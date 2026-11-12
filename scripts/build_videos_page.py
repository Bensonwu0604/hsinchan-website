#!/usr/bin/env python3
"""由 videos.json 產生官網的影片相關頁面

產出：
  videos.html          全部集數列表
  video-<id>.html      每一集的文章頁（重點、SOP、效益、章節、嵌入影片）
  index.html           首頁「最新一集」區塊（只改標記之間的內容）
  sitemap.xml          補上各集文章頁

為什麼每集要有文章頁：影片對搜尋引擎只露出標題與說明，每集腳本裡
的重點、SOP 與效益才是能被搜尋、被 LLM 引用的實質內容。一集影片
因此變成一篇可索引的文章，並把觀眾留在官網而不是送去 YouTube。

所有頁面都是靜態 HTML——搜尋引擎對 JS 渲染內容的索引不可靠。
導覽列與頁尾從 services.html 原樣取用，再把「影片」設為目前頁。

用法：
  python build_videos_page.py                       只重建頁面
  python build_videos_page.py --from-json FILE      由工作流程寫出的單集資料新增一集
  python build_videos_page.py --add ID --title ...  手動新增
"""

import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "videos.json"
TEMPLATE = ROOT / "services.html"
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://www.hsinchan.com/"
CHANNEL = "https://www.youtube.com/@欣晨工業有限公司"
MARK_START = "<!-- LATEST-EPISODE:START -->"
MARK_END = "<!-- LATEST-EPISODE:END -->"

CHECK_SVG = ('<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" '
             'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" '
             'aria-hidden="true"><path d="m4 10.5 4 4 8-9"/></svg>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:'
         'wght@300;400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&'
         'family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">\n'
         '  <link rel="stylesheet" href="style.css">')

e = html.escape


# ── 資料 ──────────────────────────────────────────────────────────────────
def load():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"show": "第一性原理拆解智慧製造",
            "show_en": "First Principles of Smart Manufacturing",
            "episodes": []}


def save(db):
    DATA.write_bytes(json.dumps(db, ensure_ascii=False, indent=2)
                     .replace("\r\n", "\n").encode("utf-8"))


def add_episode(db, ep):
    if any(x["id"] == ep["id"] for x in db["episodes"]):
        print(f"   已存在，略過：{ep['id']}")
        return False
    db["episodes"].append(ep)
    db["episodes"].sort(key=lambda x: x["published"], reverse=True)
    return True


def number_episodes(db):
    """集數依發布先後編號，最舊的是 EP.1"""
    for n, ep in enumerate(sorted(db["episodes"], key=lambda x: x["published"]), 1):
        ep["no"] = n


# ── 共用片段 ──────────────────────────────────────────────────────────────
def iso_duration(sec):
    m, s = divmod(int(sec), 60)
    return f"PT{m}M{s}S" if s else f"PT{m}M"


def mmss(sec):
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def page_url(ep):
    return f"video-{ep['id']}.html"


def chrome():
    """導覽列與頁尾，並把「影片」設成目前頁"""
    s = TEMPLATE.read_text(encoding="utf-8")
    header = s[s.index("<header"):s.index("</header>") + len("</header>")]
    footer = s[s.index("<footer"):]
    header = re.sub(r'class="nav__link nav__link--active"', 'class="nav__link"', header)
    header = header.replace(
        '<a href="videos.html" class="nav__link"',
        '<a href="videos.html" class="nav__link nav__link--active"')
    return header, footer


def ld_block(obj):
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    return "\n".join("  " + l if l.strip() else l for l in s.split("\n"))


def video_object(ep):
    vo = {
        "@type": "VideoObject",
        "@id": f"https://www.youtube.com/watch?v={ep['id']}",
        "name": ep["title"],
        "description": ep.get("intro") or ep.get("summary") or ep["title"],
        "uploadDate": ep["published"],
        "duration": iso_duration(ep["seconds"]),
        "thumbnailUrl": f"https://i.ytimg.com/vi/{ep['id']}/maxresdefault.jpg",
        "embedUrl": f"https://www.youtube.com/embed/{ep['id']}",
        "contentUrl": f"https://www.youtube.com/watch?v={ep['id']}",
        "inLanguage": "zh-TW",
        "publisher": {"@type": "Organization", "name": "欣晨工業有限公司", "url": BASE},
    }
    # 章節標成 Clip，Google 可在搜尋結果顯示「重要時刻」
    ch = ep.get("chapters") or []
    if len(ch) >= 2:
        vo["hasPart"] = [
            {"@type": "Clip", "name": label, "startOffset": t,
             "endOffset": ch[i + 1][1] if i + 1 < len(ch) else int(ep["seconds"]),
             "url": f"https://www.youtube.com/watch?v={ep['id']}&t={t}s"}
            for i, (label, t) in enumerate(ch)
        ]
    return vo


