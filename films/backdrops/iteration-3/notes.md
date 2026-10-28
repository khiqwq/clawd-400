# Iteration 3 — notes

Scenes are in `scenes/` (svg, png, `_value`, `_debug`, `_cmp`, `_crops`); scripts next to this file.
`canvas.py` is my plumbing on top of the skill (imports `svgkit`, `cellkit`, `svg2dots.py`, `compare.py`
from the skill folder; nothing copied or edited).

How I drew: every scene is composed on the screen's cell grid (120 x 213 values) — masks built with
cellkit (`cell_mask`, `outline_mask`, `dilate`, `top_edge_mask`, `polyline_mask`, `lump_shade`, `bez`) plus a
few mask builders of my own (px box, rounded box, circle, ellipse), filled, then carved; glows are computed
on the same grid, so "carve after glow" is just the order of two lines. The grid is emitted through
`svgkit.Svg` as one crisp rect per run (`cellkit.cells`) and rendered by `svg2dots.py`, so the svg2dots
value map equals the grid exactly. Review: every render cropped at 1:1 against the reference frames
(crops in my scratch folder + the `_crops.png` deliverable), and the compare sheet's value maps for
hierarchy.

## 1. carriage_night (done first, most iterations: 9 renders)

Render: `scenes/carriage_night.png` (compare: v1_300_fireplace; crops vs fireplace window/armchair and
the study shelf objects).

What is in it: ceiling band with panel joints; luggage rack in two runs (front tube, bed rail, brackets to
wall plates) with a duffel bag + book stack on the left and a strapped suitcase (handle, buckles, lid
seam) + a ribboned hatbox on the right; a pendant lamp (rose, cord, stepped shade with a hard shade
step, bulb at 1.0, glow r 63 only); two rounded train windows (frame .55 with a carved line, gasket,
latches, sill, pelmet with a fringe); four curtains tied back with a bright tie band and tassel; outside:
moon (1.0, hard shade step, two maria) with a ring halo, cross stars, far hills .08 with a ridge row,
wooded near hills with conifers, a crisp shore row, the moon's broken reflection column, village lights
with streaks, a lighthouse with beam dashes, a sailboat, glass glints; a round wall clock at 23:55 on
the pier; wainscot as rails and stiles only; Clawd's bench (key level: .6 back with carved channels,
.85 roll/seat/arms, 1.0 lit tops), a table with a hanging scalloped tablecloth, a cup with steam, the
empty right bench a level lower (in the lamp's shadow) with two headrest covers; skirting, floor band,
a runner.

Decisions that made the difference (in order of effect):
- **Walls empty.** v1 filled the whole wall below the windows with carved .19 panelling: at 1:1 it was
  exactly the "grey noise" failure, and the benches drowned in it. The brief asks for panelling, so it is
  now only rails and stiles at .22 (like a window frame), panels empty.
- **Hierarchy by light.** With both benches at the same level nothing was the subject (the value map in
  the compare sheet showed it at once; the halftone at half size did not). Clawd's bench is under the
  lamp → key level; the empty one further away → a level lower. Same logic as the fireplace armchair.
- **Curtains beside the window, straight folds.** Curtains over the frame hid the rounded corners and
  made the window unreadable; diagonal carved fold lines became staircase jaggies that read as stripes.
  Now: wall-side edge straight, glass-side edge swept into the tie, vertical carved folds, one lit strip.
- **A surface for the light pool.** Front-on, a table top is a 1–2 row edge: a "pool of light on the
  table" had nowhere to land (v2–v5 read as a brighter segment, and the moon patch with a carved bar read
  as the digits "11"). A hanging tablecloth gives the light a face: the lamp's pool is a smooth falloff
  (.27 → .85) centred under the lamp, the top edge brightest under it; the moon's patch is a crisp slanted
  parallelogram at 1.0 at the cloth's left end, separated from the pool by base tone. Soft = lamp,
  crisp = moon is the only way to tell "warm" from "cold" without colour.
- **No soft glow around the moon.** `svgkit.moon()`'s default halo (glow r·2.2 at .25) and my own r 160
  glow both read as a grey smear disc at 1:1; a one-cell ring at r 66 (.3) + a faint checker ring
  outside reads as a halo.
