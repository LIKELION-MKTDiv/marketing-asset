#!/usr/bin/env python3
"""
send_monday_report.py — 월요판 헤드라인 자동 계산 + 슬랙 발송
사용법:
  ./voc_venv/bin/python3 send_monday_report.py --from 2026-06-22 --to 2026-06-28 [--dry-run] [--send]

--dry-run (기본값): 계산 결과와 슬랙 메시지를 화면에 출력만 하고 전송하지 않음
--send: 실제로 SLACK_WEBHOOK_URL로 전송

첫 응답시간은 collect.py와 동일한 방식(운영시간 기준)으로 계산, 자동 극단치 제외 없음(개별 판단은 화요판 몫).
ALF 해결률은 태그 기반 근사치(자동)이며, 매주 화요판에서 사람이 직접 케이스 재검토 후
정밀 확정함 — 이 스크립트의 ALF% 값은 항상 "잠정치"로 표기해야 함.
"""

import argparse, json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

HERE = Path(__file__).parent
load_dotenv(HERE / '.env')

HISTORY_FILE = HERE / 'voc_weekly_history.json'
ARCHIVE_DIR = HERE / 'archive'
PII_COLUMNS = ['고객명', 'email', '담당자email']  # 축적 저장 시 항상 제거 — KPI 데이터셋은 chatId만으로 추적

_NAME_HONORIFIC_RE = re.compile(r'([가-힣]{2,4})님')


def _mask_korean_name(name):
    """이름 양끝만 남기고 가운데를 * 처리 (2026-06-11 확정 마스킹 규칙과 동일 형식)."""
    if len(name) <= 1:
        return name
    if len(name) == 2:
        return name[0] + '*'
    return name[0] + '*' * (len(name) - 2) + name[-1]


def mask_names_in_text(text):
    """상담요약 등 자유 텍스트 안에 '홍길동님'처럼 박힌 고객 실명을 마스킹.
    2026-07-14 발견: 고객명 컬럼만 지워도 상담요약 본문 안의 실명은 그대로 남아 있었음."""
    if not isinstance(text, str):
        return text
    return _NAME_HONORIFIC_RE.sub(lambda m: _mask_korean_name(m.group(1)) + '님', text)


def mask_staff_name(name):
    """실제응대담당자: 팀/봇 라벨(멋쟁이사자처럼 등)은 그대로 두고 개인 실명만 마스킹.
    콤마로 여러 값이 붙는 경우(예: '멋쟁이사자처럼, 성희라')가 있어 값 단위가 아니라
    콤마로 분리한 조각 단위로 팀 라벨 여부를 판단해야 함(2026-07-14 첫 구현에서 놓쳤던 부분)."""
    if not isinstance(name, str) or not name.strip():
        return name
    parts = [p.strip() for p in name.split(',')]
    masked = [
        p if '멋쟁이사자처럼' in p else (_mask_korean_name(p) if re.fullmatch(r'[가-힣]{2,4}', p) else p)
        for p in parts
    ]
    return ', '.join(masked)

FRT_TARGET_SEC = 600   # 첫응답시간 목표: 10분 이내
ALF_TARGET_PCT = 70.0  # ALF 해결률 목표: 70% 이상

# ALF 해결률 근사치 계산용 — 태그만으로 확인 가능한 "정책상 인적처리 필수" 카테고리.
# 개인상태확인/결제·계좌 확인 등 태그 없이 내용을 읽어야 아는 카테고리는 여기 못 잡음 —
# 그래서 이 근사치는 실제 값보다 낮게 나오는 경향이 있음(잠정치로만 사용할 것).
EXCLUDE_TAGS = ['결제환불/취소&환불', '이메일_변경', '기업문의',
                '회원정보/회원탈퇴', '회원정보/소셜로그인', '멋사대학',
                'KDT/지원완료', 'test']


def parse_dur(s):
    if pd.isna(s) or s == '':
        return np.nan
    h, m, sec = s.split(':')
    return int(h) * 3600 + int(m) * 60 + int(sec)


