# hilltop — notes

`hilltop.py` draws the three layers on the cell grid (the skill's svgkit/cellkit imported from the skill
folder, nothing edited), renders each with svg2dots (light theme), writes the mask and composites the
previews at the value level (front where the mask is white, elsewhere the denser of back and sun), then
screens them with the skill's `halftone.render` — the way the film comp will combine value layers.

Files: `hilltop_back|sun|front` `.svg/.png/_value.png`, `hilltop_front_mask.png`, `hilltop_preview.png`
(sun at y 560), `hilltop_preview_sun300.png` (sun layer moved up 29 cells = 261 px → centre y 299; a
whole-cell move keeps the dots on the grid), `hilltop_crops.png` (1:1 against r3_500_hill_clouds),
`work_feetline.png` (preview with the feet line in red and the calm box in blue — a check, not a layer).

## Decisions
- **Feet line**: the path's top edge sits on the brief's polyline, rounded to the cell row per column
  (≤ 4.5 px off). The brief gives both (1150, 675) and "flat at 657 from x 1150"; they meet with a
  3-cell ease (1150,675)→(1177,657), then flat to 1420. The row right above the feet line is a dense
  line (the verge's bottom edge), the path itself a light 3-row band under it, a carved row, then a
  dense front edge; stones in and along it. Feet on the line stand on the band's top edge.
- **Hill**: a 2–3-row grassy verge behind the path (ridge row a level denser, tufts on it, none over
  x 1150–1420), the body below the path denser toward the viewer (.3 → .66) with paper flecks and a few
  lighter tussocks, like the ref's near hill. Beyond x 1420 the top rounds down to (1920, ~769).
- **Calm**: x 1150–1420 above the hilltop is sky only. The far ranges are kept below the hilltop there.
  The only marks are the sun's two left ray tips (x ~1400, inside the box's right edge) — unavoidable
  with the sun centred at x 1500 and readable rays; they travel up with the sun.
- **Sun**: a cell-exact disc r 63 at .38 and 12 rays of 2 dots at .3 (rotated 15° so none points
  straight at the calm box). Kept separate from the tree: the crown starts right of the ray tips.
- **Tree**: four big lumps (park_day's cell-level crown: lit cap on the upper left toward the sun, the
  lower right a hard step heavier, air where lumps overlap, two sky holes), a trunk with a shade band
  and branches. Small lumps (r 40–50) read as lace — fewer, bigger lumps read as a tree.
- **Mask**: hill + tree + tufts + a one-cell air halo round them (the skill's overlap rule: the near
  shape keeps a cell of paper over whatever is behind, so the sun's dots never touch the crown or the
  ridge). Cell-exact, so its edge matches the dots.
- **Clouds**: svgkit's soft cloud (big soft things may keep averaged edges); cell-built clouds came out
  as stepped pyramids.
- **Birds**: 5-cell zigzags (tips down, wings up); a "v"/U read as a smile.

## Iterations (6 renders)
1. Sun r 72 at (1500, 560) merged with the tree crown (similar tones, touching) → sun r 63, crown moved
   right (x ~1610–1820), air halo between.
2. Cell clouds = stepped pyramids → soft svg clouds.
3. Birds read as smiles → zigzags.
4. Crown of 7 small lumps with lit caps .22 + holes = lacy broccoli → 4 big lumps, lit .3, 2 holes.
5. Value maps from svg2dots have 214 columns (a partial last cell); masks padded to match.

## Skill gaps seen
- No guidance for layered backdrops beyond film.md's outline: how to composite value layers (I used
  "front where masked, else max(back, sun)") and that masks should include the one-cell air halo.
- svg2dots' value map is 214 x 120 while cellkit works on 213 x 120 — worth one line in the docs.
- `svgkit.sun` is soft SVG; a cell-exact sun (disc + 2-dot dashes) belongs in cellkit.
