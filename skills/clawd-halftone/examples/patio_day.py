"""Worked example (day theme): the video-3 patio (assets/refs/r3_390_patio.png), redrawn with svgkit.

Read it for the technique:
  - every outline row/column sits on the 9-px grid (frame/row/col, coordinates multiples of 9);
  - tones from the measured table (floor .14, pot .17/.24, panels .25, sun .38, frame lines .62,
    dense plant .9, chair seat .96), at most ~5 levels;
  - rounded things shade as a hard step (pot, cyl), leaves split lit/dark with a 6-px paper midrib;
  - near things are cut out of what is behind (s.cut / leaf air);
  - the far city is faint (.22) with window gaps, and only shows through the window.
Clawd sits on the chair (body x 553..777, feet on the seat at y 783).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))
from svgkit import Svg, L, P  # noqa: E402

s = Svg(theme='light')

# far: the city through the window (clipped to the glass), faint
win = s.clip_rect(189, 72, 1125, 603)
with s.plane(clip=win):
    s.skyline(400, 1320, 684, [117, 72, 153, 90, 135, 108], v=0.22, seed=3)
# the window: one thin frame line (5-6 px reads as a row of medium dots) — on the grid
s.frame(180, 63, 1323, 684, 0.62)
s.col(1557, 99, 693, 0.62)
s.sun(639, 261, 90, v=0.38, ray_v=0.45)

# floor band
s.row(0, 1920, 981, 0.14, rows=11)

# left plant: broad leaves with notches, lit from the upper left, air between them
for ang, ln, wd in ((-66, 290, 126), (-36, 380, 140), (-6, 360, 134), (26, 380, 140), (56, 320, 128), (84, 230, 112)):
    s.leaf(252, 756, ang, ln, wd, dark=0.62, lit=0.34, edge=0.8, curl=0.14 * (1 if ang > 0 else -1), air=9, notches=2 if ln > 300 else 0)
s.pot(252, 972, 225, 216)

# chair (Clawd sits on it): seat the darkest piece, rail, splayed legs
s.row(495, 765, 783, 0.96, rows=3)
s.row(531, 729, 837, 0.7, rows=3)
s.line(540, 864, 522, 972, s.ink(0.9), 9); s.line(720, 864, 738, 972, s.ink(0.9), 9)
s.row(531, 729, 882, 0.6)

# desk: top slab, cabinet with two doors (light panels, one-cell outlines), clock, lamp
s.frame(792, 720, 1269, 756, 0.6, fill=0.28)
s.panel(819, 756, 423, 216, fill=0.25, edge=0.6)
s.panel(837, 774, 189, 180, fill=0.25, edge=0.5)
s.panel(1035, 774, 189, 180, fill=0.25, edge=0.5)
s.rect(1008, 855, 9, 18, fill=s.ink(0.9)); s.rect(1044, 855, 9, 18, fill=s.ink(0.9))
with s.cut():
    s.circle(1089, 675, 36, fill=s.ink(0.2), stroke=s.ink(0.9), sw=9)
    s.line(1089, 675, 1089, 652, s.ink(0.9), 7); s.line(1089, 675, 1106, 684, s.ink(0.9), 7)
s.row(1053, 1125, 702, 0.8, rows=2)
s.line(1179, 711, 1179, 639, s.ink(0.85), 9); s.line(1179, 639, 1125, 585, s.ink(0.85), 9)
s.path('M1053 603 Q1098 540 1152 576 L1143 612 Q1098 590 1062 621 Z', fill=s.ink(0.8))
s.row(1134, 1233, 702, 0.66, rows=2)

# flower pot: petals as outlined discs (>= 2 cells), dark centres
for fx, fy in ((1395, 837), (1467, 801), (1539, 846)):
    for k in range(6):
        import math
        a = k * math.pi / 3
        s.circle(fx + 23 * math.cos(a), fy + 23 * math.sin(a), 16, fill=s.ink(0.3), stroke=s.ink(0.85), sw=7)
    s.circle(fx, fy, 13, fill=s.ink(0.9))
s.leaf(1431, 858, -62, 90, 54, dark=0.62, lit=0.34, midrib=0)
s.leaf(1521, 858, 58, 90, 54, dark=0.62, lit=0.34, midrib=0)
s.pot(1467, 972, 162, 135)

# right plant: tall dense leaves (bird of paradise) on long stems, the room's darkest mass
for ang, ln, wd, cv in ((-60, 330, 117, -0.1), (-36, 420, 126, -0.08), (-12, 480, 117, 0.0), (12, 490, 117, 0.05), (36, 440, 122, 0.08), (60, 360, 117, 0.1), (80, 270, 108, 0.12)):
    s.leaf(1701, 792, ang, ln, wd, dark=0.95, lit=0.7, edge=0.95, curl=cv, stem=150, stem_v=0.85, air=9)
s.pot(1701, 972, 198, 180)

if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    svg = s.save(os.path.join(out, 'patio_day.svg'))
    subprocess.run([sys.executable, os.path.join(HERE, '..', 'scripts', 'svg2dots.py'), svg, os.path.join(out, 'patio_day.png'),
                    '--theme', 'light', '--debug'], check=True)
