"""Scene 4 — park_day (light): a park on a clear day, front-on.

Far → near: sky (sun + two clouds) · far city (faint) · far hills · mid hills · meadow (denser toward the
viewer, flecked, tufts) · the path across the frame (Clawd stands on it, centre, x 850-1075, feet y 975) ·
two near trees (lumpy crowns with lit caps and shaded undersides, trunks), a bench under the left tree, a
lamp post right of Clawd. Light from the upper left.
Tones: sky 0 · clouds .08/.16/.3 · city .14 · far hills .12 · mid hills .22 · meadow .3 → .5 · trees .3/.6/.92 ·
trunks .55/.9 · bench, lamp .92 · path paper with .3 pebbles.
"""
import numpy as np

from common import Svg, P, render, crops
from extras import (gap, box, cell_mask, cells, top_edge_mask, polyline_mask, circle_mask, dilate, CellPaint,
                    lump_shade, bez)

s = Svg(theme='light')
ink = s.ink
rng = np.random.default_rng(11)
ROWS, COLS = 120, 213
YS = np.arange(4, 1080, P)[:, None] + 0.5
XS = np.arange(4, 1920, P)[None, :] + 0.5

# ----------------------------------------------------------------------------- sky: sun + clouds
s.sun(1206, 153, 63, v=0.36, ray_v=0.3, rays=12, ray_len=27, gap=27)


def cloud(cx, base, w, lumps, paint):
    """A cell-crisp cloud: a union of lumps over a flat base; lit tops (upper left) lighter, the lower right
    a hard step heavier — like r3_500's cloud."""
    m = np.zeros((ROWS, COLS), bool)
    for dx, dy, r in lumps:
        m |= circle_mask(cx + dx * w, base + dy * w, r * w)
    m &= np.broadcast_to(YS <= base, m.shape)
    m |= cell_mask([[(cx - w * 0.5, base - w * 0.08), (cx + w * 0.5, base - w * 0.08), (cx + w * 0.52, base),
                     (cx - w * 0.52, base)]])
    d = ((XS - cx) * 0.55 + (YS - base) * 0.84) / w          # toward the lower right
    # as measured on r3_500's cloud: the lumpy top is the densest part (~.36), the base fades out toward
    # the lower left (~.1) and stays denser on the lower right (~.3)
    lowl = (XS - cx) / w * 0.6 - (YS - base) / w * 0.0
    paint.put(m, 0.22)
    paint.put(m & np.broadcast_to(YS < base - w * 0.17, m.shape), 0.42)       # the lumpy top
    paint.put(m & np.broadcast_to(YS >= base - w * 0.11, m.shape) & (lowl < -0.05), 0.1)   # fading lower left
    paint.put(m & np.broadcast_to(YS >= base - w * 0.11, m.shape) & (lowl > 0.12), 0.32)   # lower right
    paint.put(top_edge_mask(m), 0.5)                         # crisp rim along the top


sky = CellPaint()
cloud(756, 288, 420, [(-0.34, -0.1, 0.1), (-0.17, -0.19, 0.12), (0.02, -0.3, 0.13), (0.2, -0.22, 0.12),
                      (0.36, -0.12, 0.09), (-0.08, -0.12, 0.12), (0.12, -0.12, 0.12)], sky)
cloud(1449, 387, 270, [(-0.3, -0.1, 0.11), (-0.08, -0.26, 0.15), (0.17, -0.18, 0.13), (0.36, -0.08, 0.09),
                       (0.04, -0.12, 0.14)], sky)
sky.emit(s)

# ----------------------------------------------------------------------------- far city + hills
city = s.clip_rect(0, 0, 1920, 720)
with s.plane(clip=city):
    s.skyline(468, 1530, 720, [99, 171, 126, 207, 117, 153, 90, 180, 135], v=0.14, seed=4, widths=(72, 126))

