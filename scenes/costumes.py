"""Costumes, professions, fantasy and sci-fi characters (60 scenes, prefix cos_)."""
import math
from engine import (Canvas, G, GROUND, BX, BY, add, clawd, mini, sin, cos, ph, pick, tri, rng, parse, size)
from engine import beats, add_tweened
import props as P


# --------------------------------------------------------------------------- shared helpers
def legs_walk(t):
    return (1, 0, 1, 0) if t % 2 else (0, 1, 0, 1)


def smoke(f, cx, cy, r, c='L', edge='G'):
    """Puffy smoke cluster with a grey rim (reads on white and dark)."""
    parts = ((0, 0, r), (-r * .8, r * .35, r * .7), (r * .8, r * .35, r * .7), (0, -r * .55, r * .75))
    for dx, dy, rr in parts:
        f.disc(cx + dx, cy + dy, rr + 1, edge)
    for dx, dy, rr in parts:
        f.disc(cx + dx, cy + dy, rr, c)


def cloud(f, x, y, w=12):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        P.cloud(f, x + dx, y + dy, 'G', w)
    P.cloud(f, x, y, 'W', w)


def hat_art(f, info, art, dx=0, dy=0, sink=0, flip=False):
    a = parse(art)
    w, h = size(a)
    cx, top = info['head']
    f.art(a, int(round(cx - w / 2)) + dx, int(top) - h + sink + dy, flip=flip)


def tween(a, b, p):
    return a + (b - a) * p


def arrow_r(f, x, y):
    f.art(['Z......', 'ZNNNNNg', 'Z......'], x, y - 1)


# --------------------------------------------------------------------------- local art
KNIGHT = """
    .......RR.......
    ......RRR.......
    .....RR.........
    ....GGGGGGGG....
    ..GGWGGGGGGGGG..
    .GGWGGGGGGGGGGG.
    gggggggggggggggg
"""
SHIELD = """
    gggggggg
    gBBBBBBg
    gBBUUBBg
    gBUUUUBg
    gBBUUBBg
    gBBBBBBg
    .gBBBBg.
    ..gBBg..
    ...gg...
"""
HORSE = """
    ..nn....
    .nNNN...
    nNNKNN..
    nNNNNNNN
    nNN.NNNT
    .N...NN.
"""
SHURI = [['..G..', '.GgG.', 'GgkgG', '.GgG.', '..G..'],
         ['G...G', '.GgG.', '.gkg.', '.GgG.', 'G...G']]
CHEST = """
    .NNNNNNNN.
    NnnnnnnnnN
    YYYYUUYYYY
    NNNNKKNNNN
    NNNNNNNNNN
    YNNNNNNNNY
"""
CHEST_OPEN = """
    .NNNNNNNN.
    NnnnnnnnnN
    NnUUUUUUnN
    YUUYUUYUUY
    NNNNNNNNNN
    NNNNNNNNNN
    YNNNNNNNNY
"""
SWORD = (['.Wg.', '.Wg.', '.Wg.', '.Wg.', '.Wg.', 'YYYY', '.NN.'], 1, 6)


# --------------------------------------------------------------------------- wizard
def wizard_spell(f, t, n):
    """Spark spiral gathers on the wand tip, a star shoots up and bursts."""
    k = t % 16
    if k < 4:
        ra, eyes = 'high', 'focus'
    elif k < 7:
        ra, eyes = 'up', 'closed' if k < 6 else 'big'
    elif k < 12:
        ra, eyes = 'up', 'big'
    else:
        ra, eyes = 'high', 'happy'
    info = clawd(f, x=4, view='qr', ra=ra, eyes=eyes, tilt=1 if 6 <= k < 12 else 0)
    P.hat(f, info, 'wizard')
    hx, hy = info['rh']
    P.item(f, (hx, hy), 'wand')
    tx, ty = int(hx), int(hy) - 6        # wand tip
    if k < 4:
        r = 9 - k * 2
        for i in range(4):
            a = 2 * math.pi * (i / 4 + k / 6)
            f.art(['.p.', 'pPp', '.p.'] if i % 2 else P.SPARK, int(tx + r * math.cos(a)) - 1,
                  int(ty + r * math.sin(a)) - 1)
    elif k < 6:
        f.art(P.SPARK_BIG, tx - 3, ty - 3)
    elif k < 10:
        j = k - 6
        sx, sy = tx + 2 + j * 4, ty - 2 - j * 3
        for d in range(1, 4):
            f.put(sx - d * 2 + 2, sy + d * 2 + 1, 'PUp'[d - 1])
        f.art(P.STAR5, sx, sy - 2)
    else:
        p = 0.25 + (k - 10) / 6 * 0.75
        P.firework(f, 31, 5, p, c='P', c2='U', r=6)
        if k >= 12:
            P.sparkles(f, k, 4, [(26, 14), (36, 12), (31, 16)])


def wizard_staff(f, t, n):
    """Bearded wizard thumps his staff: a rune ring spreads and he levitates."""
    k = t % 16
    lift = [0, 0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4, 3, 2, 1, 0][k]
    raise_ = [0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0][k]
    squash = k == 4
    # rune ring on the floor
    if 4 <= k <= 13:
        r = 3 + (k - 4) * 2
        for i in range(16):
            a = 2 * math.pi * i / 16 + k * 0.2
            x, y = 20 + r * math.cos(a), 37 + r * 0.25 * math.sin(a)
            f.put(x, y, 'P' if i % 2 else 'p')
    y = BY - lift + (1 if squash else 0)
    info = clawd(f, y=y, h=11 if squash else 12, eyes='closed' if 4 <= k <= 6 else 'happy' if lift >= 3 else 'normal',
                 la='mid', legs=(1, 1, 1, 1) if lift >= 2 else (0, 0, 0, 0))
    P.hat(f, info, 'wizard')
    # staff
    sx = int(info['lh'][0]) - 1
    top = info['y'] - 9 - raise_
    bot = min(GROUND - 1, top + 22)
    f.rect(sx, top + 3, 1, bot - top - 2, 'N')
    glow = 4 <= k <= 13
    f.disc(sx + .5, top + 1.5, 2, 'C' if not glow or k % 2 else 'U')
    f.put(sx - 1, top, 'W')
    if glow:
        for (dx, dy) in ((-4, 0), (4, 1), (0, -4)):
            if (k + dx) % 3 == 0:
                f.put(sx + dx, top + dy, 'U')
    if 5 <= k <= 13:
        P.rising(f, ['.P.', 'PpP', '.P.'], t, n, 4, 30, count=2, height=14, jitter=2, seed=3)
        P.rising(f, ['.P.', 'PpP', '.P.'], t, n, 34, 32, count=2, height=14, jitter=2, seed=5)


