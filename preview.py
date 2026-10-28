"""Preview one scene module: python preview.py <module> [slug-substring ...]

Writes previews/<module>/sheet_XX.png (one row per entry, up to 12 frames each)
and previews/<module>/<slug>.gif, and prints basic checks.
"""
import importlib
import os
import sys

from PIL import Image, ImageDraw

import engine

ROW_FRAMES, CELL, PER_SHEET = 12, 96, 10


def main():
    mod = sys.argv[1]
    filters = sys.argv[2:]
    importlib.import_module(f'scenes.{mod}')
    entries = [e for e in engine.REG if not filters or any(s in e['slug'] for s in filters)]
    out = os.path.join('previews', mod)
    os.makedirs(out, exist_ok=True)
    rows = []
    for e in entries:
        frames = engine.render(e)
        engine.save_gif(frames, os.path.join(out, e['slug'] + '.gif'), e['dur'])
        step = max(1, len(frames) // ROW_FRAMES)
        shown = frames[::step][:ROW_FRAMES]
        row = Image.new('RGB', (180 + ROW_FRAMES * CELL, CELL), (250, 250, 250))
        d = ImageDraw.Draw(row)
        d.text((4, 4), e['slug'][:28], fill=(0, 0, 0))
        d.text((4, 20), f"{e['n']}f x {e['dur']}ms", fill=(90, 90, 90))
        d.text((4, 36), e['en'][:28], fill=(90, 90, 90))
        for i, fr in enumerate(shown):
            im = fr.to_image().resize((CELL, CELL), Image.NEAREST)
            tile = Image.new('RGBA', (CELL, CELL), (250, 250, 250, 255))
            tile.alpha_composite(im)
            row.paste(tile.convert('RGB'), (180 + i * CELL, 0))
            d.line([(180 + i * CELL, 0), (180 + i * CELL, CELL)], fill=(220, 220, 220))
        rows.append(row)
        blank = all(all(c is None for r in fr.px for c in r) for fr in frames)
        if blank:
            print('WARNING blank:', e['slug'])
    for k in range(0, len(rows), PER_SHEET):
        chunk = rows[k:k + PER_SHEET]
        sheet = Image.new('RGB', (chunk[0].width, CELL * len(chunk) + 2 * len(chunk)), (180, 180, 180))
        for i, r in enumerate(chunk):
            sheet.paste(r, (0, i * (CELL + 2)))
        sheet.save(os.path.join(out, f'sheet_{k // PER_SHEET:02d}.png'))
    slugs = [e['slug'] for e in engine.REG]
    dup = {s for s in slugs if slugs.count(s) > 1}
    print(f'{mod}: {len(engine.REG)} entries, previewed {len(entries)}; duplicate slugs: {sorted(dup) or "none"}')


if __name__ == '__main__':
    main()
