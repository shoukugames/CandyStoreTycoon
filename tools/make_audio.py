#!/usr/bin/env python3
"""Synthesise every sound in Candy Store Tycoon into assets/audio/.

Run this only when the sound design changes (needs numpy, and ffmpeg for the .ogg music).
All music is original and generated here: calm ambient loops built from warm pads, a music
box, a soft electric piano and a kalimba, with a long synthetic reverb. Each loop is seamless.
"""
import os
import shutil
import subprocess
import wave

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "audio")
RNG = np.random.default_rng(20261106)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def write_wav(path, data, rate, peak_level=0.89):
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        data = data[:, None]
    peak = np.max(np.abs(data)) or 1.0
    pcm = (data / peak * peak_level * 32767).astype("<i2")
    with wave.open(path, "wb") as handle:
        handle.setnchannels(pcm.shape[1])
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm.tobytes())
    return len(pcm) / rate


def save_sfx(name, data, rate=44100):
    secs = write_wav(os.path.join(OUT, name + ".wav"), data, rate, 0.8)
    print(f"{name}.wav: {secs:.2f}s")


def save_music(name, data, rate):
    wav = os.path.join(OUT, name + ".wav")
    secs = write_wav(wav, data, rate, 0.85)
    ogg = os.path.join(OUT, name + ".ogg")
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-c:a", "libvorbis", "-q:a", "5", ogg], check=True)
        os.remove(wav)
        print(f"{name}.ogg: {secs:.1f}s, {os.path.getsize(ogg) // 1024} KB")
    else:
        print(f"{name}.wav: {secs:.1f}s (install ffmpeg to make the smaller .ogg)")


# ---------------- DSP helpers ----------------

def lowpass(signal, rate, cutoff, order=4):
    spec = np.fft.rfft(signal, axis=0)
    freqs = np.fft.rfftfreq(signal.shape[0], 1 / rate)
    curve = 1 / (1 + (freqs / cutoff) ** order)
    if signal.ndim == 2:
        curve = curve[:, None]
    return np.fft.irfft(spec * curve, n=signal.shape[0], axis=0)


def circular_reverb(signal, rate, seconds=5.0, mix=0.5, seed=1):
    """Convolve with decaying noise, wrapping the tail so the loop stays seamless."""
    rng = np.random.default_rng(seed)
    n = signal.shape[0]
    out = np.zeros((n, 2))
    length = int(seconds * rate)
    t = np.arange(length) / rate
    for ch in range(2):
        ir = rng.standard_normal(length) * np.exp(-t * 6.9 / seconds)
        ir = lowpass(ir, rate, 3200)
        pre = int(0.02 * rate)
        ir[:pre] *= np.linspace(0, 1, pre)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(signal[:, ch], n) * np.fft.rfft(ir, n), n)
        out[:, ch] = signal[:, ch] * (1 - mix) + wet * mix * 1.5
    return out


def env_ad(n, rate, attack, decay):
    t = np.arange(n) / rate
    env = np.exp(-t * decay)
    a = max(1, int(attack * rate))
    env[:a] *= np.linspace(0, 1, a) ** 1.5
    return env


def fade_ends(n, rate, attack, release):
    env = np.ones(n)
    a = min(n, max(1, int(attack * rate)))
    r = min(n - a, max(1, int(release * rate)))
    env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    env[n - r:] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return env


def place(buf, sound, start, gain=1.0, pan=0.0):
    """Add a mono sound into a stereo loop buffer, wrapping around the end (seamless loops)."""
    n = buf.shape[0]
    left, right = gain * np.sqrt((1 - pan) / 2), gain * np.sqrt((1 + pan) / 2)
    start %= n
    pos = 0
    while pos < len(sound):
        chunk = min(len(sound) - pos, n - start)
        buf[start:start + chunk, 0] += sound[pos:pos + chunk] * left
        buf[start:start + chunk, 1] += sound[pos:pos + chunk] * right
        pos += chunk
        start = 0


# ---------------- instruments ----------------

