---
title: KDT 모객현황 데일리 리포트 260619
date: 2026-06-19
type: daily-report
tags: [kdt, 모객, daily-report]
source: kdt 모객현황 데이터 추출.ipynb
status: TEST
---

# 📊 KDT 모객현황 데일리 리포트 · 2026-06-19

> [!info] 대상 캠프 3종 · 내부직원·테스트 제외 · **TEST 출력본**

## 🔗 리포트 열기 (인터랙티브)

[▶ 260619_daily-report.html 브라우저로 열기](260619_daily-report.html)

<iframe src="260619_daily-report.html" width="100%" height="900" style="border:1px solid #2a2f3a;border-radius:10px;"></iframe>

> [!tip] iframe이 비어 보이면 옵시디언 설정 또는 보안정책 때문일 수 있습니다. 위 링크로 직접 열면 항상 동작합니다.

## 📈 핵심 요약

| 캠프 | 목표모객 | 수강정원 | 지원시작 | 지원중 | 지원완료 | 완료달성율<br>(완료/시작) | 목표달성율<br>(완료/목표) | 경쟁률<br>(지원/정원) | 내배카 보유율 |
|---|---|---|---|---|---|---|---|---|---|
| AI+ NLP 5기 | 96 | 40 | 427 | 300 | 121 | 28.3% | 126.0% | 10.7:1 | 46.1% |
| 백엔드 자바 26기 | 72 | 24 | 187 | 130 | 52 | 27.8% | 72.2% | 7.8:1 | 56.2% |
| 그로스 마케팅 6기 | 142 | 57 | 87 | 62 | 24 | 27.6% | 16.9% | 1.5:1 | 75.6% |

- **총 지원시작** 701 · **완료** 197 (평균 전환 28.1%) · **미완료 적체** 492 (70%)
- **내배카 보유율** 51.9% (유효응답 362명)

## 📅 모집 마감 전망 (트렌드 × 종결일)

| 캠프 | 모집기간 | 마감 | 경과 | 완료/목표 | 페이스(명/일) | 예상도달(목표대비) | 전망 |
|---|---|---|---|---|---|---|---|
| AI+ NLP 5기 | 2026-05-18~2026-06-22 | D-3 | 92% | 121/96 | 5.14 | 136 (142%) | 목표 조기 달성 |
| 백엔드 자바 26기 | 2026-05-27~2026-06-29 | D-10 | 71% | 52/72 | 1.0 | 62 (86%) | 마감 내 목표 미달 전망 |
| 그로스 마케팅 6기 | 2026-06-16~2026-07-19 | D-30 | 12% | 24/142 | 6.0 | 204 (144%) ⚠️초기 | 마감 내 목표 달성 전망 |

- **AI+ NLP 5기**: 목표 모객(96명) 초과 달성 · 마감 D-3 — 선발·등록 전환·정원 적합도로 전환.
- **백엔드 자바 26기**: 최근 1.0명/일 → 마감 예상 62명(목표 72 대비 86%) → **마감 내 목표 미달 전망**.
- **그로스 마케팅 6기**: 최근 6.0명/일 → 마감 예상 204명(목표 142 대비 144%) → **마감 내 목표 달성 전망** (모집 7일 미만, 신뢰도 낮음).

## 📊 전일 대비 경향성 · 직전 260617 대비 (비판적 분석)

| 캠프 | 지원시작 | 지원완료 | 완료전환율 | 내배카 | 목표달성율 | 심사진행(합/불/예비) |
|---|---|---|---|---|---|---|
| AI+ NLP 5기 | ▲44 | ▲16 | ▲0.9pp | ▲0.6pp | ▲16.6pp | 합+9 불+13 예-16 |
| 백엔드 자바 26기 | ▲13 | ▲2 | ▼0.9pp | ▲0.8pp | ▲2.8pp | 합+1 불+1 예+1 |
| 그로스 마케팅 6기 | ▲49 | ▲10 | ▼9.2pp | ▲10.6pp | ▲7.0pp | 합+11 불+0 예+0 |

*Δ = 오늘 − 직전 리포트 · 1일 변동이라 노이즈 가능성 유의*

**AI+ NLP 5기**

1. 지원 +44명 · 전환율 +0.9pp 동반 — 양·질 함께 개선. 단, 1일 변동이라 추세 확정 전 2~3일 더 관찰 필요.
2. 심사 진행 6건(합격 +9·불합격 +13·예비 -16) vs 지원완료 +16 — 완료수 증가가 '신규 완료'인지 '심사 결과 반영'인지 구분해야 전환율 해석이 정확.
3. 목표 도달 유지(달성율 126.0%) — 점검 축을 완료 수 → 등록 전환·적합도로 이동.

**백엔드 자바 26기**

1. 신규 지원 +13명인데 완료전환율 -0.9pp 하락 — 유입은 늘었으나 완료로 이어지지 않음. '숫자 증가'에 안심 말고 유입 채널 품질·지원서 이탈 지점을 의심해야 함.
2. 심사 진행 3건(합격 +1·불합격 +1·예비 +1) vs 지원완료 +2 — 완료수 증가가 '신규 완료'인지 '심사 결과 반영'인지 구분해야 전환율 해석이 정확.
3. 목표 달성율 69.4→72.2% (+2.8pp) — 오늘 +2명 페이스면 잔여 20명에 약 10일. 잔여 모집기간과 대조해 '달성 가능 페이스'인지 판단.

**그로스 마케팅 6기**

1. 신규 지원 +49명인데 완료전환율 -9.2pp 하락 — 유입은 늘었으나 완료로 이어지지 않음. '숫자 증가'에 안심 말고 유입 채널 품질·지원서 이탈 지점을 의심해야 함.
2. 심사 진행 11건(합격 +11·불합격 +0·예비 +0) vs 지원완료 +10 — 완료수 증가가 '신규 완료'인지 '심사 결과 반영'인지 구분해야 전환율 해석이 정확.
3. 목표 달성율 9.9→16.9% (+7.0pp) — 오늘 +10명 페이스면 잔여 118명에 약 12일. 잔여 모집기간과 대조해 '달성 가능 페이스'인지 판단.
4. 내배카 보유율 +10.6pp 변동 — 신규 유입의 연령·신분 세그먼트가 이동했을 가능성. 연령대×합불상태/내배카 교차표로 어느 층이 늘었는지 확인.

## 🧐 부트캠프별 점검 코멘트 (비판적 점검 포인트)

**AI+ NLP 5기** (목표 96 · 달성율 126.0%)

1. 목표 96명 도달(달성율 126.0%) — 점검 지표를 완료 '수'에서 질(적합도·등록 전환·미수료 리스크)로 전환할 시점.
2. 완료전환 28.3% vs 미완료 70% — '지원시작' 분모에 유령·중복·단순열람이 섞였는지, 아니면 지원서 문항·자격요건이 이탈 병목인지 분해해야 실제 전환율이 드러남.
3. 대학(원)생 내배카 보유율 30.5%(n=131) — 비용 민감 세그먼트. 이 그룹이 완료전환에서 더 이탈하는지 교차 점검하고 자비·국비 메시지 분기 검토.

**백엔드 자바 26기** (목표 72 · 달성율 72.2%)

1. 목표 달성율 72.2%를 절대값으로 판단하지 말 것 — 최근 7일 일평균 완료 1.4명 기준 잔여 20명은 약 14일 소요. 마감 D-10 내 달성 불가 페이스 — 강한 가속/연장 검토.
2. 완료전환 27.8% vs 미완료 70% — '지원시작' 분모에 유령·중복·단순열람이 섞였는지, 아니면 지원서 문항·자격요건이 이탈 병목인지 분해해야 실제 전환율이 드러남.
3. 대학(원)생 내배카 보유율 26.3%(n=19) — 비용 민감 세그먼트. 이 그룹이 완료전환에서 더 이탈하는지 교차 점검하고 자비·국비 메시지 분기 검토.

**그로스 마케팅 6기** (목표 142 · 달성율 16.9%)

1. 목표 달성율 16.9%를 절대값으로 판단하지 말 것 — 최근 7일 일평균 완료 6.0명 기준 잔여 118명은 약 20일 소요. 마감 D-30 대비 여유.
2. 완료전환 27.6% vs 미완료 71% — '지원시작' 분모에 유령·중복·단순열람이 섞였는지, 아니면 지원서 문항·자격요건이 이탈 병목인지 분해해야 실제 전환율이 드러남.
3. 여성 73% 편중 — 유입 채널·크리에이티브가 특정 성별에 쏠렸는지, 의도된 타깃 설계인지 점검.

## 🧮 내일배움카드 교차분석 (melt · cast)

**AI+ NLP 5기** — 연령대별 내배카 보유율

| 연령대 | YES | NO | 합계 | YES 비율 |
|---|---|---|---|---|
| ~19 | 1 | 3 | 4 | 25.0% |
| 20-24 | 37 | 87 | 124 | 29.8% |
| 25-29 | 48 | 28 | 76 | 63.2% |
| 30-34 | 16 | 6 | 22 | 72.7% |
| 35-39 | 1 | 0 | 1 | 100.0% |
| 40+ | 4 | 1 | 5 | 80.0% |

신분(상태1)별 내배카 보유율

| 신분 | YES | NO | 합계 | YES 비율 |
|---|---|---|---|---|
| 대학(원)생 | 40 | 91 | 131 | 30.5% |
| 취업준비생 | 51 | 19 | 70 | 72.9% |
| 직장인/프리랜서 | 8 | 5 | 13 | 61.5% |
| 기타 | 5 | 2 | 7 | 71.4% |
| 알 수 없음 | 3 | 8 | 11 | 27.3% |

**백엔드 자바 26기** — 연령대별 내배카 보유율

| 연령대 | YES | NO | 합계 | YES 비율 |
|---|---|---|---|---|
| ~19 | 0 | 2 | 2 | 0.0% |
| 20-24 | 13 | 11 | 24 | 54.2% |
| 25-29 | 27 | 20 | 47 | 57.4% |
| 30-34 | 8 | 3 | 11 | 72.7% |
| 35-39 | 1 | 1 | 2 | 50.0% |
| 40+ | 1 | 2 | 3 | 33.3% |

신분(상태1)별 내배카 보유율

| 신분 | YES | NO | 합계 | YES 비율 |
|---|---|---|---|---|
| 대학(원)생 | 5 | 14 | 19 | 26.3% |
| 취업준비생 | 34 | 15 | 49 | 69.4% |
| 직장인/프리랜서 | 8 | 3 | 11 | 72.7% |
| 기타 | 2 | 5 | 7 | 28.6% |
| 알 수 없음 | 1 | 2 | 3 | 33.3% |

**그로스 마케팅 6기** — 연령대별 내배카 보유율

| 연령대 | YES | NO | 합계 | YES 비율 |
|---|---|---|---|---|
| 20-24 | 9 | 4 | 13 | 69.2% |
| 25-29 | 18 | 5 | 23 | 78.3% |
| 30-34 | 3 | 1 | 4 | 75.0% |
| 35-39 | 1 | 0 | 1 | 100.0% |

신분(상태1)별 내배카 보유율

