"""Hilltop at sunrise — the last scene of "末班车" (light theme), in three layers + a mask.

  hilltop_back   sky (paper), three far hill ranges (≤ .2, nearer = denser, one paper cell between
                 ranges, a slightly denser ridge row each), three clouds, a few far birds
  hilltop_sun    the sun alone: a cell-exact disc (.38) + 2-dot ray dashes (.3), centre (1500, 560)
  hilltop_front  the near hill: the path (Clawd's feet line, exact coordinates below) as a light band with
                 carved edges and stones, a grassy verge behind it with tufts, the slope denser toward
                 the viewer with paper flecks, the hilltop's right shoulder with a lone tree (cell-level
                 crown, lit caps toward the sun, shaded undersides, sky holes); opaque where the hill is
  hilltop_front_mask.png   white where the front layer is opaque (hill + tree + their one-cell air halo)

Feet line (path surface): (0,975) (400,960) (700,885) (950,765) (1150,675) → flat y 657 to x 1420.
The brief's (1150, 675) and "flat at 657 from 1150" meet with a 3-cell ease (1150,675)→(1177,657).
Calm: x 1150–1420 above the path holds only sky (the far ranges stay below the hilltop there).

Run: python hilltop.py   (writes everything next to this script)
"""
import asyncio
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

SKILL = os.path.join(os.path.expanduser('~'), '.rec', 'claude', 'accounts', '52928', 'config', 'skills', 'clawd-halftone')
SCRIPTS = os.path.join(SKILL, 'scripts')
REFS = os.path.join(SKILL, 'assets', 'refs')
sys.path.insert(0, SCRIPTS)
from svgkit import Svg, P  # noqa: E402
from cellkit import CellPaint, cell_mask, circle_mask, dilate, outline_mask, top_edge_mask, lump_shade  # noqa: E402
import halftone  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
ROWS, COLS = 120, 213
R_, C_ = np.mgrid[0:ROWS, 0:COLS]
XC = C_ * P + 4.5                                            # cell centres in px
YC = R_ * P + 4.5
rng = np.random.default_rng(31)


def C(x):
    return int(x // P)


def rect_mask(x0, y0, x1, y1):
    m = np.zeros((ROWS, COLS), bool)
    m[max(0, C(y0)):C(y1 - 1) + 1, max(0, C(x0)):C(x1 - 1) + 1] = True
    return m


def shift_mask(m, dc, dr):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dr):H + min(0, dr), max(0, dc):W + min(0, dc)] = m[max(0, -dr):H - max(0, dr), max(0, -dc):W - max(0, dc)]
    return out


def profile_rows(fn):
    """Row index of a profile y = fn(x) at every column (cell centres)."""
    return np.array([int(round(fn(9 * c + 4.5) / P)) for c in range(COLS)])


def below(rows_):
    """Mask of the cells at or below a per-column row profile."""
    return R_ >= rows_[None, :]


# ============================================================================= the feet line
PATH = [(0, 975), (400, 960), (700, 885), (950, 765), (1150, 675), (1177, 657), (1420, 657)]


