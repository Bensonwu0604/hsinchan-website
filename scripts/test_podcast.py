#!/usr/bin/env python3
# trigger: 2026-05-20r
"""
欣晨工業 Podcast — 投影片式影片
左側：主題視覺圖表（Pillow 繪製）
右側：三張重點卡片
底部：即時字幕 + 音波
OpenAI TTS: nova（小欣）x onyx（阿晨）
"""

import os, sys, json, subprocess, tempfile, shutil, math
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# ── 版面常數 ─────────────────────────────────────────────────────────────────
W, H         = 1920, 1080
BG           = (248, 246, 240)    # 米白背景（像 NotebookLM）
DARK_BLUE    = (18,  45,  90)     # 深藍文字
MID_BLUE     = (38,  90, 160)     # 中藍
ACCENT       = (26,  63, 152)     # 欣晨藍
LIGHT_BLUE   = (220, 232, 248)    # 淺藍背景
FEMALE_CLR   = (130, 60, 220)     # 小欣 — 紫
MALE_CLR     = (0,  150, 140)     # 阿晨 — 青
CARD_BG      = (255, 255, 255)    # 卡片白底
CARD_BORDER  = (200, 210, 225)    # 卡片邊框
TEXT_MAIN    = (25,  35,  60)     # 主文字
TEXT_GRAY    = (100, 115, 140)    # 灰文字
SUB_BG       = (18,  25,  50)     # 底部字幕背景

VOICE_FEMALE = "nova"
VOICE_MALE   = "onyx"
SILENCE_SEC  = 0.40

SPLIT_X = 1050   # 左右分隔線

# ── 字型 ─────────────────────────────────────────────────────────────────────
def load_fonts():
    bold_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    ]
    reg_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ]
    bold = next((p for p in bold_paths if Path(p).exists()), None)
    reg  = next((p for p in reg_paths  if Path(p).exists()), None)
    if not bold:
        raise FileNotFoundError("找不到 CJK 字型，請安裝 fonts-noto-cjk")
    return bold, reg or bold

# ── 腳本生成（包含投影片結構）────────────────────────────────────────────────
def generate_script(ac_client):
    prompt = """你是欣晨工業 Podcast「智慧製造深度對談」製作人。
主持人：
- 小欣（女）：活潑好奇，善於提問
- 阿晨（男）：資深工程師，深入解說

今集主題：豐田改善文化（Kaizen）在台灣製造業的實踐

欣晨工業：台灣桃園，1975年創立，51年精密製造，TPS核心哲學。

請輸出兩部分：

=== SLIDES ===
(JSON陣列，每個投影片對應2-4輪對話)
[
  {
    "id": 1,
    "title": "投影片主標題（10字以內）",
    "chart_type": "pillars",
    "chart_items": ["改善","JIT","自働化"],
    "cards": [
      {"label": "現象", "text": "說明文字（40字以內）"},
      {"label": "原因", "text": "說明文字（40字以內）"},
      {"label": "重點", "text": "說明文字（40字以內）"}
    ],
    "dialogue_count": 4
  }
]
chart_type 選項：pillars（柱子）/ cycle（循環）/ bars（橫條）/ stats（數字）/ flow（流程）

=== DIALOGUE ===
小欣: 說話內容（60-80字）
阿晨: 說話內容（60-80字）
（共 18-22 輪）

要求：投影片 4-5 個，對話繁體中文，自然口語，不要其他說明"""

    print("Claude Sonnet 生成腳本與投影片...")
    msg = ac_client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()

    # 分割 SLIDES 和 DIALOGUE
    slides, dialogue = [], []
    if "=== SLIDES ===" in raw and "=== DIALOGUE ===" in raw:
        parts    = raw.split("=== DIALOGUE ===")
        slide_part = parts[0].split("=== SLIDES ===")[1].strip()
        dial_part  = parts[1].strip()

        # 解析 slides JSON
        try:
            j_start = slide_part.index("[")
            j_end   = slide_part.rindex("]") + 1
            slides  = json.loads(slide_part[j_start:j_end])
        except Exception as e:
            print(f"Slides JSON 解析失敗：{e}，使用預設投影片")
            slides = default_slides()

        # 解析對話
        for line in dial_part.split("\n"):
            line = line.strip()
            for prefix, sp in [("小欣:", "Host1"), ("小欣：", "Host1"),
                                ("阿晨:", "Host2"), ("阿晨：", "Host2")]:
                if line.startswith(prefix):
                    text = line[len(prefix):].strip()
                    if text:
                        dialogue.append({"speaker": sp, "text": text})
                    break
    else:
        print("格式不符，使用預設投影片 + 解析對話")
        slides = default_slides()
        for line in raw.split("\n"):
            line = line.strip()
            for prefix, sp in [("小欣:", "Host1"), ("小欣：", "Host1"),
                                ("阿晨:", "Host2"), ("阿晨：", "Host2")]:
                if line.startswith(prefix):
                    text = line[len(prefix):].strip()
                    if text:
                        dialogue.append({"speaker": sp, "text": text})
                    break

    if not dialogue:
        raise ValueError("無法解析對話，請檢查腳本格式")

    # 建立 dialogue_index → slide_id 對應
    seg_map, slide_idx, count = {}, 0, 0
    for i in range(len(dialogue)):
        if slide_idx < len(slides):
            seg_map[i] = slide_idx
            count += 1
            if count >= slides[slide_idx].get("dialogue_count", 4):
                slide_idx = min(slide_idx + 1, len(slides) - 1)
                count = 0
        else:
            seg_map[i] = len(slides) - 1

    print(f"腳本完成：{len(slides)} 張投影片，{len(dialogue)} 輪對話")
    return slides, dialogue, seg_map

