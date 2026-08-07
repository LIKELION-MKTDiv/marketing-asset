"""V2 렌더 재현 데모.

풀 파이프라인(CSV 추출 → LLM 프로파일링 → LLM 콘텐츠 생성)은 비결정적(LLM)이고
개인 인증(API 키)이 필요해 그대로 재현할 수 없다. 하지만 Phase 4 렌더(render_html/
render_md)는 순수 함수라 "같은 intermediate 입력 → 항상 같은 HTML/MD 출력"이 보장된다.

이 스크립트는 examples/sample_intermediate/ 의 완전 더미 intermediate 2세트
(학생형 1명 + 커리어 전환형 1명, 둘 다 실제 지원자 아님)를 읽어
generate_future_resume.render_html() / render_md() 를 class_id="kdt-backendj-27th"
로 호출한다. 클론 후 이 스크립트 하나만 실행하면 누구나 동일한 샘플 이력서
2세트(HTML+MD 총 4파일)를 examples/output/ 에서 재현할 수 있다.

실행:
    cd resume-pipeline
    python examples/render_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import generate_future_resume as g  # noqa: E402

CLASS_ID = "kdt-backendj-27th"
INTERMEDIATE_DIR = Path(__file__).resolve().parent / "sample_intermediate"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# 더미 지원자 목록 — 학생형(학력 섹션 포함) + 커리어 전환형(학력/배경 섹션 생략 케이스)
SAMPLE_NAMES = ["샘플지원자1", "샘플지원자2"]


def load_intermediate(name: str) -> tuple[dict, dict, dict]:
    ext = json.loads((INTERMEDIATE_DIR / f"{name}_1_extracted.json").read_text(encoding="utf-8"))
    prof = json.loads((INTERMEDIATE_DIR / f"{name}_2_profile.json").read_text(encoding="utf-8"))
    content = json.loads((INTERMEDIATE_DIR / f"{name}_3_content.json").read_text(encoding="utf-8"))
    return ext, prof, content


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[render_demo] class_id={CLASS_ID} — 더미 지원자 {len(SAMPLE_NAMES)}명 렌더 시작\n")

    for name in SAMPLE_NAMES:
        ext, prof, content = load_intermediate(name)

        html_text = g.render_html(ext, prof, content, class_id=CLASS_ID)
        md_text = g.render_md(ext, prof, content, class_id=CLASS_ID)

        html_path = OUTPUT_DIR / f"{name}_미래이력서.html"
        md_path = OUTPUT_DIR / f"{name}_미래이력서.md"
        html_path.write_text(html_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")

        applicant_type = prof.get("applicant_type", "?")
        has_background = "<h2>학력" in html_text or any(
            f"<h2>{t}" in html_text
            for t in ("커리어 전환", "실무 프로젝트 경력", "실무 경력", "개발 학습 및 프로젝트 경험")
        )
        print(f"- {name} ({applicant_type}) → {html_path.relative_to(ROOT)}, {md_path.relative_to(ROOT)}")
        print(f"  배경(학력) 섹션 렌더 여부: {'있음' if has_background else '생략됨 (자소서에 배경 정보 없음)'}")

    print(f"\n[render_demo] 완료 — examples/output/ 에서 결과 확인 (총 {len(SAMPLE_NAMES) * 2}개 파일)")


if __name__ == "__main__":
    main()
