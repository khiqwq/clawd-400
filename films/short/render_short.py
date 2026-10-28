"""Clawd short film "末班车 / The Last Train" — rendered the reference videos' way: static halftone rooms,
Clawd animating in them, the next room rising from below to change scenes.

  python render_short.py --frames 1.0 7.5 13.2 27.0      # stills to previews/
  python render_short.py                                  # out/short_silent.mp4 (score.py adds the sound)

Scenes (1920 x 1080 halftone backdrops from films/backdrops, clawd-halftone skill):
  A  station_night (+ the 00:00 clock)   0.0 – 6.4   Clawd waits with the sprout; midnight; hops aboard
  B  carriage_night                      6.4 – 19.4  moonlight: the sprout leans, he lifts it to the moon,
                                                     it grows a leaf; he dozes off
  C  hilltop (day, layered, sun rises)   19.4 – 34.5 he climbs the path, plants it; sunrise, it blooms
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FILMS = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(FILMS, 'tools'))
from pixfilm import canvas_image  # noqa: E402  (also puts the Clawd engine on sys.path)
from engine import Canvas, clawd, BX, GROUND  # noqa: E402
import props as P  # noqa: E402
import halftone  # noqa: E402

W, H, FPS = 1920, 1080, 30
S = 14                                 # screen px per Clawd pixel
DUR = 34.5
SLIDE = 0.36                           # the videos' room change: ~0.3 s, the next room rises from below
BK = os.path.join(FILMS, 'backdrops')
ORANGE = (227, 126, 82)

T = dict(
    bell=2.6, walk=3.2, crouch=4.25, hop=4.4, landed=4.75, wave=5.2, B=6.4,
    put=7.2, lean=10.5, notice=11.3, stand=12.0, lift=12.35, grow=13.0, lower=13.8, sit=14.3,
    doze=16.0, C=19.4, enter=19.9, top=25.6, kneel=25.8, plant=26.0, sunrise=26.3, risen=29.3,
    bloom=(27.2, 28.0, 28.8), happy=29.3, title=30.2,
)

# ----------------------------------------------------------------------------- backdrops
def load_rgb(p):
    im = Image.open(p).convert('RGB')
    full = Image.new('RGB', (W, H), im.getpixel((W - 1, H - 1)))
    full.paste(im.crop((0, 0, min(W, im.width), min(H, im.height))), (0, 0))
    return full


STATION = load_rgb(os.path.join(BK, 'iteration-3', 'scenes', 'station_night.png'))
STATION0 = load_rgb(os.path.join(BK, 'iteration-3', 'scenes', 'station_night_0000.png'))
CARRIAGE = load_rgb(os.path.join(BK, 'iteration-3', 'scenes', 'carriage_night.png'))
HB = np.asarray(Image.open(os.path.join(BK, 'hilltop', 'hilltop_back_value.png')).convert('L'), np.float32) / 255
HS = np.asarray(Image.open(os.path.join(BK, 'hilltop', 'hilltop_sun_value.png')).convert('L'), np.float32) / 255
HF = np.asarray(Image.open(os.path.join(BK, 'hilltop', 'hilltop_front_value.png')).convert('L'), np.float32) / 255
HM = np.asarray(Image.open(os.path.join(BK, 'hilltop', 'hilltop_front_mask.png')).convert('L'), np.float32) / 255
rows, cols = HB.shape
HMc = np.pad(HM, ((0, rows * 9 - HM.shape[0]), (0, cols * 9 - HM.shape[1])), mode='edge').reshape(rows, 9, cols, 9).mean(axis=(1, 3)) > 0.5
_hill_cache = {}


def hilltop(sun_dy_cells):
    """Back, then the sun shifted up by whole cells (hidden behind the hill by the front mask), then the hill."""
    if sun_dy_cells not in _hill_cache:
        sun = np.zeros_like(HS)
        k = sun_dy_cells                          # > 0: up, < 0: down (behind the hill)
        if k >= 0:
            sun[:rows - k] = HS[k:]
        else:
            sun[-k:] = HS[:rows + k]
        v = np.maximum(HB, sun)
        v = np.where(HMc, HF, v)
        _hill_cache[sun_dy_cells] = halftone.render(v, light=True).crop((0, 0, W, H)).convert('RGB')
    return _hill_cache[sun_dy_cells]


def sun_cells(t):
    u = (t - T['sunrise']) / (T['risen'] - T['sunrise'])
    u = min(1.0, max(0.0, u))
    u = u * u * (3 - 2 * u)
    return int(round(-26 + u * (26 + 29)))  # from behind the hill (y ~794) up to y ~299, a cell at a time


# ----------------------------------------------------------------------------- Clawd + props
SIZES = {'n': (16, 12, 0), 'nod': (16, 11, 0), 'sq': (18, 10, -1), 'sq2': (20, 9, -2), 'st': (14, 14, 1)}


def pose(x, feet, size='n', leg_h=3, **kw):
    """Clawd with his body's left edge at screen x and feet on screen y. Returns (Canvas, ox, oy, info)."""
    f = Canvas()
    w, h, dx = SIZES[size]
    info = clawd(f, x=BX + dx, y=GROUND - leg_h - h, w=w, h=h, leg_h=leg_h, **kw)
    ox, oy = x - BX * S, feet - GROUND * S
    return f, ox, oy, info


