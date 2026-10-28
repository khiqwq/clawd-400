"""carriage_night (dark) — inside a night train carriage, seen straight on from the aisle.

Far wall: two big rounded windows (outside a moonlit lake: the moon with a ring halo high in the left
window, its broken reflection on calm water, far hills with conifers; in the right window village
lights, a lighthouse and a sailboat), tied-back curtains under pelmets, a luggage rack with a duffel bag,
a hat, a suitcase and a hatbox, a pendant lamp over the table under the left window, a round wall
clock (five to midnight) on the pier between the windows. Near: the left bench (Clawd sits on it:
body x 110-335, seat top y 840), the empty right bench, the aisle floor with a runner.
Light: the lamp (bulb at the key level, a tiny glow, a soft pool on the table) and the moon (a faint
crisp, slanted cold patch on the tablecloth).
Walls stay empty (0): every object is a filled silhouette with its structure carved out of it; the
wainscot is only its rails and stiles at a low level, so the wall below the windows stays quiet.
Tones: outside .1-.22 · curtains .3 · frames .45 · benches .3/.6 · table .6 · luggage .45-.6 ·
lamp, moon, light patch .85-1.
"""
import numpy as np

from canvas import (XS, YS, Canvas, R, rrect, circ, ell, poly, line, edge, grow, shrink, shift, right_of, below,
                    cols_every, rows_every, checker, empty, crops, stand_in, ck, P)

c = Canvas('dark')
rng = np.random.default_rng(3)
FAR, LOW, BODY, MID, DENSE, KEY, FULL = .1, .19, .3, .45, .6, .85, 1.0

# ----------------------------------------------------------------------------- geometry (px, multiples of 9)
WIN = [(144, 810), (1110, 1776)]           # window outer frames (x)
WT, WB = 261, 648                          # outer frame top / bottom
GI = 27                                    # frame width: glass starts 27 px inside
SILL = 648
DADO = 684
FLOOR = 981
TX0, TX1, TT = 441, 783, 711               # table
LX = 648                                   # lamp (over the table's right half)
LB = (54, 396)                             # left bench (Clawd: body x 110-335)
RB = (1278, 1872)                          # right bench (empty)
SEAT = 840


def glass_of(wl, wr):
    return rrect(wl + GI, WT + GI, wr - GI, WB - GI, 27)


GLASS = glass_of(*WIN[0]) | glass_of(*WIN[1])
GL, GR = glass_of(*WIN[0]), glass_of(*WIN[1])
GT, GB = WT + GI, WB - GI                  # 288, 621

# ----------------------------------------------------------------------------- outside: the moonlit lake
SHORE = 531
# far hills: one long low range, a quiet field with a crisp ridge row
far = poly([(0, SHORE)] + [(x, 486 - 22 * np.sin(x / 140 + 0.6) - 12 * np.sin(x / 53 + 2)
                                - 30 * np.exp(-((x - 1330) / 110) ** 2)) for x in range(0, 1929, 9)] + [(1920, SHORE)]) & GLASS
c.put(far, .08)
c.put(ck.top_edge_mask(far), .22)
# a nearer wooded hill at the left of each window, cut out of the range by one cell of sky
for pts in ([(171, SHORE), (171, 486), (225, 474), (297, 478), (360, 495), (423, 513), (468, SHORE)],
            [(1611, SHORE), (1656, 509), (1710, 495), (1749, 491), (1749, SHORE)]):
    m = poly(pts) & GLASS
    c.carve(grow(m) & ~m & ~below(SHORE))
    c.put(m, .16)
    c.put(ck.top_edge_mask(m), .3)
for tx, base in ((207, 484), (252, 478), (297, 482), (1674, 506), (1719, 499)):     # conifers on the ridge
    t = poly([(tx - 20, base + 4), (tx + 20, base + 4), (tx, base - 54)]) & GLASS
    c.carve(grow(t) & ~t & ~below(base))
    c.put(t, .3)
c.put(R(0, SHORE, 1920, SHORE + 9) & GLASS, .3)                        # the far shore: one crisp row

# right window: village lights on the shore, a lighthouse on the point, a sailboat
for vx in (1197, 1224, 1269, 1314):
    c.put(R(vx, SHORE - 9, vx + 9, SHORE), .7)
