"""미래이력서 생성 스크립트 — Phase 3 데이터 → 이력서형 MD + HTML 출력."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_data(name: str, data_dir: Path) -> tuple[dict, dict, dict]:
    """Phase 1, 2, 3 중간 산출물 로드."""
    ext = json.loads((data_dir / f"{name}_1_extracted.json").read_text("utf-8"))
    prof = json.loads((data_dir / f"{name}_2_profile.json").read_text("utf-8"))
    content = json.loads((data_dir / f"{name}_3_content.json").read_text("utf-8"))
    return ext, prof, content


def render_md(ext: dict, prof: dict, content: dict) -> str:
    """이력서 스타일 Markdown 생성."""
    pi = ext["personal_info"]
    bi = ext["bootcamp_info"]
    sections = sorted(content["sections"], key=lambda s: s["order"])

    # ── 하드스킬 / 소프트스킬 추출 ──
    hard_skills_existing = prof.get("existing_competencies", [])
    soft_skills = prof.get("soft_skills", [])
    hard_skills_projected = prof.get("projected_competencies", [])

    lines: list[str] = []

    # 헤더
    lines.append(f"# {pi['name']}")
    lines.append("")
    contact = []
    if pi.get("email"):
        contact.append(pi["email"])
    if pi.get("phone"):
        phone = str(pi["phone"])
        if len(phone) == 10:
            phone = f"010-{phone[1:5]}-{phone[5:]}"
        elif len(phone) == 11:
            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        contact.append(phone)
    if contact:
        lines.append(" | ".join(contact))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(content.get("career_objective", ""))
    lines.append("")

    # Skills
    lines.append("---")
    lines.append("")
    lines.append("## Skills")
    lines.append("")

    if hard_skills_existing:
        lines.append("### 보유 역량")
        lines.append("")
        for sk in hard_skills_existing:
            lines.append(f"- {sk}")
        lines.append("")

    if hard_skills_projected:
        lines.append("### 수료 후 습득 예상 역량")
        lines.append("")
        for sk in hard_skills_projected:
            lines.append(f"- {sk}")
        lines.append("")

    if soft_skills:
        lines.append("### Soft Skills")
        lines.append("")
        for sk in soft_skills:
            lines.append(f"- {sk}")
        lines.append("")

    # 본문 섹션 (career_objective 제외)
    for sec in sections:
        if sec["section_id"] == "career_objective":
            continue
        title = sec["title"]
        if sec.get("is_projected"):
            title += " *(수료 후 예상)*"
        lines.append("---")
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")
        lines.append(sec["content"])
        lines.append("")

    # 부트캠프 하이라이트
    if content.get("bootcamp_highlight"):
        lines.append("---")
        lines.append("")
        lines.append(f"> {content['bootcamp_highlight']}")
        lines.append("")

    # 푸터
    lines.append("---")
    lines.append("")
    lines.append(
        f"*본 이력서는 {bi.get('bootcamp_name', '부트캠프')} 수료 후 "
        f"예상 역량을 기반으로 작성되었습니다.*"
    )
    lines.append("*Edited by Likelion*")
    lines.append("")

    return "\n".join(lines)


def render_html(ext: dict, prof: dict, content: dict) -> str:
    """이력서 스타일 HTML 생성 — 브라우저에서 바로 열 수 있는 단일 파일."""
    pi = ext["personal_info"]
    bi = ext["bootcamp_info"]
    sections = sorted(content["sections"], key=lambda s: s["order"])

    hard_existing = prof.get("existing_competencies", [])
    soft_skills = prof.get("soft_skills", [])
    hard_projected = prof.get("projected_competencies", [])
    applicant_type = prof.get("applicant_type", "student")

    # 전화번호 포맷
    phone = str(pi.get("phone", ""))
    if len(phone) == 10:
        phone = f"010-{phone[1:5]}-{phone[5:]}"
    elif len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    # 유형 한글
    type_label = {"student": "학생/졸업예정", "experienced": "IT 경력자", "career_changer": "전직자"}.get(applicant_type, applicant_type)

    # ── 섹션 HTML 생성 ──
    def md_to_html(text: str) -> str:
        """간단한 마크다운 → HTML 변환."""
        import re
        if not text:
            return ""
        result_lines = []
        in_ul = False
        in_table = False
        table_rows = []

        for line in text.split("\n"):
            stripped = line.strip()

            # 테이블 처리
            if stripped.startswith("|") and stripped.endswith("|"):
                if not in_table:
                    in_table = True
                    table_rows = []
                # 구분선 행 스킵
                if all(c in "|-: " for c in stripped):
                    continue
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                table_rows.append(cells)
                continue
            elif in_table:
                # 테이블 종료
                result_lines.append('<table>')
                for i, row in enumerate(table_rows):
                    tag = "th" if i == 0 else "td"
                    result_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in row) + "</tr>")
                result_lines.append("</table>")
                in_table = False
                table_rows = []

            if stripped.startswith("- ") or stripped.startswith("* "):
                if not in_ul:
                    result_lines.append("<ul>")
                    in_ul = True
                item = stripped[2:].strip()
                item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
                item = re.sub(r"\*(.+?)\*", r"<em>\1</em>", item)
                result_lines.append(f"<li>{item}</li>")
            else:
                if in_ul:
                    result_lines.append("</ul>")
                    in_ul = False
                if stripped.startswith("####"):
                    result_lines.append(f"<h4>{stripped[4:].strip()}</h4>")
                elif stripped.startswith("###"):
                    result_lines.append(f"<h3>{stripped[3:].strip()}</h3>")
                elif stripped.startswith("> "):
                    inner = stripped[2:]
                    inner = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", inner)
                    result_lines.append(f'<blockquote>{inner}</blockquote>')
                elif stripped:
                    formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
                    formatted = re.sub(r"\*(.+?)\*", r"<em>\1</em>", formatted)
                    result_lines.append(f"<p>{formatted}</p>")

        if in_ul:
            result_lines.append("</ul>")
        if in_table:
            result_lines.append('<table>')
            for i, row in enumerate(table_rows):
                tag = "th" if i == 0 else "td"
                result_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in row) + "</tr>")
            result_lines.append("</table>")

        return "\n".join(result_lines)

    sections_html = []
    for sec in sections:
        if sec["section_id"] == "career_objective":
            continue
        projected_badge = ' <span class="badge">수료 후 예상</span>' if sec.get("is_projected") else ""
        sections_html.append(f"""
        <section>
            <h2>{sec['title']}{projected_badge}</h2>
            {md_to_html(sec['content'])}
        </section>""")

    # ── 스킬 태그 ──
    def skill_tags(skills: list[str], cls: str) -> str:
        return "".join(f'<span class="skill-tag {cls}">{s}</span>' for s in skills)

    skills_section = ""
    if hard_existing:
        skills_section += f"""
            <div class="skill-group">
                <h3>보유 역량</h3>
                <div class="skill-tags">{skill_tags(hard_existing, "existing")}</div>
            </div>"""
    if hard_projected:
        skills_section += f"""
            <div class="skill-group">
                <h3>수료 후 습득 예상</h3>
                <div class="skill-tags">{skill_tags(hard_projected, "projected")}</div>
            </div>"""
    if soft_skills:
        skills_section += f"""
            <div class="skill-group">
                <h3>Soft Skills</h3>
                <div class="skill-tags">{skill_tags(soft_skills, "soft")}</div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{pi['name']} — 미래이력서 | Likelion</title>
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #1a1a1a;
    background: #f0f0f0;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}}

