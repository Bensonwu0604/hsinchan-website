#!/usr/bin/env python3
# trigger: 2026-05-20p
"""
欣晨工業 — Podcast 影片試作版
使用 OpenAI TTS：nova（小欣女聲）× onyx（阿晨男聲）
需要：ANTHROPIC_API_KEY + OPENAI_API_KEY
"""

import os, sys, json, subprocess, tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
from openai import OpenAI
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
    """生成一集約 5-7 分鐘的試作腳本，使用純文字格式（穩健不易出錯）"""
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

請生成一集約 5-7 分鐘的對話，每行一句話，格式如下：
小欣: （說話內容）
阿晨: （說話內容）

要求：
- 共 18-22 個對話輪次
- 每輪 60-90 字，自然口語，繁體中文
- 涵蓋：開場→核心概念→台灣案例→給觀眾的建議→結尾
- 自然提到欣晨工業 1-2 次
- 直接輸出對話，不要 JSON，不要編號，不要其他說明"""

    print("Claude 生成對話腳本...")
    msg = ac_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()

    # 解析「小欣: ...」/ 「阿晨: ...」格式
    dialogue = []
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("小欣:"):
            dialogue.append({"speaker": "Host1", "text": line[3:].strip()})
        elif line.startswith("阿晨:"):
            dialogue.append({"speaker": "Host2", "text": line[3:].strip()})
        elif line.startswith("小欣："):
            dialogue.append({"speaker": "Host1", "text": line[3:].strip()})
        elif line.startswith("阿晨："):
            dialogue.append({"speaker": "Host2", "text": line[3:].strip()})

    if not dialogue:
        raise ValueError(f"無法解析對話格式，原始回應前200字：{raw[:200]}")

    total = sum(len(d["text"]) for d in dialogue)
    print(f"腳本完成：{len(dialogue)} 輪對話，{total} 字（預估 {total//150:.0f} 分鐘）")
    return dialogue

# ── OpenAI TTS 音訊生成 ───────────────────────────────────────────────────────
VOICE_FEMALE = "nova"    # 小欣 — 自然女聲
VOICE_MALE   = "onyx"    # 阿晨 — 沉穩男聲

def generate_all_audio(dialogue, tmp_dir):
    oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    tmp = Path(tmp_dir)
    print(f"生成 {len(dialogue)} 段 OpenAI TTS 音訊...")
    segments = []
    for i, turn in enumerate(dialogue):
        voice = VOICE_FEMALE if turn["speaker"] == "Host1" else VOICE_MALE
        out   = tmp / f"seg_{i:03d}.mp3"
        resp  = oai.audio.speech.create(
            model="tts-1", voice=voice, input=turn["text"], speed=0.95
        )
        resp.stream_to_file(str(out))
        segments.append({"path": str(out), "speaker": turn["speaker"]})
        if (i + 1) % 5 == 0:
            print(f"   {i+1}/{len(dialogue)} 段完成")
    print("OpenAI TTS 音訊生成完成")
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

# ── NotebookLM 風格極簡視覺 ──────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    """線性插值顏色"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_gradient_circle(img, cx, cy, r, color_inner, color_outer):
    """繪製漸層圓形（從內到外）"""
    draw = ImageDraw.Draw(img)
    for dr in range(r, 0, -1):
        t = 1 - dr / r
        c = lerp_color(color_inner, color_outer, t * 0.7)
        draw.ellipse([cx-dr, cy-dr, cx+dr, cy+dr], fill=c)

