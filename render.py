#!/usr/bin/env python3
"""Render THE WORLD TODAY for Wednesday 25 November 2026 (1024x1024 PNG).

A code-drawn newspaper front page: masthead, one lead story on the
widening Iran war at sea, two second stories (Asia's AI sell-off,
Huawei's conviction), a markets strip, a 30-item digest and a footer
ticker — 39 verified stories, listed in news-20261125-shortlist.md.

Flat shapes and type only; no photographs, no copied images.
Deterministic: the same script always writes the same bytes.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
EDGE = 28
CW = SIDE - 2 * EDGE

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (248, 244, 233)
CARD = (255, 253, 247)
INK = (24, 24, 24)
GREY = (105, 100, 89)
HAIR = (199, 193, 179)
RED = (173, 33, 23)
BLUE = (27, 75, 133)
GREEN = (17, 103, 87)
PURPLE = (89, 57, 139)
AMBER = (165, 99, 0)
PINK = (147, 39, 89)
TEAL = (44, 108, 120)
DARK = (31, 33, 39)
SEA = (23, 58, 96)
SKY = (211, 226, 239)

TAGC = {
    "WORLD": RED,
    "US": BLUE,
    "TECH": PURPLE,
    "ASIA": AMBER,
    "SPORT": PINK,
    "CLIMATE": GREEN,
    "EUROPE": TEAL,
}

DIGEST = [
    ("WORLD", "Putin vows 'inevitable' retaliation for refinery strikes."),
    ("WORLD", "Kyiv claims Baltic ship strike; 'every Russian ship a target'."),
    ("WORLD", "Moscow summons Latvia's envoy as Riga weighs border closure."),
    ("WORLD", "Norway pledges at least $7bn for Ukraine in 2027."),
    ("WORLD", "Kyiv: Benghazi strike was self-defence; Libya seeks UN meeting."),
    ("WORLD", "Russia's Duma passes the 2027-29 budget."),
    ("WORLD", "No date set for the next round of peace talks, Kremlin says."),
    ("US", "Democrats win a House majority of at least 259 seats."),
    ("US", "Abrego Garcia leaves the US for Spain after a two-year fight."),
    ("US", "Washington readies new global tariffs after a trade probe."),
    ("US", "CIA and intelligence office hit by apparent cyberattack."),
    ("WORLD", "Cartagena siege ends: all ~30 hostages freed, none hurt."),
    ("ASIA", "Pakistan's first astronaut reaches China's space station."),
    ("SPORT", "Senegal regains the CAN-2025 title as CAS overturns final."),
    ("ASIA", "China investigates Shanghai party chief Chen Jining."),
    ("TECH", "China's Qianfan network answers Starlink."),
    ("WORLD", "World court rules on Myanmar's Rohingya genocide case."),
    ("CLIMATE", "COP31 autopsy: oil states pushed carbon capture; Nepal left out."),
    ("ASIA", "Dozens of miners trapped in a 100m-deep Indonesian mine."),
    ("WORLD", "DR Congo aircraft missing; rebels pull back from Bunia."),
    ("WORLD", "Drone attacks on Khartoum condemned; abductions in Blue Nile."),
    ("EUROPE", "Spain heads to a snap election."),
    ("ASIA", "Hong Kong marks a year since the Tai Po fire."),
    ("WORLD", "Zambia indicts an opposition leader on treason charges."),
    ("ASIA", "Bangladesh raises textile minimum wage 36% after protests."),
    ("WORLD", "Venezuela reveals $237.5bn debt; Argentina enters recession."),
    ("WORLD", "Israel: Eisenkot seals a first coalition deal; Lieberman joins."),
    ("WORLD", "WHO chief urges an end to the US fuel blockade on Cuba."),
    ("WORLD", "Iran flogs a singer 74 times over an unveiled concert."),
    ("SPORT", "Real Madrid rout PSV: Bellingham stunner, Mbappe brace."),
]

TICKER = [
    "AUSTRALIA CPI 4.9% - RBA HIKE ODDS RISE",
    "TURKISH HELICOPTER CRASH KILLS 5",
    "GULF PLANE CRASH KILLS 6",
    "LANDMINE TOLL AT FIVE-YEAR HIGH",
    "UN: 5 WOMEN AN HOUR KILLED BY RELATIVES IN 2025",
    "SOLOMON ISLANDS-AUSTRALIA SECURITY TREATY",
]


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_lines(d, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit width."""
    out = []
    cur = ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def hrule(d, x0, y, x1, colour=HAIR, weight=1):
    for k in range(weight):
        d.line([(x0, y + k), (x1, y + k)], fill=colour)


def centred(d, cx, y, text, fnt, colour=INK):
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=colour)


