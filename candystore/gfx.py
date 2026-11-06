"""Drawing toolkit: fonts, outlined text, smooth (supersampled) shapes, gradients, soft shadows.

pygame's filled shapes have jagged edges, so sprites are drawn at 3x size with a Pen
and scaled down smoothly, then cached. That gives clean, anti-aliased cartoon art.
"""
import math
from functools import lru_cache

import pygame

from .paths import asset

SS = 3
INK = (90, 36, 72)
INK_SOFT = (138, 90, 122)
WHITE = (255, 255, 255)
PINK = (255, 95, 162)
PINK_D = (217, 58, 125)
PURPLE = (122, 92, 255)
PURPLE_D = (86, 54, 214)
MINT = (34, 201, 168)
MINT_D = (16, 148, 121)
YELLOW = (255, 207, 58)
YELLOW_D = (217, 158, 0)
RED = (255, 91, 91)
RED_D = (199, 50, 50)
CREAM = (255, 248, 241)
GREEN_TXT = (14, 138, 111)
RED_TXT = (211, 47, 47)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t):
    return mix(c, (255, 255, 255), t)


def darken(c, t):
    return mix(c, (0, 0, 0), t)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------- fonts & text ----------------

@lru_cache(maxsize=64)
def font(size, bold=True):
    name = "Fredoka-Bold.ttf" if bold else "Fredoka-Medium.ttf"
    try:
        return pygame.font.Font(asset("fonts", name), int(size))
    except (pygame.error, FileNotFoundError, OSError):
        return pygame.font.Font(None, int(size * 1.3))


_text_cache = {}


def render_text(s, size, color, bold=True, stroke=None, stroke_w=0, shadow=None):
    key = (s, size, color, bold, stroke, stroke_w, shadow)
    surf = _text_cache.get(key)
    if surf is not None:
        return surf
    f = font(size, bold)
    body = f.render(s, True, color)
    if not stroke and not shadow:
        surf = body
    else:
        pad = stroke_w + (3 if shadow else 0)
        surf = pygame.Surface((body.get_width() + pad * 2, body.get_height() + pad * 2 + (3 if shadow else 0)),
                              pygame.SRCALPHA)
        if shadow:
            sh = f.render(s, True, shadow)
            for dx, dy in _ring(stroke_w):
                surf.blit(sh, (pad + dx, pad + dy + 3))
        if stroke:
            st = f.render(s, True, stroke)
            for dx, dy in _ring(stroke_w):
                surf.blit(st, (pad + dx, pad + dy))
        surf.blit(body, (pad, pad))
    if len(_text_cache) > 1500:
        _text_cache.clear()
    _text_cache[key] = surf
    return surf


@lru_cache(maxsize=16)
def _ring(r):
    if r <= 0:
        return ((0, 0),)
    pts = set()
    steps = max(8, int(r * 6))
    for i in range(steps):
        a = i / steps * math.tau
        pts.add((round(math.cos(a) * r), round(math.sin(a) * r)))
    for rr in range(1, r):
        for i in range(8):
            a = i / 8 * math.tau
            pts.add((round(math.cos(a) * rr), round(math.sin(a) * rr)))
    return tuple(pts)


def text(surface, s, pos, size, color=INK, anchor="center", bold=True, stroke=None, stroke_w=0, shadow=None, alpha=255):
    surf = render_text(str(s), int(size), tuple(color), bold, stroke and tuple(stroke), stroke_w, shadow and tuple(shadow))
    rect = surf.get_rect(**{anchor: (int(pos[0]), int(pos[1]))})
    if alpha < 255:
        surf = surf.copy()
        surf.set_alpha(alpha)
    surface.blit(surf, rect)
    return rect


def wrap(s, size, width, bold=False):
    f = font(size, bold)
    lines = []
    for para in s.split("\n"):
        words, line = para.split(" "), ""
        for w in words:
            test = (line + " " + w).strip()
            if f.size(test)[0] <= width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        lines.append(line)
    return lines


def paragraph(surface, s, pos, size, width, color=INK, bold=False, anchor="midtop", spacing=1.25):
    x, y = pos
    lh = int(size * spacing)
    for line in wrap(s, size, width, bold):
        text(surface, line, (x, y), size, color, anchor=anchor, bold=bold)
        y += lh
    return y


# ---------------- pen: draws at SS scale ----------------