def text_center(draw, text, font, cx, y, color):
    bb = draw.textbbox((0, 0), text, font=font)
    w = bb[2] - bb[0]
    draw.text((cx - w // 2, y), text, font=font, fill=color)
    return bb[3] - bb[1]

def create_bg(topic_title, bold_path, reg_path, out_path):
    # ── 背景：深色漸層 ──────────────────────────────────────────────────────
    img  = Image.new("RGB", (W, H), (8, 10, 20))
    draw = ImageDraw.Draw(img)

    # 柔和放射光暈（左側紫、右側青）
    for rx2, ry2, rc, color in [
        (W//4, H//2, 500, (80, 40, 160)),     # 左紫
        (W*3//4, H//2, 500, (0, 120, 140)),   # 右青
    ]:
        for radius in range(rc, 0, -8):
            alpha = int(18 * (1 - radius / rc))
            c = tuple(min(255, v + alpha) for v in color)
            draw.ellipse([rx2-radius, ry2-radius, rx2+radius, ry2+radius],
                         fill=tuple(min(255, b + alpha//4) for b in (8,10,20)))

    # ── 字型 ────────────────────────────────────────────────────────────────
    f_show    = ImageFont.truetype(reg_path,  28)
    f_label   = ImageFont.truetype(reg_path,  26)
    f_title   = ImageFont.truetype(bold_path, 72)
    f_sub     = ImageFont.truetype(reg_path,  34)
    f_initial = ImageFont.truetype(bold_path, 110)
    f_name    = ImageFont.truetype(bold_path, 38)
    f_role    = ImageFont.truetype(reg_path,  26)
    f_bottom  = ImageFont.truetype(reg_path,  24)

    CX = W // 2   # 水平中心

    # ── 頂部節目標識 ────────────────────────────────────────────────────────
    show_text = "欣晨工業  智慧製造深度對談"
    text_center(draw, show_text, f_show, CX, 52, (120, 140, 170))

    # 細分隔線
    draw.rectangle([CX-200, 98, CX+200, 100], fill=(40, 55, 90))

    # ── 主題標題 ─────────────────────────────────────────────────────────────
    # 換行處理
    words = list(topic_title)
    lines, cur = [], ""
    for ch in words:
        test = cur + ch
        bb = draw.textbbox((0,0), test, font=f_title)
        if bb[2]-bb[0] > W-200 and cur:
            lines.append(cur); cur = ch
        else:
            cur = test
    if cur: lines.append(cur)

    ty = 130
    for line in lines:
        text_center(draw, line, f_title, CX, ty, (240, 244, 250))
        bb = draw.textbbox((0,0), line, font=f_title)
        ty += (bb[3]-bb[1]) + 8

    # 副標
    text_center(draw, "SMART MANUFACTURING DEEP DIVE", f_sub, CX, ty + 12,
                (70, 100, 160))

    # ── 雙主持人圓形頭像 ──────────────────────────────────────────────────────
    AVG_Y   = 620    # 圓心 Y
    R       = 145    # 半徑
    H1_X    = W // 2 - 260   # 小欣 X
    H2_X    = W // 2 + 260   # 阿晨 X

    # 外發光環
    for host_cx, glow_c in [(H1_X, (100, 60, 200)), (H2_X, (0, 150, 160))]:
        for gr in range(R+60, R+2, -4):
            t = 1 - (gr - R - 2) / 58
            gc = tuple(min(255, int(v * t * 0.35)) for v in glow_c)
            draw.ellipse([host_cx-gr, AVG_Y-gr, host_cx+gr, AVG_Y+gr], fill=gc)

    # 小欣漸層圓（紫→藍）
    draw_gradient_circle(img, H1_X, AVG_Y, R, (130, 80, 255), (60, 100, 230))
    # 阿晨漸層圓（青→藍）
    draw_gradient_circle(img, H2_X, AVG_Y, R, (0, 200, 180), (30, 100, 200))

    draw2 = ImageDraw.Draw(img)

    # 首字
    for host_cx, initial in [(H1_X, "欣"), (H2_X, "晨")]:
        bb = draw2.textbbox((0,0), initial, font=f_initial)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        draw2.text((host_cx - tw//2, AVG_Y - th//2 - 10), initial,
                   font=f_initial, fill=(255, 255, 255, 220))

    # 名字與角色
    for host_cx, name, role in [
        (H1_X, "小欣", "女主持人"),
        (H2_X, "阿晨", "男主持人"),
    ]:
        nh = text_center(draw2, name, f_name, host_cx, AVG_Y + R + 22,
                         (240, 244, 250))
        text_center(draw2, role, f_role, host_cx, AVG_Y + R + 22 + nh + 6,
                    (100, 120, 150))

    # 中間 × 符號
    text_center(draw2, "x", f_sub, CX, AVG_Y - 20, (45, 60, 90))

    # ── 底部資訊欄（波形預留區上方）────────────────────────────────────────
    info_y = H - 200
    draw2.rectangle([0, info_y, W, info_y + 1], fill=(25, 35, 65))
    text_center(draw2, "Hsin-Chan Industrial Co., Ltd.  ·  hsinchan.com  ·  03-381-4497",
                f_bottom, CX, info_y + 14, (55, 70, 100))

    # 波形區底色
    draw2.rectangle([0, H-165, W, H], fill=(5, 7, 15))
    draw2.rectangle([0, H-167, W, H-165], fill=(35, 55, 110))

    img.save(out_path)
    print("NotebookLM 風格背景圖建立完成（1920x1080）")

# ── FFmpeg 合成最終影片 ───────────────────────────────────────────────────────
def render_video(bg_path, audio_path, duration, out_path):
    print("🎬 FFmpeg 合成影片（底部即時波形）...")
    fc = (
        "[0:v]scale=1920:1080[bg];"
        "[1:a]showwaves=s=1920x160:mode=cline:rate=30"
        ":colors=7B48FF|00C8B4[wave];"
        "[bg][wave]overlay=0:915[vout]"
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
    print("=" * 55)
    print("  欣晨工業 Podcast — NotebookLM 風格")
    print("  小欣 (nova) x 阿晨 (onyx) | OpenAI TTS")
    print("=" * 55 + "\n")

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

        # 3. gTTS 音訊生成
        segments = generate_all_audio(dialogue, tmpdir)
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
    import traceback
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)
