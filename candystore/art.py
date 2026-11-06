"""All game art, drawn in code: candy, kids, the shop, shelves, event pictures, title scene.

Sprites are drawn supersampled with gfx.Pen and cached, so the art stays smooth and fast.
"""
import math
import random
from collections import OrderedDict
from functools import lru_cache

import pygame

from . import gfx, i18n
from .gfx import Pen, darken, hexrgb, lighten, sprite
from .model import FLOOR_Y, H, PRODUCTS, W

TAU = math.tau

# ======================= CANDY =======================
LOLLI = [((255, 79, 154), (255, 214, 234)), ((122, 92, 255), (230, 222, 255)),
         ((31, 196, 163), (214, 255, 245)), ((255, 138, 31), (255, 241, 196))]
GUMMY = [(255, 59, 59), (255, 176, 0), (51, 201, 74), (255, 122, 26), (184, 75, 255)]
ICE = [((255, 77, 109), (255, 165, 61), (255, 225, 77)), ((47, 168, 255), (95, 211, 255), (180, 240, 255)),
       ((255, 112, 196), (255, 179, 225), (255, 240, 250))]
JAW = [((255, 79, 154), (255, 210, 63), (34, 201, 168), (122, 92, 255)),
       ((255, 122, 26), (255, 255, 255), (47, 168, 255), (255, 79, 154))]


def _clip_circle(layer, k, cx, cy, r):
    mask = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (int(cx * k), int(cy * k)), int(r * k))
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def _gloss(p, x, y, rx, ry, a=0.6):
    p.overlay(lambda q: q.ellipse((255, 255, 255), x, y, rx, ry), a)


def _lolli(p, v):
    c1, c2 = LOLLI[v % len(LOLLI)]
    r, cy = 31, 33
    p.rect((216, 200, 187), 45.5, cy, 9, 66, 4)
    p.rect((255, 250, 242), 47, cy, 6, 64.5, 3)
    p.circle(darken(c1, 0.3), 50, cy, r + 2.6)
    p.circle(c1, 50, cy, r)
    turns = TAU * 2.3
    a = 0.0
    while a <= turns:
        rad = (r - 5.5) * a / turns
        p.circle(c2, 50 + math.cos(a) * rad, cy + math.sin(a) * rad, 4.6)
        a += 0.05
    shade = pygame.Surface(p.s.get_size(), pygame.SRCALPHA)
    q = Pen(shade, p.k)
    q.circle((90, 0, 50, 70), 50, cy, r)
    q.circle((0, 0, 0, 0), 46, cy - 4, r - 3)
    p.s.blit(shade, (0, 0))
    _gloss(p, 39, cy - 13, 8, 4.5, 0.75)


def _gummy(p, v):
    c = GUMMY[v % len(GUMMY)]
    parts = [(50, 28, 17), (37, 14, 7.5), (63, 14, 7.5), (31, 50, 8), (69, 50, 8), (38, 80, 9.5), (62, 80, 9.5)]
    dark = darken(c, 0.38)
    for x, y, r in parts:
        p.circle(dark, x, y, r + 2.4)
    p.ellipse(dark, 50, 60, 23.4, 26.4)
    for x, y, r in parts:
        p.circle(c, x, y, r)
    p.ellipse(c, 50, 60, 21, 24)
    p.overlay(lambda q: (q.ellipse(darken(c, 0.25), 56, 66, 17, 20)), 0.35)
    p.ellipse(lighten(c, 0.3), 50, 62, 11, 13)
    p.ellipse(lighten(c, 0.45), 50, 33, 7, 5)
    p.circle(darken(c, 0.55), 44, 25, 2.3)
    p.circle(darken(c, 0.55), 56, 25, 2.3)
    p.circle(darken(c, 0.55), 50, 32, 2)
    _gloss(p, 42, 20, 5, 3, 0.8)
    _gloss(p, 39, 52, 3, 8, 0.5)


def _choc(p, v):
    x0, y0, w, h = 25, 7, 50, 86
    wc = ((47, 123, 255), (23, 75, 191)) if v % 2 else ((232, 40, 60), (163, 16, 31))
    p.rect((40, 14, 4), x0 - 2, y0 - 2, w + 4, h + 4, 7)
    p.rect((90, 46, 23), x0, y0, w, h, 5)
    cw, chh = 19, 15.5
    for i in range(2):
        for j in range(2):
            bx, by = x0 + 4 + i * (cw + 4), y0 + 4 + j * (chh + 3)
            p.rect((138, 74, 38), bx, by, cw, chh, 3)
            p.rect((180, 112, 70), bx + 2, by + 1.5, cw - 4, 2.5, 1)
    wy = y0 + h * 0.42
    teeth = [(x0, wy + 6)]
    for t in range(7):
        teeth.append((x0 + w * t / 6, wy + (0 if t % 2 else 6)))
    teeth += [(x0 + w, y0 + h - 5), (x0, y0 + h - 5)]
    p.poly((231, 233, 242), teeth)
    p.rect(wc[0], x0, wy + 8, w, y0 + h - wy - 8, 5)
    p.rect(wc[1], x0 + w * 0.68, wy + 8, w * 0.32, y0 + h - wy - 8, 5)
    p.rect(wc[1], x0 + w * 0.68, wy + 8, 6, y0 + h - wy - 8)
    p.rect((255, 246, 216), x0 + 5, wy + 17, w - 10, 16, 4)
    p.rect(wc[0], x0 + 9, wy + 22, w - 18, 2.5)
    p.rect(wc[0], x0 + 12, wy + 27, w - 24, 2)
    p.rect((255, 211, 77), x0, wy + 40, w, 3)
    _gloss(p, x0 + 6, wy + 30, 2.5, 13, 0.45)


def _ice(p, v):
    cs = ICE[v % len(ICE)]
    p.rect((182, 133, 69), 44, 54, 12, 44, 6)
    p.rect((232, 185, 121), 45.5, 55, 9, 41, 4.5)
    bx, by, bw, bh = 31, 4, 38, 60
    p.rect(darken(cs[0], 0.35), bx - 2.4, by - 2.4, bw + 4.8, bh + 4.8, 21)
    surf = p.s
    k = p.k

    def P(x, y):
        return int(x * k), int(y * k)
    pygame.draw.rect(surf, cs[0], (*P(bx, by), int(bw * k), int(bh / 3 * k) + 2),
                     border_top_left_radius=int(19 * k), border_top_right_radius=int(19 * k))
    pygame.draw.rect(surf, cs[1], (*P(bx, by + bh / 3), int(bw * k), int(bh / 3 * k) + 2))
    pygame.draw.rect(surf, cs[2], (*P(bx, by + 2 * bh / 3), int(bw * k), int(bh / 3 * k)),
                     border_bottom_left_radius=int(4 * k), border_bottom_right_radius=int(4 * k))
    p.overlay(lambda q: q.rect((255, 255, 255), bx + 5, by + 12, 6, bh - 18, 3), 0.45)
    p.overlay(lambda q: q.rect((0, 0, 50), bx + bw - 7, by + 14, 7, bh - 14), 0.12)
    p.ellipse(cs[2], bx + 28, by + bh + 2, 3, 4.5)


def _jaw(p, v):
    pal = JAW[v % 2]
    r, cx, cy = 32, 50, 50
    p.circle((70, 20, 60), cx, cy, r + 2.4)
    layer = pygame.Surface(p.s.get_size(), pygame.SRCALPHA)
    q = Pen(layer, p.k)
    q.circle(pal[0], cx, cy, r)
    ang = 0.6 + v
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(-5, 6):
        off = i * r * 0.32
        pts = []
        for dx, dy in ((off - 5, -50), (off + 5, -50), (off + 5, 50), (off - 5, 50)):
            pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
        q.poly(pal[(i + 8) % 4], pts)
    _clip_circle(layer, p.k, cx, cy, r)
    shade = pygame.Surface(p.s.get_size(), pygame.SRCALPHA)
    z = Pen(shade, p.k)
    z.circle((60, 0, 60, 90), cx, cy, r)
    z.circle((0, 0, 0, 0), cx - 4, cy - 4, r - 4)
    layer.blit(shade, (0, 0))
    _clip_circle(layer, p.k, cx, cy, r)
    p.s.blit(layer, (0, 0))
    _gloss(p, cx - 11, cy - 13, 9, 5, 0.8)


