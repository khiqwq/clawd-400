"""Scenes recreated from the reference video loops and the four reference GIFs."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, mini, sin, cos, ph, pick, tri, rng, parse)
import props as P
from kit import S

# --------------------------------------------------------------------------- local art
PAN = ['kkkkkk.....', 'kkkkkkggggg', '.kkkk......']
FOOD = {
    'veg': [['E.e', 'eEE'], ['.E.', 'EeE'], ['e.E', 'EE.']],
    'pancake': [['.TTTT.', 'TYYYYT'], ['TTTTTT'], ['TYYYYT', '.TTTT.']],
    'egg': [['.WW.', 'WUUW', '.WW.'], ['WWWW'], ['.WW.', 'WUUW', '.WW.']],
}
GUITAR_E = """
    ..........PPP
    .........PP..
    ........k....
    .......k.....
    ......k......
    ..kPPk.......
    .kPPPPP......
    kPPkkPPP.....
    kPPPPPPP.....
    .kPPPPP......
    ..kkkk.......
"""
GUITAR_A = """
    ..........nnn
    .........nn..
    ........N....
    .......N.....
    ......N......
    ..NNNN.......
    .NNNNNN......
    NNNkkNNN.....
    NNNkkNNN.....
    .NNNNNN......
    ..NNNN.......