def pad(m, seconds, rate, bright=0.8):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    out = np.zeros(n)
    for detune in (-0.08, 0.0, 0.07):
        f = midi_hz(m + detune)
        ph = RNG.uniform(0, 2 * np.pi)
        for h, amp in ((1, 1.0), (2, 0.38 * bright), (3, 0.16 * bright), (4, 0.07 * bright)):
            out += amp * np.sin(2 * np.pi * f * h * t + ph * h)
    breathe = 1 + 0.16 * np.sin(2 * np.pi * RNG.uniform(0.06, 0.12) * t + RNG.uniform(0, 6))
    return out * breathe * fade_ends(n, rate, seconds * 0.4, seconds * 0.45) / 3


def music_box(m, rate, seconds=3.5):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m)
    s = (np.sin(2 * np.pi * f * t) + 0.28 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
         + 0.12 * np.sin(2 * np.pi * f * 4.17 * t) * np.exp(-t * 9) + 0.05 * np.sin(2 * np.pi * f * 6.3 * t) * np.exp(-t * 14))
    return s * env_ad(n, rate, 0.004, 1.6)


def epiano(m, rate, seconds=4.0):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m)
    s = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t * 3))
    s += 0.2 * np.sin(2 * np.pi * f * 7 * t) * np.exp(-t * 25)
    s *= 1 + 0.12 * np.sin(2 * np.pi * 4.2 * t)
    return s * env_ad(n, rate, 0.006, 0.9)


def kalimba(m, rate, seconds=2.2):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * f * 5.95 * t) * np.exp(-t * 18)
    s += 0.1 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 6)
    return s * env_ad(n, rate, 0.002, 2.6)


def soft_bass(m, seconds, rate):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return s * fade_ends(n, rate, 0.4, seconds * 0.5)


def chord_tones(chord, low, high):
    notes = []
    for m in chord:
        for octave in range(-24, 37, 12):
            if low <= m + octave <= high:
                notes.append(m + octave)
    return sorted(set(notes))


# ---------------- the three ambient tracks ----------------

def track(rate, chords, bass, chord_s, seed, lead, lead_pattern, comp=None, verb=5.5, bright=0.8, noise=0.006):
    global RNG
    RNG = np.random.default_rng(seed)
    n = int(len(chords) * chord_s * rate)
    buf = np.zeros((n, 2))
    overlap = 3.0
    for i, chord in enumerate(chords):
        start = int((i * chord_s - overlap / 2) * rate)
        for j, m in enumerate(chord):
            place(buf, pad(m, chord_s + overlap, rate, bright), start, 0.12, (j / max(1, len(chord) - 1)) * 1.1 - 0.55)
        place(buf, soft_bass(bass[i], chord_s + overlap, rate), start, 0.2, 0.0)
        tones = chord_tones(chord, 67, 91)
        for beat, step, vel in lead_pattern(i, chord_s):
            note = tones[step % len(tones)] if step >= 0 else None
            if note:
                place(buf, lead(note, rate), int((i * chord_s + beat) * rate), vel, RNG.uniform(-0.5, 0.5))
        if comp:
            comp(buf, i, chord, chord_s, rate)
    bed = lowpass(RNG.standard_normal((n, 2)), rate, 380)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / n * 2)[:, None]
    buf += bed * noise * swell
    buf = lowpass(buf, rate, 4800)
    return circular_reverb(buf, rate, verb, 0.52, seed)