def _cotton(p, v):
    cone = [(33, 52), (67, 52), (50, 99)]
    p.poly((201, 184, 160), [(31, 51), (69, 51), (50, 101)])
    layer = pygame.Surface(p.s.get_size(), pygame.SRCALPHA)
    q = Pen(layer, p.k)
    q.poly((255, 250, 240), cone)
    for i in range(-3, 6):
        q.line((95, 184, 255), (20, 52 + i * 11), (80, 52 + i * 11 + 18), 5)
    mask = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    Pen(mask, p.k).poly((255, 255, 255, 255), cone)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    p.s.blit(layer, (0, 0))
    base = (143, 211, 255) if v % 2 else (255, 154, 213)
    blobs = [(36, 44, 14), (64, 44, 14), (50, 32, 17), (42, 20, 12), (60, 20, 12), (50, 48, 15), (32, 30, 10),
             (68, 30, 10)]
    for x, y, r in blobs:
        p.circle(darken(base, 0.15), x, y + 2, r)
    for x, y, r in blobs:
        p.circle(base, x, y, r)
    for x, y, r in blobs:
        p.circle(lighten(base, 0.45), x - r * 0.3, y - r * 0.3, r * 0.4)


_CANDY = {"lolli": _lolli, "gummy": _gummy, "choc": _choc, "ice": _ice, "jaw": _jaw, "cotton": _cotton}


