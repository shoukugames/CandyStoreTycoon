"""Title screen: animated candy rain, the logo, the main menu, the ages 10+ badge."""
import pygame

from .. import RELEASE_DATE, __version__, art, gfx, storage, ui
from ..app import W, H, Scene
from .panels import HowToOverlay, NameOverlay, SavesOverlay, SettingsOverlay


class TitleScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.backdrop = art.TitleBackdrop()
        self.dt = 0.0
        self.buttons = []
        items = [("New Game", self.new_game, "pink"), ("Load Game", self.load_menu, "mint"),
                 ("How to Play", lambda: self.push_overlay(HowToOverlay(self)), "purple"),
                 ("Settings", lambda: self.push_overlay(SettingsOverlay(self)), "yellow"),
                 ("Credits", self.credits, "white"), ("Quit", self.quit, "white")]
        y = 236
        for i, (label, fn, style) in enumerate(items):
            if i >= 4:
                x = 640 - 150 + (i - 4) * 156
                self.buttons.append(ui.Button((x, y, 144, 52), label, fn, style, 21))
            else:
                self.buttons.append(ui.Button((640 - 150, y, 300, 58), label, fn, style, 25, radius=18))
                y += 72

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
            self.toast("That save slot is empty.", "bad")
            return
        self.clear_overlays()
        self.app.switch(GameScene(self.app, state=data["state"], loaded_from=n))

    def credits(self):
        from .credits import CreditsScene
        self.app.switch(CreditsScene(self.app))

    def quit(self):
        self.app.running = False

    def handle_world(self, event):
        for b in self.buttons:
            if b.handle(event, self.app):
                return

    def update_world(self, dt, paused):
        self.dt = dt

    def draw_world(self, surface):
        t = self.app.time
        self.backdrop.draw(surface, t, self.dt)
        art.draw_logo(surface, 640, 24, t)
        for b in self.buttons:
            b.draw(surface, t)
        # ages 10+ badge
        badge = pygame.Rect(W - 300, H - 104, 276, 80)
        gfx.rrect(surface, badge.move(0, 5), gfx.PURPLE_D, 18)
        gfx.rrect(surface, badge, gfx.PURPLE, 18)
        gfx.rrect(surface, badge.inflate(-8, -8), (255, 255, 255), 14)
        tile = pygame.Rect(badge.left + 10, badge.top + 10, 60, 60)
        gfx.rrect(surface, tile, (143, 117, 255), 13, grad_to=(99, 66, 240))
        gfx.text(surface, "10+", tile.center, 28, (255, 255, 255))
        gfx.text(surface, "Recommended for", (tile.right + 12, badge.top + 28), 17, gfx.INK, anchor="midleft", bold=False)
        gfx.text(surface, "ages 10 and up", (tile.right + 12, badge.top + 52), 17, gfx.INK, anchor="midleft")
        # version + tip
        r = pygame.Rect(22, H - 66, 0, 0)
        gfx.rrect(surface, (r.x, r.y, 300, 44), (255, 255, 255), 14, alpha=215)
        gfx.text(surface, f"v{__version__}  ·  Shouku Games  ·  {RELEASE_DATE}", (r.x + 150, r.y + 22), 15, gfx.INK, bold=False)
