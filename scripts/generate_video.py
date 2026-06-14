#!/usr/bin/env python3
"""
欣晨工業 — 每日智慧製造 Facebook 影片自動發文
流程：Claude 生成腳本 → Pillow 繪製投影片 → FFmpeg 合成影片 → Facebook 上傳
"""

import os, sys, json, subprocess, tempfile, textwrap, math
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
import requests
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

# ── 設計常數 ────────────────────────────────────────────────────────────────
W, H       = 1080, 1080
BG         = (10,  13,  21)        # 深底色
SURFACE    = (16,  24,  48)        # 稍亮底色（slide body）
ACCENT     = (26,  63, 152)        # 欣晨藍
ACCENT_LT  = (90, 140, 230)        # 淺藍（強調文字）
WHITE      = (240, 244, 248)
GRAY       = (138, 155, 174)
DARK_GRAY  = (55,  70,  90)

SLIDE_DURATION = 4   # 每張 4 秒
FADE_DURATION  = 0.5 # xfade 0.5 秒

# ── 字型 ────────────────────────────────────────────────────────────────────
def load_fonts():
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_reg = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    bold_path = next((p for p in candidates if Path(p).exists()), None)
    reg_path  = next((p for p in candidates_reg if Path(p).exists()), None)
    if not bold_path:
        raise FileNotFoundError("找不到 CJK 字型，請確認已安裝 fonts-noto-cjk")
    return bold_path, reg_path or bold_path

# ── 文字換行 ─────────────────────────────────────────────────────────────────
def wrap_text(draw, text, font, max_width):
    """依像素寬度換行（支援中文）"""
    lines, current = [], ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines

def draw_wrapped(draw, text, font, x, y, max_width, fill, line_spacing=1.35):
    lines = wrap_text(draw, text, font, max_width)
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        cy += int((bbox[3] - bbox[1]) * line_spacing)
    return cy

