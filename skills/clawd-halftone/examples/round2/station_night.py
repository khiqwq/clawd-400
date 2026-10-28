"""Scene 2 — station_night (dark): a small city platform at night, side view.

Far → near: city skyline (faint) · station canopy behind the train · the passenger car (lit windows,
door left of centre, bogies hidden) · the platform (edge stripe, tiles) with two lamp posts and their
pools, the clock on a post (23:59), the name board 城南站 with a bench under it.
Clawd stands on the platform at x 260-485, feet y 975: the area behind him is the car's quiet lower body.
Tones: sky/train body 0-.08 · skyline .12 · canopy .32 · platform .06→.2 · roof/stripe .5 · lit windows,
lamps, clock digits .85-1.
"""
import numpy as np

from common import Svg, P, render, crops
from extras import gap, box, checker, dashes, star, cell_mask, cells, top_edge_mask, bez, ellipse_pts, outline_mask

s = Svg(theme='dark')
ink = s.ink

# ----------------------------------------------------------------------------- far: city skyline
# separate towers with sky between them, a crisp top row each, sparse lit windows — far = simple
rng = np.random.default_rng(7)
x = 18
while x < 1920:
    w = int(rng.integers(9, 16)) * P
    h = int(rng.choice([8, 11, 14, 17, 21, 24])) * P
    top = 216 - h
    box(s, x, top, x + w, 216, 0.07)
    s.row(x, x + w, top, 0.22)
    for yy in range(top + 18, 207, 27):
        for xx in range(x + 18, x + w - 9, 27):
            if rng.random() < 0.18:
                s.rect(xx, yy, P, P, fill=ink(0.5))
    if rng.random() < 0.35:                                  # antennas on some roofs, a red-light dot
        ax = x + w // 2 // P * P
        s.col(ax, top - 45, top, 0.2)
        s.rect(ax, top - 54, P, P, fill=ink(0.6))
    x += w + int(rng.integers(2, 6)) * P
for sx, sy, v, arm in ((126, 45, 0.35, 1), (468, 81, 0.25, 0), (783, 36, 0.3, 0), (1125, 63, 0.4, 1),
                       (1458, 27, 0.25, 0), (1701, 90, 0.3, 0), (1863, 45, 0.35, 1)):
    star(s, sx, sy, v, arm)

# ----------------------------------------------------------------------------- the canopy behind the train
CF0, CF1 = 216, 243                                          # fascia rows
box(s, 0, CF0, 1920, CF1, 0.32)
s.row(0, 1920, CF0 - 9, 0.2)                                 # roof edge flashing
for xx in range(0, 1920, 27):                                # dagger-board valance: pointed boards
    s.rect(xx, CF1, 18, 18, fill=ink(0.32))
    s.rect(xx + 4.5, CF1 + 18, 9, 9, fill=ink(0.32))
for cx_ in (189, 765, 1341, 1872):                           # columns + brackets, down behind the roof
    box(s, cx_ - 9, CF1, cx_ + 9, 360, 0.26)
    s.line(cx_ - 9, 315, cx_ - 63, CF1 + 9, ink(0.26), 9)
    s.line(cx_ + 9, 315, cx_ + 63, CF1 + 9, ink(0.26), 9)

# ----------------------------------------------------------------------------- the passenger car
CAR0, CAR1 = 36, 1881                                        # car ends (gangways beyond)
BODY = 0.18
RT, BT, BB = 351, 378, 783                                   # roof top, body top, body bottom
with s.cut():
    # roof: a band with the end curves, vents on top
    s.rect(CAR0, RT, CAR1 - CAR0, BT - RT + 18, fill=ink(0.45), rx=18)
    for vx in (252, 612, 1044, 1404, 1728):
        box(s, vx, RT - 27, vx + 90, RT, 0.3)
        gap(s, vx + 9, RT - 18, 72, 9)
    # body: a body-level field (like the kitchen ref's cabinets); its structure is carved out of it below
    s.rect(CAR0, BT, CAR1 - CAR0, BB - BT, fill=ink(BODY), rx=18)
