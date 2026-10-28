# Clawd pixel style — the rules

Distilled from the four reference GIFs (`assets/refs/1-4.gif`, not in the public repo) and ~30 hours of the reference
"lo-fi Clawd" videos, de-duplicated and measured cell by cell. The engine already encodes all of
this; read it so the scenes you write *move* the way the references do.

## Contents
1. Canvas and scale
2. Anatomy (front view)
3. Pseudo-3D: turned views, tilt, top face
4. Eyes and expressions
5. Colour palette
6. Props and effects
7. Motion and timing
8. Backdrops (video rooms)
9. Things that break the style

---

## 1. Canvas and scale

- Logical grid **40×40**, one logical pixel = **12 screen px** → 480×480 output, exactly like the
  reference GIFs. Transparent background by default.
- In the reference videos (1080p) one logical pixel measures **13.9 px**; the grid is perfectly
  regular, so frames can be turned back into cells with `scripts/pixelize.py`.
- Ground: first row under the feet is **y = 36**. Default body top-left is **(12, 21)**, centred.
- Everything — Clawd, props, effects, text — lives on the same grid. No finer detail anywhere
  (the dotted backdrops are the one exception, see §8).

## 2. Anatomy (front view)

```
.....OOOOOOOOOOOOOOOO.....   body 16 wide x 12 tall, flat orange, no outline
.....OOOOOOOOOOOOOOOO.....
.....OOKKOOOOOOOOKKOO.....   eyes 2x2 black, cols 2-3 and 12-13, rows 2-3
.....OOKKOOOOOOOOKKOO.....
.OOOOOOOOOOOOOOOOOOOOOOOO.   arms 4x4 blocks on both sides, rows 4-7 (total width 24)
.OOOOOOOOOOOOOOOOOOOOOOOO.
.OOOOOOOOOOOOOOOOOOOOOOOO.
.OOOOOOOOOOOOOOOOOOOOOOOO.
.....OOOOOOOOOOOOOOOO.....
.....OOOOOOOOOOOOOOOO.....
.....OOOOOOOOOOOOOOOO.....
.....OOOOOOOOOOOOOOOO.....
.....OO..OO....OO..OO.....   4 legs, 2 wide, at cols 0,4,10,14 (gaps 2/4/2)
.....OO..OO....OO..OO.....   3 tall in the GIFs (the videos use 4)
.....OO..OO....OO..OO.....
```

- **No mouth, ever.** The references never show one, and the user rejected a batch where mouths
  appeared. Eating = food reaching the front edge of the face and disappearing in bites, with a
  chewing bob; singing = notes; shouting = a bubble or "!" — never a mouth. Also no blush, nose,
  teeth, tongue, eye whites or coloured eyes.
- Clawd has stubby rectangular arms, **not pincers**. Never draw claws.
- Raised arm (`up`): a 3×7 bar along the body side sticking 3 px above the head.

## 3. Pseudo-3D

