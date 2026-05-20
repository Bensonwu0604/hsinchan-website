#!/usr/bin/env python3
# trigger: 2026-05-20w
"""
欣晨工業 Podcast — HTML + Playwright 高品質視覺版
HTML/CSS 渲染投影片（接近 NotebookLM 品質）
OpenAI TTS: nova（小欣）x onyx（阿晨）
"""
import os, sys, json, subprocess, tempfile, shutil, math
from pathlib import Path
from datetime import datetime, timezone, timedelta

import anthropic
from openai import OpenAI
from playwright.sync_api import sync_playwright

# ── 常數 ─────────────────────────────────────────────────────────────────────
W, H          = 1920, 1080
VOICE_FEMALE  = "nova"
VOICE_MALE    = "onyx"
SILENCE_SEC   = 0.40
ANIM_FRAMES   = 4

# ── 字型路徑（系統 Noto CJK）────────────────────────────────────────────────
FONT_BOLD = next((p for p in [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
] if Path(p).exists()), "")

FONT_REG = next((p for p in [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
] if Path(p).exists()), "")

# ── HTML 投影片模板 ───────────────────────────────────────────────────────────
def build_chart_svg(chart_type, items):
    """依類型生成 SVG 圖表"""
    w, h = 520, 280
    colors = ["#5a8cff", "#00d4b4", "#b464ff", "#ffd764"]

    if chart_type == "pillars":
        n     = min(len(items), 4)
        cw    = w // n
        hvals = [0.85, 0.65, 0.90, 0.70]
        bars  = ""
        for i, label in enumerate(items[:n]):
            bx  = i * cw + 20
            bh2 = int((h - 60) * hvals[i % 4])
            col = colors[i % 4]
            bars += f"""
              <defs>
                <linearGradient id="g{i}" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="{col}" stop-opacity="1"/>
                  <stop offset="100%" stop-color="{col}" stop-opacity="0.2"/>
                </linearGradient>
              </defs>
              <rect x="{bx}" y="{h-40-bh2}" width="{cw-40}" height="{bh2}"
                    rx="6" fill="url(#g{i})"/>
              <circle cx="{bx+(cw-40)//2}" cy="{h-40-bh2}" r="6" fill="{col}"
                      style="filter:drop-shadow(0 0 8px {col})"/>
              <text x="{bx+(cw-40)//2}" y="{h-10}" text-anchor="middle"
                    font-size="22" fill="#8899cc">{label}</text>"""
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">{bars}</svg>'

    elif chart_type == "cycle":
        items4 = (items + ["","","",""])[:4]
        nodes  = ""
        cx2, cy2, R = w//2, h//2, 95
        for i, label in enumerate(items4):
            if not label: continue
            a   = math.radians(i*90 - 45)
            ex  = cx2 + int(R * math.cos(a))
            ey  = cy2 + int(R * math.sin(a))
            col = colors[i % 4]
            if i < 3:
                na  = math.radians((i+1)*90 - 45)
                nx  = cx2 + int(R * math.cos(na))
                ny  = cy2 + int(R * math.sin(na))
                nodes += f'<line x1="{ex}" y1="{ey}" x2="{nx}" y2="{ny}" stroke="{col}" stroke-width="2" stroke-opacity="0.4"/>'
            nodes += f"""
              <circle cx="{ex}" cy="{ey}" r="38" fill="#111830"
                      stroke="{col}" stroke-width="2"
                      style="filter:drop-shadow(0 0 10px {col}40)"/>
              <text x="{ex}" y="{ey+7}" text-anchor="middle"
                    font-size="20" fill="{col}" font-weight="bold">{label}</text>"""
        nodes += f'<circle cx="{cx2}" cy="{cy2}" r="30" fill="#111830" stroke="#5a8cff" stroke-width="2"/>'
        nodes += f'<text x="{cx2}" y="{cy2+6}" text-anchor="middle" font-size="16" fill="#5a8cff">改善</text>'
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">{nodes}</svg>'

    elif chart_type == "bars":
        n     = min(len(items), 4)
        bh2   = (h - 30) // n
        vals  = [(85,35),(90,40),(75,50),(80,90)]
        bars2 = ""
        for i, label in enumerate(items[:n]):
            by2        = 15 + i * bh2
            bef, aft   = vals[i % 4]
            col        = colors[i % 4]
            bw_b       = int((w-180) * bef/100)
            bw_a       = int((w-180) * aft/100)
            bars2 += f"""
              <text x="10" y="{by2+bh2//2+6}" font-size="18" fill="#8899cc">{label}</text>
              <rect x="160" y="{by2+6}" width="{bw_b}" height="{bh2//2-10}"
                    rx="4" fill="#1e2d50"/>
              <rect x="160" y="{by2+bh2//2+2}" width="{bw_a}" height="{bh2//2-10}"
                    rx="4" fill="{col}" style="filter:drop-shadow(0 0 4px {col}60)"/>
              <text x="{160+bw_a+8}" y="{by2+bh2//2+bh2//4+6}"
                    font-size="16" fill="{col}">{aft}%</text>"""
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">{bars2}</svg>'

    elif chart_type == "stats":
        n     = min(len(items), 3)
        sw    = w // n
        stats = ""
        for i, val in enumerate(items[:n]):
            sx  = i * sw + sw//2
            col = colors[i % 4]
            stats += f"""
              <circle cx="{sx}" cy="{h//2}" r="85"
                      fill="{col}18" stroke="{col}40" stroke-width="1"/>
              <text x="{sx}" y="{h//2+8}" text-anchor="middle"
                    font-size="52" fill="{col}" font-weight="bold">{val}</text>
              <line x1="{sx-35}" y1="{h//2+42}" x2="{sx+35}" y2="{h//2+42}"
                    stroke="{col}80" stroke-width="2"/>"""
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">{stats}</svg>'

    elif chart_type == "flow":
        n   = min(len(items), 4)
        fw  = (w - 30) // n
        fls = ""
        for i, label in enumerate(items[:n]):
            bx  = 15 + i * fw
            col = colors[i % 4]
            fls += f"""
              <rect x="{bx}" y="{h//2-40}" width="{fw-28}" height="80"
                    rx="12" fill="#111830" stroke="{col}" stroke-width="2"
                    style="filter:drop-shadow(0 0 8px {col}40)"/>
              <text x="{bx+(fw-28)//2}" y="{h//2+8}" text-anchor="middle"
                    font-size="22" fill="{col}" font-weight="bold">{label}</text>"""
            if i < n-1:
                ax = bx + fw - 10
                ay = h//2
                fls += f'<polygon points="{ax},{ay-14} {ax+20},{ay} {ax},{ay+14}" fill="{col}80"/>'
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">{fls}</svg>'

    return '<svg width="520" height="280"></svg>'


