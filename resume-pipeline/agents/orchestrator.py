"""5-Phase 파이프라인 오케스트레이터."""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from config import OUTPUTS_DIR
from utils.schema import to_json

from agents import extractor, profiler, resume_writer
from generate_future_resume import render_md, render_html


def run_single(
    bootcamp_raw: dict[str, Any],
    applicant_raw: dict[str, Any],
    personal_info_mapping: dict[str, str | None],
    essay_columns: list[str],
    output_dir: Path,
    log_lines: list[str],
) -> dict[str, Any]:
    """단일 지원자에 대해 파이프라인 실행 → 미래이력서(MD+HTML) 생성."""
    t0 = time.time()
    intermediate_dir = output_dir / "intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1: 구조화 추출
    _log(log_lines, "Phase 1: 구조화 추출 시작")
    extracted = extractor.run(
        bootcamp_raw, applicant_raw, personal_info_mapping, essay_columns
    )
    name = extracted.personal_info.name
    _save_intermediate(intermediate_dir / f"{name}_1_extracted.json", extracted.to_dict())
    _log(log_lines, f"Phase 1 완료: {name} (notes: {extracted.extraction_notes})")

    # Phase 2: 프로파일링
    _log(log_lines, f"Phase 2: {name} 프로파일링 시작")
    profile = profiler.run(extracted)
    _save_intermediate(intermediate_dir / f"{name}_2_profile.json", profile.to_dict())
    _log(log_lines, f"Phase 2 완료: 유형={profile.applicant_type} (확신도={profile.type_confidence:.2f})")

    # Phase 3: 이력서 콘텐츠 생성
    _log(log_lines, f"Phase 3: {name} 이력서 콘텐츠 생성 시작 (Opus)")
    log_path = output_dir / "pipeline.log"
    resume_content = resume_writer.run(extracted, profile, log_path)
    _save_intermediate(intermediate_dir / f"{name}_3_content.json", resume_content.to_dict())
    _log(log_lines, f"Phase 3 완료: {len(resume_content.sections)}개 섹션 생성")

    # Phase 4: 미래이력서 MD + HTML 생성
    _log(log_lines, f"Phase 4: {name} 미래이력서 렌더링 시작")
    ext_dict = extracted.to_dict()
    prof_dict = profile.to_dict()
    content_dict = resume_content.to_dict()

    md_text = render_md(ext_dict, prof_dict, content_dict)
    md_path = output_dir / f"{name}_미래이력서.md"
    md_path.write_text(md_text, encoding="utf-8")

    html_text = render_html(ext_dict, prof_dict, content_dict)
    html_path = output_dir / f"{name}_미래이력서.html"
    html_path.write_text(html_text, encoding="utf-8")

    _log(log_lines, f"Phase 4 완료: {md_path.name} + {html_path.name}")

    elapsed = time.time() - t0
    _log(log_lines, f"{name} 전체 완료 ({elapsed:.1f}초)")

    return {
        "name": name,
        "applicant_type": profile.applicant_type,
        "md_path": str(md_path),
        "html_path": str(html_path),
        "sections_count": len(resume_content.sections),
        "elapsed_seconds": round(elapsed, 1),
        "success": True,
    }


def _find_already_generated(output_base: Path) -> set[str]:
    """outputs/ 하위 전체 날짜 디렉토리를 스캔하여 이미 미래이력서가 생성된 이름 목록 반환."""
    generated: set[str] = set()
    if not output_base.exists():
        return generated
    for date_dir in output_base.iterdir():
        if not date_dir.is_dir():
            continue
        for f in date_dir.iterdir():
            if f.is_file() and (
                f.name.endswith("_미래이력서.md")
                or f.name.endswith("_미래이력서.html")
            ):
                name = f.name.rsplit("_", 1)[0]
                generated.add(name)
    return generated