The references fake depth with exactly three tricks. Shade colour `o` (#C57047) is only ever a
*face you can see because Clawd turned or you look from above* — never an outline or a shadow.

### 3a. Turned views (yaw)

Measured from the video (soccer, walking, desk, building-site loops). Drawn facing right; the
left-facing views are exact mirror images.

**3/4 turn — `qr` / `ql`**
```
.....ooOOOOOOOOOOOOOO..   2-col side face at the BACK edge (the side you can now see)
.....ooOOOOOOOOOOOOOO..
.....ooOOKKOOOOOOOKKO..   far eye moves in 2 cols, near eye 1 col -> the gap shrinks
.....ooOOKKOOOOOOOKKO..   (perspective squeeze), near eye ends 1 col from the edge
.ooOOOOOOOOOOOOOOOOOO..   far arm still sticks out; its OUTER half is shaded and its root
.ooOOOOOOOOOOOOOOOOOOO.   covers the side face in orange (arm is in front of that face)
.ooOOOOOOOOOOOOOOOOOOO.   near arm hides behind the body: just a 1-px nub
.ooOOOOOOOOOOOOOOOOOO..
.....ooOOOOOOOOOOOOOO..
......oO..OO..OO..OO...   legs spread EVENLY (cols 1,5,9,13); back leg's outer col shaded
```

**Strong 3/4 — `q2r` / `q2l`** (desk, building site, walking)
```
....oooOOOOOOOOOOOOO.....   3-col side face
....oooOOOKKOOOOOOKK.....   eyes at cols 6-7 and ON the front edge; a wider glyph gets clipped
.oooOOOOOOOOOOOOOOOO.....   far arm = 3 shaded cols, root in orange over the side face
.oooOOOOOOOOOOOOOOOOOOO..   near arm reaches forward-low (typing, holding)
.oooOOOOOOOOOOOOOOOOOOOo.
....oooOOOOOOOOOOOOOOOOo.
....oo..OO....OO..OO.....   back leg fully shaded, others keep the front spacing
```

**Profile — `sr` / `sl`**: body 10 wide, 1-col shaded back edge, one eye on the front edge,
arm points forward as `oOO` (shade + 2), two legs visible.

**Back — `back`**: front silhouette, no eyes.

Turning on the spot = `front → qr → q2r → sr → back → sl → q2l → ql → front`, one view per frame
or two. Walking/travelling uses `q2r`/`qr` facing the direction of travel.

### 3b. Tilt (looking up / leaning back) — `tilt=1`

In reference GIFs 1, 2 and 3 (blowing a bubble, chatting over tea, the light-bulb idea) the near
half of the head is **1 px taller** and the **near eye sits 1 px higher** than the far eye. That
little step is what makes those poses feel alive. Use it whenever Clawd looks up, blows, sings,
is proud, has an idea. Only in turned views.

A raised near arm in a turned view (`ra='up'`, reference 3) pops up **over the front of the head**
as a 4×3 block with its underside shaded — not out of the body side.

### 3c. Top face — `top=True`

A 1-row shade band across the top = seen from slightly above. Used when Clawd nods/bows (the head
dips towards the camera) and when it turns away (reference 2, second half). Pair it with the body
1 px shorter (`y+1, h-1`) so the top really dips.

## 4. Eyes and expressions

Eyes carry all the emotion — keep them 2–4 px and black. Common glyphs (`engine.EYES`):

| glyph | look | used for |
|---|---|---|
| `normal` | 2×2 square | default |
| `blink` | 2×1 low | one frame every ~2 s (`n-3` in an 8-frame idle) |
| `closed` | 3×1 line | content, sipping, eyes shut (reference 2) |
| `happy` | `^` | joy, cheering |
| `down` | `v`/`‿` | blissful (headphones in the video) |
| `focus` | 4-wide bar + 2×1 pupil toward the facing side | concentrating (reference 4) |
| `angry` / `worried` / `sad` | slanted bars | moods |
| `big`, `wide`, `googly`, `x`, `squint` (`> <`), `heart`, `star`, `tear`, `cry`, `half`, `dot` | | reactions |

- **Front view** mirrors the right eye so expressions are symmetric.
- **Turned views do not mirror**: both eyes use the same glyph, pointing where Clawd faces
  (reference 4: both pupil blocks sit on the right when Clawd faces right).
- Looking around = `look=±1` (shift both eyes) or a turned view; looking up/down = `lookv=±1`.
- No blush, no hearts/stars as eyes: put hearts/stars/sparkles *next to* the head instead.
  `engine.EYE_ALIASES` maps retired glyph names (shine, heart, star, googly, wide, tear, cry,
  half, dollar) to reference ones so old scenes still render in style.

## 5. Colour palette

| key | hex | role |
|---|---|---|
| `O` | #E37E52 | Clawd body |
| `o` | #C57047 | side/top faces, far limbs |
| `K` | #000000 | eyes |
| `B` | #6699D0 | speech bubble (reference 2) |
| `V` | #2C5896 | headphones (video) |
| `Y` / `y` / `U` | #F3B34F / #FAD898 / #FFE25C | light bulb, music notes, sparks |
| `L` | #C8C6D6 | soap bubbles, smoke |
| `M` | #562731 | bubble wand (reference 1) |
| `b` | #383E81 | fidget spinner (reference 4), books |
| `m` | #8C1E2D | reading glasses (video) |
| `W` `w` `G` `g` `k` | whites/greys/soft black | props |
| `R Z r P p E e N n S C F T H` | | red, heart pink, pink, purples, greens, browns, sky, cyan, flame, cream, blush |

Clawd stays orange. Tints (cold blue, ghost white…) are an effect, not a new character.

## 6. Props and effects

- Same 12-px grid. Hand-held things 3–7 px; hats 7–18 px wide; the video chef hat is 18×8 and
  covers the whole head width; headphones have a band 4 rows above the head and 3×5 cups on the
  top corners; the astronaut helmet is a thin grey ellipse with a collar line through the body.
- Props attach to `info['rh']` / `info['lh']` (screen-right/left hand points) or `info['head']`.
- White props get a grey (`G`/`g`) edge; very dark props get a lighter highlight — the GIFs are
  transparent and must read on white and on dark chat backgrounds.
- **Speech bubble** (reference 2): solid blue, corners cut by 1 px, stair-step tail 3→2→1 px,
  black dots appear one per beat.
- **Light bulb** (reference 3): yellow glass with white highlight, grey screw base, flickers off
  one frame in four, a few yellow rays when lit.
- **Soap bubbles** (reference 1): lavender 1-px rings with a white glint, drift up, pop into
  4–6 scattered dots.
- Music notes: yellow (guitar, video) or navy (headphones, video); drift up, 2–3 at a time.
- Sparkles: 3×3 plus `.W./WUW/.W.` twinkling through `+ → dot → off`.
- **Anything that belongs to the eyes is anchored to the eyes the engine drew** (`info['eyes']`,
  which follows the view: 3/4 views move the far eye 2 cols and the near eye 1, q2r/q2l put the
  near eye on the front edge, profile shows one eye). Tears start *at* an eye and run down the
  cheek or spray out of it (`props.tear`, `props.tear_spray`) — never float beside the body at
  eye height. A telescope/spyglass eyepiece touches the eye it looks through (turn Clawd to
  `q2r`/`q2l` so that eye is on the front edge). Glasses/shades lenses sit on the eyes in every
  view (`props.face` does this). A wink's sparkle pops off the winking eye's corner. For a layer
  that is flipped/rotated afterwards, find the eyes in the transformed layer (black pixels).

## 7. Motion and timing

- Move in whole logical pixels. 1 px is already a big move at this scale.
- Idle: body top drops 1 px (`y+1, h-1`) for ~3 of 8 frames; blink once.
- Squash on take-off/landing: `w=18, h=10..11, x-1, y+1..2`. Stretch at the top of a jump
  (video "jump up" pose): `w=14, h=14..15`, both arms `up`.
- Jumps 4–12 px; shorten the legs (`legs=(1,1,1,1)`) while airborne.
- Walk: legs alternate `(1,0,1,0)` / `(0,1,0,1)` with a 1-px body bob, 2–3 px of travel per frame,
  in a turned view facing the travel direction (video).
- Lean/sway/head-bang: `Canvas.shear()` (±0.06…0.18). Spins/tumbles: `rot90` in 90° steps.
  Arbitrary-angle `rotate()` shreds the pixels — don't use it on Clawd.
- Frame time 80–220 ms. The reference GIFs use 200 ms per frame (first frame 100 ms); lively
  actions 80–120 ms; sleepy/idle 180–220 ms.
- Loops must be seamless; 4–32 frames is the sweet spot.

### 7a. Story beats must be readable (timing rule)

The user could not tell what Clawd was doing in GIFs where a whole story (run → leap → hit the
wall → fall → get up) played at one flat 80–110 ms per frame: every key pose flashed past once
per loop, and some actions snapped from one pose to the next with nothing in between. Repetition
hides this in cycles (a walk or a wave is seen many times per loop); a story is seen once.

- **Hold the key poses.** Anticipation (crouch, wind-up, deep breath) ~200–300 ms; the contact /
  impact / reveal frame (BONK, CRACK, CHOO!, GO!, the catch, the dunk, the costume reveal)
  300–450 ms; the result (lying dizzy, YES!, landed) 300–600 ms in total. Travel and in-between
  frames stay 70–120 ms. Use `beats(n, ms, {frame: ms})` rather than one flat `dur`.
- **Never snap at a turning point; transitions can be fast but must exist.** Where one action
  turns into another — jump → land, stand → lie down, front → turn away, arms down → arms up
  mid-story, crouch → leap — put at least one in-between (60–100 ms): views step round
  `front qr q2r sr back`, arms pass `side → mid → high → up`, squash/stretch passes through an
  in-between size. `add_tweened(..., tw_at={k: 1})` does this from the poses of frames k and k+1.
- **Only at turning points.** Don't put in-betweens into simple loops and snappy beats — blinks,
  typing, eye-glyph swaps, bobbing, walk/run arm swings, dance moves, a pop-in, a teleport, a
  jump-scare BOO, the quick comic hit itself. Smoothing those makes them look floaty and odd.
  The reference jump is pose-to-pose (squash 1 frame → stretch at the apex → squash on landing);
  keep that, just don't let a multi-stage story switch actions with no frame between.
- A `rot90` tumble can't be in-betweened by rotation (no arbitrary angles): lean with `shear` or
  hold the poses either side ~150–250 ms instead.
- Check it: count how long each distinct stage is on screen in the final GIF (Pillow merges
  identical frames). Any stage of a story under ~250 ms, or two different actions in consecutive
  frames, needs a hold or an in-between.

## 8. Backdrops (video rooms)

The videos place Clawd in rooms drawn as **thin line-art made of small square dots** (3 dots per
Clawd pixel), grey on near-black (#141414, videos 1–2, night) or light grey on off-white
(#F2F0EA, video 3, day). Furniture is outlines plus sparse halftone fills; nothing is coloured
except Clawd and his props. Use `engine.Dotted` for this, only when the user wants a scene/room
or a video; plain GIFs stay transparent.

## 9. Things that break the style

Outlines around Clawd · gradients or anti-aliasing · sub-pixel detail · pincers/claws · a mouth
on every frame · mirrored expressions in turned views · shading used as a drop shadow ·
arbitrary-angle rotation of Clawd · props drawn at a finer resolution than Clawd · recolouring
Clawd as a different character · copyrighted characters' likeness.