def build_avatar_svg(is_female, active, anim_phase):
    """SVG 半身主持人插圖"""
    alpha   = 1.0 if active else 0.22
    skin_f  = f"rgba(238,196,165,{alpha})"
    skin_m  = f"rgba(215,175,142,{alpha})"
    hair_f  = f"rgba(38,28,22,{alpha})"
    hair_m  = f"rgba(50,38,28,{alpha})"
    top_f   = f"rgba(145,75,225,{alpha})"
    top_f2  = f"rgba(175,105,250,{alpha})"
    top_m   = f"rgba(22,48,95,{alpha})"
    top_m2  = f"rgba(42,68,118,{alpha})"
    tie_m   = f"rgba(185,40,40,{alpha})"
    glow_c  = "#b464ff" if is_female else "#00c8b4"
    skin    = skin_f if is_female else skin_m
    hair    = hair_f if is_female else hair_m
    top     = top_f  if is_female else top_m
    top2    = top_f2 if is_female else top_m2

    # 呼吸動畫偏移
    bob = int(math.sin(anim_phase * math.pi * 2) * 7)

    glow = f"""
      <radialGradient id="av_glow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{glow_c}" stop-opacity="{0.25*alpha}"/>
        <stop offset="100%" stop-color="{glow_c}" stop-opacity="0"/>
      </radialGradient>
      <ellipse cx="200" cy="300" rx="200" ry="280" fill="url(#av_glow)"/>
    """ if active else ""

    if is_female:
        svg = f"""<svg viewBox="0 0 400 620" width="340" height="530"
                       style="transform:translateY({bob}px);transition:transform 0.4s ease">
          <defs>
            <linearGradient id="top_grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="{top2}"/>
              <stop offset="100%" stop-color="{top}"/>
            </linearGradient>
          </defs>
          {glow}
          <!-- 長髮（後方）-->
          <ellipse cx="148" cy="195" rx="32" ry="95" fill="{hair}"/>
          <ellipse cx="252" cy="195" rx="32" ry="95" fill="{hair}"/>
          <ellipse cx="200" cy="108" rx="72" ry="55" fill="{hair}"/>
          <!-- 頭部 -->
          <ellipse cx="200" cy="135" rx="62" ry="75" fill="{skin}"/>
          <!-- 眉毛 -->
          <path d="M174 105 Q187 98 200 103" stroke="{hair}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
          <path d="M200 103 Q213 98 226 105" stroke="{hair}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
          <!-- 眼睛 -->
          <ellipse cx="178" cy="125" rx="13" ry="10" fill="white"/>
          <ellipse cx="178" cy="125" rx="7" ry="8" fill="#2a1e15"/>
          <ellipse cx="175" cy="122" rx="2.5" ry="2.5" fill="white"/>
          <ellipse cx="222" cy="125" rx="13" ry="10" fill="white"/>
          <ellipse cx="222" cy="125" rx="7" ry="8" fill="#2a1e15"/>
          <ellipse cx="219" cy="122" rx="2.5" ry="2.5" fill="white"/>
          <!-- 睫毛 -->
          <path d="M168 115 L165 109" stroke="{hair}" stroke-width="1.8"/>
          <path d="M178 114 L178 107" stroke="{hair}" stroke-width="1.8"/>
          <path d="M188 116 L190 109" stroke="{hair}" stroke-width="1.8"/>
          <path d="M212 116 L210 109" stroke="{hair}" stroke-width="1.8"/>
          <path d="M222 114 L222 107" stroke="{hair}" stroke-width="1.8"/>
          <path d="M232 115 L235 109" stroke="{hair}" stroke-width="1.8"/>
          <!-- 鼻子 -->
          <path d="M196 148 Q200 158 204 148" stroke="{skin}" stroke-width="2" fill="none" opacity="0.6"/>
          <!-- 嘴巴（微笑）-->
          <path d="M186 165 Q200 177 214 165" stroke="rgba(175,92,92,0.9)" stroke-width="3" fill="none" stroke-linecap="round"/>
          <!-- 頸部 -->
          <rect x="186" y="208" width="28" height="40" rx="8" fill="{skin}"/>
          <!-- 肩膀/上衣 -->
          <path d="M110 248 L290 248 L270 430 L130 430 Z" fill="url(#top_grad)"/>
          <!-- V領 -->
          <path d="M176 252 L200 295 L224 252" fill="{top2}"/>
          <!-- 左臂（自然）-->
          <path d="M115 258 L82 268 L58 360 L84 368 L105 280 L128 268 Z" fill="url(#top_grad)"/>
          <ellipse cx="72" cy="374" rx="18" ry="14" fill="{skin}"/>
          <!-- 右臂（舉起手勢，動畫）-->
          <path d="M285 258 L318 250 L{'345' if anim_phase<0.5 else '338'} {'175' if anim_phase<0.5 else '185'} L{'318' if anim_phase<0.5 else '312'} {'170' if anim_phase<0.5 else '180'} L292 240 L272 268 Z" fill="url(#top_grad)"/>
          <ellipse cx="{'352' if anim_phase<0.5 else '344'}" cy="{'166' if anim_phase<0.5 else '175'}" rx="18" ry="14" fill="{skin}"/>
        </svg>"""
    else:
        svg = f"""<svg viewBox="0 0 400 620" width="340" height="530"
                       style="transform:translateY({bob}px);transition:transform 0.4s ease">
          <defs>
            <linearGradient id="suit_grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="{top2}"/>
              <stop offset="100%" stop-color="{top}"/>
            </linearGradient>
          </defs>
          {glow}
          <!-- 短髮 -->
          <ellipse cx="200" cy="112" rx="70" ry="48" fill="{hair}"/>
          <ellipse cx="148" cy="148" rx="22" ry="30" fill="{hair}"/>
          <ellipse cx="252" cy="148" rx="22" ry="30" fill="{hair}"/>
          <!-- 頭部 -->
          <ellipse cx="200" cy="145" rx="65" ry="78" fill="{skin}"/>
          <!-- 眉毛（平直）-->
          <line x1="173" y1="112" x2="197" y2="110" stroke="{hair}" stroke-width="4.5" stroke-linecap="round"/>
          <line x1="203" y1="110" x2="227" y2="112" stroke="{hair}" stroke-width="4.5" stroke-linecap="round"/>
          <!-- 眼睛 -->
          <ellipse cx="178" cy="132" rx="14" ry="10" fill="white"/>
          <ellipse cx="178" cy="132" rx="8" ry="8" fill="#2a1e15"/>
          <ellipse cx="175" cy="129" rx="2.5" ry="2.5" fill="white"/>
          <ellipse cx="222" cy="132" rx="14" ry="10" fill="white"/>
          <ellipse cx="222" cy="132" rx="8" ry="8" fill="#2a1e15"/>
          <ellipse cx="219" cy="129" rx="2.5" ry="2.5" fill="white"/>
          <!-- 鼻子 -->
          <path d="M196 158 Q200 170 208 165" stroke="{skin}" stroke-width="2.5" fill="none" opacity="0.65"/>
          <!-- 嘴巴 -->
          <path d="M186 180 Q200 191 214 180" stroke="rgba(160,85,85,0.9)" stroke-width="3" fill="none" stroke-linecap="round"/>
          <!-- 頸部 -->
          <rect x="185" y="220" width="30" height="42" rx="8" fill="{skin}"/>
          <!-- 西裝 -->
          <path d="M105 262 L295 262 L275 440 L125 440 Z" fill="url(#suit_grad)"/>
          <!-- 西裝翻領 -->
          <path d="M175 264 L158 310 L118 268 Z" fill="{top2}"/>
          <path d="M225 264 L242 310 L282 268 Z" fill="{top2}"/>
          <!-- 白襯衫 -->
          <path d="M192 268 L208 268 L205 335 L195 335 Z" fill="rgba(215,225,245,0.9)"/>
          <!-- 領帶 -->
          <path d="M195 275 L205 275 L202 340 L198 340 Z" fill="{tie_m}"/>
          <path d="M193 337 L207 337 L202 355 L198 355 Z" fill="{tie_m}"/>
          <!-- 左臂 -->
          <path d="M110 272 L78 282 L52 375 L80 382 L102 292 L125 278 Z" fill="url(#suit_grad)"/>
          <ellipse cx="66" cy="388" rx="18" ry="14" fill="{skin}"/>
          <!-- 右臂（指向，動畫）-->
          <path d="M290 272 L322 258 L{'358' if anim_phase<0.5 else '348'} {'182' if anim_phase<0.5 else '194'} L{'336' if anim_phase<0.5 else '326'} {'176' if anim_phase<0.5 else '188'} L298 248 L275 278 Z" fill="url(#suit_grad)"/>
          <!-- 食指指向 -->
          <ellipse cx="{'368' if anim_phase<0.5 else '358'}" cy="{'172' if anim_phase<0.5 else '183'}" rx="18" ry="13" fill="{skin}"/>
          <line x1="{'368' if anim_phase<0.5 else '358'}" y1="{'160' if anim_phase<0.5 else '170'}" x2="{'385' if anim_phase<0.5 else '375'}" y2="{'142' if anim_phase<0.5 else '152'}" stroke="{skin}" stroke-width="11" stroke-linecap="round"/>
        </svg>"""
    return svg