.resume {{
    max-width: 800px;
    margin: 40px auto;
    background: #fff;
    box-shadow: 0 2px 20px rgba(0,0,0,0.08);
    border-radius: 4px;
    overflow: hidden;
}}

/* ── Header ── */
.header {{
    background: linear-gradient(135deg, #FF7816 0%, #e06510 100%);
    color: #fff;
    padding: 48px 56px 40px;
    position: relative;
}}
.header::after {{
    content: 'FUTURE RESUME';
    position: absolute;
    top: 16px;
    right: 24px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    opacity: 0.5;
}}
.header h1 {{
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}}
.header .headline {{
    font-size: 16px;
    font-weight: 400;
    opacity: 0.9;
    margin-bottom: 16px;
    line-height: 1.5;
}}
.header .contact {{
    font-size: 14px;
    opacity: 0.85;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}}
.header .contact span::before {{
    margin-right: 4px;
}}
.type-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
}}
.bootcamp-badge {{
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    padding: 12px 20px;
    margin-top: 20px;
    font-size: 14px;
    font-weight: 500;
}}

/* ── Body ── */
.body {{
    padding: 40px 56px 48px;
}}

/* Summary */
.summary {{
    border-left: 4px solid #FF7816;
    padding: 20px 24px;
    background: #fef7f2;
    border-radius: 0 8px 8px 0;
    margin-bottom: 36px;
    font-size: 15px;
    line-height: 1.8;
    color: #333;
}}

