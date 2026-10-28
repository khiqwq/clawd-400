"""Coding, computers and Clawd at work (Clawd is the Claude Code mascot)."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, mini, sin, cos, ph, pick, tri, rng, parse, text_w)
from engine import beats, add_tweened
import props as P




# --------------------------------------------------------------------------- shared helpers / art
def LG(s):
    """Alternating walk legs."""
    return (1, 0, 1, 0) if s else (0, 1, 0, 1)


def window(f, x, y, w, h, bg='k', bar='g'):
    """App window: grey frame + title bar with three traffic-light dots."""
    f.rect(x, y, w, h, bar)
    f.rect(x + 1, y + 3, w - 2, h - 4, bg)
    for i, c in enumerate('RUE'):
        f.put(x + 2 + i * 2, y + 1, c)


def monitor(f, x, y, w, h, bg='k', stand=True):
    f.rect(x, y, w, h, 'g')
    f.rect(x + 1, y + 1, w - 2, h - 2, bg)
    if stand:
        cx = x + w // 2
        f.rect(cx - 1, y + h, 2, 2, 'g')
        f.rect(cx - 3, y + h + 2, 6, 1, 'g')


# Claude Code "thinking" asterisk, small -> big
AST = [
    ['F'],
    ['.F.', 'FFF', '.F.'],
    ['F.F.F', '.FFF.', 'FFFFF', '.FFF.', 'F.F.F'],
    ['...F...', '.F.F.F.', '..FFF..', 'FFFFFFF', '..FFF..', '.F.F.F.', '...F...'],
]


def spark(f, cx, cy, k, c='F'):
    a = AST[k]
    f.art(a, cx - len(a[0]) // 2, cy - len(a) // 2, cmap={'F': c})


def float_chars(f, t, n, chars, x0, y0, height=12, cols='BEP', spread=8, seed=3):
    r = rng(seed)
    cnt = len(chars)
    for i, ch in enumerate(chars):
        p = ((t / n) + i / cnt) % 1
        x = int(x0 + r.randint(-spread, spread) + math.sin(p * 6.28 + i) * 1.5)
        f.text(ch, x, int(y0 - p * height), cols[i % len(cols)])


BUG_ART = ['.k.k.', '..k..', '.EEE.', 'EEkEE', 'EEkEE', '.EEE.']


def bug(f, x, y, t=0, c='E'):
    P.bug(f, x, y, t, c=c)


CHECK = ['....W', '...WW', 'W.WW.', 'WWW..', '.W...']
XMARK = ['W...W', '.W.W.', '..W..', '.W.W.', 'W...W']


# --------------------------------------------------------------------------- 1 laptop from the front
def laptop_front(f, t, n):
    s = t % 2
    k = t % n
    float_chars(f, t, n, '01{;', 20, 15, height=12, cols='BEPF', spread=12)
    clawd(f, y=BY - 2, eyes='blink' if k == n - 3 else 'normal', lookv=1,
          la='low' if s else 'mid', ra='mid' if s else 'low')
    f.rect(10, 28, 20, 8, 'G')
    f.box(10, 28, 20, 8, 'g')
    f.art(AST[2], 18, 30, cmap={'F': 'O'})
    f.rect(6, 36, 28, 2, 'g')
    f.rect(6, 36, 28, 1, 'G')
    # little key clicks on the lid edge
    f.art(['W.W', '.W.'] if s else ['.W.', 'W.W'], 11 if s else 26, 25)


# --------------------------------------------------------------------------- 2 terminal prompt
def terminal(f, t, n):
    k = t % n
    window(f, 2, 0, 36, 22)
    cmd = 'MAKE'
    f.text('$', 4, 4, 'E')
    typed = min(len(cmd), max(0, k - 1))
    f.text(cmd[:typed], 8, 4, 'W')
    if k < 7 and k % 2 == 0:
        f.rect(8 + (text_w(cmd[:typed]) + 1 if typed else 0), 4, 3, 5, 'W')
    if 7 <= k < 11:
        for d in range(k - 6):
            f.put(4 + d * 2, 14, 'G')
    if k >= 11:
        f.text('BUILD OK', 4, 10, 'E')
    if k >= 14:
        f.text('$', 4, 16, 'E')
        if k % 2 == 0:
            f.rect(8, 16, 3, 5, 'W')
    typing = 1 <= k <= 5
    happy = 11 <= k <= 13
    s = t % 2
    clawd(f, y=BY + 1, lookv=-1, eyes='happy' if happy else 'blink' if k == 18 else 'normal',
          la='up' if happy else ('high' if typing and s else 'side'),
          ra='up' if happy else ('high' if typing and not s else 'side'))


# --------------------------------------------------------------------------- 3 scrolling logs
def log_scroll(f, t, n):
    window(f, 1, 1, 22, 35)
    r = rng(4)
    segs = [(r.randint(2, 6), r.randint(2, 9)) for _ in range(10)]
    red_y = None
    for i in range(10):
        y = 4 + (i * 3 - t) % 30
        a, b = segs[i]
        c = 'R' if i == 0 else pick('GCGEGGCGBG', i)
        f.rect(3, y, a, 1, c if i == 0 else 'g')
        f.rect(4 + a, y, b + (6 if i == 0 else 0), 1, c)
        if i == 0:
            red_y = y
    alarm = 14 <= red_y <= 24
    lv = -1 if red_y < 14 else (1 if red_y > 26 else 0)
    info = clawd(f, x=24, view='ql', eyes='big' if alarm else 'normal', lookv=lv,
                 la='high' if alarm else 'side')
    if alarm and t % 2 == 0:
        f.art(P.EXCL, 33, 13, cmap={'K': 'R'})


# --------------------------------------------------------------------------- 4 bug squash
def bug_squash(f, t, n):
    k = t % 16
    bx = 38 - k * 3 if k <= 6 else 20
    if k <= 10:
        bug(f, bx, 30, t)
    if k <= 6:
        crouch = k >= 5
        clawd(f, x=2, view='qr', look=1, eyes='focus', y=BY + crouch, h=12 - crouch)
    elif k <= 10:
        j = k - 7
        clawd(f, x=[5, 8, 11, 13][j], y=BY + [-6, -9, -8, -4][j], la='up', ra='up', legs=(1, 1, 1, 1),
              eyes='angry')
    elif k == 11:
        clawd(f, x=12, w=20, h=9, y=BY + 3, eyes='closed')
        f.art(['E.E', '.EE'], 9, 34)
        f.art(['E.E', 'EE.'], 32, 34)
        f.art(['.E.', 'E.E'], 20, 18)
    else:
        f.rect(16, 35, 12, 1, 'E')
        f.put(15, 34, 'E'); f.put(28, 34, 'e'); f.put(21, 34, 'e')
        x = 14 - (k - 12) * 3
        info = clawd(f, x=x, view='ql', y=BY + (k % 2), legs=LG(k % 2), eyes='happy')
        f.art(P.SPARK, info['x'] + 17, info['y'] - 3) if k % 2 else None


# --------------------------------------------------------------------------- 5 bug hunt with magnifier
def bug_hunt(f, t, n):
    lx = 26 + 9 * tri(t, n)
    ly = 30
    bxy = (33, 32)
    found = abs(lx - bxy[0]) < 2.5
    info = clawd(f, x=0, view='qr', ra='out', eyes='big' if found else 'focus', look=1,
                 la='side', y=BY + (0 if found else (t // 2) % 2))
    hx, hy = info['rh']
    f.line(hx, hy, lx - 4, ly - 3, 'N')
    if not found:
        f.rect(bxy[0], bxy[1], 2, 1, 'k')
    f.disc(lx, ly, 4.5, 'S')
    f.ring(lx, ly, 5.5, 'k', 1.2)
    f.put(lx - 2, ly - 2, 'W'); f.put(lx - 1, ly - 3, 'W')
    if found:
        bug(f, int(lx) - 2, int(ly) - 3, t)
        f.art(P.EXCL, info['x'] + 8, info['y'] - 8, cmap={'K': 'R'})


# --------------------------------------------------------------------------- 6 compile progress bar
def compile_bar(f, t, n):
    k = t % n
    p = min(1.0, k / 15)
    done = k >= 16
    f.text('BUILD' if not done else 'DONE!', 3, 3, 'g' if not done else 'E')
    pct = '%d%%' % int(p * 100)
    f.text(pct, 37 - text_w(pct), 3, 'g')
    P.progress(f, 3, 10, 34, p, c='E' if done else 'B', bg='g')
    if not done:
        clawd(f, eyes='line' if k < 12 else 'normal', lookv=-1, la='front', ra='front',
              legs=(0, 0, 0, 1 if t % 2 else 0))
        if k % 4 == 1:
            f.art(['L.', '.L'], 30, 33)
    else:
        j = k - 16
        dy = [0, -3, -6, -7, -6, -3, 0, 0][j]
        clawd(f, y=BY + dy, la='up', ra='up', eyes='happy', legs=(1, 1, 1, 1) if dy < -2 else (0, 0, 0, 0))
        P.sparkles(f, j, 4, [(4, 17), (35, 20), (8, 28)])


# --------------------------------------------------------------------------- 7 test suite goes green
def test_suite(f, t, n):
    k = t % n
    green = sum(1 for i in range(5) if k >= 3 + i * 3)
    for i in range(5):
        x = 2 + i * 7
        ok = i < green
        f.rect(x, 3, 7, 7, 'e' if ok else 'M')
        f.rect(x + 1, 4, 5, 5, 'E' if ok else 'R')
        f.art(CHECK if ok else XMARK, x + 1, 4)
        if ok and k == 3 + i * 3:
            f.box(x - 1, 2, 9, 9, 'U')
    msg = '%d/5 PASS' % green
    f.text_c(msg, 20, 12, 'E' if green == 5 else 'g')
    if green == 5:
        s = (t // 2) % 2
        clawd(f, la='up' if s else 'high', ra='up' if s else 'high', y=BY + 1 - 2 * s, legs=(1, 1, 1, 1) if s else (0, 0, 0, 0),
              eyes='happy')
    else:
        cur = min(4, green)
        clawd(f, look=[-2, -1, 0, 1, 2][cur], lookv=-1, eyes='worried' if green < 2 else 'normal', ra='chin')


# --------------------------------------------------------------------------- 8 deploy rocket
ROCKET = [
    '...R...',
    '..RRR..',
    '.GWWWG.',
    '.GWCWG.',
    '.GCbCG.',
    '.GWCWG.',
    '.GWWWG.',
    '.GWWWG.',
    'RGWWWGR',
    'RRWWWRR',
    'R.RRR.R',
]


def deploy_rocket(f, t, n):
    k = t % n
    f.rect(25, 36, 11, 1, 'g')
    lift = 0 if k < 7 else int(0.45 * (k - 6) ** 2)
    ry = 25 - lift
    if ry > -14:
        f.art(ROCKET, 27, ry)
        if k >= 6:
            f.art(pick([['.F.F.', 'FUUUF', '.FUF.', '..F..'], ['F.F.F', 'FUUUF', 'FUUUF', '.FUF.', '..F..']], t), 28, ry + 11)
    if 6 <= k <= 12:
        for (dx, dy) in ((-3, 0), (6, 0), (-1, -1), (4, -1)):
            f.art(P.PUFF, 28 + dx - (k - 6) // 2 * (1 if dx < 0 else -1) * 0, 32 + dy, cmap=None)
    # launch button
    pressed = 5 <= k <= 6
    f.rect(16, 33, 7, 3, 'g')
    f.rect(17, 31 + pressed, 5, 2, 'R')
    looking = k >= 7
    info = clawd(f, x=1, view='qr', ra='low' if pressed else ('wave' if k >= 14 and t % 2 else 'up' if k >= 14 else 'side'),
                 eyes='happy' if k >= 14 else ('closed' if pressed else 'normal'), lookv=-1 if looking else 0, look=1)
    if k < 5:
        P.say(f, info, '321'[min(2, k // 2)] if k < 6 else '', minw=7)
    elif 5 <= k <= 9:
        P.say(f, info, 'GO!')


# --------------------------------------------------------------------------- 9 git merge (two minis -> one)
def git_merge(f, t, n):
    k = t % n
    # graph
    f.line(5, 3, 17, 11, 'B'); f.line(34, 3, 22, 11, 'P'); f.rect(19, 11, 2, 6, 'E')
    p = min(1, k / 9)
    f.rect(int(5 + 12 * p) - 1, int(3 + 8 * p) - 1, 3, 3, 'B')
    f.rect(int(34 - 12 * p) - 1, int(3 + 8 * p) - 1, 3, 3, 'P')
    if k >= 10:
        f.rect(18, 15, 4, 4, 'E'); f.rect(19, 16, 2, 2, 'W')
    if k < 10:
        s = k % 2
        mini(f, -8 + int(k * 2.1), 28, legs=LG(s), view='qr')
        mini(f, 40 - int(k * 2.1), 28, legs=LG(not s), view='ql')
    elif k < 12:
        f.disc(20, 30, 5 + (k - 10) * 2, 'W')
        f.ring(20, 30, 6 + (k - 10) * 2, 'U')
        P.sparkles(f, k, 4, [(8, 22), (32, 24), (20, 19)])
    elif k < 22:
        j = k - 12
        clawd(f, eyes='happy' if j < 4 else 'blink' if j == 7 else 'normal',
              la='up' if j < 4 else 'side', ra='up' if j < 4 else 'side', y=BY - (1 if j in (1, 2) else 0))
    else:
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='closed')
        f.art(P.PUFF, 6, 30); f.art(P.PUFF, 30, 30)


# --------------------------------------------------------------------------- 10 commit graph grows
def git_graph(f, t, n):
    k = t % n
    x = -12 + int(k * 2.5)
    cx = x + 8
    f.rect(0, 7, 40, 1, 'g')
    nodes = [(4, 7, 'B'), (11, 7, 'B'), (18, 13, 'P'), (24, 13, 'P'), (31, 7, 'E'), (37, 7, 'B')]
    if cx >= 14:
        f.line(12, 8, 16, 12, 'P')
        f.rect(16, 13, min(cx, 27) - 16, 1, 'P')
    if cx >= 28:
        f.line(27, 12, 30, 8, 'P')
    for (nx, ny, c) in nodes:
        if cx >= nx:
            f.rect(nx - 1, ny - 1, 3, 3, c)
            if cx - nx < 3:
                f.box(nx - 2, ny - 2, 5, 5, 'U')
    s = k % 2
    info = clawd(f, x=x, y=BY + s, view='q2r', legs=LG(s), ra='up', eyes='happy' if s else 'normal')
    hx, hy = info['rh']
    P.item(f, (hx, hy), 'pencil')


# --------------------------------------------------------------------------- 11 refactor: fix indentation
def refactor(f, t, n):
    k = t % n
    window(f, 0, 2, 23, 32, bg='k')
    lens = [10, 7, 9, 5, 8, 6]
    ind = [0, 3, 6, 6, 3, 0]
    off = [7, 0, 1, 11, 9, 5]
    cols = 'CPEBFE'
    j = (k - 2) // 3
    for i in range(6):
        y = 7 + i * 4
        fixed = k >= 4 + i * 3 and k < 22
        if 0 <= j == i and k < 20:
            f.rect(1, y - 1, 21, 4, 'b')
        x = 2 + (ind[i] if fixed else off[i])
        if k == 3 + i * 3:
            x = 2 + (ind[i] + off[i]) // 2
        f.rect(x, y, 2, 2, 'G')
        f.rect(x + 3, y, lens[i], 2, cols[i])
    allok = 20 <= k < 22
    if allok:
        P.check(f, 16, 26)
    snap = any(k == 4 + i * 3 for i in range(6))
    clawd(f, x=24, view='q2l', la='out' if not allok else 'up', eyes='happy' if allok else 'normal',
          y=BY + (1 if snap else 0))
    if k >= 22:
        f.art(P.PUFF, 8, 14); f.art(P.PUFF, 4, 24)


# --------------------------------------------------------------------------- 12 rubber duck debugging
DUCK = [
    '...YYYY...',
    '..YUUUUY..',
    'FFYKUUUY..',
    'FFFYUUUY..',
    '..YUUUUYYY',
    '.YUUUUUUUY',
    '.YUUUUUUY.',
    '..YYYYYY..',
]


def rubber_duck(f, t, n):
    k = t % n
    f.rect(26, 33, 12, 3, 'B'); f.rect(26, 33, 12, 1, 'S')
    bob = 1 if (k in (9, 10)) else 0
    f.art(DUCK, 27, 25 + bob)
    if 9 <= k <= 13:
        f.art(P.QMARK, 33, 18 - (k % 2))
    if k < 14:
        info = clawd(f, x=2, view='q2r', eyes='normal' if k % 6 else 'blink', ra='mid' if (k // 2) % 2 else 'side')
        P.speech(f, 9, 3, 16, 9, c='B', tail='left')
        r = rng(k // 2)
        for row in range(2):
            ln = r.randint(4, 10)
            f.rect(11, 6 + row * 3, ln, 1, 'W')
    elif k < 20:
        j = k - 14
        dy = [0, -3, -5, -3, 0, 0][j]
        info = clawd(f, x=2, y=BY + dy, view='q2r', eyes='big', ra='up', la='up', legs=(1, 1, 1, 1) if dy else (0, 0, 0, 0))
        f.art(P.EXCL, 10, 6 + dy, cmap={'K': 'R'})
        f.art(P.EXCL, 12, 5 + dy, cmap={'K': 'R'})
    else:
        info = clawd(f, x=4, view='q2r', eyes='happy', ra='mid')
        f.art(P.HEART, 30, 20 - (k % 2))


# --------------------------------------------------------------------------- 13 "this is fine" (server on fire)
def flames(f, x, y, w, t, h=6, seed=0):
    r = rng(t * 13 + seed)
    for i in range(w):
        hh = r.randint(2, h)
        f.rect(x + i, y - hh, 1, hh, 'R')
        if hh > 2:
            f.rect(x + i, y - hh + 2, 1, hh - 2, 'F')
        if hh > 4 and i % 2:
            f.rect(x + i, y - hh + 4, 1, hh - 4, 'U')


def server_rack(f, x, y, w, h, t, leds=True, off=False, lit=None):
    f.rect(x, y, w, h, 'g')
    f.rect(x + 1, y + 1, w - 2, h - 2, 'k')
    for u in range((h - 2) // 5):
        uy = y + 2 + u * 5
        f.rect(x + 2, uy + 3, w - 4, 1, 'g')
        if leds and not off and (lit is None or u < lit):
            for j in range(3):
                on = (t + u * 2 + j) % 3 != 0
                f.put(x + 3 + j * 2, uy + 1, pick('EUE', j) if on else 'g')
        f.rect(x + w - 6, uy + 1, 3, 1, 'g')


def this_is_fine(f, t, n):
    server_rack(f, 25, 12, 13, 24, t)
    flames(f, 24, 12, 15, t, h=7)
    flames(f, 23, 36, 2, t + 1, h=10, seed=4)
    flames(f, 38, 36, 2, t + 2, h=12, seed=5)
    P.rising(f, P.PUFF, t, n, 30, 2, count=2, height=6, jitter=4, seed=3, cmap={'L': 'g'})
    info = clawd(f, x=3, y=BY + 2, leg_h=1, eyes='happy' if t % 8 != 5 else 'closed', ra='side')
    hx, hy = info['rh']
    P.item(f, (hx, hy - (1 if (t // 4) % 2 else 0)), 'mug')
    if (t // 8) % 2:
        P.say(f, info, 'FINE', dy=2)
    else:
        P.rising(f, ['L'], t, n, hx + 2, hy - 5, count=2, height=5, jitter=1)


# --------------------------------------------------------------------------- 14 coffee in, code out
TOKENS = ['{}', ';', '</>', '()', '=>', '[]']


def coffee_to_code(f, t, n):
    k = t % 8
    if k < 5:
        my = -6 + k * 4
        P.item(f, (18, my + 3), 'mug')
    gulp = k == 5
    s = t % 2
    info = clawd(f, x=BX + (0 if gulp else (1 if s else -1) if k > 5 else 0), y=BY + (1 if gulp else 0),
                 h=12 - (1 if gulp else 0), eyes='closed' if gulp else 'big' if k > 5 else 'normal',
                 lookv=-1 if k < 5 else 0, la='high' if s else 'mid', ra='mid' if s else 'high')
    if gulp:
        f.art(['.r.', 'r.r'], 26, 17)
    for i in range(3):
        p = ((t / n) + i / 3) % 1
        tok = TOKENS[(i + t // n) % len(TOKENS)]
        x = int(31 + p * 12)
        f.text(tok, x, 22 + i * 5, pick('BEP', i))
        tok2 = TOKENS[(i + 3) % len(TOKENS)]
        f.text(tok2, int(8 - p * 12) - text_w(tok2), 24 + i * 4, pick('FCE', i))


# --------------------------------------------------------------------------- 15 keyboard smash
def keyboard(f, x, y, w, t=0, hit=None):
    f.rect(x, y, w, 6, 'g')
    f.rect(x + 1, y + 1, w - 2, 4, 'G')
    for row in range(2):
        for kx in range(x + 2 + row, x + w - 2, 3):
            pressed = hit is not None and abs(kx - hit) < 6
            f.rect(kx, y + 1 + row * 2 + (1 if pressed else 0), 2, 1, 'w' if not pressed else 'g')


def keyboard_smash(f, t, n):
    k = t % 6
    smash = k in (2, 3)
    up = k in (0, 1)
    info = clawd(f, y=BY - 1 + (1 if smash else 0), eyes='angry', la='up' if up else 'low' if smash else 'mid',
                 ra='up' if up else 'low' if smash else 'mid')
    kx = 1 if smash and t % 2 else 0
    keyboard(f, 3 + kx, 30, 34, hit=None if not smash else 20)
    if smash:
        r = rng(t)
        for i in range(6):
            x = r.choice((r.randint(2, 7), r.randint(31, 36)))
            y = r.randint(22, 28)
            f.rect(x, y - (k - 2) * 2, 2, 1, pick('wGR', i))
        f.text(pick(['#@!', '%&$', '!?#'], t // 6), 3 + r.randint(0, 2), 10, 'R')
        f.text(pick(['%!', '#?', '@!'], t // 6), 29, 12, 'R')
    f.art(P.VEIN2 if t % 2 else P.VEIN, info['x'] + 11, info['y'] - 6)


# --------------------------------------------------------------------------- 16 404 not found
def big_text(f, s, x, y, c, k=2):
    from engine import FONT
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT['?'])
        for j, row in enumerate(g):
            for i, p in enumerate(row):
                if p == '#':
                    f.rect(cx + i * k, y + j * k, k, k, c)
        cx += (len(g[0]) + 1) * k
    return cx - x - k


def not_found(f, t, n):
    k = t % n
    for i, ch in enumerate('404'):
        bounce = 2 if (k // 2) % 6 == i else 0
        big_text(f, ch, 9 + i * 8, 3 - bounce, 'R' if ch == '4' else 'g')
    f.text_c('NOT FOUND', 20, 15, 'g')
    seq = ['ql', 'ql', 'front', 'qr', 'qr', 'front']
    j = (k // 4) % 6
    if k >= 16:
        clawd(f, la='high', ra='high', y=BY - 1, eyes='closed')
        f.art(P.QMARK, 6, 18 - (k % 2)); f.art(P.QMARK, 31, 18 - ((k + 1) % 2))
    else:
        clawd(f, view=seq[j], eyes='normal' if k % 7 else 'blink', ra='up' if j in (2, 5) else 'side')
        if j in (2, 5):
            f.art(P.QMARK, 27, 18)


# --------------------------------------------------------------------------- 17 hourglass wait
def hourglass(L, x, y, p, stream):
    """11 wide x 17 tall. p = fraction of sand in the bottom chamber."""
    cx = x + 5
    half = [3, 3, 3, 2, 1, 0, 0, 0, 1, 2, 3, 3, 3]
    L.rect(x, y, 11, 2, 'N'); L.rect(x, y + 15, 11, 2, 'N')
    ntop = int(round(5 * (1 - p)))
    nbot = int(round(5 * p))
    for r in range(13):
        yy = y + 2 + r
        h_ = half[r]
        L.put(cx - h_ - 1, yy, 'g'); L.put(cx + h_ + 1, yy, 'g')
        if 5 - ntop <= r < 5:
            L.rect(cx - h_, yy, 2 * h_ + 1, 1, 'Y')
        if r >= 13 - nbot:
            L.rect(cx - h_, yy, 2 * h_ + 1, 1, 'Y')
    if stream:
        L.rect(cx, y + 7, 1, max(1, 13 - nbot - 5), 'Y')


def hourglass_wait(f, t, n):
    k = t % n
    L = Canvas()
    if k < 20:
        hourglass(L, 26, 17, k / 19, 0 < k < 19)
        f.blit(L)
    elif k < 22:
        hourglass(L, 26, 17, 1, False)
        f.blit(L.rot90(k - 19, 31.5, 25.5))
    else:
        hourglass(L, 26, 17, 0, False)
        f.blit(L)
    flip = 19 <= k < 22
    droop = 0 if k < 8 else 1
    eyes = 'big' if flip else ('line' if k >= 12 else 'normal')
    info = clawd(f, x=4, y=BY + 2 + droop, h=12 - droop, leg_h=1, view='q2r', top=bool(droop) and not flip,
                 eyes=eyes, ra='out' if flip else 'side')
    if 14 <= k < 19:
        P.zzz(f, info, k, 6)


# --------------------------------------------------------------------------- 18 Claude Code thinking spinner
def thinking(f, t, n):
    seq = [0, 1, 2, 3, 3, 2, 1, 0]
    spark(f, 7, 8, seq[t % 8], c='F')
    f.text('THINK', 13, 6, 'O')
    for d in range((t // 2) % 4):
        f.put(33 + d * 2, 10, 'O')
    look = [0, 1, 1, 0, -1, -1][(t // 2) % 6]
    b = 1 if (t // 3) % 2 else 0
    clawd(f, eyes='normal' if t % 12 != 9 else 'blink', look=look, lookv=-1, ra='chin', y=BY + b, h=12 - b)
    for i in range(3):
        p = ((t / n) + i / 3) % 1
        f.rect(int(10 + i * 9 + math.sin(p * 6.28) * 2), int(12 + p * 7), 1, 1, pick('PBE', i))


# --------------------------------------------------------------------------- 19 wrench on a gear (tool use)
def gear(f, cx, cy, r, a, c='g', c2='G', teeth=8):
    f.disc(cx, cy, r, c)
    f.ring(cx, cy, r - 1.5, c2)
    f.disc(cx, cy, 1.6, 'k')
    for i in range(teeth):
        ang = a + i * 2 * math.pi / teeth
        tx, ty = cx + math.cos(ang) * (r + 0.8), cy + math.sin(ang) * (r + 0.8)
        f.rect(int(tx - 1), int(ty - 1), 2, 2, c)


def wrench_gear(f, t, n):
    a = 2 * math.pi * t / n / 4
    gear(f, 30, 22, 6, a)
    gear(f, 21.5, 9.5, 3.5, -a * 2 + 0.3, c='N', c2='T', teeth=6)
    s = (t // 2) % 2
    info = clawd(f, x=0, view='q2r', ra='high' if s else 'low', eyes='focus' if s else 'angry',
                 y=BY + (0 if s else 1))
    hx, hy = info['rh']
    hub = (29, 22)
    f.line(hx, hy, hub[0], hub[1], 'G')
    f.line(hx, hy + 1, hub[0], hub[1] + 1, 'g')
    f.art(['GGG', 'G.G', 'GGG'], hub[0] - 1, hub[1] - 1)
    if t % 4 == 1:
        f.art(P.SPARK, 36, 13)
    if t % 4 == 3:
        f.art(['U.U', '.U.', 'U.U'], 25, 30)


# --------------------------------------------------------------------------- 20 endless docs scroll
def docs_scroll(f, t, n):
    f.rect(19, 2, 20, 2, 'N'); f.rect(20, 1, 18, 1, 'T')
    f.rect(21, 4, 16, 30, 'W'); f.rect(21, 4, 1, 30, 'G'); f.rect(36, 4, 1, 30, 'G')
    f.rect(21, 34, 16, 1, 'G'); f.rect(22, 35, 15, 1, 'G')
    r = rng(9)
    lines = [(r.randint(5, 12), pick('kkBkgk', i)) for i in range(8)]
    for i, (ln, c) in enumerate(lines):
        y = 5 + (i * 4 - t) % 32
        if 5 <= y <= 31:
            f.rect(23, y, ln, 1, c)
            if c == 'g':
                f.rect(23, y + 1, ln - 2, 1, 'g')
    lv = [-1, 0, 1, 1, 0, -1][(t // 2) % 6]
    flick = t % 4 == 0
    clawd(f, x=1, view='q2r', ra='high' if flick else 'mid', eyes='normal' if t % 11 else 'blink', lookv=lv)
    if flick:
        f.art(['.W', 'W.'], 19, 20)


# --------------------------------------------------------------------------- 21 LGTM stamp
def long_tool(f, hand, tip, c='R', c2=None, tipc='k'):
    """A long pen / stylus held in Clawd's claw, reaching from the hand to the tip."""
    hx, hy = int(hand[0]), int(hand[1])
    f.line(hx, hy, tip[0], tip[1], c)
    if c2:
        f.line(hx, hy - 1, tip[0], tip[1] - 1, c2)
    f.put(tip[0], tip[1], tipc)


