#!/usr/bin/env python3
"""一次性執行：取得「永不過期」的 Facebook 粉專存取權杖

Graph Explorer 直接給的是短效使用者權杖，數小時後就失效，
自動發文會在某個週二無聲無息地停掉。真正要的是粉專權杖，
而且要先把使用者權杖換成長效版本，換出來的粉專權杖才不會過期。

流程：短效使用者權杖 → 長效使用者權杖 → 粉專權杖 → 驗證永不過期

執行：python get_facebook_token.py
"""

import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from getpass import getpass
from pathlib import Path

GRAPH = "https://graph.facebook.com/v25.0"
REPO = "Bensonwu0604/hsinchan-website"
PAGE_ID = "100069099361989"          # 欣晨工業粉專，公開資訊
NEEDED = {"pages_manage_posts", "pages_read_engagement"}


def api(path, **params):
    """呼叫 Graph API。

    4xx 時 urlopen 會丟 HTTPError 而不是回傳內容，但 Facebook 真正的
    錯誤說明就在那個回應的 body 裡。必須接住並讀出來，否則只會看到
    一句沒有資訊的 Bad Request。
    """
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read())
        except Exception:                                    # noqa: BLE001
            raise SystemExit(f"\n❌ HTTP {e.code}：{e.reason}") from None
    if "error" in data:
        err = data["error"]
        print(f"\n❌ Graph API 錯誤：{err.get('message')}")
        if err.get("error_user_msg"):
            print(f"   {err['error_user_msg']}")
        print(f"   type={err.get('type')}  code={err.get('code')}"
              f"  subcode={err.get('error_subcode')}")
        print()
        print("   常見原因：")
        print("   · 應用程式密鑰貼錯，或貼成了應用程式編號")
        print("   · 短效權杖是用別的應用程式產生的")
        print("   · 短效權杖已過期（Explorer 產生後數小時內要用掉）")
        print("   · 權杖選成了「粉絲專頁存取權杖」，這裡需要「用戶存取權杖」")
        raise SystemExit(1)
    return data


print("=" * 60)
print("  欣晨工業 Facebook 粉專權杖取得工具")
print("=" * 60)
print()
print("前置步驟（在瀏覽器完成）：")
print("1. 前往 https://developers.facebook.com/tools/explorer")
print("2. 右上角選擇你的應用程式")
print("3. 權限勾選：pages_manage_posts、pages_read_engagement、pages_show_list")
print("4. 按「Generate Access Token」並完成授權")
print("5. 複製產生的權杖（這是短效的，本工具會把它換成永久的）")
print()
print("應用程式編號與密鑰在：應用程式後台 → 設定 → 基本資料")
print()

app_id = input("App ID              : ").strip()
app_secret = getpass("App Secret（不顯示）: ").strip()
short_token = getpass("短效使用者權杖（不顯示）: ").strip()

if not (app_id and app_secret and short_token):
    raise SystemExit("❌ 三項都必須填寫")
if not app_id.isdigit():
    raise SystemExit("❌ App ID 應為純數字，你可能貼成了別的值")

# 密鑰是隱藏輸入，貼錯當下看不出來，先用格式擋掉最常見的幾種錯誤。
# 只回報長度與型態，不顯示內容。
if app_secret == app_id:
    raise SystemExit("❌ 你貼的是應用程式「編號」，不是「密鑰」。\n"
                     "   密鑰在：應用程式後台 → 設定 → 基本資料 → 應用程式密鑰 → 按「顯示」")
if app_secret.startswith("EAA"):
    raise SystemExit("❌ 你貼的是存取權杖，不是應用程式密鑰。\n"
                     "   密鑰在：應用程式後台 → 設定 → 基本資料 → 應用程式密鑰 → 按「顯示」")

# 以下只是觀察，不阻擋。Meta 文件載明憑證長度會隨時間調整，
# 任何寫死的格式規則都可能把正確的值誤判成錯的。
# 真正有權威的是下面第 ⓪ 步——直接問 Facebook。
if not re.fullmatch(r"[0-9a-f]{32}", app_secret):
    print(f"\n（註：密鑰長度 {len(app_secret)}，與常見的 32 字元十六進位格式不同。"
          "這不一定是錯的，接著由 Facebook 驗證。）")
if not short_token.startswith("EAA"):
    print(f"（註：短效權杖通常以 EAA 開頭，你輸入的不是，長度 {len(short_token)}。）")

