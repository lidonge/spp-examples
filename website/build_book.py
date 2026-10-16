#!/usr/bin/env python3
"""Render only the English book; keep unpublished repository references offline."""
from pathlib import Path
import argparse
import html
import json
import re
from urllib.parse import unquote, urlsplit
import shutil
import zipfile
import xml.etree.ElementTree as ET

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


BASE = Path(__file__).resolve().parent
BOOK_COPYRIGHT_URL = 'https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md'


def page_url(relative):
    relative = Path(relative)
    if relative.name == 'README.md':
        suffix = relative.parent.as_posix()
        return '/book/' if suffix == '.' else f'/book/{suffix}/'
    return f'/book/{relative.with_suffix("").as_posix()}/'


class PublicLinks(Treeprocessor):
    def run(self, root):
        for node in root.iter('a'):
            href = node.get('href', '')
            if href == BOOK_COPYRIGHT_URL:
                node.set('href', '/book/copyright/')
                continue
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (self.md.source.parent / unquote(parsed.path)).resolve()
            if target in self.md.pages:
                node.set('href', self.md.pages[target] + ('#' + parsed.fragment if parsed.fragment else ''))
            else:
                # References identify evidence without publishing additional private files.
                self.md.repository_references += 1
                node.tag = 'span'
                node.attrib.clear()
                node.set('class', 'repository-reference')
                node.set('title', f'Repository reference (not published here): {unquote(href)}')
        return root


class PublicLinksExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(PublicLinks(md), 'public_links', 5)


def title_of(path):
    return re.search(r'^# (.+)$', path.read_text(), re.M).group(1)


def header(section='book'):
    markup = '''<header class="topbar"><a href="/" class="wordmark" aria-label="S++ home"><span class="mark">S<span>++</span></span><span class="wordmark-divider"></span><span class="wordmark-sub">Business systems language</span></a><nav aria-label="Main navigation"><a href="/">Home</a><a href="/examples/">Examples</a><a href="/guide/">Guide</a><a href="/book/">Book</a><a href="/sources/">Source</a><a class="nav-contact" href="/#contact">Get in touch ↗</a></nav><button class="menu-toggle" aria-label="Open menu" aria-expanded="false">Menu ☰</button></header>'''
    markup = markup.replace('<a href="/sources/">Source</a>', '<a href="/sources/">Source</a><a href="/articles/">Articles</a>')
    return markup.replace(f'href="/{section}/"', f'href="/{section}/" aria-current="page"')


def article_entries():
    return json.loads((BASE / 'articles.json').read_text())


def build_articles(output):
    """Render original introductory articles from their maintained Markdown sources."""
    entries = article_entries()
    sidebar = '<a class="book-index" href="/articles/">All articles</a>' + ''.join(
        f'<a class="toc-link" href="/articles/{entry["slug"]}/">{html.escape(entry["title"])}</a>'
        for entry in entries
    )
    cards = []
    for entry in entries:
        url = f'/articles/{entry["slug"]}/'
        text = (BASE / 'articles' / entry['file']).read_text()
        body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc'])
        cards.append(f'<h2><a href="{url}">{html.escape(entry["title"])}</a></h2><p>{html.escape(entry["description"])}</p>')
        article_page(output, url, entry['title'], body, sidebar, entry['date'])
    body = '<h1>Articles on business modeling and role-oriented programming</h1><p>Practical introductions to S++ (ServPP), grounded in the Petstore and bank-deposit demonstrations. Explore participants, business facts and transaction boundaries, then follow links to the actual source.</p>' + ''.join(cards)
    article_page(output, '/articles/', 'Business Modeling and Role-Oriented Programming Articles', body, sidebar)


def article_page(output, url, title, body, sidebar, published=None):
    date = f'<time datetime="{published}">Published {published}</time>' if published else 'PRACTICAL INTRODUCTIONS'
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | S++ (ServPP)</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/book.css"><script src="/site.js" defer></script></head><body class="book-page">{header('articles')}<div class="book-layout"><aside class="book-sidebar"><nav aria-label="Articles">{sidebar}</nav></aside><main id="main-content"><div class="book-meta"><span>S++ (SERVPP) · {date}</span><a href="/guide/">Language guide</a></div><article class="book-article">{body}</article><footer class="book-footer"><a href="/articles/">All articles</a><a href="/examples/">Working examples</a><a href="mailto:hello@servpp.top">Discuss an evaluation</a></footer></main></div></body></html>'''
    target = output / url.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document)


