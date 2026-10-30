#!/usr/bin/env python3
"""Build the book companion site. Python 3.9+; no third-party packages."""

from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "docs"
CATALOG = ROOT / "data" / "catalog.json"


def e(value):
    return escape(str(value or ""), quote=True)


def checked_url(value):
    if value and urlsplit(value).scheme not in ("http", "https"):
        raise ValueError(f"Expected a public http(s) URL: {value}")
    return value


def source_host(url):
    return urlsplit(url).netloc.removeprefix("www.")


def valid_resources(chapter, kind):
    return [resource for resource in chapter.get(kind, []) if resource.get("url")]


def resource_count(chapter):
    return sum(len(valid_resources(chapter, key)) for key in ("repositories", "papers", "otherResources"))


def chapter_path(chapter):
    return f"chapters/{chapter['slug']}/"


def author_string(authors):
    if isinstance(authors, list):
        return ", ".join(author.get("name", "") if isinstance(author, dict) else str(author) for author in authors)
    return str(authors or "")


def external_link(url, label, css=""):
    return f'<a href="{e(checked_url(url))}"{f" class={chr(34)}{css}{chr(34)}" if css else ""}>{label}<span class="external-arrow" aria-hidden="true">↗</span></a>'


def paper_details(paper):
    return " · ".join(e(item) for item in (author_string(paper.get("authors", "")), paper.get("year", "")) if item)


def relationship_label(resource):
    labels = {
        "chapter-experiments": "Chapter experiments",
        "source-paper-experiments": "Source paper experiments",
        "related-software": "Related software",
        "related-course": "Related course",
        "related-experiments": "Related experiments",
    }
    value = resource.get("relationship", "")
    return labels.get(value, value.replace("-", " ").capitalize())


def header(base, active=""):
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header container">
  <a class="brand" href="{base}" aria-label="Bayesian Adversarial Machine Learning home"><span class="brand-mark" aria-hidden="true">BAML</span><span class="brand-name">The book<br>companion</span></a>
  <nav class="primary-nav" aria-label="Main navigation">
    <a href="{base}#chapters">Chapters</a>
    <a href="{base}resources/"{' aria-current="page"' if active == 'resources' else ''}>Resources</a>
    {external_link(f"https://github.com/{BOOK['organization']}", 'GitHub')}
  </nav>
</header>'''


def footer(base):
    return f'''<footer class="site-footer container">
  <div><span class="footer-title">{e(BOOK['title'])}</span>A companion to the book by Roi Naveiro and David Ríos Insua.</div>
  <nav class="footer-links" aria-label="Footer navigation"><a href="{base}#chapters">Chapters</a><a href="{base}resources/">Resources</a>{external_link(BOOK['repositoryUrl'] + '/issues', 'Suggest a correction')}</nav>
</footer>'''


def page(title, description, content, path="", depth=0, active=""):
    base = "../" * depth or "./"
    full_title = BOOK["title"] if not title else f"{title} — {BOOK['title']}"
    canonical = BOOK["siteUrl"].rstrip("/") + "/" + path
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(full_title)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#f8f7f2">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(full_title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(canonical)}">
  <meta name="twitter:card" content="summary">
  <link rel="canonical" href="{e(canonical)}">
  <link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{base}assets/site.css">
  <script src="{base}assets/site.js" defer></script>
</head>
<body>
{header(base, active)}
{content}
{footer(base)}
</body>
</html>
'''


def home():
    authors = ' <span aria-hidden="true">&amp;</span> '.join(
        f'<a href="{e(checked_url(author["url"]))}">{e(author["name"])}</a>' if author.get("url") else e(author["name"])
        for author in BOOK["authors"]
    )
    artwork = BOOK.get("coverImage") or "assets/cover-study.svg"
    alt = BOOK.get("coverAlt") or "An abstract study of uncertainty: blue contours surround an observation and its perturbed counterpart."
    caption = BOOK.get("coverCaption", "")
    artwork_width = int(BOOK.get("coverWidth", 560))
    artwork_height = int(BOOK.get("coverHeight", 640))
    rows = []
    for chapter in CHAPTERS:
        count = resource_count(chapter)
        count_label = f"{count} resource{'s' if count != 1 else ''}" if count else ""
        topics = " · ".join(chapter.get("topics", [])[:3])
        rows.append(f'''<a class="chapter-row" href="{chapter_path(chapter)}">
  <span class="chapter-number">{int(chapter['number']):02}</span>
  <span><span class="chapter-name">{e(chapter['title'])}</span><span class="chapter-topics">{e(topics)}</span></span>
  <span class="chapter-meta">{count_label}</span><span class="row-arrow" aria-hidden="true">↗</span>
</a>''')
    return page("", BOOK["description"], f'''<main id="main" class="container">
<section class="hero" aria-labelledby="book-title">
  <div class="hero-copy"><p class="eyebrow">Code, experiments &amp; further reading</p>
    <h1 id="book-title">Bayesian<br><em>Adversarial</em><br>Machine Learning</h1>
    <p class="authors">{authors}</p>
    <p class="hero-description">{e(BOOK['description'])}</p>
    <div class="hero-actions"><a class="button" href="#chapters">Chapters <span aria-hidden="true">↓</span></a><a class="text-link" href="resources/">Code &amp; papers <span aria-hidden="true">↗</span></a></div>
  </div>
  <figure class="hero-art"><img src="{e(artwork)}" width="{artwork_width}" height="{artwork_height}" alt="{e(alt)}" fetchpriority="high" decoding="async">{f'<figcaption>{e(caption)}</figcaption>' if caption else ''}</figure>
</section>
<section class="chapters-section" id="chapters" aria-labelledby="chapters-heading">
  <div class="section-heading"><h2 id="chapters-heading">Chapters</h2><span class="subtle">{len(CHAPTERS):02} chapters</span></div>
  <div class="chapter-list">{''.join(rows)}</div>
</section>
<section class="about-band" aria-labelledby="about-heading"><h2 id="about-heading">About the resources</h2><div><p>The lists include code for chapter examples and experiments, related software, and papers.</p><p><a href="{e(BOOK['repositoryUrl'])}/issues">Suggest a resource or correction</a>.</p></div></section>
</main>''')