def lgtm(f, t, n):
    k = t % n
    if k < 3:
        sy, arms, eyes = 5, 'up', 'normal'
    elif k < 6:
        sy, arms, eyes = 5 - (k - 3) * 2, 'up', 'focus'
    elif k == 6:
        sy, arms, eyes = 21, 'low', 'closed'
    else:
        sy, arms, eyes = [9, 6, 5, 5, 5, 5, 5, 5, 5][k - 7], 'up', 'happy' if k < 12 else 'normal'
    up = arms == 'up'
    info = clawd(f, y=BY - 2, la=arms, ra=arms, eyes=eyes, look=-1 if k >= 12 else 0)
    px = 8 if k < 12 else 8 - (k - 11) * 9
    py = 28 if k >= 3 else 40 - (k + 1) * 4
    f.rect(px, py, 24, 10, 'W'); f.box(px, py, 24, 10, 'G')
    for i in range(3):
        f.rect(px + 3, py + 2 + i * 2, [14, 9, 16][i], 1, 'g')
    if k >= 6:
        f.rect(px + 2, py + 1, 20, 8, 'W')
        f.box(px + 2, py + 1, 20, 8, 'E')
        f.text('LGTM', px + 5, py + 2, 'E')
    if not up and k == 6:
        f.art(['K...K', '.K.K.'], 2, 27); f.art(['K.K', '.K.'], 34, 27)
    # stamp: wide rubber plate held overhead with both claws
    f.rect(17, sy, 6, 3, 'N'); f.rect(19, sy + 3, 2, 2, 'n')
    f.rect(10, sy + 5, 20, 2, 'n'); f.rect(10, sy + 7, 20, 1, 'E')


