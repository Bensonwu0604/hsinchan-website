#!/usr/bin/env python3
# trigger: 2026-05-20u
"""
欣晨工業 Podcast — 半身主持人動畫 + 投影片
左側：小欣/阿晨半身圖（4幀呼吸動畫）
右側：投影片（標題 + 圖表 + 玻璃卡片）
底部：說話者姓名 + 字幕
OpenAI TTS: nova（小欣）x onyx（阿晨）
"""
import os, sys, json, subprocess, tempfile, shutil, math
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# ── 版面常數 ─────────────────────────────────────────────────────────────────
W, H          = 1920, 1080
BG            = (6,   8,  18)
BG2           = (10,  14,  30)
ACCENT        = (90, 140, 255)
ACCENT2       = (0,  210, 180)
FEMALE_CLR    = (180, 100, 255)   # 小欣 紫
MALE_CLR      = (0,  195, 165)    # 阿晨 青
GLASS_BG      = (16,  22,  48)
GLASS_EDGE    = (50,  70, 120)
TEXT1         = (235, 240, 255)
TEXT2         = (130, 150, 195)
TEXT3         = (60,  78, 115)
GOLD          = (255, 215, 100)

VOICE_FEMALE  = "nova"
VOICE_MALE    = "onyx"
SILENCE_SEC   = 0.40

AVATAR_W      = 820    # 左側主持人區寬度
CONTENT_X     = 850    # 右側內容起始 X
ANIM_FRAMES   = 4      # 每段對話的動畫幀數

# ── 字型 ─────────────────────────────────────────────────────────────────────
def load_fonts():
    bold = next((p for p in [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    ] if Path(p).exists()), None)
    reg = next((p for p in [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ] if Path(p).exists()), None)
    if not bold: raise FileNotFoundError("找不到 CJK 字型")
    return bold, reg or bold

# ── 工具 ─────────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def clamp(v): return max(0, min(255, int(v)))

def dim_col(c, factor, bg=BG):
    return tuple(clamp(c2*factor + bg[i]*(1-factor)) for i,c2 in enumerate(c))

def tw(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2]-bb[0], bb[3]-bb[1]

