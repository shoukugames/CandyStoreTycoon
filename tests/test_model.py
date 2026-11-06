import json
import random

from candystore import model
from candystore.model import Game


def new_game(seed=1):
    g = Game("Test Shop", rng=random.Random(seed))
    g.begin_day()
    assert g.start_prep()
    return g


def play_day(g, restock=True):
    ok, _ = g.open_store()
    assert ok
    for _ in range(200 * 20):
        if g.s["phase"] != "rush":
            break
        g.update(0.05)
        if restock:
            for i, sh in enumerate(g.s["shelves"]):
                if sh["count"] < 2 and not sh["restock"] and g.s["pantry"][sh["type"]] > 0:
                    g.begin_restock(i, sh["type"])
    assert g.s["phase"] == "summary"


def test_new_game_starts_with_1000_yen_and_grand_opening():
    g = new_game()
    assert g.s["money"] == 1000 and g.s["day"] == 1 and g.s["event"] == "opening"
    assert g.pantry_cap() == 50 and g.shelf_cap() == 10 and len(g.s["shelves"]) == 3


def test_buying_respects_money_and_pantry_space():
    g = new_game()
    assert g.buy("lolli", 10) == (True, "")
    assert g.s["money"] == 800 and g.s["pantry"]["lolli"] == 10
    assert not g.buy("choc", 100)[0]                # not enough money / space
    assert g.buy("lolli", "max")[0]
    assert g.pantry_used() == 50                    # pantry full at 50 (max fills the space)
    ok, msg = g.buy("lolli", 1)
    assert not ok and "full" in msg


def test_locked_candy_cannot_be_bought_until_its_day():
    g = new_game()
    assert not g.unlocked("jaw") and not g.buy("jaw", 1)[0]
    g.s["day"] = 4
    assert g.unlocked("jaw") and g.buy("jaw", 1)[0]


def test_shelves_hold_ten_and_switching_returns_items_to_pantry():
    g = new_game()
    g.buy("lolli", 15)
    assert g.shelf_add(0, "fill") == 10 and g.s["pantry"]["lolli"] == 5
    assert g.shelf_add(0, 1) == 0                   # shelf full
    g.set_shelf_type(0, "gummy")
    assert g.s["shelves"][0]["count"] == 0 and g.s["pantry"]["lolli"] == 15


def test_store_will_not_open_with_empty_shelves():
    g = new_game()
    ok, msg = g.open_store()
    assert not ok and "empty" in msg


def test_a_full_day_sells_candy_and_charges_rent():
    g = new_game()
    g.buy("lolli", 20)
    g.buy("gummy", 10)
    g.fill_all()
    money_before = g.s["money"]
    play_day(g)
    sm = g.s["summary"]
    assert sm["served"] > 0 and sm["revenue"] > 0
    assert sm["rent"] == model.rent_for(1)
    assert g.s["money"] == money_before + sm["revenue"] - sm["rent"]


def test_heatwave_melts_chocolate_and_doubles_ice_pop_price():
    g = new_game()
    g.s["pantry"]["choc"] = 7
    g.pick_event = lambda: "heatwave"
    g.s["phase"] = "summary"
    g.begin_day()
    assert g.s["pantry"]["choc"] == 2 and g.s["today"]["melted"] == 5
    assert g.price("ice") == 2 * model.PRODUCTS["ice"]["price"]


def test_wholesaler_sale_halves_lollipop_cost():
    g = new_game()
    g.s["event"] = "sale"
    assert g.cost("lolli") == model.PRODUCTS["lolli"]["cost"] // 2


def test_recess_rush_brings_a_wave_of_kids():
    g = new_game()
    g.s["event"] = "recess"
    g.buy("lolli", 30)
    g.fill_all()
    g.open_store()
    seen = set()
    while g.s["phase"] == "rush" and g.s["rush"]["elapsed"] < 30:
        g.update(0.05)
        seen.update(c["id"] for c in g.s["rush"]["customers"])
    assert any(k == "wave" for k, _ in g.pop_events()) or len(seen) >= 12


def test_impatient_kids_lower_the_rating():
    g = new_game()
    g.buy("lolli", 1)
    g.shelf_add(0, 1)
    play_day(g, restock=False)
    assert g.s["summary"]["unhappy"] > 0
    assert g.s["rep"] < 3.0


def test_restock_moves_pantry_stock_onto_shelf_and_can_switch_type():
    g = new_game()
    g.buy("lolli", 5)
    g.buy("gummy", 5)
    g.shelf_add(0, "fill")
    assert g.begin_restock(0, "gummy")[0]
    g.s["phase"] = "rush"
    g.s["rush"] = {"elapsed": 0, "spawn_t": 999, "customers": [], "served": 0, "unhappy": 0, "revenue": 0, "sold": {},
                   "rep_start": 3, "waves": [], "queue": [], "closed": False}
    g.update(2.0)
    sh = g.s["shelves"][0]
    assert sh["type"] == "gummy" and sh["count"] == 5 and g.s["pantry"]["lolli"] == 5


def test_game_over_when_out_of_money_and_candy():
    g = new_game()
    g.s["money"] = 5
    g.s["phase"] = "summary"
    assert g.next_day() == "gameover"


def test_reaching_the_goal_wins_once():
    g = new_game()
    g.s["money"] = model.WIN_MONEY
    g.s["phase"] = "summary"
    assert g.next_day() == "win"
    g.s["phase"] = "summary"
    assert g.next_day() == "day"


def test_upgrades_add_space_shelves_and_capacity():
    g = new_game()
    g.s["money"] = 100000
    assert g.buy_upgrade("pantry")[0] and g.pantry_cap() == 75
    assert g.buy_upgrade("shelf")[0] and len(g.s["shelves"]) == 4
    assert g.buy_upgrade("shelf_size")[0] and g.shelf_cap() == 14
    g.buy_upgrade("stocker")
    assert g.restock_time() == 0.8
    assert not g.buy_upgrade("stocker")[0]          # only one level


def test_state_round_trips_through_json_mid_rush():
    g = new_game()
    g.buy("lolli", 20)
    g.fill_all()
    g.open_store()
    for _ in range(400):
        g.update(0.05)
    data = json.loads(json.dumps(g.to_dict()))
    h = Game.from_dict(data, rng=random.Random(9))
    assert h.s["rush"]["customers"] == g.s["rush"]["customers"]
    for _ in range(100):
        h.update(0.05)                              # keeps playing after a reload


def test_shelf_layout_fits_between_door_and_counter():
    for n in range(3, 6):
        rects = model.shelf_layout(n)
        assert rects[0][0] >= 140 and rects[-1][0] + rects[-1][2] <= 1140
