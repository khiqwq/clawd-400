"""Feelings, moods, reactions and expressive idle quirks (prefix emo_).

Style contract: Clawd's face is two black eyes from the engine's glyph set and nothing else,
his body stays flat reference orange. Every emotion is carried by eye glyph, pose, motion and
effects drawn AROUND him (hearts, sweat, steam, marks, bubbles, props).
"""
import math
from engine import (Canvas, GROUND, BX, BY, add, clawd, mini, sin, ph, tri, rng, col)
from engine import beats, add_tweened
import props as P

# =========================================================================== local art
HEART5 = ['.Z.Z.', 'ZZZZZ', 'ZZZZZ', '.ZZZ.', '..Z..']
HEART_XL = ['.ZZZ.ZZZ.', 'ZZZZZZZZZ', 'ZWWZZZZZZ', 'ZWZZZZZZZ', '.ZZZZZZZ.', '..ZZZZZ..', '...ZZZ...',
            '....Z....']
HEART_SPLIT = [4, 4, 3, 5, 3, 5, 4, 4]          # zig-zag crack column per heart row
TWINKLE = ['.Y.', 'YUY', '.Y.']
STAR_PLUS = ['..U..', '..U..', 'UUWUU', '..U..', '..U..']
STAR_X = ['U...U', '.U.U.', '..W..', '.U.U.', 'U...U']
QBIG = ['.CCC.', 'CC.CC', '...CC', '..CC.', '..C..', '.....', '..C..']
EXBIG = ['RR', 'RR', 'RR', 'RR', '..', 'RR']
FEATHER = ['.....GW', '....GWW', '...GWWG', '..GWWG.', '.GWWG..', '.gGG...', 'g......']
FEATHER2 = ['....GW.', '...GWW.', '...GWG.', '..GWG..', '..GWG..', '.gGG...', '.g.....']
TUMBLE = [['..NNN..', '.N.n.NN', 'N.nNn.N', 'Nn...nN', 'N.nNn.N', 'NN.n.N.', '..NNN..'],
          ['..N.N..', '.NNnNN.', 'NnN.NnN', '.n.N.n.', 'NnN.NnN', '.NNnNN.', '..N.N..']]
CRICKET = ['e......', '.e.EEE.', '..EEEEE', '.e.e..e']
BLOB = [['...EE...', '..EEEe..', '.EEeEEE.', 'EEEEEeEE', 'EeEEEEEE', '.EEEEEE.'],
        ['..EEE...', '.EEEEe..', '.EeEEEE.', 'EEEEEeEE', 'EeEEEEEE', '.EEEEEE.']]
BLUSH_MARK = ['..Z..Z', '.Z..Z.', 'Z..Z..']


# =========================================================================== helpers
def walk(s):
    return (1, 0, 1, 0) if s else (0, 1, 0, 1)


def land(L, ground=GROUND):
    """Shift a layer so its lowest pixel sits on the row above `ground`."""
    bb = L.bbox()
    return L.shift(0, ground - bb[3]) if bb else L


def outlined(f, L, c='G'):
    """Blit a prop layer with a 1px outline (white props stay readable on white)."""
    O = Canvas(L.w, L.h)
    cc = col(c)
    for y in range(L.h):
        for x in range(L.w):
            if L.px[y][x] is None:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < L.w and 0 <= yy < L.h and L.px[yy][xx] is None:
                    O.px[yy][xx] = cc
    f.blit(O)
    f.blit(L)


def fold_arms(f, info, dy=9, view='front'):
    """Arms crossed low over the belly, drawn in the shade colour like the engine's front arms."""
    x, y, w = info['x'], info['y'], info['w']
    x0, x1 = (x + 1, x + w - 3) if view == 'ql' else (x + 3, x + w - 1) if view == 'qr' else (x + 1, x + w - 1)
    mid = (x0 + x1) // 2
    f.rect(x0, y + dy, mid - x0 + 2, 2, 'o')
    f.rect(mid - 1, y + dy + 1, x1 - mid + 1, 2, 'o')


def clock(f, cx, cy, k, n):
    """Little white clock face (grey rim) whose minute hand sweeps once per loop."""
    f.disc(cx + .5, cy + .5, 4.6, 'g')
    f.disc(cx + .5, cy + .5, 3.7, 'W')
    a = 2 * math.pi * k / n - math.pi / 2
    f.line(cx, cy, cx + round(math.cos(a) * 3), cy + round(math.sin(a) * 3), 'K')
    f.line(cx, cy, cx - 2, cy, 'K')


def cloud_bubble(f, x, y, w, h):
    T = Canvas()
    P.thought(T, x, y, w, h, c='W')
    outlined(f, T, 'G')


def puff(f, x, y, p, c='L'):
    """Little exhale puff that grows and thins, p 0..1."""
    if p < 0.34:
        f.art(['LL', 'LL'], x, y, cmap={'L': c})
    elif p < 0.67:
        f.art(['.LL.', 'LLLL', '.LL.'], x - 1, y - 1, cmap={'L': c})
    else:
        f.art(['L..L', '....', 'L..L'], x - 1, y - 2, cmap={'L': c})


def steam(f, info, k, gap=3):
    """Anger steam puffs from both sides of the head."""
    x, y, w = info['x'], info['y'], info['w']
    s = k % 3
    for sx in (x - gap - 1, x + w + gap - 2):
        f.art([P.PUFF_S, ['.LL', 'LLL', 'LL.'], ['L.L', '.L.', 'L.L']][s], sx, y - 3 - s * 2)


def heart_halves(f, x, y, sep=0, dyl=0, dyr=0, crack=False, cmap=None):
    for j, row in enumerate(HEART_XL):
        s = HEART_SPLIT[j]
        for i, c in enumerate(row):
            if c == '.':
                continue
            if cmap:
                c = cmap.get(c, c)
            if i < s:
                f.put(x + i - sep, y + j + dyl, c)
            elif i > s or not crack:
                f.put(x + i + sep, y + j + dyr, c)


def drop(f, x, y):
    f.rect(int(x), int(y), 2, 2, 'B')
    f.put(int(x), int(y), 'C')


def eye_spots(L):
    """Centres of Clawd's two eyes found in a transformed layer (black pixels, left then right)."""
    pts = [(xx, yy) for yy, row in enumerate(L.px) for xx, c in enumerate(row) if c == (0, 0, 0)]
    if not pts:
        return []
    mid = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    out = []
    for grp in ([p for p in pts if p[0] <= mid], [p for p in pts if p[0] > mid]):
        if grp:
            out.append((sum(p[0] for p in grp) / len(grp) + 0.5, sum(p[1] for p in grp) / len(grp) + 0.5))
    return out


# =========================================================================== joy & pride
def joy_burst(f, t, n):
    """Squash, leap with arms up, a rainbow star burst pops at the top."""
    k = t % n
    dys = [0, 0, None, -4, -8, -10, -11, -11, -10, -8, -4, None, 0, 0]
    dy = dys[k]
    if 4 <= k <= 11:
        q = (k - 4) / 7
        r = 6 + q * 14
        cols = 'UZCEPFBR'
        for i in range(8):
            a = i * math.pi / 4 + math.pi / 8
            px, py = 20 + math.cos(a) * r, 16 + math.sin(a) * r * 0.85
            if q < 0.6:
                f.art(['.C.', 'CWC', '.C.'], int(px) - 1, int(py) - 1, cmap={'C': cols[i]})
            else:
                f.put(px, py, cols[i])
            rr = r * 0.55
            a2 = i * math.pi / 4
            f.put(20 + math.cos(a2) * rr, 16 + math.sin(a2) * rr * 0.85, 'U')
    if dy is None:
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='closed', la='low', ra='low')
        P.dust(f, BX - 4, GROUND, 0.5)
        P.dust(f, BX + 19, GROUND, 0.5, flip=True)
    else:
        air = dy < 0
        clawd(f, y=BY + dy - (1 if air else 0), h=13 if air else 12,
              la='up' if air else 'side', ra='up' if air else 'side',
              legs=(1, 1, 1, 1) if dy <= -8 else (0, 0, 0, 0),
              eyes='happy' if (air or k >= 12) else 'normal')


