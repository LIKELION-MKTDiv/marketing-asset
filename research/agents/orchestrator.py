"""
[Head Agent] 오케스트레이터 — 하위 에이전트를 순서대로 조율한다.
사용자 명령: "경쟁사 분석"
"""
import json
import asyncio
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR
from agents import researcher, analyzer, insight_generator, documenter


async def run(verbose: bool = True) -> dict:
    """
    경쟁사 분석 전체 파이프라인 실행.

    Phase 1: 조사 (Researcher)
    Phase 2: 분석 (Analyzer)
    Phase 3: 인사이트 도출 (InsightGenerator)
    Phase 4: 문서화 (Documenter)
    """
    start_time = datetime.now()
    print(f"\n{'='*60}", flush=True)
    print(f"KDT 경쟁사 분석 파이프라인 시작: {start_time.strftime('%Y-%m-%d %H:%M')}", flush=True)
    print(f"{'='*60}\n", flush=True)

    # Phase 1: 조사
    print("[Phase 1/4] 데이터 수집 중...", flush=True)
    research_data = await researcher.run()
    _log_phase("research", research_data, start_time)

    if verbose:
        for comp in research_data["competitors"]:
            diff = comp["diff"]
            print(f"  {comp['name']}: 신규 {len(diff['added'])}개 / 종료 {len(diff['removed'])}개 / 변경 {len(diff['changed'])}개", flush=True)

    # Phase 2: 분석
    print("\n[Phase 2/4] 경쟁 분석 중...", flush=True)
    analysis_result = await analyzer.run(research_data)
    _log_phase("analysis", analysis_result, start_time)

    # Phase 3: 인사이트
    print("\n[Phase 3/4] 전략 인사이트 도출 중...", flush=True)
    insight_result = await insight_generator.run(analysis_result)
    _log_phase("insights", insight_result, start_time)

    # Phase 4: 문서화
    print("\n[Phase 4/4] MD 리포트 생성 중...", flush=True)
    doc_result = await documenter.run(insight_result)

    # 최종 결과
    end_time = datetime.now()
    elapsed = (end_time - start_time).seconds
    result = {
        "status": "완료",
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "elapsed_seconds": elapsed,
        "report_path": doc_result.get("report_path"),
        "notion_url": doc_result.get("notion_url"),
        "slack_sent": doc_result.get("slack_sent", False),
        "summary": doc_result["summary"],
        "change_stats": analysis_result["change_stats"],
    }

    _log_phase("final", result, start_time)

    print(f"\n{'='*60}", flush=True)
    print(f"[완료] 분석 완료 ({elapsed}초 소요)", flush=True)
    print(f"[리포트] {doc_result.get('report_path', '-')}", flush=True)
    if doc_result.get("notion_url"):
        print(f"[Notion] {doc_result['notion_url']}", flush=True)
    if doc_result.get("slack_sent"):
        print(f"[Slack] 전송됨", flush=True)
    print(f"{'='*60}\n", flush=True)

    return result


def _log_phase(phase: str, data: dict, start_time: datetime) -> None:
    """각 단계 결과를 outputs 디렉토리에 저장."""
    date_str = start_time.strftime("%Y-%m-%d_%H%M")
    out_dir = OUTPUT_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{phase}.json"
    out_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )
