---
name: clawd-halftone
description: "Make backdrops — rooms, interiors, landscapes, skies, streets, vehicles, scenery layers — in the exact dotted halftone style of the lo-fi Clawd (Claude Code mascot) videos: a precise front-on grayscale illustration seen through a 9-px screen of round dots whose size carries the tone, night theme (#131313 ground, light dots) or day theme (#f4f2ec cream, dark ink). Use it whenever a Clawd video, short film, promo, scene, room, set, background, backdrop or environment is needed — even if the user only says 背景 / 场景 / 房间 / 画面 / 环境 for a Clawd film. Not for the transparent Clawd GIFs/stickers themselves: never add backdrops to those unless the user asks."
---

# Clawd halftone backdrops

The videos' backdrops are **precise flat illustrations, front-on, seen through a halftone screen**:
one round dot per 9 x 9 px cell, the dot's size following the picture's tone. Draw the illustration
as an **SVG at screen size**, then `scripts/svg2dots.py` turns it into dots exactly like the videos
(each cell averages the 9 x 9 px under it, so shape edges get smaller dots — the smooth contours).

What the user wants, in their words: 视频动画里的那种细节，精度 — "the detail and precision of the
video animation, so it looks like a refined animation". What they rejected on the way:
- dotted outline line-art rooms → 粗糙、细致度低、没有明暗关系 (rough, low detail, no light and shade)
- flat uniform fills → 太单调 (monotonous); they want 明暗、远近、粗细 (light/shade, near/far, thick/thin)
- an oblique 2.5D box trick → 不要斜向 (no slanted faces)
- a perspective three.js render → 太细节太立体了，仿照视频 (too 3D, imitate the video)

## Non-negotiable (measured on the videos)

- **Front-on.** No perspective, no oblique side faces. Depth comes from overlap, tone and line weight.
- **Round dots on a 9-px grid**, 213 x 120 cells per frame, **dot area ∝ tone** (diameter 4.7·√v px,
  measured). Never draw dots yourself — draw greys, let svg2dots screen them.
- **Tone budget: ~5 levels survive** — 0 · .1 · .3 · .6 · 1 (`svgkit.L`); differences under ~.15
  vanish. Night rooms use 0 (walls) · .09 (far) · .19 (floor, thin frames) · .3 (curtains, stone) ·
  .85 (the key objects); day rooms paper · .18 (floor) · .25 (panels) · .38 (sun, lines) · .95 (the
  dense plant, a chair seat). Full tables: references/style.md §2.
- **Palettes**: night ground #131313 with dots ≈ #dddad7; day cream #f4f2ec with ink ≈ #0c0a05.
  No colour in backdrops — colour belongs to Clawd and his props.
- **Precision**: crisp rows/columns sit exactly on cells (y = 9k..9k+9: `row/col/frame`); details and
  gaps ≥ 1 cell, lines ≥ 6 px; a near shape gets a 1-cell margin of ground/paper so it separates from
  what is behind (`with s.cut():`). Text as bitmap glyphs (`bitmap_text`, `seg7`), never SVG text.
- **Fill, then carve**: walls and sky stay 0; objects are filled fields whose structure is carved out
  as 1-cell gaps (insets, joints, window surrounds, stripes) — the kitchen/fireplace way. An uncarved
  big field reads as grey noise; bare outlines read as line art.
- **Edges**: objects are stair-stepped sets of whole cells with full dots to the edge
  (`scripts/cellkit.py`); the soft averaged edge of plain SVG is for big soft things only. Objects
  ≥ ~7 cells; parts that differ by ≤ .15 or sit within 2 cells merge.
- **Light and shade**: one light direction; rounded things shade as a **hard step** (a ~30 % band one
  level heavier: `cyl`, `pot`, `cellkit.lump_shade`, leaves lit/dark at the midrib); smooth gradients
  only for big soft things (clouds, ground). Light sources crisp, their glows tiny; carve after glows.
- **Judge at 1:1.** Shrunk views make dots look smaller and fainter; the tone tables match the
  renderer within 0.05 px at 1:1.
- **Near/far and hierarchy**: far planes ≤ .25 and simple (`with s.plane(op=…)`), near planes denser
  with heavier outlines; one or two key objects at the top level, everything else at least a level
  lower.
- **Detail like the videos**: 10–15 objects per screen, each with 2–4 inner details, air between
  shapes — not lumps.
- **Leave Clawd a stage**: where he acts, keep the backdrop quiet (paper / empty). Standing Clawd's
  feet sit at y ≈ 975 px; he is 224 px wide (16 Clawd px x 14).

