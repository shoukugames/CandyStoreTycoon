import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402
import pytest  # noqa: E402

from candystore import gfx, i18n  # noqa: E402


@pytest.fixture(autouse=True)
def video():
    pygame.init()
    pygame.display.set_mode((8, 8))
    yield
    i18n.set_lang("en")


def test_formats_follow_the_language():
    i18n.set_lang("en")
    assert i18n.day_label(3) == "Day 3" and i18n.clock(14, 30) == "2:30 PM"
    assert i18n.long_date("2026-11-06") == "November 6, 2026"
    i18n.set_lang("ja")
    assert i18n.day_label(3) == "3日目" and i18n.clock(14, 30) == "午後2:30"
    assert i18n.long_date("2026-11-06") == "2026年11月6日"
    assert i18n.yen(1234) == "¥1,234" and i18n.yen(-5) == "-¥5"


def test_japanese_text_always_gets_the_japanese_font():
    i18n.set_lang("en")
    latin = gfx.font(20, sample="Sweet Treats")
    japanese = gfx.font(20, sample="ハニーやさん")
    assert latin is not japanese
    assert japanese is gfx.font(20, latin=False, sample="日本語")
    # no "tofu": every Japanese character has a real glyph in the chosen font
    assert all(m is not None for m in japanese.metrics("ハニーやさん日本語"))


def test_switching_language_redraws_cached_text_sprites():
    from candystore import art
    i18n.set_lang("en")
    english = art.shelf_label(180, "lolli", 45, False, False)
    i18n.set_lang("ja")
    japanese = art.shelf_label(180, "lolli", 45, False, False)
    assert english is not japanese


def test_cjk_wrapping_never_starts_a_line_with_closing_punctuation():
    i18n.set_lang("ja")
    for line in gfx.wrap(i18n.t("b4"), 16, 260)[1:]:
        assert line and line[0] not in gfx.NO_LINE_START


def test_random_shop_names_match_the_language():
    import random
    i18n.set_lang("ja")
    assert gfx._has_cjk(i18n.random_shop_name(random.Random(1)))
    i18n.set_lang("en")
    assert " " in i18n.random_shop_name(random.Random(1))
