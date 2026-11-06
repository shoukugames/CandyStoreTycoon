"""The shop: HUD, shelves, customers, the bottom action bar and every in-game panel."""
import random

import pygame

from .. import art, gfx, i18n, storage, ui
from ..i18n import msg, prod, t as tr
from ..app import W, H, Overlay, Scene
from ..model import DAY_LENGTH, ORDER, PRODUCTS, UPGRADES, WIN_MONEY, Game
from .panels import CX, CY, ConfirmOverlay, HowToOverlay, SavesOverlay, SettingsOverlay, Tile, close_button


yen = i18n.yen


class GameScene(Scene):
    def __init__(self, app, shop_name=None, state=None, loaded_from=None):
        super().__init__(app)
        self.game = Game.from_dict(state) if state else Game(shop_name or tr("default_shop"))
        self.speed = 1
        self.particles = []
        self.hover = -1
        self.door = 0.0
        self.last_door_sound = -9.0
        self.restock_idx = None
        self.restock_tiles = []
        self.snapshot = None
        self.money_shown = float(self.game.s["money"])
        self.money_flash = 0.0
        self._build_bar()
        if state:
            self.toast(tr("loaded", name=self.game.s["shop_name"], day=i18n.day_label(self.game.s["day"])), "good")
            self.resume_phase()
        else:
            self.game.begin_day()
            self.show_morning()

    # ---------- music ----------
    @property
    def music(self):
        return "rush" if self.game.s["phase"] == "rush" else "shop"

    def music_now(self):
        return self.music

    @property
    def s(self):
        return self.game.s

    def changed(self):
        """Game state changed under an open panel: redraw the panel and the world behind it."""
        self._veil = None
        if self.overlays:
            self.overlays[-1].refresh()

    # ---------- phases ----------
    def resume_phase(self):
        phase = self.s["phase"]
        if phase == "morning":
            self.show_morning(sound=False)
        elif phase == "summary":
            self.push_overlay(SummaryOverlay(self))
        elif phase == "gameover":
            self.push_overlay(GameOverOverlay(self))
        elif phase == "rush":
            self.push_overlay(MenuOverlay(self, ready=True))

    def show_morning(self, sound=True):
        if sound:
            self.app.audio.play("morning")
            if self.s["today"].get("unlocked"):
                self.app.audio.play("unlock")
        self.push_overlay(MorningOverlay(self))

    def start_prep(self):
        self.clear_overlays()
        if not self.game.start_prep():
            self.game_over()
            return
        if self.s["day"] == 1:
            self.toast(tr("start_market"), "good")

    def open_store(self):
        ok, m = self.game.open_store()
        if not ok:
            self.app.audio.play("error")
            self.toast(msg(m), "bad")
            return
        self.clear_overlays()
        self.speed = 1
        self.app.audio.play("door")
        self.toast(msg(m), "good")
        self.app.set_music("rush")

    def next_day(self):
        self.clear_overlays()
        result = self.game.next_day()
        if result == "gameover":
            self.game_over()
        elif result == "win":
            self.app.audio.play("win")
            self.push_overlay(WinOverlay(self))
        else:
            self.show_morning()

    def keep_playing(self):
        self.clear_overlays()
        self.game.begin_day()
        self.show_morning()

    def game_over(self):
        self.s["phase"] = "gameover"
        self.app.audio.play("sad")
        self.push_overlay(GameOverOverlay(self))

    # ---------- saving ----------
    def save_to(self, n):
        snap = self.snapshot

        def thumb(path):
            if snap is not None:
                pygame.image.save(pygame.transform.smoothscale(snap, (192, 108)), path)
        return storage.write_slot(n, self.game.to_dict(), thumb)

    def open_saves(self):
        self.close_restock()
        self.push_overlay(SavesOverlay(self, "save" if self.s["phase"] != "gameover" else "load", self.load_slot,
                                       self.save_to, paused_note=self.s["phase"] == "rush"))

    def load_slot(self, n):
        data = storage.read_slot(n)
        if not data:
            self.toast(tr("slot_empty"), "bad")
            return
        self.app.audio.play("save")
        self.app.switch(GameScene(self.app, state=data["state"], loaded_from=n))

    def quit_to_title(self):
        from .title import TitleScene
        self.app.switch(TitleScene(self.app))

    # ---------- bottom bar ----------
    def _build_bar(self):
        y = 652
        self.b_market = ui.Button((14, y, 150, 52), tr("market"), self.open_market, "mint", 20, ui.icon_surface("cart", 24))
        self.b_shelves = ui.Button((174, y, 210, 52), tr("stock_shelves"), self.open_shelves, "purple", 20, ui.icon_surface("shelf", 24))
        self.b_speed = ui.Button((14, y, 160, 52), tr("speed", n=1), self.toggle_speed, "yellow", 19)
        self.b_open = ui.Button((856, y - 2, 222, 56), tr("open_store"), self.open_store, "pink", 22, ui.icon_surface("door", 26))
        self.b_save = ui.Button((1090, y + 2, 52, 50), "", self.open_saves, "white", 18, ui.icon_surface("save", 26), radius=16)
        music_icon = "music" if self.app.settings["music"] else "music_off"
        self.b_music = ui.Button((1150, y + 2, 52, 50), "", self.toggle_music, "white", 18, ui.icon_surface(music_icon, 26),
                                 radius=16)
        self.b_menu = ui.Button((1210, y + 2, 52, 50), "", lambda: self.push_overlay(MenuOverlay(self)), "white", 18,
                                ui.icon_surface("menu", 26), radius=16)

    def bar_buttons(self):
        phase = self.s["phase"]
        out = []
        if phase == "prep":
            out += [self.b_market, self.b_shelves, self.b_open]
        if phase == "rush":
            out.append(self.b_speed)
        out += [self.b_save, self.b_music, self.b_menu]
        return out

    def toggle_speed(self):
        self.speed = 2 if self.speed == 1 else 1
        self.b_speed.label = tr("speed", n=self.speed)

    def toggle_music(self):
        st = self.app.settings
        st["music"] = not st["music"]
        self.app.save_settings()
        self.app.audio.refresh_music(self.music)
        self.b_music.icon = ui.icon_surface("music" if st["music"] else "music_off", 26)

    def open_market(self):
        if self.s["phase"] == "prep":
            self.push_overlay(MarketOverlay(self))

    def open_shelves(self):
        if self.s["phase"] == "prep":
            self.push_overlay(ShelvesOverlay(self))

    def tip(self):
        g, phase = self.game, self.s["phase"]
        for b in (self.b_market, self.b_shelves, self.b_open):
            b.pulse = False
        if phase == "prep":
            pu, ss = g.pantry_used(), g.shelf_stock()
            if pu == 0 and ss == 0:
                self.b_market.pulse = True
                return tr("tip_step1")
            if ss == 0:
                self.b_shelves.pulse = True
                return tr("tip_step2")
            self.b_open.pulse = True
            if any(sh["count"] < g.shelf_cap() and self.s["pantry"][sh["type"]] > 0 for sh in self.s["shelves"]):
                return tr("tip_room")
            return tr("tip_ready")
        if phase == "rush":
            return tr("tip_rush")
        return ""

    # ---------- restock popup ----------
    def open_restock(self, i):
        sh = self.s["shelves"][i]
        if sh["restock"]:
            self.toast(tr("already_restocking"))
            return
        self.restock_idx = i
        kinds = [k for k in ORDER if self.game.unlocked(k)]
        x, y, w, h = self.game.shelf_rects()[i]
        tw = 64 * len(kinds) + 16
        box = pygame.Rect(0, 0, tw, 104)
        box.midbottom = (x + w / 2, y + 30)
        box.x = max(8, min(W - tw - 8, box.x))
        self.restock_box = box
        self.restock_tiles = []
        for j, k in enumerate(kinds):
            n = self.s["pantry"][k]
            self.restock_tiles.append(Tile((box.x + 10 + j * 64, box.y + 34, 58, 60), art.candy(k, 42), lambda k=k: self.do_restock(i, k),
                                           selected=k == sh["type"], enabled=n > 0, badge=n, sound=None))
        self.app.audio.play("click")

    def close_restock(self):
        self.restock_idx = None
        self.restock_tiles = []

    def do_restock(self, i, k):
        ok, m = self.game.begin_restock(i, k)
        if ok:
            self.app.audio.play("pop")
        else:
            self.app.audio.play("error")
            self.toast(msg(m), "bad")
        self.close_restock()

    # ---------- input ----------
    def handle_world(self, event):
        if self.restock_idx is not None:
            for tile in self.restock_tiles:
                if tile.handle(event, self.app):
                    return
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                inside = event.type == pygame.MOUSEBUTTONDOWN and self.restock_box.collidepoint(event.pos)
                if not inside:
                    self.close_restock()
                    if event.type == pygame.KEYDOWN:
                        return
                else:
                    return
        for b in self.bar_buttons():
            if b.handle(event, self.app):
                return
        phase = self.s["phase"]
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.shelf_at(event.pos) if phase in ("prep", "rush") else -1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            i = self.shelf_at(event.pos)
            if i >= 0 and phase == "rush":
                self.open_restock(i)
            elif i >= 0 and phase == "prep":
                self.app.audio.play("click")
                self.open_shelves()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.audio.play("click")
                self.push_overlay(MenuOverlay(self))
            elif event.key == pygame.K_m:
                self.toggle_music()
            elif event.key == pygame.K_SPACE and phase == "rush":
                self.toggle_speed()

    def shelf_at(self, pos):
        for i, (x, y, w, h) in enumerate(self.game.shelf_rects()):
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                return i
        return -1

    def push_overlay(self, overlay):
        self.close_restock()
        self.hover = -1
        return super().push_overlay(overlay)

    # ---------- update ----------
    def update_world(self, dt, paused):
        g = self.game
        if not paused and self.s["phase"] == "rush":
            g.update(dt * self.speed)
        for kind, data in g.pop_events():
            self.on_event(kind, data)
        if not paused:
            step = dt * (self.speed if self.s["phase"] == "rush" else 1)
            for p in self.particles:
                p["life"] -= step
                p["vy"] += p.get("g", 0) * step
                p["x"] += p.get("vx", 0) * step
                p["y"] += p["vy"] * step
            self.particles = [p for p in self.particles if p["life"] > 0]
        self.door = max(0.0, self.door - dt * 1.5)
        self.money_shown += (self.s["money"] - self.money_shown) * min(1, dt * 10)
        if abs(self.s["money"] - self.money_shown) < 1:
            self.money_shown = self.s["money"]
        self.money_flash = max(0.0, self.money_flash - dt)
        tip = self.tip()
        self._tip = tip

    def on_event(self, kind, d):
        a = self.app.audio
        if kind == "sale":
            a.play("coin")
            self.money_flash = 0.5
            self.particles.append({"kind": "text", "x": d["x"], "y": d["y"] - 150, "text": "+" + yen(d["amount"]),
                                   "color": gfx.GREEN_TXT, "vy": -60, "life": 1.3, "max": 1.3, "big": True})
            for _ in range(5):
                self.particles.append({"kind": "coin", "x": d["x"] + random.uniform(-10, 10), "y": d["y"] - 110,
                                       "vx": random.uniform(-90, 90), "vy": random.uniform(-230, -140), "g": 520,
                                       "life": 0.9, "max": 0.9})
            self.particles.append({"kind": "heart", "x": d["x"] + 18, "y": d["y"] - 140, "vy": -50, "life": 1.1, "max": 1.1})
        elif kind == "unhappy":
            a.play("sad")
            self.particles.append({"kind": "storm", "x": d["x"], "y": d["y"] - 165, "vy": -18, "life": 1.6, "max": 1.6})
            text = tr("no_candy", name=prod(d["craving"])) if d["no_shelf"] else tr("too_slow")
            self.particles.append({"kind": "text", "x": d["x"], "y": d["y"] - 128, "text": text, "color": gfx.RED,
                                   "vy": -40, "life": 1.6, "max": 1.6})
        elif kind == "empty":
            self.toast(tr("shelf_empty_toast", name=prod(d["type"])), "bad")
        elif kind == "restocked":
            a.play("restock")
            x, y, w, h = self.game.shelf_rects()[d["shelf"]]
            self.particles.append({"kind": "text", "x": x + w / 2, "y": y + 30, "text": tr("restocked", n=d["n"], name=prod(d["type"])),
                                   "color": gfx.PURPLE, "vy": -40, "life": 1.2, "max": 1.2})
            for _ in range(10):
                self.particles.append({"kind": "spark", "x": x + random.uniform(10, w - 10), "y": y + random.uniform(60, 220),
                                       "vy": random.uniform(-60, -20), "life": 0.8, "max": 0.8})
        elif kind == "door":
            self.door = 1.2
            if self.app.time - self.last_door_sound > 1.5 and random.random() < 0.5:
                self.last_door_sound = self.app.time
                a.play("door")
        elif kind == "wave":
            a.play("whoosh")
            self.toast(tr("wave"))
        elif kind == "closing":
            a.play("door")
            self.toast(tr("closing_time"))
        elif kind == "day_end":
            a.play("day_end")
            self.speed = 1
            self.b_speed.label = tr("speed", n=1)
            self.app.set_music("shop")
            self.push_overlay(SummaryOverlay(self))

    # ---------- drawing ----------
    def draw_world(self, surface):
        g, s, t = self.game, self.s, self.app.time
        rush = s["phase"] == "rush"
        art.shop(surface, t, s["shop_name"], self.door, rush)
        cap = g.shelf_cap()
        for i, (sh, rect) in enumerate(zip(s["shelves"], g.shelf_rects())):
            hint = (tr("click_restock") if rush else tr("click_stock")) if self.hover == i else None
            art.shelf(surface, rect, sh, cap, g.price(sh["type"]), g.price_boosted(sh["type"]), self.hover == i, t, rush, hint)
        surface.blit(art.counter(), (1130, 344))
        if s["rush"]:
            kids = sorted(s["rush"]["customers"], key=lambda c: c["y"])
            for c in kids:
                blink = ((t + c["look"]["blink"]) % 4) < 0.12
                art.draw_kid(surface, c["look"], c["x"], c["y"], mood=c["mood"], phase=c["phase"], walking=c["walking"],
                             flip=c["flip"], holding=c["holding"], hold_v=c["id"] % 4, blink=blink)
            for c in kids:
                if c["state"] in ("wait", "look") or (c["state"] == "walk" and not c["holding"]):
                    frac = max(0.0, c["patience"] / c["max_patience"]) if c["state"] == "wait" else None
                    art.bubble(surface, c["x"] + 30, c["y"] - 158 * c["look"]["size"], c["craving"], frac, c["qty"], c["alt"],
                               t + c["id"])
        self.draw_particles(surface)
        self.draw_hud(surface)
        self.draw_bar(surface)
        if self.restock_idx is not None:
            self.draw_restock(surface)
        if self.snapshot is None:
            self.snapshot = pygame.Surface((W, H)).convert()
        self.snapshot.blit(surface, (0, 0))

    def draw_particles(self, surface):
        for p in self.particles:
            a = min(1.0, p["life"] / p["max"] * 2)
            k = p["kind"]
            if k == "text":
                gfx.text(surface, p["text"], (p["x"], p["y"]), 26 if p.get("big") else 20, p["color"], stroke=(255, 255, 255),
                         stroke_w=3, alpha=int(255 * a))
            else:
                img = {"coin": lambda: art.coin(9), "heart": lambda: art.heart(30), "storm": art.storm,
                       "spark": lambda: art.star(7, (255, 246, 160), (255, 207, 58))}[k]()
                if a < 1:
                    img = img.copy()
                    img.set_alpha(int(255 * a))
                surface.blit(img, img.get_rect(center=(p["x"], p["y"])))

    def draw_hud(self, surface):
        g, s = self.game, self.s
        rush = s["phase"] == "rush" and s["rush"]
        name = s["shop_name"]
        ev_name = "" if s["event"] == "normal" else i18n.ev_name(s["event"]).rstrip("!！")
        f18 = gfx.font(19)
        items = []
        items.append(("shop", min(240, gfx.text_size(name, 19)[0] + 32)))
        items.append(("day", 32 + f18.size(i18n.day_label(s["day"]))[0] + (gfx.font(13).size(ev_name)[0] + 24 if ev_name else 0)))
        items.append(("money", 44 + max(80, f18.size(yen(self.money_shown))[0]) + 12))
        items.append(("stars", 5 * 22 + 26))
        items.append(("pantry", 44 + f18.size(f"{g.pantry_used()}/{g.pantry_cap()}")[0] + 12))
        if rush:
            items.append(("clock", 170))
        gap = 10
        total = sum(w for _, w in items) + gap * (len(items) - 1)
        x = W / 2 - total / 2
        y, h = 8, 44
        for kind, w in items:
            r = pygame.Rect(int(x), y, int(w), h)
            if kind == "shop":
                ui.pill(surface, r, (255, 95, 162), gfx.PINK_D)
                label = name
                while gfx.text_size(label, 19)[0] > w - 28 and len(label) > 3:
                    label = label[:-2] + "…" if not label.endswith("…") else label[:-2] + "…"
                gfx.text(surface, label, r.center, 19, (255, 255, 255), shadow=gfx.PINK_D)
            else:
                ui.pill(surface, r, (255, 250, 220) if (kind == "money" and self.money_flash > 0) else (255, 255, 255))
            if kind == "day":
                dr = gfx.text(surface, i18n.day_label(s["day"]), (r.x + 16, r.centery), 19, gfx.INK, anchor="midleft")
                if ev_name:
                    cw = gfx.font(13).size(ev_name)[0] + 18
                    cr = pygame.Rect(dr.right + 8, r.centery - 11, cw, 22)
                    gfx.rrect(surface, cr, (255, 227, 240), 11)
                    gfx.text(surface, ev_name, cr.center, 13, gfx.PINK_D)
            elif kind == "money":
                surface.blit(ui.icon_surface("coin", 26), (r.x + 12, r.centery - 13))
                col = gfx.RED_TXT if s["money"] < 0 else (179, 107, 0)
                gfx.text(surface, yen(self.money_shown), (r.x + 44, r.centery), 19, col, anchor="midleft")
            elif kind == "stars":
                ui.stars(surface, s["rep"], (r.x + 13, r.centery - 11), 20)
            elif kind == "pantry":
                surface.blit(ui.icon_surface("box", 26), (r.x + 12, r.centery - 13))
                full = g.pantry_used() >= g.pantry_cap()
                gfx.text(surface, f"{g.pantry_used()}/{g.pantry_cap()}", (r.x + 44, r.centery), 19, gfx.RED_TXT if full else gfx.INK,
                         anchor="midleft")
            elif kind == "clock":
                f = min(1.0, s["rush"]["elapsed"] / DAY_LENGTH)
                mins = 9 * 60 + f * 9 * 60
                hh, mm = int(mins // 60), int(mins % 60 // 15 * 15)
                label = tr("closing") if f >= 1 else i18n.clock(hh, mm)
                surface.blit(ui.icon_surface("clock", 24), (r.x + 12, r.centery - 14))
                gfx.text(surface, label, (r.x + 44, r.centery - 3), 18, gfx.INK, anchor="midleft")
                bar = pygame.Rect(r.x + 16, r.bottom - 11, r.w - 32, 6)
                gfx.rrect(surface, bar, (234, 223, 255), 3)
                if f > 0.03:
                    gfx.rrect(surface, (bar.x, bar.y, int(bar.w * f), bar.h), gfx.PURPLE, 3)
            x += w + gap

    def draw_bar(self, surface):
        t = self.app.time
        shade = gfx.vgrad(W, 90, (255, 255, 255), (220, 170, 200)).convert()
        surface.blit(shade, (0, H - 90), special_flags=pygame.BLEND_RGB_MULT)
        tip = getattr(self, "_tip", "")
        if tip:
            tr = pygame.Rect(0, 0, 440 if self.s["phase"] == "prep" else 560, 46)
            tr.center = (630 if self.s["phase"] == "prep" else 620, 678)
            gfx.rrect(surface, tr, (255, 179, 212), 16)
            gfx.rrect(surface, tr.inflate(-6, -6), (255, 255, 255), 13)
            gfx.text(surface, tip, tr.center, 16, gfx.INK, bold=False)
        for b in self.bar_buttons():
            b.draw(surface, t)

    def draw_restock(self, surface):
        box = self.restock_box
        gfx.shadow(surface, box, 18, 10, 90, 6)
        gfx.rrect(surface, box, gfx.PINK, 18)
        gfx.rrect(surface, box.inflate(-8, -8), (255, 255, 255), 14)
        tri = [(box.centerx - 12, box.bottom - 2), (box.centerx + 12, box.bottom - 2), (box.centerx, box.bottom + 14)]
        x, y, w, h = self.game.shelf_rects()[self.restock_idx]
        cx = min(max(x + w / 2, box.left + 24), box.right - 24)
        tri = [(cx - 12, box.bottom - 2), (cx + 12, box.bottom - 2), (cx, box.bottom + 14)]
        pygame.draw.polygon(surface, gfx.PINK, tri)
        gfx.text(surface, tr("restock_title", n=self.restock_idx + 1), (box.centerx, box.top + 19), 15, gfx.INK)
        for tile in self.restock_tiles:
            tile.draw(surface, self.app.time)


# ======================= IN-GAME PANELS =======================

class MorningOverlay(Overlay):
    dismissable = False

    def build(self):
        self.panel = pygame.Rect(0, 0, 680, 650)
        self.panel.center = (CX, CY + 18)
        self.art = pygame.Surface((560, 250)).convert()
        self.widgets.append(ui.Button((CX - 100, self.panel.bottom - 76, 200, 56), tr("lets_go"), self.scene.start_prep, "pink", 24))

    def draw(self, surface, t):
        s = self.scene.s
        p = self.panel
        ui.draw_panel(surface, p, tr("good_morning", day=i18n.day_label(s["day"])))
        art.event_art(self.art, s["event"], t)
        ar = self.art.get_rect(midtop=(CX, p.top + 46))
        mask = gfx.rounded(ar.w, ar.h, 20, (255, 255, 255))
        img = self.art.convert_alpha()
        img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        gfx.rrect(surface, ar.inflate(10, 10).move(0, 4), (255, 208, 228), 24)
        gfx.rrect(surface, ar.inflate(10, 10), (255, 255, 255), 24)
        surface.blit(img, ar)
        gfx.text(surface, i18n.ev_name(s["event"]), (CX, ar.bottom + 34), 34, gfx.PINK_D)
        y = gfx.paragraph(surface, i18n.ev_desc(s["event"]), (CX, ar.bottom + 60), 18, 560, gfx.INK)
        chips = i18n.ev_effects(s["event"])
        today = s["today"]
        if today.get("melted"):
            n = today["melted"]
            chips.append(("bad", tr("melted", n=n) if n > 1 else tr("melted1")))
        if today.get("unlocked"):
            chips.append(("good", tr("new_at_market", names=tr("list_sep").join(prod(k) for k in today["unlocked"]))))
        ui.chips_row(surface, chips, CX, y + 18, 15, max_w=600)
        super().draw(surface, t)


class MarketOverlay(Overlay):
    def __init__(self, scene):
        self.tab = "candy"
        super().__init__(scene)

    def build(self):
        g = self.scene.game
        self.panel = pygame.Rect(0, 0, 960, 650)
        self.panel.center = (CX, CY + 16)
        p = self.panel
        self.widgets.append(close_button(self, p))
        for i, (tab, label) in enumerate((("candy", tr("candy_stock")), ("upg", tr("shop_upgrades")))):
            self.widgets.append(ui.Button((p.left + 34 + i * 190, p.top + 86, 176, 40), label, lambda tab=tab: self._tab(tab),
                                          "pink" if self.tab == tab else "white", 17, radius=14))
        if self.tab == "candy":
            for i, k in enumerate(ORDER):
                r = self._card(i)
                if not g.unlocked(k):
                    continue
                mx = g.max_buy(k)
                bx = r.centerx - 132
                for j, (n, label) in enumerate(((1, "+1"), (5, "+5"), (10, "+10"), ("max", tr("max")))):
                    ok = mx >= 1 if n == "max" else mx >= n
                    self.widgets.append(ui.Button((bx + j * 67, r.bottom - 44, 60, 32), label, lambda k=k, n=n: self._buy(k, n),
                                                  "purple" if n == "max" else "mint", 15, enabled=ok, radius=11, sound=None))
        else:
            for i, u in enumerate(UPGRADES):
                r = self._upg(i)
                lvl = self.scene.s["upgrades"][u["id"]]
                if lvl < len(u["cost"]):
                    c = u["cost"][lvl]
                    self.widgets.append(ui.Button((r.right - 118, r.centery - 20, 104, 40), yen(c), lambda uid=u["id"]: self._upgrade(uid),
                                                  "purple", 16, enabled=self.scene.s["money"] >= c, radius=13, sound=None))
        self.widgets.append(ui.Button((CX - 230, p.bottom - 68, 240, 50), tr("stock_next"), self._to_shelves, "purple", 19))
        self.widgets.append(ui.Button((CX + 30, p.bottom - 68, 140, 50), tr("done"), self.close, "white", 20))

    def _card(self, i):
        p = self.panel
        cw, ch = 290, 202
        return pygame.Rect(p.left + 34 + (i % 3) * (cw + 15), p.top + 140 + (i // 3) * (ch + 14), cw, ch)

    def _upg(self, i):
        p = self.panel
        return pygame.Rect(p.left + 34 + (i % 2) * 452, p.top + 146 + (i // 2) * 128, 440, 114)

    def _tab(self, tab):
        self.tab = tab
        self.refresh()

    def _buy(self, k, n):
        ok, m = self.scene.game.buy(k, n)
        if ok:
            self.app.audio.play("pop")
        else:
            self.app.audio.play("error")
            self.scene.toast(msg(m), "bad")
        self.scene.changed()

    def _upgrade(self, uid):
        ok, m = self.scene.game.buy_upgrade(uid)
        self.app.audio.play("upgrade" if ok else "error")
        self.scene.toast(msg(m), "good" if ok else "bad")
        self.scene.changed()

    def _to_shelves(self):
        self.close()
        self.scene.open_shelves()

    def draw(self, surface, t):
        g, s = self.scene.game, self.scene.s
        p = self.panel
        ui.draw_panel(surface, p, tr("market_title"), "mint")
        br = gfx.text(surface, tr("budget"), (p.left + 36, p.top + 58), 19, gfx.INK, anchor="midleft", bold=False)
        gfx.text(surface, yen(s["money"]), (br.right + 8, p.top + 58), 20, (179, 107, 0), anchor="midleft")
        used, cap = g.pantry_used(), g.pantry_cap()
        gfx.text(surface, tr("pantry"), (p.right - 362, p.top + 58), 19, gfx.INK, anchor="midright", bold=False)
        ui.meter(surface, (p.right - 350, p.top + 48, 290, 22), used / cap, gfx.RED if used >= cap else gfx.MINT, f"{used} / {cap}")
        if self.tab == "candy":
            for i, k in enumerate(ORDER):
                self._draw_card(surface, i, k, g)
        else:
            for i, u in enumerate(UPGRADES):
                r = self._upg(i)
                lvl = s["upgrades"][u["id"]]
                gfx.rrect(surface, r.move(0, 4), (227, 217, 255), 18)
                gfx.rrect(surface, r, (227, 217, 255), 18)
                gfx.rrect(surface, r.inflate(-6, -6), (255, 255, 255), 15)
                surface.blit(art.upgrade_icon(u["icon"], 60), (r.x + 16, r.centery - 30))
                gfx.text(surface, i18n.upg_name(u["id"]), (r.x + 92, r.y + 30), 20, gfx.INK, anchor="midleft")
                gfx.text(surface, i18n.upg_desc(u["id"]), (r.x + 92, r.y + 58), 15, gfx.INK_SOFT, anchor="midleft", bold=False)
                gfx.text(surface, tr("level", n=lvl, m=len(u["cost"])), (r.x + 92, r.y + 84), 13, gfx.PURPLE_D, anchor="midleft")
                if lvl >= len(u["cost"]):
                    ui.chip(surface, tr("maxed"), (r.right - 66, r.centery), "good", 15)
        super().draw(surface, t)

    def _draw_card(self, surface, i, k, g):
        p = PRODUCTS[k]
        r = self._card(i)
        locked = not g.unlocked(k)
        gfx.rrect(surface, r.move(0, 4), (255, 208, 228), 20)
        gfx.rrect(surface, r, (255, 208, 228), 20)
        gfx.rrect(surface, r.inflate(-6, -6), (250, 245, 248) if locked else (255, 255, 255), 17)
        img = art.candy(k, 54)
        if locked:
            img = img.copy()
            img.set_alpha(90)
        surface.blit(img, img.get_rect(center=(r.centerx, r.y + 36)))
        gfx.text(surface, prod(k), (r.centerx, r.y + 74), 20, (190, 170, 182) if locked else gfx.INK)
        gfx.text(surface, i18n.prod_desc(k), (r.centerx, r.y + 96), 14, gfx.INK_SOFT, bold=False)
        if locked:
            gfx.text(surface, tr("unlocks_on", day=i18n.day_label(p["unlock"])), (r.centerx, r.y + 150), 16, gfx.PURPLE_D)
            return
        c, pr = g.cost(k), g.price(k)
        buy = tr("buy_price", n=c)
        sell = tr("sell_price", n=pr)
        bw, sw = gfx.font(14).size(buy)[0] + 18, gfx.font(14).size(sell)[0] + 18
        bx = r.centerx - (bw + sw + 8) / 2
        gfx.rrect(surface, (bx, r.y + 109, bw, 24), (255, 232, 242), 10)
        gfx.text(surface, buy, (bx + bw / 2, r.y + 121), 14, (194, 24, 91))
        gfx.rrect(surface, (bx + bw + 8, r.y + 109, sw, 24), (220, 250, 242), 10)
        gfx.text(surface, sell, (bx + bw + 8 + sw / 2, r.y + 121), 14, gfx.GREEN_TXT)
        gfx.text(surface, tr("in_pantry", n=self.scene.s["pantry"][k], p=pr - c), (r.centerx, r.y + 145), 13,
                 gfx.INK_SOFT, bold=False)
        tag = None
        if c < p["cost"]:
            tag = (tr("tag_sale"), (255, 59, 107), (184, 32, 74))
        elif pr > p["price"]:
            tag = (tr("tag_hot"), gfx.MINT, gfx.MINT_D)
        elif c > p["cost"]:
            tag = (tr("tag_pricey"), (255, 138, 31), (200, 100, 0))
        if tag:
            img = gfx.render_text(tag[0], 14, (255, 255, 255))
            badge = pygame.Surface((img.get_width() + 20, 26), pygame.SRCALPHA)
            gfx.rrect(badge, (0, 2, badge.get_width(), 24), tag[2], 10)
            gfx.rrect(badge, (0, 0, badge.get_width(), 23), tag[1], 10)
            badge.blit(img, img.get_rect(center=(badge.get_width() / 2, 11)))
            badge = pygame.transform.rotozoom(badge, -8, 1)
            surface.blit(badge, badge.get_rect(center=(r.right - 28, r.top + 6)))


class ShelvesOverlay(Overlay):
    def build(self):
        g, s = self.scene.game, self.scene.s
        n = len(s["shelves"])
        row_h = 76
        self.panel = pygame.Rect(0, 0, 960, 250 + n * row_h)
        self.panel.center = (CX, CY + 12)
        p = self.panel
        self.row_h = row_h
        self.widgets.append(close_button(self, p))
        cap = g.shelf_cap()
        for i, sh in enumerate(s["shelves"]):
            r = self._row(i)
            for j, k in enumerate(ORDER):
                un = g.unlocked(k)
                self.widgets.append(Tile((r.x + 104 + j * 54, r.centery - 24, 48, 48), art.candy(k, 36),
                                         lambda i=i, k=k: self._set(i, k), selected=sh["type"] == k, enabled=un,
                                         badge=s["pantry"][k] if un else "?", sound=None))
            can_add = sh["count"] < cap and s["pantry"][sh["type"]] > 0
            bx = r.right - 196
            self.widgets.append(ui.Button((bx, r.centery - 17, 54, 34), "-1", lambda i=i: self._add(i, -1), "white", 15,
                                          enabled=sh["count"] > 0, radius=11, sound=None))
            self.widgets.append(ui.Button((bx + 60, r.centery - 17, 54, 34), "+1", lambda i=i: self._add(i, 1), "white", 15,
                                          enabled=can_add, radius=11, sound=None))
            self.widgets.append(ui.Button((bx + 120, r.centery - 17, 66, 34), tr("fill"), lambda i=i: self._add(i, "fill"), "pink", 15,
                                          enabled=can_add, radius=11, sound=None))
        y = p.bottom - 72
        self.widgets.append(ui.Button((CX - 330, y, 220, 52), tr("fill_all"), self._fill_all, "mint", 19, sound=None))
        self.widgets.append(ui.Button((CX - 90, y - 2, 230, 56), tr("open_store"), self.scene.open_store, "pink", 22,
                                      ui.icon_surface("door", 26)))
        self.widgets.append(ui.Button((CX + 160, y, 150, 52), tr("done"), self.close, "white", 20))

    def _row(self, i):
        p = self.panel
        return pygame.Rect(p.left + 30, p.top + 150 + i * self.row_h, p.w - 60, self.row_h - 10)

    def _set(self, i, k):
        if self.scene.game.set_shelf_type(i, k):
            self.app.audio.play("click")
        self.scene.changed()

    def _add(self, i, n):
        moved = self.scene.game.shelf_add(i, n)
        self.app.audio.play("pop" if moved > 0 else "click")
        self.scene.changed()

    def _fill_all(self):
        if self.scene.game.fill_all():
            self.app.audio.play("restock")
        else:
            self.app.audio.play("error")
            self.scene.toast(tr("nothing_to_fill"))
        self.scene.changed()

    def draw(self, surface, t):
        g, s = self.scene.game, self.scene.s
        p = self.panel
        ui.draw_panel(surface, p, tr("shelves_title"), "purple")
        gfx.text(surface, tr("shelves_help"),
                 (CX, p.top + 58), 16, gfx.INK, bold=False)
        kinds = [k for k in ORDER if g.unlocked(k)]
        x = CX - (len(kinds) * 82 + 190) / 2
        for k in kinds:
            r = pygame.Rect(int(x), p.top + 82, 74, 40)
            gfx.rrect(surface, r, (243, 220, 232), 12)
            gfx.rrect(surface, r.inflate(-4, -4), (255, 255, 255), 10)
            art.blit_candy(surface, k, (r.x + 20, r.centery), 32)
            gfx.text(surface, str(s["pantry"][k]), (r.x + 52, r.centery), 17, gfx.INK)
            x += 82
        gfx.text(surface, tr("in_pantry_total", n=g.pantry_used(), m=g.pantry_cap()), (x + 6, p.top + 102), 15, gfx.INK_SOFT,
                 anchor="midleft", bold=False)
        cap = g.shelf_cap()
        for i, sh in enumerate(s["shelves"]):
            r = self._row(i)
            gfx.rrect(surface, r.move(0, 4), (255, 208, 228), 18)
            gfx.rrect(surface, r, (255, 208, 228), 18)
            gfx.rrect(surface, r.inflate(-6, -6), (255, 255, 255), 15)
            gfx.text(surface, tr("shelf_n", n=i + 1), (r.x + 18, r.centery), 18, gfx.INK, anchor="midleft")
            mx = r.x + 104 + 6 * 54 + 16
            gfx.text(surface, f"{prod(sh['type'])}: {sh['count']}/{cap}", (mx, r.centery - 12), 14, gfx.INK, anchor="midleft")
            ui.meter(surface, (mx, r.centery + 2, 170, 16), sh["count"] / cap, gfx.PINK)
        super().draw(surface, t)


class SummaryOverlay(Overlay):
    dismissable = False

    def build(self):
        self.panel = pygame.Rect(0, 0, 640, 600)
        self.panel.center = (CX, CY + 16)
        p = self.panel
        self.widgets.append(ui.Button((CX - 230, p.bottom - 74, 200, 54), tr("save_game"), self.scene.open_saves, "white", 20,
                                      ui.icon_surface("save", 24)))
        self.widgets.append(ui.Button((CX + 20, p.bottom - 76, 210, 58), tr("next_day"), self.scene.next_day, "pink", 24))

    def draw(self, surface, t):
        s = self.scene.s
        sm = s["summary"]
        p = self.panel
        ui.draw_panel(surface, p, tr("day_complete", day=i18n.day_label(sm["day"])), "purple")
        note = tr("sum_nice")
        if sm["unhappy"] == 0 and sm["served"] > 5:
            note = tr("sum_perfect")
        elif sm["unhappy"] > sm["served"]:
            note = tr("sum_empty")
        elif sm["profit"] < 0:
            note = tr("sum_loss")
        gfx.text(surface, note, (CX, p.top + 60), 19, gfx.INK)
        cells = [(tr("happy_customers"), str(sm["served"]), gfx.GREEN_TXT), (tr("unhappy_customers"), str(sm["unhappy"]),
                                                                           gfx.RED_TXT if sm["unhappy"] else gfx.INK),
                 (tr("sales"), yen(sm["revenue"]), gfx.GREEN_TXT), (tr("rent"), "-" + yen(sm["rent"]), gfx.RED_TXT)]
        for i, (label, val, col) in enumerate(cells):
            r = pygame.Rect(p.left + 34 + (i % 2) * 292, p.top + 88 + (i // 2) * 62, 280, 52)
            self._stat(surface, r, label, val, col, 22)
        r = pygame.Rect(p.left + 34, p.top + 214, 572, 62)
        prof = sm["profit"]
        self._stat(surface, r, tr("profit"), ("+" if prof >= 0 else "") + yen(prof), gfx.GREEN_TXT if prof >= 0 else gfx.RED_TXT, 30)
        r = pygame.Rect(p.left + 34, p.top + 288, 280, 52)
        self._stat(surface, r, tr("budget_plain"), yen(s["money"]), gfx.INK, 22)
        r = pygame.Rect(p.left + 326, p.top + 288, 280, 52)
        self._stat(surface, r, tr("rating"), "", gfx.INK, 22)
        ui.stars(surface, s["rep"], (r.right - 176, r.centery - 10), 19)
        diff = sm["rep_end"] - sm["rep_start"]
        gfx.text(surface, f"{'+' if diff >= 0 else ''}{diff:.1f}", (r.right - 20, r.centery), 15,
                 gfx.GREEN_TXT if diff >= 0 else gfx.RED_TXT, anchor="midright")
        sold = sorted(sm["sold"].items(), key=lambda kv: -kv[1])
        if sold:
            widths = [gfx.font(16).size(tr("sold", n=n))[0] + 56 for _k, n in sold]
            x = CX - (sum(widths) + 10 * (len(sold) - 1)) / 2
            for (k, n), w in zip(sold, widths):
                rr = pygame.Rect(int(x), p.top + 356, w, 40)
                gfx.rrect(surface, rr, (243, 220, 232), 12)
                gfx.rrect(surface, rr.inflate(-4, -4), (255, 255, 255), 10)
                art.blit_candy(surface, k, (rr.x + 22, rr.centery), 32)
                gfx.text(surface, tr("sold", n=n), (rr.x + 42, rr.centery), 16, gfx.INK, anchor="midleft")
                x += w + 10
            gfx.text(surface, tr("best_seller", name=prod(sold[0][0])), (CX, p.top + 420), 16, gfx.INK_SOFT, bold=False)
        else:
            gfx.text(surface, tr("nothing_sold"), (CX, p.top + 380), 17, gfx.INK_SOFT, bold=False)
        if not s["won"]:
            ui.meter(surface, (CX - 200, p.top + 446, 400, 18), max(0, s["money"]) / WIN_MONEY, gfx.PURPLE,
                     tr("goal_meter", now=yen(max(0, s["money"])), goal=yen(WIN_MONEY)))
        super().draw(surface, t)

    @staticmethod
    def _stat(surface, r, label, val, col, size):
        gfx.rrect(surface, r, (255, 208, 228), 16)
        gfx.rrect(surface, r.inflate(-6, -6), (255, 255, 255), 13)
        gfx.text(surface, label, (r.x + 16, r.centery), 17, gfx.INK, anchor="midleft", bold=False)
        if val:
            gfx.text(surface, val, (r.right - 16, r.centery), size, col, anchor="midright")


class MenuOverlay(Overlay):
    def __init__(self, scene, ready=False):
        self.ready = ready
        super().__init__(scene)

    def build(self):
        self.panel = pygame.Rect(0, 0, 440, 560 if not self.ready else 600)
        self.panel.center = (CX, CY + 10)
        p = self.panel
        y = p.top + (110 if self.ready else 64)
        sc = self.scene
        items = [("resume", self.close, "pink", 24), ("save_game", sc.open_saves, "mint", 20),
                 ("load_game", lambda: sc.push_overlay(SavesOverlay(sc, "load", sc.load_slot)), "mint", 20),
                 ("how_to_play", lambda: sc.push_overlay(HowToOverlay(sc)), "purple", 20),
                 ("settings", lambda: sc.push_overlay(SettingsOverlay(sc)), "yellow", 20),
                 ("quit_to_title", self._quit, "white", 20)]
        for key, fn, style, size in items:
            label = tr(key)
            h = 58 if key == "resume" else 52
            self.widgets.append(ui.Button((p.left + 50, y, p.w - 100, h), label, fn, style, size))
            y += h + 18

    def _quit(self):
        self.scene.push_overlay(ConfirmOverlay(self.scene, tr("quit_q"), tr("quit_msg"),
                                               tr("quit_to_title"), self.scene.quit_to_title))

    def draw(self, surface, t):
        ui.draw_panel(surface, self.panel, tr("ready") if self.ready else tr("paused"), "purple")
        if self.ready:
            gfx.paragraph(surface, tr("ready_msg"),
                          (CX, self.panel.top + 50), 17, 360, gfx.INK)
        super().draw(surface, t)


class GameOverOverlay(Overlay):
    dismissable = False

    def build(self):
        self.panel = pygame.Rect(0, 0, 620, 520)
        self.panel.center = (CX, CY)
        p = self.panel
        sc = self.scene
        self.widgets.append(ui.Button((CX - 230, p.bottom - 76, 210, 54), tr("load_a_save"),
                                      lambda: sc.push_overlay(SavesOverlay(sc, "load", sc.load_slot)), "mint", 20))
        self.widgets.append(ui.Button((CX + 20, p.bottom - 76, 210, 54), tr("main_menu"), sc.quit_to_title, "pink", 20))

    def draw(self, surface, t):
        s = self.scene.s
        p = self.panel
        ui.draw_panel(surface, p, tr("game_over"), "dark")
        gfx.text(surface, tr("out_of_cash"), (CX, p.top + 64), 26, gfx.INK)
        d = s["day"]
        gfx.text(surface, tr("closed_after", name=s["shop_name"], n=d) if d != 1 else tr("closed_after1", name=s["shop_name"]), (CX, p.top + 102), 18,
                 gfx.INK, bold=False)
        tot = s["totals"]
        for i, (label, val) in enumerate(((tr("total_sales"), yen(tot["revenue"])), (tr("happy_kids"), f"{tot['served']:,}"),
                                          (tr("best_day"), yen(tot["best_day"])), (tr("final_rating"), ""))):
            r = pygame.Rect(p.left + 34 + (i % 2) * 282, p.top + 136 + (i // 2) * 64, 270, 52)
            SummaryOverlay._stat(surface, r, label, val, gfx.INK, 20)
            if not val:
                ui.stars(surface, s["rep"], (r.right - 136, r.centery - 9), 17)
        art.draw_kid(surface, art._LOOKS[4], CX, p.top + 400, mood="sad")
        gfx.text(surface, tr("gameover_tip"), (CX, p.bottom - 100), 15, gfx.INK_SOFT, bold=False)
        super().draw(surface, t)


class WinOverlay(Overlay):
    dismissable = False

    def build(self):
        self.panel = pygame.Rect(0, 0, 640, 560)
        self.panel.center = (CX, CY + 10)
        self.art = pygame.Surface((520, 200)).convert()
        self.widgets.append(ui.Button((CX - 110, self.panel.bottom - 76, 220, 56), tr("keep_playing"), self.scene.keep_playing, "pink", 22))

    def draw(self, surface, t):
        s = self.scene.s
        p = self.panel
        ui.draw_panel(surface, p, tr("tycoon"), "mint")
        art.event_art(self.art, "opening", t)
        ar = self.art.get_rect(midtop=(CX, p.top + 50))
        gfx.rrect(surface, ar.inflate(10, 10), (255, 255, 255), 22)
        surface.blit(self.art, ar)
        gfx.text(surface, tr("reached", goal=yen(WIN_MONEY)), (CX, ar.bottom + 36), 26, gfx.INK)
        gfx.paragraph(surface, tr("win_msg", name=s["shop_name"]),
                      (CX, ar.bottom + 62), 18, 520, gfx.INK)
        gfx.text(surface, tr("win_stats", days=s["day"], kids=f"{s['totals']['served']:,}"), (CX, ar.bottom + 128), 16,
                 gfx.INK_SOFT, bold=False)
        super().draw(surface, t)
