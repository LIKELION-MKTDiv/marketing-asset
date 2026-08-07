"""미래이력서 생성 스크립트 — Phase 3 데이터 → 이력서형 MD + HTML 출력."""
from __future__ import annotations

import csv
import html as _html
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import re as _re

from utils.bootcamp_common import (
    PERSONAL_BUCKET1_SECTION_IDS,
    load_common_blocks,
    log_common_block_status,
    match_fixed_topic,
)

# 제거할 예상/예정 패턴 (미래이력서는 완성형 실체 — 단서 불필요)
_PROJECTED_PATTERNS = _re.compile(
    r"\s*[\(\（]?\s*수료\s*후\s*예상\s*[\)\）]?"
    r"|\s*[\(\（]\s*예정\s*[\)\）]"
    r"|\s*\*\s*\(수료\s*후\s*예상\)\s*\*"
    r"|\s*\*(수료\s*후\s*예상)\*",
    _re.UNICODE,
)


def strip_projected(text: str) -> str:
    """content/title에서 수료 후 예상·(예정) 표기 제거."""
    if not text:
        return text
    return _PROJECTED_PATTERNS.sub("", text).strip()


# 진행형 → 완료형 치환 패턴 (summary/career_objective 전용)
_ONGOING_REPLACEMENTS = [
    # "습득하고 있습니다" → "습득하였습니다"
    (_re.compile(r"습득하고\s*있습니다"), "습득하였습니다"),
    # "성장하고 있으며" → "성장하였으며"
    (_re.compile(r"성장하고\s*있으며"), "성장하였으며"),
    # "성장하고 있습니다" → "성장하였습니다"
    (_re.compile(r"성장하고\s*있습니다"), "성장하였습니다"),
    # "목표로 하고 있습니다" → "목표로 하고 있습니다" → "목표로 하였습니다"
    (_re.compile(r"목표로\s*하고\s*있습니다"), "목표로 하였습니다"),
    # "노력하고 있습니다" → "노력하였습니다"
    (_re.compile(r"노력하고\s*있습니다"), "노력하였습니다"),
    # "발전하고 있습니다" → "발전하였습니다"
    (_re.compile(r"발전하고\s*있습니다"), "발전하였습니다"),
    # "쌓고 있습니다" → "쌓았습니다"
    (_re.compile(r"쌓고\s*있습니다"), "쌓았습니다"),
    # "익히고 있습니다" → "익혔습니다"
    (_re.compile(r"익히고\s*있습니다"), "익혔습니다"),
    # "배우고 있습니다" → "배웠습니다"
    (_re.compile(r"배우고\s*있습니다"), "배웠습니다"),
    # "키우고 있습니다" → "키웠습니다"
    (_re.compile(r"키우고\s*있습니다"), "키웠습니다"),
    # "채우고 있습니다" → "채웠습니다"
    (_re.compile(r"채우고\s*있습니다"), "채웠습니다"),
    # "준비하고 있습니다" → "준비하였습니다"
    (_re.compile(r"준비하고\s*있습니다"), "준비하였습니다"),
    # "공부하고 있습니다" → "공부하였습니다"
    (_re.compile(r"공부하고\s*있습니다"), "공부하였습니다"),
    # "강화하고 있습니다" → "강화하였습니다"
    (_re.compile(r"강화하고\s*있습니다"), "강화하였습니다"),
    # "만들어가고 있습니다" → "만들었습니다"
    (_re.compile(r"만들어가고\s*있습니다"), "만들었습니다"),
    # "만들어 가고 있습니다" → "만들었습니다"
    (_re.compile(r"만들어\s*가고\s*있습니다"), "만들었습니다"),
    # "구축하고 있습니다" → "구축하였습니다"
    (_re.compile(r"구축하고\s*있습니다"), "구축하였습니다"),
    # "개발하고 있습니다" → "개발하였습니다"
    (_re.compile(r"개발하고\s*있습니다"), "개발하였습니다"),
    # "체계적으로 습득하고 있습니다" → "체계적으로 습득하였습니다" (위 패턴에 포함되나 명시)
    # "수료 예정" → "수료" (본문 한정)
    (_re.compile(r"수료\s*예정"), "수료"),
]


def convert_to_completion_form(text: str) -> str:
    """summary/career_objective 진행형 표현을 완료형으로 치환.

    본문(summary/섹션 title)에만 적용. 푸터는 별도 처리.
    "(수료 후 예상)" 등 projected 표기는 strip_projected()에서 이미 제거되므로
    여기서는 진행형 동사 패턴만 대응.
    """
    if not text:
        return text
    result = text
    for pattern, replacement in _ONGOING_REPLACEMENTS:
        result = pattern.sub(replacement, result)
    return result


# ── 과정 공통 고정 블록 병합 ──────────────────────────────────────────────
# [2026-07-20 신설] Hoya 지시 — 부트캠프 교육 이수 내역 / 기업 연계 프로젝트 경험 /
# 멘토링 및 지원 프로그램 / 인턴십 / 취업 연계 5개 섹션은 과정 공통(개인 요소 0)이라
# LLM 생성에서 빼고 templates/bootcamp_common/{class_id}.md 를 그대로 삽입한다.
def _classify_personal_bucket(sec: dict) -> str:
    """비-고정 섹션을 앵커 위치 기준 버킷으로 분류.

    [2026-07-21 1차 개정 — 감찰 REQUEST_CHANGES 반영] bucket1(맨 앞, 실무 경력·커리어
    전환·학력)은 더 이상 fallback이 아니다 — PERSONAL_BUCKET1_SECTION_IDS 화이트리스트
    또는 명확한 제목 키워드(학력/경력/커리어전환)일 때만 진입한다. 어디에도 안 걸리는
    섹션은 "bucket_unclassified"로 분류해 merge_common_blocks가 문서 맨 뒤(fallback은
    손해가 가장 작은 자리)에 배치한다. 이전엔 미분류 섹션이 fallback으로 bucket1(맨 앞)에
    꽂혀 개인 경력·학력보다 앞에 나오는 문제가 있었다(GM06/CLD08 실측 사례).

    [2026-07-21 2차 개정 — 감찰 REQUEST_CHANGES 반영, 수정 5] sid 화이트리스트를 title
    키워드보다 먼저 평가한다. 이전엔 title 키워드 검사(bucket2/bucket3)가 먼저 실행돼,
    sid=career_transition인데 제목이 "핵심 역량 및 커리어 전환"처럼 bucket3 키워드
    ("핵심역량")를 포함하는 섹션이 sid 화이트리스트(bucket1)보다 먼저 title 검사에
    걸려 bucket3로 오분류됐다(CLD08 3건 실측). 구조 식별자(sid)가 표현(title)보다
    안정적이므로 1순위로 둔다."""
    sid = (sec.get("section_id") or "").strip().lower()
    norm_title = _re.sub(r"\s+", "", sec.get("title") or "")

    # 1순위 — sid 화이트리스트 (제목 표현이 어떻게 바뀌어도 안정적)
    if sid == "tech_stack":
        return "bucket2_tech"
    if sid == "portfolio_projects":
        return "bucket2_portfolio"
    if sid in PERSONAL_BUCKET1_SECTION_IDS:
        return "bucket1"
    if sid in ("core_competencies", "activities_awards"):
        return "bucket3"

    # 2순위 — sid가 화이트리스트 밖일 때만 title 키워드로 보조 판별
    if "기술스택" in norm_title:
        return "bucket2_tech"
    if "포트폴리오" in norm_title:
        return "bucket2_portfolio"
    if "핵심역량" in norm_title:
        return "bucket3"
    if "학력" in norm_title or "경력" in norm_title or "커리어전환" in norm_title:
        return "bucket1"
    return "bucket_unclassified"


def _fixed_section_dict(title: str, content: str, order: int) -> dict:
    slug = _re.sub(r"[^0-9A-Za-z가-힣]+", "_", title).strip("_")
    return {
        "section_id": f"fixed_common_{slug}",
        "title": title,
        "content": content,
        "order": order,
        "is_projected": False,
    }


# 앵커 순서(고정 블록 슬롯)에서, "고정 블록이 없는 주제"의 LLM 생성 섹션을 어느 슬롯에
# 꽂을지 정하는 맵. bucket_unclassified(문서 맨 뒤)로 떨어뜨리지 않고, 그 주제가 원래
# 고정 블록으로 들어갔을 자리(앵커)에 그대로 둔다. [2026-07-21 2차 감찰 REQUEST_CHANGES 수정]
_ANCHOR_SLOT_BOOTCAMP = "부트캠프 교육 이수 내역"
_ANCHOR_SLOT_ENTERPRISE = "기업 연계 프로젝트 경험"
_ANCHOR_SLOT_LATE_ORDER = {"인턴십": 0, "멘토링 및 지원 프로그램": 1, "취업 연계": 2}


