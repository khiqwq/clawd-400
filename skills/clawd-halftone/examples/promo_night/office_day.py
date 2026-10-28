"""Scene 2 — office_day (light): a home office by day, for the "dev" GIFs.

Left → right: the pinboard (notes with text rows, a photo, a calendar, pins) over the desk · the desk
(drawer pedestal, the monitor with code carved out of a dark editor, keyboard, mouse, mug, the desk
lamp at its right end) · under the desk the cables, a power strip and a waste bin · [the GIF square:
paper wall + the plank floor only] · a framed "</>" poster over the square · the window with a day city
and clouds (blind rolled up) · the credenza under it (binders, a cabinet door) with a printer, a pen
cup and a plant on top.
Light from the window (upper right): hard shade bands on the left, lit rims on the upper right.
Tones (ink on cream): wall 0 · floor .18 · panels .26 · lines .62 · city .12/.24 · screen .9 · binders
.3/.55/.9 · plant .62/.95.
"""
import numpy as np

from common import Svg, P, render, crops
from cellkit import gap, box, cell_mask, cells, CellPaint, outline_mask, dilate, circle_mask, polyline_mask, bez
from daykit import (plant, floor, books, rect_mask, rrect_pts, lit_rim, put_parts, C, YS, XS)

s = Svg(theme='light')
ink = s.ink
rng = np.random.default_rng(5)

# ----------------------------------------------------------------------------- floor: planks
floor(s)
for y in (1017, 1053):                                       # plank rows: carved joints
    gap(s, 0, y, 1920, 9)
