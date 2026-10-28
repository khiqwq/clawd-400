"""Tempo, length and loudness of audio files: python track_stats.py <files...>"""
import subprocess, sys, numpy as np

def load(p, sr=22050):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32), sr

def bpm(x, sr):
    hop = 512
    n = len(x) // hop
    e = np.array([np.sum(x[i * hop:(i + 1) * hop] ** 2) for i in range(n)])
    onset = np.maximum(0, np.diff(np.log(e + 1e-9)))
    onset -= onset.mean()
    ac = np.correlate(onset, onset, 'full')[len(onset) - 1:]
    fps = sr / hop
    lags = np.arange(len(ac)) / fps
    best, bv = 0, -1
    for b in np.arange(60, 160, 0.5):
        l = int(round(60 / b * fps))
        v = ac[l] + 0.5 * ac[2 * l] if 2 * l < len(ac) else ac[l]
        if v > bv: bv, best = v, b
    return best

for p in sys.argv[1:]:
    x, sr = load(p)
    rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    seg = [20 * np.log10(np.sqrt(np.mean(x[i:i + sr * 4] ** 2)) + 1e-9) for i in range(0, len(x) - sr * 4, sr * 4)]
    print(f'{len(x)/sr:6.1f}s  {bpm(x[:sr*90], sr):5.1f} bpm  {rms:6.1f} dB  4s-RMS: ' + ' '.join(f'{v:.0f}' for v in seg[:30]), '|', p.split('/')[-1])
