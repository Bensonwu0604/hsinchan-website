#!/usr/bin/env python3
"""把 main.js 裡尚未翻譯的日文／英文項目補齊。

判定方式：某個鍵的 ja/en 值與 zh 值完全相同，且 zh 值含中文字，
就視為未翻譯。純英文或純數字的值（ESG、SCROLL、1200°C）三語本
來就相同，不在此列。

寫回時用掃描器記下每個字面量的實際位置再就地替換，不重排整個
檔案，註解與既有排版都保留。

執行：ANTHROPIC_API_KEY=... python translate_i18n.py [--dry-run]
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
MAIN_JS = ROOT / "main.js"
MODEL = os.environ.get("TRANSLATE_MODEL", "claude-haiku-5-5")
BATCH = int(os.environ.get("TRANSLATE_BATCH", "30"))
DRY_RUN = "--dry-run" in sys.argv

CJK = re.compile(r"[\u4e00-\u9fff]")
IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")

LANG_NAME = {"ja": "日文（Japanese）", "en": "英文（English）"}


# ── main.js 掃描 ──────────────────────────────────────────────────────────
def find_block(src, lang):
    """回傳某語言區塊的 (起, 迄)，迄為對應右大括號的位置。"""
    m = re.search(rf"\n  {lang}\s*:\s*\{{", src)
    if not m:
        raise SystemExit(f"找不到語言區塊：{lang}")
    depth = 0
    for i in range(m.end() - 1, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return m.end(), i
    raise SystemExit(f"語言區塊未正確結束：{lang}")


def scan_entries(src, start, end):
    """逐字掃出 key -> (值, 字面量起點, 字面量終點)。

    不用正規表示式配對字串：main.js 同時存在單引號與雙引號的寫法，
    值裡面也可能含有另一種引號，正規表示式很容易抓錯邊界。
    """
    out = {}
    i = start
    while i < end:
        c = src[i]
        # 註解
        if c == "/" and i + 1 < end and src[i + 1] == "/":
            i = src.find("\n", i)
            if i == -1:
                break
            continue
        if not (c.isalpha() or c in "_$"):
            i += 1
            continue
        m = IDENT.match(src, i)
        key = m.group(0)
        j = m.end()
        while j < end and src[j] in " \t":
            j += 1
        if j >= end or src[j] != ":":
            i = m.end()
            continue
        j += 1
        while j < end and src[j] in " \t\n":
            j += 1
        if j >= end or src[j] not in "\"'`":
            i = m.end()          # 值不是字串（巢狀物件、陣列），略過
            continue
        quote = src[j]
        lit_start = j
        j += 1
        buf = []
        while j < end:
            ch = src[j]
            if ch == "\\":
                buf.append(src[j:j + 2])
                j += 2
                continue
            if ch == quote:
                break
            buf.append(ch)
            j += 1
        raw = "".join(buf)
        value = raw.encode().decode("unicode_escape") if "\\" in raw else raw
        out[key] = (value, lit_start, j + 1)
        i = j + 1
    return out


def js_string(s):
    """輸出單引號字面量，與 main.js 既有寫法一致。"""
    body = s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    return f"'{body}'"


# ── 翻譯 ──────────────────────────────────────────────────────────────────
def build_glossary(zh, ja, en, lang):
    """從既有譯文抽出技術詞彙對照，讓新譯文用詞一致。"""
    target = ja if lang == "ja" else en
    terms = [
        "nav_products", "nav_services", "pp_p2_title", "pp_p4_title",
        "pp_p5_title", "pp_p6_title", "srv_d2_title", "srv_d3_title",
        "srv_d4_title", "srv_d5_title", "srv_d6_title",
    ]
    pairs = [(zh[k], target[k]) for k in terms
             if k in zh and k in target and target[k] != zh[k]]
    return "\n".join(f"  {a} → {b}" for a, b in pairs)


PROMPT = """你是欣晨工業（台灣桃園的精密自動化設備製造商）官網的專業譯者。
把下列繁體中文的網站文案翻成{lang}。

這是 B2B 工業網站，讀者是製造業的採購與工程人員。

必須遵守：
1. 只輸出 JSON 物件，鍵沿用輸入的鍵，值為譯文。不要任何額外說明。
2. 數字、單位（mm、°C、nm、h）、品牌與產品名（FANUC、ABB、KUKA、
   Yaskawa、Solid Edge、Modbus TCP、OPC UA、PLC、HMI、AOI、OEE、
   FAT、SAT、STEP、ISO 10218）一律原樣保留，不要翻譯或改寫。