# --------------------------------------------------------------------------- 22 pair programming
def pair_program(f, t, n):
    k = t % n
    monitor(f, 24, 10, 15, 13)
    rows = min(5, k // 2 + 1)
    for i in range(rows):
        c = 'R' if (i == 3 and k < 10) else ('E' if i == 3 else pick('CPBF', i))
        f.rect(26, 12 + i * 2, [6, 9, 4, 8, 5][i], 1, c)
    if 8 <= k < 10:
        f.box(25, 17, 12, 3, 'U')
    s = t % 2
    clawd(f, x=4, view='q2r', ra='mid' if s else 'low', eyes='focus' if k < 8 else 'normal')
    point = 6 <= k < 12
    mini(f, 8, 14 - (1 if point and s else 0), view='qr', ra='high' if point else 'side',
         eyes='normal' if k % 10 else 'closed')
    if point:
        f.art(P.EXCL, 18, 6, cmap={'K': 'R'})
    elif k >= 12:
        f.art(P.HEART, 18, 8 - (k % 2))


# --------------------------------------------------------------------------- 23 code review with a red pen
def red_pen(f, t, n):
    k = t % n
    f.rect(2, 4, 19, 30, 'W'); f.box(2, 4, 19, 30, 'G')
    for i in range(7):
        f.rect(4 + (i % 3) * 2, 7 + i * 4, [10, 8, 12, 6, 9, 11, 7][i], 1, 'g')
    pts = []
    for j in range(min(k + 1, 8)):
        a = j / 7 * 2 * math.pi
        pts.append((11 + 7 * math.cos(a), 15 + 2.4 * math.sin(a)))
    for (x, y) in pts:
        f.put(x, y, 'R')
    tip = pts[-1]
    if k >= 8:
        ln = min(k - 7, 6)
        f.rect(6, 23, ln * 2, 1, 'R')
        tip = (6 + ln * 2, 23)
    if k >= 14:
        qa = ['.RR.', 'R..R', '...R', '..R.', '....', '..R.']
        rows = min(6, k - 13)
        f.art(qa[:rows], 15, 26)
        tip = (17, 26 + rows)
    if k >= 20:
        tip = (19 + (k - 20), 31 - (k - 20))
    tx, ty = int(tip[0]), int(tip[1])
    info = clawd(f, x=24, view='q2l', la='out', eyes='focus' if k < 20 else 'happy')
    long_tool(f, info['lh'], (tx, ty), c='R', c2='M')


# --------------------------------------------------------------------------- 24 ship it box
def ship_box(f, x, y, taped, label):
    f.rect(x, y, 17, 11, 'N'); f.box(x, y, 17, 11, 'n')
    f.rect(x, y, 17, 2, 'n')
    if taped:
        f.rect(x + 7, y, 3, 4, 'T')
    if label:
        f.text('SHIP', x + 1, y + 4, 'W')


def ship_it(f, t, n):
    k = t % n
    if k < 4:
        by = -11 + k * 9
        ship_box(f, 20, min(25, by), False, False)
        clawd(f, x=2, view='q2r', eyes='normal', lookv=-1)
        return
    if k < 12:
        squash = k == 4
        ship_box(f, 20, 25 + squash, k >= 6, k >= 9)
        work = 6 <= k <= 9
        clawd(f, x=3, view='q2r', ra='high' if work and k % 2 else 'mid' if work else 'side',
              eyes='happy' if k in (10, 11) else 'focus')
        if k in (6, 9):
            f.art(P.SPARK, 27, 20)
        if k == 4:
            P.dust(f, 18, GROUND, 0.5); P.dust(f, 38, GROUND, 0.5, flip=True)
        return
    j = k - 12
    if j < 7:
        bx = 20 + j * 4
        ship_box(f, bx, 25, True, True)
        s = j % 2
        clawd(f, x=bx - 19, y=BY + s, view='q2r', legs=LG(s), ra='mid', eyes='angry' if j < 2 else 'happy')
        P.speedlines(f, bx - 20, 24, t, n=3, length=4)
    else:
        s = j % 2
        clawd(f, x=25 - (j - 6) * 5, y=BY + s, view='q2l', legs=LG(s), eyes='happy')
        f.text('SHIPPED', 6, 6, 'E')


# --------------------------------------------------------------------------- 25 cloud upload
FILE = ['GGGGG.', 'GWWWGG', 'GWkkWG', 'GWWWWG', 'GWkkkG', 'GWWWWG', 'GGGGGG']


def big_cloud(f, x, y, w, c='w', edge='G'):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        P.cloud(f, x + dx, y + dy, c=edge, w=w)
    P.cloud(f, x, y, c=c, w=w)


def cloud_upload(f, t, n):
    k = t % n
    big_cloud(f, 11, 1, 18)
    p = min(1, max(0, (k - 3) / 8))
    P.progress(f, 13, 9, 14, p if k < 16 else 1, c='B', bg='g')
    if 12 <= k < 18:
        P.check(f, 17, 2)
    for i in range(2):
        yy = 18 - ((t * 2 + i * 4) % 8)
        f.art(['.B.', 'B.B'], 19, yy)
    up = k < 3 or k >= 16
    cheer = 12 <= k < 16
    info = clawd(f, la='up' if (up or cheer) else 'high', ra='up' if (up or cheer) else 'high',
                 eyes='happy' if cheer else 'normal', lookv=-1, y=BY - (1 if cheer and t % 2 else 0))
    if k < 3:
        f.art(FILE, 17, 11)
    elif k < 11:
        fy = 11 - (k - 3) * 2
        if fy > 4:
            f.art(FILE, 17, fy)
    elif k >= 16:
        s = [0.3, 0.7, 1.0, 1.0][k - 16]
        L = Canvas(); L.art(FILE, 17, 11)
        f.blit(L.scale(s, 20, 18))


# --------------------------------------------------------------------------- 26 overheating CPU
def cpu_overheat(f, t, n):
    heat = 'R' if t % 2 else 'F'
    for i in range(4):
        f.rect(24 + i * 3, 15, 1, 2, 'G'); f.rect(24 + i * 3, 29, 1, 2, 'G')
        f.rect(21, 18 + i * 3, 2, 1, 'G'); f.rect(35, 18 + i * 3, 2, 1, 'G')
    f.rect(23, 17, 12, 12, 'g'); f.rect(24, 18, 10, 10, 'k')
    f.disc(29, 23, 4, 'g')
    a = t * math.pi / 4
    for d in (0, math.pi / 2):
        f.line(29 - 3 * math.cos(a + d), 23 - 3 * math.sin(a + d), 29 + 3 * math.cos(a + d), 23 + 3 * math.sin(a + d), 'w')
    f.rect(28, 22, 2, 2, heat)
    for i in range(3):
        p = ((t / 6) + i / 3) % 1
        y = int(13 - p * 10)
        for j in range(4):
            f.put(25 + i * 3 + (1 if (j + int(p * 6)) % 2 else 0), y - j, 'R' if p < 0.5 else 'F')
    # thermometer
    f.rect(37, 4, 3, 20, 'G'); f.rect(38, 5, 1, 18, 'W')
    lvl = 10 + (t % 4) * 2
    f.rect(38, 23 - lvl, 1, lvl, 'R'); f.disc(38.5, 24.5, 2, 'R')
    s = t % 2
    info = clawd(f, x=0, view='q2r', ra='high' if s else 'low', eyes='worried')
    hx, hy = info['rh']
    f.art(['GGGG', 'GWWG', 'GWWG', 'GWWG', 'GGGG'] if s else ['GGGGG', 'GWWWG', 'GGGGG'], int(hx), int(hy) - 3)
    f.art(P.SWEAT, info['x'] - 3, info['y'] - 4 + t % 3, flip=True)


# --------------------------------------------------------------------------- 27 infinite loop
def infinite_loop(f, t, n):
    a = 2 * math.pi * t / n
    cx, cy, rx, ry = 12, BY, 12, 4
    x = int(round(cx - rx * math.cos(a)))
    y = int(round(cy + ry * math.sin(a)))
    front = math.sin(a) >= 0
    for i in range(24):
        b = 2 * math.pi * i / 24
        f.put(20 - 15 * math.cos(b), 34 + 3.5 * math.sin(b), 'G')
    s = t % 2

    def runner():
        L = Canvas()
        clawd(L, x=x, y=y + s, view='qr' if front else 'ql', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2),
              eyes='focus' if front else 'normal', la='low', ra='low')
        if front:
            f.blit(L.shear(-0.06, y + 15))
            P.speedlines(f, x - 1, y + 2, t, n=3, length=4)
        else:
            f.blit(L.shear(0.06, y + 15))

    if not front:
        runner()
    f.rect(19, 13, 2, 23, 'N')
    f.rect(2, 4, 36, 10, 'T'); f.box(2, 4, 36, 10, 'N')
    f.text('WHILE(1)', 4, 7, 'n')
    if front:
        runner()