def default_slides():
    return [
        {"id": 1, "title": "什麼是改善？",
         "chart_type": "pillars",
         "chart_items": ["改善", "JIT", "自働化"],
         "cards": [
             {"label": "定義", "text": "Kaizen 日文意思是「持續改善」，每天進步一點點的積累。"},
             {"label": "核心", "text": "消除七大浪費：過量生產、等待、運輸、庫存、動作、加工、不良品。"},
             {"label": "精神", "text": "沒有最好，只有更好。每個問題都是改善的機會。"}
         ], "dialogue_count": 5},
        {"id": 2, "title": "TPS 三大支柱",
         "chart_type": "cycle",
         "chart_items": ["Plan", "Do", "Check", "Act"],
         "cards": [
             {"label": "即時生產", "text": "JIT：在正確時間、以正確數量、交付正確品項。"},
             {"label": "自働化", "text": "設備自動偵測異常並停機，問題不流入下一工序。"},
             {"label": "現地現物", "text": "親自到現場確認，不信二手報告。"}
         ], "dialogue_count": 5},
        {"id": 3, "title": "台灣工廠實踐",
         "chart_type": "bars",
         "chart_items": ["換線時間", "不良率", "庫存天數", "設備效率"],
         "cards": [
             {"label": "SMED", "text": "快速換模：把換線時間從2小時縮短到30分鐘以內。"},
             {"label": "Poka-yoke", "text": "防呆設計：從機構上杜絕人為錯誤，零缺陷生產。"},
             {"label": "5S", "text": "整理整頓清掃清潔素養：讓異常在30秒內被一眼看出。"}
         ], "dialogue_count": 5},
        {"id": 4, "title": "欣晨的實踐",
         "chart_type": "stats",
         "chart_items": ["51", "1975", "03-381-4497"],
         "cards": [
             {"label": "現地現物", "text": "每個專案啟動前，工程師必定親赴客戶廠房勘察。"},
             {"label": "持續改善", "text": "從設計圖面到現場調機，永遠問：這裡還能更好嗎？"},
             {"label": "聯絡我們", "text": "桃園市大園區，歡迎洽詢自動化解決方案。"}
         ], "dialogue_count": 5},
    ]

# ── OpenAI TTS ────────────────────────────────────────────────────────────────
def audio_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True
    )
    return float(json.loads(r.stdout)["format"]["duration"])

def generate_all_audio(dialogue, tmp_dir):
    oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    tmp = Path(tmp_dir)
    print(f"OpenAI TTS 生成 {len(dialogue)} 段音訊...")
    segments = []
    for i, turn in enumerate(dialogue):
        voice = VOICE_FEMALE if turn["speaker"] == "Host1" else VOICE_MALE
        out   = tmp / f"seg_{i:03d}.mp3"
        resp  = oai.audio.speech.create(
            model="tts-1", voice=voice, input=turn["text"], speed=0.95
        )
        resp.stream_to_file(str(out))
        dur = audio_duration(out)
        segments.append({
            "path": str(out), "speaker": turn["speaker"],
            "text": turn["text"], "duration": dur
        })
        if (i + 1) % 5 == 0:
            print(f"   {i+1}/{len(dialogue)} 段完成")
    print("TTS 完成")
    return segments

