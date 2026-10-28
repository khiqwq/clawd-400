"""park_day (light) — a park on a clear day, front-on.

Far -> near: sky (the sun with ray dashes, two cell-built clouds: lumpy dense tops, bases fading) · a faint
city skyline · far hills · mid hills (each layer a field with a crisp ridge row, separated by a cell of
paper, nearer = denser) · the meadow (denser toward the viewer, flecked) · the path across the frame
(Clawd stands on it, centre, x 850-1075, feet y 975) with a few pebbles · two near trees (crowns as
clusters of shaded lumps, each lump a lit cap / body / shade in hard steps with a cell of air where it
overlaps the one behind, sky holes; trunks with a shade band, branches, root flare) · a bench by the path
under the left tree · a lamp post right of Clawd · grass tufts and a few flowers.
Light from the upper right (the sun): rounded things shade on their lower left.
Tones: sky 0 · clouds .46 → .1 · sun .38 · city .14 · far hills .12/.24 · mid hills .22/.36 · meadow
.24 → .46 · path 0 · foreground strip .34 · crowns .28/.5/.92 · trunks .55/.92 · bench, lamp, tufts .95.
"""
import math

import numpy as np

from canvas import (XS, YS, Canvas, R, rrect, circ, ell, poly, line, edge, grow, shrink, shift, right_of, below,
                    cols_every, rows_every, checker, empty, crops, stand_in, ck, P, ROWS, COLS)

c = Canvas('light')
rng = np.random.default_rng(11)
LIGHT = (0.7, -0.7)                                                    # toward the upper right
PT, PB = 936, 1026                                                     # path top / bottom (Clawd's feet at 975)

# ----------------------------------------------------------------------------- sky: sun + two clouds
SX, SY, SR = 1278, 153, 58
c.put(circ(SX, SY, SR), .38)
for k in range(12):
    a = 2 * math.pi * k / 12 + 0.13
    c.put(line([(SX + (SR + 27) * math.cos(a), SY + (SR + 27) * math.sin(a)),
                (SX + (SR + 50) * math.cos(a), SY + (SR + 50) * math.sin(a))]), .42)


def cloud(cx, base, w, lumps):
    """A cloud on cells like r3_500: a union of lumps over a flat base; the lumpy top is the densest part,
    the body thins downward and fades out toward the lower left, a crisp top edge row."""
    m = np.zeros((ROWS, COLS), bool)
    for dx, dy, r in lumps:
        m |= circ(cx + dx * w, base + dy * w, r * w)
    m |= ell(cx, base - w * 0.07, w * 0.4, w * 0.1)
    m &= ~below(base)
    m |= poly([(cx - w * 0.5, base - w * 0.07), (cx + w * 0.5, base - w * 0.07), (cx + w * 0.53, base), (cx - w * 0.53, base)])
    from scipy.ndimage import binary_fill_holes
    m = binary_fill_holes(m)
    ys, _ = np.nonzero(m)
    top = ys.min() * P
    t = np.clip((YS - top) / (base - top), 0, 1)                       # 0 at the top, 1 at the base
    lr = np.clip((XS - cx) / w + 0.5, 0, 1)                            # 0 left, 1 right
    v = .46 - .34 * t ** 1.3 + .1 * lr * t
    c.v[m] = np.broadcast_to(v, m.shape)[m]
    c.put(ck.top_edge_mask(m), .5)


cloud(630, 252, 450, [(-0.37, -0.06, 0.08), (-0.23, -0.15, 0.09), (-0.06, -0.27, 0.1), (0.1, -0.2, 0.09),
                      (0.25, -0.26, 0.085), (0.39, -0.1, 0.075), (-0.12, -0.08, 0.13), (0.14, -0.08, 0.13)])
cloud(1053, 360, 252, [(-0.32, -0.08, 0.1), (-0.12, -0.22, 0.12), (0.13, -0.3, 0.12), (0.33, -0.12, 0.1),
                       (0.02, -0.1, 0.15)])

# ----------------------------------------------------------------------------- far city, hills, meadow
x = 450
for h, w in ((99, 72), (162, 54), (126, 81), (207, 63), (117, 90), (171, 54), (90, 72), (189, 63), (135, 81), (108, 63), (153, 72)):
    if x > 1530:
        break
    m = R(x, 720 - h, x + w, 720)
    c.put(m, .14)
    for yy in range(720 - h + 18, 700, 27):
        for xx in range(x + 18, x + w - 9, 27):
            c.carve(R(xx, yy, xx + 9, yy + 9) & m)
    x += w + 18


def layer(fn, base=1080):
    return poly([(0, base), (0, fn(0))] + [(xx, fn(xx)) for xx in range(0, 1938, 18)] + [(1920, base)])


