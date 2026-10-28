"""Scene 7 — sports_day (light): the backdrop for the "sports" GIFs.

Far -> near: sky (sun upper left, two clouds) · far trees · the bleachers (faint tiers with tiny spectators,
aisles carved) · a chain-link fence · the field (mowing stripes, <= .1: the stage) · the kerb · the running
track as the floor band (lane lines carved, start line, chequered finish line).
Left: a basketball hoop (backboard with its target square, rim, net, padded pole), a ball at its foot, a bench
at the frame edge with a striped towel and a water bottle. Right: the scoreboard on a post (SCORE / HOME 3 :
GUEST 2, carved), training cones. Pennant strings tied between the frame, the backboard and the scoreboard
sag across the top, above the GIF square.
Light from the upper left (the sun): rounded things shade on the right.
"""
import math

import numpy as np

from parts import (Canvas, R, circ, outline, side, line, bezq, c_, sun, cloud, tree_far, lump, text_mask,
                   CLOUD_SMALL, P, ROWS, COLS, XS, YS, ck, full, render, crops, poly_mask, shift_mask, rows, cols)

cv = Canvas()
put, air, carve = cv.put, cv.air, cv.carve
rng = np.random.default_rng(7)

FB = 109                                                     # floor band rows 109-119; kerb row 108

# ============================================================================ sky
sun(cv, 666, 126, 54, gap=27, length=27)
cloud(cv, 1062, 171, 330, CLOUD_SMALL)
cloud(cv, 1683, 117, 250, CLOUD_SMALL)

# ============================================================================ far trees (behind the stands)
for cx, top, r in ((72, 279, 45), (189, 306, 36), (1755, 270, 48), (1863, 300, 40)):
    tree_far(cv, cx, top, r, 495)

# ============================================================================ bleachers (far, faint)
B0, B1 = 30, 182                                             # cols
BT = 36                                                      # railing row; tiers from row 37 to 54
put(R(B0, BT, B1, BT + 1), 0.2)                              # top rail
for c in range(B0, B1, 8):
    put(R(c, BT - 2, c + 1, BT), 0.2)                        # rail posts
tiers = list(range(39, 55, 3))                               # bench rows: 39, 42, ..., 54
aisles = [c for c in range(B0 + 24, B1 - 8, 38)]
for br in tiers:
    put(R(B0, br, B1, br + 1), 0.2)                          # bench edge; risers stay paper
for a in aisles:                                             # aisles: paper, a short step on each tier
    carve(R(a, BT + 1, a + 2, 55))
    for br in tiers:
        put(R(a, br, a + 1, br + 1), 0.14)
put(R(B0, BT + 1, B0 + 1, 55) | R(B1 - 1, BT + 1, B1, 55), 0.24)   # stand ends
# spectators: a body (2 x 2, light or dark shirt) on each bench, a head above; some cheering, arm up
for br in tiers:
    c = B0 + int(rng.integers(2, 4))
    while c < B1 - 3:
        if any(a - 2 <= c <= a + 2 for a in aisles):
            c += 3
            continue
        if rng.random() < 0.75:
            put(R(c, br - 2, c + 2, br), 0.34 if rng.random() < 0.5 else 0.16)
            put(R(c, br - 3, c + 1, br - 2), 0.36)
            if rng.random() < 0.2:
                put(R(c + 2, br - 4, c + 3, br - 2), 0.36)      # a raised arm
        c += int(rng.integers(3, 6))

# ============================================================================ fence + field (the stage: <= .1)
put(R(0, 55, COLS, 56), 0.1)                                 # top rail
put(R(0, 56, COLS, 61) & full((rows + cols) % 2 == 0), 0.1)  # chain-link mesh
for c in range(4, COLS, 14):
    put(R(c, 55, c + 1, 61), 0.1)                            # posts
# mowing stripes, wider toward the viewer
edges = [62, 64, 67, 70, 74, 78, 83, 89, 96, 103, 108]
for k in range(len(edges) - 1):
    if k % 2 == 0:
        put(R(0, edges[k], COLS, edges[k + 1]), 0.09)