def resource_item(resource, paper=False):
    title = resource["title"] if paper else resource["name"]
    meta = f'<p class="resource-meta">{paper_details(resource)}</p>' if paper else ""
    description = resource.get("description", "")
    relationship = relationship_label(resource) if not paper else ""
    detail = " · ".join(item for item in (relationship, source_host(resource['url'])) if item)
    return f'''<article class="resource-item"><h3>{external_link(resource['url'], e(title))}</h3>{meta}{f'<p>{e(description)}</p>' if description else ''}<span class="resource-host">{e(detail)}</span></article>'''


def chapter_page(chapter, index):
    topics = "".join(f"<li>{e(topic)}</li>" for topic in chapter.get("topics", []))
    sections = []
    for kind, heading in (("repositories", "Code & experiments"), ("papers", "Related papers"), ("otherResources", "Further resources")):
        resources = valid_resources(chapter, kind)
        if not resources:
            continue
        body = "".join(resource_item(resource, paper=kind == "papers") for resource in resources)
        sections.append(f'<section class="resource-section"><h2>{heading}</h2>{body}</section>')
    illustration = ""
    if chapter.get("image"):
        image_path = chapter["image"]
        src = image_path if urlsplit(image_path).scheme else "../../" + image_path.lstrip("/")
        caption = f"<figcaption>{e(chapter['imageCaption'])}</figcaption>" if chapter.get("imageCaption") else ""
        illustration = f'<figure class="chapter-image"><img src="{e(src)}" alt="{e(chapter.get("imageAlt", ""))}" loading="lazy">{caption}</figure>'
    pagination = []
    for offset, label, css in ((-1, "Previous chapter", "previous"), (1, "Next chapter", "next")):
        other = index + offset
        if 0 <= other < len(CHAPTERS):
            target = CHAPTERS[other]
            pagination.append(f'<a class="{css}" href="../{e(target["slug"])}/"><span>{label} · {int(target["number"]):02}</span><strong>{e(target["title"])}</strong></a>')
        else:
            pagination.append('<div aria-hidden="true"></div>')
    browse_link = f'<a class="sidebar-link" href="../../resources/?chapter={chapter["number"]}">Browse these resources <span aria-hidden="true">↗</span></a>' if resource_count(chapter) else ""
    content = f'''<main id="main" class="container">
<div class="page-heading"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../../">Home</a><span aria-hidden="true">/</span><a href="../../#chapters">Chapters</a></nav><p class="eyebrow">Chapter {int(chapter['number']):02}</p><h1>{e(chapter['title'])}</h1><p class="page-lead">{e(chapter['summary'])}</p></div>
<div class="chapter-layout"><aside class="chapter-sidebar" aria-label="Chapter topics"><h2 class="eyebrow">In this chapter</h2><ul class="topic-list">{topics}</ul>{browse_link}</aside><div class="chapter-content">{illustration}{''.join(sections)}</div></div>
<nav class="chapter-pagination" aria-label="Adjacent chapters">{''.join(pagination)}</nav>
</main>'''
    return page(f"Chapter {chapter['number']}: {chapter['title']}", chapter["summary"], content, chapter_path(chapter), 2)


