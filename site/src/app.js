/* Clawd 400 gallery: filter, select (all / invert / clear / shift-range), ZIP download, drag-out,
   frame-by-frame viewer, and window.clawd for scripts and AI agents. No dependencies. */
(() => {
  'use strict';
  const BOOT = JSON.parse(document.getElementById('clawd-boot').textContent);
  const G = BOOT.grid, SCALE = BOOT.scale;
  const ITEMS = BOOT.items.map(it => ({ ...it, nnn: String(it.n).padStart(3, '0'), ms: it.d.reduce((a, b) => a + b, 0) }));
  const BY_N = new Map(ITEMS.map(it => [it.n, it]));
  const BY_SLUG = new Map(ITEMS.map(it => [it.s, it]));
  const THEME = new Map(BOOT.themes.map(t => [t.id, t]));
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const abs = rel => new URL(rel, document.baseURI).href;
  const CARDS = new Map($$('.card').map(c => [+c.dataset.n, c]));
  const SECS = new Map($$('.sec').map(h => [h.dataset.theme, h]));
  const root = document.documentElement;

  const store = {
    get(k, d) { try { return localStorage.getItem('clawd.' + k) ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem('clawd.' + k, v); } catch { /* private mode */ } },
  };
  const state = { theme: 'all', q: '', selecting: false, selected: new Set(), anchor: null };

  function find(key) {
    if (key && typeof key === 'object') key = key.n ?? key.slug;
    if (typeof key === 'number' || /^\d+$/.test(String(key))) return BY_N.get(+key) || null;
    return BY_SLUG.get(String(key)) || null;
  }

  let toastTimer;
  function toast(msg, ms = 1800) {
    const t = $('#toast');
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { t.hidden = true; }, ms);
  }

  // ------------------------------------------------------------------ look: theme, tile backdrop, size
  $('#themeBtn').addEventListener('click', () => {
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    store.set('theme', root.dataset.theme);
  });
  const bgButtons = $$('#bgSeg button');
  function setBg(v) {
    root.dataset.bg = v; store.set('bg', v);
    bgButtons.forEach(b => b.classList.toggle('on', b.dataset.bg === v));
  }
  bgButtons.forEach(b => b.addEventListener('click', () => setBg(b.dataset.bg)));
  setBg(root.dataset.bg || 'paper');
  const size = $('#size');
  size.value = parseInt(getComputedStyle(root).getPropertyValue('--tile')) || 168;
  size.addEventListener('input', () => { root.style.setProperty('--tile', size.value + 'px'); store.set('size', size.value); });

  // ------------------------------------------------------------------ filter
  const chips = $('#chips');
  chips.innerHTML = [`<button class="chip on" data-theme="all" role="tab">全部 <small>${ITEMS.length}</small></button>`]
    .concat(BOOT.themes.map(t => `<button class="chip" data-theme="${t.id}" role="tab" title="${t.en}">${t.zh} <small>${t.count}</small></button>`)).join('');
  chips.addEventListener('click', e => {
    const c = e.target.closest('.chip'); if (!c) return;
    setFilter({ theme: c.dataset.theme });
  });
  const q = $('#q');
  q.addEventListener('input', () => setFilter({ q: q.value }));

  function matches(it, f = state) {
    if (f.theme && f.theme !== 'all' && it.t !== f.theme) return false;
    const s = (f.q || '').trim().toLowerCase();
    if (!s) return true;
    const th = THEME.get(it.t);
    const hay = `${it.nnn} ${it.n} ${it.s} ${it.s.replace(/_/g, ' ')} ${it.zh} ${it.en} ${it.t} ${th ? th.zh + ' ' + th.en : ''}`.toLowerCase();
    return s.replace(/^#/, '').split(/\s+/).every(w => hay.includes(w));
  }
  const visible = () => ITEMS.filter(it => matches(it));

  function setFilter({ theme, q: text } = {}) {
    if (theme !== undefined) state.theme = theme;
    if (text !== undefined) { state.q = text; if (q.value !== text) q.value = text; }
    $$('.chip', chips).forEach(c => c.classList.toggle('on', c.dataset.theme === state.theme));
    const shown = new Map();
    for (const it of ITEMS) {
      const ok = matches(it);
      CARDS.get(it.n).hidden = !ok;
      if (ok) shown.set(it.t, (shown.get(it.t) || 0) + 1);
    }
    for (const [t, h] of SECS) h.hidden = !shown.has(t);
    $('#empty').hidden = shown.size > 0;
    renderSel();
  }

  // ------------------------------------------------------------------ selection
  const selbar = $('#selbar'), selBtn = $('#selBtn');
  function setSelecting(on) {
    state.selecting = on;
    document.body.classList.toggle('selecting', on);
    selBtn.setAttribute('aria-pressed', on);
    selbar.hidden = !on;
    renderSel();
  }
  selBtn.addEventListener('click', () => setSelecting(!state.selecting));
  $('#selExit').addEventListener('click', () => setSelecting(false));
  $('#selAll').addEventListener('click', () => { visible().forEach(it => state.selected.add(it.n)); renderSel(); });
  $('#selInvert').addEventListener('click', () => {
    visible().forEach(it => state.selected.has(it.n) ? state.selected.delete(it.n) : state.selected.add(it.n)); renderSel();
  });
  $('#selClear').addEventListener('click', () => { state.selected.clear(); state.anchor = null; renderSel(); });
  $('#selZip').addEventListener('click', () => downloadZip([...state.selected]));

  function toggle(n, force) {
    const on = force ?? !state.selected.has(n);
    on ? state.selected.add(n) : state.selected.delete(n);
  }
  function range(a, b) {
    const vis = visible().map(it => it.n);
    let i = vis.indexOf(a), j = vis.indexOf(b);
    if (i < 0 || j < 0) return [b];
    if (i > j) [i, j] = [j, i];
    return vis.slice(i, j + 1);
  }
  function renderSel() {
    for (const [n, c] of CARDS) {
      const on = state.selected.has(n);
      if (c.classList.contains('sel') !== on) c.classList.toggle('sel', on);
      if (state.selecting) c.setAttribute('aria-selected', on); else c.removeAttribute('aria-selected');
    }
    const k = state.selected.size;
    $('#selCount').textContent = k;
    $('#selTotal').textContent = visible().length;
    const z = $('#selZip'); z.disabled = k === 0;
    $('span', z).textContent = k ? `下载 ZIP (${k})` : '下载 ZIP';
    if (viewer.open && V.it) $('#vPick').textContent = state.selected.has(V.it.n) ? '取消选择' : '加入选择';
  }

  // ------------------------------------------------------------------ cards: click, keys, long press
  const grid = $('#grid');
  let pressTimer, suppressClick = false;
  function activate(card, e) {
    const n = +card.dataset.n;
    if (state.selecting) {
      if (e && e.shiftKey && state.anchor != null) range(state.anchor, n).forEach(m => toggle(m, true));
      else toggle(n);
      state.anchor = n;
      renderSel();
    } else openViewer(n);
  }
  grid.addEventListener('click', e => {
    const card = e.target.closest('.card'); if (!card) return;
    const link = e.target.closest('a.cap');
    if (link && !state.selecting && (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1)) return;  // open in a new tab
    if (suppressClick) { suppressClick = false; e.preventDefault(); return; }
    e.preventDefault();
    if (!state.selecting && (e.ctrlKey || e.metaKey)) { setSelecting(true); }
    activate(card, e);
  });
  grid.addEventListener('keydown', e => {
    const card = e.target.closest('.card'); if (!card || e.target.closest('a')) return;
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(card, e); }
  });
  grid.addEventListener('pointerdown', e => {
    const card = e.target.closest('.card'); if (!card || e.pointerType === 'mouse') return;
    pressTimer = setTimeout(() => {
      if (!state.selecting) setSelecting(true);
      toggle(+card.dataset.n, true); state.anchor = +card.dataset.n; renderSel();
      suppressClick = true; navigator.vibrate?.(15);
    }, 480);
  });
  ['pointerup', 'pointercancel', 'pointermove'].forEach(t => grid.addEventListener(t, e => {
    if (t !== 'pointermove' || Math.abs(e.movementX) + Math.abs(e.movementY) > 6) clearTimeout(pressTimer);
  }));

  // ------------------------------------------------------------------ drag out of the browser
  const zhUrl = it => 'zh/' + encodeURIComponent(it.z);                   // the GIF under its Chinese title: 一脸问号.gif
  const themeZh = it => THEME.get(it.t)?.zh || it.t;
  function dragData(dt, it) {
    const url = abs(zhUrl(it));
    dt.effectAllowed = 'copy';
    dt.setData('DownloadURL', `image/gif:${it.z}:${url}`);                 // Chrome / Edge: drop on the desktop = 一脸问号.gif
    dt.setData('text/uri-list', url);
    dt.setData('text/plain', url);
    dt.setData('text/html', `<img src="${url}" alt="${it.en}" width="480" height="480">`);
    try { dt.setData('application/x-moz-file-promise-url', url); dt.setData('application/x-moz-file-promise-dest-filename', it.z); } catch { /* not Firefox */ }
  }
  grid.addEventListener('dragstart', e => {
    const card = e.target.closest('.card'); if (!card) return;
    const img = $('img', card);
    dragData(e.dataTransfer, BY_N.get(+card.dataset.n));
    if (e.target !== img) e.dataTransfer.setDragImage(img, img.width / 2, img.height / 2);
  });

  // ------------------------------------------------------------------ ZIP (stored, no compression: GIF/PNG already are)
  const CRC = new Uint32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  function crc32(u8) { let c = 0xFFFFFFFF; for (let i = 0; i < u8.length; i++) c = CRC[(c ^ u8[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
  function makeZip(files) {
    const enc = new TextEncoder(), parts = [], central = [];
    const d = new Date(), time = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
    const date = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
    let offset = 0;
    for (const f of files) {
      const name = enc.encode(f.name), data = f.data instanceof Uint8Array ? f.data : enc.encode(f.data);
      const crc = crc32(data), lh = new DataView(new ArrayBuffer(30)), ch = new DataView(new ArrayBuffer(46));
      lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true); lh.setUint16(6, 0x0800, true);
      lh.setUint16(10, time, true); lh.setUint16(12, date, true); lh.setUint32(14, crc, true);
      lh.setUint32(18, data.length, true); lh.setUint32(22, data.length, true); lh.setUint16(26, name.length, true);
      ch.setUint32(0, 0x02014b50, true); ch.setUint16(4, 20, true); ch.setUint16(6, 20, true); ch.setUint16(8, 0x0800, true);
      ch.setUint16(12, time, true); ch.setUint16(14, date, true); ch.setUint32(16, crc, true);
      ch.setUint32(20, data.length, true); ch.setUint32(24, data.length, true); ch.setUint16(28, name.length, true); ch.setUint32(42, offset, true);
      parts.push(lh, name, data); central.push(ch, name);
      offset += 30 + name.length + data.length;
    }
    const size = central.reduce((s, p) => s + p.byteLength, 0), end = new DataView(new ArrayBuffer(22));
    end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
    end.setUint32(12, size, true); end.setUint32(16, offset, true);
    return new Blob([...parts, ...central, end], { type: 'application/zip' });
  }
  const bytes = async url => new Uint8Array(await (await fetch(url)).arrayBuffer());
  function saveBlob(blob, name) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  function licenseText(list) {
    return `Clawd 400 — ${list.length} GIF${list.length > 1 ? 's' : ''}\n${BOOT.repo || location.href}\n\n` +
      `CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/\nCredit: "${BOOT.credit}"\n\n` +
      'Unofficial fan art. Claude, Claude Code and the Clawd character are trademarks of Anthropic;\n' +
      'the licence grants no rights to them. Check with Anthropic before commercial use of the character.\n\n' +
      list.map(it => `${it.nnn}  ${themeZh(it)}/${it.z}  ${it.en}`).join('\n') + '\n';
  }
  async function zipBlob(keys) {
    const list = keys.map(find).filter(Boolean).sort((a, b) => a.n - b.n);
    if (!list.length) throw new Error('nothing selected');
    const files = [];
    let done = 0;
    await Promise.all(list.map(async it => {
      files.push({ n: it.n, name: `clawd-400/${themeZh(it)}/${it.z}`, data: await bytes('gifs/' + it.f) });
      zipProgress(++done, list.length);
    }));
    files.sort((a, b) => a.n - b.n);
    files.push({ name: 'clawd-400/LICENSE.txt', data: licenseText(list) });
    files.push({ name: 'clawd-400/manifest.json', data: JSON.stringify(list.map(it => ({ n: it.n, slug: it.s, zh: it.zh, en: it.en, theme: it.t, file: `${themeZh(it)}/${it.z}`, durations_ms: it.d })), null, 1) });
    return { blob: makeZip(files), list };
  }
  let zipBusy = false;
  function zipProgress(k, n) { const s = $('#selZip span'); if (zipBusy && s) s.textContent = `打包中 ${k}/${n}`; }
  async function downloadZip(keys) {
    if (zipBusy) return;
    zipBusy = true; $('#selZip').disabled = true;
    try {
      const { blob, list } = await zipBlob(keys);
      saveBlob(blob, list.length === ITEMS.length ? 'clawd-400.zip' : `clawd-400_${list.length}.zip`);
      toast(`已打包 ${list.length} 个动图（${(blob.size / 1e6).toFixed(1)} MB）`);
    } catch (err) { toast('打包失败：' + err.message, 3000); }
    finally { zipBusy = false; renderSel(); }
  }

  // ------------------------------------------------------------------ frames from the sheet (native 40x40)
  const sheets = new Map();
  function sheet(it) {
    if (!sheets.has(it.n)) sheets.set(it.n, new Promise((ok, bad) => {
      const im = new Image(); im.onload = () => ok(im); im.onerror = () => bad(new Error('sheet ' + it.nnn)); im.src = `sheets/${it.nnn}.png`;
    }));
    return sheets.get(it.n);
  }
  function pixels(im) {
    const c = document.createElement('canvas'); c.width = im.width; c.height = G;
    const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(im, 0, 0);
    return x.getImageData(0, 0, im.width, G).data;
  }
  function frameCanvas(im, i, scale = 1) {
    const c = document.createElement('canvas'); c.width = c.height = G * scale;
    const x = c.getContext('2d'); x.imageSmoothingEnabled = false;
    x.drawImage(im, i * G, 0, G, G, 0, 0, G * scale, G * scale);
    return c;
  }

  // ------------------------------------------------------------------ viewer
  const viewer = $('#viewer'), canvas = $('#vCanvas'), ctx = canvas.getContext('2d');
  const V = { it: null, im: null, i: 0, playing: true, speed: 1, onion: false, grid: false, acc: 0, last: 0, raf: 0, pushed: false };
  ctx.imageSmoothingEnabled = false;

  function draw() {
    const { im, i, it } = V; if (!im) return;
    const S = canvas.width / G;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.imageSmoothingEnabled = false;
    if (V.onion && it.d.length > 1) {
      ctx.globalAlpha = .28;
      ctx.drawImage(im, ((i - 1 + it.d.length) % it.d.length) * G, 0, G, G, 0, 0, canvas.width, canvas.height);
      ctx.globalAlpha = 1;
    }
    ctx.drawImage(im, i * G, 0, G, G, 0, 0, canvas.width, canvas.height);
    if (V.grid) {
      ctx.beginPath();
      for (let k = 1; k < G; k++) { ctx.moveTo(k * S + .5, 0); ctx.lineTo(k * S + .5, canvas.height); ctx.moveTo(0, k * S + .5); ctx.lineTo(canvas.width, k * S + .5); }
      ctx.strokeStyle = root.dataset.bg === 'dark' ? 'rgba(255,255,255,.09)' : 'rgba(0,0,0,.08)'; ctx.lineWidth = 1; ctx.stroke();
    }
    $('#vFrame').textContent = `帧 ${i + 1} / ${it.d.length} · ${it.d[i]} ms`;
    $$('#vStrip button').forEach((b, k) => b.classList.toggle('on', k === i));
    const strip = $('#vStrip'), cur = $('button.on', strip);            // keep the current frame in view, horizontally only
    if (cur) {
      const b = cur.getBoundingClientRect(), s = strip.getBoundingClientRect();
      if (b.left < s.left) strip.scrollLeft += b.left - s.left - 12;
      else if (b.right > s.right) strip.scrollLeft += b.right - s.right + 12;
    }
  }
  function loop(ts) {
    if (!V.playing || !viewer.open) return;
    if (!V.last) V.last = ts;
    V.acc += (ts - V.last) * V.speed; V.last = ts;
    let changed = false;
    while (V.acc >= V.it.d[V.i]) { V.acc -= V.it.d[V.i]; V.i = (V.i + 1) % V.it.d.length; changed = true; }
    if (changed) draw();
    V.raf = requestAnimationFrame(loop);
  }
  function play(on) {
    V.playing = on; $('#vPlay').classList.toggle('paused', !on);
    cancelAnimationFrame(V.raf); V.last = 0; V.acc = 0;
    if (on) V.raf = requestAnimationFrame(loop);
  }
  function step(k) { play(false); V.i = (V.i + k + V.it.d.length) % V.it.d.length; draw(); }

  async function openViewer(key, { push = true } = {}) {
    const it = find(key); if (!it) return null;
    V.it = it; V.i = 0; V.im = null;
    const th = THEME.get(it.t);
    $('#vNum').textContent = '#' + it.nnn;
    $('#vTitle').textContent = it.zh;
    $('#vEn').textContent = it.en;
    const gifUrl = zhUrl(it);
    $('#vGif').src = gifUrl; $('#vGif').alt = it.en;
    $('#vDl').href = gifUrl; $('#vDl').setAttribute('download', it.z);
    $('#vSheet').href = `sheets/${it.nnn}.png`; $('#vSheet').setAttribute('download', `${it.zh}_帧序列.png`);
    $('#vJson').href = `api/gifs/${it.nnn}.json`; $('#vAscii').href = `api/frames/${it.nnn}.txt`;
    const maxD = Math.max(...it.d);
    $('#vStrip').innerHTML = it.d.map((d, i) =>
      `<li><button type="button" data-i="${i}" title="帧 ${i + 1} · ${d} ms"><i style="--i:${i};--n:${it.d.length};background-image:url(sheets/${it.nnn}.png)"></i>${i + 1}<b style="--w:${Math.max(8, Math.round(72 * d / maxD))}px"></b></button></li>`).join('');
    $('#vFacts').innerHTML = `
      <dt>主题</dt><dd>${th ? th.zh + ' · ' + th.en : it.t}</dd>
      <dt>帧数</dt><dd>${it.d.length} 帧 · 一圈 ${it.ms} ms</dd>
      <dt>帧时长</dt><dd>${[...new Set(it.d)].length === 1 ? `每帧 ${it.d[0]} ms` : it.d.join(' · ') + ' ms'}</dd>
      <dt>尺寸</dt><dd>480×480 · ${G}×${G} 像素 ×${SCALE}</dd>
      <dt>文件</dt><dd>${it.z} · ${(it.b / 1024).toFixed(1)} KB</dd>
      <dt>编号</dt><dd>${it.s}</dd>`;
    $('#vPal').innerHTML = '';
    if (!viewer.open) { viewer.showModal(); canvas.focus({ preventScroll: true }); V.pushed = false; }
    if (push) { history.pushState({ gif: it.n }, '', `#/gif/${it.n}`); V.pushed = true; }
    renderSel();
    try {
      const im = await sheet(it);
      if (V.it !== it) return it;
      V.im = im;
      // palette from the sheet itself
      const px = pixels(im), cols = new Map();
      for (let p = 0; p < px.length; p += 4) if (px[p + 3] > 127) { const h = '#' + [px[p], px[p + 1], px[p + 2]].map(v => v.toString(16).padStart(2, '0')).join(''); cols.set(h, (cols.get(h) || 0) + 1); }
      $('#vPal').innerHTML = [...cols].sort((a, b) => b[1] - a[1]).map(([h]) => `<span style="background:${h}" title="${h}"></span>`).join('');
      draw(); play(true);
    } catch (err) { toast(err.message, 3000); }
    return it;
  }
  function closeViewer() { if (viewer.open) viewer.close(); }
  viewer.addEventListener('close', () => {
    play(false);
    if (/^#\/gif\//.test(location.hash)) {
      if (V.pushed) history.back();                       // the entry openViewer pushed
      else history.replaceState({}, '', location.pathname + location.search);
    }
    V.pushed = false;
    if (V.it) CARDS.get(V.it.n)?.focus({ preventScroll: false });
  });
  viewer.addEventListener('click', e => { if (e.target === viewer) closeViewer(); });       // backdrop
  $('#vClose').addEventListener('click', closeViewer);
  const neighbour = k => { const vis = visible(), i = vis.findIndex(x => x.n === V.it.n), list = i < 0 ? ITEMS : vis, j = i < 0 ? ITEMS.indexOf(V.it) : i; return list[(j + k + list.length) % list.length]; };
  $('#vPrevGif').addEventListener('click', () => openViewer(neighbour(-1).n, { push: false }).then(it => it && history.replaceState({ gif: it.n }, '', `#/gif/${it.n}`)));
  $('#vNextGif').addEventListener('click', () => openViewer(neighbour(1).n, { push: false }).then(it => it && history.replaceState({ gif: it.n }, '', `#/gif/${it.n}`)));
  $('#vPlay').addEventListener('click', () => play(!V.playing));
  $('#vStep').addEventListener('click', () => step(1));
  $('#vStepBack').addEventListener('click', () => step(-1));
  $('#vStrip').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; play(false); V.i = +b.dataset.i; draw(); });
  const speedBtns = $$('#vSpeed button');
  function setSpeed(s) { V.speed = s; speedBtns.forEach(b => b.classList.toggle('on', +b.dataset.speed === s)); V.acc = 0; }
  speedBtns.forEach(b => b.addEventListener('click', () => setSpeed(+b.dataset.speed)));
  setSpeed(1);
  const flag = (id, key) => $(id).addEventListener('click', () => { V[key] = !V[key]; $(id).setAttribute('aria-pressed', V[key]); draw(); });
  flag('#vOnion', 'onion'); flag('#vGrid', 'grid');
  $('#vPick').addEventListener('click', () => { toggle(V.it.n); if (!state.selecting && state.selected.size) setSelecting(true); renderSel(); });
  $('#vCopy').addEventListener('click', async () => {
    const url = abs(`#/gif/${V.it.n}`);
    try { await navigator.clipboard.writeText(url); toast('链接已复制'); } catch { prompt('复制链接', url); }
  });
  $('#vFramesZip').addEventListener('click', async () => {
    const it = V.it, im = await sheet(it), files = [];
    for (let i = 0; i < it.d.length; i++) {
      const blob = await new Promise(r => frameCanvas(im, i, SCALE).toBlob(r, 'image/png'));
      files.push({ name: `${it.zh}/帧${String(i + 1).padStart(2, '0')}_${it.d[i]}ms.png`, data: new Uint8Array(await blob.arrayBuffer()) });
    }
    files.push({ name: `${it.zh}/${it.z}`, data: await bytes('gifs/' + it.f) });
    files.push({ name: `${it.zh}/LICENSE.txt`, data: licenseText([it]) });
    saveBlob(makeZip(files), `${it.zh}_逐帧.zip`);
  });
  $('#vGif').addEventListener('dragstart', e => dragData(e.dataTransfer, V.it));

  // ------------------------------------------------------------------ keyboard
  document.addEventListener('keydown', e => {
    if (e.target.closest('input, textarea') && e.key !== 'Escape') return;
    if (viewer.open) {
      const k = e.key;
      if (k === ' ') { e.preventDefault(); play(!V.playing); }
      else if (k === 'ArrowRight') { e.preventDefault(); step(1); }
      else if (k === 'ArrowLeft') { e.preventDefault(); step(-1); }
      else if (k === 'PageDown' || k === ']') { e.preventDefault(); $('#vNextGif').click(); }
      else if (k === 'PageUp' || k === '[') { e.preventDefault(); $('#vPrevGif').click(); }
      else if (k === 'o' || k === 'O') $('#vOnion').click();
      else if (k === 'g' || k === 'G') $('#vGrid').click();
      return;
    }
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) { e.preventDefault(); q.focus(); q.select(); }
    else if (e.key === 'Escape') { if (document.activeElement === q && q.value) setFilter({ q: '' }); else if (state.selecting) setSelecting(false); }
    else if (state.selecting && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'a') { e.preventDefault(); $('#selAll').click(); }
  });

  // ------------------------------------------------------------------ routing: #/gif/12, #/theme/dev, #/q/word
  function route({ push = false } = {}) {
    const h = decodeURIComponent(location.hash);
    let m;
    if ((m = h.match(/^#\/gif\/([\w-]+)/))) { openViewer(m[1], { push }); return; }
    if ((m = h.match(/^#\/theme\/(\w+)/))) setFilter({ theme: m[1] });
    if ((m = h.match(/^#\/q\/(.+)/))) setFilter({ q: m[1] });
    closeViewer();
  }
  addEventListener('popstate', () => route());

  // ------------------------------------------------------------------ window.clawd: the API for scripts and AI agents
  const pub = it => it && ({
    n: it.n, nnn: it.nnn, slug: it.s, zh: it.zh, en: it.en, theme: it.t, frames: it.d.length, durations_ms: [...it.d], total_ms: it.ms,
    bytes: it.b, file_zh: it.z, gif: abs('gifs/' + it.f), gif_zh: abs(zhUrl(it)), json: abs(`api/gifs/${it.nnn}.json`), ascii: abs(`api/frames/${it.nnn}.txt`),
    sheet: abs(`sheets/${it.nnn}.png`), page: abs(`g/${it.nnn}-${it.s}.html`), viewer: abs(`#/gif/${it.n}`),
    selected: state.selected.has(it.n), visible: matches(it),
  });
  const keysOf = k => (Array.isArray(k) ? k : [k]).map(find).filter(Boolean).map(it => it.n);
  const HELP = `window.clawd — Clawd 400 (${ITEMS.length} pixel GIFs, ${G}x${G} grid scaled ${SCALE}x to 480x480, transparent, CC BY 4.0)
Static data without a browser: llms.txt, api/index.json, api/gifs/{nnn}.json, api/frames/{nnn}.txt, sheets/{nnn}.png
A GIF is referenced by its number (1-${ITEMS.length}) or its slug ("cook_veggies").

Read
  clawd.themes                         -> [{id, zh, en, count}]
  clawd.list({theme, q, selected})     -> [{n, nnn, slug, zh, en, theme, frames, durations_ms, total_ms, gif, json, ascii, sheet, page, ...}]
  clawd.get(n | slug)                  -> one item, as above
  await clawd.frames(n, {format})      -> per frame {i, ms, ...}: format 'ascii' (rows of palette chars + palette), 'rgba' (40x40 RGBA array), 'dataURL' (PNG; {scale} default 1)
  await clawd.json(n)                  -> the full per-GIF JSON (palette names, bbox, changed pixels, source line)
  await clawd.ascii(n)                 -> api/frames/{nnn}.txt as text
UI
  clawd.filter({theme, q})             -> filters the grid; returns the visible items
  clawd.select(keys, mode)             -> mode 'add' (default) | 'remove' | 'toggle' | 'set'; enters selection mode
  clawd.selectAll() / clawd.invert() / clawd.clear() / clawd.selected()
  await clawd.open(n) / clawd.close()  -> the frame viewer
  await clawd.zip(keys?)               -> Blob of a ZIP (defaults to the selection); clawd.download(keys?) saves it`;

  window.clawd = Object.freeze({
    version: '1.0.0', count: ITEMS.length, grid: G, scale: SCALE, license: BOOT.license, credit: BOOT.credit, themes: BOOT.themes.map(t => ({ ...t })),
    help() { return HELP; },
    list(f = {}) {
      const flt = { theme: f.theme || 'all', q: f.q || '' };
      return ITEMS.filter(it => matches(it, flt) && (f.selected == null || state.selected.has(it.n) === !!f.selected)).map(pub);
    },
    get: key => pub(find(key)),
    async frames(key, { format = 'ascii', scale = 1 } = {}) {
      const it = find(key); if (!it) throw new Error('no such GIF: ' + key);
      const im = await sheet(it);
      const all = pixels(im);
      const pal = new Map(), CH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      const out = it.d.map((ms, i) => {
        if (format === 'dataURL') return { i, ms, dataURL: frameCanvas(im, i, scale).toDataURL('image/png') };
        if (format === 'rgba') {
          const data = [];
          for (let y = 0; y < G; y++) for (let x = 0; x < G; x++) { const p = (y * im.width + i * G + x) * 4; data.push(all[p], all[p + 1], all[p + 2], all[p + 3]); }
          return { i, ms, width: G, height: G, data };
        }
        const rows = [];
        for (let y = 0; y < G; y++) {
          let r = '';
          for (let x = 0; x < G; x++) {
            const p = (y * im.width + i * G + x) * 4;
            if (all[p + 3] < 128) { r += '.'; continue; }
            const h = '#' + [all[p], all[p + 1], all[p + 2]].map(v => v.toString(16).padStart(2, '0')).join('');
            if (!pal.has(h)) pal.set(h, CH[pal.size] || '?');
            r += pal.get(h);
          }
          rows.push(r);
        }
        return { i, ms, rows };
      });
      if (format === 'ascii') { const palette = Object.fromEntries([...pal].map(([h, ch]) => [ch, h])); palette['.'] = 'transparent'; out.forEach(f => { f.palette = palette; }); }
      return out;
    },
    json: async key => { const it = find(key); return (await fetch(`api/gifs/${it.nnn}.json`)).json(); },
    ascii: async key => { const it = find(key); return (await fetch(`api/frames/${it.nnn}.txt`)).text(); },
    filter(f = {}) { setFilter({ theme: f.theme ?? state.theme, q: f.q ?? state.q }); return visible().map(pub); },
    select(keys, mode = 'add') {
      const ns = keysOf(keys);
      if (mode === 'set') state.selected.clear();
      ns.forEach(n => mode === 'remove' ? state.selected.delete(n) : mode === 'toggle' ? toggle(n) : state.selected.add(n));
      if (!state.selecting) setSelecting(true); else renderSel();
      return [...state.selected].sort((a, b) => a - b);
    },
    selectAll() { if (!state.selecting) setSelecting(true); $('#selAll').click(); return this.selected(); },
    invert() { if (!state.selecting) setSelecting(true); $('#selInvert').click(); return this.selected(); },
    clear() { $('#selClear').click(); return []; },
    selected: () => [...state.selected].sort((a, b) => a - b),
    open: key => openViewer(key).then(pub),
    close: closeViewer,
    zip: async keys => (await zipBlob(keys ? keysOf(keys) : [...state.selected])).blob,
    download: keys => downloadZip(keys ? keysOf(keys) : [...state.selected]),
  });

  setFilter({});
  route();
  root.dataset.clawdReady = '1';
  dispatchEvent(new CustomEvent('clawd:ready', { detail: { count: ITEMS.length } }));
})();
