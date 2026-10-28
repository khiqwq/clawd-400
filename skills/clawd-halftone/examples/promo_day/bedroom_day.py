"""Scene 8 — bedroom_day (light): the backdrop for the "emotions" GIFs. A calm bedroom in the morning.

Centre top: the window (a morning sun rising behind far roofs, two birds) with curtains tied back on both
sides; below it plain wall down to the floor = Clawd's stage (the GIF square x 680-1240, y 471-1031).
Left: the nightstand (drawer, lamp, a twin-bell alarm clock at 6:00), the bed (headboard with a carved panel,
two pillows, the turned-down sheet, a patchwork quilt: carved grid, alternate patches, hearts and crosses,
a fringed hem), a wall shelf over it with books, a teddy bear and a bunny.
Right: a heart poster taped to the wall, an oval mirror over a dresser (carved drawers, a photo and a jar on
top), a big-leaf plant in a floor pot at the frame edge.
Floor band: wood boards (carved joints) with a rug (carved border, lozenges, fringe) and a pair of slippers.
Light: the window (one source) — things left of it are lit on their right, things right of it on their left.
"""
import math

import numpy as np

from parts import (Canvas, R, circ, outline, side, line, bezq, c_, sun, lump, text_mask, draw_leaves, cpot, inset,
                   FONT, P, ROWS, COLS, XS, YS, ck, full, render, crops, poly_mask, ellipse_mask, shift_mask,
                   ring, rows, cols)

cv = Canvas()
put, air, carve = cv.put, cv.air, cv.carve
rng = np.random.default_rng(11)
WOOD = 0.45                                                   # furniture fields (carved the v1_12 way)

# ============================================================================ floor band: boards + rug
put(R(0, 108, COLS, 109), 0.42)                               # skirting
put(R(0, 109, COLS, ROWS), 0.2)
for r in (112, 116):
    carve(R(0, r, COLS, r + 1))                               # board seams, wider toward the viewer
for k, (r0, r1) in enumerate(((109, 112), (113, 116), (117, 120))):
    off = (k * 7) % 23
    for c in range(off, COLS, 23 + 4 * k):
        carve(R(c, r0, c + 1, r1))                            # staggered butt joints
RG0, RG1, RGT, RGB = 78, 182, 110, 119
rug = R(RG0, RGT, RG1, RGB)
fr_ = (R(RG0 - 3, RGT, RG0, RGB) | R(RG1, RGT, RG1 + 3, RGB)) & full((rows - RGT) % 2 == 0)
air(rug | fr_)
put(rug, 0.5)
carve(outline(R(RG0 + 1, RGT + 1, RG1 - 1, RGB - 1)))         # border line
for cx_ in (RG0 + 8, RG1 - 9):                                # a lozenge near each end
    for dr, half in ((2, 0), (3, 1), (4, 2), (5, 1), (6, 0)):
        carve(R(cx_ - half, RGT + dr, cx_ + half + 1, RGT + dr + 1))
    put(R(cx_, RGT + 4, cx_ + 1, RGT + 5), 0.9)
put(fr_, 0.5)

# ============================================================================ window with curtains (centre top)
W0, W1, WT, WB = 86, 128, 12, 46                              # frame cols 86..127, rows 12..45
glass = R(W0 + 1, WT + 1, W1 - 1, WB - 1)
# morning: the sun rising behind far roofs, two birds
SX, SY = (W0 + W1) * P / 2 - 54, 333
sun(cv, SX, SY, 45, gap=24, length=27, clip=glass)
roofs = np.zeros((ROWS, COLS), bool)
for x0, x1, top, kind in ((783, 855, 387, 'gable'), (855, 927, 396, 'flat'), (999, 1071, 378, 'gable'),
                          (1071, 1143, 393, 'flat')):
    if kind == 'gable':
        roofs |= poly_mask([(x0, 414), (x0, top + 18), ((x0 + x1) / 2, top - 9), (x1, top + 18), (x1, 414)])
    else:
        roofs |= poly_mask([(x0, 414), (x0, top), (x1, top), (x1, 414)])
