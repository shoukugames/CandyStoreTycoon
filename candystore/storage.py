"""Settings and the three save slots, stored as JSON in the per-user data folder.

Files live outside the install folder so they survive updates and the game works
from a read-only install. A damaged file is set aside (renamed .corrupt), never fatal.
"""
import json
import os
import sys
import tempfile
import time

SLOTS = 3
DEFAULT_SETTINGS = {"music": True, "sfx": True, "music_volume": 0.6, "sfx_volume": 0.8, "fullscreen": False}


def data_dir():
    override = os.environ.get("CANDYSTORE_DATA")
    if override:
        path = override
    elif sys.platform == "win32":
        path = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "CandyStoreTycoon")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        path = os.path.join(base, "candystoretycoon")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        path = os.path.join(tempfile.gettempdir(), "candystoretycoon")
        os.makedirs(path, exist_ok=True)
    return path


def _path(name):
    return os.path.join(data_dir(), name)


def _load(name, default):
    path = _path(name)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, type(default)):
            return data
        raise ValueError("unexpected structure")
    except FileNotFoundError:
        return default
    except (OSError, ValueError):
        try:
            os.replace(path, path + ".corrupt")
        except OSError:
            pass
        return default


def _save(name, data):
    path = _path(name)
    temp = path + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=1, ensure_ascii=False)
        os.replace(temp, path)
        return True
    except OSError as error:
        print(f"Could not save {name}: {error}", file=sys.stderr)
        return False


def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    settings.update(_load("settings.json", {}))
    return settings


def save_settings(settings):
    _save("settings.json", settings)


# ---------- save slots ----------

def slot_file(n):
    return f"slot{n}.json"


def thumb_path(n):
    return _path(f"slot{n}.png")


def read_slot(n):
    """Return {"meta": {...}, "state": {...}} or None for an empty/damaged slot."""
    if not os.path.exists(_path(slot_file(n))):
        return None
    data = _load(slot_file(n), {})
    if not data.get("state") or not data.get("meta"):
        return None
    return data


def write_slot(n, state, thumbnail_saver=None):
    meta = {
        "shop_name": state.get("shop_name", ""),
        "day": state.get("day", 1),
        "money": state.get("money", 0),
        "rep": state.get("rep", 3),
        "phase": state.get("phase", "prep"),
        "saved_at": time.time(),
    }
    ok = _save(slot_file(n), {"meta": meta, "state": state})
    if ok and thumbnail_saver:
        try:
            thumbnail_saver(thumb_path(n))
        except Exception as error:  # noqa: BLE001 - a thumbnail is optional
            print(f"Thumbnail not saved: {error}", file=sys.stderr)
    return ok


def delete_slot(n):
    for path in (_path(slot_file(n)), thumb_path(n)):
        try:
            os.remove(path)
        except OSError:
            pass
