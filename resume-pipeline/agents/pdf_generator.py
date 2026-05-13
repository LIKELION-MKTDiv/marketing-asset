"""Phase 5: Markdown 파일 저장 (순수 함수, LLM 없음)."""
from __future__ import annotations

from pathlib import Path


def run(md_content: str, output_dir: Path, applicant_name: str) -> Path:
    """Markdown 문자열을 .md 파일로 저장."""
    filename = f"{applicant_name}_역량이력서.md"
    output_path = output_dir / filename

    print(f"  [Phase 5] MD 저장: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content, encoding="utf-8")

    return output_path