| 신분 | YES | NO | 합계 | YES 비율 |
|---|---|---|---|---|
| 대학(원)생 | 2 | 2 | 4 | 50.0% |
| 취업준비생 | 22 | 7 | 29 | 75.9% |
| 직장인/프리랜서 | 5 | 0 | 5 | 100.0% |
| 기타 | 2 | 1 | 3 | 66.7% |

## 🧭 연령대별 합불상태 현황 (연령대 × 합불상태 · cast)

**AI+ NLP 5기** — 연령대별 합불상태 현황

| 연령대 | 검토전 | 대상아님 | 예비합격 | 합격 | 불합격 | 지원취소 | 합계 |
|---|---|---|---|---|---|---|---|
| ~19 | 0 | 7 | 0 | 0 | 1 | 1 | 9 |
| 20-24 | 4 | 167 | 11 | 14 | 29 | 6 | 231 |
| 25-29 | 6 | 85 | 6 | 10 | 21 | 4 | 132 |
| 30-34 | 0 | 28 | 1 | 6 | 6 | 0 | 41 |
| 35-39 | 0 | 3 | 0 | 0 | 1 | 0 | 4 |
| 40+ | 1 | 6 | 0 | 1 | 3 | 1 | 12 |

**백엔드 자바 26기** — 연령대별 합불상태 현황

| 연령대 | 검토전 | 대상아님 | 예비합격 | 합격 | 불합격 | 지원취소 | 합계 |
|---|---|---|---|---|---|---|---|
| ~19 | 0 | 4 | 1 | 0 | 0 | 0 | 5 |
| 20-24 | 1 | 53 | 1 | 6 | 2 | 2 | 65 |
| 25-29 | 1 | 44 | 2 | 19 | 7 | 7 | 80 |
| 30-34 | 1 | 19 | 0 | 4 | 1 | 0 | 25 |
| 35-39 | 0 | 3 | 0 | 2 | 1 | 0 | 6 |
| 40+ | 1 | 7 | 1 | 0 | 1 | 0 | 10 |

**그로스 마케팅 6기** — 연령대별 합불상태 현황

| 연령대 | 검토전 | 대상아님 | 합격 | 지원취소 | 합계 |
|---|---|---|---|---|---|
| ~19 | 0 | 1 | 0 | 0 | 1 |
| 20-24 | 3 | 25 | 3 | 2 | 33 |
| 25-29 | 6 | 23 | 8 | 0 | 37 |
| 30-34 | 3 | 10 | 0 | 0 | 13 |
| 35-39 | 1 | 2 | 0 | 0 | 3 |
| 40+ | 0 | 1 | 0 | 0 | 1 |

## 🧩 만나이 분포 (지원중 유저)

| 캠프 | 중앙값 | 평균 | Q1 | Q3 | min | max | n |
|---|---|---|---|---|---|---|---|
| AI+ NLP 5기 | 24.0 | 25.4 | 22.0 | 27.0 | 17.0 | 71.0 | 307 |
| 백엔드 자바 26기 | 25.0 | 27.8 | 23.0 | 29.0 | 18.0 | 70.0 | 134 |
| 그로스 마케팅 6기 | 26.0 | 26.9 | 23.0 | 29.0 | 19.0 | 50.0 | 75 |

> 일별 박스플롯(노트북 셀2 로직)은 HTML 캠프별 탭 참조.

## 🛠 생성 스크립트 (generate_daily_report.py)

> 아래 코드를 `daily report/generate_daily_report.py`로 두고 `python generate_daily_report.py` 실행 시
> 실행 시점 날짜로 HTML + 본 MD가 함께 재생성됩니다.

