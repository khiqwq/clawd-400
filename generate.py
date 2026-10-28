"""Render every registered scene to gifs/NNN_slug.gif plus manifest.json and index.html."""
import hashlib
import html
import importlib
import json
import os
import sys
from multiprocessing import Pool

import engine
from scenes import ORDER, EXCLUDE

OUT = 'gifs'


THEMES = {'video': '视频重现 · Video loops', 'summer': '夏日篇 · Summer', 'emotions': '情绪 · Feelings',
          'life': '日常 · Daily life', 'dev': '编程 · Coding', 'sports': '运动 · Sports',
          'costumes': '角色扮演 · Costumes', 'seasons': '节日季节 · Seasons'}


def load():
    for m in ORDER:
        if os.path.exists(os.path.join('scenes', m + '.py')):
            start = len(engine.REG)
            importlib.import_module(f'scenes.{m}')
            for e in engine.REG[start:]:
                e['theme'] = m
    engine.REG[:] = [e for e in engine.REG if e['slug'] not in EXCLUDE]
    return engine.REG


def work(i):
    reg = engine.REG or load()
    e = reg[i]
    frames = engine.render(e)
    name = f'{i + 1:03d}_{e["slug"]}.gif'
    engine.save_gif(frames, os.path.join(OUT, name), e['dur'])
    h = hashlib.md5()
    for fr in frames:
        h.update(repr(fr.px).encode())
    return i, name, h.hexdigest(), len(frames)


def main():
    reg = load()
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.gif'):
            os.remove(os.path.join(OUT, f))
    slugs = [e['slug'] for e in reg]
    dups = sorted({s for s in slugs if slugs.count(s) > 1})
    if dups:
        sys.exit(f'duplicate slugs: {dups}')
    with Pool() as pool:
        res = sorted(pool.map(work, range(len(reg))))
    seen, same = {}, []
    manifest = []
    for i, name, digest, n in res:
        e = reg[i]
        if digest in seen:
            same.append((seen[digest], name))
        seen.setdefault(digest, name)
        manifest.append(dict(n=i + 1, file=f'{OUT}/{name}', slug=e['slug'], theme=e.get('theme', ''), zh=e['zh'], en=e['en'],
                             frames=n, ms=e['dur'] if isinstance(e['dur'], int) else sum(e['dur'])))
    json.dump(manifest, open('manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    write_html(manifest)
    print(f'{len(reg)} gifs written; identical animations: {same or "none"}')


def write_html(items):
    parts, cur = [], None
    for it in items:
        if it['theme'] != cur:
            cur = it['theme']
            count = sum(1 for x in items if x['theme'] == cur)
            parts.append(f'<h2>{html.escape(THEMES.get(cur, cur))} <small>{count}</small></h2>')
        parts.append(
            f'<figure><img src="{html.escape(it["file"])}" loading="lazy" alt="{html.escape(it["en"])}">'
            f'<figcaption><b>{it["n"]:03d}</b> {html.escape(it["zh"])}<br><span>{html.escape(it["en"])}</span>'
            f'</figcaption></figure>')
    cards = '\n'.join(parts)
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Clawd 400</title>
<style>
:root{{--bg:#faf8f5;--card:#fff;--ink:#2b2622;--mute:#8a817a;--line:#ece6df;--tile:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1b1917;--card:#24211f;--ink:#f1ece6;--mute:#9b928a;--line:#34302c;--tile:#24211f}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,"Microsoft YaHei",sans-serif}}
header{{padding:24px 16px 8px;max-width:1400px;margin:auto}}
h1{{margin:0 0 4px;font-size:22px}} header p{{margin:0;color:var(--mute)}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:12px}}
input{{flex:1;min-width:180px;max-width:360px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}}
button{{padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);cursor:pointer}}
button.on{{outline:2px solid #e37e52}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;padding:8px 16px 32px;max-width:1400px;margin:auto}}
h2{{grid-column:1/-1;margin:20px 0 0;font-size:17px}} h2 small{{color:var(--mute);font-weight:400}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}}
img{{width:100%;aspect-ratio:1;image-rendering:pixelated;display:block;background:var(--tile);border-radius:6px}}
body.dark img{{background:#1c1a19}} body.light img{{background:#fff}}
body.check img{{background:repeating-conic-gradient(#ddd 0 25%,#fff 0 50%) 0 0/24px 24px}}
figcaption{{font-size:12px;margin-top:4px}} figcaption span{{color:var(--mute)}}
</style></head><body>
<header><h1>Clawd 400</h1><p>{len(items)} 个像素动图 · 480×480 · 透明背景</p>
<div class="bar"><input id="q" placeholder="搜索 / search…">
<button data-bg="">跟随主题</button><button data-bg="light">白底</button><button data-bg="dark">深色底</button><button data-bg="check">透明格</button></div></header>
<main id="g">{cards}</main>
<script>
const q=document.getElementById('q');q.oninput=()=>{{const v=q.value.toLowerCase();
for(const f of document.querySelectorAll('figure'))f.style.display=f.textContent.toLowerCase().includes(v)?'':'none'}};
const bs=document.querySelectorAll('button[data-bg]');
function setBg(v){{document.body.className=v;bs.forEach(b=>b.classList.toggle('on',b.dataset.bg===v));try{{localStorage.setItem('bg',v)}}catch(e){{}}}}
bs.forEach(b=>b.onclick=()=>setBg(b.dataset.bg));
let saved='';try{{saved=localStorage.getItem('bg')||''}}catch(e){{}}setBg(saved);
</script></body></html>"""
    open('index.html', 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    main()
