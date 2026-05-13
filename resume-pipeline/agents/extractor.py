"""Phase 1: 지원서 + 부트캠프 정보 → 구조화 추출."""
from __future__ import annotations

import json
from typing import Any

from utils.llm import call_sonnet, parse_json_response
from utils.schema import (
    BootcampInfo,
    EssaySegment,
    ExtractedData,
    PersonalInfo,
)

SYSTEM_PROMPT = """\
당신은 KDT 부트캠프 지원서 데이터를 분석하는 전문가입니다.
입력된 자기소개서 답변에서 다음 정보를 구조화하여 추출하세요:

1. extracted_education: 학력 정보 (학교, 전공, 학년/졸업여부)
2. extracted_experience: 경력/경험 (직장, 프로젝트, 인턴 등)
3. extracted_skills: 보유 기술/역량 목록 (배열)
4. extracted_motivation: 지원 동기 핵심
5. extracted_goals: 목표/포부 핵심

답변에 해당 정보가 없으면 빈 문자열 또는 빈 배열로 남기세요.
반드시 JSON 형식으로만 응답하세요.
"""

USER_PROMPT_TEMPLATE = """\
아래는 KDT 부트캠프 지원자의 자기소개서 질문-답변 목록입니다.
각 질문-답변 쌍에서 정보를 구조화하여 추출해주세요.

{essays_text}

다음 JSON 형식으로 응답하세요:
```json
[
  {{
    "question": "원래 질문",
    "answer": "원래 답변",
    "extracted_education": "추출된 학력 정보",
    "extracted_experience": "추출된 경력/경험",
    "extracted_skills": ["기술1", "기술2"],
    "extracted_motivation": "지원 동기 핵심",
    "extracted_goals": "목표/포부 핵심"
  }}
]
```
"""


def run(
    bootcamp_raw: dict[str, Any],
    applicant_raw: dict[str, Any],
    personal_info_mapping: dict[str, str | None],
    essay_columns: list[str],
) -> ExtractedData:
    personal_info = _extract_personal_info(applicant_raw, personal_info_mapping)
    bootcamp_info = _build_bootcamp_info(bootcamp_raw)
    essays = _extract_essays(applicant_raw, essay_columns)

    notes: list[str] = []
    if not bootcamp_info.available_fields:
        notes.append("부트캠프 정보가 비어있습니다.")
    if not essays:
        notes.append("자기소개서 답변이 감지되지 않았습니다.")

    return ExtractedData(
        personal_info=personal_info,
        bootcamp_info=bootcamp_info,
        essays=essays,
        extraction_notes=notes,
        raw_application=applicant_raw,
    )


def _extract_personal_info(
    row: dict[str, Any],
    mapping: dict[str, str | None],
) -> PersonalInfo:
    name = ""
    email = ""
    phone = ""

    if mapping.get("name") and mapping["name"] in row:
        name = str(row[mapping["name"]])
    if mapping.get("email") and mapping["email"] in row:
        email = str(row[mapping["email"]])
    if mapping.get("phone") and mapping["phone"] in row:
        phone = str(row[mapping["phone"]])

    if not name:
        for key, val in row.items():
            key_str = str(key).lower()
            if any(kw in key_str for kw in ["이름", "성명", "name"]):
                name = str(val)
                break

    return PersonalInfo(name=name or "이름없음", email=email, phone=phone)


def _build_bootcamp_info(raw: dict[str, Any]) -> BootcampInfo:
    def _get_str(key: str) -> str:
        val = raw.get(key, "")
        return str(val).strip() if val else ""

    def _get_list(key: str) -> list[str]:
        val = raw.get(key, "")
        if isinstance(val, list):
            return val
        if not val or str(val).strip() == "":
            return []
        text = str(val)
        if "\n" in text:
            return [line.strip() for line in text.split("\n") if line.strip()]
        if "," in text:
            return [item.strip() for item in text.split(",") if item.strip()]
        return [text.strip()]

    field_map = {
        "bootcamp_name": ["부트캠프명", "과정명", "프로그램명", "bootcamp_name", "과정"],
        "track": ["트랙", "분야", "track"],
        "duration": ["기간", "교육기간", "duration"],
        "curriculum": ["커리큘럼", "교육내용", "curriculum"],
        "projects": ["프로젝트", "projects"],
        "internship_info": ["인턴십", "현장실습", "internship"],
        "partnerships": ["취업연계", "파트너사", "기업연계", "partnerships"],
        "benefits": ["혜택", "지원사항", "benefits"],
        "operation_method": ["운영방식", "운영", "operation"],
        "instructors": ["강사", "멘토", "instructors"],
        "tech_stack": ["기술스택", "기술", "tech_stack"],
    }

    resolved: dict[str, Any] = {}
    for field_name, candidates in field_map.items():
        for candidate in candidates:
            for raw_key in raw:
                if candidate in str(raw_key).lower().replace(" ", ""):
                    resolved[field_name] = raw[raw_key]
                    break
            if field_name in resolved:
                break

    available: list[str] = []
    for fn in field_map:
        if fn in resolved and resolved[fn]:
            available.append(fn)

    bootcamp_name = _get_str("bootcamp_name") if "bootcamp_name" in resolved else ""
    if not bootcamp_name:
        for key in ["부트캠프명", "과정명", "프로그램명"]:
            if key in raw and raw[key]:
                bootcamp_name = str(raw[key])
                break

    return BootcampInfo(
        bootcamp_name=bootcamp_name or "부트캠프",
        track=str(resolved.get("track", "")).strip(),
        duration=str(resolved.get("duration", "")).strip(),
        curriculum=_get_list("curriculum") if "curriculum" in resolved else [],
        projects=_get_list("projects") if "projects" in resolved else [],
        internship_info=str(resolved.get("internship_info", "")).strip(),
        partnerships=_get_list("partnerships") if "partnerships" in resolved else [],
        benefits=_get_list("benefits") if "benefits" in resolved else [],
        operation_method=str(resolved.get("operation_method", "")).strip(),
        instructors=_get_list("instructors") if "instructors" in resolved else [],
        tech_stack=_get_list("tech_stack") if "tech_stack" in resolved else [],
        available_fields=available,
        raw=raw,
    )


def _extract_essays(
    row: dict[str, Any],
    essay_columns: list[str],
) -> list[EssaySegment]:
    qa_pairs: list[dict[str, str]] = []
    for col in essay_columns:
        if col in row and row[col]:
            qa_pairs.append({"question": col, "answer": str(row[col])})

    if not qa_pairs:
        return []

    essays_text = "\n\n".join(
        f"질문: {qa['question']}\n답변: {qa['answer']}" for qa in qa_pairs
    )
    user_prompt = USER_PROMPT_TEMPLATE.format(essays_text=essays_text)

    raw_response = call_sonnet(SYSTEM_PROMPT, user_prompt)
    parsed = parse_json_response(raw_response)

    if not parsed or not isinstance(parsed, list):
        return [
            EssaySegment(question=qa["question"], answer=qa["answer"])
            for qa in qa_pairs
        ]

    segments: list[EssaySegment] = []
    for item in parsed:
        segments.append(
            EssaySegment(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                extracted_education=item.get("extracted_education", ""),
                extracted_experience=item.get("extracted_experience", ""),
                extracted_skills=item.get("extracted_skills", []),
                extracted_motivation=item.get("extracted_motivation", ""),
                extracted_goals=item.get("extracted_goals", ""),
            )
        )
    return segments