def music():
    rate = 32000

    # Title, "Sugar Clouds": F major colours, music box over warm pads
    chords = [[53, 57, 60, 64], [50, 53, 57, 60, 64], [58, 62, 65, 69], [48, 55, 60, 62, 64],
              [53, 57, 60, 64, 67], [57, 60, 64, 67], [58, 62, 65, 69, 72], [55, 60, 62, 65]]
    bass = [41, 38, 34, 36, 41, 33, 34, 36]
    phrases = [[(0.0, 4, 0.11), (1.5, 3, 0.08), (3.0, 5, 0.1), (4.5, 2, 0.07)],
               [(0.0, 3, 0.1), (0.75, 4, 0.07), (2.25, 6, 0.1), (4.5, 5, 0.08)],
               [(0.0, 5, 0.1), (1.5, 4, 0.08), (3.0, 3, 0.09), (3.75, 2, 0.06)],
               [(0.0, 2, 0.09), (2.25, 4, 0.1), (4.5, 6, 0.08)]]

    def title_lead(i, s):
        return phrases[i % 4]
    save_music("bgm_title", track(rate, chords, bass, 6.0, 11, music_box, title_lead), rate)

    # Shop prep, "Morning Pantry": D major, slow electric piano and sparse kalimba
    chords = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66, 69], [57, 61, 64, 69],
              [62, 66, 69, 76], [54, 57, 61, 64], [55, 59, 62, 66], [57, 61, 64, 67]]
    bass = [38, 35, 31, 33, 38, 30, 31, 33]

    def shop_lead(i, s):
        return [(0.5, 3 + i % 3, 0.09), (3.0, 5 - i % 2, 0.07), (5.25, 2 + i % 4, 0.08)]

    def shop_comp(buf, i, chord, s, r):
        for j, m in enumerate(sorted(chord)[:4]):
            place(buf, epiano(m + 12 if m < 60 else m, r), int((i * s + 0.02 * j) * r), 0.05, 0.3 * (j - 1.5) / 1.5)
            place(buf, epiano(m + 12 if m < 60 else m, r), int((i * s + s / 2 + 0.03 * j) * r), 0.035, 0.3 * (j - 1.5) / 1.5)
    save_music("bgm_shop", track(rate, chords, bass, 7.0, 23, kalimba, shop_lead, shop_comp, bright=0.6), rate)

    # Store open, "Sweet Afternoon": still relaxed, a gentle kalimba ostinato keeps time
    bpm = 84
    eighth = 60 / bpm / 2
    chord_s = eighth * 16
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65],
              [57, 60, 64, 71], [53, 57, 60, 64, 67], [50, 53, 57, 60], [52, 55, 59, 62]]
    bass = [45, 41, 36, 43, 45, 41, 38, 40]
    ost = [0, 2, 1, 3, 2, 4, 3, 1, 0, 2, 1, 3, 5, 4, 3, 2]

    def rush_lead(i, s):
        return [(k * eighth, ost[k] + (i % 2), 0.055 if k % 4 else 0.075) for k in range(16)]

    def rush_comp(buf, i, chord, s, r):
        top = chord_tones(chord, 74, 93)
        for k, beat in enumerate((2, 7, 10, 13)):
            if (i + k) % 2 == 0:
                place(buf, music_box(top[(i + k * 2) % len(top)], r), int((i * s + beat * eighth) * r), 0.05,
                      0.5 if k % 2 else -0.5)
    save_music("bgm_rush", track(rate, chords, bass, chord_s, 37, kalimba, rush_lead, rush_comp, verb=4.0, bright=0.7), rate)


# ---------------- sound effects ----------------

