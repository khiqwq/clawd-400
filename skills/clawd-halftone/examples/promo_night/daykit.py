"""Day-theme helpers shared by the four promo backdrops (built on the skill's svgkit + cellkit).

All coordinates in screen px, multiples of 9 (cells 9 x 9 from (0, 0)). Values are dot values
(0 = paper, 1 = the biggest ink dot).
"""
import math

import numpy as np

from svgkit import P
from cellkit import (gap, box, cell_mask, cells, CellPaint, outline_mask, dilate, circle_mask,
                     ellipse_pts, polyline_mask, lump_shade, top_edge_mask)

ROWS, COLS = 120, 213
YS = np.arange(4, 1080, P)[:, None] + 0.5
XS = np.arange(4, 1920, P)[None, :] + 0.5


def C(x):
    """px -> cell index."""
    return int(x // P)


def rect_mask(x0, y0, x1, y1):
    m = np.zeros((ROWS, COLS), bool)
    m[C(y0):C(y1 - 1) + 1, C(x0):C(x1 - 1) + 1] = True
    return m


def shift_mask(m, dc, dr):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dr):H + min(0, dr), max(0, dc):W + min(0, dc)] = m[max(0, -dr):H - max(0, dr), max(0, -dc):W - max(0, dc)]
    return out