class Pen:
    """Draw on a surface with all coordinates multiplied by k (supersampling)."""

    def __init__(self, surf, k=SS, ox=0, oy=0):
        self.s, self.k, self.ox, self.oy = surf, k, ox, oy

    def P(self, x, y):
        return (int((x + self.ox) * self.k), int((y + self.oy) * self.k))

    def circle(self, c, x, y, r, width=0):
        pygame.draw.circle(self.s, c, self.P(x, y), max(1, int(r * self.k)), int(width * self.k) if width else 0)

    def ellipse(self, c, cx, cy, rx, ry, width=0):
        k = self.k
        rect = pygame.Rect(0, 0, max(1, int(rx * 2 * k)), max(1, int(ry * 2 * k)))
        rect.center = self.P(cx, cy)
        pygame.draw.ellipse(self.s, c, rect, int(width * k) if width else 0)

    def rect(self, c, x, y, w, h, r=0, width=0):
        k = self.k
        px, py = self.P(x, y)
        pygame.draw.rect(self.s, c, (px, py, max(1, int(w * k)), max(1, int(h * k))),
                         int(width * k) if width else 0, border_radius=int(r * k))

    def poly(self, c, pts, width=0):
        pygame.draw.polygon(self.s, c, [self.P(x, y) for x, y in pts], int(width * self.k) if width else 0)

    def line(self, c, a, b, w):
        self.capsule(c, a, b, w / 2)

    def capsule(self, c, a, b, r):
        k = self.k
        pa, pb = self.P(*a), self.P(*b)
        pygame.draw.line(self.s, c, pa, pb, max(1, int(r * 2 * k)))
        pygame.draw.circle(self.s, c, pa, max(1, int(r * k)))
        pygame.draw.circle(self.s, c, pb, max(1, int(r * k)))

    def polyline(self, c, pts, w):
        for a, b in zip(pts, pts[1:]):
            self.capsule(c, a, b, w / 2)

    def arc(self, c, cx, cy, r, a0, a1, w, steps=24):
        pts = [(cx + math.cos(a0 + (a1 - a0) * i / steps) * r, cy + math.sin(a0 + (a1 - a0) * i / steps) * r)
               for i in range(steps + 1)]
        self.polyline(c, pts, w)

    def overlay(self, fn, alpha):
        """Run fn(pen) on a temporary layer and blend it at the given alpha (for gloss/shade)."""
        layer = pygame.Surface(self.s.get_size(), pygame.SRCALPHA)
        fn(Pen(layer, self.k, self.ox, self.oy))
        layer.fill((255, 255, 255, int(alpha * 255)), special_flags=pygame.BLEND_RGBA_MULT)
        self.s.blit(layer, (0, 0))


def sprite(w, h, draw, k=SS):
    """Create a w x h sprite drawn by draw(pen) at k-times size and smoothly scaled down."""
    big = pygame.Surface((max(1, int(w * k)), max(1, int(h * k))), pygame.SRCALPHA)
    draw(Pen(big, k))
    return pygame.transform.smoothscale(big, (max(1, int(w)), max(1, int(h))))


# ---------------- panels, gradients, shadows ----------------

def vgrad(w, h, top, bottom):
    surf = pygame.Surface((1, 2))
    surf.set_at((0, 0), top)
    surf.set_at((0, 1), bottom)
    return pygame.transform.smoothscale(surf, (max(1, int(w)), max(1, int(h))))


def vgrad_n(w, h, stops):
    """Vertical gradient through several colours."""
    out = pygame.Surface((int(w), int(h)))
    n = len(stops) - 1
    for i in range(n):
        y0, y1 = int(h * i / n), int(h * (i + 1) / n)
        out.blit(vgrad(w, max(1, y1 - y0), stops[i], stops[i + 1]), (0, y0))
    return out


@lru_cache(maxsize=256)
def rounded(w, h, r, color, border=0, border_color=None, grad_to=None, k=2):
    w, h = int(w), int(h)
    big = pygame.Surface((w * k, h * k), pygame.SRCALPHA)
    if border and border_color:
        pygame.draw.rect(big, border_color, (0, 0, w * k, h * k), border_radius=r * k)
        inner = pygame.Rect(border * k, border * k, (w - 2 * border) * k, (h - 2 * border) * k)
        ir = max(0, (r - border) * k)
    else:
        inner = pygame.Rect(0, 0, w * k, h * k)
        ir = r * k
    if grad_to:
        mask = pygame.Surface(inner.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=ir)
        g = vgrad(inner.w, inner.h, color, grad_to).convert_alpha()
        g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        big.blit(g, inner.topleft)
    else:
        pygame.draw.rect(big, color, inner, border_radius=ir)
    return pygame.transform.smoothscale(big, (w, h))


def rrect(surface, rect, color, r=12, border=0, border_color=None, grad_to=None, alpha=255):
    rect = pygame.Rect(rect)
    if rect.w <= 0 or rect.h <= 0:
        return
    img = rounded(rect.w, rect.h, int(r), tuple(color), int(border), border_color and tuple(border_color),
                  grad_to and tuple(grad_to))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surface.blit(img, rect.topleft)


@lru_cache(maxsize=128)
def soft_shadow(w, h, r, blur=14, strength=90):
    w, h = int(w), int(h)
    pad = blur * 2
    base = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    pygame.draw.rect(base, (60, 10, 50, strength), (pad, pad, w, h), border_radius=r)
    small = pygame.transform.smoothscale(base, (max(1, base.get_width() // 8), max(1, base.get_height() // 8)))
    return pygame.transform.smoothscale(small, base.get_size()), pad


def shadow(surface, rect, r=16, blur=14, strength=90, dy=8):
    rect = pygame.Rect(rect)
    img, pad = soft_shadow(rect.w, rect.h, r, blur, strength)
    surface.blit(img, (rect.x - pad, rect.y - pad + dy))


@lru_cache(maxsize=64)
def circle_sprite(r, color, border=0, border_color=None):
    def draw(p):
        if border:
            p.circle(border_color, r, r, r)
            p.circle(color, r, r, r - border)
        else:
            p.circle(color, r, r, r)
    return sprite(r * 2, r * 2, draw)


def aa_circle(surface, color, center, r, border=0, border_color=None, alpha=255):
    r = max(1, int(r))
    img = circle_sprite(r, tuple(color), border, border_color and tuple(border_color))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surface.blit(img, (int(center[0] - r), int(center[1] - r)))


def dim(surface, color=(58, 24, 56), alpha=130):
    veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    veil.fill((*color, alpha))
    surface.blit(veil, (0, 0))


def blur(surface, factor=6):
    w, h = surface.get_size()
    small = pygame.transform.smoothscale(surface, (max(1, w // factor), max(1, h // factor)))
    return pygame.transform.smoothscale(small, (w, h))


def star_points(cx, cy, r, inner=0.48):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    return pts
