"""Shared plumbing for the round-2 example scenes (drawn by a test run of this skill and kept as
worked examples): import the skill, render, compare, 1:1 crop sheets. Run: python station_night.py

The skill is imported from its own scripts folder (not copied).
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

SKILL = os.path.join(os.path.expanduser('~'), '.rec', 'claude', 'accounts', '52928', 'config', 'skills', 'clawd-halftone')
SCRIPTS = os.path.join(SKILL, 'scripts')
REFS = os.path.join(SKILL, 'assets', 'refs')
sys.path.insert(0, SCRIPTS)

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.join(HERE, 'out')
os.makedirs(SCENES, exist_ok=True)

from svgkit import Svg, L, P, snap  # noqa: E402,F401


def ref(name):
    return os.path.join(REFS, name + '.png')


def render(s, name, theme, ref_name):
    """svg -> dots (+ value map, debug sheet) -> compare sheet against a reference frame."""
    svg = s.save(os.path.join(SCENES, name + '.svg'))
    out = os.path.join(SCENES, name + '.png')
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'svg2dots.py'), svg, out, '--theme', theme, '--debug'], check=True)
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'compare.py'), out, '--ref', ref(ref_name),
                    '--out', os.path.join(SCENES, name + '_cmp.png')], check=True)
    return out


def crops(name, pairs, out=None, gap=12):
    """1:1 crop sheet: each pair = (label, my_box, ref_name, ref_box); boxes are (x0, y0, x1, y1) in px.
    Each row: my crop | the reference crop, both at 1:1."""
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


def crop(name, box, out, k=1):
    """Single 1:1 (or k x nearest) crop of my render, for close inspection."""
    im = Image.open(os.path.join(SCENES, name + '.png')).convert('RGB').crop(box)
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    im.save(out)
    return out


def raster(name, box=None, out=None, k=1):
    """The full-size raster of the svg before the screen (for checking the drawing itself)."""
    import asyncio
    import svg2dots
    img = asyncio.run(svg2dots.rasterize(os.path.join(SCENES, name + '.svg'), 1920, 1080))
    if box:
        img = img.crop(box)
    if k != 1:
        img = img.resize((img.width * k, img.height * k), Image.NEAREST)
    p = out or os.path.join(SCENES, name + '_raster.png')
    img.save(p)
    return p