def floor(s, y=981, v=0.18, skirting=0.42):
    """The day floor band (full width, .18) with a one-row skirting line on top."""
    s.row(0, 1920, y, v, rows=(1080 - y) // P + 1)
    if skirting:
        s.row(0, 1920, y - 9, skirting)


def soft(s, x0, y0, x1, y1, v, edge=0.62, rx=27):
    """A cushion / soft panel: light field + one-cell outline."""
    s.rect(x0, y0, x1 - x0, y1 - y0, fill=s.ink(v), rx=rx)
    s.rect(x0 + 4.5, y0 + 4.5, x1 - x0 - 9, y1 - y0 - 9, stroke=s.ink(edge), sw=9, rx=max(0, rx - 4.5))


def books(s, x0, base, specs):
    """Books standing on a shelf: specs = [(width_cells, height_px, tone, lean_px), ...], 1-cell gaps.
    Thicker books get a carved spine band near the top (and the bottom when tall)."""
    x = x0
    for wc, h, v, lean in specs:
        w = wc * P
        if lean:
            cells(s, cell_mask([[(x, base), (x + w, base), (x + w + lean, base - h), (x + lean, base - h)]]), v)
        else:
            box(s, x, base - h, x + w, base, v)
            if wc >= 3 and v >= 0.3:
                gap(s, x + 9, base - h + 18, w - 18, 9)
                if h > 100:
                    gap(s, x + 9, base - 36, w - 18, 9)
        x += w + P
    return x


def curtain(s, xo, xi, top, bottom, tie_y, body=0.26, shade=0.5, pleat=4, gather=0.45, flare=0.8,
            tie_v=0.85, light_left=True, tassel=True):
    """A curtain hanging from a rod, tied back: xo = the outer (wall) edge, xi = the inner edge at the
    top (xi > xo: curtain on the left of its window; xi < xo: on the right). Pleats of `pleat` cells:
    lit cells at `body`, the one away from the light a hard step heavier (`shade`), a one-cell fold gap
    after each pleat; the curtain narrows to `gather` of its width at the tie and flares back to `flare`
    at the hem. The folds follow the narrowing (short staircases only around the tie)."""
    W = abs(xi - xo)
    sign = 1 if xi > xo else -1
    cp = CellPaint()
    r0, r1 = C(top), C(bottom - 1)
    rt = C(tie_y)
    span_up = max(1, rt - r0)
    for r in range(r0, r1 + 1):
        if r <= rt:
            t = (r - r0) / span_up
            k = 1 - (1 - gather) * (max(0.0, (t - 0.45) / 0.55)) ** 1.6
        else:
            t = (r - rt) / max(1, r1 - rt)
            k = gather + (flare - gather) * min(1.0, t * 1.25) ** 0.8
        w = max(3 * P, W * k)
        a, b = (xo, xo + w) if sign > 0 else (xo - w, xo)
        c0, c1 = C(a + 4), C(b - 4)
        n = c1 - c0 + 1
        for j in range(n):
            # position across the curtain measured from the outer edge, scaled by the row's width
            u = (j if sign > 0 else n - 1 - j) / n * (W / P)
            q = int(u) % pleat
            right_cell = (q == pleat - 2) if sign > 0 else (q == 0)    # the pleat's rightmost cell
            left_cell = (q == 0) if sign > 0 else (q == pleat - 2)
            if q == pleat - 1:
                val = -1                                    # fold gap
            elif (right_cell if light_left else left_cell):
                val = shade                                 # the side of the pleat away from the light
            else:
                val = body
            cp.v[r, c0 + j] = val
    cp.emit(s)
    # tie-back band + tassel
    tw = W * gather
    a, b = (xo - 9, xo + tw + 9) if sign > 0 else (xo - tw - 9, xo + 9)
    box(s, int(a // P) * P, tie_y - 9, int(b // P + 1) * P, tie_y + 9, tie_v)
    if tassel:
        tx = int((b - 18) // P) * P if sign > 0 else int((a + 9) // P) * P
        box(s, tx, tie_y + 9, tx + 9, tie_y + 27, tie_v)
        box(s, tx - 9, tie_y + 27, tx + 18, tie_y + 54, tie_v)
        gap(s, tx, tie_y + 45, 9, 9)


def rod(s, x0, x1, y, v=0.62, finial=0.9):
    """A curtain rod: one crisp row with a dense ball finial at each end and two brackets."""
    s.row(x0, x1, y, v)
    for fx in (x0 - 18, x1):
        box(s, fx, y - 9, fx + 18, y + 18, finial)


def rug(s, x0, x1, y0, border=0.85, field=0.42, motif=0.92, fringe=0.42, step=72):
    """A kilim on the floor band, 9 rows from y0: a dense border row top and bottom, a carved row inside
    each, a lighter field with dense lozenges (3-row diamonds), fringes at both ends; one cell of air
    round it on the floor band."""
    y1 = y0 + 81
    gap(s, x0 - 36, y0 - 9, x1 - x0 + 72, y1 - y0 + 18)
    box(s, x0, y0, x1, y0 + 9, border); box(s, x0, y1 - 9, x1, y1, border)
    box(s, x0, y0 + 18, x1, y1 - 18, field)
    s.col(x0, y0, y1, border); s.col(x1 - 9, y0, y1, border)
    mid = y0 + 36
    for x in range((x0 + (x1 - x0) % step // 2 // P * P) + step // 2 // P * P, x1 - 27, step):
        box(s, x, mid - 9, x + 9, mid, motif); box(s, x - 9, mid, x + 18, mid + 9, motif); box(s, x, mid + 9, x + 9, mid + 18, motif)
        gap(s, x - 36, mid, 9, 9); gap(s, x + 36, mid, 9, 9)
    for y in range(y0, y1, 18):
        s.row(x0 - 27, x0, y, fringe); s.row(x1, x1 + 27, y, fringe)


def clock(s, cx, cy, r, ring=0.85, face=0.0, tick=0.62, hand=0.9, h_ang=300, m_ang=60):
    """A round wall clock, cell exact: a one-cell rim (outline of a disc), paper face, four hour
    ticks, two hands (1 cell thick: hour short, minute long), a dense centre cell."""
    disc = circle_mask(cx, cy, r)
    cells(s, disc & dilate(~disc, 2), ring)                 # a 2-cell rim
    inner = disc & ~dilate(~disc, 2)
    if face:
        cells(s, inner, face)
    for a in (0, 90, 180, 270):
        x = cx + (r - 30) * math.sin(math.radians(a)); y = cy - (r - 30) * math.cos(math.radians(a))
        box(s, C(x) * P, C(y) * P, C(x) * P + 9, C(y) * P + 9, tick)
    for ang, ln in ((h_ang, r * 0.42), (m_ang, r * 0.62)):
        pts = [(cx, cy), (cx + ln * math.sin(math.radians(ang)), cy - ln * math.cos(math.radians(ang)))]
        cells(s, polyline_mask(pts), hand)
    box(s, C(cx) * P, C(cy) * P, C(cx) * P + 9, C(cy) * P + 9, 1.0)


def frame_pic(s, x0, y0, x1, y1, v=0.85, mat=27, nail=True):
    """A picture frame: dense one-cell frame, a paper mat, the picture's own edge line. Returns the
    picture's inner box (for clipping its content)."""
    s.frame(x0, y0, x1, y1, v)
    s.frame(x0 + mat, y0 + mat, x1 - mat, y1 - mat, 0.42)
    if nail:
        mx = (x0 + x1) // 2 // P * P
        box(s, mx, y0 - 63, mx + 9, y0 - 54, 0.9)
        cells(s, polyline_mask([(mx + 4, y0 - 54), (x0 + 40, y0 - 4)]) | polyline_mask([(mx + 4, y0 - 54), (x1 - 40, y0 - 4)]), 0.42)
    return x0 + mat + 9, y0 + mat + 9, x1 - mat - 9, y1 - mat - 9


def flakes(s, rng, n, box_, v=(0.3, 0.6), avoid=None, size=1):
    """Sparse falling flakes / dust as single cells (or 2 x 2 for near ones), never inside `avoid`."""
    x0, y0, x1, y1 = box_
    out = []
    tries = 0
    while len(out) < n and tries < n * 50:
        tries += 1
        x = int(rng.integers(x0 // P, x1 // P)) * P
        y = int(rng.integers(y0 // P, y1 // P)) * P
        if avoid and any(a[0] - 18 <= x <= a[2] + 9 and a[1] - 18 <= y <= a[3] + 9 for a in avoid):
            continue
        if any(abs(x - ox) < 54 and abs(y - oy) < 54 for ox, oy in out):
            continue
        out.append((x, y))
        vv = float(rng.uniform(*v))
        box(s, x, y, x + size * P, y + size * P, vv)
    return out


def rrect_pts(x0, y0, x1, y1, r, n=8):
    """Polygon of a rounded rectangle (for cell_mask)."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def lit_rim(m, k=2, dc=1, dr=1):
    """Cells of a mask within k cells of its upper-left edge (light from the upper left): a hard-step
    lit cap like the videos' rounded things."""
    return m & ~shift_mask(m, dc * k, dr * k)


def put_parts(cp, parts, v, lit_v=None, k=2, air=True, light='left'):
    """Paint parts back to front into a CellPaint: each part gets one cell of air (paper) around it
    over the parts behind, its body at v and (optionally) a lit rim at lit_v on the side of the light
    ('left' = upper left, 'right' = upper right)."""
    for m in parts:
        if air:
            ring = dilate(m) & ~m & ~np.isnan(cp.v)
            cp.put(ring, -1)
        cp.put(m, v)
        if lit_v is not None:
            cp.put(lit_rim(m, k, dc=1 if light == 'left' else -1), lit_v)


def leaf_masks(x, y, angle, length, width, curl=0.12, stem=0, light_left=True):
    """Cell-exact leaf (same geometry as svgkit.leaf): returns (lit, dark, stem_pts). The blade splits
    at the midrib into the half facing the light and the half away from it — whole cells, crisp edges
    like the patio ref's leaves."""
    a = math.radians(angle)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux
    stem_pts = None
    if stem:
        stem_pts = [(x, y), (x + ux * stem, y + uy * stem)]
        x, y = x + ux * stem, y + uy * stem
    bend = curl * length

    def Pt(t, sd):
        bx = x + ux * length * t + nx * bend * t * t
        by = y + uy * length * t + ny * bend * t * t
        return bx + nx * sd, by + ny * sd
    W = width / 2
    ts = [i / 20 for i in range(21)]
    prof = [W * math.sin(math.pi * min(1, t * 1.04) ** 1.15) ** 0.8 for t in ts]
    Lp = [Pt(t, -p) for t, p in zip(ts, prof)]
    Rp = [Pt(t, p) for t, p in zip(ts, prof)]
    mid = [Pt(t, 0) for t in ts]
    mL = cell_mask([mid + Lp[::-1]])
    mR = cell_mask([mid + Rp[::-1]])
    whole = cell_mask([Lp + Rp[::-1]]) | mL | mR
    left_is_lit = (nx > 0) != light_left
    lit = mL if left_is_lit else mR
    dark = whole & ~lit
    return lit, dark, stem_pts


def plant(cp, leaves, lit=0.62, dark=0.95, stem_v=0.85, air=True):
    """Paint cell-exact leaves back to front into a CellPaint: one cell of air round each leaf over the
    leaves behind it. leaves = [(x, y, angle, length, width, curl, stem), ...]."""
    for (x, y, ang, ln, wd, cv, st) in leaves:
        lm, dm, sp = leaf_masks(x, y, ang, ln, wd, curl=cv, stem=st)
        m = lm | dm
        if sp:
            sm = polyline_mask(sp) & ~m
            cp.put(sm, stem_v)
        if air:
            cp.put(dilate(m) & ~m & ~np.isnan(cp.v), -1)
        cp.put(lm, lit)
        cp.put(dm, dark)