def head(title, desc, canonical, ld, og_image=f"{BASE}Logo.jpg"):
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{e(desc)}">
  <meta name="author" content="欣晨工業有限公司">
  <link rel="canonical" href="{canonical}">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">

  <title>{e(title)}</title>

  <script type="application/ld+json">
{ld}
  </script>
  {FONTS}
</head>"""


def card(ep):
    t = e(ep["title"])
    return f"""          <article class="video-card">
            <a class="video-card__thumb" href="{page_url(ep)}" aria-label="{t}">
              <img src="https://i.ytimg.com/vi/{ep['id']}/hqdefault.jpg"
                   alt="" loading="lazy" width="480" height="360">
              <span class="video-card__play" aria-hidden="true">▶</span>
              <span class="video-card__dur">{mmss(ep['seconds'])}</span>
            </a>
            <div class="video-card__body">
              <span class="video-card__date">EP.{ep['no']}　<time datetime="{ep['published']}">{ep['published']}</time></span>
              <h3 class="video-card__title"><a href="{page_url(ep)}">{t}</a></h3>
            </div>
          </article>"""


# ── 列表頁 ────────────────────────────────────────────────────────────────
def build_index(db, header, footer):
    eps = db["episodes"]
    ld = ld_block({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": f"{BASE}videos.html", "url": f"{BASE}videos.html",
         "name": f"{db['show']}｜欣晨工業",
         "description": "欣晨工業每週發布的智慧製造教學影片，以第一性原理拆解製造現場的實際問題。",
         "inLanguage": "zh-TW"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "影片", "item": f"{BASE}videos.html"}]},
        {"@type": "ItemList", "name": db["show"], "numberOfItems": len(eps),
         "itemListElement": [{"@type": "ListItem", "position": i,
                              "url": f"{BASE}{page_url(ep)}",
                              "item": video_object(ep)}
                             for i, ep in enumerate(eps, 1)]},
    ]})
    cards = "\n".join(card(ep) for ep in eps) or \
        '          <p class="svc-section-lead">第一集即將發布，敬請期待。</p>'

    return head(f"{db['show']}｜欣晨工業有限公司",
                f"欣晨工業每週發布的智慧製造教學影片《{db['show']}》。以第一性原理拆解製造現場的實際問題，附繁中、英文、日文字幕。",
                f"{BASE}videos.html", ld) + f"""
