"""Tutorial: an illustrated, page-by-page guide to playing and succeeding, in English or Japanese."""
import math
import random

import pygame

from .. import art, gfx, i18n, ui
from ..app import W, H, Scene
from ..i18n import t
from ..model import WIN_MONEY, rent_for, shelf_layout

PAGES = 9
PANEL = pygame.Rect(0, 0, 1060, 610)
PANEL.center = (W // 2, H // 2 + 22)
PIC = pygame.Rect(PANEL.left + 36, PANEL.top + 66, 450, 420)
TEXT_X = PIC.right + 36
TEXT_W = PANEL.right - 40 - TEXT_X

_LOOKS = [art.random_look(random.Random(i * 7 + 1)) for i in range(4)]


class TutorialScene(Scene):
    music = "title"

    def __init__(self, app, page=0):
        super().__init__(app)
        self.backdrop = art.TitleBackdrop()
        self.dt = 0.0
        self.page = page
        self.thumb = None
        self.event_surf = pygame.Surface((560, 250)).convert()
        self.build()

    # ---------- navigation ----------
    def build(self):
        p = PANEL
        y = p.bottom - 72
        last = self.page == PAGES - 1
        self.buttons = [ui.Button((p.left + 36, y, 170, 52), t("back"), self.prev, "white", 20, enabled=self.page > 0),
                        ui.Button((p.right - 36 - 340, y, 150, 52), t("tut_title_btn"), self.to_title, "white", 18)]
        if last:
            self.buttons.append(ui.Button((p.right - 36 - 176, y - 2, 176, 56), t("tut_start"), self.start_game, "pink",
                                          18 if i18n.lang() == "en" else 19))
        else:
            self.buttons.append(ui.Button((p.right - 36 - 176, y - 2, 176, 56), t("next"), self.next, "pink", 22))

    def go(self, page):
        self.page = max(0, min(PAGES - 1, page))
        self.build()

    def next(self):
        self.go(self.page + 1)

    def prev(self):
        self.go(self.page - 1)

    def to_title(self):
        from .title import TitleScene
        self.app.switch(TitleScene(self.app))

    def start_game(self):
        from .panels import NameOverlay
        from .title import TitleScene
        title = TitleScene(self.app)
        self.app.switch(title)
        title.push_overlay(NameOverlay(title, title.start_game))

    def handle_world(self, event):
        for b in self.buttons:
            if b.handle(event, self.app):
                return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.audio.play("click")
                self.to_title()
            elif event.key in (pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE) and self.page < PAGES - 1:
                self.app.audio.play("click")
                self.next()
            elif event.key == pygame.K_LEFT and self.page > 0:
                self.app.audio.play("click")
                self.prev()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._dots()):
                if r.inflate(10, 10).collidepoint(event.pos):
                    self.app.audio.play("click")
                    self.go(i)

    def update_world(self, dt, paused):
        self.dt = dt

    # ---------- drawing ----------
    def _dots(self):
        gap = 22
        x0 = PANEL.centerx - 30 - (PAGES - 1) * gap / 2
        return [pygame.Rect(int(x0 + i * gap) - 6, PANEL.bottom - 52, 12, 12) for i in range(PAGES)]

    def draw_world(self, surface):
        tm = self.app.time
        self.backdrop.draw(surface, tm, self.dt)
        ui.draw_panel(surface, PANEL, t("tutorial"), "mint")
        n = self.page + 1
        # picture frame
        gfx.rrect(surface, PIC.inflate(12, 12).move(0, 4), (255, 208, 228), 26)
        gfx.rrect(surface, PIC.inflate(12, 12), (255, 255, 255), 26)
        pic = pygame.Surface(PIC.size, pygame.SRCALPHA)
        pic.blit(gfx.vgrad(PIC.w, PIC.h, (255, 240, 248), (255, 225, 238)), (0, 0))
        getattr(self, f"_pic{n}")(pic, tm)
        mask = gfx.rounded(PIC.w, PIC.h, 20, (255, 255, 255))
        pic.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(pic, PIC)
        # words
        goal = i18n.yen(WIN_MONEY)
        y = PANEL.top + 70
        gfx.text(surface, t("tut_page", n=n, m=PAGES), (TEXT_X, y), 15, gfx.MINT_D, anchor="midleft")
        y = gfx.paragraph(surface, t(f"tut{n}_h"), (TEXT_X, y + 16), 30, TEXT_W, gfx.PINK_D, bold=True, anchor="topleft",
                          spacing=1.15)
        body_key = f"tut{n}_b"
        if body_key in i18n.STRINGS:
            y = gfx.paragraph(surface, t(body_key, goal=goal), (TEXT_X, y + 8), 18, TEXT_W, gfx.INK, anchor="topleft",
                              spacing=1.35)
        tips = [t(f"tut{n}_t{k}", goal=goal) for k in range(1, 7) if f"tut{n}_t{k}" in i18n.STRINGS]
        y += 14
        for i, tip in enumerate(tips):
            art.blit_candy(surface, ["lolli", "gummy", "choc", "ice", "jaw", "cotton"][i % 6], (TEXT_X + 14, y + 12), 26, i)
            y = gfx.paragraph(surface, tip, (TEXT_X + 36, y), 16, TEXT_W - 36, gfx.INK, anchor="topleft", spacing=1.3) + 8
        # page dots
        for i, r in enumerate(self._dots()):
            gfx.aa_circle(surface, gfx.PINK if i == self.page else (243, 210, 226), r.center, 7 if i == self.page else 5)
        for b in self.buttons:
            b.draw(surface, tm)

    # ---------- one picture per page ----------
    def _shop_thumb(self):
        if self.thumb is None or self.thumb[0] != i18n.lang():
            big = pygame.Surface((W, H)).convert()
            art.shop(big, 2.0, t("default_shop"), 0.6, True)
            sample = [("lolli", 9), ("gummy", 7), ("choc", 4)]
            for rect, (kind, count) in zip(shelf_layout(3), sample):
                art.shelf(big, rect, {"type": kind, "count": count, "restock": None}, 10,
                          {"lolli": 45, "gummy": 75, "choc": 160}[kind], False, False, 0, True)
            big.blit(art.counter(), (1130, 344))
            for i, (x, mood, hold) in enumerate(((330, "excited", "lolli"), (640, "happy", None), (900, "happy", "gummy"))):
                art.draw_kid(big, _LOOKS[i], x, 600, mood=mood, holding=hold)
            self.thumb = (i18n.lang(), pygame.transform.smoothscale(big, (450, 253)))
        return self.thumb[1]

    def _pic1(self, s, tm):
        s.blit(self._shop_thumb(), (0, 20))
        c = art.coin(34)
        bob = math.sin(tm * 3) * 5
        s.blit(c, c.get_rect(center=(110, 335 + bob)))
        ui.chip(s, t("tut1_t", goal=i18n.yen(WIN_MONEY)), (260, 336), "good", 20)
        st = art.star(16)
        for i in range(3):
            s.blit(st, (330 + i * 30, 380 + math.sin(tm * 4 + i) * 3))

    def _pic2(self, s, tm):
        steps = [("tut2_s1", "tut2_d1", (255, 207, 58)), ("tut2_s2", "tut2_d2", gfx.MINT),
                 ("tut2_s3", "tut2_d3", gfx.PINK), ("tut2_s4", "tut2_d4", gfx.PURPLE)]
        cells = [(120, 110), (330, 110), (330, 300), (120, 300)]
        for (a, b), (c, d) in zip(cells, cells[1:] + cells[:1]):
            pygame.draw.line(s, (230, 180, 205), (a, b), (c, d), 6)
        for i, ((head, desc, col), (cx, cy)) in enumerate(zip(steps, cells)):
            active = int(tm * 0.8) % 4 == i
            r = 54 if active else 48
            gfx.aa_circle(s, gfx.darken(col, 0.2), (cx, cy + 3), r)
            gfx.aa_circle(s, col, (cx, cy), r)
            if i == 0:
                face = art.sun_face(26, False)
                s.blit(face, face.get_rect(center=(cx, cy - 6)))
            elif i == 1:
                ic = ui.icon_surface("cart", 40)
                s.blit(ic, ic.get_rect(center=(cx, cy - 6)))
            elif i == 2:
                ic = ui.icon_surface("door", 40)
                s.blit(ic, ic.get_rect(center=(cx, cy - 6)))
            else:
                gfx.aa_circle(s, (255, 246, 200), (cx - 4, cy - 8), 18)
                gfx.aa_circle(s, col, (cx + 6, cy - 14), 15)
            gfx.text(s, str(i + 1), (cx - r + 10, cy - r + 10), 18, (255, 255, 255), stroke=gfx.darken(col, 0.35), stroke_w=2)
            gfx.text(s, t(head), (cx, cy + 26), 18, (255, 255, 255), shadow=gfx.darken(col, 0.4))
            gfx.text(s, t(desc), (cx, cy + r + 18), 15, gfx.INK)

    def _pic3(self, s, tm):
        for row, (kind, cost, price) in enumerate((("lolli", 20, 45), ("choc", 70, 160))):
            r = pygame.Rect(30, 26 + row * 150, 390, 130)
            gfx.rrect(s, r, (255, 208, 228), 18)
            gfx.rrect(s, r.inflate(-6, -6), (255, 255, 255), 15)
            art.blit_candy(s, kind, (r.x + 62, r.centery), 86 + math.sin(tm * 3 + row) * 3, row)
            gfx.text(s, i18n.prod(kind), (r.x + 120, r.y + 30), 20, gfx.INK, anchor="midleft")
            buy, sell = t("buy_price", n=cost), t("sell_price", n=price)
            ui.chip(s, buy, (r.x + 120 + gfx.text_size(buy, 15)[0] / 2 + 14, r.y + 66), "bad", 15)
            ui.chip(s, sell, (r.right - 20 - gfx.text_size(sell, 15)[0] / 2 - 14, r.y + 66), "good", 15)
            gfx.text(s, t("tut3_profit", n=price - cost), (r.x + 120, r.y + 104), 19, gfx.GREEN_TXT, anchor="midleft")
        gfx.text(s, t("pantry"), (40, 352), 18, gfx.INK, anchor="midleft")
        fill = 0.3 + 0.5 * (0.5 + 0.5 * math.sin(tm * 1.2))
        ui.meter(s, (110, 341, 300, 24), fill, gfx.MINT, f"{int(fill * 50)} / 50")
        box = ui.icon_surface("box", 40)
        s.blit(box, (40, 368))

    def _pic4(self, s, tm):
        count = 3 + int(tm * 2) % 8
        big = pygame.Surface((300, 330), pygame.SRCALPHA)
        art.shelf(big, (50, 30, 196, 248), {"type": "lolli", "count": count, "restock": None}, 10, 45, False, True, tm, False,
                  t("click_stock"))
        s.blit(big, (75, 30))
        tile_y = 352
        for i, k in enumerate(("lolli", "gummy", "ice", "choc")):
            r = pygame.Rect(64 + i * 84, tile_y, 66, 54)
            gfx.rrect(s, r, gfx.PINK if i == 0 else (255, 230, 240), 12)
            gfx.rrect(s, r.inflate(-6, -6), (255, 227, 240) if i == 0 else (255, 246, 250), 9)
            art.blit_candy(s, k, r.center, 40, i)

    def _pic5(self, s, tm):
        s.blit(gfx.vgrad(450, 170, (255, 194, 220), (255, 225, 238)), (0, 250))
        for i, (x, frac, kind, alt, label, col) in enumerate(((120, 0.8, "lolli", None, "tut5_patient", gfx.GREEN_TXT),
                                                              (320, 0.25, "choc", "gummy", "tut5_hurry", gfx.RED_TXT))):
            L = _LOOKS[i + 1]
            mood = "happy" if frac > 0.6 else "worried"
            art.draw_kid(s, L, x, 360, mood=mood)
            pulse = frac if i == 0 else 0.25 + 0.05 * math.sin(tm * 6)
            art.bubble(s, x + 30, 360 - 158 * L["size"], kind, pulse, 1 if i == 0 else 2, alt, tm + i)
            gfx.text(s, t(label), (x, 392), 17, col)
        art.blit_candy(s, "lolli", (60, 70), 40)
        for i in range(5):
            ang = tm * 2 + i
            h = art.heart(20)
            s.blit(h, (190 + math.cos(ang) * 12 + i * 4, 40 - (tm * 30 + i * 20) % 40))

    def _pic6(self, s, tm):
        for i, eid in enumerate(("heatwave", "recess", "sale", "rain")):
            art.event_art(self.event_surf, eid, tm)
            cell = pygame.Rect(12 + (i % 2) * 219, 44 + (i // 2) * 176, 207, 160)
            gfx.rrect(s, cell, (255, 208, 228), 16)
            gfx.rrect(s, cell.inflate(-6, -6), (255, 255, 255), 13)
            img = pygame.transform.smoothscale(self.event_surf, (cell.w - 14, int((cell.w - 14) * 250 / 560)))
            s.blit(img, (cell.x + 7, cell.y + 7))
            gfx.paragraph(s, i18n.ev_name(eid), (cell.centerx, cell.y + img.get_height() + 18), 17, cell.w - 16,
                          gfx.PINK_D, bold=True, spacing=1.15)

    def _pic7(self, s, tm):
        ui.stars(s, 3.5 + math.sin(tm) * 1.2, (85, 40), 52, 4)
        r = pygame.Rect(40, 130, 370, 70)
        gfx.rrect(s, r, (255, 208, 228), 16)
        gfx.rrect(s, r.inflate(-6, -6), (255, 255, 255), 13)
        gfx.text(s, t("tut7_rent"), (r.x + 20, r.centery), 19, gfx.INK, anchor="midleft", bold=False)
        day = 1 + int(tm * 0.7) % 20
        gfx.text(s, f"{i18n.day_label(day)}  -{i18n.yen(rent_for(day))}", (r.right - 20, r.centery), 22, gfx.RED_TXT,
                 anchor="midright")
        frac = 0.15 + 0.7 * (0.5 + 0.5 * math.sin(tm * 0.6))
        ui.meter(s, (40, 240, 370, 22), frac, gfx.PURPLE,
                 t("goal_meter", now=i18n.yen(int(WIN_MONEY * frac)), goal=i18n.yen(WIN_MONEY)))
        for i in range(6):
            c = art.coin(16)
            s.blit(c, (70 + i * 52, 300 + math.sin(tm * 3 + i) * 8))
        art.draw_kid(s, _LOOKS[0], 225, 412, mood="excited", holding="choc")

    def _pic8(self, s, tm):
        kinds = ["lolli", "gummy", "choc", "ice", "jaw", "cotton"]
        for i, k in enumerate(kinds):
            a = tm * 0.5 + i * math.tau / 6
            art.blit_candy(s, k, (225 + math.cos(a) * 150, 170 + math.sin(a) * 110), 74 + math.sin(a) * 10, i)
        for i, icon in enumerate(("box", "bolt")):
            img = art.upgrade_icon(icon, 70)
            s.blit(img, img.get_rect(center=(180 + i * 90, 170)))
        st = art.star(26)
        s.blit(st, st.get_rect(center=(225, 330 + math.sin(tm * 3) * 6)))

    def _pic9(self, s, tm):
        s.blit(self._shop_thumb(), (0, 0))
        s.blit(gfx.vgrad(450, 170, (155, 230, 201), (127, 217, 184)), (0, 250))
        for i in range(3):
            x = (tm * 60 + i * 150) % 560 - 60
            art.draw_kid(s, _LOOKS[i], x, 400 - (i % 2) * 10, mood="excited", phase=tm * 9 + i, walking=True,
                         holding=["lolli", "ice", "cotton"][i])