for k, (y0, y1) in enumerate(((981, 1017), (1026, 1053), (1062, 1080))):
    step = (297, 333, 369)[k]
    for x in range((k * 117) % step, 1920, step):
        gap(s, x // P * P, y0, 9, y1 - y0)                   # staggered end joints

# ----------------------------------------------------------------------------- pinboard (upper left)
PB0, PBT, PB1, PBB = 81, 108, 558, 360
box(s, PB0, PBT, PB1, PBB, 0.62)                             # frame (2 cells)
box(s, PB0 + 18, PBT + 18, PB1 - 18, PBB - 18, 0.2)          # cork
# cork texture: a few carved specks
for _ in range(40):
    x = int(rng.integers(C(PB0 + 27), C(PB1 - 27))) * P; y = int(rng.integers(C(PBT + 27), C(PBB - 27))) * P
    gap(s, x, y, 9, 9)


def note(x0, y0, x1, y1, lines, pin=0.95, line_v=0.55):
    """A paper note carved out of the cork (one cell of cork-coloured air is the cork itself), text rows
    every other row, a pin at the top centre."""
    gap(s, x0, y0, x1 - x0, y1 - y0)
    for k, ln in enumerate(lines):
        y = y0 + 27 + 18 * k
        if y > y1 - 18:
            break
        box(s, x0 + 18, y, min(x1 - 18, x0 + 18 + ln * P), y + 9, line_v)
    px = (x0 + x1) // 2 // P * P
    box(s, px - 9, y0 - 9, px + 18, y0 + 9, pin)             # pin head (3 x 2)


note(117, 144, 252, 279, [9, 11, 7, 10, 6])
note(279, 171, 387, 315, [8, 6, 9, 5, 7, 4])
# a photo (polaroid): paper frame, a picture inside with a hill + sun
gap(s, 414, 135, 108, 135)
box(s, 423, 144, 513, 225, 0.55)
cells(s, cell_mask([[(423, 225), (423, 198), (459, 171), (486, 189), (513, 171), (513, 225)]]), 0.95)
gap(s, 486, 153, 18, 18)
box(s, 459, 126, 477, 144, 0.95)
# a calendar: paper sheet, a dense header row, a grid of day cells (checker of dots), one day circled
gap(s, 414, 288, 117, 54)
s.row(423, 522, 297, 0.85)
for r in range(2):
    for c in range(5):
        box(s, 432 + c * 18, 315 + r * 18, 441 + c * 18, 324 + r * 18, 0.42 if (r, c) != (1, 2) else 0.95)
# string with two tags across the bottom left
s.row(117, 387, 333, 0.62)

# ----------------------------------------------------------------------------- desk
DX0, DX1, DT = 36, 666, 702
with s.cut():
    box(s, DX0, DT, DX1, DT + 18, 0.62)                      # top (2 rows)
    s.row(DX0 + 9, DX1 - 9, DT + 18, 0.9)                    # shadow line under the top
    # drawer pedestal (left)
    box(s, DX0 + 18, DT + 27, 279, 972, 0.3)
    # right leg panel
    box(s, DX1 - 45, DT + 27, DX1 - 18, 972, 0.62)
    box(s, DX1 - 36, DT + 27, DX1 - 27, 972, 0.26)
for k, (y0, y1) in enumerate(((DT + 36, DT + 108), (DT + 117, DT + 189), (DT + 198, 963))):
    gap(s, DX0 + 18, y0 - 9, 279 - DX0 - 18, 9)              # drawer joints carved
    box(s, DX0 + 18, y0, 81, y1, 0.55)                        # shade band (light from the right)
    box(s, 126, y0 + 27, 189, y0 + 36, 0.95)                  # pull
    gap(s, 117, y0 + 18, 81, 9); gap(s, 117, y0 + 36, 81, 9)

# ----------------------------------------------------------------------------- monitor: dark editor, code carved
MX0, MY0, MX1, MY1 = 153, 423, 513, 648
with s.cut():
    mon = cell_mask([rrect_pts(MX0, MY0, MX1, MY1, 14)])
    mp = CellPaint()
    mp.put(mon, 0.9)
    mp.put(rect_mask(MX0 + 9, MY0 + 9, MX1 - 9, MY1 - 18) & ~rect_mask(MX0 + 18, MY0 + 18, MX1 - 18, MY1 - 27), -1)
    mp.put(rect_mask(MX0 + 18, MY0 + 18, MX1 - 18, MY1 - 27), 0.85)
    mp.emit(s)
    box(s, 315, MY1, 351, DT - 18, 0.62)                     # neck
    box(s, 261, DT - 18, 405, DT, 0.85)                      # foot
gap(s, MX0 + 18, MY0 + 36, MX1 - MX0 - 36, 9)                # title bar line
for k in range(3):                                           # window controls in the title bar
    gap(s, MX0 + 27 + 18 * k, MY0 + 18 + 0, 9, 9)
# code: carved bars (rows every other row), indents, gutter line numbers, a cursor block
code = [(0, [6, 3]), (2, [5, 7]), (4, [9]), (4, [4, 2, 5]), (2, [3]), (0, [2]), (0, []), (0, [7, 4]), (2, [8, 3]), (2, [5])]
y = MY0 + 54
for ind, toks in code:
    if y > MY1 - 27:
        break
    gap(s, MX0 + 27, y, 9, 9)                                # gutter mark
    x = MX0 + 63 + ind * 18
    for tl in toks:
        w = min(tl * P, MX1 - 27 - x)
        if w > 0:
            gap(s, x, y, w, 9)
        x += tl * P + P
    y += 18
gap(s, MX0 + 63, y, 9, 9)                                    # the cursor on an empty line
gap(s, MX0 + 72, y, 9, 9)
s.col(MX0 + 45, MY0 + 54, MY1 - 36, 0.5)                     # gutter rule (lighter inside the dark screen)
# power LED
box(s, MX1 - 36, MY1 - 18, MX1 - 27, MY1 - 9, 0.2)

# keyboard + mouse in front of the monitor foot
with s.cut():
    box(s, 216, DT - 27, 441, DT, 0.62)
    box(s, 477, DT - 27, 504, DT, 0.85)
for x in range(225, 432, 18):                                 # keys: carved slots
    gap(s, x, DT - 18, 9, 9)

# mug (left of the monitor): body with a hard shade band (light from the right), handle, steam
s.cyl(72, DT - 63, 117, DT, 0.3, 0.6, light_left=False, band=0.36, rx=8)
box(s, 54, DT - 54, 72, DT - 45, 0.62); box(s, 54, DT - 27, 72, DT - 18, 0.62); s.col(54, DT - 54, DT - 18, 0.62)

# desk lamp at the right end: dense base, a post, an arm, a dome shade facing down (lit rim upper right)
LP = 567
lp = CellPaint()
dome = cell_mask([[(594, 567), (594, 549), (612, 522), (639, 513), (666, 522), (684, 549), (684, 567)]])
lp.put(rect_mask(LP, 495, LP + 9, DT - 18) | rect_mask(LP, 486, 648, 495) | rect_mask(630, 495, 648, 513), 0.85)
put_parts(lp, [rect_mask(531, DT - 18, 612, DT), dome], 0.9, lit_v=0.6, k=1, light='right', air=False)
lp.put(rect_mask(603, 567, 675, 576), 0.3)                   # the bulb's rim under the dome
lp.put(rect_mask(LP - 9, 477, LP + 18, 504), 0.95)           # joint
with s.cut():
    lp.emit(s)

# ----------------------------------------------------------------------------- cables, power strip, waste bin
# the monitor's cable drops behind the desk and runs along the floor to the strip; the lamp's cable
# follows the leg panel down; a bin in the knee space
cells(s, polyline_mask([(342, DT + 27), (342, 936)] + bez((342, 936), (342, 954), (351, 963), (369, 963))[1:]), 0.62)
s.row(369, 405, 963, 0.62)
cells(s, polyline_mask([(603, DT + 27), (603, 936)] + bez((603, 936), (603, 954), (594, 963), (576, 963))[1:]), 0.62)
s.row(549, 576, 963, 0.62)
box(s, 396, 945, 558, 972, 0.9)                              # power strip, sockets carved, a switch
for x in (414, 450, 486):
    gap(s, x, 954, 18, 9)
box(s, 522, 954, 540, 963, 0.3)
bin_ = cell_mask([[(441, 846), (540, 846), (531, 936), (450, 936)]])
bp = CellPaint()
bp.put(bin_, 0.3)
bp.put(bin_ & np.broadcast_to(XS < 468, bin_.shape), 0.6)                    # shade band (left)
bp.put(rect_mask(432, 837, 549, 855), 0.85)                                   # rim
for x in (477, 504):
    bp.put(rect_mask(x, 873, x + 9, 918), -1)                                 # carved slots
bp.put(circle_mask(490, 821, 22), 0.0)
bp.put(outline_mask(circle_mask(490, 821, 22)), 0.55)                        # a crumpled paper ball
bp.put(rect_mask(486, 812, 495, 821), 0.55)
with s.cut():
    bp.emit(s)
box(s, 396, 936, 558, 945, 0.0)

# ----------------------------------------------------------------------------- poster over the square: </>
PX0, PY0, PX1, PY1 = 807, 162, 1116, 378
s.frame(PX0, PY0, PX1, PY1, 0.9)
s.frame(PX0 + 18, PY0 + 18, PX1 - 18, PY1 - 18, 0.0, fill=0.0)
# "</>" in hand-set glyphs, strokes two cells thick (SimSun's 1-cell strokes were too thin here)
GL = {'<': ['....##', '..###.', '###...', '###...', '..###.', '....##'],
      '/': ['....##', '...##.', '..##..', '.##...', '##....', '#.....'],
      '>': ['##....', '.###..', '...###', '...###', '.###..', '##....']}
gx0 = (PX0 + PX1) // 2 // P * P - 9 * 10
for k, ch in enumerate('</>'):
    for r, row_ in enumerate(GL[ch]):
        for c, on in enumerate(row_):
            if on == '#':
                box(s, gx0 + (k * 7 + c) * P, PY0 + 54 + r * 18, gx0 + (k * 7 + c + 1) * P, PY0 + 54 + r * 18 + 18, 0.9)
for (x0, x1) in ((PX0 + 54, PX0 + 126), (PX0 + 144, PX0 + 189), (PX0 + 207, PX1 - 54)):
    s.row(x0, x1, PY1 - 54, 0.45)                            # a line of "code" under it
box(s, (PX0 + PX1) // 2 // P * P, PY0 - 45, (PX0 + PX1) // 2 // P * P + 9, PY0, 0.62)   # hanging cord
box(s, (PX0 + PX1) // 2 // P * P - 9, PY0 - 54, (PX0 + PX1) // 2 // P * P + 18, PY0 - 45, 0.9)

# ----------------------------------------------------------------------------- window: day city
WX0, WY0, WX1, WY1 = 1296, 72, 1800, 468
glass = s.clip_rect(WX0 + 9, WY0 + 9, WX1 - WX0 - 18, WY1 - WY0 - 18)
cityp = CellPaint()
x = WX0 + 9
k = 0
heights = [99, 153, 72, 126, 171, 90, 135, 117]
widths = [9, 7, 10, 8, 6, 9, 8, 10]
while x < WX1 - 9:
    w = widths[k % 8] * P; h = heights[k % 8]
    m_ = rect_mask(x, WY1 - 9 - h, min(x + w, WX1 - 9), WY1 - 9)
    cityp.put(dilate(m_) & ~m_ & ~np.isnan(cityp.v), -1)
    cityp.put(m_, 0.22)
    cityp.put(m_ & ~np.roll(m_, 1, axis=0), 0.5)            # a crisp roof row
    for yy in range(WY1 - h + 18, WY1 - 27, 27):              # window grid (carved)
        for xx in range(x + 18, min(x + w, WX1 - 9) - 9, 27):
            cityp.v[C(yy), C(xx)] = -1
    if k % 3 == 1:                                            # a water tower / antenna on some roofs
        cx_ = x + w // 2 // P * P
        cityp.put(rect_mask(cx_ - 18, WY1 - 9 - h - 36, cx_ + 18, WY1 - 9 - h - 9), 0.5)
        cityp.put(rect_mask(cx_ - 18, WY1 - 9 - h - 9, cx_ - 9, WY1 - 9 - h), 0.5)
        cityp.put(rect_mask(cx_ + 9, WY1 - 9 - h - 9, cx_ + 18, WY1 - 9 - h), 0.5)
    x += w + 9 * (1 + k % 2); k += 1
cityp.emit(s)
# two small clouds (cell exact: lumpy top densest, base fading)
cl = CellPaint()
for (cx0, cy0, sc) in ((1431, 189, 1.0), (1665, 144, 0.8)):
    m = np.zeros((120, 213), bool)
    for dx, dy, r in ((-40, 10, 26), (-8, -8, 34), (30, 4, 28), (0, 16, 24)):
        m |= circle_mask(cx0 + dx * sc, cy0 + dy * sc, r * sc)
    m &= np.broadcast_to(YS <= cy0 + 30 * sc, m.shape)
    cl.put(m, 0.18)
    cl.put(m & np.broadcast_to(YS < cy0 - 4, m.shape), 0.36)
cl.emit(s)
s.frame(WX0, WY0, WX1, WY1, 0.62)
s.col((WX0 + WX1) // 2 // P * P, WY0, WY1, 0.62)
box(s, WX0 - 27, WY1, WX1 + 27, WY1 + 18, 0.45)             # sill
# roller blind rolled up at the top + pull cord
box(s, WX0 + 9, WY0 + 9, WX1 - 9, WY0 + 36, 0.42)
s.row(WX0 + 9, WX1 - 9, WY0 + 36, 0.85)
s.col(WX1 - 54, WY0 + 45, WY0 + 153, 0.55)
box(s, WX1 - 63, WY0 + 153, WX1 - 36, WY0 + 171, 0.85)

# ----------------------------------------------------------------------------- credenza with binders
CX0, CX1, CT = 1278, 1818, 702
with s.cut():
    box(s, CX0 - 9, CT, CX1 + 9, CT + 18, 0.62)               # top (2 rows)
    s.frame(CX0, CT + 18, CX1, 972, 0.62)
    box(s, CX0, 945, CX1, 972, 0.62)                          # plinth
    s.col(1539, CT + 18, 945, 0.62)                           # divider
    box(s, CX0, 828, 1539, 846, 0.62)                         # shelf in the left bay
# binders: upright, a label window and a finger hole carved, tones alternate
bx = CX0 + 18
for k, v in enumerate((0.9, 0.55, 0.3, 0.9, 0.55, 0.9)):
    box(s, bx, CT + 36, bx + 27, 828, v)
    gap(s, bx + 9, CT + 54, 9, 27)                            # label window
    gap(s, bx + 9, 828 - 36, 9, 9)                            # finger hole
    bx += 36
cells(s, cell_mask([[(bx, 828), (bx + 27, 828), (bx + 72, CT + 45), (bx + 45, CT + 36)]]), 0.55)   # a leaning binder
# lower left bay: magazine files (shorter), a box
bx = CX0 + 18
for k, v in enumerate((0.42, 0.9, 0.42)):
    cells(s, cell_mask([[(bx, 945), (bx + 36, 945), (bx + 36, 864), (bx + 18, 864), (bx, 900)]]), v)
    bx += 45
s.frame(bx + 18, 873, 1521, 945, 0.62, fill=0.26)
box(s, bx + 63, 900, bx + 99, 909, 0.9)
# right bay: a cabinet door with an inset and a knob (light from the right: shade band on the left)
s.frame(1557, CT + 36, CX1 - 18, 927, 0.62, fill=0.26)
s.frame(1584, CT + 63, CX1 - 45, 900, 0.42)
box(s, 1584, CT + 72, 1611, 891, 0.45)
box(s, 1575, 810, 1593, 828, 0.95)

# on top: printer (left), pen cup, plant (right)
with s.cut():
    pr = CellPaint()
    body = rect_mask(1305, 621, 1503, CT)
    pr.put(body, 0.3)
    pr.put(body & np.broadcast_to(XS < 1341, body.shape), 0.6)                # shade band (left)
    pr.put(rect_mask(1305, 612, 1503, 621), 0.62)
    pr.put(rect_mask(1341, 648, 1467, 657), -1)                               # output slot
    pr.put(rect_mask(1350, 657, 1458, 675), 0.0)                              # a printed sheet
    pr.put(rect_mask(1368, 666, 1440, 675), 0.42)
    pr.put(rect_mask(1476, 630, 1485, 639), 0.95)                             # LED
    pr.put(rect_mask(1350, 585, 1458, 612), 0.0)                              # paper in the feeder
    pr.put(outline_mask(rect_mask(1350, 576, 1458, 612)), 0.42)
    pr.emit(s)
    s.cyl(1548, CT - 72, 1593, CT, 0.3, 0.6, light_left=False, band=0.36)    # pen cup
for (px_, h_, v_) in ((1557, 117, 0.9), (1566, 99, 0.45), (1575, 126, 0.9)):   # pens, 1 cell each
    box(s, px_ - 9 * (px_ == 1566) + 9 * (px_ == 1575), CT - h_, px_ - 9 * (px_ == 1566) + 9 * (px_ == 1575) + 9, CT - 72, v_)
# a columnar cactus in a pot: trunk + two arms (cells), lit half / shaded half (hard step at the
# middle, light from the right), carved ribs, a flower on top
PCX, PCB = 1719, CT
cac = CellPaint()
trunk = cell_mask([rrect_pts(PCX - 27, PCB - 189, PCX + 27, PCB - 72, 22)])
armL = cell_mask([rrect_pts(PCX - 72, PCB - 153, PCX - 45, PCB - 108, 13)]) | rect_mask(PCX - 72, PCB - 117, PCX - 27, PCB - 99)
armR = cell_mask([rrect_pts(PCX + 45, PCB - 171, PCX + 72, PCB - 126, 13)]) | rect_mask(PCX + 27, PCB - 135, PCX + 72, PCB - 117)
whole = trunk | armL | armR
cac.put(whole, 0.62)
for m_ in (trunk, armL, armR):                                  # each part's left half shaded (hard step)
    ys_, xs_ = np.nonzero(m_)
    mid = (xs_.min() + xs_.max() + 1) / 2 if m_ is trunk else xs_.min() + 2
    cac.put(m_ & np.broadcast_to(np.arange(213)[None, :] < mid, m_.shape), 0.95)
cac.put(rect_mask(PCX - 9, PCB - 171, PCX, PCB - 81), -1)                          # ribs carved
cac.put(rect_mask(PCX + 9, PCB - 171, PCX + 18, PCB - 81), -1)
cac.put(rect_mask(PCX - 9, PCB - 207, PCX + 18, PCB - 189), 0.45)                  # a flower on top
cac.put(rect_mask(PCX, PCB - 216, PCX + 9, PCB - 207), 0.45)
with s.cut():
    cac.emit(s)
s.pot(PCX, PCB, 117, 81, body=0.2, rim=0.3, edge=0.62, shade=0.45, light_left=False)

if __name__ == '__main__':
    render(s, 'office_day', 'light', 'r3_390_patio')
    crops('office_day', [
        ('desk, monitor (code carved), lamp, bin, cables', (27, 400, 707, 990), 'r3_390_patio', (760, 420, 1440, 1010)),
        ('pinboard with notes', (63, 90, 576, 380), 'v1_180_study', (110, 100, 623, 390)),
        ('window: day city + clouds', (1278, 54, 1824, 500), 'r3_80_building_site', (1080, 260, 1626, 706)),
        ('credenza: binders, printer, cactus', (1260, 440, 1830, 990), 'v1_180_study', (1290, 90, 1860, 640)),
    ])
