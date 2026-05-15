# KDT 경쟁사 분석 파이프라인

멋쟁이사자처럼(Likelion) KDT 부트캠프 시장의 주요 경쟁사를 정기 모니터링하고, 전략 인사이트와 MD 리포트를 자동 생성하는 4-Phase 멀티 에이전트 파이프라인입니다.

> Anthropic SDK 기반 비동기 멀티에이전트 + Playwright 스크래핑 + Notion/Slack 통보(선택)

---

## 한눈에 보기

| 항목 | 내용 |
|------|------|
| 대상 경쟁사 | 패스트캠퍼스 커널 · 스파르타 내일배움캠프 · 코드잇 스프린트 |
| 자사 기준 | 멋쟁이사자처럼 (https://bootcamp.likelion.net/) |
| 모델 전략 | Sonnet (수집/분석/문서화) + Opus (전략 인사이트, extended thinking) |
| 실행 방식 | `python main.py` 또는 Claude Code 슬래시 커맨드 `/경쟁사분석` |
| 결과물 | `outputs/{YYYY-MM-DD_HHMM}/report_{YYYY-MM-DD}.md` + 단계별 JSON 로그 |
| 캐시 | `data/cache/{competitor_key}.json` — 재실행 시 변경 델타만 분석 |

---

## 아키텍처

```
main.py
└── agents/orchestrator.py  (Head Agent)
    ├── [Phase 1] researcher.py        Playwright(depth0→depth1) + LLM 구조화 추출
    ├── [Phase 2] analyzer.py          경쟁 매핑 / 변경사항 분류 / 트랙 커버리지
    ├── [Phase 3] insight_generator.py 전략 인사이트 (Opus + extended thinking)
    └── [Phase 4] documenter.py        MD 리포트 빌드 + (옵션) Notion / Slack
```

### Phase별 책임

| Phase | 에이전트 | 모델 | 입력 → 출력 |
|-------|---------|------|-------------|
| 1. 조사 | `researcher` | `claude-sonnet-4-6` | URL 리스트 → 구조화된 부트캠프 목록 + 캐시 대비 diff |
| 2. 분석 | `analyzer` | `claude-sonnet-4-6` | 조사 결과 → 경쟁 매핑 / 트랙 커버리지 / 신규 트렌드 |
| 3. 인사이트 | `insight_generator` | `claude-opus-4-6` (+ thinking 4k) | 분석 데이터 → 경영진 요약 · 위협 · 기회 · 차별화 · Quick Wins |
| 4. 문서화 | `documenter` | `claude-sonnet-4-6` | 인사이트 → MD 리포트 + 300자 요약(Slack/Notion용) |

### 데이터 흐름

```
Playwright 스크래핑(메인+상세 N개)
        │
        ▼
LLM 구조화 추출 (과정명/트랙/기간/상태/특장점/키워드/취업지원/국비여부)
        │
        ▼
캐시 diff (added / removed / changed / unchanged)
        │
        ▼
경쟁 매핑 + 트랙 커버리지 + 신규 트렌드 식별
        │
        ▼
Opus 전략 인사이트 (위협 우선순위 · 기회 · 차별화 포지셔닝 · Quick Wins)
        │
        ▼
MD 리포트(섹션화) → 파일 저장 + (옵션) Notion 페이지 + Slack 알림
```

---

## 빠른 실행

### 1. 환경 준비

```bash
cd research
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # API 키 입력
```

### 2. 실행

```bash
python main.py
```

또는 Claude Code에서:

```
/경쟁사분석
```

### 3. 결과 확인

```
outputs/
└── 2026-05-15_1430/
    ├── research.json    # Phase 1 raw
    ├── analysis.json    # Phase 2 raw
    ├── insights.json    # Phase 3 raw
    ├── final.json       # 파이프라인 메타
    └── report_2026-05-15.md  # 최종 MD 리포트
```

---

## 디렉토리 구조

```
research/
├── main.py                 # 진입점 (orchestrator.run 호출)
├── config.py               # 경쟁사 URL, 모델, 경로, 환경 변수 로딩
├── requirements.txt
├── .env.example
├── .claude/
│   └── commands/
│       └── 경쟁사분석.md   # Claude Code 슬래시 커맨드
├── agents/
│   ├── orchestrator.py     # 4 Phase 순차 조율 + 단계별 JSON 로깅
│   ├── researcher.py       # 스크래핑 + 구조화 + diff
│   ├── analyzer.py         # 경쟁 매핑/분류
│   ├── insight_generator.py# Opus 전략 인사이트
│   └── documenter.py       # MD 리포트 빌드
├── utils/
│   ├── scraper.py          # Playwright depth0+depth1
│   ├── cache.py            # 경쟁사별 JSON 캐시 + diff
│   ├── notion_api.py       # Notion 페이지 생성/업데이트
│   └── slack_api.py        # Slack Webhook / Bot 전송
├── data/
│   └── cache/              # 경쟁사별 마지막 조사 결과
└── outputs/                # 실행 회차별 결과
```

---

## 환경 변수 (.env)

| 변수 | 필수 | 설명 |
|------|------|------|
| `ANTHROPIC_API_KEY` | ✅ | Anthropic API 키 |
| `NOTION_TOKEN` | Notion 사용 시 | Integration 토큰 (`secret_...`) |
| `NOTION_PARENT_PAGE_ID` | Notion 사용 시 | 결과 페이지 부모 ID (하이픈 제거 32자리) |
| `SLACK_WEBHOOK_URL` | Slack(Webhook) | Incoming Webhook URL |
| `SLACK_BOT_TOKEN` | Slack(Bot) | Bot OAuth 토큰 (`xoxb-...`) |
| `SLACK_CHANNEL` | Slack(Bot) | 채널명 (기본값 `#kdt-competitor-analysis`) |

Notion/Slack은 미설정 시 자동으로 건너뜁니다 — 로컬 MD 리포트만 생성됩니다.

---

## 스크래핑 로직

| 단계 | 설명 |
|------|------|
| depth0 | 경쟁사 메인 페이지 전체 텍스트 + `<a>` 링크 후보 추출 |
| 링크 필터 | 같은 도메인 + 키워드 매칭 (`bootcamp`, `camp`, `course`, `track`, `부트캠프`, `과정` 등) |
| depth1 | 후보 링크 상위 **최대 10개** 상세 페이지 순차 스크래핑 |
| LLM 입력 | depth0 2,000자 + depth1 각 1,500자, 총 **8,000자 컷** |
| 구조화 | 과정명 · 트랙 · 기간 · 시작일 · 상태 · 특장점(≤3) · 커리큘럼 키워드(≤5) · 취업 지원 · 국비/비용 |

---

## 캐시 & Diff 전략

- 경쟁사별 `data/cache/{competitor_key}.json`에 마지막 조사 결과 보관
- 부트캠프 식별자: `md5(name + track)` 앞 10자리
- 매 실행마다 `added` / `removed` / `changed` / `unchanged` 분류 → 변경 델타만 인사이트 단계로 전달
- **첫 실행**은 모든 과정이 `added`로 잡힘 → 베이스라인 형성

---

## 리포트 구성 (MD)

`documenter.py`가 빌드하는 리포트는 다음 섹션으로 구성됩니다:

1. **헤더** — 조사 일시, 경쟁사 목록
2. **핵심 요약** — Sonnet이 300자로 축약 (Slack 알림과 공용)
3. **이번 조사 변경사항** — 신규/종료/변경 건수 테이블
4. **경영진 요약 (Executive Summary)**
5. **경쟁 위협 분석** — 심각도 배지 (🔴/🟡/🟢) + 영향 트랙 + 대응 방안
6. **기회 요소** — 근거 · 실행 방안
7. **자사 차별화 분석** — 강점 / 보완점 / 포지셔닝 제안
8. **트랙별 전략 권고사항**
9. **Quick Wins** — 즉시 실행 가능한 개선사항 3개
10. **트랙별 시장 커버리지** — 자사 vs 3개 경쟁사 매트릭스
11. **경쟁 관계 매핑** — 직접/간접/비경쟁 분류
12. **경쟁사 신규 트렌드**
13. **경쟁사별 모집 현황 상세** — 과정 테이블 + 특장점 + 변경사항
14. **자사 현재 모집 과정**

---

## 모델 선택 근거

| 단계 | 모델 | 근거 |
|------|------|------|
| Researcher | Sonnet 4.6 | 정형 추출 — 비용 대비 충분 |
| Analyzer | Sonnet 4.6 | 분류·매핑 — 중간 복잡도 |
| InsightGenerator | **Opus 4.6 + thinking(4k)** | 다중 신호 종합 + 전략 추론 — 최고 추론력 필요 |
| Documenter | Sonnet 4.6 | 요약 문장 생성 |

---

## 운영 팁

- **첫 실행은 베이스라인**: 변경사항 분석은 2회차부터 의미가 생깁니다.
- **정기 실행 권장**: 주 1~2회 cron 또는 슬래시 커맨드로 자동화하면 변화 신호가 누적됩니다.
- **모델 단가 통제**: Phase 3만 Opus를 사용하므로, 토큰 절약은 Phase 2 입력(`competitor_data` 12,000자 컷)을 우선 조정.
- **새 경쟁사 추가**: `config.py`의 `COMPETITORS` 딕셔너리에 추가하면 자동으로 파이프라인에 포함됩니다.

---

## 확장 포인트

- **데이터베이스화**: `utils/notion_api.py:update_or_create_database_entry`를 활용해 Notion DB 누적
- **시계열 추적**: `outputs/` 회차별 JSON을 후처리하여 변경 빈도/이탈 추세 대시보드 생성
- **알림 다채널화**: `documenter.py`에 Email/Discord/Teams 어댑터 추가

---

## 라이선스

내부 사용 (멋쟁이사자처럼 마케팅 본부).