def concat_full_audio(segments, tmp_dir):
    tmp = Path(tmp_dir)
    silence = tmp / "silence.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", str(SILENCE_SEC), "-q:a", "9", "-acodec", "libmp3lame", str(silence)],
        capture_output=True, check=True
    )
    lst = tmp / "audio_list.txt"
    with open(lst, "w") as f:
        for seg in segments:
            f.write(f"file '{seg['path']}'\n")
            f.write(f"file '{silence}'\n")
    full = tmp / "full_audio.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(full)],
        capture_output=True, check=True
    )
    total = sum(s["duration"] + SILENCE_SEC for s in segments)
    print(f"音訊完成：{total/60:.1f} 分鐘")
    return str(full), total

# ── 視覺繪製 ─────────────────────────────────────────────────────────────────

def txt_w(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2]-bb[0], bb[3]-bb[1]

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

def draw_chart(draw, chart_type, chart_items, x, y, w, h):
    """依照 chart_type 繪製對應圖表"""
    if chart_type == "pillars":
        # TPS 三柱子圖
        n   = min(len(chart_items), 4)
        cw  = (w - 40) // n
        col = [ACCENT, (60,120,200), (0,140,130), (160,80,200)]
        for i, label in enumerate(chart_items[:n]):
            bx = x + 20 + i * cw
            ph = h // 2 + (i % 2) * (h // 6)
            draw.rectangle([bx+20, y+h-ph, bx+cw-20, y+h], fill=col[i % len(col)])
            draw.rectangle([bx+20, y+h-ph, bx+cw-20, y+h-ph+6], fill=(*col[i % len(col)][:3],))
            # 標籤
            f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 28)
            lw, lh = txt_w(draw, label, f)
            draw.text((bx+cw//2-lw//2, y+h+10), label, font=f, fill=DARK_BLUE)

    elif chart_type == "cycle":
        # PDCA 循環圖
        cx2, cy2 = x + w//2, y + h//2
        r = min(w, h)//2 - 30
        colors = [ACCENT, (0,140,130), (200,80,50), (160,80,200)]
        for i, label in enumerate(chart_items[:4]):
            angle = math.radians(i * 90 - 45)
            ex = cx2 + int(r * math.cos(angle))
            ey = cy2 + int(r * math.sin(angle))
            cr = 55
            col = colors[i % len(colors)]
            draw.ellipse([ex-cr, ey-cr, ex+cr, ey+cr], fill=col)
            f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 26)
            lw, lh = txt_w(draw, label, f)
            draw.text((ex-lw//2, ey-lh//2), label, font=f, fill=(255,255,255))
        # 中心圓
        draw.ellipse([cx2-40, cy2-40, cx2+40, cy2+40], fill=LIGHT_BLUE, outline=ACCENT, width=3)
        f2 = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 22)
        draw.text((cx2-22, cy2-12), "PDCA", font=f2, fill=ACCENT)

    elif chart_type == "bars":
        # 橫條圖（改善前後對比）
        n  = min(len(chart_items), 4)
        bh = (h - 40) // n
        vals_before = [100, 85, 90, 75]
        vals_after  = [45, 30, 55, 90]
        for i, label in enumerate(chart_items[:n]):
            by = y + 20 + i * bh
            # 背景條
            draw.rectangle([x+160, by+8, x+w, by+bh-12], fill=(230,235,245))
            # 改善前（淡）
            bw_b = int((w-160) * vals_before[i] / 100)
            draw.rectangle([x+160, by+8, x+160+bw_b, by+bh//2-2], fill=(180,200,230))
            # 改善後（深）
            bw_a = int((w-160) * vals_after[i] / 100)
            draw.rectangle([x+160, by+bh//2+2, x+160+bw_a, by+bh-12], fill=ACCENT)
            # 標籤
            f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 26)
            draw.text((x+8, by+bh//2-14), label, font=f, fill=DARK_BLUE)

    elif chart_type == "stats":
        # 大數字展示
        n = min(len(chart_items), 3)
        sw = w // n
        colors = [ACCENT, MID_BLUE, (0,140,130)]
        for i, val in enumerate(chart_items[:n]):
            sx = x + i * sw + sw//2
            sy = y + h//2
            f_big = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 70)
            f_sml = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 26)
            vw, vh = txt_w(draw, val, f_big)
            draw.text((sx-vw//2, sy-vh//2-10), val, font=f_big, fill=colors[i % len(colors)])

    elif chart_type == "flow":
        # 流程箭頭
        n  = min(len(chart_items), 4)
        fw = (w - 40) // n
        col = [ACCENT, (0,140,130), MID_BLUE, (160,80,200)]
        for i, label in enumerate(chart_items[:n]):
            bx = x + 20 + i * fw
            by = y + h//2 - 40
            draw.rounded_rectangle([bx, by, bx+fw-30, by+80], radius=10, fill=col[i % len(col)])
            f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 28)
            lw, lh = txt_w(draw, label, f)
            draw.text((bx+(fw-30)//2-lw//2, by+40-lh//2), label, font=f, fill=(255,255,255))
            if i < n - 1:
                ax = bx + fw - 15
                ay = by + 40
                draw.polygon([(ax, ay-16), (ax+22, ay), (ax, ay+16)], fill=(150,165,185))

def draw_info_cards(draw, cards, x, y, w, h, bold_path, reg_path):
    """右側三張資訊卡片"""
    n   = len(cards)
    ch  = (h - (n-1)*16) // n
    col = [ACCENT, MID_BLUE, (0,140,130)]
    f_label = ImageFont.truetype(bold_path, 30)
    f_text  = ImageFont.truetype(reg_path,  28)

    for i, card in enumerate(cards):
        cy = y + i * (ch + 16)
        # 白色卡片
        draw.rounded_rectangle([x, cy, x+w, cy+ch], radius=12,
                                fill=CARD_BG, outline=CARD_BORDER, width=1)
        # 上邊色條
        draw.rounded_rectangle([x, cy, x+w, cy+5], radius=3, fill=col[i % len(col)])
        # 標籤
        draw.text((x+18, cy+16), card["label"], font=f_label, fill=col[i % len(col)])
        # 文字換行
        card_text_w = w - 36
        lines = wrap_text(draw, card["text"], f_text, card_text_w)[:3]
        ty = cy + 56
        for line in lines:
            draw.text((x+18, ty), line, font=f_text, fill=TEXT_MAIN)
            ty += 36

def build_frame(slide, dialogue_text, speaker, bold_path, reg_path, out_path):
    """建立完整投影片影格"""
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── 頂部品牌欄 ────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 62], fill=DARK_BLUE)
    f_brand = ImageFont.truetype(bold_path, 26)
    f_ep    = ImageFont.truetype(reg_path,  24)
    draw.text((44, 17), "欣晨工業有限公司", font=f_brand, fill=(255,255,255))
    draw.text((320, 19), "智慧製造深度對談  SMART MANUFACTURING DEEP DIVE",
              font=f_ep, fill=(160,185,220))
    slide_label = f"Slide {slide['id']}"
    sl_w, _ = txt_w(draw, slide_label, f_ep)
    draw.text((W-sl_w-44, 19), slide_label, font=f_ep, fill=(120,150,190))

    # ── 左欄：標題 + 圖表 ────────────────────────────────────────────────
    f_title = ImageFont.truetype(bold_path, 58)
    LPAD = 50
    # 標題
    lines_t = wrap_text(draw, slide["title"], f_title, SPLIT_X - LPAD - 40)
    ty = 90
    for line in lines_t:
        draw.text((LPAD, ty), line, font=f_title, fill=DARK_BLUE)
        ty += draw.textbbox((0,0), line, font=f_title)[3] + 6

    # 分隔線
    draw.rectangle([LPAD, ty+10, SPLIT_X-30, ty+13], fill=ACCENT)

    # 圖表區域
    chart_y = ty + 30
    chart_h = H - 180 - chart_y
    draw_chart(draw, slide.get("chart_type", "pillars"),
               slide.get("chart_items", []), LPAD, chart_y,
               SPLIT_X - LPAD - 30, chart_h)

    # ── 中間垂直分隔線 ────────────────────────────────────────────────────
    draw.rectangle([SPLIT_X, 62, SPLIT_X+2, H-170], fill=CARD_BORDER)

    # ── 右欄：資訊卡片 ────────────────────────────────────────────────────
    RPAD  = 36
    RX    = SPLIT_X + RPAD
    RAREA = W - SPLIT_X - RPAD*2
    draw_info_cards(draw, slide.get("cards", [])[:3],
                    RX, 80, RAREA, H - 80 - 175, bold_path, reg_path)

    # ── 底部字幕欄 ────────────────────────────────────────────────────────
    sub_y = H - 165
    draw.rectangle([0, sub_y, W, H-3], fill=SUB_BG)
    draw.rectangle([0, sub_y, W, sub_y+3], fill=ACCENT)

    if dialogue_text:
        spk_color = FEMALE_CLR if speaker == "Host1" else MALE_CLR
        spk_name  = "小欣" if speaker == "Host1" else "阿晨"
        f_spk     = ImageFont.truetype(bold_path, 28)
        f_sub     = ImageFont.truetype(reg_path,  36)

        draw.text((44, sub_y + 14), spk_name, font=f_spk, fill=spk_color)

        sub_lines = wrap_text(draw, dialogue_text, f_sub, W - 180)[:2]
        sty = sub_y + 52
        for line in sub_lines:
            draw.text((44, sty), line, font=f_sub, fill=(240, 244, 250))
            sty += 44

    # 波形預留
    draw.rectangle([0, H-3, W, H], fill=(10, 15, 35))

    img.save(out_path)

# ── 影片合成 ─────────────────────────────────────────────────────────────────
def render_video(slides, seg_map, segments, bold_path, reg_path,
                 audio_path, total_dur, tmp_dir, out_path):
    tmp = Path(tmp_dir)
    print(f"建立 {len(segments)} 個影格...")

    concat_lines = []
    for i, seg in enumerate(segments):
        slide_idx = seg_map.get(i, len(slides)-1)
        slide     = slides[slide_idx]
        frame     = tmp / f"frame_{i:03d}.png"
        build_frame(slide, seg["text"], seg["speaker"], bold_path, reg_path, frame)
        dur = seg["duration"] + SILENCE_SEC
        concat_lines.append(f"file '{frame}'\nduration {dur:.3f}")
        if (i+1) % 5 == 0:
            print(f"   {i+1}/{len(segments)} 影格完成")

    # 最後一幀重複
    last_frame = tmp / f"frame_{len(segments)-1:03d}.png"
    concat_lines.append(f"file '{last_frame}'")

    concat_f = tmp / "frames.txt"
    concat_f.write_text("\n".join(concat_lines))

    print("FFmpeg 合成影片...")
    # 圖片序列 → 靜音影片
    silent = tmp / "silent.mp4"
    r1 = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_f),
        "-vf", "fps=30,scale=1920:1080",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(silent)
    ], capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(f"FFmpeg 靜音影片失敗：{r1.stderr[-500:]}")

    # 加音訊 + 波形（底部165px）
    fc = (
        "[0:v]scale=1920:1080[bg];"
        "[1:a]showwaves=s=1920x162:mode=cline:rate=30"
        ":colors=1a3f98|5a8ce0[wave];"
        "[bg][wave]overlay=0:915[vout]"
    )
    r2 = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(silent), "-i", str(audio_path),
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(total_dur), "-r", "30",
        str(out_path)
    ], capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(f"FFmpeg 最終合成失敗：{r2.stderr[-500:]}")

    size = Path(out_path).stat().st_size / 1024 / 1024
    print(f"影片完成：{size:.0f} MB，{total_dur/60:.1f} 分鐘")

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  欣晨工業 Podcast — 投影片式影片（圖文並貌）")
    print("  小欣 (nova) x 阿晨 (onyx) | OpenAI TTS")
    print("=" * 60 + "\n")

    tw   = datetime.now(timezone(timedelta(hours=8)))
    date = tw.strftime("%Y-%m-%d")
    ac   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. 腳本 + 投影片
        slides, dialogue, seg_map = generate_script(ac)
        print(f"\n投影片：{len(slides)} 張  |  對話：{len(dialogue)} 輪\n")

        # 2. 字型
        bold_path, reg_path = load_fonts()

        # 3. TTS
        segments  = generate_all_audio(dialogue, tmpdir)
        audio_path, total_dur = concat_full_audio(segments, tmpdir)

        # 4. 影片
        video_out = Path(tmpdir) / f"test_podcast_{date}.mp4"
        render_video(slides, seg_map, segments, bold_path, reg_path,
                     audio_path, total_dur, tmpdir, video_out)

        # 5. 輸出
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
