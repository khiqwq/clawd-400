"""Actions (body motion) + a generic compositor that layers hats, items and effects."""
import math
from engine import (Canvas, G, GROUND, BX, BY, clawd, mini, sin, cos, ph, pick, tri, rng,
                    text_w)
import props as P

# --------------------------------------------------------------------------- actions
# Each action returns (pose, tf): pose = kwargs for clawd(), tf = optional layer transform.


def _blink(o, t, n, at=None):
    e = o.get('eyes', 'normal')
    at = n - 3 if at is None else at
    if e in ('normal', 'big') and t == at and not o.get('noblink'):
        return 'blink'
    return e


def a_still(t, n, o):
    return dict(eyes=_blink(o, t, n)), None


def a_idle(t, n, o):
    b = 1 if sin(t, n) < -0.5 else 0
    return dict(y=BY + b, h=12 - b, eyes=_blink(o, t, n)), None


def a_bob(t, n, o):
    b = (t // 2) % 2
    return dict(y=BY + b, h=12 - b, eyes=_blink(o, t, n)), None


def a_hop(t, n, o):
    dy = [0, -2, -4, -5, -5, -4, -2, 0][int(8 * t / n) % 8]
    p = dict(y=BY + dy, eyes=o.get('eyes', 'happy'))
    if dy == 0 and t % n == 0:
        p.update(x=BX - 1, w=18, h=11, y=BY + 1)
    if dy <= -4:
        p['legs'] = (1, 1, 1, 1)
    return p, None


def a_jump(t, n, o):
    seq = [(0, 'sq'), (-3, ''), (-7, ''), (-9, 'up'), (-10, 'up'), (-9, 'up'), (-7, ''), (-3, ''), (0, 'sq'), (0, '')]
    dy, k = seq[int(len(seq) * t / n) % len(seq)]
    p = dict(y=BY + dy, eyes=o.get('eyes', 'happy' if k == 'up' else 'normal'))
    if k == 'sq':
        p.update(x=BX - 1, w=18, h=10, y=BY + 2, eyes='closed')
    if k == 'up':
        p.update(la='up', ra='up', legs=(1, 1, 1, 1), h=13, y=BY + dy - 1)
    return p, None


def a_walk(t, n, o):
    s = t % 2
    return dict(y=BY + s, legs=(1, 0, 1, 0) if s else (0, 1, 0, 1), eyes=_blink(o, t, n),
                view=o.get('view', 'front')), None


def _across(t, n, o, d):
    span = 64
    x = -20 + int(span * t / n) if d > 0 else 44 - int(span * t / n)
    s = (t // 2) % 2
    return dict(x=x, y=BY + s, legs=(1, 0, 1, 0) if s else (0, 1, 0, 1),
                view='qr' if d > 0 else 'ql', eyes=o.get('eyes', 'normal')), None


def a_walkr(t, n, o):
    return _across(t, n, o, 1)


def a_walkl(t, n, o):
    return _across(t, n, o, -1)


def a_scuttle(t, n, o):
    dx = int(round(6 * math.sin(2 * math.pi * t / n)))
    s = t % 2
    return dict(x=BX + dx, legs=(1, 0, 1, 0) if s else (0, 1, 0, 1), legdx=(s, -s, s, -s),
                eyes=o.get('eyes', 'normal'), look=1 if math.cos(2 * math.pi * t / n) > 0 else -1), None


def a_run(t, n, o):
    s = t % 2
    p = dict(y=BY + s - 1, legs=(2, 0, 2, 0) if s else (0, 2, 0, 2), legdx=(1, -1, 1, -1) if s else (-1, 1, -1, 1),
             view='qr', eyes=o.get('eyes', 'focus'), la='low', ra='high' if s else 'low')
    return p, (lambda L: L.shear(-0.08, 36))


def a_wave(t, n, o):
    s = (t // 2) % 2
    return dict(ra='up' if s else 'wave', eyes=o.get('eyes', 'happy'), y=BY), None


def a_wave2(t, n, o):
    s = (t // 2) % 2
    return dict(ra='up' if s else 'wave', la='wave' if s else 'up', eyes=o.get('eyes', 'happy')), None


def a_cheer(t, n, o):
    s = (t // 2) % 2
    return dict(la='up' if s else 'high', ra='up' if s else 'high', y=BY - 2 * s,
                legs=(1, 1, 1, 1) if s else (0, 0, 0, 0), eyes=o.get('eyes', 'happy' if s else 'closed')), None


def a_dance(t, n, o):
    k = t % 4
    dx = [0, 1, 0, -1][k]
    return dict(x=BX + dx, la='up' if k in (0, 1) else 'side', ra='side' if k in (0, 1) else 'up',
                legs=(1, 0, 0, 1) if k % 2 else (0, 1, 1, 0), y=BY + (k % 2), eyes=o.get('eyes', 'happy')), None


def a_groove(t, n, o):
    s = t % 2
    return dict(y=BY + s, h=12 - s, la='high' if s else 'side', ra='side' if s else 'high',
                eyes=o.get('eyes', 'closed')), None


SPIN = ['front', 'qr', 'sr', 'back', 'sl', 'ql']


def a_spin(t, n, o):
    v = SPIN[int(len(SPIN) * t / n) % len(SPIN)]
    return dict(view=v, eyes=o.get('eyes', 'normal'), y=BY - (1 if v in ('sr', 'sl') else 0)), None


def a_shake(t, n, o):
    return dict(x=BX + (1 if t % 2 else -1), eyes=o.get('eyes', 'squint')), None


def a_tremble(t, n, o):
    r = rng(t)
    return dict(x=BX + r.choice((-1, 0, 1)), y=BY + r.choice((0, 0, 1)), eyes=o.get('eyes', 'worried'),
                la='low', ra='low'), None


def a_nod(t, n, o):
    s = (t // 2) % 2
    return dict(y=BY + s, h=12 - s, top=bool(s), lookv=1 if s else 0, eyes=o.get('eyes', 'happy')), None


def a_no(t, n, o):
    k = (t // 2) % 4
    v = ['ql', 'front', 'qr', 'front'][k]
    return dict(view=v, eyes=o.get('eyes', 'closed')), None


def a_look(t, n, o):
    k = int(8 * t / n) % 8
    look = [0, -1, -1, -1, 0, 1, 1, 1][k]
    v = ['front', 'ql', 'ql', 'front', 'front', 'qr', 'qr', 'front'][k]
    return dict(view=v, look=0, eyes=o.get('eyes', 'normal')), None


def a_sleep(t, n, o):
    b = 1 if sin(t, n) < 0 else 0
    return dict(y=BY + 2 + b, h=12 - b, leg_h=1, eyes='closed', la='low', ra='low'), None


def a_sit(t, n, o):
    return dict(y=BY + 2, leg_h=1, eyes=_blink(o, t, n), la=o.get('la', 'side'), ra=o.get('ra', 'side')), None


def a_stretch(t, n, o):
    k = [0, 1, 2, 3, 3, 3, 2, 1][int(8 * t / n) % 8]
    return dict(y=BY - k, h=12 + k, w=16 - (k > 2), x=BX, la='up' if k else 'side', ra='up' if k else 'side',
                eyes='closed' if k >= 2 else 'normal'), None


def a_jelly(t, n, o):
    seq = [(16, 12), (18, 11), (19, 10), (18, 11), (16, 12), (14, 13), (13, 14), (14, 13)]
    w, h = seq[int(len(seq) * t / n) % len(seq)]
    return dict(w=w, h=h, x=20 - w // 2, y=BY + 12 - h, eyes=o.get('eyes', 'happy')), None


def a_lean(t, n, o):
    k = sin(t, n) * 0.12
    return dict(eyes=o.get('eyes', 'closed'), look=1 if k > 0 else -1), (lambda L, k=k: L.shear(k, 36))


def a_float(t, n, o):
    dy = int(round(2 * sin(t, n))) - 4
    s = t % 2
    return dict(y=BY + dy, legs=(1, 0, 1, 0) if s else (0, 1, 0, 1), eyes=o.get('eyes', 'happy'),
                la='high', ra='high'), None


def a_bounce(t, n, o):
    p = ph(t, n)
    hgt = 4 * p * (1 - p)
    dy = -int(round(hgt * 12))
    pose = dict(y=BY + dy, eyes=o.get('eyes', 'happy'), legs=(1, 1, 1, 1) if dy < -3 else (0, 0, 0, 0))
    if t % n == 0:
        pose.update(x=BX - 2, w=20, h=9, y=BY + 3, eyes='closed')
    elif dy < -8:
        pose.update(x=BX + 1, w=14, h=13, y=BY + dy - 1)
    return pose, None


def a_flip(t, n, o):
    seq = [(0, 0, 'sq'), (-5, 0, ''), (-9, 1, ''), (-11, 2, ''), (-9, 3, ''), (-5, 0, ''), (0, 0, 'sq'), (0, 0, '')]
    dy, k, s = seq[int(len(seq) * t / n) % len(seq)]
    pose = dict(y=BY + dy, eyes=o.get('eyes', 'squint' if k else 'happy'), la='up' if s == '' and dy < 0 else 'side',
                ra='up' if s == '' and dy < 0 else 'side')
    if s == 'sq':
        pose.update(x=BX - 1, w=18, h=10, y=BY + 2, eyes='closed')
    return pose, (lambda L, k=k, dy=dy: L.rot90(-k, 20, BY + dy + 7))


def a_roll(t, n, o):
    k = t % 4
    x = -20 + int(64 * t / n)
    return dict(x=x, y=BY + 1, eyes='x' if k == 2 else 'squint'), (lambda L, k=k, x=x: L.rot90(k, x + 8, BY + 8))


def a_stomp(t, n, o):
    s = (t // 2) % 2
    return dict(x=BX + (t % 2), legs=(2, 0, 2, 0) if s else (0, 2, 0, 2), eyes='angry',
                la='low', ra='low', y=BY + (t % 2)), None


def a_bow(t, n, o):
    k = [0, 1, 2, 2, 2, 1, 0, 0][int(8 * t / n) % 8]
    return dict(y=BY + k, h=12 - k, top=k > 0, lookv=k, eyes='closed' if k else o.get('eyes', 'happy'),
                la='front' if k else 'side', ra='front' if k else 'side'), None


def a_clap(t, n, o):
    s = t % 2
    return dict(la='high' if s else 'side', ra='high' if s else 'side', eyes=o.get('eyes', 'happy'),
                y=BY - s), None


def a_shrug(t, n, o):
    k = [0, 1, 1, 1, 1, 0, 0, 0][int(8 * t / n) % 8]
    return dict(la='high' if k else 'side', ra='high' if k else 'side', y=BY - k,
                eyes=o.get('eyes', 'closed') if k else 'normal'), None


def a_peek(t, n, o):
    k = [14, 10, 6, 3, 2, 2, 2, 2, 2, 2, 3, 6, 10, 14, 16, 16][int(16 * t / n) % 16]
    look = [0, 0, 0, 0, 0, -1, -1, 1, 1, 0, 0, 0, 0, 0, 0, 0][int(16 * t / n) % 16]
    return dict(y=BY + k, look=look, eyes=o.get('eyes', 'normal')), None


def a_pop(t, n, o):
    """Pop in without scaling Clawd: blank, mini Clawd, stretch, squash, settle."""
    k = int(12 * t / n) % 12
    if k == 0:
        return dict(), (lambda L: Canvas())
    if k == 1:
        def _mini(L):
            M = Canvas(); mini(M, 16, 28, eyes='big'); return M
        return dict(), _mini
    if k == 2:
        return dict(x=BX + 1, w=14, h=15, y=BY - 3, la='up', ra='up', eyes='big'), None
    if k == 3:
        return dict(x=BX - 1, w=18, h=10, y=BY + 2, eyes='closed'), None
    return dict(eyes=_blink(o, t, n, at=9) if 'eyes' not in o else o['eyes']), None


def a_pace(t, n, o):
    half = n // 2
    if t < half:
        x = 4 + int(16 * t / half); v = 'qr'
    else:
        x = 20 - int(16 * (t - half) / half); v = 'ql'
    s = t % 2
    return dict(x=x, view=v, legs=(1, 0, 1, 0) if s else (0, 1, 0, 1), y=BY + s,
                eyes=o.get('eyes', 'normal'), la='front', ra='front'), None


def a_zoomies(t, n, o):
    x = -20 + int(64 * t / n)
    s = t % 2
    return dict(x=x, y=BY - 1 + s, view='qr', legs=(2, 0, 2, 0) if s else (0, 2, 0, 2), eyes='happy',
                la='low', ra='low'), (lambda L: L.shear(-0.1, 36))


def a_wobble(t, n, o):
    k = [-1, 0, 1, 0][t % 4]
    return dict(eyes=o.get('eyes', 'x')), (lambda L, k=k: L.rotate(k * 8, 20, 36))


def a_sway(t, n, o):
    deg = 7 * sin(t, n)
    return dict(eyes=o.get('eyes', 'closed'), la='high', ra='high'), (lambda L, d=deg: L.rotate(d, 20, 36))


def a_salute(t, n, o):
    k = 1 if 2 <= int(8 * t / n) % 8 <= 6 else 0
    return dict(ra='wave' if k else 'side', eyes='focus' if k else 'normal', view='front'), None


def a_point(t, n, o):
    k = (t // 2) % 2
    return dict(ra='out', eyes=o.get('eyes', 'focus'), view='qr', x=BX - 2 + k), None


def a_hide(t, n, o):
    k = int(8 * t / n) % 8
    pose = dict(la='face', ra='face', eyes='normal', y=BY + 1)
    if k in (3, 4):
        pose.update(ra='side', look=1)
    return pose, None


def a_type(t, n, o):
    s = t % 2
    return dict(la='front' if s else 'side', ra='side' if s else 'front', eyes=o.get('eyes', 'focus'),
                y=BY + (1 if t % 4 == 0 else 0)), None


def a_lift(t, n, o):
    k = [0, 1, 2, 2, 1, 0][int(6 * t / n) % 6]
    arm = ['low', 'side', 'up'][k]
    return dict(la=arm, ra=arm, eyes='angry' if k < 2 else 'squint', y=BY + (1 if k == 2 else 0)), None


def a_swim(t, n, o):
    s = (t // 2) % 2
    return dict(y=BY + 3 + s, la='high' if s else 'low', ra='low' if s else 'high', eyes=o.get('eyes', 'happy'),
                leg_h=0), None


def a_faint(t, n, o):
    k = int(10 * t / n) % 10
    if k < 2:
        return dict(eyes='x'), (lambda L, k=k: L.rotate(10 * k, 20, 36))
    if k < 3:
        return dict(eyes='x'), (lambda L: L.rotate(45, 20, 36))
    return dict(eyes='x'), (lambda L: L.rot90(1, 20, 23).shift(7, 0))


def a_moonwalk(t, n, o):
    x = 28 - int(32 * t / n)
    s = t % 2
    return dict(x=x, view='qr', legs=(0, 1, 0, 1) if s else (1, 0, 1, 0), legdx=(-1, 0, -1, 0) if s else (0, -1, 0, -1),
                eyes=o.get('eyes', 'closed'), la='low', ra='high' if s else 'low'), None


def a_tiptoe(t, n, o):
    x = -16 + int(56 * t / n)
    s = (t // 2) % 2
    return dict(x=x, y=BY - 1 - s, view='qr', legs=(0, 1, 0, 1) if s else (1, 0, 1, 0), eyes='blink',
                la='high', ra='high'), None


ACTIONS = {k[2:]: v for k, v in globals().items() if k.startswith('a_')}
ACT_DEFAULT = {  # natural (frames, ms per frame)
    'still': (8, 180), 'idle': (8, 180), 'bob': (8, 160), 'hop': (8, 90), 'jump': (10, 90), 'walk': (8, 140),
    'walkr': (32, 80), 'walkl': (32, 80), 'scuttle': (16, 80), 'run': (6, 70), 'wave': (8, 150),
    'wave2': (8, 150), 'cheer': (8, 140), 'dance': (8, 150), 'groove': (8, 160), 'spin': (12, 100),
    'shake': (6, 70), 'tremble': (8, 70), 'nod': (8, 160), 'no': (8, 140), 'look': (16, 160), 'sleep': (12, 220),
    'sit': (8, 200), 'stretch': (12, 140), 'jelly': (8, 100), 'lean': (12, 120), 'float': (12, 140),
    'bounce': (12, 70), 'flip': (8, 90), 'roll': (16, 80), 'stomp': (8, 90), 'bow': (12, 140), 'clap': (6, 120),
    'shrug': (10, 140), 'peek': (24, 120), 'pop': (12, 90), 'pace': (24, 110), 'zoomies': (16, 60),
    'wobble': (8, 110), 'sway': (16, 110), 'salute': (10, 150), 'point': (8, 160), 'hide': (16, 150),
    'type': (6, 90), 'lift': (12, 120), 'swim': (8, 150), 'faint': (12, 140), 'moonwalk': (16, 110),
    'tiptoe': (28, 110),
}


# --------------------------------------------------------------------------- effects
def _head(info):
    return info['head']


def fx_zzz(f, t, n, i, o): P.zzz(f, i, t, n, c=o.get('fxc', 'B'))
def fx_notes(f, t, n, i, o): P.notes(f, i, t, n, c=o.get('fxc', 'K'))
def fx_hearts(f, t, n, i, o):
    cx, top = _head(i)
    P.rising(f, P.HEART, t, n, cx - 1, top - 1, count=3, height=16, jitter=9, seed=4,
             cmap={'Z': o.get('fxc', 'Z')})
def fx_sparkle(f, t, n, i, o):
    x, y, w = i['x'], i['y'], i['w']
    P.sparkles(f, t, n, [(x - 5, y - 2), (x + w + 4, y + 1), (x + w // 2, y - 6), (x - 3, y + 9), (x + w + 3, y + 11)])
def fx_sweat(f, t, n, i, o):
    x, y, w = i['x'], i['y'], i['w']
    k = t % 4
    f.art(P.SWEAT, x + w + 1, y - 1 + k)
def fx_sweat2(f, t, n, i, o):
    x, y, w = i['x'], i['y'], i['w']
    f.art(P.SWEAT, x + w + 1, y - 1 + t % 4)
    f.art(P.SWEAT, x - 3, y + 1 + (t + 2) % 4, flip=True)
def fx_steam(f, t, n, i, o):
    x, y, w = i['x'], i['y'], i['w']
    k = t % 3
    for sx, fl in ((x - 2, True), (x + w, False)):
        f.art([P.PUFF_S, ['.LL', 'LLL', 'LL.'], ['L.L', '.L.', 'L.L']][k], sx - (2 if fl else 0), y - 3 - k * 2)
def fx_vein(f, t, n, i, o):
    x, y, w = i['x'], i['y'], i['w']
    f.art(P.VEIN2 if t % 2 else P.VEIN, x + w - 5, y - 6 + (t % 2))
def fx_dizzy(f, t, n, i, o):
    cx, top = _head(i)
    P.orbit(f, cx, top - 3, 10, 2, t, n, ['.U.', 'UUU', '.U.'], count=3)
def fx_question(f, t, n, i, o):
    cx, top = _head(i)
    k = t % 4
    f.art(P.QMARK, int(cx) + 6, int(top) - 9 - (1 if k < 2 else 0))
    if o.get('two'):
        f.art(P.QMARK, int(cx) - 10, int(top) - 8 - (0 if k < 2 else 1))
def fx_exclaim(f, t, n, i, o):
    cx, top = _head(i)
    if t % 4 != 3:
        f.art(P.EXCL, int(cx) + 6, int(top) - 8 - (t % 2), cmap={'K': o.get('fxc', 'R')})
        f.art(P.EXCL, int(cx) + 8, int(top) - 8 - (t % 2), cmap={'K': o.get('fxc', 'R')}) if o.get('two') else None
def fx_dots(f, t, n, i, o): P.dots_bubble(f, i, t, c=o.get('fxc', 'B'))
def fx_bulb(f, t, n, i, o):
    cx, top = _head(i)
    P.bulb(f, int(cx) - 5, int(top) - 15, t)
def fx_rain(f, t, n, i, o):
    cx, top = _head(i)
    P.cloud(f, int(cx) - 8, int(top) - 14, c='g', w=16)
    P.rain(f, t, n, int(cx) - 6, int(cx) + 6, int(top) - 7, int(top) - 1, c='B')
def fx_sun(f, t, n, i, o): P.sun(f, 33, 6, t)
def fx_snow(f, t, n, i, o): P.falling(f, P.SNOW if False else ['W'], t, n, count=26, seed=8, sway=1.5)
def fx_snowbig(f, t, n, i, o):
    P.falling(f, ['W'], t, n, count=18, seed=8)
    P.falling(f, P.SNOW, t, n, count=6, seed=9, speed=1)
def fx_confetti(f, t, n, i, o): P.confetti(f, t, n)
def fx_fireworks(f, t, n, i, o):
    P.firework(f, 8, 8, ph(t, n), 'Z', 'U')
    P.firework(f, 31, 6, ph(t + n // 2, n), 'C', 'W')
    P.firework(f, 20, 4, ph(t + n // 4, n), 'U', 'Z', r=5)
def fx_bubbles(f, t, n, i, o):
    r = rng(3)
    for k in range(5):
        p = (t / n + k / 5) % 1
        x = 4 + r.randint(0, 30) + math.sin(p * 6 + k) * 2
        y = 38 - p * 40
        P.bubble_ring(f, x, y, 1.5 + (k % 3) * 0.6)
def fx_dust(f, t, n, i, o):
    x, y, w, h = i['x'], i['y'], i['w'], i['h']
    P.dust(f, x - 3, GROUND, ph(t, 4))
def fx_speed(f, t, n, i, o):
    x, y = i['x'], i['y']
    P.speedlines(f, x - 5, y + 1, t)
def fx_shine(f, t, n, i, o):
    """Proud glint: sparkles pop beside Clawd (never painted across his body)."""
    x, y, w = i['x'], i['y'], i['w']
    P.sparkles(f, t, n, [(x - 3, y + 1), (x + w + 2, y - 1)])


def fx_bolt(f, t, n, i, o):
    if t % 4 in (0, 1):
        f.art(P.BOLT, 4, 3); f.art(P.BOLT, 33, 6)
def fx_rainbow(f, t, n, i, o):
    k = min(6, t)
    for j, c in enumerate('RFUEBP'):
        if j < k:
            f.ring(20, 26, 18 - j, c)
def fx_code(f, t, n, i, o):
    cx, top = _head(i)
    for j, s in enumerate(['</>', '{}', '()', '=>']):
        p = (t / n + j / 4) % 1
        f.text(s, int(4 + j * 8 + math.sin(p * 6) * 1), int(top - 2 - p * 18), pick(['B', 'E', 'P', 'F'], j))
def fx_binary(f, t, n, i, o):
    r = rng(5)
    for k in range(10):
        x = r.randint(1, 37)
        off = r.random()
        p = (t / n + off) % 1
        f.text(str(r.randint(0, 1)), x, int(-5 + p * 30), 'E')
def fx_loading(f, t, n, i, o):
    cx, top = _head(i)
    P.spinner(f, int(cx), int(top) - 6, t)
def fx_leaves(f, t, n, i, o): P.falling(f, P.LEAF, t, n, count=8, seed=4, sway=3)
def fx_petals(f, t, n, i, o): P.falling(f, P.PETAL, t, n, count=12, seed=6, sway=3)
def fx_night(f, t, n, i, o):
    P.moon(f, 31, 3)
    P.sparkles(f, t, n, [(4, 4), (14, 2), (24, 8), (8, 12), (36, 14)])
def fx_bats(f, t, n, i, o):
    for k in range(3):
        a = 2 * math.pi * (t / n + k / 3)
        P.batwing(f, int(18 + 14 * math.cos(a)), int(8 + 4 * math.sin(2 * a)), t + k)
def fx_ghosts(f, t, n, i, o):
    for k in range(2):
        p = (t / n + k / 2) % 1
        P.ghost(f, int(3 + k * 28 + 2 * math.sin(p * 6.28)), int(4 + 3 * math.sin(p * 6.28 + k)), t)
def fx_flies(f, t, n, i, o):
    cx, top = _head(i)
    P.orbit(f, cx, top - 2, 9, 4, t, n, P.FLY, count=3, speed=2)
def fx_coins(f, t, n, i, o): P.falling(f, ['.UU.', 'UYYU', 'UYYU', '.UU.'], t, n, count=7, seed=12, sway=0.5)
def fx_butterfly(f, t, n, i, o):
    a = 2 * math.pi * t / n
    P.butterfly(f, int(20 + 13 * math.cos(a)), int(10 + 4 * math.sin(2 * a)), t)
def fx_heartbig(f, t, n, i, o):
    cx, top = _head(i)
    s = t % 4 < 2
    f.art(P.HEART_BIG if s else P.HEART, int(cx) - (3 if s else 1), int(top) - (11 if s else 8))
def fx_stars(f, t, n, i, o):
    P.sparkles(f, t, n, [(3, 5), (12, 2), (27, 4), (36, 9), (6, 14), (33, 18)])
def fx_shadow(f, t, n, i, o):
    pass


FX = {k[3:]: v for k, v in globals().items() if k.startswith('fx_')}
BACK_FX = {'sun', 'rainbow', 'night', 'fireworks', 'stars', 'bolt'}


# --------------------------------------------------------------------------- compositor
def S(f, t, n, act='idle', eyes=None, hat=None, hat_dy=0, face=None, item=None, item_l=None, fx=(),
      say=None, say_every=4, body=None, mouth=None, blush=False, view=None, la=None, ra=None,
      tf=None, fxc=None, think=None, mini_pals=(), extra=None, back=None, **kw):
    """Generic scene: an action plus optional hat / face gear / items / effects / speech."""
    o = dict(kw)
    if eyes:
        o['eyes'] = eyes
    if fxc:
        o['fxc'] = fxc
    pose, ptf = ACTIONS[act](t, n, o)
    if view and 'view' not in kw and act not in ('spin', 'walkr', 'walkl', 'run', 'look', 'no', 'pace'):
        pose['view'] = view
    if la:
        pose['la'] = la
    if ra:
        pose['ra'] = ra
    if mouth:
        pose['mouth'] = mouth(t) if callable(mouth) else mouth
    if blush:
        pose['blush'] = True
    if body:
        pose['body'], pose['shade'] = body if isinstance(body, tuple) and len(body) == 2 and not isinstance(body[0], int) else (body, 'o')
    fxs = [fx] if isinstance(fx, str) else list(fx)

    if back:
        back(f, t, n)
    # back effects (need a provisional info for positions)
    probe = Canvas()
    info0 = clawd(probe, **pose)
    for name in fxs:
        if name in BACK_FX:
            FX[name](f, t, n, info0, o)

    L = Canvas()
    if face == 'cape':
        P.face(L, info0, 'cape', t)
    info = clawd(L, **pose)
    if face and face != 'cape':
        for fc in ([face] if isinstance(face, str) else face):
            P.face(L, info, fc, t)
    if hat:
        if hat == 'propeller':
            P.hat(L, info, 'propeller', art=P.propeller_art(t), dy=hat_dy)
        elif hat == 'headphones':
            P.headphones(L, info)
        elif hat == 'helmet':
            P.helmet(L, info)
        else:
            P.hat(L, info, hat, dy=hat_dy)
    if item:
        P.hold(L, info, item, 'r')
    if item_l:
        P.hold(L, info, item_l, 'l')
    if extra:
        extra(L, t, n, info)
    T = tf or ptf
    if T:
        L = T(L)
    f.blit(L)

    for name in fxs:
        if name not in BACK_FX:
            FX[name](f, t, n, info, o)
    if say:
        msgs = say.split('|')
        msg = msgs[(t // say_every) % len(msgs)]
        if msg:
            P.say(f, info, msg, c=o.get('fxc', 'B') if 'dots' not in fxs else 'B')
    if think:
        cx, top = info['head']
        P.thought(f, int(cx) - 2, int(top) - 16, 14, 9)
        think(f, int(cx) - 2, int(top) - 16, t)
    return info
