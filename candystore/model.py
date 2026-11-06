"""The candy store simulation: money, pantry, shelves, customers and daily events.

Pure Python with no pygame, so it is easy to test. The whole game state is a plain
JSON-friendly dict (self.s), which is exactly what goes into a save slot.
Presentation hooks (coins, sounds, toasts) are queued in self.events for the scene.
"""
import copy
import random

W, H = 1280, 720
DAY_LENGTH = 80.0          # seconds of real time per shop day
WIN_MONEY = 25000
START_MONEY = 1000
BASE_PANTRY = 50
BASE_SHELF = 10

PRODUCTS = {
    "lolli":   {"cost": 20, "price": 45,  "pop": 34, "unlock": 1, "color": (255, 95, 162)},
    "gummy":   {"cost": 35, "price": 75,  "pop": 24, "unlock": 1, "color": (255, 154, 60)},
    "ice":     {"cost": 25, "price": 55,  "pop": 13, "unlock": 1, "color": (47, 168, 255)},
    "choc":    {"cost": 70, "price": 160, "pop": 12, "unlock": 1, "color": (139, 74, 43)},
    "jaw":     {"cost": 50, "price": 115, "pop": 10, "unlock": 4, "color": (122, 92, 255)},
    "cotton":  {"cost": 60, "price": 140, "pop": 11, "unlock": 7, "color": (255, 143, 209)},
}
ORDER = ["lolli", "gummy", "ice", "choc", "jaw", "cotton"]

EVENTS = {
    "opening": {},
    "normal": {},
    "heatwave": {"melt": {"choc": 5}, "sell_mult": {"ice": 2.0}, "demand_mult": {"ice": 3.0, "choc": 0.5}},
    "recess": {"spawn_mult": 1.7, "waves": [18.0, 46.0], "patience_mult": 0.85},
    "sale": {"cost_mult": {"lolli": 0.5}},
    "rain": {"spawn_mult": 0.75, "demand_mult": {"choc": 2.5, "ice": 0.3}, "patience_mult": 1.2},
    "party": {"demand_mult": {"gummy": 2.5}, "big_order": "gummy"},
    "festival": {"sell_all": 1.25, "spawn_mult": 1.15},
    "cocoa": {"cost_mult": {"choc": 1.5}, "sell_mult": {"choc": 1.3}},
    "sunny": {"spawn_mult": 1.35, "demand_mult": {"ice": 1.5}},
    "spooky": {"demand_mult": {"jaw": 2.5, "lolli": 1.5}, "spawn_mult": 1.1, "min_day": 5},
}
EVENT_POOL = [("normal", 18), ("heatwave", 11), ("recess", 11), ("sale", 11), ("rain", 9), ("party", 9),
              ("festival", 7), ("cocoa", 7), ("sunny", 9), ("spooky", 6)]

UPGRADES = [
    {"id": "pantry", "cost": [900, 1800, 3200], "icon": "box"},
    {"id": "shelf", "cost": [1200, 2600], "icon": "shelf"},
    {"id": "shelf_size", "cost": [1000, 2400], "icon": "tall"},
    {"id": "stocker", "cost": [800], "icon": "bolt"},
    {"id": "sign", "cost": [1500, 3200], "icon": "sign"},
    {"id": "jukebox", "cost": [1100], "icon": "music"},
]
UPGRADE_BY_ID = {u["id"]: u for u in UPGRADES}

# Kid appearance palette sizes (art.py owns the actual colours)
LOOK_SIZES = {"skin": 6, "hair": 8, "shirt": 8, "pants": 6, "shoe": 5, "style": 6, "cap": 8}

FLOOR_Y = 470


def shelf_layout(n):
    left, right, gap = 150, 1130, 18
    w = min(196, (right - left - gap * (n - 1)) / n)
    total = w * n + gap * (n - 1)
    start = left + (right - left - total) / 2
    return [(start + i * (w + gap), 222, w, 248) for i in range(n)]


def rent_for(day):
    return min(450, 60 + day * 15)


