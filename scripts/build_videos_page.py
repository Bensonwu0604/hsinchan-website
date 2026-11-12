#!/usr/bin/env python3
"""由 videos.json 產生 videos.html

每週發布後由工作流程呼叫，把新的一集寫進 videos.json 再重建頁面。
頁面是靜態 HTML 而非前端抓取——搜尋引擎與 LLM 對 JS 渲染的內容
索引不可靠，影片清單必須直接存在於原始碼裡。

導覽列與頁尾從 services.html 原樣抽出，避免兩邊各改一次而走樣。

執行：python build_videos_page.py
新增一集：python build_videos_page.py --add <youtube_id> --title "..." --date 2026-11-03 --seconds 888
"""

import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "videos.json"
OUT = ROOT / "videos.html"
TEMPLATE = ROOT / "services.html"
BASE = "https://www.hsinchan.com/"
CHANNEL = "https://www.youtube.com/@欣晨工業有限公司"


def iso_duration(sec):
    m, s = divmod(int(sec), 60)
    return f"PT{m}M{s}S" if s else f"PT{m}M"


def human_duration(sec):
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def load():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"show": "第一性原理拆解智慧製造",
            "show_en": "First Principles of Smart Manufacturing",
            "episodes": []}


def add_episode(db, vid, title, pub, seconds, summary=""):
    if any(e["id"] == vid for e in db["episodes"]):
        print(f"   已存在，略過：{vid}")
        return False
    db["episodes"].append({
        "id": vid, "title": title, "published": pub,
        "seconds": int(seconds), "summary": summary,
    })
    db["episodes"].sort(key=lambda e: e["published"], reverse=True)
    return True


def slice_template():
    """從 services.html 取出 head 之前、header、footer 三段"""
    s = TEMPLATE.read_text(encoding="utf-8")
    header = s[s.index("<header"):s.index("</header>") + len("</header>")]
    footer = s[s.index("<footer"):]
    return header, footer


