"""Clawd pixel-art GIF engine.

Everything is drawn on a 40x40 logical grid and blown up 12x to 480x480,
matching the reference GIFs (flat colours, chunky blocks, transparent bg).
"""
import math
import random
from PIL import Image

G = 40          # logical canvas size
SCALE = 12      # screen px per logical px -> 480x480
GROUND = 36     # first row below Clawd's feet
BX, BY = 12, 21 # default top-left of Clawd's 16x12 body

PAL = {
    'O': (227, 126, 82),   # Clawd orange
    'o': (197, 112, 71),   # side face / shade
    'd': (160, 84, 52),    # deep shade
    'K': (0, 0, 0),
    'k': (64, 60, 66),     # soft black
    'W': (255, 255, 255),
    'w': (226, 226, 236),  # off-white
    'L': (200, 198, 214),  # lavender grey (bubbles, smoke)
    'G': (195, 191, 182),  # light grey
    'g': (137, 134, 125),  # grey
    'B': (102, 153, 208),  # speech-bubble blue
    'b': (56, 62, 129),    # navy
    'S': (176, 212, 240),  # sky / ice
    'C': (110, 200, 220),  # cyan
    'Y': (243, 179, 79),   # golden yellow
    'y': (250, 216, 152),  # pale yellow
    'U': (255, 226, 92),   # bright yellow
    'R': (214, 64, 64),    # red
    'Z': (236, 92, 118),   # heart pink-red
    'r': (244, 168, 176),  # light pink
    'P': (150, 112, 200),  # purple
    'p': (206, 186, 238),  # lilac
    'E': (106, 178, 98),   # green
    'e': (58, 124, 70),    # dark green
    'N': (146, 96, 62),    # brown
    'n': (98, 62, 42),     # dark brown
    'T': (240, 224, 190),  # cream
    'M': (86, 39, 49),     # maroon
    'F': (248, 148, 56),   # flame orange
    'H': (235, 100, 105),  # blush
    'V': (44, 88, 150),    # headphone navy
    'm': (140, 30, 45),    # crimson (reading glasses)
}


def col(c):
    if c is None or isinstance(c, tuple):
        return c
    if c.startswith('#'):
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return PAL[c]


