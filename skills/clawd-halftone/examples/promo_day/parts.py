"""Reusable cell-level parts from beach_day / kitchen_day, for the later promo day scenes.

    from parts import *
    cv = Canvas()                       # an Svg (light) + a CellPaint
    cv.put(R(10, 20, 30, 40), .45)      # cells cols 10..29, rows 20..39
    cv.air(mask)                        # a one-cell paper ring around a mask (the overlap rule)
    ...
    cv.emit(); render(cv.s, 'name')

Everything is on the 9-px cell grid (213 x 120): stair-stepped silhouettes with full dots to the edge.
"""
import math

import numpy as np

from common import (Svg, P, ROWS, COLS, XS, YS, ck, full, render, crops, poly_mask, ellipse_mask,  # noqa: F401
                    shift_mask, ring, curve_frame)

cols = np.arange(COLS)[None, :]
rows = np.arange(ROWS)[:, None]


class Canvas:
    def __init__(self):
        self.s = Svg(theme='light')
        self.C = ck.CellPaint()

    def put(self, m, v):
        self.C.put(m, v)

    def air(self, m, n=1):
        self.C.put(ring(m, n), -1)

    def carve(self, m):
        self.C.put(m, -1)

    def emit(self):
        self.C.emit(self.s)


def R(c0, r0, c1, r1):
    """Cell rectangle: cols c0..c1-1, rows r0..r1-1."""
    m = np.zeros((ROWS, COLS), bool)
    m[max(0, r0):max(0, r1), max(0, c0):max(0, c1)] = True
    return m


def circ(cx, cy, r):
    return ck.circle_mask(cx, cy, r)


def outline(m):
    return ck.outline_mask(m)


def side(m, which):
    """Edge cells of a mask facing one side: 'l', 'r', 't', 'b'."""
    dc, dr = {'l': (1, 0), 'r': (-1, 0), 't': (0, 1), 'b': (0, -1)}[which]
    return m & ~shift_mask(m, dc, dr)


def bezq(p0, p1, p2, n=60):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


def line(pts, thick=1):
    return ck.polyline_mask(pts, thick=thick)


def c_(x):
    """px -> cell index."""
    return int(x // P)


# ----------------------------------------------------------------------------- sky
def sun(cv, cx, cy, r, v=0.36, ray_v=0.28, rays=12, gap=30, length=27, clip=None):
    """r3_390's sun: a flat disc, ray dashes of smaller dots."""
    m = circ(cx, cy, r)
    cv.put(m if clip is None else m & clip, v)
    for k in range(rays):
        a = 2 * math.pi * k / rays + math.pi / rays
        r0, r1 = r + gap, r + gap + length
        d = line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))])
        cv.put(d if clip is None else d & clip, ray_v)


def cloud(cv, cx, base, w, lumps):
    """r3_500's cloud on cells: the lumpy top densest (~.42) with a crisp rim, the base fading out to the
    lower left (~.1), denser lower right (~.32)."""
    m = np.zeros((ROWS, COLS), bool)
    for dx, dy, r in lumps:
        m |= circ(cx + dx * w, base + dy * w, r * w)
    m &= full(YS <= base)
    m |= poly_mask([(cx - w * 0.5, base - w * 0.08), (cx + w * 0.5, base - w * 0.08), (cx + w * 0.53, base), (cx - w * 0.53, base)])
    lowl = (XS - cx) / w * 0.6
    cv.put(m, 0.22)
    cv.put(m & full(YS < base - w * 0.17), 0.42)
    cv.put(m & full(YS >= base - w * 0.11) & full(lowl < -0.05), 0.1)
    cv.put(m & full(YS >= base - w * 0.11) & full(lowl > 0.12), 0.32)
    cv.put(ck.top_edge_mask(m), 0.5)
    return m


CLOUD_BIG = [(-0.34, -0.1, 0.1), (-0.17, -0.19, 0.12), (0.02, -0.3, 0.13), (0.2, -0.22, 0.12),
             (0.36, -0.12, 0.09), (-0.08, -0.12, 0.12), (0.12, -0.12, 0.12)]
