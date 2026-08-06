#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pages.py — regenerate every HTML page of shlabs.ch in the "Index"
design system (see css/shlabs.css).

    HOW TO RE-RUN
    -------------
        cd <repo root>
        python3 tools/gen_pages.py

    It rewrites, from the data in this file and nothing else:

        index.html   404.html
        about/  donate/  downloads/  empiria/
        cadence/  phosphor/  cell/  tincture/  slicery/  contour/  spazio/
        glue/  stesso/  tonnetz/  metro185/
        stochast/  mashina/  lucida/  rikoshet/  atmos/  terra/

    It never touches: cadence/manual/ (the product manual deliberately
    matches the app's own look, not the site), CNAME, img/, README.md,
    css/shlabs.css, js/shlabs.js.

    All copy lives in the data structures below. Edit it here, re-run, and
    commit this file together with the regenerated HTML. The nav and the
    footer are defined exactly once (NAV_LINKS / FOOTER_COLS), so every
    page stays in sync and internal links cannot drift apart.

    Design rules this file encodes
    ------------------------------
    * Amber is the only accent, used for status and interaction only.
      There are no per-product accent colours any more.
    * The homepage index rows are real <a> elements; they are the only
      thing on the site that inverts to ink on hover. A product sheet's
      specification rows use the same ruled geometry but never invert,
      because they are facts, not links.
    * Product sheets carry no logo art — the old app-icon PNGs are built
      for a dark UI. Real screenshots appear as "plates": a single 1px ink
      hairline, no shadow, no gradient, mono caption underneath.
    * Only /cadence/ loads JavaScript, and only for the view explorer — the
      tab row over Cadence's four views. With no script it degrades to the
      four plates stacked in flow, each with its own note.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEAR = 2026          # hardcoded so regeneration is deterministic
GITHUB = "https://github.com/shlabs-audio"
MAIL = "mailto:shlabs.contact@gmail.com"

# ═══════════════════════════════════════════════════════════════════════
#  shared chrome
# ═══════════════════════════════════════════════════════════════════════

# label, target (a "#anchor" is resolved against the homepage), extra class
NAV_LINKS = [
    ("Flagships", "#flagships", ""),
    ("Index", "#index", ""),
    ("Studio", "#studio", "nav-hide"),
    ("GitHub", GITHUB, "is-accent"),
]

FOOTER_COLS = [
    ("Flagships", [
        ("Cadence", "/cadence/"),
        ("Phosphor", "/phosphor/"),
    ]),
    ("Instruments &amp; effects", [
        ("Cell", "/cell/"),
        ("Tincture", "/tincture/"),
        ("Slicery", "/slicery/"),
        ("Contour", "/contour/"),
        ("Spazio", "/spazio/"),
    ]),
    ("Mastering &amp; MIDI", [
        ("Glue", "/glue/"),
        ("Stesso", "/stesso/"),
        ("Tonnetz", "/tonnetz/"),
        ("Metro 185", "/metro185/"),
    ]),
    ("VCV Rack", [
        ("Stochast", "/stochast/"),
        ("Mashina", "/mashina/"),
        ("Lucida", "/lucida/"),
        ("Rikoshet", "/rikoshet/"),
        ("Atmos", "/atmos/"),
    ]),
    ("Studio", [
        ("About SHLabs", "/about/"),
        ("Contact", MAIL),
        ("Support the studio", "/donate/"),
        ("GitHub", GITHUB),
    ]),
]

SWISS = (
    '<svg width="12" height="12" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
    '<rect width="32" height="32" fill="#d52b1e"/>'
    '<rect x="13" y="6" width="6" height="20" fill="#fff"/>'
    '<rect x="6" y="13" width="20" height="6" fill="#fff"/></svg>'
)


def head(title, desc, *, home=False, robots=None, canonical=None, refresh=None,
         script=False, og=None):
    """The <head> block. og defaults to the page title/description."""
    og_title, og_desc = og or (title, desc)
    L = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        "  <title>%s</title>" % title,
    ]
    if desc:
        L.append('  <meta name="description" content="%s">' % desc)
    if robots:
        L.append('  <meta name="robots" content="%s">' % robots)
    if canonical:
        L.append('  <link rel="canonical" href="%s">' % canonical)
    if refresh:
        L.append('  <meta http-equiv="refresh" content="%s">' % refresh)
    L += [
        '  <meta name="theme-color" content="#f3f2ee">',
        '  <link rel="icon" type="image/svg+xml" href="/img/favicon.svg">',
        '  <link rel="stylesheet" href="/css/shlabs.css">',
    ]
    if og_title:
        L.append('  <meta property="og:title" content="%s">' % og_title)
    if og_desc:
        L.append('  <meta property="og:description" content="%s">' % og_desc)
    if og_title or og_desc:
        L.append('  <meta property="og:type" content="website">')
    if script:
        # set before first paint so the two gallery layouts never flash
        L.append('  <script>document.documentElement.className+=" js";</script>')
    L += ["</head>", "<body>", ""]
    return "\n".join(L)


def nav(home=False, current=None):
    root = "" if home else "/"
    out = []
    for label, target, cls in NAV_LINKS:
        if target.startswith("http"):
            href, rel = target, ' rel="noopener"'
        else:
            href, rel = root + target, ""
        attrs = ' class="%s"' % cls if cls else ""
        cur = ' aria-current="page"' if current and current == label else ""
        out.append('      <a href="%s"%s%s%s>%s</a>' % (href, attrs, rel, cur, label))
    return (
        '  <a class="skip" href="#main">Skip to content</a>\n'
        '  <nav class="nav">\n'
        '    <div class="nav__in pad">\n'
        '      <a class="wordmark" href="%s">SH<i>labs</i></a>\n'
        '      <div class="nav__links mono">\n%s\n      </div>\n'
        '    </div>\n'
        '  </nav>\n' % ("#top" if home else "/", "\n".join(out))
    )


def footer():
    cols = []
    for label, links in FOOTER_COLS:
        items = []
        for text, href in links:
            rel = ' rel="noopener"' if href.startswith("http") else ""
            items.append('        <a href="%s"%s>%s</a>' % (href, rel, text))
        cols.append(
            '      <div class="foot__col">\n'
            '        <span class="mono">%s</span>\n%s\n      </div>' % (label, "\n".join(items))
        )
    return (
        '  <footer class="foot">\n'
        '    <div class="foot__cols pad">\n%s\n    </div>\n\n'
        '    <div class="pad">\n'
        '      <div class="foot__word">SH<i>labs</i></div>\n'
        '    </div>\n\n'
        '    <div class="foot__bar pad mono">\n'
        '      <span>&copy; %d SHLabs &middot; Instruments for the modular world</span>\n'
        '      <span class="swiss">%s Made in Switzerland</span>\n'
        '      <span class="dim-2">Set in Helvetica</span>\n'
        '    </div>\n'
        '  </footer>\n' % ("\n".join(cols), YEAR, SWISS)
    )


def tail(script=False):
    s = '\n  <script src="/js/shlabs.js"></script>' if script else ""
    return "</div>%s\n</body>\n</html>\n" % s


def write(relpath, html):
    path = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("  wrote %s (%d bytes)" % (relpath, len(html.encode("utf-8"))))


# ═══════════════════════════════════════════════════════════════════════
#  product sheet renderer
# ═══════════════════════════════════════════════════════════════════════

def acts_html(acts):
    out = []
    for href, label, kind in acts:
        ext = href.startswith("http")
        attr = ' target="_blank" rel="noopener"' if ext else ""
        cls = "act act--fill" if kind == "fill" else "act"
        out.append('        <a class="%s" href="%s"%s>%s</a>' % (cls, href, attr, label))
    return '      <div class="acts">\n%s\n      </div>' % "\n".join(out)


def plate_html(src, alt, w, h, cap, indent="      "):
    return (
        '%s<figure class="fig">\n'
        '%s  <div class="plate"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy"></div>\n'
        '%s  <figcaption class="mono">%s</figcaption>\n'
        '%s</figure>' % (indent, indent, src, alt, w, h, indent, cap, indent)
    )


def render_parts(parts, counter):
    """Render one section's parts. `counter` is a one-item list holding the
    running specification-row number for the whole sheet."""
    out = []
    blk = []          # prose-ish parts buffered into one padded block

    def flush():
        if blk:
            out.append('    <div class="blk pad">\n%s\n    </div>' % "\n".join(blk))
            del blk[:]

    for part in parts:
        kind = part[0]
        if kind == "head":
            flush()
            _, label, aside = part
            a = '\n      <span class="mono dim-2">%s</span>' % aside if aside else ""
            out.append(
                '    <div class="group__head group__head--first">\n'
                '      <h2 class="mono">%s</h2>%s\n'
                '    </div>' % (label, a)
            )
        elif kind == "rows":
            flush()
            for k, t, b in part[1]:
                counter[0] += 1
                out.append(
                    '    <div class="spec">\n'
                    '      <span class="row__no">%02d</span>\n'
                    '      <span class="row__id"><span class="row__cat">%s</span>'
                    '<h3 class="row__name">%s</h3></span>\n'
                    '      <p class="row__desc">%s</p>\n'
                    '    </div>' % (counter[0], k, t, b)
                )
        elif kind == "h3":
            blk.append('      <h3 class="blk__h">%s</h3>' % part[1])
        elif kind == "lead":
            blk.append('      <p class="lead">%s</p>' % part[1])
        elif kind == "body":
            blk.append('      <p class="body">%s</p>' % part[1])
        elif kind == "mono":
            blk.append('      <p class="mono dim">%s</p>' % part[1])
        elif kind == "acts":
            blk.append(acts_html(part[1]))
        elif kind == "plate":
            flush()
            _, src, alt, w, h, cap = part
            out.append('    <div class="band band--tight pad">\n%s\n    </div>'
                       % plate_html(src, alt, w, h, cap))
        elif kind == "explore":
            flush()
            # The app's own views, behind a tab row that mirrors the app's own
            # tab bar. Tab labels are written in sentence case and set upper by
            # .act, the way every other mono label on the site is. The ARIA tab
            # roles are added by js/shlabs.js, not written here, so that with no
            # script the markup is four plain figures and a hidden tab row.
            _, label, views = part
            tabs, panels = [], []
            for n, (slug, tab, src, alt, w, h, note, keys) in enumerate(views):
                tabs.append(
                    '          <button class="act explore__tab" type="button" '
                    'id="view-%s-tab" data-explore-tab>%s</button>' % (slug, tab)
                )
                kw = "".join("<span>%s</span>" % k for k in keys)
                lazy = "" if n == 0 else ' loading="lazy"'
                panels.append(
                    '          <figure class="explore__panel" id="view-%s" data-explore-panel>\n'
                    '            <figcaption class="explore__note">\n'
                    '              <p class="body">%s</p>\n'
                    '              <div class="explore__spec mono">%s</div>\n'
                    '            </figcaption>\n'
                    '            <div class="plate plate--hi"><img src="%s" alt="%s" '
                    'width="%d" height="%d"%s></div>\n'
                    '          </figure>' % (slug, note, kw, src, alt, w, h, lazy)
                )
            out.append(
                '    <div class="band band--tight pad">\n'
                '      <div class="explore" data-explore="%s">\n'
                '        <div class="explore__tabs" data-explore-tabs>\n%s\n        </div>\n'
                '        <div class="explore__panels">\n%s\n        </div>\n'
                '      </div>\n'
                '    </div>' % (label, "\n".join(tabs), "\n".join(panels))
            )
        else:
            raise ValueError("unknown part %r" % (kind,))
    flush()
    return "\n".join(out)


