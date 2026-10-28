"""Holidays, festivals, seasons, weather and nature (sea_*)."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, mini, sin, cos, ph, pick, tri, rng, parse,
                    text_w, mix, col)
from engine import beats, add_tweened
import props as P
from kit import S


# --------------------------------------------------------------------------- helpers
def steps(s):
    return (1, 0, 1, 0) if s else (0, 1, 0, 1)


def outline(L, c='G', of=None):
    """Recolour edge pixels of a layer (optionally only pixels whose colour is in `of`)."""
    out = L.copy()
    cc = col(c)
    ofs = None if of is None else {col(x) for x in of}
    for y in range(L.h):
        for x in range(L.w):
            p = L.px[y][x]
            if p is None or (ofs is not None and p not in ofs):
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < L.w and 0 <= yy < L.h and L.px[yy][xx] is None:
                    out.px[y][x] = cc
                    break
    return out


def clip(L, fn):
    for y in range(L.h):
        for x in range(L.w):
            if L.px[y][x] is not None and not fn(x, y):
                L.px[y][x] = None
    return L


def bigtext(f, s, cx, y, c='K', k=2):
    T = Canvas(90, 6)
    w = T.text(s, 0, 0, c)
    x0 = int(round(cx - w * k / 2))
    for yy in range(5):
        for xx in range(w):
            if T.px[yy][xx] is not None:
                f.rect(x0 + xx * k, y + yy * k, k, k, c)


def snow_ground(f, y=GROUND):
    f.rect(0, y, 40, 40 - y, 'W')
    f.rect(0, y, 40, 1, 'G')


def grass(f, y=GROUND):
    f.rect(0, y, 40, 40 - y, 'E')
    f.rect(0, y + 1, 40, 40 - y, 'e')
    for x in range(1, 40, 5):
        f.put(x, y - 1, 'E'); f.put(x + 2, y - 1, 'e')


def snowball(f, cx, cy, r):
    f.disc(cx, cy, r, 'W')
    f.ring(cx, cy, r, 'G')


FLAKE = ['.G.', 'GWG', '.G.']


def snowfall(f, t, n, count=8, seed=3, xs=None, top=-4, bottom=40):
    P.falling(f, FLAKE, t, n, count=count, seed=seed, sway=1.2, xs=xs, top=top, bottom=bottom)


def puff(f, cx, cy, r, c='W', edge='G'):
    L = Canvas()
    for (dx, dy, rr) in ((0, 0, r), (-r * .7, r * .3, r * .7), (r * .7, r * .3, r * .7), (0, -r * .5, r * .7)):
        L.disc(cx + dx, cy + dy, rr, c)
    f.blit(outline(L, edge))


# --------------------------------------------------------------------------- Halloween
PUMPKIN = ['.......en.......', '.......e........', '...FFFFFFFFFF...', '.FFFdFFFFFFdFFF.', 'FFFdFFFFFFFFdFFF',
           'FFdFFFFFFFFFFdFF', 'FFdFFFFFFFFFFdFF', 'FFdFFFFFFFFFFdFF', 'FFdFFFFFFFFFFdFF', 'FFFdFFFFFFFFdFFF',
           '.FFFdFFFFFFdFFF.', '...FFFFFFFFFF...']


def jack(f, x, y, stage=3, lit=False, t=0):
    L = Canvas()
    L.art(PUMPKIN, x, y)
    L = outline(L, 'N', of='Fd')
    cut = pick(['U', 'Y'], t) if lit else 'n'
    if stage >= 1:
        L.art(['..K', '.KK', 'KKK'], x + 3, y + 4, cmap={'K': cut})
    if stage >= 2:
        L.art(['K..', 'KK.', 'KKK'], x + 10, y + 4, cmap={'K': cut})
    if stage >= 3:
        L.art(['KKKKKKKKKK', '.KK.KK.KK.'], x + 3, y + 8, cmap={'K': cut})
    f.blit(L)
    if lit:
        for (gx, gy) in ((x - 2, y + 3), (x + 17, y + 5), (x + 8, y - 2)):
            if (t + gx) % 3:
                f.put(gx, gy, 'U')


def knife(f, hx, hy, tx, ty):
    n = max(abs(tx - hx), abs(ty - hy))
    for i in range(n + 1):
        x = hx + (tx - hx) * i / max(1, n)
        y = hy + (ty - hy) * i / max(1, n)
        if i < 2:
            f.put(x, y, 'n')
        else:
            f.put(x, y, 'W'); f.put(x, y + 1, 'g')


def pumpkin_carve(f, t, n):
    k = t % 16
    stage = 0 if k < 3 else 1 if k < 5 else 2 if k < 8 else 3
    lit = 9 <= k <= 14
    PX, PY = 23, 24
    if k == 13:
        jack(f, PX + 5, PY, 3, True, t)
    elif k == 14:
        jack(f, PX + 12, PY, 3, True, t)
        jack(f, PX, PY - 16, 0)
    elif k == 15:
        jack(f, PX, PY, 0)
        P.dust(f, PX - 3, GROUND, 0.4); P.dust(f, PX + 17, GROUND, 0.4, flip=True)
    else:
        jack(f, PX, PY, stage, lit, t)
    if 1 <= k <= 7:
        tgt = 'L' if k < 3 else 'R' if k < 5 else 'M'
        x, arm, (tx, ty) = {'L': (1, 'out', (PX + 4, PY + 5)), 'R': (6, 'out', (PX + 12, PY + 5)),
                            'M': (6, 'low', (PX + 8, PY + 8))}[tgt]
        info = clawd(f, x=x, view='qr', ra=arm, eyes='focus')
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        knife(f, hx, hy, tx + k % 2, ty)
        if k % 2:
            f.put(tx + 2, ty - 2, 'y'); f.put(tx - 1, ty - 3, 'U')
    elif k == 8:
        info = clawd(f, x=4, view='qr', eyes='happy')
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        knife(f, hx, hy, hx, hy + 5)
    elif 9 <= k <= 12:
        hop = [0, -2, 0, -2][k - 9]
        clawd(f, x=3, y=BY + hop, eyes='happy', la='up' if hop else 'side',
              ra='up' if hop else 'side', legs=(1, 1, 1, 1) if hop else (0, 0, 0, 0))
    elif k == 13:
        clawd(f, x=8, view='qr', ra='out', eyes='normal')
    else:
        clawd(f, x={14: 4, 15: 2, 0: 1}[k], view='qr', eyes='big' if k == 14 else 'normal', lookv=-1 if k == 14 else 0)


def sheet_layer(x, y, w, h, t, flaps=0):
    L = Canvas()
    L.rect(x + 4, y, w - 8, 1, 'W'); L.rect(x + 2, y + 1, w - 4, 1, 'W'); L.rect(x + 1, y + 2, w - 2, 1, 'W')
    L.rect(x, y + 3, w, h - 4, 'W')
    for i in range(w):
        if (i // 2 + t) % 2 == 0:
            L.put(x + i, y + h - 1, 'W')
    if flaps == 1:
        L.rect(x - 3, y + 7, 3, 4, 'W'); L.rect(x + w, y + 7, 3, 4, 'W')
    elif flaps == 2:
        L.rect(x - 3, y + 2, 3, 6, 'W'); L.rect(x + w, y + 2, 3, 6, 'W')
    L = outline(L, 'G')
    L.rect(x + 4, y + 6, 2, 2, 'K'); L.rect(x + w - 6, y + 6, 2, 2, 'K')
    return L


def ghost_sheet(f, t, n):
    k = t % 16
    lift = {8: -6, 9: -14, 10: -40, 11: -40, 12: -22, 13: -12, 14: -4}.get(k, 0)
    under = k < 8 or k >= 14 or k == 8
    dx = int(round(2 * sin(k, 8))) if k < 8 else 0
    dy = -1 if k in (2, 3, 4, 5) else 0
    L = Canvas()
    reveal = 9 <= k <= 13
    info = clawd(L, x=BX + dx, y=BY + dy, eyes='happy' if reveal else 'normal',
                 la='up' if 9 <= k <= 12 else 'side', ra='up' if 9 <= k <= 12 else 'side',)
    flaps = 2 if 4 <= k <= 6 else 1
    if lift > -40:
        L.blit(sheet_layer(BX - 2 + dx, BY - 4 + dy + lift, 20, 17, t, flaps if lift == 0 else 0))
    f.blit(L)
    if 9 <= k <= 12:
        P.say(f, info, 'BOO!', c='p')
    if 4 <= k <= 6:
        f.art(['K.K.K', '.....'], 30, 10 + (k % 2))
        f.text('OO', 30, 12 - (k % 2), 'g')


PAIL = ['..kkkkkk..', '.k......k.', 'k........k', 'dddddddddd', 'FFFFFFFFFF', 'FnnFFFFnnF', 'FFFFFFFFFF',
        'FFnnnnnnFF', '.FFFFFFFF.', '..FFFFFF..']
CANDIES = [['Z.....Z', 'ZZWZWZZ', 'Z.....Z'], ['.EE.', 'EUUE', '.EE.', '..k.', '..k.'],
           ['nGGn', 'nNNn', 'nNNn'], ['P.....P', 'PPUPUPP', 'P.....P']]


def trick_treat(f, t, n):
    k = t % 16
    i, j = k // 4, k % 4
    land = j == 3
    info = clawd(f, x=6, y=BY + (1 if land else 0), h=12 - (1 if land else 0), ra='low',
                 eyes='happy' if land else 'normal', lookv=-1 if j in (1, 2) else 0, look=1)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    px, py = hx - 1, hy - 2 + (1 if land else 0)
    f.art(PAIL, px, py)
    for q, c in enumerate('ZUPEZU'):
        f.put(px + 2 + q, py + 3 - (q % 2), c)
    cy = [-4, 6, 15, py - 2][j]
    cx = [px + 2, px + 4, px + 3, px + 2][i]
    if j < 3:
        f.art(CANDIES[i], cx, cy)
    else:
        P.sparkles(f, 0, 4, [(px - 2, py), (px + 11, py - 1)])
    if k < 3:
        P.say(f, info, 'TREAT!', c='F', dy=-2, side='l')


BRISTLE = ['.YYY..', 'YYYYYN', 'UYYUYN', 'YYYYYN', '.YYY..']


def witch_broom(f, t, n):
    P.moon(f, 30, 2)
    P.sparkles(f, t, n, [(5, 5), (15, 2), (22, 8), (37, 14)])
    x = -18 + int(round(62 * t / n))
    y = BY - 9 + int(round(2 * sin(t, n, 2)))
    for j in range(1, 6):
        tx = x - 9 - j * 3
        ty = BY + 1 + int(round(2 * sin(t - j, n, 2)))
        f.put(tx, ty + (j + t) % 2, pick(['U', 'Y', 'P'], j + t))
    L = Canvas()
    s = (t // 2) % 2
    info = clawd(L, x=x, y=y, view='qr', la='low', ra='low', eyes='happy', legs=(1, 2, 1, 2) if s else (2, 1, 2, 1))
    by = y + 10
    L.rect(x - 6, by, 30, 1, 'N')
    L.art(BRISTLE, x - 12, by - 2)
    P.hat(L, info, 'witch')
    f.blit(L)


def mummy_wrap(f, t, n):
    k = t % 16
    SP = ['front', 'qr', 'sr', 'back', 'sl', 'ql']
    if k < 2:
        info = clawd(f, eyes='normal', ra='mid')
        f.disc(info['rh'][0] + 1.5, info['rh'][1], 2, 'w'); f.ring(info['rh'][0] + 1.5, info['rh'][1], 2, 'G')
        f.put(info['rh'][0] + 1, info['rh'][1] - 1, 'g')
        return
    L = Canvas()
    if k < 10:
        v = SP[(k - 2) % 6]
        info = clawd(L, view=v, eyes='normal', y=BY - (1 if v in ('sr', 'sl') else 0))
        level = 37 - (k - 1) * 2
    elif k < 14:
        s = k % 2
        info = clawd(L, x=BX + [0, 1, 2, 1][k - 10], la='out', ra='out', legs=steps(s), y=BY + s, eyes='line')
        level = 0
    else:
        info = clawd(L, eyes='blink' if k == 15 else 'big')
        level = 27 if k == 14 else 99
    O, o = col('O'), col('o')
    for yy in range(max(0, level), 40):
        for xx in range(40):
            c = L.px[yy][xx]
            if c == O:
                L.px[yy][xx] = col('G') if (yy * 2 + xx // 3) % 5 == 0 else col('w')
            elif c == o:
                L.px[yy][xx] = col('G')
    if level < 40:
        L = outline(L, 'g', of='wG')
    f.blit(L)
    if k >= 14:
        f.rrect(10, 34, 20, 2, 'w'); f.rect(12, 35, 16, 1, 'G')
        f.line(14, 33, 18, 34, 'G'); f.line(26, 33, 22, 34, 'G')
    if 2 <= k < 10:
        cx, top = info['head']
        f.put(cx + 9 - (k % 3), top + 5 + (k % 2), 'G')


COLLAR = ['k..', 'kk.', 'kRk', 'kRk']


def cape_wings(L, x, y, w, spread):
    for s in (-1, 1):
        ex = x - 1 if s < 0 else x + w
        for r in range(15):
            ww = max(1, int(spread * min(1, (r + 2) / 7)))
            if r == 14:
                ww -= 1
            for i in range(ww + 1):
                xx = ex - i if s < 0 else ex + i
                edge = i == ww or r == 0 or (r == 14 and i % 3 == 0)
                L.put(xx, y - 1 + r, 'k' if edge else 'M')


def vampire_cape(f, t, n):
    k = t % 16
    spread = {4: 4, 10: 4}.get(k, 8 if 5 <= k <= 9 else 0)
    L = Canvas()
    x, y = BX, BY
    if spread:
        cape_wings(L, x, y, 16, spread)
    arms = 'high' if spread else 'side'
    info = clawd(L, eyes='blink' if k == 13 else ('angry' if spread else 'focus'), la=arms, ra=arms)
    L.art(COLLAR, x - 1, y - 4); L.art(COLLAR, x + 14, y - 4, flip=True)
    if not spread:
        L.rect(x - 1, y + 5, 18, 10, 'k'); L.rect(x - 1, y + 5, 18, 1, 'M')
        L.rect(x + 4, y + 7, 1, 7, 'M'); L.rect(x + 11, y + 7, 1, 7, 'M')
        L.rect(x + 3, y + 14, 2, 1, 'O'); L.rect(x + 11, y + 14, 2, 1, 'O')
    f.blit(L)
    if 5 <= k <= 10:
        p = (k - 5) / 5
        for j, (dx, dy) in enumerate(((-1, -1), (1, -1.3), (0.3, -1.6))):
            P.batwing(f, int(x + 5 + dx * p * 20), int(y + 2 + dy * p * 18), t + j)


SKEL = ['..GGG..', '.GWWWG.', '.WKWKW.', '.GWWWG.', '..WGW..']
SKEL_BODY = [
    ['...W...', '.WWWWW.', 'W.WWW.W', 'W..W..W', '..WWW..', '..W.W..', '.W...W.', '.WW.WW.'],
    ['W..W..W', '.WWWWW.', '..WWW..', '...W...', '..WWW..', '.W..W..', '.W...W.', 'WW...WW'],
    ['...W...', '.WWWWW.', 'W.WWW.W', 'W..W..W', '..WWW..', '..W.W..', '.W...W.', '.WW.WW.'],
    ['W..W..W', '.WWWWW.', '..WWW..', '...W...', '..WWW..', '..W..W.', '.W...W.', 'WW...WW'],
]


def skeleton_dance(f, t, n):
    k = t % 4
    P.moon(f, 2, 2)
    sx, sy = 29 + [0, 1, 0, -1][k], 20 + (k % 2)
    S_ = Canvas()
    S_.art(SKEL, sx, sy)
    S_.art(SKEL_BODY[k], sx, sy + 5)
    sh = S_.copy().silhouette('g').shift(1, 1)
    f.blit(sh); f.blit(S_)
    dx = [0, -1, 0, 1][k]
    info = clawd(f, x=6 + dx, y=BY + (k % 2), la='up' if k in (0, 1) else 'side', ra='side' if k in (0, 1) else 'up',
                 legs=(1, 0, 0, 1) if k % 2 else (0, 1, 1, 0), eyes='happy')
    P.notes(f, info, t, n, c='P', count=2, spread=6)
    if t % 4 == 2:
        for (ax, ay, art) in ((24, 10, ['U..', '.U.', '..U']), (37, 10, ['..U', '.U.', 'U..'])):
            f.art(art, ax, ay)


# --------------------------------------------------------------------------- Christmas
LIGHTS = [(29, 14), (31, 16), (28, 17), (27, 21), (30, 22), (33, 23), (25, 24), (28, 25), (31, 27), (34, 28),
          (24, 29), (27, 30), (30, 31), (33, 32), (36, 31)]


def xmas_tree(f, t, cx=30, top=12):
    for (ty, hgt, w0, w1) in ((top, 8, 1, 5), (top + 6, 9, 2, 7), (top + 13, 9, 3, 9)):
        for r in range(hgt):
            hw = w0 + (w1 - w0) * r / (hgt - 1)
            f.rect(int(round(cx - hw)), ty + r, int(round(2 * hw)), 1, 'E')
            f.put(int(round(cx - hw)), ty + r, 'e')
    f.rect(cx - 1, top + 22, 2, 2, 'N')
    for i, (lx, ly) in enumerate(LIGHTS):
        f.put(lx, ly, 'RUBZC'[(i + t) % 5])


def tree_star(f, t, n):
    k = t % 16
    xmas_tree(f, t)
    seq = {0: (3, 0, 'hold'), 1: (3, 0, 'hold'), 2: (3, 0, 'hold'), 3: (3, 0, 'sq'), 4: (8, -5, 'air'),
           5: (12, -8, 'air'), 6: (15, -7, 'place'), 7: (11, -3, 'air2'), 8: (6, 0, 'sq2'), 9: (4, 0, 'look'),
           10: (4, 0, 'look'), 11: (4, 0, 'look'), 12: (4, 0, 'look'), 13: (4, 0, 'look'), 14: (4, 0, 'catch'),
           15: (3, 0, 'hold')}
    x, dy, mode = seq[k]
    star_on_tree = 6 <= k <= 13
    if star_on_tree:
        sx, sy = (28, 7) if k < 13 else (29, 8)
        f.art(P.STAR5 if k < 13 else ['.U...', 'UUU..', '.UUUU', '..UU.', '.U.U.'], sx, sy)
        if 7 <= k <= 12:
            P.sparkles(f, t, n, [(25, 6), (35, 8), (30, 3)])
    if mode in ('sq', 'sq2'):
        info = clawd(f, x=x - 1, w=18, h=10, y=BY + 2, eyes='closed', la='up' if mode == 'sq' else 'side',
                     ra='up' if mode == 'sq' else 'side')
    elif mode == 'look':
        info = clawd(f, x=x, view='qr', eyes='happy' if k < 13 else 'big', lookv=-1)
    else:
        info = clawd(f, x=x, y=BY + dy, la='up', ra='up', eyes='focus' if mode == 'air' else 'normal',
                     legs=(1, 1, 1, 1) if dy else (0, 0, 0, 0))
    if mode in ('hold', 'air', 'sq', 'air2'):
        cx, top = info['head']
        f.art(P.STAR5, int(cx) - 2, int(top) - 8)
    if k == 14:
        f.art(P.STAR5, 16, 14)


def snowman_build(f, t, n):
    k = t % 20
    snow_ground(f)
    if k < 6:
        r = 2 + k * 0.6
        bx = 18 + k * 2
        snowball(f, bx, 36 - r, r)
        f.put(bx - 1 + (k % 2), 36 - r, 'G')
        clawd(f, x=int(bx - r - 20), view='qr', ra='mid', legs=steps(k % 2), y=BY + k % 2, eyes='focus')
        return
    built = 8 <= k <= 14
    if 6 <= k <= 14:
        snowball(f, 28, 31, 5)
    if built:
        snowball(f, 28, 23, 3)
        if k >= 9:
            f.put(27, 22, 'K'); f.put(29, 22, 'K')
        if k >= 10:
            f.rect(29, 23, 3, 1, 'F')
        if k >= 11:
            f.line(23, 29, 20, 26, 'N'); f.put(21, 26, 'N')
            f.line(33, 29, 36, 26, 'N'); f.put(35, 26, 'N')
            f.rect(25, 19, 7, 1, 'k'); f.rect(26, 16, 5, 3, 'k'); f.rect(26, 18, 5, 1, 'R')
    if k == 15:
        puff(f, 28, 28, 6)
    elif 16 <= k <= 18:
        r = [6, 4, 2][k - 16]
        f.disc(28, 36, r, 'W'); f.ring(28, 36, r, 'G'); snow_ground(f)
    if k == 6:
        info = clawd(f, x=4, la='up', ra='up', eyes='normal')
        snowball(f, 12, 15, 3)
    elif k == 7:
        info = clawd(f, x=8, y=BY - 5, la='up', ra='up', legs=(1, 1, 1, 1), eyes='focus')
        snowball(f, 16, 10, 3)
    elif k == 8:
        clawd(f, x=10, y=BY - 3, la='up', ra='up', legs=(1, 1, 1, 1), eyes='happy')
    elif 9 <= k <= 14:
        s = (k // 1) % 2
        clawd(f, x=6, view='qr', eyes='happy', la='up' if s and k >= 11 else 'side', ra='up' if k >= 11 else 'side',
              y=BY - (1 if s and k >= 11 else 0))
        if k >= 11:
            P.sparkles(f, t, n, [(21, 14), (36, 18), (34, 11)])
    elif k == 15:
        clawd(f, x=6, view='qr', eyes='big')
    else:
        x = [6, 4, 2, -1][k - 16]
        clawd(f, x=x, view='ql' if k < 19 else 'qr', legs=steps(k % 2), eyes='normal')
        if k == 19:
            snowball(f, 17, 34, 2)


def sack(f, x, y, t):
    L = Canvas()
    L.disc(x + 6, y + 7, 6, 'N')
    L.rect(x + 4, y, 4, 3, 'N')
    L = outline(L, 'n')
    L.rect(x + 3, y + 2, 6, 1, 'n')
    L.rect(x + 3, y + 8, 2, 3, 'n')
    b = t % 2
    L.art(['BZB', 'ZZZ', 'BZB'], x + 1, y - 2 - b)
    L.art(['EUE', 'UUU'], x + 8, y - 1 - (1 - b))
    f.blit(L)


def santa_sack(f, t, n):
    snow_ground(f)
    snowfall(f, t, n, count=6, seed=4, bottom=34)
    x = -20 + int(round(64 * t / n))
    for i, px in enumerate(range(-30, 70, 5)):
        if px < x + 2:
            f.rect(px, 37 + i % 2, 2, 1, 'G')
    s = t % 2
    sack(f, x - 7, BY - 7 + s, t)
    info = clawd(f, x=x, y=BY + s, view='qr', legs=steps(s), la='high', eyes='happy')
    P.hat(f, info, 'santa')
    if 2 <= x <= 20 and (t // 3) % 2 == 0:
        P.say(f, info, 'HO HO', c='R', tc='W', dy=-4)


BELL = ['.U.', 'UYU', 'UYU', 'UUU', '.k.']


def reindeer_bells(f, t, n):
    snowfall(f, t, n, count=7, seed=9)
    k = t % 8
    side = 1 if k < 4 else -1
    j = k % 4
    hop = [0, -2, -3, -1][j]
    x = BX + int(round(3 * sin(t, n)))
    info = clawd(f, x=x, y=BY + hop, legs=(1, 1, 0, 0) if side > 0 and hop else (0, 0, 1, 1) if hop else (0, 0, 0, 0),
                 la='out', ra='out', eyes='happy' if hop else 'closed')
    P.hat(f, info, 'antlers')
    for hand, sgn in ((info['lh'], -1), (info['rh'], 1)):
        swing = 1 if (t + (sgn > 0)) % 2 else -1
        hx, hy = int(hand[0]), int(hand[1])
        bx = hx - (1 if sgn > 0 else 2)
        f.rect(bx + 1, hy - 2, 1, 2, 'R')
        f.art(BELL, bx + swing, hy - 7)
        if (t + (sgn > 0)) % 2:
            f.art(['U.', '.U', 'U.'] if sgn > 0 else ['.U', 'U.', '.U'], bx + sgn * 4 + (1 if sgn > 0 else 0), hy - 7)
    if hop == 0:
        P.dust(f, x - 2, GROUND, 0.3); P.dust(f, x + 17, GROUND, 0.3, flip=True)


def fireplace(f, t, n):
    f.rect(22, 16, 17, 20, 'G')
    for r in range(17, 36, 3):
        f.rect(22, r, 17, 1, 'g')
        for c in range(23 + (r // 3 % 2) * 2, 39, 4):
            f.rect(c, r + 1, 1, 2, 'g')
    f.rect(26, 23, 10, 13, 'k')
    f.rect(20, 14, 20, 2, 'N'); f.rect(20, 15, 20, 1, 'n')
    f.rect(27, 33, 8, 2, 'N'); f.rect(28, 33, 6, 1, 'n')
    r = rng(t)
    for i in range(8):
        hgt = 3 + ((i * 3 + t * 2) % 5)
        f.rect(27 + i, 33 - hgt, 1, hgt, 'R' if i in (0, 7) else 'F')
        if hgt > 4:
            f.rect(27 + i, 33 - hgt + 2, 1, hgt - 3, 'U')
    if t % 3 == 0:
        f.put(29 + r.randint(0, 4), 22 - t % 2, 'U')
    for j, (sx, c) in enumerate(((22, 'R'), (28, 'E'), (34, 'O'))):
        dx = (1 if (t // 2 + j) % 2 else 0)
        L = Canvas()
        L.art(['WWW.', 'WWW.', '.CC.', '.CC.', '.CC.', 'CCC.', 'CC..'], sx + dx, 16, cmap={'C': c})
        f.blit(outline(L, 'G', of='W'))
    k = t % 16
    front = 9 <= k <= 12
    s = t % 2
    info = clawd(f, x=2, y=BY + 2, leg_h=1, view='front' if front else 'q2r', ra='out' if not front else 'side',
                 eyes='happy' if front else ('closed' if k % 8 < 6 else 'normal'))


GB = ['..NNN..', '.NWNWN.', '..NNN..', 'NNNWNNN', '..NWN..', '..NNN..']
GB_LEGS = [['.NN.NN.', 'NN...NN'], ['..NNN..', '..N.N..']]


def gingerbread_chase(f, t, n):
    p = t / n
    gx = int(round(-8 + 72 * p))
    cx = gx - 24
    s = t % 2
    gy = 27 - s
    f.art(GB + GB_LEGS[s], gx, gy)
    if s:
        f.art(['W.W'], gx + 2, gy + 1)
    L = Canvas()
    clawd(L, x=cx, y=BY - 1 + s, view='qr', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2), eyes='happy',
          la='low', ra='high' if s else 'low')
    f.blit(L.shear(-0.1, 36))
    P.speedlines(f, cx - 2, BY + 2, t)
    P.speedlines(f, gx - 1, gy, t + 3, n=2, length=4)
    if 4 <= gx <= 30 and t % 4 < 2:
        f.text('HA', gx - 1, gy - 7, 'N')


def gift_unwrap(f, t, n):
    k = t % 16
    dx = [0, 1, 0, -1][k] if k < 4 else 0
    lid_y = {5: 17, 6: 10, 7: 8, 8: 7, 9: 8, 10: 7, 11: 8, 12: 15}.get(k, 23)
    if 6 <= k <= 11:
        top = 26 - [4, 9, 11, 10, 11, 6][k - 6]
        for yy in range(top + 3, 26):
            f.put(28 + (yy % 2), yy, 'g')
        f.art(P.STAR5, 26, top - 2)
        P.confetti(f, t, n, count=14, seed=k // 3)
    f.rect(22 + dx, 26, 14, 10, 'B'); f.rect(22 + dx, 35, 14, 1, 'V')
    f.rect(28 + dx, 26, 2, 10, 'Z'); f.rect(22 + dx, 30, 14, 1, 'Z')
    f.rect(21 + dx, lid_y, 16, 3, 'B'); f.rect(21 + dx, lid_y + 2, 16, 1, 'V')
    tied = k < 4 or k >= 14
    if tied:
        f.rect(28 + dx, lid_y, 2, 3, 'Z')
        f.art(['ZZ..ZZ', 'ZZZZZZ', '.Z..Z.'], 26 + dx, lid_y - 3)
    if k == 5:
        for (ax, ay) in ((19, 21), (39, 21), (23, 18), (35, 18)):
            f.put(ax, ay, 'U')
    if k < 4:
        info = clawd(f, x=3, view='qr', eyes='big', look=1)
        if k >= 2:
            f.art(P.QMARK, 18, 12)
    elif k == 4:
        info = clawd(f, x=4, view='qr', ra='out', eyes='focus')
        f.art(['ZZ..ZZ', 'ZZZZZZ'], 23, 24)
    elif k <= 11:
        s = k % 2
        clawd(f, x=3, y=BY - s, view='front', la='up' if s else 'high', ra='up' if s else 'high', eyes='happy')
    else:
        clawd(f, x=3, view='qr', eyes='happy' if k < 14 else 'normal', ra='out' if k == 14 else 'side')


def snow_globe(f, t, n):
    k = t % 20
    sdx = [-2, 2, -2, 2][k] if k < 4 else 0
    L = Canvas()
    cx, cy, r = 20, 18, 15
    L.disc(cx, cy, r, 'S')
    L.rect(0, 30, 40, 10, 'W'); L.rect(0, 30, 40, 1, 'G')
    eyes = 'x' if k < 4 else 'squint' if k < 7 else 'normal' if k < 11 else 'happy'
    idx = [1, -1, 1, -1][k] if k < 4 else 0
    clawd(L, x=12 + idx, y=15, eyes=eyes, la='up' if 12 <= k <= 15 and k % 2 else 'side',
          ra='up' if 12 <= k <= 15 else 'side')
    rr = rng(31)
    for i in range(16):
        if k < 4:
            q = rng(i * 13 + k)
            fx, fy = q.randint(7, 33), q.randint(5, 28)
        else:
            q = rng(i * 13 + 3)
            fx, fy = q.randint(7, 33), q.randint(5, 28)
            fy = min(29, fy + (k - 3) * (1 + i % 2))
            fx += int(round(math.sin((k + i) * 0.8)))
        L.put(fx, fy, 'W')
    clip(L, lambda x, y: (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= (r - 1) ** 2)
    L.ring(cx, cy, r, 'G')
    for (hx, hy) in ((10, 8), (11, 7), (12, 6), (9, 10)):
        L.put(hx, hy, 'W')
    L.rect(9, 32, 22, 2, 'Y'); L.rect(8, 34, 24, 3, 'N'); L.rect(7, 37, 26, 1, 'n')
    L.rect(9, 32, 22, 1, 'U')
    f.blit(L.shift(sdx, 0))
    if k < 4:
        f.art(['L.', '.L', 'L.'], 1 + (k % 2), 14); f.art(['.L', 'L.', '.L'], 37 - (k % 2), 14)


# --------------------------------------------------------------------------- register: Halloween & Christmas
add_tweened('sea_pumpkin_carve', '雕南瓜灯', 'Carving a jack-o\'-lantern', pumpkin_carve, n=16, dur=140, tw_at={12: 1})
add_tweened('sea_ghost_sheet', '床单幽灵', 'Bedsheet ghost', ghost_sheet, n=16, dur=140, tw_at={12: 1})
add('sea_trick_treat', '不给糖就捣蛋', 'Trick-or-treat haul', trick_treat, n=16, dur=120)
add('sea_witch_broom', '骑扫帚飞', 'Witch on a broom', witch_broom, n=24, dur=90)
add('sea_mummy_wrap', '木乃伊缠绷带', 'Mummy wrap', mummy_wrap, n=16, dur=120)
add('sea_vampire_cape', '吸血鬼披风', 'Vampire cape swish', vampire_cape, n=16, dur=120)
add('sea_skeleton_dance', '和骷髅跳舞', 'Dancing with a skeleton', skeleton_dance, n=12, dur=130)
add_tweened('sea_bats_circle', '蝙蝠绕飞', 'Bats circling', S, n=16, dur=140, tw_at={5: 1, 9: 1}, act='hide', fx=['night', 'bats'])
add_tweened('sea_tree_star', '圣诞树放星星', 'Star on the tree', tree_star, n=16, dur=beats(16, 130, {3: 200, 5: 300, 7: 180}), tw_at={3: 1, 7: 1, 13: 1})
add_tweened('sea_snowman_build', '堆雪人', 'Building a snowman', snowman_build, n=20, dur=beats(20, 140, {7: 250, 11: 250}), tw_at={5: 1, 8: 1, 15: 1})
add('sea_santa_sack', '圣诞老人背礼物', 'Santa\'s sack', santa_sack, n=24, dur=beats(24, 100, {(12, 13, 14): 200}))
add('sea_reindeer_bells', '驯鹿摇铃铛', 'Reindeer jingle bells', reindeer_bells, n=8, dur=130)
add('sea_fireplace', '壁炉挂袜子', 'Stockings by the fire', fireplace, n=16, dur=150)
add('sea_gingerbread_chase', '追姜饼人', 'Gingerbread chase', gingerbread_chase, n=20, dur=80)
add_tweened('sea_gift_unwrap', '拆圣诞礼物', 'Unwrapping a gift', gift_unwrap, n=16, dur=120, tw_at={4: 1, 11: 1})
add('sea_snow_globe', '水晶球摇雪', 'Shaken snow globe', snow_globe, n=20, dur=120)


# --------------------------------------------------------------------------- New Year
def countdown(f, t, n):
    k = t % 20
    if k < 12:
        j = k % 4
        sq = j == 0
        bigtext(f, '321'[k // 4], 20, 2 + (1 if sq else 0), 'RFE'[k // 4], k=2)
        info = clawd(f, x=BX - (1 if sq else 0), w=18 if sq else 16, h=11 if sq else 12, y=BY + (1 if sq else 0),
                     eyes='big', lookv=-1, la='low', ra='low')
        P.hat(f, info, 'party')
        if sq:
            P.dust(f, BX - 3, GROUND, 0.2); P.dust(f, BX + 18, GROUND, 0.2, flip=True)
        return
    j = k - 12
    P.firework(f, 7, 12, ph(j, 8), 'Z', 'U', r=5)
    P.firework(f, 33, 12, ph(j + 4, 8), 'C', 'U', r=5)
    s = j % 2
    bigtext(f, '2027', 20, 2, 'U' if s else 'Z', k=2)
    info = clawd(f, y=BY - 2 * s, la='up' if s else 'high', ra='up' if s else 'high',
                 legs=(1, 1, 1, 1) if s else (0, 0, 0, 0), eyes='happy' if s else 'closed')
    P.hat(f, info, 'party')
    P.confetti(f, t, n, count=16)


BURSTS = [(8, 9, 0, 'Z', 'U'), (31, 7, 4, 'C', 'y'), (20, 4, 8, 'U', 'Z')]


def fireworks_watch(f, t, n):
    flash = None
    for (cx, cy, off, c, c2) in BURSTS:
        q = (t - off) % 12
        P.firework(f, cx, cy, q / 12, c, c2, r=6)
        if q == 3:
            flash = c
    k = t % 24
    view = 'back'
    eyes = 'normal'
    if k in (11, 16):
        view = 'ql'
    elif 12 <= k <= 15:
        view, eyes = 'front', 'happy'
    clawd(f, y=BY + 2, leg_h=1, view=view, eyes=eyes,
          la='high' if 12 <= k <= 15 else 'side', ra='high' if 12 <= k <= 15 else 'side')


POPPER = ['....UU', '...ZUU', '..UUZ.', '.ZUU..', 'UUZ...', 'UZ....']


def party_popper(f, t, n):
    k = t % 16
    jolt = k == 4
    info = clawd(f, x=6, y=BY - (1 if jolt else 0) + (k % 2 if k < 4 else 0), ra='high', la='low',
                 eyes='squint' if k < 4 else 'big' if k < 6 else 'happy' if k < 12 else 'normal')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    f.art(POPPER, hx - 1, hy - 5)
    pull = 2 if k in (3, 4) else 0
    f.line(hx - 1, hy + 1, hx - 2 - pull, hy + 4 + pull, 'k')
    f.put(hx - 2 - pull, hy + 5 + pull, 'Z')
    mx, my = hx + 4, hy - 6
    if k == 4:
        f.art(P.SPARK_BIG, mx - 3, my - 3)
    if 4 <= k <= 14:
        dt = k - 4 + 0.6
        for i in range(16):
            a = math.radians(-105 + i * 8)
            v = 2.0 + (i % 3) * 0.7
            px = mx + v * dt * math.cos(a)
            py = min(35, my + v * dt * math.sin(a) + 0.3 * dt * dt)
            c = 'ZBUEPC'[i % 6]
            if i % 4 == 0:
                for s in range(4):
                    d2 = max(0, dt - s * 0.5)
                    qx = mx + v * d2 * math.cos(a) + (1 if s % 2 else 0)
                    qy = min(35, my + v * d2 * math.sin(a) + 0.3 * d2 * d2)
                    f.put(qx, qy, c)
            elif (i + k) % 2:
                f.rect(int(px), int(py), 1, 2, c)
            else:
                f.rect(int(px), int(py), 2, 1, c)


def heart_pt(s, cx=29, cy=12, sc=0.42):
    x = 16 * math.sin(s) ** 3
    y = 13 * math.cos(s) - 5 * math.cos(2 * s) - 2 * math.cos(3 * s) - math.cos(4 * s)
    return cx + x * sc, cy - y * sc


def sparkler_heart(f, t, n):
    k = t % 16
    P.sparkles(f, t, n, [(3, 3), (14, 1), (38, 20)])
    info = clawd(f, x=1, view='qr', ra='up', eyes='happy' if k >= 12 else 'focus', look=1)
    hx, hy = info['rh']
    done = min(k, 12) / 12
    pts = [heart_pt(2 * math.pi * i / 60) for i in range(int(60 * done) + 1)]
    if k >= 12:
        c = 'Z' if k % 2 else 'U'
        for i, (x, y) in enumerate(pts):
            if k < 15 or i % 3 == 0:
                f.put(x, y, c)
        tx, ty = hx + 3, hy - 5
    else:
        for i, (x, y) in enumerate(pts):
            f.put(x, y, 'U' if i > len(pts) - 8 else 'F')
        tx, ty = pts[-1]
    f.line(hx, hy, tx, ty, 'g')
    f.art(pick([P.SPARK, ['U.U', '.W.', 'U.U'], ['.U.', 'UWU', '.U.']], t), int(tx) - 1, int(ty) - 1)


# --------------------------------------------------------------------------- Lunar New Year / festivals
ENVELOPE = ['RRRRRRR', 'RMRRRMR', 'RRMRMRR', 'RRRUURR', 'RRRUURR', 'RRRRRRR', 'RRRRRRR', 'RRRRRRR', 'MMMMMMM']
COIN_W = ['.UUU.', 'UYUYU', 'UYYYU', 'UYUYU', '.UUU.']
COIN_N = ['.U.', 'UYU', 'UYU', 'UYU', '.U.']


def red_envelope(f, t, n):
    k = t % 20
    if k < 4:
        b = [0, 2, 2, 0][k]
        clawd(f, y=BY + b, h=12 - b, top=b > 0, lookv=b, eyes='closed' if b else 'happy',
              la='front' if b else 'side', ra='front' if b else 'side')
        return
    if k < 8:
        ex, ey = [(24, -6), (18, 2), (23, 7), (19, 10)][k - 4]
        f.art(ENVELOPE, ex, ey)
        clawd(f, eyes='big', lookv=-1, look=[1, 0, 1, 0][k - 4])
        return
    if k == 8:
        info = clawd(f, la='up', ra='up', eyes='big', y=BY - 1)
        cx, top = info['head']
        f.art(ENVELOPE, int(cx) - 3, int(top) - 10)
        return
    if k < 18:
        info = clawd(f, ra='mid', eyes='big' if 12 <= k <= 15 else 'happy')
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        f.art(ENVELOPE, hx, hy - 6)
        if k >= 12:
            cy = {12: hy - 12, 13: hy - 17, 14: hy - 19, 15: hy - 18, 16: hy - 14, 17: hy - 9}[k]
            f.art(COIN_W if k % 2 else COIN_N, hx + (1 if k % 2 else 2), cy)
            if k in (13, 14):
                P.sparkles(f, t, n, [(hx - 3, cy), (hx + 9, cy + 2)])
        return
    clawd(f, la='front', ra='front', eyes='happy')
    f.art(ENVELOPE, 17, BY + 9)


SKYLANTERN = ['.YYYYY.', 'YyyyyyY', 'YyyyyyY', 'YyyUyyY', 'YyyyyyY', '.YyyyY.', '..YFY..', '...F...']


def sky_lantern(f, t, n):
    k = t % 20
    P.rising(f, ['U', 'F'], t, n, 8, 30, count=3, height=34, sway=1, seed=12, jitter=8)
    P.rising(f, ['U', 'F'], t, n, 32, 34, count=2, height=36, sway=1, seed=5, jitter=5)
    fl = {'F': pick(['F', 'U'], t)}
    if 4 <= k <= 13:
        j = k - 4
        ly = 8 - int(round(j * 3.2))
        lx = 17 + int(round(math.sin(j * 0.9) * 2))
        f.art(SKYLANTERN, lx, ly, cmap=fl)
        wave = 7 <= k <= 11
        clawd(f, eyes='normal', lookv=-1, la='up' if k == 4 else 'side',
              ra=('wave' if (k // 2) % 2 else 'up') if wave else ('up' if k == 4 else 'side'))
        return
    if k in (14, 15):
        clawd(f, la='low', ra='low', eyes='normal', lookv=1 if k == 14 else 0, y=BY + (1 if k == 14 else 0))
        f.art(['YYYYY', 'yyyyy'], 18, 32 if k == 14 else 29)
        return
    info = clawd(f, la='up', ra='up', eyes='happy')
    cx, top = info['head']
    if k == 16:
        f.art(['.YYY.', 'YyyyY', 'YyyyY', '.YYY.'], int(cx) - 2, int(top) - 7)
    else:
        f.art(SKYLANTERN, int(cx) - 3, int(top) - 11, cmap=fl)


def firecracker(f, t, n):
    bottom = 27
    shift = 3 * (t // 2)
    f.rect(31, 0, 1, bottom + 1, 'k')
    for i in range(-2, 18):
        y = -24 + 3 * i + shift
        if y > bottom or y < -3:
            continue
        if i % 2:
            f.rect(27, y, 4, 2, 'R'); f.put(27, y, 'U'); f.put(30, y + 1, 'M')
        else:
            f.rect(32, y, 4, 2, 'R'); f.put(35, y, 'U'); f.put(32, y + 1, 'M')
    r = rng(t)
    if t % 2 == 0:
        for a in range(8):
            ang = a * math.pi / 4
            for d in (2, 3, 4):
                f.put(31 + math.cos(ang) * d, 31 + math.sin(ang) * d, 'U' if d < 4 else 'F')
        f.rect(30, 30, 2, 2, 'W')
    else:
        f.art(P.PUFF, 29 + r.randint(-1, 1), 27)
    for j in range(6):
        q = rng(j * 7 + t // 2)
        bx = 31 + q.randint(-8, 7) + (t % 2) * q.choice((-1, 1))
        by = 28 + q.randint(-4, 6) + (t % 2) * 2
        f.rect(bx, by, 1 + j % 2, 1, 'R')
    for gx in (22, 25, 34, 37, 29):
        f.rect(gx, 35, 2, 1, 'R')
    bang = t % 2 == 0
    clawd(f, x=1, y=BY - (1 if bang else 0), la='high', ra='high', eyes='squint' if bang else 'closed',
          legs=(1, 1, 1, 1) if bang else (0, 0, 0, 0))


def lion_head(L, x, y, mouth=0, blink=False):
    H = Canvas()
    H.art(['...W.UUUUUUUU.W..', '..WWUUURRUUUUWW..', '.WWRRRRRRRRRRRWW.', 'WWRWWWRRRRRWWWRWW',
           'WRRWKWRRRRRWKWRRW', 'WRRWWWRRRRRWWWRRW', '.WRRRRRRYRRRRRRW.', '.WRRRRRYYYRRRRRW.'], x, y)
    if blink:
        H.rect(x + 3, y + 3, 3, 3, 'U'); H.rect(x + 11, y + 3, 3, 3, 'U')
    if mouth:
        H.rect(x + 3, y + 8, 11, mouth, 'M'); H.rect(x + 6, y + 8 + mouth - 1, 5, 1, 'Z')
    H.art(['..RWWWWWWWWWWWR..', '..RRRRRRRRRRRRR..', '...WWWWWWWWWWW...'], x, y + 8 + mouth)
    L.blit(outline(H, 'G', of='W'))


def lion_dance(f, t, n):
    k = t % 12
    s = k % 2
    dx = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1, 0, -1][k]
    hdy = [0, -1, -2, -1, 0, 1, 0, -1, -2, -2, -1, 0][k]
    mouth = 2 if k in (3, 4, 9) else 1 if k in (2, 5, 8, 10) else 0
    C = Canvas()
    for i in range(10):
        C.rect(BX - 8 + i, BY + 1 + (i + t) % 2, 1, 10, 'R')
        C.put(BX - 8 + i, BY + 11 + (i + t) % 2, 'U')
    f.blit(C.shift(dx, 0))
    clawd(f, x=BX + dx, y=BY + s, legs=steps(s), eyes='happy', la='low' if s else 'side', ra='side' if s else 'low')
    L = Canvas()
    lion_head(L, BX - 1 + dx, BY - 12 + hdy, mouth, blink=k == 7)
    f.blit(L.shear(0.12 * (1 if (k // 3) % 2 else -1), BY - 2 + hdy) if k % 3 == 1 else L)
    if mouth == 2:
        P.sparkles(f, t, n, [(5, 6), (35, 8)])


def fu_sign(rot):
    L = Canvas()
    cx, cy = 28, 16
    for y in range(cy - 10, cy + 10):
        for x in range(cx - 10, cx + 10):
            d = abs(x + .5 - cx) + abs(y + .5 - cy)
            if d <= 10:
                L.put(x, y, 'U' if d > 9 else 'R')
    P.cjk(L, '福', cx - 6, cy - 4, 'U')
    return L.rot90(rot, cx, cy) if rot else L


def fu_upside(f, t, n):
    k = t % 16
    rot = {4: 1, 5: 2, 12: 3}.get(k, 2 if 6 <= k <= 11 else 0)
    f.rect(28, 0, 1, 6, 'k')
    f.blit(fu_sign(rot))
    if k < 4:
        clawd(f, x=3, view='qr', ra='up' if k >= 2 else 'side', eyes='focus' if k >= 2 else 'normal')
    elif 6 <= k <= 11:
        s = k % 2
        clawd(f, x=3, la='high' if s else 'side', ra='high' if s else 'side', eyes='happy', y=BY - s)
        P.sparkles(f, t, n, [(16, 8), (39, 22), (24, 30)])
    elif k in (4, 5):
        clawd(f, x=3, view='qr', ra='up', eyes='big')
        f.art(['.L', 'L.'], 20, 8 + k)
    else:
        clawd(f, x=3, view='qr' if k < 14 else 'front', eyes='big' if k < 14 else 'normal',
              ra='up' if k >= 14 else 'side')
        if k >= 14:
            f.art(P.QMARK, 6, 10)


DUMPLING = ['..W..', '.WGW.', 'WWWWW']


def steamer_lid(f, x, y):
    f.rect(x + 3, y, 11, 1, 'N'); f.rect(x + 1, y + 1, 15, 1, 'Y'); f.rect(x, y + 2, 17, 1, 'Y')
    f.rect(x, y + 3, 17, 1, 'N'); f.rect(x + 7, y - 1, 3, 1, 'N')


def dumpling_steamer(f, t, n):
    k = t % 16
    for (ty, h) in ((25, 5), (30, 6)):
        f.rect(21, ty, 17, h, 'Y'); f.rect(21, ty, 17, 1, 'N'); f.rect(21, ty + h - 1, 17, 1, 'N')
        for sx in range(23, 37, 3):
            f.rect(sx, ty + 1, 1, h - 2, 'N')
    open_ = 5 <= k <= 12
    if open_:
        for dx in (22, 27, 32):
            L = Canvas(); L.art(DUMPLING, dx, 22); f.blit(outline(L, 'G'))
        r = rng(k)
        for i in range(3):
            q = (k - 5 + i * 2) % 6
            f.art(P.PUFF, 22 + i * 5 + r.randint(-1, 1), 17 - q * 3)
        if k > 7:
            f.rect(0, 22, 2, 14, 'Y'); f.rect(2, 23, 1, 12, 'N'); f.rect(0, 22, 1, 14, 'N')
        info = clawd(f, x=3, view='qr', ra='up' if k <= 7 else 'side', eyes='happy' if 7 <= k <= 11 else 'big')
        if k <= 7:
            steamer_lid(f, int(info['rh'][0]) - 8, int(info['rh'][1]) - 5)
    else:
        steamer_lid(f, 21, 21)
        if t % 2:
            f.art(P.PUFF_S, 19, 22 - t % 4); f.art(P.PUFF_S, 38, 21 - t % 3)
        clawd(f, x=2, view='qr', ra='out' if k in (4, 13) else 'side', eyes='happy' if k > 12 else 'normal')
    if k == 6:
        P.sparkles(f, 0, 4, [(20, 18), (38, 16), (29, 12)])


def mooncake_moon(f, t, n):
    k = t % 16
    f.disc(30, 10, 8, 'y'); f.ring(30, 10, 8, 'Y')
    f.rect(26, 6, 2, 2, 'U'); f.rect(32, 12, 3, 2, 'U'); f.put(29, 14, 'U')
    hop = (t // 2) % 2
    f.art(['G.G', 'G.G', 'GGG', 'GGGG', '.G.G'], 30, 6 - hop)
    cx = -8 + (t * 3) % 48
    f.rect(cx, 15, 10, 1, 'L'); f.rect(cx + 2, 14, 5, 1, 'L')
    for j, lx in enumerate((3, 11)):
        sw = 1 if (t // 3 + j) % 2 else 0
        f.rect(lx + 2, 0, 1, 2, 'k')
        f.art(P.ITEMS['lantern'][0], lx + sw, 2)
    up = 6 <= k <= 11
    info = clawd(f, x=2, y=BY + 2, leg_h=1, ra='up' if up else 'mid', eyes='closed' if up else 'happy',
                 eyes_r='normal' if up else None)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    MC = ['.NNNN.', 'NYYYYN', 'NYNNYN', 'NYNNYN', 'NYYYYN', '.NNNN.']
    if up:
        f.art(MC, hx - 2, hy - 7)
        if k in (8, 9):
            P.sparkles(f, 0, 4, [(hx + 5, hy - 9), (hx - 4, hy - 4)])
    else:
        f.art(MC, hx, hy - 3)


DRAGON = ['..RR....', '.EEEE...', 'EEUKEEE.', 'EEEEEEEW', '.EEEERR.', '..EE....', '..EE....', '.EE.....',
          '.EE.....']


def dragon_boat(f, t, n):
    k = t % 8
    b = [0, 0, 1, 1, 1, 1, 0, 0][k]
    hit = k in (0, 4)
    mini(f, 1, 19 + b, eyes='happy', la='side', ra='high' if hit else 'side')
    f.rect(10, 23 + b, 4, 4, 'R'); f.rect(10, 23 + b, 4, 1, 'U'); f.rect(10, 26 + b, 4, 1, 'U')
    fwd = k < 4
    L = Canvas()
    info = clawd(L, x=15, y=16 + b, view='qr', ra='low', la='low', eyes='angry')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    tx, ty = (hx + 6, hy + 10) if fwd else (hx - 5, hy + 10)
    f.blit(L.shear(0.06 if fwd else -0.06, 36))
    f.rect(3, 27 + b, 32, 5, 'E'); f.rect(3, 27 + b, 32, 1, 'U'); f.rect(4, 31 + b, 30, 1, 'e')
    for sx in range(5, 33, 4):
        f.put(sx + (b % 2), 29 + b, 'U')
    f.art(DRAGON, 32, 18 + b)
    f.art(['E.', 'EE', '.EE', '..E'], 0, 23 + b)
    f.rect(0, 32, 40, 8, 'B')
    for x in range(40):
        if (x + t * 2) % 8 < 3:
            f.put(x, 32, 'S')
        if (x - t * 2) % 10 < 2:
            f.put(x, 35, 'S')
    f.line(hx, hy - 3, tx, ty, 'N')
    f.rect(tx - 1, ty - 2, 3, 4, 'n')
    if k in (0, 1, 4, 5):
        f.art(['S.S', '.W.'] if k % 2 == 0 else ['W...W', '.S.S.'], tx - 2, 29)
    if hit:
        f.text('DONG', 2, 11, 'R')


HEART_BAL = ['.ZZZ.ZZZ.', 'ZZrZZZZZZ', 'ZrZZZZZZZ', 'ZZZZZZZZZ', '.ZZZZZZZ.', '..ZZZZZ..', '...ZZZ...', '....Z....']


def valentine_balloon(f, t, n):
    lift = int(round(5 * (1 - cos(t, n)) / 2))
    sw = int(round(1.5 * sin(t, n, 2)))
    f.rect(20 - (7 - lift // 2), GROUND, 2 * (7 - lift // 2), 1, 'G')
    s = t % 2
    info = clawd(f, y=BY - lift, ra='up', eyes='happy' if lift >= 2 else 'normal',
                 legs=((1, 0, 1, 0) if s else (0, 1, 0, 1)) if lift > 1 else (0, 0, 0, 0))
    hx, hy = info['rh']
    bx, by = int(hx) - 4 + sw, int(hy) - 13
    P.balloon_string(f, (hx, hy), (bx + 4, by + 8), t=t)
    f.art(HEART_BAL, bx, by)
    P.rising(f, P.HEART, t, n, 4, 22, count=3, height=16, seed=6, jitter=2)


EGG = ['.cc.', 'cddc', 'cccc', 'cddc', '.cc.']
BASKET = ['..NNNNN..', '.N.....N.', 'N.......N', 'NNNNNNNNN', 'NnNnNnNnN', 'NNNNNNNNN', '.NnNnNnN.', '..NNNNN..']


def bush(f, x, y, dx=0):
    L = Canvas()
    L.disc(x + 5, y + 6, 5, 'E'); L.disc(x + 10, y + 4, 5, 'E'); L.disc(x + 14, y + 7, 4, 'E')
    clip(L, lambda xx, yy: yy < GROUND)
    L = outline(L, 'e')
    for (px, py) in ((4, 5), (9, 3), (12, 7), (7, 8), (15, 6)):
        L.put(x + px, y + py, 'e')
    f.blit(L.shift(dx, 0))


def easter_hunt(f, t, n):
    k = t % 20
    grass(f)
    bush(f, 24, 25, (k % 2) if k < 4 else 0)
    ec = {'c': 'P', 'd': 'U'}
    egg = None
    if k < 4:
        clawd(f, x=12, view='qr', ra='out', eyes='focus')
        if k % 2:
            f.art(['.E', 'E.'], 30 + k, 21 - k); f.art(['E.', '.E'], 36, 23 - k)
    elif k < 6:
        egg = [(31, 20), (26, 12)][k - 4]
        clawd(f, x=12, view='qr', eyes='big', lookv=-1)
    elif k < 10:
        dy = [0, -2, 0, -2][k - 6]
        info = clawd(f, x=12, y=BY + dy, la='up', ra='up', eyes='happy', legs=(1, 1, 1, 1) if dy else (0, 0, 0, 0))
        cx, top = info['head']
        egg = (int(cx) - 2, int(top) - 8)
    elif k < 14:
        x = 12 - (k - 9)
        info = clawd(f, x=x, view='ql', legs=steps(k % 2), y=BY + k % 2, eyes='happy', la='mid')
        egg = (int(info['lh'][0]) - 4, int(info['lh'][1]) - 4)
    elif k < 16:
        clawd(f, x=8, view='ql', la='up' if k == 14 else 'side', eyes='happy')
        egg = [(6, 18), (3, 26)][k - 14]
    else:
        x = 8 + (k - 15)
        clawd(f, x=x, view='qr', legs=steps(k % 2), y=BY + k % 2, eyes='normal')
    if egg:
        f.art(EGG, egg[0], egg[1], cmap=ec)
    f.art(BASKET, 0, 28)
    for (ex, c) in ((2, 'C'), (4, 'Z'), (6, 'U')):
        f.rect(ex, 30, 2, 1, c)
    if k == 15:
        P.sparkles(f, 0, 4, [(1, 25), (9, 26)])


def birthday_candles(f, t, n):
    k = t % 20
    L = Canvas()
    L.rect(22, 29, 15, 6, 'r'); L.rect(22, 32, 15, 1, 'Z'); L.rect(22, 28, 15, 1, 'W')
    for dx in range(0, 15, 3):
        L.put(22 + dx, 29, 'W')
    L = outline(L, 'Z')
    f.rect(20, 35, 19, 1, 'G')
    f.blit(L)
    lit = [k < 8 or k >= 16, k < 9 or k >= 17, k < 10 or k >= 18]
    bend = 1 if 8 <= k <= 10 else 0
    for i, (cx, c) in enumerate(((25, 'B'), (29, 'U'), (33, 'E'))):
        f.rect(cx, 23, 2, 5, c); f.put(cx, 24, 'W'); f.put(cx + 1, 26, 'W')
        f.put(cx, 22, 'k')
        if lit[i]:
            fl = pick([['.U', 'UF', 'UU'], ['U.', 'FU', 'UU']], t + i)
            f.art(fl, cx + bend, 19)
        elif k < 16:
            q = (k - 8 - i) % 4
            f.put(cx + (q % 2), 20 - q, 'L'); f.put(cx + 1 - (q % 2), 18 - q, 'L')
        if k == 16 + i:
            f.art(P.SPARK, cx - 1, 17)
    if 6 <= k <= 7:
        clawd(f, x=0, w=17, h=13, y=BY - 1, view='qr', eyes='closed')
    elif 8 <= k <= 10:
        clawd(f, x=1, view='qr', eyes='closed')
        for j in range(3):
            wx = 19 + (k - 8) * 2 + j * 2
            f.rect(wx, 25 + j * 2, 2, 1, 'L')
    elif 11 <= k <= 14:
        s = k % 2
        clawd(f, x=1, y=BY - s, la='up' if s else 'high', ra='up' if s else 'high', eyes='happy')
        P.confetti(f, t, n, count=10)
    else:
        clawd(f, x=1, view='qr', eyes='big' if 16 <= k <= 18 else 'happy')


add_tweened('sea_countdown', '新年倒计时', 'New Year countdown', countdown, n=20, dur=150, tw_at={11: 1, 19: 1})
add_tweened('sea_fireworks_watch', '看烟花', 'Watching fireworks', fireworks_watch, n=24, dur=110, tw_at={10: 2, 16: 2})
add('sea_party_popper', '拉礼花筒', 'Party popper', party_popper, n=16, dur=110)
add('sea_sparkler_heart', '仙女棒画心', 'Sparkler heart', sparkler_heart, n=16, dur=110)
add_tweened('sea_red_envelope', '收红包', 'Red envelope', red_envelope, n=20, dur=130, tw_at={7: 1, 8: 1})
add_tweened('sea_sky_lantern', '放孔明灯', 'Releasing a sky lantern', sky_lantern, n=20, dur=150, tw_at={4: 1, 15: 1})
add('sea_firecracker', '放鞭炮', 'Firecracker string', firecracker, n=16, dur=90)
add('sea_lion_dance', '舞狮', 'Lion dance', lion_dance, n=12, dur=120)
add_tweened('sea_fu_upside', '福倒了', 'Fu turned upside down', fu_upside, n=16, dur=140, tw_at={1: 1, 5: 1})
add('sea_dumpling_steamer', '开笼蒸饺子', 'Steamer of dumplings', dumpling_steamer, n=16, dur=140)
add('sea_mooncake_moon', '中秋赏月', 'Mooncake under the moon', mooncake_moon, n=16, dur=170)
add('sea_dragon_boat', '划龙舟', 'Dragon boat race', dragon_boat, n=8, dur=120)
add('sea_valentine_balloon', '爱心气球', 'Heart balloon lift', valentine_balloon, n=16, dur=120)
add_tweened('sea_easter_hunt', '找彩蛋', 'Easter egg hunt', easter_hunt, n=20, dur=130, tw_at={5: 1, 9: 1, 14: 1})
add_tweened('sea_birthday_candles', '吹生日蜡烛', 'Blowing out candles', birthday_candles, n=20, dur=130, tw_at={10: 1})
add('sea_bunny_hop', '复活节兔子跳', 'Easter bunny hop', S, n=8, dur=100, act='hop', hat='bunny', item='carrot',
    fx=['petals'])


# --------------------------------------------------------------------------- weather
def canopy(f, cx, top, c='U', rib='Y'):
    L = Canvas()
    for r, hw in enumerate((4, 7, 9, 11, 12, 13)):
        L.rect(cx - hw, top + r, 2 * hw + 1, 1, c)
    for x in range(cx - 13, cx + 14):
        if (x - cx) % 4 == 2:
            L.put(x, top + 5, None) if False else L.erase(x, top + 5)
    for dx in (-5, 0, 5):
        for r in range(1, 6):
            L.put(cx + dx * r // 5, top + r, rib)
    f.blit(outline(L, rib, of=c))


def umbrella_rain(f, t, n):
    cx, top = 21, 6
    r = rng(2)
    for i in range(20):
        x = r.randint(0, 39)
        p = (t / n * 2 + r.random()) % 1
        y = int(-3 + p * 40)
        if cx - 14 <= x <= cx + 14:
            if 1 <= y <= 4:
                f.rect(x, y, 1, 2, 'B')
            elif 5 <= y <= 9:
                f.put(x - 1, top - 1, 'S'); f.put(x + 1, top - 2, 'S')
            continue
        if y < 35:
            f.rect(x, y, 1, 2, 'B')
        else:
            w = (t + i) % 3
            f.rect(x - w, 37, 2 * w + 1, 1, 'B')
    for ex in (cx - 13, cx + 13):
        dy = (t * 3 + ex) % 24
        f.rect(ex, top + 7 + dy, 1, 2, 'B')
    f.rect(2, 37, 9, 1, 'S'); f.rect(29, 37, 9, 1, 'S')
    s = (t // 2) % 2
    info = clawd(f, x=7, y=BY + s, ra='up', eyes='happy', legs=steps(s))
    hx, hy = info['rh']
    f.rect(int(hx), top + 6, 1, int(hy) - top - 5, 'k')
    canopy(f, cx, top)
    P.notes(f, info, t, n, c='B', count=2, spread=6)


def puddle_jump(f, t, n):
    k = t % 12
    f.rect(8, 36, 24, 1, 'B'); f.rect(5, 37, 30, 1, 'B'); f.rect(8, 38, 24, 1, 'B')
    f.rect(12, 37, 4, 1, 'S'); f.rect(25, 36, 3, 1, 'S')
    dy = [0, 1, -3, -6, -8, -9, -8, -6, -3, 0, 0, 0][k]
    L = Canvas()
    if k in (1, 9):
        info = clawd(L, x=BX - 1, w=18, h=10, y=BY + 2, eyes='closed')
    else:
        air = dy < -2
        info = clawd(L, y=BY + dy, eyes='happy' if air else 'normal', la='up' if air else 'side',
                     ra='up' if air else 'side', legs=(1, 1, 1, 1) if air else (0, 0, 0, 0))
    O = col('O')
    for yy in range(info['y'] + info['h'] + 1, 40):
        for xx in range(40):
            if L.px[yy][xx] == O:
                L.px[yy][xx] = col('U')
    f.blit(L)
    if k >= 9 or k == 0:
        p = (k - 8) if k >= 9 else 4
        for j in range(8):
            side = -1 if j < 4 else 1
            spread = 3 + (j % 4) * 3
            x = 20 + side * (spread + p * 2)
            y = 36 - (5 + (j % 3) * 2) * p + p * p * 1.2
            if y < 37:
                f.rect(int(x), int(y), 1, 2 if j % 2 else 1, 'B' if j % 2 else 'S')
        if k == 9:
            f.rect(5, 35, 3, 1, 'S'); f.rect(32, 35, 3, 1, 'S')


BOLT_PTS = [(31, 8), (27, 15), (32, 18), (27, 26), (31, 29), (28, 36)]


def thunderstorm(f, t, n):
    k = t % 16
    flash = k == 6
    L = Canvas()
    L.rrect(3, 3, 34, 5, 'g'); L.rrect(7, 0, 14, 5, 'g'); L.rrect(20, 1, 13, 4, 'g')
    L = outline(L, 'k')
    L.rect(9, 1, 6, 1, 'G'); L.rect(22, 2, 5, 1, 'G')
    if flash:
        L.recolor(lambda c: col('y'))
    f.blit(L)
    P.rain(f, t, n, 4, 36, 9, 35, c='B', count=12)
    if k in (6, 7):
        for a, b in zip(BOLT_PTS, BOLT_PTS[1:]):
            f.line(a[0], a[1], b[0], b[1], 'U'); f.line(a[0] + 1, a[1], b[0] + 1, b[1], 'U')
            if k == 6:
                f.line(a[0], a[1], b[0], b[1], 'W')
        f.rect(25, 35, 6, 1, 'k')
    if 8 <= k <= 12:
        f.rect(26, 35, 4, 1, 'k')
        f.art(P.PUFF, 26 + (k % 2), 30 - (k - 8) * 2)
    if flash:
        clawd(f, y=BY - 4, eyes='big', la='up', ra='up', legs=(1, 1, 1, 1))
        for (sx, sy) in ((7, 18), (6, 24), (31, 14)):
            f.art(['U.U', '.U.', 'U.U'], sx, sy)
    elif k == 7:
        clawd(f, y=BY - 2, eyes='big', la='up', ra='up', legs=(1, 1, 1, 1))
    elif 8 <= k <= 11:
        r = rng(t)
        clawd(f, x=BX + r.choice((-1, 0, 1)), y=BY + 1, la='face', ra='face')
    else:
        r = rng(t)
        clawd(f, x=BX + r.choice((-1, 0, 1)), eyes='worried', la='low', ra='low', look=-1 if k > 12 else 0)


def rainbow(f, t, n):
    k = t % 20
    nb = 0
    if 9 <= k <= 14:
        nb = k - 8
    elif k in (15, 16):
        nb = 6
    lo = {15: 2, 16: 4}.get(k, 0)
    if nb:
        L = Canvas()
        for j, c in enumerate('RFUEBP'):
            if lo <= j < nb:
                L.ring(20, 31, 18 - j, c)
        clip(L, lambda x, y: y < 31)
        f.blit(L)
    if 7 <= k <= 17:
        P.sun(f, 5, 5, t)
    cxp = {6: 20, 7: 30, 8: 44, 18: -16, 19: -3}.get(k, 12 if k < 6 else None)
    if cxp is not None:
        L = Canvas(); P.cloud(L, cxp, 3, c='g', w=16); f.blit(outline(L, 'k'))
        if k < 6:
            P.rain(f, t, n, cxp + 1, cxp + 14, 10, 20, c='B', count=6)
    if k < 6:
        clawd(f, eyes='sad', la='low', ra='low', y=BY + 1, h=11)
    elif k < 9:
        clawd(f, eyes='normal', lookv=-1, look=1)
    elif k < 15:
        s = k % 2
        clawd(f, y=BY - s, la='up' if s else 'high', ra='up' if s else 'high', eyes='happy',
              legs=(1, 1, 1, 1) if s else (0, 0, 0, 0))
    elif k < 18:
        clawd(f, eyes='happy', lookv=-1)
    else:
        clawd(f, eyes='worried', look=-1, view='ql')


def snow_angel(f, t, n):
    k = t % 8
    L = Canvas()
    L.disc(20, 20, 19, 'W')
    f.blit(outline(L, 'G'))
    for (sx, sy) in ((6, 9), (33, 11), (8, 31), (31, 33), (20, 4)):
        f.put(sx, sy, 'G')
    x, y = BX, 13
    I = Canvas()
    for side in (-1, 1):
        sx, sy = (x - 1 if side < 0 else x + 16), y + 5
        for a in range(-70, 75, 5):
            ar = math.radians(a)
            for d in range(2, 9):
                I.put(sx + side * d * math.cos(ar), sy - d * math.sin(ar), 'S')
    for lx in range(x + 1, x + 15):
        for d in range(0, 6):
            I.put(lx + (d * (lx - x - 7)) // 8, y + 12 + d, 'S')
    f.blit(outline(I, 'C'))
    up = k in (1, 2, 3)
    mid = k in (0, 4)
    arm = 'up' if up else 'side' if mid else 'low'
    spread = 1 if up else 0
    clawd(f, x=x, y=y, eyes='happy', la=arm, ra=arm,
          legdx=(-spread, 0, 0, spread))
    P.falling(f, ['.S.', 'SWS', '.S.'], t, n, count=5, seed=4, sway=1)


def windy(f, t, n):
    f.rect(5, 5, 2, 31, 'g'); f.rect(3, 3, 6, 2, 'k'); f.rect(4, 5, 4, 1, 'U')
    L = Canvas()
    s = t % 2
    clawd(L, ra='up', la='side', eyes='squint', legs=(0, 1, 0, 1) if s else (1, 0, 1, 0))
    L = L.rot90(3, 20, 28)
    bb = L.bbox()
    L = L.shift(7 - bb[0], 19 - (bb[1] + bb[3]) // 2)
    L = L.shift(0, (t // 2) % 2)
    f.blit(L)
    r = rng(6)
    for i in range(7):
        y0 = r.randint(2, 36)
        x = (r.randint(0, 50) + t * 6) % 52 - 6
        y = y0 + int(round(2 * math.sin((x + i) / 4)))
        f.art(P.LEAF if i % 2 else ['EE', '.E'], x, y, cmap={'F': 'FYR'[i % 3]})
    for i in range(4):
        y = 8 + i * 8 + (i % 2)
        x = (i * 17 + t * 9) % 56 - 10
        f.rect(x, y, 7, 1, 'L')


SANDCASTLE = [
    ['.YYYYY.', 'YYYYYYY'],
    ['.........', '.........', '..YYYYY..', '.YYYYYYY.', 'YYYYYYYYY', 'YYYNNYYYY'],
    ['Y.Y......', 'YYY......', 'YYY......', 'YYYYYYY..', 'YYYNYYYY.', 'YYYYYYYYY', 'YYYNNYYYY'],
    ['Y.Y...Y.Y', 'YYY...YYY', 'YYY...YYY', 'YYYYYYYYY', 'YYYNYYNYY', 'YYYYYYYYY', 'YYYNNYYYY'],
]


def sandcastle(f, t, n):
    k = t % 24
    f.rect(0, 35, 40, 5, 'y')
    for (dx, dy) in ((3, 37), (11, 38), (19, 36), (27, 38), (35, 37)):
        f.put(dx, dy, 'Y')
    stage = 0 if k >= 19 or k < 3 else min(3, k // 3) if k < 12 else 3
    if k < 18:
        art = SANDCASTLE[stage]
        f.art(art, 26, 35 - len(art))
        if stage == 3 and 12 <= k <= 16:
            f.rect(30, 24, 1, 5, 'k'); f.rect(31, 24, 3, 2, 'R')
    elif k == 18:
        f.art(SANDCASTLE[1][3:], 26, 32)
    wx = {16: 33, 17: 23, 18: 19, 19: 28, 20: 34}.get(k, 37 + (t // 2) % 2)
    f.rect(wx, 33, 40 - wx, 3, 'B'); f.rect(wx, 33, 40 - wx, 1, 'S'); f.rect(wx - 1, 34, 1, 2, 'S')
    if k in (16, 17):
        f.rect(wx + 4, 28, 40 - wx - 4, 6, 'B')
        f.art(['...WWS.', '..WSBBB', '.WS.BBB', 'WS..BBB', 'S..BBBB'], wx - 1, 27)
    if k == 18:
        for j in range(5):
            f.put(wx + 2 + j * 3, 31 - (j % 2), 'W'); f.put(wx + 3 + j * 3, 32, 'S')
    if k < 12:
        pat = k % 2
        clawd(f, x=6, view='qr', ra='mid' if pat else 'low', eyes='focus', y=BY + (1 - pat))
    elif k < 16:
        s = k % 2
        clawd(f, x=6, y=BY - s, la='up' if s else 'side', ra='up' if s else 'side', eyes='happy')
    elif k < 21:
        clawd(f, x=6, view='qr', eyes='big' if k < 19 else 'sad', ra='side')
        if k in (16, 17):
            f.art(P.EXCL, 24, 12, cmap={'K': 'R'})
    else:
        clawd(f, x=6, view='qr', eyes='angry', ra='mid')
    f.rect(2, 31, 4, 4, 'R'); f.rect(2, 31, 4, 1, 'M'); f.put(3, 30, 'k'); f.put(4, 30, 'k')


def leaf_pile_art(f, grow=0):
    L = Canvas()
    for x in range(15, 40):
        hgt = int((9 + grow) * math.sqrt(max(0, 1 - ((x - 28) / 12.5) ** 2)))
        for y in range(36 - hgt, 36):
            c = 'Y' if (x + y * 2) % 5 == 0 else 'R' if (x * 3 + y) % 7 == 0 else 'F'
            L.put(x, y, c)
    f.blit(outline(L, 'N'))


def leaf_pile(f, t, n):
    k = t % 20
    if k < 4:
        leaf_pile_art(f)
        s = k % 2
        L = Canvas()
        clawd(L, x=-16 + k * 5, y=BY - 1 + s, view='qr', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2), eyes='happy')
        f.blit(L.shear(-0.08, 36))
        return
    if k < 8:
        leaf_pile_art(f)
        x, dy = [(2, -4), (8, -9), (14, -8), (18, -3)][k - 4]
        clawd(f, x=x, y=BY + dy, la='up', ra='up', legs=(1, 1, 1, 1), eyes='happy')
        return
    leaf_pile_art(f, 1 if k < 12 else 0)
    if 8 <= k <= 13:
        p = k - 7
        for j in range(12):
            a = math.radians(-160 + j * 13)
            v = 2.4 + (j % 3) * 0.6
            x = 28 + v * p * math.cos(a) + math.sin(p + j) * 1.5
            y = 28 + v * p * math.sin(a) + 0.35 * p * p
            if y < 35:
                f.art(P.LEAF if j % 2 else ['FF', '.F'], int(x), int(y), cmap={'F': 'FRYN'[j % 4], 'Y': 'Y'})
    if 10 <= k <= 13:
        f.art(['KK.....KK', 'KK.....KK'], 23, 29)
    elif 14 <= k <= 16:
        info = clawd(f, x=20, y=BY + [6, 3, 2][k - 14], eyes='happy', la='up' if k == 16 else 'side',
                     ra='up' if k == 16 else 'side')
        f.rect(20, 34, 16, 2, 'F'); f.put(23, 34, 'Y'); f.put(30, 35, 'R')
        P.hat(f, info, 'leaf')
    elif k >= 17:
        x = 20 + (k - 16) * 6
        s = k % 2
        info = clawd(f, x=x, y=BY + s, view='qr', legs=steps(s), eyes='happy')
        P.hat(f, info, 'leaf')


def flowers_bloom(f, t, n):
    k = t % 20
    grass(f)
    cols = 'ZPU'
    for i, px in enumerate((25, 30, 35)):
        if k < 16:
            st = max(0, min(4, (k - 2 - 2 * i) // 2))
        else:
            st = [3, 2, 1, 0][k - 16]
        a = P.sprout_art(st)
        if k >= 16 and st >= 3:
            a = [r.replace('Z', '.').replace('U', '.') for r in a]
        f.art(a, px - len(a[0]) // 2, 36 - len(a), cmap={'Z': cols[i]})
        if k >= 16:
            q = k - 15
            f.art(P.PETAL, px + q * 3, 26 - q * 3 - i, cmap={'r': cols[i]})
        if k == 2 * i + 10:
            P.sparkles(f, 0, 4, [(px, 26)])
    pour = k < 10
    info = clawd(f, x=2, view='qr', ra='mid', eyes='focus' if pour else 'happy')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    f.rect(hx, hy - 2, 5, 4, 'g'); f.rect(hx, hy - 2, 5, 1, 'G')
    f.put(hx + 1, hy - 4, 'g'); f.put(hx + 2, hy - 4, 'g'); f.put(hx + 3, hy - 4, 'g')
    f.put(hx, hy - 3, 'g'); f.put(hx + 4, hy - 3, 'g')
    if pour:
        f.line(hx + 5, hy, hx + 8, hy + 2, 'g'); f.rect(hx + 8, hy + 2, 2, 2, 'G')
        r = rng(t)
        for j in range(5):
            dx = (j * 2 + t) % 9
            dy = (j * 5 + t * 3) % 10
            f.rect(hx + 9 + dx // 2 + dy // 2, hy + 4 + dy, 1, 2, 'B')
    else:
        f.line(hx + 5, hy, hx + 8, hy - 3, 'g'); f.rect(hx + 8, hy - 4, 2, 2, 'G')


def sakura(f, t, n):
    k = t % 20
    f.line(0, 3, 24, 7, 'n'); f.line(10, 5, 16, 1, 'n'); f.line(18, 6, 27, 10, 'n'); f.line(0, 4, 12, 6, 'n')
    for (bx, by) in ((3, 2), (8, 5), (14, 1), (16, 6), (21, 4), (26, 9), (12, 7), (22, 8)):
        f.art(['.r.', 'rZr', '.r.'], bx - 1, by - 1)
    P.falling(f, P.PETAL, t, n, count=5, seed=6, sway=2, top=6)
    sneeze = k == 13
    if k < 10:
        px, py = 17 + 3 * math.sin(k * 0.9), 8 + k * 1.3
        f.art(P.PETAL, int(px), int(py), cmap={'r': 'Z'})
        look = -1 if px < 19 else 1 if px > 22 else 0
        clawd(f, y=BY + 2, leg_h=1, eyes='normal', lookv=-1, look=look)
    elif k < 13:
        jelly = k == 12
        info = clawd(f, y=BY + 2 - jelly, h=12 + jelly, w=16 + jelly, x=BX - (1 if jelly else 0) * 0, leg_h=1,
                     eyes='squint' if jelly else 'normal', lookv=-1)
        f.art(P.PETAL, 20, 22 - jelly, cmap={'r': 'Z'})
    elif sneeze:
        clawd(f, x=BX + 1, y=BY + 3, h=11, leg_h=1, eyes='closed')
        f.text('ACHOO', 12, 13, 'K')
        for (a, b) in ((7, 22), (32, 22), (9, 28), (30, 28)):
            f.put(a, b, 'L'); f.put(a + (1 if a > 20 else -1), b, 'L')
        f.art(P.PETAL, 22, 14, cmap={'r': 'Z'})
    else:
        q = k - 13
        f.art(P.PETAL, 22 + q * 3, 14 - q * 2 + (q % 2), cmap={'r': 'Z'})
        clawd(f, y=BY + 2, leg_h=1, eyes='happy', look=1)


def net(f, hx, hy, mode):
    hx, hy = int(hx), int(hy)
    if mode == 'up':
        f.line(hx, hy, hx + 2, hy - 7, 'N')
        cx, cy = hx + 3, hy - 10
    elif mode == 'mid':
        f.line(hx, hy, hx + 7, hy - 4, 'N')
        cx, cy = hx + 10, hy - 6
    else:
        f.line(hx, hy, hx + 7, hy + 2, 'N')
        cx, cy = hx + 10, hy + 3
    f.disc(cx, cy, 3, 'w')
    f.ring(cx, cy, 3, 'G')
    f.put(cx - 1, cy - 1, 'G'); f.put(cx + 1, cy + 1, 'G')


def butterfly_chase(f, t, n):
    k = t % 24
    a = 2 * math.pi * t / n
    bx = 22 + 12 * math.sin(a)
    by = 8 + 4 * math.sin(2 * a)
    swing = {5: 'mid', 6: 'down', 7: 'down', 17: 'mid', 18: 'down', 19: 'down'}.get(k, 'up')
    if swing == 'down':
        by -= 5
    x = int(round(6 + 8 * math.sin(a - 0.6)))
    miss = k in (8, 9, 20, 21)
    s = t % 2
    info = clawd(f, x=x, y=BY + s, legs=steps(s), eyes='big' if miss else 'focus' if swing != 'up' else 'happy',
                 ra='up' if swing == 'up' else 'out' if swing == 'mid' else 'low', look=1 if bx > x + 10 else 0)
    net(f, info['rh'][0], info['rh'][1], swing)
    P.butterfly(f, int(bx), int(by), t, c='P')
    if miss:
        f.art(P.QMARK, x + 2, BY - 9)
    P.sparkles(f, t, n, [(int(bx) - 3, int(by) + 5)]) if t % 3 == 0 else None


add('sea_umbrella_rain', '雨中撑伞', 'Umbrella in the rain', umbrella_rain, n=12, dur=110)
add_tweened('sea_puddle_jump', '踩水坑', 'Puddle jump', puddle_jump, n=12, dur=90, tw_at={1: 1, 8: 1})
add_tweened('sea_thunderstorm', '雷雨惊吓', 'Thunderstorm scare', thunderstorm, n=16, dur=110, tw_at={7: 1, 11: 1})
add_tweened('sea_rainbow', '雨后彩虹', 'Rainbow after rain', rainbow, n=20, dur=140, tw_at={8: 1})
add('sea_snow_angel', '雪地天使', 'Snow angel', snow_angel, n=8, dur=150)
add('sea_windy', '被大风吹', 'Blown by the wind', windy, n=12, dur=90)
add('sea_sandcastle', '海边堆沙堡', 'Sandcastle vs. the wave', sandcastle, n=24, dur=120)
add_tweened('sea_leaf_pile', '跳进落叶堆', 'Leaf pile dive', leaf_pile, n=20, dur=beats(20, 110, {3: 160, 5: 250, 8: 200, 14: 200, 15: 250}), tw_at={3: 1, 15: 1, 16: 1})
add('sea_flowers_bloom', '浇花开花', 'Watering flowers', flowers_bloom, n=20, dur=140)
add('sea_sakura', '樱花喷嚏', 'Sakura sneeze', sakura, n=20, dur=150)
add('sea_butterfly_chase', '扑蝴蝶', 'Chasing a butterfly', butterfly_chase, n=24, dur=100)


# --------------------------------------------------------------------------- nature & night
FF0 = [(30, 10), (28, 13), (26, 16), (24, 18), (22, 20), (21, 20), (20, 20), (20, 20), (20, 20), (20, 20),
       (20, 18), (21, 15), (23, 12), (26, 9), (29, 8), (31, 9)]


def glow(f, x, y, on=True):
    x, y = int(x), int(y)
    if on:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            f.put(x + dx, y + dy, 'Y')
        f.put(x, y, 'U')
    else:
        f.put(x, y, 'g')


def fireflies(f, t, n):
    k = t % 16
    P.moon(f, 33, 2)
    f.rect(0, 36, 40, 4, 'e')
    for x in range(2, 40, 6):
        f.put(x, 35, 'e'); f.put(x + 1, 34, 'e')
    a = 2 * math.pi * t / n
    for i, (bx, by, ka, kb) in enumerate(((6, 12, 1, 2), (35, 22, 2, 1), (9, 27, 1, 1), (30, 16, 1, 2))):
        glow(f, bx + 4 * math.sin(ka * a + i), by + 3 * math.sin(kb * a + i * 2), (t + i * 3) % 5 < 3)
    fx, fy = FF0[k]
    caught = 6 <= k <= 9
    look = -1 if fx < 18 else 1 if fx > 22 else 0
    clawd(f, y=BY + 2, leg_h=1, eyes='happy' if caught else 'big' if k == 10 else 'normal', look=look,
          lookv=-1 if not caught else 0, la='high' if caught else 'up' if k == 10 else 'side',
          ra='high' if caught else 'up' if k == 10 else 'side')
    if caught:
        f.put(19, 21, 'U' if t % 2 else 'Y'); f.put(20, 21, 'U')
        if t % 2:
            f.put(19, 19, 'Y'); f.put(20, 19, 'Y')
    else:
        glow(f, fx, fy)


STARS7 = [(3, 4), (8, 2), (13, 5), (18, 3), (23, 7), (25, 12), (19, 12)]


def telescope(f, t, n):
    k = t % 16
    lines = min(6, k) if k < 12 else 0
    for i in range(lines):
        f.line(*STARS7[i], *STARS7[i + 1], 'p')
    for i, (sx, sy) in enumerate(STARS7):
        if (t + i) % 4 == 0:
            f.art(['.U.', 'UUU', '.U.'], sx - 1, sy - 1)
        else:
            f.put(sx, sy, 'U')
    # eyepiece level with Clawd's near eye (q2r, x=5: eye on the front edge, rows 23-24)
    f.line(30, 24, 26, 35, 'g'); f.line(30, 24, 34, 35, 'g'); f.line(30, 24, 30, 35, 'g')
    for d in range(3):
        f.line(23, 24 + d - 1, 35, 15 + d - 1, 'V' if d else 'B')
    f.line(24, 23, 34, 15, 'S')
    f.rect(35, 13, 2, 4, 'G'); f.rect(21, 23, 2, 2, 'k')
    if 8 <= k <= 11:
        clawd(f, x=3, ra='up', eyes='happy', lookv=-1)
        if k in (9, 10):
            P.sparkles(f, 0, 4, [(14, 9), (24, 1)])
    else:
        clawd(f, x=5, view='q2r', eyes='closed', eyes_r='normal')


def shooting_star(f, t, n):
    k = t % 20
    P.sparkles(f, t, n, [(4, 4), (12, 9), (33, 3), (37, 13), (24, 2), (6, 15)])
    if 2 <= k <= 7:
        p = (k - 2) / 5
        hx, hy = 40 - 38 * p, 1 + 14 * p
        for j in range(9, 0, -1):
            f.put(hx + j * 1.4, hy - j * 0.55, 'U' if j < 3 else 'Y' if j < 6 else 'F')
        f.rect(int(hx), int(hy), 2, 2, 'U')
    if k < 8:
        hx = 40 - 38 * max(0, (k - 2) / 5) if k >= 2 else 34
        clawd(f, y=BY + 2, leg_h=1, eyes='big' if k >= 2 else 'normal', lookv=-1,
              look=1 if hx > 24 else -1 if hx < 16 else 0)
    elif k < 16:
        clawd(f, y=BY + 2, leg_h=1, eyes='closed', la='chin', ra='chin')
        if k >= 10:
            B = Canvas()
            B.rrect(24, 6, 12, 9, 'w'); B.rrect(25, 5, 10, 11, 'w'); B.rect(22, 17, 2, 2, 'w')
            f.blit(outline(B, 'G'))
            f.art(P.STAR5, 28, 8)
    else:
        clawd(f, y=BY + 2 - (k % 2), leg_h=1, eyes='happy', la='up' if k % 2 else 'side', ra='up' if k % 2 else 'side')
        P.sparkles(f, t, n, [(8, 18), (31, 17)])


def day_night(f, t, n):
    k = t % 24
    night = k >= 12
    p = ((k % 12) + 0.5) / 12
    ang = math.pi * (1 - p)
    sx, sy = 20 + 17 * math.cos(ang), 31 - 24 * math.sin(ang)
    if night:
        P.sparkles(f, t, n, [(4, 5), (12, 2), (27, 4), (36, 9), (8, 13), (33, 16)])
        P.moon(f, int(sx) - 3, int(sy) - 3)
    else:
        P.sun(f, int(sx), int(sy), t)
    L = Canvas()
    L.disc(20, 54, 22, 'E')
    f.blit(outline(L, 'e'))
    if night:
        b = (k // 3) % 2
        info = clawd(f, y=20 + b, h=12 - b, leg_h=1, eyes='closed', la='low', ra='low')
        P.zzz(f, info, t, n)
    elif k == 0:
        clawd(f, y=18, h=13, leg_h=1, eyes='closed', la='up', ra='up')
    else:
        look = -1 if sx < 15 else 1 if sx > 25 else 0
        wave = k in (5, 6)
        clawd(f, y=19, leg_h=1, eyes='line' if k == 11 else 'happy' if wave else 'normal', look=look,
              lookv=-1 if 3 <= k <= 8 else 0, ra=('up' if k == 5 else 'wave') if wave else 'side')


FOG = [(6, 3, 26, 0, 1), (13, 4, 30, 40, -1), (31, 3, 24, 15, 1), (35, 4, 32, 55, -1)]


def fog(f, t, n):
    k = t % 16
    f.rect(34, 10, 1, 26, 'g'); f.rect(32, 8, 5, 2, 'k'); f.rect(33, 10, 3, 1, 'U')
    if t % 2:
        f.put(31, 11, 'Y'); f.put(37, 11, 'Y'); f.put(34, 12, 'Y')
    x = 10 + int(round(5 * sin(t, n)))
    right = cos(t, n) >= 0
    s = t % 2
    clawd(f, x=x, y=BY + s, view='qr' if right else 'ql', legs=steps(s), eyes='squint' if k % 8 < 5 else 'normal')
    if 6 <= k <= 10:
        f.art(P.QMARK, x + 6, BY - 8)
    for (y, h, ln, base, d) in FOG:
        x0 = int((base + d * 72 * t / n) % 72) - 32
        f.rrect(x0, y, ln, h, 'L')
        f.rect(x0 + 2, y + 1, ln - 4, h - 2, 'w')


HAIL = ['WG', 'Gg']


def hail(f, t, n):
    k = t % 12
    L = Canvas()
    L.rrect(2, 0, 36, 4, 'g'); L.rrect(8, -2, 14, 5, 'g')
    f.blit(outline(L, 'k'))
    for (gx, gy) in ((3, 35), (8, 36), (31, 35), (36, 36), (26, 37), (12, 37)):
        f.art(HAIL, gx, gy)
    bx, by = BX, BY
    hits = 0
    r = rng(14)
    for i in range(10):
        x0 = r.randint(1, 37)
        p = (t / n * 2 + r.random()) % 1
        top = by - 8
        if bx + 1 <= x0 <= bx + 14:
            if p < 0.4:
                f.art(HAIL, x0, int(-3 + (top + 3) * p / 0.4))
            else:
                q = (p - 0.4) / 0.6
                side = 1 if x0 > bx + 8 else -1
                f.art(HAIL, int(x0 + side * q * 12), int(top - 9 * math.sin(q * math.pi) + q * q * 8))
                if q < 0.15:
                    hits += 1
                    f.art(['U.U', '.U.'], x0 - 1, top - 2)
        else:
            f.art(HAIL, x0, int(-3 + 38 * p))
    flinch = hits > 0
    info = clawd(f, y=by + (1 if flinch else 0), h=12 - (1 if flinch else 0), eyes='squint' if flinch else 'worried',
                 la='low', ra='low')
    y = info['y']
    f.rect(bx + 3, y - 6, 10, 1, 'g'); f.rect(bx + 2, y - 5, 12, 4, 'g'); f.rect(bx + 1, y - 1, 14, 1, 'G')
    f.rect(bx + 4, y - 5, 1, 4, 'G'); f.rect(bx + 2, y - 6, 1, 1, 'k'); f.rect(bx + 13, y - 6, 1, 1, 'k')


COW = ['W.WW.', 'WKWWW', 'WWKWW', 'k...k']


def tornado(f, t, n):
    k = t % 16
    a = 2 * math.pi * t / n
    items = []
    for j, (ph0, rad, yy) in enumerate(((0, 13, 14), (2.1, 11, 6), (4.2, 12, 24))):
        aa = a + ph0
        items.append((math.sin(aa) > 0, j, int(20 + rad * math.cos(aa)), int(yy + 2 * math.sin(aa))))

    def draw(item):
        _, j, x, y = item
        if j == 0:
            M = Canvas()
            mini(M, x - 4, y - 4, eyes='x' if k % 4 == 2 else 'normal')
            f.blit(M.rot90(k % 4, x, y))
        elif j == 1:
            f.art(COW if k % 2 else [r[::-1] for r in COW], x - 2, y - 2)
        else:
            f.rect(x - 3, y, 6, 2, 'N'); f.rect(x - 3, y, 6, 1, 'n')
            f.art(P.LEAF, x + 4, y - 3)
    for it in items:
        if not it[0]:
            draw(it)
    for y in range(1, 37):
        hw = 2 + (36 - y) * 0.38
        c = 20 + 1.5 * math.sin(y / 5 + a * 2)
        x0 = int(round(c - hw)); w = int(round(2 * hw))
        f.rect(x0, y, w, 1, 'L')
        f.put(x0, y, 'g'); f.put(x0 + w - 1, y, 'g')
        if y % 3 == 0:
            off = int((t * 3 + y * 2) % max(1, w - 3))
            f.rect(x0 + off, y, 3, 1, 'G')
    for it in items:
        if it[0]:
            draw(it)
    P.dust(f, 12, GROUND, ph(t, 4)); P.dust(f, 27, GROUND, ph(t + 2, 4), flip=True)


def ice_skate(f, t, n):
    a = 2 * math.pi * t / n
    x = int(round(12 + 11 * math.sin(a)))
    right = math.cos(a) >= 0
    f.rect(0, 36, 40, 4, 'S'); f.rect(0, 36, 40, 1, 'C')
    for (sx, sy, w) in ((4, 38, 4), (21, 37, 6), (33, 38, 3)):
        f.rect(sx, sy, w, 1, 'W')
    for j in range(1, 8):
        px = 12 + 10 * math.sin(a - j * 0.22) + (10 if right else 6)
        f.put(px, 37 + (j % 2), 'C')
    L = Canvas()
    info = clawd(L, x=x, y=BY - 1, view='qr' if right else 'ql', legs=(0, 0, 2, 2) if right else (2, 2, 0, 0),
                 la='high', ra='high', eyes='happy' if abs(math.cos(a)) > 0.5 else 'normal')
    P.hat(L, info, 'beanie')
    O, o = col('O'), col('o')
    for xx in range(40):
        if L.px[34][xx] in (O, o):
            L.rect(xx - 1, 35, 3, 1, 'g')
    L = L.shear(-0.06 if right else 0.06, 35)
    f.blit(L)
    R = L.flipy().shift(0, 32)
    clip(R, lambda xx, yy: 37 <= yy <= 38)
    f.blit(R.silhouette('C'))


def sledding(f, t, n):
    for x in range(40):
        y0 = int(14 + 0.3 * x)
        f.rect(x, y0, 1, 40 - y0, 'W'); f.put(x, y0, 'G')
    f.art(['..e..', '.eEe.', 'eEEEe', '..n..'], 33, 19)
    px = int(round(-26 + 74 * t / n))
    sy = lambda xx: 14 + 0.3 * xx
    S_ = Canvas()
    for i in range(20):
        yy = int(sy(px + i) - 3)
        S_.rect(px + i, yy, 1, 2, 'R'); S_.put(px + i, yy + 2, 'k')
    S_.put(px + 20, int(sy(px + 20)) - 2, 'k'); S_.put(px + 21, int(sy(px + 21)) - 3, 'k')
    f.blit(S_)
    cy = int(sy(px + 10)) - 3
    s = t % 2
    info = clawd(f, x=px + 2, y=cy - 13 + s, leg_h=1, view='qr', la='up', ra='up', eyes='happy')
    P.hat(f, info, 'beanie')
    for j in range(5):
        q = rng(j + t * 5)
        f.art(['W', 'G'] if j % 2 else ['G'], px - 2 - q.randint(0, 5), int(sy(px)) - 4 - q.randint(0, 5))
    P.speedlines(f, px - 3, cy - 10, t, n=3, length=5, c='G')


def hot_cocoa(f, t, n):
    k = t % 16
    f.rect(22, 3, 17, 18, 'N'); f.rect(23, 4, 15, 15, 'S')
    W_ = Canvas()
    P.falling(W_, ['W'], t, n, count=10, seed=7, xs=(23, 38), top=2, bottom=20, sway=1)
    clip(W_, lambda x, y: 23 <= x < 38 and 4 <= y < 19)
    f.blit(W_)
    f.rect(23, 17, 15, 2, 'W'); f.rect(30, 4, 1, 15, 'N'); f.rect(23, 11, 15, 1, 'N')
    f.rect(21, 19, 19, 2, 'N'); f.rect(21, 19, 19, 1, 'n')
    sip = 9 <= k <= 11
    info = clawd(f, x=3, y=BY + 2, leg_h=1, view='qr', la='none', ra='none',
                 eyes='closed' if sip or k % 8 in (5, 6) else 'normal')
    x, y = info['x'], info['y']
    f.rect(x - 2, y + 9, 20, 5, 'P')
    for yy in (y + 11,):
        f.rect(x - 2, yy, 20, 1, 'p')
    for xx in (x + 2, x + 8, x + 14):
        f.rect(xx, y + 9, 1, 5, 'p')
    f.rect(x - 2, y + 9, 20, 1, 'p')
    mx, my = (x + 12, y + 5) if sip else (x + 14, y + 8)
    f.rect(mx, my, 4, 4, 'R'); f.rect(mx - 1, my + 1, 1, 2, 'R'); f.rect(mx, my, 4, 1, 'n')
    f.put(mx + 1, my, 'W'); f.put(mx + 3, my, 'W')
    if not sip:
        P.rising(f, ['L'], t, n, mx + 2, my - 2, count=2, height=6, jitter=1, seed=3)


def snowball_fight(f, t, n):
    k = t % 24
    if k < 4 or k >= 20:
        y = BY + 3 if k < 4 or k >= 22 else BY + 1
        info = clawd(f, x=4, y=y, eyes='normal', look=1)
    elif k < 6:
        info = clawd(f, x=4, y=BY - 1, ra='up', eyes='angry')
        hx, hy = info['rh']
        snowball(f, hx, hy - 2, 2)
    elif k < 13:
        info = clawd(f, x=4, y=BY - 1, ra='out' if k < 8 else 'side', eyes='happy' if k > 8 else 'angry')
        q = (k - 5) / 6
        snowball(f, 24 + 20 * q, 16 - 12 * q * (1 - q) * 4 + q * 8, 2)
    elif k < 17:
        info = clawd(f, x=4, y=BY - 1, eyes='big' if k >= 15 else 'happy', look=1)
        q = (k - 12) / 4
        snowball(f, 42 - 30 * q, 6 + 12 * q - 6 * q * (1 - q) * 4, 2)
    else:
        info = clawd(f, x=4 + (1 if k % 2 else -1) * (k < 19), y=BY - 1, eyes='x', look=0)
        if k < 19:
            B = Canvas(); B.rrect(6, info['y'] - 3, 14, 4, 'W'); B.rect(8, info['y'] - 4, 9, 1, 'W')
            f.blit(outline(B, 'G'))
        else:
            for (a, b) in ((6, 15), (20, 14), (9, 12), (18, 11)):
                f.art(['.W.', 'WGW'], a, b)
    for r in range(3):
        y = 27 + r * 3
        for bx in range(-3 + (r % 2) * 3, 24, 6):
            f.rect(bx, y, 6, 3, 'W'); f.rect(bx, y + 2, 6, 1, 'G'); f.rect(bx + 5, y, 1, 3, 'G')
    f.rect(0, 26, 24, 1, 'G')
    f.rect(0, GROUND, 40, 40 - GROUND, 'W'); f.rect(24, GROUND, 16, 1, 'G')


def kite(f, t, n):
    grass(f)
    for (cx0, cy, w) in ((-14 + (t * 2) % 60, 14, 12), (10 + (t * 2) % 60 - 30, 20, 9)):
        L = Canvas(); P.cloud(L, cx0, cy, c='w', w=w); f.blit(outline(L, 'G'))
    kcx = 30 + int(round(2 * sin(t, n)))
    kcy = 8 + int(round(sin(t, n, 2)))
    for y in range(kcy - 6, kcy + 8):
        for x in range(kcx - 6, kcx + 7):
            dx, dy = x + .5 - kcx, y + .5 - kcy
            inside = (dy < 0 and abs(dx) <= (dy + 6) * 0.9) or (dy >= 0 and abs(dx) <= (7 - dy) * 0.75)
            if inside:
                c = ('Z' if dx < 0 else 'U') if dy < 0 else ('B' if dx < 0 else 'E')
                if abs(dx) < .6 or abs(dy) < .6:
                    c = 'k'
                f.put(x, y, c)
    for j in range(10):
        tx = kcx - j * 0.7 + 1.5 * math.sin(j * 0.8 - t * 0.8)
        ty = kcy + 7 + j
        f.put(tx, ty, 'k')
        if j % 3 == 2:
            f.art(['R.R', '.R.'], int(tx) - 1, int(ty), cmap={'R': 'RBZ'[j // 3]})
    tug = (t // 4) % 2
    L = Canvas()
    info = clawd(L, x=3, view='qr', ra='up' if tug else 'high', eyes='happy' if tug else 'focus')
    f.blit(L.shear(-0.06, 36) if tug else L)
    hx, hy = info['rh']
    hx += -1 if tug else 0
    kx, ky = kcx - 1, kcy + 6
    for i in range(40):
        s = i / 39
        f.put(hx + (kx - hx) * s, hy + (ky - hy) * s + 5 * s * (1 - s), 'g')


RLEAVES = [(13, 35), (16, 34), (18, 35), (21, 34), (23, 35), (25, 34), (27, 35), (29, 34)]


def rake_leaves(f, t, n):
    k = t % 16
    grass(f)
    if k < 12:
        cx = -12 + int(round(20 * k / 11))
        rx = cx + 24
        inpile = 0
        for i, (lx, ly) in enumerate(RLEAVES):
            x = max(lx, rx + 2 + i % 3)
            if x >= 32:
                inpile += 1
                continue
            f.art(P.LEAF, x, ly - 1, cmap={'F': 'FYRN'[i % 4]})
        hgt = 1 + inpile // 2
        for i in range(hgt + 1):
            f.rect(32 + i // 2, 35 - i, 8 - i, 1, 'FYRF'[i % 4])
        s = k % 2
        info = clawd(f, x=cx, y=BY + s, ra='low', legs=steps(s), eyes='focus')
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        f.line(hx, hy, rx + 1, 33, 'N')
        f.rect(rx, 34, 4, 1, 'g'); f.put(rx, 35, 'g'); f.put(rx + 2, 35, 'g')
        return
    q = (k - 11) / 4
    for i, (lx, ly) in enumerate(RLEAVES):
        x = 35 + (lx - 35) * q
        y = 31 + (ly - 31) * q - 10 * math.sin(q * math.pi) + (i % 3)
        f.art(P.LEAF, int(x), int(y), cmap={'F': 'FYRN'[i % 4]})
    for i in range(3):
        y = 10 + i * 7
        x = (i * 13 + k * 9) % 48 - 8
        f.rect(x, y, 8, 1, 'L')
    cx = 8 - (k - 11) * 5
    s = k % 2
    info = clawd(f, x=cx, y=BY + s, view='ql', legs=steps(s), eyes='big', ra='side')
    if k == 12:
        f.art(P.EXCL, cx + 7, BY - 8, cmap={'K': 'R'})


def dandelion(f, t, n):
    k = t % 20
    grass(f)
    inhale = k == 6
    blow = 7 <= k <= 9
    info = clawd(f, x=3, view='qr', ra='mid', eyes='closed' if inhale or blow else 'happy' if k >= 10 else 'normal',
                 h=13 if inhale else 12, y=BY - (1 if inhale else 0), lookv=-1 if 10 <= k <= 15 else 0)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    cx, cy = hx + 3, hy - 11
    f.line(hx + 1, hy, cx, cy + 2, 'E')
    if blow:
        for j in range(3):
            f.rect(hx - 3 + (k - 7) * 2 + j * 2, hy - 8 + j * 2, 2, 1, 'L')
    if k < 7 or k >= 18:
        f.disc(cx + .5, cy + .5, 3.2, 'W'); f.ring(cx + .5, cy + .5, 3.2, 'G')
        f.put(cx, cy, 'g')
    elif k >= 16:
        rr = [1.5, 2.5][k - 16]
        f.disc(cx + .5, cy + .5, rr, 'W'); f.ring(cx + .5, cy + .5, rr, 'G')
        if k == 16:
            P.sparkles(f, 0, 4, [(cx - 4, cy - 3), (cx + 5, cy - 1)])
    else:
        f.put(cx, cy, 'g'); f.put(cx, cy + 1, 'g')
    if 7 <= k < 16:
        for i in range(10):
            d = 7 + i % 3
            ang = i * math.pi / 5
            if k < d:
                f.put(cx + 3 * math.cos(ang), cy + 3 * math.sin(ang), 'G')
                continue
            q = k - d
            sx = cx + 3 * math.cos(ang) + q * (2.2 + (i % 4) * 0.4)
            sy = cy + 3 * math.sin(ang) - q * (1.0 + (i % 3) * 0.5) + math.sin(q + i)
            f.art(['G.G', '.g.'], int(sx), int(sy))


def heatwave(f, t, n):
    k = t % 16
    f.disc(33, 6, 4, 'U')
    for a in range(8):
        ang = a * math.pi / 4 + (t % 2) * math.pi / 8
        f.put(33 + math.cos(ang) * 6.5, 6 + math.sin(ang) * 6.5, 'F' if a % 2 else 'Y')
    for i in range(3):
        sx = 4 + i * 13
        sy = 32 - ((t * 2 + i * 5) % 12)
        f.art(['.F', 'F.', '.F', 'F.'], sx + (t + i) % 2, sy)
    f.rect(0, 36, 40, 1, 'Y')
    pop = k >= 8
    info = clawd(f, y=BY + 1, h=11, la='mid' if pop else 'low', ra='mid',
                 eyes='happy' if pop and k % 4 != 3 else 'line' if not pop else 'closed')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    up = t % 2
    if up:
        f.art(['RZRZRZR', '.RZRZR.', '..RZR..', '...k...'], hx - 2, hy - 6)
    else:
        f.art(['ZRZRZ', 'RZRZR', '.RZR.', '..k..'], hx - 1, hy - 3)
    f.rect(hx - 4, hy - 6 + up * 2, 2, 1, 'L'); f.rect(hx - 6, hy - 4 + up * 2, 2, 1, 'L')
    f.art(P.SWEAT, info['x'] - 3, info['y'] - 1 + (t % 3), flip=True)
    if pop:
        lx, ly = int(info['lh'][0]), int(info['lh'][1])
        f.art(['.CC.', 'CSCC', 'CCCC', 'CCCC', '.CC.', '..N.', '..N.'], lx - 4, ly - 6)
        dy = (k * 2) % 6
        f.put(lx - 3, ly + 1 + dy, 'C')


add('sea_fireflies', '夏夜萤火虫', 'Fireflies at night', fireflies, n=16, dur=140)
add_tweened('sea_telescope', '望远镜观星', 'Stargazing telescope', telescope, n=16, dur=150, tw_at={7: 1, 11: 1})
add('sea_shooting_star', '流星许愿', 'Wishing on a shooting star', shooting_star, n=20, dur=120)
add_tweened('sea_day_night', '日出日落', 'Sunrise to moonrise', day_night, n=24, dur=150, tw_at={0: 1, 4: 1, 6: 1, 23: 1})
add('sea_fog', '大雾迷路', 'Lost in the fog', fog, n=16, dur=130)
add('sea_hail', '冰雹敲桶', 'Hail on a bucket', hail, n=12, dur=90)
add('sea_tornado', '龙卷风', 'Caught in a tornado', tornado, n=16, dur=80)
add('sea_ice_skate', '溜冰', 'Ice skating', ice_skate, n=24, dur=100)
add('sea_sledding', '滑雪橇', 'Sledding downhill', sledding, n=16, dur=90)
add('sea_hot_cocoa', '窗边热可可', 'Cocoa by the snowy window', hot_cocoa, n=16, dur=170)
add_tweened('sea_snowball_fight', '打雪仗', 'Snowball fight', snowball_fight, n=24, dur=beats(24, 100, {16: 200, 17: 350, 18: 200}), tw_at={3: 1, 5: 1})
add('sea_kite', '放风筝', 'Flying a kite', kite, n=16, dur=130)
add('sea_rake_leaves', '扫落叶', 'Raking leaves', rake_leaves, n=16, dur=beats(16, 130, {12: 350}))
add('sea_dandelion', '吹蒲公英', 'Dandelion wish', dandelion, n=20, dur=140)
add('sea_snow_shiver', '冻得发抖', 'Shivering in the snow', S, n=8, dur=80, act='tremble', hat='beanie',
    fx=['snowbig'], eyes='worried')
add('sea_spring_breeze', '春风拂面', 'Spring breeze', S, n=12, dur=130, act='lean', hat='flower',
    fx=['petals', 'butterfly'], eyes='closed')
add('sea_heatwave', '热浪扇扇子', 'Heatwave fan & ice pop', heatwave, n=16, dur=130)
