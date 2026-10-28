"""Scene 4 — snow_day (light): a snowy street by day, for the "seasons" GIFs.

Far → near: two snow clouds (top) · far hills with small far pines (faint, ≤ .1, they may pass behind
the square) · left: a chalet (45° roof band with a snow blanket and icicles, siding, attic window, two
windows with snow on the sills and flower boxes, a door with a wreath, a chimney with smoke) and a big
pine beside it · right: the lamp post (unlit lantern, snow on its cap), the snowman, a brick café (a
shingled roof under snow, icicles, a CAFE sign, a striped awning with snow on it, the window, a door) ·
the snowy street (snow = paper; the ground a dot field that gets denser toward the viewer, paper flecks,
footprints) · snowbanks at both sides · falling flakes: single cells far, plus-shaped near, carved
(paper) where they pass over dark things, none in the calm core.
Snow is drawn as paper bounded by a crisp .62 outline on the sky side. Light from the upper left.
"""
import math

import numpy as np

from common import Svg, P, render, crops, CALM
from cellkit import CellPaint, cell_mask, outline_mask, dilate, circle_mask, polyline_mask, top_edge_mask
from daykit import rect_mask, rrect_pts, shift_mask, C, YS, XS, ROWS, COLS

s = Svg(theme='light')
rng = np.random.default_rng(12)
GROUND = 972                                                 # the snow line (feet stand at 975)
R_, C_ = np.mgrid[0:ROWS, 0:COLS]

W = CellPaint()


def put(m, v):
    W.put(m, v)


def air(m):
    """One cell of paper round m over whatever is already painted (near over far)."""
    W.put(dilate(m) & ~m & ~np.isnan(W.v), -1)


def snow(m, v=0.62, under=None):
    """Snow lying on something: paper cells, a crisp outline on every side that faces the sky (or
    paper) — i.e. all of its outline except where it rests on `under`."""
    W.put(m, -1)
    bottom = m & ~shift_mask(m, 0, -1)                        # where it rests: no outline
    top = m & ~shift_mask(m, 0, 1)
    W.put(outline_mask(m) & ~(bottom & ~top), v)


# ----------------------------------------------------------------------------- clouds (top)
for (cx0, cy0, sc) in ((720, 126, 1.25), (1206, 90, 0.95)):
    m = np.zeros((ROWS, COLS), bool)
    for dx, dy, r in ((-90, 18, 45), (-36, -18, 63), (36, -9, 58), (90, 22, 40), (0, 27, 50)):
        m |= circle_mask(cx0 + dx * sc, cy0 + dy * sc, r * sc)
    m &= np.broadcast_to(YS <= cy0 + 54 * sc, m.shape)
    put(m, 0.2)
    put(m & np.broadcast_to(YS < cy0 - 9 * sc, m.shape), 0.36)
    put(top_edge_mask(m), 0.45)
    put(m & np.broadcast_to(YS > cy0 + 27 * sc, m.shape) & (XS < cx0), 0.1)

# ----------------------------------------------------------------------------- far hills + far pines (≤ .1)
def hill_y(x):
    return 801 - 36 * math.sin(x / 300 + 0.6) - 14 * math.sin(x / 110 + 2)


hills = cell_mask([[(0, GROUND), (0, 801)] + [(x, hill_y(x)) for x in range(0, 1930, 30)] + [(1920, GROUND)]])
put(hills, 0.08)
for fx, fh in ((693, 81), (747, 108), (801, 72), (1107, 90), (1152, 117), (1206, 72)):
    ty = hill_y(fx) - fh
    put(cell_mask([[(fx, ty), (fx + fh * 0.34, ty + fh + 9), (fx - fh * 0.34, ty + fh + 9)]]), 0.1)

# ----------------------------------------------------------------------------- the street (floor band)
for r in range(C(GROUND) + 1, ROWS):
    t = (r - C(GROUND) - 1) / (ROWS - 2 - C(GROUND))
    W.v[r, :] = 0.12 + 0.22 * t                               # denser toward the viewer
put(rect_mask(0, GROUND, 1920, GROUND + 9), 0.3)               # the snow line
put((rng.random((ROWS, COLS)) < 0.08) & (R_ > C(GROUND) + 1), -1)   # paper sparkle
for k, x in enumerate(range(18, 1920, 54)):                    # footprints, kept away from Clawd's feet
    if 690 < x < 1230:
        continue
    y = (1035 + int(18 * math.sin(x / 150))) // P * P + (9 if k % 2 else 0)
    put(rect_mask(x, y, x + 9, y + 18), 0.62)


