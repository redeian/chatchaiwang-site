"""Behaviour tests for chatchaiwang.com.

check.py already guards the structure of the pages. These tests guard the things
it does not: that every internal link actually resolves, that every image says
what it is, that each page has one heading and one description, and that the
metadata agrees with itself.

They read the built HTML, so they fail when the build is stale, which is the
point: the site is the html, not the source.
"""
import re
from html import unescape
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "th/index.html", "publications.html", "speaking.html", "404.html"]
LOCAL = re.compile(r'^(?!https?:|mailto:|tel:|#|javascript:)([^"#?]+)')


def page(name):
    path = SITE / name
    assert path.exists(), f"{name} was not built"
    return path.read_text(encoding="utf-8")


def attr(html, pattern):
    return re.findall(pattern, html, re.S)


@pytest.mark.parametrize("name", PAGES)
def test_every_internal_link_resolves(name):
    html = page(name)
    broken = []
    for ref in attr(html, r'href="([^"]+)"'):
        ref = unescape(ref)
        m = LOCAL.match(ref)
        if not m:
            continue
        target = (SITE / name).parent / m.group(1)
        if not target.exists():
            broken.append(ref)
    assert not broken, f"{name} has {len(broken)} broken local links: {sorted(set(broken))[:8]}"


@pytest.mark.parametrize("name", PAGES)
def test_every_image_says_what_it_is(name):
    html = page(name)
    missing = [tag for tag in attr(html, r"<img[^>]*>") if 'alt="' not in tag]
    assert not missing, f"{name} has {len(missing)} images with no alt"


@pytest.mark.parametrize("name", PAGES)
def test_every_page_has_one_heading(name):
    html = page(name)
    h1 = re.findall(r"<h1[\s>]", html)
    assert len(h1) == 1, f"{name} has {len(h1)} h1 elements"


@pytest.mark.parametrize("name", PAGES)
def test_every_page_describes_itself_once(name):
    html = page(name)
    desc = attr(html, r'<meta name="description" content="([^"]*)"')
    assert len(desc) == 1, f"{name} has {len(desc)} meta descriptions"
    assert len(desc[0]) >= 10, f"{name} description is only {len(desc[0])} chars"


@pytest.mark.parametrize("name", PAGES)
def test_description_fits_in_a_search_result(name):
    # 160 is where Google truncates. this is a real limit, not a style preference,
    # so a failing page is a page whose words will be cut off in the index.
    desc = attr(page(name), r'<meta name="description" content="([^"]*)"')[0]
    assert len(desc) <= 160, f"{name} description is {len(desc)} chars, {len(desc) - 160} over"


def test_descriptions_are_not_copied_between_pages():
    seen = {}
    for name in PAGES:
        desc = attr(page(name), r'<meta name="description" content="([^"]*)"')[0]
        assert desc not in seen, f"{name} reuses the description of {seen[desc]}"
        seen[desc] = name


@pytest.mark.parametrize("name", PAGES)
def test_canonical_and_og_url_agree(name):
    html = page(name)
    canonical = attr(html, r'<link rel="canonical" href="([^"]+)"')
    og = attr(html, r'<meta property="og:url" content="([^"]+)"')
    assert len(canonical) == 1, f"{name} has {len(canonical)} canonical links"
    assert canonical == og, f"{name} canonical {canonical} disagrees with og:url {og}"


@pytest.mark.parametrize("name", PAGES)
def test_language_attribute_matches_the_path(name):
    html = page(name)
    lang = attr(html, r'<html[^>]*lang="([^"]+)"')[0]
    expected = "th" if name.startswith("th/") else "en"
    assert lang.startswith(expected), f"{name} declares lang={lang}"


def test_the_thai_page_is_actually_thai():
    html = page("th/index.html")
    thai = len(re.findall(r"[\u0e00-\u0e7f]", html))
    assert thai > 500, f"the Thai page carries only {thai} Thai characters"
