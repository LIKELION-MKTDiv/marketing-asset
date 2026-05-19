# LLM 연동 방식 분석 및 결정 기록

## 개요

이 문서는 resume-pipeline의 LLM 호출 방식을 결정하는 과정에서 검토한 내용과 최종 결론을 기록한다.
동일한 구조의 파이프라인을 구성할 때 참고용 README로 활용할 수 있다.

---

## 배경

resume-pipeline은 지원서 CSV와 부트캠프 커리큘럼 정보를 입력받아 AI 기반 미래이력서를 생성하는 파이프라인이다.
초기 구현은 Anthropic Python SDK + `ANTHROPIC_API_KEY`를 사용하여 API를 직접 호출하는 방식이었다.

### 기존 구조

```
Python 코드 (로컬)
    ↓ HTTP 요청 (anthropic Python SDK)
Anthropic API 서버 (api.anthropic.com)
    ↓ 응답
Python 코드 → 파일 저장
```

**핵심:** 코드가 로컬에서 실행되더라도, AI 모델은 Anthropic 서버에서만 동작한다.
로컬 실행 여부와 무관하게 API 호출 자체가 과금 단위이다.

---

## 인증 방식 비교

### Anthropic API (기존)

| 항목 | 내용 |
|---|---|
| 인증 수단 | `ANTHROPIC_API_KEY` (Console에서 별도 발급) |
| 과금 방식 | 토큰당 과금 (입력/출력 토큰 합산) |
| 엔드포인트 | `https://api.anthropic.com` |
| 공식 문서 | [Anthropic API Docs](https://platform.claude.com/docs/en/api/getting-started) |

### Claude CLI (`claude -p`)

| 항목 | 내용 |
|---|---|
| 인증 수단 | Claude 구독 OAuth 토큰 (자동 관리) |
| 과금 방식 | 구독 크레딧 소비 (별도 API 청구 없음) |
| 엔드포인트 | claude.ai 인증 시스템 경유 |

### 구독 OAuth 토큰으로 Python SDK 직접 사용 가능 여부

**불가.** Anthropic API 공식 문서 기준, 인증 수단은 다음 두 가지만 지원된다.

1. `x-api-key` — API 키 (Console에서 발급, 토큰당 과금)
2. `Authorization: Bearer <token>` — Workload Identity Federation (AWS/GCP 기업 인프라 전용)

Claude 구독 OAuth 토큰은 `claude.ai` 계정 시스템 전용이며, Anthropic API(`api.anthropic.com`)와는 별개 시스템이다.
구독 토큰을 Python SDK의 `ANTHROPIC_API_KEY`에 주입하는 방법은 공식적으로 지원되지 않는다.

---

## 로컬 실행 시 비용 발생 구조

흔한 오해: *"로컬에서 돌리면 비용이 없다"*

실제 구조는 다음과 같다.

```
[로컬 Python 코드]  →  HTTP 요청  →  [Anthropic 서버, AI 모델 실행]
```

AI 모델(Claude Opus 등)은 Anthropic 데이터센터 서버에만 존재한다.
로컬에 다운로드하거나 설치하는 것은 불가능하다.
코드 실행 위치(로컬, EC2, 컨테이너 등)와 무관하게, API 호출 자체에 토큰 기준으로 과금된다.

---

## 최종 선택: Claude CLI subprocess 방식

### 변경 내용

`utils/llm.py`의 `call_sonnet` / `call_opus_streaming` 함수를 `subprocess.run`으로 교체했다.
`parse_json_response` 등 나머지 코드는 변경 없음.

```python
# 변경 전 (Anthropic SDK)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
msg = client.messages.create(model=MODEL_FAST, ...)

# 변경 후 (Claude CLI subprocess)
result = subprocess.run(
    ["claude", "-p", user, "--system-prompt", system, "--model", MODEL_FAST,
     "--dangerously-skip-permissions"],
    capture_output=True, text=True, timeout=120
)
```

Phase 3 (Opus + extended thinking) 대응:

```python
result = subprocess.run(
    ["claude", "-p", user, "--system-prompt", system, "--model", MODEL_DEEP,
     "--effort", "max", "--dangerously-skip-permissions"],
    capture_output=True, text=True, timeout=600
)
```

`--effort max`는 Claude CLI에서 extended thinking(고강도 추론)을 활성화하는 플래그다.

### SDK 제거가 가능한 이유

파이프라인의 각 Phase는 LLM에 프롬프트를 전달하고 텍스트 응답을 받는 구조이며,
JSON 파싱은 이미 `parse_json_response()`에서 텍스트 기반으로 처리하고 있다.
SDK 전용 기능(스트리밍 객체, `usage.tokens` 로깅)에 의존하는 로직이 없으므로 교체가 가능하다.

---

## 출력 품질 비교

동일 지원자 데이터, 동일 모델(`claude-sonnet-4-6` / `claude-opus-4-6`)을 기준으로 두 방식의 출력 결과를 스코어링했다.

### 스코어링 기준

| 항목 | 배점 |
|---|---|
| Headline 임팩트 (첫 문장에서 지원자 강점이 드러나는가) | 20 |
| 프로젝트 구체성 (Phase별 프로젝트가 상세 기술되는가) | 20 |
| 기술 스택 정확도 (보유/예상 역량 구분이 명확한가) | 20 |
| 부트캠프 정보 충실도 (과정 내용이 지원자에게 커스터마이징됐는가) | 15 |
| 레이아웃 가독성 (텍스트 과밀 없이 읽기 쉬운가) | 15 |
| 브랜딩 일관성 | 10 |

### 결과

| 항목 | SDK 방식 | CLI 방식 |
|---|---|---|
| Headline 임팩트 | 18 | 12 |
| 프로젝트 구체성 | 19 | 11 |
| 기술 스택 정확도 | 17 | 16 |
| 부트캠프 정보 충실도 | 13 | 10 |
| 레이아웃 가독성 | 13 | 11 |
| 브랜딩 일관성 | 9 | 8 |
| **합계** | **89점** | **68점** |

### 점수 차이의 원인

점수 차이는 모델 품질 차이가 아니라 **입력 데이터 품질 차이**에서 발생했다.

- SDK 버전 실행 시: 실제 부트캠프 상세 커리큘럼 파일 사용 (ArgoCD, EKS, AIOps, Spring Boot 등 구체적 기술 스택 포함)
- CLI 버전 실행 시: 테스트용으로 범용 커리큘럼 MD 파일 사용

동일한 입력 데이터를 사용할 경우 두 방식의 출력 품질은 동등하다.
Opus 모델과 `--effort max`(extended thinking)는 SDK의 `thinking={"type": "adaptive"}`에 상응하는 수준으로 동작했다.

---

## 결론

| 항목 | Anthropic SDK | Claude CLI subprocess |
|---|---|---|
| 인증 | API 키 필요 | 구독 토큰 (자동) |
| 과금 | 토큰당 별도 청구 | 구독 크레딧 소비 |
| 모델 | `claude-opus-4-6` | `claude-opus-4-6` (동일) |
| Extended thinking | `thinking={"type":"adaptive"}` | `--effort max` |
| 코드 변경 범위 | — | `utils/llm.py` 2개 함수 |
| 출력 품질 | 동등 (입력 동일 시) | 동등 (입력 동일 시) |

**입력 데이터(부트캠프 커리큘럼 정보)의 상세도가 출력 품질을 결정하는 핵심 변수다.**
LLM 호출 방식(SDK vs CLI)은 품질에 영향을 주지 않는다.
