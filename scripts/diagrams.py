#!/usr/bin/env python3
"""
欣晨工業 —《第一性原理拆解智慧製造》示意圖繪製

為什麼用程式畫而不是 AI 生圖：
  1. 教學型內容靠圖解傳達結構，照片只能營造氣氛
  2. AI 生圖畫不好帶文字的示意圖，中文標籤幾乎必定變亂碼
  3. 程式畫的線條乾淨、標籤精準、風格與整片一致

由編劇（Claude）決定圖解類型與標籤文字，這裡負責把它畫準。
"""

from PIL import ImageDraw, ImageFont

# 由 generate_video 注入，避免兩邊的品牌色不同步
BG = (10, 13, 21)
ACCENT = (26, 63, 152)
ACCENT_LT = (59, 130, 246)
WHITE = (240, 244, 248)
GRAY = (138, 155, 174)
DARK_GRAY = (55, 70, 90)

# 圖解類型與它適合表達的關係（這份說明會餵給編劇，讓它挑對類型）
DIAGRAM_TYPES = {
    "flow":    "線性流程：A 造成 B、B 造成 C。用在講一連串因果、製程順序，或馬斯克五步演算法。需要 3-5 個標籤。",
    "loop":    "閉環循環：最後一步回饋到第一步。用在講閉環控制、持續改善、數據回饋。需要 3-4 個標籤。",
    "layers":  "堆疊層級：下層支撐上層。用在講架構分層（感測層／邊緣層／控制層）。需要 3-4 個標籤，由下往上排。",
    "compare": "左右對比：傳統做法 vs 拆解後的做法。用在講迷思與反轉。需要正好 2 個標籤。",
    "bars":    "數量對比：用長度呈現差距。用在講成本、工時、零件數的倍率差異。需要 2-3 個「標籤|數值」字串。",
}


def _fit_font(draw, text, font_path, max_w, start, min_size=20):
    """把字級縮到塞得進指定寬度為止"""
    size = start
    while size > min_size:
        f = ImageFont.truetype(font_path, size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(font_path, min_size)


def _box(draw, x, y, w, h, label, font_path, fill_bg=True):
    """圓角方塊＋置中標籤"""
    r = 14
    if fill_bg:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=(18, 28, 54), outline=ACCENT_LT, width=3)
    else:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=r, outline=DARK_GRAY, width=3)
    f = _fit_font(draw, label, font_path, w - 40, 34)
    bb = draw.textbbox((0, 0), label, font=f)
    draw.text((x + (w - (bb[2] - bb[0])) / 2, y + (h - (bb[3] - bb[1])) / 2 - bb[1]),
              label, font=f, fill=WHITE)


def _arrow_down(draw, cx, y0, y1, color=ACCENT_LT, width=4):
    draw.line([cx, y0, cx, y1], fill=color, width=width)
    head = 13
    draw.polygon([(cx, y1), (cx - head, y1 - head), (cx + head, y1 - head)], fill=color)


