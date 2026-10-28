// halftone_runtime.js — the videos' dot screen, live, for an HTML film comp.  window.HT
//
//   const ht = HT.create(document.getElementById('dots'), { theme: 'dark' });   // a 1920x1080 <canvas>
//   // each seek: paint VALUES (grayscale, 0..255 in the red channel) into ht.cells (213x120 + 1),
//   // through the camera scaled by 1/9, then:
//   ht.draw();
//
// Values -> round dots exactly like scripts/halftone.py: area ∝ value, diameter 4.7 sqrt(v) px.
// The grid is fixed to the screen; translate layers by whole cells (9 px) when the camera is at an
// integer zoom so dots stay crisp, like the videos' whole-pixel motion.
(function () {
  const PITCH = 9;
  function create(canvas, { theme = 'dark', ground, ink } = {}) {
    const W = canvas.width, H = canvas.height;
    const cw = Math.ceil(W / PITCH) + 1, ch = Math.ceil(H / PITCH) + 1;
    const cells = document.createElement('canvas'); cells.width = cw; cells.height = ch;
    const cx = cells.getContext('2d', { willReadFrequently: true });
    const g = canvas.getContext('2d');
    const dark = theme === 'dark';
    const G = ground || (dark ? '#131313' : '#f4f2ec');
    const I = ink || (dark ? [221, 217, 215] : [12, 10, 5]);
    const SIDE = new Float32Array(256);
    for (let i = 0; i < 256; i++) { const v = i / 255; SIDE[i] = v < 0.02 ? 0 : 2.35 * Math.sqrt(v); }   // radius: dot area ∝ value, full dot 4.7 px
    function draw(opts = {}) {
      const ground = opts.ground || G, ink = opts.ink || I;
      g.setTransform(1, 0, 0, 1, 0, 0);
      g.fillStyle = ground; g.fillRect(0, 0, W, H);
      const d = cx.getImageData(0, 0, cw, ch).data;
      // group dots by size bucket: one fillStyle, many rects; antialiasing comes from fractional sides
      g.fillStyle = `rgb(${ink[0]},${ink[1]},${ink[2]})`;
      g.beginPath();
      for (let r = 0; r < ch; r++) {
        for (let c = 0; c < cw; c++) {
          const s = SIDE[d[(r * cw + c) * 4]];
          if (s <= 0) continue;
          const x = c * PITCH + 4.5, y = r * PITCH + 4.5, rr = s;
          g.moveTo(x + rr, y); g.arc(x, y, rr, 0, 6.2832);
        }
      }
      g.fill();
    }
    // set the camera transform for painting values: world matrix M (OM.view) scaled to cells
    function viewToCells(M) { cx.setTransform(M[0] / PITCH, M[1] / PITCH, M[2] / PITCH, M[3] / PITCH, M[4] / PITCH, M[5] / PITCH); }
    function clear() { cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = 1; cx.globalCompositeOperation = 'source-over'; cx.fillStyle = '#000'; cx.fillRect(0, 0, cw, ch); }
    return { cells, cx, draw, clear, viewToCells, cw, ch, PITCH };
  }
  window.HT = { create, PITCH };
})();
