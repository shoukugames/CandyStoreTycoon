"""Panels shared by the title screen and the game: save slots, settings, how to play, naming, confirm."""
import os
import random
import time

import pygame

from .. import art, gfx, storage, ui
from ..app import Overlay
from ..model import WIN_MONEY

CX, CY = 640, 360


class Label:
    """A static drawable used inside widget lists."""

    def __init__(self, fn):
        self.fn = fn

    def handle(self, event, app):
        return False

    def draw(self, surface, t):
        self.fn(surface, t)


class Tile:
    """A square picture button (candy pickers, restock choices)."""

    def __init__(self, rect, image, on_click, selected=False, enabled=True, badge=None, sound="click"):
        self.rect = pygame.Rect(rect)
        self.image, self.on_click, self.selected, self.enabled, self.badge, self.sound = image, on_click, selected, enabled, badge, sound
        self.hover = False

    def handle(self, event, app):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos):
            if self.enabled:
                if self.sound:
                    app.audio.play(self.sound)
                self.on_click()
            else:
                app.audio.play("error")
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False

    def draw(self, surface, t):
        r = self.rect.move(0, -2 if self.hover and self.enabled else 0)
        if self.selected:
            gfx.rrect(surface, r.inflate(8, 8), (255, 208, 228), 15)
            gfx.rrect(surface, r, gfx.PINK, 12)
            gfx.rrect(surface, r.inflate(-6, -6), (255, 227, 240), 9)
        else:
            gfx.rrect(surface, r, (255, 208, 228) if self.hover else (255, 230, 240), 12)
            gfx.rrect(surface, r.inflate(-6, -6), (255, 246, 250), 9)
        img = self.image
        if not self.enabled:
            img = img.copy()
            img.set_alpha(70)
        surface.blit(img, img.get_rect(center=r.center))
        if self.badge is not None:
            b = str(self.badge)
            w = max(20, gfx.font(12).size(b)[0] + 10)
            br = pygame.Rect(r.right - w + 4, r.bottom - 14, w, 18)
            gfx.rrect(surface, br, gfx.INK, 9)
            gfx.text(surface, b, br.center, 12, (255, 255, 255))


def close_button(overlay, panel):
    return ui.Button((panel.right - 58, panel.top + 14, 42, 42), "×", overlay.close, "white", 24, radius=21)


# ======================= SAVE SLOTS =======================

_thumb_cache = {}


def load_thumb(n):
    path = storage.thumb_path(n)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return None
    key = (path, mtime)
    if key not in _thumb_cache:
        try:
            _thumb_cache[key] = pygame.image.load(path).convert()
        except pygame.error:
            return None
    return _thumb_cache[key]