def happy_skip(f, t, n):
    """Skips merrily across the screen, little notes bobbing behind."""
    x = -18 + int(round(60 * t / n))
    k = t % 6
    dy = [0, -3, -5, -6, -5, -3][k]
    alt = (t // 6) % 2
    for j in (1, 2):
        nx = x - 3 - j * 8
        ny = BY - 1 - j * 3 - (1 if (t + j) % 4 < 2 else 0)
        f.art(P.NOTE if j == 1 else P.NOTE2, nx, ny, cmap={'K': 'P' if j == 1 else 'B'})
    if k == 0:
        clawd(f, x=x, y=BY + 1, h=11, view='qr', eyes='happy', la='low', ra='low')
        P.dust(f, x - 3, GROUND, 0.2)
    else:
        clawd(f, x=x, y=BY + dy, view='qr', eyes='happy',
              legs=(0, 2, 0, 2) if alt else (2, 0, 2, 0),
              la='mid' if alt else 'side', ra='low' if alt else 'mid')


def victory_dance(f, t, n):
    """Four-beat victory routine: point left, point right, twirl, jump - confetti everywhere."""
    P.confetti(f, t, n, count=18)
    k = t % n
    b, s = k // 4, k % 2
    L = Canvas()
    if b == 0:
        info = clawd(L, x=BX - 1 + s, la='up', ra='low', eyes='happy', legs=(0, 2, 0, 0) if s else (0, 0, 0, 0))
        L = L.shear(-0.13 if s else -0.06)
    elif b == 1:
        info = clawd(L, x=BX + 1 - s, la='low', ra='up', eyes='happy', legs=(0, 0, 2, 0) if s else (0, 0, 0, 0))
        L = L.shear(0.13 if s else 0.06)
    elif b == 2:
        v = ['qr', 'back', 'ql', 'front'][k % 4]
        info = clawd(L, view=v, la='high', ra='high', eyes='happy', y=BY - 1)
    else:
        dy = [-2, -5, -5, -2][k % 4]
        info = clawd(L, y=BY + dy, la='up', ra='up', legs=(1, 1, 1, 1), eyes='happy')
    f.blit(L)
    if b == 3:
        P.say(f, info, 'YAY!', dy=-2)


def hyper_bounce(f, t, n):
    """Too excited to stand still: ricochets off both walls and the floor."""
    k = t % n
    p = ((k - 2) % n) / n
    x = 4 + int(round(16 * (1 - abs(2 * p - 1))))
    j = k % 4
    dy = [0, -6, -8, -6][j]
    right = 0 < p < 0.5
    if j == 0:
        clawd(f, x=x - 2, w=20, h=9, y=BY + 3, eyes='closed', la='low', ra='low')
        P.dust(f, x - 4, GROUND, 0.4)
        P.dust(f, x + 19, GROUND, 0.4, flip=True)
        return
    if k in (2, 10):
        ex = 0 if k == 2 else 39
        f.art(['...U...', '.U.U.U.', '..UUU..', 'UUUWUUU', '..UUU..', '.U.U.U.', '...U...'], ex - 3,
              BY + dy + 2)
        xx = x + (0 if k == 2 else 3)
        clawd(f, x=xx, w=13, h=14, y=BY + dy - 2, eyes='squint',
              la='short' if k == 2 else 'up', ra='up' if k == 2 else 'short', legs=(1, 1, 1, 1))
        return
    info = clawd(f, x=x, y=BY + dy, eyes='big' if k % 2 else 'happy', la='up', ra='up', legs=(1, 1, 1, 1))
    if right:
        P.speedlines(f, x - 5, info['y'] + 1, t, n=3)
    else:
        P.speedlines(f, x + 21, info['y'] + 1, t, n=3, side='r')


def excited_vibrate(f, t, n):
    """Buzzing with excitement: jittering in place, fists pumping, squeaky vibration marks."""
    k = t % n
    amp = 1 if k % 6 < 3 else 2
    dx = amp if k % 2 else -amp
    hop = -2 if k in (5, 11) else 0
    info = clawd(f, x=BX + dx, y=BY + hop, eyes='big' if k % 2 else 'happy',
                 la='up' if k % 2 else 'high', ra='high' if k % 2 else 'up',
                 legs=(0, 1, 0, 1) if k % 2 else (1, 0, 1, 0))
    x, y, w = info['x'], info['y'], info['w']
    o = k % 2
    f.art(['.L', 'L.', '.L'] if o else ['L.', '.L', 'L.'], x - 7, y + 3)
    f.art(['L.', '.L', 'L.'] if o else ['.L', 'L.', '.L'], x + w + 6, y + 3)
    for (sx, sy) in ((2, 24), (36, 24)):
        oo = (k + sx) % 2
        f.art(['C.', '.C', 'C.', '.C'] if oo else ['.C', 'C.', '.C', 'C.'], sx, sy + oo)
    f.art(EXBIG, 10 - (k % 2), 7 + (k % 3))
    f.art(EXBIG, 28 + (k % 2), 8 - (k % 2))


def wish_star(f, t, n):
    """A shooting star streaks by; it clasps its hands, shuts its eyes and makes a wish."""
    k = t % n
    if k < 6:
        p = k / 5
        sx, sy = 41 - p * 46, 2 + p * 8
        for i in range(1, 7):
            f.put(sx + i * 2, sy - i * 0.35, 'U' if i < 3 else 'Y' if i < 5 else 'y')
        f.art(['.U.', 'UWU', '.U.'], int(sx) - 1, int(sy) - 1)
        look = 1 if p < 0.35 else (0 if p < 0.7 else -1)
        clawd(f, eyes='big', look=look, lookv=-1, la='side' if k < 3 else 'mid', ra='side' if k < 3 else 'mid')
        return
    if k < 14:
        j = k - 6
        nod = 1 if j % 4 == 3 else 0
        info = clawd(f, y=BY + nod, h=12 - nod, eyes='closed', la='short', ra='short')
        fold_arms(f, info, dy=8 - nod)
        tw = j % 4 < 2
        f.art(STAR_PLUS if tw else TWINKLE, 18 if tw else 19, 3 if tw else 4)
        for i in range(3):
            q = (j / 8 + i / 3) % 1
            px = 20 + (i - 1) * 9 + math.sin(q * 6.28 + i) * 1.5
            f.put(px + (i - 1) * 3, BY - 1 - q * 13, 'U' if q < 0.6 else 'Y')
        return
    info = clawd(f, eyes='happy', la='up', ra='up', y=BY - 1, h=13)
    f.art(STAR_X if k == 14 else STAR_PLUS, 18, 3)
    P.sparkles(f, k, 4, [(6, 12), (33, 10), (10, 4), (30, 3)])


def proud_chest(f, t, n):
    """Puffs up the chest, nose in the air, sparkles all around."""
    k = t % n
    seq = [(16, 12), (16, 12), (18, 13), (20, 14), (20, 14), (20, 14), (20, 14), (20, 14), (20, 14),
           (18, 13), (16, 12), (16, 12)]
    w, h = seq[k]
    puffed = w == 20
    clawd(f, x=20 - w // 2, y=33 - h, w=w, h=h,
          eyes='closed' if w > 16 else ('blink' if k == 11 else 'normal'),
          lookv=-1 if w > 16 else 0, la='low' if w > 16 else 'side', ra='low' if w > 16 else 'side')
    if puffed:
        P.sparkles(f, t, n, [(5, 15), (34, 14), (7, 29), (32, 30), (20, 10), (12, 5), (28, 6)])
        if 5 <= k <= 7:
            f.text('HMPH', 25, 13 - (k % 2), 'Y')


def smug_shades(f, t, n):
    """Shades slide down off the head, glint, then get pushed back up."""
    k = t % n
    sy = {4: -1, 5: 0, 6: 1, 12: 1, 13: 0, 14: -1}.get(k, -2 if k < 4 or k == 15 else 2)
    adjusting = 4 <= k <= 6 or 12 <= k <= 14
    nod = 1 if k == 10 else 0
    L = Canvas()
    info = clawd(L, y=BY + nod, h=12 - nod, eyes='blink', look=1 if k < 4 else 0, ra='up' if adjusting else 'side')
    x, y, w = info['x'], info['y'], info['w']
    yy = y + sy
    L.rect(x, yy, w, 1, 'K')
    for lx in (x + 1, x + w - 7):
        L.rect(lx, yy, 6, 3, 'K')
        L.rect(lx + 1, yy + 1, 4, 1, 'b')
    if sy == 2:
        g = {9: 0, 10: 1, 11: 2}.get(k)
        if g is not None:
            gx = x + 2 + g * 5
            L.put(gx, yy + 1, 'W'); L.put(gx + 1, yy, 'W')
    if k == 8:
        L.art(['.W.', 'WUW', '.W.'], x - 3, yy - 3)
    if k == 11:
        L.art(['.W.', 'WUW', '.W.'], x + w, yy - 3)
    f.blit(L.shear(-0.05) if 8 <= k <= 11 else L)


def thumbs_up(f, t, n):
    """Pops a thumbs-up with a 'ting'."""
    k = t % n
    up = 4 <= k <= 10
    info = clawd(f, eyes='happy' if up else ('blink' if k == 1 else 'normal'),
                 ra='none' if up else ('mid' if k in (3, 11) else 'side'))
    if up:
        x, y, w = info['x'], info['y'], info['w']
        pump = -1 if k in (6, 8) else 0
        f.rect(x + w, y + 2, 4, 3, 'O')
        fx, fy = x + w + 3, y - 1 + pump
        f.rect(fx, fy, 4, 5, 'O')
        f.rect(fx + 1, fy - 3, 2, 3, 'O')
        f.rect(fx, fy + 1, 2, 1, 'o')
        f.rect(fx, fy + 3, 2, 1, 'o')
        if k in (4, 5, 9):
            f.art(P.SPARK_BIG, fx - 2, fy - 10)
        if k == 6 or k == 8:
            f.put(fx - 2, fy - 4, 'U'); f.put(fx + 5, fy - 4, 'U')
        if 6 <= k <= 9:
            f.text('OK', 3, 12 - (k % 2), 'E')


def wink(f, t, n):
    """A cheeky wink with finger-guns; the wink flies off as a little star."""
    k = t % n
    wk = 4 <= k <= 8
    L = Canvas()
    info = clawd(L, eyes='normal', eyes_r='happy' if wk else None, ra='out' if wk else 'side')
    x, y, w = info['x'], info['y'], info['w']
    if wk:
        L.rect(x + w + 5, y + 4 - (1 if k == 4 else 0), 1, 1, 'O')
    f.blit(L.shear(0.07) if wk else L)
    if 4 <= k <= 9:
        j = k - 4
        ex, ey = max(info['eyes'])  # the star pops off the winking eye's corner, then flies off
        f.art(STAR_PLUS if j % 2 == 0 else STAR_X, int(ex) + j * 3, int(ey) - 4 - j * 3)
    if k in (4, 5):
        f.art(['..U', '...', 'U..', '...', '..U'] if k == 4 else ['.U', '..', 'U.'], x + w + 7, y + 1)
        f.text('PEW', x + w, y + 10, 'Z')


# =========================================================================== laughter & love
def ticklish(f, t, n):
    """A feather tickles its side - it squirms and giggles uncontrollably."""
    k = t % n
    fy = 24 + int(round(2 * sin(t, n, 2)))
    s = k % 2
    L = Canvas()
    clawd(L, x=BX + 1 + s, y=BY + (k % 3 == 0), eyes='squint' if s else 'happy', la='high',
          ra='up' if s else 'high')
    f.blit(L.shear(0.1 if s else -0.04))
    F = Canvas()
    F.art(FEATHER if s else FEATHER2, 3 + s, fy)
    outlined(f, F, 'g')
    for i, (tx, ty) in enumerate(((8, 15), (29, 13))):
        if (k // 2 + i) % 2 == 0:
            f.text('HA' if i else 'HE', tx + (k % 2), ty - (k % 3), 'Z')


def giggle(f, t, n):
    """Hand over mouth, shoulders shaking with little hee-hees."""
    k = t % n
    b = k % 2
    info = clawd(f, y=BY + b, h=12 - b, eyes='happy', ra='none')
    x, y, w = info['x'], info['y'], info['w']
    f.rect(x + 6, y + 5, 5, 3, 'o')
    f.rect(x + 11, y + 6, 5, 2, 'o')
    f.rect(x + w, y + 6, 2, 3, 'O')
    if k % 4 < 2:
        f.text('HE', x + w + 2, y - 6 - b, 'Z')
    else:
        f.text('HE', x - 9, y - 5 - b, 'Z')


def laugh_roll(f, t, n):
    """Laughs so hard it tips over and rocks on its back, legs in the air."""
    k = t % n
    L = Canvas()
    spots = [((4, 9), (27, 5)), ((8, 4), (25, 11))][k % 2]
    if k <= 2 or k >= 13:
        b = k % 2
        info = clawd(L, y=BY + b, h=12 - b, eyes='squint', la='short', ra='short')
        fold_arms(L, info, dy=9 - b)
        f.blit(L)
        x, y = info['x'], info['y']
        f.put(x - 2, y + 2 + (k % 3), 'C'); f.put(x + 17, y + 3 + (k % 3), 'C')
        f.text('HA', spots[0][0], spots[0][1] + 4, 'Z')
        f.text('HA', spots[1][0], spots[1][1] + 4, 'F')
        return
    if k == 3:
        clawd(L, eyes='squint', la='high', ra='high')
        f.blit(L.shear(0.25))
        f.text('HA', 27, 9, 'F')
        return
    r, dx = [(1, 2), (2, 3), (3, 2), (2, 0), (1, -2), (2, -3), (3, -2), (2, 0), (1, 0)][k - 4]
    clawd(L, eyes='squint', la='high' if k % 2 else 'mid', ra='mid' if k % 2 else 'high',
          legs=(0, 1, 0, 1) if k % 2 else (1, 0, 1, 0))
    L = land(L.rot90(r, 20, 27).shift(dx, 0))
    f.blit(L)
    f.text('HA', spots[0][0], spots[0][1], 'Z')
    f.text('HA', spots[1][0], spots[1][1], 'F')
    if r == 2:
        P.dust(f, 9 + dx, GROUND, 0.3)
        P.dust(f, 29 + dx, GROUND, 0.3, flip=True)


def self_hug(f, t, n):
    """Wraps its arms around itself and sways, squeezing tight now and then."""
    k = t % n
    sq = k in (4, 5, 12, 13)
    w, h = (15, 13) if sq else (16, 12)
    L = Canvas()
    info = clawd(L, x=20 - w // 2, y=33 - h, w=w, h=h, eyes='happy', la='none', ra='none')
    x, y = info['x'], info['y']
    L.rect(x - 1, y + 6, 2, 4, 'O'); L.rect(x + w - 1, y + 7, 2, 4, 'O')
    L.rect(x + 1, y + 8, 10, 2, 'o')
    L.rect(x + w - 11, y + 10, 10, 2, 'o')
    f.blit(L.shear(0.07 * sin(t, n)))
    if sq:
        f.art(P.HEART, x - 5, y - 2 - (k % 2))
        f.art(P.HEART, x + w + 2, y - 1 - (k % 2))
    P.rising(f, ['r'], t, n, 20, y - 2, count=3, height=10, jitter=8, seed=9)


def blow_kiss(f, t, n):
    """Kisses its hand and throws a heart that grows as it flies."""
    k = t % n
    near = k <= 3 or k >= 14
    info = clawd(f, eyes='closed' if near else 'happy', ra='none' if near else 'out')
    x, y, w = info['x'], info['y'], info['w']
    if near:
        f.rect(x + 9, y + 5, 4, 3, 'o')
        f.rect(x + 13, y + 6, 3, 2, 'o')
        if k in (2, 3):
            f.art(['Z.Z', '.Z.'], x + w + 1, y + 1 - (k - 2))
    if 4 <= k <= 13:
        p = (k - 4) / 9
        hx = x + w + 5 - p * 8
        hy = y + 3 - p * 20
        if p < 0.3:
            f.art(P.HEART, int(hx), int(hy))
        elif p < 0.65:
            f.art(HEART5, int(hx) - 1, int(hy) - 1)
        elif p < 0.95:
            f.art(P.HEART_BIG, int(hx) - 3, int(hy) - 2)
        else:
            for ox, oy in ((-5, -3), (3, -4), (-4, 3), (4, 2)):
                f.art(['Z.Z', '.Z.'], int(hx) + ox, int(hy) + oy)


def lovestruck(f, t, n):
    """Swaying dreamily, eyes squeezed happy, a big heart throbbing over its head."""
    k = t % n
    beat = k % 6 in (0, 1)
    L = Canvas()
    info = clawd(L, eyes='happy' if k % 12 < 9 else 'closed', la='high' if beat else 'mid',
                 ra='high' if beat else 'mid', y=BY - (1 if beat else 0), h=12 + (1 if beat else 0))
    f.blit(L.shear(0.1 * sin(t, n)))
    sway = int(round(1.5 * sin(t, n)))
    if beat:
        f.art(P.HEART_BIG, 17 + sway, 9)
        f.art(['Z.', '.Z'], 14 + sway, 8); f.art(['.Z', 'Z.'], 24 + sway, 8)
    else:
        f.art(HEART5, 18 + sway, 10)
    P.rising(f, P.HEART, t, n, 20, BY - 3, count=3, height=14, jitter=14, seed=4)


def heart_pound(f, t, n):
    """Heart thumping so hard it shakes its whole body - ba-dump, ba-dump."""
    k = t % n
    big = k in (0, 2)
    info = clawd(f, x=BX - 3 - (1 if big else 0), w=18 if big else 16, y=BY - (1 if big else 0),
                 h=13 if big else 12, eyes='big', la='low', ra='low')
    hx, hy = 28, 12
    if big:
        f.art(HEART_XL, hx - 4, hy - 4)
        for (ax, ay, a) in ((hx - 8, hy - 4, ['.Z', 'Z.', 'Z.', '.Z']), (hx + 6, hy - 4, ['Z.', '.Z', '.Z', 'Z.']),
                            (hx - 10, hy - 5, ['.Z', 'Z.', 'Z.', 'Z.', '.Z']),
                            (hx + 8, hy - 5, ['Z.', '.Z', '.Z', '.Z', 'Z.'])):
            f.art(a, ax, ay)
        f.text('BA' if k == 0 else 'DUMP', 1 if k == 0 else 1, 4, 'Z')
        x, w = info['x'], info['w']
        f.art(['g.g', '...'], x - 3, 34); f.art(['g.g', '...'], x + w, 34)
    else:
        f.art(HEART5, hx - 2, hy - 2)


def daydream(f, t, n):
    """Chin in hand, gazing up at a dream bubble that cycles heart, mini-self and moon."""
    k = t % n
    d = k // 8
    L = Canvas()
    clawd(L, x=3, eyes='normal', look=1, lookv=-1, la='chin')
    f.blit(L.shear(0.04 * sin(t, n)))
    cloud_bubble(f, 20, 1, 19, 13)
    j = k % 8
    if d == 0:
        a = P.HEART_BIG if j % 4 < 2 else HEART5
        f.art(a, 29 - len(a[0]) // 2, 5 if len(a) > 5 else 6)
    elif d == 1:
        hop = [0, -1, -2, -2, -1, 0, 0, 0][j]
        mini(f, 25, 4 + hop, eyes='happy', la='high' if hop else 'side', ra='high' if hop else 'side')
    else:
        P.moon(f, 24, 4)
        f.art(TWINKLE if j % 2 == 0 else ['U'], 33 - (0 if j % 2 == 0 else -1), 5 if j % 2 == 0 else 6)
        f.put(31, 10, 'U' if j % 4 < 2 else 'Y')


def awe(f, t, n):
    """Looks up wide-eyed into a beam of light, arms slowly rising."""
    k = t % n
    for ex in (5, 12, 20, 28, 35):
        steps = 18
        for s in range(steps):
            if (s - k) % 3 == 0:
                f.put(20 + (ex - 20) * s / steps, 4 + s, 'Y' if ex == 20 else 'y')
    f.disc(20, 2.5, 3, 'U')
    f.disc(20, 2.5, 1.5, 'W')
    P.falling(f, ['U'], t, n, count=6, seed=3, top=6, bottom=22, sway=2, xs=(6, 34))
    lv = int(tri(t, n) * 3.99)
    a = ['side', 'mid', 'high', 'up'][lv]
    clawd(f, y=BY - (1 if lv == 3 else 0), h=12 + (1 if lv == 3 else 0), eyes='big', lookv=-1, la=a, ra=a)


def meditate(f, t, n):
    """Floats cross-legged, eyes closed, calm ripples spreading on the floor."""
    dy = int(round(1.5 * sin(t, n))) - 6
    for j in range(2):
        p = (t / n + j / 2) % 1
        rx = 9 + p * 12
        c = 'P' if p < 0.5 else 'p'
        for i in range(48):
            a = i * math.pi / 24
            if i % 2 == 0:
                f.put(20 + rx * math.cos(a), 36 + (1.5 + rx * 0.12) * math.sin(a), c)
    sw = 12 + (dy + 6) * 2
    f.rect(20 - sw // 2, 36, sw, 1, 'G')
    P.rising(f, ['p'], t, n, 20, 30, count=4, height=22, jitter=15, seed=8, sway=1)
    info = clawd(f, y=BY + dy, leg_h=0, eyes='closed', la='low', ra='low')
    x, y, w, h = info['x'], info['y'], info['w'], info['h']
    f.rect(x - 2, y + h, w + 4, 2, 'O')
    f.rect(x + 4, y + h, w - 8, 1, 'o')
    f.put(x + 7, y + h + 1, 'o'); f.put(x + 8, y + h + 1, 'o')
    P.sparkles(f, t, n, [(4, 8), (35, 11), (9, 3)])


def calm_down(f, t, n):
    """Steaming mad, takes three deep breaths and cools off... then snaps again."""
    k = t % n
    if k < 18:
        anger = 1 - k / 17
        j = k % 6
        h = [12, 13, 14, 14, 13, 12][j]
        arms = ['side', 'side', 'mid', 'mid', 'side', 'side'][j]
        e = 'angry' if k < 2 else 'closed'
    elif k < 22:
        anger, h, arms, e = 0, 12, 'side', 'happy'
    else:
        anger, h, arms, e = 1, 12, 'low', 'angry'
    shake = (1 if k % 2 else -1) if anger > 0.8 else 0
    info = clawd(f, x=BX + shake, y=33 - h, h=h, eyes=e, la=arms, ra=arms)
    x, y, w = info['x'], info['y'], info['w']
    if k < 18 and k % 6 in (4, 5):
        puff(f, x + w + 1 + (k % 6 - 4) * 2, y + 4 - (k % 6 - 4), (k % 6 - 4) / 2 + 0.2)
    if k < 18 and k % 6 in (0, 1, 2) and k > 2:
        f.text('IN', x + w + 2, y - 3, 'B')
    if anger > 0.35:
        steam(f, info, k, gap=1 if anger > 0.7 else 0)
    if anger > 0.6 or k >= 22:
        f.art(P.VEIN2, x + w - 5, y - 6 + (k % 2))
    if 18 <= k < 22:
        P.sparkles(f, k, n, [(6, 16), (33, 14), (20, 12)])


def jiayou(f, t, n):
    """Pumps a big '加油!' sign overhead with each hop."""
    k = t % n
    s = (k // 2) % 2
    P.sign(f, 3, 2 - 2 * s, '加油!', c='U', edge='R', tc='R')
    clawd(f, y=BY - 2 * s, legs=(1, 1, 1, 1) if s else (0, 0, 0, 0), la='up', ra='up',
          eyes='happy' if s else 'closed')
    if s:
        f.art(['U.U', '.U.', 'U.U'], 1, 22)
        f.art(['U.U', '.U.', 'U.U'], 36, 20)
    else:
        f.put(2, 23, 'U'); f.put(37, 21, 'U')


def nihao(f, t, n):
    """Waves hello while a '你好' speech bubble types itself out."""
    k = t % n
    s = (k // 2) % 2
    clawd(f, x=BX - 5, y=BY - (1 if k % 4 == 1 else 0), eyes='happy', ra='up' if s else 'wave')
    bx, by, bw, bh = 12, 2, 28, 15
    P.speech(f, bx, by, bw, bh, c='B', tail='left', tail_x=14)
    if k < 4:
        for i in range(min(3, k + 1)):
            f.rect(bx + 9 + i * 4, by + 7, 2, 2, 'W')
    else:
        P.cjk(f, '你' if k < 7 else '你好', bx + 2, by + 3, 'W')


def high_five(f, t, n):
    """A mini buddy leaps up to smack Clawd's raised hand - SLAP! - then they both celebrate."""
    k = t % n
    path = {3: (27, 24), 4: (25, 19), 5: (23, 17), 6: (23, 17), 7: (25, 20), 8: (27, 25)}
    big_e = 'happy' if 5 <= k <= 14 else ('big' if k in (3, 4) else 'normal')
    clawd(f, x=3, eyes=big_e, look=1, ra='up' if 1 <= k <= 9 else 'side',
          y=BY - (1 if k in (5, 6) else 0), h=12 + (1 if k in (5, 6) else 0))
    if k in path:
        mx, my = path[k]
        mini(f, mx, my, eyes='happy' if k >= 5 else 'big', la='up', ra='high', legs=(1, 1, 1, 1))
    elif k == 2 or k == 9:
        mini(f, 27, 29, eyes='closed', legs=(1, 1, 1, 1), la='low', ra='low')
        P.dust(f, 25, GROUND, 0.4); P.dust(f, 36, GROUND, 0.4, flip=True)
    else:
        hop = -2 if k in (11, 13) else 0
        mini(f, 28, 28 + hop, eyes='happy' if k >= 10 else 'normal', look=-1 if k < 2 else 0,
             la='high' if hop else 'side', ra='high' if hop else 'side', legs=(1, 1, 1, 1) if hop else (0, 0, 0, 0))
    if k in (5, 6):
        f.art(P.SPARK_BIG, 18, 12)
        for i in range(8):
            a = i * math.pi / 4 + (math.pi / 8 if k == 6 else 0)
            f.line(21 + math.cos(a) * 5, 15 + math.sin(a) * 4, 21 + math.cos(a) * 7, 15 + math.sin(a) * 6, 'F')
        f.text('SLAP', 13, 2 + (k - 5), 'R')
    if 10 <= k <= 15:
        P.sparkles(f, k, n, [(6, 12), (35, 14), (20, 8), (12, 4), (29, 5)])


def comfort(f, t, n):
    """Pats a crying mini-Clawd on the head until it cheers up."""
    k = t % n
    happy = 8 <= k < 18
    patting = k < 14
    pat = (k // 2) % 2 == 1 and patting
    mx, my = 27, 28 + (1 if pat else 0)
    sob = (k % 2) if not happy else 0
    hop = -2 if k in (12, 13) else 0
    mini(f, mx, my + sob + hop, eyes='happy' if happy else ('normal' if k >= 18 else 'closed'),
         legs=(sob,) * 4 if not hop else (1, 1, 1, 1), la='high' if hop else 'side', ra='high' if hop else 'side')
    if not happy and k < 8:
        for i, ex in enumerate((mx + 1, mx + 6)):  # under the mini's closed eyes
            dd = (k + i) % 4
            f.rect(ex, my + 3 + dd + sob, 1, 2, 'B')
    clawd(f, x=3, view='qr', eyes='happy' if happy else 'normal', ra='none' if patting else 'side')
    if patting:
        if pat:
            f.rect(19, 24, 9, 3, 'O'); f.rect(28, 25, 5, 4, 'O'); f.rect(28, 28, 5, 1, 'o')
        else:
            f.rect(19, 23, 9, 3, 'O'); f.rect(28, 21, 5, 4, 'O'); f.rect(28, 24, 5, 1, 'o')
            f.art(['g.g', '.g.'], 29, 18)
    if 9 <= k <= 17:
        hy = 18 - (k - 9)
        f.art(P.HEART if k % 4 < 2 else HEART5, 21 - (k % 4 >= 2), hy)


# =========================================================================== anger & sulking
def furious_stomp(f, t, n):
    """Stomping so hard the floor shakes; steam out of both sides, vein throbbing."""
    k = t % n
    s = (k // 2) % 2
    L = Canvas()
    info = clawd(L, x=BX + (k % 2), y=BY + (k % 2), legs=(2, 0, 2, 0) if s else (0, 2, 0, 2), eyes='angry',
                 la='high' if s else 'mid', ra='mid' if s else 'high')
    shake = 1 if k % 4 == 0 else -1 if k % 4 == 2 else 0
    f.blit(L.shift(shake, 0))
    x, y, w = info['x'], info['y'], info['w']
    steam(f, info, k)
    if k % 2 == 0:
        for gx in (x - 3, x + w + 1):
            f.rect(gx, 35, 2, 1, 'g')
        f.art(['g.g', '...'], x - 4, 33)
        f.art(['g.g', '...'], x + w + 1, 33)
    f.art(P.VEIN2 if k % 2 else P.VEIN, x + w - 5, y - 6)
    if k % 4 < 2:
        f.text('GRR', 2, 4 + (k % 2), 'R')


def boiling(f, t, n):
    """A thermometer beside it climbs into the red until it whistles like a kettle."""
    k = t % n
    if k <= 11:
        level = k / 11
    elif k <= 15:
        level = 1
    else:
        level = (19 - k) / 4
    whistle = 12 <= k <= 15
    tx = 33
    T = Canvas()
    T.rect(tx, 6, 3, 22, 'W')
    T.disc(tx + 1.5, 30.5, 3.2, 'W')
    outlined(f, T, 'g')
    f.disc(tx + 1.5, 30.5, 2.2, 'R')
    fh = int(round(level * 20))
    if fh:
        f.rect(tx + 1, 28 - fh, 1, fh + 1, 'R')
    for yy in range(8, 27, 4):
        f.put(tx - 2, yy, 'g')
    shake = (1 if k % 2 else -1) if level > 0.6 else 0
    e = 'normal' if k < 4 else 'angry' if k < 12 else 'squint' if whistle else 'blink'
    info = clawd(f, x=BX - 4 + shake, y=BY - (1 if whistle else 0), h=12 + (1 if whistle else 0), eyes=e,
                 la='up' if whistle else ('high' if level > 0.6 else 'side'),
                 ra='up' if whistle else ('high' if level > 0.6 else 'side'))
    x, y, w = info['x'], info['y'], info['w']
    cx = x + w // 2
    if 6 <= k <= 15:
        f.art(P.VEIN2 if k % 2 else P.VEIN, x + w - 5, y - 6)
    if whistle:
        j = k - 12
        for i in range(15):
            yy = y - 2 - i
            wd = 2 + i // 4
            off = int(round(math.sin((i + j * 2) * 0.9)))
            f.rect(cx - wd // 2 + off, yy, wd, 1, 'L' if (i + j) % 3 else 'G')
        f.art(P.PUFF, cx - 5 + (j % 2) * 2, max(0, y - 19 + (j % 2)))
        f.art(['.C', 'C.', '.C'] if j % 2 else ['C.', '.C', 'C.'], cx - 8, y - 7)
        f.art(['C.', '.C', 'C.'] if j % 2 else ['.C', 'C.', '.C'], cx + 7, y - 7)
    if 16 <= k <= 18:
        puff(f, x + w + 1, y + 2, (k - 16) / 2)


def tantrum(f, t, n):
    """Full meltdown on its back: kicking, flailing, wailing."""
    k = t % n
    s = k % 2
    L = Canvas()
    clawd(L, y=12, leg_h=5, legs=(0, 3, 1, 4) if s else (3, 0, 4, 1), la='high' if s else 'low',
          ra='low' if s else 'high', eyes='squint')
    L = land(L.flipy()).shift(0, -(k % 4 == 1))
    f.blit(L)
    for lx in ((12, 25) if s else (16, 29)):
        f.art(['L.', '.L', 'L.'], lx - 2, 14 + (k % 2))
    for side, eye in zip((-1, 1), eye_spots(L)):  # tears squirt out of the eyes, sideways
        for i in range(2):
            p = ((k + i * 2 + (1 if side > 0 else 0)) % 4) / 4
            P.tear_spray(f, eye, p, side, reach=9, rise=10, fall=12)
    P.dust(f, 5, GROUND, (k % 4) / 4)
    P.dust(f, 33, GROUND, ((k + 2) % 4) / 4, flip=True)
    f.text('WAAH', 12 + (k % 2), 4 + (k // 2) % 2, 'B')


def grumpy_pout(f, t, n):
    """Arms crossed, turns away with a HMPH, peeks... and turns the other way."""
    k = t % n
    if k < 6:
        v, e, lk = 'ql', 'closed', 0
    elif k < 10:
        v, e, lk = 'front', 'blink', 1 if k < 8 else -1
    elif k < 15:
        v, e, lk = 'qr', 'closed', 0
    else:
        v, e, lk = 'front', 'closed', 0
    info = clawd(f, view=v, eyes=e, look=lk, lookv=-1 if e == 'closed' else 0, la='short', ra='short',
                 tilt=1 if v != 'front' else 0)
    x, y, w = info['x'], info['y'], info['w']
    fold_arms(f, info, dy=8, view=v)
    if 1 <= k <= 4:
        p = (k - 1) / 3
        puff(f, x - 4 - int(p * 4), y + 3 - int(p * 3), p)
        if k <= 2:
            f.text('HMPH', 1, y - 9, 'R')
    if 11 <= k <= 14:
        p = (k - 11) / 3
        puff(f, x + w + 2 + int(p * 4), y + 3 - int(p * 3), p)
        if k <= 12:
            f.text('HMPH', 23, y - 9, 'R')


def puffed_cheeks(f, t, n):
    """Holds its breath until it balloons up a little... then deflates with a long PFFF."""
    k = t % n
    sizes = [(16, 12), (16, 12), (17, 12), (17, 13), (18, 13), (19, 13), (19, 14), (20, 14), (20, 14),
             (20, 14), (19, 13), (18, 13), (17, 12), (16, 12), (16, 12), (16, 12)]
    w, h = sizes[k]
    infl = 2 <= k <= 9
    defl = 10 <= k <= 13
    dx = (1 if k % 2 else -1) if k == 9 else ([-1, -2, -2, -1][k - 10] if defl else 0)
    info = clawd(f, x=20 - w // 2 + dx, y=33 - h, w=w, h=h,
                 eyes='squint' if infl else ('closed' if defl else ('happy' if k == 14 else 'normal')),
                 la='short' if w > 18 else 'side', ra='short' if w > 18 else 'side')
    x, y = info['x'], info['y']
    if infl and k >= 5:
        f.art(['.g.', 'g.g'], x - 3, y - 2 - (k % 2))
        f.art(['.g.', 'g.g'], x + w, y - 2 - (k % 2))
    if defl:
        for i in range(k - 9):
            f.art(P.PUFF if i % 2 else P.PUFF_S, x + w + 2 + i * 4, y + 5 - i)
        f.text('PFF', 26, y - 8, 'B')


def jealous_sideye(f, t, n):
    """Wringing a hanky and side-eyeing a mini-Clawd swimming in hearts - looks away when caught."""
    k = t % n
    caught = 8 <= k < 12
    bob = 1 if k % 4 == 2 else 0
    mini(f, 28, 28 - bob, eyes='normal' if caught else 'happy', look=-1 if caught else 0,
         la='high', ra='high')
    f.art(P.HEART_BIG if k % 4 < 2 else HEART5, 29 if k % 4 < 2 else 30, 19 if k % 4 < 2 else 20)
    P.rising(f, ['Z.Z', '.Z.'], t, n, 32, 17, count=2, height=12, jitter=6, seed=6)
    tug = k % 2
    info = clawd(f, x=1, eyes='normal' if caught else 'focus', look=-1 if caught else 1,
                 lookv=-1 if caught else 0, la='short', ra='short')
    x, y, w = info['x'], info['y'], info['w']
    hy = y + 10
    H = Canvas()
    H.rect(x + 3, hy + tug, 4, 2, 'W')
    H.rect(x + 9, hy + 1 - tug, 4, 2, 'W')
    H.rect(x + 6, hy + 1, 4, 1, 'W')
    H.put(x + 4, hy + 2 + tug, 'W'); H.put(x + 11, hy + 3 - tug, 'W')
    outlined(f, H, 'G')
    f.rect(x + 1, hy + tug, 2, 2, 'o'); f.rect(x + 13, hy + 1 - tug, 2, 2, 'o')
    if caught:
        f.art(P.SWEAT, x + w + 1, y - 2 + (k - 8))
        f.art(P.NOTE, x - 1 + (k % 2), y - 8 - (k - 8), cmap={'K': 'B'})
    else:
        sc = [['.P.P.', 'P.P.P', '.P.P.'], ['P.P.P', '.P.P.', 'P.P.P']][k % 2]
        f.art(sc, x + 6, y - 6)
        if k % 4 < 2:
            f.text('GRR', x + 1, y - 13, 'E')


def sulk_cloud(f, t, n):
    """Sits sulking while its own personal rain cloud drizzles on it."""
    k = t % n
    f.rrect(5, 35, 30, 2, 'S')
    for i, px in enumerate((9, 30)):
        p = ((k + i * 4) % 8) / 8
        wd = 1 + int(p * 6)
        f.rect(px - wd // 2, 36 if p < 0.5 else 35, wd, 1, 'B')
    info = clawd(f, y=BY + 2, leg_h=1, eyes='sad', top=True, la='low', ra='low', lookv=1)
    bob = 1 if (k // 4) % 2 else 0
    P.cloud(f, 11, 5 + bob, c='g', w=18)
    f.rect(14, 5 + bob, 6, 1, 'G')
    P.rain(f, t, n, 13, 27, 12 + bob, 21, c='B', count=7)
    if k % 4 == 1:
        f.put(15, 22, 'S'); f.put(24, 22, 'S')
    d = k % 8
    f.put(info['x'] + 16 + (1 if d > 4 else 0), info['y'] + 2 + d, 'B')


def sob_fountain(f, t, n):
    """Wailing with tears spraying out in fountains on both sides."""
    k = t % n
    b = k % 2
    f.rrect(0, 35, 9, 2, 'S')
    f.rrect(31, 35, 9, 2, 'S')
    info = clawd(f, y=BY + b, h=12 - b, eyes='closed', la='low', ra='low')
    for side, eye in zip((-1, 1), sorted(info['eyes'])):  # fountains leave the eyes
        for i in range(6):
            p = (t / n + i / 6) % 1
            P.tear_spray(f, eye, p, side)
    f.text('WAAH', 13, 6 + b, 'B')


def pretty_please(f, t, n):
    """Wobbly pleading eyes, hands wringing, trembling - pretty please?"""
    k = t % n
    L = Canvas()
    info = clawd(L, y=BY + (1 if k % 4 == 3 else 0), h=12 - (1 if k % 4 == 3 else 0),
                 eyes='worried' if k % 6 < 4 else 'big', la='short', ra='short')
    x, y = info['x'], info['y']
    s = k % 2
    L.rect(x + 3, y + 9 - s, 5, 2, 'o'); L.rect(x + 8, y + 8 + s, 5, 2, 'o')
    tilt = 0.05 if (k // 4) % 3 == 0 else -0.05 if (k // 4) % 3 == 2 else 0
    f.blit(L.shear(tilt))
    for i, eye in enumerate(sorted(info['eyes'])):
        p = ((k + i * 5) % 12) / 12
        if p < 0.7:
            P.tear(f, eye, p / 0.7, screen_right=bool(i))
    for i, (px, py) in enumerate(((x - 5, y - 3), (x + 19, y - 1))):
        if (k + i * 2) % 4 == 0:
            f.art(TWINKLE, px, py)
    P.say(f, info, 'PLS', dy=-1)


def heartbreak(f, t, n):
    """A heart above its head cracks, splits and shatters - then slowly mends."""
    k = t % n
    e = ['normal', 'normal', 'big', 'big', 'big', 'sad', 'sad', 'sad', 'sad', 'sad', 'closed', 'closed', 'closed',
         'closed', 'sad', 'normal'][k]
    info = clawd(f, eyes=e, top=5 <= k <= 13, la='low' if 5 <= k <= 13 else 'side',
                 ra='low' if 5 <= k <= 13 else 'side')
    hx, hy = 16, 8
    if k <= 1:
        heart_halves(f, hx, hy - k)
    elif k == 2:
        heart_halves(f, hx + (1 if t % 2 else 0), hy, crack=True)
    elif k <= 10:
        j = k - 3
        sep = [1, 2, 3, 5, 7, 9, 10, 11][j]
        dy = [0, 0, 2, 5, 9, 14, 20, 26][j]
        heart_halves(f, hx, hy, sep=sep, dyl=dy, dyr=dy + (1 if j >= 3 else 0), crack=True)
    elif k <= 13:
        rr = rng(5)
        spread = (k - 10) * 3
        for i in range(10 - (k - 11) * 3):
            side = -1 if i % 2 else 1
            px = 20 + side * (10 + rr.randint(0, 4) + spread)
            py = 34 - rr.randint(0, 3) - (2 if k == 11 else 0)
            f.put(px, py, 'Z')
            if i % 3 == 0:
                f.put(px + 1, py, 'Z')
    elif k == 14:
        f.art(HEART5, 18, 9, cmap={'Z': 'r'})
    else:
        f.art(P.HEART_BIG, 17, 8, cmap={'Z': 'r'})
    if 10 <= k <= 13:
        el, er = sorted(info['eyes'])
        P.tear(f, el, (k - 10) / 4)
        P.tear(f, er, (k - 9.5) / 4, screen_right=True)


def lonely_spotlight(f, t, n):
    """Sits alone in a pool of light while a tumbleweed rolls by."""
    k = t % n
    for y in range(0, 36):
        half = 3 + y * 0.32
        f.rect(int(round(20 - half)), y, int(round(2 * half)), 1, 'T')
    f.rrect(5, 35, 30, 2, 'y')
    tx = -8 + int(round(52 * t / n))
    look = -1 if tx < 12 else (1 if tx > 22 else 0)
    hop = [0, 2, 3, 2, 0][k % 5]
    f.art(TUMBLE[k % 2], tx, 27 - hop)
    if hop == 0:
        P.dust(f, tx - 2, 34, 0.4)
    info = clawd(f, y=BY + 2, leg_h=1, eyes='sad', look=look, lookv=1, la='low', ra='low', top=True)
    if 12 <= k <= 15:
        puff(f, info['x'] + 9, info['y'] - 2 - (k - 12), (k - 12) / 3)


def sad_shuffle(f, t, n):
    """Head hung low, dragging its feet slowly across the screen."""
    x = -18 + int(round(60 * t / n))
    s = (t // 2) % 2
    info = clawd(f, x=x, y=BY + 1, h=11, view='qr', top=True, lookv=1, eyes='sad', la='low', ra='low',
                 legs=walk(s))
    k = t % 16
    if 4 <= k <= 9:
        p = (k - 4) / 5
        puff(f, x + 17 + int(p * 3), info['y'] - 1 - int(p * 5), p)


def gloom(f, t, n):
    """Slumped and blank-eyed, a purple aura wisping up all around it."""
    k = t % n
    sink = 1 if k >= 6 else 0
    for j in range(7):
        p = (t / n + j / 7) % 1
        wx = BX - 4 + j * 4 + int(round(math.sin(p * 6.28 + j) * 1))
        base = BY + 4 if j in (0, 6) else BY
        wy = base - 2 - int(p * 12)
        f.art(['.p', 'P.', '.P'] if j % 2 else ['p.', '.P', 'P.'], wx, wy)
    info = clawd(f, y=BY + sink, h=12 - sink, eyes='dot', lookv=1, la='low', ra='low', top=True)
    x, y, w = info['x'], info['y'], info['w']
    for i, gx in enumerate((x - 3, x - 5, x + w + 2, x + w + 4)):
        ln = 2 + (i + k) % 3
        f.rect(gx, y + 1 + (i % 2) * 2, 1, ln, 'V')
    if 8 <= k <= 11:
        puff(f, x + w + 1, y - 2 - (k - 8), (k - 8) / 3, c='p')


def bored_sigh(f, t, n):
    """Flopped flat on the floor, tapping, sighing, while a fly buzzes around."""
    k = t % n
    tap = (k // 2) % 2 if k < 8 else 0
    sigh = 10 <= k <= 13
    info = clawd(f, y=27, h=9, leg_h=0, eyes='blink', la='out', ra='mid' if tap else 'out')
    x, y, w = info['x'], info['y'], info['w']
    if k < 8 and not tap:
        f.art(['g.g'], x + w + 3, y + 4)
    if sigh:
        p = (k - 10) / 3
        puff(f, x + w // 2 + 2 + int(p * 3), y - 3 - int(p * 5), p)
    P.orbit(f, 20, 18, 11, 4, t, n, P.FLY, count=1, cmap={'k': 'g'}, speed=2)


def impatient_tap(f, t, n):
    """Arms folded, foot tapping, watching the clock... and waiting."""
    k = t % n
    tap = k % 2
    info = clawd(f, legs=(0, 0, 0, 2) if tap else (0, 0, 0, 0), legdx=(0, 0, 0, 1) if tap else (0, 0, 0, 0),
                 eyes='blink', look=1 if 4 <= k < 8 else 0, lookv=-1 if 4 <= k < 8 else 0, la='short', ra='short')
    x, y, w = info['x'], info['y'], info['w']
    fold_arms(f, info, dy=8)
    if not tap:
        f.art(['..g', '.g.', '...', 'g..'], x + w + 1, 32)
        f.text('TAP', 29, 19 - (k // 2) % 2, 'g')
    clock(f, 31, 9, k, n)
    if k % 2 == 0:
        f.art(['g.', '.g'], 25, 3); f.art(['.g', 'g.'], 36, 3)
    if k >= 8:
        f.art(P.VEIN, x + 1, y - 4)


# =========================================================================== surprise & fear
def shock_jump(f, t, n):
    """Calm... then a huge startled leap with a red '!'."""
    k = t % n
    if k < 4:
        clawd(f, eyes='blink' if k == 2 else 'normal')
        return
    if k < 9:
        dy = [-8, -10, -10, -7, -3][k - 4]
        info = clawd(f, x=BX + 1, w=14, h=15, y=BY - 3 + dy, la='up', ra='up', eyes='big')
        f.art(EXBIG, 19, max(0, info['y'] - 10))
        cx, cy = 20, info['y'] + 7
        if k <= 6:
            for i in range(8):
                a = i * math.pi / 4 + math.pi / 8
                f.line(cx + math.cos(a) * 12, cy + math.sin(a) * 9, cx + math.cos(a) * 14, cy + math.sin(a) * 11,
                       'R')
        return
    if k == 9:
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='closed')
        P.dust(f, BX - 4, GROUND, 0.5); P.dust(f, BX + 19, GROUND, 0.5, flip=True)
        return
    r = rng(k)
    info = clawd(f, x=BX + r.choice((-1, 1)), eyes='big' if k < 13 else 'normal', la='low', ra='low')
    f.art(P.SWEAT, info['x'] + info['w'] + 1, info['y'] - 1 + (k - 10))


def relieved(f, t, n):
    """Sweating bullets... wipes its brow, flicks the sweat away and lets out a big PHEW."""
    k = t % n
    if k < 4:
        r = rng(k + 3)
        info = clawd(f, x=BX + r.choice((-1, 0, 1)), eyes='worried', la='low', ra='low')
        x, y, w = info['x'], info['y'], info['w']
        f.art(P.SWEAT, x + w + 1, y - 1 + k)
        f.art(P.SWEAT, x - 3, y + 1 + (k + 2) % 4, flip=True)
        return
    if k < 8:
        j = k - 4
        info = clawd(f, eyes='worried' if j < 2 else 'closed', ra='none', la='side')
        x, y, w = info['x'], info['y'], info['w']
        hx = x + w - 5 - j * 3
        f.rect(x + w, y + 1, 3, 4, 'O')
        f.rect(hx, y, x + w - hx, 2, 'o')
        f.rect(x + w - 1, y, 2, 2, 'o')
        if j <= 1:
            f.art(P.SWEAT, hx - 3, y - 2)
        if j == 3:
            f.art(['.C', 'CC', 'CB'], x - 5, y - 5)
            f.art(['C..', '...', '..C'], x - 3, y - 7)
        elif j == 2:
            f.art(['.C', 'CC'], x - 1, y - 5)
        return
    if k < 12:
        j = k - 8
        hh = [11, 10, 10, 11][j]
        info = clawd(f, x=BX - (1 if hh == 10 else 0), w=17 if hh == 10 else 16, y=33 - hh, h=hh,
                     eyes='closed', la='low', ra='low')
        x, y, w = info['x'], info['y'], info['w']
        puff(f, x + w + 2 + j, y - 1 - j, j / 3)
        f.text('PHEW', 2, 8 - (j % 2), 'B')
        return
    clawd(f, eyes='happy' if k < 15 else 'normal', y=BY - (1 if k == 12 else 0))
    P.sparkles(f, k, n, [(6, 14), (33, 15), (20, 11)])


def scared_shrink(f, t, n):
    """Crouched and shaking all over, shiver lines and cold sweat."""
    r = rng(t * 7 + 1)
    dx, dy = r.choice((-1, 0, 1)), r.choice((0, 1))
    info = clawd(f, x=BX + 1 + dx, y=BY + 3 + dy, w=14, h=10 - dy, eyes='big' if (t // 2) % 2 else 'worried',
                 la='high', ra='high')
    x, y, w = info['x'], info['y'], info['w']
    o = t % 2
    f.art(['S.', '.S', 'S.', '.S', 'S.'] if o else ['.S', 'S.', '.S', 'S.', '.S'], x - 7, y + 1)
    f.art(['.S', 'S.', '.S', 'S.', '.S'] if o else ['S.', '.S', 'S.', '.S', 'S.'], x + w + 5, y + 1)
    for i, gx in enumerate((x + 2, x + 5, x + 8, x + 11)):
        f.rect(gx, y - 5 + (i + t) % 2, 1, 3, 'B')
    f.art(P.SWEAT, x + w + 1, y - 2 + t % 3)
    if t % 4 < 2:
        f.text('EEK', 3, 6, 'B')


def nervous_sweat(f, t, n):
    """Eyes darting, fingers poking together, sweat drops sliding off."""
    k = t % n
    look = [0, -1, -1, 0, 1, 1, 0, -1, 1, 0, 0, -1, 1, 1, 0, 0][k]
    info = clawd(f, eyes='worried', look=look, la='none', ra='none')
    x, y, w = info['x'], info['y'], info['w']
    if k % 2:
        f.rect(x + 3, y + 8, 5, 2, 'o'); f.rect(x + 8, y + 8, 5, 2, 'o')
    else:
        f.rect(x + 2, y + 8, 5, 2, 'o'); f.rect(x + 9, y + 8, 5, 2, 'o')
    f.rect(x - 1, y + 6, 1, 4, 'O'); f.rect(x + w, y + 6, 1, 4, 'O')
    for i, (sx, side) in enumerate(((x + w + 1, 1), (x - 3, -1), (x + w - 3, 0))):
        p = (t / n + i / 3) % 1
        sy = y - 3 + int(p * 16)
        if side == 0:
            sy = y - 7 + int(p * 3)
            if p > 0.5:
                continue
        f.art(['.C', 'CC', 'CB'] if side >= 0 else ['C.', 'CC', 'BC'], sx, sy)


def panic_circles(f, t, n):
    """Runs around in frantic circles, arms flailing, sweat flying."""
    for i in range(18):
        a = i * math.pi * 2 / 18
        f.put(20 + 11 * math.cos(a), 37 + 1.6 * math.sin(a), 'G')
    a = 2 * math.pi * t / n
    x = 12 + int(round(10 * math.cos(a)))
    yy = BY - 1 + int(round(2 * math.sin(a)))
    right = math.sin(a) < 0
    s = t % 2
    clawd(f, x=x, y=yy, view='qr' if right else 'ql', eyes='big',
          la='up' if s else 'wave', ra='wave' if s else 'up', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2))
    bx = x - 3 if right else x + 18
    f.art(['.C', 'CC', 'CB'], bx, yy + 1 + s)
    P.dust(f, x - 2 if right else x + 17, GROUND + (1 if math.sin(a) > 0 else 0), ph(t, 3), flip=not right)
    if t % 4 < 2:
        f.art(EXBIG, x + 7, max(0, yy - 11))


def mind_blown(f, t, n):
    """A thought so big it goes BOOM behind its head - knocked flat, smoke and confetti everywhere."""
    k = t % n
    if 4 <= k <= 9:
        q = (k - 4) / 5
        r = 5 + q * 13
        for i in range(12):
            a = i * math.pi / 6 + (math.pi / 12 if k % 2 else 0)
            f.line(20 + math.cos(a) * r * 0.45, 14 + math.sin(a) * r * 0.35,
                   20 + math.cos(a) * r, 14 + math.sin(a) * r * 0.75, 'U' if i % 2 else 'F')
        if k <= 6:
            f.disc(20, 14, 5 - (k - 4) * 1.5, 'F')
            f.disc(20, 14, 3 - (k - 4), 'U')
    if 4 <= k <= 6:
        f.text('BOOM', 13, 1 + (k % 2), 'R')
    if 5 <= k <= 12:
        q = (k - 4) / 9
        cols = 'RFUEBPZC'
        for i in range(8):
            vx = (i - 3.5) * 2.4
            vy = 16 + (i % 3) * 3
            px = 20 + vx * q * 2
            py = 14 - vy * q + 34 * q * q
            f.rect(int(px), int(py), 1 + (i % 2), 1 + ((i + 1) % 2), cols[i])
    if k < 4:
        e = ['normal', 'big', 'big', 'squint'][k]
        info = clawd(f, x=BX + ((k % 2) * 2 - 1 if k == 3 else 0), eyes=e,
                     la='mid' if k >= 2 else 'side', ra='mid' if k >= 2 else 'side')
        if k >= 1:
            f.art(['U.U', '.U.', 'U.U'] if k % 2 else ['.U.', 'UUU', '.U.'], 19, info['y'] - 6)
    elif k == 4:
        info = clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='x', la='out', ra='out')
    elif k <= 6:
        info = clawd(f, x=BX + 1, w=14, h=14, y=BY - 2, eyes='big', la='up', ra='up')
    else:
        sw = [1, 0, -1, -1, 0, 1, 1, 0, 0][k - 7]
        L = Canvas()
        info = clawd(L, eyes='x' if k <= 12 else ('blink' if k == 14 else 'normal'), la='low', ra='low')
        f.blit(L.shear(0.06 * sw))
    y = info['y']
    if 6 <= k <= 13:
        for j in range(2):
            p = ((k - 6) / 8 + j / 2) % 1
            f.art(P.PUFF if j else P.PUFF_S, 15 + j * 7 + int(math.sin(p * 6) * 2), y - 5 - int(p * 9))
    if 7 <= k <= 12:
        P.orbit(f, 20, y - 3, 9, 2, k, 6, ['.U.', 'UUU', '.U.'], count=2)


def dizzy_spiral(f, t, n):
    """X-eyed and staggering about with stars orbiting its head."""
    k = t % n
    sway = sin(t, n)
    L = Canvas()
    info = clawd(L, x=BX + int(round(2 * sway)), eyes='x' if k % 6 < 5 else 'squint',
                 legs=((1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 0, 0))[k % 4],
                 la='high' if sway > 0 else 'low', ra='low' if sway > 0 else 'high')
    f.blit(L.shear(0.1 * sway))
    P.orbit(f, 20 + int(round(4 * sway)), info['y'] - 4, 10, 2, t, n, ['.U.', 'UUU', '.U.'], count=3)
    sp = ['.CC.', 'C..C', 'C.C.', '.C..']
    f.art(sp if k % 2 else [r[::-1] for r in sp], 3, 8 + (k % 3))
    f.art([r[::-1] for r in sp] if k % 2 else sp, 33, 10 - (k % 3))


def confused_tilt(f, t, n):
    """Head tilts one way, then the other, scratching its head under a big '?'."""
    k = t % n
    side = 1 if k < 8 else -1
    j = k % 8
    tilt = [0, 0.06, 0.12, 0.12, 0.12, 0.12, 0.06, 0][j]
    scratch = 2 <= j <= 5
    arm = ('up' if k % 2 else 'wave') if scratch else 'side'
    L = Canvas()
    clawd(L, eyes='big' if side > 0 else 'dot', eyes_r='dot' if side > 0 else 'big',
          ra=arm if side > 0 else 'side', la=arm if side < 0 else 'side')
    f.blit(L.shear(tilt * side))
    if j >= 1:
        qx = 30 if side > 0 else 5
        f.art(QBIG, qx, 8 - (1 if k % 4 < 2 else 0))
        if 3 <= j <= 6:
            f.art(['CC.', '..C', '.C.', '...', '.C.'], qx + (-5 if side > 0 else 7), 4)


def awkward_crickets(f, t, n):
    """Frozen in awkward silence. Somewhere, a cricket chirps."""
    k = t % n
    look = 1 if 5 <= k <= 10 else 0
    info = clawd(f, x=5, eyes='line', look=look)
    x, y, w = info['x'], info['y'], info['w']
    f.art(P.SWEAT, x - 3, y + 1 + k // 4)
    P.speech(f, x + 1, y - 11, 13, 7, c='B', tail='left')
    for i in range(3):
        f.rect(x + 4 + i * 3, y - 8, 2, 1, 'W')
    hop = -2 if k in (12, 13) else 0
    f.art(CRICKET, 32, 32 + hop)
    if k % 4 < 2 and hop == 0:
        f.text('CRI', 27 + (k % 2), 24 - (k % 2), 'E')


def cringe(f, t, n):
    """Spots something gross, recoils, shudders all over - EW - and turns away."""
    k = t % n
    f.art(BLOB[k % 2], 31, 30)
    for i in range(2):
        p = ((k / 4) + i / 2) % 1
        f.art(['.e', 'e.', '.e'] if (k + i) % 2 else ['e.', '.e', 'e.'], 32 + i * 4, int(27 - p * 6))
    if k < 4:
        clawd(f, x=BX - 4, eyes='normal' if k < 2 else 'big', look=1)
        if k >= 2:
            f.art(['.CCC.', 'CC.CC', '...CC', '..CC.', '..C..', '.....', '..C..'], 15, 10)
        return
    if k == 4:
        L = Canvas()
        clawd(L, x=BX - 7, w=15, eyes='squint', la='high', ra='high')
        f.blit(L.shear(-0.15))
        f.art(EXBIG, 20, 9)
        return
    if k < 10:
        r = rng(k)
        L = Canvas()
        info = clawd(L, x=BX - 7 + r.choice((-1, 0, 1)), w=15, eyes='squint', la='high', ra='high',
                     y=BY + (k % 2), h=12 - (k % 2))
        f.blit(L.shear(-0.08))
        x, y, w = info['x'], info['y'], info['w']
        o = k % 2
        for sx in (x - 6, x + w + 5):
            f.art(['L.', '.L', 'L.', '.L'] if o else ['.L', 'L.', '.L', 'L.'], sx, y + 2)
        f.text('EW', 21, 10 - o, 'E')
        return
    v = 'ql'
    info = clawd(f, x=BX - 6, view=v, eyes='closed', la='low', ra='low', y=BY + (k % 2), h=12 - (k % 2))
    x, y, w = info['x'], info['y'], info['w']
    f.art(['L.', '.L', 'L.'] if k % 2 else ['.L', 'L.', '.L'], x + w + 2, y + 2)
    if k % 4 < 2:
        f.text('EW', x + w + 1, y - 7, 'E')


def embarrassed(f, t, n):
    """So flustered it hides its face and wriggles, steam puffing - peeks out... hides again."""
    k = t % n
    peek = 9 <= k <= 11
    s = (k // 2) % 2
    L = Canvas()
    info = clawd(L, x=BX + (1 if s else -1), eyes='big' if peek else 'closed', look=1 if peek else 0,
                 la='face', ra='side' if peek else 'face', legs=(1, 0, 0, 0) if s else (0, 0, 0, 1))
    f.blit(L.shear(0.06 if s else -0.06))
    x, y, w = info['x'], info['y'], info['w']
    P.rising(f, P.PUFF_S, t, n, 19, y - 3, count=3, height=12, jitter=8, seed=12)
    if not peek:
        f.art(BLUSH_MARK, x - 7, y - 1 + s)
        f.art(BLUSH_MARK, x + w + 1, y - 1 + (1 - s))
    if k < 4:
        f.text('KYAA', 2, 3 + (k % 2), 'Z')
    if k >= 12:
        f.art(P.HEART, 30, 6 - (k - 12))


def sneeze(f, t, n):
    """Ah... ah... AH... CHOO! - a big spray, a little stagger, a sniffle."""
    k = t % n
    if k < 2:
        clawd(f, eyes='normal' if k == 0 else 'blink')
        if k == 1:
            f.art(['.g', 'g.'], 30, 22)
        return
    if k < 6:
        j = k - 2
        h = 12 + [0, 1, 2, 2][j]
        a = ['side', 'mid', 'high', 'high'][j]
        info = clawd(f, y=33 - h, h=h, eyes=['blink', 'blink', 'closed', 'closed'][j], la=a, ra=a)
        f.text(['A', 'AH', 'AH.', 'AH..'][j], 22, info['y'] - 8 - j, 'B')
        return
    if k == 6:
        info = clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='squint', la='out', ra='out')
        rr = rng(2)
        cx, cy = 20, info['y'] + 4
        for i in range(18):
            a = rr.uniform(0, math.pi * 2)
            d = rr.uniform(12, 17)
            f.put(cx + math.cos(a) * d * 1.2, cy + math.sin(a) * d * 0.7, 'C' if i % 3 else 'S')
        f.art(P.PUFF, 18, info['y'] - 6)
        f.text('CHOO!', 11, 5, 'R')
        return
    if k < 9:
        clawd(f, y=BY - [3, 1][k - 7], legs=(1, 1, 1, 1) if k == 7 else (0, 0, 0, 0), eyes='x')
        rr = rng(2)
        cx, cy = 20, BY + 6
        for i in range(10):
            a = rr.uniform(0, math.pi * 2)
            d = rr.uniform(14, 18) + (k - 6) * 2
            f.put(cx + math.cos(a) * d * 1.2, cy + math.sin(a) * d * 0.6 + (k - 6) * 3, 'C')
        f.art(['.LL.', 'LLLL'], 18, BY - 9 - (k - 7) * 2)
        return
    e = ['blink', 'blink', 'normal', 'happy', 'happy', 'normal', 'blink'][k - 9]
    clawd(f, eyes=e)
    if 9 <= k <= 10:
        f.text('SNF', 26, 14 - (k - 9), 'g')


def hiccup(f, t, n):
    """Standing there awkwardly when - HIC! - it jolts into the air. Again."""
    k = t % n
    j = k % 6
    side = (k // 6) % 2
    if j == 0:
        info = clawd(f, y=BY - 3, legs=(1, 1, 1, 1), eyes='big', la='mid', ra='mid')
    elif j == 1:
        info = clawd(f, y=BY - 1, eyes='big')
    elif j == 2:
        info = clawd(f, x=BX - 1, w=18, h=11, y=BY + 1, eyes='closed')
    else:
        info = clawd(f, eyes='worried' if j < 5 else 'normal', la='short', ra='short')
        fold_arms(f, info, dy=8)
    if j <= 2:
        f.text('HIC', 27 if side else 2, BY - 9 + j, 'P')
    if 1 <= j <= 5:
        bx, by = 20 + (3 if side else -3), BY - 5 - j * 3
        f.ring(bx, by, 2 if j < 4 else 2.6, 'C')
        f.put(bx - 1, by - 1, 'W')


def facepalm(f, t, n):
    """Slaps a hand over its eyes, shakes its head, drags the hand down its face."""
    k = t % n
    if k == 0 or k == 13:
        clawd(f, eyes='blink', ra='mid' if k == 13 else 'side')
        return
    if k in (1, 2):
        clawd(f, eyes='blink', ra=['mid', 'high'][k - 1])
        return
    dx = [0, 0, 1, 0, -1, 0, 1, 0, 0, 0][k - 3] if k <= 12 else 0
    drag = {10: 2, 11: 4, 12: 6}.get(k, 0)
    info = clawd(f, x=BX + dx, y=BY + 1, h=11, top=True, eyes='blink' if drag else 'none',
                 lookv=1 if drag else 0, ra='none')
    x, y, w = info['x'], info['y'], info['w']
    f.rect(x + w, y + 2 + drag // 2, 3, 4, 'O')
    f.rect(x + 2, y + 1 + drag, 11, 4, 'o')
    f.rect(x + 12, y + 2 + drag, 4, 3, 'o')
    if k == 3:
        f.art(['U.U', '.U.', 'U.U'], x - 4, y - 3)
        f.art(['U.U', '.U.', 'U.U'], x + w + 2, y - 4)
        f.text('SMACK', 10, 2, 'R')
    if 6 <= k <= 9:
        puff(f, x - 4 - (k - 6), y + 5 - (k - 6), (k - 6) / 3)
        f.text('SIGH', 23, 9, 'g')


def eye_roll(f, t, n):
    """Rolls its eyes all the way round - UGH - and slumps."""
    k = t % n
    path = {2: (1, 0), 3: (1, -1), 4: (0, -2), 5: (-1, -1), 6: (-1, 0)}
    slump = 1 if 7 <= k <= 9 else 0
    look, lookv = path.get(k, (0, 0))
    L = Canvas()
    clawd(L, y=BY + slump, h=12 - slump, top=bool(slump), eyes='normal' if k in path else 'blink',
          look=look, lookv=lookv, la='out' if k == 7 else 'side')
    f.blit(L.shear(-0.05) if 3 <= k <= 5 else L)
    if 3 <= k <= 6:
        f.text('UGH', 25, 9 - (k % 2), 'P')
    if 7 <= k <= 10:
        puff(f, 30 + (k - 7), BY + 1 - (k - 7), (k - 7) / 3)


def yawn(f, t, n):
    """A huge stretchy yawn, then it dozes off nodding... jerks awake with a '!'."""
    k = t % n
    if k < 2 or k >= 20:
        e = 'blink' if k in (0, 1, 23) else ('big' if k == 20 else 'normal')
        info = clawd(f, eyes=e, y=BY - (2 if k == 20 else 0), legs=(1, 1, 1, 1) if k == 20 else (0, 0, 0, 0))
        if k == 20:
            f.art(EXBIG, 19, info['y'] - 9)
            f.art(['U.U', '...', 'U.U'], 9, info['y'] - 3)
        return
    if k < 10:
        j = k - 2
        h = [12, 13, 14, 14, 14, 13, 12, 12][j]
        a = ['mid', 'high', 'up', 'up', 'up', 'high', 'side', 'side'][j]
        info = clawd(f, y=33 - h, h=h, la=a, ra=a, eyes='closed' if j < 6 else 'blink')
        if 1 <= j <= 5:
            f.text('HWA' + 'A' * min(j, 3), 21 - min(j, 3) * 2, 6 - (j % 2), 'B')
        if 2 <= j <= 4:
            f.art(['.L', 'LL'], info['x'] - 3, info['y'] - 2 - j)
        return
    j = k - 10
    nod = [1, 1, 2, 2, 1, 1, 2, 3, 3, 4][j]
    info = clawd(f, y=BY + nod, h=12 - nod, top=nod >= 2, lookv=1 if nod >= 3 else 0, eyes='closed',
                 la='low', ra='low')
    P.zzz(f, info, t, n)


def mood_swings(f, t, n):
    """Happy, furious, weepy, smitten - cycling every half second."""
    k = t % n
    m, j = k // 4, k % 4
    if j == 0:
        clawd(f, x=BX - 1, w=18, h=10, y=BY + 2, eyes='closed')
        f.art(['U.U', '.U.', 'U.U'], 6, 18); f.art(['U.U', '.U.', 'U.U'], 31, 18)
        return
    if m == 0:
        dy = [0, -2, -3, -1][j]
        clawd(f, y=BY + dy, eyes='happy', la='up', ra='up', legs=(1, 1, 1, 1) if dy else (0, 0, 0, 0))
        P.sparkles(f, t, n, [(5, 14), (34, 12), (8, 28), (32, 27)])
    elif m == 1:
        info = clawd(f, x=BX + (1 if j % 2 else -1), eyes='angry', la='high', ra='high')
        f.art(P.VEIN2, info['x'] + 11, info['y'] - 6)
        steam(f, info, j)
    elif m == 2:
        info = clawd(f, y=BY + 1, h=11, top=True, eyes='sad', la='low', ra='low')
        P.cloud(f, 13, 3, c='g', w=14)
        P.rain(f, j, 4, 15, 26, 9, 19, c='B', count=5)
        P.tear(f, sorted(info['eyes'])[0], j / 4)
    else:
        L = Canvas()
        clawd(L, eyes='closed', la='mid', ra='mid')
        f.blit(L.shear(0.08 * (1 if j % 2 else -1)))
        f.art(P.HEART, 6 + j, 14 - j * 2)
        f.art(P.HEART, 31 - j, 12 - j * 2)
        f.art(HEART5, 18, 12 - j)


def mischief(f, t, n):
    """Hunched over, rubbing its hands together, eyes darting slyly."""
    k = t % n
    s = k % 2
    L = Canvas()
    look = 1 if (k // 3) % 2 else -1
    info = clawd(L, y=BY + 1, h=11, eyes='angry', look=look, la='short', ra='short')
    x, y = info['x'], info['y']
    hy = y + 8
    if s:
        L.rect(x + 3, hy, 5, 2, 'o'); L.rect(x + 7, hy + 1, 5, 2, 'o')
    else:
        L.rect(x + 4, hy + 1, 5, 2, 'o'); L.rect(x + 8, hy, 5, 2, 'o')
    f.blit(L.shear(0.06))
    for i, (px, py) in enumerate(((5, 12), (33, 15), (8, 27), (31, 29))):
        if (k + i) % 3 == 0:
            f.art(['.P.', 'PpP', '.P.'], px, py)
        elif (k + i) % 3 == 1:
            f.put(px + 1, py + 1, 'P')
    f.text('HEHE', 12 + (k % 2), 8 - (k // 2) % 2, 'P')


def determined(f, t, n):
    """Fist pumping, brows set, flames blazing up all around it."""
    k = t % n
    s = (k // 2) % 2
    tongues = [
        ['.R.', '.F.', 'FUF', 'FUF', 'UUU'],
        ['..R..', '.RF..', '.FFF.', 'FFUFF', 'FUUUF', 'UUUUU'],
        ['.F.', 'FUF', 'UUU'],
        ['.R..', '.FR.', 'FFF.', 'FUFF', 'UUUF', 'UUUU', '.UU.'],
    ]
    spots = [(9, 22), (12, 19), (16, 18), (20, 17), (24, 18), (28, 19), (31, 22), (6, 30), (34, 30),
             (5, 36), (35, 36)]
    for i, (sx, base) in enumerate(spots):
        a = tongues[(i * 3 + k) % 4]
        f.art(a, sx - len(a[0]) // 2, base - len(a))
    rr = rng(k)
    for i in range(3):
        f.put(rr.randint(4, 35), rr.randint(4, 16), 'F')
    clawd(f, la='low', ra='up' if s else 'high', eyes='angry', y=BY - (1 if s else 0), h=12 + (1 if s else 0))


def shy_scuff(f, t, n):
    """Bashfully looking down, toe drawing little circles on the floor."""
    k = t % n
    ldx, lift = [(0, 0), (-1, 1), (-1, 2), (1, 2), (1, 1), (0, 0)][(k // 2) % 6 if k < 12 else 0]
    L = Canvas()
    info = clawd(L, view='ql', eyes='normal', lookv=1, la='low', ra='low', legs=(lift, 0, 0, 0),
                 legdx=(ldx, 0, 0, 0))
    x, y, w = info['x'], info['y'], info['w']
    f.blit(L.shear(0.05 * sin(t, n)))
    for (gx, gy) in ((x - 1, GROUND), (x + 3, GROUND), (x + 1, GROUND + 1)):
        f.put(gx, gy, 'g')
    f.art(BLUSH_MARK, x + w + 1, y - 5 + (k // 4) % 2)
    if k >= 8:
        p = (k - 8) / 8
        f.art(P.HEART if p < 0.6 else ['Z'], x - 5 - int(p * 2), y - 2 - int(p * 8))
    if k < 6:
        f.art(['.r.', 'r.r'] if k % 2 else ['r.r', '.r.'], x + w - 4, y - 7)


# =========================================================================== register (60)
add_tweened('emo_joy_burst', '开心炸裂', 'Bursting with joy', joy_burst, n=14, dur=beats(14, 90, {0: 180, 2: 200, (6, 7): 150, 11: 180, (12, 13): 120}), tw_at={1: 1, 2: 1, 10: 1, 11: 1})
add('emo_happy_skip', '蹦蹦跳跳', 'Happy skip', happy_skip, n=24, dur=90)
add('emo_victory_dance', '胜利之舞', 'Victory dance', victory_dance, n=16, dur=120)
add('emo_hyper_bounce', '兴奋弹墙', 'Bouncing off the walls', hyper_bounce, n=16, dur=70)
add('emo_excited_vibrate', '激动到发抖', 'Vibrating with excitement', excited_vibrate, n=12, dur=70)
add_tweened('emo_wish_star', '对流星许愿', 'Wishing on a star', wish_star, n=16, dur=120, tw_at={13: 1, 15: 1})
add('emo_proud_chest', '骄傲挺胸', 'Proud chest-out', proud_chest, n=12, dur=140)
add('emo_smug_shades', '得意墨镜', 'Smug shades', smug_shades, n=16, dur=120)
add('emo_thumbs_up', '点个赞', 'Thumbs up', thumbs_up, n=12, dur=130)
add('emo_wink', '眨眼放电', 'Cheeky wink', wink, n=12, dur=120)
add('emo_ticklish', '怕痒', 'Ticklish', ticklish, n=12, dur=90)
add('emo_giggle', '捂嘴偷笑', 'Giggle', giggle, n=8, dur=110)
add_tweened('emo_laugh_roll', '笑到打滚', 'Rolling with laughter', laugh_roll, n=16, dur=100, tw_at={2: 1, 12: 1})
add('emo_self_hug', '抱抱自己', 'Self hug', self_hug, n=16, dur=140)
add('emo_blow_kiss', '飞吻', 'Blowing a kiss', blow_kiss, n=16, dur=110)
add('emo_lovestruck', '花痴心动', 'Love-struck', lovestruck, n=12, dur=120)
add('emo_heart_pound', '小鹿乱撞', 'Pounding heart', heart_pound, n=8, dur=110)
add('emo_daydream', '发白日梦', 'Daydreaming', daydream, n=24, dur=150)
add('emo_awe', '惊叹', 'In awe', awe, n=16, dur=130)
add('emo_meditate', '冥想平静', 'Meditation calm', meditate, n=16, dur=160)
add('emo_calm_down', '深呼吸冷静', 'Deep breaths', calm_down, n=24, dur=130)
add('emo_jiayou', '加油!', 'Cheering sign', jiayou, n=12, dur=120)
add('emo_nihao', '你好呀', 'Hello wave', nihao, n=16, dur=140)
add_tweened('emo_high_five', '击掌庆祝', 'High five', high_five, n=16, dur=beats(16, 100, {4: 150, 5: 350, 6: 250}), tw_at={0: 1, 9: 1})
add('emo_comfort', '摸头安慰', 'Comforting a friend', comfort, n=20, dur=150)
add('emo_furious_stomp', '气到跺脚', 'Furious stomp', furious_stomp, n=8, dur=90)
add('emo_boiling', '气到冒烟', 'Boiling over', boiling, n=20, dur=110)
add('emo_tantrum', '撒泼打滚', 'Tantrum', tantrum, n=8, dur=80)
add('emo_grumpy_pout', '哼!不理你', 'Grumpy pout', grumpy_pout, n=16, dur=150)
add('emo_puffed_cheeks', '鼓气包', 'Puffed cheeks', puffed_cheeks, n=16, dur=100)
add('emo_jealous', '吃醋斜眼', 'Jealous side-eye', jealous_sideye, n=16, dur=150)
add('emo_sulk_cloud', '头顶乌云', 'Sulking under a cloud', sulk_cloud, n=16, dur=160)
add('emo_sob_fountain', '嚎啕大哭', 'Sobbing fountains', sob_fountain, n=8, dur=90)
add('emo_pretty_please', '可怜巴巴', 'Pretty please', pretty_please, n=12, dur=130)
add('emo_heartbreak', '心碎了', 'Heartbreak', heartbreak, n=16, dur=130)
add('emo_lonely', '孤单', 'Lonely spotlight', lonely_spotlight, n=20, dur=150)
add('emo_sad_shuffle', '垂头丧气', 'Dejected shuffle', sad_shuffle, n=32, dur=120)
add('emo_gloom', '阴郁', 'Gloomy aura', gloom, n=12, dur=160)
add('emo_bored_sigh', '无聊叹气', 'Bored sigh', bored_sigh, n=16, dur=150)
add('emo_impatient', '不耐烦', 'Impatient tapping', impatient_tap, n=12, dur=100)
add_tweened('emo_shock_jump', '吓一跳', 'Shocked jump', shock_jump, n=14, dur=beats(14, 90, {0: 180, 4: 180, 5: 200, 6: 150, 9: 200}), tw_at={3: 1, 8: 1, 9: 1})
add('emo_relieved', '松了口气', 'Phew, relieved', relieved, n=16, dur=120)
add('emo_scared', '吓得发抖', 'Scared shaking', scared_shrink, n=10, dur=70)
add('emo_nervous_sweat', '紧张冒汗', 'Nervous sweat', nervous_sweat, n=16, dur=110)
add('emo_panic_circles', '慌得团团转', 'Panic circles', panic_circles, n=16, dur=70)
add_tweened('emo_mind_blown', '脑洞大开', 'Mind blown', mind_blown, n=16, dur=beats(16, 110, {4: 250, 5: 200, 6: 200, 8: 200}), tw_at={3: 1, 4: 1, 6: 1})
add('emo_dizzy', '晕头转向', 'Dizzy', dizzy_spiral, n=12, dur=110)
add('emo_confused', '一脸问号', 'Confused head tilt', confused_tilt, n=16, dur=150)
add('emo_awkward', '尴尬沉默', 'Awkward silence', awkward_crickets, n=16, dur=150)
add_tweened('emo_cringe', '嫌弃', 'Cringe', cringe, n=14, dur=beats(14, 110, {4: 200}), tw_at={9: 1})
add_tweened('emo_embarrassed', '羞到冒烟', 'Flustered', embarrassed, n=16, dur=110, tw_at={8: 1, 11: 1})
add_tweened('emo_sneeze', '打喷嚏', 'Sneeze', sneeze, n=16, dur=beats(16, 110, {5: 250, 6: 400, 7: 180}), tw_at={5: 1, 6: 1})
add('emo_hiccup', '打嗝', 'Hiccups', hiccup, n=12, dur=120)
add('emo_facepalm', '捂脸无语', 'Facepalm', facepalm, n=14, dur=140)
add('emo_eye_roll', '翻白眼', 'Eye roll', eye_roll, n=12, dur=120)
add_tweened('emo_yawn', '打哈欠', 'Big yawn', yawn, n=24, dur=beats(24, 140, {0: 280, 7: 280, 20: 350}), tw_at={7: 1, 19: 1})
add('emo_mood_swings', '情绪多变', 'Mood swings', mood_swings, n=16, dur=130)
add('emo_mischief', '坏笑搓手', 'Mischievous', mischief, n=12, dur=120)
add('emo_determined', '斗志燃烧', 'Determined', determined, n=12, dur=100)
add('emo_shy', '害羞画圈', 'Shy toe scuff', shy_scuff, n=16, dur=140)