<body>
  <a href="#main-content" class="skip-link">跳到主要內容 / Skip to content</a>
  {header}
  <main id="main-content">

    <section class="page-banner" aria-labelledby="page-title">
      <div class="page-banner__bg" aria-hidden="true"></div>
      <div class="container">
        <div class="page-banner__content" data-reveal>
          <p class="section-eyebrow">FIRST PRINCIPLES OF SMART MFG</p>
          <h1 class="page-banner__title" id="page-title">{e(db['show'])}</h1>
          <p class="page-banner__lead">每週一集，不講名詞、不賣設備。用第一性原理把智慧製造拆回物理與成本的本質，再依「質疑、刪除、簡化、加快、自動化」的順序談該怎麼做。每集附繁體中文、English、日本語字幕。</p>
          <div class="page-banner__actions">
            <a href="{CHANNEL}" class="btn btn--accent" target="_blank" rel="noopener" data-i18n="ep_subscribe">訂閱 YouTube 頻道</a>
            <a href="contact.html" class="btn btn--outline" data-i18n="nav_contact">聯絡我們</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section prod-detail" id="episodes" aria-labelledby="ep-title">
      <div class="container">
        <header class="section-header" data-reveal>
          <p class="section-eyebrow">EPISODES</p>
          <h2 class="section-title" id="ep-title" data-i18n="ep_all">全部集數</h2>
        </header>
        <div class="video-grid" data-reveal>
{cards}
        </div>
      </div>
    </section>

    <section class="section prod-detail prod-detail--alt" id="why" aria-labelledby="why-title">
      <div class="container">
        <header class="section-header" data-reveal>
          <p class="section-eyebrow">WHY THIS SHOW</p>
          <h2 class="section-title" id="why-title">我們為什麼做這個節目</h2>
        </header>
        <p class="svc-section-lead" data-reveal>自動化的失敗，多半不是技術不夠好，而是順序做反了——先買設備，才想清楚要解決什麼。我們做了三十年精密製造，看過太多從第五步開始的案子。</p>
        <ul class="svc-deliver" role="list" data-reveal>
          <li class="svc-deliver__item">{CHECK_SVG}
            <span><b>可複用的思考工具</b>　每集示範一個能套用到任何產業的提問句，不是單一案例的答案。</span></li>
          <li class="svc-deliver__item">{CHECK_SVG}
            <span><b>明天就能開始的 SOP</b>　每集附執行步驟與預期效益，依五步演算法排序。</span></li>
          <li class="svc-deliver__item">{CHECK_SVG}
            <span><b>三語字幕</b>　繁體中文、English、日本語，方便跨境供應鏈的夥伴一起看。</span></li>
          <li class="svc-deliver__item">{CHECK_SVG}
            <span><b>不推銷</b>　欣晨的內容只出現在結尾，而且只在與主題真的相關時。</span></li>
        </ul>
      </div>
    </section>

  </main>
  {footer}
"""


# ── 單集文章頁 ────────────────────────────────────────────────────────────
def build_episode(db, ep, header, footer, prev_ep, next_ep):
    url = f"{BASE}{page_url(ep)}"
    title = ep["title"]
    desc = (ep.get("intro") or ep.get("summary") or title)[:150]
    ld = ld_block({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url, "url": url, "name": title, "inLanguage": "zh-TW",
         "isPartOf": {"@id": f"{BASE}videos.html"},
         "mainEntity": {"@id": f"https://www.youtube.com/watch?v={ep['id']}"}},
        video_object(ep),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "影片", "item": f"{BASE}videos.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]},
    ]})

    def section(sid, eyebrow, key, label, body, alt):
        return f"""
    <section class="section prod-detail{' prod-detail--alt' if alt else ''}" id="{sid}" aria-labelledby="{sid}-title">
      <div class="container ep-article">
        <header class="section-header" data-reveal>
          <p class="section-eyebrow">{eyebrow}</p>
          <h2 class="section-title" id="{sid}-title" data-i18n="{key}">{label}</h2>
        </header>
{body}
      </div>
    </section>"""

    blocks, alt = [], False
    if ep.get("key_points"):
        items = "\n".join(f"          <li>{e(p)}</li>" for p in ep["key_points"])
        blocks.append(section("points", "KEY POINTS", "ep_keypoints", "本集重點",
                              f'        <ol class="ep-points" data-reveal>\n{items}\n        </ol>', alt))
        alt = not alt
    if ep.get("sop_steps"):
        items = "\n".join(
            f'          <li class="prod-detail__type-item"><strong>STEP {i}</strong><p>{e(s)}</p></li>'
            for i, s in enumerate(ep["sop_steps"], 1))
        blocks.append(section("sop", "SOP", "ep_sop", "導入 SOP：明天就能開始",
                              '        <p class="svc-section-lead" data-reveal>依馬斯克五步演算法排序：質疑 → 刪除 → 簡化 → 加快 → 自動化。先做前面，自動化放最後。</p>\n'
                              f'        <ul class="prod-detail__type-list" role="list" data-reveal>\n{items}\n        </ul>', alt))
        alt = not alt
    if ep.get("benefits"):
        items = "\n".join(f'          <li class="svc-deliver__item">{CHECK_SVG}\n            <span>{e(b)}</span></li>'
                          for b in ep["benefits"])
        blocks.append(section("benefits", "BENEFITS", "ep_benefits", "執行效益",
                              f'        <ul class="svc-deliver" role="list" data-reveal>\n{items}\n        </ul>', alt))
        alt = not alt
    if ep.get("chapters"):
        items = "\n".join(
            f'          <li><a href="https://www.youtube.com/watch?v={ep["id"]}&amp;t={t}s" target="_blank" rel="noopener">'
            f'<span class="ep-chapters__time">{mmss(t)}</span>{e(label)}</a></li>'
            for label, t in ep["chapters"])
        blocks.append(section("chapters", "CHAPTERS", "ep_chapters", "章節",
                              f'        <ol class="ep-chapters" role="list" data-reveal>\n{items}\n        </ol>', alt))
        alt = not alt

    nav = []
    if prev_ep:
        nav.append(f'<a class="ep-nav__link" href="{page_url(prev_ep)}"><span>上一集</span>{e(prev_ep["title"])}</a>')
    if next_ep:
        nav.append(f'<a class="ep-nav__link ep-nav__link--next" href="{page_url(next_ep)}"><span>下一集</span>{e(next_ep["title"])}</a>')
    nav_html = (f'\n        <nav class="ep-nav" aria-label="集數導覽">\n          '
                + "\n          ".join(nav) + "\n        </nav>") if nav else ""

    return head(f"{title}｜{db['show']}｜欣晨工業", desc, url, ld,
                og_image=f"https://i.ytimg.com/vi/{ep['id']}/maxresdefault.jpg") + f"""