def potted(stage, lean=0):
    a = P.sprout_art(stage)
    n = len(a)
    c = Canvas(12, n + 5)
    for r, row in enumerate(a):
        shift = 0 if lean == 0 else round(lean * (n - 1 - r) / max(1, n - 1))
        c.art([row], 2 + shift, r)
    c.art(P.POT, 2, n)
    return c, n + 5                               # canvas, height in Clawd px


def stage_of(t):
    if t < T['grow']:
        return 1
    st = 2
    for k, tb in enumerate(T['bloom']):
        if t >= tb:
            st = 3 + min(k, 1)
    return st


def walk(t, rate=0.13):
    s = int(t / rate) % 2
    return ((1, 0, 1, 0) if s else (0, 1, 0, 1)), s


def landing(u):
    return 'sq2' if u < 0.07 else 'sq' if u < 0.17 else 'n'


def seg(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else (t - a) / (b - a)


def arc(t, a, b, p0, p1, h):
    u = seg(t, a, b)
    x = p0[0] + (p1[0] - p0[0]) * u
    y = p0[1] + (p1[1] - p0[1]) * u - 4 * (h + abs(p1[1] - p0[1]) / 2) * u * (1 - u)
    return x, y


PATH = [(0, 975), (400, 960), (700, 885), (950, 765), (1150, 675), (1420, 657), (1920, 657)]


def path_y(x):
    for (x0, y0), (x1, y1) in zip(PATH, PATH[1:]):
        if x <= x1:
            u = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * max(0, u)
    return PATH[-1][1]


def sprites(t):
    """Everything drawn with the Clawd engine at time t: [(Canvas, ox, oy, clip_rect_or_None, scene)]."""
    out = []
    st = stage_of(t)

    def with_pot(info, ox, oy, side='r'):
        hx, hy = info['rh'] if side == 'r' else info['lh']
        c, h = potted(st)
        px = ox + (hx - (2 if side == 'r' else 8)) * S
        py = oy + (hy + 3 - h) * S
        return (c, px, py)

    # ---------------- A: the station
    if t < T['B'] + SLIDE:
        sc = 'A'
        clip = None
        if t < T['walk']:
            startled = T['bell'] + 0.1 < t < T['bell'] + 0.55
            eyes = 'blink' if 1.45 < t < 1.6 else 'big' if startled else 'normal'
            f, ox, oy, info = pose(260, 975, view='q2r', eyes=eyes, lookv=-1 if t > T['bell'] + 0.55 else 0, ra='front')
        elif t < T['crouch']:
            k = t - T['walk']
            x = 260 + (560 - 260) * seg(t, T['walk'], T['crouch'] - 0.05)
            legs, s = walk(k)
            f, ox, oy, info = pose(round(x / 2) * 2, 975 + s * 7, view='q2r', eyes='focus', legs=legs, ra='front')
        elif t < T['hop']:
            f, ox, oy, info = pose(560, 975, size='sq', view='q2r', eyes='focus', ra='front')
        elif t < T['landed']:
            x, y = arc(t, T['hop'], T['landed'], (560, 975), (572, 765), 40)
            f, ox, oy, info = pose(round(x), round(y), size='st', view='q2r', eyes='focus', legs=(1, 1, 1, 1), ra='front')
        else:
            u = t - T['landed']
            clip = (594, 378, 774, 765)               # inside the doorway: the frame cuts him
            view = 'q2r' if u < 0.12 else 'qr' if u < 0.24 else 'front'
            waving = t > T['wave']
            ra = ('wave' if int((t - T['wave']) / 0.22) % 2 else 'up') if waving else 'side'
            f, ox, oy, info = pose(572, 765, size=landing(u) if u < 0.2 else 'n', view=view,
                                   eyes='happy' if waving else 'normal', la='front', ra=ra)
            out.append((f, ox, oy, clip, sc))
            c, px, py = with_pot(info, ox, oy, 'l')
            out.append((c, px, py, clip, sc))
            return out
        out.append((f, ox, oy, clip, sc))
        out.append(with_pot(info, ox, oy) + (clip, sc))
        return out

    # ---------------- B: the carriage (Clawd on the left bench: body x 110-335, seat top 840)
    if t < T['C'] + SLIDE:
        sc = 'B'
        seat_feet = 840 + 2 * S
        pot_on_table = (455, 711)                     # pot's left edge, table top
        lean = 0
        if T['lean'] <= t < T['stand']:
            lean = -1 if t < T['lean'] + 0.4 else -2
        if t < T['put']:
            f, ox, oy, info = pose(110, seat_feet, leg_h=2, view='q2r', eyes='normal', ra='front')
            out.append((f, ox, oy, None, sc)); out.append(with_pot(info, ox, oy) + (None, sc))
            return out
        if t < T['stand']:
            k = t - T['put']
            eyes, ra, lookv, look, size = 'normal', 'side', -1, 0, 'n'
            if k < 0.3:
                ra, lookv, look = 'reach', 1, 1
            elif t < T['lean']:
                eyes = 'blink' if 9.2 < t < 9.35 else 'normal'
            elif t < T['notice']:
                lookv = -1
            elif t < T['notice'] + 0.45:
                eyes, lookv, look = 'big', 0, 1
            else:
                eyes, lookv, look = 'happy', 0, 1
            f, ox, oy, info = pose(110, seat_feet, size=size, leg_h=2, view='q2r', eyes=eyes, ra=ra, look=look, lookv=lookv)
            out.append((f, ox, oy, None, sc))
            c, h = potted(st, lean)
            out.append((c, pot_on_table[0] - 2 * S, pot_on_table[1] - h * S, None, sc))
            return out
        if t < T['sit']:
            # stands on the bench, lifts the sprout up into the moonlight, lowers it back
            if t < T['lift']:
                f, ox, oy, info = pose(120, 840, size='st', view='q2r', eyes='happy', ra='reach')
                c, h = potted(st)
                out.append((f, ox, oy, None, sc)); out.append((c, pot_on_table[0] - 2 * S, pot_on_table[1] - h * S, None, sc))
                return out
            up = seg(t, T['lift'], T['lift'] + 0.35) * (1 - seg(t, T['lower'], T['sit']))
            tilt = 1 if T['grow'] <= t < T['lower'] else 0
            f, ox, oy, info = pose(120, 840, view='qr', eyes='happy' if t > T['grow'] else 'big', tilt=tilt,
                                   la='up' if up > 0.6 else 'high', ra='up' if up > 0.6 else 'high')
            out.append((f, ox, oy, None, sc))
            c, h = potted(st)
            hx, hy = info['rh']
            px = ox + (hx - 3) * S
            py = oy + (hy - h + 1) * S - round(up * 2) * S
            out.append((c, px, py, None, sc))
            if T['grow'] <= t < T['grow'] + 0.5:
                sp = Canvas(16, 14); P.sparkles(sp, int((t - T['grow']) / 0.1), 4, [(2, 4), (12, 2), (8, 11)])
                out.append((sp, px - 2 * S, py - 8 * S, None, sc))
            return out
        # back on the bench, the pot on the table; content, then dozing
        k = t - T['sit']
        eyes, size = 'happy', 'n'
        if k < 0.2:
            size = 'sq'
        elif t < T['doze'] - 0.4:
            eyes = 'happy' if t < 15.0 else 'closed'
        elif t < T['doze']:
            eyes = 'blink'
        else:
            eyes = 'closed'
            if t > T['doze'] + 0.4:
                size = 'nod' if int((t - T['doze'] - 0.4) / 0.8) % 2 == 0 else 'n'
        f, ox, oy, info = pose(110, seat_feet, size=size, leg_h=2, view='q2r', eyes=eyes)
        out.append((f, ox, oy, None, sc))
        c, h = potted(st)
        out.append((c, pot_on_table[0] - 2 * S, pot_on_table[1] - h * S, None, sc))
        if t > T['doze'] + 0.6:
            z = Canvas(20, 22)
            P.zzz(z, {'head': (4, 20)}, int((t - T['doze']) / 0.2), 12, c='G')
            hx, hy = info['head']
            out.append((z, ox + (hx - 4) * S, oy + (hy - 20) * S, None, sc))
        return out

    # ---------------- C: the hilltop at sunrise (day)
    sc = 'C'
    if t < T['top']:
        k = t - T['enter']
        x = -240 + (1060 + 240) * seg(t, T['enter'], T['top'])
        legs, s = walk(max(0, k), 0.14)
        feet = path_y(x + 112)
        f, ox, oy, info = pose(round(x / 2) * 2, round(feet) + s * 7, view='q2r', eyes='focus' if t < 24 else 'normal', legs=legs, ra='front')
        out.append((f, ox, oy, None, sc)); out.append(with_pot(info, ox, oy) + (None, sc))
        return out
    X, Y = 1060, 657
    if t < T['plant']:
        f, ox, oy, info = pose(X, Y, size='sq' if t > T['kneel'] else 'n', view='q2r', eyes='normal', ra='front')
        out.append((f, ox, oy, None, sc)); out.append(with_pot(info, ox, oy) + (None, sc))
        return out
    k = t - T['plant']
    eyes = 'normal' if t < T['sunrise'] + 0.6 else 'big' if t < T['bloom'][0] else 'happy'
    tilt = 1 if t > T['happy'] else 0
    view = 'q2r' if k < 0.3 else 'qr'
    f, ox, oy, info = pose(X, Y, size='sq' if k < 0.3 else 'n', view=view, eyes=eyes, tilt=tilt,
                           lookv=-1 if tilt else 1, ra='low' if k < 0.3 else 'side')
    out.append((f, ox, oy, None, sc))
    c, h = potted(st)
    out.append((c, 1310 - 2 * S, Y - h * S, None, sc))
    for tb in T['bloom']:
        if tb <= t < tb + 0.45:
            sp = Canvas(16, 14); P.sparkles(sp, int((t - tb) / 0.1), 4, [(2, 4), (12, 2), (8, 11)])
            out.append((sp, 1310 - 4 * S, Y - (h + 9) * S, None, sc))
    return out


# ----------------------------------------------------------------------------- overlays
FONT = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 26)
TRACK = 'Happy, but a little off  —  HoliznaCC0        '


