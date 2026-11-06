/* Candy Store Tycoon — procedural music + sound effects (Web Audio API, no files needed) */
const Sound = (() => {
  const SETTINGS_KEY = 'candyStoreTycoon.settings';
  let ac = null, master, musicBus, sfxBus, noiseBuf;
  let settings = { music: true, sfx: true, musicVol: 0.55, sfxVol: 0.75 };
  let timerId = null, nextTime = 0, step = 0, tempo = 128, rush = false;

  try { Object.assign(settings, JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}')); } catch (e) { /* storage blocked */ }
  const persist = () => { try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch (e) { /* ignore */ } };

  function ensure() {
    if (ac) { if (ac.state === 'suspended') ac.resume(); return true; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return false;
    ac = new AC();
    master = ac.createGain();
    master.gain.value = 0.9;
    const comp = ac.createDynamicsCompressor();
    comp.threshold.value = -14; comp.ratio.value = 4;
    master.connect(comp); comp.connect(ac.destination);
    musicBus = ac.createGain(); sfxBus = ac.createGain();
    musicBus.connect(master); sfxBus.connect(master);
    applyVolumes();
    noiseBuf = ac.createBuffer(1, ac.sampleRate, ac.sampleRate);
    const d = noiseBuf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    return true;
  }

  function applyVolumes() {
    if (!ac) return;
    musicBus.gain.setTargetAtTime(settings.music ? settings.musicVol * 0.8 : 0, ac.currentTime, 0.05);
    sfxBus.gain.setTargetAtTime(settings.sfx ? settings.sfxVol : 0, ac.currentTime, 0.02);
  }

  const mtof = m => 440 * Math.pow(2, (m - 69) / 12);

  function tone(dest, freq, t, dur, o = {}) {
    const type = o.type || 'square', vol = o.vol ?? 0.2, attack = o.attack ?? 0.006;
    const release = o.release ?? 0.08, sustain = o.sustain ?? 0.6;
    const osc = ac.createOscillator();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (o.slideTo) osc.frequency.exponentialRampToValueAtTime(o.slideTo, t + dur);
    if (o.detune) osc.detune.value = o.detune;
    const g = ac.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + attack);
    g.gain.exponentialRampToValueAtTime(Math.max(0.0002, vol * sustain), t + Math.max(attack + 0.01, dur));
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur + release);
    let node = osc;
    if (o.filter) {
      const f = ac.createBiquadFilter();
      f.type = 'lowpass'; f.frequency.value = o.filter; f.Q.value = o.q || 0.7;
      osc.connect(f); node = f;
    }
    node.connect(g); g.connect(dest);
    if (o.vibrato) {
      const lfo = ac.createOscillator(), lg = ac.createGain();
      lfo.frequency.value = 6;
      lg.gain.setValueAtTime(0, t);
      lg.gain.linearRampToValueAtTime(freq * 0.012, t + Math.min(0.2, dur));
      lfo.connect(lg); lg.connect(osc.frequency);
      lfo.start(t); lfo.stop(t + dur + release + 0.05);
    }
    osc.start(t); osc.stop(t + dur + release + 0.05);
  }

  function noise(dest, t, dur, o = {}) {
    const src = ac.createBufferSource();
    src.buffer = noiseBuf;
    const f = ac.createBiquadFilter();
    f.type = o.ftype || 'highpass'; f.frequency.value = o.freq || 6000; f.Q.value = o.q || 0.8;
    const g = ac.createGain();
    g.gain.setValueAtTime(o.vol ?? 0.1, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(f); f.connect(g); g.connect(dest);
    src.start(t, Math.random() * 0.5); src.stop(t + dur + 0.02);
  }

  function kick(t) {
    const o = ac.createOscillator(), g = ac.createGain();
    o.type = 'sine';
    o.frequency.setValueAtTime(160, t);
    o.frequency.exponentialRampToValueAtTime(42, t + 0.13);
    g.gain.setValueAtTime(0.75, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.22);
    o.connect(g); g.connect(musicBus);
    o.start(t); o.stop(t + 0.25);
  }
  function snare(t, v = 1) {
    noise(musicBus, t, 0.14, { ftype: 'bandpass', freq: 1900, q: 0.6, vol: 0.22 * v });
    tone(musicBus, 200, t, 0.05, { type: 'triangle', vol: 0.18 * v, sustain: 0.1, release: 0.04 });
  }
  function hat(t, v) { noise(musicBus, t, 0.035, { freq: 7500, vol: v }); }

  // ---------- The tune: bright, bouncy, C major, 16 bars, 8th-note grid ----------
  // -1 = hold previous note, 0 = rest
  const MEL = [
    [64, 67, 72, 67, 64, -1, 67, -1],   // C
    [69, -1, 72, 69, 64, -1, 69, -1],   // Am
    [65, 69, 72, 69, 65, 69, 67, 65],   // F
    [62, -1, 67, -1, 71, 69, 67, -1],   // G
    [64, 67, 72, 76, 74, 72, 67, -1],   // C
    [69, 72, 76, 72, 69, -1, 64, -1],   // Am
    [65, -1, 69, 72, 74, 72, 69, 65],   // F
    [67, -1, 71, -1, 74, -1, -1, 0],    // G
    [72, -1, 69, -1, 65, -1, 69, 72],   // F
    [74, -1, 71, -1, 67, -1, 71, 74],   // G
    [76, 74, 71, 67, 64, 67, 71, 74],   // Em
    [72, -1, -1, 69, 72, 76, -1, -1],   // Am
    [77, 76, 74, 72, 69, 72, 74, -1],   // F
    [74, 72, 71, 69, 67, 69, 71, 74],   // G
    [72, -1, 67, -1, 64, 67, 72, 76],   // C
    [79, -1, 76, -1, 72, -1, 0, 0],     // C
  ];
  const CH = [[48, 0], [45, 1], [41, 0], [43, 0], [48, 0], [45, 1], [41, 0], [43, 2],
              [41, 0], [43, 0], [40, 1], [45, 1], [41, 0], [43, 2], [48, 0], [48, 0]];
  const QUAL = [[0, 4, 7], [0, 3, 7], [0, 4, 10]];
  const BASS = [0, null, 12, null, 0, 7, 12, null];

  function chordNotes(bar) {
    const [root, q] = CH[bar];
    return QUAL[q].map(iv => { let n = root + 12 + iv; while (n < 55) n += 12; while (n > 70) n -= 12; return n; });
  }

  function scheduleStep(s, t) {
    const bar = Math.floor(s / 8) % 16, i = s % 8;
    const spb = 60 / tempo / 2;
    // lead melody
    const m = MEL[bar][i];
    if (m > 0) {
      let len = 1;
      while (i + len < 8 && MEL[bar][i + len] === -1) len++;
      const d = len * spb * 0.92;
      tone(musicBus, mtof(m), t, d, { type: 'square', vol: 0.075, sustain: 0.55, release: 0.07, vibrato: len > 1, filter: 3800 });
      tone(musicBus, mtof(m + 12), t, d * 0.7, { type: 'triangle', vol: 0.03, sustain: 0.3, release: 0.05 });
    }
    // bass
    const bo = BASS[i];
    if (bo !== null) {
      const f = mtof(CH[bar][0] + bo);
      tone(musicBus, f, t, spb * 0.85, { type: 'triangle', vol: 0.28, sustain: 0.5, release: 0.04 });
      tone(musicBus, f, t, spb * 0.6, { type: 'sawtooth', vol: 0.05, sustain: 0.3, release: 0.03, filter: 700 });
    }
    // offbeat chord stabs
    if (i % 2 === 1) {
      for (const n of chordNotes(bar)) tone(musicBus, mtof(n), t, spb * 0.45, { type: 'square', vol: 0.022, sustain: 0.12, release: 0.05, filter: 2200 });
    }
    // drums
    if (i === 0 || i === 4 || (bar % 2 === 1 && i === 5)) kick(t);
    if (i === 2 || i === 6) snare(t);
    if ((bar === 7 || bar === 15) && i >= 5) snare(t + spb / 2, 0.6);
    hat(t, i % 2 ? 0.05 : 0.025);
    if (rush) {
      hat(t + spb / 2, 0.02);
      const cn = chordNotes(bar);
      tone(musicBus, mtof(cn[i % 3] + 24), t, spb * 0.4, { type: 'triangle', vol: 0.028, sustain: 0.1, release: 0.06 });
    }
  }

  function tick() {
    if (!ac) return;
    while (nextTime < ac.currentTime + 0.15) {
      if (settings.music) scheduleStep(step, nextTime);
      nextTime += 60 / tempo / 2;
      step = (step + 1) % 128;
    }
  }

  function startMusic() {
    if (!ensure()) return;
    if (timerId) return;
    nextTime = ac.currentTime + 0.1; step = 0;
    timerId = setInterval(tick, 25);
  }

  function setRush(on) { rush = on; tempo = on ? 142 : 128; }

  // ---------- Sound effects ----------
  const sfx = {
    click() { const t = ac.currentTime; tone(sfxBus, 880, t, 0.04, { type: 'square', vol: 0.08, sustain: 0.2, release: 0.03, filter: 3000 }); },
    pop() { const t = ac.currentTime; tone(sfxBus, 500, t, 0.08, { type: 'sine', vol: 0.3, slideTo: 1100, sustain: 0.3, release: 0.05 }); },
    coin() {
      const t = ac.currentTime;
      tone(sfxBus, mtof(83), t, 0.07, { type: 'square', vol: 0.12, sustain: 0.6, release: 0.02, filter: 5000 });
      tone(sfxBus, mtof(88), t + 0.07, 0.22, { type: 'square', vol: 0.12, sustain: 0.4, release: 0.12, filter: 5000 });
    },
    sad() {
      const t = ac.currentTime;
      [67, 66, 65, 62].forEach((n, k) => tone(sfxBus, mtof(n), t + k * 0.16, k === 3 ? 0.4 : 0.14, { type: 'triangle', vol: 0.22, sustain: 0.6, vibrato: k === 3 }));
    },
    restock() {
      const t = ac.currentTime;
      [72, 76, 79, 84].forEach((n, k) => tone(sfxBus, mtof(n), t + k * 0.05, 0.08, { type: 'triangle', vol: 0.2, sustain: 0.4 }));
    },
    error() { const t = ac.currentTime; tone(sfxBus, 220, t, 0.12, { type: 'square', vol: 0.1, sustain: 0.6, filter: 1200 }); tone(sfxBus, 180, t + 0.12, 0.18, { type: 'square', vol: 0.1, sustain: 0.6, filter: 1200 }); },
    fanfare() {
      const t = ac.currentTime;
      [[60, 0], [64, 0.12], [67, 0.24], [72, 0.36], [67, 0.6], [72, 0.72]].forEach(([n, d], k) =>
        tone(sfxBus, mtof(n + 12), t + d, k >= 4 ? 0.35 : 0.11, { type: 'square', vol: 0.1, sustain: 0.6, filter: 4000, vibrato: k === 5 }));
    },
    bell() { const t = ac.currentTime; tone(sfxBus, 1568, t, 0.5, { type: 'sine', vol: 0.12, sustain: 0.1, release: 0.4 }); tone(sfxBus, 2093, t + 0.08, 0.5, { type: 'sine', vol: 0.09, sustain: 0.1, release: 0.4 }); },
    whoosh() { const t = ac.currentTime; noise(sfxBus, t, 0.3, { ftype: 'bandpass', freq: 1200, q: 1.5, vol: 0.2 }); },
    save() { const t = ac.currentTime; [76, 79, 84].forEach((n, k) => tone(sfxBus, mtof(n), t + k * 0.08, 0.12, { type: 'sine', vol: 0.25, sustain: 0.5 })); },
    win() {
      const t = ac.currentTime;
      [72, 76, 79, 84, 79, 84, 88].forEach((n, k) => tone(sfxBus, mtof(n), t + k * 0.13, k === 6 ? 0.7 : 0.12, { type: 'square', vol: 0.1, sustain: 0.6, filter: 4500, vibrato: k === 6 }));
    },
  };

  function play(name) {
    if (!settings.sfx || !ensure()) return;
    try { sfx[name] && sfx[name](); } catch (e) { /* ignore audio glitches */ }
  }

  return {
    unlock() { if (ensure()) startMusic(); },
    play, setRush,
    get settings() { return settings; },
    setMusic(on) { settings.music = on; applyVolumes(); persist(); },
    setSfx(on) { settings.sfx = on; applyVolumes(); persist(); },
    setMusicVol(v) { settings.musicVol = v; applyVolumes(); persist(); },
    setSfxVol(v) { settings.sfxVol = v; applyVolumes(); persist(); },
  };
})();
