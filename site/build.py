"""Build the Clawd 400 preview site into _site/: the gallery page, one page per GIF, and a static
read-only API for scripts and AI agents (catalog JSON, per-GIF JSON, frame sheets, ASCII frames,
llms.txt, OpenAPI).

  python site/build.py                                   # relative links, for local preview
  python site/build.py --base-url https://you.github.io/clawd-400 --repo-url https://github.com/you/clawd-400
  python -m http.server 8790 -d _site                    # then open http://localhost:8790

Inputs: manifest.json, gifs/, scenes/*.py (source lines), engine.PAL (palette letters).
"""
import argparse
import hashlib
import html
import io
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone

from PIL import Image, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import engine  # noqa: E402

G = engine.G
THEMES = {  # id: (zh, en) — same order and names as generate.py
    'video': ('视频重现', 'Video loops'), 'summer': ('夏日篇', 'Summer'), 'emotions': ('情绪', 'Feelings'),
    'life': ('日常', 'Daily life'), 'dev': ('编程', 'Coding'), 'sports': ('运动', 'Sports'),
    'costumes': ('角色扮演', 'Costumes'), 'seasons': ('节日季节', 'Seasons'),
}
LICENSE = {'id': 'CC-BY-4.0', 'name': 'Creative Commons Attribution 4.0 International',
           'url': 'https://creativecommons.org/licenses/by/4.0/'}
AUTHOR = '风花叶'
CHARS = '123456789#@$%&*+=?!abcfhijlnqstuvxz'   # for colours that are not engine.PAL letters


def pal_names():
    """engine.PAL letter -> (rgb, comment) from the source, so the ASCII legend says what each colour is."""
    names = {}
    for line in open(os.path.join(ROOT, 'engine.py'), encoding='utf-8'):
        m = re.match(r"\s+'(\w)': \((\d+), (\d+), (\d+)\),\s*#\s*(.+)", line)
        if m:
            names[m.group(1)] = m.group(5).strip()
    names.setdefault('K', 'black (eyes)'); names.setdefault('W', 'white')
    return {k: (v, names.get(k, '')) for k, v in engine.PAL.items()}


def hexc(rgb):
    return '#%02x%02x%02x' % rgb


def read_gif(path):
    im = Image.open(path)
    frames, durs = [], []
    for fr in ImageSequence.Iterator(im):
        frames.append(fr.convert('RGBA').resize((G, G), Image.NEAREST))
        durs.append(int(fr.info.get('duration', 100)))
    return frames, durs


def source_line(theme, slug):
    p = os.path.join(ROOT, 'scenes', theme + '.py')
    if not os.path.exists(p):
        return None
    for i, line in enumerate(open(p, encoding='utf-8'), 1):
        if f"'{slug}'" in line or f'"{slug}"' in line:
            return i
    return None


