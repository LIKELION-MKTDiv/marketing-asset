# KDT 모객현황 데일리 리포트

KDT 부트캠프 지원서 CSV에서 모객 현황 인사이트를 추출해 인터랙티브 HTML + Obsidian용 MD 리포트를 생성하는 파이프라인.

> 소스 로직: `kdt 모객현황 데이터 추출.ipynb` 기반 (내부직원·테스트 지원 제외 처리 포함)

## 구성

| 파일 | 설명 |
|---|---|
| `generate_daily_report.py` | **표준 생성기** — CSV 읽어 HTML/MD 리포트 생성 (이중 출력) |
| `run_and_push.ps1` | **원클릭** — 리포트 생성 + git add/commit/push 자동 |
| `reports/` | 생성된 날짜별 리포트 (`{yymmdd}_daily-report.html` / `.md`) — GitHub에서 열람 |

## 실행

```powershell
# ① 생성만 (로컬)
python generate_daily_report.py

# ② 생성 + GitHub 푸시 (원클릭)
./run_and_push.ps1
```

생성기는 리포트를 **두 곳에 동시 출력**합니다:
1. `kdt-daily-report/reports/` — 레포(GitHub) 열람용
2. `C:\Users\manid\Documents\whisky\...\daily report\` — Obsidian 보기용 (폴더 있을 때만)

## 데이터 소스 / 보안

- CSV 위치 기본값: `C:\Users\manid\OneDrive\바탕 화면\data_study\kdt`
- 환경변수 `KDT_DATA_DIR`로 override 가능
- **원본 CSV·개인정보는 GitHub에 올라가지 않습니다.** 리포트에는 집계 수치(카운트·연령 분포)만 포함되며 이름·이메일 등 PII는 없음. 레포 `.gitignore`가 `*.csv`/`data/`/`outputs/`를 차단.

## 설정

부트캠프 추가/목표 변경은 `generate_daily_report.py` 상단에서:

```python
DISPLAY = { "kdt-aiplus": "AI+ NLP 5기", ... }   # 파일 prefix → 표시명
TARGETS = { "AI+ NLP 5기": 120, ... }            # 목표 지원완료수
```

CSV 폴더에 파일을 추가하면 탭이 자동으로 늘어납니다.

## 리포트 내용

- **Summary 탭**: 캠프별 퍼널 비교, 만나이 분포 박스플롯(캠프 비교), 핵심 인사이트
- **부트캠프별 탭**: 목표 대비 현황 점검 + 비판적 점검 코멘트, 일별 추이, 연령/성별 분포, 일일 만나이 박스플롯, 내배카 교차분석(연령·성별·신분 × 내배카 melt·cast)
