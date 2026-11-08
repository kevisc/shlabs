#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pages.py: regenerate every HTML page of shlabs.ch in the "Index"
design system (see css/shlabs.css).

    HOW TO RE-RUN
    -------------
        cd <repo root>
        python3 tools/gen_pages.py

    It rewrites, from the data in this file and nothing else:

        index.html   404.html
        about/  donate/  downloads/  empiria/
        cadence/  kinora/  cell/  schlagzeugs/  contour/  spazio/  lacuna/
        legato/  stesso/  tonnetz/  metro185/   (glue/ redirects to legato/)
        stochast/  mashina/  lucida/  rikoshet/  atmos/  terra/
        gsw/  gsw/cadence/  gsw/kinora/   (Schwiizerdütsch, see gsw_home())
        phosphor/  gsw/phosphor/   (redirects: Kinora was called Phosphor)

    It never touches: cadence/manual/ (the product manual deliberately
    matches the app's own look, not the site), CNAME, img/, README.md,
    css/shlabs.css, js/shlabs.js.

    All copy lives in the data structures below. Edit it here, re-run, and
    commit this file together with the regenerated HTML. The nav and the
    footer are defined exactly once (NAV_LINKS / FOOTER_COLS), so every
    page stays in sync and internal links cannot drift apart.

    Voice rules for all copy in this file
    -------------------------------------
    * Humble, specific and technical. State what a tool is, what it does
      and what it lets the user do. Give the numbers.
    * Plain standard technical English. Short sentences, one idea each,
      active voice, present tense. Direct, never sarcastic or abstract.
    * No slogans, metaphors or superlatives (premium, lush, brain, alive,
      state-of-the-art). No claims about other products. No "not X but Y".
    * No em dashes. Page titles use " · SHLabs". Keep control names as the
      app shows them. Mark what is in beta or planned as such.

    Design rules this file encodes
    ------------------------------
    * Amber is the only accent, used for status and interaction only.
      There are no per-product accent colours any more.
    * The homepage index rows are real <a> elements; they are the only
      thing on the site that inverts to ink on hover. A product sheet's
      specification rows use the same ruled geometry but never invert,
      because they are facts, not links.
    * Product sheets carry no logo art: the old app-icon PNGs are built
      for a dark UI. Real screenshots appear as "plates": a single 1px ink
      hairline, no shadow, no gradient, mono caption underneath.
    * Only /cadence/ loads JavaScript, and only for the view explorer: the
      tab row over the Cadence screenshots. With no script it degrades to
      those plates stacked in flow, each with its own note.
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
    ("GitHub", GITHUB, "is-accent nav-hide-sm"),
]

FOOTER_COLS = [
    ("Flagships", [
        ("Cadence", "/cadence/"),
        ("Kinora", "/kinora/"),
    ]),
    ("Instruments &amp; effects", [
        ("Cell", "/cell/"),
        ("Schlagzeugs", "/schlagzeugs/"),
        ("Contour", "/contour/"),
        ("Spazio", "/spazio/"),
    ]),
    ("Mastering &amp; MIDI", [
        ("Legato", "/legato/"),
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
        ("Schwiizerdütsch", "/gsw/"),
    ]),
]

SWISS = (
    '<svg width="12" height="12" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
    '<rect width="32" height="32" fill="#d52b1e"/>'
    '<rect x="13" y="6" width="6" height="20" fill="#fff"/>'
    '<rect x="6" y="13" width="20" height="6" fill="#fff"/></svg>'
)

LANG_FLAG = SWISS.replace('<svg width="12" height="12"', '<svg class="lang__flag" width="9" height="9"')


def lang_switch(here, href):
    """The EN | CH switch at the end of the nav. `here` is the page's own
    language ("en" or "gsw"). The switch links to the same page in the other
    language, or to the Swiss German home when there is no such page."""
    to, label = ("gsw", "Schwiizerdütsch") if here == "en" else ("en", "English")
    en = "lang__seg is-on" if here == "en" else "lang__seg"
    ch = "lang__seg is-on" if here == "gsw" else "lang__seg"
    return ('      <a class="lang" href="%s" hreflang="%s" lang="%s" title="%s" aria-label="%s">'
            '<span class="%s" aria-hidden="true">EN</span>'
            '<span class="%s" aria-hidden="true">%sCH</span></a>\n'
            % (href, to, to, label, label, en, ch, LANG_FLAG))


def head(title, desc, *, home=False, robots=None, canonical=None, refresh=None,
         script=False, og=None, lang="en"):
    """The <head> block. og defaults to the page title/description."""
    og_title, og_desc = og or (title, desc)
    L = [
        "<!doctype html>",
        '<html lang="%s">' % lang,
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


def nav(home=False, current=None, gsw="/gsw/"):
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
        '      <div class="nav__links mono">\n%s\n%s      </div>\n'
        '    </div>\n'
        '  </nav>\n' % ("#top" if home else "/", "\n".join(out), lang_switch("en", gsw))
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
        '      <span>&copy; %d SHLabs &middot; Software for music and visuals</span>\n'
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
        elif kind == "frames":
            # A grid of engine frames, each labelled with its preset and scene.
            flush()
            _, frames, cap = part
            cells = "\n".join(
                '        <div class="frame">\n'
                '          <div class="plate"><img src="%s" alt="%s, a frame from the %s scene" '
                'width="%d" height="%d" loading="lazy"></div>\n'
                '          <p class="frame__cap mono"><span>%s</span><span class="dim-2">%s</span></p>\n'
                '        </div>' % (src, name, scene, w, h, name, scene)
                for src, name, scene, w, h in frames)
            out.append(
                '    <div class="band band--tight pad">\n'
                '      <figure class="fig">\n'
                '        <div class="frames">\n%s\n        </div>\n'
                '        <figcaption class="mono">%s</figcaption>\n'
                '      </figure>\n'
                '    </div>' % (cells, cap))
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


GSW_TWIN = {"Cadence": "/gsw/cadence/", "Kinora": "/gsw/kinora/"}


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
        + nav(gsw=GSW_TWIN.get(p["name"], "/gsw/"))
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
             """an early look. Pricing and availability will be announced at release.""")

VCV_NEED = ("""You need <strong>VCV Rack 2</strong>, a free download for macOS, Windows """
            """and Linux from <a class="link" href="https://vcvrack.com/Rack" target="_blank" """
            """rel="noopener">vcvrack.com/Rack</a>.""")

