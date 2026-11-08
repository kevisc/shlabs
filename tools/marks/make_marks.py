#!/usr/bin/env python3
"""
make_marks.py: every SHLabs product icon, drawn from one set of parts.

    python3 tools/marks/make_marks.py sheet <out.png>     the review sheet: every mark, 300/64/32/16 px
    python3 tools/marks/make_marks.py site                img/<slug>.png for every mark, 512 px
    python3 tools/marks/make_marks.py app <slug> <dir>    one product's icon files, into <dir>:
        icon-src.png    1024, the tile on Apple's 824-in-1024 grid, transparent round it (ICON_BIG)
        logo.png        1024, full bleed
        logo_256.png     256, square, mid detail: an editor header that frames it with a rule
        badge_128.png    128, the detail of a ~20 pt badge beside a wordmark
        <Name>.iconset/  the ten sizes, each drawn for its size
        <Name>.icns      iconutil's pack of the iconset (macOS), metadata stripped

THE SYSTEM (Lacuna's and Schlagzeugs' coded icons were the first two):
  * A near-black rounded tile (radius 0.2237 of its side) and a warm-grey hairline inside it.
  * Thin white lines; quieter grey lines for what supports; hollow node rings at the joints.
  * One accent, cyan #87FAFD, on what the product does now, with a soft glow of the same hue.
  * No gradients, no bevels, no letters. Each mark keeps the idea its old icon had.
  * Small sizes get their own weights: under a 96 px tile the lines and nodes grow and the
    hairline goes; under 40 px hollow nodes become solid dots. A mark may draw less when small.
  * VCV Rack families: the same grammar on a lighter gunmetal tile, with beaded lines, after the
    patch points of a module panel. Same accent.

Deterministic: Pillow only, no randomness, no fonts, no network.
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))

TILE      = (8, 9, 11)
TILE_VCV  = (24, 26, 29)          # gunmetal: the VCV panels' grammar
HAIRLINE  = (62, 62, 59)
HAIR_VCV  = (78, 80, 80)
GREY      = (150, 156, 162)
WHITE     = (240, 244, 246)
CYAN      = (135, 250, 253)       # #87FAFD, sampled from Contour, Glue and Stesso (see Lacuna's make_logo.py)
CYAN_GLOW = (0, 238, 248)
SS = 4

LINE, NODE_R, NODE_W, LIT_R = 0.0105, 0.0215, 0.0085, 0.0270   # tile units, full detail
BEAD_STEP = 0.034


# ----------------------------------------------------------------------------- geometry (tile units)
def catmull(points, n=48):
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(points[-1])
    return out


def arc(cx, cy, r, a0, a1, n=200, ry=None, rot=0.0):
    """Degrees, counter-clockwise, y up as on paper."""
    ry = r if ry is None else ry
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = r * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy - (x * s + y * c)))
    return out


def at(cx, cy, r, a):
    return (cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a)))


def bez(p0, p1, p2, p3, n=120):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def beads(pts, step):
    """Points every `step` along a polyline, ends included."""
    out, acc = [pts[0]], 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        while acc + seg >= step and seg > 0:
            t = (step - acc) / seg
            a = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            out.append(a); seg = math.dist(a, b); acc = 0.0
        acc += seg
    if math.dist(out[-1], pts[-1]) > step * 0.4: out.append(pts[-1])
    return out


# ----------------------------------------------------------------------------- a mark is a list of parts
class Mark:
    def __init__(self, vcv=False):
        self.vcv = vcv
        self.parts = []

    def line(self, pts, colour=WHITE, w=1.0): self.parts.append(("line", (pts, w), colour)); return self
    def lit_line(self, pts, w=1.0):           self.parts.append(("line", (pts, w), CYAN)); return self
    def node(self, p, colour=WHITE, s=1.0):   self.parts.append(("node", (p, s), colour)); return self
    def lit(self, p, s=1.0):                  self.parts.append(("lit", (p, s), CYAN)); return self
    def dot(self, p, colour=WHITE, s=1.0):    self.parts.append(("dot", (p, s), colour)); return self


def tier(px):
    return "full" if px >= 96 else ("mid" if px >= 40 else "tiny")


def render(fn, size, inset=True, square=False, detail_px=None):
    """`fn(tier)` builds the mark. detail_px draws at the weights of a smaller tile (a badge)."""
    S = size * SS
    margin = S * 100 / 1024 if inset else 0.0
    T = S - 2 * margin
    px = detail_px if detail_px else T / SS
    t = tier(px)
    mark = fn(t)
    grow = {"full": 1.0, "mid": 2.1, "tiny": 3.6}[t]
    node_grow = {"full": 1.0, "mid": 1.5, "tiny": 2.1}[t]
    hollow = t != "tiny"
    tile, hair = (TILE_VCV, HAIR_VCV) if mark.vcv else (TILE, HAIRLINE)

    def P(p): return (margin + p[0] * T, margin + p[1] * T)

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = T * 0.2237
    if square:
        d.rectangle([margin, margin, margin + T - 1, margin + T - 1], fill=tile + (255,))
    else:
        d.rounded_rectangle([margin, margin, margin + T - 1, margin + T - 1], radius=radius, fill=tile + (255,))
    if t == "full" and not square:
        inner = T * 0.055
        d.rounded_rectangle([margin + inner, margin + inner, margin + T - 1 - inner, margin + T - 1 - inner],
                            radius=radius - inner * 0.75, outline=hair + (255,), width=max(1, int(T * 0.0035)))

    def disc(dr, c, r, fill=None, outline=None, width=0):
        dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill, outline=outline, width=max(0, int(round(width))))

    def poly(dr, pts, colour, w):
        if mark.vcv:                                   # beaded: a patch-point line
            step = BEAD_STEP * (1.0 if t == "full" else 1.6 if t == "mid" else 2.4)
            for b in beads(pts, step):
                disc(dr, P(b), w * 0.62, fill=colour + (255,))
            return
        q = [P(p) for p in pts]
        dr.line(q, fill=colour + (255,), width=max(1, int(round(w))), joint="curve")
        disc(dr, q[0], w / 2, fill=colour + (255,)); disc(dr, q[-1], w / 2, fill=colour + (255,))

    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    for kind, data, colour in mark.parts:
        if colour != CYAN: continue
        if kind == "line":
            q = [P(p) for p in data[0]]
            g.line(q, fill=CYAN_GLOW + (255,), width=max(1, int(LINE * T * grow * data[1] * 2.6)), joint="curve")
        elif kind == "lit":
            disc(g, P(data[0]), LIT_R * T * node_grow * data[1] * 1.5, fill=CYAN_GLOW + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(0.018 * T * (1.0 if t == "full" else 1.4)))
    glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.7)))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)

    for kind, data, colour in mark.parts:
        if kind == "line":
            poly(d, data[0], colour, LINE * T * grow * data[1])
        elif kind == "node":
            c, s = P(data[0]), data[1]
            if hollow:
                disc(d, c, NODE_R * T * node_grow * s, fill=tile + (255,), outline=colour + (255,), width=NODE_W * T * node_grow)
            else:
                disc(d, c, NODE_R * T * node_grow * s * 0.75, fill=colour + (255,))
        elif kind == "lit":
            disc(d, P(data[0]), LIT_R * T * node_grow * data[1], fill=CYAN + (255,))
        elif kind == "dot":
            disc(d, P(data[0]), NODE_R * T * node_grow * data[1] * 0.55, fill=colour + (255,))
    return img.resize((size, size), Image.LANCZOS)


# ============================================================================= the products
def cadence(t):
    """The master clock: a C that is a bar of four beats, the downbeat lit, the hand on it."""
    m = Mark(); c = (0.52, 0.5); r = 0.275
    m.line(arc(*c, r, 42, 318))
    beats = [42 + (318 - 42) * i / 3 for i in range(4)]
    m.line([c, at(*c, r, beats[0])], GREY)
    m.node(c, GREY, 0.8)
    for b in beats[1:]: m.node(at(*c, r, b))
    m.lit(at(*c, r, beats[0]))
    return m


def kinora(t):
    """A picture drawn the way a screen draws it: a disc of scan lines over a horizon, the line
    being drawn now lit. Fewer lines when small, so the gaps survive."""
    m = Mark(); c = (0.5, 0.47); r = 0.27
    n = {"full": 9, "mid": 7, "tiny": 5}[t]
    lit_i = round(n * 0.6) - (0 if n > 5 else 1)
    ys = [c[1] - r + r * 2 * (i + 0.5) / n for i in range(n)]
    end = None
    for i, y in enumerate(ys):
        h = (r * r - (y - c[1]) ** 2) ** 0.5
        seg = [(c[0] - h, y), (c[0] + h, y)]
        if i == lit_i: m.lit_line(seg); end = seg[1]
        else: m.line(seg, WHITE if i < lit_i else GREY, 0.85)
    m.line([(0.16, 0.80), (0.84, 0.80)], GREY, 0.7)
    m.lit(end, 0.8)
    return m


def cell(t):
    """A cell: a hexagon, its nucleus lit."""
    m = Mark(); c = (0.5, 0.5)
    outer = [at(*c, 0.29, 90 + 60 * i) for i in range(7)]
    m.line(outer)
    if t != "tiny": m.line([at(*c, 0.145, 90 + 60 * i) for i in range(7)], GREY, 0.85)
    for p in outer[:6]: m.node(p, WHITE, 0.85)
    m.lit(c, 1.25)
    return m


def contour(t):
    """A drawn modulation curve through its points, one lit, a quieter echo under it."""
    m = Mark()
    main = [(0.17, 0.60), (0.33, 0.52), (0.47, 0.31), (0.64, 0.58), (0.83, 0.42)]
    echo = [(0.17, 0.70), (0.33, 0.64), (0.47, 0.48), (0.64, 0.68), (0.83, 0.58)]
    if t != "tiny": m.line(catmull(echo, 40), GREY, 0.8)
    m.line(catmull(main, 40))
    m.node(main[0]); m.node(main[3]); m.lit(main[2])
    return m


def spazio(t):
    """Space: a sphere and the orbit through it, the moving source lit."""
    m = Mark(); c = (0.5, 0.5)
    m.line(arc(*c, 0.255, 0, 360))
    m.line(arc(*c, 0.36, 0, 360, ry=0.11, rot=-18), GREY, 0.85)
    m.node(c, WHITE, 0.9)
    m.node(at(*c, 0.255, 90), WHITE, 0.8); m.node(at(*c, 0.255, 270), WHITE, 0.8)
    m.lit(arc(*c, 0.36, 12, 12, 1, ry=0.11, rot=-18)[0])
    return m


def legato(t):
    """Bound together: two lines drawn into one through a ring."""
    m = Mark()
    m.line(bez((0.16, 0.28), (0.32, 0.28), (0.36, 0.50), (0.455, 0.50)))
    m.line(bez((0.16, 0.72), (0.32, 0.72), (0.36, 0.50), (0.455, 0.50)))
    m.lit_line([(0.545, 0.50), (0.84, 0.50)])
    m.node((0.16, 0.28), WHITE, 0.8); m.node((0.16, 0.72), WHITE, 0.8)
    m.node((0.50, 0.50), WHITE, 2.0)
    m.lit((0.84, 0.50), 0.85)
    return m


def stesso(t):
    """An equaliser band: the bell on its axis, its centre lit."""
    m = Mark()
    m.line([(0.16, 0.66), (0.84, 0.66)], GREY, 0.85)
    m.line(catmull([(0.16, 0.66), (0.33, 0.645), (0.42, 0.42), (0.50, 0.31), (0.58, 0.42), (0.67, 0.645), (0.84, 0.66)], 40))
    m.node((0.30, 0.66), WHITE, 0.85); m.node((0.70, 0.66), WHITE, 0.85)
    if t != "tiny": m.line([(0.50, 0.66), (0.50, 0.38)], GREY, 0.6)
    m.lit((0.50, 0.31))
    return m


def tonnetz(t):
    """The tone net: seven notes and their links, one triad lit."""
    m = Mark(); c = (0.5, 0.5); r = 0.25
    ring = [at(*c, r, 90 + 60 * i) for i in range(6)]
    for i in range(6):
        m.line([ring[i], ring[(i + 1) % 6]], GREY, 0.85)
        if i not in (0, 1): m.line([c, ring[i]], GREY, 0.85)
    m.lit_line([c, ring[0]]); m.lit_line([c, ring[1]]); m.lit_line([ring[0], ring[1]])
    for i in range(2, 6): m.node(ring[i])
    m.lit(c); m.lit(ring[0]); m.lit(ring[1])
    return m


def metro185(t):
    """Eight steps of a sequencer on their rail, the playing step lit."""
    m = Mark()
    base = 0.68; h = [0.26, 0.15, 0.21, 0.10, 0.31, 0.17, 0.07, 0.23]
    xs = [0.19 + i * (0.62 / 7) for i in range(8)]
    m.line([(0.15, base), (0.85, base)], GREY, 0.85)
    for i, (x, hh) in enumerate(zip(xs, h)):
        if i == 4:
            m.lit_line([(x, base), (x, base - hh)]); m.lit((x, base - hh), 0.9)
        else:
            m.line([(x, base), (x, base - hh)], WHITE, 0.9); m.node((x, base - hh), WHITE, 0.75)
    return m


# ============================================================================= the VCV Rack families
def stochast(t):
    """Chance, counted: a normal distribution in columns of beads, the sampled column lit."""
    m = Mark(vcv=True)
    xs = [0.22 + i * 0.07 for i in range(9)]
    base = 0.72
    for i, x in enumerate(xs):
        hgt = 0.40 * math.exp(-((i - 4) ** 2) / 5.0) + 0.03
        seg = [(x, base), (x, base - hgt)]
        if i == 5: m.lit_line(seg); m.lit(seg[1], 0.8)
        else: m.line(seg, WHITE if abs(i - 4) <= 2 else GREY)
    return m


def mashina(t):
    """A machine: a chip on its pins, one pin driven."""
    m = Mark(vcv=True)
    x0, x1, y0, y1 = 0.30, 0.70, 0.30, 0.70
    m.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
    for k in range(3):
        y = 0.38 + k * 0.12
        m.line([(0.17, y), (x0, y)], GREY); m.line([(x1, y), (0.83, y)], GREY)
    m.lit_line([(x1, 0.50), (0.83, 0.50)])
    m.node((0.50, 0.50), WHITE, 1.3)
    m.lit((0.83, 0.50), 0.8)
    return m


def lucida(t):
    """Light on a grid: a function plotted over a field of points."""
    m = Mark(vcv=True)
    if t == "full":
        for i in range(7):
            for j in range(7):
                m.dot((0.20 + i * 0.10, 0.20 + j * 0.10), GREY, 0.7)
    curve = [(0.20 + i * 0.05, 0.50 - 0.22 * math.sin((i / 12) * 2 * math.pi)) for i in range(13)]
    m.lit_line(curve)
    m.lit(curve[3], 0.8)
    return m


def rikoshet(t):
    """A ricochet: a ball bouncing lower each time along its floor, the last bounce lit."""
    m = Mark(vcv=True)
    floor = 0.70
    m.line([(0.15, floor), (0.85, floor)], GREY)
    x, w, hgt = 0.18, 0.26, 0.40
    pts = []
    for k in range(3):
        pts.append(arc(x + w / 2, floor, w / 2, 180, 0, 60, ry=hgt))
        x += w; w *= 0.68; hgt *= 0.55
    m.line(pts[0]); m.line(pts[1]); m.lit_line(pts[2])
    m.node((0.18, floor), WHITE, 0.8)
    m.lit(pts[2][-1], 0.8)
    return m


def atmos(t):
    """Air: three rings of a rising column, its axis, the top ring lit."""
    m = Mark(vcv=True)
    m.line([(0.50, 0.20), (0.50, 0.80)], GREY)
    m.line(arc(0.50, 0.70, 0.16, 0, 360, ry=0.045))
    m.line(arc(0.50, 0.52, 0.24, 0, 360, ry=0.06))
    m.line(arc(0.50, 0.32, 0.30, 0, 360, ry=0.07))
    m.lit((0.80, 0.32), 0.8)
    return m


def terra(t):
    """The earth: a globe of beads, its equator and a meridian, one place lit."""
    m = Mark(vcv=True); c = (0.5, 0.5)
    m.line(arc(*c, 0.28, 0, 360))
    m.line(arc(*c, 0.28, 0, 360, ry=0.09), GREY)
    m.line(arc(*c, 0.11, 0, 360, ry=0.28), GREY)
    m.lit((0.5 + 0.28 * math.cos(math.radians(-35)), 0.5 - 0.09 * math.sin(math.radians(-35))), 0.9)
    return m


def phosphor_vcv(t):
    """Phosphor for VCV Rack: a signal path of three modules, the screen at its end lit."""
    m = Mark(vcv=True)
    m.line([(0.20, 0.50), (0.42, 0.50)]); m.line([(0.50, 0.50), (0.68, 0.50)])
    m.node((0.20, 0.50)); m.node((0.46, 0.50), WHITE, 1.2)
    m.line(arc(0.76, 0.50, 0.08, 0, 360), WHITE)
    m.lit((0.76, 0.50), 1.1)
    return m


# slug, display name, drawing
FAMILY = [("cadence", "Cadence", cadence), ("kinora", "Kinora", kinora), ("cell", "Cell", cell),
          ("contour", "Contour", contour), ("spazio", "Spazio", spazio), ("legato", "Legato", legato),
          ("stesso", "Stesso", stesso), ("tonnetz", "Tonnetz", tonnetz), ("metro185", "Metro 185", metro185)]
VCV = [("stochast", "Stochast", stochast), ("mashina", "Mashina", mashina), ("lucida", "Lucida", lucida),
       ("rikoshet", "Rikoshet", rikoshet), ("atmos", "Atmos", atmos), ("terra", "Terra", terra),
       ("phosphor", "Phosphor (VCV)", phosphor_vcv)]
ALL = {slug: (name, fn) for slug, name, fn in FAMILY + VCV}


# ============================================================================= output
def strip_icns_metadata(path):
    """iconutil adds an eXIf chunk to every PNG it packs; drop it and text chunks (from Lacuna)."""
    drop = {b"eXIf", b"iTXt", b"tEXt", b"zTXt"}
    blob = open(path, "rb").read()
    assert blob[:4] == b"icns"
    entries, i = [], 8
    while i < len(blob):
        kind, n = blob[i:i + 4], int.from_bytes(blob[i + 4:i + 8], "big")
        body = blob[i + 8:i + n]
        if body[:8] == b"\x89PNG\r\n\x1a\n":
            kept, j = [body[:8]], 8
            while j < len(body):
                m = int.from_bytes(body[j:j + 4], "big")
                if body[j + 4:j + 8] not in drop: kept.append(body[j:j + 12 + m])
                j += 12 + m
            body = b"".join(kept)
        entries.append(kind + (8 + len(body)).to_bytes(4, "big") + body)
        i += n
    payload = b"".join(entries)
    with open(path, "wb") as f:
        f.write(b"icns" + (8 + len(payload)).to_bytes(4, "big") + payload)


def save(img, path):
    img.save(path, format="PNG", optimize=False, compress_level=9)
    print("wrote", path)


def app(slug, out):
    name, fn = ALL[slug]
    os.makedirs(out, exist_ok=True)
    save(render(fn, 1024, inset=True), os.path.join(out, "icon-src.png"))
    save(render(fn, 1024, inset=False), os.path.join(out, "logo.png"))
    save(render(fn, 256, inset=False, square=True, detail_px=64), os.path.join(out, "logo_256.png"))
    save(render(fn, 128, inset=False, detail_px=36), os.path.join(out, "badge_128.png"))
    stem = name.replace(" ", "").split("(")[0]
    iconset = os.path.join(out, stem + ".iconset")
    os.makedirs(iconset, exist_ok=True)
    for f in os.listdir(iconset): os.remove(os.path.join(iconset, f))
    for base in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            save(render(fn, base * scale, inset=True), os.path.join(iconset, "icon_%dx%d%s.png" % (base, base, "@2x" if scale == 2 else "")))
    if sys.platform == "darwin":
        icns = os.path.join(out, stem + ".icns")
        subprocess.run(["iconutil", "-c", "icns", iconset, "-o", icns], check=True)
        strip_icns_metadata(icns)
        print("wrote", icns)


def sheet(out):
    rows = [("SHLabs products", FAMILY), ("VCV Rack families", VCV)]
    big, cw, ch, cols = 260, 300, 380, 5
    height = 40
    for _, items in rows: height += 40 + ((len(items) + cols - 1) // cols) * ch
    sh = Image.new("RGB", (cols * cw + 20, height), (236, 234, 228)); dr = ImageDraw.Draw(sh)
    y = 20
    for title, items in rows:
        dr.text((20, y), title, fill=(20, 20, 20)); y += 30
        for i, (slug, name, fn) in enumerate(items):
            x, yy = (i % cols) * cw + 20, y + (i // cols) * ch
            im = render(fn, big); sh.paste(im, (x, yy), im)
            sx = x
            for s in (64, 32, 16):
                im = render(fn, s); sh.paste(im, (sx, yy + big + 12), im); sx += s + 14
            dr.text((x, yy + big + 86), name, fill=(20, 20, 20))
        y += ((len(items) + cols - 1) // cols) * ch + 10
    sh.save(out); print("wrote", out)


def site():
    for slug, (name, fn) in ALL.items():
        save(render(fn, 512, inset=False), os.path.join(SITE, "img", slug + ".png"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sheet" and len(sys.argv) == 3: sheet(sys.argv[2])
    elif cmd == "site": site()
    elif cmd == "app" and len(sys.argv) == 4: app(sys.argv[2], sys.argv[3])
    else: sys.exit(__doc__)
