#!/usr/bin/env python3
"""
欣晨工業 — NotebookLM 同款技術 Podcast 影片生成器
使用 Google Gemini 2.5 Flash TTS 多主持人語音合成
（這是 NotebookLM Deep Dive 底層使用的相同 Google 語音技術）

所需 API Keys：
  ANTHROPIC_API_KEY  — Claude Sonnet 生成對話腳本
  GOOGLE_API_KEY     — Gemini 2.5 Flash TTS 多人語音合成
"""

import os, json, base64, wave, subprocess, tempfile, asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
import requests
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

# ── 視覺常數 ────────────────────────────────────────────────────────────────
W, H       = 1920, 1080
BG         = (8,  12,  22)
SURFACE    = (14, 22,  42)
ACCENT     = (26, 63, 152)
ACCENT_LT  = (90, 140, 230)
FEMALE_CLR = (220, 80, 130)
MALE_CLR   = (50, 160, 220)
WHITE      = (240, 244, 248)
GRAY       = (120, 140, 168)
DARK       = (30, 40, 60)

# Gemini TTS 聲音 (NotebookLM 使用的相同聲音庫)
VOICE_FEMALE = "Zephyr"    # 自然女聲
VOICE_MALE   = "Puck"      # 自然男聲

# ── 題材 ─────────────────────────────────────────────────────────────────────
TOPICS = [
    ("改善文化 × 豐田哲學",   "Kaizen",    "Kaizen持續改善如何在台灣製造業落地：七大浪費消除、VSM價值流、Poka-yoke防呆設計。欣晨工業將TPS哲學落實在每個客戶專案。"),
    ("機械手臂整合實戰",      "機器人",    "FANUC、ABB、KUKA在台灣工廠的導入策略，第七軸線性走行軸、協作機器人安全整合、視覺引導定位的完整解決方案。"),
    ("AI視覺檢測的革命",      "AOI",       "深度學習如何讓AOI準確率突破99.5%？工業相機選型、打光設計、半導體與電子封裝瑕疵偵測的實際案例。"),
    ("數位雙生與預測維護",    "數位雙生",  "IoT感測器、OPC-UA、雲端儀表板——讓設備在虛擬世界說話，提前預測故障、減少停機30%的完整技術架構。"),
    ("台灣製造業的未來路",    "工業4.0",   "從工業3.5到4.0，台灣中小製造業的務實數位化路徑：先連結、再可視、再AI分析、最後自主優化。"),
    ("高溫工業耗材秘辛",      "高溫材料",  "碳化矽保護管為何能在1600°C的鋁液中撐過數百小時？石墨脫氣管的純度如何影響鑄件氣孔率？材料科學揭密。"),
    ("電動車製造的新機會",    "EV",        "電動車浪潮為台灣精密零件製造業帶來什麼？電池模組組裝自動化、電機鋁殼鑄造脫氣、JIT排程挑戰。"),
    ("半導體精密製程挑戰",    "半導體",    "台灣半導體供應鏈每個零件的精密要求，SiC保護管、夾治具精度、熱電偶溫控——每個微米都是競爭力。"),
    ("OEE從60%到85%的路",    "OEE",       "整體設備效率的三個分母：可用率、性能效率、良品率。如何透過Kaizen系統性地把OEE從台灣平均60%提升到世界級85%？"),
    ("精密量測的感動",        "量測",      "三次元量測機、雷射掃描、機器視覺量測——精密製造的品質根基。量測數據如何回饋製程，形成品質改善的飛輪。"),
]

# ── 字型 ─────────────────────────────────────────────────────────────────────
def load_fonts():
    bold_list = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    ]
    reg_list = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ]
    bold = next((p for p in bold_list if Path(p).exists()), None)
    reg  = next((p for p in reg_list  if Path(p).exists()), None)
    if not bold:
        raise FileNotFoundError("找不到 CJK 字型，請安裝 fonts-noto-cjk")
    return bold, reg or bold

