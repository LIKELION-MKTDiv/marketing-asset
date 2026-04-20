"""
Playwright 기반 웹 스크래퍼.
depth0: 메인 페이지에서 부트캠프 관련 링크 추출
depth1: 해당 링크(상세 페이지)만 스크래핑
"""
import asyncio
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright, Page

PAGE_TIMEOUT = 20_000
EXTRA_WAIT   = 2_000

# 부트캠프 상세 페이지로 볼 URL/텍스트 키워드
BOOTCAMP_URL_KEYWORDS = [
    "bootcamp", "boot-camp", "camp", "course", "track", "program",
    "curriculum", "cohort", "sprint", "kernel", "kdt",
    # 한글 포함 URL은 보통 인코딩되어 있어 텍스트 필터로
]
BOOTCAMP_TEXT_KEYWORDS = [
    "부트캠프", "캠프", "과정", "트랙", "커리큘럼", "코스",
    "국비", "취업", "개발자", "백엔드", "프론트엔드", "풀스택",
    "데이터", "AI", "클라우드", "DevOps", "앱", "모바일",
]
MAX_DEPTH1_PAGES = 10  # 상세 페이지 최대 수집 수


def _is_same_domain(base_url: str, link: str) -> bool:
    base = urlparse(base_url)
    target = urlparse(link)
    return target.netloc == "" or target.netloc == base.netloc


def _is_bootcamp_link(href: str, text: str) -> bool:
    href_lower = href.lower()
    text_lower = text.lower()
    for kw in BOOTCAMP_URL_KEYWORDS:
        if kw in href_lower:
            return True
    for kw in BOOTCAMP_TEXT_KEYWORDS:
        if kw in text_lower:
            return True
    return False


async def _fetch_text(page: Page, url: str) -> str:
    try:
        await page.goto(url, timeout=PAGE_TIMEOUT, wait_until="load")
        await page.wait_for_timeout(EXTRA_WAIT)
        return await page.inner_text("body")
    except Exception as e:
        return f"[SCRAPE_ERROR: {e}]"


async def fetch_depth0_and_depth1(base_url: str) -> dict:
    """
    depth0 메인 페이지 스크래핑 후
    부트캠프 관련 링크만 골라 depth1 페이지까지 수집.

    Returns:
        {
            "main_text": str,          # depth0 전체 텍스트
            "detail_pages": [          # depth1 상세 페이지들
                {"url": str, "text": str}
            ]
        }
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # depth0: 메인 페이지
        main_text = await _fetch_text(page, base_url)

        # 링크 추출
        try:
            raw_links = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => ({href: e.href, text: e.innerText.trim().slice(0,80)}))"
            )
        except Exception:
            raw_links = []

        # 부트캠프 관련 링크만 필터 (같은 도메인 + 키워드)
        candidate_urls = []
        seen = set()
        for link in raw_links:
            href = link.get("href", "")
            text = link.get("text", "")
            if (
                href
                and href not in seen
                and _is_same_domain(base_url, href)
                and href != base_url
                and not href.endswith((".pdf", ".png", ".jpg", ".zip"))
                and _is_bootcamp_link(href, text)
            ):
                seen.add(href)
                candidate_urls.append(href)

        # 상위 N개만 수집
        target_urls = candidate_urls[:MAX_DEPTH1_PAGES]

        # depth1: 상세 페이지 순차 수집 (rate limit 고려)
        detail_pages = []
        for url in target_urls:
            text = await _fetch_text(page, url)
            detail_pages.append({"url": url, "text": text})

        await browser.close()

    return {
        "main_text": main_text,
        "detail_pages": detail_pages,
    }


async def fetch_multiple_sites(urls: list[str]) -> dict[str, dict]:
    """여러 사이트를 순차적으로 depth0+depth1 스크래핑."""
    results = {}
    for url in urls:
        results[url] = await fetch_depth0_and_depth1(url)
    return results
