"""home_day (light) — a cosy living room in daylight.

Left -> right: a bookshelf (books, a clock, a vase with a sprig, a book stack, a globe, baskets; a trailing
pothos on top) · a snake plant in a floor pot · the big window over the sofa (the sun with ray dashes, a
small cloud, the far city along the sill, a rolled-up blind) · the sofa (Clawd
stands in front of it, centre, x 850-1075, feet y 975) with two throw pillows · a floor lamp under a framed
picture · a bird of paradise in a big pot. A rug on the floor band.
Light from the upper left: rounded things carry a hard shade step on the right.
Tones (ink on cream): wall / sky 0 · floor .18 · panels and cushions .22-.3 · lines .6-.75 · sun .38 ·
city .22 · the dense plants, a pillow, the legs .95.
"""
import math

import numpy as np

from canvas import (XS, YS, Canvas, R, rrect, circ, ell, poly, line, edge, grow, shrink, shift, right_of, below,
                    cols_every, rows_every, checker, empty, crops, stand_in, ck, P)
from daykit import leaf, pot

c = Canvas('light')
rng = np.random.default_rng(5)
FLOOR = 981

# ----------------------------------------------------------------------------- window: sun, cloud, far city
WX0, WY0, WX1, WY1 = 621, 108, 1305, 585
glass = R(WX0 + 9, WY0 + 9, WX1 - 9, WY1)
# far city along the sill: flat .22 blocks, paper window gaps, no outlines (far = simple)
x = WX0 + 9
for h, w in ((90, 72), (135, 63), (72, 90), (117, 54), (153, 72), (99, 81), (72, 63), (126, 72), (81, 63), (108, 72)):
    if x >= WX1 - 9:
        break
    m = R(x, WY1 - h, min(x + w, WX1 - 9), WY1) & glass
    c.put(m, .18)
    for yy in range(WY1 - h + 18, WY1 - 18, 27):
        for xx in range(x + 18, x + w - 18, 27):
            c.carve(R(xx, yy, xx + 9, yy + 9) & m)
    x += w + 9
# the sun: a flat disc .38, rays as 2-cell dashes
SX, SY, SR = 801, 270, 63
c.put(circ(SX, SY, SR), .38)
for k in range(12):
    a = 2 * math.pi * k / 12
    p0 = (SX + (SR + 27) * math.cos(a), SY + (SR + 27) * math.sin(a))
    p1 = (SX + (SR + 50) * math.cos(a), SY + (SR + 50) * math.sin(a))
    c.put(line([p0, p1]) & glass, .4)
# a small cloud: lumpy top denser, base fading
cl = (circ(1107, 234, 30) | circ(1152, 214, 37) | circ(1199, 234, 27)) & ~below(243) | R(1062, 234, 1242, 252)
c.put(cl & glass, .14)
c.put(cl & ~below(216) & glass, .3)
c.put(ck.top_edge_mask(cl) & glass, .38)
# frame: one crisp line, the centre mullion, the sill (two rows), a rolled-up blind with its cord
c.put(edge(R(WX0, WY0, WX1, WY1 + 9)), .6)
c.put(R(954, WY0, 963, WY1), .6)
c.put(R(WX0 - 27, WY1, WX1 + 27, WY1 + 18), .45)
c.put(R(WX0 - 27, WY1, WX1 + 27, WY1 + 9), .6)
c.put(R(WX0 + 18, WY0 + 9, WX1 - 18, WY0 + 36), .3)
c.put(R(WX0 + 18, WY0 + 27, WX1 - 18, WY0 + 36), .5)

# ----------------------------------------------------------------------------- picture on the wall + floor lamp
PX0, PY0, PX1, PY1 = 1332, 171, 1530, 333
frame = R(PX0, PY0, PX1, PY1)
c.put(frame & ~shrink(frame, 2), .9)
c.put(edge(shrink(frame, 4)), .4)
inner = shrink(frame, 5)
c.put(poly([(PX0, 318), (1386, 282), (1413, 291), (1449, 255), (1494, 288), (PX1, 300), (PX1, PY1), (PX0, PY1)]) & inner, .62)
c.put(poly([(PX0, 318), (1413, 300), (1458, 309), (PX1, 297), (PX1, PY1), (PX0, PY1)]) & inner, .9)
c.put(circ(1386, 232, 14) & inner, .45)
c.put(R(1427, 117, 1436, PY0), .4)                                     # wire to the nail
c.put(R(1418, 108, 1445, 126), .75)


