#!/usr/bin/env python3
"""
欣晨工業 — NotebookLM 風格雙主持人 Podcast 影片生成器
流程：Claude 生成對話 → OpenAI TTS 雙聲道 → FFmpeg 合成影片 → 上傳 FB + YouTube
主持人：小欣（女）× 阿晨（男），取自「欣晨」二字
"""

import os, sys, json, subprocess, tempfile, math, struct, wave
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic, requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

# ── 設計常數 ────────────────────────────────────────────────────────────────
W, H        = 1920, 1080
BG          = (8,  12,  22)
SURFACE     = (14, 22,  42)
ACCENT      = (26, 63, 152)
ACCENT_LT   = (90, 140, 230)
FEMALE_CLR  = (220, 80, 130)    # 小欣 — 玫瑰色
MALE_CLR    = (50, 160, 220)    # 阿晨 — 天藍色
WHITE       = (240, 244, 248)
GRAY        = (120, 140, 168)
DARK        = (30, 40, 60)

# TTS 聲音對應
VOICE_FEMALE = "nova"    # OpenAI TTS 女聲
VOICE_MALE   = "onyx"    # OpenAI TTS 男聲

# ── 主題題材（20 個，每3天輪換）────────────────────────────────────────────
TOPICS = [
    ("改善文化與豐田哲學",  "Kaizen",   "從豐田工廠到台灣製造業，改善文化如何讓工廠每天比昨天好一點點？VSM、5S、Poka-yoke的實際應用與落地案例。"),
    ("工業機器人整合實戰",  "機器人",   "FANUC、ABB、KUKA機械手臂在台灣中小製造業的導入策略，第七軸設計、視覺引導、協作機器人（Cobot）安全整合。"),
    ("AI視覺檢測革命",     "AOI",      "深度學習如何讓AOI準確率突破99.5%？工業相機選型、打光設計、半導體與電子封裝的瑕疵偵測實例。"),
    ("數位雙生與預測維護",  "數位雙生", "IoT感測器、OPC-UA通訊、雲端儀表板——如何讓工廠設備在虛擬世界說話，提前預測故障、減少停機。"),
    ("台灣製造業的未來路",  "工業4.0",  "從工業3.5到工業4.0，台灣中小製造業的務實數位化路徑，燈塔工廠的共同特徵與可借鑑的策略。"),
    ("高溫工業耗材技術",    "高溫材料", "碳化矽保護管、高純度石墨、耐火材料——在1600°C以上極端環境中，材料選擇如何決定製程成敗？"),
    ("電動車製造的機會",    "EV",       "電動車零件、電池模組、電機殼鑄造——EV浪潮為台灣精密製造業帶來什麼新機會和技術挑戰？"),
    ("半導體製程精密挑戰",  "半導體",   "台灣半導體供應鏈對精密耗材的嚴苛要求，從擴散爐爐管到夾治具設計，每個微米都是競爭力。"),
    ("OEE設備效率密碼",     "OEE",      "整體設備效率（OEE）如何從60%提升到85%？可用率、性能效率、良品率背後的改善邏輯與實戰做法。"),
    ("射出成型優化秘訣",    "射出成型", "料管材質選擇、溫度控制精度、SMED快速換模——射出成型製程的隱性損失與系統性優化方法。"),
    ("人形機器人零件需求",  "人形機器人","Tesla Optimus、Figure、Unitree崛起，台灣精密加工業如何抓住關節傳動、輕量結構件的新商機？"),
    ("JIT即時生產哲學",     "JIT",       "從豐田拉式生產到現代工廠，JIT如何消滅庫存浪費？台灣製造業導入JIT的挑戰、做法與成功案例。"),
    ("工廠數位化起步指南",  "數位化",    "設備上網→即時儀表板→AI診斷→自主優化，四個層次的數位化路徑，沒有IT背景的工廠老闆如何開始？"),
    ("夾治具設計的精髓",    "夾治具",    "±0.02mm重複定位精度如何實現？模組化工裝、快拆設計、自動化系統中夾治具扮演的關鍵角色。"),
    ("碳中和製造新思維",    "淨零",      "製造業碳中和不只是環保議題，也是降成本機會：能源監控、廢熱回收、設備效率提升的實務做法。"),
    ("現地現物的力量",      "現地現物",  "豐田最核心的現場哲學：不相信二手報告，親自到現場。欣晨工業如何把這個原則落實在每個客戶專案？"),
    ("台灣鋁鑄造業升級",    "鋁鑄造",    "石墨脫氣管、澆注系統加熱管、即時溫度監控——台灣鋁合金壓鑄廠如何透過精密耗材提升鑄件品質？"),
    ("自動化ROI計算框架",   "自動化ROI", "如何向老闆說明自動化投資值得？人力成本節省、良率提升、停機減少——一個可量化的ROI計算方法論。"),
    ("製造業人才培育新策略", "人才",      "老師傅退休潮、技術斷層危機，數位工具如何幫助知識傳承？技能矩陣、AR輔助訓練的台灣工廠實例。"),
    ("精密量測技術前沿",    "量測",      "CMM三次元量測、雷射掃描、非接觸光學量測——精密製造的品質根基，以及量測數據如何回饋製程改善。"),
]