VCV_MAC = "macOS (Apple Silicon). Windows, Linux &amp; Intel builds are planned through the VCV Library."

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
    "title": "Cadence · SHLabs",
    "desc": """Cadence is a four-channel performance mixer and master clock for hardware, files and live inputs. It has a sample-accurate 24-PPQN MIDI clock, beatgrid players, automatic structure analysis, on-device stem separation, a Composer timeline with a piano roll, MIDI and audio take recording, and an OSC broadcast. Standalone app for macOS and Windows. Coming soon.""",
    "crumb": ("Performance &amp; live", "/#cat-live"),
    "cat": "Performance mixer &amp; master clock",
    "status": "Coming soon",
    "soon": True,
    "claim": "A four-channel performance mixer and master clock.",
    "lead": """Each channel takes a live input or a beatgrid player. A sample-accurate MIDI clock drives your hardware. Assist can hold the mix while you play. A part you play on a keyboard or a hardware synth records back onto its channel as a loop.""",
    "spec": ["Standalone app", "macOS and Windows, beta in testing"],
    # No hero plate: the Perform shot that used to sit here is the first view
    # of the explorer below, and one screenshot on a sheet twice is one too
    # many. The explorer opens the page in its place.
    "script": True,
    "sections": [
        {"parts": [
            ("head", "Inside Cadence", "Four views, one surface"),
            # PERFORM / COMPOSER / SAMPLER, in the app's own order, which is
            # also the order of the number keys that switch them. The app's
            # fourth view, COLLECTION, is described in the paragraph under the
            # explorer instead of shown: the whole subject of that shot is the
            # track table, and the licensed titles in it have to be blurred,
            # which leaves the widest column a ladder of grey beside crisp BPM
            # and key columns.
            # Every claim below is checked against the app: docs/manual/index.html
            # and TESTERS.md in the hybrid-mixer repo, and the view sources.
            ("explore", "Cadence views", [
                ("perform", "Perform",
                 "/img/shots/cadence.jpg",
                 "The Perform view: four mixer strips with faders and meters at the centre, a deck waveform either side of them, and the collection docked below",
                 2360, 1864,
                 """Perform is the mixer. It has four strips under one master section. Each strip runs a live input or a deck from your collection.""",
                 ["3-band EQ with full kill", "Filter per channel",
                  "Pre-fader cue bus", "Stem chips per deck", "REC chip per deck"]),
                ("composer", "Composer",
                 "/img/shots/cadence-arrange.jpg",
                 "The Composer view: four channel lanes carrying audio clips and MIDI blocks on a numbered bar timeline, with automation curves under the lanes and a toolbar of clip and automation tools above them",
                 2360, 1864,
                 """Composer is a bar timeline for laying out a set in advance. It has one lane per channel, with audio clips and MIDI blocks on the lanes and automation drawn underneath. Its own PLAY runs the arrangement.""",
                 ["Whole set to sixteenth-note zoom", "Piano roll with marquee editing",
                  "Vol / filt / dly / verb / OSC / macro and stem lanes",
                  "Saved as a Composition"]),
                ("sampler", "Sampler",
                 "/img/shots/cadence-sampler.jpg",
                 "The Sampler view: a zoomed waveform with a beatgrid-snapped selection highlighted, under the save, monitor and strip controls",
                 2360, 1864,
                 """Sampler is a non-destructive editor for cutting regions out of tracks. Select on the beatgrid and audition through the Sampler's own voice. Then save the piece, or collect regions into a strip and render them as one crossfaded clip.""",
                 ["Beatgrid-snapped selection", "Its own preview voice, no deck borrowed",
                  "Cue and main are independent", "24-bit WAV, equal-power joins"]),
            ]),
            ("body", """The fourth view is the Collection, the library you load from. A scan reads the tempo, a bar-accurate beatgrid, the musical key and the loudness that auto-gain uses. The table then shows a waveform, BPM, key, genre, length, grid confidence and stems status for every track. Search filters as you type, on a word, a key or a BPM range. While a deck plays, tracks in a compatible key tint green. LOAD 1 to 4 above the table put the selected track on a channel. Each button shows that channel's live level, so you can see which decks are playing. Music comes in through Add Files, or through Import XML for a rekordbox collection with its playlists, beatgrids and hot cues."""),
        ]},
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("One surface", "One surface for the whole set",
                 """Live inputs, prepared clips and hardware share the same four channels. Cadence holds the tempo, the grid and the structure of the set in one place."""),
                ("One clock", "Cadence is the master clock",
                 """A sample-accurate 24-PPQN MIDI clock, phase-locked to the audio clock and not driven by a timer. It sends transport start and stop and has tap tempo. Your hardware follows Cadence, so the rig has one clock."""),
                ("Assist", "Play hardware on top",
                 """Assist can carry a transition on its own. It is key-aware, its pacing is adjustable, and it can loop the build into the drop. That leaves both hands free for the modular, the drum machine or the synth. You can take the mix back at any point."""),
            ]),
        ]},
        {"parts": [
            ("head", "Capabilities", ""),
            ("rows", [
                ("Mixer", "Four channels, DJ layout",
                 """Each channel takes a live input or its own internal player. It has a three-band EQ with full kills and one HP/LP filter knob. A pre-fader cue bus has selectable master and cue output routing. Master metering is included. Each strip also has a delay and a send to a shared reverb."""),
                ("Clock &amp; sync", "Hardware locked to the grid",
                 """24-PPQN MIDI clock out, sample-accurate and phase-locked to audio, with transport start and stop. It drives eurorack, Elektron boxes and drum machines. Use tap tempo for anything unclocked. An OSC broadcast sends beat, phase and tempo to software on the network."""),
                ("Players", "Beatgrid clips",
                 """Quantized bar launch, warp and vari-speed sync to the master tempo, a flexible grid with key-lock, eight hot cues and cue preview from the browser. Waveform lanes show phase and sync against the beatgrid, so you can see whether two decks line up."""),
                ("Composer", "A set laid out in advance",
                 """A bar timeline with one lane per channel: full-length clips, MIDI blocks and hand-drawn automation, under its own PLAY. Zoom runs from a whole set on one screen down to a sixteenth note. The piano roll selects and edits notes in bulk, and it lights the rows of the key the app has resolved. A layout saves and reloads as a Composition."""),
                ("Analysis", "Beatgrid and structure",
                 """Automatic beatgrid and structure detection marks intro, break, drop and outro. Auto-sections snap to bars. Analysis also gives mood descriptors and clip-safe gain. The library stores the results, so a track needs preparing only once."""),
                ("Assist", "An auto-DJ layer you steer",
                 """Key-aware transition modes, adjustable pacing, a build-up loop into the drop and FX ramps. When tracks are separated, transitions use the stems: bass swaps and vocal handovers instead of EQ moves alone. You can take the mix back during a transition without a jump in level."""),
                ("Control", "Mapped to your gear",
                 """MIDI-learn on every control, with A/B bank switching so a small controller can reach the whole surface. A phone remote joins over the local network by QR code. OSC broadcasts clock phase, beat, BPM and transport, with master band energy, kick onsets, per-stem levels and a drop-aware intensity signal."""),
                ("The look", "Two surfaces, one switch",
                 """Cadence starts in the Index look: this site's design language in dark form, square and ruled, with type set by role. Classic, the earlier surface, is still a setting. The switch is instant and does not interrupt the mix."""),
            ]),
        ]},
        {"parts": [
            ("head", "Stems", "Drums · Bass · Other · Vocals"),
            ("lead", """Cadence separates a track into four parts on your machine, with no cloud and no upload. You can then kill a vocal, keep the drums under the next track or solo a bassline. Assist can swap the basslines of two tracks instead of trading EQ bands."""),
            ("rows", [
                ("Separate", "Four parts, on your machine",
                 """One right-click separates a track into drums, bass, other and vocals. A neural model (htdemucs) runs locally. A club track takes about forty seconds on Apple Silicon. Results stay in the library cache, so each track is separated once."""),
                ("Perform", "Kills quantized to the bar",
                 """Each stemmed deck shows four mute chips and a solo per part, all quantized to the grid. A queued kill blinks until the bar line and then takes effect. Shift-click for an instant kill. Key-lock holds pitch, and every chip is MIDI-learnable."""),
                ("Assist + stems", "Assist mixes with the parts",
                 """Transitions use the stems when they exist. Bass swaps exchange the two basslines on the swap bar. The incoming vocal waits until the outgoing vocal has ended. With both tracks separated, Assist hands over the drums first, then the bass."""),
            ]),
        ]},
        {"parts": [
            ("head", "Recording", "The mix · MIDI takes · audio takes"),
            ("lead", """Cadence records the mix it sends out. It also records into itself: a part played on a keyboard or a hardware synth is captured on its channel and loops there."""),
            ("rows", [
                ("The take", "Count in, play, loop",
                 """Arm a channel and the count-in starts on the next bar line, so the loop stays in phase with the grid. The click is audible during the count. The recording stops at the loop length you chose, and the loop starts at once in the phase you played it. One shared menu sets loop length and count-in bars for every kind of take."""),
                ("MIDI", "Three places to record into",
                 """Record a MIDI device onto a Perform channel, onto a Composer lane, or into the clip open in the note editor. Quantize is a sensitivity control. It moves note starts and leaves your durations as played. Snap to key moves an off-key note to the nearest note in the resolved key. It does nothing when no key resolves."""),
                ("Audio", "Hardware synths on the grid",
                 """Record a hardware synth on a live input, or a hosted instrument, as a looping clip on the channel or as a clip in a composition. The tap sits after the sound source and before the EQ, the filter and the sends, so you can still shape the loop afterwards. The take is latency-compensated, with a manual trim for interfaces that report latency wrongly. It is placed on the master grid directly and does not go through beat detection."""),
                ("The mix", "The master output",
                 """The master button records the master bus, after the compressor and the limiter, as a 24-bit WAV. It runs independently of the channel takes, so you can record the set and a loop on channel 3 at the same time."""),
            ]),
        ]},
        {"slab": True, "id": "bundle", "parts": [
            ("head", "The bundle", "Ten products"),
            ("h3", "Cadence and Kinora work together"),
            ("lead", """Cadence sends live data to Kinora over OSC. Kinora uses that data to drive the picture, so the visuals follow the set while you keep mixing. Both apps do this today."""),
            ("rows", [
                ("Cadence sends", "Clock, structure, energy",
                 """Beat and clock phase, BPM and transport, master band energy across bass, mid and high, kick onsets, and a drop-aware intensity signal. When a deck plays separated stems, it also sends per-stem levels and drum-stem onsets. The broadcast runs continuously while you play."""),
                ("So Kinora can", "Keep visuals on the same grid",
                 """Lock scene motion to beat phase. Follow the bands with reactive parameters. Fire shockwave ripples on kick onsets. Raise the image into each drop. Output runs fullscreen on a projector."""),
            ]),
            ("body", """The bundle also includes <a class="link" href="/cell/">Cell</a>, <a class="link" href="/schlagzeugs/">Schlagzeugs</a>, <a class="link" href="/contour/">Contour</a>, <a class="link" href="/spazio/">Spazio</a>, <a class="link" href="/lacuna/">Lacuna</a>, <a class="link" href="/legato/">Legato</a>, <a class="link" href="/stesso/">Stesso</a> and <a class="link" href="/tonnetz/">Tonnetz</a>. That is every instrument, effect and mastering tool in the line."""),
            ("body", """Schlagzeugs plays Cadence's drum clips directly. The Beats assist writes a drum clip on the General MIDI drum map, which is the default map in Schlagzeugs."""),
            ("body", """Lacuna follows Cadence's key. With Follow on, its six resonances retune to the key of the deck Cadence plays, in any host on the same computer."""),
            ("body", """A Tonnetz link is planned for the bundle. Cadence would follow and steer harmony through note-follow over OSC."""),
            ("mono", "Bundle pricing announced at release."),
            ("acts", [("/kinora/", "Kinora &rarr;", ""),
                      ("/tonnetz/", "Tonnetz &rarr;", ""),
                      ALL_PRODUCTS]),
        ]},
        {"parts": [
            ("head", "Influences", ""),
            ("body", """Cadence's workflow owes a debt to deadmau5's Autopilot. Its DAW-style set preparation and hybrid performance approach raised a question for us: how much of a set can you prepare before it stops being a performance?"""),
            ("body", """Cadence differs in three ways. It is built around hardware, with a sample-accurate MIDI clock for your modular and drum machines. It broadcasts clock, structure and energy over OSC, so a paired video synth can follow the set. And every control maps to the gear you already own."""),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Cadence is a paid SHLabs app in active development. This page is an early look."""),
            ("body", """The macOS and Windows builds are in beta testing. Pricing and availability will be announced at release. For early access, or to ask whether Cadence can clock a specific device, write to us."""),
            ("acts", [(MAIL, "Write us", "fill"), ALL_PRODUCTS]),
        ]},
    ],
}

# ─── Kinora (called Phosphor until November 2026) ───────────────────────────
PRODUCTS["kinora"] = {
    "name": "Kinora",
    "title": "Kinora · SHLabs",
    "desc": """Kinora, formerly Phosphor, is a GPU-based audio-reactive video synthesiser: thirty-two scenes, a 100k particle system, band envelopes and onset detection, Syphon output and recording. It locks to Cadence over OSC, to the host playhead, or to the beat it finds in the audio. On a Mac it can capture whatever is playing. VST3 / AU / Standalone. Coming soon.""",
    "crumb": ("Visuals", "/#cat-visuals"),
    "cat": "Audio-reactive video synth",
    "status": "Coming soon",
    "soon": True,
    "claim": "An audio-reactive video synthesiser. Until November 2026 it was called Phosphor. The Kinora was a home moving-picture viewer, made from 1896 to 1914.",
    "lead": """A GLSL engine on the GPU, with thirty-two scenes and a particle system of 100,000 points. Band envelopes and onset detection drive the image. It locks to your clock or to the beat it finds in the audio. Output goes fullscreen to a projector or floats over the music you play. When inserted on a track, it passes the audio through unchanged.""",
    "spec": ["VST3 · AU · Standalone", "macOS"],
    "shot": ("/img/shots/phosphor-live.jpg",
             "The window in LIVE mode, with the Night Drive 85 preset. A development build from before the rename, so the header still reads PHOSPHOR",
             1920, 1230),
    "sections": [
        {"parts": [
            ("head", "What it does", ""),
            ("rows", [
                ("Scene engine", "Thirty-two scenes",
                 """Everything renders on the GPU in GLSL. <strong>Fields</strong> holds more than twelve morphable patterns. <strong>Fractal</strong> runs Julia, Mandelbrot and Burning Ship. <strong>Spectrum</strong> and <strong>Waveform</strong> draw the audio itself from an FFT and an oscilloscope. Other scenes include a tunnel flythrough, a retro horizon, flowers, jellyfish, 3D pipes, chrome, mazes and datamosh. Press G to open the scene gallery."""),
                ("Particles", "100,000 points",
                 """A GPGPU particle system with more than 100,000 points, trails and reflections. The simulation runs entirely on the graphics card."""),
                ("Reactivity", "Bands and onsets",
                 """Separate envelopes for overall level and for bass, mid and high. Onset detectors for kick, snare and hat. Spectral centroid tilts the colour with the brightness of the sound. One master REACT control sets the overall response."""),
                ("Sync", "Clock sources",
                 """Lock to <a class="link" href="/cadence/">Cadence</a> over OSC and follow beat, phase, BPM, transport, band energy, onsets and drop intensity. Use the host playhead inside a DAW. Or let Kinora find the beat in the audio, for a stream or a record with no clock."""),
                ("Just listen", "A visualiser for the music you play",
                 """On a Mac, Kinora captures what any app plays, such as Spotify, Apple Music or a browser, with no cable and no loopback driver. A hands-free director runs over it. Kinora asks the player what is playing, so a new track changes the scene and the album art sets the palette. You can float it over the player, with click-through if you want, or set it as a live desktop wallpaper with a menu bar icon. A flash limiter keeps the picture under three flashes a second. The controls fade when the mouse rests."""),
                ("Performance", "For live use",
                 """Fullscreen output to a second display or projector. <strong>Evolve</strong> gives hands-free generative drift. <strong>Auto</strong> moves between presets, and <strong>Flow</strong> morphs between them: cut, smooth or slow. 138 factory presets and 15 colour palettes, layered dual-engine blending, a video-clip layer with reactive blending, and shockwave ripples on the kick."""),
                ("I/O &amp; control", "Outputs and remote control",
                 """Syphon output on macOS feeds VJ software or a media server. H.264 recording and PNG snapshots capture the output. MIDI-learn covers every control, and a phone remote joins over the local network by QR code."""),
            ]),
            ("mono", """VST3 &middot; AU &middot; Standalone. macOS now. A Windows build is in CI with the visuals and reactivity. Syphon and recording stay macOS-only."""),
        ]},
        {"parts": [
            ("head", "Engine output", "Two of the 138 presets"),
            ("frames", [
                ("/img/phosphor/lotus.jpg", "Lotus", "Bloom", 1280, 720),
                ("/img/phosphor/chrome-studio.jpg", "Chrome Studio", "Chrome", 1280, 720),
            ], "Frames rendered by the Kinora engine at 1280 &times; 720. Each label gives the preset, then its scene."),
        ]},
        {"slab": True, "id": "bundle", "parts": [
            ("head", "The bundle", "Bundle pricing at release"),
            ("h3", "Kinora locks to Cadence"),
            ("body", """Cadence broadcasts clock phase, beat, BPM, transport, master band energy, kick onsets and a drop-aware intensity signal over OSC. Kinora uses them to put motion on the beat, move parameters with the bands, react to the kick and raise the image into the drop. The bundle also includes the plugin line: Cell, Schlagzeugs, Contour, Spazio, Lacuna, Legato, Stesso and Tonnetz."""),
            ("acts", [("/cadence/#bundle", "See the bundle &rarr;", "")]),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Kinora is a paid, closed-source SHLabs app in active development."""),
            ("body", """This page is an early look. Pricing and availability will be announced at release. For early access, or to ask about a specific host, projector or media server, write to us."""),
            ("acts", [(MAIL, "Write us", "fill"), ALL_PRODUCTS]),
        ]},
    ],
}

