#!/usr/bin/env python3
"""
欣晨工業 — 智慧製造 10-13 分鐘深度解析長片自動發布（FB + YouTube）
流程：Claude 生成第一性原理腳本 → OpenAI TTS 旁白配音 → Pillow 繪製畫面
      → FFmpeg 逐段合成（Ken Burns 效果）→ 串接 → 上傳 Facebook + YouTube
"""

import os, sys, json, base64, subprocess, tempfile, textwrap, math, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import topics
import diagrams

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
# 翻譯是機械性工作，不需要最強模型；用 Haiku 每支約 $0.05
TRANSLATE_MODEL = os.environ.get("TRANSLATE_MODEL", "claude-haiku-4-5")
SUBTITLE_LANGS = [x for x in os.environ.get("SUBTITLE_LANGS", "en,ja").split(",") if x]
# 上傳測試模式：YouTube 以不公開狀態上傳、跳過 Facebook。
# 用來驗證上傳與字幕 API 這條鏈路，而不讓任何東西公開。
UPLOAD_TEST = os.environ.get("UPLOAD_TEST", "false").lower() == "true"
# captions.insert 需要 force-ssl，比單純上傳影片的權限更大
YT_SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
             "https://www.googleapis.com/auth/youtube.force-ssl"]
WEB_SEARCH_MAX_USES = int(os.environ.get("WEB_SEARCH_MAX_USES", "6"))

# ── 片長控制（目標 10-13 分鐘）──────────────────────────────────────────────
TARGET_MIN_SEC = 10 * 60      # 成片下限
TARGET_MAX_SEC = 15 * 60      # 成片上限
TARGET_MID_SEC = 12.5 * 60    # 微調時瞄準的中心值
# 腳本階段的粗估語速（字/秒）。只用來決定「要不要請 Claude 重寫」，
# 真正的片長微調是依據配音後量到的實際秒數，所以這個常數不準也不會失準。
CHARS_PER_SEC  = 4.3   # 依 edge-tts 實測校正：同腳本比 OpenAI 慢約 6%
SCRIPT_EST_MIN = 9.5 * 60     # 粗估低於此值就請 Claude 加長
SCRIPT_EST_MAX = 15.5 * 60    # 粗估高於此值才重寫。估算誤差約 ±10%，
                              # 卡太緊會讓邊界值白白重跑一次最貴的呼叫
MAX_RATE_ADJ   = 15           # 語速調整上限 ±15%（再多就不自然）

# tts-1-hd 比 tts-1 貴一倍，但整支影片也只差約 $0.04，為成片品質值得
# 配音來源：edge-tts 用的 zh-TW-*Neural 是微軟 Azure 的官方台灣中文語音，
# 母語腔調且免費；OpenAI 的聲線是英語母語，唸中文會有明顯外國腔。
# 但 edge-tts 走非官方免費端點，所以保留 OpenAI 作為端點不可用時的備援，
# 由 preflight 探測一次後決定整支影片的來源，避免同一支影片混用兩種聲線。
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "edge")
TTS_MODEL = os.environ.get("TTS_MODEL", "tts-1-hd")   # 僅 OpenAI 備援時使用
TTS_SPEED = float(os.environ.get("TTS_SPEED", "1.0"))
VOICES = {
    "edge":   {"A": os.environ.get("HOST_A_VOICE", "zh-TW-YunJheNeural"),
               "B": os.environ.get("HOST_B_VOICE", "zh-TW-HsiaoChenNeural")},
    "openai": {"A": "onyx", "B": "nova"},
}
HOST_VOICES = VOICES[TTS_PROVIDER if TTS_PROVIDER in VOICES else "edge"]
# preflight 探測後填入，整支影片共用同一個來源
ACTIVE_TTS = {"provider": TTS_PROVIDER if TTS_PROVIDER in VOICES else "edge"}
HOST_LABELS = {"A": "主持人 A", "B": "主持人 B"}

ICON_KEYS = ["gear", "sensor", "chip", "heat", "data", "network",
             "check", "warning", "cycle", "robot", "idea", "factory"]

for _n, _v in (("BG", BG), ("ACCENT", ACCENT), ("ACCENT_LT", ACCENT_LT),
               ("WHITE", WHITE), ("GRAY", GRAY), ("DARK_GRAY", DARK_GRAY)):
    setattr(diagrams, _n, _v)      # 品牌色單一來源，避免兩邊不同步

DISPLAY_FONT = None   # 標題字型，main() 啟動時載入

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

SERIES_NAME_ZH = "第一性原理拆解智慧製造"
SERIES_NAME_EN = "FIRST PRINCIPLES OF SMART MFG"

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


def load_display_font(fallback_bold):
    """標題用的第二套字型（思源宋體）

    標題和內文若是同一套字的不同粗細，只有粗細差、沒有個性差，
    看起來就像系統預設。襯線標題配無襯線內文才是真正的字型搭配。
    字型由 workflow 下載到 scripts/fonts/；抓不到就退回原本的黑體，
    不讓字型問題害整支影片失敗。
    """
    here = Path(__file__).resolve().parent
    for p in (here / "fonts" / "NotoSerifTC-Bold.otf",
              Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"),
              Path("/usr/share/fonts/opentype/noto/NotoSerifCJKtc-Bold.otf")):
        if p.exists():
            return str(p)
    print("   ⚠️  找不到標題字型，改用黑體（視覺層次會較弱）")
    return fallback_bold

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
    out = Image.blend(src, tinted, 0.30).convert("RGBA")
    return Image.blend(Image.new("RGB", src.size, BG).convert("RGBA"), out, 0.93)

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
    """左緣淡出遮罩

    淡出太短太陡會在照片左緣留下一道看得見的垂直接縫。
    用較長的過渡距離搭配平滑曲線（smoothstep），兩端斜率為零，
    才不會在淡出起點與終點各留下一條可辨識的邊。
    """
    w, h = size
    mask = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(mask)
    span = min(fade_px, w)
    for x in range(span):
        t = x / span
        md.line([(x, 0), (x, h)], fill=int(255 * (t * t * (3 - 2 * t))))
    return mask

def _resolve_visual(key, image_path):
    """優先用當集生成的圖，沒有就退回 repo 內的本地素材"""
    if image_path and Path(image_path).exists():
        return load_generated_image(image_path), "photo"
    return load_asset(key), ASSETS.get(key, {}).get("kind", "photo")

