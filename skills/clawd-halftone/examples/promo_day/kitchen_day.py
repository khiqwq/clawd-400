"""Scene 6 — kitchen_day (light): the backdrop for the "life" GIFs.

Front-on kitchen wall in daylight. Centre top: the window (sun and a far garden in the glass, gingham valance,
cross mullion) with a potted basil and a little cactus on the sill; below it plain wall = Clawd's stage
(the GIF square x 680-1240, y 471-1031 stays paper down to the floor band).
Left run: the fridge (doors, handles, a magnet note, a photo, magnets) under a small cabinet; upper cabinets
with inset doors; subway tiles; a utensil rail (ladle, turner, whisk); the counter with the kettle; lower
cabinets (drawers, doors, plinth).
Right run: a hanging pothos in a macrame hanger; open shelves (jars, books, plates, mugs, a spoon crock); tiles;
the counter with the fruit bowl and a stockpot over the oven; lower cabinets; a cutting board.
Floor band: a quiet checker of tiles under a skirting line.
Light: the window (one source) — things left of it are lit on their right, things right of it on their left.
Built on cells (CellPaint): crisp stair-stepped silhouettes, fill-then-carve detail, one-cell air rings.
"""
import math

import numpy as np

from common import (Svg, P, ROWS, COLS, XS, YS, ck, full, render, crops, poly_mask, ellipse_mask,
                    shift_mask, ring, curve_frame)

s = Svg(theme='light')
C = ck.CellPaint()
rng = np.random.default_rng(3)
cols = np.arange(COLS)[None, :]
rows = np.arange(ROWS)[:, None]


def put(m, v):
    C.put(m, v)


def air(m, n=1):
    C.put(ring(m, n), -1)


def R(c0, r0, c1, r1):
    """Cell rectangle: cols c0..c1-1, rows r0..r1-1."""
    m = np.zeros((ROWS, COLS), bool)
    m[max(0, r0):max(0, r1), max(0, c0):max(0, c1)] = True
    return m


def circ(cx, cy, r):
    return ck.circle_mask(cx, cy, r)


def outline(m):
    return ck.outline_mask(m)


def side(m, which):
    """Edge cells of a mask on one side: 'l', 'r', 't', 'b' (the cells whose neighbour that way is outside)."""
    dc, dr = {'l': (1, 0), 'r': (-1, 0), 't': (0, 1), 'b': (0, -1)}[which]
    return m & ~shift_mask(m, dc, dr)


# ============================================================================ geometry (cells)
FLOOR = 109                     # floor band rows 109-119 (y 981+); skirting row 108
CT = 76                         # counter top rows 76-77 (y 684-702)
LC0, LC1 = 35, 75               # left run cols (x 315-675)
RC0, RC1 = 139, 213             # right run cols (x 1251-1920)
UTOP, UBOT = 7, 45              # upper cabinets rows 7-44 + underside row 44

