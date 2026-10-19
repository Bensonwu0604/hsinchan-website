#!/usr/bin/env python3
"""
一次性執行：取得 YouTube OAuth Refresh Token
執行方式：python get_youtube_token.py
輸出的 refresh_token 存入 GitHub Secret: YT_REFRESH_TOKEN
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

REPO = "Bensonwu0604/hsinchan-website"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          # 上傳字幕軌需要 force-ssl，比單純上傳影片的權限更大
          "https://www.googleapis.com/auth/youtube.force-ssl"]

print("=" * 55)
print("  欣晨工業 YouTube Refresh Token 取得工具")
print("=" * 55)
print()
print("前置步驟：")
print("1. 到 https://console.cloud.google.com")
print("2. 建立或選擇一個專案")
print("3. 啟用「YouTube Data API v3」")
print("4. 建立 OAuth 2.0 憑證（類型選「桌面應用程式」）")
print("   ※ 本次授權會同時要求上傳影片與上傳字幕兩項權限")
print("5. 下載 JSON 憑證檔案，存成 scripts/client_secrets.json")
print("   （有這個檔就不必手動貼 client_id／secret，可避免貼錯）")
print()

# 手動複製貼上是 invalid_client 最常見的來源（漏字、多空白、貼錯欄位）。
# Google Console 可直接下載憑證 JSON，有這個檔就優先用它。
secrets_file = Path(__file__).resolve().parent / "client_secrets.json"
if secrets_file.exists():
    client_config = json.loads(secrets_file.read_text(encoding="utf-8"))
    node = client_config.get("installed") or client_config.get("web") or {}
    client_id     = node.get("client_id", "")
    client_secret = node.get("client_secret", "")
    print(f"✅ 已讀取 {secrets_file.name}")
    print(f"   client_id：...{client_id[-32:]}")
    if "web" in client_config:
        print("   ⚠️  這是「網頁應用程式」憑證，本腳本需要「電腦版應用程式」類型")
else:
    print("（找不到 client_secrets.json，改為手動輸入）")
    client_id     = input("請輸入 client_id     : ").strip()
    client_secret = input("請輸入 client_secret : ").strip()
    client_config = {
        "installed": {
            "client_id":     client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
            "token_uri":     "https://oauth2.googleapis.com/token",
        }
    }

if not client_id.endswith(".apps.googleusercontent.com"):
    print()
    print("❌ client_id 格式不對，應以 .apps.googleusercontent.com 結尾。")
    print("   你可能貼到了 client_secret（GOCSPX- 開頭）或別的值。")
    raise SystemExit(1)

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
# prompt="consent" 是必要的：這個應用先前已被授權過，
# Google 預設不會再發新的 refresh token，會印出 None。
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

if not creds.refresh_token:
    print()
    print("❌ 沒有取得 refresh token。")
    print("   請到 https://myaccount.google.com/permissions 移除本應用的授權後重試。")
    raise SystemExit(1)

print()
print("=" * 55)
print("✅ 授權成功")
print("=" * 55)

VALUES = {
    "YT_CLIENT_ID":     client_id,
    "YT_CLIENT_SECRET": client_secret,
    "YT_REFRESH_TOKEN": creds.refresh_token,
}


def find_gh():
    """gh 不一定在 PATH 上（Windows 安裝器預設不加）。"""
    found = shutil.which("gh")
    if found:
        return found
    for candidate in (r"C:\Program Files\GitHub CLI\gh.exe",
                      Path.home() / "AppData/Local/Programs/GitHub CLI/gh.exe"):
        if Path(candidate).exists():
            return str(candidate)
    return None


gh = find_gh()
if gh:
    print()
    print("可以直接寫入 GitHub Secrets，不必複製貼上，")
    print("憑證也不會留在終端機捲軸或剪貼簿裡。")
    if input(f"寫入 {REPO}？[Y/n] ").strip().lower() in ("", "y", "yes"):
        ok = True
        for name, value in VALUES.items():
            # 用 stdin 傳值，不要用 --body：命令列參數會進 shell 歷史紀錄
            r = subprocess.run([gh, "secret", "set", name, "--repo", REPO],
                               input=value, text=True,
                               capture_output=True)
            if r.returncode == 0:
                print(f"  ✅ {name}")
            else:
                ok = False
                print(f"  ❌ {name}：{r.stderr.strip()}")
        if ok:
            print()
            print("三個 secret 都已寫入。接著驗證：")
            print("   python scripts/check_youtube_auth.py")
            raise SystemExit(0)
        print()
        print("有項目失敗，請改用下面的手動方式。")

print()
print("手動設定（在你自己的終端機執行，貼上時不會顯示）：")
for name in VALUES:
    print(f"   gh secret set {name} --repo {REPO}")
print()
print("三個值分別是：")
print(f"   YT_CLIENT_ID     {client_id}")
print(f"   YT_CLIENT_SECRET {client_secret[:7]}…（長度 {len(client_secret)}）")
print(f"   YT_REFRESH_TOKEN {creds.refresh_token[:6]}…（長度 {len(creds.refresh_token)}）")
print()
print("完整值未顯示，避免留在終端機紀錄中。")
print("需要完整值請加 --show 參數重跑，或改用上面的自動寫入。")

if "--show" in sys.argv:
    print()
    for name, value in VALUES.items():
        print(f"{name} = {value}")
