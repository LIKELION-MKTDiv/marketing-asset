#!/usr/bin/env python3
"""
collect.py — 채널톡 API → 로컬 CSV 수집
사용법: python collect.py --from 2026-06-15 --to 2026-06-21

환경변수 (또는 .env 파일):
  CHANNEL_ACCESS_KEY
  CHANNEL_ACCESS_SECRET
"""

import os, sys, time, json, argparse, requests
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

import pandas as pd

# ── 설정 ──────────────────────────────────────────────────────────────
BASE_URL = 'https://api.channel.io'
KST = timezone(timedelta(hours=9))

# 공휴일 (2025~2026)
KR_HOLIDAYS = {
    '2025-01-01','2025-01-28','2025-01-29','2025-01-30',
    '2025-03-01','2025-05-05','2025-05-06','2025-06-06',
    '2025-08-15','2025-10-03','2025-10-06','2025-10-07',
    '2025-10-08','2025-10-09','2025-12-25',
    '2026-01-01','2026-02-16','2026-02-17','2026-02-18',
    '2026-03-01','2026-03-02','2026-05-05','2026-05-24',
    '2026-05-25','2026-06-03','2026-06-06','2026-07-17',
    '2026-08-15','2026-08-17','2026-09-24','2026-09-25',
    '2026-09-26','2026-10-03','2026-10-05','2026-10-09','2026-12-25'
}

OUTPUT_DIR = Path(__file__).parent / 'voc_csv'

# ── 유틸 함수 ──────────────────────────────────────────────────────────
def kst_day(ms):
    return datetime.fromtimestamp(int(ms)/1000, tz=KST).strftime('%Y-%m-%d')

def fmt_kst(ms):
    if not ms: return ''
    return datetime.fromtimestamp(int(ms)/1000, tz=KST).strftime('%Y-%m-%d %H:%M:%S')

def fmt_duration(ms):
    if ms is None or ms < 0: return ''
    total = round(ms / 1000)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f'{h}:{m:02d}:{s:02d}'

def business_millis_between(start_ms, end_ms):
    if not start_ms or not end_ms or end_ms <= start_ms: return 0
    slots = [(10*60, 12*60), (13*60, 18*60)]
    total = 0
    s_dt = datetime.fromtimestamp(start_ms/1000, tz=KST)
    e_dt = datetime.fromtimestamp(end_ms/1000, tz=KST)
    cur  = s_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    e_day = e_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    while cur <= e_day:
        ds = cur.strftime('%Y-%m-%d')
        if cur.weekday() < 5 and ds not in KR_HOLIDAYS:
            for sm, em in slots:
                ss = cur + timedelta(minutes=sm)
                es = cur + timedelta(minutes=em)
                ov_s = max(s_dt, ss); ov_e = min(e_dt, es)
                if ov_e > ov_s:
                    total += (ov_e - ov_s).total_seconds() * 1000
        cur += timedelta(days=1)
    return total

def normalize_tags(tags):
    if not tags: return []
    if isinstance(tags, list): return [str(t).strip() for t in tags if t]
    return [t.strip() for t in str(tags).split(',') if t.strip()]

def is_private(m):
    if not m: return False
    opts = m.get('options', [])
    return isinstance(opts, list) and 'private' in opts


# ── API 호출 ────────────────────────────────────────────────────────────
def call_api(headers, path, params=None):
    url = BASE_URL + path
    for attempt in range(5):
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise Exception(f'API 오류: {path}')


def get_managers(headers):
    mgr_map, since = {}, None
    while True:
        params = {'limit': 500}
        if since: params['since'] = since
        r = call_api(headers, '/open/v5/managers', params)
        for m in r.get('managers', []):
            if m and m.get('id') is not None:
                mgr_map[str(m['id'])] = {
                    'name'   : m.get('name', ''),
                    'email'  : m.get('email', ''),
                    'removed': bool(m.get('removed', False))
                }
        since = r.get('next')
        if not since: break
    return mgr_map


def get_messages(headers, chat_id):
    msgs, since = [], None
    while True:
        params = {'sortOrder': 'asc', 'limit': 500}
        if since: params['since'] = since
        r = call_api(headers, f'/open/v5/user-chats/{chat_id}/messages', params)
        msgs.extend(r.get('messages', []))
        since = r.get('next')
        if not since: break
    return msgs