def merge_common_blocks(sections: list[dict], class_id: str | None) -> list[dict]:
    """LLM 생성 섹션(sections, order로 이미 정렬된 상태) + 과정 공통 고정 블록을 병합.

    class_id에 해당하는 고정 블록 파일이 없으면 sections를 그대로 반환한다
    (하위호환 — 고정 블록 파일 없는 과거 과정은 기존 동작 100% 유지, 영향 0).

    앵커 순서 (고정, Hoya 지시 2026-07-20):
      1. (개인) 실무 경력·커리어 전환 → 학력           [bucket1]
      2. (고정 또는 그 자리의 LLM 원본) 부트캠프 교육 이수 내역
      3. (개인) 기술 스택 → 프로젝트 포트폴리오         [bucket2]
      4. (고정 또는 그 자리의 LLM 원본) 기업 연계 프로젝트 경험
      5. (개인) 핵심 역량 및 활동                      [bucket3]
      6. (고정 또는 그 자리의 LLM 원본) 인턴십 → 멘토링 및 지원 프로그램 → 취업 연계
      7. (개인, fallback) 진짜 미분류 섹션              [bucket_unclassified — 문서 맨 뒤]

    [2026-07-21 1차 개정 — 감찰 REQUEST_CHANGES 반영]
    - 진입 시 항상 [공통블록] 로드/미적용 1줄 로그 (조용한 폴백 금지, class_id 오타 조기 발견).
    - dedup 안전망은 "고정 주제로 보이는가"(match_fixed_topic)뿐 아니라 "그 주제가 이번
      class_id의 common_blocks에 실제로 존재하는가"까지 함께 확인한다. 블록이 없는 과정
      (예: CLD08은 '기업 연계 프로젝트 경험' 블록이 없음)에서 그 주제로 보이는 LLM 생성
      섹션을 무조건 제거하면 대체 콘텐츠 없이 섹션이 통째로 사라지므로, 이 경우엔 원본
      LLM 섹션을 그대로 살려둔다.

    [2026-07-21 2차 개정 — 감찰 REQUEST_CHANGES 반영, CLD08 12명 순서 밀림]
    - 위 1차 개정에서 "그대로 살려둔" 섹션이 _classify_personal_bucket()으로 다시 들어가면
      bucket1 화이트리스트(학력/경력/커리어전환)에 안 걸려 bucket_unclassified(문서 맨 뒤)로
      떨어졌다 — 대체 콘텐츠는 안 사라졌지만 "제자리"가 아니라 맨 뒤로 밀려 기존 방식(고정
      블록 도입 전 LLM 순서)과 위치가 달라짐. match_fixed_topic으로 canonical 주제가 확인된
      섹션은 _classify_personal_bucket을 거치지 않고, 그 canonical이 원래 꽂혔을 앵커 슬롯에
      직접 배치한다 — bucket_unclassified는 canonical조차 없는 "진짜" 미분류 섹션 전용으로 좁힘.
    """
    log_common_block_status(class_id, common_blocks := load_common_blocks(class_id), context="merge_common_blocks")
    if not common_blocks:
        return sections

    # career_objective는 render_md/render_html에서 sections 루프 자체를 스킵하므로
    # 순서에 영향 없이 그대로 통과시킨다.
    career_obj_secs = [s for s in sections if s.get("section_id") == "career_objective"]
    others = [s for s in sections if s.get("section_id") != "career_objective"]

    # 안전망 — LLM이 지침을 어기고 고정 주제와 겹치는 섹션을 생성했으면 제거(고정 블록이 대체).
    # 그 주제의 고정 블록이 이번 class_id에 없으면(예: CLD08의 기업 연계) 제거하지 않고,
    # 그 주제의 "앵커 자리"에 원본 LLM 섹션을 그대로 꽂는다(orphan_* 버킷).
    remaining: list[dict] = []
    orphan_bootcamp: list[dict] = []
    orphan_enterprise: list[dict] = []
    orphan_late: list[dict] = []
    for s in others:
        canonical = match_fixed_topic(s.get("title", ""), s.get("section_id"))
        if canonical is not None and canonical in common_blocks:
            continue  # 고정 블록이 대체 — 원본 LLM 섹션은 버림 (기존 동작)
        if canonical == _ANCHOR_SLOT_BOOTCAMP:
            orphan_bootcamp.append(s)
        elif canonical == _ANCHOR_SLOT_ENTERPRISE:
            orphan_enterprise.append(s)
        elif canonical in _ANCHOR_SLOT_LATE_ORDER:
            orphan_late.append(s)
        else:
            remaining.append(s)  # canonical 없음 — 진짜 개인 섹션(bucket 분류 대상)

    orphan_bootcamp.sort(key=lambda s: s.get("order", 0))
    orphan_enterprise.sort(key=lambda s: s.get("order", 0))
    orphan_late.sort(
        key=lambda s: (
            _ANCHOR_SLOT_LATE_ORDER[match_fixed_topic(s.get("title", ""), s.get("section_id"))],
            s.get("order", 0),
        )
    )

    others = remaining

    bucket1 = sorted(
        (s for s in others if _classify_personal_bucket(s) == "bucket1"),
        key=lambda s: s.get("order", 0),
    )
    bucket2_tech = [s for s in others if _classify_personal_bucket(s) == "bucket2_tech"]
    bucket2_portfolio = [s for s in others if _classify_personal_bucket(s) == "bucket2_portfolio"]
    bucket3 = sorted(
        (s for s in others if _classify_personal_bucket(s) == "bucket3"),
        key=lambda s: s.get("order", 0),
    )
    # fallback(진짜 미분류) — bucket3보다도 뒤, 문서 맨 끝. 손해가 가장 작은 자리.
    bucket_unclassified = sorted(
        (s for s in others if _classify_personal_bucket(s) == "bucket_unclassified"),
        key=lambda s: s.get("order", 0),
    )

    ordered: list[dict] = list(career_obj_secs)
    order_n = 1

    def _append(sec: dict) -> None:
        nonlocal order_n
        sec = dict(sec)
        sec["order"] = order_n
        ordered.append(sec)
        order_n += 1

    for s in bucket1:
        _append(s)
    if _ANCHOR_SLOT_BOOTCAMP in common_blocks:
        _append(_fixed_section_dict(_ANCHOR_SLOT_BOOTCAMP, common_blocks[_ANCHOR_SLOT_BOOTCAMP], order_n))
    else:
        for s in orphan_bootcamp:
            _append(s)
    for s in bucket2_tech + bucket2_portfolio:
        _append(s)
    if _ANCHOR_SLOT_ENTERPRISE in common_blocks:
        _append(_fixed_section_dict(_ANCHOR_SLOT_ENTERPRISE, common_blocks[_ANCHOR_SLOT_ENTERPRISE], order_n))
    else:
        for s in orphan_enterprise:
            _append(s)
    for s in bucket3:
        _append(s)
    for fixed_title in ("인턴십", "멘토링 및 지원 프로그램", "취업 연계"):
        if fixed_title in common_blocks:
            _append(_fixed_section_dict(fixed_title, common_blocks[fixed_title], order_n))
        else:
            for s in orphan_late:
                if match_fixed_topic(s.get("title", ""), s.get("section_id")) == fixed_title:
                    _append(s)
    for s in bucket_unclassified:
        _append(s)

    return ordered


def load_data(name: str, data_dir: Path) -> tuple[dict, dict, dict]:
    """Phase 1, 2, 3 중간 산출물 로드."""
    ext = json.loads((data_dir / f"{name}_1_extracted.json").read_text("utf-8"))
    prof = json.loads((data_dir / f"{name}_2_profile.json").read_text("utf-8"))
    content = json.loads((data_dir / f"{name}_3_content.json").read_text("utf-8"))
    return ext, prof, content


def _footer_bootcamp_name(bi: dict) -> str:
    """푸터용 과정명. 괄호 부가설명 제거.
    backendj 계열은 지원자별 이름 변형('자바 백엔드 개발자 부트캠프 N기'/'백엔드 자바 부트캠프 N기' 등)을
    '자바 백엔드 부트캠프 {N}기'로 정규화 — 기수(N)는 bootcamp_name에서 동적 추출.
    [2026-07-03] 기존 '26기' 하드코딩 제거 (27기 도입, 정우빈 푸터 26기 오염 건)."""
    raw = bi.get("bootcamp_name") or ""
    clean = raw.split(" (")[0].strip()
    if "백엔드" in raw and "자바" in raw:
        m = _re.search(r"(\d+)\s*기", raw)
        return f"자바 백엔드 부트캠프 {m.group(1)}기" if m else "자바 백엔드 부트캠프"
    return clean or "부트캠프"


# ═══════════════════════════════════════════════════════════════════════
# ── V2 렌더러 (과정별 온보딩 가능한 미래이력서 V2) ──────────────────────
# [2026-08-05 신설] Hoya 지시 — temp/render_v2.py 프로토타입(샘플 지원자 A/BEJV27 대상,
# 브라우저 QA로 렌더 버그 2건 수정 완료된 working 코드)을 프로덕션 render_html/render_md에
# 이식. V2_COURSES에 등록된 class_id만 아래 V2 렌더를 타고, 나머지 과정은 render_md/
# render_html 하단의 기존 V1 로직을 그대로 탄다 (게이트는 각 함수 최상단 참조).
#
# 새 과정 V2 온보딩 = ① V2_COURSES에 class_id 한 줄 추가 ② templates/bootcamp_common/
# {class_id}.md 준비 ③ 필요하면 아래 [과정별 커스터마이즈 지점] dict에 항목 추가(없어도
# 제네릭 fallback으로 동작). 상세 체크리스트: docs/V2_렌더_명세.md.
# ═══════════════════════════════════════════════════════════════════════

# V2 렌더를 적용할 과정. 새 과정은 이 set에 class_id만 추가하면 된다 (하드코딩 == 비교 금지).
V2_COURSES: set[str] = {"kdt-backendj-27th"}

_V2_CSS_PATH = Path(__file__).resolve().parent / "templates" / "v2_simple.css"


def _v2_css() -> str:
    """V2 전용 CSS. 레포 내부 templates/v2_simple.css에서 로드 (Downloads 등 외부 경로 의존 금지)."""
    return _V2_CSS_PATH.read_text(encoding="utf-8")


def _v2_esc(s) -> str:
    return _html.escape(str(s or ""))