roofs &= glass
carve(ck.dilate(roofs) & ~roofs & glass & full(YS < 414))     # air between the roofs and the sun
put(roofs, 0.16)
put(ck.top_edge_mask(roofs), 0.3)
put(R(W0 + 1, 46 - 2, W1 - 1, 46 - 1) & glass, 0.2)          # the far street line
carve(R(90, 44, 91, 45) | R(113, 43, 114, 44) | R(122, 44, 123, 45))   # lit windows in the far houses
for bx, by in ((1053, 207), (1107, 180)):
    c, r = c_(bx), c_(by)
    for dc, dr in ((-2, 1), (-1, 0), (0, 1), (1, 0), (2, 1)):
        put(R(c + dc, r + dr, c + dc + 1, r + dr + 1), 0.62)
frame = outline(R(W0, WT, W1, WB))
mull = R(106, WT, 107, WB)
put(frame | mull, 0.62)
put(R(W0 - 2, WB, W1 + 2, WB + 2), 0.62)                       # sill
put(R(W0 - 2, WB + 1, W1 + 2, WB + 2), 0.85)
# curtains: hang from the rod, tied back at row 32, flaring to the sill; folds carved
rod = R(W0 - 9, 9, W1 + 9, 10)


def curtain(c_out, c_in_top, tie_r=32, bottom=49, left=True):
    """A curtain panel: from the rod (cols between c_out and c_in_top) gathered to a tie-back at tie_r,
    then flaring out to the bottom. Folds as carved columns that follow the gathering."""
    m = np.zeros((ROWS, COLS), bool)
    w_top = abs(c_in_top - c_out)
    for r in range(10, bottom):
        if r <= tie_r:
            t = (r - 10) / (tie_r - 10)
            w = round(w_top * (1 - 0.55 * t ** 1.4))
        else:
            t = (r - tie_r) / (bottom - tie_r)
            w = round(w_top * (0.45 + 0.3 * t))
        if left:
            m[r, c_out:c_out + w] = True
        else:
            m[r, c_out - w + 1:c_out + 1] = True
    return m


cl = curtain(W0 - 8, W0 + 4, left=True)
cr = curtain(W1 + 7, W1 - 5, left=False)
air(cl | cr | rod)
for m, left in ((cl, True), (cr, False)):
    put(m, 0.3)
    # folds: carved columns at fixed fractions of each row's width (they bunch at the tie)
    for r in range(10, 49):
        cs = np.nonzero(m[r])[0]
        if len(cs) < 3:
            continue
        for f in (0.33, 0.66):
            carve(R(cs[0] + int(round(f * (len(cs) - 1))), r, cs[0] + int(round(f * (len(cs) - 1))) + 1, r + 1))
    # the side away from the window a step darker (shade), hem dense
    shade = R(0, 0, W0 - 5, ROWS) if left else R(W1 + 5, 0, COLS, ROWS)
    put(m & shade, 0.5)
    put(side(m, 'b'), 0.85)
    tie = R(0, 31, COLS, 33) & m
    put(tie, 0.9)
put(rod, 0.85)
put(R(W0 - 10, 8, W0 - 8, 11) | R(W1 + 8, 8, W1 + 10, 11), 0.9)   # finials