def build_slide_html(slide, speaker, dialogue_text, anim_phase):
    """生成一張投影片的完整 HTML"""
    is_female   = (speaker == "Host1")
    spk_name    = "小欣" if is_female else "阿晨"
    spk_role    = "女主持人" if is_female else "男主持人"
    spk_color   = "#b464ff" if is_female else "#00c8b4"
    glow_color  = "#7b30c8" if is_female else "#008878"

    avatar_svg  = build_avatar_svg(is_female, True,  anim_phase)
    chart_svg   = build_chart_svg(slide.get("chart_type","pillars"),
                                  slide.get("chart_items",[]))
    cards_html  = ""
    for i, card in enumerate(slide.get("cards",[])[:3]):
        col = ["#5a8cff","#00d4b4","#b464ff"][i]
        cards_html += f"""
        <div class="card" style="--c:{col}">
          <div class="card-top" style="background:{col}"></div>
          <div class="card-label" style="color:{col}">
            <span class="dot" style="background:{col}"></span>{card['label']}
          </div>
          <div class="card-sep" style="background:{col}33"></div>
          <div class="card-text">{card['text']}</div>
        </div>"""

    # 字幕（一行截斷）
    subtitle_html = ""
    if dialogue_text:
        # 截斷到約 55 個中文字的長度（確保一行）
        txt = dialogue_text[:56] + ("…" if len(dialogue_text) > 56 else "")
        subtitle_html = f"""
        <div class="subtitle">
          <span class="sub-name" style="color:{spk_color}">{spk_name}</span>
          <span class="sub-text">{txt}</span>
        </div>"""

    font_css = ""
    if FONT_BOLD:
        font_css = f"""
        @font-face {{
          font-family: 'NotoSans';
          src: url('file://{FONT_BOLD}');
          font-weight: 700;
        }}"""
    if FONT_REG:
        font_css += f"""
        @font-face {{
          font-family: 'NotoSans';
          src: url('file://{FONT_REG}');
          font-weight: 400;
        }}"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{font_css}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1920px; height: 1080px; overflow: hidden;
  font-family: 'NotoSans', 'Noto Sans TC', sans-serif;
  background: #06081a;
  color: #e8eeff;
}}
/* ── 背景光暈 ── */
.bg {{
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 55% 65% at 22% 48%, {glow_color}22 0%, transparent 65%),
    radial-gradient(ellipse 50% 60% at 78% 52%, #0a3a3a22 0%, transparent 60%),
    linear-gradient(160deg, #06081a 0%, #0c1230 50%, #06081a 100%);
}}
.grid {{
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(80,100,180,0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(80,100,180,0.07) 1px, transparent 1px);
  background-size: 80px 80px;
}}
/* ── 頂部品牌欄 ── */
.topbar {{
  position: absolute; top: 0; left: 0; right: 0; height: 52px;
  background: rgba(6,8,26,0.92);
  display: flex; align-items: center;
  padding: 0 44px;
  border-bottom: 2px solid #5a8cff;
  box-shadow: 0 0 20px #5a8cff40;
  z-index: 10;
}}
.brand {{ font-weight: 700; font-size: 22px; color: #e8eeff; }}
.ep    {{ font-size: 20px; color: #8899cc; margin-left: 28px; }}
.slide-no {{ margin-left: auto; font-size: 20px; color: #445580; }}
/* ── 分隔線 ── */
.divider {{
  position: absolute; top: 52px; bottom: 158px; left: 840px; width: 1px;
  background: linear-gradient(180deg, transparent 0%, #334488 20%, #334488 80%, transparent 100%);
  z-index: 5;
}}
/* ── 左側：主持人 ── */
.avatar-panel {{
  position: absolute; top: 52px; left: 0; width: 840px; bottom: 158px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 0;
}}
.avatar-wrap {{
  filter: drop-shadow(0 0 30px {spk_color}50);
}}
.host-name {{
  font-size: 36px; font-weight: 700; color: {spk_color};
  margin-top: 8px;
  text-shadow: 0 0 20px {spk_color}80;
}}
.host-role {{ font-size: 22px; color: #556688; margin-top: 4px; }}
/* ── 右側：投影片內容 ── */
.content-panel {{
  position: absolute; top: 62px; left: 868px; right: 28px; bottom: 168px;
  display: flex; flex-direction: column; gap: 0;
  overflow: hidden;
}}
.slide-title {{
  font-size: 52px; font-weight: 700; color: #eef2ff;
  line-height: 1.2; margin-bottom: 8px;
  text-shadow: 0 2px 20px rgba(90,140,255,0.3);
}}
.title-bar {{
  width: 200px; height: 3px; margin-bottom: 14px;
  background: linear-gradient(90deg, #5a8cff, transparent);
  box-shadow: 0 0 12px #5a8cff80;
}}
.chart-area {{ flex: 0 0 auto; margin-bottom: 12px; }}
.cards-area {{
  flex: 1 1 auto;
  display: flex; flex-direction: column; gap: 10px;
  min-height: 0;
}}
/* ── 卡片 ── */
.card {{
  flex: 1 1 0; min-height: 0;
  background: rgba(16,22,50,0.85);
  border: 1px solid var(--c, #5a8cff)33;
  border-radius: 14px; padding: 10px 16px;
  display: flex; flex-direction: column; gap: 4px;
  backdrop-filter: blur(8px);
  box-shadow: 0 0 16px var(--c, #5a8cff)20, inset 0 1px 0 rgba(255,255,255,0.05);
  overflow: hidden;
}}
.card-top {{ height: 4px; border-radius: 4px; margin: -10px -16px 6px; }}
.card-label {{
  font-size: 22px; font-weight: 700; display: flex; align-items: center; gap: 8px;
}}
.dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
.card-sep {{ height: 1px; margin: 2px 0; }}
.card-text {{ font-size: 21px; color: #c8d4ec; line-height: 1.5; }}
/* ── 底部字幕 ── */
.subtitle-bar {{
  position: absolute; left: 0; right: 0; bottom: 0; height: 155px;
  background: linear-gradient(180deg, rgba(6,8,22,0.92) 0%, rgba(3,4,14,0.98) 100%);
  border-top: 2px solid #5a8cff;
  box-shadow: 0 0 24px #5a8cff50;
  display: flex; align-items: center; justify-content: center;
  padding: 0 60px;
}}
.subtitle {{
  display: flex; align-items: baseline; gap: 16px;
  max-width: 1800px;
}}
.sub-name {{
  font-size: 28px; font-weight: 700;
  white-space: nowrap;
  text-shadow: 0 0 12px currentColor;
}}
.sub-text {{
  font-size: 38px; color: #eef2ff; line-height: 1.2;
  white-space: nowrap; overflow: hidden;
}}
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="grid"></div>
  <!-- 頂部 -->
  <div class="topbar">
    <span class="brand">欣晨工業有限公司</span>
    <span class="ep">智慧製造深度對談 SMART MANUFACTURING DEEP DIVE</span>
    <span class="slide-no">SLIDE {slide['id']}</span>
  </div>
  <!-- 左右分隔 -->
  <div class="divider"></div>
  <!-- 左：主持人 -->
  <div class="avatar-panel">
    <div class="avatar-wrap">{avatar_svg}</div>
    <div class="host-name">{spk_name}</div>
    <div class="host-role">{spk_role}</div>
  </div>
  <!-- 右：投影片內容 -->
  <div class="content-panel">
    <div class="slide-title">{slide['title']}</div>
    <div class="title-bar"></div>
    <div class="chart-area">{chart_svg}</div>
    <div class="cards-area">{cards_html}</div>
  </div>
  <!-- 底部字幕 -->
  <div class="subtitle-bar">{subtitle_html}</div>
</body>
</html>"""