def _v2_md_inline(s) -> str:
    """**x** → <strong>, 나머지는 escape."""
    s = _v2_esc(s)
    return _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def _v2_md_to_html(text: str) -> str:
    """V2 전용 간단 md → HTML (h3/h4, ul/li, p, strong, table).

    render_html() 내부의 V1 md_to_html은 nested 함수라 재사용 불가 + escape 동작이
    다르므로(V2는 html.escape 포함) 별도 구현으로 둔다."""
    if not text:
        return ""
    out: list[str] = []
    in_ul = False
    in_table = False
    rows: list[list[str]] = []

    def flush_table():
        nonlocal in_table, rows
        if not rows:
            in_table = False
            return
        out.append("<table>")
        for i, r in enumerate(rows):
            tag = "th" if i == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{_v2_md_inline(c)}</{tag}>" for c in r) + "</tr>")
        out.append("</table>")
        in_table = False
        rows = []

    for line in text.split("\n"):
        t = line.strip()
        if t.startswith("|") and t.endswith("|"):
            if all(c in "|-: " for c in t):
                continue
            if in_ul:
                out.append("</ul>")
                in_ul = False
            in_table = True
            rows.append([c.strip() for c in t.strip("|").split("|")])
            continue
        elif in_table:
            flush_table()

        if not t or t == "---":
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if t.startswith("#### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h4>{_v2_md_inline(t[5:])}</h4>")
        elif t.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3>{_v2_md_inline(t[4:])}</h3>")
        elif t.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_v2_md_inline(t[2:])}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{_v2_md_inline(t)}</p>")
    if in_table:
        flush_table()
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


# [과정별 커스터마이즈 지점 1] 보유기술 3그룹 정의 — 과정마다 기술 카테고리 구성이 다르다
# (예: 그로스마케팅엔 DevOps 카테고리가 없음). class_id → [(그룹명, [원본 카테고리...]), ...].
# 새 과정 추가 시 여기에 항목을 넣으면 큐레이션된 그룹으로 노출된다. 미등록 과정은
# _v2_skill_groups_for()의 제네릭 fallback(raw 카테고리를 그대로 각자 그룹화)으로 동작.
V2_SKILL_GROUPS_BY_COURSE: dict[str, list[tuple[str, list[str]]]] = {
    "kdt-backendj-27th": [
        ("Backend", ["Backend", "Database"]),
        ("Frontend", ["Frontend"]),
        ("DevOps & Infra", ["DevOps & Infra", "Monitoring"]),
    ],
}
_V2_SKILL_GROUP_EXCLUDE = {"Tools", "보유역량"}  # 저정보 카테고리(제네릭 fallback에서 제외)


