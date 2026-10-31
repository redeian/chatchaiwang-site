#!/usr/bin/env python3
"""Render assets/cv.pdf from the same data that builds the site.

The PDF is a document, not a web page: A4, one column, no JavaScript, no
external requests, cream paper on ink to match the identity.

Two things are deliberate here. Chrome paginates a single flowing document
unreliably (a paragraph that starts at the top of page two comes out one
character per line, and no amount of `break-inside` fixes it), so every page
is an explicit `.sheet` of fixed A4 height with `page-break-after`. And the
PDF is printed by Chrome rather than LibreOffice because LibreOffice cannot
see the TH Sarabun face here and drops every Thai glyph in the titles.

Run: env -u PYTHONPATH /opt/homebrew/anaconda3/bin/python3 build_cv.py
Then check the page count against the sheet count, and read the heights the
`measure` mode reports.
"""
from __future__ import annotations

import html
import pathlib
import subprocess
import sys

import build as S

SITE = pathlib.Path(__file__).resolve().parent
OUT_PDF = SITE / "assets" / "cv.pdf"
TMP_HTML = SITE / ".cv.html"

SERIF = '"Iowan Old Style", Palatino, "Palatino Linotype", Georgia, serif'
SANS = ('-apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, '
        '"Sarabun", "Thonburi", sans-serif')

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0;
    -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { background: #F5F2EA; }
body { color: #0B0B0C; font-family: SANS_STACK; font-size: 8.6pt; line-height: 1.42;
       -webkit-font-smoothing: antialiased; }
a { color: inherit; text-decoration: none; }
em { font-style: italic; }
.dot { color: #B4AFA4; padding: 0 .45em; }

.sheet { position: relative; width: 210mm; height: 297mm; padding: 14mm 16mm 12mm;
         page-break-after: always; overflow: hidden; background: #F5F2EA; }
.sheet:last-of-type { page-break-after: auto; }
.sheet .mark { position: absolute; right: 16mm; top: 14mm; width: 9mm; opacity: .9; }

h1 { font-family: SERIF_STACK; font-size: 25pt; line-height: 1.04; letter-spacing: -.012em;
     font-weight: 400; }
h1 span { color: #6B675E; font-size: 14pt; letter-spacing: 0; }
.role { font-size: 9.2pt; margin-top: 2.4mm; }
.role b { font-weight: 600; }
.contact { margin-top: 2mm; font-size: 8pt; color: #6B675E; }
.contact a { border-bottom: .5px solid rgba(11,11,12,.25); }
.hd { border-bottom: 1.4px solid #0B0B0C; padding-bottom: 5mm; }
.hd.has-photo { position: relative; padding-right: 38mm; min-height: 35mm; }
.portrait { position: absolute; right: 0; top: -1mm; width: 30mm; height: 35mm;
            object-fit: cover; object-position: 50% 18%; border-radius: 1.2mm; }

.lede { font-size: 8.9pt; line-height: 1.5; margin-top: 5mm; max-width: 168mm; }

.stat { margin-top: 4.5mm; }
.stat div { display: inline-block; vertical-align: top; margin-right: 8mm; min-width: 26mm; }
.stat b { display: block; font-family: SERIF_STACK; font-size: 14pt; font-weight: 400; line-height: 1.1; }
.stat small { font-size: 7.2pt; color: #6B675E; letter-spacing: .03em; }

section { margin-top: 4.4mm; }
h2 { font-size: 7.3pt; letter-spacing: .17em; text-transform: uppercase; font-weight: 600;
     color: #6B675E; border-top: .9px solid rgba(11,11,12,.28); padding-top: 1.7mm;
     margin-bottom: 2.2mm; }
h2 .n { float: right; letter-spacing: .04em; text-transform: none; font-weight: 400; }

.row { position: relative; padding-left: 25mm; margin-bottom: 2mm; }
.row .when { position: absolute; left: 0; top: .2mm; width: 21mm; font-size: 7.6pt; color: #6B675E; }
.row .role-line { font-weight: 600; }

.eng { margin-bottom: 2.8mm; }
.eng .org { font-weight: 600; font-size: 9.2pt; }
.eng .meta { font-size: 7.6pt; color: #6B675E; margin-bottom: 1mm; }
.eng p { margin-bottom: .8mm; }

.sub { font-size: 7.2pt; letter-spacing: .13em; text-transform: uppercase; color: #6B675E;
       margin: 2mm 0 1.3mm; }
.sub.first { margin-top: 0; }
.pub { font-size: 7.7pt; line-height: 1.34; margin-bottom: .85mm; padding-left: 5mm; text-indent: -5mm; }
.pub .y { color: #6B675E; }
.pub a { border-bottom: .5px solid rgba(11,11,12,.2); }
.clients { color: #6B675E; font-size: 8pt; line-height: 1.45; }
.foot { position: absolute; left: 16mm; right: 16mm; bottom: 8mm; font-size: 6.9pt;
        color: #9C978C; border-top: .5px solid rgba(11,11,12,.12); padding-top: 1.4mm; }
.foot .r { float: right; }
""".replace("SANS_STACK", SANS).replace("SERIF_STACK", SERIF)


def rel(url: str, text: str) -> str:
    return f'<a href="{html.escape(url)}">{html.escape(text)}</a>' if url else html.escape(text)


def e(t: str) -> str:
    return html.escape(str(t))


def paras(body) -> list[str]:
    """ENGAGEMENTS body is a list of paragraphs for some entries and a single
    string for others. Iterating a bare string emits one <p> per character,
    which silently doubles the page and reads as a layout bug."""
    if isinstance(body, str):
        return [body]
    return list(body)


def row(when: str, body: str) -> str:
    return (f'<div class="row"><div class="when">{e(when)}</div>'
            f'<div class="what">{body}</div></div>')


def sheet(inner: str, mark: str) -> str:
    return (f'<div class="sheet">{mark}<div class="page-body">{inner}</div>'
            f'<div class="foot"><span>{e(S.NAME_FULL)} &middot; curriculum vitae &middot; October 2026</span>'
            f'<span class="r">chatchaiwang.com</span></div></div>')


def build_pages() -> tuple[str, dict]:
    projects = sorted(S.PROJECTS, key=lambda p: S.project_span(p[3]), reverse=True)
    pubs = [("Journals", S.JOURNALS), ("Conferences", S.CONFERENCES),
            ("Thai-language proceedings", S.THAI), ("Preprints", S.PREPRINTS)]
    n_pubs = sum(len(v) for _, v in pubs)
    n_speak = sum(len(v) for v in S.SPEAKING.values())
    assert n_pubs == 18, n_pubs
    assert n_speak == 76, n_speak

    mark = '<img class="mark" src="assets/icons/mark.svg" alt="">'

    # ---- page 1: who he is, and what he has delivered
    p1 = [f"""
<div class="hd has-photo">
  <img class="portrait" src="assets/img/portrait-960.jpg" alt="Chatchai Wangwiwattana">
  <h1>Chatchai Wangwiwattana<span>, Ph.D.</span></h1>
  <div class="role"><b>Vice President of Information Technology</b>, University of the Thai Chamber of Commerce
    <span class="dot">&middot;</span> Assistant Professor</div>
  <div class="contact">{e(S.EMAIL)}<span class="dot">&middot;</span>chatchaiwang.com
    <span class="dot">&middot;</span>{rel(S.LINKEDIN, "linkedin.com/in/chatchai-mark-wangwiwattana-ph-d")}
    <span class="dot">&middot;</span>Bangkok, Thailand</div>
</div>
<p class="lede">Technology executive and academic, eighteen years across software engineering, IT leadership
and higher education. Accountable for IT strategy, infrastructure and security for a whole university while
teaching and publishing applied AI research. Has led commissioned research for the Senate of Thailand, True
Corporation, ETDA and the Department of Primary Industries and Mines, and builds capability programmes the
institution can run without him.</p>
<div class="stat">
  <div><b>18</b><small>peer-reviewed papers</small></div>
  <div><b>{n_speak}</b><small>programmes since 2018</small></div>
  <div><b>{len(projects)}</b><small>funded research projects</small></div>
  <div><b>2008</b><small>first software role</small></div>
  <div><b>8</b><small>systems built in house</small></div>
</div>"""]
    engagements = ['<section><h2><span>Selected engagements</span>'
                   '<span class="n">delivered, with an outcome</span></h2>']
    for g in S.ENGAGEMENTS:
        engagements.append(f'<div class="eng"><div class="org">{e(g["org"])}</div>'
                           f'<div class="meta">{g["meta"]}</div>'
                           + "".join(f"<p>{p}</p>" for p in paras(g["body"])) + "</div>")
    engagements.append("</section>")
    p1.append("".join(engagements))

    # ---- page 2: the record — appointments, then the funded work
    p2 = ['<section><h2><span>Experience</span>'
          '<span class="n">2018 to present, and the decade before</span></h2>']
    for group, rows in S.EXPERIENCE:
        p2.append(f'<div class="sub first">{e(group)}</div>')
        for title, org, when in rows:
            p2.append(row(when, f'<span class="role-line">{e(title)}</span>, {e(org)}'))
    p2.append("</section>")

    p2.append('<section><h2><span>Research grants</span>'
              '<span class="n">commissioned and funded</span></h2>')
    for title, role, funder, years in projects:
        p2.append(row(years,
                      f'<span class="role-line">{e(role)}</span>, {e(title)}'
                      f'<br><span style="color:#6B675E">Funded by {e(funder)}</span>'))
    p2.append("</section>")

    p2.append('<section><h2><span>Certifications</span></h2>')
    for cert, issuer in S.CERTIFICATIONS:
        p2.append(row("", f'<span class="role-line">{e(cert)}</span>, {e(issuer)}'))
    p2.append("</section>")

    # ---- page 3: the academic record
    p3 = ['<section><h2><span>Education</span></h2>']
    for deg, inst in S.EDUCATION:
        p3.append(row("", f'<span class="role-line">{e(deg)}</span>, {e(inst)}'))
    p3.append('<div class="sub">Executive programmes</div>')
    for name, yr in S.EXEC_PROGRAMMES:
        p3.append(row(yr, e(name)))
    p3.append("</section>")

    p3.append(f'<section><h2><span>Teaching and speaking</span>'
              f'<span class="n">{n_speak} programmes since 2018</span></h2>'
              f'<p class="clients">{e(S.CLIENTS)}</p></section>')

    p3.append(f'<section><h2><span>Publications</span>'
              f'<span class="n">{n_pubs} peer-reviewed, 2015 to 2026</span></h2>')
    for label, items in pubs:
        items = sorted(items, key=lambda p: int(p["year"]), reverse=True)
        p3.append(f'<div class="sub">{e(label)}, {len(items)}</div>')
        for p in items:
            link = p["url"]
            tail = f' {rel(link, "doi" if "doi.org" in link else "link")}' if link else ""
            p3.append(f'<div class="pub"><span class="y">{p["year"]}.</span> {e(p["authors"])}. '
                      f'{e(p["title"])}. <em>{e(p["venue"])}</em>.{tail}</div>')
    p3.append("</section>")

    doc = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
           "<title>Chatchai Wangwiwattana, Ph.D. — Curriculum Vitae</title>"
           f"<style>{CSS}</style></head><body>"
           + sheet("".join(p1), "") + sheet("".join(p2), mark) + sheet("".join(p3), mark)
           + "</body></html>")
    return doc, {"pubs": n_pubs, "speaking": n_speak, "projects": len(projects), "sheets": 3}


def verify(pdf) -> None:
    """The sheet is a fixed box with overflow:hidden, so a page that is a few
    points too tall loses its last rows silently — the file still opens and
    still looks fine at a glance. Fail the build instead."""
    problems = []
    for i, pg in enumerate(pdf):
        blocks = [b for b in pg.get_text("blocks") if b[4].strip()]
        foot = [b for b in blocks if "curriculum vitae" in b[4]]
        if not foot:
            problems.append(f"p{i+1}: no footer block found")
            continue
        foot_top = foot[0][1]
        body = [b for b in blocks if b not in foot]
        over = [b for b in body if b[3] > foot_top - 1]
        if over:
            problems.append(
                f"p{i+1}: {len(over)} block(s) collide with the footer "
                f"(lowest y {max(b[3] for b in over):.0f}, footer at {foot_top:.0f}): "
                f"{over[0][4].strip()[:60]!r}")
    last = pdf[-1].get_text()
    for sentinel in ("arXiv:2101.10191", "PREPRINTS"):
        if sentinel not in last:
            problems.append(f"last page is missing {sentinel!r} — the tail was clipped")
    if problems:
        raise SystemExit("LAYOUT FAIL\n  " + "\n  ".join(problems))


def main() -> int:
    doc, counts = build_pages()
    TMP_HTML.write_text(doc, encoding="utf-8")
    subprocess.run([
        S.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=4000", f"--print-to-pdf={OUT_PDF}", TMP_HTML.as_uri(),
    ], check=True, capture_output=True)
    import fitz
    pdf = fitz.open(OUT_PDF)
    print(f"wrote {OUT_PDF.relative_to(SITE)}  {OUT_PDF.stat().st_size / 1024:.0f} KB  {counts}")
    print(f"pages in pdf: {pdf.page_count} (expected {counts['sheets']})")
    for i, pg in enumerate(pdf):
        thai = sum(1 for c in pg.get_text() if "\u0e00" <= c <= "\u0e7f")
        print(f"  p{i+1}: chars={len(pg.get_text())} thai={thai}")
    verify(pdf)
    print("layout check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
