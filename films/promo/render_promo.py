"""Promo: every GIF gets a little scene — it plays in a backdrop at the videos' scale, a frame draws on
around it, it loops twice inside the frame, then a cut to the next GIF.

  python render_promo.py --only 1-6 --out test.mp4        # a few vignettes, for checking
  python render_promo.py --out promo_video.mp4 --jobs 6    # all 400 (silent; mix_promo.py adds music)

Backdrops: backdrops.json maps theme -> {png, theme: dark|light}; one halftone PNG per theme, reused.
"""
import argparse
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
FPS = 30
W, H = 1920, 1080
SCALE = 14                       # screen px per Clawd pixel (the videos: 13.9)
FEET_Y = 975                     # Clawd's feet on the floor line
CELL = 9
ORANGE = (227, 126, 82)
DOT = {'dark': (221, 217, 215), 'light': (12, 10, 5)}
GROUND = {'dark': (19, 19, 19), 'light': (244, 242, 236)}
FRAME_IN = 0.45                  # seconds for the frame to draw on
MIN_INTRO = 1.4                  # the GIF plays at least this long before it is framed


def load_manifest():
    return json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))


def gif_frames(path):
    im = Image.open(path)
    out = []
    for fr in ImageSequence.Iterator(im):
        out.append((fr.convert('RGBA').resize((40, 40), Image.NEAREST), fr.info.get('duration', 100) / 1000))
    return out


def plan(frames):
    """Timing of one vignette: intro loops (whole loops, >= MIN_INTRO), then two framed loops."""
    L = sum(d for _, d in frames)
    n_intro = max(1, math.ceil(MIN_INTRO / L - 1e-6))
    return L, n_intro * L, n_intro * L + 2 * L


def frame_at(frames, L, u):
    u = u % L
    for im, d in frames:
        if u < d:
            return im
        u -= d
    return frames[-1][0]


def content_box(frames):
    """Union bbox of the GIF's visible pixels over all frames (Clawd px), padded by 1."""
    x0 = y0 = 40; x1 = y1 = 0
    for im, _ in frames:
        b = im.getbbox()
        if b:
            x0, y0, x1, y1 = min(x0, b[0]), min(y0, b[1]), max(x1, b[2]), max(y1, b[3])
    return max(0, x0 - 1), max(0, y0 - 1), min(40, x1 + 1), min(40, y1 + 1)


def dotted_rect_points(x0, y0, x1, y1):
    """Cell-grid points along a rectangle, clockwise from the top-left (for the draw-on)."""
    c0, r0, c1, r1 = x0 // CELL, y0 // CELL, x1 // CELL, y1 // CELL
    pts = [(c, r0) for c in range(c0, c1 + 1)] + [(c1, r) for r in range(r0 + 1, r1 + 1)]
    pts += [(c, r1) for c in range(c1 - 1, c0 - 1, -1)] + [(c0, r) for r in range(r1 - 1, r0, -1)]
    return pts


def draw_frame(img, box, p, theme):
    """The frame: a row of full-size round dots around the GIF, drawn on clockwise (p 0..1), with the
    four corners in Clawd orange."""
    d = ImageDraw.Draw(img)
    pts = dotted_rect_points(*box)
    n = int(round(len(pts) * min(1.0, p)))
    col = DOT[theme]
    for c, r in pts[:n]:
        cx, cy = c * CELL + 4.5, r * CELL + 4.5
        d.ellipse([cx - 2.7, cy - 2.7, cx + 2.7, cy + 2.7], fill=col)
    if p >= 1:
        c0, r0, c1, r1 = box[0] // CELL, box[1] // CELL, box[2] // CELL, box[3] // CELL
        for c, r in ((c0, r0), (c1, r0), (c0, r1), (c1, r1)):
            d.rectangle([c * CELL, r * CELL, c * CELL + 8, r * CELL + 8], fill=ORANGE)


def title_at(playlist, t):
    for p in playlist:
        if p['t0'] <= t < p['t1']:
            return p['title']
    return 'HoliznaCC0'


class Tag:
    """The videos' now-playing tag, top right, scrolling."""
    def __init__(self):
        self.font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 26)

    def strip(self, text, theme):
        w = int(self.font.getlength(text)) + 60
        im = Image.new('RGBA', (w, 40), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 4), text, font=self.font, fill=(226, 226, 226) if theme == 'dark' else (20, 18, 14))
        return im

    def draw(self, img, text, theme, t):
        box = (1322, 38, 1862, 106)
        if theme == 'dark':
            ImageDraw.Draw(img).rectangle(box, fill=(27, 27, 27))
        note = ImageDraw.Draw(img)
        nc = (226, 226, 226) if theme == 'dark' else ORANGE
        note.ellipse([1346, 76, 1356, 86], fill=nc); note.ellipse([1362, 72, 1372, 82], fill=nc)
        note.rectangle([1353, 56, 1356, 80], fill=nc); note.rectangle([1369, 52, 1372, 76], fill=nc); note.rectangle([1353, 52, 1372, 57], fill=nc)
        s = self.strip(text + '        ', theme)
        off = int(t * 38) % s.width
        win = Image.new('RGBA', (450, 40), (0, 0, 0, 0))
        win.alpha_composite(s, (-off, 0)); win.alpha_composite(s, (s.width - off, 0))
        img.alpha_composite(win, (1392, 52))


