"""Style lint: flag scenes where Clawd stops looking like the references.

    python lint.py [module ...]        # project modules (default: every module in scenes.ORDER)
    python lint.py my_scenes.py        # or any scene file

Checks every frame of every scene:
  tint   - clawd() called with a body/shade colour other than the reference orange
  eyes   - a retired eye glyph was requested (white sclera, coloured eyes, tears, lids)
  face   - foreign pixels on Clawd's face (rows 1-8 of the body): white, pink, red, yellow,
           blue... i.e. hand-drawn mouths, teeth, tongues, blush, sclera, tinted bodies.
  cover  - less than half of the face area is still orange (melted, recoloured, hidden)
Props that legitimately cross the face (sunglasses, masks, a cup being sipped) can trip
`face`/`cover`; look at those frames before changing anything.
"""
import importlib
import os
import sys

import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

try:
    from scenes import ORDER
except ImportError:  # used outside the project (e.g. from the skill folder)
    ORDER = []

BODY = {engine.PAL['O'], engine.PAL['o'], engine.PAL['K']}
CALLS = []
_orig = engine.clawd


def _spy(f, *a, **kw):
    info = _orig(f, *a, **kw)
    CALLS.append((f, dict(kw), info))
    return info


def lint_module(mod):
    start = len(engine.REG)
    if mod.endswith('.py'):
        spec = importlib.util.spec_from_file_location('lint_scene', os.path.abspath(mod))
        m = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.dirname(os.path.abspath(mod)))
        spec.loader.exec_module(m)
    else:
        m = importlib.import_module(f'scenes.{mod}')
    # scene modules imported `clawd` by name; patch their reference too
    if getattr(m, 'clawd', None) is _orig:
        m.clawd = _spy
    report = []
    for e in engine.REG[start:]:
        flags = {}
        for t in range(e['n']):
            CALLS.clear()
            f = engine.Canvas()
            e['fn'](f, t, e['n'], **e['kw'])
            for (canvas, kw, info) in CALLS:
                if canvas is not f:
                    continue  # drawn on a layer: checked below through the final frame
                body = engine.col(kw.get('body', 'O'))
                if body not in (engine.PAL['O'],):
                    flags['tint'] = flags.get('tint', 0) + 1
                for k in ('eyes', 'eyes_r'):
                    if kw.get(k) in engine.EYE_ALIASES:
                        flags['eyes'] = flags.get('eyes', 0) + 1
            for (canvas, kw, info) in CALLS:
                if kw.get('view', 'front') in ('back',) or info.get('w', 16) < 8:
                    continue
                x, y, w = int(info['x']), int(info['y']), int(info['w'])
                foreign = orange = total = 0
                for yy in range(y + 1, y + 9):
                    for xx in range(x + 1, x + w - 1):
                        c = f.get(xx, yy)
                        total += 1
                        if c in BODY:
                            orange += c != engine.PAL['K']
                        elif c is not None:
                            foreign += 1
                if foreign >= 2:
                    flags['face'] = max(flags.get('face', 0), foreign)
                if total and orange / total < 0.5:
                    flags['cover'] = flags.get('cover', 0) + 1
        if flags:
            report.append((e['slug'], flags))
    return report


def main():
    mods = sys.argv[1:] or [m for m in ORDER if os.path.exists(os.path.join('scenes', m + '.py'))]
    engine.clawd = _spy
    total = 0
    for mod in mods:
        rep = lint_module(mod)
        total += len(rep)
        print(f'== {mod}: {len(rep)} flagged')
        for slug, flags in rep:
            print(f'   {slug:28s} ' + ' '.join(f'{k}={v}' for k, v in sorted(flags.items())))
    print('total flagged:', total)


if __name__ == '__main__':
    main()