def build_sources(repo, docs_repo, output):
    """Publish the source-language demo files, without build products or credentials."""
    mapping = {}
    summaries = []
    for demo, directory, label in [('petstore-demo', 'demos/petstore', 'Petstore'), ('xbod-deposit-demo', 'demos/bank-deposit', 'Bank deposit')]:
        root = repo / directory / 'src/main/spp'
        files = sorted(p for p in root.rglob('*') if p.suffix in {'.spp', '.app', '.phy', '.enum'})
        urls = {path: f'/sources/{demo}/{path.relative_to(root).as_posix()}/' for path in files}
        for path, url in urls.items():
            mapping[path.resolve()] = url
            mapping[(docs_repo / path.relative_to(repo)).resolve()] = url
        # Directory references in the manuscript open the demo's source overview.
        mapping[root.resolve()] = f'/sources/{demo}/'
        for directory in {p.parent for p in files}:
            mapping[directory.resolve()] = f'/sources/{demo}/#' + directory.relative_to(root).as_posix().replace('/', '-')
            mapping[(docs_repo / directory.relative_to(repo)).resolve()] = mapping[directory.resolve()]
        mapping[(docs_repo / root.relative_to(repo)).resolve()] = f'/sources/{demo}/'
        groups = {}
        for path in files:
            groups.setdefault(path.parent.relative_to(root).as_posix(), []).append(path)
        sidebar = ['<a class="book-index" href="/sources/">All demo sources</a>', '<label class="toc-search">Find a source file<input type="search" id="chapter-search" placeholder="Search filenames" autocomplete="off"></label>']
        overview = []
        for group, members in groups.items():
            sidebar.append(f'<span class="toc-part">{html.escape(group)}</span>')
            overview.append(f'<h2 id="{group.replace("/", "-")}">{html.escape(group)}</h2><ul>')
            for path in members:
                sidebar.append(f'<a class="toc-link" data-title="{html.escape(str(path.relative_to(root)).lower(), quote=True)}" href="{urls[path]}">{html.escape(path.name)}</a>')
                overview.append(f'<li><a href="{urls[path]}">{html.escape(path.name)}</a></li>')
            overview.append('</ul>')
        sidebar.append('<p id="chapter-search-empty" hidden>No matching files.</p>')
        archive = output / 'sources/downloads' / f'{demo}.zip'
        archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in files:
                bundle.write(path, f'{directory}/src/main/spp/{path.relative_to(root)}')
        overview_body = f'<h1>{label} source</h1><p>{len(files)} source files, organized by business domain and function. The download contains SPP, APP, PHY and enum definitions.</p><p><a href="/sources/downloads/{demo}.zip" download>Download {label} source ZIP</a></p>' + ''.join(overview)
        source_page(output, f'/sources/{demo}/', f'{label} source', overview_body, ''.join(sidebar))
        for path in files:
            relative = path.relative_to(root)
            raw_url = f'/sources/downloads/{demo}/{relative.as_posix()}'
            raw = output / raw_url.lstrip('/')
            raw.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, raw)
            lines = ''.join(f'<span class="source-line" id="L{i}"><a class="line-number" href="#L{i}" aria-label="Line {i}">{i}</a><code>{html.escape(line)}</code></span>' for i, line in enumerate(path.read_text().splitlines(), 1))
            body = f'<h1 class="source-title">{html.escape(path.name)}</h1><p class="source-path">{html.escape(str(relative))}</p><p><a href="{raw_url}" download>Download original file</a> · <a href="/sources/{demo}/">{label} source contents</a></p><pre class="source-code">{lines}</pre>'
            nav = ''.join(sidebar).replace(f'href="{urls[path]}"', f'href="{urls[path]}" aria-current="page"')
            source_page(output, urls[path], f'{path.name} · {relative.parent} · {label}', body, nav)
        summaries.append(f'<h2><a href="/sources/{demo}/">{label}</a></h2><p>{len(files)} files · <a href="/sources/{demo}/">Browse online</a> · <a href="/sources/downloads/{demo}.zip" download>Download ZIP</a></p>')
        print(f'Built {len(files)} {label} source pages')
    source_page(output, '/sources/', 'Demo source', '<h1>Read the demo source</h1><p>Explore the business models and scenarios alongside their application and physical configuration. These are the current source-language files from the two demonstrations.</p>' + ''.join(summaries), '<a class="book-index" href="/book/">Read the English book</a><a class="book-index" href="/sources/petstore-demo/">Petstore</a><a class="book-index" href="/sources/xbod-deposit-demo/">Bank deposit</a>')
    return mapping


