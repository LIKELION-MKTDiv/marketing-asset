"""멋사 역량 이력서 PDF 생성 파이프라인 — CLI 진입점."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import OUTPUTS_DIR
from utils.data_loader import (
    detect_essay_columns,
    detect_personal_info_columns,
    load_file,
    parse_applications,
    parse_bootcamp_info,
)
from agents.orchestrator import run_batch


def main() -> None:
    parser = argparse.ArgumentParser(
        description="멋사 역량 이력서 PDF 생성 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
사용 예시:
  python main.py --bootcamp bootcamp.csv --applications applicants.csv
  python main.py --bootcamp curriculum.md project.md --applications applicants.xlsx
  python main.py --bootcamp info.txt --applications applicants.csv --output-dir ./my_outputs
        """,
    )
    parser.add_argument(
        "--bootcamp",
        required=True,
        nargs="+",
        help="부트캠프 정보 파일 경로 (CSV/Excel/TXT/MD 지원, 복수 파일 가능)",
    )
    parser.add_argument(
        "--applications",
        required=True,
        help="지원서 데이터 CSV/Excel 파일 경로",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=f"출력 디렉토리 (기본: {OUTPUTS_DIR})",
    )

    args = parser.parse_args()

    bootcamp_paths = [Path(p) for p in args.bootcamp]
    applications_path = Path(args.applications)

    for bp in bootcamp_paths:
        if not bp.exists():
            print(f"[ERROR] 부트캠프 파일을 찾을 수 없습니다: {bp}", file=sys.stderr)
            sys.exit(1)
    if not applications_path.exists():
        print(f"[ERROR] 지원서 파일을 찾을 수 없습니다: {applications_path}", file=sys.stderr)
        sys.exit(1)

    output_base = Path(args.output_dir) if args.output_dir else OUTPUTS_DIR

    # 데이터 로드
    print("데이터 로드 중...")
    bootcamp_input = bootcamp_paths if len(bootcamp_paths) > 1 else bootcamp_paths[0]
    bootcamp_raw = parse_bootcamp_info(bootcamp_input)
    print(f"  부트캠프 정보: {len(bootcamp_raw)}개 필드 로드 ({len(bootcamp_paths)}개 파일)")

    applications_df = load_file(applications_path)
    total_loaded = len(applications_df)

    # 컬럼 감지 (필터링 전에 수행)
    columns = list(applications_df.columns)
    personal_info_mapping = detect_personal_info_columns(columns)
    essay_columns = detect_essay_columns(columns)

    if not essay_columns:
        print("[WARN] 자기소개서 컬럼이 감지되지 않았습니다. 긴 텍스트 컬럼을 자소서로 간주합니다.")
        for col in columns:
            if col not in (personal_info_mapping.values()):
                essay_columns.append(str(col))

    # 지원 완료자 + 자소서 작성자만 필터링
    status_col = None
    for col in columns:
        if "지원상태" in str(col):
            status_col = col
            break

    if status_col:
        before = len(applications_df)
        applications_df = applications_df[
            applications_df[status_col].astype(str).str.strip() == "지원완료"
        ]
        print(f"  지원상태 필터: {before}명 → {len(applications_df)}명 (지원완료만)")

    if essay_columns:
        before = len(applications_df)
        has_essay = applications_df[essay_columns].apply(
            lambda row: any(
                isinstance(v, str) and len(v.strip()) > 10 for v in row
            ),
            axis=1,
        )
        applications_df = applications_df[has_essay]
        print(f"  자소서 필터: {before}명 → {len(applications_df)}명 (자소서 작성자만)")

    applicants = parse_applications(applications_df)
    print(f"  지원자: {total_loaded}명 로드 → {len(applicants)}명 필터 통과")

    print(f"  개인정보 매핑: {personal_info_mapping}")
    print(f"  자소서 컬럼: {len(essay_columns)}개 감지")

    if not applicants:
        print("[ERROR] 필터 통과한 지원자가 없습니다.", file=sys.stderr)
        sys.exit(1)

    # 파이프라인 실행
    run_batch(
        bootcamp_raw=bootcamp_raw,
        applicants=applicants,
        personal_info_mapping=personal_info_mapping,
        essay_columns=essay_columns,
        output_base=output_base,
    )


if __name__ == "__main__":
    main()
