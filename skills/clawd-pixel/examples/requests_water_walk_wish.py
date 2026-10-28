"""Three Clawd GIFs:
  water_bloom  - waters a sprout, it grows and blooms
  walk_wave    - walks in side-on, stops, turns to the viewer and waves, walks off
  star_wish    - night, gazes up at the stars, a shooting star passes, makes a wish
"""
import math
from engine import add, clawd, Canvas, Dotted, BX, BY, GROUND, pick, rng
import props as P

# =========================================================================== 1) water -> grow -> bloom
CAN_UP = """
.BBB......
B...B.....
CCCCC....B
CCCCC...C.
CCCCCCCC..
CCCCC.....
"""
CAN_TIP = """
.BBB........
B...B.......
CCCCCC......
CCCCCC......
CCCCCCCC....
.CCCCC.CC...
.........C..
..........B.
"""
TIP_ROSE = (10, 7)             # rose (spout tip) inside CAN_TIP
POT = """
NnnnnnnnN
.NNNNNNN.
.NNNNNNN.
..NNNNN..
"""
POT_X, POT_Y = 30, 32          # pot top-left; rim row 32, bottom row 35 (feet row)
STEM_X = POT_X + 4             # stem column (pot centre)
SOIL = POT_Y - 1               # first stem row

# stage -> (stem height, leaf-pair heights, top)
STAGES = [
    (1, [], 'tip'),            # 0 tiny sprout
    (2, [], 'tip'),            # 1
    (3, [1], 'tip'),           # 2 first leaves
    (4, [1], 'tip'),           # 3
    (5, [1, 3], 'tip'),        # 4 second leaves
    (5, [1, 3], 'bud'),        # 5 bud
    (5, [1, 3], 'flower'),     # 6 bloom
]


