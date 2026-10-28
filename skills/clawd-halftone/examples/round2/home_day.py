"""Scene 3 — home_day (light): a cosy living room in daylight.

Left → right: bookshelf (books, small objects, a trailing plant on top) · snake plant in a small pot ·
sofa under the big window (sun + far city in the glass, a succulent on the sill) — Clawd stands in front of
the sofa, centre, x 850-1075, feet y 975 · floor lamp under a framed picture · big dense plant in a big pot.
A rug on the floor band. Light from the upper left (the sun side): rounded things shade on the right.
Tones (day, ink on cream): wall/sky 0 · floor .18 · panels/sofa .26 · pots .2/.3 · lines .55-.62 ·
sun .36 · city .2 · dense plant, pillow, legs .9-.96.
"""
import math

from common import Svg, P, render, crops
from extras import gap, box, cell_mask, cells, bez, polyline_mask, outline_mask, ellipse_pts

s = Svg(theme='light')
ink = s.ink

# ----------------------------------------------------------------------------- window: sun + far city
WX0, WY0, WX1, WY1 = 621, 99, 1305, 594
glass = s.clip_rect(WX0 + 9, WY0 + 9, WX1 - WX0 - 18, WY1 - WY0 - 18)
with s.plane(clip=glass):
    s.skyline(WX0 + 9, WX1, WY1 - 9, [126, 81, 171, 108, 144, 90, 153, 117], v=0.2, seed=5, widths=(72, 135))
    s.sun(810, 252, 72, v=0.36, ray_v=0.3, rays=12, ray_len=27, gap=27)
s.frame(WX0, WY0, WX1, WY1, 0.6)                          # frame: one crisp line
s.col(954, WY0 + 9, WY1 - 9, 0.6)                         # centre mullion
box(s, WX0 - 27, WY1, WX1 + 27, WY1 + 18, 0.42)            # sill (2 rows)
# roller blind rolled up at the top, with its pull cord
box(s, WX0 + 18, WY0 + 9, WX1 - 18, WY0 + 27, 0.3)
s.col(1251, WY0 + 27, WY0 + 117, 0.5)
box(s, 1242, WY0 + 117, 1269, WY0 + 135, 0.7, rx=4)

# succulent on the sill (small pot)
s.pot(1215, WY1, 72, 54, body=0.2, rim=0.3, edge=0.6, shade=0.42)
for ang, ln in ((-50, 36), (-15, 45), (20, 42), (55, 33)):
    s.leaf(1215, WY1 - 54, ang, ln, 27, dark=0.9, lit=0.62, edge=None, midrib=0, curl=0)

# ----------------------------------------------------------------------------- picture on the wall
with s.shift(dx=-72):                                      # centred over the floor lamp
    PX0, PY0, PX1, PY1 = 1386, 162, 1593, 333
    s.frame(PX0, PY0, PX1, PY1, 0.85)                          # frame (dense) + a paper mat inside
    s.frame(PX0 + 27, PY0 + 27, PX1 - 27, PY1 - 27, 0.4)       # the picture's edge
    pic = s.clip_rect(PX0 + 36, PY0 + 36, PX1 - PX0 - 72, PY1 - PY0 - 72)
    with s.plane(clip=pic):
        s.circle(1449, 225, 18, fill=ink(0.36))
        cells(s, cell_mask([[(PX0 + 27, 297), (1458, 252), (1494, 270), (1530, 234), (PX1 - 27, 279), (PX1 - 27, 300), (PX0 + 27, 300)]]), 0.62)
    s.col(1485, 108, PY0, 0.4)                                 # hanging wire to a nail
    box(s, 1476, 99, 1503, 117, 0.7, rx=4)

