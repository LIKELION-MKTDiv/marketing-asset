# IT 취업 콘텐츠 발행 프로젝트

## 프로젝트 목적
IT 개발자/비개발자 취업을 원하는 사람들이 관심 가질 만한 트렌드 소식과 정보를 조사하여
빠르게 SEO 최적화 콘텐츠를 작성·발행한다.

## 에이전트 구성

| 에이전트 | 파일 | 역할 |
|---------|------|------|
| 1. 트렌드 조사 | `agents/researcher_prompt.md` | IT 취업 관련 최신 트렌드 5~7개 조사 |
| 2. 선별 감독관 | `agents/research_supervisor_prompt.md` | 조사 결과에서 콘텐츠화할 2~3개 주제 선별 |
| 3. 콘텐츠 에디터 | `agents/editor_prompt.md` | 1위 주제로 SEO 최적화 블로그 포스팅 작성 |
| 4. 검수 감독관 | `agents/content_supervisor_prompt.md` | 작성 콘텐츠 SEO/품질 검수 (100점 채점) |

## 실행 방법

```bash
# 1. 의존성 설치 (최초 1회)
cd pipeline
pip install -r requirements.txt

# 2. API 키 설정
set ANTHROPIC_API_KEY=your_api_key_here   # Windows
# export ANTHROPIC_API_KEY=your_api_key_here  # Mac/Linux

# 3. 파이프라인 실행
python run_pipeline.py
```

## 산출물 구조

```
outputs/
└── YYYY-MM-DD/
    ├── 1_research_report.md    ← 트렌드 조사 리포트
    ├── 2_selected_trends.md    ← 선별된 주제 (우선순위 포함)
    ├── 3_draft_content.md      ← SEO 최적화 블로그 초안
    ├── 4_reviewed_content.md   ← 검수 리포트 + 초안 (최종 검토용)
    └── pipeline_log.txt        ← 실행 로그
```

## SEO 가이드
`SEOREADME.md` — 네이버블로그/브런치/인블로그 SEO 구조 규약

## 최종 검토 절차 (담당자 직접 수행)
1. `outputs/YYYY-MM-DD/4_reviewed_content.md` 열기
2. 검수 리포트 확인 (점수, 필수 수정 사항)
3. 초안 콘텐츠 직접 수정
4. 플랫폼에 발행