class SavesOverlay(Overlay):
    """mode 'save' shows Save Here buttons; 'load' only Load/Delete. on_load(n) loads slot n."""

    def __init__(self, scene, mode, on_load, on_save=None, paused_note=False):
        self.mode, self.on_load, self.on_save, self.paused_note = mode, on_load, on_save, paused_note
        self.confirm = None
        super().__init__(scene)

    def build(self):
        self.panel = pygame.Rect(0, 0, 800, 600)
        self.panel.center = (CX, CY + 10)
        p = self.panel
        self.widgets.append(close_button(self, p))
        top = p.top + 70 + (22 if self.paused_note else 0)
        self.rows = []
        for n in range(1, storage.SLOTS + 1):
            data = storage.read_slot(n)
            row = pygame.Rect(p.left + 30, top + (n - 1) * 140, p.w - 60, 126)
            self.rows.append((n, row, data))
            bx = row.right - 150
            y = row.top + 12
            if self.mode == "save":
                confirming = self.confirm == ("save", n)
                self.widgets.append(ui.Button((bx, y, 136, 32), "Overwrite?" if confirming else "Save Here",
                                              lambda n=n: self._save(n), "red" if confirming else "pink", 15, radius=12, sound=None))
                y += 38
            if data:
                self.widgets.append(ui.Button((bx, y, 136, 32), "Load", lambda n=n: self.on_load(n), "mint", 15, radius=12))
                y += 38
                confirming = self.confirm == ("del", n)
                self.widgets.append(ui.Button((bx, y, 136, 32), "Really delete?" if confirming else "Delete",
                                              lambda n=n: self._delete(n), "red" if confirming else "white", 15, radius=12))
        self.widgets.append(ui.Button((CX - 70, p.bottom - 64, 140, 46), "Back", self.close, "white", 20))

    def _save(self, n):
        if storage.read_slot(n) and self.confirm != ("save", n):
            self.confirm = ("save", n)
            self.app.audio.play("click")
            self.refresh()
            return
        self.confirm = None
        if self.on_save and self.on_save(n):
            self.app.audio.play("save")
            self.scene.toast(f"Game saved to Slot {n}!", "good")
        else:
            self.app.audio.play("error")
            self.scene.toast("Could not save the game.", "bad")
        self.refresh()

    def _delete(self, n):
        if self.confirm != ("del", n):
            self.confirm = ("del", n)
            self.refresh()
            return
        self.confirm = None
        storage.delete_slot(n)
        self.scene.toast(f"Slot {n} deleted.")
        self.refresh()

    def draw(self, surface, t):
        p = self.panel
        ui.draw_panel(surface, p, "Save Game" if self.mode == "save" else "Load Game", "purple")
        if self.paused_note:
            gfx.text(surface, "The store is paused while this menu is open.", (CX, p.top + 66), 16, gfx.INK_SOFT, bold=False)
        for n, row, data in self.rows:
            gfx.rrect(surface, row.move(0, 4), (255, 208, 228), 20)
            gfx.rrect(surface, row, (255, 208, 228), 20)
            gfx.rrect(surface, row.inflate(-6, -6), (255, 255, 255), 17)
            gfx.aa_circle(surface, gfx.PURPLE_D, (row.left + 40, row.centery + 3), 23)
            gfx.aa_circle(surface, gfx.PURPLE, (row.left + 40, row.centery), 23)
            gfx.text(surface, str(n), (row.left + 40, row.centery), 24, (255, 255, 255))
            th = pygame.Rect(row.left + 78, row.centery - 47, 168, 94)
            gfx.rrect(surface, th.inflate(6, 6), (255, 208, 228), 14)
            thumb = load_thumb(n) if data else None
            if thumb:
                img = pygame.transform.smoothscale(thumb, th.size)
                mask = gfx.rounded(th.w, th.h, 11, (255, 255, 255))
                img = img.convert_alpha()
                img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(img, th)
            else:
                gfx.rrect(surface, th, (243, 225, 236), 11)
                gfx.text(surface, "Saved" if data else "Empty", th.center, 17, (201, 163, 184))
            x = th.right + 20
            if data:
                m = data["meta"]
                gfx.text(surface, m.get("shop_name", "Shop"), (x, row.top + 30), 22, gfx.INK, anchor="midleft")
                extra = " · mid-rush" if m.get("phase") == "rush" else ""
                gfx.text(surface, f"Day {m.get('day', 1)}  ·  ¥{m.get('money', 0):,}{extra}", (x, row.top + 60), 16,
                         gfx.INK_SOFT, anchor="midleft", bold=False)
                ui.stars(surface, m.get("rep", 3), (x, row.top + 76), 18)
                when = time.strftime("%Y-%m-%d %H:%M", time.localtime(m.get("saved_at", 0)))
                gfx.text(surface, f"Saved {when}", (x, row.top + 108), 13, (176, 138, 160), anchor="midleft", bold=False)
            else:
                gfx.text(surface, "Empty Slot", (x, row.top + 46), 22, (201, 163, 184), anchor="midleft")
                gfx.text(surface, "No game saved here yet.", (x, row.top + 76), 16, gfx.INK_SOFT, anchor="midleft", bold=False)
        super().draw(surface, t)


# ======================= SETTINGS =======================

class SettingsOverlay(Overlay):
    def build(self):
        s = self.app.settings
        self.panel = pygame.Rect(0, 0, 560, 400)
        self.panel.center = (CX, CY)
        p = self.panel
        self.widgets.append(close_button(self, p))

        def toggle(key):
            s[key] = not s[key]
            self.app.save_settings()
            if key == "music":
                self.app.audio.refresh_music(self.scene.music_now())
            self.refresh()

        def vol(key, v):
            s[key] = round(v, 2)
            self.app.audio.apply_volume()
            self.app.save_settings()
        y = p.top + 100
        for key, vkey, label in (("music", "music_volume", "Music"), ("sfx", "sfx_volume", "Sounds")):
            self.widgets.append(Label(lambda surf, t, label=label, y=y: gfx.text(surf, label, (p.left + 50, y), 22, gfx.INK, anchor="midleft")))
            self.widgets.append(ui.Slider((p.left + 170, y - 12, 230, 24), s[vkey], lambda v, vk=vkey: vol(vk, v)))
            self.widgets.append(ui.Button((p.right - 130, y - 20, 86, 40), "On" if s[key] else "Off",
                                          lambda k=key: toggle(k), "mint" if s[key] else "white", 18, radius=14))
            y += 76

        def fullscreen():
            self.app.toggle_fullscreen()
            self.refresh()
        self.widgets.append(ui.Button((CX - 130, y - 10, 260, 46), "Exit Full Screen" if self.app.fullscreen else "Full Screen",
                                      fullscreen, "purple", 19))
        self.widgets.append(ui.Button((CX - 60, p.bottom - 66, 120, 46), "Done", self.close, "pink", 20))

    def draw(self, surface, t):
        ui.draw_panel(surface, self.panel, "Settings", "purple")
        gfx.text(surface, "Keys: Esc menu · M music · Space speed · F11 full screen", (CX, self.panel.bottom - 92), 14,
                 gfx.INK_SOFT, bold=False)
        super().draw(surface, t)


# ======================= HOW TO PLAY =======================