def new_state(shop_name="Sweet Treats"):
    return {
        "version": 1, "shop_name": shop_name, "day": 0, "money": START_MONEY, "rep": 3.0,
        "pantry": {k: 0 for k in ORDER},
        "upgrades": {u["id"]: 0 for u in UPGRADES},
        "shelves": [{"type": "lolli", "count": 0, "restock": None},
                    {"type": "gummy", "count": 0, "restock": None},
                    {"type": "choc", "count": 0, "restock": None}],
        "event": "opening", "last_event": None, "phase": "morning", "today": {}, "rush": None, "summary": None,
        "totals": {"revenue": 0, "served": 0, "unhappy": 0, "best_day": 0}, "won": False, "next_id": 1,
    }


class Game:
    """Messages returned by actions are (key, params) tuples; i18n.msg() turns them into text."""

    def __init__(self, shop_name="Sweet Treats", state=None, rng=None):
        self.rng = rng or random.Random()
        self.s = state if state is not None else new_state(shop_name)
        self.events = []
        self._normalise()

    # ---------- persistence ----------
    def _normalise(self):
        base = new_state(self.s.get("shop_name", "Sweet Treats"))
        for key, value in base.items():
            self.s.setdefault(key, copy.deepcopy(value))
        for k in ORDER:
            self.s["pantry"].setdefault(k, 0)
        for u in UPGRADES:
            self.s["upgrades"].setdefault(u["id"], 0)
        for shelf in self.s["shelves"]:
            shelf.setdefault("restock", None)
        self.sync_shelves()

    def to_dict(self):
        return copy.deepcopy(self.s)

    @classmethod
    def from_dict(cls, data, rng=None):
        return cls(state=copy.deepcopy(data), rng=rng)

    # ---------- helpers ----------
    def emit(self, kind, **data):
        self.events.append((kind, data))

    def pop_events(self):
        out, self.events = self.events, []
        return out

    @property
    def ev(self):
        return EVENTS.get(self.s["event"], EVENTS["normal"])

    def pantry_cap(self):
        return BASE_PANTRY + 25 * self.s["upgrades"]["pantry"]

    def shelf_cap(self):
        return BASE_SHELF + 4 * self.s["upgrades"]["shelf_size"]

    def pantry_used(self):
        return sum(self.s["pantry"].values())

    def shelf_stock(self):
        return sum(sh["count"] for sh in self.s["shelves"])

    def unlocked(self, k):
        return self.s["day"] >= PRODUCTS[k]["unlock"]

    def cost(self, k):
        return max(1, round(PRODUCTS[k]["cost"] * self.ev.get("cost_mult", {}).get(k, 1)))

    def price(self, k):
        return round(PRODUCTS[k]["price"] * self.ev.get("sell_mult", {}).get(k, 1) * self.ev.get("sell_all", 1))

    def price_boosted(self, k):
        return self.price(k) > PRODUCTS[k]["price"]

    def cheapest_cost(self):
        return min(self.cost(k) for k in ORDER if self.unlocked(k))

    def sync_shelves(self):
        want = 3 + self.s["upgrades"]["shelf"]
        extra = ["ice", "gummy"]
        while len(self.s["shelves"]) < want:
            self.s["shelves"].append({"type": extra[(len(self.s["shelves"]) - 3) % 2], "count": 0, "restock": None})

    def shelf_rects(self):
        return shelf_layout(len(self.s["shelves"]))

    def shelf_center(self, i):
        x, _y, w, _h = self.shelf_rects()[i]
        return x + w / 2

    # ---------- day flow ----------
    def pick_event(self):
        if self.s["day"] == 1:
            return "opening"
        pool = [(e, w) for e, w in EVENT_POOL
                if e != self.s["last_event"] and EVENTS[e].get("min_day", 0) <= self.s["day"]]
        total = sum(w for _, w in pool)
        r = self.rng.random() * total
        for e, w in pool:
            r -= w
            if r <= 0:
                return e
        return "normal"

    def begin_day(self):
        s = self.s
        s["day"] += 1
        s["last_event"] = s["event"]
        s["event"] = self.pick_event()
        s["today"] = {"melted": 0, "unlocked": [k for k in ORDER if PRODUCTS[k]["unlock"] == s["day"] and s["day"] > 1]}
        for k, n in self.ev.get("melt", {}).items():
            lost = min(n, s["pantry"][k])
            s["pantry"][k] -= lost
            s["today"]["melted"] += lost
        s["phase"] = "morning"
        s["rush"] = None

    def start_prep(self):
        """Morning card closed. Returns False if the game is over."""
        self.s["phase"] = "prep"
        return not self.check_game_over()

    def check_game_over(self):
        if self.pantry_used() + self.shelf_stock() == 0 and self.s["money"] < self.cheapest_cost():
            self.s["phase"] = "gameover"
            return True
        return False

    def open_store(self):
        if self.s["phase"] != "prep":
            return False, ("not_prep", {})
        if self.shelf_stock() == 0:
            return False, ("shelves_empty", {})
        self.s["phase"] = "rush"
        self.s["rush"] = {"elapsed": 0.0, "spawn_t": 1.0, "customers": [], "served": 0, "unhappy": 0, "revenue": 0,
                          "sold": {}, "rep_start": self.s["rep"], "waves": list(self.ev.get("waves", [])),
                          "queue": [], "closed": False}
        return True, ("open", {})

    # ---------- market ----------
    def max_buy(self, k):
        return max(0, min(self.s["money"] // self.cost(k), self.pantry_cap() - self.pantry_used()))

    def buy(self, k, n):
        if not self.unlocked(k):
            return False, ("locked", {})
        room = self.pantry_cap() - self.pantry_used()
        c = self.cost(k)
        if n == "max":
            n = self.max_buy(k)
        if room <= 0:
            return False, ("pantry_full", {})
        if n > room:
            return False, ("space_left", {"n": room})
        if n <= 0 or n * c > self.s["money"]:
            return False, ("no_money", {})
        self.s["money"] -= n * c
        self.s["pantry"][k] += n
        return True, None

    def buy_upgrade(self, uid):
        u = UPGRADE_BY_ID[uid]
        lvl = self.s["upgrades"][uid]
        if lvl >= len(u["cost"]):
            return False, ("maxed", {})
        c = u["cost"][lvl]
        if self.s["money"] < c:
            return False, ("no_money", {})
        self.s["money"] -= c
        self.s["upgrades"][uid] += 1
        self.sync_shelves()
        return True, ("upgraded", {"upgrade": uid})

    # ---------- shelves (prep) ----------
    def set_shelf_type(self, i, k):
        sh = self.s["shelves"][i]
        if not self.unlocked(k) or sh["type"] == k:
            return False
        self.s["pantry"][sh["type"]] += sh["count"]   # items go back where they came from
        sh["count"] = 0
        sh["type"] = k
        return True

    def shelf_add(self, i, n):
        sh, cap = self.s["shelves"][i], self.shelf_cap()
        if n == "fill":
            n = cap - sh["count"]
        if n > 0:
            n = min(n, cap - sh["count"], self.s["pantry"][sh["type"]])
        else:
            n = max(n, -sh["count"])
        if not n:
            return 0
        sh["count"] += n
        self.s["pantry"][sh["type"]] -= n
        return n

    def fill_all(self):
        return sum(self.shelf_add(i, "fill") for i in range(len(self.s["shelves"])))

    # ---------- rush ----------
    def restock_time(self):
        return 0.8 if self.s["upgrades"]["stocker"] else 1.6

    def begin_restock(self, i, k):
        sh = self.s["shelves"][i]
        if sh["restock"]:
            return False, ("restocking", {})
        if self.s["pantry"].get(k, 0) <= 0:
            return False, ("none_in_pantry", {"type": k})
        if sh["type"] == k and sh["count"] >= self.shelf_cap():
            return False, ("shelf_full", {})
        t = self.restock_time()
        sh["restock"] = {"type": k, "t": t, "total": t}
        return True, None

    def complete_restock(self, i):
        sh = self.s["shelves"][i]
        k = sh["restock"]["type"]
        sh["restock"] = None
        if sh["type"] != k:
            self.s["pantry"][sh["type"]] += sh["count"]
            sh["count"] = 0
            sh["type"] = k
        n = min(self.shelf_cap() - sh["count"], self.s["pantry"][k])
        sh["count"] += n
        self.s["pantry"][k] -= n
        self.emit("restocked", shelf=i, n=n, type=k)

    def spawn_interval(self):
        d = self.s["day"]
        day_mult = 0.6 + d * 0.12 if d <= 3 else min(1.45, 1 + (d - 4) * 0.025)
        rep_mult = 0.55 + self.s["rep"] * 0.15
        sign_mult = 1 + 0.2 * self.s["upgrades"]["sign"]
        return 3.0 / (self.ev.get("spawn_mult", 1) * day_mult * rep_mult * sign_mult)

    def pick_craving(self, exclude=None):
        dm = self.ev.get("demand_mult", {})
        opts = [(k, PRODUCTS[k]["pop"] * dm.get(k, 1)) for k in ORDER if self.unlocked(k) and k != exclude]
        r = self.rng.random() * sum(w for _, w in opts)
        for k, w in opts:
            r -= w
            if r <= 0:
                return k
        return opts[0][0]

    def random_look(self):
        r = self.rng
        look = {key: r.randrange(n) for key, n in LOOK_SIZES.items()}
        look.update(stripe=r.random() < 0.4, size=round(0.88 + r.random() * 0.2, 3), blink=round(r.random() * 4, 3))
        return look

    def spawn_customer(self):
        r, rng, ev = self.s["rush"], self.rng, self.ev
        craving = self.pick_craving()
        alt = self.pick_craving(craving) if rng.random() < 0.3 else None
        qty = 1 if rng.random() < 0.7 else (2 if rng.random() < 0.75 else 3)
        if ev.get("big_order") == craving and rng.random() < 0.55:
            qty = 3 + rng.randrange(3)
        patience = rng.uniform(9, 13) * ev.get("patience_mult", 1) * (1.35 if self.s["upgrades"]["jukebox"] else 1)
        c = {"id": self.s["next_id"], "look": self.random_look(), "x": -50.0, "y": rng.uniform(580, 615),
             "state": "walk", "tx": 0.0, "shelf": -1, "craving": craving, "alt": alt, "want": craving, "qty": qty,
             "patience": patience, "max_patience": patience, "phase": rng.random() * 6, "mood": "happy",
             "timer": 0.0, "speed": rng.uniform(150, 190), "holding": None, "check": 0.0, "flip": False,
             "walking": False, "no_shelf": False, "gone": False}
        self.s["next_id"] += 1
        self._target(c)
        r["customers"].append(c)
        self.emit("door")

    def find_shelf(self, c, need_stock):
        for k in (c["craving"], c["alt"]):
            if not k:
                continue
            best = -1
            for i, sh in enumerate(self.s["shelves"]):
                if sh["type"] == k and (not need_stock or sh["count"] > 0):
                    if best < 0 or sh["count"] > self.s["shelves"][best]["count"]:
                        best = i
            if best >= 0:
                return best, k
        return None

    def _go_to(self, c, found):
        c["shelf"], c["want"] = found
        c["tx"] = self.shelf_center(found[0]) + self.rng.uniform(-55, 55)
        c["state"] = "walk"

    def _target(self, c):
        found = self.find_shelf(c, True) or self.find_shelf(c, False)
        if found:
            self._go_to(c, found)
        else:
            c["shelf"], c["want"], c["tx"], c["state"] = -1, c["craving"], self.rng.uniform(300, 1000), "walk"

    def update(self, dt):
        if self.s["phase"] != "rush" or not self.s["rush"]:
            return
        r = self.s["rush"]
        r["elapsed"] += dt
        is_open = r["elapsed"] < DAY_LENGTH
        if is_open:
            r["spawn_t"] -= dt
            if r["spawn_t"] <= 0:
                self.spawn_customer()
                r["spawn_t"] = self.spawn_interval() * self.rng.uniform(0.55, 1.45)
            if r["waves"] and r["elapsed"] >= r["waves"][0]:
                r["waves"].pop(0)
                r["queue"].extend(r["elapsed"] + k * 0.45 for k in range(6))
                self.emit("wave")
            while r["queue"] and r["elapsed"] >= r["queue"][0]:
                r["queue"].pop(0)
                self.spawn_customer()
        elif not r["closed"]:
            r["closed"] = True
            self.emit("closing")
            for c in r["customers"]:
                if c["state"] == "wait" or (c["state"] == "walk" and not c["holding"] and not self.find_shelf(c, True)):
                    self._leave(c, "wait")

        for i, sh in enumerate(self.s["shelves"]):
            if sh["restock"]:
                sh["restock"]["t"] -= dt
                if sh["restock"]["t"] <= 0:
                    self.complete_restock(i)

        for c in r["customers"]:
            self._update_customer(c, dt)
        r["customers"] = [c for c in r["customers"] if not c["gone"]]
        if not is_open and not r["customers"]:
            self.end_day()

    def _leave(self, c, mood):
        c["state"], c["mood"], c["tx"] = "leave", mood, -80.0

    def _move(self, c, tx, dt):
        d = tx - c["x"]
        step = c["speed"] * dt
        c["flip"] = d < 0
        if abs(d) <= step:
            c["x"] = tx
            return True
        c["x"] += step if d > 0 else -step
        c["phase"] += dt * 11
        return False

    def _update_customer(self, c, dt):
        c["walking"] = False
        st = c["state"]
        if st == "walk":
            c["walking"] = True
            if self._move(c, c["tx"], dt):
                c["state"], c["timer"], c["walking"] = "look", 0.45, False
        elif st == "look":
            c["timer"] -= dt
            if c["timer"] <= 0:
                self._try_buy(c)
        elif st == "wait":
            c["patience"] -= dt
            f = c["patience"] / c["max_patience"]
            c["mood"] = "happy" if f > 0.6 else ("wait" if f > 0.3 else "worried")
            c["check"] -= dt
            if c["check"] <= 0:
                c["check"] = 0.25
                found = self.find_shelf(c, True)
                if found:
                    c["no_shelf"] = False
                    self._go_to(c, found)
                    return
            if c["patience"] <= 0:
                self._leave(c, "sad")
                self.s["rush"]["unhappy"] += 1
                self.s["rep"] = max(1.0, self.s["rep"] - (0.025 if c["no_shelf"] else 0.05))
                self.emit("unhappy", x=c["x"], y=c["y"], craving=c["craving"], no_shelf=c["no_shelf"])
        elif st in ("exit", "leave"):
            c["walking"] = True
            if self._move(c, 1360 if st == "exit" else c["tx"], dt):
                c["gone"] = True
            if st == "leave" and c["x"] < 120:
                self.emit("door")

    def _try_buy(self, c):
        r = self.s["rush"]
        sh = self.s["shelves"][c["shelf"]] if c["shelf"] >= 0 else None
        if sh and sh["type"] == c["want"] and sh["count"] > 0:
            n = min(c["qty"], sh["count"])
            sh["count"] -= n
            earn = n * self.price(sh["type"])
            self.s["money"] += earn
            r["revenue"] += earn
            r["served"] += 1
            r["sold"][sh["type"]] = r["sold"].get(sh["type"], 0) + n
            self.s["rep"] = min(5.0, self.s["rep"] + (0.035 if n == c["qty"] else 0.015))
            c["holding"], c["mood"], c["state"] = sh["type"], "excited", "exit"
            self.emit("sale", x=c["x"], y=c["y"], amount=earn)
            if sh["count"] == 0:
                self.emit("empty", type=sh["type"])
            return
        found = self.find_shelf(c, True)
        if found and found[0] != c["shelf"]:
            self._go_to(c, found)
        elif r["closed"]:
            self._leave(c, "wait")
        else:
            c["state"] = "wait"
            if not found and not self.find_shelf(c, False):
                c["no_shelf"] = True
                c["patience"] = min(c["patience"], c["max_patience"] * 0.45)

    def end_day(self):
        s, r = self.s, self.s["rush"]
        rent = rent_for(s["day"])
        s["money"] -= rent
        s["summary"] = {"day": s["day"], "served": r["served"], "unhappy": r["unhappy"], "revenue": r["revenue"],
                        "rent": rent, "profit": r["revenue"] - rent, "sold": dict(r["sold"]),
                        "rep_start": r["rep_start"], "rep_end": s["rep"], "event": s["event"]}
        t = s["totals"]
        t["revenue"] += r["revenue"]
        t["served"] += r["served"]
        t["unhappy"] += r["unhappy"]
        t["best_day"] = max(t["best_day"], r["revenue"])
        for sh in s["shelves"]:
            sh["restock"] = None
        s["rush"] = None
        s["phase"] = "summary"
        self.emit("day_end")

    def next_day(self):
        """After the summary. Returns 'gameover', 'win' or 'day'."""
        if self.check_game_over():
            return "gameover"
        if not self.s["won"] and self.s["money"] >= WIN_MONEY:
            self.s["won"] = True
            return "win"
        self.begin_day()
        return "day"
