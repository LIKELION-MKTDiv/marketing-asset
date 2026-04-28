import os
import sys
import pickle
import asyncio
import re

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from playwright.async_api import async_playwright

# ── 인증 설정 ──────────────────────────────────────────────
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'google_credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

# ── 시트 설정 ──────────────────────────────────────────────
SPREADSHEET_ID = '1vuMaG09jHMtlHu8RQa1oiWgoPXIG-RAJWSOX92nvpFc'
SHEET_NAME = '오늘 공부 후기, 블로그 챌린지 26-03회차'
URL_COL = 'A'       # URL 열
COURSE_COL = 'B'    # 교육과정명 열
PERIOD_COL = 'C'    # 기수 열
TITLE_COL = 'K'     # 제목 결과 열
TAG_COL = 'L'       # 해시태그 결과 열
NOTE_COL = 'M'      # 비고 열
START_ROW = 55      # 헤더 제외 데이터 시작 행

# ── 교육과정 스킬 매핑 ──────────────────────────────────────
COURSE_SKILL_MAP = {
    '그로스마케팅': ['#마케팅', '#그로스마케팅', '#growth', '#ga4', '#seo', '#콘텐츠마케팅'],
    '백엔드': ['#java', '#spring', '#python', '#django', '#fastapi', '#node.js', '#springboot', '#mysql', '#postgresql'],
    '자바': ['#java', '#springboot', '#spring', '#jpa', '#mysql'],
    '프론트엔드': ['#html', '#css', '#javascript', '#typescript', '#react', '#vue', '#next.js'],
    '안드로이드': ['#android', '#kotlin', '#java', '#androidstudio'],
    '클라우드': ['#aws', '#cloud', '#docker', '#kubernetes', '#devops', '#linux', '#terraform'],
    'aws': ['#aws', '#cloud', '#docker', '#kubernetes', '#devops', '#linux', '#terraform'],
    '유니티': ['#unity', '#c#', '#gamedev', '#게임개발'],
    '게임': ['#unity', '#c#', '#gamedev', '#게임개발'],
    'ux': ['#figma', '#ux', '#ui', '#디자인', '#prototyping'],
    'ui': ['#figma', '#ux', '#ui', '#디자인', '#prototyping'],
    '디자인': ['#figma', '#ux', '#ui', '#디자인'],
    'ai': ['#python', '#ai', '#machinelearning', '#deeplearning', '#llm', '#pytorch', '#tensorflow'],
    'pm': ['#pm', '#기획', '#productmanagement', '#애자일', '#scrum'],
}

REQUIRED_HASHTAG = '#멋쟁이사자처럼후기'
REQUIRED_TITLE_KEYWORD = '멋쟁이사자처럼부트캠프'
NOTION_DOMAIN = 'notion.so'

# 인정하지 않는 플랫폼 (X 처리)
INVALID_PLATFORMS = {
    'notion.so': '노션 페이지 사용 — 개인 블로그 포스팅 필요',
    'github.io': 'GitHub 페이지 사용 — 개인 블로그 포스팅 필요',
    'github.com': 'GitHub 페이지 사용 — 개인 블로그 포스팅 필요',
    'oopy.io': 'Oopy 페이지 사용 — 개인 블로그 포스팅 필요',
}


# ── 구글 인증 ──────────────────────────────────────────────
def get_sheets_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)


# ── 시트 데이터 읽기 ───────────────────────────────────────
def read_rows(service):
    """A~C열 읽기: [(url, course_name, period), ...]"""
    range_name = f"'{SHEET_NAME}'!{URL_COL}{START_ROW}:{PERIOD_COL}"
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name
    ).execute()
    values = result.get('values', [])
    rows = []
    for row in values:
        url = row[0].strip() if len(row) > 0 else ''
        course = row[1].strip() if len(row) > 1 else ''
        period = row[2].strip() if len(row) > 2 else ''
        rows.append((url, course, period))
    return rows


# ── 시트에 결과 쓰기 ───────────────────────────────────────
def write_results(service, results):
    """results: [(row_index, title_result, tag_result, note), ...]"""
    data = []
    for row_idx, title_result, tag_result, note in results:
        data.append({
            'range': f"'{SHEET_NAME}'!{TITLE_COL}{row_idx}",
            'values': [[title_result]]
        })
        data.append({
            'range': f"'{SHEET_NAME}'!{TAG_COL}{row_idx}",
            'values': [[tag_result]]
        })
        data.append({
            'range': f"'{SHEET_NAME}'!{NOTE_COL}{row_idx}",
            'values': [[note]]
        })

    body = {'valueInputOption': 'RAW', 'data': data}
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()


# ── 인정 불가 플랫폼 확인 ──────────────────────────────────
def get_invalid_reason(url):
    """인정 불가 플랫폼이면 사유 반환, 아니면 None"""
    url_lower = url.lower()
    for domain, reason in INVALID_PLATFORMS.items():
        if domain in url_lower:
            return reason
    return None


# ── 제목 판별 ──────────────────────────────────────────────
def normalize(text):
    """공백, 특수문자 제거 후 소문자 변환"""
    return re.sub(r'[\s\-_\[\]\(\)\<\>]', '', text).lower()

def check_title(title, course_name=''):
    """(결과, 이유) 반환"""
    title_norm = normalize(title)
    # 띄어쓰기 순서 무관하게 브랜드명 체크 (멋쟁이사자처럼 + 부트캠프 둘 다 포함)
    has_brand = '멋쟁이사자처럼부트캠프' in title_norm or (
        '멋쟁이사자처럼' in title_norm and '부트캠프' in title_norm
    )

    if not has_brand:
        return 'X', f'제목: "{title}"'

    if course_name:
        if normalize(course_name) in title_norm:
            return 'O', ''

    for keyword in COURSE_SKILL_MAP.keys():
        if keyword in title_norm:
            return 'O', ''

    return '△', f'제목: "{title}" (교육과정명 미포함)'


