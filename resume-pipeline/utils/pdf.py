"""Playwright 기반 PDF 렌더링 유틸."""
from __future__ import annotations

from pathlib import Path

from config import TEMPLATES_DIR


def render_pdf(html_content: str, output_path: Path) -> Path:
    from playwright.sync_api import sync_playwright

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # CSS/폰트 경로를 절대 경로로 변환
    base_url = TEMPLATES_DIR.as_uri() + "/"
    html_with_base = html_content.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<link rel="stylesheet" href="{base_url}styles.css">',
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_with_base, wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
            print_background=True,
        )
        browser.close()

    return output_path
