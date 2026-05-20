#!/usr/bin/env python3
# trigger: 2026-05-20s
"""
欣晨工業 Podcast — 高質感暗色投影片影片
NVIDIA/Bloomberg 風格：漸層發光圖表 + 玻璃磨砂卡片 + 動態字幕
OpenAI TTS: nova（小欣）x onyx（阿晨）
"""
import os, sys, json, subprocess, tempfile, shutil, math
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── 設計系統 ─────────────────────────────────────────────────────────────────
W, H        = 1920, 1080
# 顏色
BG          = (6,   8,  18)      # 極深藍黑
BG2         = (10, 14,  28)      # 稍亮背景
ACCENT      = (90, 140, 255)     # 電光藍（主強調）
ACCENT2     = (0,  210, 180)     # 青綠（次強調）
FEMALE_CLR  = (180, 100, 255)    # 小欣 — 紫
MALE_CLR    = (0,  200, 170)     # 阿晨 — 青
GLASS_BG    = (18,  24,  50)     # 玻璃卡片底色
GLASS_EDGE  = (50,  70, 120)     # 卡片邊框
TEXT1       = (235, 240, 255)    # 主文字（近白）
TEXT2       = (130, 150, 195)    # 副文字（淡藍灰）
TEXT3       = (70,  88, 130)     # 輕文字
GOLD        = (255, 215, 100)    # 金色強調

VOICE_FEMALE = "nova"
VOICE_MALE   = "onyx"
SILENCE_SEC  = 0.40
SPLIT_X      = 980   # 左右分隔

# ── 字型 ─────────────────────────────────────────────────────────────────────
def load_fonts():
    bold_cands = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
                  "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"]
    reg_cands  = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
                  "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"]
    bold = next((p for p in bold_cands if Path(p).exists()), None)
    reg  = next((p for p in reg_cands  if Path(p).exists()), None)
    if not bold:
        raise FileNotFoundError("找不到 CJK 字型")
    return bold, reg or bold

# ── 顏色工具 ─────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def blend_rgba(base, overlay_rgb, alpha):
    """在 base 圖層上疊加 overlay（alpha 0-1）"""
    return tuple(clamp(b*(1-alpha) + o*alpha) for b, o in zip(base, overlay_rgb))

# ── 繪圖工具 ─────────────────────────────────────────────────────────────────
def tw(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2]-bb[0], bb[3]-bb[1]

