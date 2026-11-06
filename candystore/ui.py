"""Widgets: candy buttons, panels, chips, stars, sliders, text input and toasts."""
import math
from functools import lru_cache

import pygame

from . import art, gfx
from .gfx import darken, lighten

STYLES = {
    "pink": (gfx.PINK, gfx.PINK_D, (255, 255, 255)),
    "purple": (gfx.PURPLE, gfx.PURPLE_D, (255, 255, 255)),
    "mint": (gfx.MINT, gfx.MINT_D, (255, 255, 255)),
    "yellow": (gfx.YELLOW, gfx.YELLOW_D, (107, 67, 0)),
    "white": ((255, 255, 255), (226, 184, 207), gfx.INK),
    "red": (gfx.RED, gfx.RED_D, (255, 255, 255)),
    "grey": ((200, 190, 198), (160, 148, 158), (255, 255, 255)),
}


@lru_cache(maxsize=256)
def button_face(w, h, style, radius, pressed):
    c, cd, _tc = STYLES[style]
    depth = 5
    s = pygame.Surface((w, h + depth), pygame.SRCALPHA)
    if not pressed:
        gfx.rrect(s, (0, depth, w, h), cd, radius)
    oy = depth - 1 if pressed else 0
    gfx.rrect(s, (0, oy, w, h), cd, radius)
    gfx.rrect(s, (3, oy + 3, w - 6, h - 6), lighten(c, 0.3), max(2, radius - 3), grad_to=c)
    hl = gfx.rounded(max(2, w - 16), max(2, int(h * 0.32)), max(1, radius - 6), (255, 255, 255))
    hl = hl.copy()
    hl.set_alpha(70)
    s.blit(hl, (8, oy + 5))
    return s


class Button:
    def __init__(self, rect, label, on_click=None, style="pink", size=20, icon=None, enabled=True, sound="click",
                 radius=16, tag=None):
        self.rect = pygame.Rect(rect)
        self.label, self.on_click, self.style, self.size = label, on_click, style, size
        self.icon, self.enabled, self.sound, self.radius, self.tag = icon, enabled, sound, radius, tag
        self.hover = self.down = False
        self.pulse = False

    def handle(self, event, app):
        if event.type == pygame.MOUSEMOTION:
            was = self.hover
            self.hover = self.rect.collidepoint(event.pos)
            if self.hover and not was and self.enabled:
                app.audio.play("hover")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            if self.enabled:
                self.down = True
            else:
                app.audio.play("error")
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            hit = self.down and self.rect.collidepoint(event.pos)
            self.down = False
            if hit and self.enabled:
                if self.sound:
                    app.audio.play(self.sound)
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface, t=0.0):
        style = self.style if self.enabled else "grey"
        pressed = self.down and self.hover
        r = self.rect
        scale = 1.0
        if self.pulse and self.enabled and not pressed:
            scale = 1 + 0.035 * (0.5 + 0.5 * math.sin(t * 5))
        face = button_face(r.w, r.h, style, self.radius, pressed)
        lift = -1 if (self.hover and self.enabled and not pressed) else 0
        if scale != 1.0:
            face = pygame.transform.smoothscale(face, (int(face.get_width() * scale), int(face.get_height() * scale)))
        fr = face.get_rect(center=(r.centerx, r.centery + 2 + lift))
        surface.blit(face, fr)
        tc = STYLES[style][2]
        cy = r.centery + lift + (4 if pressed else 0)
        shadow = None if style in ("white", "yellow") else darken(STYLES[style][0], 0.35)
        if self.icon:
            ic = self.icon
            if self.label:
                tw = gfx.font(self.size).size(self.label)[0]
                total = ic.get_width() + 8 + tw
                x0 = r.centerx - total / 2
                surface.blit(ic, (x0, cy - ic.get_height() / 2))
                gfx.text(surface, self.label, (x0 + ic.get_width() + 8, cy), self.size, tc, anchor="midleft", shadow=shadow)
            else:
                surface.blit(ic, ic.get_rect(center=(r.centerx, cy)))
        else:
            gfx.text(surface, self.label, (r.centerx, cy), self.size, tc, shadow=shadow)


def draw_panel(surface, rect, title=None, color="pink"):
    rect = pygame.Rect(rect)
    gfx.shadow(surface, rect, 30, 22, 110, 14)
    gfx.rrect(surface, rect.inflate(8, 8), (255, 179, 212), 32)
    gfx.rrect(surface, rect, (255, 255, 255), 28)
    gfx.rrect(surface, rect.inflate(-10, -10), gfx.CREAM, 24)
    if title:
        ribbon(surface, title, (rect.centerx, rect.top), color)