def resources_page():
    options = '<option value="">All chapters</option>' + "".join(
        f'<option value="{chapter["number"]}">{int(chapter["number"]):02} — {e(chapter["title"])}</option>' for chapter in CHAPTERS
    )
    rows = []
    for chapter in CHAPTERS:
        for kind, label, type_key in (("repositories", "Code", "code"), ("papers", "Paper", "papers"), ("otherResources", "Resource", "other")):
            for resource in valid_resources(chapter, kind):
                title = resource["title"] if kind == "papers" else resource["name"]
                details = paper_details(resource) if kind == "papers" else e(resource.get("description", ""))
                relationship = relationship_label(resource) if kind == "repositories" else ""
                label_detail = f'<p class="resource-meta">{e(relationship)}</p>' if relationship else ""
                rows.append(f'''<article class="catalogue-row" data-resource data-type="{type_key}" data-chapter="{chapter['number']}">
  <div class="catalogue-tag">{label}<a href="../{chapter_path(chapter)}"><span>Chapter {int(chapter['number']):02}</span></a></div>
  <div><h2>{external_link(resource['url'], e(title))}</h2>{f'<p>{details}</p>' if details else ''}{label_detail}<p class="resource-meta">{e(chapter['title'])}</p></div>
  <span class="row-arrow" aria-hidden="true">↗</span>
</article>''')
    content = f'''<main id="main" class="container">
<div class="page-heading"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a><span aria-hidden="true">/</span><span>Resources</span></nav><h1>Code &amp; further reading</h1><p class="page-lead">Code, papers, and other resources organized by chapter. Search by title, author, or topic.</p></div>
<section aria-label="Resource catalogue">
<div class="resource-controls"><label><span class="control-label">Search the resources</span><input class="search-input" type="search" placeholder="Title, author, or topic" data-resource-search aria-controls="resource-results"></label><label><span class="control-label">Chapter</span><select class="chapter-select" data-chapter-filter aria-controls="resource-results">{options}</select></label></div>
<div class="filter-bar"><div class="filter-buttons" role="group" aria-label="Resource type"><button class="filter-button" type="button" data-type-filter="all" aria-pressed="true">All</button><button class="filter-button" type="button" data-type-filter="code" aria-pressed="false">Code</button><button class="filter-button" type="button" data-type-filter="papers" aria-pressed="false">Papers</button></div><span class="result-count" data-result-count role="status" aria-live="polite">{len(rows)} resources</span></div>
<noscript><p>All resources are listed below. Enable JavaScript to use search and filters.</p></noscript>
<div class="resource-catalogue" id="resource-results">{''.join(rows)}<p class="empty-state" data-empty-state hidden>No resources match these filters. Try another term or select all chapters.</p></div>
</section><p class="resource-note">Resources relevant to several chapters appear in each chapter’s list.</p>
</main>'''
    return page("Resources", "Code repositories, reproducible experiments, and related papers for every chapter of Bayesian Adversarial Machine Learning.", content, "resources/", 1, "resources")


def validate():
    if not CHAPTERS:
        raise ValueError("The catalogue needs at least one chapter")
    slugs = set()
    numbers = set()
    for chapter in CHAPTERS:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", chapter["slug"]):
            raise ValueError(f"Invalid chapter slug: {chapter['slug']}")
        if chapter["slug"] in slugs or chapter["number"] in numbers:
            raise ValueError("Chapter slugs and numbers must be unique")
        slugs.add(chapter["slug"])
        numbers.add(chapter["number"])
        for kind in ("repositories", "papers", "otherResources"):
            for resource in chapter.get(kind, []):
                checked_url(resource.get("url", ""))
    checked_url(BOOK["siteUrl"])
    checked_url(BOOK["repositoryUrl"])


def write(relative_path, content):
    destination = OUTPUT / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build():
    validate()
    OUTPUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "assets", OUTPUT / "assets", dirs_exist_ok=True)
    write("index.html", home())
    for index, chapter in enumerate(CHAPTERS):
        write(chapter_path(chapter) + "index.html", chapter_page(chapter, index))
    write("resources/index.html", resources_page())
    not_found = f'<main id="main" class="container not-found"><p class="eyebrow">404</p><h1>Page not found</h1><p>This page may have moved or the link may be incorrect.</p><a class="button" href="{e(BOOK["siteUrl"])}#chapters">Chapters <span aria-hidden="true">↗</span></a></main>'
    # GitHub serves this document at arbitrary paths, so its assets and navigation use absolute URLs.
    error = page("Page not found", "Return to the book’s chapters and supporting resources.", not_found, "404.html")
    error = error.replace('href="./', f'href="{e(BOOK["siteUrl"].rstrip("/"))}/').replace('src="./', f'src="{e(BOOK["siteUrl"].rstrip("/"))}/')
    write("404.html", error)
    urls = [BOOK["siteUrl"].rstrip("/") + "/" + path for path in ["", "resources/"] + [chapter_path(chapter) for chapter in CHAPTERS]]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{e(url)}</loc></url>\n" for url in urls) + '</urlset>\n'
    write("sitemap.xml", sitemap)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BOOK['siteUrl'].rstrip('/')}/sitemap.xml\n")
    write(".nojekyll", "")
    print(f"Built {len(CHAPTERS)} chapter pages and {sum(resource_count(chapter) for chapter in CHAPTERS)} resource entries in {OUTPUT}")


if __name__ == "__main__":
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    BOOK, CHAPTERS = data["book"], data["chapters"]
    build()
