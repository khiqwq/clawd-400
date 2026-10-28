"""Value-map painter for halftone backdrops.

A backdrop is a small grayscale painting on the halftone's cell grid (one cell = one dot = 9 px at
1080p, 213 x 120 cells per 1920 x 1080 screen). Values are 0..1 = dot size (0 = no dot, 1 = a full
outline dot). Paint flat tones like a flat-design illustration, then a light-and-shade pass, then
render through halftone.render(). Coordinates are cells (floats are rounded).

    from paint import Paint, T
    p = Paint(213, 120)
    p.rect(20, 40, 50, 30, T.MID, line=T.BRIGHT)        # a cabinet: mid fill, bright outline
    p.inset(24, 44, 18, 22, T.DIM)                       # a door panel
    p.glow(110, 60, 30, 0.35)                            # lamp light
    p.save('room')                                       # room_value.png (+ alpha) and room.png (halftone)
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import halftone  # noqa: E402

CELL = halftone.PITCH            # px per cell at 1080p
CLAWD_PX = 14                    # film px per Clawd pixel (videos: 13.9)


class T:
    """The tones the reference rooms use (value = dot size). Walls stay EMPTY (0)."""
    EMPTY = 0.0
    FAINT = 0.08      # far things, things in shadow, rain, a tree outside the window
    DIM = 0.18        # wall decor, back shelves, curtains in shade
    MID = 0.32        # furniture bodies, floor band
    LIGHT = 0.5       # lit faces, front furniture
    BRIGHT = 0.85     # outlines, frames, the key object
    MAX = 1.0         # highlights, light sources


def cells_of_px(px):
    return px / CELL


def cells_of_clawd(n):
    """Clawd pixels -> cells (16 Clawd px wide body = ~25 cells)."""
    return n * CLAWD_PX / CELL


class Paint:
    def __init__(self, w=213, h=120):
        self.w, self.h = int(w), int(h)
        self.v = np.zeros((self.h, self.w), np.float32)
        self.a = np.zeros((self.h, self.w), np.float32)     # coverage: 1 where something is painted

    # ------------------------------------------------------------------ masks
    def _mask(self, draw):
        m = Image.new('L', (self.w, self.h), 0)
        draw(ImageDraw.Draw(m))
        return np.asarray(m, np.float32) / 255.0

    def _put(self, mask, tone, op='set'):
        m = mask > 0.5
        if op == 'set':
            self.v[m] = tone
        elif op == 'max':
            self.v[m] = np.maximum(self.v[m], tone)
        elif op == 'mul':
            self.v[m] *= tone
        elif op == 'add':
            self.v[m] = np.clip(self.v[m] + tone, 0, 1)
        self.a[m] = 1.0
        return m

    @staticmethod
    def _box(x, y, w, h):
        return [round(x), round(y), round(x + w) - 1, round(y + h) - 1]

    # ------------------------------------------------------------------ shapes (flat tone + optional outline)
    def rect(self, x, y, w, h, tone, line=None, lw=1):
        self._put(self._mask(lambda d: d.rectangle(self._box(x, y, w, h), fill=255)), tone)
        if line is not None:
            self.box(x, y, w, h, line, lw)

    def box(self, x, y, w, h, tone, lw=1):
        self._put(self._mask(lambda d: d.rectangle(self._box(x, y, w, h), outline=255, width=lw)), tone)

    def rrect(self, x, y, w, h, r, tone, line=None, lw=1):
        b = self._box(x, y, w, h)
        self._put(self._mask(lambda d: d.rounded_rectangle(b, radius=r, fill=255)), tone)
        if line is not None:
            self._put(self._mask(lambda d: d.rounded_rectangle(b, radius=r, outline=255, width=lw)), line)

    def ellipse(self, x, y, w, h, tone, line=None, lw=1):
        b = self._box(x, y, w, h)
        self._put(self._mask(lambda d: d.ellipse(b, fill=255)), tone)
        if line is not None:
            self._put(self._mask(lambda d: d.ellipse(b, outline=255, width=lw)), line)

    def circle(self, cx, cy, r, tone, line=None, lw=1):
        self.ellipse(cx - r, cy - r, 2 * r, 2 * r, tone, line, lw)

    def poly(self, pts, tone, line=None, lw=1):
        pts = [(round(a), round(b)) for a, b in pts]
        self._put(self._mask(lambda d: d.polygon(pts, fill=255)), tone)
        if line is not None:
            self._put(self._mask(lambda d: d.line(pts + pts[:1], fill=255, width=lw)), line)

    def line(self, x0, y0, x1, y1, tone, width=1):
        self._put(self._mask(lambda d: d.line([round(x0), round(y0), round(x1), round(y1)], fill=255, width=width)), tone)

    def polyline(self, pts, tone, width=1):
        pts = [(round(a), round(b)) for a, b in pts]
        self._put(self._mask(lambda d: d.line(pts, fill=255, width=width, joint='curve')), tone)

    def arc(self, cx, cy, r, a0, a1, tone, width=1):
        b = [round(cx - r), round(cy - r), round(cx + r), round(cy + r)]
        self._put(self._mask(lambda d: d.arc(b, a0, a1, fill=255, width=width)), tone)

    def dot(self, x, y, tone):
        x, y = round(x), round(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.v[y, x] = tone; self.a[y, x] = 1

    def inset(self, x, y, w, h, tone, line=None):
        """A recessed panel (cabinet door, drawer, picture): its own flat tone, optional rim."""
        self.rect(x, y, w, h, tone, line)

    # ------------------------------------------------------------------ 2.5D: depth the videos' way
    def block(self, x, y, w, h, tone, d=4, side='r', side_k=0.55, top_k=1.35, line=None):
        """AVOID — the user rejected oblique faces (不要斜向). Kept only for old scripts.
        A box seen nearly straight on, with its side face and top face showing — the same pseudo-3D
        as Clawd's turned views: front face flat `tone`, side face one step darker (tone*side_k), top
        face one step lighter (tone*top_k). d = depth of the receding faces in cells (oblique, rising
        0.5 cell per cell). side='r' / 'l' picks which side shows (the side away from the viewer's
        centre, or away from the light)."""
        dy = d * 0.5
        if side == 'r':
            sp = [(x + w, y), (x + w + d, y - dy), (x + w + d, y + h - dy), (x + w, y + h)]
            tp = [(x, y), (x + d, y - dy), (x + w + d, y - dy), (x + w, y)]
        else:
            sp = [(x, y), (x - d, y - dy), (x - d, y + h - dy), (x, y + h)]
            tp = [(x, y), (x - d, y - dy), (x + w - d, y - dy), (x + w, y)]
        self.poly(sp, min(1.0, tone * side_k))
        self.poly(tp, min(1.0, tone * top_k))
        self.rect(x, y, w, h, tone, line=line)

    def over(self, other, fade=1.0, x=0, y=0):
        """Composite another Paint (a depth plane) on top: its painted cells replace ours, its tones
        scaled by `fade`. Paint far planes with fade .35-.6, mid .75-.9, near 1 — far things get
        smaller, fainter dots, which is how the videos show distance."""
        h, w = other.h, other.w
        x0, y0 = int(round(x)), int(round(y))
        ys, xs = max(0, y0), max(0, x0)
        ye, xe = min(self.h, y0 + h), min(self.w, x0 + w)
        if ye <= ys or xe <= xs:
            return
        sub_a = other.a[ys - y0:ye - y0, xs - x0:xe - x0] > 0.5
        sub_v = other.v[ys - y0:ye - y0, xs - x0:xe - x0] * fade
        region_v = self.v[ys:ye, xs:xe]
        region_a = self.a[ys:ye, xs:xe]
        region_v[sub_a] = sub_v[sub_a]
        region_a[sub_a] = 1

    def plane(self):
        """A blank Paint the same size, for painting one depth plane before `over`-ing it."""
        return Paint(self.w, self.h)

    def erase(self, x, y, w, h):
        """Cut a hole (window glass in a layer that sits over a landscape)."""
        m = self._mask(lambda d: d.rectangle(self._box(x, y, w, h), fill=255)) > 0.5
        self.v[m] = 0; self.a[m] = 0

    def erase_poly(self, pts):
        pts = [(round(a), round(b)) for a, b in pts]
        m = self._mask(lambda d: d.polygon(pts, fill=255)) > 0.5
        self.v[m] = 0; self.a[m] = 0

    # ------------------------------------------------------------------ tone fields (light and shade)
    def vgrad(self, x, y, w, h, t0, t1, ease=1.0):
        """Vertical gradient fill t0 (top) -> t1 (bottom)."""
        x0, y0, x1, y1 = self._box(x, y, w, h)
        for yy in range(max(0, y0), min(self.h, y1 + 1)):
            u = (yy - y0) / max(1, y1 - y0)
            self.v[yy, max(0, x0):min(self.w, x1 + 1)] = t0 + (t1 - t0) * u ** ease
            self.a[yy, max(0, x0):min(self.w, x1 + 1)] = 1

    def glow(self, cx, cy, r, gain, power=1.6, region=None, only_painted=False):
        """Additive light from a source: gain at the centre, 0 at radius r. region=(x,y,w,h) clips it
        (light inside a fireplace, a window); only_painted lights objects but leaves the empty wall."""
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        add = gain * np.clip(1 - d, 0, 1) ** power
        if region is not None:
            x0, y0, x1, y1 = self._box(*region)
            m = np.zeros_like(add); m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = 1; add *= m
        if only_painted:
            add *= self.a
        self.v = np.clip(self.v + add, 0, 1)
        self.a = np.maximum(self.a, (add > 0.03).astype(np.float32))

    def beam(self, pts, gain, fade_to=0.0):
        """A wedge of light (a window's light on the floor, a lamp cone): polygon pts, gain fading
        along the first->last edge direction to fade_to * gain."""
        m = self._mask(lambda d: d.polygon([(round(a), round(b)) for a, b in pts], fill=255)) > 0.5
        ys, xs = np.nonzero(m)
        if len(ys) == 0:
            return
        (ax, ay), (bx, by) = pts[0], pts[-1]
        L = max(1e-6, math.hypot(bx - ax, by - ay))
        u = np.clip(((xs - ax) * (bx - ax) + (ys - ay) * (by - ay)) / L ** 2, 0, 1)
        self.v[ys, xs] = np.clip(self.v[ys, xs] + gain * (1 - u * (1 - fade_to)), 0, 1)
        self.a[ys, xs] = 1

    def shade(self, x, y, w, h, k):
        """Multiply a region by k (< 1 = shadow): under furniture, the far side of an object."""
        x0, y0, x1, y1 = self._box(x, y, w, h)
        self.v[max(0, y0):y1 + 1, max(0, x0):x1 + 1] *= k

    def shade_poly(self, pts, k):
        m = self._mask(lambda d: d.polygon([(round(a), round(b)) for a, b in pts], fill=255)) > 0.5
        self.v[m] *= k

    def depth(self, k):
        """Dim the whole layer (atmospheric depth: farther = smaller dots)."""
        self.v *= k

    # ------------------------------------------------------------------ patterns
    def bricks(self, x, y, w, h, tone, mortar, bw=4, bh=2):
        self.rect(x, y, w, h, mortar)
        for r, yy in enumerate(range(round(y), round(y + h), bh + 1)):
            off = (bw + 1) // 2 if r % 2 else 0
            for xx in range(round(x) - off, round(x + w), bw + 1):
                x0, x1 = max(xx, round(x)), min(xx + bw, round(x + w))
                if x1 > x0:
                    self.rect(x0, yy, x1 - x0, min(bh, round(y + h) - yy), tone)

    def slats(self, x, y, w, h, tone, gap_tone, every=4, vertical=True):
        self.rect(x, y, w, h, gap_tone)
        if vertical:
            for xx in range(round(x), round(x + w), every):
                self.rect(xx, y, every - 1, h, tone)
        else:
            for yy in range(round(y), round(y + h), every):
                self.rect(x, yy, w, every - 1, tone)

    def books(self, x, y, w, h, seed=1, tones=(T.DIM, T.MID, T.LIGHT)):
        """A row of book spines standing on a shelf whose top is y + h."""
        r = np.random.default_rng(seed)
        xx = x
        while xx < x + w - 1:
            bw = int(r.integers(1, 3)); bh = int(r.integers(max(2, h - 3), h + 1))
            if r.random() < 0.15:          # a gap or a leaning book
                xx += 2; continue
            self.rect(xx, y + h - bh, bw, bh, tones[int(r.integers(0, len(tones)))])
            xx += bw + (1 if r.random() < 0.5 else 0)

    def leaves(self, cx, cy, n, size, tone, seed=1, spread=1.0, droop=0.0):
        """A plant: n leaves fanning out from (cx, cy) upward (droop > 0 bends them down)."""
        r = np.random.default_rng(seed)
        for k in range(n):
            ang = math.radians(-90 + (k - (n - 1) / 2) * 140 / max(1, n - 1) * spread + r.uniform(-8, 8))
            L = size * r.uniform(0.7, 1.1)
            tx, ty = cx + math.cos(ang) * L, cy + math.sin(ang) * L + droop * L * abs(math.cos(ang))
            mx, my = (cx + tx) / 2, (cy + ty) / 2
            nx, ny = -(ty - cy) / L, (tx - cx) / L
            wdt = L * 0.22
            self.poly([(cx, cy), (mx + nx * wdt, my + ny * wdt), (tx, ty), (mx - nx * wdt, my - ny * wdt)], tone)
            self.line(cx, cy, mx, my, max(0.0, tone - 0.12))

    def text(self, s, x, y, tone, size=12):
        """Bitmap text (SimSun 12 px renders CJK and Latin); each font px = one cell at size 12."""
        font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', size)
        m = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(m).text((round(x), round(y)), s, font=font, fill=255)
        self._put(np.asarray(m, np.float32) / 255 > 0.43, tone)

    # ------------------------------------------------------------------ output
    def value_image(self):
        """L+A image of the value map (what a film comp loads as a layer)."""
        v = (np.clip(self.v, 0, 1) * 255).astype(np.uint8)
        a = (np.clip(self.a, 0, 1) * 255).astype(np.uint8)
        return Image.merge('LA', (Image.fromarray(v), Image.fromarray(a)))

    def data_uri(self):
        """The value map as a data: URI, for an HTML comp opened from file:// (file:// images taint a canvas)."""
        import base64
        import io
        buf = io.BytesIO()
        self.value_image().save(buf, 'PNG')
        return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')

    def render(self, theme='dark'):
        return halftone.render(self.v, light=(theme == 'light'))

    def save(self, stem, theme='dark', preview=True):
        self.value_image().save(stem + '_value.png')
        if preview:
            self.render(theme).save(stem + '.png')
        return stem + '.png'