def floor_lamp(lx, top=387, base=972):
    """A floor lamp (off, daytime): a cell-exact drum shade wider at the bottom with a hard shade band on
    the right, rim rows, a one-cell pole, a pull switch, a dense base. lx = the pole cell's left edge."""
    bot = top + 99
    shade = poly([(lx - 45, top), (lx + 54, top), (lx + 90, bot), (lx - 81, bot)])
    c.cut(shade | R(lx - 81, top - 9, lx + 90, bot + 9))
    c.put(shade, .26)
    c.put(shade & right_of(lx + 36), .5)
    c.put(R(lx - 81, bot, lx + 90, bot + 9), .75)
    c.put(R(lx - 45, top - 9, lx + 54, top), .75)
    c.carve(R(lx - 63, bot - 27, lx + 72, bot - 18) & shade)           # a carved band on the shade
    c.put(R(lx, bot + 9, lx + 9, base - 18), .75)
    c.put(R(lx + 9, bot + 99, lx + 18, bot + 171), .45)                # pull cord
    c.put(rrect(lx + 9, bot + 171, lx + 27, bot + 189, 4), .8)
    c.put(rrect(lx - 45, base - 18, lx + 54, base, 8), .95)


floor_lamp(1422)

# ----------------------------------------------------------------------------- floor band, skirting, rug
c.put(R(0, FLOOR, 1920, 1080), .18)
c.put(R(0, 963, 1920, 972), .4)
RG0, RG1, RGT, RGB = 540, 1386, 990, 1071
rug = R(RG0, RGT, RG1, RGB)
c.cut(rug)
c.put(rug, .7)
c.carve(edge(shrink(rug, 1)))                                          # inner border line
c.put(edge(shrink(rug, 2)) & checker(), .95)                           # a dotted dense band inside it
for k, x in enumerate(range(RG0 + 54, RG1 - 54, 72)):                  # lozenges: carved diamonds with a dense eye
    cy_ = RGT + 36
    c.carve(R(x + 9, cy_ - 18, x + 18, cy_ - 9) | R(x, cy_ - 9, x + 27, cy_) | R(x - 9, cy_, x + 36, cy_ + 9)
            | R(x, cy_ + 9, x + 27, cy_ + 18) | R(x + 9, cy_ + 18, x + 18, cy_ + 27))
    c.put(R(x + 9, cy_, x + 18, cy_ + 9), .95)
for y in range(RGT, RGB, 18):                                          # fringe
    c.put(R(RG0 - 27, y, RG0 - 9, y + 9) | R(RG1 + 9, y, RG1 + 27, y + 9), .55)

# ----------------------------------------------------------------------------- bookshelf (left)
BS0, BS1, BST, BSB = 54, 450, 360, 963
SHELVES = [513, 666, 819]


def books(x0, base, specs):
    """A run of books on a shelf: specs = (width_cells, height_px, tone); 1-cell gaps between them; a
    spine band carved near the top (and the foot) of the thicker ones. Returns the x after the run."""
    x = x0
    for wc, h, v in specs:
        w = wc * P
        b = R(x, base - h, x + w, base)
        c.put(b, v)
        if wc >= 2 and v > .4:
            c.carve(R(x + 9 * (wc > 2), base - h + 18, x + w - 9 * (wc > 2), base - h + 27))
        if v <= .4:
            c.put(edge(b), .7)
        x += w + P
    return x


case = R(BS0, BST, BS1, BSB)
c.cut(case | R(BS0 - 9, BST - 18, BS1 + 9, BST))
c.put(R(BS0, BST, BS0 + 18, BSB) | R(BS1 - 18, BST, BS1, BSB), .92)    # sides
c.put(R(BS0 - 9, BST - 18, BS1 + 9, BST), .92)                         # top board with an overhang
for y in SHELVES:
    c.put(R(BS0, y, BS1, y + 18), .92)
    c.put(R(BS0 + 18, y + 9, BS1 - 18, y + 18), .6)                    # the board's front edge, lit