def fmt_minsec(total_sec):
    m, s = divmod(int(round(total_sec)), 60)
    return f'{m}분 {s}초'


def archive_week(df, from_str, to_str):
    """VOC 리포트 기능과 무관하게 KPI 데이터셋으로 남기기 위한 익명화 영구 저장.
    고객명·email 등 직접식별정보는 제거하고 chatId 기준으로만 추적 가능하게 유지.
    2026-07-14: 컬럼 삭제만으론 부족함이 드러남 — 상담요약 자유텍스트 안에 박힌 고객 실명,
    실제응대담당자 컬럼의 직원 실명도 함께 마스킹."""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    df = df.copy()
    drop_cols = [c for c in PII_COLUMNS if c in df.columns]
    df = df.drop(columns=drop_cols)
    if '상담요약' in df.columns:
        df['상담요약'] = df['상담요약'].apply(mask_names_in_text)
    if '실제응대담당자' in df.columns:
        df['실제응대담당자'] = df['실제응대담당자'].apply(mask_staff_name)
    df.to_csv(ARCHIVE_DIR / f'voc_raw_{from_str}_{to_str}.csv', index=False)


def collect_week(from_str, to_str, out_dir):
    subprocess.run(
        [sys.executable, str(HERE / 'collect.py'), '--from', from_str, '--to', to_str, '--out', str(out_dir)],
        check=True
    )
    csv_path = out_dir / f'voc_raw_{from_str[:7]}_{from_str}_{to_str}.csv'
    df = pd.read_csv(csv_path)
    archive_week(df, from_str, to_str)
    return df


def compute_headline(df):
    nonphone = df[~df['처리구분'].isin(['전화', '전화-착신X'])].copy()

    agent = nonphone[nonphone['처리구분'] == '상담원연결'].copy()
    agent['응답초'] = agent['첫응답소요'].apply(parse_dur)
    clean = agent['응답초'].dropna()  # 이미 운영시간 기준으로 정규화된 값 — 별도 극단치 자동제외 안 함(개별 케이스 판단은 화요판 수동검토 몫)
    frt_sec = clean.mean() if len(clean) else 0.0

    alf_n = (nonphone['처리구분'] == 'ALF 해결').sum()
    agent['제외'] = agent['태그'].apply(lambda t: any(x in str(t) for x in EXCLUDE_TAGS))
    pool_agent = len(agent) - agent['제외'].sum()
    inflow = alf_n + pool_agent
    alf_rate = (alf_n / inflow * 100) if inflow else 0.0

    return {
        'nonphone_total': len(nonphone),
        'frt_sec': frt_sec,
        'frt_n': len(clean),
        'alf_n': int(alf_n),
        'alf_pool': int(inflow),
        'alf_rate': round(alf_rate, 1),
    }


PRECISE_CACHE_DIR = HERE / 'precise_review_cache'


def _cache_path(from_str, to_str):
    return PRECISE_CACHE_DIR / f'{from_str}_{to_str}.json'


