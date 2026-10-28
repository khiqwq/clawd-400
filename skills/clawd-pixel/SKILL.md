---
name: clawd-pixel
description: Make animated pixel-art GIFs, sprite animations or short videos of Clawd — the small orange blocky crab-like mascot of Claude Code — in the exact style of the user's reference GIFs and lo-fi Clawd videos (40x40 grid scaled to 480x480, flat orange body, 2x2 black eyes, stubby arms, four legs, pseudo-3D turns). Use this whenever the user asks for Clawd / 小螃蟹 / Claude Code mascot animations, 动图, GIF, 表情包, stickers, sprite sheets, loops, or a Clawd scene/room/video, including batches ("make 20 Clawd GIFs"), edits to existing Clawd scenes, or learning from new Clawd reference GIFs/videos — even if they don't say "pixel art".
---

# Clawd pixel animations

## Non-negotiable (the user rejected work that broke these)

- **Clawd's face is two black eyes and nothing else.** No mouth of any kind — not for eating,
  singing, shouting, laughing or surprise — no teeth, tongue, blush, nose, mustache, cheek marks,
  eye whites, coloured eyes (hearts/stars as eyes) or oversized eyes. Only the glyphs in
  `engine.EYES`. The engine ignores `mouth=`/`blush=`; never hand-draw them either.
- **Clawd's body is the reference orange**, with the shade colour only on side/top faces. No tints
  (angry red, gloomy grey, cold blue, sick green, ghost white), no colour flashes over him, no
  patterns, no outlines, no melting/splitting/non-integer scaling/arbitrary rotation.
- **Emotion lives in the eye glyph, the pose, the motion and effects around him** (hearts, sweat,
  steam, !/?, sparkles, clouds, bubbles, text). Costumes and props may cover him; they never add
  facial features.
- Run `python <skill>/scripts/lint.py`-style checks (see step 4) before delivering.

This skill holds a small Python engine that already draws Clawd exactly like the references, plus
the rules it encodes. You write a *scene function* per animation; the engine renders it.

Bundled:
- `scripts/engine.py` `props.py` `kit.py` — canvas, Clawd in every view, props, effects, actions
- `scripts/render.py` — scene file → GIF / WebP / MP4 / PNG frames / contact sheet
- `scripts/gallery.py` — index.html grid for a folder of GIFs
- `scripts/pixelize.py`, `scripts/study_video.py` — for studying new references
- `references/style.md` — **the style rules** (anatomy, pseudo-3D views, eyes, palette, timing)
- `references/motifs.md` — every reference animation broken into beats, with example slugs
- `references/api.md` — engine API; `references/learning.md` — how to learn from new references
- `examples/*.py` — ~50 finished scenes recreating the reference loops; copy from them freely
- `examples/themes/*.py` — 360 more finished scenes (emotions, daily life, coding, sports,
  costumes, seasons) that passed the style rules; search them before inventing a motion
- `scripts/lint.py` — style check for any scene file (tints, retired eyes, things drawn on the face)
- `assets/refs/1-4.gif` — the original reference GIFs (not included in the public repo; put your own
  official Clawd reference GIFs here)

Requires Python 3 with Pillow (and numpy for the study tools); ffmpeg only for MP4 / video study.

## Workflow

1. **Pin down the request.** What should Clawd do, how many GIFs, output format (default:
   480×480 transparent GIF, seamless loop), and whether it needs a room backdrop or text (Chinese
   is supported). If the request is close to a reference loop, read its row in
   `references/motifs.md` and open the example.
2. **Read `references/style.md` once per session** before drawing — especially §3 pseudo-3D and
   §4 eyes. Those are where hand-drawn attempts go wrong (wrong eye placement in turned views,
   mirrored glyphs, shade used as outline, arbitrary rotation).
3. **Write a scene file** in the user's working folder (not inside the skill), e.g.
   `clawd_scenes.py`:
   ```python
   from engine import add, clawd, Canvas, BX, BY, GROUND, sin, pick, rng
   import props as P
   from kit import S

   def idea(f, t, n):
       up = t % 12 >= 4
       info = clawd(f, view='qr', tilt=int(up), ra='up' if up else 'side', eyes='big' if up else 'normal')
       cx, top = info['head']
       P.bulb(f, int(cx) - 6, int(top) - 15, t, lit=up)

   add('idea', '灵光一闪', 'Idea!', idea, n=12, dur=140)
   add('cheer', '加油', 'Cheer', S, n=8, dur=140, act='cheer', fx=['confetti'])
   ```
   One function per *motion idea*; parameters for variants. Use `kit.S` for quick
   action + props + effects combinations, custom functions when the motion is the point.
