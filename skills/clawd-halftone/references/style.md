# What the reference backdrops are made of

Measured at 1:1 on video 1–2 (night rooms) and video 3 (day rooms). Frames: `../assets/refs/` (not in the public repo)
(named by room). Recovered value maps: `ref_maps/`.

## Contents
1. The screen and the tone budget
2. Measured tones (night, day)
3. Precision rules (grid, minimum sizes, separation)
4. Light, shade and depth (front-on)
5. Object recipes
6. Scale and composition around Clawd
7. Which reference has what
8. Failure modes (from the test rounds)

## 1. The screen and the tone budget

- 9 px pitch, round dots centred in their cell, one colour; **dot area ∝ tone**: diameter = 4.7·√v px.
- Only ~5 tones survive: **0 (no dot) · .1 (1.5 px) · .3 (2.6 px) · .6 (3.6 px) · 1 (4.7 px)**, plus
  .2 / .45 in between at most. Differences under ~.15 vanish; above ~.85 everything looks the same.
  Design in these levels (`svgkit.L`).
- svg2dots averages each 9 x 9 cell: an edge that cuts a cell makes a smaller dot (smooth contours).

## 2. Measured tones

Night rooms (light dots on #131313):

| level | value (diameter) | objects |
|---|---|---|
| far | .09 (1.4 px) | the tree/plant seen through a window, far silhouettes |
| floor / thin frames | .19 (2.1 px) | floor slats, window frame lines, faint glow edges |
| bodies | .28–.31 (2.5–2.6 px) | curtains, fireplace stone, picture frames, wall rail |
| mid | .42 (3 px) | a guitar, secondary furniture |
| key | .85 (4.3 px) | the armchair, desk, piano, shelf objects, flames — the room's subjects |
| walls | 0 | always empty |

Day rooms (dark ink on #f4f2ec):

| level | value (diameter) | objects |
|---|---|---|
| floor band | .18 (2.0 px) | full-width band at the bottom |
| panels | .23–.27 (2.2–2.5 px) | pot rims, desk/cabinet doors |
| lines, sun | .35–.4 (2.8–2.9 px) | window frame line, the sun disc, pot bodies |
| far city | ~.22, ~30 % of the area | rectangles with window gaps, behind everything |
| dense | .92–.96 (4.5 px) | the dark plant, a chair seat |
| sky / walls | 0 | paper |

## 3. Precision rules

- **Grid**: cells start at (0, 0); a crisp row/column of dots must cover whole cells (y = 9k..9k+9).
  A stroke centred on a cell edge becomes two half-size rows. Use `row/col/frame`, snap coordinates.
- **Minimum sizes**: details and gaps ≥ 1 cell (9 px), lines ≥ 6 px, objects ≥ 5 cells. Veins,
  notches, clock hands, dashes thinner than that disappear.
- **Separation**: near over far reads only with a 1-cell margin of ground/paper around the near
  shape (`with s.cut():`, leaf `air=`). This is the overlap rule for everything, not only leaves.
- **Fill, then carve.** Walls stay 0, but an *object* may be a big field (a cabinet, a train side, a
  fireplace) as long as its structure is carved out of it as 1-cell gaps (insets, joints, window
  surrounds, stripes) — that is how the kitchen and fireplace frames draw. An *uncarved* big field
  (.18–.3 over a wall, a platform, the sky) reads as grey noise; pure outlines read as line art (both
  rejected). Carve after any glow so the gaps stay dark inside the light. Day: sky/walls paper, the
  floor band the only full-width field.
- **Edges**: objects are stair-stepped sets of whole cells with full dots right up to the edge
  (`cellkit.cell_mask` + `cells`/`CellPaint`). svg2dots' averaging rims curved SVG edges with small
  dots — right only for big soft things (clouds, glows, ground).
- **Merging**: parts whose tones differ by ≤ .15 merge into one lump; two objects within 2 cells of
  each other merge. Separate with a level step or a 1-cell gap.
- **Minimum object size ~7 cells** (a cup, a tag, a lantern): at 4–5 cells things become blobs.
- **Hierarchy**: one or two key objects at the key level; everything else at least one level lower.
- **Text**: bitmap glyphs, one glyph pixel per cell (`bitmap_text`), clock digits `seg7`. SVG text
  becomes mush.

## 4. Light, shade and depth (front-on)

- **No perspective, no oblique faces.** Depth = overlap + tone + line weight.
- **Rounded things: a hard step**, not a smooth ramp: a band ~30 % of the width one level heavier
  on the side away from the light (`cyl`, `pot`); leaves split lit/dark at the midrib (step ≥ .2).
  Smooth gradients only for big soft things (clouds denser at the bottom, ground denser toward the
  viewer, glows).
- **Lights**: the source crisp (a cell-mask lantern or bulb at the key level, a ring halo for the
  moon), the glow tiny (r ~80 px, ~.15) and blended; a pool of light as a stepped ellipse or a small
  elliptical glow; dark/empty around. Big soft glows read as cloudy smears and swallow the source
  (only a big fire carries one). Clip the glow element itself; never put a blended element inside a
  clipped group (it paints black).
- **Near/far**: far planes ≤ .25, simpler, no outlines (`with s.plane(op=…)`); near planes denser
  with the heaviest outlines.

## 5. Object recipes

- **Window**: a one-cell frame line, mullions the same; outside empty (night) / paper (day) with a far
  view (city .22 with gaps, a FAINT tree, the moon or sun); curtains either side (bodies level, fold
  lines as 1-cell gaps).
- **Plants**: `pot` (rim band, tapering body, rounded bottom, one-cell outline, hard shade band); stems
  ≥ 7 px; `leaf` with lit/dark halves, 6-px midrib, `air` between leaves; a dark tall plant at the
  dense level; a broad-leaf plant lighter.
- **Furniture**: front-on silhouettes, key piece at the key level (night) / dense (day); panels and
  drawers as `panel`/`frame` with knobs ≥ 1 cell; legs ≥ 1 cell wide.
- **Floor band**: rows from y ≈ 981 down, .18–.19, with slats or nothing.
- **Sky**: `sun` (disc .38 + 2-dot ray dashes), `moon` (bright disc + ring halo), clouds with a bumpy
  top of separate lumps as the densest part and a base that fades out (r3_500), `skyline` (far city).
- **Hills / ground layers**: each layer a field, separated from the next by a one-cell paper line, a
  ridge row (`cellkit.top_edge_mask`) slightly denser; nearer layers denser (r3_500).
- **Trees** (day): build the crown on cells from a few round lumps; give each lump a lit edge row on
  the light side and a darker edge on the shade side, and separate lumps with a one-cell paper gap only
  on the shade side. (`lump_shade`'s parallel diagonal bands make every lump a beach ball; a lump
  without separation merges into one blob.) Trunk as `cyl`; grass as `tuft`s and a path — never a
  uniform lawn field.
- **Train car side** (night): a .3–.35 body field (a .18 field reads as noise) with the structure
  carved (window surrounds, a stripe channel, door inset and joint, panel seams); lit windows bright
  (.6–.85) with seat backs and passengers carved as silhouettes; bogies hidden by the platform edge.
- **Platform** (night): dark, lit only by pools of light under the lamps; tile joints carved after
  the glow; a bright edge stripe row.
- **Lantern / lamp post**: a cell-mask head wider at the top, two carved glazing bars, a cap and a
  finial, the post a 1-cell column, a tiny glow (r ~80, .14).
- **Sofa**: cushions as light fields (.16–.26) with one-cell outlines; arms with the hard shade step.
- **Rug**: a dense field (~.6) with a carved border, lozenges and a fringe row — it must beat the floor band.
- **Night lights**: lamps, fire: the source at the key level, a small `glow`, dark around. A pool of
  light needs a surface to land on: front-on, a table top is only an edge row — light the top edge row
  (brightest under the lamp) and the tablecloth face below it (a soft ellipse), not the wall. Two
  lights without colour read apart by their edges: warm lamp = soft-edged pool, cold moon = a
  crisp-edged slanted patch with the window bar's shadow carved through it.
- **Moon**: a bright disc with a one-step shade, a carved gap, then a thin dotted ring halo — not a
  soft glow (that smears).
- **Curtains**: folds as vertical carved gaps (diagonal carving steps into saw teeth), tied back
  with a lit band, a valance on top.
- **Wall panelling under windows**: rails and stiles only (a few rows/columns), never a full field.
- **Clocks / digits**: `seg7` at 5 x 9 cells or larger (4 x 7 is too small to read); lit digits
  on a dark board, not dark digits carved in a light one.

## 6. Scale and composition around Clawd

Clawd 224 x 168 body (+42 legs) at 14 px per Clawd pixel; standing feet y ≈ 975. Armchair ~400 wide,
window 500–1100, door ~270 x 680, desk ~470 x 250, potted plant 230 wide and up to 800 tall, floor band
~100 tall. Keep the area behind Clawd quiet (0 / paper); key object next to or under him; busiest decor
in the outer thirds and the top third.

## 7. Which reference has what (`../assets/refs/`)

| frame | theme | objects worth studying |
|---|---|---|
| v1_180_study | night | desk + chair (thick strokes), bookshelf with objects, plant in the window (far), wall rail |
| v1_300_fireplace | night | armchair (key), curtains, window with tree + rain, fireplace bricks + fire glow, picture |
| v1_525_music_room | night | piano, guitars, speakers, window with curtains, floor slats |
| v1_12_kitchen | night | cabinets with insets, stove, sink, hanging utensils, window |
| v1_415_bedroom_disco | night | disco ball with light rays, bed, bookshelf, desk |
| v1_75_space | night | planet with shaded side, stars |
| r3_390_patio | day | plants (two kinds), pots, desk, chair, window, sun, far city |
| r3_80_building_site / v3_200 | day | girders (dense flanges), near/far buildings |
| r3_500_hill_clouds | day | clouds, hills/dunes (denser toward the viewer), a house |
| r3_715_pool | day | top-down pool, tiled border, water pattern |
| r3_15_disco_day | day | disco ball, scattered sparkles |

Measuring: the tone tables were measured as dot diameters at 1:1 and the renderer reproduces them
within 0.05 px (night .85 → 4.3 px, .3 → 2.5, .19 → 2.0, .09 → 1.5). Shrunk views make dots look
smaller and fainter than they are — judge tones only on 1:1 crops or on the value map.

## 8. Failure modes (from the test rounds)

- Uncarved mid-tone fields at night (a wall, a platform at .3) → grey noise; the cure is carving, not
  emptying (an empty train side reads as line art).
- Every object at the same level → no subject; Clawd drowns.
- A uniform lawn / ground field → monotonous; use tufts, paths, a density gradient.
- Blobby tree crowns and leaves without air → lumps; use lit caps, holes, 1-cell gaps.
- Details below a cell (thin veins, dashes, hands) → lost.
- Off-grid outlines → two rows of half dots.
- Glows over busy areas → the light disappears.
- Line art only / flat uniform fills / oblique faces / perspective → rejected by the user before.
