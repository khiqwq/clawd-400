"""Scene modules, in gallery order. Each module registers entries with engine.add()."""
ORDER = ['video', 'summer', 'emotions', 'life', 'dev', 'sports', 'costumes', 'seasons']

# Left out of the final 400: same idea as a scene in another module, or the thinnest compositions.
EXCLUDE = {
    'cos_farmer_water', 'sea_flowers_bloom',   # watering -> bloom (kept: life_water_plant)
    'sea_shooting_star',                        # wish on a meteor (kept: emo_wish_star)
    'cos_archer_bullseye',                      # archery (kept: sport_archery)
    'sea_kite',                                 # kite (kept: life_kite)
    'cos_clown_juggle',                         # juggling (kept: sport_juggling)
    'sea_bunny_hop',                            # bunny ears hop (kept: cos_bunny_hop)
    'cos_painter_easel',                        # easel painting (kept: life_paint_easel)
    'sea_sakura',                               # sneeze gag (kept: emo_sneeze)
    'sea_dumpling_steamer',                     # steamer lid (kept: life_dumpling_steam)
    'life_block_tower',                         # tower topples (kept: dev_ctrl_z)
    'sea_snow_shiver', 'sea_spring_breeze',     # plain compositions
}
