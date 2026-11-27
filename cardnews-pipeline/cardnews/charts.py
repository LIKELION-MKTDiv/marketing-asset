# -*- coding: utf-8 -*-
"""spec.json의 "charts"를 SVG로 그린다. 본문 HTML에 {{chart:ID}}로 넣는다.

지원 형식
  gauge  반원 게이지   {"type":"gauge","items":[{"value":34,"label":"1위","color":"primary"}, ...]}
  bars   가로 막대     {"type":"bars","rows":[["항목",34],...],"max":40,"unit":"%","highlight":[0],
                        "ticks":[0,10,20,30,40],"width":760}
색은 brand.json colors의 키(primary, accent ...) 또는 #HEX로 쓴다.
차트 안 글자는 명암비 자동 검수에서 제외되므로 패널(밝은 배경) 안에 넣는 것을 기본으로 한다.
"""
import itertools

_uid = itertools.count()


def _c(b, key, fallback):
    return b.get('colors', {}).get(key, key) if key else b.get('colors', {}).get(fallback, '#333333')


def _font(b):
    return b.get('fonts', {}).get('family', 'Pretendard')


def gauge(cfg, b):
    ink, track = _c(b, cfg.get('ink'), 'ink'), _c(b, cfg.get('track'), 'track')
    r, w, cx, cy = 165, 26, 200, 230
    L = 3.14159265 * r
    arc = f'M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}'
    out = []
    for it in cfg['items']:
        col = _c(b, it.get('color'), 'primary')
        v = max(0, min(100, float(it['value'])))
        out.append(f"<svg width='400' height='300' viewBox='0 0 400 300' style='font-family:{_font(b)}'>"
                   f"<path d='{arc}' fill='none' stroke='{track}' stroke-width='{w}' stroke-linecap='round'/>"
                   f"<path d='{arc}' fill='none' stroke='{col}' stroke-width='{w}' stroke-linecap='round' "
                   f"stroke-dasharray='{L * v / 100:.1f} {L:.1f}'/>"
                   f"<text x='{cx}' y='{cy - 20}' text-anchor='middle' font-size='68' font-weight='800' fill='{col}'>"
                   f"{it.get('display', str(it['value']) + cfg.get('unit', '%'))}</text>"
                   f"<text x='{cx}' y='{cy + 58}' text-anchor='middle' font-size='34' font-weight='700' fill='{ink}'>"
                   f"{it.get('label', '')}</text></svg>")
    return "<div style='display:flex;justify-content:space-around'>" + ''.join(out) + '</div>'


def bars(cfg, b):
    ink, sub, grid = _c(b, cfg.get('ink'), 'ink'), _c(b, cfg.get('sub'), 'muted'), _c(b, cfg.get('grid'), 'track')
    hi = _c(b, cfg.get('color'), 'primary')
    lo = _c(b, cfg.get('color_rest'), 'secondary')
    rows, mx, unit = cfg['rows'], float(cfg.get('max') or max(r[1] for r in cfg['rows'])), cfg.get('unit', '')
    hl = set(cfg.get('highlight', [0]))
    W = int(cfg.get('width', 760))
    x0, x1, step = int(W * 0.2), int(W * 0.84), 115
    Hh = 40 + step * len(rows) + 50
    s = f"<svg width='{W}' height='{Hh}' viewBox='0 0 {W} {Hh}' style='font-family:{_font(b)}'>"
    for t in cfg.get('ticks', []):
        x = x0 + (x1 - x0) * t / mx
        s += f"<line x1='{x:.0f}' y1='20' x2='{x:.0f}' y2='{Hh - 60}' stroke='{grid}' stroke-width='2' stroke-dasharray='{'0' if t == 0 else '6 8'}'/>"
        s += f"<text x='{x:.0f}' y='{Hh - 20}' text-anchor='middle' font-size='24' fill='{sub}'>{t:g}{unit}</text>"
    for i, (label, v) in enumerate(rows):
        y = 40 + i * step
        bw = (x1 - x0) * float(v) / mx
        col = hi if i in hl else lo
        s += f"<text x='0' y='{y + 50}' font-size='36' font-weight='{800 if i in hl else 600}' fill='{ink}'>{label}</text>"
        s += f"<rect x='{x0}' y='{y + 12}' width='{bw:.0f}' height='56' rx='28' fill='{col}'/>"
        s += f"<text x='{x0 + bw + 18:.0f}' y='{y + 53}' font-size='40' font-weight='800' fill='{col}'>{v:g}{unit}</text>"
    return s + '</svg>'


KINDS = {'gauge': gauge, 'bars': bars}


def render(cfg, b):
    if cfg.get('type') not in KINDS:
        raise ValueError(f"지원하지 않는 차트 형식: {cfg.get('type')} (gauge, bars)")
    return KINDS[cfg['type']](cfg, b)
