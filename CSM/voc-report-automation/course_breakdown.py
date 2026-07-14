#!/usr/bin/env python3
"""
course_breakdown.py — 화요판 작성 전 과정별 인입건수 사전 집계
사용법: python course_breakdown.py --from 2026-06-29 --to 2026-07-05

목적: 화요판 심층분석에서 사람(세션)이 매번 원본 153여 건을 처음부터 다 읽지 않도록,
      "이미 명확한 것"만 자동 집계하고 "애매한 것"은 review_queue로 남겨서 세션이
      그 부분만 집중해서 읽게 한다.

이 스크립트가 하는 일 (전부 tuesday_template.md의 "과정별 인입 문의 수 집계 규칙"을 그대로 코드화):
  - 전화/전화-착신X 제외
  - 태그에서 실제 과정 태그(KDT/*, KDC, AIERS/*, 광화문_라이언즈)만 골라 집계
  - AIERS/AIERS 하루완성 통합
  - 기타문의 + 다른 태그 조합 → 다른 태그로 재매칭
  - 이메일_변경/회원정보/결제환불/미래내일일경험/멋사대학 등 비과정 태그는 집계에서 제외

이 스크립트가 "하지 않는" 일 (반드시 사람/세션이 원본을 읽고 판단해야 함, 자동화 금지):
  - review_queue(과목 특정 불가) 건들이 진짜 이탈인지 판단
  - ALF 해결률 산정을 위한 매니저연결 건의 구조적 제외 여부 판단
    → 이건 precise_review.py가 Claude로 이미 케이스별 검토·캐시해두므로, 화요판 작성 시
      precise_review_cache/{from}_{to}.json을 그대로 참고할 것 (여기서 재수행하지 않음)
  - CSAT/설문 정형문구 오분류, 중복 재오픈 판단, 응답지연 극단치의 실제 원인
    → 전부 상담요약 원문을 직접 읽어야 하는 정성 판단. 이 스크립트는 후보를 좁혀줄 뿐,
      최종 판단은 대체하지 않는다.
"""

import argparse
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent

COURSE_PREFIXES = ('KDT', 'KDC', 'AIERS', '광화문_라이언즈')
PHONE_TAGS = ['전화', '전화-착신X']


def normalize_course_tag(t):
    return 'AIERS/하루완성' if t.startswith('AIERS') else t


def pick_course(tagstr):
    """실제 과정 태그를 하나 골라 반환. 없으면 None(=사람이 읽어야 할 건)."""
    if pd.isna(tagstr) or not str(tagstr).strip():
        return None
    tags = [x.strip() for x in str(tagstr).split(',') if x.strip()]
    for t in tags:
        if t.startswith(COURSE_PREFIXES):
            return normalize_course_tag(t)
    return None  # 기타문의 단독, 비과정 태그만 있음, 또는 무태그 — 전부 사람이 확인


def run(from_str, to_str):
    csv_path = HERE / 'archive' / f'voc_raw_{from_str}_{to_str}.csv'
    if not csv_path.exists():
        raise FileNotFoundError(
            f'{csv_path} 없음 — 월요 자동화가 그 주 데이터를 아직 수집 안 했거나 archive_week()가 실패했을 수 있음. '
            f'collect.py --from {from_str} --to {to_str} 로 직접 수집 후 재시도.'
        )
    df = pd.read_csv(csv_path)
    nonphone = df[~df['처리구분'].isin(PHONE_TAGS)].copy()
    nonphone['과정'] = nonphone['태그'].apply(pick_course)

    resolved = nonphone[nonphone['과정'].notna()]
    review_queue = nonphone[nonphone['과정'].isna()]

    counts = resolved['과정'].value_counts()
    total = int(counts.sum())

    print(f'[{from_str} ~ {to_str}] 비전화 {len(nonphone)}건 → 과정 특정 {total}건 / 리뷰큐(사람 확인 필요) {len(review_queue)}건\n')
    print('📊 과정별 인입 문의 수 (자동 집계 — 태그 확정건만)')
    print('| 과정 | 건수 | 비율 |')
    print('|---|---|---|')
    for course, n in counts.items():
        print(f'| {course} | {n}건 | {n/total*100:.1f}% |')

    print('\n⚠️ 리뷰큐 — 태그로 과목 특정 불가, 원본 상담요약을 직접 읽고 판단할 것 (자동 분류 금지)')
    for _, row in review_queue.iterrows():
        tag = row['태그'] if pd.notna(row['태그']) else '(무태그)'
        summary = str(row['상담요약'])[:60] if pd.notna(row['상담요약']) else ''
        print(f"  - chatId={row['chatId']} | 태그={tag} | state={row['state']} | 요약: {summary}")

    print('\n💡 ALF 해결률·FRT 극단치 판단은 이 스크립트가 다루지 않음 — '
          f'precise_review_cache/{from_str}_{to_str}.json (Monday 자동화가 이미 생성) 참고할 것.')

    return {'total': total, 'counts': counts.to_dict(), 'review_queue_n': len(review_queue)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--from', dest='from_str', required=True)
    p.add_argument('--to', dest='to_str', required=True)
    args = p.parse_args()
    run(args.from_str, args.to_str)