/* Skills */
.skills-section {{
    margin-bottom: 36px;
}}
.skills-section > h2 {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    padding-bottom: 10px;
    border-bottom: 2px solid #FF7816;
    margin-bottom: 20px;
}}
.skill-group {{
    margin-bottom: 16px;
}}
.skill-group h3 {{
    font-size: 14px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}}
.skill-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}
.skill-tag {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}}
.skill-tag.existing {{
    background: #FF7816;
    color: #fff;
}}
.skill-tag.projected {{
    background: #fff3eb;
    color: #d45a00;
    border: 1px solid #ffd4b3;
}}
.skill-tag.soft {{
    background: #f0f0f0;
    color: #555;
}}

/* Sections */
section {{
    margin-bottom: 32px;
}}
section h2 {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    padding-bottom: 10px;
    border-bottom: 2px solid #FF7816;
    margin-bottom: 16px;
}}
section h3 {{
    font-size: 16px;
    font-weight: 700;
    color: #333;
    margin: 16px 0 8px;
}}
section h4 {{
    font-size: 14px;
    font-weight: 600;
    color: #555;
    margin: 12px 0 6px;
}}
section p {{
    font-size: 14.5px;
    color: #444;
    margin-bottom: 8px;
    line-height: 1.8;
}}
section ul {{
    margin: 8px 0 12px 20px;
    font-size: 14.5px;
    color: #444;
}}
section li {{
    margin-bottom: 6px;
    line-height: 1.7;
}}
section table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 13.5px;
}}
section th {{
    background: #f8f8f8;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #ddd;
}}
section td {{
    padding: 10px 14px;
    border-bottom: 1px solid #eee;
    color: #444;
    vertical-align: top;
}}
section blockquote {{
    border-left: 3px solid #FF7816;
    padding: 12px 16px;
    background: #fef7f2;
    border-radius: 0 6px 6px 0;
    margin: 12px 0;
    font-size: 14px;
    color: #555;
}}
.badge {{
    display: inline-block;
    background: #fff3eb;
    color: #d45a00;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    margin-left: 8px;
    vertical-align: middle;
}}

/* ── Footer ── */
.footer {{
    background: #fafafa;
    border-top: 1px solid #eee;
    padding: 24px 56px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #999;
}}
.footer .likelion {{
    font-weight: 700;
    color: #FF7816;
}}

