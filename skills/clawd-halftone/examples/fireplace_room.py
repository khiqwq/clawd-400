"""Worked example: the reference fireplace room (video 1), repainted with paint.py from its recovered
value map (references/ref_maps/night_fireplace.png). Compare examples/out/fireplace_room.png with
assets/refs/v1_300.png. Clawd sits in the armchair's dark cut-out (x 40-72, y 67-92).

Read it for HOW a room is built: flat tones by importance, inset details, one light source with a
gradient, a patterned floor band — not for its layout.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from paint import Paint, T  # noqa: E402

p = Paint(213, 120)

# floor band: a rail line and dim vertical boards (drawn first, furniture stands on it)
p.rect(0, 96, 213, 2, T.MID)
for x in range(2, 213, 10):
    p.rect(x, 98, 1, 22, 0.24)

# curtains + rod: mid tone, darker fold lines
p.rect(0, 4, 104, 2, 0.6); p.rect(97, 3, 8, 4, 0.6)
for (x0, x1) in ((0, 16), (75, 96)):
    p.rect(x0, 6, x1 - x0, 84, 0.35)
    for fx in range(x0 + 4, x1 - 1, 5):
        p.rect(fx, 12, 1, 70, 0.2)

# window: outside is dark with a faint tree and rain; the frame is a bright grid
p.rect(16, 12, 60, 57, T.EMPTY)
p.poly([(16, 20), (28, 14), (40, 22), (34, 30), (44, 34), (30, 38), (36, 44), (16, 46)], T.FAINT + 0.12)
for (x, y) in ((61, 15), (74, 26), (36, 41), (55, 44)):
    p.line(x, y, x - 2, y + 4, 0.7)
p.box(16, 12, 60, 57, 0.9)
for x in (23, 46, 67):
    p.rect(x, 12, 2, 57, 0.9)
for y in (31, 50):
    p.rect(16, y, 60, 2, 0.9)

# the armchair is the key object: brightest flat shape, round arms with a spiral, legs
p.rrect(33, 54, 44, 44, 8, 0.92)
p.ellipse(26, 76, 16, 14, 0.92); p.ellipse(76, 76, 14, 14, 0.92)
p.circle(36, 83, 3, 0.45); p.circle(84, 83, 3, 0.45)
p.rect(24, 96, 4, 13, 0.92); p.rect(80, 96, 3, 13, 0.92)
p.rect(40, 67, 32, 25, T.EMPTY)                      # where Clawd sits

# a cat asleep on a footstool, left
p.rect(6, 96, 24, 2, T.MID)
p.poly([(8, 91), (14, 89), (26, 90), (30, 94), (28, 97), (10, 97)], 0.9)
p.rect(25, 97, 3, 10, 0.9)

# fireplace: mid stone body, brick arch with dark mortar, a hot interior lit by the fire
p.rect(135, 0, 15, 48, T.MID); p.rect(132, 13, 21, 3, 0.4)
p.rect(119, 48, 61, 8, 0.36)
p.rect(110, 56, 64, 54, T.MID)
p.bricks(110, 56, 64, 54, T.MID, 0.12, bw=7, bh=4)
p.rect(123, 66, 39, 41, 0.0)
p.ellipse(123, 58, 39, 18, 0.0)
p.glow(142, 92, 26, 0.42, power=1.3, region=(123, 58, 39, 49))
p.poly([(133, 107), (136, 86), (139, 92), (142, 79), (146, 90), (149, 84), (151, 107)], 0.92)
p.line(126, 108, 158, 100, 0.92, 2); p.line(128, 100, 160, 108, 0.92, 2)
p.rect(107, 108, 70, 3, T.MID)

# mantel things: a trailing plant, a small box, books
p.leaves(110, 50, 7, 11, 0.9, seed=3, droop=0.5)
p.line(108, 50, 112, 66, 0.9)
p.rect(125, 41, 7, 7, 0.75); p.rect(126, 42, 5, 5, 0.3)
p.books(157, 38, 13, 10, seed=2, tones=(0.6, 0.8, 0.7))

# a picture on the wall: dim frame, a sun and a line of hills inside
p.rect(186, 21, 27, 38, 0.33); p.rect(188, 23, 25, 34, 0.08)
p.circle(198, 33, 6, 0.33)
p.polyline([(189, 53), (195, 45), (200, 49), (209, 38), (213, 42)], 0.33, 2)

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
    os.makedirs(out, exist_ok=True)
    print(p.save(os.path.join(out, 'fireplace_room')))