def compute_headline_precise(df, from_str, to_str, use_cache=True):
    """precise_review.py(Claude API 배치 검수)로 태그 기반 근사치 대신 케이스별로 판정한
    alf_n/alf_pool/frt_sec를 계산 — 화요판에서 사람이 하던 검토를 자동화한 버전.
    같은 주(from_str~to_str)는 precise_review_cache/에 판정 결과(chatId 목록만, 상담요약 원문은
    저장 안 함)를 저장해두고 재사용 — 재실행/재테스트해도 API를 다시 부르지 않는다.
    API 실패(키 없음/네트워크 오류/응답 파싱 실패) 시 None 반환 — 호출부가 태그 기반
    근사치로 조용히 폴백해야 한다(리포트 발송 자체를 막으면 안 됨)."""
    from precise_review import review_alf_exclusions, review_frt_exclusions

    nonphone = df[~df['처리구분'].isin(['전화', '전화-착신X'])].copy()
    agent = nonphone[nonphone['처리구분'] == '상담원연결'].copy()
    agent['응답초'] = agent['첫응답소요'].apply(parse_dur)
    agent['chatId'] = agent['chatId'].astype(str)
    clean = agent['응답초'].dropna()

    alf_n = int((nonphone['처리구분'] == 'ALF 해결').sum())

    cache_file = _cache_path(from_str, to_str)
    cached = None
    if use_cache and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            print(f'[AI 자동 케이스검수] 캐시 발견({cache_file.name}) — API 재호출 없이 재사용')
        except Exception:
            cached = None

    if cached is not None:
        excluded_alf = set(cached['excluded_alf'])
        excluded_frt = set(cached['excluded_frt'])
    else:
        alf_cases = agent[['chatId', '상담요약']].fillna('').to_dict('records')
        excluded_alf = review_alf_exclusions(alf_cases)
        if excluded_alf is None:
            return None

        delayed = agent[agent['응답초'] >= 900].copy()
        delayed['응답분'] = delayed['응답초'] / 60
        delayed_cases = delayed[['chatId', '상담요약', '응답분']].to_dict('records')
        excluded_frt = review_frt_exclusions(delayed_cases)
        if excluded_frt is None:
            return None

        PRECISE_CACHE_DIR.mkdir(exist_ok=True)
        cache_file.write_text(json.dumps({
            'from': from_str, 'to': to_str,
            'excluded_alf': sorted(excluded_alf),
            'excluded_frt': sorted(excluded_frt),
        }, ensure_ascii=False, indent=2))

    alf_pool = alf_n + (len(agent) - len(excluded_alf))
    alf_rate = round(alf_n / alf_pool * 100, 1) if alf_pool else 0.0

    keep = agent[~agent['chatId'].isin(excluded_frt)]
    frt_values = keep['응답초'].dropna()
    frt_sec = frt_values.mean() if len(frt_values) else 0.0

    return {
        'nonphone_total': len(nonphone),
        'frt_sec': frt_sec,
        'frt_n': len(clean),
        'alf_n': alf_n,
        'alf_pool': int(alf_pool),
        'alf_rate': alf_rate,
        'alf_excluded_n': len(excluded_alf),
        'frt_excluded_n': len(excluded_frt),
    }


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {'weeks': [], 'cumulative': None}


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))


def render_bar(value, unit, max_blocks=10):
    """value를 unit 단위 블록 수로 환산해 █▌░ 막대 문자열로 렌더링(0.5칸 단위, 최대 max_blocks)."""
    blocks = min(value / unit, max_blocks)
    blocks = round(blocks * 2) / 2
    full = int(blocks)
    half = (blocks - full) == 0.5
    empty = max_blocks - full - (1 if half else 0)
    return '█' * full + ('▌' if half else '') + '░' * empty


def frt_dot(frt_sec):
    m = frt_sec / 60
    return '🔴' if m > 30 else ('🟡' if m >= 15 else '🟢')


def alf_dot(rate):
    return '🟢' if rate >= 70 else ('🟡' if rate >= 60 else '🔴')


def meets_target(metrics):
    """첫응답시간 10분 초과 AND ALF해결률 70% 이하 — 둘 다 미달일 때만 실제 채널(#cdchapter) 자동발송.
    (2026-07-09 확정: 둘 중 하나라도 기준을 충족하면 테스트 채널만 발송하고 사람이 검토 후 수동 발송)"""
    return metrics['frt_sec'] > FRT_TARGET_SEC and metrics['alf_rate'] <= ALF_TARGET_PCT