def tag(img, t, day):
    d = ImageDraw.Draw(img)
    if not day:
        d.rectangle((1322, 38, 1862, 106), fill=(27, 27, 27))
    nc = ORANGE if day else (226, 226, 226)
    d.ellipse([1346, 76, 1356, 86], fill=nc); d.ellipse([1362, 72, 1372, 82], fill=nc)
    d.rectangle([1353, 56, 1356, 80], fill=nc); d.rectangle([1369, 52, 1372, 76], fill=nc); d.rectangle([1353, 52, 1372, 57], fill=nc)
    w = int(FONT.getlength(TRACK))
    strip = Image.new('RGBA', (w, 40), (0, 0, 0, 0))
    ImageDraw.Draw(strip).text((0, 4), TRACK, font=FONT, fill=(20, 18, 14) if day else (226, 226, 226))
    off = int(t * 38) % w
    win = Image.new('RGBA', (450, 40), (0, 0, 0, 0))
    win.alpha_composite(strip, (-off, 0)); win.alpha_composite(strip, (w - off, 0))
    img.alpha_composite(win, (1392, 52))


TITLE_EN = Image.open(os.path.join(HERE, 'assets', 'title_en.png')).convert('RGBA')
TITLE_ZH = Image.open(os.path.join(HERE, 'assets', 'title_zh.png')).convert('RGBA')
_zh = np.asarray(TITLE_ZH).copy(); _zh[..., :3] = (20, 18, 14)        # ink on the day sky
TITLE_ZH = Image.fromarray(_zh)