"""
WAND = ['.MMM.', 'M...M', 'M...M', '.MMM.', '..M..', '..M..', '..M..']


def stars_bg(f, t, n, seed=21, count=7):
    r = rng(seed)
    pts = [(r.randint(1, 38), r.randint(1, 38)) for _ in range(count)]
    for i, (x, y) in enumerate(pts):
        k = (t + i) % 4
        if k == 0:
            f.art(['.W.', 'WWW', '.W.'], x - 1, y - 1, cmap={'W': 'G'})
        elif k in (1, 3):
            f.put(x, y, 'G')


# --------------------------------------------------------------------------- kitchen (video)
def cook(f, t, n, food='veg', view='qr', steam=True):
    k = t % 12
    bob = 1 if k in (1, 2) else 0
    toss = k in (3, 4)
    info = clawd(f, x=BX + 5, y=BY + bob, h=12 - bob, view=view, la='mid' if toss else 'side',
                 eyes='blink' if k == 7 else 'normal')
    P.hat(f, info, 'chef')
    hx, hy = info['lh']
    px, py = int(hx) - 11, int(hy) - 1
    f.art(PAN, px, py)
    # food arc: rests in pan, flies on frames 4..10
    if 4 <= k <= 10:
        p = (k - 4) / 6
        hgt = int(round(4 * p * (1 - p) * 11))
        fr = FOOD[food][(k - 4) % 3]
        f.art(fr, px + 1 + (k % 2), py - 1 - hgt - len(fr) + 1)
    else:
        fr = FOOD[food][0]
        f.art(fr, px + 1, py - len(fr))
    if steam:
        P.rising(f, ['L'], t, n, px + 3, py - 3, count=2, height=6, jitter=2, seed=2)


def chef_arrives(f, t, n):
    """Video: jumps in stretched with arms up, lands squashed, chef hat drops on."""
    k = t % 20
    if k < 3:
        info = clawd(f, y=BY - 3 - (2 - k), h=14, w=14, x=BX + 1, la='up', ra='up', legs=(1, 1, 1, 1), eyes='normal')
    elif k == 3:
        info = clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='closed')
    else:
        info = clawd(f, eyes='normal' if k < 9 else 'happy' if k < 12 else 'normal', view='qr' if k >= 12 else 'front')
    if 5 <= k:
        drop = max(0, 12 - (k - 5) * 4)
        P.hat(f, info, 'chef', dy=-drop)
        if drop == 0 and k == 8:
            f.art(['L.......L', '.L.....L.'], info['x'] + 3, info['y'] - 10)
    if k >= 12:
        hx, hy = info['lh']
        f.art(PAN, int(hx) - 11, int(hy) - 1)
        f.art(FOOD['veg'][0], int(hx) - 10, int(hy) - 3)


def stir(f, t, n):
    k = t % 8
    info = clawd(f, view='front', la='low', ra='low', eyes='blink' if k < 6 else 'closed')
    P.hat(f, info, 'chef')
    # pot in front of the body
    f.rect(BX + 2, BY + 8, 12, 7, 'g'); f.rect(BX + 1, BY + 8, 14, 1, 'G'); f.rect(BX + 2, BY + 14, 12, 1, 'k')
    f.rect(BX, BY + 10, 2, 1, 'g'); f.rect(BX + 14, BY + 10, 2, 1, 'g')
    lx = BX + 6 + [0, 2, 4, 2, 0, -2, -4, -2][k] // 2
    f.rect(lx, BY + 3, 1, 6, 'N'); f.rect(lx - 1, BY + 2, 3, 1, 'N')
    f.rect(BX + 3, BY + 9, 10, 1, 'F')
    P.rising(f, ['L', 'L'], t, n, BX + 7, BY + 6, count=3, height=10, jitter=5, seed=5)


# --------------------------------------------------------------------------- headphones (video)
def vibe(f, t, n, notes_c='V', nod=False):
    L = Canvas()
    b = (t // 2) % 2 if nod else 0
    info = clawd(L, eyes='down', y=BY + b, h=12 - b, top=bool(b))
    P.headphones(L, info)
    k = 0 if nod else round(sin(t, n) * 2) / 2
    f.blit(L.shear(k * 0.12, 36) if k else L)
    P.notes(f, info, t, n, c=notes_c, count=2)


def phones_on(f, t, n):
    k = t % 24
    if k < 8:  # walk in from the left
        s = k % 2
        clawd(f, x=-6 + k * 2, y=BY + s, view='q2r', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
        return
    if k < 10:
        clawd(f, x=10 + (k - 8), view='qr')
        return
    info = clawd(f, x=BX, eyes='normal' if k < 14 else 'down', la='up' if 10 <= k < 14 else 'side',
                 ra='up' if 10 <= k < 14 else 'side')
    lift = max(0, 10 - (k - 10) * 3)
    P.headphones(f, info, lift=lift)
    if k >= 15:
        L = f.copy()
        f.px = L.shear(0.06 * (1 if (k // 2) % 2 else -1), 36).px
        P.notes(f, info, t, n, c='V', count=2)


# --------------------------------------------------------------------------- space (video)
def legs_trail(f, info, t, c='O'):
    x, y, w, h = info['x'], info['y'], info['w'], info['h']
    for i, lx in enumerate((1, 5, w - 6, w - 2)):
        wig = (t + i) % 2
        f.rect(x + lx, y + h, 2, 1, c)
        f.rect(x + lx + 1, y + h + 1, 2, 1, c)
        f.rect(x + lx + 2 + wig, y + h + 2, 2, 1, c)


def astronaut(f, t, n, mode='float'):
    stars_bg(f, t, n)
    if mode == 'planet':
        f.disc(7, 30, 5, 'p'); f.line(0, 33, 14, 27, 'P')
    dx = int(round(2 * sin(t, n)))
    dy = int(round(2 * cos(t, n))) - 6
    L = Canvas()
    info = clawd(L, x=BX + dx, y=BY + dy, leg_h=0, view='ql', top=True,
                 eyes='blink' if t % n == n - 2 else 'normal',
                 ra='wave' if mode == 'wave' and (t // 2) % 2 else 'up' if mode == 'wave' else 'side')
    legs_trail(L, info, t)
    P.helmet(L, info)
    if mode == 'flag':
        f.rect(0, 34, 40, 6, 'G'); f.rect(0, 34, 40, 1, 'w')
        for cx in (6, 30):
            f.rect(cx, 36, 3, 1, 'g')
        f.rect(33, 22, 1, 12, 'k'); f.rect(34, 22, 5, 3, 'R'); f.rect(34, 23, 5, 1, 'W')
    if mode == 'spin':
        L = L.rot90((t * 4 // n) % 4, 20, BY + dy + 6)
    f.blit(L)
    if mode == 'float' and t % 4 == 0:
        f.art(['.U.', 'UWU', '.U.'], info['x'] + info['w'] + 3, info['y'] - 3)


# --------------------------------------------------------------------------- guitar (video)
def guitar(f, t, n, art=GUITAR_E, solo=False, chill=False):
    L = Canvas()
    s = (t // (2 if chill else 1)) % 2
    info = clawd(L, view='q2r' if not chill else 'front', eyes='closed' if (solo or s) else 'normal',
                 ra='low' if s else 'side')
    L.art(art, BX + 5, BY + 3 + s)
    if solo:
        L = L.shear(0.18 if s else -0.06, 36)
    elif not chill:
        L = L.shear(0.08 if s else -0.04, 36)
    f.blit(L)
    P.notes(f, info, t, n, c='Y', count=3 if not chill else 2)
    if solo:
        for (x, y) in ((33, 10), (35, 22), (4, 14)):
            if (t + x) % 3 == 0:
                f.art(P.BOLT, x, y - 3, cmap={'U': 'U'})
            elif (t + x) % 3 == 1:
                f.art(['U.U', '.U.', 'U.U'], x, y)


def rock_jump(f, t, n):
    k = t % 10
    dy = [0, -3, -7, -9, -10, -9, -7, -3, 0, 0][k]
    L = Canvas()
    info = clawd(L, y=BY + dy, legs=(1, 1, 1, 1) if dy < -2 else (0, 0, 0, 0),
                 eyes='closed' if dy < -6 else 'angry', ra='up' if dy < -6 else 'side')
    L.art(GUITAR_E, BX + 4, BY + 3 + dy)
    f.blit(L)
    if k in (8, 9):
        P.dust(f, BX - 3, GROUND, (k - 8) / 2); P.dust(f, BX + 18, GROUND, (k - 8) / 2, flip=True)
    if dy < -8:
        f.art(P.SPARK_BIG, 3, 4); f.art(P.SPARK_BIG, 30, 2)


# --------------------------------------------------------------------------- desk (video)
def desk_bg(f, t, monitor=True):
    f.rect(27, 28, 13, 1, 'G'); f.rect(28, 29, 1, 8, 'g'); f.rect(38, 29, 1, 8, 'g')
    if monitor:
        f.rect(31, 19, 8, 7, 'k'); f.rect(32, 20, 6, 5, 'b'); f.rect(34, 26, 2, 2, 'k')
        for j in range(3):
            w = (t * 3 + j * 5) % 5 + 1
            f.rect(33, 21 + j * 1 + j, w, 1, 'C')
    f.rect(26, 27, 5, 1, 'k')


def chair(f, x=9):
    f.rect(x, 34, 18, 1, 'g'); f.rect(x + 8, 35, 2, 3, 'g'); f.rect(x + 4, 38, 10, 1, 'g')
    f.rect(x, 22, 2, 12, 'g')


def desk_type(f, t, n, think=False, sip=False):
    desk_bg(f, t)
    chair(f)
    k = t % 2
    eyes = 'normal'
    if think:
        eyes = 'normal'
    info = clawd(f, x=10, y=BY + 1, leg_h=2, view='q2r', ra='side' if not think else 'up',
                 eyes='blink' if t % n == n - 3 else eyes)
    if not think and not sip:
        f.rect(26, 26 - k, 3, 1, 'O')
    if think:
        P.dots_bubble(f, info, t)
    if sip:
        P.item(f, (info['rh'][0], info['rh'][1] - 2 - (t // 4) % 2), 'mug')
        P.rising(f, ['L'], t, n, info['rh'][0] + 2, info['rh'][1] - 6, count=2, height=5, jitter=1)


def desk_flail(f, t, n):
    """Video: leaps off the chair and tumbles, limbs everywhere, then drops back."""
    desk_bg(f, t)
    chair(f)
    k = t % 16
    if k < 3 or k >= 13:
        clawd(f, x=10, y=BY + 1, leg_h=2, view='q2r', eyes='normal' if k < 2 or k > 13 else 'big')
        return
    j = k - 3
    dy = [-4, -9, -12, -13, -12, -9, -5, -1, 1, 1][j]
    L = Canvas()
    clawd(L, x=10, y=BY + dy, eyes=pick(['big', 'x', 'squint', 'big'], j), la=pick(['up', 'wave', 'out'], j),
          ra=pick(['wave', 'out', 'up'], j), legs=pick([(0, 2, 1, 0), (2, 0, 0, 1), (1, 1, 2, 0)], j))
    f.blit(L.rot90([0, 1, 1, 2, 2, 3, 3, 0, 0, 0][j], 20, BY + dy + 7))


# --------------------------------------------------------------------------- reading (video)
def read(f, t, n, sleepy=False, stack=False):
    k = t % 16
    if stack:
        for j, c in enumerate('RBEY'):
            f.rect(30, 33 - j * 2, 8, 2, c); f.rect(30, 33 - j * 2, 8, 1, 'w' if j % 2 else 'T')
    if sleepy:
        nod = 1 if k >= 8 else 0
        info = clawd(f, eyes='closed' if k >= 6 else 'blink', y=BY + nod, h=12 - nod, top=bool(nod))
        P.face(f, info, 'readers')
        P.item(f, (info['rh'][0], info['rh'][1] + nod * 2), 'book', art=(['bbbbb', 'bwwwb', 'bbbbb', 'bwwwb', 'bbbbb'], 0, 2))
        if k >= 8:
            P.zzz(f, info, t, n)
        return
    info = clawd(f, eyes='blink' if k == 13 else 'normal', look=1 if 4 <= k < 12 else 0)
    P.face(f, info, 'readers')
    hx, hy = info['rh']
    flip = k in (10, 11)
    f.rect(hx, hy - 2, 4, 6, 'b'); f.rect(hx + 1, hy - 1, 3, 4, 'w')
    if flip:
        f.rect(hx + 1, hy - 4, 3, 3, 'w'); f.rect(hx + 4, hy - 4, 1, 3, 'b')
    else:
        f.rect(hx + 1, hy - 1, 3, 1, 'k') if k % 4 < 2 else f.rect(hx + 1, hy + 1, 3, 1, 'k')


def armchair_arrive(f, t, n):
    k = t % 20
    f.rect(6, 26, 4, 11, 'g'); f.rect(30, 26, 4, 11, 'g'); f.rect(8, 33, 24, 3, 'G'); f.rect(8, 18, 24, 3, 'g')
    if k < 6:
        s = k % 2
        clawd(f, x=-14 + k * 4, y=BY - 1 + s, view='q2r', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
    elif k < 8:
        clawd(f, y=BY - 4, h=14, w=14, x=BX + 1, la='up', ra='up', legs=(1, 1, 1, 1))
    elif k == 8:
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 1, eyes='closed', leg_h=0)
    else:
        info = clawd(f, y=BY - 2, leg_h=0, eyes='happy' if k < 11 else 'normal')
        if k >= 11:
            P.face(f, info, 'readers')
            hx, hy = info['rh']
            f.rect(hx, hy - 2, 4, 6, 'b'); f.rect(hx + 1, hy - 1, 3, 4, 'w')
    f.rect(8, 33, 24, 3, 'G')


# --------------------------------------------------------------------------- moving between rooms (video)
def walk_in(f, t, n):
    k = t % 24
    if k < 10:
        s = k % 2
        clawd(f, x=-16 + k * 3, y=BY + s, view='q2r', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
    else:
        j = k - 10
        v = ['qr', 'front', 'front', 'front', 'front', 'ql', 'ql', 'front', 'front', 'front', 'front', 'front', 'qr', 'qr'][j]
        clawd(f, x=BX + 2, view=v, eyes='blink' if j == 9 else 'happy' if j in (2, 3) else 'normal',
              ra='up' if j in (2, 3) else 'side')


def walk_out(f, t, n):
    k = t % 24
    f.rect(30, 14, 9, 22, 'g'); f.rect(31, 15, 7, 21, 'k')
    door = k < 14 or k > 20
    if k < 12:
        s = k % 2
        clawd(f, x=2 + k * 2, y=BY + s, view='q2r', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
    elif k < 14:
        clawd(f, x=26, view='back')
    elif k < 17:
        L = Canvas(); clawd(L, x=26 + (k - 13) * 2, view='q2r')
        for y in range(L.h):
            for x in range(31, L.w):
                L.px[y][x] = None
        f.blit(L)
    if door:
        f.rect(31, 15, 7, 21, 'N'); f.rect(36, 25, 1, 2, 'U')
    else:
        f.rect(31, 15, 2, 21, 'N')


def stairs(f, t, n):
    for i in range(7):
        f.rect(i * 6, 36 - i * 4, 40, 4, 'g')
        f.rect(i * 6, 36 - i * 4, 40, 1, 'G')
    p = ph(t, n)
    x = -6 + int(p * 36)
    y = 13 - int(p * 24)
    L = Canvas()
    s = t % 2
    clawd(L, x=x, y=y + s, view='q2r', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
    f.blit(L.rotate(-25, x + 8, y + 8))


def teleport(f, t, n):
    k = t % 20
    if k < 6:
        clawd(f, view=['front', 'qr', 'sr', 'back', 'sl', 'ql'][k], eyes='squint')
        return
    if k < 9:
        L = Canvas(); clawd(L, view='front', eyes='squint')
        for y in range(L.h):
            if (y + k) % 3 == 0:
                L.px[y] = [None] * L.w
            elif (y + k) % 3 == 1:
                L.px[y] = ([None] * 2 + L.px[y])[:L.w]
        R = L.copy().recolor(lambda c: (236, 92, 118)).shift(-1, 0)
        C = L.copy().recolor(lambda c: (110, 200, 220)).shift(1, 0)
        f.blit(R); f.blit(C); f.blit(L)
        return
    if k < 11:
        for y in range(BY + 2, BY + 13, 3 - (k - 9)):
            f.rect(BX + 2 + (k - 9) * 4, y, 12 - (k - 9) * 8, 1, 'C')
        return
    if k < 14:
        if k == 12:
            f.art(['..W..', '.WCW.', 'WCWCW', '.WCW.', '..W..'], 18, 26)
        return
    j = k - 14  # reappear: the vanish played backwards (scanlines -> glitch -> Clawd)
    if j < 2:
        for y in range(BY + 2, BY + 13, 2 + j):
            f.rect(BX + 6 - j * 4, y, 4 + j * 8, 1, 'C')
        return
    L = Canvas(); clawd(L, eyes='big' if j < 4 else 'normal')
    if j == 2:
        for y in range(L.h):
            if y % 3 == 0:
                L.px[y] = [None] * L.w
        f.blit(L.copy().recolor(lambda c: (110, 200, 220)).shift(1, 0))
    f.blit(L)
    if j == 3:
        P.sparkles(f, 0, 4, [(6, 18), (33, 20), (20, 10)])


def space_drop(f, t, n):
    k = t % 16
    seq = [-30, -22, -14, -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dy = seq[k]
    if k == 4:
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='x')
        P.dust(f, BX - 3, GROUND, 0.5); P.dust(f, BX + 18, GROUND, 0.5, flip=True)
    elif k < 4:
        L = Canvas(); info = clawd(L, y=BY + dy, h=14, w=14, x=BX + 1, la='up', ra='up', eyes='big', leg_h=3)
        f.blit(L)
        f.rect(BX + 4, BY + dy - 6, 1, 4, 'L'); f.rect(BX + 11, BY + dy - 8, 1, 5, 'L')
    else:
        info = clawd(f, eyes=['x', 'x', 'squint', 'normal', 'normal', 'blink', 'normal', 'happy', 'happy', 'happy', 'normal', 'normal'][k - 4])
        if 5 <= k <= 9:
            P.orbit(f, 20, BY - 3, 9, 2, k, 4, ['.U.', 'UUU', '.U.'], count=3)


def stretch_tall(f, t, n):
    k = t % 12
    seq = ['n', 'n', 'sq', 'tall', 'tall', 'tall', 'sq', 'n', 'n', 'n', 'n', 'n']
    s = seq[k]
    if s == 'sq':
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='closed')
    elif s == 'tall':
        clawd(f, x=BX + 1, w=14, h=15, y=BY - 3 - (k == 4), la='up', ra='up', eyes='closed' if k == 4 else 'normal')
    else:
        clawd(f, eyes='blink' if k == 10 else 'normal')


# --------------------------------------------------------------------------- reference GIFs
def bubbles(f, t, n, big=False):
    k = t % 12
    blowing = 2 <= k <= 5
    info = clawd(f, x=BX - 7, view='qr', eyes='closed' if blowing else 'happy' if k > 8 else 'normal',
                 tilt=1 if blowing else 0)
    hx, hy = info['rh']
    f.art(WAND, int(hx), int(hy) - 6)
    if big:
        r = [0, 0, 1, 2, 3, 4, 5, 6, 6.5, 0, 0, 0][k]
        if r:
            P.bubble_ring(f, hx + 3 + r, hy - 4 - r, r)
        if k == 9:
            for a in range(8):
                f.put(hx + 10 + 7 * math.cos(a * .8), hy - 11 + 7 * math.sin(a * .8), 'L')
        return
    for i in range(3):
        p = ((k - 3 - i * 3) % 12) / 12
        if p < 0.75:
            bx = hx + 4 + p * 14 + math.sin(p * 9 + i) * 1.5
            by = hy - 6 - p * 26
            P.bubble_ring(f, bx, by, 1.5 + i * 0.7, c='L' if i % 2 else 'p')
        elif p < 0.85:
            bx, by = hx + 4 + .78 * 14, hy - 6 - .78 * 26
            for a in range(6):
                f.put(bx + 3 * math.cos(a), by + 3 * math.sin(a), 'L')


def tea_talk(f, t, n):
    k = t % 16
    turned = k >= 8
    info = clawd(f, eyes='closed', top=turned, y=BY + (1 if turned else 0), h=12 - (1 if turned else 0),
                 view='ql' if turned else 'qr', tilt=0 if turned else 1)
    side = 'l' if turned else 'r'
    P.hold(f, info, 'cup', side)
    P.dots_bubble(f, info, k % 8, side='l' if turned else 'r')


def tea_sip(f, t, n):
    k = t % 12
    sip = 4 <= k <= 8
    info = clawd(f, eyes='closed' if sip else 'happy' if k > 8 else 'normal', ra='chin' if sip else 'side')
    if sip:
        P.item(f, (info['x'] + info['w'] - 9, info['y'] + 6), 'cup')
    else:
        P.hold(f, info, 'cup', 'r', dy=0)
    if not sip:
        P.rising(f, ['L', 'L'], t, n, info['rh'][0] + 3, info['rh'][1] - 4, count=2, height=6, jitter=1)
    else:
        f.art(['.r.', 'r.r'], info['x'] + info['w'] - 3, info['y'] - 3) if k == 6 else None


def idea(f, t, n, ding=False):
    k = t % 12
    up = not ding or k >= 5
    info = clawd(f, view='qr', tilt=1 if up else 0, ra='up' if up else 'side',
                 eyes='big' if ding and k >= 5 else 'blink' if k == 9 else 'normal')
    cx, top = info['head']
    lit = (not ding) or k >= 5
    P.bulb(f, int(cx) - 6, int(top) - 15, t if lit else 3, lit=lit)
    if ding and k in (5, 6, 7):
        for (dx, dy) in ((-4, -10), (8, -12), (-3, -16), (7, -17)):
            f.art(['U.U', '.U.', 'U.U'] if k % 2 else ['.U.', 'UUU', '.U.'], int(cx) + dx, int(top) + dy)


def spinner(f, t, n, on_head=False):
    k = t % 4
    arts = [P.ITEMS['spinner'][0],
            ['.bb...', 'bWWbb.', '.bkkbb', '.bkkb.', 'bbWWb.', '...bb.'],
            ['..bb..', '.bkkb.', 'bWkkWb', 'bWkkWb', '.bkkb.', '..bb..'],
            ['...bb.', '.bbWWb', '.bkkb.', 'bbkkb.', '.bWWb.', '.bb...']]
    if on_head:
        info = clawd(f, eyes='angry' if k % 2 else 'focus', lookv=-1 if True else 0, view='front')
        cx, top = info['head']
        f.rect(int(cx), int(top) - 2, 1, 2, 'k')
        f.art(arts[k], int(cx) - 3, int(top) - 8)
        return
    info = clawd(f, view='qr', eyes='focus', look=1)
    hx, hy = info['rh']
    f.art(arts[k], int(hx), int(hy) - 3)
    if k == 0:
        f.art(['K'], int(hx) + 7, int(hy) - 4)


def turn_top(f, t, n):
    """Reference 2: turns away showing the top face, then back."""
    k = t % 12
    seq = [('front', False), ('qr', False), ('qr', True), ('front', True), ('ql', True), ('ql', False)]
    v, tp = seq[(k // 2) % 6]
    clawd(f, view=v, top=tp, y=BY + (1 if tp else 0), h=12 - (1 if tp else 0), eyes='closed' if tp else 'normal')


# --------------------------------------------------------------------------- register (40)
add('cook_veggies', '颠锅炒青菜', 'Chef flips veggies', cook, n=12, dur=130)
add('cook_pancake', '翻松饼', 'Pancake flip', cook, n=12, dur=130, food='pancake')
add('cook_egg', '煎鸡蛋', 'Frying an egg', cook, n=12, dur=130, food='egg', view='front')
add('chef_arrives', '跳进厨房戴帽子', 'Chef hat drops on', chef_arrives, n=20, dur=120)
add('stir_soup', '搅汤', 'Stirring soup', stir, n=8, dur=150)
add('vibe_headphones', '戴耳机摇摆', 'Headphone vibes', vibe, n=12, dur=140)
add('vibe_nod', '戴耳机点头', 'Headphone nod', vibe, n=8, dur=150, nod=True, notes_c='Y')
add('phones_on', '戴上耳机', 'Putting headphones on', phones_on, n=24, dur=120)
add('astro_float', '太空漂浮', 'Astronaut float', astronaut, n=16, dur=140)
add('astro_spin', '失重翻转', 'Zero-g spin', astronaut, n=16, dur=110, mode='spin')
add('astro_wave', '宇航员挥手', 'Astronaut wave', astronaut, n=16, dur=140, mode='wave')
add('astro_planet', '星球旁漂浮', 'Floating by a planet', astronaut, n=16, dur=150, mode='planet')
add('astro_flag', '月球插旗', 'Flag on the moon', astronaut, n=16, dur=150, mode='flag')
add('guitar_rock', '弹电吉他', 'Electric guitar', guitar, n=8, dur=120)
add('guitar_solo', '吉他独奏', 'Guitar solo', guitar, n=8, dur=90, solo=True)
add('guitar_chill', '木吉他弹唱', 'Acoustic strum', guitar, n=8, dur=170, art=GUITAR_A, chill=True)
add('rock_jump', '摇滚跳跃', 'Rock star jump', rock_jump, n=10, dur=90)
add('desk_typing', '书桌打字', 'Typing at the desk', desk_type, n=8, dur=110)
add('desk_think', '书桌前思考', 'Thinking at the desk', desk_type, n=16, dur=150, think=True)
add('desk_coffee', '书桌喝咖啡', 'Coffee at the desk', desk_type, n=8, dur=200, sip=True)
add('desk_flail', '从椅子上蹦起', 'Desk flail', desk_flail, n=16, dur=90)
add('read_glasses', '戴眼镜看书', 'Reading with glasses', read, n=16, dur=170)
add('read_doze', '看书打瞌睡', 'Dozing over a book', read, n=16, dur=200, sleepy=True)
add('read_stack', '书堆旁阅读', 'Reading by a book stack', read, n=16, dur=170, stack=True)
add('armchair_arrive', '跳上扶手椅', 'Hop into the armchair', armchair_arrive, n=20, dur=120)
add('walk_in', '走进房间', 'Walking in', walk_in, n=24, dur=110)
add('walk_out_door', '开门离开', 'Out the door', walk_out, n=24, dur=110)
add('stairs_climb', '爬楼梯', 'Climbing stairs', stairs, n=16, dur=110)
add('teleport', '转圈传送', 'Spin teleport', teleport, n=20, dur=90)
add('space_drop', '从天而降', 'Drop-in landing', space_drop, n=16, dur=100)
add('stretch_tall', '拉长跳', 'Stretch hop', stretch_tall, n=12, dur=110)
add('bubble_wand', '吹泡泡', 'Blowing bubbles', bubbles, n=12, dur=150)
add('bubble_big', '吹大泡泡', 'One big bubble', bubbles, n=12, dur=130, big=True)
add('tea_talk', '喝茶聊天', 'Tea and chatter', tea_talk, n=16, dur=180)
add('tea_sip', '抿一口茶', 'Sip of tea', tea_sip, n=12, dur=170)
add('idea_bulb', '灵光一闪', 'Idea!', idea, n=12, dur=160)
add('idea_ding', '灯泡点亮', 'Lightbulb ding', idea, n=12, dur=130, ding=True)
add('fidget_spinner', '指尖陀螺', 'Fidget spinner', spinner, n=8, dur=90)
add('spinner_head', '头顶陀螺', 'Spinner on head', spinner, n=8, dur=90, on_head=True)
add('turn_around', '转身看看', 'Turning around', turn_top, n=12, dur=170)