- Small objects needed redrawing at cell level 2–3 times: the suitcase read as a radio until it became one
  .6 field with carved strap gaps + a handle arch; a framed picture on the pier read as a TV and a hat as a
  bell (both dropped); a scarf read as a magnet (dropped); the round clock reads.

For the film: the outside (glass mask `GLASS`) should become its own scrolling layer (sky/moon fixed,
hills slow, shore + water faster); the lamp pool and the moon patch are separate lifts and could be
their own additive layers (film.md "Layers").

Stage check (orange stand-in, `stand_in()` in canvas.py): body x 110–335 sits on the cushion top at
y 840, framed by the backrest and arms, the table top at mid-body height to his right.

## Skill feedback (so far)

- **Wanted: a value canvas on cells.** `cellkit.CellPaint` is half of it. What I needed in every scene:
  px → cell mask builders (box, rounded box, circle, ellipse — `circle_mask` exists, the rest don't),
  `put / carve / lift / cut(margin)` on one array, a cell-level `glow` (screen-blended), text and seg7 on
  cells, then one `emit`. With SVG glows + carving, "carve after glow" means emitting in three passes;
  on an array it is two lines. canvas.py is that helper (~150 lines) if you want to fold it in.
- **cellkit vs svg2dots grid size:** cellkit masks are 120 x 213; svg2dots' value map is 120 x 214 (it
  pads the partial last column). Harmless, but it trips array comparisons.
- **`moon()` default halo contradicts the skill's own glow rule** (big soft glows = smear). Suggest a ring
  halo (one cell at ~1.8 r) as the default and the soft glow optional and small.
- **Missing recipe: light on a front-on table.** Say that a table top is an edge-on band, so a pool of
  light needs a vertical receiving face (tablecloth, apron, a wall behind) and that soft vs crisp edges are
  what distinguish two light sources in grey.
- **Curtain recipe:** "fold lines as 1-cell gaps" — add "straight and vertical"; diagonal 1-cell carved
  lines staircase into jaggies. Also: hang curtains beside the frame, not over it.
- **The compare sheet's value maps were the most useful hierarchy check**; worth saying in SKILL.md
  step 5 that hierarchy is judged on the value maps (the half-size halftones flatten it), tones on 1:1.
- **Key-object guidance:** "one or two key objects" — add that it should be what Clawd uses (his seat,
  his desk), and that a duplicate object (the second bench) goes a level lower with a light reason.

## 2. station_night (6 renders; started from examples/round2/station_night.py)

Render: `scenes/station_night.png` (compare: v1_12_kitchen; crops vs the kitchen cabinets, the bedroom
bookshelf objects, the fireplace).

What changed against round 2 (which I re-cropped at 1:1 first): there the car body was a .18 field over
half the frame (noise), the lit windows read as dark "门" shapes, the lamp heads sat against the canopy
and vanished, the platform was a uniform textured field, everything was at one level.
- **Car side like the kitchen cabinets:** one body field (.34) with the structure carved out of it —
  1-cell window surrounds, a 4-row livery channel with a .85 stripe in it, panel seams under the piers,
  skirt seam, underframe slots, the door as an inset (carved channel) with leaves a level brighter.
  I tried two alternatives first: body at 0 lit only near the lamps by a big glow (the glow's soft edge is
  the "smear" failure), and the round-2 .2 field (noise). The .34 field reads as a deliberate texture, a
  .2 field does not.
- **Lit windows that read lit:** a .8 pane with only a rack line near the top and the seat backs as a
  2-row carved band along the bottom with two headrest bumps; two windows have a passenger (head +
  shoulders) rising from the band. Big carved seat backs (round 2, my v1/v2) turn every window into 门.
- **Lamp heads against the sky:** tall posts so the lanterns (1.0, two carved glazing bars, cap, finial,
  glow r 90 .16) sit over the dark skyline, not over the canopy or the lit windows.
