"""Title screen: animated candy rain, the logo, the main menu, the language toggle and the ages 10+ badge."""
import pygame

from .. import RELEASE_DATE, __version__, art, gfx, i18n, storage, ui
from ..app import W, H, Scene
from ..i18n import t
from .panels import HowToOverlay, NameOverlay, SavesOverlay, SettingsOverlay


class LanguageToggle:
    """Two-part switch: English | 日本語. The active language is highlighted."""

    def __init__(self, scene, topright):
        self.scene = scene
        self.parts = []
        x = topright[0]
        for code, label in reversed((("en", "English"), ("ja", "日本語"))):
            w = 116
            x -= w
            self.parts.insert(0, (code, label, pygame.Rect(x, topright[1], w, 44)))
        self.hover = None

    def handle(self, event, app):
        if event.type == pygame.MOUSEMOTION:
            self.hover = next((c for c, _l, r in self.parts if r.collidepoint(event.pos)), None)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for code, _label, r in self.parts:
                if r.collidepoint(event.pos):
                    app.audio.play("click")
                    self.scene.set_language(code)
                    return True
        return False

    def draw(self, surface, tm):
        first, last = self.parts[0][2], self.parts[-1][2]
        outer = first.union(last).inflate(10, 10)
        gfx.rrect(surface, outer.move(0, 5), gfx.PURPLE_D, outer.h // 2)
        gfx.rrect(surface, outer, (255, 255, 255), outer.h // 2)
        for code, label, r in self.parts:
            active = i18n.lang() == code
            if active:
                gfx.rrect(surface, r, (143, 117, 255), r.h // 2, grad_to=(99, 66, 240))
            elif self.hover == code:
                gfx.rrect(surface, r, (237, 232, 255), r.h // 2)
            # each label in its own script's font so both always read correctly
            gfx.text(surface, label, r.center, 19, (255, 255, 255) if active else gfx.PURPLE_D, latin=(code == "en"))
        gfx.text(surface, t("language"), (outer.centerx, outer.bottom + 16), 14, gfx.INK, bold=False)


class TitleScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.backdrop = art.TitleBackdrop()
        self.dt = 0.0
        self.lang_toggle = LanguageToggle(self, (W - 22, 20))
        self.build()

    def build(self):
        self.buttons = []
        items = [("new_game", self.new_game, "pink"), ("tutorial", self.tutorial, "mint"),
                 ("load_game", self.load_menu, "mint"),
                 ("how_to_play", lambda: self.push_overlay(HowToOverlay(self)), "purple"),
                 ("settings", lambda: self.push_overlay(SettingsOverlay(self)), "yellow"),
                 ("credits", self.credits, "white"), ("quit", self.quit, "white")]
        y = 234 + (24 if i18n.lang() == "ja" else 0)
        for i, (key, fn, style) in enumerate(items):
            if i >= 5:
                x = 640 - 150 + (i - 5) * 156
                self.buttons.append(ui.Button((x, y + 2, 144, 48), t(key), fn, style, 20))
            else:
                self.buttons.append(ui.Button((640 - 150, y, 300, 52), t(key), fn, style, 23, radius=17))
                y += 62 if i18n.lang() == "en" else 60
        self.buttons[1].pulse = not self.app.settings.get("tutorial_seen")

    def set_language(self, code):
        if code == i18n.lang():
            return
        i18n.set_lang(code)
        self.app.settings["language"] = code
        self.app.save_settings()
        self.build()

    def new_game(self):
        self.push_overlay(NameOverlay(self, self.start_game))

    def start_game(self, name):
        from .game import GameScene
        self.clear_overlays()
        self.app.switch(GameScene(self.app, shop_name=name))

    def load_menu(self):
        self.push_overlay(SavesOverlay(self, "load", self.load_slot))

    def load_slot(self, n):
        from .game import GameScene
        data = storage.read_slot(n)
        if not data:
            self.toast(t("slot_empty"), "bad")
            return
        self.clear_overlays()
        self.app.switch(GameScene(self.app, state=data["state"], loaded_from=n))

    def tutorial(self):
        from .tutorial import TutorialScene
        self.app.settings["tutorial_seen"] = True
        self.app.save_settings()
        self.app.switch(TutorialScene(self.app))

    def credits(self):
        from .credits import CreditsScene
        self.app.switch(CreditsScene(self.app))

    def quit(self):
        self.app.running = False

    def handle_world(self, event):
        if self.lang_toggle.handle(event, self.app):
            return
        for b in self.buttons:
            if b.handle(event, self.app):
                return

    def update_world(self, dt, paused):
        self.dt = dt

    def draw_world(self, surface):
        tm = self.app.time
        self.backdrop.draw(surface, tm, self.dt)
        art.draw_logo(surface, 640, 24, tm)
        if i18n.lang() == "ja":
            gfx.text(surface, t("title_ja"), (640, 222), 24, (255, 255, 255), stroke=gfx.PINK_D, stroke_w=3)
        for b in self.buttons:
            b.draw(surface, tm)
        self.lang_toggle.draw(surface, tm)
        # ages 10+ badge
        badge = pygame.Rect(W - 300, H - 104, 276, 80)
        gfx.rrect(surface, badge.move(0, 5), gfx.PURPLE_D, 18)
        gfx.rrect(surface, badge, gfx.PURPLE, 18)
        gfx.rrect(surface, badge.inflate(-8, -8), (255, 255, 255), 14)
        tile = pygame.Rect(badge.left + 10, badge.top + 10, 60, 60)
        gfx.rrect(surface, tile, (143, 117, 255), 13, grad_to=(99, 66, 240))
        gfx.text(surface, "10+", tile.center, 28, (255, 255, 255), latin=True)
        gfx.text(surface, t("ages_line1"), (tile.right + 12, badge.top + 28), 17, gfx.INK, anchor="midleft", bold=False)
        gfx.text(surface, t("ages_line2"), (tile.right + 12, badge.top + 52), 17, gfx.INK, anchor="midleft")
        # version line
        gfx.rrect(surface, (22, H - 66, 300, 44), (255, 255, 255), 14, alpha=215)
        gfx.text(surface, f"v{__version__}  ·  Shouku Games  ·  {RELEASE_DATE}", (172, H - 44), 15, gfx.INK, bold=False,
                 latin=True)
