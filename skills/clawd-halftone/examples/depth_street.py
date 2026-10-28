"""Worked example: depth the videos' way — a night street in three planes.

far plane (fade .45): skyline silhouettes, a few lit windows, no outlines
mid plane (fade .85): two buildings as blocks (front face + darker side face + lighter top), 1-cell rims
near plane (fade 1):  a lamp post, a railing, a bench — 2-cell bright outlines, the lamp's glow
light: the moon (upper left) and the street lamp; the side faces turn away from the moon (side='r').
Clawd would walk along the pavement at row ~108.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from paint import Paint, T  # noqa: E402

p = Paint(213, 120)

# sky: the moon with its halo (a light source, MAX), nothing else — the sky stays empty
p.glow(40, 22, 30, 0.22, power=1.8)
p.circle(40, 22, 7, T.MAX)

# far plane: skyline, flat, no outlines, sparse lit windows
far = p.plane()
for x, w, h in ((60, 14, 46), (76, 10, 34), (88, 18, 56), (108, 12, 40), (122, 20, 62), (144, 9, 30), (155, 16, 50), (173, 22, 44), (196, 17, 58)):
    far.rect(x, 96 - h, w, h, T.MID)
    for yy in range(96 - h + 4, 92, 6):
        for xx in range(x + 2, x + w - 2, 4):
            if (xx * 7 + yy * 3) % 5 == 0:
                far.rect(xx, yy, 2, 2, T.LIGHT + 0.2)
p.over(far, fade=0.45)

# mid plane: two buildings as blocks with side faces, rims, windows with sills
mid = p.plane()
mid.block(8, 30, 46, 72, T.MID, d=8, side='r', line=T.LIGHT)
for r in range(4):
    for c in range(3):
        x, y = 13 + c * 14, 36 + r * 16
        mid.rect(x, y, 8, 10, T.FAINT, line=T.LIGHT)
        if (r + c) % 3 == 0:
            mid.rect(x + 1, y + 1, 6, 8, 0.7)          # a lit window
        mid.rect(x - 1, y + 10, 10, 1, T.LIGHT)
mid.block(150, 44, 40, 58, T.MID, d=8, side='r', line=T.LIGHT)
for r in range(3):
    for c in range(3):
        x, y = 154 + c * 12, 50 + r * 15
        mid.rect(x, y, 7, 9, T.FAINT, line=T.LIGHT)
mid.rect(162, 88, 12, 14, T.DIM, line=T.LIGHT)          # a door
mid.poly([(158, 86), (178, 86), (181, 82), (155, 82)], T.LIGHT)   # its awning
p.over(mid, fade=0.85)

# ground: pavement band with a kerb, slabs fading with distance
p.rect(0, 102, 213, 2, T.LIGHT)
p.rect(0, 104, 213, 16, T.DIM)
for x in range(0, 213, 12):
    p.rect(x, 104, 1, 16, T.FAINT)

# near plane: lamp post with a 2-cell bright outline, a railing, a bench
near = p.plane()
near.rect(118, 22, 3, 82, T.BRIGHT)
near.poly([(112, 22), (127, 22), (124, 15), (115, 15)], T.LIGHT, line=T.BRIGHT, lw=2)
near.rect(115, 22, 9, 3, T.MAX)
for x in range(60, 104, 6):
    near.rect(x, 90, 1, 13, T.LIGHT)
near.rect(58, 89, 48, 2, T.BRIGHT)
near.block(132, 92, 22, 3, T.LIGHT, d=3, side='r')       # bench seat
near.rect(134, 95, 2, 8, T.LIGHT); near.rect(150, 95, 2, 8, T.LIGHT)
near.rect(132, 84, 22, 2, T.LIGHT)                       # backrest
p.over(near, fade=1.0)

# light pass: the lamp's pool on the pavement and on the nearby faces; shadow under the bench
p.glow(120, 30, 42, 0.32, power=1.5, only_painted=True)
p.beam([(104, 104), (136, 104), (146, 120), (94, 120)], 0.28, fade_to=0.3)
p.shade(132, 103, 22, 4, 0.5)

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
    os.makedirs(out, exist_ok=True)
    print(p.save(os.path.join(out, 'depth_street')))