def draw_cx(draw, text, font, cx, y, color):
    w2, h2 = tw(draw, text, font)
    draw.text((cx - w2//2, y), text, font=font, fill=color)
    return h2

def wrap_text(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if draw.textbbox((0,0), test, font=font)[2] > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = test
    if cur: lines.append(cur)
    return lines

def radial_glow(img, cx, cy, r, color, intensity=0.4):
    """放射狀光暈"""
    d = ImageDraw.Draw(img)
    for dr in range(r, 0, -3):
        t = (1 - dr/r) ** 2
        c = tuple(clamp(bg + col*t*intensity)
                  for bg, col in zip(BG, color))
        d.ellipse([cx-dr, cy-dr, cx+dr, cy+dr], fill=c)

def draw_glow_line(draw, x1, y1, x2, y2, color, width=2, glow_w=8):
    """發光線條"""
    for w in range(glow_w, 0, -2):
        a = 0.06 * (1 - w/glow_w)
        gc = tuple(clamp(c*a*3) for c in color)
        draw.line([x1,y1,x2,y2], fill=gc, width=w)
    draw.line([x1,y1,x2,y2], fill=color, width=width)

# ── 圖表繪製（高質感版）──────────────────────────────────────────────────────
def draw_chart(img, draw, chart_type, items, x, y, w, h, bold_path, reg_path):
    fb = ImageFont.truetype(bold_path, 26)
    fr = ImageFont.truetype(reg_path,  22)

    if chart_type == "pillars":
        # 漸層光柱圖
        n   = min(len(items), 4)
        cw  = (w - 60) // n
        heights = [0.85, 0.65, 0.90, 0.70]
        colors  = [ACCENT, ACCENT2, FEMALE_CLR, MALE_CLR]
        base_y  = y + h - 30
        for i, label in enumerate(items[:n]):
            bx  = x + 30 + i * cw
            ph  = int((h - 80) * heights[i % len(heights)])
            col = colors[i % len(colors)]
            # 底部暗光
            for dr in range(40, 0, -4):
                gc = tuple(clamp(c * 0.3 * (1-dr/40)) for c in col)
                draw.ellipse([bx+cw//2-dr, base_y-10, bx+cw//2+dr, base_y+10], fill=gc)
            # 柱身漸層（深→亮）
            for gy in range(ph):
                t   = gy / ph
                gc  = lerp(tuple(c//4 for c in col), col, t)
                draw.line([bx+20, base_y-gy, bx+cw-20, base_y-gy], fill=gc)
            # 頂部發光
            draw.ellipse([bx+18, base_y-ph-8, bx+cw-18, base_y-ph+8],
                         fill=tuple(min(255,c+60) for c in col))
            # 標籤
            lw2, _ = tw(draw, label, fb)
            draw.text((bx+cw//2-lw2//2, base_y+8), label, font=fb, fill=TEXT2)

    elif chart_type == "cycle":
        # PDCA 光環圖
        cx2 = x + w//2
        cy2 = y + h//2
        R   = min(w, h)//2 - 30
        colors = [ACCENT, ACCENT2, FEMALE_CLR, MALE_CLR]
        labels = items[:4] if len(items) >= 4 else items + [""]*(4-len(items))
        # 背景環
        draw.ellipse([cx2-R-10, cy2-R-10, cx2+R+10, cy2+R+10],
                     outline=GLASS_EDGE, width=2)
        for i, label in enumerate(labels):
            if not label: continue
            angle = math.radians(i*90 - 45)
            ex = cx2 + int(R * math.cos(angle))
            ey = cy2 + int(R * math.sin(angle))
            col = colors[i % len(colors)]
            # 發光節點
            for gr in range(35, 5, -3):
                gc = tuple(clamp(c*0.35*(1-gr/35)) for c in col)
                draw.ellipse([ex-gr, ey-gr, ex+gr, ey+gr], fill=gc)
            draw.ellipse([ex-28, ey-28, ex+28, ey+28], fill=col)
            # 連線
            if i < 3:
                nx = cx2 + int(R*math.cos(math.radians((i+1)*90-45)))
                ny = cy2 + int(R*math.sin(math.radians((i+1)*90-45)))
                draw_glow_line(draw, ex, ey, nx, ny, col, width=2)
            lw2, lh2 = tw(draw, label, fb)
            draw.text((ex-lw2//2, ey-lh2//2), label, font=fb, fill=TEXT1)
        # 中心
        draw.ellipse([cx2-32, cy2-32, cx2+32, cy2+32],
                     fill=GLASS_BG, outline=ACCENT, width=2)
        draw_cx(draw, "改善", fb, cx2, cy2-13, ACCENT)

    elif chart_type == "bars":
        # 橫條對比圖（改善前後）
        n  = min(len(items), 4)
        bh = (h - 40) // n
        vals = [(85, 35), (90, 40), (75, 50), (80, 90)]
        for i, label in enumerate(items[:n]):
            by  = y + 20 + i * bh
            # 網格線
            for gx in [0.25, 0.5, 0.75]:
                draw.line([x+160+int((w-180)*gx), by, x+160+int((w-180)*gx), by+bh-12],
                          fill=GLASS_EDGE, width=1)
            before, after = vals[i % len(vals)]
            # 改善前（暗）
            bw_b = int((w-180) * before/100)
            for px in range(bw_b):
                t = px / bw_b
                c = lerp((40,55,90), (80,100,150), t)
                draw.line([x+160+px, by+8, x+160+px, by+bh//2-4], fill=c)
            # 改善後（亮）
            bw_a = int((w-180) * after/100)
            for px in range(bw_a):
                t = px / bw_a
                c = lerp(tuple(c2//3 for c2 in ACCENT), ACCENT, t)
                draw.line([x+160+px, by+bh//2+4, x+160+px, by+bh-12], fill=c)
            # 數值標籤
            draw.text((x+160+bw_a+6, by+bh//2+4), f"{after}%", font=fr, fill=ACCENT)
            # 項目名稱
            draw.text((x+8, by+bh//2-12), label, font=fr, fill=TEXT2)

    elif chart_type == "stats":
        # 大數字展示
        n   = min(len(items), 3)
        sw  = (w - 40) // n
        cols = [ACCENT, GOLD, ACCENT2]
        for i, val in enumerate(items[:n]):
            sx  = x + 20 + i*sw + sw//2
            sy  = y + h//2
            col = cols[i % len(cols)]
            # 發光背景圓
            radial_glow(img, sx, sy, 90, col, 0.3)
            # 大數字
            f_big = ImageFont.truetype(bold_path, 72)
            draw_cx(draw, val, f_big, sx, sy-38, col)
            # 底線
            draw.rectangle([sx-40, sy+42, sx+40, sy+45],
                           fill=tuple(c//2 for c in col))

    elif chart_type == "flow":
        n   = min(len(items), 4)
        fw  = (w - 50) // n
        cols = [ACCENT, ACCENT2, FEMALE_CLR, MALE_CLR]
        for i, label in enumerate(items[:n]):
            bx  = x + 25 + i*fw
            by  = y + h//2 - 45
            col = cols[i % len(cols)]
            # 發光框
            for pad in range(6, 0, -2):
                gc = tuple(clamp(c*0.2) for c in col)
                draw.rounded_rectangle([bx-pad, by-pad, bx+fw-25+pad, by+90+pad],
                                       radius=12+pad, fill=gc)
            draw.rounded_rectangle([bx, by, bx+fw-25, by+90],
                                   radius=12, fill=GLASS_BG, outline=col, width=2)
            lw2, lh2 = tw(draw, label, fb)
            draw.text((bx+(fw-25)//2-lw2//2, by+45-lh2//2), label, font=fb, fill=col)
            if i < n-1:
                ax = bx + fw - 10
                ay = by + 45
                draw.polygon([(ax,ay-14),(ax+20,ay),(ax,ay+14)], fill=col)

# ── 玻璃卡片（Glassmorphism）────────────────────────────────────────────────
def draw_glass_cards(img, draw, cards, x, y, w, h, bold_path, reg_path):
    n   = len(cards[:3])
    ch  = (h - (n-1)*14) // n
    cols = [ACCENT, ACCENT2, FEMALE_CLR]
    fb  = ImageFont.truetype(bold_path, 30)
    fr  = ImageFont.truetype(reg_path,  27)
    fs  = ImageFont.truetype(reg_path,  22)

    for i, card in enumerate(cards[:n]):
        cy2 = y + i*(ch+14)
        col = cols[i % len(cols)]

        # 發光邊框效果
        for pad in range(5, 0, -1):
            gc = tuple(clamp(c*0.15*(1-pad/5)) for c in col)
            draw.rounded_rectangle([x-pad, cy2-pad, x+w+pad, cy2+ch+pad],
                                   radius=18+pad, fill=gc)

        # 玻璃底色
        draw.rounded_rectangle([x, cy2, x+w, cy2+ch],
                                radius=16, fill=GLASS_BG)

        # 頂部色帶
        draw.rounded_rectangle([x, cy2, x+w, cy2+6], radius=3, fill=col)

        # 類別標籤 + 小圓點
        draw.ellipse([x+16, cy2+20, x+28, cy2+32], fill=col)
        draw.text((x+36, cy2+15), card["label"], font=fb, fill=col)

        # 分隔線
        draw.rectangle([x+16, cy2+54, x+w-16, cy2+56], fill=GLASS_EDGE)

        # 內容文字
        lines = wrap_text(draw, card["text"], fr, w-36)[:3]
        ty2   = cy2 + 66
        for line in lines:
            draw.text((x+16, ty2), line, font=fr, fill=TEXT1)
            ty2 += 36

# ── 完整影格建立 ──────────────────────────────────────────────────────────────
def build_frame(slide, dialogue_text, speaker, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── 全域背景光暈 ──────────────────────────────────────────────────────
    radial_glow(img, W//4,  H//2, 600, (40, 80, 180), 0.15)
    radial_glow(img, W*3//4, H//2, 500, (0,  150, 140), 0.12)

    # 細網格
    for gx in range(0, W, 80):
        draw.line([gx, 0, gx, H], fill=(14, 20, 40))
    for gy in range(0, H, 80):
        draw.line([0, gy, W, gy], fill=(14, 20, 40))

    # ── 頂部品牌欄 ────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 58], fill=(8, 12, 26))
    draw_glow_line(draw, 0, 58, W, 58, ACCENT, width=2, glow_w=10)

    fb_hd  = ImageFont.truetype(bold_path, 25)
    fr_hd  = ImageFont.truetype(reg_path,  23)
    draw.text((44, 16), "欣晨工業有限公司", font=fb_hd, fill=TEXT1)
    draw.text((310, 18), "智慧製造深度對談  SMART MANUFACTURING DEEP DIVE",
              font=fr_hd, fill=TEXT2)
    sl_txt = f"SLIDE {slide['id']}"
    sl_w, _ = tw(draw, sl_txt, fr_hd)
    draw.text((W-sl_w-44, 18), sl_txt, font=fr_hd, fill=TEXT3)

    # ── 左欄：標題 + 圖表 ────────────────────────────────────────────────
    LPAD = 48
    fb_t  = ImageFont.truetype(bold_path, 60)
    fr_s  = ImageFont.truetype(reg_path,  28)

    title_lines = wrap_text(draw, slide["title"], fb_t, SPLIT_X - LPAD - 30)
    ty = 78
    for line in title_lines:
        draw.text((LPAD, ty), line, font=fb_t, fill=TEXT1)
        _, lh2 = tw(draw, line, fb_t)
        ty += lh2 + 6

    # 標題下方發光線
    draw_glow_line(draw, LPAD, ty+12, LPAD+220, ty+12, ACCENT, width=2, glow_w=8)

    chart_y = ty + 36
    chart_h = H - 190 - chart_y
    draw_chart(img, draw, slide.get("chart_type","pillars"),
               slide.get("chart_items",[]), LPAD, chart_y,
               SPLIT_X - LPAD - 24, chart_h, bold_path, reg_path)

    # ── 中間光線 ─────────────────────────────────────────────────────────
    draw_glow_line(draw, SPLIT_X, 58, SPLIT_X, H-175, GLASS_EDGE, width=1, glow_w=6)

    # ── 右欄：玻璃卡片 ───────────────────────────────────────────────────
    RPAD = 32
    RX   = SPLIT_X + RPAD
    RW   = W - SPLIT_X - RPAD*2
    draw_glass_cards(img, draw, slide.get("cards",[])[:3],
                     RX, 76, RW, H-76-182, bold_path, reg_path)

    # ── 底部字幕欄（說話者頭像 + 文字）──────────────────────────────────
    SUB_Y = H - 172
    # 底色
    for gy2 in range(SUB_Y, H):
        t  = (gy2 - SUB_Y) / (H - SUB_Y)
        c  = lerp(BG2, (4,6,14), t)
        draw.line([0, gy2, W, gy2], fill=c)
    draw_glow_line(draw, 0, SUB_Y, W, SUB_Y, ACCENT, width=2, glow_w=12)

    if dialogue_text:
        spk_col  = FEMALE_CLR if speaker == "Host1" else MALE_CLR
        spk_name = "小欣" if speaker == "Host1" else "阿晨"
        spk_role = "女主持人" if speaker == "Host1" else "男主持人"

        # 說話者小圓頭像
        AV_X, AV_Y, AV_R = 54, SUB_Y + 86, 38
        for ar in range(AV_R+14, AV_R, -2):
            gc = tuple(clamp(c*0.4*(1-(ar-AV_R)/14)) for c in spk_col)
            draw.ellipse([AV_X-ar, AV_Y-ar, AV_X+ar, AV_Y+ar], fill=gc)
        draw.ellipse([AV_X-AV_R, AV_Y-AV_R, AV_X+AV_R, AV_Y+AV_R], fill=spk_col)
        fb_av = ImageFont.truetype(bold_path, 28)
        init_w, init_h = tw(draw, spk_name[0], fb_av)
        draw.text((AV_X-init_w//2, AV_Y-init_h//2), spk_name[0],
                  font=fb_av, fill=TEXT1)

        # 名稱 + 角色
        fb_sp = ImageFont.truetype(bold_path, 26)
        fr_ro = ImageFont.truetype(reg_path,  20)
        draw.text((AV_X+AV_R+14, SUB_Y+64), spk_name, font=fb_sp, fill=spk_col)
        draw.text((AV_X+AV_R+14, SUB_Y+96), spk_role, font=fr_ro, fill=TEXT3)

        # 對話文字（最多2行）
        fb_sub = ImageFont.truetype(reg_path, 36)
        sub_lines = wrap_text(draw, dialogue_text, fb_sub, W-220)[:2]
        sty = SUB_Y + 20
        for line in sub_lines:
            draw.text((148, sty), line, font=fb_sub, fill=TEXT1)
            sty += 48

    # 波形預留（最底部）
    draw.rectangle([0, H-3, W, H], fill=(2,4,10))

    img.save(out_path)

# ── 腳本生成 ─────────────────────────────────────────────────────────────────
def generate_script(ac_client):
    prompt = """你是欣晨工業 Podcast「智慧製造深度對談」製作人。
主持人：小欣（女，活潑好奇）、阿晨（男，資深工程師）
名字取自「欣晨工業」，台灣桃園，1975年，51年精密製造，TPS核心哲學。

今集：豐田改善文化（Kaizen）在台灣製造業的實踐

請輸出：
=== SLIDES ===
[
  {"id":1,"title":"投影片標題（10字）","chart_type":"pillars",
   "chart_items":["改善","JIT","自働化"],
   "cards":[{"label":"現象","text":"40字以內"},{"label":"原因","text":"40字"},{"label":"重點","text":"40字"}],
   "dialogue_count":5}
]
chart_type: pillars/cycle/bars/stats/flow

=== DIALOGUE ===
小欣: （60-80字）
阿晨: （60-80字）
共18-22輪，繁體中文，自然口語，不要其他說明"""

    print("Claude 生成腳本...")
    msg = ac_client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()

    slides, dialogue = [], []
    if "=== SLIDES ===" in raw and "=== DIALOGUE ===" in raw:
        parts     = raw.split("=== DIALOGUE ===")
        slide_raw = parts[0].split("=== SLIDES ===")[1].strip()
        dial_raw  = parts[1].strip()
        try:
            j1 = slide_raw.index("["); j2 = slide_raw.rindex("]")+1
            slides = json.loads(slide_raw[j1:j2])
        except:
            slides = default_slides()
        for line in dial_raw.split("\n"):
            line = line.strip()
            for pfx, sp in [("小欣:","Host1"),("小欣：","Host1"),
                            ("阿晨:","Host2"),("阿晨：","Host2")]:
                if line.startswith(pfx):
                    t = line[len(pfx):].strip()
                    if t: dialogue.append({"speaker":sp,"text":t})
                    break
    else:
        slides = default_slides()
        for line in raw.split("\n"):
            for pfx,sp in [("小欣:","Host1"),("小欣：","Host1"),
                           ("阿晨:","Host2"),("阿晨：","Host2")]:
                if line.strip().startswith(pfx):
                    t = line.strip()[len(pfx):].strip()
                    if t: dialogue.append({"speaker":sp,"text":t})
                    break

    if not dialogue:
        raise ValueError("無法解析對話")

    seg_map, si, cnt = {}, 0, 0
    for i in range(len(dialogue)):
        if si < len(slides): seg_map[i] = si
        else: seg_map[i] = len(slides)-1
        cnt += 1
        if si < len(slides) and cnt >= slides[si].get("dialogue_count", 5):
            si = min(si+1, len(slides)-1); cnt = 0

    print(f"腳本完成：{len(slides)} 張投影片，{len(dialogue)} 輪對話")
    return slides, dialogue, seg_map

def default_slides():
    return [
        {"id":1,"title":"什麼是 Kaizen 改善？",
         "chart_type":"pillars","chart_items":["改善","JIT","自働化"],
         "cards":[{"label":"定義","text":"Kaizen 意為「持續改善」，讓每個人每天進步一點點，積累出卓越成果。"},
                  {"label":"七大浪費","text":"過量生產、等待、運輸、庫存、動作、加工過度、不良品。"},
                  {"label":"精神","text":"沒有最好，只有更好。每個問題都是改善機會，而非災難。"}],
         "dialogue_count":5},
        {"id":2,"title":"TPS 豐田生產系統",
         "chart_type":"cycle","chart_items":["Plan","Do","Check","Act"],
         "cards":[{"label":"即時生產 JIT","text":"正確時間、正確數量、正確品項——消除庫存浪費，讓生產線流暢。"},
                  {"label":"自働化 Jidoka","text":"設備能自動偵測異常並停機，品質問題不流入下一工序。"},
                  {"label":"現地現物","text":"親自到現場確認，不信二手報告，用眼睛和雙手理解問題。"}],
         "dialogue_count":5},
        {"id":3,"title":"台灣工廠導入 Kaizen",
         "chart_type":"bars","chart_items":["換線時間","不良率","庫存天數","設備稼動率"],
         "cards":[{"label":"SMED 快速換模","text":"把換線時間從 2 小時縮短到 30 分鐘，生產彈性提升 3 倍。"},
                  {"label":"Poka-yoke 防呆","text":"從機構設計源頭杜絕人為錯誤，實現零缺陷生產目標。"},
                  {"label":"5S 視覺管理","text":"整理整頓清掃清潔素養，讓任何異常在 30 秒內被一眼看出。"}],
         "dialogue_count":5},
        {"id":4,"title":"欣晨工業的實踐",
         "chart_type":"stats","chart_items":["51年","1975","桃園"],
         "cards":[{"label":"現地現物落實","text":"每個專案啟動前，欣晨工程師必定親赴客戶廠房，現場丈量。"},
                  {"label":"持續改善文化","text":"從設計圖面到現場調機，永遠問自己：這裡還能更好嗎？"},
                  {"label":"聯絡欣晨工業","text":"桃園市大園區，電話 03-381-4497，hsinchan.com"}],
         "dialogue_count":5},
    ]

# ── TTS + 音訊處理 ────────────────────────────────────────────────────────────
def audio_duration(path):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",str(path)],
                       capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def generate_all_audio(dialogue, tmp_dir):
    oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    tmp = Path(tmp_dir)
    print(f"OpenAI TTS 生成 {len(dialogue)} 段音訊...")
    segments = []
    for i, turn in enumerate(dialogue):
        voice = VOICE_FEMALE if turn["speaker"]=="Host1" else VOICE_MALE
        out   = tmp / f"seg_{i:03d}.mp3"
        resp  = oai.audio.speech.create(model="tts-1", voice=voice,
                                        input=turn["text"], speed=0.95)
        resp.stream_to_file(str(out))
        dur = audio_duration(out)
        segments.append({"path":str(out),"speaker":turn["speaker"],
                         "text":turn["text"],"duration":dur})
        if (i+1) % 5 == 0:
            print(f"   {i+1}/{len(dialogue)} 段完成")
    print("TTS 完成")
    return segments

def concat_full_audio(segments, tmp_dir):
    tmp = Path(tmp_dir)
    silence = tmp/"silence.mp3"
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=24000:cl=mono",
                    "-t",str(SILENCE_SEC),"-q:a","9","-acodec","libmp3lame",str(silence)],
                   capture_output=True, check=True)
    lst = tmp/"audio_list.txt"
    with open(lst,"w") as f:
        for s in segments:
            f.write(f"file '{s['path']}'\nfile '{silence}'\n")
    full = tmp/"full_audio.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(full)],
                   capture_output=True, check=True)
    total = sum(s["duration"]+SILENCE_SEC for s in segments)
    print(f"音訊完成：{total/60:.1f} 分鐘")
    return str(full), total

# ── 影片合成（含投影片切換過場）─────────────────────────────────────────────
def render_video(slides, seg_map, segments, bold_path, reg_path,
                 audio_path, total_dur, tmp_dir, out_path):
    tmp = Path(tmp_dir)
    print(f"建立 {len(segments)} 個高質感影格...")

    concat_lines = []
    prev_slide   = -1
    for i, seg in enumerate(segments):
        slide_idx = seg_map.get(i, len(slides)-1)
        slide     = slides[slide_idx]
        frame     = tmp / f"frame_{i:03d}.png"
        build_frame(slide, seg["text"], seg["speaker"], bold_path, reg_path, frame)

        dur = seg["duration"] + SILENCE_SEC

        # 投影片切換時插入 0.3s 淡黑過場
        if slide_idx != prev_slide and prev_slide >= 0:
            black = tmp / f"black_{i:03d}.png"
            Image.new("RGB", (W, H), (2,3,8)).save(black)
            concat_lines.append(f"file '{black}'\nduration 0.3")

        concat_lines.append(f"file '{frame}'\nduration {dur:.3f}")
        prev_slide = slide_idx

        if (i+1) % 5 == 0:
            print(f"   {i+1}/{len(segments)} 影格完成")

    # 最後一幀重複
    concat_lines.append(f"file '{tmp}/frame_{len(segments)-1:03d}.png'")
    concat_f = tmp/"frames.txt"
    concat_f.write_text("\n".join(concat_lines))

    print("FFmpeg 合成影片...")
    silent = tmp/"silent.mp4"
    r1 = subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_f),
        "-vf","fps=30,scale=1920:1080",
        "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",str(silent)
    ], capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(f"FFmpeg 靜音影片失敗：{r1.stderr[-500:]}")

    # 加音訊 + 藍色波形
    fc = ("[0:v]scale=1920:1080[bg];"
          "[1:a]showwaves=s=1920x162:mode=cline:rate=30:colors=5a8cff|00d4b4[wave];"
          "[bg][wave]overlay=0:915[vout]")
    r2 = subprocess.run([
        "ffmpeg","-y","-i",str(silent),"-i",str(audio_path),
        "-filter_complex",fc,"-map","[vout]","-map","1:a",
        "-c:v","libx264","-preset","fast","-crf","22",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-t",str(total_dur),"-r","30",str(out_path)
    ], capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(f"FFmpeg 最終合成失敗：{r2.stderr[-500:]}")

    size = Path(out_path).stat().st_size/1024/1024
    print(f"影片完成：{size:.0f} MB，{total_dur/60:.1f} 分鐘")

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  欣晨工業 Podcast — 高質感暗色投影片影片")
    print("  NVIDIA/Bloomberg 風格 | OpenAI TTS")
    print("=" * 60 + "\n")

    tw   = datetime.now(timezone(timedelta(hours=8)))
    date = tw.strftime("%Y-%m-%d")
    ac   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        slides, dialogue, seg_map = generate_script(ac)
        bold_path, reg_path = load_fonts()
        segments  = generate_all_audio(dialogue, tmpdir)
        audio_path, total_dur = concat_full_audio(segments, tmpdir)
        video_out = Path(tmpdir) / f"test_podcast_{date}.mp4"
        render_video(slides, seg_map, segments, bold_path, reg_path,
                     audio_path, total_dur, tmpdir, video_out)
        final = Path(f"test_podcast_{date}.mp4")
        shutil.copy(video_out, final)
        print(f"\n完成：{final}（{total_dur/60:.1f} 分鐘）")
        print("請至 GitHub Actions Artifacts 下載 test-podcast-video")

if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)