ground = CellPaint()
far = cell_mask([[(0, 1080), (0, 684)] + [(x, 684 - 30 * np.sin(x / 260) - 18 * np.sin(x / 97 + 1)) for x in range(0, 1930, 30)] + [(1920, 1080)]])
mid = cell_mask([[(0, 1080), (0, 756)] + [(x, 744 - 26 * np.sin(x / 210 + 2) - 12 * np.sin(x / 73)) for x in range(0, 1930, 30)] + [(1920, 1080)]])
near = cell_mask([[(0, 1080), (0, 810)] + [(x, 812 - 14 * np.sin(x / 170 + 0.5) - 8 * np.sin(x / 51)) for x in range(0, 1930, 30)] + [(1920, 1080)]])
ground.put(far, 0.12)
ground.put(top_edge_mask(far), 0.24)
ground.put(dilate(mid) & ~mid, -1)                            # air: each nearer layer is cut out of the
ground.put(mid, 0.22)                                         # one behind it by one cell of paper
ground.put(top_edge_mask(mid), 0.36)
# meadow: denser toward the viewer (row by row), flecked with paper like the hill ref
rows_v = np.clip(0.32 + (YS - 810) / 270 * 0.4, 0.32, 0.74) * np.ones((1, COLS))
ground.put(dilate(near) & ~near, -1)
ground.put(near, 0)
ground.v[near] = rows_v[near]
ground.put(top_edge_mask(near), 0.5)
fleck = near & (rng.random((ROWS, COLS)) < 0.05) & (YS > 830)
ground.put(fleck, -1)
# the path: a paper band with a crisp grass edge above and below, a few pebbles
PT, PB = 936, 1017
path = np.broadcast_to((YS > PT) & (YS < PB), (ROWS, COLS))
ground.put(path, -1)
ground.put(np.broadcast_to((YS > PT - 9) & (YS < PT), (ROWS, COLS)), 0.6)
ground.put(np.broadcast_to((YS > PB) & (YS < PB + 9), (ROWS, COLS)), 0.6)
for _ in range(26):
    c, r = int(rng.integers(0, COLS - 2)), int(rng.integers(PT // P + 1, PB // P - 1))
    if not (94 <= c <= 120):                                 # keep Clawd's feet clean
        ground.v[r, c:c + int(rng.integers(1, 3))] = 0.3
ground.emit(s)


# ----------------------------------------------------------------------------- trees
def shift_mask(m, dc, dr):
    """m shifted by dc columns, dr rows (outside = False)."""
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dr):H + min(0, dr), max(0, dc):W + min(0, dc)] = m[max(0, -dr):H - max(0, dr), max(0, -dc):W - max(0, dc)]
    return out


