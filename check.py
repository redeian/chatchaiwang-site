#!/usr/bin/env python3
"""Gates for chatchaiwang.com. Run after build.py, before any push.

Every check here exists because that exact thing broke once and shipped
silently: a theme that came back, a path that only broke off-root, a count that
drifted from the data, a schema block that stopped parsing. Exits non-zero and
prints what failed, so release.sh can refuse to publish.

    env -u PYTHONPATH /opt/homebrew/anaconda3/bin/python3 check.py
"""

import json
import re
import sys
from pathlib import Path

import build

SITE = Path(__file__).resolve().parent
PAGES = ["index.html", "th/index.html", "publications.html", "speaking.html", "404.html"]
HOME = ["index.html", "th/index.html"]

failures = []
notes = []


def fail(msg):
    failures.append(msg)


def read(name, min_bytes=2000):
    path = SITE / name
    if not path.exists():
        fail(f"{name} is missing")
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) < min_bytes:
        fail(f"{name} is only {len(text)} bytes")
    return text


pages = {name: read(name) for name in PAGES}

# 1. one surface only -------------------------------------------------------
for name, html in pages.items():
    if "prefers-color-scheme" in html:
        fail(f"{name} still carries a prefers-color-scheme block")
    if 'content="#0B0B0C"' in html:
        fail(f"{name} still carries the dark theme-color")

# 2. no root-absolute internal path, including inside srcset ---------------
abs_re = re.compile(r'(?:href|src|srcset|imagesrcset)="(/[^"]*)"')
for name, html in pages.items():
    for hit in abs_re.findall(html):
        fail(f"{name} has a root-absolute path: {hit}")
    for attr in re.findall(r'(?:srcset|imagesrcset)="([^"]*)"', html):
        for candidate in attr.split(","):
            url = candidate.strip().split(" ")[0]
            if url.startswith("/"):
                fail(f"{name} has a root-absolute srcset candidate: {url}")

# 3. structured data parses and says the right thing -----------------------
def ld_blocks(html):
    return re.findall(r'application/ld\+json">(.*?)</script>', html, re.S)


for name in HOME:
    html = pages[name]
    blocks = ld_blocks(html)
    if not blocks:
        fail(f"{name} has no JSON-LD")
        continue
    parsed = []
    for raw in blocks:
        try:
            parsed.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            fail(f"{name} has JSON-LD that does not parse: {exc}")

    person = next((b for b in parsed if b.get("@type") == "Person"), None)
    if not person:
        fail(f"{name} has no Person block")
    else:
        if person.get("identifier", {}).get("value") != build.ORCID_ID:
            fail(f"{name} Person has no ORCID identifier")
        if person.get("alternateName") != build.ALIASES:
            fail(f"{name} alternateName drifted from build.ALIASES")
        expected_same_as = 1 + len(build.SAME_AS) + (1 if build.RESEARCHGATE else 0)
        if len(person.get("sameAs", [])) != expected_same_as:
            fail(f"{name} sameAs has {len(person.get('sameAs', []))}, expected {expected_same_as}")
        orgs = [o for o in person.get("worksFor", []) if o.get("@id")]
        if not orgs:
            fail(f"{name} worksFor does not carry the hub @id")

# 4. the two homepages announce each other ---------------------------------
for name, other in (("index.html", "th"), ("th/index.html", "en")):
    if f'hreflang="{other}"' not in pages[name]:
        fail(f"{name} has no hreflang={other}")
    if 'hreflang="x-default"' not in pages[name]:
        fail(f"{name} has no x-default hreflang")

# 5. every count is counted, not remembered --------------------------------
publications = build.JOURNALS + build.CONFERENCES + build.THAI + build.PREPRINTS
pub_page = pages["publications.html"]
for item in publications:
    if item["title"] not in pub_page:
        fail(f'publications.html is missing "{item["title"][:60]}…"')
notes.append(f"{len(publications)} publications present")

programmes = sum(len(v) for v in build.SPEAKING.values())
speak_rows = pages["speaking.html"].count('class="row"')
if speak_rows != programmes:
    fail(f'speaking.html renders {speak_rows} rows for {programmes} programmes')
notes.append(f"{programmes} programmes present")

grant_rows = pages["index.html"].count('class="row"')

# 6. the identity links are actually on the page --------------------------
for name in HOME:
    html = pages[name]
    for url in (build.HUB, build.SCHOLAR, build.GITHUB, build.KAGGLE, build.XTW, build.ORCID):
        if url not in html:
            fail(f"{name} does not link {url}")
    if not re.search(r'rel="me[\s"]', html):
        fail(f"{name} has no rel=me link")

# 7. the machine-readable files exist and agree ---------------------------
llms = read("llms.txt", 400)
if build.ORCID_ID not in llms:
    fail("llms.txt does not carry the ORCID")
if build.HUB not in llms:
    fail("llms.txt does not point at the identity hub")

robots = read("robots.txt", 300)
for agent in ("GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"):
    if agent not in robots:
        fail(f"robots.txt does not name {agent}")

sitemap = read("sitemap.xml", 300)
locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
if len(locs) != 4:
    fail(f"sitemap.xml has {len(locs)} urls, expected 4")
for loc in locs:
    if not loc.startswith(build.BASE):
        fail(f"sitemap.xml url is off-domain: {loc}")

bib = read("assets/publications.bib", 1000)
bib_entries = len(re.findall(r"^@", bib, re.M))
if bib_entries < len(publications):
    fail(f"publications.bib has {bib_entries} entries for {len(publications)} publications")

# 8. the CV and the portrait are really there ------------------------------
for asset in ("assets/cv.pdf", "assets/og.png", "assets/img/portrait-960.webp",
              "assets/img/portrait-480.webp", "favicon.ico"):
    if not (SITE / asset).exists():
        fail(f"missing asset: {asset}")

# --------------------------------------------------------------------------
for note in notes:
    print(f"  · {note}")
if failures:
    print(f"\n{len(failures)} problem(s):")
    for problem in failures:
        print(f"  ✗ {problem}")
    sys.exit(1)

print(f"\ncheck: PASS — {len(pages)} pages, {len(publications)} publications, "
      f"{programmes} programmes, {grant_rows} profile rows")