def build(db):
    header, footer = slice_template()
    eps = db["episodes"]

    # ── 結構化資料：ItemList 包住每一集的 VideoObject ──
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{BASE}videos.html",
                "url": f"{BASE}videos.html",
                "name": f"{db['show']}｜欣晨工業",
                "description": "欣晨工業每週發布的智慧製造教學影片，以第一性原理拆解製造現場的實際問題。",
                "inLanguage": "zh-TW",
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "首頁", "item": BASE},
                    {"@type": "ListItem", "position": 2, "name": "影片",
                     "item": f"{BASE}videos.html"},
                ],
            },
            {
                "@type": "ItemList",
                "name": db["show"],
                "numberOfItems": len(eps),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i,
                        "item": {
                            "@type": "VideoObject",
                            "@id": f"https://www.youtube.com/watch?v={e['id']}",
                            "name": e["title"],
                            "description": e.get("summary") or e["title"],
                            "uploadDate": e["published"],
                            "duration": iso_duration(e["seconds"]),
                            "thumbnailUrl": f"https://i.ytimg.com/vi/{e['id']}/maxresdefault.jpg",
                            "embedUrl": f"https://www.youtube.com/embed/{e['id']}",
                            "contentUrl": f"https://www.youtube.com/watch?v={e['id']}",
                            "publisher": {
                                "@type": "Organization",
                                "name": "欣晨工業有限公司",
                                "url": BASE,
                            },
                            "inLanguage": "zh-TW",
                        },
                    }
                    for i, e in enumerate(eps, 1)
                ],
            },
        ],
    }
    ld = json.dumps(graph, ensure_ascii=False, indent=2)
    ld = "\n".join("  " + l if l.strip() else l for l in ld.split("\n"))

    # ── 影片卡片 ──
    cards = []
    for e in eps:
        t = html.escape(e["title"])
        cards.append(f"""          <article class="video-card">
            <a class="video-card__thumb" href="https://www.youtube.com/watch?v={e['id']}"
               target="_blank" rel="noopener" aria-label="在 YouTube 觀看：{t}">
              <img src="https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg"
                   alt="{t}" loading="lazy" width="480" height="360">
              <span class="video-card__play" aria-hidden="true">▶</span>
              <span class="video-card__dur">{human_duration(e['seconds'])}</span>
            </a>
            <div class="video-card__body">
              <time class="video-card__date" datetime="{e['published']}">{e['published']}</time>
              <h3 class="video-card__title">
                <a href="https://www.youtube.com/watch?v={e['id']}" target="_blank" rel="noopener">{t}</a>
              </h3>
            </div>
          </article>""")

    empty = ("""          <p class="svc-section-lead">第一集即將發布，敬請期待。</p>"""
             if not cards else "\n".join(cards))

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="欣晨工業每週發布的智慧製造教學影片《{db['show']}》。以第一性原理拆解製造現場的實際問題，附繁中、英文、日文字幕。">
  <meta name="author" content="欣晨工業有限公司">
  <link rel="canonical" href="{BASE}videos.html">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{db['show']}｜欣晨工業">
  <meta property="og:description" content="每週一集，以第一性原理拆解智慧製造。繁中／英／日三語字幕。">
  <meta property="og:url" content="{BASE}videos.html">
  <meta property="og:image" content="{BASE}Logo.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{db['show']}｜欣晨工業">
  <meta name="twitter:description" content="每週一集，以第一性原理拆解智慧製造。">

  <title>{db['show']}｜欣晨工業有限公司</title>

  <script type="application/ld+json">
{ld}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <a href="#main-content" class="skip-link">跳到主要內容 / Skip to content</a>
  {header}
  <main id="main-content">

    <section class="page-banner" aria-labelledby="page-title">
      <div class="page-banner__bg" aria-hidden="true"></div>
      <div class="container">
        <div class="page-banner__content" data-reveal>
          <p class="section-eyebrow">FIRST PRINCIPLES OF SMART MFG</p>
          <h1 class="page-banner__title" id="page-title">{db['show']}</h1>
          <p class="page-banner__lead">每週一集，不講名詞、不賣設備。用第一性原理把智慧製造拆回物理與成本的本質，再談該怎麼做、先做哪一步。每集附繁體中文、English、日本語字幕。</p>
          <div class="page-banner__actions">
            <a href="{CHANNEL}" class="btn btn--accent" target="_blank" rel="noopener">訂閱 YouTube 頻道</a>
            <a href="contact.html" class="btn btn--outline">聊聊你的產線</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section prod-detail" id="episodes" aria-labelledby="ep-title">
      <div class="container">
        <header class="section-header" data-reveal>
          <p class="section-eyebrow">EPISODES</p>
          <h2 class="section-title" id="ep-title">全部集數</h2>
        </header>
        <div class="video-grid" data-reveal>
{empty}
        </div>
      </div>
    </section>

    <section class="section prod-detail prod-detail--alt" id="why" aria-labelledby="why-title">
      <div class="container">
        <header class="section-header" data-reveal>
          <p class="section-eyebrow">WHY THIS SHOW</p>
          <h2 class="section-title" id="why-title">我們為什麼做這個節目</h2>
        </header>
        <p class="svc-section-lead" data-reveal>自動化的失敗，多半不是技術不夠好，而是順序做反了——先買設備，才想清楚要解決什麼。這個節目把每個主題拆到物理與成本的本質，再依「質疑、刪除、簡化、加快、自動化」的順序談執行。我們做了三十年精密製造，看過太多從第五步開始的案子。</p>
        <ul class="svc-deliver" role="list" data-reveal>
          <li class="svc-deliver__item"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 10.5 4 4 8-9"/></svg>
            <span><b>可複用的思考工具</b>　每集示範一個能套用到任何產業的提問句，不是單一案例的答案。</span></li>
          <li class="svc-deliver__item"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 10.5 4 4 8-9"/></svg>
            <span><b>明天就能開始的 SOP</b>　每集附執行步驟與預期效益，依五步演算法排序。</span></li>
          <li class="svc-deliver__item"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 10.5 4 4 8-9"/></svg>
            <span><b>三語字幕</b>　繁體中文、English、日本語，方便跨境供應鏈的夥伴一起看。</span></li>
          <li class="svc-deliver__item"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 10.5 4 4 8-9"/></svg>
            <span><b>不推銷</b>　欣晨的內容只出現在結尾，而且只在與主題真的相關時。</span></li>
        </ul>
      </div>
    </section>

    <section class="cta-banner" aria-labelledby="cta-title">
      <div class="container">
        <div class="cta-banner__content" data-reveal>
          <p class="section-eyebrow" style="color:var(--c-accent-light)">GET STARTED</p>
          <h2 class="cta-banner__title" id="cta-title">影片裡的作法，想用在您的產線上？</h2>
          <p class="cta-banner__desc">歡迎提供您的工件、節拍與現場條件，欣晨工業技術團隊將協助評估可行方案。</p>
          <a href="contact.html" class="btn btn--accent btn--xl">聯絡我們</a>
        </div>
      </div>
    </section>

  </main>
  {footer}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", metavar="YOUTUBE_ID")
    ap.add_argument("--title")
    ap.add_argument("--date", default=str(date.today()))
    ap.add_argument("--seconds", type=int, default=0)
    ap.add_argument("--summary", default="")
    args = ap.parse_args()

    db = load()
    if args.add:
        if not args.title:
            raise SystemExit("--add 需要同時給 --title")
        if add_episode(db, args.add, args.title, args.date, args.seconds, args.summary):
            DATA.write_bytes(json.dumps(db, ensure_ascii=False, indent=2)
                             .replace("\r\n", "\n").encode("utf-8"))
            print(f"   已加入：{args.title}")

    DATA.write_bytes(json.dumps(db, ensure_ascii=False, indent=2)
                     .replace("\r\n", "\n").encode("utf-8"))
    OUT.write_bytes(build(db).replace("\r\n", "\n").encode("utf-8"))
    print(f"videos.html 已重建（{len(db['episodes'])} 集）")


if __name__ == "__main__":
    main()