def _v2_skill_groups_for(class_id: str | None, raw: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    if class_id in V2_SKILL_GROUPS_BY_COURSE:
        return V2_SKILL_GROUPS_BY_COURSE[class_id]
    return [(cat, [cat]) for cat in raw.keys() if cat not in _V2_SKILL_GROUP_EXCLUDE]


# [과정별 커스터마이즈 지점 5] 보유기술 하드스킬 고정 블록 — 부트캠프 표준 스택은 지원자
# 전원 동일(개인화 요소 없음)이라, LLM 생성 '기술 스택'(포맷이 지원자마다 제각각: **Cat**·표·
# ### Cat·불릿·**서브라벨:**·괄호설명 등 6+종이라 파싱 취약)을 파싱하는 대신 이 고정 그룹을
# 전원에게 렌더한다. Soft Skills만 개인(prof) 유지. (2026-08-07 Hoya 지시 — 프로젝트 고정블록과
# 동일 결. 미등록 과정은 _v2_parse_tech_stack 파서 fallback으로 동작.)
V2_FIXED_SKILLS_BY_COURSE: dict[str, list[tuple[str, list[str]]]] = {
    "kdt-backendj-27th": [
        ("Backend", ["Java", "Spring Boot", "Spring Security", "JPA", "Hibernate", "QueryDSL"]),
        ("Frontend", ["HTML", "CSS", "JavaScript", "React", "Next.js", "Node.js"]),
        ("DevOps & Infra", ["Docker", "Kubernetes", "GitHub Actions", "Nginx", "AWS", "Linux"]),
    ],
}


def _v2_skill_render_groups(secs: dict[str, str], class_id: str | None) -> list[tuple[str, list[str]]]:
    """보유기술 렌더용 [(그룹명, [태그...]), ...]. 고정블록 과정은 표준 스택(전원 동일),
    미등록 과정은 지원자별 '기술 스택' 파싱. HTML·MD 양쪽이 공유한다."""
    fixed = V2_FIXED_SKILLS_BY_COURSE.get(class_id or "")
    if fixed:
        return [(g, list(tags)) for g, tags in fixed]
    raw = _v2_parse_tech_stack(secs.get("기술 스택", ""))
    out = []
    for gname, srcs in _v2_skill_groups_for(class_id, raw):
        items: list[str] = []
        for s in srcs:
            items.extend(raw.get(s, []))
        out.append((gname, items))
    return out


def _v2_parse_tech_stack(tech_md: str) -> dict[str, list[str]]:
    """기술 스택 섹션 md → {카테고리: [항목...]}.

    LLM 출력 포맷이 지원자마다 달라 4형태를 모두 지원한다:
      ① '**카테고리**\\n항목, 항목'        (샘플 지원자 D)
      ② 표 '| **카테고리** | 항목, 항목 |'  (샘플 지원자 E·샘플 지원자 F)
      ③ '### 카테고리\\n항목, 항목'          (샘플 지원자 G)
      ④ '### 카테고리\\n- 항목\\n- 항목'      (샘플 지원자 H, 불릿)
    (2026-08-07 — ①만 처리하던 파서가 ②③④ 지원자의 하드 스킬을 통째 누락시킴)."""
    raw: dict[str, list[str]] = {}
    cat = None

    def add_items(c, text):
        if c is None:
            return
        # 서브라벨 접두 제거: '- **언어 및 프레임워크:** Java, ...' → 'Java, ...'
        # (카테고리 안에 **라벨:** 형태로 소분류가 박힌 지원자 대응 — 안 벗기면 카피에 ** 노출)
        t = _re.sub(r"^\*\*[^*]+?:\*\*\s*", "", text.strip())
        t = t.replace("**", "").strip()  # 남은 볼드 마커 제거
        raw.setdefault(c, []).extend(x.strip() for x in _re.split(r"[,·]", t) if x.strip())

    for line in tech_md.split("\n"):
        t = line.strip()
        if not t:
            continue
        # ② 표 포맷: | **카테고리** | 항목, 항목 |
        if t.startswith("|") and t.endswith("|"):
            if all(ch in "|-: " for ch in t):  # 구분선(|---|---|) 스킵
                continue
            cells = [c.strip() for c in t.strip("|").split("|")]
            if len(cells) < 2:
                continue
            key = _re.sub(r"[*#]", "", cells[0]).strip()
            if not key or key in ("카테고리", "구분", "분류", "기술"):  # 헤더행 스킵
                continue
            cat = key
            raw.setdefault(cat, [])
            add_items(cat, cells[1])
            continue
        # ①③ 헤더: **카테고리**  또는  ### 카테고리
        m = _re.match(r"^\*\*(.+?)\*\*$", t) or _re.match(r"^#{2,4}\s+(.+)$", t)
        if m:
            cat = _re.sub(r"[*#]", "", m.group(1)).strip()
            raw.setdefault(cat, [])
            continue
        # ④ 항목 줄 (불릿 '- '/'* ' 또는 콤마 리스트)
        add_items(cat, t[1:].strip() if t[:1] in "-*" else t)
    return raw


def _v2_render_skills(secs: dict[str, str], prof: dict, class_id: str | None) -> str:
    """보유 기술 섹션 HTML — 기술스택 카테고리(과정별 그룹) + Soft Skills."""
    parts = ['<section><h2>보유 기술</h2>']

    for gname, items in _v2_skill_render_groups(secs, class_id):
        items = items[:6]
        if not items:
            continue
        parts.append(f'<div class="skill-group"><h4>{_v2_esc(gname)}</h4><div class="skill-tags">')
        parts.append("".join(f'<span class="skill-tag">{_v2_esc(x)}</span>' for x in items))
        parts.append('</div></div>')

    soft = prof.get("soft_skills", [])[:3]
    if soft:
        parts.append('<div class="skill-group"><h4>Soft Skills</h4><div class="skill-tags">')
        parts.append("".join(f'<span class="skill-tag">{_v2_esc(x)}</span>' for x in soft))
        parts.append('</div></div>')
    parts.append('<div class="skills-note">※ 부트캠프 과정에서 습득 예정</div>')
    parts.append('</section>')
    return "\n".join(parts)


def _v2_parse_projects(project_md: str) -> list[dict[str, str]]:
    """'프로젝트 경험' 고정 블록 md → [{meta, title, overview, role, tech, result}, ...].

    [2026-08-06 방향전환 — Hoya 지시] 원래는 지원자별 LLM 생성 '프로젝트 포트폴리오'
    섹션을 파싱했으나, 포맷이 지원자마다 제각각(--- 유무·필드 콜론 위치·제목 구분자)이라
    truncation 버그가 반복 발생했다. backendj-27th 1~3차 프로젝트는 지원자 전원 동일한
    부트캠프 표준 프로젝트라 개인화 요소가 0 — 파서를 튼튼하게 고치는 대신 파싱 자체를
    없애고 templates/bootcamp_common/{class_id}.md '프로젝트 경험' 고정 확정본(포맷 통제됨)
    을 그대로 읽는다. 인자가 secs(지원자별 섹션)에서 common_blocks 값(과정 고정 블록)으로
    바뀐 것 외 파싱 로직 자체는 원래 포맷(### N차 ...: 제목 + - **필드**: 값)에 맞춘 그대로."""
    blocks = _re.split(r"\n---\n", project_md)
    projects: list[dict[str, str]] = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        title_m = _re.search(r"^###\s*(.+)$", b, _re.M)
        if not title_m:
            continue
        raw_title = title_m.group(1).replace("⭐", "").strip()
        if ":" in raw_title:
            meta, ptitle = raw_title.split(":", 1)
            meta, ptitle = meta.strip(), ptitle.strip()
        else:
            meta, ptitle = "", raw_title

        def field(key: str, block: str = b) -> str:
            m = _re.search(rf"- \*\*{key}\*\*:\s*(.+)", block)
            return m.group(1).strip() if m else ""

        projects.append({
            "meta": meta, "title": ptitle,
            "overview": field("개요"), "role": field("역할"),
            "tech": field("기술"), "result": field("성과"),
        })
    return projects


def _v2_render_projects(common_blocks: dict[str, str]) -> str:
    """프로젝트 경험 섹션 HTML — 과정 공통 고정 블록(전원 동일, templates/bootcamp_common/
    {class_id}.md '프로젝트 경험')을 렌더. class_id에 이 블록이 없으면(V2 온보딩 시 아직
    준비 안 된 과정) 빈 카드 목록으로 헤더만 렌더 — 온보딩 체크리스트에서 채워야 함."""
    cards = []
    for p in _v2_parse_projects(common_blocks.get("프로젝트 경험", "")):
        c = ['<div class="project">']
        c.append(f'<div class="project-head"><h3>{_v2_esc(p["title"])}</h3></div>')
        if p["meta"]:
            c.append(f'<div class="project-meta">{_v2_esc(p["meta"])}</div>')
        if p["overview"]:
            c.append(f'<p>{_v2_esc(p["overview"])}</p>')
        if p["role"]:
            c.append(f'<p style="color:#666;font-size:13.5px;"><strong>역할</strong> · {_v2_esc(p["role"])}</p>')
        if p["tech"]:
            c.append(f'<div class="project-tech"><strong>기술</strong> · {_v2_esc(p["tech"])}</div>')
        if p["result"]:
            c.append(f'<div class="project-meaning">{_v2_esc(p["result"])}</div>')
        c.append('</div>')
        cards.append("\n".join(c))
    return ('<section><h2>프로젝트 경험 <span class="badge">수료 후 예상</span></h2>\n'
            + "\n".join(cards) + '</section>')


# ── 버그2: '학력' 슬롯 일반화 — 학생=학력, 전향자=개인화 배경 섹션 (2026-08-06) ──────
# V2가 이미 별도 섹션으로 렌더하는 3개 고정 제목(기술 스택/프로젝트 포트폴리오/핵심 역량 및
# 활동)을 제외한 "나머지 개인화 섹션 전부"가 학력 슬롯에 들어간다. 원래 코드는
# secs.get("학력", "")로 고정 조회해서, 전향자(section_id=career_transition/
# existing_experience — 제목이 "커리어 전환"/"실무 프로젝트 경력"/"개발 학습 및 프로젝트
# 경험"/"실무 경력" 등으로 다름)의 배경 섹션이 빈 슬롯(13자 렌더) 뒤로 통째로 소실됐다.
_V2_FIXED_PERSONAL_EXCLUDE_SIDS = {"tech_stack", "portfolio_projects", "core_competencies", "activities_awards"}
_V2_FIXED_PERSONAL_EXCLUDE_TITLES = {"기술 스택", "프로젝트 포트폴리오", "핵심 역량 및 활동"}


def _v2_background_sections(content: dict) -> list[dict]:
    """학력 슬롯에 렌더할 개인화 배경 섹션 목록(원본 순서 유지).

    구조 식별자(section_id) 우선 판별 + title 보조(안전망) — 위 3개 고정 슬롯이 아닌
    섹션은 전부 배경 섹션으로 간주한다. 학생은 보통 1개(학력), 전향자는 1~2개
    (커리어 전환/실무 경력 등)가 나올 수 있고 둘 다 원본 제목 그대로 non-empty 렌더한다.
    이미 고정 3섹션은 제외했으므로 중복 렌더는 없다."""
    out = []
    for s in content.get("sections", []):
        sid = (s.get("section_id") or "").strip().lower()
        title = s.get("title", "")
        if sid in _V2_FIXED_PERSONAL_EXCLUDE_SIDS or title in _V2_FIXED_PERSONAL_EXCLUDE_TITLES:
            continue
        if not (s.get("content") or "").strip():
            continue
        out.append(s)
    return out


# [과정별 커스터마이즈 지점 2] 교육이수 커리큘럼 태그 큐레이션 — 이력서에 노출할 상위
# 역량 태그를 과정별로 손으로 고른 목록. 새 과정 추가 시 여기에 넣으면 그대로 노출되고,
# 미등록 과정은 _v2_derive_curriculum_tags()가 공통블록 표의 '핵심 역량' 열에서 동적 추출한다.
V2_CURRICULUM_TAGS_BY_COURSE: dict[str, list[str]] = {
    "kdt-backendj-27th": ["Java 백엔드 개발", "객체지향·SOLID 설계", "Spring Boot·JPA",
                           "REST API 설계", "프론트엔드(React·Next.js)", "컨테이너·CI/CD", "무중단 배포"],
}

# [과정별 커스터마이즈 지점 3] 부트캠프 소개 2줄 — 과정별 마케팅 문구. 새 과정 추가 시
# 여기에 넣으면 그대로 노출되고, 미등록 과정은 _v2_intro_text()가 track/과정명 기반
# 제네릭 문장으로 대체한다 (사실을 창작하지 않고 구조만 채우는 fallback — 환각 방지).
V2_INTRO_BY_COURSE: dict[str, str] = {
    "kdt-backendj-27th": (
        "취업을 목표로 Java·Spring 백엔드 개발의 기초부터 DevOps 운영까지 다루는 실무형 부트캠프입니다. "
        "코딩테스트 없이 입문하여 AI 기반 풀코스 커리큘럼과 기업 연계 프로젝트·인턴십을 경험합니다."
    ),
}

# [과정별 커스터마이즈 지점 4] 교육 기간 라벨 — "N개월 (H시간)" 표기. 과정 공식 명칭이
# 실제 날짜 계산과 다를 수 있어(예: 960시간 과정을 공식적으로 "6개월 과정"으로 표기)
# 정확한 표기가 필요하면 여기에 명시한다. 미등록 과정은 _v2_format_period()가 공통블록
# 원문의 날짜 2개 + "총 N시간" 표기에서 개월수·시간을 동적 계산(올림)해 채운다.
V2_PERIOD_LABEL_BY_COURSE: dict[str, str] = {
    "kdt-backendj-27th": "6개월 (960시간)",
}


def _v2_derive_curriculum_tags(edu_md: str, limit: int = 7) -> list[str]:
    """커리큘럼 표의 '핵심 역량' 열(마지막 열)에서 태그 동적 추출 — 제네릭 fallback."""
    tags: list[str] = []
    seen: set[str] = set()
    table_lines = [ln.strip() for ln in edu_md.split("\n")
                   if ln.strip().startswith("|") and ln.strip().endswith("|")]
    data_rows = [ln for ln in table_lines if not all(c in "|-: " for c in ln)][1:]  # 헤더행 제외
    for row in data_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if not cells:
            continue
        last = cells[-1]
        for t in _re.split(r"[,·]", last):
            t = t.strip()
            if t and t not in seen:
                seen.add(t)
                tags.append(t)
        if len(tags) >= limit:
            break
    return tags[:limit]


def _v2_intro_text(class_id: str | None, bi: dict) -> str:
    if class_id in V2_INTRO_BY_COURSE:
        return V2_INTRO_BY_COURSE[class_id]
    track = (bi.get("track") or "").strip()
    bname = (bi.get("bootcamp_name") or "").split(" (")[0].strip()
    base = track or bname or "실무형"
    return (f"{base} 역량을 목표로 실무 중심 커리큘럼을 다루는 부트캠프입니다. "
            f"상세 커리큘럼은 아래 교육 이수 내역을 참고해 주세요.")


def _v2_format_period(class_id: str | None, period_raw: str) -> str:
    dm = _re.findall(r"(\d{4}\.\d{2}\.\d{2})", period_raw)
    if len(dm) < 2:
        return period_raw
    label = V2_PERIOD_LABEL_BY_COURSE.get(class_id or "")
    if label is None:
        hm = _re.search(r"총\s*(\d+)\s*시간", period_raw)
        d1 = datetime.strptime(dm[0], "%Y.%m.%d")
        d2 = datetime.strptime(dm[1], "%Y.%m.%d")
        days = (d2 - d1).days
        months = max(1, -(-days // 30))  # ceil(days/30) — 부분월도 1개월로 올림
        label = f"{months}개월" + (f" ({hm.group(1)}시간)" if hm else "")
    return f"{dm[0]} ~ {dm[1]} · {label}"


def _v2_render_edu(class_id: str | None, common_blocks: dict[str, str], bi: dict) -> str:
    edu_md = common_blocks.get("부트캠프 교육 이수 내역", "")
    bc_badge = (bi.get("bootcamp_name", "") or "").split(" — ")[0].split(" (")[0].strip()
    bname_m = _re.search(r"^###\s*(.+)$", edu_md, _re.M)
    bname = bname_m.group(1).strip() if bname_m else bc_badge
    period_m = _re.search(r"\*\*교육 기간:\*\*\s*(.+)", edu_md)
    period_raw = period_m.group(1).strip() if period_m else ""
    period = _v2_format_period(class_id, period_raw)

    tags = V2_CURRICULUM_TAGS_BY_COURSE.get(class_id) if class_id else None
    if tags is None:
        tags = _v2_derive_curriculum_tags(edu_md) or []
    tag_html = "".join(f'<span class="skill-tag">{_v2_esc(t)}</span>' for t in tags)
    intro = _v2_intro_text(class_id, bi)

    return f'''<section><h2>교육 이수 내역</h2>
<h3>{_v2_esc(bname)}</h3>
<div class="edu-meta">{_v2_esc(period)}</div>
<p style="font-size:14px;color:#555;margin:4px 0 14px;">{_v2_esc(intro)}</p>
<div class="skill-tags">{tag_html}</div>
<div class="self-study"><strong>학습 특징</strong> — 팀 스크럼·주 2회 현직자 피드백, 데일리 코드 리뷰, TIL 챌린지, IntelliJ·Claude AI 지원 바이브 코딩 환경</div>
</section>'''


def _render_html_v2(ext: dict, prof: dict, content: dict, class_id: str | None) -> str:
    """미래이력서 HTML V2. 7섹션: 상단·Summary·보유기술·핵심역량·학력·프로젝트경험·교육이수·인턴십.

    원본: temp/render_v2.py 프로토타입(샘플 지원자 A/BEJV27 대상, 브라우저 QA로 렌더 버그 2건
    수정 완료). class_id별 커스터마이즈는 위 V2_*_BY_COURSE dict + 제네릭 fallback 참조."""
    secs = {s["title"]: s["content"] for s in content["sections"]}
    pi = ext["personal_info"]
    bi = ext["bootcamp_info"]
    common_blocks = load_common_blocks(class_id)
    log_common_block_status(class_id, common_blocks, context="_render_html_v2")

    phone = str(pi.get("phone", ""))
    if len(phone) == 10:
        phone = "0" + phone
    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    headline = content.get("headline", "")
    summary = content.get("career_objective", "")
    badge = (bi.get("bootcamp_name", "") or "").split(" — ")[0].split(" (")[0].strip()
    track = (bi.get("track", "") or "").strip()

    skills_html = _v2_render_skills(secs, prof, class_id)
    core_html = f'<section><h2>핵심 역량 및 활동</h2>{_v2_md_to_html(secs.get("핵심 역량 및 활동", ""))}</section>'
    # 학력 슬롯 — 개인 배경 섹션(학생=학력, 전향자=커리어 전환/실무 경력 등)을 원본 제목 그대로 렌더
    edu_bg_html = "".join(
        f'<section><h2>{_v2_esc(s.get("title", "학력"))}</h2>{_v2_md_to_html(s.get("content", ""))}</section>'
        for s in _v2_background_sections(content)
    )
    # 프로젝트 = 과정 공통 고정 블록(전원 동일). 지원자별 파싱 폐기 (포맷 취약성 제거)
    projects_html = _v2_render_projects(common_blocks)
    curri_html = _v2_render_edu(class_id, common_blocks, bi)
    intern_md = common_blocks.get("인턴십", "").replace(" (우수 수료자 대상 추천서 제공)", "")
    intern_html = f'<section><h2>인턴십</h2>{_v2_md_to_html(intern_md)}</section>'

    doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_v2_esc(pi['name'])} — 미래이력서 | Likelion</title>
<style>{_v2_css()}</style>
</head>
<body>
<div class="resume">
    <div class="header">
        <h1>{_v2_esc(pi['name'])}</h1>
        <div class="headline">{_v2_esc(headline)}</div>
        <div class="contact">
            <span>{_v2_esc(pi.get('email', ''))}</span>
            <span>{_v2_esc(phone)}</span>
        </div>
        <div class="bootcamp-badge">{_v2_esc(badge)}{' &mdash; ' + _v2_esc(track) if track else ''}</div>
    </div>
    <div class="body">
        <div class="summary">{_v2_esc(summary)}</div>
        {skills_html}
        {core_html}
        {projects_html}
        {edu_bg_html}
        {curri_html}
        {intern_html}
    </div>
    <div class="footer">
        <div>본 이력서는 {_footer_bootcamp_name(bi)} 수료 후 예상 역량을 기반으로 작성되었습니다.</div>
        <div>Edited by <span class="likelion">Likelion</span></div>
    </div>
</div>
</body>
</html>"""
    return doc


def _render_md_v2(ext: dict, prof: dict, content: dict, class_id: str | None) -> str:
    """미래이력서 Markdown V2 — HTML V2와 동일한 7섹션·순서를 마크다운으로 미러링.

    HTML V2(render_v2.py 프로토타입)엔 MD 버전이 없었다 — 이번 프로덕션 이관에서 신규 설계
    (2026-08-05). 헤더 #, 섹션 ##, 보유기술은 그룹별 소제목+콤마 나열, 프로젝트는 카드 대신
    불릿, 학력→프로젝트경험 순서는 HTML V2와 동일하게 유지."""
    secs = {s["title"]: s["content"] for s in content["sections"]}
    pi = ext["personal_info"]
    bi = ext["bootcamp_info"]
    common_blocks = load_common_blocks(class_id)
    log_common_block_status(class_id, common_blocks, context="_render_md_v2")

    phone = str(pi.get("phone", ""))
    if len(phone) == 10:
        phone = "0" + phone
    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    badge = (bi.get("bootcamp_name", "") or "").split(" — ")[0].split(" (")[0].strip()
    track = (bi.get("track", "") or "").strip()

    lines: list[str] = []

    # 헤더
    lines.append(f"# {pi['name']}")
    lines.append("")
    contact = [c for c in [pi.get("email", ""), phone] if c]
    if contact:
        lines.append(" | ".join(contact))
    lines.append(f"**{badge}{' — ' + track if track else ''}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(content.get("career_objective", ""))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 보유 기술
    lines.append("## 보유 기술")
    lines.append("")
    for gname, items in _v2_skill_render_groups(secs, class_id):
        items = items[:6]
        if not items:
            continue
        lines.append(f"### {gname}")
        lines.append(", ".join(items))
        lines.append("")
    soft = prof.get("soft_skills", [])[:3]
    if soft:
        lines.append("### Soft Skills")
        lines.append(", ".join(soft))
        lines.append("")
    lines.append("*※ 부트캠프 과정에서 습득 예정*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 핵심 역량 및 활동
    lines.append("## 핵심 역량 및 활동")
    lines.append("")
    lines.append(secs.get("핵심 역량 및 활동", ""))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 프로젝트 경험
    lines.append("## 프로젝트 경험 *(수료 후 예상)*")
    lines.append("")
    for p in _v2_parse_projects(common_blocks.get("프로젝트 경험", "")):
        header = f"### {p['title']}" + (f" — {p['meta']}" if p["meta"] else "")
        lines.append(header)
        if p["overview"]:
            lines.append(f"- 개요: {p['overview']}")
        if p["role"]:
            lines.append(f"- 역할: {p['role']}")
        if p["tech"]:
            lines.append(f"- 기술: {p['tech']}")
        if p["result"]:
            lines.append(f"- 성과: {p['result']}")
        lines.append("")
    lines.append("---")
    lines.append("")

    # 학력 슬롯 — 개인 배경 섹션(학생=학력, 전향자=커리어 전환/실무 경력 등)을 원본 제목 그대로
    for s in _v2_background_sections(content):
        lines.append(f"## {s.get('title', '학력')}")
        lines.append("")
        lines.append(s.get("content", ""))
        lines.append("")
        lines.append("---")
        lines.append("")

    # 교육 이수 내역
    edu_md = common_blocks.get("부트캠프 교육 이수 내역", "")
    bname_m = _re.search(r"^###\s*(.+)$", edu_md, _re.M)
    bname = bname_m.group(1).strip() if bname_m else badge
    period_m = _re.search(r"\*\*교육 기간:\*\*\s*(.+)", edu_md)
    period_raw = period_m.group(1).strip() if period_m else ""
    period = _v2_format_period(class_id, period_raw)
    tags = V2_CURRICULUM_TAGS_BY_COURSE.get(class_id) if class_id else None
    if tags is None:
        tags = _v2_derive_curriculum_tags(edu_md) or []
    intro = _v2_intro_text(class_id, bi)

    lines.append("## 교육 이수 내역")
    lines.append("")
    lines.append(f"### {bname}")
    lines.append(f"*{period}*")
    lines.append("")
    lines.append(intro)
    lines.append("")
    if tags:
        lines.append(", ".join(tags))
        lines.append("")
    lines.append("**학습 특징** — 팀 스크럼·주 2회 현직자 피드백, 데일리 코드 리뷰, TIL 챌린지, "
                  "IntelliJ·Claude AI 지원 바이브 코딩 환경")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 인턴십
    intern_md = common_blocks.get("인턴십", "").replace(" (우수 수료자 대상 추천서 제공)", "")
    lines.append("## 인턴십")
    lines.append("")
    lines.append(intern_md)
    lines.append("")

    # 푸터
    lines.append("---")
    lines.append("")
    lines.append(f"*본 이력서는 {_footer_bootcamp_name(bi)} 수료 후 예상 역량을 기반으로 작성되었습니다.*")
    lines.append("*Edited by **Likelion***")
    lines.append("")

    return "\n".join(lines)


def render_md(ext: dict, prof: dict, content: dict, class_id: str | None = None) -> str:
    """이력서 스타일 Markdown 생성.

    class_id가 V2_COURSES에 있으면 _render_md_v2()로 위임한다 (7섹션 V2 구조).
    그 외(V1) — class_id가 주어지고 templates/bootcamp_common/{class_id}.md 가 존재하면,
    부트캠프 교육 이수 내역/기업 연계 프로젝트 경험/멘토링 및 지원 프로그램/인턴십/취업 연계
    5개 섹션을 LLM 생성분 대신 과정 공통 고정 블록으로 병합한다 (merge_common_blocks).
    파일이 없으면(과거 과정) sections가 그대로 반환되어 기존 동작과 동일하다."""
    if class_id in V2_COURSES:
        return _render_md_v2(ext, prof, content, class_id)

    pi = ext["personal_info"]
    bi = ext["bootcamp_info"]
    sections = sorted(content["sections"], key=lambda s: s.get("order", 0))
    sections = merge_common_blocks(sections, class_id)

    # ── 하드스킬 / 소프트스킬 추출 ──
    hard_skills_existing = prof.get("existing_competencies", [])
    soft_skills = prof.get("soft_skills", [])
    hard_skills_projected = prof.get("projected_competencies", [])

    lines: list[str] = []

    # 헤더
    lines.append(f"# {pi['name']}")
    lines.append("")
    contact = []
    if pi.get("email"):
        contact.append(pi["email"])
    if pi.get("phone"):
        phone = str(pi["phone"])
        if len(phone) == 10:
            phone = "0" + phone  # 앞자리 0 누락 보정
        if len(phone) == 11:
            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        contact.append(phone)
    if contact:
        lines.append(" | ".join(contact))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(convert_to_completion_form(strip_projected(content.get("career_objective", ""))))
    lines.append("")

    # Skills
    lines.append("---")
    lines.append("")
    lines.append("## Skills")
    lines.append("")

    if hard_skills_existing:
        lines.append("### 보유 역량")
        lines.append("")
        for sk in hard_skills_existing:
            lines.append(f"- {sk}")
        lines.append("")

    if hard_skills_projected:
        lines.append("### 습득 역량")
        lines.append("")
        for sk in hard_skills_projected:
            lines.append(f"- {sk}")
        lines.append("")

    if soft_skills:
        lines.append("### Soft Skills")
        lines.append("")
        for sk in soft_skills:
            lines.append(f"- {sk}")
        lines.append("")

    # 본문 섹션 (career_objective 제외)
    for sec in sections:
        if sec.get("section_id") == "career_objective":
            continue
        title = strip_projected(sec.get("title", ""))
        sec_content = strip_projected(sec.get("content", ""))
        lines.append("---")
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")
        lines.append(sec_content)
        lines.append("")

    # 부트캠프 하이라이트
    if content.get("bootcamp_highlight"):
        lines.append("---")
        lines.append("")
        lines.append(f"> {strip_projected(content['bootcamp_highlight'])}")
        lines.append("")

    # 푸터
    lines.append("---")
    lines.append("")
    lines.append(f"*본 이력서는 {_footer_bootcamp_name(bi)} 수료 후 예상 역량을 기반으로 작성되었습니다.*")
    lines.append("*Edited by **Likelion***")
    lines.append("")

    return "\n".join(lines)


def render_html(ext: dict, prof: dict, content: dict, class_id: str | None = None) -> str:
    """이력서 스타일 HTML 생성 — 브라우저에서 바로 열 수 있는 단일 파일.

    class_id가 V2_COURSES에 있으면 _render_html_v2()로 위임한다 (7섹션 V2 구조).
    그 외(V1) — class_id 병합 로직은 render_md와 동일 (merge_common_blocks 참조)."""
    if class_id in V2_COURSES:
        return _render_html_v2(ext, prof, content, class_id)

    pi = ext["personal_info"]
    bi = ext["bootcamp_info"]
    sections = sorted(content["sections"], key=lambda s: s.get("order", 0))
    sections = merge_common_blocks(sections, class_id)

    # 부트캠프 뱃지용 과정명 — 커리큘럼 부제/괄호 설명 제거 (예: "AI NLP 엔지니어 부트캠프 5기")
    _bc_badge = (bi.get("bootcamp_name", "") or "").split(" — ")[0].split(" (")[0].strip()

    # 배지 표시 문자열 — 그로스 마케팅 과정만 '…부트캠프 수료' 고정.
    # [2026-06-18] Hoya 요청: 그로스 마케팅 배지를 수료형으로 통일. 다른 과정(AIPNLP/BEJV 등)은 'name — track' 형식.
    # [2026-07-20] Hoya 요청: 기간 괄호((2026.08.05(수) 개강 ~ 6개월 과정 (총 960시간)) 등) 제거 — 과정명 — 트랙 까지만. GM06/BEJV27/CLD08 공통.
    if "그로스 마케팅" in (bi.get("bootcamp_name", "") or ""):
        _badge_text = "데이터·AI 기반 실무형 그로스 마케팅 부트캠프 수료"
    else:
        _track = (bi.get("track", "") or "").strip()
        _badge_text = f"{_bc_badge} &mdash; {_track}" if _track else _bc_badge

    hard_existing = prof.get("existing_competencies", [])
    soft_skills = prof.get("soft_skills", [])
    hard_projected = prof.get("projected_competencies", [])
    applicant_type = prof.get("applicant_type", "student")

    # 전화번호 포맷
    phone = str(pi.get("phone", ""))
    if len(phone) == 10:
        phone = "0" + phone  # 앞자리 0 누락 보정
    if len(phone) == 11:
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    # ── 섹션 HTML 생성 ──
    def md_to_html(text: str) -> str:
        """간단한 마크다운 → HTML 변환."""
        import re
        if not text:
            return ""

        def _cell_html(c: str) -> str:
            """테이블 셀 변환. '**주차**: 라벨' 형태(부트캠프 이수 표 1열)는
            주차와 ': 라벨'을 줄바꿈으로 분리한다(주차 위, 라벨 아래)."""
            m = re.match(r"^\*\*(.+?)\*\*:\s*(.+)$", c.strip())
            if m:
                return f"<strong>{m.group(1)}</strong><br>{m.group(2)}"
            return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", c)

        result_lines = []
        in_ul = False
        in_table = False
        table_rows = []

        for line in text.split("\n"):
            stripped = line.strip()

            # 테이블 처리
            if stripped.startswith("|") and stripped.endswith("|"):
                if not in_table:
                    in_table = True
                    table_rows = []
                # 구분선 행 스킵
                if all(c in "|-: " for c in stripped):
                    continue
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                table_rows.append(cells)
                continue
            elif in_table:
                # 테이블 종료
                result_lines.append('<table>')
                for i, row in enumerate(table_rows):
                    tag = "th" if i == 0 else "td"
                    converted = [_cell_html(c) for c in row]
                    result_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in converted) + "</tr>")
                result_lines.append("</table>")
                in_table = False
                table_rows = []

            if stripped.startswith("- ") or stripped.startswith("* "):
                if not in_ul:
                    result_lines.append("<ul>")
                    in_ul = True
                item = stripped[2:].strip()
                item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
                item = re.sub(r"\*(.+?)\*", r"<em>\1</em>", item)
                result_lines.append(f"<li>{item}</li>")
            else:
                if in_ul:
                    result_lines.append("</ul>")
                    in_ul = False
                if stripped.startswith("####"):
                    result_lines.append(f"<h4>{stripped[4:].strip()}</h4>")
                elif stripped.startswith("###"):
                    result_lines.append(f"<h3>{stripped[3:].strip()}</h3>")
                elif stripped.startswith("> "):
                    inner = stripped[2:]
                    inner = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", inner)
                    result_lines.append(f'<blockquote>{inner}</blockquote>')
                elif stripped:
                    formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
                    formatted = re.sub(r"\*(.+?)\*", r"<em>\1</em>", formatted)
                    result_lines.append(f"<p>{formatted}</p>")

        if in_ul:
            result_lines.append("</ul>")
        if in_table:
            result_lines.append('<table>')
            for i, row in enumerate(table_rows):
                tag = "th" if i == 0 else "td"
                converted = [_cell_html(c) for c in row]
                result_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in converted) + "</tr>")
            result_lines.append("</table>")

        return "\n".join(result_lines)

    sections_html = []
    for sec in sections:
        if sec.get("section_id") == "career_objective":
            continue
        # is_projected badge 제거 — 미래이력서는 완성형 실체
        sec_title = strip_projected(sec.get("title", ""))
        sec_content_html = md_to_html(strip_projected(sec.get("content", "")))
        sections_html.append(f"""
        <section>
            <h2>{sec_title}</h2>
            {sec_content_html}
        </section>""")

    # ── 스킬 태그 ──
    def skill_tags(skills: list[str], cls: str) -> str:
        return "".join(f'<span class="skill-tag {cls}">{s}</span>' for s in skills)

    skills_section = ""
    if hard_existing:
        skills_section += f"""
            <div class="skill-group">
                <h3>보유 역량</h3>
                <div class="skill-tags">{skill_tags(hard_existing, "existing")}</div>
            </div>"""
    if hard_projected:
        skills_section += f"""
            <div class="skill-group">
                <h3>습득 역량</h3>
                <div class="skill-tags">{skill_tags(hard_projected, "projected")}</div>
            </div>"""
    if soft_skills:
        skills_section += f"""
            <div class="skill-group">
                <h3>Soft Skills</h3>
                <div class="skill-tags">{skill_tags(soft_skills, "soft")}</div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{pi['name']} — 미래이력서 | Likelion</title>
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #1a1a1a;
    background: #f0f0f0;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}}

.resume {{
    max-width: 800px;
    margin: 40px auto;
    background: #fff;
    box-shadow: 0 2px 20px rgba(0,0,0,0.08);
    border-radius: 4px;
    overflow: hidden;
}}

/* ── Header ── */
.header {{
    background: linear-gradient(135deg, #FF7816 0%, #e06510 100%);
    color: #fff;
    padding: 48px 56px 40px;
    position: relative;
}}
.header::after {{
    content: 'FUTURE RESUME';
    position: absolute;
    top: 16px;
    right: 24px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    opacity: 0.5;
}}
.header h1 {{
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}}
.header .headline {{
    font-size: 16px;
    font-weight: 400;
    opacity: 0.9;
    margin-bottom: 16px;
    line-height: 1.5;
}}
.header .contact {{
    font-size: 14px;
    opacity: 0.85;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}}
.header .contact span::before {{
    margin-right: 4px;
}}
.bootcamp-badge {{
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    padding: 12px 20px;
    margin-top: 20px;
    font-size: 14px;
    font-weight: 500;
}}

/* ── Body ── */
.body {{
    padding: 40px 56px 48px;
}}

/* Summary */
.summary {{
    border-left: 4px solid #FF7816;
    padding: 20px 24px;
    background: #fef7f2;
    border-radius: 0 8px 8px 0;
    margin-bottom: 36px;
    font-size: 15px;
    line-height: 1.8;
    color: #333;
}}

/* Skills */
.skills-section {{
    margin-bottom: 36px;
}}
.skills-section > h2 {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    padding-bottom: 10px;
    border-bottom: 2px solid #FF7816;
    margin-bottom: 20px;
}}
.skill-group {{
    margin-bottom: 16px;
}}
.skill-group h3 {{
    font-size: 14px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}}
.skill-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}
.skill-tag {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}}
.skill-tag.existing {{
    background: #FF7816;
    color: #fff;
}}
.skill-tag.projected {{
    background: #fff3eb;
    color: #d45a00;
    border: 1px solid #ffd4b3;
}}
.skill-tag.soft {{
    background: #f0f0f0;
    color: #555;
}}

