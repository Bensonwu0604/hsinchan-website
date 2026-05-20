#!/usr/bin/env python3
"""
欣晨工業 — Podcast 影片試作版
使用 Edge TTS（微軟免費神經語音，不需額外 API Key）
女聲：zh-TW-HsiaoChenNeural（小欣）
男聲：zh-TW-YunJheNeural（阿晨）
只需 ANTHROPIC_API_KEY 即可試作完整影片
"""

import os, sys, json, subprocess, asyncio, tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
import edge_tts
from PIL import Image, ImageDraw, ImageFont

# ── 視覺常數（同正式版）──────────────────────────────────────────────────────
W, H         = 1920, 1080
BG           = (8,  12,  22)
SURFACE      = (14, 22,  42)
ACCENT       = (26, 63, 152)
ACCENT_LT    = (90, 140, 230)
FEMALE_CLR   = (220, 80, 130)
MALE_CLR     = (50, 160, 220)
WHITE        = (240, 244, 248)
GRAY         = (120, 140, 168)
DARK         = (30, 40, 60)

VOICE_FEMALE = "zh-TW-HsiaoChenNeural"   # Edge TTS 台灣女聲
VOICE_MALE   = "zh-TW-YunJheNeural"      # Edge TTS 台灣男聲

# ── 字型 ─────────────────────────────────────────────────────────────────────
def load_fonts():
    bold_candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    ]
    reg_candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ]
    bold = next((p for p in bold_candidates if Path(p).exists()), None)
    reg  = next((p for p in reg_candidates  if Path(p).exists()), None)
    if not bold:
        raise FileNotFoundError("找不到 CJK 字型，請安裝 fonts-noto-cjk")
    return bold, reg or bold

# ── Claude 生成對話腳本 ────────────────────────────────────────────────────────
def generate_script(ac_client):
    """生成一集約 5-7 分鐘的試作腳本（縮短版，節省測試時間）"""
    prompt = """你是欣晨工業有限公司的 Podcast 製作人，製作「智慧製造深度對談」試作集。

主持人：
- 小欣（女）：活潑好奇，善於提問，代表觀眾視角
- 阿晨（男）：資深工程師，深入解說，提供數據與案例
名字取自「欣晨工業」，自然融入品牌識別。

今集主題：豐田改善文化（Kaizen）在台灣製造業的實踐

欣晨工業背景（自然融入，不過度推銷）：
- 台灣桃園，1975年創立，51年精密製造經驗
- 核心哲學：豐田生產方式 TPS（Kaizen/JIT/Jidoka）
- 服務：機械手臂整合、AOI視覺檢測、工業加熱器、熱電偶

請生成一集約 5-7 分鐘的對話（試作版），輸出 JSON 陣列：
[
  {"speaker": "小欣", "text": "開場白..."},
  {"speaker": "阿晨", "text": "專業解說..."},
  ...
]

要求：
- 共 18-22 個對話輪次
- 每輪 60-90 字，自然口語，繁體中文
- 涵蓋：開場→核心概念→台灣案例→給觀眾的建議→結尾
- 自然提到欣晨工業 1-2 次
- 只輸出 JSON，不要其他說明"""

    print("🤖 Claude 生成對話腳本...")
    msg = ac_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:])
        if raw.rstrip().endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
    dialogue = json.loads(raw.strip())
    total = sum(len(d["text"]) for d in dialogue)
    print(f"✅ 腳本完成：{len(dialogue)} 輪對話，{total} 字（預估 {total//150:.0f} 分鐘）")
    return dialogue

