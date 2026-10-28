"""Cell-exact plant / pot helpers for the day scenes (on canvas.Canvas). Light from the upper left."""
import math

import numpy as np

from canvas import R, rrect, poly, line, edge, grow, shrink, shift, right_of, below, ck, P, XS, YS


def leaf_pts(x, y, angle, length, width, curl=0.1):
    """svgkit.leaf's outline as points: (left half, right half, midrib) from the base (x, y) toward
    `angle` (0 = up, + = clockwise)."""
    a = math.radians(angle)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux
    bend = curl * length

    def Pt(t, sd):
        bx = x + ux * length * t + nx * bend * t * t
        by = y + uy * length * t + ny * bend * t * t
        return bx + nx * sd, by + ny * sd
    W = width / 2
    ts = [i / 24 for i in range(25)]
    prof = [W * math.sin(math.pi * min(1, t * 1.04) ** 1.15) ** 0.8 for t in ts]
    Lp = [Pt(t, -p) for t, p in zip(ts, prof)]
    Rp = [Pt(t, p) for t, p in zip(ts, prof)]
    mid = [Pt(t, 0) for t in ts]
    return Lp, Rp, mid, (nx, ny)


def leaf(c, x, y, angle, length, width, dark=.95, lit=.62, curl=0.1, stem=0, stem_v=.9, air=1, midrib=True,
         notches=0):
    """A leaf on cells: the half facing the light (upper left) `lit`, the other `dark`, a carved midrib,
    optional carved notches (monstera slits), an optional stem (one-cell line) before the blade, `air`
    cells of paper cut around it. Returns the leaf mask."""
    if stem:
        a = math.radians(angle)
        x2, y2 = x + math.sin(a) * stem, y - math.cos(a) * stem
        sm = line([(x, y), (x2, y2)])
        c.cut(sm, air)
        c.put(sm, stem_v)
        x, y = x2, y2
    Lp, Rp, mid, (nx, ny) = leaf_pts(x, y, angle, length, width, curl)
    m = poly(Lp + Rp[::-1])
    left = poly(mid + Lp[::-1]) & m
    c.cut(m, air)
    c.put(m, dark)
    # which half faces the upper left light: the side whose normal points up-left
    lit_half = left if (-nx - ny) > 0 else m & ~left
    c.put(lit_half, lit)
    if midrib:
        c.carve(line(mid[2:-3]) & m)
    for k in range(notches):
        t = 0.25 + 0.5 * k / max(1, notches - 1)
        i = int(t * 24)
        for side in (Lp, Rp):
            px, py = side[i]
            mx, my = mid[min(24, i + 2)]
            c.carve(line([(px, py), (px + (mx - px) * 0.6, py + (my - py) * 0.6)]) & m)
    return m


def pot(c, cx, base, w, h, body=.2, rim=.3, shade=.42, rim_shade=.52, edge_v=.65, rim_h=None):
    """Flower pot like r3_390: a rim band and a tapering body with rounded bottom corners, a one-cell
    outline, a hard shade band (~28 %) on the right. cx, w, base, h in px (multiples of 9)."""
    rim_h = rim_h or max(27, round(h * 0.26 / P) * P)
    x0, x1 = cx - w / 2, cx + w / 2
    t = max(9, round(w * 0.08 / P) * P)
    rim_m = rrect(x0, base - h, x1, base - h + rim_h, 6)
    body_m = poly([(x0 + 9, base - h + rim_h), (x1 - 9, base - h + rim_h), (x1 - 9 - t, base - 9), (x1 - 9 - t - 18, base),
                   (x0 + 9 + t + 18, base), (x0 + 9 + t, base - 9)])
    whole = rim_m | body_m
    c.cut(whole)
    xs = x1 - w * 0.28
    c.put(body_m, body)
    c.put(body_m & right_of(xs), shade)
    c.put(edge(body_m), edge_v)
    c.put(rim_m, rim)
    c.put(rim_m & right_of(xs), rim_shade)
    c.put(edge(rim_m), edge_v)
    return whole