def masthead(d):
    name = load(SERIF, 62)
    centred(d, SIDE / 2, 26, "THE WORLD TODAY", name, INK)
    hrule(d, EDGE, 96, SIDE - EDGE, INK, 2)
    dateline = load(SANSB, 14)
    centred(
        d,
        SIDE / 2,
        104,
        "WEDNESDAY 25 NOVEMBER 2026  \u00b7  WORLD EDITION  \u00b7  39 STORIES",
        dateline,
        INK,
    )
    hrule(d, EDGE, 126, SIDE - EDGE, INK, 1)


def strait_scene(d, x0, y0, x1, y1):
    """Flat drawing of a tanker and mines in the strait."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    d.rectangle([x0, y0 + 95, x1, y1], fill=SEA)
    # sun
    d.ellipse([x1 - 52, y0 + 14, x1 - 22, y0 + 44], fill=(238, 196, 90))
    # tanker hull
    d.polygon(
        [(x0 + 18, y0 + 108), (x1 - 18, y0 + 108), (x1 - 34, y0 + 138), (x0 + 34, y0 + 138)],
        fill=(38, 38, 44),
    )
    # containers sit on the hull, funnel beside them
    for i, col in enumerate([(173, 33, 23), (165, 99, 0), (44, 108, 120)]):
        cx = x0 + 34 + i * 62
        d.rectangle([cx, y0 + 84, cx + 54, y0 + 108], fill=col)
    # funnel
    d.rectangle([x1 - 66, y0 + 78, x1 - 44, y0 + 108], fill=(210, 210, 205))
    # mines: spiked circles in the water, clear of the caption strip
    for mx, my in [(x0 + 70, y1 - 42), (x1 - 90, y1 - 28), (x0 + 190, y1 - 46)]:
        for ang in range(0, 360, 45):
            import math

            r = 13
            ex = mx + r * math.cos(math.radians(ang))
            ey = my + r * math.sin(math.radians(ang))
            d.line([(mx, my), (ex, ey)], fill=(20, 20, 20), width=2)
        d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(20, 20, 20))
    # caption
    cap = load(SANSB, 11)
    d.text((x0 + 10, y1 - 16), "THE STRAIT OF HORMUZ", font=cap, fill=(255, 255, 255))


def lead_story(d):
    x0, x1 = EDGE, EDGE + 660
    y = 140
    kick = load(SANSB, 15)
    d.text((x0, y), "IRAN WAR \u2014 STRAIT OF HORMUZ", font=kick, fill=RED)
    head = load(SERIF, 32)
    d.text((x0, y + 24), "Mines in the Strait: two more", font=head, fill=INK)
    d.text((x0, y + 60), "tankers hit as Iran shuts the strait", font=head, fill=INK)
    deck = load(SANS, 15)
    deck_lines = wrap_lines(
        d,
        "Iran's navy says two tankers struck mines and caught fire in the early hours; "
        "on Monday it claimed three more under US escort.",
        deck,
        x1 - x0,
    )
    yy = y + 100
    for line in deck_lines:
        d.text((x0, yy), line, font=deck, fill=INK)
        yy += 20
    body = load(SANS, 13)
    body_lines = wrap_lines(
        d,
        "Tehran's army chief ordered the waterway closed \u201cfurther day by day\u201d "
        "until its demands are met, while the Saudi-led coalition struck Yemen's "
        "Hodeidah port and the Houthis threatened Jeddah. Brent crude has fallen "
        "more than a fifth in November.",
        body,
        x1 - x0,
    )
    yy += 8
    for line in body_lines:
        d.text((x0, yy), line, font=body, fill=GREY)
        yy += 17
    strait_scene(d, 712, 140, SIDE - EDGE, 330)


def second_card(d, x0, x1, y0, y1, tag, tag_colour, head_lines, body_text, extra):
    d.rectangle([x0, y0, x1, y1], outline=HAIR, width=1)
    d.rectangle([x0, y0, x1, y0 + 4], fill=tag_colour)
    kick = load(SANSB, 13)
    d.text((x0 + 12, y0 + 12), tag, font=kick, fill=tag_colour)
    head = load(SERIF, 23)
    yy = y0 + 34
    for line in head_lines:
        d.text((x0 + 12, yy), line, font=head, fill=INK)
        yy += 28
    body = load(SANS, 12)
    for line in wrap_lines(d, body_text, body, x1 - x0 - 24):
        d.text((x0 + 12, yy), line, font=body, fill=GREY)
        yy += 16
    extra(d, x0, x1, yy, y1)


def market_bars(d, x0, x1, y_top, y_bot):
    """Small vertical bars for the Asian sell-off, one green exception."""
    vals = [("KOSPI", -6.1), ("TAIEX", -4.9), ("NIKKEI", -2.6), ("SHANGHAI", -1.7), ("DOW", 0.9)]
    lab = load(SANSB, 10)
    num = load(SANSB, 10)
    n = len(vals)
    slot = (x1 - x0 - 24) / n
    base = y_bot - 14
    top = y_top + 2
    span = base - top
    for i, (name, v) in enumerate(vals):
        cx = x0 + 12 + slot * i + slot / 2
        hgt = max(4, abs(v) / 6.5 * span)
        col = GREEN if v >= 0 else RED
        d.rectangle([cx - 13, base - hgt, cx + 13, base], fill=col)
        sign = "+" if v >= 0 else ""
        vt = f"{sign}{v}%"
        vw = d.textlength(vt, font=num)
        if hgt >= 14:
            # value sits inside the bar, in white
            d.text((cx - vw / 2, base - hgt + 2), vt, font=num, fill=(255, 255, 255))
        else:
            d.text((cx - vw / 2, base - hgt - 13), vt, font=num, fill=col)
        nw = d.textlength(name, font=lab)
        d.text((cx - nw / 2, base + 3), name, font=lab, fill=GREY)


def huawei_stat(d, x0, x1, y_top, y_bot):
    big = load(SERIF, 30)
    small = load(SANSB, 11)
    d.text((x0 + 12, y_top + 2), "10 of 12", font=big, fill=RED)
    d.text((x0 + 150, y_top + 14), "counts guilty", font=small, fill=INK)
    d.text((x0 + 12, y_top + 38), "12-WEEK TRIAL  \u00b7  60+ WITNESSES  \u00b7  SENTENCING 14 SEPT 2027",
           font=small, fill=GREY)


def second_row(d):
    y0, y1 = 342, 512
    second_card(
        d, EDGE, EDGE + 476, y0, y1,
        "MARKETS \u00b7 ASIA", RED,
        ["Asia's AI rout sweeps", "the region"],
        "Fresh tariff threats piled on the tech sell-off; the Dow topped 50,000.",
        market_bars,
    )
    second_card(
        d, EDGE + 492, SIDE - EDGE, y0, y1,
        "TECH \u00b7 LAW", PURPLE,
        ["Huawei guilty on 10 counts", "in US sanctions trial"],
        "A Brooklyn jury found the Chinese giant guilty of sanctions violations, bank "
        "fraud and stealing US trade secrets after a 12-week trial.",
        huawei_stat,
    )


def markets_strip(d):
    fnt = load(SANSB, 14)
    centred(
        d, SIDE / 2, 522,
        "NIKKEI \u22122.6%  \u00b7  KOSPI \u22126.1%  \u00b7  TAIEX \u22124.9%  \u00b7  "
        "SHANGHAI \u22121.7%  \u00b7  DOW 50,019 +0.9%  \u00b7  NASDAQ \u22121.5%  \u00b7  BRENT $87.49",
        fnt, INK,
    )
    hrule(d, EDGE, 548, SIDE - EDGE, INK, 1)


def digest_block(d):
    head = load(SANSB, 14)
    d.text((EDGE, 560), "THE DAY IN BRIEF", font=head, fill=INK)
    hrule(d, EDGE + 150, 568, SIDE - EDGE, HAIR, 1)
    tag_fnt = load(SANSB, 11)
    txt_fnt = load(SANS, 11)
    col_w = 476
    left = DIGEST[:15]
    right = DIGEST[15:]
    for ci, items in enumerate((left, right)):
        x = EDGE + ci * (col_w + 16)
        y = 586
        for tag, text in items:
            col = TAGC[tag]
            d.text((x, y), tag, font=tag_fnt, fill=col)
            tw = d.textlength(tag + "  ", font=tag_fnt)
            line = text
            while d.textlength(line, font=txt_fnt) > col_w - tw and len(line) > 10:
                line = line.rsplit(" ", 1)[0]
            d.text((x + tw, y), line, font=txt_fnt, fill=INK)
            y += 24


def footer_ticker(d):
    d.rectangle([EDGE, 952, SIDE - EDGE, 1000], fill=DARK)
    fnt = load(SANSB, 11)
    top = "  \u00b7  ".join(TICKER[:3])
    bot = "  \u00b7  ".join(TICKER[3:])
    centred(d, SIDE / 2, 960, top, fnt, (235, 232, 224))
    centred(d, SIDE / 2, 978, bot, fnt, (235, 232, 224))


def build(out_path):
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    lead_story(d)
    second_row(d)
    markets_strip(d)
    digest_block(d)
    footer_ticker(d)
    img.save(out_path, "PNG")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