# ─── Cell ─────────────────────────────────────────────────────────────
PRODUCTS["cell"] = vst(
    name="Cell",
    title="Cell · SHLabs",
    desc="""Cell is a subtractive synthesizer with a low CPU load: two band-limited oscillators, sub and noise into one state-variable filter, with envelopes, an LFO, a compact mod matrix and an FX rack that bypasses when off. VST3 / AU / Standalone.""",
    crumb=("Synthesizers &amp; instruments", "/#cat-synths"),
    cat="Subtractive synthesizer",
    claim="""A subtractive synthesizer with a low CPU load.""",
    lead="""Two band-limited oscillators, a sub and noise feed one state-variable filter. Filter and amp envelopes, an LFO and a compact modulation matrix shape the voice. It uses about one percent of a CPU core for eight voices.""",
    shot=("/img/shots/cell.jpg", "The Cell plugin interface", 1280, 843),
    rows=[
        ("The voice", "Two oscillators, sub and noise",
         """Two independent oscillators, each with saw, pulse with PWM, triangle or sine. A sub one or two octaves down and a white-noise source join them in one signal path."""),
        ("The filter", "One state-variable filter",
         """A state-variable filter after Andy Simper, with cutoff, resonance and key-tracking. It is stable at every setting. It has its own envelope and amount control."""),
        ("Envelopes &amp; LFO", "Two envelopes, one LFO",
         """A filter ADSR, an amp ADSR and one LFO."""),
        ("Mod matrix", "A compact modulation matrix",
         """Four assignable slots route Filter Env, Amp Env, LFO, Velocity, Mod Wheel, Key Track or Aftertouch to cutoff, resonance, pitch, PWM, oscillator level, pan and LFO rate."""),
        ("FX rack", "Built-in effects",
         """Drive, chorus, ping-pong delay and reverb. The rack bypasses itself completely when off, so a dry Cell uses no extra CPU for effects."""),
        ("CPU load", "One on every track",
         """Band-limited PolyBLEP oscillators and control-rate modulation keep the load at about one percent of a CPU core for eight voices. You can run one on every track. Thirty presets are included."""),
    ],
)

# ─── Schlagzeugs ──────────────────────────────────────────────────────
PRODUCTS["schlagzeugs"] = vst(
    name="Schlagzeugs",
    title="Schlagzeugs · SHLabs",
    desc="""Schlagzeugs is a generative drum machine and MIDI source: six lanes of DFAM-style step sequencing with Labyrinth-style registers that mutate and lock, polymeter and polyrhythm per lane, and six voices: an analog-style kick, a snare that morphs into a clap, an 808 hat cluster and two Rings-style modal resonators. Every lane also sends MIDI. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Synthesizers &amp; instruments", "/#cat-synths"),
    cat="Generative drum machine",
    claim="""A six-lane generative drum machine and MIDI source.""",
    lead="""Six lanes, each a clocked sequencer with its own length and rate, so polymeter and polyrhythm are the default. The step registers mutate at a rate you set and freeze on command. Six voices play the result. Every lane also sends a MIDI note, so the same pattern can drive a Syntakt, a Cycles or a eurorack drum module.""",
    shot=("/img/shots/schlagzeugs.jpg", "The Schlagzeugs plugin interface", 2364, 1376),
    rows=[
        ("Registers", "Patterns that mutate and lock",
         """Each lane's steps are a Labyrinth-style register. CORRUPT mutates them once per cycle. DENSITY decides what a mutated step becomes. LOCK freezes every register, and ROLL redraws them all from a seed. The kick's downbeat is never mutated."""),
        ("Polymeter", "Six lengths, six rates",
         """Lane lengths from 1 to 32 steps, and rates from quarter notes to 1/16 triplets. One POLYMETER control moves the six lengths toward a coprime set, so the lanes drift out of phase and back over a long cycle."""),
        ("Steps", "DFAM rows, per step",
         """Gate, velocity, pitch, probability and ratchets on every step, plus two modulation rows that reach the voice: one for tune, one for decay or tone. Euclidean fills per lane, with swing and humanize for the whole kit."""),
        ("Voices", "Six voices in one kit",
         """An analog-style kick with a pitch envelope and FM click. A snare that morphs into a clap. Closed and open hats from a six-oscillator 808 cluster, where the closed hat chokes the open one. A tom and a metal percussion voice on Rings-style modal resonators, with ratios that morph from membrane to metal."""),
        ("MIDI", "An instrument and a sequencer",
         """Every lane sends a note on its own number and channel, on the General MIDI drum map by default. A note in on a lane's number plays that voice, so a drum clip from Cadence's Beats assist or from any DAW plays the kit."""),
        ("Clock", "Host or free-running",
         """Follows the host transport sample-accurately, or runs at its own tempo in the standalone. The engine is deterministic per seed and split-invariant, so a pattern sounds the same live and bounced."""),
    ],
)

# ─── Contour ──────────────────────────────────────────────────────────
PRODUCTS["contour"] = vst(
    name="Contour",
    title="Contour · SHLabs",
    desc="""Contour is a multi-LFO modulation rack with a draggable curve editor, tempo sync, multiband routing and MIDI output. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Effects", "/#cat-effects"),
    cat="Multi-LFO modulation rack",
    claim="""A modulation rack with a draggable curve editor.""",
    lead="""Draw the shape of your modulation, lock it to the beat and route it to a target. Four independent curve-LFOs, tempo-synced or free, shape volume, pan and a built-in filter. Use it for sidechain pumping, trance gates, auto-pan and rhythmic filter moves.""",
    shot=("/img/shots/contour.jpg", "The Contour plugin interface", 1280, 1137),
    rows=[
        ("Curve editor", "Draw your modulation",
         """A multi-point curve with bendable segments. Drag points, set the tension and snap to the grid. A library of starter shapes includes sidechain pump, trance gates, stairs, pluck and sample &amp; hold."""),
        ("Four LFOs", "A modulation rack",
         """Four independent curve-LFOs, each routable to volume, pan, filter cutoff or resonance. Stack them on one target or spread them across several. Each LFO has depth, smoothing, phase, swing, invert and stereo offset."""),
        ("Timing", "Sync, free or triggered",
         """Tempo-sync to bar fractions, including dotted and triplet. Run free in Hz. Retrigger from MIDI notes, or follow the audio with an envelope trigger for transient-locked ducking."""),
        ("Multiband", "Per-band modulation",
         """Split the signal into two or three bands and route each LFO to a band. You can duck only the lows under the kick, or auto-pan a single band. Crossovers are phase-correct, with adjustable split points."""),
        ("MIDI out", "Curves as MIDI CC",
         """Each LFO can stream as a MIDI CC, so a drawn curve can control hardware and other instruments."""),
        ("Workflow", "Interface",
         """A resizable interface shows the input waveform behind the curve, so you can line modulation up with transients. Undo and redo cover every move. A preset browser holds your own shapes and patches."""),
    ],
)

# ─── Spazio ───────────────────────────────────────────────────────────
PRODUCTS["spazio"] = vst(
    name="Spazio",
    title="Spazio · SHLabs",
    desc="""Spazio is a combined delay and reverb. One CONTINUUM control moves from a studio delay to a hall, through diffused settings in between. It has tempo-synced echoes, an 8-line modulated reverb network, freeze, ducking and a live decay-profile display. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Effects", "/#cat-effects"),
    cat="Reverb and delay continuum",
    claim="""One engine from delay to reverb.""",
    lead="""A studio delay at one end and a modulated reverb at the other. One CONTINUUM control moves between them. In the middle, repeats diffuse into reverb tails. Every parameter underneath stays adjustable.""",
    shot=("/img/shots/spazio.jpg", "The Spazio plugin interface", 1280, 813),
    rows=[
        ("Continuum", "Delay to hall on one control",
         """CONTINUUM morphs the whole engine: pure repeats on the left, pure reverb on the right. In the middle, the echoes feed the reverb network, so every repeat gets a tail. The morph is equal-power, smoothed and automatable."""),
        ("Echo", "A studio delay",
         """Tempo-synced with sixteen divisions, including dotted and triplet, or free-running with per-channel times. Ping-pong cross-feed. Feedback past 100%, limited by a saturation stage in the loop. Loop filters darken each pass. Wow-style modulation runs from light chorus to tape wobble."""),
        ("Smear", "Diffusion in the delay loop",
         """A diffuser inside the feedback loop blurs repeats a little more on every pass. At zero, a slapback stays clean. At the top of the range, repeats become dense washes."""),
        ("Space", "A modulated reverb",
         """An eight-line modulated reverb network with two-band decay, so the lows can ring longer or shorter than the mids. High-frequency damping, size from plate to large hall, decay from 0.1 to 60 seconds, and a lossless FREEZE that holds the sound indefinitely."""),
        ("Decay profile", "A view of the impulse response",
         """The display shows the actual impulse response of the current settings: tap spikes, diffusion and tail. It recomputes as you turn knobs, using the engine itself."""),
        ("Control", "Mix controls",
         """Program-dependent ducking lowers the effect while the source plays. Width runs from mono to extra-wide. A tilt tone darkens or opens the wet path. Thirty-six parameters, zero latency, click-free time glides (crossfade or tape repitch), and factory and user presets."""),
    ],
)

# ─── Lacuna ───────────────────────────────────────────────────────────
# Every claim below is checked against the 0.2.0 build: README, QUICKSTART and docs/ in the
# lacuna-vst repo, and its in-process test suites (docs/VALIDATION.md there).
PRODUCTS["lacuna"] = vst(
    name="Lacuna",
    title="Lacuna · SHLabs",
    desc="""Lacuna is a harmonic resonator: six tuned resonators driven by the sound you feed them. Gap, Bloom and Ripple shape the response. Hold and Strike keep and test it. MIDI notes move the root, and Follow tracks the key Cadence is playing. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Effects", "/#cat-effects"),
    cat="Harmonic resonator",
    claim="""Six tuned resonators driven by your audio.""",
    lead="""Feed it a drum loop, a pluck or a voice. Six resonators tuned to a chord take their energy from that sound and ring. Gap holds them back while the source plays. Bloom sets how fast they return. Ripple lets the six voices enter one after another, so a hit gets a short harmonic reply.""",
    spec=["VST3 · AU · Standalone", "macOS · Windows to follow"],
    shot=("/img/shots/lacuna.jpg", "The Lacuna plugin interface", 1280, 886),
    rows=[
        ("Resonators", "Six tuned voices",
         """Six resonators ring at the pitches of a chord: fifths, minor or major ninth, suspended, or the exact harmonic series. Set the root on the panel, or play it. A held MIDI note moves it, and the last note held wins."""),
        ("Gap &amp; Bloom", "Room for the source",
         """Gap pulls the response down while the source is loud, so the hit stays clear. Bloom sets how the response returns once the sound falls away, from twenty milliseconds to more than a second."""),
        ("Ripple", "Voices in sequence",
         """After each hit, the six voices can enter one after another instead of all at once. At full Ripple they arrive a sixteenth note apart, at the host's tempo."""),
        ("Hold &amp; Strike", "Sustain and test",
         """Hold stops new sound from exciting the resonators and sustains what is ringing, for as long as it stays on. Strike sends one short burst, so you can hear a chord or a decay without routing any audio."""),
        ("Follow", "In Cadence's key",
         """With Follow on, Lacuna tracks the key Cadence is playing on the same computer, inside Cadence or in another host. The root moves to the key, and the ninth voicings turn major or minor with it. When the feed stops, the last key holds."""),
        ("Clean", "Nothing added",
         """No oscillator and no noise in the signal path: silence in is silence out. Zero latency, the same level from 44.1 to 192 kHz, and a display of the input, the response and each voice as it rings."""),
    ],
)

