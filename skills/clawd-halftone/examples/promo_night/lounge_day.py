"""Scene 1 — lounge_day (light): a cosy lounge in daylight, for the "video" GIFs.

Left → right: the window (sun, a cloud, a far city low in the glass) between tied-back curtains · the
armchair (the key piece, dense, its parts separated by carved air, lit rims on the upper left) in
front of it · the floor lamp (unlit, a soft drum shade) beside the chair · [the GIF square: paper wall,
the floor band and the rug only] · a picture over the square · the side table with the radio, the
wall clock over it · the bookshelf (books, photo, vase, globe, baskets, a pilea on top).
Light from the window (upper left): rounded things carry their hard shade band on the right.
Tones (ink on cream): wall 0 · floor .18 · curtains .26/.5 · panels .26-.3 · lines .42-.62 · sun .36 ·
city .2 · armchair + radio .9 (lit rims .6) · books .3/.55/.9 · rug .6.
"""
import numpy as np

from common import Svg, P, render, crops
from cellkit import gap, box, cell_mask, cells, CellPaint, outline_mask, dilate, circle_mask, polyline_mask, ellipse_pts, lump_shade
from daykit import (plant, floor, books, curtain, rod, rug, clock, frame_pic, rect_mask, rrect_pts, lit_rim, put_parts,
                    C, YS, XS)

s = Svg(theme='light')
ink = s.ink

# ----------------------------------------------------------------------------- floor + rug
floor(s)
rug(s, 594, 1323, 990)

# ----------------------------------------------------------------------------- window: sun, cloud, far city
WX0, WY0, WX1, WY1 = 144, 126, 513, 594
MX, TY = 324, 405                                          # mullion column, transom row
for (x0, y0, x1, y1) in ((WX0 + 9, TY + 9, MX, WY1), (MX + 9, TY + 9, WX1 - 9, WY1)):
    cl = s.clip_rect(x0, y0, x1 - x0, y1 - y0)
    with s.plane(clip=cl):                                 # far city low in the lower panes
        s.skyline(x0 - 27, x1 + 27, y1, [99, 144, 72, 126, 108, 162], v=0.2, seed=3 + x0, widths=(54, 99))
s.sun(234, 252, 40, v=0.36, ray_v=0.3, rays=12, ray_len=22, gap=18)
cp = CellPaint()                                           # a cloud: lumpy top densest, base fading
m = np.zeros((120, 213), bool)
for cx, cy, r in ((380, 280, 30), (418, 256, 38), (462, 274, 30), (440, 296, 26), (398, 300, 24)):
    m |= circle_mask(cx, cy, r)
m &= np.broadcast_to(YS <= 306, m.shape)
m &= rect_mask(MX + 18, WY0 + 18, WX1 - 18, TY - 9)
cp.put(m, 0.2)
cp.put(m & np.broadcast_to(YS < 276, m.shape), 0.38)
cp.put(m & np.broadcast_to(YS > 290, m.shape) & (XS < 410), 0.1)
cp.emit(s)
s.frame(WX0, WY0, WX1, WY1, 0.62)
s.col(MX, WY0, WY1, 0.62)
s.row(WX0, WX1, TY, 0.62)
box(s, WX0 - 27, WY1, WX1 + 27, WY1 + 18, 0.45)          # sill (2 rows) + its apron
box(s, WX0 - 9, WY1 + 18, WX1 + 9, WY1 + 27, 0.62)

# curtains outside the frame (so the frame line stays whole), rod with finials
rod(s, 45, 612, 99)
curtain(s, 45, 135, 108, 639, 432, body=0.26, shade=0.55, pleat=4, gather=0.5, flare=0.85)
curtain(s, 612, 522, 108, 639, 432, body=0.26, shade=0.55, pleat=4, gather=0.5, flare=0.85)

