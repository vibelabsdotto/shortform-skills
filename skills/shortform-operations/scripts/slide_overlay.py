#!/usr/bin/env python3
"""slide_overlay.py — Text-Overlay-CLI für VibeLabs Shortform-Slides.

Legt nativen TikTok-Style-Text pixelgenau über Bilder (Pillow, kein AI).
Master-Bilder bleiben neutral; Overlays werden als Derivat ausgegeben
(Suffix `-text.jpg`), sodass das Master-Asset wiederverwendbar bleibt.

Usage:
  slide_overlay.py IMAGE OUT [options]

Options:
  --text "..."            Overlay-Text (mehrzeilig via \n)
  --pos top|center|bottom (default: center)
  --font /path.ttf        Font (default: Arial Bold)
  --size 76               Font-Größe px (bei 1080er Breite)
  --color "#FFFFFF"       Textfarbe
  --scrim auto|none|dark  auto = Gradient unten/oben je nach Pos (default auto)
  --stroke 8              Outline px um den Text
  --maxwidth 980          max. Textbreite px (auto line-wrap)
  --out-width 1080        Export-Breite (Höhe folgt 9:16, default 1920)

Beispiel:
  python3 slide_overlay.py slide.jpg B01-01-s1-text.jpg \
    --text "3 things I wish I knew before trying to gain weight." \
    --pos center --size 84
"""
import argparse
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DEFAULT_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TARGET_H = 1920


def fit_1080x1920(img: Image.Image) -> Image.Image:
    """Cover-crop auf 1080x1920 (mittig), wie Photo-Mode-Slides."""
    tw, th = 1080, TARGET_H
    scale = max(tw / img.width, th / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (img.width - tw) // 2
    top = (img.height - th) // 2
    return img.crop((left, top, left + tw, top + th))


def wrap_text(draw, text, font, max_w):
    """Einfacher Wort-Wrap; Ehrt explizite \\n."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = f"{cur} {w}"
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def scrim(draw, pos):
    """Dunkler Verlauf hinter dem Text für Lesbarkeit."""
    h = TARGET_H
    band_h = int(h * 0.45)
    if pos == "bottom":
        top = h - band_h
        coords = [(0, top), (0, h)]
    elif pos == "top":
        coords = [(0, 0), (0, band_h)]
    else:  # center
        top = (h - band_h) // 2
        coords = [(0, top), (0, top + band_h)]
    grad = Image.new("L", (1, band_h))
    for i in range(band_h):
        t = i / max(band_h - 1, 1)
        # Stärkste Abdeckung in Bildmitte des Bandes
        alpha = int(140 * (1 - abs(t - 0.5) * 2) ** 1.2)
        grad.putpixel((0, i), alpha)
    grad = grad.resize((1080, band_h))
    black = Image.new("RGBA", (1080, band_h), (0, 0, 0, 255))
    black.putalpha(grad)
    draw._image.paste(black, (0, coords[0][1]), black)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("out")
    ap.add_argument("--text", required=True)
    ap.add_argument("--pos", choices=["top", "center", "bottom"], default="center")
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--size", type=int, default=76)
    ap.add_argument("--color", default="#FFFFFF")
    ap.add_argument("--scrim", choices=["auto", "none", "dark"], default="auto")
    ap.add_argument("--stroke", type=int, default=8)
    ap.add_argument("--maxwidth", type=int, default=980)
    args = ap.parse_args()

    img = Image.open(args.image).convert("RGB")
    img = fit_1080x1920(img)
    base = img.convert("RGBA")
    draw = ImageDraw.Draw(base)

    font = ImageFont.truetype(args.font, args.size)
    lines = wrap_text(draw, args.text, font, args.maxwidth)

    if args.scrim != "none":
        scrim(draw, args.pos)

    line_h = int(args.size * 1.25)
    total = line_h * len(lines)
    if args.pos == "top":
        y = int(TARGET_H * 0.08)
    elif args.pos == "bottom":
        y = TARGET_H - int(TARGET_H * 0.12) - total
    else:
        y = (TARGET_H - total) // 2

    stroke = args.stroke if args.stroke > 0 else 0
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (1080 - w) // 2
        draw.text((x, y), line, font=font, fill=args.color,
                  stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += line_h

    base.convert("RGB").save(args.out, quality=92)
    print(f"OK {args.out}")


if __name__ == "__main__":
    main()