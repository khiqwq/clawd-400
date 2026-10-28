"""Scene 3 — stage_day (light): a small theatre stage on cream paper, for the "costumes" GIFs.

Top: the valance (pleats, swags, a fringe, tassels) across the frame, a border drape behind it, a can
spotlight hanging at the centre · sides: heavy velvet curtains drawn and tied back (pleats with a hard
shade step toward the wings, fold gaps carved) · behind: the back drape (faint .1) · the spotlight cone:
a paper (less ink) wedge with stair-stepped edges from the lamp down to the stage, its pool on the boards
· the prop chest with a crown on it (left) · the coat rack with a top hat, a bowler, a scarf and a cane
(right) · the stage floor (planks) with the apron lip and the footlights (hoods + ray dashes) below it.
Light: the spotlight at the centre, so each curtain is lit on its inner side.
Tones (ink on cream): back drape .1 · border .26 · curtains .62/.95 · valance .62/.95 · floor .3 · chest
.3/.6/.95 · rack .85 · cone + pool paper.
"""
import math

import numpy as np

from common import Svg, P, render, crops
from cellkit import gap, box, cell_mask, cells, CellPaint, outline_mask, dilate, circle_mask, polyline_mask, ellipse_pts
from daykit import curtain, rect_mask, rrect_pts, lit_rim, put_parts, C, YS, XS, ROWS, COLS

s = Svg(theme='light')
ink = s.ink

VB = 189                                                     # valance bottom (swags included)
FLOOR, LIP = 981, 1035                                       # stage floor top, apron lip row

bg = CellPaint()
# ----------------------------------------------------------------------------- back drape + border
bg.put(rect_mask(0, VB, 1920, FLOOR - 9), 0.1)

# ----------------------------------------------------------------------------- the spotlight cone (paper wedge)
LX, LENS = 960, 270
cone = cell_mask([[(LX - 27, LENS), (LX + 27, LENS), (1152, FLOOR), (768, FLOOR)]])
bg.put(cone & ~rect_mask(0, 0, 1920, LENS), -1)
# a second, wider step of half-light round the cone (the stepped edge, not a blur)
cone2 = cell_mask([[(LX - 45, LENS), (LX + 45, LENS), (1197, FLOOR), (723, FLOOR)]])
bg.put(cone2 & ~cone & ~rect_mask(0, 0, 1920, LENS) & rect_mask(0, 297, 1920, FLOOR), 0.05)
bg.emit(s)

# ----------------------------------------------------------------------------- stage floor: planks + the pool
fl = CellPaint()
fl.put(rect_mask(0, FLOOR, 1920, LIP), 0.3)
fl.put(rect_mask(0, FLOOR - 9, 1920, FLOOR), 0.62)           # back edge of the stage (upstage line)
for y in (999, 1017):
    fl.put(rect_mask(0, y, 1920, y + 9), -1)                 # plank joints