class Site:
    def __init__(self, out, base, repo):
        self.out, self.base, self.repo = out, base.rstrip('/'), repo.rstrip('/')
        self.pal = pal_names()
        self.rgb2ch = {v[0]: k for k, v in self.pal.items()}

    def ver(self, name):
        """Cache-busting tag for a source file: Pages serves with a 10-minute max-age."""
        return hashlib.sha1(open(os.path.join(HERE, 'src', name), 'rb').read()).hexdigest()[:8]

    def url(self, rel):
        """Absolute when the base URL is known (the deployed site), relative otherwise."""
        return f'{self.base}/{rel}' if self.base else rel

    def write(self, rel, data):
        p = os.path.join(self.out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        mode = 'wb' if isinstance(data, bytes) else 'w'
        with open(p, mode, **({} if mode == 'wb' else {'encoding': 'utf-8', 'newline': '\n'})) as f:
            f.write(data)

    # ------------------------------------------------------------------ per GIF
    def item(self, m):
        n, slug, theme = m['n'], m['slug'], m['theme']
        nnn = f'{n:03d}'
        src = os.path.join(ROOT, m['file'])
        raw = open(src, 'rb').read()
        frames, durs = read_gif(src)
        zh_file = m['zh'] + '.gif'                     # the name a GIF gets when dragged out or downloaded
        shutil.copyfile(src, os.path.join(self.out, 'gifs', os.path.basename(src)))

        sheet = Image.new('RGBA', (G * len(frames), G), (0, 0, 0, 0))
        for i, fr in enumerate(frames):
            sheet.paste(fr, (i * G, 0))
        buf = io.BytesIO(); sheet.save(buf, 'PNG', optimize=True)
        self.write(f'sheets/{nnn}.png', buf.getvalue())

        # palette letters: engine.PAL where it matches, spare symbols otherwise; '.' = transparent
        used, extra = {}, iter(CHARS)
        grids, bbox, diffs, prev = [], [G, G, 0, 0], [], None
        for fr in frames:
            px = fr.load()
            rows = []
            for y in range(G):
                row = []
                for x in range(G):
                    r, g, b, a = px[x, y]
                    if a < 128:
                        row.append('.')
                        continue
                    rgb = (r, g, b)
                    ch = used.get(rgb)
                    if ch is None:
                        ch = self.rgb2ch.get(rgb) or next(extra)
                        used[rgb] = ch
                    row.append(ch)
                    bbox = [min(bbox[0], x), min(bbox[1], y), max(bbox[2], x + 1), max(bbox[3], y + 1)]
                rows.append(''.join(row))
            diffs.append(None if prev is None else sum(a != b for ra, rb in zip(prev, rows) for a, b in zip(ra, rb)))
            grids.append(rows); prev = rows
        diffs[0] = sum(a != b for ra, rb in zip(grids[-1], grids[0]) for a, b in zip(ra, rb))  # loop seam
        palette = [{'char': ch, 'hex': hexc(rgb), 'name': self.pal[ch][1] if ch in self.pal and self.pal[ch][0] == rgb else ''}
                   for rgb, ch in sorted(used.items(), key=lambda kv: kv[1])]

        title = f"{nnn} {slug} · {m['zh']} / {m['en']}"
        lines = [f'# Clawd 400 · {title}',
                 f'# {len(frames)} frames, {G}x{G} pixels each (the GIF is the same grid scaled {engine.SCALE}x to 480x480).',
                 '# One character per pixel. "." = transparent. Frames loop forever.',
                 '# palette: ' + '  '.join(f"{p['char']}={p['hex']}" + (f" ({p['name']})" if p['name'] else '') for p in palette), '']
        for i, (rows, d) in enumerate(zip(grids, durs)):
            lines.append(f'## frame {i + 1}/{len(frames)} · {d} ms')
            lines += rows
            lines.append('')
        self.write(f'api/frames/{nnn}.txt', '\n'.join(lines))

        th = THEMES.get(theme, (theme, theme))
        page = f'g/{nnn}-{slug}.html'
        line = source_line(theme, slug)
        rec = {
            'n': n, 'slug': slug,
            'name': {'zh': m['zh'], 'en': m['en']},
            'theme': {'id': theme, 'zh': th[0], 'en': th[1]},
            'gif': {'url': self.url(m['file']), 'file': os.path.basename(src),
                    'zh_file': zh_file, 'width': 480, 'height': 480,
                    'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'transparent': True},
            'pixels': {'grid': G, 'scale': engine.SCALE, 'bbox': bbox,
                       'note': 'bbox = [x0, y0, x1, y1] of all visible pixels over every frame, in grid pixels'},
            'frames': {'count': len(frames), 'durations_ms': durs, 'total_ms': sum(durs), 'loop': 'infinite',
                       'changed_pixels': diffs,
                       'sheet': {'url': self.url(f'sheets/{nnn}.png'), 'frame_width': G, 'frame_height': G, 'layout': 'horizontal strip, frame i at x = i*40'},
                       'ascii': self.url(f'api/frames/{nnn}.txt')},
            'palette': palette,
            'keywords': sorted(set(slug.split('_')) | {theme, 'clawd', 'pixel-art', 'gif'}),
            'links': {'json': self.url(f'api/gifs/{nnn}.json'), 'page': self.url(page),
                      'viewer': self.url(f'#/gif/{n}')},
            'license': LICENSE, 'credit': f'Clawd 400 by {AUTHOR} — CC BY 4.0',
        }
        if line and self.repo:
            rec['source'] = {'file': f'scenes/{theme}.py', 'line': line, 'url': f'{self.repo}/blob/main/scenes/{theme}.py#L{line}'}
        self.write(f'api/gifs/{nnn}.json', json.dumps(rec, ensure_ascii=False, indent=1))
        return rec

    # ------------------------------------------------------------------ pages
    def card(self, r, eager):
        n, nnn = r['n'], f"{r['n']:03d}"
        zh, en = html.escape(r['name']['zh']), html.escape(r['name']['en'])
        alt = html.escape(f"Clawd — {r['name']['en']} ({r['name']['zh']}), {r['frames']['count']}-frame pixel GIF")
        return (f'<article class="card" id="g{nnn}" data-n="{n}" data-slug="{r["slug"]}" data-theme="{r["theme"]["id"]}" '
                f'data-frames="{r["frames"]["count"]}" data-ms="{r["frames"]["total_ms"]}" tabindex="0">'
                f'<div class="tile"><img src="gifs/{r["gif"]["file"]}" width="480" height="480" alt="{alt}" '
                f'{"" if eager else "loading=lazy "}decoding="async"></div>'
                f'<span class="num">{nnn}</span><span class="tick" aria-hidden="true"></span>'
                f'<a class="cap" href="g/{nnn}-{r["slug"]}.html" draggable="false"><b>{zh}</b><span>{en}</span></a></article>')

    def index(self, recs, built):
        parts, cur = [], None
        for k, r in enumerate(recs):
            t = r['theme']['id']
            if t != cur:
                cur = t
                cnt = sum(1 for x in recs if x['theme']['id'] == t)
                parts.append(f'<h2 class="sec" data-theme="{t}"><span>{html.escape(r["theme"]["zh"])}</span>'
                             f'<small>{html.escape(r["theme"]["en"])} · {cnt}</small></h2>')
            parts.append(self.card(r, k < 18))
        data = [{'n': r['n'], 's': r['slug'], 'zh': r['name']['zh'], 'en': r['name']['en'], 't': r['theme']['id'],
                 'f': r['gif']['file'], 'z': r['gif']['zh_file'], 'b': r['gif']['bytes'], 'd': r['frames']['durations_ms']} for r in recs]
        boot = {'themes': [{'id': k, 'zh': v[0], 'en': v[1], 'count': sum(1 for r in recs if r['theme']['id'] == k)} for k, v in THEMES.items()],
                'items': data, 'grid': G, 'scale': engine.SCALE, 'license': LICENSE, 'credit': f'Clawd 400 by {AUTHOR} — CC BY 4.0',
                'repo': self.repo, 'built': built}
        ld = {'@context': 'https://schema.org', '@type': 'ImageGallery', 'name': 'Clawd 400',
              'description': '400 animated pixel-art GIFs of Clawd, the Claude Code mascot. Transparent 480x480 GIFs on a 40x40 grid.',
              'license': LICENSE['url'], 'creator': {'@type': 'Person', 'name': AUTHOR},
              'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'application/json', 'contentUrl': self.url('api/index.json')},
                               {'@type': 'DataDownload', 'encodingFormat': 'application/zip', 'contentUrl': self.url('downloads/clawd-400.zip')}],
              'numberOfItems': len(recs)}
        tpl = open(os.path.join(HERE, 'src', 'index.html'), encoding='utf-8').read()
        page = (tpl.replace('{{CARDS}}', '\n'.join(parts))
                   .replace('{{BOOT}}', json.dumps(boot, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
                   .replace('{{JSONLD}}', json.dumps(ld, ensure_ascii=False))
                   .replace('{{REPO}}', html.escape(self.repo or '#'))
                   .replace('{{OG}}', html.escape(self.url('og.png')))
                   .replace('href="app.css"', f'href="app.css?v={self.ver("app.css")}"')
                   .replace('src="app.js"', f'src="app.js?v={self.ver("app.js")}"')
                   .replace('{{ZIPMB}}', f"{os.path.getsize(os.path.join(self.out, 'downloads', 'clawd-400.zip')) / 1e6:.0f}"))
        self.write('index.html', page)

    def detail_page(self, r, prev, nxt):
        nnn = f"{r['n']:03d}"
        zh, en = html.escape(r['name']['zh']), html.escape(r['name']['en'])
        fr = r['frames']
        ld = {'@context': 'https://schema.org', '@type': 'ImageObject', 'name': f"{r['name']['en']} ({r['name']['zh']})",
              'contentUrl': r['gif']['url'], 'encodingFormat': 'image/gif', 'width': 480, 'height': 480,
              'license': LICENSE['url'], 'creditText': r['credit'], 'creator': {'@type': 'Person', 'name': AUTHOR},
              'keywords': ', '.join(r['keywords'])}
        strip = ''.join(f'<li><i style="--i:{i}"></i><span>{i + 1} · {d} ms</span></li>' for i, d in enumerate(fr['durations_ms']))
        pal = ''.join(f'<li><i style="background:{p["hex"]}"></i><code>{p["char"]} {p["hex"]}</code> {html.escape(p["name"])}</li>' for p in r['palette'])
        src = f'<a href="{html.escape(r["source"]["url"])}">scenes/{r["theme"]["id"]}.py#L{r["source"]["line"]}</a>' if 'source' in r else '—'
        def nav(x, label):
            return f'<a href="{x["n"]:03d}-{x["slug"]}.html">{label}</a>' if x else '<span></span>'
        page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{nnn} {zh} · {en} — Clawd 400</title>
<meta name="description" content="Clawd pixel GIF #{nnn}: {en} / {zh}. {fr['count']} frames, {fr['total_ms']} ms loop, 480x480 transparent. CC BY 4.0.">
<meta property="og:title" content="{nnn} {zh} · {en} — Clawd 400"><meta property="og:image" content="{html.escape(r['gif']['url'])}">
<meta property="og:type" content="website"><meta name="twitter:card" content="summary">
<link rel="alternate" type="application/json" href="../api/gifs/{nnn}.json" title="This GIF as JSON">
<link rel="alternate" type="text/plain" href="../api/frames/{nnn}.txt" title="Frames as ASCII pixel grids">
<link rel="icon" href="../favicon.svg"><link rel="stylesheet" href="../detail.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
<nav class="top"><a href="../#/gif/{r['n']}">← Clawd 400</a><span>{nav(prev, '← ' + (f"{prev['n']:03d}" if prev else ''))}{nav(nxt, (f"{nxt['n']:03d}" if nxt else '') + ' →')}</span></nav>
<main>
<figure><img src="../gifs/{r['gif']['file']}" width="480" height="480" alt="Clawd — {en} ({zh})"></figure>
<section>
<p class="num">#{nnn} · {html.escape(r['theme']['zh'])} {html.escape(r['theme']['en'])}</p>
<h1>{zh}</h1><p class="en">{en}</p>
<dl>
<dt>Frames</dt><dd>{fr['count']} · {fr['total_ms']} ms per loop</dd>
<dt>Durations</dt><dd>{', '.join(str(d) for d in fr['durations_ms'])} ms</dd>
<dt>Size</dt><dd>480×480 GIF ({G}×{G} grid ×{engine.SCALE}), {r['gif']['bytes'] / 1024:.1f} KB, transparent</dd>
<dt>Source</dt><dd>{src}</dd>
<dt>Data</dt><dd><a href="../api/gifs/{nnn}.json">JSON</a> · <a href="../api/frames/{nnn}.txt">ASCII frames</a> · <a href="../sheets/{nnn}.png">frame sheet</a> · <a href="../gifs/{r['gif']['file']}" download="{html.escape(r['gif']['zh_file'])}">GIF</a></dd>
<dt>License</dt><dd><a href="{LICENSE['url']}">CC BY 4.0</a> — {html.escape(r['credit'])}</dd>
</dl>
</section>
</main>
<h2>Frames</h2>
<ol class="strip" style="--sheet:url(../sheets/{nnn}.png);--n:{fr['count']}">{strip}</ol>
<h2>Palette</h2><ul class="pal">{pal}</ul>
</body></html>"""
        self.write(f"g/{nnn}-{r['slug']}.html", page)

    # ------------------------------------------------------------------ API + agent files
    def api(self, recs, built):
        cat = {
            'name': 'Clawd 400', 'version': built[:10], 'count': len(recs),
            'description': '400 animated pixel-art GIFs of Clawd, the Claude Code mascot. 480x480 transparent GIFs drawn on a 40x40 grid scaled 12x.',
            'license': LICENSE, 'credit': f'Clawd 400 by {AUTHOR} — CC BY 4.0', 'repository': self.repo or None,
            'notice': 'Unofficial fan art. Claude, Claude Code and the Clawd character are trademarks of Anthropic; the licence grants no trademark rights.',
            'endpoints': {
                'catalog': self.url('api/index.json'), 'gif_json': self.url('api/gifs/{nnn}.json'),
                'ascii_frames': self.url('api/frames/{nnn}.txt'), 'frame_sheet': self.url('sheets/{nnn}.png'),
                'gif': self.url('gifs/{file}'), 'page': self.url('g/{nnn}-{slug}.html'), 'all_zip': self.url('downloads/clawd-400.zip'),
                'openapi': self.url('api/openapi.json'), 'llms': self.url('llms.txt'),
            },
            'themes': [{'id': k, 'zh': v[0], 'en': v[1], 'count': sum(1 for r in recs if r['theme']['id'] == k)} for k, v in THEMES.items()],
            'items': [{'n': r['n'], 'nnn': f"{r['n']:03d}", 'slug': r['slug'], 'zh': r['name']['zh'], 'en': r['name']['en'],
                       'theme': r['theme']['id'], 'frames': r['frames']['count'], 'total_ms': r['frames']['total_ms'],
                       'gif': r['gif']['url'], 'zh_file': r['gif']['zh_file'], 'json': r['links']['json'], 'ascii': r['frames']['ascii'],
                       'sheet': r['frames']['sheet']['url'], 'page': r['links']['page'], 'keywords': r['keywords']} for r in recs],
        }
        self.write('api/index.json', json.dumps(cat, ensure_ascii=False, indent=1))
        self.write('api/themes.json', json.dumps(cat['themes'], ensure_ascii=False, indent=1))
        self.write('api/openapi.json', json.dumps(openapi(self.base), ensure_ascii=False, indent=1))

        u = self.url
        self.write('llms.txt', f"""# Clawd 400

> 400 animated pixel-art GIFs of Clawd, the Claude Code mascot: transparent 480x480 GIFs, each drawn on a 40x40 pixel grid and scaled 12x, in 8 themes. Free to use, including commercially, under CC BY 4.0 with credit ("Clawd 400 by {AUTHOR} — CC BY 4.0"). Unofficial fan art: the Clawd character and the Claude marks belong to Anthropic.

Everything below is static JSON, text or images. No key and no JavaScript needed. Numbers are 1–400; `nnn` is the number zero-padded to 3 digits (007).

## Read the GIFs

- [Catalog]({u('api/index.json')}): every GIF with number, slug, Chinese and English title, theme, frame count, loop length, and the URLs below
- [One GIF]({u('api/gifs/001.json')}): `api/gifs/{{nnn}}.json`, with per-frame durations (ms), changed pixels per frame, palette (hex + name), content bounding box, file size, sha256, and source line in the engine
- [Frames as text]({u('api/frames/001.txt')}): `api/frames/{{nnn}}.txt`, every frame as a 40x40 character grid, one character per pixel, with the palette legend. The easiest way for a language model to "see" the animation
- [Frame sheet]({u('sheets/001.png')}): `sheets/{{nnn}}.png`, all frames side by side at native 40x40 (frame i at x = 40*i)
- [Themes]({u('api/themes.json')})
- [OpenAPI description]({u('api/openapi.json')})

## Get the files

- GIF: `gifs/{{nnn}}_{{slug}}.gif` (the catalog's `gif` field). Suggested local file name: the Chinese title, `{{中文名}}.gif` (`zh_file`)
- [All 400 as one ZIP]({u('downloads/clawd-400.zip')})
- Human page per GIF: `g/{{nnn}}-{{slug}}.html`

## In a browser (Playwright, Puppeteer…)

The gallery page exposes `window.clawd` once `document.documentElement.dataset.clawdReady === "1"` (or on the `clawd:ready` event). Call `clawd.help()` for the full list. Main calls: `clawd.list({{theme, q}})`, `clawd.get(n | slug)`, `await clawd.frames(n, {{format: 'ascii' | 'rgba' | 'dataURL'}})`, `clawd.select([...])`, `clawd.selectAll()`, `clawd.invert()`, `clawd.selected()`, `clawd.open(n)`, `await clawd.zip([...])`.

## Optional

- [Full catalog as text]({u('llms-full.txt')}): one line per GIF
- [Source code, skills and engine]({self.repo or 'https://github.com/'}): MIT. The Python engine that draws Clawd, and the Claude Code skills `clawd-pixel` and `clawd-halftone`
""")
        rows = [f"{r['n']:03d} | {r['slug']} | {r['name']['zh']} | {r['name']['en']} | {r['theme']['id']} | "
                f"{r['frames']['count']} frames | {r['frames']['total_ms']} ms | {r['gif']['url']}" for r in recs]
        self.write('llms-full.txt', '# Clawd 400 — full catalog\n\n'
                   '> nnn | slug | 中文 | English | theme | frames | loop length | GIF URL. Per-GIF JSON: api/gifs/{nnn}.json; ASCII frames: api/frames/{nnn}.txt\n\n'
                   + '\n'.join(rows) + '\n')
        if self.base:
            urls = [u(''), u('llms.txt'), u('api/index.json')] + [r['links']['page'] for r in recs]
            self.write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                       + '\n'.join(f'<url><loc>{html.escape(x)}</loc></url>' for x in urls) + '\n</urlset>\n')
        self.write('robots.txt', 'User-agent: *\nAllow: /\n' + (f"Sitemap: {u('sitemap.xml')}\n" if self.base else ''))

    def zip_all(self, recs):
        p = os.path.join(self.out, 'downloads', 'clawd-400.zip')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with zipfile.ZipFile(p, 'w', zipfile.ZIP_STORED) as z:
            for r in recs:
                z.write(os.path.join(ROOT, 'gifs', r['gif']['file']), f"clawd-400/{r['theme']['zh']}/{r['gif']['zh_file']}")
            z.writestr('clawd-400/manifest.json', json.dumps([{k: r[k] for k in ('n', 'slug', 'name', 'theme')} | {'file': f"{r['theme']['zh']}/{r['gif']['zh_file']}", 'frames': r['frames']['count'], 'durations_ms': r['frames']['durations_ms']} for r in recs], ensure_ascii=False, indent=1))
            z.writestr('clawd-400/LICENSE.txt', license_note(self.repo))


def license_note(repo):
    return (f'Clawd 400 by {AUTHOR}\n{repo}\n\nThe GIFs are licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/\n'
            'You may use, share and adapt them, commercially too, if you credit: "Clawd 400 by ' + AUTHOR + ' — CC BY 4.0".\n\n'
            'Unofficial fan art. Claude, Claude Code and the Clawd character are trademarks of Anthropic;\n'
            'this licence grants no rights to them. Check with Anthropic before commercial use of the character.\n')


def openapi(base):
    def get(summary, ctype, params=None):
        op = {'get': {'summary': summary, 'responses': {'200': {'description': 'OK', 'content': {ctype: {}}}}}}
        if params:
            op['get']['parameters'] = [{'name': p, 'in': 'path', 'required': True, 'schema': {'type': 'string'}} for p in params]
        return op
    return {
        'openapi': '3.1.0',
        'info': {'title': 'Clawd 400 static API', 'version': '1.0.0',
                 'description': 'Read-only static files. nnn = GIF number 001-400. No auth, CORS as served by GitHub Pages.'},
        'servers': [{'url': base or '/'}],
        'paths': {
            '/api/index.json': get('Catalog of all 400 GIFs', 'application/json'),
            '/api/themes.json': get('The 8 themes with counts', 'application/json'),
            '/api/gifs/{nnn}.json': get('One GIF: titles, frames, durations, palette, bbox, file info, source', 'application/json', ['nnn']),
            '/api/frames/{nnn}.txt': get('Every frame as a 40x40 character grid with a palette legend', 'text/plain', ['nnn']),
            '/sheets/{nnn}.png': get('All frames side by side at 40x40', 'image/png', ['nnn']),
            '/gifs/{file}': get('The GIF (480x480, transparent)', 'image/gif', ['file']),
            '/downloads/clawd-400.zip': get('All 400 GIFs with manifest and licence', 'application/zip'),
        },
    }


def favicon():
    """Clawd's front view from the engine, as an SVG of pixel rects."""
    f = engine.Canvas()
    engine.clawd(f)
    cells = [(x, y, c) for y, row in enumerate(f.px) for x, c in enumerate(row) if c is not None]
    x0 = min(x for x, _, _ in cells); x1 = max(x for x, _, _ in cells) + 1
    y0 = min(y for _, y, _ in cells); y1 = max(y for _, y, _ in cells) + 1
    s = max(x1 - x0, y1 - y0)
    ox, oy = x0 - (s - (x1 - x0)) / 2, y0 - (s - (y1 - y0)) / 2
    rects = ''.join(f'<rect x="{x - ox:g}" y="{y - oy:g}" width="1.02" height="1.02" fill="{hexc(c)}"/>' for x, y, c in cells)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" shape-rendering="crispEdges">{rects}</svg>\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, '_site'))
    ap.add_argument('--base-url', default=os.environ.get('CLAWD_BASE_URL', ''))
    ap.add_argument('--repo-url', default=os.environ.get('CLAWD_REPO_URL', ''))
    a = ap.parse_args()
    if os.path.exists(a.out):                     # empty it rather than delete it: a preview server may be serving it
        for name in os.listdir(a.out):
            p = os.path.join(a.out, name)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(os.path.join(a.out, 'gifs'), exist_ok=True)
    site = Site(a.out, a.base_url, a.repo_url)
    built = datetime.now(timezone.utc).isoformat(timespec='seconds')
    man = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
    recs = [site.item(m) for m in man]
    for i, r in enumerate(recs):
        site.detail_page(r, recs[i - 1] if i else None, recs[i + 1] if i + 1 < len(recs) else None)
    site.zip_all(recs)
    site.api(recs, built)
    site.index(recs, built)
    for f in ('app.js', 'app.css', 'detail.css'):
        shutil.copyfile(os.path.join(HERE, 'src', f), os.path.join(a.out, f))
    site.write('favicon.svg', favicon())
    og = os.path.join(ROOT, 'films', 'covers', 'og.png')
    if os.path.exists(og):
        shutil.copyfile(og, os.path.join(a.out, 'og.png'))
    site.write('.nojekyll', '')
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(a.out) for f in fs)
    print(f'{len(recs)} GIFs -> {a.out} ({total / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