def draw_asset_panel(img, key, x0, fade_px=440, image_path=None):
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
    """品牌浮水印：靠左對齊 80px 邊距，與左上角系列標上下呼應成一個框架"""
    draw.text((80, H - 72), "欣晨工業 HSIN-CHAN INDUSTRIAL", font=font_small, fill=DARK_GRAY)

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

diagrams._ICON_FN = draw_icon   # 圖示繪製注入，必須在 draw_icon 定義之後

def make_title_slide(topic_title, topic_tag, bold_path, reg_path, out_path, asset_key="ev_line", image_path=None):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)
    draw_hero_photo(img, asset_key, image_path)
    draw = ImageDraw.Draw(img)

    font_eyebrow  = ImageFont.truetype(bold_path, 30)
    font_title    = ImageFont.truetype(DISPLAY_FONT or bold_path, 96)
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

    img.save(out_path)

def make_chapter_slide(index, total, title, bullets, icon_key, asset_key, bold_path, reg_path, out_path,
                       image_path=None, diagram=None):
    """每個 beat 一張：左欄圖說文字，右側放圖解或照片

    右側優先畫「圖解」——教學型內容靠結構圖傳達關係，照片只能營造氣氛。
    沒有圖解時才退回照片，讓畫面仍有內容。
    """
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    # 圖先鋪，文字後畫，確保文字永遠在最上層
    panel_x = int(W * 0.54)
    if not (diagram and diagrams.draw_diagram(img, diagram, panel_x, W, H, bold_path)):
        draw_asset_panel(img, asset_key, panel_x, image_path=image_path)
    draw = ImageDraw.Draw(img)

    font_eyebrow = ImageFont.truetype(bold_path, 28)
    font_title   = ImageFont.truetype(DISPLAY_FONT or bold_path, 66)
    font_bullet  = ImageFont.truetype(reg_path,  38)
    font_small   = ImageFont.truetype(reg_path,  24)
    font_host    = ImageFont.truetype(reg_path,  24)

    draw.text((80, 70), f"{SERIES_NAME_ZH} · {SERIES_NAME_EN}", font=font_small, fill=DARK_GRAY)
    draw.text((80, 110), f"CHAPTER {index:02d} / {total:02d}", font=font_eyebrow, fill=ACCENT_LT)
    draw_accent_line(draw, 155, 160)

    text_w   = panel_x - 110          # 文字欄保留與圖片的間距
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

    # 章節進度條：用有功能的元素填滿下方留白，順便把「第幾章 / 共幾章」
    # 從文字變成一眼可見的視覺資訊，觀眾知道自己看到哪裡了。
    bar_y, bar_h = H - 150, 4
    draw.rectangle([80, bar_y, 80 + text_w, bar_y + bar_h], fill=(26, 34, 54))
    done = int(text_w * index / max(total, 1))
    draw.rectangle([80, bar_y, 80 + done, bar_y + bar_h], fill=ACCENT_LT)
    for i in range(1, total):                      # 每章一個刻度
        tick = 80 + int(text_w * i / total)
        draw.rectangle([tick, bar_y - 3, tick + 1, bar_y + bar_h + 3], fill=BG)

    draw_logo_watermark(draw, font_small, right_edge=80 + text_w)
    img.save(out_path)

def make_cta_slide(quote, cta_question, bold_path, reg_path, out_path):
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_bg_gradient(img)

    font_tag   = ImageFont.truetype(reg_path,  24)
    font_cta   = ImageFont.truetype(DISPLAY_FONT or bold_path, 50)
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


    img.save(out_path)

# ── Claude API ───────────────────────────────────────────────────────────────
def get_today_topic():
    """從 50 個智慧製造概念的知識圖譜選出本集題目

    每集是「主概念 × 相關概念 × 切入視角」的交會點，而不是單講一個名詞，
    所以有限的概念能持續展開成新內容（實測 10 年內 289 集不重複）。
    """
    tw_now   = datetime.now(timezone(timedelta(hours=8)))
    date_str = tw_now.strftime("%Y-%m-%d")

    primary, partner, lens = topics.pick_episode(tw_now.date())
    title, tag, angle = topics.describe(primary, partner, lens)

    print(f"📅 日期：{date_str}（第 {topics.week_index(tw_now.date())} 週）")
    print(f"📌 本集題目：{title}")
    print(f"   維度：{topics.DIMENSIONS[primary['dim']]} × {topics.DIMENSIONS[partner['dim']]}")
    print(f"   切入視角：{lens[0]}")
    return title, tag, angle, date_str

ICON_ENUM_HINT = "gear / sensor / chip / heat / data / network / check / warning / cycle / robot / idea / factory"
PHOTO_ENUM_HINT = " / ".join(f"{k}（{v['desc']}）" for k, v in ASSETS.items())
DIAGRAM_HINT = "\n".join(f"  * {k}：{v}" for k, v in diagrams.DIAGRAM_TYPES.items())

def extract_script_json(msg):
    """從回應中取出腳本 JSON

    回應裡不只有答案：思考開啟時 content[0] 可能是 thinking block，
    開放網頁搜尋後還會夾雜搜尋結果區塊與模型的說明文字。
    直接把所有 text 串起來會讓 JSON 解析失敗，所以逐層退讓：
    整段能解析就用整段，否則取最外層的大括號區間。
    """
    raw = "".join(
        b.text for b in msg.content
        if getattr(b, "type", None) == "text" and getattr(b, "text", None)
    ).strip()

    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) > 1:
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]
    raw = raw.strip()

    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass

    # 退而求其次：取第一個 { 到最後一個 } 之間，剝掉前後的說明文字
    start, end = raw.find("{"), raw.rfind("}")
    return raw[start:end + 1] if start != -1 and end > start else raw


def generate_video_script(topic_title, topic_angle):
    print(f"🤖 呼叫 {SCRIPT_MODEL} 生成 12-14 分鐘長片腳本...")
    ac = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""你是《{SERIES_NAME_ZH}》（{SERIES_NAME_EN}）節目的編劇，這是一個雙主持人對談節目：
主持人 A 是男性，理性冷靜，擅長拆解數據與物理/成本根本原理；
主持人 B 是女性，擅長追問、幫觀眾把疑惑問出來，並把原理連結到實際應用場景。
兩人要像真人來回討論，B 可以質疑、驚訝、追問，A 再進一步解釋——不是兩人各自唸稿。

目標受眾：製造業從業者、工程師、科技創業者，以及對特斯拉/馬斯克式創新邏輯有興趣的知識型觀眾。
風格：快節奏、語氣像在拆解一個被大家誤解的行業迷思。