LHX = 1611
tower = poly([(LHX - 6, 441), (LHX + 15, 441), (LHX + 33, SHORE - 18), (LHX - 24, SHORE - 18)])
c.carve(grow(tower | R(LHX - 27, 396, LHX + 36, 441)))
c.put(tower, .36)
c.put(tower & right_of(LHX + 9), .45)
c.carve(R(LHX - 27, 468, LHX + 36, 477) | R(LHX - 27, 495, LHX + 36, 504))   # painted bands (carved)
c.put(R(LHX - 27, 432, LHX + 36, 441), .45)                            # gallery
c.put(R(LHX - 9, 414, LHX + 18, 432), FULL)                            # lamp room (lit)
c.put(R(LHX - 18, 405, LHX + 27, 414) | R(LHX, 396, LHX + 9, 405), .45) # roof + finial
for k, (dx, w, v) in enumerate(((36, 3, .45), (72, 2, .3), (99, 2, .2))):   # beam dashes
    c.put(R(LHX + dx, 414 + 9 * (k > 0), LHX + dx + w * 9, 423 + 9 * (k > 0)) & GLASS, v)
    c.put(R(LHX - dx - w * 9 + 9, 414 + 9 * (k > 0), LHX - dx + 9, 423 + 9 * (k > 0)) & GLASS, v)
sail = poly([(1413, 567), (1413, 477), (1476, 567)]) | poly([(1395, 567), (1395, 504), (1350, 567)])
hull = poly([(1332, 576), (1494, 576), (1476, 594), (1350, 594)])
c.carve(grow(sail | hull | R(1395, 468, 1413, 576)))
c.put(sail & GLASS, .3)
c.put(sail & right_of(1440) & GLASS, .42)
c.put(R(1404, 468, 1413, 576) & GLASS, .45)                           # mast
c.put(hull & GLASS, .45)
c.put(R(1359, 603, 1467, 612) & GLASS, .14)                            # its reflection

# the moon, high in the left window: bright disc, a hard shade step, two maria, a ring halo
MX, MY, MR = 468, 378, 37
halo = grow(circ(MX, MY, 66)) & ~circ(MX, MY, 66)
c.carve(circ(MX, MY, 66))
c.put(halo & GLASS, .3)
c.put(grow(circ(MX, MY, 93)) & ~circ(MX, MY, 93) & GLASS & (c.v < .05) & checker(), .14)
moon = circ(MX, MY, MR)
c.put(moon, FULL)
_, _, mshade = ck.lump_shade(MX, MY, MR, moon, lit_t=2, shade_t=0.4)
c.put(mshade, .62)
c.put(R(MX - 18, MY - 18, MX, MY - 9) | R(MX + 9, MY + 9, MX + 18, MY + 18), .62)

# stars: crisp crosses and single cells
for sx, sy, v, arm in ((252, 333, .5, 1), (702, 315, .3, 0), (639, 432, .22, 0), (324, 414, .22, 0),
                       (747, 396, .45, 1), (1179, 342, .45, 1), (1323, 387, .22, 0), (1467, 315, .3, 0),
                       (1503, 405, .22, 0), (1701, 333, .5, 1), (1404, 450, .2, 0)):
    m = R(sx, sy, sx + 9, sy + 9)
    c.put(m & GLASS, v + (.25 if arm else 0))
    if arm:
        c.put((shift(m, 1) | shift(m, -1) | shift(m, 0, 1) | shift(m, 0, -1)) & GLASS, v * .5)

# glass glints: two short diagonal strokes in the upper right corner of each pane
for wl, wr in WIN:
    gx, gy = wr - 99, WT + 45
    c.put(line([(gx, gy + 36), (gx + 36, gy)]) & GLASS, .22)
    c.put(line([(gx + 27, gy + 45), (gx + 54, gy + 18)]) & GLASS, .16)

