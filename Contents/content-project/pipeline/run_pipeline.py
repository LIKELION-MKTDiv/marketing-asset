"""
IT 취업 콘텐츠 발행 파이프라인
=====================================
4개 에이전트가 순차적으로 실행되어 날짜별 폴더에 산출물을 저장합니다.

실행 방법:
  python run_pipeline.py

환경 변수:
  ANTHROPIC_API_KEY: Anthropic API 키 (필수)

산출물 구조:
  outputs/YYYY-MM-DD/
    1_research_report.md     ← 트렌드 조사 리포트
    2_selected_trends.md     ← 선별된 트렌드
    3_draft_content.md       ← 초안 콘텐츠
    4_reviewed_content.md    ← 검수 리포트 + 최종 콘텐츠
    pipeline_log.txt         ← 실행 로그
"""

import anthropic
import datetime
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# ── 경로 설정 ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
AGENTS_DIR = PROJECT_DIR / "agents"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
SEO_GUIDE_PATH = PROJECT_DIR / "SEOREADME.md"


def load_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def log(msg: str, log_path: Path):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def call_agent(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_message: str,
    step_name: str,
    log_path: Path,
    max_tokens: int = 8000,
) -> str:
    """Claude API 호출 (adaptive thinking + streaming)"""
    log(f"  → API 호출 중... ({step_name})", log_path)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        # 스트리밍으로 진행 상황 표시
        collected_text = []
        for event in stream:
            if (
                event.type == "content_block_delta"
                and hasattr(event.delta, "type")
                and event.delta.type == "text_delta"
            ):
                collected_text.append(event.delta.text)
                # 진행 점 표시 (100자마다)
                if len("".join(collected_text)) % 200 == 0:
                    print(".", end="", flush=True)

        final = stream.get_final_message()

    print()  # 줄바꿈
    # 텍스트 블록만 추출
    result = ""
    for block in final.content:
        if block.type == "text":
            result += block.text

    log(f"  ✓ 완료 (입력 {final.usage.input_tokens}토큰 / 출력 {final.usage.output_tokens}토큰)", log_path)
    return result


