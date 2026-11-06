#!/usr/bin/env python3
"""Draw the game icon with the game's own art: assets/icon.png and assets/icon.ico.

Run this only when the design changes. Needs Pillow for the .ico file.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

from candystore import art  # noqa: E402

pygame.init()
pygame.display.set_mode((16, 16))
png = os.path.join(ROOT, "assets", "icon.png")
pygame.image.save(art.app_icon(512), png)
Image.open(png).save(os.path.join(ROOT, "assets", "icon.ico"),
                     sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("assets/icon.png, assets/icon.ico")