# ── 腳本生成 ─────────────────────────────────────────────────────────────────
def generate_script(topic_title, topic_angle, ac_client):
    print("🤖 Claude Sonnet 生成對話腳本...")
    prompt = f"""你是欣晨工業有限公司的 Podcast 製作人，製作「智慧製造深度對談」節目。

主持人設定：
- 小欣（Host1，女）：活潑好奇，善於提問，代表觀眾視角，偶爾驚嘆
- 阿晨（Host2，男）：資深工程師背景，深入解說，善用數據和案例，語氣沉穩
名字取自「欣晨工業」，名字自然融入對話中。

今集主題：{topic_title}
角度：{topic_angle}

欣晨工業（自然融入2-3次，不硬推銷）：
台灣桃園，1975年創立，51年精密製造，豐田TPS哲學
產品：加熱器（1200°C）、熱電偶、碳化矽保護管、石墨脫氣管
服務：機械手臂整合（FANUC/ABB/KUKA）、AOI視覺檢測、數位雙生

請生成一集8-10分鐘深度對談，以以下格式輸出，每行一個對話：
Host1: （說話內容）
Host2: （說話內容）

要求：
- 共30-38輪對話
- 每輪70-100字，自然流暢口語，繁體中文
- 開場有互相問候感，結尾有溫暖收尾
- 包含具體數字、案例、反直覺的觀點
- 直接輸出對話內容，不要JSON，不要其他說明"""

    msg = ac_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()

    # 解析 "Host1: ..." / "Host2: ..." 格式
    dialogue = []
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("Host1:"):
            dialogue.append({"speaker": "Host1", "text": line[6:].strip()})
        elif line.startswith("Host2:"):
            dialogue.append({"speaker": "Host2", "text": line[6:].strip()})
        elif line.startswith("小欣:"):
            dialogue.append({"speaker": "Host1", "text": line[3:].strip()})
        elif line.startswith("阿晨:"):
            dialogue.append({"speaker": "Host2", "text": line[3:].strip()})

    total = sum(len(d["text"]) for d in dialogue)
    print(f"✅ 腳本完成：{len(dialogue)} 輪對話，{total} 字（預估 {total//150:.0f} 分鐘）")
    return dialogue

# ── Gemini TTS 多主持人語音合成 ──────────────────────────────────────────────
def format_script_for_gemini(dialogue):
    """將對話轉成 Gemini TTS 理解的格式"""
    lines = []
    for turn in dialogue:
        tag = "Host1" if turn["speaker"] == "Host1" else "Host2"
        lines.append(f"{tag}: {turn['text']}")
    return "\n".join(lines)

def generate_audio_gemini(script_text, out_wav, google_api_key, chunk_idx=0):
    """呼叫 Gemini 2.5 Flash TTS 生成多主持人音訊"""
    client = genai.Client(api_key=google_api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=script_text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Host1",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=VOICE_FEMALE
                                )
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Host2",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=VOICE_MALE
                                )
                            )
                        )
                    ]
                )
            )
        )
    )

    # 取得音訊資料（PCM 24kHz 16-bit mono）
    audio_part = response.candidates[0].content.parts[0]
    audio_bytes = base64.b64decode(audio_part.inline_data.data)

    # 存成 WAV
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # 16-bit
        wf.setframerate(24000)
        wf.writeframes(audio_bytes)

    size = Path(out_wav).stat().st_size / 1024
    print(f"✅ Gemini TTS 音訊生成：{size:.0f} KB")
    return str(out_wav)

def tts_with_chunks(dialogue, tmp_dir, google_api_key, chunk_size=18):
    """將對話分段生成（每段18輪），避免超過 token 上限"""
    tmp = Path(tmp_dir)
    wav_parts = []

    chunks = [dialogue[i:i+chunk_size] for i in range(0, len(dialogue), chunk_size)]
    print(f"🎙️  Gemini TTS 分 {len(chunks)} 段生成（每段 {chunk_size} 輪）...")

    for i, chunk in enumerate(chunks):
        print(f"   生成第 {i+1}/{len(chunks)} 段...")
        script_text = format_script_for_gemini(chunk)
        wav_out = tmp / f"chunk_{i:02d}.wav"
        generate_audio_gemini(script_text, wav_out, google_api_key, i)
        wav_parts.append(str(wav_out))

    # 合併所有 WAV → 單一 MP3
    concat_list = tmp / "wav_list.txt"
    with open(concat_list, "w") as f:
        for p in wav_parts:
            f.write(f"file '{p}'\n")

    full_mp3 = tmp / "podcast_audio.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list),
         "-codec:a", "libmp3lame", "-qscale:a", "2",
         str(full_mp3)],
        capture_output=True, check=True
    )

    # 取得時長
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(full_mp3)],
        capture_output=True, text=True
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    print(f"✅ 音訊合併完成：{duration/60:.1f} 分鐘")
    return str(full_mp3), duration

