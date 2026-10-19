#!/usr/bin/env python3
"""
驗證 YouTube 授權是否可用（唯讀，不會上傳任何東西）

檢查三件事：
  1. refresh token 能不能換到 access token
  2. 授權範圍有沒有包含上傳字幕所需的 force-ssl
  3. 能不能真的呼叫到 YouTube API

執行：python check_youtube_auth.py
"""

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build

UPLOAD = "https://www.googleapis.com/auth/youtube.upload"
FORCE_SSL = "https://www.googleapis.com/auth/youtube.force-ssl"


def ask(name):
    v = os.environ.get(name)
    if v:
        print(f"{name:18} 取自環境變數")
        return v.strip()
    return input(f"請輸入 {name}：").strip()


print("=" * 58)
print("  YouTube 授權驗證（唯讀，不會上傳任何東西）")
print("=" * 58)

client_id     = ask("YT_CLIENT_ID")
client_secret = ask("YT_CLIENT_SECRET")
refresh_token = ask("YT_REFRESH_TOKEN")

creds = Credentials(
    token=None,
    refresh_token=refresh_token,
    client_id=client_id,
    client_secret=client_secret,
    token_uri="https://oauth2.googleapis.com/token",
    scopes=[UPLOAD, FORCE_SSL],
)

print("\n[1/3] 用 refresh token 換 access token…")
try:
    creds.refresh(GoogleRequest())
    print("      ✅ 成功")
except Exception as e:                              # noqa: BLE001
    print(f"      ❌ 失敗：{e}")
    print("      → refresh token 無效或已被撤銷，請重新執行 get_youtube_token.py")
    raise SystemExit(1)

print("\n[2/3] 檢查授權範圍…")
granted = set(creds.granted_scopes or [])
for scope, label in ((UPLOAD, "上傳影片"), (FORCE_SSL, "上傳字幕 (force-ssl)")):
    print(f"      {'✅' if scope in granted else '❌'} {label}")
if FORCE_SSL not in granted:
    print("      → 缺少 force-ssl，字幕會上傳失敗。")
    print("        請重新執行 get_youtube_token.py 重新授權。")

print("\n[3/3] 實際呼叫 YouTube API…")
try:
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    items = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    if items:
        print(f"      ✅ 已連上頻道：{items[0]['snippet']['title']}")
    else:
        print("      ⚠️  連得上 API，但這個帳號沒有 YouTube 頻道")
except Exception as e:                              # noqa: BLE001
    print(f"      ❌ 失敗：{str(e)[:200]}")
    print("      → 確認專案已啟用 YouTube Data API v3")
    raise SystemExit(1)

print("\n" + "=" * 58)
if FORCE_SSL in granted:
    print("✅ 全部通過，影片與字幕都能上傳")
else:
    print("⚠️  影片可以上傳，但字幕不行（缺 force-ssl）")
print("=" * 58)