# ============================================================================ kerb + track (floor band)
put(R(0, 108, COLS, 109), 0.55)                              # kerb (feet line)
put(R(0, FB, COLS, ROWS), 0.34)
for r in (111, 115):
    carve(R(0, r, COLS, r + 1))                              # lane lines
carve(R(14, FB, 15, ROWS))                                   # start line
for r in range(FB, ROWS):                                    # chequered finish line, 2 x 2 blocks
    for c in range(188, 192):
        if ((r - FB) // 2 + (c - 188) // 2) % 2 == 0:
            put(R(c, r, c + 1, r + 1), 0.92)
        else:
            carve(R(c, r, c + 1, r + 1))
carve(R(187, FB, 188, ROWS)); carve(R(192, FB, 193, ROWS))

# ============================================================================ basketball hoop (left)
HB0, HB1, HBT, HBB = 28, 59, 29, 48                          # backboard cols/rows
board = R(HB0, HBT, HB1, HBB)
HC = (HB0 + HB1) // 2                                        # centre col (43)
net = np.zeros((ROWS, COLS), bool)
for i, r in enumerate(range(HBB + 1, HBB + 8)):
    k = i // 3
    net[r, HC - 5 + k:HC + 6 - k] = True
rim = R(HC - 6, HBB, HC + 7, HBB + 1)
pole = R(HC - 1, HBB + 9, HC + 1, 108)
pad = R(HC - 2, 84, HC + 2, 100)
base = R(HC - 3, 104, HC + 3, 108)
hoop = board | net | rim | pole | pad | base
air(hoop)
put(board, 0.1)
put(outline(board), 0.9)
put(outline(R(HB0 + 1, HBT + 1, HB1 - 1, HBB)) & full(cols >= HB1 - 3), 0.3)   # board edge thickness (shade)
put(outline(R(HC - 5, HBB - 9, HC + 6, HBB + 1)), 0.9)       # target square
put(pole, 0.85)
put(pole & full(cols == HC), 0.5)                            # lit half of the pole
put(pad, 0.5)
put(pad & full(cols >= HC + 1), 0.85)
put(outline(pad) & side(pad, 't'), 0.85)
put(base, 0.85)
put(net, 0.12)
put(net & full((rows + cols) % 2 == 0), 0.66)                # mesh
put(outline(net) & ~side(net, 't'), 0.66)
put(rim, 0.95)

# ============================================================================ pennant strings
def string(p0, p1, sag, n_flags, tones):
    """A string sagging between two points, triangular pennants hanging from it, alternating tones; each
    pennant cut out of what is behind it."""
    (x0, y0), (x1, y1) = p0, p1
    pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)) for t in np.linspace(0, 1, 60)]
    sm = line(pts)
    air(sm)
    put(sm, 0.55)
    for k in range(n_flags):
        t = (k + 0.5) / n_flags
        fx = x0 + (x1 - x0) * t
        fy = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
        f = poly_mask([(fx - 36, fy + 2), (fx + 36, fy + 2), (fx, fy + 80)])
        air(f)
        v = tones[k % len(tones)]
        put(f, v)
        if v < 0.5:
            put(outline(f), 0.85)                              # light flags get a dense edge
        else:
            put(f & ~shift_mask(f, 1, 1), 0.45)                # lit edge on dense flags
            if k % 3 == 0:
                carve(f & full((YS > fy + 27) & (YS < fy + 36)) & ~outline(f))   # a carved stripe


string((-9, 72), (HB0 * P, HBT * P), 40, 2, (0.62, 0.9))
string((HB1 * P, HBT * P), (147 * P, 22 * P), 140, 7, (0.9, 0.3, 0.62))
string((199 * P, 22 * P), (1930, 90), 24, 1, (0.3,))