# ----------------------------------------------------------------------------- pine
def pine(cc, top_r, tiers, base_y, trunk_w=2):
    """A pine on 45° tiers (one cell wider per row: clean stairs). Lower tiers first, each upper tier in
    front of the one below with a cell of air; every tier: dense needles, the lit half (left) lighter,
    snow lying along its shoulders (2 paper cells + a .62 line above), drooping tips carved along the
    bottom row. tiers = [(top_row_offset, height_rows), ...] from the top."""
    tr = rect_mask((cc - trunk_w // 2) * P, base_y - 99, (cc + (trunk_w + 1) // 2 + 1) * P, base_y)
    masks = []
    for off, h in tiers:
        t0 = top_r + off
        m = (R_ >= t0) & (R_ < t0 + h) & (np.abs(C_ - cc) <= (R_ - t0))
        masks.append((t0, h, m))
    allm = tr.copy()
    for _, _, m in masks:
        allm |= m
    air(allm | dilate(allm))
    put(tr, 0.95)
    for t0, h, m in reversed(masks):                             # bottom tier first
        air(m)
        put(m, 0.9)
        put(m & (C_ < cc), 0.6)                                   # lit half
        d = R_ - t0 - np.abs(C_ - cc)                             # rows below the slope line
        sn = m & (d >= 0) & (d < 2) & (np.abs(C_ - cc) >= 1)
        put(sn, -1)
        line = (d == -1) & (R_ >= t0) & (np.abs(C_ - cc) >= 1) & (np.abs(C_ - cc) <= h - 1)
        put(line, 0.62)
        put(rect_mask(0, 0, 1920, 1080) & (R_ == t0 - 1) & (C_ == cc), 0.62)
        bot = m & (R_ == t0 + h - 1) & ((C_ - cc) % 2 == 1)
        put(bot, -1)                                              # drooping tips


# ----------------------------------------------------------------------------- left: the chalet
AC, AR = 29, 39                                              # apex cell (x 261, y 351)
EAVE_R = 66                                                  # eave row (y 594)
roofband = (R_ >= AR) & (R_ <= EAVE_R + 3) & ((R_ - AR) - np.abs(C_ - AC) >= 0) & ((R_ - AR) - np.abs(C_ - AC) < 4)
roofband &= (C_ >= 0) & (C_ <= 58)
snowband = (R_ >= AR - 3) & ((R_ - AR) - np.abs(C_ - AC) >= -3) & ((R_ - AR) - np.abs(C_ - AC) < 0) & (R_ <= EAVE_R)
snowband &= (C_ >= 1) & (C_ <= 57)
wall = (R_ >= AR + 4) & (R_ < C(GROUND)) & ((R_ - AR) - np.abs(C_ - AC) >= 4) & (C_ >= 5) & (C_ <= 53)
wall |= (R_ > EAVE_R) & (R_ < C(GROUND)) & (C_ >= 5) & (C_ <= 53)
# chimney first (behind the roof)
chim = rect_mask(369, 378, 423, 486)
air(chim)
put(chim, 0.9)
put(chim & rect_mask(0, 0, 387, 1080), 0.6)                    # lit side (left)
for k, y in enumerate(range(387, 486, 18)):                    # brick joints
    put(chim & rect_mask(0, y, 1920, y + 9), -1)
    put(chim & rect_mask(396 if k % 2 else 405, y - 9, (396 if k % 2 else 405) + 9, y), -1)
ccap = cell_mask([rrect_pts(360, 342, 432, 405, 18)]) & ~rect_mask(0, 378, 1920, 1080)
air(ccap & ~dilate(chim))
snow(ccap)
for (sx, sy, r) in ((414, 315, 16), (450, 270, 20), (495, 216, 25)):
    pm = circle_mask(sx, sy, r)
    put(pm, 0.18)
    put(top_edge_mask(pm), 0.36)
air(wall | roofband | snowband)
put(wall, 0.3)
for y in range(405, GROUND, 27):                               # siding: carved board joints
    put(wall & rect_mask(0, y, 1920, y + 9), -1)
sh = wall & (C_ >= 49)
put(sh, 0.6)                                                   # shade band (right)
for y in range(405, GROUND, 27):
    put(sh & rect_mask(0, y, 1920, y + 9), -1)
put(roofband, 0.95)
put(roofband & (C_ < AC) & ((R_ - AR) - np.abs(C_ - AC) == 3), 0.6)   # lit underside line, left slope
snow(snowband)
for c in (2, 5, 7, 52, 54, 56):                                # icicles under the eaves
    rows_ = np.nonzero(roofband[:, c])[0]
    if len(rows_):
        r = rows_.max() + 1
        W.v[r:r + 2 + c % 3, c] = 0.62
# attic window (round), two windows, the door
aw = circle_mask(261, 477, 36)
put(dilate(aw) & ~aw, -1)
put(aw & dilate(~aw, 1), 0.95)
put(aw & ~dilate(~aw, 1), 0.5)
put(aw & ~dilate(~aw, 1) & (rect_mask(256, 0, 266, 1080) | rect_mask(0, 472, 1920, 482)), -1)
for wx0 in (81, 342):
    fr = rect_mask(wx0, 693, wx0 + 99, 828)
    put(dilate(fr) & ~fr, -1)
    put(fr, 0.95)
    put(rect_mask(wx0 + 9, 702, wx0 + 90, 819), 0.5)
    put(rect_mask(wx0 + 45, 702, wx0 + 54, 819) | rect_mask(wx0 + 9, 756, wx0 + 90, 765), -1)
    put(rect_mask(wx0 + 18, 711, wx0 + 27, 720) | rect_mask(wx0 + 27, 720, wx0 + 36, 729), -1)   # glint
    sill = rect_mask(wx0 - 18, 828, wx0 + 117, 837)
    put(sill, 0.95)
    sn = cell_mask([rrect_pts(wx0 - 18, 801, wx0 + 117, 846, 16)]) & ~rect_mask(0, 828, 1920, 1080)
    snow(sn)
    fb = rect_mask(wx0 - 9, 837, wx0 + 108, 864)               # flower box (evergreen sprigs)
    put(fb, 0.62)
    put(rect_mask(wx0, 846, wx0 + 99, 855), -1)
DX0, DX1 = 216, 306
dm = rect_mask(DX0, 756, DX1, GROUND)
put(dilate(dm) & ~dm, -1)
put(dm, 0.95)
put(rect_mask(DX0 + 18, 864, DX1 - 18, 954) & ~rect_mask(DX0 + 27, 873, DX1 - 27, 945), -1)
wr = circle_mask((DX0 + DX1) / 2, 810, 27) & ~circle_mask((DX0 + DX1) / 2, 810, 13)
put(dilate(wr) & ~wr & dm, -1)
put(wr, 0.45)
put(rect_mask(256, 828, 266, 846), 0.95)
put(rect_mask(DX1 - 27, 900, DX1 - 18, 909), -1)
put(rect_mask(DX0 - 18, GROUND - 9, DX1 + 18, GROUND), 0.95)   # door step

# ----------------------------------------------------------------------------- big pine beside the chalet
pine(67, 48, [(0, 9), (7, 10), (15, 12), (25, 13), (36, 14)], GROUND)

# ----------------------------------------------------------------------------- right: the café
CX0, CEAVE = 1512, 621
cw = rect_mask(CX0, CEAVE, 1920, GROUND)
air(cw)
put(cw, 0.26)
for k, y in enumerate(range(CEAVE + 9, GROUND, 18)):          # bricks: carved bed joints + staggered heads
    put(cw & rect_mask(0, y, 1920, y + 9), -1)
    for x in range(CX0 + (27 if k % 2 else 0), 1920, 54):
        put(cw & rect_mask(x, y - 9, x + 9, y), -1)
roof = cell_mask([[(CX0 - 36, CEAVE), (CX0 + 36, 495), (1920, 495), (1920, CEAVE)]])
air(roof)
put(roof, 0.9)
for k, y in enumerate(range(504, CEAVE - 9, 27)):              # shingle rows: a carved course line,
    put(roof & rect_mask(0, y + 18, 1920, y + 27), -1)           # staggered tab joints every 72 px
    for x in range(CX0 + (36 if k % 2 else 0), 1920, 72):
        put(roof & rect_mask(x, y, x + 9, y + 18), -1)
gut = rect_mask(CX0 - 45, CEAVE - 9, 1920, CEAVE + 9)
put(gut, 0.95)
rs = cell_mask([[(CX0 + 9, 495), (CX0 + 45, 450), (1930, 450), (1930, 495)]])
air(rs)
snow(rs)
for k, x in enumerate(range(CX0 - 36, 1920, 45)):              # icicles under the gutter
    W.v[C(CEAVE + 9):C(CEAVE + 9) + 1 + k % 3, C(x)] = 0.62
# sign: a dense frame round paper, CAFE in dense glyphs (drawn after this layer)
SB0, SB1, SBT, SBB = 1566, 1890, 657, 783
sb = rect_mask(SB0, SBT, SB1, SBB)
air(sb)
put(sb, 0.95)
put(rect_mask(SB0 + 9, SBT + 9, SB1 - 9, SBB - 9), -1)
# awning: stripes, a scalloped edge, snow on top; the window under it; the door with a sconce
SW0, SW1 = 1575, 1764
awn = rect_mask(SW0 - 27, 819, SW1 + 27, 846)
asn = cell_mask([rrect_pts(SW0 - 36, 801, SW1 + 36, 828, 12)]) & ~rect_mask(0, 819, 1920, 1080)
air(awn | asn)
for k, x in enumerate(range(SW0 - 27, SW1 + 27, 27)):
    put(awn & rect_mask(x, 0, x + 27, 1080), 0.95 if k % 2 == 0 else 0.3)
    put(rect_mask(x + 9, 846, x + 18, 855), 0.95 if k % 2 == 0 else 0.3)
snow(asn)
win = rect_mask(SW0, 873, SW1, 954)
put(dilate(win) & ~win, -1)
put(win, 0.95)
put(rect_mask(SW0 + 9, 882, SW1 - 9, 945), 0.5)
put(rect_mask((SW0 + SW1) // 2 // P * P, 882, (SW0 + SW1) // 2 // P * P + 9, 945), -1)
put(rect_mask(SW0 + 27, 891, SW0 + 36, 900) | rect_mask(SW0 + 36, 900, SW0 + 45, 909), -1)
dd = rect_mask(1818, 828, 1890, GROUND)
put(dilate(dd) & ~dd, -1)
put(dd, 0.95)
put(rect_mask(1836, 846, 1872, 900), 0.5)
put(rect_mask(1872, 918, 1881, 927), -1)

# ----------------------------------------------------------------------------- lamp post (unlit), snow on its cap
LX = 1269
post = rect_mask(LX, 531, LX + 18, 945)
base = rect_mask(LX - 18, 936, LX + 36, GROUND) | rect_mask(LX - 9, 918, LX + 27, 936)
head = cell_mask([[(LX - 36, 459), (LX + 54, 459), (LX + 36, 522), (LX - 18, 522)]])
capm = rect_mask(LX - 45, 441, LX + 63, 459) | rect_mask(LX - 18, 432, LX + 36, 441)
ring_ = rect_mask(LX - 18, 522, LX + 36, 531)
air(post | base | head | capm | ring_)
put(post | base, 0.9)
put(post & rect_mask(0, 0, LX + 9, 1080), 0.6)
put(head, 0.2)
put(outline_mask(head), 0.9)
put(head & (rect_mask(LX - 9, 459, LX, 522) | rect_mask(LX + 18, 459, LX + 27, 522)), 0.9)
put(capm | ring_, 0.95)
lsn = cell_mask([rrect_pts(LX - 45, 405, LX + 63, 450, 18)]) & ~(capm | rect_mask(0, 441, 1920, 1080))
air(lsn)
snow(lsn)
W.v[C(459):C(459) + 2, C(LX - 45)] = 0.62
W.v[C(459), C(LX + 54)] = 0.62

# ----------------------------------------------------------------------------- snowman (bottom ball first)
SX = 1386
for (x, y, r) in ((SX, 909, 63), (SX, 810, 45), (SX, 738, 33)):
    m = circle_mask(x, y, r)
    air(m)
    W.put(m, -1)
    d = ((XS - x) * 0.6 + (YS - y) * 0.8) / r
    put(m & (d > 0.45), 0.3)                                    # shade crescent (lower right)
    put(outline_mask(m), 0.85)
for (x, y) in ((SX - 18, 729), (SX + 9, 729)):
    put(rect_mask(x, y, x + 9, y + 9), 0.95)                    # coal eyes
put(rect_mask(SX, 747, SX + 36, 756), 0.62)                     # carrot nose
for y in (792, 819, 846):
    put(rect_mask(SX - 4, y, SX + 5, y + 9), 0.95)              # buttons
scarf = rect_mask(SX - 36, 765, SX + 36, 783) | rect_mask(SX + 9, 783, SX + 27, 828)
put(scarf, 0.95)
put(rect_mask(SX + 9, 801, SX + 27, 810), -1)
hat = rect_mask(SX - 27, 657, SX + 27, 702) | rect_mask(SX - 45, 702, SX + 45, 711)
air(hat)
put(hat, 0.95)
put(rect_mask(SX - 27, 684, SX + 27, 693), 0.3)
for pts in ([(SX - 45, 801), (SX - 72, 783), (SX - 99, 756)], [(SX + 45, 801), (SX + 72, 783), (SX + 99, 765)]):
    put(polyline_mask(pts) & ~dilate(circle_mask(SX, 810, 45), 0), 0.85)

# ----------------------------------------------------------------------------- snowbanks at both sides
# low paper lumps along the snow line (outline on the sky side only, never along the frame edge or the
# bottom), a light shade texture on their lower right; the street shows below them
for mounds in (((54, 64), (153, 50)), ((378, 54), (468, 44)), ((1494, 58), (1593, 46), (1872, 66))):
    m = np.zeros((ROWS, COLS), bool)
    for (mx, rr) in mounds:
        m |= circle_mask(mx, 1008, rr)
    m &= rect_mask(0, 0, 1920, 1017)
    air(m & rect_mask(0, 0, 1920, 1008))
    W.put(m, -1)
    o = outline_mask(m) & (R_ < C(1008)) & (C_ > 0) & (C_ < COLS - 1)
    put(o, 0.62)
    for (mx, rr) in mounds:                                          # shade crescent, lower right
        d = ((XS - mx) * 0.7 + (YS - 1008) * 0.7) / rr
        put(m & ~o & (d > 0.25) & np.broadcast_to(YS > 960, m.shape) & circle_mask(mx, 1008, rr), 0.14)
W.emit(s)
W0v = W.v.copy()
s.bitmap_text(SB0 + 27, SBT + 18, 'CAFE', 0.95, size=12, gap=2)

# ----------------------------------------------------------------------------- falling flakes (a new layer)
W = CellPaint()
calm = (CALM[0] - 27, CALM[1] - 27, CALM[2] + 27, CALM[3])
placed = []


def can_place(x, y, rad):
    if calm[0] <= x <= calm[2] and calm[1] <= y <= calm[3]:
        return False
    return all(abs(x - a) > rad or abs(y - b) > rad for a, b in placed)


def under(x, y):
    v = W0v[C(y), C(x)]
    return 0 if np.isnan(v) else v


for _ in range(600):                                            # far flakes: one cell
    x = int(rng.integers(1, COLS - 1)) * P; y = int(rng.integers(1, C(GROUND) - 2)) * P
    if len(placed) > 60 or not can_place(x, y, 72):
        continue
    placed.append((x, y))
    W.v[C(y), C(x)] = -1 if under(x, y) > 0.4 else 0.45
for _ in range(600):                                            # near flakes: plus-shaped, lower
    x = int(rng.integers(2, COLS - 2)) * P; y = int(rng.integers(C(360), C(GROUND) - 3)) * P
    if len(placed) > 85 or not can_place(x, y, 90):
        continue
    placed.append((x, y))
    dark = under(x, y) > 0.4
    for dx, dy in ((0, 0), (9, 0), (-9, 0), (0, 9), (0, -9)):
        W.v[C(y + dy), C(x + dx)] = -1 if dark else (0.62 if (dx, dy) == (0, 0) else 0.4)
W.emit(s)

if __name__ == '__main__':
    render(s, 'snow_day', 'light', 'r3_500_hill_clouds')
    crops('snow_day', [
        ('chalet: roof band + snow, siding, windows, door, chimney', (0, 300, 560, 1000), 'r3_500_hill_clouds', (1100, 380, 1660, 1080)),
        ('pine on 45-degree tiers, snow on the shoulders', (468, 400, 740, 1000), 'r3_390_patio', (1380, 140, 1652, 740)),
        ('lamp post, snowman, café (sign, awning, shingles)', (1200, 380, 1920, 1000), 'r3_80_building_site', (1080, 260, 1800, 880)),
        ('clouds + far hills behind the square, snowy street', (540, 0, 1400, 300), 'r3_500_hill_clouds', (1000, 60, 1860, 360)),
    ])