## Workflow

1. **Look first.** Open `assets/refs/*.png` (1080p frames; not shipped in the public repo, see below) and crop the kind of object you are about
   to draw at full size. Read `references/style.md` (tones, object recipes, depth).
2. **Block** the scene in screen px: what is near/mid/far, where the light comes from, Clawd's stage.
3. **Compose on cells** with `scripts/cellcanvas.py` (the recommended way, from the round-3 test that
   gave the best results): masks in px → cells (`R rrect circ ell poly line edge grow shrink shift
   below right_of cols_every rows_every checker`), a `Canvas(theme)` with `put carve cut obj lift glow
   text seg7`, `save(name, ref)` renders through svg2dots into ./scenes. Study `examples/round3/*.py`.
   Or draw free SVG with `scripts/svgkit.py` (read its docstring): `Svg(theme)`, `ink(v)` and the
   `L` levels; grid pieces `row col frame panel snap shift`; `plane cut blend glow`; objects `leaf pot
   cyl cloud canopy tuft sun moon skyline`; text `bitmap_text seg7`. For objects with curved
   silhouettes, `scripts/cellkit.py`: `cell_mask` / `cells` / `CellPaint` (cell-exact fills, -1 =
   carve), `lump_shade`, `outline_mask`, `top_edge_mask`, `dilate`, `gap`, `checker`, `star`.
   style.md §5 has recipes (train side, platform, lantern, sofa, rug, trees, hills, clouds).
4. **Render**: `python scripts/svg2dots.py scene.svg out.png --theme light|dark --debug` — the debug
   sheet puts the raster before the screen next to the dots. A raster that looks great can still fail
   as dots: judge the dots.
5. **Compare at full size**: `python scripts/compare.py out.png --ref <assets/refs/frame.png | ref_map name>`
   (it shows both value maps too), then crop the same kind of object from both at 1:1. Check tones (dot sizes), outline rows, gaps,
   shading direction, far planes lighter. Iterate until a viewer could not tell which is which.
6. **Films**: references/film.md (layers, windows, parallax, live screen in an HTML comp).

## Files

- `scripts/svg2dots.py` — SVG → value map → round-dot halftone (the main path)
- `scripts/svgkit.py` — SVG helpers: levels, grid pieces, planes, cut, blend, glow, objects, text
- `scripts/cellkit.py` — cell-exact masks and fills (stair-stepped silhouettes, carving, lump shading)
- `scripts/halftone.py` — the calibrated screen (`render`), and study tools (`dehalf`, `fit`, `round`)
- `scripts/paint.py` — older cell-grid painter (value maps directly on cells), still usable
- `scripts/compare.py` — side-by-side with a reference frame or recovered map
- `scripts/halftone_runtime.js` — the same screen live in an HTML comp
- `references/style.md` — measured tones, how each kind of object is drawn, depth, themes
- `references/film.md` — films: layers, windows, parallax, comps
- `references/ref_maps/` — recovered value maps of the reference rooms (not shipped publicly)
- `assets/refs/` — **not included in the public repo** (they are frames of Anthropic's lo-fi Clawd
  videos). Save your own 1080p screenshots of those videos here under these names; `compare.py` and
  style.md §7 refer to them. Reference frames named by room (night: study, fireplace, music room, kitchen,
  bedroom/disco, space; day: patio, building site, hill + clouds, pool, disco); style.md §7 says what
  each one shows
- `examples/patio_day.py` (SVG, day) → `examples/out/`
- `examples/round3/` — the best test run (cellcanvas): `carriage_night.py` (night interior, two
  windows on a moonlit lake, lamp vs moonlight), `station_night.py`, `home_day.py`, `park_day.py`;
  renders in `round3/out/`
- `scripts/cellcanvas.py` — the cell-exact value canvas (recommended)
- `examples/promo_day/` (beach, kitchen, sports ground, bedroom) and `examples/promo_night/`
  (lounge, office, stage, snowy street — all drawn in the day theme) — light-theme scenes with a calm
  centre for a GIF/Clawd to play in (`*_square.png` shows the calm zone); renders in `scenes/`
- `examples/round2/` — an earlier test run: `station_night.py` (carved train side,
  lit windows, lanterns, clock, sign), `home_day.py` (bookshelf, sofa, rug, plants, window),
  `park_day.py` (cell-level trees, layered hills, clouds, tufts); renders in `round2/out/`
- `examples/fireplace_room.py` — older cell-grid painter example (night)