# ── 工具 ─────────────────────────────────────────────────────────────────────
def get_today_topic():
    tw = datetime.now(timezone(timedelta(hours=8)))
    idx = (tw.timetuple().tm_yday // 3) % len(TOPICS)
    title, tag, angle = TOPICS[idx]
    date_str = tw.strftime("%Y-%m-%d")
    print(f"📅 {date_str}（年第{tw.timetuple().tm_yday}天，題材 #{idx}）")
    print(f"🎙️  今集主題：{title}")
    return title, tag, angle, date_str

def load_fonts():
    paths_bold = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    ]
    paths_reg = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ]
    bold = next((p for p in paths_bold if Path(p).exists()), None)
    reg  = next((p for p in paths_reg  if Path(p).exists()), None)
    if not bold:
        raise FileNotFoundError("找不到 CJK 字型，請安裝 fonts-noto-cjk")
    return bold, reg or bold

# ── 腳本生成 ─────────────────────────────────────────────────────────────────
def generate_script(topic_title, topic_angle, ac_client):
    print("🤖 Claude 生成對話腳本（~10分鐘）...")
    prompt = f"""你是一個 Podcast 節目製作人，要為欣晨工業有限公司製作一集「智慧製造深度對談」節目。

節目格式：NotebookLM 風格雙主持人深度對談
- 女主持人：小欣（活潑、善於提問、代表觀眾視角）
- 男主持人：阿晨（資深工程師背景、善於深入解說、代表業界經驗）
- 名字取自「欣晨工業」，自然融入品牌識別

今集主題：{topic_title}
方向提示：{topic_angle}

欣晨工業背景（自然融入，不要過度推銷）：
- 1996年創立，30年精密製造經驗，台灣桃園市大園區
- 核心產品：工業加熱器（1200°C）、熱電偶、碳化矽保護管、高濃度奈米氣泡流體模組
- 核心服務：機械手臂整合（FANUC/ABB/KUKA）、AOI視覺檢測、數位雙生
- 哲學：豐田生產方式 TPS（Kaizen/JIT/Jidoka）

請生成一集約10分鐘的對話腳本，輸出為 JSON 陣列：
[
  {{"speaker": "小欣", "text": "（開場白、引入主題）..."}},
  {{"speaker": "阿晨", "text": "（專業解說）..."}},
  {{"speaker": "小欣", "text": "（追問、轉折）..."}},
  ...
]

要求：
- 共 28-35 個對話輪次
- 每輪 60-100 字（繁體中文），自然口語，不像讀稿
- 涵蓋：主題介紹→核心概念→深度解析→台灣案例→觀眾實用建議→結尾
- 小欣負責提問、驚嘆、串場；阿晨負責深度解說、數據、案例
- 不要「主持人A說：」這種格式，直接輸出對話內容
- 自然提到欣晨工業2-3次，不硬推銷
- 只輸出 JSON 陣列，不要前言說明"""

    msg = ac_client.messages.create(
        model="claude-sonnet-4-6",   # 用 Sonnet 確保腳本品質
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = raw[:-3]
    dialogue = json.loads(raw.strip())
    total_chars = sum(len(d["text"]) for d in dialogue)
    print(f"✅ 腳本生成完成：{len(dialogue)} 輪對話，{total_chars} 字（預估 {total_chars//150} 分鐘）")
    return dialogue

# ── TTS 音訊生成 ─────────────────────────────────────────────────────────────
def generate_audio_segments(dialogue, oai_client, tmp_dir):
    """為每個對話輪次生成 MP3，回傳 (mp3_path, speaker) 清單"""
    segments = []
    tmp = Path(tmp_dir)
    print(f"🔊 生成 {len(dialogue)} 段 TTS 音訊...")
    for i, turn in enumerate(dialogue):
        speaker = turn["speaker"]
        text    = turn["text"]
        voice   = VOICE_FEMALE if speaker == "小欣" else VOICE_MALE
        out     = tmp / f"seg_{i:03d}_{speaker}.mp3"

        with oai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=0.95,         # 稍慢，更清晰
        ) as resp:
            resp.stream_to_file(str(out))

        segments.append({"path": str(out), "speaker": speaker, "text": text})
        if (i + 1) % 5 == 0:
            print(f"   {i+1}/{len(dialogue)} 段完成")

    print("✅ TTS 音訊生成完成")
    return segments