# ============================================================================ floor band
put(R(0, 108, COLS, 109), 0.42)                                  # skirting line
chk = ((rows - FLOOR) // 3 + cols // 6) % 2 == 0
put(R(0, FLOOR, COLS, ROWS) & full(chk), 0.26)
put(R(0, FLOOR, COLS, ROWS) & full(~chk), 0.1)

# ============================================================================ window (centre top)
W0, W1, WT, WB = 83, 130, 12, 48                                 # frame cols 83..129, rows 12..47
glass = R(W0 + 1, WT + 1, W1 - 1, WB - 1)
# far view in the glass: a faint hill line, a round tree and a roof in the right pane
hill = poly_mask([(747, 432), (747, 384)] + [(x, 388 - 10 * math.sin(x / 70) - 6 * math.sin(x / 31 + 1)) for x in range(747, 1180, 12)] + [(1170, 432)]) & glass
put(hill, 0.14)
put(ck.top_edge_mask(hill), 0.26)
t = circ(1125, 340, 31) & glass
put(t, 0.22)
put(t & ~shift_mask(t, -1, -1), 0.36)
put(R(125, 42, 126, 47) & glass, 0.3)
roofs = poly_mask([(990, 432), (990, 398), (1022, 374), (1054, 398), (1054, 432)]) & glass
put(roofs, 0.2)
put(R(111, 44, 113, 47), -1)                                     # a lit window in the far house
# the sun in the left pane, ray dashes, all inside the glass
SX, SY, SR = 999, 225, 40
put(circ(SX, SY, SR), 0.36)
for k in range(8):
    a = 2 * math.pi * k / 8 + math.pi / 8
    put(ck.polyline_mask([(SX + (SR + 22) * math.cos(a), SY + (SR + 22) * math.sin(a)),
                          (SX + (SR + 46) * math.cos(a), SY + (SR + 46) * math.sin(a))]) & glass, 0.28)
# frame, one mullion, sill
frame = outline(R(W0, WT, W1, WB))
mull = R(106, WT, 107, WB)
put(frame | mull, 0.62)
sill = R(W0 - 2, WB, W1 + 2, WB + 2)
put(sill, 0.62)
put(R(W0 - 2, WB + 1, W1 + 2, WB + 2), 0.85)                    # its shaded front edge
# gingham valance hanging from the frame top, scalloped hem
val = R(W0 - 1, WT, W1 + 1, WT + 5)
for c in range(W0 - 1, W1 + 1):
    k = (c - (W0 - 1)) % 6
    if k in (1, 2, 3, 4):
        val[WT + 5, c] = True
    if k in (2, 3):
        val[WT + 6, c] = True
air(val)
ging = ((rows // 2) + (cols // 2)) % 2 == 0
put(val, 0.16)
put(val & full(ging), 0.5)
put(val & full((rows // 2) % 2 == 0) & full((cols // 2) % 2 == 0), 0.85)   # where the stripes cross
put(R(W0 - 2, WT - 1, W1 + 2, WT), 0.85)                         # curtain rod
put(R(W0 - 3, WT - 1, W0 - 2, WT + 1) | R(W1 + 2, WT - 1, W1 + 3, WT + 1), 0.85)   # rod ends


# wall clock above the window (3 o'clock: only straight hands stay crisp at this size)
CKX, CKY, CKR = 960, 50, 38
ck_m = circ(CKX, CKY, CKR)
air(ck_m)
put(outline(ck_m), 0.9)
put(outline(ck_m) & ~shift_mask(ck_m, 1, 1), 0.5)               # lit rim toward the light
cc_, cr_ = int(CKX // P), int(CKY // P)
put(R(cc_, cr_ - 3, cc_ + 1, cr_ + 1), 0.9)                      # minute hand (12)
put(R(cc_, cr_, cc_ + 3, cr_ + 1), 0.9)                          # hour hand (3)
for dc, dr in ((0, 4), (-4, 0)):                                 # ticks at 6 and 9
    put(R(cc_ + dc, cr_ + dr - (1 if dr else 0), cc_ + dc + 1, cr_ + dr + (0 if dr else 1)), 0.55)


# ============================================================================ pots (cell recipe of r3_390)
def cpot(cx, base, w, h, light='l', body=0.2, rim=0.3, shade=0.5, edge=0.66):
    """r3_390 pot on cells: rim band (wider), tapering body with stepped rounded bottom corners, one-cell
    outline, a hard shade band (~30 %) on the side away from the light."""
    rim_h = max(2, round(h * 0.28 / P))
    c0, c1 = int(round((cx - w / 2) / P)), int(round((cx + w / 2) / P))
    rb, rt = base // P, base // P - h // P
    rim_m = R(c0, rt, c1, rt + rim_h)
    bod = np.zeros((ROWS, COLS), bool)
    nrows = rb - (rt + rim_h)
    for i, r in enumerate(range(rt + rim_h, rb)):
        inset = 1 + (i * 1) // max(1, nrows - 1)
        if r == rb - 1:
            inset += 1
        bod[r, c0 + inset:c1 - inset] = True
    m = rim_m | bod
    air(m)
    w_ = c1 - c0
    band = max(2, round(w_ * 0.3))
    sh = R(c1 - band, 0, c1, ROWS) if light == 'l' else R(c0, 0, c0 + band, ROWS)
    put(bod, body); put(bod & sh, shade)
    put(rim_m, rim); put(rim_m & sh, min(1, shade + 0.15))
    put(outline(bod), edge); put(outline(rim_m), edge)
    return m


def cleaf(cx, cy, ang, L, W, lit=0.42, dark=0.9, light_up=True):
    """A small leaf on cells: an ellipse along `ang` (deg, 0 = right), split lit/dark along its midline."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    X, Y = np.broadcast_to(XS, (ROWS, COLS)), np.broadcast_to(YS, (ROWS, COLS))
    u = (X - cx) * ux + (Y - cy) * uy
    v = -(X - cx) * uy + (Y - cy) * ux
    m = (u / (L / 2)) ** 2 + (v / (W / 2)) ** 2 <= 1
    upper = (v < 0) if ux >= 0 else (v > 0)
    if not light_up:
        upper = ~upper
    return m, m & upper, m & ~upper


def leaf2(cx, cy, ang, L, W, light=(-0.6, -0.8)):
    """A teardrop leaf on cells (wide near the stem, pointed at the tip), pointing along `ang` (deg,
    0 = right, 90 = down) from its centre; the half of the blade facing `light` is the lit half."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    X, Y = np.broadcast_to(XS, (ROWS, COLS)), np.broadcast_to(YS, (ROWS, COLS))
    u = ((X - cx) * ux + (Y - cy) * uy) / (L / 2)
    v = -(X - cx) * uy + (Y - cy) * ux
    halfw = W / 2 * np.sqrt(np.clip(1 - u * u, 0, 1)) * (1 - 0.3 * u)
    m = (np.abs(v) <= halfw) & (np.abs(u) <= 1)
    s = -uy * light[0] + ux * light[1]
    lit = m & (v * s > 0)
    return m, lit, m & ~lit


def draw_leaves(spec, lit_v=0.42, dark_v=0.92, light=(-0.6, -0.8)):
    """Leaves back to front, each cut out of the ones behind it with a one-cell air ring. Small leaves
    (< 6 cells across) can't carry a lit/dark split (each half would be 2 cells of noise): they are solid
    dense with a one-cell lit rim on the side facing the light."""
    allm = np.zeros((ROWS, COLS), bool)
    dc = -1 if light[0] < 0 else 1
    for cx, cy, ang, L_, W_ in spec:
        m, lt, dk = leaf2(cx, cy, ang, L_, W_, light)
        air(m)
        put(m, dark_v)
        put(m & ~shift_mask(m, -dc, 1), lit_v)
        allm |= m
    return allm


# basil on the sill: five big leaves in a dome, stems showing between them
BAX = 864
stems = (ck.polyline_mask([(BAX, 369), (BAX, 290)]) | ck.polyline_mask([(BAX, 360), (BAX - 36, 336)]) |
         ck.polyline_mask([(BAX, 360), (BAX + 36, 336)]))
air(stems)
put(stems, 0.75)
draw_leaves([(BAX - 50, 345, 195, 68, 46), (BAX + 50, 345, -15, 68, 46), (BAX - 30, 293, 235, 66, 44),
             (BAX + 30, 293, -55, 66, 44), (BAX, 254, -90, 60, 42)])
basil = cpot(BAX, WB * P, 90, 63, light='l')
# a little saguaro cactus with a flower
CAX = 1062
cac_pot = cpot(CAX, WB * P, 72, 54, light='l')
cc = int(CAX // P)
trunk = R(cc - 2, 31, cc + 2, 42)
trunk[31, cc - 2] = trunk[31, cc + 1] = False
arm_l = R(cc - 5, 36, cc - 2, 38) | R(cc - 5, 33, cc - 3, 36)
arm_r = R(cc + 2, 34, cc + 5, 36) | R(cc + 3, 31, cc + 5, 34)
cac = trunk | arm_l | arm_r
air(cac)
put(cac, 0.55)
put(cac & (R(cc + 1, 0, cc + 2, ROWS) | R(cc + 4, 0, cc + 5, ROWS) | R(cc - 3, 0, cc - 2, ROWS)), 0.92)   # shade side
put(R(cc - 1, 33, cc, 41), -1)                                   # rib, carved
fl = R(cc - 1, 29, cc + 1, 30) | R(cc - 2, 28, cc - 1, 29) | R(cc + 1, 28, cc + 2, 29)
air(fl)
put(fl, 0.45)
put(R(cc - 1, 29, cc + 1, 30), 0.92)

# ============================================================================ left: fridge + cabinet above
F0, F1 = 4, 32
fr = R(F0, 30, F1, 107)
for (c, r) in ((F0, 30), (F1 - 1, 30), (F0, 106), (F1 - 1, 106)):
    fr[r, c] = False                                             # rounded corners
air(fr)
put(fr, 0.14)
put(fr & R(F0, 0, F0 + 3, ROWS), 0.32)                           # shade band away from the window
put(outline(fr), 0.7)
put(R(F0 + 1, 51, F1 - 1, 52), -1)                               # door gap (freezer above)
put(R(F0, 51, F0 + 1, 52) | R(F1 - 1, 51, F1, 52), 0.7)
for r0, r1 in ((40, 48), (54, 68)):                              # handles on the window side
    put(R(F1 - 4, r0, F1 - 3, r1), 0.92)
    put(R(F1 - 5, r0, F1 - 4, r1), -1)
put(R(F0 + 2, 107, F0 + 5, 108) | R(F1 - 5, 107, F1 - 2, 108), 0.85)       # feet
# the magnet note: paper with a one-cell edge, three lines of 'writing', a magnet holding it
note = R(10, 59, 21, 72)
put(note, -1)
put(outline(note), 0.45)
for r, c1 in ((62, 19), (65, 17), (68, 18)):
    put(R(12, r, c1, r + 1), 0.72)
put(R(14, 57, 17, 60), 0.92)                                     # magnet
put(R(15, 57, 16, 58), 0.45)                                     # its highlight
# a photo on the freezer door + round magnets
ph = R(9, 35, 17, 44)
put(ph, 0.5)
put(outline(ph), 0.85)
put(R(10, 41, 16, 43), 0.85)                                     # a hill in the photo
put(R(14, 37, 16, 39), 0.2)                                      # its sun
for mc, mr in ((22, 37), (24, 76), (8, 80)):
    put(R(mc, mr, mc + 2, mr + 2), 0.92)
CAB = 0.45                                                       # painted cabinets: a mid field, insets carved


def inset(c0, r0, c1, r1, light):
    """A recessed door panel the v1_12 way: a carved ring, two cells wide on the bottom and on the side away
    from the light (the recess in shadow), one cell on the lit sides."""
    put(outline(R(c0, r0, c1, r1)), -1)
    put(R(c0, r1 - 2, c1, r1 - 1), -1)
    if light == 'r':
        put(R(c0 + 1, r0, c0 + 2, r1), -1)
    else:
        put(R(c1 - 2, r0, c1 - 1, r1), -1)


def doors_field(c0, r0, c1, r1, doors, pulls, light='r'):
    """A cabinet run the v1_12 way (day tones): one mid field, the gaps between doors and a one-cell inset
    ring in each door carved to paper, dense pulls. doors = [(d0, d1)], pulls = [(c, r0, r1)]."""
    m = R(c0, r0, c1, r1)
    put(m, CAB)
    for k, (d0, d1) in enumerate(doors):
        if k:
            put(R(d0 - 1, r0, d0, r1), -1)
        inset(d0 + 1, r0 + 2, d1 - 1, r1 - 2, light)
    for c, a, b in pulls:
        put(R(c, a, c + 1, b), 0.95)
    return m


# small cabinet above the fridge
doors_field(F0, UTOP, F1, 28, ((F0, 18), (18, F1)), ((16, 20, 25), (19, 20, 25)))
put(R(F0 - 1, UTOP - 1, F1 + 1, UTOP), 0.85)                     # crown
put(R(F0, 28, F1, 29), 0.85)                                     # underside in shade

# ============================================================================ left: upper cabinets
doors_field(LC0, UTOP, LC1, UBOT - 1, ((LC0, LC0 + 13), (LC0 + 14, LC0 + 27), (LC0 + 28, LC1)),
            ((LC0 + 11, UBOT - 10, UBOT - 5), (LC0 + 25, UBOT - 10, UBOT - 5), (LC0 + 29, UBOT - 10, UBOT - 5)))
put(R(LC0 - 1, UTOP - 1, LC1 + 1, UTOP), 0.85)                   # crown
put(R(LC0, UBOT - 1, LC1, UBOT), 0.85)                           # underside in shade
# ============================================================================ tiles (subway), both runs


def tiles(c0, c1, r0, r1):
    m = R(c0, r0, c1, r1)
    put(m, 0.16)
    for r in range(r0, r1):
        k = (r - r0) % 3
        if k == 2:
            put(R(c0, r, c1, r + 1), -1)                         # bed joint
        else:
            off = 0 if ((r - r0) // 3) % 2 == 0 else 3
            for c in range(c0 + off, c1, 6):
                put(R(c, r, c + 1, r + 1), -1)                   # head joints, staggered
    return m


tiles(LC0, LC1, UBOT + 1, CT)
tiles(RC0, RC1, 48, CT)

# ============================================================================ counters + lower cabinets


def lower_run(c0, c1, doors, light):
    """Counter (a dense slab, a paper row under it), the cabinets as a carved mid field, a plinth."""
    put(R(c0 - 1, CT, c1 + 1, CT + 2), 0.9)                      # counter top slab
    put(R(c0, CT + 2, c1, CT + 3), -1)
    lc = R(c0, CT + 3, c1, 106)
    put(lc, CAB)
    put(R(c0 + 1, 106, c1 - 1, 108), 0.8)                        # plinth, set back
    for d0, d1, kind in doors:
        if d0 > c0:
            put(R(d0 - 1, CT + 3, d0, 106), -1)
        put(R(d0, 84, d1, 85), -1)                               # drawer / door split
        hc = (d0 + d1) // 2
        put(R(hc - 2, 81, hc + 2, 82), 0.95)                     # drawer pull
        if kind == 'door':
            inset(d0 + 1, 86, d1 - 1, 105, light)               # recessed panel
            kc = d1 - 3 if light == 'l' else d0 + 2
            put(R(kc, 88, kc + 1, 92), 0.95)


lower_run(LC0, LC1, ((LC0 + 1, LC0 + 20, 'door'), (LC0 + 21, LC1 - 1, 'door')), light='r')

# ============================================================================ left: kettle on the counter
KX, KB = 432, CT * P                                             # centre x, sits on the counter (y 684)
body = poly_mask([(372, KB), (492, KB), (486, 630), (468, 603), (396, 603), (378, 630)])
lid = R(int(405 // P), 64, int(459 // P) + 1, 67)
lid[64, int(405 // P)] = lid[64, int(459 // P)] = False
knob = R(int(KX // P) - 1, 62, int(KX // P) + 1, 64)
handle = ck.polyline_mask(ck.bez((390, 606), (384, 520), (480, 520), (474, 606), n=40))
spout = ck.polyline_mask([(384, 650), (354, 628), (330, 603)], thick=2)
kettle = body | lid | knob | handle | spout
air(kettle)
put(body | spout, 0.9)
put(body & full(XS > 459), 0.42)                                 # lit side toward the window (hard step)
put(R(int(468 // P), 69, int(468 // P) + 1, 73) & body, -1)      # glint
put(R(int(372 // P), 75, int(492 // P) + 1, 76) & body, 0.95)    # base band
put(lid, 0.62)
put(knob, 0.92)
put(handle & ~body, 0.85)

# ============================================================================ left: utensil rail
put(R(54, 51, 74, 52), 0.75)                                     # rail
put(R(54, 50, 55, 53) | R(73, 50, 74, 53), 0.85)                # brackets
uten = np.zeros((ROWS, COLS), bool)
# ladle
lad_h = R(57, 52, 58, 66)
lad_b = circ(57 * P + 4.5, 618, 22) & full(YS > 600)
lad_b |= R(55, 66, 60, 67)
# turner (spatula) with carved slots
tur_h = R(64, 52, 65, 62)
tur_head = R(62, 62, 67, 71)
tur_head[70, 62] = tur_head[70, 66] = False
# whisk: wire loop
wh_h = R(70, 52, 71, 58)
loop = ellipse_mask(70 * P + 4.5, 594, 24, 36) & full(YS > 570)
uten = lad_h | lad_b | tur_h | tur_head | wh_h | loop
air(uten)
put(lad_h | tur_h | wh_h, 0.85)
put(lad_b, 0.9)
put(lad_b & full(XS > 57 * P + 8), 0.45)
put(tur_head, 0.62)
put(R(63, 63, 64, 69) | R(65, 63, 66, 69), -1)
put(outline(loop), 0.72)
put(R(70, 59, 71, 69), 0.72)
put(R(69, 58, 72, 59), 0.9)                                      # ferrule

# ============================================================================ right: hanging pothos
HX = 1305
hc_ = int(HX // P)
put(R(hc_, 0, hc_ + 1, 2), 0.85)                                 # hook
put(R(hc_ - 1, 2, hc_ + 2, 4), 0.85)                             # ring
ropes = (ck.polyline_mask([(HX + 4, 36), (HX - 40, 150)]) | ck.polyline_mask([(HX + 4, 36), (HX + 48, 150)]) |
         ck.polyline_mask([(HX + 4, 36), (HX + 4, 120)]))
put(ropes, 0.45)
LW = (-0.6, -0.8)                                                # light from the window (upper left of here)
# leaves above the rim (behind the pot), then the pot, then the trailing vines with their leaves
draw_leaves([(HX - 44, 126, 215, 66, 46), (HX + 52, 126, -35, 66, 46)], light=LW)
hp = cpot(HX + 4, 222, 108, 72, light='l', body=0.2, rim=0.3)
vines = [((HX - 36, 214), (HX - 62, 320), (HX - 40, 430)), ((HX + 48, 214), (HX + 84, 320), (HX + 70, 414))]
vm = np.zeros((ROWS, COLS), bool)
spec = [(HX - 72, 210, 160, 66, 46), (HX + 84, 210, 20, 66, 46)]   # leaves spilling over the rim
for vi, (p0, p1, p2) in enumerate(vines):
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, 40)]
    vm |= ck.polyline_mask(pts)
    for i, t in enumerate((0.42, 0.75, 1.0)):
        x, y = pts[min(39, int(t * 39))]
        sgn = -1 if (i + vi) % 2 == 0 else 1
        spec.append((x + sgn * 26, y + 4, 90 - sgn * 50, 63, 45))
vm &= full(YS > 222)
air(vm)
put(vm, 0.75)
draw_leaves(spec, light=LW)

# ============================================================================ right: open shelves
SH0, SH1 = 160, 211


def shelf(r):
    put(R(SH0, r, SH1, r + 2), 0.75)
    for bc in (SH0 + 3, SH1 - 4):                                # brackets
        put(R(bc, r + 2, bc + 1, r + 5), 0.62)
        put(R(bc + 1, r + 2, bc + 2, r + 4), 0.62)
        put(R(bc + 2, r + 2, bc + 3, r + 3), 0.62)


shelf(26)
shelf(44)


def jar(c0, c1, base, h, fillv=0.45, fill_h=4):
    m = R(c0, base - h, c1, base)
    lid_ = R(c0 + 1, base - h - 2, c1 - 1, base - h)
    air(m | lid_)
    put(m, 0.12)
    put(R(c0, base - fill_h, c1, base), fillv)
    put(outline(m), 0.62)
    put(lid_, 0.88)
    put(R(c0 + 1, base - h + 2, c0 + 2, base - fill_h - 1), -1)  # glass glint (lit side)


jar(162, 168, 26, 8, fill_h=5)
jar(170, 176, 26, 9, fillv=0.7, fill_h=4)
jar(178, 183, 26, 7, fill_h=3)
# books standing on the top shelf
x = 187
for wc, h, v in ((2, 11, 0.88), (3, 10, 0.4), (2, 12, 0.7), (3, 9, 0.88)):
    b = R(x, 26 - h, x + wc, 26)
    air(b)
    put(b, v)
    if wc == 3:
        put(R(x + 1, 26 - h + 2, x + 2, 26 - h + 3), -1)
    x += wc + 1
# leaning book
lean = poly_mask([(x * P, 26 * P), (x * P + 27, 26 * P), (x * P + 72, 26 * P - 90), (x * P + 45, 26 * P - 99)])
air(lean); put(lean, 0.55)
# lower shelf: plates stack, two mugs, a crock of wooden spoons
for k in range(3):
    put(R(162, 43 - 2 * k, 175, 44 - 2 * k), 0.62)
put(R(162, 39, 163, 44) | R(174, 39, 175, 44), 0.62)


def mug(c0, base):
    m = R(c0, base - 5, c0 + 5, base)
    hdl = outline(R(c0 + 5, base - 4, c0 + 8, base - 1))
    air(m | hdl)
    put(m, 0.2)
    put(m & R(c0 + 3, 0, c0 + 5, ROWS), 0.5)
    put(outline(m), 0.7)
    put(hdl & ~m, 0.7)


mug(178, 44)
mug(188, 44)
crock = R(198, 38, 205, 44)
spoons = R(199, 32, 200, 38) | R(201, 30, 202, 38) | R(203, 33, 204, 38) | R(200, 29, 203, 31)
air(crock | spoons)
put(spoons, 0.75)
put(crock, 0.3)
put(crock & R(202, 0, 205, ROWS), 0.6)
put(outline(crock), 0.7)

# ============================================================================ right: counter, fruit bowl, oven + pot
lower_run(RC0, RC1, ((RC0 + 1, RC0 + 15, 'door'), (RC0 + 16, RC0 + 30, 'door'), (RC0 + 62, RC1 + 3, 'door')), light='l')
# the oven replaces the cabinets in between
OV0, OV1 = RC0 + 31, RC0 + 61
ov = R(OV0, CT + 2, OV1, 106)
put(ov, 0.3)
put(outline(ov), 0.7)
put(R(OV0 + 1, 83, OV1 - 1, 84), -1)                             # control strip / door split
for kx in (OV0 + 3, OV0 + 7, OV1 - 9, OV1 - 5):
    put(R(kx, 79, kx + 2, 81), 0.92)                             # knobs
put(R(OV0 + 12, 79, OV1 - 12, 81), 0.85)                         # clock window
put(R(OV0 + 13, 79, OV0 + 14, 80) | R(OV0 + 15, 80, OV0 + 16, 81) | R(OV1 - 14, 79, OV1 - 13, 80), 0.3)
put(R(OV0 + 3, 85, OV1 - 3, 86), 0.92)                           # door handle bar
put(R(OV0 + 3, 86, OV1 - 3, 87), -1)
win = R(OV0 + 4, 89, OV1 - 4, 102)
put(win, 0.86)
put(R(OV0 + 5, 95, OV1 - 5, 96), -1)                             # rack, carved
put(R(OV0 + 6, 91, OV0 + 7, 93) | R(OV0 + 7, 90, OV0 + 8, 91), 0.3)   # glass reflection
# stockpot on the counter above the oven (lit from the window: left)
PC0, PC1 = OV0 + 6, OV0 + 23
pot = R(PC0, 66, PC1, CT)
pot_lid = R(PC0 - 1, 64, PC1 + 1, 66)
pot_knob = R((PC0 + PC1) // 2 - 1, 62, (PC0 + PC1) // 2 + 1, 64)
lugs = R(PC0 - 2, 67, PC0, 69) | R(PC1, 67, PC1 + 2, 69)
air(pot | pot_lid | pot_knob | lugs)
put(pot, 0.24)
put(pot & R(PC1 - 5, 0, PC1, ROWS), 0.55)
put(outline(pot), 0.72)
put(R(PC0, 70, PC1, 71) & pot, 0.72)                             # a band
put(pot_lid, 0.62)
put(pot_lid & R(PC1 - 4, 0, PC1 + 1, ROWS), 0.85)
put(pot_knob | lugs, 0.9)
# fruit bowl (lit from the window: left): fruit as plain round lumps (body, a shade rim on the lower right,
# a glint), side by side; the dense bowl in front cuts their bottoms


def fruit(cx, cy, r, body, stem=True):
    m = circ(cx, cy, r)
    air(m)
    put(m, body)
    put(side(m, 'b') | side(m, 'r'), min(0.95, body + 0.4))
    gc, gr = int((cx - r * 0.4) // P), int((cy - r * 0.4) // P)
    put(R(gc, gr, gc + 1, gr + 1), -1)
    if stem:
        sc, sr = int(cx // P), int((cy - r) // P)
        put(R(sc, sr - 1, sc + 1, sr + 1), 0.9)
    return m


banana = poly_mask(ck.bez((1334, 610), (1366, 552), (1444, 552), (1470, 604), n=20) +
                   ck.bez((1458, 608), (1436, 578), (1384, 578), (1350, 614), n=20))
air(banana)
put(banana, 0.3)
put(banana & ~shift_mask(banana, 0, -1), 0.8)                    # its underside in shade
fruit(1332, 618, 29, 0.5)                                        # apple
fruit(1395, 616, 29, 0.24, stem=False)                           # orange
put(R(int(1395 // P), int(588 // P) + 1, int(1395 // P) + 1, int(588 // P) + 2), 0.9)
fruit(1449, 624, 24, 0.5)                                        # apple
bowl = poly_mask([(1296, 639), (1458, 639), (1446, 660), (1420, 675), (1334, 675), (1308, 660)])
foot = R(int(1350 // P), 75, int(1404 // P) + 1, 76)
air(bowl | foot)
put(bowl, 0.9)
put(bowl & full(XS < 1336), 0.42)                                # lit side toward the window
put(R(int(1296 // P), 71, int(1458 // P) + 1, 72) & bowl, 0.62)  # rim
put(foot, 0.9)
# cutting board leaning on the tiles at the far right
cb = R(203, 55, 211, 76)
cb[55, 203] = cb[55, 210] = False
air(cb)
put(cb, 0.3)
put(outline(cb), 0.66)
put(R(206, 57, 208, 59), -1)                                     # hanging hole
put(R(204, 61, 205, 75), 0.45)                                   # grain line

C.emit(s)

if __name__ == '__main__':
    render(s, 'kitchen_day')
    crops('kitchen_day', [
        ('upper cabinets (carved insets), fridge', (0, 40, 700, 420), 'v1_12_kitchen', (340, 0, 1040, 380)),
        ('counter, kettle, utensils, lower cabinets', (300, 440, 700, 980), 'v1_12_kitchen', (1000, 380, 1400, 920)),
        ('fruit bowl, stockpot, oven', (1260, 540, 1820, 980), 'v1_12_kitchen', (1420, 440, 1920, 880)),
        ('window: valance, sun, basil, cactus', (720, 0, 1200, 470), 'r3_390_patio', (340, 50, 820, 520)),
        ('hanging pothos (leaves)', (1180, 0, 1440, 470), 'r3_390_patio', (0, 270, 260, 740)),
        ('floor band (checker) + skirting', (0, 950, 700, 1080), 'r3_390_patio', (0, 950, 700, 1080)),
    ])