def build_message(from_str, to_str, metrics, history, review_mode='approx'):
    """review_mode: 'manual'(사람이 --alf-n 등으로 직접 확정치 주입) /
    'ai_auto'(Claude 자동 케이스검수 성공) / 'approx'(태그 기반 근사치, 검수 실패 또는 미시도)."""
    frt_sec = metrics['frt_sec']
    alf_rate = metrics['alf_rate']
    label = from_str[5:].replace('-', '/')

    weeks = history.get('weeks', [])
    cum = history.get('cumulative')

    # history에 이번 주(label)가 이미 들어있으면(예: 확정된 주를 재실행/재테스트) 중복 표시하지 않고
    # 방금 계산한 값으로 그 자리를 교체 — "지난주 대비"도 그 이전 주 기준으로 비교
    if weeks and weeks[-1]['label'] == label:
        prev_week = weeks[-2] if len(weeks) >= 2 else None
        base_weeks = weeks[:-1]
    else:
        prev_week = weeks[-1] if weeks else None
        base_weeks = weeks

    trend_rows = base_weeks + [{'label': label, 'frt_sec': frt_sec, 'alf_rate': alf_rate,
                                 'alf_n': metrics['alf_n'], 'alf_pool': metrics['alf_pool']}]

    lines = []
    lines.append(f"📊 주간 VOC 리포트 - 월요일 09시 발행 ({from_str[5:].replace('-', '.')} ~ {to_str[5:].replace('-', '.')})")
    lines.append('')
    lines.append(f"📊 CS 주간 지표 (26.01.12 ~ {to_str[5:].replace('-', '.')})")
    lines.append('')

    # 첫 응답 시간
    frt_line = f"⚡ 첫 응답 시간: {fmt_minsec(frt_sec)} {frt_dot(frt_sec)}"
    if prev_week:
        delta = frt_sec - prev_week['frt_sec']
        frt_line += f" (지난주 {fmt_minsec(prev_week['frt_sec'])} 대비 {'▼' if delta <= 0 else '▲'}{fmt_minsec(abs(delta))} {'감소' if delta <= 0 else '증가'})"
    lines.append(frt_line)
    lines.append('```')
    for row in trend_rows[-7:]:
        arrow = ' ←' if row is trend_rows[-1] else ''
        lines.append(f"{row['label']} {render_bar(row['frt_sec'], 120)} {fmt_minsec(row['frt_sec'])}{arrow}")
    lines.append('```')
    lines.append('🔴 30분 초과 · 🟡 15~30분 · 🟢 15분 미만')
    lines.append('')

    # ALF 해결률
    alf_line = f"🤖 ALF 해결률: {alf_rate}% {alf_dot(alf_rate)}"
    if prev_week:
        d = round(alf_rate - prev_week['alf_rate'], 1)
        alf_line += f" (지난주 {prev_week['alf_rate']}% 대비 {'▲' if d >= 0 else '▼'}{abs(d)}%p)"
    lines.append(alf_line)
    lines.append('')
    lines.append(f"ALF 분석 대상: {metrics['alf_pool']}건 / ALF 단독해결: {metrics['alf_n']}건 / 교육 매니저 연결: {metrics['alf_pool']-metrics['alf_n']}건")
    lines.append('```')
    for row in trend_rows[-8:]:
        arrow = ' ←' if row is trend_rows[-1] else ''
        lines.append(f"{row['label']} {render_bar(row['alf_rate'], 10)} {row['alf_rate']}% · {row['alf_n']}/{row['alf_pool']}건{arrow}")
    lines.append('```')
    lines.append('🔴 60% 미만 · 🟡 60~70% · 🟢 70% 이상')
    lines.append('')

    # 누적 요약
    if cum:
        new_total = cum['alf_cum_total'] + metrics['alf_pool']
        new_n = cum['alf_cum_n'] + metrics['alf_n']
        new_alf_cum_rate = round(new_n / new_total * 100, 1) if new_total else 0.0
        # frt 누적은 alf_cum_total과 동일한 분모를 근사치로 사용(전용 FRT 누적건수 트래킹 없음)
        new_frt_cum_sec = (cum['frt_cum_sec'] * cum['alf_cum_total'] + frt_sec * metrics['alf_pool']) / new_total if new_total else frt_sec

        lines.append(f"📌 누적 요약 (26.01.12 ~ {to_str[5:].replace('-', '.')})")
        lines.append('')
        frt_cum_delta = new_frt_cum_sec - cum['frt_cum_sec']
        lines.append(f"⚡ 첫 응답 시간: {fmt_minsec(new_frt_cum_sec)} {frt_dot(new_frt_cum_sec)} "
                     f"{'▼' if frt_cum_delta <= 0 else '▲'}{fmt_minsec(abs(frt_cum_delta))} (지난주 누적 {fmt_minsec(cum['frt_cum_sec'])})")
        alf_cum_delta = round(new_alf_cum_rate - cum['alf_cum_rate'], 1)
        lines.append(f"🤖 ALF 해결률: {new_alf_cum_rate}% {alf_dot(new_alf_cum_rate)} "
                     f"{'▲' if alf_cum_delta >= 0 else '▼'}{abs(alf_cum_delta)}%p (지난주 누적 {cum['alf_cum_rate']}%) — "
                     f"{new_n:,} / {new_total:,}건 (지난주 누적 {cum['alf_cum_n']:,} / {cum['alf_cum_total']:,}건)")
        lines.append('')

    lines.append('⚠️ 월요일 리포트의 경우 주말 인입 건이 모두 반영되지 않아 이후 수치가 일부 변경될 수 있습니다.')
    if review_mode == 'manual':
        lines.append('✅ ALF 해결률·첫응답시간 모두 클로드 AI가 케이스별 상담요약을 직접 검토해 확정한 값입니다.')
    elif review_mode == 'ai_auto':
        lines.append('🤖 ALF 해결률·첫응답시간 모두 Claude가 케이스별 상담요약을 자동 검토해 반영한 값입니다(사람 최종검수 전, 화요판에서 재확인됩니다).')
    else:
        lines.append('⚠️ ALF 해결률은 태그 기반 자동 근사치(잠정치)입니다 — 화요판에서 케이스별 재검토 후 정밀 확정됩니다.')

    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--from', dest='from_str', required=True)
    p.add_argument('--to', dest='to_str', required=True)
    p.add_argument('--send', action='store_true', help='실제 슬랙 전송')
    p.add_argument('--skip-collect', action='store_true', help='이미 수집된 CSV 재사용(재수집 안 함)')
    # 케이스별 검토(구조적 제외/순수 미해결, FRT 극단치 판별)로 계산한 정밀치를 직접 주입 —
    # 지정하면 compute_headline()의 태그기반 근사치 대신 이 값을 그대로 사용
    p.add_argument('--alf-n', type=int, help='정밀 검토 후 ALF 단독해결 건수(수동 주입, 최우선)')
    p.add_argument('--alf-pool', type=int, help='정밀 검토 후 ALF 분석대상 건수(분모, 수동 주입)')
    p.add_argument('--frt-sec', type=float, help='정밀 검토 후 첫응답시간 평균(초, 수동 주입)')
    p.add_argument('--no-ai-review', action='store_true', help='Claude 자동 케이스검수 건너뛰고 태그 근사치만 사용(테스트/비용절감용)')
    p.add_argument('--no-cache', action='store_true', help='같은 주의 캐시된 자동검수 결과가 있어도 무시하고 API를 다시 호출')
    args = p.parse_args()

    out_dir = HERE / 'voc_csv'
    if args.skip_collect:
        csv_path = out_dir / f'voc_raw_{args.from_str[:7]}_{args.from_str}_{args.to_str}.csv'
        df = pd.read_csv(csv_path)
        archive_week(df, args.from_str, args.to_str)
    else:
        df = collect_week(args.from_str, args.to_str, out_dir)
    metrics = compute_headline(df)

    # 우선순위: 사람이 직접 넣은 --alf-n/--frt-sec(화요판 최종 확정치) > Claude 자동 케이스검수 > 태그 기반 근사치
    manual_override = args.alf_n is not None and args.alf_pool is not None
    review_mode = 'approx'
    if manual_override:
        metrics['alf_n'] = args.alf_n
        metrics['alf_pool'] = args.alf_pool
        metrics['alf_rate'] = round(args.alf_n / args.alf_pool * 100, 1) if args.alf_pool else 0.0
        review_mode = 'manual'
    elif not args.no_ai_review:
        print('[AI 자동 케이스검수] Claude로 ALF/FRT 배치 검토 중...')
        precise_metrics = compute_headline_precise(df, args.from_str, args.to_str, use_cache=not args.no_cache)
        if precise_metrics is not None:
            metrics.update(precise_metrics)
            review_mode = 'ai_auto'
            print(f"[AI 자동 케이스검수] 완료 — ALF 제외 {precise_metrics['alf_excluded_n']}건, "
                  f"FRT 극단치 제외 {precise_metrics['frt_excluded_n']}건")
        else:
            print('[AI 자동 케이스검수] 실패 — 태그 기반 근사치로 폴백')
    if args.frt_sec is not None:
        metrics['frt_sec'] = args.frt_sec
        review_mode = 'manual'

    history = load_history()

    message = build_message(args.from_str, args.to_str, metrics, history, review_mode=review_mode)

    print('=== 계산된 지표 ===')
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print()
    print('=== 슬랙 메시지 미리보기 ===')
    print(message)

    raw_both_missed = meets_target(metrics)
    # review_mode가 'approx'(태그 근사치, AI 검수 실패 시 폴백)일 때는 신뢰도가 낮아
    # 지표가 아무리 나빠 보여도 실채널 자동발송을 막는다(2026-07-10 확정 — 근사치 오판정으로
    # #cdchapter에 잘못된 긴급알람이 실제 발송된 사고 이후 추가된 안전장치).
    both_missed = raw_both_missed and review_mode != 'approx'
    if raw_both_missed and review_mode == 'approx':
        print(f"\n=== 발송 조건 판정 === 첫응답 {fmt_minsec(metrics['frt_sec'])}(목표 10분 이내) / "
              f"ALF {metrics['alf_rate']}%(목표 70% 이상) → "
              f"⚠️ 수치상 둘 다 미달이지만 근사치(review_mode=approx)라 신뢰 불가 → 실채널 자동발송 보류, 테스트채널만 + 수동확인 필요")
    else:
        print(f"\n=== 발송 조건 판정 === 첫응답 {fmt_minsec(metrics['frt_sec'])}(목표 10분 이내) / "
              f"ALF {metrics['alf_rate']}%(목표 70% 이상) → "
              f"{'🚨 둘 다 미달 → 실채널 자동발송' if both_missed else '✅ 하나 이상 충족 → 테스트채널만, 수동검토 필요'}")

    if args.send:
        test_url = os.environ.get('SLACK_WEBHOOK_TEST') or os.environ.get('SLACK_WEBHOOK_URL')
        r = requests.post(test_url, json={'text': message}, allow_redirects=False)
        print(f'[테스트 채널 전송] status={r.status_code}')

        report_url = os.environ.get('SLACK_WEBHOOK_REPORT')
        if both_missed and report_url:
            r2 = requests.post(report_url, json={'text': message}, allow_redirects=False)
            print(f'[실제 채널(#cdchapter) 전송] status={r2.status_code} — 첫응답시간·ALF 둘 다 미달로 긴급 자동 발송')
        elif raw_both_missed and review_mode == 'approx':
            print('[실제 채널 미발송] 근사치 기준 둘 다 미달로 보이나 review_mode=approx라 신뢰 불가 — 테스트 채널 결과를 사람이 직접 확인 후 수동 발송 여부 결정 필요')
        elif not both_missed:
            print('[실제 채널 미발송] 둘 중 하나 이상 기준 충족 — 테스트 채널 결과 검사 후 수동 발송 여부 결정 필요')
        elif not report_url:
            print('[실제 채널 미발송] SLACK_WEBHOOK_REPORT 미설정')
    else:
        print('\n[드라이런] 실제 전송하지 않음 — 전송하려면 --send 옵션 추가')

    print('\n※ history(voc_weekly_history.json)는 자동 갱신되지 않습니다 — 화요판 확정 후 수동으로 반영하세요.')


if __name__ == '__main__':
    main()