# ── Edge TTS 音訊生成 ─────────────────────────────────────────────────────────
async def tts_one(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save(str(out_path))

async def generate_all_audio(dialogue, tmp_dir):
    tmp = Path(tmp_dir)
    print(f"🔊 生成 {len(dialogue)} 段 Edge TTS 音訊（免費神經語音）...")
    segments = []
    for i, turn in enumerate(dialogue):
        speaker = turn["speaker"]
        voice   = VOICE_FEMALE if speaker == "小欣" else VOICE_MALE
        out     = tmp / f"seg_{i:03d}.mp3"
        await tts_one(turn["text"], voice, out)
        segments.append({"path": str(out), "speaker": speaker})
        if (i + 1) % 5 == 0:
            print(f"   {i+1}/{len(dialogue)} 段完成")
    print("✅ TTS 音訊完成")
    return segments

def concat_audio(segments, tmp_dir):
    tmp = Path(tmp_dir)

    # 建立靜音段
    silence = tmp / "silence.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", "0.45", "-q:a", "9", "-acodec", "libmp3lame", str(silence)],
        capture_output=True, check=True
    )

    # Concat list
    list_file = tmp / "concat.txt"
    with open(list_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg['path']}'\n")
            f.write(f"file '{silence}'\n")

    full = tmp / "full_audio.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-c", "copy", str(full)],
        capture_output=True, check=True
    )

    # 取得時長
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(full)],
        capture_output=True, text=True
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    print(f"✅ 音訊拼接完成：{duration/60:.1f} 分鐘")
    return str(full), duration

# ── Podcast 視覺背景 ──────────────────────────────────────────────────────────
def draw_bg_gradient(img):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = BG[0] + (SURFACE[0] - BG[0]) * y // H
        g = BG[1] + (SURFACE[1] - BG[1]) * y // H
        b = BG[2] + (SURFACE[2] - BG[2]) * y // H
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    for x in range(0, W, 72):
        draw.line([(x, 0), (x, H)], fill=(20, 32, 60))
    for y in range(0, H, 72):
        draw.line([(0, y), (W, y)], fill=(20, 32, 60))

