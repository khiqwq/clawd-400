"""SVG illustration -> the videos' halftone.

    python svg2dots.py scene.svg out.png [--theme dark|light] [--size 1920x1080]

Draw the scene as an SVG at screen size (viewBox 0 0 1920 1080) the way it should LOOK, in greys:
  dark theme  (night): light shapes on black — white = the biggest dot, black = no dot;
  light theme (day):   dark shapes on white paper — black = the biggest dot, white = no dot.
Chromium rasterizes it; every 9 x 9 px cell is averaged into one value (so shape edges get smaller
dots — the videos' smooth contours) and drawn as one round dot. Writes out.png (the halftone) and
out_value.png (the cell value map, 213 x 120, value = dot size).
"""
import argparse
import asyncio
import io
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import halftone  # noqa: E402

PITCH = halftone.PITCH


async def rasterize(svg_path, w, h):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': w, 'height': h})
        svg = open(svg_path, encoding='utf-8').read()
        await pg.set_content(f'<html><body style="margin:0;background:#888">{svg}</body></html>')
        await pg.wait_for_timeout(50)
        png = await pg.screenshot(clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        await b.close()
    return Image.open(io.BytesIO(png)).convert('L')


def cells_from_image(img, light=False):
    a = np.asarray(img, np.float32) / 255.0
    if light:
        a = 1.0 - a
    H, W = a.shape
    rows, cols = -(-H // PITCH), -(-W // PITCH)              # partial cells at the edge count too
    a = np.pad(a, ((0, rows * PITCH - H), (0, cols * PITCH - W)), mode='edge')
    return a.reshape(rows, PITCH, cols, PITCH).mean(axis=(1, 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('out')
    ap.add_argument('--theme', default='dark', choices=['dark', 'light'])
    ap.add_argument('--size', default='1920x1080')
    ap.add_argument('--debug', action='store_true', help='also write out_debug.png: the raster before the screen | the dots')
    a = ap.parse_args()
    w, h = (int(x) for x in a.size.split('x'))
    img = asyncio.run(rasterize(a.svg, w, h))
    light = a.theme == 'light'
    v = cells_from_image(img, light)
    Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)).save(a.out[:-4] + '_value.png')
    dots = halftone.render(v, light=light).crop((0, 0, w, h))      # exactly the frame size
    dots.save(a.out)
    if a.debug:
        sbs = Image.new('RGB', (w, h // 2), (90, 90, 90))
        sbs.paste(img.convert('RGB').resize((w // 2, h // 2)), (0, 0)); sbs.paste(dots.resize((w // 2, h // 2)), (w // 2, 0))
        sbs.save(a.out[:-4] + '_debug.png')
    print(a.out)


if __name__ == '__main__':
    main()