def product_page(p):
    """Render one product sheet."""
    crumb_label, crumb_href = p["crumb"]
    status_cls = "is-soon" if p.get("soon") else "is-free"

    spec = "".join("<span>%s</span>" % s for s in p["spec"])

    hero_plate = ""
    if p.get("shot"):
        src, alt, w, h = p["shot"]
        hero_plate = ('\n  <div class="band band--tight pad">\n%s\n  </div>\n'
                      % plate_html(src, alt, w, h, alt + ".", indent="    "))

    counter = [0]
    secs = []
    for sec in p["sections"]:
        body = render_parts(sec["parts"], counter)
        sid = ' id="%s"' % sec["id"] if sec.get("id") else ""
        if sec.get("slab"):
            secs.append('  <div class="slab">\n  <section class="sec"%s>\n%s\n  </section>\n  </div>'
                        % (sid, body))
        else:
            secs.append('  <section class="sec"%s>\n%s\n  </section>' % (sid, body))

    return (
        head(p["title"], p["desc"], script=p.get("script", False))
        + nav()
        + '\n  <div class="sheet">\n\n'
        '  <nav class="crumb pad mono" aria-label="Breadcrumb">\n'
        '    <a href="/#index">Index</a>\n'
        '    <span class="sep" aria-hidden="true">/</span>\n'
        '    <a href="%s">%s</a>\n'
        '    <span class="sep" aria-hidden="true">/</span>\n'
        '    <span aria-current="page">%s</span>\n'
        '  </nav>\n\n'
        '  <header class="psheet pad" id="main">\n'
        '    <div class="psheet__meta mono">\n'
        '      <span class="dim">%s</span>\n'
        '      <span class="%s">%s</span>\n'
        '    </div>\n'
        '    <h1 class="psheet__name">%s</h1>\n'
        '    <div class="psheet__grid">\n'
        '      <div class="psheet__claim"><p>%s</p></div>\n'
        '      <div class="psheet__desc"><p class="body">%s</p></div>\n'
        '    </div>\n'
        '    <div class="psheet__spec mono">%s</div>\n'
        '  </header>\n'
        '%s\n  <div class="rule--ink"></div>\n\n'
        '%s\n\n' % (crumb_href, crumb_label, p["name"],
                    p["cat"], status_cls, p["status"], p["name"],
                    p["claim"], p["lead"], spec, hero_plate, "\n\n".join(secs))
        + footer()
        + tail(script=p.get("script", False))
    )


# ═══════════════════════════════════════════════════════════════════════
#  the catalogue: shared fragments
# ═══════════════════════════════════════════════════════════════════════

VST_CLOSE = ("""A paid, closed-source SHLabs plugin in active development. This page is """
             """an early look; pricing and availability will be announced when it ships. """
             """Follow SHLabs to hear when it lands.""")

VCV_NEED = ("""You'll need <strong>VCV Rack 2</strong> — a free download for macOS, Windows """
            """and Linux from <a class="link" href="https://vcvrack.com/Rack" target="_blank" """
            """rel="noopener">vcvrack.com/Rack</a>.""")

VCV_MAC = "macOS (Apple Silicon). Windows, Linux &amp; Intel builds coming via the VCV Library."

ALL_PRODUCTS = ("/#index", "All products &rarr;", "")
ALL_VCV = ("/#vcv", "All VCV modules &rarr;", "")


def vst(**kw):
    """A standalone/VST product sheet with one capability list and a close."""
    kw.setdefault("soon", True)
    kw.setdefault("status", "Coming soon")
    kw.setdefault("spec", ["VST3 · AU · Standalone", "macOS &amp; Windows"])
    kw["sections"] = [
        {"parts": [("head", kw.pop("head", "What it does"), ""),
                   ("rows", kw.pop("rows"))]},
        {"parts": [("head", "Get it", ""),
                   ("body", VST_CLOSE),
                   ("acts", [ALL_PRODUCTS])]},
    ]
    return kw


# ═══════════════════════════════════════════════════════════════════════
#  the catalogue: product data
# ═══════════════════════════════════════════════════════════════════════

PRODUCTS = {}

# ─── Cadence ──────────────────────────────────────────────────────────
PRODUCTS["cadence"] = {
    "name": "Cadence",
    "title": "Cadence — SHLabs",
    "desc": """Cadence is a hybrid-performance brain from SHLabs: a DJ-style four-channel performance mixer, master clock and sync hub for hardware, files and live inputs. Sample-accurate 24-PPQN MIDI clock, beatgrid players, automatic structure analysis, Ableton Link and OSC. Standalone app, macOS. Coming soon.""",
    "crumb": ("Performance &amp; live", "/#cat-live"),
    "cat": "Performance mixer &amp; master clock",
    "status": "Coming soon",
    "soon": True,
    "claim": "A hybrid-performance brain.",
    "lead": """Four channels of live inputs and beatgrid players under DJ-style hands, a sample-accurate MIDI clock that the rest of your rig follows, and an assist layer that can hold the mix together while you play hardware on top.""",
    "spec": ["Standalone app", "macOS — Windows alpha in testing"],
    # No hero plate: the Perform shot that used to sit here is the first view
    # of the explorer below, and one screenshot on a sheet twice is one too
    # many. The explorer opens the page in its place.
    "script": True,
    "sections": [
        {"parts": [
            ("head", "Inside Cadence", "Four views, one surface"),
            # PERFORM / COLLECTION / ARRANGE / SAMPLER, in the app's own order.
            # Every claim below is checked against the app: docs/manual/index.html
            # and TESTERS.md in the hybrid-mixer repo, and the view sources.
            ("explore", "Cadence views", [
                ("perform", "Perform",
                 "/img/shots/cadence.jpg",
                 "The Perform view: four mixer strips with faders and meters at the centre, a deck waveform either side of them, and the collection docked below",
                 2360, 1864,
                 """Perform — the mixer: four strips, each running a live input or a deck from your collection, under one master section.""",
                 ["3-band EQ with full kill", "Filter per channel",
                  "Pre-fader cue bus", "Master metering"]),
                ("composer", "Composer",
                 "/img/shots/cadence-arrange.jpg",
                 "The Composer view: four deck lanes of clips on a numbered bar timeline, under a toolbar of clip and automation tools",
                 2360, 1864,
                 """Composer — a bar timeline where the set is laid out in advance: one lane per deck, each track a full-length clip that launches its deck as the master playhead crosses it.""",
                 ["Vol / filt / dly / verb / OSC lanes", "Macro envelopes M1–M8",
                  "Saved as a performance Set"]),
                ("collection", "Collection",
                 "/img/shots/cadence-collection.jpg",
                 "The Collection view: the track table with waveform, BPM, key, genre, length, grid and stems columns, and Load 1 to 4 buttons above it",
                 2360, 1864,
                 """Collection — the library you load from, scanned and sorted: waveform, BPM, key, beatgrid confidence and stems status in the columns.""",
                 ["Load onto channels 1–4", "Search by key or BPM range",
                  "Harmonic matches tint green", "rekordbox XML import"]),
                ("sampler", "Sampler",
                 "/img/shots/cadence-sampler.jpg",
                 "The Sampler view: a zoomed waveform with a beatgrid-snapped selection highlighted, under the save, monitor and strip controls",
                 2360, 1864,
                 """Sampler — a non-destructive editor for snipping regions out of tracks: select on the beatgrid, then save the piece, or collect regions into a strip and render them as one crossfaded clip.""",
                 ["Beatgrid-snapped selection", "Cue or main monitoring, own level",
                  "24-bit WAV, equal-power joins"]),
            ]),
        ]},
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("The brain", "One surface for the whole set",
                 """Live inputs, prepared clips and hardware all meet on the same four channels. Cadence holds the tempo, the grid and the structure of the set in one place, so there is a single thing to look at when the room is dark and something needs to change now."""),
                ("One clock", "Everything follows Cadence",
                 """A sample-accurate 24-PPQN MIDI clock, phase-locked to the audio clock rather than driven by a timer, with transport start and stop, tap tempo and Ableton Link. Cadence is built to be the one clock in the room, not another device negotiating for sync."""),
                ("Hands free", "Play hardware on top",
                 """The assist layer can carry a transition on its own — key-aware, paced how you like it, looping the build into the drop. That buys you both hands for the modular, the drum machine or the synth, and you take the mix back whenever you want it."""),
            ]),
        ]},
        {"parts": [
            ("head", "Capabilities", ""),
            ("rows", [
                ("Mixer", "Four channels, DJ ergonomics",
                 """Each channel takes a live input or its own internal player. Three-band EQ with full kills, one HP/LP filter knob per channel in the DJ idiom, a pre-fader cue bus with selectable master and cue output routing, and master metering. Per-channel delay and a shared reverb send sit on the same strip."""),
                ("Clock &amp; sync", "Hardware locked to the grid",
                 """24-PPQN MIDI clock out, sample-accurate and phase-locked to audio, driving eurorack, Elektron boxes and drum machines with transport start and stop. Tap tempo for anything unclocked, Ableton Link for anything on the network."""),
                ("Players", "Beatgrid-native clips",
                 """Quantized bar launch, warp and vari-speed sync to the master tempo, flexible grid with key-lock, eight hot cues and cue preview from the browser. Waveform lanes show phase and sync against the beat grid, and a composer view runs a master playhead over the whole set."""),
                ("Analysis", "It reads the track",
                 """Automatic beatgrid and structure detection marks intro, break, drop and outro, with auto-sections snapped to bars, mood descriptors and clip-safe gain. The library stores the analysis, so a track you prepared once stays prepared."""),
                ("Assist", "An auto-DJ layer you steer",
                 """Key-aware transition modes, adjustable pacing, a build-up loop into the drop and FX ramps. When tracks are separated, transitions use the stems themselves — real bass swaps and vocal handovers, not just EQ moves. Hand it the next stretch and it holds the mix; take it back mid-transition and nothing jumps."""),
                ("Control", "Mapped to your gear",
                 """MIDI-learn on everything, with A/B bank switching so a small controller still reaches the whole surface. A phone remote joins over the local network by QR code. OSC broadcasts clock phase, beat, BPM and transport alongside master band energy, kick onsets, per-stem levels and a drop-aware intensity signal."""),
            ]),
        ]},
        {"parts": [
            ("head", "Stems", "Drums · Bass · Other · Vocals"),
            ("lead", """Cadence separates a track into its four parts on your machine — no cloud, no upload — and then treats them as performance surface: kill a vocal, keep the drums under the next tune, solo a bassline, and let the auto-DJ trade basslines instead of EQ bands."""),
            ("rows", [
                ("Separate", "Four parts, on your machine",
                 """One right-click separates a track into drums, bass, other and vocals with a state-of-the-art neural model running locally — around forty seconds for a club track on Apple Silicon. Results live in the library cache, so a track is only ever separated once."""),
                ("Perform", "Kills that land on the bar",
                 """Each stemmed deck grows four mute chips and a solo per part, all quantized to the grid — a queued kill blinks until the bar line and drops exactly on it, or shift-click for an instant stab. Key-lock holds pitch throughout, and every chip is MIDI-learnable."""),
                ("Assist + stems", "The auto-DJ mixes with the parts",
                 """Transitions become stem-aware when the material allows it: bass swaps trade the actual basslines on the swap bar, the incoming vocal waits until the outgoing one is out of the way, and with both tracks separated it hands over drums first, then bass — the way you would."""),
            ]),
        ]},
        {"slab": True, "id": "bundle", "parts": [
            ("head", "The bundle", "The full SHLabs studio"),
            ("h3", "Built to perform together"),
            ("lead", """Phosphor listens to Cadence over OSC and locks the visuals to the clock. Motion lands on the beat, parameters move with bass, mid and high energy, kicks flash, and the image surges when the drop arrives and settles back through the breakdown. This is how the two apps already behave together, not something on a roadmap."""),
            ("rows", [
                ("Cadence sends", "Clock, structure, energy",
                 """Beat and clock phase, BPM and transport, master band energy across bass, mid and high, kick onsets, and a drop-aware intensity signal — plus live per-stem levels and drum-stem onsets when a deck plays separated stems. Broadcast continuously over OSC while you play."""),
                ("Phosphor answers", "Visuals on the same grid",
                 """Scene motion locks to beat phase, reactive parameters follow the bands, kick onsets fire shockwave ripples, and intensity drives the whole image up into the drop — fullscreen on the projector."""),
            ]),
            ("body", """And the bundle is the whole studio: alongside <strong>Cadence</strong> and <strong>Phosphor</strong> it includes <a class="link" href="/cell/">Cell</a>, <a class="link" href="/tincture/">Tincture</a>, <a class="link" href="/contour/">Contour</a>, <a class="link" href="/spazio/">Spazio</a>, <a class="link" href="/glue/">Glue</a>, <a class="link" href="/stesso/">Stesso</a> and <a class="link" href="/tonnetz/">Tonnetz</a> — every instrument, effect and mastering tool in the line."""),
            ("body", """A Tonnetz link — Cadence following and steering harmony via note-follow over OSC — is planned for the bundle."""),
            ("mono", "Bundle pricing announced at release."),
            ("acts", [("/phosphor/", "Phosphor &rarr;", ""),
                      ("/tonnetz/", "Tonnetz &rarr;", ""),
                      ALL_PRODUCTS]),
        ]},
        {"parts": [
            ("head", "Influences", ""),
            ("body", """Cadence's performance workflow owes an honest debt to deadmau5's Autopilot. Its DAW-style set preparation and hybrid performance thinking pushed us to ask how much of a set can be prepared in advance before it stops being a performance and becomes a playback."""),
            ("body", """Cadence goes its own way from there: it is a hardware-first brain, putting out a sample-accurate MIDI clock that your modular and drum machines follow; it is open at the edges, broadcasting clock, structure and energy over OSC to a paired video synth that reacts to the shape of your set; and every control on it maps to whatever gear you already own."""),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Cadence is a premium SHLabs app in active development. This page is an early look."""),
            ("body", """The macOS build is in testing and a Windows alpha is running alongside it. Pricing and availability are announced when it ships. For early access, or if you want to know whether Cadence will clock the specific box on your desk, write to us."""),
            ("acts", [(MAIL, "Write us", "fill"), ALL_PRODUCTS]),
        ]},
    ],
}

# ─── Phosphor ─────────────────────────────────────────────────────────
PRODUCTS["phosphor"] = {
    "name": "Phosphor",
    "title": "Phosphor — SHLabs",
    "desc": """Phosphor is a GPU-native audio-reactive video synthesiser from SHLabs: five scene families, a 100k particle system, band envelopes and onset detection, Syphon output and recording. Locks to Cadence over OSC, to the host playhead or to Ableton Link. VST3 / AU / Standalone. Coming soon.""",
    "crumb": ("Visuals", "/#cat-visuals"),
    "cat": "Audio-reactive video synth",
    "status": "Coming soon",
    "soon": True,
    "claim": "A video synthesiser that listens.",
    "lead": """A GPU-native GLSL engine with five scene families and a hundred-thousand-particle system, driven by real band envelopes and onset detection, locked to your clock and thrown fullscreen onto the projector. Insert it on a track and the audio passes through untouched.""",
    "spec": ["Premium · VST3 · AU · Standalone", "macOS"],
    "shot": ("/img/shots/phosphor.jpg", "The Phosphor plugin interface", 1280, 1040),
    "sections": [
        {"parts": [
            ("head", "What it does", ""),
            ("rows", [
                ("Scene engine", "Five families of image",
                 """Everything renders on the GPU in GLSL. Morphable pattern <strong>Fields</strong> cover more than twelve forms; <strong>Tunnel</strong> is a flythrough; <strong>Fractals</strong> run Julia, Mandelbrot and Burning Ship; <strong>Spectrum</strong> draws bars, radial and spectrograph views from a true FFT; <strong>Ambient</strong> holds nebula, aurora, caustics and lava."""),
                ("Particles", "A hundred thousand of them",
                 """A GPGPU particle system running upward of 100,000 points with trails and reflections, simulated entirely on the graphics card so the count buys you density rather than dropped frames."""),
                ("Reactivity", "It hears more than level",
                 """Separate envelopes for overall level and for bass, mid and high, plus onset detectors for kick, snare and hat. Spectral centroid tilts the colour toward the brightness of the sound. One master REACT control sets how hard all of it pushes."""),
                ("Sync", "Three ways to stay in time",
                 """Lock to <a class="link" href="/cadence/">Cadence</a> over OSC and follow beat, phase, BPM, transport, band energy, onsets and drop intensity. Or take the host playhead inside a DAW. Or run standalone on Ableton Link. Motion stays on the grid either way."""),
                ("Performance", "Built for the room",
                 """Fullscreen to a second display or projector, <strong>Evolve</strong> for hands-free generative drift, <strong>Auto</strong> for preset roaming and <strong>Flow</strong> to morph between them — cut, smooth or slow. More than 36 presets and 15 colour palettes, layered dual-engine blending, a video-clip layer with reactive blending, and shockwave ripples on the kick."""),
                ("I/O &amp; control", "Out to the rest of the rig",
                 """Syphon output on macOS feeds your VJ software or media server; H.264 recording and PNG snapshots capture the set. MIDI-learn covers every control, and a phone remote joins over the local network by QR code."""),
            ]),
            ("mono", """VST3 &middot; AU &middot; Standalone. macOS now; a Windows build is in CI with the visuals and reactivity intact &mdash; Syphon and recording stay macOS-only."""),
        ]},
        {"parts": [
            ("head", "Engine output", ""),
            ("plate", "/img/shots/phosphor-visual.jpg",
             "A frame rendered by the Phosphor engine", 1600, 715,
             "Engine output &mdash; a single frame captured straight out of Phosphor."),
        ]},
        {"slab": True, "id": "bundle", "parts": [
            ("head", "The bundle", "Bundle pricing at release"),
            ("h3", "Made to lock to Cadence"),
            ("body", """Cadence broadcasts clock phase, beat, BPM, transport, master band energy, kick onsets and a drop-aware intensity signal over OSC. Phosphor listens and answers: motion on the beat, parameters on the bands, flashes on the kick, and the whole image surging into the drop. The bundle includes the full plugin line too — Cell, Tincture, Contour, Spazio, Glue, Stesso and Tonnetz."""),
            ("acts", [("/cadence/#bundle", "See the bundle &rarr;", "")]),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Phosphor is the SHLabs studio made visible — sound turned into light."""),
            ("body", """A premium, closed-source SHLabs release in active development. This page is an early look; pricing and availability are announced when it ships. For early access, or questions about a specific host, projector or media server, write to us."""),
            ("acts", [(MAIL, "Write us", "fill"), ALL_PRODUCTS]),
        ]},
    ],
}

