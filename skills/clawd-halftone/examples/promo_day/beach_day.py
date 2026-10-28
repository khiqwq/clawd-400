"""Scene 5 — beach_day (light): the backdrop for the "summer" GIFs.

Far -> near: sky (sun with ray dashes upper left, two r3_500 clouds, gulls) · horizon with a far headland and a
sailboat · the sea (a faint far field with carved wave lines; wave crests at the sides) · the shore (scalloped
wash, lace) · sand fading in from paper at the water to the floor band (near sand, denser toward the viewer)
with shells, a starfish and a sand dollar.
Left: the striped umbrella, a deck chair (profile) in its shade, a sandcastle with a flag. Right: the palm
(segmented trunk, fronds with lit/shaded halves and notched leaflets, coconuts) on a dune with beach grass,
a bucket and a spade.
Light from the upper left (the sun): rounded things shade on the right.
The GIF square (x 680-1240, y 471-1031) stays calm: sea/sand <= .1 there; the objects frame it.
Every object is built on cells (stair-stepped silhouettes, full dots to the edge) with a 1-cell air ring.
"""
import math

import numpy as np

from common import (Svg, P, ROWS, COLS, XS, YS, ck, full, render, crops, poly_mask, ellipse_mask,
                    shift_mask, ring, curve_frame)

s = Svg(theme='light')
C = ck.CellPaint()
rng = np.random.default_rng(5)
cols = np.arange(COLS)[None, :]
rows = np.arange(ROWS)[:, None]


def put(m, v):
    C.put(m, v)


def air(m, n=1):
    C.put(ring(m, n), -1)


def circ(cx, cy, r):
    return ck.circle_mask(cx, cy, r)


def cellrect(c0, r0, c1, r1):
    m = np.zeros((ROWS, COLS), bool)
    m[max(0, r0):r1, max(0, c0):c1] = True
    return m


def band(pts, half):
    """Cells within `half` px of a polyline (a thick crisp curve) + arclength / signed offset fields."""
    S, D, T, total = curve_frame(pts)
    return (np.abs(D) <= half) & (T > 0) & (T < 1), S, D, T


def bezq(p0, p1, p2, n=60):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


FB = 981                                                     # floor band top (row 109); feet at 975
HZ = 459                                                     # horizon row (y 459-468)

# ============================================================================ sky
SUNX, SUNY, SUNR = 513, 189, 84
put(circ(SUNX, SUNY, SUNR), 0.36)
for k in range(12):
    a = 2 * math.pi * k / 12 + math.pi / 12
    r0, r1 = SUNR + 30, SUNR + 60
    put(ck.polyline_mask([(SUNX + r0 * math.cos(a), SUNY + r0 * math.sin(a)), (SUNX + r1 * math.cos(a), SUNY + r1 * math.sin(a))]), 0.28)


def cloud(cx, base, w, lumps):
    """r3_500's cloud on cells: the lumpy top the densest part (~.42) with a crisp rim, the base fading
    toward the lower left (~.1), denser on the lower right (~.32)."""
    m = np.zeros((ROWS, COLS), bool)
    for dx, dy, r in lumps:
        m |= circ(cx + dx * w, base + dy * w, r * w)
    m &= full(YS <= base)
    m |= poly_mask([(cx - w * 0.5, base - w * 0.08), (cx + w * 0.5, base - w * 0.08), (cx + w * 0.53, base), (cx - w * 0.53, base)])
    lowl = (XS - cx) / w * 0.6
    put(m, 0.22)
    put(m & full(YS < base - w * 0.17), 0.42)
    put(m & full(YS >= base - w * 0.11) & full(lowl < -0.05), 0.1)
    put(m & full(YS >= base - w * 0.11) & full(lowl > 0.12), 0.32)
    put(ck.top_edge_mask(m), 0.5)
    return m


cloud(990, 297, 430, [(-0.34, -0.1, 0.1), (-0.17, -0.19, 0.12), (0.02, -0.3, 0.13), (0.2, -0.22, 0.12),
                      (0.36, -0.12, 0.09), (-0.08, -0.12, 0.12), (0.12, -0.12, 0.12)])
