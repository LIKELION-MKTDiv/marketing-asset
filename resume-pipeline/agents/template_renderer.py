"""Phase 4: Markdown 렌더링 (순수 함수, LLM 없음)."""
from __future__ import annotations

from config import BRAND_NAME, BRAND_NAME_EN
from utils.schema import BootcampInfo, PersonalInfo, ResumeContent


def run(
    resume: ResumeContent,
    personal_info: PersonalInfo,
    bootcamp_info: BootcampInfo,
) -> str:
    """ResumeContent → Markdown 문자열 렌더링."""
    lines: list[str] = []

    # ── 헤더 ──
    lines.append(f"# {personal_info.name}")
    if resume.headline:
        lines.append(f"### {resume.headline}")
    lines.append("")

    # 연락처
    contact_parts: list[str] = []
    if personal_info.email:
        contact_parts.append(f"Email: {personal_info.email}")
    if personal_info.phone:
        contact_parts.append(f"Tel: {personal_info.phone}")
    if contact_parts:
        lines.append(" | ".join(contact_parts))
        lines.append("")

    # 구분선
    lines.append("---")
    lines.append("")

    # 부트캠프 뱃지
    if bootcamp_info.bootcamp_name:
        badge = f"> **{bootcamp_info.bootcamp_name}**"
        if bootcamp_info.track:
            badge += f" — {bootcamp_info.track}"
        if bootcamp_info.duration:
            badge += f" ({bootcamp_info.duration})"
        lines.append(badge)
        lines.append("")

    # 커리어 목표
    if resume.career_objective:
        lines.append("## 커리어 목표")
        lines.append("")
        lines.append(resume.career_objective)
        lines.append("")

    # ── 본문 섹션 ──
    for section in sorted(resume.sections, key=lambda s: s.order):
        # 커리어 목표 중복 방지
        if section.section_id == "career_objective":
            continue

        title = section.title
        if section.is_projected:
            title += " *(수료 후 예상)*"

        lines.append(f"## {title}")
        lines.append("")
        lines.append(section.content)
        lines.append("")

    # 부트캠프 하이라이트
    if resume.bootcamp_highlight:
        lines.append("---")
        lines.append("")
        lines.append(f"> {resume.bootcamp_highlight}")
        lines.append("")

    # ── 푸터 ──
    lines.append("---")
    lines.append("")
    lines.append(
        f"*본 이력서는 {bootcamp_info.bootcamp_name or '부트캠프'} 수료 후 "
        f"예상 역량을 기반으로 작성되었습니다.*"
    )
    lines.append(f"*Edited by {BRAND_NAME_EN} ({BRAND_NAME})*")
    lines.append("")

    return "\n".join(lines)
