# Reference animations, beat by beat

Every distinct animation found in the references, after removing loops that repeat. Each has a
worked implementation in `examples/` (slug in brackets) — open it when a request is close to one
of these instead of starting from scratch.

## The four reference GIFs (`assets/refs/`)

| # | what happens | how it is built |
|---|---|---|
| 1 | Clawd holds a maroon bubble wand, turns 3/4, tilts up and blows; a lavender bubble grows, drifts up and pops into dots; eyes go closed → happy `^` | `qr` + `tilt=1` while blowing, wand art at `rh`, `bubble_ring` drifting up, pop = 6 dots [`bubble_wand`, `bubble_big`] |
| 2 | Teacup in hand, eyes closed, blue speech bubble fills with dots one by one; then Clawd turns away (top face shows) and keeps chatting | `qr` + `tilt=1` + `closed`, `dots_bubble`; second half `ql` + `top=True`, bubble flips side [`tea_talk`] |
| 3 | Lightbulb idea: 3/4 turn, near arm raised over the head, bulb flickers, a blink | `qr`, `tilt=1`, `ra='up'`, `bulb()` [`idea_bulb`, `idea_ding`] |
| 4 | Focused: 3/4 turn, `focus` eyes looking forward, fidget spinner spinning in the hand | `qr`, `focus`, 4-frame spinner art [`fidget_spinner`] |

## Video 1–2 (night rooms; the two videos loop the same six scenes)

| scene | loop | extra beats seen | implementation |
|---|---|---|---|
| kitchen | chef hat, frying pan held out, greens tossed up and caught, steam | jumps in stretched with arms up → lands squashed → hat drops on | [`cook_veggies`, `cook_pancake`, `cook_egg`, `chef_arrives`, `stir_soup`] |
| lounge | blue headphones, eyes `‿`, swaying/bobbing to music | walks in, turns front, headphones come down onto the head | [`vibe_headphones`, `vibe_nod`, `phones_on`] |
| space | glass helmet, floating, legs trailing back, twinkles | slow drift | [`astro_float`, `astro_spin`, `astro_wave`, `astro_planet`, `astro_flag`] |
| music room | purple electric guitar, rocking, yellow notes | head-banging solo with sparks, turning | [`guitar_rock`, `guitar_solo`, `guitar_chill`, `rock_jump`] |
| desk | strong 3/4 side view, sitting, typing | rare: leaps off the chair and tumbles in the air, drops back | [`desk_typing`, `desk_think`, `desk_coffee`, `desk_flail`] |
| fireplace | big crimson reading glasses, book, page flips | walks in, jumps up stretched, lands in the armchair, glasses + book appear | [`read_glasses`, `read_doze`, `read_stack`, `armchair_arrive`] |
| transitions | walking in 3/4 between rooms, climbing stairs (whole body tilted), through doors | spin on the spot + horizontal glitch stripes = teleport; dropping in from above | [`walk_in`, `walk_out_door`, `stairs_climb`, `teleport`, `space_drop`, `stretch_tall`] |

## Video 3 (daytime rooms, light dotted backdrops)

| scene | loop | implementation |
|---|---|---|
| disco | mint headphones at DJ decks, scratching; holds up a spinning vinyl | [`dj_deck`, `dj_vinyl`] |
| disco | keepy-uppy: the ball travels foot → knee → head → other side while Clawd turns to follow it | [`soccer_keepy`, `soccer_header`] |
| building site | yellow hard hat; hides completely under it, then pops out; wrench work on a girder; walking a girder over the city | [`hardhat_hide`, `hardhat_wrench`, `girder_walk`] |
| beach path | carrying a checked picnic basket, a cherry pops out | [`picnic_basket`] |
| pool (top view) | lying in a striped inner tube with sunglasses, ripples; pulls the shades down to peek | [`pool_float`, `pool_peek`] |
| dunes / sea | sandboarding off a lip; surfing a wave then wiping out | [`sandboard`, `surf_wipeout`] |
| beach | sunglasses drop from the sky onto the face | [`shades_drop`] |
| patio desk | same strong-3/4 typing loop as the night desk (a repeat) | — |

## Request-style examples (`examples/requests_water_walk_wish.py`)

Made by a fresh session using only this skill, for "浇水开花 / 侧身走进来回头挥手 / 看流星许愿":
`water_bloom` (3/4 watering, sprout grows to a flower, tilt on the bloom), `walk_wave` (q2r walk in,
q2r→qr→front turn, wave, walks off right so the loop is seamless), `star_wish` (dark dotted night
backdrop, tilt + lookv=-1 gazing up, meteor, bowed head with top face for the wish).

## Choreography patterns worth reusing

- **Arrive → act → settle**: walk in (turned view) → face front → do the thing → small blink. Most
  video loops are built this way.
- **Anticipation**: squash 1 frame before any jump, stretch at the apex, squash on landing.
- **Hold the pose**: in a 12-frame loop, 6–8 frames can be the same pose with only an eye blink or
  a prop moving — the references are calm; not every pixel has to move.
- **Secondary motion carries the loop**: steam, notes, dots in a bubble, a bulb flicker, a
  spinner. Clawd can stay almost still.
- **One gag per GIF**: a single readable idea per loop beats several small ones.