# ----------------------------------------------------------------------------- armchair (key, dense)
ch = CellPaint()
back = cell_mask([rrect_pts(180, 657, 468, 828, 54)])
armL = cell_mask([rrect_pts(108, 747, 207, 945, 40)])
armR = cell_mask([rrect_pts(441, 747, 540, 945, 40)])
cush = cell_mask([rrect_pts(216, 801, 432, 873, 14)])
skirt = rect_mask(216, 882, 432, 945)
put_parts(ch, [back, skirt, cush, armL, armR], 0.9, lit_v=0.6, k=2)
for m_ in (armL, armR):                                    # the arm's roll: a carved line under it
    ch.put(m_ & np.broadcast_to((YS > 801) & (YS < 810), m_.shape) & np.broadcast_to(XS > 117, m_.shape), -1)
for bx, by in ((243, 702), (324, 702), (405, 702), (283, 747), (364, 747)):
    ch.v[C(by), C(bx)] = -1                                # tufting buttons
ch.put(rect_mask(216, 918, 432, 927), -1)                  # skirt piping
for lx in (135, 486):                                      # turned legs
    ch.put(rect_mask(lx, 945, lx + 27, 972), 0.95)
ch.put(rect_mask(117, 945, 531, 954) & ~rect_mask(135, 945, 162, 954) & ~rect_mask(486, 945, 513, 954), np.nan)
with s.cut():
    ch.emit(s)

# ----------------------------------------------------------------------------- floor lamp (unlit)
LX = 648                                                     # pole column
LT, LB = 387, 486
with s.cut():
    shade_m = cell_mask([[(LX - 45, LT), (LX + 54, LT), (LX + 81, LB), (LX - 72, LB)]])
    cells(s, shade_m, 0.22)
    cells(s, shade_m & np.broadcast_to(XS > LX + 24, shade_m.shape), 0.45)
    s.row(LX - 72, LX + 81, LB - 9, 0.62)
    s.row(LX - 45, LX + 54, LT, 0.62)
    s.col(LX, LB, 945, 0.62)
    box(s, LX - 36, 945, LX + 45, 963, 0.9)
    box(s, LX - 27, 936, LX + 36, 945, 0.9)
    box(s, LX - 9, LT - 18, LX + 18, LT, 0.62)             # finial
box(s, LX + 27, LB, LX + 36, LB + 63, 0.45)                # pull chain
box(s, LX + 18, LB + 63, LX + 45, LB + 81, 0.85)

# ----------------------------------------------------------------------------- picture over the square
ix0, iy0, ix1, iy1 = frame_pic(s, 819, 180, 1098, 378)
mtn = cell_mask([[(ix0, iy1), (ix0, iy1 - 36), (900, 252), (945, 297), (990, 243), (ix1, iy1 - 54), (ix1, iy1)]])
mtn &= rect_mask(ix0, iy0, ix1, iy1)
cp2 = CellPaint()
cp2.put(mtn, 0.55)
cp2.put(mtn & np.broadcast_to(XS > 950, mtn.shape) & ~np.broadcast_to(XS > 1000, mtn.shape), 0.85)
cp2.put(mtn & np.broadcast_to(YS < 270, mtn.shape), -1)
cp2.put(rect_mask(ix0, iy1 - 18, ix1, iy1), 0.3)
cp2.emit(s)
box(s, 1026, 225, 1044, 243, 0.36)

# ----------------------------------------------------------------------------- side table + radio
TX0, TX1, TT = 1269, 1458, 783
with s.cut():
    box(s, TX0, TT, TX1, TT + 18, 0.62)                      # top (2 rows)
    s.frame(TX0 + 18, TT + 18, TX1 - 18, TT + 63, 0.62, fill=0.26)   # apron with a drawer
    for lx in (TX0 + 18, TX1 - 36):
        box(s, lx, TT + 63, lx + 18, 972, 0.9)
    box(s, TX0 + 36, 909, TX1 - 36, 918, 0.62)              # lower shelf
