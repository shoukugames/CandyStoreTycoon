import os

import pytest

from candystore import storage


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("CANDYSTORE_DATA", str(tmp_path))
    return tmp_path


def test_three_slots_save_load_and_delete(data_dir):
    for n in range(1, storage.SLOTS + 1):
        assert storage.read_slot(n) is None
        assert storage.write_slot(n, {"shop_name": f"Shop {n}", "day": n, "money": 100 * n, "phase": "prep"})
    assert storage.read_slot(2)["meta"]["shop_name"] == "Shop 2"
    assert storage.read_slot(3)["state"]["money"] == 300
    storage.delete_slot(2)
    assert storage.read_slot(2) is None and storage.read_slot(1) is not None


def test_thumbnail_is_written_next_to_the_slot(data_dir):
    def saver(path):
        with open(path, "wb") as handle:
            handle.write(b"png")
    storage.write_slot(1, {"shop_name": "A"}, saver)
    assert os.path.exists(storage.thumb_path(1))


def test_damaged_slot_is_set_aside_not_fatal(data_dir):
    (data_dir / "slot1.json").write_text("{not json", encoding="utf-8")
    assert storage.read_slot(1) is None
    assert (data_dir / "slot1.json.corrupt").exists()


def test_settings_have_defaults_and_persist(data_dir):
    s = storage.load_settings()
    assert s["music"] is True and 0 <= s["music_volume"] <= 1
    s["music"] = False
    storage.save_settings(s)
    assert storage.load_settings()["music"] is False