# --------------------------------------------------------------------------- 28 todo list ticked off
def todo(f, t, n):
    k = t % n
    f.rect(3, 5, 19, 30, 'N'); f.rect(4, 7, 17, 27, 'W')
    f.rect(9, 3, 7, 4, 'g'); f.rect(10, 4, 5, 2, 'G')
    done = sum(1 for i in range(4) if k >= 3 + i * 5)
    if k >= 22:
        done = 4
    for i in range(4):
        y = 10 + i * 6
        f.box(6, y, 4, 4, 'g')
        ln = [9, 7, 8, 6][i]
        f.rect(11, y + 1, ln, 1, 'G' if i < done else 'k')
        if i < done:
            f.rect(11, y + 1, ln, 1, 'G')
            f.art(['....E', '...E.', 'E.E..', '.E...'], 6, y - 1)
    cur = min(done, 3)
    tick = any(k == 3 + i * 5 for i in range(4))
    info = clawd(f, x=24, view='q2l', la='out', eyes='happy' if done == 4 else 'normal', y=BY + (1 if tick else 0))
    tx, ty = 8 + (2 if tick else 0), 12 + cur * 6 - (1 if tick else 0)
    if done == 4:
        tx, ty = 20, 30
        P.sparkles(f, t, n, [(30, 14), (36, 18), (25, 10)])
    long_tool(f, info['lh'], (tx + 1, ty + 1), c='Y', c2='U')


# --------------------------------------------------------------------------- 29 pomodoro timer
def pomodoro(f, t, n):
    k = t % n
    ring = 16 <= k < 22
    dx = (1 if t % 2 else -1) if ring else 0
    cx, cy = 30 + dx, 27
    f.disc(cx, cy, 7, 'R')
    f.disc(cx - 2, cy - 2, 2, 'Z')
    f.art(['e.E.e', '.eEe.', '..e..'], int(cx) - 2, cy - 9)
    f.rect(int(cx) - 5, cy - 1, 10, 3, 'T')
    off = (k * 2) if k < 16 else 32
    for i in range(6):
        xx = int(cx) - 5 + (i * 4 - off) % 10
        f.rect(xx, cy - 1, 1, 2 if i % 2 else 1, 'n')
    f.put(int(cx), cy - 2, 'k'); f.put(int(cx), cy + 2, 'k')
    if ring:
        for (rx, ry) in ((-10, -4), (8, -6), (-9, 3), (9, 2)):
            if (t + rx) % 2:
                f.art(['K.', '.K'] if rx < 0 else ['.K', 'K.'], int(cx) + rx, cy + ry, cmap={'K': 'R'})
    if k < 16:
        s = t % 2
        clawd(f, x=1, view='q2r', ra='mid' if s else 'low', eyes='focus')
        f.rect(19, 30, 5, 1, 'g'); f.rect(18, 31, 6, 1, 'G')
    elif ring:
        j = k - 16
        dy = [-5, -7, -6, -3, 0, 0][j]
        clawd(f, x=1, y=BY + dy, view='q2r', la='up', ra='up', eyes='big', legs=(1, 1, 1, 1) if dy else (0, 0, 0, 0))
        f.art(P.EXCL, 9, 10 + dy, cmap={'K': 'R'})
    else:
        clawd(f, x=3, view='q2r', ra='out', eyes='closed' if k == 22 else 'normal')