# ----------------------------------------------------------------------------- floor band + rug
s.row(0, 1920, 981, 0.18, rows=11)
s.row(0, 1920, 972, 0.42)                                  # skirting line
RG0, RG1, RGT, RGB = 549, 1377, 999, 1062
box(s, RG0, RGT, RG1, RGB, 0.62)                           # rug: a dense band, pattern carved
gap(s, RG0 + 9, RGT + 9, RG1 - RG0 - 18, 9)               # inner border
gap(s, RG0 + 9, RGB - 18, RG1 - RG0 - 18, 9)
for k, x in enumerate(range(RG0 + 45, RG1 - 36, 54)):      # diamonds: a carved 3-row lozenge each
    gap(s, x, RGT + 27, 9, 9); gap(s, x - 9, RGT + 36, 27, 9); gap(s, x, RGT + 45, 9, 9)
    box(s, x, RGT + 36, x + 9, RGT + 45, 0.62)
for y in range(RGT, RGB, 18):                              # fringe
    s.row(RG0 - 27, RG0, y, 0.45); s.row(RG1, RG1 + 27, y, 0.45)

# ----------------------------------------------------------------------------- bookshelf (left)
BS0, BS1, BST, BSB = 45, 459, 351, 972
SH = [BST, 504, 657, 810, BSB - 18]                        # shelf boards (top of each, 2 rows thick)
with s.cut():
    box(s, BS0, BST, BS1, BSB, 0.0)
    s.frame(BS0, BST, BS1, BSB, 0.62)
    for y in SH:
        box(s, BS0, y, BS1, y + 18, 0.62)
    box(s, BS0 - 9, BST - 9, BS1 + 9, BST + 9, 0.62)       # top board overhang
    box(s, BS0 + 9, BSB, BS0 + 36, BSB + 9, 0.9); box(s, BS1 - 36, BSB, BS1 - 9, BSB + 9, 0.9)   # feet


def books(x0, base, specs):
    """A run of books standing on a shelf: specs = [(width_cells, height_px, tone, lean), ...]; 1-cell
    gaps between them; a spine band carved near the top of the thicker ones."""
    x = x0
    for wc, h, v, lean in specs:
        w = wc * P
        if lean:
            s.poly([(x, base), (x + w, base), (x + w + lean, base - h), (x + lean, base - h)], fill=ink(v))
        else:
            box(s, x, base - h, x + w, base, v)
            if wc >= 3:
                gap(s, x + 9, base - h + 18, w - 18, 9)
            if wc >= 3 and h > 100:
                gap(s, x + 9, base - 36, w - 18, 9)
        x += w + P
    return x


# shelf 1 (y 504): books + a small clock
x = books(BS0 + 18, 504, [(3, 108, 0.9, 0), (2, 126, 0.55, 0), (3, 117, 0.3, 0), (2, 99, 0.9, 0), (4, 90, 0.55, 0)])
s.circle(x + 54, 504 - 45, 36, fill=ink(0.26), stroke=ink(0.85), sw=9)     # clock
box(s, x + 49.5, 504 - 72, x + 58.5, 504 - 45, 0.85); box(s, x + 54, 504 - 49.5, x + 81, 504 - 40.5, 0.85)
box(s, x + 36, 504 - 9, x + 72, 504, 0.85)
# shelf 2 (y 657): a vase with a sprig, books lying flat, a bookend
s.cyl(BS0 + 27, 657 - 90, BS0 + 81, 657, 0.26, 0.5, light_left=True, band=0.34, rx=14)
box(s, BS0 + 36, 657 - 99, BS0 + 72, 657 - 90, 0.62)
for ang in (-20, 10, 35):
    s.leaf(BS0 + 54, 657 - 99, ang, 63, 22, dark=0.9, lit=0.6, edge=None, midrib=0, curl=0.1)
for k, (w, v) in enumerate(((207, 0.55), (189, 0.9), (216, 0.3))):     # a stack lying flat
    box(s, BS0 + 126, 657 - 27 * (k + 1), BS0 + 126 + w, 657 - 27 * k - 9, v)
