"""Pixel props for Clawd: hats, face gear, held items and effects."""
import math
from engine import (Canvas, G, GROUND, parse, size, rng, sin, cos, ph, pick, tri,
                    text_w, col, mix)

# --------------------------------------------------------------------------- hats
# name -> (art, sink) ; sink = rows the hat overlaps into the body top
HATS = {
    'party': ("""
        ...U...
        ..UUU..
        ...Z...
        ..ZZZ..
        ..BBB..
        .ZZZZZ.
        .BBBBB.
        ZZZZZZZ
    """, 0),
    'crown': ("""
        U...UU...U
        UU.UYYU.UU
        UUUUUUUUUU
        YZYYBBYYZY
        YYYYYYYYYY
    """, 0),
    'tophat': ("""
        ..kkkkkk..
        ..kkkkkk..
        ..kkkkkk..
        ..kkkkkk..
        ..RRRRRR..
        kkkkkkkkkk
    """, 0),
    'santa': ("""
        ...........WW.
        .......RRRRWW.
        .....RRRRRR...
        ...RRRRRRRRR..
        ..RRRRRRRRRRR.
        WWWWWWWWWWWWWWWW
        WWWWWWWWWWWWWWWW
    """, 1),
    'witch': ("""
        .........kk...
        ........kkk...
        .......kkkk...
        ......kkkkk...
        .....kkkkkk...
        .....kkkkkkk..
        .....PPPPPPP..
        ....kkkkkkkkk.
        kkkkkkkkkkkkkkkk
    """, 0),
    'wizard': ("""
        .......b......
        ......bbb.....
        ......bUb.....
        .....bbbbb....
        .....bbbbU....
        ....bbUbbbb...
        ....bbbbbbb...
        ...bbbbbbbUb..
        bbbbbbbbbbbbbbbb
    """, 0),
    'cowboy': ("""
        ....NNNNNNNN....
        ...NNNNnNNNNN...
        ...nnnnnnnnnn...
        N..NNNNNNNNNN..N
        NNNNNNNNNNNNNNNN
        .NNNNNNNNNNNNNN.
    """, 0),
    'chef': ("""
        ..WWWW.WWWWW.WWW..
        .WWWWWWWWWWWWWWWW.
        WWWWWWWWWWWWWWWWWG
        WWWWWWWWWWWWWWWWWG
        .WWWWWWWWWWWWWWWG.
        .wwwwwwwwwwwwwwwG.
        .WWWWWWWWWWWWWWWG.
        .WWWWWWWWWWWWWWWG.
    """, 0),
    'chef_s': ("""
        ..WWW..WWW..
        .WWWWWWWWWW.
        .WWWWWWWWWW.
        ..WWWWWWWW..
        ..WWWWWWWW..
        ..GGGGGGGG..
    """, 0),
    'grad': ("""
        .......kk.......
        ...kkkkkkkkkk...
        kkkkkkkkkkkkkkkk
        ...kkkkkkkkkk..U
        ....kkkkkkkk...U
        ....kkkkkkkk..UU
    """, 0),
    'beanie': ("""
        ......WW......
        ....RRRRRR....
        ..RRRRRRRRRR..
        .RRRRRRRRRRRR.
        WRWRWRWRWRWRWRWR
    """, 1),
    'cap': ("""
        ....BBBBBB.......
        ...BBBBWBBB......
        ..BBBBBBBBBBBBBBB
    """, 0),
    'capback': ("""
        .......BBBBBB....
        ......BBBBBBBB...
        BBBBBBBBBBBBBBB..
    """, 0),
    'bow': ("""
        ZZ...ZZ
        ZZZ.ZZZ
        ZZZrZZZ
        ZZZ.ZZZ
        ZZ...ZZ
    """, 0),
    'halo': ("""
        ..UUUUUU..
        UUU....UUU
        ..UUUUUU..
    """, -2),
    'horns': ("""
        R..............R
        RR............RR
        RR............RR
    """, 0),
    'bunny': ("""
        .WW......WW.
        WrrW....WrrW
        WrrW....WrrW
        WrrW....WrrW
        WrrW....WrrW
        .WW......WW.
        .WW......WW.
    """, 0),
    'cat': ("""
        oO..........Oo
        oOO........OOo
        oOOO......OOOo
    """, 0),
    'viking': ("""
        W..............W
        WW....GGGG....WW
        .WW.GGGGGGGG.WW.
        ..WGGGGGGGGGGW..
        ..GGGGGGGGGGGG..
        gggggggggggggggg
    """, 1),
    'hardhat': ("""
        .....UUUUUU.....
        ...UUUUUUUUUU...
        ..UUUUUYUUUUUU..
        ..UUUUUYUUUUUU..
        YYYYYYYYYYYYYYYYYY
    """, 0),
    'beret': ("""
        .......k......
        ..kkkkkkkkkk..
        kkkkkkkkkkkkkk
        .kkkkkkkkkkkk.
    """, 0),
    'pirate': ("""
        ...kkkkkkkkkk...
        ..kkkkkWWkkkkk..
        .kkkkkkkkkkkkkk.
        kkkkkkWkkWkkkkkk
        .kkkkkkkkkkkkkk.
        ..UUUUUUUUUUUU..
    """, 0),
    'ninja': ("""
        RRRRRRRRRRRRRRRR
        RRRRRRRRRRRRRRRR
    """, 2),
    'bucket': ("""
        ....EEEEEEEE....
        ...EEEEEEEEEE...
        ...eeeeeeeeee...
        EEEEEEEEEEEEEEEE
    """, 1),
    'sailor': ("""
        ...WWWWWWWWWW...
        ..WWWWWWWWWWWW..
        ..bbbbbbbbbbbb..
    """, 0),
    'jester': ("""
        U..............U
        PP............ZZ
        .PP...PPZZ...ZZ.
        ..PPPPPPZZZZZZ..
        ..PPPPPPZZZZZZ..
    """, 0),
    'flower': ("""
        .Z.
        ZUZ
        .Z.
        .E.
    """, 0),
    'tiara': ("""
        .....W.....
        ..W.WCW.W..
        GGGGGGGGGGG
    """, 0),
    'fire': ("""
        ...RRRRRRRRRR...
        RRRRRRRRRRRRRRRR
        .RRRRUUUURRRRRR.
        RRRRRRRRRRRRRRRR
    """, 0),
    'propeller': ("""
        .....RRRBBB.....
        ........K.......
        .....YYYYYY.....
        ...ZZZZZZZZZZ...
        ..BBBBBBBBBBBB..
    """, 0),
    'antlers': ("""
        N.N..........N.N
        NNN..........NNN
        .N............N.
        .NN..........NN.
    """, 0),
    'mushroom': ("""
        ....RRRRRRRR....
        ..RRWWRRRRWRRR..
        .RRRWWRRRRRRWRR.
        RRRRRRRRRWWRRRRR
        RRWWRRRRRWWRRRRR
    """, 0),
    'frog': ("""
        .WWW......WWW.
        WKKW......WKKW
        EEEEEEEEEEEEEE
        EEEEEEEEEEEEEE
    """, 0),
    'helmet': ("""
        ....RRRRRRRR....
        ..RRRRRRRRRRRR..
        .RRRRRRUURRRRRR.
        RRRRRRRRRRRRRRRR
    """, 0),
    'leaf': ("""
        ..EE
        .EEe
        EEe.
        .n..
    """, 0),
    'candle': ("""
        .U.
        .F.
        WWW
        WWW
    """, 0),
    'pumpkin': ("""
        ......e........
        ...FFFeFFFF....
        .FFFFFFFFFFFF..
        FFFFFFFFFFFFFF.
    """, 0),
}


