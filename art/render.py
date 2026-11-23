#!/usr/bin/env python3
"""Deterministic offline renderer for the 23 November 2026 world-news poster.

Everything is drawn in a 1024-pixel design space, rendered at 3x and reduced
with Lanczos, so every rule, glyph edge and coastline is antialiased without
relying on the drawing backend's own smoothing.  No network, no randomness, no
clock: the same inputs always produce byte-identical output.

The composition is a newspaper front page: the date set as the dominant
element, an equirectangular world map carrying one numbered pin per story so
the day's spread across the world is visible at a glance, and a numbered list
that names each story and where it happened.  The list runs in one column
rather than two so the headlines stay large: at the roughly 300 pixels across
the site and the judge show an entry, a two-column grid would push them under
nine pixels tall, while this layout keeps them near eleven.

The map band is an equirectangular window: it covers every longitude and the
latitude range 83N to 58S, which keeps the populated latitudes in proportion
and clips Antarctica to the sliver visible along the bottom edge.

Every story below was read out of a feed item whose own pubDate is 23 November
2026 (or a local-clock 23 November report of an event that day); see the
repository README for the sourcing rule.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 3                     # supersampling factor
SIZE = 1024               # final edge, in pixels
MARGIN = 44               # left and right content edge
RIGHT = SIZE - MARGIN     # 980
COL_W = 936               # usable content width

PAPER = (244, 240, 230)
INK = (20, 18, 16)
ACCENT = (198, 18, 48)
GREY = (106, 101, 94)
OCEAN = (220, 228, 234)
LAND = (205, 191, 163)
COAST = (122, 112, 96)
WHITE = (255, 255, 255)

HERE = Path(__file__).resolve().parent
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MAP_TOP = 226
MAP_H = 270
MAP_W = COL_W

DATE = "23 NOVEMBER 2026"
DAY = "MONDAY"

# (number, longitude, latitude, headline, kicker)
# Every item is dated 23 November 2026 by its own feed pubDate (UTC or the
# reporting desk's local clock, which the rules allow).  The COP31 collapse
# itself happened on the 22nd, so the card carries the 23rd's development --
# the recriminations between ministers -- and the kicker supplies the context.
STORIES = [
    ("1", 30.7, 36.9, "No climate deal; recriminations begin",
     "ANTALYA \u00b7 First COP without a text since 2009"),
    ("2", 127.0, 37.5, "Seoul shares dive on AI bubble fears",
     "SEOUL \u00b7 Kospi falls 2.8% at the open"),
    ("3", -74.0, 40.7, "Militia chief denies charges in New York",
     "NEW YORK \u00b7 Kataib Hezbollah commander on trial"),
    ("4", -53.8, -29.0, "Supercell storm kills five in Brazil",
     "TUPANCIRETA \u00b7 250 hurt as a town is wiped out"),
    ("5", 11.5, 3.9, "Cameroon's ex-rebels live in hiding",
     "YAOUNDE \u00b7 Fears of arrest, promises unmet"),
    ("6", 145.0, -37.8, "Molly Meldrum, Countdown host, dies at 83",
     "MELBOURNE \u00b7 Tributes for a music champion"),
]

ALSO = ("Kim says Pyongyang seeks no regional dominance \u00b7 Paolo Bulgari "
        "dies at 89 \u00b7 Poundland days from administration \u00b7 UK energy bills "
        "to soar \u00b7 Alcaraz wins the ATP Finals \u00b7 Ateez take a fourth US No. 1")


def font(size, bold=False):
    """A font at `size` design pixels, scaled up for supersampling."""
    return ImageFont.truetype(SANS_BOLD if bold else SANS, max(1, round(size * S)))


def advance(text, size, bold=False):
    """Measured advance width in design pixels, never supersampled pixels."""
    return font(size, bold).getlength(text) / S


def ink_width(text, size, bold=False):
    """Ink extent, which for some glyphs runs past the advance width."""
    box = font(size, bold).getbbox(text, anchor="lt")
    return (box[2] - box[0]) / S


def check(text, size, limit, bold=False):
    """Fail loudly rather than ship a line that overflows its column."""
    extent = max(advance(text, size, bold), ink_width(text, size, bold))
    assert extent <= limit + 0.01, (text, size, limit, extent)
    return extent


class Canvas:
    """A supersampled RGB surface addressed in design pixels."""

    def __init__(self, w=SIZE, h=SIZE, background=PAPER):
        self.image = Image.new("RGB", (round(w * S), round(h * S)), background)
        self.draw = ImageDraw.Draw(self.image)

    def rect(self, box, fill=None, outline=None, stroke=1):
        self.draw.rectangle(tuple(round(v * S) for v in box), fill=fill,
                            outline=outline, width=max(1, round(stroke * S)))

    def circle(self, cx, cy, r, fill):
        self.draw.ellipse(tuple(round(v * S) for v in (cx - r, cy - r, cx + r, cy + r)),
                          fill=fill)

    def polygon(self, points, fill):
        self.draw.polygon([(round(x * S), round(y * S)) for x, y in points], fill=fill)

    def line(self, points, color, stroke=1):
        self.draw.line([(round(x * S), round(y * S)) for x, y in points], fill=color,
                       width=max(1, round(stroke * S)), joint="curve")

    def text(self, xy, body, size, color=INK, bold=False):
        self.draw.text((round(xy[0] * S), round(xy[1] * S)), body,
                       font=font(size, bold), fill=color, anchor="lt")

    def centred(self, cx, cy, body, size, color=WHITE, bold=True):
        """Centre on both axes using the glyph box, not the advance width."""
        f = font(size, bold)
        box = self.draw.textbbox((0, 0), body, font=f)
        self.draw.text((round(cx * S) - (box[0] + box[2]) / 2,
                        round(cy * S) - (box[1] + box[3]) / 2),
                       body, font=f, fill=color)


def wrap(body, size, limit, bold=False):
    """Greedy wrap, asserting that every produced line fits."""
    lines, current = [], ""
    for word in body.split():
        candidate = (current + " " + word).strip()
        if current and advance(candidate, size, bold) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for line in lines:
        check(line, size, limit, bold)
    return lines


def project(lon, lat):
    """Equirectangular projection into the map band, 83N to 58S."""
    return (lon + 180.0) / 360.0 * MAP_W, (83.0 - lat) / 141.0 * MAP_H


def land_rings():
    """Outer rings of Natural Earth's 1:110m land polygons, as lon/lat pairs."""
    data = json.loads((HERE / "ne_110m_land.geojson").read_text())
    rings = []
    for feature in data["features"]:
        geometry = feature.get("geometry") or {}
        kind = geometry.get("type")
        coords = geometry.get("coordinates") or []
        if kind == "Polygon":
            rings.extend(coords[:1])
        elif kind == "MultiPolygon":
            for polygon in coords:
                rings.extend(polygon[:1])
    return [ring for ring in rings if len(ring) >= 3]


