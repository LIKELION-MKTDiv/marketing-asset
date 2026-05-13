"""Phase 2: 지원자 유형 분류 + 역량 매핑."""
from __future__ import annotations

from utils.llm import call_sonnet, parse_json_response
from utils.schema import ApplicantProfile, ExtractedData

SYSTEM_PROMPT = """\
당신은 KDT 부트캠프 지원자를 분석하는 HR/교육 전문가입니다.
지원자의 자기소개서 분석 결과와 부트캠프 정보를 기반으로 프로파일링합니다.

## 지원자 유형 분류 기준
1. career_changer (전직자): 비IT 업종 경력 보유, IT 분야 전환 목적
2. student (대학생/졸업예정): 재학중 또는 졸업 직후, 정규 직장경력 없음
3. experienced (IT 인접 경력자): IT 관련 경력이 있거나, 개발/디자인/기획 경험 보유

## 출력 항목
- applicant_type: 3가지 중 하나
- type_confidence: 분류 확신도 (0.0~1.0)
- type_rationale: 분류 근거 (1-2문장)
- existing_competencies: 현재 보유 역량 목록
- soft_skills: 소프트스킬 목록
- education_summary: 학력 요약
- experience_summary: 경력 요약
- projected_competencies: 부트캠프 수료 후 습득 예상 역량
- synergy_points: 기존 배경 + 부트캠프 시너지 포인트
- recommended_sections: 이력서에 포함할 섹션 ID 목록
- career_narrative: 이력서 서사 방향 (1-2문장)

반드시 JSON 형식으로만 응답하세요.
"""

USER_PROMPT_TEMPLATE = """\
## 지원자 정보
이름: {name}

## 자기소개서 분석 결과
{essays_summary}

## 부트캠프 정보
- 부트캠프명: {bootcamp_name}
- 트랙: {track}
- 기간: {duration}
- 커리큘럼: {curriculum}
- 프로젝트: {projects}
- 기술스택: {tech_stack}
- 인턴십: {internship}
- 취업연계: {partnerships}

## 요청
위 정보를 기반으로 지원자를 프로파일링하고 JSON으로 응답하세요.
recommended_sections에 포함 가능한 ID:
career_objective, existing_experience, education, bootcamp_training,
tech_stack, portfolio_projects, internship, partnerships, instructor_credibility,
career_transition, activities_awards

```json
{{
  "applicant_type": "student|career_changer|experienced",
  "type_confidence": 0.0,
  "type_rationale": "",
  "existing_competencies": [],
  "soft_skills": [],
  "education_summary": "",
  "experience_summary": "",
  "projected_competencies": [],
  "synergy_points": [],
  "recommended_sections": [],
  "career_narrative": ""
}}
```
"""


def run(extracted: ExtractedData) -> ApplicantProfile:
    bi = extracted.bootcamp_info
    pi = extracted.personal_info

    essays_summary = _format_essays(extracted)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=pi.name,
        essays_summary=essays_summary,
        bootcamp_name=bi.bootcamp_name,
        track=bi.track or "미정",
        duration=bi.duration or "미정",
        curriculum=", ".join(bi.curriculum) if bi.curriculum else "정보 없음",
        projects=", ".join(bi.projects) if bi.projects else "정보 없음",
        tech_stack=", ".join(bi.tech_stack) if bi.tech_stack else "정보 없음",
        internship=bi.internship_info or "정보 없음",
        partnerships=", ".join(bi.partnerships) if bi.partnerships else "정보 없음",
    )

    raw_response = call_sonnet(SYSTEM_PROMPT, user_prompt)
    parsed = parse_json_response(raw_response)

    if not parsed or not isinstance(parsed, dict):
        return ApplicantProfile(
            applicant_type="student",
            type_confidence=0.0,
            type_rationale="LLM 응답 파싱 실패 — 기본값 사용",
            career_narrative="부트캠프 수료를 통한 실무 역량 확보",
        )

    return ApplicantProfile(
        applicant_type=parsed.get("applicant_type", "student"),
        type_confidence=float(parsed.get("type_confidence", 0.0)),
        type_rationale=parsed.get("type_rationale", ""),
        existing_competencies=parsed.get("existing_competencies", []),
        soft_skills=parsed.get("soft_skills", []),
        education_summary=parsed.get("education_summary", ""),
        experience_summary=parsed.get("experience_summary", ""),
        projected_competencies=parsed.get("projected_competencies", []),
        synergy_points=parsed.get("synergy_points", []),
        recommended_sections=parsed.get("recommended_sections", []),
        career_narrative=parsed.get("career_narrative", ""),
    )


def _format_essays(extracted: ExtractedData) -> str:
    if not extracted.essays:
        return "자기소개서 데이터 없음"

    parts: list[str] = []
    for i, seg in enumerate(extracted.essays, 1):
        lines = [f"### 질문 {i}: {seg.question}"]
        if seg.extracted_education:
            lines.append(f"- 학력: {seg.extracted_education}")
        if seg.extracted_experience:
            lines.append(f"- 경력/경험: {seg.extracted_experience}")
        if seg.extracted_skills:
            lines.append(f"- 보유 스킬: {', '.join(seg.extracted_skills)}")
        if seg.extracted_motivation:
            lines.append(f"- 지원 동기: {seg.extracted_motivation}")
        if seg.extracted_goals:
            lines.append(f"- 목표: {seg.extracted_goals}")
        if not any([seg.extracted_education, seg.extracted_experience,
                     seg.extracted_skills, seg.extracted_motivation, seg.extracted_goals]):
            lines.append(f"- 원문 답변: {seg.answer[:300]}")
        parts.append("\n".join(lines))

    return "\n\n".join(parts)
