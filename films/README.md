# Films

Two films made from the Clawd engine and the `clawd-halftone` backdrops. The finished videos are too
big for the repo, so they are not included. These scripts rebuild them.

| Folder | What |
|---|---|
| `short/` | 《末班车 / The Last Train》, 34.5 s. `render_short.py` renders the picture to `out/short_silent.mp4`. `score_short.py` adds music and foley to make `out/clawd_last_train.mp4`. |
| `promo/` | The 400-GIF promo, about 44 min. `mix_promo.py` mixes the music and writes `playlist.json`. `render_promo.py --theme <id>` renders one theme, and `render_promo.py --concat` joins them into `out/clawd400_promo.mp4`. |
| `backdrops/` | The halftone backdrops the films use: `iteration-3/` holds the station, the carriage and two day rooms; `hilltop/` holds the layered sunrise. The `brief*.md` files describe each scene. |
| `covers/` | The video covers and the site's social card. `make_covers.py` rebuilds them. |
| `tools/` | Shared helpers. `pixfilm.py` turns Clawd engine canvases into film frames; `halftone.py` is the calibrated dot screen. |

Needs: Python 3.10+, Pillow, NumPy, ffmpeg, and Playwright with Chromium (for svg2dots).

Not included (see [../NOTICE.md](../NOTICE.md)):
- **Music.** HoliznaCC0's CC0 lo-fi collections from OpenGameArt go in `music/dl/`. The short uses
  "Happy, but a little off", saved as `music/short_track.mp3`.
- **onetake.** `score_short.py` imports `sfx_palette.py` from
  [onetake](https://github.com/feitangyuan/onetake), which has its own noncommercial licence. Put its
  `scripts/` in `onetake-kit/scripts/`.

The promo backdrops (`promo/backdrops/*.png`) were drawn with the scripts in
`skills/clawd-halftone/examples/promo_day` and `promo_night`.
