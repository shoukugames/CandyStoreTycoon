"""Every piece of on-screen text, in English and Japanese.

t("key", name=value) returns the text for the current language. Switching language
clears the cached sprites that contain text so everything redraws in the new language.
"""
import datetime
import locale
import os

LANGS = ("en", "ja")
LANG = {"current": "en"}


def lang():
    return LANG["current"]


def default_language():
    """Japanese if the computer is set to Japanese, otherwise English."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        if os.environ.get(var, "").lower().startswith("ja"):
            return "ja"
    try:
        loc = locale.getlocale()[0] or ""
        if loc.lower().startswith(("ja", "japanese")):
            return "ja"
    except (ValueError, TypeError):
        pass
    if os.name == "nt":
        try:
            import ctypes
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF == 0x11:   # LANG_JAPANESE
                return "ja"
        except (AttributeError, OSError):
            pass
    return "en"


def set_lang(code):
    if code not in LANGS:
        code = "en"
    if code == LANG["current"]:
        return
    LANG["current"] = code
    clear_text_caches()


def clear_text_caches():
    from . import art, gfx, ui
    gfx.font.cache_clear()
    gfx._text_cache.clear()
    for fn in (art.shop_base, art.shelf_label, art._open_sign, art.counter, art.price_tag, art._banner,
               art.upgrade_icon, ui.ribbon_img):
        fn.cache_clear()


def t(key, **kw):
    pair = STRINGS.get(key)
    if pair is None:
        return key
    text = pair[1] if LANG["current"] == "ja" else pair[0]
    return text.format(**kw) if kw else text


def pick(en, ja):
    return ja if LANG["current"] == "ja" else en


# ---------------- formats ----------------

def yen(n):
    n = int(round(n))
    return ("-" if n < 0 else "") + f"¥{abs(n):,}"


def day_label(n):
    return pick(f"Day {n}", f"{n}日目")


def clock(hh, mm):
    h12 = hh - 12 if hh > 12 else hh
    if LANG["current"] == "ja":
        return f"{'午後' if hh >= 12 else '午前'}{h12}:{mm:02d}"
    return f"{h12}:{mm:02d} {'PM' if hh >= 12 else 'AM'}"


def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return pick(f"{d.strftime('%B')} {d.day}, {d.year}", f"{d.year}年{d.month}月{d.day}日")


# ---------------- game content ----------------

PRODUCTS = {
    "lolli":  (("Lollipop", "ペロペロキャンディ"), ("Cheap and sells super fast.", "安くて、すごくよく売れる！")),
    "gummy":  (("Gummy Bears", "クマのグミ"), ("Chewy, fruity, always popular.", "もちもちフルーツ味。大人気！")),
    "ice":    (("Ice Pop", "アイスキャンディ"), ("Cool treat. Wild on hot days!", "ひんやり。暑い日に大人気！")),
    "choc":   (("Chocolate Bar", "板チョコ"), ("Sells slower, but BIG profit.", "売れるのはゆっくり、でも大もうけ！")),
    "jaw":    (("Jawbreaker", "にじ色アメ玉"), ("Rainbow layers that last.", "にじ色の層がずっと続く！")),
    "cotton": (("Cotton Candy", "わたあめ"), ("Fluffy sugar clouds. Trendy!", "ふわふわの雲。今はやり！")),
}


def prod(k):
    return pick(*PRODUCTS[k][0])


def prod_desc(k):
    return pick(*PRODUCTS[k][1])


EVENTS = {
    "opening": (("Grand Opening!", "グランドオープン！"),
                ("Your candy store opens today! Buy candy at the Market, stock your shelves, then open the doors.",
                 "今日はお店のオープン日！市場でおかしを買って、たなにならべたら、お店を開けよう。"),
                [("info", "Fewer customers while word spreads", "うわさが広まるまでお客さんは少なめ")]),
    "normal": (("A Sweet Ordinary Day", "いつもの楽しい一日"),
               ("Nothing unusual today. A perfect day to plan ahead!", "今日はとくに何もなし。先の計画を立てるチャンス！"),
               [("info", "Normal prices and customers", "ねだんもお客さんもいつもどおり")]),
    "heatwave": (("Summer Heatwave", "夏の猛暑"),
                 ("It is SO hot! Chocolate in your pantry melted, but everyone wants ice pops.",
                  "とっても暑い！倉庫のチョコがとけちゃった。でもみんなアイスキャンディがほしい！"),
                 [("bad", "Up to 5 chocolate bars melt", "板チョコが最大5個とける"),
                  ("good", "Ice Pops sell for DOUBLE", "アイスキャンディが2倍のねだんで売れる")]),
    "recess": (("School Recess Rush", "休み時間ラッシュ"),
               ("The school bell rang! A huge wave of hungry kids is coming. Restock twice as fast!",
                "学校のチャイムが鳴った！おなかペコペコの子どもたちが大集合。2倍の速さで補充しよう！"),
               [("good", "TONS of customers", "お客さんがいっぱい"), ("bad", "Kids are less patient", "子どもたちは待てる時間が短め")]),
    "sale": (("Wholesaler Sale", "問屋さんの大売り出し"),
             ("Lollipops are half price at the market today! Stock up while it is cheap.",
              "今日は市場でペロペロキャンディが半額！安いうちに仕入れよう。"),
             [("good", "Lollipops cost 50% less", "ペロペロキャンディが半額")]),
    "rain": (("Rainy Day", "雨の日"),
             ("Pitter-patter! Fewer kids come out, but the ones who do want cozy chocolate.",
              "ザーザー！お客さんは少ないけど、来た子はあったかいチョコがほしいみたい。"),
             [("bad", "Fewer customers", "お客さんが少なめ"), ("good", "Chocolate in demand", "チョコが人気"),
              ("good", "Kids wait longer", "子どもたちが長く待ってくれる")]),
    "party": (("Birthday Party", "お誕生日会"),
              ("A birthday party is happening nearby. Party kids buy gummy bears by the handful!",
               "近くでお誕生日会！パーティーの子たちはクマのグミをどっさり買うよ。"),
              [("good", "Gummy Bear demand way up", "クマのグミが大人気"), ("info", "Some kids buy 3 to 5", "3〜5個まとめて買う子も")]),
    "festival": (("Candy Festival", "おかしまつり"),
                 ("The town candy festival is on! Everyone happily pays a little more.",
                  "町のおかしまつり！みんな少し高くてもよろこんで買ってくれる。"),
                 [("good", "All candy sells for +25%", "全部のおかしが25%高く売れる"), ("good", "More customers", "お客さんが多め")]),
    "cocoa": (("Cocoa Shortage", "カカオ不足"),
              ("Cocoa beans are hard to find. Chocolate costs more, but sells for more too.",
               "カカオ豆が足りない！チョコの仕入れは高いけど、高く売れるよ。"),
              [("bad", "Chocolate costs +50%", "チョコの仕入れが50%アップ"), ("good", "Chocolate sells for +30%", "チョコが30%高く売れる")]),
    "sunny": (("Sunny Saturday", "晴れた土曜日"),
              ("No school and lovely weather! Families are out walking all day.",
               "学校はお休み、いいお天気！一日中、家族づれがおさんぽしているよ。"),
              [("good", "Lots more customers", "お客さんがたくさん")]),
    "spooky": (("Spooky Costume Day", "おばけ仮装デー"),
               ("Kids are out in costumes and they LOVE jawbreakers and lollipops.",
                "仮装した子どもたちは、にじ色アメ玉とペロペロキャンディが大好き！"),
               [("good", "Jawbreakers and Lollipops in demand", "アメ玉とペロペロキャンディが人気")]),
}


def ev_name(e):
    return pick(*EVENTS.get(e, EVENTS["normal"])[0])


def ev_desc(e):
    return pick(*EVENTS.get(e, EVENTS["normal"])[1])


def ev_effects(e):
    return [(kind, pick(en, ja)) for kind, en, ja in EVENTS.get(e, EVENTS["normal"])[2]]


UPGRADES = {
    "pantry": (("Bigger Pantry", "大きな倉庫"), ("+25 storage slots", "倉庫が25個ぶん広くなる")),
    "shelf": (("Extra Shelf", "たなを追加"), ("Another display shelf", "ちんれつだなが1つふえる")),
    "shelf_size": (("Taller Shelves", "背の高いたな"), ("+4 items per shelf", "どのたなも4個多く置ける")),
    "stocker": (("Speedy Stocker", "スピード補充"), ("Restock twice as fast", "補充が2倍速くなる")),
    "sign": (("Neon Candy Sign", "ネオンかんばん"), ("+20% customers per level", "レベルごとにお客さん20%アップ")),
    "jukebox": (("Jukebox", "ジュークボックス"), ("Kids wait 35% longer", "子どもが35%長く待ってくれる")),
}


def upg_name(uid):
    return pick(*UPGRADES[uid][0])


def upg_desc(uid):
    return pick(*UPGRADES[uid][1])


def msg(m):
    """Turn a model message (key, params) into text."""
    if not m:
        return ""
    key, params = m
    params = dict(params)
    if "type" in params:
        params["name"] = prod(params.pop("type"))
    if "upgrade" in params:
        params["name"] = upg_name(params.pop("upgrade"))
    return t("msg." + key, **params)


# ---------------- interface text ----------------

STRINGS = {
    # title
    "new_game": ("New Game", "はじめから"),
    "load_game": ("Load Game", "つづきから"),
    "how_to_play": ("How to Play", "遊び方"),
    "settings": ("Settings", "設定"),
    "credits": ("Credits", "クレジット"),
    "quit": ("Quit", "終了"),
    "title_ja": ("", "キャンディストア・タイクーン"),
    "ages_line1": ("Recommended for", "対象年齢"),
    "ages_line2": ("ages 10 and up", "10才以上"),
    "language": ("Language", "言語"),
    # common
    "back": ("Back", "もどる"),
    "done": ("Done", "とじる"),
    "cancel": ("Cancel", "キャンセル"),
    "on": ("On", "ON"),
    "off": ("Off", "OFF"),
    "resume": ("Resume", "つづける"),
    "save_game": ("Save Game", "セーブ"),
    "got_it": ("Got it!", "わかった！"),
    # name entry
    "name_title": ("Name Your Shop", "お店の名前"),
    "name_prompt": ("Every great candy store needs a great name!", "すてきなお店には、すてきな名前が必要！"),
    "random_name": ("Random Name", "おまかせ"),
    "start": ("Start!", "スタート！"),
    "default_shop": ("Sweet Treats", "スイートキャンディ"),
    # saves
    "load_title": ("Load Game", "ロード"),
    "save_title": ("Save Game", "セーブ"),
    "save_here": ("Save Here", "ここにセーブ"),
    "overwrite": ("Overwrite?", "上書きする？"),
    "load": ("Load", "ロード"),
    "delete": ("Delete", "消す"),
    "really_delete": ("Really delete?", "本当に消す？"),
    "empty": ("Empty", "空き"),
    "saved": ("Saved", "セーブ済み"),
    "empty_slot": ("Empty Slot", "空きスロット"),
    "no_save": ("No game saved here yet.", "まだセーブされていません。"),
    "mid_rush": ("mid-rush", "営業中"),
    "saved_at": ("Saved {when}", "セーブ日時 {when}"),
    "paused_note": ("The store is paused while this menu is open.", "このメニューを開いている間、お店は一時停止しています。"),
    "saved_to": ("Game saved to Slot {n}!", "スロット{n}にセーブしました！"),
    "save_failed": ("Could not save the game.", "セーブできませんでした。"),
    "slot_deleted": ("Slot {n} deleted.", "スロット{n}を消しました。"),
    "slot_empty": ("That save slot is empty.", "そのスロットは空です。"),
    "loaded": ("Loaded {name}, {day}", "{name}（{day}）をロードしました"),
    # settings
    "music": ("Music", "BGM"),
    "sounds": ("Sounds", "効果音"),
    "full_screen": ("Full Screen", "全画面"),
    "exit_full_screen": ("Exit Full Screen", "全画面をやめる"),
    "keys_help": ("Keys: Esc menu · M music · Space speed · F11 full screen",
                  "キー：Esc メニュー・M BGM・スペース スピード・F11 全画面"),
    # how to play
    "h1": ("The Register", "レジ"),
    "b1": ("You start with ¥1,000. Spend it wisely at the Market on lollipops, gummy bears, chocolate and more. "
           "Run out of money AND candy and it is Game Over!",
           "はじめのお金は¥1,000。市場でペロペロキャンディやグミ、チョコなどをかしこく仕入れよう。"
           "お金もおかしも無くなったらゲームオーバー！"),
    "h2": ("The Pantry", "倉庫"),
    "b2": ("Candy you buy waits in your backroom pantry. It holds 50 items to start. When it is full you cannot buy "
           "more until you clear some space.",
           "買ったおかしは裏の倉庫にしまわれます。最初は50個まで。いっぱいになったら、場所をあけるまで買えません。"),
    "h3": ("The Shop Floor", "売り場"),
    "b3": ("Kids only buy candy they can SEE on your display shelves. Each shelf holds 10 of one candy. Cheap "
           "lollipops sell fast; chocolate sells slower but earns far more. You decide!",
           "子どもたちは、たなに見えているおかししか買いません。1つのたなには同じおかしが10個まで。"
           "安いキャンディはすぐ売れる、チョコはゆっくりだけど大もうけ。どうする？"),
    "h4": ("The Rush", "営業タイム"),
    "b4": ("Press Open Store. Kids show what they want in a thought bubble with a patience ring. Have it on a shelf and "
           "they pay you. Wait too long and they leave sad, lowering your star rating.",
           "「お店を開ける」をおそう。子どもたちは、ほしいおかしを吹き出しで教えてくれます。まわりの輪は待てる時間。"
           "たなにあれば買ってくれるけど、待たせすぎると悲しんで帰り、星の評価が下がります。"),
    "h5": ("Restocking", "補充"),
    "b5": ("During the rush, click any shelf to refill it from your pantry, or switch it to a different candy.",
           "営業中はたなをクリックすると倉庫から補充できます。ちがうおかしに入れかえることもできるよ。"),
    "h6": ("Every Morning", "毎朝のできごと"),
    "b6": ("A new event: heatwaves, recess rushes, wholesale sales and more. Read the card and plan ahead!",
           "猛暑、休み時間ラッシュ、大売り出しなど、毎朝ちがうできごとが起こります。カードを読んで作戦を立てよう！"),
    "h7": ("Grow", "お店を大きく"),
    "b7": ("Rent is due each night. Buy upgrades at the Market. Reach {goal} to become a Candy Tycoon. "
           "You can save at any time in one of 3 save slots.",
           "毎晩お店の家賃をはらいます。市場でアップグレードを買おう。{goal}ためるとキャンディ王！"
           "3つのスロットにいつでもセーブできます。"),
    # confirm / menu
    "quit_q": ("Quit?", "やめる？"),
    "quit_msg": ("Any progress since your last save will be lost.", "最後にセーブしてからの進み具合は消えてしまいます。"),
    "quit_to_title": ("Quit to Title", "タイトルへ"),
    "paused": ("Paused", "一時停止"),
    "ready": ("Ready?", "準備はいい？"),
    "ready_msg": ("This game was saved during a rush. Press Resume when you are ready!",
                  "このゲームは営業中にセーブされました。準備ができたら「つづける」をおしてね！"),
    # HUD / bar
    "day_word": ("Day", "日目"),
    "closing": ("Closing", "閉店"),
    "market": ("Market", "市場"),
    "stock_shelves": ("Stock Shelves", "たなにならべる"),
    "open_store": ("Open Store", "お店を開ける"),
    "speed": ("Speed {n}x", "スピード{n}倍"),
    "tip_step1": ("Step 1: Visit the Market and buy candy!", "ステップ1：市場でおかしを買おう！"),
    "tip_step2": ("Step 2: Put candy on your shelves!", "ステップ2：おかしをたなにならべよう！"),
    "tip_room": ("Shelves have room! Fill up, or Open Store.", "たなにすき間あり！補充するか、お店を開けよう。"),
    "tip_ready": ("All set! Press Open Store.", "準備OK！「お店を開ける」をおそう。"),
    "tip_rush": ("Click a shelf to restock it!", "たなをクリックして補充しよう！"),
    "click_restock": ("Click to restock", "クリックで補充"),
    "click_stock": ("Click to stock", "クリックでならべる"),
    "restock_title": ("Restock Shelf {n} from pantry", "たな{n}に倉庫から補充"),
    "restocking": ("Restocking...", "補充中..."),
    "empty_shelf": ("EMPTY!", "からっぽ！"),
    "open_sign": ("OPEN", "営業中"),
    "closed_sign": ("CLOSED", "準備中"),
    "start_market": ("Start by visiting the Market!", "まずは市場に行ってみよう！"),
    "store_open": ("The store is OPEN!", "お店がオープンしました！"),
    "shelf_empty_toast": ("{name} shelf is empty! Click it to restock.", "{name}のたながからっぽ！クリックして補充しよう。"),
    "already_restocking": ("Already restocking this shelf!", "このたなは補充中です！"),
    "wave": ("Here comes a wave of kids!", "子どもたちがどっと来たよ！"),
    "closing_time": ("Closing time! Finishing the last customers...", "閉店の時間！最後のお客さんを見送ろう..."),
    "too_slow": ("Too slow!", "おそいよ〜！"),
    "no_candy": ("No {name}?!", "{name}がない！？"),
    "restocked": ("+{n} {name}", "{name} +{n}"),
    # morning
    "good_morning": ("{day}: Good Morning!", "{day}：おはよう！"),
    "lets_go": ("Let's Go!", "いってみよう！"),
    "melted": ("Oh no! {n} chocolate bars melted!", "たいへん！板チョコが{n}個とけちゃった！"),
    "melted1": ("Oh no! 1 chocolate bar melted!", "たいへん！板チョコが1個とけちゃった！"),
    "new_at_market": ("New at the Market: {names}", "市場に新しいおかし：{names}"),
    "list_sep": (", ", "、"),
    # market
    "market_title": ("Wholesale Market", "おかし市場"),
    "budget": ("Budget:", "予算："),
    "pantry": ("Pantry", "倉庫"),
    "candy_stock": ("Candy Stock", "おかし"),
    "shop_upgrades": ("Shop Upgrades", "アップグレード"),
    "buy_price": ("Buy ¥{n}", "仕入れ ¥{n}"),
    "sell_price": ("Sell ¥{n}", "売値 ¥{n}"),
    "in_pantry": ("In pantry: {n}  ·  Profit ¥{p} each", "倉庫：{n}個  ·  1個のもうけ ¥{p}"),
    "unlocks_on": ("Unlocks on {day}", "{day}に登場"),
    "tag_sale": ("SALE!", "セール！"),
    "tag_hot": ("HOT!", "人気！"),
    "tag_pricey": ("PRICEY", "値上がり"),
    "level": ("Level {n}/{m}", "レベル {n}/{m}"),
    "maxed": ("MAXED", "最大"),
    "stock_next": ("Stock Shelves Next", "次はたなにならべる"),
    "max": ("Max", "最大"),
    # shelves
    "shelves_title": ("Stock Your Shelves", "たなにならべよう"),
    "shelves_help": ("Pick a candy for each shelf, then fill it from your pantry. Only candy on shelves can be sold!",
                     "たなごとにおかしを選んで、倉庫からならべよう。たなにあるおかしだけが売れるよ！"),
    "in_pantry_total": ("in pantry ({n}/{m})", "倉庫（{n}/{m}）"),
    "shelf_n": ("Shelf {n}", "たな{n}"),
    "fill": ("Fill", "満タン"),
    "fill_all": ("Fill All Shelves", "全部満タン"),
    "nothing_to_fill": ("Nothing to fill. Buy matching candy or change shelf types.",
                        "ならべるものがありません。おかしを買うか、たなの種類を変えよう。"),
    # summary
    "day_complete": ("{day} Complete!", "{day} おつかれさま！"),
    "sum_nice": ("Nice work today!", "今日もよくがんばったね！"),
    "sum_perfect": ("Perfect day: every kid left happy!", "パーフェクト！みんな笑顔で帰ったよ！"),
    "sum_empty": ("Lots of kids left empty-handed. Keep shelves stocked!", "何も買えずに帰った子が多かったよ。たなを切らさないで！"),
    "sum_loss": ("You lost money today. Stock more candy to sell more!", "今日は赤字。もっと仕入れて、もっと売ろう！"),
    "happy_customers": ("Happy customers", "笑顔のお客さん"),
    "unhappy_customers": ("Unhappy customers", "悲しいお客さん"),
    "sales": ("Sales", "売り上げ"),
    "rent": ("Shop rent", "家賃"),
    "profit": ("Today's profit", "今日のもうけ"),
    "budget_plain": ("Budget", "予算"),
    "rating": ("Rating", "評価"),
    "sold": ("{n} sold", "{n}個"),
    "best_seller": ("Best seller: {name}", "一番売れたのは：{name}"),
    "nothing_sold": ("Nothing sold today.", "今日は何も売れなかった。"),
    "goal_meter": ("Tycoon goal: {now} / {goal}", "キャンディ王まで：{now} / {goal}"),
    "next_day": ("Next Day", "次の日へ"),
    # game over / win
    "game_over": ("Game Over", "ゲームオーバー"),
    "out_of_cash": ("Out of candy and out of cash!", "おかしもお金も無くなっちゃった！"),
    "closed_after": ("{name} closed its doors after {n} days.", "{name}は{n}日目でお店をしめました。"),
    "closed_after1": ("{name} closed its doors after 1 day.", "{name}は1日目でお店をしめました。"),
    "total_sales": ("Total sales", "売り上げ合計"),
    "happy_kids": ("Happy kids", "笑顔の子ども"),
    "best_day": ("Best day", "最高の日"),
    "final_rating": ("Final rating", "最後の評価"),
    "gameover_tip": ("Tip: always keep enough money to buy stock tomorrow!", "ヒント：明日の仕入れのお金はいつも残しておこう！"),
    "load_a_save": ("Load a Save", "セーブをロード"),
    "main_menu": ("Main Menu", "タイトルへ"),
    "tycoon": ("Candy Tycoon!", "キャンディ王！"),
    "reached": ("You reached {goal}!", "{goal}たまった！"),
    "win_msg": ("{name} is now the most famous candy store in town. Amazing job, Tycoon!",
                "{name}は町で一番有名なおかし屋さんになりました。すごいね、キャンディ王！"),
    "win_stats": ("Days played: {days}  ·  Happy kids served: {kids}", "プレイ日数：{days}  ·  笑顔のお客さん：{kids}人"),
    "keep_playing": ("Keep Playing", "まだまだ続ける"),
    "grand_opening_banner": ("GRAND OPENING", "グランドオープン"),
    "sale_tag_big": ("50% OFF", "半額！"),
    "sale_tag_small": ("LOLLIPOPS", "ペロペロキャンディ"),
    # credits
    "credits_title": ("Credits", "クレジット"),
    "version_line": ("Version v{v}  ·  Released {date}", "バージョン v{v}  ·  公開日 {date}"),
    "created_by": ("Created by", "制作"),
    "made_with": ("Made with", "開発ツール"),
    "claude_code": ("Claude Code (Anthropic)", "Claude Code（Anthropic）"),
    "recommended_ages": ("Recommended for ages 10+", "対象年齢：10才以上"),
    "license_line": ("License: GNU General Public License v3.0 (GPL-3.0)", "ライセンス：GNU一般公衆利用許諾書 v3.0（GPL-3.0）"),
    "license_short": ("This game is free software: you can share and change it under the terms of the GPL v3. "
                      "It comes with ABSOLUTELY NO WARRANTY.",
                      "このゲームはフリーソフトウェアです。GPL v3の条件のもとで、自由に共有・改変できます。"
                      "無保証です。"),
    "font_credit": ("Fonts: Fredoka, M PLUS Rounded 1c (SIL Open Font License)  ·  Music & sound: original, made in code",
                    "フォント：Fredoka、M PLUS Rounded 1c（SIL OFL）  ·  音楽・効果音：オリジナル（プログラムで生成）"),
    "view_license": ("View License", "ライセンスを読む"),
    "license_title": ("GNU GPL v3.0 License", "GNU GPL v3.0 ライセンス"),
    "license_note": ("", "※法的に有効なのは英語の原文です。"),
    # tutorial
    "tutorial": ("Tutorial", "チュートリアル"),
    "next": ("Next", "つぎへ"),
    "tut_start": ("Start a New Game", "ゲームをはじめる"),
    "tut_title_btn": ("Title Screen", "タイトルへ"),
    "tut_page": ("Page {n} of {m}", "{n} / {m} ページ"),
    "tut1_h": ("Welcome, Shopkeeper!", "ようこそ、店長さん！"),
    "tut1_b": ("You own a brand-new candy store with ¥1,000 in the register. Your goal: grow it into the most famous "
               "shop in town by saving up {goal}. This tutorial shows you how to play, and how to win!",
               "あなたは新しいおかし屋さんの店長です。レジには¥1,000。目標は{goal}ためて、町で一番有名なお店に"
               "すること！このチュートリアルで、遊び方と勝つコツを教えるね。"),
    "tut1_t": ("Goal: {goal}", "目標：{goal}"),
    "tut2_h": ("A Day at the Shop", "お店の一日"),
    "tut2_b": ("Every day has four steps. Repeat them, and your shop grows a little more each day!",
               "毎日、4つのステップがあります。くり返すたびに、お店が少しずつ大きくなるよ！"),
    "tut2_s1": ("Morning", "朝"), "tut2_d1": ("Read the event", "できごとを読む"),
    "tut2_s2": ("Prep", "準備"), "tut2_d2": ("Buy and stock", "仕入れてならべる"),
    "tut2_s3": ("Open", "営業"), "tut2_d3": ("Serve the kids", "子どもたちに売る"),
    "tut2_s4": ("Night", "夜"), "tut2_d4": ("Rent and results", "家賃と結果"),
    "tut3_h": ("Buying Candy", "おかしの仕入れ"),
    "tut3_b": ("Open the Market. Each candy shows what it costs to buy and what kids pay for it. The difference is "
               "your profit! Candy goes into your pantry, which holds 50 items to start.",
               "市場を開こう。おかしごとに「仕入れ値」と「売値」が書いてあります。その差があなたのもうけ！"
               "買ったおかしは倉庫へ。最初は50個まで入ります。"),
    "tut3_t1": ("Lollipops: small profit, but kids buy them all the time.", "ペロペロキャンディ：もうけは少しだけど、よく売れる。"),
    "tut3_t2": ("Chocolate: sells slowly, but earns ¥90 each.", "板チョコ：売れるのはゆっくり、でも1個¥90のもうけ。"),
    "tut3_t3": ("Don't spend every yen. Keep some for tomorrow!", "お金を全部使わないで、明日のぶんを残そう！"),
    "tut3_profit": ("Profit ¥{n}", "もうけ ¥{n}"),
    "tut4_h": ("Stocking the Shelves", "たなにならべる"),
    "tut4_b": ("Kids can only buy what they SEE. Each shelf holds one kind of candy, up to 10. Press Stock Shelves, "
               "pick a candy for each shelf, then press Fill.",
               "子どもたちは、見えるおかししか買えません。1つのたなには1種類、10個まで。「たなにならべる」で"
               "おかしを選んで「満タン」をおそう。"),
    "tut4_t1": ("Popular candy can go on more than one shelf.", "人気のおかしは2つのたなにならべてもOK。"),
    "tut4_t2": ("An empty shelf earns nothing!", "からっぽのたなは1円もかせげない！"),
    "tut5_h": ("Serving the Kids", "子どもたちに売る"),
    "tut5_b": ("Press Open Store. Each kid shows the candy they want in a thought bubble. The ring around it is their "
               "patience: green, then yellow, then red.",
               "「お店を開ける」をおそう。子どもたちは、ほしいおかしを吹き出しで教えてくれます。まわりの輪は"
               "待てる時間。緑→黄→赤の順に減っていきます。"),
    "tut5_t1": ("Shelf running low? Click it to restock from your pantry.", "たなが少なくなったら、クリックして倉庫から補充しよう。"),
    "tut5_t2": ("A small extra bubble is a second choice they would also buy.", "小さい吹き出しは「これでもいいよ」のおかし。"),
    "tut5_t3": ("Happy kids raise your stars, and stars bring more customers.", "笑顔のお客さんで星が上がり、お客さんも増える！"),
    "tut5_patient": ("Happy to wait", "まだ待てる"),
    "tut5_hurry": ("Hurry!", "いそいで！"),
    "tut6_h": ("Read the Morning Event", "朝のできごとを読もう"),
    "tut6_b": ("Every morning brings a surprise. Change your plan to match it!",
               "毎朝ちがうできごとが起こります。それに合わせて作戦を変えよう！"),
    "tut6_t1": ("Heatwave: stock lots of Ice Pops. They sell for double!", "夏の猛暑：アイスキャンディをたくさん。2倍で売れる！"),
    "tut6_t2": ("Recess Rush: fill every shelf and restock fast.", "休み時間ラッシュ：全部のたなを満タンに、すばやく補充。"),
    "tut6_t3": ("Wholesaler Sale: buy extra lollipops while they are cheap.", "大売り出し：安いうちにペロペロキャンディを多めに。"),
    "tut6_t4": ("Rainy Day: chocolate sells best.", "雨の日：チョコが一番売れる。"),
    "tut7_h": ("Money, Rent and Stars", "お金・家賃・星"),
    "tut7_b": ("Every night you pay rent, and it goes up a little each day. If you ever have no money AND no candy, "
               "the shop closes: Game Over!",
               "毎晩、家賃をはらいます。家賃は少しずつ上がっていきます。お金もおかしも無くなったら、お店は"
               "おしまい。ゲームオーバー！"),
    "tut7_t1": ("Check the summary each night: which candy sold best?", "毎晩の結果を見て、どのおかしが売れたかチェック。"),
    "tut7_t2": ("More stars mean more customers tomorrow.", "星が多いほど、次の日のお客さんが増える。"),
    "tut7_t3": ("The goal bar shows how close you are to {goal}.", "ゴールのバーで{goal}まであとどれくらいか分かるよ。"),
    "tut7_rent": ("Rent tonight", "今夜の家賃"),
    "tut8_h": ("Tips to Become a Tycoon", "キャンディ王になるコツ"),
    "tut8_t1": ("Mix cheap fast sellers with high-profit candy.", "安くてよく売れるおかしと、もうけの大きいおかしを組み合わせよう。"),
    "tut8_t2": ("Buy Bigger Pantry and Speedy Stocker early.", "「大きな倉庫」と「スピード補充」は早めに買おう。"),
    "tut8_t3": ("Watch the thought bubbles and stock what kids want.", "吹き出しをよく見て、ほしがっているおかしをならべよう。"),
    "tut8_t4": ("Jawbreakers (Day 4) and Cotton Candy (Day 7) earn more.", "にじ色アメ玉（4日目）とわたあめ（7日目）で、もっともうけよう。"),
    "tut8_t5": ("Use 2x speed when everything is under control.", "うまくいっている時は2倍スピードで時短。"),
    "tut8_t6": ("Save before a big day, so you can try again.", "大事な日の前にセーブしておけば、やり直せるよ。"),
    "tut9_h": ("You're Ready!", "準備OK！"),
    "tut9_b": ("That's everything you need. Name your shop and open the doors. Good luck, future Candy Tycoon!",
               "これで準備はばっちり。お店に名前をつけて、ドアを開けよう。がんばれ、未来のキャンディ王！"),
    # model messages
    "msg.locked": ("That candy is still locked.", "そのおかしはまだ買えません。"),
    "msg.pantry_full": ("Your pantry is full! Put candy on shelves to make space.", "倉庫がいっぱい！たなにならべて場所をあけよう。"),
    "msg.space_left": ("Only {n} space left in the pantry!", "倉庫の空きはあと{n}個だけ！"),
    "msg.no_money": ("Not enough money!", "お金が足りません！"),
    "msg.maxed": ("Already maxed out!", "もう最大です！"),
    "msg.upgraded": ("{name} purchased!", "{name}を買いました！"),
    "msg.not_prep": ("The store can only open during prep.", "お店を開けられるのは準備中だけです。"),
    "msg.shelves_empty": ("Your shelves are empty! Stock them first.", "たながからっぽ！先におかしをならべよう。"),
    "msg.open": ("The store is OPEN!", "お店がオープンしました！"),
    "msg.restocking": ("Already restocking this shelf!", "このたなは補充中です！"),
    "msg.none_in_pantry": ("No {name} in your pantry!", "倉庫に{name}がありません！"),
    "msg.shelf_full": ("That shelf is already full!", "そのたなはもう満タンです！"),
}

NAMES = {
    "en": (["Sugar", "Candy", "Gumdrop", "Lolly", "Rainbow", "Sprinkle", "Bubble", "Cocoa", "Jelly", "Fizzy", "Taffy", "Honey"],
           ["Shack", "Palace", "Corner", "Castle", "Emporium", "Hut", "Factory", "Kingdom", "Station", "Cottage", "Market", "Island"]),
    "ja": (["シュガー", "キャンディ", "グミグミ", "ペロペロ", "にじいろ", "マシュマロ", "ふわふわ", "ココア", "ゼリー", "ハニー", "ぱちぱち", "ドロップ"],
           ["ハウス", "パレス", "コーナー", "キャッスル", "ショップ", "ランド", "ファクトリー", "王国", "ステーション", "やさん", "マーケット", "アイランド"]),
}


def random_shop_name(rng):
    a, b = NAMES[LANG["current"]]
    sep = "" if LANG["current"] == "ja" else " "
    return f"{rng.choice(a)}{sep}{rng.choice(b)}"