c.put(R(BS0, BSB - 27, BS1, BSB), .92)                                 # plinth
c.carve(R(BS0 + 27, BSB - 18, BS1 - 27, BSB - 9))
c.put(R(BS0 + 9, BSB, BS0 + 36, BSB + 9) | R(BS1 - 36, BSB, BS1 - 9, BSB + 9), .95)   # feet
IN0, IN1 = BS0 + 27, BS1 - 27
# shelf 1: books + a small round clock
x = books(IN0, SHELVES[0], [(3, 108, .95), (2, 126, .55), (3, 117, .3), (2, 99, .95), (4, 90, .55)])
ckx, cky = x + 45, SHELVES[0] - 45
c.put(circ(ckx, cky, 36), .9)
c.put(circ(ckx, cky, 27), .2)
c.put(R(ckx - 4.5, cky - 22.5, ckx + 4.5, cky + 4.5) | R(ckx - 4.5, cky - 4.5, ckx + 18, cky + 4.5), .95)
c.put(R(ckx - 27, SHELVES[0] - 9, ckx + 27, SHELVES[0]), .9)
# shelf 2: a vase with a sprig, a stack of flat books, two upright books
vx = IN0 + 27
vase = rrect(vx - 22.5, SHELVES[1] - 81, vx + 22.5, SHELVES[1], 13) | R(vx - 13.5, SHELVES[1] - 99, vx + 13.5, SHELVES[1] - 72)
c.put(vase, .3)
c.put(vase & right_of(vx + 9), .55)
c.put(edge(vase), .75)
for ang, ln in ((-25, 54), (8, 63), (35, 50)):
    leaf(c, vx, SHELVES[1] - 99, ang, ln, 22, dark=.95, lit=.6, curl=.12, midrib=False, air=0)
for k, (x0_, w, v) in enumerate(((IN0 + 81, 189, .55), (IN0 + 90, 171, .95), (IN0 + 72, 207, .3))):
    b = R(x0_, SHELVES[1] - 27 * (k + 1), x0_ + w, SHELVES[1] - 27 * k - 9)
    c.put(b, v)
    if v <= .4:
        c.put(edge(b), .7)
    else:
        c.carve(R(x0_ + 18, SHELVES[1] - 27 * k - 18 - 9 * 0, x0_ + 27, SHELVES[1] - 27 * k - 9 - 9 * 0) & b & False)
books(IN1 - 45, SHELVES[1], [(2, 117, .95)])
# shelf 3: a globe on its stand + books
gx, gy, gr = IN0 + 54, SHELVES[2] - 72, 45
globe = circ(gx, gy, gr)
c.put(globe, .3)
_, _, gsh = ck.lump_shade(gx, gy, gr, globe, lit_t=2, shade_t=0.25)
c.put(gsh, .55)
c.put(edge(globe), .75)
c.put(line([(gx - 18, gy - 36), (gx + 9, gy - 18), (gx - 9, gy + 9), (gx + 18, gy + 27)]) & globe, .95)   # a coast
c.put(R(gx - 4.5, gy + gr, gx + 4.5, SHELVES[2] - 9) | R(gx - 27, SHELVES[2] - 9, gx + 27, SHELVES[2]), .9)
books(IN0 + 117, SHELVES[2], [(3, 126, .55), (3, 135, .95), (2, 117, .3), (3, 126, .55), (2, 108, .95)])
# shelf 4: two baskets (one woven: rows carved; one with a handle)
for bx0, v in ((IN0, .3), (IN0 + 189, .55)):
    bk = R(bx0, BSB - 135, bx0 + 162, BSB - 27)
    c.put(bk, v)
    c.put(edge(bk), .75)
    if v < .4:
        c.carve(bk & rows_every(BSB - 117, 18) & ~edge(bk))
    else:
        c.put(R(bx0 + 63, BSB - 117, bx0 + 99, BSB - 99), .95)
        c.carve(R(bx0 + 9, BSB - 81, bx0 + 153, BSB - 72))

# a cactus in a small pot on the top board: a ribbed column with two arms, lit left half, a flower
TP = 369
cact = rrect(TP - 22.5, BST - 207, TP + 22.5, BST - 72, 22) | rrect(TP - 63, BST - 162, TP - 36, BST - 108, 13)     | R(TP - 45, BST - 126, TP - 18, BST - 108) | rrect(TP + 36, BST - 189, TP + 63, BST - 126, 13) | R(TP + 18, BST - 144, TP + 45, BST - 126)
c.cut(cact)
c.put(cact, .95)
c.put(cact & ~right_of(TP - 4.5), .55)                                 # the lit side (hard step)
c.carve(R(TP + 4.5, BST - 189, TP + 13.5, BST - 81))                   # a rib
c.put(R(TP - 9, BST - 225, TP + 18, BST - 207), .7)                    # flower
c.put(R(TP, BST - 234, TP + 9, BST - 225), .95)
pot(c, TP, BST - 18, 99, 63, rim_h=27)
# ----------------------------------------------------------------------------- snake plant (floor pot, left of the sofa)
SPX = 540
for dx, ang, ln, wd in ((-27, -10, 171, 32), (0, 2, 225, 36), (27, 13, 162, 32), (-13, -26, 117, 28), (18, 28, 108, 28)):
    m = leaf(c, SPX + dx, 864, ang, ln, wd, dark=.95, lit=.65, curl=.02, midrib=False, air=1)
    c.carve(m & rows_every(711 + dx % 18, 45) & ~edge(m))              # the snake plant's cross bands
