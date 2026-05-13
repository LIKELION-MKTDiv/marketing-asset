# resume-pipeline — 멋사 역량 이력서 PDF 생성 파이프라인

## 개요

KDT 부트캠프 지원자의 자기소개서 + 부트캠프 정보를 조합하여 "수료 후 역량 이력서(경력기술서)" PDF를 생성하는 5-Phase 파이프라인.

## 실행

```bash
cd resume-pipeline
pip install -r requirements.txt
cp .env.example .env              # ANTHROPIC_API_KEY 설정
python main.py --bootcamp data/sample/bootcamp.csv --applications data/sample/applicants.csv
```

> WeasyPrint Windows 설치: GTK 런타임 필요 — https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows

## 파이프라인 구조

```
Phase 1: Extractor (Sonnet)     — CSV/Excel → 구조화 데이터 추출
Phase 2: Profiler (Sonnet)      — 지원자 유형 분류 + 역량 매핑
Phase 3: Resume Writer (Opus)   — 이력서 콘텐츠 생성 (extended thinking)
Phase 4: Template Renderer      — Jinja2 HTML 렌더링 (순수 함수)
Phase 5: PDF Generator          — WeasyPrint HTML→PDF (순수 함수)
```

## 입력 데이터

- `--bootcamp`: 부트캠프 정보 CSV/Excel (단일 행 또는 key-value 2열)
- `--applications`: 지원서 CSV/Excel (1행=1지원자, 자소서 Q&A 컬럼 포함)
- 개인정보 컬럼(이름/이메일/전화)은 자동 감지

## 출력

```
outputs/YYYY-MM-DD/
├── {이름}_역량이력서.pdf
├── intermediate/
│   ├── {이름}_1_extracted.json
│   ├── {이름}_2_profile.json
│   ├── {이름}_3_content.json
│   └── {이름}_4_rendered.html
├── batch_summary.json
└── pipeline.log
```

## 지원자 유형별 템플릿

| 유형 | 템플릿 | 레이아웃 |
|---|---|---|
| career_changer (전직자) | career_changer.html | 2단 컬럼 + 전환 하이라이트 |
| student (대학생) | student.html | 단일 컬럼, 프로젝트 강조 |
| experienced (경력자) | experienced.html | 2단 컬럼, 기술스택 전면 배치 |

## 모델 전략

- `claude-sonnet-4-6`: Phase 1 (추출), Phase 2 (분류)
- `claude-opus-4-6` + extended thinking: Phase 3 (이력서 생성)

## 브랜딩

- 로고: `assets/likelion_logo.png`
- 컬러: #FF7816 (메인), #333333 (보조)
- 폰트: Pretendard (`templates/fonts/`)
