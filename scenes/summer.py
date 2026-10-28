"""Scenes recreated from the third reference video (daytime: disco DJ, building site, beach, pool)."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, sin, cos, ph, pick, rng)
from engine import beats, add_tweened
import props as P

MINT = (190, 222, 210)
BALL = [['.K.', 'KWK', '.K.'], ['K.K', '.K.', 'K.K']]
BOARD = (214, 102, 150)


def ball(f, x, y, t):
    f.art(['WKW', 'KWK', 'WKW'] if t % 2 else ['KWK', 'WKW', 'KWK'], int(x), int(y), cmap={'W': 'W'})
    f.put(int(x) - 1, int(y) + 1, 'G'); f.put(int(x) + 3, int(y) + 1, 'G')


def mint_phones(f, info):
    P.headphones(f, info, c=MINT, pad=(160, 200, 188))


# --------------------------------------------------------------------------- disco DJ
def deck(f, t, spin=True):
    f.rect(8, 30, 26, 2, 'G'); f.rect(8, 32, 26, 5, 'g'); f.rect(8, 30, 26, 1, 'w')
    for cx in (13, 28):
        f.disc(cx, 30, 3, 'k')
        a = t * 1.3 + cx
        f.put(cx - 1 + round(math.cos(a) * 2), 29 + round(math.sin(a) * 1), 'W')
    for i in range(4):
        f.put(18 + i * 2, 33 + (t + i) % 2, pick(['U', 'C', 'Z', 'E'], i + t))


def disco(f, t):
    f.disc(20, 3, 3, 'G')
    for (x, y) in ((18, 2), (21, 3), (19, 4)):
        f.put(x, y, 'W' if (t + x) % 2 else 'g')
    r = rng(4)
    for i in range(5):
        if (t + i) % 3 == 0:
            f.put(r.randint(2, 38), r.randint(6, 20), pick(['C', 'Z', 'U'], i))


def dj(f, t, n):
    disco(f, t)
    s = t % 4
    info = clawd(f, y=BY - 1 + (t % 2), eyes='down' if s < 2 else 'normal', ra='front' if s in (1, 2) else 'side',
                 la='low')
    mint_phones(f, info)
    deck(f, t)
    P.notes(f, info, t, n, c='Y', count=2)


def vinyl(f, t, n):
    disco(f, t)
    k = t % 16
    up = 3 <= k <= 12
    info = clawd(f, eyes='happy' if up else 'normal', ra='up' if up else 'side', la='low')
    mint_phones(f, info)
    deck(f, t, spin=not up)
    if up:
        hx, hy = info['rh']
        cx, cy = int(hx) + 1, int(hy) - 5
        f.disc(cx, cy, 4, 'k'); f.disc(cx, cy, 1.5, 'R')
        a = t * 1.1
        f.put(cx + round(math.cos(a) * 3) - 1, cy + round(math.sin(a) * 3) - 1, 'g')
        if k % 3 == 0:
            f.art(P.SPARK, cx + 4, cy - 6)


# --------------------------------------------------------------------------- soccer
def keepy(f, t, n):
    """Ball travels foot -> knee -> head -> other side while Clawd follows it."""
    path = [(31, 33), (29, 26), (26, 19), (21, 15), (16, 15), (11, 19), (7, 26), (5, 33),
            (7, 26), (11, 19), (16, 15), (21, 15), (26, 19), (29, 26)]
    k = t % len(path)
    bx, by = path[k]
    v = 'qr' if bx > 22 else 'ql' if bx < 18 else 'front'
    kick = by >= 32
    info = clawd(f, view=v, look=(1 if bx > 20 else -1),
                 legs=(0, 0, 0, 2) if kick and bx > 20 else (2, 0, 0, 0) if kick else (0, 0, 0, 0),
                 lookv=-1 if by < 18 else 0, eyes='normal' if not kick else 'focus')
    ball(f, bx - 1, by - 1, t)


def header(f, t, n):
    k = t % 8
    hgt = [0, 5, 9, 11, 11, 9, 5, 0][k]
    squash = k == 0
    info = clawd(f, x=BX - (1 if squash else 0), w=18 if squash else 16, h=11 if squash else 12,
                 y=BY + (1 if squash else 0), eyes='closed' if squash else 'normal', lookv=-1, la='high', ra='high')
    ball(f, 19, info['y'] - 4 - hgt, t)
    if squash:
        f.art(['K.K', '...', '.K.'], 13, BY - 5, cmap={'K': 'L'}); f.art(['K.K', '...', '.K.'], 24, BY - 5, cmap={'K': 'L'})


# --------------------------------------------------------------------------- building site
HARDHAT = """
    ....UUUUUUUU....
    ..UUUUUYYUUUUU..
    .UUUUUYUUYUUUUU.
    UUUUUUYUUYUUUUUU
    UUUUUUUYYUUUUUUU
    YYYYYYYYYYYYYYYYYY
