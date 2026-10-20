#!/usr/bin/env python3
"""查明一個 Facebook 物件到底是粉絲專頁還是個人檔案。

Graph API 只能發文到粉絲專頁。個人檔案沒有對應的發文 API，
不論權限怎麼設都無法自動發文，必須先確認清楚再決定做法。

執行：python check_facebook_target.py
憑證讀 fb_credentials.json，或直接輸入。
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v25.0"
CRED = Path(__file__).resolve().parent / "fb_credentials.json"

TARGETS = {
    "100069099361989": "網站上連結的對象",
    "111671913657635": "目前自動發文的對象",
}


def api(path, token, **params):
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode({**params, "access_token": token})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:                                    # noqa: BLE001
            return {"error": {"message": f"HTTP {e.code}"}}


print("=" * 58)
print("  Facebook 發文目標檢查")
print("=" * 58)

if CRED.exists():
    c = json.loads(CRED.read_text(encoding="utf-8"))
    app_id, app_secret = str(c.get("app_id", "")), str(c.get("app_secret", ""))
    print(f"✅ 已讀取 {CRED.name}")
else:
    print("找不到 fb_credentials.json，請直接輸入：")
    app_id = input("App ID     : ").strip()
    app_secret = input("App Secret : ").strip()

app_token = f"{app_id}|{app_secret}"

for oid, label in TARGETS.items():
    print()
    print(f"── {oid}（{label}）" + "─" * 18)
    # 只有粉絲專頁會有 fan_count / category 這類欄位
    d = api(oid, app_token, fields="id,name,category,fan_count,followers_count,link")
    if "error" in d:
        print(f"   ❌ {d['error'].get('message')}")
        print("   查不到公開資料，通常代表它不是粉絲專頁，")
        print("   或該物件不對這個應用程式公開。")
        continue
    print(f"   名稱     ：{d.get('name')}")
    if d.get("category"):
        print(f"   類別     ：{d['category']}  ← 有類別表示這是粉絲專頁")
    if d.get("fan_count") is not None:
        print(f"   按讚人數 ：{d['fan_count']}")
    if d.get("followers_count") is not None:
        print(f"   追蹤人數 ：{d['followers_count']}")
    if d.get("link"):
        print(f"   連結     ：{d['link']}")
    if not d.get("category") and d.get("fan_count") is None:
        print("   ⚠️  沒有粉絲專頁專屬欄位，很可能是個人檔案")

print()
print("=" * 58)
print("判讀")
print("=" * 58)
print("· 兩個都是粉絲專頁 → 挑追蹤人數多的那個，兩邊設定改成一致")
print("· 網站那個不是粉絲專頁 → 它是個人檔案，無法自動發文。")
print("  選擇：改在粉絲專頁經營，或把個人檔案轉換成粉絲專頁")
print("· 網站那個查不到 → 可能由別的 Facebook 帳號管理，")
print("  需用該帳號重新產生權杖，或把目前帳號加為該粉專管理員")
