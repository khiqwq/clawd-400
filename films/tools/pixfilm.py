"""Shared pieces for the Clawd films: a sprite atlas + per-frame draw list for the pixel layer, and
the dotted line-art renderer for rooms (the reference videos' look: 4 px dots on a 9 px pitch).

The film's pixel layer is authored in Python with the real engine, so Clawd is drawn exactly like the
GIFs; the HTML comp only plays it back (frame index = t * fps) under its camera.
"""
import hashlib
import json
import math
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

import engine  # noqa: E402
from engine import Canvas, col  # noqa: E402

LPX = 14            # film px per logical (Clawd) pixel — the videos measure 13.9
DOT_PITCH = 9       # film px between dot centres in the rooms
DOT_SIZE = 4


def canvas_image(c):
    im = Image.new('RGBA', (c.w, c.h), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(c.px):
        for x, v in enumerate(row):
            if v is not None:
                px[x, y] = tuple(v) + (255,)
    return im


class Track:
    """Per-frame list of sprites for the pixel layer. Sprites are engine Canvases, deduplicated."""

    def __init__(self, fps, dur, w, h):
        self.fps, self.dur, self.w, self.h = fps, dur, w, h
        self.n = int(round(dur * fps))
        self.frames = [[] for _ in range(self.n)]
        self.keys, self.imgs = {}, []

    def sprite(self, c):
        im = canvas_image(c)
        box = im.getbbox()
        if box is None:
            return None
        im = im.crop(box)
        key = hashlib.md5(im.tobytes() + bytes(str(im.size), 'ascii')).hexdigest()
        if key not in self.keys:
            self.keys[key] = len(self.imgs)
            self.imgs.append(im)
        return self.keys[key], box[0], box[1]

    def put(self, i, c, lx, ly):
        """Draw Canvas c with its top-left at logical (lx, ly) of the layer on frame i."""
        s = self.sprite(c)
        if s is not None:
            idx, ox, oy = s
            self.frames[i] += [idx, int(lx) + ox, int(ly) + oy]

    def export(self, path_png, path_js, extra=None):
        # shelf-pack the sprites into one atlas
        order = sorted(range(len(self.imgs)), key=lambda k: -self.imgs[k].size[1])
        W, x, y, sh, rects = 1024, 0, 0, 0, [None] * len(self.imgs)
        for k in order:
            w, h = self.imgs[k].size
            if x + w > W:
                x, y, sh = 0, y + sh + 1, 0
            rects[k] = [x, y, w, h]
            x += w + 1
            sh = max(sh, h)
        atlas = Image.new('RGBA', (W, y + sh + 1), (0, 0, 0, 0))
        for k, im in enumerate(self.imgs):
            atlas.paste(im, (rects[k][0], rects[k][1]))
        atlas.save(path_png)
        data = dict(L=LPX, w=self.w, h=self.h, fps=self.fps, n=self.n, rects=rects, frames=self.frames)
        data.update(extra or {})
        with open(path_js, 'w', encoding='utf-8') as f:
            f.write('window.PIX = ' + json.dumps(data, separators=(',', ':')) + ';\n')
        return atlas.size, len(self.imgs)


class Dots:
    """Dotted line art. Coordinates are logical px (floats ok); drawn on a 9-px dot grid.
    Values are grey levels: B bright outline, M mid, D dim, F faint fill."""
    B, M, D, F = 214, 150, 96, 62

    def __init__(self, w_l, h_l):
        self.wpx, self.hpx = int(w_l * LPX), int(h_l * LPX)
        self.cols, self.rows = math.ceil(self.wpx / DOT_PITCH), math.ceil(self.hpx / DOT_PITCH)
        self.im = Image.new('L', (self.cols, self.rows), 0)
        self.d = ImageDraw.Draw(self.im)

    @staticmethod
    def c(v):
        return int(round(v * LPX / DOT_PITCH))

    def _box(self, x, y, w, h):
        return [self.c(x), self.c(y), max(self.c(x), self.c(x + w) - 1), max(self.c(y), self.c(y + h) - 1)]

    def rect(self, x, y, w, h, v=B, fill=None):
        self.d.rectangle(self._box(x, y, w, h), outline=v, fill=fill)

    def fill(self, x, y, w, h, v=F):
        self.d.rectangle(self._box(x, y, w, h), fill=v)

    def clear(self, x, y, w, h):
        self.d.rectangle(self._box(x, y, w, h), fill=0)

    def line(self, x0, y0, x1, y1, v=B, width=1):
        self.d.line([self.c(x0), self.c(y0), self.c(x1), self.c(y1)], fill=v, width=width)

    def ellipse(self, x, y, w, h, v=B, fill=None):
        self.d.ellipse(self._box(x, y, w, h), outline=v, fill=fill)

    def poly(self, pts, v=B, fill=None):
        self.d.polygon([(self.c(a), self.c(b)) for a, b in pts], outline=v, fill=fill)

    def hatch(self, x, y, w, h, v=D, step=2):
        x0, y0, x1, y1 = self._box(x, y, w, h)
        for yy in range(y0, y1 + 1, step):
            for xx in range(x0 + (yy // step) % 2, x1 + 1, step):
                self.im.putpixel((xx, yy), v)

    def dot(self, x, y, v=B):
        cx, cy = self.c(x), self.c(y)
        if 0 <= cx < self.cols and 0 <= cy < self.rows:
            self.im.putpixel((cx, cy), v)

    def render(self):
        out = Image.new('RGBA', (self.wpx, self.hpx), (0, 0, 0, 0))
        dr = ImageDraw.Draw(out)
        px = self.im.load()
        for cy in range(self.rows):
            for cx in range(self.cols):
                v = px[cx, cy]
                if v:
                    x, y = cx * DOT_PITCH, cy * DOT_PITCH
                    dr.rectangle([x, y, x + DOT_SIZE - 1, y + DOT_SIZE - 1], fill=(v, v, v, 255))
        return out


def art_canvas(rows, cmap=None, w=None, h=None):
    """A Canvas holding one piece of pixel art (engine art syntax)."""
    rows = engine.parse(rows) if isinstance(rows, str) else rows
    c = Canvas(w or max(len(r) for r in rows), h or len(rows))
    c.art(rows, 0, 0, cmap=cmap or {})
    return c


# ---------------------------------------------------------------- timing helpers (seconds)
def seg(t, t0, t1):
    return 0.0 if t <= t0 else 1.0 if t >= t1 else (t - t0) / (t1 - t0)


def arc(t, t0, t1, p0, p1, height):
    """Ballistic hop from p0 to p1 (logical px), rising about `height` above the higher end."""
    u = seg(t, t0, t1)
    x = p0[0] + (p1[0] - p0[0]) * u
    y = p0[1] + (p1[1] - p0[1]) * u - 4 * (height + abs(p1[1] - p0[1]) / 2) * u * (1 - u)
    return round(x), round(y)


def fall(t, t0, t1, y0, y1):
    u = seg(t, t0, t1)
    return round(y0 + (y1 - y0) * u * u)


def lerp(a, b, u):
    return a + (b - a) * u
