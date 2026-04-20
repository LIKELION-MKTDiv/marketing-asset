"""
[Agent 4] 문서화 에이전트.
insights.json / analysis.json 의 전체 데이터를 MD 리포트로 변환한다.
"""
import json
import re
from datetime import datetime
from pathlib import Path
import anthropic
from config import DOC_MODEL, ANTHROPIC_API_KEY, OUTPUT_DIR


# ─────────────────────────────────────────────
# JSON 파싱 헬퍼 (raw_text / raw 문자열 처리)
# ─────────────────────────────────────────────

def _parse_raw(value) -> dict | list | None:
    """dict/list면 그대로, 문자열이면 JSON 파싱 시도.
    불완전한 JSON의 경우 섹션별 키를 개별 파싱해 dict로 조합한다."""
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return None

    text = value.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text).strip()

    # 1) 완전한 JSON 파싱
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2) 불완전 JSON — 각 최상위 키를 개별로 추출
    result = {}
    # 최상위 키 목록 탐색
    key_pattern = re.compile(r'"(\w+)"\s*:\s*', re.MULTILINE)
    top_keys = []
    for m in key_pattern.finditer(text):
        # 대략적인 depth 파악 — 0레벨 키만 수집
        before = text[:m.start()]
        depth = before.count('{') - before.count('}') + before.count('[') - before.count(']')
        if depth <= 1:
            top_keys.append((m.group(1), m.start()))

    for idx, (key, start) in enumerate(top_keys):
        # 값 시작 위치
        val_start = text.index(':', start) + 1
        # 다음 최상위 키 직전까지 또는 끝까지
        val_end = top_keys[idx + 1][1] - 1 if idx + 1 < len(top_keys) else len(text)
        val_str = text[val_start:val_end].strip().rstrip(',').strip()
        try:
            result[key] = json.loads(val_str)
        except Exception:
            # 문자열로라도 저장
            result[key] = val_str

    return result if result else None


# ─────────────────────────────────────────────
# 요약 생성 (Slack/헤더용)
# ─────────────────────────────────────────────

SUMMARY_PROMPT = """
아래 KDT 경쟁사 분석 인사이트를 300자 이내 요약으로 작성하세요.
핵심 발견 2-3가지 + 즉시 실행 가능한 액션 1개 포함. 한국어로.

{insights}
"""


async def _make_summary(insights: dict) -> str:
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    msg = await client.messages.create(
        model=DOC_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": SUMMARY_PROMPT.format(
            insights=json.dumps(insights, ensure_ascii=False)[:3000]
        )}]
    )
    return msg.content[0].text.strip()


# ─────────────────────────────────────────────
# MD 빌더
# ─────────────────────────────────────────────

def _severity_badge(s: str) -> str:
    return {"높음": "🔴 높음", "중간": "🟡 중간", "낮음": "🟢 낮음"}.get(s, s)