x = books(BS0 + 351, 657, [(2, 117, 0.9, 0), (2, 108, 0.55, 0)])
# shelf 3 (y 810): globe on a stand + books
gx, gy = BS0 + 81, 810 - 72
s.circle(gx, gy, 45, fill=ink(0.26))
s.path(f'M{gx - 45} {gy} A45 45 0 0 0 {gx + 45} {gy}', fill=ink(0.55))   # shaded lower half... hard step
s.path(f'M{gx - 14} {gy - 40} Q{gx + 22} {gy - 18} {gx - 4} {gy + 18}', stroke=ink(0.85), sw=9)   # a continent
s.path(f'M{gx - 58} {gy - 30} A58 58 0 0 0 {gx + 30} {gy + 50}', stroke=ink(0.62), sw=9)          # meridian ring
box(s, gx - 27, 801, gx + 27, 810, 0.85); box(s, gx - 4.5, gy + 45, gx + 4.5, 801, 0.85)
books(BS0 + 171, 810, [(3, 126, 0.55, 0), (3, 135, 0.9, 0), (2, 117, 0.3, 0), (3, 126, 0.55, 0), (2, 99, 0, 27)])
# shelf 4 (y 954): baskets / boxes
for bx0, v in ((BS0 + 27, 0.3), (BS0 + 216, 0.55)):
    box(s, bx0, 954 - 117, bx0 + 171, 954, v)
    for yy in range(954 - 99, 954, 18):
        gap(s, bx0 + 9, yy, 153, 9) if v == 0.3 else None
    if v == 0.55:
        box(s, bx0 + 72, 954 - 99, bx0 + 99, 954 - 81, 0.95)                 # handle
        gap(s, bx0 + 9, 954 - 63, 153, 9)
# pilea ("pancake plant") on top of the shelf: thin stems, round leaves split lit/dark (hard step)
PX, PB = 369, BST - 9
for (ex, ey, r) in ((-72, -171, 29), (-18, -225, 32), (40, -198, 29), (81, -144, 27), (-90, -117, 25), (18, -144, 27)):
    s.line(PX + 4.5, PB - 72, PX + 4.5 + ex * 0.8, PB + ey + r * 0.6, ink(0.62), 7)
for (ex, ey, r) in ((-72, -171, 29), (-18, -225, 32), (40, -198, 29), (81, -144, 27), (-90, -117, 25), (18, -144, 27)):
    cxl, cyl = PX + 4.5 + ex, PB + ey
    s.circle(cxl, cyl, r + 9, fill=s.paper)
    s.circle(cxl, cyl, r, fill=ink(0.6))
    s.path(f'M{cxl} {cyl - r} A{r} {r} 0 0 1 {cxl} {cyl + r} Z', fill=ink(0.92))   # shade half (right)
s.pot(PX, PB, 99, 81, body=0.2, rim=0.3, edge=0.62, shade=0.44)

# ----------------------------------------------------------------------------- snake plant (small floor pot)
for dx, ang, ln, wd in ((-27, -12, 180, 36), (0, 2, 234, 40), (27, 14, 171, 36), (-9, -28, 126, 32), (18, 30, 117, 32)):
    s.leaf(531 + dx, 873, ang, ln, wd, dark=0.95, lit=0.66, edge=None, midrib=0, curl=0.02, air=9)
s.pot(531, 972, 108, 108, body=0.2, rim=0.3, edge=0.62, shade=0.44)

# ----------------------------------------------------------------------------- sofa
SX0, SX1 = 612, 1314


def soft(x0, y0, x1, y1, v, edge=0.62, rx=27):
    """A cushion: light field + one-cell outline (like the patio desk panels)."""
    s.rect(x0, y0, x1 - x0, y1 - y0, fill=ink(v), rx=rx)
    s.rect(x0 + 4.5, y0 + 4.5, x1 - x0 - 9, y1 - y0 - 9, stroke=ink(edge), sw=9, rx=max(0, rx - 4.5))