s.row(CAR0 + 18, CAR1 - 18, BT, 0.62)                       # gutter line under the roof
# windows: lit fields, carved interior (luggage rail, straps, seat backs)
WT, WB = 441, 567
def car_window(x0, w=162, rider=False):
    """A lit window: a bright field with the interior carved out of it as dark silhouettes (the refs'
    way): the luggage rail, two seat backs with rounded tops, optionally a passenger's head."""
    s.rect(x0 - 9, WT - 9, w + 18, WB - WT + 18, fill=s.paper, rx=20)   # rubber surround (carved)
    s.rect(x0, WT, w, WB - WT, fill=ink(0.86), rx=14)
    gap(s, x0 + 18, WT + 18, w - 36, 9)                      # luggage rail
    for k in range(3):                                       # rail brackets
        gap(s, x0 + 27 + k * ((w - 63) // 2 // P * P), WT + 27, 9, 9)
    for sxx in (x0 + 18, x0 + w - 72):                       # two seat backs
        s.rect(sxx, WB - 63, 54, 63, fill=s.paper, rx=16)
        box(s, sxx + 18, WB - 54, sxx + 36, WB - 45, 0.86)   # a button / headrest tab
    if rider:                                                # a passenger between the seat backs
        cx = x0 + w / 2
        s.circle(cx, WB - 77, 20, fill=s.paper)
        s.rect(cx - 27, WB - 54, 54, 54, fill=s.paper, rx=14)


for wx, rider in ((144, False), (324, True), (504, False), (945, False), (1125, False), (1359, True),
                  (1539, False), (1719, False)):
    car_window(wx, w=144, rider=rider)
# livery: a double stripe under the windows, a thin one over them
gap(s, CAR0 + 9, 594, CAR1 - CAR0 - 18, 9)
s.row(CAR0 + 9, CAR1 - 9, 603, 0.62, rows=2)
gap(s, CAR0 + 9, 621, CAR1 - CAR0 - 18, 9)
s.row(CAR0 + 9, CAR1 - 9, 630, 0.45)
gap(s, CAR0 + 9, 639, CAR1 - CAR0 - 18, 9)
gap(s, CAR0 + 9, 414, CAR1 - CAR0 - 18, 9)                  # a carved line over the windows
# the door, left of centre: frame, two leaves with tall lit windows, handles, step
DX0, DX1 = 702, 900
gap(s, DX0 - 9, 396, DX1 - DX0 + 18, BB - 396)              # door opening carved through the stripes
box(s, DX0, 405, DX1, BB, BODY + 0.08)                       # the leaves, a hair brighter than the body
s.frame(DX0, 405, DX1, BB, 0.62)
gap(s, (DX0 + DX1) // 2 // P * P, 414, 9, BB - 414)         # leaf joint (carved)
for lx in (DX0 + 27, (DX0 + DX1) // 2 // P * P + 27):
    s.rect(lx - 9, 432, 72, 180, fill=s.paper, rx=12)
    s.rect(lx, 441, 54, 162, fill=ink(0.86), rx=8)
    gap(s, lx + 18, 459, 18, 9)
box(s, (DX0 + DX1) // 2 // P * P - 18, 648, (DX0 + DX1) // 2 // P * P, 684, 0.9)
box(s, (DX0 + DX1) // 2 // P * P + 9, 648, (DX0 + DX1) // 2 // P * P + 27, 684, 0.9)
box(s, DX0 - 18, BB - 9, DX1 + 18, BB + 9, 0.5)             # step plate
# car number + a small destination board over the door
s.seg7(1530, 666, '07', 0.6, ghost=0)
box(s, 738, 369, 864, 396, 0.86)
gap(s, 756, 378, 18, 9); gap(s, 792, 378, 36, 9)
# skirt (the bogies are hidden by the platform)
box(s, CAR0 + 36, 738, CAR1 - 36, BB, 0.2)
for gx in range(CAR0 + 72, CAR1 - 60, 54):
    gap(s, gx, 747, 9, 27)
# gangways at both ends (bellows: vertical ribs)
for gx0, gx1 in ((0, CAR0 - 9), (CAR1 + 9, 1920)):
    for xx in range(gx0, gx1, 18):
        s.col(xx, 405, 765, 0.3)

# ----------------------------------------------------------------------------- platform
PE = 801                                                     # platform edge (far side, against the car)
# surface: a faint uniform field (like the music-room floor); the lamp pools are added below, then the
# tile joints are carved last so they stay crisp inside the light
box(s, 0, PE + 36, 1920, 1080, 0.07)
# coping + the edge stripe (tactile dashes)
box(s, 0, PE, 1920, PE + 18, 0.55)
s.row(0, 1920, PE + 18, 0.0)
for xx in range(0, 1920, 27):
    box(s, xx, PE + 27, xx + 18, PE + 36, 0.9)


# ----------------------------------------------------------------------------- lamp posts + pools
def lamp_post(x, top=288, base=966):
    """A station lamp: cast base, pole, a lantern head with a lit pane under a cap; light pool on the
    platform. x = left edge of the 2-cell pole (multiple of 9)."""
    with s.cut():
        box(s, x - 18, base - 45, x + 36, base, 0.62)          # base
        box(s, x - 9, base - 63, x + 27, base - 45, 0.62)
        box(s, x, top + 81, x + 18, base - 63, 0.62)           # pole
        box(s, x - 9, top + 63, x + 27, top + 81, 0.62)        # collar
        lant = cell_mask([[(x - 36, top), (x + 54, top), (x + 36, top + 63), (x - 18, top + 63)]])
        cells(s, lant, 1.0)                                    # lit glass, wider at the top
        box(s, x - 54, top - 18, x + 72, top, 0.7)             # cap
        box(s, x - 27, top - 36, x + 45, top - 18, 0.7)
        box(s, x, top - 54, x + 18, top - 36, 0.7)             # finial
        box(s, x - 27, top + 63, x + 45, top + 72, 0.7)        # bottom ring
    for bx_ in (x - 9, x + 18):                                # glazing bars (carved): three panes
        gap(s, bx_, top + 9, 9, 54)
    s.glow(x + 9, top + 27, 81, 0.14, mid=0.3)


LAMPS = (72, 1305)
for lx in LAMPS:                                               # pools of light on the platform (before
    s.glow(lx + 9, 948, 270, 0.42, mid=0.45, ry=81)            # the joints, so the tiles show in them)
# tile joints: rows spaced wider toward the viewer (depth without perspective), staggered verticals
JR = [855, 900, 954, 1017]
for jy in JR:
    gap(s, 0, jy, 1920, 9)
bands = [PE + 36] + [j + 9 for j in JR] + [1080]
for k in range(len(bands) - 1):
    step = (90, 108, 126, 144, 162)[k]
    for jx in range((k % 2) * step // 2 // P * P, 1920, step // P * P):
        gap(s, jx, bands[k], 9, (JR + [1080])[k] - bands[k])
for lx in LAMPS:
    lamp_post(lx)

# ----------------------------------------------------------------------------- clock on a post (23:59)
CK0, CK1, CKT = 945, 1197, 630
with s.cut():
    box(s, CK0, CKT, CK1, CKT + 99, 0.62)
    box(s, (CK0 + CK1) // 2 // P * P - 9, CKT + 99, (CK0 + CK1) // 2 // P * P + 9, 966, 0.55)
    box(s, (CK0 + CK1) // 2 // P * P - 36, 948, (CK0 + CK1) // 2 // P * P + 36, 966, 0.62)
    box(s, (CK0 + CK1) // 2 // P * P - 27, CKT - 18, (CK0 + CK1) // 2 // P * P + 27, CKT, 0.62)
gap(s, CK0 + 9, CKT + 9, CK1 - CK0 - 18, 81)
s.seg7(CK0 + 27, CKT + 18, '23:59', 1.0, ghost=0)

# ----------------------------------------------------------------------------- name board 城南站 + bench
NB0, NB1, NBT, NBB = 1404, 1854, 576, 738
with s.cut():
    box(s, NB0, NBT, NB1, NBB, 0.62)
    for px in (NB0 + 9, NB1 - 27):                            # posts down to the platform
        box(s, px, NBB, px + 18, 966, 0.55)
gap(s, NB0 + 9, NBT + 9, NB1 - NB0 - 18, NBB - NBT - 18)
s.row(NB0 + 18, NB1 - 18, NBB - 27, 0.3)                     # underline
tw = s.bitmap_text(NB0 + 45, NBT + 18, '城南站', 0.95, size=12, gap=2)

# bench: slatted back + seat, cast-iron ends
BX0, BX1 = 1485, 1773
with s.cut():
    for y in (858, 885):
        box(s, BX0 + 18, y, BX1 - 18, y + 18, 0.5)           # back slats
    box(s, BX0, 921, BX1, 939, 0.62)                         # seat edge
    for ex in (BX0 + 18, BX1 - 45):                          # cast-iron ends: arm, leg
        box(s, ex, 849, ex + 27, 966, 0.85)
        box(s, ex - 9, 912, ex + 36, 921, 0.85)
gap(s, BX0 + 18, 876, BX1 - BX0 - 36, 9)

if __name__ == '__main__':
    render(s, 'station_night', 'dark', 'v1_415_bedroom_disco')
    crops('station_night', [
        ('lit car windows, door (carved interiors)', (120, 330, 920, 800), 'v1_12_kitchen', (980, 400, 1780, 870)),
        ('clock 23:59 + name board + bench', (930, 560, 1880, 980), 'v1_415_bedroom_disco', (0, 280, 950, 700)),
        ('lamp post + pool of light', (0, 200, 400, 1080), 'v1_300_fireplace', (1080, 200, 1480, 1080)),
    ])
