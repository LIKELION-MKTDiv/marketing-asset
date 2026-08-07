"""과정 공통 고정 블록 로더.

Hoya 지시 2026-07-20: 같은 과정 지원자 전원에게 동일한 5개 섹션
(부트캠프 교육 이수 내역 / 기업 연계 프로젝트 경험 / 멘토링 및 지원 프로그램 /
인턴십 / 취업 연계)은 개인 요소가 0인데도 매 지원자마다 Opus가 새로 작문해왔다.
전체 산출 분량의 50~57%가 이 중복 콘텐츠였고 섹션 제목마저 지원자마다 달라졌다.

이 모듈은 `templates/bootcamp_common/{class_id}.md`(과정별 고정 블록)를
{섹션명: 본문} dict로 파싱한다. 목적: ① 크레딧 절감 ② 과정 내 표기 통일
③ 사실 숫자(104H/160H 등) 재작문에 따른 환각 차단.

**하위호환 필수**: class_id에 해당하는 파일이 없으면 빈 dict를 반환한다.
과거 과정(AIPNLP05·BEJV26·CLD07 등)은 이 모듈이 존재하기 전과 100% 동일하게 동작해야 한다.

[2026-07-21 개정 — 감찰 REQUEST_CHANGES 반영]
- title-only 매칭(match_fixed_topic)이 실데이터 448건(재스캔 453건) 전수 스캔에서
  21건 누출(제목이 별칭 목록에 없는 표현으로 생성됨)로 확인됨. section_id 화이트리스트
  매칭을 1순위로 추가하고 제목 별칭은 보조로 내림(구조 식별자 우선 매칭 원칙).
- class_id 검증 부재(경로 인젝션 위험) + 조용한 폴백(로그 없음) 문제를 함께 닫는다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# 6개 고정 섹션 표준 제목 — 고정 블록 md의 '## ' 헤더와 정확히 일치해야 한다.
# [2026-08-06] '프로젝트 경험' 신설 — V2 온보딩 과정(현재 kdt-backendj-27th)에서 지원자
# 전원 동일한 부트캠프 표준 프로젝트(1차/2차/3차)를 렌더하는 고정 블록. V1 merge_common_blocks
# 앵커 목록(_ANCHOR_SLOT_*)엔 포함되지 않음 — V2 렌더러(_v2_render_projects)가 common_blocks
# 에서 직접 읽어 쓰는 V2 전용 슬롯이라 V1 병합 로직에는 영향 없음.
FIXED_SECTION_TITLES = [
    "부트캠프 교육 이수 내역",
    "프로젝트 경험",
    "기업 연계 프로젝트 경험",
    "멘토링 및 지원 프로그램",
    "인턴십",
    "취업 연계",
]

# 고정 섹션 판별용 별칭(정규화 후 부분일치). LLM이 그래도 유사 제목 섹션을
# 만들어낸 경우(예: "인턴십 프로그램", "취업 연계 프로그램", "기업 연계 프로젝트")
# 중복 제거에도 이 별칭을 사용한다 (render_md/render_html의 dedup 공용).
# ── match_fixed_topic()의 2순위(보조) 매칭. 1순위는 아래 SECTION_ID_TOPIC_MAP.
FIXED_ALIASES: dict[str, list[str]] = {
    "부트캠프 교육 이수 내역": ["부트캠프 교육 이수", "부트캠프 이수 내역", "부트캠프 이수"],
    "기업 연계 프로젝트 경험": ["기업 연계", "기업연계"],
    "멘토링 및 지원 프로그램": ["멘토링"],
    "인턴십": ["인턴십"],
    "취업 연계": ["취업 연계", "취업연계"],
}

# ── section_id 화이트리스트 (1순위 매칭) ──────────────────────────────────
# [2026-07-21 신설] 실데이터(474건, 고유 class×name 453건) 전수 스캔으로 실측한
# section_id → 표준 제목 매핑. LLM이 제목을 아무리 바꿔 써도(예: "채용 연계 프로그램",
# "심화 프로젝트(기업 수준) 상세") section_id는 6개 카테고리 계열(bootcamp_training/
# internship*/partnerships*/mentoring*/enterprise*·corporate*·capstone*·company*)로
# 비교적 안정적으로 나온다 — 이게 title-only 매칭이 놓친 21건을 잡는 1순위 축.
# 정확한 canonical 배정은 scan(title_by_sid) 실측 표본을 근거로 함(2026-07-21).
SECTION_ID_TOPIC_MAP: dict[str, str] = {
    "bootcamp_training": "부트캠프 교육 이수 내역",
    "internship": "인턴십",
    "internship_experience": "인턴십",
    "internship_partnerships": "인턴십",
    "partnerships": "취업 연계",
    "partnerships_project": "기업 연계 프로젝트 경험",
    "partnerships_mentoring": "멘토링 및 지원 프로그램",
    "mentoring": "멘토링 및 지원 프로그램",
    "mentoring_support": "멘토링 및 지원 프로그램",
    "mentoring_partnerships": "멘토링 및 지원 프로그램",
    "mentoring_and_support": "멘토링 및 지원 프로그램",
    "enterprise_project": "기업 연계 프로젝트 경험",
    "enterprise_partnership": "기업 연계 프로젝트 경험",
    "enterprise_project_detail": "기업 연계 프로젝트 경험",
    "corporate_project": "기업 연계 프로젝트 경험",
    "corporate_partnership": "기업 연계 프로젝트 경험",
    "corporate_partnerships": "기업 연계 프로젝트 경험",
    "company_project": "기업 연계 프로젝트 경험",
}

# prefix 매칭(startswith) — "capstone_project", "capstone_project_detail" 등 계열 전부 커버.
SECTION_ID_PREFIX_TOPICS: list[tuple[str, str]] = [
    ("capstone_project", "기업 연계 프로젝트 경험"),
]

# 개인 섹션 버킷1(실무 경력·커리어 전환·학력) 판별용 section_id 화이트리스트.
# _classify_personal_bucket()의 1순위 매칭 — generate_future_resume.py에서 사용.
PERSONAL_BUCKET1_SECTION_IDS: set[str] = {
    "education",
    "existing_experience",
    "career_transition",
    "existing_competencies",
}

# class_id는 시트에서 온 값을 그대로 파일 경로에 사용하므로(common_block_path) 검증 필수.
_CLASS_ID_RE = re.compile(r"^[a-z0-9_.-]+$")

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "bootcamp_common"

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_SECTION_HEADER_RE = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_HR_LINE_RE = re.compile(r"^-{3,}$")


def common_block_path(class_id: str) -> Path:
    """class_id → 고정 블록 md 경로 (존재 여부 무관)."""
    return _TEMPLATES_DIR / f"{class_id}.md"


def load_common_blocks(class_id: str | None) -> dict[str, str]:
    """class_id에 해당하는 고정 블록 md를 {섹션명: 본문(md)} dict로 파싱.

    - HTML 주석(메타 정보)은 제거한다.
    - '## 제목' 기준으로 섹션을 분리한다.
    - 섹션 사이 구분선('---')은 본문에서 제거한다.
    - 파일이 없거나 class_id가 비어있으면 빈 dict 반환 (하위호환 — 기존 동작 100% 유지).
    - class_id가 `^[a-z0-9_.-]+$` 형식이 아니면(경로 인젝션 방어) 빈 dict + 경고 후 반환.
    - 파싱된 섹션명이 FIXED_SECTION_TITLES에 없으면 헤더 오타 의심 경고 출력
      (과정별 섹션 개수가 다른 건 정상이므로 "개수 불일치"가 아니라 "알 수 없는 섹션명"을 기준으로 함).
    """
    if not class_id:
        return {}

    if not _CLASS_ID_RE.match(class_id):
        print(
            f"[공통블록] 경고: class_id 형식 불일치({class_id!r}, 허용 패턴 ^[a-z0-9_.-]+$) — 빈 dict 반환",
            file=sys.stderr,
        )
        return {}

    path = common_block_path(class_id)
    if not path.is_file():
        return {}

    raw = path.read_text(encoding="utf-8")
    raw = _HTML_COMMENT_RE.sub("", raw)

    matches = list(_SECTION_HEADER_RE.finditer(raw))
    blocks: dict[str, str] = {}
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body_lines = raw[start:end].split("\n")

        # 앞뒤 빈 줄 제거
        while body_lines and body_lines[0].strip() == "":
            body_lines.pop(0)
        while body_lines and body_lines[-1].strip() == "":
            body_lines.pop()
        # 섹션 말미의 '---' 구분선(다음 섹션과의 구분자) 제거
        while body_lines and _HR_LINE_RE.match(body_lines[-1].strip()):
            body_lines.pop()
            while body_lines and body_lines[-1].strip() == "":
                body_lines.pop()

        blocks[title] = "\n".join(body_lines)

    for title in blocks:
        if title not in FIXED_SECTION_TITLES:
            print(
                f"[공통블록] 경고: {class_id} — 알 수 없는 섹션명 '{title}' "
                f"(헤더 오타 의심, 표준 5종: {', '.join(FIXED_SECTION_TITLES)})",
                file=sys.stderr,
            )

    return blocks


def log_common_block_status(class_id: str | None, common_blocks: dict[str, str], *, context: str = "") -> None:
    """[공통블록] 로드/미적용 1줄 로그 (필수 — 조용한 폴백 금지).

    class_id 오타·미전달로 고정 블록이 미적용됐는데 경고 없이 예전 동작(전 섹션 LLM 생성)으로
    조용히 복귀하면, 크레딧 낭비가 성공한 실행처럼 보이는 문제를 막기 위한 진입점 로그.
    merge_common_blocks(generate_future_resume.py)·writer 지침 주입(_common_block_exclusion)
    양쪽 진입점에서 호출한다.
    """
    prefix = f"[공통블록]{f' {context}' if context else ''}".rstrip() + " "
    if common_blocks:
        print(f"{prefix}{class_id}: {len(common_blocks)}개 로드 ({', '.join(common_blocks.keys())})")
        return
    if not class_id:
        reason = "class_id 미전달"
    elif not _CLASS_ID_RE.match(class_id):
        reason = f"class_id 형식 불일치({class_id!r})"
    else:
        reason = f"파일 없음: {common_block_path(class_id)}"
    print(f"{prefix}미적용 ({reason})")


def aliases_and_ids_for(canonical: str) -> tuple[list[str], list[str]]:
    """canonical 표준 제목에 대응하는 프롬프트용 제목 별칭 예시 + section_id 예시를 반환.

    [2026-07-21 2차 감찰 REQUEST_CHANGES 수정] resume_writer.py의
    COMMON_BLOCK_EXCLUSION_TEMPLATE 금지 예시 문단이 하드코딩돼 있어, 블록이 없는 과정
    (예: CLD08의 '기업 연계 프로젝트 경험')에도 그 주제 생성을 금지하는 문구가 그대로
    들어가 버렸다(class별 블록 유무와 무관하게 정적). 이 함수는 FIXED_ALIASES/
    SECTION_ID_TOPIC_MAP/SECTION_ID_PREFIX_TOPICS(정책 SSOT)에서 동적으로 뽑아,
    writer._common_block_exclusion()이 "로드된 common_blocks 기준"으로만 예시를
    구성하게 한다 — 정책이 프롬프트와 후처리(match_fixed_topic) 양쪽에서 같은 값을
    참조하도록 SSOT를 한 곳(이 모듈)으로 유지."""
    aliases = [canonical] + list(FIXED_ALIASES.get(canonical, []))
    ids = [sid for sid, c in SECTION_ID_TOPIC_MAP.items() if c == canonical]
    ids += [prefix for prefix, c in SECTION_ID_PREFIX_TOPICS if c == canonical]
    return aliases, ids


def normalize_title(title: str) -> str:
    """제목 비교용 정규화 — 공백 제거."""
    return re.sub(r"\s+", "", title or "")


def match_fixed_topic(title: str, section_id: str | None = None) -> str | None:
    """title/section_id가 5개 고정 주제(또는 그 제목 변형) 중 하나에 해당하면
    표준 제목을 반환. 해당 없으면 None.

    LLM이 지침을 어기고 유사 제목 섹션을 생성했을 때 렌더 단계에서
    걸러내는 안전망(dedup)으로 사용한다.

    매칭 우선순위 (2026-07-21 개정):
      1순위 — section_id 화이트리스트(SECTION_ID_TOPIC_MAP/SECTION_ID_PREFIX_TOPICS).
              구조 식별자라 LLM이 제목을 완전히 다르게 써도(예: "채용 연계 프로그램") 안정적.
      2순위 — title 별칭 매칭(FIXED_ALIASES). section_id가 없거나 화이트리스트 밖일 때 보조로 사용.

    **주의**: 이 함수는 "고정 주제에 속하는가"만 판별한다. 그 주제가 실제로 이번 class_id의
    고정 블록 dict(common_blocks)에 존재하는지는 호출부(merge_common_blocks)에서 별도로
    확인해야 한다 — 블록이 없는 과정(예: CLD08의 기업 연계)에서 이 함수 결과만으로 무조건
    제거하면 대체 콘텐츠 없이 섹션이 통째로 사라진다.
    """
    norm_sid = (section_id or "").strip().lower()
    if norm_sid:
        if norm_sid in SECTION_ID_TOPIC_MAP:
            return SECTION_ID_TOPIC_MAP[norm_sid]
        for prefix, canonical in SECTION_ID_PREFIX_TOPICS:
            if norm_sid.startswith(prefix):
                return canonical

    norm_title = normalize_title(title)
    if not norm_title:
        return None
    for canonical, aliases in FIXED_ALIASES.items():
        for alias in aliases:
            if normalize_title(alias) in norm_title:
                return canonical
    return None
