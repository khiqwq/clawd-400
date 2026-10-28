"""Render a scene file to GIF / WebP / MP4 / PNG frames / contact sheet.

    python render.py my_scene.py                       # every add() in the file -> out/<slug>.gif
    python render.py my_scene.py --only wave hop      # just these slugs
    python render.py my_scene.py --sheet              # also out/<slug>_sheet.png for checking
    python render.py my_scene.py --bg "#1c1a19"       # opaque background instead of transparent
    python render.py my_scene.py --mp4 --loops 4      # video (needs ffmpeg), uses the backdrop if set
    python render.py my_scene.py --webp --scale 6     # 240x240 animated WebP

The scene file imports from engine / props / kit (this folder is put on sys.path) and
registers animations with engine.add(slug, zh, en, fn, n=frames, dur=ms, backdrop=None, **kw).
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import engine  # noqa: E402


def load(path):
    spec = importlib.util.spec_from_file_location('clawd_scene', os.path.abspath(path))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return engine.REG


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scene')
    ap.add_argument('--out', default='out')
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--scale', type=int, default=engine.SCALE, help='screen px per logical px (12 -> 480x480)')
    ap.add_argument('--bg', help='solid background colour, e.g. "#ffffff" (default: transparent)')
    ap.add_argument('--gif', action='store_true', help='write GIF (default when no format is given)')
    ap.add_argument('--webp', action='store_true')
    ap.add_argument('--mp4', action='store_true')
    ap.add_argument('--png', action='store_true', help='write every frame as PNG')
    ap.add_argument('--sheet', action='store_true', help='contact sheet of all frames (with backdrop/bg)')
    ap.add_argument('--cell', type=int, default=240, help='contact-sheet cell size in px (240 shows eye placement)')
    ap.add_argument('--sheet-bg', default='#faf8f5', help='sheet background for transparent GIFs, e.g. "#1c1a19"')
    ap.add_argument('--loops', type=int, default=3, help='loop count baked into the MP4')
    a = ap.parse_args()
    if not (a.gif or a.webp or a.mp4 or a.png):
        a.gif = True
    os.makedirs(a.out, exist_ok=True)
    for e in load(a.scene):
        if a.only and e['slug'] not in a.only:
            continue
        frames = engine.render(e)
        durs = e['dur'] if isinstance(e['dur'], list) else [e['dur']] * len(frames)
        base = os.path.join(a.out, e['slug'])
        opaque = e.get('backdrop') is not None or a.bg
        if a.gif:
            if opaque:
                engine.save_rgb_gif(engine.compose(frames, e.get('backdrop'), a.bg, a.scale), base + '.gif', durs)
            elif a.scale == engine.SCALE:
                engine.save_gif(frames, base + '.gif', durs)
            else:
                ims = engine.compose(frames, None, None, a.scale)
                ims[0].save(base + '.gif', save_all=True, append_images=ims[1:], duration=durs, loop=0,
                            disposal=2)
        ims = None
        if a.webp or a.png or a.mp4:
            ims = engine.compose(frames, e.get('backdrop'), a.bg, a.scale)
        if a.webp:
            ims[0].save(base + '.webp', save_all=True, append_images=ims[1:], duration=durs, loop=0, lossless=True)
        if a.png:
            os.makedirs(base, exist_ok=True)
            for i, im in enumerate(ims):
                im.save(os.path.join(base, f'{i:03d}.png'))
        if a.mp4:
            write_mp4(ims, durs, base + '.mp4', a.loops)
        if a.sheet:
            write_sheet(ims or engine.compose(frames, e.get('backdrop'), a.bg, a.scale), base + '_sheet.png',
                        a.cell, a.sheet_bg)
        print('wrote', base)


def write_sheet(ims, path, cell, bg):
    from PIL import Image
    cols = min(6, len(ims))
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * cell, rows * cell), engine.col(bg))
    for i, im in enumerate(ims):
        tile = Image.new('RGBA', im.size, engine.col(bg) + (255,))
        tile.alpha_composite(im.convert('RGBA'))
        out.paste(tile.convert('RGB').resize((cell, cell), Image.NEAREST), ((i % cols) * cell, (i // cols) * cell))
    out.save(path)


def write_mp4(ims, durs, path, loops):
    ff = shutil.which('ffmpeg')
    if not ff:
        sys.exit('ffmpeg not found on PATH - install it or use --gif/--webp')
    with tempfile.TemporaryDirectory() as tmp:
        lines = []
        for k in range(loops):
            for i, (im, d) in enumerate(zip(ims, durs)):
                p = os.path.join(tmp, f'{i:03d}.png')
                if k == 0:
                    im.convert('RGB').save(p)
                lines += [f"file '{i:03d}.png'", f'duration {d / 1000:.3f}']
        lines.append(lines[-2])
        lst = os.path.join(tmp, 'list.txt')
        open(lst, 'w').write('\n'.join(lines))
        subprocess.run([ff, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vsync', 'vfr',
                        '-pix_fmt', 'yuv420p', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=neighbor', path],
                       check=True)


if __name__ == '__main__':
    main()