@lru_cache(maxsize=512)
def candy(kind, size, variant=0):
    size = max(4, int(size))
    k = gfx.SS * size / 100
    big = pygame.Surface((int(100 * k), int(100 * k)), pygame.SRCALPHA)
    _CANDY[kind](Pen(big, k), variant)
    if kind == "choc":
        big = pygame.transform.rotate(big, 13)
    scale = size / (100 * k)
    small = pygame.transform.smoothscale(big, (max(1, int(big.get_width() * scale)), max(1, int(big.get_height() * scale))))
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    out.blit(small, small.get_rect(center=(size // 2, size // 2)))
    return out


def blit_candy(surface, kind, center, size, variant=0, angle=0):
    img = candy(kind, int(size), variant)
    if angle:
        img = pygame.transform.rotozoom(img, angle, 1)
    surface.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))


# ======================= SMALL SPRITES =======================

@lru_cache(maxsize=32)
def coin(r):
    def d(p):
        p.circle((217, 154, 0), r, r, r)
        p.circle((255, 200, 61), r, r, r * 0.82)
        p.circle((255, 243, 176), r, r, r * 0.64)
        p.circle((255, 200, 61), r, r, r * 0.52)
    s = sprite(r * 2, r * 2, d)
    gfx.text(s, "¥", (r, r + 1), int(r * 1.15), (179, 116, 0))
    return s


@lru_cache(maxsize=32)
def star(r, fill=(255, 210, 63), edge=(224, 161, 0)):
    def d(p):
        p.poly(edge, gfx.star_points(r + 2, r + 2, r + 2))
        p.poly(fill, gfx.star_points(r + 2, r + 2, r - 0.5))
    return sprite(r * 2 + 4, r * 2 + 4, d)


@lru_cache(maxsize=16)
def heart(s, col=(255, 79, 122)):
    def d(p):
        pts = []
        for i in range(60):
            t = i / 60 * TAU
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((s / 2 + x * s / 36, s / 2 + y * s / 36))
        p.poly(col, pts)
        p.circle(lighten(col, 0.5), s * 0.33, s * 0.35, s * 0.08)
    return sprite(s, s, d)


@lru_cache(maxsize=16)
def cloud(w, col=(255, 255, 255)):
    h = int(w * 0.6)

    def d(p):
        u = w / 100
        for x, y, r in ((28, 38, 22), (52, 28, 26), (74, 40, 20), (50, 44, 22)):
            p.circle(col, x * u, y * u, r * u)
        p.rect(col, 22 * u, 38 * u, 60 * u, 20 * u, 10 * u)
    return sprite(w, h, d)


@lru_cache(maxsize=4)
def storm():
    s = pygame.Surface((70, 70), pygame.SRCALPHA)
    s.blit(cloud(64, (140, 140, 168)), (3, 0))
    bolt = sprite(30, 34, lambda p: p.poly((255, 210, 63), [(16, 0), (4, 18), (13, 18), (8, 34), (26, 12), (16, 12), (22, 0)]))
    s.blit(bolt, (22, 32))
    return s


# ======================= KIDS =======================
SKIN = [hexrgb(c) for c in ("#ffdcc2", "#f6c8a0", "#e0a77a", "#c68654", "#8d5a36", "#6b4226")]
HAIR = [hexrgb(c) for c in ("#2b1a12", "#5b3416", "#a0582a", "#e8b84a", "#d9472b", "#1a1a2e", "#7a4bd9", "#ff6fae")]
SHIRT = [hexrgb(c) for c in ("#ff5fa2", "#7a5cff", "#22c9a8", "#ffb000", "#2fa8ff", "#ff6b3d", "#9be15d", "#ff8fd1")]
PANTS = [hexrgb(c) for c in ("#3c5aa6", "#4a3a6b", "#2f2f3f", "#6b8bd6", "#a05a2c", "#3f8f7a")]
SHOE = [hexrgb(c) for c in ("#ffffff", "#ff5fa2", "#333344", "#ffcf3a", "#2fa8ff")]

_kid_cache = OrderedDict()
KID_W, KID_H, FOOT_X, FOOT_Y = 130, 205, 65, 196


def random_look(rng=random):
    return {"skin": rng.randrange(6), "hair": rng.randrange(8), "shirt": rng.randrange(8), "pants": rng.randrange(6),
            "shoe": rng.randrange(5), "style": rng.randrange(6), "cap": rng.randrange(8),
            "stripe": rng.random() < 0.4, "size": 0.88 + rng.random() * 0.2, "blink": rng.random() * 4}


def _rot(v, a):
    x, y = v
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _draw_kid(p, L, mood, swing, bob, holding_pose, blinking):
    skin, hair, shirt = SKIN[L["skin"]], HAIR[L["hair"]], SHIRT[L["shirt"]]
    pants, shoe = PANTS[L["pants"]], SHOE[L["shoe"]]
    style = L["style"]
    p.overlay(lambda q: q.ellipse((90, 36, 72), 0, 2, 27, 7), 0.2)
    # legs
    for hx, a in ((-7, swing), (7, -swing)):
        hip = (hx, -40 + bob)
        foot = _add(hip, _rot((0, 33), a))
        p.capsule(darken(pants, 0.25), hip, foot, 6.6)
        p.capsule(pants, hip, foot, 5.4)
        sh = _add(foot, (3, 3))
        p.ellipse(darken(shoe, 0.3), sh[0], sh[1], 10, 6.4)
        p.ellipse(shoe, sh[0], sh[1] - 0.5, 8.8, 5.2)
    # back arm
    back_a = swing * 0.9 if abs(swing) > 0 else -0.12
    sh_b = (-15, -71 + bob)
    hand_b = _add(sh_b, _rot((0, 24), back_a))
    p.capsule(darken(shirt, 0.3), sh_b, hand_b, 5.2)
    p.circle(darken(skin, 0.08), hand_b[0], hand_b[1] + 1, 5.5)
    # body
    p.rect(darken(shirt, 0.3), -18.5, -81.5 + bob, 37, 47, 14)
    p.rect(shirt, -17, -80 + bob, 34, 44, 13)
    if L["stripe"]:
        p.rect(lighten(shirt, 0.55), -16.5, -64 + bob, 33, 5)
        p.rect(lighten(shirt, 0.55), -17, -54 + bob, 34, 5)
    p.overlay(lambda q: q.rect((255, 255, 255), -13, -77 + bob, 8, 30, 4), 0.22)
    hy = -102 + bob
    # back hair
    if style == 1:
        p.circle(hair, -27, hy + 2, 10)
        p.circle(hair, 27, hy + 2, 10)
        p.circle(SHIRT[L["cap"]], -22, hy - 5, 4)
        p.circle(SHIRT[L["cap"]], 22, hy - 5, 4)
    elif style == 3:
        p.rect(hair, -28, hy - 20, 56, 50, 22)
    elif style == 5:
        for i in range(9):
            a = math.pi + i / 8 * math.pi
            p.circle(hair, math.cos(a) * 24, hy + math.sin(a) * 22 + 2, 11)
    # head
    p.circle(darken(skin, 0.18), 0, hy, 26.4)
    p.circle(skin, 0, hy, 25)
    p.circle(skin, -25, hy + 2, 5)
    p.circle(skin, 25, hy + 2, 5)
    # front hair
    if style in (0, 4):
        pts = [(math.cos(a) * 27, hy + math.sin(a) * 27)
               for a in [math.pi * (1.0 + 1.0 * i / 20) for i in range(21)]]
        pts += [(18, hy - 10), (6, hy - 14), (-8, hy - 9), (-27, hy - 1)]
        p.poly(hair, pts)
    elif style in (1, 3):
        pts = [(math.cos(a) * 27.5, hy + math.sin(a) * 27.5) for a in [math.pi * (1 + i / 20) for i in range(21)]]
        for i in range(6):
            pts.append((26 - i * 10.4, hy - 6 + (-7 if i % 2 else 2)))
        p.poly(hair, pts)
    elif style == 2:
        pts = [(-26, hy - 3)]
        for i in range(6):
            pts += [(-23 + i * 9.6, hy - 34 - (i % 2) * 5), (-18 + i * 9.6, hy - 16)]
        pts += [(26, hy - 3), (0, hy - 12)]
        p.poly(hair, pts)
        p.poly(hair, [(math.cos(a) * 26.5, hy + math.sin(a) * 26.5) for a in [math.pi * (1 + i / 16) for i in range(17)]])
    elif style == 5:
        for i in range(7):
            p.circle(hair, -20 + i * 6.7, hy - 20 + math.sin(i * 1.7) * 2, 8)
    if style == 4:
        cap = SHIRT[L["cap"]]
        p.poly(cap, [(math.cos(a) * 28, hy - 4 + math.sin(a) * 28) for a in [math.pi * (1 + i / 20) for i in range(21)]])
        p.rect(cap, 2, hy - 9, 36, 7, 4)
        p.circle(lighten(cap, 0.4), -8, hy - 20, 4)
    # face
    eye = (43, 26, 43)
    if blinking:
        p.line(eye, (-11, hy + 1), (-5, hy + 1), 2.4)
        p.line(eye, (5, hy + 1), (11, hy + 1), 2.4)
    else:
        p.ellipse(eye, -8, hy + 1, 3.6, 4.6)
        p.ellipse(eye, 8, hy + 1, 3.6, 4.6)
        p.circle((255, 255, 255), -7, hy - 0.8, 1.4)
        p.circle((255, 255, 255), 9, hy - 0.8, 1.4)
    p.overlay(lambda q: (q.circle((255, 90, 120), -15, hy + 9, 4.8), q.circle((255, 90, 120), 15, hy + 9, 4.8)), 0.4)
    m = (122, 43, 59)
    if mood == "happy":
        p.arc(m, 0, hy + 8, 7, 0.15 * math.pi, 0.85 * math.pi, 2.6)
    elif mood == "excited":
        p.poly(m, [(-7, hy + 9)] + [(math.cos(a) * 7, hy + 9 + math.sin(a) * 7) for a in
                                     [math.pi * i / 12 for i in range(13)]])
        p.ellipse((255, 120, 140), 0, hy + 13.5, 3.5, 2)
    elif mood == "wait":
        p.line(m, (-5, hy + 13), (5, hy + 13), 2.6)
    elif mood == "worried":
        p.arc(m, 0, hy + 18, 6, 1.25 * math.pi, 1.75 * math.pi, 2.6)
    elif mood == "sad":
        p.arc(m, 0, hy + 20, 8, 1.2 * math.pi, 1.8 * math.pi, 2.6)
    if mood in ("sad", "worried"):
        p.line(m, (-12, hy - 10), (-4, hy - 7), 2.4)
        p.line(m, (12, hy - 10), (4, hy - 7), 2.4)
    if mood == "sad":
        p.ellipse((95, 200, 255), -10, hy + 11, 2.6, 4)
    # front arm
    fa = -swing * 0.9 if abs(swing) > 0 else (-0.95 if holding_pose else 0.12)
    sh_f = (15, -71 + bob)
    hand_f = _add(sh_f, _rot((0, 24), fa))
    p.capsule(darken(shirt, 0.25), sh_f, hand_f, 5.6)
    p.capsule(shirt, sh_f, _add(sh_f, _rot((0, 14), fa)), 5.2)
    p.circle(skin, hand_f[0], hand_f[1] + 1, 5.6)
    return _add(hand_f, (0, 4))


def kid(L, mood="happy", phase=0.0, walking=False, flip=False, holding=None, hold_v=0, blink=False):
    swing_bucket = int((phase % TAU) / TAU * 12) if walking else -1
    key = (L["skin"], L["hair"], L["shirt"], L["pants"], L["shoe"], L["style"], L["cap"], L["stripe"],
           round(L["size"], 2), mood, swing_bucket, flip, holding, hold_v, blink)
    img = _kid_cache.get(key)
    if img is not None:
        _kid_cache.move_to_end(key)
        return img
    size = L["size"]
    ph = (swing_bucket + 0.5) / 12 * TAU if walking else 0
    swing = math.sin(ph) * 0.55 if walking else 0
    bob = -abs(math.sin(ph)) * 4 if walking else 0
    k = 2 * size
    big = pygame.Surface((int(KID_W * k), int(KID_H * k)), pygame.SRCALPHA)
    hand = _draw_kid(Pen(big, k, FOOT_X, FOOT_Y), L, mood, swing, bob, holding is not None, blink)
    img = pygame.transform.smoothscale(big, (int(KID_W * size), int(KID_H * size)))
    if holding:
        hx, hy = (hand[0] + FOOT_X) * size, (hand[1] + FOOT_Y) * size
        blit_candy(img, holding, (hx, hy - 8), 34 * size, hold_v)
    if flip:
        img = pygame.transform.flip(img, True, False)
    _kid_cache[key] = img
    if len(_kid_cache) > 500:
        _kid_cache.popitem(last=False)
    return img


def draw_kid(surface, L, x, y, **kw):
    img = kid(L, **kw)
    s = L["size"]
    fx = (KID_W - FOOT_X) * s if kw.get("flip") else FOOT_X * s
    surface.blit(img, (int(x - fx), int(y - FOOT_Y * s)))


# ======================= THOUGHT BUBBLE =======================

@lru_cache(maxsize=4)
def _bubble_base():
    def d(p):
        for x, y, r in ((22, 92, 4.5), (31, 83, 7), (52, 52, 31)):
            p.circle((230, 205, 220), x, y + 2, r + 1)
        for x, y, r in ((22, 92, 4), (31, 83, 6.5), (52, 52, 30)):
            p.circle((255, 255, 255), x, y, r)
    return sprite(104, 104, d)


@lru_cache(maxsize=128)
def _ring(bucket):
    frac = bucket / 60

    def d(p):
        p.arc((241, 226, 234), 30, 30, 27, 0, TAU, 5, 48)
        if frac > 0:
            hue = max(0.0, min(120.0, frac * 130))
            c = pygame.Color(0)
            c.hsva = (hue, 85, 92, 100)
            p.arc((c.r, c.g, c.b), 30, 30, 27, -math.pi / 2, -math.pi / 2 + TAU * frac, 5.5, max(4, int(48 * frac)))
    return sprite(60, 60, d)


def bubble(surface, x, y, kind, frac, qty, alt, t):
    y += math.sin(t * 4) * 1.5
    base = _bubble_base()
    surface.blit(base, (int(x - 52), int(y - 52)))
    if frac is not None:
        surface.blit(_ring(int(max(0, min(1, frac)) * 60)), (int(x - 30), int(y - 30)))
    blit_candy(surface, kind, (x, y + 1), 40)
    if qty > 1:
        gfx.aa_circle(surface, gfx.PINK, (x + 22, y - 21), 11, 2, (255, 255, 255))
        gfx.text(surface, f"x{qty}", (x + 22, y - 21), 13, (255, 255, 255))
    if alt:
        gfx.aa_circle(surface, (255, 255, 255), (x + 31, y + 17), 13, 2, (232, 210, 222))
        blit_candy(surface, alt, (x + 31, y + 18), 20)


# ======================= SHOP =======================

def _bunting_color(i):
    return [gfx.PINK, gfx.YELLOW, gfx.MINT, gfx.PURPLE, (47, 168, 255)][i % 5]


@lru_cache(maxsize=4)
def shop_base(shop_name):
    surf = pygame.Surface((W, H)).convert()
    surf.blit(gfx.vgrad(W, FLOOR_Y, (255, 211, 231), (255, 232, 242)), (0, 0))
    stripe = pygame.Surface((24, FLOOR_Y), pygame.SRCALPHA)
    stripe.fill((255, 255, 255, 110))
    for x in range(0, W, 56):
        surf.blit(stripe, (x, 0))
    for x in range(12, W, 56):
        for y in range(130, 390, 34):
            gfx.aa_circle(surf, (255, 200, 222), (x, y + ((x // 56) % 2) * 17), 4)
    # wainscot
    surf.blit(gfx.vgrad(W, FLOOR_Y - 390, (167, 240, 220), (127, 220, 196)), (0, 390))
    pygame.draw.rect(surf, (95, 201, 173), (0, 386, W, 8))
    for x in range(20, W, 80):
        gfx.rrect(surf, (x, 404, 56, 52), (190, 246, 230), 8)
    # floor
    surf.blit(gfx.vgrad(W, H - FLOOR_Y, (255, 194, 220), (255, 225, 238)), (0, FLOOR_Y))
    tile = pygame.Surface((10, 10), pygame.SRCALPHA)
    row_y, rh, row = FLOOR_Y, 26, 0
    while row_y < H:
        tw = 60 + row * 6
        off = (row % 2) * tw
        t = pygame.Surface((tw, rh), pygame.SRCALPHA)
        t.fill((255, 255, 255, 140))
        for x in range(-tw * 2 + off, W + tw, tw * 2):
            surf.blit(t, (x, row_y))
        row_y += rh
        rh += 5
        row += 1
    del tile
    sh = gfx.vgrad(W, 40, (230, 160, 196), (255, 214, 232)).convert()
    sh.set_alpha(120)
    surf.blit(sh, (0, FLOOR_Y), special_flags=pygame.BLEND_RGB_MULT)
    pygame.draw.rect(surf, (232, 143, 184), (0, FLOOR_Y - 3, W, 6))
    # bunting string + flags
    pts = []
    for i in range(65):
        x = i * W / 64
        seg = (x % (W / 2)) / (W / 2)
        pts.append((x, 116 + math.sin(seg * math.pi) * 12))
    pygame.draw.aalines(surf, (217, 122, 168), False, pts)
    for i in range(26):
        fx = 20 + i * 48
        seg = (fx % (W / 2)) / (W / 2)
        fy = 116 + math.sin(seg * math.pi) * 12
        flag = sprite(24, 24, lambda p, c=_bunting_color(i): p.poly(c, [(1, 0), (23, 0), (12, 23)]))
        surf.blit(flag, (fx - 12, fy))
    # name sign
    tw = max(260, gfx.text_size(shop_name, 32)[0] + 70)
    sx, sy = W // 2 - tw // 2, 140
    pygame.draw.aaline(surf, (176, 122, 82), (sx + 30, sy), (sx + 50, 118))
    pygame.draw.aaline(surf, (176, 122, 82), (sx + tw - 30, sy), (sx + tw - 50, 118))
    gfx.shadow(surf, (sx, sy, tw, 62), 20, 10, 80, 5)
    gfx.rrect(surf, (sx, sy, tw, 62), (143, 117, 255), 20, grad_to=(99, 66, 240))
    dash = sprite(tw - 10, 52, lambda p: p.rect((255, 255, 255), 0, 0, tw - 10, 52, 16, 2.5))
    dash.set_alpha(150)
    surf.blit(dash, (sx + 5, sy + 5))
    gfx.text(surf, shop_name, (W // 2, sy + 31), 32, (255, 255, 255), stroke=(69, 38, 194), stroke_w=4)
    # windows (frames drawn here; sky is animated per frame)
    for wx in (250, 1030):
        ring = sprite(104, 104, lambda p: (p.circle((255, 156, 200), 52, 52, 52), p.circle((255, 255, 255), 52, 52, 49),
                                           p.circle((0, 0, 0, 0), 52, 52, 40)))
        surf.blit(ring, (wx - 52, 165 - 52))
    # door frame
    gfx.rrect(surf, (14, 222, 112, FLOOR_Y - 222 + 4), (255, 255, 255), 10)
    pygame.draw.rect(surf, (90, 58, 138), (22, 230, 96, FLOOR_Y - 230))
    pygame.draw.rect(surf, (255, 233, 168), (26, 234, 88, FLOOR_Y - 234))
    # wall lollipop decoration
    blit_candy(surf, "lolli", (150, 300), 70, 1)
    return surf


@lru_cache(maxsize=2)
def _window_mask():
    return sprite(80, 80, lambda p: p.circle((255, 255, 255, 255), 40, 40, 40))


@lru_cache(maxsize=2)
def _window_cross():
    def d(p):
        p.line((255, 255, 255), (0, 40), (80, 40), 5)
        p.line((255, 255, 255), (40, 0), (40, 80), 5)
    return sprite(80, 80, d)


@lru_cache(maxsize=2)
def _sky_window():
    s = gfx.vgrad(80, 80, (127, 210, 255), (205, 241, 255)).convert_alpha()
    s.blit(sprite(140, 50, lambda p: p.ellipse((155, 225, 93), 70, 40, 70, 22)), (-30, 58))
    return s


@lru_cache(maxsize=4)
def _door(width):
    h = FLOOR_Y - 230

    def d(p):
        p.rect((232, 80, 143), 0, 0, width, h, 6)
        p.rect((255, 122, 181), 0, 0, width * 0.7, h, 6)
        p.rect((191, 239, 255), width * 0.15, 14, width * 0.7, 80, min(30, width * 0.34))
        p.rect((255, 255, 255), width * 0.25, 26, max(1, width * 0.08), 50)
        p.circle((255, 210, 63), width * 0.82, h * 0.55, 5)
    return sprite(max(4, width), h, d)


@lru_cache(maxsize=2)
def _open_sign(is_open):
    s = pygame.Surface((96, 38), pygame.SRCALPHA)
    gfx.rrect(s, (2, 2, 92, 34), (255, 255, 255), 11)
    gfx.rrect(s, (5, 5, 86, 28), gfx.MINT if is_open else gfx.RED, 9)
    label = i18n.t("open_sign" if is_open else "closed_sign")
    gfx.text(s, label, (48, 19), 17 if gfx.font(17).size(label)[0] < 80 else 14, (255, 255, 255))
    return s


def shop(surface, t, shop_name, door_open=0.0, store_open=False):
    surface.blit(shop_base(shop_name), (0, 0))
    # animated windows
    for wx in (250, 1030):
        win = _sky_window().copy()
        cx = -40 + ((t * 8 + wx) % 140)
        win.blit(cloud(44), (cx, 22))
        win.blit(_window_mask(), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        win.blit(_window_cross(), (0, 0))
        surface.blit(win, (wx - 40, 125))
    # marquee lights
    tw = max(260, gfx.text_size(shop_name, 32)[0] + 70)
    sx = W // 2 - tw // 2
    for i in range(12):
        lx = sx + 14 + i * (tw - 28) / 11
        on = (int(t * 3) + i) % 2 == 0
        col = (255, 233, 107) if on else (216, 196, 255)
        gfx.aa_circle(surface, col, (lx, 139), 4)
        gfx.aa_circle(surface, col, (lx, 203), 4)
    # door
    dw = int(96 * (1 - min(1, door_open) * 0.75))
    surface.blit(_door(dw), (22, 230))
    sign = pygame.transform.rotozoom(_open_sign(store_open), math.sin(t * 1.5) * 2.5, 1)
    surface.blit(sign, sign.get_rect(center=(70, 200)))
    # awning
    surface.blit(awning(), (0, 0))


@lru_cache(maxsize=1)
def awning():
    n, y = 20, 66
    w = W / n

    def d(p):
        for i in range(n):
            col = (255, 255, 255) if i % 2 else gfx.PINK
            p.rect(col, i * w, 0, w + 1, y)
            p.circle(col, i * w + w / 2, y, w / 2)
        p.overlay(lambda q: q.rect((0, 0, 0), 0, y - 8, W, 8), 0.08)
    return sprite(W, y + w / 2 + 2, d, k=2)


@lru_cache(maxsize=1)
def counter():
    s = pygame.Surface((180, 240), pygame.SRCALPHA)
    x, y = 20, 76
    gfx.shadow(s, (x, y, 135, 150), 12, 8, 70, 5)
    gfx.rrect(s, (x, y, 135, 150), (255, 122, 181), 12)
    for i in range(4):
        gfx.rrect(s, (x + 12 + i * 32, y + 26, 16, 118), (255, 190, 220), 6)
    gfx.rrect(s, (x - 8, y - 6, 151, 22), (255, 243, 248), 9, 3, (255, 179, 212))
    rx, ry = x + 22, y - 66

    def reg(p):
        p.rect(gfx.PURPLE, 0, 20, 92, 42, 8)
        p.rect(gfx.PURPLE_D, 10, 0, 72, 28, 6)
        p.rect((184, 255, 233), 16, 5, 60, 16, 4)
        for i in range(4):
            for j in range(2):
                p.rect((255, 255, 255), 10 + i * 19, 30 + j * 13, 14, 9, 3)
    s.blit(sprite(92, 62, reg), (rx, ry))
    gfx.text(s, "¥ ¥ ¥", (rx + 46, ry + 13), 11, gfx.GREEN_TXT)

    def jar(p):
        p.rect((220, 245, 255), 2, 4, 26, 40, 8)
        for i in range(6):
            p.circle([gfx.PINK, gfx.YELLOW, gfx.MINT][i % 3], 9 + (i % 3) * 7, 34 - (i // 3) * 8, 4)
        p.rect(gfx.PINK, 0, 0, 30, 7, 3)
    s.blit(sprite(30, 46, jar), (x, y - 56))
    return s


# ======================= SHELVES =======================

@lru_cache(maxsize=16)
def shelf_base(w, h, tiers):
    w, h = int(w), int(h)
    s = pygame.Surface((w + 30, h + 30), pygame.SRCALPHA)
    gfx.shadow(s, (15, 15 + 34, w, h - 34), 12, 10, 90, 6)
    body = sprite(w, h - 34, lambda p: (p.rect((150, 96, 54), 0, 0, w, h - 34, 12),
                                        p.rect((214, 156, 100), 3, 2, w - 6, h - 40, 10)))
    s.blit(body, (15, 15 + 34))
    gfx.rrect(s, (15 + 9, 15 + 44, w - 18, h - 62), (255, 241, 247), 8)
    inner_h = h - 62
    for i in range(6):
        st = pygame.Surface((max(1, (w - 18) // 12), inner_h), pygame.SRCALPHA)
        st.fill((255, 95, 162, 18))
        s.blit(st, (15 + 9 + i * (w - 18) / 6, 15 + 44))
    tier_h = inner_h / tiers
    for t in range(tiers):
        by = 15 + 44 + tier_h * (t + 1)
        gfx.rrect(s, (15 + 5, by - 4, w - 10, 10), (168, 105, 58), 4)
        pygame.draw.line(s, (214, 160, 120), (15 + 8, by - 2), (15 + w - 8, by - 2), 2)
    return s


@lru_cache(maxsize=32)
def shelf_label(w, kind, price, boosted, hover):
    w = int(w)
    s = pygame.Surface((w - 12, 38), pygame.SRCALPHA)
    col = PRODUCTS[kind]["color"]
    gfx.rrect(s, (0, 0, w - 12, 38), col, 12)
    gfx.rrect(s, (3, 3, w - 18, 32), (255, 255, 255) if hover else (255, 250, 242), 10)
    name = i18n.prod(kind)
    size = 16 if w >= 170 else 14
    room = w - 12 - 66
    while size > 10 and gfx.font(size).size(name)[0] > room:
        size -= 1
    gfx.text(s, name, ((w - 12 - 56) / 2 + 2, 19), size, gfx.INK)
    gfx.rrect(s, (w - 12 - 54, 8, 44, 22), gfx.MINT if boosted else gfx.YELLOW, 11)
    gfx.text(s, f"¥{price}", (w - 12 - 32, 19), 13, (255, 255, 255) if boosted else (107, 67, 0))
    return s


def shelf(surface, rect, sh, cap, price, boosted, hover, t, rush, hint=None):
    x, y, w, h = rect
    tiers = 2 if cap <= 10 else 3
    per_row = math.ceil(cap / tiers)
    surface.blit(shelf_base(w, h, tiers), (x - 15, y - 15))
    surface.blit(shelf_label(w, sh["type"], price, boosted, hover), (x + 6, y))
    inner_top, inner_h = y + 44, h - 62
    tier_h = inner_h / tiers
    size = int(min(54, tier_h * 0.78, (w - 30) / per_row * 1.7))
    idx = 0
    for tr in range(tiers):
        base_y = inner_top + tier_h * (tr + 1)
        for c in range(per_row):
            if idx < sh["count"]:
                cx = x + 20 + (w - 40) * (c + 0.5) / per_row
                blit_candy(surface, sh["type"], (cx, base_y - size * 0.48 - 3), size, (idx * 7 + tr) % 5)
            idx += 1
    full, empty = sh["count"] >= cap, sh["count"] == 0
    pill = pygame.Rect(0, 0, 62, 24)
    pill.center = (x + w / 2, y + h - 2)
    gfx.rrect(surface, pill, gfx.RED if empty else gfx.MINT if full else (255, 255, 255), 12, 2,
              gfx.RED_D if empty else gfx.MINT_D if full else (255, 179, 212))
    gfx.text(surface, f"{sh['count']}/{cap}", pill.center, 14, (255, 255, 255) if (empty or full) else gfx.INK)
    if empty and rush and not sh["restock"]:
        a = int(60 + math.sin(t * 6) * 40)
        gfx.rrect(surface, (x + 9, inner_top, w - 18, inner_h), (255, 91, 91), 8, alpha=a)
        gfx.text(surface, i18n.t("empty_shelf"), (x + w / 2, inner_top + inner_h / 2), 22, gfx.RED, stroke=(255, 255, 255), stroke_w=3)
    if sh["restock"]:
        rs = sh["restock"]
        f = 1 - rs["t"] / rs["total"]
        gfx.rrect(surface, (x + 9, inner_top, w - 18, inner_h), (255, 255, 255), 8, alpha=170)
        blit_candy(surface, rs["type"], (x + w / 2, y + 108 + math.sin(t * 10) * 4), 56)
        gfx.text(surface, i18n.t("restocking"), (x + w / 2, y + 166), 15, gfx.INK)
        gfx.rrect(surface, (x + 22, y + 180, w - 44, 14), (243, 220, 232), 7)
        if f > 0.05:
            gfx.rrect(surface, (x + 22, y + 180, int((w - 44) * f), 14), gfx.PINK, 7)
    if hover:
        ring = gfx.rounded(int(w + 10), int(h + 10), 16, (0, 0, 0, 0), 5, (255, 207, 58))
        surface.blit(ring, (x - 5, y - 5))
        if hint:
            gfx.text(surface, hint, (x + w / 2, y - 18), 15, gfx.INK, stroke=(255, 255, 255), stroke_w=3)


# ======================= UPGRADE ICONS =======================

@lru_cache(maxsize=16)
def upgrade_icon(kind, size=56):
    def d(p):
        u = size / 64
        if kind == "box":
            p.poly((156, 102, 48), [(6 * u, 21 * u), (32 * u, 10 * u), (58 * u, 21 * u), (58 * u, 47 * u), (32 * u, 58 * u), (6 * u, 47 * u)])
            p.poly((224, 169, 109), [(9 * u, 23 * u), (32 * u, 13 * u), (55 * u, 23 * u), (55 * u, 45 * u), (32 * u, 55 * u), (9 * u, 45 * u)])
            p.poly((240, 192, 140), [(9 * u, 23 * u), (32 * u, 13 * u), (55 * u, 23 * u), (32 * u, 33 * u)])
            p.line((156, 102, 48), (32 * u, 33 * u), (32 * u, 55 * u), 2.5 * u)
            p.line(gfx.MINT, (46 * u, 4 * u), (46 * u, 18 * u), 5 * u)
            p.line(gfx.MINT, (39 * u, 11 * u), (53 * u, 11 * u), 5 * u)
        elif kind == "shelf":
            p.rect((156, 102, 48), 10 * u, 8 * u, 44 * u, 50 * u, 5 * u)
            p.rect((255, 241, 247), 15 * u, 13 * u, 34 * u, 40 * u, 3 * u)
            p.rect((168, 105, 58), 15 * u, 31 * u, 34 * u, 4 * u)
            p.circle(gfx.PINK, 23 * u, 25 * u, 5 * u)
            p.circle(gfx.PURPLE, 36 * u, 25 * u, 5 * u)
            p.circle(gfx.MINT, 29 * u, 45 * u, 5 * u)
        elif kind == "tall":
            p.rect((156, 102, 48), 14 * u, 4 * u, 30 * u, 56 * u, 5 * u)
            p.rect((224, 169, 109), 17 * u, 7 * u, 24 * u, 50 * u, 3 * u)
            p.rect((168, 105, 58), 17 * u, 22 * u, 24 * u, 4 * u)
            p.rect((168, 105, 58), 17 * u, 40 * u, 24 * u, 4 * u)
            p.line(gfx.MINT, (54 * u, 34 * u), (54 * u, 10 * u), 4.5 * u)
            p.poly(gfx.MINT, [(46 * u, 16 * u), (54 * u, 5 * u), (62 * u, 16 * u)])
        elif kind == "bolt":
            p.circle(gfx.YELLOW_D, 32 * u, 32 * u, 27 * u)
            p.circle(gfx.YELLOW, 32 * u, 32 * u, 24 * u)
            p.poly((255, 255, 255), [(36 * u, 10 * u), (19 * u, 36 * u), (31 * u, 36 * u), (27 * u, 54 * u), (45 * u, 27 * u), (33 * u, 27 * u)])
        elif kind == "sign":
            p.rect(gfx.PURPLE_D, 5 * u, 13 * u, 54 * u, 36 * u, 10 * u)
            p.rect(gfx.PURPLE, 8 * u, 16 * u, 48 * u, 30 * u, 8 * u)
            p.circle(gfx.PINK, 12 * u, 8 * u, 3.5 * u)
            p.circle(gfx.MINT, 52 * u, 8 * u, 3.5 * u)
        elif kind == "music":
            p.rect(gfx.PINK_D, 11 * u, 5 * u, 42 * u, 54 * u, 19 * u)
            p.rect(gfx.PINK, 14 * u, 8 * u, 36 * u, 48 * u, 16 * u)
            p.circle((255, 233, 107), 32 * u, 38 * u, 10 * u)
            p.line((255, 255, 255), (21 * u, 22 * u), (43 * u, 22 * u), 4 * u)
    s = sprite(size, size, d)
    if kind == "sign":
        gfx.text(s, "OPEN", (size / 2, size * 0.48), int(size * 0.24), (255, 233, 107))
    return s


# ======================= BACKDROPS & EVENT ART =======================

@lru_cache(maxsize=4)
def rays(radius, n=12, alpha=46):
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(n):
        a = i / n * TAU
        w = math.pi / n * 0.55
        pts = [(radius, radius), (radius + math.cos(a - w) * radius * 1.5, radius + math.sin(a - w) * radius * 1.5),
               (radius + math.cos(a + w) * radius * 1.5, radius + math.sin(a + w) * radius * 1.5)]
        pygame.draw.polygon(s, (255, 255, 255, alpha), pts)
    return s


def draw_rays(surface, center, radius, t, speed=0.15, n=12, alpha=46):
    img = pygame.transform.rotate(rays(radius, n, alpha), (t * speed * 57.3) % (360 / n))
    surface.blit(img, img.get_rect(center=center))


@lru_cache(maxsize=8)
def sun_face(r, shades):
    def d(p):
        c = r + 4
        p.circle((255, 159, 26), c, c, r + 3)
        p.circle(gfx.YELLOW, c, c, r)
        if shades:
            p.rect((43, 26, 43), c - r * 0.65, c - r * 0.25, r * 0.55, r * 0.34, 8)
            p.rect((43, 26, 43), c + r * 0.1, c - r * 0.25, r * 0.55, r * 0.34, 8)
            p.rect((43, 26, 43), c - r * 0.15, c - r * 0.18, r * 0.3, 4)
        else:
            p.circle((122, 59, 0), c - r * 0.3, c - r * 0.1, 5)
            p.circle((122, 59, 0), c + r * 0.3, c - r * 0.1, 5)
        p.arc((122, 59, 0), c, c + r * 0.1, r * 0.35, 0.2 * math.pi, 0.8 * math.pi, 4)
        p.overlay(lambda q: (q.circle((255, 90, 90), c - r * 0.55, c + r * 0.3, 8),
                             q.circle((255, 90, 90), c + r * 0.55, c + r * 0.3, 8)), 0.35)
    return sprite(r * 2 + 8, r * 2 + 8, d)


@lru_cache(maxsize=4)
def sun_rays(r):
    def d(p):
        c = r + 34
        for i in range(12):
            a = i / 12 * TAU
            pts = [(c + math.cos(a - 0.12) * (r + 2), c + math.sin(a - 0.12) * (r + 2)),
                   (c + math.cos(a) * (r + 28), c + math.sin(a) * (r + 28)),
                   (c + math.cos(a + 0.12) * (r + 2), c + math.sin(a + 0.12) * (r + 2))]
            p.poly((255, 210, 63), pts)
    return sprite((r + 34) * 2, (r + 34) * 2, d)


def draw_sun(surface, x, y, r, t, shades=False):
    rr = pygame.transform.rotate(sun_rays(r), (t * 20) % 30)
    surface.blit(rr, rr.get_rect(center=(x, y)))
    face = sun_face(r, shades)
    surface.blit(face, face.get_rect(center=(x, y)))


@lru_cache(maxsize=16)
def blob(w, h, color):
    return sprite(w, h, lambda p: p.ellipse(color, w / 2, h / 2, w / 2, h / 2))


@lru_cache(maxsize=4)
def school():
    def d(p):
        p.rect((232, 87, 75), 15, 50, 180, 120)
        p.poly((194, 62, 51), [(0, 54), (105, 0), (210, 54)])
        p.circle((51, 51, 51), 105, 32, 18)
        p.circle((255, 255, 255), 105, 32, 15.5)
        for i in range(3):
            p.rect((191, 239, 255), 33 + i * 56, 72, 32, 28, 3)
        p.rect((122, 75, 42), 87, 120, 36, 50, 4)
    return sprite(210, 172, d)


@lru_cache(maxsize=2)
def price_tag():
    s = sprite(232, 108, lambda p: (p.rect((255, 255, 255), 0, 0, 232, 108, 22), p.rect((255, 59, 107), 6, 6, 220, 96, 18),
                                    p.circle((255, 255, 255), 30, 54, 9)))
    gfx.text(s, i18n.t("sale_tag_big"), (128, 46), 40, (255, 255, 255), stroke=(184, 32, 74), stroke_w=3)
    gfx.text(s, i18n.t("sale_tag_small"), (128, 82), 18, (255, 233, 107))
    return s


@lru_cache(maxsize=2)
def cake():
    def d(p):
        p.rect((255, 243, 248), 0, 60, 200, 70, 14)
        p.rect((255, 154, 213), 30, 0, 140, 62, 12)
        for i in range(7):
            p.circle((255, 255, 255), 40 + i * 20, 2, 10)
        for i in range(9):
            p.circle(gfx.PINK, 12 + i * 22, 62, 9)
        for i in range(5):
            p.rect([gfx.PURPLE, gfx.MINT, gfx.YELLOW][i % 3], 52 + i * 22, -36 + 40, 8, 32, 3)
    return sprite(200, 132, d)


@lru_cache(maxsize=2)
def tent():
    def d(p):
        for i in range(8):
            col = (255, 255, 255) if i % 2 else (255, 79, 154)
            p.poly(col, [(160, 20), (i * 40, 140), ((i + 1) * 40, 140)])
        p.poly(gfx.YELLOW, [(160, 0), (178, 10), (160, 20)])
        p.rect((255, 232, 242), 20, 140, 280, 70)
        p.rect(gfx.INK, 130, 150, 60, 60, 6)
    return sprite(320, 210, d)


@lru_cache(maxsize=2)
def up_arrow():
    return sprite(90, 110, lambda p: (p.poly((255, 255, 255), [(45, 0), (90, 52), (62, 52), (62, 110), (28, 110), (28, 52), (0, 52)]),
                                      p.poly((255, 59, 59), [(45, 6), (82, 48), (58, 48), (58, 105), (32, 105), (32, 48), (8, 48)])))


@lru_cache(maxsize=2)
def pumpkin():
    def d(p):
        p.rect((90, 138, 42), 46, 0, 8, 16, 3)
        p.ellipse((255, 138, 31), 50, 52, 50, 40)
        p.ellipse((217, 106, 0), 50, 52, 20, 40, 3)
        p.poly((255, 233, 107), [(26, 46), (38, 32), (48, 46)])
        p.poly((255, 233, 107), [(74, 46), (62, 32), (52, 46)])
        p.poly((255, 233, 107), [(28, 58)] + [(50 + math.cos(a) * 22, 58 + math.sin(a) * 18) for a in
                                               [math.pi * i / 10 for i in range(11)]])
    return sprite(100, 94, d)


@lru_cache(maxsize=2)
def umbrella():
    def d(p):
        p.poly(gfx.PINK, [(70 + math.cos(a) * 70, 70 + math.sin(a) * 70) for a in [math.pi + math.pi * i / 24 for i in range(25)]])
        p.poly(gfx.YELLOW, [(70, 70)] + [(70 + math.cos(a) * 70, 70 + math.sin(a) * 70) for a in
                                         [math.pi * 1.36 + math.pi * 0.28 * i / 8 for i in range(9)]])
        p.line(gfx.INK, (70, 70), (70, 150), 4)
    return sprite(140, 152, d)


EVENT_BG = {
    "opening": ((255, 209, 236), (184, 242, 230)), "normal": ((255, 227, 240), (217, 204, 255)),
    "heatwave": ((255, 207, 107), (255, 122, 69)), "recess": ((169, 220, 255), (95, 168, 255)),
    "sale": ((255, 242, 122), (255, 179, 217)), "rain": ((181, 198, 224), (107, 133, 179)),
    "party": ((255, 194, 226), (200, 155, 255)), "festival": ((255, 211, 110), (255, 126, 179)),
    "cocoa": ((240, 214, 187), (168, 119, 79)), "sunny": ((199, 243, 255), (255, 229, 138)),
    "spooky": ((201, 163, 255), (90, 58, 138)),
}
_LOOKS = [random_look(random.Random(i * 11 + 3)) for i in range(6)]
CONFETTI = [gfx.PINK, gfx.YELLOW, gfx.MINT, gfx.PURPLE, (47, 168, 255), (255, 255, 255)]


def confetti(surface, w, h, t, n=40):
    for i in range(n):
        x = (i * 97.3 + math.sin(t + i) * 20) % w
        y = (i * 53.7 + t * (40 + (i % 5) * 12)) % (h + 20) - 10
        a = t * 3 + i
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in ((-4, -2), (4, -2), (4, 2), (-4, 2))]
        pygame.draw.polygon(surface, CONFETTI[i % 6], pts)


def event_art(surface, eid, t):
    w, h = surface.get_size()
    top, bottom = EVENT_BG.get(eid, EVENT_BG["normal"])
    surface.blit(gfx.vgrad(w, h, top, bottom), (0, 0))
    draw_rays(surface, (w // 2, int(h * 0.55)), 420, t)

    def ground(col):
        g = blob(int(w * 1.4), 180, col)
        surface.blit(g, (w / 2 - g.get_width() / 2, h - 50))

    def bob(i, amp=7, sp=3):
        return math.sin(t * sp + i) * amp

    if eid == "heatwave":
        draw_sun(surface, 100, 78, 42, t, True)
        ground((255, 176, 102))
        blit_candy(surface, "choc", (w / 2 + 10, h * 0.52), 130)
        for i in range(4):
            ln = 20 + (t * 25 + i * 13) % 40
            gfx.rrect(surface, (w / 2 - 22 + i * 16, h * 0.52 + 40, 10, int(ln)), (90, 46, 23), 5)
        surface.blit(blob(140, 28, (90, 46, 23)), (w / 2 - 60, h - 38))
        for i in range(3):
            blit_candy(surface, "ice", (w - 150 + i * 50, h * 0.55 + bob(i)), 90, i)
    elif eid == "recess":
        ground((126, 217, 87))
        sc = school()
        surface.blit(sc, (w / 2 - 105, 28))
        for i in range(5):
            x = (t * 120 + i * 130) % (w + 120) - 60
            draw_kid(surface, _LOOKS[i], x, h - 12 - (i % 2) * 10, mood="excited", phase=t * 14 + i, walking=True)
    elif eid == "sale":
        ground((255, 208, 228))
        for i in range(6):
            blit_candy(surface, "lolli", (70 + i * 90 + (60 if i > 2 else 0), h * 0.64 + bob(i, 8)), 90, i)
        tag = pygame.transform.rotozoom(price_tag(), 7 + math.sin(t * 2) * 3, 1)
        surface.blit(tag, tag.get_rect(center=(w / 2, h * 0.4)))
    elif eid == "rain":
        surface.blit(cloud(130, (238, 243, 251)), (20, 10))
        surface.blit(cloud(150, (226, 234, 246)), (300, 0))
        for i in range(42):
            x, y = (i * 37) % w, (i * 29 + t * 300) % h
            pygame.draw.aaline(surface, (255, 255, 255), (x, y), (x - 6, y + 16))
        ground((124, 155, 201))
        draw_kid(surface, _LOOKS[2], w / 2, h - 18, mood="happy", holding="choc")
        um = umbrella()
        surface.blit(um, (w / 2 - 70, h - 18 - 220))
        blit_candy(surface, "choc", (110, h * 0.62), 90)
        blit_candy(surface, "choc", (w - 110, h * 0.62), 90, 1)
    elif eid == "party":
        confetti(surface, w, h, t, 50)
        ground((255, 179, 217))
        ck = cake()
        cx, cy = w / 2, h - 20
        surface.blit(ck, (cx - 100, cy - 132))
        for i in range(5):
            kx = cx - 44 + i * 22
            fl = 9 + math.sin(t * 20 + i) * 2
            surface.blit(blob(10, int(fl * 2), (255, 176, 0)), (kx - 5, cy - 132 - fl * 2 + 2))
            surface.blit(blob(5, 10, (255, 246, 160)), (kx - 2.5, cy - 140))
        for i in range(4):
            blit_candy(surface, "gummy", (70 + i * 80 if i < 2 else w - 230 + (i - 2) * 80, h * 0.6 + bob(i, 8, 4)), 80, i)
    elif eid == "festival":
        ground((255, 224, 138))
        surface.blit(tent(), (w / 2 - 160, 20))
        blit_candy(surface, "cotton", (100, h * 0.55), 100)
        blit_candy(surface, "cotton", (w - 100, h * 0.55), 100, 1)
        confetti(surface, w, h, t, 30)
    elif eid == "cocoa":
        ground((201, 154, 112))
        for i in range(3):
            blit_candy(surface, "choc", (w / 2 - 110 + i * 110, h * 0.58 - (20 if i == 1 else 0)), 120, i)
        ar = up_arrow()
        surface.blit(ar, ar.get_rect(center=(w - 90, 110 + bob(0, 6))))
        surface.blit(coin(30), (60, 60))
        surface.blit(coin(22), (118, 108))
    elif eid == "sunny":
        draw_sun(surface, w - 100, 78, 42, t, True)
        surface.blit(cloud(100), (30, 30))
        ground((155, 225, 93))
        for i in range(4):
            x = (t * 70 + i * 160) % (w + 120) - 60
            draw_kid(surface, _LOOKS[i + 1], x, h - 14 - (i % 2) * 8, mood="happy", phase=t * 9 + i, walking=True,
                     holding=["lolli", "ice", "gummy", "lolli"][i])
    elif eid == "spooky":
        ground((58, 42, 90))
        gfx.aa_circle(surface, (255, 246, 200), (w - 100, 70), 40)
        for i in range(3):
            pk = pumpkin()
            surface.blit(pk, pk.get_rect(center=(w / 2 - 130 + i * 130, h * 0.62 + bob(i, 6))))
        blit_candy(surface, "jaw", (80, h * 0.5), 70)
        blit_candy(surface, "jaw", (w - 80, h * 0.5), 70, 1)
    else:
        if eid == "opening":
            confetti(surface, w, h, t, 50)
        ground((255, 194, 220))
        kinds = ["lolli", "gummy", "choc", "ice", "jaw", "cotton"]
        items = []
        for i in range(6):
            a = t * 0.6 + i * TAU / 6
            items.append((math.sin(a), kinds[i], w / 2 + math.cos(a) * 190, h * 0.5 + math.sin(a) * 60, 76 + math.sin(a) * 14, i))
        for _z, kind, x, y, s, i in sorted(items):
            blit_candy(surface, kind, (x, y), s, i)
        if eid == "opening":
            ban = _banner(i18n.t("grand_opening_banner"))
            ban = pygame.transform.rotozoom(ban, math.sin(t * 2) * 3, 1)
            surface.blit(ban, ban.get_rect(center=(w / 2, h * 0.48)))
        else:
            st = star(40)
            surface.blit(st, st.get_rect(center=(w / 2, h * 0.5)))


@lru_cache(maxsize=8)
def _banner(label, color=(255, 59, 107), dark=(184, 32, 74)):
    f = gfx.font(26)
    tw = f.size(label)[0] + 70
    s = sprite(tw, 44, lambda p: p.poly(color, [(20, 2), (tw - 20, 2), (tw, 22), (tw - 20, 42), (20, 42), (0, 22)]))
    gfx.text(s, label, (tw / 2, 22), 26, (255, 255, 255), stroke=dark, stroke_w=3)
    return s


# ======================= TITLE SCENE =======================

class TitleBackdrop:
    def __init__(self):
        rng = random.Random(5)
        kinds = ["lolli", "gummy", "choc", "ice", "jaw", "cotton"]
        self.candies = [{"kind": kinds[i % 6], "x": rng.uniform(0, W), "y": rng.uniform(0, H), "s": int(rng.uniform(40, 86)),
                         "v": i, "sp": rng.uniform(22, 50), "rot": rng.uniform(0, 360), "vr": rng.uniform(-40, 40)}
                        for i in range(24)]
        self.bg = None

    def _static(self):
        if self.bg is None:
            self.bg = gfx.vgrad_n(W, H, [(255, 159, 208), (255, 201, 227), (255, 231, 184)]).convert()
        return self.bg

    def draw(self, surface, t, dt):
        surface.blit(self._static(), (0, 0))
        draw_rays(surface, (W // 2, int(H * 0.3)), 900, t, 0.08, 16, 50)
        for c in self.candies:
            c["y"] += c["sp"] * dt
            c["rot"] += c["vr"] * dt
            if c["y"] > H + 60:
                c["y"], c["x"] = -60, random.uniform(0, W)
            img = pygame.transform.rotate(candy(c["kind"], c["s"], c["v"]), c["rot"])
            img.set_alpha(215)
            surface.blit(img, img.get_rect(center=(c["x"], c["y"])))
        surface.blit(_title_ground(), (0, 0))
        for i in range(3):
            x = 380 + (t * 50 + i * 300) % 900
            draw_kid(surface, _LOOKS[i + 2], x, H - 30 + (i % 2) * 8, mood="excited", phase=t * 8 + i * 2, walking=True,
                     holding=["lolli", "ice", "cotton"][i])


@lru_cache(maxsize=1)
def _title_ground():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.blit(blob(840, 340, (155, 230, 201)), (250 - 420, H + 60 - 170))
    s.blit(blob(920, 360, (127, 217, 184)), (1060 - 460, H + 70 - 180))
    sx, sy = 90, H - 230

    def store(p):
        p.rect((255, 179, 212), 10, 30, 234, 204, 12)
        p.rect((255, 243, 248), 12, 32, 230, 200, 10)
        for i in range(7):
            col = gfx.PINK if i % 2 == 0 else (255, 255, 255)
            p.rect(col, i * 36, 24, 36, 40)
            p.circle(col, 18 + i * 36, 64, 18)
        p.rect((191, 239, 255), 30, 102, 110, 80, 8)
        p.rect(gfx.PURPLE, 162, 110, 58, 120, 6)
        p.circle((255, 210, 63), 208, 170, 4)
    s.blit(sprite(252, 236, store), (sx - 12, sy - 30))
    blit_candy(s, "lolli", (sx + 46, sy + 120), 50)
    blit_candy(s, "gummy", (sx + 78, sy + 128), 38, 1)
    blit_candy(s, "choc", (sx + 106, sy + 122), 44)
    return s


def draw_logo(surface, cx, y, t):
    word = "Candy Store"
    cols = [(159, 240, 222), (255, 241, 248), (255, 224, 102)]
    f = gfx.font(92, latin=True)
    widths = [f.size(ch)[0] for ch in word]
    total = sum(widths)
    x = cx - total / 2
    for i, ch in enumerate(word):
        if ch != " ":
            dy = math.sin(t * 3.9 - i * 0.5) * 10
            img = gfx.render_text(ch, 92, cols[i % 3], True, (217, 58, 125), 6, (122, 30, 90), latin=True)
            rot = pygame.transform.rotozoom(img, math.sin(t * 3.9 - i * 0.5) * 3, 1)
            surface.blit(rot, rot.get_rect(center=(x + widths[i] / 2, y + 50 + dy)))
        x += widths[i]
    badge = _tycoon_badge()
    rb = pygame.transform.rotozoom(badge, 2, 1)
    surface.blit(rb, rb.get_rect(center=(cx, y + 142)))


@lru_cache(maxsize=1)
def _tycoon_badge():
    s = pygame.Surface((360, 86), pygame.SRCALPHA)
    gfx.rrect(s, (4, 8, 352, 74), (69, 38, 194), 22)
    gfx.rrect(s, (4, 2, 352, 74), (255, 255, 255), 22)
    gfx.rrect(s, (9, 7, 342, 64), (143, 117, 255), 18, grad_to=(99, 66, 240))
    f = gfx.font(50, latin=True)
    word = "TYCOON"
    spacing = 12
    total = sum(f.size(c)[0] for c in word) + spacing * (len(word) - 1)
    x = 180 - total / 2
    for c in word:
        img = gfx.render_text(c, 50, (255, 255, 255), True, None, 0, (69, 38, 194), latin=True)
        s.blit(img, (x - 3, 39 - img.get_height() / 2))
        x += f.size(c)[0] + spacing
    return s


def app_icon(size=512):
    """The game icon: a big swirl lollipop on a candy-pink tile."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    gfx.rrect(s, (0, 0, size, size), (217, 58, 125), int(size * 0.22))
    gfx.rrect(s, (int(size * 0.03), int(size * 0.03), int(size * 0.94), int(size * 0.94)), (255, 140, 190),
              int(size * 0.2), grad_to=(255, 79, 151))
    img = pygame.transform.rotozoom(candy("lolli", int(size * 0.86), 0), -18, 1)
    s.blit(img, img.get_rect(center=(size * 0.5, size * 0.52)))
    g = candy("gummy", int(size * 0.34), 1)
    s.blit(g, g.get_rect(center=(size * 0.24, size * 0.76)))
    st = star(int(size * 0.07))
    s.blit(st, st.get_rect(center=(size * 0.8, size * 0.2)))
    return s