far = layer(lambda x: 666 - 30 * np.sin(x / 260) - 16 * np.sin(x / 97 + 1))
mid = layer(lambda x: 744 - 26 * np.sin(x / 210 + 2) - 12 * np.sin(x / 73))
near = layer(lambda x: 801 - 12 * np.sin(x / 170 + 0.5) - 7 * np.sin(x / 51))
c.put(far, .12)
c.put(ck.top_edge_mask(far), .24)
c.carve(grow(mid) & ~mid)
c.put(mid, .22)
c.put(ck.top_edge_mask(mid), .36)
c.carve(grow(near) & ~near)
gv = np.broadcast_to(np.clip(.24 + (YS - 801) / 130 * .22, .24, .46), near.shape)
c.v[near] = gv[near]                                                   # meadow: denser toward the viewer
c.put(ck.top_edge_mask(near), .45)
fleck = near & (rng.random((ROWS, COLS)) < 0.05) & below(828)
c.carve(fleck)
# the path: a paper band, its two grass edges crisp rows, a few pebbles (none at Clawd's feet)
c.carve(R(0, PT, 1920, PB))
c.put(R(0, PT - 9, 1920, PT), .62)
c.put(R(0, PB, 1920, PB + 9), .62)
fg = R(0, PB + 9, 1920, 1080)                                          # the foreground strip under the path
c.put(fg, .34)
c.carve(fg & (rng.random((ROWS, COLS)) < 0.06))
for _ in range(22):
    cc, rr = int(rng.integers(0, COLS - 2)), int(rng.integers(PT // P + 1, PB // P - 1))
    if not (88 <= cc <= 124):
        c.v[rr, cc:cc + int(rng.integers(1, 3))] = .3


# ----------------------------------------------------------------------------- trees
def tree(lumps, trunk, branches, holes):
    """A near tree. Trunk (body .55, a hard shade band on the left, a root flare) and branches first; then
    the crown cut out of the sky behind it, then lump by lump, back to front (no gaps between lumps: the
    clumps are told apart by their shade crescents and a one-cell paper arc on the lower-left side where a
    clump overlaps the one behind): body .5, a lit crescent .28 along its edge toward the sun, a shade crescent .92 along its
    lower-left edge (hard steps that follow the silhouette); a one-cell outline; sky holes 2 x 2 cells."""
    tx0, ty0, tx1, ty1 = trunk
    tm = R(tx0, ty0, tx1, ty1) | poly([(tx0 - 27, ty1), (tx0, ty1 - 45), (tx1, ty1 - 45), (tx1 + 27, ty1)])
    c.cut(tm)
    c.put(tm, .55)
    c.put(tm & ~right_of(tx0 + (tx1 - tx0) * 0.38), .92)
    c.carve(R(tx0 + 27, ty0 + 63, tx0 + 36, ty0 + 117) | R(tx0 + 45, ty0 + 171, tx0 + 54, ty0 + 207))   # bark marks
    for pts in branches:
        bm = ck.polyline_mask(pts, thick=2)
        c.put(bm, .92)
    crown = np.zeros((ROWS, COLS), bool)
    for cx, cy, r in lumps:
        crown |= circ(cx, cy, r)
    c.cut(crown)
    drawn = np.zeros((ROWS, COLS), bool)
    for cx, cy, r in lumps:
        m = circ(cx, cy, r)
        ll = np.broadcast_to((XS - cx) * -0.7 + (YS - cy) * 0.7 > -r * 0.2, m.shape)   # its lower-left side
        c.carve(grow(m) & ~m & drawn & ll)                             # a paper arc where it overlaps a clump behind
        drawn |= m
        c.put(m, .5)
        c.put(m & ~shift(m, 3, -3), .92)                               # shade: a crescent on the lower left
        c.put(m & ~shift(m, -2, 2), .28)                               # lit cap: a crescent toward the sun
    c.put(edge(crown) & (c.v > 0) & ~shift(crown, -2, 2), .8)       # one-cell outline (not over the lit caps)
    for hx, hy in holes:
        c.carve(R(hx, hy, hx + 18, hy + 18))


tree(lumps=[(140, 360, 86), (250, 255, 96), (385, 250, 92), (475, 350, 80), (200, 450, 92), (430, 455, 86),
            (320, 355, 112), (305, 480, 84)],
     trunk=(279, 540, 351, 945),
     branches=[[(306, 600), (297, 520), (220, 445)], [(324, 590), (380, 505), (430, 470)]],
     holes=[(234, 333), (396, 315), (342, 441)])
tree(lumps=[(1650, 310, 86), (1770, 270, 94), (1880, 345, 88), (1610, 420, 86), (1850, 460, 84), (1735, 385, 112),
            (1700, 495, 86)],
     trunk=(1701, 560, 1764, 945),
     branches=[[(1728, 620), (1720, 540), (1660, 480)], [(1740, 610), (1795, 525)]],
     holes=[(1683, 333), (1800, 414)])

# ----------------------------------------------------------------------------- bench by the path (under the left tree)
BX0, BX1 = 495, 801
slats = R(BX0 + 18, 819, BX1 - 18, 837) | R(BX0 + 18, 846, BX1 - 18, 864)
seat = R(BX0, 882, BX1, 900)
ends = R(BX0 + 18, 810, BX0 + 36, 927) | R(BX1 - 36, 810, BX1 - 18, 927) | R(BX0 + 9, 918, BX0 + 45, 927) | R(BX1 - 45, 918, BX1 - 9, 927)
arms = line([(BX0 + 27, 873), (BX0 - 9, 873), (BX0 - 9, 891)]) | line([(BX1 - 27, 873), (BX1 + 9, 873), (BX1 + 9, 891)])
under = R(BX0 + 9, 900, BX1 - 9, 909)
c.cut(slats | seat | ends | arms | under, 2)
c.put(slats | seat | ends | arms, .95)
c.put(under, .4)                                                       # the seat's underside, in shade
c.carve(R(BX0 + 27, 828, BX1 - 27, 829))
c.put(R(BX0 + 9, 882, BX1 - 9, 891), .7)                               # the seat's lit top edge

# ----------------------------------------------------------------------------- lamp post right of Clawd
LX = 1296
pole = R(LX - 18, 909, LX + 36, PT) | R(LX - 9, 891, LX + 27, 909) | R(LX, 594, LX + 18, 891) | R(LX - 9, 576, LX + 27, 594)
lant = poly([(LX - 36, 504), (LX + 54, 504), (LX + 36, 567), (LX - 18, 567)])
cap = R(LX - 54, 486, LX + 72, 504) | R(LX - 27, 468, LX + 45, 486) | R(LX, 450, LX + 18, 468) | R(LX - 27, 567, LX + 45, 576)
c.cut(pole | lant | cap)
c.put(pole | cap, .95)
c.put(pole & right_of(LX + 9), .6)                                     # lit side of the pole
c.put(lant, .26)                                                       # glass (unlit by day)
c.put(lant & ~right_of(LX + 9), .42)
c.put((R(LX - 9, 513, LX, 567) | R(LX + 18, 513, LX + 27, 567)) & lant, .95)   # glazing bars


# ----------------------------------------------------------------------------- grass tufts + flowers
def tuft(x, base, h=45, v=.95):
    """Three blades as one-cell stair lines from a base point, cut out of the meadow with a cell of paper."""
    m = line([(x + 4.5, base), (x + 4.5, base - h)])
    m |= line([(x + 4.5, base), (x - h * 0.55, base - h * 0.72)])
    m |= line([(x + 4.5, base), (x + h * 0.55 + 9, base - h * 0.72)])
    c.cut(m)
    c.put(m, v)


for x, base, h in ((99, PT - 9, 45), (171, PT - 9, 36), (414, PT - 9, 45), (828, PT - 9, 40), (1116, PT - 9, 45),
                   (1188, PT - 9, 36), (1404, PT - 9, 45), (1530, PT - 9, 36), (1611, PT - 9, 45), (1827, PT - 9, 40),
                   (585, 855, 27), (1053, 846, 27), (1449, 864, 27), (153, 864, 27), (936, 873, 27),
                   (63, 1071, 45), (342, 1071, 40), (720, 1071, 45), (1215, 1071, 45), (1575, 1071, 40), (1872, 1071, 45)):
    tuft(x, base, h)
for fx, fy in ((369, 873), (999, 864), (1494, 882), (1665, 855), (1350, 1062)):
    m = line([(fx + 4.5, fy + 36), (fx + 4.5, fy)]) | R(fx - 9, fy - 18, fx + 18, fy + 9)
    c.cut(m)
    c.put(m, .95)
    c.carve(R(fx, fy - 9, fx + 9, fy))                                 # the flower's paper eye

if __name__ == '__main__':
    c.save('park_day', 'r3_500_hill_clouds')
    crops('park_day', [
        ('cloud', (440, 50, 900, 270), 'r3_500_hill_clouds', (1080, 80, 1540, 300)),
        ('hills, meadow, path, bench', (380, 600, 1100, 1080), 'r3_500_hill_clouds', (0, 600, 720, 1080)),
        ('tree crown + trunk (foliage vs the patio plant)', (40, 140, 580, 950), 'r3_390_patio', (0, 260, 540, 1070)),
    ])
    stand_in('park_day', [(850, 765, 1075, 933), (878, 933, 906, 975), (934, 933, 962, 975), (990, 933, 1018, 975), (1046, 933, 1060, 975)],
             r'C:\Users\风花叶\AppData\Local\Temp\claude\E--GitHub-Clawd\5d038197-3164-4eae-84f6-24ffc9a67e21\scratchpad\it3\park_stage.png')
