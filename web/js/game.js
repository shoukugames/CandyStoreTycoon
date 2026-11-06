/* Candy Store Tycoon — game logic */
(() => {
  'use strict';
  const W = 1280, H = 720;
  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  const $ = id => document.getElementById(id);

  // ======================= DATA =======================
  const PRODUCTS = {
    lolli:  { name: 'Lollipop',      cost: 20, price: 45,  pop: 34, unlock: 1, color: '#ff5fa2', desc: 'Cheap and sells super fast. A kid favourite!' },
    gummy:  { name: 'Gummy Bears',   cost: 35, price: 75,  pop: 24, unlock: 1, color: '#ff9a3c', desc: 'Chewy, fruity and always popular.' },
    ice:    { name: 'Ice Pop',       cost: 25, price: 55,  pop: 13, unlock: 1, color: '#2fa8ff', desc: 'Cool treat. Goes wild on hot days!' },
    choc:   { name: 'Chocolate Bar', cost: 70, price: 160, pop: 12, unlock: 1, color: '#8b4a2b', desc: 'Pricey, sells slower, but BIG profit.' },
    jaw:    { name: 'Jawbreaker',    cost: 50, price: 115, pop: 10, unlock: 4, color: '#7a5cff', desc: 'Rainbow layers that last forever.' },
    cotton: { name: 'Cotton Candy',  cost: 60, price: 140, pop: 11, unlock: 7, color: '#ff8fd1', desc: 'Fluffy sugar clouds. Super trendy!' },
  };
  const ORDER = ['lolli', 'gummy', 'ice', 'choc', 'jaw', 'cotton'];

  const EVENTS = {
    opening:  { name: 'Grand Opening!', desc: 'Your candy store opens today! Buy candy at the Market, stock your shelves, then open the doors.', effects: [['info', 'Fewer customers while word spreads']] },
    normal:   { name: 'A Sweet Ordinary Day', desc: 'Nothing unusual today. A perfect day to plan ahead!', effects: [['info', 'Normal prices and customers']] },
    heatwave: { name: 'Summer Heatwave', desc: 'It is SO hot! Some chocolate bars melted in your pantry, but everyone wants ice pops.', melt: { choc: 5 }, sellMult: { ice: 2 }, demandMult: { ice: 3, choc: 0.5 }, effects: [['bad', 'Up to 5 chocolate bars melt'], ['good', 'Ice Pops sell for DOUBLE'], ['info', 'Lots of kids want Ice Pops']] },
    recess:   { name: 'School Recess Rush', desc: 'The school bell rang! A massive wave of hungry kids is coming. Restock your shelves twice as fast!', spawnMult: 1.7, waves: [18, 46], patienceMult: 0.85, effects: [['good', 'TONS of customers'], ['bad', 'Kids are a little less patient'], ['info', 'Two big waves of kids']] },
    sale:     { name: 'Wholesaler Sale', desc: 'Lollipops are half off at the market today! Stock up your pantry while it is cheap.', costMult: { lolli: 0.5 }, effects: [['good', 'Lollipops cost 50% less']] },
    rain:     { name: 'Rainy Day', desc: 'Pitter-patter! Fewer kids come out in the rain, but the ones who do want cozy chocolate.', spawnMult: 0.75, demandMult: { choc: 2.5, ice: 0.3 }, patienceMult: 1.2, effects: [['bad', 'Fewer customers'], ['good', 'Chocolate is in demand'], ['good', 'Kids wait longer']] },
    party:    { name: 'Birthday Party', desc: 'A big birthday party is happening nearby. Party kids buy gummy bears by the handful!', demandMult: { gummy: 2.5 }, bigOrder: 'gummy', effects: [['good', 'Gummy Bear demand way up'], ['info', 'Some kids buy 3-5 at once']] },
    festival: { name: 'Candy Festival', desc: 'The town candy festival is on! Everyone is happy to pay a little more today.', sellAll: 1.25, spawnMult: 1.15, effects: [['good', 'All candy sells for +25%'], ['good', 'More customers']] },
    cocoa:    { name: 'Cocoa Shortage', desc: 'Cocoa beans are hard to find. Chocolate costs more at the market, but sells for more too.', costMult: { choc: 1.5 }, sellMult: { choc: 1.3 }, effects: [['bad', 'Chocolate costs +50%'], ['good', 'Chocolate sells for +30%']] },
    sunny:    { name: 'Sunny Saturday', desc: 'No school and lovely weather! Families are out walking all day long.', spawnMult: 1.35, demandMult: { ice: 1.5 }, effects: [['good', 'Lots more customers']] },
    spooky:   { name: 'Spooky Costume Day', desc: 'Kids are trick-or-treating in costumes and they LOVE jawbreakers and lollipops.', demandMult: { jaw: 2.5, lolli: 1.5 }, spawnMult: 1.1, minDay: 5, effects: [['good', 'Jawbreakers & Lollipops in demand']] },
  };
  const EVENT_POOL = [['normal', 18], ['heatwave', 11], ['recess', 11], ['sale', 11], ['rain', 9], ['party', 9], ['festival', 7], ['cocoa', 7], ['sunny', 9], ['spooky', 6]];

  const UPGRADES = [
    { id: 'pantry',    name: 'Bigger Pantry',       desc: '+25 backroom storage slots', cost: [900, 1800, 3200], icon: 'box' },
    { id: 'shelf',     name: 'Extra Display Shelf', desc: 'Add another shelf to the shop floor', cost: [1200, 2600], icon: 'shelf' },
    { id: 'shelfSize', name: 'Taller Shelves',      desc: '+4 items on every shelf', cost: [1000, 2400], icon: 'tall' },
    { id: 'stocker',   name: 'Speedy Stocker',      desc: 'Restock shelves twice as fast', cost: [800], icon: 'bolt' },
    { id: 'sign',      name: 'Neon Candy Sign',     desc: '+20% more customers each level', cost: [1500, 3200], icon: 'sign' },
    { id: 'jukebox',   name: 'Jukebox',             desc: 'Music keeps kids waiting 35% longer', cost: [1100], icon: 'music' },
  ];

  const DAY_LENGTH = 80;           // seconds of real time per shop day
  const WIN_MONEY = 25000;
  const SAVE_PREFIX = 'candyStoreTycoon.slot.';
  const SLOTS = 3;

  // ======================= STATE =======================
  let state = null;
  let screen = 'title';           // 'title' | 'game'
  let time = 0, speed = 1, hoverShelf = -1, particles = [], modalStack = [], doorOpen = 0;
  let restockShelf = -1;
  let displayMoney = 0;
  const icons = {};

  function newState(name) {
    return {
      version: 1, shopName: name, day: 0, money: 1000, rep: 3,
      pantry: Object.fromEntries(ORDER.map(k => [k, 0])),
      upgrades: Object.fromEntries(UPGRADES.map(u => [u.id, 0])),
      shelves: [{ type: 'lolli', count: 0 }, { type: 'gummy', count: 0 }, { type: 'choc', count: 0 }],
      event: 'opening', lastEvent: null, phase: 'morning', today: {}, rush: null, summary: null,
      totals: { revenue: 0, served: 0, unhappy: 0, bestDay: 0 }, won: false, nextId: 1, tutorial: true,
    };
  }

  const ev = () => EVENTS[state.event] || EVENTS.normal;
  const pantryCap = () => 50 + 25 * state.upgrades.pantry;
  const shelfCap = () => 10 + 4 * state.upgrades.shelfSize;
  const pantryUsed = () => ORDER.reduce((a, k) => a + state.pantry[k], 0);
  const shelfStock = () => state.shelves.reduce((a, s) => a + s.count, 0);
  const unlocked = k => state.day >= PRODUCTS[k].unlock;
  const costOf = k => Math.max(1, Math.round(PRODUCTS[k].cost * ((ev().costMult || {})[k] || 1)));
  const priceOf = k => Math.round(PRODUCTS[k].price * ((ev().sellMult || {})[k] || 1) * (ev().sellAll || 1));
  const rentFor = d => Math.min(450, 60 + d * 15);
  const fmt = n => (n < 0 ? '-' : '') + Math.abs(Math.round(n)).toLocaleString('en-US');
  const yen = n => '¥' + fmt(n);
  const rand = (a, b) => a + Math.random() * (b - a);
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function syncShelves() {
    const want = 3 + state.upgrades.shelf;
    const extra = ['ice', 'gummy'];
    while (state.shelves.length < want) state.shelves.push({ type: extra[state.shelves.length - 3] || 'lolli', count: 0 });
  }

  // ======================= RESIZE =======================
  let scale = 1, dpr = 1;
  function resize() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    scale = Math.min(window.innerWidth / W, window.innerHeight / H);
    $('stage').style.transform = `translate(-50%, -50%) scale(${scale})`;
    canvas.width = Math.round(W * scale * dpr);
    canvas.height = Math.round(H * scale * dpr);
  }
  window.addEventListener('resize', resize);

  // ======================= UI HELPERS =======================
  function toast(msg, kind = '') {
    const el = document.createElement('div');
    el.className = 'toast ' + kind; el.textContent = msg;
    $('toasts').appendChild(el);
    while ($('toasts').children.length > 4) $('toasts').firstChild.remove();
    setTimeout(() => el.remove(), 3100);
  }

  function showModal(render, opts = {}) {
    modalStack.push({ render, ...opts });
    paintModal();
    hideRestock();
  }
  function replaceModal(render, opts = {}) { modalStack.pop(); showModal(render, opts); }
  function closeModal() {
    const top = modalStack.pop();
    if (top && top.onClose) top.onClose();
    paintModal();
  }
  function closeAllModals() { modalStack = []; paintModal(); }
  function paintModal() {
    const top = modalStack[modalStack.length - 1];
    if (!top) { $('modalLayer').classList.add('hidden'); $('modal').innerHTML = ''; return; }
    const scroll = $('modal').querySelector('.scroll');
    const st = scroll ? scroll.scrollTop : 0;
    $('modal').innerHTML = top.render();
    $('modalLayer').classList.remove('hidden');
    const ns = $('modal').querySelector('.scroll');
    if (ns && top._painted) ns.scrollTop = st;
    top._painted = true;
    const inp = $('modal').querySelector('input[autofocus]');
    if (inp) setTimeout(() => { inp.focus(); inp.select(); }, 30);
  }
  const refreshModal = () => { if (modalStack.length) paintModal(); };
  const isPaused = () => screen === 'game' && modalStack.length > 0;

  function starsHTML(rep, size = 20) {
    let s = '';
    for (let i = 1; i <= 5; i++) {
      const f = Math.max(0, Math.min(1, rep - (i - 1)));
      const id = 'sg' + Math.random().toString(36).slice(2, 8);
      s += `<svg class="star" style="width:${size}px;height:${size}px" viewBox="0 0 24 24"><defs><linearGradient id="${id}"><stop offset="${f}" stop-color="#ffd23f"/><stop offset="${f}" stop-color="#f1dce7"/></linearGradient></defs><path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7L12 17.3 5.8 20.9l1.6-7L2 9.2l7.1-.6z" fill="url(#${id})" stroke="${f > 0 ? '#e0a100' : '#d8b8c8'}" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
    }
    return s;
  }

  let lastHud = '';
  function updateHUD() {
    if (!state) return;
    $('hudShop').textContent = state.shopName;
    $('hudDay').textContent = state.day;
    $('hudEvent').textContent = state.event === 'normal' ? '' : ev().name.replace('!', '');
    displayMoney += (state.money - displayMoney) * 0.2;
    if (Math.abs(state.money - displayMoney) < 1) displayMoney = state.money;
    $('hudMoney').textContent = fmt(displayMoney);
    $('hudMoney').style.color = state.money < 0 ? '#d32f2f' : '';
    $('hudPantry').textContent = `${pantryUsed()}/${pantryCap()}`;
    const repKey = Math.round(state.rep * 20);
    if (repKey + '' !== lastHud) { $('hudStars').innerHTML = starsHTML(state.rep); lastHud = repKey + ''; }
    const rush = state.phase === 'rush' && state.rush;
    $('clockPill').classList.toggle('hidden', !rush);
    if (rush) {
      const f = Math.min(1, state.rush.elapsed / DAY_LENGTH);
      const mins = 9 * 60 + f * 9 * 60;
      const hh = Math.floor(mins / 60), mm = Math.floor(mins % 60 / 15) * 15;
      $('hudClock').textContent = f >= 1 ? 'Closing' : `${hh > 12 ? hh - 12 : hh}:${String(mm).padStart(2, '0')} ${hh >= 12 ? 'PM' : 'AM'}`;
      $('hudClockBar').style.width = (f * 100) + '%';
    }
  }

  function updateBar() {
    if (!state) return;
    const prep = state.phase === 'prep', rush = state.phase === 'rush';
    $('btnMarket').classList.toggle('hidden', !prep);
    $('btnShelves').classList.toggle('hidden', !prep);
    $('btnOpen').classList.toggle('hidden', !prep);
    $('btnSpeed').classList.toggle('hidden', !rush);
    $('btnSpeed').textContent = `Speed ${speed}x`;
    $('btnMusic').classList.toggle('off', !Sound.settings.music);
    let tip = '';
    if (prep) {
      const pu = pantryUsed(), ss = shelfStock();
      $('btnOpen').classList.remove('pulse'); $('btnMarket').classList.remove('pulse'); $('btnShelves').classList.remove('pulse');
      if (pu === 0 && ss === 0) { tip = 'Step 1: Visit the <b>Market</b> and buy some candy for your pantry!'; $('btnMarket').classList.add('pulse'); }
      else if (ss === 0) { tip = 'Step 2: Put candy on your display shelves. Kids only buy what they can see!'; $('btnShelves').classList.add('pulse'); }
      else if (pu > 0 && state.shelves.some(s => s.count < shelfCap() && state.pantry[s.type] > 0)) { tip = 'Shelves have room! Fill them up, or press <b>Open Store</b> when ready.'; $('btnOpen').classList.add('pulse'); }
      else { tip = 'All set! Press <b>Open Store</b> to let the kids in.'; $('btnOpen').classList.add('pulse'); }
    } else if (rush) {
      tip = '<b>Click a shelf</b> to restock it from your pantry before it runs out!';
    }
    $('tip').innerHTML = tip;
    $('tip').classList.toggle('hidden', !tip);
  }

  function refreshAll() { updateHUD(); updateBar(); refreshModal(); }

  // ======================= DAY FLOW =======================
  function startNewGame(name) {
    state = newState(name || 'Sweet Treats');
    displayMoney = state.money;
    screen = 'game';
    particles = []; speed = 1;
    showGameUI();
    beginDay();
  }

  function pickEvent() {
    if (state.day === 1) return 'opening';
    const pool = EVENT_POOL.filter(([id]) => id !== state.lastEvent && (EVENTS[id].minDay || 0) <= state.day);
    const total = pool.reduce((a, [, w]) => a + w, 0);
    let r = Math.random() * total;
    for (const [id, w] of pool) { if ((r -= w) <= 0) return id; }
    return 'normal';
  }

  function beginDay() {
    state.day++;
    state.lastEvent = state.event;
    state.event = pickEvent();
    state.today = { melted: 0 };
    const melt = ev().melt;
    if (melt) for (const k in melt) { const n = Math.min(melt[k], state.pantry[k]); state.pantry[k] -= n; state.today.melted += n; }
    const newly = ORDER.filter(k => PRODUCTS[k].unlock === state.day && state.day > 1);
    state.today.unlocked = newly;
    state.phase = 'morning';
    state.rush = null;
    Sound.setRush(false);
    refreshAll();
    showMorning();
  }

  function showMorning() {
    Sound.play('fanfare');
    showModal(() => {
      const e = ev();
      let extra = '';
      if (state.today.melted > 0) extra += `<div class="chip bad" style="margin-top:8px">Oh no! ${state.today.melted} chocolate bar${state.today.melted > 1 ? 's' : ''} melted in your pantry!</div>`;
      if (state.today.unlocked && state.today.unlocked.length) extra += `<div class="chip good" style="margin-top:8px">New candy unlocked at the Market: ${state.today.unlocked.map(k => PRODUCTS[k].name).join(', ')}!</div>`;
      return `<div class="panel event-card">
        <h2>Day ${state.day}: Good Morning!</h2>
        <canvas id="eventArt" width="1120" height="500"></canvas>
        <div class="ename">${e.name}</div>
        <p class="edesc">${e.desc}</p>
        <div class="eeffects">${(e.effects || []).map(([k, t]) => `<span class="chip ${k}">${t}</span>`).join('')}</div>
        ${extra}
        <div class="row"><button class="btn btn-pink btn-big" data-action="startPrep">Let's Go!</button></div>
      </div>`;
    }, { kind: 'morning' });
  }

  function startPrep() {
    closeAllModals();
    state.phase = 'prep';
    if (checkGameOver()) return;
    if (state.day === 1 && state.tutorial) setTimeout(() => toast('Start by visiting the Market!', 'good'), 400);
    refreshAll();
  }

  function cheapestCost() { return Math.min(...ORDER.filter(unlocked).map(costOf)); }

  function checkGameOver() {
    if (pantryUsed() + shelfStock() === 0 && state.money < cheapestCost()) {
      state.phase = 'gameover';
      showGameOver();
      return true;
    }
    return false;
  }

  function openStore() {
    if (shelfStock() === 0) { Sound.play('error'); toast('Your shelves are empty! Stock them first.', 'bad'); return; }
    const e = ev();
    state.phase = 'rush';
    state.rush = {
      elapsed: 0, spawnT: 1.0, customers: [], served: 0, unhappy: 0, revenue: 0, sold: {}, repStart: state.rep,
      waves: (e.waves || []).slice(), queue: [],
    };
    state.tutorial = false;
    speed = 1;
    Sound.play('bell');
    Sound.setRush(true);
    toast('The store is OPEN!', 'good');
    refreshAll();
  }

  function spawnInterval() {
    const e = ev();
    const dayMult = state.day <= 3 ? 0.6 + state.day * 0.12 : Math.min(1.45, 1 + (state.day - 4) * 0.025);
    const repMult = 0.55 + state.rep * 0.15;
    const signMult = 1 + 0.2 * state.upgrades.sign;
    return 3.0 / ((e.spawnMult || 1) * dayMult * repMult * signMult);
  }

  function pickCraving(exclude) {
    const e = ev(); const dm = e.demandMult || {};
    const opts = ORDER.filter(k => unlocked(k) && k !== exclude).map(k => [k, PRODUCTS[k].pop * (dm[k] || 1)]);
    const total = opts.reduce((a, [, w]) => a + w, 0);
    let r = Math.random() * total;
    for (const [k, w] of opts) if ((r -= w) <= 0) return k;
    return opts[0][0];
  }

  function spawnCustomer() {
    const r = state.rush, e = ev();
    const craving = pickCraving();
    const alt = Math.random() < 0.3 ? pickCraving(craving) : null;
    let qty = Math.random() < 0.7 ? 1 : Math.random() < 0.75 ? 2 : 3;
    if (e.bigOrder === craving && Math.random() < 0.55) qty = 3 + ((Math.random() * 3) | 0);
    const patience = rand(9, 13) * (e.patienceMult || 1) * (state.upgrades.jukebox ? 1.35 : 1);
    const c = {
      id: state.nextId++, look: Art.randomLook(), x: -50, y: rand(580, 615), state: 'walk', tx: 0, shelf: -1,
      craving, alt, qty, patience, maxPatience: patience, phase: Math.random() * 6, mood: 'happy', timer: 0,
      speed: rand(150, 190), holding: null, checkT: 0, wantType: craving,
    };
    targetCustomer(c);
    r.customers.push(c);
    doorOpen = 1.2;
    if (Math.random() < 0.35) Sound.play('bell');
  }

  function shelfX(i) { const l = Art.shelfLayout(state.shelves.length)[i]; return l.x + l.w / 2; }

  function findShelf(c, needStock) {
    for (const type of [c.craving, c.alt]) {
      if (!type) continue;
      let best = -1;
      state.shelves.forEach((s, i) => {
        if (s.type === type && (!needStock || s.count > 0)) {
          if (best < 0 || s.count > state.shelves[best].count) best = i;
        }
      });
      if (best >= 0) return { i: best, type };
    }
    return null;
  }

  function targetCustomer(c) {
    const f = findShelf(c, true) || findShelf(c, false);
    if (f) { c.shelf = f.i; c.wantType = f.type; c.tx = shelfX(f.i) + rand(-55, 55); }
    else { c.shelf = -1; c.wantType = c.craving; c.tx = rand(300, 1000); }
    c.state = 'walk';
  }

  function addParticle(p) { particles.push({ life: 1, max: 1, vx: 0, vy: -40, ...p }); }

  function updateRush(dt) {
    const r = state.rush;
    r.elapsed += dt;
    const open = r.elapsed < DAY_LENGTH;
    if (open) {
      r.spawnT -= dt;
      if (r.spawnT <= 0) { spawnCustomer(); r.spawnT = spawnInterval() * rand(0.55, 1.45); }
      if (r.waves.length && r.elapsed >= r.waves[0]) {
        r.waves.shift();
        for (let k = 0; k < 6; k++) r.queue.push(r.elapsed + k * 0.45);
        toast('Here comes a wave of kids!', '');
        Sound.play('whoosh');
      }
      while (r.queue.length && r.elapsed >= r.queue[0]) { r.queue.shift(); spawnCustomer(); }
    } else if (!r.closed) {
      r.closed = true;
      Sound.play('bell');
      toast('Closing time! Finishing up the last customers...', '');
      for (const c of r.customers) if (c.state === 'walk' || c.state === 'wait') {
        if (c.state === 'wait' || !findShelf(c, true)) { c.state = 'leave'; c.mood = 'wait'; c.tx = -80; }
      }
    }

    // restocking
    state.shelves.forEach((s, i) => {
      if (!s.restock) return;
      s.restock.t -= dt;
      if (s.restock.t <= 0) completeRestock(i);
    });

    for (const c of r.customers) updateCustomer(c, dt, open);
    r.customers = r.customers.filter(c => !c.gone);
    if (!open && r.customers.length === 0) endDay();
  }

  function updateCustomer(c, dt, open) {
    const move = (tx) => {
      const d = tx - c.x;
      const step = c.speed * dt;
      c.flip = d < 0;
      if (Math.abs(d) <= step) { c.x = tx; return true; }
      c.x += Math.sign(d) * step; c.phase += dt * 11; return false;
    };
    c.walking = false;
    switch (c.state) {
      case 'walk':
        c.walking = true;
        if (move(c.tx)) { c.state = 'look'; c.timer = 0.45; c.walking = false; }
        break;
      case 'look':
        c.timer -= dt;
        if (c.timer <= 0) tryBuy(c);
        break;
      case 'wait': {
        c.patience -= dt;
        const f = c.patience / c.maxPatience;
        c.mood = f > 0.6 ? 'happy' : f > 0.3 ? 'wait' : 'worried';
        c.checkT -= dt;
        if (c.checkT <= 0) {
          c.checkT = 0.25;
          const found = findShelf(c, true);
          if (found) { c.noShelf = false; c.shelf = found.i; c.wantType = found.type; c.tx = shelfX(found.i) + rand(-50, 50); c.state = 'walk'; break; }
        }
        if (c.patience <= 0) {
          c.state = 'leave'; c.mood = 'sad'; c.tx = -80;
          state.rush.unhappy++;
          state.rep = Math.max(1, state.rep - (c.noShelf ? 0.025 : 0.05));
          Sound.play('sad');
          addParticle({ kind: 'storm', x: c.x, y: c.y - 150, life: 1.6, max: 1.6, vy: -20 });
          addParticle({ kind: 'text', x: c.x, y: c.y - 130, text: c.noShelf ? `No ${PRODUCTS[c.craving].name}?!` : 'Too slow!', color: '#ff5b5b', life: 1.6, max: 1.6 });
        }
        break;
      }
      case 'exit':
        c.walking = true;
        if (move(1360)) c.gone = true;
        break;
      case 'leave':
        c.walking = true;
        if (move(c.tx)) c.gone = true;
        if (c.x < 120) doorOpen = Math.max(doorOpen, 0.6);
        break;
    }
  }

  function tryBuy(c) {
    const s = state.shelves[c.shelf];
    if (s && s.type === c.wantType && s.count > 0) {
      const n = Math.min(c.qty, s.count);
      s.count -= n;
      const earn = n * priceOf(s.type);
      state.money += earn;
      const r = state.rush;
      r.revenue += earn; r.served++;
      r.sold[s.type] = (r.sold[s.type] || 0) + n;
      state.rep = Math.min(5, state.rep + (n === c.qty ? 0.035 : 0.015));
      c.holding = s.type; c.holdV = c.id % 4;
      c.mood = 'excited'; c.state = 'exit';
      Sound.play('coin');
      $('hudMoney').parentElement.classList.remove('flash'); void $('hudMoney').offsetWidth; $('hudMoney').parentElement.classList.add('flash');
      addParticle({ kind: 'text', x: c.x, y: c.y - 150, text: '+' + yen(earn), color: '#0e8a6f', life: 1.3, max: 1.3, vy: -60, big: true });
      for (let k = 0; k < 4; k++) addParticle({ kind: 'coin', x: c.x + rand(-10, 10), y: c.y - 110, vx: rand(-90, 90), vy: rand(-220, -140), g: 500, life: 0.9, max: 0.9 });
      addParticle({ kind: 'heart', x: c.x + 18, y: c.y - 140, vy: -50, life: 1.1, max: 1.1 });
      if (s.count === 0) toast(`${PRODUCTS[s.type].name} shelf is empty! Click it to restock.`, 'bad');
    } else {
      // nothing here — wait, or move on if another shelf has it
      const found = findShelf(c, true);
      if (found && found.i !== c.shelf) { c.shelf = found.i; c.wantType = found.type; c.tx = shelfX(found.i) + rand(-50, 50); c.state = 'walk'; }
      else if (state.rush.closed) { c.state = 'leave'; c.mood = 'wait'; c.tx = -80; }
      else { c.state = 'wait'; if (!found && !findShelf(c, false)) { c.noShelf = true; c.patience = Math.min(c.patience, c.maxPatience * 0.45); } }
    }
  }

  function restockTime() { return (state.upgrades.stocker ? 0.8 : 1.6); }

  function beginRestock(i, type) {
    const s = state.shelves[i];
    if (s.restock) return;
    if (state.pantry[type] <= 0) { Sound.play('error'); toast(`No ${PRODUCTS[type].name} in your pantry!`, 'bad'); return; }
    if (s.type === type && s.count >= shelfCap()) { Sound.play('error'); toast('That shelf is already full!', ''); return; }
    s.restock = { type, t: restockTime(), total: restockTime() };
    Sound.play('pop');
    hideRestock();
  }

  function completeRestock(i) {
    const s = state.shelves[i], type = s.restock.type;
    s.restock = null;
    if (s.type !== type) { state.pantry[s.type] = (state.pantry[s.type] || 0) + s.count; s.count = 0; s.type = type; }
    const n = Math.min(shelfCap() - s.count, state.pantry[type]);
    s.count += n; state.pantry[type] -= n;
    Sound.play('restock');
    const l = Art.shelfLayout(state.shelves.length)[i];
    addParticle({ kind: 'text', x: l.x + l.w / 2, y: l.y + 30, text: `+${n} ${PRODUCTS[type].name}`, color: '#7a5cff', life: 1.2, max: 1.2 });
    for (let k = 0; k < 10; k++) addParticle({ kind: 'spark', x: l.x + rand(10, l.w - 10), y: l.y + rand(60, 220), vy: rand(-60, -20), life: 0.8, max: 0.8 });
  }

  function endDay() {
    const r = state.rush;
    const rent = rentFor(state.day);
    state.money -= rent;
    const profit = r.revenue - rent;
    state.summary = { day: state.day, served: r.served, unhappy: r.unhappy, revenue: r.revenue, rent, profit, sold: r.sold, repStart: r.repStart, repEnd: state.rep, event: state.event };
    state.totals.revenue += r.revenue; state.totals.served += r.served; state.totals.unhappy += r.unhappy;
    state.totals.bestDay = Math.max(state.totals.bestDay, r.revenue);
    state.rush = null;
    state.phase = 'summary';
    state.shelves.forEach(s => { if (s.restock) { s.restock = null; } });
    Sound.setRush(false);
    Sound.play('fanfare');
    refreshAll();
    showSummary();
  }

  function showSummary() {
    showModal(() => {
      const s = state.summary;
      const repDiff = s.repEnd - s.repStart;
      const sold = Object.entries(s.sold).sort((a, b) => b[1] - a[1]);
      const best = sold[0];
      let msg = 'Nice work today!';
      if (s.unhappy === 0 && s.served > 5) msg = 'Perfect day — every kid left happy!';
      else if (s.unhappy > s.served) msg = 'Lots of kids left empty-handed. Try keeping shelves stocked!';
      else if (s.profit < 0) msg = 'You lost money today. Stock more candy so you can sell more!';
      return `<div class="panel summary">
        <h2 class="purple">Day ${s.day} Complete!</h2>
        <p style="text-align:center;font-weight:600">${msg}</p>
        <div class="stats">
          <div class="stat"><span>Happy customers</span><b class="pos">${s.served}</b></div>
          <div class="stat"><span>Unhappy customers</span><b class="${s.unhappy ? 'neg' : ''}">${s.unhappy}</b></div>
          <div class="stat"><span>Sales</span><b class="pos">${yen(s.revenue)}</b></div>
          <div class="stat"><span>Shop rent</span><b class="neg">-${yen(s.rent)}</b></div>
          <div class="stat big"><span>Today's profit</span><b class="${s.profit >= 0 ? 'pos' : 'neg'}">${s.profit >= 0 ? '+' : ''}${yen(s.profit)}</b></div>
          <div class="stat"><span>Budget</span><b>${yen(state.money)}</b></div>
          <div class="stat"><span>Rating</span><span style="display:flex;align-items:center;gap:6px">${starsHTML(state.rep, 18)} <b class="${repDiff >= 0 ? 'pos' : 'neg'}" style="font-size:15px">${repDiff >= 0 ? '+' : ''}${repDiff.toFixed(1)}</b></span></div>
        </div>
        ${sold.length ? `<div class="soldlist">${sold.map(([k, n]) => `<div class="sold"><img src="${icons[k]}" alt="">${n} sold</div>`).join('')}</div>` : ''}
        ${best ? `<p style="text-align:center;font-size:15px;color:var(--ink-soft)">Best seller: <b>${PRODUCTS[best[0]].name}</b></p>` : ''}
        <div class="row">
          <button class="btn btn-white" data-action="save"><span class="bi bi-save"></span>Save Game</button>
          <button class="btn btn-pink btn-big" data-action="nextDay">Next Day</button>
        </div>
      </div>`;
    }, { kind: 'summary' });
  }

  function nextDay() {
    closeAllModals();
    if (checkGameOver()) return;
    if (!state.won && state.money >= WIN_MONEY) { state.won = true; showWin(); return; }
    beginDay();
  }

  function showWin() {
    Sound.play('win');
    showModal(() => `<div class="panel summary" style="text-align:center">
      <h2 class="mint">Candy Tycoon!</h2>
      <canvas id="eventArt" data-event="opening" width="1040" height="400" style="width:520px;height:200px;border-radius:20px;border:4px solid #fff;align-self:center"></canvas>
      <p style="font-size:22px;font-weight:700;margin-top:12px">You reached ${yen(WIN_MONEY)}!</p>
      <p>${esc(state.shopName)} is now the most famous candy store in town. Amazing job, Tycoon!</p>
      <p style="color:var(--ink-soft)">Days played: ${state.day} &middot; Happy kids served: ${fmt(state.totals.served)}</p>
      <div class="row"><button class="btn btn-pink btn-big" data-action="keepPlaying">Keep Playing</button></div>
    </div>`);
  }

  function showGameOver() {
    Sound.play('sad');
    refreshAll();
    showModal(() => `<div class="panel summary" style="text-align:center">
      <h2 class="dark">Game Over</h2>
      <p style="font-size:22px;font-weight:700">Out of candy and out of cash!</p>
      <p>${esc(state.shopName)} had to close its doors after ${state.day} day${state.day > 1 ? 's' : ''}.</p>
      <div class="stats">
        <div class="stat"><span>Total sales</span><b class="pos">${yen(state.totals.revenue)}</b></div>
        <div class="stat"><span>Happy kids</span><b>${fmt(state.totals.served)}</b></div>
        <div class="stat"><span>Best day</span><b>${yen(state.totals.bestDay)}</b></div>
        <div class="stat"><span>Final rating</span><span>${starsHTML(state.rep, 18)}</span></div>
      </div>
      <p style="color:var(--ink-soft)">Tip: always keep enough money to buy more stock tomorrow!</p>
      <div class="row">
        <button class="btn btn-mint" data-action="loadMenu">Load a Save</button>
        <button class="btn btn-pink btn-big" data-action="quitConfirmed">Main Menu</button>
      </div>
    </div>`, { kind: 'gameover' });
  }

  // ======================= MARKET =======================
  let marketTab = 'candy';
  function upgradeIcon(kind) {
    const s = {
      box: '<path d="M8 22l24-10 24 10v24L32 56 8 46z" fill="#e0a96d" stroke="#9c6630" stroke-width="3" stroke-linejoin="round"/><path d="M8 22l24 10 24-10M32 32v24" stroke="#9c6630" stroke-width="3" fill="none"/><path d="M44 8v14M37 15h14" stroke="#22c9a8" stroke-width="5" stroke-linecap="round"/>',
      shelf: '<rect x="10" y="8" width="44" height="50" rx="5" fill="#e0a66d" stroke="#9c6630" stroke-width="3"/><rect x="15" y="13" width="34" height="40" fill="#fff1f7"/><path d="M15 33h34" stroke="#a8693a" stroke-width="4"/><circle cx="23" cy="26" r="5" fill="#ff5fa2"/><circle cx="36" cy="26" r="5" fill="#7a5cff"/><circle cx="29" cy="46" r="5" fill="#22c9a8"/>',
      tall: '<rect x="16" y="4" width="32" height="56" rx="5" fill="#e0a66d" stroke="#9c6630" stroke-width="3"/><path d="M20 22h24M20 40h24" stroke="#a8693a" stroke-width="4"/><path d="M56 30V10M50 16l6-6 6 6" stroke="#22c9a8" stroke-width="4" fill="none" stroke-linecap="round"/>',
      bolt: '<circle cx="32" cy="32" r="26" fill="#ffcf3a" stroke="#d99e00" stroke-width="3"/><path d="M36 10L20 36h12l-4 18 16-26H32z" fill="#fff" stroke="#d99e00" stroke-width="2.5" stroke-linejoin="round"/>',
      sign: '<rect x="6" y="14" width="52" height="34" rx="10" fill="#7a5cff" stroke="#5636d6" stroke-width="3"/><text x="32" y="38" text-anchor="middle" font-family="Fredoka,sans-serif" font-weight="700" font-size="17" fill="#ffe96b">OPEN</text><circle cx="12" cy="10" r="3" fill="#ff5fa2"/><circle cx="52" cy="10" r="3" fill="#22c9a8"/>',
      music: '<rect x="12" y="6" width="40" height="52" rx="18" fill="#ff5fa2" stroke="#d93a7d" stroke-width="3"/><circle cx="32" cy="38" r="10" fill="#ffe96b"/><path d="M20 22h24" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
    }[kind];
    return `<svg class="uico" viewBox="0 0 64 64">${s}</svg>`;
  }

  function showMarket() {
    marketTab = 'candy';
    showModal(() => {
      const used = pantryUsed(), cap = pantryCap();
      const pct = Math.min(100, (used / cap) * 100);
      let body = '';
      if (marketTab === 'candy') {
        body = `<div class="cards">${ORDER.map(k => {
          const p = PRODUCTS[k];
          if (!unlocked(k)) return `<div class="card locked"><img src="${icons[k]}" alt=""><div class="name">${p.name}</div><div class="desc">${p.desc}</div><div class="lockmsg">Unlocks on Day ${p.unlock}</div></div>`;
          const c = costOf(k), pr = priceOf(k);
          const cheaper = c < p.cost, pricier = c > p.cost, sellUp = pr > p.price;
          const maxN = Math.max(0, Math.min(Math.floor(state.money / c), cap - used));
          const btn = (n, label) => `<button class="btn btn-sm ${n === 'max' ? 'btn-purple' : 'btn-mint'}" data-action="buy" data-type="${k}" data-n="${n}" ${(n === 'max' ? maxN < 1 : maxN < n) ? 'disabled' : ''}>${label}</button>`;
          return `<div class="card">
            ${cheaper ? '<div class="tag">SALE!</div>' : ''}${sellUp ? '<div class="tag good">HOT!</div>' : ''}
            <img src="${icons[k]}" alt="">
            <div class="name">${p.name}</div>
            <div class="desc">${p.desc}</div>
            <div class="prices"><span class="cost">Buy ${cheaper || pricier ? `<s>¥${p.cost}</s>` : ''}¥${c}</span><span class="sell">Sell ¥${pr}</span></div>
            <div class="owned">In pantry: <b>${state.pantry[k]}</b> &middot; Profit ¥${pr - c} each</div>
            <div class="buyrow">${btn(1, '+1')}${btn(5, '+5')}${btn(10, '+10')}${btn('max', 'Max')}</div>
          </div>`;
        }).join('')}</div>`;
      } else {
        body = `<div class="upgrades">${UPGRADES.map(u => {
          const lvl = state.upgrades[u.id], max = u.cost.length, done = lvl >= max, c = u.cost[lvl];
          return `<div class="upg">${upgradeIcon(u.icon)}<div class="uinfo"><div class="uname">${u.name}</div><div class="udesc">${u.desc}</div><div class="ulvl">Level ${lvl}/${max}</div></div>
            ${done ? '<span class="chip good">MAXED</span>' : `<button class="btn btn-sm btn-purple" data-action="upgrade" data-id="${u.id}" ${state.money < c ? 'disabled' : ''}>${yen(c)}</button>`}</div>`;
        }).join('')}</div>`;
      }
      return `<div class="panel" style="width:900px">
        <button class="close" data-action="close">&times;</button>
        <h2 class="mint">Wholesale Market</h2>
        <div class="subbar">
          <span>Budget: <b style="color:#b36b00">${yen(state.money)}</b></span>
          <span style="display:flex;align-items:center;gap:8px;flex:1;max-width:380px">Pantry <div class="meter"><i class="${used >= cap ? 'full' : ''}" style="width:${pct}%"></i><span>${used} / ${cap}</span></div></span>
        </div>
        <div class="tabs"><button class="tab ${marketTab === 'candy' ? 'on' : ''}" data-action="mtab" data-tab="candy">Candy Stock</button><button class="tab ${marketTab === 'upg' ? 'on' : ''}" data-action="mtab" data-tab="upg">Shop Upgrades</button></div>
        <div class="scroll">${body}</div>
        <div class="row" style="margin-top:12px"><button class="btn btn-purple" data-action="toShelves">Stock Shelves Next</button><button class="btn btn-white" data-action="close">Done</button></div>
      </div>`;
    }, { kind: 'market' });
  }

  function buy(type, nRaw) {
    const c = costOf(type), room = pantryCap() - pantryUsed();
    let n = nRaw === 'max' ? Math.min(Math.floor(state.money / c), room) : +nRaw;
    if (room <= 0) { Sound.play('error'); toast('Your pantry is full! Put candy on shelves to make space.', 'bad'); return; }
    if (n > room) { Sound.play('error'); toast(`Only ${room} space left in the pantry!`, 'bad'); return; }
    if (n * c > state.money) { Sound.play('error'); toast('Not enough money!', 'bad'); return; }
    if (n <= 0) return;
    state.money -= n * c;
    state.pantry[type] += n;
    Sound.play('pop');
    refreshAll();
  }

  function buyUpgrade(id) {
    const u = UPGRADES.find(x => x.id === id), lvl = state.upgrades[id], c = u.cost[lvl];
    if (c === undefined) return;
    if (state.money < c) { Sound.play('error'); toast('Not enough money!', 'bad'); return; }
    state.money -= c; state.upgrades[id]++;
    syncShelves();
    Sound.play('win');
    toast(`${u.name} purchased!`, 'good');
    refreshAll();
  }

  // ======================= SHELVES PANEL =======================
  function showShelves() {
    showModal(() => {
      const cap = shelfCap();
      return `<div class="panel" style="width:900px">
        <button class="close" data-action="close">&times;</button>
        <h2 class="purple">Stock Your Shelves</h2>
        <div class="subbar"><span>Pick a candy for each shelf, then fill it from your pantry. Only candy on shelves can be sold!</span></div>
        <div class="subbar" style="justify-content:center;gap:8px;flex-wrap:wrap">
          ${ORDER.filter(unlocked).map(k => `<span class="sold"><img src="${icons[k]}" alt="">${state.pantry[k]}</span>`).join('')}
          <span style="font-size:15px;color:var(--ink-soft)">in pantry (${pantryUsed()}/${pantryCap()})</span>
        </div>
        <div class="scroll"><div class="shelfrows">
          ${state.shelves.map((s, i) => `<div class="shelfrow">
            <div class="sname">Shelf ${i + 1}</div>
            <div class="picker">${ORDER.map(k => `<button class="pick ${s.type === k ? 'on' : ''} ${unlocked(k) ? '' : 'lock'}" data-action="setType" data-i="${i}" data-type="${k}" title="${PRODUCTS[k].name}"><img src="${icons[k]}" alt=""><span class="n">${unlocked(k) ? state.pantry[k] : '?'}</span></button>`).join('')}</div>
            <div class="count"><div>${PRODUCTS[s.type].name}: ${s.count}/${cap}</div><div class="meter"><i style="width:${(s.count / cap) * 100}%"></i></div></div>
            <div class="ctrls">
              <button class="btn btn-sm btn-white" data-action="shelfAdd" data-i="${i}" data-n="-1" ${s.count ? '' : 'disabled'}>-1</button>
              <button class="btn btn-sm btn-white" data-action="shelfAdd" data-i="${i}" data-n="1" ${s.count < cap && state.pantry[s.type] ? '' : 'disabled'}>+1</button>
              <button class="btn btn-sm btn-pink" data-action="shelfAdd" data-i="${i}" data-n="fill" ${s.count < cap && state.pantry[s.type] ? '' : 'disabled'}>Fill</button>
            </div>
          </div>`).join('')}
        </div></div>
        <div class="row" style="margin-top:14px">
          <button class="btn btn-mint" data-action="fillAll">Fill All Shelves</button>
          <button class="btn btn-pink btn-big" data-action="openFromShelves"><span class="bi bi-door"></span>Open Store</button>
          <button class="btn btn-white" data-action="close">Done</button>
        </div>
      </div>`;
    }, { kind: 'shelves' });
  }

  function setShelfType(i, type) {
    const s = state.shelves[i];
    if (!unlocked(type) || s.type === type) return;
    // put current items back into the pantry (they came from there)
    state.pantry[s.type] += s.count; s.count = 0; s.type = type;
    Sound.play('click');
    refreshAll();
  }
  function shelfAdd(i, n) {
    const s = state.shelves[i], cap = shelfCap();
    if (n === 'fill') n = Math.min(cap - s.count, state.pantry[s.type]);
    n = +n;
    if (n > 0) { n = Math.min(n, cap - s.count, state.pantry[s.type]); }
    else { n = Math.max(n, -s.count); }
    if (!n) return;
    s.count += n; state.pantry[s.type] -= n;
    Sound.play(n > 0 ? 'pop' : 'click');
    refreshAll();
  }
  function fillAll() {
    let moved = 0;
    state.shelves.forEach(s => { const n = Math.min(shelfCap() - s.count, state.pantry[s.type]); s.count += n; state.pantry[s.type] -= n; moved += n; });
    if (moved) Sound.play('restock'); else { Sound.play('error'); toast('Nothing to fill — buy matching candy or change shelf types.', ''); }
    refreshAll();
  }

  // ======================= RESTOCK POPUP =======================
  function showRestock(i) {
    const s = state.shelves[i];
    if (s.restock) { toast('Already restocking this shelf!', ''); return; }
    restockShelf = i;
    const l = Art.shelfLayout(state.shelves.length)[i];
    const opts = ORDER.filter(k => unlocked(k));
    const el = $('restockPop');
    el.innerHTML = `<div class="rtitle">Restock Shelf ${i + 1} from pantry</div><div class="ropts">${opts.map(k => `<button class="ropt ${k === s.type ? 'cur' : ''}" data-action="restock" data-i="${i}" data-type="${k}" ${state.pantry[k] ? '' : 'disabled style="opacity:.35"'}><img src="${icons[k]}" alt="">${state.pantry[k]}</button>`).join('')}</div>`;
    el.classList.remove('hidden');
    const w = el.offsetWidth;
    el.style.left = Math.max(8, Math.min(W - w - 8, l.x + l.w / 2 - w / 2)) + 'px';
    el.style.top = (l.y + 40 - el.offsetHeight) + 'px';
    Sound.play('click');
  }
  function hideRestock() { restockShelf = -1; $('restockPop').classList.add('hidden'); }

  // ======================= SAVE / LOAD =======================
  let storageOK = true;
  try { const k = '__cst_test'; localStorage.setItem(k, '1'); localStorage.removeItem(k); } catch (e) { storageOK = false; }

  function readSlot(n) {
    if (!storageOK) return null;
    try { const raw = localStorage.getItem(SAVE_PREFIX + n); return raw ? JSON.parse(raw) : null; } catch (e) { return null; }
  }
  function makeThumb() {
    try {
      const c = document.createElement('canvas'); c.width = 192; c.height = 108;
      c.getContext('2d').drawImage(canvas, 0, 0, 192, 108);
      return c.toDataURL('image/jpeg', 0.7);
    } catch (e) { return null; }
  }
  function writeSlot(n) {
    if (!storageOK) { toast('Saving is not available in this browser.', 'bad'); return false; }
    const data = {
      meta: { shopName: state.shopName, day: state.day, money: state.money, rep: state.rep, phase: state.phase, savedAt: Date.now(), thumb: makeThumb() },
      state: JSON.parse(JSON.stringify(state)),
    };
    try { localStorage.setItem(SAVE_PREFIX + n, JSON.stringify(data)); }
    catch (e) {
      data.meta.thumb = null;
      try { localStorage.setItem(SAVE_PREFIX + n, JSON.stringify(data)); } catch (e2) { toast('Could not save — storage is full.', 'bad'); return false; }
    }
    Sound.play('save');
    toast(`Game saved to Slot ${n}!`, 'good');
    return true;
  }
  function deleteSlot(n) { try { localStorage.removeItem(SAVE_PREFIX + n); } catch (e) { /* ignore */ } }

  function loadSlot(n) {
    const data = readSlot(n);
    if (!data || !data.state) { toast('That save slot is empty.', 'bad'); return; }
    state = Object.assign(newState(data.state.shopName), data.state);
    state.pantry = Object.assign(newState('').pantry, data.state.pantry);
    state.upgrades = Object.assign(newState('').upgrades, data.state.upgrades);
    syncShelves();
    displayMoney = state.money;
    particles = []; speed = 1; lastHud = '';
    screen = 'game';
    closeAllModals();
    hideRestock();
    showGameUI();
    Sound.play('save');
    toast(`Loaded ${state.shopName} — Day ${state.day}`, 'good');
    Sound.setRush(state.phase === 'rush');
    refreshAll();
    if (state.phase === 'morning') showMorning();
    else if (state.phase === 'summary') showSummary();
    else if (state.phase === 'gameover') showGameOver();
    else if (state.phase === 'rush') showMenu(true);
  }

  let confirmKey = null;
  function showSaves(mode) {
    confirmKey = null;
    showModal(() => {
      const canSave = mode === 'save' && state && state.phase !== 'gameover';
      const slots = [];
      for (let n = 1; n <= SLOTS; n++) {
        const d = readSlot(n), m = d && d.meta;
        const confirmSave = confirmKey === 'save' + n, confirmDel = confirmKey === 'del' + n;
        slots.push(`<div class="slot ${m ? '' : 'empty'}">
          <div class="num">${n}</div>
          ${m && m.thumb ? `<img class="thumb" src="${m.thumb}" alt="">` : `<div class="thumb">${m ? 'Saved' : 'Empty'}</div>`}
          <div class="sinfo">
            <div class="stitle">${m ? esc(m.shopName) : 'Empty Slot'}</div>
            ${m ? `<div class="smeta">Day ${m.day} &middot; ${yen(m.money)} &middot; ${(m.rep || 0).toFixed(1)} stars${m.phase === 'rush' ? ' &middot; mid-rush' : ''}</div>
                   <div class="sdate">Saved ${new Date(m.savedAt).toLocaleString()}</div>` : '<div class="smeta">No game saved here yet.</div>'}
          </div>
          <div class="sbtns">
            ${canSave ? `<button class="btn btn-sm ${confirmSave ? 'btn-red' : 'btn-pink'}" data-action="slotSave" data-n="${n}">${confirmSave ? 'Overwrite?' : 'Save Here'}</button>` : ''}
            ${m ? `<button class="btn btn-sm btn-mint" data-action="slotLoad" data-n="${n}">Load</button>
                   <button class="btn btn-sm ${confirmDel ? 'btn-red' : 'btn-white'}" data-action="slotDel" data-n="${n}">${confirmDel ? 'Really delete?' : 'Delete'}</button>` : ''}
          </div>
        </div>`);
      }
      return `<div class="panel saves">
        <button class="close" data-action="close">&times;</button>
        <h2 class="purple">${canSave ? 'Save Game' : 'Load Game'}</h2>
        ${storageOK ? '' : '<p class="neg" style="text-align:center">Your browser is blocking storage, so saves cannot be kept.</p>'}
        ${state && screen === 'game' && state.phase === 'rush' ? '<p style="text-align:center;font-size:15px;color:var(--ink-soft)">The store is paused while this menu is open.</p>' : ''}
        <div class="slots">${slots.join('')}</div>
        <div class="row"><button class="btn btn-white" data-action="close">Back</button></div>
      </div>`;
    }, { kind: 'saves' });
  }

  // ======================= MENUS =======================
  function showMenu(fromLoad) {
    showModal(() => `<div class="panel" style="width:440px;align-items:stretch">
      <h2 class="purple">${fromLoad ? 'Ready?' : 'Paused'}</h2>
      ${fromLoad ? '<p style="text-align:center">Your game was saved during a rush. Press Resume when you are ready!</p>' : ''}
      <div style="display:flex;flex-direction:column;gap:12px;margin-top:6px">
        <button class="btn btn-pink btn-big" data-action="close">Resume</button>
        <button class="btn btn-mint" data-action="save">Save Game</button>
        <button class="btn btn-mint" data-action="loadMenu">Load Game</button>
        <button class="btn btn-purple" data-action="howto">How to Play</button>
        <button class="btn btn-yellow" data-action="settings">Settings</button>
        <button class="btn btn-white" data-action="quit">Quit to Title</button>
      </div>
    </div>`, { kind: 'menu' });
  }

  function showSettings() {
    showModal(() => {
      const s = Sound.settings;
      return `<div class="panel" style="width:520px">
        <button class="close" data-action="close">&times;</button>
        <h2 class="purple">Settings</h2>
        <div class="setting"><label>Music</label><input type="range" min="0" max="1" step="0.05" value="${s.musicVol}" data-input="musicVol"><button class="btn btn-sm ${s.music ? 'btn-mint' : 'btn-white'}" data-action="toggleMusic">${s.music ? 'On' : 'Off'}</button></div>
        <div class="setting"><label>Sounds</label><input type="range" min="0" max="1" step="0.05" value="${s.sfxVol}" data-input="sfxVol"><button class="btn btn-sm ${s.sfx ? 'btn-mint' : 'btn-white'}" data-action="toggleSfx">${s.sfx ? 'On' : 'Off'}</button></div>
        <p style="font-size:15px;color:var(--ink-soft);text-align:center">Keyboard: <b>Esc</b> = menu &middot; <b>M</b> = music &middot; <b>Space</b> = speed during a rush</p>
        <div class="row"><button class="btn btn-pink" data-action="close">Done</button></div>
      </div>`;
    });
  }

  function showHowTo() {
    showModal(() => `<div class="panel howto">
      <button class="close" data-action="close">&times;</button>
      <h2>How to Play</h2>
      <div class="scroll">
      <ol>
        <li><b>The Register:</b> You start with ¥1,000. Spend it wisely at the <b>Market</b> on Lollipops, Gummy Bears, Chocolate and more. Run out of money AND candy and it's Game Over!</li>
        <li><b>The Pantry:</b> Candy you buy goes into your backroom pantry. It only holds 50 items to start — if it's full, you can't buy more until you clear space.</li>
        <li><b>The Shop Floor:</b> Kids can only buy candy that's on your <b>display shelves</b>. Each shelf holds 10 items of one kind. Cheap lollipops sell fast — chocolate sells slower but makes way more profit. You decide!</li>
        <li><b>The Rush:</b> Press <b>Open Store</b>. Kids walk in with a thought bubble showing what they want, plus a patience ring. If your shelf has it, they buy it and you get paid. If they wait too long, they leave sad and your rating drops.</li>
        <li><b>Restock during the rush:</b> Click any shelf to refill it from your pantry. You can even switch it to a different candy!</li>
        <li><b>Every morning</b> brings a new event — heatwaves, recess rushes, wholesale sales and more. Read the card and plan ahead.</li>
        <li>Each night you pay shop rent. Buy <b>upgrades</b> at the Market to grow your store. Reach <b>${yen(WIN_MONEY)}</b> to become a Candy Tycoon!</li>
        <li><b>Save any time</b> with the save button — you have 3 save slots.</li>
      </ol>
      </div>
      <div class="row"><button class="btn btn-pink" data-action="close">Got it!</button></div>
    </div>`);
  }

  function showNewGame() {
    showModal(() => `<div class="panel" style="width:520px;text-align:center">
      <button class="close" data-action="close">&times;</button>
      <h2>Name Your Shop</h2>
      <p>Every great candy store needs a great name!</p>
      <input class="input" id="shopName" maxlength="22" value="Sweet Treats" autofocus>
      <div class="row">
        <button class="btn btn-yellow btn-sm" data-action="randomName">Random Name</button>
      </div>
      <div class="row"><button class="btn btn-pink btn-big" data-action="startGame">Start!</button></div>
    </div>`);
  }
  const NAMES_A = ['Sugar', 'Candy', 'Gumdrop', 'Lolly', 'Rainbow', 'Sprinkle', 'Bubble', 'Cocoa', 'Jelly', 'Fizzy', 'Taffy', 'Honey'];
  const NAMES_B = ['Shack', 'Palace', 'Corner', 'Castle', 'Emporium', 'Hut', 'Factory', 'Kingdom', 'Station', 'Cottage', 'Market', 'Island'];

  function showGameUI() {
    $('title').classList.add('hidden');
    $('hud').classList.remove('hidden');
    $('bottombar').classList.remove('hidden');
  }
  function showTitle() {
    screen = 'title'; state = null;
    closeAllModals(); hideRestock();
    Sound.setRush(false);
    $('title').classList.remove('hidden');
    $('hud').classList.add('hidden');
    $('bottombar').classList.add('hidden');
  }

  // ======================= INPUT =======================
  const actions = {
    newGame: showNewGame,
    randomName: () => { const i = $('shopName'); if (i) i.value = `${NAMES_A[(Math.random() * NAMES_A.length) | 0]} ${NAMES_B[(Math.random() * NAMES_B.length) | 0]}`; },
    startGame: () => { const n = ($('shopName') && $('shopName').value.trim()) || 'Sweet Treats'; closeAllModals(); startNewGame(n.slice(0, 22)); },
    loadMenu: () => showSaves('load'),
    save: () => { if (!state) return; showSaves('save'); },
    howto: showHowTo,
    settings: showSettings,
    close: closeModal,
    menu: () => { if (modalStack.length) return; showMenu(false); },
    market: () => { if (state.phase === 'prep') showMarket(); },
    shelves: () => { if (state.phase === 'prep') showShelves(); },
    toShelves: () => { closeModal(); showShelves(); },
    open: openStore,
    openFromShelves: () => { closeAllModals(); openStore(); },
    startPrep, nextDay,
    keepPlaying: () => { closeAllModals(); beginDay(); },
    speed: () => { speed = speed === 1 ? 2 : 1; updateBar(); },
    toggleMusic: () => { Sound.setMusic(!Sound.settings.music); updateBar(); refreshModal(); },
    toggleSfx: () => { Sound.setSfx(!Sound.settings.sfx); refreshModal(); },
    mtab: el => { marketTab = el.dataset.tab; refreshModal(); },
    buy: el => buy(el.dataset.type, el.dataset.n),
    upgrade: el => buyUpgrade(el.dataset.id),
    setType: el => setShelfType(+el.dataset.i, el.dataset.type),
    shelfAdd: el => shelfAdd(+el.dataset.i, el.dataset.n),
    fillAll,
    restock: el => beginRestock(+el.dataset.i, el.dataset.type),
    slotSave: el => {
      const n = +el.dataset.n;
      if (readSlot(n) && confirmKey !== 'save' + n) { confirmKey = 'save' + n; refreshModal(); return; }
      confirmKey = null;
      // capture thumbnail without the modal: canvas never contains DOM, so it is already clean
      if (writeSlot(n)) refreshModal();
    },
    slotLoad: el => loadSlot(+el.dataset.n),
    slotDel: el => {
      const n = +el.dataset.n;
      if (confirmKey !== 'del' + n) { confirmKey = 'del' + n; refreshModal(); return; }
      confirmKey = null; deleteSlot(n); toast(`Slot ${n} deleted.`, ''); refreshModal();
    },
    quit: () => {
      showModal(() => `<div class="panel" style="width:460px;text-align:center"><h2 class="dark">Quit?</h2><p>Any progress since your last save will be lost.</p>
        <div class="row"><button class="btn btn-white" data-action="close">Cancel</button><button class="btn btn-red" data-action="quitConfirmed">Quit to Title</button></div></div>`);
    },
    quitConfirmed: showTitle,
  };

  document.addEventListener('click', e => {
    Sound.unlock();
    const el = e.target.closest('[data-action]');
    if (el && !el.disabled) {
      const a = el.dataset.action;
      if (actions[a]) {
        if (!['buy', 'restock', 'shelfAdd', 'setType', 'upgrade', 'slotSave', 'slotLoad'].includes(a)) Sound.play('click');
        actions[a](el);
      }
      return;
    }
    if (!e.target.closest('#restockPop')) hideRestock();
  });
  document.addEventListener('input', e => {
    const k = e.target.dataset && e.target.dataset.input;
    if (k === 'musicVol') Sound.setMusicVol(+e.target.value);
    if (k === 'sfxVol') { Sound.setSfxVol(+e.target.value); }
  });
  document.addEventListener('change', e => { if (e.target.dataset && e.target.dataset.input === 'sfxVol') Sound.play('coin'); });
  document.addEventListener('keydown', e => {
    Sound.unlock();
    if (e.target.tagName === 'INPUT') { if (e.key === 'Enter' && $('shopName')) actions.startGame(); return; }
    if (e.key === 'Escape') {
      if (restockShelf >= 0) { hideRestock(); return; }
      const top = modalStack[modalStack.length - 1];
      if (top) { if (!['morning', 'summary', 'gameover'].includes(top.kind)) closeModal(); }
      else if (screen === 'game') showMenu(false);
    }
    if (e.key === 'm' || e.key === 'M') actions.toggleMusic();
    if (e.key === ' ' && screen === 'game' && state && state.phase === 'rush' && !modalStack.length) { e.preventDefault(); actions.speed(); }
  });

  function stagePoint(e) {
    const r = canvas.getBoundingClientRect();
    return { x: ((e.clientX - r.left) / r.width) * W, y: ((e.clientY - r.top) / r.height) * H };
  }
  function shelfAt(p) {
    if (!state) return -1;
    const L = Art.shelfLayout(state.shelves.length);
    return L.findIndex(l => p.x >= l.x && p.x <= l.x + l.w && p.y >= l.y && p.y <= l.y + l.h);
  }
  canvas.addEventListener('mousemove', e => {
    if (screen !== 'game' || modalStack.length) { hoverShelf = -1; canvas.classList.remove('pointer'); return; }
    const okPhase = state.phase === 'prep' || state.phase === 'rush';
    hoverShelf = okPhase ? shelfAt(stagePoint(e)) : -1;
    canvas.classList.toggle('pointer', hoverShelf >= 0);
  });
  canvas.addEventListener('mouseleave', () => { hoverShelf = -1; });
  canvas.addEventListener('click', e => {
    if (screen !== 'game' || modalStack.length) return;
    const i = shelfAt(stagePoint(e));
    if (i < 0) { hideRestock(); return; }
    e.stopPropagation();
    if (state.phase === 'rush') showRestock(i);
    else if (state.phase === 'prep') { Sound.play('click'); showShelves(); }
  });

  // ======================= RENDER =======================
  function updateParticles(dt) {
    for (const p of particles) {
      p.life -= dt;
      if (p.g) p.vy += p.g * dt;
      p.x += p.vx * dt; p.y += p.vy * dt;
    }
    particles = particles.filter(p => p.life > 0);
  }

  function drawParticles() {
    for (const p of particles) {
      const a = Math.min(1, p.life / p.max * 2);
      ctx.save(); ctx.globalAlpha = a;
      if (p.kind === 'text') Art.text(ctx, p.text, p.x, p.y, p.big ? 26 : 20, p.color, { stroke: '#fff', lw: 6 });
      else if (p.kind === 'coin') Art.coin(ctx, p.x, p.y, 9);
      else if (p.kind === 'heart') Art.heart(ctx, p.x, p.y, 16);
      else if (p.kind === 'spark') Art.star(ctx, p.x, p.y, 7 * a + 2, '#fff6a0', '#ffcf3a');
      else if (p.kind === 'storm') { Art.cloud(ctx, p.x - 26, p.y, 26, '#8c8ca8'); ctx.strokeStyle = '#ffd23f'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(p.x, p.y + 10); ctx.lineTo(p.x - 6, p.y + 22); ctx.lineTo(p.x + 3, p.y + 22); ctx.lineTo(p.x - 4, p.y + 36); ctx.stroke(); }
      ctx.restore();
    }
  }

  function renderShop() {
    const rush = state.phase === 'rush';
    Art.shopBackground(ctx, time, W, H, { shopName: state.shopName, doorOpen, storeOpen: rush });
    Art.awning(ctx, 66, time, W);
    const L = Art.shelfLayout(state.shelves.length), cap = shelfCap(), e = ev();
    state.shelves.forEach((s, i) => {
      const sm = (e.sellMult || {})[s.type] || e.sellAll;
      Art.shelf(ctx, L[i], s, cap, {
        product: PRODUCTS[s.type], price: priceOf(s.type), priceUp: sm && sm > 1, hover: hoverShelf === i, t: time, rush,
        hint: hoverShelf === i ? (rush ? 'Click to restock' : 'Click to stock') : null,
      });
    });
    Art.counter(ctx, time, W);
    if (state.rush) {
      const cs = state.rush.customers.slice().sort((a, b) => a.y - b.y);
      for (const c of cs) {
        Art.kid(ctx, c.look, c.x, c.y, { walking: c.walking, phase: c.phase, t: time, mood: c.mood, flip: c.flip, holding: c.holding, holdV: c.holdV });
      }
      for (const c of cs) {
        if (c.state === 'wait' || c.state === 'look' || (c.state === 'walk' && !c.holding)) {
          const frac = c.state === 'wait' ? Math.max(0, c.patience / c.maxPatience) : null;
          Art.bubble(ctx, c.x + 30, c.y - 158 * c.look.size, c.craving, frac, c.qty, c.alt, time + c.id);
        }
      }
    }
    drawParticles();
  }

  let last = performance.now();
  function frame(now) {
    const rdt = Math.min(0.05, (now - last) / 1000);
    last = now;
    time += rdt;
    ctx.setTransform(scale * dpr, 0, 0, scale * dpr, 0, 0);
    if (screen === 'title') {
      Art.titleScene(ctx, time, W, H, rdt);
    } else if (state) {
      if (state.phase === 'rush' && !isPaused()) {
        const dt = rdt * speed;
        updateRush(dt);
        updateParticles(dt);
      } else if (!isPaused()) updateParticles(rdt);
      doorOpen = Math.max(0, doorOpen - rdt * 1.5);
      renderShop();
      updateHUD();
    }
    // animated event art inside modal
    const ea = document.getElementById('eventArt');
    if (ea) {
      const ectx = ea.getContext('2d');
      ectx.setTransform(2, 0, 0, 2, 0, 0);
      Art.eventArt(ectx, ea.dataset.event || (state && state.event) || 'normal', ea.width / 2, ea.height / 2, time);
    }
    requestAnimationFrame(frame);
  }

  // ======================= BOOT =======================
  let booted = false;
  function boot() {
    if (booted) return; booted = true;
    for (const k of ORDER) icons[k] = Art.makeIcon(k, 128, 0);
    resize();
    requestAnimationFrame(frame);
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(boot, boot); else boot();
  // safety: if fonts never resolve (offline), boot anyway
  setTimeout(boot, 2500);

  // debug hook for testing
  window.__cst = { get state() { return state; }, startNewGame, openStore, actions, step: dt => { if (state && state.phase === 'rush') updateRush(dt); }, writeSlot, loadSlot, readSlot, get modals() { return modalStack.map(m => m.kind); } };
})();
