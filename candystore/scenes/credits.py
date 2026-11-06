"""Credits screen and the full GNU GPL v3 licence viewer."""
import datetime
import os
import webbrowser

import pygame

from .. import CREATOR, EMAIL, RELEASE_DATE, TITLE, WEBSITE, __version__, art, gfx, ui
from ..app import W, H, Scene
from ..paths import root


def release_date_text():
    d = datetime.date.fromisoformat(RELEASE_DATE)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


class LinkLabel:
    def __init__(self, center, label, url, size=20):
        self.label, self.url, self.size = label, url, size
        w, h = gfx.font(size).size(label)
        self.rect = pygame.Rect(0, 0, w, h + 4)
        self.rect.center = center
        self.hover = False

    def handle(self, event, app):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos):
            app.audio.play("click")
            if not app.smoke:
                try:
                    webbrowser.open(self.url)
                except Exception:  # noqa: BLE001 - no browser is fine
                    pass
            return True
        return False

    def draw(self, surface, t):
        col = gfx.PINK_D if self.hover else gfx.PURPLE_D
        r = gfx.text(surface, self.label, self.rect.center, self.size, col)
        pygame.draw.line(surface, col, (r.left, r.bottom - 2), (r.right, r.bottom - 2), 2)


class CreditsScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.backdrop = art.TitleBackdrop()
        self.dt = 0.0
        self.panel = pygame.Rect(0, 0, 820, 610)
        self.panel.center = (W // 2, H // 2 + 14)
        p = self.panel
        self.widgets = [
            LinkLabel((p.centerx, p.top + 302), WEBSITE, WEBSITE, 20),
            LinkLabel((p.centerx, p.top + 336), EMAIL, f"mailto:{EMAIL}", 20),
            ui.Button((p.centerx - 230, p.bottom - 74, 220, 52), "View License", self.license, "purple", 20),
            ui.Button((p.centerx + 10, p.bottom - 74, 220, 52), "Back", self.back, "pink", 20),
        ]

    def back(self):
        from .title import TitleScene
        self.app.switch(TitleScene(self.app))

    def license(self):
        self.app.switch(LicenseScene(self.app))

    def handle_world(self, event):
        for w in self.widgets:
            if w.handle(event, self.app):
                return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()

    def update_world(self, dt, paused):
        self.dt = dt

    def draw_world(self, surface):
        t = self.app.time
        self.backdrop.draw(surface, t, self.dt)
        p = self.panel
        ui.draw_panel(surface, p, "Credits", "purple")
        cx = p.centerx
        gfx.text(surface, TITLE, (cx, p.top + 66), 34, gfx.PINK_D)
        gfx.text(surface, f"Version v{__version__}  ·  Released {release_date_text()}", (cx, p.top + 102), 18, gfx.INK, bold=False)
        y = p.top + 146
        for head, body in (("Created by", CREATOR), ("Made with", "Claude Code (Anthropic)")):
            gfx.text(surface, head, (cx, y), 16, gfx.INK_SOFT, bold=False)
            gfx.text(surface, body, (cx, y + 26), 26, gfx.INK)
            y += 66
        gfx.text(surface, "Shouku Games", (cx, p.top + 274), 18, gfx.INK_SOFT)
        ui.chip(surface, "Recommended for ages 10+", (cx, p.top + 384), "info", 16)
        gfx.text(surface, "License: GNU General Public License v3.0 (GPL-3.0)", (cx, p.top + 428), 18, gfx.INK)
        gfx.paragraph(surface, "This game is free software: you can share and change it under the terms of the GPL v3. "
                               "It comes with ABSOLUTELY NO WARRANTY.", (cx, p.top + 446), 14, 640, gfx.INK_SOFT)
        gfx.text(surface, "Font: Fredoka (SIL Open Font License)  ·  Music & sound: original, made in code",
                 (cx, p.top + 500), 13, gfx.INK_SOFT, bold=False)
        for i, k in enumerate(("lolli", "gummy", "choc")):
            art.blit_candy(surface, k, (p.left + 70, p.top + 150 + i * 90), 70, i)
        for i, k in enumerate(("ice", "jaw", "cotton")):
            art.blit_candy(surface, k, (p.right - 70, p.top + 150 + i * 90), 70, i)
        for w in self.widgets:
            w.draw(surface, t)


def read_license():
    for path in (os.path.join(root(), "LICENSE"), os.path.join(root(), "COPYING")):
        try:
            with open(path, encoding="utf-8") as handle:
                return handle.read()
        except OSError:
            continue
    return "GNU GENERAL PUBLIC LICENSE Version 3.\nSee https://www.gnu.org/licenses/gpl-3.0.html"


class LicenseScene(Scene):
    music = "title"
    LINE_H = 21

    def __init__(self, app):
        super().__init__(app)
        self.panel = pygame.Rect(0, 0, 900, 640)
        self.panel.center = (W // 2, H // 2 + 20)
        self.view = pygame.Rect(self.panel.left + 40, self.panel.top + 60, self.panel.w - 100, self.panel.h - 150)
        self.lines = []
        # join the licence's hard-wrapped lines into paragraphs, then wrap them to the panel width
        for para in read_license().replace("\r", "").split("\n\n"):
            text = " ".join(line.strip() for line in para.splitlines() if line.strip())
            if text:
                self.lines.extend(gfx.wrap(text, 15, self.view.w - 10, bold=False))
            self.lines.append("")
        self.scroll = 0.0
        self.drag = None
        self.back_btn = ui.Button((self.panel.centerx - 90, self.panel.bottom - 72, 180, 50), "Back", self.back, "pink", 20)
        self.bg = None

    @property
    def max_scroll(self):
        return max(0, len(self.lines) * self.LINE_H - self.view.h)

    def back(self):
        self.app.switch(CreditsScene(self.app))

    def handle_world(self, event):
        if self.back_btn.handle(event, self.app):
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y * 60
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.back()
            step = {pygame.K_DOWN: 40, pygame.K_UP: -40, pygame.K_PAGEDOWN: self.view.h - 40,
                    pygame.K_PAGEUP: -(self.view.h - 40), pygame.K_HOME: -10 ** 6, pygame.K_END: 10 ** 6}.get(event.key)
            if step:
                self.scroll += step
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._bar().inflate(20, 0).collidepoint(event.pos):
            self.drag = (event.pos[1], self.scroll)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.drag = None
        elif event.type == pygame.MOUSEMOTION and self.drag:
            track = self.view.h - self._thumb_h()
            if track > 0:
                self.scroll = self.drag[1] + (event.pos[1] - self.drag[0]) / track * self.max_scroll
        self.scroll = max(0, min(self.max_scroll, self.scroll))

    def _thumb_h(self):
        total = len(self.lines) * self.LINE_H
        return max(40, self.view.h * self.view.h / max(1, total))

    def _bar(self):
        return pygame.Rect(self.view.right + 18, self.view.top, 12, self.view.h)

    def draw_world(self, surface):
        if self.bg is None:
            self.bg = gfx.vgrad_n(W, H, [(255, 159, 208), (255, 201, 227), (255, 231, 184)]).convert()
        surface.blit(self.bg, (0, 0))
        p = self.panel
        ui.draw_panel(surface, p, "GNU GPL v3.0 License", "purple")
        clip = surface.get_clip()
        surface.set_clip(self.view)
        first = int(self.scroll // self.LINE_H)
        y = self.view.top - (self.scroll % self.LINE_H)
        for line in self.lines[first:first + self.view.h // self.LINE_H + 2]:
            if line:
                gfx.text(surface, line, (self.view.left, y), 15, gfx.INK, anchor="topleft", bold=False)
            y += self.LINE_H
        surface.set_clip(clip)
        bar = self._bar()
        gfx.rrect(surface, bar, (243, 225, 236), 6)
        th = self._thumb_h()
        ty = bar.top + (bar.h - th) * (self.scroll / self.max_scroll if self.max_scroll else 0)
        gfx.rrect(surface, (bar.x, int(ty), bar.w, int(th)), (255, 179, 212), 6)
        self.back_btn.draw(surface, self.app.time)
