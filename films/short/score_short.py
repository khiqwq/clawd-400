"""Sound for "末班车": the music (HoliznaCC0 — Happy, but a little off, CC0 1.0, opengameart.org) cut in two
sections, plus a few synthesized foley sounds (onetake's sfx_palette), mixed and muxed onto the film.

Section 1: track 4.3 s → film 0 (the drums enter at track 10.7 = film 6.4, the carriage rising in),
           fading out while Clawd dozes (film 17.8 → 19.4).
Section 2: track 95.7 s → film 19.4 (the hilltop rising in); the drums stop at track 106.5 = film 30.2,
           exactly when the title lands; the melodic tail carries the end.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'onetake-kit', 'scripts'))
from sfx_palette import Score, air, glass, wood, sub, bubble  # noqa: E402

TL = json.load(open(os.path.join(HERE, 'out', 'timeline.json')))
T, DUR = TL['T'], TL['dur']
TRACK = os.path.join(HERE, '..', 'music', 'short_track.mp3')
OUT = os.path.join(HERE, 'out')


def foley():
    s = Score(dur=DUR, T60=1.0)
    rng = np.random.default_rng(3)
    # A: midnight chime, steps to the door, the hop, the landing
    s.place(glass(784, 1.4, 0.5), T['bell'], 0.22, 0.25, 0.5)
    s.place(glass(659, 1.6, 0.5), T['bell'] + 0.42, 0.2, 0.25, 0.5)
    for k in range(4):
        s.place(wood(260 + rng.uniform(-20, 20), 0.06), T['walk'] + 0.13 + k * 0.26, 0.10, -0.4 + k * 0.08, 0.15)
    s.place(air(0.3, 300, 1800, 1.3), T['hop'] - 0.02, 0.14, -0.1, 0.3)
    s.place(wood(170, 0.1), T['landed'], 0.28, -0.1, 0.2); s.place(sub(80, 0.4), T['landed'], 0.12, 0, 0.2)
    # scene changes: the next room rising from below
    for tb in (T['B'], T['C']):
        s.place(air(0.42, 260, 2400, 1.2, 0.55), tb - 0.05, 0.3, 0.0, 0.45)
    # B: the pot set down, the lean, the notice, the lift, the new leaf, sitting back down
    s.place(wood(210, 0.08), T['put'] + 0.25, 0.22, -0.3, 0.2)
    s.place(glass(1568, 0.5, 0.3), T['lean'] + 0.05, 0.06, -0.3, 0.6)
    s.place(bubble(620, 0.2), T['notice'], 0.16, -0.3, 0.3)
    s.place(air(0.3, 400, 2200, 1.4), T['lift'], 0.12, -0.3, 0.3)
    for k, f in enumerate((1046, 1318, 1568)):
        s.place(glass(f, 1.1, 0.6), T['grow'] + k * 0.09, 0.13, -0.3, 0.55)
    s.place(wood(180, 0.08), T['sit'] + 0.05, 0.16, -0.3, 0.2)
    # C: steps up the hill (quiet, slowing), planting, the bloom
    t = T['enter'] + 0.1
    k = 0
    while t < T['top']:
        s.place(wood(300 + rng.uniform(-25, 25), 0.05), t, 0.06, -0.6 + 0.9 * (t - T['enter']) / (T['top'] - T['enter']), 0.15)
        t += 0.28; k += 1
    s.place(wood(150, 0.12), T['plant'], 0.24, 0.3, 0.25); s.place(sub(70, 0.5), T['plant'], 0.1, 0.3, 0.2)
    for tb, f in zip(T['bloom'], (784, 1046, 1318)):
        s.place(glass(f, 1.3, 0.6), tb, 0.15, 0.35, 0.55)
    path = os.path.join(OUT, 'sfx.wav')
    s.write(path)
    return path


def music():
    path = os.path.join(OUT, 'music_short.wav')
    f = (f"[0:a]atrim=4.3:{4.3 + T['C']},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.6,"
         f"afade=t=out:st={17.8}:d={T['C'] - 17.8}[a];"
         f"[1:a]atrim=95.7:{95.7 + DUR - T['C'] + 0.1},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.7,"
         f"afade=t=out:st={DUR - T['C'] - 1.6}:d=1.6,adelay={int(T['C'] * 1000)}|{int(T['C'] * 1000)}[b];"
         f"[a][b]amix=inputs=2:normalize=0,atrim=0:{DUR},loudnorm=I=-20:TP=-4:LRA=11[m]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', TRACK, '-i', TRACK, '-filter_complex', f, '-map', '[m]', '-ar', '48000', '-ac', '2', path], check=True)
    return path


def main():
    sfx, mus = foley(), music()
    mix = os.path.join(OUT, 'mix_short.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mus, '-i', sfx, '-filter_complex',
                    '[0:a][1:a]amix=inputs=2:normalize=0:weights=1 1.6,loudnorm=I=-16:TP=-3.5:LRA=11[o]', '-map', '[o]', '-ar', '48000', mix], check=True)
    final = os.path.join(OUT, 'clawd_last_train.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'short_silent.mp4'), '-i', mix, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', final], check=True)
    print(final)


if __name__ == '__main__':
    main()