<body>
  <a href="#main-content" class="skip-link">跳到主要內容 / Skip to content</a>
  {header}
  <main id="main-content">

    <section class="page-banner" aria-labelledby="page-title">
      <div class="page-banner__bg" aria-hidden="true"></div>
      <div class="container ep-article">
        <div class="page-banner__content" data-reveal>
          <nav aria-label="麵包屑" class="breadcrumb">
            <ol class="breadcrumb__list" role="list">
              <li class="breadcrumb__item"><a href="index.html" data-i18n="nav_home">首頁</a></li>
              <li class="breadcrumb__item"><a href="videos.html" data-i18n="nav_videos">影片</a></li>
              <li class="breadcrumb__item" aria-current="page">EP.{ep['no']}</li>
            </ol>
          </nav>
          <p class="section-eyebrow">{e(db['show'])}　EP.{ep['no']}</p>
          <h1 class="page-banner__title ep-title" id="page-title">{e(title)}</h1>
          <p class="ep-meta"><time datetime="{ep['published']}">{ep['published']}</time>　·　{mmss(ep['seconds'])}　·　繁中／English／日本語字幕</p>
        </div>
      </div>
    </section>

    <section class="section prod-detail" id="watch" aria-label="影片">
      <div class="container ep-article">
        <div class="ep-embed" data-reveal>
          <iframe src="https://www.youtube-nocookie.com/embed/{ep['id']}" title="{e(title)}"
                  loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen></iframe>
        </div>
        <p class="ep-intro" data-reveal>{e(ep.get('intro') or ep.get('summary') or '')}</p>{nav_html}
      </div>
    </section>
{''.join(blocks)}

    <section class="cta-banner" aria-labelledby="cta-title">
      <div class="container">
        <div class="cta-banner__content" data-reveal>
          <p class="section-eyebrow">GET STARTED</p>
          <h2 class="cta-banner__title" id="cta-title">影片裡的作法，想用在您的產線上？</h2>
          <p class="cta-banner__desc">歡迎提供您的工件、節拍與現場條件，欣晨工業技術團隊將協助評估可行方案。</p>
          <a href="contact.html" class="btn btn--accent btn--xl" data-i18n="nav_contact">聯絡我們</a>
        </div>
      </div>
    </section>

  </main>
  {footer}
