"""Halftone study + renderer for the reference videos' backdrops.

The reference rooms are a grayscale painting seen through a fixed halftone screen: one dot per
9 x 9 px cell, dot size AND brightness growing with the painting's value. This module goes both ways:

  python halftone.py dehalf ref.png out.png [--scale 4]   # recover the value map (213 x 120 cells), enlarged
  python halftone.py fit ref1.png ref2.png ...            # measure dot area / brightness against value
  python halftone.py round ref.png out.png                # dehalftone + re-render, side by side with the original
"""
import sys

import numpy as np
from PIL import Image

PITCH = 9


def to_gray(path):
    return np.asarray(Image.open(path).convert('L')).astype(np.float32)


def ground_of(a):
    return float(np.median(a))


def phase(a, light=False):
    """Grid offset (ox, oy) of the dot centres: the offset whose samples deviate most from the ground."""
    g = ground_of(a)
    best = None
    for oy in range(PITCH):
        for ox in range(PITCH):
            s = np.abs(a[oy::PITCH, ox::PITCH] - g).mean()
            if best is None or s > best[0]:
                best = (s, ox, oy)
    return best[1], best[2]


def cells(a):
    """Per-cell ink energy: sum over the 9x9 cell (centred on the dot) of |pixel - ground|."""
    g = ground_of(a)
    ox, oy = phase(a)
    x0, y0 = ox - 4, oy - 4
    H, W = a.shape
    rows, cols = (H - y0) // PITCH, (W - x0) // PITCH
    d = np.abs(a - g)
    out = np.zeros((rows, cols), np.float32)
    peak = np.zeros((rows, cols), np.float32)
    area = np.zeros((rows, cols), np.float32)
    for r in range(rows):
        for c in range(cols):
            ys, xs = y0 + r * PITCH, x0 + c * PITCH
            if ys < 0 or xs < 0:
                continue
            blk = d[ys:ys + PITCH, xs:xs + PITCH]
            out[r, c] = blk.sum()
            peak[r, c] = blk.max()
            area[r, c] = (blk > 24).sum()
    return out, peak, area, (x0, y0)


def dehalftone(a, full=None):
    """Value map. Cells with a solid fill (Clawd, UI, text) are not dots: they are zeroed, and the scale
    is set by the brightest dot-like cells (outline dots read as ~0.9-1)."""
    e, peak, area, origin = cells(a)
    dot = (area <= 30) & (e > 0)
    full = full or np.percentile(e[dot], 99.7)
    v = np.clip(e / full, 0, 1)
    v[~dot] = 0
    return v, peak, area, origin


def fit(paths):
    vs, pk, ar = [], [], []
    for p in paths:
        a = to_gray(p)
        v, peak, area, _ = dehalftone(a)
        m = v > 0.01
        vs.append(v[m]); pk.append(peak[m]); ar.append(area[m])
    v, peak, area = np.concatenate(vs), np.concatenate(pk), np.concatenate(ar)
    print(' value  n      peak(med)  area(med px)')
    for lo in np.arange(0, 1.0, 0.1):
        m = (v >= lo) & (v < lo + 0.1)
        if m.sum():
            print(f' {lo:.1f}   {m.sum():6d}  {np.median(peak[m]):6.0f}     {np.median(area[m]):5.1f}')


# ----------------------------------------------------------------------------- renderer
# Dot look measured from the references (see fit): a square-ish dot whose side and brightness grow with v.
DOT_D = 4.7      # px, diameter of a full dot (v = 1)


def dot_sprite(v, sub=8):
    """9x9 coverage sprite for value v in 0..1: an antialiased ROUND dot centred in its cell whose AREA
    is proportional to v: diameter = 4.7 * sqrt(v) px. Measured on the day video at 1:1: floor dots
    ~2.0 px (v .18), panels 2.2-2.5 (.23-.28), sun 2.9 (.38), the densest foliage and a chair seat
    4.5-4.6 (.92-.96). All dots the same colour; the size carries the tone."""
    r = DOT_D / 2 * np.sqrt(max(0.0, v))
    n = PITCH * sub
    yy, xx = np.mgrid[0:n, 0:n]
    c = 4.5 * sub - 0.5
    inside = ((xx - c) ** 2 + (yy - c) ** 2) <= (r * sub) ** 2
    return inside.reshape(PITCH, sub, PITCH, sub).mean(axis=(1, 3)).astype(np.float32)


LUT = [dot_sprite(i / 63) for i in range(64)]
LUT_ARR = np.stack(LUT)
LUT_ARR[0] = 0


DARK = ((19, 19, 19), (221, 217, 215))          # night videos: ground, dot colour (measured)
LIGHT = ((244, 242, 236), (12, 10, 5))           # day video: cream paper, near-black ink (measured)


def render(v, ground=19, ink=214, light=False, colors=None):
    """Value map (rows x cols, 0..1) -> RGB halftone image (cols*9 x rows*9), round dots.
    colors=(ground_rgb, ink_rgb) overrides; by default the measured DARK / LIGHT palettes."""
    rows, cols = v.shape
    q = np.clip((np.asarray(v, np.float32) * 63).round().astype(int), 0, 63)
    q[np.asarray(v) <= 0.02] = 0
    cov = LUT_ARR[q].transpose(0, 2, 1, 3).reshape(rows * PITCH, cols * PITCH)      # vectorised: one sprite per cell
    g, i = colors or (LIGHT if light else DARK)
    g, i = np.array(g, np.float32), np.array(i, np.float32)
    img = g[None, None, :] * (1 - cov[..., None]) + i[None, None, :] * cov[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')


def main():
    cmd = sys.argv[1]
    if cmd == 'dehalf':
        a = to_gray(sys.argv[2])
        v, *_ = dehalftone(a)
        k = int(sys.argv[sys.argv.index('--scale') + 1]) if '--scale' in sys.argv else 4
        Image.fromarray((v * 255).astype(np.uint8)).resize((v.shape[1] * k, v.shape[0] * k), Image.NEAREST).save(sys.argv[3])
    elif cmd == 'fit':
        fit(sys.argv[2:])
    elif cmd == 'round':
        a = to_gray(sys.argv[2])
        v, *_ = dehalftone(a)
        light = ground_of(a) > 128
        r = render(v, ground=ground_of(a), ink=(214 if not light else 40), light=light)
        o = Image.open(sys.argv[2]).convert('RGB')
        sbs = Image.new('RGB', (o.width, o.height // 2))
        sbs.paste(o.crop((0, 300, o.width // 2, 300 + o.height // 2)), (0, 0))
        sbs.paste(r.crop((0, 300, o.width // 2, 300 + o.height // 2)), (o.width // 2, 0))
        sbs.save(sys.argv[3])


if __name__ == '__main__':
    main()
