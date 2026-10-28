"""Sports, exercise, movement and physical comedy (60 scenes, slug prefix sport_)."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, mini, sin, cos, ph, pick, tri, rng, parse, text_w)
from engine import beats, add_tweened
import props as P
from kit import S


# --------------------------------------------------------------------------- helpers
def lerp(a, b, p):
    return a + (b - a) * p


def walk(s):
    return (1, 0, 1, 0) if s else (0, 1, 0, 1)


def lay(**kw):
    """Draw Clawd on its own layer (for shear / rot90 / clipping)."""
    L = Canvas()
    return L, clawd(L, **kw)


def ol(f, art, x, y, oc='G', cmap=None, flip=False):
    """Art with a 1px outline so white things read on white and dark backgrounds."""
    rows = parse(art)
    if flip:
        w = max(len(r) for r in rows)
        rows = [r.ljust(w, '.')[::-1] for r in rows]
    pts = {(i, j) for j, r in enumerate(rows) for i, ch in enumerate(r) if ch not in '. '}
    x, y = int(round(x)), int(round(y))
    for (i, j) in pts:
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (i + di, j + dj) not in pts:
                f.put(x + i + di, y + j + dj, oc)
    f.art(rows, x, y, cmap=cmap)


def rot_art(a, k=1):
    """Rotate an art block by k*90 degrees clockwise."""
    rows = parse(a)
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, '.') for r in rows]
    for _ in range(k % 4):
        rows = [''.join(rows[len(rows) - 1 - j][i] for j in range(len(rows))) for i in range(len(rows[0]))]
    return rows


def vshear(L, k, px=20):
    """Column shear: column x moves down by round((x - px) * k) (for slopes)."""
    out = Canvas()
    for y in range(L.h):
        for x in range(L.w):
            c = L.px[y][x]
            if c is not None:
                out.put(x, y + int(round((x - px) * k)), c)
    return out


def outline_layer(L, oc='g'):
    """Add a 1px outline around everything drawn on layer L (in place) and return it."""
    pts = [(x, y) for y in range(L.h) for x in range(L.w) if L.px[y][x] is not None]
    filled = set(pts)
    for (x, y) in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in filled:
                L.put(q[0], q[1], oc)
    return L


def drop_to(L, bottom=GROUND):
    bb = L.bbox()
    return L.shift(0, bottom - bb[3]) if bb else L


def limb(f, x0, y0, x1, y1, c='O', t=2):
    for i in range(t):
        for j in range(t):
            f.line(x0 + i, y0 + j, x1 + i, y1 + j, c)


def racket(f, hx, hy, ang, r=3.0, head='R', fill='w', handle='k', hl=4):
    dx, dy = math.cos(ang), math.sin(ang)
    f.line(hx, hy, hx + dx * hl, hy + dy * hl, handle)
    cx, cy = hx + dx * (hl + r + .5) + .5, hy + dy * (hl + r + .5) + .5
    f.disc(cx, cy, r, fill)
    f.ring(cx, cy, r, head)
    return cx, cy


def bat(f, hx, hy, ang, length=12, c='N'):
    dx, dy = math.cos(ang), math.sin(ang)
    ex, ey = hx + dx * length, hy + dy * length
    f.line(hx, hy, ex, ey, c)
    ox, oy = (1, 0) if abs(dy) > abs(dx) else (0, 1)
    f.line(hx + dx * 4 + ox, hy + dy * 4 + oy, ex + ox, ey + oy, c)
    f.put(hx, hy, 'n')
    return ex, ey


def ground(f, c='G', y=GROUND, x0=0, x1=G):
    f.rect(x0, y, x1 - x0, 1, c)


def ticks(f, off, y=37, c='G', gap=8, w=3):
    """Scrolling ground dashes; off increases -> dashes move left."""
    for i in range(-1, G // gap + 2):
        f.rect(i * gap - int(off) % gap, y, w, 1, c)


def impact(f, x, y, c='U', c2='W'):
    f.art(['U.U.U', '.UWU.', 'UWWWU', '.UWU.', 'U.U.U'], int(x) - 2, int(y) - 2, cmap={'U': c, 'W': c2})


def blink_text(f, s, cx, y, t, cols=('R', 'U')):
    f.text_c(s, cx, y, cols[t % len(cols)])


# --------------------------------------------------------------------------- balls & gear art
SOCCER = (['.GWG.', 'GKKWG', 'WKKWW', 'GWWKG', '.GKG.'],
          ['.GKG.', 'GWWKG', 'KWKKW', 'GWKKG', '.GWG.'])
BASKET = (['.nnnn.', 'nFFnFn', 'nnnnnn', 'nFFnFn', 'nFFnFn', '.nnnn.'],
          ['.nnnn.', 'nFnFFn', 'nnnnnn', 'nFnFFn', 'nFnFFn', '.nnnn.'],
          ['.nnnn.', 'nnFFFn', 'nnnnnn', 'nnFFFn', 'nnFFFn', '.nnnn.'],
          ['.nnnn.', 'nFFFnn', 'nnnnnn', 'nFFFnn', 'nFFFnn', '.nnnn.'])
BASKET_SQ = ['..nnnn..', '.nFFnFFn', 'nnnnnnnn', '.nnnnnn.']
BOWL = (['.PPP.', 'PpPPP', 'PkPkP', 'PPPPP', '.PPP.'],
        ['.PPP.', 'PPPkP', 'PPpPP', 'PkPPP', '.PPP.'])
PIN = ['.WW.', 'WWWG', '.WG.', '.RR.', '.WG.', 'WWWG', 'WWWG', 'WWWG', 'WWWG', '.WG.']
TENNIS = ['.UU.', 'UEUU', 'UUEU', '.UU.']
BASEBALL = ['.W.', 'WWR', '.W.']
BALLOON = ['.ZZZ.', 'ZWZZZ', 'ZZZZZ', 'ZZZZZ', '.ZZZ.', '..Z..']


# --------------------------------------------------------------------------- soccer
def bicycle_kick(f, t, n):
    k = t % 16
    ground(f, 'E', 36)
    ball = None
    if k < 4:
        ball = [(0, 1), (4, 4), (8, 7), (11, 10)][k]
        sq = k == 3
        clawd(f, x=BX - (1 if sq else 0), y=BY + (2 if sq else 0), w=18 if sq else 16, h=10 if sq else 12,
              eyes='closed' if sq else 'normal', look=-1, lookv=-1, la='side', ra='side')
    elif k <= 6:
        rot = k - 3
        cx, cy = 20, [16, 13, 15][k - 4]
        L, info = lay(x=cx - 8, y=cy - 6, la='up', ra='up', legs=(0, 0, 0, 0), eyes='focus' if k < 6 else 'happy')
        f.blit(L.rot90(rot, cx, cy))
        if k == 4:
            ball = (11, 7)
        elif k == 5:
            ball = (17, 0)
            impact(f, 21, 3)
        else:
            ball = (29, 1)
            P.speedlines(f, 28, 1, t, n=2, length=7)
    elif k == 7:
        clawd(f, x=BX - 1, y=BY + 2, w=18, h=10, eyes='closed')
        P.dust(f, 8, GROUND, 0.3); P.dust(f, 31, GROUND, 0.3, flip=True)
        ball = (37, -1)
    elif k <= 12:
        s = (k - 8) % 2
        clawd(f, y=BY - 2 * s, la='up' if s else 'high', ra='up' if s else 'high',
              legs=(1, 1, 1, 1) if s else (0, 0, 0, 0), eyes='happy')
        blink_text(f, 'WOW!', 20, 4, k, ('R', 'Y'))
        if s:
            P.sparkles(f, k, 4, [(4, 14), (35, 12)])
    else:
        clawd(f, eyes='blink' if k == 14 else 'normal', look=-1 if k == 15 else 0, lookv=-1 if k == 15 else 0)
    if ball:
        f.art(SOCCER[t % 2], *ball)


def goal_net(f, bulge=None):
    for y in range(19, 36):
        for x in range(30, 40):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                dx = 0
                if bulge:
                    d = math.hypot(x - bulge[0], y - bulge[1])
                    dx = 2 if d < 3 else 1 if d < 6 else 0
                f.put(x + dx, y, 'L')
    f.rect(27, 16, 13, 1, 'G'); f.rect(27, 17, 13, 1, 'W'); f.rect(27, 18, 13, 1, 'G')
    f.rect(27, 16, 1, 20, 'G'); f.rect(28, 17, 1, 19, 'W'); f.rect(29, 18, 1, 18, 'G')


def goal_kick(f, t, n):
    k = t % 20
    ground(f, 'E', 36)
    ball = (20, 31)
    bulge = None
    if 5 <= k <= 8:
        ball = [(24, 27), (28, 24), (31, 22), (34, 22)][k - 5]
        if k == 8:
            bulge = (36, 24)
    elif 9 <= k <= 13:
        ball = (34, min(31, 22 + (k - 8) * 3))
    elif k >= 14:
        j = k - 14
        ball = (33 - j * 13 // 5 if j < 5 else 20, 31 - (1 if j % 2 else 0))
        if j == 5:
            ball = (20, 31)
    inside = ball[0] >= 29
    if inside:
        f.art(SOCCER[t % 2], *ball)
    goal_net(f, bulge)
    if k < 4:
        s = k % 2
        clawd(f, x=-6 + 3 * k, y=BY - s, view='q2r', legs=walk(s), eyes='focus')
    elif k == 4:
        x, y = 4, BY
        clawd(f, x=x, y=y, view='q2r', legs=(0, 0, 0, 3), eyes='focus')
        f.rect(x + 14, y + 12, 2, 1, 'O'); f.rect(x + 15, y + 13, 4, 2, 'O')
        impact(f, 22, 32)
    elif k <= 7:
        x, y = 4, BY
        up = k == 5
        clawd(f, x=x, y=y, view='q2r', legs=(0, 0, 0, 3) if up else (0, 0, 0, 0),
              eyes='big' if k > 5 else 'focus')
        if up:
            f.rect(x + 15, y + 9, 2, 3, 'O'); f.rect(x + 16, y + 8, 3, 2, 'O')
    elif k <= 13:
        s = (k - 8) % 2
        clawd(f, x=4, y=BY - 3 * s, view='front', la='up' if s else 'high', ra='up' if s else 'high',
              legs=(1, 1, 1, 1) if s else (0, 0, 0, 0), eyes='happy')
        blink_text(f, 'GOAL!', 13, 4, k, ('R', 'Y'))
        if s:
            P.sparkles(f, k, 4, [(3, 12), (24, 8)])
    else:
        j = k - 14
        s = j % 2
        clawd(f, x=4 - j * 2, y=BY + s, view='q2l', legs=walk(s), eyes='happy')
    if not inside:
        f.art(SOCCER[t % 2], *ball)
        if 5 <= k <= 7:
            P.speedlines(f, ball[0] - 1, ball[1], t, n=2, length=4)


def goal_frame_back(f):
    f.rect(1, 6, 38, 1, 'G'); f.rect(1, 6, 1, 30, 'G'); f.rect(38, 6, 1, 30, 'G')
    for y in range(8, 36, 3):
        for x in range(3, 37, 3):
            f.put(x, y, 'L')
    ground(f, 'E', 36)


def gloves(f, info, which=('l', 'r'), c='E', c2='e'):
    for s in which:
        hx, hy = info['lh' if s == 'l' else 'rh']
        f.rect(int(hx) - 2, int(hy) - 2, 4, 4, c)
        f.rect(int(hx) - 2, int(hy) + 1, 4, 1, c2)


def goalie_dive(f, t, n):
    k = t % 16
    goal_frame_back(f)
    ball = None
    if k < 4:
        b = k % 2
        info = clawd(f, x=BX, y=BY + b, h=12 - b, la='mid', ra='mid', eyes='focus', look=-1 if k < 2 else 1)
        gloves(f, info)
    elif k == 4:
        info = clawd(f, x=BX, y=BY + 1, h=11, la='mid', ra='mid', eyes='big', look=-1)
        gloves(f, info)
        ball = (1, 29)
    elif k in (5, 6):
        L = Canvas()
        cx, cy = (22, 18) if k == 5 else (26, 14)
        info = clawd(L, x=cx - 8, y=cy - 6, la='up', ra='up', eyes='focus' if k == 5 else 'happy',
                     legs=(1, 1, 0, 0))
        gloves(L, info)
        f.blit(L.rot90(1, cx, cy))
        if k == 5:
            ball = (12, 20)
            P.speedlines(f, 11, 17, t, n=3, length=5)
        else:
            ball = (31, 4)
            impact(f, 33, 6)
    elif k in (7, 8, 9, 10):
        L = Canvas()
        info = clawd(L, x=12, y=10, la='up', ra='up', eyes='closed' if k == 7 else 'happy')
        gloves(L, info)
        L = drop_to(L.rot90(1, 20, 16), 36 if k > 7 else 30)
        f.blit(L)
        bb = L.bbox()
        ball = (bb[2] - 3, bb[1] + 4)
        if k == 8:
            P.dust(f, 12, GROUND, 0.5); P.dust(f, 34, GROUND, 0.5, flip=True)
    elif k in (11, 12, 13):
        y = BY - (2 if k == 12 else 0)
        info = clawd(f, x=18, y=y, la='up', ra='up', eyes='happy', legs=(1, 1, 1, 1) if k == 12 else (0, 0, 0, 0))
        gloves(f, info)
        ball = (24, y - 9)
    else:
        j = k - 14
        info = clawd(f, x=16 - j * 2, la='high' if j == 0 else 'mid', ra='mid', eyes='normal', view='ql')
        gloves(f, info)
        if j == 0:
            ball = (4, 10)
    if ball:
        f.art(SOCCER[t % 2], *ball)


# --------------------------------------------------------------------------- basketball
DRIB = [  # (ball x, ball top) per frame; None top = squashed on the floor
    (30, 23), (30, 27), (30, None), (30, 27),
    (30, 23), (31, 28), (16, None), (4, 28),
    (4, 23), (4, 27), (4, None), (4, 27),
    (4, 23), (3, 28), (16, None), (31, 28)]


def dribble(f, t, n):
    k = t % 16
    bx, by = DRIB[k]
    u = k % 4
    side = 1 if (k < 4 or k >= 15 or k == 5) else -1 if 7 <= k <= 13 else 0
    low = by is None
    info = clawd(f, x=BX + side, y=BY + (1 if low else 0), h=12 - (1 if low else 0),
                 eyes='focus', look=side, lookv=1 if (by is None or by > 26) else 0,
                 ra='high' if (bx > 20 and u == 0) else 'side', la='high' if (bx < 10 and u == 0) else 'side')
    if low:
        f.art(BASKET_SQ, bx, 32)
        f.art(['L........L'], bx - 1, 35)
    else:
        f.art(pick(BASKET, k), bx, by)


def hoop(f, bulge=0):
    f.rect(38, 0, 2, 36, 'g')
    f.rect(35, 1, 2, 15, 'W'); f.rect(34, 1, 1, 15, 'G'); f.rect(37, 1, 1, 15, 'G')
    f.rect(35, 6, 2, 4, 'R')
    rim(f)
    net = ['GWGWGWGW', '.WGWGWG.', '.GWGWGW.', '..WGWG..']
    if bulge:
        net = ['GWGWGWGW', 'WGWGWGWG', 'GW....GW', '.WG..GW.', '..WGWG..']
    f.art(net, 27, 13)


def rim(f):
    f.rect(27, 12, 8, 1, 'R')


def dunk(f, t, n):
    k = t % 20
    ground(f, 'G', 36)
    hoop(f, bulge=k in (8, 9))
    ball = None
    reach = None
    shear = 0
    if k < 4:
        x, s = -4 + 3 * k, k % 2
        L, info = lay(x=x, y=BY + s, view='q2r', legs=walk(s), ra='side', eyes='focus')
        hx, hy = info['rh']
        ball = (int(hx) - 2, 26 if s == 0 else 30)
    elif k == 4:
        L, info = lay(x=7, y=BY + 2, w=17, h=10, view='q2r', ra='mid', eyes='closed')
        hx, hy = info['rh']
        ball = (int(hx) - 2, int(hy) - 5)
    elif k <= 7:
        x, y = [(9, 15), (11, 10), (11, 11)][k - 5]
        L, info = lay(x=x, y=y, view='q2r', ra='none', legs=(1, 1, 1, 1), eyes='focus' if k < 7 else 'angry')
        tip = [(x + 19, y - 4), (x + 19, y - 3), (x + 18, y)][k - 5]
        reach = (x + 13, y + 1, tip[0], tip[1])
        ball = (tip[0] - 2, tip[1] - 6) if k < 7 else (28, 9)
    elif k <= 10:
        x, y = 11, 16
        L, info = lay(x=x, y=y, view='q2r', ra='none', eyes='happy' if k > 8 else 'closed')
        reach = (x + 13, y + 1, 29, 11)
        shear = [0, 0.1, -0.08][k - 8]
        ball = [(28, 15), (28, 23), (29, 30)][k - 8]
    elif k == 11:
        L, info = lay(x=11, y=BY + 2, w=18, h=10, view='q2r', eyes='closed')
        ball = (30, 25)
    elif k == 12:
        L, info = lay(x=11, view='q2r', eyes='happy', ra='up')
        ball = (30, 30)
    else:
        j = k - 13
        x = [9, 6, 3, 0, -2, -5, -7][j]
        s = j % 2
        L, info = lay(x=x, y=BY + s, view='q2r', legs=walk(1 - s), ra='side', eyes='normal')
        hx, hy = info['rh']
        ball = (int(hx) - 2, 26 if s else 30)
    if reach:
        limb(L, reach[0], reach[1], reach[2] - 1, reach[3], 'O', t=3)
    if shear:
        L = L.shear(shear, 12)
    f.blit(L)
    if ball:
        f.art(pick(BASKET, k), *ball)
    if k in (7, 8):
        rim(f)
        if reach and k == 8:
            limb(f, reach[2] - 3, reach[3], reach[2] - 1, reach[3], 'O', t=2)
    if k == 7:
        impact(f, 31, 8)
    if k in (8, 9, 10):
        f.text('DUNK!', 2, 3, 'R' if k % 2 else 'Y')
    if 5 <= k <= 6:
        P.speedlines(f, info['x'] - 1, info['y'] + 3, t, n=3, length=5)


def ball_spin(f, t, n):
    k = t % 16
    right = k < 8
    u = k % 8
    tossing = u >= 6
    ra = 'up' if (right and not tossing) or (not right and u == 7) else 'side'
    la = 'up' if (not right and not tossing) or (right and u == 7) else 'side'
    b = 1 if u in (2, 3) else 0
    info = clawd(f, eyes='focus', look=1 if right else -1, lookv=-1, ra=ra, la=la, y=BY + b, h=12 - b)
    if tossing:
        p = (u - 5) / 3
        bx = lerp(27, 7, p) if right else lerp(7, 27, p)
        by = 12 - 28 * p * (1 - p)
        f.art(pick(BASKET, k), int(bx), int(by))
    else:
        hx, hy = info['rh'] if right else info['lh']
        bx, by = int(hx) - 3, int(hy) - 6
        f.art(BASKET[u % 4], bx, by)
        arc = [['L......L', '........'], ['........', 'L......L']][u % 2]
        f.art(arc, bx - 1, by + 2)
        if u == 0:
            f.art(['.W.', 'WUW', '.W.'], bx + (7 if right else -4), by - 2)


# --------------------------------------------------------------------------- racket & bat sports
def tennis_serve(f, t, n):
    k = t % 16
    ground(f, 'E', 36)
    f.rect(37, 29, 1, 7, 'g'); f.rect(38, 29, 2, 1, 'W'); f.rect(38, 30, 2, 1, 'G')
    for yy in range(31, 36, 2):
        f.rect(38, yy, 2, 1, 'L')
    x, y = 7, BY
    ball = None
    la, ra, eyes, rk, behind, lookv = 'mid', 'side', 'focus', -0.3 * math.pi, False, 0
    if k < 2:
        ball = (x - 7, y + 1 + k)
        eyes = 'normal' if k == 0 else 'focus'
    elif k == 2:
        la, ra, rk = 'up', 'mid', -0.42 * math.pi
        ball = (x - 3, y - 9)
        lookv = -1
    elif k in (3, 4):
        la, ra, rk, behind = 'up', 'up', (-0.95 if k == 3 else -0.85) * math.pi, True
        ball = [(x + 1, y - 14), (x + 5, y - 16)][k - 3]
        lookv = -1
    elif k == 5:
        ra, rk = 'up', -0.55 * math.pi
        ball = (x + 8, y - 14)
        eyes, lookv = 'angry', -1
    elif k < 9:
        ra, rk = 'low', 0.62 * math.pi
        ball = [(x + 17, y - 12), (x + 25, y - 9), (x + 32, y - 6)][k - 6]
    elif k < 14:
        ra, rk, behind = 'high', -0.8 * math.pi, True
        eyes = 'happy'
    elif k == 15:
        ball = (x - 7, y + 1)
    if behind:
        info0 = clawd(Canvas(), x=x, y=y, view='q2r', la=la, ra=ra)
        racket(f, *info0['rh'], rk)
    info = clawd(f, x=x, y=y, view='q2r', la=la, ra=ra, eyes=eyes, lookv=lookv)
    if not behind:
        cx, cy = racket(f, *info['rh'], rk)
        if k == 5:
            impact(f, cx + 1, cy - 3)
    if ball:
        f.art(TENNIS, *ball)
        if 6 <= k <= 8:
            P.speedlines(f, ball[0] - 1, ball[1] - 1, t, n=2, length=6)
    if 9 <= k <= 13:
        f.text('ACE!', 24, 5, 'R' if k % 2 else 'Y')


def pingpong(f, t, n):
    k = t % 12
    # table in perspective (Clawd at the far end, we play from the camera)
    for y in range(18, 36):
        p = (y - 18) / 17
        hw = int(round(11 + p * 8))
        f.rect(20 - hw, y, 2 * hw, 1, 'e')
        f.put(20 - hw, y, 'W'); f.put(19 + hw, y, 'W')
        f.put(20, y, 'W')
    f.rect(9, 18, 22, 1, 'W')
    path = [(31, 12, 2), (28, 16, 2), (26, 21, 2), (25, 28, 3), (26, 32, 3), (29, 34, 4),
            (28, 29, 3), (27, 24, 3), (27, 20, 2), (28, 16, 2), (29, 13, 2), (30, 12, 2)]
    bx, by, bs = path[k]
    sw = {10: 'side', 11: 'high', 0: 'mid'}.get(k, 'side')
    dx = 1 if k in (0, 1, 10, 11) else 0
    L, info = lay(x=BX + dx, y=4, eyes='focus', look=1 if bx > 22 else 0, lookv=1 if by > 24 else 0,
                  ra=sw, la='side')
    hx, hy = info['rh']
    L.rect(int(hx), int(hy) - 3, 1, 3, 'N')
    L.disc(hx + .5, hy - 5, 2.6, 'R')
    for y in range(18, 40):
        L.px[y] = [None] * 40
    f.blit(L)
    # net
    f.rect(6, 23, 28, 1, 'W'); f.rect(6, 24, 28, 1, 'G'); f.rect(6, 22, 1, 3, 'G'); f.rect(33, 22, 1, 3, 'G')
    f.rect(6, 36, 1, 4, 'g'); f.rect(33, 36, 1, 4, 'g')
    if k in (3, 8):
        f.art(['L...L'], bx - 2, by + bs)
    f.rect(bx, by, bs, bs, 'U')
    # our paddle at the bottom
    py = 39 if k != 5 else 37
    pxx = 34 if k != 5 else 32
    f.disc(pxx, py, 6, 'R'); f.ring(pxx, py, 6, 'M')
    if k == 5:
        impact(f, 30, 33)
    if k == 0:
        impact(f, 33, 10)


def baseball(f, t, n):
    k = t % 16
    ground(f, 'N', 36)
    f.art(['.WWW.', 'WWWWW'], 22, 34)
    x, y = 4, BY
    ball = None
    bsize = 3
    eyes, lookv = 'focus', 0
    if k < 8:
        ra = 'high'
        ang = -0.62 * math.pi + 0.06 * math.pi * sin(k, 4)
        if k >= 5:
            ang = -0.7 * math.pi
        behind = True
        if k >= 5:
            ball = [(39, 24), (36, 25), (33, 25)][k - 5]
    elif k == 8:
        ra, ang, behind = 'out', 0.0, False
        ball = (31, 24)
        eyes = 'angry'
    else:
        ra, ang, behind = 'up', -0.8 * math.pi, True
        eyes, lookv = 'happy', -1
        if k <= 12:
            ball = [(31, 15), (33, 8), (35, 3), (36, 0)][k - 9]
            bsize = [3, 2, 2, 1][k - 9]
    if behind:
        info0 = clawd(Canvas(), x=x, y=y, view='q2r', ra=ra)
        bat(f, *info0['rh'], ang)
    info = clawd(f, x=x, y=y, view='q2r', ra=ra, eyes=eyes, lookv=lookv)
    P.hat(f, info, 'helmet', dx=-1)
    if not behind:
        bat(f, *info['rh'], ang)
    if ball:
        if bsize == 3:
            ol(f, BASEBALL, *ball)
        else:
            f.rect(ball[0], ball[1], bsize, bsize, 'W'); f.rect(ball[0] + bsize, ball[1], 1, bsize, 'G')
    if k == 8:
        impact(f, 33, 25)
        f.text('CRACK!', 18, 4, 'R')
    if 9 <= k <= 11:
        f.art(['L', '.', 'L'], ball[0] - 2, ball[1] + 3)
    if k in (13, 15):
        f.art(['.U.', 'UWU', '.U.'], 35, 0)
    elif k == 14:
        f.put(36, 1, 'U')


# --------------------------------------------------------------------------- bowling / golf
def bowling(f, t, n):
    k = t % 20
    f.rect(0, 36, 40, 1, 'N'); f.rect(0, 37, 40, 1, 'n')
    x, y = 1, BY
    pins = (27, 31, 35)
    ball = None
    shear = 0
    ra, eyes, h = 'mid', 'focus', 12
    if k == 0:
        ball = 'hand'
    elif k == 1:
        ra = 'none'
        shear = -0.05
        f.art(BOWL[0], x - 4, y + 6)
    elif k == 2:
        ra, h = 'low', 11
        ball = (x + 19, 31)
    elif k <= 8:
        ra = 'low'
        ball = ([20, 21, 22, 23, 24, 25][k - 3], 31)
        shear = [0, 0.06, -0.06, 0.08, -0.08, 0][k - 3]
        eyes = 'worried' if k < 8 else 'big'
    if k == 9:
        ball = (26, 31)
    elif 10 <= k <= 11:
        ball = (32 + (k - 10) * 5, 31)
    elif k >= 15:
        ball = (40 - (k - 15) * 5, 31)
    if 9 <= k <= 14:
        j = k - 9
        flights = [(-2, -3, 1), (1, -4, 2), (3, -2, 3)]
        for i, px in enumerate(pins):
            vx, vy, r = flights[i]
            xx = px + vx * (j + 1)
            yy = 26 + vy * (j + 1) + (j + 1) * (j + 1) // 2
            PL = Canvas()
            PL.art(rot_art(PIN, (r + j) % 4), xx, min(yy, 29))
            f.blit(outline_layer(PL))
    L = Canvas()
    if 9 <= k <= 14:
        j = k - 9
        info = clawd(L, x=x + 2, y=BY - (3 if j % 2 else 0), la='up' if j % 2 else 'high', ra='up' if j % 2 else 'high',
                     eyes='happy', legs=(1, 1, 1, 1) if j % 2 else (0, 0, 0, 0))
    else:
        info = clawd(L, x=x, y=y + (12 - h), h=h, view='q2r', ra=ra, eyes=eyes)
    if shear:
        L = L.shear(shear, 36)
    if ball == 'hand':
        hx, hy = info['rh']
        L.art(BOWL[0], int(hx) - 1, int(hy) - 3)
    f.blit(L)
    if 9 <= k <= 14:
        j = k - 9
        f.text('STRIKE!', 2, 3, 'R' if j % 2 else 'Y')
        if j == 0:
            impact(f, 29, 30)
    else:
        drop = 0
        if 15 <= k <= 18:
            drop = [-14, -9, -4, -1][k - 15]
            f.rect(25, drop + 25, 14, 1, 'g')
        PL = Canvas()
        for px in pins:
            PL.art(PIN, px - 1, 26 + drop)
        f.blit(outline_layer(PL))
    if ball and ball != 'hand':
        f.art(BOWL[t % 2], *ball)


def golf_putt(f, t, n):
    k = t % 16
    f.rect(0, 36, 40, 2, 'E'); f.rect(0, 36, 40, 1, 'e')
    f.rect(32, 36, 4, 1, 'K')
    wave = k % 4 < 2
    f.rect(36, 17, 1, 19, 'g')
    f.art(['RRRR', 'RRRRR', 'RRR'] if wave else ['RRRRR', 'RRRR', 'RR'], 37, 17)
    x, y = 2, BY
    head = 0
    ball = 24
    eyes = 'focus'
    jump = 0
    if k < 4:
        head = [0, 0, -1, 0][k]
    elif k == 4:
        head = -3
    elif k == 5:
        head = 2
    elif k <= 11:
        head = 1
        ball = [24, 26, 28, 30, 31, 32, 33][k - 5]
        eyes = 'focus' if k < 10 else 'worried'
    else:
        ball = None
        eyes = 'happy'
        jump = 2 if k in (12, 14) else 0
    hold = k < 12
    info = clawd(f, x=x, y=y - jump, view='q2r', ra='up' if not hold else 'side', eyes=eyes,
                 legs=(1, 1, 1, 1) if jump else (0, 0, 0, 0))
    hx, hy = info['rh']
    if hold:
        f.line(hx, hy, hx + head, 34, 'g')
        f.rect(int(hx) + head - 1, 34, 3, 2, 'k')
    else:
        f.line(hx, hy, hx + 3, hy - 9, 'g')
        f.rect(int(hx) + 2, int(hy) - 11, 3, 2, 'k')
        f.text('!', int(hx) + 7, int(hy) - 7, 'R')
    if ball is not None:
        ol(f, ['WW', 'WW'], ball, 34 + (1 if k == 11 else 0))
    if k == 12:
        f.art(['L...L', '.L.L.'], 31, 33)
    if k == 15:
        ol(f, ['WW', 'WW'], 24, 30)


# --------------------------------------------------------------------------- combat
def bag_layer(swing):
    L = Canvas()
    L.rect(32, 0, 1, 10, 'g')
    L.rect(29, 9, 7, 1, 'k')
    L.rect(28, 10, 9, 21, 'V'); L.rect(29, 11, 1, 19, 'B')
    L.rect(28, 13, 9, 1, 'k'); L.rect(28, 27, 9, 1, 'k')
    L.rect(29, 31, 7, 1, 'V')
    k = -swing / 30.0
    return L.shear(k, 0) if swing else L


def boxing_bag(f, t, n):
    k = t % 16
    swing = [0, 1, 1, 1, 1, 0, 0, 2, 4, 3, 1, -1, -2, -1, 0, 0][k]
    f.blit(bag_layer(swing))
    punch = k in (1, 3, 7)
    lean = 0.0
    x = 4
    if k in (5, 6):
        lean = 0.06
    if k == 7:
        lean, x = -0.1, 5
    b = (k // 2) % 2
    L, info = lay(x=x, y=BY + b, view='q2r', ra='out' if punch else 'high', la='high',
                  eyes='angry' if punch else 'focus', legs=walk(k % 2) if not punch else (0, 0, 0, 0))
    hx, hy = info['rh']
    lx, ly = info['lh']
    L.rect(int(lx) - 2, int(ly) - 2, 3, 4, 'R'); L.rect(int(lx) - 2, int(ly) + 1, 3, 1, 'M')
    L.rect(int(hx) - 2, int(hy) - 2, 4, 4, 'R'); L.rect(int(hx) - 3, int(hy) - 2, 1, 4, 'W')
    L.rect(int(hx) - 2, int(hy) + 1, 4, 1, 'M')
    if lean:
        L = L.shear(lean, 36)
    f.blit(L)
    if punch:
        impact(f, 29, int(hy) - 1)
    if k in (7, 8):
        P.burst(f, 18, 8, 'POW')
    if k in (9, 10, 11):
        f.art(P.SWEAT, info['x'] - 3, info['y'] - 2 + (k - 9), flip=True)


def headband(f, info, t, c='R'):
    """Hachimaki tied round the top edge (never across the face)."""
    x, y, w = info['x'], info['y'], info['w']
    f.rect(x, y, w, 1, c)
    tail = pick([['RR.', '.RR'], ['RRR', 'R..'], ['.RR', 'RR.']], t)
    f.art(tail, x - 3, y, cmap={'R': c})


def boards(f, y, broken=0):
    if not broken:
        f.rect(24, y, 14, 2, 'N'); f.rect(24, y + 1, 14, 1, 'n')
        f.rect(24, y + 2, 14, 2, 'N'); f.rect(24, y + 3, 14, 1, 'n')
        return
    d = min(broken, 3)
    for side in (0, 1):
        for j in range(2):
            x0, x1 = (24, 30) if side == 0 else (37, 31)
            yy = y + j * 2
            f.line(x0, yy, x1, yy + d, 'N')
            f.line(x0, yy + 1, x1, yy + 1 + d, 'n')


def karate(f, t, n):
    k = t % 16
    for bx in (24, 34):
        f.rect(bx, 32, 4, 4, 'g'); f.rect(bx, 32, 4, 1, 'G'); f.rect(bx + 1, 34, 2, 1, 'k')
    x, y = 8, BY
    ra, eyes = 'side', 'normal'
    by = 28
    broken = 0
    if k < 2:
        eyes = 'focus' if k else 'normal'
    elif k < 5:
        ra = ('high', 'up', 'up')[k - 2]
        eyes = 'focus'
    elif k == 5:
        ra, eyes = 'out', 'angry'
        broken = 1
    elif k <= 9:
        ra, eyes = 'out' if k < 7 else 'side', 'angry' if k < 7 else 'happy'
        broken = k - 4
    elif k <= 12:
        ra = 'high' if k % 2 else 'side'
        eyes = 'closed'
        broken = 4
    else:
        by = [14, 22, 28][k - 13]
    info = clawd(f, x=x, y=y, view='q2r', ra=ra, eyes=eyes)
    headband(f, info, t)
    boards(f, by, broken)
    if k == 4:
        f.text('HIYA!', 2, 4, 'R')
    if k == 5:
        f.art(['L....', '.L...', '..L..'], 22, 19)
        impact(f, 31, 28)
    if 6 <= k <= 9:
        r = rng(k)
        for i in range(5):
            f.put(31 + r.randint(-5, 5), 26 - (k - 5) * 2 + r.randint(-2, 2), 'N')
    if 10 <= k <= 12:
        hx, hy = info['rh']
        f.art(['W.W', '.W.'] if k % 2 else ['.W.', 'W.W'], int(hx), int(hy) - 6, cmap={'W': 'S'})


def sumo(f, t, n):
    k = t % 16
    f.rect(0, 36, 40, 1, 'y'); f.rect(0, 37, 40, 1, 'N')
    side = 0 if k < 8 else 1
    u = k % 8
    x, w, y, h = 10, 20, BY, 12
    lift = u in (1, 2, 3)
    stomp = u == 4
    L = Canvas()
    legs = (3, 3, 0, 0) if (lift and side == 0) else (0, 0, 3, 3) if (lift and side == 1) else (0, 0, 0, 0)
    if stomp:
        y, h = BY + 2, 10
    clawd(L, x=x, y=y, w=w, h=h, legs=legs, eyes='angry' if lift or stomp else 'focus',
          la='low' if not (lift and side == 0) else 'out', ra='low' if not (lift and side == 1) else 'out')
    btop = max(y + 9, y + h - 2)
    L.rect(x, btop, w, y + h - btop, 'V'); L.rect(x + w // 2 - 2, y + h, 4, 2, 'V')
    L.rect(x + w // 2 - 1, y - 2, 3, 2, 'k'); L.put(x + w // 2, y - 3, 'k')
    if lift:
        hgt = [0, 4, 8, 10][u]
        if side == 0:
            limb(L, x - 1, y + h - 3, x - 6, y + h - 3 - hgt, 'O', t=3)
        else:
            limb(L, x + w - 2, y + h - 3, x + w + 3, y + h - 3 - hgt, 'O', t=3)
        L = L.shear(0.06 if side == 0 else -0.06, 36)
    f.blit(L.shift(0, 1) if stomp else L)
    if stomp or u == 5:
        p = 0.2 if stomp else 0.6
        P.dust(f, 5, GROUND, p); P.dust(f, 33, GROUND, p, flip=True)
    if stomp:
        f.text('STOMP!', 9, 3, 'R')
        f.art(['L.L.L'], 4 + side * 26, 30)


def fencing(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    bal_y = 23
    if k >= 10:
        bal_y = 23 + [16, 12, 8, 4, 2, 0][k - 10]
    if k < 7 or k >= 10:
        bob = 1 if (k // 2) % 2 else 0
        f.line(34, bal_y + bob + 6, 34, 35, 'k')
        f.rect(33, 35, 3, 1, 'g')
        f.art(BALLOON, 32, bal_y + bob)
    if k == 7:
        P.burst(f, 33, 26, 'POP', c='U', c2='Z')
    elif k in (8, 9):
        r = rng(k)
        for i in range(6):
            f.put(33 + r.randint(-6, 6), 26 + (k - 7) * 3 + r.randint(-4, 4), 'Z')
        f.rect(33, 35, 3, 1, 'g')
    xs = [0, 0, 2, 3, 5, 6, 8, 8, 8, 6, 4, 2, 1, 0, 0, 0]
    x = xs[k]
    lunge = k in (6, 7, 8)
    salute = k in (12, 13)
    s = k % 2 if k in (2, 3, 4, 5, 9, 10, 11) else 0
    if lunge:
        info = clawd(f, x=x, y=BY + 1, h=11, view='q2r', ra='out', la='up', legdx=(-2, -1, 2, 3), eyes='angry')
        hx, hy = info['rh']
        f.line(hx, hy, hx + 9, hy, 'G'); f.rect(int(hx), int(hy) - 1, 1, 3, 'U')
    elif salute:
        info = clawd(f, x=x, view='q2r', ra='up', eyes='closed')
        hx, hy = info['rh']
        f.line(hx, hy, hx, hy - 9, 'G'); f.rect(int(hx) - 1, int(hy), 3, 1, 'U')
    else:
        info = clawd(f, x=x, y=BY + s, view='q2r', ra='mid', la='up', legs=walk(s) if s else (0, 0, 0, 0),
                     eyes='focus')
        hx, hy = info['rh']
        f.line(hx, hy, hx + 9, hy - 1, 'G'); f.rect(int(hx), int(hy) - 1, 1, 3, 'U')


# --------------------------------------------------------------------------- gym
def barbell_art(f, cx, y):
    f.rect(cx - 16, y, 32, 1, 'g'); f.rect(cx - 16, y - 1, 32, 1, 'G')
    for sx in (-1, 1):
        px = cx + sx * 13
        f.rect(px - (2 if sx < 0 else 0), y - 5, 3, 11, 'R'); f.rect(px - (2 if sx < 0 else 0), y - 5, 3, 1, 'Z')
        ix = px + (1 if sx < 0 else -2)
        f.rect(ix, y - 3, 1, 7, 'B')
        f.rect(cx + sx * 16 - (1 if sx > 0 else 0), y - 1, 1, 2, 'G')


def barbell(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    x = BX
    tremble = 0
    if k in (0, 1):
        y, h, bar_y, eyes = BY + 3, 10, 31, 'focus' if k else 'normal'
    elif k in (2, 3):
        y, h, bar_y, eyes = BY + 1, 11, [29, 27][k - 2], 'angry'
        tremble = k % 2
    elif k in (4, 5):
        y, h, bar_y, eyes = BY, 12, BY + 6, 'angry'
    elif k == 6:
        y, h, bar_y, eyes = BY + 2, 10, BY + 7, 'closed'
    elif k <= 11:
        y, h, bar_y, eyes = BY, 12, BY - 6, 'squint' if k < 10 else 'happy'
        tremble = 1 if k in (7, 9) else -1 if k in (8, 10) else 0
    elif k == 12:
        y, h, bar_y, eyes = BY, 12, 31, 'big'
    elif k == 13:
        y, h, bar_y, eyes = BY, 12, 30, 'happy'
    else:
        y, h, bar_y, eyes = BY + (k - 13), 12 - (k - 13), 31, 'happy'
    xx = x + tremble
    overhead = bar_y < y
    arms = 'none'
    if overhead:
        arms = 'up'
    elif k in (12, 13):
        arms = 'up' if k == 12 else 'high'
    if not overhead:
        barbell_art(f, 20 + (tremble if arms == 'none' else 0), bar_y)
    info = clawd(f, x=xx, y=y, h=h, eyes=eyes, la=arms, ra=arms, legdx=(-tremble, 0, 0, tremble))
    if overhead:
        barbell_art(f, 20 + tremble, bar_y)
        f.rect(xx - 3, bar_y + 1, 3, y - bar_y, 'O'); f.rect(xx + 16, bar_y + 1, 3, y - bar_y, 'O')
    elif arms == 'none':
        top = y + 4
        f.rect(xx - 3, top, 3, max(1, bar_y - top + 1), 'O'); f.rect(xx + 16, top, 3, max(1, bar_y - top + 1), 'O')
    if 7 <= k <= 10:
        f.art(P.SWEAT, xx + 19, y + (k % 3))
        f.art(P.SWEAT, xx - 5, y + 1 + (k + 1) % 3, flip=True)
    if 2 <= k <= 5:
        f.art(P.VEIN, xx + 11, y - 5)
    if k == 12:
        P.dust(f, 2, GROUND, 0.2); P.dust(f, 36, GROUND, 0.2, flip=True)
        f.text('CLANG', 11, 4, 'g')


def slab(f, px, py, d, nrm, length=14, thick=5):
    for si in range(length * 2):
        s = si / 2 + .25
        for wi in range(thick * 2):
            w = wi / 2 + .25
            xx = px + d[0] * s + nrm[0] * w
            yy = py + d[1] * s + nrm[1] * w
            edge = wi in (0, 1, thick * 2 - 2, thick * 2 - 1)
            c = 'g' if edge and int(s) % 2 == 0 else 'k'
            f.put(math.floor(xx), math.floor(yy), c)


def tire_flip(f, t, n):
    k = t % 16
    phis = [0, 0, 25, 50, 72, 90, 120, 150, 180]
    scroll = 0
    if k <= 8:
        phi = phis[k]
    else:
        phi = 180
        scroll = [3, 6, 9, 12, 14, 16, 18][k - 9]
    ticks(f, scroll, y=37, c='G', gap=6)
    ground(f, 'g', 36)
    a = math.radians(phi)
    if phi <= 90:
        slab(f, 30 - scroll, 36, (-math.cos(a), -math.sin(a)), (math.sin(a), -math.cos(a)))
    else:
        slab(f, 35 - scroll, 36, (-math.cos(a), -math.sin(a)), (-math.sin(a), math.cos(a)))
    if k <= 1:
        clawd(f, x=0, y=BY + 2, h=10, view='q2r', ra='low', eyes='focus' if k else 'normal')
    elif k <= 4:
        x = [2, 4, 6][k - 2]
        clawd(f, x=x, y=BY + (1 if k == 2 else 0), h=11 if k == 2 else 12, view='q2r',
              ra=['low', 'mid', 'high'][k - 2], eyes='angry')
        f.art(P.VEIN, x + 12, BY - 6)
    elif k <= 8:
        x = 9 if k == 5 else 11
        clawd(f, x=x, view='q2r', ra='out' if k < 8 else 'up', eyes='angry' if k < 8 else 'happy')
        if k == 8:
            P.dust(f, 30, GROUND, 0.3); P.dust(f, 39, GROUND, 0.3, flip=True)
            f.text('THUD', 25, 10, 'g')
    else:
        j = k - 9
        x = int(round(lerp(11, 0, (j + 1) / 7)))
        s = j % 2
        clawd(f, x=x, y=BY + s, view='q2r', legs=walk(s), eyes='happy' if j < 3 else 'normal')


DUMB_H = ['kk..kk', 'kkggkk', 'kk..kk']


def dumbbell_curl(f, t, n):
    k = t % 16
    rep, u = divmod(k, 4)
    left = rep % 2 == 0
    pose = ['down', 'high', 'wave', 'high'][u]
    la = pose if left else 'down'
    ra = pose if not left else 'down'
    strain = u == 2
    info = clawd(f, la=la, ra=ra, eyes='angry' if strain else 'focus' if u else 'normal',
                 y=BY + (1 if strain else 0), h=12 - (1 if strain else 0))
    x, y = info['x'], info['y']
    for side, st in (('l', la), ('r', ra)):
        if st == 'down':
            cx = x - 2 if side == 'l' else x + 17
            f.art(DUMB_H, cx - 3, y + 10)
        elif st == 'high':
            cx = x - 4 if side == 'l' else x + 19
            f.art(DUMB_H, cx - 3, y + 1)
        else:
            hx, hy = info['lh'] if side == 'l' else info['rh']
            f.art(DUMB_H, int(hx) - 3, int(hy) - 3)
    f.text(str(rep + 1), 19, 4, 'g')
    if strain:
        P.rising(f, ['LL', 'LL'], t, n, 26, 18, count=1, height=4, jitter=0)
        if rep >= 2:
            f.art(P.SWEAT, x + (17 if left else -3), y - 1, flip=not left)


def pushups(f, t, n):
    k = t % 12
    rep, u = divmod(k, 4)
    depth = [0, 3, 5, 3][u]
    if rep == 2:
        depth = [0, 3, 5, 5][u]
    x, y = BX, 19 + depth
    trem = 1 if rep == 2 and u == 3 else 0
    ground(f, 'G', 36)
    info = clawd(f, x=x + trem, y=y, leg_h=0, la='none', ra='none', top=True,
                 eyes='closed' if depth == 5 else 'focus' if rep < 2 else 'angry', lookv=1 if depth else 0)
    xx = x + trem
    if depth == 0:
        f.rect(xx - 3, y + 4, 3, 36 - (y + 4), 'O'); f.rect(xx + 16, y + 4, 3, 36 - (y + 4), 'O')
    elif depth == 3:
        f.rect(xx - 4, y + 4, 4, 2, 'O'); f.rect(xx - 4, y + 6, 3, 36 - (y + 6), 'O')
        f.rect(xx + 16, y + 4, 4, 2, 'O'); f.rect(xx + 17, y + 6, 3, 36 - (y + 6), 'O')
    else:
        f.rect(xx - 6, y + 3, 6, 2, 'O'); f.rect(xx - 6, y + 5, 2, 36 - (y + 5), 'O')
        f.rect(xx + 16, y + 3, 6, 2, 'O'); f.rect(xx + 20, y + 5, 2, 36 - (y + 5), 'O')
    f.text(str(rep + 1), 19, 6, 'g')
    if rep == 2:
        f.art(P.SWEAT, xx + 17, y - 4 + u)
        f.art(P.SWEAT, xx - 3, y - 3 + (u + 1) % 4, flip=True)
    if depth == 5:
        P.dust(f, xx - 9, GROUND, 0.2); P.dust(f, xx + 24, GROUND, 0.2, flip=True)


def squats(f, t, n):
    k = t % 12
    rep_, u = divmod(k, 4)
    d = [0, 2, 3, 2][u]
    ground(f, 'G', 36)
    x, y = BX, BY + d
    leg_h = 3 - d if d < 3 else 1
    spread = (-d, -(d // 2), d // 2, d)
    info = clawd(f, x=x, y=y, leg_h=3 if d == 0 else max(1, 36 - (y + 12)), legdx=spread, la='high', ra='high',
                 eyes='angry' if d == 3 else 'focus' if d else 'normal')
    if d == 3:
        f.rect(x - 2, y + 10, 3, 2, 'O'); f.rect(x + 15, y + 10, 3, 2, 'O')
    lag = 1 if u == 2 else 0
    mini(f, x + 4, y - 8 - 2 * lag, eyes='happy', la='up' if k % 2 else 'high', ra='high' if k % 2 else 'up',
         legs=(0, 0, 0, 0), body='O', shade='o')
    if lag:
        f.art(['L....L'], x + 5, y - 2)
    f.text(str(rep_ + 1), 3, 4, 'g')
    if d == 3:
        f.art(P.SWEAT, x + 18, y - 1)
        f.art(P.SWEAT, x - 3, y, flip=True)
    if u == 0 and k:
        f.text('GO!', 27, 4, 'Z')


def pullups(f, t, n):
    k = t % 12
    f.rect(4, 6, 2, 30, 'g'); f.rect(34, 6, 2, 30, 'g')
    ground(f, 'G', 36)
    ys = [15, 15, 12, 8, 4, 4, 6, 10, 15, 15, 15, 15]
    y = ys[k]
    swing = [0, 1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 1][k]
    up = y <= 6
    if up:
        f.rect(4, 7, 32, 2, 'g'); f.rect(4, 7, 32, 1, 'G')
    L, info = lay(x=BX + swing, y=y, la='none', ra='none', legs=(0, 0, 0, 0),
                  eyes='happy' if k in (4, 5) else 'angry' if 2 <= k <= 3 else 'normal' if not up else 'focus',
                  legdx=(swing, swing, swing, swing))
    xx = BX + swing
    if up:
        L.rect(xx - 3, y + 2, 3, 6, 'O'); L.rect(xx + 16, y + 2, 3, 6, 'O')
    else:
        L.rect(xx - 2, 8, 2, y + 6 - 8, 'O'); L.rect(xx + 16, 8, 2, y + 6 - 8, 'O')
    f.blit(L)
    if not up:
        f.rect(4, 7, 32, 2, 'g'); f.rect(4, 7, 32, 1, 'G')
    if up:
        f.rect(xx - 3, 6, 3, 3, 'O'); f.rect(xx + 16, 6, 3, 3, 'O')
    else:
        f.rect(xx - 2, 6, 2, 3, 'O'); f.rect(xx + 16, 6, 2, 3, 'O')
    if k in (4, 5):
        P.sparkles(f, k, 4, [(10, 2), (30, 3)])
    if k in (2, 3):
        f.art(P.SWEAT, xx + 18, y + 2)


def jump_rope(f, t, n):
    k = t % 8
    th = 2 * math.pi * k / 8
    ground(f, 'G', 36)
    hop = [0, 0, 1, 3, 4, 3, 1, 0][k]
    y = BY - hop
    hand_y = y + 7
    ymid = 21 - 16 * math.cos(th)
    front = math.sin(th) < 0

    def rope(c='k'):
        x0, x1 = BX - 4, BX + 20
        for xx in range(x0, x1 + 1):
            q = (xx - (x0 + x1) / 2) / ((x1 - x0) / 2)
            yy = hand_y + (ymid - hand_y) * (1 - q * q)
            f.put(xx, int(round(yy)), c)
    rope('k' if front else 'g')
    info = clawd(f, y=y, la='side', ra='side', legs=(1, 1, 1, 1) if hop >= 3 else (0, 0, 0, 0),
                 eyes='happy' if hop >= 3 else 'normal', look=0)
    for hx in (BX - 5, BX + 20):
        f.rect(hx, hand_y - 1, 2, 3, 'R')
    if hop == 0 and k == 0:
        P.dust(f, BX - 2, GROUND, 0.2); P.dust(f, BX + 17, GROUND, 0.2, flip=True)


def hula(f, t, n):
    k = t % 8
    phi = 2 * math.pi * k / 8
    cx, cy = 20 + 3 * math.cos(phi), 29
    sway = -int(round(2 * math.cos(phi)))
    pts = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        px, py = cx + 12 * math.cos(a), cy + 3.2 * math.sin(a)
        stripe = int((i + k * 3) // 6) % 2
        pts.append((px, py, math.sin(a) > 0, 'Z' if stripe else 'U'))
    for px, py, fr, c in pts:
        if not fr:
            f.put(px, py, c)
    clawd(f, x=BX + sway, la='up', ra='up', eyes='happy', y=BY + (1 if k % 4 == 2 else 0),
          legdx=(sway, 0, 0, sway))
    for px, py, fr, c in pts:
        if fr:
            f.put(px, py, c)


def yoga_tree(f, t, n):
    k = t % 16
    f.rect(5, 36, 30, 1, 'P'); f.rect(5, 37, 30, 1, 'p')
    wob = [0, 0.02, 0.03, 0.02, 0, -0.02, -0.03, -0.02, 0, 0.08, -0.1, 0.07, -0.03, 0, 0, 0][k]
    breath = 1 if k in (2, 3, 4, 5) else 0
    shaky = k in (9, 10, 11)
    x, y = BX, BY - breath
    L, info = lay(x=x, y=y, legs=(3, 3, 0, 0), la='none', ra='none',
                  eyes='worried' if shaky else 'closed')
    L.rect(x + 1, y + 12, 7, 2, 'O'); L.rect(x + 7, y + 12, 2, 2, 'o')
    limb(L, x + 1, y + 2, x - 4, y - 6, 'O', t=3)
    limb(L, x + 12, y + 2, x + 17, y - 6, 'O', t=3)
    grow = 0 if shaky else min(3, (k + 2) // 3) if k < 9 else 3
    leaves = [['.E', 'EE'], ['E.E', 'EEE', '.e.'], ['.E.E', 'EEEE', '.EEe', '..e.']]
    if grow:
        lf = leaves[grow - 1]
        L.art(lf, x - 6, y - 7 - len(lf) + 2)
        L.art(lf, x + 18, y - 7 - len(lf) + 2, flip=True)
    f.blit(L.shear(wob, 36) if wob else L)
    if shaky:
        f.art(P.SWEAT, x + 18, y + 2 + (k - 9))
        f.art(['.E', 'E.'], x - 6 + (k - 9), y - 6 + (k - 9) * 4)
        f.art(['E.', '.E'], x + 21 - (k - 9), y - 5 + (k - 9) * 4)
    if k in (6, 14):
        f.art(['.W.', 'WUW', '.W.'], 31 if k == 6 else 6, 6)


def jumping_jacks(f, t, n):
    k = t % 8
    u = k % 4
    ground(f, 'G', 36)
    if u == 0:
        info = clawd(f, la='down', ra='down', legdx=(1, 1, -1, -1), eyes='normal')
    elif u == 2:
        L, info = lay(y=BY - 3, la='none', ra='none', legdx=(-3, -2, 2, 3), legs=(0, 1, 1, 0), eyes='happy')
        x, y = BX, BY - 3
        limb(L, x - 2, y + 3, x - 6, y - 4, 'O', t=3)
        limb(L, x + 15, y + 3, x + 19, y - 4, 'O', t=3)
        f.blit(L)
        f.art(['.S', 'SS'], x - 9, y - 6); f.art(['S.', 'SS'], x + 24, y - 6)
    else:
        info = clawd(f, y=BY - 1, la='high', ra='high', legdx=(-1, -1, 1, 1), eyes='normal')
    f.text(str(k // 4 + 1) if u != 2 else '', 19, 4, 'g')


# --------------------------------------------------------------------------- cardio & wheels
def treadmill(f, t, n):
    k = t % 16
    f.rect(1, 34, 31, 2, 'k')
    for i in range(6):
        xx = 2 + (i * 6 - k * 3) % 30
        f.rect(xx, 34, 2, 1, 'g')
    f.rect(0, 34, 1, 2, 'G'); f.rect(31, 34, 1, 2, 'G')
    f.rect(1, 36, 31, 1, 'g')
    f.rect(31, 16, 2, 18, 'g')
    f.rect(26, 21, 8, 1, 'g')
    f.rect(27, 12, 10, 5, 'k'); f.rect(28, 13, 8, 3, 'b')
    for j in range(3):
        f.rect(29 + j * 2, 14, 1, 1 + (1 if (k + j) % 3 == 0 else 0), 'C')
    drift = [6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 2, 3, 5, 6][k]
    s = k % 2
    L, info = lay(x=drift, y=18 + s, view='q2r', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
                  legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1), ra='high' if s else 'low',
                  eyes='worried' if 8 <= k <= 11 else 'focus')
    f.blit(L.shear(-0.08, 34))
    f.art(P.SWEAT, drift - 3 - (k % 3), 17 + (k % 3), flip=True)
    if k >= 12:
        P.speedlines(f, drift - 1, 21, t, n=3, length=4)


TREE = ['.EEE.', 'EEeEE', 'EEEEE', '.EeE.', '..N..', '..N..']


def jogging(f, t, n):
    k = t % 16
    off = k * 2
    for i in range(3):
        tx = 6 + i * 16 - off % 16 + (0 if i % 2 else 0)
        if (i + (off // 16)) % 2 == 0:
            f.art(TREE, tx, 20)
            f.rect(tx + 2, 26, 1, 4, 'N')
        else:
            f.art(['.EE.', 'EEEE'], tx, 28)
    f.rect(0, 30, 40, 1, 'e')
    ticks(f, off, y=37, c='G', gap=8, w=4)
    ground(f, 'G', 36)
    s = (k // 2) % 2
    info = clawd(f, x=10, y=BY + s, view='q2r', legs=walk((k // 2) % 2), ra='mid' if s else 'low',
                 la='mid' if not s else 'low', eyes='happy' if k < 8 else 'normal')
    x, y = info['x'], info['y']
    P.hat(f, info, 'cap', dx=1)
    if k % 4 == 0:
        f.art(['LL', 'LL'], x + 18, y + 3)
    elif k % 4 == 1:
        f.art(['.L', 'L.'], x + 20, y + 2)
    f.art(P.SWEAT, x - 3 - (k % 4) // 2, y + 4 + (k % 4), flip=True)


def wheel(f, cx, cy, r, ang, c='k', spoke='g'):
    f.ring(cx, cy, r, c, t=1.2)
    for j in range(2):
        a = ang + j * math.pi / 2
        dx, dy = math.cos(a) * (r - 1.5), math.sin(a) * (r - 1.5)
        f.line(cx - dx - .5, cy - dy - .5, cx + dx - .5, cy + dy - .5, spoke)
    f.rect(int(cx) - 1, int(cy) - 1, 2, 2, 'G')


def cycling(f, t, n):
    k = t % 8
    ticks(f, k * 4, y=37, c='G', gap=8, w=4)
    ground(f, 'g', 36)
    rx, ry, fx, fy = 9, 30, 31, 30
    cxk, cyk = 20, 30
    a = 2 * math.pi * k / 8
    p1 = (cxk + 3 * math.cos(a), cyk + 3 * math.sin(a))
    p2 = (cxk - 3 * math.cos(a), cyk - 3 * math.sin(a))
    # far leg (shaded) behind the bike
    limb(f, 22, 24, p2[0], p2[1], 'o', t=2)
    wheel(f, rx + .5, ry + .5, 5.5, -a * 1.2)
    wheel(f, fx + .5, fy + .5, 5.5, -a * 1.2)
    for (x0, y0, x1, y1) in ((rx, ry, cxk, cyk), (rx, ry, 17, 24), (17, 24, cxk, cyk), (17, 24, 28, 23),
                             (cxk, cyk, 28, 23), (28, 23, fx, fy), (28, 23, 29, 20)):
        f.line(x0, y0, x1, y1, 'R')
    f.rect(29, 20, 3, 1, 'k')
    f.rect(15, 23, 5, 1, 'k')
    b = 1 if k % 4 < 2 else 0
    info = clawd(f, x=11, y=11 + b, view='q2r', leg_h=0, ra='low', eyes='happy' if k < 4 else 'focus')
    P.hat(f, info, 'helmet', dx=-1)
    limb(f, 23, 22 + b, p1[0], p1[1], 'O', t=2)
    f.rect(int(p1[0]) - 1, int(p1[1]) + 1, 3, 1, 'g')
    P.speedlines(f, 3, 14, t, n=3, length=5)


def unicycle(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    phi = 2 * math.pi * k / 16
    cx = 20 + 4 * math.sin(phi)
    vel = math.cos(phi)
    lean = -0.12 * vel
    ang = (cx - 20) / 3.0
    L = Canvas()
    wheel(L, cx, 31, 4.6, ang)
    L.rect(int(cx) - 1, 23, 2, 8, 'g')
    L.rect(int(cx) - 3, 23, 6, 1, 'k')
    pa = ang
    for sgn, c in ((1, 'O'), (-1, 'o')):
        px, py = cx + sgn * 2 * math.cos(pa), 31 + sgn * 2 * math.sin(pa)
        limb(L, int(cx) - 1 + sgn * 2, 23, px, py, c, t=2)
    arms = [('up', 'out'), ('wave', 'high'), ('out', 'up'), ('high', 'wave')][(k // 2) % 4]
    clawd(L, x=int(round(cx)) - 8, y=11, leg_h=0, la=arms[0], ra=arms[1], eyes='worried' if abs(vel) > .5 else 'focus')
    L = L.shear(lean, 31)
    f.blit(L)
    if abs(vel) > 0.7:
        f.art(P.SWEAT, int(cx) + (10 if vel < 0 else -12), 10 + k % 3, flip=vel > 0)


BOARD = {
    'A': ['N..............N', '.NNNNNNNNNNNNNN.', '.nnnnnnnnnnnnnn.', '..gg........gg..'],
    'B': ['.kkkkkkkkkkkkkk.', '.kkkkkkkkkkkkkk.', '.NNNNNNNNNNNNNN.'],
    'C': ['..gg........gg..', '.nnnnnnnnnnnnnn.', '.NNNNNNNNNNNNNN.', 'N..............N'],
    'D': ['.NNNNNNNNNNNNNN.', '.RRRUURRRRUURRR.', '.NNNNNNNNNNNNNN.'],
    'E': ['.............NN', '...........NN.G', '.........NN..G.', '.......NN......', '.....NN........',
          '...NN..........', 'NNN............'],
}


def kickflip(f, t, n):
    k = t % 16
    ticks(f, k * 3, y=37, c='G', gap=8, w=3)
    ground(f, 'g', 36)
    bx = 12
    cy = [18, 18, 18, 18, 20, 13, 8, 6, 8, 12, 19, 18, 18, 18, 18, 18][k]
    board = {5: 'E', 6: 'B', 7: 'C', 8: 'D', 9: 'A'}.get(k, 'A')
    by = {5: 28, 6: 21, 7: 19, 8: 21, 9: cy + 14, 10: 33}.get(k, 32)
    sq = k in (4, 10)
    tuck = 5 <= k <= 8
    info = clawd(f, x=12, y=cy, h=10 if sq else 12, w=17 if sq else 16, view='q2r',
                 legs=(2, 2, 2, 2) if tuck else (0, 0, 0, 0), la='up' if tuck else 'side',
                 ra='up' if 6 <= k <= 8 else 'mid', eyes='focus' if k < 9 else 'happy',
                 leg_h=3 if not sq else 3)
    f.art(BOARD[board], bx, by)
    if k == 10:
        P.dust(f, 10, GROUND, 0.2); P.dust(f, 29, GROUND, 0.2, flip=True)
    if 11 <= k <= 14:
        f.text('RAD!', 24, 6, 'R' if k % 2 else 'Y')
    if k in (6, 7, 8):
        f.art(['L', 'L', '.', 'L'], bx - 3, by - 2)
        f.art(['L', '.', 'L', 'L'], bx + 15, by - 2)


# --------------------------------------------------------------------------- water
def water(f, top, k, x0=0, x1=G, speed=1):
    f.rect(x0, top, x1 - x0, G - top, 'B')
    for x in range(x0, x1):
        if (x + k * speed) % 6 in (0, 1):
            f.put(x, top, 'C')
        else:
            f.put(x, top, 'S') if (x + k * speed) % 6 == 3 else None
    r = rng(9)
    for i in range(4):
        xx = (r.randint(0, 39) - k * speed) % 40
        if x0 <= xx < x1:
            f.rect(xx, top + 3 + i * 2, 2, 1, 'C')


STROKE = [(6, -2), (12, -5), (18, -1), (20, 5), (15, 11), (9, 12), (4, 10), (2, 5)]


STROKE = [(6, -2), (12, -5), (18, -1), (20, 5), (15, 11), (9, 12), (4, 10), (2, 5)]
SWIMCAP = ['..UUUUUUUUUUUU..', '.UUUUUUUUUUUUUU.', 'YYYYYYYYYYYYYYYY']


def swim_laps(f, t, n):
    k = t % 16
    surf = 27
    for i in range(14):
        xx = (i * 3 - k * 2) % 42 - 1
        f.rect(xx, surf - 2, 2, 2, 'R' if i % 2 else 'W')
    f.rect(0, surf - 1, 40, 1, 'G')
    u = k % 8
    bob = 1 if u in (2, 3, 6, 7) else 0
    breathe = k in (12, 13)
    x, y = 10, 17 + bob
    L = Canvas()
    fx_, fy_ = STROKE[(u + 4) % 8]
    limb(L, x + 6, y + 4, x + fx_ - 2, y + fy_, 'o', t=3)
    clawd(L, x=x, y=y, view='q2r', ra='none', la='none', leg_h=0,
          eyes='happy' if breathe else 'normal', tilt=1 if breathe else 0)
    L.art(SWIMCAP, x, y - 3)
    hx_, hy_ = STROKE[u]
    limb(L, x + 12, y + 4, x + hx_, y + hy_, 'O', t=3)
    f.blit(L)
    f.rect(0, surf, 40, 13, 'B')
    for x_ in range(40):
        if (x_ + k * 2) % 5 in (0, 1):
            f.put(x_, surf, 'C')
        elif (x_ + k * 2) % 5 == 3:
            f.put(x_, surf, 'S')
    for i in range(3):
        f.rect((7 + i * 13 - k * 2) % 40, surf + 4 + i * 3, 3, 1, 'C')
    if u in (3, 4):
        f.art(['W.W', '.W.', 'WWW'] if u == 3 else ['.W.', 'W.W'], x + 19, surf - 3)
    foam = pick([['W.W.', '.WWW', 'WWWW'], ['.W.W', 'WWW.', 'WWWW']], k)
    ol(f, foam, 4 - (k % 2), surf - 2, oc='C')
    if breathe:
        f.art(['.LL', 'LLL'], 29, 12 - (k - 12) * 2)


def diving(f, t, n):
    k = t % 24
    surf = 32
    water(f, surf, k)
    f.rect(0, 22, 21, 2, 'W'); f.rect(0, 24, 21, 1, 'G'); f.rect(20, 22, 1, 2, 'G')
    f.rect(3, 25, 3, 7, 'g')
    if k < 3:
        s = k % 2
        clawd(f, x=[-14, -6, 2][k], y=7 + s, view='q2r', legs=walk(s), eyes='happy')
    elif k == 3:
        clawd(f, x=4, y=10, h=10, w=17, view='q2r', eyes='closed')
    elif k == 4:
        clawd(f, x=6, y=4, view='q2r', la='up', ra='up', legs=(1, 1, 1, 1), eyes='happy')
    elif k == 5:
        clawd(f, x=9, y=3, view='front', la='up', ra='up', legs=(1, 1, 1, 1), eyes='closed')
    elif k <= 8:
        rot, cx, cy = [(1, 22, 10), (2, 26, 18), (2, 28, 28)][k - 6]
        L, info = lay(x=cx - 8, y=cy - 6, la='up', ra='up', eyes='closed' if k < 8 else 'squint')
        L = L.rot90(rot, cx, cy)
        if k == 6:
            P.speedlines(f, 14, 4, t, n=2, length=4)
        f.blit(L)
        if k == 8:
            water(f, surf, k)
    elif k <= 10:
        r = rng(4)
        hgt = 9 if k == 9 else 5
        for i in range(12):
            a = math.pi * (0.1 + 0.8 * i / 11)
            rr = hgt * (0.6 + 0.4 * r.random())
            f.rect(int(28 + math.cos(a) * rr * 1.2), int(surf - math.sin(a) * rr), 2, 2, 'W' if i % 2 else 'C')
        f.ring(28, surf + 2, 4 + (k - 9) * 3, 'S')
    elif k <= 12:
        f.ring(28, surf + 2, 9 + (k - 11) * 2, 'S')
        if k == 12:
            clawd(f, x=20, y=23, eyes='normal', la='none', ra='none')
            water(f, surf, k)
    else:
        j = k - 13
        xx = int(round(lerp(20, -16, j / 10)))
        clawd(f, x=xx, y=23 - (j % 2), view='q2l', eyes='happy', ra='up' if j % 2 else 'high', la='none')
        water(f, surf, k)
        f.art(['W.W', '.W.'], xx + 17, surf - 2) if j % 2 else None
        if j < 3:
            f.text('10', 30, 4, 'Y'); f.box(28, 2, 11, 9, 'g')
    # board flexes under the take-off
    if k == 3:
        f.rect(14, 22, 7, 3, None); f.rect(14, 24, 7, 2, 'W'); f.rect(14, 26, 7, 1, 'G')


TARGET_C = (34, 26)


def target(f):
    cx, cy = TARGET_C
    f.rect(cx - 4, cy + 4, 1, 36 - cy - 4, 'N'); f.rect(cx + 4, cy + 4, 1, 36 - cy - 4, 'N')
    f.disc(cx + .5, cy + .5, 6, 'W'); f.ring(cx + .5, cy + .5, 6, 'G')
    f.disc(cx + .5, cy + .5, 4.6, 'B')
    f.disc(cx + .5, cy + .5, 3.2, 'R')
    f.disc(cx + .5, cy + .5, 1.8, 'U')


def archery(f, t, n):
    k = t % 16
    ground(f, 'E', 36)
    target(f)
    x, y = 0, BY
    draw = [0, 0, 1, 2, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0][k]
    eyes = 'focus' if 2 <= k <= 6 else 'happy' if 9 <= k <= 13 else 'normal'
    info = clawd(f, x=x, y=y, view='q2r', ra='out', eyes=eyes)
    hx, hy = info['rh']
    bx = int(hx) + 1
    top, bot = y - 1, y + 13
    bend = 2 + draw // 2
    for yy in range(top, bot + 1):
        q = (yy - (top + bot) / 2) / ((bot - top) / 2)
        f.put(bx + int(round(bend * (1 - q * q))), yy, 'N')
    nock = bx - draw * 2
    f.line(bx, top, nock, int(hy), 'G'); f.line(nock, int(hy), bx, bot, 'G')
    arrow_x = None
    if k < 7 or k == 15:
        arrow_x = nock
    elif k in (7, 8):
        arrow_x = [nock + 12, nock + 22][k - 7]
    if arrow_x is not None:
        ay = int(hy)
        f.rect(arrow_x, ay, 11, 1, 'n'); f.rect(arrow_x + 11, ay, 1, 1, 'g')
        f.art(['R.', '.R', 'R.'], arrow_x - 1, ay - 1)
        if k in (7, 8):
            P.speedlines(f, arrow_x - 2, ay - 3, t, n=2, length=5)
    if 9 <= k <= 14:
        cx, cy = TARGET_C
        wob = [-1, 1, -1, 0, 0, 0][k - 9]
        f.rect(cx - 7, cy, 7, 1, 'n')
        f.art(['R.', '.R', 'R.'], cx - 9, cy - 1 + wob)
        if k == 9:
            impact(f, cx, cy)
        if k <= 13:
            f.text('BULLSEYE', 4, 3, 'R' if k % 2 else 'Y')
    if k == 14:
        f.art(['L.L', '.L.', 'L.L'], TARGET_C[0] - 8, TARGET_C[1] - 1)


def tutu(f, x, y, w, flare, t):
    """Tutu ruffle; y is the body top, the ruffle sits on rows 9-11."""
    y = y + 9
    wide = w + 4 + flare * 2
    x0 = x + w // 2 - wide // 2
    f.rect(x0, y, wide, 2, 'r')
    edge = ''.join('r' if (i + t) % 2 == 0 else '.' for i in range(wide))
    f.art([edge], x0, y + 2)
    f.rect(x0 + 1, y, wide - 2, 1, 'Z')


def pointe(f, x, y, leg_h=4, spread=0):
    for lx in (x + 5 - spread, x + 10 + spread):
        f.rect(lx, y, 1, leg_h, 'O')
        f.rect(lx, y + leg_h - 1, 1, 1, 'r')


def ballet(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    if k < 2:
        info = clawd(f, y=BY, la='low', ra='low', legdx=(-1, -1, 1, 1), eyes='closed')
        tutu(f, info['x'], info['y'], 16, 0, 0)
        P.hat(f, info, 'bow')
        return
    if k < 10:
        views = ['front', 'front', 'qr', 'sr', 'back', 'sl', 'ql', 'front']
        v = views[k - 2]
        y = BY - 2
        L, info = lay(y=y, view=v, la='up', ra='up', leg_h=0, eyes='closed' if v == 'front' else 'normal')
        x, w = info['x'], info['w']
        pointe(L, BX, y + 12, 5)
        tutu(L, x, y, w, 2 if 3 <= k <= 8 else 0, k)
        P.hat(L, info, 'bow')
        f.blit(L)
        if 3 <= k <= 8:
            f.art(['L....', '.L...', '..LLL'], 3, 24 - (k % 2) * 3)
            f.art(['....L', '...L.', 'LLL..'], 32, 22 + (k % 2) * 3)
        return
    if k < 14:
        L, info = lay(x=13, y=BY - 1, view='q2r', ra='out', la='up', legs=(3, 3, 0, 0), leg_h=4,
                      eyes='closed')
        limb(L, 13, BY + 8, 5, BY + 4, 'O', t=2)
        L.put(4, BY + 4, 'r'); L.put(4, BY + 5, 'r')
        tutu(L, 13, BY - 1, 16, 1, k)
        P.hat(L, info, 'bow')
        f.blit(L.shear(0.06, 36))
        if k == 12:
            P.sparkles(f, 0, 4, [(32, 10), (6, 12)])
        return
    j = k - 14
    info = clawd(f, y=BY + j, h=12 - j, top=bool(j), lookv=j, la='low', ra='low', legdx=(-1, -1, 1, 1),
                 eyes='closed')
    tutu(f, info['x'], info['y'], 16, 0, 0)
    P.hat(f, info, 'bow')


HEADSPIN = ['front', 'qr', 'sr', 'back', 'sl', 'ql']


def headspin(f, t, n):
    k = t % 12
    f.rect(6, 36, 28, 2, 'N'); f.rect(6, 36, 28, 1, 'y')
    v = HEADSPIN[k % 6]
    L, info = lay(y=16, view=v, la='out', ra='out', leg_h=5, legdx=(-3, -1, 1, 3),
                  legs=((k % 2), 0, 0, (k + 1) % 2), eyes='squint' if k % 3 else 'closed')
    P.hat(L, info, 'capback' if v in ('front', 'qr', 'ql') else 'cap', flip=v in ('sl', 'ql'))
    L = L.rot90(2, 20, 20)
    L = drop_to(L, 36)
    f.blit(L)
    arcs = [['LL.....LL', '..L...L..'], ['.L.....L.', 'L.......L']]
    f.art(arcs[k % 2], 15, 2)
    f.art(['L.L'] if k % 2 else ['.L.'], 7 + (k % 3), 26)
    f.art(['L.L'] if k % 2 == 0 else ['.L.'], 30 - (k % 3), 26)


def cartwheel(f, t, n):
    k = t % 20
    ground(f, 'G', 36)
    if k < 6 or k >= 14:
        j = k if k < 6 else k - 14
        cx = [3, 7, 11, 14, 17, 20][j] if k < 6 else 20 + (j + 1) * 4
        rot = j % 4
        L, info = lay(x=cx - 8, y=12, la='up', ra='up', legdx=(-2, -1, 1, 2),
                      eyes='happy' if rot in (0, 2) else 'squint')
        L = drop_to(L.rot90(rot, cx, 18), 36)
        f.blit(L)
        if rot in (1, 3):
            P.dust(f, cx - 2, GROUND, 0.4)
    else:
        j = k - 6
        up = j % 2
        clawd(f, y=BY - (1 if up else 0), la='wave' if up else 'up', ra='up' if up else 'wave',
              eyes='happy', legdx=(-1, -1, 1, 1))
        if j in (1, 3, 5):
            P.sparkles(f, j, 4, [(5, 10), (34, 12), (20, 4)])
        if j >= 1:
            f.text('TA-DA', 11, 3, 'R' if j % 2 else 'Y')


def trampoline(f, t, n):
    k = t % 12
    ys = [20, 15, 10, 6, 3, 2, 3, 6, 10, 13, 15, 16]
    rots = {4: 1, 5: 2, 6: 3}
    y = ys[k]
    sag = {0: 4, 11: 2, 1: 1}.get(k, 0)
    # frame + legs
    f.rect(4, 31, 2, 5, 'g'); f.rect(34, 31, 2, 5, 'g')
    f.rect(2, 30, 6, 2, 'B'); f.rect(32, 30, 6, 2, 'B')
    f.line(7, 30, 20, 30 + sag, 'k'); f.line(20, 30 + sag, 32, 30, 'k')
    if k == 0:
        info = clawd(f, x=BX - 1, y=20 + 1, w=18, h=10, leg_h=3, eyes='closed')
        f.art(['L......L'], 16, 34)
    else:
        L, info = lay(y=y - (2 if k == 1 else 0), h=14 if k == 1 else 12, x=BX + (1 if k == 1 else 0),
                      w=14 if k == 1 else 16, la='up' if k in (1, 2, 3, 8, 9) else 'high',
                      ra='up' if k in (1, 2, 3, 8, 9) else 'high',
                      legs=(1, 1, 1, 1) if 2 <= k <= 9 else (0, 0, 0, 0),
                      eyes='squint' if k in rots else 'happy')
        if k in rots:
            L = L.rot90(rots[k], 20, y + 7)
        f.blit(L)
    if k in (4, 5, 6):
        P.sparkles(f, k, 4, [(5, 4), (34, 6)])
    if k == 0:
        f.text('BOING', 11, 4, 'P')


BOXES = [44, 42, 40, 38, 36, 33, 27, 21, 15, 9, 5, 2, -1, -4, -7, -10]


def parkour(f, t, n):
    k = t % 16
    scroll = sum(abs(BOXES[(i + 1) % 16] - BOXES[i]) if i < 15 else 3 for i in range(k))
    ticks(f, scroll, y=37, c='G', gap=7, w=3)
    ground(f, 'g', 36)
    bx = BOXES[k]
    f.rect(bx, 28, 9, 8, 'g'); f.rect(bx, 28, 9, 1, 'G'); f.rect(bx + 1, 31, 7, 1, 'k')
    x = 14
    if k <= 4 or k >= 11:
        s = k % 2
        L, info = lay(x=x, y=BY - 1 + s, view='q2r', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
                      legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1), ra='low' if s else 'high',
                      eyes='focus' if k <= 4 else 'happy')
        f.blit(L.shear(-0.08, 36))
        if k >= 11:
            P.speedlines(f, x - 1, BY + 1, t, n=3, length=5)
    elif k == 10:
        clawd(f, x=x - 1, y=BY + 2, w=18, h=10, view='q2r', eyes='closed')
        P.dust(f, x - 2, GROUND, 0.3); P.dust(f, x + 18, GROUND, 0.3, flip=True)
    else:
        y = {5: 16, 6: 11, 7: 10, 8: 12, 9: 17}[k]
        L, info = lay(x=x, y=y, view='q2r', ra='low', legs=(2, 2, 2, 2), eyes='focus' if k < 8 else 'happy')
        hx, hy = info['rh']
        if k in (5, 6, 7):
            limb(L, int(hx) - 2, int(hy), int(hx) - 2, 27, 'O', t=2)
        L = L.shear(-0.12 if k < 8 else 0.08, y + 12)
        f.blit(L)
        P.speedlines(f, x - 2, y + 2, t, n=3, length=4)


JUGGLE_C = ('R', 'B', 'E')


def juggling(f, t, n):
    k = t % 12
    balls = []
    for i in range(3):
        q = (k + 4 * i) % 12
        if q < 6:
            p, x0, x1 = q / 6, 31, 6
        else:
            p, x0, x1 = (q - 6) / 6, 6, 31
        bx = lerp(x0, x1, p)
        by = 24 - 20 * math.sin(math.pi * p)
        balls.append((bx, by, JUGGLE_C[i], q))
    toss_r = any(q == 0 for *_, q in balls)
    toss_l = any(q == 6 for *_, q in balls)
    hb = max(balls, key=lambda b: -b[1])
    info = clawd(f, ra='high' if toss_r else 'side', la='high' if toss_l else 'side',
                 eyes='normal', look=1 if hb[0] > 22 else -1 if hb[0] < 18 else 0, lookv=-1,
                 y=BY + (1 if k % 4 == 2 else 0), h=12 - (1 if k % 4 == 2 else 0))
    for bx, by, c, q in balls:
        f.art(['.CC.', 'CCCC', 'CCCC', '.CC.'], int(bx) - 1, int(by), cmap={'C': c})
        f.put(int(bx), int(by) + 1, 'W')


def pogo(f, t, n):
    k = t % 16
    u = k % 8
    side = 1 if k < 8 else -1
    hgt = [0, 3, 7, 10, 11, 10, 7, 3][u]
    dx = int(round(-side * 3 + side * 6 * (u / 8)))
    comp = 3 if u == 0 else 0
    ground(f, 'G', 36)
    y = BY - 4 - hgt + comp
    cx = 20 + dx
    peg = y + 15
    tip = 36 - hgt
    f.rect(cx - 1, y + 3, 2, peg - (y + 3), 'g')
    f.rect(cx - 9, y + 3, 18, 1, 'g')
    clawd(f, x=cx - 8, y=y, la='mid', ra='mid', legs=(0, 1, 1, 0), legdx=(1, 1, -1, -1),
          eyes='happy' if hgt > 6 else 'focus' if u else 'closed')
    f.rect(cx - 11, y + 2, 2, 3, 'R'); f.rect(cx + 9, y + 2, 2, 3, 'R')
    f.rect(cx - 4, peg, 8, 1, 'k')
    for j in range(max(1, tip - peg - 2)):
        f.rect(cx - 2 + (j % 2), peg + 1 + j, 3, 1, 'G' if j % 2 else 'g')
    f.rect(cx - 1, tip - 2, 2, 2, 'k')
    if u == 0:
        P.dust(f, cx - 6, GROUND, 0.2); P.dust(f, cx + 4, GROUND, 0.2, flip=True)
        f.text('BOING', 2 if side < 0 else 20, 4, 'P')


def skates(f, info, legdx, legs=(0, 0, 0, 0)):
    x, y, w, h = info['x'], info['y'], info['w'], info['h']
    for i, lx in enumerate((0, 4, w - 6, w - 2)):
        xx = x + lx + legdx[i]
        yy = y + h + 2 - legs[i]
        f.rect(xx - 1, yy, 3, 2, 'W'); f.rect(xx - 1, yy + 1, 3, 1, 'R')
        f.put(xx - 1, yy + 2, 'k'); f.put(xx + 1, yy + 2, 'k')


def roller_skates(f, t, n):
    k = t % 16
    ground(f, 'G', 37)
    spread = [0, 1, 2, 3, 4, 5, 6, 6, 1, 0, 0, -1, 0, 1, 1, 0][k]
    slide = int(round(4 * sin(k, 16)))
    drop = max(0, spread - 3)
    legdx = (-spread, -spread // 2, spread // 2, spread)
    arms = [('up', 'out'), ('wave', 'high'), ('out', 'up'), ('high', 'wave')][(k // 2) % 4] if spread > 1 \
        else ('side', 'side')
    eyes = 'worried' if spread > 2 else 'big' if k == 8 else 'happy'
    info = clawd(f, x=BX + slide, y=BY - 1 + drop, leg_h=2, legdx=legdx, la=arms[0], ra=arms[1], eyes=eyes)
    skates(f, info, legdx)
    if spread > 3:
        f.art(P.SWEAT, info['x'] + 18, info['y'] - 1 + k % 3)
    if k == 8:
        f.text('PHEW', 12, 4, 'g')
    ticks(f, -slide * 3, y=38, c='G', gap=9, w=2)


def kayak(f, t, n):
    k = t % 12
    surf = 30
    water(f, surf, k, speed=2)
    side = k < 6
    u = k % 6
    tilt = [0.9, 0.6, 0.3, 0.6, 0.9, 1.0][u]
    cx, cy = 26, 23
    a = math.atan2(tilt, 1.0) if side else math.atan2(-tilt, 1.0)
    dx, dy = math.cos(a) * 11, math.sin(a) * 11
    p0, p1 = (cx - dx, cy - dy), (cx + dx, cy + dy)
    f.line(p0[0], p0[1], p1[0], p1[1], 'k')
    for (px, py) in (p0, p1):
        f.rect(int(px) - 1, int(py) - 1, 3, 3, 'Y')
    clawd(f, x=8, y=17, view='q2r', ra='out', leg_h=0, eyes='happy' if k < 6 else 'focus')
    f.art(['.RRRRRRRRRRRRRRRRRRRRRRRRRRR.', 'RRRRRRRRRRRRRRRRRRRRRRRRRRRRRR', '.MMMMMMMMMMMMMMMMMMMMMMMMMMMM.'],
          4, 28)
    f.rect(8, 28, 18, 1, 'k')
    lowp = p1 if p1[1] > p0[1] else p0
    if lowp[1] >= surf - 1:
        f.art(['W.W', '.W.'] if k % 2 else ['.W.', 'W.W'], int(lowp[0]) - 1, surf - 3)
    for i in range(3):
        xx = (36 - k * 3 - i * 13) % 44 - 2
        f.rect(xx, surf + 2 + i * 2, 4, 1, 'C')


def finish_line(f, t, n):
    k = t % 20
    ground(f, 'G', 36)
    for i in range(6):
        for j in range(2):
            f.rect(26 + i * 2, 4 + j * 2, 2, 2, 'k' if (i + j) % 2 else 'W')
    f.box(25, 3, 14, 6, 'g')
    f.rect(25, 9, 1, 27, 'g'); f.rect(38, 9, 1, 27, 'g')
    x = [-16, -11, -6, -1, 4, 9, 14, 17, 20, 20, 20, 20, 20, 20, 20, 24, 29, 34, 39, 44][k]
    run = k < 8 or k >= 15
    if run:
        s = k % 2
        L, info = lay(x=x, y=BY - 1 + s, view='q2r', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
                      legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1), ra='up' if k == 7 else 'mid' if s else 'low',
                      la='up' if k == 7 else 'mid', eyes='focus' if k < 7 else 'happy')
        L.rect(x, BY - 1 + s, 16, 1, 'R'); L.art(['RR', '.R'] if s else ['R.', 'RR'], x - 2, BY - 1 + s)
        f.blit(L.shear(-0.06, 36))
    else:
        j = k - 8
        up = j % 2
        P.confetti(f, k, 8, count=14)
        info = clawd(f, x=x, y=BY - 3 * up, la='up', ra='up', legs=(1, 1, 1, 1) if up else (0, 0, 0, 0), eyes='happy')
        f.rect(x, BY - 3 * up, 16, 1, 'R')
    tape_y = 32
    if k < 7 or k >= 18:
        f.rect(26, tape_y, 12, 1, 'R')
    elif k == 7:
        f.line(26, tape_y, 33, tape_y + 2, 'R'); f.line(33, tape_y + 2, 37, tape_y, 'R')
        impact(f, 33, tape_y)
    else:
        fl = (k % 2)
        f.art(['RR', '.RR', '..R'] if fl else ['R', 'RR', '.RR', '..R'], 26, tape_y)
        f.art(['.RR', 'RR.', 'R..'] if fl else ['..R', '.RR', 'RR.'], 35, tape_y)


def podium(f, t, n):
    k = t % 16
    P.confetti(f, k, 16, count=16)
    f.rect(12, 28, 16, 8, 'U'); f.rect(12, 28, 16, 1, 'y'); f.text('1', 19, 30, 'Y')
    f.rect(0, 31, 12, 5, 'G'); f.rect(0, 31, 12, 1, 'w'); f.text('2', 5, 31, 'g')
    f.rect(28, 33, 12, 3, 'N'); f.rect(28, 33, 12, 1, 'T')
    ground(f, 'g', 36)
    raise_ = k % 4 < 2
    info = clawd(f, x=12, y=13 - (1 if raise_ else 0), la='up' if raise_ else 'high', ra='up' if raise_ else 'high',
                 eyes='happy', legs=(0, 0, 0, 0))
    lx, ly = info['lh']; rx, ry = info['rh']
    ty = int(min(ly, ry)) - 7
    f.art(['UUUUUUUU', 'YUUUUUUY', 'Y.UUUU.Y', '..UUUU..', '...UU...', '..YYYY..'], 16, ty)
    f.rect(19, ty + 1, 2, 2, 'W')
    if raise_:
        P.sparkles(f, k, 4, [(13, ty - 1), (27, ty + 1)])
    clap = k % 2
    mini(f, 2, 23, eyes='happy', la='high' if clap else 'side', ra='high' if clap else 'side')
    mini(f, 30, 25, eyes='happy', la='side' if clap else 'high', ra='side' if clap else 'high')
    f.put(6, 29, 'G'); f.put(34, 31, 'N')


ROW_SEAT = [14, 11, 8, 5, 4, 4, 5, 7, 9, 11, 13, 14]


def rowing_machine(f, t, n):
    k = t % 12
    ground(f, 'G', 36)
    # rail, foot plate, flywheel housing with a little monitor
    f.rect(2, 33, 32, 1, 'G'); f.rect(2, 34, 32, 1, 'g'); f.rect(3, 35, 2, 1, 'g'); f.rect(30, 35, 2, 1, 'g')
    f.rect(29, 27, 2, 6, 'k')
    spin = k * (2 if 1 <= k <= 4 else 1)
    f.disc(35, 28, 4.5, 'k'); f.ring(35, 28, 4.5, 'g')
    for j in range(2):
        a = spin * 0.8 + j * math.pi / 2
        f.line(35 + math.cos(a) * 3 - .5, 28 + math.sin(a) * 3 - .5, 35 - math.cos(a) * 3 - .5,
               28 - math.sin(a) * 3 - .5, 'G')
    f.rect(33, 19, 5, 4, 'k'); f.rect(34, 20, 3, 2, 'C' if k % 2 else 'E')
    f.rect(35, 23, 1, 1, 'g')
    sx = ROW_SEAT[k]
    drive = 1 <= k <= 4
    finish = k in (4, 5)
    lean = 0.1 if k in (0, 11) else -0.12 if finish else 0
    x, y = sx, 19
    L, info = lay(x=x, y=y, view='q2r', leg_h=0, ra='out' if not finish else 'side',
                  eyes='angry' if drive else 'focus' if k in (0, 11) else 'normal')
    hipx, hipy = x + 13, y + 11
    footx = 28
    reach = footx - hipx
    if reach > 6:
        limb(L, hipx, hipy, footx - 1, 30, 'O', t=2)
    else:
        kx = (hipx + footx) // 2
        limb(L, hipx, hipy, kx, hipy - 4, 'O', t=2)
        limb(L, kx, hipy - 4, footx - 1, 30, 'O', t=2)
    if lean:
        L = L.shear(lean, 31)
    hx, hy = info['rh']
    hx += int(round(lean * (31 - hy)))
    f.line(hx, hy, 33, 26, 'k')
    f.blit(L)
    f.rect(int(hx), int(hy) - 1, 1, 3, 'k')
    f.rect(sx + 2, 31, 10, 2, 'k'); f.rect(sx + 2, 31, 10, 1, 'g')
    if finish:
        f.art(P.SWEAT, x - 3, y - 1 + (k % 2), flip=True)
    if drive:
        f.art(['L.L', '.L.'] if k % 2 else ['.L.', 'L.L'], 31, 30)


# --------------------------------------------------------------------------- cheer & team games
def pompom(f, cx, cy, t, c1, c2):
    r = rng(t * 7 + int(cx))
    f.disc(cx, cy, 2.8, c1)
    for i in range(10):
        a = r.random() * 2 * math.pi
        d = 2.6 + r.random() * 1.6
        f.put(cx + math.cos(a) * d, cy + math.sin(a) * d, c2 if i % 2 else c1)


def pom_poms(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    y, la, ra, legs, kick = BY, 'side', 'side', (0, 0, 0, 0), None
    if k < 4:
        y = BY + (k % 2)
    elif k < 8:
        la = ra = 'up'
        y = BY - (3 if k in (5, 6) else 0)
        legs = (1, 1, 1, 1) if k in (5, 6) else legs
    elif k < 12:
        a = (k // 2) % 2
        la, ra = ('up', 'low') if a else ('low', 'up')
    elif k < 14:
        la = ra = 'out'
        legs, kick = (3, 3, 0, 0), True
    L, info = lay(y=y, la=la, ra=ra, legs=legs, eyes='happy' if k % 4 else 'closed')
    if kick:
        limb(L, BX + 1, y + 10, BX - 5, y + 2, 'O', t=3)
    P.hat(L, info, 'bow')
    f.blit(L.shear(-0.05, 36) if kick else L)
    for side in ('lh', 'rh'):
        hx, hy = info[side]
        pompom(f, hx + (-1 if side == 'lh' else 1), hy, k, 'Z' if side == 'lh' else 'U', 'W')
    if 4 <= k < 8:
        f.text('GO!', 15, 2, 'R' if k % 2 else 'Z')
    if k >= 12:
        f.text('CLAWD!', 9, 2, 'Z' if k % 2 else 'R')


def tug_of_war(f, t, n):
    k = t % 16
    d = int(round(3 * math.sin(2 * math.pi * k / 16)))
    if k in (11, 12):
        d = 5
    ground(f, 'G', 36)
    f.rect(21, 36, 2, 2, 'W'); f.rect(21, 36, 2, 1, 'G')
    cx = 2 + d
    L, info = lay(x=cx, y=BY, view='q2r', ra='out', eyes='big' if k in (11, 12) else 'angry',
                  legdx=(-1, -1, 0, 0) if d > 0 else (0, 0, 0, 0))
    lean = -0.18 if k not in (11, 12) else -0.02
    L = L.shear(lean, 36)
    f.blit(L)
    hx, hy = info['rh']
    hx += int(round(lean * (36 - hy)))
    mx = 29 + d
    M = Canvas()
    mini(M, mx, 28, eyes='normal', view='ql', la='side', ra='side')
    M = M.shear(0.22, 36)
    f.blit(M)
    mhx, mhy = mx - 2 + int(round(0.22 * (36 - 31))), 31
    f.line(hx, hy, mhx, mhy, 'N')
    f.line(mhx, mhy, 40, mhy + 1, 'N')
    midx = int((hx + mhx) / 2)
    midy = int(round(lerp(hy, mhy, (midx - hx) / max(1, mhx - hx))))
    f.rect(midx, midy + 1, 2, 3, 'R')
    if d > 0 and k % 2 == 0:
        P.dust(f, cx - 2, GROUND, 0.3)
    if k in (11, 12):
        f.text('!', mx + 10, 20, 'R')
    else:
        f.art(P.SWEAT, cx - 3, BY - 2 + k % 3, flip=True)


def limbo_bar(f, wob=0):
    for i in range(16):
        f.put(16 + i, 22 + (wob if 4 <= i <= 11 else 0), 'R' if (i // 2) % 2 else 'W')
    f.rect(15, 21, 3, 1, 'g'); f.rect(30, 21, 3, 1, 'g')


def limbo(f, t, n):
    k = t % 20
    ground(f, 'G', 36)
    f.rect(16, 22, 1, 14, 'g'); f.rect(31, 22, 1, 14, 'g')
    plan = {0: (-8, 12, 0), 1: (-4, 12, 0), 2: (0, 12, 0), 3: (3, 11, 0.06),
            4: (4, 10, 0.14), 5: (5, 9, 0.22), 6: (6, 9, 0.26)}
    if k in plan:
        x, h, lean = plan[k]
    elif k <= 12:
        x, h, lean = 7 + (k - 7) * 2, 9, 0.26 + 0.03 * (k % 2)
    elif k == 13:
        x, h, lean = 22, 14, 0
    elif k <= 15:
        x, h, lean = 22, 12, 0
    else:
        x, h, lean = 22 + (k - 15) * 5, 12, 0
    w = 16 + (12 - h) * 2 // 3 if h < 12 else (14 if h > 12 else 16)
    y = 33 - h
    s_ = k % 2
    wob = 1 if 7 <= k <= 12 and k % 2 else 0
    passed = k >= 13
    if passed:
        limbo_bar(f)
    if k <= 2 or k >= 16:
        L, info = lay(x=x, y=y + s_, view='q2r', legs=walk(s_), eyes='happy')
    elif k in (13, 14, 15):
        L, info = lay(x=x, y=y - (1 if k == 14 else 0), w=w, h=h, la='up', ra='up', eyes='happy')
    else:
        L, info = lay(x=x, y=y, w=w, h=h, view='q2r', la='none', ra='mid', legdx=(-1, 0, 1, 2),
                      legs=walk(s_), eyes='worried' if k >= 5 else 'focus')
    if lean:
        L = L.shear(-lean, 33)
    f.blit(L)
    if not passed:
        limbo_bar(f, wob)
    if 7 <= k <= 12:
        f.art(P.SWEAT, x - 6, 17 + k % 3, flip=True)
    if k in (14, 15):
        P.sparkles(f, k, 4, [(26, 6), (38, 12)])


PEEL = ['.UUUU.', 'UUnUUU', 'U....n']


def banana_slip(f, t, n):
    k = t % 22
    ground(f, 'G', 36)
    peel = None
    on_head = False
    if k < 6:
        peel = (22, 33)
    if k < 6:
        s = k % 2
        x = [-14, -10, -6, -2, 2, 5][k]
        clawd(f, x=x, y=BY + s, view='q2r', legs=walk(s), eyes='happy')
    elif k == 6:
        L, info = lay(x=8, y=BY - 1, view='q2r', legdx=(0, 0, 2, 3), legs=(0, 0, 1, 1), eyes='big', ra='up',
                      la='up')
        f.blit(L.shear(-0.2, 36))
        peel = (27, 33)
        f.art(['L.L', '.L.'], 21, 30)
    elif k == 7:
        L, info = lay(x=10, y=10, view='q2r', la='up', ra='up', eyes='big')
        f.blit(L.rot90(3, 18, 18))
        peel = (28, 18)
    elif k <= 12:
        L, info = lay(x=10, y=12, la='low', ra='low', eyes='x', legs=pick([(0, 2, 0, 2), (2, 0, 2, 0)], k))
        L = drop_to(L.rot90(2, 18, 18), 36)
        f.blit(L)
        bb = L.bbox()
        if k == 8:
            P.dust(f, bb[0] - 2, GROUND, 0.3); P.dust(f, bb[2] + 1, GROUND, 0.3, flip=True)
            f.text('OOF', 25, 4, 'R')
        peel = [(26, 2), (22, 1), (19, 3), (16, 6), (14, 9)][k - 8]
        P.orbit(f, (bb[0] + bb[2]) / 2, bb[1] - 4, 8, 2, k, 4, ['.U.', 'UUU', '.U.'], count=3)
    elif k <= 15:
        info = clawd(f, x=10, y=BY + (1 if k == 13 else 0), h=12 - (1 if k == 13 else 0),
                     view='front' if k < 15 else 'qr', eyes='x' if k == 13 else 'squint' if k == 14 else 'normal')
        on_head = True
        if k == 13:
            f.art(['L.L', '...', 'L.L'], 13, 14)
    else:
        j = k - 16
        s = j % 2
        info = clawd(f, x=10 + j * 6, y=BY + s, view='q2r', legs=walk(s), eyes='normal')
        on_head = True
    if on_head:
        f.art(PEEL, info['x'] + 5, info['y'] - 3)
    if peel:
        f.art(PEEL, *peel)


def bricks(f, x0, crack=False):
    f.rect(x0, 0, G - x0, 36, 'g')
    for row in range(0, 36, 3):
        f.rect(x0, row, G - x0, 1, 'G')
        off = 0 if (row // 3) % 2 else 2
        for xx in range(x0 + off, G, 4):
            f.rect(xx, row + 1, 1, 2, 'G')
    if crack:
        f.art(['K..', '.K.', 'KK.', '..K', '.K.'], x0, 20)


def wall_bonk(f, t, n):
    k = t % 24
    ground(f, 'G', 36)
    bricks(f, 32, crack=6 <= k <= 22)
    if k <= 5:
        s = k % 2
        x = [-16, -10, -4, 2, 8, 14][k]
        L, info = lay(x=x, y=BY - 1 + s, view='q2r', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
                      legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1), ra='low' if s else 'high', eyes='happy')
        f.blit(L.shear(-0.08, 36))
        if k >= 3:
            P.speedlines(f, x - 1, BY + 1, t, n=3, length=5)
    elif k == 6:
        clawd(f, x=19, y=19, w=13, h=14, leg_h=3, eyes='x', la='up', ra='high')
        P.burst(f, 14, 9, 'BONK')
    elif k == 7:
        L, info = lay(x=14, y=10, view='q2r', la='up', ra='up', eyes='x')
        f.blit(L.rot90(3, 22, 16))
    elif k <= 13:
        L, info = lay(x=6, y=12, la='low', ra='low', eyes='x', legs=pick([(0, 2, 0, 2), (2, 0, 2, 0)], k))
        L = drop_to(L.rot90(2, 14, 18), 36)
        f.blit(L)
        bb = L.bbox()
        if k == 8:
            P.dust(f, bb[0] - 2, GROUND, 0.3); P.dust(f, bb[2] + 1, GROUND, 0.3, flip=True)
        P.orbit(f, (bb[0] + bb[2]) / 2, bb[1] - 3, 7, 2, k, 4, ['.U.', 'UUU', '.U.'], count=3)
    elif k == 14:
        clawd(f, x=10, y=BY + 2, h=10, eyes='squint')
    elif k <= 16:
        clawd(f, x=10, view=['ql', 'qr'][k - 15], eyes='closed')
        f.art(['L.L', '.L.'] if k % 2 else ['.L.', 'L.L'], 18, 14)
    else:
        j = k - 17
        s = j % 2
        L, info = lay(x=[8, 3, -2, -7, -12, -17, -22][j], y=BY + s, view='q2l', legs=walk(s), eyes='squint')
        f.blit(L.shear(0.06 if s else -0.06, 36))


def blocks(f):
    f.art(['g...', 'gg..', 'ggg.', 'gggg'], 3, 32)


def sprint_start(f, t, n):
    k = t % 20
    ground(f, 'G', 36)
    blocks(f)
    if k <= 7:
        setp = k >= 4
        y, h, lean = (BY + 1, 11, 0.28) if setp else (BY + 3, 9, 0.16)
        bob = (k % 2) if not setp else 0
        trem = (k % 2) if setp else 0
        L, info = lay(x=4 + trem, y=y + bob, h=h - bob, view='q2r', ra='low', la='none',
                      eyes='focus' if setp else ('blink' if k == 2 else 'normal'), legdx=(0, 0, 1, 2))
        hx, hy = info['rh']
        limb(L, int(hx) - 2, int(hy), int(hx) - 3, 35, 'O', t=2)
        f.blit(L.shear(lean, 36))
        f.text('READY' if not setp else 'SET', 20, 4, 'g')
        if setp:
            f.art(P.SWEAT, 26, BY - 3 + (k % 2))
    elif k <= 11:
        x = [8, 17, 27, 38][k - 8]
        s_ = k % 2
        L, info = lay(x=x, y=BY - 1 + s_, view='q2r', legs=(2, 0, 2, 0) if s_ else (0, 2, 0, 2),
                      legdx=(1, -1, 1, -1) if s_ else (-1, 1, -1, 1), ra='high' if s_ else 'low', eyes='angry')
        f.blit(L.shear(-0.1, 36))
        P.speedlines(f, x - 1, BY + 1, t, n=3, length=7)
        if k == 8:
            P.burst(f, 20, 7, 'GO!')
    if 8 <= k <= 14:
        p = (k - 8) / 7
        P.dust(f, 6, GROUND, p); P.dust(f, 12, GROUND, min(1, p + 0.3), flip=True)
    if k >= 15:
        j = k - 15
        s_ = j % 2
        xx = [-18, -13, -8, -3, 1][j]
        clawd(f, x=xx, y=BY + s_, view='q2r', legs=walk(s_), eyes='happy')
        f.art(['LL', 'LL'] if s_ else ['.L', 'L.'], xx + 18, BY + 2)


def hj_bar(f):
    for i in range(14):
        f.put(23 + i, 17, 'R' if (i // 2) % 2 else 'W')
    f.rect(22, 16, 3, 1, 'g'); f.rect(36, 16, 3, 1, 'g')


def high_jump(f, t, n):
    k = t % 20
    ground(f, 'G', 36)
    sink = 2 if k == 9 else 1 if k == 10 else 0
    f.rect(20, 30 + sink, 20, 6 - sink, 'B'); f.rect(20, 30 + sink, 20, 1, 'S'); f.rect(20, 35, 20, 1, 'V')
    f.rect(23, 11, 1, 19, 'g'); f.rect(37, 11, 1, 19, 'g')
    hj_bar(f)
    if k <= 4:
        s = k % 2
        x = [-14, -9, -4, 1, 5][k]
        L, info = lay(x=x, y=BY - 1 + s, view='q2r', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
                      legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1), eyes='focus')
        f.blit(L.shear(-0.06, 36))
    elif k == 5:
        clawd(f, x=8, y=BY - 5, la='up', ra='up', legs=(1, 1, 0, 0), eyes='focus', view='front')
    elif k <= 8:
        rot, cx, cy = [(1, 17, 11), (2, 29, 6), (3, 31, 14)][k - 6]
        L, info = lay(x=cx - 8, y=cy - 6, la='up', ra='up', eyes='closed' if k == 7 else 'squint')
        f.blit(L.rot90(rot, cx, cy))
    elif k <= 12:
        L, info = lay(x=22, y=12, la='up', ra='up', legs=pick([(0, 1, 1, 0), (1, 0, 0, 1)], k), eyes='happy')
        L = L.rot90(2, 30, 18)
        L = drop_to(L, 31 + sink)
        f.blit(L)
        if k >= 10:
            f.text('YES!', 2, 4, 'R' if k % 2 else 'Y')
    elif k == 13:
        L, info = lay(x=22, y=12, eyes='happy')
        f.blit(drop_to(L.rot90(1, 30, 18), 31))
    elif k == 14:
        clawd(f, x=22, y=BY - 2, la='up', ra='up', eyes='happy', legs=(1, 1, 1, 1))
    else:
        j = k - 15
        s = j % 2
        clawd(f, x=[16, 9, 2, -5, -12][j], y=BY + s, view='q2l', legs=walk(s), eyes='happy')



FRIS = (['..ZZZ..', 'ZZZrZZZ', '.MMMMM.'], ['ZZZrZZZ', '.MMMMM.'])


def qbez(p0, c, p1, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1])


def frisbee(f, t, n):
    k = t % 24
    ground(f, 'E', 36)
    fr = None
    my = 28
    if 2 <= k <= 9:
        fr = qbez((23, 25), (27, -8), (31, 19), (k - 2) / 7)
    elif k in (10, 11):
        my = [24, 26][k - 10]
    elif 12 <= k <= 19:
        fr = qbez((29, 24), (14, -10), (18, 14), (k - 12) / 7)
    if k in (8, 9):
        my = [24, 21][k - 8]
    mini_frame = Canvas()
    mini(mini_frame, 31, my, eyes='happy' if k in (9, 10, 11) else 'normal', view='ql',
         la='high' if 8 <= k <= 13 else 'side', ra='high' if k in (12, 13) else 'side',
         legs=(1, 1, 1, 1) if my < 28 else (0, 0, 0, 0))
    f.blit(mini_frame)
    if k in (10, 11, 12):
        f.art(FRIS[0], 28, my - 1)
    jump = {19: 3, 20: 6, 21: 3}.get(k, 0)
    if k < 2:
        L, info = lay(x=2, y=BY, view='q2r', ra='low' if k == 1 else 'side', eyes='focus')
        hx, hy = info['rh']
        f.blit(L)
        f.art(FRIS[0], int(hx) - 2, int(hy) - 2)
    else:
        info = clawd(f, x=2, y=BY - jump, view='q2r', ra='out' if k in (2, 3) else 'up' if jump else 'side',
                     legs=(1, 1, 1, 1) if jump else (0, 0, 0, 0),
                     eyes='happy' if 3 <= k <= 11 or k >= 21 else 'focus', lookv=-1 if 4 <= k <= 19 else 0)
        if k in (20, 21, 22, 23):
            hx, hy = info['rh']
            f.art(FRIS[0], int(hx) - 2, int(hy) - 3)
    if fr:
        f.art(FRIS[k % 2], int(fr[0]) - 3, int(fr[1]) - 1)
        if k not in (2, 19):
            f.art(['L.L'], int(fr[0]) - 7 if k < 12 else int(fr[0]) + 5, int(fr[1]))


DBALL = ['.RRR.', 'RWRRR', 'RRRRR', 'RRRRM', '.RMM.']


def dodgeball(f, t, n):
    k = t % 24
    ground(f, 'G', 36)
    x = 10
    ball = None
    if k <= 5:
        ball = (40 - 8 * k, 20)
    elif k <= 11:
        ball = (40 - 8 * (k - 6), 30)
    elif k <= 15:
        ball = [(40, 25), (35, 25), (30, 25), (25, 25)][k - 12]
    elif k <= 18:
        ball = [(30, 16), (35, 9), (40, 4)][k - 16]
    if 1 <= k <= 4:
        clawd(f, x=x - 1, y=BY + 4, w=18, h=8, view='q2r', eyes='closed' if k in (2, 3) else 'big')
    elif 7 <= k <= 10:
        hy = [3, 7, 7, 3][k - 7]
        clawd(f, x=x, y=BY - hy, view='q2r', legs=(2, 2, 2, 2), la='up', ra='up', eyes='happy')
    elif 12 <= k <= 14:
        clawd(f, x=x, view='q2r', ra='none', la='none', eyes='closed')
        if k > 12:
            f.art(['.L', 'L.'], x + 17, BY - 2)
    elif k == 15:
        clawd(f, x=x - 2, y=BY + 1, h=11, view='q2r', eyes='x')
        P.burst(f, 30, 10, 'BONK')
    elif 16 <= k <= 19:
        sw = [-0.1, 0.1, -0.06, 0.06][k - 16]
        L, info = lay(x=x - 2, view='q2r', eyes='x' if k < 18 else 'squint')
        f.blit(L.shear(sw, 36))
        P.orbit(f, x + 6, BY - 3, 7, 2, k, 4, ['.U.', 'UUU', '.U.'], count=3)
    else:
        b = k % 2
        clawd(f, x=x, y=BY + b, h=12 - b, view='q2r', eyes='focus', ra='mid', la='mid')
    if ball:
        f.art(DBALL, *ball)
        if k not in (15, 16, 17, 18):
            f.art(['LL..', '..LL'], ball[0] + 6, ball[1] + 1)


HOLDS = 'RBUEPF'


def climb_rope(f):
    for yy in range(2, 36):
        f.put(19, yy, 'N' if yy % 3 else 'y')
        f.put(20, yy, 'y' if yy % 3 == 1 else 'N')


def bell(f, shake=0):
    f.rect(31, 2, 1, 2, 'k')
    f.art(['.UUU.', '.UUU.', 'UUUUU', 'YYYYY', '..k..'], 29 + shake, 4)


def rope_climb(f, t, n):
    k = t % 24
    f.rect(2, 0, 36, 2, 'g'); f.rect(2, 0, 36, 1, 'G')
    climb_rope(f)
    ys = [21, 20, 18, 17, 15, 14, 12, 11, 9, 8, 6, 5, 4, 4, 4, 4, 7, 12, 17, 21, 21, 21, 21, 21]
    y = ys[k]
    x = 12
    ringing = 13 <= k <= 15
    bell(f, shake=[1, -1, 1][k - 13] if ringing else 0)
    sliding = 16 <= k <= 18
    L, info = lay(x=x, y=y, leg_h=0, la='none', ra='none',
                  eyes='happy' if ringing or sliding else 'focus' if k < 12 else 'normal',
                  lookv=-1 if k <= 12 else 0)
    a = k % 2
    if k <= 11 or k >= 19:
        hl, hr = (y - 5 - 3 * a, y - 2 - 3 * (1 - a)) if k <= 11 else (y - 3, y - 4)
        limb(L, x + 1, y + 2, 17, hl, 'O', t=2)
        limb(L, x + 13, y + 2, 20, hr, 'O', t=2)
        L.rect(17, hl - 1, 2, 3, 'O'); L.rect(20, hr - 1, 2, 3, 'O')
    elif k <= 15:
        limb(L, x + 1, y + 2, 17, y - 3, 'O', t=2)
        L.rect(17, y - 4, 2, 3, 'O')
        limb(L, x + 13, y + 2, 28, y - 1 + (k % 2), 'O', t=2)
    else:
        limb(L, x + 1, y + 2, 17, y - 2, 'O', t=2)
        limb(L, x + 13, y + 2, 20, y - 2, 'O', t=2)
    limb(L, x + 3, y + 11, 17, y + 15, 'O', t=2)
    limb(L, x + 11, y + 11, 20, y + 15, 'O', t=2)
    f.blit(L)
    if ringing:
        f.text('DING', 2, 26, 'Y' if k % 2 else 'U')
        f.art(['U.U', '.U.'] if k % 2 else ['.U.', 'U.U'], 35, 6)
    if sliding:
        f.art(['L', 'L', '.', 'L'], 14, y - 8)
        f.art(['L', '.', 'L', 'L'], 25, y - 7)
        f.art(['.L.', 'L.L'], 18, y + 17)
    if k == 19:
        P.dust(f, 12, GROUND, 0.3); P.dust(f, 25, GROUND, 0.3, flip=True)


def splits(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    sp = [0, 0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 5, 0, 0, 0, 0][k]
    if k == 12:
        clawd(f, x=BX + 1, y=BY - 4, w=14, h=15, la='up', ra='up', eyes='happy')
        return
    x = BX
    y = BY + (sp * 2 if sp < 6 else 13) - (0 if sp < 6 else 0)
    if sp == 0:
        info = clawd(f, eyes='happy' if k > 12 else 'normal', la='side', ra='side',
                     legdx=(0, 0, 0, 0), y=BY + (1 if k == 13 else 0), h=12 - (1 if k == 13 else 0))
        return
    trem = 1 if sp == 6 and k % 2 else 0
    L, info = lay(x=x + trem, y=y if sp < 6 else 22, leg_h=0, la='high' if sp >= 4 else 'side',
                  ra='high' if sp >= 4 else 'side',
                  eyes='big' if sp == 6 else 'worried' if sp >= 3 else 'normal')
    by = (y if sp < 6 else 22) + 12
    reach = sp * 2
    limb(L, x + 1 + trem, by - 1, x - reach + trem, 34, 'O', t=3)
    limb(L, x + 12 + trem, by - 1, x + 13 + reach + trem, 34, 'O', t=3)
    f.blit(L)
    if sp == 6:
        f.art(P.SWEAT, x + 18, 18 + k % 3)
        f.art(P.SWEAT, x - 3, 19 + (k + 1) % 3, flip=True)
        if k in (7, 8):
            f.text('!!', 18, 6, 'R')


def sack_race(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    u = k % 4
    hop = [0, 4, 6, 4][u]
    x = int(round(-16 + 3.6 * k))
    sq = u == 0
    y = BY - hop + (2 if sq else 0)
    h = 10 if sq else 12
    info = clawd(f, x=x - (1 if sq else 0), y=y, w=18 if sq else 16, h=h, view='q2r', leg_h=0, ra='low',
                 eyes='happy' if hop else 'closed')
    top = y + 9
    bottom = 36 - hop
    sw = 20 if sq else 18
    f.rect(x - 1 - (1 if sq else 0), top, sw, bottom - top, 'N')
    f.rect(x - 1 - (1 if sq else 0), top, sw, 1, 'y')
    for yy in range(top + 2, bottom, 3):
        f.put(x + 3, yy, 'n'); f.put(x + 11, yy + 1, 'n')
    if sq:
        P.dust(f, x - 3, GROUND, 0.3); P.dust(f, x + 18, GROUND, 0.3, flip=True)


def warmup(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    f.rect(4, 36, 32, 1, 'E')
    if k < 8:
        right = k < 4
        u = k % 4
        bend = [0.0, 0.2, 0.42, 0.2][u]
        L, info = lay(la='up' if right else 'side', ra='side' if right else 'up',
                      eyes='closed' if u == 2 else 'normal', look=1 if right else -1)
        f.blit(L.shear(bend if right else -bend, 33) if bend else L)
        if u == 2:
            f.art(['L', '.', 'L'], 36 if right else 3, 12)
    elif k < 12:
        u = k - 8
        fold = [2, 4, 4, 2][u]
        info = clawd(f, y=BY + fold, h=12 - fold, top=True, lookv=1, la='down', ra='down', eyes='closed')
        if u in (1, 2):
            f.art(['.W.', 'WUW', '.W.'], 33, 22)
    else:
        u = k - 12
        arms = ['up', 'high', 'side', 'low'][u]
        info = clawd(f, la=arms, ra=arms, eyes='happy')
        arc = [['.LL.', 'L..L'], ['L...', 'L...', '.L..'], ['L..', '.L.'], ['.L', 'L.']][u]
        f.art(arc, info['x'] - 8, info['y'] - 3 + u * 3)
        f.art(arc, info['x'] + info['w'] + 4, info['y'] - 3 + u * 3, flip=True)


HURDLES = (12, 26)


def hurdle(f, hx):
    f.rect(hx - 1, 26, 8, 2, 'W'); f.rect(hx, 26, 2, 2, 'R'); f.rect(hx + 4, 26, 2, 2, 'R')
    f.rect(hx - 1, 28, 8, 1, 'G')
    f.rect(hx, 29, 1, 7, 'g'); f.rect(hx + 5, 29, 1, 7, 'g')
    f.rect(hx - 1, 35, 3, 1, 'g'); f.rect(hx + 4, 35, 3, 1, 'g')


def hurdles(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    for hx in HURDLES:
        hurdle(f, hx)
    x = int(round(-16 + 3.6 * k))
    cx = x + 8
    off = 0
    for hx in HURDLES:
        d = (cx - (hx + 3)) / 2.4
        off = max(off, 11 - d * d)
    off = int(round(max(0, off)))
    s = k % 2
    if off > 2:
        L, info = lay(x=x, y=BY - off, view='q2r', legs=(0, 2, 2, 0), legdx=(-2, -1, 2, 3), ra='out',
                      la='up', eyes='focus')
        f.blit(L.shear(0.06, 36))
    else:
        L, info = lay(x=x, y=BY - 1 + s, view='q2r', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
                      legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1), ra='high' if s else 'low', eyes='happy')
        f.blit(L.shear(-0.08, 36))
    P.speedlines(f, x - 1, info['y'] + 2, t, n=2, length=4)


SHOT = ['.ggg.', 'gkGkg', 'gkkkg', 'gkkkg', '.ggg.']


def shot_put(f, t, n):
    k = t % 16
    ground(f, 'G', 36)
    f.rect(0, 36, 22, 1, 'W'); f.rect(21, 33, 1, 3, 'W')
    ball = None
    flag = k >= 11
    if k <= 1 or k >= 14:
        info = clawd(f, x=2, view='q2r', ra='high', eyes='focus' if k <= 1 else 'normal')
        ball = (19, BY - 2)
    elif k <= 3:
        L, info = lay(x=2, y=BY + 2, h=10, view='q2r', ra='high', eyes='focus')
        f.blit(L.shear(-0.1, 36))
        ball = (19, BY + 1)
    elif k == 4:
        info = clawd(f, x=5, y=BY - 2, view='q2r', ra='high', legs=(1, 1, 1, 1), eyes='angry')
        ball = (21, BY - 3)
    elif k == 5:
        L, info = lay(x=6, view='q2r', ra='none', eyes='angry')
        limb(L, 6 + 14, BY + 3, 6 + 21, BY - 3, 'O', t=3)
        f.blit(L.shear(0.08, 36))
        ball = (27, BY - 8)
        f.text('HUP!', 2, 4, 'R')
    else:
        info = clawd(f, x=6, view='q2r', ra='out' if k < 8 else 'none', eyes='big' if k < 10 else 'happy',
                     y=BY - (2 if k in (11, 13) else 0), legs=(1, 1, 1, 1) if k in (11, 13) else (0, 0, 0, 0))
        if k <= 10:
            p = (k - 5) / 5
            ball = (int(lerp(27, 35, p)), int(13 - 14 * p + 26 * p * p))
    if ball:
        f.art(SHOT, *ball)
    if k >= 10:
        f.art(['.gg.', 'kkkk'], 34, 34) if k > 10 else None
        f.art(SHOT, 35, 32) if k > 10 else None
    if k == 10:
        P.dust(f, 32, GROUND, 0.2); P.dust(f, 39, GROUND, 0.2, flip=True)
        f.text('THUD', 22, 22, 'g')
    if flag:
        f.rect(33, 25, 1, 8, 'k'); f.art(['RR', 'RRR', 'RR'], 34, 25)
        if k in (12, 13):
            f.text('20M', 22, 14, 'Y' if k % 2 else 'R')



# --------------------------------------------------------------------------- register
add_tweened('sport_bicycle_kick', '倒挂金钩', 'Bicycle kick', bicycle_kick, n=16, dur=beats(16, 90, {(0, 1, 2): 110, 3: 250, 4: 150, 5: 400, 6: 180, 7: 200, (8, 9, 10, 11, 12): 120, (13, 14, 15): 160}), tw_at={2: 1, 3: 1, 6: 1, 7: 1, 12: 1})
add_tweened('sport_goal_kick', '射门得分', 'Goal kick', goal_kick, n=20, dur=beats(20, 100, {3: 150, 4: 300, 5: 220, 6: 140, 7: 140, 8: 350, (9, 10, 11, 12, 13): 130, (14, 15, 16, 17, 18, 19): 110}), tw_at={7: 1, 13: 1, 19: 1})
add_tweened('sport_goalie_dive', '守门员扑救', 'Goalie dive', goalie_dive, n=16, dur=beats(16, 100, {8: 250}), tw_at={4: 1, 13: 1})
add('sport_crossover', '胯下运球', 'Crossover dribble', dribble, n=16, dur=80)
add_tweened('sport_dunk', '扣篮', 'Slam dunk', dunk, n=20, dur=beats(20, 90, {3: 100, 4: 250, 5: 130, 6: 150, 7: 300, 8: 300, 9: 180, 10: 180, 11: 200, 12: 300, (13, 14, 15, 16, 17, 18, 19): 100}), tw_at={3: 1, 4: 1, 10: 1, 11: 1, 12: 1})
add('sport_ball_spin', '指尖转球', 'Finger ball spin', ball_spin, n=16, dur=90)
add_tweened('sport_tennis_serve', '网球发球', 'Tennis serve', tennis_serve, n=16, dur=beats(16, 100, {(0, 1): 150, (2, 3): 160, 4: 250, 5: 300, (9, 10, 11, 12, 13): 130, (14, 15): 150}), tw_at={1: 1, 5: 1})
add('sport_ping_pong', '乒乓球对打', 'Ping-pong rally', pingpong, n=12, dur=90)
add('sport_baseball', '棒球全垒打', 'Home run swing', baseball, n=16, dur=beats(16, 100, {(0, 1, 2, 3, 4): 130, (5, 6, 7): 110, 8: 400, 9: 180, (10, 11, 12): 130, (13, 14, 15): 150}))
add_tweened('sport_bowling', '保龄球全中', 'Bowling strike', bowling, n=20, dur=beats(20, 90, {0: 150, 1: 250, 2: 200, 9: 300, (10, 11, 12, 13, 14): 130, (15, 16, 17, 18, 19): 110}), tw_at={0: 1, 1: 1, 8: 1, 14: 1})
add_tweened('sport_golf_putt', '高尔夫推杆', 'Golf putt', golf_putt, n=16, dur=120, tw_at={11: 1, 15: 1})
add('sport_punch_bag', '打沙袋', 'Punching bag', boxing_bag, n=16, dur=90)
add_tweened('sport_karate_chop', '空手劈板', 'Karate chop', karate, n=16, dur=beats(16, 110, {3: 150, 4: 350, 5: 250}), tw_at={4: 1, 11: 1})
add_tweened('sport_sumo_stomp', '相扑踏步', 'Sumo stomp', sumo, n=16, dur=beats(16, 110, {3: 200, 4: 350, 11: 200, 12: 350}), tw_at={0: 1, 3: 1, 8: 1, 11: 1})
add_tweened('sport_fencing', '击剑刺气球', 'Fencing lunge', fencing, n=16, dur=beats(16, 100, {6: 150, 7: 350, 8: 150}), tw_at={5: 1, 8: 1, 11: 1, 13: 1})
add_tweened('sport_barbell', '举杠铃', 'Clean and jerk', barbell, n=16, dur=beats(16, 110, {7: 200, 12: 350}), tw_at={6: 1, 13: 1})
add_tweened('sport_tire_flip', '翻轮胎', 'Tire flip', tire_flip, n=16, dur=beats(16, 110, {5: 200, 8: 350}), tw_at={4: 1, 7: 1, 8: 1})
add('sport_dumbbell_curl', '哑铃弯举', 'Dumbbell curls', dumbbell_curl, n=16, dur=120)
add('sport_pushups', '俯卧撑', 'Push-ups', pushups, n=12, dur=120)
add('sport_squats', '背人深蹲', 'Piggyback squats', squats, n=12, dur=130)
add('sport_pullups', '引体向上', 'Pull-ups', pullups, n=12, dur=120)
add('sport_jump_rope', '跳绳', 'Jump rope', jump_rope, n=8, dur=90)
add('sport_hula_hoop', '转呼啦圈', 'Hula hoop', hula, n=8, dur=100)
add('sport_yoga_tree', '瑜伽树式', 'Yoga tree pose', yoga_tree, n=16, dur=160)
add('sport_jumping_jacks', '开合跳', 'Jumping jacks', jumping_jacks, n=8, dur=110)
add('sport_treadmill', '跑步机', 'Treadmill', treadmill, n=16, dur=80)
add('sport_jogging', '晨跑', 'Morning jog', jogging, n=16, dur=100)
add('sport_cycling', '骑自行车', 'Cycling', cycling, n=8, dur=90)
add('sport_unicycle', '骑独轮车', 'Unicycle wobble', unicycle, n=16, dur=110)
add_tweened('sport_kickflip', '滑板尖翻', 'Skateboard kickflip', kickflip, n=16, dur=beats(16, 100, {4: 200, 7: 200, 9: 200, (11, 12, 13, 14): 120}), tw_at={3: 1, 4: 1, 8: 1, 9: 1})
add('sport_swim_laps', '自由泳', 'Swimming laps', swim_laps, n=16, dur=110)
add_tweened('sport_diving_board', '跳水', 'High dive', diving, n=24, dur=beats(24, 100, {2: 120, 3: 260, 4: 150, 5: 400, 6: 150, 7: 150, 8: 130, 9: 300, 10: 200, 11: 150, 12: 300, (13, 14, 15): 200}), tw_at={2: 1, 3: 1, 4: 1, 12: 1})
add('sport_archery', '射箭正中靶心', 'Archery bullseye', archery, n=16, dur=100)
add_tweened('sport_ballet', '芭蕾旋转', 'Ballet pirouette', ballet, n=16, dur=120, tw_at={1: 1, 9: 1, 13: 1})
add('sport_headspin', '霹雳舞头转', 'Breakdance headspin', headspin, n=12, dur=80)
add('sport_cartwheel', '侧手翻', 'Cartwheels', cartwheel, n=20, dur=120)
add_tweened('sport_trampoline', '蹦床空翻', 'Trampoline flip', trampoline, n=12, dur=beats(12, 100, {0: 250, 5: 220}), tw_at={0: 1, 11: 1})
add_tweened('sport_parkour', '跑酷翻越', 'Parkour vault', parkour, n=16, dur=beats(16, 90, {5: 120, 6: 150, 7: 220, 8: 150, 9: 120, 10: 200}), tw_at={9: 1, 10: 1})
add('sport_juggling', '抛球杂耍', 'Juggling', juggling, n=12, dur=100)
add('sport_pogo', '弹簧高跷', 'Pogo stick', pogo, n=16, dur=90)
add_tweened('sport_roller_skates', '溜冰鞋摇晃', 'Wobbly roller skates', roller_skates, n=16, dur=beats(16, 110, {8: 350}), tw_at={1: 1, 7: 1})
add('sport_kayak', '划皮艇', 'Kayaking', kayak, n=12, dur=110)
add_tweened('sport_finish_line', '冲过终点线', 'Finish line', finish_line, n=20, dur=beats(20, 90, {6: 120, 7: 350, (8, 9, 10, 11, 12, 13, 14): 120}), tw_at={6: 1, 7: 1, 14: 1})
add('sport_podium', '领奖台', 'Top of the podium', podium, n=16, dur=150)
add('sport_rowing_machine', '划船机', 'Rowing machine', rowing_machine, n=12, dur=110)
add('sport_pom_poms', '啦啦队花球', 'Cheer pom-poms', pom_poms, n=16, dur=120)
add('sport_tug_of_war', '拔河', 'Tug of war', tug_of_war, n=16, dur=120)
add_tweened('sport_limbo', '林波舞钻杆', 'Limbo', limbo, n=20, dur=beats(20, 120, {13: 200, 14: 200}), tw_at={2: 1, 15: 1})
add_tweened('sport_banana_slip', '踩香蕉皮滑倒', 'Banana peel slip', banana_slip, n=22, dur=beats(22, 100, {6: 300, 7: 220, 8: 450, (9, 10, 11, 12): 130, 13: 280, 14: 200, 15: 250}), tw_at={5: 1, 6: 1, 7: 1})
add_tweened('sport_wall_bonk', '撞墙眼冒金星', 'Bonk into a wall', wall_bonk, n=24, dur=beats(24, 90, {6: 450, 7: 200, 8: 220, (9, 10, 11, 12, 13): 120, 14: 280, 15: 220, 16: 220, (17, 18, 19, 20, 21, 22, 23): 100}), tw_at={5: 1, 6: 1, 7: 1, 16: 1})
add_tweened('sport_sprint_start', '起跑冲刺', 'Sprint start', sprint_start, n=20, dur=beats(20, 90, {(0, 1, 2, 3, 4, 5, 6, 7): 150, 8: 400, (12, 13, 14): 120, (15, 16, 17, 18, 19): 110}), tw_at={3: 1, 7: 1, 19: 1})
add_tweened('sport_high_jump', '背越式跳高', 'High jump flop', high_jump, n=20, dur=beats(20, 90, {4: 110, 5: 250, 6: 160, 7: 320, 8: 160, 9: 220, (10, 11, 12): 160, 13: 180, 14: 280, (15, 16, 17, 18, 19): 100}), tw_at={4: 1, 12: 1, 13: 1, 14: 1})
add_tweened('sport_frisbee', '飞盘传接', 'Frisbee catch', frisbee, n=24, dur=beats(24, 100, {0: 200, 1: 220, 2: 150, 9: 150, 10: 250, 11: 150, 12: 150, 20: 250, 21: 150, (22, 23): 200}), tw_at={1: 1, 18: 1, 21: 1})
add_tweened('sport_dodgeball', '躲避球', 'Dodgeball', dodgeball, n=24, dur=beats(24, 110, {1: 160, 8: 180, 9: 180, (12, 13, 14): 200, 15: 450, (16, 17, 18, 19): 130, (20, 21, 22, 23): 120}), tw_at={0: 1, 4: 1, 6: 1, 10: 1, 11: 1})
add('sport_rope_climb', '爬绳敲钟', 'Rope climb to the bell', rope_climb, n=24, dur=100)
add_tweened('sport_splits', '劈叉', 'The splits', splits, n=16, dur=120, tw_at={1: 1, 11: 1, 12: 1})
add('sport_sack_race', '袋鼠跳', 'Sack race', sack_race, n=16, dur=100)
add_tweened('sport_warmup', '热身拉伸', 'Warm-up stretches', warmup, n=16, dur=140, tw_at={3: 1, 7: 1, 11: 1, 15: 1})
add_tweened('sport_hurdles', '跨栏', 'Hurdles', hurdles, n=16, dur=90, tw_at={4: 1, 12: 1})
add_tweened('sport_shot_put', '推铅球', 'Shot put', shot_put, n=16, dur=beats(16, 110, {4: 200, 5: 350, 10: 300, (12, 13): 200}), tw_at={4: 1, 5: 1, 7: 1, 13: 1})