# ─── Legato (called Glue until 1.0.0) ─────────────────────────────────
PRODUCTS["legato"] = vst(
    name="Legato",
    title="Legato · SHLabs",
    desc="""Legato is an SSL-style mastering bus compressor with stepped controls, program-dependent release, a sidechain high-pass, Mid/Side, a parallel mix and a large gain-reduction meter. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Mastering tools", "/#cat-mastering"),
    cat="Mastering bus compressor",
    claim="""An SSL-style bus compressor. Legato is Italian for bound together. Until 1.0.0 it was called Glue.""",
    lead="""A bus compressor in the style of the SSL G-series, with a clean VCA core and program-dependent release. It applies moderate gain reduction across the stereo image, on a mix bus or a master.""",
    shot=("/img/shots/glue.jpg", "The Legato plugin interface (1.0.0, as Glue)", 1280, 759),
    rows=[
        ("Topology", "Feed-forward VCA",
         """A feed-forward VCA compressor in the style of the SSL G-series. It is designed for low amounts of gain reduction on a full mix."""),
        ("SSL controls", "Stepped &amp; program-dependent",
         """Stepped ratio, attack and release, plus an Auto release that adapts to the signal. Brief peaks recover fast. Sustained passages recover slowly."""),
        ("Sidechain HPF", "Less low-end pumping",
         """A high-pass filter on the detector stops kick and bass from triggering the whole bus. The compression then follows the rest of the mix."""),
        ("Mid / Side", "Centre and sides, apart",
         """Switch the detector into Mid/Side and compress the centre and the sides independently. You can tighten the middle without reducing the width, or the reverse. The stereo link adjusts from dual-mono to fully linked."""),
        ("Parallel mix", "Wet/dry blend",
         """A wet/dry Mix control for parallel compression. Compress hard, then blend the result under the dry signal to add density and keep the transients."""),
        ("Metering", "Gain reduction",
         """A large gain-reduction meter with input and output levels on either side. Soft knee, makeup gain and an auto-gain option keep the level matched while you adjust."""),
    ],
)

# ─── Stesso ───────────────────────────────────────────────────────────
PRODUCTS["stesso"] = vst(
    name="Stesso",
    title="Stesso · SHLabs",
    desc="""Stesso is a mastering equaliser: up to 24 bands and eight filter types over a live pre/post spectrum, a draggable curve, slopes from 6 to 96 dB/oct, and per-band Left/Right or Mid/Side. VST3 / AU / Standalone. Coming soon.""",
    crumb=("Mastering tools", "/#cat-mastering"),
    cat="Mastering equaliser",
    claim="""A mastering equaliser with a draggable curve over a live spectrum.""",
    lead="""Up to twenty-four bands, eight filter types and slopes from 6 to 96 dB per octave. It covers broad tone shaping and narrow corrections on one panel.""",
    shot=("/img/shots/stesso.jpg", "The Stesso plugin interface", 1280, 871),
    rows=[
        ("Drag the curve", "Edit on the curve",
         """Place a node anywhere on the response and drag it. Frequency and gain follow the cursor, and the scroll wheel sets Q. The whole EQ is one curve drawn over the spectrum."""),
        ("24 bands · 8 types", "Bands and filter types",
         """Up to twenty-four bands and eight filter shapes, including bell, low and high shelf, high-pass, low-pass and notch. Slopes run from 6 to 96 dB per octave."""),
        ("Pre / post spectrum", "A live analyser",
         """A real-time analyser shows the signal before and after the EQ, behind the curve. Find a resonance, then place the band on it."""),
        ("L/R · Mid/Side", "Per-band stereo",
         """Any band can process the full stereo signal, the left or right channel only, or the mid or sides only. You can de-ess the centre alone, brighten the sides alone or correct a channel imbalance."""),
        ("Filter core", "Curve and response",
         """The curve on screen is the response the filters apply. The core is suitable for the master bus and for narrow corrective cuts."""),
        ("Workflow", "Interface",
         """A resizable interface with a readable grid. Solo-listen per band to audition a move. Gain matching and a preset browser for your own mastering chains."""),
    ],
)

# ─── Tonnetz ──────────────────────────────────────────────────────────
PRODUCTS["tonnetz"] = vst(
    name="Tonnetz",
    title="Tonnetz · SHLabs",
    desc="""Tonnetz is a MIDI harmony generator: a master key and scale, an interactive Neo-Riemannian lattice, three quantizers, a voiced chord generator, arpeggiator, bass, drone and a progression sequencer, all driving your synths over MIDI. VST3 / AU / Standalone. Coming soon.""",
    crumb=("MIDI generators &amp; composers", "/#cat-midi"),
    cat="MIDI harmony generator",
    claim="""A MIDI harmony generator for your whole rig.""",
    lead="""Set a key and scale, then play chords from an interactive Neo-Riemannian lattice. Three quantizers, a voiced chord generator, an arpeggiator, bass and drone all use the same harmony. They drive any synth or hardware over MIDI. Tonnetz makes no sound of its own.""",
    shot=("/img/shots/tonnetz.jpg", "The Tonnetz plugin interface", 1280, 1226),
    rows=[
        ("The lattice", "Chords on a Tonnetz",
         """An interactive Neo-Riemannian Tonnetz lattice sits at the centre of the plugin. Click a triad and all parts follow. Notes light up as they play."""),
        ("Master harmony", "One key for all parts",
         """A live, modulatable key and scale with degree-to-chord stacking (root / 3 / 5 / 7 / 9 / 11 / 13). Change the degree and every part re-voices at once."""),
        ("Quantizers", "Three MIDI quantizers",
         """Three independent channels snap incoming MIDI to the master key, in Scale, Triad, 7th, 9th or Full mode. Each has its own input and output MIDI channel and octave."""),
        ("Chord + parts", "Chords, arpeggio, bass, drone",
         """A voiced chord generator with voice-leading, spread and inversions, plus an arpeggiator, bass and drone. Each part routes to its own synth on its own channel, with swing and humanize."""),
        ("Song mode", "Progression sequencer",
         """A 16-step progression sequencer drives the degree from the host transport or the internal clock, so changes land on the beat or bar. Twelve factory presets are included, and you can save your own."""),
        ("Perform", "Live controls",
         """Chord-by-MIDI, global transpose, quantized chord changes, MIDI-Learn on every control, and drag-to-DAW MIDI export of the whole arrangement."""),
    ],
)

# ─── Metro 185 ────────────────────────────────────────────────────────
PRODUCTS["metro185"] = vst(
    name="Metro 185",
    title="Metro 185 · SHLabs",
    desc="""Metro 185 is a MIDI-effect step sequencer based on the RYK M-185 and Roland System 100m. VST3 / AU / Standalone. Coming soon.""",
    crumb=("MIDI generators &amp; composers", "/#cat-midi"),
    cat="MIDI step sequencer",
    claim="""A MIDI step sequencer based on the RYK M-185 and Roland System 100m.""",
    lead="""A MIDI effect. Place it on a MIDI track, route it into any instrument and drive it with eight steps.""",
    shot=("/img/shots/metro185.jpg", "The Metro 185 plugin interface", 1280, 865),
    rows=[
        ("Step engine", "Eight steps",
         """Eight steps with sample-accurate MIDI generation, locked to the host transport. Per step: pitch, gate mode, pulse count (1–8), velocity, gate length, ratchets, slide, skip and two CC outputs."""),
        ("14 gate modes", "Gate modes per step",
         """Single, repeat, legato, hold, divisions, probability gates and two Euclidean modes that spread onsets across a step's pulses. RYK-style ratcheting gives up to four re-triggers."""),
        ("Musical", "34 scales &amp; swing",
         """Automatic quantization to 34 scales with root selection. Global and MIDI-input transpose, swing on every other pulse, and pitch-bend slide between steps."""),
        ("Play modes", "Direction &amp; chance",
         """Forward, reverse, ping-pong, random and brownian. Each has a "fixed" variant that always traverses all eight steps. Sequence length is 1–8."""),
        ("Host", "DAW integration",
         """Full transport sync, every control automatable, right-click MIDI-learn on any parameter, state saved with the project, and a configurable MIDI output channel."""),
        ("Patterns", "Save &amp; recall",
         """Store and load full patterns to disk. Route the two per-step CC outputs to modulate other devices."""),
    ],
)

