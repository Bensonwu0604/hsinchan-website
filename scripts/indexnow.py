#!/usr/bin/env python3
"""通知 IndexNow：這些網址剛新增或更新了

IndexNow 是 Bing 主導的即時索引協定（Yandex、Naver、Seznam 等共用），
不必等爬蟲巡到，提交後通常數分鐘內就會被抓取。Bing 的索引同時供應
Copilot、ChatGPT 搜尋與 DuckDuckGo，所以這也直接影響 LLM 找不找得到。

金鑰檔 <key>.txt 放在網站根目錄，用來證明我們擁有這個網域。
金鑰本身依協定設計就是公開的，不是機密。

用法：
  python indexnow.py --all                    提交 sitemap 中全部網址
  python indexnow.py --since HEAD~1 --wait    提交上一次 commit 改到的頁面
  python indexnow.py --files a.html b.html    提交指定檔案
  python indexnow.py https://www.hsinchan.com/xxx.html
--wait 會先確認網址已部署（回 200）再提交，避免通知 Bing 去抓還沒上線的頁面。
"""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "www.hsinchan.com"
BASE = f"https://{HOST}/"
KEY = "7e19d612360c86de1ba45b3cd77a568c"
ENDPOINT = "https://api.indexnow.org/indexnow"


def file_to_url(name):
    name = Path(name).name
    if name == "index.html":
        return BASE
    if name.endswith(".html"):
        return BASE + name
    if name in ("sitemap.xml", "llms.txt", "llms-full.txt", "robots.txt"):
        return BASE + name
    return None


def from_sitemap():
    s = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", s)


def changed_since(ref):
    out = subprocess.run(["git", "diff", "--name-only", ref, "HEAD"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.split() if "/" not in f]   # 只取根目錄的網站檔


def wait_live(url, timeout=240):
    """等 Vercel 部署完成，網址回 200 才算上線"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    return True
        except urllib.error.HTTPError:
            pass
        except Exception:                                    # noqa: BLE001
            pass
        time.sleep(10)
    return False


def submit(urls):
    body = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{BASE}{KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]


MEANING = {
    200: "已受理",
    202: "已收到，金鑰驗證中（第一次提交常見，屬正常）",
    400: "格式錯誤",
    403: "金鑰無效或金鑰檔讀不到",
    422: "網址不屬於這個網域，或金鑰不符",
    429: "提交太頻繁，稍後再試",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--since", metavar="REF")
    ap.add_argument("--files", nargs="+")
    ap.add_argument("--wait", action="store_true")
    a = ap.parse_args()

    urls = list(a.urls)
    if a.all:
        urls += from_sitemap()
    if a.since:
        urls += [u for u in map(file_to_url, changed_since(a.since)) if u]
    if a.files:
        urls += [u for u in map(file_to_url, a.files) if u]
    urls = list(dict.fromkeys(urls))                       # 去重並保留順序

    if not urls:
        print("沒有需要提交的網址")
        return

    print(f"準備提交 {len(urls)} 個網址到 IndexNow")
    if a.wait:
        live = []
        for u in urls:
            if wait_live(u):
                live.append(u)
            else:
                print(f"   ⚠️  尚未上線，略過：{u}")
        urls = live
        if not urls:
            print("沒有已上線的網址可提交")
            sys.exit(1)

    code, detail = submit(urls)
    print(f"IndexNow 回應 HTTP {code}：{MEANING.get(code, '未預期的回應')}")
    if detail:
        print(f"   {detail}")
    for u in urls[:30]:
        print(f"   · {u}")
    if len(urls) > 30:
        print(f"   … 另有 {len(urls) - 30} 個")
    if code not in (200, 202):
        sys.exit(1)


if __name__ == "__main__":
    main()
