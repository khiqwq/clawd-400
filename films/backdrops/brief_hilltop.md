# Hilltop at sunrise (last scene of the short film "末班车") — light theme, layered

Clawd gets off the night train at dawn, walks up a hill carrying a potted sprout and plants it on the
top as the sun rises. One 1920 x 1080 frame, front-on, light theme, in three layers so the sun can
rise from behind the hill in the film:

1. `hilltop_back` — the sky (paper), two or three far hill ranges (faint, ≤ .2, separated by one-cell
   paper lines, nearer = denser), a couple of clouds, a few birds far away.
2. `hilltop_sun` — the sun alone (disc ~.38 + 2-dot ray dashes), centred at x 1500, y 560; the film
   slides this layer up from behind the hill (it will travel to about y 300).
3. `hilltop_front` — the near hill and everything on it, opaque where the hill is: it hides the sun
   when the sun is low. The hill rises from the lower left to a gentle rounded top on the right:
   ground at the frame's bottom-left, a path whose surface (Clawd's feet line) goes through
   (0, 975) → (400, 960) → (700, 885) → (950, 765) → (1150, 675) and then runs flat at y 657 from
   x 1150 to x 1420. Draw the path as a clear band on the hill (carved edges, a few stones) so feet on
   that line read as walking on it. A lone tree at about x 1560–1760 rooted on the hilltop's right
   shoulder (cell-level canopy with lit caps), grass tufts along the path, the near slope denser
   toward the viewer. Keep x 1150–1420 above the path calm (Clawd plants the sprout at x ~1330).
   Also save `hilltop_front_mask.png`: white where this layer is opaque (the hill and the tree), black
   elsewhere, 1920 x 1080.

Deliverables: for each layer `<layer>.svg`, `<layer>.png` (svg2dots render), `<layer>_value.png`; a
`hilltop_preview.png` with the three composited (sun at y 560) and one with the sun at y 300; the
mask; your script; notes.md.