for k, (y0, y1) in enumerate(((FLOOR, 999), (1008, 1017), (1026, LIP))):
    for x in range((k * 153) % 279, 1920, 279):
        fl.put(rect_mask(x // P * P, y0, x // P * P + 9, y1), -1)   # staggered butt joints
# the pool of light: two hard steps (paper core, a .12 ring), joints stay carved
pool_out = cell_mask([ellipse_pts(960, 1008, 270, 40)])
pool_in = cell_mask([ellipse_pts(960, 1008, 207, 30)])
fl.v[pool_out & (fl.v > 0)] = 0.12
fl.v[pool_in & (fl.v > 0)] = 0.0
# apron lip + the front face with its panel joints
fl.put(rect_mask(0, LIP, 1920, LIP + 9), 0.95)
fl.put(rect_mask(0, LIP + 9, 1920, 1080), 0.42)
for x in range(0, 1920, 216):
    fl.put(rect_mask(x, LIP + 18, x + 9, 1080), -1)
fl.emit(s)
# footlights along the front edge: hooded lamps sitting on the lip (dense hoods, a carved glint), each
# with a cell of air above it on the boards (its light)
for x in range(63, 1920, 162):
    xx = x // P * P
    gap(s, xx - 27, LIP - 27, 63, 9)
    box(s, xx - 9, LIP - 18, xx + 18, LIP - 9, 0.95)
    box(s, xx - 18, LIP - 9, xx + 27, LIP, 0.95)
    gap(s, xx, LIP - 9, 9, 9)

# ----------------------------------------------------------------------------- the spotlight (a can on a pipe)
with s.cut():
    s.row(828, 1092, 225, 0.62)                                # pipe
    box(s, LX - 9, 234, LX + 9, 243, 0.85)                     # clamp
    can = cell_mask([rrect_pts(LX - 36, 243, LX + 36, LENS + 9, 8)])
    cp = CellPaint()
    cp.put(can, 0.9)
    cp.put(lit_rim(can, 1), 0.6)
    cp.put(rect_mask(LX - 54, LENS, LX - 36, LENS + 18) | rect_mask(LX + 36, LENS, LX + 54, LENS + 18), 0.85)   # barn doors
    cp.emit(s)
    box(s, LX - 27, LENS + 9, LX + 27, LENS + 18, 0.2)         # the lens (light)

# ----------------------------------------------------------------------------- curtains (heavy velvet)
def drape(side, x_top, x_tie, x_hem, top, tie, bottom):
    """A heavy curtain drawn to one side: its folds stay vertical columns (7-cell pleats: 3 dense, 2 mid,
    1 lit, a carved fold), the silhouette swoops in from the top to the tie and flares out to the hem.
    side = 'L' (on the left wall, lit from the right) or 'R'. x_* = the inner edge's distance from the
    outer edge (px)."""
    cp = CellPaint()
    r0, rt, r1 = C(top), C(tie), C(bottom - 1)
    for r in range(r0, r1 + 1):
        if r <= rt:
            u = (r - r0) / max(1, rt - r0)
            w = x_top - (x_top - x_tie) * u ** 2.2
        else:
            u = (r - rt) / max(1, r1 - rt)
            w = x_tie + (x_hem - x_tie) * u ** 0.75
        n = max(3, int(round(w / P)))
        for j in range(n):
            q = j % 7                                           # j counted from the outer edge
            val = (0.95, 0.95, 0.95, 0.62, 0.62, 0.3, -1)[q]
            c = j if side == 'L' else COLS - 1 - j
            cp.v[r, c] = val
        c_in = n - 1 if side == 'L' else COLS - n
        cp.v[r, c_in] = 0.95                                    # the inner edge: one dense column
    cp.put(rect_mask(0, bottom - 9, 1920, bottom) & ~np.isnan(cp.v), 0.95)   # hem
    cp.emit(s)
    # tie-back: a dense rope band round the gathered curtain + a tassel on its inner side
    w = x_tie
    x0, x1 = (0, w + 18) if side == 'L' else (1920 - w - 18, 1920)
    box(s, x0 // P * P, tie - 9, (x1 + 8) // P * P, tie + 9, 0.95)
    gap(s, x0 // P * P, tie + 9, (x1 + 8) // P * P - x0 // P * P, 9)
    tx = ((x1 - 18) if side == 'L' else (x0 + 9)) // P * P
    box(s, tx, tie + 9, tx + 9, tie + 36, 0.95)
    box(s, tx - 9, tie + 36, tx + 18, tie + 81, 0.95)
    gap(s, tx, tie + 54, 9, 9)


drape('L', 477, 207, 369, VB, 657, 972)
drape('R', 477, 207, 369, VB, 657, 972)

# ----------------------------------------------------------------------------- valance: pleats, swags, fringe, tassels
VT = 99                                                      # pleated band height
SW = 384                                                     # swag width
val = CellPaint()
band = rect_mask(0, 0, 1920, VT)
val.put(band, 0.45)
for x in range(0, 1920, 45):                                 # pleats: a fold shadow + a carved fold
    val.put(rect_mask(x + 27, 18, x + 36, VT), 0.95)
    val.put(rect_mask(x + 36, 18, x + 45, VT), -1)
val.put(rect_mask(0, 0, 1920, 9), 0.95)                      # top rail
val.put(rect_mask(0, 9, 1920, 18), -1)
for k in range(1920 // SW + 1):
    x0, x1 = k * SW, k * SW + SW
    cx = (x0 + x1) / 2
    outer = cell_mask([[(x0, VT - 9)] + [(cx + (x1 - x0) / 2 * math.cos(math.radians(a)), VT + 99 * math.sin(math.radians(a)))
                                          for a in range(180, -1, -10)] + [(x1, VT - 9)]])
    inner = cell_mask([[(x0 + 45, VT - 9)] + [(cx + (x1 - x0 - 90) / 2 * math.cos(math.radians(a)), VT + 45 * math.sin(math.radians(a)))
                                               for a in range(180, -1, -10)] + [(x1 - 36, VT - 9)]])
    val.put(dilate(outer) & ~outer & ~band, -1)
    val.put(outer, 0.95)                                     # the swag: dense,
    val.put(dilate(inner) & outer & ~inner & ~band, -1)      # a carved drape line,
    val.put(inner & ~band, 0.3)                              # its upper fold lighter
    # fringe under the swag: every other column, 3 cells, one cell of air
    for c in range(C(x0) + 1, min(COLS, C(x1))):
        rows_ = np.nonzero(outer[:, c])[0]
        if len(rows_) and c % 2 == 0:
            rr = rows_.max() + 2
            val.v[rr:rr + 4, c] = 0.85
for k in range(1920 // SW + 2):                              # tassels at the swag joints
    x = k * SW // P * P
    val.put(rect_mask(x - 9, VT, x + 9, VT + 45), 0.95)
    val.put(rect_mask(x - 18, VT + 45, x + 27, VT + 99), 0.95)
    val.put(rect_mask(x - 9, VT + 63, x + 18, VT + 72), -1)
    val.put(rect_mask(x - 18, VT + 99, x + 27, VT + 117) & ~rect_mask(x - 9, VT + 99, x, VT + 117) & ~rect_mask(x + 9, VT + 99, x + 18, VT + 117), 0.85)
with s.cut():
    val.emit(s)

# ----------------------------------------------------------------------------- prop chest with a crown (left)
CH0, CH1, LT_, LB_ = 405, 675, 819, 891                      # chest; lid top / lid bottom
ch = CellPaint()
lid = cell_mask([rrect_pts(CH0, LT_, CH1, LB_ + 45, 40)]) & rect_mask(CH0, LT_, CH1, LB_)
bodym = rect_mask(CH0, LB_ + 9, CH1, 972)
for m_ in (lid, bodym):
    ch.put(m_, 0.3)
    ch.put(outline_mask(m_), 0.95)
for x in (CH0 + 54, CH1 - 72):                               # metal straps over lid + body
    ch.put(rect_mask(x, LT_, x + 18, 972) & (lid | bodym), 0.95)
ch.put(rect_mask(CH0 + 9, LB_ + 36, CH1 - 9, LB_ + 45) & ~rect_mask(CH0 + 54, 0, CH0 + 72, 1080) & ~rect_mask(CH1 - 72, 0, CH1 - 54, 1080), 0.62)   # a plank line
mx = (CH0 + CH1) // 2 // P * P
ch.put(rect_mask(mx - 18, LB_ - 18, mx + 27, LB_ + 36), 0.95)  # lock plate over the joint, keyhole carved
ch.put(rect_mask(mx, LB_, mx + 9, LB_ + 18), -1)
ch.put(rect_mask(CH0 - 18, LB_ + 27, CH0, LB_ + 45) | rect_mask(CH1, LB_ + 27, CH1 + 18, LB_ + 45), 0.95)   # handles
# the crown sitting on the lid: a band with carved jewels, three points tipped with balls
crown = cell_mask([[(486, LT_), (486, LT_ - 72), (513, LT_ - 36), (540, LT_ - 81), (567, LT_ - 36), (594, LT_ - 72), (594, LT_)]])
ch.put(dilate(crown) & ~crown & ~np.isnan(ch.v), -1)
ch.put(crown, 0.95)
for x, y in ((486, LT_ - 81), (540, LT_ - 90), (594, LT_ - 81)):
    ch.put(rect_mask(x - 9, y - 9, x + 9, y + 9), 0.95)
ch.put(rect_mask(495, LT_ - 27, 594, LT_ - 18), -1)
for x in (504, 540, 576):
    ch.put(rect_mask(x, LT_ - 27, x + 9, LT_ - 18), 0.3)
with s.cut():
    ch.emit(s)

# ----------------------------------------------------------------------------- coat rack with hats (right)
RX = 1341                                                   # pole (2 cells)
rk = CellPaint()
rk.put(rect_mask(RX, 513, RX + 18, 954), 0.85)
rk.put(rect_mask(RX - 9, 486, RX + 27, 513), 0.95)           # finial
rk.put(rect_mask(RX - 72, 954, RX + 90, 972), 0.95)          # base bar + feet
rk.put(rect_mask(RX - 72, 945, RX - 45, 954) | rect_mask(RX + 63, 945, RX + 90, 954), 0.95)
rk.put(rect_mask(RX - 9, 936, RX + 27, 954), 0.95)
for y, d in ((585, -1), (585, 1), (702, -1), (702, 1)):      # hooks: out, then up
    if d < 0:
        rk.put(rect_mask(RX - 54, y, RX, y + 9), 0.85); rk.put(rect_mask(RX - 54, y - 18, RX - 45, y), 0.85)
    else:
        rk.put(rect_mask(RX + 18, y, RX + 72, y + 9), 0.85); rk.put(rect_mask(RX + 63, y - 18, RX + 72, y), 0.85)
# top hat on the upper left hook (hung by its brim): tall crown, carved band, brim
th = rect_mask(RX - 81, 504, RX - 27, 567) | rect_mask(RX - 99, 567, RX - 9, 585)
rk.put(dilate(th) & ~th & ~np.isnan(rk.v), -1)
rk.put(th, 0.95)
rk.put(rect_mask(RX - 81, 549, RX - 27, 558), -1)
rk.put(rect_mask(RX - 45, 504, RX - 27, 549), 0.62)          # the side toward the spotlight lit
# bowler on the upper right hook: dome, carved band, brim
dome = cell_mask([ellipse_pts(RX + 72, 576, 36, 54, a0=180, a1=360)])
bw = dome | rect_mask(RX + 27, 567, RX + 117, 585)
rk.put(dilate(bw) & ~bw & ~np.isnan(rk.v), -1)
rk.put(bw, 0.95)
rk.put(dome & np.broadcast_to(XS < RX + 63, dome.shape) & np.broadcast_to(YS < 558, dome.shape), 0.62)
rk.put(rect_mask(RX + 36, 549, RX + 108, 558) & dome, -1)
# striped scarf from the lower right hook: two tails, stripes carved, a fringe
for x0, y1 in ((RX + 45, 864), (RX + 72, 819)):
    m_ = rect_mask(x0, 693, x0 + 27, y1)
    rk.put(m_, 0.95)
    for y in range(720, y1 - 18, 36):
        rk.put(rect_mask(x0, y, x0 + 27, y + 9), -1)
    rk.put(rect_mask(x0, y1, x0 + 9, y1 + 18) | rect_mask(x0 + 18, y1, x0 + 27, y1 + 18), 0.62)
# cane on the lower left hook: crook + shaft
rk.put(rect_mask(RX - 72, 684, RX - 45, 693) | rect_mask(RX - 72, 693, RX - 63, 711), 0.95)
rk.put(rect_mask(RX - 72, 711, RX - 63, 918), 0.95)
rk.put(rect_mask(RX - 72, 918, RX - 63, 927), 0.62)
with s.cut():
    rk.emit(s)

if __name__ == '__main__':
    render(s, 'stage_day', 'light', 'r3_715_pool')
    crops('stage_day', [
        ('valance (swags, fringe, tassels) + curtain', (0, 0, 640, 720), 'v1_525_music_room', (760, 60, 1400, 780)),
        ('spotlight cone on the faint back drape, pool, footlights', (600, 200, 1320, 1080), 'r3_715_pool', (600, 120, 1320, 1000)),
        ('prop chest + crown', (380, 700, 720, 990), 'v1_180_study', (0, 640, 340, 930)),
        ('coat rack: top hat, bowler, scarf, cane', (1170, 460, 1500, 990), 'v1_525_music_room', (290, 240, 620, 770)),
    ])
