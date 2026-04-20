"""
[Agent 1] 조사 에이전트.
depth0(메인) → depth1(부트캠프 상세) 링크만 수집 후 LLM 구조화.
"""
import json
import asyncio
import anthropic
from config import COMPETITORS, OWN_COMPANY, RESEARCH_MODEL, ANTHROPIC_API_KEY
from utils.scraper import fetch_multiple_sites
from utils.cache import load_cache, save_cache, diff_bootcamps

# LLM에 넘길 텍스트 최대 길이 (depth1 페이지 합산)
MAX_TEXT_CHARS = 8000

EXTRACTION_PROMPT = """
KDT 부트캠프 사이트 텍스트에서 현재 모집중이거나 모집 예정인 과정만 추출하세요.

사이트: {site_name} ({url})

## 추출 항목 (각 과정마다)
- name: 과정명
- track: 기술 트랙 (웹 풀스택/AI·ML/데이터/클라우드/모바일 등)
- duration: 교육 기간
- start_date: 시작/모집 일정 (없으면 null)
- status: "모집중" | "모집예정" | "모집마감" | "상시모집"
- features: 주요 특장점 (최대 3개)
- curriculum_keywords: 핵심 기술스택·키워드 (최대 5개)
- employment_support: 취업 지원 내용 요약 (없으면 null)
- price_info: 국비지원 여부·비용 정보

## 텍스트
{text}

JSON 배열만 반환. 과정이 없으면 [].
"""


def _build_text(scraped: dict) -> str:
    """depth0 + depth1 텍스트를 합쳐 MAX_TEXT_CHARS 이내로 자른다."""
    parts = []
    main = scraped.get("main_text", "")
    if main and not main.startswith("[SCRAPE_ERROR"):
        parts.append(f"[메인 페이지]\n{main[:2000]}")

    for dp in scraped.get("detail_pages", []):
        text = dp.get("text", "")
        if text and not text.startswith("[SCRAPE_ERROR"):
            parts.append(f"[상세: {dp['url']}]\n{text[:1500]}")

    combined = "\n\n".join(parts)
    return combined[:MAX_TEXT_CHARS]


async def _extract_bootcamps(site_name: str, url: str, scraped: dict) -> list[dict]:
    text = _build_text(scraped)
    if len(text.strip()) < 50:
        print(f"[Researcher] 텍스트 부족, 건너뜀: {site_name}", flush=True)
        return []

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    msg = await client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(
            site_name=site_name, url=url, text=text
        )}],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        print(f"[Researcher] JSON 파싱 실패 ({site_name}): {raw[:80]}", flush=True)
        return []


async def run() -> dict:
    all_sites = {**COMPETITORS, "_own": OWN_COMPANY}

    # 1단계: 순차 스크래핑 (depth0 → depth1)
    urls = [info["url"] for info in all_sites.values()]
    print(f"[Researcher] {len(urls)}개 사이트 스크래핑 (depth0+depth1)...", flush=True)
    scraped_map = await fetch_multiple_sites(urls)

    for key, info in all_sites.items():
        dp_count = len(scraped_map.get(info["url"], {}).get("detail_pages", []))
        print(f"  {info['name']}: 상세 페이지 {dp_count}개 수집", flush=True)

    # 2단계: LLM 추출 (병렬)
    print("[Researcher] LLM 구조화 추출 중...", flush=True)
    key_order = list(all_sites.keys())
    extract_tasks = [
        _extract_bootcamps(
            all_sites[k]["name"],
            all_sites[k]["url"],
            scraped_map.get(all_sites[k]["url"], {})
        )
        for k in key_order
    ]
    extracted_all = await asyncio.gather(*extract_tasks)

    # 3단계: 결과 조립
    competitor_results = []
    own_bootcamps = []

    for i, key in enumerate(key_order):
        bootcamps = extracted_all[i]
        info = all_sites[key]

        if key == "_own":
            own_bootcamps = bootcamps
            print(f"  [자사] {info['name']}: {len(bootcamps)}개 과정", flush=True)
            continue

        cache = load_cache(key)
        old_bootcamps = cache.get("bootcamps", []) if cache else []
        diff = diff_bootcamps(old_bootcamps, bootcamps)
        save_cache(key, {"name": info["name"], "url": info["url"], "bootcamps": bootcamps})

        print(
            f"  {info['name']}: {len(bootcamps)}개 과정 | "
            f"신규 {len(diff['added'])} / 종료 {len(diff['removed'])} / 변경 {len(diff['changed'])}",
            flush=True
        )
        competitor_results.append({
            "competitor_key": key,
            "name": info["name"],
            "url": info["url"],
            "all_bootcamps": bootcamps,
            "diff": diff,
            "is_first_run": cache is None,
        })

    return {
        "competitors": competitor_results,
        "own_bootcamps": own_bootcamps,
    }