mx_ = (TX0 + TX1) // 2 // P * P
box(s, mx_ - 9, TT + 36, mx_ + 18, TT + 45, 0.9)           # drawer pull
for k, (x0, w, v) in enumerate(((TX0 + 54, 117, 0.55), (TX0 + 63, 99, 0.9), (TX0 + 45, 126, 0.3))):
    box(s, x0, 909 - 18 * (k + 1), x0 + w, 909 - 18 * k, v)   # magazines on the lower shelf

# the radio: a dense cabinet; a round speaker (light cloth, a carved ring, the cone's centre), a dial
# window with its needle, two knobs ringed by air, a handle, the antenna
RX0, RX1, RT, RB = 1278, 1449, 666, 783
rad = cell_mask([rrect_pts(RX0, RT, RX1, RB, 27)])
rp = CellPaint()
rp.put(rad, 0.9)
gcx, gcy, gr = RX0 + 63, RT + 58, 45
grille = circle_mask(gcx, gcy, gr)
rp.put(grille, -1)                                          # carved ring round the speaker
rp.put(circle_mask(gcx, gcy, gr - 9), 0.3)                  # the cloth
rp.put(circle_mask(gcx, gcy, 20) & ~circle_mask(gcx, gcy, 11), -1)   # the cone's ring
rp.put(circle_mask(gcx, gcy, 11), 0.9)
rp.put(rect_mask(RX1 - 72, RT + 18, RX1 - 18, RT + 54), -1)  # dial window
rp.put(rect_mask(RX1 - 63, RT + 36, RX1 - 27, RT + 45), 0.3)  # scale
rp.put(rect_mask(RX1 - 45, RT + 27, RX1 - 36, RT + 45), 0.95)  # needle
for kx in (RX1 - 72, RX1 - 45):                              # two knobs, ringed by air
    rp.put(rect_mask(kx - 9, RT + 63, kx + 27, RT + 99) & ~rect_mask(kx, RT + 72, kx + 18, RT + 90), -1)
    rp.put(rect_mask(kx, RT + 72, kx + 18, RT + 90), 0.45)
with s.cut():
    rp.emit(s)
    s.col(RX0 + 36, RT - 27, RT, 0.62); s.col(RX1 - 45, RT - 27, RT, 0.62)   # handle
    s.row(RX0 + 36, RX1 - 36, RT - 36, 0.62)
    s.col(RX1 - 18, RT - 90, RT, 0.45)                                        # antenna
    box(s, RX1 - 27, RT - 99, RX1, RT - 90, 0.85)

# wall clock over the side table (ten past ten)
clock(s, 1359, 441, 72, h_ang=300, m_ang=60)

# ----------------------------------------------------------------------------- bookshelf (right)
BS0, BS1, BST, BSB = 1521, 1881, 279, 972
SH = [BST, 450, 621, 792]                                  # shelf boards (top of each, 2 rows)
with s.cut():
    s.frame(BS0, BST, BS1, BSB, 0.62)
    for y in SH:
        box(s, BS0, y, BS1, y + 18, 0.62)
    box(s, BS0 - 18, BST - 18, BS1 + 18, BST, 0.62)          # top board overhang
    box(s, BS0, BSB - 36, BS1, BSB, 0.62)                    # plinth
    box(s, BS0 + 9, BSB, BS0 + 36, BSB + 9, 0.9); box(s, BS1 - 36, BSB, BS1 - 9, BSB + 9, 0.9)
gap(s, BS0 + 18, BSB - 27, BS1 - BS0 - 36, 9)               # plinth groove
# shelf 1 (base y 450): a run of books, a leaning one, a small framed photo
x = books(s, BS0 + 18, 450, [(3, 126, 0.9, 0), (2, 135, 0.55, 0), (3, 117, 0.42, 0), (2, 108, 0.9, 0), (3, 126, 0.55, 0), (2, 99, 0.9, 36)])
s.frame(x + 54, 450 - 90, x + 153, 450, 0.85)
s.frame(x + 72, 450 - 72, x + 135, 450 - 18, 0.3, fill=0.3)
# shelf 2 (base y 621): vase with a sprig, a stack of books lying flat, books
s.cyl(BS0 + 27, 621 - 90, BS0 + 81, 621, 0.26, 0.55, light_left=True, band=0.34, rx=14)
box(s, BS0 + 36, 621 - 99, BS0 + 72, 621 - 90, 0.62)
for ang in (-25, 5, 35):
    s.leaf(BS0 + 54, 621 - 99, ang, 63, 22, dark=0.9, lit=0.6, edge=None, midrib=0, curl=0.1)
