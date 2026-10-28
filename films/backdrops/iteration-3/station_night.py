"""station_night (dark) — a small city platform at night, side view across the platform.

Far -> near: night sky with a crescent moon and a faint city skyline (towers .1 with a crisp top row,
sparse lit windows) · the far platform's canopy above the train (fascia with a dagger valance, small
hanging lamps) · the passenger car (roof with vents; a .2 body whose structure is carved: window
surrounds, livery stripe gaps, panel seams; a row of lit windows with carved seat backs and a few
passengers; the door left of centre with lit door windows; a destination board; the car number; a
gangway to the next car; bogies hidden by the platform edge) · the platform (coping, tactile strip, a dark
surface lit only in the lamps' pools, tile joints carved in the light) · two lamp posts, the clock on a
post showing 23:59, the name board 城南站 on two posts with a bench under it.
Clawd stands on the platform at x 260-485, feet y 975, in the left lamp's pool.
Tones: sky 0 · skyline .1/.22 · canopy .3 · car body .2 · roof .42 · stripe .6 · lit windows .7 ·
platform 0 (+ pools .35) · lamps, clock digits, name board 1.0 / .85.
"""
import numpy as np

from canvas import (XS, YS, Canvas, R, rrect, circ, ell, poly, line, edge, grow, shrink, shift, right_of,
                    below, cols_every, rows_every, checker, empty, crops, stand_in, ck, P)

c = Canvas('dark')
rng = np.random.default_rng(7)
FAR, LOW, BODY, MID, DENSE, KEY, FULL = .1, .2, .3, .42, .6, .85, 1.0

# ----------------------------------------------------------------------------- geometry
RT, RB = 306, 351                         # roof top, roof bottom / body top
BB = 765                                  # body bottom (bogies hidden by the platform)
PE = 783                                  # platform edge
WT, WB = 414, 531                         # window top / bottom
CAR1 = 1737                               # this car's right end; gangway; next car from 1791
DX0, DX1 = 594, 774                       # the door (left of centre)
WINS = [27, 216, 405, 819, 1008, 1197, 1386, 1575]
WW = 144

# ----------------------------------------------------------------------------- sky: crescent moon + faint skyline
mx, my = 1683, 99
c.put(circ(mx, my, 33) & ~circ(mx + 15, my - 9, 30), KEY)              # crescent
x = 0
k = 0
SKY_BASE = 252
while x < 1920:
    w = int(rng.integers(8, 15)) * P
    h = int(rng.choice([7, 10, 13, 16, 19, 22])) * P
    top = SKY_BASE - h
    if not (mx - 60 < x + w and x < mx + 60 and top < my + 50):
        m = R(x, top, x + w, SKY_BASE)
        c.put(m, FAR)
        c.put(R(x, top, x + w, top + 9), .22)
        for yy in range(top + 27, SKY_BASE - 9, 27):
            for xx in range(x + 18, x + w - 9, 27):
                if rng.random() < 0.2:
                    c.put(R(xx, yy, xx + 9, yy + 9), .45)
        if rng.random() < 0.3:
            ax = x + w // 2 // P * P
            c.put(R(ax, top - 36, ax + 9, top), .2)
            c.put(R(ax, top - 45, ax + 9, top - 36), .6)
    x += w + int(rng.integers(1, 5)) * P
    k += 1