def mix(a, b, t):
    a, b = col(a), col(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def parse(art):
    """Art strings: one row per line, whitespace ignored, '.' = transparent."""
    if isinstance(art, (list, tuple)):
        return list(art)
    return [ln.strip() for ln in art.strip('\n').splitlines() if ln.strip()]


def size(art):
    rows = parse(art)
    return max(len(r) for r in rows), len(rows)


# --------------------------------------------------------------------------- font
_F = {
    'A': '.#.|#.#|###|#.#|#.#', 'B': '##.|#.#|##.|#.#|##.', 'C': '.##|#..|#..|#..|.##',
    'D': '##.|#.#|#.#|#.#|##.', 'E': '###|#..|##.|#..|###', 'F': '###|#..|##.|#..|#..',
    'G': '.##|#..|#.#|#.#|.##', 'H': '#.#|#.#|###|#.#|#.#', 'I': '###|.#.|.#.|.#.|###',
    'J': '..#|..#|..#|#.#|.#.', 'K': '#.#|#.#|##.|#.#|#.#', 'L': '#..|#..|#..|#..|###',
    'M': '#.#|###|###|#.#|#.#', 'N': '##.|#.#|#.#|#.#|#.#', 'O': '###|#.#|#.#|#.#|###',
    'P': '##.|#.#|##.|#..|#..', 'Q': '.#.|#.#|#.#|##.|.##', 'R': '##.|#.#|##.|#.#|#.#',
    'S': '.##|#..|.#.|..#|##.', 'T': '###|.#.|.#.|.#.|.#.', 'U': '#.#|#.#|#.#|#.#|###',
    'V': '#.#|#.#|#.#|#.#|.#.', 'W': '#.#|#.#|###|###|#.#', 'X': '#.#|#.#|.#.|#.#|#.#',
    'Y': '#.#|#.#|.#.|.#.|.#.', 'Z': '###|..#|.#.|#..|###',
    '0': '.#.|#.#|#.#|#.#|.#.', '1': '.#.|##.|.#.|.#.|###', '2': '##.|..#|.#.|#..|###',
    '3': '##.|..#|.#.|..#|##.', '4': '#.#|#.#|###|..#|..#', '5': '###|#..|##.|..#|##.',
    '6': '.##|#..|###|#.#|###', '7': '###|..#|.#.|.#.|.#.', '8': '###|#.#|###|#.#|###',
    '9': '###|#.#|###|..#|##.',
    '!': '#|#|#|.|#', '.': '.|.|.|.|#', ',': '.|.|.|#|#', ':': '.|#|.|#|.', "'": '#|#|.|.|.',
    '?': '##.|..#|.#.|...|.#.', '-': '...|...|###|...|...', '+': '...|.#.|###|.#.|...',
    '=': '...|###|...|###|...', '/': '..#|..#|.#.|#..|#..', '\\': '#..|#..|.#.|..#|..#',
    '<': '..#|.#.|#..|.#.|..#', '>': '#..|.#.|..#|.#.|#..', '(': '.#|#.|#.|#.|.#',
    ')': '#.|.#|.#|.#|#.', '[': '##|#.|#.|#.|##', ']': '##|.#|.#|.#|##',
    '{': '.##|.#.|##.|.#.|.##', '}': '##.|.#.|.##|.#.|##.', '_': '...|...|...|...|###',
    '*': '...|#.#|.#.|#.#|...', '#': '#.#|###|#.#|###|#.#', '$': '.##|##.|.#.|.##|##.',
    '%': '#..|..#|.#.|#..|..#', '^': '.#.|#.#|...|...|...', '~': '....|.#.#|#.#.|....|....',
    '@': '.##.|#..#|#.##|#...|.##.', '&': '.#.|#.#|.#.|#.#|.##', '|': '#|#|#|#|#',
    ' ': '..|..|..|..|..', '♥': '.#.#.|#####|#####|.###.|..#..', '%%': '',
}
FONT = {k: v.split('|') for k, v in _F.items() if v}


def text_w(s):
    return sum(len(FONT.get(ch, FONT['?'])[0]) + 1 for ch in s.upper()) - 1 if s else 0


# --------------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w=G, h=G):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]

    def put(self, x, y, c):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = col(c)

    def get(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[y][x]
        return None

    def erase(self, x, y, w=1, h=1):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.px[yy][xx] = None

    def rect(self, x, y, w, h, c):
        c = col(c)
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        for yy in range(max(0, y0), min(self.h, y0 + int(h))):
            row = self.px[yy]
            for xx in range(max(0, x0), min(self.w, x0 + int(w))):
                row[xx] = c

    def box(self, x, y, w, h, c):
        """Outline rectangle."""
        self.rect(x, y, w, 1, c); self.rect(x, y + h - 1, w, 1, c)
        self.rect(x, y, 1, h, c); self.rect(x + w - 1, y, 1, h, c)

    def rrect(self, x, y, w, h, c):
        """Rectangle with the four corner pixels cut (pixel 'rounded')."""
        self.rect(x + 1, y, w - 2, h, c)
        self.rect(x, y + 1, w, h - 2, c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def disc(self, cx, cy, r, c):
        """Filled circle centred on pixel-edge coords (cx, cy)."""
        for y in range(int(cy - r - 1), int(cy + r + 1)):
            for x in range(int(cx - r - 1), int(cx + r + 1)):
                if (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= r * r:
                    self.put(x, y, c)

    def ring(self, cx, cy, r, c, t=1):
        for y in range(int(cy - r - 1), int(cy + r + 1)):
            for x in range(int(cx - r - 1), int(cx + r + 1)):
                d = math.hypot(x + .5 - cx, y + .5 - cy)
                if r - t <= d <= r:
                    self.put(x, y, c)

    def art(self, art, x, y, flip=False, cmap=None, only=None):
        rows = parse(art)
        wmax = max(len(r) for r in rows)
        for j, row in enumerate(rows):
            if flip:
                row = row.ljust(wmax, '.')[::-1]
            for i, ch in enumerate(row):
                if ch in '. ':
                    continue
                if cmap and ch in cmap:
                    ch = cmap[ch]
                if ch is None:
                    continue
                if only is None or ch in only:
                    self.put(x + i, y + j, ch)

    def text(self, s, x, y, c='K'):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT['?'])
            for j, row in enumerate(g):
                for i, p in enumerate(row):
                    if p == '#':
                        self.put(cx + i, y + j, c)
            cx += len(g[0]) + 1
        return cx - x - 1

    def text_c(self, s, cx, y, c='K'):
        """Text centred on pixel-edge x coordinate cx."""
        return self.text(s, int(round(cx - text_w(s) / 2)), y, c)

    def blit(self, other, dx=0, dy=0):
        for y in range(other.h):
            ty = y + dy
            if not 0 <= ty < self.h:
                continue
            srow, trow = other.px[y], self.px[ty]
            for x in range(other.w):
                c = srow[x]
                if c is not None and 0 <= x + dx < self.w:
                    trow[x + dx] = c

    def copy(self):
        c = Canvas(self.w, self.h)
        c.px = [row[:] for row in self.px]
        return c

    def recolor(self, fn):
        for row in self.px:
            for i, c in enumerate(row):
                if c is not None:
                    row[i] = fn(c)
        return self

    def outline(self, c):
        """New canvas with a 1-px outline in colour c around everything drawn (for white props)."""
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is None and any(self.get(x + dx, y + dy) is not None
                                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    out.px[y][x] = col(c)
        out.blit(self)
        return out

    def silhouette(self, c):
        c = col(c)
        return self.recolor(lambda _: c)

    def bbox(self):
        xs = [x for y in range(self.h) for x in range(self.w) if self.px[y][x] is not None]
        ys = [y for y in range(self.h) for x in range(self.w) if self.px[y][x] is not None]
        if not xs:
            return None
        return min(xs), min(ys), max(xs) + 1, max(ys) + 1

    # ---- whole-layer transforms (return new canvases)
    def flipx(self):
        c = Canvas(self.w, self.h)
        c.px = [row[::-1] for row in self.px]
        return c

    def flipy(self):
        c = Canvas(self.w, self.h)
        c.px = [row[:] for row in self.px[::-1]]
        return c

    def shift(self, dx, dy):
        c = Canvas(self.w, self.h)
        c.blit(self, dx, dy)
        return c

    def rot90(self, k, cx=20, cy=28):
        """Rotate by k*90deg clockwise around pixel-edge point (cx, cy)."""
        k %= 4
        if k == 0:
            return self.copy()
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c is None:
                    continue
                nx, ny = x, y
                for _ in range(k):
                    nx, ny = cx + cy - ny - 1, cy - cx + nx
                out.put(nx, ny, c)
        return out

    def rotate(self, deg, cx=20, cy=28):
        """Nearest-neighbour rotation by any angle (keeps the chunky look)."""
        out = Canvas(self.w, self.h)
        a = math.radians(-deg)
        ca, sa = math.cos(a), math.sin(a)
        for y in range(self.h):
            for x in range(self.w):
                u, v = x + .5 - cx, y + .5 - cy
                sx, sy = cx + u * ca - v * sa, cy + u * sa + v * ca
                c = self.get(math.floor(sx), math.floor(sy)) if 0 <= sx < self.w and 0 <= sy < self.h else None
                if c is not None:
                    out.px[y][x] = c
        return out

    def scale(self, s, ax=20, ay=36, sy=None):
        """Nearest scale around anchor (ax, ay); sy for separate vertical scale."""
        sy = s if sy is None else sy
        out = Canvas(self.w, self.h)
        if s <= 0 or sy <= 0:
            return out
        for y in range(self.h):
            for x in range(self.w):
                srcx = math.floor((x + .5 - ax) / s + ax)
                srcy = math.floor((y + .5 - ay) / sy + ay)
                c = self.get(srcx, srcy) if 0 <= srcx < self.w and 0 <= srcy < self.h else None
                if c is not None:
                    out.px[y][x] = c
        return out

    def shear(self, k, pivot=36):
        """Lean: row y shifts by round((pivot - y) * k)."""
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            d = int(round((pivot - y) * k))
            for x in range(self.w):
                c = self.px[y][x]
                if c is not None:
                    out.put(x + d, y, c)
        return out

    def wave(self, amp, period, phase):
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            d = int(round(amp * math.sin(2 * math.pi * (y / period + phase))))
            for x in range(self.w):
                c = self.px[y][x]
                if c is not None:
                    out.put(x + d, y, c)
        return out

    def to_image(self):
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        im.putdata([(c + (255,)) if c else (0, 0, 0, 0) for row in self.px for c in row])
        return im.resize((self.w * SCALE, self.h * SCALE), Image.NEAREST)


# --------------------------------------------------------------------------- anim helpers
def ph(t, n):
    """Phase 0..1 of frame t in a loop of n."""
    return (t % n) / n


def sin(t, n, k=1, off=0.0):
    return math.sin(2 * math.pi * (k * t / n + off))


def cos(t, n, k=1, off=0.0):
    return math.cos(2 * math.pi * (k * t / n + off))


def pick(seq, t):
    return seq[t % len(seq)]


def tri(t, n):
    """0 -> 1 -> 0 triangle over the loop."""
    p = ph(t, n)
    return 1 - abs(2 * p - 1)


def rng(seed):
    return random.Random(seed)


# --------------------------------------------------------------------------- Clawd
# Left-arm rectangles (dx, dy, w, h) relative to body top-left; right arm is mirrored.
ARMS = {
    'side':  [(-4, 4, 4, 4)],
    'mid':   [(-4, 2, 4, 4)],
    'high':  [(-4, 0, 4, 4)],
    'low':   [(-4, 7, 4, 4)],
    'up':    [(-3, -3, 3, 7)],
    'wave':  [(-4, -3, 3, 4), (-3, 1, 3, 3)],
    'down':  [(-3, 5, 3, 6)],
    'out':   [(-7, 5, 7, 3)],
    'reach': [(-6, 2, 3, 3), (-4, 4, 4, 3)],
    'short': [(-2, 4, 2, 4)],
    'front': [(1, 6, 6, 3)],    # folded across the belly (drawn in shade)
    'face':  [(1, 1, 6, 4)],    # covering the eyes (drawn in shade)
    'chin':  [(2, 5, 4, 3)],    # thinking pose (drawn in shade)
    'none':  [],
}
SHADED_ARMS = {'front', 'face', 'chin'}

# Eye glyphs for the LEFT eye (mirrored for the right). (rows, dy)
EYES = {
    # Only black glyphs at the reference size. Clawd's face is two eyes and nothing else.
    'normal':   (['KK', 'KK'], 2),
    'big':      (['KK', 'KK', 'KK'], 1),     # wide awake / surprised (tall eyes, video)
    'closed':   (['KKK'], 3),                # content, sipping (reference 2)
    'blink':    (['KK'], 3),
    'happy':    (['.K.', 'K.K'], 2),         # ^ ^ (reference 1)
    'down':     (['K.K', '.K.'], 2),         # blissful (headphones, video)
    'sad':      (['..K', 'KK.'], 2),
    'angry':    (['KKKK', '..KK'], 2),
    'worried':  (['..KK', 'KKKK'], 2),
    'focus':    (['KKKK', '..KK'], 2),       # reference 4, same orientation on both eyes
    'squint':   (['K..', '.K.', 'K..'], 1),  # > <
    'x':        (['K.K', '.K.', 'K.K'], 1),
    'dot':      (['K'], 3),
    'line':     (['KK'], 2),
    'none':     ([], 2),
}
# Retired glyphs (white sclera, coloured eyes, attached tears, lids) fall back to reference ones.
EYE_ALIASES = {'shine': 'normal', 'half': 'blink', 'heart': 'happy', 'star': 'big', 'googly': 'big',
               'dollar': 'big', 'wide': 'big', 'tear': 'normal', 'cry': 'closed'}
for _k, _v in EYE_ALIASES.items():
    EYES[_k] = EYES[_v]
EYES_SAME = {'focus'}  # glyphs not mirrored for the right eye


def _eye_rows(name, right):
    rows, dy = EYES[name]
    if right and name not in EYES_SAME:
        w = max((len(r) for r in rows), default=0)
        rows = [r.ljust(w, '.')[::-1] for r in rows]
    return rows, dy


def clawd(f, x=BX, y=BY, w=16, h=12, eyes='normal', eyes_r=None, look=0, lookv=0,
          la='side', ra='side', legs=(0, 0, 0, 0), legdx=(0, 0, 0, 0), leg_h=3,
          view='front', top=False, body='O', shade='o', blush=False, mouth=None,
          eye_col=None, tilt=0):
    """Draw Clawd. (x, y) = body top-left. Returns anchor points.

    view: front | back | qr/ql (3/4 turn) | q2r/q2l (strong 3/4) | sr/sl (profile).
    Turned views follow the reference video pixel-for-pixel (see _clawd_turned).
    tilt=1 (turned views): looking up / leaning back - near half of the head rises 1px.
    """
    if _HOOK:  # tweened() is recording or replacing poses for an in-between frame
        hook = _HOOK.pop()
        try:
            kw = hook(dict(x=x, y=y, w=w, h=h, eyes=eyes, eyes_r=eyes_r, look=look, lookv=lookv, la=la,
                           ra=ra, legs=legs, legdx=legdx, leg_h=leg_h, view=view, top=top, body=body,
                           shade=shade, blush=blush, mouth=mouth, eye_col=eye_col, tilt=tilt))
            return clawd(f, **kw)
        finally:
            _HOOK.append(hook)
    body, shade = col(body), col(shade)
    info = dict(x=x, y=y, w=w, h=h, head=(x + w / 2, y), view=view)
    if view in TURNED:
        return _clawd_turned(f, x, y, w, h, eyes, eyes_r, look, lookv, la, ra, legs, legdx, leg_h, view,
                             top, body, shade, blush, mouth, eye_col, tilt, info)

    # legs
    lx = [0, 4, w - 6, w - 2]
    for i in range(4):
        lh = leg_h - legs[i]
        if lh > 0:
            f.rect(x + lx[i] + legdx[i], y + h, 2, lh, body)

    # body
    f.rect(x, y, w, h, body)
    if top:
        f.rect(x, y, w, 1, shade)

    # arms
    def draw_arm(state, right):
        c = shade if state in SHADED_ARMS else body
        pts = []
        for (dx, dy, aw, ah) in ARMS[state]:
            ax = x + w - dx - aw if right else x + dx
            f.rect(ax, y + dy, aw, ah, c)
            pts.append((ax, y + dy, aw, ah))
        return pts

    lp = draw_arm(la, False) if la not in SHADED_ARMS or view == 'back' else []
    rp = draw_arm(ra, True) if ra not in SHADED_ARMS or view == 'back' else []

    def hand(pts, right, state):
        if not pts:
            return (x + (w if right else 0), y + 6)
        ax, ay, aw, ah = pts[0]
        if state in ('up', 'wave'):
            return (ax + aw / 2, ay)
        return ((ax + aw) if right else ax, ay + ah / 2)
    info['lh'] = hand(lp, False, la)
    info['rh'] = hand(rp, True, ra)

    if view == 'back':
        return info

    # eyes (right eye mirrored so expressions are symmetric)
    er = eyes_r or eyes
    for right, name in ((False, eyes), (True, er)):
        rows, dy = _eye_rows(name, right)
        if not rows:
            continue
        gw = max(len(r) for r in rows)
        ox = (x + 3 - gw // 2) if not right else (x + w - 3 - (gw - gw // 2))
        cmap = {'K': eye_col} if eye_col else {}
        cmap['o'] = shade
        f.art(rows, ox + look, y + dy + lookv, cmap=cmap)
    info['eyes'] = ((x + 3 + look, y + 3 + lookv), (x + w - 3 + look, y + 3 + lookv))
    # no mouth, no blush: the references never draw them (mouth/blush args are ignored)
    # shaded arms go on top of the face
    if la in SHADED_ARMS:
        draw_arm(la, False)
    if ra in SHADED_ARMS:
        draw_arm(ra, True)
    return info


def _mouth(f, mouth, mx, my):
    if mouth == 'o':
        f.rect(mx, my, 2, 2, 'K')
    elif mouth == 'O':
        f.rect(mx, my, 2, 3, 'K'); f.put(mx, my + 2, 'Z'); f.put(mx + 1, my + 2, 'Z')
    elif mouth == 'line':
        f.rect(mx, my, 2, 1, 'K')
    elif mouth == 'smile':
        f.art(['K..K', '.KK.'], mx - 1, my)
    elif mouth == 'frown':
        f.art(['.KK.', 'K..K'], mx - 1, my)
    elif mouth == 'w':
        f.art(['K.K.K', '.K.K.'], mx - 1, my)
    elif mouth == 'tongue':
        f.art(['KKKK', '.ZZ.'], mx - 1, my)
    elif mouth == 'teeth':
        f.art(['KKKK', 'KWWK', 'KKKK'], mx - 1, my)


TURNED = {'qr': 1, 'ql': 1, 'q2r': 2, 'q2l': 2, 'sr': 3, 'sl': 3}


def _clawd_turned(f, x, y, w, h, eyes, eyes_r, look, lookv, la, ra, legs, legdx, leg_h, view, top, body,
                  shade, blush, mouth, eye_col, tilt, info):
    """Turned Clawd, measured from the reference video (1 logical px = 13.9 screen px there).

    Always drawn facing RIGHT, then mirrored about the body centre for the *l views.
      yaw 1 (qr)  : 2-col shaded side face at the back; far eye moves in 2 cols, near eye 1 col
                    (perspective squeezes the gap); far arm sticks out with its outer half shaded;
                    near arm is a 2-col stub; the 4 legs spread evenly (1,5,9,13), back leg shaded.
      yaw 2 (q2r) : 3-col side face; eyes at cols 6-7 and on the front edge (near eye clipped);
                    far arm shows as a 3-col shaded block; near arm reaches forward-low.
      yaw 3 (sr)  : profile, 10 wide; one eye on the front edge; arm points forward (shade+2).
    Eye glyphs are NOT mirrored in turned views: both eyes look where Clawd is facing.
    tilt=1 lifts the near half of the head 1px and the near eye with it (looking up /
    leaning back, as in the reference GIFs 1-3).
    """
    yaw = TURNED[view]
    left = view.endswith('l')
    if left:  # draw the mirror image facing right, then flip
        la, ra = ra, la
        legs, legdx = tuple(legs[::-1]), tuple(-d for d in legdx[::-1])
        eyes, eyes_r = (eyes_r or eyes), eyes
        look = -look
    far_e, near_e = eyes, (eyes_r or eyes)
    off = f.w if left else 0  # draw off-canvas-safe, then mirror and shift back
    x += off
    L = Canvas(f.w * 3 if left else f.w, f.h)
    cmap = {'K': eye_col} if eye_col else {}
    cmap['o'] = shade

    if yaw == 3:
        sw = 10
        sx = x + (w - sw) // 2
        for lx, lift in ((1, legs[0]), (sw - 3, legs[3])):
            if leg_h - lift > 0:
                L.rect(sx + lx, y + h, 2, leg_h - lift, body)
        if leg_h - legs[0] > 0:
            L.rect(sx + 1, y + h, 1, leg_h - legs[0], shade)
        L.rect(sx, y, sw, h, body)
        L.rect(sx, y, 1, h, shade)
        if top:
            L.rect(sx, y, sw, 1, shade)
        if ra == 'up':
            L.rect(sx + sw - 4, y - 3, 3, 3, body); L.rect(sx + sw - 4, y - 1, 3, 1, shade)
            rh = (sx + sw - 2, y - 3)
        elif ra == 'none' or ra in SHADED_ARMS:
            rh = (sx + sw, y + 6)
        else:
            dy = {'high': 1, 'mid': 2, 'wave': 0, 'low': 7, 'down': 7}.get(ra, 4)
            L.rect(sx + sw, y + dy, 1, 4, shade); L.rect(sx + sw + 1, y + dy, 2, 4, body)
            rh = (sx + sw + 3, y + dy + 2)
        lh = (sx, y + 6)
        rows, dy = EYES[near_e]
        if rows:
            gw = max(len(r) for r in rows)
            rows = [r[gw - 2:] if gw > 2 else r for r in rows]
            L.art(rows, sx + sw - 2 + look, y + dy + lookv - tilt, cmap=cmap)
        if tilt:
            L.rect(sx + sw // 2, y - 1, sw - sw // 2, 1, shade if top else body)
        eyes_pos = ((sx + sw - 1, y + 3), (sx + sw - 1, y + 3))
        bx, bw = sx, sw
    else:
        band = 2 if yaw == 1 else 3
        lxs = [1, 5, w - 7, w - 3] if yaw == 1 else [0, 4, w - 6, w - 2]
        for i, lx in enumerate(lxs):
            lh_ = leg_h - legs[i]
            if lh_ > 0:
                L.rect(x + lx + legdx[i], y + h, 2, lh_, body)
                if i == 0:
                    L.rect(x + lx + legdx[i], y + h, 1 if yaw == 1 else 2, lh_, shade)
        L.rect(x, y, w, h, body)
        L.rect(x, y, band, h, shade)
        if top:
            L.rect(x, y, w, 1, shade)
        if tilt:
            L.rect(x + w // 2 - 1, y - 1, w - w // 2 + 1, 1, shade if top else body)
        # far arm (screen-left in the facing-right drawing)
        lh = (x, y + 6)
        if la == 'none' or la in SHADED_ARMS:
            pass
        elif yaw == 2 and la in ('side', 'mid', 'high', 'low'):
            # video: 3 shaded cols outside, and the arm root covers the side face in orange
            dy = ARMS[la][0][1]
            L.rect(x - 3, y + dy, 3, 4, shade)
            L.rect(x, y + dy, band, 4, body)
            lh = (x - 3, y + dy + 2)
        else:
            for (dx, dy, aw, ah) in ARMS[la]:
                L.rect(x + dx, y + dy, aw, ah, body)
                if dx < 0:
                    nshade = 1 if la in ('up', 'wave', 'down') else max(1, min(aw, -dx) - 2)
                    L.rect(x + dx, y + dy, nshade, ah, shade)
                    if dx + aw >= 0 and la not in ('up', 'wave'):
                        L.rect(x, y + dy, band, ah, body)  # arm root sits in front of the side face
            dx, dy, aw, ah = ARMS[la][0]
            lh = (x + dx + aw / 2, y + dy) if la in ('up', 'wave') else (x + dx, y + dy + ah / 2)
        # near arm (screen-right)
        if ra == 'none' or ra in SHADED_ARMS:
            rh = (x + w, y + 6)
        elif ra in ('up', 'wave'):
            # reference GIF 3: the raised near arm pops up over the front of the head,
            # with its underside in shade (wave tips it one column forward)
            ax = x + w - 5 + (1 if ra == 'wave' else 0) - tilt
            L.rect(ax, y - 3 - tilt, 4, 3, body); L.rect(ax, y - 1 - tilt, 4, 1, shade)
            rh = (ax + 2, y - 3 - tilt)
        elif ra in ('out', 'reach'):
            L.rect(x + w, y + 5, 6, 2, body)
            rh = (x + w + 6, y + 6)
        elif yaw == 1:
            # video: the near arm is almost hidden behind the body - a 1-col nub
            dy = ARMS[ra][0][1] if ARMS.get(ra) else 4
            dy = min(max(dy, 0), h - 4) + 1
            L.rect(x + w, y + dy, 1, 2, body)
            rh = (x + w + 1, y + dy + 1)
        else:
            dy = {'high': 3, 'mid': 4, 'low': 8, 'down': 8}.get(ra, 6)
            L.rect(x + w, y + dy, 3, 3, body); L.rect(x + w + 3, y + dy + 1, 1, 2, shade)
            rh = (x + w + 4, y + dy + 1)
        # eyes: same glyph orientation for both (looking where Clawd faces)
        placed = []
        for which, name in (('far', far_e), ('near', near_e)):
            rows, dy = EYES[name]
            if not rows:
                placed.append((x + (4 if which == 'far' else w - 3), y + 3))
                continue
            gw = max(len(r) for r in rows)
            if yaw == 1:
                ox = (x + 3 - gw // 2 + 2) if which == 'far' else (x + w - 3 - (gw - gw // 2) + 1)
            else:
                ox = (x + 7 - gw // 2) if which == 'far' else (x + w - gw)
            ox += look
            ey = y + dy + lookv - (tilt if which == 'near' else 0)
            rows = [r[:max(0, x + w - ox)] for r in rows]  # the front edge can clip the near eye
            L.art(rows, ox, ey, cmap=cmap)
            placed.append((ox + gw // 2, ey + 1))
        eyes_pos = tuple(placed)
        for st in (la, ra):  # shaded arms across the face
            if st in SHADED_ARMS:
                for (dx, dy, aw, ah) in ARMS[st]:
                    L.rect(x + band + dx, y + dy, aw, ah, shade)
        bx, bw = x, w
    if left:
        cx2 = 2 * x + w
        M = Canvas(L.w, f.h)
        for yy in range(L.h):
            row = L.px[yy]
            for xx in range(L.w):
                if row[xx] is not None:
                    M.put(cx2 - 1 - xx, yy, row[xx])
        L = M
        lh, rh = (cx2 - rh[0] - off, rh[1]), (cx2 - lh[0] - off, lh[1])
        eyes_pos = tuple((cx2 - ex - off, ey) for ex, ey in eyes_pos)
        bx = cx2 - bx - bw - off
    f.blit(L, -off, 0)
    info.update(lh=lh, rh=rh, eyes=eyes_pos, x=bx, w=bw)
    return info


def mini(f, x, y, eyes='normal', legs=(0, 0, 0, 0), la='side', ra='side', body='O',
         shade='o', look=0, view='front'):
    """Half-size Clawd: body 8x6 at (x, y), total 12 wide incl. arms, 8 tall incl. legs."""
    body, shade = col(body), col(shade)
    for i, lx in enumerate((0, 2, 5, 7)):
        if 2 - legs[i] > 0:
            f.rect(x + lx, y + 6, 1, 2 - legs[i], body)
    f.rect(x, y, 8, 6, body)
    arm = {'side': (-2, 2, 2, 2), 'up': (-1, -2, 1, 4), 'high': (-2, 0, 2, 2),
           'low': (-2, 3, 2, 2), 'none': None}
    for right, st in ((False, la), (True, ra)):
        a = arm[st]
        if a:
            dx, dy, aw, ah = a
            ax = x + 8 - dx - aw if right else x + dx
            f.rect(ax, y + dy, aw, ah, body)
    if view == 'back':
        return
    if view == 'qr':
        f.rect(x, y, 1, 6, shade); look += 1
    if view == 'ql':
        f.rect(x + 7, y, 1, 6, shade); look -= 1
    e = {'normal': (['K'], 1), 'closed': (['KK'], 2), 'big': (['K', 'K'], 1),
         'happy': (['.K', 'K.'], 1), 'heart': (['Z'], 1), 'x': (['K'], 1),
         'shine': (['K'], 1), 'none': ([], 1)}
    rows, dy = e.get(eyes, e['normal'])
    for right in (False, True):
        r = rows if not right else [s[::-1] for s in rows]
        gw = max((len(s) for s in r), default=1)
        ox = x + 1 if not right else x + 7 - gw
        f.art(r, ox + look, y + dy)


# --------------------------------------------------------------------------- output
def save_gif(frames, path, durs):
    if isinstance(durs, int):
        durs = [durs] * len(frames)
    colors = {}
    for fr in frames:
        for row in fr.px:
            for c in row:
                if c is not None and c not in colors:
                    colors[c] = len(colors) + 1
    if len(colors) > 255:
        raise ValueError(f'{path}: too many colours ({len(colors)})')
    pal = [255, 0, 255]
    for c in colors:
        pal += list(c)
    pal += [0] * (768 - len(pal))
    imgs = []
    for fr in frames:
        data = bytes(colors[c] if c is not None else 0 for row in fr.px for c in row)
        im = Image.frombytes('P', (fr.w, fr.h), data)
        im.putpalette(pal)
        im = im.resize((fr.w * SCALE, fr.h * SCALE), Image.NEAREST)
        imgs.append(im)
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durs, loop=0,
                 transparency=0, disposal=2, optimize=False)


def sheet(frames, path, cols=8, cell=160, bg=(250, 250, 250)):
    rows = (len(frames) + cols - 1) // cols
    out = Image.new('RGB', (cols * cell, rows * cell), bg)
    for i, fr in enumerate(frames):
        im = fr.to_image().resize((cell, cell), Image.NEAREST)
        tile = Image.new('RGBA', (cell, cell), bg + (255,))
        tile.alpha_composite(im)
        out.paste(tile.convert('RGB'), ((i % cols) * cell, (i // cols) * cell))
    out.save(path)


# --------------------------------------------------------------------------- dotted backdrops
class Dotted:
    """Room backdrop in the style of the reference videos: thin line-art made of small square
    dots on a flat ground, 3 dots per Clawd pixel. Coordinates are logical pixels (floats ok).
    dark=True -> night rooms of videos 1-2; dark=False -> daytime rooms of video 3."""
    K = 3

    def __init__(self, dark=True, ink=None, ground=None):
        self.ground = ground or ((20, 20, 20) if dark else (242, 240, 234))
        self.ink = col(ink) if ink else ((92, 92, 92) if dark else (196, 194, 188))
        self.n = G * self.K
        self.cells = {}

    def dot(self, sx, sy, c=None):
        if 0 <= sx < self.n and 0 <= sy < self.n:
            self.cells[(int(sx), int(sy))] = col(c) if c else self.ink

    def line(self, x0, y0, x1, y1, c=None, gap=1):
        k = self.K
        a, b = (round(x0 * k), round(y0 * k)), (round(x1 * k), round(y1 * k))
        steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
        for i in range(0, steps + 1, gap + 1):
            self.dot(a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps, c)

    def rect(self, x, y, w, h, c=None, gap=1):
        self.line(x, y, x + w, y, c, gap); self.line(x, y + h, x + w, y + h, c, gap)
        self.line(x, y, x, y + h, c, gap); self.line(x + w, y, x + w, y + h, c, gap)

    def fill(self, x, y, w, h, c=None, step=2):
        k = self.K
        for sy in range(round(y * k), round((y + h) * k), step):
            for sx in range(round(x * k) + (sy // step) % 2, round((x + w) * k), step):
                self.dot(sx, sy, c)

    def ring(self, cx, cy, r, c=None):
        k = self.K
        for i in range(int(2 * math.pi * r * k / 2) + 1):
            a = i * 2 / (r * k)
            self.dot(round((cx + math.cos(a) * r) * k), round((cy + math.sin(a) * r) * k), c)

    def to_image(self, scale=SCALE):
        size = G * scale
        im = Image.new('RGB', (size, size), self.ground)
        px = im.load()
        cell = scale / self.K
        dot = max(1, int(round(cell * 0.7)))
        for (sx, sy), c in self.cells.items():
            x0, y0 = int(sx * cell), int(sy * cell)
            for yy in range(y0, min(size, y0 + dot)):
                for xx in range(x0, min(size, x0 + dot)):
                    px[xx, yy] = c
        return im


def compose(frames, backdrop=None, bg=None, scale=SCALE):
    """Flatten frames to RGB images: over a Dotted backdrop (static or fn(t, n)) or a solid bg."""
    out = []
    for t, fr in enumerate(frames):
        if backdrop is not None:
            d = backdrop(t, len(frames)) if callable(backdrop) else backdrop
            base = d.to_image(scale).convert('RGBA')
        else:
            base = Image.new('RGBA', (fr.w * scale, fr.h * scale), col(bg) + (255,) if bg else (0, 0, 0, 0))
        im = fr.to_image()
        if scale != SCALE:
            im = im.resize((fr.w * scale, fr.h * scale), Image.NEAREST)
        base.alpha_composite(im)
        out.append(base)
    return out


def save_rgb_gif(images, path, durs):
    """Save already-flattened RGB(A) images as an opaque GIF with one shared palette."""
    if isinstance(durs, int):
        durs = [durs] * len(images)
    rgb = [im.convert('RGB') for im in images]
    colors = {}
    for im in rgb:
        for _, c in im.getcolors(1 << 20):
            colors[c] = 1
    if len(colors) > 256:
        pal_src = rgb[0].quantize(256)
    else:
        pal_src = Image.new('P', (1, 1))
        flat = [v for c in colors for v in c]
        pal_src.putpalette(flat + [0] * (768 - len(flat)))
    frames = [im.quantize(palette=pal_src, dither=Image.Dither.NONE) for im in rgb]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=False)


# --------------------------------------------------------------------------- registry
REG = []


def add(slug, zh, en, fn, n=8, dur=160, backdrop=None, **kw):
    """Register one GIF: fn(f, t, n, **kw) draws frame t of n into canvas f.
    backdrop: optional Dotted (or fn(t, n) -> Dotted) used by render.py for opaque output."""
    REG.append(dict(slug=slug, zh=zh, en=en, fn=fn, n=n, dur=dur, kw=kw, backdrop=backdrop))


def beats(n, ms, hold=None):
    """Per-frame durations for add(dur=...): `ms` for each of the n frames, except `hold`
    {frame: ms} (a key may also be a tuple or range of frames). Use it to hold key poses
    (anticipation, contact, impact text, landing) ~300-600 ms while in-betweens stay short."""
    d = [ms] * n
    for k, v in (hold or {}).items():
        for i in (k if isinstance(k, (tuple, list, range)) else (k,)):
            d[i % n] = v
    return d


def render(entry):
    frames = []
    for t in range(entry['n']):
        f = Canvas()
        entry['fn'](f, t, entry['n'], **entry['kw'])
        frames.append(f)
    return frames


# --------------------------------------------------------------------------- in-betweens
# Clawd must never snap from one pose to a far one between two frames (front -> profile,
# arms side -> up, standing -> squashed...). tweened() finds those snaps and inserts short
# in-between frames whose clawd() poses lie halfway along the way (views step around the
# turn, arms pass through mid/high, sizes and positions interpolate in whole pixels).
_HOOK = []
VIEW_RING = ['front', 'qr', 'q2r', 'sr', 'back', 'sl', 'q2l', 'ql']
ARM_LINKS = [('low', 'side'), ('side', 'mid'), ('mid', 'high'), ('high', 'up'), ('up', 'wave'),
             ('high', 'wave'), ('down', 'low'), ('down', 'side'), ('side', 'out'), ('mid', 'reach'),
             ('reach', 'out'), ('reach', 'high'), ('side', 'short'), ('short', 'none'),
             ('short', 'front'), ('front', 'chin'), ('chin', 'face')]
EYE_STEPS = ['big', 'normal', 'blink', 'closed']


def _view_path(a, b):
    if a == b or a not in VIEW_RING or b not in VIEW_RING:
        return [a, b] if a != b else [a]
    i, j, m = VIEW_RING.index(a), VIEW_RING.index(b), len(VIEW_RING)
    d = (j - i) % m
    step = 1 if d < m - d else -1
    if d == m - d:  # half turn: go round through the front (turn towards the viewer)
        step = 1 if (0 - i) % m < d else -1
    path = [a]
    while i != j:
        i = (i + step) % m
        path.append(VIEW_RING[i])
    return path


def _arm_path(a, b):
    if a == b:
        return [a]
    nb = {}
    for p, q in ARM_LINKS:
        nb.setdefault(p, []).append(q)
        nb.setdefault(q, []).append(p)
    prev, todo = {a: None}, [a]
    while todo:
        cur = todo.pop(0)
        if cur == b:
            break
        for q in nb.get(cur, []):
            if q not in prev:
                prev[q] = cur
                todo.append(q)
    if b not in prev:
        return [a, b]
    path = [b]
    while path[-1] != a:
        path.append(prev[path[-1]])
    return path[::-1]


def _rd(v):
    return int(math.floor(v + 0.5))


def _along(path, u):
    return path[min(len(path) - 1, _rd(u * (len(path) - 1)))]


def _mix_pose(a, b, u):
    """clawd() kwargs a fraction u of the way from pose a to pose b."""
    near = a if u <= 0.5 else b
    m = dict(near)
    for k in ('x', 'y', 'w', 'h', 'leg_h', 'look', 'lookv', 'tilt'):
        if isinstance(a[k], (int, float)) and isinstance(b[k], (int, float)):
            m[k] = _rd(a[k] + (b[k] - a[k]) * u)
    for k in ('legs', 'legdx'):
        m[k] = tuple(_rd(p + (q - p) * u) for p, q in zip(a[k], b[k]))
    m['view'] = _along(_view_path(a['view'], b['view']), u)
    m['la'] = _along(_arm_path(a['la'], b['la']), u)
    m['ra'] = _along(_arm_path(a['ra'], b['ra']), u)
    for k in ('eyes', 'eyes_r'):
        if a[k] in EYE_STEPS and b[k] in EYE_STEPS:
            i, j = EYE_STEPS.index(a[k]), EYE_STEPS.index(b[k])
            m[k] = EYE_STEPS[_rd(i + (j - i) * u)]
    return m


def _poses(fn, t, n, kw):
    """clawd() kwargs of every call made while drawing frame t (in call order)."""
    calls = []

    def rec(p):
        calls.append(p)
        return p
    _HOOK.append(rec)
    try:
        fn(Canvas(), t, n, **kw)
    finally:
        _HOOK.remove(rec)
    return calls


def _on_canvas(p):
    return p['x'] + p['w'] > 1 and p['x'] < G - 1 and p['y'] + p['h'] > 1 and p['y'] < G - 1


def snap_steps(a, b):
    """How many in-betweens the jump from pose a to pose b needs (0 = it already flows)."""
    if not (_on_canvas(a) and _on_canvas(b)):
        return 0
    s = max(len(_view_path(a['view'], b['view'])), len(_arm_path(a['la'], b['la'])),
            len(_arm_path(a['ra'], b['ra']))) - 2
    size = abs(a['w'] - b['w']) + abs(a['h'] - b['h'])
    if size >= 3:
        s = max(s, 1 if size < 6 else 2)
    if isinstance(a['leg_h'], int) and isinstance(b['leg_h'], int) and abs(a['leg_h'] - b['leg_h']) >= 2:
        s = max(s, 1)
    if s and abs(a['y'] - b['y']) >= 8:
        s = max(s, 2)
    return max(0, min(2, s))


def find_snaps(fn, n, **kw):
    """{frame k: in-betweens needed between frame k and k+1 (k = n-1 is the loop seam)}."""
    P = [_poses(fn, t, n, kw) for t in range(n)]
    out = {}
    for k in range(n):
        a, b = P[k], P[(k + 1) % n]
        if n < 2 or len(a) != len(b):
            continue
        s = max((snap_steps(p, q) for p, q in zip(a, b)), default=0)
        if s:
            out[k] = s
    return out


def tweened(fn, n, dur=160, at='auto', ms=70, skip=(), **kw):
    """Insert in-between frames where Clawd would snap between poses.

        add('slug', zh, en, *tweened(scene, 16, 120), **scene_kw)

    Returns (fn2, n2, dur2) for add(). at='auto' detects snaps (find_snaps); or pass
    {k: steps} to put `steps` in-betweens after frame k. skip: frames k to leave as cuts.
    Each in-between lasts `ms` (keep it short: 60-100 ms); original frames keep `dur`
    (an int or a per-frame list). kw: the scene kwargs, needed only for at='auto'.
    """
    durs = list(dur) if isinstance(dur, (list, tuple)) else [dur] * n
    plan = find_snaps(fn, n, **kw) if at == 'auto' else dict(at)
    for k in skip:
        plan.pop(k, None)
    seq, d2 = [], []
    for k in range(n):
        seq.append((k, None))
        d2.append(durs[k])
        for i in range(plan.get(k, 0)):
            seq.append((k, (i + 1) / (plan[k] + 1)))
            d2.append(ms)

    def fn2(f, t, n2, **kw2):
        k, u = seq[t % len(seq)]
        if u is None:
            return fn(f, k, n, **kw2)
        k1 = (k + 1) % n
        a, b = _poses(fn, k, n, kw2), _poses(fn, k1, n, kw2)
        mids = [_mix_pose(p, q, u) for p, q in zip(a, b)]
        it = iter(mids)

        def sub(p):
            return next(it, p)
        _HOOK.append(sub)
        try:
            return fn(f, k if u <= 0.5 else k1, n, **kw2)
        finally:
            _HOOK.remove(sub)
    fn2.__name__ = getattr(fn, '__name__', 'scene') + '_tweened'
    fn2.plan = plan
    return fn2, len(seq), d2


def add_tweened(slug, zh, en, fn, n=8, dur=160, backdrop=None, tw_at='auto', tw_skip=(), tw_ms=70, **kw):
    """add() with in-between frames wherever Clawd would snap between poses (see tweened)."""
    fn2, n2, d2 = tweened(fn, n, dur, at=tw_at, ms=tw_ms, skip=tw_skip, **kw)
    add(slug, zh, en, fn2, n=n2, dur=d2, backdrop=backdrop, **kw)