"""
GIRDER = ['gggggggggggggggggggggggggggggggggggggggg', 'g.G.G.G.G.G.G.G.G.G.G.G.G.G.G.G.G.G.G.Gg'.replace('.', 'g'),
          'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG']


def city(f, t):
    for i, (x, h) in enumerate(((2, 14), (8, 20), (14, 11), (24, 17), (31, 22))):
        f.box(x, 33 - h, 6, h + 1, 'G')
        for wy in range(36 - h, 33, 3):
            f.put(x + 2, wy, 'G'); f.put(x + 3, wy, 'G')


def hardhat_on(f, info, dy=0):
    f.art(HARDHAT, int(info['x']) - 1, int(info['y']) - 6 + dy)


def hardhat_hide(f, t, n):
    k = t % 20
    if k < 8:
        # tucked under the hat: only the shaded back and feet show
        f.rect(BX + 1, BY + 6, 14, 6, 'o'); f.rect(BX + 2, BY + 12, 2, 3, 'O'); f.rect(BX + 12, BY + 12, 2, 3, 'O')
        f.art(HARDHAT, BX - 1, BY + 1 - (1 if k in (3, 6) else 0))
        return
    if k < 12:
        rise = (k - 8) * 2
        info = clawd(f, y=BY + 6 - rise, h=6 + rise, eyes='normal' if k > 9 else 'none', leg_h=3)
        hardhat_on(f, info)
        return
    info = clawd(f, eyes='happy' if k < 15 else 'normal', ra='up' if k < 15 else 'side', la='up' if k < 15 else 'side')
    hardhat_on(f, info)


def wrench_work(f, t, n):
    k = t % 8
    f.rect(32, 14, 3, 22, 'g'); f.rect(31, 14, 5, 1, 'G'); f.rect(31, 35, 5, 1, 'G')
    f.rect(32, 24, 3, 3, 'k')
    info = clawd(f, x=BX - 2, view='q2r', ra=pick(['high', 'side', 'side', 'high'], k // 2), eyes='focus' if k % 4 else 'blink')
    hardhat_on(f, info)
    hx, hy = info['rh']
    wy = int(hy) - (3 if k // 2 in (0, 3) else 0)
    f.art(['G.G', 'GGG', '.G.', '.G.', '.G.'], int(hx), wy - 2)
    if k in (2, 6):
        f.art(['U.U', '.U.', 'U.U'], 33, 22)


def girder_walk(f, t, n):
    city(f, t)
    for row, y in enumerate((30, 31, 32)):
        f.art([GIRDER[row]], 0, y)
    for x in range(2, 40, 8):
        f.put(x, 31, 'k')
    x = -16 + int(56 * t / n)
    s = (t // 2) % 2
    info = clawd(f, x=x, y=14 + s, leg_h=3, view='q2r', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1),
                 la='up' if t % 6 < 3 else 'side')
    hardhat_on(f, info)


# --------------------------------------------------------------------------- beach / picnic
BASKET = ['..NNNNN..', '.N.....N.', 'YNYNYNYNY', 'NYNYNYNYN', 'YNYNYNYNY', '.YNYNYNY.']


def picnic(f, t, n):
    k = t % 16
    x = 4 + int(20 * tri(k, 16))
    right = k < 8
    s = t % 2
    info = clawd(f, x=x, y=BY + s, view='q2r' if right else 'q2l', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
    bx = int(info['lh'][0]) - 8 if right else int(info['rh'][0]) - 1
    f.art(BASKET, bx, BY + 6 + s)
    f.put(bx + 3, BY + 7 + s, 'R'); f.put(bx + 5, BY + 7 + s, 'R')
    p = (k % 8) / 8
    if p < 0.75:
        h = int(4 * (p / 0.75) * (1 - p / 0.75) * 12)
        f.art(['.e', 'RR', 'RR'], bx + 4, BY + 4 + s - h)


def tri(t, n):
    p = (t % n) / n
    return 1 - abs(2 * p - 1)


# --------------------------------------------------------------------------- pool (top view)
def tube(f, cx, cy, t):
    for y in range(cy - 13, cy + 14):
        for x in range(cx - 15, cx + 16):
            d = math.hypot((x + .5 - cx) / 15, (y + .5 - cy) / 13)
            if 0.62 <= d <= 1.0:
                a = math.atan2(y - cy, x - cx)
                f.put(x, y, 'S' if int((a + math.pi) / (math.pi / 4)) % 2 else 'B')
    # water ripples
    r = 16 + (t % 8) * 0.5
    for a in range(0, 360, 36):
        ang = math.radians(a + t * 5)
        f.put(cx + math.cos(ang) * r, cy + math.sin(ang) * (r - 2), 'S')


def pool(f, t, n, peek=False):
    k = t % 16
    bob = 1 if (t // 4) % 2 else 0
    tube(f, 20, 22 + bob, t)
    info = clawd(f, y=BY - 6 + bob, leg_h=3, eyes='normal', legs=(0, 1, 1, 0) if t % 4 < 2 else (0, 0, 0, 0))
    x, y, w = info['x'], info['y'], info['w']
    slide = 0
    if peek:
        slide = [0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0][k]
    if slide < 2 or not peek:
        f.rect(x, y + 2 + slide, w, 1, 'K')
        f.rect(x + 1, y + 2 + slide, 6, 3, 'K'); f.rect(x + w - 7, y + 2 + slide, 6, 3, 'K')
    else:
        f.rect(x, y + 4, w, 1, 'K')
        f.rect(x + 1, y + 4, 6, 2, 'K'); f.rect(x + w - 7, y + 4, 6, 2, 'K')
        f.art(['WW', 'WK'], x + 3, y + 1); f.art(['WW', 'KW'], x + w - 5, y + 1)
    if k in (5, 6) and not peek:
        f.art(['W.', '.W'], x + 3, y + 2); f.art(['W.', '.W'], x + w - 5, y + 2)
    if peek and k in (13, 14):
        f.art(['W.', '.W'], x + w - 5, y + 2)


# --------------------------------------------------------------------------- board sports
def sandboard(f, t, n):
    k = t % 16
    # dune slope from upper left to lower right with a lip
    for x in range(40):
        top = int(10 + x * 0.55) if x < 26 else int(10 + 26 * 0.55) - (x - 26) // 3
        f.rect(x, top + 8, 1, 40, 'y')
        f.put(x, top + 8, 'Y')
    p = k / 16
    x = -8 + int(p * 44)
    ground = (int(10 + (x + 8) * 0.55) + 8) if x + 8 < 26 else int(10 + 26 * 0.55) + 8
    air = 0
    if 10 <= k <= 14:
        air = [3, 6, 7, 6, 3][k - 10]
    by = ground - 15 - air
    L = Canvas()
    info = clawd(L, x=x, y=by, view='q2r', legs=(1, 1, 1, 1) if air else (0, 0, 0, 0),
                 eyes='happy' if air else 'focus', ra='up' if air else 'side')
    L.rect(x - 2, by + 15, 20, 1, BOARD); L.rect(x - 3, by + 14, 1, 1, BOARD)
    f.blit(L.shear(0, 36) if air else L.shear(-0.0, 36))
    if not air:
        P.dust(f, x - 3, ground, (t % 4) / 4)


def surf(f, t, n):
    k = t % 20
    # wave
    crest = 6 + int(2 * sin(t, 10))
    for x in range(40):
        h = int(14 + 10 * math.exp(-((x - 30) / 9) ** 2))
        top = 38 - h
        f.rect(x, top, 1, 40 - top, 'B')
        f.put(x, top, 'S')
    for x in range(26, 36):
        f.put(x, 38 - 24 + (x - 26) // 4 - 1, 'W')
    if k < 14:
        x = 2 + int(k * 1.4)
        lean = 1 if k % 4 < 2 else -1
        L = Canvas()
        info = clawd(L, x=x, y=8 + lean, view='q2r', la='up', ra='side', eyes='focus' if k % 6 else 'happy')
        L.rect(x - 2, 23 + lean, 20, 1, BOARD); L.rect(x - 3, 22 + lean, 2, 1, BOARD)
        f.blit(L.shear(0.06 * lean, 23))
        f.put(x - 4, 22, 'W'); f.put(x - 6, 21, 'W')
    elif k < 16:
        # wipeout: Clawd tumbles head-first off the board into the wave (k 14), board flips, splash
        if k == 14:
            L = Canvas()
            clawd(L, x=20, y=12, view='q2r', la='up', ra='up', eyes='x')
            f.blit(L.rot90(1, 28, 18))
        f.art(['W.W.W', '.WWW.', 'WW.WW'], 20, 14)
        f.rect(26, 8 - (k - 14) * 3, 2, 8, BOARD)
    else:
        bob = (k % 2)
        L = Canvas(); clawd(L, x=14, y=19 + bob, eyes='x' if k < 18 else 'squint')
        for yy in range(26, 40):
            L.px[yy] = [None] * 40
        f.blit(L)
        f.rect(12, 26, 18, 1, 'S')


def shades_drop(f, t, n):
    k = t % 16
    land = 6
    info_probe = Canvas()
    if k < land:
        info = clawd(f, eyes='normal', look=0, lookv=-1)
        y = -4 + k * 4
        f.rect(BX, y, 16, 1, 'K'); f.rect(BX + 1, y, 6, 3, 'K'); f.rect(BX + 9, y, 6, 3, 'K')
        return
    sq = k == land
    info = clawd(f, x=BX - (1 if sq else 0), w=18 if sq else 16, h=11 if sq else 12, y=BY + (1 if sq else 0),
                 eyes='none', ra='up' if 9 <= k <= 12 else 'side', la='side')
    P.face(f, info, 'shades')
    if k in (8, 9):
        f.art(['W.', '.W'], info['x'] + 2, info['y'] + 2)
    if 9 <= k <= 12:
        P.sparkles(f, k, 4, [(5, 14), (33, 12)])


# --------------------------------------------------------------------------- register (13)
add('dj_deck', '打碟', 'DJ at the decks', dj, n=8, dur=120)
add('dj_vinyl', '举起黑胶', 'Showing off a vinyl', vinyl, n=16, dur=130)
add('soccer_keepy', '颠足球', 'Keepy-uppy', keepy, n=14, dur=110)
add('soccer_header', '头顶球', 'Header bounces', header, n=8, dur=100)
add('hardhat_hide', '躲进安全帽', 'Hiding under a hard hat', hardhat_hide, n=20, dur=120)
add('hardhat_wrench', '工地拧螺丝', 'Wrench on the girder', wrench_work, n=8, dur=130)
add('girder_walk', '钢梁上散步', 'Girder stroll', girder_walk, n=28, dur=100)
add_tweened('picnic_basket', '提野餐篮', 'Picnic basket walk', picnic, n=16, dur=120, tw_at={7: 1, 15: 1})
add('pool_float', '泳池漂漂', 'Pool float', pool, n=16, dur=150)
add('pool_peek', '拉下墨镜偷看', 'Peeking over shades', pool, n=16, dur=140, peek=True)
add('sandboard', '沙丘滑板', 'Sandboarding', sandboard, n=16, dur=90)
add_tweened('surf_wipeout', '冲浪翻车', 'Surf and wipeout', surf, n=20, dur=beats(20, 110, {13: 160, 14: 300, 15: 200, 16: 250}), tw_at={19: 1})
add('shades_drop', '墨镜从天而降', 'Shades drop', shades_drop, n=16, dur=110)