"""


# ── 首頁「最新一集」 ──────────────────────────────────────────────────────
def build_latest(db):
    if not db["episodes"]:
        return ""
    ep = db["episodes"][0]
    pts = (ep.get("key_points") or [])[:3]
    pts_html = ("\n" + "\n".join(f"              <li>{e(p)}</li>" for p in pts)) if pts else ""
    lead = e(ep.get("intro") or ep.get("summary") or "")
    if len(lead) > 140:
        lead = lead[:138] + "…"
    return f"""
    <section class="section latest-ep" id="latest-episode" aria-labelledby="latest-title">
      <div class="container">
        <header class="section-header" data-reveal>
          <p class="section-eyebrow">FIRST PRINCIPLES OF SMART MFG</p>
          <h2 class="section-title" id="latest-title" data-i18n="ep_latest">最新一集</h2>
        </header>
        <div class="latest-ep__grid" data-reveal>
          <a class="latest-ep__thumb video-card__thumb" href="{page_url(ep)}" aria-label="{e(ep['title'])}">
            <img src="https://i.ytimg.com/vi/{ep['id']}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">
            <span class="video-card__play" aria-hidden="true">▶</span>
            <span class="video-card__dur">{mmss(ep['seconds'])}</span>
          </a>
          <div class="latest-ep__body">
            <p class="video-card__date">EP.{ep['no']}　{ep['published']}</p>
            <h3 class="latest-ep__title"><a href="{page_url(ep)}">{e(ep['title'])}</a></h3>
            <p class="latest-ep__lead">{lead}</p>
            {'<ul class="latest-ep__points" role="list">' + pts_html + '\n            </ul>' if pts else ''}
            <div class="latest-ep__actions">
              <a href="{page_url(ep)}" class="btn btn--accent" data-i18n="ep_read">閱讀重點與 SOP</a>
              <a href="videos.html" class="btn btn--outline" data-i18n="ep_all">全部集數</a>
            </div>
          </div>
        </div>
      </div>
    </section>
"""


def update_index(db):
    s = INDEX.read_text(encoding="utf-8")
    if MARK_START not in s:
        anchor = '    <section class="section marquee-wrap" id="partners"'
        if anchor not in s:
            print("   ⚠️  首頁找不到插入位置，略過最新一集區塊")
            return
        s = s.replace(anchor, f"    {MARK_START}\n    {MARK_END}\n\n{anchor}", 1)
    a = s.index(MARK_START) + len(MARK_START)
    b = s.index(MARK_END)
    s = s[:a] + build_latest(db) + "    " + s[b:]
    INDEX.write_bytes(s.replace("\r\n", "\n").encode("utf-8"))


def update_sitemap(db):
    s = SITEMAP.read_text(encoding="utf-8")
    added = 0
    for ep in db["episodes"]:
        loc = f"{BASE}{page_url(ep)}"
        if f"<loc>{loc}</loc>" in s:
            continue
        s = s.replace("</urlset>", f"""
  <url>
    <loc>{loc}</loc>
    <lastmod>{ep['published']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>""")
        added += 1
    SITEMAP.write_bytes(s.replace("\r\n", "\n").encode("utf-8"))
    if added:
        print(f"   sitemap 新增 {added} 筆")


def write(path, text):
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json", metavar="FILE")
    ap.add_argument("--add", metavar="YOUTUBE_ID")
    ap.add_argument("--title")
    ap.add_argument("--date", default=str(date.today()))
    ap.add_argument("--seconds", type=int, default=0)
    ap.add_argument("--summary", default="")
    args = ap.parse_args()

    db = load()
    if args.from_json:
        ep = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        if add_episode(db, ep):
            print(f"   已加入：{ep['title']}")
    elif args.add:
        if not args.title:
            raise SystemExit("--add 需要同時給 --title")
        if add_episode(db, {"id": args.add, "title": args.title, "published": args.date,
                            "seconds": args.seconds, "summary": args.summary}):
            print(f"   已加入：{args.title}")

    number_episodes(db)
    save(db)

    header, footer = chrome()
    eps_old_first = sorted(db["episodes"], key=lambda x: x["published"])
    write(ROOT / "videos.html", build_index(db, header, footer))
    for i, ep in enumerate(eps_old_first):
        prev_ep = eps_old_first[i - 1] if i > 0 else None
        next_ep = eps_old_first[i + 1] if i + 1 < len(eps_old_first) else None
        write(ROOT / page_url(ep), build_episode(db, ep, header, footer, prev_ep, next_ep))
    update_index(db)
    update_sitemap(db)
    print(f"已重建：videos.html、{len(db['episodes'])} 個單集頁、首頁最新一集、sitemap")


if __name__ == "__main__":
    main()