def draw_cx(draw, text, font, cx, y, color):
    w2, h2 = tw(draw, text, font)
    draw.text((cx-w2//2, y), text, font=font, fill=color)
    return h2

def wrap_text(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        test = cur+ch
        if draw.textbbox((0,0), test, font=font)[2] > max_w and cur:
            lines.append(cur); cur = ch
        else: cur = test
    if cur: lines.append(cur)
    return lines

def glow_line(draw, x1,y1,x2,y2, color, w=2, gw=8):
    for gw2 in range(gw,0,-2):
        gc = tuple(clamp(c*0.08*(gw2/gw)) for c in color)
        draw.line([x1,y1,x2,y2], fill=gc, width=gw2)
    draw.line([x1,y1,x2,y2], fill=color, width=w)

def radial_glow(draw, img, cx, cy, r, color, strength=0.2):
    for dr in range(r,0,-4):
        t = (1-dr/r)**1.5
        c = lerp(BG, color, t*strength)
        draw.ellipse([cx-dr,cy-dr,cx+dr,cy+dr], fill=c)

# ── 半身主持人繪圖 ────────────────────────────────────────────────────────────
SKIN_F = (238, 196, 165)   # 女性膚色
SKIN_M = (215, 175, 142)   # 男性膚色
HAIR_F = (38,  28,  22)    # 深棕髮
HAIR_M = (50,  38,  28)    # 深棕髮（男）
TOP_F  = (145, 75, 225)    # 小欣上衣 — 紫
TOP_FL = (175, 105, 250)   # 上衣亮色
TOP_M  = (22,  48,  95)    # 阿晨西裝 — 深藍
TOP_ML = (42,  68, 118)    # 西裝亮色
TIE_M  = (185, 40,  40)    # 領帶紅

def draw_female(img, cx, base_y, active, anim_t):
    """小欣半身像（anim_t: 0.0-1.0, 呼吸動畫相位）"""
    alpha  = 1.0 if active else 0.28
    # 輕微呼吸：頭部微微上下浮動
    bob    = int(math.sin(anim_t * math.pi * 2) * 6)
    draw   = ImageDraw.Draw(img)

    def da(c): return dim_col(c, alpha)
    skin = da(SKIN_F); hair = da(HAIR_F)
    top  = da(TOP_F);  topl = da(TOP_FL)

    hy = base_y + bob   # 呼吸偏移

    # ── 發光背景圓 ──
    if active:
        for gr in range(180, 0, -6):
            t = (1-gr/180)**2
            gc = tuple(clamp(c*t*0.35) for c in FEMALE_CLR)
            draw.ellipse([cx-gr, hy-gr+60, cx+gr, hy+gr+60], fill=gc)

    # ── 長髮（頭後方）──
    draw.ellipse([cx-68, hy-90, cx-30, hy+190], fill=hair)
    draw.ellipse([cx+30, hy-90, cx+68, hy+190], fill=hair)
    # 瀏海
    draw.ellipse([cx-60, hy-115, cx+60, hy-30], fill=hair)

    # ── 頭部 ──
    draw.ellipse([cx-55, hy-100, cx+55, hy+75], fill=skin)

    # ── 臉部特徵 ──
    # 眉毛
    for ex in [cx-20, cx+20]:
        draw.arc([ex-13, hy-38, ex+13, hy-22], 200, 340, fill=hair, width=3)
    # 眼睛
    for ex in [cx-20, cx+20]:
        draw.ellipse([ex-11, hy-22, ex+11, hy-4], fill=(250,250,255))
        draw.ellipse([ex-6, hy-20, ex+6, hy-6], fill=(35,28,22))
        draw.ellipse([ex-3, hy-19, ex-1, hy-17], fill=(255,255,255))  # 高光
    # 鼻子
    draw.line([cx-3, hy+5, cx-6, hy+18], fill=tuple(clamp(c*0.82) for c in skin), width=2)
    # 嘴巴（微笑）
    draw.arc([cx-14, hy+22, cx+14, hy+38], 12, 168, fill=(175, 92, 92), width=3)
    # 腮紅
    for ex in [cx-32, cx+32]:
        for r in range(14, 0, -2):
            draw.ellipse([ex-r, hy+8, ex+r, hy+8+r], fill=(240,185,170,0))

    # ── 頸部 ──
    draw.rectangle([cx-14, hy+72, cx+14, hy+108], fill=skin)

    # ── 肩膀/上衣 ──
    sy = hy + 105
    draw.polygon([(cx-85, sy), (cx+85, sy), (cx+62, sy+220), (cx-62, sy+220)], fill=top)
    # V領
    draw.polygon([(cx-24, sy+8), (cx, sy+50), (cx+24, sy+8)], fill=topl)

    # ── 左手臂（自然垂放）──
    draw.polygon([(cx-85, sy+12), (cx-108, sy+12),
                  (cx-118, sy+145), (cx-95, sy+145)], fill=top)
    draw.ellipse([cx-118, sy+138, cx-92, sy+162], fill=skin)

    # ── 右手臂（舉起手勢，隨動畫微動）──
    arm_lift = int(anim_t * 12) if active else 0
    draw.polygon([(cx+85, sy+12), (cx+108, sy+12),
                  (cx+122+arm_lift//2, sy+60-arm_lift),
                  (cx+100+arm_lift//2, sy+60-arm_lift)], fill=top)
    # 前臂
    ax_end = cx + 120 + arm_lift
    ay_end = sy + 55 - arm_lift
    draw.polygon([(cx+108, sy+12),
                  (cx+125, sy+12),
                  (ax_end+18, ay_end),
                  (ax_end,   ay_end)], fill=skin)
    draw.ellipse([ax_end-2, ay_end-6, ax_end+22, ay_end+18], fill=skin)

def draw_male(img, cx, base_y, active, anim_t):
    """阿晨半身像（anim_t: 0.0-1.0）"""
    alpha = 1.0 if active else 0.28
    bob   = int(math.sin(anim_t * math.pi * 2) * 5)
    draw  = ImageDraw.Draw(img)

    def da(c): return dim_col(c, alpha)
    skin = da(SKIN_M); hair = da(HAIR_M)
    top  = da(TOP_M);  topl = da(TOP_ML)
    tie  = da(TIE_M)

    hy = base_y + bob

    # 發光背景
    if active:
        for gr in range(180, 0, -6):
            t = (1-gr/180)**2
            gc = tuple(clamp(c*t*0.35) for c in MALE_CLR)
            draw.ellipse([cx-gr, hy-gr+60, cx+gr, hy+gr+60], fill=gc)

    # 短髮（頭頂）
    draw.ellipse([cx-62, hy-112, cx+62, hy-40], fill=hair)
    for dx in [-55, -50, 50, 55]:
        draw.ellipse([cx+dx-10, hy-80, cx+dx+10, hy-20], fill=hair)

    # 頭部
    draw.ellipse([cx-58, hy-98, cx+58, hy+78], fill=skin)

    # 臉部
    # 眉毛（平直，男性特徵）
    for ex in [cx-21, cx+21]:
        draw.line([ex-12, hy-35, ex+12, hy-31], fill=hair, width=4)
    # 眼睛
    for ex in [cx-21, cx+21]:
        draw.ellipse([ex-12, hy-24, ex+12, hy-5], fill=(250,250,255))
        draw.ellipse([ex-7, hy-22, ex+7, hy-7], fill=(35,28,22))
        draw.ellipse([ex-4, hy-21, ex-2, hy-19], fill=(255,255,255))
    # 鼻子
    draw.line([cx, hy+5, cx-5, hy+20], fill=tuple(clamp(c*0.8) for c in skin), width=2)
    draw.arc([cx-7, hy+14, cx+7, hy+22], 10, 170, fill=tuple(clamp(c*0.8) for c in skin), width=2)
    # 嘴（輕微微笑）
    draw.arc([cx-12, hy+26, cx+12, hy+40], 15, 165, fill=(160, 85, 85), width=3)

    # 頸部
    draw.rectangle([cx-15, hy+75, cx+15, hy+110], fill=skin)

    # 西裝
    sy = hy + 108
    draw.polygon([(cx-90, sy), (cx+90, sy), (cx+65, sy+225), (cx-65, sy+225)], fill=top)
    # 西裝翻領
    draw.polygon([(cx-28, sy), (cx-10, sy+65), (cx-45, sy+8)], fill=topl)
    draw.polygon([(cx+28, sy), (cx+10, sy+65), (cx+45, sy+8)], fill=topl)
    # 白襯衫
    draw.polygon([(cx-10, sy+3), (cx+10, sy+3), (cx+6, sy+80), (cx-6, sy+80)],
                 fill=(220, 228, 245))
    # 領帶
    draw.polygon([(cx-5, sy+18), (cx+5, sy+18), (cx+3, sy+90), (cx-3, sy+90)], fill=tie)
    draw.polygon([(cx-7, sy+88), (cx+7, sy+88), (cx+3, sy+105), (cx-3, sy+105)], fill=tie)

    # 左手臂
    draw.polygon([(cx-90, sy+14), (cx-113, sy+14),
                  (cx-123, sy+150), (cx-100, sy+150)], fill=top)
    draw.ellipse([cx-123, sy+142, cx-97, sy+168], fill=skin)

    # 右手臂（指向/說明動作，有動畫）
    lift = int(20 + anim_t * 18) if active else 5
    draw.polygon([(cx+90, sy+14),
                  (cx+113, sy+14),
                  (cx+140, sy+30-lift),
                  (cx+118, sy+30-lift)], fill=top)
    # 前臂指向
    ax = cx + 140
    ay = sy + 28 - lift
    draw.polygon([(cx+115, sy+28-lift), (cx+132, sy+28-lift),
                  (ax+60,  ay-25),
                  (ax+42,  ay-25)], fill=skin)
    # 手掌（指向）
    draw.ellipse([ax+38, ay-38, ax+66, ay-18], fill=skin)
    # 食指
    draw.line([ax+52, ay-36, ax+65, ay-55], fill=skin, width=10)

# ── 圖表（沿用上版，縮小適應右側）────────────────────────────────────────────
def draw_chart_right(img, draw, chart_type, items, x, y, w, h, bold_path, reg_path):
    fb = ImageFont.truetype(bold_path, 24)
    fr = ImageFont.truetype(reg_path,  20)

    if chart_type == "pillars":
        n = min(len(items), 4)
        cw = (w-40)//n
        colors = [ACCENT, ACCENT2, FEMALE_CLR, MALE_CLR]
        heights = [0.85, 0.65, 0.90, 0.70]
        base_y2 = y+h-25
        for i, label in enumerate(items[:n]):
            bx = x+20+i*cw; col = colors[i%4]
            ph = int((h-60)*heights[i%4])
            for gy in range(ph):
                t = gy/ph
                gc = lerp(tuple(c//5 for c in col), col, t)
                draw.line([bx+14, base_y2-gy, bx+cw-14, base_y2-gy], fill=gc)
            draw.ellipse([bx+12, base_y2-ph-6, bx+cw-12, base_y2-ph+6],
                         fill=tuple(min(255,c+60) for c in col))
            lw2,_ = tw(draw, label, fb)
            draw.text((bx+cw//2-lw2//2, base_y2+5), label, font=fb, fill=TEXT2)

    elif chart_type == "cycle":
        cx2 = x+w//2; cy2 = y+h//2; R = min(w,h)//2-25
        colors = [ACCENT, ACCENT2, FEMALE_CLR, MALE_CLR]
        items4 = (items+["","","",""])[:4]
        draw.ellipse([cx2-R-8,cy2-R-8,cx2+R+8,cy2+R+8], outline=GLASS_EDGE, width=1)
        for i, label in enumerate(items4):
            if not label: continue
            a = math.radians(i*90-45)
            ex = cx2+int(R*math.cos(a)); ey = cy2+int(R*math.sin(a))
            col = colors[i%4]
            for gr in range(28,4,-3):
                gc = tuple(clamp(c*0.4*(1-gr/28)) for c in col)
                draw.ellipse([ex-gr,ey-gr,ex+gr,ey+gr], fill=gc)
            draw.ellipse([ex-22,ey-22,ex+22,ey+22], fill=col)
            lw2, lh2 = tw(draw, label, fb)
            draw.text((ex-lw2//2, ey-lh2//2), label, font=fb, fill=TEXT1)
        draw.ellipse([cx2-26,cy2-26,cx2+26,cy2+26], fill=GLASS_BG, outline=ACCENT, width=2)
        draw_cx(draw, "改善", fb, cx2, cy2-12, ACCENT)

    elif chart_type == "bars":
        n = min(len(items),4); bh = (h-30)//n
        vals = [(85,35),(90,40),(75,50),(80,90)]
        for i, label in enumerate(items[:n]):
            by2 = y+15+i*bh; bef,aft = vals[i%4]
            draw.rectangle([x+130,by2+4,x+w,by2+bh-8], fill=(18,26,48))
            bw_b = int((w-140)*bef/100)
            for px in range(bw_b):
                gc = lerp((40,55,90),(70,95,140), px/bw_b)
                draw.line([x+130+px,by2+4,x+130+px,by2+bh//2-2], fill=gc)
            bw_a = int((w-140)*aft/100)
            for px in range(bw_a):
                gc = lerp(tuple(c//4 for c in ACCENT), ACCENT, px/bw_a)
                draw.line([x+130+px,by2+bh//2+2,x+130+px,by2+bh-8], fill=gc)
            draw.text((x+130+bw_a+5, by2+bh//2+2), f"{aft}%", font=fr, fill=ACCENT)
            draw.text((x+4, by2+bh//2-10), label, font=fr, fill=TEXT2)

    elif chart_type == "stats":
        n = min(len(items),3); sw = (w-20)//n
        colors2 = [ACCENT, GOLD, ACCENT2]
        for i, val in enumerate(items[:n]):
            sx = x+10+i*sw+sw//2; sy = y+h//2; col = colors2[i%3]
            f_big = ImageFont.truetype(bold_path, 58)
            draw_cx(draw, val, f_big, sx, sy-30, col)
            draw.rectangle([sx-35,sy+32,sx+35,sy+35], fill=tuple(c//2 for c in col))

    elif chart_type == "flow":
        n = min(len(items),4); fw = (w-30)//n
        colors3 = [ACCENT, ACCENT2, FEMALE_CLR, MALE_CLR]
        for i, label in enumerate(items[:n]):
            bx = x+15+i*fw; by2 = y+h//2-38; col = colors3[i%4]
            for pad in range(5,0,-1):
                gc = tuple(clamp(c*0.2) for c in col)
                draw.rounded_rectangle([bx-pad,by2-pad,bx+fw-22+pad,by2+76+pad], radius=10+pad, fill=gc)
            draw.rounded_rectangle([bx,by2,bx+fw-22,by2+76], radius=10, fill=GLASS_BG, outline=col, width=2)
            lw2, lh2 = tw(draw, label, fb)
            draw.text((bx+(fw-22)//2-lw2//2, by2+38-lh2//2), label, font=fb, fill=col)
            if i<n-1:
                ax = bx+fw-8
                draw.polygon([(ax,by2+38-14),(ax+18,by2+38),(ax,by2+38+14)], fill=col)

# ── 玻璃卡片 ─────────────────────────────────────────────────────────────────
def draw_glass_cards(draw, cards, x, y, w, h, bold_path, reg_path):
    n = len(cards[:3]); ch = (h-(n-1)*12)//n
    colors = [ACCENT, ACCENT2, FEMALE_CLR]
    fb = ImageFont.truetype(bold_path, 26); fr = ImageFont.truetype(reg_path, 24)
    for i, card in enumerate(cards[:n]):
        cy2 = y+i*(ch+12); col = colors[i%3]
        for pad in range(5,0,-1):
            gc = tuple(clamp(c*0.18*(1-pad/5)) for c in col)
            draw.rounded_rectangle([x-pad,cy2-pad,x+w+pad,cy2+ch+pad], radius=16+pad, fill=gc)
        draw.rounded_rectangle([x,cy2,x+w,cy2+ch], radius=14, fill=GLASS_BG)
        draw.rounded_rectangle([x,cy2,x+w,cy2+5], radius=3, fill=col)
        draw.ellipse([x+13,cy2+17,x+25,cy2+29], fill=col)
        draw.text((x+33,cy2+12), card["label"], font=fb, fill=col)
        draw.rectangle([x+14,cy2+48,x+w-14,cy2+50], fill=GLASS_EDGE)
        lines = wrap_text(draw, card["text"], fr, w-32)[:3]
        ty2 = cy2+58
        for line in lines:
            draw.text((x+14,ty2), line, font=fr, fill=TEXT1); ty2+=32

# ── 完整影格建立 ──────────────────────────────────────────────────────────────
def build_frame(slide, dialogue_text, speaker, anim_phase,
                bold_path, reg_path, out_path):
    """
    anim_phase: 0.0~1.0，控制呼吸動畫相位
    """
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # 全域背景光暈
    radial_glow(draw, img, AVATAR_W//2, H//2, 500, FEMALE_CLR if speaker=="Host1" else MALE_CLR, 0.1)
    radial_glow(draw, img, AVATAR_W//2+CONTENT_X, H//2, 400, ACCENT, 0.08)

    # 細網格
    for gx2 in range(0,W,80):
        draw.line([gx2,0,gx2,H], fill=(12,18,36))
    for gy2 in range(0,H,80):
        draw.line([0,gy2,W,gy2], fill=(12,18,36))

    # ── 頂部品牌欄 ────────────────────────────────────────────────────────
    draw.rectangle([0,0,W,55], fill=(7,10,22))
    glow_line(draw, 0,55, W,55, ACCENT, w=2, gw=10)
    fb_hd = ImageFont.truetype(bold_path, 24)
    fr_hd = ImageFont.truetype(reg_path,  22)
    draw.text((44,14), "欣晨工業有限公司", font=fb_hd, fill=TEXT1)
    draw.text((296,16), "智慧製造深度對談  SMART MANUFACTURING DEEP DIVE",
              font=fr_hd, fill=TEXT2)
    sl_txt = f"SLIDE {slide['id']}"
    slw,_ = tw(draw, sl_txt, fr_hd)
    draw.text((W-slw-44,16), sl_txt, font=fr_hd, fill=TEXT3)

    # ── 左側：主持人頭像 ─────────────────────────────────────────────────
    glow_line(draw, AVATAR_W,55, AVATAR_W,H-168, GLASS_EDGE, w=1, gw=6)
    avatar_cx = AVATAR_W//2
    avatar_by = 330   # 人像基準Y（頭部中心偏移參考）

    if speaker == "Host1":
        draw_female(img, avatar_cx, avatar_by, True,  anim_phase)
        draw_male  (img, avatar_cx, avatar_by, False, 0.0)  # 另一人不顯示（節省空間）
    else:
        draw_male  (img, avatar_cx, avatar_by, True,  anim_phase)
        draw_female(img, avatar_cx, avatar_by, False, 0.0)

    # 主持人名字 + 角色（頭像下方）
    fb_nm = ImageFont.truetype(bold_path, 36)
    fr_ro = ImageFont.truetype(reg_path,  24)
    spk_name  = "小欣" if speaker=="Host1" else "阿晨"
    spk_role  = "女主持人" if speaker=="Host1" else "男主持人"
    spk_color = FEMALE_CLR if speaker=="Host1" else MALE_CLR
    nh = draw_cx(draw, spk_name, fb_nm, avatar_cx, H-228, spk_color)
    draw_cx(draw, spk_role, fr_ro, avatar_cx, H-228+nh+6, TEXT3)

    # ── 右側：投影片內容 ─────────────────────────────────────────────────
    CX  = CONTENT_X
    CW  = W - CX - 30
    fb_t = ImageFont.truetype(bold_path, 54)
    fr_s = ImageFont.truetype(reg_path,  26)

    # 投影片標題
    t_lines = wrap_text(draw, slide["title"], fb_t, CW-20)
    ty = 72
    for line in t_lines:
        draw.text((CX, ty), line, font=fb_t, fill=TEXT1)
        _,lh = tw(draw, line, fb_t)
        ty += lh+5

    # 標題底線
    glow_line(draw, CX, ty+10, CX+200, ty+10, ACCENT, w=2, gw=8)

    # 圖表（上半）
    chart_top = ty + 30
    chart_h   = 280
    draw_chart_right(img, draw, slide.get("chart_type","pillars"),
                     slide.get("chart_items",[]),
                     CX, chart_top, CW-20, chart_h, bold_path, reg_path)

    # 卡片（下半）
    cards_top = chart_top + chart_h + 10
    cards_h   = H - 168 - cards_top - 10
    draw_glass_cards(draw, slide.get("cards",[])[:3],
                     CX, cards_top, CW-20, cards_h, bold_path, reg_path)

    # ── 底部字幕欄 ────────────────────────────────────────────────────────
    sub_y = H - 165
    for gy3 in range(sub_y, H):
        t = (gy3-sub_y)/(H-sub_y)
        draw.line([0,gy3,W,gy3], fill=lerp(BG2, (3,5,12), t))
    glow_line(draw, 0,sub_y, W,sub_y, ACCENT, w=2, gw=12)

    if dialogue_text:
        fb_sub = ImageFont.truetype(reg_path, 40)
        # 即時字幕：強制一行，超過長度截斷
        text_1l = dialogue_text
        while len(text_1l) > 4:
            tw3, _ = tw(draw, text_1l, fb_sub)
            if tw3 <= W - 160:
                break
            text_1l = text_1l[:-2] + "..."
        # 居中顯示，背景藥丸
        tw3, th3 = tw(draw, text_1l, fb_sub)
        tx = (W - tw3) // 2
        ty3 = sub_y + (165 - th3) // 2
        px, py = 22, 10
        draw.rounded_rectangle(
            [tx-px, ty3-py, tx+tw3+px, ty3+th3+py],
            radius=12, fill=(15, 20, 45, 0)
        )
        draw.text((tx, ty3), text_1l, font=fb_sub, fill=TEXT1)

    img.save(out_path)

# ── 腳本生成 ─────────────────────────────────────────────────────────────────
def generate_script(ac_client):
    prompt = """你是欣晨工業 Podcast「智慧製造深度對談」製作人。
主持人：小欣（女，活潑好奇）、阿晨（男，資深工程師）
欣晨工業：台灣桃園，1975年，51年精密製造，TPS核心哲學。

今集：豐田改善文化（Kaizen）在台灣製造業的實踐

請輸出：
=== SLIDES ===
[{"id":1,"title":"標題（10字）","chart_type":"pillars",
  "chart_items":["改善","JIT","自働化"],
  "cards":[{"label":"現象","text":"40字以內"},{"label":"原因","text":"40字"},{"label":"重點","text":"40字"}],
  "dialogue_count":5}]
chart_type: pillars/cycle/bars/stats/flow，共4-5個投影片

=== DIALOGUE ===
小欣: （60-80字）
阿晨: （60-80字）
共18-22輪，繁體中文，直接輸出不要說明"""

    print("Claude Sonnet 生成腳本...")
    msg = ac_client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4000,
        messages=[{"role":"user","content":prompt}]
    )
    raw = msg.content[0].text.strip()
    slides, dialogue = [], []

    if "=== SLIDES ===" in raw and "=== DIALOGUE ===" in raw:
        p2 = raw.split("=== DIALOGUE ===")
        sp = p2[0].split("=== SLIDES ===")[1].strip()
        dp = p2[1].strip()
        try:
            j1=sp.index("["); j2=sp.rindex("]")+1
            slides = json.loads(sp[j1:j2])
        except:
            slides = default_slides()
        for line in dp.split("\n"):
            for pfx,sp2 in [("小欣:","Host1"),("小欣：","Host1"),("阿晨:","Host2"),("阿晨：","Host2")]:
                if line.strip().startswith(pfx):
                    t=line.strip()[len(pfx):].strip()
                    if t: dialogue.append({"speaker":sp2,"text":t}); break
    else:
        slides = default_slides()
        for line in raw.split("\n"):
            for pfx,sp2 in [("小欣:","Host1"),("小欣：","Host1"),("阿晨:","Host2"),("阿晨：","Host2")]:
                if line.strip().startswith(pfx):
                    t=line.strip()[len(pfx):].strip()
                    if t: dialogue.append({"speaker":sp2,"text":t}); break

    if not dialogue: raise ValueError("無法解析對話")

    seg_map, si, cnt = {}, 0, 0
    for i in range(len(dialogue)):
        seg_map[i] = min(si, len(slides)-1)
        cnt += 1
        if si<len(slides) and cnt>=slides[si].get("dialogue_count",5):
            si=min(si+1,len(slides)-1); cnt=0

    print(f"腳本完成：{len(slides)} 張投影片，{len(dialogue)} 輪對話")
    return slides, dialogue, seg_map

def default_slides():
    return [
        {"id":1,"title":"什麼是 Kaizen 改善？","chart_type":"pillars",
         "chart_items":["改善","JIT","自働化"],
         "cards":[{"label":"定義","text":"Kaizen 意為持續改善，每天進步一點點，積累出卓越製造成果。"},
                  {"label":"七大浪費","text":"過量生產、等待、運輸、庫存、動作、加工過度、不良品。"},
                  {"label":"精神","text":"沒有最好，只有更好。每個問題都是改善機會，而非災難。"}],
         "dialogue_count":5},
        {"id":2,"title":"TPS 豐田生產系統","chart_type":"cycle",
         "chart_items":["Plan","Do","Check","Act"],
         "cards":[{"label":"即時生產 JIT","text":"正確時間、數量、品項——消除庫存浪費，讓生產線暢流。"},
                  {"label":"自働化 Jidoka","text":"設備自動偵測異常並停機，品質問題不流入下一工序。"},
                  {"label":"現地現物","text":"親自到現場確認，不信二手報告，用眼睛和雙手理解問題。"}],
         "dialogue_count":5},
        {"id":3,"title":"台灣工廠導入 Kaizen","chart_type":"bars",
         "chart_items":["換線時間","不良率","庫存天數","設備稼動"],
         "cards":[{"label":"SMED 快速換模","text":"換線時間從2小時縮至30分鐘，生產彈性提升3倍。"},
                  {"label":"Poka-yoke 防呆","text":"機構設計源頭杜絕人為錯誤，實現零缺陷生產目標。"},
                  {"label":"5S 視覺管理","text":"整理整頓清掃清潔素養，異常30秒內被一眼看出。"}],
         "dialogue_count":5},
        {"id":4,"title":"欣晨工業的實踐","chart_type":"stats",
         "chart_items":["51年","1975","桃園"],
         "cards":[{"label":"現地現物落實","text":"每個專案前，欣晨工程師必定親赴客戶廠房現場勘察。"},
                  {"label":"持續改善文化","text":"從設計圖面到現場調機，永遠問：這裡還能更好嗎？"},
                  {"label":"聯絡欣晨工業","text":"桃園市大園區，電話 03-381-4497，hsinchan.com"}],
         "dialogue_count":5},
    ]

# ── TTS ───────────────────────────────────────────────────────────────────────
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
        out   = tmp/f"seg_{i:03d}.mp3"
        resp  = oai.audio.speech.create(model="tts-1", voice=voice,
                                        input=turn["text"], speed=0.95)
        resp.stream_to_file(str(out))
        dur = audio_duration(out)
        segments.append({"path":str(out),"speaker":turn["speaker"],
                          "text":turn["text"],"duration":dur})
        if (i+1)%5==0: print(f"   {i+1}/{len(dialogue)} 段完成")
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
        for s in segments: f.write(f"file '{s['path']}'\nfile '{silence}'\n")
    full = tmp/"full_audio.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(full)],
                   capture_output=True, check=True)
    total = sum(s["duration"]+SILENCE_SEC for s in segments)
    print(f"音訊完成：{total/60:.1f} 分鐘")
    return str(full), total

# ── 影片合成（動畫幀 + 投影片切換淡入）──────────────────────────────────────
def render_video(slides, seg_map, segments, bold_path, reg_path,
                 audio_path, total_dur, tmp_dir, out_path):
    tmp = Path(tmp_dir)
    n_total = len(segments)
    print(f"建立 {n_total * ANIM_FRAMES} 個動畫影格...")

    concat_lines = []
    prev_slide   = -1

    for i, seg in enumerate(segments):
        slide_idx = seg_map.get(i, len(slides)-1)
        slide     = slides[slide_idx]
        dur       = seg["duration"] + SILENCE_SEC
        frame_dur = dur / ANIM_FRAMES

        # 投影片切換：插入 0.25s 淡黑過場
        if slide_idx != prev_slide and prev_slide >= 0:
            blk = tmp / f"black_{i:03d}.png"
            Image.new("RGB", (W, H), (2,3,8)).save(blk)
            concat_lines.append(f"file '{blk}'\nduration 0.25")

        # ANIM_FRAMES 個動畫幀
        for af in range(ANIM_FRAMES):
            anim_phase = af / ANIM_FRAMES   # 0.0, 0.25, 0.5, 0.75
            frame = tmp / f"frame_{i:03d}_{af}.png"
            build_frame(slide, seg["text"], seg["speaker"], anim_phase,
                        bold_path, reg_path, frame)
            concat_lines.append(f"file '{frame}'\nduration {frame_dur:.3f}")

        prev_slide = slide_idx
        if (i+1) % 5 == 0:
            print(f"   {i+1}/{n_total} 段完成")

    # 最後一幀重複
    last = tmp / f"frame_{n_total-1:03d}_{ANIM_FRAMES-1}.png"
    concat_lines.append(f"file '{last}'")
    concat_f = tmp/"frames.txt"
    concat_f.write_text("\n".join(concat_lines))

    print("FFmpeg 合成影片...")
    silent = tmp/"silent.mp4"
    r1 = subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_f),
        "-vf","fps=24,scale=1920:1080",
        "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",str(silent)
    ], capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(f"FFmpeg 靜音影片：{r1.stderr[-500:]}")

    # 加音訊（不加波形）
    r2 = subprocess.run([
        "ffmpeg","-y","-i",str(silent),"-i",str(audio_path),
        "-map","0:v","-map","1:a",
        "-c:v","libx264","-preset","fast","-crf","22",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-t",str(total_dur),str(out_path)
    ], capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(f"FFmpeg 最終合成：{r2.stderr[-500:]}")

    size = Path(out_path).stat().st_size/1024/1024
    print(f"影片完成：{size:.0f} MB，{total_dur/60:.1f} 分鐘")

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    print("="*60)
    print("  欣晨工業 Podcast — 半身主持人 + 動畫 + 投影片")
    print("  小欣 (nova) x 阿晨 (onyx) | OpenAI TTS")
    print("="*60+"\n")

    tw2  = datetime.now(timezone(timedelta(hours=8)))
    date = tw2.strftime("%Y-%m-%d")
    ac   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        slides, dialogue, seg_map = generate_script(ac)
        bold_path, reg_path = load_fonts()
        segments  = generate_all_audio(dialogue, tmpdir)
        audio_path, total_dur = concat_full_audio(segments, tmpdir)
        video_out = Path(tmpdir)/f"test_podcast_{date}.mp4"
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