# --------------------------------------------------------------------------- knight
def knight_shield(f, t, n):
    """Knight braces behind a shield; arrows clang off and drop."""
    k = t % 12
    hit = k in (4, 10)
    info = clawd(f, x=BX + 3 + (1 if hit else 0), eyes='squint' if hit else 'focus', ra='high')
    x, y, w = info['x'], info['y'], info['w']
    hat_art(f, info, KNIGHT, sink=1)
    P.item(f, info['rh'], '', art=SWORD)
    sx = x - 8 + (1 if hit else 0)
    f.art(SHIELD, sx, y + 2)
    for off in (0, 6):
        j = (k - off) % 12
        if j < 4:
            arrow_r(f, -6 + j * 4 + (sx - 10), y + 5 + off // 3)
        elif j == 4:
            f.art(['U.U', '.W.', 'U.U'], sx - 3, y + 4 + off // 3)
        elif j < 9:
            # tumbling down after the clang
            yy = y + 6 + off // 3 + (j - 4) * 2
            xx = sx - 6 - (j - 4)
            if j % 2:
                f.art(['g', 'N', 'N', 'N', 'Z'], xx, min(yy, GROUND - 5))
            else:
                f.art(['ZNNNg'], xx - 2, min(yy, GROUND - 1))
        else:
            f.art(['ZNNNg'], sx - 11, GROUND - 1)


def knight_horse(f, t, n):
    """Galloping across on a hobby horse, pennant flapping."""
    x = -20 + int(62 * t / n)
    s = t % 4
    dy = [0, -2, -3, -1][s]
    L = Canvas()
    y = BY + dy
    # stick
    L.line(x + 2, GROUND - 1, x + 21, y + 4, 'n')
    L.art(['Y.Y', '.Y.'], x, GROUND - 2)
    info = clawd(L, x=x, y=y, view='qr', ra='side', legs=(1, 0, 1, 0) if s % 2 else (0, 1, 0, 1),
                 legdx=(1, -1, 1, -1) if s % 2 else (0, 0, 0, 0), eyes='happy' if s == 2 else 'focus')
    hat_art(L, info, KNIGHT, sink=1)
    L.art(HORSE, x + 18, y - 1)
    L.rect(x + 7, y - 6 - (1 if s == 2 else 0), 1, 3, 'k')
    L.art(['ZZZ', 'ZZ.'] if s % 2 else ['ZZ.', 'ZZZ'], x + 4, y - 7 - (1 if s == 2 else 0))
    f.blit(L)
    if s == 0:
        P.dust(f, x - 2, GROUND, 0.5)


# --------------------------------------------------------------------------- pirate
def pirate_spyglass(f, t, n):
    """Pirate on a rocking deck extends a spyglass towards a little island."""
    k = t % 16
    # far sea + island
    f.rect(0, 26, 40, 5, 'B')
    for i in range(7):
        xx = (i * 7 + k) % 42 - 2
        f.rect(xx, 26 + i % 2 * 2, 3, 1, 'S')
    f.rect(32, 25, 6, 1, 'Y'); f.rect(34, 21, 1, 4, 'N'); f.art(['EE.EE', '.EEE.'], 32, 20)
    bob = [0, 0, 1, 1, 1, 0, 0, -1][k % 8]
    L = Canvas()
    L.rect(0, 30, 40, 1, 'n')
    for px in range(1, 40, 6):
        L.rect(px, 31, 1, 5, 'n')
    L.rect(0, 36, 40, 4, 'N'); L.rect(0, 37, 40, 1, 'n'); L.rect(0, 39, 40, 1, 'n')
    for px in (5, 18, 31):
        L.put(px, 38, 'n')
    ext = [0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 1][k]
    C = Canvas()
    # strong 3/4 view: the near eye sits on the front edge, so the eyepiece can touch it
    info = clawd(C, x=5, view='q2r', ra='mid', eyes='normal' if ext < 5 else 'big')
    P.hat(C, info, 'pirate')
    cx, cy = max(info['eyes'])
    ex = int(cx) + 2
    ey = int(cy) - 1
    C.rect(ex - 1, ey - 1, 3, 4, 'N')
    C.rect(ex + 2, ey, 3 + ext, 2, 'Y')
    C.rect(ex + 2, ey - 1, 2, 4, 'n')
    C.rect(ex + 5 + ext, ey - 1, 2, 4, 'Y')
    if ext >= 5:
        C.put(ex + 6 + ext, ey, 'W')
    C = C.shear([0, 0.03, 0.05, 0.03, 0, -0.03, -0.05, -0.03][k % 8], 36)
    L.blit(C)
    f.blit(L.shift(0, bob))
    if 7 <= k <= 10:
        P.say(f, info, 'LAND!', dy=bob - 1)
    # gull
    gx = 40 - (k * 3) % 48
    f.art(['k.k', '.k.'] if k % 2 else ['kk.kk', '..k..'], gx, 6 + (k % 3))


def pirate_treasure(f, t, n):
    """Digs at the X, a chest rises, opens in a shower of coins, then sinks again."""
    k = t % 20
    # sand mound
    f.rrect(22, 32, 16, 5, 'Y'); f.rect(24, 32, 4, 1, 'y'); f.rect(21, 35, 18, 1, 'N')
    hole = [1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 1, 0][k]
    if k < 8 or k >= 18:
        f.art(['R.R', '.R.', 'R.R'], 28, 33)
    if hole:
        f.rect(30 - hole, 33, hole * 2, 3, 'n')
    digging = k < 8
    up = digging and k % 2 == 1
    happy = 10 <= k <= 16
    info = clawd(f, x=4, view='qr', ra='up' if happy else 'mid' if up else 'low',
                 la='up' if happy else 'side', eyes='happy' if happy else 'focus' if digging else 'normal',
                 tilt=1 if happy else 0)
    P.hat(f, info, 'pirate')
    hx, hy = info['rh']
    if digging or k >= 18:
        # shovel: handle from hand to blade in the sand
        bx, by = (29, 31) if up else (29, 34)
        f.line(hx, hy, bx - 1, by - 1, 'N')
        f.rect(bx - 1, by - 1, 3, 3, 'g'); f.put(bx, by - 1, 'G')
        if up:
            r = rng(k)
            for i in range(3):
                f.rect(31 + i * 2 + r.randint(0, 2), 27 - i * 2 - r.randint(0, 2), 2, 1, 'Y')
    else:
        f.line(6, 36, 14, 35, 'N'); f.rect(3, 35, 3, 2, 'g')
    if 8 <= k <= 17:
        cy = {8: 33, 9: 30, 16: 30, 17: 33}.get(k, 29)
        art = CHEST_OPEN if 10 <= k <= 15 else CHEST
        f.art(art, 25, cy - (1 if 10 <= k <= 15 else 0))
        f.rect(21, 35, 18, 1, 'N')
        if 10 <= k <= 15:
            f.rect(26, cy - 4, 8, 3, 'n'); f.rect(25, cy - 2, 10, 1, 'N')
            for i in range(3):
                p = ((k - 10) / 6 + i / 3) % 1
                cx = 30 + int(math.sin(i * 2.1) * 3 + (i - 1) * p * 8)
                cy2 = int(cy - 5 - p * 16 + p * p * 8)
                f.art(['.UU.', 'UYYU', '.UU.'], cx - 2, cy2)
            P.sparkles(f, k, 4, [(24, 24), (36, 22), (30, 18)])


# --------------------------------------------------------------------------- ninja
def ninja_body(f, info, t, flutter=True):
    """Black hood and red headband, worn on top of the head (face left clear)."""
    x, y, w = info['x'], info['y'], info['w']
    f.rect(x + 1, y - 4, w - 2, 1, 'g'); f.rect(x, y - 3, w, 2, 'k')
    f.rect(x, y - 1, w, 2, 'R'); f.rect(x, y - 1, w, 1, 'Z')
    if flutter:
        wob = t % 2
        if info['view'] in ('qr', 'q2r', 'front'):
            f.rect(x - 4, y - 1 + wob, 4, 1, 'R'); f.rect(x - 5, y - wob, 4, 1, 'R')
        else:
            f.rect(x + w, y - 1 + wob, 4, 1, 'R'); f.rect(x + w + 1, y - wob, 4, 1, 'R')


def ninja_star(f, t, n):
    """Throws a spinning star, vanishes in a smoke puff, reappears."""
    k = t % 16
    if k <= 9 or k == 15:
        if k < 2:
            ra = 'high'
        elif k < 4:
            ra = 'out'
        else:
            ra = 'side'
        la = 'side'
        eyes = 'focus'
        y = BY + (1 if k == 15 else 0)
        if k >= 7:
            la, ra, eyes = 'front', 'front', 'closed'
        info = clawd(f, x=6, y=y, view='qr' if k < 7 else 'front', ra=ra, la=la, eyes=eyes)
        ninja_body(f, info, t)
    if 2 <= k <= 7:
        sx = 30 + (k - 2) * 7 - 8
        f.art(SHURI[k % 2], sx, 25 - (k - 2))
        if k > 2:
            f.rect(sx - 5, 27 - (k - 2), 4, 1, 'L')
    if k == 10:
        smoke(f, 14, 26, 6)
    elif k == 11:
        smoke(f, 9, 24, 3); smoke(f, 20, 27, 3)
    elif k == 12:
        f.art(P.PUFF, 6, 18); f.art(P.PUFF, 22, 20)
        f.art(['.e', 'eE'], 15, 31)
    elif k == 13:
        f.art(['.e', 'eE'], 16, 34)
    elif k == 14:
        smoke(f, 14, 27, 5)
        f.art(['.e', 'eE'], 17, 35)


def ninja_dash(f, t, n):
    """Zips between three spots leaving after-images."""
    spots = [(4, 'qr', 'side', 'out', 1), (22, 'ql', 'out', 'side', 1), (13, 'front', 'front', 'front', 0)]
    seg = (t // 4) % 3
    j = t % 4
    x0 = spots[seg - 1][0]
    x1, v, la, ra, crouch = spots[seg]
    if j == 0:
        a, b = sorted((x0, x1))
        for yy in (BY + 3, BY + 7, BY + 10):
            f.rect(a + 2, yy, b - a + 10, 1, 'G')
    y = BY + (crouch if j else 0)
    info = clawd(f, x=x1, y=y, h=12 - (1 if j == 1 else 0), view=v, la=la if j else 'low', ra=ra if j else 'low',
                 eyes='focus' if v == 'front' else 'normal' if j < 3 else 'blink')
    ninja_body(f, info, t)
    if j == 1:
        P.dust(f, x1 - 2, GROUND, 0.5); P.dust(f, x1 + 16, GROUND, 0.5, flip=True)


# --------------------------------------------------------------------------- superhero
def hero_cape(f, x0, y0, t, length=14, c='R', c2='M'):
    for i in range(length):
        w = 4 + i // 3
        wob = int(round(math.sin(i / 3.0 - t * 1.6) * 1.3))
        f.rect(x0 - i, y0 + wob, 1, w, c)
        f.put(x0 - i, y0 + wob + w - 1, c2)


def hero_fly(f, t, n):
    """Flying fist-first, cape rippling, clouds whipping past."""
    for i, (w, yy, sp) in enumerate(((12, 5, 5), (8, 30, 7), (10, 16, 4))):
        xx = 44 - (t * sp + i * 17) % 62
        cloud(f, xx, yy, w)
    dy = [0, -1, -1, 0, 1, 1][t % 6]
    L = Canvas()
    x, y = 13, BY - 5 + dy
    hero_cape(L, x + 1, y + 1, t)
    info = clawd(L, x=x, y=y, view='qr', ra='out', la='low', legs=(1, 1, 1, 1), eyes='focus')
    f.blit(L.shear(-0.08, y + 8))
    P.speedlines(f, x - 12, y + 3, t, n=3, length=5)


def hero_change(f, t, n):
    """Walks into a booth an office worker, bursts out with a cape and flies off."""
    k = t % 20

    def booth(f, dx=0, open_=False, window=None):
        f.rect(10 + dx, 10, 20, 2, 'V'); f.rect(13 + dx, 8, 14, 2, 'V'); f.rect(16 + dx, 9, 8, 1, 'U')
        f.rect(11 + dx, 12, 2, 24, 'V'); f.rect(27 + dx, 12, 2, 24, 'V'); f.rect(10 + dx, 35, 20, 1, 'V')
        if open_:
            f.rect(13 + dx, 12, 14, 23, 'k')
            f.rect(29 + dx, 12, 3, 23, 'B'); f.rect(30 + dx, 14, 1, 8, 'S')
        else:
            f.rect(13 + dx, 12, 14, 23, 'B')
            f.rect(15 + dx, 14, 10, 9, 'S'); f.rect(20 + dx, 14, 1, 9, 'B'); f.rect(15 + dx, 18, 10, 1, 'B')
            f.rect(15 + dx, 25, 10, 7, 'V'); f.rect(24 + dx, 27, 1, 2, 'U')
            if window:
                f.rect(15 + dx, 14, 10, 9, window)
    if k < 5:
        booth(f)
        info = clawd(f, x=-14 + k * 4, y=BY + k % 2, view='qr', legs=legs_walk(k))
        hx, hy = info['rh']
        f.rect(hx, hy, 6, 4, 'N'); f.rect(hx, hy + 1, 6, 1, 'n'); f.box(hx + 2, hy - 1, 2, 2, 'n')
    elif k == 5:
        booth(f, open_=True)
        info = clawd(f, x=12, view='back')
    elif k < 11:
        booth(f, dx=(1 if k % 2 else -1), window=pick(['U', 'S', 'Z', 'S', 'C'], k))
        for (x, y) in ((6, 14), (33, 18), (8, 28), (32, 8)):
            if (x + k) % 2:
                f.art(['U.U', '.U.', 'U.U'], x, y)
        if k == 10:
            f.art(P.EXCL, 34, 26, cmap={'K': 'R'})
    else:
        booth(f, open_=k < 14)
        if k < 15:
            y = [BY - 2, BY - 10, BY - 20, BY - 32][k - 11]
            L = Canvas()
            L.rect(11, y + 2, 18, 14 + (k - 11), 'R'); L.rect(11, y + 15 + (k - 11), 18, 1, 'M')
            info = clawd(L, y=y, la='up', ra='up', legs=(1, 1, 1, 1), eyes='happy')
            f.blit(L)
            if k == 11:
                f.art(P.SPARK_BIG, 2, 16); f.art(P.SPARK_BIG, 31, 22)
        elif k < 17:
            f.art(['.U.', 'UUU', '.U.'], 19, 2 + (k - 15) * 2)


# --------------------------------------------------------------------------- register 1-10
add('cos_wizard_spell', '巫师施法', 'Wizard star spell', wizard_spell, n=16, dur=110)
add('cos_wizard_staff', '法杖悬浮', 'Wizard staff levitation', wizard_staff, n=16, dur=120)
add('cos_knight_shield', '骑士举盾', 'Knight shield block', knight_shield, n=12, dur=110)
add('cos_knight_horse', '骑竹马冲锋', 'Hobby-horse knight', knight_horse, n=16, dur=90)
add('cos_pirate_spyglass', '海盗望远镜', 'Pirate spyglass', pirate_spyglass, n=16, dur=140)
add_tweened('cos_pirate_treasure', '海盗挖宝', 'Digging up treasure', pirate_treasure, n=20, dur=120, tw_at={9: 1, 16: 1})
add_tweened('cos_ninja_star', '忍者飞镖', 'Ninja star and vanish', ninja_star, n=16, dur=100, tw_at={15: 1})
add('cos_ninja_dash', '忍者瞬移', 'Ninja dash', ninja_dash, n=12, dur=90)
add('cos_hero_fly', '超人飞行', 'Superhero flight', hero_fly, n=12, dur=80)
add_tweened('cos_hero_change', '电话亭变身', 'Booth quick change', hero_change, n=20, dur=beats(20, 110, {11: 200, 12: 400, 13: 250, 14: 150}), tw_at={4: 1, 11: 1, 12: 1})


# --------------------------------------------------------------------------- royals
SCEPTER = (['.Z.', 'ZUZ', '.Z.', '.Y.', '.Y.', '.Y.', '.Y.', '.Y.'], 1, 5)


def ermine(f, x, y, w):
    f.rect(x, y, w, 2, 'W'); f.rect(x, y + 2, w, 1, 'G')
    for i in range(x + 1, x + w - 1, 3):
        f.put(i, y + (i // 3) % 2, 'k')


def royal_wave(f, t, n):
    """Crowned and robed, a slow parade wave on the red carpet while petals fall."""
    k = t % 12
    f.rect(0, 36, 40, 3, 'R'); f.rect(0, 39, 40, 1, 'U')
    for i in range(0, 40, 4):
        f.put(i + 1, 36, 'Z')
    L = Canvas()
    x, y = BX, BY
    L.rect(x - 2, y + 4, 20, 11, 'P'); ermine(L, x - 2, y + 13, 20)
    s = (k // 3) % 2
    info = clawd(L, x=x, y=y, eyes='happy' if k % 6 != 5 else 'closed', ra='wave' if s else 'high', la='side',
                 legs=(0, 0, 0, 0))
    P.hat(L, info, 'crown')
    P.item(L, info['lh'], '', art=SCEPTER, flip=True, dx=-1)
    P.falling(f, P.PETAL, t, n, count=7, seed=6, sway=3, bottom=34)
    f.blit(L.shear(0.03 * (1 if s else -1), 36))
    if k % 6 == 0:
        f.art(P.SPARK, int(info['head'][0]) + 5, BY - 9)


def royal_knighting(f, t, n):
    """The crowned Clawd taps a kneeling mini Clawd on each shoulder; it rises a knight."""
    k = t % 16
    f.rect(0, 36, 40, 2, 'R'); f.rect(0, 38, 40, 1, 'U')
    f.rect(18, BY + 4, 20, 11, 'P'); ermine(f, 18, BY + 13, 20)
    info = clawd(f, x=20, view='ql', la='high', eyes='closed' if k in (4, 5, 8, 9) else 'normal')
    P.hat(f, info, 'crown')
    hx, hy = info['lh']
    tips = {4: (5, 27), 5: (5, 28), 8: (11, 27), 9: (11, 28)}
    tip = tips.get(k, (14, 12) if k < 12 else (13, 11))
    f.line(hx - 1, hy - 1, tip[0], tip[1], 'G')
    f.line(hx - 1, hy - 2, tip[0], tip[1] - 1, 'W')
    f.rect(hx - 2, hy - 3, 1, 4, 'Y'); f.put(hx, hy - 1, 'N')
    if k in (5, 9):
        f.art(['U.U', '.W.', 'U.U'], tip[0] - 1, tip[1] - 4)
    # the mini squire
    if k < 12:
        mini(f, 3, 29, eyes='closed', legs=(2, 2, 2, 2), la='low', ra='low', view='qr')
    else:
        hop = [0, 3, 1, 0][k - 12]
        mini(f, 3, 28 - hop, eyes='happy', la='up', ra='up', view='qr', legs=(1, 1, 1, 1) if hop else (0, 0, 0, 0))
        f.rect(5, 26 - hop, 5, 2, 'G'); f.put(8, 24 - hop, 'R'); f.rect(8, 25 - hop, 2, 1, 'R')
        P.sparkles(f, k, 4, [(2, 20), (14, 22), (8, 16)])


# --------------------------------------------------------------------------- detective / spy
DEERSTALKER = """
    ....NNNNNN....
    ..NNnNNnNNnN..
    .NnNNnNNnNNnN.
    nnNNNNNNNNNNnn
"""
FEDORA = """
    ....nnnnnn....
    ...nnnNNnnn...
    ...kkkkkkkk...
    nnnnnnnnnnnnnn
"""


def detective_trail(f, t, n):
    """Deerstalker detective follows paw prints, magnifier near the floor."""
    x = -14 + int(56 * t / n)
    s = (t // 2) % 2
    L = Canvas()
    info = clawd(L, x=x, y=BY + s, view='qr', ra='low', legs=legs_walk(t // 2),
                 eyes='focus' if t < n * 0.7 else 'big')
    hat_art(L, info, DEERSTALKER, dx=-1)
    f.blit(L.shear(0.07, 36))
    hx, hy = info['rh']
    lx, ly = int(hx) + 5, int(hy) - 1
    for i, px in enumerate(range(2, 44, 5)):
        if px + 2 < lx + 1:
            f.art(['g.g', '.g.'], px, 37 + i % 2)
    f.line(hx, hy, lx - 2, ly - 1, 'N')
    f.disc(lx + .5, ly + .5, 3.2, 'S'); f.ring(lx + .5, ly + .5, 3.6, 'k')
    f.put(lx - 1, ly - 1, 'W'); f.put(lx, ly - 2, 'W')
    for i, px in enumerate(range(2, 44, 5)):
        if 0 <= px + 1 - lx <= 4:
            f.art(['k.k', 'k.k', '.k.'], lx - 1, ly - 1)
    if t >= n * 0.7:
        f.art(P.EXCL, int(info['head'][0]) + 8, BY - 9, cmap={'K': 'R'})
    elif n * 0.35 < t < n * 0.55:
        f.art(P.QMARK, int(info['head'][0]) + 8, BY - 9)


def spy_sneak(f, t, n):
    """Tiptoeing spy behind a newspaper with eye holes, lowers it for a peek."""
    k = t % 24
    if k < 8:
        x = -16 + int(k * 3.5)
    elif k < 16:
        x = 12
    else:
        x = 12 + int((k - 15) * 3.5)
    walking = k < 8 or k >= 16
    s = k % 2 if walking else 0
    lowered = 10 <= k <= 13
    look = [0, 0, -1, -1, 1, 1, 0, 0][k - 8] if 8 <= k < 16 else 0
    info = clawd(f, x=x, y=BY - s, view='front', legs=(0, 1, 0, 1) if s else (1, 0, 1, 0) if walking else (0, 0, 0, 0),
                 look=look, la='high', ra='high', eyes='normal')
    hat_art(f, info, FEDORA)
    y = info['y']
    py = y + 8 if lowered else y + 4
    f.rect(x - 1, py, 18, 11, 'W'); f.box(x - 1, py, 18, 11, 'G')
    f.rect(x + 8, py, 1, 11, 'G')
    if not lowered:
        f.text('NEWS', x + 1, py + 6, 'k')
    else:
        f.rect(x + 1, py + 2, 6, 2, 'k')
    for r in range(py + 2, py + 10, 2):
        f.rect(x + 10, r, 5, 1, 'g')
    if lowered:
        P.dots_bubble(f, info, k - 10)


# --------------------------------------------------------------------------- cowboy
def cowboy_lasso(f, t, n):
    """Spins a lasso overhead, throws it over a fence post and tugs."""
    k = t % 20
    f.rect(32, 23, 3, 13, 'N'); f.rect(32, 23, 3, 1, 'n'); f.rect(30, 28, 10, 1, 'n'); f.rect(30, 32, 10, 1, 'n')
    tug = 14 <= k <= 17
    L = Canvas()
    info = clawd(L, x=4, view='qr', ra='up' if k < 10 else 'out' if k < 18 else 'high',
                 eyes='angry' if tug else 'focus' if 10 <= k < 14 else 'happy', tilt=1 if k < 10 else 0)
    P.hat(L, info, 'cowboy')
    hx, hy = info['rh']
    if k < 10 or k >= 18:
        cx, cy, rx, ry = hx, info['y'] - 8, 7, 2.2
        if k >= 18:
            q = (k - 17) / 3
            cx, cy = tween(33, hx, q), tween(26, info['y'] - 8, q)
        a0 = k * 1.4
        pts = [(cx + rx * math.cos(a0 + i * math.pi / 8), cy + ry * math.sin(a0 + i * math.pi / 8)) for i in range(16)]
        for i, (px, py) in enumerate(pts):
            L.put(px, py, 'T' if i == 0 else 'N')
        L.line(hx, hy, pts[4][0], pts[4][1], 'N')
    elif k < 14:
        q = (k - 9) / 4
        cx, cy = tween(hx + 4, 33.5, q), tween(info['y'] - 6, 25, q)
        L.ring(cx, cy, 4 - q * 1.5, 'N')
        L.line(hx, hy, cx - 3, cy + 1, 'N')
    else:
        L.ring(33.5, 25.5, 3, 'N')
        L.line(hx, hy, 31, 25, 'N')
    f.blit(L.shear(-0.07, 36) if tug else L)
    if tug and k % 2:
        f.art(P.SWEAT, 2, BY - 2)


TUMBLE = [['.nNn.', 'N.n.N', 'nN.Nn', 'N.n.N', '.nNn.'],
          ['.NnN.', 'n.N.n', 'Nn.nN', 'n.N.n', '.NnN.']]


def cowboy_tumbleweed(f, t, n):
    """Sheriff watches a tumbleweed bounce past, tips the hat."""
    k = t % 16
    f.rect(30, 22, 3, 14, 'E'); f.rect(27, 25, 2, 5, 'E'); f.rect(27, 29, 4, 2, 'E'); f.rect(35, 24, 2, 4, 'E')
    f.rect(33, 27, 4, 2, 'E'); f.rect(31, 22, 1, 14, 'e')
    for i in range(0, 40, 7):
        f.put(i + 2, 37, 'Y')
    wx = 42 - k * 3.2
    wy = 31 - [0, 2, 3, 2, 0][k % 5]
    look = 1 if wx > 24 else -1 if wx < 14 else 0
    tip = 7 <= k <= 10
    f.art(TUMBLE[k % 2], int(wx), int(wy))
    info = clawd(f, x=10, view='qr' if look > 0 else 'ql' if look < 0 else 'front', ra='up' if tip else 'side',
                 la='side', eyes='normal' if not tip else 'happy')
    P.hat(f, info, 'cowboy', dy=-2 if tip else 0)
    f.rect(int(wx) + 6, int(wy) + 2, 3, 1, 'L'); f.rect(int(wx) + 8, int(wy) + 4, 2, 1, 'L')


# --------------------------------------------------------------------------- rescue & medicine
def flame(f, cx, by, s, t):
    """Flame of size s (0..3) standing on row by."""
    if s <= 0:
        return
    hgt = 3 * s + 1
    for j in range(hgt):
        q = (j + 1) / hgt
        hw = max(0, int(round(q * s)))
        sway = ((t + j) % 3 == 0) * (1 if t % 2 else -1) if j < hgt / 2 else 0
        yy = by - hgt + j
        f.rect(cx - hw + sway, yy, 2 * hw + 1, 1, 'R')
        if hw >= 1 and j > 1:
            f.rect(cx - hw + 1 + sway, yy, 2 * hw - 1, 1, 'F')
        if hw >= 2 and j > hgt / 2:
            f.rect(cx - hw + 2, yy, 2 * hw - 3, 1, 'U')


def firefighter_hose(f, t, n):
    """Hose arcs water onto a fire until it's out, steam billows."""
    k = t % 16
    sz = [3, 3, 3, 3, 3, 3, 2, 2, 1, 1, 0, 0, 0, 0, 1, 2][k]
    spray = 2 <= k <= 11
    f.line(0, 34, 6, 32, 'g')
    info = clawd(f, x=3 - (1 if spray and k % 2 else 0), view='qr', ra='mid', la='mid',
                 eyes='focus' if sz else 'happy')
    P.hat(f, info, 'helmet')
    hx, hy = info['rh']
    f.rect(hx, hy - 1, 3, 2, 'g'); f.rect(hx + 3, hy - 1, 1, 2, 'Y')
    f.rect(23, 36, 14, 1, 'g')
    flame(f, 30, 36, sz, t)
    if spray:
        x0, y0, x1, y1 = hx + 4, hy - 1, 30, 32
        for i in range(7):
            p = ((k * 0.17 + i / 7) % 1)
            px = tween(x0, x1, p)
            py = tween(y0, y1, p) - 7 * math.sin(math.pi * p)
            f.rect(int(px), int(py), 2, 1, 'B' if i % 2 else 'S')
    if 9 <= k <= 13:
        P.rising(f, P.PUFF, t, n, 28, 30, count=2, height=12, jitter=3, seed=9)


def head_mirror(f, info):
    x, y = info['x'], info['y']
    f.rect(x + 1, y, 14, 1, 'g')
    f.disc(x + 8, y - 1, 2.3, 'G'); f.put(x + 7, y - 2, 'W'); f.put(x + 8, y - 1, 'g')


def doctor_stethoscope(f, t, n):
    """Doctor listens to a mini patient; a heartbeat scrolls on the monitor."""
    k = t % 16
    f.rect(23, 4, 16, 10, 'k'); f.rect(24, 5, 14, 8, 'b')
    P.heartbeat(f, 24, 10, 14, t, c='E')
    info = clawd(f, x=4, view='qr', ra='out', eyes='focus' if k < 10 else 'happy')
    head_mirror(f, info)
    x, y = info['x'], info['y']
    hx, hy = info['rh']
    f.line(hx - 3, hy + 3, hx, hy + 1, 'k'); f.line(hx - 4, hy + 4, hx - 7, hy + 4, 'k')
    ah = k in (6, 7, 8)
    mini(f, 27, 28, eyes='closed' if ah else 'normal', ra='side', la='side', view='ql')
    f.rect(hx, hy, 2, 2, 'g')
    if ah:
        P.speech(f, 28, 16, 11, 7, c='B', tail='down', text='AH')
    if k >= 10:
        P.rising(f, P.HEART, t, n, 30, 26, count=2, height=10, jitter=3, seed=2)


def scarecrow(f, t, n):
    """Straw-hat scarecrow on a pole: crows land on the arms, a wiggle shoos them off."""
    k = t % 16
    f.rect(0, 36, 40, 1, 'n')
    for i in range(1, 40, 5):
        f.art(['.E', 'EE', 'e.'], i, 33)
    f.rect(19, 17, 2, 19, 'N'); f.rect(2, 25, 36, 2, 'N'); f.rect(2, 25, 36, 1, 'n')
    wig = k in (10, 11, 12)
    L = Canvas()
    info = clawd(L, y=BY - 6, la='out', ra='out', leg_h=2, eyes='angry' if wig else 'blink' if k == 5 else 'normal')
    hat_art(L, info, STRAW, sink=1)
    for (hx, hy), d in ((info['lh'], -1), (info['rh'], 1)):
        L.art(['Y.', 'YY', 'Y.'] if d > 0 else ['.Y', 'YY', '.Y'], int(hx) + (0 if d > 0 else -2), int(hy) - 1)
    f.blit(L.shear((0.08 if k % 2 else -0.08) if wig else 0, 31))
    crow_sit = ['.kk.', 'kkkU', 'gkk.', '.k.k']
    crow_fly = [['k...k', 'gk.kg', '.kkk.', '..U..'], ['.....', 'gkkkg', 'k.k.k', '..U..']]
    for side, (hx, hy) in ((0, info['lh']), (1, info['rh'])):
        bx = int(hx) + (1 if side == 0 else -5)
        by = int(hy) - 6
        if k < 4:
            q = 1 - (k + 1) / 4
            fx_ = bx + (-14 if side == 0 else 14) * q
            f.art(crow_fly[k % 2], int(fx_), int(by - 16 * q))
        elif k < 11:
            peck = 1 if (k + side) % 3 == 0 else 0
            f.art(crow_sit if side == 0 else [r[::-1] for r in crow_sit], bx, by + peck)
        else:
            q = (k - 10) / 5
            fx_ = bx + (-14 if side == 0 else 14) * q
            f.art(crow_fly[k % 2], int(fx_), int(by - 18 * q))
    if wig:
        f.art(P.EXCL, 4, 8, cmap={'K': 'R'}); f.art(P.EXCL, 34, 9, cmap={'K': 'R'})


FLASK = """
    ..GG..
    ..GG..
    .GxxG.
    GxxxxG
    GxxxxG
    .GGGG.
"""
FLASK_TILT = """
    .GGG.....
    GxxxGG...
    GxxxxGGG.
    GxxxxG..G
    .GGGG....
"""


def scientist_potion(f, t, n):
    """Pours one flask into another; it bubbles, goes POOF and leaves soot."""
    k = t % 16
    f.rect(24, 31, 16, 1, 'G'); f.rect(24, 32, 16, 1, 'g'); f.rect(26, 33, 1, 3, 'g'); f.rect(37, 33, 1, 3, 'g')
    liquid = 'C' if k < 3 or k >= 14 else 'P' if k < 6 else 'E'
    sooty = 11 <= k <= 13
    info = clawd(f, x=4, view='qr', ra='out' if k < 6 else 'side',
                 eyes='focus' if k < 6 else 'big' if k < 10 else 'x' if k < 13 else 'blink' if k == 13 else 'happy',
                 y=BY - (2 if k == 10 else 0))
    x, y = info['x'], info['y']
    f.rect(x, y - 1, 16, 1, 'k'); f.rect(x + 4, y - 3, 4, 3, 'k'); f.rect(x + 10, y - 3, 4, 3, 'k')
    f.rect(x + 5, y - 2, 2, 1, 'C'); f.rect(x + 11, y - 2, 2, 1, 'C')
    f.art(FLASK, 28, 25, cmap={'x': liquid})
    hx, hy = info['rh']
    if 1 <= k <= 5:
        f.art(FLASK_TILT, int(hx) - 3, int(hy) - 5, cmap={'x': 'Z'})
        for yy in range(int(hy) - 2, 26):
            f.put(int(hx) + 5, yy, 'Z')
    elif k == 0:
        f.art(FLASK, int(hx) - 2, int(hy) - 5, cmap={'x': 'Z'})
    if 6 <= k <= 9:
        P.rising(f, ['.E.', 'E.E', '.E.'], t, n, 30, 22, count=3, height=8, jitter=2, seed=4)
    if k == 10:
        smoke(f, 31, 15, 5, c='E', edge='e'); smoke(f, 21, 9, 3, c='p', edge='P')
    elif 11 <= k <= 12:
        smoke(f, 22 + k, 10 - (k - 11) * 3, 3)
    if sooty:
        f.art(['.L.', 'L.L'], x + 6, y - 4)


# --------------------------------------------------------------------------- register 11-20
add('cos_royal_wave', '国王巡游挥手', 'Royal parade wave', royal_wave, n=12, dur=150)
add('cos_royal_knighting', '册封小骑士', 'Knighting ceremony', royal_knighting, n=16, dur=140)
add('cos_detective_trail', '侦探追脚印', 'Detective on the trail', detective_trail, n=24, dur=110)
add('cos_spy_sneak', '报纸后的间谍', 'Newspaper spy', spy_sneak, n=24, dur=120)
add_tweened('cos_cowboy_lasso', '牛仔套索', 'Cowboy lasso throw', cowboy_lasso, n=20, dur=100, tw_at={9: 1})
add('cos_cowboy_tumbleweed', '警长与风滚草', 'Sheriff and tumbleweed', cowboy_tumbleweed, n=16, dur=130)
add('cos_firefighter_hose', '消防员灭火', 'Firefighter hose', firefighter_hose, n=16, dur=110)
add('cos_doctor_stethoscope', '医生听诊', 'Doctor checkup', doctor_stethoscope, n=16, dur=150)
add('cos_scarecrow', '稻草人赶乌鸦', 'Scarecrow and crows', scarecrow, n=16, dur=130)
add('cos_scientist_potion', '科学家调药水', 'Potion goes poof', scientist_potion, n=16, dur=beats(16, 130, {10: 350, 11: 200, 12: 200}))


# --------------------------------------------------------------------------- mad science & robots
def zigzag(f, x0, y0, x1, y1, seed, c='U', c2='W', steps=5, amp=2):
    r = rng(seed)
    pts = [(x0, y0)]
    for i in range(1, steps):
        q = i / steps
        pts.append((tween(x0, x1, q) + r.uniform(-amp, amp), tween(y0, y1, q) + r.uniform(-amp, amp)))
    pts.append((x1, y1))
    for (a, b), (c_, d) in zip(pts, pts[1:]):
        f.line(a, b + 1, c_, d + 1, c2)
        f.line(a, b, c_, d, c)


def mad_lightning(f, t, n):
    """Tesla coil arcs into a wild-haired scientist who lights up."""
    k = t % 12
    f.rect(1, 31, 9, 5, 'g'); f.rect(1, 31, 9, 1, 'G')
    for yy in range(18, 31):
        f.rect(4, yy, 3, 1, 'F' if yy % 2 else 'N')
    f.disc(5.5, 15.5, 3.2, 'G'); f.put(4, 14, 'W'); f.put(5, 13, 'W')
    zap = k % 4 in (0, 1)
    flash = k % 4 == 1
    info = clawd(f, x=22, la='up', ra='up' if zap else 'high', eyes='big' if zap else 'worried',
                 y=BY - (1 if zap else 0))
    x, y = info['x'], info['y']
    for i in range(0, 16, 3):
        up = 2 if zap and i % 2 == 0 else 1
        f.rect(x + i, y - up, 2, up, 'W'); f.put(x + i + 1, y - up - 1, 'G')
    f.rect(x, y - 1, 16, 1, 'G') if not zap else None
    hx, hy = info['lh']
    if zap:
        zigzag(f, 8, 15, hx, hy, k, steps=4)
        zigzag(f, 6, 12, 2, 4, k + 7, c='C', steps=3, amp=1.5)
        zigzag(f, 8, 13, 14, 6, k + 3, c='C', steps=3, amp=1.5)
    else:
        f.art(['.C.', 'C.C', '.C.'], 4, 11 - k % 2)
    if flash:
        for (sx_, sy_) in ((19, 24), (39, 22), (29, 15)):
            f.art(['U.U', '.U.', 'U.U'], sx_ - 1, sy_ - 1)
    if 8 <= k <= 9:
        P.burst(f, 31, 8, 'ZAP')


def robot_beep(f, t, n):
    """Robot costume: jerky robot dance, blinking chest lights, BEEP / BOOP."""
    k = t % 16
    poses = [('out', 'low'), ('up', 'side'), ('low', 'out'), ('side', 'up')]
    la, ra = poses[(k // 2) % 4]
    dx = [0, 1, 0, -1][(k // 2) % 4]
    info = clawd(f, x=BX + dx, la=la, ra=ra, eyes='line' if k % 4 == 3 else 'normal',
                 legs=(1, 0, 0, 0) if (k // 2) % 2 else (0, 0, 0, 1))
    x, y = info['x'], info['y']
    f.rect(x + 1, y - 3, 14, 3, 'G'); f.rect(x, y - 1, 16, 1, 'g')
    for bx in (x + 2, x + 13):
        f.put(bx, y - 2, 'W')
    for i, c in enumerate('REU'):
        f.put(x + 5 + i * 3, y - 2, c if (k + i) % 3 else 'g')
    f.rect(x + 7, y - 7, 2, 4, 'g')
    f.rect(x + 6, y - 9, 4, 2, 'R' if k % 2 else 'Z')
    if k % 8 < 6:
        P.say(f, info, 'BEEP' if k < 8 else 'BOOP', c='C')


def box_robot(f, t, n):
    """Cardboard-box robot suit round the body: a stiff, rocking waddle across."""
    x = -18 + int(58 * t / n)
    s_ = (t // 2) % 2
    L = Canvas()
    info = clawd(L, x=x, legs=(2, 0, 2, 0) if s_ else (0, 2, 0, 2), la='none', ra='none',
                 eyes='focus' if t % 8 else 'blink')
    y = info['y']
    by = y + 5
    L.rect(x - 2, by, 20, 7, 'N'); L.box(x - 2, by, 20, 7, 'n')
    L.rect(x + 6, by, 4, 7, 'T')
    L.art(['NN.', '.NN'], x - 4, by - 2); L.art(['.NN', 'NN.'], x + 17, by - 2)
    L.rect(x, by + 2, 3, 3, 'k'); L.put(x + 1, by + 3, 'R' if t % 2 else 'E')
    L.rect(x + 13, by + 2, 2, 1, 'U'); L.rect(x + 13, by + 4, 2, 1, 'B')
    sw = 1 if s_ else -1
    L.rect(x - 5, by + 2 + sw, 3, 3, 'O'); L.rect(x + 18, by + 2 - sw, 3, 3, 'O')
    L.rect(x + 2, y - 1, 12, 1, 'g')
    ax = x + 8 + (1 if t % 4 < 2 else -1)
    L.line(x + 8, y - 1, ax, y - 5, 'g'); L.disc(ax + .5, y - 6.5, 1.5, 'G'); L.put(ax, y - 7, 'W')
    f.blit(L.shear(0.07 if s_ else -0.07, 36))


# --------------------------------------------------------------------------- creature suits
def dino_roar(f, t, n):
    """Dinosaur hoodie: stomp stomp, wind-up, big RAWR."""
    k = t % 16
    roar = 8 <= k <= 12
    wind = k in (6, 7)
    L = Canvas()
    shake = (1 if k % 2 else -1) if roar else 0
    info = clawd(L, x=BX + shake, eyes='angry' if roar else 'closed' if wind else 'normal',
                 legs=((2, 0, 2, 0) if (k // 2) % 2 else (0, 2, 0, 2)) if k < 6 else (0, 0, 0, 0),
                 la='high' if roar else 'side', ra='high' if roar else 'side')
    x, y = info['x'], info['y']
    # tail
    wag = (k // 2) % 2
    L.rect(x + 16, y + 8, 2, 3, 'E'); L.rect(x + 18, y + 9 - wag, 3, 2, 'E'); L.rect(x + 21, y + 10 - wag * 2, 2, 1, 'E')
    # hood
    L.rect(x - 1, y - 3, 18, 3, 'E'); L.rect(x - 1, y - 3, 2, 8, 'E'); L.rect(x + 15, y - 3, 2, 8, 'E')
    L.rect(x + 1, y, 14, 1, 'e')
    for i in range(0, 16, 4):
        L.art(['.e.', 'eee'], x + i, y - 5)
    if roar:
        P.burst(f, 30, 8, 'RAWR')
    T = L
    if wind:
        T = L.shear(-0.1, 36)
    f.blit(T)
    if k < 6 and k % 2 == 0:
        P.dust(f, x - 2, GROUND, 0.4); P.dust(f, x + 16, GROUND, 0.4, flip=True)
    if roar:
        for yy in (BY + 2, BY + 6):
            f.rect(1 + k % 2, yy, 4, 1, 'L')


EARS_UP = """
    .GG......GG.
    GWWG....GWWG
    GWrG....GrWG
    GWrG....GrWG
    GWrG....GrWG
    GWrG....GrWG
    .GWG....GWG.
"""
EARS_FLOP = """
    GG..........GG
    GWWG......GWWG
    .GWrG....GrWG.
    ..GrG....GrG..
    ..GrG....GrG..
    ..GWG....GWG..
"""


def bunny_hop(f, t, n):
    """Bunny-eared Clawd hops across; the ears flop on every landing."""
    j = t % 4
    x = -12 + int(56 * t / n)
    dy = [0, -4, -6, -3][j]
    sq = j == 0
    info = clawd(f, x=x - (1 if sq else 0), y=BY + dy + (1 if sq else 0), w=18 if sq else 16, h=11 if sq else 12,
                 view='qr', eyes='happy' if j in (1, 2) else 'closed' if sq else 'normal',
                 legs=(1, 1, 1, 1) if j in (1, 2) else (0, 0, 0, 0))
    hat_art(f, info, EARS_FLOP if j in (0, 3) else EARS_UP, sink=1)
    f.art(['.GG.', 'GWWG', 'GWWG', '.GG.'], info['x'] - 3, info['y'] + 6)
    if sq:
        P.dust(f, x - 2, GROUND, 0.3)


def cat_purr(f, t, n):
    """Cat ears and whiskers: kneading, tail swishing, purring."""
    k = t % 16
    s = (k // 2) % 2
    info = clawd(f, y=BY + 2, leg_h=1, la='low' if s else 'side', ra='side' if s else 'low',
                 eyes='closed' if k % 8 else 'happy', h=12 - (k % 2))
    x, y = info['x'], info['y']
    hat_art(f, info, ['oO..........Oo', 'oOO........OOo', 'oOrO......OrOo', 'oOrrO....OrrOo'], sink=0)
    # tail
    sw = [0, 1, 2, 1, 0, -1, -2, -1][k % 8]
    pts = [(x + 15, y + 10), (x + 18, y + 9), (x + 20, y + 7), (x + 21 + sw // 2, y + 4), (x + 21 + sw, y + 1)]
    for (a, b), (c_, d) in zip(pts, pts[1:]):
        f.line(a, b, c_, d, 'O'); f.line(a + 1, b, c_ + 1, d, 'o')
    f.rect(pts[-1][0], pts[-1][1] - 1, 2, 2, 'O')
    # purr
    for i, yy in enumerate((y + 3, y + 8)):
        if (k + i) % 2:
            f.art(['L.', '.L', 'L.'], x - 7, yy); f.art(['.L', 'L.', '.L'], x + 23, yy)
    P.rising(f, ['L.L.', '.L.L'], t, n, x + 4, y - 4, count=2, height=10, jitter=5, seed=8)


FROGHAT = """
    .eeee......eeee.
    eWWKKe....eKKWWe
    eWWKKe....eKKWWe
    EEEEEEEEEEEEEEEE
    EEEEEEEEEEEEEEEE
    eeeeeeeeeeeeeeee
"""


def frog_tongue(f, t, n):
    """Frog-hat Clawd snaps a buzzing fly with a long tongue, gulps."""
    k = t % 16

    def flypos(q):
        a = 2 * math.pi * q
        return 28 + 7 * math.cos(a), 12 + 4 * math.sin(2 * a)
    gulp = k in (12, 13)
    info = clawd(f, x=BX - (1 if gulp else 0), w=18 if gulp else 16, y=BY + 1, h=11,
                 eyes='happy' if k >= 12 else 'focus' if k >= 6 else 'normal')
    hat_art(f, info, FROGHAT, sink=1)
    mx, my = info['x'] + info['w'] // 2, info['y'] - 2
    f.rect(mx - 4, my, 8, 1, 'e')
    if k in (9, 10, 11):
        f.rect(mx - 2, my - 1, 4, 2, 'M')
    if k < 10:
        fx, fy = flypos(k / 10)
        f.art(P.FLY if k % 2 else ['k.k', 'kkk'], int(fx), int(fy))
    elif k == 10:
        fx, fy = flypos(1.0)
        f.line(mx, my, fx + 1, fy + 1, 'Z'); f.line(mx - 1, my, fx, fy + 1, 'Z')
        f.rect(int(fx), int(fy), 3, 2, 'R')
        f.art(P.FLY, int(fx), int(fy) - 2)
    elif k == 11:
        fx, fy = tween(mx, flypos(1.0)[0], .45), tween(my, flypos(1.0)[1], .45)
        f.line(mx, my, fx, fy, 'Z'); f.rect(int(fx), int(fy) - 1, 3, 2, 'R')
        f.art(P.FLY, int(fx), int(fy) - 2)
    elif k >= 14:
        f.art(P.FLY, 40 - (k - 13) * 4, 12)
    if 6 <= k <= 9:
        f.art(P.EXCL, info['x'] - 3, info['y'] - 9)


# --------------------------------------------------------------------------- viking
VIKING = """
    Y..............Y
    yY....gggg....Yy
    yyY.gGGGGGGg.Yyy
    .yygGGGGGGGGgyy.
    ..gGGWGGGGGGGg..
    gggggggggggggggg
"""
HORN = """
    ..........NN
    .........yyN
    ........yyy.
    .......yyY..
    .....yyyY...
    ..TTyyY.....
    TTTTY.......
"""


def viking_horn(f, t, n):
    """Viking puffs up and blasts a horn; sound waves roll out."""
    k = t % 12
    blow = 3 <= k <= 10
    puff = k in (1, 2)
    L = Canvas()
    info = clawd(L, x=3 - (1 if puff else 0), w=18 if puff else 16, view='qr', ra='high',
                 eyes='closed' if blow else 'normal', tilt=1 if blow else 0)
    x, y, w_ = info['x'], info['y'], info['w']
    hat_art(L, info, VIKING, sink=1)
    # braided beard
    L.art(HORN, x + w_, y - 1 + (0 if blow else 2))
    f.blit(L.shear(-0.05, 36) if blow else L)
    if blow:
        bx, by = x + 26, y - 1
        for i in range(3):
            r = 3 + ((k - 3) * 2 + i * 4) % 12
            for a in range(-6, 3):
                ang = a * 0.25
                f.put(bx + r * math.cos(ang), by + r * math.sin(ang), 'B' if i % 2 else 'U')


# --------------------------------------------------------------------------- magician
MWAND = (['W', 'k', 'k', 'k', 'k', 'W'], 0, 4)


def magic_table(f):
    f.rect(22, 30, 17, 2, 'P'); f.rect(22, 32, 17, 1, 'U')
    f.rect(25, 33, 1, 3, 'n'); f.rect(35, 33, 1, 3, 'n')


def magician_hat(f, t, n):
    """Taps an upside-down top hat on the table and a mini Clawd pops out."""
    k = t % 20
    magic_table(f)
    up = [0, 0, 0, 0, 0, 0, 3, 6, 9, 10, 10, 10, 10, 10, 7, 3, 0, 0, 0, 0][k]
    if up:
        M = Canvas()
        mini(M, 27, 26 - up, eyes='happy' if 9 <= k <= 13 else 'normal', la='up' if 10 <= k <= 13 and k % 2 else 'side',
             ra='up' if 9 <= k <= 13 else 'side')
        for yy in range(24, 40):
            M.px[yy] = [None] * 40
        f.blit(M)
    f.rect(24, 24, 13, 1, 'k'); f.rect(24, 23, 13, 1, 'g')
    f.rect(26, 25, 9, 5, 'k'); f.rect(26, 28, 9, 1, 'R'); f.rect(26, 25, 1, 5, 'g')
    ra = ['high', 'mid', 'high', 'mid', 'out', 'out'][k] if k < 6 else 'up' if 9 <= k <= 13 else 'side'
    info = clawd(f, x=2, view='qr', ra=ra, la='up' if 9 <= k <= 13 else 'side',
                 eyes='focus' if k < 6 else 'happy' if 9 <= k <= 13 else 'normal')
    P.item(f, info['rh'], '', art=MWAND)
    if k < 4:
        hx, hy = info['rh']
        f.art(P.SPARK, int(hx) + 1, int(hy) - 7 + k % 2)
    if k == 5:
        smoke(f, 30, 21, 3)
    if 9 <= k <= 13:
        P.sparkles(f, k, 4, [(23, 16), (37, 14), (30, 10)])


CARD = [['GGG', 'GWG', 'GZG', 'GWG', 'GGG'], ['G', 'G', 'G', 'G', 'G'], ['GGG', 'GWG', 'GkG', 'GWG', 'GGG']]


def magician_cards(f, t, n):
    """A stream of playing cards springs from hand to hand over the head."""
    info = clawd(f, la='mid', ra='mid', eyes='normal', look=int(round(sin(t, n) * 1)))
    P.hat(f, info, 'tophat')
    x0, y0 = info['lh'][0], info['lh'][1] - 2
    x1, y1 = info['rh'][0], info['rh'][1] - 2
    for i in range(11):
        q = ((t / n) * 2 + i / 11) % 1
        cx = tween(x0, x1, q)
        cy = tween(y0, y1, q) - 12 * math.sin(math.pi * q)
        side = (i + t) % 3
        f.art(CARD[0 if side == 0 else 1 if side == 1 else 2], int(cx) - 1, int(cy) - 2)


# --------------------------------------------------------------------------- register 21-30
add('cos_mad_lightning', '疯狂科学家', 'Mad-scientist lightning', mad_lightning, n=12, dur=90)
add('cos_robot_beep', '机器人舞', 'Robot costume dance', robot_beep, n=16, dur=130)
add('cos_box_robot', '纸箱机器人', 'Cardboard box robot', box_robot, n=16, dur=130)
add('cos_dino_roar', '恐龙连帽衫', 'Dino hoodie RAWR', dino_roar, n=16, dur=110)
add('cos_bunny_hop', '兔耳蹦跳', 'Bunny-ear hops', bunny_hop, n=16, dur=90)
add('cos_cat_purr', '猫耳呼噜', 'Cat ears purring', cat_purr, n=16, dur=150)
add('cos_frog_tongue', '青蛙帽吐舌', 'Frog hat catches a fly', frog_tongue, n=16, dur=beats(16, 110, {10: 300, 11: 200}))
add('cos_viking_horn', '维京号角', 'Viking horn blast', viking_horn, n=12, dur=120)
add_tweened('cos_magician_hat', '帽子变出小Clawd', 'Mini out of the hat', magician_hat, n=20, dur=120, tw_at={8: 1, 13: 1})
add('cos_magician_cards', '魔术师飞牌', 'Card spring flourish', magician_cards, n=14, dur=90)


# --------------------------------------------------------------------------- circus & fantasy
def clown_juggle(f, t, n):
    """Clown wig, red nose, ruff and big shoes, juggling a three-ball cascade."""
    k = t % 12
    s = (k // 2) % 2
    info = clawd(f, la='mid' if s else 'side', ra='side' if s else 'mid', eyes='happy' if k % 6 < 3 else 'normal',
                 lookv=-1)
    x, y = info['x'], info['y']
    f.art(['.ZB', 'UZB', 'ZUZ', '.Z.'], x - 2, y - 2)
    f.art(['BZ.', 'BZU', 'ZUZ', '.Z.'], x + 15, y - 2)
    P.hat(f, info, 'party', dy=-1)
    f.rrect(x - 3, 34, 7, 3, 'R'); f.rrect(x + 12, 34, 7, 3, 'R'); f.put(x - 2, 34, 'W'); f.put(x + 13, 34, 'W')
    lx, ly = info['lh'][0] - 1, info['lh'][1] - 2
    rx, ry = info['rh'][0] + 1, info['rh'][1] - 2
    for i, c in enumerate('RBE'):
        p = (t / n + i / 3) % 1
        if p < .5:
            q = p * 2
            bx, by = tween(lx, rx, q), tween(ly, ry, q) - 13 * math.sin(math.pi * q)
        else:
            q = (p - .5) * 2
            bx, by = tween(rx, lx, q), tween(ry, ly, q) - 13 * math.sin(math.pi * q)
        f.disc(bx, by, 2, c); f.put(bx - 1, by - 1, 'W')


TAIL = """
    CCCCCCCCCCCCCC
    CCeCCCeCCCeCCC
    .CCCeCCCeCCCC.
    ..CCCCCCCCCC..
    ...CCeCCCeC...
    ....CCCCCC....
    .....CCCC.....
    ....CCCCCC....
    ..CCCC..CCCC..
    .CCC......CCC.
"""


def water(f, t, y0=31, crest='S'):
    f.rect(0, y0, 40, 40 - y0, 'B')
    for i in range(8):
        xx = (i * 6 + t) % 44 - 3
        f.rect(xx, y0 + (i % 3) * 2, 3, 1, crest)
    for xx in range(0, 40, 4):
        f.put((xx + t) % 40, y0 - 1, 'S')


def mermaid_splash(f, t, n):
    """Mermaid-tail Clawd leaps out of the waves in an arc and dives back in."""
    k = t % 20
    M = Canvas()
    if k <= 12:
        q = k / 12
        x = int(-2 + q * 26)
        y = int(30 - 20 * math.sin(math.pi * q))
        info = clawd(M, x=x, y=y, leg_h=0, la='up' if q < .5 else 'side', ra='up' if q < .5 else 'side',
                     eyes='happy' if .3 < q < .7 else 'closed')
        M.art(TAIL, x + 1, y + 12)
        M.art(['.F.', 'FFF', '.F.'], x + 12, y - 2)
        M = M.shear(0.25 * (0.5 - q) * 2, y + 12)
        for yy in range(32, 40):
            M.px[yy] = [None] * 40
    water(f, t)
    f.blit(M)
    for (sx, start) in ((4, 0), (26, 11)):
        j = k - start
        if 0 <= j < 4:
            for d in (-1, 1):
                for i in range(3):
                    f.rect(sx + d * (2 + j * 2 + i), 29 - (3 - abs(j - 1)) - i * 2 + j, 1, 2, 'S' if i % 2 else 'W')
            f.rect(sx - 3, 30, 7, 1, 'W')
    if k >= 13:
        j = k - 13
        f.ring(28, 31.5, 2 + j, 'S') if j < 5 else None
        if k in (15, 16, 17):
            f.art(['C.C', '.C.'], 30 - (k - 15), 29)
        P.rising(f, ['W'], t, n, 26, 34, count=2, height=4, jitter=3, seed=k)


WING = {
    'up': ['GG......', 'GWGG....', 'GWWWGG..', '.GWWWWG.', '..GWWWWG', '...GGGGG'],
    'mid': ['........', 'GGGG....', 'GWWWGGGG', '.GWWWWWG', '..GGGGGG', '........'],
    'down': ['........', '...GGGGG', '..GWWWWG', '.GWWWWG.', 'GWWWGG..', 'GG......'],
}


def angel_flutter(f, t, n):
    """Feathered wings flap, halo bobs, a few feathers float down."""
    k = t % 12
    dy = int(round(2 * sin(t, n))) - 4
    w = ['up', 'mid', 'down', 'mid'][k % 4]
    L = Canvas()
    x, y = BX, BY + dy
    L.art(WING[w], x - 8, y + 1)
    L.art(WING[w], x + 16, y + 1, flip=True)
    info = clawd(L, x=x, y=y, eyes='happy', legs=(1, 0, 1, 0) if k % 4 < 2 else (0, 1, 0, 1),
                 la='low', ra='low')
    P.falling(f, ['.G', 'GW', 'W.'], t, n, count=3, seed=13, sway=3, top=-4, bottom=40)
    f.blit(L)
    hb = (k // 2) % 2
    f.art(['.UUUUUU.', 'U......U', '.UUUUUU.'], x + 4, y - 7 - hb, cmap=None)


PITCHFORK = (['g.g.g', 'g.g.g', 'ggggg', '..R..', '..R..', '..R..', '..R..', '..R..', '..R..'], 2, 6)


def devil_fork(f, t, n):
    """Little devil horns and tail; jabs the pitchfork at a balloon - POP - and snickers."""
    k = t % 12
    jab = k == 5
    laugh = 6 <= k <= 9
    info = clawd(f, x=BX - 2 + (1 if laugh and k % 2 else 0), view='qr', ra='up' if jab else 'high',
                 eyes='happy' if laugh else 'angry', tilt=1 if k in (4, 5) else 0)
    x, y = info['x'], info['y']
    P.hat(f, info, 'horns')
    wag = [0, 1, 2, 1][k % 4]
    f.line(x - 1, y + 10, x - 5, y + 7 - wag, 'R')
    f.line(x - 5, y + 7 - wag, x - 6, y + 2 - wag, 'R')
    f.art(['.R.', 'RRR'], x - 7, y + 0 - wag)
    hx, hy = info['rh']
    P.item(f, (hx, hy - (3 if jab else 0)), '', art=PITCHFORK, dx=1 if jab else 0)
    by = {0: 6, 1: 7, 2: 6, 3: 5, 4: 6, 10: -3, 11: 2}.get(k)
    if by is not None:
        f.art(P.ITEMS['balloon'][0], 30, by)
        f.line(32, by + 6, 31, by + 12, 'g')
    if k == 6:
        P.burst(f, 32, 9, 'POP', c='U', c2='Z')
    if laugh:
        f.text('HE', 30, 22 - (k % 2), 'R')


# --------------------------------------------------------------------------- sci-fi
def alien_ufo(f, t, n):
    """Antenna headband; a UFO beams Clawd up a little and sets it back down."""
    k = t % 16
    beam = 2 <= k <= 13
    lift = [0, 0, 0, 1, 2, 4, 6, 8, 9, 9, 8, 6, 4, 2, 1, 0][k]
    ux = 20 + int(round(sin(t, n)))
    if beam:
        for yy in range(10, 37):
            hw = 3 + (yy - 10) * 0.32
            if (yy + k) % 3:
                f.rect(int(ux - hw), yy, int(2 * hw), 1, 'y')
    info = clawd(f, y=BY - lift, legs=(1, 0, 1, 0) if lift and k % 2 else (0, 1, 0, 1) if lift else (0, 0, 0, 0),
                 la='wave' if lift >= 6 else 'side', ra='up' if lift >= 6 and k % 2 else 'side',
                 eyes='happy' if lift >= 4 else 'big' if beam else 'normal', lookv=-1 if beam else 0)
    x, y = info['x'], info['y']
    bob = k % 2
    for ax, d in ((x + 3, -1), (x + 12, 1)):
        f.line(ax, y - 1, ax + d, y - 4, 'k')
        f.rect(ax + d - (1 if d < 0 else 0), y - 6 + bob, 2, 2, 'E'); f.put(ax + d - (1 if d < 0 else 0), y - 6 + bob, 'W')
    # saucer
    f.rrect(ux - 4, 1, 8, 4, 'C'); f.put(ux - 2, 2, 'W')
    f.rrect(ux - 11, 5, 22, 4, 'G'); f.rect(ux - 11, 7, 22, 1, 'g'); f.rect(ux - 8, 9, 16, 1, 'g')
    for i in range(5):
        f.put(ux - 9 + i * 4 + 1, 6, pick(['U', 'Z', 'C'], i + k))


def sailor_row(f, t, n):
    """Sailor cap, rowing a little boat over the waves, a gull overhead."""
    k = t % 16
    water(f, t, y0=33)
    bob = [0, 0, 1, 1][(k // 2) % 4]
    L = Canvas()
    ph_ = (k // 2) % 4
    arm = ['high', 'mid', 'side', 'low'][ph_]
    info = clawd(L, x=BX, y=BY - 2 + bob, la=arm, ra=arm, eyes='happy' if ph_ == 3 else 'focus' if ph_ < 2 else 'normal')
    hat_art(L, info, ['...GGGGGGGG...', '..GWWWWWWWWG..', '..bbbbbbbbbb..'], sink=0)
    x, y = info['x'], info['y']
    # oars
    for d, (hx, hy) in ((-1, info['lh']), (1, info['rh'])):
        ox = hx + d * [4, 6, 8, 6][ph_]
        oy = 36 + [-4, -1, 1, -2][ph_]
        L.line(hx, hy, ox, oy, 'N')
        L.rect(ox - (2 if d < 0 else 0), oy, 3, 2, 'N')
    hy = y + 9
    L.rect(4, hy, 32, 2, 'n'); L.rect(5, hy + 2, 30, 2, 'N'); L.rect(7, hy + 4, 26, 1, 'N'); L.rect(9, hy + 5, 22, 1, 'n')
    L.put(10, hy + 2, 'W'); L.put(28, hy + 2, 'W')
    f.blit(L.shear([0, .03, 0, -.03][ph_], 36))
    if ph_ == 1:
        for sx in (1, 36):
            f.art(['W.W', '.S.'], sx, 31)
    gx = 44 - (t * 3) % 52
    f.art(['k.k', '.k.'] if k % 2 else ['kk.kk', '..k..'], gx, 5 + (k % 3))


# --------------------------------------------------------------------------- crafts & trades
STRAW = """
    .....YYYYYY.....
    ....YYYYYYYY....
    ....NNNNNNNN....
    YYYYYYYYYYYYYYYY
    .yyyyyyyyyyyyyy.
"""


def farmer_water(f, t, n):
    """Straw hat and overalls; watering two sprouts until they bloom."""
    k = t % 16
    f.rect(23, 35, 17, 2, 'n'); f.rect(23, 35, 17, 1, 'N')
    stage = min(4, k // 3)
    for px in (27, 34):
        a = P.sprout_art(stage)
        w_, h_ = size(a)
        f.art(a, px - w_ // 2, 35 - h_)
    pour = k < 12
    info = clawd(f, x=3, view='qr', ra='mid' if pour else 'side', la='side',
                 eyes='focus' if pour else 'happy')
    x, y = info['x'], info['y']
    hat_art(f, info, STRAW, sink=1)
    hx, hy = info['rh']
    cx, cy = int(hx), int(hy) - 3
    if pour:
        f.rect(cx, cy, 6, 5, 'G'); f.box(cx, cy, 6, 5, 'g'); f.art(['.ggg.', 'g...g'], cx, cy - 2)
        f.line(cx + 6, cy + 1, cx + 9, cy + 3, 'g'); f.rect(cx + 9, cy + 3, 2, 2, 'g')
        for i in range(4):
            p = ((k / 4) + i / 4) % 1
            for px in (cx + 10, cx + 12):
                f.rect(px + int(p * 3) + i % 2 * 2, cy + 5 + int(p * (33 - cy - 5)), 1, 2, 'B')
    else:
        f.rect(cx - 1, cy + 3, 6, 5, 'G'); f.box(cx - 1, cy + 3, 6, 5, 'g')
        P.sparkles(f, k, 4, [(24, 22), (37, 20), (31, 16)])


def puppeteer(f, t, n):
    """From a ledge, works a cross-bar marionette of a mini Clawd dancing below."""
    k = t % 16
    s = (k // 2) % 2
    f.rect(0, 26, 21, 2, 'N'); f.rect(0, 28, 21, 1, 'n'); f.rect(2, 29, 2, 7, 'n'); f.rect(17, 29, 2, 7, 'n')
    info = clawd(f, x=2, y=11, view='qr', ra='mid', eyes='focus' if k % 8 < 6 else 'squint')
    hx, hy = info['rh']
    tilt = 1 if s else -1
    bx = int(hx) + 4
    by = int(hy) - 2
    f.rect(hx, by, 5, 1, 'N')
    f.line(bx - 4, by + 1 + tilt, bx + 5, by + 1 - tilt, 'N'); f.rect(bx, by - 2, 1, 6, 'N')
    hop = [0, 2, 3, 2, 0, 0, 1, 0][k % 8]
    mx, my = 25, 28 - hop
    mini(f, mx, my, eyes='happy' if hop else 'normal', la='up' if s else 'side', ra='side' if s else 'up',
         legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))
    for (sx, sy, ex, ey) in ((bx - 4, by + 1 + tilt, mx - 1, my + (-2 if s else 2)),
                             (bx + 5, by + 1 - tilt, mx + 9, my + (2 if s else -2)),
                             (bx, by + 4, mx + 4, my)):
        f.line(sx, sy, ex, ey, 'L')


def mail_delivery(f, t, n):
    """Mail carrier walks up to a mailbox, posts a letter, the flag pops up."""
    k = t % 20
    f.rect(31, 26, 2, 10, 'g')
    f.rrect(27, 17, 10, 9, 'V'); f.rect(27, 25, 10, 1, 'b'); f.rect(29, 20, 6, 1, 'k'); f.put(28, 18, 'S')
    flag_up = 11 <= k
    if flag_up:
        f.rect(37, 15, 1, 8, 'g'); f.rect(37, 15, 3, 2, 'R')
    else:
        f.rect(37, 21, 3, 1, 'g'); f.rect(38, 22, 2, 2, 'R')
    if k < 7:
        x, v, walk = -16 + k * 4, 'qr', True
    elif k < 16:
        x, v, walk = 8, 'qr', False
    else:
        x, v, walk = 8 - (k - 15) * 6, 'ql', True
    posting = 8 <= k <= 10
    wave = 12 <= k <= 15
    info = clawd(f, x=x, y=BY + (k % 2 if walk else 0), view=v, legs=legs_walk(k) if walk else (0, 0, 0, 0),
                 ra='out' if posting else 'wave' if wave and k % 2 else 'up' if wave else 'side',
                 eyes='happy' if wave else 'normal', tilt=1 if posting else 0)
    x, y = info['x'], info['y']
    cap = ['....VVVVVV......', '...VVVUVVVV.....', '..VVVVVVVVVVkkk.'] if v == 'qr' else \
          ['......VVVVVV....', '.....VVVVUVVV...', '.kkkVVVVVVVVVV..']
    hat_art(f, info, cap)
    bxx = x - 7 if v == 'qr' else x + 17
    f.rect(bxx, y + 7, 6, 5, 'N'); f.rect(bxx, y + 7, 6, 2, 'n'); f.rect(bxx + 1, y + 6, 3, 1, 'W'); f.put(bxx + 3, y + 6, 'G')
    if posting:
        hx, hy = info['rh']
        ex = int(tween(hx, 30, (k - 8) / 2))
        ey = int(tween(hy - 2, 19, (k - 8) / 2))
        f.rect(ex, ey, 5, 4, 'W'); f.box(ex, ey, 5, 4, 'G'); f.art(['G...G', '.G.G.', '..G..'], ex, ey)
    if k == 11:
        f.art(['U.U', '.U.', 'U.U'], 34, 11)


def painter_easel(f, t, n):
    """Beret painter dabs a little landscape (with a self-portrait) onto the easel."""
    k = t % 24
    f.line(27, 14, 24, 35, 'N'); f.line(35, 14, 38, 35, 'N'); f.line(31, 20, 31, 35, 'n')
    cx0, cy0, cw, ch = 24, 11, 15, 12
    f.rect(cx0, cy0, cw, ch, 'W'); f.box(cx0, cy0, cw, ch, 'G'); f.rect(cx0 - 1, cy0 + ch, cw + 2, 1, 'N')
    st = k // 3
    if st >= 1:
        f.rect(cx0 + 1, cy0 + 1, cw - 2, 4, 'S')
    if st >= 2:
        f.disc(cx0 + 11.5, cy0 + 3, 2, 'U')
    if st >= 3:
        f.rect(cx0 + 1, cy0 + 8, cw - 2, 3, 'E'); f.rect(cx0 + 3, cy0 + 7, 6, 1, 'E')
    if st >= 4:
        f.rect(cx0 + 4, cy0 + 4, 5, 4, 'O'); f.put(cx0 + 5, cy0 + 5, 'K'); f.put(cx0 + 7, cy0 + 5, 'K')
        f.put(cx0 + 3, cy0 + 6, 'O'); f.put(cx0 + 9, cy0 + 6, 'O')
    painting = k < 15
    targets = [(29, 13), (34, 13), (30, 14), (35, 14), (36, 13), (34, 15), (28, 19), (33, 20), (30, 19),
               (29, 16), (30, 17), (31, 16), (28, 16), (31, 18), (30, 15)]
    paint = 'SSSSUUUEEEEOOOOO'[min(15, k)] if painting else 'O'
    back = 0 if painting else -3 if k < 21 else -1
    info = clawd(f, x=4 + back, view='qr', ra='mid' if painting else 'side', la='mid',
                 eyes='focus' if painting else 'happy')
    hat_art(f, info, ['......R.......', '..RRRRRRRRRR..', 'RRRRRRRRRRRRRR', '.MMMMMMMMMMMM.'], dx=-2, sink=1)
    lx, ly = info['lh']
    f.art(['.TTTTT.', 'TZTBTUT', 'TTETTTT', '.TTTT..'], int(lx) - 6, int(ly) - 1)
    f.art(['.GGGGG.', 'G.....G', 'G.....G', '.GGGG..'], int(lx) - 6, int(ly) - 1, only='G')
    hx, hy = info['rh']
    if painting:
        tx, ty = targets[k]
        f.line(hx, hy, tx - 1, ty + 1, 'N'); f.rect(tx - 1, ty, 2, 1, paint)
    else:
        f.line(hx, hy, hx + 3, hy - 4, 'N'); f.put(hx + 3, hy - 5, 'O')
        if 15 <= k <= 21:
            P.sparkles(f, k, 4, [(23, 8), (39, 12), (31, 6)])


# --------------------------------------------------------------------------- register 31-40
add('cos_clown_juggle', '小丑抛球', 'Clown juggling', clown_juggle, n=12, dur=100)
add_tweened('cos_mermaid_splash', '美人鱼跃水', 'Mermaid leap', mermaid_splash, n=20, dur=100, tw_at={5: 1})
add('cos_angel_flutter', '小天使扑翅', 'Angel wings flutter', angel_flutter, n=12, dur=120)
add('cos_devil_fork', '小恶魔戳气球', 'Little devil pops a balloon', devil_fork, n=12, dur=beats(12, 120, {6: 300, 7: 150}))
add('cos_alien_ufo', '外星人光束', 'UFO tractor beam', alien_ufo, n=16, dur=120)
add('cos_sailor_row', '水手划船', 'Sailor rowing', sailor_row, n=16, dur=140)
add('cos_farmer_water', '农夫浇花', 'Farmer watering sprouts', farmer_water, n=16, dur=140)
add('cos_puppeteer', '提线木偶师', 'Marionette puppeteer', puppeteer, n=16, dur=130)
add_tweened('cos_mail_delivery', '邮递员送信', 'Mail delivery', mail_delivery, n=20, dur=beats(20, 110, {10: 200, 11: 300}), tw_at={11: 1, 15: 1})
add('cos_painter_easel', '画家写生', 'Painter at the easel', painter_easel, n=24, dur=120)


# --------------------------------------------------------------------------- performers & guards
def thick(f, x0, y0, x1, y1, c):
    f.line(x0, y0, x1, y1, c); f.line(x0, y0 + 1, x1, y1 + 1, c)


def conductor_baton(f, t, n):
    """Conductor at the music stand beats a 4/4 pattern; the baton tip leaves a trail."""
    k = t % 16
    keys = [(33, 34), (24, 14), (39, 23), (33, 5)]

    def tip_at(kk):
        bb, qq = (kk % 16) // 4, (kk % 4) / 4
        aa, cc = keys[bb], keys[(bb + 1) % 4]
        return tween(aa[0], cc[0], qq), tween(aa[1], cc[1], qq) + 4 * math.sin(math.pi * qq)
    beat = k // 4
    tx, ty = tip_at(k)
    # music stand
    f.rect(3, 24, 1, 12, 'g'); f.rect(0, 35, 7, 1, 'g')
    f.rect(0, 20, 8, 5, 'W'); f.box(0, 20, 8, 5, 'G'); f.rect(1, 21, 3, 1, 'g'); f.rect(4, 23, 3, 1, 'g')
    y0 = BY + (1 if k % 4 == 0 else 0)
    ra = 'up' if ty < y0 - 3 else 'high' if ty < y0 + 3 else 'out' if tx > BX + 24 else 'low'
    info = clawd(f, x=BX, ra=ra, la='high' if beat == 0 else 'mid' if beat == 3 else 'side',
                 eyes='closed' if beat < 3 else 'happy', y=y0)
    hx, hy = info['rh']
    for d in (1, 2, 3):
        px, py = tip_at(k - d)
        f.rect(int(px), int(py), 2 if d == 1 else 1, 1, 'P' if d == 1 else 'p')
    dl = max(1.0, math.hypot(tx - hx, ty - hy))
    bx_, by_ = hx + (tx - hx) / dl * 8, hy + (ty - hy) / dl * 8
    f.line(hx, hy, bx_, by_, 'g'); f.put(bx_, by_, 'W'); f.put(hx, hy, 'N')
    P.notes(f, info, t, n, c='P', count=2, spread=12)


def sword_slash(f, t, n):
    """Swordsman slices a tossed apple clean in two, then sheathes."""
    k = t % 12
    slash = k == 4
    info = clawd(f, x=4, view='qr', ra='out' if slash else 'high' if k < 4 else 'side',
                 eyes='angry' if k in (3, 4, 5) else 'closed' if k >= 8 else 'focus', tilt=1 if k < 4 else 0)
    x, y = info['x'], info['y']
    f.rect(x, y - 1, 16, 2, 'B'); f.rect(x - 3, y + k % 2, 3, 1, 'B'); f.rect(x - 4, y + 1 - k % 2, 3, 1, 'B')
    hx, hy = info['rh']
    if slash:
        f.line(hx, hy - 1, hx + 9, hy - 6, 'g'); f.line(hx, hy - 2, hx + 9, hy - 7, 'W')
        f.rect(hx - 1, hy - 3, 1, 4, 'Y')
        for i in range(14):
            a = -2.2 + i * 0.16
            for r, c in ((12, 'W'), (11, 'S')):
                f.put(hx + 2 + r * math.cos(a), hy + 2 + r * math.sin(a), c)
    elif k < 4:
        P.item(f, info['rh'], '', art=SWORD)
    else:
        f.rect(x - 3, y + 5, 2, 9, 'n'); f.rect(x - 4, y + 4, 4, 1, 'Y'); f.rect(x - 3, y + 2, 2, 2, 'N')
    apple = P.ITEMS['apple'][0]
    if k < 5:
        q = (k + 1) / 5
        ax, ay = tween(40, 26, q), 22 - 16 * math.sin(math.pi * q * .8)
        f.art(apple, int(ax), int(ay))
    else:
        j = k - 5
        rows = parse(apple)
        left = [r[:3] for r in rows]
        right = [r[3:] for r in rows]
        yy = min(30, 12 + j * j * 1 + j * 2)
        f.art(left, 25 - j, int(yy) + (1 if j else 0))
        f.art(right, 30 + j, int(yy))
        f.rect(27 - j, int(yy) + 2, 1, 3, 'T'); f.rect(30 + j, int(yy) + 2, 1, 3, 'T')


def bee(f, x, y, t):
    f.art(['G.G' if t % 2 else '.G.', 'UkU'], int(x), int(y))


def beekeeper(f, t, n):
    """Veiled beekeeper lifts a honeycomb frame; bees loop, the smoker puffs."""
    k = t % 16
    lift = [0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0, 0, 0][k]
    info = clawd(f, la='mid' if lift > 1 else 'side', ra='side', eyes='happy' if 5 <= k <= 9 else 'normal')
    x, y = info['x'], info['y']
    hat_art(f, info, ['....GGGGGGGG....', '...GTTTTTTTTG...', '..GTTTTTTTTTTG..', 'GGTTTTTTTTTTTTGG',
                      'GTTTTTTTTTTTTTTG', '.GGGGGGGGGGGGGG.'], sink=1, dx=0)
    for vx in (x - 2, x - 1, x + 16, x + 17):
        for vy in range(y + 1, y + 8):
            if (vx + vy) % 2 == 0:
                f.put(vx, vy, 'L')
    lx, ly = info['lh']
    fx, fy = int(lx) - 9, int(ly) - 4 - lift * 2
    f.rect(fx, fy, 9, 8, 'N'); f.rect(fx + 1, fy + 1, 7, 6, 'Y')
    for cy in range(fy + 1, fy + 7, 2):
        for cx in range(fx + 1 + (cy // 2) % 2, fx + 8, 2):
            f.put(cx, cy, 'U')
    hx, hy = info['rh']
    f.rect(hx, hy - 2, 4, 5, 'G'); f.box(hx, hy - 2, 4, 5, 'g'); f.rect(hx + 1, hy - 3, 2, 1, 'g')
    f.rect(hx + 4, hy, 2, 2, 'N')
    if k % 4 < 2:
        P.rising(f, P.PUFF_S, t, n, hx + 1, hy - 5, count=2, height=8, jitter=1, seed=3)
    for i in range(4):
        a = 2 * math.pi * (t / n + i / 4)
        bx = 20 + 15 * math.cos(a) + (2 * math.sin(3 * a))
        by = 14 + 6 * math.sin(2 * a)
        bee(f, bx, by, t + i)


def lifeguard_ring(f, t, n):
    """Lifeguard on a high chair spots a waving swimmer and tosses the rescue ring."""
    k = t % 16
    f.line(4, 39, 6, 27, 'G'); f.line(19, 39, 17, 27, 'G'); f.rect(5, 32, 13, 1, 'G')
    f.rect(2, 25, 19, 2, 'W'); f.box(2, 25, 19, 2, 'G')
    f.rect(3, 4, 1, 21, 'g'); f.art(['RRRR', 'RRR.', 'RR..'] if k % 2 else ['RRR.', 'RRRR', 'RR..'], 4, 4)
    throw = 6 <= k <= 7
    info = clawd(f, x=4, y=12, leg_h=1, view='qr', ra='high' if k in (4, 5) else 'out' if throw else 'side',
                 eyes='big' if 2 <= k <= 3 else 'focus' if k < 8 else 'happy', tilt=1 if k in (4, 5) else 0)
    P.hat(f, info, 'cap')
    mx, my = 29, 30 + (k % 2)
    saved = k >= 11
    mini(f, mx, my, eyes='happy' if saved else 'normal', la='up' if not saved and k % 2 else 'side',
         ra='up' if not saved and k % 2 == 0 else 'side', view='ql')
    f.rect(22, 34, 18, 6, 'B')
    for i in range(4):
        f.rect((i * 5 + k) % 18 + 22, 34 + (i % 2) * 2, 3, 1, 'S')
    hx, hy = info['rh']
    if k < 6:
        rx, ry = hx + 1, hy - 1
    elif k < 11:
        q = (k - 5) / 5
        rx, ry = tween(hx + 2, mx + 4, q), tween(hy - 2, my + 3, q) - 10 * math.sin(math.pi * q)
    else:
        rx, ry = mx + 4, my + 4
    f.ring(rx, ry, 3.5, 'R'); f.ring(rx, ry, 2, 'W')
    for (a, b) in ((-3, 0), (2, 0), (0, -3), (0, 2)):
        f.put(rx + a, ry + b, 'W')
    if saved:
        f.rect(22, 34, 18, 1, 'B'); f.rect(int(rx) - 4, 34, 8, 1, 'R')
        P.sparkles(f, k, 4, [(25, 24), (38, 26), (33, 20)])
    if 0 <= k <= 3:
        f.art(P.EXCL, 36, 20 - k % 2, cmap={'K': 'R'})


def mime_box(f, t, n):
    """Mime in stripes and beret feels for the walls of an invisible box."""
    k = t % 16
    seg = k // 4
    dx = [0, 0, 0, -2][seg]
    la, ra = [('side', 'out'), ('out', 'out'), ('up', 'up'), ('out', 'side')][seg]
    info = clawd(f, x=BX + dx, la=la, ra=ra, eyes='worried' if seg in (1, 2) else 'normal',
                 look=1 if seg == 0 else -1 if seg == 3 else 0)
    x, y = info['x'], info['y']
    hat_art(f, info, ['.......k......', '..kkkkkkkkkk..', 'kkkkkkkkkkkkkk', '.gggggggggggg.'], dx=-3, sink=0)
    slide = (k % 4) - 1
    for side, st in (('l', la), ('r', ra)):
        hx, hy = info['lh'] if side == 'l' else info['rh']
        if st == 'out':
            px = int(hx) - 2 if side == 'l' else int(hx)
            f.rect(px, hy - 2 + slide, 2, 4, 'W'); f.box(px, hy - 2 + slide, 2, 4, 'G')
            wx = px - 1 if side == 'l' else px + 2
            for wy in range(int(hy) - 7, int(hy) + 7, 2):
                f.put(wx, wy, 'L')
        elif st == 'up':
            px = int(hx) - 2
            f.rect(px, hy - 2, 4, 2, 'W'); f.box(px, hy - 2, 4, 2, 'G')
    if seg == 2:
        for wx in range(x - 4, x + 21, 2):
            f.put(wx, y - 6, 'L')


def mech_pilot(f, t, n):
    """A tiny pilot in a big stomping mech: legs piston, the cockpit bobs."""
    k = t % 16
    s = (k // 4) % 2
    j = k % 4
    lift = [0, 2, 3, 1][j]
    bob = [1, 0, 0, 1][j]
    y0 = 6 + bob
    L = Canvas()
    info = clawd(L, x=BX, y=y0, leg_h=0, la='none', ra='none', eyes='focus' if j else 'closed')
    L.rect(26, y0 - 3, 1, 3, 'g'); L.put(26, y0 - 4, 'R' if k % 2 else 'U')
    hull_y = y0 + 9
    L.rect(8, hull_y, 24, 9, 'g'); L.rect(8, hull_y, 24, 1, 'G'); L.rect(8, hull_y + 8, 24, 1, 'k')
    L.rect(18, hull_y + 3, 4, 3, 'k'); L.rect(19, hull_y + 4, 2, 1, 'C')
    for rx in (10, 29):
        L.put(rx, hull_y + 2, 'G'); L.put(rx, hull_y + 6, 'G')
    for side, ax in ((0, 3), (1, 32)):
        sw = (1 if (j + side * 2) % 4 < 2 else -1)
        L.rect(ax, hull_y + 2 + sw, 5, 6, 'g'); L.rect(ax, hull_y + 2 + sw, 5, 1, 'G')
        L.art(['k.k', 'k.k'], ax + 1, hull_y + 8 + sw)
    f.blit(L)
    for side, lx in ((0, 11), (1, 23)):
        up = lift if side == s else 0
        top = hull_y + 9
        foot = 36 - up
        f.rect(lx, top, 6, 3, 'g'); f.rect(lx + 1, top + 3, 4, 1, 'k')
        f.rect(lx + 1, top + 4, 4, foot - top - 5, 'g'); f.rect(lx + 1, top + 4, 1, foot - top - 5, 'G')
        f.rect(lx - 1, foot - 2, 8, 2, 'k'); f.rect(lx - 1, foot - 2, 8, 1, 'g')
    if j == 0:
        px = 11 if s else 23
        P.dust(f, px - 3, GROUND, 0.5); P.dust(f, px + 7, GROUND, 0.5, flip=True)
    if j in (1, 2):
        f.art(P.PUFF_S, 4, hull_y - 3 - j)


def time_travel(f, t, n):
    """The clock spins and every jump lands Clawd in a different era's hat."""
    k = t % 16
    f.ring(20, 22, 16, 'G', t=1)
    for i in range(12):
        a = 2 * math.pi * i / 12
        f.put(20 + 14 * math.cos(a), 22 + 14 * math.sin(a), 'g')
    a1 = 2 * math.pi * k / 4
    a2 = 2 * math.pi * k / 16
    f.line(20, 22, 20 + 12 * math.sin(a1), 22 - 12 * math.cos(a1), 'P')
    f.line(20, 22, 20 + 8 * math.sin(a2), 22 - 8 * math.cos(a2), 'b')
    era = k // 4
    jump = k % 4 == 0
    info = clawd(f, eyes='big' if jump else 'normal', y=BY - (2 if jump else 0), la='up' if jump else 'side',
                 ra='mid')
    x, y = info['x'], info['y']
    if era == 0:
        hat_art(f, info, KNIGHT, sink=1)
    elif era == 1:
        P.hat(f, info, 'tophat')
    elif era == 2:
        P.hat(f, info, 'cowboy')
    else:
        f.rect(x + 1, y - 1, 14, 1, 'G')
        for ax in (x + 3, x + 12):
            f.rect(ax, y - 4, 1, 3, 'g'); f.rect(ax - 1, y - 6, 3, 2, 'C')
    hx, hy = info['rh']
    f.disc(hx + 2, hy - 2, 2.5, 'U'); f.put(hx + 2, hy - 3, 'k'); f.put(hx + 2, hy - 2, 'k'); f.put(hx + 3, hy - 2, 'k')
    f.rect(hx + 1, hy - 5, 2, 1, 'Y')
    if jump:
        for i in range(8):
            a = 2 * math.pi * i / 8 + k
            f.put(20 + 18 * math.cos(a), 24 + 12 * math.sin(a), 'P' if i % 2 else 'U')
        f.art(P.SPARK_BIG, 1, 3); f.art(P.SPARK_BIG, 32, 30)


def diver_helmet(f, t, n):
    """Brass dome diving helmet: slow-motion steps on the sea floor, bubbles and a fish."""
    k = t % 16
    f.rect(0, 36, 40, 4, 'y'); f.put(6, 37, 'Z'); f.put(31, 38, 'F')
    for sx in (2, 35):
        for i in range(10):
            sw = int(round(math.sin(i / 2.5 + t * 0.6)))
            f.rect(sx + sw, 35 - i, 2, 1, 'E' if i % 3 else 'e')
    fx = (t * 3) % 56 - 10
    f.art(P.ITEMS['fish'][0], 40 - fx, 6, flip=True)
    bob = [0, -1, -2, -2, -1, 0, 0, 0][k % 8]
    s_ = (k // 4) % 2
    info = clawd(f, y=BY + bob, legs=(2, 0, 2, 0) if s_ else (0, 2, 0, 2), la='mid' if s_ else 'high',
                 ra='high' if s_ else 'mid', eyes='normal' if k % 8 != 7 else 'blink')
    x, y, w = info['x'], info['y'], info['w']
    cx, cy = x + w / 2, y + 5
    rx, ry = w / 2 + 3, 10.5
    for yy in range(int(cy - ry - 1), int(cy) + 1):
        for xx in range(int(cx - rx - 1), int(cx + rx + 1)):
            d = ((xx + .5 - cx) / rx) ** 2 + ((yy + .5 - cy) / ry) ** 2
            if 0.72 <= d <= 1.0:
                f.put(xx, yy, 'N' if d > .87 else 'Y')
    f.rect(x - 2, y + 5, w + 4, 2, 'N'); f.rect(x - 2, y + 5, w + 4, 1, 'Y')
    for bx_ in (x - 1, x + 4, x + 11, x + 16):
        f.put(bx_, y + 6, 'U')
    f.rect(int(cx) + 4, int(cy - ry) + 2, 2, 1, 'W'); f.put(int(cx) + 6, int(cy - ry) + 3, 'W')
    f.rect(int(cx) - 1, int(cy - ry) - 1, 2, 2, 'N')
    f.line(cx, cy - ry - 2, cx + 4, 0, 'k')
    for i in range(3):
        p_ = (t / n * 2 + i / 3) % 1
        P.bubble_ring(f, cx - 3 + math.sin(p_ * 9 + i) * 2, cy - ry - 3 - p_ * 12, 1 + (i % 2) * .6, c='S')


PITH = """
    .....NNNNNN.....
    ...NTTTTTTTTN...
    ..NTTTTTTTTTTN..
    ..NNNNNNNNNNNN..
    NTTTTTTTTTTTTTTN
    .NNNNNNNNNNNNNN.
"""


def explorer_map(f, t, n):
    """Pith-helmet explorer: map upside-down, turn it round, aha - that way!"""
    k = t % 16
    pointing = k >= 12
    info = clawd(f, x=BX - (3 if pointing else 0), view='qr' if pointing else 'front', la='mid',
                 ra='out' if pointing else 'mid',
                 eyes='down' if k < 4 else 'worried' if k < 10 else 'big' if k < 12 else 'happy')
    hat_art(f, info, PITH, sink=1)
    x, y = info['x'], info['y']
    if pointing:
        mx, my, mw = x - 7, y + 9, 9
    elif 6 <= k <= 7:
        mx, my, mw = x + 6, y + 9, 4
    else:
        mx, my, mw = x - 3, y + 9, 22
    M = Canvas()
    M.rect(mx, my, mw, 7, 'T'); M.box(mx, my, mw, 7, 'N')
    if mw > 8:
        for i in range(0, mw - 4, 2):
            M.put(mx + 2 + i, my + 5 - (i // 4) % 2, 'R')
        M.art(['R.R', '.R.', 'R.R'], mx + mw - 5, my + 2)
        M.rect(mx + 2, my + 2, 2, 2, 'E'); M.put(mx + 5, my + 1, 'E')
        M.line(mx + 1, my + 6, mx + 6, my + 3, 'B')
    if 4 <= k <= 9 and mw > 8:
        M = M.flipy().shift(0, 2 * my + 7 - 40)
    f.blit(M)
    if 4 <= k <= 9:
        f.art(P.QMARK, x + 18, y - 8)
    elif 10 <= k <= 11:
        f.art(P.EXCL, x + 18, y - 8, cmap={'K': 'R'})
    if pointing:
        f.art(['..E..', '.EEE.', 'EEEEE', '..n..'], 33, 26)
        f.art(['.E.', 'EEE', '.n.'], 37, 29)


def crossing_guard(f, t, n):
    """Crossing guard holds up the STOP sign while mini Clawds cross the zebra."""
    f.rect(0, 36, 40, 4, 'g')
    for sx in range(1, 40, 5):
        f.rect(sx, 37, 3, 3, 'W'); f.rect(sx, 36, 3, 1, 'G')
    k = t % 16
    info = clawd(f, x=3, y=BY - 5, view='qr', ra='up', eyes='happy' if k % 8 < 6 else 'blink')
    x, y = info['x'], info['y']
    P.hat(f, info, 'cap')
    hx, hy = info['rh']
    f.rect(hx, hy - 4, 1, 4, 'g')
    sx, sy = int(hx) - 9, max(0, int(hy) - 13)
    f.rrect(sx, sy, 19, 9, 'G'); f.rrect(sx + 1, sy + 1, 17, 7, 'R')
    f.text('STOP', sx + 2, sy + 2, 'W')
    for i in range(3):
        mxp = int(((t / n) * 56 + i * 15) % 60) - 12
        s = (t + i) % 2
        mini(f, mxp, 29, eyes='happy' if i == 1 else 'normal', view='qr', legs=(1, 0, 1, 0) if s else (0, 1, 0, 1),
             la='up' if i == 1 and s else 'side')


# --------------------------------------------------------------------------- register 41-50
add('cos_conductor_baton', '指挥家', 'Conductor 4/4 beat', conductor_baton, n=16, dur=120)
add_tweened('cos_sword_slash', '剑客劈苹果', 'Swordsman apple slice', sword_slash, n=12, dur=beats(12, 100, {3: 200, 4: 300, 5: 200, 6: 150}), tw_at={3: 1})
add('cos_beekeeper', '养蜂人', 'Beekeeper and bees', beekeeper, n=16, dur=140)
add('cos_lifeguard_ring', '救生员扔救生圈', 'Lifeguard ring toss', lifeguard_ring, n=16, dur=120)
add_tweened('cos_mime_box', '默剧隐形箱', 'Mime in an invisible box', mime_box, n=16, dur=150, tw_at={7: 1, 11: 1})
add('cos_mech_pilot', '机甲驾驶员', 'Tiny mech pilot', mech_pilot, n=16, dur=110)
add('cos_time_travel', '时间旅行者', 'Time traveller hat jumps', time_travel, n=16, dur=120)
add('cos_diver_helmet', '深海潜水员', 'Brass-helmet diver', diver_helmet, n=16, dur=150)
add('cos_explorer_map', '探险家看地图', 'Explorer reads the map', explorer_map, n=16, dur=150)
add('cos_crossing_guard', '导护员举牌', 'Crossing guard', crossing_guard, n=16, dur=130)


# --------------------------------------------------------------------------- circus & fairy tale
def jester_ball(f, t, n):
    """Jester with jingling bells balances on a rolling striped ball."""
    k = t % 16
    bx = 20 + 6 * sin(t, n)
    br = 7
    rot = -bx / br
    for yy in range(21, 37):
        for xx in range(int(bx - 9), int(bx + 9)):
            dx, dy = xx + .5 - bx, yy + .5 - 29
            d = math.hypot(dx, dy)
            if d <= br:
                a = math.atan2(dy, dx) + rot
                f.put(xx, yy, 'g' if d > br - 1 else 'R' if int((a % (2 * math.pi)) / (math.pi / 3)) % 2 else 'U')
    f.put(bx - 3, 25, 'W'); f.put(bx - 4, 26, 'W')
    lean = -cos(t, n) * 0.12
    L = Canvas()
    s = k % 2
    info = clawd(L, x=int(round(bx)) - 8, y=10, legs=(1, 0, 1, 0) if s else (0, 1, 0, 1),
                 la='up' if (k // 2) % 2 else 'out', ra='out' if (k // 2) % 2 else 'up',
                 eyes='worried' if abs(lean) > .08 else 'happy')
    P.hat(L, info, 'jester')
    f.blit(L.shear(lean, 22))
    cx = int(info['head'][0])
    if k % 2 == 0:
        for (dx_, dy_) in ((-9, -7), (8, -7)):
            f.art(['U.U', '.U.', 'U.U'] if k % 4 == 0 else ['.U.', 'U.U', '.U.'], cx + dx_ + int(lean * 14), 10 + dy_ - 2)


def princess_twirl(f, t, n):
    """Tiara and a ball gown that flares out as she twirls."""
    k = t % 12
    v = ['front', 'qr', 'sr', 'back', 'sl', 'ql'][(k // 2) % 6]
    flare = .35 if v == 'front' else .55 if v in ('qr', 'ql') else .75
    y = BY - 2
    for j, yy in enumerate(range(y + 6, 37)):
        hw = 7 + j * flare
        f.rect(int(20 - hw), yy, int(2 * hw), 1, 'r')
        f.put(int(20 - hw), yy, 'Z'); f.put(int(20 + hw) - 1, yy, 'Z')
    f.rect(int(20 - (7 + (36 - y - 6) * flare)), 36, int(2 * (7 + (36 - y - 6) * flare)), 1, 'Z')
    for i in range(3):
        sx = 20 + int((7 + 9 * flare) * math.cos(k + i * 2))
        f.put(sx, 33 - i * 2, 'W')
    info = clawd(f, y=y, view=v, leg_h=0, la='high', ra='high', eyes='happy')
    if v != 'back':
        P.hat(f, info, 'tiara')
    else:
        P.hat(f, info, 'tiara', dy=1)
    P.orbit(f, 20, BY + 4, 17, 6, t, n, ['.W.', 'WUW', '.W.'], count=3)


ARCH_CAP = """
    ..........RR
    ....EEEEERR.
    ...EEEEEEeR.
    ..EEEEEEEEe.
    EEEEEEEEEEEE
"""


def archer_bullseye(f, t, n):
    """Feather-capped archer draws, looses, and hits the bullseye."""
    k = t % 16
    tx, ty = 34, 21
    wob = 1 if k in (10, 12) else -1 if k == 11 else 0
    f.line(31, 36, 33, 26, 'N'); f.line(37, 36, 35, 26, 'N')
    for r, c in ((5, 'R'), (4, 'W'), (3, 'R'), (2, 'W'), (1, 'U')):
        f.disc(tx + .5 + wob, ty + .5, r, c)
    f.ring(tx + .5 + wob, ty + .5, 5.6, 'g')
    draw = [0, 1, 2, 3, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0][k]
    info = clawd(f, x=2, view='qr', ra='out', la='side', eyes='focus' if k < 6 else 'big' if k < 10 else 'happy')
    hat_art(f, info, ARCH_CAP, dx=-1)
    hx, hy = info['rh']
    bx = int(hx) + 1
    f.line(bx, hy - 7, bx + 2, hy - 4, 'N'); f.line(bx + 2, hy - 4, bx + 2, hy + 3, 'N'); f.line(bx + 2, hy + 3, bx, hy + 6, 'N')
    px = bx - draw
    f.line(bx, hy - 7, px, hy, 'G'); f.line(px, hy, bx, hy + 6, 'G')
    if k < 6:
        f.line(px, hy, bx + 6, hy, 'N'); f.put(bx + 7, hy, 'g'); f.put(px, hy - 1, 'Z'); f.put(px, hy + 1, 'Z')
    elif k < 10:
        ax = int(tween(bx + 6, tx - 1, (k - 5) / 4))
        ay = int(tween(hy, ty, (k - 5) / 4))
        f.rect(ax - 7, ay, 7, 1, 'N'); f.put(ax, ay, 'g'); f.put(ax - 7, ay - 1, 'Z'); f.put(ax - 7, ay + 1, 'Z')
        f.rect(ax - 12, ay, 3, 1, 'L')
    else:
        f.rect(tx - 6 + wob, ty, 6, 1, 'N'); f.put(tx - 6 + wob, ty - 1, 'Z'); f.put(tx - 6 + wob, ty + 1, 'Z')
        if k >= 11:
            P.sparkles(f, k, 4, [(28, 13), (39, 15), (34, 12)])


def ringmaster_hoop(f, t, n):
    """Ringmaster holds up a hoop; a mini Clawd runs in and leaps through it."""
    k = t % 16
    f.rect(-1, BY + 6, 4, 10, 'R'); f.rect(-1, BY + 15, 4, 1, 'M'); f.put(1, BY + 8, 'U'); f.put(1, BY + 11, 'U')
    info = clawd(f, x=1, view='qr', ra='out', la='up' if k >= 10 else 'side',
                 eyes='happy' if k >= 10 else 'normal')
    x, y = info['x'], info['y']
    P.hat(f, info, 'tophat')
    hx, hy = info['rh']
    cx, cy = 29, 22
    ring = [(cx + 2.5 * math.cos(a / 16 * 2 * math.pi), cy + 7 * math.sin(a / 16 * 2 * math.pi), a) for a in range(16)]
    f.line(hx, hy, cx - 1, cy + 7, 'g')
    for (px, py, a) in ring:
        if px < cx:
            f.rect(px, py, 2, 1, 'R' if a % 2 else 'U')
    # mini path
    p = k / 16
    mxp = -8 + p * 52
    if 12 <= mxp <= 34:
        q = (mxp - 12) / 22
        my = 29 - 12 * math.sin(math.pi * q)
    else:
        my = 29
    if mxp < 40:
        mini(f, int(mxp), int(my), eyes='happy' if my < 26 else 'normal', view='qr',
             legs=(1, 1, 1, 1) if my < 28 else (1, 0, 1, 0) if k % 2 else (0, 1, 0, 1),
             la='up' if my < 26 else 'side', ra='up' if my < 26 else 'side')
    for (px, py, a) in ring:
        if px >= cx:
            f.rect(px, py, 2, 1, 'R' if a % 2 else 'U')
    if 9 <= k <= 13:
        P.sparkles(f, k, 4, [(22, 10), (36, 12), (30, 6)])


LAMP = """
    .......U......
    .....YYYYY....
    YY..UUUUUUU...
    Y.YUUUUUUUUUUY
    YY.UUUUUUUUYY.
    ....YYYYYYY...
    ......YYYY....
"""


def genie_lamp(f, t, n):
    """Purple smoke curls from a golden lamp, becomes a turbaned genie, then pours back in."""
    k = t % 20
    lx, ly = 10, 29
    shake = 1 if k in (1, 2) else 0
    f.art(LAMP, lx + (shake if k % 2 else -shake), ly)
    sx, sy = lx + 13, ly + 3
    form = {7: .3, 8: .7, 15: .7, 16: .3}.get(k, 1 if 9 <= k <= 14 else 0)
    smoke_amt = {3: .25, 4: .5, 5: .75, 6: 1, 7: 1, 8: .8, 9: .5, 14: .5, 15: .8, 16: 1, 17: .75, 18: .5, 19: .25}.get(k, 0)
    bob = int(round(sin(t, 10)))
    gx, gy = 13, 4 + bob
    # smoky tail from spout up to the genie
    if smoke_amt or form:
        steps = 10
        for i in range(steps + 1):
            q = i / steps
            if q > max(smoke_amt, form):
                break
            px = sx + (gx + 8 - sx) * q + 3 * math.sin(q * 6 + k * .7)
            py = sy - (sy - (gy + 13)) * q
            r = 1 + q * 2.5
            f.disc(px, py, r + .8, 'P'); f.disc(px, py, r, 'p')
    if form:
        L = Canvas()
        info = clawd(L, x=gx, y=gy, leg_h=0, la='front', ra='front', eyes='happy' if 10 <= k <= 13 else 'normal',
                     lookv=1 if k in (12, 13) else 0, top=k in (12, 13))
        hat_art(L, info, ['......UU......', '...PPPPPPPP...', '..PPPPpPPPPP..', '.PPPPPPUPPPPP.', '.pppppppppppp.'],
                sink=1)
        L.rect(gx + 2, gy + 12, 12, 1, 'p')
        if form < 1:
            r_ = 4 if form < .5 else 7
            smoke(f, gx + 8, gy + 6, r_, c='p', edge='P')
        else:
            f.blit(L)
        if 10 <= k <= 13:
            P.sparkles(f, k, 4, [(8, 6), (33, 8), (30, 18)])


DWING = {
    'up': ['P.......', 'PP...P..', 'PpP.PpP.', 'PppPpppP', '.PpppppP', '..PPPPPP'],
    'down': ['..PPPPPP', '.PpppppP', 'PppPpppP', 'PpP.PpP.', 'PP...P..', 'P.......'],
}


def dragon_fire(f, t, n):
    """Dragon costume: bat wings flap, a deep breath, then a gout of fire."""
    k = t % 12
    up = k % 2 == 0
    dy = (-1 if up else 1) - 4
    inhale = k in (4, 5)
    breath = 6 <= k <= 9
    L = Canvas()
    x, y = 4, BY + dy
    L.art(DWING['up' if up else 'down'], x - 7, y - 1 + (0 if up else 3))
    L.art(DWING['up' if up else 'down'], x + 14, y - 3 + (0 if up else 3), flip=True)
    info = clawd(L, x=x - (1 if inhale else 0), y=y, w=18 if inhale else 16, view='qr', legs=(1, 1, 1, 1),
                 eyes='closed' if inhale else 'angry' if breath else 'normal')
    L.art(['Y......Y', 'YY....YY'], x + 4, y - 2)
    L.line(x, y + 10, x - 5, y + 13, 'P'); L.art(['.P.', 'PPP'], x - 7, y + 12)
    f.blit(L)
    if breath:
        mx, my = x + 17, y + 7
        ln = [10, 18, 20, 20][k - 6]
        for i in range(ln):
            hw = 1 + i * .3
            for yy in range(int(my - hw), int(my + hw) + 1):
                c = 'U' if abs(yy - my) < hw * .4 else 'F' if abs(yy - my) < hw * .8 else 'R'
                if (i + yy + k) % 5:
                    f.put(mx + i, yy, c)
    if k in (10, 11):
        smoke(f, 33, 28 - (k - 10) * 3, 2 + (k - 10))
    if inhale:
        f.art(['L.', '.L'], x + 20, y + 4); f.art(['.L', 'L.'], x + 20, y + 9)


def pilot_banner(f, t, n):
    """Aviator-cap Clawd flies a little plane across towing a HELLO banner."""
    x = -62 + int(104 * t / n)
    y = 12 + int(round(sin(t, n, 2)))
    cloud(f, (30 - t * 2) % 52 - 12, 30, 12)
    cloud(f, (10 - t) % 52 - 12, 4, 9)
    L = Canvas()
    # banner
    bx = x
    L.rect(bx, y + 6, 23, 8, 'W'); L.box(bx, y + 6, 23, 8, 'G')
    for i in range(0, 23, 4):
        if (i // 4 + t) % 2:
            L.put(bx + i, y + 13, 'G')
    L.text('HELLO', bx + 2, y + 8, 'R')
    L.line(bx + 23, y + 9, bx + 28, y + 10, 'g')
    px = bx + 30
    # plane + pilot
    info = clawd(L, x=px + 6, y=y, view='qr', la='none', ra='side', eyes='happy')
    L.art(['....NNNNNN.....', '...NNNNNNNNN...', '..NNNNNNNNNNNNN'], px + 6, y - 3)
    L.rect(px + 9, y - 3, 4, 2, 'k'); L.rect(px + 10, y - 2, 2, 1, 'C')
    L.rect(px + 6, y + 9, 22, 4, 'R'); L.rect(px + 6, y + 9, 22, 1, 'Z'); L.rect(px + 2, y + 9, 4, 3, 'R')
    L.art(['RRR', 'RR.', 'R..'], px, y + 6)
    L.rect(px + 10, y + 11, 14, 2, 'Y'); L.rect(px + 10, y + 12, 14, 1, 'y')
    L.rect(px + 28, y + 9, 2, 4, 'g')
    L.rect(px + 30, y + 5 if t % 2 else y + 10, 1, 6 if t % 2 else 1, 'k')
    if t % 2 == 0:
        L.rect(px + 30, y + 5, 1, 1, 'k'); L.rect(px + 30, y + 16, 1, 1, 'k')
    L.line(px + 14, y + 13, px + 12, y + 16, 'k'); L.line(px + 21, y + 13, px + 23, y + 16, 'k')
    L.rect(px + 11, y + 16, 2, 2, 'k'); L.rect(px + 22, y + 16, 2, 2, 'k')
    sc = t % 2
    L.rect(px + 3, y + 5 + sc, 4, 1, 'W'); L.rect(px + 1, y + 6 - sc, 3, 1, 'W')
    f.blit(L)


def teacher_chalk(f, t, n):
    """Teacher writes 1+1=2 on the chalkboard, taps it proudly, then wipes it."""
    k = t % 20
    f.rect(0, 9, 27, 21, 'N'); f.rect(1, 10, 25, 19, 'e'); f.rect(0, 30, 27, 1, 'n')
    txt = '1+1=2'
    shown = min(5, (k + 1) // 2) if k < 10 else 5
    f.text(txt[:shown], 4, 17, 'W')
    erase = 16 <= k <= 19
    if erase:
        ex = 2 + (k - 16) * 7
        f.rect(1, 10, min(25, ex + 4) - 1, 19, 'e')
        for yy in range(12, 27, 3):
            f.rect(2, yy, max(0, ex - 1), 1, 'E')
        f.rect(ex, 16, 5, 4, 'N'); f.rect(ex, 16, 5, 1, 'T')
    if k >= 13 and not erase:
        P.check(f, 18, 23)
    writing = k < 10
    turned = 10 <= k <= 15
    info = clawd(f, x=23, view='front' if turned else 'ql', la='high',
                 ra='up' if k in (11, 12) else 'side', eyes='happy' if turned else 'focus')
    x, y = info['x'], info['y']
    hx, hy = info['lh']
    if writing:
        wx = 4 + shown * 4
        wy = 19 + (k % 2)
        f.line(hx, hy, wx + 1, wy, 'N')
        f.rect(wx, wy - 1, 2, 2, 'W')
    elif erase:
        f.line(hx, hy, ex + 4, 18, 'N')
    elif turned:
        f.line(hx, hy, 17, 19, 'N'); f.put(17, 19, 'W')


def lumberjack_chop(f, t, n):
    """Plaid shirt and beanie: one big axe swing splits the log."""
    k = t % 12
    f.rect(24, 34, 15, 2, 'n')
    if k < 5 or k == 11:
        f.rect(27, 26, 9, 8, 'N'); f.rect(27, 26, 9, 2, 'T'); f.rect(29, 26, 5, 1, 'y'); f.put(31, 27, 'N')
        f.rect(28, 29, 1, 4, 'n'); f.rect(33, 30, 1, 3, 'n')
    else:
        j = min(k - 5, 3)
        f.rect(27 - j, 26 + j, 4, 8 - j, 'N'); f.rect(27 - j, 26 + j, 4, 1, 'T')
        f.rect(32 + j, 26 + j, 4, 8 - j, 'N'); f.rect(32 + j, 26 + j, 4, 1, 'T')
        f.rect(31 - j, 27 + j, 1, 7 - j, 'y'); f.rect(32 + j, 27 + j, 1, 7 - j, 'y')
    pose = ['high', 'up', 'up', 'mid', 'out', 'out', 'out', 'side', 'side', 'side', 'side', 'side'][k]
    info = clawd(f, x=6, view='qr', ra=pose, la='side', eyes='angry' if k < 5 else 'happy' if k >= 7 else 'closed',
                 tilt=1 if k in (1, 2) else 0)
    x, y = info['x'], info['y']
    P.hat(f, info, 'beanie')
    hx, hy = info['rh']
    heads = {0: (x + 20, y - 4), 1: (x + 12, y - 9), 2: (x + 12, y - 9), 3: (x + 26, y - 4), 4: (30, 24),
             5: (31, 25), 6: (31, 25)}
    if k in heads:
        ax, ay = heads[k]
        f.line(hx, hy, ax, ay, 'N')
        f.rect(ax - 1, ay - 2, 3, 4, 'g'); f.rect(ax + (1 if ax > hx else -1), ay - 2, 1, 4, 'G')
    else:
        f.line(x + 2, 35, x + 9, 31, 'N'); f.rect(x + 1, 33, 3, 3, 'g')
    if 4 <= k <= 7:
        r = rng(k)
        for i in range(4):
            f.rect(31 + r.randint(-6, 6), 24 - (k - 3) * 2 - r.randint(0, 3), 2, 1, 'y' if i % 2 else 'N')
        if k == 4:
            f.art(['U.U', '.W.', 'U.U'], 33, 21)


def miner_lamp(f, t, n):
    """Head-lamp sweeps the dark mine, finds a gem; pick swing, gem held high."""
    k = t % 16
    # rock wall and ceiling
    f.rect(0, 0, 40, 3, 'g'); f.art(['ggg', '.g.', '.g.'], 8, 3); f.art(['gg', 'g.'], 22, 3)
    f.rect(31, 10, 9, 27, 'g'); f.rect(29, 16, 2, 20, 'g'); f.rect(31, 10, 9, 1, 'G'); f.rect(29, 16, 2, 1, 'G')
    f.put(34, 14, 'k'); f.put(35, 15, 'k'); f.put(33, 30, 'k'); f.put(37, 28, 'k')
    gem_in = k < 12
    hit = 8 <= k <= 11
    if gem_in:
        f.art(['.CC.', 'CWCC', '.CC.'], 32, 21)
    f.rect(0, 36, 40, 1, 'g')
    look = 'ql' if k < 4 else 'qr'
    info = clawd(f, x=8, view=look, ra='up' if k >= 12 else 'high' if hit and k % 2 == 0 else 'out' if hit else 'side',
                 eyes='big' if 6 <= k <= 7 else 'happy' if k >= 12 else 'focus', tilt=1 if k >= 12 else 0)
    x, y = info['x'], info['y']
    hat_art(f, info, ['....gggggggg....', '..gGGGGGGGGGGg..', '.gGGGGGGGGGGGGg.', 'gggggggggggggggg'])
    lx, ly = x + 8, y - 3
    f.rect(lx - 1, ly - 1, 3, 2, 'U'); f.put(lx, ly - 1, 'W')
    ang = {0: 3.4, 1: 3.5, 2: 3.3, 3: 3.2, 4: 4.5, 5: 5.4, 6: 5.75, 7: 5.75}.get(k, 5.75 if k < 12 else None)
    if ang is not None:
        for yy in range(40):
            for xx in range(40):
                dx, dy = xx + .5 - lx, yy + .5 - ly
                d = math.hypot(dx, dy)
                if 3 < d < 24 and (xx + yy) % 2 == 0:
                    a = math.atan2(dy, dx) % (2 * math.pi)
                    if abs((a - ang + math.pi) % (2 * math.pi) - math.pi) < .28 and f.get(xx, yy) is None:
                        f.put(xx, yy, 'y')
    hx, hy = info['rh']
    if hit:
        tip = (31, 21) if k % 2 else (int(hx) + 3, int(hy) - 7)
        f.line(hx, hy, tip[0] - 2, tip[1] + 2, 'N')
        f.line(tip[0] - 4, tip[1] - 1, tip[0], tip[1] + 3, 'G')
        if k % 2:
            f.art(['U.U', '.W.', 'U.U'], 28, 18)
            f.rect(30, 26, 1, 1, 'G'); f.rect(28, 28, 1, 1, 'g')
    elif k >= 12:
        f.art(['.CC.', 'CWCC', 'CCCC', '.CC.'], int(hx) - 1, int(hy) - 5)
        P.sparkles(f, k, 4, [(int(hx) - 4, int(hy) - 7), (int(hx) + 5, int(hy) - 5), (int(hx), int(hy) - 10)])
    if 6 <= k <= 7:
        f.art(P.EXCL, x + 4, y - 11, cmap={'K': 'U'})


# --------------------------------------------------------------------------- register 51-60
add('cos_jester_ball', '小丑踩球', 'Jester on a ball', jester_ball, n=16, dur=100)
add('cos_princess_twirl', '公主转圈', 'Princess gown twirl', princess_twirl, n=12, dur=110)
add('cos_archer_bullseye', '弓箭手正中靶心', 'Archer bullseye', archer_bullseye, n=16, dur=100)
add('cos_ringmaster_hoop', '马戏团钻火圈', 'Ringmaster hoop jump', ringmaster_hoop, n=16, dur=110)
add('cos_genie_lamp', '神灯精灵', 'Genie from the lamp', genie_lamp, n=20, dur=120)
add('cos_dragon_fire', '小龙喷火', 'Dragon costume fire', dragon_fire, n=12, dur=110)
add('cos_pilot_banner', '飞行员拉横幅', 'Pilot towing a banner', pilot_banner, n=24, dur=80)
add('cos_teacher_chalk', '老师写黑板', 'Teacher at the chalkboard', teacher_chalk, n=20, dur=140)
add('cos_lumberjack_chop', '伐木工劈柴', 'Lumberjack log split', lumberjack_chop, n=12, dur=110)
add_tweened('cos_miner_lamp', '矿工寻宝石', 'Miner finds a gem', miner_lamp, n=16, dur=130, tw_at={11: 1, 15: 1})
