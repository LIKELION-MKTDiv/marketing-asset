# resume-pipeline — 멋사 미래이력서 생성 파이프라인

## 개요

KDT 부트캠프 지원자의 자기소개서 + 부트캠프 정보를 조합하여 "미래이력서(MD + HTML)"를 생성하는 파이프라인.

---

## 생성 대상 필터 기준

> **반드시 아래 두 조건을 모두 충족하는 지원자만 생성 대상으로 포함한다.**

| 조건 | 컬럼명 | 값 |
|------|--------|-----|
| 지원 완료 | `지원상태` | `지원완료` |
| 검토 대기 | `합불상태` | `검토전` |

- 입력 CSV: `data/sample/kdt-{부트캠프코드}-{기수}_지원서_{타임스탬프}.csv`
- `지원상태`가 `지원완료`가 아닌 행(지원중, 지원취소 등)은 제외
- `합불상태`가 `검토전`이 아닌 행(대상아님, 합격, 불합격 등)은 제외
- 자소서 컬럼에 유효한 텍스트(10자 초과)가 없는 행은 제외

## 중복 생성 방지

> **이미 이력서가 생성된 지원자는 재생성하지 않는다.**

### 판별 기준

- `outputs/` 하위 전체 날짜 디렉토리를 스캔하여 아래 파일 존재 여부로 판별:
  - `{이름}_미래이력서.md` 또는 `{이름}_미래이력서.html`
- intermediate 파일(`{이름}_3_content.json`)이 존재하면 Phase 3까지 완료된 것으로 간주
- 이미 생성된 이름 목록은 파이프라인 시작 시 로그에 출력하고 스킵 처리

### 재생성이 필요한 경우

- 수동으로 해당 지원자의 output 파일을 삭제한 뒤 다시 실행
- 또는 `--force` 플래그 사용 시 중복 체크 무시 (미구현 시 파일 삭제 방식 사용)

---

## 실행

### 미래이력서 생성 (통합 파이프라인)

```bash
cd resume-pipeline
pip install -r requirements.txt
cp .env.example .env              # ANTHROPIC_API_KEY 설정
python main.py --bootcamp "data/sample/kdt-cld-7th 부트캠프 커리큘럼 정보.md" "data/sample/kdt-cld-7th 부트캠프 프로젝트 정보.md" --applications "data/sample/kdt-cld-7th_지원서_2026_05_11_17_50_42.csv"
```

### 미래이력서 단독 재생성 (intermediate 데이터 활용)

```bash
python generate_future_resume.py                    # 미생성 대상 자동 탐색
python generate_future_resume.py --names 홍길동      # 특정 이름 지정
```

- Phase 1~3 intermediate 산출물이 선행되어야 함 (main.py 실행 시 자동 생성)

> WeasyPrint Windows 설치: GTK 런타임 필요 — https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows

## 파이프라인 구조 (main.py)

```
Phase 1: Extractor (Sonnet)     — CSV/Excel → 구조화 데이터 추출
Phase 2: Profiler (Sonnet)      — 지원자 유형 분류 + 역량 매핑
Phase 3: Resume Writer (Opus)   — 이력서 콘텐츠 생성 (extended thinking)
Phase 4: Future Resume Renderer — 미래이력서 MD + HTML 렌더링 (순수 함수)
```

- Phase 4는 `generate_future_resume.py`의 `render_md()` / `render_html()` 호출
- HTML 내 테이블 셀의 `**text**` → `<strong>text</strong>` 변환은 `md_to_html()` 내부에서 자동 처리

## 입력 데이터

- `--bootcamp`: 부트캠프 정보 파일 (CSV/Excel/TXT/MD 지원, 복수 파일 가능)
- `--applications`: 지원서 CSV/Excel 파일 (1행=1지원자, 자소서 Q&A 컬럼 포함)
- CSV 파일명 패턴: `kdt-{부트캠프코드}-{기수}_지원서_{타임스탬프}.csv`
- 개인정보 컬럼(이름/이메일/전화)은 자동 감지

## 출력

```
outputs/YYYY-MM-DD/
├── {이름}_미래이력서.md
├── {이름}_미래이력서.html
├── 미래이력서_활용가이드.txt
├── intermediate/
│   ├── {이름}_1_extracted.json
│   ├── {이름}_2_profile.json
│   └── {이름}_3_content.json
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
