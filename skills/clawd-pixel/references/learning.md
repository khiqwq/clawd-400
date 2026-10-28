# Learning from new references

The user may hand over more reference GIFs, images or (very long) videos and ask you to keep
learning. This is how the current rules were derived — repeat it and fold what you learn back
into `style.md` / the engine.

## Long videos (hours)

1. Probe: `ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact X.mp4`
2. Keyframes only (fast even for 10 h of AV1):
   `python scripts/study_video.py keyframes X.mp4 OUTDIR` (wraps
   `ffmpeg -skip_frame nokey -i X.mp4 -fps_mode vfr -frame_pts 1 -vf scale=320:-2 k_%08d.jpg`;
   file names are frame numbers, so seconds = number / fps).
3. Cluster by room/background, then within each room by Clawd's own appearance (crop around the
   orange pixels): `python scripts/study_video.py cluster OUTDIR` → `rooms.png` sheets plus a
   JSON of groups with timestamps. Loops repeat for hours — the group sizes tell you which beats
   are the main loop and which are rare extras worth looking at. Only distinct groups count.
4. For each distinct group pull a short high-res clip around Clawd:
   `ffmpeg -ss T -i X.mp4 -t 5 -vf "fps=4,crop=480:420:X:Y" f_%03d.png` and tile it into a strip.
5. Turn frames into cells: `python scripts/pixelize.py frame.png [--unit 13.9]` prints the
   logical-pixel map (`O` body, `o` shade, `K` black). Compare it with
   `python scripts/pixelize.py --engine view=qr tilt=1` (the engine's own output) and fix the
   engine where they differ.

## GIFs / images

Extract frames with Pillow (`ImageSequence`), note size, frame count and per-frame durations, and
tile them on white. The reference GIFs are rendered with a little perspective, so their pixel
grid is not perfectly even (~11–12 px); measure proportions rather than exact cells.

## What to look for

Proportions (body/arms/legs/eyes), which faces get shade and when, where each eye goes per view,
what moves vs. what holds still, how many frames each beat lasts, how props attach, colours.
Write each finding down as a rule with the reason, then update the engine and re-render the
affected examples.