# ============================================================================ scoreboard on a post (right)
S0, S1, ST, SB = 147, 199, 22, 49
sb = R(S0, ST, S1, SB)
cap = R(S0 - 1, ST - 1, S1 + 1, ST)
spost = R(172, SB, 174, 108)
sbase = R(170, 105, 176, 108)
air(sb | cap | spost | sbase)
put(sb, 0.9)
put(cap, 0.62)
carve(outline(R(S0 + 1, ST + 1, S1 - 1, SB - 1)))             # inner frame line, carved
put(spost, 0.85)
put(spost & full(cols == 172), 0.5)
put(sbase, 0.85)
# lettering, carved out of the board
tm, tw = text_mask(0, 0, 'SCORE')
m, _ = text_mask((S0 + S1) // 2 - tw // 2, ST + 3, 'SCORE')
carve(m)
carve(R(S0 + 3, ST + 9, S1 - 3, ST + 10))                    # rule under the title
_, w1 = text_mask(0, 0, 'HOME')
_, w2 = text_mask(0, 0, 'GUEST')
L0, L1 = S0 + 2, (S0 + S1) // 2
M0, M1 = (S0 + S1) // 2 + 1, S1 - 2
carve(text_mask((L0 + L1) // 2 - w1 // 2, ST + 12, 'HOME')[0])
carve(text_mask((M0 + M1) // 2 - w2 // 2, ST + 12, 'GUEST')[0])
carve(R((S0 + S1) // 2, ST + 11, (S0 + S1) // 2 + 1, SB - 2))  # divider


def seg7_mask(c, r, ch, w=4, h=7):
    SEG = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg', '5': 'acdfg', '6': 'acdefg',
           '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
    segs = {'a': (1, 0, w - 2, 1), 'b': (w - 1, 1, 1, h // 2 - 1), 'c': (w - 1, h // 2 + 1, 1, h - h // 2 - 2),
            'd': (1, h - 1, w - 2, 1), 'e': (0, h // 2 + 1, 1, h - h // 2 - 2), 'f': (0, 1, 1, h // 2 - 1),
            'g': (1, h // 2, w - 2, 1)}
    m = np.zeros((ROWS, COLS), bool)
    for k in SEG[ch]:
        sx, sy, sw, sh = segs[k]
        m[r + sy:r + sy + sh, c + sx:c + sx + sw] = True
    return m


carve(seg7_mask((L0 + L1) // 2 - 2, ST + 18, '3'))
carve(seg7_mask((M0 + M1) // 2 - 2, ST + 18, '2'))
# little lamps along the top of the board
for c in range(S0 + 2, S1 - 1, 4):
    put(R(c, ST - 3, c + 1, ST - 2), 0.62)
    put(R(c, ST - 2, c + 1, ST - 1), 0.85)

# ============================================================================ bench with towel and bottle (left edge)
BX0, BX1 = 2, 37
back1 = R(BX0 + 1, 88, BX1 - 1, 90)
back2 = R(BX0 + 1, 92, BX1 - 1, 94)
seat = R(BX0, 97, BX1, 99)
legs = R(BX0 + 3, 88, BX0 + 5, 108) | R(BX1 - 5, 88, BX1 - 3, 108)
feet = R(BX0 + 2, 107, BX0 + 6, 108) | R(BX1 - 6, 107, BX1 - 2, 108)
rail = R(BX0 + 5, 102, BX1 - 5, 103)
air(back1 | back2 | seat | legs | feet | rail)
put(back1 | back2, 0.62)
put(back1 & side(back1, 'b'), 0.85); put(back2 & side(back2, 'b'), 0.85)
put(seat, 0.85)
put(R(BX0, 98, BX1, 99), 0.55)                             # seat edge in light
put(legs | feet | rail, 0.9)
# a striped towel folded over the backrest near the left end, fringe at the bottom
towel = R(BX0 + 7, 87, BX0 + 14, 97)
fringe = R(BX0 + 7, 97, BX0 + 14, 98) & full(cols % 2 == 0)
air(towel | fringe)
put(towel, 0.16)
put(towel & full(((rows - 87) // 2) % 3 == 1), 0.88)
put(towel & full(cols >= BX0 + 12), 0.42)
put(towel & full(cols >= BX0 + 12) & full(((rows - 87) // 2) % 3 == 1), 0.95)
put(R(BX0 + 7, 87, BX0 + 14, 88), 0.88)                     # the fold over the rail
put(fringe, 0.6)
# water bottle standing on the seat
bot = R(26, 88, 31, 97)
bcap = R(27, 86, 30, 88)
nozzle = R(28, 85, 29, 86)
air(bot | bcap | nozzle)
put(bot, 0.2)
put(bot & full(cols >= 29), 0.55)
put(outline(bot), 0.72)
put(R(26, 90, 31, 93), 0.88)                                 # label band
carve(R(27, 91, 28, 92))                                     # glint
put(bcap | nozzle, 0.9)

# ============================================================================ basketball, cones
BLX, BLY, BLR = 549, 927, 45
ball = lump(cv, BLX, BLY, BLR, 0.62, glint=False)
put(R(c_(BLX) - 3, c_(BLY) - 3, c_(BLX) - 1, c_(BLY) - 1) & ball, 0.3)          # lit patch, upper left
carve(R(c_(BLX), c_(BLY - BLR) + 1, c_(BLX) + 1, c_(BLY + BLR)) & ball & ~outline(ball))   # seams
carve(R(c_(BLX - BLR) + 1, c_(BLY), c_(BLX + BLR), c_(BLY) + 1) & ball & ~outline(ball))


def cone(cx, base=972, w=63, h=72):
    m = poly_mask([(cx - w / 2, base), (cx - 6, base - h), (cx + 6, base - h), (cx + w / 2, base)])
    foot = R(c_(cx - w / 2) - 1, c_(base) - 1, c_(cx + w / 2) + 2, c_(base))
    air(m | foot)
    put(m, 0.88)
    put(m & full(XS < cx - 4), 0.5)
    carve(m & full((YS > base - h * 0.62) & (YS < base - h * 0.62 + 9)))   # reflective band
    put(foot, 0.88)


for x in (1287, 1395, 1503):
    cone(x)

# ============================================================================ training goal (right edge)
G0, G1, GT = 180, 212, 87
gframe = R(G0, GT, G0 + 2, 108) | R(G1 - 2, GT, G1, 108) | R(G0, GT, G1, GT + 2)
gnet = R(G0 + 2, GT + 2, G1 - 2, 108)
air(gframe | gnet)
put(gnet & full((rows + cols) % 2 == 0), 0.45)               # the net
put(R(G0 + 2, GT + 2, G1 - 2, GT + 4) & full((rows + cols) % 2 == 0), 0.7)   # its roof, in shade
put(gframe, 0.92)
put(gframe & (full(cols == G0) | full(cols == G1 - 2) | full(rows == GT)), 0.5)   # lit faces (upper left)
put(R(G0 - 1, 107, G0 + 3, 108) | R(G1 - 3, 107, G1 + 1, 108), 0.92)  # weights

cv.emit()

if __name__ == '__main__':
    render(cv.s, 'sports_day')
    crops('sports_day', [
        ('pennants over far bleachers (tiny spectators)', (520, 230, 1320, 520), 'r3_80_building_site', (1060, 260, 1860, 550)),
        ('scoreboard on a post', (1300, 160, 1820, 500), 'v1_415_bedroom_disco', (0, 280, 520, 620)),
        ('hoop: backboard, rim, net, padded pole', (230, 240, 600, 990), 'r3_390_patio', (780, 520, 1150, 990)),
        ('bench, towel, bottle, ball', (0, 760, 620, 990), 'r3_390_patio', (480, 760, 1100, 990)),
        ('track (lanes carved), goal, cones', (1240, 760, 1920, 1080), 'r3_500_hill_clouds', (0, 760, 680, 1080)),
    ])