def hat(f, info, name, dx=0, dy=0, flip=False, art=None):
    a, sink = HATS[name] if art is None else (art, 0)
    w, h = size(a)
    cx, top = info['head']
    f.art(a, int(round(cx - w / 2)) + dx, int(top) - h + sink + dy, flip=flip)


def propeller_art(t):
    blades = pick(['.....RRRBBB.....', '......RRRB......', '....BBB.RRR.....', '.......KB.......'], t)
    a = parse(HATS['propeller'][0])
    a[0] = blades
    return a


def sprout_art(stage):
    """Growth stages 0-4 (stem centred on column 3 of a 7-wide box)."""
    arts = [
        ['...E...', '...E...'],
        ['..E.E..', '...E...', '...E...'],
        ['.EE.EE.', '..EEE..', '...E...', '...E...'],
        ['.EE.EE.', 'EEE.EEE', '.EEEEE.', '...E...', '...E...'],
        ['..ZZZ..', '.ZZUZZ.', '..ZZZ..', 'EE.E.EE', '.EEEEE.', '...E...', '...E...'],
    ]
    return arts[max(0, min(stage, len(arts) - 1))]


def headphones(f, info, c='V', pad=None, lift=0):
    """Big over-ear headphones like the video. lift>0 raises them (putting them on)."""
    pad = pad or c
    x, y, w = info['x'], info['y'] - lift, info['w']
    f.put(x - 1, y - 1, c); f.put(x - 1, y - 2, c); f.put(x, y - 3, c)
    f.rect(x + 1, y - 4, w - 2, 1, c)
    f.put(x + w - 1, y - 3, c); f.put(x + w, y - 2, c); f.put(x + w, y - 1, c)
    f.rect(x - 2, y, 3, 5, pad); f.rect(x + w - 1, y, 3, 5, pad)


def helmet(f, info, c='G', hi='W'):
    """Astronaut glass dome around the head, collar across the body (video space scene)."""
    x, y, w = info['x'], info['y'], info['w']
    cx, cy = x + w / 2, y + 5
    rx, ry = w / 2 + 2.5, 9.5
    for yy in range(int(cy - ry - 1), int(cy) + 1):
        for xx in range(int(cx - rx - 1), int(cx + rx + 1)):
            d = ((xx + .5 - cx) / rx) ** 2 + ((yy + .5 - cy) / ry) ** 2
            if 0.80 <= d <= 1.0:
                f.put(xx, yy, c)
    f.rect(x - 1, y + 5, w + 2, 1, c)
    f.rect(int(cx) + 3, int(cy - ry) + 2, 2, 1, hi)
    f.put(int(cx) + 5, int(cy - ry) + 3, hi)


# --------------------------------------------------------------------------- face gear
EYE_GEAR = {'shades', 'shades_cool', 'glasses', 'readers', 'round', '3d', 'monocle', 'eyepatch', 'goggles'}