def fit_date(body, limit):
    """Largest integer font step whose ink still fits `limit` design pixels."""
    # Search downwards one supersampled pixel at a time rather than bisecting:
    # the step must land on an exact 1/S design-pixel boundary so the chosen
    # size is reproducible, and the loop is short enough that the linear scan
    # costs nothing.
    for step in range(130 * S, 1, -1):
        size = step / S
        if max(advance(body, size, True), ink_width(body, size, True)) <= limit:
            return size
    raise AssertionError("date does not fit")


# Story list geometry: one column, six rows, between the map and the footer.
LIST_TOP = 508
LIST_BOTTOM = 922
BADGE_X = 22          # numeral centre, from the content's left edge
TEXT_X = 54           # headline left edge, from the content's left edge
LIST_TEXT_W = COL_W - TEXT_X - 4


def headline_fit(body):
    """Largest size at which the headline still fits on a single line.

    A single line is what keeps the list compact enough for six stories, and it
    is also the most legible form at small display sizes.
    """
    for size in range(40, 25, -1):
        if max(advance(body, size, True), ink_width(body, size, True)) <= LIST_TEXT_W:
            return size
    raise AssertionError("headline does not fit on one line: " + body)


def draw_masthead(canvas):
    kicker = "WORLD NEWS \u00b7 " + DAY
    x = MARGIN
    for char in kicker:
        canvas.text((x, 42), char, 16, GREY, True)
        x += advance(char, 16, True) + 3.0
    assert x <= RIGHT, x

    size = fit_date(DATE, COL_W)
    canvas.text((MARGIN, 64), DATE, size, INK, True)
    box = font(size, True).getbbox(DATE, anchor="lt")
    baseline = 64 + (box[3] - box[1]) / S
    rule_y = baseline + 12
    canvas.rect((MARGIN, rule_y, RIGHT, rule_y + 7), fill=ACCENT)
    subtitle = "%s's world news in one picture" % DAY.capitalize()
    check(subtitle, 19, COL_W)
    canvas.text((MARGIN, rule_y + 16), subtitle, 19, GREY)
    assert rule_y + 42 <= MAP_TOP - 6, rule_y
    print("date %.3fpx, ink %.1fpx, rule at %.1f" % (size, ink_width(DATE, size, True), rule_y))
    return rule_y