# ─── Cell ─────────────────────────────────────────────────────────────
PRODUCTS["cell"] = vst(
    name="Cell",
    title="Cell — SHLabs",
    desc="""Cell is a lightweight, CPU-frugal subtractive synthesizer — two band-limited oscillators, sub and noise into one state-variable filter, with envelopes, an LFO, a compact mod matrix and a bypass-when-off FX rack. VST3 / AU / Standalone.""",
    crumb=("Synthesizers &amp; instruments", "/#cat-synths"),
    cat="Subtractive synthesizer",
    claim="""A lightweight, CPU-frugal subtractive synth — the clean analog voice you can load on every track.""",
    lead="""Two band-limited oscillators, sub and noise into one state-variable filter, with filter and amp envelopes, an LFO and a compact modulation matrix. Nothing you don't need, and almost no CPU.""",
    shot=("/img/shots/cell.jpg", "The Cell plugin interface", 1280, 843),
    rows=[
        ("The voice", "Two oscillators, sub and noise",
         """Two independent oscillators — saw, pulse with PWM, triangle or sine — plus a sub an octave or two down and a white-noise source, mixed into one clean signal path."""),
        ("The filter", "One clean state-variable filter",
         """An Andy-Simper SVF with cutoff, resonance and key-tracking — stable at every setting — with its own dedicated envelope and amount control. Low-pass warmth or biting resonance."""),
        ("Envelopes &amp; LFO", "Shape and movement",
         """A filter ADSR and an amp ADSR for the essentials, plus one LFO — everything you need to make the voice breathe, and none of the clutter."""),
        ("Mod matrix", "A compact modulation matrix",
         """Four assignable slots route Filter Env, Amp Env, LFO, Velocity, Mod Wheel, Key Track or Aftertouch to cutoff, resonance, pitch, PWM, oscillator level, pan and LFO rate."""),
        ("FX rack", "Effects when you want them",
         """A built-in rack — drive, chorus, ping-pong delay and reverb — that bypasses itself completely when off, so a dry Cell stays as cheap as it gets."""),
        ("Featherweight", "Stack it everywhere",
         """Band-limited PolyBLEP oscillators and control-rate modulation keep it clean and almost free — around one percent of a CPU core for eight voices — so you can run one on every track. Thirty presets to start."""),
    ],
)

# ─── Tincture ─────────────────────────────────────────────────────────
PRODUCTS["tincture"] = vst(
    name="Tincture",
    title="Tincture — SHLabs",
    desc="""Tincture is a wavetable synthesizer built around modulation you can touch: band-limited morphing wavetables, warp into FM and ring-mod, drawable LFOs, a 48-slot matrix and a studio FX rack. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Synthesizers &amp; instruments", "/#cat-synths"),
    cat="Wavetable synthesizer",
    claim="""A wavetable synthesizer built around one idea: modulation you can touch.""",
    lead="""Morph band-limited wavetables, warp them into sync, FM and ring-mod territory, then drag an LFO straight onto any knob and watch the sound move — drawable LFOs, live modulation rings and a studio FX rack included.""",
    shot=("/img/shots/tincture.jpg", "The Tincture plugin interface", 1280, 1170),
    rows=[
        ("Wavetables", "Morph without the fizz",
         """Two wavetable oscillators on a band-limited mip-mapped engine — clean at any pitch, no aliasing. Morph across frames on a live waterfall display, browse the factory bank or drop any Serum-format WAV straight onto it."""),
        ("Warp", "Bend every table further",
         """Per-oscillator warp multiplies the timbral space of every table: hard sync, bend, PWM, mirror — plus FM and ring modulation from oscillator two. Warp amount is a modulation target like everything else."""),
        ("Modulation", "Drag it onto anything",
         """Grab an LFO, envelope or macro chip and drop it on any knob — every valid target glows on the way. Coloured rings show depth, live markers show the actual moving values, and a 48-slot matrix keeps the overview."""),
        ("Drawable LFOs", "Draw the movement",
         """Four LFOs with a drawable curve editor: click to add points, snap to the grid, bend each segment by dragging it. Tempo-sync them for pumps and gates, or run them free for slow drift."""),
        ("Voice", "Wide, thick, playable",
         """Up to 16-voice unison per oscillator with detune, blend and stereo spread; sub and coloured noise; dual state-variable filter with drive; poly, mono and legato modes with glide and velocity response."""),
        ("Studio FX", "Finished sound, in the box",
         """A seven-stage rack: distortion, chorus, tempo-synced ping-pong delay, a Dattorro plate reverb, EQ, an SSL-style bus compressor and a maximizer on the output — the same engines as the SHLabs mastering plugins."""),
    ],
)

# ─── Slicery ──────────────────────────────────────────────────────────
PRODUCTS["slicery"] = vst(
    name="Slicery",
    title="Slicery — SHLabs",
    desc="""Slicery is a slice instrument from SHLabs: drop in a loop, chop it into playable slices across the keyboard, shape each one, and grab the keepers to your library. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Synthesizers &amp; instruments", "/#cat-synths"),
    cat="Slice instrument",
    claim="""The chop-and-play workflow you actually repeat, in one focused instrument.""",
    lead="""Drop in a song or a loop and Slicery chops it into slices, maps them across the keyboard, and lets you play them back — then save the ones you love out to your sample library.""",
    shot=("/img/shots/slicery.jpg", "The Slicery plugin interface", 1280, 921),
    rows=[
        ("Chop", "Transient or grid",
         """Slice by onset detection with a sensitivity control, or divide cleanly by note value at a set tempo. Markers are drawn right over the waveform, ready to nudge."""),
        ("Playable", "Across the keyboard",
         """Every slice maps chromatically from C1 upward, so the chop is instantly playable from your host or a controller — audition a slice with a click, or perform the whole loop by hand."""),
        ("Per-slice voice", "Shape every hit",
         """Gain, pitch (±24), reverse, anti-click fades, gate vs one-shot, and choke groups for hi-hat-style mutual exclusivity — each slice tuned to sit exactly how you want."""),
        ("Library", "Keep the good ones",
         """Found a one-shot you love? Name it and grab it straight to your sample library. Slicery is as much a sample-prep tool as an instrument."""),
        ("Launch clips", "Loop &amp; sync",
         """Turn a slice into a looping launch clip locked to a shared clock — Slicery doubles as a clip launcher for hybrid performance rigs."""),
        ("Workflow", "Fast and focused",
         """Drag-and-drop loading, a clear waveform with slice pads, and a workflow centred on the loop you repeat: chop, play, keep. Think ReCycle × Serato Sample, distilled."""),
    ],
)