HOWTO = [
    ("The Register", "You start with ¥1,000. Spend it wisely at the Market on lollipops, gummy bears, chocolate and more. "
                     "Run out of money AND candy and it is Game Over!"),
    ("The Pantry", "Candy you buy waits in your backroom pantry. It holds 50 items to start. When it is full you cannot buy "
                   "more until you clear some space."),
    ("The Shop Floor", "Kids only buy candy they can SEE on your display shelves. Each shelf holds 10 of one candy. Cheap "
                       "lollipops sell fast; chocolate sells slower but earns far more. You decide!"),
    ("The Rush", "Press Open Store. Kids show what they want in a thought bubble with a patience ring. Have it on a shelf and "
                 "they pay you. Wait too long and they leave sad, lowering your star rating."),
    ("Restocking", "During the rush, click any shelf to refill it from your pantry, or switch it to a different candy."),
    ("Every Morning", "A new event: heatwaves, recess rushes, wholesale sales and more. Read the card and plan ahead!"),
    ("Grow", f"Rent is due each night. Buy upgrades at the Market. Reach ¥{WIN_MONEY:,} to become a Candy Tycoon. "
             "You can save at any time in one of 3 save slots."),
]


class HowToOverlay(Overlay):
    def build(self):
        self.panel = pygame.Rect(0, 0, 860, 640)
        self.panel.center = (CX, CY + 8)
        self.widgets.append(close_button(self, self.panel))
        self.widgets.append(ui.Button((CX - 80, self.panel.bottom - 62, 160, 46), "Got it!", self.close, "pink", 20))

    def draw(self, surface, t):
        p = self.panel
        ui.draw_panel(surface, p, "How to Play")
        y = p.top + 58
        icons = ["coin", "box", "lolli", "gummy", "choc", "ice", "cotton"]
        for i, (head, body) in enumerate(HOWTO):
            ix, iy = p.left + 56, y + 22
            if icons[i] in ("coin",):
                img = art.coin(18)
                surface.blit(img, img.get_rect(center=(ix, iy)))
            elif icons[i] == "box":
                img = ui.icon_surface("box", 36)
                surface.blit(img, img.get_rect(center=(ix, iy)))
            else:
                art.blit_candy(surface, icons[i], (ix, iy), 44, i)
            gfx.text(surface, head, (p.left + 92, y + 8), 19, gfx.PINK_D, anchor="midleft")
            y2 = gfx.paragraph(surface, body, (p.left + 92, y + 22), 15, p.w - 140, gfx.INK, anchor="topleft", spacing=1.2)
            y = max(y2, y + 50) + 10
        super().draw(surface, t)


# ======================= NAME YOUR SHOP =======================

NAMES_A = ["Sugar", "Candy", "Gumdrop", "Lolly", "Rainbow", "Sprinkle", "Bubble", "Cocoa", "Jelly", "Fizzy", "Taffy", "Honey"]
NAMES_B = ["Shack", "Palace", "Corner", "Castle", "Emporium", "Hut", "Factory", "Kingdom", "Station", "Cottage", "Market", "Island"]


class NameOverlay(Overlay):
    def __init__(self, scene, on_start):
        self.on_start = on_start
        self.input = ui.TextInput((0, 0, 420, 64), "Sweet Treats")
        super().__init__(scene)

    def build(self):
        self.panel = pygame.Rect(0, 0, 560, 380)
        self.panel.center = (CX, CY)
        p = self.panel
        self.input.rect.center = (CX, p.top + 150)
        self.widgets += [close_button(self, p), self.input,
                         ui.Button((CX - 90, p.top + 204, 180, 38), "Random Name", self._random, "yellow", 16, radius=13),
                         ui.Button((CX - 90, p.bottom - 82, 180, 56), "Start!", self._start, "pink", 24)]

    def _random(self):
        self.input.value = f"{random.choice(NAMES_A)} {random.choice(NAMES_B)}"
        self.input.select_all = False

    def _start(self):
        name = self.input.value.strip() or "Sweet Treats"
        self.on_start(name[:22])

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.app.audio.play("click")
            self._start()
            return True
        return super().handle(event)

    def draw(self, surface, t):
        ui.draw_panel(surface, self.panel, "Name Your Shop")
        gfx.text(surface, "Every great candy store needs a great name!", (CX, self.panel.top + 76), 18, gfx.INK, bold=False)
        super().draw(surface, t)


# ======================= CONFIRM =======================

class ConfirmOverlay(Overlay):
    def __init__(self, scene, title, message, yes_label, on_yes, style="red"):
        self.title, self.message, self.yes_label, self.on_yes, self.style = title, message, yes_label, on_yes, style
        super().__init__(scene)

    def build(self):
        self.panel = pygame.Rect(0, 0, 500, 260)
        self.panel.center = (CX, CY)
        p = self.panel
        self.widgets += [ui.Button((CX - 200, p.bottom - 80, 180, 50), "Cancel", self.close, "white", 20),
                         ui.Button((CX + 20, p.bottom - 80, 180, 50), self.yes_label, self.on_yes, self.style, 20)]

    def draw(self, surface, t):
        ui.draw_panel(surface, self.panel, self.title, "dark")
        gfx.paragraph(surface, self.message, (CX, self.panel.top + 60), 19, 420, gfx.INK)
        super().draw(surface, t)