def tree(lumps, trunk, branches, holes, arcs, body=0.52, lit=0.22, shade=0.92):
    """A near tree: crown = the union of lumps as one mass (body), a lit rim 2 cells deep wherever the
    crown's edge faces the upper left (so every lump gets its own lit cap), a shaded rim 3 cells deep on the
    lower right + the whole underside a hard step heavier; a few one-cell paper arcs on the shade side to
    separate lumps; sky holes; trunk (hard shade band) with branches."""
    tx0, ty0, tx1, ty1 = trunk
    s.cyl(tx0, ty0, tx1, ty1, 0.55, 0.9, light_left=True, band=0.36)
    s.poly([(tx0 - 18, ty1), (tx0, ty1 - 36), (tx1, ty1 - 36), (tx1 + 18, ty1)], fill=ink(0.9))   # root flare
    for pts in branches:
        s.poly(pts, stroke=ink(0.9), sw=18, closed=False)
    U = np.zeros((ROWS, COLS), bool)
    ms = [circle_mask(cx, cy, r) for cx, cy, r in lumps]
    for m in ms:
        U |= m
    ys, xs = np.nonzero(U)
    under = U & np.broadcast_to(YS > ys.mean() * P + 0.3 * (ys.max() - ys.min()) * P / 2, U.shape)
    paint = CellPaint()
    paint.put(U, body)
    for k, m in enumerate(ms):                                # per lump, back to front: visible part only
        later = np.zeros_like(U)
        for m2 in ms[k + 1:]:
            later |= m2
        vis = m & ~later
        earlier = np.zeros_like(U)
        for m2 in ms[:k]:
            earlier |= m2
        cx, cy, r = lumps[k]
        _, _, sh = lump_shade(cx, cy, r, m, lit_t=0.5, shade_t=0.2)
        paint.put(vis & (sh | ~shift_mask(m, -2, -2)), shade)  # lower-right part of each lump, hard step
        paint.put(vis & ~shift_mask(m, 2, 2), lit)            # lit cap on its upper left
        ring = dilate(m) & ~m & earlier & ~later & (shift_mask(m, -1, -1) | shift_mask(m, 0, -1) | shift_mask(m, -1, 0))
        paint.put(ring, -1)                                   # air where it overlaps the lumps behind
    for hx, hy in holes:                                      # sky holes, 2 x 2 cells
        c, r = int(hx // P), int(hy // P)
        paint.v[r:r + 2, c:c + 2] = -1
    with s.cut():
        paint.emit(s)


tree(lumps=[(140, 340, 88), (250, 250, 100), (380, 250, 96), (470, 345, 84), (190, 440, 100), (320, 360, 120),
            (430, 450, 92), (300, 490, 96)],
     trunk=(261, 540, 333, 945),
     branches=[[(297, 600), (297, 520), (230, 450)], [(306, 590), (360, 500), (400, 470)]],
     holes=[(225, 333), (387, 306), (333, 441)],
     arcs=[(320, 360, 120, -10, 100), (190, 440, 100, 10, 80), (380, 250, 96, 20, 110), (250, 250, 100, 30, 120)])
tree(lumps=[(1640, 310, 88), (1760, 280, 96), (1870, 360, 90), (1600, 420, 90), (1720, 390, 116), (1840, 470, 88),
            (1690, 500, 92)],
     trunk=(1692, 560, 1755, 945),
     branches=[[(1722, 620), (1716, 540), (1660, 490)], [(1730, 610), (1780, 530)]],
     holes=[(1683, 333), (1791, 414)],
     arcs=[(1720, 390, 116, -10, 100), (1600, 420, 90, 10, 90), (1760, 280, 96, 20, 110)])

# ----------------------------------------------------------------------------- bench (under the left tree)
BX0, BX1 = 468, 783
with s.cut():
    for y in (828, 855):                                     # backrest slats (2 rows each)
        box(s, BX0 + 18, y, BX1 - 18, y + 18, 0.92)
    box(s, BX0, 891, BX1, 909, 0.92)                         # seat front edge
    box(s, BX0 + 9, 909, BX1 - 9, 918, 0.36)                 # seat underside (shade)
    for ex in (BX0 + 18, BX1 - 36):                          # cast ends: back post, leg, foot
        box(s, ex, 819, ex + 18, 963, 0.95)
        box(s, ex - 9, 954, ex + 27, 963, 0.95)
    for ax, sgn in ((BX0, -1), (BX1, 1)):                    # curled armrests
        s.path(f'M{ax - sgn * 18} 873 Q{ax + sgn * 9} 873 {ax + sgn * 9} 891', stroke=ink(0.92), sw=9)

# ----------------------------------------------------------------------------- lamp post (right of Clawd)
LX = 1296
with s.cut():
    box(s, LX - 18, 918, LX + 36, 945, 0.92)                 # base
    box(s, LX, 585, LX + 18, 918, 0.92)                      # pole
    box(s, LX - 9, 567, LX + 27, 585, 0.92)
    lant = cell_mask([[(LX - 36, 495), (LX + 54, 495), (LX + 36, 558), (LX - 18, 558)]])
    cells(s, lant, 0.3)                                      # glass (light, unlit by day)
    box(s, LX - 54, 477, LX + 72, 495, 0.92)                 # cap
    box(s, LX - 27, 459, LX + 45, 477, 0.92)
    box(s, LX, 441, LX + 18, 459, 0.92)
    box(s, LX - 27, 558, LX + 45, 567, 0.92)
for bx_ in (LX - 9, LX + 18):
    box(s, bx_, 504, bx_ + 9, 558, 0.92)                     # glazing bars (dark by day)


# ----------------------------------------------------------------------------- grass tufts (cell-exact)
def tuft(x, base, h=45, v=0.92):
    """Three blades as one-cell stair lines from a base point (x multiple of 9), cut out of the meadow
    with one cell of paper so they read on a dense field."""
    m = polyline_mask([(x + 4.5, base), (x + 4.5, base - h)])
    m |= polyline_mask([(x + 4.5, base), (x - h * 0.55, base - h * 0.7)])
    m |= polyline_mask([(x + 4.5, base), (x + h * 0.55 + 9, base - h * 0.7)])
    cells(s, dilate(m) & ~m, s.paper)
    cells(s, m, v)


for x, base, h in ((99, 930, 45), (180, 925, 36), (396, 930, 45), (819, 930, 45), (1125, 930, 45),
                   (1188, 925, 36), (1386, 930, 45), (1530, 930, 36), (1611, 930, 45), (1800, 930, 45),
                   (558, 870, 27), (1035, 860, 27), (1440, 865, 27), (153, 860, 27)):
    tuft(x, base, h)

# a few flowers in the meadow: a paper head on a dark stem
for fx, fy in ((360, 891), (927, 873), (1494, 900), (1584, 873)):
    m = polyline_mask([(fx + 4.5, fy + 36), (fx + 4.5, fy)]) | (circle_mask(fx + 4.5, fy - 9, 17))
    cells(s, dilate(m) & ~m, s.paper)
    cells(s, m, 0.9)
    gap(s, fx, fy - 18, 9, 9)                                # paper eye of the flower

if __name__ == '__main__':
    render(s, 'park_day', 'light', 'r3_500_hill_clouds')
    crops('park_day', [
        ('cloud', (520, 70, 1000, 300), 'r3_500_hill_clouds', (1080, 80, 1560, 310)),
        ('hills, meadow, path, bench', (380, 600, 1100, 1080), 'r3_500_hill_clouds', (0, 600, 720, 1080)),
        ('tree crown + trunk', (40, 130, 580, 950), 'r3_390_patio', (0, 260, 540, 1080)),
    ])
