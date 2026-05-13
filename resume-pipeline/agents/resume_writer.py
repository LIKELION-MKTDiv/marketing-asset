"""Phase 3: 역량 이력서 콘텐츠 생성 (Opus + extended thinking)."""
from __future__ import annotations

from pathlib import Path

from utils.llm import call_opus_streaming, parse_json_response
from utils.schema import (
    ApplicantProfile,
    ExtractedData,
    ResumeContent,
    ResumeSection,
)

SYSTEM_PROMPT = """\
당신은 IT 취업 전문 이력서 작성 컨설턴트입니다.
KDT 부트캠프 지원자의 배경 + 부트캠프 교육 정보를 결합하여
"수료 후 작성 가능한 역량 이력서(경력기술서)" 콘텐츠를 생성합니다.

## 핵심 원칙
1. 지원자의 실제 배경(자기소개서 기반)은 사실 그대로 반영
2. 부트캠프 수료 후 예상 역량은 커리큘럼/프로젝트 기반으로 현실적 수준 작성
3. 예상 항목에는 반드시 "(수료 후 예상)" 또는 "(예정)" 접미사 포함
4. 유형별 커리어 내러티브 톤:
   - career_changer: 기존 산업 경험의 가치를 기술 전환 관점으로 재해석
   - student: 빠른 학습력과 프로젝트 경험 강조
   - experienced: 기존 기술 역량 심화 + 새로운 스택 확장
5. 한국어로 작성, 전문적이지만 자연스러운 어투
6. 각 섹션은 이력서에 직접 삽입 가능한 완성된 문장/목록

## 출력 JSON 구조
- headline: 이름 아래 한줄 소개 (예: "3년차 마케터 출신 백엔드 개발자")
- career_objective: 커리어 목표 (3-4문장)
- bootcamp_highlight: 부트캠프 수료 하이라이트 1문장
- template_type: 사용할 템플릿 타입 (career_changer/student/experienced)
- sections: 배열, 각 항목:
  - section_id: 고유 ID
  - title: 섹션 표시 제목 (한글)
  - content: 섹션 본문 (마크다운 허용)
  - order: 표시 순서 (1부터)
  - is_projected: 수료 후 예상 항목이면 true
"""

USER_PROMPT_TEMPLATE = """\
## 지원자 프로필
- 이름: {name}
- 유형: {applicant_type} ({type_rationale})
- 커리어 서사 방향: {career_narrative}

## 기존 역량
- 보유 역량: {existing_competencies}
- 소프트스킬: {soft_skills}
- 학력: {education_summary}
- 경력: {experience_summary}

## 부트캠프 수료 후 예상 역량
- 습득 예상: {projected_competencies}
- 시너지 포인트: {synergy_points}

## 부트캠프 정보
- 부트캠프명: {bootcamp_name}
- 트랙: {track}
- 기간: {duration}
- 커리큘럼: {curriculum}
- 프로젝트: {projects}
- 기술스택: {tech_stack}
- 인턴십: {internship}
- 취업연계: {partnerships}
- 혜택: {benefits}
- 운영방식: {operation}
- 강사진: {instructors}

## 포함할 섹션
{recommended_sections}

## 자기소개서 원문 발췌
{essays_raw}

위 정보를 기반으로 역량 이력서 콘텐츠를 JSON으로 생성하세요.
"""


def run(
    extracted: ExtractedData,
    profile: ApplicantProfile,
    log_path: Path | None = None,
) -> ResumeContent:
    bi = extracted.bootcamp_info
    pi = extracted.personal_info

    essays_raw = "\n\n".join(
        f"Q: {seg.question}\nA: {seg.answer[:500]}"
        for seg in extracted.essays
    ) or "자기소개서 데이터 없음"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=pi.name,
        applicant_type=profile.applicant_type,
        type_rationale=profile.type_rationale,
        career_narrative=profile.career_narrative,
        existing_competencies=", ".join(profile.existing_competencies) or "없음",
        soft_skills=", ".join(profile.soft_skills) or "없음",
        education_summary=profile.education_summary or "정보 없음",
        experience_summary=profile.experience_summary or "정보 없음",
        projected_competencies=", ".join(profile.projected_competencies) or "미정",
        synergy_points=", ".join(profile.synergy_points) or "없음",
        bootcamp_name=bi.bootcamp_name,
        track=bi.track or "미정",
        duration=bi.duration or "미정",
        curriculum=", ".join(bi.curriculum) if bi.curriculum else "정보 없음",
        projects=", ".join(bi.projects) if bi.projects else "정보 없음",
        tech_stack=", ".join(bi.tech_stack) if bi.tech_stack else "정보 없음",
        internship=bi.internship_info or "정보 없음",
        partnerships=", ".join(bi.partnerships) if bi.partnerships else "정보 없음",
        benefits=", ".join(bi.benefits) if bi.benefits else "정보 없음",
        operation=bi.operation_method or "정보 없음",
        instructors=", ".join(bi.instructors) if bi.instructors else "정보 없음",
        recommended_sections=", ".join(profile.recommended_sections) or "기본 섹션",
        essays_raw=essays_raw,
    )

    print(f"  [Phase 3] {pi.name} 이력서 콘텐츠 생성 중 (Opus)...")
    raw_response = call_opus_streaming(SYSTEM_PROMPT, user_prompt, log_path)
    parsed = parse_json_response(raw_response)

    if not parsed or not isinstance(parsed, dict):
        return _fallback_content(extracted, profile)

    sections: list[ResumeSection] = []
    for item in parsed.get("sections", []):
        sections.append(
            ResumeSection(
                section_id=item.get("section_id", "unknown"),
                title=item.get("title", ""),
                content=item.get("content", ""),
                order=item.get("order", 0),
                is_projected=item.get("is_projected", False),
            )
        )

    return ResumeContent(
        headline=parsed.get("headline", ""),
        career_objective=parsed.get("career_objective", ""),
        sections=sorted(sections, key=lambda s: s.order),
        bootcamp_highlight=parsed.get("bootcamp_highlight", ""),
        template_type=parsed.get("template_type", profile.applicant_type),
    )


def _fallback_content(
    extracted: ExtractedData,
    profile: ApplicantProfile,
) -> ResumeContent:
    bi = extracted.bootcamp_info
    sections = [
        ResumeSection(
            section_id="career_objective",
            title="커리어 목표",
            content=profile.career_narrative or "IT 분야 전문가로 성장",
            order=1,
        ),
        ResumeSection(
            section_id="bootcamp_training",
            title=f"{bi.bootcamp_name} 교육 이수 (예정)",
            content=f"- 기간: {bi.duration}\n- 트랙: {bi.track}",
            order=2,
            is_projected=True,
        ),
    ]

    if profile.existing_competencies:
        sections.append(
            ResumeSection(
                section_id="existing_competencies",
                title="보유 역량",
                content="\n".join(f"- {c}" for c in profile.existing_competencies),
                order=3,
            )
        )

    return ResumeContent(
        headline=f"{bi.track} 개발자 지망",
        career_objective=profile.career_narrative,
        sections=sections,
        bootcamp_highlight=f"{bi.bootcamp_name} 수료 예정",
        template_type=profile.applicant_type,
    )
