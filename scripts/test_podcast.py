#!/usr/bin/env python3
# trigger: 2026-05-20c
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

def draw_topic_icon_simple(draw, cx, cy, color, size=100):
    """簡易主題圖示（工廠符號）"""
    s = size
    draw.rectangle([cx-s//2, cy-s//3, cx+s//2, cy+s//3], outline=color, width=5)
    draw.polygon([(cx-s//2-10, cy-s//3), (cx, cy-s*0.7), (cx+s//2+10, cy-s//3)], outline=color, width=5)
    draw.rectangle([cx-14, cy-s//3+18, cx+14, cy+s//3], fill=color)

def draw_avatar_v2(draw, cx, cy, r, color, initial, role, name, f_big, f_role, f_name):
    for ring in range(r+38, r+2, -3):
        t = 1 - (ring-r-2)/36
        c = tuple(min(255, int(v*t*0.5)) for v in color)
        draw.ellipse([cx-ring, cy-ring, cx+ring, cy+ring], outline=c)
    for dr in range(r, 0, -4):
        ratio = 1 - dr/r
        rc = tuple(min(255, int(c + (255-c)*ratio*0.15)) for c in color)
        draw.ellipse([cx-dr, cy-dr, cx+dr, cy+dr], fill=rc)
    bb = draw.textbbox((0,0), initial, font=f_big)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx-tw//2, cy-th//2-8), initial, font=f_big, fill=WHITE)
    bb2 = draw.textbbox((0,0), role, font=f_role)
    rw = bb2[2]-bb2[0]+20; rh = bb2[3]-bb2[1]+10
    draw.rounded_rectangle([cx-rw//2, cy+r+16, cx+rw//2, cy+r+16+rh], radius=6, fill=color)
    draw.text((cx-rw//2+10, cy+r+21), role, font=f_role, fill=WHITE)
    bb3 = draw.textbbox((0,0), name, font=f_name)
    nw = bb3[2]-bb3[0]
    draw.text((cx-nw//2, cy+r+16+rh+8), name, font=f_name, fill=GRAY)

def create_bg(topic_title, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # 漸層底色
    for y in range(H):
        ratio = y / H
        r = int(8 + 10 * ratio); g = int(12 + 16 * ratio); b = int(22 + 33 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(22, 35, 65))
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(22, 35, 65))

    COL1, COL2 = 560, 1360
    draw.rectangle([0, 0, W, 64], fill=(8, 14, 28))
    draw.rectangle([0, 64, W, 70], fill=ACCENT)
    draw.rectangle([COL1, 70, COL1+2, H-172], fill=(30, 48, 90))
    draw.rectangle([COL2, 70, COL2+2, H-172], fill=(30, 48, 90))

    f_brand   = ImageFont.truetype(bold_path, 26)
    f_ep      = ImageFont.truetype(reg_path,  24)
    f_title_l = ImageFont.truetype(bold_path, 50)
    f_stat    = ImageFont.truetype(bold_path, 28)
    f_init    = ImageFont.truetype(bold_path, 96)
    f_role    = ImageFont.truetype(bold_path, 28)
    f_name    = ImageFont.truetype(reg_path,  26)
    f_vs      = ImageFont.truetype(bold_path, 44)
    f_badge   = ImageFont.truetype(reg_path,  22)
    f_sec     = ImageFont.truetype(bold_path, 30)
    f_bullet  = ImageFont.truetype(reg_path,  26)
    f_company = ImageFont.truetype(bold_path, 28)
    f_comp_s  = ImageFont.truetype(reg_path,  22)
    f_bottom  = ImageFont.truetype(reg_path,  26)

    # 頂部
    draw.text((44, 17), "欣晨工業有限公司", font=f_brand, fill=WHITE)
    draw.text((314, 19), "智慧製造深度對談  ·  SMART MANUFACTURING DEEP DIVE", font=f_ep, fill=GRAY)
    trial_text = "試作版  Edge TTS"
    bb_tr = draw.textbbox((0,0), trial_text, font=f_ep)
    draw.text((W-(bb_tr[2]-bb_tr[0])-44, 19), trial_text, font=f_ep, fill=ACCENT_LT)

    # 左欄
    icon_cx = COL1 // 2
    draw_topic_icon_simple(draw, icon_cx, 255, (60, 200, 120), 105)
    title_lines = wrap_cjk(draw, topic_title, f_title_l, COL1-60)
    ty = 400
    for line in title_lines:
        bb = draw.textbbox((0,0), line, font=f_title_l)
        lw = bb[2]-bb[0]
        draw.text((max(30, icon_cx-lw//2), ty), line, font=f_title_l, fill=WHITE)
        ty += (bb[3]-bb[1]) + 8
    for stat_text in ["豐田生產方式 TPS", "Kaizen / JIT / Jidoka", "現地現物 現場哲學"]:
        draw.rounded_rectangle([30, ty+10, COL1-30, ty+58], radius=8, fill=(14, 22, 46))
        draw.rounded_rectangle([30, ty+10, 36, ty+58], radius=4, fill=(60, 200, 120))
        draw.text((50, ty+22), stat_text, font=f_stat, fill=WHITE)
        ty += 68

    # 中欄
    mid_cx = (COL1 + COL2) // 2
    h1_cx  = COL1 + (COL2-COL1)//4
    h2_cx  = COL1 + (COL2-COL1)*3//4

    badge_txt = "試作版  Edge TTS 台灣神經語音"
    bb_b = draw.textbbox((0,0), badge_txt, font=f_badge)
    bw = bb_b[2]-bb_b[0]+28; bh = bb_b[3]-bb_b[1]+14
    bx = mid_cx - bw//2
    draw.rounded_rectangle([bx, 88, bx+bw, 88+bh], radius=8, fill=(20, 36, 80))
    draw.rounded_rectangle([bx, 88, bx+bw, 90], radius=1, fill=ACCENT_LT)
    draw.text((bx+14, 95), badge_txt, font=f_badge, fill=ACCENT_LT)

    f_ch = ImageFont.truetype(bold_path, 36)
    bb_ch = draw.textbbox((0,0), "智慧製造深度對談", font=f_ch)
    draw.text((mid_cx-(bb_ch[2]-bb_ch[0])//2, 128), "智慧製造深度對談", font=f_ch, fill=WHITE)

    draw_avatar_v2(draw, h1_cx, 490, 108, FEMALE_CLR, "欣", "女主持人", "小欣", f_init, f_role, f_name)
    draw_avatar_v2(draw, h2_cx, 490, 108, MALE_CLR,   "晨", "男主持人", "阿晨", f_init, f_role, f_name)
    bb_vs = draw.textbbox((0,0), "×", font=f_vs)
    draw.text((mid_cx-(bb_vs[2]-bb_vs[0])//2, 462), "×", font=f_vs, fill=(40, 60, 100))

    # 右欄
    rx = COL2 + 36; rw = W - COL2 - 60
    draw.text((rx, 90), "本集重點", font=f_sec, fill=ACCENT_LT)
    draw.rectangle([rx, 128, rx+50, 132], fill=ACCENT)
    by2 = 148
    for bullet in ["· 改善文化核心概念", "· 七大浪費與消除方法", "· Poka-yoke 防呆設計", "· 台灣工廠實際案例", "· 欣晨工業 TPS 實踐"]:
        for line in wrap_cjk(draw, bullet, f_bullet, rw):
            draw.text((rx, by2), line, font=f_bullet, fill=GRAY)
            bb = draw.textbbox((0,0), line, font=f_bullet)
            by2 += (bb[3]-bb[1]) + 6
        by2 += 4

    company_y = H - 330
    draw.rounded_rectangle([rx-6, company_y, W-24, H-186], radius=10, fill=(12, 20, 40))
    draw.rounded_rectangle([rx-6, company_y, rx-2, H-186], radius=4, fill=ACCENT)
    draw.text((rx+10, company_y+14), "欣晨工業有限公司", font=f_company, fill=WHITE)
    draw.text((rx+10, company_y+50), "Hsin-Chan Industrial Co., Ltd.", font=f_comp_s, fill=GRAY)
    iy = company_y + 86
    for icon, text in [("📞", "03-381-4497"), ("🌐", "www.hsinchan.com"), ("📅", "Est. 1975 · 51年製造")]:
        draw.text((rx+10, iy), f"{icon}  {text}", font=f_comp_s, fill=GRAY); iy += 34

    # 底部
    draw.rectangle([0, H-172, W, H], fill=(5, 8, 16))
    draw.rectangle([0, H-175, W, H-172], fill=ACCENT)
    bottom_text = "🎙  小欣 × 阿晨  ·  每3天更新  ·  智慧製造深度對談"
    bb_bot = draw.textbbox((0,0), bottom_text, font=f_bottom)
    draw.text(((W-(bb_bot[2]-bb_bot[0]))//2, H-138), bottom_text, font=f_bottom, fill=GRAY)

    img.save(out_path)
    print("🖼️  三欄式 Podcast 背景圖建立完成（1920×1080）")

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
        topic = "改善文化 × 豐田哲學 × 台灣製造"
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