# ─── Contour ──────────────────────────────────────────────────────────
PRODUCTS["contour"] = vst(
    name="Contour",
    title="Contour — SHLabs",
    desc="""Contour is the first SHLabs VST: a multi-LFO modulation rack with a draggable curve editor, tempo sync, multiband routing and MIDI output. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Effects", "/#cat-effects"),
    cat="Multi-LFO modulation rack",
    claim="""A modulation rack built around a draggable curve editor.""",
    lead="""Draw the exact shape of your modulation, lock it to the beat, and route it where it needs to go. Four independent curve-LFOs, tempo-synced or free, shaping volume, pan and a built-in filter — the sidechain pump, trance gate, auto-pan and rhythmic filter moves, all from one panel.""",
    shot=("/img/shots/contour.jpg", "The Contour plugin interface", 1280, 1137),
    rows=[
        ("Curve editor", "Draw your modulation",
         """A multi-point curve with bendable segments — drag points, shape the tension, snap to the grid. A library of starter shapes (sidechain pump, trance gates, stairs, pluck, sample &amp; hold) gets you moving fast."""),
        ("Four LFOs", "A modulation rack",
         """Four independent curve-LFOs, each routable to volume, pan, filter cutoff or resonance — stack them on one target or spread them across several. Per-LFO depth, smoothing, phase, swing, invert and stereo offset."""),
        ("Locked in time", "Sync, free, or triggered",
         """Tempo-sync to bar fractions (dotted and triplet included), run free in Hz, retrigger from MIDI notes, or follow the audio with an envelope trigger for hands-free, transient-locked ducking."""),
        ("Multiband", "Per-band movement",
         """Split into two or three bands and route each LFO to a band — duck only the lows under the kick while the highs breathe, or auto-pan a single band. Phase-correct crossovers, adjustable split points."""),
        ("MIDI out", "Send the shapes out",
         """Each LFO can stream as a MIDI CC, turning your drawn curves into control data for hardware and other instruments — the curve editor as a modulation source beyond the plugin itself."""),
        ("Workflow", "Made to play",
         """A clean, resizable interface with the input waveform behind the curve so you line modulation up to transients, undo/redo on every move, and a preset browser for your own shapes and patches."""),
    ],
)

# ─── Spazio ───────────────────────────────────────────────────────────
PRODUCTS["spazio"] = vst(
    name="Spazio",
    title="Spazio — SHLabs",
    desc="""Spazio is a reverb–delay continuum: a studio delay at one end, a hall at the other, and the diffused, blooming territory in between — morphed by one CONTINUUM control. Tempo-synced echoes, an 8-line modulated reverb network, freeze, ducking and a live decay-profile display. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Effects", "/#cat-effects"),
    cat="Reverb and delay continuum",
    claim="""One engine for every space between echo and hall.""",
    lead="""A precision studio delay at one end, a lush modulated reverb at the other — and the territory in between, where repeats smear, diffuse and bloom into tails, on a single CONTINUUM control. Every parameter underneath stays yours to adjust.""",
    shot=("/img/shots/spazio.jpg", "The Spazio plugin interface", 1280, 813),
    rows=[
        ("Continuum", "Echo to hall, one move",
         """The headline control morphs the whole engine: pure repeats on the left, pure space on the right. In the middle the reverb network is fed by the echoes themselves, so every repeat blooms a tail. Equal-power, fully smoothed, automatable."""),
        ("Echo", "A serious studio delay",
         """Tempo-synced (sixteen divisions, dotted and triplet) or free-running per-channel times, ping-pong cross-feed, feedback past 100% that self-limits through an in-loop saturation stage, loop filters that darken each pass, and wow-style modulation from subtle chorus to tape wobble."""),
        ("Smear", "The in-between maker",
         """A diffuser inside the feedback loop turns clean repeats into washes that thicken with every pass — slapback stays crisp at zero, dub clouds and ambient smears live at the top. This is the zone most delays and reverbs leave uncovered."""),
        ("Space", "A modern modulated reverb",
         """An eight-line modulated reverb network with two-band decay — let the lows bloom past the mids or tighten them — high-frequency damping, size from plate to vast hall, decay from 0.1 to 60 seconds, and a lossless FREEZE that holds the room forever."""),
        ("Decay profile", "See the space you are shaping",
         """The display renders the actual impulse response of your current settings — tap spikes, bloom, tail — recomputed live as you turn knobs. Not a stock animation: the real engine, rendered ahead of time."""),
        ("Control", "Mix-ready by design",
         """Program-dependent ducking keeps the space behind the performance, width runs from mono to extra-wide, a tilt tone darkens or opens the wet path — thirty-six parameters, zero latency, click-free time glides (crossfade or tape repitch), factory and user presets."""),
    ],
)

# ─── Glue ─────────────────────────────────────────────────────────────
PRODUCTS["glue"] = vst(
    name="Glue",
    title="Glue — SHLabs",
    desc="""Glue is an SSL-style mastering bus compressor: program-dependent glue with stepped controls, a sidechain high-pass, Mid/Side, parallel mix and a big gain-reduction meter. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Mastering tools", "/#cat-mastering"),
    cat="Mastering bus compressor",
    claim="""The compressor that does what its name says: it glues a mix together.""",
    lead="""An SSL G-series-style bus compressor with a clean VCA core, program-dependent release and the mastering essentials — gentle, musical gain riding across the whole stereo image, on your mix bus or master.""",
    shot=("/img/shots/glue.jpg", "The Glue plugin interface", 1280, 759),
    rows=[
        ("The glue", "Bus compression, done right",
         """A feed-forward VCA compressor in the spirit of the SSL G-series — the sound that holds a mix together. Subtle, cohesive gain movement that makes a busy arrangement feel like one performance."""),
        ("SSL controls", "Stepped &amp; program-dependent",
         """The classic stepped ratio, attack and release, plus an Auto release that adapts to the music — brief peaks recover fast, sustained passages breathe slowly."""),
        ("Sidechain HPF", "Stop the low-end pump",
         """A high-pass on the detector keeps kick and bass from triggering the whole bus, so the compression follows the music instead of riding the sub. The single most important control for mastering glue."""),
        ("Mid / Side", "Centre and sides, apart",
         """Switch the detector into Mid/Side and compress the centre and the stereo sides independently — tighten the middle without squashing the width, or vice versa. Adjustable stereo link from dual-mono to fully linked."""),
        ("Parallel mix", "New-York blend",
         """A wet/dry Mix control for parallel compression — slam the compressed path and dial it back under the dry signal for density and punch without losing the transients."""),
        ("Metering", "See the gain ride",
         """A large gain-reduction meter anchors the panel, flanked by input and output levels, with a soft knee, makeup and an auto-gain option so the level stays matched while you dial in the feel."""),
    ],
)

# ─── Stesso ───────────────────────────────────────────────────────────
PRODUCTS["stesso"] = vst(
    name="Stesso",
    title="Stesso — SHLabs",
    desc="""Stesso is a mastering equaliser: up to 24 bands and eight filter types over a live pre/post spectrum, a draggable curve, gentle 6 to surgical 96 dB/oct slopes, and per-band Left/Right or Mid/Side. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Mastering tools", "/#cat-mastering"),
    cat="Mastering equaliser",
    claim="""A transparent mastering equaliser built around a draggable curve over a live spectrum.""",
    lead="""Up to twenty-four bands, eight filter types and slopes from a gentle 6 to a surgical 96 dB per octave — broad tone-shaping and tight problem-solving from one clean panel.""",
    shot=("/img/shots/stesso.jpg", "The Stesso plugin interface", 1280, 871),
    rows=[
        ("Drag the curve", "Shape it by hand",
         """Drop a node anywhere on the response and drag it — frequency and gain under the cursor, Q on the scroll wheel. The whole EQ is one interactive curve drawn straight over the spectrum."""),
        ("24 bands · 8 types", "From broad to surgical",
         """Up to twenty-four bands and eight filter shapes — bell, low and high shelf, high- and low-pass, notch and more — with slopes from a gentle 6 to a razor 96 dB per octave."""),
        ("Pre / post spectrum", "See what you hear",
         """A real-time analyser shows the signal before and after the EQ behind the curve, so every move is informed — find the resonance, then place the band exactly on it."""),
        ("L/R · Mid/Side", "Per-band stereo",
         """Set any band to process the full stereo, just the left or right, or the mid or the sides — de-ess only the centre, brighten only the width, tame a channel imbalance."""),
        ("Precision DSP", "Clean and true",
         """A precise, independently verified filter core — the response you draw is the response you get, transparent enough for the master bus and sharp enough to fix a problem."""),
        ("Workflow", "Made to master",
         """A clean, resizable interface with a readable grid, solo-listen per band to audition a move, gain matching and a preset browser for your own mastering chains."""),
    ],
)

# ─── Tonnetz ──────────────────────────────────────────────────────────
PRODUCTS["tonnetz"] = vst(
    name="Tonnetz",
    title="Tonnetz — SHLabs",
    desc="""Tonnetz is a MIDI harmony conductor: a master key and scale, an interactive Neo-Riemannian lattice, three quantizers, a voiced chord generator, arpeggiator, bass, drone and a progression sequencer — all driving your synths over MIDI. VST3 / AU / Standalone. Coming soon.""",
    crumb=("MIDI generators &amp; composers", "/#cat-midi"),
    cat="MIDI harmony conductor",
    claim="""A harmonic conductor for your whole rig.""",
    lead="""Set a key and scale, then play chords from an interactive Neo-Riemannian lattice while three quantizers, a voiced chord generator, an arpeggiator, bass and drone all stay locked to the same harmony — and drive any synth or hardware over MIDI. No sound of its own; it conducts the instruments you already own.""",
    shot=("/img/shots/tonnetz.jpg", "The Tonnetz plugin interface", 1280, 1226),
    rows=[
        ("The lattice", "Play harmony in space",
         """An interactive Neo-Riemannian Tonnetz lattice at the centre of the plugin — click a triad and the whole rig follows, with the notes lighting up as they play. The harmonic map no other plugin puts front and centre."""),
        ("Master harmony", "One key, everything obeys",
         """A live, modulatable key and scale with degree → chord stacking (root / 3 / 5 / 7 / 9 / 11 / 13). Change the degree and every part re-voices, in tune, instantly."""),
        ("Quantizers", "Never a wrong note",
         """Three independent channels snap incoming MIDI to the master key — Scale, Triad, 7th, 9th or Full — each on its own input/output MIDI channel and octave. Play freely; it stays in key."""),
        ("Chord + parts", "A whole band, in key",
         """A voiced chord generator with voice-leading, spread and inversions, plus an arpeggiator, bass and drone — each routable to its own synth on its own channel, with swing and humanize for feel."""),
        ("Song mode", "Write the progression",
         """A 16-step progression sequencer drives the degree from the clock — host transport or internal — so your changes land exactly on the beat or bar. Twelve factory presets to start, save your own."""),
        ("Perform", "Built to play live",
         """Chord-by-MIDI, global transpose, quantized chord changes, MIDI-Learn on every control, and drag-to-DAW MIDI export of the whole arrangement. A performance instrument, not just a utility."""),
    ],
)

# ─── Metro 185 ────────────────────────────────────────────────────────
PRODUCTS["metro185"] = vst(
    name="Metro 185",
    title="Metro 185 — SHLabs",
    desc="""Metro 185 is a professional MIDI-effect step sequencer from SHLabs, in the lineage of the RYK M-185 and Roland System 100m — reimagined for the DAW. VST3 / AU / Standalone. Coming soon.""",
    crumb=("MIDI generators &amp; composers", "/#cat-midi"),
    cat="MIDI step sequencer",
    claim="""A step sequencer in the lineage of the RYK M-185 and Roland System 100m, reimagined for the DAW.""",
    lead="""A pure MIDI effect — drop it on a MIDI track, route it into any instrument, and drive it with eight deep, expressive steps.""",
    shot=("/img/shots/metro185.jpg", "The Metro 185 plugin interface", 1280, 865),
    rows=[
        ("Step engine", "Eight deep steps",
         """Eight steps with sample-accurate MIDI generation locked to host transport. Per step: pitch, gate mode, pulse count (1–8), velocity, gate length, ratchets, slide, skip and two CC outputs."""),
        ("14 gate modes", "Per-step character",
         """Single, repeat, legato, hold, divisions, probability gates and two Euclidean modes that spread onsets across a step's pulses — plus RYK-style ratcheting up to four re-triggers."""),
        ("Musical", "34 scales &amp; swing",
         """Automatic quantization to 34 scales with root selection, global and MIDI-input transpose, swing on every other pulse, and pitch-bend slide between steps."""),
        ("Play modes", "Direction &amp; chance",
         """Forward, reverse, ping-pong, random and brownian — each with a "fixed" variant that always traverses all eight steps. Sequence length 1–8."""),
        ("DAW-native", "Built for the host",
         """Full transport sync, every control automatable, right-click MIDI-learn on any parameter, state saved with the project, and a configurable MIDI output channel."""),
        ("Patterns", "Save &amp; recall",
         """Store and load full patterns to disk, and route the two per-step CC outputs to modulate anything in your rack — the sequence becomes a modulation source too."""),
    ],
)