def run_batch(
    bootcamp_raw: dict[str, Any],
    applicants: list[dict[str, Any]],
    personal_info_mapping: dict[str, str | None],
    essay_columns: list[str],
    output_base: Path | None = None,
) -> Path:
    """배치 처리: 전체 지원자에 대해 파이프라인 실행."""
    run_date = datetime.now().strftime("%Y-%m-%d")
    base = output_base or OUTPUTS_DIR
    output_dir = base / run_date
    output_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []
    _log(log_lines, f"=== 배치 시작: {len(applicants)}명 ===")
    _log(log_lines, f"출력 디렉토리: {output_dir}")

    # 중복 생성 방지: 이미 생성된 이름 스캔
    already_generated = _find_already_generated(base)
    if already_generated:
        _log(log_lines, f"이미 생성 완료된 이력서: {len(already_generated)}명 — {', '.join(sorted(already_generated))}")

    results: list[dict[str, Any]] = []
    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, applicant_raw in enumerate(applicants, 1):
        # 이름 추출 후 중복 체크
        name_col = personal_info_mapping.get("name")
        applicant_name = None
        if name_col and name_col in applicant_raw:
            applicant_name = str(applicant_raw[name_col]).strip()

        if applicant_name and applicant_name in already_generated:
            _log(log_lines, f"[SKIP] {applicant_name} — 이미 생성된 이력서 존재")
            print(f"\n[{i}/{len(applicants)}] {applicant_name} — 스킵 (이미 생성됨)")
            results.append({
                "name": applicant_name,
                "success": True,
                "skipped": True,
            })
            skip_count += 1
            continue

        print(f"\n{'='*60}")
        print(f"[{i}/{len(applicants)}] 처리 중...")
        print(f"{'='*60}")

        try:
            result = run_single(
                bootcamp_raw, applicant_raw,
                personal_info_mapping, essay_columns,
                output_dir, log_lines,
            )
            results.append(result)
            success_count += 1
            print(f"  -> 완료: {result['name']} ({result['elapsed_seconds']}초)")

        except Exception as e:
            name = applicant_name or "알 수 없음"

            error_msg = f"{name}: {type(e).__name__}: {e}"
            _log(log_lines, f"[ERROR] {error_msg}")
            print(f"  -> 실패: {error_msg}", file=sys.stderr)

            results.append({
                "name": name,
                "success": False,
                "error": str(e),
            })
            fail_count += 1

    # 배치 요약
    summary = {
        "run_date": run_date,
        "total": len(applicants),
        "success": success_count,
        "skipped": skip_count,
        "failed": fail_count,
        "results": results,
    }
    summary_path = output_dir / "batch_summary.json"
    _save_intermediate(summary_path, summary)

    # 로그 저장
    log_path = output_dir / "pipeline.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    # 활용법 가이드 생성
    if success_count > 0:
        from generate_future_resume import generate_guide
        guide = generate_guide()
        guide_path = output_dir / "미래이력서_활용가이드.txt"
        guide_path.write_text(guide, encoding="utf-8")
        _log(log_lines, "활용법 가이드 생성 완료: 미래이력서_활용가이드.txt")

    _log(log_lines, f"=== 배치 완료: 성공 {success_count} / 스킵 {skip_count} / 실패 {fail_count} ===")
    print(f"\n{'='*60}")
    print(f"배치 완료: 성공 {success_count}건, 스킵(중복) {skip_count}건, 실패 {fail_count}건")
    print(f"출력: {output_dir}")
    print(f"{'='*60}")

    return output_dir


def _log(lines: list[str], msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    lines.append(entry)
    print(f"  {entry}")


def _generate_usage_guide(output_dir: Path) -> None:
    """역량이력서 MD 파일 활용법 가이드 TXT 생성."""
    guide = """\
=====================================
  역량 이력서(MD) 활용 가이드
  Edited by Likelion
=====================================

안녕하세요!
본 파일은 부트캠프 수료 후 작성 가능한 역량 이력서를
미리 확인할 수 있도록 Likelion이 준비한 자료입니다.

함께 제공된 .md(마크다운) 파일이 여러분의 역량 이력서입니다.


[이렇게 사용해보세요]
-------------------------------------

1. 내 역량 이력서 확인하기
   - 본인 이름이 포함된 .md 파일을 찾아 열어보세요.
   - 메모장, VS Code 등 텍스트 에디터로 열 수 있습니다.
   - GitHub, Notion에 붙여넣으면 서식이 자동 적용됩니다.

2. 수료 후 달라질 나의 모습 파악하기
   - "(수료 후 예상)" 표시가 된 항목은 부트캠프 교육과정을
     성실히 이수했을 때 갖출 수 있는 역량입니다.
   - 현재 보유 역량과 비교하며 성장 로드맵을 그려보세요.

3. 실제 취업 이력서에 활용하기
   - 수료 후, 이 문서를 기반으로 실제 이력서를 작성할 수 있습니다.
   - "(수료 후 예상)" 항목을 실제 경험으로 교체하면 완성됩니다.
   - 프로젝트 결과물, 성과 지표를 추가하면 더 강력해집니다.


[내 이력서 작성에 MD 파일 이용하는 방법]
-------------------------------------

방법 1 — Notion에 붙여넣기
   .md 파일을 텍스트 에디터로 열고 전체 복사(Ctrl+A → Ctrl+C) 후
   Notion 페이지에 붙여넣기(Ctrl+V) 하면 서식이 자동 적용됩니다.
   이후 Notion에서 자유롭게 편집하세요.

방법 2 — GitHub에 업로드
   GitHub 저장소에 .md 파일을 업로드하면 자동으로 렌더링됩니다.
   포트폴리오 README로 활용하기 좋습니다.

방법 3 — VS Code로 편집
   VS Code에서 .md 파일을 열고 Ctrl+Shift+V를 누르면
   미리보기 화면이 나타납니다. 실시간으로 편집하며 확인하세요.

방법 4 — 한글/Word로 변환
   온라인 마크다운 변환 도구(예: dillinger.io, markdowntohtml.com)에
   내용을 붙여넣으면 HTML이나 PDF로 변환할 수 있습니다.
   그 후 Word 등으로 추가 편집이 가능합니다.


[편집 팁]
-------------------------------------

- ## 으로 시작하는 줄은 섹션 제목입니다.
- **굵은 글씨**는 별표 두 개(**)로 감싸져 있습니다.
- - 으로 시작하는 줄은 목록 항목입니다.
- > 으로 시작하는 줄은 인용/강조 블록입니다.
- 자유롭게 내용을 추가, 수정, 삭제할 수 있습니다.


[주의사항]
-------------------------------------

- 본 이력서는 부트캠프 수료 전 예상 역량 기반으로 작성되었습니다.
- 실제 취업 지원 시에는 수료 후 실제 경험으로 업데이트하세요.
- 개인정보(이메일, 연락처)가 포함되어 있으니 공유 시 주의하세요.


-------------------------------------
Likelion | 멋쟁이사자처럼
문의: 담당 매니저에게 연락해주세요.
=====================================
"""
    guide_path = output_dir / "역량이력서_활용가이드.txt"
    guide_path.write_text(guide, encoding="utf-8")


def _save_intermediate(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