def html_to_png(html_content, out_path):
    """Playwright 截圖"""
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox","--disable-setuid-sandbox"])
        page    = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.set_content(html_content, wait_until="networkidle")
        page.wait_for_timeout(300)   # 等字型渲染
        page.screenshot(path=str(out_path), clip={"x":0,"y":0,"w":1920,"h":1080})
        browser.close()


# ── 腳本生成 ─────────────────────────────────────────────────────────────────
def generate_script(ac_client):
    prompt = """你是欣晨工業 Podcast「智慧製造深度對談」資深製作人。
主持人：小欣（女，活潑好奇，善於追問）、阿晨（男，資深工程師，深入解說）
欣晨工業：台灣桃園，1975年，51年精密製造，TPS核心哲學。

今集：豐田改善文化（Kaizen）在台灣製造業的實踐

【起承轉合結構，目標10-13分鐘】
- 起（6輪）：衝擊開場＋引出主題，開頭要有震撼數字或反直覺問題
- 承（12輪）：深入 Kaizen/TPS 概念，台灣工廠真實案例，數據豐富
- 轉（6輪）：反轉——台灣企業導入改善的陷阱，阿晨給破解之道，小欣有驚嘆反應
- 合（8-10輪）：欣晨實踐，給聽眾3個行動建議，最後呼應開場形成收尾結圓

請輸出：
=== SLIDES ===
[{"id":1,"title":"標題（10字）","chart_type":"stats",
  "chart_items":["數值","數值","關鍵詞"],
  "cards":[{"label":"現象","text":"35字"},{"label":"核心問題","text":"35字"},{"label":"今集重點","text":"35字"}],
  "dialogue_count":6}
  ...共6張，chart_type: pillars/cycle/bars/stats/flow]

=== DIALOGUE ===
小欣: （80-100字）
阿晨: （80-100字）
共32-36輪，總字數約2600-3200字
繁體中文，口語自然，直接輸出不要說明"""

    print("Claude Sonnet 生成腳本（起承轉合）...")
    msg = ac_client.messages.create(
        model="claude-sonnet-4-6", max_tokens=6000,
        messages=[{"role":"user","content":prompt}]
    )
    raw = msg.content[0].text.strip()

    slides, dialogue = [], []
    if "=== SLIDES ===" in raw and "=== DIALOGUE ===" in raw:
        parts = raw.split("=== DIALOGUE ===")
        sp    = parts[0].split("=== SLIDES ===")[1].strip()
        dp    = parts[1].strip()
        try:
            j1=sp.index("["); j2=sp.rindex("]")+1
            slides = json.loads(sp[j1:j2])
        except:
            slides = default_slides()
        for line in dp.split("\n"):
            for pfx,spk in [("小欣:","Host1"),("小欣：","Host1"),
                            ("阿晨:","Host2"),("阿晨：","Host2")]:
                if line.strip().startswith(pfx):
                    t = line.strip()[len(pfx):].strip()
                    if t: dialogue.append({"speaker":spk,"text":t}); break
    else:
        slides = default_slides()
        for line in raw.split("\n"):
            for pfx,spk in [("小欣:","Host1"),("小欣：","Host1"),
                            ("阿晨:","Host2"),("阿晨：","Host2")]:
                if line.strip().startswith(pfx):
                    t = line.strip()[len(pfx):].strip()
                    if t: dialogue.append({"speaker":spk,"text":t}); break

    if not dialogue: raise ValueError("無法解析對話")

    seg_map, si, cnt = {}, 0, 0
    for i in range(len(dialogue)):
        seg_map[i] = min(si, len(slides)-1)
        cnt += 1
        if si < len(slides) and cnt >= slides[si].get("dialogue_count",6):
            si = min(si+1, len(slides)-1); cnt = 0

    total = sum(len(d["text"]) for d in dialogue)
    print(f"腳本完成：{len(slides)} 張投影片，{len(dialogue)} 輪，{total} 字（約 {total//155:.0f} 分鐘）")
    return slides, dialogue, seg_map