── 節目的核心論點（整個系列共用的脊椎，每一集都要服膺它）──
這個節目存在的理由，是用第一性原理**重新定義智慧製造**，而不是介紹一堆技術名詞。

業界現行的定義是一份採購清單，而且是典型的類比推理：
  「裝感測器 ＋ 全廠聯網 ＋ 加上 AI ＝ 工業 4.0 ＝ 智慧製造」
它回答的是「要買什麼」，不是「為什麼」。所以工廠花了大錢，卻說不出到底變聰明在哪裡。

本節目主張的定義，是從製造的物理與經濟本質推導出來的：
  製造的本質，是把物質重新排列成更高價值的形態。
  而所有的浪費，最終都來自同一件事——**決策發生的當下，資訊不足或來得太晚**。
  因此：

    ★ 智慧製造 ＝ 讓決策所需的資訊，在決策發生的地點與時刻就位。★

  它跟「買了多少設備」無關，跟「資訊與決策之間的距離」有關。

這個定義會推導出一切，每一集都要用它當試金石：
  - 感測器的價值，只在於它產出「與某個決策相關」的資訊；量了沒人用的數據是零
  - 網路與邊緣運算的價值，只在於把資訊在「還來得及反應」的時間內送到
  - AI 的價值，只在於把資料變成決策；做不出決策的模型只是昂貴的報表
  - 沒有人會依據它採取行動的儀表板，價值為零——無論它多好看
  - 自動化若沒縮短這個距離，只是把原本愚蠢的動作做得更快

所以每一集在談它的主題時，都要回答同一個問題：
**這項技術，究竟縮短了「哪一個決策」與「哪一份資訊」之間的距離？**
如果答不出來，就要誠實指出它在多數工廠其實是浪費——這種誠實正是本節目的價值所在。

── 改善的執行順序：馬斯克五步演算法（與核心論點互補）──
核心論點回答「智慧製造是什麼」，這套演算法回答「該用什麼順序做」。
五個步驟**有嚴格先後，不可跳過、不可調換**：

  1. 質疑要求 —— 每一條規格都要問「這是誰訂的、為什麼」。
     要求必須掛上一個「人名」，不能是「部門的要求」或「業界慣例」。
     出自聰明人的要求最危險，因為沒有人敢質疑。
  2. 刪除 —— 能刪的零件、製程、工序、報表，一律先刪掉。
     檢驗刪得夠不夠的標準：如果後來沒有被迫加回大約 10%，就是刪得不夠。
  3. 簡化／優化 —— **只有做完前兩步才能做這一步**。
     聰明工程師最常犯的錯，就是去優化一個根本不該存在的東西。
  4. 加快速度 —— 縮短週期時間。但在前三步之前加速，只是更快地做錯事。
  5. 自動化 —— **放在最後**。

本節目對這套演算法的核心主張：
  ★ 台灣製造業最普遍的浪費，就是直接從第 5 步開始——
    把不該存在的流程自動化、為不該存在的零件買機械手臂。★
  馬斯克自己在 Model 3 產線上就犯過這個錯：過度自動化導致產能地獄，
  後來他公開承認「人類被低估了」。連他都會在第 5 步跌倒，這正是最好的警示。

這套演算法要實際用在以下地方，不要只是提一次名詞：
  - 第三幕每個維度的 beat B（第一性原理拆解），要明確對應到第 1、2 步
  - 第三幕每個維度的 beat C（智慧製造應用），要說清楚是在第 3、4、5 步的哪一步
  - 第四幕（盲點警示）要檢驗：這個主題有沒有跳步的風險？
  - **sop_steps 必須依照這五步的順序排列**，先質疑與刪除，最後才談自動化

── 這支影片同時要達成兩個目標，缺一不可 ──
【教育目標】觀眾看完要帶走一個「可以自己拿去用」的思考工具，而不只是聽了一集有趣的故事。
  具體要求：每個維度的「第一性原理拆解」beat，都要示範一個**可以套用到任何產業的提問句**
  （例如：「這個成本裡，有多少是物理必然，有多少只是歷史習慣？」）。
  觀眾應該能在自己的工作現場複述這個問題。寧可把一個觀念講透，也不要蜻蜓點水講五個。

【行銷目標】看完後，觀眾對欣晨工業應該產生的印象是：
  「這是一家真正懂製造本質、而且能把原理落地成實體設備的公司」——而不是「這家公司很會打廣告」。
  達成方式是**展現思考深度**，不是增加曝光次數。因此：
  - **正片完全不要提到欣晨**。開場、核心觀念、三大維度、反思這四幕都是純粹的教學內容，
    一次都不要出現公司名稱或產品。觀眾在學東西的時候不該被廣告打斷。
  - **只有第五幕結語可以帶出欣晨**，而且只用一到兩句話，做法是：
    把本集拆解出的原理，連回欣晨實際在做的事，讓它成為「這個原理有人真的做出來了」的例證，
    而不是「順便介紹一下我們公司」。
  - 可動用的可信度資產：1996 年創立、30 年精密製造經驗、以 TPS 為核心哲學、
    1200°C 工業加熱器、熱電偶、一體式料管、碳化矽保護管、機械手臂整合、AOI 視覺檢測
    （挑與本集主題最相關的一項，不要列清單）
  - 前面十分鐘的內容夠強，片尾這一句才有說服力。順序不能顛倒。

欣晨工業是台灣桃園1996年創立的精密自動化設備製造商，以豐田生產方式（TPS）為核心哲學。
主要業務：工業加熱器（1200°C）、熱電偶、一體式料管、碳化矽保護管、機械手臂整合、AOI視覺檢測。

今日主題：{topic_title}
角度提示：{topic_angle}

── 寫作方法：第一性原理（Elon Musk 式 First Principles Reasoning）──
不要用「業界都這麼說」「大家習慣這樣做」之類的類比式推論（reasoning by analogy）堆砌內容。
可以引用特斯拉 Giga Factory、一體化壓鑄（Giga Press）等公開案例作為示範性佐證；但如果今日主題離汽車製造較遠，
就改用更貼切、可驗證的業界標竿案例，不要每集都硬套特斯拉——落地的主角終究要回到今日主題與欣晨工業的技術領域。

── 全片架構（總長約 12-14 分鐘，五幕，缺一不可）──
第一幕 Hook 開場（約 60 秒）：用一個強烈對比畫面感破題（例如：傳統工廠的沉悶堆積 vs 高度自動化產線的特寫），
  點出一個大家以為是「錢」或「資源」的問題，但其實是「思考方式」的問題，拋出全片要拆解的疑問，並說明本集主旨。
