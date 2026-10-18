#!/usr/bin/env python3
"""
欣晨工業 — 智慧製造 10-13 分鐘深度解析長片自動發布（FB + YouTube）
流程：Claude 生成第一性原理腳本 → OpenAI TTS 旁白配音 → Pillow 繪製畫面
      → FFmpeg 逐段合成（Ken Burns 效果）→ 串接 → 上傳 Facebook + YouTube
"""

import os, sys, json, base64, subprocess, tempfile, textwrap, math, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
import requests
from PIL import Image, ImageDraw, ImageFont, ImageChops
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

# ── 設計常數 ────────────────────────────────────────────────────────────────
W, H       = 1920, 1080            # 16:9 長片格式
BG         = (10,  13,  21)        # 深底色
SURFACE    = (16,  24,  48)        # 稍亮底色（slide body）
ACCENT     = (26,  63, 152)        # 欣晨藍
ACCENT_LT  = (90, 140, 230)        # 淺藍（強調文字）
WHITE      = (240, 244, 248)
GRAY       = (138, 155, 174)
DARK_GRAY  = (55,  70,  90)

VIDEO_FPS  = 30
CLIP_FADE  = 0.4    # 每段片頭尾淡入淡出秒數
ZOOM_END   = 1.04   # 每段緩慢放大至 104%（Ken Burns 效果）
                    # 放大是置中裁切：1.08 會把 80px 版面邊距吃到剩約 10px，
                    # 文字幾乎貼邊、還可能被平台 UI 蓋住；1.04 可保留約 45px。
DIALOGUE_GAP = 0.25 # 雙主持人對話間停頓秒數
TTS_RETRIES  = 4    # 單句配音失敗重試次數
TTS_BACKOFF  = 3    # 重試退避基數（秒）
SCRIPT_RETRIES = 3  # 腳本生成/驗證失敗重試次數
SCRIPT_MODEL = os.environ.get("SCRIPT_MODEL", "claude-opus-5-5")

# ── 片長控制（目標 10-13 分鐘）──────────────────────────────────────────────
TARGET_MIN_SEC = 10 * 60      # 成片下限
TARGET_MAX_SEC = 13 * 60      # 成片上限
TARGET_MID_SEC = 11.5 * 60    # 微調時瞄準的中心值
# 腳本階段的粗估語速（字/秒）。只用來決定「要不要請 Claude 重寫」，
# 真正的片長微調是依據配音後量到的實際秒數，所以這個常數不準也不會失準。
CHARS_PER_SEC  = 4.6
SCRIPT_EST_MIN = 9 * 60       # 粗估低於此值就請 Claude 加長
SCRIPT_EST_MAX = 14.5 * 60    # 粗估高於此值就請 Claude 縮短
MAX_RATE_ADJ   = 15           # 語速調整上限 ±15%（再多就不自然）

# tts-1-hd 比 tts-1 貴一倍，但整支影片也只差約 $0.04，為成片品質值得
TTS_MODEL = os.environ.get("TTS_MODEL", "tts-1-hd")
TTS_SPEED = float(os.environ.get("TTS_SPEED", "1.0"))
HOST_VOICES = {
    "A": os.environ.get("HOST_A_VOICE", "onyx"),   # 男主持人：低沉
    "B": os.environ.get("HOST_B_VOICE", "nova"),   # 女主持人：明亮
}
HOST_LABELS = {"A": "主持人 A", "B": "主持人 B"}

ICON_KEYS = ["gear", "sensor", "chip", "heat", "data", "network",
             "check", "warning", "cycle", "robot", "idea", "factory"]

GLOW_SIZE  = 1100                  # 左上角光暈直徑
GLOW_PEAK  = 70                    # 光暈中心最大不透明度（0-255）

# ── 圖文素材 ────────────────────────────────────────────────────────────────
# workflow 以 working-directory: scripts 執行，所以用檔案位置回推 repo 根目錄
PHOTO_DIR = Path(__file__).resolve().parent.parent / "photo"
# kind=photo 直接做暗化藍調處理；kind=cad 是綠幕 CAD 圖，去背後轉成藍色線框
ASSETS = {
    "ev_line":  {"file": "ev-factory.webp",     "kind": "photo", "desc": "電動車產線：機械手臂與電池裝配"},
    "semi_fab": {"file": "semi-factory.webp",   "kind": "photo", "desc": "半導體無塵室：晶圓與製程監控"},
    "kaizen":   {"file": "kaizen-factory.webp", "kind": "photo", "desc": "豐田改善看板：TPS 精實現場"},
    "station":  {"file": "ST01.webp",           "kind": "cad",   "desc": "自動化工作站設計圖"},
    "gripper":  {"file": "Robot夾具.webp",       "kind": "cad",   "desc": "機械手臂夾具設計圖"},
}
ASSET_KEYS = list(ASSETS)

# ── AI 生圖（依每個 beat 的內容生成專屬畫面）────────────────────────────────
IMAGE_MODEL   = os.environ.get("IMAGE_MODEL", "gpt-image-2")
# low 便宜但畫質撐不起成片，high 每支要 $4+；medium 是這個用途的合理點
IMAGE_QUALITY = os.environ.get("IMAGE_QUALITY", "low")
IMAGE_RETRIES = 3
# gpt-image-2 只支援 1024x1024 / 1024x1536 / 1536x1024，
# 版位需要的 16:9 與 4:5 由繪圖層滿版裁切補足
IMAGE_SIZES = {"16:9": "1536x1024", "4:5": "1024x1536"}
# 全片共用的風格指令：生圖最大的風險是每張調性不一，整支影片會散掉
IMAGE_STYLE = (
    "Cinematic photographic style, dark moody industrial setting, near-black background, "
    "deep blue color grading with a single cool blue accent light, high contrast, "
    "shallow depth of field, no text, no words, no letters, no logos, no watermarks, "
    "photorealistic, shot on a full-frame camera, 35mm lens."
)
_asset_cache = {}

SERIES_NAME_ZH = "第一性拆解製造"
SERIES_NAME_EN = "FIRST PRINCIPLES MFG"

# ── 字型 ────────────────────────────────────────────────────────────────────
def load_fonts():
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "C:/Windows/Fonts/msjhbd.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_reg = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "C:/Windows/Fonts/msjh.ttc",
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

