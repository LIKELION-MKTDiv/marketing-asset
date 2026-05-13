from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ApplicantType = Literal["career_changer", "student", "experienced"]


@dataclass
class PersonalInfo:
    name: str
    email: str = ""
    phone: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BootcampInfo:
    bootcamp_name: str
    track: str = ""
    duration: str = ""
    curriculum: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    internship_info: str = ""
    partnerships: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    operation_method: str = ""
    instructors: list[str] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)
    available_fields: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EssaySegment:
    question: str
    answer: str
    extracted_education: str = ""
    extracted_experience: str = ""
    extracted_skills: list[str] = field(default_factory=list)
    extracted_motivation: str = ""
    extracted_goals: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExtractedData:
    personal_info: PersonalInfo
    bootcamp_info: BootcampInfo
    essays: list[EssaySegment] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)
    raw_application: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ApplicantProfile:
    applicant_type: ApplicantType = "student"
    type_confidence: float = 0.0
    type_rationale: str = ""
    existing_competencies: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    education_summary: str = ""
    experience_summary: str = ""
    projected_competencies: list[str] = field(default_factory=list)
    synergy_points: list[str] = field(default_factory=list)
    recommended_sections: list[str] = field(default_factory=list)
    career_narrative: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResumeSection:
    section_id: str
    title: str
    content: str
    order: int = 0
    is_projected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResumeContent:
    headline: str = ""
    career_objective: str = ""
    sections: list[ResumeSection] = field(default_factory=list)
    bootcamp_highlight: str = ""
    template_type: ApplicantType = "student"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── 직렬화 헬퍼 ──────────────────────────────────────

def to_json(obj: Any, indent: int = 2) -> str:
    if hasattr(obj, "to_dict"):
        return json.dumps(obj.to_dict(), ensure_ascii=False, indent=indent)
    return json.dumps(obj, ensure_ascii=False, indent=indent)