def path_y(x):
    for (x0, y0), (x1, y1) in zip(PATH, PATH[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def ground_y(x):
    """The hill's surface: the path on the left, then the rounded top and the right shoulder."""
    if x <= 1420:
        return path_y(x)
    t = (x - 1420) / 500
    return 657 + 112 * t ** 1.7                               # (1420,657) → (1920,769), rounding down


# ============================================================================= layer 1: back
back = CellPaint()


def far_range(fn, body, ridge):
    rows_ = profile_rows(fn)
    m = below(rows_)
    back.put(dilate(m) & ~m & ~np.isnan(back.v), -1)          # one paper cell over the range behind
    back.put(m, body)
    back.put(top_edge_mask(m), ridge)
    return m


A = far_range(lambda x: 588 + 0.075 * x - 26 * math.sin(x / 210 + 1.0) - 12 * math.sin(x / 77), 0.07, 0.13)
B = far_range(lambda x: 702 + 0.05 * x - 30 * math.sin(x / 260 + 2.6) - 10 * math.sin(x / 61 + 1), 0.11, 0.17)
Cc = far_range(lambda x: 806 + 0.03 * x - 24 * math.sin(x / 190 + 0.3) - 9 * math.sin(x / 53 + 2), 0.15, 0.2)
# the far ranges get paper flecks too (like the ref's hills), sparse
back.put((rng.random((ROWS, COLS)) < 0.05) & A & ~top_edge_mask(A), -1)


def cloud(cx, base, w, lumps):
    """A cell-crisp cloud like r3_500: lumpy top the densest part, the base fading out to the lower
    left, a bit denser on the lower right."""
    m = np.zeros((ROWS, COLS), bool)
    for dx, dy, r in lumps:
        m |= circle_mask(cx + dx * w, base + dy * w, r * w)
    m &= YC <= base
    m |= cell_mask([[(cx - w * 0.5, base - w * 0.07), (cx + w * 0.5, base - w * 0.07), (cx + w * 0.53, base), (cx - w * 0.53, base)]])
    back.put(m, 0.2)
    back.put(m & (YC < base - w * 0.16), 0.38)
    lowl = (XC - cx) / w
    back.put(m & (YC >= base - w * 0.1) & (lowl < -0.08), 0.09)
    back.put(m & (YC >= base - w * 0.1) & (lowl > 0.14), 0.28)
    back.put(top_edge_mask(m), 0.46)


# clouds: big soft things — svgkit's soft cloud (bumpy top densest, base fading), as in r3_500
CLOUDS = ((414, 225, 400, 150), (1044, 144, 270, 100), (1800, 270, 200, 76))
# far birds: little "v"s of five cells
for bx, by in ((648, 378), (711, 351), (747, 396), (1260, 252), (1305, 279)):
    c, r = C(bx), C(by)
    for dc, dr in ((-2, 1), (-1, 0), (0, 1), (1, 0), (2, 1)):     # wing tips down, wings up, body down
        back.v[r + dr, c + dc] = 0.62

# ============================================================================= layer 2: the sun
SUNX, SUNY, SUNR = 1500, 560, 63
sun = CellPaint()
disc = circle_mask(SUNX, SUNY, SUNR)
sun.put(disc, 0.38)
for k in range(12):                                          # 2-dot ray dashes
    a = 2 * math.pi * k / 12 + math.pi / 12
    for rr in (SUNR + 27, SUNR + 36):
        x, y = SUNX + rr * math.cos(a), SUNY + rr * math.sin(a)
        sun.v[C(y), C(x)] = 0.3

# ============================================================================= layer 3: front (hill + tree)
front = CellPaint()
sr = profile_rows(lambda x: ground_y(x))                     # surface row (top of the path / ground)
xs_c = np.arange(COLS) * P + 4.5
on_path = xs_c <= 1438
verge = np.where(xs_c < 1100, 3, 2)                         # rows of grassy verge behind the path
hr = sr - verge                                              # hill silhouette row
hill = below(hr)
front.put(hill, 0.0)
# the body: denser toward the viewer, by depth below the surface (rows), paper flecks
depth = (R_ - sr[None, :]).astype(float)
body = hill & (depth >= 0)
span = np.maximum(1, ROWS - sr)[None, :]
front.v[body] = (0.3 + 0.36 * np.clip(depth / span, 0, 1) ** 0.8)[body]
front.put(body & (rng.random((ROWS, COLS)) < 0.06), -1)
# lighter lumps in the slope (soft tussocks, like the ref's speckled ground)
for _ in range(16):
    x = rng.uniform(40, 1900); yb = ground_y(min(max(x, 0), 1919))
    y = yb + rng.uniform(60, 1080 - yb + 20)
    m = circle_mask(x, y, rng.uniform(14, 24)) & body
    front.v[m] = np.maximum(0.12, front.v[m] - 0.18)
# the verge behind the path: grass, the ridge row on top a level denser
vg = hill & (depth < 0)
front.put(vg, 0.3)
front.put(top_edge_mask(hill), 0.5)
# the path: a light band 3 rows deep from the feet line, its top edge = the verge's bottom row (dense
# line right behind the feet), a carved row under it, then a dense front edge (kerb), stones
path = body & (depth >= 0) & (depth < 3) & on_path[None, :]
front.put(path, 0.07)
front.put(vg & (depth == -1) & on_path[None, :], 0.62)       # the line the feet stand on
front.put(body & (depth == 3) & on_path[None, :], -1)        # carved edge
front.put(body & (depth == 4) & on_path[None, :], 0.62)      # front edge of the path
# the path ends at the hilltop: round the end off into the verge
end = (C_ >= C(1420)) & (C_ <= C(1438))
front.put(path & end & (depth == 0), 0.3)
# stones in the path (1x1, 2x1) and a few bigger ones on its front edge (lit top-left cell)
for x in (153, 342, 531, 666, 819, 1008, 1287):
    c = C(x); r = sr[c] + 1
    front.v[r, c] = 0.62
    if x % 2:
        front.v[r, c + 1] = 0.45
for x in (252, 594, 900, 1098):
    c = C(x); r = sr[c] + 4
    front.v[r - 1:r + 1, c:c + 2] = 0.85
    front.v[r - 1, c] = 0.45


def tuft(x, base_row, h=3, v=0.62):
    """A grass tuft standing on a row: a centre blade h cells and two shorter side blades leaning out."""
    c = C(x)
    for k in range(h):
        front.v[base_row - 1 - k, c] = v
    for k in range(h - 1):
        front.v[base_row - 1 - k, c - 1 - (k >= 1)] = v
        front.v[base_row - 1 - k, c + 1 + (k >= 1)] = v


tuft_mask = np.zeros((ROWS, COLS), bool)
before = np.isnan(front.v).copy()
for x in (36, 117, 207, 288, 369, 459, 549, 621, 702, 783, 864, 945, 1035, 1107, 1494, 1593, 1845):
    if 1140 < x < 1430:
        continue
    c = C(x)
    tuft(x, hr[c], h=3 if (x // 9) % 3 else 2, v=0.62)
tuft_mask = before & ~np.isnan(front.v)
# tufts in the near slope (denser toward the viewer)
for x, y in ((90, 1062), (243, 1035), (414, 1053), (612, 1017), (765, 999), (990, 1044), (1206, 999),
             (1386, 1008), (1557, 954), (1710, 1026), (1860, 990), (1134, 900), (1269, 819), (1440, 864),
             (1647, 846), (1800, 891), (1017, 891), (1503, 747)):
    c, r = C(x), C(y)
    if r < sr[c] + 6:
        continue
    for k in range(2):
        front.v[r - k, c] = 0.85
    front.v[r, c - 1] = 0.85; front.v[r, c + 1] = 0.85
    front.v[r - 1, c - 2] = 0.85; front.v[r - 1, c + 2] = 0.85


# ----------------------------------------------------------------------------- the lone tree
def tree(lumps, trunk, branches, holes, body=0.6, lit=0.3, shade=0.92):
    """Cell-level crown (after the skill's park_day): lumps unioned, every lump a lit cap on its upper
    left (toward the sun), its lower right a hard step heavier, air where it overlaps lumps behind, sky
    holes; a trunk with a hard shade band and branches."""
    tx0, ty0, tx1, ty1 = trunk
    U = np.zeros((ROWS, COLS), bool)
    ms = [circle_mask(cx, cy, r) for cx, cy, r in lumps]
    for m in ms:
        U |= m
    tm = rect_mask(tx0, ty0, tx1, ty1)
    flare = cell_mask([[(tx0 - 18, ty1 + 9), (tx0, ty1 - 36), (tx1, ty1 - 36), (tx1 + 18, ty1 + 9)]])
    br = np.zeros_like(U)
    for pts in branches:
        from cellkit import polyline_mask
        br |= polyline_mask(pts, thick=2)
    whole = U | tm | flare | br
    front.put(dilate(whole) & ~whole & (R_ < hr[None, :]), -1)     # air against the sky (not into the hill)
    front.put(tm | flare, 0.55)
    front.put((tm | flare) & (XC > tx0 + (tx1 - tx0) * 0.55), 0.92)
    front.put(br & ~U, 0.85)
    front.put(U, body)
    for k, m in enumerate(ms):
        later = np.zeros_like(U)
        for m2 in ms[k + 1:]:
            later |= m2
        earlier = np.zeros_like(U)
        for m2 in ms[:k]:
            earlier |= m2
        vis = m & ~later
        cx, cy, r = lumps[k]
        _, _, sh = lump_shade(cx, cy, r, m, lit_t=0.5, shade_t=0.2)
        front.put(vis & (sh | ~shift_mask(m, -2, -2)), shade)
        front.put(vis & ~shift_mask(m, 2, 2), lit)
        ring = dilate(m) & ~m & earlier & ~later & (shift_mask(m, -1, -1) | shift_mask(m, 0, -1) | shift_mask(m, -1, 0))
        front.put(ring, -1)
    for hx, hy in holes:
        c, r = C(hx), C(hy)
        front.v[r:r + 2, c:c + 2] = -1
    return whole


TX = 1701
tree_m = tree(lumps=[(1672, 515, 54), (1764, 505, 58), (1706, 440, 66), (1730, 566, 50)],
              trunk=(TX - 18, 585, TX + 18, int(ground_y(TX)) + 9),
              branches=[[(TX, 639), (TX - 27, 603), (TX - 45, 585)], [(TX + 9, 630), (TX + 45, 594)]],
              holes=[(1701, 486), (1755, 531)])

# ============================================================================= render + composite


def emit(cp, name, extra=None):
    s = Svg(theme='light')
    cp.emit(s)
    if extra:
        extra(s)
    svg = s.save(os.path.join(OUT, name + '.svg'))
    out = os.path.join(OUT, name + '.png')
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'svg2dots.py'), svg, out, '--theme', 'light'], check=True)
    return np.asarray(Image.open(os.path.join(OUT, name + '_value.png')).convert('L'), np.float32) / 255


def main():
    vb = emit(back, 'hilltop_back', lambda s: [s.cloud(cx, cy, w, h, top=0.42, bottom=0.08) for cx, cy, w, h in CLOUDS])
    vs = emit(sun, 'hilltop_sun')
    vf = emit(front, 'hilltop_front')
    # mask: the hill (from its silhouette down), the tree, and their one-cell air halo
    opaque = hill | tree_m | dilate(tree_m) & ~hill | (dilate(hill) & ~hill) | tuft_mask
    opaque = np.pad(opaque, ((0, 0), (0, vb.shape[1] - COLS)), mode='edge')    # value maps carry the partial 214th column
    big = np.kron(opaque.astype(np.uint8), np.ones((P, P), np.uint8))[:1080, :1920] * 255
    Image.fromarray(big.astype(np.uint8)).save(os.path.join(OUT, 'hilltop_front_mask.png'))
    for tag, dy in (('', 0), ('_sun300', -29)):                       # -29 cells = -261 px → sun at y 299
        sv = np.zeros_like(vs)
        if dy:
            sv[:dy, :] = vs[-dy:, :]
        else:
            sv = vs
        v = np.where(opaque, vf, np.maximum(vb, sv))
        halftone.render(v, light=True).crop((0, 0, 1920, 1080)).save(os.path.join(OUT, f'hilltop_preview{tag}.png'))
    # the feet line drawn over a copy of the preview (for checking only)
    im = Image.open(os.path.join(OUT, 'hilltop_preview.png')).convert('RGB')
    d = ImageDraw.Draw(im)
    d.line([(x, y) for x, y in PATH], fill=(214, 60, 40), width=2)
    d.rectangle((1150, 300, 1420, 657), outline=(30, 120, 200), width=2)
    im.save(os.path.join(OUT, 'work_feetline.png'))
    v0 = np.where(opaque, vf, np.maximum(vb, vs))
    sky = (R_ < (hr - 1)[None, :]) & (C_ >= C(1150)) & (C_ < C(1420)) & (R_ >= C(300))
    v0 = v0[:, :COLS]
    print('calm (x 1150-1420, y 300 to the hill): max', float(v0[sky].max()), 'cells > .05:', int((v0[sky] > 0.05).sum()))


if __name__ == '__main__':
    main()
