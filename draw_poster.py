#!/usr/bin/env python3
"""Poster collage of the world news of Thursday 26 November 2026.

Draws a single 1024x1024 PNG with Pillow: a bold poster with a flat-illustration
hero scene (rocket rising past a space station, crescent Earth below), a headline
across the top, and three captioned vignettes along the bottom (tariffs factory,
courtroom gavel, chess board), plus a ticker of further stories.

Deterministic: fixed geometry, fixed colours, no randomness, no wall-clock,
no network. Two runs produce byte-identical files.

Writes to /output/entry.png (or $MAKEFUN_OUTPUT_DIR) and to entry.png next
to this file.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette (warm poster colours) ---------------------------------------
CREAM = (251, 243, 223)
PAPER = (247, 232, 201)
INK = (33, 29, 25)
ORANGE = (232, 93, 38)
RUST = (201, 62, 28)
AMBER = (246, 168, 33)
GOLD = (250, 204, 84)
PLUM = (123, 45, 91)
TEAL = (46, 134, 171)
TEAL_DARK = (31, 94, 122)
GREEN = (96, 160, 90)
WHITE = (255, 255, 255)
STEEL = (214, 222, 228)
STEEL_DARK = (150, 163, 175)
BLUE_PANEL = (52, 98, 158)
RED = (198, 44, 36)
FLAME_Y = (255, 196, 66)
FLAME_O = (255, 122, 26)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def centered(draw, cx, y, text, fnt, fill):
    """Draw text centred on cx, top edge at y. Returns its height."""
    box = draw.textbbox((0, 0), text, font=fnt)
    w = box[2] - box[0]
    draw.text((cx - w / 2 - box[0], y - box[1]), text, font=fnt, fill=fill)
    return box[3] - box[1]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_sky(draw, x0, y0, x1, y1):
    """Vertical warm gradient: amber at top, deep rust at the bottom."""
    n = y1 - y0
    for i in range(n):
        t = i / max(n - 1, 1)
        # amber -> orange -> rust, easing through the middle
        if t < 0.55:
            c = lerp(AMBER, ORANGE, t / 0.55)
        else:
            c = lerp(ORANGE, (176, 52, 40), (t - 0.55) / 0.45)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


STARS = [
    (60, 240, 3), (150, 300, 2), (240, 250, 3), (330, 330, 2),
    (470, 250, 3), (560, 320, 2), (700, 240, 3), (830, 290, 2),
    (920, 350, 3), (90, 420, 2), (420, 400, 2), (640, 430, 3),
    (880, 470, 2), (200, 480, 2), (760, 520, 2), (980, 540, 3),
]


def draw_station(draw, ox, oy, scale=1.0):
    """Flat space station: central module, solar panels, dish."""
    # solar panels (left and right wings)
    for sx in (-1, 1):
        x0 = ox + sx * 118 * scale
        draw.rectangle([x0 - 62 * scale, oy - 26 * scale,
                        x0 + 62 * scale, oy + 26 * scale],
                       fill=BLUE_PANEL, outline=INK, width=4)
        for i in range(1, 4):
            gx = x0 - 62 * scale + i * 31 * scale
            draw.line([(gx, oy - 26 * scale), (gx, oy + 26 * scale)],
                      fill=(120, 165, 205), width=2)
        # truss arm
        draw.line([(ox + sx * 52 * scale, oy),
                   (ox + sx * (118 - 62) * scale, oy)], fill=INK, width=6)
    # central module
    draw.rounded_rectangle([ox - 52 * scale, oy - 20 * scale,
                            ox + 52 * scale, oy + 20 * scale],
                           radius=12 * scale, fill=STEEL, outline=INK, width=4)
    draw.rectangle([ox - 52 * scale, oy - 4 * scale,
                    ox + 52 * scale, oy + 4 * scale], fill=STEEL_DARK)
    # dish on top
    draw.arc([ox - 22 * scale, oy - 52 * scale,
              ox + 22 * scale, oy - 8 * scale],
             start=180, end=360, fill=WHITE, width=5)
    draw.line([(ox, oy - 30 * scale), (ox, oy - 20 * scale)],
              fill=INK, width=4)


def draw_rocket_layer():
    """Rocket on its own RGBA layer, pointing up, for rotation."""
    layer = Image.new("RGBA", (260, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = 130
    # flame
    d.polygon([(cx - 26, 330), (cx + 26, 330), (cx + 12, 400), (cx, 418),
               (cx - 12, 400)], fill=FLAME_O)
    d.polygon([(cx - 14, 330), (cx + 14, 330), (cx + 6, 378), (cx, 392),
               (cx - 6, 378)], fill=FLAME_Y)
    # fins
    d.polygon([(cx - 34, 250), (cx - 34, 330), (cx - 66, 348),
               (cx - 52, 268)], fill=RED, outline=INK)
    d.polygon([(cx + 34, 250), (cx + 34, 330), (cx + 66, 348),
               (cx + 52, 268)], fill=RED, outline=INK)
    # body
    d.rounded_rectangle([cx - 34, 60, cx + 34, 332], radius=30,
                        fill=WHITE, outline=INK, width=5)
    # nose cone
    d.polygon([(cx - 34, 84), (cx + 34, 84), (cx, 6)],
              fill=RED, outline=INK)
    # window
    d.ellipse([cx - 17, 130, cx + 17, 164], fill=TEAL, outline=INK, width=4)
    d.ellipse([cx - 8, 136, cx + 4, 148], fill=(180, 225, 240))
    # stripes
    d.rectangle([cx - 34, 210, cx + 34, 226], fill=ORANGE)
    d.rectangle([cx - 34, 246, cx + 34, 262], fill=ORANGE)
    # "TIANGONG" flag band
    d.rectangle([cx - 34, 282, cx + 34, 306], fill=TEAL)
    return layer


def draw_earth(draw, cx, cy, r):
    """Crescent Earth: lit teal disc, dark shadow disc offset up-right."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL, outline=INK, width=5)
    # land patches on the lit side (lower-left crescent)
    draw.ellipse([cx - r + 8, cy - 18, cx - r + 48, cy + 16], fill=GREEN)
    draw.ellipse([cx - r + 26, cy + 22, cx - r + 58, cy + 52], fill=GREEN)
    draw.ellipse([cx - r + 44, cy - r + 34, cx - r + 70, cy - r + 58], fill=GREEN)
    # dark shadow disc biting the upper-right side -> crescent
    shadow = (43, 32, 54)
    draw.ellipse([cx - r + 62, cy - r - 20, cx + r + 62, cy + r - 20],
                 fill=shadow)
    # re-outline the lit crescent edge
    draw.arc([cx - r, cy - r, cx + r, cy + r], start=95, end=265,
             fill=INK, width=5)


