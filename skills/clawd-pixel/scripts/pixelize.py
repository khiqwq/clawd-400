"""Turn a frame of a reference video into Clawd's logical-pixel grid (or dump the engine's own).

    python pixelize.py frame.png [frame2.png ...] [--unit 13.9]
    python pixelize.py --engine view=qr tilt=1 eyes=focus

Output legend: O body orange, o shade, K black (eyes), . anything else.
The grid is anchored on the top-left of Clawd's orange pixels; in the 1080p reference videos one
logical pixel is 13.9 px.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def orange_mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 150) & (g > 70) & (g < 160) & (b < 130) & (r - b > 60)


def cell(c):
    r, g, b = (int(v) for v in c)
    if r > 150 and r - b > 60 and g < 160:
        return 'O' if r > 212 else 'o'
    if max(r, g, b) < 14:
        return 'K'
    if r > 150 and r - b > 40:
        return 'o'
    return '.'


def pixelize(path, unit):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    ys, xs = np.nonzero(orange_mask(a))
    if len(xs) == 0:
        return f'{path}: no Clawd found'
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    nx, ny = int(round((x1 - x0 + 1) / unit)), int(round((y1 - y0 + 1) / unit))
    rows = []
    for j in range(-1, ny + 1):
        row = ''
        for i in range(-1, nx + 1):
            cx, cy = int(x0 + (i + .5) * unit), int(y0 + (j + .5) * unit)
            row += cell(a[cy, cx]) if 0 <= cx < a.shape[1] and 0 <= cy < a.shape[0] else ' '
        rows.append(row)
    return f'--- {os.path.basename(path)} ({nx}x{ny} cells)\n' + '\n'.join(rows)


def engine_dump(pairs):
    import engine
    kw = {}
    for p in pairs:
        k, v = p.split('=', 1)
        kw[k] = int(v) if v.lstrip('-').isdigit() else (v == 'True' if v in ('True', 'False') else v)
    f = engine.Canvas()
    engine.clawd(f, **kw)
    inv = {v: k for k, v in engine.PAL.items()}
    x0, y0, x1, y1 = f.bbox()
    rows = [''.join(inv.get(f.px[y][x], '?') if f.px[y][x] else '.' for x in range(x0 - 1, x1 + 1))
            for y in range(y0, y1)]
    return f'--- engine {kw}\n' + '\n'.join(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('items', nargs='*')
    ap.add_argument('--unit', type=float, default=13.9)
    ap.add_argument('--engine', action='store_true', help='items are clawd() kwargs, e.g. view=qr tilt=1')
    a = ap.parse_args()
    if a.engine:
        print(engine_dump(a.items))
    else:
        for p in a.items:
            print(pixelize(p, a.unit))


if __name__ == '__main__':
    main()
