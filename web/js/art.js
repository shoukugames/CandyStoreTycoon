/* Candy Store Tycoon — all graphics are drawn in code (no image files) */
const Art = (() => {
  const TAU = Math.PI * 2;
  const FONT = "'Fredoka', 'Trebuchet MS', sans-serif";

  function rr(ctx, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  function circle(ctx, x, y, r) { ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); }
  function shade(hex, amt) {
    const n = parseInt(hex.slice(1), 16);
    let r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    if (amt > 0) { r += (255 - r) * amt; g += (255 - g) * amt; b += (255 - b) * amt; }
    else { r *= 1 + amt; g *= 1 + amt; b *= 1 + amt; }
    return `rgb(${r | 0},${g | 0},${b | 0})`;
  }
  function gloss(ctx, x, y, rx, ry, rot = -0.5, a = 0.55) {
    ctx.save(); ctx.fillStyle = `rgba(255,255,255,${a})`;
    ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, TAU); ctx.fill(); ctx.restore();
  }
  function text(ctx, str, x, y, size, fill, opts = {}) {
    ctx.save();
    ctx.font = `${opts.weight || 700} ${size}px ${FONT}`;
    ctx.textAlign = opts.align || 'center';
    ctx.textBaseline = opts.base || 'middle';
    if (opts.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = opts.lw || size * 0.22; ctx.strokeStyle = opts.stroke; ctx.strokeText(str, x, y); }
    ctx.fillStyle = fill; ctx.fillText(str, x, y);
    ctx.restore();
  }

  // ======================= CANDY =======================
  const LOLLI = [['#ff4f9a', '#ffd6ea'], ['#7a5cff', '#e6deff'], ['#1fc4a3', '#d6fff5'], ['#ff8a1f', '#fff1c4']];
  const GUMMY = ['#ff3b3b', '#ffb000', '#33c94a', '#ff7a1a', '#b84bff'];

  function lolli(ctx, x, y, s, v) {
    const r = s * 0.31, cy = y - s * 0.17;
    const [c1, c2] = LOLLI[v % LOLLI.length];
    rr(ctx, x - s * 0.035, cy, s * 0.07, s * 0.64, s * 0.03);
    ctx.fillStyle = '#fffaf2'; ctx.fill(); ctx.strokeStyle = '#d8c8bb'; ctx.lineWidth = Math.max(1, s * 0.015); ctx.stroke();
    circle(ctx, x, cy, r); ctx.fillStyle = c1; ctx.fill();
    ctx.save(); circle(ctx, x, cy, r); ctx.clip();
    ctx.strokeStyle = c2; ctx.lineWidth = r * 0.3; ctx.lineCap = 'round';
    ctx.beginPath();
    const turns = TAU * 2.4;
    for (let a = 0; a <= turns; a += 0.12) {
      const rad = r * 1.05 * a / turns;
      const px = x + Math.cos(a) * rad, py = cy + Math.sin(a) * rad;
      a === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.stroke();
    const g = ctx.createRadialGradient(x - r * 0.3, cy - r * 0.3, r * 0.1, x, cy, r * 1.1);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(80,0,40,0.28)');
    ctx.fillStyle = g; ctx.fillRect(x - r, cy - r, r * 2, r * 2);
    ctx.restore();
    circle(ctx, x, cy, r); ctx.strokeStyle = shade(c1, -0.3); ctx.lineWidth = Math.max(1, s * 0.025); ctx.stroke();
    gloss(ctx, x - r * 0.38, cy - r * 0.42, r * 0.28, r * 0.15);
  }

  function gummy(ctx, x, y, s, v) {
    const c = GUMMY[v % GUMMY.length], u = s / 100;
    const parts = [[0, -22, 17], [-13, -36, 7.5], [13, -36, 7.5], [-19, 0, 8], [19, 0, 8], [-12, 30, 9.5], [12, 30, 9.5]];
    const path = () => {
      ctx.beginPath();
      for (const [px, py, pr] of parts) { ctx.moveTo(x + px * u + pr * u, y + py * u); ctx.arc(x + px * u, y + py * u, pr * u, 0, TAU); }
      ctx.moveTo(x + 21 * u, y + 10 * u); ctx.ellipse(x, y + 10 * u, 21 * u, 24 * u, 0, 0, TAU);
    };
    path(); ctx.strokeStyle = shade(c, -0.35); ctx.lineWidth = 4.5 * u; ctx.lineJoin = 'round'; ctx.stroke();
    path();
    const g = ctx.createLinearGradient(x - 20 * u, y - 40 * u, x + 20 * u, y + 40 * u);
    g.addColorStop(0, shade(c, 0.35)); g.addColorStop(0.5, c); g.addColorStop(1, shade(c, -0.2));
    ctx.fillStyle = g; ctx.fill();
    ctx.fillStyle = shade(c, 0.45); ctx.beginPath(); ctx.ellipse(x, y - 17 * u, 7 * u, 5 * u, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = shade(c, -0.5);
    circle(ctx, x - 6 * u, y - 25 * u, 2.2 * u); ctx.fill(); circle(ctx, x + 6 * u, y - 25 * u, 2.2 * u); ctx.fill();
    circle(ctx, x, y - 18 * u, 2 * u); ctx.fill();
    ctx.fillStyle = shade(c, 0.25); ctx.beginPath(); ctx.ellipse(x, y + 12 * u, 11 * u, 13 * u, 0, 0, TAU); ctx.fill();
    gloss(ctx, x - 8 * u, y - 30 * u, 5 * u, 3 * u, -0.6, 0.7);
    gloss(ctx, x - 10 * u, y + 2 * u, 3 * u, 8 * u, 0.2, 0.45);
  }

  function choc(ctx, x, y, s, v) {
    const w = s * 0.5, h = s * 0.86, u = s / 100;
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.22);
    rr(ctx, -w / 2, -h / 2, w, h, 5 * u); ctx.fillStyle = '#5a2e17'; ctx.fill();
    const cols = 2, rows = 2, top = -h / 2 + 4 * u, cw = (w - 12 * u) / cols, chh = (h * 0.44 - 6 * u) / rows;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      const bx = -w / 2 + 4 * u + i * (cw + 4 * u), by = top + j * (chh + 3 * u);
      rr(ctx, bx, by, cw, chh, 3 * u); ctx.fillStyle = '#8a4a26'; ctx.fill();
      ctx.fillStyle = 'rgba(255,220,180,0.35)'; ctx.fillRect(bx + 2 * u, by + 1.5 * u, cw - 4 * u, 2.5 * u);
    }
    const wy = -h / 2 + h * 0.42;
    const wc = v % 2 ? ['#2f7bff', '#174bbf'] : ['#e8283c', '#a3101f'];
    ctx.beginPath(); ctx.moveTo(-w / 2, wy + 5 * u);
    const teeth = 6;
    for (let k = 0; k <= teeth; k++) ctx.lineTo(-w / 2 + (w * k) / teeth, wy + (k % 2 ? 0 : 5 * u));
    ctx.lineTo(w / 2, h / 2 - 5 * u); ctx.arcTo(w / 2, h / 2, w / 2 - 5 * u, h / 2, 5 * u);
    ctx.lineTo(-w / 2 + 5 * u, h / 2); ctx.arcTo(-w / 2, h / 2, -w / 2, h / 2 - 5 * u, 5 * u); ctx.closePath();
    ctx.fillStyle = '#e7e9f2'; ctx.fill();
    rr(ctx, -w / 2, wy + 8 * u, w, h / 2 - wy - 8 * u, 5 * u);
    const g = ctx.createLinearGradient(-w / 2, 0, w / 2, 0);
    g.addColorStop(0, wc[1]); g.addColorStop(0.35, wc[0]); g.addColorStop(1, wc[1]);
    ctx.fillStyle = g; ctx.fill();
    rr(ctx, -w / 2 + 5 * u, wy + 18 * u, w - 10 * u, 16 * u, 4 * u); ctx.fillStyle = '#fff6d8'; ctx.fill();
    ctx.fillStyle = wc[0]; ctx.fillRect(-w / 2 + 9 * u, wy + 23 * u, w - 18 * u, 2.5 * u); ctx.fillRect(-w / 2 + 12 * u, wy + 28 * u, w - 24 * u, 2 * u);
    ctx.fillStyle = '#ffd34d'; ctx.fillRect(-w / 2, wy + 40 * u, w, 3 * u);
    rr(ctx, -w / 2, -h / 2, w, h, 5 * u); ctx.strokeStyle = 'rgba(40,10,0,0.55)'; ctx.lineWidth = 2.2 * u; ctx.stroke();
    gloss(ctx, -w / 2 + 6 * u, wy + 30 * u, 2.5 * u, 14 * u, 0, 0.45);
    ctx.restore();
  }

  function ice(ctx, x, y, s, v) {
    const u = s / 100;
    const sets = [['#ff4d6d', '#ffa53d', '#ffe14d'], ['#2fa8ff', '#5fd3ff', '#b4f0ff'], ['#ff70c4', '#ffb3e1', '#fff0fa']];
    const cs = sets[v % sets.length];
    rr(ctx, x - 5 * u, y + 5 * u, 10 * u, 42 * u, 5 * u); ctx.fillStyle = '#e8b979'; ctx.fill(); ctx.strokeStyle = '#b68545'; ctx.lineWidth = 1.6 * u; ctx.stroke();
    const bx = x - 19 * u, by = y - 46 * u, bw = 38 * u, bh = 60 * u;
    ctx.save();
    ctx.beginPath(); ctx.moveTo(bx, by + bh); ctx.lineTo(bx, by + 18 * u); ctx.arc(x, by + 19 * u, 19 * u, Math.PI, 0); ctx.lineTo(bx + bw, by + bh); ctx.closePath();
    ctx.clip();
    for (let k = 0; k < 3; k++) { ctx.fillStyle = cs[k]; ctx.fillRect(bx, by + (bh * k) / 3, bw, bh / 3 + 1); }
    ctx.fillStyle = 'rgba(255,255,255,0.4)'; ctx.fillRect(bx + 5 * u, by + 10 * u, 6 * u, bh - 16 * u);
    ctx.fillStyle = 'rgba(0,0,40,0.12)'; ctx.fillRect(bx + bw - 7 * u, by, 7 * u, bh);
    ctx.restore();
    ctx.beginPath(); ctx.moveTo(bx, by + bh); ctx.lineTo(bx, by + 18 * u); ctx.arc(x, by + 19 * u, 19 * u, Math.PI, 0); ctx.lineTo(bx + bw, by + bh); ctx.closePath();
    ctx.strokeStyle = shade(cs[0], -0.35); ctx.lineWidth = 2.4 * u; ctx.stroke();
    ctx.fillStyle = cs[2]; ctx.beginPath(); ctx.ellipse(x + 9 * u, by + bh + 2 * u, 3 * u, 4.5 * u, 0, 0, TAU); ctx.fill();
  }

  function jaw(ctx, x, y, s, v) {
    const r = s * 0.32;
    const palettes = [['#ff4f9a', '#ffd23f', '#22c9a8', '#7a5cff'], ['#ff7a1a', '#fff', '#2fa8ff', '#ff4f9a']];
    const p = palettes[v % 2];
    ctx.save(); circle(ctx, x, y, r); ctx.clip();
    ctx.fillStyle = p[0]; ctx.fillRect(x - r, y - r, r * 2, r * 2);
    ctx.translate(x, y); ctx.rotate(0.6 + v);
    for (let k = -4; k <= 4; k++) { ctx.fillStyle = p[(k + 8) % 4]; ctx.fillRect(k * r * 0.32 - r * 0.08, -r, r * 0.16, r * 2); }
    ctx.setTransform(ctx.getTransform()); ctx.rotate(-(0.6 + v)); ctx.translate(-x, -y);
    const g = ctx.createRadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r * 1.05);
    g.addColorStop(0, 'rgba(255,255,255,0.25)'); g.addColorStop(0.7, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(60,0,60,0.4)');
    ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
    ctx.restore();
    circle(ctx, x, y, r); ctx.strokeStyle = 'rgba(70,20,60,0.6)'; ctx.lineWidth = Math.max(1, s * 0.025); ctx.stroke();
    gloss(ctx, x - r * 0.35, y - r * 0.4, r * 0.3, r * 0.17, -0.6, 0.75);
  }

  function cotton(ctx, x, y, s, v) {
    const u = s / 100;
    ctx.save();
    ctx.beginPath(); ctx.moveTo(x - 17 * u, y); ctx.lineTo(x + 17 * u, y); ctx.lineTo(x, y + 47 * u); ctx.closePath();
    ctx.fillStyle = '#fffaf0'; ctx.fill(); ctx.save(); ctx.clip();
    ctx.strokeStyle = '#5fb8ff'; ctx.lineWidth = 5 * u;
    for (let k = -3; k < 6; k++) { ctx.beginPath(); ctx.moveTo(x - 30 * u, y + k * 11 * u); ctx.lineTo(x + 30 * u, y + k * 11 * u + 18 * u); ctx.stroke(); }
    ctx.restore();
    ctx.strokeStyle = '#c9b8a0'; ctx.lineWidth = 1.5 * u; ctx.stroke();
    const base = v % 2 ? '#8fd3ff' : '#ff9ad5';
    const blobs = [[-14, -8, 14], [14, -8, 14], [0, -20, 17], [-8, -32, 12], [10, -32, 12], [0, -4, 15], [-18, -22, 10], [18, -22, 10]];
    ctx.fillStyle = shade(base, -0.15);
    for (const [bx, by, br] of blobs) { circle(ctx, x + bx * u, y + by * u + 2 * u, br * u); ctx.fill(); }
    ctx.fillStyle = base;
    for (const [bx, by, br] of blobs) { circle(ctx, x + bx * u, y + by * u, br * u); ctx.fill(); }
    ctx.fillStyle = shade(base, 0.45);
    for (const [bx, by, br] of blobs) { circle(ctx, x + bx * u - br * u * 0.3, y + by * u - br * u * 0.3, br * u * 0.4); ctx.fill(); }
    ctx.restore();
  }

  const CANDY = { lolli, gummy, choc, ice, jaw, cotton };
  function candy(ctx, type, x, y, s, v = 0) { CANDY[type] && CANDY[type](ctx, x, y, s, v); }

  function coin(ctx, x, y, r) {
    circle(ctx, x, y, r); ctx.fillStyle = '#ffc83d'; ctx.fill(); ctx.strokeStyle = '#d99a00'; ctx.lineWidth = r * 0.2; ctx.stroke();
    circle(ctx, x, y, r * 0.62); ctx.strokeStyle = '#fff3b0'; ctx.lineWidth = r * 0.12; ctx.stroke();
    text(ctx, '¥', x, y + r * 0.05, r * 1.0, '#b37400');
  }
  function star(ctx, x, y, r, fill = '#ffd23f', stroke = '#e0a100') {
    ctx.beginPath();
    for (let k = 0; k < 10; k++) {
      const a = -Math.PI / 2 + (k * Math.PI) / 5, rad = k % 2 ? r * 0.48 : r;
      ctx.lineTo(x + Math.cos(a) * rad, y + Math.sin(a) * rad);
    }
    ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.lineJoin = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = r * 0.18; ctx.stroke();
  }
  function heart(ctx, x, y, s, col = '#ff4f7a') {
    ctx.beginPath();
    ctx.moveTo(x, y + s * 0.35);
    ctx.bezierCurveTo(x - s * 0.9, y - s * 0.25, x - s * 0.35, y - s * 0.85, x, y - s * 0.3);
    ctx.bezierCurveTo(x + s * 0.35, y - s * 0.85, x + s * 0.9, y - s * 0.25, x, y + s * 0.35);
    ctx.fillStyle = col; ctx.fill();
  }
  function cloud(ctx, x, y, s, col = '#fff') {
    ctx.fillStyle = col;
    ctx.beginPath();
    ctx.arc(x, y, s * 0.5, 0, TAU); ctx.arc(x + s * 0.5, y - s * 0.2, s * 0.6, 0, TAU);
    ctx.arc(x + s * 1.1, y, s * 0.45, 0, TAU); ctx.rect(x, y - s * 0.1, s * 1.1, s * 0.55);
    ctx.fill();
  }

  // ======================= KIDS =======================
  const SKIN = ['#ffdcc2', '#f6c8a0', '#e0a77a', '#c68654', '#8d5a36', '#6b4226'];
  const HAIR = ['#2b1a12', '#5b3416', '#a0582a', '#e8b84a', '#d9472b', '#1a1a2e', '#7a4bd9', '#ff6fae'];
  const SHIRT = ['#ff5fa2', '#7a5cff', '#22c9a8', '#ffb000', '#2fa8ff', '#ff6b3d', '#9be15d', '#ff8fd1'];
  const PANTS = ['#3c5aa6', '#4a3a6b', '#2f2f3f', '#6b8bd6', '#a05a2c', '#3f8f7a'];
  const pick = a => a[(Math.random() * a.length) | 0];

  function randomLook() {
    return {
      skin: pick(SKIN), hair: pick(HAIR), shirt: pick(SHIRT), pants: pick(PANTS),
      shoe: pick(['#ffffff', '#ff5fa2', '#333344', '#ffcf3a', '#2fa8ff']),
      style: (Math.random() * 6) | 0, stripe: Math.random() < 0.4, cap: pick(SHIRT),
      size: 0.88 + Math.random() * 0.2, blink: Math.random() * 4,
    };
  }

  function kid(ctx, L, x, y, o = {}) {
    const t = o.t || 0, walking = !!o.walking, mood = o.mood || 'happy';
    const ph = o.phase || 0;
    const swing = walking ? Math.sin(ph) * 0.55 : 0;
    const bob = walking ? -Math.abs(Math.sin(ph)) * 4 : Math.sin(t * 2 + L.blink) * 1.2;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(L.size * (o.flip ? -1 : 1), L.size);
    // shadow
    ctx.fillStyle = 'rgba(90,36,72,0.18)'; ctx.beginPath(); ctx.ellipse(0, 2, 26, 7, 0, 0, TAU); ctx.fill();
    // legs
    const leg = (hx, a) => {
      ctx.save(); ctx.translate(hx, -40 + bob); ctx.rotate(a);
      rr(ctx, -5.5, 0, 11, 34, 5); ctx.fillStyle = L.pants; ctx.fill();
      ctx.fillStyle = L.shoe; ctx.beginPath(); ctx.ellipse(3, 36, 9, 5.5, 0, 0, TAU); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.25)'; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.restore();
    };
    leg(-7, swing); leg(7, -swing);
    // back arm
    const arm = (sx, a, front) => {
      ctx.save(); ctx.translate(sx, -72 + bob); ctx.rotate(a);
      rr(ctx, -5, -2, 10, 24, 5); ctx.fillStyle = front ? L.shirt : shade(L.shirt, -0.15); ctx.fill();
      circle(ctx, 0, 25, 5.5); ctx.fillStyle = L.skin; ctx.fill();
      ctx.restore();
    };
    const armA = walking ? -swing * 0.9 : (o.holding ? -0.9 : 0.12);
    arm(-16, walking ? swing * 0.9 : -0.12, false);
    // body
    rr(ctx, -17, -80 + bob, 34, 44, 13);
    ctx.fillStyle = L.shirt; ctx.fill();
    if (L.stripe) {
      ctx.save(); rr(ctx, -17, -80 + bob, 34, 44, 13); ctx.clip();
      ctx.fillStyle = 'rgba(255,255,255,0.55)'; ctx.fillRect(-17, -64 + bob, 34, 5); ctx.fillRect(-17, -54 + bob, 34, 5);
      ctx.restore();
    }
    ctx.fillStyle = 'rgba(255,255,255,0.2)'; rr(ctx, -13, -77 + bob, 8, 30, 4); ctx.fill();
    // back hair (long styles)
    const hy = -102 + bob;
    ctx.fillStyle = L.hair;
    if (L.style === 1) { circle(ctx, -27, hy + 2, 10); ctx.fill(); circle(ctx, 27, hy + 2, 10); ctx.fill(); }
    if (L.style === 3) { rr(ctx, -28, hy - 20, 56, 50, 22); ctx.fill(); }
    if (L.style === 5) { for (let k = 0; k < 9; k++) { const a = Math.PI + (k / 8) * Math.PI; circle(ctx, Math.cos(a) * 24, hy + Math.sin(a) * 22 + 2, 11); ctx.fill(); } }
    // head
    circle(ctx, 0, hy, 25); ctx.fillStyle = L.skin; ctx.fill();
    circle(ctx, -25, hy + 2, 5); ctx.fill(); circle(ctx, 25, hy + 2, 5); ctx.fill();
    // front hair
    ctx.fillStyle = L.hair;
    if (L.style === 0 || L.style === 4) {
      ctx.beginPath(); ctx.arc(0, hy, 26.5, Math.PI * 1.02, Math.PI * 1.98); ctx.quadraticCurveTo(10, hy - 12, 0, hy - 14); ctx.quadraticCurveTo(-12, hy - 8, -26, hy - 3); ctx.fill();
    } else if (L.style === 1 || L.style === 3) {
      ctx.beginPath(); ctx.arc(0, hy, 27, Math.PI * 1.0, Math.PI * 2.0);
      for (let k = 0; k <= 5; k++) ctx.lineTo(26 - k * 10.4, hy - 6 + (k % 2 ? -6 : 2));
      ctx.fill();
    } else if (L.style === 2) {
      ctx.beginPath(); ctx.moveTo(-26, hy - 2);
      for (let k = 0; k < 6; k++) { ctx.lineTo(-24 + k * 9.6, hy - 34 - (k % 2) * 4); ctx.lineTo(-20 + k * 9.6 + 4, hy - 14); }
      ctx.lineTo(26, hy - 2); ctx.arc(0, hy, 26, 0, Math.PI, true); ctx.closePath();
      ctx.save(); ctx.clip(); ctx.restore();
      ctx.beginPath(); ctx.moveTo(-26, hy - 4);
      for (let k = 0; k < 6; k++) { ctx.lineTo(-23 + k * 9.6, hy - 33 - (k % 2) * 5); ctx.lineTo(-18 + k * 9.6, hy - 16); }
      ctx.lineTo(26, hy - 4); ctx.quadraticCurveTo(0, hy - 10, -26, hy - 4); ctx.fill();
    } else if (L.style === 5) {
      for (let k = 0; k < 7; k++) { circle(ctx, -20 + k * 6.7, hy - 20 + Math.sin(k * 1.7) * 2, 8); ctx.fill(); }
    }
    if (L.style === 4) {
      ctx.fillStyle = L.cap;
      ctx.beginPath(); ctx.arc(0, hy - 4, 27, Math.PI, 0); ctx.closePath(); ctx.fill();
      rr(ctx, 4, hy - 9, 34, 7, 4); ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.35)'; circle(ctx, -8, hy - 20, 4); ctx.fill();
    }
    // face
    const blinking = ((t + L.blink) % 4) < 0.12;
    ctx.fillStyle = '#2b1a2b';
    if (blinking) { ctx.fillRect(-11, hy + 1, 7, 2); ctx.fillRect(4, hy + 1, 7, 2); }
    else {
      ctx.beginPath(); ctx.ellipse(-8, hy + 1, 3.4, 4.4, 0, 0, TAU); ctx.fill();
      ctx.beginPath(); ctx.ellipse(8, hy + 1, 3.4, 4.4, 0, 0, TAU); ctx.fill();
      ctx.fillStyle = '#fff'; circle(ctx, -7, hy - 0.5, 1.3); ctx.fill(); circle(ctx, 9, hy - 0.5, 1.3); ctx.fill();
    }
    ctx.fillStyle = 'rgba(255,90,120,0.35)'; circle(ctx, -15, hy + 9, 4.5); ctx.fill(); circle(ctx, 15, hy + 9, 4.5); ctx.fill();
    ctx.strokeStyle = '#7a2b3b'; ctx.lineWidth = 2.4; ctx.lineCap = 'round';
    ctx.beginPath();
    if (mood === 'happy') { ctx.arc(0, hy + 9, 7, 0.15 * Math.PI, 0.85 * Math.PI); }
    else if (mood === 'excited') { ctx.fillStyle = '#7a2b3b'; ctx.arc(0, hy + 10, 6.5, 0, Math.PI); ctx.closePath(); ctx.fill(); }
    else if (mood === 'wait') { ctx.moveTo(-5, hy + 13); ctx.lineTo(5, hy + 13); }
    else if (mood === 'worried') { ctx.moveTo(-5, hy + 14); ctx.quadraticCurveTo(0, hy + 10, 5, hy + 14); }
    else if (mood === 'sad') { ctx.arc(0, hy + 18, 7, 1.2 * Math.PI, 1.8 * Math.PI); }
    ctx.stroke();
    if (mood === 'sad' || mood === 'worried') {
      ctx.beginPath(); ctx.moveTo(-12, hy - 9); ctx.lineTo(-4, hy - 6); ctx.moveTo(12, hy - 9); ctx.lineTo(4, hy - 6); ctx.stroke();
    }
    if (mood === 'sad') { ctx.fillStyle = '#5fc8ff'; ctx.beginPath(); ctx.ellipse(-10, hy + 9 + ((t * 30) % 10), 2.5, 4, 0, 0, TAU); ctx.fill(); }
    // front arm (holding candy?)
    arm(16, armA, true);
    if (o.holding) {
      ctx.save(); ctx.translate(16, -72 + bob); ctx.rotate(armA);
      candy(ctx, o.holding, 0, 34, 30, o.holdV || 0);
      ctx.restore();
    }
    ctx.restore();
  }

  function bubble(ctx, x, y, type, frac, qty, alt, t) {
    const wob = Math.sin(t * 4) * 1.5;
    y += wob;
    ctx.save();
    ctx.shadowColor = 'rgba(90,36,72,0.25)'; ctx.shadowBlur = 8; ctx.shadowOffsetY = 3;
    ctx.fillStyle = '#fff';
    circle(ctx, x - 22, y + 36, 4); ctx.fill();
    circle(ctx, x - 14, y + 28, 6); ctx.fill();
    circle(ctx, x, y, 28); ctx.fill();
    ctx.restore();
    if (frac !== null) {
      ctx.lineWidth = 5; ctx.lineCap = 'round';
      ctx.strokeStyle = '#f1e2ea'; circle(ctx, x, y, 28); ctx.stroke();
      const hue = Math.max(0, Math.min(120, frac * 130));
      ctx.strokeStyle = `hsl(${hue},85%,50%)`;
      ctx.beginPath(); ctx.arc(x, y, 28, -Math.PI / 2, -Math.PI / 2 + TAU * frac); ctx.stroke();
    }
    candy(ctx, type, x, y + 2, 38, 0);
    if (qty > 1) {
      circle(ctx, x + 22, y - 20, 11); ctx.fillStyle = '#ff5fa2'; ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.stroke();
      text(ctx, 'x' + qty, x + 22, y - 19.5, 12, '#fff');
    }
    if (alt) {
      circle(ctx, x + 30, y + 16, 13); ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = '#e8d2de'; ctx.lineWidth = 2; ctx.stroke();
      candy(ctx, alt, x + 30, y + 17, 18, 0);
    }
  }

  // ======================= SHOP SCENE =======================
  function awning(ctx, y, t, W) {
    const n = 20, w = W / n;
    for (let i = 0; i < n; i++) {
      ctx.fillStyle = i % 2 ? '#fff' : '#ff5fa2';
      ctx.fillRect(i * w, 0, w + 1, y);
      ctx.beginPath(); ctx.arc(i * w + w / 2, y, w / 2, 0, Math.PI); ctx.fill();
    }
    ctx.fillStyle = 'rgba(0,0,0,0.08)'; ctx.fillRect(0, y - 8, W, 8);
  }

  function shopBackground(ctx, t, W, H, opts = {}) {
    const floorY = 470;
    // wall
    let g = ctx.createLinearGradient(0, 0, 0, floorY);
    g.addColorStop(0, '#ffd3e7'); g.addColorStop(1, '#ffe8f2');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, floorY);
    ctx.fillStyle = 'rgba(255,255,255,0.45)';
    for (let x = 0; x < W; x += 56) ctx.fillRect(x, 0, 24, floorY);
    // little polka dots on stripes
    ctx.fillStyle = 'rgba(255,95,162,0.12)';
    for (let x = 12; x < W; x += 56) for (let y = 130; y < floorY; y += 34) { circle(ctx, x, y + ((x / 56) % 2) * 17, 4); ctx.fill(); }
    // wainscot
    g = ctx.createLinearGradient(0, 390, 0, floorY);
    g.addColorStop(0, '#a7f0dc'); g.addColorStop(1, '#7fdcc4');
    ctx.fillStyle = g; ctx.fillRect(0, 390, W, floorY - 390);
    ctx.fillStyle = '#5fc9ad'; ctx.fillRect(0, 386, W, 8);
    ctx.fillStyle = 'rgba(255,255,255,0.35)';
    for (let x = 20; x < W; x += 80) { rr(ctx, x, 404, 56, 52, 8); ctx.fill(); }
    // floor
    g = ctx.createLinearGradient(0, floorY, 0, H);
    g.addColorStop(0, '#ffc2dc'); g.addColorStop(1, '#ffe1ee');
    ctx.fillStyle = g; ctx.fillRect(0, floorY, W, H - floorY);
    let rowY = floorY, rh = 26, row = 0;
    while (rowY < H) {
      const tw = 60 + row * 6;
      const off = (row % 2) * tw;
      for (let x = -tw * 2 + off; x < W + tw; x += tw * 2) {
        ctx.fillStyle = 'rgba(255,255,255,0.55)';
        ctx.fillRect(x, rowY, tw, rh);
      }
      rowY += rh; rh += 5; row++;
    }
    g = ctx.createLinearGradient(0, floorY, 0, floorY + 40);
    g.addColorStop(0, 'rgba(120,40,90,0.2)'); g.addColorStop(1, 'rgba(120,40,90,0)');
    ctx.fillStyle = g; ctx.fillRect(0, floorY, W, 40);
    ctx.fillStyle = '#e88fb8'; ctx.fillRect(0, floorY - 3, W, 6);

    // round windows
    for (const wx of [250, 1030]) {
      ctx.save();
      circle(ctx, wx, 165, 44); ctx.clip();
      g = ctx.createLinearGradient(0, 120, 0, 210); g.addColorStop(0, '#7fd2ff'); g.addColorStop(1, '#cdf1ff');
      ctx.fillStyle = g; ctx.fillRect(wx - 50, 115, 100, 100);
      cloud(ctx, wx - 60 + ((t * 8 + wx) % 140), 160, 20, 'rgba(255,255,255,0.95)');
      ctx.fillStyle = '#9be15d'; ctx.beginPath(); ctx.ellipse(wx, 215, 70, 22, 0, 0, TAU); ctx.fill();
      ctx.restore();
      circle(ctx, wx, 165, 44); ctx.lineWidth = 9; ctx.strokeStyle = '#fff'; ctx.stroke();
      ctx.lineWidth = 3; ctx.strokeStyle = '#ff9cc8'; circle(ctx, wx, 165, 49); ctx.stroke();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(wx - 44, 165); ctx.lineTo(wx + 44, 165); ctx.moveTo(wx, 121); ctx.lineTo(wx, 209); ctx.stroke();
    }

    // bunting
    const flags = ['#ff5fa2', '#ffcf3a', '#22c9a8', '#7a5cff', '#2fa8ff'];
    ctx.strokeStyle = '#d97aa8'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(0, 116); ctx.quadraticCurveTo(W / 4, 140, W / 2, 116); ctx.quadraticCurveTo((3 * W) / 4, 140, W, 116); ctx.stroke();
    for (let i = 0; i < 26; i++) {
      const fx = 20 + i * 48, seg = fx < W / 2 ? fx / (W / 2) : (fx - W / 2) / (W / 2);
      const fy = 116 + Math.sin(seg * Math.PI) * 12;
      const sw = Math.sin(t * 2 + i) * 0.08;
      ctx.save(); ctx.translate(fx, fy); ctx.rotate(sw);
      ctx.fillStyle = flags[i % flags.length];
      ctx.beginPath(); ctx.moveTo(-11, 0); ctx.lineTo(11, 0); ctx.lineTo(0, 22); ctx.closePath(); ctx.fill();
      ctx.restore();
    }

    // shop name sign
    const name = opts.shopName || 'Sweet Treats';
    ctx.save();
    ctx.font = `700 34px ${FONT}`;
    const tw = Math.max(260, ctx.measureText(name).width + 70);
    ctx.restore();
    const sx = W / 2 - tw / 2, sy = 140;
    ctx.strokeStyle = '#b07a52'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(sx + 30, sy); ctx.lineTo(sx + 50, 118); ctx.moveTo(sx + tw - 30, sy); ctx.lineTo(sx + tw - 50, 118); ctx.stroke();
    ctx.save(); ctx.shadowColor = 'rgba(90,36,72,0.3)'; ctx.shadowBlur = 10; ctx.shadowOffsetY = 5;
    rr(ctx, sx, sy, tw, 62, 20);
    g = ctx.createLinearGradient(0, sy, 0, sy + 62); g.addColorStop(0, '#8f75ff'); g.addColorStop(1, '#6342f0');
    ctx.fillStyle = g; ctx.fill(); ctx.restore();
    rr(ctx, sx + 5, sy + 5, tw - 10, 52, 16); ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.setLineDash([6, 6]); ctx.lineWidth = 2.5; ctx.stroke(); ctx.setLineDash([]);
    text(ctx, name, W / 2, sy + 32, 32, '#fff', { stroke: '#4526c2', lw: 6 });
    // blinking marquee lights
    for (let k = 0; k < 12; k++) {
      const lx = sx + 14 + (k * (tw - 28)) / 11;
      const on = (Math.floor(t * 3) + k) % 2 === 0;
      circle(ctx, lx, sy - 1, 4); ctx.fillStyle = on ? '#ffe96b' : '#d8c4ff'; ctx.fill();
      circle(ctx, lx, sy + 63, 4); ctx.fill();
    }

    // door
    const dx = 22, dy = 230, dw = 96, dh = floorY - dy;
    const open = Math.min(1, opts.doorOpen || 0);
    rr(ctx, dx - 8, dy - 8, dw + 16, dh + 8, 10); ctx.fillStyle = '#fff'; ctx.fill();
    ctx.fillStyle = '#5a3a8a'; ctx.fillRect(dx, dy, dw, dh);
    ctx.fillStyle = '#ffe9a8'; ctx.fillRect(dx + 4, dy + 4, dw - 8, dh - 4);
    ctx.save(); ctx.translate(dx, dy);
    const dwOpen = dw * (1 - open * 0.75);
    g = ctx.createLinearGradient(0, 0, dwOpen, 0); g.addColorStop(0, '#ff7ab5'); g.addColorStop(1, '#e8508f');
    rr(ctx, 0, 0, dwOpen, dh, 6); ctx.fillStyle = g; ctx.fill();
    rr(ctx, dwOpen * 0.15, 14, dwOpen * 0.7, 80, 30); ctx.fillStyle = '#bfefff'; ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fillRect(dwOpen * 0.25, 26, dwOpen * 0.08, 50);
    circle(ctx, dwOpen * 0.82, dh * 0.55, 5); ctx.fillStyle = '#ffd23f'; ctx.fill();
    ctx.restore();
    // OPEN / CLOSED sign
    const isOpen = !!opts.storeOpen;
    ctx.save(); ctx.translate(dx + dw / 2, dy - 30); ctx.rotate(Math.sin(t * 1.5) * 0.04);
    rr(ctx, -44, -16, 88, 30, 9); ctx.fillStyle = isOpen ? '#22c9a8' : '#ff5b5b'; ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
    text(ctx, isOpen ? 'OPEN' : 'CLOSED', 0, 0, 17, '#fff');
    ctx.restore();

    // big wall candy decorations
    ctx.save(); ctx.globalAlpha = 0.9;
    candy(ctx, 'lolli', 150, 300, 70, 1);
    ctx.restore();
  }

  function counter(ctx, t, W) {
    const x = 1150, y = 420;
    // counter
    ctx.save(); ctx.shadowColor = 'rgba(90,36,72,0.25)'; ctx.shadowBlur = 12; ctx.shadowOffsetY = 6;
    rr(ctx, x, y, 135, 150, 12); ctx.fillStyle = '#ff7ab5'; ctx.fill(); ctx.restore();
    ctx.fillStyle = 'rgba(255,255,255,0.55)';
    for (let k = 0; k < 4; k++) ctx.fillRect(x + 12 + k * 32, y + 26, 16, 118);
    rr(ctx, x - 8, y - 6, 151, 22, 9); ctx.fillStyle = '#fff3f8'; ctx.fill(); ctx.strokeStyle = '#ffb3d4'; ctx.lineWidth = 3; ctx.stroke();
    // register
    const rx = x + 22, ry = y - 66;
    rr(ctx, rx, ry + 20, 92, 42, 8); ctx.fillStyle = '#7a5cff'; ctx.fill();
    rr(ctx, rx + 10, ry, 72, 28, 6); ctx.fillStyle = '#5636d6'; ctx.fill();
    rr(ctx, rx + 16, ry + 5, 60, 16, 4); ctx.fillStyle = '#b8ffe9'; ctx.fill();
    text(ctx, '¥ ¥ ¥', rx + 46, ry + 13.5, 11, '#0e8a6f');
    for (let i = 0; i < 4; i++) for (let j = 0; j < 2; j++) { rr(ctx, rx + 10 + i * 19, ry + 30 + j * 13, 14, 9, 3); ctx.fillStyle = '#fff'; ctx.fill(); }
    // candy jar
    ctx.save(); ctx.globalAlpha = 0.85;
    rr(ctx, x + 2, y - 52, 26, 40, 8); ctx.fillStyle = 'rgba(220,245,255,0.8)'; ctx.fill(); ctx.restore();
    for (let k = 0; k < 6; k++) { circle(ctx, x + 8 + (k % 3) * 7, y - 22 - Math.floor(k / 3) * 8, 4); ctx.fillStyle = ['#ff5fa2', '#ffcf3a', '#22c9a8'][k % 3]; ctx.fill(); }
    rr(ctx, x, y - 56, 30, 7, 3); ctx.fillStyle = '#ff5fa2'; ctx.fill();
  }

  function shelfLayout(n) {
    const left = 150, right = 1130, gap = 18;
    const w = Math.min(196, (right - left - gap * (n - 1)) / n);
    const total = w * n + gap * (n - 1);
    const start = left + (right - left - total) / 2;
    const arr = [];
    for (let i = 0; i < n; i++) arr.push({ x: start + i * (w + gap), y: 222, w, h: 248 });
    return arr;
  }

  function shelf(ctx, r, s, cap, info) {
    const { x, y, w, h } = r;
    const tiers = cap <= 10 ? 2 : 3;
    const perRow = Math.ceil(cap / tiers);
    // cabinet
    ctx.save(); ctx.shadowColor = 'rgba(90,36,72,0.3)'; ctx.shadowBlur = 14; ctx.shadowOffsetY = 6;
    rr(ctx, x, y + 34, w, h - 34, 12);
    const g = ctx.createLinearGradient(x, 0, x + w, 0); g.addColorStop(0, '#c98a55'); g.addColorStop(0.5, '#e0a66d'); g.addColorStop(1, '#b97a46');
    ctx.fillStyle = g; ctx.fill(); ctx.restore();
    rr(ctx, x + 9, y + 44, w - 18, h - 62, 8); ctx.fillStyle = '#fff1f7'; ctx.fill();
    ctx.fillStyle = 'rgba(255,95,162,0.08)';
    for (let k = 0; k < 6; k++) ctx.fillRect(x + 9 + k * (w - 18) / 6, y + 44, (w - 18) / 12, h - 62);
    // sign / label
    const p = info.product;
    rr(ctx, x + 6, y, w - 12, 38, 12);
    ctx.fillStyle = info.hover ? '#fff' : '#fffaf2'; ctx.fill();
    ctx.lineWidth = 3.5; ctx.strokeStyle = p ? p.color : '#ddd'; ctx.stroke();
    if (p) {
      text(ctx, p.name, x + w / 2 - 22, y + 19, w < 160 ? 14 : 16, '#5a2448', { weight: 700 });
      rr(ctx, x + w - 56, y + 8, 44, 22, 11); ctx.fillStyle = info.priceUp ? '#22c9a8' : '#ffcf3a'; ctx.fill();
      text(ctx, '¥' + info.price, x + w - 34, y + 19.5, 13, info.priceUp ? '#fff' : '#6b4300');
    } else text(ctx, 'Empty shelf', x + w / 2, y + 19, 15, '#a07a90');
    // tiers & candy
    const innerTop = y + 44, innerH = h - 62, tierH = innerH / tiers;
    let idx = 0;
    const size = Math.min(54, tierH * 0.78, ((w - 30) / perRow) * 1.7);
    for (let tr = 0; tr < tiers; tr++) {
      const baseY = innerTop + tierH * (tr + 1);
      for (let c = 0; c < perRow; c++) {
        if (idx < s.count && s.type) {
          const cx = x + 20 + ((w - 40) * (c + 0.5)) / perRow;
          const bounce = info.bounceIdx === idx ? Math.sin(info.t * 20) * 2 : 0;
          candy(ctx, s.type, cx, baseY - size * 0.48 + bounce, size, (idx * 7 + tr) % 5);
        }
        idx++;
      }
      rr(ctx, x + 5, baseY - 4, w - 10, 10, 4); ctx.fillStyle = '#a8693a'; ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(x + 8, baseY - 3, w - 16, 2.5);
    }
    // count pill
    const full = s.count >= cap, empty = s.count === 0;
    rr(ctx, x + w / 2 - 30, y + h - 14, 60, 24, 12);
    ctx.fillStyle = empty ? '#ff5b5b' : full ? '#22c9a8' : '#fff'; ctx.fill();
    ctx.strokeStyle = empty ? '#c73232' : full ? '#109479' : '#ffb3d4'; ctx.lineWidth = 2.5; ctx.stroke();
    text(ctx, `${s.count}/${cap}`, x + w / 2, y + h - 1.5, 14, empty || full ? '#fff' : '#5a2448');
    // empty warning flash
    if (empty && info.rush) {
      const a = 0.35 + Math.sin(info.t * 6) * 0.25;
      rr(ctx, x + 9, y + 44, w - 18, h - 62, 8); ctx.fillStyle = `rgba(255,91,91,${a * 0.3})`; ctx.fill();
      text(ctx, 'EMPTY!', x + w / 2, y + 44 + (h - 62) / 2, 22, '#ff5b5b', { stroke: '#fff', lw: 5 });
    }
    // restocking progress
    if (s.restock) {
      const f = 1 - s.restock.t / s.restock.total;
      rr(ctx, x + 9, y + 44, w - 18, h - 62, 8); ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fill();
      candy(ctx, s.restock.type, x + w / 2, y + 112 + Math.sin(info.t * 10) * 4, 56, 0);
      text(ctx, 'Restocking...', x + w / 2, y + 168, 15, '#5a2448');
      rr(ctx, x + 22, y + 182, w - 44, 14, 7); ctx.fillStyle = '#f3dce8'; ctx.fill();
      rr(ctx, x + 22, y + 182, (w - 44) * f, 14, 7); ctx.fillStyle = '#ff5fa2'; ctx.fill();
    }
    if (info.hover) {
      rr(ctx, x - 4, y - 4, w + 8, h + 8, 16); ctx.strokeStyle = 'rgba(255,207,58,0.95)'; ctx.lineWidth = 5; ctx.stroke();
      if (info.hint) text(ctx, info.hint, x + w / 2, y - 18, 15, '#5a2448', { stroke: '#fff', lw: 5 });
    }
  }

  // ======================= EVENT ART =======================
  function sun(ctx, x, y, r, t, shades) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 0.4);
    ctx.fillStyle = '#ffd23f';
    for (let k = 0; k < 12; k++) { ctx.rotate(TAU / 12); ctx.beginPath(); ctx.moveTo(-8, -r - 4); ctx.lineTo(0, -r - 26 - Math.sin(t * 4 + k) * 5); ctx.lineTo(8, -r - 4); ctx.fill(); }
    ctx.restore();
    circle(ctx, x, y, r); ctx.fillStyle = '#ffcf3a'; ctx.fill(); ctx.strokeStyle = '#ff9f1a'; ctx.lineWidth = 5; ctx.stroke();
    if (shades) {
      ctx.fillStyle = '#2b1a2b'; rr(ctx, x - r * 0.62, y - r * 0.22, r * 0.5, r * 0.32, 8); ctx.fill(); rr(ctx, x + r * 0.12, y - r * 0.22, r * 0.5, r * 0.32, 8); ctx.fill();
      ctx.fillRect(x - r * 0.15, y - r * 0.15, r * 0.3, 4);
    } else {
      ctx.fillStyle = '#7a3b00'; circle(ctx, x - r * 0.3, y - r * 0.1, 5); ctx.fill(); circle(ctx, x + r * 0.3, y - r * 0.1, 5); ctx.fill();
    }
    ctx.strokeStyle = '#7a3b00'; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(x, y + r * 0.1, r * 0.35, 0.2 * Math.PI, 0.8 * Math.PI); ctx.stroke();
    ctx.fillStyle = 'rgba(255,90,90,0.35)'; circle(ctx, x - r * 0.55, y + r * 0.25, 8); ctx.fill(); circle(ctx, x + r * 0.55, y + r * 0.25, 8); ctx.fill();
  }
  function confetti(ctx, W, H, t, n = 40) {
    const cols = ['#ff5fa2', '#ffcf3a', '#22c9a8', '#7a5cff', '#2fa8ff', '#fff'];
    for (let i = 0; i < n; i++) {
      const x = (i * 97.3 + Math.sin(t + i) * 20) % W, y = ((i * 53.7) + t * (40 + (i % 5) * 12)) % (H + 20) - 10;
      ctx.save(); ctx.translate(x, y); ctx.rotate(t * 3 + i); ctx.fillStyle = cols[i % cols.length]; ctx.fillRect(-4, -2, 8, 4); ctx.restore();
    }
  }
  const EVENT_BG = {
    opening: ['#ffd1ec', '#b8f2e6'], normal: ['#ffe3f0', '#d9ccff'], heatwave: ['#ffcf6b', '#ff7a45'],
    recess: ['#a9dcff', '#5fa8ff'], sale: ['#fff27a', '#ffb3d9'], rain: ['#b5c6e0', '#6b85b3'],
    party: ['#ffc2e2', '#c89bff'], festival: ['#ffd36e', '#ff7eb3'], cocoa: ['#f0d6bb', '#a8774f'],
    sunny: ['#c7f3ff', '#ffe58a'], spooky: ['#c9a3ff', '#5a3a8a'],
  };
  const LOOKS = Array.from({ length: 6 }, randomLook);

  function eventArt(ctx, id, W, H, t) {
    const bg = EVENT_BG[id] || EVENT_BG.normal;
    const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, bg[0]); g.addColorStop(1, bg[1]);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // rotating rays
    ctx.save(); ctx.translate(W / 2, H * 0.55); ctx.rotate(t * 0.15); ctx.fillStyle = 'rgba(255,255,255,0.18)';
    for (let k = 0; k < 12; k++) { ctx.rotate(TAU / 12); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-60, -700); ctx.lineTo(60, -700); ctx.fill(); }
    ctx.restore();
    const ground = (col) => { ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(W / 2, H + 40, W * 0.7, 90, 0, 0, TAU); ctx.fill(); };

    if (id === 'heatwave') {
      sun(ctx, 110, 80, 46, t, true);
      ground('#ffb066');
      // melting chocolate
      ctx.save(); ctx.translate(W / 2 + 10, H * 0.55);
      choc(ctx, 0, 0, 130, 0);
      ctx.fillStyle = '#5a2e17';
      for (let k = 0; k < 4; k++) { const len = 20 + ((t * 25 + k * 13) % 40); rr(ctx, -30 + k * 18, 40, 10, len, 5); ctx.fill(); circle(ctx, -25 + k * 18, 40 + len, 7); ctx.fill(); }
      ctx.restore();
      ctx.fillStyle = '#5a2e17'; ctx.beginPath(); ctx.ellipse(W / 2 + 10, H - 24, 70, 14, 0, 0, TAU); ctx.fill();
      for (let k = 0; k < 3; k++) { ice(ctx, W - 150 + k * 50, H * 0.55 + Math.sin(t * 3 + k) * 6, 90, k); }
      // heat squiggles
      ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
      for (let k = 0; k < 3; k++) { ctx.beginPath(); for (let yy = 0; yy < 60; yy += 4) ctx.lineTo(220 + k * 30 + Math.sin(yy / 8 + t * 5) * 5, 170 - yy); ctx.stroke(); }
    } else if (id === 'recess') {
      ground('#7ed957');
      // school
      const sx = W / 2 - 90, sy = 40;
      ctx.fillStyle = '#e8574b'; ctx.fillRect(sx, sy + 40, 180, 120);
      ctx.fillStyle = '#c23e33'; ctx.beginPath(); ctx.moveTo(sx - 15, sy + 44); ctx.lineTo(sx + 90, sy - 10); ctx.lineTo(sx + 195, sy + 44); ctx.fill();
      circle(ctx, sx + 90, sy + 22, 16); ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = '#333'; ctx.lineWidth = 3; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(sx + 90, sy + 22); ctx.lineTo(sx + 90 + Math.cos(t * 3) * 10, sy + 22 + Math.sin(t * 3) * 10); ctx.moveTo(sx + 90, sy + 22); ctx.lineTo(sx + 90, sy + 12); ctx.stroke();
      ctx.fillStyle = '#bfefff'; for (let k = 0; k < 3; k++) { ctx.fillRect(sx + 18 + k * 56, sy + 62, 32, 28); }
      ctx.fillStyle = '#7a4b2a'; ctx.fillRect(sx + 72, sy + 110, 36, 50);
      // bell
      ctx.save(); ctx.translate(sx + 90, sy - 24); ctx.rotate(Math.sin(t * 12) * 0.4); ctx.fillStyle = '#ffcf3a';
      ctx.beginPath(); ctx.moveTo(-12, 10); ctx.quadraticCurveTo(-12, -12, 0, -12); ctx.quadraticCurveTo(12, -12, 12, 10); ctx.closePath(); ctx.fill(); ctx.restore();
      // running kids
      for (let k = 0; k < 5; k++) {
        const x = ((t * 120 + k * 130) % (W + 120)) - 60;
        kid(ctx, LOOKS[k], x, H - 14 - (k % 2) * 10, { walking: true, phase: t * 14 + k, t, mood: 'excited' });
      }
    } else if (id === 'sale') {
      ground('#ffd0e4');
      for (let k = 0; k < 6; k++) lolli(ctx, 70 + k * 90 + (k > 2 ? 60 : 0), H * 0.62 + Math.sin(t * 3 + k) * 8, 90, k);
      ctx.save(); ctx.translate(W / 2, H * 0.4); ctx.rotate(-0.12 + Math.sin(t * 2) * 0.05);
      rr(ctx, -110, -48, 220, 96, 18); ctx.fillStyle = '#ff3b6b'; ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.stroke();
      circle(ctx, -86, 0, 9); ctx.fillStyle = '#fff'; ctx.fill();
      text(ctx, '50% OFF', 12, -6, 42, '#fff', { stroke: '#b8204a', lw: 6 });
      text(ctx, 'LOLLIPOPS', 12, 30, 18, '#ffe96b');
      ctx.restore();
    } else if (id === 'rain') {
      cloud(ctx, 60, 60, 60, '#eef3fb'); cloud(ctx, 330, 50, 70, '#e2eaf6');
      ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 3; ctx.lineCap = 'round';
      for (let k = 0; k < 40; k++) { const x = (k * 37) % W, y = (k * 29 + t * 300) % H; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 6, y + 16); ctx.stroke(); }
      ground('#7c9bc9');
      // umbrella kid with chocolate
      ctx.save(); ctx.translate(W / 2, H - 20);
      kid(ctx, LOOKS[2], 0, 0, { t, mood: 'happy', holding: 'choc' });
      ctx.fillStyle = '#ff5fa2'; ctx.beginPath(); ctx.arc(0, -150, 70, Math.PI, 0); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#ffcf3a'; ctx.beginPath(); ctx.arc(0, -150, 70, Math.PI * 1.33, Math.PI * 1.66); ctx.lineTo(0, -150); ctx.fill();
      ctx.strokeStyle = '#5a2448'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(0, -150); ctx.lineTo(0, -70); ctx.stroke();
      ctx.restore();
      choc(ctx, 120, H * 0.62, 90, 0); choc(ctx, W - 120, H * 0.62, 90, 1);
    } else if (id === 'party') {
      confetti(ctx, W, H, t, 50);
      ground('#ffb3d9');
      const cx = W / 2, cy = H - 50;
      rr(ctx, cx - 100, cy - 60, 200, 70, 14); ctx.fillStyle = '#fff3f8'; ctx.fill();
      rr(ctx, cx - 70, cy - 120, 140, 62, 12); ctx.fillStyle = '#ff9ad5'; ctx.fill();
      ctx.fillStyle = '#fff'; for (let k = 0; k < 7; k++) { circle(ctx, cx - 60 + k * 20, cy - 118, 10); ctx.fill(); }
      ctx.fillStyle = '#ff5fa2'; for (let k = 0; k < 9; k++) { circle(ctx, cx - 88 + k * 22, cy - 58, 9); ctx.fill(); }
      for (let k = 0; k < 5; k++) {
        const kx = cx - 44 + k * 22;
        rr(ctx, kx - 4, cy - 156, 8, 32, 3); ctx.fillStyle = ['#7a5cff', '#22c9a8', '#ffcf3a'][k % 3]; ctx.fill();
        ctx.fillStyle = '#ffb000'; ctx.beginPath(); ctx.ellipse(kx, cy - 166 + Math.sin(t * 15 + k) * 1.5, 5, 9 + Math.sin(t * 20 + k) * 2, 0, 0, TAU); ctx.fill();
        ctx.fillStyle = '#fff6a0'; ctx.beginPath(); ctx.ellipse(kx, cy - 164, 2.5, 5, 0, 0, TAU); ctx.fill();
      }
      for (let k = 0; k < 4; k++) gummy(ctx, k < 2 ? 70 + k * 80 : W - 230 + (k - 2) * 80, H * 0.6 + Math.sin(t * 4 + k) * 8, 80, k);
    } else if (id === 'festival') {
      ground('#ffe08a');
      ctx.save(); ctx.translate(W / 2, 30);
      const stripes = 8;
      for (let k = 0; k < stripes; k++) {
        ctx.fillStyle = k % 2 ? '#fff' : '#ff4f9a';
        ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-160 + (k * 320) / stripes, 120); ctx.lineTo(-160 + ((k + 1) * 320) / stripes, 120); ctx.fill();
      }
      ctx.fillStyle = '#ffcf3a'; ctx.beginPath(); ctx.moveTo(0, -20); ctx.lineTo(18, -10); ctx.lineTo(0, 0); ctx.fill();
      ctx.fillStyle = '#ffe8f2'; ctx.fillRect(-140, 120, 280, 70);
      ctx.fillStyle = '#5a2448'; ctx.fillRect(-30, 130, 60, 60);
      ctx.restore();
      cotton(ctx, 100, H * 0.55, 100, 0); cotton(ctx, W - 100, H * 0.55, 100, 1);
      confetti(ctx, W, H, t, 30);
    } else if (id === 'cocoa') {
      ground('#c99a70');
      for (let k = 0; k < 3; k++) choc(ctx, W / 2 - 110 + k * 110, H * 0.58 + (k === 1 ? -20 : 0), 120, k);
      ctx.save(); ctx.translate(W - 90, 110 + Math.sin(t * 3) * 6);
      ctx.fillStyle = '#ff3b3b'; ctx.beginPath(); ctx.moveTo(0, -50); ctx.lineTo(40, 0); ctx.lineTo(15, 0); ctx.lineTo(15, 50); ctx.lineTo(-15, 50); ctx.lineTo(-15, 0); ctx.lineTo(-40, 0); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 4; ctx.stroke(); ctx.restore();
      coin(ctx, 90, 90, 30); coin(ctx, 140, 130, 22);
    } else if (id === 'sunny') {
      sun(ctx, W - 100, 80, 46, t, true);
      cloud(ctx, 60, 70, 40);
      ground('#9be15d');
      for (let k = 0; k < 4; k++) {
        const x = ((t * 70 + k * 160) % (W + 120)) - 60;
        kid(ctx, LOOKS[k + 1], x, H - 16 - (k % 2) * 8, { walking: true, phase: t * 9 + k, t, mood: 'happy', holding: ['lolli', 'ice', 'gummy', 'lolli'][k] });
      }
    } else if (id === 'spooky') {
      ground('#3a2a5a');
      circle(ctx, W - 100, 70, 40); ctx.fillStyle = '#fff6c8'; ctx.fill();
      for (let k = 0; k < 3; k++) {
        const px = W / 2 - 130 + k * 130, py = H * 0.62 + Math.sin(t * 3 + k) * 6;
        ctx.fillStyle = '#ff8a1f'; ctx.beginPath(); ctx.ellipse(px, py, 50, 40, 0, 0, TAU); ctx.fill();
        ctx.strokeStyle = '#d96a00'; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(px, py, 20, 40, 0, 0, TAU); ctx.stroke();
        ctx.fillStyle = '#5a8a2a'; ctx.fillRect(px - 4, py - 52, 8, 14);
        ctx.fillStyle = '#ffe96b';
        ctx.beginPath(); ctx.moveTo(px - 24, py - 6); ctx.lineTo(px - 12, py - 20); ctx.lineTo(px - 2, py - 6); ctx.fill();
        ctx.beginPath(); ctx.moveTo(px + 24, py - 6); ctx.lineTo(px + 12, py - 20); ctx.lineTo(px + 2, py - 6); ctx.fill();
        ctx.beginPath(); ctx.arc(px, py + 6, 22, 0.1 * Math.PI, 0.9 * Math.PI); ctx.fill();
      }
      jaw(ctx, 80, H * 0.5, 70, 0); jaw(ctx, W - 80, H * 0.5, 70, 1);
    } else {
      // opening / normal
      if (id === 'opening') confetti(ctx, W, H, t, 50);
      ground('#ffc2dc');
      const items = ['lolli', 'gummy', 'choc', 'ice', 'jaw', 'cotton'];
      for (let k = 0; k < 6; k++) {
        const a = t * 0.6 + (k * TAU) / 6;
        candy(ctx, items[k], W / 2 + Math.cos(a) * 190, H * 0.5 + Math.sin(a) * 60, 76 + Math.sin(a) * 14, k);
      }
      if (id === 'opening') {
        ctx.save(); ctx.translate(W / 2, H * 0.48); ctx.rotate(Math.sin(t * 2) * 0.05);
        ctx.fillStyle = '#ff3b6b'; ctx.beginPath(); ctx.moveTo(-140, -20); ctx.lineTo(140, -20); ctx.lineTo(160, 0); ctx.lineTo(140, 20); ctx.lineTo(-140, 20); ctx.lineTo(-160, 0); ctx.closePath(); ctx.fill();
        text(ctx, 'GRAND OPENING', 0, 1, 26, '#fff', { stroke: '#b8204a', lw: 5 });
        ctx.restore();
      } else {
        star(ctx, W / 2, H * 0.5, 40 + Math.sin(t * 3) * 3);
      }
    }
  }

  // ======================= TITLE SCENE =======================
  const titleCandies = [];
  const TYPES = ['lolli', 'gummy', 'choc', 'ice', 'jaw', 'cotton'];
  for (let i = 0; i < 26; i++) titleCandies.push({ type: TYPES[i % 6], x: Math.random() * 1280, y: Math.random() * 720, s: 40 + Math.random() * 50, v: i, sp: 25 + Math.random() * 45, rot: Math.random() * TAU, vr: (Math.random() - 0.5) * 1.5 });

  function titleScene(ctx, t, W, H, dt) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#ff9fd0'); g.addColorStop(0.55, '#ffc9e3'); g.addColorStop(1, '#ffe7b8');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.translate(W / 2, H * 0.3); ctx.rotate(t * 0.08); ctx.fillStyle = 'rgba(255,255,255,0.2)';
    for (let k = 0; k < 16; k++) { ctx.rotate(TAU / 16); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-90, -1100); ctx.lineTo(90, -1100); ctx.fill(); }
    ctx.restore();
    for (const c of titleCandies) {
      c.y += c.sp * dt; c.rot += c.vr * dt;
      if (c.y > H + 60) { c.y = -60; c.x = Math.random() * W; }
      ctx.save(); ctx.globalAlpha = 0.85; ctx.translate(c.x, c.y); ctx.rotate(c.rot);
      candy(ctx, c.type, 0, 0, c.s, c.v); ctx.restore();
    }
    // hills + storefront
    ctx.fillStyle = '#9be6c9'; ctx.beginPath(); ctx.ellipse(250, H + 60, 420, 170, 0, 0, TAU); ctx.fill();
    ctx.fillStyle = '#7fd9b8'; ctx.beginPath(); ctx.ellipse(1060, H + 70, 460, 180, 0, 0, TAU); ctx.fill();
    const sx = 90, sy = H - 230, sw = 230, sh = 200;
    ctx.fillStyle = '#fff3f8'; rr(ctx, sx, sy, sw, sh, 10); ctx.fill();
    ctx.strokeStyle = '#ffb3d4'; ctx.lineWidth = 4; ctx.stroke();
    for (let i = 0; i < 7; i++) { ctx.fillStyle = i % 2 ? '#fff' : '#ff5fa2'; ctx.fillRect(sx - 12 + i * 36, sy - 6, 36, 40); ctx.beginPath(); ctx.arc(sx + 6 + i * 36, sy + 34, 18, 0, Math.PI); ctx.fill(); }
    ctx.fillStyle = '#bfefff'; rr(ctx, sx + 18, sy + 72, 110, 80, 8); ctx.fill();
    lolli(ctx, sx + 46, sy + 120, 50, 0); gummy(ctx, sx + 78, sy + 128, 38, 1); choc(ctx, sx + 106, sy + 122, 44, 0);
    ctx.fillStyle = '#7a5cff'; rr(ctx, sx + 150, sy + 80, 58, 120, 6); ctx.fill();
    circle(ctx, sx + 196, sy + 140, 4); ctx.fillStyle = '#ffd23f'; ctx.fill();
    for (let k = 0; k < 3; k++) {
      const x = 380 + ((t * 50 + k * 300) % 900);
      kid(ctx, LOOKS[k + 2], x, H - 30 + (k % 2) * 8, { walking: true, phase: t * 8 + k * 2, t, mood: 'excited', holding: ['lolli', 'ice', 'cotton'][k], flip: false });
    }
  }

  function makeIcon(type, size = 128, v = 0) {
    const c = document.createElement('canvas'); c.width = size; c.height = size;
    const x = c.getContext('2d');
    candy(x, type, size / 2, size / 2 + size * 0.04, size * 0.86, v);
    return c.toDataURL();
  }

  return { rr, circle, text, candy, coin, star, heart, cloud, kid, bubble, randomLook, shopBackground, awning, counter, shelfLayout, shelf, eventArt, titleScene, makeIcon, sun, shade };
})();
