"""Video covers for the two Clawd films, plus the preview site's social card.

  python make_covers.py      # short_cover.png/.jpg, promo_cover.png/.jpg, og.png, and *_thumb.png checks

Short: the night station re-screened from its value map (films/tools/halftone.py, 9-px cells, round
dots), Clawd and the sprout from the engine at 24 px per Clawd px. Promo and og: a straight grid of cards,
one GIF keyframe each at an integer scale, rotated once as a sheet (supersampled), with the title straight
on top. Titles in the 5x7 pixel font (Clawd orange) and the 12-px simsun bitmap scaled by an integer.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
FILMS = os.path.join(HERE, '..')
ROOT = os.path.join(FILMS, '..')
sys.path.insert(0, os.path.join(FILMS, 'tools'))
from pixfilm import canvas_image  # noqa: E402  (also puts the Clawd engine on sys.path)
from engine import Canvas, clawd, BX, GROUND  # noqa: E402
import props as P  # noqa: E402
import halftone  # noqa: E402

W, H = 1920, 1080
CELL = 9
ORANGE = (227, 126, 82)
NIGHT_INK = (230, 226, 220)
DAY_INK = (20, 18, 14)
PAPER = (244, 242, 236)
BK = os.path.join(FILMS, 'backdrops')

# ----------------------------------------------------------------------------- type
FONT5x7 = {
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'I': ['.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'P': ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
    'X': ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
    'F': ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
    'G': ['.###.', '#...#', '#....', '#.###', '#...#', '#...#', '.####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '0': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
    '3': ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
    '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
    '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
    '6': ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
    '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
    '9': ['.###.', '#...#', '#...#', '.####', '....#', '...#.', '.##..'],
    ' ': ['.....'] * 7,
    '·': ['.....', '.....', '.....', '..#..', '.....', '.....', '.....'],
}


def pixel_word(text, scale, rgb=ORANGE, gap=1):
    """A word in the 5x7 pixel font, each font pixel a scale x scale square."""
    w = len(text) * (5 + gap) - gap
    im = Image.new('RGBA', (w, 7), (0, 0, 0, 0))
    px = im.load()
    for k, ch in enumerate(text):
        for r, row in enumerate(FONT5x7[ch]):
            for c, v in enumerate(row):
                if v == '#':
                    px[k * (5 + gap) + c, r] = rgb + (255,)
    return im.resize((w * scale, 7 * scale), Image.NEAREST)


def cjk(text, scale, rgb):
    """Chinese as the 12-px simsun bitmap (thresholded, no anti-aliasing), scaled by an integer."""
    font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 12)
    im = Image.new('L', (int(font.getlength(text)) + 2, 14), 0)
    ImageDraw.Draw(im).text((0, 0), text, font=font, fill=255)
    rgba = Image.new('RGBA', im.size, (0, 0, 0, 0))
    rgba.putdata([rgb + (255,) if v > 110 else (0, 0, 0, 0) for v in im.getdata()])
    rgba = rgba.crop(rgba.getbbox())
    return rgba.resize((rgba.width * scale, rgba.height * scale), Image.NEAREST)


# ----------------------------------------------------------------------------- backdrops
def value_map(path):
    return np.asarray(Image.open(path).convert('L'), np.float32) / 255


def screen(v, light):
    """Value map (cells) -> the films' round-dot halftone, cropped to 1920 x 1080."""
    im = halftone.render(np.clip(v, 0, 1), light=light).convert('RGB')
    full = Image.new('RGB', (W, H), im.getpixel((im.width - 1, im.height - 1)))
    full.paste(im.crop((0, 0, min(W, im.width), min(H, im.height))), (0, 0))
    return full


