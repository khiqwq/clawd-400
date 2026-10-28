"""Shared plumbing for the promo backdrops (day set drawn in this folder): import the skill, render,
check the GIF square, 1:1 crop sheets.  Run a scene: python lounge_day.py

The skill is imported from its own scripts folder (not copied, not edited).
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

SKILL = os.path.join(os.path.expanduser('~'), '.rec', 'claude', 'accounts', '52928', 'config', 'skills', 'clawd-halftone')
SCRIPTS = os.path.join(SKILL, 'scripts')
REFS = os.path.join(SKILL, 'assets', 'refs')
sys.path.insert(0, SCRIPTS)

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.join(HERE, 'scenes')
WORK = os.path.join(HERE, 'work')                  # compare sheets, close-up crops while iterating
os.makedirs(SCENES, exist_ok=True)
os.makedirs(WORK, exist_ok=True)

from svgkit import Svg, L, P, snap  # noqa: E402,F401

# The GIF square of the promo (brief_promo.md) and its calm core
GIF = (680, 471, 1240, 1031)
CALM = (740, 500, 1180, 975)


def ref(name):
    return os.path.join(REFS, name + '.png')


def render(s, name, theme='light', ref_name='r3_390_patio'):
    """svg -> dots (+ value map, debug sheet), a compare sheet in work/, the GIF-square check."""
    svg = s.save(os.path.join(SCENES, name + '.svg'))
    out = os.path.join(SCENES, name + '.png')
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'svg2dots.py'), svg, out, '--theme', theme, '--debug'], check=True)
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'compare.py'), out, '--ref', ref(ref_name),
                    '--out', os.path.join(WORK, name + '_cmp.png')], check=True)
    square(name)
    return out


def square(name):
    """The render with the GIF square (solid) and its calm core (dashed) outlined; prints the densest
    cell inside the calm core above the floor band (must stay <= .1)."""
    im = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB')
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = GIF
    for k in range(3):
        d.rectangle((x0 - k, y0 - k, x1 + k, y1 + k), outline=(214, 60, 40))
    cx0, cy0, cx1, cy1 = CALM
    for x in range(cx0, cx1, 24):
        d.line((x, cy0, min(x + 12, cx1), cy0), fill=(30, 120, 200), width=2)
        d.line((x, cy1, min(x + 12, cx1), cy1), fill=(30, 120, 200), width=2)
    for y in range(cy0, cy1, 24):
        d.line((cx0, y, cx0, min(y + 12, cy1)), fill=(30, 120, 200), width=2)
        d.line((cx1, y, cx1, min(y + 12, cy1)), fill=(30, 120, 200), width=2)
    v = np.asarray(Image.open(os.path.join(SCENES, name + '_value.png')).convert('L'), np.float32) / 255
    c0, c1 = cx0 // P, (cx1 - 1) // P
    r0, r1 = cy0 // P, (cy1 - 1) // P - 1                 # the last row touches the floor line
    core = v[r0:r1 + 1, c0:c1 + 1]
    mx = float(core.max())
    n = int((core > 0.105).sum())
    d.text((x0 + 6, y0 + 6), f'calm core max {mx:.2f}, cells > .1: {n}', fill=(214, 60, 40))
    im.save(os.path.join(SCENES, name + '_square.png'))
    print(f'{name}: calm core max {mx:.3f}, cells > .1: {n}')
    return mx, n


def crops(name, pairs, out=None, gap=12):
    """1:1 crop sheet: each pair = (label, my_box, ref_name, ref_box); boxes are (x0, y0, x1, y1) in px."""
    mine = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB')
    rows = []
    for label, mb, rn, rb in pairs:
        a = mine.crop(mb)
        b = Image.open(ref(rn)).convert('RGB').crop(rb)
        h = max(a.height, b.height) + 22
        row = Image.new('RGB', (a.width + b.width + gap, h), (80, 80, 80))
        row.paste(a, (0, 22)); row.paste(b, (a.width + gap, 22))
        d = ImageDraw.Draw(row)
        d.text((4, 4), f'mine: {label}  {mb}', fill=(255, 210, 0))
        d.text((a.width + gap + 4, 4), f'ref {rn}  {rb}', fill=(255, 210, 0))
        rows.append(row)
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + gap * (len(rows) - 1)
    sheet = Image.new('RGB', (W, H), (60, 60, 60))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height + gap
    p = out or os.path.join(SCENES, name + '_crops.png')
    sheet.save(p)
    return p


def crop(name, box, tag, k=1):
    """A 1:1 (or k x nearest) crop of my render into work/, for close inspection."""
    im = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB').crop(box)
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    p = os.path.join(WORK, f'{name}_{tag}.png')
    im.save(p)
    return p


if __name__ == '__main__':
    # python common.py crop <name> x0 y0 x1 y1 tag [k]
    if sys.argv[1] == 'crop':
        n = sys.argv[2]; b = tuple(int(t) for t in sys.argv[3:7]); t = sys.argv[7]
        k = int(sys.argv[8]) if len(sys.argv) > 8 else 1
        print(crop(n, b, t, k))
    elif sys.argv[1] == 'square':
        square(sys.argv[2])