# ── 繪製函數 ─────────────────────────────────────────────────────────────────
def draw_bg_gradient(img):
    """畫深色漸層底色"""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(BG[0] + (SURFACE[0] - BG[0]) * ratio)
        g = int(BG[1] + (SURFACE[1] - BG[1]) * ratio)
        b = int(BG[2] + (SURFACE[2] - BG[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    # 左上裝飾光暈
    for radius in range(350, 0, -1):
        alpha = int(18 * (1 - radius / 350))
        r = min(255, ACCENT[0] + alpha)
        g = min(255, ACCENT[1] + alpha // 2)
        b = min(255, ACCENT[2] + alpha // 2)
        draw.ellipse([-radius//2, -radius//2, radius//2, radius//2], fill=(r, g, b, 0))

def draw_accent_line(draw, y, width=120):
    """左側藍色裝飾線"""
    draw.rectangle([80, y, 80 + width, y + 5], fill=ACCENT_LT)

def draw_logo_watermark(draw, font_small):
    """右下角品牌浮水印"""
    text = "欣晨工業 Hsin-Chan Industrial"
    bbox = draw.textbbox((0, 0), text, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text((W - tw - 50, H - 65), text, font=font_small, fill=DARK_GRAY)

def make_title_slide(topic_title, topic_tag, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    font_eyebrow  = ImageFont.truetype(bold_path, 28)
    font_title    = ImageFont.truetype(bold_path, 82)
    font_subtitle = ImageFont.truetype(reg_path,  36)
    font_brand    = ImageFont.truetype(bold_path, 30)
    font_small    = ImageFont.truetype(reg_path,  24)

    # 眉標
    draw.text((80, 180), "智慧製造每日一則", font=font_eyebrow, fill=ACCENT_LT)
    draw_accent_line(draw, 218, 200)

    # 大標題（換行）
    title_y = 260
    title_y = draw_wrapped(draw, topic_title, font_title, 80, title_y, W - 160, WHITE, 1.15)

    # 標籤 badge
    badge_text = f"  #{topic_tag}  "
    bbox = draw.textbbox((0, 0), badge_text, font=font_subtitle)
    bw = bbox[2] - bbox[0] + 20
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([80, title_y + 40, 80 + bw, title_y + 40 + bh], radius=8, fill=ACCENT)
    draw.text((90, title_y + 48), badge_text.strip(), font=font_subtitle, fill=WHITE)

    # 品牌
    draw.text((80, H - 160), "欣晨工業有限公司", font=font_brand, fill=WHITE)
    draw.text((80, H - 115), "Hsin-Chan Industrial Co., Ltd. · Since 1996", font=font_small, fill=GRAY)

    img.save(out_path)

def make_point_slide(number, title, body, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    font_num   = ImageFont.truetype(bold_path, 110)
    font_title = ImageFont.truetype(bold_path, 52)
    font_body  = ImageFont.truetype(reg_path,  36)
    font_small = ImageFont.truetype(reg_path,  24)

    # 背景大數字（淡）
    draw.text((W - 220, 60), f"{number:02d}", font=font_num, fill=(26, 63, 152, 0))
    # 重新畫帶透明度效果（直接用深色）
    draw.text((W - 220, 60), f"{number:02d}", font=font_num, fill=(30, 50, 100))

    # 裝飾線
    draw_accent_line(draw, 160, 60)

    # Point 標題
    y = 190
    y = draw_wrapped(draw, title, font_title, 80, y, W - 160, ACCENT_LT, 1.2)

    # 分隔線
    draw.rectangle([80, y + 24, W - 80, y + 26], fill=DARK_GRAY)

    # 內文
    y = y + 50
    draw_wrapped(draw, body, font_body, 80, y, W - 160, GRAY, 1.55)

    draw_logo_watermark(draw, font_small)
    img.save(out_path)

def make_cta_slide(bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    font_cta   = ImageFont.truetype(bold_path, 56)
    font_info  = ImageFont.truetype(reg_path,  40)
    font_sub   = ImageFont.truetype(reg_path,  32)
    font_small = ImageFont.truetype(reg_path,  24)

    draw_accent_line(draw, 200, 80)
    draw.text((80, 240), "需要精密自動化解決方案？", font=font_cta, fill=WHITE)

    y = 380
    draw.text((80, y),       "🌐  www.hsinchan.com",   font=font_info, fill=ACCENT_LT)
    draw.text((80, y + 70),  "📞  03-381-4497",        font=font_info, fill=ACCENT_LT)
    draw.text((80, y + 140), "✉   hc3814497@gmail.com", font=font_sub,  fill=GRAY)

    draw.rectangle([80, H - 180, W - 80, H - 178], fill=DARK_GRAY)
    draw.text((80, H - 160), "欣晨工業有限公司", font=font_sub,   fill=WHITE)
    draw.text((80, H - 115), "台灣桃園 · 1996年創立 · 30年精密製造經驗", font=font_small, fill=GRAY)

    img.save(out_path)

# ── Claude API ───────────────────────────────────────────────────────────────
TOPICS = [
    ("Kaizen 改善文化",   "Kaizen",    "Kaizen持續改善的工廠實踐：消除七大浪費，VSM價值流分析，SOP標準化 — 讓工廠每天比昨天好一點點的系統方法。"),
    ("JIT 即時生產",      "JIT",       "JIT即時生產如何消滅庫存浪費：正確時間、正確數量、正確品項 — 拉式生產系統讓生產線流暢無阻的邏輯。"),
    ("工業機械手臂整合",  "機器人",    "2025年工業機器人應用趨勢：FANUC、ABB、KUKA協作機器人在台灣製造業的落地案例，第七軸線性走行軸拓展工作範圍。"),
    ("AI 視覺檢測 AOI",   "AI視覺",    "深度學習AOI如何把瑕疵偵測準確率從90%提升到99.5%：工業相機選型、打光設計、CNN模型訓練的實務重點。"),
    ("數位雙生應用",      "數位雙生",  "數位雙生讓工廠在虛擬世界先跑模擬，再在真實世界執行：IoT感測器架構、OPC-UA通訊、預測性維護減少停機30%。"),
    ("Poka-yoke 防呆設計","防呆",      "Poka-yoke防呆設計：用機構設計從源頭杜絕人為錯誤，讓新手工人也能零缺陷作業的工業工程思維。"),
    ("OEE 設備效率提升",  "OEE",       "OEE整體設備效率：世界級工廠目標85%，台灣中小製造業平均55-65%。可用率×性能效率×良品率，每個數字背後的改善機會。"),
    ("半導體精密製程",    "半導體",    "台灣半導體供應鏈的精密耗材需求：SiC保護管、精密夾治具、高溫熱電偶 — 支撐摩爾定律前進的關鍵材料技術。"),
    ("電動車製造自動化",  "EV",        "電動車製造的自動化挑戰：電池組裝精密點焊、電機鋁殼鑄造脫氣、JIT生產排程 — EV時代對台灣零件廠的新機會。"),
    ("工廠數位化轉型",    "工業4.0",   "工業4.0在台灣中小製造業的現實路徑：從連結設備、建立儀表板，到AI診斷、自主優化 — 分階段推進的務實策略。"),
    ("SMED 快速換模",     "SMED",      "SMED快速換模如何讓換線時間從3小時縮到30分鐘：內外作業分離、標準化程序、模組化工裝設計的實際做法。"),
    ("預測性維護 PdM",    "預測維護",  "預測性維護如何在設備壞掉前發出警報：振動分析、熱像儀診斷、電流頻譜 — 從被動維修到主動預防的轉型邏輯。"),
    ("精密夾治具設計",    "夾治具",    "高精度夾治具如何實現±0.02mm重複定位精度：快拆設計縮短換線、模組化降低開發成本 — 自動化系統的基石。"),
    ("高溫工業耗材",      "高溫材料",  "工業高溫材料的選材邏輯：SiC保護管、高純度石墨、耐火材料 — 在1200°C以上的極端環境中，材料選擇決定製程成敗。"),
    ("人形機器人零件製造","人形機器人", "人形機器人崛起對精密製造的需求：關節傳動套筒、輕量鋁合金結構件、耐磨陶瓷導向件 — ±0.01mm加工精度的挑戰。"),
    ("製造業供應鏈韌性",  "供應鏈",    "COVID後製造業供應鏈重組：台灣工廠如何在效率與韌性之間找平衡？近岸採購、安全庫存緩衝、供應商多元化策略。"),
    ("協作機器人 Cobot",  "Cobot",     "協作機器人不是取代工人，而是解放工人：UR、FANUC CRX安全整合（ISO TS 15066），人機協作在台灣中小製造業的ROI計算。"),
    ("碳中和製造",        "淨零碳排",  "製造業淨零路徑：能源監控ISO 50001、設備效率提升、廢熱回收 — 精實製造如何同時降低成本與碳排放量。"),
    ("SPC 統計製程控制",  "品質管理",  "SPC統計製程控制：Cp/Cpk指數量化製程能力，把品質管制從結果端移到製程端 — 為什麼「預防」永遠比「檢驗」便宜。"),
    ("IoT 工廠感測網路",  "IIoT",      "工業IoT架構設計：OPC-UA、MQTT、Modbus TCP通訊協定選型，如何讓工廠中所有設備都開口說話，建立數據驅動決策基礎。"),
]

def get_today_topic():
    tw_now   = datetime.now(timezone(timedelta(hours=8)))
    day_idx  = tw_now.timetuple().tm_yday % len(TOPICS)
    title, tag, angle = TOPICS[day_idx]
    date_str = tw_now.strftime("%Y-%m-%d")
    print(f"📅 日期：{date_str}（年第{tw_now.timetuple().tm_yday}天）")
    print(f"📌 今日題材：{title}（#{tag}）")
    return title, tag, angle, date_str

def generate_video_script(topic_title, topic_angle):
    print("🤖 呼叫 Claude API 生成影片腳本...")
    ac = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""你是欣晨工業有限公司的社群媒體編輯，需要為 Facebook 影片製作腳本。

欣晨工業是台灣桃園1996年創立的精密自動化設備製造商，以豐田生產方式（TPS）為核心哲學。
主要業務：工業加熱器（1200°C）、熱電偶、一體式料管、碳化矽保護管、機械手臂整合、AOI視覺檢測。

今日題材：{topic_title}
角度提示：{topic_angle}

請以JSON格式輸出影片腳本，嚴格遵守以下結構：
{{
  "slide_title": "一句話的投影片主標（15字以內，有衝擊力）",
  "points": [
    {{ "title": "重點標題（10字以內）", "body": "說明（50-70字，具體有數據）" }},
    {{ "title": "重點標題（10字以內）", "body": "說明（50-70字，具體有數據）" }},
    {{ "title": "重點標題（10字以內）", "body": "說明（50-70字，具體有數據）" }},
    {{ "title": "重點標題（10字以內）", "body": "說明（50-70字，具體有數據）" }}
  ],
  "fb_caption": "Facebook 貼文說明（300-400字，專業不說教，結尾有互動問題）\\n\\n#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5"
}}

要求：
- 繁體中文
- 數字要有根據（可引用產業現況或技術規格）
- 自然連結欣晨工業的技術能力，不硬推銷
- 只輸出JSON，不要前言說明"""

    msg = ac.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    # 去掉可能的 markdown code block
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── 影片生成 ─────────────────────────────────────────────────────────────────
def create_video(slide_paths, out_path):
    """用 FFmpeg concat + xfade 合成影片"""
    n = len(slide_paths)
    # 建立 filter_complex：每張 slide 顯示 SLIDE_DURATION 秒，間格 FADE_DURATION 秒 crossfade
    inputs = []
    for p in slide_paths:
        inputs += ["-loop", "1", "-t", str(SLIDE_DURATION + FADE_DURATION), "-i", str(p)]

    # xfade chain
    fc_parts = []
    last_label = "[0:v]"
    for i in range(1, n):
        offset = SLIDE_DURATION * i - FADE_DURATION * (i - 1)
        out_label = f"[v{i}]" if i < n - 1 else "[vout]"
        fc_parts.append(
            f"{last_label}[{i}:v]xfade=transition=fade:duration={FADE_DURATION}:offset={offset:.2f}{out_label}"
        )
        last_label = f"[v{i}]"

    filter_complex = "; ".join(fc_parts)

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + ["-filter_complex", filter_complex,
           "-map", "[vout]",
           "-c:v", "libx264", "-preset", "fast",
           "-pix_fmt", "yuv420p",
           "-r", "30",
           str(out_path)]
    )
    print("🎬 FFmpeg 合成影片...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 失敗：{result.stderr[-800:]}")
    size_mb = Path(out_path).stat().st_size / 1024 / 1024
    print(f"✅ 影片生成完成：{out_path}（{size_mb:.1f} MB）")

# ── Facebook 影片上傳 ─────────────────────────────────────────────────────────
def upload_video_to_facebook(video_path, caption):
    page_id = os.environ["FB_PAGE_ID"]
    token   = os.environ["FB_ACCESS_TOKEN"]

    print("📤 上傳影片到 Facebook...")
    with open(video_path, "rb") as vf:
        resp = requests.post(
            f"https://graph-video.facebook.com/v21.0/{page_id}/videos",
            data={"description": caption, "access_token": token},
            files={"source": ("video.mp4", vf, "video/mp4")},
            timeout=180,
        )
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Facebook API 錯誤：{data['error']['message']}")
    print(f"✅ Facebook 影片發布成功！Video ID：{data.get('id')}")
    return data.get("id")

# ── YouTube 影片上傳 ───────────────────────────────────────────────────────────
def upload_video_to_youtube(video_path, slide_title, caption, topic_tag, date_str):
    client_id     = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("⚠️  缺少 YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN，跳過 YouTube 上傳")
        return None

    print("📺 上傳影片到 YouTube...")

    # 用 refresh token 取得 access token
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(GoogleRequest())

    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    yt_title = f"【智慧製造】{slide_title}｜欣晨工業 Hsin-Chan Industrial"
    if len(yt_title) > 100:
        yt_title = yt_title[:97] + "..."

    yt_desc = (
        f"{caption}\n\n"
        f"─────────────────────────────\n"
        f"欣晨工業有限公司｜Hsin-Chan Industrial Co., Ltd.\n"
        f"🌐 https://www.hsinchan.com\n"
        f"📞 +886-3-381-4497\n"
        f"📍 台灣桃園市大園區中正東路三段490號\n"
        f"⏰ 週一至週五 08:00–17:30\n\n"
        f"欣晨工業1996年創立，以豐田生產方式（TPS）為核心，提供精密自動化設備與工業耗材。\n"
        f"服務：機械手臂整合、AOI視覺檢測、數位雙生、工業加熱器、熱電偶、一體式料管。"
    )

    tags = [
        "智慧製造", "工業自動化", "欣晨工業", "Hsin-Chan Industrial",
        "台灣製造", "豐田生產方式", "TPS", "精密製造", "桃園工業",
        topic_tag, "Industry 4.0", "工業4.0", "製造業",
    ]

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title":       yt_title,
                "description": yt_desc,
                "tags":        tags,
                "categoryId":  "28",   # Science & Technology
                "defaultLanguage": "zh-TW",
            },
            "status": {
                "privacyStatus":           "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=media,
    )

    # resumable upload loop
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"   上傳中... {pct}%", end="\r")

    video_id = response.get("id")
    print(f"\n✅ YouTube 影片發布成功！https://youtu.be/{video_id}")
    return video_id

# ── 主程式 ───────────────────────────────────────────────────────────────────
def main():
    print("═══════════════════════════════════════════")
    print("  欣晨工業 — 每日智慧製造 Facebook 影片發文")
    print("═══════════════════════════════════════════")

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    if dry_run:
        print("⚠️  DRY RUN：只產生影片，不上傳\n")

    topic_title, topic_tag, topic_angle, date_str = get_today_topic()

    # 1. 生成腳本
    script = generate_video_script(topic_title, topic_angle)
    print(f"\n📝 投影片主標：{script['slide_title']}")
    for i, pt in enumerate(script["points"], 1):
        print(f"   {i}. {pt['title']}")
    print(f"\n── Facebook 說明文字（前100字）──")
    print(script["fb_caption"][:100] + "...")

    # 2. 載入字型
    bold_path, reg_path = load_fonts()
    print(f"\n🔤 字型：{Path(bold_path).name}")

    # 3. 繪製投影片
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        slides = []

        # Title slide
        p = tmp / "slide_00_title.png"
        make_title_slide(script["slide_title"], topic_tag, bold_path, reg_path, p)
        slides.append(p)
        print("🖼️  Title slide")

        # Point slides
        for i, pt in enumerate(script["points"], 1):
            p = tmp / f"slide_{i:02d}_point.png"
            make_point_slide(i, pt["title"], pt["body"], bold_path, reg_path, p)
            slides.append(p)
            print(f"🖼️  Point {i}: {pt['title']}")

        # CTA slide
        p = tmp / "slide_99_cta.png"
        make_cta_slide(bold_path, reg_path, p)
        slides.append(p)
        print("🖼️  CTA slide")

        # 4. 合成影片
        video_path = tmp / f"hsinchan_{date_str}.mp4"
        create_video(slides, video_path)

        if dry_run:
            import shutil
            out = Path(f"hsinchan_video_{date_str}.mp4")
            shutil.copy(video_path, out)
            print(f"\n✅ Dry run 完成，影片儲存為：{out}")
            return

        # 5. 同時上傳 Facebook + YouTube
        print("\n── 上傳至各平台 ────────────────────────────")
        fb_id = upload_video_to_facebook(str(video_path), script["fb_caption"])
        yt_id = upload_video_to_youtube(
            str(video_path), script["slide_title"],
            script["fb_caption"], topic_tag, date_str
        )

        print(f"\n🎉 完成！{date_str} 影片已發布")
        if fb_id: print(f"   Facebook Video ID : {fb_id}")
        if yt_id: print(f"   YouTube Video ID  : {yt_id}  (https://youtu.be/{yt_id})")

if __name__ == "__main__":
    main()