def cells_box(x0, y0, x1, y1):
    """Screen px box -> cell slice."""
    return slice(y0 // CELL, -(-y1 // CELL)), slice(x0 // CELL, -(-x1 // CELL))


# ----------------------------------------------------------------------------- Clawd
SIZES = {'n': (16, 12, 0), 'sq': (18, 10, -1), 'st': (14, 14, 1)}


def pose(S, x, feet, size='n', leg_h=3, **kw):
    """Clawd with his body's left edge at screen x and feet on screen y, S screen px per Clawd px."""
    f = Canvas()
    w, h, dx = SIZES[size]
    info = clawd(f, x=BX + dx, y=GROUND - leg_h - h, w=w, h=h, leg_h=leg_h, **kw)
    return f, x - BX * S, feet - GROUND * S, info


def potted(stage):
    a = P.sprout_art(stage)
    n = len(a)
    c = Canvas(12, n + 5)
    for r, row in enumerate(a):
        c.art([row], 2, r)
    c.art(P.POT, 2, n)
    return c, n + 5


def paste(img, c, S, ox, oy):
    spr = canvas_image(c).resize((c.w * S, c.h * S), Image.NEAREST)
    img.alpha_composite(spr, (int(ox), int(oy)))


def clawd_with_pot(img, S, x, feet, stage=1, **kw):
    f, ox, oy, info = pose(S, x, feet, ra='front', **kw)
    paste(img, f, S, ox, oy)
    hx, hy = info['rh']
    c, h = potted(stage)
    paste(img, c, S, ox + (hx - 2) * S, oy + (hy + 3 - h) * S)


# ----------------------------------------------------------------------------- short
def short_cover():
    S = 24
    v = value_map(os.path.join(BK, 'iteration-3', 'scenes', 'station_night_value.png'))
    from scipy.ndimage import uniform_filter
    wgt = np.full_like(v, 0.55)                                  # the station steps back...
    wgt[cells_box(1060, 40, 1920, 480)] = 0.2                    # quiet behind the title
    wgt[cells_box(1420, 540, 1840, 720)] = 0.35                  # the station sign, not a second title
    wgt = uniform_filter(wgt, 5, mode='nearest')                 # soft edges, no boxes
    wgt[cells_box(1005, 515, 1300, 630)] = 1.0                   # ...except the clock: 23:59
    img = screen(v * wgt, light=False).convert('RGBA')

    clawd_with_pot(img, S, 230, 1010, stage=2, view='q2r', eyes='normal', lookv=-1)

    en = pixel_word('CLAWD', 12)
    zh = cjk('末班车', 16, NIGHT_INK)
    sub = pixel_word('THE LAST TRAIN', 5, NIGHT_INK)
    right = 1810
    img.alpha_composite(en, (right - en.width, 96))
    img.alpha_composite(zh, (right - zh.width, 96 + en.height + 36))
    img.alpha_composite(sub, (right - sub.width, 96 + en.height + 36 + zh.height + 36))
    return img.convert('RGB')


# ----------------------------------------------------------------------------- promo: a tilted wall of Clawds
BODY = {(227, 126, 82), (197, 112, 71), (160, 84, 52), (0, 0, 0)}
FRAME_INK = (12, 10, 5)
CARD = (251, 250, 246)


def keyframes():
    """One frame per GIF (40 x 40 RGBA, cropped to its content) — of the frames where Clawd is fully in
    view, the one with the most going on — plus what the wall needs to spread them out: theme, the
    props' dominant hue (None when they are grey/black) and how much of it is dark."""
    import colorsys
    man = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
    out = []
    for it in man:
        cand = []
        for fr in ImageSequence.Iterator(Image.open(os.path.join(ROOT, it['file']))):
            im = fr.convert('RGBA').resize((40, 40), Image.NEAREST)
            a = np.asarray(im)
            op = a[..., 3] > 0
            cols = list(map(tuple, a[..., :3][op]))
            props = [c for c in cols if c not in BODY]
            orange = np.isin(a[..., :3].reshape(-1, 3) @ np.array([65536, 256, 1]), [227 * 65536 + 126 * 256 + 82, 197 * 65536 + 112 * 256 + 71]).reshape(40, 40) & op
            ys, xs = np.nonzero(orange)
            upright = len(xs) > 0 and (xs.max() - xs.min()) >= (ys.max() - ys.min())   # not mid-flip
            cand.append((len(props) * 3 + int(op.sum()), len(cols) - len(props), im, props, upright))
        most = max(c[1] for c in cand)
        ok = [c for c in cand if c[1] >= 0.85 * most]
        ok = [c for c in ok if c[4]] or ok
        _, _, im, props, _ = max(ok, key=lambda c: c[0])
        hue = None
        if len(props) >= 6:
            hsv = np.array([colorsys.rgb_to_hsv(*(np.array(c) / 255)) for c in props])
            w = hsv[:, 1] * hsv[:, 2]
            if w.mean() > 0.18:
                ang = hsv[:, 0] * 2 * np.pi
                hue = (np.arctan2((w * np.sin(ang)).sum(), (w * np.cos(ang)).sum()) / (2 * np.pi)) % 1
        dark = sum(1 for c in props if sum(c) < 200) / 1600
        out.append(dict(n=it['n'], theme=it['theme'], im=im.crop(im.getbbox()), props=len(props), hue=hue, dark=dark))
    return out


def hue_gap(a, b):
    if a is None or b is None:
        return 0.15 if (a is None) != (b is None) else 0.0
    d = abs(a - b) % 1
    return min(d, 1 - d)


def pick(frames, n, seed):
    """n keyframes, themes in proportion; within a theme the most colourful, most different in hue,
    few dark-heavy ones."""
    rng = np.random.default_rng(seed)
    themes = []
    for f in frames:
        if f['theme'] not in themes:
            themes.append(f['theme'])
    size = {t: sum(f['theme'] == t for f in frames) for t in themes}
    quota = {t: max(3, round(n * size[t] / len(frames))) for t in themes}
    while sum(quota.values()) > n:
        quota[max(quota, key=quota.get)] -= 1
    while sum(quota.values()) < n:
        quota[max(themes, key=lambda t: size[t] - quota[t])] += 1
    chosen = []
    for t in themes:
        pool = [f for f in frames if f['theme'] == t]
        mine = []
        for _ in range(min(quota[t], len(pool))):
            def score(f):
                spread = min([hue_gap(f['hue'], g['hue']) for g in mine] or [0.5])
                return f['props'] / 60 + spread * 6 - f['dark'] * 40 + rng.random() * 0.8
            mine.append(max((f for f in pool if f not in mine), key=score))
        chosen += mine
    return chosen


def arrange(tiles, cols, rows, seed):
    """Fill the grid row by row, each cell taking the tile that differs most from its neighbours
    (theme and hue), so themes and colours spread evenly."""
    rng = np.random.default_rng(seed)
    left = list(tiles)
    grid = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            nb = [grid[r][c - 1] if c else None, grid[r - 1][c] if r else None,
                  grid[r - 1][c - 1] if r and c else None, grid[r - 1][c + 1] if r and c + 1 < cols else None,
                  grid[r][c - 2] if c > 1 else None, grid[r - 2][c] if r > 1 else None]
            nb = [x for x in nb if x]

            def score(f):
                return sum((f['theme'] != g['theme']) * 2 + hue_gap(f['hue'], g['hue']) * 6 for g in nb) + rng.random()
            grid[r][c] = max(left, key=score)
            left.remove(grid[r][c])
    return grid


def wall(w, h, frames, s, pad, gap, angle, seed, ss=2):
    """A straight grid of cards (a keyframe at s px per Clawd px, centred on each card), rotated as one
    sheet by `angle` degrees counter-clockwise and cropped to w x h. Drawn at ss x and scaled down, so the
    rotated pixel edges come out clean."""
    card = 40 * s + 2 * pad
    pitch = card + gap
    th = np.radians(abs(angle))
    need_w, need_h = w * np.cos(th) + h * np.sin(th), w * np.sin(th) + h * np.cos(th)
    cols, rows = int(np.ceil(need_w / pitch)) + 1, int(np.ceil(need_h / pitch)) + 1
    grid = arrange(pick(frames, cols * rows, seed), cols, rows, seed)
    q = s * ss
    big = Image.new('RGB', (cols * pitch * ss, rows * pitch * ss), PAPER)
    d = ImageDraw.Draw(big)
    for r in range(rows):
        for c in range(cols):
            x, y = (c * pitch + gap // 2) * ss, (r * pitch + gap // 2) * ss
            d.rectangle([x, y, x + card * ss - 1, y + card * ss - 1], fill=CARD)
            t = grid[r][c]['im']
            g = t.resize((t.width * q, t.height * q), Image.NEAREST)
            gx = x + pad * ss + (40 - t.width) // 2 * q              # centred on whole Clawd pixels
            gy = y + pad * ss + (40 - t.height) // 2 * q
            big.paste(g, (gx, gy), g)
    big = big.rotate(angle, resample=Image.BICUBIC, fillcolor=PAPER)
    cx, cy = big.width // 2, big.height // 2
    big = big.crop((cx - w * ss // 2, cy - h * ss // 2, cx + w * ss // 2, cy + h * ss // 2))
    return big.resize((w, h), Image.LANCZOS).convert('RGBA'), cols * rows


def dotted_frame(img, box, ink=FRAME_INK):
    """The promo's frame: a row of round dots on the 9-px cell grid around box, Clawd-orange corners."""
    d = ImageDraw.Draw(img)
    c0, r0, c1, r1 = box[0] // CELL, box[1] // CELL, box[2] // CELL, box[3] // CELL
    pts = [(c, r0) for c in range(c0, c1 + 1)] + [(c1, r) for r in range(r0 + 1, r1 + 1)]
    pts += [(c, r1) for c in range(c1 - 1, c0 - 1, -1)] + [(c0, r) for r in range(r1 - 1, r0, -1)]
    for c, r in pts:
        cx, cy = c * CELL + 4.5, r * CELL + 4.5
        d.ellipse([cx - 2.7, cy - 2.7, cx + 2.7, cy + 2.7], fill=ink)
    for c, r in ((c0, r0), (c1, r0), (c0, r1), (c1, r1)):
        d.rectangle([c * CELL, r * CELL, c * CELL + 8, r * CELL + 8], fill=ORANGE)


def title_block(n_scale, en_scale, zh_scale, gap):
    """'400' / CLAWD / 400 个像素动图, centred in one RGBA block."""
    big = pixel_word('400', n_scale)
    en = pixel_word('CLAWD', en_scale)
    zh = cjk('400 个像素动图', zh_scale, DAY_INK)
    w = max(big.width, en.width, zh.width)
    h = big.height + gap + en.height + gap + zh.height
    blk = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    y = 0
    for part in (big, en, zh):
        blk.alpha_composite(part, ((w - part.width) // 2, y))
        y += part.height + gap
    return blk


def title_panel(img, title, pad, tag_scale):
    """The title, straight, on a paper panel in the middle: the promo's dotted frame and a 开源 label."""
    w, h = img.size
    tx, ty = (w - title.width) // 2, (h - title.height) // 2
    box = (tx - pad, ty - pad, tx + title.width + pad, ty + title.height + pad)
    box = (box[0] // CELL * CELL, box[1] // CELL * CELL, -(-box[2] // CELL) * CELL, -(-box[3] // CELL) * CELL)
    m = 2 * CELL
    ImageDraw.Draw(img).rectangle([box[0] - m, box[1] - m, box[2] + CELL + m - 1, box[3] + CELL + m - 1], fill=PAPER)
    dotted_frame(img, box)
    img.alpha_composite(title, (tx, ty))
    tag = cjk('开源', tag_scale, PAPER)
    k = 2 * tag_scale
    lab = Image.new('RGBA', (tag.width + 2 * k, tag.height + 2 * k), DAY_INK + (255,))
    lab.alpha_composite(tag, (k, k))
    img.alpha_composite(lab, (box[2] - 3 * CELL - lab.width, box[1] + 4 - lab.height // 2))


def promo_cover(frames):
    img, n = wall(W, H, frames, s=6, pad=12, gap=26, angle=15, seed=4)
    title_panel(img, title_block(28, 14, 5, 34), 44, 3)
    print('promo cover: wall of', n, 'tiles')
    return img.convert('RGB')


def og_card(frames):
    """The site's social card, 1200 x 630: the same wall, a size down."""
    img, n = wall(1200, 630, frames, s=4, pad=10, gap=18, angle=15, seed=9)
    title_panel(img, title_block(16, 8, 3, 18), 26, 2)
    print('og: wall of', n, 'tiles')
    return img.convert('RGB')


def save(img, name):
    img.save(os.path.join(HERE, name + '.png'))
    if img.size == (W, H):
        img.save(os.path.join(HERE, name + '.jpg'), quality=90, subsampling=0)
    img.resize((320, round(320 * img.height / img.width)), Image.LANCZOS).save(os.path.join(HERE, name + '_thumb.png'))


def main():
    save(short_cover(), 'short_cover')
    frames = keyframes()
    save(promo_cover(frames), 'promo_cover')
    save(og_card(frames), 'og')
    print('ok')


if __name__ == '__main__':
    main()