# water: calm and dark; the moon's broken reflection column, the lights' short streaks, few ripples
water = GLASS & below(SHORE + 9)
for k, (w, v, dx) in enumerate(((8, .85, 0), (6, .7, 1), (7, .55, -1), (4, .45, 0), (5, .35, 1), (3, .25, 0))):
    y = SHORE + 18 + 9 * (2 * k if k < 3 else k + 3)
    x0 = (MX // P - w // 2 + dx) * P
    c.put(R(x0, y, x0 + w * P, y + 9) & water, v)
for vx in (1197, 1269, 1314):
    c.put(R(vx, SHORE + 18, vx + 9, SHORE + 36) & water, .4)
    c.put(R(vx, SHORE + 45, vx + 9, SHORE + 54) & water, .22)
c.put(R(LHX - 9, SHORE + 18, LHX + 18, SHORE + 27) & water, .5)
c.put(R(LHX, SHORE + 36, LHX + 9, SHORE + 45) & water, .3)
for x, y, w in ((261, 576, 3), (612, 567, 4), (684, 594, 2), (333, 603, 2), (1161, 585, 3), (1503, 567, 3),
                (1647, 603, 2), (1278, 612, 2)):
    c.put(R(x, y, x + w * P, y + 9) & water, .14)

# ----------------------------------------------------------------------------- ceiling + cornice
c.put(R(0, 0, 1920, 18), .19)
for x in range(207, 1920, 432):                                        # ceiling panel joints
    c.carve(R(x, 0, x + 9, 18))
c.put(R(0, 27, 1920, 36), .36)

# ----------------------------------------------------------------------------- luggage rack + luggage
RT = 153
RACK = [(27, 504), (729, 1899)]
for x0, x1 in RACK:
    c.put(R(x0, RT, x1, RT + 9), DENSE)                                 # front tube
    c.put(R(x0, RT + 18, x1, RT + 27), .36)                             # rack bed rail
    for bx in list(range(x0 + 27, x1 - 18, 270)) + [x1 - 36]:          # brackets down to wall plates
        c.put(R(bx, RT + 9, bx + 9, RT + 18), DENSE)
        c.put(R(bx, RT + 27, bx + 9, 207), MID)
        c.put(R(bx - 9, 207, bx + 18, 216), MID)

# duffel bag (left rack): a rounded roll, end-cap seams, a carved zip with its pull, two handle loops
bag = rrect(171, 99, 405, RT, 24)
c.put(bag, MID)
c.put(bag & right_of(351), DENSE)                                      # hard shade step
for ex in (198, 369):
    c.carve(R(ex, 99, ex + 9, RT) & bag)                               # end-cap seams
c.carve(R(225, 117, 342, 126))                                         # zip
c.put(R(288, 117, 306, 126), KEY)
for hx in (243, 315):
    c.put(edge(ell(hx + 4.5, 99, 27, 24)) & ~below(99), DENSE)          # handle loops
# a book stack beside it
for k, (x0, x1, v) in enumerate(((432, 495, MID), (441, 486, DENSE), (423, 492, BODY))):
    c.put(R(x0, RT - 18 * (k + 1), x1, RT - 18 * k - 9), v)

# suitcase (right rack): the upper wall's key piece — one bright field, structure carved
SX0, SX1, ST = 1278, 1530, 72
case = rrect(SX0, ST, SX1, RT, 18)
c.put(case, DENSE)
c.carve(R(SX0, ST + 27, SX1, ST + 36))                                 # lid seam
for sx in (SX0 + 54, SX1 - 72):                                        # straps: carved both sides
    c.carve(R(sx - 9, ST, sx, RT) | R(sx + 18, ST, sx + 27, RT))
    c.put(R(sx, ST, sx + 18, RT), KEY)
    c.put(R(sx - 9, ST + 45, sx + 27, ST + 54), FULL)                  # buckle
    c.carve(R(sx, ST + 45, sx + 18, ST + 54))
HX = (SX0 + SX1) // 2 // P * P                                         # handle on top
c.put(R(HX - 27, ST - 27, HX + 36, ST - 18) | R(HX - 27, ST - 18, HX - 18, ST) | R(HX + 27, ST - 18, HX + 36, ST), DENSE)
c.put(R(HX - 36, ST - 9, HX - 9, ST) | R(HX + 18, ST - 9, HX + 45, ST), DENSE)   # handle mounts
# hatbox with a ribbon and a bow
HB0, HB1 = 1611, 1746
hbx = rrect(HB0, 99, HB1, RT, 9)
c.put(hbx, MID)
c.put(hbx & right_of(HB1 - 45), DENSE)
c.put(R(HB0 - 9, 90, HB1 + 9, 108), DENSE)                             # lid
c.carve(R(HB0, 108, HB1, 117))
c.carve(R(1665, 90, 1674, RT) | R(1692, 90, 1701, RT))
c.put(R(1674, 90, 1692, RT), KEY)                                      # ribbon
c.put(R(1647, 72, 1674, 81) | R(1656, 81, 1674, 90) | R(1692, 72, 1719, 81) | R(1692, 81, 1710, 90) | R(1674, 81, 1692, 90), KEY)

# ----------------------------------------------------------------------------- pendant lamp over the table
c.put(R(LX - 36, 36, LX + 36, 45), MID)                                # ceiling rose
c.put(R(LX - 9, 45, LX + 9, 54), MID)
c.put(R(LX - 4.5, 54, LX + 4.5, 117), MID)                             # cord (one column)
lshade = poly([(LX - 27, 117), (LX + 27, 117), (LX + 72, 171), (LX - 72, 171)])
c.put(lshade, DENSE)
c.put(lshade & right_of(LX + 27), KEY)                                 # hard step
c.carve(R(LX - 45, 144, LX + 45, 153) & lshade)                        # a carved band
c.put(R(LX - 81, 171, LX + 81, 180), KEY)                              # rim
bulb = R(LX - 22.5, 180, LX + 22.5, 198) | R(LX - 13.5, 198, LX + 13.5, 207)
c.glow(LX, 189, 63, .14, mid=.3)
c.put(bulb, FULL)

# ----------------------------------------------------------------------------- windows: frame, sill, pelmet
for wl, wr in WIN:
    outer = rrect(wl, WT, wr, WB, 45)
    g = glass_of(wl, wr)
    c.put(outer & ~g, .55)
    c.carve(edge(shrink(outer, 2)) & ~g)                               # carved line: outer frame | gasket
    c.put(edge(grow(g)) & ~g & ~edge(shrink(outer, 2)), BODY)
    c.put(R(wl + 81, WB - 18, wl + 108, WB - 9) | R(wr - 108, WB - 18, wr - 81, WB - 9), KEY)   # latches
    c.put(R(wl - 27, SILL, wr + 27, SILL + 18), MID)                   # sill
    c.put(R(wl - 27, SILL, wr + 27, SILL + 9), DENSE)
    c.put(R(wl - 54, 234, wr + 54, 252), MID)                          # pelmet
    c.put(R(wl - 54, 252, wr + 54, 261) & checker(), MID)              # its fringe
    c.carve(R(wl - 45, 243, wr + 45, 244))


def curtain(xa, s):
    """A curtain beside a window, tied back: the wall-side edge nearly straight, the glass-side edge swept
    in to the tie-back and flaring out below it. xa = the window's outer edge, s = +1 for the left curtain,
    -1 for the right one. Body .3; the strip between the inner fold and the glass-side edge a step lighter
    (lit by the window); straight vertical fold lines carved; a bright tie-back band with a tassel."""
    def X(dx):
        return xa + s * dx
    top, waist, bot = 261, 486, 657
    inner = ck.bez((X(36), top), (X(36), 400), (X(-9), 450), (X(-27), waist), 12) +         ck.bez((X(-27), waist), (X(-18), 560), (X(27), 600), (X(27), bot), 12)
    outer = [(X(-90), bot), (X(-90), 540), (X(-72), waist), (X(-90), 430), (X(-90), top)]
    m = poly(inner + outer)
    c.obj(m, BODY)
    lit = m & ~shift(m, 3 * s, 0)
    c.put(lit, MID)
    for fx in (-63, -36):                                              # folds above the tie
        x = X(fx) // P * P
        c.carve(R(x, top + 18, x + 9, waist - 27) & shrink(m, 1))
    for fx in (-54, -18):                                              # folds below
        x = X(fx) // P * P
        c.carve(R(x, waist + 36, x + 9, bot - 9) & shrink(m, 1))
    x0, x1 = sorted((X(-72), X(-18)))
    tie = R(x0 // P * P, waist - 9, x1 // P * P + 9, waist + 9)
    c.cut(tie)
    c.put(tie, KEY)
    tx = (X(-72) if s > 0 else X(-81)) // P * P                        # tassel on the wall side
    c.cut(R(tx, waist + 9, tx + 18, waist + 45))
    c.put(R(tx, waist + 9, tx + 18, waist + 27) | R(tx + 4, waist + 27, tx + 14, waist + 45), KEY)
    return m


for wl, wr in WIN:
    curtain(wl, 1)
    curtain(wr - 9, -1)

# ----------------------------------------------------------------------------- pier: a round wall clock (five to midnight) + a hat on a hook
CKX, CKY, CKR = 963, 369, 45
ring = circ(CKX, CKY, CKR) & ~circ(CKX, CKY, CKR - 10)
c.obj(circ(CKX, CKY, CKR), 0)
c.put(ring, DENSE)
c.put(ring & ~right_of(CKX - 18) | ring & ~below(CKY - 18) & ~right_of(CKX + 18), KEY)
for dx, dy in ((0, -27), (27, 0), (0, 27), (-27, 0)):                  # hour marks
    c.put(R(CKX - 4.5 + dx, CKY - 4.5 + dy, CKX + 4.5 + dx, CKY + 4.5 + dy), BODY)
c.put(R(CKX - 4.5, CKY - 22, CKX + 4.5, CKY + 4.5), FULL)               # hour hand (to 12)
c.put(line([(CKX, CKY), (CKX - 20, CKY - 22)]), FULL)                  # minute hand (to 11: 23:55)
c.put(R(CKX - 4.5, CKY - 4.5, CKX + 4.5, CKY + 4.5), FULL)
c.put(R(CKX - 4.5, CKY - CKR - 9, CKX + 4.5, CKY - CKR), MID)          # hanger

# ----------------------------------------------------------------------------- wainscot below the windows: rails + stiles, panels left empty
c.put(R(0, DADO, 1920, DADO + 9), .36)                                 # dado rail
c.put(R(0, 927, 1920, 936), .22)                                       # bottom rail
for x in (801, 954, 1107):                                             # stiles, lined up with the pier above
    c.put(R(x, DADO + 18, x + 9, 927), .22)
    c.put(R(x - 9, DADO + 9, x + 18, DADO + 18), .22)                  # a little capital under the rail
c.put(R(0, 954, 1920, 972), BODY)
c.put(R(0, 954, 1920, 963), MID)

# ----------------------------------------------------------------------------- floor: band + runner
c.put(R(0, FLOOR, 1920, 1080), .14)
c.put(R(0, FLOOR, 1920, FLOOR + 9), BODY)
CR0, CR1 = 1017, 1071                                                  # the runner: a field, border carved
c.put(R(0, CR0, 1920, CR1), .3)
c.carve(R(0, CR0 + 9, 1920, CR0 + 18) | R(0, CR1 - 18, 1920, CR1 - 9))
c.carve(R(0, CR0 + 27, 1920, CR0 + 36) & cols_every(27, 54))           # a sparse carved motif

# ----------------------------------------------------------------------------- the table and the two lights on it
# the lamp's pool: a soft ellipse on the table and the wall right under it (below the sill only)
c.glow(LX, TT + 27, 200, .16, mid=.5, ry=63, m=below(SILL + 27))
TC = 810                                                               # tablecloth hem
cloth = R(TX0, TT, TX1, TC)
c.obj(cloth | R(TX0 - 9, TT, TX1 + 9, TT + 9), BODY)
c.put(R(TX0 - 9, TT, TX1 + 9, TT + 9), KEY)                            # the table top's lit edge
c.carve(R(TX0, TT + 9, TX1, TT + 18))
c.put(R(TX0, TC - 9, TX1, TC) & checker(), BODY)                       # scalloped hem
c.carve(R(TX0, TC - 18, TX1, TC - 9) & ~checker())
for fx in (TX0 + 72, TX1 - 81):                                        # two soft folds
    c.carve(R(fx, TT + 36, fx + 9, TC - 27))
for lx_ in (TX0 + 27, TX1 - 45):                                       # legs under the cloth
    c.obj(R(lx_, TC + 9, lx_ + 18, 963), MID)
    c.put(R(lx_ + 9, TC + 9, lx_ + 18, 963), DENSE)
    c.obj(R(lx_ - 9, 954, lx_ + 27, 972), DENSE)
# the lamp's warm pool: the middle of the cloth a step lighter, soft-edged (from the glow) + a stepped core
d = np.sqrt(((XS - LX) / 115) ** 2 + ((YS - TT - 18) / 80) ** 2)           # soft pool: smooth falloff
pool = np.broadcast_to(np.clip(1 - d, 0, 1) ** 0.7 * .6, c.v.shape)
c.v[cloth] = np.clip(c.v[cloth] + pool[cloth], 0, 1)
edge_row = R(TX0 - 9, TT, TX1 + 9, TT + 9)                             # the top edge: brightest under the lamp
c.v[edge_row] = np.broadcast_to(np.clip(1 - np.abs(XS - LX) / 260, 0, 1) * .5 + .5, c.v.shape)[edge_row]
c.carve(R(TX0, TT + 9, TX1, TT + 18))
# the moon's cold patch: crisp, the window bar's shadow carved through it
patch = poly([(450, TT + 18), (504, TT + 18), (531, TC - 18), (477, TC - 18)])
c.put(patch, FULL)
# a cup and saucer at the right end, a wisp of steam
cup = R(702, 675, 747, TT - 9) | R(693, TT - 9, 756, TT)
handle = R(747, 684, 765, 693) | R(756, 693, 765, 702) | R(747, 702, 765, 711) & False
c.carve(grow(cup | handle) & ~below(TT))
c.put(cup, KEY)
c.put(R(702, 675, 747, 684), FULL)                                    # the rim, lit
c.carve(R(711, 684, 738, 693))
c.put(R(747, 684, 765, 693) | R(756, 693, 765, 702), KEY)              # handle
for x, y in ((711, 648), (720, 630), (711, 612), (729, 594)):          # a wisp of steam
    c.put(R(x, y, x + 9, y + 18), .3)


# ----------------------------------------------------------------------------- benches (front-on, upholstered)
def bench(x0, x1, back_v, seat_v, top_v, doilies=()):
    """Backrest (a .42 field, wide channels carved, a bright top roll), armrests at both ends, a thick seat
    cushion (top at SEAT) with carved piping, a skirt panel with a vent grille, feet. Cut out of what is
    behind with a 1-cell margin."""
    back = rrect(x0 + 18, 711, x1 - 18, SEAT, 18)
    arms = rrect(x0, 765, x0 + 45, 900, 16) | rrect(x1 - 45, 765, x1, 900, 16)
    seat = rrect(x0 + 18, SEAT, x1 - 18, 900, 14)
    base = R(x0 + 45, 909, x1 - 45, 963)
    c.cut(back | arms | seat | base)
    c.put(back, back_v)
    c.put(R(x0, 711, x1, 729) & back, seat_v)                          # top roll
    c.carve(R(x0, 729, x1, 738) & back)
    c.carve(back & cols_every(x0 + 72, 72) & below(747) & ~below(SEAT - 18))   # channels
    c.carve(R(x0, SEAT - 18, x1, SEAT - 9) & back)                     # the crease
    c.put(seat, seat_v)
    c.put(R(x0, SEAT, x1, SEAT + 9) & seat, top_v)                     # the cushion's lit top
    c.carve(R(x0 + 45, SEAT + 36, x1 - 45, SEAT + 45) & seat)          # piping
    c.put(base, BODY)
    c.carve(edge(base))
    c.carve(R(x0 + 81, 918, x1 - 81, 954) & cols_every(x0 + 81, 18))   # vent slots
    c.cut(arms)
    c.put(arms, seat_v)
    c.put(arms & ~shift(arms, 0, 1), top_v)                            # lit tops
    for ax in (x0, x1 - 45):
        c.carve(R(ax + 9, 801, ax + 36, 810))
    for fx in (x0 + 36, x1 - 63):
        c.obj(R(fx, 963, fx + 27, 981), KEY)                           # feet
    for ax in doilies:                                                 # headrest covers with a scalloped hem
        d_ = R(ax, 702, ax + 108, 774)
        c.cut(d_)
        c.put(d_, KEY)
        c.put(R(ax, 765, ax + 108, 774) & ~checker(), 0)
        c.carve(R(ax + 9, 747, ax + 99, 756))


bench(*LB, DENSE, KEY, FULL)        # Clawd's bench, under the lamp: the room's key object
bench(*RB, BODY, MID, DENSE, doilies=(1386, 1674))   # the empty one, further from the lamp: a level lower

if __name__ == '__main__':
    c.save('carriage_night', 'v1_300_fireplace')
    crops('carriage_night', [
        ('window, tied curtains, moon over the lake', (20, 220, 920, 690), 'v1_300_fireplace', (0, 40, 900, 510)),
        ("Clawd's bench (key) + the lit table", (20, 660, 820, 1000), 'v1_300_fireplace', (40, 470, 840, 810)),
        ('rack: suitcase + hatbox (objects on a shelf)', (1240, 20, 1800, 240), 'v1_180_study', (1300, 100, 1860, 320)),
    ])
    stand_in('carriage_night', [(110, 672, 335, 840), (138, 840, 166, 882), (194, 840, 222, 882), (250, 840, 278, 882),
                                (306, 840, 320, 882)],
             r'C:\Users\风花叶\AppData\Local\Temp\claude\E--GitHub-Clawd\5d038197-3164-4eae-84f6-24ffc9a67e21\scratchpad\it3\carriage_stage.png')