def default_slides():
    return [
        {"id":1,"title":"你的工廠每天浪費多少？","chart_type":"stats",
         "chart_items":["30%","7種","51年"],
         "cards":[{"label":"驚人事實","text":"研究顯示：製造業平均有30%以上的活動是不創造價值的浪費。"},
                  {"label":"核心問題","text":"為何工廠年復一年知道問題存在，卻難以持續改善？"},
                  {"label":"今集解答","text":"豐田用51年打造的Kaizen哲學，台灣工廠能複製嗎？"}],
         "dialogue_count":6},
        {"id":2,"title":"Kaizen 改善核心哲學","chart_type":"pillars",
         "chart_items":["改善","JIT","自働化"],
         "cards":[{"label":"定義","text":"每天比昨天進步一點點，不是大革命，而是持續的微進化積累。"},
                  {"label":"七大浪費","text":"過量生產、等待、運輸、庫存、動作、加工過度、不良品。"},
                  {"label":"現地現物","text":"不信二手報告，親自到現場，用眼確認、用手丈量。"}],
         "dialogue_count":6},
        {"id":3,"title":"TPS 豐田生產系統","chart_type":"cycle",
         "chart_items":["Plan","Do","Check","Act"],
         "cards":[{"label":"PDCA 循環","text":"計劃→執行→確認→行動，改善是螺旋式向上的過程。"},
                  {"label":"JIT 即時生產","text":"正確時間、數量、品項，消除庫存浪費，生產線暢流。"},
                  {"label":"Jidoka 自働化","text":"設備自動偵測異常並停機，品質從製程中建立而非檢驗。"}],
         "dialogue_count":6},
        {"id":4,"title":"台灣工廠的改善困境","chart_type":"bars",
         "chart_items":["導入成功","持續執行","員工認同","管理支持"],
         "cards":[{"label":"反直覺事實","text":"80%的改善計畫3個月後停止——不是方法錯，是文化沒跟上。"},
                  {"label":"最大誤解","text":"許多人以為改善等於裁員，豐田的改善從不以裁員為目標。"},
                  {"label":"破解關鍵","text":"改善要從讓人更輕鬆出發，而非讓人更拼命。"}],
         "dialogue_count":6},
        {"id":5,"title":"欣晨工業的 Kaizen 實踐","chart_type":"flow",
         "chart_items":["現地現物","問題分析","方案設計","驗證改善"],
         "cards":[{"label":"現場第一","text":"每個專案前，欣晨工程師必定親赴客戶廠房，現場丈量真實需求。"},
                  {"label":"設計改善","text":"SMED縮短換線、Poka-yoke防呆、SOP標準化三位一體。"},
                  {"label":"成果數字","text":"客戶平均換線時間減少60%，不良品率降低45%。"}],
         "dialogue_count":7},
        {"id":6,"title":"立刻可做的 3 個行動","chart_type":"stats",
         "chart_items":["今天","本週","本月"],
         "cards":[{"label":"今天就做","text":"走到現場，找1件每天覺得麻煩的事，問它「為什麼？」五次。"},
                  {"label":"本週完成","text":"和團隊一起畫出一道工序的流程，標出哪裡是浪費。"},
                  {"label":"本月啟動","text":"選一個問題，用 PDCA 解決它，記錄改善前後的數字。"}],
         "dialogue_count":7},
    ]

