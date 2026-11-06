# Reporting a bug in Candy Store Tycoon

Thank you for helping make Candy Store Tycoon better! A good bug report lets us
find and fix the problem quickly.

**Where to send it:** email **info@shoukugames.org** with the subject
`Candy Store Tycoon bug: <short summary>`, or open an issue on the project's
repository.

## Before you report

1. Check you have the latest version (shown at the bottom of the title screen
   and on the **Credits** screen).
2. Try to make the problem happen a second time and note the exact steps.

## Copy this template

```
Candy Store Tycoon version:  (e.g. v0.2.0, from the Credits screen)
Language setting:            (English / 日本語)
Operating system:            (e.g. Windows 11, Ubuntu 24.04, Debian 12)
How installed:               (.exe / .deb / from source)
Day and event:               (e.g. Day 6, School Recess Rush)
Which screen:                (title / market / shelves / store open / summary / saves ...)

What happened:

What I expected to happen:

Steps to make it happen again:
1.
2.
3.

How often:                   (every time / sometimes / once)
```

## Helpful extras

- **A screenshot or video** of the problem.
- **The save file**, if the bug happens in a saved game. Saves are plain text
  and hold only your shop name and game progress:
  - Windows: `%APPDATA%\CandyStoreTycoon\slot1.json` (or `slot2`, `slot3`)
  - Linux: `~/.local/share/candystoretycoon/slot1.json`
- **Crash log:** if the game closes unexpectedly it writes `crash.log` to the
  same folder. Please attach it.
- **From source:** run `python3 run_game.py --windowed` in a terminal and copy
  any error text it prints.
- **Self-test:** `candystoretycoon --smoke-test result.txt` (or the .exe with
  the same option) plays through every screen and writes the result to
  `result.txt`.

## Known limitations

- On a computer with no working audio device the game runs silently.
- Saves stay on the computer where they were made. To move them, copy the
  `slot*.json` and `slot*.png` files from the folder above.
- The Windows .exe is not code-signed, so Windows SmartScreen may show a
  warning the first time. Choose **More info → Run anyway**.

---

# バグの報告（日本語）

キャンディストア・タイクーンの改善にご協力いただきありがとうございます。

**送り先：** **info@shoukugames.org** へ、件名 `Candy Store Tycoon bug: <かんたんな内容>` でメールしてください。

## 報告の前に

1. 最新版か確認してください（タイトル画面の左下と「クレジット」に表示されています）。
2. もう一度同じことが起きるか試して、手順をメモしてください。

## テンプレート

```
バージョン：            （例：v0.2.0）
OS：                    （例：Windows 11、Ubuntu 24.04）
インストール方法：        （.exe / .deb / ソースから）
言語設定：              （English / 日本語）
何日目・できごと：        （例：6日目、休み時間ラッシュ）
どの画面：              （タイトル / 市場 / たな / 営業中 / 結果 / セーブ など）

何が起きたか：

本当はどうなってほしかったか：

もう一度起こす手順：
1.
2.
3.

起きる頻度：            （毎回 / ときどき / 1回だけ）
```

## あると助かるもの

- 問題の **スクリーンショットや動画**。
- セーブデータで起きる場合は **セーブファイル**（お店の名前と進み具合だけが入っています）：
  - Windows：`%APPDATA%\CandyStoreTycoon\slot1.json`（または slot2、slot3）
  - Linux：`~/.local/share/candystoretycoon/slot1.json`
- ゲームが急に終了した場合は、同じフォルダの **crash.log**。
- **自己診断：** `candystoretycoon --smoke-test result.txt`（.exe でも同じ）を実行すると、
  全画面を自動で確認して結果を `result.txt` に書き出します。