def render_range(args):
    idxs, out, backdrops, track_at = args
    man = load_manifest()
    bgs = {}
    tag = Tag()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    t_global = track_at['start'][idxs[0]]
    for k in idxs:
        it = man[k]
        bd = backdrops.get(it['theme'], backdrops['default'])
        if bd['png'] not in bgs:
            src = Image.open(os.path.join(HERE, bd['png'])).convert('RGBA')
            full = Image.new('RGBA', (W, H), GROUND[bd['theme']] + (255,))
            full.paste(src.crop((0, 0, min(W, src.width), min(H, src.height))), (0, 0))
            bgs[bd['png']] = full
        bg, theme = bgs[bd['png']], bd['theme']
        frames = gif_frames(os.path.join(ROOT, it['file']))
        L, t_frame, total = plan(frames)
        bx0, by0, bx1, by1 = content_box(frames)
        gx, gy = W // 2 - 20 * SCALE, FEET_Y - 36 * SCALE
        box = (gx + bx0 * SCALE - 12, gy + by0 * SCALE - 12, gx + bx1 * SCALE + 12, gy + by1 * SCALE + 12)
        n = int(round(total * FPS))
        for f in range(n):
            u = f / FPS
            img = bg.copy()
            g = frame_at(frames, L, u).resize((40 * SCALE, 40 * SCALE), Image.NEAREST)
            img.alpha_composite(g, (gx, gy))
            if u >= t_frame:
                draw_frame(img, box, (u - t_frame) / FRAME_IN, theme)
            tag.draw(img, title_at(track_at['playlist'], t_global), theme, t_global)
            ff.stdin.write(img.tobytes())
            t_global += 1 / FPS
    ff.stdin.close(); ff.wait()
    return out


def schedule(man, idxs):
    """Start time of every vignette, to keep the tag scrolling and the music aligned across chunks."""
    start, t = {}, 0.0
    for k in idxs:
        frames = gif_frames(os.path.join(ROOT, man[k]['file']))
        start[k] = t
        t += round(plan(frames)[2] * FPS) / FPS
    return start, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None, help='e.g. 1-6 (1-based, manifest order)')
    ap.add_argument('--out', default='promo_video.mp4')
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--theme', default=None, help='render only this theme (timeline stays global)')
    ap.add_argument('--concat', action='store_true', help='join out/theme_*.mp4 in manifest order and add the music')
    a = ap.parse_args()
    man = load_manifest()
    if a.concat:
        return concat_all(man)
    allidx = list(range(len(man)))
    start, total = schedule(man, allidx)                 # global timeline: tag + music stay aligned
    idxs = allidx
    if a.only:
        lo, hi = (int(x) for x in a.only.split('-'))
        idxs = idxs[lo - 1:hi]
    if a.theme:
        idxs = [k for k in idxs if man[k]['theme'] == a.theme]
        a.out = f'theme_{a.theme}.mp4'
    backdrops = json.load(open(os.path.join(HERE, 'backdrops.json'), encoding='utf-8'))
    total = sum(round(plan(gif_frames(os.path.join(ROOT, man[k]['file'])))[2] * FPS) / FPS for k in idxs)
    playlist = json.load(open(os.path.join(HERE, 'playlist.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'playlist.json')) else []

    print(f'{len(idxs)} vignettes, {total / 60:.1f} min')
    n = max(1, min(a.jobs, len(idxs)))
    size = math.ceil(len(idxs) / n)
    chunks = [idxs[i * size:(i + 1) * size] for i in range(n) if idxs[i * size:(i + 1) * size]]
    tag = a.out[:-4]
    os.makedirs(os.path.join(HERE, 'out', 'parts', tag), exist_ok=True)
    jobs = [(c, os.path.join(HERE, 'out', 'parts', tag, f'part{j:02d}.mp4'), backdrops, {'start': start, 'playlist': playlist}) for j, c in enumerate(chunks)]
    if len(jobs) == 1:
        parts = [render_range(jobs[0])]
    else:
        with Pool(len(jobs)) as pool:
            parts = pool.map(render_range, jobs)
    lst = os.path.join(HERE, 'out', 'parts', tag, 'list.txt')
    with open(lst, 'w') as f:
        for p in parts:
            f.write(f"file '{os.path.basename(p)}'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(HERE, 'out', a.out)], check=True)
    print(os.path.join(HERE, 'out', a.out))


def concat_all(man):
    order = []
    for it in man:
        if it['theme'] not in order:
            order.append(it['theme'])
    lst = os.path.join(HERE, 'out', 'themes.txt')
    with open(lst, 'w') as f:
        for th in order:
            f.write(f"file 'theme_{th}.mp4'\n")
    silent = os.path.join(HERE, 'out', 'promo_silent.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', silent], check=True)
    final = os.path.join(HERE, 'out', 'clawd400_promo.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', os.path.join(HERE, 'out', 'music.wav'),
                    '-c:v', 'copy', '-af', 'volume=-1.5dB', '-c:a', 'aac', '-b:a', '256k', '-shortest', final], check=True)   # AAC overshoots ~1 dB: true peak lands at -3.7
    print(final)


if __name__ == '__main__':
    main()
