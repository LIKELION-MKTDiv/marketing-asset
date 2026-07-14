# VOC 위클리 리포트 자동화

Channel.io(채널톡)에 쌓이는 고객 문의(VOC)를 API로 직접 수집해서, **첫 응답 시간·ALF(챗봇) 해결률**을 매주 자동으로 집계하고 Slack으로 발송하는 파이프라인. 화요판 심층분석(정성 분석)은 이 코드가 아니라 사람(+AI 세션)이 직접 작성하며, 그 작업에 쓰는 분석 규칙(방법론)만 이 저장소에 함께 공개합니다.

> 원본 저장소: `voc-report-automation`(비공개) — 이 폴더는 코드와 방법론만 선별해 옮긴 사본입니다.

---

## 🚀 구성

| 파일 | 역할 |
|---|---|
| `collect.py` | Channel.io Open API로 특정 기간 채팅 데이터를 수집해 CSV로 저장 |
| `send_monday_report.py` | 월요판 헤드라인 리포트 계산 + Slack 발송(트렌드 바차트·누적요약 포함) |
| `precise_review.py` | ALF 해결률·첫응답시간을 태그 기반 근사치 대신 **Claude가 케이스별로 자동 검토**해서 보정 |
| `course_breakdown.py` | 화요판 작성 전, 과정별 인입 건수를 태그 기준으로 사전 집계 |
| `voc_weekly_history.json` | 주차별 확정 지표 이력(첫응답시간·ALF해결률) — 트렌드 차트용, 집계 수치만 포함 |
| `methodology/monday_template.md` | 월요판 자동 계산 규칙 |
| `methodology/tuesday_template.md` | 화요판 정성분석 규칙 — 결론 한 문장 선별, 고객 원문 인용, 가설-근거-검증 3줄 세트, 주차 간 이슈 추적, 금지 표현 등 |

## ⚙️ 실행 방법

```bash
pip install -r requirements.txt
cp .env.example .env   # 아래 환경변수 채워넣기

python collect.py --from 2026-07-06 --to 2026-07-12
python send_monday_report.py --from 2026-07-06 --to 2026-07-12 --send
```

### 환경 변수 (`.env`)

| 변수 | 용도 |
|---|---|
| `CHANNEL_ACCESS_KEY`, `CHANNEL_ACCESS_SECRET` | Channel.io Open API 인증 |
| `SLACK_WEBHOOK_TEST` / `SLACK_WEBHOOK_REPORT` / `SLACK_WEBHOOK_QNA` | 채널별 Slack 발송 웹훅 |
| `SLACK_BOT_TOKEN` | Slack 채널 읽기(`conversations.history`)용 |
| `ANTHROPIC_API_KEY` | `precise_review.py`의 케이스별 자동 검수용(Claude API) |

---

## 💡 이 자동화가 푸는 문제

- **ALF 해결률을 태그만 보고 계산하면 실제보다 낮게 나온다** — ALF가 답변하고 고객이 더 응답하지 않으면 채팅이 `closed`로 전환되지 않고 `initial`(대기) 상태로 남는 등, API 상태값 하나만 믿으면 안 되는 지점들을 여러 차례 검증하며 코드로 고정해뒀습니다(`collect.py` 상단 주석 참고).
- **"매니저 연결 = ALF 실패"가 아니다** — 환불/계정탈퇴처럼 정책상 사람이 처리해야 하는 문의와, ALF가 원래 답할 수 있어야 하는 정보성 문의를 구분해서 해결률을 계산합니다(`methodology/tuesday_template.md`의 ALF 해결률 산정 방식 참고).
- **사람이 매주 원본 대화를 전부 읽지 않아도 되게** — `course_breakdown.py`가 태그로 이미 명확한 건은 자동 집계하고, 애매한 건만 review_queue로 남겨서 사람이 그 부분만 집중해서 읽도록 합니다.

---

## 🔒 데이터 보안

- **이 폴더에는 실제 상담 원본 데이터가 포함되어 있지 않습니다.** `archive/`(주차별 원본 CSV), `precise_review_cache/`(AI 검수 캐시)는 원본 저장소에만 있으며 이 공개 사본에는 올리지 않았습니다.
- `voc_weekly_history.json`은 주차별 **집계 수치**(첫응답시간 초, ALF 해결률 %, 건수)만 담고 있어 개인정보가 없습니다.
- 실제 운영 시에는 반드시 `.env`(git에 올리지 않음)에 API 키·웹훅 URL을 넣어 사용하세요.
- 상담요약처럼 자유 텍스트가 섞인 데이터를 다룰 때는 컬럼 삭제만으로 익명화가 끝나지 않는다는 점(자유 텍스트 안에 실명이 박혀 있을 수 있음)을 원본 저장소 운영 중 직접 겪었습니다 — 관련 데이터를 다시 다룰 일이 있다면 자유 텍스트 필드도 반드시 스캔하세요.