def source_page(output, url, title, body, sidebar):
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — S++ source</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/book.css"><script src="/site.js" defer></script><script src="/book.js" defer></script></head><body class="book-page">{header('sources')}<div class="book-layout"><aside class="book-sidebar"><details class="book-toc" open><summary>Source contents</summary><nav aria-label="Source files">{sidebar}</nav></details></aside><main><div class="book-meta"><span>DEMO SOURCE · SPP / APP / PHY</span><a href="/book/">Read the book</a></div><article class="book-article">{body}</article><footer class="book-footer"><a href="/sources/">All demo sources</a><a href="/">S++ home</a></footer></main></div></body></html>'''
    target = output / url.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document)


def build(source, output):
    source = source.resolve()
    shutil.copytree(BASE / 'static', output, dirs_exist_ok=True)
    files = sorted(source.rglob('*.md'))
    pages = {path: page_url(path.relative_to(source)) for path in files}
    copyright_page = BASE.parent / 'book/COPYRIGHT.md'
    files.append(copyright_page.resolve())
    pages[copyright_page.resolve()] = '/book/copyright/'
    pages.update(build_sources(BASE.parent, source.parent.parent.parent, output))
    # The translation map is the author's deliberate reading order, rather than filename order.
    entries = json.loads((source / 'translation-map.json').read_text())['sections']
    order = [source / entry['english'] for entry in entries]
    sidebar = ['<a class="book-index" href="/book/">Full book contents</a>']
    for path in order:
        title = title_of(path)
        group = path.name == 'README.md'
        sidebar.append(f'<a class="toc-link {"toc-part" if group else "toc-chapter"}" href="{pages[path]}" data-title="{html.escape(title.lower(), quote=True)}">{html.escape(title)}</a>')
    sidebar.append('<a class="book-index" href="/book/complete-manuscript/">Read the complete book</a>')
    for path in files:
        text = path.read_text()
        if path == source / 'README.md':
            text = re.sub(r'\n\[Chinese Edition\]\([^\n]+\)\n', '\n', text)
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', PublicLinksExtension()], extension_configs={'toc': {'permalink': '¶'}})
        md.source = path
        md.pages = pages
        md.repository_references = 0
        body = md.convert(text)
        title = title_of(path)
        if path == source / 'complete-manuscript.md':
            title += ' — Complete English Book'
        note = ''
        if md.repository_references:
            note = '<aside class="book-reference-note">Underlined repository references identify supporting engineering records outside this published English edition. Hover over a reference to see its original path. Demo source files are available in the <a href="/sources/">source browser</a>.</aside>'
        nav = ''.join(sidebar).replace(f'href="{pages[path]}"', f'href="{pages[path]}" aria-current="page"')
        quicklinks = '<a href="/book/">Contents</a><a href="/book/complete-manuscript/">Complete book</a>'
        document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html.escape(title, quote=True)} — S++ modeling, language mechanisms and engineering practice."><title>{html.escape(title)} — S++</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/book.css"><script src="/site.js" defer></script><script src="/book.js" defer></script></head>
