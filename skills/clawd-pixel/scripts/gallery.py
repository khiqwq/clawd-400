"""Build index.html next to a folder of GIFs: python gallery.py out/ [--title "Clawd"]

Titles come from manifest.json (list of {file, zh, en}) when present, else from file names.
"""
import argparse
import html
import json
import os


def build(folder, title):
    folder = os.path.abspath(folder)
    parent = os.path.dirname(folder)
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith(('.gif', '.webp')))
    meta = {}
    man = os.path.join(parent, 'manifest.json')
    if os.path.exists(man):
        for it in json.load(open(man, encoding='utf-8')):
            meta[os.path.basename(it['file'])] = it
    rel = os.path.basename(folder)
    cards = []
    for n in names:
        it = meta.get(n, {})
        zh = it.get('zh', os.path.splitext(n)[0])
        en = it.get('en', '')
        cards.append(f'<figure><img src="{html.escape(rel)}/{html.escape(n)}" loading="lazy" alt="{html.escape(en or zh)}">'
                     f'<figcaption>{html.escape(zh)}<br><span>{html.escape(en)}</span></figcaption></figure>')
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>
:root{{--bg:#faf8f5;--card:#fff;--ink:#2b2622;--mute:#8a817a;--line:#ece6df}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1b1917;--card:#24211f;--ink:#f1ece6;--mute:#9b928a;--line:#34302c}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,"Microsoft YaHei",sans-serif}}
header{{padding:20px 16px 0;max-width:1400px;margin:auto}} h1{{margin:0;font-size:20px}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}
input,button{{padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}}
button.on{{outline:2px solid #e37e52}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;padding:16px;max-width:1400px;margin:auto}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}}
img{{width:100%;aspect-ratio:1;image-rendering:pixelated;display:block;border-radius:6px}}
body.dark img{{background:#1c1a19}} body.light img{{background:#fff}}
body.check img{{background:repeating-conic-gradient(#ddd 0 25%,#fff 0 50%) 0 0/24px 24px}}
figcaption{{font-size:12px;margin-top:4px}} figcaption span{{color:var(--mute)}}
</style></head><body><header><h1>{html.escape(title)} · {len(names)}</h1>
<div class="bar"><input id="q" placeholder="搜索 / search"><button data-bg="">跟随主题</button>
<button data-bg="light">白底</button><button data-bg="dark">深色底</button><button data-bg="check">透明格</button></div></header>
<main>{''.join(cards)}</main><script>
const q=document.getElementById('q');q.oninput=()=>{{const v=q.value.toLowerCase();
for(const f of document.querySelectorAll('figure'))f.style.display=f.textContent.toLowerCase().includes(v)?'':'none'}};
const bs=document.querySelectorAll('button[data-bg]');
function setBg(v){{document.body.className=v;bs.forEach(b=>b.classList.toggle('on',b.dataset.bg===v))}}
bs.forEach(b=>b.onclick=()=>setBg(b.dataset.bg));setBg('');
</script></body></html>"""
    out = os.path.join(parent, 'index.html')
    open(out, 'w', encoding='utf-8').write(page)
    print('wrote', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('folder')
    ap.add_argument('--title', default='Clawd')
    a = ap.parse_args()
    build(a.folder, a.title)