def _eye_gear_turned(f, info, name):
    """Glasses & co. in a turned view: each lens centred on the eye the engine actually drew
    (info['eyes']); in profile only the visible eye gets a lens."""
    y = info['y']
    (ax, _), (bx, _) = sorted(info['eyes'])
    lx, rx = int(math.floor(ax)), int(math.floor(bx))   # eye centres (between the 2 eye cols)
    single = rx - lx < 4                                  # profile: one eye on the front edge
    facing_r = info['view'].endswith('r')
    lenses = [rx if facing_r else lx] if single else [lx, rx]
    lens = {'shades': (2, 3, 1, 3, 'K'), 'shades_cool': (3, 3, 1, 3, 'K'), 'glasses': (2, 2, 1, 4, 'K'),
            'readers': (3, 3, 1, 5, 'm'), 'round': (2, 2, 1, 4, 'K'), '3d': (2, 2, 1, 4, 'K'),
            'monocle': (2, 2, 1, 4, 'Y'), 'eyepatch': (2, 2, 1, 4, 'K'), 'goggles': (2, 3, 1, 4, 'k')}[name]
    lw_l, lw_r, top, lh, c = lens
    near = max(lenses) if facing_r else min(lenses)
    boxes = []
    for i, cx in enumerate(lenses):
        if name == 'monocle' and cx != near:
            continue
        if name == 'eyepatch' and len(lenses) == 2 and cx == near:
            continue
        x0 = cx - lw_l
        boxes.append((x0, cx + lw_r - x0))
    if name in ('shades', 'shades_cool', 'goggles') or (name in ('glasses', 'readers', 'round', '3d') and len(boxes) == 2):
        if len(boxes) == 2:
            f.rect(boxes[0][0] + boxes[0][1], y + 2, boxes[1][0] - boxes[0][0] - boxes[0][1], 1, c)
    for x0, bw in boxes:
        if name in ('shades', 'shades_cool', 'eyepatch'):
            f.rect(x0, y + 2 if name != 'eyepatch' else y + 1, bw, lh if name == 'eyepatch' else 3, c)
            if name == 'shades':
                f.put(x0 + 1, y + 2, 'W')
        elif name == 'goggles':
            f.rect(x0, y + 1, bw, 4, 'k'); f.rect(x0 + 1, y + 2, bw - 2, 2, 'C')
        elif name == '3d':
            f.rect(x0, y + 1, bw, 4, 'K'); f.rect(x0 + 1, y + 2, bw - 2, 2, 'R' if x0 == boxes[0][0] else 'C')
        else:
            f.box(x0, y + 1 if name != 'readers' else y + 1, bw, lh, c)
    if name == 'eyepatch' and boxes:
        f.line(info['x'], y, info['x'] + info['w'] - 1, y + 2, 'K')


def eye_cols(eye, screen_right):
    """Pixel column under an eye centre from info['eyes'] (outer column of the 2-wide eye)."""
    return int(math.floor(eye[0])) - (0 if screen_right else 1)


def tear(f, eye, p, screen_right=False, ground=GROUND, c='B', hi='C'):
    """A tear a fraction p (0..1) of its way from an eye (an info['eyes'] centre) to the ground:
    it wells up under the eye, runs down the cheek over the body and drips off. Tears always
    start AT an eye - never float beside Clawd."""
    x = eye_cols(eye, screen_right)
    y0 = int(math.floor(eye[1])) + 1
    y = y0 + int(round(p * max(0, ground - 2 - y0)))
    f.put(x, y, hi)
    f.put(x, y + 1, c)


def tear_spray(f, eye, p, side, reach=14, rise=20, fall=30, c='B'):
    """Comic fountain tear: leaves the eye at p=0 and arcs outwards (side -1/+1)."""
    ex, ey = eye
    px = ex + side * (1 + p * reach)
    py = ey - 1 - rise * p + fall * p * p
    f.rect(int(px), int(py), 2, 2, c)
    f.put(int(px), int(py), 'C')