RIBBON = {"pink": ((255, 122, 181), (255, 79, 151), gfx.PINK_D), "purple": ((143, 117, 255), (99, 66, 240), gfx.PURPLE_D),
          "mint": ((69, 220, 189), (24, 179, 148), gfx.MINT_D), "dark": ((138, 90, 122), (90, 36, 72), (58, 24, 56))}


@lru_cache(maxsize=32)
def ribbon_img(title, color):
    top, bottom, dark = RIBBON[color]
    f = gfx.font(30)
    w = f.size(title)[0] + 56
    s = pygame.Surface((w, 60), pygame.SRCALPHA)
    gfx.rrect(s, (0, 6, w, 52), dark, 18)
    gfx.rrect(s, (0, 0, w, 52), (255, 255, 255), 18)
    gfx.rrect(s, (4, 4, w - 8, 44), top, 15, grad_to=bottom)
    gfx.text(s, title, (w / 2, 26), 30, (255, 255, 255), shadow=dark)
    return s


def ribbon(surface, title, midtop, color="pink"):
    img = ribbon_img(title, color)
    surface.blit(img, img.get_rect(center=(midtop[0], midtop[1] + 2)))


CHIP = {"good": ((236, 253, 248), (155, 232, 214), gfx.GREEN_TXT), "bad": ((255, 240, 240), (255, 179, 179), (198, 40, 40)),
        "info": ((245, 242, 255), (214, 204, 255), gfx.PURPLE_D), "plain": ((255, 255, 255), (255, 208, 228), gfx.INK)}