# ── TTS ───────────────────────────────────────────────────────────────────────
def audio_duration(path):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json",
                        "-show_format",str(path)], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def generate_all_audio(dialogue, tmp_dir):
    oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    tmp = Path(tmp_dir)
    print(f"OpenAI TTS 生成 {len(dialogue)} 段音訊...")
    segments = []
    for i, turn in enumerate(dialogue):
        voice = VOICE_FEMALE if turn["speaker"]=="Host1" else VOICE_MALE
        out   = tmp/f"seg_{i:03d}.mp3"
        resp  = oai.audio.speech.create(model="tts-1", voice=voice,
                                        input=turn["text"], speed=0.95)
        resp.stream_to_file(str(out))
        dur = audio_duration(out)
        segments.append({"path":str(out),"speaker":turn["speaker"],
                          "text":turn["text"],"duration":dur})
        if (i+1)%5==0: print(f"   {i+1}/{len(dialogue)} 段完成")
    print("TTS 完成")
    return segments

def concat_full_audio(segments, tmp_dir):
    tmp = Path(tmp_dir)
    silence = tmp/"silence.mp3"
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=24000:cl=mono",
                    "-t",str(SILENCE_SEC),"-q:a","9","-acodec","libmp3lame",str(silence)],
                   capture_output=True, check=True)
    lst = tmp/"audio_list.txt"
    with open(lst,"w") as f:
        for s in segments: f.write(f"file '{s['path']}'\nfile '{silence}'\n")
    full = tmp/"full_audio.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0",
                    "-i",str(lst),"-c","copy",str(full)], capture_output=True, check=True)
    total = sum(s["duration"]+SILENCE_SEC for s in segments)
    print(f"音訊完成：{total/60:.1f} 分鐘")
    return str(full), total