def concat_audio(segments, silence_ms=400, tmp_dir=None):
    """拼接所有音訊片段，插入靜音間隔，回傳最終 MP3 路徑"""
    tmp = Path(tmp_dir)

    # 建立靜音 MP3
    silence_path = tmp / "silence.mp3"
    dur = silence_ms / 1000.0
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
         "-t", str(dur), "-q:a", "9", "-acodec", "libmp3lame", str(silence_path)],
        capture_output=True, check=True
    )

    # 建立 concat list（每段後加靜音）
    list_path = tmp / "concat.txt"
    with open(list_path, "w") as f:
        for seg in segments:
            f.write(f"file '{seg['path']}'\n")
            f.write(f"file '{silence_path}'\n")

    full_audio = tmp / "podcast_audio.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_path), "-c", "copy", str(full_audio)],
        capture_output=True, check=True
    )
    # 取得實際時長
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(full_audio)],
        capture_output=True, text=True
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    print(f"✅ 音訊拼接完成：{duration/60:.1f} 分鐘")
    return str(full_audio), duration

# ── 視覺 ─────────────────────────────────────────────────────────────────────
def draw_bg(img):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = BG[0] + (SURFACE[0] - BG[0]) * y // H
        g = BG[1] + (SURFACE[1] - BG[1]) * y // H
        b = BG[2] + (SURFACE[2] - BG[2]) * y // H
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    # grid overlay
    for x in range(0, W, 72):
        draw.line([(x, 0), (x, H)], fill=(26, 40, 70))
    for y in range(0, H, 72):
        draw.line([(0, y), (W, y)], fill=(26, 40, 70))