- **Platform dark, light only in the pools:** the surface is 0; each pool is an ellipse with a crisp rim
  and a smooth rise toward the post (.12 → .42), tile joints carved after it (rows wider toward the
  viewer, staggered verticals). Smooth glows looked like smoke, three hard steps looked like rugs; crisp
  rim + smooth inside reads as light on tiles. Clawd's feet (x 260–485, y 975) are in the left pool.
- **Text:** bright 12-px SimSun glyphs on a dark face read cleanly; dark glyphs carved into a lit face
  (a lightbox look) are mush at 12 px and busy at 14–16 (tested all four, scratch). Clock digits seg7 at
  w 5 x h 9 cells with ghost segments .1 read "23:59"; at the default 4 x 7 the colon and 5 read weakly.
- Kept from round 2: skyline recipe (towers .1, crisp top row, sparse lit windows, antennas), canopy
  fascia + dagger valance, the bench. Added: crescent moon, small lamps under the far canopy, roof vents,
  gangway + the next car, destination board over the door, the car number. Dropped a litter bin that
  crowded the right lamp post.

Skill feedback from this scene:
- **seg7 default size (4 x 7) is too small for a station clock;** document a size table (4x7 small
  read-out, 5x9 a wall clock).
- **bitmap_text:** say that lettering should be bright on a dark face; carved (dark) glyphs need ≥ 16 px
  and still look busy. Also: the font path is hard-coded (simsun.ttc) with no fallback.
- **"Train car side" recipe says .18 body field** — that is below where a field reads as texture; .3–.35
  (like the kitchen cabinets) worked, .18–.2 read as noise both in round 2 and in my v2.
- Wanted: an `ellipse pool` helper (crisp rim + inner falloff) — the skill offers only `glow` (soft
  edge) or "a stepped ellipse" in prose.

## 3. home_day (8 renders; started from examples/round2/home_day.py's layout)

Render: `scenes/home_day.png` (compare: r3_390_patio; crops vs the patio's right plant, its window, its
pot + chair).

What changed against round 2 (re-cropped at 1:1 first: soft SVG-averaged leaf edges, a faint pot, a weak
rug, a pilea that read as a cluster of blobs, books that faded into the shelf):
- Everything is cell-exact now (`daykit.py`: `leaf` = svgkit.leaf's outline on cells with the lit half
  facing the upper left, `pot` = svgkit.pot on cells). Leaves have dense dots right up to a stepped edge,
  like r3_390.
- **No carved midrib on dense leaves.** With the 1-cell carved midrib the bird-of-paradise leaves split
  into two thin strips at 1:1; the ref shows lit/dark halves with no gap. lit .5 vs dark .95 (the skill
  says lit .36 for SVG leaves; on cells .5 reads better against .95).
- **Depth inside the big plant:** a layer of lighter leaves (.32/.2, no air) behind the dense ones, the
  way r3_390 puts a lighter plant behind the dark one.
- Bookshelf frame and boards dense (.92) with a lit front edge row; book spines carved only near the top;
  the pilea became a cactus with a flower (reads at once); the rug is taller (.7, carved border line, a
  dotted dense band, carved lozenges with dense eyes, fringe) so it beats the floor band.