第二幕 核心觀念（約 2 分鐘，2 個 beats）：解釋「類比推理」vs「第一性原理」的差異——
  beat 1：業界迷思是什麼樣的類比推理（「大家都外包」「行業標準就是這個價」）；
  beat 2：製造的物理本質（把原物料重新排列組合成更高價值的形狀/功能）與經濟本質（減少能量損耗、時間成本、搬運無效率）。
第三幕 三大維度案例拆解（約 7-8 分鐘，3 個維度 x 各 3 個 beats＝9 個 beats）：
  維度依序為「產線設計」「數據與軟體」「供應鏈與物流」，每個維度都要包含恰好 3 個 beats：
    beat A：傳統做法是什麼、為什麼大家這樣做
    beat B：第一性原理拆解——問「為什麼非得這樣？」，拆到物理/成本/資料的根本限制
    beat C：智慧製造應用——拆解後得出的新做法，落回今日主題。這裡仍是教學，不要提到任何公司名稱
第四幕 深度反思與盲點警示（約 2 分鐘，2 個 beats）：
  beat 1：盲目套用第一性原理的風險——不是所有工廠都該追求極致自動化/一體化，高客製化、小批量的工廠反而可能資本支出回不來；
  beat 2：第一性原理的終極考量是「資本效率」，不是為拆解而拆解。
第五幕 Outro 結語（約 60 秒，1 個 cta）：這是全片唯一可以提到欣晨工業的地方。
  結語的順序是：先用金句收束本集原理 → 再用一到兩句把這個原理連回欣晨實際在做的事
  （例證式，不是自我介紹）→ 最後邀請觀眾留言。
  一句濃縮全片核心的金句（例如精神類似「智慧製造的終點不是買最貴的機器人，而是敢不敢把現有的行業規矩歸零重來」，但要換成貼合今日主題的原創金句）；
  再加一個邀請觀眾留言互動的 CTA 問句（例如精神類似「你所在的產業，有哪些『大家都這麼做』的潛規則？留言告訴我們」，換成貼合今日主題的原創版本）。

