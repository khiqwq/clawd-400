"""Cell-exact drawing for halftone backdrops (use with svgkit.Svg). All coordinates in px; cells are
9 x 9 from (0, 0).

The videos' silhouettes are stair-stepped with full dots right up to the edge: a shape is a set of
whole cells. svg2dots' averaging instead rims every curved edge of an SVG shape with small dots,
which is right only for big soft things (clouds, glows, ground). For objects, build a cell mask and
emit it as crisp runs:

    from svgkit import Svg
    from cellkit import cell_mask, cells, CellPaint, lump_shade, outline_mask, dilate, gap, ellipse_pts
    m = cell_mask([ellipse_pts(600, 400, 160, 120)])
    cp = CellPaint(); cp.put(m, .6)
    lit, body, shade = lump_shade(600, 400, 160, m); cp.put(lit, .3); cp.put(shade, .9)
    cp.put(outline_mask(m), .9); cp.emit(s)

Carving: inner detail in the videos is mostly *gaps* (no dots) cut into a filled object — `gap()` or
CellPaint value -1. Carve after any glow so the gaps stay dark inside the light.
These helpers came from the round-2 test (films/backdrops/iteration-2).
"""
import math

P = 9


def snap(v):
    return round(v / P) * P


def gap(s, x, y, w, h, rx=0):
    """Carve: a paper/ground rect (no dots) — the refs' main way of drawing inner detail."""
    s.rect(x, y, w, h, fill=s.paper, rx=rx)


def box(s, x0, y0, x1, y1, v, rx=0):
    """Filled rect by corners."""
    s.rect(x0, y0, x1 - x0, y1 - y0, fill=s.ink(v), rx=rx)


def checker(s, x0, y0, x1, y1, v, phase=0):
    """Every other cell lit: a mesh / net / grille that stays crisp on the screen."""
    for r, y in enumerate(range(y0, y1, P)):
        for c, x in enumerate(range(x0, x1, P)):
            if (r + c + phase) % 2 == 0:
                s.rect(x, y, P, P, fill=s.ink(v))


def dashes(s, y, segs, v):
    """One crisp row of dashes: segs = [(x0, x1), ...] (multiples of 9)."""
    for x0, x1 in segs:
        s.rect(x0, y, x1 - x0, P, fill=s.ink(v))


def star(s, x, y, v=0.45, arm=1, core=None):
    """A small cross-shaped star like v1_75_space: centre cell + arms of `arm` cells."""
    s.rect(x, y, P, P, fill=s.ink(core if core is not None else min(1, v + 0.2)))
    for k in range(1, arm + 1):
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            s.rect(x + dx * P, y + dy * P, P, P, fill=s.ink(v * (0.75 ** (k - 1))))


def profile(x0, x1, base, pts):
    """Closed polygon for a ridge/silhouette: pts = [(x, y), ...] along the top, closed down to base."""
    return [(x0, base)] + pts + [(x1, base)]


def cell_mask(polys, w=1920, h=1080):
    """Cells (rows x cols bool) whose centre lies inside any of the polygons (px coordinates)."""
    import numpy as np
    from PIL import Image, ImageDraw
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    for pts in polys:
        d.polygon([(float(x), float(y)) for x, y in pts], fill=255)
    a = np.asarray(im)
    return a[4::P, 4::P] > 127


def cells(s, mask, v, x_off=0, y_off=0):
    """Emit a cell mask as crisp rect runs (one rect per horizontal run): stair-stepped edges with full
    dots up to the edge, like the refs' silhouettes (svg2dots' averaging otherwise rims every curved
    edge with a row of small dots)."""
    rows, cols = mask.shape
    for r in range(rows):
        c = 0
        while c < cols:
            if mask[r, c]:
                c0 = c
                while c < cols and mask[r, c]:
                    c += 1
                s.rect(x_off + c0 * P, y_off + r * P, (c - c0) * P, P, fill=s.ink(v) if not isinstance(v, str) else v)
            else:
                c += 1


def cell_poly(s, pts, v):
    """A polygon filled cell-exact (see cells())."""
    cells(s, cell_mask([pts]), v)


