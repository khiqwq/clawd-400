# Promo backdrops brief

In the promo each of the 400 Clawd GIFs plays in a scene, then a dotted frame draws around it and it
loops twice. One backdrop per GIF theme, reused for every GIF of that theme. Every backdrop: one
1920 x 1080 frame, front-on, in the reference videos' halftone style (the clawd-halftone skill).

**The GIF square** — the GIF plays at x 680–1240, y 471–1031 (Clawd's body centred at x 960, feet at
y 975 on the floor line). Each GIF also shows its own effects around Clawd inside that square (music
notes, sparkles, speech bubbles, small props). Keep the square calm so those read: inside x 740–1180,
y 500–975 only the floor band and at most faint, far things (≤ .1); the room's objects frame the
square from both sides and the top. The floor band continues under it.

**All promo backdrops are LIGHT theme** — many GIFs draw their own effects in black (notes, text,
question marks), which vanish on a dark ground, and the GIFs are never modified. The "night set"
below is drawn as daytime versions (lounge_day, office_day, stage_day, snow_day).

## Set A (originally night, now drawn in the light theme)

1. **lounge_night** — for the "video" GIFs (they recreate the reference loops: cooking, desk, guitar,
   reading, space). A cosy night lounge: a window with stars and a crescent moon on one side, a floor
   lamp with its pool of light, an armchair, a side table with a radio, a bookshelf, a rug.
2. **office_night** — for the "dev" GIFs. A home office at night: a desk on one side with a monitor
   whose screen glows (code lines as carved bars), a desk lamp, a pinboard with notes, a shelf with
   binders and a plant, a window with a city at night (lit windows), cables. The GIFs bring their own
   laptops/props, so nothing in the centre.
3. **stage_night** — for the "costumes" GIFs. A small theatre stage: heavy curtains drawn to the sides
   (folds carved), a valance with a fringe on top, a spotlight cone from above landing on the centre of
   the stage floor (stepped, not a blur), footlights along the front edge, a prop chest and a
   coat rack with hats at the sides.
4. **snow_night** — for the "seasons" GIFs. A snowy street at night: falling snow (sparse 1-cell
   flakes, more in front), snow-covered roofs of two small houses with warmly lit windows, a lamp post
   with a lantern and its pool on the snow, pine trees with snow on the branches, a snowman at one
   side, snowbanks.

## Day set (light theme)

5. **beach_day** — for the "summer" GIFs. A beach: the sea's horizon with gentle waves (carved
   lines), the sun with rays, two clouds, a palm tree on one side (fronds with lit/shaded halves), a
   striped umbrella and a deck chair on the other, a sandcastle, shells, the sand denser toward the
   viewer.
6. **kitchen_day** — for the "life" GIFs. A home kitchen in daylight: a window with the sun and a
   potted herb on the sill, upper cabinets with insets, a counter with a kettle and a fruit bowl, a
   fridge with a magnet note, a hanging plant, utensils on a rail, tiles behind the counter.

## Deliverables (in the folder you are given)

- `scenes/<name>.svg`, `scenes/<name>.png`, `scenes/<name>_value.png`, `scenes/<name>_debug.png`
- `scenes/<name>_square.png` — the render with the GIF square outlined (to check it is calm)
- `scenes/<name>_crops.png` — 1:1 crops of your render next to the closest reference objects
- your scripts and `notes.md` (what worked, what the skill missed)