def effects():
    rate = 44100

    def tone(freq, seconds, kind="sine", decay=8.0, attack=0.003):
        n = int(seconds * rate)
        t = np.arange(n) / rate
        f = np.asarray(freq) if np.ndim(freq) else np.full(n, float(freq))
        ph = 2 * np.pi * np.cumsum(f) / rate
        if kind == "sine":
            s = np.sin(ph)
        elif kind == "tri":
            s = 2 / np.pi * np.arcsin(np.sin(ph))
        elif kind == "bell":
            s = np.sin(ph) + 0.3 * np.sin(2.76 * ph) * np.exp(-t * 5) + 0.12 * np.sin(5.4 * ph) * np.exp(-t * 9)
        else:
            s = np.sin(ph) + 0.25 * np.sin(2 * ph)
        return s * env_ad(n, rate, attack, decay)

    def sil(s):
        return np.zeros(int(s * rate))

    def at(s, x):
        return np.concatenate([sil(s), x])

    def mix(*xs):
        n = max(len(x) for x in xs)
        out = np.zeros(n)
        for x in xs:
            out[:len(x)] += x
        return out

    def stereo(mono, verb=0.25, tail=0.6, seed=5):
        pad_ = np.concatenate([mono, sil(tail)])
        rng = np.random.default_rng(seed)
        length = int(0.6 * rate)
        t = np.arange(length) / rate
        out = np.zeros((len(pad_), 2))
        for ch in range(2):
            ir = rng.standard_normal(length) * np.exp(-t * 9)
            ir /= np.sqrt(np.sum(ir ** 2))
            wet = np.convolve(pad_, ir)[:len(pad_)]
            out[:, ch] = pad_ * (1 - verb) + wet * verb
        return out

    hz = midi_hz
    save_sfx("click", stereo(mix(tone(1100, 0.05, "sine", 70) * 0.6, tone(2200, 0.03, "sine", 120) * 0.2), 0.08, 0.15))
    save_sfx("hover", tone(1900, 0.03, "sine", 140) * 0.25)
    pop = tone(np.linspace(420, 980, int(0.11 * rate)), 0.11, "sine", 22)
    save_sfx("pop", stereo(pop, 0.15, 0.3))
    save_sfx("coin", stereo(mix(tone(hz(88), 0.5, "bell", 9), at(0.07, tone(hz(95), 0.7, "bell", 7)),
                                at(0.07, tone(hz(100), 0.5, "sine", 14) * 0.25)), 0.3))
    save_sfx("restock", stereo(mix(*[at(i * 0.055, tone(hz(m), 0.5, "bell", 9) * 0.7) for i, m in enumerate([76, 79, 83, 88])]), 0.35))
    save_sfx("sad", stereo(mix(*[at(i * 0.2, tone(hz(m), 0.6, "tri", 4.5) * 0.7) for i, m in enumerate([67, 65, 64, 60])]), 0.35))
    save_sfx("door", stereo(mix(tone(hz(91), 1.4, "bell", 3.2) * 0.6, at(0.11, tone(hz(86), 1.4, "bell", 3.2) * 0.5)), 0.4, 1.0))
    save_sfx("error", stereo(np.concatenate([tone(330, 0.14, "tri", 9), tone(262, 0.24, "tri", 7)]) * 0.7, 0.2))
    save_sfx("morning", stereo(mix(*[at(i * 0.16, tone(hz(m), 1.6, "bell", 2.6) * 0.6) for i, m in enumerate([72, 76, 79, 84, 88])],
                                   at(0.1, tone(hz(60), 2.0, "sine", 1.5) * 0.3)), 0.45, 1.2))
    save_sfx("day_end", stereo(mix(*[at(i * 0.22, tone(hz(m), 1.8, "bell", 2.2) * 0.55) for i, m in enumerate([79, 76, 72, 67, 72])],
                                   at(0.0, tone(hz(48), 2.4, "sine", 1.2) * 0.3)), 0.45, 1.2))
    save_sfx("win", stereo(mix(*[at(i * 0.12, tone(hz(m), 1.8, "bell", 2.4) * 0.55) for i, m in enumerate([72, 76, 79, 84, 88, 91, 96])],
                               at(0.2, tone(hz(48), 2.6, "sine", 1.0) * 0.35)), 0.45, 1.4))
    save_sfx("save", stereo(mix(*[at(i * 0.08, tone(hz(m), 0.6, "sine", 8) * 0.6) for i, m in enumerate([79, 84, 91])]), 0.3))
    shh = lowpass(np.random.default_rng(9).standard_normal(int(0.6 * rate)), rate, 1600)
    shh *= np.sin(np.linspace(0, np.pi, len(shh))) ** 2
    save_sfx("whoosh", stereo(shh * 0.5, 0.3))
    save_sfx("upgrade", stereo(mix(*[at(i * 0.07, tone(hz(m), 0.9, "bell", 4) * 0.6) for i, m in enumerate([72, 79, 84, 91])]), 0.4))
    save_sfx("unlock", stereo(mix(tone(hz(84), 1.0, "bell", 4), at(0.1, tone(hz(91), 1.2, "bell", 3.5))) * 0.6, 0.4))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    effects()
    music()