def chip(surface, label, center, kind="plain", size=15):
    bg, border, tc = CHIP[kind]
    w = gfx.font(size).size(label)[0] + 28
    r = pygame.Rect(0, 0, w, size + 16)
    r.center = center
    gfx.rrect(surface, r, border, r.h // 2)
    gfx.rrect(surface, r.inflate(-4, -4), bg, r.h // 2 - 2)
    gfx.text(surface, label, r.center, size, tc)
    return r


def chips_row(surface, items, center_x, y, size=15, gap=8, max_w=600):
    widths = [gfx.font(size).size(lbl)[0] + 28 for _k, lbl in items]
    rows, row, rw = [], [], 0
    for item, w in zip(items, widths):
        if row and rw + w + gap > max_w:
            rows.append((row, rw))
            row, rw = [], 0
        row.append((item, w))
        rw += w + (gap if row[:-1] else 0)
    if row:
        rows.append((row, rw))
    for row, rw in rows:
        x = center_x - rw / 2
        for (kind, lbl), w in row:
            chip(surface, lbl, (x + w / 2, y), kind, size)
            x += w + gap
        y += size + 24
    return y


def stars(surface, rep, pos, size=20, gap=2):
    x, y = pos
    full = art.star(size // 2)
    empty = art.star(size // 2, (241, 220, 231), (216, 184, 200))
    for i in range(5):
        f = max(0.0, min(1.0, rep - i))
        surface.blit(empty, (x, y))
        if f > 0:
            w = int(full.get_width() * f)
            surface.blit(full, (x, y), (0, 0, w, full.get_height()))
        x += full.get_width() + gap
    return x


def pill(surface, rect, color=(255, 255, 255), border=(255, 179, 212)):
    rect = pygame.Rect(rect)
    gfx.rrect(surface, rect.move(0, 4), (230, 140, 180), rect.h // 2)
    gfx.rrect(surface, rect, border, rect.h // 2)
    gfx.rrect(surface, rect.inflate(-6, -6), color, rect.h // 2 - 3)


def meter(surface, rect, frac, color=gfx.MINT, label=None):
    rect = pygame.Rect(rect)
    gfx.rrect(surface, rect, (236, 198, 219), rect.h // 2)
    gfx.rrect(surface, rect.inflate(-4, -4), (243, 225, 236), rect.h // 2 - 2)
    fw = int((rect.w - 4) * max(0.0, min(1.0, frac)))
    if fw > rect.h - 4:
        gfx.rrect(surface, (rect.x + 2, rect.y + 2, fw, rect.h - 4), color, rect.h // 2 - 2, grad_to=lighten(color, 0.35))
    if label:
        gfx.text(surface, label, rect.center, max(11, rect.h - 6), gfx.INK)


class Slider:
    def __init__(self, rect, value, on_change):
        self.rect = pygame.Rect(rect)
        self.value, self.on_change = value, on_change
        self.drag = False

    def handle(self, event, app):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.inflate(20, 20).collidepoint(event.pos):
            self.drag = True
            self._set(event.pos[0])
            return True
        if event.type == pygame.MOUSEMOTION and self.drag:
            self._set(event.pos[0])
            return True
        if event.type == pygame.MOUSEBUTTONUP and self.drag:
            self.drag = False
            app.audio.play("coin")
            return True
        return False

    def _set(self, x):
        self.value = max(0.0, min(1.0, (x - self.rect.x) / self.rect.w))
        self.on_change(self.value)

    def draw(self, surface, t=0.0):
        meter(surface, (self.rect.x, self.rect.centery - 8, self.rect.w, 16), self.value, gfx.PINK)
        kx = self.rect.x + self.rect.w * self.value
        gfx.aa_circle(surface, (255, 255, 255), (kx, self.rect.centery), 14, 3, gfx.PINK_D)


class TextInput:
    """Single-line text box. Supports Japanese input methods (IME): the text being composed is shown underlined."""

    def __init__(self, rect, value="", max_len=22):
        self.rect = pygame.Rect(rect)
        self.value, self.max_len = value, max_len
        self.select_all = True
        self.composing = ""

    def ime_rect(self, app):
        """Tell the input method where the box is (window coordinates) so its candidate list appears beside it."""
        try:
            scale, ox, oy = app._transform()
            r = self.rect
            pygame.key.set_text_input_rect(pygame.Rect(int(ox + r.x * scale), int(oy + r.bottom * scale),
                                                       int(r.w * scale), 10))
        except (pygame.error, AttributeError):
            pass

    def handle(self, event, app):
        if event.type == pygame.TEXTEDITING:
            self.composing = event.text
            if event.text and self.select_all:
                self.value, self.select_all = "", False
            return True
        if event.type == pygame.TEXTINPUT:
            self.composing = ""
            if self.select_all:
                self.value, self.select_all = "", False
            self.value = (self.value + event.text)[: self.max_len]
            return True
        if event.type == pygame.KEYDOWN:
            if self.composing:
                return True            # keys belong to the input method while composing
            if event.key == pygame.K_BACKSPACE:
                self.value = "" if self.select_all else self.value[:-1]
                self.select_all = False
                return True
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_END, pygame.K_HOME):
                self.select_all = False
                return True
        return False

    def draw(self, surface, t=0.0):
        gfx.rrect(surface, self.rect, gfx.PINK, 18)
        gfx.rrect(surface, self.rect.inflate(-8, -8), (255, 255, 255), 14)
        f = gfx.font(28)
        shown = self.value + self.composing
        if self.select_all and self.value:
            tw = f.size(self.value)[0]
            gfx.rrect(surface, (self.rect.centerx - tw / 2 - 4, self.rect.centery - 18, tw + 8, 36), (255, 214, 234), 8)
        r = gfx.text(surface, shown, self.rect.center, 28, gfx.INK)
        if self.composing:
            cw = f.size(self.composing)[0]
            pygame.draw.line(surface, gfx.PURPLE, (r.right - cw, r.bottom - 6), (r.right, r.bottom - 6), 2)
        if int(t * 2) % 2 == 0 and not self.select_all:
            x = r.right + 3 if shown else self.rect.centerx
            pygame.draw.line(surface, gfx.PINK_D, (x, self.rect.centery - 14), (x, self.rect.centery + 14), 3)


class Toasts:
    def __init__(self):
        self.items = []

    def add(self, text, kind=""):
        self.items.append([text, kind, 3.0])
        self.items = self.items[-4:]

    def update(self, dt):
        for it in self.items:
            it[2] -= dt
        self.items = [it for it in self.items if it[2] > 0]

    def draw(self, surface, bottom=628):
        y = bottom
        for text, kind, life in reversed(self.items):
            border, shade = {"bad": (gfx.RED, gfx.RED_D), "good": (gfx.MINT, gfx.MINT_D)}.get(kind, (gfx.PURPLE, gfx.PURPLE_D))
            w = gfx.font(18).size(text)[0] + 40
            appear = min(1.0, (3.0 - life) * 6)
            fade = min(1.0, life * 2.5)
            r = pygame.Rect(0, 0, w, 42)
            r.midbottom = (640, y + (1 - appear) * 16)
            a = int(255 * fade)
            gfx.rrect(surface, r.move(0, 4), shade, 16, alpha=a)
            gfx.rrect(surface, r, border, 16, alpha=a)
            gfx.rrect(surface, r.inflate(-6, -6), (255, 255, 255), 13, alpha=a)
            gfx.text(surface, text, r.center, 18, gfx.INK, alpha=a)
            y -= 50


def icon_surface(kind, size=26, color=(255, 255, 255)):
    return _icon(kind, size, color)


@lru_cache(maxsize=64)
def _icon(kind, size, color):
    def d(p):
        u = size / 24
        if kind == "cart":
            p.polyline(color, [(2 * u, 4 * u), (5 * u, 4 * u), (7.5 * u, 15 * u), (18.5 * u, 15 * u), (21 * u, 7 * u), (6.5 * u, 7 * u)], 2.4 * u)
            p.circle(color, 9 * u, 19.5 * u, 2 * u)
            p.circle(color, 17 * u, 19.5 * u, 2 * u)
        elif kind == "shelf":
            p.rect(color, 3 * u, 2 * u, 18 * u, 20 * u, 2 * u, 2.2 * u)
            p.line(color, (3 * u, 9 * u), (21 * u, 9 * u), 2.2 * u)
            p.line(color, (3 * u, 15.5 * u), (21 * u, 15.5 * u), 2.2 * u)
            p.circle(color, 8 * u, 6 * u, 1.8 * u)
            p.circle(color, 13 * u, 6 * u, 1.8 * u)
        elif kind == "door":
            p.rect(color, 6 * u, 3 * u, 12 * u, 19 * u, 1.5 * u, 2.2 * u)
            p.line(color, (3 * u, 21.5 * u), (21 * u, 21.5 * u), 2.2 * u)
            p.circle(color, 15 * u, 12.5 * u, 1.6 * u)
        elif kind == "save":
            p.rect(gfx.PURPLE_D, 3 * u, 2 * u, 18 * u, 20 * u, 3 * u)
            p.rect(gfx.PURPLE, 4.5 * u, 3.5 * u, 15 * u, 17 * u, 2 * u)
            p.rect((255, 255, 255), 7 * u, 3.5 * u, 9 * u, 6 * u)
            p.rect((255, 255, 255), 7 * u, 13 * u, 10 * u, 6 * u, 1 * u)
            p.rect(gfx.PURPLE_D, 12.5 * u, 4.5 * u, 2 * u, 4 * u)
        elif kind == "music":
            p.polyline(gfx.PINK, [(9 * u, 18 * u), (9 * u, 5 * u), (20 * u, 3 * u), (20 * u, 16 * u)], 2.4 * u)
            p.circle(gfx.PINK, 6.5 * u, 18 * u, 3 * u)
            p.circle(gfx.PINK, 17.5 * u, 16 * u, 3 * u)
        elif kind == "music_off":
            p.polyline((190, 170, 182), [(9 * u, 18 * u), (9 * u, 5 * u), (20 * u, 3 * u), (20 * u, 16 * u)], 2.4 * u)
            p.circle((190, 170, 182), 6.5 * u, 18 * u, 3 * u)
            p.circle((190, 170, 182), 17.5 * u, 16 * u, 3 * u)
            p.line(gfx.RED, (3 * u, 3 * u), (21 * u, 21 * u), 2.6 * u)
        elif kind == "menu":
            for y in (6, 12, 18):
                p.line(gfx.INK, (4 * u, y * u), (20 * u, y * u), 2.6 * u)
        elif kind == "coin":
            pass
        elif kind == "box":
            p.poly((156, 102, 48), [(3 * u, 8 * u), (12 * u, 4 * u), (21 * u, 8 * u), (21 * u, 18 * u), (12 * u, 22 * u), (3 * u, 18 * u)])
            p.poly((224, 169, 109), [(4.5 * u, 9 * u), (12 * u, 5.6 * u), (19.5 * u, 9 * u), (19.5 * u, 17 * u), (12 * u, 20.4 * u), (4.5 * u, 17 * u)])
            p.poly((240, 192, 140), [(4.5 * u, 9 * u), (12 * u, 5.6 * u), (19.5 * u, 9 * u), (12 * u, 12.4 * u)])
        elif kind == "clock":
            p.circle(gfx.PURPLE, 12 * u, 12 * u, 11 * u)
            p.circle((255, 255, 255), 12 * u, 12 * u, 8.6 * u)
            p.polyline(gfx.PURPLE, [(12 * u, 6 * u), (12 * u, 12 * u), (16 * u, 14 * u)], 2.2 * u)
    if kind == "coin":
        return pygame.transform.smoothscale(art.coin(24), (size, size))
    return gfx.sprite(size, size, d)
