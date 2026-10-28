"""Helpers for drawing halftone backdrops as SVG (then svg2dots.py).

Everything is in screen px of a 1920 x 1080 frame. The screen's cells are 9 x 9 px starting at (0, 0):
cell edges are multiples of 9. Rules the helpers follow (references/style.md §1–3):
  - a crisp row / column of dots = a shape covering whole cells (y = 9k .. 9k+9) → row(), col(), frame();
    a 9-px stroke centred on a cell edge gives two rows of half-size dots;
  - only ~5 tones survive the screen: L.EMPTY 0, L.FAINT .1, L.MID .3, L.DENSE .6, L.FULL 1 (+ .2/.45 in
    between at most); differences under ~.2 vanish;
  - details and gaps must be >= 1 cell (9 px); lines >= 6 px; objects >= 5 cells;
  - near over far reads only with a 1-cell margin of ground/paper around the near shape → cut();
  - lights are blended (screen at night, multiply for day shadows) and need dark surroundings → glow();
  - rounded things shade as a HARD step (a ~30 % band one level heavier), not a smooth ramp → cyl(), pot().
Theme greys: ink(v) gives the grey for dot value v (dark theme: white = biggest dot; light: black).

    from svgkit import Svg, L
    s = Svg(theme='light')
    s.frame(819, 756, 1242, 972, L.DENSE, fill=.25)          # a cabinet, outline row + panel tone
    s.pot(1700, 972, 198, 180)
    s.leaf(1700, 800, -20, 380, 120)
    s.save('scene.svg')

Grid helpers and several object helpers came from the iteration-1 test (films/backdrops).
"""
import contextlib
import math

import numpy as np

P = 9                                   # px per cell


class L:
    """The tones that survive the screen (dot value)."""
    EMPTY, FAINT, LOW, MID, HIGH, DENSE, FULL = 0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 1.0


def snap(v):
    """Snap px to the cell grid."""
    return round(v / P) * P


