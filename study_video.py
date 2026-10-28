"""Study a long reference video without watching it: keyframes -> rooms -> distinct Clawd beats.

    python study_video.py keyframes VIDEO OUTDIR      # only decodes keyframes (fast, any length)
    python study_video.py cluster OUTDIR [OUTDIR2..]  # rooms.png, beats_<room>.png, beats.json

Loops in these videos repeat for hours; clustering keeps one entry per distinct look and counts
how often it appears, so rare extras (a jump, a turn, a prop change) stand out.
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw


def keyframes(video, out):
    os.makedirs(out, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-skip_frame', 'nokey', '-i', video, '-an', '-fps_mode', 'vfr',
                    '-frame_pts', '1', '-vf', 'scale=320:-2', '-q:v', '4', os.path.join(out, 'k_%08d.jpg')],
                   check=True)
    print(len(glob.glob(os.path.join(out, 'k_*.jpg'))), 'keyframes in', out)


def vec(fn, size=(48, 27)):
    return np.asarray(Image.open(fn).convert('L').resize(size), dtype=np.float32)


def greedy(items, key, thresh):
    groups = []
    for it in items:
        v = key(it)
        best, bi = 1e9, -1
        for i, g in enumerate(groups):
            d = float(np.mean(np.abs(g[0] - v)))
            if d < best:
                best, bi = d, i
        if best < thresh:
            groups[bi][1].append(it)
        else:
            groups.append((v, [it]))
    groups.sort(key=lambda g: -len(g[1]))
    return groups


def clawd_crop(fn):
    im = Image.open(fn).convert('RGB')
    a = np.asarray(im).astype(int)
    m = (a[..., 0] > 150) & (a[..., 1] > 70) & (a[..., 1] < 150) & (a[..., 2] < 120) & (a[..., 0] - a[..., 2] > 60)
    ys, xs = np.nonzero(m)
    if len(xs) < 15:
        return None
    cx, cy = int(np.median(xs)), int(np.median(ys))
    return im.crop((cx - 32, cy - 34, cx + 32, cy + 30)).resize((64, 64)), (cx, cy)


def cluster(dirs):
    files = sorted(f for d in dirs for f in glob.glob(os.path.join(d, 'k_*.jpg')))
    rooms = greedy(files, vec, 9)
    out = dirs[0]
    report = []
    W, H = 240, 135
    sheet = Image.new('RGB', (8 * W, ((len(rooms) + 7) // 8) * (H + 12)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, (_, mem) in enumerate(rooms):
        x, y = (i % 8) * W, (i // 8) * (H + 12)
        sheet.paste(Image.open(mem[0]).convert('RGB').resize((W, H)), (x, y + 12))
        d.text((x + 2, y), f'room {i}: {len(mem)} frames', fill=(0, 0, 0))
    sheet.save(os.path.join(out, 'rooms.png'))
    for ri, (_, mem) in enumerate(rooms):
        if len(mem) < 20:
            continue
        crops = [(f, c) for f in mem for c in [clawd_crop(f)] if c]
        beats = greedy(crops, lambda it: np.asarray(it[1][0].convert('L').resize((24, 24)), dtype=np.float32), 14)
        cell = 96
        bs = Image.new('RGB', (min(14, len(beats)) * cell, ((len(beats) + 13) // 14) * (cell + 12)), (255, 255, 255))
        dd = ImageDraw.Draw(bs)
        entry = []
        for bi, (_, its) in enumerate(beats):
            x, y = (bi % 14) * cell, (bi // 14) * (cell + 12)
            bs.paste(its[0][1][0].resize((cell, cell), Image.NEAREST), (x, y + 12))
            dd.text((x + 2, y), f'{bi}:{len(its)}', fill=(0, 0, 0))
            entry.append(dict(beat=bi, count=len(its), examples=[
                dict(file=os.path.basename(f), frame=int(os.path.basename(f)[2:-4]), pos=c[1]) for f, c in its[:3]]))
        bs.save(os.path.join(out, f'beats_room{ri}.png'))
        report.append(dict(room=ri, frames=len(mem), beats=entry))
        print(f'room {ri}: {len(mem)} frames, {len(beats)} distinct beats', [len(b[1]) for b in beats][:20])
    json.dump(report, open(os.path.join(out, 'beats.json'), 'w'), indent=1)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'keyframes' and len(sys.argv) == 4:
        keyframes(sys.argv[2], sys.argv[3])
    elif cmd == 'cluster' and len(sys.argv) >= 3:
        cluster(sys.argv[2:])
    else:
        sys.exit(__doc__)
