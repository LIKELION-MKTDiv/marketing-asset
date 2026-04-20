# KDT 경쟁사 분석 프로젝트

멋쟁이사자처럼 KDT 부트캠프 경쟁사 정기 모니터링 파이프라인.

## 빠른 실행

```bash
cd /c/Users/manid/competitor-analysis
python main.py
```

또는 Claude Code에서 `/경쟁사분석` 슬래시 커맨드 실행.

## 에이전트 구조

```
main.py
└── orchestrator.py (헤드 에이전트)
    ├── researcher.py   [Phase 1] Playwright 스크래핑 + LLM 구조화
    ├── analyzer.py     [Phase 2] 경쟁 매핑 + 변경사항 분류
    ├── insight_generator.py [Phase 3] 전략 인사이트 (claude-opus-4-6 + thinking)
    └── documenter.py   [Phase 4] Notion 페이지 + Slack 알림
```

## 모델

| 에이전트 | 모델 | 이유 |
|---------|------|------|
| researcher | claude-sonnet-4-6 | 구조화 추출, 비용 효율 |
| analyzer | claude-sonnet-4-6 | 분류/매핑, 중간 복잡도 |
| insight_generator | claude-opus-4-6 + thinking | 고차원 전략 추론 |
| documenter | claude-sonnet-4-6 | 요약 문서 작성 |

## 환경 변수 (.env)

| 변수 | 필수 | 설명 |
|------|------|------|
| ANTHROPIC_API_KEY | ✅ | Anthropic API 키 |
| NOTION_TOKEN | Notion 사용 시 | Integration 토큰 |
| NOTION_PARENT_PAGE_ID | Notion 사용 시 | 결과 저장 페이지 ID |
| SLACK_WEBHOOK_URL | Slack 사용 시 | Incoming Webhook URL |
| SLACK_BOT_TOKEN | Slack Bot 방식 시 | Bot OAuth 토큰 |
| SLACK_CHANNEL | Bot 방식 시 | 채널명 (예: #kdt-분석) |

## 초기 설정

```bash
pip install -r requirements.txt
playwright install chromium  # 브라우저 설치
cp .env.example .env         # API 키 입력
```

## 캐시 구조

`data/cache/{competitor_key}.json` — 경쟁사별 마지막 조사 결과 저장.
재실행 시 변경분만 분석하므로 처음보다 빠르게 실행됨.