# ─── Stochast (VCV) ───────────────────────────────────────────────────
PRODUCTS["stochast"] = {
    "name": "Stochast",
    "title": "Stochast — SHLabs",
    "desc": """Stochast is a free, open-source suite of 28 VCV Rack 2 modules across five plugins that turn real statistical, social, and stochastic processes into control voltage. Sample a distribution, clock a segregation grid, sweep a filter with an epidemic curve — quirky, generative patch material with genuinely correct math under the hood. GPL-3.0. macOS, Windows, Linux.""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "5 plugins · 28 modules",
    "status": "Free &amp; open source",
    "soon": False,
    "claim": "Real math as patchable voltage.",
    "lead": """Twenty-eight open-source modules across five plugins that turn real statistical, social, and stochastic processes into control voltage you can patch anywhere in your rack. Sample a distribution as a modulation source, clock a segregation grid into a gate sequencer, let an epidemic curve sweep a filter. Quirky, generative, alive — and the math underneath is the genuine article, not a toy.""",
    "spec": ["5 plugins · 28 modules", "GPL-3.0", "macOS · Windows · Linux"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("Real math", "Instruments built from processes",
                 """Each module is a genuine statistical, agent-based, or dynamical process — a bootstrap resampler, a Granovetter cascade, an SIR epidemic, a reaction-diffusion field — exposed as knobs and control voltage. The output is quirky and alive precisely because the process underneath behaves the way the theory says it should."""),
                ("Patchable", "Voltage you can route anywhere",
                 """Patch them like anything else on your rack. A sampling distribution becomes a modulation source; a segregation grid becomes a generative gate pattern; a drift-diffusion decision fires triggers; an opinion-dynamics model becomes a slow, evolving CV sweep. No stats background needed to enjoy it — and if you do know the math, you can trust it."""),
                ("Reproducible", "Seeded, exact, portable",
                 """Every random module wraps a Mersenne-Twister generator with an explicit on-panel seed, so the same seed is byte-identical across macOS, Windows and Linux. Closed-form quantities use the standard numerical recipes — Lentz continued fractions, BCa bootstrap, Sanger's rule. Patches are plain-JSON <span class="mono">.vcv</span> files, and Tape exports its buffer to CSV for R, Python or Julia."""),
            ]),
        ]},
        {"parts": [
            ("head", "The five plugins", ""),
            ("rows", [
                ("Methods · 15 modules", "Statistical workflow",
                 """Sample · Frame · Regress · Test · Boot · Lag · Code · Tab · Strata · Cohort · Factor · Seed · Tape · Gauge · Quantity. The full sampling-to-inference chain — draws, regressions, tests and bootstraps — turned into patchable voltage."""),
                ("Polis · 6 modules", "Agent-based social models",
                 """Cascade · Discourse · Pareto · Dilemma · Diffusion · Network. Granovetter cascades, opinion dynamics, wealth condensation, iterated dilemmas, and small-world / scale-free networks as evolving control sources."""),
                ("Epi · 1 module", "Network epidemiology",
                 """Outbreak — SIR-style epidemic spread on Watts-Strogatz, Erdős-Rényi and Barabási-Albert graphs. "Flatten the curve" is one patch cable away, its infection wave driving whatever you route it into."""),
                ("Space · 3 modules", "Spatial dynamics",
                 """Life · Schelling · Turing. Conway's Game of Life with rule presets, Schelling segregation on a 24 × 24 grid, and Gray-Scott reaction-diffusion traversing spots, stripes and labyrinths."""),
                ("Decisions · 3 modules", "Behavioral economics &amp; cognition",
                 """Prospect · Bandit · DDM. Kahneman-Tversky prospect theory, K-armed bandits with ε-greedy / UCB1 / Thompson sampling, and the Ratcliff drift-diffusion model of decision timing."""),
                ("Not a classroom tool", "This one is for patching",
                 """Stochast began as a teaching idea, but what it really is is a box of modular-synth instruments made from real mathematics. If you want statistics as a teaching tool instead, that is the job of the separate, browser-based Empiria app — Stochast is for music."""),
            ]),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Free, open source, and correct under the hood. No paid tier, no telemetry, no account."""),
            ("body", """You'll need <strong>VCV Rack 2</strong> — a free download for macOS, Windows and Linux from <a class="link" href="https://vcvrack.com/Rack" target="_blank" rel="noopener">vcvrack.com/Rack</a>. Grab the latest <strong>.vcvplugin</strong> archives from GitHub releases, drop them into Rack's user plugin folder and restart — the modules appear under the <strong>SHLabs</strong> brand. Source is on GitHub under GPL-3.0-or-later, with a full methods manual: read it, build it, or send a fix."""),
            ("acts", [
                ("https://github.com/shlabs-audio/stochast/releases/latest", "Download the plugins &darr;", "fill"),
                ("https://github.com/shlabs-audio/stochast/blob/main/docs/methods_manual.md", "Read the manual &rarr;", ""),
                ("https://github.com/shlabs-audio/stochast", "Source on GitHub &rarr;", ""),
                ALL_VCV,
            ]),
        ]},
    ],
}

# ─── Mashina (VCV) ────────────────────────────────────────────────────
PRODUCTS["mashina"] = {
    "name": "Mashina",
    "title": "Mashina — SHLabs",
    "desc": """Mashina is a free family of eight VCV Rack 2 modules pairing Soviet-era analog character with West-Coast synthesis: drum voices, oscillators, a master clock, a plate reverb, and generative sequencers. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "8 modules",
    "status": "Free download",
    "soon": False,
    "claim": "Soviet machines meet the West Coast.",
    "lead": """A family of eight VCV Rack modules that pair the gritty, idiosyncratic character of mid-century Soviet synthesizers — the Polivoks, the ANS, the Aelita — with the patch-cable, function-generator tradition of West Coast synthesis. Drum voices, oscillators, a master clock, a plate reverb, and generative sequencers, all in one rack.""",
    "spec": ["8 modules", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("Why Soviet", "Character from constraint",
                 """The Eastern-bloc synthesizer tradition worked under tight component constraints, which produced characterful nonlinearities — overdriven envelopes, drifty VCOs, idiosyncratic filters — that became part of the instrument's voice. Mashina treats that voice as a design ideal, not as kitsch. Each module's name is its Russian function."""),
                ("Why West Coast", "Synthesis as patching",
                 """Buchla, Serge, Make Noise: synthesis as patching rather than playing, timbre as a parametric space rather than a preset library. Mashina inherits that grammar — open-ended, parameter-rich modules that reward exploration. Soviet machines met the West Coast nowhere in real life; Mashina puts them together."""),
                ("One family", "A shared panel language",
                 """A consistent SHLabs panel grammar — a gunmetal field, a red family stripe under each header, and clear left-to-right signal flow — shared with the other SHLabs series so a Mashina module reads as part of one instrument family."""),
            ]),
        ]},
        {"parts": [
            ("head", "The eight modules", ""),
            ("rows", [
                ("Udar · удар", "Percussion voice + sequencer",
                 """Analog-style drum voice with an 8-step sequencer, a DFAM homage: two VCOs, noise, a tanh-saturated ladder filter, per-step pitch / velocity / gate modes, conditional triggers, and polyphonic per-step trigger and velocity outputs to drive poly VCAs and envelopes."""),
                ("Klubok · клубок", "Generative dual sequencer + voice",
                 """A Labyrinth-style pair of step engines with per-step probability, length, divergence, and feedback for evolving patterns — feeding their own VCO, filter, wavefolder and plate-reverb voice, or any other module via 1V/oct and gate streams."""),
                ("Bochka · бочка", "Techno kick voice",
                 """A punchy kick: pitch-swept sine, filtered click, sub layer, transient punch, tanh drive, tilt EQ, and a choke input. KIT MODE turns one polyphonic trigger cable into kick / snare / hat / clap — a mini drum kit in one module."""),
                ("Takt · такт", "Master clock",
                 """A Pamela-style master clock with eight independent divided / multiplied outputs (/64 to ×64), tap tempo, run / stop, reset, global swing, pulse width, and BPM CV, plus a master beat output for syncing the rest of the rack."""),
                ("Otzvuk · отзвук", "Plate reverb",
                 """A warm Dattorro-style plate with shimmer, a self-ducker, modulation, tilt EQ, and tape drive in the feedback path. CHARACTER morphs ROOM → PLATE → HALL → SHIMMER, and pre-delay can be tempo-synced from a clock input."""),
                ("Strela · стрела", "Register additive VCO",
                 """A register-driven additive oscillator inspired by 1950s Soviet console computers: a 16-bit switch register controls 16 harmonics, a clock shifts the register, and a polyphonic bit-CV input combines via OR / AND / XOR. Spectral thinning, tilt, per-partial phase distortion, and drive."""),
                ("Volna · волна", "Polyphonic analog VCO",
                 """A polyphonic oscillator with four simultaneous band-limited outputs (sine, triangle, saw, pulse), PolyBLEP anti-aliasing, CV-able PWM, hard sync, FM with a LIN / EXP switch, per-voice drift for natural chorus, and a warmth control."""),
                ("Podton · подтон", "Subharmonic synth",
                 """A Subharmonicon-style polyrhythmic voice: two VCOs each with two integer-divided sub-oscillators, dual 4-step sequencers on independent clock divisions, a ladder filter, per-step gate modes, conditional triggers, and a drone mode."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", ""),
            ("lead", """Free, and built to be played. No account, no nag screen."""),
            ("body", VCV_NEED + """ Download the <strong>.vcvplugin</strong> below and drop it into Rack's user plugin folder, then restart — the modules appear under the <strong>SHLabs</strong> brand."""),
            ("mono", VCV_MAC),
            ("acts", [
                ("/downloads/SHLabs-Mashina-2.0.0-mac-arm64.vcvplugin", "Download the plugin &darr;", "fill"),
                ALL_VCV,
            ]),
        ]},
    ],
}

# ─── Lucida (VCV) ─────────────────────────────────────────────────────
PRODUCTS["lucida"] = {
    "name": "Lucida",
    "title": "Lucida — SHLabs",
    "desc": """Lucida is a free generative-visual series of VCV Rack 2 modules: emergent systems — a cellular-automaton CV grid (Colony) and a probabilistic shift register (Turing) — rendered on screen and turned into CV. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "2 modules · Colony, Turing",
    "status": "Free download",
    "soon": False,
    "claim": "Generative systems, made visible.",
    "lead": """A series of VCV Rack modules built around emergent systems — cellular automata, shift registers, iterated processes — that you watch evolve on screen and patch as control voltage. Each module is a small generative world: set it running, nudge it, and harvest the patterns it produces as pitch, gates, and modulation.""",
    "spec": ["2 modules", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("Seen, not hidden", "Systems you can watch",
                 """Lucida modules are generative systems you can see. The on-panel display is not decoration: it is the state of the process, and watching it is how you learn to steer it. A change to a knob propagates visibly across the grid or the register before it ever reaches a cable."""),
                ("Patchable emergence", "Self-organizing CV",
                 """Every module turns its internal dynamics into useful CV — scan taps, polyphonic rows, quantized pitch, gates — so a self-organizing system becomes a playable sequencer and modulation source, not just a screensaver."""),
                ("One family", "A creep-green accent",
                 """Lucida inherits the SHLabs industrial panel grammar — gunmetal field, header strip, clear signal flow — with a creep-green family accent that ties the series together and sets it apart from Mashina's red."""),
            ]),
        ]},
        {"parts": [
            ("head", "The modules", ""),
            ("rows", [
                ("Colony", "Cellular-automaton CV grid",
                 """The flagship. A 24×16 toroidal cellular automaton evolves on screen and emits CV. SPREAD biases the birth / survive rules, MUTATE injects per-cell noise, and FLOW clock-multiplies or -divides the simulation step. Paint cells with the mouse, sweep the scan position with SCAN_CV, freeze the simulation while keeping outputs live, and choose scan-and-tap, polyphonic-row / column, or quadrant-mix output modes."""),
                ("Turing", "Probabilistic shift register",
                 """A 16-bit looping shift register in the Music Thing Modular tradition. LOCK slides between full randomness and an exact repeating pattern; LENGTH sets the loop (2–16 bits). A built-in quantizer (10 scales × 12 roots) puts the output straight onto a melody. Outputs: quantized V/OCT, raw bipolar analog, a write-position gate, polyphonic per-bit gates, and a clock pulse. The display shows the live bits above a scrolling history, so the lock pattern becomes visible."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", ""),
            ("lead", """Free, and built to be played. No account, no nag screen."""),
            ("body", VCV_NEED + """ Colony and Turing ship together in the <strong>SHLabs-Colony</strong> plugin: download the <strong>.vcvplugin</strong> below and drop it into Rack's user plugin folder, then restart — the modules appear under the <strong>SHLabs</strong> brand."""),
            ("mono", VCV_MAC),
            ("acts", [
                ("/downloads/SHLabs-Colony-2.0.0-mac-arm64.vcvplugin", "Download the plugin &darr;", "fill"),
                ALL_VCV,
            ]),
        ]},
    ],
}

# ─── Rikoshet (VCV) ───────────────────────────────────────────────────
PRODUCTS["rikoshet"] = {
    "name": "Rikoshet",
    "title": "Rikoshet — SHLabs",
    "desc": """Rikoshet is four free, tempo-synced rhythmic effects for VCV Rack 2: a rhythmic gate, a ping-pong delay, an 8-step pattern delay and a crossfader. Lock them to your clock for movement in time and across the stereo field. Free and open source, GPL-3.0. macOS, Windows, Linux.""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "4 modules · Gate, PingPong, MultiTap, Blend",
    "status": "Free &amp; open source",
    "soon": False,
    "claim": "Rhythmic delay and gate effects.",
    "lead": """Four tempo-synced rhythmic effects for VCV Rack. A rhythmic gate, a ping-pong delay, an 8-step pattern delay and a crossfader — feed them a clock and everything they do locks to musical time, from two bars down to a 1/32. Pull the clock and they run free. CV over the controls that matter.""",
    "spec": ["4 modules", "GPL-3.0", "macOS · Windows · Linux"],
    "sections": [
        {"parts": [
            ("head", "What they share", ""),
            ("rows", [
                ("In time", "Locked to your clock",
                 """Patch a clock and every module snaps its motion to musical subdivisions — two bars down to a 1/32, with dotted and triplet values. No clock? They run from their own tempo knob, so they work standalone or in a patch."""),
                ("Stereo", "Movement across the field",
                 """These are effects that move in space as well as time — stereo offset, ping-pong cross-feed, alternating tap panning and width. They stay out of the way harmonically and put their character into timing and the stereo image."""),
                ("CV", "Modulate what matters",
                 """Every module exposes CV over the controls you'd actually want to automate — rate, time, feedback, mix, depth — plus click-free parameter glides so sweeps and modulation stay clean, and dry-through bypass on every one."""),
            ]),
        ]},
        {"parts": [
            ("head", "The four modules", ""),
            ("rows", [
                ("Gate · 10 HP", "Rhythmic gate",
                 """A tempo-synced amplitude gate — tremolo to hard pattern gating. Rate picks from 14 musical subdivisions; Shape morphs a hard square to a raised cosine; Pulse Width sets the duty cycle; a Stereo Offset slips the right channel for width. CV over Rate, Shape, Depth and PW, plus a gate-envelope output."""),
                ("PingPong · 12 HP", "Ping-pong delay",
                 """A stereo delay with cross-fed feedback that bounces repeats between channels. Spread offsets the right-channel time for tumbling echoes, Cross sets how much feedback crosses sides, and low- and high-cut sit in the feedback path so repeats darken naturally as they fade. Sync or free time."""),
                ("MultiTap · 20 HP", "Pattern delay",
                 """An 8-step delay across a tempo-synced window. Per-tap level sliders place the hits, alternating L/R panning with Spread opens the stereo image, Decay tapers the taps toward the end, and Feedback recirculates the whole pattern — darkening a little each pass through the high-cut."""),
                ("Blend · 6 HP", "Crossfader",
                 """A stereo A/B crossfader with input drive and an equal-power curve. Blend parallel chains of Rikoshet effects into one rhythm, or use it as a dry/wet control around a serial chain. CV over Mix and Drive — the small utility that ties the family together."""),
            ]),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Free, open source, and built to be played. No account, no nag screen."""),
            ("body", """Search <strong>Rikoshet</strong> in the VCV Library and click Add, or download the plugin directly and drop it into Rack's user plugin folder. It appears under the <strong>SHLabs</strong> brand. Source is on GitHub under GPL-3.0 — read it, build it, or send a fix."""),
            ("acts", [
                ("https://github.com/shlabs-audio/rikoshet/releases/latest", "Download the plugin &darr;", "fill"),
                ("https://github.com/shlabs-audio/rikoshet", "Source on GitHub &rarr;", ""),
                ALL_VCV,
            ]),
        ]},
    ],
}