# ── 視覺背景（三欄式，文圖並貌）────────────────────────────────────────────

# 每個主題對應的圖形元素資訊
TOPIC_META = {
    "Kaizen":    {"icon": "kaizen",  "stat1": "七大浪費", "stat2": "VSM / 5S / SMED", "stat3": "Poka-yoke 防呆", "color": (60, 200, 120)},
    "機器人":    {"icon": "robot",   "stat1": "FANUC / ABB / KUKA", "stat2": "第七軸走行軸", "stat3": "視覺引導定位", "color": (80, 160, 240)},
    "AOI":       {"icon": "vision",  "stat1": "精度 ±0.01mm", "stat2": "CNN 深度學習", "stat3": "瑕疵率 < 0.5%", "color": (200, 160, 60)},
    "數位雙生":  {"icon": "twin",    "stat1": "IoT 即時感測", "stat2": "OPC-UA 通訊", "stat3": "停機減少 30%", "color": (100, 200, 220)},
    "工業4.0":   {"icon": "factory", "stat1": "連結 → 可視", "stat2": "AI 診斷 → 優化", "stat3": "工業 3.5 漸進路", "color": (160, 100, 240)},
    "高溫材料":  {"icon": "flame",   "stat1": "SiC > 1600°C", "stat2": "石墨純度 99.9%", "stat3": "耐熱衝擊設計", "color": (240, 120, 60)},
    "EV":        {"icon": "ev",      "stat1": "電池模組組裝", "stat2": "鋁殼鑄造脫氣", "stat3": "JIT 生產排程", "color": (60, 200, 160)},
    "半導體":    {"icon": "chip",    "stat1": "SiC 爐管保護", "stat2": "±0.01mm 精度", "stat3": "製程溫控 ±0.5°C", "color": (180, 80, 240)},
    "OEE":       {"icon": "gauge",   "stat1": "世界級目標 85%", "stat2": "台灣平均 60%", "stat3": "可用率×效率×良率", "color": (240, 200, 60)},
    "量測":      {"icon": "measure", "stat1": "CMM 三次元量測", "stat2": "雷射掃描儀", "stat3": "GD&T 幾何公差", "color": (60, 180, 200)},
}
DEFAULT_META = {"icon": "factory", "stat1": "智慧製造", "stat2": "51年製造經驗", "stat3": "豐田TPS哲學", "color": ACCENT_LT}