def run_pipeline():
    # API 키 확인
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ 오류: ANTHROPIC_API_KEY 환경 변수가 설정되어 있지 않습니다.")
        print("   설정 방법: set ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # 날짜별 출력 폴더 생성
    today = datetime.date.today().strftime("%Y-%m-%d")
    output_dir = OUTPUTS_DIR / today
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "pipeline_log.txt"

    print("\n" + "=" * 60)
    print("  IT 취업 콘텐츠 발행 파이프라인 시작")
    print(f"  날짜: {today}")
    print(f"  출력 폴더: {output_dir}")
    print("=" * 60 + "\n")

    log(f"파이프라인 시작 | 날짜: {today}", log_path)

    # SEO 가이드 로드
    seo_guide = load_file(SEO_GUIDE_PATH)

    # ── STEP 1: 트렌드 조사 ───────────────────────────────────────────────
    print("📡 STEP 1/4: 트렌드/정보 조사 에이전트 실행 중...")
    log("STEP 1: 트렌드 조사 시작", log_path)

    researcher_system = load_file(AGENTS_DIR / "researcher_prompt.md")
    researcher_user = f"""오늘 날짜 기준({today})으로 IT 개발자/비개발자 취업을 희망하는 사람들이
관심 가질 만한 최신 트렌드와 정보를 조사해주세요.

웹 검색, 최신 IT 뉴스, 채용 동향, SNS 화제 등을 종합하여
조사 리포트 형식에 맞게 5~7개 트렌드를 정리해주세요."""

    research_report = call_agent(
        client, researcher_system, researcher_user, "트렌드 조사", log_path
    )

    report_path = output_dir / "1_research_report.md"
    header = f"# 트렌드 조사 리포트\n생성일: {today}\n생성자: 트렌드 조사 에이전트\n\n---\n\n"
    save_file(report_path, header + research_report)
    print(f"  ✅ 저장: {report_path.name}\n")
    log(f"STEP 1 완료 → {report_path.name}", log_path)

    # ── STEP 2: 트렌드 선별 ───────────────────────────────────────────────
    print("🔍 STEP 2/4: 트렌드 선별 감독관 실행 중...")
    log("STEP 2: 트렌드 선별 시작", log_path)

    supervisor1_system = load_file(AGENTS_DIR / "research_supervisor_prompt.md")
    supervisor1_user = f"""아래 조사 리포트를 검토하고, 블로그 콘텐츠로 제작하기 가장 적합한
2~3개 주제를 선별하여 선별 리포트를 작성해주세요.

## 조사 리포트
{research_report}"""

    selected_trends = call_agent(
        client, supervisor1_system, supervisor1_user, "트렌드 선별", log_path
    )

    trends_path = output_dir / "2_selected_trends.md"
    header2 = f"# 트렌드 선별 리포트\n생성일: {today}\n생성자: 선별 감독관\n\n---\n\n"
    save_file(trends_path, header2 + selected_trends)
    print(f"  ✅ 저장: {trends_path.name}\n")
    log(f"STEP 2 완료 → {trends_path.name}", log_path)

    # ── STEP 3: 콘텐츠 작성 ───────────────────────────────────────────────
    print("✍️  STEP 3/4: 콘텐츠 에디터 실행 중...")
    log("STEP 3: 콘텐츠 작성 시작", log_path)

    editor_system = load_file(AGENTS_DIR / "editor_prompt.md")

    # 선별 리포트에서 우선순위 1위 주제만 추출
    priority1_section = selected_trends
    if "## 선별된 주제 [우선순위 2위]" in selected_trends:
        priority1_section = selected_trends.split("## 선별된 주제 [우선순위 2위]")[0].strip()
    elif "---" in selected_trends:
        sections = selected_trends.split("---")
        if len(sections) >= 2:
            priority1_section = "---".join(sections[:2]).strip()

    editor_user = f"""아래 우선순위 1위 주제 정보를 바탕으로 완성된 블로그 포스팅을 작성해주세요.

중요: thinking 없이 바로 블로그 본문을 작성해주세요. 출력 형식에 맞게 메타 정보부터 본문, CTA, 태그까지 빠짐없이 포함해야 합니다.

## 우선순위 1위 주제
{priority1_section}

## SEO 가이드
{seo_guide}"""

    draft_content = call_agent(
        client, editor_system, editor_user, "콘텐츠 작성", log_path,
        max_tokens=16000,
    )

    draft_path = output_dir / "3_draft_content.md"
    header3 = f"# 콘텐츠 초안\n생성일: {today}\n생성자: 콘텐츠 에디터\n상태: 검수 대기\n\n---\n\n"
    save_file(draft_path, header3 + draft_content)
    print(f"  ✅ 저장: {draft_path.name}\n")
    log(f"STEP 3 완료 → {draft_path.name}", log_path)

    # ── STEP 4: 콘텐츠 검수 ───────────────────────────────────────────────
    print("🔎 STEP 4/4: 콘텐츠 검수 감독관 실행 중...")
    log("STEP 4: 콘텐츠 검수 시작", log_path)

    supervisor2_system = load_file(AGENTS_DIR / "content_supervisor_prompt.md")
    supervisor2_user = f"""아래 초안 콘텐츠를 SEO 가이드 기준에 따라 검수하고 검수 리포트를 작성해주세요.

## SEO 가이드
{seo_guide}

## 초안 콘텐츠
{draft_content}"""

    reviewed_content = call_agent(
        client, supervisor2_system, supervisor2_user, "콘텐츠 검수", log_path,
        max_tokens=16000,
    )

    # 검수 리포트 + 원본 초안을 함께 저장
    reviewed_path = output_dir / "4_reviewed_content.md"
    header4 = (
        f"# 검수 완료 콘텐츠 패키지\n"
        f"생성일: {today}\n"
        f"상태: ⏳ 최종 검토 대기 (담당자 확인 필요)\n\n"
        f"---\n\n"
        f"## 검수 리포트\n\n"
    )
    divider = "\n\n---\n\n## 원본 초안 콘텐츠\n\n"
    save_file(reviewed_path, header4 + reviewed_content + divider + draft_content)
    print(f"  ✅ 저장: {reviewed_path.name}\n")
    log(f"STEP 4 완료 → {reviewed_path.name}", log_path)

    # ── 완료 메시지 ──────────────────────────────────────────────────────
    print("=" * 60)
    print("  ✅ 파이프라인 완료!")
    print(f"\n  📁 산출물 폴더: {output_dir}")
    print("\n  📋 생성된 파일:")
    for f in sorted(output_dir.glob("*.md")):
        print(f"     - {f.name}")
    print("\n  ⚠️  4_reviewed_content.md 를 열어 최종 검토해주세요!")
    print("=" * 60 + "\n")

    log("파이프라인 완료 ✅", log_path)
    log(f"최종 검토 필요: {reviewed_path}", log_path)


if __name__ == "__main__":
    run_pipeline()