# ─── Atmos (VCV) ──────────────────────────────────────────────────────
PRODUCTS["atmos"] = {
    "name": "Atmos",
    "title": "Atmos — SHLabs",
    "desc": """Atmos is a free family of four VCV Rack 2 modules for tone, space, and time: the Helix ladder filter, the Halo stereo repeater, the Skywave character delay, and the Metro 185 step sequencer. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "4 modules · Helix, Halo, Metro185, Skywave",
    "status": "Free download",
    "soon": False,
    "claim": "Tone, space and time.",
    "lead": """Four VCV Rack modules for shaping tone, space, and time: the <strong>Helix</strong> transistor-ladder filter, the <strong>Halo</strong> stereo repeater, the <strong>Skywave</strong> character delay with reverb, and the <strong>Metro 185</strong> step sequencer. A filter, two stereo time effects, and a sequencer to drive them.""",
    "spec": ["4 modules", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "The four modules", ""),
            ("rows", [
                ("Helix", "Transistor-ladder filter",
                 """A 4-pole Moog-style lowpass that self-oscillates and tracks V/oct, so it doubles as a sine source. Three twists go beyond a clone — DRIFT detunes the poles, FRICTION adds per-stage saturation, TURBULENCE feeds noise into the resonance. Simultaneous LP / HP / BP outs, selectable slope, drive, and 16-voice poly."""),
                ("Halo", "Stereo color repeater",
                 """A modulated multi-tap delay network with two independent zones and polarizing pitch drift, for smeared, gently detuned echoes that spread a sound across the stereo field."""),
                ("Skywave", "Character delay &amp; reverb",
                 """A multi-model stereo delay with scatter reverb, themed on radio propagation. Three engines — longwave (tape), shortwave (bucket-brigade), and microwave (clean digital) — plus internal modulation, atmospheric hiss and crackle, freeze, and clock sync."""),
                ("Metro 185", "Step sequencer",
                 """An eight-stage sequencer in the M185 / Metropolis tradition: each stage has a pitch, a pulse count, and a gate type. The count and gate-type controls are vertical sliders and patchable over polyphonic CV, so the sequence itself becomes modulatable."""),
            ]),
        ]},
        {"parts": [
            ("head", "Design notes", ""),
            ("rows", [
                ("Long-form by default", "Set it and listen",
                 """Atmos modules assume the listener won't be holding still in front of a knob. Knob ranges resolve into multi-minute evolutions, modulation depths are calibrated for slow movement, and defaults sit at "interesting but not active." Patch one in and leave it."""),
                ("Aesthetic", "Warm-gold, few jacks",
                 """The family uses a warm-gold accent under each panel header and layouts that favor large knobs over crowded jack rows — these are tools you set once and listen to, not modules you re-cable every measure."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", "Each module ships as its own plugin"),
            ("lead", """Free, and built to be played. Each module ships as its own plugin — grab the ones you want."""),
            ("body", VCV_NEED + """ Download the <strong>.vcvplugin</strong> files below and drop them into Rack's user plugin folder, then restart — they appear under the <strong>SHLabs</strong> brand."""),
            ("mono", VCV_MAC),
            ("acts", [
                ("/downloads/SHLabs-Helix-2.0.0-mac-arm64.vcvplugin", "Helix &darr;", "fill"),
                ("/downloads/SHLabs-Halo-2.0.0-mac-arm64.vcvplugin", "Halo &darr;", "fill"),
                ("/downloads/SHLabs-Skywave-2.0.0-mac-arm64.vcvplugin", "Skywave &darr;", "fill"),
                ("/downloads/SHLabs-Metro185-2.0.0-mac-arm64.vcvplugin", "Metro 185 &darr;", "fill"),
                ALL_VCV,
            ]),
        ]},
    ],
}

# ─── Terra (VCV) ──────────────────────────────────────────────────────
PRODUCTS["terra"] = {
    "name": "Terra",
    "title": "Terra — SHLabs",
    "desc": """Terra is a free gestural granular sampler for VCV Rack 2 — six grain voices steered by an on-panel XY field over a stereo 8-second buffer. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "1 module",
    "status": "Free download",
    "soon": False,
    "claim": "A gestural granular sampler.",
    "lead": """Terra records a few seconds of audio into a buffer and plays it back as overlapping grains, steered by an on-panel XY field — read position on one axis, grain pitch on the other. Six voices spread around that point for thick, evolving textures.""",
    "spec": ["1 module", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("The field", "Steer six voices by hand",
                 """Six grain voices share a stereo 8-second buffer fed from AUDIO IN; FREEZE captures the buffer so you can scrub a held sound. The signature control is the on-panel XY field: X is buffer read position, Y is grain pitch (±12 semitones). POSITION and PITCH knobs, plus X-CV and Y-CV, set the center of the field."""),
                ("The cloud", "Spread, scatter, shape",
                 """SPREAD distributes the six voices around the center on a ring, SCATTER adds per-grain randomization. DENSITY (1–100 g/s), SIZE (1–500 ms), SHAPE (Hann to rectangular), JITTER, and FEEDBACK round out the grain controls, and V/OCT transposes the whole field."""),
                ("Outputs", "Mix plus per-voice poly",
                 """Outputs are a stereo L/R mix plus a polyphonic OUT carrying one voice per channel, so each of the six grains can be processed downstream independently before you fold them back together."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", ""),
            ("lead", """Free, and built to be played. No account, no nag screen."""),
            ("body", VCV_NEED + """ Download the <strong>.vcvplugin</strong> below and drop it into Rack's user plugin folder, then restart — the module appears under the <strong>SHLabs</strong> brand."""),
            ("mono", VCV_MAC),
            ("acts", [
                ("/downloads/SHLabs-Atlas-2.0.0-mac-arm64.vcvplugin", "Download the plugin &darr;", "fill"),
                ALL_VCV,
            ]),
        ]},
    ],
}


# ═══════════════════════════════════════════════════════════════════════
#  the homepage
# ═══════════════════════════════════════════════════════════════════════

# group id, group label, group aside, [(no, href, category, name, desc, status, status class)]
INDEX_GROUPS = [
    ("cat-live", "Performance &amp; live", "The centre of the rig", [
        ("01", "/cadence/", "Performance mixer &amp; master clock", "Cadence",
         """Four channels of live input or beatgrid players, DJ filter and full-kill EQ, a pre-fader cue bus, and a clock the rest of the rig follows.""",
         "Soon", "is-soon"),
    ]),
    ("cat-synths", "Synthesizers &amp; instruments", "Sound sources you play", [
        ("02", "/cell/", "Subtractive synthesizer", "Cell",
         """The essential analog voice, built to stack. Two band-limited oscillators, sub and noise into one clean state-variable filter. Featherweight on the CPU.""",
         "Soon", "is-soon"),
        ("03", "/tincture/", "Wavetable synthesizer", "Tincture",
         """Modulation you can touch: morphing wavetables, warp into FM and ring-mod, drawable LFOs and a 48-slot matrix.""",
         "Soon", "is-soon"),
        ("04", "/slicery/", "Slice instrument", "Slicery",
         """Chop a loop into playable slices across the keyboard, shape each hit and grab the keepers to your library.""",
         "Soon", "is-soon"),
    ]),
    ("cat-effects", "Effects", "Modulation · space", [
        ("05", "/contour/", "Multi-LFO modulation rack", "Contour",
         """Draw modulation on a curve editor and lock it to the beat. Four curve-LFOs over volume, pan and filter, with MIDI out.""",
         "Soon", "is-soon"),
        ("06", "/spazio/", "Reverb and delay continuum", "Spazio",
         """Studio delay, modulated reverb and everything between on one CONTINUUM control. Echoes that smear and bloom into tails.""",
         "Soon", "is-soon"),
    ]),
    ("cat-mastering", "Mastering tools", "The last mile of a mix", [
        ("07", "/glue/", "Mastering bus compressor", "Glue",
         """SSL-style glue with stepped controls, program-dependent release, sidechain high-pass, Mid/Side and a parallel mix.""",
         "Soon", "is-soon"),
        ("08", "/stesso/", "Mastering equaliser", "Stesso",
         """A draggable curve over a live spectrum. Up to 24 bands, eight filter types, per-band Left/Right or Mid/Side.""",
         "Soon", "is-soon"),
    ]),
    ("cat-midi", "MIDI generators &amp; composers", "Sequencing &amp; harmony brains", [
        ("09", "/tonnetz/", "MIDI harmony conductor", "Tonnetz",
         """Master key and scale, an interactive Tonnetz lattice, three quantizers, chords, arp, bass and drone, driving your synths.""",
         "Soon", "is-soon"),
        ("10", "/metro185/", "MIDI step sequencer", "Metro 185",
         """Eight deep steps in the RYK M-185 and System 100m lineage, reimagined for the DAW. Ratchets, 34 scales, gate modes.""",
         "Soon", "is-soon"),
    ]),
    ("cat-visuals", "Visuals", "Sound you can see", [
        ("11", "/phosphor/", "Audio-reactive video synth", "Phosphor",
         """Beat-locked GPU scenes you throw fullscreen onto a projector. Fields, tunnel, fractals, spectrum, ambient, plus Syphon out.""",
         "Soon", "is-soon"),
    ]),
]