def collect_chat_ids(headers, from_str, to_str):
    # 'state' 파라미터를 생략하면 API가 기본값(사실상 'opened'만)만 반환한다 —
    # "전체 상태 조회"가 되지 않으므로, 필요한 state를 각각 명시해 조회 후 합쳐야 한다.
    # 'closed'만 조회하면 안 되는 이유: ALF가 답변하고 고객이 더 응답하지 않으면
    # 채팅이 'closed'로 전환되지 않고 'initial'(대기) 상태로 남는다.
    # 이 상태 채팅을 빼면 ALF 단독해결 건이 대량 누락된다 (2026-07 확인된 실사례:
    # 이번 주 state=initial & alfTriggered=true 65건 vs state=closed 82건).
    ids = set()
    for state in ('closed', 'initial', 'opened'):
        since, guard = None, 0
        while True:
            params = {'sortOrder': 'desc', 'limit': 500, 'state': state}
            if since: params['since'] = since
            r   = call_api(headers, '/open/v5/user-chats', params)
            ucs = r.get('userChats', [])
            page_recent = False
            for uc in ucs:
                ca = uc.get('closedAt')
                cr = uc.get('createdAt')
                if ca and from_str <= kst_day(ca) <= to_str:
                    ids.add(str(uc['id']))
                elif not ca and cr and from_str <= kst_day(cr) <= to_str:
                    ids.add(str(uc['id']))
                ua = uc.get('updatedAt')
                if ua and kst_day(ua) >= from_str:
                    page_recent = True
            since = r.get('next')
            guard += 1
            if not since or (not page_recent and ucs) or guard >= 200:
                break
    return list(ids)


def build_record(headers, chat_id, mgr_map):
    r    = call_api(headers, f'/open/v5/user-chats/{chat_id}')
    uc   = r.get('userChat', r)
    user = r.get('user')
    msgs = get_messages(headers, chat_id)

    # 실제 응대 담당자
    seen, rep_ids = set(), []
    for m in msgs:
        if not m or is_private(m): continue
        if m.get('personType') == 'manager':
            pid = str(m.get('personId', ''))
            if pid and pid not in seen:
                seen.add(pid); rep_ids.append(pid)

    rep_names, rep_emails = [], []
    for pid in rep_ids:
        mg = mgr_map.get(pid)
        if mg:
            rep_names.append(mg['name'] + ('(삭제됨)' if mg['removed'] else ''))
            if mg['email']: rep_emails.append(mg['email'])
        else:
            rep_names.append(f'(미상:{pid})')

    # 고객 정보
    profile    = (user or {}).get('profile', {}) or {}
    member_id  = (user or {}).get('memberId', '') or profile.get('memberId', '')
    cust_email = profile.get('email', '') or (user or {}).get('email', '')
    cust_name  = uc.get('name','') or (user or {}).get('name','') or profile.get('name','')
    is_member  = '회원' if user and str(user.get('member','')).lower()=='true' else '비회원'

    # 태그
    tag_names = normalize_tags(uc.get('tags', []))

    # 시간 지표
    cust_times, mgr_times, all_times = [], [], []
    for m in msgs:
        if not m or is_private(m): continue
        t = m.get('createdAt')
        if not t: continue
        t = int(t)
        pt = m.get('personType', '')
        if pt == 'user':      cust_times.append(t); all_times.append(t)
        elif pt == 'manager': mgr_times.append(t);  all_times.append(t)

    cust_first_ms = min(cust_times) if cust_times else None
    mgr_first_ms  = min(mgr_times)  if mgr_times  else None
    end_ms        = max(all_times)  if all_times  else None

    # 응답 대상 고객 메시지 = 매니저 첫 응답 '직전' 마지막 고객 메시지.
    # 채팅 맨 처음 고객 메시지(cust_first_ms)를 기준으로 하면, ALF가 먼저
    # 여러 턴 응대하다가 한참 뒤에야 고객이 매니저를 부른 경우 ALF가
    # 응대하던 시간까지 전부 "매니저 지연"으로 잘못 잡힌다
    # (2026-07-06 실사례: 10시간43분으로 집계됐던 건이 실제로는 매니저가
    #  고객의 "매니저 연결해주세요" 요청 후 약 3분 만에 응답한 건이었음).
    cust_ref_ms = None
    if mgr_first_ms:
        prior = [t for t in cust_times if t <= mgr_first_ms]
        cust_ref_ms = max(prior) if prior else cust_first_ms
    else:
        cust_ref_ms = cust_first_ms

    frt = ''
    if cust_ref_ms and mgr_first_ms and mgr_first_ms >= cust_ref_ms:
        frt = fmt_duration(business_millis_between(cust_ref_ms, mgr_first_ms))

    # 상담요약 (마지막 실질 bot 메시지 — CSAT/자동종료 등 정형 문구는 제외)
    # 실제 처리 요약과 "추가로 궁금하신 점..." 같은 정형 문구가 거의 같은 시각에
    # 연속 발송되는 경우가 많아, 단순히 '가장 늦은 bot 메시지'를 고르면 정형 문구가
    # 뽑혀 실제 문의 내용이 사라진다 (2026-07-06 KDC 5건에서 확인됨).
    BOILERPLATE_PATTERNS = (
        '추가로 궁금하신 점',
        '좋은 점수 감사합니다',
        '원활한 상담을 위해',
        '지금은 상담 운영시간이 아닙니다',
    )
    best_text, best_time = '', -1
    for m in msgs:
        if not m or m.get('personType') != 'bot': continue
        txt = str(m.get('plainText','') or '').strip()
        if not txt: continue
        if any(p in txt for p in BOILERPLATE_PATTERNS): continue
        t = int(m.get('createdAt', 0) or 0)
        if t > best_time: best_time = t; best_text = m.get('plainText','')

    # 처리구분
    is_phone = '전화' in tag_names
    if is_phone:
        resolution = '전화' if best_text else '전화-착신X'
    elif not cust_first_ms:
        resolution = ''
    elif mgr_first_ms:
        resolution = '상담원연결'
    else:
        resolution = 'ALF 해결'

    return {
        'chatId'       : str(uc.get('id', chat_id)),
        '고객명'        : cust_name,
        'memberId'     : member_id,
        'email'        : cust_email,
        '실제응대담당자'  : ', '.join(rep_names),
        '담당자email'   : ', '.join(rep_emails),
        '태그'          : ', '.join(tag_names),
        '태그설명'       : '',
        '상담요약'       : best_text,
        'state'        : uc.get('state',''),
        '매체'          : uc.get('mediumType','') or uc.get('mediumName',''),
        '상담생성'       : fmt_kst(uc.get('createdAt')),
        '대화시작'       : fmt_kst(cust_first_ms),
        '응답대상질문시각' : fmt_kst(cust_ref_ms),
        '담당자첫응답'   : fmt_kst(mgr_first_ms),
        '첫응답소요'     : frt,
        '대화종료'       : fmt_kst(end_ms),
        '처리구분'       : resolution,
        'csat'         : (uc.get('profile') or {}).get('csat', ''),
        'csat의견'      : (uc.get('profile') or {}).get('csatComment', ''),
    }


