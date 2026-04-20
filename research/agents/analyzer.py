"""
[Agent 2] 분석 에이전트 — 수집 데이터 정제/분류 및 자사와 경쟁 관계 분석.
"""
import json
import anthropic
from config import ANALYSIS_MODEL, ANTHROPIC_API_KEY


ANALYSIS_PROMPT = """
당신은 KDT 교육시장 경쟁 분석 전문가입니다.

## 자사 (멋쟁이사자처럼) 현재 모집 부트캠프
{own_bootcamps}

## 경쟁사 조사 결과
{competitor_data}

다음 항목을 분석해 JSON으로 응답하세요:

1. competitive_map: 경쟁사별로 자사와 직접 경쟁하는 과정 매핑
   - competitor: 경쟁사명
   - their_camp: 경쟁사 과정명
   - our_camp: 자사 유사 과정명
   - competition_level: "직접경쟁" | "간접경쟁" | "비경쟁"
   - overlap_reason: 겹치는 이유

2. market_coverage: 트랙별 시장 커버리지
   - track: 트랙명
   - competitors_offering: 해당 트랙을 제공하는 경쟁사 목록
   - likelion_offers: 멋쟁이사자처럼이 제공 여부 (bool)

3. new_trends: 경쟁사에서 새로 보이는 트렌드/기술 스택 (자사에 없는 것)

4. changes_summary: 이번 조사에서 발견된 주요 변경사항 요약
   - added_camps: 새로 발견된 과정들
   - removed_camps: 사라진 과정들
   - notable_changes: 주목할 변경사항

JSON만 응답. 설명 불필요.
"""


async def run(research_data: dict) -> dict:
    """연구 데이터를 받아 경쟁 분석을 수행."""
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    # 경쟁사 데이터 요약 (토큰 절약)
    competitor_summary = []
    for comp in research_data["competitors"]:
        competitor_summary.append({
            "name": comp["name"],
            "bootcamps": comp["all_bootcamps"],
            "changes": {
                "added": comp["diff"]["added"],
                "removed": comp["diff"]["removed"],
                "changed": [c["new"] for c in comp["diff"]["changed"]],
            }
        })

    prompt = ANALYSIS_PROMPT.format(
        own_bootcamps=json.dumps(research_data["own_bootcamps"], ensure_ascii=False, indent=2),
        competitor_data=json.dumps(competitor_summary, ensure_ascii=False, indent=2)[:12000],
    )

    message = await client.messages.create(
        model=ANALYSIS_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[Analyzer] JSON 파싱 실패: {raw[:200]}")
        analysis = {"raw": raw}

    # 변경 통계 집계
    total_added = sum(len(c["diff"]["added"]) for c in research_data["competitors"])
    total_removed = sum(len(c["diff"]["removed"]) for c in research_data["competitors"])
    total_changed = sum(len(c["diff"]["changed"]) for c in research_data["competitors"])

    return {
        "analysis": analysis,
        "change_stats": {
            "total_added": total_added,
            "total_removed": total_removed,
            "total_changed": total_changed,
        },
        "research_data": research_data,
    }
