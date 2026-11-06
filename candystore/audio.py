"""Music and sound effects. If there is no audio device the game simply stays silent."""
import os

import pygame

from .paths import asset

MUSIC = {"title": "bgm_title.ogg", "shop": "bgm_shop.ogg", "rush": "bgm_rush.ogg"}
EFFECTS = ["click", "hover", "pop", "coin", "restock", "sad", "door", "error", "morning", "day_end", "win", "save",
           "whoosh", "upgrade", "unlock"]
VOLUME = {"hover": 0.3, "click": 0.55, "door": 0.45, "whoosh": 0.5, "coin": 0.7, "pop": 0.6}


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.ok = False
        self.sounds = {}
        self.current = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 1024)
            pygame.mixer.set_num_channels(20)
            for name in EFFECTS:
                self.sounds[name] = pygame.mixer.Sound(asset("audio", name + ".wav"))
            self.apply_volume()
            self.ok = True
        except (pygame.error, FileNotFoundError, OSError) as error:
            print(f"Audio disabled: {error}")

    def apply_volume(self):
        sv = self.settings.get("sfx_volume", 0.8)
        for name, snd in self.sounds.items():
            snd.set_volume(VOLUME.get(name, 0.8) * sv)
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(0.7 * self.settings.get("music_volume", 0.6))

    def play(self, name):
        if self.ok and self.settings["sfx"] and name in self.sounds:
            self.sounds[name].play()

    def music(self, which):
        if not self.ok or which is None:
            return
        if not self.settings["music"]:
            pygame.mixer.music.fadeout(500)
            self.current = None
            return
        if which == self.current:
            return
        self.current = which
        try:
            pygame.mixer.music.fadeout(600)
            pygame.mixer.music.load(asset("audio", MUSIC[which]))
            self.apply_volume()
            pygame.mixer.music.play(-1, fade_ms=2500)
        except pygame.error as error:
            print(f"Music unavailable: {error}")

    def refresh_music(self, which):
        self.current = None
        self.music(which)


def exists():
    return os.path.exists(asset("audio", "click.wav"))