# --------------------------------------------------------------------------- 30 slide with growing bar chart
def slide_chart(f, t, n):
    k = t % n
    f.rect(8, 1, 31, 21, 'W'); f.box(8, 1, 31, 21, 'G'); f.rect(8, 22, 31, 1, 'g')
    f.rect(11, 18, 25, 1, 'g')
    hs = [5, 9, 14]
    tops = []
    for i, (h, c) in enumerate(zip(hs, 'BEF')):
        g = min(h, max(0, int((k - i * 4) * 1.5)))
        if k >= 20:
            g = h + (1 if (t + i) % 2 and i == 2 else 0)
        f.rect(13 + i * 8, 18 - g, 5, g, c)
        tops.append((15 + i * 8, 18 - g))
    if k >= 16:
        f.line(14, 11, 31, 3, 'R'); f.art(['RRR', '.RR', 'R.R'], 30, 2)
    cur = min(2, k // 5)
    tx, ty = tops[cur]
    info = clawd(f, x=-1, y=BY + 1, view='q2r', ra='high', eyes='happy' if k >= 16 else 'normal', lookv=-1 if k < 16 else 0)
    hx, hy = info['rh']
    f.line(hx, hy, tx, ty - 1, 'N')
    f.put(tx, ty - 1, 'R')


# --------------------------------------------------------------------------- 31 inbox zero
ENV = ['GGGGGGGGG', 'GGWWWWWGG', 'GWGWWWGWG', 'GWWGGGWWG', 'GWWWWWWWG', 'GGGGGGGGG']


def inbox_zero(f, t, n):
    k = t % n
    if k < 20:
        cnt = 5 - k // 4
        fling = k % 4
    else:
        cnt, fling = 0, -1
    f.rect(2, 34, 13, 2, 'g'); f.rect(2, 30, 1, 4, 'g'); f.rect(14, 30, 1, 4, 'g')
    if k >= 22:
        for i in range(k - 21):
            f.art(ENV, 4, 28 - i * 3 - (23 - k) * 6)
    for i in range(cnt):
        f.art(ENV, 4, 28 - i * 3)
    if cnt:
        f.disc(14, 13 - 0, 3.5, 'R')
        f.text(str(cnt), 13, 11, 'W')
    if 0 <= fling and k < 20:
        p = fling / 3
        ex = int(18 + p * 24)
        ey = int(14 - 10 * math.sin(p * math.pi))
        f.art(ENV, ex, ey)
    zero = 20 <= k < 22
    info = clawd(f, x=16, view='q2l' if fling in (0, 1) else 'front',
                 la='out' if fling == 0 else 'up' if fling in (1, 2) else 'side',
                 ra='up' if zero else 'side', eyes='happy' if zero or cnt == 0 else 'focus')
    if cnt == 0 and k < 22:
        f.text('INBOX 0', 6, 4, 'E')
        P.sparkles(f, t, n, [(4, 14), (35, 12), (20, 3)])


# --------------------------------------------------------------------------- 32 ctrl+c ctrl+v clones
def keycap(f, x, y, label, down=False):
    w = text_w(label) + 4
    f.rect(x, y + 1, w, 7, 'g')
    f.rect(x, y + (1 if down else 0), w, 6, 'G')
    f.rect(x + 1, y + 1 + (1 if down else 0), w - 2, 4, 'w')
    f.text(label, x + 2, y + 1 + (1 if down else 0), 'k')
    return w


def copy_paste(f, t, n):
    k = t % n
    if k < 4:
        cnt, combo = 1, 'C'
    elif k < 18:
        cnt, combo = (2 if k < 8 else 3), 'V'
    else:
        cnt, combo = (2 if k < 20 else 1), 'Z'
    down = (k % 4) in (1, 2)
    w = keycap(f, 0, 0, 'CTRL', down=down)
    f.text('+', w + 1, 1, 'g')
    keycap(f, w + 5, 0, combo, down=down)
    spots = [(0, BY), (22, BY), (22, BY - 13)]
    party = 12 <= k < 18
    s = (t // 2) % 2
    for i in [j for j in (0, 2, 1) if j < cnt]:
        x, y = spots[i]
        up = party and (s + i) % 2
        clawd(f, x=x, y=y - (1 if up else 0), eyes='happy' if party else ('normal' if i == 0 else 'big'),
              la='up' if up else 'side', ra='up' if up else 'side', view='front' if i else ('qr' if k >= 4 else 'front'))
    if k < 4:
        for i in range(0, 24, 2):
            f.put(-3 + i, BY - 2, 'B'); f.put(-3 + i, BY + 16, 'B')
        for i in range(0, 18, 2):
            f.put(20, BY - 2 + i, 'B')
    for (kk, i) in ((4, 1), (8, 2), (18, 2), (20, 1)):
        if kk <= k < kk + 2:
            x, y = spots[i]
            f.art(P.PUFF, x - 4, y + 4); f.art(P.PUFF, x + 16, y + 2)
            if kk < 12:
                P.sparkles(f, 0, 4, [(x + 2, y - 3), (x + 14, y - 4)])


# --------------------------------------------------------------------------- 33 task stack topples
def task_topple(f, t, n):
    k = t % n
    cols = 'BEPFCZ'
    if k < 18:
        cnt = min(5, k // 3 + 1)
        S_ = Canvas()
        for i in range(cnt):
            y = BY - 4 - i * 4
            fall = (k % 3) if i == cnt - 1 and k < 15 else 2
            y -= (2 - fall) * 5
            S_.rect(13, y, 14, 4, 'k'); S_.rect(14, y + 1, 12, 2, cols[i]); S_.rect(15, y + 1, 4, 1, 'W')
        sway = 0 if k < 12 else [0.05, -0.08, 0.12, -0.14, 0.2, 0.3][k - 12]
        f.blit(S_.shear(sway, BY) if sway else S_)
        clawd(f, la='up', ra='up', eyes='normal' if k < 12 else 'worried', look=-1 if sway > 0 else 1 if sway < 0 else 0,
              legs=(0, 0, 0, 0) if k < 12 else ((1, 0, 0, 0) if t % 2 else (0, 0, 0, 1)), x=BX + (int(-sway * 8) if k >= 12 else 0))
    else:
        j = k - 18
        for i in range(5):
            gx = [27, 31, 3, 24, 34][i]
            gy = min(33, [10, 6, 12, 2, 8][i] + j * 8)
            f.rect(gx, gy, 6 if i % 2 else 8, 3, 'k'); f.rect(gx + 1, gy + 1, 4 if i % 2 else 6, 1, cols[i])
        if j < 3:
            clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='x')
        else:
            clawd(f, eyes='closed' if j == 3 else 'normal', la='side', ra='side')
        if j >= 2:
            P.orbit(f, 20, BY - 2, 8, 2, t, 6, ['.U.', 'UUU', '.U.'], count=3)


# --------------------------------------------------------------------------- 34 battery low -> charging
def battery_charge(f, t, n):
    k = t % n
    if k < 8:
        lvl = 4 - k // 2
    elif k < 12:
        lvl = 0
    elif k < 24:
        lvl = min(4, (k - 12) // 2)
    else:
        lvl = 4
    f.rect(11, 2, 17, 9, 'g'); f.rect(28, 4, 2, 5, 'g'); f.rect(12, 3, 15, 7, 'W')
    c = 'E' if lvl >= 3 else 'U' if lvl == 2 else 'R'
    for i in range(lvl):
        f.rect(13 + i * 3 + (i > 1), 4, 3, 5, c)
    if lvl == 0 and t % 2 and k < 12:
        f.rect(13, 4, 1, 5, 'R')
    plugged = 10 <= k < 26
    if 12 <= k < 24:
        f.art(P.BOLT, 18, 4, cmap={'U': 'U'}) if t % 2 else None
    tired = 1 if 4 <= k < 14 else 0
    if k < 14:
        eyes = 'normal' if k < 4 else 'line' if k < 8 else 'closed'
        info = clawd(f, y=BY + 1 + tired, h=12 - tired, eyes=eyes, la='low', ra='low', top=bool(tired))
    elif k < 22:
        info = clawd(f, eyes='normal' if k < 18 else 'big', ra='side', la='side')
    else:
        dy = [0, -3, -5, -3, 0, 0][k - 22]
        info = clawd(f, y=BY + dy, eyes='happy', la='up', ra='up', legs=(1, 1, 1, 1) if dy else (0, 0, 0, 0))
    if 8 <= k < 28:
        px = 40 - (min(k, 10) - 7) * 4 if k < 10 else 30 if k < 26 else 30 + (k - 25) * 4
        py = info['y'] + 8
        f.rect(px + 4, py + 1, 40, 1, 'g')
        f.rect(px, py, 4, 3, 'g'); f.rect(px - 2, py, 2, 1, 'G'); f.rect(px - 2, py + 2, 2, 1, 'G')
    if 22 <= k:
        P.sparkles(f, t, n, [(5, 16), (35, 18), (8, 28)])


# --------------------------------------------------------------------------- 35 wifi search
def wifi(f, cx, cy, bars, c='B', off='G'):
    for r in range(1, 4):
        cc = c if bars >= r else off
        rr = r * 3
        for x in range(-rr - 1, rr + 2):
            for y in range(-rr - 1, 1):
                d = math.hypot(x + .5, y + .5)
                if rr - 1.2 <= d <= rr and -y - 0.5 >= abs(x + .5) * 0.75:
                    f.put(cx + x, cy + y, cc)
    f.rect(cx - 1, cy, 2, 2, c if bars >= 0 else off)


def wifi_search(f, t, n):
    k = t % n
    xs = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 22, 22, 22, 22, 20, 17, 14, 11, 8, 6, 4, 2, 2]
    x = xs[k]
    bars = max(0, 3 - abs(x - 22) // 5)
    if k in (11, 12, 13, 14):
        bars = 3
    still = 10 <= k <= 14
    s = t % 2
    info = clawd(f, x=x, y=BY + (0 if still else s), view='front' if still else ('qr' if k < 10 else 'ql'),
                 legs=(0, 0, 0, 0) if still else LG(s), la='up', ra='up',
                 eyes='happy' if bars == 3 else 'worried' if bars == 0 else 'normal', lookv=-1)
    lx = x + 3
    f.rect(lx, BY - 9, 10, 6, 'g'); f.rect(lx + 1, BY - 8, 8, 4, 'k')
    f.rect(lx - 1, BY - 3, 12, 1, 'G')
    if bars == 3:
        f.rect(lx + 2, BY - 7, 6, 1, 'E'); f.rect(lx + 2, BY - 5, 4, 1, 'E')
    wifi(f, lx + 5, BY - 12, bars - 1 if bars else -1)
    if bars == 0 and t % 4 < 2:
        f.art(P.QMARK, lx + 11, BY - 19)


# --------------------------------------------------------------------------- 36 matrix rain
def matrix_rain(f, t, n):
    r = rng(31)
    cols = [(x, r.random(), r.choice((1, 2))) for x in range(1, 40, 5)]
    glyphs = '01ABZ7'

    def rain(front):
        for i, (x, off, sp) in enumerate(cols):
            if (x in (1, 36)) != front:
                continue
            head = (t / n * sp + off) % 1 * 52
            for j in range(6):
                y = int(head) - j * 6
                if -6 < y < 40:
                    ch = glyphs[(i + j + t // 2) % len(glyphs)]
                    f.text(ch, x, y, 'E' if j == 0 else 'e')

    rain(False)
    nod = 1 if (t // 2) % 2 else 0
    clawd(f, x=BX + 1, y=BY + nod, h=12 - nod, eyes='down' if nod else 'focus', top=bool(nod))
    rain(True)


# --------------------------------------------------------------------------- 37 robot arm
def ik(sx, sy, ex, ey, l1, l2):
    dx, dy = ex - sx, ey - sy
    d = max(1e-3, min(l1 + l2 - 0.01, math.hypot(dx, dy)))
    a = math.atan2(dy, dx)
    b = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    ang = a - b
    return sx + l1 * math.cos(ang), sy + l1 * math.sin(ang)


def robot_arm(f, t, n):
    k = t % n
    path = [(19, 30), (19, 30), (16, 18), (8, 13), (4, 18), (4, 25), (4, 25), (6, 16), (14, 15), (19, 22),
            (19, 30), (19, 30)]
    m = len(path)
    q = k / n * (m - 1)
    i0 = int(q)
    fr = q - i0
    ex = path[i0][0] + (path[min(m - 1, i0 + 1)][0] - path[i0][0]) * fr
    ey = path[i0][1] + (path[min(m - 1, i0 + 1)][1] - path[i0][1]) * fr
    carrying = 1.5 <= q < 5.5
    sx, sy = 11, 28
    jx, jy = ik(sx, sy, ex, ey, 11, 11)
    f.rect(0, 30, 6, 6, 'g'); f.rect(0, 30, 6, 1, 'G')
    f.rect(8, 30, 7, 6, 'g'); f.rect(9, 28, 5, 2, 'k')
    if q >= 5.5 or q < 0.5:
        f.rect(1, 26, 4, 4, 'B'); f.rect(1, 26, 4, 1, 'S')
    if q < 1.5:
        f.rect(17, 32, 5, 4, 'B'); f.rect(17, 32, 5, 1, 'S')
    for (ax, ay, bx, by) in ((sx, sy, jx, jy), (jx, jy, ex, ey)):
        f.line(ax, ay, bx, by, 'G'); f.line(ax + 1, ay, bx + 1, by, 'g')
    f.rect(int(jx) - 1, int(jy) - 1, 3, 3, 'g'); f.put(int(jx), int(jy), 'Y')
    cx, cy = int(ex), int(ey)
    if carrying:
        f.rect(cx - 2, cy + 2, 5, 4, 'B'); f.rect(cx - 2, cy + 2, 5, 1, 'S')
    open_ = not carrying
    f.rect(cx - 2, cy, 5, 2, 'g')
    f.rect(cx - 3 - open_, cy + 1, 1, 3, 'g'); f.rect(cx + 3 + open_, cy + 1, 1, 3, 'g')
    tilt = -1 if ex < 12 else 1
    clawd(f, x=24, view='q2l', la='low', eyes='focus', look=0)
    f.rect(27, 34, 7, 2, 'g'); f.rect(27, 33, 7, 1, 'G')
    f.line(30, 32, 30 + tilt, 31, 'g'); f.rect(29 + tilt, 30, 2, 1, 'R')


# --------------------------------------------------------------------------- 38 pixel art editor
SPRITE = ['........', '.OOOOOO.', '.OKOOKO.', 'OOOOOOOO', '.OOOOOO.', '.OOOOOO.', '.O.O.O.O', '........']


def pixel_editor(f, t, n):
    k = t % n
    gx, gy = 2, 8
    f.rect(gx - 1, gy - 1, 18, 18, 'g')
    for yy in range(8):
        for xx in range(8):
            f.rect(gx + xx * 2, gy + yy * 2, 2, 2, 'W' if (xx + yy) % 2 else 'w')
    cells = [(xx, yy) for yy in range(8) for xx in range(8) if SPRITE[yy][xx] != '.']
    shown = len(cells) if k >= 20 else int(len(cells) * k / 20)
    for (xx, yy) in cells[:shown]:
        f.rect(gx + xx * 2, gy + yy * 2, 2, 2, SPRITE[yy][xx])
    for i, c in enumerate('OKEBRU'):
        f.rect(2 + i * 3, 3, 2, 2, c)
    f.box(1 + (0 if k % 4 else 3), 2, 4, 4, 'k')
    if shown:
        cx, cy = cells[min(shown, len(cells)) - 1]
        tx, ty = gx + cx * 2 + 1, gy + cy * 2 + 1
    else:
        tx, ty = gx + 3, gy + 3
    if k >= 20:
        tx, ty = 20, 30
        P.sparkles(f, t, n, [(1, 7), (19, 9), (10, 27)])
    info = clawd(f, x=24, view='q2l', la='out', eyes='happy' if k >= 20 else 'focus')
    long_tool(f, info['lh'], (tx, ty), c='g', c2='G')


# --------------------------------------------------------------------------- 39 git blame
def git_blame(f, t, n):
    k = t % n
    window(f, 1, 0, 38, 20)
    for i in range(4):
        y = 5 + i * 4
        hot = i == 2 and k >= 3
        if hot:
            f.rect(2, y - 1, 36, 4, 'M')
        f.rect(3, y, 3, 2, 'O' if i == 2 else pick('BPE', i))
        f.put(4, y, 'k')
        f.rect(8, y, [14, 20, 17, 11][i], 1, 'R' if hot else 'G')
    if k >= 5:
        f.text('BLAME', 17, 14, 'U')
    seq = k // 4
    if seq < 2:
        info = clawd(f, x=1, view='front', eyes='normal', lookv=-1)
    elif seq < 3:
        info = clawd(f, x=1, view='qr', eyes='big', look=1)
        f.art(P.SWEAT, 18, 20 + k % 3)
    elif seq < 5:
        info = clawd(f, x=1, view='q2r', ra='out', eyes='angry')
    else:
        info = clawd(f, x=1, view='front', la='high', ra='high', eyes='closed')
    mini_pose = 'side'
    if 3 <= seq < 5:
        mini_pose = 'high'
    mini(f, 29, 28, view='ql' if seq >= 3 else 'front', la='high' if 3 <= seq < 5 and (k % 2) else mini_pose,
         ra='high' if seq >= 5 else 'side', eyes='closed' if seq >= 5 else 'normal')
    if 3 <= seq < 5:
        f.art(P.SWEAT, 37, 24 + k % 3)


# --------------------------------------------------------------------------- 40 the missing semicolon
SEMI = ['YY', 'YY', '..', '..', 'YY', 'YY', '.Y', 'Y.']


def semicolon(f, t, n):
    k = t % n
    window(f, 2, 1, 36, 16)
    big_text(f, 'X=1', 6, 6, 'W', k=2)
    fixed = k >= 13 and k < 22
    if not fixed:
        if t % 2:
            f.rect(30, 14, 4, 1, 'R')
        if k < 12:
            f.box(29, 5, 5, 10, 'R') if t % 4 < 2 else None
    if k < 9:
        x = -14 + k * 4
        s = k % 2
        info = clawd(f, x=x, y=BY + s, view='qr', legs=LG(s), la='up', ra='up', eyes='focus')
        f.art(SEMI, x + 7, BY - 9 + s)
    elif k < 13:
        j = k - 9
        info = clawd(f, x=22, y=BY + (1 if j == 0 else 0), la='up', ra='up', eyes='closed' if j == 0 else 'big', lookv=-1)
        sy = [11, 6, 4, 5][j] if j else 12
        f.art(SEMI, 30, sy if j else BY - 9)
    else:
        f.art([s.replace('Y', 'E') for s in SEMI], 30, 5)
        if fixed:
            f.rect(6, 15, 20, 1, 'E')
        if k < 18:
            info = clawd(f, x=22, eyes='happy', la='up' if t % 2 else 'high', ra='up' if t % 2 else 'high')
            P.check(f, 31, 16)
        else:
            s = k % 2
            clawd(f, x=22 + (k - 17) * 4, y=BY + s, view='qr', legs=LG(s), eyes='happy')


# --------------------------------------------------------------------------- 41 hello world
def hello_world(f, t, n):
    k = t % n
    letters = [(ch, 1 + i * 8, 2) for i, ch in enumerate('HELLO')] + [(ch, 1 + i * 8, 13) for i, ch in enumerate('WORLD')]
    shown = min(10, max(0, k - 1))
    for i, (ch, x, y) in enumerate(letters[:shown]):
        wave = int(round(1.5 * math.sin(2 * math.pi * (t / 8) - i * 0.7))) if k >= 12 else 0
        c = 'RFYEBP'[i % 6]
        if i == shown - 1 and k < 12:
            big_text(f, ch, x - 1, y - 1, 'G')
        big_text(f, ch, x, y + wave, c)
    done = k >= 12
    s = t % 2
    if not done:
        clawd(f, y=BY + 2, eyes='focus', lookv=-1, la='high' if s else 'mid', ra='mid' if s else 'high')
    else:
        b = (t // 2) % 2
        clawd(f, y=BY + 2 - b, eyes='happy', la='up' if b else 'high', ra='up' if b else 'high',
              legs=(1, 1, 1, 1) if b else (0, 0, 0, 0))
        P.sparkles(f, t, n, [(37, 24), (2, 26), (36, 33)])


# --------------------------------------------------------------------------- 42 kanban board
def kanban(f, t, n):
    k = t % n
    f.rect(0, 0, 40, 19, 'G'); f.rect(1, 1, 38, 17, 'W')
    for i, c in enumerate('gUE'):
        f.rect(2 + i * 13, 2, 11, 2, c)
        if i:
            f.rect(1 + i * 13, 4, 1, 13, 'G')
    cols_x = [4, 17, 30]
    colors = 'ZBP'
    # card c: TODO -> DOING over k=6c..6c+2, DOING -> DONE over 6c+3..6c+5
    pos = []
    for c in range(3):
        a = 6 * c
        if k >= 22:
            col, mv = 2, None
        elif k < a:
            col, mv = 0, None
        elif k < a + 3:
            col, mv = 0, (k - a) / 3
        elif k < a + 6:
            col, mv = 1, (k - a - 3) / 3
        else:
            col, mv = 2, None
        if mv is None:
            x, y = cols_x[col], 6 + c * 4
        else:
            x0, x1 = cols_x[col], cols_x[col + 1]
            x = x0 + (x1 - x0) * mv
            y = 6 + c * 4 - int(3 * math.sin(mv * math.pi))
        if k >= 22:
            q = (k - 21) / 2
            x = cols_x[2] + (cols_x[0] - cols_x[2]) * q
            y = 6 + c * 4 - int(4 * math.sin(q * math.pi))
        pos.append((int(x), int(y), mv is not None))
    for c, (x, y, moving) in enumerate(pos):
        f.rect(x, y, 7, 3, colors[c]); f.rect(x + 1, y + 1, 4, 1, 'W')
        if moving:
            f.box(x - 1, y - 1, 9, 5, 'k')
    mover = [p for p in pos if p[2]]
    done = 18 <= k < 22
    if mover:
        tx = mover[0][0] + 3
        cx = int(tx) - 8
        s = t % 2
        clawd(f, x=cx, view='front', ra='up', la='side', eyes='focus', y=BY + s)
    elif done:
        b = (t // 2) % 2
        clawd(f, x=12, eyes='happy', la='up' if b else 'high', ra='up' if b else 'high', y=BY - b)
        P.sparkles(f, t, n, [(36, 22), (3, 24), (34, 32)])
    else:
        clawd(f, x=12 if k < 22 else 6, eyes='normal', look=-1 if k >= 22 else 0)


# --------------------------------------------------------------------------- 43 ctrl+z un-topples the tower
def ctrl_z(f, t, n):
    k = t % n
    home = [(27, 32 - i * 4) for i in range(4)]
    fell = [(18, 32), (32, 32), (36, 28), (25, 32)]
    cols = 'BEPF'

    def block(x, y, c):
        f.rect(x, y, 8, 4, c); f.rect(x, y, 8, 1, 'W'); f.box(x, y, 8, 4, 'k')

    if k < 5:
        pos = home
    elif k < 10:
        q = ((k - 4) / 5) ** 2
        pos = [(int(hx + (fx - hx) * q), int(hy + (fy - hy) * q)) for (hx, hy), (fx, fy) in zip(home, fell)]
    elif k < 12:
        pos = fell
    elif k < 18:
        q = 1 - ((k - 11) / 6)
        pos = [(int(hx + (fx - hx) * q), int(hy + (fy - hy) * q)) for (hx, hy), (fx, fy) in zip(home, fell)]
    else:
        pos = home
    order = sorted(range(4), key=lambda i: -pos[i][1])
    for i in order:
        block(pos[i][0], pos[i][1], cols[i])
    if 10 <= k < 18:
        w = keycap(f, 2, 2, 'CTRL', down=k in (10, 11))
        f.text('+', 2 + w + 1, 4, 'g')
        keycap(f, 2 + w + 5, 2, 'Z', down=k in (10, 11))
        if k >= 12:
            f.art(['..B..B', '.BB.BB', 'BBBBBB', '.BB.BB', '..B..B'], 30, 3)
    if k < 4:
        s = k % 2
        clawd(f, x=-12 + k * 6, y=BY + s, view='q2r', legs=LG(s), eyes='normal')
    elif k < 10:
        clawd(f, x=10, view='q2r', ra='out' if k < 6 else 'up', eyes='big' if k < 8 else 'x')
        if k == 4:
            f.art(['K.K', '.K.', 'K.K'], 26, 22)
    elif k < 18:
        clawd(f, x=10, view='q2r', eyes='squint' if k < 12 else 'normal', ra='side', y=BY + (1 if k in (10, 11) else 0))
    else:
        s = k % 2
        clawd(f, x=10 - (k - 17) * 4, y=BY + s, view='q2r', legs=LG(s), eyes='happy')


# --------------------------------------------------------------------------- 44 hopping across giant keys
def key_hop(f, t, n):
    k = t % n
    word = 'CLAWD'
    if k < 20:
        i, j = k // 4, k % 4
        tx = 4 + 8 * i
        if j == 0 or i == 0:
            fx = tx
        else:
            fx = tx
        cx = tx - 8 + (j / 4) * 8 if 0 < i and False else tx
        prev = 4 + 8 * max(0, i - 1)
        q = j / 4
        cx = prev + (tx - prev) * min(1, q * 2) if i > 0 else tx
        dy = [0, -5, -3, 0][j] if i > 0 else [0, -2, -1, 0][j]
        pressed = i if j in (2, 3) or (i == 0) else i - 1
        typed = i + (1 if j >= 2 else 0) if i > 0 else (1 if j >= 2 else 0)
    else:
        j = k - 20
        cx = 36 + (4 - 36) * (j / 3)
        dy = [-4, -8, -6, -2][j]
        pressed, typed = -1, 0
    for ki, ch in enumerate(word):
        x = ki * 8
        down = 1 if ki == pressed and dy == 0 else 0
        f.rect(x, 31, 8, 5, 'g')
        f.rect(x, 29 + down, 8, 5, 'G')
        f.rect(x + 1, 29 + down, 6, 4, 'U' if down else 'w')
        f.text(ch, x + 3, 29 + down - 0, 'k')
    shown = word[:max(0, min(5, typed))]
    f.rect(2, 2, 36, 9, 'g'); f.rect(3, 3, 34, 7, 'k')
    f.text('>' + shown, 5, 4, 'E')
    if t % 2:
        f.rect(5 + text_w('>' + shown) + 1, 4, 3, 5, 'E')
    s = 1 if dy < 0 else 0
    clawd(f, x=int(cx) - 8, y=29 - 15 + dy, view='front' if k >= 20 else 'qr', legs=(1, 1, 1, 1) if dy < -2 else (0, 0, 0, 0),
          la='up' if dy < -2 else 'side', ra='up' if dy < -2 else 'side', eyes='happy' if dy < 0 else 'normal')


# --------------------------------------------------------------------------- 45 chasing the mouse cursor
CURSOR = ['K.....', 'KK....', 'KWK...', 'KWWK..', 'KWWWK.', 'KWWWWK', 'KWWKKK', 'KKWK..', 'K.KWK.', '...KK.']


def cursor_chase(f, t, n):
    a = 2 * math.pi * t / n
    cx = 20 + 14 * math.sin(a)
    cy = 9 + 4 * math.sin(2 * a)
    lag = 2 * math.pi * (t - 3) / n
    bx = 20 + 11 * math.sin(lag)
    moving_r = math.cos(lag) > 0
    near = abs(cx - bx) < 5 and cy > 9
    s = t % 2
    k = t % n
    jump = k in (7, 8, 9, 23, 24, 25)
    dy = {7: -4, 8: -7, 9: -3, 23: -4, 24: -7, 25: -3}.get(k, 0)
    info = clawd(f, x=int(bx) - 8, y=BY + dy + (0 if jump else s), view='qr' if moving_r else 'ql',
                 legs=(1, 1, 1, 1) if jump else LG(s), la='up' if jump else 'side', ra='up' if jump else 'side',
                 eyes='big' if jump else 'focus')
    if jump:
        cy -= 4
        cx += 3 if moving_r else -3
    f.art(CURSOR, int(cx), int(cy))
    if k in (8, 24):
        f.ring(int(cx) + 1, int(cy) + 1, 4, 'B')


# --------------------------------------------------------------------------- 46 chat with the assistant
def ai_chat(f, t, n):
    f.rect(19, 0, 21, 37, 'g'); f.rect(20, 1, 19, 35, 'W')
    arr = t // 6
    off = 8 * arr + min(8, (t % 6) * 4)
    newest = arr
    for j in range(newest - 5, newest + 1):
        y = 34 - 7 - 8 * (newest - j) - min(8, (t % 6) * 4) + 8
        if j == newest:
            y = 34 - 7 + 8 - min(8, (t % 6) * 4)
        if y > 30 or y < -8:
            continue
        mine = j % 2 == 0
        L = [9, 12, 7, 14][j % 4]
        if mine:
            x = 37 - L - 2
            f.rect(x, y, L + 2, 6, 'G'); f.rect(x + 1, y + 2, L - 2, 1, 'w')
        else:
            x = 21
            f.rect(x, y, L + 4, 6, 'O')
            if j == newest and t % 6 < 3:
                for d in range(3):
                    f.put(x + 2 + d * 2, y + 3, 'W' if d <= t % 3 else 'o')
            else:
                f.rect(x + 2, y + 2, L, 1, 'W'); f.rect(x + 2, y + 4, L - 4, 1, 'W')
    f.rect(20, 31, 19, 5, 'w'); f.rect(20, 31, 19, 1, 'G')
    if (t // 2) % 2:
        f.rect(22, 33, 1, 2, 'k')
    s = t % 2
    clawd(f, x=-1, view='q2r', ra='mid' if s else 'low', eyes='blink' if t % 13 == 4 else 'normal')


# --------------------------------------------------------------------------- 47 PR merged by head-bonk
def pr_merged(f, t, n):
    k = t % n
    merged = 12 <= k < 23
    f.rect(2, 1, 36, 20, 'g'); f.rect(3, 2, 34, 18, 'W')
    f.rect(3, 2, 34, 6, 'P' if merged else 'E')
    f.text('MERGED' if merged else 'PR #42', 5, 3, 'W')
    for i in range(3):
        x = 5 + i * 6
        if k >= 2 + i * 3:
            f.art(['...E', '..E.', 'E.E.', '.E..'], x, 9)
        else:
            f.rect(x + 1, 10, 2, 2, 'U' if t % 2 else 'Y')
    f.rect(24, 10, 10, 1, 'G')
    bonk = k == 11
    by = 14 - (1 if bonk else 0)
    if not merged:
        f.rect(9, by, 22, 6, 'e' if bonk else 'E')
        f.text('MERGE', 11, by + 1, 'W')
    else:
        f.art(['P...P', 'P..P.', 'PPP..', 'P..P.', 'P...P'], 18, 13)
    if k < 9:
        clawd(f, eyes='normal' if k % 5 else 'blink', lookv=-1)
    elif k < 14:
        j = k - 9
        dy = [0, -3, -2, 0, 0][j]
        sq = j == 0
        clawd(f, x=BX - (1 if sq else 0), w=18 if sq else 16, h=10 if sq else 12, y=BY + (2 if sq else dy),
              la='up' if 0 < j < 3 else 'side', ra='up' if 0 < j < 3 else 'side',
              eyes='closed' if j in (1, 2) else 'happy', legs=(1, 1, 1, 1) if 0 < j < 3 else (0, 0, 0, 0))
        if j == 2:
            f.art(['U...U', '.U.U.'], 17, BY + dy - 4)
    else:
        b = (t // 2) % 2
        if merged:
            P.confetti(f, t, n, count=10)
        clawd(f, eyes='happy', la='up' if b else 'high', ra='up' if b else 'high', y=BY - b)


# --------------------------------------------------------------------------- 48 plug in the server
def cable_plug(f, t, n):
    k = t % n
    lit = 0 if k < 11 or k >= 21 else min(5, k - 10)
    server_rack(f, 27, 8, 12, 28, t, lit=lit)
    f.rect(26, 24, 1, 3, 'g')
    if k < 10:
        x = 1 + k
        s = k % 2
        info = clawd(f, x=x, y=BY + s, view='q2r', legs=LG(s), ra='mid', eyes='angry')
    elif k < 21:
        info = clawd(f, x=7, view='q2r', ra='mid', eyes='happy' if k >= 13 else 'focus')
    else:
        j = k - 21
        L = Canvas()
        info = clawd(L, x=6 - j * 2, view='q2r', ra='up', eyes='x')
        f.blit(L.rot90(-(j + 1) % 4 if j < 2 else 0, 14 - j * 2, BY + 6) if j < 2 else L)
    hx, hy = info['rh']
    plug_x = int(hx) if k < 21 else 26 - 3
    if 10 <= k < 21:
        plug_x = 23
    f.rect(plug_x, int(hy) - 1, 3, 3, 'G'); f.rect(plug_x + 3, int(hy), 1, 1, 'g')
    f.line(0, 35, int(hx) - 4, 35, 'g')
    f.line(int(hx) - 4, 35, plug_x, int(hy), 'g')
    if k == 10:
        f.art(P.SPARK, 24, 20)
    if k == 21:
        f.art(P.SPARK_BIG, 22, 18)


# --------------------------------------------------------------------------- 49 dark mode toggle
def dark_mode(f, t, n):
    k = t % n
    dark = 6 <= k < 18
    if dark:
        f.rect(0, 0, 40, 40, 'k')
        P.sparkles(f, t, n, [(4, 5), (15, 3), (9, 13), (26, 6)])
    f.rect(29, 13, 9, 13, 'G' if not dark else 'g')
    f.rect(30, 14, 7, 11, 'w' if not dark else 'b')
    f.rect(32, 16, 3, 7, 'g')
    f.rect(32, 16 if dark else 19, 3, 4, 'W' if not dark else 'U')
    flip = k in (5, 6, 17, 18)
    if dark:
        clawd(f, x=4, view='q2r', ra='out' if flip else 'side', eyes='happy' if not flip else 'normal')
        f.text('DARK', 3, 2, 'w')
    else:
        clawd(f, x=4, view='q2r', ra='out' if flip else 'side', eyes='squint' if not flip else 'normal')
        f.text('LIGHT', 3, 2, 'Y')
        for (sx, sy) in ((2, 10), (36, 30), (20, 9)):
            if (t + sx) % 3 == 0:
                f.art(['.Y.', 'Y.Y', '.Y.'], sx, sy)


# --------------------------------------------------------------------------- 50 ping / pong packets
def packet_ping(f, t, n):
    k = t % n
    f.rect(0, 28, 10, 7, 'g'); f.rect(1, 29, 8, 5, 'k'); f.rect(0, 35, 12, 1, 'G')
    f.rect(2, 30, 4, 1, 'E')
    server_rack(f, 31, 16, 9, 20, t)
    half = n // 2
    out = k < half
    p = (k % half) / half
    if out:
        x = 6 + p * 26
    else:
        x = 32 - p * 26
    y = 20 - 14 * math.sin(p * math.pi)
    f.rect(int(x), int(y), 5, 4, 'C'); f.rect(int(x), int(y), 5, 1, 'W'); f.box(int(x), int(y), 5, 4, 'V')
    for d in (1, 2):
        tx = x - d * 3 if out else x + 5 + d * 3 - 3
        f.put(tx, y + 2, 'C')
    if 0 <= k % half < 3 and k >= 3:
        pass
    if k < 3:
        f.text('PONG', 1, 21, 'B')
    if half <= k < half + 3:
        f.text('PING', 22, 9, 'E')
    f.text('%dMS' % (12 + (k // 6) % 3), 15, 1, 'g')
    look = 1 if out == (p < 0.5) else -1
    view = 'qr' if (x > 20) else 'ql'
    clawd(f, x=12, y=BY + 1, view=view, eyes='normal', lookv=-1 if 0.2 < p < 0.8 else 0)


# --------------------------------------------------------------------------- 51 stepping through the debugger
def step_debug(f, t, n):
    k = t % n
    step = k // 4
    window(f, 0, 1, 24, 30)
    for i in range(6):
        y = 6 + i * 4
        if i == step:
            f.rect(1, y - 1, 22, 3, 'b')
        f.rect(6 + (i % 2) * 2, y, [10, 7, 12, 8, 9, 6][i], 1, pick('CGPGEG', i))
    f.disc(3, 6 + 2 * 4 + 0.5, 1.5, 'R')
    ay = 6 + step * 4 - 1
    f.art(['U..', 'UU.', 'UUU', 'UU.', 'U..'][1:4], 1 if step != 2 else 4, ay)
    f.rect(26, 2, 13, 9, 'w'); f.box(26, 2, 13, 9, 'g')
    f.text('X=%d' % (step + 1), 28, 4, 'B')
    press = k % 4 == 3
    keycap(f, 11, 31, 'F10', down=press)
    clawd(f, x=23, view='q2l', la='low' if press else 'mid', eyes='focus' if step != 2 else 'big', y=BY + (1 if press else 0))
    if step == 2:
        f.art(P.EXCL, 33, 14, cmap={'K': 'R'})


# --------------------------------------------------------------------------- 52 sudo unlock
def padlock(f, x, y, open_=0, shake=0):
    x += shake
    f.rect(x + 2, y - open_, 2, 8, 'g'); f.rect(x + 10, y - open_, 2, 8, 'g')
    f.rect(x + 2, y - open_, 10, 2, 'g'); f.put(x + 3, y + 1 - open_, 'G'); f.put(x + 11, y + 1 - open_, 'G')
    f.rect(x, y + 7, 14, 11, 'Y'); f.rect(x + 1, y + 8, 12, 9, 'U')
    f.rect(x + 6, y + 10, 2, 3, 'k'); f.rect(x + 5, y + 10, 4, 2, 'k')


def sudo(f, t, n):
    k = t % n
    open_ = 0 if k < 11 or k >= 22 else min(4, (k - 10) * 2)
    shake = (1 if k % 2 else -1) if 8 <= k < 11 else 0
    padlock(f, 23, 14, open_, shake)
    if k < 8:
        info = clawd(f, x=1, view='q2r', ra='mid' if k % 2 else 'low', eyes='focus')
        P.say(f, info, '$' + 'SUDO'[:max(1, min(4, k))] if k < 7 else '$SUDO')
    elif k < 11:
        info = clawd(f, x=1, view='q2r', eyes='worried')
        f.art(P.SWEAT, 18, 18 + k % 3)
    else:
        b = (t // 2) % 2
        info = clawd(f, x=1, view='q2r', eyes='happy', ra='up' if b else 'high', y=BY - b)
        if k < 22:
            P.sparkles(f, t, n, [(36, 8), (22, 10), (38, 22)])


# --------------------------------------------------------------------------- 53 bandage on a cracked screen
BANDAGE = ['.rrrrrrr.', 'rrTrTrTrr', '.rrrrrrr.']


def patch_crack(f, t, n):
    k = t % n
    broken = k < 9 or k >= 21
    monitor(f, 18, 4, 21, 17)
    if broken:
        r = rng(t)
        for i in range(4):
            yy = 6 + r.randint(0, 12)
            f.rect(19 + r.randint(0, 6), yy, r.randint(4, 12), 1, pick('RCPE', i))
    else:
        f.art(['K.....K', '.......', 'K.....K', '.KKKKK.'], 25, 9, cmap={'K': 'E'})
    f.line(24, 5, 28, 10, 'w'); f.line(28, 10, 26, 14, 'w'); f.line(28, 10, 33, 12, 'w')
    on = 8 <= k < 21
    if on:
        f.art(BANDAGE, 24, 9)
    if k >= 21:
        j = k - 21
        f.art(BANDAGE, 24, 12 + j * 7)
    if k < 6:
        s = k % 2
        info = clawd(f, x=-6 + k * 2, y=BY + s, view='q2r', legs=LG(s), ra='high', eyes='focus')
        f.art(BANDAGE, int(info['rh'][0]) - 1, int(info['rh'][1]) - 3)
    elif k < 9:
        info = clawd(f, x=4, view='q2r', ra='up', eyes='focus', y=BY - 1)
        if k < 8:
            f.art(BANDAGE, int(info['rh'][0]) - 2, int(info['rh'][1]) - 3)
    elif k < 21:
        info = clawd(f, x=4, view='q2r', eyes='happy' if k < 18 else 'normal', ra='side')
        if k < 13:
            P.check(f, 10, 8)
    else:
        info = clawd(f, x=4, view='q2r', eyes='big', ra='side')
        f.art(P.EXCL, 12, 10, cmap={'K': 'R'})


# --------------------------------------------------------------------------- 54 node_modules is heavy
def node_modules(f, t, n):
    k = t % n
    if k < 20:
        g = k / 19
        bw = int(8 + 22 * g)
        bh = int(5 + 9 * g)
        strain = min(2, int(g * 3))
        info = clawd(f, x=BX, y=BY + strain, h=12 - strain, la='up', ra='up',
                     eyes=['normal', 'focus', 'squint'][strain], top=strain > 1)
        bx = 20 - bw // 2
        by = info['y'] - 3 - bh
        f.rect(bx, by, bw, bh, 'N'); f.box(bx, by, bw, bh, 'n')
        if bw > 12:
            f.text('NPM', bx + bw // 2 - 5, by + bh // 2 - 2, 'W')
        for i in range(3):
            p = ((t / 6) + i / 3) % 1
            dx = [-8, 3, 10][i]
            f.rect(20 + dx, int(-3 + p * (by + 2)), 2, 2, pick('RBE', i))
        if strain >= 1:
            f.art(P.SWEAT, info['x'] + 18, info['y'] + t % 3)
            f.art(P.SWEAT, info['x'] - 4, info['y'] + 1 + (t + 1) % 3, flip=True)
    else:
        j = k - 20
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='x' if j < 3 else 'squint', la='low', ra='low')
        f.rect(6, 10, 28, 14, 'N'); f.box(6, 10, 28, 14, 'n')
        f.text('NPM', 15, 15, 'W')
        if j < 2:
            f.art(P.PUFF, 0, 31); f.art(P.PUFF, 36, 31)
        else:
            P.orbit(f, 20, 7, 9, 2, t, 4, ['.U.', 'UUU', '.U.'], count=3)


# --------------------------------------------------------------------------- 55 ctrl+s spam
def floppy(f, x, y, big=0):
    w = 14 + big * 2
    x -= big; y -= big
    f.rect(x, y, w, w, 'B'); f.rect(x + 1, y + 1, w - 2, w - 2, 'V')
    f.rect(x + 3, y + 1, w - 6, 4, 'G'); f.rect(x + w - 6, y + 2, 2, 2, 'V')
    f.rect(x + 2, y + w - 7, w - 4, 6, 'W'); f.box(x + 2, y + w - 7, w - 4, 6, 'G')
    f.rect(x + 4, y + w - 5, w - 8, 1, 'G')


def ctrl_s(f, t, n):
    k = t % n
    frantic = k < 12
    press = frantic and k % 2 == 1
    floppy(f, 24, 5, big=1 if press else 0)
    if press or (12 <= k < 15):
        f.rect(19, 22, 21, 7, 'E'); f.text('SAVED', 20, 23, 'W')
    w = keycap(f, 4, 31, 'CTRL', down=press)
    keycap(f, 4 + w + 2, 31, 'S', down=press)
    if frantic:
        clawd(f, x=1, y=BY - 3 + (1 if press else 0), view='q2r', ra='low' if press else 'mid', la='side',
              eyes='worried' if k < 8 else 'focus')
        f.art(P.SWEAT, 18, 16 + k % 3)
    else:
        clawd(f, x=1, y=BY - 3, view='q2r', eyes='closed' if k < 14 else 'happy')
        f.art(['.LL', 'LLL'], 20, 23 - (k - 12))


# --------------------------------------------------------------------------- 56 contribution graph fills up
def contrib(f, t, n):
    k = t % n
    r = rng(8)
    cells = [(cx, cy) for cx in range(9) for cy in range(5)]
    r.shuffle(cells)
    lvl = {c: r.choice('EEe') for c in cells}
    shown = len(cells) if k >= 20 else int(len(cells) * k / 20)
    on = set(cells[:shown])
    for (cx, cy) in [(a, b) for a in range(9) for b in range(5)]:
        x, y = 2 + cx * 4, 3 + cy * 4
        c = lvl[(cx, cy)] if (cx, cy) in on else 'G'
        if k >= 20 and (cx + cy + t) % 4 == 0:
            c = 'U'
        f.rect(x, y, 3, 3, c)
    for (cx, cy) in cells[max(0, shown - 2):shown]:
        if k < 20:
            f.box(2 + cx * 4 - 1, 3 + cy * 4 - 1, 5, 5, 'U')
    b = t % 2
    if k < 20:
        clawd(f, y=BY + 1 - b * 2, legs=(1, 1, 1, 1) if b else (0, 0, 0, 0), eyes='focus' if not b else 'happy',
              la='mid' if b else 'side', ra='side' if b else 'mid')
    else:
        clawd(f, y=BY + 1, eyes='happy', la='up', ra='up' if t % 2 else 'high')


# --------------------------------------------------------------------------- 57 reboot
def reboot(f, t, n):
    k = t % n
    monitor(f, 7, 1, 26, 19)
    sx, sy, sw, sh = 8, 2, 24, 17
    if k < 4:
        r = rng(3)
        for i in range(5):
            f.rect(sx + r.randint(0, 6), sy + 2 + i * 3, r.randint(5, 14), 1, 'g')
        f.rect(16, 7, 8, 5, 'g'); f.rect(17, 8, 6, 3, 'W'); f.rect(19, 9, 2, 1, 'R')
    elif k == 5:
        f.rect(sx, sy + 8, sw, 1, 'W')
    elif k == 6:
        f.rect(19, 10, 2, 1, 'W')
    elif 9 <= k < 14:
        spark(f, 20, 9, min(3, k - 9), c='F')
        P.progress(f, 12, 14, 16, (k - 9) / 4, c='F', bg='g')
    elif k >= 14:
        f.rect(sx, sy, sw, sh, 'S')
        f.rect(sx, sy + sh - 3, sw, 3, 'b')
        for i, c in enumerate('UEZ'):
            f.rect(sx + 2 + i * 5, sy + 2, 3, 3, c)
        f.rect(sx + 14, sy + 5, 8, 6, 'W'); f.rect(sx + 14, sy + 5, 8, 1, 'g')
        spark(f, sx + 2, sy + sh - 2, 1, c='F')
    led = 'E' if (k < 4 or k >= 9) else 'g'
    f.rect(31, 18, 1, 1, led)
    if k < 4:
        clawd(f, view='front', eyes='worried', la='high' if k % 2 else 'side', y=BY + 1)
    elif k < 6:
        clawd(f, x=14, view='qr', ra='up', eyes='focus', y=BY + 1)
        f.art(P.SPARK, 30, 15) if k == 4 else None
    elif k < 14:
        clawd(f, view='front', eyes='normal' if k % 3 else 'blink', y=BY + 1, la='front', ra='front')
    else:
        b = (t // 2) % 2
        clawd(f, view='front', eyes='happy', y=BY + 1 - b, la='up' if b else 'side', ra='up' if b else 'side')


# --------------------------------------------------------------------------- 58 blue screen
def bsod(f, t, n):
    k = t % n
    monitor(f, 6, 1, 28, 18)
    blue = k >= 4
    if not blue:
        for i in range(5):
            f.rect(9, 4 + i * 3, [12, 8, 16, 10, 6][i], 1, pick('CEPF', i))
        if t % 2:
            f.rect(9 + 6 + 1, 16, 2, 1, 'W')
    else:
        f.rect(7, 2, 26, 16, 'B')
        big_text(f, ':(', 9, 4, 'W')
        f.rect(9, 15, 20, 1, 'S'); f.rect(9, 13, 14, 1, 'S')
    if k < 4:
        clawd(f, y=BY + 1, eyes='focus', la='front', ra='front')
    elif k < 9:
        clawd(f, y=BY + 1, eyes='big', la='high', ra='high')
        if k < 7:
            f.art(P.EXCL, 33, 22 - (k % 2), cmap={'K': 'R'}); f.art(P.EXCL, 35, 22 - (k % 2), cmap={'K': 'R'})
        f.art(P.SWEAT, 4, 22 + k % 3)
    else:
        clawd(f, x=BX - 2, w=20, h=9, y=BY + 3, eyes='x', la='low', ra='low')
        P.orbit(f, 20, BY - 1, 9, 2, t, 4, ['.U.', 'UUU', '.U.'], count=3)


# --------------------------------------------------------------------------- 59 drag & drop into a folder


def folder(f, x, y, front=True, squash=0):
    w = 21
    if not front:
        f.rect(x, y - 2, 7, 2, 'Y')
        f.rect(x, y, w, 40 - y, 'Y')
    else:
        f.rect(x - squash, y + 3 + squash, w + 2 * squash, 40 - y - 3, 'U')
        f.rect(x - squash, y + 3 + squash, w + 2 * squash, 1, 'Y')
        f.rect(x - squash, y + 3 + squash, 1, 40 - y - 3, 'Y'); f.rect(x + w - 1 + squash, y + 3 + squash, 1, 40 - y - 3, 'Y')


def drag_drop(f, t, n):
    k = t % n
    fx, fy = 19, 25
    folder(f, fx, fy, front=False)
    cy = BY
    if k < 6:
        hx, hy = -6 + k * 4, 2 + k * 2
        clawd(f, x=2, eyes='normal', lookv=-1, look=-1 if k < 3 else 0)
        f.art(CURSOR, hx, hy)
        if k == 5:
            f.ring(hx + 1, hy + 1, 3.5, 'B')
        folder(f, fx, fy)
    elif k < 18:
        lift = min(9, (k - 6) * 3)
        x = min(23, 2 + max(0, k - 9) * 3)
        clawd(f, x=x, y=cy - lift, legs=pick([(1, 0, 0, 1), (0, 1, 1, 0)], t), la='high', ra='high',
              eyes='big' if k < 9 else 'happy')
        folder(f, fx, fy)
        bx0, by0 = x - 5, cy - lift - 2
        for i in range(0, 26, 2):
            f.put(bx0 + i, by0, 'B'); f.put(bx0 + i, by0 + 19, 'B')
        for i in range(0, 20, 2):
            f.put(bx0, by0 + i, 'B'); f.put(bx0 + 25, by0 + i, 'B')
        f.art(CURSOR, x + 14, cy - lift + 10)
    elif k < 24:
        j = k - 18
        y = [13, 19, 25, 31, 31, 31][j]
        clawd(f, x=23, y=y, la='up', ra='up', eyes='closed')
        folder(f, fx, fy, squash=1 if j == 3 else 0)
        f.art(CURSOR, 33 + j * 2, 2 - j * 4)
        if j >= 3:
            f.disc(37, 27, 2.5, 'R'); f.text('1', 36, 25, 'W')
    else:
        j = k - 24
        if j < 3:
            clawd(f, x=23, y=[27, 23, 20][j], eyes='normal', look=-1)
            folder(f, fx, fy)
        else:
            q = (j - 3) / 4
            x = int(23 - 21 * q)
            y = cy - int(round(12 * math.sin(q * math.pi))) if j > 3 else 17
            clawd(f, x=x, y=y, view='ql', la='up', ra='up', legs=(1, 1, 1, 1) if j < 7 else (0, 0, 0, 0), eyes='happy')
            folder(f, fx, fy)

# --------------------------------------------------------------------------- 60 zip it up
def zip_compress(f, t, n):
    k = t % n
    # archive on the right: squashes as it is zipped shut
    if k < 12:
        ah = 18
    elif k < 18:
        ah = 18 - (k - 11)
    elif k < 22:
        ah = 12
    else:
        ah = 12 + (k - 21) * 3
    ax, aw = 23, 15
    ay = 36 - ah
    f.rect(ax, ay, aw, ah, 'N'); f.box(ax, ay, aw, ah, 'n')
    f.rect(ax, ay, aw, 3, 'n')
    zip_y = ay if k < 12 else ay + int((ah - 2) * min(1, (k - 11) / 5)) if k < 22 else ay
    for yy in range(ay + 1, ay + ah - 1):
        closed = 12 <= k < 22 and yy <= zip_y
        f.put(ax + 12, yy, 'G' if closed else 'k')
        if not closed:
            f.put(ax + 11 + (yy % 2) * 2, yy, 'G')
    f.rect(ax + 11, zip_y, 3, 3, 'U'); f.put(ax + 12, zip_y + 3, 'Y')
    f.text('ZIP', ax + 1, ay + ah - 7, 'T')
    if 18 <= k < 22:
        f.text('-80%', 22, 12, 'E')
    # files tossed in
    for i in range(3):
        a = i * 4
        if a <= k < a + 4:
            q = (k - a) / 4
            fx = int(10 + q * 16)
            fy = int(14 - 10 * math.sin(q * math.pi))
            f.art(FILE, fx, fy)
    tossing = k < 12 and k % 4 in (0, 1)
    pulling = 12 <= k < 18
    info = clawd(f, x=2, view='q2r', ra='up' if tossing else ('low' if pulling and k % 2 else 'mid' if pulling else 'side'),
                 eyes='happy' if 18 <= k < 22 else 'focus', y=BY + (1 if pulling and k % 2 else 0))
    if 18 <= k < 22:
        P.sparkles(f, t, n, [(21, 20), (38, 8), (30, 4)])


# --------------------------------------------------------------------------- register 1-12
add('dev_laptop_front', '笔记本打字', 'Laptop typing (front)', laptop_front, n=8, dur=100)
add('dev_terminal', '终端敲命令', 'Terminal command', terminal, n=20, dur=130)
add('dev_log_scroll', '盯着日志', 'Watching the logs', log_scroll, n=30, dur=100)
add_tweened('dev_bug_squash', '踩扁bug', 'Bug squash', bug_squash, n=16, dur=beats(16, 100, {6: 160, 8: 160, 10: 300, 11: 200}), tw_at={6: 1, 10: 1, 11: 1})
add('dev_bug_hunt', '放大镜找bug', 'Bug hunt', bug_hunt, n=24, dur=110)
add_tweened('dev_compile_bar', '等编译', 'Compiling...', compile_bar, n=24, dur=120, tw_at={15: 1, 23: 1})
add_tweened('dev_test_suite', '测试全绿', 'Tests go green', test_suite, n=24, dur=130, tw_at={14: 1, 23: 1})
add_tweened('dev_deploy_rocket', '发射上线', 'Deploy rocket', deploy_rocket, n=28, dur=110, tw_at={13: 1, 27: 1})
add_tweened('dev_git_merge', '分支合并', 'Git merge', git_merge, n=24, dur=beats(24, 110, {12: 250}), tw_at={15: 1, 21: 1})
add('dev_git_graph', '提交图', 'Commit graph', git_graph, n=24, dur=110)
add_tweened('dev_refactor', '整理缩进', 'Refactor indentation', refactor, n=24, dur=130, tw_at={19: 1, 21: 1})
add_tweened('dev_rubber_duck', '小黄鸭调试', 'Rubber duck debugging', rubber_duck, n=24, dur=150, tw_at={13: 1, 19: 1})

# --------------------------------------------------------------------------- register 13-24
add('dev_this_is_fine', '服务器着火没事', 'This is fine', this_is_fine, n=16, dur=130)
add('dev_coffee_to_code', '咖啡变代码', 'Coffee in, code out', coffee_to_code, n=16, dur=100)
add('dev_keyboard_smash', '暴躁砸键盘', 'Keyboard smash', keyboard_smash, n=12, dur=80)
add_tweened('dev_404', '找不到页面', '404 not found', not_found, n=24, dur=140, tw_at={7: 1, 11: 1})
add('dev_hourglass', '沙漏等待', 'Hourglass wait', hourglass_wait, n=24, dur=130)
add('dev_thinking', '思考中', 'Thinking...', thinking, n=24, dur=110)
add('dev_wrench_gear', '扳手拧齿轮', 'Tool use: wrench', wrench_gear, n=16, dur=100)
add('dev_docs_scroll', '翻长文档', 'Endless docs', docs_scroll, n=32, dur=110)
add('dev_lgtm', '盖章通过', 'LGTM stamp', lgtm, n=16, dur=120)
add('dev_pair_program', '结对编程', 'Pair programming', pair_program, n=16, dur=140)
add('dev_red_pen', '红笔审代码', 'Red-pen review', red_pen, n=24, dur=120)
add_tweened('dev_ship_it', '打包发货', 'Ship it!', ship_it, n=24, dur=110, tw_at={18: 1, 23: 1})

# --------------------------------------------------------------------------- register 25-40
add('dev_cloud_upload', '上传到云', 'Cloud upload', cloud_upload, n=20, dur=110)
add('dev_cpu_overheat', 'CPU过热', 'Overheating CPU', cpu_overheat, n=12, dur=90)
add('dev_infinite_loop', '死循环', 'Infinite loop', infinite_loop, n=24, dur=80)
add('dev_todo', '待办打勾', 'Todo list', todo, n=24, dur=130)
add('dev_pomodoro', '番茄钟', 'Pomodoro timer', pomodoro, n=24, dur=120)
add('dev_slide_chart', '汇报图表', 'Slide with a bar chart', slide_chart, n=24, dur=130)
add('dev_inbox_zero', '清空收件箱', 'Inbox zero', inbox_zero, n=24, dur=beats(24, 110, {20: 400, 21: 300, (22, 23): 200}))
add('dev_copy_paste', '复制粘贴', 'Ctrl+C, Ctrl+V', copy_paste, n=24, dur=120)
add_tweened('dev_task_topple', '任务堆倒塌', 'Task pile topples', task_topple, n=24, dur=beats(24, 110, {16: 200, 17: 250, 18: 250}), tw_at={17: 1, 20: 1, 23: 1})
add_tweened('dev_battery', '没电充电', 'Low battery, recharge', battery_charge, n=28, dur=110, tw_at={21: 1, 27: 1})
add('dev_wifi_search', '找信号', 'Hunting for wifi', wifi_search, n=24, dur=120)
add('dev_matrix', '黑客帝国', 'Matrix rain', matrix_rain, n=16, dur=90)
add('dev_robot_arm', '操控机械臂', 'Robot arm', robot_arm, n=24, dur=110)
add('dev_pixel_editor', '画像素图', 'Pixel art editor', pixel_editor, n=24, dur=120)
add_tweened('dev_git_blame', '甩锅', 'Git blame', git_blame, n=24, dur=140, tw_at={19: 1})
add_tweened('dev_semicolon', '补上分号', 'The missing semicolon', semicolon, n=24, dur=110, tw_at={17: 1})

# --------------------------------------------------------------------------- register 41-60
add('dev_hello_world', '你好世界', 'Hello, World!', hello_world, n=24, dur=120)
add('dev_kanban', '看板挪卡片', 'Kanban board', kanban, n=24, dur=130)
add_tweened('dev_ctrl_z', '撤销撤销', 'Ctrl+Z', ctrl_z, n=24, dur=beats(24, 110, {6: 160, 8: 250, 9: 200, 10: 350}), tw_at={5: 1, 9: 1})
add('dev_key_hop', '跳键盘', 'Hopping on giant keys', key_hop, n=24, dur=110)
add_tweened('dev_cursor_chase', '追鼠标', 'Chasing the cursor', cursor_chase, n=32, dur=90, tw_at={6: 1, 9: 1, 22: 1, 25: 1})
add('dev_ai_chat', '对话中', 'Chatting', ai_chat, n=24, dur=130)
add_tweened('dev_pr_merged', '顶开合并', 'PR merged', pr_merged, n=24, dur=120, tw_at={8: 1, 9: 1, 23: 1})
add_tweened('dev_cable_plug', '插网线', 'Plugging in the server', cable_plug, n=24, dur=beats(24, 110, {21: 300, 22: 300}), tw_at={20: 1, 23: 1})
add('dev_dark_mode', '深色模式', 'Dark mode toggle', dark_mode, n=24, dur=120)
add('dev_packet_ping', 'ping一下', 'Ping, pong', packet_ping, n=24, dur=100)
add('dev_step_debug', '单步调试', 'Step debugger', step_debug, n=24, dur=130)
add_tweened('dev_sudo', 'sudo解锁', 'Sudo unlock', sudo, n=24, dur=120, tw_at={10: 1, 23: 1})
add_tweened('dev_patch_crack', '贴创可贴', 'Patching a crack', patch_crack, n=24, dur=110, tw_at={8: 1})
add_tweened('dev_node_modules', '依赖太重', 'Heavy node_modules', node_modules, n=24, dur=110, tw_at={23: 1})
add('dev_ctrl_s', '疯狂保存', 'Ctrl+S spam', ctrl_s, n=16, dur=100)
add('dev_contrib_graph', '提交格子变绿', 'Contribution graph', contrib, n=24, dur=110)
add_tweened('dev_reboot', '重启大法', 'Reboot', reboot, n=24, dur=130, tw_at={3: 1, 5: 1, 13: 1})
add_tweened('dev_bsod', '蓝屏了', 'Blue screen', bsod, n=16, dur=140, tw_at={8: 1, 15: 1})
add_tweened('dev_drag_drop', '拖进文件夹', 'Drag and drop', drag_drop, n=32, dur=beats(32, 100, {5: 250, 18: 200, 22: 200}), tw_at={23: 1, 26: 1, 31: 1})
add('dev_zip', '压缩打包', 'Zip it up', zip_compress, n=24, dur=110)
