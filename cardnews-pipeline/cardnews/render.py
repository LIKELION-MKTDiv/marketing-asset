# -*- coding: utf-8 -*-
"""카드뉴스 렌더러: 브랜드 키트(brand.json) + 콘텐츠(spec.json) -> HTML -> PNG, 렌더 직후 자동 검수.

사용 (cardnews-pipeline 폴더에서):
  python -m cardnews.render --brand brands/likelion --spec examples/likelion-sample/spec.json --out out/likelion-sample

구조
  brand.json  브랜드 담당자가 한 번 채우는 값: 캔버스, 안전 여백, 색, 글자 크기 체계, 로고, 공통 요소, 검수 기준
  spec.json   콘텐츠마다 새로 쓰는 값: 슬라이드별 배경, 본문 HTML, 차트, 로고 색, 다음 장 티저
  render.py   두 파일을 합쳐 슬라이드마다 HTML을 만들고 Chromium(Playwright)으로 PNG를 찍는다
  audit.py    찍은 결과에서 여백 침범, 글자 크기 하한, 명암비를 측정한다

경로 규약
  spec 안의 {A}  = spec.json 옆 assets/ 폴더 (사진, 배경 플레이트)
  spec 안의 {B}  = 브랜드 폴더의 assets/ (로고, 패턴 등 브랜드 고정 자산)
"""
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

from PIL import Image

from . import audit, charts

HERE = Path(__file__).resolve().parent
CHART_RE = re.compile(r'\{\{chart:([\w-]+)\}\}')


def load_brand(brand_dir: Path) -> dict:
    f = brand_dir / 'brand.json'
    if not f.is_file():
        sys.exit(f'brand.json이 없습니다: {f}')
    b = json.loads(f.read_text(encoding='utf-8'))
    b.setdefault('canvas', {'width': 1080, 'height': 1350})
    b.setdefault('safe_area', {'top': 100, 'right': 100, 'bottom': 100, 'left': 100})
    b.setdefault('chrome', {})
    b.setdefault('audit', {})
    return b


def brand_css(b: dict) -> str:
    W, H = b['canvas']['width'], b['canvas']['height']
    s = b['safe_area']
    v = [f'--W:{W}px', f'--H:{H}px'] + [f'--safe-{k}:{s[k]}px' for k in ('top', 'right', 'bottom', 'left')]
    v += [f'--c-{k}:{c}' for k, c in b.get('colors', {}).items()]
    css = ':root{' + ';'.join(v) + '}\n'
    fam = b.get('fonts', {}).get('family', 'Pretendard')
    css += f"html,body,.card{{font-family:'{fam}',Pretendard,'Apple SD Gothic Neo','Malgun Gothic',sans-serif}}\n"
    # 글자 크기 체계: brand.json type의 키마다 .t-{키} 클래스를 만든다
    for key, t in b.get('type', {}).items():
        rule = [f"font-size:{t['size']}px", f"font-weight:{t.get('weight', 700)}",
                f"line-height:{t.get('line', 1.4)}", f"letter-spacing:{t.get('tracking', '-0.02em')}"]
        if 'color' in t:
            rule.append(f"color:{resolve_color(b, t['color'])}")
        css += f".t-{key}{{{';'.join(rule)}}}\n"
    return css


def resolve_color(b: dict, c: str) -> str:
    return b.get('colors', {}).get(c, c)


def prep_logos(b: dict, brand_dir: Path, out: Path) -> dict:
    """로고 원본의 투명 여백을 잘라 '잉크' 기준으로 맞춘다. 원본 캔버스 크기로 맞추면 실제 로고가 작아진다."""
    lg = b.get('logo') or {}
    res = {}
    dst = out / '_brand'
    dst.mkdir(parents=True, exist_ok=True)
    for variant, rel in (lg.get('files') or {}).items():
        src = brand_dir / rel
        if not src.is_file():
            print(f'  경고: 로고 파일 없음 {src}')
            continue
        im = Image.open(src).convert('RGBA')
        bbox = im.split()[3].getbbox()
        if bbox:
            im = im.crop(bbox)
        p = dst / f'logo_{variant}.png'
        im.save(p)
        res[variant] = p.resolve().as_uri()
    return res