def plant(f, stage, sway=0):
    h, leaves, top = STAGES[stage]
    cx = STEM_X
    for i in range(h):
        # the top half of the stem leans with the sway
        f.put(cx + (sway if i >= h // 2 + 1 else 0), SOIL - i, 'e')
    for lh in leaves:
        y = SOIL - lh
        big = lh == 1 and h >= 4
        if big:
            f.art(['E..', 'EEE'], cx - 3, y - 1)
            f.art(['..E', 'EEE'], cx + 1, y - 1)
        else:
            f.art(['E.', 'EE'], cx - 2, y - 1)
            f.art(['.E', 'EE'], cx + 1, y - 1)
    ty = SOIL - h            # row just above the stem
    tx = cx + sway
    if top == 'tip':
        f.art(['E.E'], tx - 1, ty)
    elif top == 'bud':
        f.art(['.Z.', 'EZE'], tx - 1, ty - 1)
    elif top == 'flower':
        f.art(['.Z.Z.', 'ZZUZZ', '.ZZZ.'], tx - 2, ty - 2)


def water(f, x, y0, y1, k):
    """Shower from the rose (x, y0) down to the soil row y1, two drop columns in a twinkling
    checker; k = frames since pouring began (the stream reaches the soil after a frame)."""
    end = min(y1, y0 + 2 + 2 * k)
    for yy in range(y0 + 1, end + 1):
        f.put(x + (yy + k) % 2, yy, 'B')
    if end == y1 and k % 2 == 0:                                    # splash
        f.put(x - 1, y1, 'S'); f.put(x + 2, y1, 'S')


def water_bloom(f, t, n):
    k = t % n
    x0 = 4                     # body left; far arm reaches col 0
    stage = [0, 0, 0, 0, 0, 1, 2, 3, 3, 4, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6][k]
    pour = 2 <= k <= 7
    pose = dict(x=x0, view='qr', ra='high' if pour else 'mid', eyes='normal', lookv=1)
    if k >= 9:
        pose.update(ra='low')                                       # can set down, watching
    if k in (9, 10, 11):
        pose.update(eyes='big', lookv=1)                            # "it's growing!"
    if k == 12:
        pose.update(eyes='big', lookv=0, y=BY - 1)                  # bloom pop: tiny start
    if 13 <= k <= 16:
        up = k in (13, 15)
        pose.update(eyes='happy', lookv=0, tilt=1, la='up' if up else 'side',
                    y=BY - (1 if up else 0))
    if k == 18:
        pose.update(eyes='blink')
    if k >= 17:
        pose.update(lookv=1)
    info = clawd(f, **pose)
    hx, hy = int(info['rh'][0]), int(info['rh'][1])
    if pour:                   # arm lifted, can tipped, shower on the soil
        f.art(CAN_TIP, hx, hy - 3)
        water(f, hx + TIP_ROSE[0], hy - 3 + TIP_ROSE[1], SOIL, k - 2)
    elif k >= 9:               # can stands on the ground by the front foot, nub on the handle
        f.art(CAN_UP, hx - 2, GROUND - 6)
    else:
        f.art(CAN_UP, hx, hy - 3)
        if k == 8:             # last drip landing after the can comes upright
            f.put(31, SOIL, 'B')
    sway = 1 if k in (4, 11, 17) else 0
    plant(f, stage, sway)
    f.art(POT, POT_X, POT_Y)
    # bloom: sparkle burst, then a calm twinkle
    fx, fy = STEM_X, SOIL - 7
    if k == 12:
        for dx, dy in ((-5, -2), (5, -2), (0, -6), (-4, 3), (4, 3)):
            f.art(P.SPARK, fx + dx - 1, fy + dy)
    elif 13 <= k <= 16:
        P.sparkles(f, k, n, [(fx - 5, fy - 1), (fx + 4, fy - 3), (fx, fy - 5)])


# per-frame timing: calm start, quicker pour, a beat on the bloom, slow settle
WATER_DUR = [220, 200, 150, 130, 130, 130, 130, 130, 180, 170, 170, 200,
             110, 150, 150, 150, 150, 200, 160, 320]
add('water_bloom', '浇水开花', 'Watering a sprout until it blooms', water_bloom, n=20, dur=WATER_DUR)


# =========================================================================== 2) walk in, turn, wave
WALK_IN = 10                   # x = -15 .. 12, 3 px a frame
WALK_OUT = 9                   # x = 15 .. 39, then the loop re-enters on the left


def walk_wave(f, t, n):
    k = t % n
    if k < WALK_IN:            # walk in, strong 3/4 facing the travel direction
        s = k % 2
        clawd(f, x=-15 + 3 * k, y=BY + s, view='q2r',
              legs=(1, 0, 1, 0) if s else (0, 1, 0, 1), eyes='blink' if k == 5 else 'normal')
        return
    j = k - WALK_IN
    # stop-settle, turn q2r -> qr -> front, wave x3, arm down, turn back
    beats = ['settle', 'qr', 'front', 'w_up', 'w_wave', 'w_up', 'w_wave', 'w_up', 'w_wave',
             'done', 'qr_out']
    if j < len(beats):
        b = beats[j]
        if b == 'settle':
            clawd(f, x=BX, y=BY + 1, h=11, view='q2r')
        elif b == 'qr':
            clawd(f, x=BX, view='qr', eyes='normal')
        elif b == 'front':
            clawd(f, x=BX, view='front', eyes='big')
        elif b.startswith('w_'):
            up = b == 'w_up'
            clawd(f, x=BX, view='front', eyes='happy', blush=True,
                  ra='up' if up else 'wave', y=BY + (0 if up else 1), h=12 - (0 if up else 1))
        elif b == 'done':
            clawd(f, x=BX, view='front', eyes='happy', blush=True)
        elif b == 'qr_out':
            clawd(f, x=BX, view='qr', eyes='normal')
        return
    m = j - len(beats)         # walk off to the right
    s = m % 2
    clawd(f, x=BX + 3 * (m + 1), y=BY + s, view='q2r',
          legs=(1, 0, 1, 0) if s else (0, 1, 0, 1))


WALK_N = WALK_IN + 11 + WALK_OUT
WALK_DUR = ([100] * WALK_IN + [200, 130, 220] + [170] * 6 + [260, 130] + [100] * WALK_OUT)
add('walk_wave', '走进来挥手', 'Walk in, turn and wave', walk_wave, n=WALK_N, dur=WALK_DUR)


# =========================================================================== 3) night: shooting star wish
STARS = [(3, 15), (11, 4), (17, 11), (25, 2), (29, 9), (36, 4), (34, 16), (21, 18), (4, 19), (38, 23)]
METEOR = [(13, 1), (20, 4), (27, 7), (34, 10), (41, 13)]     # head position per frame


def night_room():
    d = Dotted(dark=True)
    d.line(0, 36, 40, 36)
    # a soft hill on the right and a few grass tufts, line-art only
    pts = [(24, 36), (27, 34), (31, 32.5), (35, 32), (40, 32.5)]
    for (a, b), (c, e) in zip(pts, pts[1:]):
        d.line(a, b, c, e)
    for gx in (2, 26, 33):
        d.line(gx, 36, gx - 0.6, 34.8); d.line(gx + 0.6, 36, gx + 1.2, 34.8)
    return d


def sky(f, t):
    P.moon(f, 2, 2)
    for i, (x, y) in enumerate(STARS):
        k = (t + i * 3) % 6
        if k == 0:
            f.art(['.y.', 'yWy', '.y.'], x - 1, y - 1)
        elif k == 3:
            f.put(x, y, 'g')
        else:
            f.put(x, y, 'w' if i % 2 else 'y')


def wish_bubble(f, x, y, w, h, c='B'):
    """Rounded thought bubble (2-px corner rounding) with two puffs trailing down-left."""
    f.rect(x + 2, y, w - 4, h, c)
    f.rect(x + 1, y + 1, w - 2, h - 2, c)
    f.rect(x, y + 2, w, h - 4, c)
    f.rect(x + 1, y + h + 1, 2, 2, c)
    f.put(x - 1, y + h + 4, c)


def meteor(f, j):
    """j = 0..4 frames into the streak; the tail gets longer, then fades."""
    hx, hy = METEOR[j]
    tail = [3, 6, 8, 8, 5][j]
    for i in range(tail, 0, -1):
        c = 'U' if i <= 2 else 'y' if i <= 5 else 'g'
        f.put(hx - round(i * 2.33), hy - i, c)
    f.rect(hx - 1, hy - 1, 2, 2, 'W')


def star_wish(f, t, n):
    k = t % n
    sky(f, k)
    if 6 <= k <= 10:
        meteor(f, k - 6)
    x0 = 6
    sit = dict(x=x0, y=BY + 2, leg_h=1)        # sitting on the ground
    if k < 6 or k >= 21:                        # gazing up: turned, tilted, eyes up
        e = 'blink' if k == 3 else 'happy' if k == 21 else 'normal'
        info = clawd(f, view='qr', tilt=1, lookv=-1, eyes=e, **sit)
    elif k <= 9:                                # follows the streak
        info = clawd(f, view='qr', tilt=1, lookv=-1 if k < 8 else 0, eyes='big' if k >= 7 else 'normal',
                     look=1 if k >= 8 else 0, **sit)
    elif k == 10:                               # gasp: perks up (stretch 1 px), '!'
        info = clawd(f, view='qr', tilt=1, eyes='big', x=x0, y=BY + 1, h=13, leg_h=1)
        cx, top = info['head']
        f.art(P.EXCL, int(cx) + 5, int(top) - 8, cmap={'K': 'U'})
    elif k == 11:                               # turn to the viewer
        info = clawd(f, view='front', eyes='big', **sit)
    elif k <= 19:                               # wish: head bowed (top face), eyes shut, arms down
        info = clawd(f, view='front', eyes='closed', top=True, x=x0, y=BY + 3, h=11, leg_h=1,
                     la='low', ra='low', lookv=1)
        cx, top = info['head']
        j = k - 12
        bx, by, bw, bh = int(cx) + 3, int(top) - 15, 11, 9
        if j == 1:                              # bubble starts as puffs
            f.put(bx - 1, by + bh + 4, 'B'); f.rect(bx + 1, by + bh + 1, 2, 2, 'B')
        elif 2 <= j <= 6:                       # thought bubble with the wished-for star
            wish_bubble(f, bx, by, bw, bh)
            f.art(P.STAR5 if j % 2 == 0 else ['..W..', '.UUU.', 'UUWUU', '.UUU.', 'U...U'],
                  bx + 3, by + 2)
        elif j == 7:                            # the wish floats off to the sky as sparkles
            for dx, dy in ((2, 0), (6, -3), (9, 2), (5, 5)):
                f.art(P.SPARK, bx + dx - 1, by + dy - 1)
    else:                                       # k == 20: eyes open, happy
        info = clawd(f, view='front', eyes='happy', **sit)


STAR_DUR = [200] * 6 + [90, 90, 90, 90] + [260, 160] + [200] * 8 + [200, 180, 200, 200]
add('star_wish', '流星许愿', 'Wishing on a shooting star', star_wish, n=24, dur=STAR_DUR,
    backdrop=night_room())