請以 JSON 格式輸出，嚴格遵守以下結構。"dialogue" 都是陣列，每個元素是 {{"speaker":"A"或"B","line":"該句台詞"}}，
A/B 要交替來回（不是A講完全部再B講全部）。字數都是口語唸出的字數，不是書面字數：
{{
  "video_title": "影片主標題（18-28字）。標題是觀眾唯一的進入點，必須讓他在三秒內知道『看完我會得到什麼』。結構＝具體主題＋可驗證的結果或代價。只有好奇心、看不出效益的標題不合格。例：『IIoT 導入順序搞錯，三年白花錢：先接一個溫度點就夠』。反例：『工業物聯網，別從網路開始』（有懸念但不知道能學到什麼）、『淺談智慧製造』（兩者皆無）。不要用驚嘆號或『震驚』『必看』這類詞。",
  "hook_dialogue": [ {{"speaker":"A","line":"..."}}, {{"speaker":"B","line":"..."}}, ... ]  // 3-4 輪對話，總字數約230-260字（唸出約55-62秒）
  ,
  "concept_beats": [
    {{ "title": "beat標題（12字內）", "icon": "{ICON_ENUM_HINT} 其中一個", "photo": "{PHOTO_ENUM_HINT} 其中一個的代號", "image_prompt": "英文，描述這段要搭配的畫面", "diagram": {{"type":"...","labels":["...","..."]}} 或 null,
       "bullets": ["重點短句1（14-22字，要是讀得通的完整短句，不是關鍵字堆疊）","重點短句2（14-22字）"],
       "dialogue": [ {{"speaker":"A","line":"..."}}, {{"speaker":"B","line":"..."}}, ... ] }}  // 總字數約230-260字（約55-62秒）
    // 正好 2 個，對應核心觀念 beat1、beat2
  ],
  "dimensions": [
    {{ "name": "產線設計", "icon": "{ICON_ENUM_HINT} 其中一個",
       "beats": [
         {{ "label": "傳統做法", "photo": "素材代號", "image_prompt": "英文畫面描述", "diagram": {{"type":"...","labels":[...]}} 或 null, "bullets": ["...","..."], "dialogue": [...] }},   // 總字數約175-205字（約41-48秒）
         {{ "label": "第一性原理拆解", "photo": "素材代號", "image_prompt": "英文畫面描述", "diagram": {{"type":"...","labels":[...]}} 或 null, "bullets": ["...","..."], "dialogue": [...] }},
         {{ "label": "智慧製造應用", "photo": "素材代號", "image_prompt": "英文畫面描述", "diagram": {{"type":"...","labels":[...]}} 或 null, "bullets": ["...","..."], "dialogue": [...] }}
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
  "outro_dialogue": [ {{"speaker":"A","line":"..."}}, {{"speaker":"B","line":"..."}}, ... ]  // 3-4 輪，總字數約230-260字（約55-62秒），口語版的結語。順序：收束原理 → 用一兩句把原理連回欣晨實際做的事（全片唯一一次提到公司）→ 邀請留言。不用唸出電話或網址，畫面會顯示聯絡資訊
  ,
  "key_points": ["本集重點1", "本集重點2", "..."],
  "sop_steps": ["步驟1", "步驟2", "..."],
  "benefits": ["效益1", "效益2", "..."],
  "fb_caption": "Facebook 貼文說明（300-400字）。這是觀眾滑過動態牆時唯一會先看到的文字，要能獨立成立。結構：第一行用一句反直覺的鉤子讓人停下來（不要寫「本集介紹…」這種開頭）；中段用 2-3 句說明這集拆解了什麼、觀眾會學到哪個可複用的思考工具；接著一句不推銷的可信度陳述（欣晨 30 年精密製造的實作視角）；最後用影片的互動問句邀請留言。專業、不說教、不用驚嘆號堆疊。\\n\\n#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5"
}}

要求：
- 繁體中文，口語自然、像真人對話（這是要被語音合成唸出來的雙主持人台詞，不是書面文章）

── 先查資料，再動筆（這個節目必須與時俱進）──
你有網頁搜尋工具。動筆前**先針對今日主題搜尋 2-4 次**，弄清楚：
  - 這個技術在最近一兩年的實際進展、成熟度、普及程度
  - 有沒有具體、可查證的案例、數據或價格水準
  - 業界現在真正在爭論或踩雷的點是什麼
觀眾是製造業從業者，他們分辨得出「教科書式的通論」和「真的在追這個領域的人」。
搜尋到的內容要融進論證裡，不要只是把新聞唸一遍。
查不到可靠資料的主張，就改用物理與成本推理，不要硬掰。

── 事實準確性（最高優先，違反會毀掉整個頻道的可信度）──
這支影片會以欣晨工業的名義公開發布。捏造的數據一旦被同業指出來，傷害遠大於內容無聊。
- 數字優先來自剛剛搜尋到的可查證來源；查得到就給精確值，查不到才退回數量級
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
- diagram 是這段的「圖解」，**比照片重要得多**：教學型內容靠結構圖傳達關係，照片只能營造氣氛。
  只要這段在講「關係、流程、層次、對比、數量差距」，就一定要給 diagram；
  真的只是在描述現場場景時才留空（填 null）。格式為
  {{"type":"類型","labels":["標籤1","標籤2",...],"icons":["圖示1","圖示2",...]}}，可用類型：
{DIAGRAM_HINT}
  icons 可選填，長度與 labels 相同，每個從前述 icon 清單挑一個視覺上貼切的，
  flow 與 layers 會把它畫成方塊左側的圖示徽章；不填就改用序號，兩者都好看。
  標籤規則：每個標籤 4-8 個字、是名詞或動作短語，不要寫整句話；
  bars 類型的每個標籤寫成「名稱|數值」，例如 "傳統沖壓焊接|70 個零件"。
  圖解必須和該段 bullets 講的是同一件事，不要另起爐灶。
- key_points / sop_steps / benefits 是影片說明欄的骨幹，要能**脫離影片獨立閱讀**，
  讓沒看完影片的人光讀說明也學得到東西（說明欄會被搜尋索引，是引流的關鍵）：
  * key_points：5-10 條本集重點。每條 20-40 字，是完整的陳述句，要帶具體的量級或條件，
    不要寫「導入 IIoT 很重要」這種廢話。順序照影片推進。
  * sop_steps：5-8 個「明天就能開始做」的執行步驟，**必須依照馬斯克五步演算法的順序**
    （質疑→刪除→簡化→加快→自動化），不要一開頭就叫人買設備。每條 25-50 字，要有明確的動作與
    可驗收的產出（例如「先挑一台稼動率最低的機台，只接一個溫度點，連續記錄兩週」）。
    不要寫成抽象原則，要寫成一個廠務主管看得懂、能排進行程的動作。
  * benefits：3-5 條執行後的實際效益。要講清楚「省到什麼、省多少量級、多久看得到」，
    無法量化時就講可驗證的狀態改變，不要寫「提升競爭力」這種無法檢驗的話。
- 欣晨工業的置入規則見前述【行銷目標】，嚴格遵守「最多 3 次、只在應用 beat、必須自然銜接」
- 只輸出JSON，不要前言說明"""

    last_err = None
    feedback = ""
    for attempt in range(1, SCRIPT_RETRIES + 1):
        # 腳本決定整支影片的教育價值與行銷品質，是最值得投資的一環。
        # 相對於生圖成本（約 $0.47/支），換上最強模型每支只多約 $0.12。
        # Opus 5.5 思考永遠開啟，effort 預設是 medium，這裡明確拉到 high；
        # 思考 token 會計入 max_tokens，所以改用串流並放寬上限，避免 JSON 被截斷。
        # 開放網頁搜尋，讓每一集都能接上該主題的當下發展，而不是只複述
        # 訓練資料裡的通論。這也讓「數字要有根據」從靠記憶變成可查證。
        with ac.messages.stream(
            model=SCRIPT_MODEL,
            max_tokens=32000,
            output_config={"effort": "high"},
            tools=[{"type": "web_search_20260209", "name": "web_search",
                    "max_uses": WEB_SEARCH_MAX_USES}],
            messages=[{"role": "user", "content": prompt + feedback}],
        ) as stream:
            msg = stream.get_final_message()

        if msg.stop_reason == "max_tokens":
            last_err = "輸出被 max_tokens 截斷，JSON 不完整"
            print(f"   ⚠️  腳本生成第 {attempt}/{SCRIPT_RETRIES} 次：{last_err}")
            feedback = "\n\n【上次失敗】輸出過長被截斷，請縮短台詞總字數後重新輸出完整 JSON。"
            continue

        raw = extract_script_json(msg)
        try:
            script = json.loads(raw)
            validate_script(script)
            return script
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            print(f"   ⚠️  腳本生成第 {attempt}/{SCRIPT_RETRIES} 次不合格：{e}")
            # 盲目重試只會再寫出一份同樣的腳本，必須告訴它哪裡不合格
            feedback = f"\n\n【上次失敗的原因，請針對這點修正後重新輸出】\n{e}"

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

def validate_script(script, check_length=True):
    """上線前先驗證腳本結構

    配音與算圖要跑數十分鐘，結構錯誤必須在這裡就擋下來，
    而不是等到跑了一半才拋 KeyError。
    """
    for key in ("video_title", "hook_dialogue", "concept_beats", "dimensions",
                "reflection_beats", "outro_quote", "outro_cta_question",
                "outro_dialogue", "fb_caption", "key_points", "sop_steps", "benefits"):
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

    # 片長檢查的目的是約束 Claude 的產出；用現成腳本測試流程時不適用
    est = estimate_script_seconds(script)
    if check_length and not (SCRIPT_EST_MIN <= est <= SCRIPT_EST_MAX):
        raise ValueError(
            f"腳本粗估片長 {est/60:.1f} 分鐘，超出可接受範圍 "
            f"{SCRIPT_EST_MIN/60:.1f}-{SCRIPT_EST_MAX/60:.1f} 分鐘"
        )

# ── 語音旁白（雙主持人對話）──────────────────────────────────────────────────
def _tts_edge(text, voice, out_path):
    """edge-tts：微軟 Azure 官方台灣中文語音，母語腔調"""
    import asyncio, edge_tts

    async def _run():
        await edge_tts.Communicate(text, voice).save(str(out_path))

    asyncio.run(_run())


def _tts_openai(text, voice, out_path):
    """OpenAI TTS：端點穩定但聲線是英語母語，唸中文有外國腔，僅作備援"""
    from openai import OpenAI
    resp = OpenAI(api_key=os.environ["OPENAI_API_KEY"]).audio.speech.create(
        model=TTS_MODEL, voice=voice, input=text,
        response_format="mp3", speed=TTS_SPEED,
    )
    Path(out_path).write_bytes(resp.read())


def synthesize_line(text, voice, out_path, retries=TTS_RETRIES):
    """生成單句語音

    單次執行要發約 50 次請求，偶發網路失敗屬正常；
    這裡逐次退避重試，避免一句失敗就讓整個長片流程報銷。
    來源由 ACTIVE_TTS 決定，整支影片一致，不會中途換聲線。
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("旁白台詞為空，無法配音")

    fn = _tts_edge if ACTIVE_TTS["provider"] == "edge" else _tts_openai
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            fn(text, voice, out_path)
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

    # 逐句配音的副產物：每句的實際長度已知，字幕時間軸可以精確算出來，
    # 不必靠語音辨識回推。這裡回傳相對於本段開頭的 (起, 迄, 台詞)。
    cues, t = [], 0.0
    for k, (turn, lp) in enumerate(zip(dialogue, line_paths)):
        dur = get_audio_duration(lp)
        cues.append((t, t + dur, turn["line"].strip()))
        t += dur + (DIALOGUE_GAP if k < len(line_paths) - 1 else 0)
    return out_path, cues

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
    if UPLOAD_TEST:
        print("📤 上傳測試模式：跳過 Facebook（FB 沒有不公開上傳可用）")
        return None
    page_id = os.environ["FB_PAGE_ID"]
    token   = os.environ["FB_ACCESS_TOKEN"]

    print("📤 上傳影片到 Facebook...")
    with open(video_path, "rb") as vf:
        resp = requests.post(
            f"https://graph-video.facebook.com/v25.0/{page_id}/videos",
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
        scopes=YT_SCOPES,
    )
    creds.refresh(GoogleRequest())

    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    # 標題前置：搜尋結果約 60 字就截斷，開頭字元最珍貴。
    # 原本的「【智慧製造】」前綴與英文品牌後綴會把效益擠出顯示範圍。
    yt_title = f"{slide_title}｜欣晨工業"
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
                # 測試用 unlisted（中文介面「不公開」）而非 private（「私人」）：
                # private 只有頻道擁有者登入後看得到，審片的人拿到連結也打不開；
                # unlisted 憑連結就能看，但不進搜尋、不出現在頻道頁。
                "privacyStatus":           "unlisted" if UPLOAD_TEST else "public",
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

def preflight_check():
    """開跑前先驗證金鑰

    配音是流程最後才用到 OpenAI，但金鑰無效時整支影片已經跑了好幾分鐘、
    腳本的模型費用也付掉了。這裡用一次免費的 models.list() 先確認，
    讓失敗在幾秒內發生而不是七分鐘後。
    """
    print("🔑 檢查金鑰…")
    missing = [k for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY") if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"缺少必要的環境變數：{', '.join(missing)}")

    key = os.environ["OPENAI_API_KEY"]
    if key != key.strip():
        # GitHub Secret 會原樣保存貼上的內容，多一個換行就會 401
        print("   ⚠️  OPENAI_API_KEY 前後有空白字元，已自動去除")
        os.environ["OPENAI_API_KEY"] = key.strip()

    # 只印長度與前綴，不印任何金鑰內容：長度足以看出是否貼到截斷的 key，
    # 而 GitHub 的遮罩對完整字串才有效，印出片段反而會造成外洩。
    k = os.environ["OPENAI_API_KEY"]
    prefix = "sk-proj-" if k.startswith("sk-proj-") else ("sk-" if k.startswith("sk-") else "（非 sk- 開頭）")
    print(f"   OPENAI_API_KEY：長度 {len(k)}、前綴 {prefix}")

    from openai import OpenAI
    try:
        OpenAI(api_key=os.environ["OPENAI_API_KEY"]).models.list()
    except Exception as e:                      # noqa: BLE001
        raise RuntimeError(
            f"OPENAI_API_KEY 無法通過驗證：{e}\n"
            "請到 https://platform.openai.com/api-keys 重新產生，"
            "並更新 repo 的 OPENAI_API_KEY secret（注意結尾不要帶換行或空白）"
        ) from None
    print("   ✅ 金鑰可用")

    # 探測配音來源：edge-tts 腔調自然但走非官方端點，先試一句短的確認可用；
    # 不通就整支改用 OpenAI，而不是跑到一半才發現、或讓同一支影片混用兩種聲線。
    if ACTIVE_TTS["provider"] == "edge":
        probe = Path(tempfile.gettempdir()) / "_tts_probe.mp3"
        try:
            _tts_edge("測試", VOICES["edge"]["A"], probe)
            if not (probe.exists() and probe.stat().st_size > 0):
                raise RuntimeError("edge-tts 回傳空音檔")
            print("🎙️  配音來源：edge-tts（台灣中文原生語音）\n")
        except Exception as e:                  # noqa: BLE001
            ACTIVE_TTS["provider"] = "openai"
            HOST_VOICES.update(VOICES["openai"])
            print(f"   ⚠️  edge-tts 無法使用（{str(e)[:80]}），改用 OpenAI TTS")
            print("🎙️  配音來源：OpenAI TTS（備援，中文腔調較不自然）\n")
        finally:
            probe.unlink(missing_ok=True)
    else:
        print(f"🎙️  配音來源：{ACTIVE_TTS['provider']}\n")

def _hms(seconds):
    """YouTube 章節格式：未滿一小時用 M:SS，超過才用 H:MM:SS"""
    total = int(seconds)
    h, m, sec = total // 3600, (total % 3600) // 60, total % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def build_description(script, chapters):
    """組出說明欄：重點、SOP、效益、章節

    這段要能脫離影片獨立閱讀——說明欄會被搜尋索引，是引流的主要入口，
    而且沒看完影片的人也該帶得走東西。
    章節時間軸由實際段落長度算出，不是請模型猜的。
    """
    NL = "\n"
    parts = [script["fb_caption"].split("#")[0].strip()]

    if script.get("key_points"):
        parts.append("【本集重點】" + NL + NL.join(
            f"{i}. {pt}" for i, pt in enumerate(script["key_points"], 1)))

    if script.get("sop_steps"):
        parts.append("【導入 SOP：明天就能開始】" + NL + NL.join(
            f"Step {i}　{st}" for i, st in enumerate(script["sop_steps"], 1)))

    if script.get("benefits"):
        parts.append("【執行效益】" + NL + NL.join(f"・{b}" for b in script["benefits"]))

    if chapters:
        # YouTube 章節規則：第一章必須是 0:00，且至少三章
        parts.append("【章節】" + NL + NL.join(
            f"{_hms(t)} {label}" for label, t in chapters))

    tags = "#" + script["fb_caption"].split("#", 1)[1] if "#" in script["fb_caption"] else ""
    if tags:
        parts.append(tags.strip())
    return (NL + NL).join(parts)


def _srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def build_srt(cues, texts=None):
    """由時間軸組出 SRT；texts 可換成其他語言，順序必須與 cues 一致"""
    lines = []
    for i, (start, end, zh) in enumerate(cues, 1):
        text = (texts[i - 1] if texts and i - 1 < len(texts) else zh).strip()
        if not text:
            continue
        lines.append(f"{i}")
        lines.append(f"{_srt_time(start)} --> {_srt_time(end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def translate_lines(lines, targets=("en", "ja")):
    """把台詞整批翻譯成其他語言

    逐句翻譯會失去上下文、也貴；整批送並要求回傳等長陣列，
    數量對不上就放棄該語言，不讓字幕錯位。
    """
    import anthropic as _a
    client = _a.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    names = {"en": "English", "ja": "Japanese"}
    out = {}
    for lang in targets:
        payload = json.dumps(lines, ensure_ascii=False)
        prompt = (
            "以下是一支繁體中文智慧製造教學影片的逐句字幕，JSON 陣列格式。\n"
            f"請翻成{names[lang]}，用於影片字幕：口語、簡潔、一句對一句。\n"
            "專有名詞（IIoT、OEE、SMED、AOI、PLC 等）保留原文。\n"
            "只輸出一個等長的 JSON 字串陣列，不要任何說明文字。\n\n"
            + payload
        )
        try:
            msg = client.messages.create(
                model=TRANSLATE_MODEL, max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
            start, end = raw.find("["), raw.rfind("]")
            got = json.loads(raw[start:end + 1])
            if len(got) != len(lines):
                raise ValueError(f"翻譯句數不符（{len(got)} vs {len(lines)}），會造成字幕錯位")
            out[lang] = got
            print(f"   ✅ {names[lang]} 字幕（{len(got)} 句）")
        except Exception as e:                      # noqa: BLE001
            print(f"   ⚠️  {names[lang]} 字幕翻譯失敗，略過：{e}")
    return out


def upload_captions(video_id, srt_files):
    """把字幕軌上傳到 YouTube

    captions.insert 需要 youtube.force-ssl 權限，比上傳影片的
    youtube.upload 更大。若現有 refresh token 權限不足，就只記錄警告，
    不讓字幕問題害掉已經成功上傳的影片。
    """
    if not video_id or not srt_files:
        return
    client_id     = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")
    if not all([client_id, client_secret, refresh_token]):
        return

    print("💬 上傳字幕軌...")
    try:
        creds = Credentials(
            token=None, refresh_token=refresh_token,
            client_id=client_id, client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=YT_SCOPES,
        )
        creds.refresh(GoogleRequest())
        youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    except Exception as e:                          # noqa: BLE001
        print(f"   ⚠️  字幕授權失敗，略過：{e}")
        return

    names = {"zh-TW": "繁體中文", "en": "English", "ja": "日本語"}
    for lang, body in srt_files.items():
        tmp_srt = Path(tempfile.gettempdir()) / f"cap_{lang}.srt"
        tmp_srt.write_text(body, encoding="utf-8")
        try:
            youtube.captions().insert(
                part="snippet",
                body={"snippet": {"videoId": video_id, "language": lang,
                                  "name": names.get(lang, lang), "isDraft": False}},
                media_body=MediaFileUpload(str(tmp_srt), mimetype="application/octet-stream"),
            ).execute()
            print(f"   ✅ {names.get(lang, lang)}")
        except Exception as e:                      # noqa: BLE001
            msg = str(e)
            if "insufficient" in msg.lower() or "forbidden" in msg.lower() or "403" in msg:
                print(f"   ⚠️  {lang} 失敗：YT_REFRESH_TOKEN 權限不足。"
                      "請用 scripts/get_youtube_token.py 重新授權（已含 force-ssl）")
            else:
                print(f"   ⚠️  {lang} 失敗：{msg[:160]}")
        finally:
            tmp_srt.unlink(missing_ok=True)


# ── 主程式 ───────────────────────────────────────────────────────────────────
def main():
    print("═══════════════════════════════════════════")
    print(f"  {SERIES_NAME_ZH} — 雙主持人長片自動發布")
    print("═══════════════════════════════════════════")

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    if dry_run:
        print("⚠️  DRY RUN：只產生影片，不上傳\n")

    preflight_check()

    topic_title, topic_tag, topic_angle, date_str = get_today_topic()

    # 1. 生成腳本
    #    FIXTURE_SCRIPT 指向一份現成的腳本 JSON，用來跳過這一步。
    #    腳本生成是唯一需要 Anthropic 的環節，跳過它就能在額度受限時
    #    仍然真實驗證其餘全部流程：生圖、圖解、字型、配音、算圖、
    #    字幕、以及真正的 FB / YouTube 上傳。
    fixture = os.environ.get("FIXTURE_SCRIPT")
    if fixture:
        script = json.loads(Path(fixture).read_text(encoding="utf-8"))
        validate_script(script, check_length=False)
        print(f"📄 使用現成腳本：{fixture}（跳過 Claude，不耗用 Anthropic 額度）")
    else:
        script = generate_video_script(topic_title, topic_angle)
    print(f"\n📝 影片主標：{script['video_title']}")
    for dim in script["dimensions"]:
        print(f"   維度：{dim['name']}")

    # 2. 載入字型
    bold_path, reg_path = load_fonts()
    global DISPLAY_FONT
    DISPLAY_FONT = load_display_font(bold_path)
    print(f"\n🔤 字型：標題 {Path(DISPLAY_FONT).name} ／ 內文 {Path(reg_path).name}")

    # 章節編號只算「有章節卡」的 beats：核心觀念 + 三維度 + 反思，不含 hook/outro
    total_chapters = len(script["concept_beats"]) \
        + sum(len(dim["beats"]) for dim in script["dimensions"]) \
        + len(script["reflection_beats"])
    chapter_idx = 0

    # 圖解覆蓋率：教學內容靠圖解傳達結構，退回照片的比例過高代表提示詞引導不夠
    _all_beats = (script["concept_beats"] + script["reflection_beats"]
                  + [b for d in script["dimensions"] for b in d["beats"]])
    _kinds = {}
    for _b in _all_beats:
        if isinstance(_b.get("diagram"), dict):
            _k = _b["diagram"].get("type", "?")
            _kinds[_k] = _kinds.get(_k, 0) + 1
    _n = sum(_kinds.values())
    print(f"📐 圖解覆蓋：{_n}/{len(_all_beats)} 段"
          + (f"（{', '.join(f'{k}×{v}' for k, v in sorted(_kinds.items()))}）" if _kinds else ""))

    # 3. 逐段生成語音旁白 + 畫面 + 合成片段
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 先依每段台詞生成專屬畫面；沒金鑰或生圖失敗都會退回 repo 內的本地素材
        images = {}
        if os.environ.get("OPENAI_API_KEY"):
            # 有圖解的段落在算圖時會優先畫圖解，那張生成圖根本不會出現在畫面上——
            # 所以直接跳過，不要花錢生一張必定被丟掉的圖。
            def _needs_image(beat):
                return not isinstance(beat.get("diagram"), dict)

            jobs = [("00_hook", script.get("hero_image_prompt") or script["concept_beats"][0].get("image_prompt"), "16:9")]
            for j, beat in enumerate(script["concept_beats"], 1):
                if _needs_image(beat):
                    jobs.append((f"01_concept_{j}", beat.get("image_prompt"), "4:5"))
            for d, dim in enumerate(script["dimensions"], 1):
                for j, beat in enumerate(dim["beats"], 1):
                    if _needs_image(beat):
                        jobs.append((f"02_dim{d}_{j}", beat.get("image_prompt"), "4:5"))
            for j, beat in enumerate(script["reflection_beats"], 1):
                if _needs_image(beat):
                    jobs.append((f"03_reflect_{j}", beat.get("image_prompt"), "4:5"))
            print(f"\n🖼️  依台詞生成畫面（{IMAGE_MODEL}，共 {len(jobs)} 張）")
            no_prompt = []
            for tag, prompt_text, aspect in jobs:
                if not prompt_text:
                    # 腳本沒給畫面描述，和「生圖失敗」是兩回事，要分開記
                    no_prompt.append(tag)
                    continue
                got = generate_beat_image(prompt_text, aspect, tmp / f"{tag}_gen.png")
                if got:
                    images[tag] = got
                    print(f"   ✅ {tag}")
            print(f"   生成 {len(images)}/{len(jobs)} 張，其餘用本地素材")
            if no_prompt:
                print(f"   ⚠️  有 {len(no_prompt)} 段腳本未提供 image_prompt：{', '.join(no_prompt)}")
        else:
            print("\n🖼️  未設定 GOOGLE_API_KEY，全部使用 repo 內素材")

        clip_paths = []
        chapters = []
        subtitles = []
        total_duration = 0.0

        def build_segment(tag, draw_fn, dialogue, label=None):
            nonlocal total_duration
            chapters.append((label or tag, total_duration))   # 起點＝先前累計長度
            seg_start = total_duration
            audio_path, cues = synthesize_dialogue(dialogue, tmp, tag)
            subtitles.extend((seg_start + a, seg_start + b, txt) for a, b, txt in cues)
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
            script["hook_dialogue"], label="開場",
        )

        # 第二幕：核心觀念
        for j, beat in enumerate(script["concept_beats"], 1):
            chapter_idx += 1
            build_segment(
                f"01_concept_{j}",
                lambda p, beat=beat, idx=chapter_idx, tag=f"01_concept_{j}": make_chapter_slide(
                    idx, total_chapters, beat["title"], beat["bullets"], beat["icon"],
                    beat["photo"], bold_path, reg_path, p, image_path=images.get(tag),
                    diagram=beat.get("diagram")
                ),
                beat["dialogue"], label=beat["title"],
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
                        beat["photo"], bold_path, reg_path, p, image_path=images.get(tag),
                    diagram=beat.get("diagram")
                    ),
                    beat["dialogue"], label=title,
                )

        # 第四幕：深度反思與盲點警示
        for j, beat in enumerate(script["reflection_beats"], 1):
            chapter_idx += 1
            build_segment(
                f"03_reflect_{j}",
                lambda p, beat=beat, idx=chapter_idx, tag=f"03_reflect_{j}": make_chapter_slide(
                    idx, total_chapters, beat["title"], beat["bullets"], beat["icon"],
                    beat["photo"], bold_path, reg_path, p, image_path=images.get(tag),
                    diagram=beat.get("diagram")
                ),
                beat["dialogue"], label=beat["title"],
            )

        # 第五幕：Outro 結語（金句 + CTA 問句）
        build_segment(
            "99_outro",
            lambda p: make_cta_slide(
                script["outro_quote"], script["outro_cta_question"], bold_path, reg_path, p
            ),
            script["outro_dialogue"], label="結語",
        )

        print(f"\n🎞️  共 {len(clip_paths)} 段，總長約 {total_duration/60:.1f} 分鐘")

        # 4. 串接所有片段
        video_path = tmp / f"hsinchan_{date_str}.mp4"
        concat_clips(clip_paths, video_path)

        # 5. 字幕：中文由時間軸直接產生，其他語言整批翻譯
        print(f"\n💬 產生字幕（{len(subtitles)} 句）")
        srt_files = {"zh-TW": build_srt(subtitles)}
        if SUBTITLE_LANGS:
            for lang, texts in translate_lines([c[2] for c in subtitles], SUBTITLE_LANGS).items():
                srt_files[lang] = build_srt(subtitles, texts)

        if dry_run:
            import shutil
            out = Path(f"hsinchan_video_{date_str}.mp4")
            shutil.copy(video_path, out)
            for lang, body in srt_files.items():
                Path(f"hsinchan_video_{date_str}.{lang}.srt").write_text(body, encoding="utf-8")
            print(f"\n✅ Dry run 完成，影片儲存為：{out}")
            print(f"   字幕：{'、'.join(srt_files)}")
            return

        # 6. 同時上傳 Facebook + YouTube
        print("\n── 上傳至各平台 ────────────────────────────")
        if UPLOAD_TEST:
            print("⚠️  上傳測試模式：YouTube 設為不公開、跳過 Facebook")
        description = build_description(script, chapters)
        fb_id = upload_video_to_facebook(str(video_path), description)
        yt_id = upload_video_to_youtube(
            str(video_path), script["video_title"],
            description, topic_tag, date_str
        )
        # 字幕軌必須在影片上傳完成、拿到 video_id 之後才能掛上去
        upload_captions(yt_id, srt_files)

        print(f"\n🎉 完成！{date_str} 影片已發布")
        if fb_id: print(f"   Facebook Video ID : {fb_id}")
        if yt_id: print(f"   YouTube Video ID  : {yt_id}  (https://youtu.be/{yt_id})")

if __name__ == "__main__":
    main()