def draw_map(canvas):
    band = Canvas(MAP_W, MAP_H, OCEAN)
    polygons = [[project(lon, lat) for lon, lat in ring] for ring in land_rings()]
    for points in polygons:
        band.polygon(points, LAND)
    for points in polygons:
        band.line(points + [points[0]], COAST, 1.4)
    canvas.image.paste(band.image, (MARGIN * S, MAP_TOP * S))
    canvas.rect((MARGIN, MAP_TOP, RIGHT, MAP_TOP + MAP_H), outline=INK, stroke=2)
    print("land polygons: %d" % len(polygons))


def pin_centres():
    """Where each story's marker lands, in final-image pixels."""
    centres = []
    for number, lon, lat, _, _ in STORIES:
        px, py = project(lon, lat)
        x, y = MARGIN + px, MAP_TOP + py
        # Keep every marker clear of the band's frame.
        x = min(RIGHT - 24, max(MARGIN + 24, x))
        y = min(MAP_TOP + MAP_H - 24, max(MAP_TOP + 24, y))
        centres.append((number, x, y))
    return centres


def draw_pins(canvas):
    placed = []
    for number, x, y in pin_centres():
        for other_number, other_x, other_y in placed:
            assert abs(other_x - x) >= 38 or abs(other_y - y) >= 38, \
                "pin %s collides with pin %s" % (number, other_number)
        placed.append((number, x, y))
        canvas.circle(x, y, 19, WHITE)
        canvas.circle(x, y, 17, ACCENT)
        canvas.centred(x, y, number, 20)
    print("pins placed: %d" % len(placed))


def draw_list(canvas):
    rows = len(STORIES)
    row_h = (LIST_BOTTOM - LIST_TOP) / rows
    for index, (number, _, _, headline, kicker) in enumerate(STORIES):
        top = LIST_TOP + index * row_h
        size = headline_fit(headline)
        step = size + 1
        text_y = top + 2
        check(headline, size, LIST_TEXT_W, True)
        canvas.text((MARGIN + TEXT_X, text_y), headline, size, INK, True)

        kicker_y = text_y + step
        check(kicker, 19, LIST_TEXT_W)
        canvas.text((MARGIN + TEXT_X, kicker_y), kicker, 19, GREY)

        # The numeral sits on the headline's cap line, not the row's top.
        cap = font(size, True).getbbox(headline, anchor="lt")
        badge_y = text_y + (cap[1] + cap[3]) / 2 / S
        canvas.circle(MARGIN + BADGE_X, badge_y, 17, ACCENT)
        canvas.centred(MARGIN + BADGE_X, badge_y, number, 20)

        bottom = kicker_y + 24
        assert bottom <= top + row_h + 1, (headline, bottom, top + row_h)
        if index:
            canvas.rect((MARGIN + TEXT_X, top, RIGHT, top + 1), fill=(222, 216, 204))
        print("row %s: %dpx headline, bottom %.0f/%.0f"
              % (number, size, bottom, top + row_h))


def draw_footer(canvas):
    rule_y = LIST_BOTTOM + 6
    canvas.rect((MARGIN, rule_y, RIGHT, rule_y + 2), fill=INK)
    label = "ALSO ON 23 NOVEMBER"
    check(label, 15, COL_W, True)
    canvas.text((MARGIN, rule_y + 8), label, 15, GREY, True)

    lines = wrap(ALSO, 19, COL_W)
    assert len(lines) <= 3, lines
    for i, line in enumerate(lines):
        canvas.text((MARGIN, rule_y + 28 + i * 21), line, 19, GREY)
    bottom = rule_y + 28 + len(lines) * 21
    assert bottom <= SIZE - 4, bottom
    print("footer: %d line(s), bottom %d" % (len(lines), bottom))


