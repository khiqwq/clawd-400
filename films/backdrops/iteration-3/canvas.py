"""Iteration-3 plumbing: a cell-exact value canvas on top of the clawd-halftone skill.

The scene is composed directly on the screen's cell grid (120 rows x 213 cols, 9 px cells) as a value map
(0 = no dot, 1 = the biggest dot), then emitted through the skill's svgkit.Svg as crisp cell rects and
rendered by the skill's svg2dots.py. Working on cells (instead of free SVG shapes) gives every object
the references' stair-stepped silhouette with full dots up to the edge, and makes "carve after glow"
an ordinary array operation.

The skill is imported from its own folder (not copied, not edited).
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SKILL = os.path.join(os.path.expanduser('~'), '.rec', 'claude', 'accounts', '52928', 'config', 'skills', 'clawd-halftone')
SCRIPTS = os.path.join(SKILL, 'scripts')
REFS = os.path.join(SKILL, 'assets', 'refs')
sys.path.insert(0, SCRIPTS)

from svgkit import Svg, L, P  # noqa: E402,F401
import cellkit as ck  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.join(HERE, 'scenes')
os.makedirs(SCENES, exist_ok=True)

ROWS, COLS = 120, 213
YS = np.arange(ROWS)[:, None] * P + 4.5          # cell centres, px
XS = np.arange(COLS)[None, :] * P + 4.5


def ref(name):
    return os.path.join(REFS, name + '.png')


# ----------------------------------------------------------------------------- masks (px in, cells out)
def empty():
    return np.zeros((ROWS, COLS), bool)


def R(x0, y0, x1, y1):
    """Cells whose centre lies in the px box [x0, x1) x [y0, y1) (use multiples of 9 for exact cells)."""
    return (XS >= x0) & (XS < x1) & (YS >= y0) & (YS < y1)


def rrect(x0, y0, x1, y1, r):
    """Rounded box (corner radius r px), cell-exact."""
    m = R(x0, y0, x1, y1)
    cx = np.clip(XS, x0 + r, x1 - r)
    cy = np.clip(YS, y0 + r, y1 - r)
    return m & ((XS - cx) ** 2 + (YS - cy) ** 2 <= r * r)


def circ(cx, cy, r):
    return (XS - cx) ** 2 + (YS - cy) ** 2 <= r * r


def ell(cx, cy, rx, ry):
    return ((XS - cx) / rx) ** 2 + ((YS - cy) / ry) ** 2 <= 1


def poly(pts):
    return ck.cell_mask([pts])


def line(pts, thick=1):
    return ck.polyline_mask(pts, thick=thick)


def edge(m):
    """One-cell contour of a mask (cellkit.outline_mask)."""
    return ck.outline_mask(m)


def grow(m, n=1):
    return ck.dilate(m, n)


def shrink(m, n=1):
    return ~ck.dilate(~m, n)


def shift(m, dc=0, dr=0):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dr):H + min(0, dr), max(0, dc):W + min(0, dc)] = m[max(0, -dr):H - max(0, dr), max(0, -dc):W - max(0, dc)]
    return out


def right_of(x):
    return np.broadcast_to(XS >= x, (ROWS, COLS))


def below(y):
    return np.broadcast_to(YS >= y, (ROWS, COLS))


def cols_every(x0, step, width=1):
    """Columns x0 + k*step (px), `width` cells wide — for grilles, slats, channel stitching."""
    c = (XS - x0) // P
    return np.broadcast_to((c % (step // P) < width) & (XS >= x0), (ROWS, COLS))


def rows_every(y0, step, width=1):
    r = (YS - y0) // P
    return np.broadcast_to((r % (step // P) < width) & (YS >= y0), (ROWS, COLS))


def checker(phase=0):
    r, c = np.mgrid[0:ROWS, 0:COLS]
    return (r + c + phase) % 2 == 0


# ----------------------------------------------------------------------------- the canvas
class Canvas:
    """Value map on the cell grid. put / carve / glow / text; save() -> svg + svg2dots render."""

    def __init__(self, theme='dark'):
        self.theme = theme
        self.v = np.zeros((ROWS, COLS))

    def put(self, m, v):
        self.v[m] = v
        return m

    def carve(self, m):
        self.v[m] = 0
        return m

    def cut(self, m, n=1):
        """Clear an n-cell margin around a near shape (the overlap rule), before drawing it."""
        self.v[grow(m, n) & ~m] = 0
        return m

    def obj(self, m, v, n=1):
        """A near object: margin of ground around it, then the fill."""
        self.cut(m, n)
        self.v[m] = v
        return m

    def lift(self, m, dv):
        self.v[m] = np.clip(self.v[m] + dv, 0, 1)

    def glow(self, cx, cy, r, v, mid=0.45, ry=None, m=None):
        """svgkit.glow on cells: v at the centre, v*mid at 40 %, 0 at r (ry for an ellipse); added
        like screen (night light) / multiply (day shadow ink): v' = 1 - (1-v)(1-g). m limits it."""
        ry = ry or r
        d = np.sqrt(((XS - cx) / r) ** 2 + ((YS - cy) / ry) ** 2)
        g = np.where(d < 0.4, v + (v * mid - v) * d / 0.4, v * mid * np.clip((1 - d) / 0.6, 0, 1))
        g = np.broadcast_to(g, self.v.shape).copy()
        if m is not None:
            g[~m] = 0
        self.v = 1 - (1 - self.v) * (1 - g)

    def text(self, x, y, txt, v, size=12, font='C:/Windows/Fonts/simsun.ttc', gap=1):
        """Bitmap glyphs, one glyph pixel per cell (svgkit.bitmap_text on cells). Returns the mask."""
        f = ImageFont.truetype(font, size)
        m = empty()
        c0, r0 = int(x // P), int(y // P)
        for ch in txt:
            im = Image.new('L', (size + 4, size + 4), 0)
            d = ImageDraw.Draw(im)
            d.fontmode = '1'
            d.text((0, 0), ch, font=f, fill=255)
            a = np.asarray(im) > 127
            for rr, cc in zip(*np.nonzero(a)):
                if 0 <= r0 + rr < ROWS and 0 <= c0 + cc < COLS:
                    m[r0 + rr, c0 + cc] = True
            c0 += (size // 2 if ord(ch) < 128 else size) + gap
        self.v[m] = v
        return m

    def seg7(self, x, y, txt, v, w=4, h=7, ghost=0.0):
        """Clock digits (svgkit.seg7 on cells): w x h cells per digit, segments one cell thick."""
        SEG = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg', '5': 'acdfg', '6': 'acdefg',
               '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
        c, r = int(x // P), int(y // P)
        m = empty()
        for ch in txt:
            if ch == ':':
                m[r + h // 2 - 1, c] = True
                m[r + h // 2 + 1, c] = True
                c += 2
                continue
            on = SEG.get(ch, '')
            segs = {'a': (1, 0, w - 2, 1), 'b': (w - 1, 1, 1, h // 2 - 1), 'c': (w - 1, h // 2 + 1, 1, h - h // 2 - 2),
                    'd': (1, h - 1, w - 2, 1), 'e': (0, h // 2 + 1, 1, h - h // 2 - 2), 'f': (0, 1, 1, h // 2 - 1),
                    'g': (1, h // 2, w - 2, 1)}
            for k, (sx, sy, sw, sh) in segs.items():
                if k in on:
                    m[r + sy:r + sy + sh, c + sx:c + sx + sw] = True
                elif ghost:
                    self.v[r + sy:r + sy + sh, c + sx:c + sx + sw] = ghost
            # corners of lit segments joined, like a seven-segment glyph drawn on a grid
            c += w + 1
        self.v[m] = v
        return m

    # ------------------------------------------------------------------ output
    def svg(self):
        s = Svg(theme=self.theme)
        q = np.round(np.clip(self.v, 0, 1) * 63) / 63           # the screen's 64 dot sizes
        for val in np.unique(q):
            if val <= 0.02:
                continue
            ck.cells(s, q == val, float(val))
        return s

    def save(self, name, ref_name=None, debug=True):
        s = self.svg()
        svg = s.save(os.path.join(SCENES, name + '.svg'))
        out = os.path.join(SCENES, name + '.png')
        cmd = [sys.executable, os.path.join(SCRIPTS, 'svg2dots.py'), svg, out, '--theme', 'light' if self.theme == 'light' else 'dark']
        if debug:
            cmd.append('--debug')
        subprocess.run(cmd, check=True)
        if ref_name:
            subprocess.run([sys.executable, os.path.join(SCRIPTS, 'compare.py'), out, '--ref', ref(ref_name),
                            '--out', os.path.join(SCENES, name + '_cmp.png')], check=True)
        return out


# ----------------------------------------------------------------------------- review sheets
def crops(name, pairs, out=None, gap=12):
    """1:1 crop sheet: each pair = (label, my_box, ref_name, ref_box). Each row: mine | reference."""
    mine = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB')
    rows = []
    for label, mb, rn, rb in pairs:
        a = mine.crop(mb)
        b = Image.open(ref(rn)).convert('RGB').crop(rb)
        h = max(a.height, b.height) + 22
        row = Image.new('RGB', (a.width + b.width + gap, h), (80, 80, 80))
        row.paste(a, (0, 22))
        row.paste(b, (a.width + gap, 22))
        d = ImageDraw.Draw(row)
        d.text((4, 4), f'mine: {label}  {mb}', fill=(255, 210, 0))
        d.text((a.width + gap + 4, 4), f'ref {rn}  {rb}', fill=(255, 210, 0))
        rows.append(row)
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + gap * (len(rows) - 1)
    sheet = Image.new('RGB', (W, H), (60, 60, 60))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + gap
    p = out or os.path.join(SCENES, name + '_crops.png')
    sheet.save(p)
    return p


def stand_in(name, boxes, out):
    """Review only: the render with flat orange Clawd stand-ins (x0, y0, x1, y1) to judge his stage."""
    im = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB')
    d = ImageDraw.Draw(im)
    for b in boxes:
        d.rectangle(b, fill=(217, 119, 87))
    im.save(out)
    return out