@media print {{
    body {{ background: #fff; }}
    .resume {{ box-shadow: none; margin: 0; border-radius: 0; }}
    .header {{ padding: 32px 40px; }}
    .body {{ padding: 24px 40px; }}
    .footer {{ padding: 16px 40px; }}
}}
</style>
</head>
<body>
<div class="resume">
    <div class="header">
        <div class="type-badge">{type_label}</div>
        <h1>{pi['name']}</h1>
        <div class="headline">{content.get('headline', '')}</div>
        <div class="contact">
            <span>{pi.get('email', '')}</span>
            <span>{phone}</span>
        </div>
        <div class="bootcamp-badge">
            {bi.get('bootcamp_name', '')} &mdash; {bi.get('track', '')} ({bi.get('duration', '')})
        </div>
    </div>

    <div class="body">
        <div class="summary">
            {content.get('career_objective', '')}
        </div>

        <div class="skills-section">
            <h2>Skills</h2>
            {skills_section}
        </div>

        {"".join(sections_html)}
    </div>

    <div class="footer">
        <div>본 이력서는 {bi.get('bootcamp_name', '부트캠프')} 수료 후 예상 역량을 기반으로 작성되었습니다.</div>
        <div>Edited by <span class="likelion">Likelion</span></div>
    </div>
</div>
</body>
</html>"""

    return html


def generate_guide() -> str:
    """미래이력서 활용 가이드."""
    return """\
=====================================
  미래이력서 활용 가이드
  Edited by Likelion
=====================================

안녕하세요!
이 문서는 부트캠프 수료 후 작성 가능한 이력서를
미리 확인할 수 있도록 Likelion이 준비한 자료입니다.

함께 제공된 파일은 두 종류입니다:
  1. .md 파일  — 텍스트 기반 이력서 (편집용)
  2. .html 파일 — 브라우저에서 바로 열어보는 이력서 (열람용)


[이렇게 사용해보세요]
-------------------------------------

1. HTML 파일로 내 미래이력서 확인하기
   - .html 파일을 더블클릭하면 브라우저에서 바로 열립니다.
   - 디자인이 적용된 상태로 내 미래 역량을 한눈에 볼 수 있습니다.

2. MD 파일로 직접 편집하기
   - .md 파일을 메모장, VS Code 등으로 열어 자유롭게 수정할 수 있습니다.
   - Notion에 복사·붙여넣기하면 서식이 자동 적용됩니다.

3. 수료 후 실제 이력서로 전환하기
   - "(수료 후 예상)" 표시된 항목을 실제 경험으로 교체하세요.
   - 프로젝트 결과물, 성과 지표를 추가하면 더 강력해집니다.
   - Skills 섹션에 실제 사용 경험과 숙련도를 업데이트하세요.


[내 이력서에 들어간 핵심 요소]
-------------------------------------

- Summary     : 나의 커리어 방향과 핵심 가치를 한 문단으로
- Skills      : 보유 역량 + 수료 후 습득 예상 역량 + 소프트스킬
- Education   : 학력 + 부트캠프 교육 이력
- Projects    : 부트캠프 프로젝트 포트폴리오 (수료 후 예상)
- Experience  : 기존 경력 또는 활동 이력


[MD 파일 활용법]
-------------------------------------

방법 1 — Notion에 붙여넣기
   .md 파일 전체 복사(Ctrl+A → Ctrl+C) 후
   Notion 페이지에 붙여넣기하면 서식 자동 적용

방법 2 — GitHub 포트폴리오
   GitHub 저장소에 업로드하면 자동 렌더링
   README.md로 활용하면 포트폴리오 홈 역할

방법 3 — VS Code 미리보기
   VS Code에서 Ctrl+Shift+V로 실시간 미리보기

방법 4 — PDF 변환
   온라인 도구(dillinger.io 등)에서 PDF/HTML 변환 가능


[주의사항]
-------------------------------------

- 본 이력서는 수료 전 예상 역량 기반입니다.
- 실제 취업 지원 시 수료 후 경험으로 업데이트하세요.
- 개인정보(이메일, 연락처) 포함 — 공유 시 주의하세요.


-------------------------------------
Likelion | 멋쟁이사자처럼
=====================================
"""


def main():
    data_dir = Path("outputs/2026-05-11/intermediate")
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(f"outputs/{today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    names = ["김지수", "변재우"]

    for name in names:
        print(f"\n{'='*50}")
        print(f" {name} 미래이력서 생성")
        print(f"{'='*50}")

        ext, prof, content = load_data(name, data_dir)

        # MD 생성
        md = render_md(ext, prof, content)
        md_path = output_dir / f"{name}_미래이력서.md"
        md_path.write_text(md, encoding="utf-8")
        print(f"  MD:   {md_path} ({md_path.stat().st_size:,} bytes)")

        # HTML 생성
        html = render_html(ext, prof, content)
        html_path = output_dir / f"{name}_미래이력서.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"  HTML: {html_path} ({html_path.stat().st_size:,} bytes)")

    # 활용 가이드
    guide = generate_guide()
    guide_path = output_dir / "미래이력서_활용가이드.txt"
    guide_path.write_text(guide, encoding="utf-8")
    print(f"\n  가이드: {guide_path}")

    print(f"\n{'='*50}")
    print(f"완료! 출력: {output_dir}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
