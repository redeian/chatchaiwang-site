# chatchaiwang.com

Static personal site. Online resume, publications, and speaking record for
Chatchai Wangwiwattana, Ph.D.

## What this is

Four hand-built HTML files with the CSS inlined into each one. No framework, no
build step at runtime, no JavaScript, no external requests, no fonts to download,
no analytics, no cookies. A cold first view is the document plus one WebP image.

```
index.html          profile, focus, research, experience, selected work
publications.html   all 18 peer-reviewed items with DOIs
speaking.html       all 76 programmes, 2018 to 2026
404.html
robots.txt
sitemap.xml
site.webmanifest
assets/
  cv.pdf            CV, generated from the Word master
  og.png            1200x630 social card
  img/portrait-*.{webp,jpg}   hero portrait, 480 and 960 wide
  icons/            favicon set, apple touch icon, PWA icons, mark.svg
build.py            regenerates every page and the social card
```

## Editing

Content lives in Python data structures at the top of `build.py` — `STATS`,
`FOCUS`, `PROJECTS`, `EXPERIENCE`, `JOURNALS`, `CONFERENCES`, `THAI`,
`PREPRINTS`, `SPEAKING`, `EDUCATION`, `CERTIFICATIONS`. Edit the data, not the
HTML, then:

```bash
env -u PYTHONPATH /opt/homebrew/anaconda3/bin/python3 build.py
```

The `env -u PYTHONPATH` prefix matters on this machine: the Hermes install venv
shadows PIL and fontTools otherwise.

## Design

Paper `#F5F2EA`, ink `#0B0B0C`, muted `#6B675E`, one hairline weight. Serif for
display, system sans for text. One theme only — a dark variant was built and
removed: the colour organisation marks need a light plate, and maintaining two
surfaces bought the reader nothing.

## SEO

Per-page title, description, canonical, Open Graph and Twitter card, one
`Person` JSON-LD block on the profile and an `ItemList` of `ScholarlyArticle` on
the publications page, plus `sitemap.xml` and `robots.txt`. All names, roles and
publication titles are real text in the HTML, not baked into images.

## Deploying

Paths are relative, so the same folder works at a domain root, at a project
subpath, or opened straight from disk. Point any static host at this directory.
For GitHub Pages, push the repo and enable Pages on the branch root; add a
`CNAME` file containing the domain once DNS is moved.

Changing the canonical domain means editing `BASE` in `build.py` and rebuilding.
