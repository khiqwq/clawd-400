"""Music for the promo: the CC0 HoliznaCC0 collections played back to back with crossfades, cut to the
video's length, loudness-matched. Writes playlist.json (for the now-playing tag) and out/music.wav.

  python mix_promo.py            # plan + mix for the full 400-GIF schedule
"""
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, '..', 'music', 'dl')
XF = 3.0                       # crossfade seconds
SR = 48000


def duration(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)


def title_of(p):
    name = os.path.basename(p)
    name = re.sub(r'(\.mp3)+$', '', name)
    name = re.sub(r'^\d+\s*', '', name)
    artist, _, track = name.partition(' - ')
    return f'{track.strip()} — {artist.strip()}' if track else name


def main():
    sys.path.insert(0, HERE)
    import render_promo as R
    man = R.load_manifest()
    _, total = R.schedule(man, list(range(len(man))))
    files = sorted(glob.glob(os.path.join(DL, '**', '*.mp3'), recursive=True))
    # a fixed, pleasant order: alternate the collections so the mood keeps moving
    by = {}
    for f in files:
        by.setdefault(os.path.dirname(f), []).append(f)
    order, groups = [], list(by.values())
    while any(groups):
        for g in groups:
            if g:
                order.append(g.pop(0))
    playlist, t = [], 0.0
    for f in order:
        d = duration(f)
        playlist.append(dict(file=f, title=title_of(f), t0=round(t, 3), t1=round(t + d - XF, 3), dur=d))
        t += d - XF
        if t >= total:
            break
    json.dump([dict(title=p['title'], t0=p['t0'], t1=p['t1'], source='HoliznaCC0, CC0 1.0 (opengameart.org)') for p in playlist],
              open(os.path.join(HERE, 'playlist.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # mix: normalise each track, chain acrossfades, trim to the video, fade out the last 4 s
    args, filt = [], []
    for k, p in enumerate(playlist):
        args += ['-i', p['file']]
        filt.append(f'[{k}:a]aresample={SR},loudnorm=I=-17:TP=-3:LRA=11,aformat=channel_layouts=stereo[a{k}]')
    last = 'a0'
    for k in range(1, len(playlist)):
        filt.append(f'[{last}][a{k}]acrossfade=d={XF}:c1=tri:c2=tri[x{k}]')
        last = f'x{k}'
    filt.append(f'[{last}]atrim=0:{total:.3f},afade=t=out:st={total - 4:.3f}:d=4[out]')
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    out = os.path.join(HERE, 'out', 'music.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', str(SR), out], check=True)
    print(len(playlist), 'tracks,', f'{total / 60:.1f} min ->', out)


if __name__ == '__main__':
    main()