/* Sections */
section {{
    margin-bottom: 32px;
}}
section h2 {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    padding-bottom: 10px;
    border-bottom: 2px solid #FF7816;
    margin-bottom: 16px;
}}
section h3 {{
    font-size: 16px;
    font-weight: 700;
    color: #333;
    margin: 16px 0 8px;
}}
section h4 {{
    font-size: 14px;
    font-weight: 600;
    color: #555;
    margin: 12px 0 6px;
}}
section p {{
    font-size: 14.5px;
    color: #444;
    margin-bottom: 8px;
    line-height: 1.8;
}}
section ul {{
    margin: 8px 0 12px 20px;
    font-size: 14.5px;
    color: #444;
}}
section li {{
    margin-bottom: 6px;
    line-height: 1.7;
}}
section table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 13.5px;
    /* table-layout: auto(기본) — 내용 기반 컬럼 폭. 표마다 컬럼 성격이 달라
       고정%(fixed)를 강제하면 짧은 중간열은 과폭·긴 첫열은 세로로 밀림.
       세로 1글자 쌓임은 아래 word-break: keep-all 로 방지. (2026-07-01) */
}}
section th {{
    background: #f8f8f8;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #ddd;
}}
section td {{
    padding: 10px 14px;
    border-bottom: 1px solid #eee;
    color: #444;
    vertical-align: top;
}}
section th, section td {{
    word-break: keep-all;
    overflow-wrap: break-word;
}}
section blockquote {{
    border-left: 3px solid #FF7816;
    padding: 12px 16px;
    background: #fef7f2;
    border-radius: 0 6px 6px 0;
    margin: 12px 0;
    font-size: 14px;
    color: #555;
}}
.badge {{
    display: inline-block;
    background: #fff3eb;
    color: #d45a00;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    margin-left: 8px;
    vertical-align: middle;
}}

