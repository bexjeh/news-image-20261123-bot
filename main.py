#!/usr/bin/env python3
"""Render '23 November 2026 in one picture': a 1024x1024 news poster.

Standard library only. No network. Writes entry.png into MAKEFUN_OUTPUT_DIR
when set, else the current directory. Deterministic.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# Hand-drawn 5x7 bitmap font. Each glyph is 7 rows of 5 bits, '#' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01000", "00100"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "10001", "10001", "10011", "01101", "00010", "00100"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# ---------------------------------------------------------------- stories
# (region tag, headline, body, accent colour)
HEROES = [
    ("CLIMATE - GLOBAL", "COP31 collapses with no deal",
     "Talks end in overtime; text drops fossil fuels.",
     (178, 34, 34)),
    ("MIDDLE EAST", "Hormuz tanker attacks surge",
     "Three tankers hit in two days as attacks surge.",
     (146, 64, 14)),
    ("SPORT - USA", "Verstappen wins wild Las Vegas GP",
     "35 lead changes; Norris, Piastri follow.",
     (21, 94, 117)),
]

STORIES = [
    ("EUROPE", "Kyiv strike kills 14",
     "Drone hits a home outside Kyiv; 14 missing.", (178, 34, 34)),
    ("EUROPE", "Ship burns off Finland",
     "Cargo ship still ablaze after a drone attack.", (178, 34, 34)),
    ("AFRICA", "Drones hit Russian ship",
     "Corvette Merkury damaged; ten hurt, no claim.", (146, 64, 14)),
    ("AFRICA", "UN site hit in Khartoum",
     "Strikes kill four, damage a UN site.", (146, 64, 14)),
    ("MIDDLE EAST", "Iran unveils new launcher",
     "Guard unveils a dual launcher in a base.", (146, 64, 14)),
    ("MIDDLE EAST", "Gaza food truck hit",
     "Food truck hit, 3 dead; army cites militants.", (146, 64, 14)),
    ("MIDDLE EAST", "Bahrain site hit, two hurt",
     "Attack sets a civilian plant ablaze.", (146, 64, 14)),
    ("SOUTH ASIA", "Nepal PM meets Modi",
     "Talks cover trade, energy and a $2bn package.", (21, 94, 117)),
    ("SOUTH ASIA", "India post record 720/9",
     "India declare at 720/9, a record total.", (21, 94, 117)),
    ("SOUTH ASIA", "Bangladesh unrest kills 6",
     "Protests spread as Hasina return blocked.", (21, 94, 117)),
    ("SOUTH ASIA", "Pakistan seal Test series",
     "Pakistan win by eight wickets, take series 1-0.", (21, 94, 117)),
    ("EAST ASIA", "S. Korea minister quits",
     "Minister resigns amid an AI cheating scandal.", (15, 118, 110)),
    ("SOUTHEAST ASIA", "Factory fire: 36 missing",
     "Three dead; rescuers search for 36 workers.", (15, 118, 110)),
    ("OCEANIA", "Australia, NZ urge truce",
     "Joint call with Canada: end the war in Ukraine.", (15, 118, 110)),
    ("N. AMERICA", "Democrats clinch 258 seats",
     "Recount win seals a record majority.", (30, 64, 175)),
    ("N. AMERICA", "FBI probes database breach",
     "Hack of the crime database under investigation.", (30, 64, 175)),
    ("N. AMERICA", "Delta delays hit Atlanta",
     "System failure delays 400-plus flights.", (30, 64, 175)),
    ("S. AMERICA", "Mexico seizes Chapo Isidro",
     "Cartel boss seized; eleven killed in the raid.", (124, 58, 237)),
    ("EUROPE", "France protests, week six",
     "106,000 march over living costs in France.", (178, 34, 34)),
    ("GLOBAL", "Hunger Games tops charts",
     "Prequel opens at No. 1 with $120m.", (124, 58, 237)),
    ("GLOBAL", "Anthropic slides after IPO",
     "Shares fall 8.5% as Nasdaq gives up 2026 gains.", (124, 58, 237)),
    ("EUROPE", "Alcaraz wins ATP Finals",
     "Beats Zverev 6-2, 7-6 for a first Turin title.", (178, 34, 34)),
    ("EAST ASIA", "Nvidia chip row grows",
     "Ex-staffer tied to network moving chips to China.", (15, 118, 110)),
    ("GLOBAL", "Miley Cyrus marries",
     "Singer weds Maxx Morando in California.", (124, 58, 237)),
]

# ---------------------------------------------------------------- canvas
BG = (245, 243, 238)      # warm paper
CARD = (255, 255, 255)
INK = (17, 24, 39)        # near-black headlines
BODY = (55, 65, 81)       # dark grey body
MUTED = (107, 114, 128)
NAVY = (15, 42, 67)
NAVY2 = (23, 58, 88)
LINE = (203, 213, 225)

bg = bytearray(W * H * 3)
txt = bytearray(W * H * 3)   # text colour layer
msk = bytearray(W * H)       # text coverage mask


def fill_rect(x, y, w, h, col):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = col
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            bg[i] = r
            bg[i + 1] = g
            bg[i + 2] = b


def fill_circle(cx, cy, rad, col):
    r, g, b = col
    for yy in range(cy - rad, cy + rad + 1):
        for xx in range(cx - rad, cx + rad + 1):
            dx = xx - cx
            dy = yy - cy
            if dx * dx + dy * dy <= rad * rad and 0 <= xx < W and 0 <= yy < H:
                i = (yy * W + xx) * 3
                bg[i] = r
                bg[i + 1] = g
                bg[i + 2] = b


def ring(cx, cy, rad, thick, col):
    r, g, b = col
    for yy in range(cy - rad - thick, cy + rad + thick + 1):
        for xx in range(cx - rad - thick, cx + rad + thick + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if (rad - thick) ** 2 <= d2 <= (rad + thick) ** 2:
                if 0 <= xx < W and 0 <= yy < H:
                    i = (yy * W + xx) * 3
                    bg[i] = r
                    bg[i + 1] = g
                    bg[i + 2] = b


def draw_text(x, y, s, col, scale):
    """Draw string s with its top-left at (x, y). scale 2 -> 14 px cap height."""
    cx = x
    r, g, b = col
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for gy in range(7):
            row = glyph[gy]
            for gx in range(5):
                if row[gx] == '1':
                    px = cx + gx * scale
                    py = y + gy * scale
                    for sy in range(scale):
                        for sx in range(scale):
                            xx = px + sx
                            yy = py + sy
                            if 0 <= xx < W and 0 <= yy < H:
                                i = (yy * W + xx) * 3
                                txt[i] = r
                                txt[i + 1] = g
                                txt[i + 2] = b
                                msk[yy * W + xx] = 255
        cx += 6 * scale
    return cx


def text_w(s, scale):
    return len(s) * 6 * scale


def wrap(s, max_chars):
    words = s.split(' ')
    lines = []
    cur = ''
    for wd in words:
        if not cur:
            cur = wd
        elif len(cur) + 1 + len(wd) <= max_chars:
            cur += ' ' + wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, col, scale, max_chars, max_lines, line_h):
    lines = wrap(s, max_chars)[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * line_h, ln, col, scale)
    return len(lines)


# ---------------------------------------------------------------- layout
def build():
    fill_rect(0, 0, W, H, BG)

    # header band
    fill_rect(0, 0, W, 74, NAVY)
    fill_rect(0, 74, W, 4, (200, 162, 39))
    draw_text(16, 14, "MONDAY 23 NOVEMBER 2026", (255, 255, 255), 4)
    draw_text(16, 50, "WORLD NEWS IN ONE IMAGE", (191, 219, 245), 2)
    right = "27 STORIES - TO 08:00 UTC"
    draw_text(W - 16 - text_w(right, 2), 50, right, (191, 219, 245), 2)

    margin = 12
    gap = 8
    col_w = (W - 2 * margin - 2 * gap) // 3
    hero_y = 86
    hero_h = 158

    # hero cards: one simple single-scene illustration band + big text
    for ci, (tag, head, body, accent) in enumerate(HEROES):
        x = margin + ci * (col_w + gap)
        fill_rect(x, hero_y, col_w, hero_h, CARD)
        fill_rect(x, hero_y, col_w, 4, accent)
        # illustration band
        band_y = hero_y + 4
        band_h = 46
        if ci == 0:
            fill_rect(x, band_y, col_w, band_h, (224, 242, 254))
            fill_circle(x + 52, band_y + 23, 17, (34, 197, 94))
            ring(x + 52, band_y + 23, 17, 1, (255, 255, 255))
            fill_rect(x + 35, band_y + 21, 34, 3, (255, 255, 255))
            fill_rect(x + 50, band_y + 8, 3, 30, (255, 255, 255))
            fill_rect(x + 96, band_y + 14, 150, 3, (178, 34, 34))
            draw_text(x + 96, band_y + 24, "NO DEAL", (178, 34, 34), 2)
        elif ci == 1:
            fill_rect(x, band_y, col_w, band_h, (254, 243, 199))
            # tanker: hull with a pointed bow, stacked containers, funnel
            fill_rect(x + 18, band_y + 22, 96, 10, (30, 64, 175))
            fill_rect(x + 114, band_y + 22, 14, 10, (30, 64, 175))
            fill_rect(x + 114, band_y + 26, 22, 6, (30, 64, 175))
            fill_rect(x + 26, band_y + 10, 18, 12, (178, 34, 34))
            fill_rect(x + 46, band_y + 10, 18, 12, (21, 94, 117))
            fill_rect(x + 66, band_y + 10, 18, 12, (146, 64, 14))
            fill_rect(x + 36, band_y + 2, 14, 8, (178, 34, 34))
            fill_rect(x + 96, band_y + 12, 8, 10, (55, 65, 81))
            fill_rect(x + 18, band_y + 36, 110, 3, (30, 64, 175))
            fill_rect(x + 140, band_y + 12, 170, 3, (30, 64, 175))
            fill_rect(x + 140, band_y + 22, 170, 3, (30, 64, 175))
            fill_rect(x + 140, band_y + 32, 170, 3, (30, 64, 175))
        else:
            fill_rect(x, band_y, col_w, band_h, (226, 232, 240))
            sq = 8
            for r in range(3):
                for c in range(12):
                    if (r + c) % 2 == 0:
                        fill_rect(x + 16 + c * sq, band_y + 10 + r * sq, sq, sq,
                                  (17, 24, 39))
            # race car: low body, cabin, rear spoiler, two wheels
            fill_rect(x + 128, band_y + 24, 66, 8, (178, 34, 34))
            fill_rect(x + 146, band_y + 14, 26, 10, (178, 34, 34))
            fill_rect(x + 186, band_y + 10, 4, 14, (17, 24, 39))
            fill_rect(x + 182, band_y + 8, 12, 3, (17, 24, 39))
            fill_circle(x + 142, band_y + 34, 6, (17, 24, 39))
            fill_circle(x + 180, band_y + 34, 6, (17, 24, 39))
            draw_text(x + 210, band_y + 14, "50 LAPS", (17, 24, 39), 2)
            draw_text(x + 210, band_y + 30, "35 PASSES", (17, 24, 39), 2)
        ty = band_y + band_h + 8
        draw_text(x + 10, ty, tag, accent, 2)
        draw_wrapped(x + 10, ty + 18, head, INK, 3, 17, 2, 24)
        draw_wrapped(x + 10, ty + 18 + 48, body, BODY, 2, 26, 2, 17)

    # grid cards
    grid_y = hero_y + hero_h + gap
    rows = 8
    row_h = (H - grid_y - 30 - (rows - 1) * gap) // rows
    for idx, (tag, head, body, accent) in enumerate(STORIES):
        r = idx // 3
        c = idx % 3
        x = margin + c * (col_w + gap)
        y = grid_y + r * (row_h + gap)
        fill_rect(x, y, col_w, row_h, CARD)
        fill_rect(x, y, col_w, 4, accent)
        draw_text(x + 10, y + 10, tag, accent, 2)
        draw_wrapped(x + 10, y + 28, head, INK, 2, 26, 1, 17)
        draw_wrapped(x + 10, y + 48, body, BODY, 2, 26, 2, 17)

    # footer
    fy = H - 26
    draw_text(16, fy + 4, "All stories first reported 22-23 November 2026.",
              MUTED, 2)
    tail = "MONDAY 23 NOVEMBER 2026"
    draw_text(W - 16 - text_w(tail, 2), fy + 4, tail, MUTED, 2)


# ---------------------------------------------------------------- unsharp
def box_blur(src, radius):
    """Separable box blur of a bytearray mask; returns list of ints 0..255."""
    wdt = radius * 2 + 1
    tmp = [0] * (W * H)
    # horizontal
    for yy in range(H):
        base = yy * W
        s = 0
        for k in range(-radius, radius + 1):
            xx = min(max(0, k), W - 1)
            s += src[base + xx]
        for xx in range(W):
            tmp[base + xx] = s // wdt
            xa = xx - radius
            xb = xx + radius + 1
            if xa >= 0:
                s -= src[base + xa]
            if xb < W:
                s += src[base + xb]
    out = [0] * (W * H)
    # vertical
    for xx in range(W):
        s = 0
        for k in range(-radius, radius + 1):
            yy = min(max(0, k), H - 1)
            s += tmp[yy * W + xx]
        for yy in range(H):
            out[yy * W + xx] = s // wdt
            ya = yy - radius
            yb = yy + radius + 1
            if ya >= 0:
                s -= tmp[ya * W + xx]
            if yb < H:
                s += tmp[yb * W + xx]
    return out


def composite():
    blur = box_blur(msk, 2)
    out = bytearray(W * H * 3)
    for i in range(W * H):
        m = msk[i]
        if m == 0:
            j = i * 3
            out[j] = bg[j]
            out[j + 1] = bg[j + 1]
            out[j + 2] = bg[j + 2]
            continue
        a = m + int(0.6 * (m - blur[i]))
        if a < 0:
            a = 0
        elif a > 255:
            a = 255
        j = i * 3
        if a == 255:
            out[j] = txt[j]
            out[j + 1] = txt[j + 1]
            out[j + 2] = txt[j + 2]
        else:
            inv = 255 - a
            out[j] = (txt[j] * a + bg[j] * inv) // 255
            out[j + 1] = (txt[j + 1] * a + bg[j + 1] * inv) // 255
            out[j + 2] = (txt[j + 2] * a + bg[j + 2] * inv) // 255
    return out


# ---------------------------------------------------------------- png
def png_bytes(rgb):
    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += rgb[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    build()
    rgb = composite()
    data = png_bytes(rgb)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