pot(c, SPX, 963, 108, 99, rim_h=27)

# ----------------------------------------------------------------------------- sofa
SX0, SX1 = 612, 1314


def cushion(m, v, edge_v=.72):
    c.put(m, v)
    c.put(edge(m), edge_v)


sofa_all = (R(SX0 + 63, 666, SX1 - 63, 945) | rrect(SX0, 720, SX0 + 99, 945, 36) | rrect(SX1 - 99, 720, SX1, 945, 36))
c.cut(sofa_all)
for k in range(3):                                                     # back cushions
    x0_ = SX0 + 90 + k * 180
    cushion(rrect(x0_, 675, x0_ + 171, 819, 22), .2)
c.put(R(SX0 + 72, 864, SX1 - 72, 945), .5)                             # base
c.carve(R(SX0 + 99, 900, SX1 - 99, 909))                               # its piping
for k in range(3):                                                     # seat cushions
    x0_ = SX0 + 90 + k * 180
    cm = rrect(x0_, 810, x0_ + 171, 873, 16)
    c.carve(grow(cm) & ~below(873))
    cushion(cm, .3)
for ax0 in (SX0, SX1 - 99):                                            # arms: hard shade band, outline
    am = rrect(ax0, 720, ax0 + 99, 945, 36)
    c.carve(grow(am))
    c.put(am, .36)
    c.put(am & right_of(ax0 + 63), .62)
    c.put(edge(am), .8)
    c.carve(R(ax0 + 18, 765, ax0 + 81, 774) & am)                      # the arm's roll seam
for lx_ in (SX0 + 27, SX0 + 72, SX1 - 99, SX1 - 54):                  # tapered legs
    c.put(poly([(lx_, 945), (lx_ + 27, 945), (lx_ + 21, 975), (lx_ + 6, 975)]) | R(lx_, 945, lx_ + 27, 954), .95)
# throw pillows: a dense one (left), a striped one (right), cut out of the cushions
p1 = rrect(SX0 + 108, 702, SX0 + 234, 819, 22)
p2 = rrect(SX1 - 234, 711, SX1 - 117, 819, 20)
c.cut(p1 | p2)
c.put(p1, .95)
c.put(p1 & ~shift(p1, 2, 2), .7)                                       # its lit upper left
c.carve(R(SX0 + 162, 756, SX0 + 180, 765))                             # a button
c.put(p2, .5)
c.carve(p2 & rows_every(729, 18) & ~edge(p2))
c.put(edge(p2), .75)

# ----------------------------------------------------------------------------- big plant (right): bird of paradise
PCX = 1773
# a lighter layer of leaves behind the dense ones (the patio ref's depth inside one plant)
for ang, stem, ln, wd, cv in ((-40, 300, 210, 100, -0.1), (22, 360, 200, 96, 0.08), (58, 210, 200, 90, 0.12), (-75, 160, 170, 80, -0.1)):
    leaf(c, PCX, 800, ang, ln, wd, dark=.32, lit=.2, curl=cv, stem=stem, stem_v=.4, air=0, midrib=False)
for ang, stem, ln, wd, cv in ((-50, 150, 230, 92, -0.12), (50, 140, 220, 92, 0.12), (-30, 250, 250, 96, -0.08),
                              (28, 260, 250, 96, 0.08), (-10, 330, 260, 92, -0.04), (10, 200, 240, 96, 0.05),
                              (-68, 70, 190, 84, -0.14), (70, 60, 180, 84, 0.14)):
    leaf(c, PCX, 800, ang, ln, wd, dark=.95, lit=.5, curl=cv, stem=stem, stem_v=.9, air=1, midrib=False)
pot(c, PCX, 963, 207, 171, rim_h=36)

if __name__ == '__main__':
    c.save('home_day', 'r3_390_patio')
    crops('home_day', [
        ('big plant + pot', (1440, 180, 1920, 990), 'r3_390_patio', (1360, 140, 1840, 950)),
        ('window: sun, cloud, far city', (600, 90, 1330, 620), 'r3_390_patio', (340, 50, 1070, 580)),
        ('sofa + snake plant (Clawd stands centre)', (470, 620, 1330, 990), 'r3_390_patio', (60, 560, 920, 930)),
    ])
    stand_in('home_day', [(850, 765, 1075, 933), (878, 933, 906, 975), (934, 933, 962, 975), (990, 933, 1018, 975), (1046, 933, 1060, 975)],
             r'C:\Users\风花叶\AppData\Local\Temp\claude\E--GitHub-Clawd\5d038197-3164-4eae-84f6-24ffc9a67e21\scratchpad\it3\home_stage.png')
