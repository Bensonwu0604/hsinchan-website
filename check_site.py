#!/usr/bin/env python3
"""網站整體檢查

查幾類實際會出問題的東西：
  1. 內部連結指向不存在的檔案
  2. data-i18n 的鍵在 main.js 裡缺翻譯（或缺某個語言）
  3. 同一頁出現重複的 id
  4. 圖片缺 alt、外連缺 rel="noopener"
  5. 引用的圖片／CSS／JS 檔案不存在
  6. HTML 區塊標籤未配對
  7. CSS 大括號未配對、用到未定義的變數
"""

import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
PAGES = sorted(ROOT.glob("*.html"))
issues = defaultdict(list)


def add(cat, msg):
    issues[cat].append(msg)


# ── main.js 的翻譯鍵 ────────────────────────────────────────────────
js = (ROOT / "main.js").read_text(encoding="utf-8")
lang_blocks = re.findall(r"(zh|ja|en)\s*:\s*\{", js)
keys_per_lang = {}
for lang in ("zh", "ja", "en"):
    m = re.search(rf"\b{lang}\s*:\s*\{{", js)
    if not m:
        continue
    depth, i = 0, m.end() - 1
    for j in range(m.end() - 1, len(js)):
        if js[j] == "{":
            depth += 1
        elif js[j] == "}":
            depth -= 1
            if depth == 0:
                i = j
                break
    # 鍵值可能多個寫在同一行，前面也可能隔著註解行，
    # 所以先把註解剝掉，再抓所有 key: 值 的組合
    body = re.sub(r"//[^\n]*", "", js[m.end():i])
    keys_per_lang[lang] = set(re.findall(r"(?:^|[{,\s])([a-zA-Z0-9_]+)\s*:\s*['\"`\[{]", body))

all_keys = set().union(*keys_per_lang.values()) if keys_per_lang else set()

# ── 逐頁檢查 ────────────────────────────────────────────────────────
used_keys = set()
for p in PAGES:
    s = p.read_text(encoding="utf-8")
    name = p.name

    # 內部連結
    for href in re.findall(r'href="([^"#?:]+\.html)[^"]*"', s):
        if not (ROOT / href).exists():
            add("連結失效", f"{name} → {href}")

    # 引用的靜態檔案
    for src in re.findall(r'(?:src|href)="((?!https?:|mailto:|tel:|#)[^"]+\.(?:jpg|jpeg|png|webp|svg|css|js|json|ico))"', s):
        if not (ROOT / src).exists():
            add("檔案遺失", f"{name} → {src}")

    # i18n 鍵
    for k in re.findall(r'data-i18n="([a-zA-Z0-9_]+)"', s):
        used_keys.add(k)
        if k not in all_keys:
            add("翻譯鍵缺漏", f"{name} → {k}（main.js 完全沒有）")
        else:
            missing = [l for l, ks in keys_per_lang.items() if k not in ks]
            if missing:
                add("翻譯語言缺漏", f"{name} → {k} 缺 {'/'.join(missing)}")

    # 重複 id
    ids = re.findall(r'\sid="([^"]+)"', s)
    for dup in {i for i in ids if ids.count(i) > 1}:
        add("重複 id", f"{name} → id=\"{dup}\" 出現 {ids.count(dup)} 次")

    # 圖片 alt
    for tag in re.findall(r"<img\b[^>]*>", s):
        if "alt=" not in tag:
            add("無障礙", f"{name} → <img> 缺 alt：{tag[:70]}")

    # 外部連結安全性
    for tag in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', s):
        if "noopener" not in tag:
            add("外連安全", f"{name} → target=_blank 缺 rel=noopener：{tag[:70]}")

    # 區塊標籤配對
    for tag in ("div", "section", "nav", "footer", "header", "main", "ul", "li", "article"):
        o = len(re.findall(rf"<{tag}\b", s))
        c = len(re.findall(rf"</{tag}>", s))
        if o != c:
            add("標籤未配對", f"{name} → <{tag}> 開 {o} / 關 {c}")

    # 常見殘留
    for marker in ("<<<<<<<", ">>>>>>>", "TODO", "FIXME", "lorem ipsum"):
        if marker in s:
            add("殘留標記", f"{name} → 含 {marker}")

# 未使用的翻譯鍵（只列數量，太多不值得逐條看）
unused = all_keys - used_keys
nav_ok = {k for k in unused if k.startswith(("hero_", "idx_", "pd_", "pp_", "srv_", "esg_", "ab_", "cr_", "ct_", "tc_"))}
orphan = unused - nav_ok

# ── CSS ────────────────────────────────────────────────────────────
css = (ROOT / "style.css").read_text(encoding="utf-8")
if css.count("{") != css.count("}"):
    add("CSS 結構", f"大括號不配對：{css.count('{')} 開 / {css.count('}')} 關")

defined_vars = set(re.findall(r"(--[a-zA-Z0-9-]+)\s*:", css))
for v in set(re.findall(r"var\((--[a-zA-Z0-9-]+)", css)):
    if v not in defined_vars:
        add("CSS 變數", f"{v} 被使用但未定義")

# 檔案換行格式
for f in list(PAGES) + [ROOT / "style.css", ROOT / "main.js"]:
    if b"\r\n" in f.read_bytes():
        add("換行格式", f"{f.name} 使用 CRLF（其餘檔案為 LF）")

# ── 輸出 ────────────────────────────────────────────────────────────
print("=" * 62)
print(f"  網站檢查　{len(PAGES)} 個頁面")
print("=" * 62)

if not issues:
    print("\n✅ 未發現問題\n")
else:
    for cat in sorted(issues):
        print(f"\n【{cat}】{len(issues[cat])} 項")
        for m in issues[cat][:12]:
            print(f"   · {m}")
        if len(issues[cat]) > 12:
            print(f"   … 另有 {len(issues[cat]) - 12} 項")

print("\n" + "-" * 62)
print(f"翻譯鍵：定義 {len(all_keys)}　使用 {len(used_keys)}　未使用 {len(unused)}")
for lang, ks in sorted(keys_per_lang.items()):
    print(f"   {lang}: {len(ks)} 鍵")
print(f"問題總數：{sum(len(v) for v in issues.values())}")