# ── 影片合成 ─────────────────────────────────────────────────────────────────
def render_video(slides, seg_map, segments, audio_path, total_dur, tmp_dir, out_path):
    tmp = Path(tmp_dir)
    n   = len(segments)
    print(f"Playwright 渲染 {n * ANIM_FRAMES} 張 HTML 投影片...")

    concat_lines = []
    prev_slide   = -1

    for i, seg in enumerate(segments):
        slide_idx = seg_map.get(i, len(slides)-1)
        slide     = slides[slide_idx]
        dur       = seg["duration"] + SILENCE_SEC
        fdur      = dur / ANIM_FRAMES

        # 投影片切換：淡黑過場
        if slide_idx != prev_slide and prev_slide >= 0:
            blk = tmp/f"black_{i}.png"
            with sync_playwright() as p:
                b = p.chromium.launch(args=["--no-sandbox"])
                pg = b.new_page(viewport={"width":1920,"height":1080})
                pg.set_content("<html><body style='margin:0;background:#030408;width:1920px;height:1080px'></body></html>")
                pg.screenshot(path=str(blk))
                b.close()
            concat_lines.append(f"file '{blk}'\nduration 0.28")

        for af in range(ANIM_FRAMES):
            anim_phase = af / ANIM_FRAMES
            frame      = tmp/f"frame_{i:03d}_{af}.png"
            html       = build_slide_html(slide, seg["speaker"], seg["text"], anim_phase)
            html_to_png(html, frame)
            concat_lines.append(f"file '{frame}'\nduration {fdur:.3f}")

        prev_slide = slide_idx
        if (i+1) % 3 == 0:
            print(f"   {i+1}/{n} 段完成")

    concat_lines.append(f"file '{tmp}/frame_{n-1:03d}_{ANIM_FRAMES-1}.png'")
    cf = tmp/"frames.txt"; cf.write_text("\n".join(concat_lines))

    print("FFmpeg 合成影片...")
    silent = tmp/"silent.mp4"
    r1 = subprocess.run(
        ["ffmpeg","-y","-f","concat","-safe","0","-i",str(cf),
         "-vf","fps=24,scale=1920:1080",
         "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",str(silent)],
        capture_output=True, text=True)
    if r1.returncode != 0: raise RuntimeError(f"FFmpeg 靜音：{r1.stderr[-400:]}")

    r2 = subprocess.run(
        ["ffmpeg","-y","-i",str(silent),"-i",str(audio_path),
         "-map","0:v","-map","1:a",
         "-c:v","libx264","-preset","fast","-crf","22",
         "-c:a","aac","-b:a","128k",
         "-pix_fmt","yuv420p","-t",str(total_dur),str(out_path)],
        capture_output=True, text=True)
    if r2.returncode != 0: raise RuntimeError(f"FFmpeg 最終：{r2.stderr[-400:]}")

    size = Path(out_path).stat().st_size/1024/1024
    print(f"影片完成：{size:.0f} MB，{total_dur/60:.1f} 分鐘")

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    print("="*60)
    print("  欣晨工業 Podcast — HTML+Playwright 高品質視覺版")
    print("  起承轉合結構 | OpenAI TTS nova x onyx")
    print("="*60+"\n")

    tw2  = datetime.now(timezone(timedelta(hours=8)))
    date = tw2.strftime("%Y-%m-%d")
    ac   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        slides, dialogue, seg_map = generate_script(ac)
        segments  = generate_all_audio(dialogue, tmpdir)
        audio_path, total_dur = concat_full_audio(segments, tmpdir)
        video_out = Path(tmpdir)/f"test_podcast_{date}.mp4"
        render_video(slides, seg_map, segments, audio_path, total_dur, tmpdir, video_out)
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