def _build_md(insight_result: dict, summary: str) -> str:
    # 원시 데이터 파싱
    raw_insights = insight_result.get("insights", {})
    insights = _parse_raw(raw_insights.get("raw_text", raw_insights)) or raw_insights

    analysis_result = insight_result.get("analysis_result", {})
    raw_analysis = analysis_result.get("analysis", {})
    analysis = _parse_raw(raw_analysis.get("raw", raw_analysis)) or raw_analysis

    research = analysis_result.get("research_data", {})
    stats = analysis_result.get("change_stats", {})
    date_str = insight_result.get("generated_at", "")[:10]

    lines = []

    # ── 헤더 ──────────────────────────────────
    lines += [
        f"# KDT 경쟁사 분석 리포트",
        f"",
        f"> **조사 일시:** {date_str}",
        f"> **경쟁사:** 패스트캠퍼스 커널 / 스파르타 내일배움캠프 / 코드잇 스프린트",
        f"> **자사:** 멋쟁이사자처럼 (bootcamp.likelion.net)",
        f"",
        f"---",
        f"",
    ]

    # ── 핵심 요약 ──────────────────────────────
    lines += ["## 핵심 요약", "", summary, "", "---", ""]

    # ── 변경사항 통계 ──────────────────────────
    lines += [
        "## 이번 조사 변경사항",
        "",
        "| 구분 | 건수 |",
        "|------|------|",
        f"| 신규 부트캠프 | **{stats.get('total_added', 0)}개** |",
        f"| 종료/삭제 | {stats.get('total_removed', 0)}개 |",
        f"| 내용 변경 | {stats.get('total_changed', 0)}개 |",
        "",
        "---",
        "",
    ]

    # ── Executive Summary ─────────────────────
    exec_summary = insights.get("executive_summary", "")
    if exec_summary:
        lines += [
            "## 경영진 요약",
            "",
            exec_summary,
            "",
            "---",
            "",
        ]

    # ── 경쟁 위협 ──────────────────────────────
    threats = insights.get("competitive_threats", [])
    if threats:
        lines += ["## 경쟁 위협 분석", ""]
        for i, t in enumerate(threats, 1):
            severity = _severity_badge(t.get("severity", ""))
            affected = ", ".join(t.get("affected_tracks", []))
            lines += [
                f"### {i}. {t.get('threat', '')[:80]}",
                f"",
                f"- **심각도:** {severity}",
                f"- **영향 트랙:** {affected}",
                f"",
                f"**대응 방안**",
                f"",
                f"{t.get('recommendation', '')}",
                f"",
            ]
        lines += ["---", ""]

    # ── 기회 요소 ──────────────────────────────
    opportunities = insights.get("opportunities", [])
    if opportunities:
        lines += ["## 기회 요소", ""]
        for i, o in enumerate(opportunities, 1):
            lines += [
                f"### {i}. {o.get('opportunity', '')}",
                f"",
                f"**근거:** {o.get('rationale', '')}",
                f"",
                f"**실행 방안:** {o.get('action', '')}",
                f"",
            ]
        lines += ["---", ""]

    # ── 차별화 분석 ────────────────────────────
    diff = insights.get("differentiation_analysis", {})
    if diff:
        lines += ["## 자사 차별화 분석", ""]

        strengths = diff.get("our_strengths", [])
        if strengths:
            lines += ["### 자사 강점 (경쟁사 대비)", ""]
            for s in strengths:
                lines.append(f"- {s}")
            lines.append("")

        gaps = diff.get("gaps_to_fill", [])
        if gaps:
            lines += ["### 보완이 필요한 부분", ""]
            for g in gaps:
                lines.append(f"- {g}")
            lines.append("")

        positioning = diff.get("unique_positioning", "")
        if positioning:
            lines += [
                "### 차별화 포지셔닝 제안",
                "",
                positioning,
                "",
            ]
        lines += ["---", ""]

    # ── 트랙별 권고사항 ────────────────────────
    track_recs = insights.get("track_recommendations", [])
    if isinstance(track_recs, list) and track_recs:
        lines += ["## 트랙별 전략 권고사항", ""]
        for tr in track_recs:
            if not isinstance(tr, dict):
                continue
            lines += [
                f"### {tr.get('track', '')}",
                f"",
                f"**현황**",
                f"",
                f"{tr.get('situation', '')}",
                f"",
                f"**권고 방향**",
                f"",
                f"{tr.get('recommendation', '')}",
                f"",
            ]
        lines += ["---", ""]

    # ── Quick Wins ────────────────────────────
    quick_wins = insights.get("quick_wins", [])
    if quick_wins:
        lines += ["## 즉시 실행 가능한 개선사항 (Quick Wins)", ""]
        for i, w in enumerate(quick_wins, 1):
            lines.append(f"{i}. {w}")
        lines += ["", "---", ""]

    # ── 시장 커버리지 ──────────────────────────
    market_coverage = analysis.get("market_coverage", [])
    if market_coverage:
        lines += [
            "## 트랙별 시장 커버리지",
            "",
            "| 트랙 | 자사 | 패스트캠퍼스 | 스파르타 | 코드잇 |",
            "|------|------|-------------|---------|--------|",
        ]
        for mc in market_coverage:
            track = mc.get("track", "")
            likelion = "✅" if mc.get("likelion_offers") else "❌"
            competitors = mc.get("competitors_offering", [])
            fc = "✅" if any("패스트캠퍼스" in c for c in competitors) else "❌"
            sp = "✅" if any("스파르타" in c for c in competitors) else "❌"
            co = "✅" if any("코드잇" in c for c in competitors) else "❌"
            lines.append(f"| {track} | {likelion} | {fc} | {sp} | {co} |")
        lines += ["", "---", ""]

    # ── 경쟁 관계 매핑 ────────────────────────
    comp_map = analysis.get("competitive_map", [])
    if comp_map:
        lines += [
            "## 경쟁 관계 매핑",
            "",
            "| 경쟁사 | 경쟁사 과정 | 자사 과정 | 경쟁 수준 |",
            "|--------|------------|---------|---------|",
        ]
        for cm in comp_map:
            competitor = cm.get("competitor", "")
            their = cm.get("their_camp", "-")
            ours = cm.get("our_camp") or "없음"
            level = cm.get("competition_level", "")
            level_badge = {"직접경쟁": "🔴 직접", "간접경쟁": "🟡 간접", "비경쟁": "⚪ 없음"}.get(level, level)
            lines.append(f"| {competitor} | {their} | {ours} | {level_badge} |")
        lines += ["", "---", ""]

    # ── 신규 트렌드 ────────────────────────────
    new_trends = analysis.get("new_trends", [])
    if new_trends:
        lines += ["## 경쟁사 신규 트렌드", ""]
        for tr in new_trends:
            trend_name = tr.get("trend", "")
            desc = tr.get("description", "")
            competitor = tr.get("competitor", "")
            related = tr.get("related_camp", "")
            lines += [
                f"### {trend_name}",
                f"",
                f"{desc}",
                f"",
                f"- **발견 경쟁사:** {competitor}",
                f"- **관련 과정:** {related}",
                f"",
            ]
        lines += ["---", ""]

    # ── 경쟁사별 모집 현황 ─────────────────────
    lines += ["## 경쟁사별 모집 현황 상세", ""]
    for comp in research.get("competitors", []):
        diff_info = comp.get("diff", {})
        all_camps = comp.get("all_bootcamps", [])

        lines += [
            f"### {comp['name']}",
            f"",
            f"🔗 {comp['url']}",
            f"",
        ]

        if all_camps:
            lines += [
                "| 과정명 | 트랙 | 기간 | 상태 | 국비지원 |",
                "|--------|------|------|------|---------|",
            ]
            for b in all_camps:
                price = b.get("price_info", "")
                kdt = "✅" if price and ("국비" in price or "내일배움" in price) else "-"
                lines.append(
                    f"| {b.get('name','')} | {b.get('track','')} "
                    f"| {b.get('duration','')} | {b.get('status','')} | {kdt} |"
                )
            lines.append("")

            # 특장점/커리큘럼 상세
            for b in all_camps:
                name = b.get("name", "")
                features = b.get("features", [])
                keywords = b.get("curriculum_keywords", [])
                employment = b.get("employment_support", "")
                if features or keywords or employment:
                    lines += [f"**{name}**", ""]
                    if features:
                        for f in features:
                            lines.append(f"- {f}")
                    if keywords:
                        lines.append(f"- 커리큘럼: {', '.join(keywords)}")
                    if employment:
                        lines.append(f"- 취업 지원: {employment}")
                    lines.append("")

        # 변경사항
        added = diff_info.get("added", [])
        removed = diff_info.get("removed", [])
        changed = diff_info.get("changed", [])
        if added:
            lines += ["**🆕 신규 과정**"]
            for b in added:
                lines.append(f"- {b.get('name','')} ({b.get('track','')})")
            lines.append("")
        if removed:
            lines += ["**❌ 종료/삭제**"]
            for b in removed:
                lines.append(f"- {b.get('name','')} ({b.get('track','')})")
            lines.append("")
        if changed:
            lines += ["**✏️ 내용 변경**"]
            for c in changed:
                lines.append(f"- {c.get('new',{}).get('name','')}")
            lines.append("")

        lines.append("")

    # ── 자사 현황 ──────────────────────────────
    own = research.get("own_bootcamps", [])
    if own:
        lines += ["## 자사 현재 모집 과정", ""]
        for b in own:
            lines += [
                f"### {b.get('name','')}",
                f"- **트랙:** {b.get('track','')}",
                f"- **기간:** {b.get('duration','')}",
                f"- **상태:** {b.get('status','')}",
            ]
            features = b.get("features", [])
            if features:
                for f in features:
                    lines.append(f"- {f}")
            lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 실행 진입점
# ─────────────────────────────────────────────

async def run(insight_result: dict) -> dict:
    date_str = datetime.now().strftime("%Y-%m-%d")
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")

    print("[Documenter] 요약 생성 중...", flush=True)
    raw_insights = insight_result.get("insights", {})
    parsed = _parse_raw(raw_insights.get("raw_text", raw_insights)) or {}
    summary = await _make_summary(parsed)

    print("[Documenter] MD 리포트 빌드 중...", flush=True)
    md_content = _build_md(insight_result, summary)

    out_dir = OUTPUT_DIR / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"report_{date_str}.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"[Documenter] 리포트 저장 완료: {md_path}", flush=True)

    return {
        "report_path": str(md_path),
        "notion_url": None,
        "slack_sent": False,
        "summary": summary,
    }