def draw_wrapped(draw, text, font, x, y, max_width, fill, line_spacing=1.35, dry=False):
    """畫出換行文字並回傳結束的 y；dry=True 只量高度不落筆（用於版面置中計算）"""
    lines = wrap_text(draw, text, font, max_width)
    cy = y
    for line in lines:
        if not dry:
            draw.text((x, cy), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        cy += int((bbox[3] - bbox[1]) * line_spacing)
    return cy

# ── 繪製函數 ─────────────────────────────────────────────────────────────────
def generate_beat_image(prompt, aspect, out_path):
    """依該段台詞的畫面描述生成一張圖；失敗回傳 None，交由本地素材接手"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    full_prompt = "\n\n".join([prompt.strip(), IMAGE_STYLE])
    last_err = None
    for attempt in range(1, IMAGE_RETRIES + 1):
        try:
            resp = client.images.generate(
                model=IMAGE_MODEL,
                prompt=full_prompt,
                size=IMAGE_SIZES.get(aspect, "1024x1024"),
                quality=IMAGE_QUALITY,
                n=1,
            )
            b64 = resp.data[0].b64_json
            if b64:
                Path(out_path).write_bytes(base64.b64decode(b64))
                return out_path
            last_err = "回應中沒有影像資料"
        except Exception as e:                      # noqa: BLE001
            last_err = e
        if attempt < IMAGE_RETRIES:
            time.sleep(2 * attempt)
    print(f"   ⚠️  生圖失敗，改用本地素材：{last_err}")
    return None

def load_generated_image(path):
    """生成圖也要壓暗偏藍，才能和整體深色設計同調"""
    src = Image.open(path).convert("RGB")
    tinted = _tint_by_luminance(src, (6, 9, 18), (120, 165, 225), 120)
    out = Image.blend(src, tinted, 0.48).convert("RGBA")
    return Image.blend(Image.new("RGB", src.size, BG).convert("RGBA"), out, 0.84)

def _chroma_key_alpha(img):
    """綠幕去背：綠底從飽和綠一路褪成近白，固定門檻會漏，改用綠偏移判定

    背景條件 g > r+6 且 g > b-2；CAD 模型本身是中性灰（g-r≈0）故不會被誤殺。
    """
    r, g, b = img.split()
    is_greener_than_red  = ImageChops.subtract(g, r).point(lambda v: 255 if v > 6 else 0)
    is_not_bluer_than_g  = ImageChops.subtract(b, g).point(lambda v: 255 if v < 2 else 0)
    background = ImageChops.multiply(is_greener_than_red, is_not_bluer_than_g)
    return ImageChops.invert(background)

def _tint_by_luminance(img, shadow_rgb, light_rgb, lift):
    """依灰階把圖重新上色成品牌藍調

    輸出顏色只跟亮度有關，所以可以直接對灰階圖做 LUT，不需要 numpy。
    """
    lum = img.convert("L")
    channels = []
    for c in range(3):
        lut = [
            max(0, min(255, int(
                shadow_rgb[c] + (light_rgb[c] - shadow_rgb[c]) * (1 - v / 255) * 1.5 + (v / 255) * lift
            )))
            for v in range(256)
        ]
        channels.append(lum.point(lut))
    return Image.merge("RGB", channels)

def load_asset(key):
    """載入並處理素材，回傳 RGBA（結果快取，一支影片會重複用到同一張）"""
    if key in _asset_cache:
        return _asset_cache[key]
    meta = ASSETS.get(key) or ASSETS[ASSET_KEYS[0]]
    src  = Image.open(PHOTO_DIR / meta["file"]).convert("RGB")

    if meta["kind"] == "cad":
        alpha = _chroma_key_alpha(src)
        tinted = _tint_by_luminance(src, BG, ACCENT_LT, 70)
        out = Image.merge("RGBA", (*tinted.split(), alpha))
        out = out.crop(out.getbbox())           # 裁掉去背後周圍的空白
    else:
        # 實拍照壓暗並偏藍，讓文字與品牌色仍是畫面主角
        tinted = _tint_by_luminance(src, (6, 9, 18), (120, 165, 225), 120)
        out = Image.blend(src, tinted, 0.55).convert("RGBA")
        out = Image.blend(Image.new("RGB", src.size, BG).convert("RGBA"), out, 0.78)

    _asset_cache[key] = out
    return out

def _edge_fade_mask(size, fade_px):
    """左緣淡出遮罩，讓照片自然融進深色底，不留硬邊"""
    w, h = size
    mask = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(mask)
    for x in range(min(fade_px, w)):
        md.line([(x, 0), (x, h)], fill=int(255 * (x / fade_px) ** 1.5))
    return mask

def _resolve_visual(key, image_path):
    """優先用當集生成的圖，沒有就退回 repo 內的本地素材"""
    if image_path and Path(image_path).exists():
        return load_generated_image(image_path), "photo"
    return load_asset(key), ASSETS.get(key, {}).get("kind", "photo")

def draw_asset_panel(img, key, x0, fade_px=260, image_path=None):
    """把素材鋪在畫面右側：實拍／生成圖做滿版裁切並左緣淡出，CAD 置中擺放"""
    asset, kind = _resolve_visual(key, image_path)
    pw, ph = W - x0, H
    if kind == "cad":
        fitted = asset.copy()
        fitted.thumbnail((int(pw * 0.82), int(ph * 0.62)), Image.LANCZOS)
        px = x0 + (pw - fitted.width) // 2
        py = (ph - fitted.height) // 2
        img.paste(fitted, (px, py), fitted)
        return

    scale = max(pw / asset.width, ph / asset.height)
    fitted = asset.resize((max(int(asset.width * scale), pw), max(int(asset.height * scale), ph)), Image.LANCZOS)
    left = (fitted.width - pw) // 2
    top  = (fitted.height - ph) // 2
    fitted = fitted.crop((left, top, left + pw, top + ph)).convert("RGB")
    img.paste(fitted, (x0, 0), _edge_fade_mask((pw, ph), fade_px))

def draw_hero_photo(img, key, image_path=None):
    """開場滿版主視覺：照片鋪滿，由左至右漸亮，左半壓暗保證大標可讀"""
    asset, _ = _resolve_visual(key, image_path)
    scale = max(W / asset.width, H / asset.height)
    fitted = asset.resize((max(int(asset.width * scale), W), max(int(asset.height * scale), H)), Image.LANCZOS)
    left = (fitted.width - W) // 2
    top  = (fitted.height - H) // 2
    fitted = fitted.crop((left, top, left + W, top + H)).convert("RGB")

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for x in range(W):
        t = x / W
        md.line([(x, 0), (x, H)], fill=int(235 * max(t - 0.18, 0) ** 1.4))
    img.paste(fitted, (0, 0), mask)

def _radial_glow_mask(size, peak_alpha):
    """產生中心亮、邊緣全透明的圓形遮罩（左上角光暈用）"""
    small = 128
    mask  = Image.new("L", (small, small), 0)
    md    = ImageDraw.Draw(mask)
    for i in range(small // 2, 0, -1):
        t = 1 - i / (small / 2)          # 0=邊緣 1=中心
        md.ellipse([small/2 - i, small/2 - i, small/2 + i, small/2 + i],
                   fill=int(peak_alpha * (t ** 2)))
    mask = mask.resize((size, size), Image.BICUBIC)
    # 只取左上 1/4 貼在畫布原點，光暈自然從角落散出
    full = Image.new("L", (W, H), 0)
    full.paste(mask, (-size // 2, -size // 2))
    return full

def draw_bg_gradient(img):
    """畫深色漸層底色"""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(BG[0] + (SURFACE[0] - BG[0]) * ratio)
        g = int(BG[1] + (SURFACE[1] - BG[1]) * ratio)
        b = int(BG[2] + (SURFACE[2] - BG[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    # 左上裝飾光暈（真正的柔邊徑向漸層：小尺寸遮罩放大後合成，避免硬邊色塊蓋住文字）
    img.paste(Image.new("RGB", img.size, ACCENT), (0, 0), _radial_glow_mask(GLOW_SIZE, GLOW_PEAK))

def draw_accent_line(draw, y, width=120):
    """左側藍色裝飾線"""
    draw.rectangle([80, y, 80 + width, y + 5], fill=ACCENT_LT)

def draw_logo_watermark(draw, font_small, right_edge=None):
    """品牌浮水印，預設貼右下；給 right_edge 可改貼在文字欄內，不壓到照片"""
    text = "欣晨工業 Hsin-Chan Industrial"
    bbox = draw.textbbox((0, 0), text, font=font_small)
    tw = bbox[2] - bbox[0]
    x = (right_edge if right_edge is not None else W - 50) - tw
    draw.text((x, H - 65), text, font=font_small, fill=DARK_GRAY)

def draw_icon(draw, key, cx, cy, r, color=ACCENT_LT):
    """用幾何圖形畫簡易圖示（不依賴外部圖示檔，CI 環境免安裝）"""
    lw = max(int(r * 0.09), 3)
    if key == "gear":
        draw.ellipse([cx-r*0.55, cy-r*0.55, cx+r*0.55, cy+r*0.55], outline=color, width=lw)
        for i in range(8):
            ang = i * math.pi / 4
            draw.line([cx+math.cos(ang)*r*0.55, cy+math.sin(ang)*r*0.55,
                       cx+math.cos(ang)*r,      cy+math.sin(ang)*r], fill=color, width=lw)
        draw.ellipse([cx-r*0.2, cy-r*0.2, cx+r*0.2, cy+r*0.2], outline=color, width=lw)
    elif key == "sensor":
        draw.line([cx-r, cy, cx+r, cy], fill=color, width=lw)
        for i, amp in enumerate([0.3, 0.7, 1.0, 0.5, 0.8]):
            x = cx - r*0.8 + i * r*0.4
            draw.line([x, cy, x, cy - r*0.8*amp], fill=color, width=lw)
    elif key == "chip":
        draw.rectangle([cx-r*0.5, cy-r*0.5, cx+r*0.5, cy+r*0.5], outline=color, width=lw)
        for i in range(3):
            off = -r*0.3 + i*r*0.3
            draw.line([cx-r*0.5, cy+off, cx-r*0.85, cy+off], fill=color, width=lw)
            draw.line([cx+r*0.5, cy+off, cx+r*0.85, cy+off], fill=color, width=lw)
            draw.line([cx+off, cy-r*0.5, cx+off, cy-r*0.85], fill=color, width=lw)
            draw.line([cx+off, cy+r*0.5, cx+off, cy+r*0.85], fill=color, width=lw)
    elif key == "heat":
        draw.polygon([(cx, cy-r), (cx+r*0.4, cy-r*0.2), (cx+r*0.25, cy),
                      (cx+r*0.5, cy+r*0.6), (cx, cy+r), (cx-r*0.5, cy+r*0.6),
                      (cx-r*0.25, cy), (cx-r*0.4, cy-r*0.2)], outline=color, width=lw)
    elif key == "data":
        for i, h in enumerate([0.4, 0.7, 1.0, 0.55]):
            x = cx - r*0.75 + i*r*0.4
            draw.rectangle([x, cy+r*0.6 - r*1.2*h, x+r*0.3, cy+r*0.6], outline=color, width=lw)
    elif key == "network":
        pts = [(cx, cy-r*0.8), (cx-r*0.8, cy+r*0.5), (cx+r*0.8, cy+r*0.5)]
        draw.line([pts[0], pts[1]], fill=color, width=lw)
        draw.line([pts[1], pts[2]], fill=color, width=lw)
        draw.line([pts[2], pts[0]], fill=color, width=lw)
        for x, y in pts:
            draw.ellipse([x-r*0.14, y-r*0.14, x+r*0.14, y+r*0.14], fill=BG, outline=color, width=lw)
    elif key == "check":
        draw.ellipse([cx-r*0.8, cy-r*0.8, cx+r*0.8, cy+r*0.8], outline=color, width=lw)
        draw.line([cx-r*0.35, cy, cx-r*0.05, cy+r*0.35], fill=color, width=lw)
        draw.line([cx-r*0.05, cy+r*0.35, cx+r*0.45, cy-r*0.35], fill=color, width=lw)
    elif key == "warning":
        draw.polygon([(cx, cy-r), (cx+r*0.85, cy+r*0.7), (cx-r*0.85, cy+r*0.7)], outline=color, width=lw)
        draw.line([cx, cy-r*0.3, cx, cy+r*0.15], fill=color, width=lw)
        draw.ellipse([cx-lw, cy+r*0.35-lw, cx+lw, cy+r*0.35+lw], fill=color)
    elif key == "cycle":
        draw.arc([cx-r*0.8, cy-r*0.8, cx+r*0.8, cy+r*0.8], 30, 300, fill=color, width=lw)
        ang = math.radians(300)
        ax, ay = cx + math.cos(ang)*r*0.8, cy + math.sin(ang)*r*0.8
        draw.line([ax, ay, ax - r*0.25, ay - r*0.05], fill=color, width=lw)
        draw.line([ax, ay, ax - r*0.05, ay + r*0.25], fill=color, width=lw)
    elif key == "robot":
        draw.rectangle([cx-r*0.5, cy-r*0.4, cx+r*0.5, cy+r*0.4], outline=color, width=lw)
        draw.ellipse([cx-r*0.2, cy-r*0.25, cx-r*0.05, cy-r*0.1], fill=color)
        draw.ellipse([cx+r*0.05, cy-r*0.25, cx+r*0.2, cy-r*0.1], fill=color)
        draw.line([cx, cy-r*0.4, cx, cy-r*0.65], fill=color, width=lw)
        draw.ellipse([cx-lw, cy-r*0.65-lw, cx+lw, cy-r*0.65+lw], fill=color)
        draw.line([cx-r*0.5, cy+r*0.1, cx-r*0.8, cy+r*0.3], fill=color, width=lw)
        draw.line([cx+r*0.5, cy+r*0.1, cx+r*0.8, cy+r*0.3], fill=color, width=lw)
    elif key == "idea":
        draw.ellipse([cx-r*0.5, cy-r*0.8, cx+r*0.5, cy+r*0.15], outline=color, width=lw)
        draw.line([cx-r*0.2, cy+r*0.15, cx-r*0.2, cy+r*0.4], fill=color, width=lw)
        draw.line([cx+r*0.2, cy+r*0.15, cx+r*0.2, cy+r*0.4], fill=color, width=lw)
        draw.line([cx-r*0.2, cy+r*0.4, cx+r*0.2, cy+r*0.4], fill=color, width=lw)
    elif key == "factory":
        draw.rectangle([cx-r*0.8, cy, cx+r*0.8, cy+r*0.6], outline=color, width=lw)
        draw.line([cx-r*0.8, cy, cx-r*0.8, cy-r*0.4, ], fill=color, width=lw)
        draw.line([cx-r*0.8, cy-r*0.4, cx-r*0.45, cy], fill=color, width=lw)
        draw.line([cx-r*0.1, cy, cx-r*0.1, cy-r*0.55], fill=color, width=lw)
        draw.line([cx-r*0.1, cy-r*0.55, cx+r*0.3, cy], fill=color, width=lw)
        draw.line([cx+r*0.55, cy-r*0.25, cx+r*0.55, cy], fill=color, width=lw)
    else:
        draw.ellipse([cx-r*0.6, cy-r*0.6, cx+r*0.6, cy+r*0.6], outline=color, width=lw)

def draw_host_badge(draw, x, y, font, label, color=ACCENT_LT):
    """畫一個簡易人形圖示＋標籤，標示雙主持人對談格式"""
    r = 24
    cx, cy = x + r, y + r
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=3)
    draw.ellipse([cx-r*0.32, cy-r*0.55, cx+r*0.32, cy+r*0.05], fill=color)
    draw.pieslice([cx-r*0.6, cy, cx+r*0.6, cy+r*0.95], 180, 360, fill=color)
    draw.text((x + r*2 + 14, y + r - 15), label, font=font, fill=GRAY)

def make_title_slide(topic_title, topic_tag, bold_path, reg_path, out_path, asset_key="ev_line", image_path=None):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)
    draw_hero_photo(img, asset_key, image_path)
    draw = ImageDraw.Draw(img)

    font_eyebrow  = ImageFont.truetype(bold_path, 30)
    font_title    = ImageFont.truetype(bold_path, 96)
    font_subtitle = ImageFont.truetype(reg_path,  38)
    font_brand    = ImageFont.truetype(bold_path, 32)
    font_small    = ImageFont.truetype(reg_path,  26)

    # 眉標（系列品牌）
    draw.text((80, 150), f"{SERIES_NAME_ZH} · {SERIES_NAME_EN}", font=font_eyebrow, fill=ACCENT_LT)
    draw_accent_line(draw, 194, 200)

    # 大標題（換行）
    title_y = 250
    title_y = draw_wrapped(draw, topic_title, font_title, 80, title_y, int(W * 0.68), WHITE, 1.15)

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

    # 雙主持人標示
    draw_host_badge(draw, int(W * 0.68), 70, font_small, "主持人 A")
    draw_host_badge(draw, int(W * 0.68) + 220, 70, font_small, "主持人 B")

    img.save(out_path)

def make_chapter_slide(index, total, title, bullets, icon_key, asset_key, bold_path, reg_path, out_path, image_path=None):
    """每個 beat 一張：左欄圖說文字，右側鋪實拍照或 CAD 線框，構成圖文版面"""
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    # 圖先鋪，文字後畫，確保文字永遠在最上層
    panel_x = int(W * 0.54)
    draw_asset_panel(img, asset_key, panel_x, image_path=image_path)
    draw = ImageDraw.Draw(img)

    font_eyebrow = ImageFont.truetype(bold_path, 28)
    font_title   = ImageFont.truetype(bold_path, 58)
    font_bullet  = ImageFont.truetype(reg_path,  34)
    font_small   = ImageFont.truetype(reg_path,  24)
    font_host    = ImageFont.truetype(reg_path,  24)

    draw.text((80, 70), f"{SERIES_NAME_ZH} · {SERIES_NAME_EN}", font=font_small, fill=DARK_GRAY)
    draw.text((80, 110), f"CHAPTER {index:02d} / {total:02d}", font=font_eyebrow, fill=ACCENT_LT)
    draw_accent_line(draw, 155, 160)

    text_w   = panel_x - 150          # 文字欄保留與圖片的間距
    bullet_w = text_w - 40

    # 先量「圖示＋標題＋分隔線＋條列」整塊高度，再置中於可用區間
    ICON_BLOCK = 92
    block_h = ICON_BLOCK
    block_h = draw_wrapped(draw, title, font_title, 80, block_h, text_w, WHITE, 1.2, dry=True) + 90
    for bullet in bullets:
        block_h = draw_wrapped(draw, bullet, font_bullet, 114, block_h, bullet_w, GRAY, 1.45, dry=True) + 26

    band_top, band_bottom = 215, H - 200
    y = max(band_top, band_top + (band_bottom - band_top - block_h) // 2)

    # 小圖示徽章：保留原本的符號語彙，但不再與照片爭版面
    draw_icon(draw, icon_key, 80 + 30, y + 30, 30)
    y += ICON_BLOCK

    y = draw_wrapped(draw, title, font_title, 80, y, text_w, WHITE, 1.2)

    y += 40
    draw.rectangle([80, y, 80 + text_w, y + 2], fill=DARK_GRAY)
    y += 50

    for bullet in bullets:
        draw.ellipse([80, y + 14, 93, y + 27], fill=ACCENT_LT)
        y = draw_wrapped(draw, bullet, font_bullet, 114, y, bullet_w, GRAY, 1.45)
        y += 26

    draw_host_badge(draw, 80, H - 140, font_host, "主持人 A")
    draw_host_badge(draw, 300, H - 140, font_host, "主持人 B")
    draw_logo_watermark(draw, font_small, right_edge=80 + text_w)
    img.save(out_path)

def make_cta_slide(quote, cta_question, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    font_tag   = ImageFont.truetype(reg_path,  24)
    font_cta   = ImageFont.truetype(bold_path, 50)
    font_q     = ImageFont.truetype(reg_path,  32)
    font_info  = ImageFont.truetype(reg_path,  34)
    font_sub   = ImageFont.truetype(reg_path,  30)
    font_small = ImageFont.truetype(reg_path,  24)

    draw.text((80, 70), f"{SERIES_NAME_ZH} · {SERIES_NAME_EN}", font=font_tag, fill=DARK_GRAY)
    draw_accent_line(draw, 130, 80)

    text_w     = int(W * 0.70)
    CONTACT_H  = 180

    # 先量「金句＋互動問句＋聯絡資訊」整塊高度，再置中，避免中段出現大片留白
    qh  = draw_wrapped(draw, f"「{quote}」", font_cta, 80, 0, text_w, WHITE, 1.25, dry=True) + 30
    qah = draw_wrapped(draw, cta_question, font_q, 80, qh, text_w, ACCENT_LT, 1.4, dry=True) + 60
    block_h = qah + CONTACT_H

    band_top, band_bottom = 200, H - 220
    y = max(band_top, band_top + (band_bottom - band_top - block_h) // 2)
    quote_top = y

    y = draw_wrapped(draw, f"「{quote}」", font_cta, 80, y, text_w, WHITE, 1.25)
    y += 30
    y = draw_wrapped(draw, cta_question, font_q, 80, y, text_w, ACCENT_LT, 1.4)

    y += 60
    draw.text((80, y),       "網站｜www.hsinchan.com",   font=font_info, fill=ACCENT_LT)
    draw.text((80, y + 60),  "電話｜03-381-4497",        font=font_info, fill=ACCENT_LT)
    draw.text((80, y + 120), "Email｜hc3814497@gmail.com", font=font_sub,  fill=GRAY)

    draw.rectangle([80, H - 180, W - 80, H - 178], fill=DARK_GRAY)
    draw.text((80, H - 160), "欣晨工業有限公司", font=font_sub,   fill=WHITE)
    draw.text((80, H - 115), "台灣桃園 · 1996年創立 · 30年精密製造經驗", font=font_small, fill=GRAY)

    draw_host_badge(draw, W - 420, quote_top, font_small, "主持人 A")
    draw_host_badge(draw, W - 420, quote_top + 70, font_small, "主持人 B")

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
    ("智慧化自動化設備",  "智慧自動化", "智慧化自動化設備如何從單機自動化升級到互聯互通：整合感測器、PLC控制與AI演算法，讓設備自己判斷、自己調整、自己優化製程參數。"),
    ("智慧化自動化設備",  "智慧自動化", "智慧化自動化設備的核心是數據閉環：感測層收集、邊緣運算分析、控制層即時反應 — 讓產線從「會動」進化到「會思考」。"),
    ("智慧化自動化設備",  "智慧自動化", "智慧化自動化設備在台灣中小製造業的導入路徑：從單一工作站的感測升級開始，逐步串接成能自我優化的智慧產線網路。"),
]

def get_today_topic():
    tw_now   = datetime.now(timezone(timedelta(hours=8)))
    day_idx  = tw_now.timetuple().tm_yday % len(TOPICS)
    title, tag, angle = TOPICS[day_idx]
    date_str = tw_now.strftime("%Y-%m-%d")
    print(f"📅 日期：{date_str}（年第{tw_now.timetuple().tm_yday}天）")
    print(f"📌 今日題材：{title}（#{tag}）")
    return title, tag, angle, date_str

ICON_ENUM_HINT = "gear / sensor / chip / heat / data / network / check / warning / cycle / robot / idea / factory"
PHOTO_ENUM_HINT = " / ".join(f"{k}（{v['desc']}）" for k, v in ASSETS.items())

def generate_video_script(topic_title, topic_angle):
    print(f"🤖 呼叫 {SCRIPT_MODEL} 生成 11-12 分鐘長片腳本...")
    ac = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""你是《{SERIES_NAME_ZH}》（{SERIES_NAME_EN}）節目的編劇，這是一個雙主持人對談節目：
主持人 A 是男性，理性冷靜，擅長拆解數據與物理/成本根本原理；
主持人 B 是女性，擅長追問、幫觀眾把疑惑問出來，並把原理連結到實際應用場景。
兩人要像真人來回討論，B 可以質疑、驚訝、追問，A 再進一步解釋——不是兩人各自唸稿。

目標受眾：製造業從業者、工程師、科技創業者，以及對特斯拉/馬斯克式創新邏輯有興趣的知識型觀眾。
風格：快節奏、語氣像在拆解一個被大家誤解的行業迷思。

── 這支影片同時要達成兩個目標，缺一不可 ──
【教育目標】觀眾看完要帶走一個「可以自己拿去用」的思考工具，而不只是聽了一集有趣的故事。
  具體要求：每個維度的「第一性原理拆解」beat，都要示範一個**可以套用到任何產業的提問句**
  （例如：「這個成本裡，有多少是物理必然，有多少只是歷史習慣？」）。
  觀眾應該能在自己的工作現場複述這個問題。寧可把一個觀念講透，也不要蜻蜓點水講五個。

【行銷目標】看完後，觀眾對欣晨工業應該產生的印象是：
  「這是一家真正懂製造本質、而且能把原理落地成實體設備的公司」——而不是「這家公司很會打廣告」。
  達成方式是**展現思考深度**，不是增加曝光次數。因此：
  - 全片提到「欣晨」最多 3 次，且只能出現在各維度的「智慧製造應用」beat 裡
  - 每次提及都必須是「因為剛剛拆解出這個原理，所以對應到某項實際能力」的自然銜接，
    不能是插播式的自我介紹或產品型錄朗讀
  - 可動用的可信度資產：1996 年創立、30 年精密製造經驗、以 TPS 為核心哲學、
    1200°C 工業加熱器、熱電偶、一體式料管、碳化矽保護管、機械手臂整合、AOI 視覺檢測
  - 寧可一次都不提而讓內容夠強，也不要為了提及而破壞敘事

欣晨工業是台灣桃園1996年創立的精密自動化設備製造商，以豐田生產方式（TPS）為核心哲學。
主要業務：工業加熱器（1200°C）、熱電偶、一體式料管、碳化矽保護管、機械手臂整合、AOI視覺檢測。

今日主題：{topic_title}
角度提示：{topic_angle}

── 寫作方法：第一性原理（Elon Musk 式 First Principles Reasoning）──
不要用「業界都這麼說」「大家習慣這樣做」之類的類比式推論（reasoning by analogy）堆砌內容。
可以引用特斯拉 Giga Factory、一體化壓鑄（Giga Press）等公開案例作為示範性佐證；但如果今日主題離汽車製造較遠，
就改用更貼切、可驗證的業界標竿案例，不要每集都硬套特斯拉——落地的主角終究要回到今日主題與欣晨工業的技術領域。

── 全片架構（總長約 11-12 分鐘，五幕，缺一不可）──
第一幕 Hook 開場（約 60 秒）：用一個強烈對比畫面感破題（例如：傳統工廠的沉悶堆積 vs 高度自動化產線的特寫），
  點出一個大家以為是「錢」或「資源」的問題，但其實是「思考方式」的問題，拋出全片要拆解的疑問，並說明本集主旨。
第二幕 核心觀念（約 2 分鐘，2 個 beats）：解釋「類比推理」vs「第一性原理」的差異——
  beat 1：業界迷思是什麼樣的類比推理（「大家都外包」「行業標準就是這個價」）；
  beat 2：製造的物理本質（把原物料重新排列組合成更高價值的形狀/功能）與經濟本質（減少能量損耗、時間成本、搬運無效率）。
第三幕 三大維度案例拆解（約 6 分鐘，3 個維度 x 各 3 個 beats＝9 個 beats）：
  維度依序為「產線設計」「數據與軟體」「供應鏈與物流」，每個維度都要包含恰好 3 個 beats：
    beat A：傳統做法是什麼、為什麼大家這樣做
    beat B：第一性原理拆解——問「為什麼非得這樣？」，拆到物理/成本/資料的根本限制
    beat C：智慧製造應用——拆解後得出的新做法，並自然連結到今日主題／欣晨工業技術能對應的部分
第四幕 深度反思與盲點警示（約 2 分鐘，2 個 beats）：
  beat 1：盲目套用第一性原理的風險——不是所有工廠都該追求極致自動化/一體化，高客製化、小批量的工廠反而可能資本支出回不來；
  beat 2：第一性原理的終極考量是「資本效率」，不是為拆解而拆解。
第五幕 Outro 結語（約 60 秒，1 個 cta）：
  一句濃縮全片核心的金句（例如精神類似「智慧製造的終點不是買最貴的機器人，而是敢不敢把現有的行業規矩歸零重來」，但要換成貼合今日主題的原創金句）；
  再加一個邀請觀眾留言互動的 CTA 問句（例如精神類似「你所在的產業，有哪些『大家都這麼做』的潛規則？留言告訴我們」，換成貼合今日主題的原創版本）。

請以 JSON 格式輸出，嚴格遵守以下結構。"dialogue" 都是陣列，每個元素是 {{"speaker":"A"或"B","line":"該句台詞"}}，
A/B 要交替來回（不是A講完全部再B講全部）。字數都是口語唸出的字數，不是書面字數：
{{
  "video_title": "影片主標題（15字以內，有衝擊力，可以是挑戰常規假設的問句或反直覺陳述）",
  "hook_dialogue": [ {{"speaker":"A","line":"..."}}, {{"speaker":"B","line":"..."}}, ... ]  // 3-4 輪對話，總字數約230-260字（唸出約55-62秒）
  ,
  "concept_beats": [
    {{ "title": "beat標題（12字內）", "icon": "{ICON_ENUM_HINT} 其中一個", "photo": "{PHOTO_ENUM_HINT} 其中一個的代號", "image_prompt": "英文，描述這段要搭配的畫面",
       "bullets": ["重點短句1（12字內）","重點短句2（12字內）"],
       "dialogue": [ {{"speaker":"A","line":"..."}}, {{"speaker":"B","line":"..."}}, ... ] }}  // 總字數約230-260字（約55-62秒）
    // 正好 2 個，對應核心觀念 beat1、beat2
  ],
  "dimensions": [
    {{ "name": "產線設計", "icon": "{ICON_ENUM_HINT} 其中一個",
       "beats": [
         {{ "label": "傳統做法", "photo": "素材代號", "image_prompt": "英文畫面描述", "bullets": ["...","..."], "dialogue": [...] }},   // 總字數約150-180字（約35-42秒）
         {{ "label": "第一性原理拆解", "bullets": ["...","..."], "dialogue": [...] }},
         {{ "label": "智慧製造應用", "bullets": ["...","..."], "dialogue": [...] }}
       ] }},
    {{ "name": "數據與軟體", "icon": "...", "beats": [ ... 同上 3 個 ... ] }},
    {{ "name": "供應鏈與物流", "icon": "...", "beats": [ ... 同上 3 個 ... ] }}
  ],
  "reflection_beats": [
    {{ "title": "beat標題（12字內）", "icon": "{ICON_ENUM_HINT} 其中一個", "photo": "素材代號", "image_prompt": "英文畫面描述",
       "bullets": ["...","..."], "dialogue": [...] }}  // 總字數約230-260字（約55-62秒）
    // 正好 2 個，對應盲點警示、資本效率
  ],
  "outro_image_prompt": "英文畫面描述，給結語用的收束畫面",
  "outro_quote": "結尾金句（30字以內，原創、貼合今日主題，不是書面摘要而是一句可以被記住的話）",
  "outro_cta_question": "邀請觀眾留言互動的問句（30字以內，貼合今日主題）",
  "outro_dialogue": [ {{"speaker":"A","line":"..."}}, {{"speaker":"B","line":"..."}}, ... ]  // 3-4 輪，總字數約230-260字（約55-62秒），口語版的結語，可以呼應金句但不用逐字重複，不用唸出電話或網址（畫面會顯示聯絡資訊）
  ,
  "fb_caption": "Facebook 貼文說明（300-400字）。這是觀眾滑過動態牆時唯一會先看到的文字，要能獨立成立。結構：第一行用一句反直覺的鉤子讓人停下來（不要寫「本集介紹…」這種開頭）；中段用 2-3 句說明這集拆解了什麼、觀眾會學到哪個可複用的思考工具；接著一句不推銷的可信度陳述（欣晨 30 年精密製造的實作視角）；最後用影片的互動問句邀請留言。專業、不說教、不用驚嘆號堆疊。\\n\\n#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5"
}}

要求：
- 繁體中文，口語自然、像真人對話（這是要被語音合成唸出來的雙主持人台詞，不是書面文章）

── 事實準確性（最高優先，違反會毀掉整個頻道的可信度）──
這支影片會以欣晨工業的名義公開發布。捏造的數據一旦被同業指出來，傷害遠大於內容無聊。
- 只使用你有把握、屬於公開常識等級的事實（例：Giga Press 把數十個沖壓件整合成極少數鑄件）
- **不確定就不要給精確數字**。改用數量級、比例或推理式表述
  （「從數十個零件變成個位數」「能耗大概是原本的幾分之一」），不要編造「降低 37.2%」這種假精確
- **絕對不要把查不到的數據掛在具名公司上**（不可出現「台積電良率提升 23.7%」這類虛構統計）
- 說服力要來自**物理與成本的推理過程**，不是來自統計數字的堆砌——
  這正是第一性原理的精神：能從物理推導出來的結論，不需要引用別人的數據來背書
- 涉及不確定的推估時，讓主持人明說這是推估（「保守估計」「量級上大概是」）
- dimensions 陣列必須正好 3 組，且每組 beats 必須正好 3 個，依序是「傳統做法／第一性原理拆解／智慧製造應用」
- icon 欄位只能從這些選一個：{ICON_ENUM_HINT}，要挑視覺上貼切的
- photo 欄位只能填這些代號之一：{PHOTO_ENUM_HINT}（這是生圖失敗時的備援，仍要填）
- image_prompt 是這段的專屬畫面描述，**用英文寫**，20-35 個字，要點：
  * 直接描述「鏡頭裡看到什麼」的具體工業場景，呼應該段台詞在講的事
  * 只描述主體與環境，不要寫風格、打光、色調（全片統一套用，不用你指定）
  * 畫面中不要有任何文字、標誌、招牌
  * 例：an empty legacy factory floor with idle CNC machines and stacked work-in-process pallets
  * 每段的畫面要有差異，不要每段都是同一種機械手臂特寫
- 欣晨工業的置入規則見前述【行銷目標】，嚴格遵守「最多 3 次、只在應用 beat、必須自然銜接」
- 只輸出JSON，不要前言說明"""

    last_err = None
    for attempt in range(1, SCRIPT_RETRIES + 1):
        # 腳本決定整支影片的教育價值與行銷品質，是最值得投資的一環。
        # 相對於生圖成本（約 $0.47/支），換上最強模型每支只多約 $0.12。
        # Opus 5.5 思考永遠開啟，effort 預設是 medium，這裡明確拉到 high；
        # 思考 token 會計入 max_tokens，所以改用串流並放寬上限，避免 JSON 被截斷。
        with ac.messages.stream(
            model=SCRIPT_MODEL,
            max_tokens=32000,
            output_config={"effort": "high"},
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            msg = stream.get_final_message()

        if msg.stop_reason == "max_tokens":
            last_err = "輸出被 max_tokens 截斷，JSON 不完整"
            print(f"   ⚠️  腳本生成第 {attempt}/{SCRIPT_RETRIES} 次：{last_err}")
            continue

        # 思考開啟後 content[0] 可能是 thinking block，必須挑出 text block 再合併
        raw = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text").strip()
        # 去掉可能的 markdown code block
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            script = json.loads(raw.strip())
            validate_script(script)
            return script
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            print(f"   ⚠️  腳本生成第 {attempt}/{SCRIPT_RETRIES} 次不合格：{e}")

    raise RuntimeError(f"腳本連續 {SCRIPT_RETRIES} 次不合格：{last_err}")

def iter_dialogues(script):
    """依播放順序走訪每一段對話（hook → 核心觀念 → 三維度 → 反思 → outro）"""
    yield script["hook_dialogue"]
    for beat in script["concept_beats"]:
        yield beat["dialogue"]
    for dim in script["dimensions"]:
        for beat in dim["beats"]:
            yield beat["dialogue"]
    for beat in script["reflection_beats"]:
        yield beat["dialogue"]
    yield script["outro_dialogue"]

def estimate_script_seconds(script):
    """用台詞字數粗估成片長度（含每段對話之間的停頓）"""
    total = 0.0
    for dialogue in iter_dialogues(script):
        chars = sum(len(str(t["line"]).strip()) for t in dialogue)
        total += chars / CHARS_PER_SEC + DIALOGUE_GAP * max(len(dialogue) - 1, 0)
    return total

def _check_dialogue(dialogue, where):
    if not isinstance(dialogue, list) or not dialogue:
        raise ValueError(f"{where}：dialogue 必須是非空陣列")
    for turn in dialogue:
        if not isinstance(turn, dict) or "speaker" not in turn or "line" not in turn:
            raise ValueError(f"{where}：每則對話需含 speaker 與 line")
        if turn["speaker"] not in HOST_VOICES:
            raise ValueError(f"{where}：speaker 只能是 A 或 B，收到 {turn['speaker']!r}")
        if not str(turn["line"]).strip():
            raise ValueError(f"{where}：line 不可為空（空字串無法配音）")

def normalize_assets(script):
    """把 photo 欄位補齊並正規化

    素材只有幾張，Claude 偶爾會填錯或漏填；這種小事不值得讓整支長片重跑，
    所以就地回退成輪流取用，確保每張章節卡都有圖。
    """
    fallback = iter(ASSET_KEYS * 40)
    def fix(beat):
        if beat.get("photo") not in ASSETS:
            beat["photo"] = next(fallback)
    for beat in script["concept_beats"]:
        fix(beat)
    for dim in script["dimensions"]:
        for beat in dim["beats"]:
            fix(beat)
    for beat in script["reflection_beats"]:
        fix(beat)

def validate_script(script):
    """上線前先驗證腳本結構

    配音與算圖要跑數十分鐘，結構錯誤必須在這裡就擋下來，
    而不是等到跑了一半才拋 KeyError。
    """
    for key in ("video_title", "hook_dialogue", "concept_beats", "dimensions",
                "reflection_beats", "outro_quote", "outro_cta_question",
                "outro_dialogue", "fb_caption"):
        if not script.get(key):
            raise ValueError(f"腳本缺少必要欄位：{key}")

    _check_dialogue(script["hook_dialogue"], "hook_dialogue")
    _check_dialogue(script["outro_dialogue"], "outro_dialogue")

    for name in ("concept_beats", "reflection_beats"):
        beats = script[name]
        if not isinstance(beats, list) or len(beats) != 2:
            raise ValueError(f"{name} 必須正好 2 個 beat，收到 {len(beats) if isinstance(beats, list) else type(beats)}")
        for i, beat in enumerate(beats, 1):
            for key in ("title", "bullets", "dialogue"):
                if not beat.get(key):
                    raise ValueError(f"{name}[{i}] 缺少 {key}")
            _check_dialogue(beat["dialogue"], f"{name}[{i}]")

    dims = script["dimensions"]
    if not isinstance(dims, list) or len(dims) != 3:
        raise ValueError(f"dimensions 必須正好 3 組，收到 {len(dims) if isinstance(dims, list) else type(dims)}")
    for d, dim in enumerate(dims, 1):
        if not dim.get("name") or not isinstance(dim.get("beats"), list):
            raise ValueError(f"dimensions[{d}] 缺少 name 或 beats")
        if len(dim["beats"]) != 3:
            raise ValueError(f"dimensions[{d}]（{dim.get('name')}）必須正好 3 個 beat，收到 {len(dim['beats'])}")
        for j, beat in enumerate(dim["beats"], 1):
            for key in ("label", "bullets", "dialogue"):
                if not beat.get(key):
                    raise ValueError(f"dimensions[{d}].beats[{j}] 缺少 {key}")
            _check_dialogue(beat["dialogue"], f"dimensions[{d}].beats[{j}]")

    normalize_assets(script)

    est = estimate_script_seconds(script)
    if not (SCRIPT_EST_MIN <= est <= SCRIPT_EST_MAX):
        raise ValueError(
            f"腳本粗估片長 {est/60:.1f} 分鐘，超出可接受範圍 "
            f"{SCRIPT_EST_MIN/60:.1f}-{SCRIPT_EST_MAX/60:.1f} 分鐘"
        )

# ── 語音旁白（雙主持人對話）──────────────────────────────────────────────────
def synthesize_line(text, voice, out_path, retries=TTS_RETRIES):
    """用 OpenAI TTS 生成單句語音

    單次執行要發約 50 次請求，偶發網路失敗屬正常；
    這裡逐次退避重試，避免一句失敗就讓整個長片流程報銷。
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("旁白台詞為空，無法配音")

    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.audio.speech.create(
                model=TTS_MODEL,
                voice=voice,
                input=text,
                response_format="mp3",
                speed=TTS_SPEED,
            )
            Path(out_path).write_bytes(resp.read())
            if Path(out_path).exists() and Path(out_path).stat().st_size > 0:
                return
            last_err = RuntimeError("TTS 回傳空音檔")
        except Exception as e:          # noqa: BLE001 — 任何網路/協定錯誤都值得重試
            last_err = e
        if attempt < retries:
            wait = TTS_BACKOFF * attempt
            print(f"   ⚠️  配音失敗（第 {attempt}/{retries} 次）：{last_err} — {wait}秒後重試")
            time.sleep(wait)
    raise RuntimeError(f"配音連續 {retries} 次失敗：{last_err}")

def make_silence_clip(duration, out_path):
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
           "-t", f"{duration}", "-q:a", "9", "-acodec", "libmp3lame", str(out_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"靜音片段生成失敗：{result.stderr[-500:]}")

def synthesize_dialogue(dialogue, tmp_dir, tag):
    """把一段 A/B 交替台詞合成為一個連續音檔（逐句配音＋靜音間隔串接）"""
    silence_path = tmp_dir / "_silence.mp3"
    if not silence_path.exists():
        make_silence_clip(DIALOGUE_GAP, silence_path)

    line_paths = []
    for k, turn in enumerate(dialogue):
        voice = HOST_VOICES.get(turn["speaker"], HOST_VOICES["A"])
        line_path = tmp_dir / f"{tag}_line{k}.mp3"
        synthesize_line(turn["line"], voice, line_path)
        line_paths.append(line_path)

    list_file = tmp_dir / f"{tag}_dlist.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for k, p in enumerate(line_paths):
            f.write(f"file '{p.resolve().as_posix()}'\n")
            if k < len(line_paths) - 1:
                f.write(f"file '{silence_path.resolve().as_posix()}'\n")

    out_path = tmp_dir / f"{tag}_dialogue.mp3"
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"對話音檔串接失敗：{result.stderr[-800:]}")
    return out_path

def get_audio_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    )
    return float(result.stdout.strip())

# ── 影片生成 ─────────────────────────────────────────────────────────────────
def render_segment_clip(image_path, audio_path, duration, out_path):
    """單張靜圖 + 旁白音檔 → 一段帶 Ken Burns 緩慢放大效果的影片片段"""
    frames = max(int(duration * VIDEO_FPS), 1)
    # zoompan 的縮放量會量化到整數來源像素，直接對 1080p 做會讓文字每隔幾格抖一下。
    # 先放大 2 倍再 zoompan 回 1080p，縮放步階落在實際像素上，字就不會閃爍。
    zoompan = (
        f"scale={W*2}:{H*2},"
        f"zoompan=z='min(1+({ZOOM_END}-1)*on/{frames},{ZOOM_END})'"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s={W}x{H}:fps={VIDEO_FPS}"
    )
    fade_out_start = max(duration - CLIP_FADE, 0)
    vf = f"{zoompan},fade=in:st=0:d={CLIP_FADE},fade=out:st={fade_out_start:.2f}:d={CLIP_FADE}"
    af = f"afade=in:st=0:d={CLIP_FADE},afade=out:st={fade_out_start:.2f}:d={CLIP_FADE}"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-t", f"{duration:.2f}",
        "-vf", vf,
        "-af", af,
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(VIDEO_FPS),
        # 取樣率/聲道固定下來，後面 concat 才能安全地直接 stream copy
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-shortest",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 片段合成失敗：{result.stderr[-800:]}")

def concat_clips(clip_paths, out_path):
    """串接所有片段（編碼參數一致，可直接 stream copy，不需重新轉檔）"""
    list_file = Path(out_path).parent / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{Path(p).resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 片段串接失敗：{result.stderr[-800:]}")
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
    print(f"  {SERIES_NAME_ZH} — 雙主持人長片自動發布")
    print("═══════════════════════════════════════════")

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    if dry_run:
        print("⚠️  DRY RUN：只產生影片，不上傳\n")

    topic_title, topic_tag, topic_angle, date_str = get_today_topic()

    # 1. 生成腳本
    script = generate_video_script(topic_title, topic_angle)
    print(f"\n📝 影片主標：{script['video_title']}")
    for dim in script["dimensions"]:
        print(f"   維度：{dim['name']}")

    # 2. 載入字型
    bold_path, reg_path = load_fonts()
    print(f"\n🔤 字型：{Path(bold_path).name}")

    # 章節編號只算「有章節卡」的 beats：核心觀念 + 三維度 + 反思，不含 hook/outro
    total_chapters = len(script["concept_beats"]) \
        + sum(len(dim["beats"]) for dim in script["dimensions"]) \
        + len(script["reflection_beats"])
    chapter_idx = 0

    # 3. 逐段生成語音旁白 + 畫面 + 合成片段
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 先依每段台詞生成專屬畫面；沒金鑰或生圖失敗都會退回 repo 內的本地素材
        images = {}
        if os.environ.get("OPENAI_API_KEY"):
            jobs = [("00_hook", script.get("hero_image_prompt") or script["concept_beats"][0].get("image_prompt"), "16:9")]
            for j, beat in enumerate(script["concept_beats"], 1):
                jobs.append((f"01_concept_{j}", beat.get("image_prompt"), "4:5"))
            for d, dim in enumerate(script["dimensions"], 1):
                for j, beat in enumerate(dim["beats"], 1):
                    jobs.append((f"02_dim{d}_{j}", beat.get("image_prompt"), "4:5"))
            for j, beat in enumerate(script["reflection_beats"], 1):
                jobs.append((f"03_reflect_{j}", beat.get("image_prompt"), "4:5"))
            print(f"\n🖼️  依台詞生成畫面（{IMAGE_MODEL}，共 {len(jobs)} 張）")
            for tag, prompt_text, aspect in jobs:
                if not prompt_text:
                    continue
                got = generate_beat_image(prompt_text, aspect, tmp / f"{tag}_gen.png")
                if got:
                    images[tag] = got
                    print(f"   ✅ {tag}")
            print(f"   生成 {len(images)}/{len(jobs)} 張，其餘用本地素材")
        else:
            print("\n🖼️  未設定 GOOGLE_API_KEY，全部使用 repo 內素材")

        clip_paths = []
        total_duration = 0.0

        def build_segment(tag, draw_fn, dialogue):
            nonlocal total_duration
            audio_path = synthesize_dialogue(dialogue, tmp, tag)
            duration = get_audio_duration(audio_path)
            image_path = tmp / f"{tag}.png"
            draw_fn(image_path)
            clip_path = tmp / f"{tag}_clip.mp4"
            render_segment_clip(image_path, audio_path, duration, clip_path)
            clip_paths.append(clip_path)
            total_duration += duration
            print(f"🎬 {tag}  ⏱️  {duration:.1f}秒")

        # 第一幕：Hook 開場
        build_segment(
            "00_hook",
            lambda p: make_title_slide(script["video_title"], topic_tag, bold_path, reg_path, p,
                                       image_path=images.get("00_hook")),
            script["hook_dialogue"],
        )

        # 第二幕：核心觀念
        for j, beat in enumerate(script["concept_beats"], 1):
            chapter_idx += 1
            build_segment(
                f"01_concept_{j}",
                lambda p, beat=beat, idx=chapter_idx, tag=f"01_concept_{j}": make_chapter_slide(
                    idx, total_chapters, beat["title"], beat["bullets"], beat["icon"],
                    beat["photo"], bold_path, reg_path, p, image_path=images.get(tag)
                ),
                beat["dialogue"],
            )

        # 第三幕：三大維度案例拆解
        for d, dim in enumerate(script["dimensions"], 1):
            for j, beat in enumerate(dim["beats"], 1):
                chapter_idx += 1
                title = f"{dim['name']} · {beat['label']}"
                build_segment(
                    f"02_dim{d}_{j}",
                    lambda p, dim=dim, beat=beat, title=title, idx=chapter_idx, tag=f"02_dim{d}_{j}": make_chapter_slide(
                        idx, total_chapters, title, beat["bullets"], dim["icon"],
                        beat["photo"], bold_path, reg_path, p, image_path=images.get(tag)
                    ),
                    beat["dialogue"],
                )

        # 第四幕：深度反思與盲點警示
        for j, beat in enumerate(script["reflection_beats"], 1):
            chapter_idx += 1
            build_segment(
                f"03_reflect_{j}",
                lambda p, beat=beat, idx=chapter_idx, tag=f"03_reflect_{j}": make_chapter_slide(
                    idx, total_chapters, beat["title"], beat["bullets"], beat["icon"],
                    beat["photo"], bold_path, reg_path, p, image_path=images.get(tag)
                ),
                beat["dialogue"],
            )

        # 第五幕：Outro 結語（金句 + CTA 問句）
        build_segment(
            "99_outro",
            lambda p: make_cta_slide(
                script["outro_quote"], script["outro_cta_question"], bold_path, reg_path, p
            ),
            script["outro_dialogue"],
        )

        print(f"\n🎞️  共 {len(clip_paths)} 段，總長約 {total_duration/60:.1f} 分鐘")

        # 4. 串接所有片段
        video_path = tmp / f"hsinchan_{date_str}.mp4"
        concat_clips(clip_paths, video_path)

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
            str(video_path), script["video_title"],
            script["fb_caption"], topic_tag, date_str
        )

        print(f"\n🎉 完成！{date_str} 影片已發布")
        if fb_id: print(f"   Facebook Video ID : {fb_id}")
        if yt_id: print(f"   YouTube Video ID  : {yt_id}  (https://youtu.be/{yt_id})")

if __name__ == "__main__":
    main()