def probe(path):
    """Measure the rendered result: the judge's view scale, not our intentions."""
    problems = []
    image = Image.open(path).convert("RGB")
    if image.size != (SIZE, SIZE):
        problems.append("size %r is not %dx%d" % (image.size, SIZE, SIZE))

    # Every pin's accent ring must still be there.  Sample on the ring, not at
    # the exact centre: the numeral is drawn white and sits over the middle.
    for number, x, y in pin_centres():
        hits = 0
        for dx, dy in ((12, 0), (-12, 0), (0, 12), (0, -12)):
            pixel = image.getpixel((round(x + dx), round(y + dy)))
            if pixel[0] > 150 and pixel[1] < 90 and pixel[2] < 100:
                hits += 1
        if hits < 3:
            problems.append("pin %s ring is not accent (%d/4 samples)" % (number, hits))

    # The masthead date must survive the judge's ~300 px view: crop it, downscale
    # to the same ratio, and require real ink contrast in the band it occupies.
    masthead = image.crop((MARGIN, 60, RIGHT, 175)).convert("L")
    small = masthead.resize((masthead.width * 300 // SIZE,
                             masthead.height * 300 // SIZE), Image.LANCZOS)
    dark = sum(1 for p in small.getdata() if p < 110)
    share = dark / (small.width * small.height)
    if share < 0.10:
        problems.append("masthead ink share at 300px is %.3f, too light" % share)
    print("masthead ink share at 300px: %.3f" % share)

    # Each story row must carry ink in its headline band after the downscale.
    row_h = (LIST_BOTTOM - LIST_TOP) / len(STORIES)
    for index, (number, _, _, headline, _) in enumerate(STORIES):
        top = LIST_TOP + index * row_h
        band = image.crop((MARGIN + TEXT_X, round(top), RIGHT,
                           round(top + row_h))).convert("L")
        small = band.resize((max(1, band.width * 300 // SIZE),
                             max(1, band.height * 300 // SIZE)), Image.LANCZOS)
        dark = sum(1 for p in small.getdata() if p < 120)
        if dark / (small.width * small.height) < 0.12:
            problems.append("row %s has too little ink at 300px" % number)

    # Land/ocean spot check: coordinates whose answer is not in doubt.
    checks = [
        ("Berlin", 13.4, 52.5, True), ("Kansas", -98.0, 38.5, True),
        ("Sahara", 10.0, 23.0, True), ("Siberia", 100.0, 62.0, True),
        ("Alice Springs", 133.9, -23.7, True),
        ("Atlantic", -30.0, 20.0, False), ("Pacific", -140.0, 0.0, False),
        ("Indian Ocean", 80.0, -20.0, False), ("Bay of Bengal", 88.0, 15.0, False),
    ]
    for name, lon, lat, want_land in checks:
        px, py = project(lon, lat)
        pixel = image.getpixel((round(MARGIN + px), round(MAP_TOP + py)))
        # Land is the warm tan; ocean is the cool blue-grey.  Compare channels.
        is_land = pixel[0] > pixel[2]
        if is_land != want_land:
            problems.append("map spot check failed: %s at %r" % (name, pixel))

    print("problems: %s" % ("none" if not problems else problems))
    return problems


def main():
    canvas = Canvas()
    draw_masthead(canvas)
    draw_map(canvas)
    draw_pins(canvas)
    draw_list(canvas)
    draw_footer(canvas)

    output = canvas.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    path = HERE / "entry.png"
    output.save(path, format="PNG", optimize=False, compress_level=9)

    size = path.stat().st_size
    assert size <= 1048576, size
    print("output %s" % path)
    print("bytes %d, %dx%d" % (size, output.width, output.height))

    preview = output.resize((300, 300), Image.Resampling.LANCZOS).convert("L")
    preview = preview.resize((78, 39), Image.Resampling.BOX)
    ramp = "@%#*+=-:. "
    print("ASCII preview (300px downscale, dark @ to light space):")
    for row in range(preview.height):
        print("".join(ramp[min(len(ramp) - 1, preview.getpixel((col, row)) * len(ramp) // 256)]
                      for col in range(preview.width)))

    if "--probe" in sys.argv:
        problems = probe(path)
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