cloud(207, 342, 270, [(-0.3, -0.1, 0.11), (-0.08, -0.26, 0.15), (0.17, -0.18, 0.13), (0.36, -0.08, 0.09),
                      (0.04, -0.12, 0.14)])


def gull(x, y, v=0.62):
    """A gull: two wing humps one cell thick (an 'm'); x, y = the centre cell."""
    c, r = int(x // P), int(y // P)
    for dc, dr in ((-3, 1), (-2, 0), (-1, 0), (0, 1), (1, 0), (2, 0), (3, 1)):
        C.v[r + dr, c + dc] = v


for gx, gy in ((1206, 360), (1125, 405), (720, 396)):
    gull(gx, gy)

# ============================================================================ horizon: headland, sailboat
hl = poly_mask([(-10, HZ + 9), (-10, 423), (70, 414), (160, 420), (250, 441), (320, HZ + 9)])
put(hl, 0.14)
put(ck.top_edge_mask(hl), 0.3)
BX = 639
put(poly_mask([(BX, 360), (BX, 441), (BX + 54, 441)]), 0.22)          # main sail
put(poly_mask([(BX - 9, 378), (BX - 9, 441), (BX - 40, 441)]), 0.22)  # jib
put(ck.polyline_mask([(BX - 4, 351), (BX - 4, 450)]), 0.5)            # mast
put(poly_mask([(BX - 54, 450), (BX + 72, 450), (BX + 54, 468), (BX - 36, 468)]), 0.45)

# ============================================================================ sea
SHORE = np.array([int(round((702 + 11 * math.sin(c * P / 150) + 6 * math.sin(c * P / 61 + 1)) / P)) for c in range(COLS)])
sea = np.zeros((ROWS, COLS), bool)
for c in range(COLS):
    sea[HZ // P + 1:SHORE[c], c] = True
put(sea, 0.1)
put(sea & full(YS < 495), 0.2)                               # the far sea a level denser at the horizon
C.v[HZ // P, :] = 0.38                                       # horizon line
# carved wave lines: rows of paper dashes, spaced wider and longer toward the viewer
for r, (lmin, lmax, gmin, gmax) in ((53, (3, 6, 3, 7)), (56, (3, 7, 4, 8)), (59, (4, 8, 4, 9)), (62, (5, 9, 5, 10)),
                                     (66, (6, 11, 5, 11)), (70, (7, 13, 6, 12)), (74, (8, 15, 6, 13))):
    c = int(rng.integers(0, 6))
    while c < COLS:
        L_ = int(rng.integers(lmin, lmax + 1))
        for cc in range(c, min(COLS, c + L_)):
            if sea[r, cc]:
                C.v[r, cc] = -1
        c += L_ + int(rng.integers(gmin, gmax + 1))
# gentle wave crests at the sides: a small arc of dots with a carved foam line under it
for wx, wy, L_ in ((36, 513, 8), (99, 594, 11), (18, 666, 10), (1269, 621, 9), (1314, 522, 7),
                   (1782, 630, 11), (1845, 540, 8), (1395, 675, 10)):
    c, r = int(wx // P), int(wy // P)
    arc = np.zeros((ROWS, COLS), bool)
    arc[r, c + 1:c + L_ - 1] = True
    arc[r + 1, c] = arc[r + 1, c + L_ - 1] = True
    if (sea & arc).sum() == arc.sum():
        put(arc, 0.5)
        put(cellrect(c + 1, r + 1, c + L_ - 1, r + 2), -1)
# the wash: the sea's scalloped edge, a paper line, a lace row of foam
lace = np.zeros((ROWS, COLS), bool)
for c in range(COLS):
    lace[SHORE[c] + 1, c] = True
put(lace & full(cols % 4 != 3), 0.1)

# ============================================================================ sand + floor band
# the sand fades in from paper at the water to .1 at the feet line (the stage), then the floor band
sand = np.zeros((ROWS, COLS), bool)
for c in range(COLS):
    sand[SHORE[c] + 3:FB // P, c] = True
tv = 0.1 * np.clip((YS - 765) / (975 - 765), 0, 1) ** 0.9
tv = np.where(tv < 0.035, 0, tv)
C.v[sand] = np.broadcast_to(tv, (ROWS, COLS))[sand]
fb = full(YS > FB)
rows_v = np.clip(0.2 + (YS - FB) / (1080 - FB) * 0.24, 0.2, 0.44)
C.v[fb] = np.broadcast_to(rows_v, (ROWS, COLS))[fb]
# sand ripples: gentle wavy carved lines, in pieces, spaced wider toward the viewer
for y0, ph, segs in ((1008, 0.0, ((180, 270), (400, 540), (700, 1220), (1380, 1500), (1640, 1770))),
                     (1062, 1.9, ((180, 280), (380, 540), (700, 1220), (1660, 1780)))):
    m = ck.polyline_mask([(x, y0 + 8 * math.sin(x / 120 + ph)) for x in range(0, 1930, 15)]) & fb
    for x0, x1 in segs:
        put(m & full((XS > x0) & (XS < x1)), -1)

# ============================================================================ umbrella (left)
UX = 405                                                     # pole: 2 cells, x 405-423
UCX = UX + 9
UTOP, UBOT, URX = 549, 657, 243
NG = 6
tips = [UCX - URX + 2 * URX * k / NG for k in range(NG + 1)]
canopy = poly_mask([(UCX + URX * math.cos(math.radians(a)), UBOT - (UBOT - UTOP) * math.sin(math.radians(a))) for a in range(0, 181, 3)])
for k in range(NG):
    a, b = tips[k], tips[k + 1]
    canopy |= poly_mask([(a, UBOT - 4)] + [(a + (b - a) * i / 16, UBOT + 27 * math.sin(math.pi * i / 16)) for i in range(17)])
# gores converge on the apex: assign each cell by its x projected to the canopy's bottom along a ray from
# just above the apex; below the dome line (the scallops) by plain x
ang_x = UCX + (XS - UCX) * (UBOT - UTOP + 20) / np.maximum(YS - UTOP + 20, 1)
gore_of = np.clip(np.floor((ang_x - (UCX - URX)) / (2 * URX / NG)), 0, NG - 1).astype(int)
gore_of = np.where(YS > UBOT, np.clip(np.floor((XS - (UCX - URX)) / (2 * URX / NG)), 0, NG - 1), gore_of)
pole = cellrect(UX // P, UBOT // P, UX // P + 2, FB // P + 1)
finial = cellrect(UX // P, (UTOP - 18) // P, UX // P + 2, UTOP // P + 1)
collar = cellrect(UX // P - 1, 792 // P, UX // P + 3, 792 // P + 1)
air(canopy | pole | finial | collar)
dense = full(gore_of % 2 == 0)
put(canopy & dense, 0.9)
put(canopy & ~dense, 0.2)
put(canopy & ~dense & full(XS > UCX + URX * 0.36), 0.45)     # hard shade band on the right
put(ck.outline_mask(canopy), 0.9)                            # one-cell rim all round
put(finial | pole | collar, 0.85)

# ============================================================================ deck chair (profile, facing right)


def bar(p, q, thick=2):
    return ck.polyline_mask([p, q], thick=thick)


fA = bar((153, 702), (333, 975))                             # back frame: backrest top -> front foot
fB = bar((351, 846), (171, 975))                             # seat frame: seat front -> back foot
fC = bar((216, 801), (108, 975))                             # rear support (ratchet bar)
sling_pts = ck.bez((162, 711), (186, 846), (252, 891), (351, 846), n=60)
sling, S_, D_, T_ = band(sling_pts, 18)
frame = fA | fB | fC
air(frame | sling)
put(frame, 0.8)
put(sling, 0.24)
put(sling & ((S_ // 27) % 2 == 0), 0.9)                      # stripes across the canvas
put(sling & (D_ > 9), 0.9)                                   # its underside edge in shade
put(fA & ~sling & full(YS < 760), 0.8)

# ============================================================================ sandcastle
SC0, SC1, SB = 459, 675, 972


def blockshade(m, lit=0.26, shade=0.52, band_=0.32, edge=0.66):
    """A sand block: lit body, a hard shade band on its right, a one-cell outline."""
    cs = np.nonzero(m.any(axis=0))[0]
    x0, x1 = cs.min() * P, (cs.max() + 1) * P
    put(m, lit)
    put(m & full(XS > x1 - (x1 - x0) * band_), shade)
    put(ck.outline_mask(m), edge)


def tower(cx, top, bot, wb, wt):
    """A bucket-moulded tower: tapering (wb px wide at the base, wt at the top), crenellated top row."""
    m = poly_mask([(cx - wb / 2, bot), (cx - wt / 2, top), (cx + wt / 2, top), (cx + wb / 2, bot)])
    r = top // P - 1
    c0, c1 = int((cx - wt / 2) // P) + 1, int((cx + wt / 2) // P)
    for c in range(c0, c1, 2):
        m[r, c] = True
    m[r, c1 - 1] = True
    return m


c0, c1 = SC0 // P, SC1 // P
wall = cellrect(c0, 918 // P, c1, SB // P + 1)
for c in range(c0, c1, 3):
    wall[918 // P - 1, c:c + 2] = True
tl = tower(SC0 + 36, 828, 918, 72, 54)
tr = tower(SC1 - 36, 828, 918, 72, 54)
KX = (SC0 + SC1) / 2
keep = tower(KX, 774, 918, 81, 63)
kc = int(KX // P)
flagpole = cellrect(kc, 693 // P, kc + 1, 765 // P)
flag = poly_mask([(kc * P + 9, 693), (kc * P + 9, 729), (kc * P + 63, 711)])
castle = wall | tl | tr | keep
air(castle | flagpole | flag)
for m in (wall, tl, tr, keep):
    blockshade(m)
put(flagpole, 0.85)
put(flag, 0.9)
# arched gate + arched windows (carved), one groove per tower (the bucket's ridge)
put(cellrect(kc - 1, 945 // P, kc + 2, SB // P + 1) | cellrect(kc, 936 // P, kc + 1, 945 // P), -1)
for wx, wy in ((SC0 + 36, 855), (SC1 - 36, 855), (KX, 801)):
    wc = int(wx // P)
    put(cellrect(wc, wy // P + 1, wc + 1, wy // P + 3), -1)
for m, cx in ((tl, SC0 + 36), (tr, SC1 - 36), (keep, KX)):
    put(m & full((YS > 891) & (YS < 900)) & ~ck.outline_mask(m), -1)

# ============================================================================ palm (right)
TB = (1710, FB)                                              # trunk base
TT = (1557, 333)                                             # trunk top (under the crown)
trunk_pts = ck.bez(TB, (1724, 760), (1665, 480), TT, n=80)
trunk = np.zeros((ROWS, COLS), bool)
trunk_ring = np.zeros((ROWS, COLS), bool)
trunk_shade = np.zeros((ROWS, COLS), bool)
r_top, r_bot = TT[1] // P, TB[1] // P
for r in range(r_top, r_bot):
    y = r * P + 4.5
    k = min(range(len(trunk_pts)), key=lambda i: abs(trunk_pts[i][1] - y))
    cx = trunk_pts[k][0]
    t = (y - TT[1]) / (TB[1] - TT[1])
    hw = 26 + 14 * t                                         # half-width: 26 px at the top, 40 at the base
    seg = (r - r_top) % 4
    c0_, c1_ = int(round((cx - hw) / P)), int(round((cx + hw) / P))
    if seg == 0:
        c0_ -= 1                                             # each segment's top juts out on the lit side
    trunk[r, c0_:c1_] = True
    w = c1_ - c0_
    trunk_shade[r, c1_ - max(2, round(w * 0.4)):c1_] = True
    if seg == 3:
        trunk_ring[r, c0_:c1_] = True
trunk |= poly_mask([(1650, FB), (1676, 945), (1750, 945), (1778, FB)])         # root flare
trunk_shade |= trunk & full(XS > 1734) & full(YS > 940)

dune = poly_mask([(1430, FB + 2), (1490, 954), (1570, 936), (1670, 927), (1790, 930), (1880, 943), (1930, 950), (1930, FB + 2)])
air(dune)
put(dune, 0.18)
put(ck.top_edge_mask(dune), 0.38)
air(trunk)
put(trunk, 0.34)
put(trunk & trunk_shade, 0.88)
put(trunk_ring, 0.88)


def frond(p0, p1, p2, width, period=45, gapw=9, slant=1.1):
    """A palm frond along a quadratic curve p0 (crown) -> p2 (tip): the upper half lit, the lower half
    shaded (hard step along the rachis); leaflets suggested by notches carved in from the edges (deep on the
    lower edge, shallow on the upper), slanted toward the tip. Returns (mask, lit, dark, carve)."""
    pts = bezq(p0, p1, p2)
    S, D, T, total = curve_frame(pts)
    prof = width / 2 * np.sin(np.pi * np.clip(T, 0, 1) ** 0.58) ** 0.65
    inside = (np.abs(D) <= prof) & (T > 0.06) & (T < 0.99)
    mid = len(pts) // 2
    tx, ty = pts[mid + 1][0] - pts[mid - 1][0], pts[mid + 1][1] - pts[mid - 1][1]
    ny = tx / math.hypot(tx, ty)                             # normal (-ty, tx): its y component
    upper = (D < 0) if ny > 0 else (D > 0)
    phase = (S - slant * np.abs(D)) % period
    depth = np.where(upper, 0.66, 0.4)
    carve = inside & (np.abs(D) > prof * depth) & (phase < gapw) & (T > 0.2)
    return inside, inside & upper, inside & ~upper, carve


CROWN = (1557, 315)
fronds = [  # back to front: (control, tip, width) — leaning with the trunk, not mirror-symmetric
    ((1610, 95), (1752, 136), 100),
    ((1430, 88), (1251, 178), 112),
    ((1772, 262), (1905, 472), 117),
    ((1350, 250), (1205, 455), 117),
    ((1664, 384), (1772, 566), 94),
    ((1474, 404), (1418, 602), 88),
]
for ctrl, tip, wd in fronds:
    m, lm, dm, cv = frond(CROWN, ctrl, tip, wd)
    air(m)
    put(lm, 0.4)
    put(dm, 0.92)
    put(cv, -1)
nuts = np.zeros((ROWS, COLS), bool)
for cx, cy in ((1527, 358), (1576, 364), (1550, 400)):      # coconuts: lumps, lit cap / body / shade
    nuts |= circ(cx, cy, 27)
air(nuts)
for cx, cy in ((1527, 358), (1576, 364), (1550, 400)):
    m = circ(cx, cy, 27)
    lit, body, sh = ck.lump_shade(cx, cy, 27, m, lit_t=0.35, shade_t=0.25)
    put(body, 0.55); put(lit, 0.26); put(sh, 0.92)


# ============================================================================ beach grass on the dune
def grass(x, base, hs, v=0.85):
    """Beach grass: one-cell blades side by side with a cell of air between them, mostly upright, the tip
    bent one cell outward (left blades lean left, right ones right); hs = blade heights in cells."""
    m = np.zeros((ROWS, COLS), bool)
    c0 = int(x // P) - len(hs) + 1
    rb = int(base // P)
    for k, h in enumerate(hs):
        c = c0 + 2 * k
        lean = -1 if k < len(hs) / 2 - 0.5 else (1 if k > len(hs) / 2 - 0.5 else 0)
        m[rb - h + 2:rb + 1, c] = True
        m[rb - h:rb - h + 2, c + lean] = True
    air(m)
    put(m, v)


grass(1503, 963, [5, 8, 6, 4])
grass(1611, 945, [6, 9, 7])
grass(1818, 945, [5, 9, 10, 6])
grass(1881, 954, [6, 4])

# ============================================================================ bucket + spade (right of the square)
BK0, BK1, BKT = 1296, 1404, 876
bucket = poly_mask([(BK0 + 4, BKT + 9), (BK1 - 4, BKT + 9), (BK1 - 18, 975), (BK0 + 18, 975)])
rim = cellrect(BK0 // P, BKT // P, BK1 // P + 1, BKT // P + 2)
handle = ck.polyline_mask([(BK0 + 4, BKT)] + [(BK0 + 4 + (BK1 - BK0 - 8) * i / 20, BKT - 45 * math.sin(math.pi * i / 20)) for i in range(21)])
SPX = 1449
blade = poly_mask([(SPX - 22, 927), (SPX + 22, 927), (SPX + 22, 960), (SPX, 978), (SPX - 22, 960)])
shaft = cellrect(SPX // P, 810 // P, SPX // P + 1, 927 // P)
grip = cellrect(SPX // P - 1, 801 // P, SPX // P + 2, 801 // P + 1) | cellrect(SPX // P - 1, 810 // P, SPX // P, 819 // P) | cellrect(SPX // P + 1, 810 // P, SPX // P + 2, 819 // P)
air(bucket | rim | handle | blade | shaft | grip)
put(handle & ~rim, 0.8)
put(bucket, 0.26)
put(bucket & full(XS > BK1 - 40), 0.55)
put(ck.outline_mask(bucket), 0.72)
put(bucket & full((YS > 927) & (YS < 945)) & ~ck.outline_mask(bucket), 0.9)   # painted band
put(rim, 0.72)
put(blade, 0.45)
put(blade & full(XS > SPX + 4), 0.75)
put(ck.outline_mask(blade), 0.85)
put(shaft | grip, 0.85)


# ============================================================================ shells (floor band, outside the square)
def scallop(cx, cy, r=50):
    """A scallop: a dense fan (upper half disc) whose ribs are light columns (only straight carving stays
    clean at this size), a lit rim on the upper left, the hinge ears a row below."""
    c, rr = int(cx // P), int(cy // P)
    m = circ(cx, cy, r) & full(YS <= cy)
    ears = cellrect(c - 2, rr + 1, c + 3, rr + 2)
    air(m | ears)
    put(m, 0.88)
    put(m & full((cols - c) % 3 == 0) & full(YS < cy - 9), 0.3)
    put(m & ~shift_mask(m, 1, 1) & full(XS < cx), 0.45)
    put(ears, 0.88)


def starfish(cx, cy, R=45, r=18, rot=0):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5 + math.radians(rot)
        rr = R if k % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    m = poly_mask(pts)
    air(m)
    put(m, 0.9)
    put(m & ~shift_mask(m, 1, 1), 0.42)                      # lit edge (upper left)
    put(circ(cx, cy, 6) & m, -1)                             # carved centre


def pebble(cx, cy, rx, ry):
    m = ellipse_mask(cx, cy, rx, ry)
    air(m)
    put(m, 0.62)
    put(m & ~shift_mask(m, 1, 1), 0.3)


scallop(117, 1053, r=50)
starfish(333, 1030, R=48, r=20)
scallop(603, 1062, r=40)
starfish(1314, 1035, R=40, r=17, rot=18)
scallop(1575, 1053, r=45)
starfish(1836, 1030, R=44, r=19, rot=-12)

C.emit(s)

if __name__ == '__main__':
    render(s, 'beach_day')
    crops('beach_day', [
        ('palm crown: fronds lit/shaded halves', (1200, 90, 1920, 640), 'r3_390_patio', (1340, 140, 1920, 690)),
        ('cloud', (760, 100, 1240, 320), 'r3_500_hill_clouds', (1080, 80, 1560, 300)),
        ('sun + rays', (390, 50, 650, 330), 'r3_390_patio', (480, 100, 800, 430)),
        ('umbrella, deck chair, sandcastle', (90, 520, 690, 1000), 'r3_390_patio', (0, 270, 780, 990)),
        ('bucket + spade (pot recipe)', (1280, 780, 1480, 990), 'r3_390_patio', (130, 740, 380, 980)),
        ('sand: fade-in, floor band, shells', (0, 820, 720, 1080), 'r3_500_hill_clouds', (0, 680, 720, 1080)),
    ])