def draw_factory(draw, x0, y0, x1, y1):
    """Flat factory with smokestacks and a gear."""
    mx = (x0 + x1) // 2
    # stacks
    for sx, sh in ((x0 + 34, 96), (x0 + 78, 116)):
        draw.rectangle([sx, y0 + 150 - sh, sx + 34, y0 + 150],
                       fill=STEEL_DARK, outline=INK, width=4)
        draw.ellipse([sx - 2, y0 + 150 - sh - 34, sx + 16, y0 + 150 - sh - 16],
                     fill=(228, 226, 220), outline=INK, width=3)
        draw.ellipse([sx + 18, y0 + 150 - sh - 26, sx + 32, y0 + 150 - sh - 12],
                     fill=(228, 226, 220), outline=INK, width=3)
    # main hall with sawtooth roof
    draw.polygon([(x0 + 14, y0 + 150), (x0 + 14, y0 + 96), (x0 + 66, y0 + 66),
                  (x0 + 118, y0 + 96), (x0 + 170, y0 + 66), (x0 + 222, y0 + 96),
                  (x0 + 222, y0 + 150)], fill=AMBER, outline=INK, width=4)
    # door + windows
    draw.rectangle([mx - 18, y0 + 112, mx + 18, y0 + 150],
                   fill=INK)
    for wx in (x0 + 34, x0 + 172):
        draw.rectangle([wx, y0 + 112, wx + 26, y0 + 132],
                       fill=WHITE, outline=INK, width=3)
    # gear
    gx, gy, gr = x1 - 44, y0 + 42, 20
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=RUST, outline=INK, width=4)
    draw.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], fill=CREAM, outline=INK, width=3)
    for ang in (0, 60, 120, 180, 240, 300):
        import math
        a = math.radians(ang)
        x2 = gx + int((gr + 8) * math.cos(a))
        y2 = gy + int((gr + 8) * math.sin(a))
        draw.line([(gx, gy), (x2, y2)], fill=RUST, width=8)


def draw_gavel(draw, x0, y0, x1, y1):
    """Flat gavel striking a sound block, with motion lines."""
    cx = (x0 + x1) // 2
    cy = y0 + 82
    # sound block
    draw.rounded_rectangle([cx - 62, y0 + 132, cx + 62, y0 + 152],
                           radius=8, fill=AMBER, outline=INK, width=4)
    # handle (diagonal) meeting the head's lower-left corner
    draw.line([(cx - 78, y0 + 118), (cx + 22, y0 + 42)], fill=INK, width=18)
    draw.line([(cx - 78, y0 + 118), (cx + 22, y0 + 42)], fill=(146, 102, 62), width=11)
    # knob at the handle end
    draw.ellipse([cx - 86, y0 + 110, cx - 70, y0 + 126], fill=(122, 84, 52),
                 outline=INK, width=3)
    # gavel head
    draw.rounded_rectangle([cx + 8, y0 + 8, cx + 78, y0 + 52],
                           radius=10, fill=(146, 102, 62), outline=INK, width=4)
    draw.rectangle([cx + 8, y0 + 8, cx + 24, y0 + 52], fill=RUST, outline=INK, width=3)
    draw.rectangle([cx + 62, y0 + 8, cx + 78, y0 + 52], fill=RUST, outline=INK, width=3)