- Far city fainter (.18) and lower so the window reads as sky with a city at the sill.
- Tried and dropped: a succulent on the sill (a blob against the city) and a hanging plant in front of the
  window (three versions: small leaves at 5–7 cells and lumps of r 18–27 px read as beads on strings, not
  foliage; the study ref's hanging plant works because it is ~250 px of lumps). Dropped rather than ship it.

Skill feedback from this scene:
- **`leaf()` notes:** say that the midrib gap is for big lit leaves (≥ 12 cells wide) only, and that leaves
  under ~8 cells long become blobs; small foliage needs lumps (cellkit.lump_shade) at r ≥ 30 px.
- Wanted: `leaf` and `pot` in cellkit (cell-exact versions); every day object ended up needing them.
- The light-theme value of "lit" halves (.36 in svgkit.leaf) is too close to paper next to dense .95
  leaves on cells; .5 holds the shape.

## 4. park_day (8 renders; started from examples/round2/park_day.py)

Render: `scenes/park_day.png` (compare: r3_500_hill_clouds; crops vs its cloud and hills, and the patio
plant for foliage).

What changed against round 2 (re-cropped at 1:1 first: crowns as messy patches, a meadow so dense that
the bench and tufts merged into it, a dense band under the path, one smooth mound per cloud):
- **Light from the sun's side.** The sun is upper right, so lit caps face upper right and shade sits lower
  left (round 2 lit everything from the upper left with the sun on the right).
- **Tree crowns, three tries.** (a) Each lump cut out of the ones behind with a full paper ring and
  split by `lump_shade` → a pile of beach balls (diagonal bands, rings everywhere). (b) One crown mass,
  no gaps → a blob. (c) Kept: lumps back to front with a lit crescent toward the sun (2 cells) and a
  shade crescent on the lower left (3 cells) that follow each lump's silhouette, a one-cell paper arc only
  on the shade side where a lump overlaps the clump behind, a one-cell outline except on the lit edge, sky
  holes. Reads as clumps of foliage with volume.
- **Meadow lighter (.24 → .46, flecked), foreground strip .34**, so the dense bench (2-cell air margin),
  lamp base, tufts and flowers stand out the way objects do on r3_500's hill.
- **Clouds** with separate bumps of different heights (the ref's silhouette), holes filled
  (`binary_fill_holes`), a body ellipse, densest at the top, thinning to the base and to the lower left.
- Kept from round 2: the layered hills with ridge rows and one-cell paper separation, the cell-exact tufts,
  the flowers with a paper eye, the lamp post (now with a lit/shade split on the pole and the glass).

Skill feedback from this scene:
- **`lump_shade` gives straight diagonal bands** across a lump (thresholds on a projection), which is what
  makes the "beach ball" look; silhouette-following crescents (`m & ~shift(m, toward light)`) read as
  volume. Worth adding as `lump_crescents(mask, light=(dx, dy), lit=2, shade=3)` (needs a `shift` helper —
  cellkit has none; I had to write one).
- The tree recipe ("a few round lumps ... each split by lump_shade ... a one-cell outline") does not say
  how lumps separate. Full air rings = balls; no air = blob; air only on the shade side works.
- **cellkit cloud:** the clouds need hole filling after the lump union (scipy) — a `fill_holes` in cellkit
  would save a dependency hunt.
- No reference frame has a tree; the closest is the patio plant. A tree reference (or a worked crown in
  examples/) would help most.

## Summary of skill feedback (all scenes)

Missing helpers I had to write (all in `canvas.py` / `daykit.py`):
1. A cell-grid value canvas: px → cell masks (box, rounded box, ellipse), `put/carve/lift/cut(margin)`,
   a screen-blended `glow` on cells, `text`/`seg7` on cells, one `emit` to svgkit.Svg. This removed the
   "carve after glow" ordering problem and made every edge cell-exact. Biggest single win.
2. `shift(mask, dc, dr)` (for crescents, lit edges, "edge facing the light").
3. Cell-exact `leaf` and `pot` (svgkit's are SVG shapes with averaged edges).
4. A pool-of-light helper with a crisp rim and an inner falloff.
5. `fill_holes`, `lump_crescents`.

Unclear or wrong in the docs:
- "Train car side: a .18 body field" — reads as noise; .3–.35 (kitchen cabinets) works.
- `moon()`'s default soft halo = the smear the skill warns against; use a ring.
- Curtain folds should be straight vertical gaps; hang curtains beside the frame.
- A table top front-on cannot receive a light pool; say what can (cloth, apron, wall).
- seg7 default 4 x 7 is too small for a clock; bitmap_text should be bright on dark.
- `leaf()`'s midrib splits dense leaves on cells; leaves under ~8 cells long become blobs.
- Hierarchy is easiest to judge on the compare sheet's value maps, not on the half-size halftones;
  SKILL.md step 5 could say so.
- svg2dots value maps are 120 x 214, cellkit masks 120 x 213.

Workflow notes:
- The scratchpad was shared with another process (a `crop.py` I wrote was overwritten mid-session); I
  moved my scratch files to a private subfolder. Also, while I worked, someone else wrote
  `_station_0000.py` and `scenes/station_night_0000.*` into this folder — not mine, left untouched.