with s.cut():
    box(s, SX0 + 63, 864, SX1 - 63, 945, 0.5)                                 # base (darker)
    for k in range(3):                                                        # back cushions
        cx0 = SX0 + 90 + k * 180
        soft(cx0, 666, cx0 + 171, 819, 0.16)
    for k in range(3):                                                        # seat cushions
        cx0 = SX0 + 90 + k * 180
        soft(cx0, 801, cx0 + 171, 873, 0.26, rx=18)
    for ax0 in (SX0, SX1 - 99):                                               # arms: hard shade band
        s.cyl(ax0, 720, ax0 + 99, 945, 0.3, 0.56, light_left=True, band=0.34, rx=40)
        s.rect(ax0 + 4.5, 724.5, 90, 216, stroke=ink(0.7), sw=9, rx=36)
    for lx in (SX0 + 27, SX0 + 72, SX1 - 99, SX1 - 54):                       # tapered legs
        s.poly([(lx, 945), (lx + 27, 945), (lx + 21, 972), (lx + 6, 972)], fill=ink(0.92))
gap(s, SX0 + 99, 900, SX1 - SX0 - 198, 9)                                     # base piping
for k in range(3):                                                            # tufting buttons
    cx0 = SX0 + 90 + k * 180
    for bx in (cx0 + 54, cx0 + 108):
        box(s, bx, 720, bx + 9, 729, 0.7)
# throw pillows: a dense one (left), a striped one (right), each cut out of the sofa
with s.cut():
    s.rect(SX0 + 108, 702, 126, 117, fill=ink(0.92), rx=22)
    s.rect(SX1 - 234, 711, 117, 108, fill=ink(0.5), rx=20)
for y in range(729, 810, 18):
    gap(s, SX1 - 225, y, 99, 9)
box(s, SX0 + 162, 756, SX0 + 180, 774, 0.2)

# ----------------------------------------------------------------------------- floor lamp (off, daytime)
def floor_lamp(lx, top=387, base=972):
    """Floor lamp: a crisp drum shade (cell mask, wider at the bottom) with a hard shade band on the right,
    rim rows, a one-cell pole, a pull switch, a dense base. lx = pole cell (multiple of 9)."""
    import numpy as _np
    bot = top + 90
    with s.cut():
        shade = cell_mask([[(lx - 45, top), (lx + 54, top), (lx + 90, bot), (lx - 81, bot)]])
        cells(s, shade, 0.26)
        sh = _np.zeros_like(shade); sh[:, int((lx + 27) // P):] = True
        cells(s, shade & sh, 0.46)
        s.row(lx - 81, lx + 90, bot, 0.62); s.row(lx - 45, lx + 54, top - 9, 0.62)
        s.col(lx, bot + 9, base - 18, 0.62)
        s.rect(lx - 45, base - 18, 99, 18, fill=ink(0.85), rx=8)
        box(s, lx + 9, bot + 108, lx + 18, bot + 180, 0.45)                # pull switch
    box(s, lx - 9, bot + 9, lx + 18, bot + 18, 0.62)


floor_lamp(1413)

# ----------------------------------------------------------------------------- big plant (right): dense
PCX = 1782
# bird of paradise: paddle leaves on long stems, spread so each leaf keeps paper around it (the ref's
# leaves never touch); back leaves first, the front ones over them with an air margin
for ang, stem, ln, wd, cv in ((-50, 150, 230, 92, -0.12), (50, 140, 220, 92, 0.12), (-30, 250, 250, 96, -0.08),
                              (28, 260, 250, 96, 0.08), (-10, 330, 260, 92, -0.04), (10, 200, 240, 96, 0.05),
                              (-68, 70, 190, 84, -0.14), (70, 60, 180, 84, 0.14)):
    s.leaf(PCX, 810, ang, ln, wd, dark=0.95, lit=0.7, edge=0.95, curl=cv, stem=stem, stem_v=0.85, stem_w=9,
           air=14, midrib=7)
s.pot(PCX, 972, 207, 189, body=0.2, rim=0.3, edge=0.62, shade=0.44)

if __name__ == '__main__':
    render(s, 'home_day', 'light', 'r3_390_patio')
    crops('home_day', [
        ('big plant + pot', (1440, 140, 1920, 990), 'r3_390_patio', (1300, 100, 1780, 950)),
        ('window: sun + far city', (600, 80, 1330, 620), 'r3_390_patio', (340, 50, 1070, 590)),
        ('sofa + snake plant (Clawd stands here)', (440, 600, 1340, 1000), 'r3_390_patio', (60, 560, 960, 960)),
    ])
