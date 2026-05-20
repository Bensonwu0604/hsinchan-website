#!/usr/bin/env python3
"""
一次性執行：取得 YouTube OAuth Refresh Token
執行方式：python get_youtube_token.py
輸出的 refresh_token 存入 GitHub Secret: YT_REFRESH_TOKEN
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

print("=" * 55)
print("  欣晨工業 YouTube Refresh Token 取得工具")
print("=" * 55)
print()
print("前置步驟：")
print("1. 到 https://console.cloud.google.com")
print("2. 建立或選擇一個專案")
print("3. 啟用「YouTube Data API v3」")
print("4. 建立 OAuth 2.0 憑證（類型選「桌面應用程式」）")
print("5. 下載 JSON 憑證檔案，儲存為 client_secrets.json")
print()

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

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

print()
print("=" * 55)
print("✅ 授權成功！請將以下資訊存入 GitHub Secrets：")
print("=" * 55)
print()
print(f"Secret 名稱: YT_CLIENT_ID")
print(f"Secret 值  : {client_id}")
print()
print(f"Secret 名稱: YT_CLIENT_SECRET")
print(f"Secret 值  : {client_secret}")
print()
print(f"Secret 名稱: YT_REFRESH_TOKEN")
print(f"Secret 值  : {creds.refresh_token}")
print()
print("GitHub → Settings → Secrets and variables → Actions → New repository secret")
