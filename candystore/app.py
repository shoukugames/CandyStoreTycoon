"""Window, main loop, scenes and overlay panels.

The game draws onto a fixed 1280 x 720 canvas which is scaled to fit the window, so it
looks the same at any window size or in full screen (F11 or Alt+Enter).
"""
import os
import sys
import traceback

import pygame

from . import TITLE, __version__, storage
from .audio import Audio
from .paths import asset
from .ui import Toasts

W, H = 1280, 720


class Overlay:
    """A panel shown above a scene. While any overlay is open the store is paused."""
    dismissable = True     # Esc closes it

    def __init__(self, scene):
        self.scene = scene
        self.app = scene.app
        self.widgets = []
        self.build()

    def build(self):
        pass

    def refresh(self):
        self.widgets = []
        self.build()

    def close(self):
        self.scene.pop_overlay(self)

    def handle(self, event):
        for w in list(self.widgets):
            if w.handle(event, self.app):
                return True
        return event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)

    def update(self, dt):
        pass

    def draw(self, surface, t):
        for w in self.widgets:
            w.draw(surface, t)


class Scene:
    music = "title"

    def __init__(self, app):
        self.app = app
        self.overlays = []
        self.toasts = Toasts()
        self._veil = None

    # overlays
    def push_overlay(self, overlay):
        self.overlays.append(overlay)
        self._veil = None
        return overlay

    def pop_overlay(self, overlay=None):
        if overlay is None and self.overlays:
            self.overlays.pop()
        elif overlay in self.overlays:
            self.overlays.remove(overlay)
        self._veil = None
        if self.overlays:
            self.overlays[-1].refresh()

    def clear_overlays(self):
        self.overlays = []
        self._veil = None

    def refresh_overlays(self):
        for ov in self.overlays:
            ov.refresh()

    def toast(self, text, kind=""):
        self.toasts.add(text, kind)

    # lifecycle
    def enter(self):
        pass

    def leave(self):
        pass

    def handle(self, event):
        if self.overlays:
            top = self.overlays[-1]
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and top.dismissable:
                self.app.audio.play("click")
                top.close()
                return
            top.handle(event)
            return
        self.handle_world(event)

    def handle_world(self, event):
        pass

    def music_now(self):
        return self.music

    def update(self, dt):
        self.toasts.update(dt)
        if self.overlays:
            self.overlays[-1].update(dt)
        self.update_world(dt, paused=bool(self.overlays))

    def update_world(self, dt, paused):
        pass

    def draw(self, surface):
        if self.overlays and self._veil is not None:
            surface.blit(self._veil, (0, 0))
        else:
            self.draw_world(surface)
            if self.overlays:
                # soft blur + dim of the world behind the panels, made once per change
                veil = pygame.transform.smoothscale(surface, (W // 6, H // 6))
                veil = pygame.transform.smoothscale(veil, (W, H))
                shade = pygame.Surface((W, H), pygame.SRCALPHA)
                shade.fill((58, 24, 56, 120))
                veil.blit(shade, (0, 0))
                self._veil = veil
                surface.blit(veil, (0, 0))
        if self.overlays:
            self.overlays[-1].draw(surface, self.app.time)
        self.toasts.draw(surface)

    def draw_world(self, surface):
        pass


class App:
    def __init__(self, windowed=False, smoke=False):
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.key.set_repeat(400, 40)
        self.settings = storage.load_settings()
        self.smoke = smoke
        pygame.display.set_caption(f"{TITLE} v{__version__}")
        try:
            pygame.display.set_icon(pygame.image.load(asset("icon.png")))
        except (pygame.error, FileNotFoundError):
            pass
        self.fullscreen = self.settings.get("fullscreen", False) and not windowed and not smoke
        self._make_window()
        self.canvas = pygame.Surface((W, H)).convert()
        self.audio = Audio(self.settings)
        self.time = 0.0
        self.scene = None
        self.running = True
        self.mouse = (0, 0)

    def _make_window(self):
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            info = pygame.display.Info()
            w, h = W, H
            if info.current_w and info.current_w < W + 40:
                scale = (info.current_w - 60) / W
                w, h = int(W * scale), int(H * scale)
            self.window = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    def save_settings(self):
        storage.save_settings(self.settings)

    def switch(self, scene):
        if self.scene:
            self.scene.leave()
        self.scene = scene
        scene.enter()
        self.audio.music(scene.music)

    def set_music(self, which):
        self.audio.music(which)

    def _transform(self):
        ww, wh = self.window.get_size()
        scale = min(ww / W, wh / H)
        return scale, (ww - W * scale) / 2, (wh - H * scale) / 2

    def to_canvas(self, pos):
        scale, ox, oy = self._transform()
        return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))

    def present(self):
        scale, ox, oy = self._transform()
        if abs(scale - 1) < 0.001 and ox == 0 and oy == 0:
            self.window.blit(self.canvas, (0, 0))
        else:
            self.window.fill((58, 24, 56))
            size = (int(W * scale), int(H * scale))
            self.window.blit(pygame.transform.smoothscale(self.canvas, size), (int(ox), int(oy)))
        pygame.display.flip()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.settings["fullscreen"] = self.fullscreen
        self.save_settings()
        self._make_window()

    def run(self):
        from .scenes.title import TitleScene
        self.switch(TitleScene(self))
        clock = pygame.time.Clock()
        pygame.key.start_text_input()
        while self.running:
            dt = min(clock.tick(60) / 1000.0, 0.05)
            self.time += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_F11 or
                                                     (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)):
                    self.toggle_fullscreen()
                    continue
                if hasattr(event, "pos") and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                                                           pygame.MOUSEMOTION):
                    data = dict(event.dict)
                    data["pos"] = self.to_canvas(event.pos)
                    event = pygame.event.Event(event.type, data)
                self.scene.handle(event)
            self.mouse = self.to_canvas(pygame.mouse.get_pos())
            self.scene.update(dt)
            self.scene.draw(self.canvas)
            self.present()
        pygame.quit()


def _crash_log(error_text):
    try:
        path = os.path.join(storage.data_dir(), "crash.log")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(f"{TITLE} v{__version__}\n{error_text}")
        return path
    except OSError:
        return None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--version" in argv:
        print(f"{TITLE} v{__version__}")
        return 0
    if "--smoke-test" in argv:
        from .smoke import smoke_test
        i = argv.index("--smoke-test")
        out = argv[i + 1] if i + 1 < len(argv) else None
        return smoke_test(out)
    try:
        App(windowed="--windowed" in argv).run()
    except Exception:  # noqa: BLE001 - last-chance crash report
        text = traceback.format_exc()
        print(text, file=sys.stderr)
        _crash_log(text)
        return 1
    return 0
