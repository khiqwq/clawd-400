# Backdrops in a film (HTML comp, camera, layers)

## Layers

Paint each depth as its own `Paint` and save the **value map** (`stem_value.png`, L + alpha):
- the room / interior (windows and doors **erased** to holes with `erase` / `erase_poly`, so what is
  behind shows through);
- what is outside, as long strips for scrolling scenery (far / mid / near), each a separate layer;
- light that changes over time (a lamp's glow, moonlight on a table, a beam) as its own layer, so the
  comp can fade it in and out (additive);
- foreground pieces Clawd walks behind (a platform edge, a door frame) on top.
A layer may be any size in cells: 1 screen = 213 x 120; a 3-screen panorama = 640 cells wide.

## Live halftone (scripts/halftone_runtime.js)

**Load value layers as data: URIs.** A comp opened from file:// (render.py, stills.py) taints the
canvas when it draws a file:// image, and `getImageData` then throws a SecurityError. Write the
layer manifest with `Paint.data_uri()` (or base64 the PNG) instead of a relative path.

Each seek: clear the 214 x 121 cells canvas, draw every value layer through the camera
(`ht.viewToCells(OM.view(cam, {depth}))`, then `drawImage(layer, x, y)` in world cells x 9 px), add
lights with `globalCompositeOperation = 'lighter'`, darken with `'multiply'` (a fill of grey), then
`ht.draw()`. The dot grid stays fixed to the screen; content moves under it.
- At zoom 1, round layer offsets to whole cells → dots stay crisp and motion steps like the videos'.
- While zooming, values resample between cells; that is fine for a push of a second or two.
- Use `imageSmoothingEnabled = true` on the cells canvas when the camera is not at zoom 1, false at 1.

## Pre-rendered halftone

For a backdrop that only slides (the videos' room change: the next room slides up from below in
~0.3 s and the dots move with it), render it once with `Paint.save()` and move the PNG. Dots then
belong to the world, exactly like the reference.

## Clawd and props

Clawd is a separate crisp pixel layer on top (14 px per Clawd pixel at zoom 1). Never darken, tint
or halftone him; light changes affect the backdrop only.

## Theme changes

Night → day can cross over: animate the ground from #131313 to #f4f2ec while the dots go from light
to dark (both through mid grey) over ~1 s, ideally under a camera move.