def face(f, info, name, t=0):
    if name in EYE_GEAR and info.get('view') in ('qr', 'ql', 'q2r', 'q2l', 'sr', 'sl') and 'eyes' in info:
        return _eye_gear_turned(f, info, name)
    x, y, w = info['x'], info['y'], info['w']
    if info.get('view') == 'qr':
        x += 1
    elif info.get('view') == 'ql':
        x -= 1
    if name == 'shades':
        f.rect(x + 1, y + 2, 5, 3, 'K'); f.rect(x + w - 6, y + 2, 5, 3, 'K')
        f.rect(x + 6, y + 2, w - 12, 1, 'K')
        f.put(x + 2, y + 2, 'W'); f.put(x + w - 5, y + 2, 'W')
    elif name == 'shades_cool':
        f.rect(x, y + 2, w, 1, 'K')
        f.rect(x + 1, y + 2, 6, 3, 'K'); f.rect(x + w - 7, y + 2, 6, 3, 'K')
        f.put(x + 2, y + 3, 'b'); f.put(x + w - 6, y + 3, 'b')
    elif name == 'glasses':
        f.box(x + 1, y + 1, 4, 4, 'K'); f.box(x + w - 5, y + 1, 4, 4, 'K')
        f.rect(x + 5, y + 2, w - 10, 1, 'K')
    elif name == 'readers':  # big crimson reading glasses from the video
        f.box(x, y + 1, 6, 5, 'm'); f.box(x + w - 6, y + 1, 6, 5, 'm')
        f.rect(x + 6, y + 2, w - 12, 1, 'm')
    elif name == 'round':
        for ox in (x + 1, x + w - 5):
            f.art(['.KK.', 'K..K', 'K..K', '.KK.'], ox, y + 1)
        f.rect(x + 5, y + 2, w - 10, 1, 'K')
    elif name == '3d':
        f.rect(x + 1, y + 1, 4, 4, 'K'); f.rect(x + w - 5, y + 1, 4, 4, 'K')
        f.rect(x + 2, y + 2, 2, 2, 'R'); f.rect(x + w - 4, y + 2, 2, 2, 'C')
        f.rect(x + 5, y + 2, w - 10, 1, 'K')
    elif name == 'monocle':
        f.box(x + w - 5, y + 1, 4, 4, 'Y'); f.line(x + w - 2, y + 5, x + w - 1, y + 9, 'Y')
    elif name == 'eyepatch':
        f.rect(x + 1, y + 1, 4, 4, 'K'); f.line(x, y, x + w - 1, y + 2, 'K')
    elif name == 'mask':
        f.rect(x, y + 1, w, 4, 'K')
        f.rect(x + 2, y + 2, 2, 2, 'W'); f.rect(x + w - 4, y + 2, 2, 2, 'W')
    elif name == 'goggles':
        f.rect(x, y + 2, w, 1, 'k')
        f.rect(x + 1, y + 1, 5, 4, 'k'); f.rect(x + w - 6, y + 1, 5, 4, 'k')
        f.rect(x + 2, y + 2, 3, 2, 'C'); f.rect(x + w - 5, y + 2, 3, 2, 'C')
    elif name == 'vr':
        f.rect(x - 1, y + 1, w + 2, 5, 'k'); f.rect(x, y + 2, w, 3, 'g')
        f.rect(x + 2, y + 3, w - 4, 1, pick(['C', 'P', 'E', 'U'], t))
    elif name == 'medmask':
        f.rect(x + 2, y + 5, w - 4, 4, 'S'); f.rect(x, y + 5, 2, 1, 'w'); f.rect(x + w - 2, y + 5, 2, 1, 'w')
        f.rect(x + 3, y + 6, w - 6, 1, 'C')
    elif name == 'beard':
        f.art(['WW............WW', 'WWWW........WWWW', 'WWWWWWWWWWWWWWWW', '.WWWWWWWWWWWWWW.',
               '..WWWWWWWWWWWW..', '....WWWWWWWW....', '......WWWW......'], x, y + 5)
    elif name == 'bandana':
        f.rect(x, y + 5, w, 4, 'R'); f.put(x + 3, y + 6, 'W'); f.put(x + 9, y + 7, 'W'); f.put(x + 12, y + 6, 'W')
        f.art(['RRRR', '.RR.', '..R.'], x + w // 2 - 2, y + 9)
    elif name == 'scarf':
        f.rect(x - 1, y + 8, w + 2, 2, 'R'); f.rect(x + w - 4, y + 10, 3, 4, 'R')
        f.rect(x + w - 4, y + 13, 3, 1, 'W')
    elif name == 'bowtie':
        f.art(['RR..RR', 'RRRRRR', 'RR..RR'], x + w // 2 - 3, y + 8)
    elif name == 'tie':
        f.art(['.R.', 'RRR', '.R.', '.R.', 'RRR', '.R.'], x + w // 2 - 1, y + 6)
    elif name == 'necklace':
        f.line(x + 2, y + 7, x + 7, y + 9, 'U'); f.line(x + w - 3, y + 7, x + w - 8, y + 9, 'U')
        f.rect(x + 7, y + 9, 2, 2, 'Z')
    elif name == 'cape':  # drawn behind: call before clawd
        f.art(['RRRRRRRRRRRRRRRRRR', 'RRRRRRRRRRRRRRRRRR', '.RRRRRRRRRRRRRRRRRR',
               '.RRRRRRRRRRRRRRRRRRR', '..RRRRRRRRRRRRRRRRRR'], x - 1, y + 2)


# --------------------------------------------------------------------------- held items
# name -> (art, grip_x, grip_y)  grip = pixel (in the art) that sits at the hand point
ITEMS = {
    'mug': ("""
        GGGGG..
        GNNNGGG
        GWWWG.G
        GWWWG.G
        GWWWGGG
        .GGG...
    """, 0, 3),
    'cup': ("""
        GWWWWWG..
        GWWWWWGGG
        .GWWWG..G
        ..GGG.GG.
        GGGGGGGG.
    """, 0, 2),
    'boba': ("""
        ...k.
        ...k.
        LLLLL
        LTTTL
        LTTTL
        LkTkL
        LkkkL
        .LLL.
    """, 0, 4),
    'icecream': ("""
        .rrr.
        rrrrr
        ZrrrZ
        YYYYY
        .YNY.
        .YYY.
        ..Y..
    """, 1, 5),
    'lolly': ("""
        .ZZZ.
        ZWZWZ
        ZZWZZ
        ZWZWZ
        .ZZZ.
        ..W..
        ..W..
        ..W..
    """, 2, 6),
    'pizza': ("""
        NNNNNN
        YRYYRY
        .YYYY.
        .YRYY.
        ..YY..
        ..Y...
    """, 0, 1),
    'donut': ("""
        .ZZZZ.
        ZUZZBZ
        ZZ..ZZ
        NZ..ZN
        NNNNNN
        .NNNN.
    """, 0, 3),
    'apple': ("""
        ..n.E
        .RRRE
        RRWRRR
        RRRRRR
        RRRRRR
        .RRRR.
    """, 0, 3),
    'burger': ("""
        .YYYYYY.
        YYTYYTYY
        EEEEEEEE
        nnnnnnnn
        YYYYYYYY
    """, 0, 2),
    'cookie': ("""
        .NNNN.
        NNnNNN
        NnNNnN
        NNNnNN
        .NNNN.
    """, 0, 2),
    'phone': ("""
        kkkk
        kSSk
        kSSk
        kSSk
        kkkk
    """, 0, 2),
    'magnifier': ("""
        .kkk...
        kSWSk..
        kSSSk..
        kSSSk..
        .kkk...
        ....N..
        .....N.
        ......N
    """, 6, 7),
    'wand': ("""
        .U.
        UUU
        .U.
        .k.
        .k.
        .k.
        .W.
    """, 1, 5),
    'sword': ("""
        .W.
        .W.
        .W.
        .W.
        .W.
        YYY
        .N.
    """, 1, 6),
    'flag': ("""
        kRRRRR
        kRRRRR
        kRRRR.
        k.....
        k.....
        k.....
    """, 0, 5),
    'flower': ("""
        .Z.
        ZUZ
        .Z.
        .E.
        EE.
        .E.
    """, 1, 5),
    'rose': ("""
        .RR.
        RRRR
        .RR.
        .E..
        .EE.
        .E..
    """, 1, 5),
    'trophy': ("""
        UUUUUU
        UUUUUU
        UUUUUU
        .UUUU.
        ..UU..
        .YYYY.
    """, 0, 2),
    'hammer': ("""
        ggggg
        ggggg
        ..N..
        ..N..
        ..N..
    """, 2, 4),
    'wrench': ("""
        G.G
        GGG
        .G.
        .G.
        .G.
    """, 1, 4),
    'torch': ("""
        .F.
        FUF
        FUF
        .N.
        .N.
    """, 1, 4),
    'mic': ("""
        GgG
        gGg
        GgG
        .k.
        .k.
    """, 1, 4),
    'book': ("""
        BBBBB
        BWWWB
        BBBBB
        BWWWB
        BBBBB
    """, 0, 2),
    'heart': ("""
        .Z.Z.
        ZZZZZ
        ZZZZZ
        .ZZZ.
        ..Z..
    """, 0, 2),
    'star': ("""
        ..U..
        .UUU.
        UUUUU
        .UUU.
        U...U
    """, 0, 2),
    'coin': ("""
        .UUU.
        UYUYU
        UYUYU
        UYUYU
        .UUU.
    """, 0, 2),
    'key': ("""
        UUU....
        U.UUUUU
        UUU.U.U
    """, 0, 1),
    'gift': ("""
        .Z.Z.
        ..Z..
        BBZBB
        BBZBB
        BBZBB
    """, 0, 3),
    'brush': ("""
        ..P
        .NN
        .N.
        N..
        N..
    """, 0, 4),
    'pencil': ("""
        ...k
        ..YT
        .YY.
        YY..
        Z...
    """, 0, 4),
    'spinner': ("""
        ..bb..
        .bWWb.
        bbkkbb
        bbkkbb
        .bWWb.
        ..bb..
    """, 0, 3),
    'sparkler': ("""
        U.W.U
        .UWU.
        WWUWW
        .UWU.
        U.k.U
        ..k..
        ..k..
    """, 2, 6),
    'lantern': ("""
        ..k..
        .YYY.
        RRRRR
        RYRYR
        RRRRR
        .YYY.
        ..Y..
    """, 2, 0),
    'envelope': ("""
        RRRRR
        RUUUR
        RRURR
        RRRRR
        RRRRR
    """, 0, 2),
    'candy': ("""
        Z.....Z
        ZZWZWZZ
        Z.....Z
    """, 0, 1),
    'carrot': ("""
        ..E.E
        ...E.
        ..FF.
        .FF..
        FF...
    """, 0, 4),
    'fish': ("""
        .CCC.C
        CKCCCC
        .CCC.C
    """, 0, 1),
    'banana': ("""
        ....n
        ...U.
        ..UU.
        UUU..
    """, 0, 3),
    'watermelon': ("""
        RKRRKR
        RRRKRR
        .EEEE.
    """, 0, 1),
    'sushi': ("""
        .FFFF.
        WWWWWW
        kkkkkk
    """, 0, 1),
    'paper': ("""
        GGGG
        GkkG
        GWWG
        GkkG
        GGGG
    """, 0, 2),
    'controller': ("""
        .kkkkkk.
        kkWkkRkk
        kWWWkkBk
        kkWkkkkk
        kk....kk
    """, 0, 2),
    'camera': ("""
        .kk....
        kkkkkkk
        kGkkkGk
        kkkSkkk
        kkkkkkk
    """, 0, 2),
    'racket': ("""
        .EEE.
        EWEWE
        EEWEE
        EWEWE
        .EEE.
        ..N..
        ..N..
    """, 2, 6),
    'bat': ("""
        ...N
        ...N
        ..NN
        ..N.
        .N..
        n...
    """, 0, 5),
    'broom': ("""
        ...........YYY
        NNNNNNNNNNYYYY
        ...........YYY
    """, 3, 1),
    'umbrella': ("""
        ....RRR....
        ..RRRRRRR..
        .RRWRRRWRR.
        RRRRRRRRRRR
        .....k.....
        .....k.....
        .....k.....
        .....k.....
        .....k.....
        ...k.k.....
        ....k......
    """, 5, 8),
    'balloon': ("""
        .ZZZ.
        ZWZZZ
        ZZZZZ
        ZZZZZ
        .ZZZ.
        ..Z..
    """, 2, 5),
    'wateringcan': ("""
        ..CCC.....
        .C...C....
        CCCCCCC..C
        CCCCCCC.C.
        CCCCCCCC..
        CCCCCCC...
    """, 0, 3),
    'dumbbell': ("""
        kk.......kk
        kkGGGGGGGkk
        kk.......kk
    """, 5, 1),
}


def item(f, pt, name, flip=False, dx=0, dy=0, art=None):
    a, gx, gy = ITEMS[name] if art is None else art
    w, _ = size(a)
    if flip:
        gx = w - 1 - gx
    f.art(a, int(round(pt[0])) - gx + dx, int(round(pt[1])) - gy + dy, flip=flip)


def hold(f, info, name, side='r', dx=0, dy=0):
    """Hold an item in the right ('r') or left ('l') hand."""
    if side == 'r':
        item(f, info['rh'], name, dx=dx, dy=dy)
    else:
        item(f, info['lh'], name, flip=True, dx=dx - 1, dy=dy)


def balloon_string(f, hand, top, c='k', t=0):
    hx, hy = hand
    bx, by = top
    steps = max(1, int(abs(hy - by)))
    for i in range(steps + 1):
        yy = hy - (hy - by) * i / steps
        xx = hx + (bx - hx) * i / steps + math.sin(i / 2 + t) * 0.6
        f.put(xx, yy, c)


# --------------------------------------------------------------------------- effects
NOTE = ['.KK', '.K.', 'KK.', 'KK.']
NOTE2 = ['.KKKK', '.K..K', '.K..K', 'KK.KK', 'KK.KK']
HEART = ['Z.Z', 'ZZZ', '.Z.']
HEART_BIG = ['.ZZ.ZZ.', 'ZZZZZZZ', 'ZZZZZZZ', '.ZZZZZ.', '..ZZZ..', '...Z...']
SPARK = ['.W.', 'WUW', '.W.']
SPARK_BIG = ['...U...', '...U...', '..UWU..', 'UUWWWUU', '..UWU..', '...U...', '...U...']
STAR5 = ['..U..', '.UUU.', 'UUUUU', '.UUU.', 'U...U']
DROP = ['.B.', 'BBB', 'BBB', '.B.']
SWEAT = ['.S', 'SS', 'SS']
PUFF = ['.LL.', 'LLLL', 'LLLL', '.LL.']
PUFF_S = ['LL', 'LL']
QMARK = ['KKK.', '...K', '.KK.', '....', '.K..']
EXCL = ['K', 'K', 'K', '.', 'K']
VEIN = ['R.R', '...', 'R.R']
VEIN2 = ['.R.R.', 'RR.RR', '.....', 'RR.RR', '.R.R.']
BOLT = ['..UU', '.UU.', 'UUUU', '..U.', '.U..']
SNOW = ['.W.', 'WWW', '.W.']
LEAF = ['.F', 'FY']
PETAL = ['r.', 'rr']
FLY = ['k.k', '.k.']


def zzz(f, info, t, n, c='B'):
    cx, top = info['head']
    for i in range(3):
        p = ((t / n) + i / 3) % 1
        size_ = 1 if p < 0.33 else 2 if p < 0.66 else 3
        x = int(cx + 6 + p * 8)
        y = int(top - 1 - p * 14)
        z = {1: ['KK', '.K', 'KK'], 2: ['KKK', '..K', '.K.', 'KKK'], 3: ['KKKK', '...K', '..K.', '.K..', 'KKKK']}[size_]
        f.art(z, x, y - len(z), cmap={'K': c})


def notes(f, info, t, n, c='K', count=3, spread=10):
    cx, top = info['head']
    r = rng(7)
    for i in range(count):
        p = ((t / n) + i / count) % 1
        x0 = cx + r.randint(-spread, spread)
        x = int(x0 + math.sin(p * 6.28 + i) * 2)
        y = int(top - 6 - p * 14)
        f.art(NOTE if i % 2 else NOTE2, x, y, cmap={'K': c})


def rising(f, glyph, t, n, x0, y0, count=3, height=16, sway=2, seed=1, jitter=6, cmap=None):
    """Glyphs drifting upward in a staggered loop."""
    r = rng(seed)
    offs = [r.uniform(-jitter, jitter) for _ in range(count)]
    for i in range(count):
        p = ((t / n) + i / count) % 1
        x = int(round(x0 + offs[i] + math.sin(p * 6.28 + i * 2) * sway))
        y = int(round(y0 - p * height))
        f.art(glyph, x, y, cmap=cmap)


def falling(f, glyph, t, n, count=10, seed=3, speed=1.0, sway=1.5, top=-4, bottom=40, cmap=None, xs=None):
    r = rng(seed)
    for i in range(count):
        x0 = r.uniform(0, G) if xs is None else r.uniform(*xs)
        off = r.random()
        p = ((t / n) * speed + off) % 1
        y = top + p * (bottom - top)
        x = x0 + math.sin(p * 6.28 * 2 + i) * sway
        f.art(glyph, int(x), int(y), cmap=cmap)


def sparkles(f, t, n, pts, glyphs=(SPARK, ['W']), seed=5):
    r = rng(seed)
    for i, (x, y) in enumerate(pts):
        on = (t + r.randint(0, 3)) % 4
        if on == 0:
            f.art(SPARK, x - 1, y - 1)
        elif on == 1:
            f.put(x, y, 'W')
        elif on == 2:
            f.art(['.U.', 'UWU', '.U.'], x - 1, y - 1)


def orbit(f, cx, cy, rx, ry, t, n, glyph, count=3, cmap=None, speed=1):
    for i in range(count):
        a = 2 * math.pi * (speed * t / n + i / count)
        f.art(glyph, int(round(cx + math.cos(a) * rx)) - len(glyph[0]) // 2,
              int(round(cy + math.sin(a) * ry)) - len(glyph) // 2, cmap=cmap)


def speech(f, x, y, w, h, c='B', tail='left', text=None, tc='K', tail_x=None):
    """Speech bubble like the reference (solid blue, stair-step tail)."""
    f.rrect(x, y, w, h, c)
    tx = (x + 3 if tail == 'left' else x + w - 4) if tail_x is None else tail_x
    if tail == 'left':
        f.art(['CCC', 'CC.', 'C..'], tx, y + h, cmap={'C': c})
    elif tail == 'right':
        f.art(['CCC', '.CC', '..C'], tx, y + h, cmap={'C': c})
    elif tail == 'down':
        f.art(['CCC', '.C.'], tx, y + h, cmap={'C': c})
    if text:
        lines = text.split('\n')
        th = len(lines) * 6 - 1
        for i, ln in enumerate(lines):
            f.text_c(ln, x + w / 2, y + (h - th) // 2 + i * 6, tc)


def say(f, info, text, t=None, c='B', tc='K', dy=0, side='r', minw=7):
    """Bubble sized to text, placed above-right (or left) of the head."""
    lines = text.split('\n')
    w = max(minw, max(text_w(l) for l in lines) + 4)
    h = len(lines) * 6 + 3
    cx, top = info['head']
    if side == 'r':
        x = int(min(G - w - 1, cx - 1))
        tail = 'left'
    else:
        x = int(max(1, cx - w + 1))
        tail = 'right'
    y = int(top - h - 4 + dy)
    speech(f, x, y, w, h, c=c, tail=tail, text=text, tc=tc)
    return x, y, w, h


def dots_bubble(f, info, t, c='B', side='r', dy=0):
    """Reference-style bubble whose dots fill in one by one."""
    k = (t // 2) % 4
    cx, top = info['head']
    w, h = 10, 8
    x = int(cx - 1) if side == 'r' else int(cx - w + 1)
    y = int(top - h - 4 + dy)
    speech(f, x, y, w, h, c=c, tail='left' if side == 'r' else 'right')
    for i in range(k):
        f.put(x + 3 + i * 2, y + 4, 'K')


def thought(f, x, y, w, h, c='w', edge='G', tail='left'):
    """Cloud-shaped thought bubble with a 2-puff trail; grey edge so it reads on white."""
    L = Canvas(f.w, f.h)
    L.rrect(x, y + 1, w, h - 2, c)
    L.rrect(x + 1, y, w - 2, h, c)
    for i in range(1, w - 2, 4):
        L.rect(x + i, y - 1, 3, 1, c)
    for i in range(3, w - 3, 4):
        L.rect(x + i, y + h, 3, 1, c)
    tx = x + 2 if tail == 'left' else x + w - 4
    L.rect(tx, y + h + 2, 2, 2, c)
    L.put(tx - 1 if tail == 'left' else tx + 2, y + h + 5, c)
    f.blit(L.outline(edge) if edge else L)


def bulb(f, x, y, t, lit=True):
    on = lit and (t % 4 != 3)
    a = ['...YYY...', '.YYyyyYY.', '.YyWWyyY.', 'YyWyyyyyY', 'YyyyyyyyY', 'YyyyWyyyY',
         '.YyyWyyY.', '..YyWyY..', '...GGG...', '...ggg...', '...GGG...', '....g....']
    cm = None if on else {'y': 'G', 'Y': 'g', 'W': 'G'}
    f.art(a, x, y, cmap=cm)
    if on and t % 2 == 0:
        for (rx, ry) in ((-2, 3), (10, 3), (4, -2), (-1, -1), (9, -1)):
            f.put(x + rx, y + ry, 'U')


def cloud(f, x, y, c='w', w=12):
    f.rrect(x, y + 2, w, 4, c)
    f.rrect(x + 2, y, w // 2, 4, c)
    f.rrect(x + w // 2, y + 1, w // 2 - 1, 3, c)


def rain(f, t, n, x0, x1, y0, y1, c='B', seed=2, count=8):
    r = rng(seed)
    for i in range(count):
        x = r.randint(x0, x1)
        off = r.random()
        p = (t / n * 2 + off) % 1
        y = int(y0 + p * (y1 - y0))
        f.rect(x, y, 1, 2, c)


def sun(f, cx, cy, t, r=3):
    f.disc(cx, cy, r, 'U')
    rays = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    for i, (dx, dy) in enumerate(rays):
        if (i + t) % 2 == 0:
            L = r + 2
            f.put(cx + dx * L - (1 if dx < 0 else 0), cy + dy * L - (1 if dy < 0 else 0), 'Y')


def moon(f, x, y):
    f.art(['..UUU.', '.UUU..', 'UUU...', 'UUU...', 'UUU...', '.UUU..', '..UUU.'], x, y)


def confetti(f, t, n, count=24, seed=11, cols='ZBUEPC'):
    r = rng(seed)
    for i in range(count):
        x0 = r.uniform(0, G)
        off = r.random()
        c = cols[i % len(cols)]
        p = (t / n + off) % 1
        y = -2 + p * 44
        x = x0 + math.sin(p * 12 + i) * 1.5
        if (t + i) % 2:
            f.rect(int(x), int(y), 1, 2, c)
        else:
            f.rect(int(x), int(y), 2, 1, c)


def firework(f, cx, cy, p, c='Z', c2='U', r=7):
    """p in 0..1: rise, burst, fade."""
    if p < 0.25:
        f.rect(cx, int(cy + (0.25 - p) * 60), 1, 2, c2)
        return
    q = (p - 0.25) / 0.75
    rr = 2 + q * r
    for k in range(12):
        a = k * math.pi / 6
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        if q < 0.7:
            f.put(x, y, c)
            f.put(cx + math.cos(a) * rr * 0.6, cy + math.sin(a) * rr * 0.6, c2)
        elif k % 2 == 0:
            f.put(x, y + (q - 0.7) * 6, c)


def dust(f, x, y, p, flip=False):
    """Little dust puff at feet; p 0..1."""
    if p < 0.33:
        f.art(['.L', 'LL'], x, y - 2, flip=flip)
    elif p < 0.66:
        f.art(['.LL', 'LLL'], x - 1 if not flip else x, y - 2, flip=flip)
    else:
        f.art(['L.L', '...'], x - 2 if not flip else x + 1, y - 3, flip=flip)


def speedlines(f, x, y, t, n=4, length=6, c='L', side='l'):
    r = rng(17 + t)
    for i in range(n):
        yy = y + i * 3 + r.randint(0, 1)
        L = length + r.randint(-2, 2)
        xx = x - L - r.randint(0, 2) if side == 'l' else x + r.randint(0, 2)
        f.rect(xx, yy, L, 1, c)


def bubble_ring(f, cx, cy, r, c='L', hi='W'):
    f.ring(cx, cy, r, c)
    f.put(cx - r / 2, cy - r / 2, hi)


def burst(f, cx, cy, text='POW', c='U', c2='R', tc='K'):
    w = text_w(text) + 6
    h = 11
    x, y = cx - w // 2, cy - h // 2
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        rr = (w / 2 + 1) if k % 2 == 0 else (w / 2 - 2)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * h / w))
    for i in range(16):
        f.line(cx, cy, pts[i][0], pts[i][1], c2)
    f.rrect(x + 1, y + 2, w - 2, h - 4, c)
    f.text_c(text, cx, cy - 2, tc)


def heartbeat(f, x, y, w, t, c='E'):
    shape = [0, 0, 0, 0, -1, 0, 3, -5, 2, 0, 0, 0]
    for i in range(w):
        k = (i + t * 2) % len(shape)
        f.put(x + i, y + shape[k], c)


def progress(f, x, y, w, p, c='E', bg='k'):
    f.box(x, y, w, 4, bg)
    f.rect(x + 1, y + 1, int((w - 2) * p), 2, c)


def spinner(f, cx, cy, t, c='K', c2='L'):
    pts = [(0, -2), (1, -2), (2, -1), (2, 0), (2, 1), (1, 2), (0, 2), (-1, 2), (-2, 1), (-2, 0), (-2, -1), (-1, -2)]
    for i, (dx, dy) in enumerate(pts):
        k = (i - t) % 12
        f.put(cx + dx, cy + dy, c if k < 4 else c2)


def check(f, x, y, c='E'):
    f.art(['.....C', '....CC', 'C..CC.', 'CCCC..', '.CC...'], x, y, cmap={'C': c})


def cross(f, x, y, c='R'):
    f.art(['CC..CC', '.CCCC.', '..CC..', '.CCCC.', 'CC..CC'], x, y, cmap={'C': c})


def bug(f, x, y, t=0, c='E'):
    legs = pick(['k.k.k', '.k.k.'], t)
    f.art(['.k.k.', '..k..', '.CCC.', 'CCkCC', 'CCkCC', '.CCC.'], x, y, cmap={'C': c})
    f.art([legs], x, y + 3)


def ghost(f, x, y, t=0, c='W'):
    bottom = pick(['W.W.WW', 'WW.W.W'], t)
    f.art(['.WWWW.', 'WWWWWW', 'WKWWKW', 'WWWWWW', 'WWWWWW', bottom], x, y, cmap={'W': c})


def batwing(f, x, y, t=0):
    if t % 2:
        f.art(['k.....k', 'kk.k.kk', '.kkkkk.', '...k...'], x, y)
    else:
        f.art(['...k...', '.kkkkk.', 'kk...kk', 'k.....k'], x, y)


def butterfly(f, x, y, t=0, c='P', c2='U'):
    if t % 2:
        f.art(['CC.CC', 'CCkCC', '.CkC.', 'CC.CC'], x, y, cmap={'C': c})
    else:
        f.art(['.CkC.', '..k..', '.CkC.'], x, y + 1, cmap={'C': c})


# --------------------------------------------------------------------------- CJK text (SimSun 12px bitmaps)
_CJK = {}


def _glyph(ch):
    if ch not in _CJK:
        from PIL import Image, ImageDraw, ImageFont
        font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 12)
        im = Image.new('L', (14, 14), 0)
        ImageDraw.Draw(im).text((0, 0), ch, font=font, fill=255)
        rows = [''.join('#' if im.getpixel((x, y)) > 110 else '.' for x in range(12)) for y in range(14)]
        _CJK[ch] = rows
    return _CJK[ch]


def cjk_w(s):
    return sum(6 if ord(ch) < 128 else 12 for ch in s)


def cjk(f, s, x, y, c='K'):
    """Draw Chinese text with 12x12 bitmap glyphs (ASCII falls back to the 3x5 font)."""
    cx = x
    for ch in s:
        if ord(ch) < 128:
            f.text(ch, cx + 1, y + 4, c); cx += 6
            continue
        for j, row in enumerate(_glyph(ch)):
            for i, p in enumerate(row):
                if p == '#':
                    f.put(cx + i, y + j - 2, c)
        cx += 12
    return cx - x


def sign(f, x, y, text, c='T', edge='N', tc='K', stick=True):
    """A held-up sign board sized to CJK/ASCII text."""
    w = cjk_w(text) + 4
    f.rect(x, y, w, 14, c); f.box(x, y, w, 14, edge)
    cjk(f, text, x + 2, y + 2, tc)
    if stick:
        f.rect(x + w // 2, y + 14, 1, 6, edge)
    return w


POT = ['nnnnnnnn', 'NNNNNNNN', '.NNNNNN.', '.NNNNNN.', '..NNNN..']


def shooting_star(f, x, y, p, length=8):
    """Meteor heading down-left; (x, y) = start of its path, p 0..1 along a 24-px diagonal."""
    hx, hy = x - p * 24, y + p * 12
    for i, c in enumerate('WUUyyL'[:length]):
        f.put(hx + i * 2, hy - i, c)
    f.rect(int(hx) - 1, int(hy), 2, 2, 'W')