VCV_ROWS = [
    ("12", "/stochast/", "5 plugins · 28 modules", "Stochast",
     """Statistics and emergence as patchable CV: sampling distributions, the bootstrap, agent-based cascades, epidemics, reaction-diffusion.""",
     "Free", "is-free"),
    ("13", "/mashina/", "8 modules", "Mashina",
     """Soviet machines meet the West Coast. Drum voices, oscillators, a master clock, a plate reverb and generative sequencers.""",
     "Free", "is-free"),
    ("14", "/lucida/", "2 modules · Colony, Turing", "Lucida",
     """Generative systems made visible. A cellular-automaton grid and a probabilistic shift-register sequencer with a built-in quantizer.""",
     "Free", "is-free"),
    ("15", "/rikoshet/", "4 modules · Gate, PingPong, MultiTap, Blend", "Rikoshet",
     """Rhythmic delay and gate effects, tempo-synced. Lock them to your clock for movement in time and across the stereo field.""",
     "Free", "is-free"),
    ("16", "/atmos/", "4 modules · Helix, Halo, Metro185, Skywave", "Atmos",
     """Tone, space and time. A transistor-ladder filter, a stereo colour repeater, a character delay with reverb and an eight-stage sequencer.""",
     "Free", "is-free"),
    ("17", "/downloads/SHLabs-Phosphor-2.0.0-mac-arm64.vcvplugin",
     "3 modules · Beam, Chroma, Cathode", "Phosphor for VCV Rack",
     """An LZX-style video chain that passes a lo-fi RGB frame over an expander bus, turning luma and motion back into CV.""",
     "Free &darr;", "is-free"),
]


def index_row(no, href, cat, name, desc, status, scls):
    return (
        '      <a class="row" href="%s">\n'
        '        <span class="row__no">%s</span>\n'
        '        <span class="row__id"><span class="row__cat">%s</span>'
        '<span class="row__name">%s</span></span>\n'
        '        <span class="row__desc">%s</span>\n'
        '        <span class="row__status %s">%s</span>\n'
        '      </a>' % (href, no, cat, name, desc, scls, status)
    )


def homepage():
    groups = []
    first = True
    for gid, label, aside, rows in INDEX_GROUPS:
        cls = "group__head group__head--first" if first else "group__head"
        first = False
        groups.append(
            '      <div class="%s" id="%s">\n'
            '        <h3 class="mono">%s</h3>\n'
            '        <span class="mono dim-2">%s</span>\n'
            '      </div>' % (cls, gid, label, aside)
        )
        groups += [index_row(*r) for r in rows]

    vcv = [index_row(*r) for r in VCV_ROWS]

    return (
        head("SHLabs — instruments for the modular world",
             """SHLabs is an independent audio-tools studio. Cadence, a performance mixer and master clock, and Phosphor, an audio-reactive video synth, lead a line of VST3 / AU plugins and standalone apps, alongside free and paid modules for VCV Rack 2.""",
             home=True,
             og=("SHLabs — instruments for the modular world",
                 "An independent studio making instruments for the stage, the DAW and VCV Rack."))
        + nav(home=True)
        + """
  <div class="sheet" id="top">

  <!-- ─── hero ───────────────────────────────────────────────────────── -->
  <header class="hero pad" id="main">
    <div class="hero__meta mono">
      <span>Independent audio-tools studio · Switzerland</span>
      <span class="dim-2">Catalogue %d</span>
    </div>

    <h1 class="display">Instruments<br>built to be<br>played.</h1>

    <div class="hero__grid">
      <div class="hero__lead">
        <p class="lead">
          SHLabs builds instruments at the intersection of musical use, real
          computation and unusual control surfaces. A line of VST3 and AU plugins
          and standalone apps, plus modules for
          <a class="link" href="https://vcvrack.com" target="_blank" rel="noopener">VCV Rack 2</a>.
        </p>
      </div>

      <nav class="hero__toc toc" aria-label="Contents">
        <span class="mono dim toc__h">Contents</span>
        <a href="#flagships"><span class="n">01</span><span class="t">Flagships</span><span class="leader"></span><span class="n">2</span></a>
        <a href="#index"><span class="n">02</span><span class="t">Plugins &amp; apps</span><span class="leader"></span><span class="n">11</span></a>
        <a href="#vcv"><span class="n">03</span><span class="t">VCV Rack 2</span><span class="leader"></span><span class="n">6</span></a>
        <a href="#studio"><span class="n">04</span><span class="t">The studio</span><span class="leader"></span><span class="n">3</span></a>
      </nav>
    </div>
  </header>

  <div class="rule--ink"></div>

  <!-- ─── 01 flagships ───────────────────────────────────────────────── -->
  <section class="sec" id="flagships">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">01</span> Flagships</h2>
      <span class="mono dim">Premium · Coming soon</span>
    </div>

    <div class="flag pad">
      <div class="flag__id">
        <span class="mono dim">Performance &amp; live · Standalone</span>
        <h3 class="flag__name"><a href="/cadence/">Cadence</a></h3>
      </div>
      <div class="flag__text">
        <p class="flag__claim">The brain of a hybrid set.</p>
        <p class="body">
          A four-channel performance mixer, master clock and sync hub in one
          standalone app. Beatgrid clip players with quantized launch, automatic
          structure detection, on-device stem separation with quantized stem kills,
          and an assist layer that can carry a transition. A sample-accurate MIDI
          clock keeps your modular, drum machines and grooveboxes following you,
          not the other way round.
        </p>
        <div class="flag__spec mono">
          <span>4-channel mixer</span>
          <span>24-PPQN MIDI clock</span>
          <span>Ableton Link</span>
          <span>OSC broadcast</span>
          <span class="dim-2">macOS · Windows alpha in testing</span>
        </div>
      </div>
    </div>

    <div class="flag pad">
      <div class="flag__id">
        <span class="mono dim">Visuals · VST3 · AU · Standalone</span>
        <h3 class="flag__name"><a href="/phosphor/">Phosphor</a></h3>
      </div>
      <div class="flag__text">
        <p class="flag__claim">A video synth that listens.</p>
        <p class="body">
          A GPU-native visual instrument with five scene families (morphing fields,
          tunnel, fractals, spectrum, ambient) and a hundred-thousand-particle
          system on top. Band envelopes and onset detectors drive the image, and it
          locks to Cadence, to your host playhead or to Ableton Link before going
          fullscreen on the projector.
        </p>
        <div class="flag__spec mono">
          <span>GLSL engine</span>
          <span>36+ presets</span>
          <span>Syphon out</span>
          <span>MIDI learn</span>
          <span class="dim-2">macOS · Windows in CI</span>
        </div>
      </div>
    </div>

    <div class="note pad">
      <div class="note__k mono">The bundle</div>
      <div class="note__v">
        <p class="body">
          The two lock over OSC: Phosphor follows Cadence's clock and beat phase,
          reads master band energy and kick onsets, and surges when the drop lands.
          The bundle is the whole studio, with Cell, Tincture, Contour, Spazio,
          Glue, Stesso and Tonnetz included.
        </p>
        <p class="mono dim-2" style="margin-top:12px"><a class="link" href="/cadence/#bundle">Bundle pricing at release</a></p>
      </div>
    </div>
  </section>

  <div class="rule--ink"></div>

  <!-- ─── 02 the index ───────────────────────────────────────────────── -->
  <section class="sec" id="index">
    <span class="anchor" id="products" aria-hidden="true"></span>
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">02</span> Plugins &amp; apps</h2>
      <span class="mono dim">VST3 · AU · Standalone · macOS &amp; Windows</span>
    </div>

    <div class="index">

%s

      <div class="index__foot mono">
        <span>Eleven titles · one design language</span>
        <span>Soon = pre-release</span>
      </div>
    </div>
  </section>

  <div class="rule--ink"></div>

  <!-- ─── 03 vcv rack ────────────────────────────────────────────────── -->
  <section class="sec" id="vcv">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">03</span> VCV Rack 2</h2>
      <span class="mono dim">Modules · macOS · Windows · Linux</span>
    </div>

    <div class="index">
      <div class="group__head group__head--first">
        <h3 class="mono">Module sets</h3>
        <span class="mono dim-2">All free to download</span>
      </div>

%s

      <div class="index__foot mono">
        <span>Direct download: macOS (Apple Silicon). Windows, Linux &amp; Intel via the VCV Library.</span>
        <span>Community-first</span>
      </div>
    </div>
  </section>

  <div class="rule--ink"></div>

  <!-- ─── 04 studio ──────────────────────────────────────────────────── -->
  <section class="sec" id="studio">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">04</span> The studio</h2>
      <span class="mono dim">What ties them together</span>
    </div>

    <div class="ethos pad">
      <div>
        <span class="mono dim">State</span>
        <h3>Nothing gets lost</h3>
        <p class="body">
          Generative modules are seedable and every plugin recalls its full state.
          Stumble onto a sound you love and dial it back any time. Save it, share
          it, and it plays the same on every machine.
        </p>
      </div>
      <div>
        <span class="mono dim">Interface</span>
        <h3>Built to be played</h3>
        <p class="body">
          Whether it is a panel in the rack or a plugin window in your DAW, the
          interface is a control surface, not decoration. Drag-to-assign
          modulation, MIDI learn, sensible defaults and no telemetry.
        </p>
      </div>
      <div>
        <span class="mono dim">Engine</span>
        <h3>Real under the hood</h3>
        <p class="body">
          The processes are the real thing: analog-modelled circuits, feedback,
          sampling, stochastic motion. Every tool is voiced as an instrument first,
          expressive, surprising, and made to be listened to.
        </p>
      </div>
    </div>

    <div class="strip pad">
      <div class="strip__a">
        <h4>The studio</h4>
        <p class="body">
          An independent audio-tools studio making instruments for the modular
          world and the DAW. One person, one design language, two branches: plugins
          and standalone apps for the stage and the DAW, and open modules for
          VCV Rack 2.
        </p>
      </div>
      <div class="strip__b">
        <span class="mono dim" style="display:block;margin-bottom:12px">Contact</span>
        <div class="stack">
          <a href="mailto:shlabs.contact@gmail.com">shlabs.contact@gmail.com</a>
          <a href="https://github.com/shlabs-audio" rel="noopener">github.com/shlabs-audio</a>
          <a href="/about/">About SHLabs</a>
          <a href="/donate/">Support the studio</a>
        </div>
      </div>
      <div class="strip__c">
        <span class="mono dim" style="display:block;margin-bottom:12px">Formats</span>
        <div class="stack dim">
          <span>VST3 · AU</span>
          <span>Standalone</span>
          <span>VCV Rack 2</span>
        </div>
      </div>
    </div>
  </section>

""" % (YEAR, "\n".join(groups), "\n".join(vcv))
        + footer()
        + tail()
    )


# ═══════════════════════════════════════════════════════════════════════
#  utility pages
# ═══════════════════════════════════════════════════════════════════════

