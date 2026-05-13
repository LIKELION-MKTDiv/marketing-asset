from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def load_file(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path, engine="openpyxl")

    # CSV: utf-8 우선, 실패 시 cp949 fallback
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


def parse_bootcamp_info(paths: pd.DataFrame | str | Path | list[str | Path]) -> dict[str, Any]:
    """부트캠프 정보를 dict로 변환.

    지원 형식: CSV/Excel (단일행 또는 key-value 2열), TXT, MD.
    TXT/MD는 Sonnet으로 구조화 추출.
    다중 파일(list) 전달 시 텍스트를 병합하여 한 번에 구조화.
    """
    if isinstance(paths, pd.DataFrame):
        return _parse_bootcamp_from_df(paths)

    if isinstance(paths, list):
        return _parse_bootcamp_from_multiple(paths)

    path = Path(paths)
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        return _parse_bootcamp_from_text([path])

    return _parse_bootcamp_from_df(load_file(path))


def _parse_bootcamp_from_df(df: pd.DataFrame) -> dict[str, Any]:
    # key-value 2열 형태 (컬럼 2개: 항목명, 값)
    if len(df.columns) == 2:
        df.columns = ["key", "value"]
        return {
            row["key"]: row["value"]
            for _, row in df.iterrows()
            if pd.notna(row["key"])
        }

    # 단일 행 형태 (컬럼명이 항목명)
    if len(df) >= 1:
        row = df.iloc[0]
        return {
            col: row[col]
            for col in df.columns
            if pd.notna(row[col])
        }

    return {}


def _parse_bootcamp_from_multiple(paths: list[str | Path]) -> dict[str, Any]:
    """다중 파일에서 부트캠프 정보 추출. 텍스트 파일은 병합 후 구조화."""
    text_paths: list[Path] = []
    csv_paths: list[Path] = []

    for p in paths:
        p = Path(p)
        if p.suffix.lower() in (".txt", ".md"):
            text_paths.append(p)
        else:
            csv_paths.append(p)

    if text_paths:
        return _parse_bootcamp_from_text(text_paths)

    if csv_paths:
        return _parse_bootcamp_from_df(load_file(csv_paths[0]))

    return {}


def _parse_bootcamp_from_text(paths: list[Path]) -> dict[str, Any]:
    """TXT/MD 파일(들)을 병합 후 Sonnet으로 구조화 추출."""
    from utils.llm import call_sonnet, parse_json_response

    raw_parts: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="cp949")
        raw_parts.append(f"=== {path.name} ===\n{text}")

    raw_text = "\n\n".join(raw_parts)

    system = """\
당신은 KDT 부트캠프 정보를 구조화하는 전문가입니다.
여러 문서에서 추출한 부트캠프 정보를 통합하여 JSON으로 응답하세요.
해당 정보가 없으면 빈 문자열 또는 빈 배열로 남기세요.

필드 목록:
- 부트캠프명 (bootcamp_name): 과정/프로그램 이름
- 트랙 (track): 분야 (백엔드, 프론트엔드, AI, 클라우드 등)
- 기간 (duration): 교육 기간
- 커리큘럼 (curriculum): 주차별 주요 교육 내용 배열 (각 항목은 "N주차: 내용" 형태)
- 프로젝트 (projects): 프로젝트 목록 배열 (각 항목은 프로젝트명 + 간단 설명)
- 인턴십 (internship_info): 인턴십/현장실습 정보
- 취업연계 (partnerships): 파트너 기업 배열
- 혜택 (benefits): 제공 혜택 배열
- 운영방식 (operation_method): 온/오프라인, 일정 등
- 강사진 (instructors): 강사/TA 약력 배열
- 기술스택 (tech_stack): 교육에서 다루는 기술 배열
- 프로젝트_상세 (projects_detail): 각 프로젝트의 목표, 향상역량, 진행방식을 포함한 상세 배열

반드시 JSON 형식으로만 응답하세요."""

    user = f"아래 부트캠프 정보 문서들을 통합하여 구조화해주세요:\n\n{raw_text[:12000]}"

    response = call_sonnet(system, user, max_tokens=8192)
    parsed = parse_json_response(response)

    if parsed and isinstance(parsed, dict):
        parsed["_raw_text"] = raw_text
        return parsed

    return {"_raw_text": raw_text}


def parse_applications(df_or_path: pd.DataFrame | str | Path) -> list[dict[str, Any]]:
    """지원서 CSV/Excel에서 지원자별 dict 리스트로 변환."""
    if not isinstance(df_or_path, pd.DataFrame):
        df_or_path = load_file(df_or_path)

    df = df_or_path
    applicants: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        record: dict[str, Any] = {}
        for col in df.columns:
            val = row[col]
            if pd.notna(val):
                record[col] = val
        if record:
            applicants.append(record)

    return applicants


def detect_essay_columns(columns: list[str]) -> list[str]:
    """자기소개서 질문 컬럼을 휴리스틱으로 감지."""
    essay_keywords = ["자기소개", "지원동기", "목표", "경험", "역량", "포부", "소개"]
    result = []
    for col in columns:
        col_str = str(col)
        if any(kw in col_str for kw in essay_keywords):
            result.append(col_str)
        elif len(col_str) > 20:
            result.append(col_str)
    return result


def detect_personal_info_columns(
    columns: list[str],
) -> dict[str, str | None]:
    """이름/이메일/전화번호 컬럼을 휴리스틱으로 감지."""
    mapping: dict[str, str | None] = {"name": None, "email": None, "phone": None}

    name_keywords = ["이름", "성명", "name"]
    email_keywords = ["이메일", "email", "메일"]
    phone_keywords = ["전화", "휴대", "연락처", "phone", "mobile"]

    for col in columns:
        col_lower = str(col).lower()
        if not mapping["name"] and any(kw in col_lower for kw in name_keywords):
            mapping["name"] = str(col)
        if not mapping["email"] and any(kw in col_lower for kw in email_keywords):
            mapping["email"] = str(col)
        if not mapping["phone"] and any(kw in col_lower for kw in phone_keywords):
            mapping["phone"] = str(col)

    return mapping
