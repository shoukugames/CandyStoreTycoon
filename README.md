# Candy Store Tycoon v0.1.0

A bright, cheerful candy-shop management game with relaxing ambient music.
**Recommended for ages 10+.**

You start with ¥1,000 and an empty shop. Buy candy at the wholesale market,
keep it in your backroom pantry, choose what goes on the display shelves, then
open the doors. Colourful kids arrive with cravings and a patience timer. Keep
them happy, pay the rent, grow the store and become a **Candy Tycoon**.

- **Created by:** Shawn Rapaz
- **Made with:** Claude Code
- **Publisher:** Shouku Games, <https://shoukugames.org/>, info@shoukugames.org
- **Released:** November 6, 2026
- **License:** GNU General Public License v3.0 (see `LICENSE`)

## Features

- **The Register:** start with ¥1,000. Run out of money *and* candy and it is game over.
- **The Pantry:** backroom storage for 50 items (upgradable). When it is full,
  you can't buy more until you make space.
- **The Shop Floor:** kids only buy what is on the display shelves. Each shelf
  holds 10 of one candy, so you pick between cheap, fast-selling lollipops and
  slower, high-profit chocolate.
- **The Rush:** kids walk in with a thought bubble showing what they want and a
  patience ring. Click a shelf to restock it from the pantry before it runs out.
- **Six candies:** Lollipop, Gummy Bears, Ice Pop and Chocolate Bar from the
  start, then Jawbreaker (day 4) and Cotton Candy (day 7).
- **Morning events:** Summer Heatwave (chocolate melts, ice pops sell for double),
  School Recess Rush (huge waves of kids), Wholesaler Sale (half-price
  lollipops), Rainy Day, Birthday Party, Candy Festival, Cocoa Shortage, Sunny
  Saturday and Spooky Costume Day.
- **Upgrades:** Bigger Pantry, Extra Shelf, Taller Shelves, Speedy Stocker, Neon
  Candy Sign and Jukebox.
- **Goal:** reach ¥25,000 to become a Candy Tycoon. You can keep playing after that.
- **Three save slots.** You can save at any time: in the morning, during prep, in
  the middle of a rush (the store pauses while the menu is open) or at the end
  of the day. Each slot shows a picture of your shop, the day, money and rating.
- **Graphics and sound:** all art is drawn in code and smoothed by supersampling.
  The music is three calm, original ambient loops (title, shop, store open)
  built from soft pads, a music box, an electric piano and a kalimba.
- **Credits screen:** includes the full GPL-3.0 licence viewer.

## Controls

| Action | Control |
| --- | --- |
| Everything | Mouse |
| Restock a shelf during the rush | Click the shelf |
| Pause menu (save, load, settings) | Esc or the menu button |
| Music on/off | M |
| 1x / 2x speed during the rush | Space |
| Full screen | F11 or Alt+Enter |

## Install

- **Windows:** run `CandyStoreTycoon-v0.1.0.exe`. There is nothing to install.
- **Debian / Ubuntu:** `sudo apt install ./candystoretycoon_v0.1.0_amd64.deb`,
  then start *Candy Store Tycoon* from the games menu or type `candystoretycoon`.

Saves and settings are stored in `%APPDATA%\CandyStoreTycoon` on Windows and
`~/.local/share/candystoretycoon` on Linux, so they survive updates.

## Run from source

```sh
python3 -m pip install -r requirements.txt
python3 run_game.py              # add --windowed to ignore the full-screen setting
python3 run_game.py --version
```

## Build the installers

```sh
./build.sh                       # both
packaging/build_linux.sh         # dist/candystoretycoon_v0.1.0_amd64.deb
packaging/build_windows.sh       # dist/CandyStoreTycoon-v0.1.0.exe (built on Linux with Wine)
```

The Linux build needs `python3-venv`, `dpkg-deb` and `fakeroot`. The Windows
build needs `wine`, `xvfb-run` and `curl`. On the first run it installs Windows
Python from python.org into a private Wine prefix under `build/`. Each script
finishes by running the packaged game's built-in self-test.

## Development

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m pytest                # game logic and save slots
python3 run_game.py --smoke-test result.txt   # plays through every screen
python3 tools/make_audio.py      # regenerate music and sounds (needs numpy + ffmpeg)
python3 tools/make_icon.py       # regenerate the icon (needs Pillow)
```

Set `CANDYSTORE_SHOTS=<folder>` while running the smoke test to save a
screenshot of every screen.

Project layout: `candystore/model.py` is the simulation (no pygame, fully
tested), `art.py` and `gfx.py` draw everything, `ui.py` holds the widgets,
`scenes/` holds the screens and panels, and `storage.py` handles the save
slots. `web/` contains the earlier browser prototype.

## Reporting bugs

See [BUGREPORT.md](BUGREPORT.md), or email **info@shoukugames.org**.

## Credits

- Game design, direction and production: **Shawn Rapaz**
- Built with **Claude Code** (Anthropic)
- Font: **Fredoka**, copyright 2016 The Fredoka Project Authors, SIL Open Font License 1.1
  (`assets/fonts/OFL-Fredoka.txt`)
- Music and sound effects: original, synthesised by `tools/make_audio.py`
- Made with Python and pygame

Copyright (C) 2026 Shawn Rapaz. This program is free software: you can
redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. It is distributed WITHOUT ANY
WARRANTY. See `LICENSE` for details.