# ── 메인 ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='채널톡 VOC 수집')
    parser.add_argument('--from', dest='from_date', required=True, help='시작일 YYYY-MM-DD')
    parser.add_argument('--to',   dest='to_date',   required=True, help='종료일 YYYY-MM-DD')
    parser.add_argument('--out',  dest='out_dir',   default=str(OUTPUT_DIR), help='CSV 저장 폴더')
    args = parser.parse_args()

    key    = os.environ.get('CHANNEL_ACCESS_KEY', '')
    secret = os.environ.get('CHANNEL_ACCESS_SECRET', '')
    if not key or not secret:
        print('❌ CHANNEL_ACCESS_KEY / CHANNEL_ACCESS_SECRET 환경변수 필요')
        print('   .env 파일에 추가하거나 export로 설정하세요')
        sys.exit(1)

    headers = {
        'x-access-key'   : key,
        'x-access-secret': secret,
        'Accept'         : 'application/json'
    }

    from_str = args.from_date
    to_str   = args.to_date
    out_dir  = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    year_month = from_str[:7]
    out_file   = out_dir / f'voc_raw_{year_month}_{from_str}_{to_str}.csv'

    print(f'[{from_str} ~ {to_str}] 수집 시작')

    # 1. 상담 ID 수집
    print('1/3 상담 ID 수집 중...')
    ids = collect_chat_ids(headers, from_str, to_str)
    print(f'    대상: {len(ids)}건')
    if len(ids) > 300:
        print(f'    ⚠️ 대량 건수 — 완료까지 시간이 걸립니다')

    # 2. 매니저 맵
    print('2/3 매니저 목록 로딩...')
    mgr_map = get_managers(headers)
    print(f'    매니저: {len(mgr_map)}명')

    # 3. 상담 데이터 수집
    print('3/3 상담 데이터 수집 중...')
    records = []
    ok = fail = 0
    for i, chat_id in enumerate(ids):
        try:
            rec = build_record(headers, chat_id, mgr_map)
            # 인입일 필터 (인입일 기준)
            rec['인입일'] = rec['상담생성'][:10] if rec['상담생성'] else ''
            records.append(rec)
            ok += 1
        except Exception as e:
            fail += 1
            print(f'    실패 {chat_id}: {e}')
        time.sleep(0.12)
        if (i+1) % 50 == 0:
            print(f'    진행: {i+1}/{len(ids)} — 성공 {ok} / 실패 {fail}')

    # 인입일 기준 필터
    df = pd.DataFrame(records)
    if len(df) > 0:
        df = df[(df['인입일'] >= from_str) & (df['인입일'] <= to_str)].copy()

    df.to_csv(out_file, index=False, encoding='utf-8-sig')
    print(f'\n✅ 저장 완료: {out_file}')
    print(f'   수집 {ok}건 → 인입기준 {len(df)}건 (실패 {fail}건)')
    return str(out_file)


if __name__ == '__main__':
    main()