# ── ⓪ 先單獨驗證編號與密鑰 ──────────────────────────────────────────
# client_credentials 只用到應用程式本身的憑證，與使用者權杖無關。
# 先跑這一步，失敗就確定是密鑰問題，不必再猜權杖。
print("\n⓪ 驗證應用程式編號與密鑰…")
try:
    api("oauth/access_token",
        grant_type="client_credentials",
        client_id=app_id,
        client_secret=app_secret)
except SystemExit:
    print("\n   這一步只用到應用程式編號與密鑰，與短效權杖無關。")
    print("   失敗代表兩者之一不正確，最常見的是密鑰。")
    print()
    print("   正確取得方式：")
    print("   應用程式後台 → 設定 → 基本資料 → 應用程式密鑰 → 按「顯示」")
    print("   （可能需要重新輸入 Facebook 密碼）→ 用複製按鈕複製")
    print()
    print("   密鑰是 32 個小寫十六進位字元，與應用程式編號完全不同。")
    raise
print("   ✅ 應用程式憑證正確")

# ── ① 短效 → 長效使用者權杖（約 60 天）──────────────────────────────
print("① 換取長效使用者權杖…")
long_user = api("oauth/access_token",
                grant_type="fb_exchange_token",
                client_id=app_id,
                client_secret=app_secret,
                fb_exchange_token=short_token)["access_token"]
print("   ✅ 已取得")

# ── ② 長效使用者權杖 → 粉專權杖（這一個才永不過期）──────────────────
print("② 取得粉專權杖…")
page_token = api(PAGE_ID, fields="access_token", access_token=long_user).get("access_token")
if not page_token:
    raise SystemExit(
        "❌ 這個帳號沒有該粉專的管理權限，或權限未勾選 pages_show_list。\n"
        f"   粉專 ID：{PAGE_ID}")
print("   ✅ 已取得")

# ── ③ 驗證：必須永不過期，且具備發文權限 ───────────────────────────
print("③ 驗證權杖…")
info = api("debug_token", input_token=page_token,
           access_token=f"{app_id}|{app_secret}")["data"]

expires = info.get("expires_at", -1)
scopes = set(info.get("scopes", []))
ok = True

if expires == 0:
    print("   ✅ 有效期限：永不過期")
else:
    ok = False
    print(f"   ❌ 有效期限：{expires}（應為 0）")
    print("      代表來源使用者權杖不是長效的，請重新產生短效權杖後再跑一次")

missing = NEEDED - scopes
if missing:
    ok = False
    print(f"   ❌ 缺少權限：{'、'.join(sorted(missing))}")
else:
    print(f"   ✅ 權限齊備：{'、'.join(sorted(NEEDED))}")

if info.get("is_valid"):
    print("   ✅ 權杖有效")
else:
    ok = False
    print("   ❌ 權杖無效")

if not ok:
    raise SystemExit("\n驗證未通過，權杖不會寫入 GitHub。請依上面訊息修正後重跑。")


# ── ④ 寫入 GitHub Secrets ────────────────────────────────────────────
def find_gh():
    found = shutil.which("gh")
    if found:
        return found
    for c in (r"C:\Program Files\GitHub CLI\gh.exe",
              Path.home() / "AppData/Local/Programs/GitHub CLI/gh.exe"):
        if Path(c).exists():
            return str(c)
    return None


gh = find_gh()
if gh:
    print()
    if input(f"寫入 {REPO} 的 FB_ACCESS_TOKEN？[Y/n] ").strip().lower() in ("", "y", "yes"):
        # 用 stdin 傳值，不要用 --body：命令列參數會進 shell 歷史紀錄
        r = subprocess.run([gh, "secret", "set", "FB_ACCESS_TOKEN", "--repo", REPO],
                           input=page_token, text=True, capture_output=True)
        if r.returncode == 0:
            print("   ✅ FB_ACCESS_TOKEN 已寫入")
            print("\n完成。Facebook 上傳鏈路的憑證已齊備。")
            raise SystemExit(0)
        print(f"   ❌ 寫入失敗：{r.stderr.strip()}")

print()
print("手動設定（在你自己的終端機執行，貼上時不會顯示）：")
print(f"   gh secret set FB_ACCESS_TOKEN --repo {REPO}")
print()
print(f"權杖：{page_token[:8]}…（長度 {len(page_token)}）")
print("完整值未顯示，避免留在終端機紀錄中。加 --show 可印出完整值。")

if "--show" in sys.argv:
    print(f"\nFB_ACCESS_TOKEN = {page_token}")