def draw_chess(draw, x0, y0, x1, y1):
    """Flat 4x4 chess board with a king and a pawn, draw agreed."""
    bs = 136
    bx = (x0 + x1) // 2 - bs // 2
    by = y0 + 8
    cell = bs // 4
    for r in range(4):
        for c in range(4):
            col = CREAM if (r + c) % 2 == 0 else INK
            draw.rectangle([bx + c * cell, by + r * cell,
                            bx + (c + 1) * cell, by + (r + 1) * cell],
                           fill=col, outline=INK, width=2)
    # white king on a dark square
    kx, ky = bx + 1 * cell + cell // 2, by + 1 * cell + cell // 2
    draw.ellipse([kx - 13, ky - 13, kx + 13, ky + 13], fill=WHITE, outline=INK, width=3)
    draw.text((kx, ky), "K", font=font(22, bold=True), fill=INK, anchor="mm")
    # black pawn on a light square
    px, py = bx + 2 * cell + cell // 2, by + 2 * cell + cell // 2
    draw.ellipse([px - 11, py - 11, px + 11, py + 11], fill=INK, outline=WHITE, width=2)
    draw.text((px, py), "P", font=font(18, bold=True), fill=WHITE, anchor="mm")


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- outer frame ------------------------------------------------------
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=12)

    # ---- header band ------------------------------------------------------
    d.rectangle([12, 12, W - 12, 208], fill=RUST)
    d.rectangle([12, 12, W - 12, 208], outline=INK, width=4)
    centered(d, W // 2, 30, "SPACE, TARIFFS AND", font(58, bold=True), CREAM)
    centered(d, W // 2, 96, "A COURTROOM", font(58, bold=True), GOLD)
    centered(d, W // 2, 164, "Thursday 26 November 2026",
             font(30, bold=True), WHITE)

    # ---- hero scene -------------------------------------------------------
    draw_sky(d, 12, 212, W - 12, 700)
    d.rectangle([12, 212, W - 12, 700], outline=INK, width=4)
    # stars
    for (sx, sy, sr) in STARS:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=WHITE)
    # sun
    d.ellipse([880, 236, 962, 318], fill=GOLD, outline=INK, width=4)
    # space station, upper left
    draw_station(d, 240, 330, scale=0.9)
    # crescent Earth, lower left (fully above the caption ribbon)
    draw_earth(d, 140, 548, 78)
    # rocket, rising diagonally centre-right
    rocket = draw_rocket_layer().rotate(24, resample=Image.BICUBIC,
                                        expand=True)
    img.paste(rocket, (600, 250), rocket)
    # hero caption ribbon
    d.rectangle([12, 636, W - 12, 700], fill=INK)
    centered(d, W // 2, 650,
             "PAKISTAN'S FIRST ASTRONAUT FLIES TO TIANGONG",
             font(26, bold=True), CREAM)

    # ---- three vignettes --------------------------------------------------
    panels = [
        ("US PLANS NEW TARIFFS", "on global trading partners", draw_factory),
        ("JUDGE BLOCKS TRUMP", "birthright citizenship order", draw_gavel),
        ("WORLD CHESS, GAME 2", "ends in a draw", draw_chess),
    ]
    pw, gap, y0, y1 = 322, 10, 716, 930
    x = 14
    for title, sub, drawer in panels:
        d.rounded_rectangle([x, y0, x + pw, y1], radius=14,
                            fill=PAPER, outline=INK, width=4)
        drawer(d, x + 12, y0 + 8, x + pw - 12, y0 + 158)
        centered(d, x + pw // 2, y0 + 162, title, font(23, bold=True), INK)
        centered(d, x + pw // 2, y0 + 190, sub, font(19), INK)
        x += pw + gap

    # ---- ticker of further stories ---------------------------------------
    d.rectangle([12, 944, W - 12, 1012], fill=INK)
    centered(d, W // 2, 952,
             "ALSO: KIM SEEKS WIDER NUCLEAR DEPLOYMENT  \u2022  UKRAINE STRIKES RUSSIAN AIR BASE",
             font(19, bold=True), CREAM)
    centered(d, W // 2, 980,
             "CAIRO TANKER FIRE KILLS 30  \u2022  BEPICOLOMBO REACHES MERCURY",
             font(19, bold=True), GOLD)

    return img


def main():
    img = build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")
    here = os.path.dirname(os.path.abspath(__file__))
    img.save(os.path.join(here, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
