"""Daily life: food & drink, home chores, self-care and hobbies (60 scenes)."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, mini, sin, cos, ph, pick, tri, rng, parse, size,
                    text_w)
from engine import beats, add_tweened
import props as P
from kit import S


# --------------------------------------------------------------------------- helpers
def wl(t):
    """Alternating walk legs."""
    return (1, 0, 1, 0) if t % 2 else (0, 1, 0, 1)


def blinky(t, n, at=None, base='normal'):
    at = n - 3 if at is None else at
    return 'blink' if t % n == at else base


def arc(x0, y0, x1, y1, h, p):
    """Point on a parabola from (x0, y0) to (x1, y1) peaking h px above the chord."""
    x = x0 + (x1 - x0) * p
    y = y0 + (y1 - y0) * p - 4 * h * p * (1 - p)
    return int(round(x)), int(round(y))


def table(f, x, y, w, c='N', c2='n', legs=True):
    f.rect(x, y, w, 1, c); f.rect(x, y + 1, w, 1, c2)
    if legs:
        f.rect(x + 1, y + 2, 1, GROUND - y - 2, c2); f.rect(x + w - 2, y + 2, 1, GROUND - y - 2, c2)


def path_pts(way):
    """Pixel path through way-points (Bresenham per segment, no repeats)."""
    out = []
    for (x0, y0), (x1, y1) in zip(way, way[1:]):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            if not out or out[-1] != (x0, y0):
                out.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy
    return out


def cut(art, holes):
    """Return art rows with (col, row) pixels removed."""
    rows = [list(r) for r in parse(art)]
    for (i, j) in holes:
        if 0 <= j < len(rows) and 0 <= i < len(rows[j]):
            rows[j][i] = '.'
    return [''.join(r) for r in rows]


def crumbs(f, x, y, k, cols='YN'):
    for j in range(3):
        f.put(x + j * 2 - 2 + (k + j) % 2, y + k * 2 + j, cols[j % len(cols)])


# =========================================================================== FOOD & DRINK
PIZZA = [
    '.........NN',
    '.......UUNN',
    '.....UURUNN',
    '...UUUUUUNN',
    '.UUURUUUUNN',
    '...UUUUURNN',
    '.....URUUNN',
    '.......YUNN',
    '.........NN',
]


def pizza_art(b):
    holes = []
    for j in range(9):
        for i in range(11):
            if i < b or (b and i == b and 3 <= j <= 5) or (b and i == b + 1 and j == 4):
                holes.append((i, j))
    return cut(PIZZA, holes)


def pizza(f, t, n):
    k = t % 16
    b = [0, 0, 0, 3, 3, 3, 5, 5, 5, 7, 7, 7, 11, 11, 11, 11][k]
    chomp = k in (3, 6, 9, 12)
    x, y = 4, BY
    rise = {0: 6, 1: 2}.get(k, 0)
    gone = b >= 11
    info = clawd(f, x=x, y=y + (1 if chomp else 0), h=12 - (1 if chomp else 0), view='q2r',
                 ra='side' if gone else 'out',
                 eyes='closed' if chomp else ('happy' if k >= 13 else 'normal' if k < 2 else 'normal'))
    if not gone:
        px, py = x + 16 - 1 - (1 if chomp else 0), y + 3 + rise
        f.art(pizza_art(b), px, py)
        f.rect(px + 8, py + 6, 3, 2, 'O'); f.put(px + 10, py + 5, 'O')
    if k in (4, 5, 7, 8, 10, 11, 13, 14):
        crumbs(f, x + 17, y + 10, (k - 1) % 3)
    if k >= 13:
        f.art(P.HEART, x + 17, y - 4 - (k - 13))


DONUT = [
    '..rrrr..',
    '.rUrrBr.',
    'rWr..rZr',
    'rr....rr',
    'Yr....rY',
    'YYY..YYY',
    '.NYYYYN.',
    '..NNNN..',
]


def donut(f, t, n):
    """Tosses a donut up, spinning, and catches it ringed on the tip of a raised claw."""
    k = t % 14
    x, y = BX, BY
    up = 6 <= k <= 11
    crouch = k == 2
    eyes = 'normal' if k < 2 else 'closed' if crouch else 'big' if k < 9 else 'happy'
    clawd(f, x=x, y=y + (1 if crouch else 0), h=12 - (1 if crouch else 0), ra='up' if up else 'side',
          eyes=eyes, lookv=-1 if 3 <= k <= 8 else 0, look=1 if 3 <= k <= 8 else 0)
    w = 16
    rest = (x + w + 2, y + 3 + (1 if crouch else 0))
    ring = (x + w - 2, y - 6)
    if k < 3 or k >= 12:
        f.art(DONUT, *rest)
    elif k <= 8:
        px, py = arc(rest[0], rest[1], ring[0], ring[1], 16, (k - 3) / 6)
        f.art(DONUT if k % 2 else DONUT_EDGE, px, py + (0 if k % 2 else 2))
    else:
        f.art(DONUT if k % 2 == 0 else DONUT_EDGE, ring[0], ring[1] + (0 if k % 2 == 0 else 2))
        P.sparkles(f, k, 4, [(x + w + 9, y - 6), (x + w - 5, y - 9), (x - 3, y + 1)])


CONE = [
    '..rrr..',
    '.rWrrr.',
    'rrrrrrr',
    'rrrrrrr',
    'ZrrZrrZ',
    'YYYYYYY',
    '.YNYNY.',
    '.NYNYN.',
    '..YNY..',
    '..NYN..',
    '...Y...',
]


def icecream(f, t, n):
    k = t % 16
    x, y = 4, BY
    lick = k in (11, 12, 13)
    eyes = 'normal'
    if 3 <= k <= 9:
        eyes = 'worried'
    if k == 10:
        eyes = 'sad'
    if lick:
        eyes = 'closed'
    if k >= 14:
        eyes = 'happy'
    f.art(['.rrrr.', 'rrrrrr'], 27, 34)
    clawd(f, x=x, y=y + (1 if k == 12 else 0), h=12 - (1 if k == 12 else 0), view='q2r', ra='high', eyes=eyes)
    if lick:
        # scoop pressed to the front of the face, a lick at a time
        cx, cy = x + 16, y - 1
        f.art(cut(CONE, [(0, 2), (0, 3), (1, 1), (0, 4)][:2 * (k - 10)]), cx, cy)
        f.art(P.HEART, x + 10, y - 5 - (k - 11))
    else:
        cx, cy = x + 16 + 1, y - 7
        f.art(CONE, cx, cy)
    if not lick and k <= 5:
        L = k
        f.rect(cx + 6, cy + 4, 1, 1 + L, 'r')
        if L >= 3:
            f.rect(cx + 6, cy + 4 + L, 2, 1, 'r')
    if 6 <= k <= 9:
        dy = [27, 29, 31, 33][k - 6]
        f.art(['r', 'rr', 'rr'] if k > 6 else ['r', 'r'], cx + 6, dy - 2)
    if k == 10:
        f.art(['r....r', '.r..r.'], 27, 31)
        f.art(P.SWEAT, x + 18, y - 2)


def noodles(f, t, n):
    k = t % 12
    x, y = 3, BY
    slurp = 4 <= k <= 8
    chew = k >= 9
    bob = 1 if chew and k % 2 else 0
    eyes = 'normal' if k < 2 else 'big' if k < 4 else 'closed' if slurp else 'happy'
    info = clawd(f, x=x, y=y + bob, h=12 - bob, view='q2r', ra='high', eyes=eyes)
    fe, my = x + 16, y + 6
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    bx, by = 20, 30
    # chopsticks
    if k < 2:
        tip = (27, 31)
    elif k == 2:
        tip = (25, 27)
    elif k <= 8:
        tip = (fe + 1, my)
    else:
        tip = (30, 21)
    f.line(hx, hy - 1, tip[0], tip[1], 'N'); f.line(hx + 1, hy, tip[0] + 1, tip[1] + 1, 'n')
    # noodles hanging from the chopsticks / being slurped up to the front of the face
    if 2 <= k <= 8:
        top = tip[1] + 1
        bot = by if k <= 4 else [by - 1, by - 3, by - 5, my + 2][k - 5]
        for i in range(3):
            sx = tip[0] - 1 + i
            for yy in range(top, bot):
                f.put(sx + ((yy + k + i) // 2) % 2, yy, 'Y')
        if slurp:
            for (dx, dy) in ((5, -3), (7, 0), (4, 3), (8, -2)):
                if (k + dx) % 2:
                    f.put(fe + dx, my + dy, 'B')
    # bowl
    f.rect(bx + 1, by, 16, 1, 'T'); f.put(bx, by, 'G'); f.put(bx + 17, by, 'G')
    for i in range(3):
        f.put(bx + 4 + i * 5 + (k % 2), by, 'Y')
    for j, (a, w) in enumerate(((0, 18), (1, 16), (2, 14), (3, 12))):
        f.rect(bx + a, by + 1 + j, w, 1, 'W')
        f.put(bx + a, by + 1 + j, 'G'); f.put(bx + a + w - 1, by + 1 + j, 'G')
    for i in range(1, 15, 3):
        f.rect(bx + 1 + i, by + 2, 2, 1, 'R')
    f.rect(bx + 5, by + 5, 8, 1, 'g')
    P.rising(f, ['L'], t, n, bx + 9, by - 2, count=2, height=6, jitter=5, seed=3)
    if chew:
        f.art(P.HEART, x + 15, y - 4 - (k - 9))


BOBA_WAY = [(32, 21), (32, 14), (31, 12), (30, 11), (29, 10), (27, 10), (26, 11), (25, 12), (24, 14),
            (24, 18), (23, 21), (22, 24), (21, 26)]
BOBA_PATH = path_pts(BOBA_WAY)


def boba(f, t, n):
    x, y = 4, BY
    # how close is a pearl to the front of the face?
    ps = [((t / n) + i / 2) % 1 for i in range(2)]
    gulp = any(p > 0.88 for p in ps)
    info = clawd(f, x=x, y=y + (1 if gulp else 0), h=12 - (1 if gulp else 0), view='q2r',
                 eyes='happy' if gulp else 'closed', w=16 + (1 if gulp else 0))
    # cup
    cx, cy = 28, 23
    for j in range(13):
        a = 0 if j < 4 else 1 if j < 10 else 2
        w = 9 - 2 * a
        f.rect(cx + a, cy + j, w, 1, 'T' if j < 9 else 'n')
        f.put(cx + a, cy + j, 'L'); f.put(cx + a + w - 1, cy + j, 'L')
    f.rect(cx + 3, cy + 12, 3, 1, 'L')
    for (px, py) in ((cx + 3, cy + 9), (cx + 5, cy + 10), (cx + 2, cy + 10), (cx + 4, cy + 11)):
        f.put(px, py, 'N')
    f.rect(cx, cy - 1, 9, 1, 'L'); f.rect(cx + 1, cy - 2, 7, 1, 'L'); f.rect(cx + 2, cy - 2, 2, 1, 'W')
    # straw + travelling pearls
    for (px, py) in BOBA_PATH:
        f.put(px, py, 'Z')
    for p in ps:
        if p < 0.92:
            px, py = BOBA_PATH[int(p / 0.92 * (len(BOBA_PATH) - 1))]
            f.rect(px, py, 2, 2, 'n'); f.put(px, py, 'N')
    if gulp:
        f.art(['.K.', 'K.K'], x + 17, y - 1)


BURGER = [  # bottom -> top: (art, y)
    (['YYYYYYYYYYYY', '.NNNNNNNNNN.'], 32),
    (['.nnnnnnnnnn.', 'nNnnnNnnnnNn', '.nnnnnnnnnn.'], 29),
    (['UUUUUUUUUUUU', '.U...U..U...'], 28),
    (['E.EE.EE.EE.E', 'EEEEEEEEEEEE'], 26),
    (['RRRRRRRRRRRR'], 25),
    (['...YYYYYY...', '.YYTYYYYTYY.', 'YYYYYTYYYYYY', 'YYYYYYYYYYYY'], 21),
]


def burger(f, t, n):
    k = t % 20
    bx = 24
    f.rect(bx - 2, 34, 16, 1, 'W'); f.put(bx - 2, 34, 'G'); f.put(bx + 13, 34, 'G')
    f.rect(bx - 1, 35, 14, 1, 'G')
    chomp = k == 14
    bitten = 14 <= k <= 16
    gone = k >= 17
    look = 0
    lookv = -1 if k < 12 else 0
    eyes = 'normal' if k < 12 else 'big' if k < 14 else 'closed' if chomp else 'happy'
    info = clawd(f, x=4 + (3 if chomp else 0), y=BY, view='qr', look=1, lookv=lookv, eyes=eyes, la='low' if gone else 'side', ra='low' if gone else 'side')
    if not gone:
        for j, (art, yy) in enumerate(BURGER):
            land = 2 * j + 2
            if k < 2 * j:
                continue
            if k < land:
                dy = [-16, -6][k - 2 * j]
            else:
                dy = 1 if k == land and j < 5 else 0
            a = art
            if bitten:
                a = cut(a, [(i, r) for i in range(4) for r in range(len(a))
                            if (yy + r) in range(22, 31) and i < 4 - abs(yy + r - 26) // 2])
            f.art(a, bx, yy + dy)
        if k in (12, 13):
            P.sparkles(f, k, 4, [(bx - 2, 18), (bx + 13, 20), (bx + 6, 15)])
    else:
        crumbs(f, bx + 4, 30, k - 17, 'YN')
        if k == 17:
            f.art(P.PUFF, bx + 4, 27)
    if bitten and not chomp:
        crumbs(f, 22, 30, k - 15)


SUSHI = [
    ['.FyFF.', 'GWWWWG'],
    ['.RRRR.', 'GWWWWG'],
    ['.UkUU.', 'GWkWWG'],
    ['.kkkk.', '.kWFk.'],
]
PLATE_C = ['B', 'Z', 'U', 'E']


def sushi(f, t, n):
    k = t % 20
    x, y = 4, BY - 4
    eat = 10 <= k <= 13
    look = -1 if (k >= 14 or k < 4) else 0
    eyes = 'happy' if eat else 'big' if 7 <= k <= 9 else blinky(k, 20, 17)
    bob = 1 if eat and k % 2 else 0
    info = clawd(f, x=x, y=y + bob, h=12 - bob, view='q2r', ra='side', look=look, eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    fe = x + 16
    if k in (5, 6):
        tip = (28, 24) if k == 5 else (26, 27)
    elif 7 <= k <= 9:
        tip = [(25, 24), (23, 23), (fe, y + 5)][k - 7]
    else:
        tip = (32, 14)
    f.line(hx - 1, hy - 1, tip[0], tip[1], 'N'); f.line(hx, hy, tip[0] + 1, tip[1] + 1, 'n')
    if 7 <= k <= 9:
        f.art(['.RRRR.', 'GWWWWG'], tip[0], tip[1] + 1)
    if eat:
        f.art(P.HEART, x + 12, y - 4 - (k - 10))
    # belt
    f.rect(0, 31, 40, 2, 'G')
    for xx in range(-4, 44, 4):
        f.put(xx + (2 * k) % 4, 32, 'g')
    f.rect(0, 33, 40, 3, 'g'); f.rect(0, 33, 40, 1, 'k')
    for xx in range(2, 40, 10):
        f.rect(xx, 34, 2, 1, 'G')
    for i in range(-4, 5):
        px = -1 + 10 * i + 2 * k
        if px < -9 or px > 40:
            continue
        c = PLATE_C[i % 4]
        f.rect(px, 29, 8, 1, c); f.rect(px + 1, 30, 6, 1, c)
        f.put(px + 1, 30, 'g'); f.put(px + 6, 30, 'g')
        if not (i == 1 and k >= 7):
            f.art(SUSHI[i % 4], px + 1, 27)


MELON = [
    'RRRKRRRRKRRR',
    '.RRRRRKRRRR.',
    '..wwwwwwww..',
    '...EEEEEE...',
]


def melon(f, t, n):
    k = t % 16
    x, y = 3, BY
    spit = k in (5, 9, 13)
    puff = k in (4, 8, 12)
    munch = not (spit or puff)
    bob = 1 if munch and k % 2 else 0
    clawd(f, x=x, y=y + bob, h=12 - bob, view='q2r', w=16 + (1 if puff else 0),
          eyes='closed' if munch else 'normal' if spit else 'squint')
    fe = x + 16 + (1 if puff else 0)
    wedge = cut(MELON, [(0, 0), (1, 0), (2, 0)])
    if munch:
        f.art(wedge, fe, y + 5)
    else:
        f.art(wedge, fe + 2, y + 9)
    if spit:
        f.art(['L.', '.L', 'L.'], fe + 1, y + 4)
    for s_, k0 in enumerate((5, 9, 13)):
        d = (k - k0) % 16
        if 0 <= d <= 6:
            sx, sy = arc(fe + 1, y + 6, 41, 34, 10, d / 6)
            f.rect(sx, sy, 1, 2, 'K')
    if spit:
        f.text('PTU', fe + 1, y - 5, 'g')


KERNEL = ['.UU.', 'UWWU', 'YWWY', '.YY.']


def popcorn(f, t, n):
    x, y = 6, BY
    # bucket
    bx = 30
    for j in range(9):
        a = 0 if j < 3 else 1 if j < 7 else 2
        for i in range(a, 9 - a):
            f.put(bx + i, 27 + j, 'R' if (i // 2) % 2 == 0 else 'W')
        f.put(bx + a, 27 + j, 'G' if (a // 2) % 2 else 'R')
        f.put(bx + 8 - a, 27 + j, 'G')
    f.rect(bx + 2, 35, 5, 1, 'G')
    for (px, py) in ((bx, 25), (bx + 3, 24), (bx + 6, 25), (bx + 2, 26), (bx + 5, 26)):
        f.art(KERNEL, px, py)
    catching = False
    chew = False
    for i in range(2):
        d = (t + i * 6) % 12
        if d < 7:
            kx, ky = arc(33, 23, x + 16, y + 6, 16, d / 6)
            f.art(KERNEL, kx - 1, ky - 1)
            if d >= 4:
                catching = True
        elif d < 10:
            chew = True
    bob = 1 if chew and t % 2 else 0
    clawd(f, x=x, y=y + bob, h=12 - bob, view='q2r', lookv=-1 if catching else 0,
          eyes='big' if catching else 'happy' if chew else 'normal')
    if chew:
        crumbs(f, x + 17, y + 9, t % 3, 'yW')
    # re-draw airborne kernels on top of Clawd
    for i in range(2):
        d = (t + i * 6) % 12
        if d < 6:
            kx, ky = arc(33, 23, x + 16, y + 6, 16, d / 6)
            f.art(KERNEL, kx - 1, ky - 1)


CAKE = [
    '.......WW',
    '....WWWWG',
    '.WWWWWWWG',
    'WWWWWWWWG',
    'yyyyyyyyN',
    'ZZZZZZZZn',
    'yyyyyyyyN',
    'yyyyyyyyN',
]
BERRY = ['.E.', 'RRR', 'RWR', '.R.']


def cake(f, t, n):
    k = t % 16
    x, y = 2, BY
    table(f, 22, 31, 17)
    f.rect(23, 30, 15, 1, 'W'); f.put(23, 30, 'G'); f.put(37, 30, 'G')
    f.art(CAKE, 26, 22)
    hx, hy = x + 16 + 4, y + 2
    eyes = 'normal'
    if 5 <= k <= 8:
        eyes = 'happy'
    elif 9 <= k <= 11:
        eyes = 'closed'
    elif k >= 12:
        eyes = 'happy'
    info = clawd(f, x=x, y=y + (1 if k in (10, 11) else 0), view='q2r', ra='high', eyes=eyes)
    # fork tip path
    rest = (31, 18)
    if k < 3:
        tip = [(24, 16), (27, 14), (30, 16)][k]
    elif k == 3:
        tip = (31, 18)
    elif k == 4:
        tip = (30, 15)
    elif k <= 8:
        tip = [(28, 11), (26, 9), (26, 9), (27, 10)][k - 5]
    elif k == 9:
        tip = (21, 26)
    else:
        tip = (24, 17)
    f.line(hx, hy, tip[0], tip[1] + 3, 'g')
    f.art(['G.G', 'GGG'], tip[0] - 1, tip[1] + 1)
    have = 4 <= k <= 8
    if have:
        f.art(BERRY, tip[0] - 1, tip[1] - 3)
        if k in (6, 7):
            P.sparkles(f, k, 4, [(tip[0] - 5, tip[1] - 4), (tip[0] + 4, tip[1] - 5), (tip[0], tip[1] - 8)])
    # strawberry on the cake
    if k < 4 or k >= 13:
        by = 18 if k < 4 or k >= 15 else [4, 12][k - 13]
        if k == 3:
            by = 18
        f.art(BERRY, 31, by)
    if k in (10, 11, 12):
        f.art(P.HEART, x + 17, y - 4 - (k - 10) * 2)


APPLES = [
    ['...nE..', '..RnEE.', '.RRRRR.', 'RRWRRRR', 'RRRRRRR', 'RRRRRRR', '.RRRRR.', '..R.R..'],
    ['...nE..', '..RnEE.', '..TRRR.', '.TTRRRR', '.TTRRRR', '..TRRRR', '.RRRRR.', '..R.R..'],
    ['...nE..', '...nEE.', '..TTRR.', '..TTTR.', '..TTTR.', '..TTRR.', '.RRRRR.', '..R.R..'],
    ['...nE..', '...nE..', '..RRR..', '..TTT..', '...T...', '..TTT..', '..RRR..', '.......'],
]


def apple(f, t, n):
    k = t % 12
    x, y = 5, BY
    state = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0][k]
    bite = k in (2, 5, 8)
    toss = k in (9, 10)
    chew = k in (3, 4, 6, 7)
    eyes = 'closed' if bite else 'happy' if chew or k in (10, 11) else 'normal'
    dy = 1 if bite or (chew and k % 2) else 0
    info = clawd(f, x=x, y=y + dy, h=12 - dy, view='q2r', ra='up' if toss else 'high', eyes=eyes)
    fe = x + 16
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if bite:
        f.art(APPLES[state], fe - 1, y + 2)
        f.text_c('CRUNCH', 24, 8 + (k % 2), 'R')
        for (dx, dy2) in ((8, -2), (9, 3), (7, 7)):
            f.put(fe + dx, y + 4 + dy2, 'T')
    elif toss:
        cx, cy = arc(hx - 2, hy - 7, -8, 6, 10, (k - 8) / 3)
        f.art(APPLES[3], cx, cy)
    else:
        f.art(APPLES[0 if k == 11 else state], hx - 1, hy - 6)
        if k == 11:
            f.art(P.SPARK, hx + 6, hy - 9)
    if chew:
        crumbs(f, fe + 1, y + 9, k % 3, 'TR')


LEMON = ['..UUU', '.UyWU', 'UyWyU', 'UWyU.', 'UUU..']


def lemon(f, t, n):
    k = t % 14
    x, y = 6, BY
    fe = x + 16
    if k < 2 or k >= 9:
        eyes = 'blink' if k == 9 else 'happy' if k >= 11 else 'normal'
        info = clawd(f, x=x, y=y, view='q2r', ra='high', eyes=eyes)
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        art = LEMON if k < 2 else cut(LEMON, [(0, 2), (0, 3), (1, 3), (0, 4), (1, 4), (2, 4)])
        f.art(art, hx - 1, hy - 5)
        if k == 9:
            f.art(P.SWEAT, x + 17, y - 2)
        return
    if k == 2:
        clawd(f, x=x, y=y + 1, h=11, view='q2r', ra='high', eyes='closed')
        f.art(LEMON, fe - 1, y + 2)
        return
    # the sour shiver: squash/stretch pulses, jitter, effects around (never on) Clawd
    j = k - 3
    w, h = [(14, 14), (17, 11), (14, 14), (17, 11), (15, 13), (16, 12)][j]
    jx = (1 if k % 2 else -1)
    clawd(f, x=x + (16 - w) // 2 + jx, y=y + 12 - h, w=w, h=h, view='q2r', ra='low', la='low',
          eyes='squint' if j % 2 else 'x')
    for (sx, sy) in ((x - 6, y + 1), (x + 20, y + 2)):
        f.art(['S.', '.S', 'S.', '.S'] if (k + sx) % 2 else ['.S', 'S.', '.S', 'S.'], sx, sy)
    f.art(P.EXCL, x + 6, y - 9 + (k % 2), cmap={'K': 'Y'})
    f.art(P.EXCL, x + 8, y - 9 + (k % 2), cmap={'K': 'Y'})
    if j >= 3:
        f.art(P.SWEAT, x + 18, y - 3)


CAN = ['.GGG.', 'GgGgG', 'RRRRR', 'RWWRR', 'RRWWR', 'RRRRR', 'RWRRR', 'RRRRR', '.GGG.']


def soda(f, t, n):
    k = t % 16
    x, y = BX, BY
    shaking = k < 6
    spray = 7 <= k <= 11
    drip = 10 <= k <= 15
    eyes = ('angry' if shaking else 'big' if k == 6 else 'big' if spray else
            'sad' if k < 14 else 'blink' if k == 14 else 'normal')
    up = shaking and k % 2 == 0
    info = clawd(f, x=x + ((1 if k % 2 else -1) if shaking else 0), y=y,
                 ra='up' if up else 'mid' if shaking else 'high', eyes=eyes)
    hx, hy = info['rh']
    if shaking:
        cxx, cyy = int(hx) - 2, int(hy) - (9 if up else 6)
        for i in range(3):
            f.rect(cxx + 6, cyy + 1 + i * 3 + (2 if up else -1), 2, 1, 'L')
            f.rect(cxx - 3, cyy + 2 + i * 3 + (2 if up else -1), 2, 1, 'L')
    else:
        cxx, cyy = int(hx) - 1, int(hy) - 9
    f.art(CAN, cxx, cyy)
    if k == 6:
        f.text('PSST', cxx - 5, cyy - 7, 'g')
        f.art(['N.N', '.N.'], cxx + 1, cyy - 2)
    if spray:
        top = [cyy - 7, cyy - 14, cyy - 17, cyy - 17, cyy - 12][k - 7]
        for yy in range(top, cyy):
            wid = 1 + (cyy - yy) // 6
            ox = int(round(math.sin((yy + k * 2) / 2.0)))
            f.rect(cxx + 2 - wid + ox, yy, 2 * wid + 1, 1, 'T')
            f.put(cxx + 2 + ox, yy, 'N')
        f.rrect(cxx - 2, top - 4, 9, 5, 'T'); f.rect(cxx - 1, top - 3, 2, 1, 'W')
        f.put(cxx + 2, top - 2, 'N'); f.put(cxx + 5, top - 1, 'N')
        r = rng(k)
        for i in range(8):
            a = r.uniform(0.1, math.pi - 0.1)
            d = 4 + (k - 7) * 2 + r.random() * 4
            f.rect(cxx + 2 + math.cos(a) * d * 1.4, top - 1 + (k - 7) * 2 - math.sin(a) * 3 + r.random() * 3,
                   1, 2, 'N' if i % 2 else 'T')
    if drip:
        # a blob of foam lands on top of the head; drops fall past the sides
        hx0, top0 = info['head']
        sz = max(0, 3 - max(0, k - 12))
        if sz:
            f.rrect(int(hx0) - 2 - sz, top0 - 2, 4 + 2 * sz, 2, 'T'); f.put(int(hx0) - 1, top0 - 2, 'W')
            f.put(int(hx0) + sz, top0 - 1, 'N')
        for (sx, off) in ((x - 1, 0), (x + 16, 5)):
            f.rect(sx, top0 + ((k - 10) * 3 + off) % 12, 1, 2, 'T')
    if k >= 14:
        f.art(P.SWEAT, x + 17, y - 1)


STEAMER = ['NNNNNNNNNNNNNN', 'YYNYYNYYNYYNYY', 'YYNYYNYYNYYNYY', 'NNNNNNNNNNNNNN', 'YYNYYNYYNYYNYY',
           'NNNNNNNNNNNNNN']
LID = ['.....nn.....', '...NNNNNN...', '.NYYNYYNYYN.', 'NYYNYYNYYNYY', 'NNNNNNNNNNNN']
DUMPLING = ['..WW..', '.WgWW.', 'WgWWgW', 'GWWWWG']


def dumpling(f, t, n):
    k = t % 14
    x, y = 3, BY
    sx, sy = 23, 28
    table(f, 20, 34, 19)
    lift = [0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0][k]
    happy = 5 <= k <= 9
    info = clawd(f, x=x, y=y, view='q2r', ra=['side', 'mid', 'high'][lift],
                 eyes='happy' if happy else 'normal' if lift == 2 else 'normal')
    if lift == 2:
        for i, dx in enumerate((0, 4, 8)):
            f.art(DUMPLING, sx + dx, sy - 3)
    f.art(STEAMER, sx, sy)
    if lift == 0:
        f.art(LID, sx + 1, sy - 5)
    else:
        hx, hy = info['rh']
        f.art(LID, int(hx) - 1, int(hy) - 4)
    if lift == 2:
        s = min(k - 3, 4) if k <= 9 else 1
        for i in range(3):
            p = ((t / 5) + i / 3) % 1
            px = sx + 2 + i * 4 + int(math.sin(p * 6 + i) * 2)
            py = sy - 5 - int(p * (6 + s * 3))
            f.art(P.PUFF if i % 2 else ['.LL', 'LLL', 'LL.'], px, py)
    if 6 <= k <= 9:
        f.art(P.HEART, x + 15, y - 5 - (k - 6))


BOX = ['UUUUUUUUUW', 'URRRUUUUUW', 'UURRRUEUUW', 'UUUUUUUUUW', 'YYYYYYYYYG']
CARTON = ['GGGGGGGG.', 'GWWWWWWGG', 'GBBBWWWWG', 'GBBBWWWGG', 'GGGGGGGG.']


def cereal(f, t, n):
    k = t % 24
    x, y = 2, BY
    bx, by = 23, 29
    table(f, 20, 34, 19)
    if k < 8:
        lvl, milk = (k + 1) // 3, 0
    elif k < 14:
        lvl, milk = 3, min(3, (k - 7) // 2)
    elif k < 22:
        lvl = milk = max(0, 3 - (k - 14) // 2)
    else:
        lvl = milk = 0
    eat = 14 <= k < 22
    spoon_up = eat and k % 2 == 0
    info = clawd(f, x=x + (1 if eat else 0), y=y, view='q2r',
                 ra='high' if (not eat or spoon_up) else 'side',
                 eyes='happy' if eat and not spoon_up else 'closed' if spoon_up else 'normal' if k < 14 else 'normal')
    # bowl
    for j, (a, w) in enumerate(((0, 13), (0, 13), (1, 11), (2, 9), (3, 7))):
        f.rect(bx + a, by + j, w, 1, 'W'); f.put(bx + a, by + j, 'G'); f.put(bx + a + w - 1, by + j, 'G')
    f.rect(bx + 1, by + 2, 11, 1, 'B')
    if lvl or milk:
        top = by - max(lvl, milk) + 1
        for yy in range(top, by + 1):
            if milk and yy >= by - milk + 1:
                f.rect(bx + 1, yy, 11, 1, 'w')
            f.put(bx, yy, 'G'); f.put(bx + 12, yy, 'G')
        for i in range(lvl * 4):
            f.put(bx + 1 + (i * 5) % 11, top + (i * 3) % max(1, lvl), pick('FUZY', i))
    hx, hy = info['rh']
    hx, hy = int(hx), int(hy)
    if k < 8:  # cereal box tipped on its side, pouring from the right end
        f.art(BOX, hx - 3, hy - 5)
        for i in range(3):
            yy = hy - 2 + ((k * 2 + i * 3) % (by - hy + 1))
            f.put(hx + 7 + (i % 2), yy, pick('FUZ', i + k))
    elif k < 14:  # milk carton
        f.art(CARTON, hx - 3, hy - 5)
        if k < 13:
            f.rect(hx + 6, hy - 1, 1, by - hy + 1, 'W'); f.rect(hx + 7, hy - 1, 1, by - hy + 1, 'G')
    else:
        if spoon_up:  # spoonful raised to the front of the face
            f.rect(hx - 2, hy - 1, 3, 1, 'G'); f.rect(hx - 4, hy - 2, 2, 2, 'G'); f.put(hx - 4, hy - 3, 'U')
        else:
            f.line(hx, hy, hx + 4, by - 1, 'G'); f.rect(hx + 4, by - 1, 2, 1, 'G')


TOAST = ['.NN.', 'NYYN', 'NYYN', 'NNNN']


def toaster(f, tx, ty, popped, glow):
    f.rrect(tx, ty, 12, 8, 'g'); f.rrect(tx + 1, ty + 1, 10, 6, 'G'); f.rect(tx + 2, ty + 2, 1, 4, 'W')
    for sx in (tx + 2, tx + 7):
        f.rect(sx, ty, 4, 1, 'F' if glow else 'k')
    f.rect(tx + 12, ty + (2 if popped else 5), 2, 1, 'k')
    f.put(tx + 9, ty + 5, 'k')
    f.rect(tx + 1, ty + 8, 2, 1, 'k'); f.rect(tx + 9, ty + 8, 2, 1, 'k')


def toast(f, t, n):
    k = t % 14
    x, y = 2, BY
    tx, ty = 25, 25
    table(f, 22, 34, 17)
    dy = {7: 1, 8: -6, 9: -4}.get(k, 0)
    eyes = 'focus' if k < 6 else 'big' if k == 6 else 'big' if k == 8 else 'closed' if k == 9 else 'happy'
    info = clawd(f, x=x, y=y + dy, h=12 - (1 if k == 7 else 0), view='q2r',
                 legs=(1, 1, 1, 1) if k in (8, 9) else ((0, 0, 0, 1) if k < 6 and k % 2 else (0, 0, 0, 0)),
                 ra='up' if k in (8, 9) else 'side', la='up' if k in (8, 9) else 'side', eyes=eyes)
    w = 16
    # bread sticking out of the slots / flying
    t2 = {6: ty - 5, 7: ty - 10, 8: ty - 12, 9: ty - 9, 10: ty - 4, 11: ty - 4, 12: ty - 2}.get(k, ty - 1)
    if k < 6:
        f.rect(tx + 2, ty - 1, 4, 1, 'N'); f.rect(tx + 7, ty - 1, 4, 1, 'N')
    if k == 6:
        f.art(TOAST, tx + 2, ty - 5)
    if k == 7:
        f.art(TOAST, tx - 2, ty - 12)
    if k == 8:
        f.art(TOAST, x + w + 2, y + dy + 1)
    if k >= 6:
        f.art(TOAST, tx + 7, t2)
    toaster(f, tx, ty, 6 <= k <= 11, k < 6 and k % 2 == 0)
    if k >= 9:  # toast pressed to the front of the face, shrinking bite by bite
        cols = {9: 4, 10: 4, 11: 3, 12: 2, 13: 1}[k]
        f.art([r[:cols] for r in TOAST], x + w - 1, y + dy + 5)
        if k >= 11:
            crumbs(f, x + w + 1, y + 10, k - 11)
    if k == 6:
        f.text('POP', tx + 1, ty - 12, 'R')
    elif k < 6 and k % 2:
        f.text('TIK', tx + 1, ty - 7, 'g')


FRUIT = [['.E.', 'ZZZ', 'ZWZ', '.Z.'], ['U...', 'UU..', '.UUU'], ['.e.', 'eEe', 'EKE', '.e.']]


def blender(f, t, n):
    k = t % 18
    x, y = 3, BY
    jx = 26
    table(f, 22, 34, 17)
    blend = 6 <= k <= 11
    sip = 13 <= k <= 17
    shake = (1 if k % 2 else -1) if blend else 0
    eyes = 'squint' if blend else 'happy' if k == 12 else 'closed' if sip else 'normal'
    info = clawd(f, x=x + shake, y=y, view='q2r',
                 ra='out' if k == 5 else 'high' if k < 5 else 'side', eyes=eyes)
    # base
    f.rrect(jx - 1 + shake, 29, 11, 5, 'k'); f.rect(jx + shake, 30, 9, 1, 'g')
    f.rect(jx + 6 + shake, 31, 2, 2, 'R' if not blend or k % 2 else 'Z')
    # jar contents
    if k < 6:
        level = [0, 3, 3, 6, 6, 9][k]
    elif k <= 12:
        level = 9
    else:
        level = max(0, 9 - (k - 12) * 2)
    jl = jx + shake
    r = rng(k)
    for j in range(level):
        yy = 28 - j
        for i in range(1, 8):
            if blend:
                c = 'r' if r.random() < (k - 5) / 7 else r.choice('ZUEW')
            elif k <= 5:
                c = 'ZUE'[min(2, j // 3)] if (i + j) % 3 else 'W'
            else:
                c = 'r'
            f.put(jl + i, yy, c)
    if level and k >= 12:
        f.put(jl + 2, 28 - level + 1, 'W')
    # glass jar
    f.rect(jl, 17, 1, 12, 'L'); f.rect(jl + 8, 17, 1, 12, 'L')
    if not level:
        f.rect(jl + 1, 28, 7, 1, 'L')
    f.rect(jl + 2, 18, 1, 4, 'W')
    if 5 <= k <= 11:
        f.rect(jl - 1, 15, 11, 2, 'k'); f.rect(jl + 3, 14, 3, 1, 'k'); f.rect(jl, 15, 9, 1, 'g')
    if blend:
        f.text('VRRR', 25, 6 + (k % 2), 'g')
        for i in range(3):
            f.put(jl + 2 + (k + i * 2) % 5, 20 + i * 3, 'W')
    # fruit tossed in
    if k < 5 and k % 2 == 0:
        fx, fy = arc(x + 20, y + 3, jx + 3, 14, 6, 0.6)
        f.art(FRUIT[k // 2], fx, fy)
    if sip:
        f.line(x + 15, y + 7, jl + 4, 28 - max(level, 1), 'C')


FRIDGE_IN = {
    'milk': (['GGG', 'GWG', 'GBG', 'GWG', 'GGG'], 26, 9),
    'jelly': (['.ZZ.', 'ZrZZ', 'ZZZZ'], 31, 11),
    'cheese': (['...U', '.UUU', 'UYUU', 'UUUU'], 30, 18),
    'apple': (['.n.', 'RRR', 'RRR'], 26, 19),
    'veg': (['E.E.E', 'EeEeE', '.FFF.'], 27, 27),
}


def fridge(f, t, n):
    k = t % 16
    x, y = 5, BY
    fx, fy, fw, fh = 24, 5, 14, 31
    door = 0 if k < 2 or k >= 11 else 1 if k in (2, 10) else 2
    lean = 1 if 4 <= k <= 8 else 0
    # cabinet + interior
    f.rect(fx, fy, fw, fh, 'G')
    if door:
        f.rect(fx + 1, fy + 1, fw - 2, fh - 2, 'y')
        for sy in (14, 22, 30):
            f.rect(fx + 1, sy, fw - 2, 1, 'G')
        for name, (art, ax, ay) in FRIDGE_IN.items():
            if name == 'cheese' and k >= 9:
                continue
            f.art(art, ax, ay)
    if door == 0:
        f.rect(fx + 1, fy + 1, fw - 2, fh - 2, 'W'); f.rect(fx + 1, 13, fw - 2, 1, 'G')
        f.rect(fx + 2, 8, 1, 3, 'g'); f.rect(fx + 2, 16, 1, 5, 'g')
    elif door == 1:
        f.rect(fx + 7, fy, 7, fh, 'G'); f.rect(fx + 8, fy + 1, 5, fh - 2, 'W'); f.rect(fx + 8, 13, 5, 1, 'G')
        f.rect(fx + 9, 16, 1, 5, 'g')
    else:
        f.rect(fx + fw, fy, 2, fh, 'G'); f.rect(fx + fw, fy + 1, 1, fh - 2, 'W')
    f.rect(fx + 1, fy + fh, 2, 1, 'g'); f.rect(fx + fw - 3, fy + fh, 2, 1, 'g')
    if door == 2:
        for (lx, ly) in ((fx - 2, 12), (fx - 3, 20), (fx - 2, 28)):
            if (k + ly) % 2:
                f.rect(lx, ly, 2, 1, 'U')
    have = 9 <= k <= 14
    bite = max(0, k - 11)
    info = clawd(f, x=x + lean, y=y, view='q2r', ra='high' if have or k in (1, 2) else 'side',
                 eyes='big' if 3 <= k <= 8 else 'happy' if k >= 12 else 'normal' if k == 9 else 'normal', tilt=1 if 4 <= k <= 8 else 0)
    if have:
        hx, hy = info['rh']
        art = [r[:max(1, 4 - bite)] for r in FRIDGE_IN['cheese'][0]]
        f.art(art, int(hx) - 1, int(hy) - 4)
    if 5 <= k <= 8:
        P.sparkles(f, k, 4, [(32, 17), (28, 25)])
    if k >= 12:
        crumbs(f, x + 18, y + 10, k - 12, 'UY')


def microwave(f, t, n):
    k = t % 16
    x, y = 3, BY
    mx, my = 21, 17
    # counter
    f.rect(20, 28, 20, 1, 'W'); f.rect(20, 29, 20, 1, 'G')
    f.rect(21, 30, 18, 6, 'N'); f.rect(29, 30, 1, 6, 'n'); f.put(27, 32, 'U'); f.put(31, 32, 'U')
    running = k < 12
    f.rrect(mx, my, 18, 11, 'g'); f.rect(mx + 1, my + 1, 16, 9, 'G')
    f.rect(mx + 2, my + 2, 10, 7, 'y' if running else 'k')
    f.rect(mx + 2, my + 2, 10, 1, 'g')
    off = [0, 1, 2, 1, 0, -1, -2, -1][k % 8] if running else 0
    f.rect(mx + 3, my + 8, 8, 1, 'W' if running else 'g')
    f.art(['B..B', 'BBBB', '.BB.'], mx + 5 + off, my + 5)
    f.rect(mx + 13, my + 2, 4, 7, 'k')
    digit = str(max(0, 6 - k // 2)) if running else '0'
    f.text(digit, mx + 14, my + 3, 'E')
    for i in range(2):
        f.put(mx + 14 + i * 2, my + 9, 'k')
    ding = k == 12
    happy = k >= 12
    clawd(f, x=x, y=y - (3 if ding else 0), view='q2r',
          legs=(1, 1, 1, 1) if ding else ((0, 0, 0, 1) if k % 2 and running else (0, 0, 0, 0)),
          eyes='big' if ding else 'happy' if happy else 'focus' if k % 6 != 5 else 'blink',
          ra='up' if ding else 'side', la='up' if ding else 'side')
    if ding:
        f.text('DING', mx + 1, my - 8, 'R')
        f.art(['R.R', '.R.'], mx + 18, my - 4)
    if k >= 13:
        P.rising(f, ['L', 'L'], k - 13, 3, mx + 7, my - 2, count=2, height=5, jitter=3, seed=8)
        f.art(P.HEART, x + 13, y - 4 - (k - 13))


COOKIE = ['.NN.', 'NnNN', 'NNnN', '.NN.']


def cookie_jar(f, t, n):
    k = t % 24
    jx, jy = 25, 22
    # big glass jar on the floor
    for j in range(13):
        a = 1 if j in (0, 12) else 0
        f.put(jx + a, jy + j, 'L'); f.put(jx + 11 - a, jy + j, 'L')
    f.rect(jx + 2, jy + 12, 8, 1, 'L'); f.rect(jx + 2, jy + 2, 1, 3, 'W')
    for i, (cx, cy) in enumerate(((1, 8), (6, 8), (3, 3), (7, 2))):
        f.art(COOKIE, jx + cx, jy + cy, cmap={'N': 'Y', 'n': 'N'} if i % 2 else None)
    lid_up = k in (8, 9)
    f.rrect(jx - 1, jy - 2 - (3 if lid_up else 0), 14, 2, 'B')
    f.rect(jx + 5, jy - 3 - (3 if lid_up else 0), 2, 1, 'b')
    if k < 8:
        x = -16 + k * 3
        s = (k // 2) % 2
        clawd(f, x=x, y=BY - 1 - s, view='qr', legs=(0, 1, 0, 1) if s else (1, 0, 1, 0),
              eyes='blink', la='high', ra='high')
        return
    if k < 14:
        v = {11: 'ql', 12: 'front', 13: 'qr'}.get(k, 'qr')
        info = clawd(f, x=6, y=BY - 1, view=v, ra='high' if k < 11 else 'side',
                     la='high' if k >= 11 else 'side',
                     eyes='big' if k in (8, 9) else 'worried' if k >= 11 else 'normal')
        if k >= 10:
            hx, hy = info['rh'] if k == 10 else info['lh']
            f.art(COOKIE, int(hx) - 2, int(hy) - 3)
        if k in (8, 9):
            P.sparkles(f, k, 4, [(jx + 4, jy - 7), (jx + 9, jy + 2)])
        return
    j = k - 14
    x = 5 - j * 3
    s = (k // 2) % 2
    info = clawd(f, x=x, y=BY - 1 - s, view='ql', legs=(0, 1, 0, 1) if s else (1, 0, 1, 0),
                 eyes='happy', la='high', ra='side')
    hx, hy = info['lh']
    f.art([r[:4 - min(3, j // 3)] for r in COOKIE], int(hx) - 3, int(hy) - 3)
    if j % 3 == 1:
        crumbs(f, x + 2, BY + 8, j % 3)


def sweep(f, t, n):
    k = t % 16
    x, y = 4, BY
    s = int(round(3 * sin(t, 8)))
    L = Canvas()
    clawd(L, x=x, y=y, view='q2r', ra='mid', eyes='happy' if k % 8 < 4 else 'closed')
    f.blit(L.shear(s * 0.02, 36))
    hx, hy = 24, y + 4
    bx = 30 + s
    f.line(hx - 2, hy - 3, bx, 32, 'N')
    f.art(['.nnnn.', 'YYYYYY', 'YYYYYYY', 'Y.Y.Y.Y'], bx - 3, 32)
    # dust drifting toward the dustpan
    for i in range(5):
        p = (t / n + i / 5) % 1
        dx = 33 + int(p * 4)
        f.put(dx + (i % 2), 35 - (1 if i % 2 == 0 and p > 0.5 else 0), 'g' if i % 2 else 'n')
    if s > 0:
        P.dust(f, bx + 4, 36, ph(t, 4))
    f.art(['R....', 'RRRRR', 'RRRRR'], 35, 33); f.rect(39, 30, 1, 3, 'g')


def vacuum(f, t, n):
    k = t % 16
    x = 3 + int(round(3 * sin(t, n)))
    y = BY
    jit = k % 2
    info = clawd(f, x=x, y=y + jit, view='q2r', ra='high', eyes='focus' if k < 8 else 'happy', legs=wl(t))
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    vx = hx + 1
    f.line(hx - 1, hy - 1, vx + 2, 25, 'g')
    f.rect(vx + 1, 25, 4, 8, 'P'); f.rect(vx + 2, 26, 1, 5, 'p'); f.rect(vx + 1, 29, 4, 1, 'b')
    f.rect(vx, 33, 9, 2, 'k'); f.rect(vx + 1, 33, 7, 1, 'g'); f.put(vx + 1, 35, 'G'); f.put(vx + 6, 35, 'G')
    nose = vx + 9
    bun = 36
    if k < 8:
        d = bun - nose
        if d > 2:
            f.art(['.LL.', 'LKKL', '.LL.'], bun, 32)
        elif d > 0:
            f.art(['LL', 'KL'], bun - 1, 33)
        for i in range(2):
            f.rect(nose + 1 + (k + i) % 3, 33 + i, 2, 1, 'L')
        f.text('VRR', vx - 2, 15 + jit, 'g')
    else:
        bx = 43 - (k - 8)
        f.art(['.LL.', 'LKKL', '.LL.'] if k % 2 else ['LLL.', 'LKKL', '.LLL'], bx, 32)


def washer(f, t, n):
    k = t % 16
    shake = (1 if k % 2 else 0) if k >= 8 else 0
    wx, wy = 20 + shake, 10
    f.rect(wx, wy, 20, 26, 'G'); f.rect(wx + 1, wy + 1, 18, 24, 'W')
    f.rect(wx + 1, wy + 4, 18, 1, 'G')
    f.rect(wx + 3, wy + 1, 6, 2, 'g'); f.rect(wx + 14, wy + 1, 2, 2, 'k')
    f.put(wx + 11, wy + 2, 'E' if k % 2 else 'R')
    cx, cy = wx + 10, wy + 15
    f.disc(cx, cy, 8, 'g'); f.disc(cx, cy, 6.5, 'G'); f.disc(cx, cy, 5.5, 'S')
    wl_ = cy + int(round(sin(t, 8)))
    for yy in range(int(wl_), int(cy + 6)):
        for xx in range(int(cx - 6), int(cx + 6)):
            if (xx + .5 - cx) ** 2 + (yy + .5 - cy) ** 2 <= 5.5 ** 2:
                f.put(xx, yy, 'C')
    for i, art in enumerate((['RR', 'R.', 'RR'], ['UUU', '.U.'], ['ZZ', 'ZZ'])):
        a = 2 * math.pi * (t / 8 + i / 3)
        f.art(art, int(round(cx + 3 * math.cos(a))) - 1, int(round(cy + 3 * math.sin(a))) - 1)
    f.put(cx - 3, cy - 3, 'W'); f.put(cx - 2, cy - 4, 'W')
    a = 2 * math.pi * (t / 8)
    look, lookv = int(round(math.cos(a))), int(round(math.sin(a)))
    sway = int(round(sin(t, 8)))
    clawd(f, x=2 + sway, y=BY + 2, leg_h=1, eyes='normal', look=look, lookv=lookv, la='short', ra='short')


SHIRT = ['UUU.UUU', 'UUUUUUU', '.UUUUU.', '.UUYUU.', '.UUUUU.']
TOWEL = ['SBBBS', 'BBBBB', 'BBBBB', 'BBBBB', 'SBBBS', 'B.B.B']
SOCK = ['RR', 'RR', 'RW', 'RRR', '.RR']


def hang(f, art, x, y, k, gust):
    rows = parse(art)
    for j, row in enumerate(rows):
        off = int(round(math.sin(k * 1.3 + j * 0.7) * (j / 3) * (2 if gust else 0.6)))
        f.art([row], x + off, y + j)
    f.rect(x + 1, y - 1, 1, 2, 'N'); f.rect(x + len(rows[0]) - 2, y - 1, 1, 2, 'N')


def laundry(f, t, n):
    k = t % 16
    gust = 10 <= k <= 13
    f.rect(1, 4, 2, 32, 'N'); f.rect(37, 4, 2, 32, 'N')
    for xx in range(3, 37):
        f.put(xx, 6 + int(round(2 * math.sin(math.pi * (xx - 3) / 34))), 'g')
    hang(f, TOWEL, 5, 8, k, gust)
    hang(f, SOCK, 13, 9, k + 2, gust)
    f.art(['..UBZ....', 'NNNNNNNNN', 'NnNnNnNnN', 'NNNNNNNNN', '.NnNnNnN.'], 30, 31)
    if gust:  # wind lines pass behind Clawd
        for i in range(3):
            xx = (k * 6 + i * 13) % 44 - 4
            f.rect(xx, 12 + i * 6, 5, 1, 'L')
    pose = {0: ('low', 'normal'), 1: ('high', 'normal'), 2: ('high', 'normal'), 3: ('up', 'focus'),
            4: ('up', 'focus'), 5: ('up', 'focus')}.get(k, ('side', 'happy'))
    if gust:
        pose = ('side', 'big')
    if k >= 14:
        pose = ('side', 'sad')
    x, y = 13, BY
    info = clawd(f, x=x, y=y, ra=pose[0], la='up' if 3 <= k <= 5 else 'side', eyes=pose[1],
                 look=1 if gust or k >= 14 else 0)
    if k in (1, 2):
        hx, hy = info['rh']
        f.art(SHIRT, int(hx) - 2, int(hy) - 6)
    elif 3 <= k <= 5:
        f.art(SHIRT, 17, 13 - (5 - k) * 2)
    elif 6 <= k <= 10:
        hang(f, SHIRT, 17, 9, k, gust)
    elif k == 11:
        f.art(SHIRT, 24, 4)
    elif k == 12:
        f.art(SHIRT, 32, 0)
    if k >= 14:
        f.art(P.SWEAT, x + 17, y - 1)


def dishes(f, t, n):
    k = t % 16
    x, y = 3, 18
    rinse = 8 <= k <= 11
    sink = k >= 14 or k == 0
    eyes = 'focus' if k < 8 else 'normal' if rinse else 'happy'
    clawd(f, x=x, y=y, view='q2r', ra='high', eyes=eyes if k != 5 else 'blink')
    # faucet on the right
    f.rect(36, 19, 1, 10, 'g'); f.rect(31, 19, 6, 1, 'g'); f.rect(31, 20, 1, 1, 'g'); f.rect(35, 26, 3, 1, 'G')
    if rinse:
        f.rect(31, 21, 1, 7, 'C'); f.put(31, 21 + (k % 3) * 2, 'W')
    px, py = (26, 23) if not rinse else (31, 24)
    if sink:
        py = 27 if k == 0 else 30
    f.disc(px, py, 4.5, 'W'); f.ring(px, py, 4.5, 'G'); f.ring(px, py, 2.6, 'w')
    spots = [(-2, -2), (1, 1), (2, -2), (-2, 2)]
    left = 4 if k < 2 or sink else max(0, 4 - (k - 1) // 2) if k < 8 else 0
    for (dx, dy) in spots[:left]:
        f.rect(px + dx, py + dy, 2, 1, 'N')
    if 1 <= k < 8:
        a = 2 * math.pi * k / 4
        f.art(['UUU', 'YYY'], int(px + 2 * math.cos(a)) - 1, int(py + 2 * math.sin(a)) - 1)
        P.rising(f, ['.L.', 'L.L', '.L.'], t, 8, px, py - 5, count=3, height=10, jitter=5, seed=4)
    if 12 <= k <= 13:
        f.art(P.SPARK, px + 3, py - 6); f.put(px - 4, py - 4, 'W')
    # counter front
    f.rect(1, 28, 38, 1, 'g'); f.rect(1, 29, 38, 7, 'G')
    f.rect(1, 29, 1, 7, 'g'); f.rect(38, 29, 1, 7, 'g'); f.rect(20, 30, 1, 6, 'g')
    f.rect(18, 31, 1, 2, 'k'); f.rect(22, 31, 1, 2, 'k')
    if rinse and k % 2:
        f.put(27, 26, 'C'); f.put(35, 25, 'C')


def can(f, bx, by, pour):
    """Watering can, spout to the right; pour tips the spout down."""
    f.rect(bx, by, 6, 4, 'C'); f.rect(bx + 1, by + 1, 1, 2, 'S')
    for (dx, dy) in ((1, -1), (2, -2), (3, -2), (4, -1)):
        f.put(bx + dx, by + dy, 'C')
    if pour:
        f.line(bx + 6, by + 1, bx + 8, by + 3, 'C'); f.rect(bx + 8, by + 4, 2, 1, 'B')
    else:
        f.line(bx + 6, by + 2, bx + 8, by, 'C'); f.rect(bx + 8, by - 1, 2, 1, 'B')


def plant(f, bx, by, d, t):
    """Potted flower with droop d (0 = perky, 1 = wilted)."""
    H = 6
    sway = int(round(sin(t, 8))) if d < 0.2 else 0
    pts = []
    for i in range(H + 1):
        u = i / H
        pts.append((int(round(bx + d * u * u * 5 + sway * u)), int(round(by - i + d * u ** 3 * 6))))
    for (x, y) in pts:
        f.put(x, y, 'E')
    for i, side in ((2, -1), (4, 1)):
        x, y = pts[i]
        if d < 0.5:
            f.art(['EE.', '.EE'] if side < 0 else ['.EE', 'EE.'], x - 3 if side < 0 else x + 1, y - 2)
        else:
            f.art(['.EE', 'EE.'] if side < 0 else ['EE.', '.EE'], x - 3 if side < 0 else x + 1, y)
    x, y = pts[-1]
    if d < 0.5:
        f.art(['.Z.Z.', 'ZZZZZ', 'ZZUZZ', 'ZZZZZ', '.Z.Z.'], x - 2, y - 4)
    else:
        f.art(['Z.', 'ZZ', 'Z.'], x, y + 1)


def water_plant(f, t, n):
    k = t % 24
    x, y = 4, BY
    if k < 4:
        d = 1.0
    elif k < 8:
        d = 1.0 - (k - 4) / 4 * 0.4
    elif k < 12:
        d = 0.6 - (k - 7) * 0.15
    elif k < 18:
        d = 0.0
    else:
        d = (k - 17) / 6
    d = max(0.0, min(1.0, d))
    pour = 4 <= k <= 11
    happy = 11 <= k <= 17
    info = clawd(f, x=x, y=y, ra='up' if pour else 'side',
                 eyes='sad' if k < 4 else 'happy' if happy else 'worried' if k >= 20 else 'normal')
    # pot
    f.rect(25, 30, 10, 1, 'd'); f.rect(26, 31, 8, 4, 'F'); f.rect(27, 35, 6, 1, 'd')
    f.rect(26, 29, 8, 1, 'n')
    plant(f, 30, 28, d, t)
    hx, hy = info['rh']
    if pour:
        can(f, int(hx) - 2, int(hy) - 5, True)
        for i in range(3):
            yy = int(hy) + ((k * 3 + i * 4) % 10)
            f.rect(int(hx) + 7 + (i % 2), yy, 1, 2, 'B')
    else:
        can(f, int(hx) - 1, int(hy) - 1, False)
    if happy:
        P.sparkles(f, k, 4, [(24, 17), (36, 20), (31, 13)])
    if 12 <= k <= 15:
        f.art(P.HEART, x + 15, y - 4 - (k - 12))


BAG = ['..kk.kk..', '...kkk...', '.kkkkkkk.', 'kkgkkkkkk', 'kgkkkkkkk', 'kkkkkkkkk', '.kkkkkkk.']


def trash(f, t, n):
    k = t % 24
    bx = 28
    lid_open = 8 <= k <= 11
    # bin
    f.rect(bx, 24, 10, 11, 'E')
    for xx in range(bx + 1, bx + 10, 2):
        f.rect(xx, 25, 1, 9, 'e')
    f.rect(bx + 1, 35, 2, 1, 'k'); f.rect(bx + 7, 35, 2, 1, 'k')
    if lid_open:
        f.rect(bx + 10, 12, 2, 12, 'e'); f.rect(bx + 12, 17, 1, 2, 'e')
    else:
        f.rect(bx - 1, 22, 12, 2, 'e'); f.rect(bx + 3, 21, 4, 1, 'e')
        if k == 12:
            f.text('BANG', bx - 6, 14, 'g')
            P.dust(f, bx - 3, 24, 0.5); P.dust(f, bx + 11, 24, 0.5, flip=True)
    if k < 8:
        x = -16 + k * 3
        s = k % 2
        info = clawd(f, x=x, y=BY + s, view='q2r', legs=wl(k), la='up', ra='up', eyes='squint')
        f.art(BAG, x + 4, BY + s - 9)
        for i in range(2):
            yy = BY - 13 - ((k + i * 2) % 4)
            f.art(['E.', '.E', 'E.'], x + 6 + i * 3, yy)
        return
    if k < 15:
        toss = 9 <= k <= 11
        v = 'q2r' if k < 12 else 'front'
        clap = k in (12, 13, 14)
        info = clawd(f, x=9, y=BY, view=v, la='up' if k <= 9 else ('high' if clap and k % 2 else 'side'),
                     ra='up' if k <= 9 else ('high' if clap and k % 2 else 'side'),
                     eyes='squint' if k < 11 else 'happy')
        if k <= 8:
            f.art(BAG, 13, BY - 9)
        elif toss:
            px, py = arc(13, BY - 9, bx + 1, 18, 5, (k - 8) / 3)
            f.art(BAG, px, py)
        if clap and k % 2:
            f.art(['L.L', '.L.'], 19, BY - 3)
        if k == 14:
            P.sparkles(f, 0, 4, [(6, 18), (26, 17)])
        return
    j = k - 15
    x = 9 - j * 3
    info = clawd(f, x=x, y=BY + j % 2, view='q2l', legs=wl(k), eyes='happy')


IRON = ['..kkkk...', '..k..k...', 'gWWWWWWg.', 'gWWWWWWWg', 'ggggggggg']
WRINKLES = [(20, 27), (22, 28), (24, 26), (26, 28), (27, 27), (29, 26), (30, 28)]


def iron(f, t, n):
    k = t % 16
    if k < 8:
        x = k
    elif k < 12:
        x = 8 - (k - 8) * 2
    else:
        x = 0
    y = 20
    info = clawd(f, x=x, y=y, view='q2r', ra='low', eyes='focus' if k < 8 else 'happy' if k < 12 else 'normal')
    # board (top-down surface) + legs, below Clawd's face
    f.line(12, 33, 24, 35, 'g'); f.line(24, 33, 12, 35, 'g')
    f.rect(5, 29, 28, 4, 'P'); f.rect(6, 30, 26, 2, 'p')
    f.rect(33, 30, 2, 2, 'P'); f.rect(32, 30, 1, 2, 'p')
    for xx in range(8, 32, 4):
        f.put(xx, 31, 'P')
    flip = {12: 1, 13: 0, 14: 1}.get(k, 2)
    top = 30 + (2 - flip) // 2
    if flip:
        f.rect(17, top, 14, flip, 'B')
    if flip == 2:
        f.rect(18, 29, 3, 1, 'B'); f.rect(18, 32, 3, 1, 'B'); f.put(17, 30, 'S'); f.put(17, 31, 'S')
    hx = int(info['rh'][0])
    ix = hx - 3
    smooth = ix + 8 if k < 8 else 99
    if flip == 2:
        for wx in (20, 22, 24, 26, 27, 29):
            if wx >= smooth or k == 15:
                f.put(wx, 30 + (wx % 2), 'b')
    if k < 12:
        f.art(IRON, ix, 26)
        P.rising(f, ['L'], t, 4, ix + 6, 24, count=2, height=5, jitter=2, seed=3)
    else:
        f.art(IRON, ix + 2, 25)


def duster(f, t, n):
    k = t % 16
    x, y = 3, BY
    f.rect(22, 18, 18, 1, 'N'); f.rect(22, 19, 18, 1, 'n'); f.rect(24, 20, 1, 2, 'n'); f.rect(37, 20, 1, 2, 'n')
    f.art(['.B.', 'BBB', 'BSB', 'BBB', '.B.'], 28, 13)
    f.rect(32, 12, 2, 6, 'R'); f.rect(34, 13, 2, 5, 'E'); f.rect(36, 12, 2, 6, 'U'); f.rect(32, 13, 2, 1, 'W')
    if k < 2 or k >= 14:
        for (dx, dy) in ((27, 17), (31, 11), (35, 12), (38, 17), (30, 17)):
            f.put(dx, dy, 'L')
    shake = k in (9, 10, 11)
    eyes = 'normal'
    if k == 6:
        eyes = 'big'
    elif 7 <= k <= 8:
        eyes = 'squint'
    elif shake:
        eyes = 'x' if k == 9 else 'squint'
    elif k >= 12:
        eyes = 'happy'
    info = clawd(f, x=x + ((1 if k % 2 else -1) if shake else 0), y=y, view='q2r', ra='high', eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    s_ = [0, 2, 4, 6, 4, 2, 6, 3, 3, 3, 3, 3, 0, 0, 0, 0][k]
    tip = (hx + 4 + s_, hy - 9)
    f.line(hx - 1, hy - 1, tip[0], tip[1], 'N')
    f.art(['.ZrZ.', 'ZrZrZ', 'rZrZr', '.rZr.'] if k % 2 else ['.rZr.', 'rZrZr', 'ZrZrZ', '.ZrZ.'], tip[0] - 2, tip[1] - 3)
    if 1 <= k <= 5:
        for i in range(3):
            p = ((k - 1) / 5 + i / 3) % 1
            f.put(int(29 + p * 4 + i * 2), int(16 - p * 6), 'L')
    # a dust cloud rolls off the shelf and engulfs the space AROUND Clawd
    if k == 6:
        for (cx, cy, r) in ((30, 15, 3.5), (25, 17, 3)):
            f.disc(cx, cy, r, 'L')
    if 7 <= k <= 8:
        for (cx, cy, r) in ((x - 2, y + 2, 3), (x + 4, y - 3, 3.5), (x + 12, y - 4, 3.5), (x + 19, y + 1, 3),
                            (x - 1, y + 10, 2.5), (x + 19, y + 9, 2.5)):
            f.disc(cx, cy - (k - 7), r, 'L'); f.ring(cx, cy - (k - 7), r, 'G')
    if shake:
        r = rng(k)
        for i in range(10):
            a = r.uniform(0, 2 * math.pi)
            d = 11 + r.random() * 3 + (k - 9) * 2
            f.rect(int(x + 8 + math.cos(a) * d), int(y + 6 + math.sin(a) * d * 0.8), 1 + i % 2, 1, 'L')
        f.art(['L.L', '.L.', 'L.L'] if k % 2 else ['.L.', 'L.L', '.L.'], x - 5, y + 1)
    if 12 <= k <= 13:
        P.sparkles(f, k, 4, [(x - 2, y - 2), (x + 17, y - 4)])


HEART_FOG = [(1, 0), (2, 0), (4, 0), (5, 0), (0, 1), (3, 1), (6, 1), (0, 2), (6, 2), (1, 3), (5, 3),
             (2, 4), (4, 4), (3, 5)]


def window_wipe(f, t, n):
    k = t % 16
    x, y = 4, BY
    gx, gy = 22, 6
    f.rect(gx, gy, 17, 26, 'N'); f.rect(gx + 1, gy + 1, 15, 24, 'S')
    f.rect(gx + 8, gy + 1, 1, 24, 'N'); f.rect(gx + 1, gy + 12, 15, 1, 'N')
    f.rect(gx - 1, gy + 26, 19, 2, 'n')
    for i in range(3):
        f.put(gx + 3 + i, gy + 6 - i, 'W'); f.put(gx + 11 + i, gy + 17 - i, 'W')
    # fog patch at Clawd's breath height
    fx, fy = gx + 4, gy + 18
    r = 0
    if k < 2 or k >= 12:
        r = 3.6
    elif k < 8:
        r = 3.6 - (k - 1) * 0.6
    elif k in (10, 11):
        r = 1.8 if k == 10 else 3.6
    if r > 0.5:
        f.disc(fx, fy, r, 'w')
    if k < 2 or k >= 12:
        m = len(HEART_FOG) if k < 2 else min(len(HEART_FOG), (k - 11) * 4)
        for (dx, dy) in HEART_FOG[:m]:
            f.put(fx - 3 + dx, fy - 3 + dy, 'S')
    lean = 1 if k in (10, 11) else 0
    wiping = 2 <= k <= 7
    drawing = 12 <= k <= 14
    info = clawd(f, x=x + lean, y=y, view='q2r', ra='high' if (wiping or drawing) else 'side',
                 eyes='focus' if wiping else 'happy' if k in (8, 9) or k < 2 else 'normal')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if wiping:
        a = 2 * math.pi * k / 3
        cx, cy = int(fx + 2 * math.cos(a)) - 1, int(fy + 2 * math.sin(a)) - 1
        f.line(hx, hy, cx, cy + 1, 'O')
        f.art(['UUU', 'UYU', 'UUU'], cx - 1, cy - 1)
    if drawing:
        dx, dy = HEART_FOG[min(len(HEART_FOG) - 1, (k - 11) * 4 - 1)]
        f.line(hx, hy, fx - 3 + dx, fy - 3 + dy + 1, 'O')
    if k in (8, 9):
        f.art(P.SPARK, gx + 3, gy + 15); f.art(['.W.', 'WWW', '.W.'], gx + 12, gy + 4)
    if k in (10, 11):
        f.art(['L.', '.L', 'L.'], x + 18, y + 6)


DUCK = ['...UU.', '...UKF', 'UUUUU.', '.UUUU.']


def bubble_bath(f, t, n):
    k = t % 16
    x, y = 12, 12
    splash = k in (6, 7)
    clawd(f, x=x, y=y + (1 if k % 4 == 2 else 0), la='up' if splash else 'side', ra='up' if splash else 'side',
          eyes='happy' if k % 8 < 5 else 'closed')
    # tub
    f.rect(4, 25, 32, 1, 'G'); f.rect(4, 26, 32, 7, 'W'); f.rect(5, 33, 30, 1, 'G')
    f.rect(4, 26, 1, 7, 'G'); f.rect(35, 26, 1, 7, 'G'); f.rect(5, 25, 30, 1, 'W'); f.put(4, 25, 'G')
    f.rect(6, 34, 2, 2, 'U'); f.rect(32, 34, 2, 2, 'U')
    f.rect(8, 28, 24, 1, 'w')
    # foam heaped along the rim (below Clawd's face)
    for i, (bx, r) in enumerate(((7, 2.6), (11, 3.2), (16, 2.4), (21, 2.6), (25, 2.6), (29, 3.2), (33, 2.4))):
        bob = (k // 2 + i) % 2
        f.disc(bx, 26 - bob, r, 'W'); f.ring(bx, 26 - bob, r, 'L')
    dx = int(round(3 * sin(t, n)))
    f.art(DUCK, 31 + dx, 20 + (k % 2))
    r = rng(2)
    for i, bx in enumerate((5, 9, 34)):
        p = (t / n * 2 + i / 3) % 1
        P.bubble_ring(f, bx + r.randint(0, 2), 22 - p * 20, 1.2 + (i % 2) * 0.5)
    if splash:
        for (sx, sy) in ((7, 18), (33, 15), (9, 13), (31, 11)):
            f.put(sx + (k % 2), sy - (k - 6) * 2, 'C')
    if k in (10, 11, 12):
        P.notes(f, {'head': (20, y)}, t, n, c='B', count=1)


def brush_teeth(f, t, n):
    """Sleepy scrubbing: the brush works at the front of the face, foam bubbles up around it."""
    k = t % 12
    x, y = 5, BY
    bob = 1 if k % 6 >= 3 else 0
    clawd(f, x=x, y=y + bob, h=12 - bob, view='q2r', ra='mid', eyes='blink' if k < 9 else 'closed')
    fe = x + 16
    by = y + 5 + bob
    dx = [0, 1, 2, 1][k % 4]
    # toothbrush: bristle head against the front edge, handle out to the near hand
    f.rect(fe + dx, by - 2, 2, 4, 'W'); f.rect(fe + dx, by - 2, 2, 1, 'G'); f.rect(fe + dx, by + 1, 2, 1, 'G')
    f.rect(fe + 2 + dx, by, 9 - dx, 1, 'C'); f.rect(fe + 4 + dx, by - 1, 6 - dx, 1, 'S')
    # foam builds up around the brush head
    foam = min(4, k // 2 + 1) if k < 10 else 2
    for i, (fx, fy) in enumerate(((fe + 2, by - 4), (fe - 1 + 3, by + 2), (fe + 4, by - 3), (fe + 3, by + 3))[:foam]):
        f.art(['.W.', 'WLW'] if (i + k) % 2 else ['WW', 'LW'], fx + dx, fy)
    for i in range(2):
        p = (t / n + i / 2) % 1
        P.bubble_ring(f, fe + 3 + i * 5, by - 5 - p * 14, 1.2)


def bed_front(f, top=26, color='B', pat='S'):
    f.rrect(5, 14, 30, 22, 'N'); f.rect(6, 15, 28, 1, 'n'); f.rect(5, 18, 30, 1, 'n')
    f.rrect(9, 20, 22, 6, 'W'); f.rect(9, 25, 22, 1, 'G'); f.put(9, 21, 'G'); f.put(30, 21, 'G')


def bed_sleep(f, t, n):
    k = t % 16
    bed_front(f)
    breath = 1 if (k // 2) % 2 else 0
    turned = 8 <= k <= 11
    clawd(f, x=12, y=18 - breath, eyes='closed', view='ql' if turned else 'front', leg_h=0)
    top = 27 - breath
    f.rect(6, top, 28, 35 - top, 'B'); f.rect(6, top, 28, 1, 'W'); f.rect(6, top + 1, 28, 1, 'G')
    for (sx, sy) in ((9, 3), (16, 5), (23, 3), (30, 5), (12, 7), (27, 7)):
        if top + sy < 35:
            f.art(['.S.', 'SWS', '.S.'] if (sx + k // 4) % 2 else ['S'], sx - 1, top + sy - 1)
    f.rect(5, 35, 2, 1, 'n'); f.rect(33, 35, 2, 1, 'n')
    P.zzz(f, {'head': (20, 17)}, t, n, c='B')


def alarm(f, t, n):
    k = t % 16
    ringing = k < 6 or k >= 14
    smack = k in (6, 7)
    # nightstand + clock
    f.rect(26, 28, 13, 8, 'N'); f.rect(26, 28, 13, 1, 'n'); f.rect(28, 31, 9, 1, 'n'); f.put(32, 33, 'U')
    sh = (1 if k % 2 else -1) if ringing else 0
    cx, cy = 32 + sh, 22
    if k == 7:
        f.art(['.UU..UU.', 'RRRRRRRR', 'RWWWWWWR', 'RRRRRRRR', '.k....k.'], cx - 4, cy + 1)
        f.art(['U.U', '.U.', 'U.U'], cx - 9, cy - 4); f.art(['U.U', '.U.', 'U.U'], cx + 6, cy - 3)
    else:
        f.art(['UU', 'UU'], cx - 4, cy - 5 + (1 if sh > 0 else 0)); f.art(['UU', 'UU'], cx + 2, cy - 5 + (1 if sh < 0 else 0))
        f.rect(cx - 1, cy - 5, 2, 1, 'k')
        f.disc(cx, cy, 4.5, 'R'); f.disc(cx, cy, 3.2, 'W')
        f.rect(cx - 1, cy - 2, 1, 3, 'K'); f.rect(cx - 1, cy, 3, 1, 'K')
        f.put(cx - 3, cy + 4, 'k'); f.put(cx + 2, cy + 4, 'k')
    if ringing:
        for (dx, dy, art) in ((-8, -4, ['K.', '.K', 'K.']), (6, -5, ['.K', 'K.', '.K']), (-7, 1, ['KK']), (6, 1, ['KK'])):
            if (k + dx) % 2 == 0:
                f.art(art, cx + dx, cy + dy, cmap={'K': 'R'})
        if k % 2 == 0:
            f.text('RING', 23, 9, 'R')
    # bed: Clawd tucked in under the blanket, face out
    f.rect(0, 30, 25, 4, 'W'); f.rect(0, 33, 25, 1, 'G'); f.rect(1, 34, 2, 2, 'N'); f.rect(21, 34, 2, 2, 'N')
    f.rrect(0, 17, 9, 6, 'W'); f.rect(0, 22, 9, 1, 'G')
    eyes = 'squint' if ringing and k < 6 else 'closed'
    if k == 5:
        eyes = 'angry'
    if k >= 14:
        eyes = 'squint'
    clawd(f, x=3, y=15, eyes=eyes, leg_h=0, la='none', ra='none')
    bump = 1 if ringing and k % 2 else 0
    f.rect(0, 25 - bump, 25, 7, 'P'); f.rect(0, 25 - bump, 25, 1, 'p')
    for xx in range(2, 24, 5):
        f.put(xx, 28, 'p'); f.put(xx + 2, 30, 'p')
    if k == 5 or smack:
        ax = 19
        reach = 27 if k == 5 else cx - 3
        f.rect(ax, 22 if k == 5 else 20, reach - ax, 2, 'O')
        f.rect(reach - 1, 20 if k == 6 else 21, 4, 3, 'O')
    if k == 6:
        f.text('BONK', 22, 11, 'R')
    if 8 <= k <= 13:
        P.zzz(f, {'head': (8, 13)}, k - 8, 6, c='B')


def shower(f, t, n):
    k = t % 16
    f.rect(1, 2, 38, 1, 'g')
    for yy in range(3, 36):
        f.rect(2, yy, 7 - (1 if (yy // 4) % 2 else 0), 1, 'P')
        f.put(3 + ((yy // 4) % 2), yy, 'p')
    for xx in (2, 5, 8):
        f.put(xx, 3, 'G')
    f.rect(31, 2, 1, 5, 'g'); f.rect(25, 6, 7, 1, 'g'); f.rect(21, 7, 7, 2, 'G'); f.rect(21, 9, 7, 1, 'g')
    # water streaks fall behind Clawd
    r = rng(4)
    for i in range(9):
        xx = r.randint(19, 30)
        off = r.randint(0, 9)
        for s_ in range(3):
            yy = 11 + (k * 3 + off + s_ * 8) % 24
            if 11 <= yy < 35:
                f.rect(xx, yy, 1, 2, 'C')
    sway = int(round(2 * sin(t, 8)))
    L = Canvas()
    scrub = (k // 2) % 2
    clawd(L, x=13, y=BY, eyes='closed', la='up' if scrub else 'side', ra='side' if scrub else 'up')
    # shampoo lather piled on top of the head
    for (dx, r_) in ((3, 2.0), (7, 2.6), (11, 2.2), (14, 1.6)):
        L.disc(13 + dx, BY - 2.2, r_, 'W'); L.ring(13 + dx, BY - 2.2, r_, 'L')
    f.blit(L.shear(sway * 0.03, 36))
    for (sx, d) in ((11, -1), (29, 1)):
        f.put(sx + d * (k % 3), 34 - (k % 2), 'C')
    P.notes(f, {'head': (20, BY - 5)}, t, n, c='B', count=2)


DRYER = ['.PPPPP', 'kPPPPPP', 'kPPPPPP', '.PPPPP.', '...PP..', '...PP..', '...PP..']


def hair_dryer(f, t, n):
    k = t % 12
    x, y = BX - 2, BY
    L = Canvas()
    clawd(L, x=x, y=y, ra='high', eyes='closed' if k % 6 < 4 else 'happy')
    f.blit(L.shear(-0.07 if k % 2 else -0.03, 36))
    hx, hy = x + 20, y + 2
    f.art(DRYER, hx - 4, hy - 8)
    f.put(hx - 4, hy - 7, 'g')
    # warm air streams over the top of the head
    for i in range(4):
        p = ((t / 4) + i / 4) % 1
        lx = int(hx - 6 - p * 16)
        f.rect(lx, y - 8 + i - int(p * 2), 3, 1, 'L')
    for i in range(3):
        p = ((t / 6) + i / 3) % 1
        f.put(int(x - 4 - p * 6), int(y + 2 + i * 3 - p * 3), 'B')


def easel(f, t, n):
    k = t % 24
    x, y = 3, BY
    # easel frame
    f.line(31, 7, 25, 35, 'N'); f.line(31, 7, 37, 35, 'N'); f.line(31, 7, 31, 35, 'n')
    lift = {20: -9, 21: -24}.get(k, 0)
    cx, cy = 24, 10
    stage = 0 if k >= 22 else min(14, k)

    def canvas(dy, st):
        f.rect(cx, cy + dy, 14, 15, 'G'); f.rect(cx + 1, cy + 1 + dy, 12, 13, 'W')
        if st >= 1:
            rows = min(6, st * 2)
            f.rect(cx + 1, cy + 1 + dy, 12, rows, 'S')
        if st >= 4:
            f.disc(cx + 10, cy + 4 + dy, 2.2, 'U')
        if st >= 6:
            hill = min(3, st - 5)
            for i in range(12):
                hgt = 3 + int(round(1.5 * math.sin(i / 3.5))) if hill >= 3 else hill
                f.rect(cx + 1 + i, cy + 14 - hgt + dy, 1, hgt, 'E')
        if st >= 9:
            f.rect(cx + 3, cy + 8 + dy, 1, 3, 'N'); f.disc(cx + 3.5, cy + 7 + dy, 2, 'e')
        if st >= 11:
            f.rect(cx + 7, cy + 9 + dy, 4, 3, 'O'); f.put(cx + 8, cy + 10 + dy, 'K'); f.put(cx + 10, cy + 10 + dy, 'K')
            f.put(cx + 7, cy + 12 + dy, 'O'); f.put(cx + 10, cy + 12 + dy, 'O')
        if st >= 13:
            f.rect(cx + 10, cy + 13 + dy, 2, 1, 'R')
    canvas(0, 0 if k >= 20 else stage)
    if 20 <= k <= 21:
        canvas(lift, 14)
    f.rect(cx - 1, 25, 16, 1, 'N')
    admire = 14 <= k <= 19
    info = clawd(f, x=x - (1 if admire else 0), y=y, view='q2r', ra='side' if admire else 'high',
                 eyes='happy' if admire else 'focus' if k < 14 else 'normal')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    paint = 'S' if k < 4 else 'U' if k < 6 else 'E' if k < 9 else 'e' if k < 11 else 'O' if k < 13 else 'R'
    targets = {0: (27, 12), 1: (33, 13), 2: (28, 15), 3: (34, 16), 4: (33, 14), 5: (35, 13),
               6: (27, 22), 7: (31, 21), 8: (35, 22), 9: (27, 17), 10: (28, 16), 11: (32, 20), 12: (34, 20),
               13: (34, 23)}
    if k < 14:
        tx, ty = targets[k]
        if k % 2:
            ty += 1
        f.line(hx - 1, hy, tx, ty, 'N'); f.rect(tx, ty, 1, 1, paint)
        f.put(tx + 1, ty, 'n')
    else:
        f.line(hx - 1, hy - 1, hx + 2, hy - 6, 'N'); f.put(hx + 2, hy - 7, 'R')
    if admire:
        P.sparkles(f, k, 4, [(22, 8), (39, 14), (30, 4)])
    # palette in the far hand
    f.art(['.WWW.', 'WRUBW', 'WWEWW', '.WW..'], x - 7, y + 7)
    f.rect(x - 7, y + 7, 1, 1, 'G')


CAMERA = ['..gg......', 'gggggggggg', 'gkkkkkkyyg', 'gkkGGGkkkg', 'gkGSSSGkkg', 'gkGSKSGkkg',
          'gkkGGGkkkg', 'gggggggggg']


def photo(f, t, n):
    """Snaps a picture (flash!), the polaroid pops out, gets shaken until it develops."""
    k = t % 16
    x, y = 4, BY
    fe = x + 16
    holding_cam = k <= 8
    eyes = 'focus' if k < 3 else 'closed' if k == 3 else 'big' if k <= 8 else 'happy' if k >= 13 else 'normal'
    info = clawd(f, x=x, y=y, view='q2r', ra='high', eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if holding_cam:
        jit = 1 if k in (1, 2) else 0
        f.art(CAMERA_SIDE, fe + 1 + jit, y + 1)
    if k == 3:
        cx, cy = fe + 12, y + 4
        f.art(['...W...', '.W.W.W.', '..WWW..', 'WWWWWWW', '..WWW..', '.W.W.W.', '...W...'], cx - 3, cy - 3)
        for (dx, dy) in ((8, 0), (6, -6), (6, 6), (0, -8)):
            f.line(cx + dx // 2, cy + dy // 2, cx + dx, cy + dy, 'U')
    if k == 4:
        f.art(P.SPARK, fe + 10, y + 2)
    # the polaroid slides out of the top of the camera
    if 5 <= k <= 8:
        h = (k - 4) * 2
        f.rect(fe + 2, y + 1 - h, 6, h, 'W'); f.rect(fe + 2, y + 1 - h, 1, h, 'G'); f.rect(fe + 7, y + 1 - h, 1, h, 'G')
        f.rect(fe + 2, y + 1 - h, 6, 1, 'G')
        if h > 2:
            f.rect(fe + 3, y + 2 - h, 4, min(h - 2, 4), 'g')
    if k >= 9:
        sh = (1 if k % 2 else -1) if k <= 12 else 0
        px, py = hx - 3 + sh, hy - 10
        f.rect(px, py, 7, 8, 'W'); f.box(px, py, 7, 8, 'G')
        dev = k - 9
        if dev == 0:
            f.rect(px + 1, py + 1, 5, 5, 'k')
        elif dev == 1:
            f.rect(px + 1, py + 1, 5, 5, 'g')
        else:
            f.rect(px + 1, py + 1, 5, 5, 'S'); f.rect(px + 2, py + 3, 3, 3, 'O')
            f.put(px + 2, py + 4, 'K'); f.put(px + 4, py + 4, 'K')
        if k <= 12:
            f.art(['L', '.', 'L'], px - 2 if sh < 0 else px + 8, py + 2)
        if k >= 13:
            f.art(P.HEART, px + 2, py - 5 - (k - 13))


def knit(f, t, n):
    k = t % 16
    x, y = BX, BY - 4
    f.rect(x + 1, 30, 14, 2, 'N'); f.rect(x + 1, 31, 14, 1, 'n'); f.rect(x + 2, 32, 2, 4, 'n'); f.rect(x + 12, 32, 2, 4, 'n')
    yb = y + (1 if k % 4 == 2 else 0)
    clawd(f, x=x, y=yb, leg_h=1, la='low', ra='low', eyes='focus' if k % 8 < 6 else 'happy')
    cross = k % 2
    cx, cy = x + 8, yb + 11
    # scarf: hangs from the needles, pools on the floor to the left (stripes scroll = it grows)
    path = [(cx - 2, yy) for yy in range(cy, 34)] + [(xx, 34) for xx in range(cx - 3, 0, -1)]
    for s_, (px, py) in enumerate(path):
        c = 'R' if ((s_ - t) // 2) % 2 == 0 else 'U'
        f.rect(px, py, 4 if py < 34 else 1, 1 if py < 34 else 2, c)
    # needles cross at the bottom of the body, well below the face
    f.line(x - 2, yb + 11, cx + 4 + cross, yb + 9, 'G'); f.line(x + 17, yb + 11, cx - 5 - cross, yb + 9, 'G')
    f.put(cx + 4 + cross, yb + 9, 'W'); f.put(cx - 5 - cross, yb + 9, 'W')
    bx, by = 33, 31
    f.disc(bx, by, 3.5, 'P')
    a = 2 * math.pi * t / 8
    for i in range(3):
        f.put(bx + math.cos(a + i * 2.1) * 2, by + math.sin(a + i * 2.1) * 2, 'p')
    f.line(bx - 3, by - 2, cx + 1, cy, 'P')


FISH = ['..CCC...', '.CCCCC.C', 'CKCCCCCC', '.CCCCC.C', '..CCC...']


def fishing(f, t, n):
    k = t % 20
    # water and dock
    for xx in range(0, 40):
        f.rect(xx, 32, 1, 8, 'B')
        if (xx + k) % 6 == 0:
            f.put(xx, 32, 'S')
    f.rect(0, 29, 17, 2, 'N')
    for xx in (3, 8, 13):
        f.put(xx, 29, 'n')
    f.rect(2, 31, 1, 9, 'n'); f.rect(13, 31, 1, 9, 'n')
    x, y = 2, 17
    bite = k in (8, 9)
    caught = 13 <= k <= 15
    eyes = 'normal' if k < 8 else 'big' if bite else 'focus' if k < 13 else 'happy' if caught else 'normal'
    info = clawd(f, x=x, y=y + (1 if k % 8 >= 4 and k < 8 else 0), view='q2r', ra='high', leg_h=0,
                 eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    tip = (34, 8)
    if k == 9:
        tip = (33, 12)
    elif 10 <= k <= 12:
        tip = (31, 3)
    elif caught:
        tip = (29, 5)
    f.line(hx - 1, hy + 1, tip[0], tip[1], 'N')
    bob = (31, 30 + (1 if k % 4 >= 2 else 0))
    if k < 8:
        f.line(tip[0], tip[1], bob[0] + 1, bob[1], 'g')
        f.art(['.R.', 'RRR', 'WWW'], bob[0], bob[1])
        if k % 4 == 3:
            f.put(bob[0] - 2, 32, 'W'); f.put(bob[0] + 4, 32, 'W')
    elif k == 8:
        f.line(tip[0], tip[1], bob[0] + 1, 31, 'g'); f.art(['.R.'], bob[0], 32)
        f.art(['W...W', '.W.W.'], bob[0] - 1, 30)
    elif k == 9:
        f.line(tip[0], tip[1], bob[0] + 1, 33, 'g')
        f.art(['W.W.W'], bob[0] - 1, 31)
    elif k <= 12:
        fx, fy = arc(31, 31, 28, 9, 8, (k - 9) / 3)
        f.line(tip[0], tip[1], fx + 4, fy, 'g')
        f.art(FISH, fx, fy)
        if k == 10:
            f.art(['W.W.W', '.W.W.'], 29, 30)
    elif caught:
        f.line(tip[0], tip[1], tip[0], tip[1] + 3, 'g')
        f.art(FISH if k % 2 else [r[::-1] for r in FISH], tip[0] - 4, tip[1] + 3)
        P.sparkles(f, k, 4, [(24, 4), (37, 12)])
    elif k <= 17:
        fx, fy = arc(25, 9, 36, 31, 6, (k - 15) / 2)
        f.line(tip[0], tip[1], tip[0], tip[1] + 2, 'g')
        if k < 17:
            f.art(FISH, fx, fy)
        else:
            f.art(['W.W.W', '.WWW.'], 34, 30)
    else:
        bx, by = arc(tip[0], tip[1], 31, 30, 3, (k - 17) / 3)
        f.line(tip[0], tip[1], bx + 1, by, 'g')
        f.art(['.R.', 'RRR', 'WWW'], bx, by)
    if bite:
        f.art(P.EXCL, x + 8, y - 8, cmap={'K': 'R'})


# =========================================================================== HOBBIES
PAD = ['.kkkkkk.', 'kgkkkkRk', 'kggkkBkk', 'kkkkkkkk', 'kk....kk']


def video_game(f, t, n):
    k = t % 12
    # cabinet + TV
    f.rect(23, 29, 17, 7, 'N'); f.rect(23, 29, 17, 1, 'n'); f.rect(31, 31, 1, 4, 'n')
    f.rect(24, 15, 15, 13, 'g'); f.rect(25, 16, 13, 11, 'k'); f.rect(26, 17, 11, 9, 'b')
    f.rect(30, 28, 3, 1, 'g')
    # the tiny game on screen
    f.rect(26, 25, 11, 1, 'E')
    obs = [37 - (t % 12), 37 - ((t + 6) % 12)]
    for ox in obs:
        if 26 <= ox <= 35:
            f.rect(ox, 23, 1, 2, 'R')
    d = min(abs(ox - 28) for ox in obs)
    jump = {0: 3, 1: 2, 2: 1}.get(d, 0)
    f.rect(28, 23 - jump, 2, 2, 'O'); f.put(29, 23 - jump, 'K')
    if k % 4 < 2:
        f.put(33, 19, 'U')
    # player
    x, y = 2, BY + 2
    lean = 0.05 * jump
    L = Canvas()
    info = clawd(L, x=x, y=y - (1 if jump >= 2 else 0), leg_h=1, view='q2r', ra='mid',
                 eyes='focus' if jump < 2 else 'big', tilt=1 if jump >= 2 else 0)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    L.art(PAD, hx - 3, hy - 2)
    if jump == 3:
        L.put(hx + 2, hy - 1, 'U')
    f.blit(L.shear(-lean, 36) if lean else L)
    if jump == 3:
        f.art(['.W.', 'W.W'], hx + 2, hy - 6)


def piano(f, t, n):
    k = t % 12
    x, y = BX, BY - 3
    sway = [0, 0, 1, 1, 0, 0, -1, -1, 0, 0, 1, 1][k]
    info = clawd(f, x=x + sway, y=y, la='none', ra='none', eyes='closed' if k % 6 < 4 else 'happy')
    # keyboard
    kx0, ky = 3, 28
    f.rect(kx0 - 1, ky - 1, 37, 1, 'n')
    f.rect(kx0, ky, 35, 5, 'W')
    lhand = [6, 9, 6, 9, 6, 9, 6, 9, 6, 9, 6, 9][k]
    rhand = [24, 27, 30, 33, 30, 27, 24, 27, 30, 33, 30, 27][k]
    down_l, down_r = (k % 2 == 0), (k % 2 == 1)
    for i in range(12):
        kx = kx0 + i * 3
        pressed = (down_l and kx <= lhand < kx + 3) or (down_r and kx <= rhand < kx + 3)
        if pressed:
            f.rect(kx, ky + 1, 2, 4, 'G')
        f.rect(kx + 2, ky, 1, 5, 'G')
    for i in (0, 1, 3, 4, 5, 7, 8, 10):
        f.rect(kx0 + i * 3 + 2, ky, 2, 3, 'K')
    f.rect(kx0 - 1, ky + 5, 37, 2, 'n'); f.rect(kx0 - 1, ky + 5, 37, 1, 'N')
    f.rect(kx0 + 1, ky + 7, 2, 1, 'n'); f.rect(kx0 + 32, ky + 7, 2, 1, 'n')
    # arms reaching down to the keys
    bx = x + sway
    for hx, down, side in ((lhand, down_l, -1), (rhand, down_r, 1)):
        top = y + 6
        hy = ky - 2 + (1 if down else 0)
        sx = bx if side < 0 else bx + 16
        if side < 0:
            f.rect(min(hx, sx - 2), top, abs(sx - hx) + 1, 2, 'O')
        else:
            f.rect(sx, top, max(2, hx - sx + 2), 2, 'O')
        f.rect(hx, top, 2, hy - top + 1, 'O')
    P.notes(f, info, t, n, c='P', count=2)


def drums(f, t, n):
    k = t % 8
    x, y = BX, 16
    hitL = k in (0, 2, 5, 6)
    hitR = k in (1, 3, 5, 7)
    crash = k == 5
    kick = k % 2 == 0
    info = clawd(f, x=x, y=y + (1 if kick else 0), la='high' if not hitL else 'low', ra='high' if not hitR else 'low',
                 eyes='closed' if crash else 'angry' if k % 4 == 1 else 'focus')
    lh, rh = info['lh'], info['rh']
    f.rect(2, 29, 1, 7, 'g'); f.rect(0, 35, 5, 1, 'g')
    f.rect(1, 26, 9, 3, 'R'); f.rect(1, 25, 9, 1, 'W'); f.put(0, 25, 'G'); f.put(10, 25, 'G')
    f.rect(1, 27, 9, 1, 'U')
    tipL = (6, 24) if hitL else (3, 12)
    f.line(int(lh[0]) + 1, int(lh[1]), tipL[0], tipL[1], 'N')
    f.rect(35, 18, 1, 18, 'g'); f.rect(33, 35, 5, 1, 'g')
    tilt = 1 if hitR else 0
    f.rect(30, 17 - tilt, 5, 1, 'U'); f.rect(35, 17, 5, 1, 'U'); f.rect(31, 18 - tilt, 3, 1, 'Y'); f.put(35, 16, 'Y')
    tipR = (32, 16) if hitR else (37, 8)
    f.line(int(rh[0]) - 1, int(rh[1]), tipR[0], tipR[1], 'N')
    # bass drum, its rim just below Clawd's face
    sh = 1 if kick else 0
    f.disc(20, 31 + sh, 6, 'W'); f.ring(20, 31 + sh, 6, 'R', 1.5); f.ring(20, 31 + sh, 3, 'G')
    f.rect(17, 31 + sh, 6, 1, 'R')
    if hitL:
        f.art(['K.K', '.K.'] if k % 4 == 0 else ['.K.', 'K.K'], 4, 20)
    if crash:
        f.text('TSS', 29, 5, 'Y')
        f.art(['U.U', '.U.', 'U.U'], 37, 12)
    elif hitR:
        f.art(['U.', '.U'], 36, 13)


def violin(f, t, n):
    k = t % 12
    x, y = 15, BY
    sway = int(round(sin(t, 12)))
    L = Canvas()
    clawd(L, x=x, y=y, la='high', ra='low', eyes='closed' if k % 6 < 4 else 'happy')
    # fiddle held out at the left shoulder, beside (not over) the body
    vx, vy = x - 10, y + 4
    L.line(vx + 2, vy, vx - 2, vy - 6, 'n'); L.rect(vx - 3, vy - 8, 2, 2, 'n')
    L.art(['.NNN.', 'NNnNN', '.NNN.', 'NNnNN', 'NNNNN', '.NNN.'], vx, vy)
    L.rect(vx + 2, vy + 1, 1, 4, 'n')
    # bow saws back and forth along the belly line, below the face
    s = int(round(4 * sin(t, 6)))
    by = y + 9
    L.line(vx - 2 + s, by, x + 22 + s, by, 'g'); L.line(vx - 2 + s, by + 1, x + 22 + s, by + 1, 'w')
    f.blit(L.shear(sway * 0.04, 36))
    P.notes(f, {'head': (22, y)}, t, n, c='N', count=2)


def karaoke(f, t, n):
    k = t % 16
    f.rect(2, 1, 36, 11, 'g'); f.rect(3, 2, 34, 9, 'b')
    sung = k // 4
    for i, wd in enumerate(['LA', 'LA', 'LA']):
        f.text(wd, 7 + i * 10, 5, 'U' if i < sung or (i == sung and k % 4 >= 2) else 'W')
    if k < 12:
        f.rect(8 + min(2, k // 4) * 10, 3 if k % 2 else 2, 2, 1, 'Z')
    for i, c in enumerate('PCZU'):
        sx = int(20 + 15 * math.sin(2 * math.pi * (t / n) + i * 1.6))
        f.rect(sx - 2, 35, 5, 1, c)
    x, y = 7, BY
    hop = 1 if k % 4 == 1 else 0
    info = clawd(f, x=x, y=y - hop, view='q2r', eyes='closed', ra='mid',
                 la='up' if k >= 12 and k % 2 else 'side')
    fe = x + 16
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    # mic held up in front of the face
    my = y - hop + 2
    f.art(['gGg', 'GGG', 'gGg'], fe + 1, my)
    f.line(fe + 2, my + 3, hx, hy, 'g')
    P.notes(f, {'head': (fe + 4, y - 3)}, t, n, c='Z', count=2, spread=7)


def selfie(f, t, n):
    k = t % 12
    pose = k // 3
    x, y = 11, BY
    eyes, eyes_r, la, shear = [('happy', None, 'wave', 0.05), ('normal', 'blink', 'side', -0.04),
                               ('big', None, 'up', 0.0), ('closed', None, 'high', 0.04)][pose]
    L = Canvas()
    info = clawd(L, x=x, y=y, eyes=eyes, eyes_r=eyes_r, la=la, ra='up')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    L.art(['ZZZZ', 'ZkZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ', 'ZZZZ'], hx - 1, hy - 6)
    L.put(hx + 1, hy - 5, 'W')
    f.blit(L.shear(shear, 36) if shear else L)
    if k % 3 == 1:
        f.art(['.W.', 'WWW', '.W.'], hx + 3, hy - 9)
        f.art(['U...U', '.....', 'U...U'], hx + 2, hy - 10)
    if k % 3 == 2:
        f.art(P.HEART, hx + 4, hy - 12)
        f.art(['.U.', 'UUU', '.U.'] if pose % 2 else P.HEART, hx - 6, hy - 10)


def phone_call(f, t, n):
    k = t % 16
    # little table + rotary phone
    f.rect(0, 28, 11, 1, 'N'); f.rect(0, 29, 11, 1, 'n'); f.rect(1, 30, 1, 6, 'n'); f.rect(9, 30, 1, 6, 'n')
    f.rrect(1, 24, 9, 4, 'R'); f.disc(5.5, 25.5, 1.6, 'W'); f.put(5, 25, 'k')
    f.rect(1, 23, 2, 1, 'R'); f.rect(8, 23, 2, 1, 'R')
    x, y = 17, BY
    line = ['MHM', 'MHM', 'YEP', 'BYE'][k // 4]
    nod = line == 'MHM' and k % 2
    info = clawd(f, x=x, y=y + (1 if nod else 0), h=12 - (1 if nod else 0), la='high',
                 ra='wave' if line == 'BYE' and k % 2 else 'up' if line == 'BYE' else 'side',
                 eyes='closed' if nod else 'happy' if line in ('YEP', 'BYE') else 'normal',
                 top=bool(nod))
    yy = y + (1 if nod else 0)
    # handset against the side of the head
    f.art(['RR.', 'RR.', '.R.', '.R.', '.R.', '.RR', '.RR'], x - 3, yy)
    # coiled cord: zig-zag sagging from the phone to the handset
    x0, y0, x1, y1 = 9, 27, x - 2, yy + 7
    bounce = [0, 1, 2, 1][k % 4]
    steps = 14
    for i in range(steps + 1):
        u = i / steps
        cx = x0 + (x1 - x0) * u
        cy = y0 + (y1 - y0) * u + math.sin(u * math.pi) * (4 + bounce)
        f.put(cx, cy + (1 if i % 2 else -1), 'Z')
    P.say(f, info, line, c='B')


ENVELOPE = ['GGGGGGG', 'GWGWGWG', 'GWWGWWG', 'GWWWWWG', 'GGGGGGG']
ENV_OPEN = ['.GGGGG.', 'GWWWWWG', 'GGGGGGG', 'GWGWGWG', 'GWWGWWG', 'GWWWWWG', 'GGGGGGG']


def postbox(f):
    f.rrect(29, 16, 9, 4, 'R'); f.rect(29, 19, 9, 15, 'R'); f.rect(28, 34, 11, 2, 'M')
    f.rect(29, 22, 1, 2, 'K'); f.rect(29, 21, 2, 1, 'M')
    f.rect(32, 26, 4, 3, 'U'); f.rect(33, 27, 2, 1, 'R'); f.rect(30, 18, 7, 1, 'M')


def mail(f, t, n):
    k = t % 24
    postbox(f)
    if k < 7:
        x = 3
    elif k < 13:
        x = 3 + (k - 6)
    elif k < 17:
        x = 9
    else:
        x = max(3, 9 - (k - 16))
    walking = 7 <= k < 13 or 17 <= k < 23
    view = 'q2l' if 17 <= k < 22 else 'q2r'
    lick = k in (1, 2)
    eyes = 'closed' if lick else 'happy' if k >= 15 else 'focus' if k in (4, 5) else 'normal'
    info = clawd(f, x=x, y=BY + (k % 2 if walking else 0), view=view, ra='high', legs=wl(k) if walking else (0, 0, 0, 0),
                 eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if view == 'q2l':
        hx, hy = int(info['lh'][0]), int(info['lh'][1])
    if k < 13:
        art = ENV_OPEN if k < 3 else ENVELOPE
        ex, ey = hx - 1, hy - len(art) - 1 + 2
        f.art(art, ex, ey)
        if k >= 4:
            f.rect(ex + 5, ey + 1, 2, 2, 'Z')
        if k == 4:
            f.art(['U.U', '.U.', 'U.U'], ex + 7, ey - 3)
    elif k < 17:
        ex = hx - 1 + (k - 13) * 2
        ey = 21
        for j, row in enumerate(ENVELOPE):
            for i, ch in enumerate(row):
                if ex + i < 29:
                    f.put(ex + i, ey + j, ch)
        if ex < 29:
            f.rect(min(ex + 5, 28), ey + 1, max(0, min(2, 29 - ex - 5)), 2, 'Z')
    if 15 <= k <= 18:
        f.art(P.HEART, 32, 12 - (k - 15) * 2)
    if k == 23:
        f.art(ENV_OPEN, hx - 1, hy - 6)
        f.art(P.SPARK, hx + 6, hy - 9)


CROSS_BLACK = {(1, 0), (3, 1), (0, 2), (2, 3), (4, 2)}
CROSS_FILL = [(0, 0), (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (4, 1), (1, 2), (2, 2), (3, 2), (0, 3), (1, 3)]


def crossword(f, t, n):
    k = t % 16
    x, y = BX, BY - 3
    think = k < 4
    done = 12 <= k <= 13
    flip = k in (14, 15)
    eyes = 'normal' if think else 'focus' if k < 12 else 'happy' if done else 'blink'
    info = clawd(f, x=x, y=y, la='low', ra='high' if think else 'low', eyes=eyes, lookv=-1 if think else 0,
                 look=1 if think and k % 2 else 0)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    # folded newspaper held in front of the lower body, crossword side up
    px, py = x + 1, y + 10
    rows = 12 if not flip else (5 if k == 14 else 9)
    oy = (12 - rows) // 2
    f.rect(px, py + oy, 17, rows, 'W'); f.box(px, py + oy, 17, rows, 'G')
    if not flip:
        f.rect(px + 2, py + 1, 6, 1, 'g'); f.rect(px + 10, py + 1, 5, 1, 'g')
        gx, gy = px + 1, py + 2
        filled = 0 if think else min(len(CROSS_FILL), (k - 3) * 2) if k < 12 else len(CROSS_FILL)
        for j in range(3):
            for i in range(5):
                cx, cy = gx + i * 3, gy + j * 3
                f.box(cx, cy, 4, 4, 'g')
                if (i, j) in CROSS_BLACK:
                    f.rect(cx + 1, cy + 1, 2, 2, 'k')
        cells = [c for c in CROSS_FILL if c[1] < 3]
        filled = min(filled, len(cells))
        for (i, j) in cells[:filled]:
            cx, cy = gx + i * 3, gy + j * 3
            f.put(cx + 1, cy + 1, 'B'); f.put(cx + 2, cy + 2, 'B')
        if 4 <= k < 12:
            i, j = cells[max(0, filled - 1)]
            tx, ty = gx + i * 3 + 2, gy + j * 3 + 2
            f.line(hx - 1, hy, tx + 1, ty - 1, 'Y'); f.put(tx, ty, 'k'); f.put(hx - 1, hy, 'Z')
    else:
        f.rect(px + 2, py + oy + 1, 13, 1, 'g')
    if think:
        # pencil tapped against the raised claw while pondering
        f.rect(hx - 1, hy - 6 + (k % 2), 1, 5, 'Y'); f.put(hx - 1, hy - 7 + (k % 2), 'Z')
        f.art(P.QMARK, x + 18, y - 8 + (k % 2))
    if done:
        P.sparkles(f, k, 4, [(x - 3, y), (x + 19, y + 2), (x + 8, y - 5)])


SKY_PIECE = ['..SS..', 'SSSSSS', 'SSSSSS', 'SSSSSS', 'EEEEEE']


def jigsaw(f, t, n):
    k = t % 16
    x, y = 2, BY
    placed = 8 <= k <= 13
    cheer = 9 <= k <= 12
    eyes = 'focus' if k < 5 else 'normal' if k < 8 else 'happy' if k < 13 else 'normal'
    info = clawd(f, x=x, y=y - (1 if cheer and k % 2 else 0), view='q2r', ra='up' if cheer else 'high', eyes=eyes)
    # puzzle lying on the floor to the right
    gx = 20
    f.rect(gx, 30, 19, 6, 'S'); f.rect(gx, 34, 19, 2, 'E')
    f.rect(gx, 30, 19, 1, 'B'); f.rect(gx, 30, 1, 6, 'B'); f.rect(gx + 18, 30, 1, 6, 'B')
    f.disc(35, 32, 1.6, 'U')
    for sx in (26, 33):
        for yy in range(31, 36):
            f.put(sx, yy, 'e' if yy >= 34 else 'B')
    hole = (27, 30)
    if not placed:
        f.rect(hole[0], hole[1] + 1, 6, 4, 'n'); f.rect(hole[0] + 2, hole[1], 2, 1, 'n')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if k < 5:
        art = SKY_PIECE if k % 2 == 0 else [''.join(r[i] for r in SKY_PIECE[::-1]) for i in range(6)]
        f.art(art, hx - 1, hy - 7)
        if k in (1, 3):
            f.art(P.QMARK, x + 10, y - 8)
    elif k < 8:
        px, py = arc(hx - 1, hy - 7, hole[0], hole[1], 3, (k - 4) / 4)
        f.art(SKY_PIECE, px, py)
    elif placed:
        f.art(SKY_PIECE, hole[0], hole[1])
        if k in (8, 9):
            f.text('CLICK', 21, 14, 'g')
            P.sparkles(f, k, 4, [(24, 28), (35, 28), (30, 26)])
    else:
        f.art(SKY_PIECE, hole[0], hole[1] - (k - 13) * 3)


BLK = [('R', 'M'), ('B', 'b'), ('U', 'Y'), ('E', 'e'), ('P', 'b')]
SCAT = [(27, 31), (34, 31), (21, 31), (34, 26), (39, 31)]


def block(f, x, y, j):
    c, e = BLK[j]
    f.rect(x, y, 5, 5, e); f.rect(x + 1, y + 1, 3, 3, c); f.put(x + 2, y + 2, 'W')


def tower(f, t, n):
    k = t % 24
    x, y = 3, BY
    slot = lambda j: (27, 31 - 5 * j)
    eyes = 'focus'
    ra = 'side'
    L = Canvas()
    if k < 12:
        j = k // 3 + 1
        ph_ = k % 3
        for i in range(5):
            if i < j or i == 0:
                block(L, *slot(i), i)
            elif i > j:
                block(L, *SCAT[i], i)
        sx, sy = SCAT[j]
        tx, ty = slot(j)
        if ph_ == 0:
            block(L, sx, sy - 3, j); ra = 'high'
        elif ph_ == 1:
            px, py = arc(sx, sy - 3, tx, ty, 6, 0.5)
            block(L, px, py, j); ra = 'up'
        else:
            block(L, tx, ty, j)
        eyes = 'focus'
    elif k < 18:
        for i in range(5):
            block(L, *slot(i), i)
        eyes = 'happy' if k < 15 else 'worried'
    elif k == 18:
        for i in range(5):
            if i == 0:
                block(L, *slot(0), 0)
            else:
                sx, sy = slot(i)
                tx, ty = SCAT[i]
                block(L, (sx + tx) // 2 + 2, (sy + ty) // 2, i)
        eyes = 'big'
    else:
        for i in range(5):
            block(L, *SCAT[i], i)
        eyes = 'x' if k < 21 else 'blink' if k == 21 else 'normal'
    if 15 <= k <= 17:
        L = L.shear([0.03, -0.04, 0.06][k - 15], 36)
    info = clawd(f, x=x, y=y, view='q2r', ra=ra, eyes=eyes, la='high' if k in (19, 20) else 'side')
    f.blit(L)
    if 12 <= k <= 14:
        P.sparkles(f, k, 4, [(24, 8), (35, 12), (29, 5)])
    if k == 18:
        f.text('CLONK', 10, 6, 'g')


def yoyo(f, t, n):
    k = t % 16
    x, y = 4, BY
    hx, hy = x + 20, y + 4
    if k < 8:
        d = [0, 3, 6, 9, 9, 6, 3, 0][k]
        yx, yy = hx, hy + 2 + d
    elif k < 15:
        a = math.pi / 2 - 2 * math.pi * (k - 8) / 7
        yx, yy = hx + 6 + 6 * math.cos(a) - 6 * (1 - (k - 8) / 7) * 0, hy + 2 + 6 * math.sin(a) - 0
    else:
        yx, yy = hx, hy + 5
    yx, yy = int(round(yx)), int(round(yy))
    look = 1 if yx > hx + 2 else 0
    lookv = 1 if yy > hy + 4 else -1 if yy < hy - 1 else 0
    info = clawd(f, x=x, y=y, ra='high' if k in (4, 5, 15) else 'mid', eyes='happy' if 8 <= k <= 14 else 'normal',
                 look=look, lookv=lookv)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    f.line(hx - 1, hy, yx, yy, 'g')
    f.art(['.RR.', 'RWZR', 'RZWR', '.RR.'] if k % 2 else ['.RR.', 'RZWR', 'RWZR', '.RR.'], yx - 2, yy - 1)
    if 8 <= k <= 14:
        f.put(yx + 3, yy + 1, 'L')


def kite(f, t, n):
    k = t % 16
    a = 2 * math.pi * t / n

    def kpos(tt):
        aa = 2 * math.pi * tt / n
        return 29 + 4 * math.cos(aa), 8 + 3 * math.sin(2 * aa)
    kx, ky = kpos(t)
    kx, ky = int(round(kx)), int(round(ky))
    # grass tufts
    for gx in (3, 15, 27, 36):
        f.art(['E.E', '.E.'], gx, 34)
    x, y = 3, BY
    info = clawd(f, x=x, y=y + (k % 2), view='q2r', ra='up', legs=wl(t), eyes='happy', tilt=1)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    f.line(hx, hy, kx, ky + 4, 'g')
    # tail of bows lagging behind
    prev = (kx, ky + 4)
    for i in range(1, 5):
        px = int(round(kx + i * 1.5 + 1.5 * math.sin(2 * math.pi * (t / 8) - i)))
        py = ky + 4 + i * 3
        f.line(prev[0], prev[1], px, py, 'g')
        f.art(['B.B', '.B.', 'B.B'] if i % 2 else ['U.U', '.U.', 'U.U'], px - 1, py - 1)
        prev = (px, py)
    f.art(['...Z...', '..ZZU..', '.ZZZUU.', 'NNNNNNN', '.UUNZZ.', '..UNZ..', '...N...'], kx - 3, ky - 3)


GFISH = ['Y.FF.', 'YFFKF', 'Y.FF.']


def goldfish(f, t, n):
    k = t % 16
    table(f, 19, 31, 20)
    bx, by, r = 29, 22, 8
    # water + gravel inside the bowl
    for yy in range(by - r, by + r):
        for xx in range(bx - r, bx + r):
            d = (xx + .5 - bx) ** 2 + (yy + .5 - by) ** 2
            if d <= (r - 1) ** 2 and yy >= by - 5:
                f.put(xx, yy, 'S')
    f.rect(bx - 5, by + 5, 10, 1, 'Y'); f.rect(bx - 4, by + 6, 8, 1, 'N')
    for i, yy in enumerate(range(by + 4, by - 3, -1)):
        f.put(bx - 4 + (i % 2), yy, 'E')
    # fish
    if k < 6:
        fx, fy, right = 25 + k, by, True
    elif k < 10:
        fx, fy, right = 30 - (k - 6), by - 4 + (1 if k == 9 else 0), False
    elif k < 14:
        fx, fy, right = 23, by - 1, False
    else:
        fx, fy, right = 24 + (k - 14) * 2, by, True
    f.art(GFISH if right else [r_[::-1] for r_ in GFISH], fx, fy)
    if 7 <= k <= 9:
        for i in range(3):
            f.put(bx - 2 + i * 2, by - 5 + (k - 7) + (i % 2), 'U')
        if k == 9:
            P.bubble_ring(f, fx + 1, by - 7, 1.2)
    f.ring(bx, by, r, 'L')
    f.rect(bx - 4, by - r - 1, 8, 1, 'L')
    f.put(bx - 5, by - 5, 'W'); f.put(bx - 6, by - 3, 'W')
    # Clawd
    lean = 2 if 10 <= k <= 13 else 0
    sprinkle = k == 6
    info = clawd(f, x=3 + lean, y=BY, view='q2r', ra='up' if sprinkle else 'side',
                 eyes='big' if lean else 'happy' if 7 <= k <= 9 else 'normal')
    if sprinkle:
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        for i in range(3):
            f.put(hx + 3 + i * 2, hy - 1 + i, 'U')
    if k in (11, 12):
        f.art(P.HEART, 21, 9 - (k - 11))


def pet_mini(f, t, n):
    k = t % 16
    x, y = 3, BY
    pour = 4 <= k <= 7
    info = clawd(f, x=x, y=y, view='q2r', ra='high' if k >= 2 and k <= 8 else 'side',
                 eyes='happy' if k >= 10 else 'normal')
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if 2 <= k <= 8:
        if pour:
            f.art(['NNNNNN.', 'NUUUUNn', 'NUCCUNn', 'NUUUUN.', 'NNNNNN.'], hx - 1, hy - 5)
            for i in range(3):
                f.put(hx + 6 + (i % 2), hy - 2 + ((k * 2 + i * 3) % 8), 'n')
        else:
            f.art(['.NNN.', 'NNNNN', 'NUUUN', 'NUCUN', 'NUUUN', 'NNNNN'], hx - 1, hy - 6)
    # bowl
    fill = 0 if k < 5 else min(3, k - 4) if k < 9 else max(0, 3 - (k - 8) // 2)
    f.rect(23, 33, 8, 2, 'R'); f.rect(24, 35, 6, 1, 'M')
    if fill:
        f.rect(25, 33 - (1 if fill > 1 else 0), 4, 1, 'n')
        for i in range(fill):
            f.put(24 + i * 2, 32, 'N')
    # the pet
    if k < 8:
        my = 28 - (3 if k % 2 else 0)
        mini(f, 29, my, eyes='happy' if k % 2 else 'big', legs=(1, 1, 1, 1) if k % 2 else (0, 0, 0, 0),
             la='up' if k % 2 else 'side', ra='up' if k % 2 else 'side')
    elif k < 14:
        mini(f, 27, 28 + (k % 2), eyes='closed', view='ql')
    else:
        mini(f, 29, 28, eyes='happy' if k == 14 else 'happy')
        f.art(P.HEART, 32, 22 - (k - 14) * 2)


CRANE_UP = ['....Z.Z....', '...ZZ.ZZ...', 'Z.ZZZ.ZZZ.Z', '.ZZZZZZZZZ.', '...ZZZZZ...']
CRANE_DN = ['Z.........Z', '.ZZZZZZZZZ.', '...ZZZZZ...', '..ZZ...ZZ..', '.Z.......Z.']
FOLDS = [
    ['ZZZZZZZZ', 'ZrrrrrrZ', 'ZrrrrrrZ', 'ZrrrrrrZ', 'ZrrrrrrZ', 'ZrrrrrrZ', 'ZrrrrrrZ', 'ZZZZZZZZ'],
    ['Z.......', 'ZZ......', 'ZrZ.....', 'ZrrZ....', 'ZrrrZ...', 'ZrrrrZ..', 'ZrrrrrZ.', 'ZZZZZZZZ'],
    ['...Z....', '..ZrZ...', '.ZrrrZ..', 'ZrrrrrZ.', 'ZZZZZZZ.'],
    ['...Z...', '..ZrZ..', '.ZrrrZ.', 'ZrrZrrZ', '.ZrrrZ.', '..ZrZ..', '...Z...'],
    ['Z.....Z', '.Z...Z.', '..ZrZ..', '.ZrrrZ.', 'ZZZZZZZ'],
]


def origami(f, t, n):
    k = t % 20
    x, y = BX, BY - 2
    stage = [0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4][k] if k <= 10 else None
    fly = 11 <= k <= 15
    eyes = 'focus' if k < 9 else 'normal' if k < 11 else 'happy' if fly else 'normal'
    clawd(f, x=x, y=y, la='low', ra='low', eyes=eyes, look=1 if fly else 0, lookv=-1 if fly else 0)
    top = y + 9
    if stage is not None:
        art = FOLDS[stage]
        w, h = size(art)
        f.art(art, 20 - w // 2, top + 8 - h)
        if k in (3, 5, 7, 9):
            f.art(['U.U', '.U.', 'U.U'], 30, top + 2)
    elif fly:
        j = k - 11
        f.art(CRANE_UP if k % 2 else CRANE_DN, 24 + j * 4, top + 3 - j * 6)
    else:
        if k >= 17:
            f.art(FOLDS[0], 16, top)
        if k == 16:
            P.sparkles(f, 0, 4, [(20, top + 3)])
            f.put(20, top + 4, 'W')
    if 11 <= k <= 13:
        P.sparkles(f, k, 4, [(6, 12), (35, 22)])


def carrot(f, t, n):
    k = t % 16
    # soil mound + carrot greens
    f.rect(21, 34, 14, 2, 'n'); f.rect(23, 33, 10, 1, 'N')
    grow = {13: 1, 14: 2, 15: 3}.get(k, 3 if k < 8 else 0)
    stretch = 1 if 3 <= k <= 7 else 0
    if grow:
        for i, dx in enumerate((-1, 0, 1)):
            hgt = grow + stretch + (1 if i == 1 else 0)
            f.rect(27 + dx * 2, 33 - hgt, 1, hgt, 'E')
            f.put(27 + dx * 2, 33 - hgt, 'e')
    if 3 <= k <= 7:
        f.rect(26, 32, 3, 1, 'F')
    x, y = 6, BY
    L = Canvas()
    if k < 8:
        tug = 2 <= k <= 7
        info = clawd(L, x=x - (1 if tug and k % 2 else 0), y=y, view='q2r', ra='mid',
                     eyes='angry' if tug else 'focus', legs=(0, 0, 0, 1) if tug else (0, 0, 0, 0))
        hx, hy = int(info['rh'][0]), int(info['rh'][1])
        L.line(hx, hy, 27, 30 - stretch, 'O')
        f.blit(L.shear(-0.08 if tug and k % 2 else -0.04 if tug else 0, 36))
        if tug:
            f.art(P.SWEAT, x - 3, y - 2)
            if k % 2:
                f.put(24, 32, 'n'); f.put(31, 31, 'n')
    elif k == 8:
        clawd(f, x=x - 3, w=18, h=9, y=BY + 3, eyes='x', view='q2r')
        f.text('POP', 23, 18, 'F')
        P.dust(f, x - 4, GROUND, 0.5)
    else:
        info = clawd(f, x=x, y=y, view='front', la='up', ra='up', eyes='big' if k < 12 else 'happy')
    # the big carrot
    CAR = ['.E.E.', 'EEEEE', '.FFF.', 'FFFFF', 'FFdFF', '.FFF.', '.FdF.', '..F..', '..F..']
    if k == 8:
        f.art(CAR, 25, 18)
    elif k == 9:
        f.art(CAR, 20, 8)
    elif k >= 10:
        f.art(CAR, x + 6, y - 9 - (1 if k % 2 else 0))
        if k >= 11:
            P.sparkles(f, k, 4, [(x + 2, y - 8), (x + 15, y - 5)])


def tv_remote(f, t, n):
    k = t % 16
    # sofa
    f.rrect(1, 18, 24, 12, 'V'); f.rect(2, 19, 22, 1, 'B')
    f.rect(1, 25, 4, 9, 'B'); f.rect(1, 25, 4, 1, 'S'); f.rect(21, 25, 4, 9, 'B'); f.rect(21, 25, 4, 1, 'S')
    f.rect(5, 30, 16, 4, 'B'); f.rect(5, 30, 16, 1, 'S')
    f.rect(2, 34, 2, 2, 'n'); f.rect(22, 34, 2, 2, 'n')
    # TV
    f.rect(28, 17, 11, 9, 'g'); f.rect(29, 18, 9, 7, 'k'); f.rect(32, 26, 3, 1, 'g'); f.rect(30, 27, 7, 9, 'N')
    ch = k // 4
    sx, sy = 29, 18
    if ch == 0:
        r = rng(k)
        for yy in range(7):
            for xx in range(9):
                f.put(sx + xx, sy + yy, r.choice('WGgk'))
    elif ch == 1:
        for i, c in enumerate('RUECBPZ'):
            f.rect(sx + i + (1 if i > 3 else 0), sy, 1 + (1 if i == 3 else 0), 7, c)
    elif ch == 2:
        f.rect(sx, sy, 9, 7, 'B')
        f.art(['Y.FF.', 'YFFKF', 'Y.FF.'] if k % 2 else ['.FF.Y', 'FKFFY', '.FF.Y'], sx + 2, sy + 2)
    else:
        f.rect(sx, sy, 9, 7, 'r')
        mini(f, sx + 1 if k % 2 else sx + 2, sy, eyes='happy', la='up' if k % 2 else 'side', ra='side' if k % 2 else 'up')
    click = k % 4 == 3 and k < 12
    eyes = 'blink' if ch < 3 else 'normal'
    info = clawd(f, x=6, y=19, leg_h=0, view='qr', ra='out' if click else 'side', eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    f.rect(hx - 1, hy - 1, 3, 2, 'k'); f.put(hx + 1, hy - 1, 'R')
    if click:
        f.put(hx + 3, hy - 2, 'R'); f.put(hx + 5, hy - 3, 'R')
    if ch == 3:
        f.art(P.HEART, 14, 13 - (k % 2))


DIE = {1: ['.....', '..K..', '.....'], 6: ['K...K', 'K...K', 'K...K'], 3: ['K....', '..K..', '....K'],
       5: ['K...K', '..K..', 'K...K'], 2: ['K....', '.....', '....K'], 4: ['K...K', '.....', 'K...K']}


def die(f, x, y, v):
    f.rect(x, y, 7, 5, 'W'); f.box(x, y, 7, 5, 'G')
    f.art(DIE[v], x + 1, y + 1)


def dice(f, t, n):
    k = t % 16
    f.rect(3, 29, 34, 7, 'T'); f.box(3, 29, 34, 7, 'N')
    for i in range(8):
        f.rect(5 + i * 4, 30, 3, 2, 'RBEU'[i % 4])
    f.rect(5, 33, 3, 2, 'E'); f.rect(33, 33, 3, 2, 'R')
    f.art(['.P', 'PP'], 14, 32)
    x, y = BX, 14
    shake = k < 4
    throw = k == 4
    rolling = 5 <= k <= 9
    cheer = 10 <= k <= 13
    clawd(f, x=x + ((1 if k % 2 else -1) if shake else 0), y=y - (2 if cheer and k % 2 else 0),
          la=('high' if k % 2 else 'mid') if shake else 'up' if cheer else 'side',
          ra=('mid' if k % 2 else 'high') if shake else 'up' if cheer else 'out' if throw else 'side',
          eyes='closed' if shake else 'big' if cheer else 'focus')
    if shake:  # rattling dice
        die(f, x + 18, y - 1 + (k % 2) * 2, [2, 5, 3, 6][k])
        f.art(['L.L', '.L.'] if k % 2 else ['.L.', 'L.L'], x + 26, y + 1)
    if rolling or throw:
        j = k - 4
        for d, (x0, x1) in enumerate(((29, 15), (31, 26))):
            px = x0 + int((x1 - x0) * j / 5) + d * 2
            py = [22, 26, 24, 28, 27, 29][j] - d
            die(f, px, py, [3, 5, 2, 4, 1, 6][(j + d * 2) % 6] if j < 5 else 6)
    elif k >= 10:
        die(f, 15, 29, 6); die(f, 26, 28, 6)
        if cheer:
            f.text('6+6', 14, 5, 'R')
            P.sparkles(f, k, 4, [(6, 12), (34, 10), (30, 4)])


DONUT_EDGE = ['.rrrrrr.', 'rUrrBrZr', 'YYYYYYYY', '.NNNNNN.']


JELLY = ['..EEEEEEE..', '.EWEeEEeEE.', '.EWEeEEeEE.', 'EEEEeEEeEEE', 'EWEEeEEeEEE', 'EEEEEEEEEEE', 'eeeeeeeeeee']


def jelly(f, t, n):
    """Pokes a jelly with a spoon: it wobbles, and Clawd wobbles right along with it."""
    k = t % 16
    x, y = 3, BY
    table(f, 21, 31, 18)
    f.rect(22, 30, 15, 1, 'W'); f.put(22, 30, 'G'); f.put(36, 30, 'G')
    wob = [0, 0, 0, 0.3, -0.25, 0.2, -0.15, 0.1, -0.05, 0, 0, 0.15, -0.1, 0.05, 0, 0][k]
    J = Canvas()
    J.art(JELLY, 24, 23)
    f.blit(J.shear(wob, 30) if wob else J)
    poke = k in (2, 10)
    eyes = 'big' if k < 2 else 'closed' if poke else 'happy' if wob else 'normal'
    L = Canvas()
    info = clawd(L, x=x, y=y, view='q2r', ra='high', eyes=eyes)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    tip = (24, 26) if poke else (hx + 3, hy - 3)
    L.line(hx, hy, tip[0], tip[1], 'G'); L.rect(tip[0] - (1 if poke else 0), tip[1] - 1, 2, 2, 'G')
    f.blit(L.shear(-wob * 0.5, 36) if wob else L)
    if wob:
        side = 1 if wob > 0 else -1
        f.art(['L.', '.L', 'L.'] if side > 0 else ['.L', 'L.', '.L'], 36, 23)
        f.art(['.L', 'L.', '.L'] if side > 0 else ['L.', '.L', 'L.'], 21, 23)
    if k in (6, 7, 14):
        f.art(P.HEART, x + 12, y - 4 - (k % 2))


CAMERA_SIDE = ['.yg.....', 'gggggg..', 'gkkkkgGG', 'gkkkkGSG', 'gkkkkgGG', 'gggggg..']


# --------------------------------------------------------------------------- register
add('life_pizza_munch', '大口吃披萨', 'Pizza munch', pizza, n=16, dur=130)
add('life_donut_toss', '甜甜圈套圈', 'Donut ring toss', donut, n=14, dur=120)
add('life_icecream_melt', '冰淇淋化了', 'Melting ice cream', icecream, n=16, dur=140)
add('life_noodle_slurp', '吸溜面条', 'Slurping noodles', noodles, n=12, dur=130)
add('life_boba_straw', '珍珠奶茶', 'Boba crazy straw', boba, n=16, dur=110)
add('life_burger_stack', '叠汉堡', 'Burger stack', burger, n=20, dur=120)
add('life_sushi_belt', '回转寿司', 'Conveyor sushi', sushi, n=20, dur=120)
add('life_watermelon_seeds', '吐西瓜籽', 'Spitting melon seeds', melon, n=16, dur=120)
add('life_popcorn_catch', '接爆米花', 'Popcorn catch', popcorn, n=12, dur=110)
add('life_cake_strawberry', '先吃草莓', 'Strawberry on top', cake, n=16, dur=130)
add('life_apple_crunch', '咔嚓啃苹果', 'Apple crunch', apple, n=12, dur=130)
add('life_lemon_sour', '酸柠檬', 'Sour lemon', lemon, n=14, dur=120)
add('life_soda_fizz', '摇汽水', 'Shaken soda', soda, n=16, dur=110)
add('life_dumpling_steam', '揭笼屉', 'Steamed dumplings', dumpling, n=14, dur=140)
add('life_cereal_pour', '倒麦片', 'Cereal and milk', cereal, n=24, dur=120)
add_tweened('life_toast_pop', '吐司弹起来', 'Toast pop catch', toast, n=14, dur=beats(14, 120, {6: 300, 7: 150, 8: 250, 9: 150}), tw_at={7: 1, 9: 1})
add('life_jelly_wobble', '戳果冻', 'Wobbly jelly', jelly, n=16, dur=110)
add('life_smoothie_blend', '榨果昔', 'Smoothie blender', blender, n=18, dur=120)
add('life_fridge_raid', '偷吃冰箱', 'Fridge raid', fridge, n=16, dur=130)
add_tweened('life_microwave_wait', '等微波炉', 'Microwave countdown', microwave, n=16, dur=beats(16, 140, {12: 350}), tw_at={11: 1, 12: 1})
add_tweened('life_cookie_jar', '偷拿饼干', 'Cookie jar sneak', cookie_jar, n=24, dur=beats(24, 110, {8: 200, 9: 200, 10: 250, 11: 200, 13: 200, 14: 300}), tw_at={7: 1, 10: 1, 13: 1})
add('life_sweep_floor', '扫地', 'Sweeping up', sweep, n=16, dur=110)
add('life_vacuum', '吸尘器', 'Vacuuming', vacuum, n=16, dur=100)
add('life_washer_watch', '盯着洗衣机', 'Watching the washer', washer, n=16, dur=120)
add('life_laundry_line', '晾衣服', 'Laundry line gust', laundry, n=16, dur=130)
add('life_wash_dishes', '洗碗', 'Washing dishes', dishes, n=16, dur=120)
add_tweened('life_water_plant', '浇花', 'Watering a droopy plant', water_plant, n=24, dur=120, tw_at={3: 1, 11: 1})
add_tweened('life_trash_out', '倒垃圾', 'Taking out the trash', trash, n=24, dur=beats(24, 110, {8: 200, 9: 150, 10: 150, 11: 200, 12: 350, 13: 200}), tw_at={9: 1, 11: 1, 14: 1})
add('life_iron_shirt', '熨衣服', 'Ironing a shirt', iron, n=16, dur=120)
add('life_feather_duster', '掸灰尘', 'Dust cloud shake-off', duster, n=16, dur=120)
add('life_window_wipe', '擦窗画爱心', 'Window wipe & doodle', window_wipe, n=16, dur=130)
add('life_bubble_bath', '泡泡浴', 'Bubble bath', bubble_bath, n=16, dur=140)
add('life_brush_teeth', '刷牙', 'Brushing teeth', brush_teeth, n=12, dur=110)
add('life_bed_sleep', '盖被子睡觉', 'Tucked in bed', bed_sleep, n=16, dur=200)
add('life_alarm_snooze', '拍闹钟', 'Snoozing the alarm', alarm, n=16, dur=beats(16, 120, {5: 160, 6: 350}))
add('life_shower_sing', '洗澡唱歌', 'Shower singing', shower, n=16, dur=130)
add('life_hair_dryer', '吹风机', 'Blow-dry', hair_dryer, n=12, dur=100)
add('life_paint_easel', '画画', 'Painting at the easel', easel, n=24, dur=130)
add('life_photo_polaroid', '拍立得', 'Polaroid snap', photo, n=16, dur=130)
add('life_knit_scarf', '织围巾', 'Knitting a scarf', knit, n=16, dur=140)
add('life_fishing', '钓鱼', 'Gone fishing', fishing, n=20, dur=130)
add('life_video_game', '打游戏', 'Gaming on the TV', video_game, n=12, dur=110)
add('life_piano', '弹钢琴', 'Piano player', piano, n=12, dur=130)
add('life_drums', '打鼓', 'Drum kit', drums, n=8, dur=110)
add('life_violin', '拉小提琴', 'Violin serenade', violin, n=12, dur=130)
add('life_karaoke', '卡拉OK', 'Karaoke night', karaoke, n=16, dur=130)
add('life_selfie', '自拍', 'Selfie poses', selfie, n=12, dur=150)
add_tweened('life_phone_call', '打电话', 'Phone call', phone_call, n=16, dur=150, tw_at={11: 1, 15: 1})
add_tweened('life_post_letter', '寄信', 'Posting a letter', mail, n=24, dur=120, tw_at={16: 1, 21: 1})
add('life_crossword', '填字游戏', 'Newspaper crossword', crossword, n=16, dur=150)
add('life_jigsaw', '拼图', 'Last jigsaw piece', jigsaw, n=16, dur=130)
add('life_block_tower', '搭积木', 'Block tower', tower, n=24, dur=120)
add('life_yoyo', '玩溜溜球', 'Yo-yo tricks', yoyo, n=16, dur=100)
add('life_kite', '放风筝', 'Flying a kite', kite, n=16, dur=140)
add('life_goldfish', '看金鱼', 'Goldfish bowl', goldfish, n=16, dur=140)
add('life_feed_pet', '喂小宠物', 'Feeding the pet', pet_mini, n=16, dur=130)
add('life_origami_crane', '折纸鹤', 'Origami crane', origami, n=20, dur=130)
add_tweened('life_carrot_pull', '拔萝卜', 'Pulling a carrot', carrot, n=16, dur=beats(16, 120, {7: 200, 8: 350}), tw_at={7: 1, 8: 1, 15: 1})
add('life_tv_remote', '换台', 'Channel surfing', tv_remote, n=16, dur=160)
add('life_dice_roll', '掷骰子', 'Rolling dice', dice, n=16, dur=120)