def _draw_flow(draw, box, labels, font_path):
    x, y, w, h = box
    n = len(labels)
    gap = 54
    bh = min((h - gap * (n - 1)) // n, 150)
    total = bh * n + gap * (n - 1)
    cy = y + (h - total) // 2
    for i, label in enumerate(labels):
        top = cy + i * (bh + gap)
        _box(draw, x, top, w, bh, label, font_path)
        if i < n - 1:
            _arrow_down(draw, x + w // 2, top + bh + 8, top + bh + gap - 8)


def _draw_loop(draw, box, labels, font_path):
    """環形排列，箭頭首尾相接，最後一步回到第一步"""
    import math
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    radius = min(w, h) / 2 - 95
    n = len(labels)
    pts = []
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        pts.append((cx + math.cos(ang) * radius, cy + math.sin(ang) * radius))

    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        pad = 78
        sx, sy = x0 + dx / L * pad, y0 + dy / L * pad
        ex, ey = x1 - dx / L * pad, y1 - dy / L * pad
        draw.line([sx, sy, ex, ey], fill=ACCENT_LT, width=4)
        ang = math.atan2(ey - sy, ex - sx)
        head = 14
        draw.polygon([
            (ex, ey),
            (ex - head * math.cos(ang - 0.5), ey - head * math.sin(ang - 0.5)),
            (ex - head * math.cos(ang + 0.5), ey - head * math.sin(ang + 0.5)),
        ], fill=ACCENT_LT)

    for (px, py), label in zip(pts, labels):
        r = 72
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(18, 28, 54), outline=ACCENT_LT, width=3)
        f = _fit_font(draw, label, font_path, r * 1.8, 30, 18)
        bb = draw.textbbox((0, 0), label, font=f)
        draw.text((px - (bb[2] - bb[0]) / 2, py - (bb[3] - bb[1]) / 2 - bb[1]), label, font=f, fill=WHITE)


def _draw_layers(draw, box, labels, font_path):
    """由下往上堆疊，下層較寬，表達「下層支撐上層」"""
    x, y, w, h = box
    n = len(labels)
    gap = 26
    bh = min((h - gap * (n - 1)) // n, 130)
    total = bh * n + gap * (n - 1)
    top0 = y + (h - total) // 2
    for i, label in enumerate(labels):           # labels[0] 是最底層
        shrink = int((n - 1 - i) * 0)            # 等寬較穩重，不做梯形
        bx = x + shrink
        bw = w - shrink * 2
        top = top0 + (n - 1 - i) * (bh + gap)
        _box(draw, bx, top, bw, bh, label, font_path)


def _draw_compare(draw, box, labels, font_path):
    """上下兩塊對比，中間以「VS」分隔"""
    x, y, w, h = box
    bh = min((h - 120) // 2, 230)
    top_y = y + (h - (bh * 2 + 120)) // 2

    _box(draw, x, top_y, w, bh, labels[0], font_path, fill_bg=False)
    f = ImageFont.truetype(font_path, 40)
    bb = draw.textbbox((0, 0), "VS", font=f)
    draw.text((x + (w - (bb[2] - bb[0])) / 2, top_y + bh + 34), "VS", font=f, fill=ACCENT_LT)
    _box(draw, x, top_y + bh + 120, w, bh, labels[1], font_path)


def _draw_bars(draw, box, items, font_path):
    """水平長條對比，長度正比於數值，用來呈現倍率差距"""
    x, y, w, h = box
    parsed = []
    for it in items:
        label, _, value = str(it).partition("|")
        parsed.append((label.strip(), value.strip() or ""))

    nums = []
    for _, v in parsed:
        digits = "".join(c for c in v if c.isdigit() or c == ".")
        nums.append(float(digits) if digits else 1.0)
    peak = max(nums) or 1

    n = len(parsed)
    gap = 70
    bh = 64
    total = n * (bh + 52) + gap * (n - 1)
    cy = y + (h - total) // 2
    f_lab = ImageFont.truetype(font_path, 32)
    f_val = ImageFont.truetype(font_path, 30)
    for i, ((label, value), num) in enumerate(zip(parsed, nums)):
        top = cy + i * (bh + 52 + gap)
        draw.text((x, top), label, font=f_lab, fill=WHITE)
        bar_y = top + 50
        draw.rounded_rectangle([x, bar_y, x + w, bar_y + bh], radius=8, fill=(18, 24, 40))
        bw = max(int(w * num / peak), 12)
        draw.rounded_rectangle([x, bar_y, x + bw, bar_y + bh], radius=8, fill=ACCENT_LT)
        if value:
            draw.text((x + 18, bar_y + (bh - 38) / 2), value, font=f_val, fill=BG if bw > 140 else WHITE)


_RENDERERS = {
    "flow": _draw_flow,
    "loop": _draw_loop,
    "layers": _draw_layers,
    "compare": _draw_compare,
    "bars": _draw_bars,
}


def draw_diagram(img, spec, x0, W, H, font_path):
    """把圖解畫進畫面右側欄；spec 不合法回傳 False，讓呼叫端退回照片"""
    if not isinstance(spec, dict):
        return False
    kind = spec.get("type")
    labels = spec.get("labels")
    if kind not in _RENDERERS or not isinstance(labels, list) or len(labels) < 2:
        return False
    labels = [str(l).strip() for l in labels if str(l).strip()]
    if len(labels) < 2:
        return False
    if kind == "compare":
        labels = labels[:2]
    elif kind == "flow":
        labels = labels[:5]        # 馬斯克五步演算法需要容納 5 步
    else:
        labels = labels[:4]

    draw = ImageDraw.Draw(img)
    pad_x, pad_y = 90, 150
    box = (x0 + pad_x, pad_y, W - x0 - pad_x * 2, H - pad_y * 2)
    _RENDERERS[kind](draw, box, labels, font_path)
    return True