# ─── Stochast (VCV) ───────────────────────────────────────────────────
PRODUCTS["stochast"] = {
    "name": "Stochast",
    "title": "Stochast · SHLabs",
    "desc": """Stochast is a free, open-source suite of 28 VCV Rack 2 modules in five plugins. It turns statistical, social and stochastic processes into control voltage. Sample a distribution, clock a segregation grid or sweep a filter with an epidemic curve. GPL-3.0. macOS, Windows, Linux.""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "5 plugins · 28 modules",
    "status": "Free &amp; open source",
    "soon": False,
    "claim": "Statistical and social models as control voltage.",
    "lead": """Twenty-eight open-source modules in five plugins. Each one turns a statistical, social or stochastic process into control voltage that you can patch anywhere in your rack. Sample a distribution as a modulation source, clock a segregation grid into a gate sequencer, or let an epidemic curve sweep a filter. The models follow the published methods.""",
    "spec": ["5 plugins · 28 modules", "GPL-3.0", "macOS · Windows · Linux"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("Models", "Instruments built from processes",
                 """Each module is a statistical, agent-based or dynamical process, exposed as knobs and control voltage. Examples are a bootstrap resampler, a Granovetter cascade, an SIR epidemic and a reaction-diffusion field. The output behaves the way the underlying model does."""),
                ("Patchable", "Voltage you can route anywhere",
                 """Patch them like any other module. A sampling distribution becomes a modulation source. A segregation grid becomes a generative gate pattern. A drift-diffusion decision fires triggers. An opinion-dynamics model becomes a slow CV sweep. You do not need a statistics background to use them."""),
                ("Reproducible", "Seeded, exact, portable",
                 """Every random module wraps a Mersenne-Twister generator with an explicit on-panel seed, so a seed gives byte-identical results on macOS, Windows and Linux. Closed-form quantities use standard numerical recipes: Lentz continued fractions, BCa bootstrap, Sanger's rule. Patches are plain-JSON <span class="mono">.vcv</span> files, and Tape exports its buffer to CSV for R, Python or Julia."""),
            ]),
        ]},
        {"parts": [
            ("head", "The five plugins", ""),
            ("rows", [
                ("Methods · 15 modules", "Statistical workflow",
                 """Sample · Frame · Regress · Test · Boot · Lag · Code · Tab · Strata · Cohort · Factor · Seed · Tape · Gauge · Quantity. The chain from sampling to inference as patchable voltage: draws, regressions, tests and bootstraps."""),
                ("Polis · 6 modules", "Agent-based social models",
                 """Cascade · Discourse · Pareto · Dilemma · Diffusion · Network. Granovetter cascades, opinion dynamics, wealth condensation, iterated dilemmas, and small-world and scale-free networks as control sources."""),
                ("Epi · 1 module", "Network epidemiology",
                 """Outbreak: SIR-style epidemic spread on Watts-Strogatz, Erdős-Rényi and Barabási-Albert graphs. Its infection wave drives whatever you patch it into."""),
                ("Space · 3 modules", "Spatial dynamics",
                 """Life · Schelling · Turing. Conway's Game of Life with rule presets, Schelling segregation on a 24 × 24 grid, and Gray-Scott reaction-diffusion through spots, stripes and labyrinths."""),
                ("Decisions · 3 modules", "Behavioral economics &amp; cognition",
                 """Prospect · Bandit · DDM. Kahneman-Tversky prospect theory, K-armed bandits with ε-greedy, UCB1 and Thompson sampling, and the Ratcliff drift-diffusion model of decision timing."""),
                ("Purpose", "For patching, not teaching",
                 """Stochast began as a teaching idea, but it is a set of modular-synth instruments. For statistics as a teaching tool, use the separate browser-based Empiria app."""),
            ]),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Free and open source. No paid tier, no telemetry, no account."""),
            ("body", """You need <strong>VCV Rack 2</strong>, a free download for macOS, Windows and Linux from <a class="link" href="https://vcvrack.com/Rack" target="_blank" rel="noopener">vcvrack.com/Rack</a>. Download the latest <strong>.vcvplugin</strong> archives from GitHub releases, place them in Rack's user plugin folder and restart. The modules appear under the <strong>SHLabs</strong> brand. The source is on GitHub under GPL-3.0-or-later, with a full methods manual."""),
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
    "title": "Mashina · SHLabs",
    "desc": """Mashina is a free family of eight VCV Rack 2 modules based on Soviet-era synthesizers and West Coast synthesis: drum voices, oscillators, a master clock, a plate reverb and generative sequencers. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "8 modules",
    "status": "Free download",
    "soon": False,
    "claim": "Eight modules based on Soviet synthesizers and West Coast synthesis.",
    "lead": """A family of eight VCV Rack modules. They combine the circuits and quirks of mid-century Soviet synthesizers, such as the Polivoks, the ANS and the Aelita, with the patching tradition of West Coast synthesis. The set has drum voices, oscillators, a master clock, a plate reverb and generative sequencers.""",
    "spec": ["8 modules", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("Why Soviet", "Design under constraint",
                 """Eastern-bloc synthesizers were built under tight component limits. That produced nonlinear behaviour: overdriven envelopes, drifting VCOs and unusual filters. Mashina takes that behaviour as a design reference. Each module's name is its Russian function."""),
                ("Why West Coast", "Synthesis as patching",
                 """Buchla, Serge and Make Noise treat synthesis as patching, and timbre as a parameter space. Mashina follows that approach with open-ended modules that have many parameters. The two traditions never met historically. Mashina combines them."""),
                ("One family", "A shared panel layout",
                 """Panels share the SHLabs layout: a gunmetal field, a red family stripe under each header, and left-to-right signal flow. The other SHLabs series use the same layout."""),
            ]),
        ]},
        {"parts": [
            ("head", "The eight modules", ""),
            ("rows", [
                ("Udar · удар", "Percussion voice + sequencer",
                 """An analog-style drum voice with an 8-step sequencer, modelled on the DFAM. Two VCOs, noise, a tanh-saturated ladder filter, per-step pitch, velocity and gate modes, conditional triggers, and polyphonic per-step trigger and velocity outputs for poly VCAs and envelopes."""),
                ("Klubok · клубок", "Generative dual sequencer + voice",
                 """A Labyrinth-style pair of step engines with per-step probability, length, divergence and feedback. They feed their own VCO, filter, wavefolder and plate-reverb voice, or any other module through 1V/oct and gate streams."""),
                ("Bochka · бочка", "Techno kick voice",
                 """A kick voice: pitch-swept sine, filtered click, sub layer, transient control, tanh drive, tilt EQ and a choke input. KIT MODE turns one polyphonic trigger cable into kick, snare, hat and clap."""),
                ("Takt · такт", "Master clock",
                 """A Pamela-style master clock with eight independent divided or multiplied outputs (/64 to ×64), tap tempo, run and stop, reset, global swing, pulse width and BPM CV. A master beat output syncs the rest of the rack."""),
                ("Otzvuk · отзвук", "Plate reverb",
                 """A Dattorro-style plate with shimmer, a self-ducker, modulation, tilt EQ and tape drive in the feedback path. CHARACTER morphs from ROOM to PLATE, HALL and SHIMMER. Pre-delay can sync to a clock input."""),
                ("Strela · стрела", "Register additive VCO",
                 """A register-driven additive oscillator based on 1950s Soviet console computers. A 16-bit switch register controls 16 harmonics, a clock shifts the register, and a polyphonic bit-CV input combines through OR, AND or XOR. Spectral thinning, tilt, per-partial phase distortion and drive."""),
                ("Volna · волна", "Polyphonic analog VCO",
                 """A polyphonic oscillator with four simultaneous band-limited outputs: sine, triangle, saw and pulse. PolyBLEP anti-aliasing, CV-controlled PWM, hard sync, FM with a LIN/EXP switch, per-voice drift for chorus, and a warmth control."""),
                ("Podton · подтон", "Subharmonic synth",
                 """A Subharmonicon-style polyrhythmic voice. Two VCOs each have two integer-divided sub-oscillators. Dual 4-step sequencers run on independent clock divisions. It also has a ladder filter, per-step gate modes, conditional triggers and a drone mode."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", ""),
            ("lead", """Free. No account, no nag screen."""),
            ("body", VCV_NEED + """ Download the <strong>.vcvplugin</strong> below, place it in Rack's user plugin folder and restart. The modules appear under the <strong>SHLabs</strong> brand."""),
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
    "title": "Lucida · SHLabs",
    "desc": """Lucida is a free series of generative VCV Rack 2 modules with on-panel displays: a cellular-automaton CV grid (Colony) and a probabilistic shift register (Turing). Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "2 modules · Colony, Turing",
    "status": "Free download",
    "soon": False,
    "claim": "Generative modules with a live display of their state.",
    "lead": """VCV Rack modules built on cellular automata, shift registers and iterated processes. The panel shows the process as it runs. You patch its output as pitch, gates and modulation.""",
    "spec": ["2 modules", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("Display", "The state on the panel",
                 """The on-panel display shows the state of the process. Watching it is how you learn to steer it. A knob change shows on the grid or the register before it reaches a cable."""),
                ("Outputs", "Self-organizing CV",
                 """Every module turns its internal state into CV: scan taps, polyphonic rows, quantized pitch and gates. A self-organizing system becomes a sequencer and a modulation source."""),
                ("One family", "A green accent",
                 """Lucida uses the SHLabs panel layout: a gunmetal field, a header strip and clear signal flow. A green family accent separates it from Mashina's red."""),
            ]),
        ]},
        {"parts": [
            ("head", "The modules", ""),
            ("rows", [
                ("Colony", "Cellular-automaton CV grid",
                 """A 24×16 toroidal cellular automaton runs on screen and emits CV. SPREAD biases the birth and survive rules, MUTATE injects per-cell noise, and FLOW multiplies or divides the simulation clock. Paint cells with the mouse and sweep the scan position with SCAN_CV. Freeze the simulation while the outputs stay live. Output modes are scan-and-tap, polyphonic row or column, and quadrant mix."""),
                ("Turing", "Probabilistic shift register",
                 """A 16-bit looping shift register in the Music Thing Modular tradition. LOCK moves between full randomness and an exact repeating pattern. LENGTH sets the loop from 2 to 16 bits. A built-in quantizer has 10 scales and 12 roots. Outputs: quantized V/OCT, raw bipolar analog, a write-position gate, polyphonic per-bit gates and a clock pulse. The display shows the live bits above a scrolling history."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", ""),
            ("lead", """Free. No account, no nag screen."""),
            ("body", VCV_NEED + """ Colony and Turing ship together in the <strong>SHLabs-Colony</strong> plugin. Download the <strong>.vcvplugin</strong> below, place it in Rack's user plugin folder and restart. The modules appear under the <strong>SHLabs</strong> brand."""),
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
    "title": "Rikoshet · SHLabs",
    "desc": """Rikoshet is four free, tempo-synced rhythmic effects for VCV Rack 2: a rhythmic gate, a ping-pong delay, an 8-step pattern delay and a crossfader. Free and open source, GPL-3.0. macOS, Windows, Linux.""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "4 modules · Gate, PingPong, MultiTap, Blend",
    "status": "Free &amp; open source",
    "soon": False,
    "claim": "Rhythmic delay and gate effects.",
    "lead": """Four tempo-synced rhythmic effects for VCV Rack: a rhythmic gate, a ping-pong delay, an 8-step pattern delay and a crossfader. With a clock patched in, they lock to musical time from two bars down to a 1/32. Without a clock, they run free. The main controls have CV inputs.""",
    "spec": ["4 modules", "GPL-3.0", "macOS · Windows · Linux"],
    "sections": [
        {"parts": [
            ("head", "What they share", ""),
            ("rows", [
                ("Timing", "Locked to your clock",
                 """With a clock patched in, every module locks to musical subdivisions from two bars down to a 1/32, with dotted and triplet values. Without a clock, each one runs from its own tempo knob."""),
                ("Stereo", "Stereo controls",
                 """The effects work in the stereo field as well as in time: stereo offset, ping-pong cross-feed, alternating tap panning and width. They do not add harmonic colour of their own."""),
                ("CV", "CV inputs",
                 """Every module has CV over rate, time, feedback, mix or depth. Parameter glides are click-free, and every module has dry-through bypass."""),
            ]),
        ]},
        {"parts": [
            ("head", "The four modules", ""),
            ("rows", [
                ("Gate · 10 HP", "Rhythmic gate",
                 """A tempo-synced amplitude gate, from tremolo to hard pattern gating. Rate picks from 14 musical subdivisions. Shape morphs a hard square to a raised cosine. Pulse Width sets the duty cycle. Stereo Offset shifts the right channel for width. CV over Rate, Shape, Depth and PW, plus a gate-envelope output."""),
                ("PingPong · 12 HP", "Ping-pong delay",
                 """A stereo delay with cross-fed feedback that moves repeats between channels. Spread offsets the right-channel time. Cross sets how much feedback crosses sides. Low-cut and high-cut filters sit in the feedback path, so repeats darken as they fade. Sync or free time."""),
                ("MultiTap · 20 HP", "Pattern delay",
                 """An 8-step delay across a tempo-synced window. Per-tap level sliders place the hits. Alternating L/R panning with Spread widens the image. Decay tapers the taps toward the end. Feedback recirculates the whole pattern through the high-cut."""),
                ("Blend · 6 HP", "Crossfader",
                 """A stereo A/B crossfader with input drive and an equal-power curve. Blend parallel chains of Rikoshet effects, or use it as a dry/wet control around a serial chain. CV over Mix and Drive."""),
            ]),
        ]},
        {"parts": [
            ("head", "Get it", ""),
            ("lead", """Free and open source. No account, no nag screen."""),
            ("body", """Search <strong>Rikoshet</strong> in the VCV Library and click Add, or download the plugin and place it in Rack's user plugin folder. It appears under the <strong>SHLabs</strong> brand. The source is on GitHub under GPL-3.0."""),
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
    "title": "Atmos · SHLabs",
    "desc": """Atmos is a free family of four VCV Rack 2 modules for tone, space and time: the Helix ladder filter, the Halo stereo repeater, the Skywave delay and the Metro 185 step sequencer. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "4 modules · Helix, Halo, Metro185, Skywave",
    "status": "Free download",
    "soon": False,
    "claim": "A filter, two stereo time effects and a sequencer.",
    "lead": """Four VCV Rack modules: the <strong>Helix</strong> transistor-ladder filter, the <strong>Halo</strong> stereo repeater, the <strong>Skywave</strong> delay with reverb, and the <strong>Metro 185</strong> step sequencer.""",
    "spec": ["4 modules", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "The four modules", ""),
            ("rows", [
                ("Helix", "Transistor-ladder filter",
                 """A 4-pole Moog-style lowpass that self-oscillates and tracks V/oct, so it can also act as a sine source. Three added controls: DRIFT detunes the poles, FRICTION adds per-stage saturation, and TURBULENCE feeds noise into the resonance. Simultaneous LP, HP and BP outputs, selectable slope, drive and 16-voice polyphony."""),
                ("Halo", "Stereo colour repeater",
                 """A modulated multi-tap delay network with two independent zones and polarizing pitch drift. It gives diffuse, slightly detuned echoes across the stereo field."""),
                ("Skywave", "Delay &amp; reverb",
                 """A multi-model stereo delay with scatter reverb, themed on radio propagation. Three engines: longwave (tape), shortwave (bucket-brigade) and microwave (clean digital). Internal modulation, hiss and crackle, freeze and clock sync."""),
                ("Metro 185", "Step sequencer",
                 """An eight-stage sequencer in the M185 and Metropolis tradition. Each stage has a pitch, a pulse count and a gate type. The count and gate-type controls are vertical sliders and accept polyphonic CV."""),
            ]),
        ]},
        {"parts": [
            ("head", "Design notes", ""),
            ("rows", [
                ("Slow by default", "Set it and listen",
                 """Knob ranges cover changes that take several minutes. Modulation depths suit slow movement. Defaults give a sound that moves without any input."""),
                ("Panel", "Gold accent, few jacks",
                 """The family uses a gold accent under each panel header. Layouts favour large knobs over rows of jacks, because you set these modules once and listen."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", "Each module ships as its own plugin"),
            ("lead", """Free. Each module ships as its own plugin, so you can install only the ones you want."""),
            ("body", VCV_NEED + """ Download the <strong>.vcvplugin</strong> files below, place them in Rack's user plugin folder and restart. They appear under the <strong>SHLabs</strong> brand."""),
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
    "title": "Terra · SHLabs",
    "desc": """Terra is a free gestural granular sampler for VCV Rack 2: six grain voices steered by an on-panel XY field over a stereo 8-second buffer. Free download for macOS (Apple Silicon).""",
    "crumb": ("VCV Rack 2", "/#vcv"),
    "cat": "1 module",
    "status": "Free download",
    "soon": False,
    "claim": "A gestural granular sampler.",
    "lead": """Terra records a few seconds of audio into a buffer and plays it back as overlapping grains. An on-panel XY field steers them: read position on one axis, grain pitch on the other. Six voices spread around that point.""",
    "spec": ["1 module", "Freeware", "macOS (Apple Silicon)"],
    "sections": [
        {"parts": [
            ("head", "What it is", ""),
            ("rows", [
                ("The field", "Steer six voices by hand",
                 """Six grain voices share a stereo 8-second buffer fed from AUDIO IN. FREEZE holds the buffer so you can scrub a held sound. On the XY field, X is the buffer read position and Y is grain pitch (±12 semitones). POSITION and PITCH knobs, plus X-CV and Y-CV, set the centre of the field."""),
                ("The cloud", "Spread, scatter, shape",
                 """SPREAD places the six voices around the centre on a ring. SCATTER adds per-grain randomization. The other grain controls are DENSITY (1–100 g/s), SIZE (1–500 ms), SHAPE (Hann to rectangular), JITTER and FEEDBACK. V/OCT transposes the whole field."""),
                ("Outputs", "Mix plus per-voice poly",
                 """A stereo L/R mix, plus a polyphonic OUT with one voice per channel. You can process each of the six grains separately downstream."""),
            ]),
        ]},
        {"id": "get", "parts": [
            ("head", "Get it", ""),
            ("lead", """Free. No account, no nag screen."""),
            ("body", VCV_NEED + """ Download the <strong>.vcvplugin</strong> below, place it in Rack's user plugin folder and restart. The module appears under the <strong>SHLabs</strong> brand."""),
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
    ("cat-live", "Performance &amp; live", "Mixer and clock", [
        ("01", "/cadence/", "Performance mixer &amp; master clock", "Cadence",
         """Four channels of live input or beatgrid players, a filter and full-kill EQ per channel, a pre-fader cue bus, and a master MIDI clock.""",
         "Soon", "is-soon"),
    ]),
    ("cat-synths", "Synthesizers &amp; instruments", "Sound sources", [
        ("02", "/cell/", "Subtractive synthesizer", "Cell",
         """Two band-limited oscillators, sub and noise into one state-variable filter. About one percent of a CPU core for eight voices.""",
         "Soon", "is-soon"),
        ("03", "/schlagzeugs/", "Generative drum machine", "Schlagzeugs",
         """Six lanes with their own lengths and rates. DFAM-style sequencing, Labyrinth-style registers, Rings-style toms, and MIDI out on every lane.""",
         "Soon", "is-soon"),
    ]),
    ("cat-effects", "Effects", "Modulation · space · resonance", [
        ("04", "/contour/", "Multi-LFO modulation rack", "Contour",
         """Draw modulation on a curve editor and lock it to the beat. Four curve-LFOs over volume, pan and filter, with MIDI out.""",
         "Soon", "is-soon"),
        ("05", "/spazio/", "Reverb and delay continuum", "Spazio",
         """A studio delay and a modulated reverb on one CONTINUUM control. In the middle, repeats diffuse into reverb tails.""",
         "Soon", "is-soon"),
        ("06", "/lacuna/", "Harmonic resonator", "Lacuna",
         """Six tuned resonators driven by your audio. Gap, Bloom and Ripple shape the response, and Follow tracks Cadence's key.""",
         "Soon", "is-soon"),
    ]),
    ("cat-mastering", "Mastering tools", "Compression and EQ", [
        ("07", "/legato/", "Mastering bus compressor", "Legato",
         """An SSL-style bus compressor with stepped controls, program-dependent release, sidechain high-pass, Mid/Side and a parallel mix.""",
         "Soon", "is-soon"),
        ("08", "/stesso/", "Mastering equaliser", "Stesso",
         """A draggable curve over a live spectrum. Up to 24 bands, eight filter types, per-band Left/Right or Mid/Side.""",
         "Soon", "is-soon"),
    ]),
    ("cat-midi", "MIDI generators &amp; composers", "Sequencing and harmony", [
        ("09", "/tonnetz/", "MIDI harmony generator", "Tonnetz",
         """Master key and scale, an interactive Tonnetz lattice, three quantizers, chords, arpeggio, bass and drone, sent to your synths over MIDI.""",
         "Soon", "is-soon"),
        ("10", "/metro185/", "MIDI step sequencer", "Metro 185",
         """Eight steps based on the RYK M-185 and System 100m. Ratchets, 34 scales and 14 gate modes.""",
         "Soon", "is-soon"),
    ]),
    ("cat-visuals", "Visuals", "Video synthesis", [
        ("11", "/kinora/", "Audio-reactive video synth", "Kinora",
         """Beat-locked GPU scenes for a projector, or for whatever your Mac is playing. Thirty-two scenes and Syphon output.""",
         "Soon", "is-soon"),
    ]),
]

VCV_ROWS = [
    ("12", "/stochast/", "5 plugins · 28 modules", "Stochast",
     """Statistical and social models as patchable CV: sampling distributions, the bootstrap, agent-based cascades, epidemics, reaction-diffusion.""",
     "Free", "is-free"),
    ("13", "/mashina/", "8 modules", "Mashina",
     """Based on Soviet synthesizers and West Coast synthesis. Drum voices, oscillators, a master clock, a plate reverb and generative sequencers.""",
     "Free", "is-free"),
    ("14", "/lucida/", "2 modules · Colony, Turing", "Lucida",
     """A cellular-automaton grid and a probabilistic shift-register sequencer with a built-in quantizer. Each shows its state on the panel.""",
     "Free", "is-free"),
    ("15", "/rikoshet/", "4 modules · Gate, PingPong, MultiTap, Blend", "Rikoshet",
     """Rhythmic delay and gate effects, tempo-synced to your clock.""",
     "Free", "is-free"),
    ("16", "/atmos/", "4 modules · Helix, Halo, Metro185, Skywave", "Atmos",
     """A transistor-ladder filter, a stereo colour repeater, a delay with reverb and an eight-stage sequencer.""",
     "Free", "is-free"),
    ("17", "/downloads/SHLabs-Phosphor-2.0.0-mac-arm64.vcvplugin",
     "3 modules · Beam, Chroma, Cathode", "Phosphor for VCV Rack",
     """An LZX-style video chain. It passes a low-resolution RGB frame over an expander bus and turns luma and motion back into CV.""",
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
        head("SHLabs · Software for music and visuals",
             """SHLabs is an independent studio in Switzerland. It makes Cadence, a performance mixer and master clock, Kinora, an audio-reactive video synth, a line of VST3 and AU plugins, and free modules for VCV Rack 2.""",
             home=True,
             og=("SHLabs · Software for music and visuals",
                 "An independent studio in Switzerland. Apps, plugins and modules for the stage, the DAW and VCV Rack."))
        + nav(home=True, gsw="/gsw/")
        + """
  <div class="sheet" id="top">

  <!-- ─── hero ───────────────────────────────────────────────────────── -->
  <header class="hero pad" id="main">
    <div class="hero__meta mono">
      <span>Independent studio · Switzerland</span>
      <span class="dim-2">Catalogue %d</span>
    </div>

    <h1 class="display">Software<br>for music<br>and visuals.</h1>

    <div class="hero__grid">
      <div class="hero__lead">
        <p class="lead">
          SHLabs makes VST3 and AU plugins, standalone apps and modules for
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
      <span class="mono dim">Paid · Coming soon</span>
    </div>

    <div class="flag pad">
      <div class="flag__id">
        <span class="mono dim">Performance &amp; live · Standalone</span>
        <h3 class="flag__name"><a href="/cadence/">Cadence</a></h3>
      </div>
      <div class="flag__text">
        <p class="flag__claim">A four-channel performance mixer and master clock.</p>
        <p class="body">
          A standalone app with beatgrid clip players and quantized launch.
          It detects track structure, separates stems on your machine and can
          kill them on the bar. Assist can carry a transition. A Composer timeline
          lays out a set in advance. MIDI or audio that you play records back onto
          its channel as a loop. A sample-accurate MIDI clock drives your modular,
          drum machines and grooveboxes.
        </p>
        <div class="flag__spec mono">
          <span>4-channel mixer</span>
          <span>24-PPQN MIDI clock</span>
          <span>OSC broadcast</span>
          <span class="dim-2">macOS · Windows beta in testing</span>
        </div>
      </div>
    </div>

    <div class="flag pad">
      <div class="flag__id">
        <span class="mono dim">Visuals · VST3 · AU · Standalone</span>
        <h3 class="flag__name"><a href="/kinora/">Kinora</a></h3>
      </div>
      <div class="flag__text">
        <p class="flag__claim">An audio-reactive video synth.</p>
        <p class="body">
          A GPU engine with thirty-two scenes and a particle system of
          100,000 points. Band envelopes
          and onset detectors drive the image. It locks to Cadence or to your host
          playhead and runs fullscreen on a projector.
        </p>
        <div class="flag__spec mono">
          <span>GLSL engine</span>
          <span>138 presets</span>
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
          Cadence sends its clock, beat phase, band energy, kick onsets and drop
          intensity to Kinora over OSC, so the visuals follow the set. The bundle
          also includes Cell, Schlagzeugs, Contour, Spazio, Lacuna, Legato, Stesso
          and Tonnetz.
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
        <span>Eleven titles</span>
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
        <span>Free</span>
      </div>
    </div>
  </section>

  <div class="rule--ink"></div>

  <!-- ─── 04 studio ──────────────────────────────────────────────────── -->
  <section class="sec" id="studio">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">04</span> The studio</h2>
      <span class="mono dim">How we work</span>
    </div>

    <div class="ethos pad">
      <div>
        <span class="mono dim">State</span>
        <h3>Full recall</h3>
        <p class="body">
          Generative modules are seedable. Every plugin recalls its full state.
          A saved patch plays the same on every machine.
        </p>
      </div>
      <div>
        <span class="mono dim">Interface</span>
        <h3>Controls first</h3>
        <p class="body">
          Panels and plugin windows carry controls, not decoration. Drag-to-assign
          modulation, MIDI learn and sensible defaults. No telemetry.
        </p>
      </div>
      <div>
        <span class="mono dim">Engine</span>
        <h3>Named methods</h3>
        <p class="body">
          The tools use analog-modelled circuits, feedback, sampling and stochastic
          processes. Product pages name the method behind a tool where one applies.
        </p>
      </div>
    </div>

    <div class="strip pad">
      <div class="strip__a">
        <h4>The studio</h4>
        <p class="body">
          An independent studio in Switzerland. One person builds everything here:
          plugins and standalone apps for the stage and the DAW, and free modules
          for VCV Rack 2.
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
        head("About · SHLabs",
             """SHLabs is a one-person studio in Switzerland. It makes modules for VCV Rack, VST3 and AU plugins, and standalone apps.""")
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
      <div class="psheet__claim"><p>Software for the rack, the DAW and the stage.</p></div>
      <div class="psheet__desc">
        <p class="body">
          SHLabs is a small independent studio. The catalogue started with modules
          for <a class="link" href="https://vcvrack.com" target="_blank" rel="noopener">VCV&nbsp;Rack</a>.
          A second branch of VST3&nbsp;and AU plugins and standalone apps is in
          beta. They run in Ableton Live, Logic, Bitwig and other hosts. The tools
          cover modulation, sequencing, generative sources, gate logic and stochastic
          processes. Many draw on analog computing, where a calculation was a
          physical process that you could see.
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
          On the rack side, the catalogue has five families:
          <strong>Stochast</strong>, <strong>Mashina</strong>, <strong>Lucida</strong>,
          <strong>Rikoshet</strong> and <strong>Atmos</strong>. All of them are free.
          On the DAW side, the paid line covers synths, effects, mastering tools,
          MIDI generators and visuals. Both sides share one design language.
        </p>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">How it started</h2>
      <span class="mono dim-2">Background</span>
    </div>
    <div class="cols pad cols--open">
      <div class="cols__k mono">In the first person</div>
      <div class="cols__v prose">
        <p>
          SHLabs is a one-person studio. I grew up near Zurich, Switzerland, and
          work as a data scientist. I have played synthesizers for as long as I can
          remember, and that led to modular.
        </p>
        <p>
          The tools on this site began as things I built for my own jams, live
          shows and productions. One question kept coming up: what if the maths that
          usually stays inside code were something you could turn, patch and hear?
          The tools grew into families from there.
        </p>
        <p>
          I now release them. I expand and test each one first. The VCV&nbsp;Rack
          modules came first, and the plugin line follows. New releases appear when
          they are ready.
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
        Write to us with questions about a release, requests for early access, bug
        reports, or to ask whether a piece of gear works with these tools.
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
             """Support SHLabs: sponsor the studio on GitHub, tell others about the tools, or open an issue. Contributions fund development time and the free modules.""")
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
      <span class="dim-2">Optional</span>
    </div>
    <h1 class="psheet__name">Support</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>Contributions fund development time.</p></div>
      <div class="psheet__desc">
        <p class="body">
          SHLabs is an independent studio. Development happens in evenings and
          at weekends. If a module is useful to you, a contribution helps pay for
          the next one and keeps the free modules free.
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
        Sponsor on GitHub with a monthly amount that you set, or send a one-off
        contribution. GitHub handles the payments, so you need only your existing
        GitHub account.
      </p>
      <div class="acts">
        <a class="act act--fill" href="https://github.com/sponsors/kevisc" target="_blank" rel="noopener">Sponsor on GitHub &#8599;</a>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">Other ways to help</h2>
      <span class="mono dim-2">Free</span>
    </div>
    <div class="spec">
      <span class="row__no">01</span>
      <span class="row__id"><span class="row__cat">Spread the word</span><h3 class="row__name">Tell people about it</h3></span>
      <p class="row__desc">Mention a module in a patch you share, on social media, or to a friend who racks. Word of mouth helps a small studio more than most things, and it costs nothing.</p>
    </div>
    <div class="spec">
      <span class="row__no">02</span>
      <span class="row__id"><span class="row__cat">On GitHub</span><h3 class="row__name">Open an issue</h3></span>
      <p class="row__desc">Bug reports, edge cases, and requests for new modules are all welcome on the SHLabs GitHub at <a class="link" href="https://github.com/shlabs-audio" target="_blank" rel="noopener">github.com/shlabs-audio</a>. Clear steps to reproduce a bug help most.</p>
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
        kb = "%d KB" % round(os.path.getsize(path) / 1024) if os.path.exists(path) else "n/a"
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
        head("Downloads · SHLabs",
             """Direct downloads of the free SHLabs VCV Rack 2 plugins for macOS (Apple Silicon). Place the .vcvplugin file in Rack's user plugin folder and restart.""")
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
          Download a <strong>.vcvplugin</strong> file, place it in Rack's user
          plugin folder and restart. The modules appear under the
          <strong>SHLabs</strong> brand. You need
          <a class="link" href="https://vcvrack.com/Rack" target="_blank" rel="noopener">VCV&nbsp;Rack&nbsp;2</a>,
          which is also a free download.
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
        head("Not found · SHLabs", "", robots="noindex", og=(None, None))
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
      <div class="psheet__claim"><p>This page does not exist.</p></div>
      <div class="psheet__desc">
        <p class="body">
          Check the address, or go to the catalogue of plugins, standalone apps
          and VCV Rack modules.
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


def renamed_stub(lang, name, target, words):
    """A product that changed its name. The old address forwards at once, to people and to
    search engines, like glue/ does for Legato. phosphor/beta/ is not touched: it is its own page."""
    return ('<!doctype html>\n<html lang="%s"><head><meta charset="utf-8"><title>%s · SHLabs</title>\n'
            '<meta http-equiv="refresh" content="0; url=%s"><link rel="canonical" href="https://shlabs.ch%s">\n'
            '<meta name="robots" content="noindex"></head>\n'
            '<body><p>%s <a href="%s">%s</a>.</p></body></html>\n' % (lang, name, target, target, words, target, name))


def empiria_page():
    """A redirect stub. The canonical page is /stochast/; the visible copy is
    only ever seen if the refresh and the script are both blocked."""
    return (
        head("Empiria → Stochast · SHLabs", "", robots="noindex",
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


def cadence_beta_page():
    """Unlisted beta download page. Not in the nav, not in the index, noindex for robots.
    Testers reach it by link only. The file table is generated from
    downloads/beta/SHA256SUMS.txt when the beta artifacts are in place; until then the
    page says the build is in preparation, so a stale link never serves a stale file."""
    sums = os.path.join(ROOT, "downloads", "beta", "SHA256SUMS.txt")
    rows = []
    if os.path.isfile(sums):
        for line in open(sums, encoding="utf-8"):
            parts = line.split()
            if len(parts) >= 2:
                digest, name = parts[0], parts[-1].lstrip("*")
                path = os.path.join(ROOT, "downloads", "beta", name)
                size = os.path.getsize(path) if os.path.isfile(path) else 0
                if not size:
                    mb = "missing"
                elif size < 1e6:
                    mb = "%.0f KB" % (size / 1e3)
                else:
                    mb = "%.1f MB" % (size / 1e6)
                rows.append((name, mb, digest))
    if rows:
        table = "\n".join(
            '        <tr><td><a class="link" href="/downloads/beta/%s">%s</a></td>'
            '<td class="mono dim">%s</td><td class="mono dim-2">%s</td></tr>' % (n, n, mb, d[:16] + "…")
            for n, mb, d in rows)
        files = ('      <table class="tbl">\n        <tr><th>File</th><th>Size</th><th>sha256</th></tr>\n'
                 + table + '\n      </table>\n'
                 '      <p class="mono dim">Full checksums: <a class="link" href="/downloads/beta/SHA256SUMS.txt">SHA256SUMS.txt</a></p>')
    else:
        files = '      <p class="body">The 0.9.5 beta build is in preparation. This page fills in when it is cut.</p>'
    return (
        head("Cadence beta · SHLabs", "Cadence 0.9.5 beta downloads for invited testers.",
             robots="noindex, nofollow", og=(None, None))
        + nav()
        + """
  <div class="sheet">
  <main class="mid pad" id="main">
    <div class="hero__meta mono">
      <span class="dim">Cadence</span>
      <span class="dim-2">0.9.5 beta, invited testers</span>
    </div>
    <h1 class="display">Cadence beta</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>Apple Silicon and Windows. Unsigned, so each system asks once before the first launch. The install card in the zip explains the one step.</p></div>
      <div class="psheet__desc">
""" + files + """
        <p class="body" style="margin-top:22px">
          The Mac zip is 0.9.5. Controllers come ready to map: the Denon DJ SC LIVE 4 is built
          in, the mapping dialog downloads thirteen more from this site, and a tour shows where
          each control of yours acts in Cadence. The FX panel has a professional filter (Clean or
          Ladder, resonance, drive and a tempo-synced sweep), a delay from 1/32 to 4 bars with a
          dub filter in its loop, a reverb with Room, Hall, Plate and Shimmer, and your own
          presets. Every band of the window has the mixer's rails. Phosphor is now called Kinora,
          and Cadence says so. The Kinora features in Cadence need the next Kinora beta, which is
          not on this page yet. The zip also carries 0.9.4's suggested hot cues, whole recorded
          sets on a deck, the now-playing card for OBS, a tracklist for every recording and
          sections on a controller; 0.9.3's hot cues on a controller, where a mapped pad is
          the cue with its number and a press on an empty one sets it; 0.9.2's Peers, where another Cadence on the network mirrors this mix as a
          surface and either chair can move any control, with the linked collection loadable over the
          link; 0.9.1's Assist that mixes slower and in layers (Gradual by default, a staged stem
          hand-over, bar-long stem ramps, a tempo glide across the overlap, and an Assist chapter in
          the manual); and 0.9.0's pads in Perform with a step sequencer, MATCH, tags, ratings
          and relink in the Collection, stems and grid-aware samples in the Sampler, a Composer with
          multi-select, a cycle and a tempo lane, plugins with a long look-ahead that no longer move
          the mix, mono and sidechain plugins, and true-peak meters. The release note has the whole
          list. The Windows installer is still 0.6.0 until our build minutes clear.
          Apple Silicon Macs need macOS 14 or newer. Intel Macs are not supported in this beta.
          Windows shows "Windows protected your PC" on first run: choose More info, then Run anyway.
          The SHLabs plugins are listed above one by one and per platform, so you can take
          only the ones you host in Cadence. The Mac plugin zips are fresh cuts for the launch: each
          carries its licence and third-party notices and passed an in-process smoke test; Glue is
          now Legato. Lacuna 0.2.0 and Schlagzeugs 0.2.0 are universal too. A Mac zip holds the AU and the VST3; a Windows zip
          holds the VST3 and a standalone exe. Each has its own install card. On the Mac, Cell,
          Contour, Legato (1.1.0, called Glue until 1.0.0; the Windows zip is still Glue 1.0.0), Spazio, Stesso and Tonnetz are universal builds and Kinora (still named Phosphor 0.6.1 in its zip) is
          Apple Silicon only. Nothing is code-signed for Windows, so the standalone exe asks once;
          a host loading the VST3 does not.
        </p>
        <p class="body">
          Bugs, impressions and questions to
          <a class="link" href="mailto:shlabs.contact@gmail.com">shlabs.contact@gmail.com</a>.
          Most useful: what you did, what you expected, what happened, and the diagnostics file
          (CADENCE wordmark, About, Save diagnostics file).
        </p>
      </div>
    </div>
  </main>

"""
        + footer()
        + '</div>\n</body>\n</html>\n'
    )


# ═══════════════════════════════════════════════════════════════════════
#  Schwiizerdütsch: a small homage, three pages under /gsw/
#  (gsw is the ISO 639 code for Swiss German). Zurich dialect, in the same
#  plain voice as the English pages. Product and technical terms stay in
#  English, as they do in speech. The English pages stay the full reference.
# ═══════════════════════════════════════════════════════════════════════

GSW_LINK = [
    ("Beat und Tempo", "D Visuals bliibed im Takt",
     """Du muesch kei Tempo tappe."""),
    ("Bass, Mitte, Höhi", "Jede Teil vom Mix isch im Bild",
     """Parameter folged de drüü Bänder."""),
    ("Kick-Treffer", "Jede Kick git en visuelle Treffer",
     """Kinora löst bi jedem Kick e Schockwälle uus."""),
    ("Drop-Intensität", "S Bild baut sich bis zum Drop uuf",
     """Cadence meldet, wie starch de Drop isch."""),
]

GSW_CADENCE = [
    ("Mixer", "Vier Kanäl",
     """Jede Kanal nimmt en Live-Iigang oder en Player. Er hät en Drüü-Band-EQ mit Full Kill und en Filter. En Pre-Fader-Cue-Bus isch au debii."""),
    ("Clock", "Hardware uf em Grid",
     """24-PPQN-MIDI-Clock, sample-gnau und mit de Audio-Clock gekopplet. Mit Start, Stopp und Tap Tempo. Dini Hardware folgt Cadence."""),
    ("Stems", "Vier Teil, uf dim Computer",
     """En Rechtsklick trännt en Track i Drums, Bass, Other und Vocals. S Modell lauft lokal, ohni Cloud und ohni Upload. En Club-Track bruucht uf Apple Silicon öppe vierzg Sekunde."""),
    ("Assist", "En Auto-DJ, wo du stüürsch",
     """Assist chan en Übergang eleige mache und kännt d Tonart. Du chasch de Mix jederziit zrugg neh."""),
    ("Composer", "Es Set im Voruus",
     """E Timeline i Täkt, mit ere Spuur pro Kanal. Druf ligged Audio-Clips, MIDI und Automation."""),
    ("Ufnahm", "Takes als Loop",
     """Kanal scharf stelle, iizähle, spile. De Loop lauft grad im Takt wiiter. De Master nimmt Cadence als 24-Bit-WAV uuf."""),
]

GSW_KINORA = [
    ("Szene", "32 Szene",
     """Vo Fields und Fractal bis Horizon, Pipes und Chrome. Alles lauft i GLSL uf de GPU."""),
    ("Partikel", "100'000 Pünkt",
     """D Simulation lauft ganz uf de Grafikcharte."""),
    ("Reaktion", "Bänder und Onsets",
     """Eigeni Hüllkurve für Level, Bass, Mitte und Höhi. Onset-Detektore für Kick, Snare und Hat."""),
    ("Sync", "Clock-Quälle",
     """Cadence per OSC, de Host-Playhead i de DAW, oder de Beat, wo Kinora im Audio findet."""),
    ("Output", "Bild use",
     """Vollbild uf en zweite Bildschirm oder en Beamer. Syphon uf macOS, H.264-Ufnahm und PNG-Snapshots."""),
]


def gsw_spec(rows):
    return "\n".join(
        '    <div class="spec">\n'
        '      <span class="row__no">%02d</span>\n'
        '      <span class="row__id"><span class="row__cat">%s</span>'
        '<h3 class="row__name">%s</h3></span>\n'
        '      <p class="row__desc">%s</p>\n'
        '    </div>' % (i, cat, name, desc)
        for i, (cat, name, desc) in enumerate(rows, 1)
    )


def gsw_nav(english):
    return (
        '  <a class="skip" href="#main">Zum Inhalt</a>\n'
        '  <nav class="nav">\n'
        '    <div class="nav__in pad">\n'
        '      <a class="wordmark" href="/gsw/">SH<i>labs</i></a>\n'
        '      <div class="nav__links mono">\n'
        '      <a href="/gsw/cadence/">Cadence</a>\n'
        '      <a href="/gsw/kinora/">Kinora</a>\n'
        '%s'
        '      </div>\n'
        '    </div>\n'
        '  </nav>\n' % lang_switch("gsw", english)
    )


def gsw_footer(english):
    return (
        '  <footer class="foot">\n'
        '    <div class="pad">\n'
        '      <div class="foot__word">SH<i>labs</i></div>\n'
        '    </div>\n\n'
        '    <div class="foot__bar pad mono">\n'
        '      <span>&copy; %d SHLabs &middot; Software für Musig und Visuals</span>\n'
        '      <span class="swiss">%s Gmacht i de Schwiiz</span>\n'
        '      <a class="dim-2" href="%s" hreflang="en" lang="en">English</a>\n'
        '    </div>\n'
        '  </footer>\n' % (YEAR, SWISS, english)
    )


def gsw_home():
    return (
        head("SHLabs · Software für Musig und Visuals",
             """SHLabs isch es unabhängigs Studio i de Schwiiz. Apps, Plugins und Module für d Bühni, d DAW und VCV Rack.""",
             lang="gsw", canonical="https://shlabs.ch/gsw/")
        + gsw_nav("/")
        + """
  <div class="sheet" id="top">

  <header class="hero pad" id="main">
    <div class="hero__meta mono">
      <span>Unabhängigs Studio · Schwiiz</span>
      <span class="dim-2">Schwiizerdütsch</span>
    </div>

    <h1 class="display">Software<br>für Musig<br>und Visuals.</h1>

    <div class="hero__grid">
      <div class="hero__lead">
        <p class="lead">
          SHLabs macht VST3- und AU-Plugins, Standalone-Apps und Module für
          <a class="link" href="https://vcvrack.com" target="_blank" rel="noopener">VCV Rack 2</a>.
          Die Siite isch e chlini Hommage a d Mundart. Alli Details stönd uf de
          <a class="link" href="/" hreflang="en">änglische Siite</a>.
        </p>
      </div>
    </div>
  </header>

  <div class="rule--ink"></div>

  <section class="sec">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">01</span> Di zwei Apps</h2>
      <span class="mono dim">Choschtet öppis · Chunnt bald</span>
    </div>

    <div class="flag pad">
      <div class="flag__id">
        <span class="mono dim">Performance &amp; Live · Standalone</span>
        <h3 class="flag__name"><a href="/gsw/cadence/">Cadence</a></h3>
      </div>
      <div class="flag__text">
        <p class="flag__claim">En Performance-Mixer mit vier Kanäl und ere Master-Clock.</p>
        <p class="body">
          Jede Kanal nimmt en Live-Iigang oder en Player mit Beatgrid. Cadence
          erchännt d Struktur vomene Track und trännt d Stems diräkt uf dim
          Computer. Assist chan en Übergang eleige mache. E sample-gnaui MIDI-Clock
          stüürt dis Modular und dini Drum Machines.
        </p>
      </div>
    </div>

    <div class="flag pad">
      <div class="flag__id">
        <span class="mono dim">Visuals · VST3 · AU · Standalone</span>
        <h3 class="flag__name"><a href="/gsw/kinora/">Kinora</a></h3>
      </div>
      <div class="flag__text">
        <p class="flag__claim">En Video-Synth, wo uf Audio reagiert.</p>
        <p class="body">
          E GPU-Engine mit 32 Szene und eme Partikelsystem mit
          100'000 Pünkt. Hüllkurve und Onset-Detektore stüüred s Bild. Kinora
          synchronisiert sich mit Cadence oder mit em Host und lauft im Vollbild
          uf em Beamer.
        </p>
      </div>
    </div>
  </section>

  <div class="rule--ink"></div>

  <section class="sec" id="link">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">02</span> Wie s funktioniert</h2>
      <span class="mono dim">Per OSC</span>
    </div>
    <div class="blk pad">
      <p class="lead">Cadence schickt Live-Date a Kinora. Kinora bruucht si, zum s Bild z stüüre. Du chasch eifach wiiter mixe.</p>
    </div>
%s
  </section>

  <div class="rule--ink"></div>

  <section class="sec">
    <div class="sec__head pad">
      <h2 class="sec__title"><span class="mono sec__no">03</span> S Bundle</h2>
      <span class="mono dim">Priis bim Release</span>
    </div>
    <div class="blk pad">
      <p class="lead">Zäh Produkt: Cadence, Kinora und acht Plugins.</p>
      <p class="body">Cell, Schlagzeugs, Contour, Spazio, Lacuna, Legato, Stesso und Tonnetz.</p>
      <div class="acts">
        <a class="act act--fill" href="mailto:shlabs.contact@gmail.com">Schriib eus</a>
        <a class="act" href="/#index" hreflang="en">Alli Produkt &rarr;</a>
      </div>
    </div>
  </section>

""" % gsw_spec(GSW_LINK)
        + gsw_footer("/")
        + tail()
    )


def gsw_product(slug, name, cat, claim, desc, rows, close, other, shot=None):
    plate = ""
    if shot:
        src, alt, w, h = shot
        plate = ('\n  <div class="band band--tight pad">\n%s\n  </div>\n'
                 % plate_html(src, alt, w, h, alt + ".", indent="    "))
    return (
        head("%s · SHLabs" % name, claim, lang="gsw",
             canonical="https://shlabs.ch/gsw/%s/" % slug)
        + gsw_nav("/%s/" % slug)
        + """
  <div class="sheet">

  <header class="psheet pad" id="main">
    <div class="psheet__meta mono">
      <span class="dim">%s</span>
      <span class="is-soon">Chunnt bald</span>
    </div>
    <h1 class="psheet__name">%s</h1>
    <div class="psheet__grid">
      <div class="psheet__claim"><p>%s</p></div>
      <div class="psheet__desc"><p class="body">%s</p></div>
    </div>
  </header>
%s
  <div class="rule--ink"></div>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">Was es macht</h2>
    </div>
%s
  </section>

  <section class="sec">
    <div class="group__head group__head--first">
      <h2 class="mono">Überchoo</h2>
    </div>
    <div class="blk pad">
      <p class="body">%s</p>
      <div class="acts">
        <a class="act act--fill" href="mailto:shlabs.contact@gmail.com">Schriib eus</a>
        <a class="act" href="/gsw/%s/">%s &rarr;</a>
        <a class="act" href="/%s/" hreflang="en">Alli Details uf Änglisch &rarr;</a>
      </div>
    </div>
  </section>

""" % (cat, name, claim, desc, plate, gsw_spec(rows), close, other.lower(), other, slug)
        + gsw_footer("/%s/" % slug)
        + tail()
    )


def gsw_cadence():
    return gsw_product(
        "cadence", "Cadence", "Performance-Mixer &amp; Master-Clock",
        "En Performance-Mixer mit vier Kanäl und ere Master-Clock.",
        """Jede Kanal nimmt en Live-Iigang oder en Player mit Beatgrid. E sample-gnaui MIDI-Clock stüürt dini Hardware. Assist chan de Mix hebe, während du spilsch. Was du uf eme Keyboard oder eme Hardware-Synth spilsch, nimmt Cadence uf em gliiche Kanal als Loop uuf.""",
        GSW_CADENCE,
        """Cadence isch e choschtepflichtigi App i aktiver Entwicklig. D Beta lauft uf macOS und Windows. Für Early Access schriib eus.""",
        "Kinora")


def gsw_kinora():
    return gsw_product(
        "kinora", "Kinora", "Audio-reaktive Video-Synth",
        "En Video-Synth, wo uf Audio reagiert.",
        """E GLSL-Engine uf de GPU, mit 32 Szene und eme Partikelsystem mit 100'000 Pünkt. Bänder und Onsets stüüred s Bild. Wänn Kinora uf eme Track lauft, gaht s Audio unveränderet dure. Bis im November 2026 hät d App Phosphor gheisse.""",
        GSW_KINORA,
        """Kinora isch e choschtepflichtigi App i aktiver Entwicklig. Für Early Access schriib eus.""",
        "Cadence",
        shot=("/img/shots/phosphor-live.jpg",
              "S Fänschter im LIVE-Modus, mit em Preset Night Drive 85. E Entwicklerversion vor em neue Name, drum staht no PHOSPHOR obe",
              1920, 1230))


# ═══════════════════════════════════════════════════════════════════════
#  main
# ═══════════════════════════════════════════════════════════════════════

def main():
    if not os.path.isfile(os.path.join(ROOT, "css", "shlabs.css")):
        sys.exit("error: run this from inside the shlabs repo (css/shlabs.css not found)")

    print("SHLabs: regenerating pages into %s" % ROOT)
    write("index.html", homepage())
    write("404.html", notfound_page())
    write("about/index.html", about_page())
    write("donate/index.html", donate_page())
    write("downloads/index.html", downloads_page())
    write("empiria/index.html", empiria_page())
    write("cadence/beta/index.html", cadence_beta_page())   # unlisted, noindex
    for slug, p in PRODUCTS.items():
        write("%s/index.html" % slug, product_page(p))
    write("gsw/index.html", gsw_home())
    write("gsw/cadence/index.html", gsw_cadence())
    write("gsw/kinora/index.html", gsw_kinora())
    # Kinora was called Phosphor until November 2026: the old addresses send people on.
    write("phosphor/index.html", renamed_stub("en", "Kinora", "/kinora/", "Phosphor is now called"))
    write("gsw/phosphor/index.html", renamed_stub("gsw", "Kinora", "/gsw/kinora/", "Phosphor heisst jetzt"))
    print("done: %d pages" % (12 + len(PRODUCTS)))


if __name__ == "__main__":
    main()