def draw_topic_icon(draw, cx, cy, icon_type, color, size=130):
    """繪製主題專屬幾何圖示"""
    s = size
    if icon_type == "kaizen":
        # 循環改善箭頭（三個弧段）
        for i, angle in enumerate([0, 120, 240]):
            import math
            a1 = math.radians(angle + 15)
            a2 = math.radians(angle + 95)
            pts = [(cx + int(s*0.7*math.cos(math.radians(a))) ,
                    cy + int(s*0.7*math.sin(math.radians(a)))) for a in range(angle+15, angle+95, 5)]
            if len(pts) > 1:
                draw.line(pts, fill=color, width=8)
        draw.ellipse([cx-18, cy-18, cx+18, cy+18], fill=color)
    elif icon_type == "robot":
        # 機械手臂輪廓
        draw.rectangle([cx-12, cy-s+20, cx+12, cy-s//2], fill=color)
        draw.rectangle([cx-s//2, cy-s//2-12, cx+12, cy-s//2+12], fill=color)
        draw.rectangle([cx-s//2, cy-12, cx-s//2+80, cy+12], fill=color)
        draw.ellipse([cx-s//2-18, cy-28, cx-s//2+18, cy+28], outline=color, width=6)
        draw.ellipse([cx-s+40, cy-14, cx-s+68, cy+14], fill=color)
    elif icon_type == "vision":
        # 相機鏡頭
        draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=color, width=5)
        draw.ellipse([cx-s//2, cy-s//2, cx+s//2, cy+s//2], outline=color, width=5)
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=color)
        draw.line([cx-s, cy, cx-s//2, cy], fill=color, width=4)
        draw.line([cx+s//2, cy, cx+s, cy], fill=color, width=4)
    elif icon_type == "twin":
        # 連結節點
        nodes = [(cx-90, cy-50), (cx+90, cy-50), (cx, cy+70), (cx-90, cy+30), (cx+90, cy+30)]
        for i, (x1, y1) in enumerate(nodes):
            for j, (x2, y2) in enumerate(nodes):
                if i < j:
                    draw.line([x1, y1, x2, y2], fill=(*color[:3], 80), width=2)
        for x, y in nodes:
            draw.ellipse([x-12, y-12, x+12, y+12], fill=color)
    elif icon_type == "flame":
        # 高溫火焰符號
        import math
        pts = []
        for a in range(0, 360, 8):
            r = s * (0.7 + 0.3 * abs(math.sin(math.radians(a * 3))))
            pts.append((cx + int(r * math.cos(math.radians(a))),
                        cy + int(r * math.sin(math.radians(a)))))
        if pts:
            draw.polygon(pts, outline=color, fill=(*color[:3], 40))
        draw.ellipse([cx-30, cy-30, cx+30, cy+30], fill=color)
    elif icon_type == "chip":
        # 晶片
        draw.rectangle([cx-s//2, cy-s//2, cx+s//2, cy+s//2], outline=color, width=6)
        draw.rectangle([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=color)
        for i in range(4):
            y_off = -s//3 + i * s//4
            draw.line([cx-s//2, cy+y_off, cx-s, cy+y_off], fill=color, width=4)
            draw.line([cx+s//2, cy+y_off, cx+s, cy+y_off], fill=color, width=4)
    elif icon_type == "gauge":
        # 儀表板
        import math
        for a in range(220, -41, -10):
            ra = math.radians(a)
            x1 = cx + int(s*0.75 * math.cos(ra))
            y1 = cy + int(s*0.75 * math.sin(ra))
            x2 = cx + int(s * math.cos(ra))
            y2 = cy + int(s * math.sin(ra))
            draw.line([x1, y1, x2, y2], fill=color, width=3)
        # 指針
        needle_a = math.radians(160)
        draw.line([cx, cy, cx + int(s*0.65*math.cos(needle_a)),
                   cy + int(s*0.65*math.sin(needle_a))], fill=(240, 80, 60), width=6)
        draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=WHITE)
    elif icon_type == "ev":
        # 電動車輪廓
        draw.rounded_rectangle([cx-s, cy-s//3, cx+s, cy+s//3], radius=20, outline=color, width=5)
        draw.ellipse([cx-s+20, cy+s//3-20, cx-s+70, cy+s//3+20], fill=color)
        draw.ellipse([cx+s-70, cy+s//3-20, cx+s-20, cy+s//3+20], fill=color)
        draw.line([cx-40, cy-s//3, cx-40, cy], fill=color, width=4)
        draw.line([cx+40, cy-s//3, cx+40, cy], fill=color, width=4)
        draw.rectangle([cx-20, cy-s//4, cx+20, cy+s//4], fill=color)
    elif icon_type == "measure":
        # 量測尺
        draw.rectangle([cx-s, cy-15, cx+s, cy+15], outline=color, width=4)
        for i in range(-10, 11):
            h = 20 if i % 5 == 0 else 10
            x = cx + i * (s // 10)
            draw.line([x, cy-h, x, cy+h], fill=color, width=2 if i % 5 == 0 else 1)
        draw.line([cx, cy-40, cx, cy-20], fill=(240, 80, 60), width=5)
    else:
        # factory — 工廠符號
        draw.rectangle([cx-s//2, cy-s//3, cx+s//2, cy+s//3], outline=color, width=5)
        draw.polygon([(cx-s//2-10, cy-s//3), (cx, cy-s*0.75), (cx+s//2+10, cy-s//3)], outline=color, width=5)
        draw.rectangle([cx-15, cy-s//3+20, cx+15, cy+s//3], fill=color)

def wrap_cjk(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if draw.textbbox((0,0), test, font=font)[2] > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = test
    if cur: lines.append(cur)
    return lines

def draw_info_card(draw, x, y, w, h, label, value, color, f_label, f_value):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=10, fill=(14, 24, 50))
    draw.rounded_rectangle([x, y, x+4, y+h], radius=2, fill=color)
    bb = draw.textbbox((0,0), label, font=f_label)
    draw.text((x+14, y+10), label, font=f_label, fill=GRAY)
    draw.text((x+14, y+32), value, font=f_value, fill=WHITE)

def draw_avatar_v2(draw, cx, cy, r, color, initial, role, name, f_big, f_role, f_name):
    # 外層發光環
    for ring in range(r+40, r+2, -3):
        t = 1 - (ring-r-2)/38
        c = tuple(min(255, int(v*t*0.5)) for v in color)
        draw.ellipse([cx-ring, cy-ring, cx+ring, cy+ring], outline=c)
    # 主圓（漸層模擬：多個同心橢圓）
    for dr in range(r, 0, -4):
        ratio = 1 - dr/r
        rc = tuple(min(255, int(c + (255-c)*ratio*0.15)) for c in color)
        draw.ellipse([cx-dr, cy-dr, cx+dr, cy+dr], fill=rc)
    # 首字
    bb = draw.textbbox((0,0), initial, font=f_big)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx-tw//2, cy-th//2-8), initial, font=f_big, fill=WHITE)
    # 角色標籤（badge 樣式）
    bb2 = draw.textbbox((0,0), role, font=f_role)
    rw = bb2[2]-bb2[0]+20
    rh = bb2[3]-bb2[1]+10
    draw.rounded_rectangle([cx-rw//2, cy+r+16, cx+rw//2, cy+r+16+rh], radius=6, fill=color)
    draw.text((cx-rw//2+10, cy+r+21), role, font=f_role, fill=WHITE)
    # 名稱
    bb3 = draw.textbbox((0,0), name, font=f_name)
    nw = bb3[2]-bb3[0]
    draw.text((cx-nw//2, cy+r+16+rh+8), name, font=f_name, fill=GRAY)

def create_bg_image(topic_title, bold_path, reg_path, out_path, topic_tag="factory"):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # ── 全版漸層底色 ──────────────────────────────────────────────
    for y in range(H):
        ratio = y / H
        r = int(BG[0] + (18-BG[0]) * ratio)
        g = int(BG[1] + (28-BG[1]) * ratio)
        b = int(BG[2] + (55-BG[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    meta = TOPIC_META.get(topic_tag, DEFAULT_META)
    icon_color = meta["color"]

    # ── 細格線（三欄分隔感）──────────────────────────────────────
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(22, 35, 65))
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(22, 35, 65))

    # ── 頂部品牌欄 ────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 64], fill=(8, 14, 28))
    draw.rectangle([0, 64, W, 70], fill=ACCENT)

    f_brand  = ImageFont.truetype(bold_path, 26)
    f_ep     = ImageFont.truetype(reg_path,  24)
    draw.text((44, 17), "欣晨工業有限公司", font=f_brand, fill=WHITE)
    ep_text = "智慧製造深度對談  ·  SMART MANUFACTURING DEEP DIVE"
    draw.text((320, 19), ep_text, font=f_ep, fill=GRAY)
    tech_text = "Powered by Google Gemini TTS  ×  Claude Sonnet"
    bb_t = draw.textbbox((0,0), tech_text, font=f_ep)
    draw.text((W - (bb_t[2]-bb_t[0]) - 44, 19), tech_text, font=f_ep, fill=ACCENT_LT)

    # ── 三欄分隔線 ────────────────────────────────────────────────
    COL1 = 560    # 左欄右邊界
    COL2 = 1360   # 中欄右邊界
    draw.rectangle([COL1, 70, COL1+2, H-172], fill=(30, 48, 90))
    draw.rectangle([COL2, 70, COL2+2, H-172], fill=(30, 48, 90))

    # ════════════════════════════════════════════════════
    # 左欄：主題插畫 + 關鍵數據
    # ════════════════════════════════════════════════════
    f_title_l = ImageFont.truetype(bold_path, 52)
    f_stat_l  = ImageFont.truetype(bold_path, 30)
    f_stat_v  = ImageFont.truetype(bold_path, 36)
    f_label_s = ImageFont.truetype(reg_path,  22)
    f_eyebrow = ImageFont.truetype(reg_path,  24)

    # 主題圖示（居中左欄）
    icon_cx = COL1 // 2
    draw_topic_icon(draw, icon_cx, 260, meta["icon"], icon_color, size=110)

    # 主題標題
    title_lines = wrap_cjk(draw, topic_title, f_title_l, COL1 - 60)
    ty = 410
    for line in title_lines:
        bb = draw.textbbox((0,0), line, font=f_title_l)
        lw = bb[2]-bb[0]
        draw.text((max(30, icon_cx - lw//2), ty), line, font=f_title_l, fill=WHITE)
        ty += (bb[3]-bb[1]) + 8

    # 三個數據卡片
    card_y = ty + 24
    for stat_text in [meta["stat1"], meta["stat2"], meta["stat3"]]:
        draw.rounded_rectangle([30, card_y, COL1-30, card_y+52], radius=8, fill=(14, 22, 46))
        draw.rounded_rectangle([30, card_y, 36, card_y+52], radius=4, fill=icon_color)
        draw.text((50, card_y+13), stat_text, font=f_stat_l, fill=WHITE)
        card_y += 64

    # ════════════════════════════════════════════════════
    # 中欄：雙主持人
    # ════════════════════════════════════════════════════
    f_init  = ImageFont.truetype(bold_path, 96)
    f_role  = ImageFont.truetype(bold_path, 28)
    f_name  = ImageFont.truetype(reg_path,  26)
    f_vs    = ImageFont.truetype(bold_path, 44)
    f_badge = ImageFont.truetype(reg_path,  22)

    mid_cx   = (COL1 + COL2) // 2
    host1_cx = COL1 + (COL2 - COL1) // 4
    host2_cx = COL1 + (COL2 - COL1) * 3 // 4
    host_cy  = 490

    draw_avatar_v2(draw, host1_cx, host_cy, 108, FEMALE_CLR,
                   "欣", "女主持人", "小欣", f_init, f_role, f_name)
    draw_avatar_v2(draw, host2_cx, host_cy, 108, MALE_CLR,
                   "晨", "男主持人", "阿晨", f_init, f_role, f_name)

    # VS 分隔
    bb_vs = draw.textbbox((0,0), "×", font=f_vs)
    draw.text((mid_cx - (bb_vs[2]-bb_vs[0])//2, host_cy - 22), "×", font=f_vs, fill=(40, 60, 100))

    # NotebookLM badge（中欄頂）
    badge_txt = "NotebookLM 同款 Google 語音技術"
    bb_b = draw.textbbox((0,0), badge_txt, font=f_badge)
    bw = bb_b[2]-bb_b[0]+28
    bh = bb_b[3]-bb_b[1]+14
    bx = mid_cx - bw//2
    by = 88
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=8, fill=(20, 36, 80))
    draw.rounded_rectangle([bx, by, bx+bw, by+2], radius=1, fill=ACCENT_LT)
    draw.text((bx+14, by+7), badge_txt, font=f_badge, fill=ACCENT_LT)

    # 頻道標題（中欄）
    ch_title = "智慧製造深度對談"
    f_ch = ImageFont.truetype(bold_path, 38)
    bb_ch = draw.textbbox((0,0), ch_title, font=f_ch)
    draw.text((mid_cx - (bb_ch[2]-bb_ch[0])//2, 128), ch_title, font=f_ch, fill=WHITE)

    # ════════════════════════════════════════════════════
    # 右欄：節目資訊
    # ════════════════════════════════════════════════════
    f_sec_title = ImageFont.truetype(bold_path, 30)
    f_bullet    = ImageFont.truetype(reg_path,  26)
    f_company   = ImageFont.truetype(bold_path, 28)
    f_company_s = ImageFont.truetype(reg_path,  22)

    rx = COL2 + 36
    rw = W - COL2 - 60

    # 「本集重點」小標
    draw.text((rx, 90), "本集重點", font=f_sec_title, fill=ACCENT_LT)
    draw.rectangle([rx, 128, rx+50, 132], fill=ACCENT)

    bullets = [
        f"· {meta['stat1']}",
        f"· {meta['stat2']}",
        f"· {meta['stat3']}",
        "· 台灣製造業應用實例",
        "· 導入策略與 ROI 分析",
        "· 欣晨工業實戰經驗分享",
    ]
    by2 = 148
    for bullet in bullets:
        for line in wrap_cjk(draw, bullet, f_bullet, rw):
            draw.text((rx, by2), line, font=f_bullet, fill=GRAY)
            bb = draw.textbbox((0,0), line, font=f_bullet)
            by2 += (bb[3]-bb[1]) + 6
        by2 += 4

    # 公司資訊欄（右欄下方）
    company_y = H - 330
    draw.rounded_rectangle([rx-6, company_y, W-24, H-186], radius=10, fill=(12, 20, 40))
    draw.rounded_rectangle([rx-6, company_y, rx-2, H-186], radius=4, fill=ACCENT)

    draw.text((rx+10, company_y+14), "欣晨工業有限公司", font=f_company, fill=WHITE)
    draw.text((rx+10, company_y+50), "Hsin-Chan Industrial Co., Ltd.", font=f_company_s, fill=GRAY)

    info_items = [
        ("📍", "桃園市大園區中正東路三段490號"),
        ("📞", "03-381-4497  |  +886-3-381-4497"),
        ("🌐", "www.hsinchan.com"),
        ("📅", "1975年創立  ·  51年精密製造經驗"),
    ]
    iy = company_y + 86
    for icon, text in info_items:
        draw.text((rx+10, iy), f"{icon}  {text}", font=f_company_s, fill=GRAY)
        iy += 34

    # ── 底部波形區 ────────────────────────────────────────────────
    draw.rectangle([0, H-172, W, H], fill=(5, 8, 16))
    draw.rectangle([0, H-175, W, H-172], fill=ACCENT)

    # 底部中央文字
    bottom_text = "🎙  小欣 × 阿晨  ·  每3天更新  ·  智慧製造深度對談"
    f_bottom = ImageFont.truetype(reg_path, 26)
    bb_bot = draw.textbbox((0,0), bottom_text, font=f_bottom)
    draw.text(((W-(bb_bot[2]-bb_bot[0]))//2, H-138), bottom_text, font=f_bottom, fill=GRAY)

    img.save(out_path)
    print("🖼️  三欄式 Podcast 背景圖建立完成（1920×1080）")

# ── FFmpeg 合成影片 ───────────────────────────────────────────────────────────
def render_video(bg_path, audio_path, duration, out_path):
    print("🎬 FFmpeg 合成影片（底部即時波形）...")
    fc = (
        "[0:v]scale=1920:1080[bg];"
        "[1:a]showwaves=s=1920x162:mode=cline:rate=30:colors=1a3f98|5a8ce0[wave];"
        "[bg][wave]overlay=0:905[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_path),
        "-i",    str(audio_path),
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration), "-r", "30",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 失敗：{result.stderr[-800:]}")
    size = Path(out_path).stat().st_size / 1024 / 1024
    print(f"✅ 影片合成完成：{size:.0f} MB，{duration/60:.1f} 分鐘")

# ── 上傳 ─────────────────────────────────────────────────────────────────────
def upload_facebook(video_path, topic_title, dialogue):
    page_id = os.environ["FB_PAGE_ID"]
    token   = os.environ["FB_ACCESS_TOKEN"]
    snippet = dialogue[0]["text"][:120] if dialogue else ""
    caption = (
        f"🎙️ 【智慧製造深度對談】{topic_title}\n\n"
        f"{snippet}...\n\n"
        f"本集由欣晨工業小欣與阿晨深度對談，帶你了解{topic_title}的核心觀念與台灣製造業應用。\n\n"
        f"#智慧製造 #工業自動化 #欣晨工業 #台灣製造 #豐田生產方式 #TPS #Podcast #NotebookLM"
    )
    print("📤 上傳至 Facebook...")
    with open(video_path, "rb") as vf:
        resp = requests.post(
            f"https://graph-video.facebook.com/v21.0/{page_id}/videos",
            data={"description": caption, "access_token": token},
            files={"source": ("podcast.mp4", vf, "video/mp4")},
            timeout=300,
        )
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"FB 錯誤：{data['error']['message']}")
    print(f"✅ Facebook 發布成功！ID：{data.get('id')}")
    return caption

def upload_youtube(video_path, topic_title, caption, topic_tag):
    cid = os.environ.get("YT_CLIENT_ID")
    cs  = os.environ.get("YT_CLIENT_SECRET")
    rt  = os.environ.get("YT_REFRESH_TOKEN")
    if not all([cid, cs, rt]):
        print("⚠️  缺少 YouTube Secrets，跳過 YouTube 上傳")
        return None
    creds = Credentials(
        token=None, refresh_token=rt, client_id=cid, client_secret=cs,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(GoogleRequest())
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    title = f"【智慧製造深度對談】{topic_title}｜欣晨工業 Podcast"[:100]
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": caption,
                        "tags": ["智慧製造", "工業自動化", "欣晨工業", "Podcast", topic_tag,
                                 "TPS", "豐田生產方式", "台灣製造業", "NotebookLM"],
                        "categoryId": "28", "defaultLanguage": "zh-TW"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=media,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   上傳中... {int(status.progress()*100)}%", end="\r")
    vid = response.get("id")
    print(f"\n✅ YouTube 發布成功！https://youtu.be/{vid}")
    return vid

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    print("═══════════════════════════════════════════════════════")
    print("  欣晨工業 — NotebookLM 同款技術 Podcast 影片")
    print("  Claude Sonnet 腳本 × Gemini 2.5 Flash TTS 多主持人語音")
    print("  小欣（Zephyr 女聲）× 阿晨（Puck 男聲）")
    print("═══════════════════════════════════════════════════════\n")

    dry_run     = os.environ.get("DRY_RUN", "false").lower() == "true"
    google_key  = os.environ["GOOGLE_API_KEY"]
    tw          = datetime.now(timezone(timedelta(hours=8)))
    date_str    = tw.strftime("%Y-%m-%d")
    topic_idx   = (tw.timetuple().tm_yday // 3) % len(TOPICS)
    topic_title, topic_tag, topic_angle = TOPICS[topic_idx]

    print(f"📅 {date_str}  今集：{topic_title}")
    if dry_run:
        print("⚠️  DRY RUN：產生影片但不上傳\n")

    ac = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 1. 生成對話腳本
        dialogue = generate_script(topic_title, topic_angle, ac)
        print("\n── 腳本前3輪預覽 ────────────────────────────────────")
        for turn in dialogue[:3]:
            tag = "小欣" if turn["speaker"] == "Host1" else "阿晨"
            print(f"  [{tag}] {turn['text'][:60]}…")
        print()

        # 2. 載入字型 & 建立背景
        bold_path, reg_path = load_fonts()
        bg_path = tmp / "bg.png"
        create_bg_image(topic_title, bold_path, reg_path, bg_path, topic_tag)

        # 3. Gemini TTS 多主持人語音合成（分段）
        audio_path, duration = tts_with_chunks(dialogue, tmpdir, google_key)

        # 4. 合成影片
        video_out = tmp / f"podcast_gemini_{date_str}.mp4"
        render_video(bg_path, audio_path, duration, video_out)

        if dry_run:
            import shutil
            final = Path(f"podcast_gemini_{date_str}.mp4")
            shutil.copy(video_out, final)
            print(f"\n✅ Dry run 完成：{final}（{duration/60:.1f} 分鐘）")
            return

        # 5. 上傳 FB + YouTube
        print("\n── 上傳各平台 ────────────────────────────────────────")
        caption = upload_facebook(str(video_out), topic_title, dialogue)
        yt_id   = upload_youtube(str(video_out), topic_title, caption, topic_tag)
        print(f"\n🎉 {date_str} Podcast 發布完成")
        if yt_id:
            print(f"   YouTube：https://youtu.be/{yt_id}")

if __name__ == "__main__":
    main()