def title(img, t):
    u = seg(t, T['title'], T['title'] + 0.5)
    if u <= 0:
        return
    rise = round((1 - u) ** 2 * 3) * S                                  # drops in by whole Clawd pixels
    a = TITLE_EN.copy(); a.putalpha(Image.fromarray((np.asarray(a.getchannel('A')) * u).astype(np.uint8)))
    img.alpha_composite(a, (240, 372 - rise))
    u2 = seg(t, T['title'] + 0.4, T['title'] + 0.9)
    if u2 > 0:
        b = TITLE_ZH.copy(); b.putalpha(Image.fromarray((np.asarray(b.getchannel('A')) * u2).astype(np.uint8)))
        img.alpha_composite(b, (248, 520))


# ----------------------------------------------------------------------------- frames
def scene_image(sc, t):
    if sc == 'A':
        return STATION0 if t >= T['bell'] else STATION
    if sc == 'B':
        return CARRIAGE
    return hilltop(sun_cells(t))


def slide_offsets(t):
    """y offsets for (scene, offset) pairs on screen at t."""
    for a, b, tb in (('A', 'B', T['B']), ('B', 'C', T['C'])):
        if tb <= t < tb + SLIDE:
            u = (t - tb) / SLIDE
            e = u * u * (3 - 2 * u)
            return [(a, -round(e * H)), (b, H - round(e * H))]
    sc = 'A' if t < T['B'] else 'B' if t < T['C'] else 'C'
    return [(sc, 0)]