# ============================================================================ left: nightstand, lamp, alarm clock
N0, N1, NT = 2, 21, 84
ns_top = R(N0 - 1, NT, N1 + 1, NT + 2)
ns_body = R(N0, NT + 2, N1, 101)
ns_legs = R(N0 + 1, 101, N0 + 3, 108) | R(N1 - 3, 101, N1 - 1, 108)
air(ns_top | ns_body | ns_legs)
put(ns_body, WOOD)
inset(cv, N0 + 1, NT + 3, N1 - 1, 93, light='r')              # drawer
put(R((N0 + N1) // 2 - 1, 89, (N0 + N1) // 2 + 1, 90), 0.95)   # knob
carve(R(N0, 94, N1, 95))
inset(cv, N0 + 1, 95, N1 - 1, 100, light='r')                 # lower shelf front
put(ns_top, 0.85)
put(ns_legs, 0.85)
# lamp: a round base (lit right), stem, a drum shade with a dense rim
LX = 72
lbase = circ(LX, 735, 22) | R(c_(LX) - 2, 82, c_(LX) + 3, 84)
stem = R(c_(LX), 73, c_(LX) + 1, 79)
shade = poly_mask([(LX - 36, 594), (LX + 36, 594), (LX + 54, 657), (LX - 54, 657)])
air(lbase | stem | shade)
put(lbase, 0.85)
put(lbase & full(XS > LX + 4), 0.42)
put(stem, 0.85)
put(shade, 0.14)
put(shade & full(XS < LX - 20), 0.32)                         # away from the window
put(side(shade, 'b') | side(shade, 't'), 0.85)
put(outline(shade) & ~side(shade, 'b') & ~side(shade, 't'), 0.62)
# twin-bell alarm clock at 6:00
CX_, CY_ = 153, 726
face = circ(CX_, CY_, 28)
bells = circ(CX_ - 22, 693, 13) & full(YS < 696) | circ(CX_ + 22, 693, 13) & full(YS < 696)
hammer = R(c_(CX_), 75, c_(CX_) + 1, 77)
cfeet = R(c_(CX_) - 2, 83, c_(CX_) - 1, 84) | R(c_(CX_) + 2, 83, c_(CX_) + 3, 84)
air(face | bells | hammer | cfeet)
put(face, 0.1)
put(outline(face), 0.9)
put(outline(face) & ~shift_mask(face, -1, 1), 0.5)            # lit rim toward the window
fc, fr = c_(CX_), c_(CY_)
put(R(fc, fr - 2, fc + 1, fr + 1), 0.9)                        # minute hand (12)
put(R(fc, fr, fc + 1, fr + 2), 0.9)                            # hour hand (6)
put(bells, 0.9)
put(hammer | cfeet, 0.9)

# ============================================================================ the bed
HB0, HB1, HBT = 23, 30, 62                                    # headboard
FB0, FB1, FBT = 70, 75, 78                                    # footboard
QT, QB = 83, 102                                              # quilt front: rows 83..101
Q0, Q1 = 30, 70
head = R(HB0, HBT, HB1, 108)
head[HBT, HB0] = head[HBT, HB1 - 1] = False
foot = R(FB0, FBT, FB1, 108)
foot[FBT, FB0] = foot[FBT, FB1 - 1] = False
rail = R(Q0, QB, FB0, QB + 2)
blegs = R(Q0 + 1, QB + 2, Q0 + 3, 108) | R(FB0 - 3, QB + 2, FB0 - 1, 108)
air(head | foot | rail | blegs)
for m, li in ((head, 'r'), (foot, 'l')):
    put(m, WOOD)
    put(m & side(m, 't'), 0.85)
cs_h = np.nonzero(head.any(axis=0))[0]
inset(cv, HB0 + 1, HBT + 3, HB1 - 1, 98, light='r')
inset(cv, FB0 + 1, FBT + 3, FB1 - 1, 98, light='l')
put(rail, 0.62)
put(blegs, 0.85)
for cxp, top in (((HB0 + HB1) * P / 2, HBT * P), ((FB0 + FB1) * P / 2, FBT * P)):
    kn = circ(cxp, top - 16, 14)
    air(kn)
    put(kn, 0.85)
    put(kn & ~shift_mask(kn, -1, 1), 0.42)
# quilt: carved grid of 6-cell patches, alternate tones, a heart or a cross in each
quilt = R(Q0, QT, FB0, QB)
air(quilt)
put(quilt, 0.3)
heart = FONT['♥']
for pi, c0 in enumerate(range(Q0, FB0, 6)):
    for pj, r0 in enumerate(range(QT + 1, QB, 6)):
        cell = R(c0 + 1, r0, min(c0 + 6, FB0), min(r0 + 5, QB))
        if (pi + pj) % 2 == 0:
            put(cell, 0.66)
            carve(R(c0 + 3, r0 + 1, c0 + 4, r0 + 4) | R(c0 + 2, r0 + 2, c0 + 5, r0 + 3))   # carved cross
        else:
            for dr, rowstr in enumerate(heart):
                for dc, k in enumerate(rowstr):
                    if k == 'X' and c0 + 1 + dc < FB0 and r0 + dr < QB:
                        put(R(c0 + 1 + dc, r0 + dr, c0 + 2 + dc, r0 + dr + 1), 0.9)
    carve(R(c0, QT + 1, c0 + 1, QB - 1))                      # grid columns
for r0 in range(QT + 1, QB, 6):
    carve(R(Q0, r0 + 5, FB0, r0 + 6))                         # grid rows
put(R(Q0, QT, FB0, QT + 1), 0.85)                             # the quilt's top edge
put(R(Q0, QB - 1, FB0, QB) & full(cols % 2 == 0), 0.85)       # fringed hem
carve(R(Q0, QB - 1, FB0, QB) & full(cols % 2 == 1))
# the turned-down sheet at the head end and two pillows
sheet = R(Q0, QT - 1, Q0 + 13, QT + 3)
air(sheet)
put(sheet, 0.08)
put(outline(sheet), 0.72)
p_back = R(HB1 + 1, 72, HB1 + 12, 82)
p_back[72, HB1 + 1] = p_back[72, HB1 + 11] = p_back[81, HB1 + 1] = p_back[81, HB1 + 11] = False
p_front = R(HB1 + 4, 76, HB1 + 17, 83)
p_front[76, HB1 + 4] = p_front[76, HB1 + 16] = p_front[82, HB1 + 4] = p_front[82, HB1 + 16] = False
air(p_back)
put(p_back, 0.14)
put(outline(p_back), 0.72)
air(p_front)
put(p_front, 0.1)
put(outline(p_front), 0.8)
put(p_front & full((rows + cols) % 3 == 0) & ~outline(p_front), 0.45)   # dotted pillowcase

# ============================================================================ wall shelf over the bed: books + plush toys
SH0, SH1, SHR = 33, 70, 52
put(R(SH0, SHR, SH1, SHR + 2), 0.8)
for bc in (SH0 + 2, SH1 - 3):
    put(R(bc, SHR + 2, bc + 1, SHR + 5) | R(bc + 1, SHR + 2, bc + 2, SHR + 4), 0.62)
x = SH0 + 1
for wc, h, v in ((2, 10, 0.88), (3, 9, 0.4), (2, 11, 0.66)):
    b = R(x, SHR - h, x + wc, SHR)
    air(b)
    put(b, v)
    if wc == 3:
        carve(R(x + 1, SHR - h + 2, x + 2, SHR - h + 3))
    x += wc + 1
# leaning book
lb = poly_mask([(x * P, SHR * P), (x * P + 27, SHR * P), (x * P + 63, SHR * P - 72), (x * P + 36, SHR * P - 80)])
air(lb); put(lb, 0.5)
# teddy bear: ears, head, muzzle, body, paws (lit from the window: right)
TX = 53 * P
bear_head = circ(TX, 390, 30)
bear_ears = circ(TX - 26, 363, 12) | circ(TX + 26, 363, 12)
bear_body = circ(TX, 444, 34) & full(YS < SHR * P)
bear = bear_head | bear_ears | bear_body
air(bear)
put(bear, 0.55)
put(bear & full(XS > TX + 10), 0.3)                           # lit side
put(side(bear, 'l') | side(bear, 'b'), 0.88)
carve(ring(bear_head) & bear_body)                             # a line under the chin
put(circ(TX, 402, 13), 0.12)                                   # muzzle
put(R(c_(TX), c_(400), c_(TX) + 1, c_(400) + 1), 0.95)         # nose
put(R(c_(TX) - 2, c_(378), c_(TX) - 1, c_(378) + 1) | R(c_(TX) + 2, c_(378), c_(TX) + 3, c_(378) + 1), 0.95)  # eyes
put(circ(TX - 30, 438, 11) | circ(TX + 30, 438, 11), 0.62)      # paws
# bunny: long ears, head, body
BNX = 64 * P
bun_ears = R(c_(BNX) - 3, 32, c_(BNX) - 1, 41) | R(c_(BNX) + 1, 31, c_(BNX) + 3, 41)
bun_head = circ(BNX, 396, 26)
bun_body = circ(BNX, 444, 31) & full(YS < SHR * P)
bun = bun_ears | bun_head | bun_body
air(bun)
put(bun, 0.16)
put(outline(bun), 0.72)
put(R(c_(BNX) - 2, 34, c_(BNX) - 1, 40) | R(c_(BNX) + 1, 33, c_(BNX) + 2, 40), 0.45)   # inner ears
carve(ring(bun_head) & bun_body)
put(R(c_(BNX) - 2, c_(393), c_(BNX) - 1, c_(393) + 1) | R(c_(BNX) + 1, c_(393), c_(BNX) + 2, c_(393) + 1), 0.95)
put(R(c_(BNX), c_(405), c_(BNX) + 1, c_(405) + 1), 0.62)          # nose

# ============================================================================ right: heart poster (taped)
PO0, PO1, POT, POB = 185, 206, 12, 40
poster = R(PO0, POT, PO1, POB)
air(poster)
put(poster, 0.08)
put(outline(poster), 0.72)
big_heart = np.zeros((ROWS, COLS), bool)
hx, hy = (PO0 + PO1) * P / 2, 210
big_heart |= circ(hx - 25, hy - 6, 29) | circ(hx + 25, hy - 6, 29)
big_heart |= poly_mask([(hx - 52, hy + 4), (hx + 52, hy + 4), (hx, hy + 72)])
big_heart &= R(PO0 + 2, POT + 2, PO1 - 2, POB - 6)
put(big_heart, 0.88)
put(big_heart & ~shift_mask(big_heart, -1, 1), 0.42)          # lit edge toward the window
carve(R(c_(hx - 34), c_(hy - 22), c_(hx - 34) + 1, c_(hy - 22) + 2))   # glint
tm, tw = text_mask(0, 0, 'HELLO')
carve(R(PO0 + 1, POB - 7, PO1 - 1, POB - 1) & ~outline(poster))
put(text_mask((PO0 + PO1) // 2 - tw // 2, POB - 6, 'HELLO')[0], 0.72)
for cc, rr in ((PO0 - 1, POT - 1), (PO1 - 1, POT - 1)):       # tape on the top corners
    put(R(cc, rr, cc + 2, rr + 2), 0.3)

# ============================================================================ right: dresser + mirror + plant
D0, D1, DT = 142, 180, 84
d_top = R(D0 - 1, DT, D1 + 1, DT + 2)
d_body = R(D0, DT + 2, D1, 106)
d_legs = R(D0 + 1, 106, D0 + 3, 108) | R(D1 - 3, 106, D1 - 1, 108)
air(d_top | d_body | d_legs)
put(d_body, WOOD)
mid = (D0 + D1) // 2
carve(R(mid, DT + 2, mid + 1, 94))                            # two small drawers on top
for a, b in ((D0, mid), (mid + 1, D1)):
    inset(cv, a + 1, DT + 3, b - 1, 94, light='l')
    put(R((a + b) // 2 - 1, 89, (a + b) // 2 + 1, 90), 0.95)
carve(R(D0, 94, D1, 95))
inset(cv, D0 + 1, 95, D1 - 1, 105, light='l')                  # a wide drawer
put(R(mid - 3, 99, mid + 4, 100), 0.95)
put(d_top, 0.85)
put(d_legs, 0.85)
# on top: a framed photo, a round jar
ph = R(146, 76, 153, 84)
air(ph)
put(ph, 0.85)
put(R(147, 77, 152, 83), 0.14)
put(R(148, 80, 151, 83), 0.62)                                 # two figures in the photo
carve(R(149, 80, 150, 83))
jar = lump(cv, 1530, 741, 18, 0.3)
put(R(c_(1530) - 1, c_(741) - 3, c_(1530) + 2, c_(741) - 2), 0.85)   # lid knob
# oval mirror on the wall above the dresser
MX, MY = mid * P + 4.5, 594
mo = ellipse_mask(MX, MY, 99, 126)
mi = ellipse_mask(MX, MY, 81, 108)
air(mo)
put(mo, 0.85)
put(mo & ~mi & ~shift_mask(mo, 1, 1), 0.45)                   # lit side of the frame (window: left)
put(mi, 0.1)
for k, (x0, y0, L_) in enumerate(((MX - 54, MY + 9, 72), (MX - 30, MY + 30, 54))):
    carve(line([(x0, y0), (x0 + L_ * 0.6, y0 - L_)]) & mi)     # shine
put(R(mid, c_(MY - 126) - 3, mid + 1, c_(MY - 126)), 0.62)     # hanging cord
put(R(mid - 1, c_(MY - 126) - 4, mid + 2, c_(MY - 126) - 3), 0.85)   # nail
# big-leaf plant at the frame edge (lit from the window: left)
PX = 1800
draw_leaves(cv, [(PX - 84, 690, 200, 126, 72), (PX + 70, 640, -40, 126, 72), (PX - 40, 600, 240, 120, 66),
                 (PX + 30, 560, -75, 120, 66), (PX - 96, 790, 170, 108, 62), (PX + 86, 770, 10, 108, 62)],
            light=(-0.6, -0.8), split=True, lit_v=0.36)
stems = line([(PX, 860), (PX - 12, 640)]) | line([(PX, 860), (PX + 40, 600)]) | line([(PX, 860), (PX - 60, 760)])
put(stems & ~full(np.nan_to_num(cv.C.v, nan=0) > 0.3), 0.8)
cpot(cv, PX, 972, 171, 117, light='l', body=0.2, rim=0.3)

# ============================================================================ slippers on the rug (right of the square)


def slipper(c0, r_base, w=12):
    """A slipper side-on: a low sole, a rounded toe cap at the front (right), the open heel low; light body,
    dense outline, a fluffy band (mid tone) along the opening."""
    m = R(c0, r_base - 2, c0 + w, r_base + 1)
    m |= R(c0 + w - 6, r_base - 3, c0 + w - 1, r_base - 2)
    m[r_base - 2, c0] = False
    air(m)
    put(m, 0.12)
    put(outline(m), 0.85)
    put(R(c0 + 2, r_base - 2, c0 + w - 6, r_base - 1), 0.55)     # the fluffy collar
    put(R(c0, r_base, c0 + w, r_base + 1), 0.92)                 # sole
    return m


slipper(140, 115)
slipper(155, 117)

cv.emit()

if __name__ == '__main__':
    render(cv.s, 'bedroom_day')
    crops('bedroom_day', [
        ('window with tied curtains, sunrise', (680, 60, 1250, 460), 'v1_300_fireplace', (1100, 0, 1670, 400)),
        ('bed: quilt patchwork, pillows, headboard', (180, 480, 700, 990), 'v1_300_fireplace', (360, 450, 880, 960)),
        ('shelf: books, teddy, bunny', (280, 260, 640, 520), 'v1_180_study', (0, 300, 360, 560)),
        ('nightstand, lamp, alarm clock', (0, 560, 220, 990), 'r3_390_patio', (1040, 540, 1260, 970)),
        ('mirror, dresser, plant', (1270, 400, 1920, 990), 'r3_390_patio', (1270, 140, 1920, 730)),
        ('rug + slippers in the floor band', (1100, 960, 1700, 1080), 'r3_390_patio', (1100, 960, 1700, 1080)),
    ])