class Svg:
    def __init__(self, w=1920, h=1080, theme='dark'):
        self.w, self.h, self.theme = w, h, theme
        self.parts, self.defs = [], []
        self._id = 0

    # ------------------------------------------------------------------ colours
    def ink(self, v):
        """Grey for dot value v (0 = no dot, 1 = biggest dot) in this theme."""
        v = max(0.0, min(1.0, v))
        g = round(255 * (v if self.theme == 'dark' else 1 - v))
        return f'#{g:02x}{g:02x}{g:02x}'

    @property
    def paper(self):
        return self.ink(0)

    @property
    def light_mode(self):
        """Blend mode for adding light (night) / shadow ink (day)."""
        return 'screen' if self.theme == 'dark' else 'multiply'

    def uid(self, p='g'):
        self._id += 1
        return f'{p}{self._id}'

    def lgrad(self, x1, y1, x2, y2, stops):
        """Linear gradient in user space; stops = [(offset 0..1, value), ...]. Two stops at the same
        offset make a hard step. Returns url(#id)."""
        i = self.uid('lg')
        st = ''.join(f'<stop offset="{o}" stop-color="{self.ink(v)}"/>' for o, v in stops)
        self.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')
        return f'url(#{i})'

    # ------------------------------------------------------------------ primitives
    def add(self, s):
        self.parts.append(s)

    @staticmethod
    def _st(fill, stroke, sw, extra=''):
        out = f' fill="{fill or "none"}"'
        if stroke:
            out += f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'
        return out + extra

    def rect(self, x, y, w, h, fill=None, stroke=None, sw=9, rx=0, op=1, clip=None):
        c = f' clip-path="url(#{clip})"' if clip else ''
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"{self._st(fill, stroke, sw)} opacity="{op}"{c}/>')

    def circle(self, cx, cy, r, fill=None, stroke=None, sw=9, op=1):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}"{self._st(fill, stroke, sw)} opacity="{op}"/>')

    def ellipse(self, cx, cy, rx, ry, fill=None, stroke=None, sw=9, op=1, rot=0):
        self.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})"{self._st(fill, stroke, sw)} opacity="{op}"/>')

    def path(self, d, fill=None, stroke=None, sw=9, op=1, clip=None):
        c = f' clip-path="url(#{clip})"' if clip else ''
        self.add(f'<path d="{d}"{self._st(fill, stroke, sw)} opacity="{op}"{c}/>')

    def poly(self, pts, fill=None, stroke=None, sw=9, op=1, closed=True):
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + (' Z' if closed else '')
        self.path(d, fill, stroke, sw, op)

    def line(self, x1, y1, x2, y2, stroke, sw=9, op=1, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{da} opacity="{op}"/>')

    def clip_rect(self, x, y, w, h):
        i = self.uid('cl')
        self.defs.append(f'<clipPath id="{i}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
        return i

    def clip_path(self, d):
        i = self.uid('cp')
        self.defs.append(f'<clipPath id="{i}"><path d="{d}"/></clipPath>')
        return i

    # ------------------------------------------------------------------ grid-exact pieces
    def row(self, x0, x1, y, v, rows=1, op=1):
        """A crisp row (or rows) of dots: a rect covering whole cells. Keep y (and x0, x1) multiples of 9."""
        self.rect(x0, y, x1 - x0, P * rows, fill=self.ink(v), op=op)

    def col(self, x, y0, y1, v, cols=1, op=1):
        self.rect(x, y0, P * cols, y1 - y0, fill=self.ink(v), op=op)

    def frame(self, x0, y0, x1, y1, v, t=1, fill=None, rx=0):
        """Cell-aligned box: an outline t cells thick at value v, optional fill value inside."""
        if fill is not None:
            self.rect(x0, y0, x1 - x0, y1 - y0, fill=self.ink(fill), rx=rx)
        th = P * t
        if rx:
            self.rect(x0 + th / 2, y0 + th / 2, x1 - x0 - th, y1 - y0 - th, stroke=self.ink(v), sw=th, rx=max(0, rx - th / 2))
        else:
            self.rect(x0, y0, x1 - x0, th, fill=self.ink(v)); self.rect(x0, y1 - th, x1 - x0, th, fill=self.ink(v))
            self.rect(x0, y0, th, y1 - y0, fill=self.ink(v)); self.rect(x1 - th, y0, th, y1 - y0, fill=self.ink(v))

    def hgrad(self, x0, y0, x1, y1, stops, rx=0):
        self.rect(x0, y0, x1 - x0, y1 - y0, fill=self.lgrad(x0, 0, x1, 0, stops), rx=rx)

    def vgrad(self, x0, y0, x1, y1, stops, rx=0):
        self.rect(x0, y0, x1 - x0, y1 - y0, fill=self.lgrad(0, y0, 0, y1, stops), rx=rx)

    # ------------------------------------------------------------------ groups: planes, blending, shifts
    @contextlib.contextmanager
    def plane(self, op=1, clip=None):
        """Everything drawn inside as one group at opacity op (a far plane: op .35–.6)."""
        mark = len(self.parts); yield
        inner = ''.join(self.parts[mark:]); del self.parts[mark:]
        c = f' clip-path="url(#{clip})"' if clip else ''
        self.add(f'<g opacity="{op}"{c}>{inner}</g>')

    @contextlib.contextmanager
    def blend(self, mode=None, op=1):
        """Blend what is drawn inside onto what is below: 'screen' adds light (night), 'multiply' adds
        ink (day shadows). Default: the theme's light_mode. Never wrap a blended group in a clipped <g>
        (the clip isolates it and the blend paints black) — clip the element itself."""
        mark = len(self.parts); yield
        inner = ''.join(self.parts[mark:]); del self.parts[mark:]
        self.add(f'<g style="mix-blend-mode:{mode or self.light_mode}" opacity="{op}">{inner}</g>')

    @contextlib.contextmanager
    def shift(self, dx=0, dy=0):
        """Move what is drawn inside (keep dx, dy multiples of 9 to stay on the grid)."""
        mark = len(self.parts); yield
        inner = ''.join(self.parts[mark:]); del self.parts[mark:]
        self.add(f'<g transform="translate({dx} {dy})">{inner}</g>')

    @contextlib.contextmanager
    def cut(self, margin=P):
        """Draw a near shape cut out of what is behind it: everything drawn inside is first drawn as a
        paper/ground silhouette fattened by `margin` px, then drawn normally. This is the overlap rule."""
        mark = len(self.parts); yield
        inner = ''.join(self.parts[mark:]); del self.parts[mark:]
        i = self.uid('cut')
        self.defs.append(f'<filter id="{i}" x="-20%" y="-20%" width="140%" height="140%">'
                         f'<feMorphology in="SourceAlpha" operator="dilate" radius="{margin}" result="d"/>'
                         f'<feFlood flood-color="{self.paper}" result="f"/><feComposite in="f" in2="d" operator="in"/></filter>')
        self.add(f'<g filter="url(#{i})">{inner}</g>')
        self.add(inner)

    # ------------------------------------------------------------------ light
    def glow(self, cx, cy, r, v, mid=0.45, ry=None, clip=None, mode=None):
        """A light (night: added with screen) or a soft shadow (day: multiply): v at the centre, v*mid at
        40 %, 0 at r. Keep lights small and on a dark surround — a glow raising its neighbours to .6+
        makes the source disappear. clip= goes on the element itself (see blend())."""
        ry = ry or r
        c = f' clip-path="url(#{clip})"' if clip else ''
        i = self.uid('gl')
        self.defs.append(f'<radialGradient id="{i}" gradientUnits="objectBoundingBox" cx="0.5" cy="0.5" r="0.5">'
                         f'<stop offset="0" stop-color="{self.ink(v)}"/><stop offset="0.4" stop-color="{self.ink(v * mid)}"/>'
                         f'<stop offset="1" stop-color="{self.ink(0)}"/></radialGradient>')
        self.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{ry}" fill="url(#{i})"{c} style="mix-blend-mode:{mode or self.light_mode}"/>')

    # ------------------------------------------------------------------ text
    def bitmap_text(self, x, y, txt, v, size=12, font='C:/Windows/Fonts/simsun.ttc', gap=2):
        """Grid-exact text: the font's 1-bit bitmap strike (SimSun: clean 12/14/16 px), each glyph pixel
        drawn as one whole cell at (x, y) (multiples of 9). Glyphs `size` cells tall. SVG <text> turns
        into mush on the screen — use this. Returns the width in px."""
        from PIL import Image, ImageDraw, ImageFont
        f = ImageFont.truetype(font, size)
        cx = x
        for ch in txt:
            im = Image.new('L', (size + 4, size + 4), 0)
            d = ImageDraw.Draw(im); d.fontmode = '1'
            d.text((0, 0), ch, font=f, fill=255)
            a = np.asarray(im) > 127
            for r in range(a.shape[0]):
                c0 = None
                for c in range(a.shape[1] + 1):
                    on = c < a.shape[1] and a[r, c]
                    if on and c0 is None:
                        c0 = c
                    if not on and c0 is not None:
                        self.rect(cx + c0 * P, y + r * P, (c - c0) * P, P, fill=self.ink(v)); c0 = None
            cx += ((size // 2 if ord(ch) < 128 else size) + gap) * P
        return cx - x - gap * P

    def seg7(self, x, y, txt, v, ghost=0.1, cell=P, w=4, h=7):
        """Clock digits on a w x h cell grid each (segments one cell thick), unlit segments at `ghost`."""
        SEG = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg', '5': 'acdfg', '6': 'acdefg',
               '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
        cx = x
        for ch in txt:
            if ch == ':':
                self.rect(cx, y + 2 * cell, cell, cell, fill=self.ink(v)); self.rect(cx, y + 4 * cell, cell, cell, fill=self.ink(v))
                cx += 2 * cell; continue
            on = SEG.get(ch, '')
            segs = {'a': (1, 0, w - 2, 1), 'b': (w - 1, 1, 1, h // 2 - 1), 'c': (w - 1, h // 2 + 1, 1, h - h // 2 - 2),
                    'd': (1, h - 1, w - 2, 1), 'e': (0, h // 2 + 1, 1, h - h // 2 - 2), 'f': (0, 1, 1, h // 2 - 1), 'g': (1, h // 2, w - 2, 1)}
            for k, (sx, sy, sw_, sh) in segs.items():
                self.rect(cx + sx * cell, y + sy * cell, sw_ * cell, sh * cell, fill=self.ink(v if k in on else ghost))
            cx += (w + 1) * cell
        return cx - x

    # ------------------------------------------------------------------ objects (drawn for the screen)
    def leaf(self, x, y, angle, length, width, dark=0.6, lit=0.36, edge=0.8, curl=0.12, sw=6, midrib=6, notches=0,
             stem=0, stem_v=0.7, stem_w=9, light_left=True, air=0, notch_w=10):
        """A leaf from its base (x, y) toward `angle` (0 = up, + = clockwise): the half facing the light
        `lit`, the other `dark` (a step of >= .2 so it survives), an `edge` outline, a paper midrib >= 6 px,
        optional monstera `notches` (paper slits), an optional `stem` (px) before the blade, and `air`
        (px of paper around it, so it separates from what is behind). Returns the tip point."""
        a = math.radians(angle)
        ux, uy = math.sin(a), -math.cos(a)
        nx, ny = -uy, ux
        if stem:
            self.line(x, y, x + ux * stem, y + uy * stem, self.ink(stem_v), stem_w)
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
        left_is_lit = (nx > 0) != light_left
        if air:
            self.poly(Lp + Rp[::-1], fill=self.paper, stroke=self.paper, sw=2 * air)
        self.poly(mid + Lp[::-1], fill=self.ink(lit if left_is_lit else dark))
        self.poly(mid + Rp[::-1], fill=self.ink(dark if left_is_lit else lit))
        if edge is not None:
            self.poly(Lp + Rp[::-1], stroke=self.ink(edge), sw=sw)
        for k in range(notches):
            t = 0.24 + 0.56 * k / max(1, notches - 1)
            for sd in (-1, 1):
                p0, p1 = Pt(t + 0.09, sd * W * 1.2), Pt(t, sd * W * 0.22)
                self.line(p0[0], p0[1], p1[0], p1[1], self.paper, notch_w)
        if midrib:
            self.poly(mid[1:-2], stroke=self.paper, sw=midrib, closed=False)
        return Pt(1, 0)

    def cyl(self, x0, y0, x1, y1, v, shade_v, light_left=True, band=0.3, rx=0, edge=None, sw=9):
        """A cylinder / rounded body front-on, the videos' way: a flat tone with a HARD shade band
        (~30 % of the width) on the side away from the light, optional outline."""
        w = x1 - x0
        xs = x1 - w * band if light_left else x0 + w * band
        o = (xs - x0) / w
        st = [(0, v), (o, v), (o, shade_v), (1, shade_v)] if light_left else [(0, shade_v), (o, shade_v), (o, v), (1, v)]
        self.rect(x0, y0, w, y1 - y0, fill=self.lgrad(x0, 0, x1, 0, st), rx=rx)
        if edge is not None:
            self.rect(x0 + sw / 2, y0 + sw / 2, w - sw, y1 - y0 - sw, stroke=self.ink(edge), sw=sw, rx=max(0, rx - sw / 2))

    def pot(self, cx, base, w, h, body=0.17, rim=0.24, edge=0.6, shade=0.36, light_left=True, rim_h=None):
        """Flower pot like the video-3 refs: rim band + tapering body with rounded bottom corners, one-cell
        outline, a hard shade band (~28 %) on the side away from the light. Snap cx, w, base to 9."""
        rim_h = rim_h or round(h * 0.26 / P) * P
        x0, x1 = cx - w / 2, cx + w / 2
        t = round(w * 0.06 / P) * P
        d = (f'M{x0 + 9} {base - h + rim_h} H{x1 - 9} L{x1 - 9 - t} {base - 18} Q{x1 - 9 - t} {base} {x1 - 27 - t} {base} '
             f'H{x0 + 27 + t} Q{x0 + 9 + t} {base} {x0 + 9 + t} {base - 18} Z')
        xs = (x1 - w * 0.28) if light_left else (x0 + w * 0.28)
        o = (xs - x0) / w
        st = [(0, body), (o, body), (o, shade), (1, shade)] if light_left else [(0, shade), (o, shade), (o, body), (1, body)]
        self.path(d, fill=self.lgrad(x0, 0, x1, 0, st))
        self.path(d, stroke=self.ink(edge), sw=9)
        r2 = min(1, rim + 0.22)
        st2 = [(0, rim), (o, rim), (o, r2), (1, r2)] if light_left else [(0, r2), (o, r2), (o, rim), (1, rim)]
        self.rect(x0, base - h, w, rim_h, fill=self.lgrad(x0, 0, x1, 0, st2), rx=4)
        self.rect(x0 + 4.5, base - h + 4.5, w - 9, rim_h - 9, stroke=self.ink(edge), sw=9, rx=4)

    def cloud(self, cx, cy, w, h, top=0.42, bottom=0.08):
        """A cloud like r3_500: a bumpy top of separate lumps (the DENSEST part), the base fading out.
        For a crisper, stair-stepped cloud build it on cells (cellkit)."""
        i = self.uid('cl')
        lumps = [(-0.34, 0.1, 0.26), (-0.12, -0.18, 0.34), (0.14, -0.3, 0.36), (0.36, -0.06, 0.28), (0.02, 0.12, 0.3)]
        parts = ''.join(f'<circle cx="{cx + dx * w}" cy="{cy + dy * h}" r="{r * w * 0.62}"/>' for dx, dy, r in lumps)
        parts += f'<rect x="{cx - w / 2}" y="{cy}" width="{w}" height="{h * 0.36}" rx="{h * 0.18}"/>'
        self.defs.append(f'<clipPath id="{i}">{parts}</clipPath>')
        g = self.lgrad(0, cy - h * 0.6, 0, cy + h * 0.36, [(0, top), (0.55, (top + bottom) / 2), (1, bottom)])
        self.rect(cx - w, cy - h, 2 * w, 2 * h, fill=g, clip=i)

    def canopy(self, cx, cy, r, v=0.6, lit=0.3, shade=0.85, lumps=7, holes=3, seed=1):
        """A tree crown: lumpy blob (circle union), lit caps on the light side (upper left) at `lit`, the
        body `v`, the lower right a hard step heavier `shade`, a few paper sky-holes (>= 2 cells)."""
        rng = np.random.default_rng(seed)
        circ = []
        for k in range(lumps):
            a = 2 * math.pi * k / lumps + rng.uniform(-0.3, 0.3)
            circ.append((cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.45, r * rng.uniform(0.42, 0.58)))
        circ.append((cx, cy, r * 0.62))
        i = self.uid('cn')
        self.defs.append(f'<clipPath id="{i}">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{rr}"/>' for x, y, rr in circ) + '</clipPath>')
        g = self.lgrad(cx - r, cy - r, cx + r, cy + r, [(0, lit), (0.38, lit), (0.38, v), (0.68, v), (0.68, shade), (1, shade)])
        self.rect(cx - 1.4 * r, cy - 1.4 * r, 2.8 * r, 2.8 * r, fill=g, clip=i)
        for k in range(holes):
            hx, hy = cx + rng.uniform(-0.5, 0.5) * r, cy + rng.uniform(-0.3, 0.4) * r
            self.circle(snap(hx), snap(hy), P * rng.uniform(1.0, 1.6), fill=self.paper)

    def tuft(self, x, base, v=0.6, h=54):
        """A grass tuft: three short blades | / \\ from a base point, 9 px wide strokes."""
        for dx, dy in ((0, -h), (-h * 0.45, -h * 0.75), (h * 0.45, -h * 0.75)):
            self.line(x, base, x + dx, base + dy, self.ink(v), 8)

    def sun(self, cx, cy, r, v=0.38, ray_v=0.45, rays=12, ray_len=36, gap=27):
        """The video-3 sun: a flat disc and short rays made of 2-dot dashes (each dash >= 1 cell)."""
        self.circle(cx, cy, r, fill=self.ink(v))
        for k in range(rays):
            a = 2 * math.pi * k / rays
            r0, r1 = r + gap, r + gap + ray_len
            self.line(cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a), self.ink(ray_v), 9)

    def moon(self, cx, cy, r, v=1.0, halo=0.25, halo_r=None, phase=0.0):
        """Night moon: a full disc (or a crescent with phase > 0: a paper bite), a small blended halo."""
        self.glow(cx, cy, halo_r or r * 2.2, halo, mid=0.35)
        self.circle(cx, cy, r, fill=self.ink(v))
        if phase:
            self.circle(cx + r * phase, cy - r * 0.15, r * 0.95, fill=self.paper)

    def skyline(self, x0, x1, base, heights, v=0.22, win=0.0, seed=2, widths=(90, 160)):
        """Far city: flat rectangles at <= .25 with a grid of window gaps (paper), no outlines."""
        rng = np.random.default_rng(seed)
        x = x0
        k = 0
        while x < x1:
            w = snap(rng.uniform(*widths)); h = snap(heights[k % len(heights)])
            self.rect(x, base - h, min(w, x1 - x), h, fill=self.ink(v))
            for yy in range(int(base - h + 18), int(base - 18), 27):
                for xx in range(int(x + 18), int(x + w - 18), 27):
                    self.rect(snap(xx), snap(yy), 9, 9, fill=self.ink(win))
            x += w + snap(rng.uniform(0, 27)); k += 1

    def panel(self, x, y, w, h, fill=0.25, edge=0.6, inset=None, **_):
        """A flat front panel (cabinet, drawer, door): fill tone + a one-cell outline (grid-aligned)."""
        self.frame(x, y, x + w, y + h, edge, fill=fill)
        if inset:
            self.frame(x + inset, y + inset, x + w - inset, y + h - inset, edge * 0.8)

    def save(self, path):
        body = ''.join(self.parts)
        defs = f'<defs>{"".join(self.defs)}</defs>' if self.defs else ''
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
               f'<rect width="100%" height="100%" fill="{self.paper}"/>{defs}{body}</svg>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        return path