def bez(p0, p1, p2, p3, n=16):
    """Points along a cubic Bezier (for building polygons that go through cell_mask)."""
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def ellipse_pts(cx, cy, rx, ry, n=48, a0=0, a1=360):
    return [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
            for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]


def polyline_mask(pts, w=1920, h=1080, thick=1):
    """Cells a polyline passes through: a one-cell crisp line along any curve (thick = cells across)."""
    import numpy as np
    m = np.zeros((len(range(4, h, P)), len(range(4, w, P))), bool)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) / 3) + 1
        for i in range(n + 1):
            x, y = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
            c, r = int(x // P), int(y // P)
            for dc in range(thick):
                if 0 <= r < m.shape[0] and 0 <= c + dc < m.shape[1]:
                    m[r, c + dc] = True
    return m


def outline_mask(mask):
    """The cells of a mask that touch its outside (4-neighbourhood): a one-cell crisp contour."""
    import numpy as np
    m = mask
    pad = np.pad(m, 1)
    inner = pad[1:-1, 1:-1] & pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    return m & ~inner


def top_edge_mask(mask):
    """The topmost cell of every column of a mask (a crisp ridge line for hills, crowns...)."""
    import numpy as np
    out = np.zeros_like(mask)
    pad = np.pad(mask, ((1, 0), (0, 0)))
    out |= mask & ~pad[:-1, :]
    return out


def hshade(s, x0, x1, lit_left=True, band=0.3, a=0.6, b=0.3):
    """Horizontal hard-step gradient url (lit tone a, shade tone b) across x0..x1."""
    w = x1 - x0
    o = (1 - band) if lit_left else band
    st = [(0, a), (o, a), (o, b), (1, b)] if lit_left else [(0, b), (o, b), (o, a), (1, a)]
    return s.lgrad(x0, 0, x1, 0, st)


def vshade(s, y0, y1, top=0.6, bottom=0.3, at=0.5):
    """Vertical hard-step gradient url (top tone above `at`, bottom tone below)."""
    return s.lgrad(0, y0, 0, y1, [(0, top), (at, top), (at, bottom), (1, bottom)])


def circle_mask(cx, cy, r, w=1920, h=1080):
    """Cells whose centre is within r of (cx, cy)."""
    import numpy as np
    ys = np.arange(4, h, P)[:, None] + 0.5
    xs = np.arange(4, w, P)[None, :] + 0.5
    return (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r


def dilate(mask, n=1):
    """Grow a cell mask by n cells (4-neighbourhood steps)."""
    import numpy as np
    m = mask.copy()
    for _ in range(n):
        p = np.pad(m, 1)
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


class CellPaint:
    """A cell-level layer on top of the SVG: put values into masks (later puts win), then emit() as crisp
    rect runs. -1 = paper (carved). For things whose structure lives on the cell grid (tree crowns,
    shaded lumps) — the refs' stair-stepped look with exact control of every cell."""

    def __init__(self, rows=120, cols=213):
        import numpy as np
        self.v = np.full((rows, cols), np.nan)

    def put(self, mask, v):
        self.v[mask] = v

    def emit(self, s):
        import numpy as np
        vals = np.unique(self.v[~np.isnan(self.v)])
        for val in vals:
            m = self.v == val
            cells(s, m, s.paper if val < 0 else float(val))


def lump_shade(cx, cy, r, mask, lit_dir=(-0.7, -0.7), lit_t=0.42, shade_t=0.3):
    """Split a round lump's cells into (lit, body, shade) masks by their offset along the light direction:
    hard steps, the videos' way of shading rounded things."""
    import numpy as np
    ys = np.arange(4, 1080, P)[:, None] + 0.5
    xs = np.arange(4, 1920, P)[None, :] + 0.5
    d = ((xs - cx) * lit_dir[0] + (ys - cy) * lit_dir[1]) / r
    lit = mask & (d > lit_t)
    shade = mask & (d < -shade_t)
    return lit, mask & ~lit & ~shade, shade