```python
# -*- coding: utf-8 -*-
"""
KDT 모객현황 데일리 리포트 생성기
- 소스: kdt 지원서 CSV (노트북 'kdt 모객현황 데이터 추출.ipynb' 로직 기반)
- 출력: {yymmdd}_daily-report.html / .md  (Summary + 부트캠프별 탭)
- 이중 출력: 레포 reports/ (GitHub용) + Obsidian 폴더 (보기용)
실행: python generate_daily_report.py
환경변수: KDT_DATA_DIR 로 CSV 폴더 경로 override 가능
"""
import pandas as pd, os, numpy as np, json
from datetime import datetime, timedelta

# CSV 데이터 소스 (로컬 전용 — GitHub에는 올라가지 않음). 환경변수로 override 가능.
FOLDER = os.environ.get("KDT_DATA_DIR", r"C:\Users\manid\OneDrive\바탕 화면\data_study\kdt")

# 출력 위치 (이중): ① 레포 reports/  ② Obsidian daily report 폴더(있으면)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(_SCRIPT_DIR, "reports")
OBSIDIAN_DIR = r"C:\Users\manid\Documents\whisky\멋쟁이사자처럼\업무 노트\daily report"
os.makedirs(REPORTS_DIR, exist_ok=True)

# 출력 모드 (환경변수 override): 기본은 reports/ + Obsidian 둘 다 HTML+MD
#  KDT_OBSIDIAN_ONLY=1 → Obsidian 폴더에만 출력 (reports/·GitHub 미반영)
#  KDT_MD_ONLY=1        → MD만 출력 (HTML 생략, MD 내 iframe도 생략)
OBSIDIAN_ONLY = os.environ.get("KDT_OBSIDIAN_ONLY") in ("1", "true", "True")
MD_ONLY       = os.environ.get("KDT_MD_ONLY") in ("1", "true", "True")
if OBSIDIAN_ONLY and os.path.isdir(OBSIDIAN_DIR):
    OUT_DIRS = [OBSIDIAN_DIR]
else:
    OUT_DIRS = [REPORTS_DIR] + ([OBSIDIAN_DIR] if os.path.isdir(OBSIDIAN_DIR) else [])
OUTDIR = REPORTS_DIR  # 하위 호환 (단일 참조용)

# 부트캠프 표시명 매핑 (파일 prefix -> 보기 좋은 이름)
DISPLAY = {
    "kdt-aiplus": "AI+ NLP 5기",
    "kdt-backendj-26th": "백엔드 자바 26기",
    "kdt-growth-6th": "그로스 마케팅 6기",
}

# 부트캠프별 목표 모객수(=목표 지원완료수) (표시명 기준)
TARGETS = {
    "AI+ NLP 5기": 96,
    "백엔드 자바 26기": 72,
    "그로스 마케팅 6기": 142,
}

# 부트캠프별 수강정원 (표시명 기준)
CAPACITY = {
    "AI+ NLP 5기": 40,
    "백엔드 자바 26기": 24,
    "그로스 마케팅 6기": 57,
}

# 부트캠프별 모객 기간 (시작, 마감) — YYYY-MM-DD
PERIODS = {
    "AI+ NLP 5기": ("2026-05-18", "2026-06-22"),
    "백엔드 자바 26기": ("2026-05-27", "2026-06-29"),
    "그로스 마케팅 6기": ("2026-06-16", "2026-07-19"),
}

def load(path):
    try: df = pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError: df = pd.read_csv(path, encoding='cp949')
    return df.fillna('')

def calc_age(birth, ref):
    if pd.isnull(birth) or pd.isnull(ref): return np.nan
    return ref.year - birth.year - ((ref.month, ref.day) < (birth.month, birth.day))

def age_band(a):
    if pd.isnull(a): return None
    a = int(a)
    if a < 20: return "~19"
    if a < 25: return "20-24"
    if a < 30: return "25-29"
    if a < 35: return "30-34"
    if a < 40: return "35-39"
    return "40+"
BANDS = ["~19","20-24","25-29","30-34","35-39","40+"]
# 합불상태 표시 순서 (심사 파이프라인 순)
STATUS_ORDER = ["검토전","대상아님","예비합격","합격","불합격","지원취소"]

def disp_name(fname):
    base = os.path.splitext(fname)[0]
    prefix = base.split('_')[0]
    return DISPLAY.get(prefix, prefix)

def analyze(f):
    df = load(os.path.join(FOLDER, f))
    name = disp_name(f)

    is_test = df['지원취소 사유'].str.lower().str.contains('test|테스트', case=False)
    is_internal = is_test | df['지원서 이메일'].str.contains('likelion.net', case=False) | df['가입 이메일'].str.contains('likelion.net', case=False)

    cond_completed = (df['지원완료일'] != '') & (df['지원상태'] != '지원취소') & (~is_internal)
    cond_applying  = df['합불상태'].isin(['검토전','대상아님']) & (df['지원완료일'] == '') & (~is_internal)
    cond_canceled  = (df['지원상태'] == '지원취소') & (df['지원완료일'] != '') & (~is_internal)

    완료 = int(cond_completed.sum()); 지원중 = int(cond_applying.sum()); 유효취소 = int(cond_canceled.sum())
    시작 = 완료 + 지원중 + 유효취소
    conv = round(완료/시작*100,1) if 시작 else 0
    cancel_rate = round(유효취소/시작*100,1) if 시작 else 0

    # 내배카 유효응답 풀 (yes/no, 내부제외, 지원완료·지원중)
    nbc_pool = df[df['내배카 보유'].str.lower().isin(['yes','no']) & (~is_internal) & df['지원상태'].isin(['지원완료','지원중'])].copy()
    nbc_pool['nbc'] = nbc_pool['내배카 보유'].str.lower()
    nbc_tot = len(nbc_pool); nbc_yes = int((nbc_pool['nbc']=='yes').sum())
    nbc_rate = round(nbc_yes/nbc_tot*100,1) if nbc_tot else 0

    # 날짜
    d = df.copy()
    d['최초작성일'] = pd.to_datetime(d['최초작성일'], errors='coerce')
    d['지원완료일'] = pd.to_datetime(d['지원완료일'], errors='coerce')
    d['생년월일']  = pd.to_datetime(d['생년월일'], errors='coerce')

    started = d[(d['합불상태'].isin(['검토전','대상아님']) & ~is_internal) |
                ((d['지원상태']=='지원완료') & d['지원완료일'].notna() & ~is_internal) |
                ((d['지원상태']=='지원취소') & d['지원완료일'].notna() & ~is_internal)]
    daily = {str(k): int(v) for k,v in started.groupby(started['최초작성일'].dt.date).size().items() if pd.notna(k)}
    comp = d[d['지원완료일'].notna() & (d['지원상태']!='지원취소') & ~is_internal]
    comp_daily = {str(k): int(v) for k,v in comp.groupby(comp['지원완료일'].dt.date).size().items() if pd.notna(k)}

    # 만나이 (지원중 풀 기준 - 노트북과 동일)
    app = d[d['합불상태'].isin(['검토전','대상아님']) & ~is_internal].copy()
    app['만나이'] = app.apply(lambda x: calc_age(x['생년월일'], x['최초작성일']), axis=1)
    ages = app['만나이'].dropna()
    age = {}
    if len(ages):
        age = {'median':float(ages.median()),'q1':float(ages.quantile(.25)),'q3':float(ages.quantile(.75)),
               'min':float(ages.min()),'max':float(ages.max()),'mean':round(float(ages.mean()),1),'n':int(len(ages))}
    age_band_hist = {b:int((app['만나이'].apply(age_band)==b).sum()) for b in BANDS}

    # === 일일 지원중 유저 만나이 분포 (박스플롯용 raw 값) — 노트북 셀2 로직 ===
    app_age = app.dropna(subset=['만나이']).copy()
    age_by_day = {}
    for dt, grp in app_age.groupby(app_age['최초작성일'].dt.date):
        if pd.notna(dt):
            age_by_day[str(dt)] = [int(x) for x in grp['만나이'].tolist()]
    age_all = [int(x) for x in app_age['만나이'].tolist()]

    # === 연령대 × 합불상태 피벗 (전체 비내부 지원자, 만나이 유효) ===
    prof = d[~is_internal].copy()
    prof['만나이'] = prof.apply(lambda x: calc_age(x['생년월일'], x['최초작성일']), axis=1)
    prof['연령대'] = prof['만나이'].apply(age_band)
    prof = prof[prof['연령대'].notna()]
    status_present = [s for s in STATUS_ORDER if s in set(prof['합불상태'])]
    age_status = []
    for b in BANDS:
        sub = prof[prof['연령대']==b]
        if len(sub)==0: continue
        age_status.append({'band':b,'total':int(len(sub)),
                           'counts':{s:int((sub['합불상태']==s).sum()) for s in status_present}})

    # 일별 박스플롯 통계 (q1/median/q3/min/max) — 정렬된 날짜 순서
    box_daily = []
    for dt in sorted(age_by_day):
        v = age_by_day[dt]
        box_daily.append({'q1':round(float(np.percentile(v,25)),1),'median':round(float(np.median(v)),1),
                          'q3':round(float(np.percentile(v,75)),1),'min':float(min(v)),'max':float(max(v)),'n':len(v)})

    # 목표 대비 달성율 + 수강정원 지표
    target = TARGETS.get(name)
    capacity = CAPACITY.get(name)
    ach_vs_start = round(완료/시작*100,1) if 시작 else 0
    ach_vs_target = round(완료/target*100,1) if target else None
    competition = round(시작/capacity,1) if capacity else None   # 경쟁률(지원시작/정원)
    fill_vs_capacity = round(완료/capacity*100,1) if capacity else None  # 정원 대비 완료(%)

    # === 모객 기간 기반 마감 도달 전망 (트렌드 × 종결일) ===
    proj = None
    period = PERIODS.get(name)
    if period:
        ps = datetime.strptime(period[0], '%Y-%m-%d').date()
        pe = datetime.strptime(period[1], '%Y-%m-%d').date()
        today_d = datetime.now().date()
        days_total = (pe - ps).days + 1
        days_elapsed = max(0, min((today_d - ps).days + 1, days_total))
        days_left = max((pe - today_d).days, 0)
        time_pct = round(days_elapsed/days_total*100) if days_total else 0
        # 완료 페이스: 7일 이상이면 최근 7일(달력) 평균, 미만이면 경과 전체 평균
        if days_elapsed >= 7:
            recent = sum(comp_daily.get(str(today_d - timedelta(days=i)), 0) for i in range(7))
            pace = round(recent/7, 2)
        else:
            pace = round(완료/days_elapsed, 2) if days_elapsed > 0 else 0
        projected = int(round(완료 + days_left * pace))
        proj_tpct = round(projected/target*100) if target else None
        early = days_elapsed < 7
        if target and 완료 >= target:
            tier, label = 'done', '목표 조기 달성'
        elif target and projected >= target:
            tier, label = 'safe', '마감 내 목표 달성 전망'
        elif target and projected >= target*0.9:
            tier, label = 'tight', '목표 근접·미달 위험'
        elif target:
            tier, label = 'risk', '마감 내 목표 미달 전망'
        else:
            tier, label = 'na', '목표 미설정'
        proj = {'start':period[0],'end':period[1],'days_total':days_total,'days_elapsed':days_elapsed,
                'days_left':days_left,'time_pct':time_pct,'pace':pace,'projected':projected,
                'proj_tpct':proj_tpct,'tier':tier,'label':label,'early':early}

    # === melt/cast 교차분석: 내배카 풀에 속성 join ===
    p = nbc_pool.copy()
    p['최초작성일'] = pd.to_datetime(p['최초작성일'], errors='coerce')
    p['생년월일']  = pd.to_datetime(p['생년월일'], errors='coerce')
    p['만나이'] = p.apply(lambda x: calc_age(x['생년월일'], x['최초작성일']), axis=1)
    p['연령대'] = p['만나이'].apply(age_band)
    p['상태1_norm'] = p['상태1'].replace('', '알 수 없음')
    p['성별_norm'] = p['성별'].map({'male':'남성','female':'여성'}).fillna('미상')

    def cast(col, order=None):
        g = p.groupby([col,'nbc']).size().unstack(fill_value=0)
        for c in ['yes','no']:
            if c not in g.columns: g[c]=0
        g['합계'] = g['yes']+g['no']
        g['yes_rate'] = (g['yes']/g['합계']*100).round(1)
        if order: g = g.reindex([o for o in order if o in g.index])
        rows=[]
        for idx,r in g.iterrows():
            if r['합계']==0: continue
            rows.append({'key':str(idx),'yes':int(r['yes']),'no':int(r['no']),
                         'tot':int(r['합계']),'yes_rate':float(r['yes_rate'])})
        return rows

    by_age    = cast('연령대', BANDS)
    by_gender = cast('성별_norm', ['남성','여성','미상'])
    status_order = ['대학(원)생','취업준비생','직장인/프리랜서','기타','알 수 없음']
    by_status = cast('상태1_norm', status_order)

    return {
        'name':name,'file':f,'total_rows':len(df),
        '시작':시작,'지원중':지원중,'완료':완료,'유효취소':유효취소,
        'conv':conv,'cancel_rate':cancel_rate,
        'nbc_tot':nbc_tot,'nbc_yes':nbc_yes,'nbc_rate':nbc_rate,
        'daily':daily,'comp_daily':comp_daily,'age':age,'age_band':age_band_hist,
        'gender_pool':{'남성':int((app['성별']=='male').sum()),'여성':int((app['성별']=='female').sum())},
        'by_age':by_age,'by_gender':by_gender,'by_status':by_status,
        'age_by_day':age_by_day,'age_all':age_all,'box_daily':box_daily,
        'age_status':age_status,'status_present':status_present,
        'target':target,'ach_vs_start':ach_vs_start,'ach_vs_target':ach_vs_target,
        'capacity':capacity,'competition':competition,'fill_vs_capacity':fill_vs_capacity,
        'proj':proj,
    }

camps = [analyze(f) for f in sorted(os.listdir(FOLDER)) if f.endswith('.csv')]
DATA = {'generated': datetime.now().strftime('%Y-%m-%d %H:%M'), 'camps': camps}

# ---------- HTML 생성 ----------
import re as _re
yymmdd = datetime.now().strftime('%y%m%d')
out_path = os.path.join(OUTDIR, f"{yymmdd}_daily-report.html")

# ---------- 직전 리포트 로드 (전일 대비 경향성 분석용) ----------
def load_prev_data(today_yymmdd):
    """REPORTS_DIR + Obsidian 폴더에서 오늘 이전 날짜의 최신 리포트 HTML을 찾아 embedded DATA 추출."""
    search_dirs = [d for d in (REPORTS_DIR, OBSIDIAN_DIR) if os.path.isdir(d)]
    found = {}  # yymmdd -> path (최신 dir 우선)
    for d in search_dirs:
        for fn in os.listdir(d):
            m = _re.match(r'(\d{6})_daily-report\.html$', fn)
            if m and m.group(1) < today_yymmdd:
                found.setdefault(m.group(1), os.path.join(d, fn))
    if not found:
        return None, None
    prev = max(found)
    try:
        html = open(found[prev], encoding='utf-8').read()
        mm = _re.search(r'const DATA = (\{.*?\});\s*\nChart\.register', html, _re.S)
        if not mm:
            return prev, None
        return prev, json.loads(mm.group(1))
    except Exception:
        return prev, None

prev_yymmdd, prev_data = load_prev_data(yymmdd)
prev_by_name = {c['name']: c for c in prev_data['camps']} if prev_data else {}

def status_tot(camp):
    t = {}
    for r in camp.get('age_status', []):
        for s, n in r['counts'].items():
            t[s] = t.get(s, 0) + n
    return t

def build_trend(c):
    """전일 대비 경향성 — 비판적 사고 기반 인사이트 (2~4개)."""
    prev = prev_by_name.get(c['name'])
    if not prev:
        return None
    # 목표가 바뀌었을 수 있으므로 직전 달성율은 '현재 목표' 기준으로 재계산(공정 비교)
    prev_ach = round(prev.get('완료',0)/c['target']*100,1) if c['target'] else None
    d = {
        'start': c['시작'] - prev.get('시작', 0),
        'comp':  c['완료'] - prev.get('완료', 0),
        'ing':   c['지원중'] - prev.get('지원중', 0),
        'conv':  round(c['conv'] - prev.get('conv', 0), 1),
        'nbc':   round(c['nbc_rate'] - prev.get('nbc_rate', 0), 1),
        'tgt':   round((c['ach_vs_target'] or 0) - (prev_ach or 0), 1),
    }
    st_now, st_prev = status_tot(c), status_tot(prev)
    d_pass = st_now.get('합격', 0) - st_prev.get('합격', 0)
    d_fail = st_now.get('불합격', 0) - st_prev.get('불합격', 0)
    d_pre  = st_now.get('예비합격', 0) - st_prev.get('예비합격', 0)
    review_delta = d_pass + d_fail + d_pre
    ins = []
    # ① 유입량 vs 전환 품질 (가장 비판적으로 봐야 할 지점)
    if d['start'] > 0 and d['conv'] < 0:
        ins.append(f"<b>신규 지원 +{d['start']}명인데 완료전환율 {d['conv']}pp 하락</b> — 유입은 늘었으나 완료로 이어지지 않음. '숫자 증가'에 안심 말고 유입 채널 품질·지원서 이탈 지점을 의심해야 함.")
    elif d['start'] > 0 and d['conv'] >= 0:
        ins.append(f"<b>지원 +{d['start']}명 · 전환율 {('+' if d['conv']>=0 else '')}{d['conv']}pp 동반</b> — 양·질 함께 개선. 단, 1일 변동이라 추세 확정 전 2~3일 더 관찰 필요.")
    else:
        ins.append(f"<b>신규 지원 {d['start']}명(정체·감소)</b> — 모집 모멘텀 둔화. 마감 임박 효과 없는지, 매체 소진인지 분리 점검.")
    # ② 완료 증가의 '출처' — 신규 완료인지 심사 진행인지
    if review_delta > 0:
        ins.append(f"<b>심사 진행 {review_delta}건</b>(합격 {d_pass:+d}·불합격 {d_fail:+d}·예비 {d_pre:+d}) vs 지원완료 {d['comp']:+d} — 완료수 증가가 '신규 완료'인지 '심사 결과 반영'인지 구분해야 전환율 해석이 정확.")
    elif d['comp'] != 0:
        ins.append(f"<b>지원완료 {d['comp']:+d}명</b> — 심사 결과 변동은 없음. 순수 신규 완료 흐름.")
    # ③ 목표 달성율 진척 vs 페이스
    if c['target']:
        rem = c['target'] - c['완료']
        if d['comp'] > 0 and rem > 0:
            eta = round(rem / d['comp'])
            ins.append(f"<b>목표 달성율 {prev_ach}→{c['ach_vs_target']}% ({d['tgt']:+}pp)</b> — 오늘 +{d['comp']}명 페이스면 잔여 {rem}명에 약 {eta}일. 잔여 모집기간과 대조해 '달성 가능 페이스'인지 판단.")
        elif rem <= 0:
            ins.append(f"목표 도달 유지(달성율 {c['ach_vs_target']}%) — 점검 축을 완료 수 → 등록 전환·적합도로 이동.")
    # ④ 세그먼트 이동 신호
    if abs(d['nbc']) >= 3:
        ins.append(f"<b>내배카 보유율 {d['nbc']:+}pp 변동</b> — 신규 유입의 연령·신분 세그먼트가 이동했을 가능성. 연령대×합불상태/내배카 교차표로 어느 층이 늘었는지 확인.")
    return {'d': d, 'review': {'pass': d_pass, 'fail': d_fail, 'pre': d_pre}, 'ins': ins[:4]}

trends = {c['name']: build_trend(c) for c in camps}
has_trend = prev_data is not None and any(trends.values())

tot_start = sum(c['시작'] for c in camps)
tot_comp  = sum(c['완료'] for c in camps)
tot_ing   = sum(c['지원중'] for c in camps)
tot_nbc_t = sum(c['nbc_tot'] for c in camps)
tot_nbc_y = sum(c['nbc_yes'] for c in camps)
avg_conv  = round(tot_comp/tot_start*100,1) if tot_start else 0
nbc_rate_all = round(tot_nbc_y/tot_nbc_t*100,1) if tot_nbc_t else 0

HTML = """<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KDT 모객현황 데일리 리포트 · __YYMMDD__</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@sgratzl/chartjs-chart-boxplot@4.4.4/build/index.umd.min.js"></script>
<style>
:root{--bg:#0f1115;--card:#181b22;--card2:#1f232c;--line:#2a2f3a;--txt:#e6e8ec;--sub:#9aa3b2;--accent:#ff7a45;--blue:#4dabf7;--green:#51cf66;--red:#ff6b6b;--yellow:#ffd43b;--purple:#b197fc}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;line-height:1.5;padding:28px 20px;max-width:1180px;margin:0 auto}
header{border-bottom:2px solid var(--accent);padding-bottom:14px}
h1{font-size:23px;font-weight:800;letter-spacing:-.5px}
.meta{color:var(--sub);font-size:13px;margin-top:6px}
.tag{display:inline-block;background:var(--card2);color:var(--sub);font-size:11px;padding:2px 8px;border-radius:10px;margin-right:6px}
.tabs{display:flex;gap:6px;margin:18px 0 22px;flex-wrap:wrap;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:10;border-bottom:1px solid var(--line)}
.tab{background:var(--card);border:1px solid var(--line);color:var(--sub);padding:9px 16px;border-radius:9px;cursor:pointer;font-size:13.5px;font-weight:600;transition:.15s}
.tab:hover{color:var(--txt)}
.tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.panel{display:none}.panel.active{display:block}
h2{font-size:17px;margin:30px 0 12px;padding-left:10px;border-left:4px solid var(--accent)}
h3{font-size:13.5px;color:var(--sub);margin:0 0 8px;font-weight:600}
.grid{display:grid;gap:14px}
.kpi-grid{grid-template-columns:repeat(auto-fit,minmax(140px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .label{font-size:12px;color:var(--sub)}.kpi .val{font-size:26px;font-weight:800;margin-top:4px}.kpi .sub{font-size:12px;color:var(--sub);margin-top:2px}
.acc{color:var(--accent)}.up{color:var(--green)}.down{color:var(--red)}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:6px}
th,td{padding:9px 11px;text-align:center;border-bottom:1px solid var(--line)}
th{background:var(--card2);color:var(--sub);font-weight:600;font-size:12px}
td.name{text-align:left;font-weight:700}
.two{grid-template-columns:1fr 1fr}@media(max-width:760px){.two{grid-template-columns:1fr}}
canvas{max-height:300px}
.pill{font-size:11px;padding:2px 7px;border-radius:8px;font-weight:700}
.pill.g{background:rgba(81,207,102,.15);color:var(--green)}.pill.r{background:rgba(255,107,107,.15);color:var(--red)}
.insight{background:var(--card2);border-left:3px solid var(--blue);padding:11px 15px;border-radius:8px;margin-bottom:10px;font-size:13.5px}
.insight.warn{border-left-color:var(--yellow)}.insight.alert{border-left-color:var(--red)}
.insight b{color:var(--accent)}.insight .h{font-weight:800;display:block;margin-bottom:3px;color:var(--txt)}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);color:var(--sub);font-size:12px}
.barmini{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:12px}
.barmini .t{width:78px;color:var(--sub);text-align:right;flex-shrink:0}
.barmini .bar{flex:1;height:18px;background:var(--card2);border-radius:5px;overflow:hidden;position:relative}
.barmini .bar>span{display:block;height:100%}
.barmini .v{width:96px;flex-shrink:0;font-size:11px;color:var(--sub)}
.comment-card{border-left:3px solid var(--yellow);background:rgba(255,212,59,.05)}
.comments{margin:4px 0 0;padding-left:0;list-style:none}
.comments li{position:relative;padding:8px 10px 8px 26px;font-size:13.5px;border-bottom:1px solid var(--line);line-height:1.55}
.comments li:last-child{border-bottom:none}
.comments li::before{content:'▹';position:absolute;left:6px;top:8px;color:var(--yellow);font-weight:700}
.comments b{color:var(--accent)}
</style></head><body>
<header><h1>📊 KDT 모객현황 데일리 리포트</h1>
<div class="meta"><span class="tag">기준일 __DATE__</span><span class="tag">소스: kdt 지원서 CSV __NCAMP__종</span><span class="tag">내부직원·테스트 제외</span><span class="tag">TEST 출력본</span></div>
</header>
<div class="tabs" id="tabs"></div>
__PANELS__
<footer>생성 __GEN__ · 소스 노트북 <code>kdt 모객현황 데이터 추출.ipynb</code> 로직 기반 · 내배카 비율은 yes/no 유효응답(지원완료·지원중) 기준 · 상태1 공란은 '알 수 없음' 처리<br>⚠️ TEST 출력본 — 지표 정의·디밸롭 협의 후 정식화 예정</footer>
<script>
const DATA = __DATAJSON__;
Chart.register(ChartDataLabels);
const C={txt:'#e6e8ec',sub:'#9aa3b2',acc:'#ff7a45',blue:'#4dabf7',green:'#51cf66',red:'#ff6b6b',yellow:'#ffd43b',purple:'#b197fc',line:'#2a2f3a'};
function baseOpt(){return{responsive:true,plugins:{legend:{labels:{color:C.sub,font:{size:11}}},datalabels:{display:false}},scales:{x:{ticks:{color:C.sub,maxRotation:60,font:{size:9}},grid:{color:C.line}},y:{ticks:{color:C.sub},grid:{color:C.line},beginAtZero:true}}};}
function cum(o){let k=Object.keys(o).sort(),s=0,r=[];for(const x of k){s+=o[x];r.push(s);}return {k,r};}

// 탭 — URL 해시(#slug)로 탭별 공유/특정 가능
const tabs=document.getElementById('tabs');
const names=['Summary',...DATA.camps.map(c=>c.name)];
function slugify(n){return n.toLowerCase().replace(/[^\\p{L}\\p{N}]+/gu,'-').replace(/^-+|-+$/g,'');}
const slugs=names.map((n,i)=>i===0?'summary':slugify(n));
names.forEach((n,i)=>{const b=document.createElement('div');b.className='tab'+(i===0?' active':'');b.id='tab-'+slugs[i];b.textContent=n;b.onclick=()=>{if(location.hash.slice(1)!==slugs[i])location.hash=slugs[i];else sel(i);};tabs.appendChild(b);});
function sel(i){if(i<0||i>=names.length)i=0;document.querySelectorAll('.tab').forEach((t,j)=>t.classList.toggle('active',j===i));document.querySelectorAll('.panel').forEach((p,j)=>p.classList.toggle('active',j===i));}
function selFromHash(){let h=decodeURIComponent((location.hash||'').replace(/^#/,'')).toLowerCase();let i=slugs.indexOf(h);if(i<0){const m=h.match(/^tab-?(\\d+)$/);if(m)i=Number(m[1]);else if(/^\\d+$/.test(h))i=Number(h);}sel(i<0?0:i);}
window.addEventListener('hashchange',selFromHash);

const charts=[];
function mkLine(id,startO,compO,proj){
  const s=cum(startO),c=cum(compO);
  const labels=s.k.slice();
  const startData=s.r.slice();
  const compData=s.k.map(d=>c.k.includes(d)?c.r[c.k.indexOf(d)]:null);
  let projData=labels.map(_=>null);
  let showSet=new Set();
  if(proj && proj.pace>0 && proj.end){
    const lastComp = c.r.length? c.r[c.r.length-1] : 0;           // 현재 누적 완료
    projData[projData.length-1]=lastComp;                          // 마지막 실측점에 앵커
    let dt=new Date(labels[labels.length-1]+'T00:00:00');
    const end=new Date(proj.end+'T00:00:00');
    let acc=lastComp;
    while(true){ dt.setDate(dt.getDate()+1); if(dt>end) break;
      labels.push(dt.toISOString().slice(0,10)); startData.push(null); compData.push(null);
      acc=acc+proj.pace; projData.push(Math.round(acc)); }
    const fut=projData.map((v,i)=>v!=null?i:-1).filter(i=>i>=0).slice(1); // 앵커 제외 미래점
    const step=Math.max(1,Math.ceil(fut.length/12));
    fut.forEach((idx,k)=>{ if(k%step===0) showSet.add(idx); });
    if(fut.length) showSet.add(fut[fut.length-1]);                  // 마감 예상치는 항상 표기
  }
  const ds=[
    {label:'누적 지원시작',data:startData,borderColor:C.acc,backgroundColor:'transparent',tension:.25,pointRadius:2,pointBackgroundColor:C.acc,
     datalabels:{display:ctx=>startData[ctx.dataIndex]!=null,align:'top',anchor:'end',color:C.acc,font:{weight:'bold',size:8},formatter:v=>v}},
    {label:'누적 지원완료',data:compData,borderColor:C.blue,backgroundColor:'transparent',tension:.25,pointRadius:2,pointBackgroundColor:C.blue,spanGaps:true,
     datalabels:{display:ctx=>compData[ctx.dataIndex]!=null,align:'bottom',anchor:'start',color:C.blue,font:{weight:'bold',size:8},formatter:v=>v}}
  ];
  if(showSet.size){
    ds.push({label:'예상 완료(시뮬·점선)',data:projData,borderColor:C.green,borderDash:[6,4],backgroundColor:'transparent',tension:0,spanGaps:true,
      pointRadius:ctx=>showSet.has(ctx.dataIndex)?2.5:0,pointBackgroundColor:C.green,
      datalabels:{display:ctx=>showSet.has(ctx.dataIndex),align:'top',anchor:'end',color:C.green,font:{weight:'bold',size:8},formatter:v=>v}});
  }
  charts.push(new Chart(document.getElementById(id),{type:'line',data:{labels,datasets:ds},options:baseOpt()}));
}
function mkDailyBar(id,startO){
  const k=Object.keys(startO).sort();
  charts.push(new Chart(document.getElementById(id),{type:'bar',data:{labels:k,datasets:[
    {label:'일별 신규 지원시작',data:k.map(d=>startO[d]),backgroundColor:C.acc,
     datalabels:{display:true,anchor:'end',align:'end',color:C.sub,font:{size:9},formatter:v=>v}}]},options:baseOpt()}));
}
function mkNbcCross(id,rows,labelKey){
  charts.push(new Chart(document.getElementById(id),{type:'bar',data:{labels:rows.map(r=>r.key),datasets:[
    {label:'내배카 YES',data:rows.map(r=>r.yes),backgroundColor:C.green,stack:'s',
     datalabels:{display:true,color:'#0f1115',font:{weight:'bold',size:11},formatter:v=>v>0?v:''}},
    {label:'내배카 NO',data:rows.map(r=>r.no),backgroundColor:C.red,stack:'s',
     datalabels:{display:true,color:'#0f1115',font:{weight:'bold',size:11},formatter:v=>v>0?v:''}},
    {type:'line',label:'YES 비율(%)',data:rows.map(r=>r.yes_rate),borderColor:C.yellow,backgroundColor:'transparent',yAxisID:'y2',tension:.2,pointRadius:3,pointBackgroundColor:C.yellow,
     datalabels:{display:true,align:'top',color:C.yellow,font:{weight:'bold',size:11},formatter:v=>v.toFixed(0)+'%'}}]},
    options:{responsive:true,plugins:{legend:{labels:{color:C.sub,font:{size:11}}},datalabels:{}},scales:{
      x:{stacked:true,ticks:{color:C.sub,font:{size:11}},grid:{color:C.line}},
      y:{stacked:true,ticks:{color:C.sub},grid:{color:C.line},beginAtZero:true,title:{display:true,text:'명',color:C.sub}},
      y2:{position:'right',min:0,max:100,ticks:{color:C.yellow,callback:v=>v+'%'},grid:{drawOnChartArea:false},title:{display:true,text:'YES 비율',color:C.yellow}}}}}));
}
// 박스플롯 통계 레이블 플러그인 (q1/median/q3/min/max) — 박스 우측에 배경 픽셀과 함께 표기
function boxStatLabels(stats,keys,fs){return {id:'boxlbl'+Math.random(),afterDatasetsDraw(c){
  const meta=c.getDatasetMeta(0), y=c.scales.y, ctx=c.ctx; if(!y)return;
  const F=fs||11; ctx.save();ctx.font='bold '+F+'px sans-serif';ctx.textBaseline='middle';ctx.textAlign='left';
  const cfg={max:['max ',C.sub],q3:['Q3 ',C.red],median:['중앙 ',C.acc],q1:['Q1 ',C.blue],min:['min ',C.sub]};
  stats.forEach((s,i)=>{const el=meta.data[i]; if(!el)return;
    const hw=(el.width||el.getProps?(el.getProps(['width']).width||40):40)/2;
    const x=el.x+hw+8;
    keys.forEach(k=>{ if(s[k]==null)return; const o=cfg[k]; const yy=y.getPixelForValue(s[k]);
      const txt=o[0]+s[k], w=ctx.measureText(txt).width;
      ctx.fillStyle='rgba(15,17,21,.78)';
      ctx.fillRect(x-3, yy-F/2-2, w+6, F+4);
      ctx.fillStyle=o[1]; ctx.fillText(txt, x, yy);});});
  ctx.restore();}};}
function mkBoxCompare(id){
  const labels=DATA.camps.map(c=>c.name), data=DATA.camps.map(c=>c.age_all);
  const stats=DATA.camps.map(c=>c.age);
  charts.push(new Chart(document.getElementById(id),{type:'boxplot',data:{labels,datasets:[
    {label:'만나이 분포',data,backgroundColor:'rgba(77,171,247,.35)',borderColor:C.blue,borderWidth:2,
     itemRadius:2,itemStyle:'circle',itemBackgroundColor:'rgba(255,122,69,.5)',outlierBackgroundColor:C.red,medianColor:C.acc,
     datalabels:{display:false}}]},
    options:{responsive:true,layout:{padding:{right:80}},plugins:{legend:{display:false},datalabels:{display:false}},scales:{x:{ticks:{color:C.txt,font:{size:12}},grid:{color:C.line}},y:{ticks:{color:C.sub},grid:{color:C.line},title:{display:true,text:'만나이',color:C.sub}}}},
    plugins:[boxStatLabels(stats,['max','q3','median','q1','min'],11)]}));
}
const medLine=(yval)=>({id:'medLine'+Math.random(),afterDatasetsDraw(c){
  const {ctx,chartArea:{left,right},scales:{y}}=c; if(!y)return; const yy=y.getPixelForValue(yval);
  ctx.save();ctx.strokeStyle=C.sub;ctx.setLineDash([5,4]);ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(left,yy);ctx.lineTo(right,yy);ctx.stroke();
  ctx.setLineDash([]);ctx.fillStyle=C.sub;ctx.font='11px sans-serif';ctx.fillText('전체 중앙값 '+yval+'세',left+6,yy-4);ctx.restore();}});
function mkBoxDaily(id,byDay,overallMedian,boxStats){
  const labels=Object.keys(byDay).sort(), data=labels.map(d=>byDay[d]);
  charts.push(new Chart(document.getElementById(id),{type:'boxplot',data:{labels,datasets:[
    {label:'일별 만나이',data,backgroundColor:'rgba(177,151,252,.3)',borderColor:C.purple,borderWidth:1.5,
     itemRadius:1.5,itemStyle:'circle',itemBackgroundColor:'rgba(255,122,69,.45)',outlierBackgroundColor:C.red,medianColor:C.acc,
     datalabels:{display:false}}]},
    options:{responsive:true,plugins:{legend:{display:false},datalabels:{display:false}},scales:{
      x:{ticks:{color:C.sub,maxRotation:60,font:{size:8}},grid:{color:C.line}},
      y:{ticks:{color:C.sub},grid:{color:C.line},title:{display:true,text:'만나이',color:C.sub}}}},
    plugins:[medLine(overallMedian),boxDailyLabels(boxStats)]}));
}
// 일별 박스 위/아래에 Q3/중앙/Q1 작게 표기
function boxDailyLabels(stats){return {id:'bdl'+Math.random(),afterDatasetsDraw(c){
  const meta=c.getDatasetMeta(0), y=c.scales.y, ctx=c.ctx; if(!y)return;
  ctx.save();ctx.font='7px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
  stats.forEach((s,i)=>{const el=meta.data[i]; if(!el)return; const x=el.x;
    ctx.fillStyle=C.red;  ctx.fillText(s.q3,     x, y.getPixelForValue(s.q3)-6);
    ctx.fillStyle=C.acc;  ctx.fillText(s.median, x, y.getPixelForValue(s.median)-0.5);
    ctx.fillStyle=C.blue; ctx.fillText(s.q1,     x, y.getPixelForValue(s.q1)+6);});
  ctx.restore();}};}
// 연령대 × 합불상태 스택 가로막대 (각 세그먼트 명수 표기)
function mkAgeStatus(id,rows,statuses){
  const STC={'검토전':C.sub,'대상아님':C.blue,'예비합격':C.yellow,'합격':C.green,'불합격':C.red,'지원취소':'#7a7f8a'};
  const labels=rows.map(r=>r.band+'세');
  const ds=statuses.map(s=>({label:s,data:rows.map(r=>r.counts[s]||0),backgroundColor:STC[s]||C.sub,stack:'s',
    datalabels:{display:true,color:'#0f1115',font:{weight:'bold',size:10},formatter:v=>v>0?v:''}}));
  charts.push(new Chart(document.getElementById(id),{type:'bar',data:{labels,datasets:ds},
    options:{indexAxis:'y',responsive:true,plugins:{legend:{labels:{color:C.sub,font:{size:11}}},datalabels:{}},scales:{
      x:{stacked:true,ticks:{color:C.sub},grid:{color:C.line},title:{display:true,text:'명',color:C.sub}},
      y:{stacked:true,ticks:{color:C.txt,font:{size:12}},grid:{color:C.line}}}}}));
}
function mkStatusBar(id,rows){
  charts.push(new Chart(document.getElementById(id),{type:'bar',data:{labels:rows.map(r=>r.key+' (n='+r.tot+')'),datasets:[
    {label:'내배카 보유율(%)',data:rows.map(r=>r.yes_rate),backgroundColor:rows.map(r=>r.key==='알 수 없음'?C.sub:C.purple),
     datalabels:{display:true,anchor:'end',align:'end',color:C.txt,font:{weight:'bold',size:12},formatter:v=>v.toFixed(1)+'%'}}]},
    options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},datalabels:{}},scales:{
      x:{min:0,max:100,ticks:{color:C.sub,callback:v=>v+'%'},grid:{color:C.line}},
      y:{ticks:{color:C.txt,font:{size:12}},grid:{color:C.line}}}}}));
}
__INIT__
</script></body></html>"""

# Summary 패널
def fmt(n): return f"{n:,}"

# 전일 대비 경향성 섹션 빌드
def dspan(v, suffix=''):
    if v > 0:  return f"<span class='up'>▲{v}{suffix}</span>"
    if v < 0:  return f"<span class='down'>▼{abs(v)}{suffix}</span>"
    return f"<span style='color:var(--sub)'>±0{suffix}</span>"

if not has_trend:
    trend_html = """<h2>전일 대비 경향성</h2><div class="insight">직전 리포트를 찾지 못해 비교를 생략합니다. (reports 폴더에 이전 날짜 리포트가 있으면 다음 실행부터 자동 비교)</div>"""
else:
    trows, tcards = "", ""
    for c in camps:
        tr = trends.get(c['name'])
        if not tr: continue
        d, rv = tr['d'], tr['review']
        review_txt = f"합{rv['pass']:+d} 불{rv['fail']:+d} 예{rv['pre']:+d}"
        trows += (f"<tr><td class='name'>{c['name']}</td><td>{dspan(d['start'])}</td><td>{dspan(d['comp'])}</td>"
                  f"<td>{dspan(d['conv'],'pp')}</td><td>{dspan(d['nbc'],'pp')}</td><td>{dspan(d['tgt'],'pp')}</td>"
                  f"<td style='font-size:12px'>{review_txt}</td></tr>")
        lis = "".join(f"<li>{x}</li>" for x in tr['ins'])
        tcards += f"<div class='card comment-card' style='margin-top:10px'><h3>📊 {c['name']} — 전일 대비 경향성</h3><ul class='comments'>{lis}</ul></div>"
    trend_html = f"""<h2>전일 대비 경향성 · 직전 {prev_yymmdd} 대비 (비판적 분석)</h2>
<div class="card"><h3>핵심 지표 전일 대비 변화 (Δ)</h3>
<table><thead><tr><th>캠프</th><th>지원시작</th><th>지원완료</th><th>완료전환율</th><th>내배카</th><th>목표달성율</th><th>심사진행<br>(합/불/예비)</th></tr></thead><tbody>{trows}</tbody></table>
<p style="font-size:12px;color:var(--sub);margin-top:8px">Δ = 오늘 − 직전 리포트. pp = 퍼센트포인트. ▲ 증가 / ▼ 감소. 1일 변동이므로 추세 확정 전 노이즈 가능성 유의.</p></div>
{tcards}"""

# 모집 마감 전망 (Summary 테이블)
_TIER_PILL = {'done':'g','safe':'g','tight':'y','risk':'r','na':''}
_TIER_PILLCSS = {'g':'pill g','y':'pill','r':'pill r'}
def _proj_pill(tier, label):
    p = _TIER_PILL.get(tier, '')
    if p == 'g': return f"<span class='pill g'>{label}</span>"
    if p == 'r': return f"<span class='pill r'>{label}</span>"
    if p == 'y': return f"<span class='pill' style='background:rgba(255,212,59,.15);color:var(--yellow)'>{label}</span>"
    return label
_prows = ""
for c in camps:
    pj = c.get('proj')
    if not pj:
        _prows += f"<tr><td class='name'>{c['name']}</td><td colspan='8' style='color:var(--sub)'>모집기간 미설정</td></tr>"
        continue
    proj_disp = f"{pj['projected']} ({pj['proj_tpct']}%)" if pj.get('proj_tpct') is not None else f"{pj['projected']}"
    early = " ⚠️초기" if pj['early'] else ""
    _prows += (f"<tr><td class='name'>{c['name']}</td><td>{pj['start']}~{pj['end']}</td><td><b>D-{pj['days_left']}</b></td>"
               f"<td>{pj['time_pct']}%</td><td>{c['완료']}/{c['target'] if c.get('target') else '—'}</td><td>{pj['pace']}</td><td>{proj_disp}{early}</td>"
               f"<td>{_proj_pill(pj['tier'], pj['label'])}</td></tr>")
proj_summary_html = f"""<h2>모집 마감 전망 (트렌드 × 종결일)</h2>
<div class="card"><table>
<thead><tr><th>캠프</th><th>모집기간</th><th>마감</th><th>경과</th><th>완료/목표</th><th>페이스<br>(명/일)</th><th>예상 도달<br>(목표대비)</th><th>전망</th></tr></thead>
<tbody>{_prows}</tbody></table>
<p style="font-size:12px;color:var(--sub);margin-top:8px">예상 도달 = 현재 완료 + 잔여일 × 최근 완료 페이스(7일↑은 최근 7일 평균, 미만은 경과 전체 평균). ⚠️초기 = 모집 7일 미만, 추정 신뢰도 낮음.</p></div>"""

summary = f"""<div class="panel active" id="p0">
<h2>전체 요약</h2>
<div class="grid kpi-grid">
  <div class="card kpi"><div class="label">총 지원시작</div><div class="val">{fmt(tot_start)}</div><div class="sub">{' · '.join(c['name']+' '+str(c['시작']) for c in camps)}</div></div>
  <div class="card kpi"><div class="label">지원완료</div><div class="val acc">{fmt(tot_comp)}</div><div class="sub">완료전환 {avg_conv}%</div></div>
  <div class="card kpi"><div class="label">미완료(지원중)</div><div class="val down">{fmt(tot_ing)}</div><div class="sub">전체의 {round(tot_ing/tot_start*100)}% 적체</div></div>
  <div class="card kpi"><div class="label">내배카 보유율</div><div class="val">{nbc_rate_all}%</div><div class="sub">유효응답 {fmt(tot_nbc_t)}명</div></div>
  <div class="card kpi"><div class="label">대상 캠프</div><div class="val">{len(camps)}</div><div class="sub">개</div></div>
</div>
{proj_summary_html}
{trend_html}
<h2>캠프별 퍼널 비교</h2>
<div class="card"><table>
<thead><tr><th>캠프</th><th>지원시작</th><th>지원중</th><th>지원완료</th><th>완료전환율</th><th>유효취소</th><th>내배카 보유율</th></tr></thead><tbody>
"""
maxconv = max(c['conv'] for c in camps)
for c in camps:
    pill = 'g' if c['conv']==maxconv else 'r'
    summary += f"<tr><td class='name'>{c['name']}</td><td>{c['시작']}</td><td>{c['지원중']}</td><td><b class='acc'>{c['완료']}</b></td><td><span class='pill {pill}'>{c['conv']}%</span></td><td>{c['유효취소']} ({c['cancel_rate']}%)</td><td>{c['nbc_rate']}%</td></tr>\n"
agestat = ""
for c in camps:
    a=c['age']
    agestat += f"<tr><td class='name'>{c['name']}</td><td><b class='acc'>{a.get('median','-')}</b></td><td>{a.get('mean','-')}</td><td>{a.get('q1','-')}</td><td>{a.get('q3','-')}</td><td>{a.get('min','-')}</td><td>{a.get('max','-')}</td><td>{a.get('n','-')}</td></tr>"
summary += """</tbody></table></div>
<h2>캠프별 비교 차트</h2>
<div class="grid two">
  <div class="card"><h3>지원시작 vs 완료 (명)</h3><canvas id="sum_funnel"></canvas></div>
  <div class="card"><h3>완료전환율 · 내배카 보유율 (%)</h3><canvas id="sum_rate"></canvas></div>
</div>
<h2>지원중 유저 만나이 분포 — 캠프 비교 (박스플롯)</h2>
<div class="card"><h3>박스 = Q1~Q3 · 중앙선 = 중앙값 · 수염 = min~max</h3><canvas id="sum_box" style="max-height:300px"></canvas>
<table style="margin-top:12px"><thead><tr><th>캠프</th><th>중앙값</th><th>평균</th><th>Q1</th><th>Q3</th><th>min</th><th>max</th><th>n</th></tr></thead><tbody>
__AGESTAT__
</tbody></table></div>
<h2>핵심 인사이트</h2>
"""
# 동적 인사이트
best = max(camps,key=lambda c:c['conv']); worst=min(camps,key=lambda c:c['conv'])
hi_nbc = max(camps,key=lambda c:c['nbc_rate'])
summary += f"""<div class="insight alert"><span class="h">🚨 미완료 적체가 최대 누수 — 전체 시작자의 {round(tot_ing/tot_start*100)}%가 지원중에서 멈춤</span>완료전환율 평균 {avg_conv}%. 트래픽은 유입되나 <b>지원서 완료</b> 단계 대규모 이탈. 완료유도 넛지 ROI 최상위 구간.</div>
<div class="insight warn"><span class="h">⚠️ 내배카(국비) 의존도 캠프별 격차 — 최고 {hi_nbc['name']} {hi_nbc['nbc_rate']}%</span>국비 지원 메시지 민감도가 캠프마다 다름 → 소구 메시지 분리 검토.</div>
<div class="insight"><span class="h">💡 전환율 격차 — {best['name']} {best['conv']}% vs {worst['name']} {worst['conv']}%</span>탭에서 캠프별 연령·성별·신분 교차분석으로 차이 원인 추적.</div>
</div>"""

# 캠프별 점검 코멘트 (비판적 사고 — 데이터 신호 기반 2~3개 선별)
def build_comments(c):
    out = []
    시작,완료,지원중 = c['시작'],c['완료'],c['지원중']
    target,avs = c['target'],c['ach_vs_target']
    # ① 목표 run-rate (절대 달성율 함정 경고)
    comp_sorted = sorted(c['comp_daily'].items())
    last7 = comp_sorted[-7:]
    avg_comp = round(sum(v for _,v in last7)/len(last7),1) if last7 else 0
    rem = (target-완료) if target else None
    pj = c.get('proj')
    dleft = pj['days_left'] if pj else None
    if rem is not None and rem>0:
        if avg_comp>0:
            eta = round(rem/avg_comp)
            verdict = ""
            if dleft is not None:
                verdict = (f" 마감 D-{dleft} 대비 <b>여유</b>." if eta <= dleft*0.7
                           else (f" 마감 D-{dleft}로 <b>빠듯</b> — 가속 필요." if eta <= dleft
                                 else f" 마감 D-{dleft} 내 <b>달성 불가 페이스</b> — 강한 가속/연장 검토."))
            out.append(f"<b>목표 달성율 {avs}%를 절대값으로 판단하지 말 것</b> — 최근 7일 일평균 완료 {avg_comp}명 기준 잔여 {rem}명은 약 <b>{eta}일</b> 소요.{verdict}")
        else:
            dtxt = f" 마감 D-{dleft}." if dleft is not None else ""
            out.append(f"<b>최근 7일 완료 유입이 거의 정체</b>(일평균 {avg_comp}명) — 목표까지 {rem}명 남았으나 완료 모멘텀이 멈춤.{dtxt} 마감 리마인드·완료유도 트리거 시급.")
    elif rem is not None:
        out.append(f"목표 {target}명 도달(달성율 {avs}%) — 점검 지표를 완료 '수'에서 <b>질</b>(적합도·등록 전환·미수료 리스크)로 전환할 시점.")
    # ② 완료전환 병목 / 분모 신뢰성
    clog = round(지원중/시작*100) if 시작 else 0
    out.append(f"<b>완료전환 {c['conv']}% vs 미완료 {clog}%</b> — '지원시작' 분모에 유령·중복·단순열람이 섞였는지, 아니면 지원서 문항·자격요건이 이탈 병목인지 분해해야 실제 전환율이 드러남.")
    # ③ 가장 강한 신호 1개 추가 선별
    starts = sorted(c['daily'].items())
    oavg = sum(v for _,v in starts)/len(starts) if starts else 0
    l3 = starts[-3:]; l3avg = sum(v for _,v in l3)/len(l3) if l3 else 0
    univ = next((r for r in c['by_status'] if r['key']=='대학(원)생'), None)
    gp=c['gender_pool']; gtot=gp.get('남성',0)+gp.get('여성',0)
    mshare = round(gp.get('남성',0)/gtot*100) if gtot else 50
    cand=[]
    if oavg>0 and l3avg < 0.6*oavg:
        cand.append((9, f"<b>최근 3일 신규 지원 급감</b>(일평균 {oavg:.0f}→{l3avg:.0f}명) — 매체 예산 소진·타깃 피로 가능성. 채널별 잔여 예산·CPA를 우선 점검."))
    if univ and univ['yes_rate']<40:
        cand.append((7, f"<b>대학(원)생 내배카 보유율 {univ['yes_rate']}%</b>(n={univ['tot']}) — 비용 민감 세그먼트. 이 그룹이 완료전환에서 더 이탈하는지 교차 점검하고 자비·국비 메시지 분기 검토."))
    if mshare>=60 or mshare<=40:
        skew = '남성' if mshare>=60 else '여성'; sv = mshare if mshare>=60 else 100-mshare
        cand.append((5, f"<b>{skew} {sv}% 편중</b> — 유입 채널·크리에이티브가 특정 성별에 쏠렸는지, 의도된 타깃 설계인지 점검."))
    if c['age'].get('max',0)>=60:
        cand.append((3, f"만나이 최대 {c['age'].get('max')}세 등 <b>이상치</b> 존재 — 생년월일 오입력 가능성. 분포 해석 전 데이터 품질·정제 룰 점검."))
    cand.sort(key=lambda x:x[0], reverse=True)
    if cand: out.append(cand[0][1])
    return out[:3]

# 캠프별 패널
panels = summary
for i,c in enumerate(camps):
    pid=f"p{i+1}"
    t=c['target']; avs=c['ach_vs_target']; avstart=c['ach_vs_start']
    rem = (t-c['완료']) if t else None
    if avs is None:
        emoji,stxt,scls = 'ℹ️','목표 미설정',''
    elif avs>=100:
        emoji,stxt,scls = '🎉','목표 달성·초과','up'
    elif avs>=80:
        emoji,stxt,scls = '🟢','목표 임박 (80%+)','up'
    elif avs>=50:
        emoji,stxt,scls = '🟡','목표 절반 이상',''
    else:
        emoji,stxt,scls = '🔴','목표 미달 — 가속 필요','down'
    remtxt = (f"목표까지 <b>{rem}명</b> 남음" if (rem and rem>0) else "목표 달성") if t else ""
    insight_cls = 'alert' if (avs is not None and avs<50) else ('warn' if (avs is not None and avs<80) else '')
    cap = c.get('capacity'); comp_ratio = c.get('competition')
    cap_disp = f"{cap}명" if cap else '미설정'
    cap_ctx = f" · 수강정원 {cap}명 · 경쟁률 {comp_ratio}:1(지원/정원)" if cap else ""
    if t is not None:
        t_disp, avs_disp = str(t), f"{avs}%"
        body = f"목표 모객 <b>{t}명</b> 중 <b>{c['완료']}명</b> 달성 · 목표 달성율 <b>{avs}%</b> · {remtxt}. 지원완료 달성율(시작 대비) {avstart}%{cap_ctx}."
    else:
        t_disp, avs_disp = '미설정', '—'
        body = f"<b>목표 미설정</b> 캠프 — 지원완료 <b>{c['완료']}명</b> · 지원완료 달성율(시작 대비) {avstart}%{cap_ctx}. 목표치 설정 시 달성율·페이스 분석이 추가됩니다."
    # 모집 마감 전망 박스
    pj = c.get('proj')
    if pj:
        pcls = {'risk':'alert','tight':'warn'}.get(pj['tier'], '')
        icon = {'done':'🎉','safe':'✅','tight':'⚠️','risk':'🚨','na':'📅'}.get(pj['tier'], '📅')
        if pj['tier'] == 'done':
            diag = f"이미 목표 모객(<b>{t}명</b>) 초과 달성 — 마감까지 D-{pj['days_left']}. 잔여 기간은 선발·등록 전환·정원({cap or '-'}명) 적합도에 집중."
        elif t:
            diag = f"최근 완료 페이스 <b>{pj['pace']}명/일</b> → 마감({pj['end']}) 예상 누적 <b>{pj['projected']}명</b> (목표 {t} 대비 <b>{pj['proj_tpct']}%</b>) → <b>{pj['label']}</b>."
        else:
            diag = f"최근 완료 페이스 {pj['pace']}명/일. 목표 미설정으로 도달 전망은 생략."
        early_note = " <i style='color:var(--sub)'>(모집 7일 미만 — 추정 신뢰도 낮음)</i>" if pj['early'] else ""
        proj_html = (f'<div class="insight {pcls}" style="margin-top:12px"><span class="h">{icon} 모집 마감 전망 — '
                     f"{pj['start']} ~ {pj['end']} · 마감 D-{pj['days_left']} (기간 {pj['days_total']}일 중 {pj['days_elapsed']}일 · {pj['time_pct']}% 경과)</span>\n{diag}{early_note}</div>")
    else:
        proj_html = ""
    panels += f"""<div class="panel" id="{pid}">
<h2>현황 점검 (인사이트)</h2>
<div class="insight {insight_cls}"><span class="h">{emoji} {c['name']} — {stxt}</span>
{body}</div>
<div class="grid kpi-grid">
  <div class="card kpi"><div class="label">목표 모객수</div><div class="val">{t_disp}</div><div class="sub">목표 지원완료</div></div>
  <div class="card kpi"><div class="label">수강정원</div><div class="val">{cap_disp}</div><div class="sub">최종 정원</div></div>
  <div class="card kpi"><div class="label">지원완료수</div><div class="val acc">{c['완료']}</div><div class="sub">현재 모객</div></div>
  <div class="card kpi"><div class="label">목표 달성율</div><div class="val {scls}">{avs_disp}</div><div class="sub">= 완료/목표</div></div>
  <div class="card kpi"><div class="label">경쟁률</div><div class="val">{(str(comp_ratio)+':1') if comp_ratio else '—'}</div><div class="sub">지원시작/정원</div></div>
</div>
{proj_html}
<div class="card comment-card" style="margin-top:14px"><h3>🧐 점검 코멘트 (비판적 점검 포인트)</h3>
<ul class="comments">
{''.join(f'<li>{x}</li>' for x in build_comments(c))}
</ul></div>
<h2>{c['name']} — 퍼널 요약</h2>
<div class="grid kpi-grid">
  <div class="card kpi"><div class="label">지원시작</div><div class="val">{c['시작']}</div><div class="sub">원본 {c['total_rows']}행</div></div>
  <div class="card kpi"><div class="label">지원중</div><div class="val down">{c['지원중']}</div><div class="sub">미완료</div></div>
  <div class="card kpi"><div class="label">지원완료</div><div class="val acc">{c['완료']}</div><div class="sub">전환 {c['conv']}%</div></div>
  <div class="card kpi"><div class="label">유효취소</div><div class="val">{c['유효취소']}</div><div class="sub">{c['cancel_rate']}%</div></div>
  <div class="card kpi"><div class="label">내배카 보유율</div><div class="val">{c['nbc_rate']}%</div><div class="sub">유효 {c['nbc_tot']}명</div></div>
</div>
<h2>일별 추이</h2>
<div class="card"><h3>일별 신규 지원시작 (명)</h3><canvas id="{pid}_daily" style="max-height:240px"></canvas></div>
<div class="card" style="margin-top:14px"><h3>누적 지원시작 vs 완료 (일자별 수치) + <span style="color:var(--green)">예상 완료 시뮬레이션(점선)</span> — 마감일까지 최근 페이스 외삽</h3><canvas id="{pid}_cum" style="max-height:340px"></canvas></div>
<h2>지원자 프로필</h2>
<div class="card"><h3>연령대 분포 (지원중, 만나이) — 중앙값 {c['age'].get('median','-')}세 · 평균 {c['age'].get('mean','-')} · Q1~Q3 {c['age'].get('q1','-')}~{c['age'].get('q3','-')} · 범위 {c['age'].get('min','-')}~{c['age'].get('max','-')}</h3>
"""
    # 연령대 미니바
    mx = max(c['age_band'].values()) or 1
    for b in BANDS:
        v=c['age_band'][b]; w=round(v/mx*100)
        panels += f"<div class='barmini'><span class='t'>{b}세</span><span class='bar'><span style='width:{w}%;background:var(--blue)'></span></span><span class='v'>{v}명</span></div>"
    panels += "</div>\n"
    panels += f"""<div class="card" style="margin-top:14px"><h3>일일 지원중 유저 만나이 분포 (박스플롯) — 일자별 <span style="color:var(--red)">Q3</span>·<span style="color:var(--accent)">중앙</span>·<span style="color:var(--blue)">Q1</span> 표기 · 전체 중앙값 {c['age'].get('median','-')}세 점선</h3><canvas id="{pid}_box" style="max-height:360px"></canvas></div>\n"""

    # 연령대 × 합불상태 피벗 (차트 + cast 테이블)
    panels += f"""<div class="card" style="margin-top:14px"><h3>연령대별 현재 합불상태 현황 (연령대 × 합불상태 · cast)</h3><canvas id="{pid}_agestatus" style="max-height:320px"></canvas>"""
    sp = c['status_present']
    th = "".join(f"<th>{s}</th>" for s in sp)
    rows_html = ""
    for r in c['age_status']:
        tds = "".join(f"<td>{r['counts'].get(s,0)}</td>" for s in sp)
        rows_html += f"<tr><td class='name'>{r['band']}세</td>{tds}<td><b class='acc'>{r['total']}</b></td></tr>"
    panels += f"""<table style="margin-top:12px"><thead><tr><th>연령대</th>{th}<th>합계</th></tr></thead><tbody>{rows_html}</tbody></table></div>\n"""

    panels += f"""<h2>내일배움카드 교차분석 (melt · cast)</h2>
<div class="grid two">
  <div class="card"><h3>① 연령대별 내배카 YES/NO + YES비율</h3><canvas id="{pid}_age"></canvas></div>
  <div class="card"><h3>② 성별 내배카 YES/NO + YES비율</h3><canvas id="{pid}_gender"></canvas></div>
</div>
<div class="card" style="margin-top:14px"><h3>③ 상태1(신분)별 내배카 보유율 — 공란은 '알 수 없음'</h3><canvas id="{pid}_status" style="max-height:260px"></canvas></div>
"""
    # cast 테이블 3종
    def tbl(title,rows):
        h=f"<div class='card'><h3>{title}</h3><table><thead><tr><th>구분</th><th>YES</th><th>NO</th><th>합계</th><th>YES 비율</th></tr></thead><tbody>"
        for r in rows:
            h+=f"<tr><td class='name'>{r['key']}</td><td>{r['yes']}</td><td>{r['no']}</td><td>{r['tot']}</td><td><b class='acc'>{r['yes_rate']}%</b></td></tr>"
        h+="</tbody></table></div>"
        return h
    panels += "<div class='grid two' style='margin-top:14px'>"
    panels += tbl("연령대 × 내배카 (cast)", c['by_age'])
    panels += tbl("성별 × 내배카 (cast)", c['by_gender'])
    panels += "</div>"
    panels += "<div style='margin-top:14px'>"+tbl("상태1(신분) × 내배카 (cast)", c['by_status'])+"</div>"
    panels += "</div>\n"

# INIT 스크립트
init = """
// summary charts
new Chart(document.getElementById('sum_funnel'),{type:'bar',data:{labels:DATA.camps.map(c=>c.name),datasets:[
  {label:'지원시작',data:DATA.camps.map(c=>c['시작']),backgroundColor:C.acc,datalabels:{display:true,anchor:'end',align:'end',color:C.txt,font:{weight:'bold',size:12},formatter:v=>v}},
  {label:'지원완료',data:DATA.camps.map(c=>c['완료']),backgroundColor:C.blue,datalabels:{display:true,anchor:'end',align:'end',color:C.txt,font:{weight:'bold',size:12},formatter:v=>v}}]},options:baseOpt()});
new Chart(document.getElementById('sum_rate'),{type:'bar',data:{labels:DATA.camps.map(c=>c.name),datasets:[
  {label:'완료전환율',data:DATA.camps.map(c=>c.conv),backgroundColor:C.green,datalabels:{display:true,anchor:'end',align:'end',color:C.txt,font:{weight:'bold',size:12},formatter:v=>v+'%'}},
  {label:'내배카 보유율',data:DATA.camps.map(c=>c.nbc_rate),backgroundColor:C.purple,datalabels:{display:true,anchor:'end',align:'end',color:C.txt,font:{weight:'bold',size:12},formatter:v=>v+'%'}}]},options:baseOpt()});
mkBoxCompare('sum_box');
// per-camp
DATA.camps.forEach((c,i)=>{const p='p'+(i+1);
  mkDailyBar(p+'_daily',c.daily);
  mkLine(p+'_cum',c.daily,c.comp_daily,c.proj);
  mkBoxDaily(p+'_box',c.age_by_day,c.age.median,c.box_daily);
  mkAgeStatus(p+'_agestatus',c.age_status,c.status_present);
  mkNbcCross(p+'_age',c.by_age);
  mkNbcCross(p+'_gender',c.by_gender);
  mkStatusBar(p+'_status',c.by_status);
});
// 초기 로드 시 URL 해시에 해당하는 탭 활성화 (공유 링크 지원)
selFromHash();
"""

HTML = (HTML.replace("__YYMMDD__",yymmdd).replace("__DATE__",datetime.now().strftime('%Y-%m-%d'))
        .replace("__NCAMP__",str(len(camps))).replace("__GEN__",DATA['generated'])
        .replace("__PANELS__",panels).replace("__AGESTAT__",agestat)
        .replace("__DATAJSON__",json.dumps(DATA,ensure_ascii=False))
        .replace("__INIT__",init))

# (HTML은 메모리에 보관 — MD 생성 후 OUT_DIRS 전체에 함께 기록)

# ---------- Obsidian용 Markdown 동반 노트 생성 ----------
html_name = f"{yymmdd}_daily-report.html"
date_str = datetime.now().strftime('%Y-%m-%d')

# 목표 미설정 캠프 표시용 헬퍼
def tgt_str(c): return str(c['target']) if c.get('target') is not None else '미설정'
def atv_str(c): return f"{c['ach_vs_target']}%" if c.get('ach_vs_target') is not None else '—'
def cap_str(c): return str(c['capacity']) if c.get('capacity') is not None else '미설정'
def comp_str(c): return f"{c['competition']}:1" if c.get('competition') is not None else '—'

# 캠프 요약 표
funnel_rows = "\n".join(
    f"| {c['name']} | {tgt_str(c)} | {cap_str(c)} | {c['시작']} | {c['지원중']} | {c['완료']} | {c['ach_vs_start']}% | {atv_str(c)} | {comp_str(c)} | {c['nbc_rate']}% |"
    for c in camps)
# 연령×내배카, 상태1×내배카 핵심 표 (캠프별)
def md_cast(c):
    s = f"**{c['name']}** — 연령대별 내배카 보유율\n\n| 연령대 | YES | NO | 합계 | YES 비율 |\n|---|---|---|---|---|\n"
    s += "\n".join(f"| {r['key']} | {r['yes']} | {r['no']} | {r['tot']} | {r['yes_rate']}% |" for r in c['by_age'])
    s += "\n\n신분(상태1)별 내배카 보유율\n\n| 신분 | YES | NO | 합계 | YES 비율 |\n|---|---|---|---|---|\n"
    s += "\n".join(f"| {r['key']} | {r['yes']} | {r['no']} | {r['tot']} | {r['yes_rate']}% |" for r in c['by_status'])
    return s
cast_blocks = "\n\n".join(md_cast(c) for c in camps)

# 연령대 × 합불상태 피벗 (캠프별)
def md_agestatus(c):
    sp = c['status_present']
    head = "| 연령대 | " + " | ".join(sp) + " | 합계 |\n|" + "---|"*(len(sp)+2) + "\n"
    body = "\n".join("| " + r['band'] + " | " + " | ".join(str(r['counts'].get(s,0)) for s in sp) + f" | {r['total']} |" for r in c['age_status'])
    return f"**{c['name']}** — 연령대별 합불상태 현황\n\n{head}{body}"
agestatus_blocks = "\n\n".join(md_agestatus(c) for c in camps)

def strip_tags(s):
    import re as _re
    return _re.sub(r'<[^>]+>','',s)
comments_md = "\n\n".join(
    f"**{c['name']}** (목표 {tgt_str(c)} · 달성율 {atv_str(c)})\n\n" +
    "\n".join(f"{j+1}. {strip_tags(x)}" for j,x in enumerate(build_comments(c)))
    for c in camps)

# 전일 대비 경향성 (MD)
if has_trend:
    def _dm(v, s=''):
        return (f"▲{v}{s}" if v>0 else (f"▼{abs(v)}{s}" if v<0 else f"±0{s}"))
    trow_md = "\n".join(
        (lambda c,tr: f"| {c['name']} | {_dm(tr['d']['start'])} | {_dm(tr['d']['comp'])} | {_dm(tr['d']['conv'],'pp')} | {_dm(tr['d']['nbc'],'pp')} | {_dm(tr['d']['tgt'],'pp')} | 합{tr['review']['pass']:+d} 불{tr['review']['fail']:+d} 예{tr['review']['pre']:+d} |")(c, trends[c['name']])
        for c in camps if trends.get(c['name']))
    tins_md = "\n\n".join(
        f"**{c['name']}**\n\n" + "\n".join(f"{j+1}. {strip_tags(x)}" for j,x in enumerate(trends[c['name']]['ins']))
        for c in camps if trends.get(c['name']))
    trend_md = (f"## 📊 전일 대비 경향성 · 직전 {prev_yymmdd} 대비 (비판적 분석)\n\n"
                f"| 캠프 | 지원시작 | 지원완료 | 완료전환율 | 내배카 | 목표달성율 | 심사진행(합/불/예비) |\n"
                f"|---|---|---|---|---|---|---|\n{trow_md}\n\n*Δ = 오늘 − 직전 리포트 · 1일 변동이라 노이즈 가능성 유의*\n\n{tins_md}\n")
else:
    trend_md = "## 📊 전일 대비 경향성\n\n직전 리포트가 없어 비교를 생략합니다.\n"

# 모집 마감 전망 (MD)
_pmrows, _pmdiag = [], []
for c in camps:
    pj = c.get('proj')
    if not pj:
        _pmrows.append(f"| {c['name']} | 미설정 | — | — | — | — | — | — |")
        continue
    proj_disp = f"{pj['projected']} ({pj['proj_tpct']}%)" if pj.get('proj_tpct') is not None else f"{pj['projected']}"
    early = " ⚠️초기" if pj['early'] else ""
    _pmrows.append(f"| {c['name']} | {pj['start']}~{pj['end']} | D-{pj['days_left']} | {pj['time_pct']}% | {c['완료']}/{c['target'] if c.get('target') else '—'} | {pj['pace']} | {proj_disp}{early} | {pj['label']} |")
    if pj['tier'] == 'done':
        _pmdiag.append(f"- **{c['name']}**: 목표 모객({c['target']}명) 초과 달성 · 마감 D-{pj['days_left']} — 선발·등록 전환·정원 적합도로 전환.")
    elif c.get('target'):
        cav = " (모집 7일 미만, 신뢰도 낮음)" if pj['early'] else ""
        _pmdiag.append(f"- **{c['name']}**: 최근 {pj['pace']}명/일 → 마감 예상 {pj['projected']}명(목표 {c['target']} 대비 {pj['proj_tpct']}%) → **{pj['label']}**{cav}.")
proj_md = ("## 📅 모집 마감 전망 (트렌드 × 종결일)\n\n"
           "| 캠프 | 모집기간 | 마감 | 경과 | 완료/목표 | 페이스(명/일) | 예상도달(목표대비) | 전망 |\n"
           "|---|---|---|---|---|---|---|---|\n" + "\n".join(_pmrows) + "\n\n" + "\n".join(_pmdiag) + "\n")

with open(__file__, 'r', encoding='utf-8') as fp:
    py_src = fp.read()

# 인터랙티브(HTML) 안내 블록 — MD_ONLY일 땐 HTML이 없으므로 생략
if MD_ONLY:
    interactive_block = "> [!note] 이 노트는 MD 단독 출력본입니다. 인터랙티브 HTML 대시보드는 생성하지 않았습니다 (필요 시 `python generate_daily_report.py`로 재생성)."
else:
    interactive_block = (f"## 🔗 리포트 열기 (인터랙티브)\n\n"
                         f"[▶ {html_name} 브라우저로 열기]({html_name})\n\n"
                         f'<iframe src="{html_name}" width="100%" height="900" style="border:1px solid #2a2f3a;border-radius:10px;"></iframe>\n\n'
                         f"> [!tip] iframe이 비어 보이면 옵시디언 설정 또는 보안정책 때문일 수 있습니다. 위 링크로 직접 열면 항상 동작합니다.")

md = f"""---
title: KDT 모객현황 데일리 리포트 {yymmdd}
date: {date_str}
type: daily-report
tags: [kdt, 모객, daily-report]
source: kdt 모객현황 데이터 추출.ipynb
status: TEST
---

# 📊 KDT 모객현황 데일리 리포트 · {date_str}

> [!info] 대상 캠프 {len(camps)}종 · 내부직원·테스트 제외 · **TEST 출력본**

{interactive_block}

## 📈 핵심 요약

| 캠프 | 목표모객 | 수강정원 | 지원시작 | 지원중 | 지원완료 | 완료달성율<br>(완료/시작) | 목표달성율<br>(완료/목표) | 경쟁률<br>(지원/정원) | 내배카 보유율 |
|---|---|---|---|---|---|---|---|---|---|
{funnel_rows}

- **총 지원시작** {tot_start} · **완료** {tot_comp} (평균 전환 {avg_conv}%) · **미완료 적체** {tot_ing} ({round(tot_ing/tot_start*100)}%)
- **내배카 보유율** {nbc_rate_all}% (유효응답 {tot_nbc_t}명)

{proj_md}
{trend_md}
## 🧐 부트캠프별 점검 코멘트 (비판적 점검 포인트)

{comments_md}

## 🧮 내일배움카드 교차분석 (melt · cast)

{cast_blocks}

## 🧭 연령대별 합불상태 현황 (연령대 × 합불상태 · cast)

{agestatus_blocks}

## 🧩 만나이 분포 (지원중 유저)

| 캠프 | 중앙값 | 평균 | Q1 | Q3 | min | max | n |
|---|---|---|---|---|---|---|---|
""" + "\n".join(
    f"| {c['name']} | {c['age'].get('median','-')} | {c['age'].get('mean','-')} | {c['age'].get('q1','-')} | {c['age'].get('q3','-')} | {c['age'].get('min','-')} | {c['age'].get('max','-')} | {c['age'].get('n','-')} |"
    for c in camps) + f"""

> 일별 박스플롯(노트북 셀2 로직)은 HTML 캠프별 탭 참조.

## 🛠 생성 스크립트 (generate_daily_report.py)

> 아래 코드를 `daily report/generate_daily_report.py`로 두고 `python generate_daily_report.py` 실행 시
> 실행 시점 날짜로 HTML + 본 MD가 함께 재생성됩니다.

```python
{py_src}
```

---
*생성 {DATA['generated']} · 내배카 비율은 yes/no 유효응답(지원완료·지원중) 기준 · 상태1 공란은 '알 수 없음' 처리*
"""

# ---------- 출력: OUT_DIRS 각 폴더에 (MD_ONLY면 MD만) ----------
for d in OUT_DIRS:
    mp = os.path.join(d, f"{yymmdd}_daily-report.md")
    if not MD_ONLY:
        hp = os.path.join(d, f"{yymmdd}_daily-report.html")
        with open(hp, 'w', encoding='utf-8') as fp:
            fp.write(HTML)
        print("WROTE", hp)
    with open(mp, 'w', encoding='utf-8') as fp:
        fp.write(md)
    print("WROTE", mp)

```

---
*생성 2026-06-19 11:26 · 내배카 비율은 yes/no 유효응답(지원완료·지원중) 기준 · 상태1 공란은 '알 수 없음' 처리*
