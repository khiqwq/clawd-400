"""Side-by-side review: your halftone render next to a reference room.

  python compare.py out.png --ref night_study [--out cmp.png]

--ref is a name in references/ref_maps (rendered through the same halftone) or a path to a 1080p
frame. Both are shown at half size, plus both value maps below, so tone range, detail density and
light logic can be judged together.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import halftone  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('render')
    ap.add_argument('--ref', default='night_study')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    mine = Image.open(a.render).convert('RGB')
    stem = a.render[:-4]
    mv = Image.open(stem + '_value.png').convert('L') if os.path.exists(stem + '_value.png') else None
    rp = os.path.join(HERE, '..', 'references', 'ref_maps', a.ref + '.png')
    if os.path.exists(rp):
        rv = Image.open(rp).convert('L')
        light = a.ref.startswith('day')
        ref = halftone.render(np.asarray(rv, np.float32) / 255, ground=243 if light else 19, ink=40 if light else 214, light=light)
    else:
        ref = Image.open(a.ref).convert('RGB')
        v, *_ = halftone.dehalftone(np.asarray(ref.convert('L'), np.float32))     # the frame's value map
        rv = Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8))
    W, H = 960, 540
    S = Image.new('RGB', (W * 2 + 10, H * 2 + 10), (70, 70, 70))
    S.paste(mine.resize((W, int(mine.height * W / mine.width))).crop((0, 0, W, H)), (0, 0))
    S.paste(ref.resize((W, H)), (W + 10, 0))
    for k, v in enumerate((mv, rv)):
        if v is not None:
            S.paste(v.resize((W, int(v.height * W / v.width)), Image.NEAREST).convert('RGB').crop((0, 0, W, H)), (k * (W + 10), H + 10))
    d = ImageDraw.Draw(S)
    d.text((6, 6), 'yours', fill=(255, 220, 0)); d.text((W + 16, 6), 'reference: ' + a.ref, fill=(255, 220, 0))
    out = a.out or stem + '_cmp.png'
    S.save(out)
    print(out)


if __name__ == '__main__':
    main()
