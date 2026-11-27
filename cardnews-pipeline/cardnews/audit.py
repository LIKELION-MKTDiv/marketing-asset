# -*- coding: utf-8 -*-
"""렌더 직후 자동 검수: 여백 침범, 글자 크기 하한, 명암비.

명암비는 배경 '평균'이 아니라 글자 영역의 최악값으로 잰다.
  밝은 글자 -> 그 영역 배경의 밝은 쪽 상위 2% 휘도와 비교
  어두운 글자 -> 어두운 쪽 하위 2% 휘도와 비교
사진·그라데이션 배경은 평균으로 재면 통과하지만 일부 글자가 묻히기 때문이다.

검사 대상은 .content 안의 HTML 글자다. SVG 차트 안 글자와 data-audit="off" 요소는 제외한다.
안전 여백 밖으로 일부러 내보내는 요소(풀블리드 장식 글자 등)는 data-free 속성을 붙이면 여백 검사만 건너뛴다.
"""
import io
import json
import re

import numpy as np
from PIL import Image

JS_COLLECT = r"""() => {
  const out = [];
  const root = document.querySelector('.content');
  if (!root) return out;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = n.textContent;
    if (!t.trim()) continue;
    const el = n.parentElement;
    if (el.closest('svg') || el.closest('[data-audit="off"]')) continue;
    const r = document.createRange();
    r.selectNodeContents(n);
    const rs = [...r.getClientRects()].filter(x => x.width > 0 && x.height > 0);
    if (!rs.length) continue;
    const cs = getComputedStyle(el);
    let op = 1, e = el;
    while (e) { op *= parseFloat(getComputedStyle(e).opacity); e = e.parentElement; }
    for (const x of rs) out.push({text: t.trim().slice(0, 30), x0: x.left, y0: x.top, x1: x.right, y1: x.bottom,
      color: cs.color, size: parseFloat(cs.fontSize), opacity: op, free: !!el.closest('[data-free]')});
  }
  return out;
}"""

HIDE_TEXT = ".content, .content *{color:transparent !important;text-shadow:none !important;-webkit-text-stroke:0 !important}"


def _rgba(s):
    v = [float(x) for x in re.findall(r'[\d.]+', s)]
    return v[:3], (v[3] if len(v) > 3 else 1.0)


def rel_lum(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def _hex(rgb):
    return '#%02X%02X%02X' % tuple(int(round(x)) for x in rgb)


async def check(page, b: dict, slide_id: str) -> dict:
    W, H = b['canvas']['width'], b['canvas']['height']
    s = b['safe_area']
    cfg = b.get('audit', {})
    targets = {k.upper(): v for k, v in (cfg.get('contrast') or {}).items()}
    default_t = targets.pop('DEFAULT', 4.5)
    large_t = targets.pop('LARGE', default_t)
    large_px = cfg.get('large_px', 48)
    pct = cfg.get('bg_percentile', 98)
    min_px = cfg.get('min_font_px', 0)
    tol = 2

    items = await page.evaluate(JS_COLLECT)
    await page.add_style_tag(content=HIDE_TEXT)
    bg = np.asarray(Image.open(io.BytesIO(await page.screenshot())).convert('RGB'), dtype=np.float64)

    issues, rows = [], []
    for it in items:
        x0, y0, x1, y1 = (int(round(it[k])) for k in ('x0', 'y0', 'x1', 'y1'))
        if not it['free'] and (x0 < s['left'] - tol or x1 > W - s['right'] + tol
                               or y0 < s['top'] - tol or y1 > H - s['bottom'] + tol):
            issues.append(f"여백침범  x {x0}~{x1}, y {y0}~{y1} (허용 x {s['left']}~{W - s['right']}, "
                          f"y {s['top']}~{H - s['bottom']})  '{it['text']}'")
        if min_px and it['size'] < min_px - 0.5 and not it['free']:
            issues.append(f"글자크기  {it['size']:.0f}px < 하한 {min_px}px  '{it['text']}'")
        reg = bg[max(0, y0):min(H, y1), max(0, x0):min(W, x1)]
        if reg.size == 0:
            continue
        rgb, a = _rgba(it['color'])
        a *= it['opacity']
        if a <= 0.01:
            continue
        mean = reg.reshape(-1, 3).mean(axis=0)
        eff = np.array(rgb) * a + mean * (1 - a)
        lt = float(rel_lum(eff))
        lum = rel_lum(reg)
        lb = float(np.percentile(lum, pct)) if lt >= float(np.median(lum)) else float(np.percentile(lum, 100 - pct))
        ratio = (max(lt, lb) + 0.05) / (min(lt, lb) + 0.05)
        hx = _hex(rgb)
        tgt = targets.get(hx, large_t if it['size'] >= large_px else default_t)
        ok = ratio >= tgt
        rows.append({'text': it['text'], 'color': hx, 'size': it['size'], 'ratio': round(ratio, 2), 'target': tgt, 'ok': ok})
        if not ok:
            issues.append(f"명암비    {ratio:.2f}:1 < {tgt}:1  ({hx}, {it['size']:.0f}px)  '{it['text']}'")
    # 같은 글자 덩어리가 여러 줄로 잡히면 같은 경고가 반복되므로 중복 제거
    return {'id': slide_id, 'issues': list(dict.fromkeys(issues)), 'contrast': rows}


def report(reports, out) -> int:
    fails = sum(len(r['issues']) for r in reports)
    print('\n=== 검수 결과 (여백 · 글자 크기 · 명암비) ===')
    for r in reports:
        worst = min((c['ratio'] for c in r['contrast']), default=None)
        head = f"{r['id']:<24} " + ('통과' if not r['issues'] else f"★ {len(r['issues'])}건")
        if worst is not None:
            head += f"   최저 명암비 {worst}:1"
        print(head)
        for i in r['issues']:
            print('    -', i)
    print(f'검수 이슈 합계 {fails}건' if fails else '전 슬라이드 통과')
    (out / 'audit.json').write_text(json.dumps(reports, ensure_ascii=False, indent=1), encoding='utf-8')
    return fails
