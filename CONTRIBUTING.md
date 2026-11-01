# Working rules for chatchaiwang.com

A static site built by `build.py` into committed HTML. No framework, no runtime,
no external requests at load time, CSS inlined per page. Deployed by pushing
`main`, served by GitHub Pages.

Anyone, human or agent, changing this repository follows these rules.

## Generated and hand-written

- `build.py` holds the content as Python data and renders `index.html`,
  `th/index.html`, `publications.html`, `speaking.html`, `404.html`.
  **Never hand-edit those HTML files.** Edit `build.py`, then run the build.
- `build_cv.py` renders `assets/cv.pdf`. It carries a new timestamp on every
  run, so a rebuild always shows it as modified. That is expected, not drift.
- `check.py` is the oracle. `ci/verify.sh` runs it, then asserts the committed
  HTML matches what the build produces, then runs the behaviour tests.

## One command

```bash
bash ci/verify.sh
```

It must pass on a fresh clone of `main` on a machine with no Chrome. If it does
not, the repository is not in a shippable state and nothing else matters.

## Rules

- Change content in `build.py`, never in the generated HTML.
- Thai and English pages say the same thing. A change to one language is a
  change to both.
- Counts come from the data structures, never hardcoded in prose.
- No new external request, no new font, no framework, no build step beyond
  `build.py`.
- No root-absolute URL. Everything relative, so the site works under a path.
- Every page has one `h1`, one meta description under 160 characters, a
  canonical link that agrees with `og:url`, and every internal link resolves.
- Do not edit `check.py`, `ci/`, `tests/` or `factory.json` in a normal change.
  If a check is wrong, a person changes it in its own commit that says why.

## Out of scope unless asked for

Analytics, a CMS, dark mode (removed on purpose), comments, a newsletter, any
client-side JavaScript framework.