def draw_avatar(draw, cx, cy, r, color, initial, name, font_init, font_name):
    # 光暈
    for ring in range(r + 28, r, -3):
        a = int(50 * (1 - (ring - r) / 28))
        draw.ellipse([cx-ring, cy-ring, cx+ring, cy+ring], outline=(*color[:3],))
    # 主圓
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
    # 首字
    bb = draw.textbbox((0, 0), initial, font=font_init)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx - tw//2, cy - th//2), initial, font=font_init, fill=WHITE)
    # 名稱
    bb2 = draw.textbbox((0, 0), name, font=font_name)
    nw = bb2[2] - bb2[0]
    draw.text((cx - nw//2, cy + r + 22), name, font=font_name, fill=WHITE)

def create_bg(topic_title, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    f_brand   = ImageFont.truetype(bold_path, 28)
    f_eyebrow = ImageFont.truetype(reg_path,  30)
    f_title   = ImageFont.truetype(bold_path, 60)
    f_init    = ImageFont.truetype(bold_path, 110)
    f_name    = ImageFont.truetype(bold_path, 40)
    f_tag     = ImageFont.truetype(reg_path,  26)
    f_small   = ImageFont.truetype(reg_path,  24)

    # 品牌頂欄
    draw.rectangle([0, 0, W, 68], fill=(10, 16, 30))
    draw.text((48, 18), "欣晨工業有限公司  智慧製造深度對談", font=f_brand, fill=GRAY)
    draw.text((W-320, 18), "Hsin-Chan Industrial", font=f_brand, fill=(30, 48, 80))

    # 藍色分隔線
    draw.rectangle([0, 68, W, 74], fill=ACCENT)

    # 主題標題
    bb = draw.textbbox((0,0), topic_title, font=f_title)
    tw = bb[2]-bb[0]
    draw.text(((W-tw)//2, 105), topic_title, font=f_title, fill=WHITE)

    # 眉標
    eyebrow = "SMART MANUFACTURING DEEP DIVE  ·  PODCAST"
    bb2 = draw.textbbox((0,0), eyebrow, font=f_eyebrow)
    ew = bb2[2]-bb2[0]
    draw.text(((W-ew)//2, 185), eyebrow, font=f_eyebrow, fill=ACCENT_LT)

    # 裝飾線
    draw.rectangle([(W//2-100), 232, (W//2+100), 236], fill=ACCENT)

    # 試作標籤
    badge = "  試作版  Edge TTS  "
    bb3 = draw.textbbox((0,0), badge, font=f_tag)
    bw, bh = bb3[2]-bb3[0]+20, bb3[3]-bb3[1]+12
    draw.rounded_rectangle([W//2-bw//2, 248, W//2+bw//2, 248+bh], radius=6, fill=(40, 60, 100))
    draw.text((W//2-bw//2+10, 252), badge.strip(), font=f_tag, fill=ACCENT_LT)

    # 主持人頭像
    draw_avatar(draw, W//4, 570, 115, FEMALE_CLR, "欣", "小欣", f_init, f_name)
    draw_avatar(draw, W*3//4, 570, 115, MALE_CLR,   "晨", "阿晨", f_init, f_name)

    # 中間 × 符號
    bb4 = draw.textbbox((0,0), "×", font=f_name)
    xw = bb4[2]-bb4[0]
    draw.text((W//2-xw//2, 540), "×", font=f_name, fill=GRAY)

    # 底部音波區
    draw.rectangle([0, H-175, W, H], fill=(5, 8, 16))
    draw.rectangle([0, H-178, W, H-175], fill=ACCENT)

    # 底部資訊
    draw.text((48, H-140), "🌐  www.hsinchan.com",    font=f_small, fill=GRAY)
    draw.text((48, H-105), "📞  03-381-4497",          font=f_small, fill=GRAY)
    draw.text((48, H-68),  "📍  桃園市大園區 · Est. 1975 · 51年精密製造", font=f_small, fill=(40, 55, 80))

    img.save(out_path)
    print("🖼️  背景圖建立完成（1920×1080）")

# ── FFmpeg 合成最終影片 ───────────────────────────────────────────────────────
def render_video(bg_path, audio_path, duration, out_path):
    print("🎬 FFmpeg 合成影片（底部即時波形）...")
    fc = (
        "[0:v]scale=1920:1080[bg];"
        "[1:a]showwaves=s=1920x165:mode=cline:rate=30:colors=1a3f98|5a8ce0[wave];"
        "[bg][wave]overlay=0:902[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_path),
        "-i",    str(audio_path),
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration), "-r", "30",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 失敗：\n{result.stderr[-800:]}")
    size = Path(out_path).stat().st_size / 1024 / 1024
    print(f"✅ 影片合成完成：{size:.0f} MB，{duration/60:.1f} 分鐘")

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    print("═══════════════════════════════════════════════════")
    print("  欣晨工業 — Podcast 影片試作版")
    print("  主持人：小欣 × 阿晨  |  Edge TTS（免費神經語音）")
    print("═══════════════════════════════════════════════════\n")

    tw   = datetime.now(timezone(timedelta(hours=8)))
    date = tw.strftime("%Y-%m-%d")

    ac = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 1. 生成腳本
        dialogue = generate_script(ac)

        # 印出腳本預覽
        print("\n── 對話腳本預覽（前5輪）──────────────────────────")
        for turn in dialogue[:5]:
            print(f"[{turn['speaker']}] {turn['text'][:60]}…")
        print("──────────────────────────────────────────────────\n")

        # 2. 字型 & 背景
        bold_path, reg_path = load_fonts()
        bg_path = tmp / "bg.png"
        topic   = "改善文化 × 豐田哲學 × 台灣製造"
        create_bg(topic, bold_path, reg_path, bg_path)

        # 3. TTS 音訊（async）
        segments = asyncio.run(generate_all_audio(dialogue, tmpdir))
        audio_path, duration = concat_audio(segments, tmpdir)

        # 4. 合成影片
        video_out = tmp / f"test_podcast_{date}.mp4"
        render_video(bg_path, audio_path, duration, video_out)

        # 複製到工作目錄（供 artifact 上傳）
        import shutil
        final = Path(f"test_podcast_{date}.mp4")
        shutil.copy(video_out, final)
        print(f"\n🎉 試作影片完成：{final}")
        print(f"   時長：{duration/60:.1f} 分鐘")
        print(f"   檔案大小：{final.stat().st_size/1024/1024:.0f} MB")
        print("\n✅ 請至 GitHub Actions → Artifacts 下載 'test-podcast-video'")

if __name__ == "__main__":
    main()
