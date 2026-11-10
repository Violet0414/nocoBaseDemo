# -*- coding: utf-8 -*-
"""生成文字版品牌图：党校智慧管理平台（Pillow 实现，无需浏览器）
产物：logo.png（亮色字/透明底）、logo-dark.png（暗色字/透明底）、favicon.png（党字红底圆角方块）
用法：F:/Python/python.exe gen_logo.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
PUBLIC = OUT.parent.parent / "main" / "public"

BOLD_FONT = r"C:\Windows\Fonts\msyhbd.ttc"  # 微软雅黑 Bold

TEXT = "党校智慧管理平台"
FONT_SIZE = 88
LETTER_SPACING = 6  # 字间距（px）
PAD = 14

DARK_COLOR = (24, 24, 27, 255)      # zinc-900，浅色底用
LIGHT_COLOR = (250, 250, 250, 255)  # zinc-50，深色底用


def draw_wordmark(color):
    font = ImageFont.truetype(BOLD_FONT, FONT_SIZE)
    # 逐字测量（含间距），算总宽
    widths = []
    for ch in TEXT:
        bbox = font.getbbox(ch)
        widths.append(bbox[2] - bbox[0])
    total_w = sum(widths) + LETTER_SPACING * (len(TEXT) - 1)
    ascent, descent = font.getmetrics()
    text_h = ascent + descent

    img = Image.new("RGBA", (total_w + PAD * 2, text_h + PAD * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x = PAD
    for ch, w in zip(TEXT, widths):
        bbox = font.getbbox(ch)
        draw.text((x - bbox[0], PAD), ch, font=font, fill=color)
        x += w + LETTER_SPACING
    return img


def rounded_gradient_favicon(size=256, radius=56):
    """红色渐变圆角方块 + 居中白字「党」"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # 135° 线性渐变 #c22b2b -> #7f1d1d（逐行近似）
    top = (194, 43, 43)
    bottom = (127, 29, 29)
    grad = Image.new("RGBA", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = (y / (size - 1)) * 0.8 + (x_diag := 0) * 0  # 简化：纵向渐变
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        gd.line([(0, y), (size, y)], fill=(r, g, b, 255))
    # 圆角蒙版
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)

    # 居中「党」
    font = ImageFont.truetype(BOLD_FONT, int(size * 0.58))
    bbox = font.getbbox("党")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw = ImageDraw.Draw(img)
    draw.text(
        ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
        "党",
        font=font,
        fill=(255, 255, 255, 255),
    )
    return img


logo_light = draw_wordmark(DARK_COLOR)
logo_light.save(OUT / "logo.png")
print(f"OK {OUT/'logo.png'} {logo_light.size}")

logo_dark = draw_wordmark(LIGHT_COLOR)
logo_dark.save(OUT / "logo-dark.png")
print(f"OK {OUT/'logo-dark.png'} {logo_dark.size}")

favicon = rounded_gradient_favicon()
favicon.save(OUT / "favicon.png")
print(f"OK {OUT/'favicon.png'} {favicon.size}")

# 同步进 main/public（build 时打入 dist，随 deploy 上线）
(PUBLIC / "logo.png").write_bytes((OUT / "logo.png").read_bytes())
(PUBLIC / "logo-dark.png").write_bytes((OUT / "logo-dark.png").read_bytes())
(PUBLIC / "favicon.png").write_bytes((OUT / "favicon.png").read_bytes())
print(f"copied -> {PUBLIC}")