def about_page():
    return (
        head("About — SHLabs",
             """SHLabs is a one-person independent studio near Zurich making instruments for VCV Rack and the DAW: modules, VST3 / AU plugins and standalone apps.""")
        + nav(current="Studio")
        + """
  <div class="sheet">

  <nav class="crumb pad mono" aria-label="Breadcrumb">
    <a href="/">SHLabs</a>
    <span class="sep" aria-hidden="true">/</span>
    <span aria-current="page">The studio</span>
  </nav>

  <header class="psheet pad" id="main">
    <div class="psheet__meta mono">
      <span class="dim">The studio</span>
      <span class="dim-2">Independent · Switzerland</span>
    </div>
    <h1 class="psheet__name">About</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>Instruments for the rack and the DAW.</p></div>
      <div class="psheet__desc">
        <p class="body">
          SHLabs is a small independent studio making music software across
          formats. The catalog started with modules for
          <a class="link" href="https://vcvrack.com" target="_blank" rel="noopener">VCV&nbsp;Rack</a>,
          and is now growing a second branch of DAW-ready plugins — VST3&nbsp;/&nbsp;AU and
          standalone apps that run in Ableton Live, Logic, Bitwig and beyond.
          Whatever the format, the instruments put real processes on the panel —
          modulation and LFOs, sequencers, generative sources, gate logic and
          stochastic motion — drawn from the older tradition of analog computing,
          where a calculation was something physical and visible rather than
          hidden behind function calls.
        </p>
      </div>
    </div>
  </header>

  <div class="rule--ink"></div>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">The catalogue</h2>
      <span class="mono dim-2">Two branches</span>
    </div>
    <div class="cols pad cols--open">
      <div class="cols__k mono">Families</div>
      <div class="cols__v">
        <p class="body">
          On the rack side the catalog is organized into families, each with its
          own character: <strong>Stochast</strong>, <strong>Mashina</strong>,
          <strong>Lucida</strong>, <strong>Rikoshet</strong> and
          <strong>Atmos</strong>. Some are free; others are paid releases that fund
          continued development. On the DAW side, a growing line of synths, effects,
          mastering tools, MIDI brains and visuals shares one design language — the
          same metallic control surfaces, the same instruments-first feel.
        </p>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">How it started</h2>
      <span class="mono dim-2">A founding story</span>
    </div>
    <div class="cols pad cols--open">
      <div class="cols__k mono">In the first person</div>
      <div class="cols__v prose">
        <p>
          SHLabs is a one-person studio. I grew up near Zurich, Switzerland, and
          work as a data scientist — but synthesizers have been a love of mine for
          as long as I can remember, and that fascination eventually led, as it
          tends to, to modular.
        </p>
        <p>
          The tools on this site started years ago as things I built for my own
          needs and my own pleasure: modules and plugins I used in my own jams,
          live shows and music production. Along the way they kept circling a
          simple question — what if the maths that usually disappears inside code
          were laid out as something you could turn, patch, and hear? A sequencer
          here, a generative source there, and the tools kept growing into families.
        </p>
        <p>
          Now I've decided to release them. Expanded, polished and made dependable,
          they're ready to be shared with the world — first with the VCV&nbsp;Rack
          community, and with the plugin line arriving, with anyone working in a DAW.
          The same ideas carry across: whether it's a module you patch or a plugin
          you insert, it should be real under the hood and a pleasure to play. New
          families, plugins and updates are released as they're ready.
        </p>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">Contact</h2>
      <span class="mono dim-2">Get in touch</span>
    </div>
    <div class="blk pad">
      <p class="body">
        Questions about a release, early access to something still in testing, bug
        reports, or whether a particular piece of gear will play nicely with the
        tools here — the studio inbox is open.
      </p>
      <p class="mono dim">shlabs.contact@gmail.com</p>
      <div class="acts">
        <a class="act act--fill" href="mailto:shlabs.contact@gmail.com">Write us</a>
        <a class="act" href="/#index">Browse the catalogue &rarr;</a>
        <a class="act" href="/donate/">Support the studio</a>
      </div>
    </div>
  </section>

"""
        + footer()
        + tail()
    )


def donate_page():
    return (
        head("Support SHLabs",
             """Support SHLabs: sponsor the studio on GitHub, spread the word, or open an issue. Contributions help the next module get built and keep the free modules coming.""")
        + nav()
        + """
  <div class="sheet">

  <nav class="crumb pad mono" aria-label="Breadcrumb">
    <a href="/">SHLabs</a>
    <span class="sep" aria-hidden="true">/</span>
    <span aria-current="page">Support</span>
  </nav>

  <header class="psheet pad" id="main">
    <div class="psheet__meta mono">
      <span class="dim">Support the work</span>
      <span class="dim-2">Optional · always</span>
    </div>
    <h1 class="psheet__name">Support</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>Help the next module get built.</p></div>
      <div class="psheet__desc">
        <p class="body">
          SHLabs is an independent studio, and development time comes out of
          evenings and weekends. If a module has earned a place in your rack or
          just given you the pleasure of patching, a contribution helps the next
          one get written — and keeps the free modules coming.
        </p>
      </div>
    </div>
  </header>

  <div class="rule--ink"></div>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">GitHub Sponsors</h2>
      <span class="mono dim-2">Recurring or one-off</span>
    </div>
    <div class="blk pad">
      <p class="body">
        Sponsor on GitHub for a monthly amount — any value, set by you — or send a
        one-off contribution. Payments are handled by GitHub, so no account beyond
        your existing GitHub one is required. It is the clearest, lowest-friction
        way to support the studio and keep the free modules coming.
      </p>
      <div class="acts">
        <a class="act act--fill" href="https://github.com/sponsors/kevisc" target="_blank" rel="noopener">Sponsor on GitHub &#8599;</a>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">Other ways to help</h2>
      <span class="mono dim-2">Free, and worth more</span>
    </div>
    <div class="spec">
      <span class="row__no">01</span>
      <span class="row__id"><span class="row__cat">Spread the word</span><h3 class="row__name">Tell people about it</h3></span>
      <p class="row__desc">Mention a module in a patch you share, on social media, or to a friend who racks. Word of mouth in the modular community beats any donation in long-run usefulness — and it costs nothing.</p>
    </div>
    <div class="spec">
      <span class="row__no">02</span>
      <span class="row__id"><span class="row__cat">On GitHub</span><h3 class="row__name">Open an issue</h3></span>
      <p class="row__desc">Bug reports, edge cases, and requests for new modules are all welcome on the SHLabs GitHub at <a class="link" href="https://github.com/shlabs-audio" target="_blank" rel="noopener">github.com/shlabs-audio</a>. A clear repro is worth its weight in gold.</p>
    </div>
    <div class="blk pad">
      <div class="acts">
        <a class="act" href="/#index">Browse the catalogue &rarr;</a>
        <a class="act" href="/about/">About the studio</a>
      </div>
    </div>
  </section>

"""
        + footer()
        + tail()
    )


# filename stem -> (label, the page it belongs to or None)
DOWNLOADS = [
    ("SHLabs-Mashina-2.0.0-mac-arm64.vcvplugin", "8 modules", "Mashina", "/mashina/"),
    ("SHLabs-Colony-2.0.0-mac-arm64.vcvplugin", "2 modules · Colony, Turing", "Lucida", "/lucida/"),
    ("SHLabs-Helix-2.0.0-mac-arm64.vcvplugin", "Atmos · transistor-ladder filter", "Helix", "/atmos/"),
    ("SHLabs-Halo-2.0.0-mac-arm64.vcvplugin", "Atmos · stereo colour repeater", "Halo", "/atmos/"),
    ("SHLabs-Skywave-2.0.0-mac-arm64.vcvplugin", "Atmos · character delay &amp; reverb", "Skywave", "/atmos/"),
    ("SHLabs-Metro185-2.0.0-mac-arm64.vcvplugin", "Atmos · eight-stage sequencer", "Metro 185", "/atmos/"),
    ("SHLabs-Atlas-2.0.0-mac-arm64.vcvplugin", "1 module · gestural granular sampler", "Terra", "/terra/"),
    ("SHLabs-Phosphor-2.0.0-mac-arm64.vcvplugin", "3 modules · Beam, Chroma, Cathode", "Phosphor for VCV Rack", None),
]


def downloads_page():
    rows = []
    for i, (fname, cat, label, page) in enumerate(DOWNLOADS, 1):
        path = os.path.join(ROOT, "downloads", fname)
        kb = "%d KB" % round(os.path.getsize(path) / 1024) if os.path.exists(path) else "—"
        detail = ('Product sheet: <a class="link" href="%s">%s</a>. ' % (page, label)) if page else ""
        rows.append(
            '      <a class="row" href="/downloads/%s">\n'
            '        <span class="row__no">%02d</span>\n'
            '        <span class="row__id"><span class="row__cat">%s</span>'
            '<span class="row__name">%s</span></span>\n'
            '        <span class="row__desc">%s<span class="mono">%s</span></span>\n'
            '        <span class="row__status is-free">%s</span>\n'
            '      </a>' % (fname, i, cat, label, detail, fname, kb)
        )
    return (
        head("Downloads — SHLabs",
             """Direct downloads of the free SHLabs VCV Rack 2 plugins for macOS (Apple Silicon). Drop the .vcvplugin file into Rack's user plugin folder and restart.""")
        + nav()
        + """
  <div class="sheet">

  <nav class="crumb pad mono" aria-label="Breadcrumb">
    <a href="/">SHLabs</a>
    <span class="sep" aria-hidden="true">/</span>
    <span aria-current="page">Downloads</span>
  </nav>

  <header class="psheet pad" id="main">
    <div class="psheet__meta mono">
      <span class="dim">VCV Rack 2 plugins</span>
      <span class="is-free">Free</span>
    </div>
    <h1 class="psheet__name">Downloads</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>Every direct download, in one list.</p></div>
      <div class="psheet__desc">
        <p class="body">
          Download a <strong>.vcvplugin</strong> file and drop it into Rack's user
          plugin folder, then restart — the modules appear under the
          <strong>SHLabs</strong> brand. You'll need
          <a class="link" href="https://vcvrack.com/Rack" target="_blank" rel="noopener">VCV&nbsp;Rack&nbsp;2</a>,
          itself a free download.
        </p>
      </div>
    </div>
    <div class="psheet__spec mono"><span>macOS (Apple Silicon)</span><span>Windows, Linux &amp; Intel via the VCV Library</span></div>
  </header>

  <div class="rule--ink"></div>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">Direct downloads</h2>
      <span class="mono dim-2">Version 2.0.0</span>
    </div>
    <div class="index">

%s

      <div class="index__foot mono">
        <span>Stochast and Rikoshet are distributed from GitHub releases.</span>
        <span>GPL-3.0 and freeware</span>
      </div>
    </div>
  </section>

""" % "\n".join(rows)
        + footer()
        + tail()
    )


def notfound_page():
    return (
        head("Not found — SHLabs", "", robots="noindex", og=(None, None))
        + nav()
        + """
  <div class="sheet">
  <main class="mid pad" id="main">
    <div class="hero__meta mono">
      <span class="dim">Error 404</span>
      <span class="dim-2">Page not found</span>
    </div>
    <h1 class="display">404</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>No module patches to that input.</p></div>
      <div class="psheet__desc">
        <p class="body">
          The page you asked for is not on this sheet. The full catalogue —
          plugins, standalone apps and VCV Rack modules — is one link away.
        </p>
        <div class="acts" style="margin-top:26px">
          <a class="act act--fill" href="/">Back to SHLabs</a>
          <a class="act" href="/#index">Browse the index &rarr;</a>
        </div>
      </div>
    </div>
  </main>

"""
        + footer()
        + tail()
    )


def empiria_page():
    """A redirect stub. The canonical page is /stochast/; the visible copy is
    only ever seen if the refresh and the script are both blocked."""
    return (
        head("Empiria → Stochast — SHLabs", "", robots="noindex",
             canonical="https://shlabs.ch/stochast/", refresh="0; url=/stochast/",
             og=(None, None))
        + nav()
        + """
  <div class="sheet">
  <main class="mid pad" id="main">
    <div class="hero__meta mono">
      <span class="dim">Renamed</span>
      <span class="dim-2">Redirecting</span>
    </div>
    <h1 class="display">Stochast</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>The VCV Rack suite has been renamed.</p></div>
      <div class="psheet__desc">
        <p class="body">
          The VCV Rack suite has been renamed to
          <a class="link" href="/stochast/">Stochast</a>. Redirecting…
        </p>
        <div class="acts" style="margin-top:26px">
          <a class="act act--fill" href="/stochast/">Go to Stochast &rarr;</a>
        </div>
      </div>
    </div>
  </main>

"""
        + footer()
        + '</div>\n  <script>location.replace("/stochast/");</script>\n</body>\n</html>\n'
    )


# ═══════════════════════════════════════════════════════════════════════
#  main
# ═══════════════════════════════════════════════════════════════════════

def main():
    if not os.path.isfile(os.path.join(ROOT, "css", "shlabs.css")):
        sys.exit("error: run this from inside the shlabs repo (css/shlabs.css not found)")

    print("SHLabs — regenerating pages into %s" % ROOT)
    write("index.html", homepage())
    write("404.html", notfound_page())
    write("about/index.html", about_page())
    write("donate/index.html", donate_page())
    write("downloads/index.html", downloads_page())
    write("empiria/index.html", empiria_page())
    for slug, p in PRODUCTS.items():
        write("%s/index.html" % slug, product_page(p))
    print("done — %d pages" % (6 + len(PRODUCTS)))


if __name__ == "__main__":
    main()