CLOUD_SMALL = [(-0.3, -0.1, 0.11), (-0.08, -0.26, 0.15), (0.17, -0.18, 0.13), (0.36, -0.08, 0.09), (0.04, -0.12, 0.14)]


# ----------------------------------------------------------------------------- plants
def leaf2(cx, cy, ang, L, W, light=(-0.6, -0.8)):
    """A teardrop leaf (wide near the stem, pointed at the tip) along `ang` (deg, 0 = right, 90 = down)
    from its centre. Returns (mask, lit half, dark half)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    X, Y = np.broadcast_to(XS, (ROWS, COLS)), np.broadcast_to(YS, (ROWS, COLS))
    u = ((X - cx) * ux + (Y - cy) * uy) / (L / 2)
    v = -(X - cx) * uy + (Y - cy) * ux
    halfw = W / 2 * np.sqrt(np.clip(1 - u * u, 0, 1)) * (1 - 0.3 * u)
    m = (np.abs(v) <= halfw) & (np.abs(u) <= 1)
    s = -uy * light[0] + ux * light[1]
    lit = m & (v * s > 0)
    return m, lit, m & ~lit


def draw_leaves(cv, spec, lit_v=0.42, dark_v=0.92, light=(-0.6, -0.8), split=False):
    """Leaves back to front, each cut out of the ones behind it by a one-cell air ring. Small leaves are
    solid dense with a one-cell lit rim facing the light; split=True gives big leaves lit/dark halves."""
    allm = np.zeros((ROWS, COLS), bool)
    dc = -1 if light[0] < 0 else 1
    for cx, cy, ang, L_, W_ in spec:
        m, lt, dk = leaf2(cx, cy, ang, L_, W_, light)
        cv.air(m)
        if split:
            cv.put(lt, lit_v); cv.put(dk, dark_v)
        else:
            cv.put(m, dark_v)
            cv.put(m & ~shift_mask(m, -dc, 1), lit_v)
        allm |= m
    return allm


def cpot(cv, cx, base, w, h, light='l', body=0.2, rim=0.3, shade=0.5, edge=0.66):
    """r3_390's pot on cells: a wider rim band, a tapering body with stepped bottom corners, a one-cell
    outline, a hard shade band (~30 %) away from the light."""
    rim_h = max(2, round(h * 0.28 / P))
    c0, c1 = int(round((cx - w / 2) / P)), int(round((cx + w / 2) / P))
    rb, rt = base // P, base // P - h // P
    rim_m = R(c0, rt, c1, rt + rim_h)
    bod = np.zeros((ROWS, COLS), bool)
    nrows = rb - (rt + rim_h)
    for i, r in enumerate(range(rt + rim_h, rb)):
        inset = 1 + i // max(1, nrows - 1)
        if r == rb - 1:
            inset += 1
        bod[r, c0 + inset:c1 - inset] = True
    m = rim_m | bod
    cv.air(m)
    band = max(2, round((c1 - c0) * 0.3))
    sh = R(c1 - band, 0, c1, ROWS) if light == 'l' else R(c0, 0, c0 + band, ROWS)
    cv.put(bod, body); cv.put(bod & sh, shade)
    cv.put(rim_m, rim); cv.put(rim_m & sh, min(1, shade + 0.15))
    cv.put(outline(bod), edge); cv.put(outline(rim_m), edge)
    return m


def tree_far(cv, cx, top, r, base, v=0.18, shade=0.3):
    """A far round tree: a crown of three lumps (shade on the lower right), a one-cell trunk."""
    m = circ(cx, top + r, r) | circ(cx - r * 0.6, top + r * 1.5, r * 0.7) | circ(cx + r * 0.6, top + r * 1.45, r * 0.75)
    cv.put(R(c_(cx), c_(top + r * 1.8), c_(cx) + 1, c_(base)), shade)
    cv.put(m, v)
    cv.put(m & ~shift_mask(m, -1, -1), shade)
    cv.put(ck.top_edge_mask(m), shade)
    return m


# ----------------------------------------------------------------------------- furniture details
def inset(cv, c0, r0, c1, r1, light='r'):
    """A recessed panel the v1_12 way: a carved ring, two cells wide on the bottom and on the side away from
    the light (the recess in shadow), one cell on the lit sides."""
    cv.carve(outline(R(c0, r0, c1, r1)))
    cv.carve(R(c0, r1 - 2, c1, r1 - 1))
    if light == 'r':
        cv.carve(R(c0 + 1, r0, c0 + 2, r1))
    else:
        cv.carve(R(c1 - 2, r0, c1 - 1, r1))


def lump(cv, cx, cy, r, body, light='l', glint=True):
    """A small round thing (fruit, ball, knob): one tone, a dense rim on the shade side, a paper glint."""
    m = circ(cx, cy, r)
    cv.air(m)
    cv.put(m, body)
    far = 'r' if light == 'l' else 'l'
    cv.put(side(m, 'b') | side(m, far), min(0.95, body + 0.4))
    if glint:
        gx = cx - r * 0.4 if light == 'l' else cx + r * 0.4
        cv.carve(R(c_(gx), c_(cy - r * 0.4), c_(gx) + 1, c_(cy - r * 0.4) + 1))
    return m


# ----------------------------------------------------------------------------- tiny cell font (3 x 5, M/W 5 wide)
FONT = {
    'A': ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'], 'B': ['XX.', 'X.X', 'XX.', 'X.X', 'XX.'],
    'C': ['.XX', 'X..', 'X..', 'X..', '.XX'], 'D': ['XX.', 'X.X', 'X.X', 'X.X', 'XX.'],
    'E': ['XXX', 'X..', 'XX.', 'X..', 'XXX'], 'G': ['.XX', 'X..', 'X.X', 'X.X', '.XX'],
    'H': ['X.X', 'X.X', 'XXX', 'X.X', 'X.X'], 'I': ['XXX', '.X.', '.X.', '.X.', 'XXX'],
    'L': ['X..', 'X..', 'X..', 'X..', 'XXX'], 'M': ['X...X', 'XX.XX', 'X.X.X', 'X...X', 'X...X'],
    'N': ['X..X', 'XX.X', 'X.XX', 'X..X', 'X..X'], 'O': ['.X.', 'X.X', 'X.X', 'X.X', '.X.'],
    'P': ['XX.', 'X.X', 'XX.', 'X..', 'X..'], 'R': ['XX.', 'X.X', 'XX.', 'X.X', 'X.X'],
    'S': ['.XX', 'X..', '.X.', '..X', 'XX.'], 'T': ['XXX', '.X.', '.X.', '.X.', '.X.'],
    'U': ['X.X', 'X.X', 'X.X', 'X.X', 'XXX'], 'W': ['X...X', 'X...X', 'X.X.X', 'XX.XX', 'X...X'],
    'Y': ['X.X', 'X.X', '.X.', '.X.', '.X.'], 'Z': ['XXX', '..X', '.X.', 'X..', 'XXX'],
    '0': ['XXX', 'X.X', 'X.X', 'X.X', 'XXX'], '1': ['.X.', 'XX.', '.X.', '.X.', 'XXX'],
    '2': ['XX.', '..X', '.X.', 'X..', 'XXX'], '3': ['XX.', '..X', '.X.', '..X', 'XX.'],
    '4': ['X.X', 'X.X', 'XXX', '..X', '..X'], '5': ['XXX', 'X..', 'XX.', '..X', 'XX.'],
    '7': ['XXX', '..X', '.X.', '.X.', '.X.'], '9': ['XXX', 'X.X', 'XXX', '..X', 'XX.'],
    '!': ['X', 'X', 'X', '.', 'X'], ':': ['.', 'X', '.', 'X', '.'], ' ': ['..', '..', '..', '..', '..'],
    '♥': ['.X.X.', 'XXXXX', 'XXXXX', '.XXX.', '..X..'],
}


def text_mask(c, r, txt, gap=1):
    """Cells of a word in the 3 x 5 font, top-left at cell (c, r). Returns (mask, width in cells)."""
    m = np.zeros((ROWS, COLS), bool)
    x = c
    for ch in txt:
        g = FONT[ch]
        for dr, rowstr in enumerate(g):
            for dc, k in enumerate(rowstr):
                if k == 'X' and 0 <= r + dr < ROWS and 0 <= x + dc < COLS:
                    m[r + dr, x + dc] = True
        x += len(g[0]) + gap
    return m, x - c - gap