def bg_html(bg, b: dict, A: str) -> str:
    if not bg:
        bg = {'kind': 'color', 'value': resolve_color(b, b.get('default_bg', 'bg'))}
    kind = bg.get('kind', 'color')
    val = str(bg.get('value', '')).replace('{A}', A)
    if kind in ('color', 'gradient'):
        return f"<div class='bgfill' style=\"background:{resolve_color(b, val)}\"></div>"
    src = str(bg.get('src', '')).replace('{A}', A)
    if not src.startswith(('file:', 'http')):
        src = f'{A}/{src}'
    pos = bg.get('position', 'center')
    mode = bg.get('mode', 'full')
    if kind == 'plate' or mode == 'plain':
        return f"<div class='photo' style=\"background-image:url('{src}');background-position:{pos}\"></div>"
    if mode == 'blur':
        return f"<div class='photo blur' style=\"background-image:url('{src}')\"></div><div class='shade'></div>"
    if mode == 'top':
        h = int(bg.get('height', 900))
        return (f"<div class='photo' style=\"background-image:url('{src}');background-position:{pos};bottom:auto;height:{h}px\"></div>"
                f"<div class='fade-to-bg' style='top:{h - 320}px'></div>")
    return f"<div class='photo' style=\"background-image:url('{src}');background-position:{pos}\"></div><div class='shade-b'></div>"


def chrome_html(b: dict, slide: dict, idx: int, total: int, logos: dict) -> str:
    ch = b['chrome']
    h = ''
    if ch.get('grain'):
        h += "<div class='grain'></div>"
    if ch.get('handle') and slide.get('handle', True):
        h += f"<div class='handle'>{ch['handle']}</div>"
    if ch.get('teaser_bar'):
        nxt = slide.get('next')
        pg = f"<span class='pg'>{idx}/{total}</span>" if ch.get('page_counter', True) else ''
        if nxt:
            h += f"<div class='bar'>{pg}<span class='next'>{nxt}</span></div>"
        else:
            tail = ch.get('end_label') or ch.get('handle') or ''
            h += f"<div class='bar end'>{pg}<span style='margin-left:auto'>{tail}</span></div>"
    variant = slide.get('logo', (b.get('logo') or {}).get('default', 'none'))
    if variant and variant != 'none' and variant in logos:
        lg = b['logo']
        bottom = lg.get('bottom', b['safe_area']['bottom'])
        h += (f"<img class='logo' src='{logos[variant]}' style='width:{lg.get('ink_width', 188)}px;"
              f"bottom:{bottom}px' data-logo='1'>")
    return h


def page_html(b: dict, slide: dict, idx: int, total: int, A: str, B: str, logos: dict, spec: dict) -> str:
    base = (HERE / 'base.css').read_text(encoding='utf-8')
    body = slide.get('html', '').replace('{A}', A).replace('{B}', B)
    body = CHART_RE.sub(lambda m: charts.render(spec.get('charts', {})[m.group(1)], b), body)
    font_css = b.get('fonts', {}).get('css', 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.min.css')
    W, H = b['canvas']['width'], b['canvas']['height']
    return (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
            f"<link rel='stylesheet' href='{font_css}'><style>{base}\n{brand_css(b)}</style></head>"
            f"<body style='width:{W}px;height:{H}px'><div class='card'>{bg_html(slide.get('bg'), b, A)}"
            f"<div class='content'>{body}</div>{chrome_html(b, slide, idx, total, logos)}</div></body></html>")


async def run(brand_dir: Path, spec_path: Path, out: Path, only=None, strict=False):
    b = load_brand(brand_dir)
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'html').mkdir(exist_ok=True)
    A = (spec_path.parent / 'assets').resolve().as_uri()
    B = (brand_dir / 'assets').resolve().as_uri()
    logos = prep_logos(b, brand_dir, out)
    W, H = b['canvas']['width'], b['canvas']['height']
    slides = spec['slides']
    total = spec.get('total', len(slides))
    from playwright.async_api import async_playwright
    reports = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        pg = await browser.new_page(viewport={'width': W, 'height': H})
        for i, s in enumerate(slides, 1):
            if only and s['id'] not in only:
                continue
            f = out / 'html' / f"{s['id']}.html"
            f.write_text(page_html(b, s, s.get('pg', i), total, A, B, logos, spec), encoding='utf-8')
            await pg.goto(f.resolve().as_uri())
            await pg.wait_for_load_state('networkidle')
            await pg.evaluate('document.fonts.ready')
            await pg.screenshot(path=str(out / f"{s['id']}.png"))
            reports.append(await audit.check(pg, b, s['id']))
            print('  png', s['id'])
        await browser.close()
    fails = audit.report(reports, out)
    print(f'저장: {out.resolve()}  ({len(reports)}장)')
    if strict and fails:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description='브랜드 키트 + 콘텐츠 spec으로 카드뉴스 PNG를 만든다')
    ap.add_argument('--brand', required=True, help='브랜드 폴더 (brand.json이 있는 곳)')
    ap.add_argument('--spec', required=True, help='콘텐츠 spec.json')
    ap.add_argument('--out', required=True, help='출력 폴더')
    ap.add_argument('--only', nargs='*', help='일부 슬라이드 id만 다시 렌더')
    ap.add_argument('--strict', action='store_true', help='검수 실패가 있으면 종료 코드 1')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(run(Path(a.brand), Path(a.spec), Path(a.out), a.only, a.strict))


if __name__ == '__main__':
    main()
