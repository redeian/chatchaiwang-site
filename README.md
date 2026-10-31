# chatchaiwang.com — runbook

Static personal site for Chatchai Wangwiwattana. Four pages, CSS inlined, no
framework, no JavaScript, no external requests, no fonts to download, no
analytics, no cookies. Read this before touching anything; the whole point of the
file is that a new session can be productive in two minutes.

Live: <https://www.chatchaiwang.com/>
Repo: `redeian/chatchaiwang-site`, branch `main`, served by GitHub Pages.

---

## The one rule

**`build.py` is the source of truth. Never edit a `.html` file by hand.**

`index.html`, `th/index.html`, `publications.html`, `speaking.html`, `404.html`,
`sitemap.xml`, `robots.txt`, `llms.txt` and `assets/publications.bib` are all
generated. A hand edit survives until the next build and then vanishes with no
error. If a `.mjs`, a shell one-liner or a perl snippet is handed over that
rewrites output HTML, do not run it — read it for its intent and implement that
in `build.py`.

## Everyday commands

```bash
cd ~/HermesHome/site

./release.sh                          # build + gates, publishes nothing
./release.sh --publish "what changed" # build + gates + commit + push + wait + verify
./release.sh --verify                 # check the live site against this build
```

`env -u PYTHONPATH` is baked into the scripts and matters on this machine: the
Hermes venv shadows PIL and fontTools, and the build dies inside the social-card
render without the unset.

Editing is always the same loop: change a data structure in `build.py`, run
`./release.sh`, look at the printed gate result, publish when the wording is right.

## Where things live

| Path | What it is |
|---|---|
| `build.py` | the generator — every page, the sitemap, `robots.txt`, `llms.txt`, the `.bib` |
| `check.py` | the gates; imports `build.py` so it reads the same data the pages were built from |
| `release.sh` | build → gate → publish → wait → verify |
| `build_cv.py` | prints `assets/cv.pdf` from the same data through Chrome |
| `prep_logos.py` | normalises the organisation marks in `assets/logos/` |
| `assets/` | `cv.pdf`, `og.png`, `img/`, `icons/`, `logos/`, `publications.bib` |
| `a79c10db…txt` | IndexNow key. Do not delete; Bing re-verifies with it |

## Data structures in `build.py`

Edit these, never the HTML.

| Constant | Drives |
|---|---|
| `STATS` / `TH_STATS` | the four tiles at the top |
| `FOCUS` / `TH_FOCUS` | the three focus cards |
| `PROJECTS` | research grants; sorted by `project_span()`, newest first |
| `ENGAGEMENTS` / `TH_ENGAGEMENTS` | Selected engagements, above the grants on purpose |
| `EXPERIENCE` | leadership, industry, advisory groups |
| `JOURNALS`, `CONFERENCES`, `THAI`, `PREPRINTS` | the 18 publications and the `.bib` |
| `SPEAKING` | 76 programmes, dict keyed by year |
| `EDUCATION`, `CERTIFICATIONS` | the bottom two columns |
| `ALIASES`, `SAME_AS` | the identity graph; must match the hub at `markdigitalacademy.com/about` |
| `LOGO_BANDS` / `TH_BANDS` | the four logo bands |

Identity constants sit at the top of `build.py`: `BASE`, `EMAIL`, `LINKEDIN`,
`YOUTUBE`, `ACADEMY`, `HUB`, `ORG_ID`, `GITHUB`, `KAGGLE`, `XTW`, `SCHOLAR`,
`FACEBOOK`, `ACM`, `ORCID`, `ORCID_ID`, `RESEARCHGATE` (deliberately empty).

## Editing rules that came from real mistakes

- **Numbers are counted, never typed.** `check.py` compares rendered rows against
  `len(JOURNALS + CONFERENCES + THAI + PREPRINTS)` and against every title in
  `SPEAKING`. If a count is wrong the build refuses to publish.
- **One organisation, one spelling.** The same body spelled two ways reads as two
  relationships. `Department of Primary Industries and Mines` is the correct name.
- **Client figures belong to the client.** No team sizes, budgets, savings or
  project counts from Srithai, Generali or B.Grimm without their clearance. Scope
  he owns himself (50-person IT org, 2,000 computers, 20,000 iPads) is fine.
- **Thai is one page, not a translation.** `/th/` is the same record with Thai
  scaffolding; organisation names and publication titles keep their own language.
  Nicknames live in JSON-LD `alternateName` only — Mark had the visible
  equivalence sentence removed from the hero, do not put it back.
- **No root-absolute paths.** Everything relative so the folder works at a domain
  root, a subpath, or `file://`. `check.py` fails on `href="/…"`, `src="/…"` and on
  a root-absolute candidate hidden inside `srcset`.
- **One theme.** Paper and ink, always light. No `prefers-color-scheme`, no second
  `theme-color`; `check.py` fails if either comes back.

## Publishing and verifying

`./release.sh --publish "message"` does the whole sequence and prints the live
status of eight URLs. What it does behind the scenes, in case you need it by hand:

```bash
git push origin main
gh api repos/redeian/chatchaiwang-site/pages/builds/latest --jq '.commit+" "+.status'
curl -s -o /dev/null -w '%{http_code}\n' \
  --resolve www.chatchaiwang.com:443:185.199.108.153 https://www.chatchaiwang.com/th/
```

**Always check the live site with `--resolve`.** This Mac's DNS cache kept serving
`ghs.googlehosted.com` — the old Google Sites — for hours after the domain moved,
so a plain `curl` showed the previous site and 404s on every new path while the
deployment was perfectly fine for everyone else. Compare
`dscacheutil -q host -a name www.chatchaiwang.com` (stale) against
`dig +short www.chatchaiwang.com @8.8.8.8` (real). The fix is local:

```bash
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

then a hard reload. Never re-push or revert a build because of it.

## Known open items

- **`https://chatchaiwang.com` (apex) has no working certificate.** GitHub presents
  `CN = *.github.io`, so apex HTTPS returns `000`. `www` is fine. Either point the
  apex back at the old host or wait for GitHub to issue the certificate.
- **Google Search Console is not set up.** Needs his Google account. Path:
  `search.google.com/search-console` → Add property → **Domain** (not URL prefix)
  → DNS TXT at `@` → verify → submit `https://www.chatchaiwang.com/sitemap.xml`.
  Offering the faster route: if he pastes the `google-site-verification` token, put
  it in `head()` and rebuild.
- **ORCID has zero works.** `assets/publications.bib` exists for exactly this:
  ORCID → Works → Add → Import from BibTeX, and ORCID resolves each DOI against
  Crossref. His registered researcher URL is also still `http://`, worth fixing.
- **ResearchGate: no profile found.** Every guessed URL answers 403 and the alias
  search finds nothing. `RESEARCHGATE` stays empty until he supplies the URL — a
  wrong profile link costs more than a missing one.
- **The back link from `markdigitalacademy.com/about` is his to add.** The
  relationship only merges when both ends declare it.

## Files that are not the site

`build.py`, `build_cv.py`, `prep_logos.py`, `check.py`, `release.sh` are committed
and served, which is harmless for a personal site and means the repo alone is
enough to rebuild everything from a clone.