3. 箭頭「→」、全形括號內的原文標註要保留。
4. 長度盡量與原文相當，這些字串會放進固定版面。
5. 語氣是專業、具體、不誇大的工業文案，不要行銷腔。
{tone}

既有譯文的用詞對照，請沿用：
{glossary}

待翻譯：
{payload}"""

TONE = {
    "ja": "6. 日文用です・ます體，技術名詞用通行的片假名或漢語詞。",
    "en": "6. English: professional B2B prose, sentence case, no title case headings.",
}


def translate(client, lang, items, zh, ja, en):
    payload = json.dumps(items, ensure_ascii=False, indent=1)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": PROMPT.format(
            lang=LANG_NAME[lang], tone=TONE[lang],
            glossary=build_glossary(zh, ja, en, lang), payload=payload)}],
    )
    text = "".join(b.text for b in msg.content
                   if getattr(b, "type", None) == "text").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n|\n```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a == -1 or b == -1:
            raise
        return json.loads(text[a:b + 1])


def main():
    src = MAIN_JS.read_text(encoding="utf-8")
    blocks = {l: find_block(src, l) for l in ("zh", "ja", "en")}
    entries = {l: scan_entries(src, *blocks[l]) for l in blocks}
    zh = {k: v[0] for k, v in entries["zh"].items()}
    ja = {k: v[0] for k, v in entries["ja"].items()}
    en = {k: v[0] for k, v in entries["en"].items()}

    print(f"解析完成：zh {len(zh)}　ja {len(ja)}　en {len(en)} 鍵")

    todo = {}
    for lang, cur in (("ja", ja), ("en", en)):
        todo[lang] = [k for k, v in zh.items()
                      if CJK.search(v) and cur.get(k, v) == v]
        print(f"  {lang} 待譯：{len(todo[lang])}")

    if not any(todo.values()):
        print("沒有待翻譯項目")
        return

    if DRY_RUN:
        for lang, keys in todo.items():
            print(f"\n[{lang}] 前五筆：")
            for k in keys[:5]:
                print(f"   {k}: {zh[k][:50]}")
        return

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    results = {"ja": {}, "en": {}}

    for lang, keys in todo.items():
        for i in range(0, len(keys), BATCH):
            chunk = keys[i:i + BATCH]
            items = {k: zh[k] for k in chunk}
            n = i // BATCH + 1
            total = (len(keys) + BATCH - 1) // BATCH
            for attempt in range(3):
                try:
                    got = translate(client, lang, items, zh, ja, en)
                    missing = [k for k in chunk if not got.get(k)]
                    if missing and attempt < 2:
                        raise ValueError(f"缺 {len(missing)} 鍵")
                    results[lang].update(
                        {k: v for k, v in got.items() if k in items and v})
                    print(f"  [{lang}] 批次 {n}/{total}　{len(chunk)} 鍵 ✅")
                    break
                except Exception as e:                   # noqa: BLE001
                    if attempt == 2:
                        print(f"  [{lang}] 批次 {n}/{total} 失敗，略過：{e}")
                    else:
                        time.sleep(2 * (attempt + 1))

    # ── 就地寫回 ──────────────────────────────────────────────────────
    edits = []
    for lang in ("ja", "en"):
        ent = entries[lang]
        for k, v in results[lang].items():
            if k not in ent:
                continue                      # 該語言區塊沒有這個鍵
            _, a, b = ent[k]
            edits.append((a, b, js_string(v)))

    # 由後往前取代，前面的位移才不會被影響
    edits.sort(key=lambda e: -e[0])
    for a, b, text in edits:
        src = src[:a] + text + src[b:]

    MAIN_JS.write_bytes(src.replace("\r\n", "\n").encode("utf-8"))
    print(f"\n已寫回 {len(edits)} 筆（ja {len(results['ja'])}、en {len(results['en'])}）")

    # 寫回後重新解析一次，確認檔案結構沒被破壞
    check = MAIN_JS.read_text(encoding="utf-8")
    for lang in ("zh", "ja", "en"):
        e = scan_entries(check, *find_block(check, lang))
        print(f"  驗證 {lang}：{len(e)} 鍵")


if __name__ == "__main__":
    main()