def draw_host_avatar(draw, cx, cy, r, color, name, bold_font, label_font, active=True):
    alpha = 255 if active else 80
    # 外圈光暈
    if active:
        for ring in range(r + 30, r - 1, -3):
            a = int(60 * (1 - (ring - r) / 30))
            draw.ellipse([cx - ring, cy - ring, cx + ring, cy + ring],
                         outline=(*color, a))
    # 主圓
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color if active else DARK)
    # 名字首字
    initial = name[0]
    bbox = draw.textbbox((0, 0), initial, font=bold_font)
    tw = bbox[2] - bbox[0]; th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), initial,
              font=bold_font, fill=WHITE if active else GRAY)
    # 主持人名稱
    bbox2 = draw.textbbox((0, 0), name, font=label_font)
    lw = bbox2[2] - bbox2[0]
    clr = WHITE if active else GRAY
    draw.text((cx - lw // 2, cy + r + 20), name, font=label_font, fill=clr)

def create_podcast_bg(topic_title, bold_path, reg_path, out_path):
    """建立靜態 Podcast 背景圖（1920×1080）"""
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg(img)

    font_brand  = ImageFont.truetype(bold_path, 30)
    font_eyebrow = ImageFont.truetype(reg_path,  32)
    font_title  = ImageFont.truetype(bold_path, 64)
    font_host   = ImageFont.truetype(bold_path, 120)
    font_label  = ImageFont.truetype(bold_path, 42)
    font_small  = ImageFont.truetype(reg_path,  26)

    # 頂部品牌欄
    draw.rectangle([0, 0, W, 72], fill=(12, 18, 36))
    draw.text((50, 20), "欣晨工業有限公司  |  智慧製造深度對談",
              font=font_brand, fill=GRAY)
    draw.text((W - 340, 20), "Hsin-Chan Industrial", font=font_brand, fill=DARK)

    # 主題標題
    draw.rectangle([0, 72, W, 78], fill=ACCENT)
    bbox = draw.textbbox((0, 0), topic_title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 110), topic_title, font=font_title, fill=WHITE)

    # 眉標
    eyebrow = "SMART MANUFACTURING DEEP DIVE"
    bbox2 = draw.textbbox((0, 0), eyebrow, font=font_eyebrow)
    ew = bbox2[2] - bbox2[0]
    draw.text(((W - ew) // 2, 200), eyebrow, font=font_eyebrow, fill=ACCENT_LT)

    # 裝飾分隔線
    draw.rectangle([W//2 - 120, 250, W//2 + 120, 254], fill=ACCENT)

    # 女主持人（左）
    draw_host_avatar(draw, W // 4, 550, 120, FEMALE_CLR, "小欣",
                     font_host, font_label, active=True)

    # 男主持人（右）
    draw_host_avatar(draw, W * 3 // 4, 550, 120, MALE_CLR, "阿晨",
                     font_host, font_label, active=True)

    # 中間 × 符號
    draw.text((W // 2 - 18, 490), "×", font=font_label, fill=GRAY)

    # 底部波形預留區（黑底）
    draw.rectangle([0, H - 180, W, H], fill=(5, 8, 16))
    draw.rectangle([0, H - 182, W, H - 180], fill=ACCENT)

    # 底部公司資訊
    draw.text((50, H - 140), "🌐 hsinchan.com",    font=font_small, fill=GRAY)
    draw.text((50, H - 100), "📞 03-381-4497",     font=font_small, fill=GRAY)
    draw.text((50, H - 60),  "📍 桃園市大園區 · Est. 1996", font=font_small, fill=DARK)

    img.save(out_path)
    print("🖼️  Podcast 背景圖建立完成")

# ── 影片合成 ─────────────────────────────────────────────────────────────────
def render_final_video(bg_path, audio_path, duration, topic_title, out_path):
    """FFmpeg：背景 + 音訊 + showwaves 即時波形 + 字幕"""
    print("🎬 FFmpeg 合成最終影片（含即時波形）...")

    # showwaves 濾鏡：在底部180px區域顯示即時音訊波形
    filter_complex = (
        "[0:v]scale=1920:1080[bg];"
        "[1:a]showwaves=s=1920x170:mode=cline:rate=30:colors=1a3f98|5a8ce0[wave];"
        "[bg][wave]overlay=0:898[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_path),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        "-r", "30",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 失敗：{result.stderr[-1000:]}")
    size = Path(out_path).stat().st_size / 1024 / 1024
    print(f"✅ 影片合成完成：{out_path}（{size:.0f} MB，{duration/60:.1f} 分鐘）")

# ── 上傳 ─────────────────────────────────────────────────────────────────────
def upload_facebook(video_path, topic_title, dialogue):
    token   = os.environ["FB_ACCESS_TOKEN"]
    page_id = os.environ["FB_PAGE_ID"]
    # 從對話取摘要（前後各兩輪）
    intro = dialogue[0]["text"][:100]
    outro = dialogue[-1]["text"][:100]
    caption = (
        f"🎙️ 【智慧製造深度對談】{topic_title}\n\n"
        f"{intro}…\n\n"
        f"本集精彩內容：\n"
        + "\n".join(f"• {d['text'][:40]}…" for d in dialogue[2:8:2])
        + f"\n\n{outro}…\n\n"
        f"#智慧製造 #工業自動化 #欣晨工業 #台灣製造 #豐田生產方式 #TPS #工業4點0"
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
    desc  = caption + "\n\n欣晨工業有限公司 · https://www.hsinchan.com · 03-381-4497"
    tags  = ["智慧製造", "工業自動化", "欣晨工業", "Podcast", topic_tag,
             "TPS", "豐田生產方式", "台灣製造業", "Industry 4.0", "工業4.0"]
    print("📺 上傳至 YouTube...")
    media   = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = yt.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": title, "description": desc,
                          "tags": tags, "categoryId": "28",
                          "defaultLanguage": "zh-TW"},
              "status":  {"privacyStatus": "public",
                          "selfDeclaredMadeForKids": False}},
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
    print("═══════════════════════════════════════════════════")
    print("  欣晨工業 — NotebookLM 風格雙主持人 Podcast 影片")
    print("  主持人：小欣（女）× 阿晨（男）")
    print("═══════════════════════════════════════════════════")

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    if dry_run:
        print("⚠️  DRY RUN 模式\n")

    # 取得今日題材
    topic_title, topic_tag, topic_angle, date_str = get_today_topic()

    # 初始化 API 客戶端
    ac_client  = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    oai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 1. 生成對話腳本
        dialogue = generate_script(topic_title, topic_angle, ac_client)

        # 2. 載入字型 & 建立背景
        bold_path, reg_path = load_fonts()
        bg_path = tmp / "podcast_bg.png"
        create_podcast_bg(topic_title, bold_path, reg_path, bg_path)

        # 3. 生成 TTS 音訊
        segments  = generate_audio_segments(dialogue, oai_client, tmpdir)
        audio_path, duration = concat_audio(segments, silence_ms=450, tmp_dir=tmpdir)

        # 4. 合成影片
        video_path = tmp / f"podcast_{date_str}.mp4"
        render_final_video(bg_path, audio_path, duration, topic_title, video_path)

        if dry_run:
            import shutil
            out = Path(f"hsinchan_podcast_{date_str}.mp4")
            shutil.copy(video_path, out)
            print(f"\n✅ Dry run 完成，影片：{out}（{duration/60:.1f} 分鐘）")
            return

        # 5. 同時上傳 FB + YouTube
        print("\n── 上傳至各平台 ──────────────────────────────────")
        caption = upload_facebook(str(video_path), topic_title, dialogue)
        yt_id   = upload_youtube(str(video_path), topic_title, caption, topic_tag)
        print(f"\n🎉 完成！{date_str} Podcast 影片已發布")
        if yt_id:
            print(f"   YouTube：https://youtu.be/{yt_id}")

if __name__ == "__main__":
    main()