4. **Render, lint and look at it.**
   `python <skill>/scripts/render.py clawd_scenes.py --out out --sheet`
   `python <skill>/scripts/lint.py clawd_scenes.py` — flags tinted bodies, retired eye glyphs and
   foreign pixels on Clawd's face (props crossing the face can be false positives; look).
   Then Read every `out/<slug>_sheet.png`. Check: Clawd readable in every frame, eyes placed per
   the view rules, loop seams (last frame → first), nothing clipped at the 40×40 edge, props
   legible on white *and* dark. **Timing** (style.md §7a): in a multi-stage story every key pose
   is on screen long enough to read (impact/reveal 300–450 ms via `beats()`), and no turning
   point snaps from one action to the next — give it a fast in-between (`add_tweened`, 60–100 ms);
   leave simple loops and snappy beats alone. Tears, glasses, eyepieces and wink sparkles sit on
   the eyes from `info['eyes']`, in every view. Fix and re-render until it looks like the references. Never hand
   over GIFs you have not looked at.
5. **Deliver.** GIFs in `out/`; for more than a handful run
   `python <skill>/scripts/gallery.py out --title "..."` and point the user at `index.html`.
   Video: `--mp4 --loops N` (add a `Dotted` backdrop for the room look). Smaller files:
   `--scale 6` (240 px) or `--webp`.

## Style in one breath

Flat orange #E37E52 block 16×12, 2×2 black eyes at cols 2–3/12–13, 4×4 arms at rows 4–7, four
2-wide legs at 0/4/10/14. Depth only from shade #C57047 on faces you can see: a 2-col side face
when turned 3/4 (far eye moves 2, near eye 1, both glyphs facing the same way, far arm out with
shaded tip, near arm a 1-px nub, legs spread evenly), 3 cols in strong 3/4, a 1-row top face when
seen from above, and `tilt=1` (near half of the head 1 px higher) when looking up. Whole-pixel
motion, squash 18×10 / stretch 14×15, 80–220 ms per frame, calm loops where secondary motion
(steam, notes, dots, flicker) does a lot of the work. Details and the reasons are in
`references/style.md`.

## Judgment calls

- **Stories vs loops.** GIFs loop, so close the circle inside the animation: the flower folds
  back to a bud, Clawd walks off one side and re-enters from the other, the wish bubble pops and
  the opening pose returns. Only when no return makes sense, hold the last frame 2–3× longer so
  the cut reads as a pause.
- **Direction words.** 侧着身子走 / walking sideways → the strong 3/4 walk (`q2r`/`q2l`) the videos
  use. 侧面 / profile / 剪影 → `sr`/`sl`. 转身 / 回头看我 → step through the views to `front`, one or
  two frames each.
- **Night and sky scenes.** Stars and a moon on a transparent GIF disappear on white chat
  backgrounds; for sky/room scenes use `Dotted(dark=True)` as a backdrop (opaque). Plain Clawd
  actions stay transparent.
- **Hands.** Clawd's arms are blocks; clasped or praying hands don't read on the front view.
  Show wishing/praying with closed eyes + `top=True` (head bowed) + low arms, or a turned view
  with the near arm raised.
- **Frame counts.** Pillow merges identical consecutive frames and sums their durations — expected.
- **Checking.** `--sheet` cells are 240 px (enough to see eye placement); add
  `--sheet-bg "#1c1a19"` to check that props still read on a dark background.

## Batches

For dozens or hundreds of GIFs: split by theme into separate scene files, keep slugs unique,
give every GIF a different *idea* (not a recolour or hat swap of the same motion), and render a
contact sheet per file to review in bulk. If subagents help, give each one a theme, this skill's
path, the rule to read `references/style.md` first, and "write only your own scene file".

## When the user brings new references

Follow `references/learning.md`: keyframes → cluster rooms → cluster Clawd beats (loops repeat,
count each distinct beat once) → high-res clips → `pixelize.py` to read them cell by cell →
compare with `pixelize.py --engine ...` → update the engine and `style.md`. Treat the user's
corrections ("the eyes in 3/4 view are off") as the most valuable signal: measure, fix the engine
(not just one scene), re-render the examples, and write the rule down.