for k, (w, v) in enumerate(((171, 0.55), (153, 0.9), (180, 0.42))):
    box(s, BS0 + 117, 621 - 27 * (k + 1), BS0 + 117 + w, 621 - 27 * k - 9, v)
books(s, BS0 + 315, 621, [(2, 117, 0.9, 0), (2, 108, 0.55, 0)])
# shelf 3 (base y 792): globe on a stand + books
gx, gy = BS0 + 72, 792 - 81
globe = circle_mask(gx, gy, 45)
gp = CellPaint()
gp.put(globe, 0.3)
_, _, gsh = lump_shade(gx, gy, 45, globe, lit_t=0.5, shade_t=0.15)
gp.put(gsh, 0.6)
gp.put(cell_mask([[(gx - 18, gy - 36), (gx + 9, gy - 27), (gx + 18, gy), (gx - 9, gy + 18), (gx - 27, gy - 9)]]) & globe, 0.9)
gp.put(outline_mask(globe), 0.62)
gp.emit(s)
box(s, gx - 27, 783, gx + 27, 792, 0.85); box(s, gx - 4.5, gy + 45, gx + 4.5, 783, 0.85)
books(s, BS0 + 162, 792, [(3, 126, 0.55, 0), (3, 135, 0.9, 0), (2, 117, 0.42, 0), (3, 126, 0.55, 0), (2, 108, 0.9, 0)])
# shelf 4 (base y 936): two baskets
for bx0, v in ((BS0 + 27, 0.3), (BS0 + 198, 0.55)):
    box(s, bx0, 936 - 108, bx0 + 144, 936, v)
    if v == 0.3:
        for yy_ in range(936 - 90, 936, 18):
            gap(s, bx0 + 9, yy_, 126, 9)
    else:
        box(s, bx0 + 54, 936 - 90, bx0 + 90, 936 - 72, 0.95)
        gap(s, bx0 + 9, 936 - 54, 126, 9)
# snake plant on top of the shelf: upright sword leaves split lit/dark, air between them
PX, PB = 1782, BST - 18
pc = CellPaint()
plant(pc, [(PX + dx, PB - 63, ang, ln, wd, 0.02, 0) for dx, ang, ln, wd in
           ((-9, -32, 99, 36), (18, 32, 90, 36), (-27, -12, 135, 40), (27, 13, 126, 40), (0, 2, 180, 44))])
pc.emit(s)
s.pot(PX, PB, 108, 81, body=0.2, rim=0.3, edge=0.62, shade=0.45)
# a small stack of books + a mug at the other end of the top
for k, (w, v) in enumerate(((144, 0.9), (126, 0.42), (153, 0.55))):
    box(s, BS0 + 9, BST - 18 - 27 * (k + 1), BS0 + 9 + w, BST - 18 - 27 * k - 9, v)

if __name__ == '__main__':
    render(s, 'lounge_day', 'light', 'r3_390_patio')
    crops('lounge_day', [
        ('window + curtains + sun', (36, 80, 640, 650), 'r3_390_patio', (340, 50, 944, 620)),
        ('armchair + floor lamp (key piece)', (90, 370, 740, 990), 'r3_390_patio', (0, 370, 650, 990)),
        ('radio, side table, bookshelf', (1260, 260, 1900, 990), 'r3_390_patio', (1280, 260, 1920, 990)),
        ('rug on the floor band', (540, 940, 1380, 1080), 'r3_500_hill_clouds', (540, 940, 1380, 1080)),
    ])