def frame(t):
    img = Image.new('RGBA', (W, H), (19, 19, 19, 255))
    shown = slide_offsets(t)
    sprite_list = sprites(t)
    for sc, dy in shown:
        img.paste(scene_image(sc, t), (0, dy))
        for c, ox, oy, clip, ssc in sprite_list:
            if ssc != sc:
                continue
            spr = canvas_image(c).resize((c.w * S, c.h * S), Image.NEAREST)
            if clip:
                x0, y0, x1, y1 = clip
                m = Image.new('L', spr.size, 0)
                ImageDraw.Draw(m).rectangle((x0 - ox, y0 - oy, x1 - ox - 1, y1 - oy - 1), fill=255)
                a = Image.fromarray(np.minimum(np.asarray(spr.getchannel('A')), np.asarray(m)))
                spr.putalpha(a)
            img.alpha_composite(spr, (int(ox), int(oy) + dy))
    day = t >= T['C'] + SLIDE / 2
    tag(img, t, day)
    title(img, t)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', nargs='*', type=float)
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'previews'), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    if a.frames:
        for t in a.frames:
            frame(t).convert('RGB').save(os.path.join(HERE, 'previews', f'f_{t:05.2f}.png'))
        print('stills written')
        return
    out = os.path.join(HERE, 'out', 'short_silent.mp4')
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n = int(round(DUR * FPS))
    for i in range(n):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    json.dump({'T': T, 'dur': DUR, 'slide': SLIDE}, open(os.path.join(HERE, 'out', 'timeline.json'), 'w'), indent=1)
    print(out)


if __name__ == '__main__':
    main()