for sx, sy, v in ((99, 45, .4), (558, 27, .3), (927, 63, .35), (1314, 36, .3), (1872, 117, .3), (1494, 18, .25)):
    if c.v[sy // P, sx // P] == 0:
        c.put(R(sx, sy, sx + 9, sy + 9), v)

# ----------------------------------------------------------------------------- far canopy above the train
CF0, CF1 = 225, 252
c.carve(R(0, CF0 - 9, 1920, CF1 + 36))
c.put(R(0, CF0, 1920, CF1), BODY)                                      # fascia
c.carve(R(0, CF0 + 9, 1920, CF0 + 18) & cols_every(0, 18))             # a carved dash line
for xx in range(0, 1920, 27):                                          # dagger valance: pointed boards
    c.put(R(xx, CF1, xx + 18, CF1 + 9) | R(xx + 4.5, CF1 + 9, xx + 13.5, CF1 + 18), BODY)
for xx in range(117, 1920, 270):                                       # small lamps hung under the canopy
    c.put(R(xx + 4.5, CF1 + 18, xx + 13.5, CF1 + 27), .3)
    c.put(R(xx, CF1 + 27, xx + 18, CF1 + 36), .7)

# ----------------------------------------------------------------------------- the passenger car
# The car side is drawn like the kitchen ref's cabinets: one body field (.3) with its structure carved
# out of it — window surrounds, the livery stripe's channel, panel seams, the door's inset — and the lit
# windows bright inside it.
body = rrect(-60, RB - 18, CAR1, BB, 27) & below(RB)
nextcar = rrect(1791, RB - 18, 2000, BB, 27) & below(RB)
roof = rrect(-60, RT, CAR1, RB + 18, 27) & ~below(RB)
roof2 = rrect(1791, RT, 2000, RB + 18, 27) & ~below(RB)
CARS = body | nextcar
LAMPS = (171, 1323)
c.put(CARS, .34)
c.put(roof | roof2, MID)
c.put(R(0, RT, 1920, RT + 9) & (roof | roof2), DENSE)                 # the roof's lit crown
c.carve(R(0, RB, 1920, RB + 9))                                        # gutter (carved)
for vx in (153, 711, 1269):                                            # roof vents / AC housings
    c.put(rrect(vx, RT - 27, vx + 216, RT + 9, 9) & ~below(RT), BODY)
    c.carve(R(vx + 18, RT - 18, vx + 198, RT - 9) & cols_every(vx + 18, 18))
# gangway bellows between the cars
c.put(R(CAR1 + 9, RB + 18, 1782, BB - 18) & cols_every(CAR1 + 9, 18), BODY)
# the livery: a carved channel with a bright stripe in it; a thin carved line over the windows
c.carve(R(0, 369, 1920, 378) & CARS)
c.carve(R(0, 558, 1920, 594) & CARS)
c.put(R(0, 567, 1920, 585) & CARS, KEY)
# lower body: panel seams under the window piers, the skirt seam, underframe slots, the bottom edge
for sx in (198, 387, 801, 990, 1179, 1368, 1557):
    c.carve(R(sx, 603, sx + 9, 693) & CARS)
c.carve(R(0, 693, 1920, 702) & CARS)
c.put(R(0, 702, 1920, BB) & CARS, .2)
c.carve(R(0, 711, 1920, BB - 18) & cols_every(36, 72) & CARS)
c.put(R(0, BB - 9, 1920, BB) & CARS, MID)
c.carve(R(CAR1 - 18, RB + 18, CAR1 - 9, BB - 9) | R(1800, RB + 18, 1809, BB - 9))   # car-end seams


def window(x0, rider=None):
    """A lit car window: a carved surround, a bright interior (.8), and carved inside it the luggage rack
    line near the top and the row of seat backs along the bottom (a 2-row band with two headrest bumps);
    optionally a passenger's head and shoulders rising from it."""
    w = rrect(x0, WT, x0 + WW, WB, 22)
    c.carve(grow(w))
    c.put(w, .8)
    c.carve(R(x0 + 18, WT + 18, x0 + WW - 18, WT + 27))                # luggage rack
    c.carve(R(x0, WB - 18, x0 + WW, WB) & w)                           # seat backs
    for hx0 in (x0 + 18, x0 + WW - 45):
        c.carve(R(hx0, WB - 36, hx0 + 27, WB - 18))                    # headrests
    if rider:
        hx = x0 + WW // 2 // P * P - 9
        c.carve(R(hx + 9, WB - 63, hx + 18, WB - 54) | R(hx, WB - 54, hx + 27, WB - 36) | R(hx - 9, WB - 36, hx + 36, WB - 18))
    return w


for wx in WINS:
    window(wx, rider={405: 0, 1197: 0}.get(wx))
window(1854)                                                           # next car

# the door: an inset (carved channel), two leaves a level brighter with tall lit windows, joint, handles
c.carve(R(DX0 - 9, 369, DX1 + 9, BB))
leaves = R(DX0, 378, DX1, BB - 9)
c.put(leaves, MID)
mid_ = (DX0 + DX1) // 2 // P * P
c.carve(R(mid_, 378, mid_ + 9, BB))                                    # leaf joint
for lx in (DX0 + 27, mid_ + 27):
    dw = rrect(lx, WT - 9, lx + 54, 612, 14)
    c.carve(grow(dw))
    c.put(dw, .8)
    c.carve(R(lx + 18, WT + 9, lx + 36, WT + 18))                      # a hand strap seen inside
    c.carve(R(lx + 22.5, WT + 18, lx + 31.5, WT + 36))
c.put(R(mid_ - 27, 648, mid_ - 9, 684) | R(mid_ + 18, 648, mid_ + 36, 684), FULL)   # handles
c.put(R(DX0 - 18, BB - 9, DX1 + 18, BB), DENSE)                       # step plate
# destination board over the door (lit, text carved as bars)
c.carve(R(DX0 + 9, 342, DX1 - 9, 378))
dest = R(DX0 + 18, 351, DX1 - 18, 369)
c.put(dest, KEY)
c.carve(R(DX0 + 36, 351, DX0 + 54, 360) | R(DX0 + 72, 360, DX0 + 117, 369) | R(DX0 + 126, 351, DX0 + 144, 369))
# car number on the body, right of the door
c.seg7(1638, 630, '07', DENSE, w=3, h=5)

# ----------------------------------------------------------------------------- platform: coping, tactile strip, dark surface
c.put(R(0, PE, 1920, PE + 9), MID)                                     # coping edge
c.carve(R(0, PE + 9, 1920, PE + 18))
c.put(R(0, PE + 18, 1920, PE + 36), DENSE)                             # tactile strip
c.put(R(0, PE + 18, 1920, PE + 36) & checker(), KEY)
c.carve(R(0, PE + 36, 1920, PE + 45))

# pools of light from the two lamps (before the joints are carved)
SURF = below(PE + 45)
for lx in LAMPS:
    d = np.sqrt(((XS - lx - 9) / 288) ** 2 + ((YS - 972) / 92) ** 2)  # a pool of light: crisp rim,
    pool = np.broadcast_to(np.where(d <= 1, .12 + .3 * np.clip(1 - d, 0, 1) ** 1.2, 0), c.v.shape)   # brighter to the post
    c.v[SURF] = np.maximum(c.v[SURF], pool[SURF])
# tile joints: rows spaced wider toward the viewer (depth without perspective), staggered verticals
JR = [855, 900, 954, 1017]
for jy in JR:
    c.carve(R(0, jy, 1920, jy + 9))
bands = [PE + 45] + [j + 9 for j in JR]
ends = JR + [1080]
for k in range(len(bands)):
    step = (108, 126, 144, 162, 180)[k]
    for jx in range((k % 2) * step // 2 // P * P, 1920, step // P * P):
        c.carve(R(jx, bands[k], jx + 9, ends[k]))


# ----------------------------------------------------------------------------- lamp posts
def lamp_post(x, top=117, base=963):
    """A station lamp on our platform: cast base, a two-cell pole, a lantern (lit glass wider at the
    top, two carved glazing bars, cap, finial, bottom ring), a tiny glow. x = the pole's left column."""
    parts = (R(x - 18, base - 36, x + 36, base) | R(x - 9, base - 63, x + 27, base - 36) | R(x, top + 99, x + 18, base - 63)
             | R(x - 9, top + 81, x + 27, top + 99))
    lant = poly([(x - 36, top + 18), (x + 54, top + 18), (x + 36, top + 72), (x - 18, top + 72)])
    cap = R(x - 54, top, x + 72, top + 18) | R(x - 27, top - 18, x + 45, top) | R(x, top - 36, x + 18, top - 18)
    ring = R(x - 27, top + 72, x + 45, top + 81)
    c.cut(parts | lant | cap | ring)
    c.glow(x + 9, top + 45, 90, .16, mid=.3)
    c.put(parts, DENSE)
    c.put(parts & right_of(x + 9), KEY)
    c.put(lant, FULL)
    c.put(cap | ring, KEY)
    c.carve((R(x - 9, top + 27, x, top + 72) | R(x + 18, top + 27, x + 27, top + 72)) & lant)   # glazing bars


for lx in LAMPS:
    lamp_post(lx)

# ----------------------------------------------------------------------------- the clock on a post (23:59)
CK0, CK1, CKT = 1008, 1296, 513
ckx = (CK0 + CK1) // 2 // P * P
case = R(CK0, CKT, CK1, CKT + 117)
post = R(ckx - 9, CKT + 117, ckx + 18, 954) | R(ckx - 36, 945, ckx + 45, 963) | R(ckx - 27, CKT - 27, ckx + 36, CKT)
c.cut(case | post)
c.put(post, MID)
c.put(post & right_of(ckx + 9), DENSE)
c.put(case, DENSE)
c.put(R(CK0, CKT, CK1, CKT + 9), KEY)                                  # lit top edge
c.carve(R(CK0 + 9, CKT + 18, CK1 - 9, CKT + 108))                      # the dark face
c.seg7(CK0 + 27, CKT + 18, '23:59', FULL, w=5, h=9, ghost=.1)

# ----------------------------------------------------------------------------- name board 城南站 (a lightbox on two posts) + bench + bin
NB0, NB1, NBT, NBB = 1422, 1836, 549, 711
board = R(NB0, NBT, NB1, NBB)
legs = R(NB0 + 27, NBB, NB0 + 45, 963) | R(NB1 - 45, NBB, NB1 - 27, 963)
c.cut(board | legs)
c.put(legs, MID)
c.put(board, DENSE)
c.put(R(NB0, NBT, NB1, NBT + 9), KEY)                                  # lit top edge
c.carve(shrink(board, 1))                                              # dark face
c.put(edge(shrink(board, 2)), .2)                                      # an inner rule, faint
c.text(NB0 + 36, NBT + 27, '城南站', FULL, size=12, gap=2)
c.put(R(NB0 + 36, NBB - 36, NB1 - 36, NBB - 27), BODY)                 # a rule under the name

# bench under the board: slatted back + seat, cast ends
BX0, BX1 = 1485, 1773
bench_m = (R(BX0 + 18, 846, BX1 - 18, 864) | R(BX0 + 18, 873, BX1 - 18, 891) | R(BX0, 909, BX1, 927))
ends_m = R(BX0 + 18, 837, BX0 + 45, 963) | R(BX1 - 45, 837, BX1 - 18, 963) | R(BX0 + 9, 900, BX0 + 54, 909) | R(BX1 - 54, 900, BX1 - 9, 909)
c.cut(bench_m | ends_m)
c.put(bench_m, DENSE)
c.put(R(BX0, 909, BX1, 918), KEY)
c.put(ends_m, KEY)

if __name__ == '__main__':
    c.save('station_night', 'v1_12_kitchen')
    crops('station_night', [
        ('car side: a carved field, lit windows, the door', (0, 300, 840, 790), 'v1_12_kitchen', (330, 0, 1170, 490)),
        ('clock 23:59, name board, bench', (990, 480, 1860, 980), 'v1_415_bedroom_disco', (0, 260, 870, 760)),
        ("lamp post + pool of light (Clawd's spot)", (0, 60, 520, 1080), 'v1_300_fireplace', (1060, 60, 1580, 1080)),
    ])
    stand_in('station_night', [(260, 765, 485, 933), (288, 933, 316, 975), (344, 933, 372, 975), (400, 933, 428, 975), (456, 933, 470, 975)],
             r'C:\Users\风花叶\AppData\Local\Temp\claude\E--GitHub-Clawd\5d038197-3164-4eae-84f6-24ffc9a67e21\scratchpad\it3\station_stage.png')
