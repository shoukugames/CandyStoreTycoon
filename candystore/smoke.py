"""Automatic self-test: visits every screen and plays real shop days.

Used by the build scripts to prove a packaged game really starts and plays:
    candystoretycoon --smoke-test result.txt
Set CANDYSTORE_SHOTS=<folder> to also save a screenshot of each screen.
"""
import os
import random
import sys
import tempfile
import traceback


def smoke_test(out_path=None):
    os.environ.setdefault("CANDYSTORE_DATA", tempfile.mkdtemp(prefix="candystore-smoke-"))
    shots = os.environ.get("CANDYSTORE_SHOTS")
    lines = []
    ok = True
    try:
        import pygame

        from . import model, storage
        from .app import App
        from .scenes import game as game_mod
        from .scenes.credits import CreditsScene, LicenseScene
        from .scenes.game import GameScene
        from .scenes.panels import HowToOverlay, NameOverlay, SavesOverlay, SettingsOverlay
        from .scenes.title import TitleScene

        app = App(windowed=True, smoke=True)
        count = {"n": 0}
        prefix = {"p": ""}

        def frames(scene, n=10, name=None, dt=1 / 60):
            for _ in range(n):
                pygame.event.pump()
                app.time += dt
                scene.update(dt)
                scene.draw(app.canvas)
                app.present()
            if shots and name:
                os.makedirs(shots, exist_ok=True)
                count["n"] += 1
                pygame.image.save(app.canvas, os.path.join(shots, f"{prefix['p']}{count['n']:02d}_{name}.png"))

        def click(scene, pos):
            for kind in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                data = {"pos": pos, "button": 1} if kind != pygame.MOUSEMOTION else {"pos": pos, "rel": (0, 0), "buttons": (0, 0, 0)}
                scene.handle(pygame.event.Event(kind, data))

        from . import i18n
        for language in ("ja", "en"):
            i18n.set_lang(language)
            prefix["p"] = language + "_"
            # ---- title and its panels, credits, licence ----
            title = TitleScene(app)
            app.switch(title)
            frames(title, 30, "title")
            for cls in (HowToOverlay, SettingsOverlay):
                title.push_overlay(cls(title))
                frames(title, 4, cls.__name__)
                title.clear_overlays()
            title.push_overlay(NameOverlay(title, lambda n: None))
            frames(title, 4, "name_shop")
            title.clear_overlays()
            from .scenes.tutorial import PAGES, TutorialScene
            tut = TutorialScene(app)
            app.switch(tut)
            for page in range(PAGES):
                tut.go(page)
                frames(tut, 4, f"tutorial_{page + 1}")
            tut.start_game()
            assert app.scene.overlays, "tutorial did not lead into a new game"
            credits = CreditsScene(app)
            app.switch(credits)
            frames(credits, 6, "credits")
            lic = LicenseScene(app)
            app.switch(lic)
            lic.scroll = 900
            frames(lic, 4, "license")
            assert len(lic.lines) > 400, "licence text missing"
            lines.append("screens ok")

            # ---- a real game: morning -> buy -> shelves -> rush -> summary ----
            scene = GameScene(app, shop_name="Smoke Sweets")
            app.switch(scene)
            frames(scene, 20, "morning")
            assert scene.s["phase"] == "morning"
            click(scene, scene.overlays[-1].widgets[0].rect.center)       # Let's Go!
            frames(scene, 5, "prep_empty")
            assert scene.s["phase"] == "prep", scene.s["phase"]
            scene.open_market()
            frames(scene, 4, "market")
            g = scene.game
            assert g.buy("lolli", 20)[0] and g.buy("gummy", 10)[0] and g.buy("choc", 3)[0]
            scene.overlays[-1].tab = "upg"
            scene.changed()
            frames(scene, 4, "market_upgrades")
            scene.clear_overlays()
            scene.open_shelves()
            g.fill_all()
            scene.changed()
            frames(scene, 4, "shelves")
            scene.clear_overlays()
            scene.open_store()
            assert scene.s["phase"] == "rush"
            sold_before = 0
            shot_taken = False
            for step in range(60 * 200):
                frames(scene, 1, None, 1 / 30)
                if scene.s["phase"] != "rush":
                    break
                for i, sh in enumerate(scene.s["shelves"]):
                    if sh["count"] < 3 and not sh["restock"] and scene.s["pantry"][sh["type"]] > 0:
                        scene.open_restock(i)
                        frames(scene, 1, "restock_popup" if not shot_taken else None)
                        scene.do_restock(i, sh["type"])
                        shot_taken = True
                if step == 600:
                    frames(scene, 1, "rush")
                    # save in the middle of the rush, load it back, and keep playing
                    assert scene.save_to(2), "mid-rush save failed"
                    kids = len(scene.s["rush"]["customers"])
                    scene.load_slot(2)
                    scene = app.scene
                    assert scene.s["phase"] == "rush" and len(scene.s["rush"]["customers"]) == kids, "rush did not reload"
                    frames(scene, 2, "loaded_mid_rush")
                    scene.clear_overlays()
                sold_before = scene.s["rush"]["served"] if scene.s["rush"] else sold_before
            assert scene.s["phase"] == "summary", f"day did not end ({scene.s['phase']})"
            frames(scene, 10, "summary")
            sm = scene.s["summary"]
            assert sm["served"] > 0, "nobody bought anything"
            lines.append(f"day 1: served {sm['served']}, unhappy {sm['unhappy']}, sales {sm['revenue']}")

            # ---- saves panel, menu, next day, quick simulated days ----
            scene.open_saves()
            frames(scene, 4, "saves")
            assert storage.read_slot(2) is not None
            scene.clear_overlays()
            scene.push_overlay(game_mod.MenuOverlay(scene))
            frames(scene, 3, "menu")
            scene.clear_overlays()
            rng = random.Random(3)
            for _ in range(4):
                scene.game.s["phase"] = "summary"
                scene.next_day()
                frames(scene, 3, f"morning_{scene.s['event']}")
                scene.start_prep()
                if scene.s["phase"] == "gameover":
                    break
                g = scene.game
                for k in model.ORDER:
                    if g.unlocked(k):
                        g.buy(k, rng.randint(3, 10))
                g.fill_all()
                scene.open_store()
                while scene.s["phase"] == "rush":
                    g.update(1 / 20)
                    for i, sh in enumerate(scene.s["shelves"]):
                        if sh["count"] < 2 and not sh["restock"] and scene.s["pantry"][sh["type"]] > 0:
                            g.begin_restock(i, sh["type"])
                scene.game.pop_events()
            lines.append(f"played to day {scene.s['day']} with {scene.s['money']} yen")

            # ---- game over and win panels ----
            scene.clear_overlays()
            scene.push_overlay(game_mod.WinOverlay(scene))
            frames(scene, 4, "win")
            scene.clear_overlays()
            scene.push_overlay(game_mod.GameOverOverlay(scene))
            frames(scene, 4, "gameover")

            # ---- title load menu sees the saves ----
            title = TitleScene(app)
            app.switch(title)
            title.push_overlay(SavesOverlay(title, "load", title.load_slot))
            frames(title, 4, "title_load")
            title.load_slot(2)
            assert isinstance(app.scene, GameScene)
            lines.append("saves ok")
            lines.append(f"{language} ok")
        pygame.quit()
    except Exception:  # noqa: BLE001 - report every failure
        ok = False
        lines.append("FAILED\n" + traceback.format_exc())
    text = ("OK " if ok else "") + "; ".join(lines)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1
