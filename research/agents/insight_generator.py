"""
[Agent 3] 인사이트 도출 에이전트 — 분석 결과에서 전략적 인사이트 생성.
Opus 모델 사용 (가장 고차원 추론 필요).
"""
import json
import anthropic
from config import INSIGHT_MODEL, ANTHROPIC_API_KEY
from datetime import datetime


INSIGHT_PROMPT = """
당신은 멋쟁이사자처럼(Likelion)의 마케팅 전략 어드바이저입니다.
KDT 부트캠프 시장에서 경쟁사 분석 결과를 바탕으로 실행 가능한 전략 인사이트를 도출해주세요.

## 분석 데이터
{analysis_data}

## 요청 사항

다음 구조로 인사이트를 작성하세요:

### 1. executive_summary (경영진 요약, 3-5문장)
이번 조사의 핵심 발견사항 요약

### 2. competitive_threats (경쟁 위협, 우선순위 순)
각 항목:
- threat: 위협 내용
- severity: "높음" | "중간" | "낮음"
- affected_tracks: 영향받는 트랙
- recommendation: 대응 방안

### 3. opportunities (기회 요소)
각 항목:
- opportunity: 기회 내용
- rationale: 근거
- action: 활용 방안

### 4. differentiation_analysis (차별화 분석)
- our_strengths: 자사 강점 (경쟁사 대비)
- gaps_to_fill: 보완이 필요한 부분
- unique_positioning: 차별화 포지셔닝 제안

### 5. track_recommendations (트랙별 권고사항)
각 트랙에 대해:
- track: 트랙명
- situation: 현황
- recommendation: 권고 방향

### 6. quick_wins (즉시 실행 가능한 개선사항, 3개)

JSON으로 응답. 한국어로 작성.
"""


async def run(analysis_result: dict) -> dict:
    """분석 결과에서 전략 인사이트를 도출."""
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    prompt = INSIGHT_PROMPT.format(
        analysis_data=json.dumps(analysis_result["analysis"], ensure_ascii=False, indent=2)[:10000],
    )

    print("[InsightGenerator] Opus 모델로 전략 인사이트 생성 중...")
    message = await client.messages.create(
        model=INSIGHT_MODEL,
        max_tokens=12000,
        thinking={
            "type": "enabled",
            "budget_tokens": 4000,
        },
        messages=[{"role": "user", "content": prompt}],
    )

    # thinking 블록 제외하고 텍스트만 추출
    raw = ""
    for block in message.content:
        if block.type == "text":
            raw = block.text.strip()
            break

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        insights = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[InsightGenerator] JSON 파싱 실패, 텍스트로 저장")
        insights = {"raw_text": raw}

    return {
        "insights": insights,
        "generated_at": datetime.now().isoformat(),
        "analysis_result": analysis_result,
    }
