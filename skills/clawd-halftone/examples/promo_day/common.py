"""Shared plumbing for the promo day backdrops (beach_day, kitchen_day).

Imports the clawd-halftone skill from its own scripts folder (nothing copied or edited), renders
SVG -> dots (+ value map, debug sheet), draws the GIF square overlay, checks the calm zone on the value
map, and builds 1:1 crop sheets (mine | reference).

The brief's GIF square: x 680-1240, y 471-1031 (Clawd centred at x 960, feet y 975). Calm zone inside it:
x 740-1180, y 500-975 -> only the floor band and faint far things (<= .1).
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

SKILL = os.path.join(os.path.expanduser('~'), '.rec', 'claude', 'accounts', '52928', 'config', 'skills', 'clawd-halftone')
SCRIPTS = os.path.join(SKILL, 'scripts')
REFS = os.path.join(SKILL, 'assets', 'refs')
sys.path.insert(0, SCRIPTS)

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.join(HERE, 'scenes')
os.makedirs(SCENES, exist_ok=True)

from svgkit import Svg, L, P, snap  # noqa: E402,F401
import cellkit as ck  # noqa: E402,F401

ROWS, COLS = 120, 213
YS = np.arange(4, 1080, P)[:, None] + 0.5          # cell centres (px)
XS = np.arange(4, 1920, P)[None, :] + 0.5
SQUARE = (680, 471, 1240, 1031)
CALM = (740, 500, 1180, 975)


def full(m):
    return np.broadcast_to(m, (ROWS, COLS)).copy()


def ref(name):
    return os.path.join(REFS, name + '.png')


def calm_mask():
    x0, y0, x1, y1 = CALM
    return full((XS >= x0) & (XS <= x1) & (YS >= y0) & (YS <= y1))


def check_calm(name):
    """Max dot value inside the calm zone (value map) + how many cells exceed .1."""
    v = np.asarray(Image.open(os.path.join(SCENES, name + '_value.png')).convert('L'), np.float32) / 255
    v = v[:ROWS, :COLS]
    m = calm_mask()
    zone = v[m]
    over = int((zone > 0.105).sum())
    print(f'[calm] {name}: max {zone.max():.3f}, mean {zone.mean():.3f}, cells > .1: {over} / {zone.size}')
    return zone.max(), over


def square_overlay(name):
    """The render with the GIF square (red), the calm zone (orange) and a ghost Clawd (feet y 975)."""
    im = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB')
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle(SQUARE, outline=(220, 40, 40, 255), width=3)
    x0, y0, x1, y1 = CALM
    for x in range(x0, x1, 24):
        d.line([(x, y0), (min(x + 12, x1), y0)], fill=(240, 140, 0, 255), width=2)
        d.line([(x, y1), (min(x + 12, x1), y1)], fill=(240, 140, 0, 255), width=2)
    for y in range(y0, y1, 24):
        d.line([(x0, y), (x0, min(y + 12, y1))], fill=(240, 140, 0, 255), width=2)
        d.line([(x1, y), (x1, min(y + 12, y1))], fill=(240, 140, 0, 255), width=2)
    # ghost Clawd: body 224 x 168 centred at x 960, four legs 42 tall to the feet at 975
    d.rectangle((848, 765, 1072, 933), fill=(217, 119, 87, 70), outline=(217, 119, 87, 160))
    for lx in (862, 918, 988, 1044):
        d.rectangle((lx, 933, lx + 14, 975), fill=(217, 119, 87, 70))
    d.text((SQUARE[0] + 6, SQUARE[1] + 4), 'GIF square 680-1240 x 471-1031 / calm zone dashed', fill=(220, 40, 40, 255))
    p = os.path.join(SCENES, name + '_square.png')
    im.save(p)
    return p


def render(s, name, theme='light'):
    svg = s.save(os.path.join(SCENES, name + '.svg'))
    out = os.path.join(SCENES, name + '.png')
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'svg2dots.py'), svg, out, '--theme', theme, '--debug'], check=True)
    square_overlay(name)
    check_calm(name)
    return out


def crops(name, pairs, out=None, gap=12):
    """1:1 crop sheet: each pair = (label, my_box, ref_name, ref_box); boxes (x0, y0, x1, y1) px."""
    mine = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB')
    rows = []
    for label, mb, rn, rb in pairs:
        a = mine.crop(mb)
        b = Image.open(ref(rn)).convert('RGB').crop(rb)
        h = max(a.height, b.height) + 22
        row = Image.new('RGB', (a.width + b.width + gap, h), (80, 80, 80))
        row.paste(a, (0, 22)); row.paste(b, (a.width + gap, 22))
        d = ImageDraw.Draw(row)
        d.text((4, 4), f'mine: {label}  {mb}', fill=(255, 210, 0))
        d.text((a.width + gap + 4, 4), f'ref {rn}  {rb}', fill=(255, 210, 0))
        rows.append(row)
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + gap * (len(rows) - 1)
    sheet = Image.new('RGB', (W, H), (60, 60, 60))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + gap
    p = out or os.path.join(SCENES, name + '_crops.png')
    sheet.save(p)
    return p


def crop(name, box, out, k=1):
    im = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB').crop(box)
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    im.save(out)
    return out


# ----------------------------------------------------------------------------- cell-level helpers
def poly_mask(pts):
    return ck.cell_mask([pts])


def ellipse_mask(cx, cy, rx, ry):
    return full(((XS - cx) / rx) ** 2 + ((YS - cy) / ry) ** 2 <= 1)


def rect_mask(x0, y0, x1, y1):
    """Cells whose centre lies in the px box."""
    return full((XS > x0) & (XS < x1) & (YS > y0) & (YS < y1))


def shift_mask(m, dc, dr):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dr):H + min(0, dr), max(0, dc):W + min(0, dc)] = m[max(0, -dr):H - max(0, dr), max(0, -dc):W - max(0, dc)]
    return out


def ring(m, n=1):
    """n cells of air around a mask."""
    return ck.dilate(m, n) & ~m


def curve_frame(pts, mask_box=None):
    """For every cell: (s, d) = arclength position along the polyline pts and signed distance from it
    (positive on the left of the direction of travel, in screen coords: left = (dy, -dx) normal... we
    use n = (-ty, tx)). Returns s, d, t (0..1), each ROWS x COLS (nan outside mask_box)."""
    pts = np.asarray(pts, float)
    seg = np.diff(pts, axis=0)
    seglen = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0], np.cumsum(seglen)])
    total = cum[-1]
    X = np.broadcast_to(XS, (ROWS, COLS)); Y = np.broadcast_to(YS, (ROWS, COLS))
    best_d2 = np.full((ROWS, COLS), np.inf)
    S = np.zeros((ROWS, COLS)); D = np.zeros((ROWS, COLS))
    for k in range(len(seg)):
        ax, ay = pts[k]; dx, dy = seg[k]; L2 = dx * dx + dy * dy
        u = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1)
        px, py = ax + u * dx, ay + u * dy
        d2 = (X - px) ** 2 + (Y - py) ** 2
        better = d2 < best_d2
        best_d2 = np.where(better, d2, best_d2)
        S = np.where(better, cum[k] + u * seglen[k], S)
        # sign: cross(tangent, point - p) ; normal n = (-dy, dx)/|.|
        cross = (dx * (Y - py) - dy * (X - px)) / np.sqrt(L2)
        D = np.where(better, cross, D)
    return S, D, S / total, total
