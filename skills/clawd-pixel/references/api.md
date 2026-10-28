# Engine API (scripts/engine.py, props.py, kit.py)

Scene files `from engine import ...`, `import props as P`, `from kit import S`; `render.py` puts
`scripts/` on `sys.path`, so a scene file can live anywhere.

## Contents
1. Registering animations
2. Canvas
3. clawd() and mini()
4. props.py
5. kit.py — actions and the S() compositor
6. Backdrops and output

---

## 1. Registering animations

```python
from engine import add, clawd, BX, BY, GROUND, sin, cos, ph, pick, tri, rng

def wave(f, t, n, color='O'):          # called once per frame on a fresh 40x40 Canvas
    s = (t // 2) % 2
    clawd(f, ra='up' if s else 'wave', eyes='happy', body=color)

add('wave_hi', '挥手', 'Wave hello', wave, n=8, dur=150)      # extra kwargs go to the function
add('wave_dark', '挥手', 'Wave', wave, n=8, dur=150, backdrop=room())  # opaque, video-style room
```

`dur` is ms per frame (int) or a list per frame — `beats(n, ms, {frame: ms, (f1, f2): ms})` builds
the list (hold key poses, keep in-betweens short). In-betweens at a story's turning points:

```python
from engine import add_tweened, beats
# 1 in-between after frame 4 (crouch -> leap) and after 11 (landing), each 70 ms (tw_ms)
add_tweened('dunk', '扣篮', 'Slam dunk', dunk, n=20, dur=beats(20, 90, {4: 250, 7: 300}),
            tw_at={4: 1, 11: 1})
```
`add_tweened` renders each in-between by re-running frame k with every `clawd()` pose moved part
of the way to frame k+1's (views step round `VIEW_RING`, arms walk `ARM_LINKS`
side→mid→high→up, x/y/w/h/legs interpolate in whole pixels). `engine.find_snaps(fn, n, **kw)`
lists the snaps ({frame: steps needed}); `tw_at='auto'` uses all of them — usually too many, pick
the turning points. Props drawn at fixed coordinates stay where frame k had them, so look at
every in-between (rotated layers can't be tweened: hold the poses around a `rot90` instead).

Other helpers: `ph(t,n)` phase 0..1, `sin/cos(t,n,k,off)`,
`tri(t,n)` 0→1→0, `pick(seq,t)`, `rng(seed)` deterministic random (seed it the same every frame
so particles stay consistent).

## 2. Canvas (40×40, colours are palette keys or RGB tuples)

`put(x,y,c)` `get` `erase` `rect(x,y,w,h,c)` `box` (outline) `rrect` (corners cut) `line`
`disc(cx,cy,r,c)` `ring` `art(rows_or_str, x, y, flip=False, cmap={'K':'R'})` (`.` = transparent,
whitespace ignored) `text(s,x,y,c)` (3×5 caps font) `text_c` (centred) `blit(other,dx,dy)` `copy`
`recolor(fn)` `silhouette(c)` `outline(c)` (returns a copy with a 1-px outline — use it on white
props) `bbox()`. Colours anywhere accept palette keys, RGB tuples or `'#rrggbb'`.
Whole-layer transforms return new canvases: `flipx` `flipy` `shift(dx,dy)` `rot90(k,cx,cy)`
`shear(k,pivot_y)` `scale(s,ax,ay,sy)` `wave(amp,period,phase)` `rotate(deg)` (props only).
Draw Clawd on his own `Canvas()` layer when you need to transform him, then `f.blit(layer)`.

## 3. clawd() and mini()

```python
info = clawd(f, x=12, y=21, w=16, h=12,
             eyes='normal', eyes_r=None, look=0, lookv=0,      # glyph names in engine.EYES
             la='side', ra='side',                              # arm poses in engine.ARMS
             legs=(0,0,0,0), legdx=(0,0,0,0), leg_h=3,          # per-leg lift / shift, leg length
             view='front',   # front back qr ql q2r q2l sr sl
             tilt=0,         # turned views: near half of head +1px, near eye +1px
             top=False,      # 1-row top face (seen from above)
             body='O', shade='o', blush=False, mouth=None, eye_col=None)
```
Returns `info`: `x y w h`, `head=(cx, top_y)`, `lh`/`rh` = screen-left/right hand points,
`eyes`. Arm poses: `side mid high low up wave down out reach short front face chin none`
(`front`/`face`/`chin` are drawn across the body in shade).
mouth= and blush= are accepted but ignored (no mouths in this style). Squash/stretch by changing `w`/`h`/`x`/`y` (keep the feet on `GROUND`: `y = GROUND - leg_h - h`).

`mini(f, x, y, eyes, legs, la, ra, body, look, view)` — half-size Clawd (8×6 body) for crowds,
pets, clones.

## 4. props.py

- `HATS` + `hat(f, info, name, dx, dy)`: party crown tophat santa witch wizard cowboy chef chef_s
  grad beanie cap capback bow halo horns bunny cat viking hardhat beret pirate ninja bucket sailor
  jester flower tiara fire propeller antlers mushroom frog helmet leaf candle pumpkin.
  Specials: `headphones(f, info, c, pad, lift)`, `helmet(f, info)` (astronaut), `propeller_art(t)`,
  `sprout_art(stage)`.
- `face(f, info, name)`: shades shades_cool glasses readers round 3d monocle eyepatch mask mustache
  nose goggles vr medmask beard bandana scarf bowtie tie necklace cape. In turned views the eye
  gear is centred on `info['eyes']` (one lens in profile, monocle on the near eye).
- Eye-anchored effects: `tear(f, eye, p, screen_right)` (wells under an eye, runs down the cheek,
  drips to the ground; `eye` = an `info['eyes']` centre, `p` 0..1), `tear_spray(f, eye, p, side)`
  (comic fountain leaving the eye), `eye_cols(eye, screen_right)`. Use `sorted(info['eyes'])` for
  screen-left/right; in a q2r/q2l view the near eye is on the front edge — put eyepieces there.
- `ITEMS` + `hold(f, info, name, side='r')` / `item(f, pt, name)`: mug cup boba icecream lolly
  pizza donut apple burger cookie phone magnifier wand sword flag flower rose trophy hammer wrench
  torch mic book heart star coin key gift brush pencil spinner sparkler lantern envelope candy
  carrot fish banana watermelon sushi paper controller camera racket bat broom umbrella balloon
  wateringcan dumbbell. `POT` (flower-pot art), `sprout_art(0..4)` (stem centred on col 3),
  `shooting_star(f, x, y, p)`, `thought(f, x, y, w, h, c='w', edge='G', tail='left')`.
- Effects: `zzz notes rising falling sparkles orbit speech say dots_bubble thought bulb cloud rain
  sun moon confetti firework dust speedlines bubble_ring burst heartbeat progress spinner check
  cross bug ghost batwing butterfly balloon_string`.
- Glyphs: `NOTE NOTE2 HEART HEART_BIG SPARK SPARK_BIG STAR5 DROP SWEAT PUFF PUFF_S QMARK EXCL VEIN
  VEIN2 BOLT SNOW LEAF PETAL FLY`.
- Text: `say(f, info, 'HI')` speech bubble sized to text; `cjk(f, '加油', x, y, c)` 12-px Chinese
  (SimSun bitmaps, Windows); `sign(f, x, y, '加油!', c, edge, tc)` held-up board.

## 5. kit.py

`ACTIONS[name](t, n, opts) -> (pose, transform)`; `ACT_DEFAULT[name] = (frames, ms)`.
Actions: still idle bob hop jump walk walkr walkl scuttle run wave wave2 cheer dance groove spin
shake tremble nod no look sleep sit stretch jelly lean float bounce flip roll stomp bow clap shrug
peek pop pace zoomies wobble sway salute point hide type lift swim faint moonwalk tiptoe.

`S(f, t, n, act='idle', eyes=, hat=, face=, item=, item_l=, fx=[...], say='HI|YO', body=,
mouth=, blush=, view=, la=, ra=, tf=, extra=fn(L,t,n,info), back=fn(f,t,n))` composes an action
with props and `FX` effects (zzz notes hearts sparkle sweat sweat2 steam vein dizzy question
exclaim dots bulb rain sun snow snowbig confetti fireworks bubbles dust speed shine bolt rainbow
code binary loading leaves petals night bats ghosts flies coins butterfly heartbeig stars).
Good for quick variations; write a custom function when the motion itself is the idea.

## 6. Backdrops and output

- `Dotted(dark=True)` — video-style dotted line-art room: `line rect fill(step) ring dot`
  (logical coords, floats ok). Pass as `add(..., backdrop=d)` or `backdrop=fn(t, n)`.
- `render.py scene.py [--only slug..] [--out DIR] [--sheet [--cell 240] [--sheet-bg #hex]]
  [--bg #hex] [--scale N] [--gif --webp --mp4 --png] [--loops K]`. Sheets include the backdrop
  or `--bg`.
- `engine.save_gif(frames, path, durs)` transparent GIF; `engine.compose(frames, backdrop, bg,
  scale)` → RGBA images; `engine.save_rgb_gif(images, path, durs)`; `engine.sheet(frames, path)`.
- `gallery.py DIR` builds an `index.html` grid of every GIF in a folder (light/dark/checker
  background toggle, search).