/* ── Footer ── */
.footer {{
    background: #fafafa;
    border-top: 1px solid #eee;
    padding: 24px 56px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #999;
}}
.footer .likelion {{
    font-weight: 700;
    color: #FF7816;
}}

@media print {{
    body {{ background: #fff; }}
    .resume {{ box-shadow: none; margin: 0; border-radius: 0; }}
    .header {{ padding: 32px 40px; }}
    .body {{ padding: 24px 40px; }}
    .footer {{ padding: 16px 40px; }}
}}
</style>
</head>
<body>
<div class="resume">
    <div class="header">
        <h1>{pi['name']}</h1>
        <div class="headline">{content.get('headline', '')}</div>
        <div class="contact">
            <span>{pi.get('email', '')}</span>
            <span>{phone}</span>
        </div>
        <div class="bootcamp-badge">
            {_badge_text}
        </div>
    </div>

    <div class="body">
        <div class="summary">
            {convert_to_completion_form(strip_projected(content.get('career_objective', '')))}
        </div>

        <div class="skills-section">
            <h2>Skills</h2>
            {skills_section}
        </div>

        {"".join(sections_html)}
    </div>

    <div class="footer">
        <div>본 이력서는 {_footer_bootcamp_name(bi)} 수료 후 예상 역량을 기반으로 작성되었습니다.</div>
        <div>Edited by <span class="likelion">Likelion</span></div>
    </div>
</div>
</body>
</html>"""

    return html


def generate_guide() -> str:
    """미래이력서 활용 가이드."""
    return """\
=====================================
  미래이력서 활용 가이드
  Edited by Likelion
=====================================

안녕하세요!
이 문서는 부트캠프 수료 후 작성 가능한 이력서를
미리 확인할 수 있도록 Likelion이 준비한 자료입니다.

함께 제공된 파일은 두 종류입니다:
  1. .md 파일  — 텍스트 기반 이력서 (편집용)
  2. .html 파일 — 브라우저에서 바로 열어보는 이력서 (열람용)


[이렇게 사용해보세요]
-------------------------------------

1. HTML 파일로 내 미래이력서 확인하기
   - .html 파일을 더블클릭하면 브라우저에서 바로 열립니다.
   - 디자인이 적용된 상태로 내 미래 역량을 한눈에 볼 수 있습니다.

2. MD 파일로 직접 편집하기
   - .md 파일을 메모장, VS Code 등으로 열어 자유롭게 수정할 수 있습니다.
   - Notion에 복사·붙여넣기하면 서식이 자동 적용됩니다.

3. 수료 후 실제 이력서로 전환하기
   - 프로젝트 항목을 실제 결과물과 성과 지표로 업데이트하세요.
   - Skills 섹션에 실제 사용 경험과 숙련도를 추가하면 더 강력해집니다.


[내 이력서에 들어간 핵심 요소]
-------------------------------------

- Summary     : 나의 커리어 방향과 핵심 가치를 한 문단으로
- Skills      : 보유 역량 + 습득 역량 + 소프트스킬
- Education   : 학력 + 부트캠프 교육 이력
- Projects    : 부트캠프 프로젝트 포트폴리오
- Experience  : 기존 경력 또는 활동 이력


[MD 파일 활용법]
-------------------------------------

방법 1 — Notion에 붙여넣기
   .md 파일 전체 복사(Ctrl+A → Ctrl+C) 후
   Notion 페이지에 붙여넣기하면 서식 자동 적용

방법 2 — GitHub 포트폴리오
   GitHub 저장소에 업로드하면 자동 렌더링
   README.md로 활용하면 포트폴리오 홈 역할

방법 3 — VS Code 미리보기
   VS Code에서 Ctrl+Shift+V로 실시간 미리보기

방법 4 — PDF 변환
   온라인 도구(dillinger.io 등)에서 PDF/HTML 변환 가능


[주의사항]
-------------------------------------

- 실제 취업 지원 시 프로젝트 결과물과 성과 지표를 업데이트하세요.
- 개인정보(이메일, 연락처) 포함 — 공유 시 주의하세요.


-------------------------------------
Likelion | 멋쟁이사자처럼
=====================================
"""


def _load_application_emails(data_root: Path) -> dict[str, dict[str, str]]:
    """원본 지원서 CSV에서 이름 → {가입이메일, 지원서이메일} 매핑 로드.

    data/sample/ 하위의 가장 최신 CSV를 자동 탐색한다.
    """
    import glob as _glob

    import pandas as pd

    # data/sample/ 내 지원서 CSV 탐색 (최신순)
    csv_candidates = sorted(
        _glob.glob(str(data_root / "data" / "sample" / "*.csv"))
        + _glob.glob(str(data_root / "data" / "*.csv")),
        key=lambda p: Path(p).stat().st_mtime,
        reverse=True,
    )

    mapping: dict[str, dict[str, str]] = {}
    for csv_path in csv_candidates:
        try:
            df = pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="cp949")

        cols = list(df.columns)
        # 이름 컬럼 탐색
        name_col = None
        for c in cols:
            if "가입 이름" in str(c) or c == "이름":
                name_col = c
                break
        if name_col is None:
            continue

        # 이메일 컬럼 탐색
        signup_email_col = None
        app_email_col = None
        for c in cols:
            if "가입 이메일" in str(c) or c == "가입이메일":
                signup_email_col = c
            elif "지원서 이메일" in str(c) or c == "지원서이메일":
                app_email_col = c

        if signup_email_col is None and app_email_col is None:
            continue

        for _, row in df.iterrows():
            name = str(row.get(name_col, "")).strip()
            if not name:
                continue
            mapping[name] = {
                "가입이메일": str(row.get(signup_email_col, "")).strip() if signup_email_col else "",
                "지원서이메일": str(row.get(app_email_col, "")).strip() if app_email_col else "",
            }
        break  # 첫 매칭 CSV만 사용

    return mapping


def generate_contact_csv(output_dir: Path, outputs_base: Path) -> Path:
    """부트캠프 전체 하위 폴더를 스캔하여 이전+오늘 전체 배포목록 CSV 생성.

    outputs_base(=outputs/kdt-cld-7th/) 하위 모든 날짜 폴더에서
    미래이력서가 존재하는 사람의 정보를 통합하여 오늘 폴더에 CSV 저장.
    → 매 실행마다 이전 명단 + 신규 명단이 합산된 전체 목록 생성.
    """
    rows: list[dict] = []
    seen_names: set[str] = set()

    # 1) outputs_base 하위 전체 날짜 폴더에서 미래이력서 수집
    resume_names: set[str] = set()
    name_to_date_dir: dict[str, str] = {}  # 이름 → 생성된 날짜 폴더명
    for date_dir in sorted(outputs_base.iterdir()):
        if not date_dir.is_dir():
            continue
        for f in date_dir.iterdir():
            if f.is_file() and f.name.endswith("_미래이력서.md"):
                name = f.name.replace("_미래이력서.md", "")
                resume_names.add(name)
                name_to_date_dir[name] = date_dir.name  # 최신 날짜로 덮어씀

    # 2) 원본 CSV에서 가입이메일 / 지원서이메일 로드
    # outputs_base가 outputs/kdt-cld-7th/ 형태일 수 있으므로 프로젝트 루트 탐색
    project_root = outputs_base
    while project_root.name != "resume-pipeline" and project_root != project_root.parent:
        project_root = project_root.parent
    if project_root.name != "resume-pipeline":
        project_root = outputs_base.parent  # fallback
    email_map = _load_application_emails(project_root)

    # 3) intermediate 데이터에서 전화번호/유형 추출 (전체 날짜 폴더)
    # 신규 구조: 결과 폴더(outputs_base/{date}/) 및 _logs 폴더(_logs/{class_id}/{date}/)를 모두 탐색
    name_to_extracted: dict[str, dict] = {}
    name_to_profile: dict[str, dict] = {}
    _logs_base = outputs_base.parent.parent / "_logs" / outputs_base.name \
        if outputs_base.parent.name != "_logs" else outputs_base
    _inter_search_bases = [outputs_base]
    if _logs_base.is_dir() and _logs_base != outputs_base:
        _inter_search_bases.append(_logs_base)
    for _search_base in _inter_search_bases:
        for date_dir in sorted(_search_base.iterdir()):
            inter = date_dir / "intermediate"
            if not inter.is_dir():
                continue
            for f in inter.iterdir():
                if f.name.endswith("_1_extracted.json"):
                    name = f.name.replace("_1_extracted.json", "")
                    name_to_extracted[name] = json.loads(f.read_text("utf-8"))
                elif f.name.endswith("_2_profile.json"):
                    name = f.name.replace("_2_profile.json", "")
                    name_to_profile[name] = json.loads(f.read_text("utf-8"))

    # 4) 전체 미래이력서 대상자를 CSV에 포함
    for name in sorted(resume_names):
        if name in seen_names:
            continue
        seen_names.add(name)

        ext = name_to_extracted.get(name, {})
        prof = name_to_profile.get(name, {})
        pi = ext.get("personal_info", {})
        emails = email_map.get(name, {})

        phone = str(pi.get("phone", ""))
        if len(phone) == 10:
            phone = "0" + phone  # 앞자리 0 누락 보정
        if len(phone) == 11:
            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

        applicant_type = prof.get("applicant_type", "")
        type_labels = {
            "career_changer": "전직자",
            "student": "학생",
            "experienced": "경력자",
        }

        rows.append({
            "이름": name,
            "가입 이메일": emails.get("가입이메일", pi.get("email", "")),
            "지원서 이메일": emails.get("지원서이메일", ""),
            "전화번호": phone,
            "지원자유형": type_labels.get(applicant_type, applicant_type),
            "생성일": name_to_date_dir.get(name, ""),
            "MD파일": f"{name}_미래이력서.md",
            "HTML파일": f"{name}_미래이력서.html",
        })

    fieldnames = ["이름", "가입 이메일", "지원서 이메일", "전화번호", "지원자유형", "생성일", "MD파일", "HTML파일"]
    csv_path = output_dir / "미래이력서_배포목록.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def _find_eligible_names(outputs_base: Path) -> list[tuple[str, Path]]:
    """outputs/ 전체를 스캔하여 Phase 3 완료(_3_content.json 존재) &&
    미래이력서 미생성인 이름과 intermediate 경로를 반환.
    신규 구조: intermediate는 _logs/{class_id}/{date}/intermediate 에도 존재."""
    # 1) intermediate에서 _3_content.json 보유 이름 수집
    candidates: dict[str, Path] = {}  # name -> intermediate dir
    _logs_base = outputs_base.parent.parent / "_logs" / outputs_base.name \
        if outputs_base.parent.name != "_logs" else outputs_base
    _inter_search_bases = [outputs_base]
    if _logs_base.is_dir() and _logs_base != outputs_base:
        _inter_search_bases.append(_logs_base)
    for _search_base in _inter_search_bases:
        for date_dir in sorted(_search_base.iterdir()):
            inter = date_dir / "intermediate"
            if not inter.is_dir():
                continue
            for f in inter.iterdir():
                if f.name.endswith("_3_content.json"):
                    name = f.name.replace("_3_content.json", "")
                    candidates[name] = inter  # 최신 날짜가 덮어씀

    # 2) 이미 미래이력서가 존재하는 이름 제외
    already: set[str] = set()
    for date_dir in outputs_base.iterdir():
        if not date_dir.is_dir():
            continue
        for f in date_dir.iterdir():
            if f.name.endswith("_미래이력서.html") or f.name.endswith("_미래이력서.md"):
                already.add(f.name.rsplit("_", 1)[0])

    eligible = [(n, d) for n, d in candidates.items() if n not in already]
    return eligible


def main():
    import argparse

    parser = argparse.ArgumentParser(description="미래이력서 생성 (MD + HTML)")
    parser.add_argument("--data-dir", default=None, help="intermediate 디렉토리 경로 (미지정 시 자동 스캔)")
    parser.add_argument("--names", nargs="*", default=None, help="생성할 이름 목록 (미지정 시 미생성 대상 자동 탐색)")
    parser.add_argument("--output-dir", default=None, help="출력 디렉토리 (미지정 시 outputs/오늘날짜)")
    parser.add_argument("--bootcamp-code", default=None,
                        help="부트캠프 코드 (예: kdt-cld-7th). outputs/{code}/ 하위에 출력")
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    outputs_root = Path("outputs")
    if args.bootcamp_code:
        outputs_base = outputs_root / args.bootcamp_code
    else:
        outputs_base = outputs_root
    outputs_base.mkdir(parents=True, exist_ok=True)

    output_dir = Path(args.output_dir) if args.output_dir else outputs_base / today
    output_dir.mkdir(parents=True, exist_ok=True)

    # 대상 결정
    if args.names and args.data_dir:
        # 명시 지정 모드
        targets = [(n, Path(args.data_dir)) for n in args.names]
    elif args.names:
        # 이름만 지정 → intermediate 자동 탐색 (결과 폴더 + _logs 폴더 모두 탐색)
        candidates: dict[str, Path] = {}
        _logs_base_m = outputs_base.parent.parent / "_logs" / outputs_base.name \
            if outputs_base.parent.name != "_logs" else outputs_base
        _search_bases_m = [outputs_base]
        if _logs_base_m.is_dir() and _logs_base_m != outputs_base:
            _search_bases_m.append(_logs_base_m)
        for _sb in _search_bases_m:
            for date_dir in sorted(_sb.iterdir()):
                inter = date_dir / "intermediate"
                if not inter.is_dir():
                    continue
                for f in inter.iterdir():
                    if f.name.endswith("_3_content.json"):
                        name = f.name.replace("_3_content.json", "")
                        candidates[name] = inter
        targets = [(n, candidates[n]) for n in args.names if n in candidates]
    else:
        # 자동 모드: 미생성 대상 탐색
        targets = _find_eligible_names(outputs_base)

    if not targets:
        print("미래이력서 생성 대상이 없습니다 (모두 생성 완료 또는 intermediate 데이터 없음).")
        return

    print(f"생성 대상: {len(targets)}명 — {', '.join(n for n, _ in targets)}")

    for name, data_dir in targets:
        print(f"\n{'='*50}")
        print(f" {name} 미래이력서 생성")
        print(f"{'='*50}")

        ext, prof, content = load_data(name, data_dir)

        # class_id = --bootcamp-code (outputs/{class_id}/ 구조와 동일 값).
        # 미지정 시 None → merge_common_blocks가 빈 dict 반환해 기존 동작 그대로.
        class_id = args.bootcamp_code

        # MD 생성
        md = render_md(ext, prof, content, class_id=class_id)
        md_path = output_dir / f"{name}_미래이력서.md"
        md_path.write_text(md, encoding="utf-8")
        print(f"  MD:   {md_path} ({md_path.stat().st_size:,} bytes)")

        # HTML 생성
        html = render_html(ext, prof, content, class_id=class_id)
        html_path = output_dir / f"{name}_미래이력서.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"  HTML: {html_path} ({html_path.stat().st_size:,} bytes)")

    # 활용 가이드
    guide = generate_guide()
    guide_path = output_dir / "미래이력서_활용가이드.txt"
    guide_path.write_text(guide, encoding="utf-8")
    print(f"\n  가이드: {guide_path}")

    # 배포용 CSV (이메일 목록)
    csv_path = generate_contact_csv(output_dir, outputs_base)
    csv_count = sum(1 for _ in open(csv_path, encoding="utf-8-sig")) - 1  # header 제외
    print(f"  CSV:  {csv_path} ({csv_count}명)")

    print(f"\n{'='*50}")
    print(f"완료! 출력: {output_dir}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