<body class="book-page">{header()}<div class="book-layout"><aside class="book-sidebar"><details class="book-toc" open><summary>Book contents</summary><nav aria-label="Book contents"><label class="toc-search">Find a chapter<input type="search" id="chapter-search" placeholder="Search chapter titles" autocomplete="off"></label>{nav}<p id="chapter-search-empty" hidden>No matching chapters.</p></nav></details></aside><main id="main-content"><div class="book-meta"><span>ENGLISH EDITION · OCTOBER 15, 2026</span><div>{quicklinks}</div></div><article class="book-article">{body}</article>{note}<footer class="book-footer"><a href="/book/">← Book contents</a><a href="/">S++ home</a><a href="mailto:hello@servpp.top">Get in touch</a><a href="/book/copyright/">Book: all rights reserved</a></footer></main></div></body></html>'''
        target = output / pages[path].lstrip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document)
    print(f'Built {len(files)} English book pages from {source}')
    build_articles(output)
    build_search_assets(output)


def build_search_assets(output):
    """Provide canonical page URLs and a sitemap for public search discovery."""
    origin = 'https://us.servpp.top'
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.Element(f'{{{namespace}}}urlset')
    articles = {f'/articles/{entry["slug"]}/': entry for entry in article_entries()}
    descriptions = {
        '/': 'S++ (ServPP) is an experimental role-oriented language for business systems. Explore explicit participants, services and transactions through working demos.',
        '/guide/': 'Learn how S++ (ServPP) separates business models, roles, checks and scenarios from deployment and physical implementation using SPP, APP and PHY.',
        '/examples/': 'Explore S++ (ServPP) business modeling through Petstore ordering, payment and returns, and selected banking deposit and reversal transactions.',
        '/articles/': 'Practical articles on business modeling, role-oriented programming and business transaction boundaries with S++ (ServPP) examples and source.',
        '/sources/': 'Browse S++ (ServPP) Petstore and bank-deposit business models, scenarios and APP/PHY configurations online, organized by domain and function.',
    }
    for path in sorted(output.rglob('*.html')):
        relative = '/' + path.relative_to(output).as_posix()
        if relative.endswith('index.html'):
            relative = relative[:-len('index.html')]
        canonical = origin + relative
        text = re.sub(r'<link\s+rel="canonical"[^>]*>', '', path.read_text())
        title = html.unescape(re.search(r'<title>(.*?)</title>', text, re.S).group(1))
        existing = re.search(r'<meta name="description" content="([^"]*)"', text)
        entry = articles.get(relative)
        description = descriptions.get(relative) or (entry['description'] if entry else None)
        description = description or (html.unescape(existing.group(1)) if existing else f'{title}. Read the S++ (ServPP) business-language source and related examples.')
        text = re.sub(r'<meta name="description"[^>]*>', '', text)
        text = re.sub(r'<meta (?:property="og:[^"]+"|name="twitter:[^"]+")[^>]*>', '', text)
        text = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
        metadata = f'<link rel="canonical" href="{html.escape(canonical, quote=True)}"><meta name="description" content="{html.escape(description, quote=True)}">'
        for key, value in {'og:site_name': 'S++ (ServPP)', 'og:type': 'article' if entry else 'website', 'og:title': title, 'og:description': description, 'og:url': canonical, 'og:locale': 'en_US'}.items():
            metadata += f'<meta property="{key}" content="{html.escape(value, quote=True)}">'
        metadata += '<meta name="twitter:card" content="summary">'
        metadata += f'<meta name="twitter:title" content="{html.escape(title, quote=True)}"><meta name="twitter:description" content="{html.escape(description, quote=True)}">'
        structured = None
        if relative == '/':
            structured = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'S++', 'alternateName': ['ServPP', 'S++ (ServPP)'], 'url': origin + '/', 'inLanguage': 'en'}
        elif entry:
            structured = {'@context': 'https://schema.org', '@type': 'Article', 'headline': entry['title'], 'description': description, 'datePublished': entry['date'], 'inLanguage': 'en', 'mainEntityOfPage': canonical, 'author': {'@type': 'Organization', 'name': 'S++ project', 'url': origin + '/'}}
        if structured:
            metadata += '<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
        text = text.replace('</head>', metadata + '</head>')
        path.write_text(text)
        node = ET.SubElement(sitemap, f'{{{namespace}}}url')
        ET.SubElement(node, f'{{{namespace}}}loc').text = canonical
    ET.indent(sitemap, space='  ')
    ET.ElementTree(sitemap).write(output / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (output / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /sources/downloads/\n\nSitemap: {origin}/sitemap.xml\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=BASE.parent / 'book/en')
    parser.add_argument('--output', type=Path, default=BASE / 'dist')
    args = parser.parse_args()
    build(args.source, args.output)
