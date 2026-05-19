# shlabs-site

Static website for the SHLabs open-source modular-synthesizer imprint, served
at <https://shlabs.kevinschoenholzer.com>.

The site is plain HTML + Tailwind CSS (via the official CDN). No build step,
no dependencies. Edit a `.html` file, push, GitHub Pages republishes within
~30 seconds.

## Structure

```
shlabs-site/
├── index.html              landing page — hero + module-families grid
├── empiria/index.html      Empiria suite page (the showcase family)
├── about/index.html        About SHLabs / the author
├── donate/index.html       GitHub Sponsors + PayPal
├── 404.html                fallback
├── img/favicon.svg
├── CNAME                   subdomain mapping for GitHub Pages
└── .gitignore
```

Per-family pages live in their own subdirectory (`mashina/`, `helix/`, etc.)
and are linked from the index card grid. As you add a new family, create the
folder + `index.html` and unhide the corresponding card in `index.html`.

## Deployment

1. Push this repo to GitHub at `kevisc/shlabs-site` (or any name).
2. In repo Settings → Pages: source `main` / root.
3. Add a DNS CNAME at your registrar:
   `shlabs` → `kevisc.github.io`
4. GitHub Pages will issue a Let's Encrypt cert automatically. Site
   live at <https://shlabs.kevinschoenholzer.com> after DNS propagates
   (usually minutes; up to an hour for slower providers).

The `CNAME` file in this repo (containing the single line
`shlabs.kevinschoenholzer.com`) tells GitHub Pages which custom domain
this site serves. If you ever change the subdomain, update this file
and the DNS record together.

## Local preview

Any static-file server works. Two quick options:

```bash
# Python (bundled with macOS)
python3 -m http.server 8000

# Or, if you have Node:
npx serve .
```

Then open <http://localhost:8000> in a browser.

## Editing

The site uses Tailwind CSS loaded from `cdn.tailwindcss.com`. Utility
classes are inline in the HTML. The color palette is configured in the
inline `tailwind.config = { ... }` block at the top of each `.html` file
— keep it identical across pages or factor it out into a shared
`<script>` if you grow the site.

Brand colors used throughout:

| Token  | Hex      | Use                                  |
|--------|----------|--------------------------------------|
| bg     | #0a0c12  | page background                      |
| panel  | #161924  | card background                      |
| border | #23273a  | hairlines                            |
| muted  | #9aa0b4  | secondary text                       |
| cyan   | #6ec8e0  | accent (Empiria family stripe color) |
| amber  | #f5c842  | PayPal donate accent                 |

## License

The site content (text, layout, design) is © Kevin Schoenholzer and
released under CC-BY-4.0. Modules linked from the site are GPL-3.0-or-later.