# ── 해시태그 판별 ──────────────────────────────────────────
def check_hashtags(tags_text, course_name=''):
    """(결과, 이유) 반환"""
    tags_lower = normalize(tags_text)
    has_required = normalize(REQUIRED_HASHTAG) in tags_lower
    # 필수태그 외 다른 태그도 있는지 확인
    other_tags = tags_text.replace(REQUIRED_HASHTAG, '').strip()
    has_other = bool(other_tags)

    if has_required and has_other:
        return 'O', ''
    elif has_required and not has_other:
        return '△', f'{REQUIRED_HASHTAG}만 있고 다른 태그 없음'
    elif not has_required:
        return 'X', f'{REQUIRED_HASHTAG} 미포함 (태그: "{tags_text}")'


# ── 플랫폼별 크롤링 ────────────────────────────────────────
async def crawl_velog(page, url):
    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
    await page.wait_for_timeout(3000)
    title = await page.title()
    # 벨로그 태그는 href="/velog.io/tags/..." 패턴
    tag_elements = await page.query_selector_all('a[href*="velog.io/tags/"]')
    tags = []
    for el in tag_elements:
        text = (await el.inner_text()).strip()
        if text:
            tags.append(f'#{text}' if not text.startswith('#') else text)
    return title, ' '.join(tags)


async def crawl_tistory(page, url):
    await page.goto(url, wait_until='networkidle', timeout=30000)
    title = await page.title()
    tag_elements = await page.query_selector_all('.tag-list a, .tags a, a.tag, [class*="tag"] a')
    tags = []
    for el in tag_elements:
        text = await el.inner_text()
        text = text.strip()
        if text:
            tags.append(f'#{text}' if not text.startswith('#') else text)
    return title, ' '.join(tags)


async def crawl_naver(page, url):
    await page.goto(url, wait_until='networkidle', timeout=30000)
    # 네이버 블로그는 iframe 구조
    title = ''
    tags_text = ''

    # mainFrame iframe 접근
    frames = page.frames
    for frame in frames:
        if 'blog.naver.com' in frame.url and frame.url != url:
            try:
                t = await frame.title()
                if t:
                    title = t
                tag_els = await frame.query_selector_all('.post_tag a, .se-hashtag, [class*="tag"]')
                tags = []
                for el in tag_els:
                    text = await el.inner_text()
                    text = text.strip()
                    if text:
                        tags.append(f'#{text}' if not text.startswith('#') else text)
                tags_text = ' '.join(tags)
            except Exception:
                pass
            break

    if not title:
        title = await page.title()

    return title, tags_text


async def crawl_generic(page, url):
    await page.goto(url, wait_until='networkidle', timeout=30000)
    title = await page.title()
    # 일반적인 태그 선택자 시도
    tag_elements = await page.query_selector_all('[class*="tag"] a, .tags a, .hashtag')
    tags = []
    for el in tag_elements:
        text = await el.inner_text()
        text = text.strip()
        if text:
            tags.append(f'#{text}' if not text.startswith('#') else text)
    return title, ' '.join(tags)


async def crawl_url(browser, url):
    if not url or not url.startswith('http'):
        return '', ''

    page = await browser.new_page()
    try:
        if 'velog.io' in url:
            title, tags = await crawl_velog(page, url)
        elif 'tistory.com' in url:
            title, tags = await crawl_tistory(page, url)
        elif 'blog.naver.com' in url:
            title, tags = await crawl_naver(page, url)
        else:
            title, tags = await crawl_generic(page, url)
        return title, tags
    except Exception as e:
        print(f'  ⚠️  크롤링 실패: {url} — {e}')
        return '', ''
    finally:
        await page.close()


# ── 메인 ──────────────────────────────────────────────────
async def main():
    print('🔐 구글 시트 인증 중...')
    service = get_sheets_service()

    print('📋 행 데이터 읽는 중...')
    rows = read_rows(service)
    print(f'  → {len(rows)}개 행 발견\n')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for i, (url, course, period) in enumerate(rows):
            row_idx = START_ROW + i
            print(f'[{i+1}/{len(rows)}] {url[:60]}...' if len(url) > 60 else f'[{i+1}/{len(rows)}] {url}')
            if course:
                print(f'  교육과정: {course} {period}')

            if not url:
                write_results(service, [(row_idx, '-', '-', '')])
                continue

            invalid_reason = get_invalid_reason(url)
            if invalid_reason:
                print(f'  → 인정 불가 플랫폼 → X ({invalid_reason})')
                write_results(service, [(row_idx, 'X', 'X', invalid_reason)])
                continue

            title, tags = await crawl_url(browser, url)

            # 404 체크
            if '404' in title or 'not found' in title.lower():
                print(f'  → 404 삭제')
                write_results(service, [(row_idx, '삭제', '삭제', '404 삭제')])
                continue

            title_result, title_note = check_title(title, course)
            tag_result, tag_note = check_hashtags(tags, course)
            note = ' / '.join(filter(None, [title_note, tag_note]))

            print(f'  제목: {title[:50]}' if title else '  제목: (없음)')
            print(f'  태그: {tags[:80]}' if tags else '  태그: (없음)')
            print(f'  → K열: {title_result} / L열: {tag_result}' + (f' / M열: {note}' if note else ''))

            write_results(service, [(row_idx, title_result, tag_result, note)])

        await browser.close()

    print('✅ 완료!')


if __name__ == '__main__':
    asyncio.run(main())
