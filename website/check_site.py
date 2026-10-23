#!/usr/bin/env python3
"""Check generated static pages for missing local files and fragment targets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re


ARCHIVED_DEMO_DOCUMENTS = {
    'petstore/docs/technical-services.md',
    'petstore/docs/reservation-failure-handling.md',
    'petstore/docs/regression-2026-10-12-conserved-transfers.md',
    'petstore/docs/quantum-opening-recovery.md',
    'petstore/docs/known-issues.md',
    'bank-deposit/docs/latest-refactoring-verification.md',
    'bank-deposit/docs/web-workbench.md',
    'bank-deposit/docs/completion-audit.md',
    'bank-deposit/docs/legacy-entry-migration.md',
    'bank-deposit/docs/known-issues-latest.md',
    'bank-deposit/docs/source-map.md',
    'petstore/docs/transaction-boundary-audit.md',
}
ALLOWED_GITHUB_PATHS = {
    '/lidonge/spp-basic',
    '/lidonge/spp-basic/tree/main/examples',
    '/lidonge/spp-examples',
} | {
    '/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/' + document
    for document in ARCHIVED_DEMO_DOCUMENTS
}


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.targets = set(), []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.targets.append(attrs[attr])


root = Path(__file__).resolve().parent / 'dist'
verification_files = {p for p in root.glob('google*.html')
                      if re.fullmatch(r'google[0-9a-f]+\.html', p.name)
                      and p.read_text().strip() == f'google-site-verification: {p.name}'}
pages = {p: Links(p.read_text()) for p in root.rglob('*.html') if p not in verification_files}
errors = []
checked = 0
for page, parsed in pages.items():
    text = page.read_text()
    relative = '/' + page.relative_to(root).as_posix()
    if relative.endswith('index.html'):
        relative = relative[:-len('index.html')]
    canonical = re.findall(r'<link rel="canonical" href="([^"]+)"', text)
    if canonical != ['https://us.servpp.top' + relative]:
        errors.append(f'{page.relative_to(root)}: missing, duplicate or incorrect canonical URL')
    for pattern, label in [(r'<title>[^<]+</title>', 'title'),
                           (r'<meta name="description" content="[^"]+"', 'description'),
                           (r'<meta property="og:title" content="[^"]+"', 'sharing title'),
                           (r'<meta property="og:description" content="[^"]+"', 'sharing description')]:
        if len(re.findall(pattern, text)) != 1:
            errors.append(f'{page.relative_to(root)}: expected one nonempty {label}')
    for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
        try:
            data = json.loads(payload)
            if data.get('@type') == 'WebSite' and 'ServPP' not in data.get('alternateName', []):
                errors.append('Homepage structured data must include the ServPP alternate name')
        except ValueError:
            errors.append(f'{page.relative_to(root)}: invalid structured JSON')
    navigation = re.search(r'<nav aria-label="Main navigation">(.*?)</nav>', text, re.S)
    if navigation:
        for destination in ('https://platform.servpp.top/login', 'https://github.com/lidonge/spp-basic'):
            if f'href="{destination}"' not in navigation.group(1):
                errors.append(f'{page.relative_to(root)}: missing platform or basic source navigation')
    if page == root / 'index.html':
        if not navigation or '<a href="https://github.com/lidonge/spp-basic/tree/main/examples">Source</a>' not in navigation.group(1):
            errors.append('Homepage Source navigation must open the public examples repository directly')
        if 'https://github.com/lidonge/spp-examples' not in parsed.targets:
            errors.append('Homepage must link to the public examples repository')
        if 'Public platform registration is not open yet.' not in text:
            errors.append('Homepage must disclose the current registration availability')
    for href in parsed.targets:
        link = urlsplit(href)
        if link.hostname and link.hostname.lower() in {'github.com', 'www.github.com', 'raw.githubusercontent.com'}:
            if link.hostname.lower() != 'github.com' or link.path.rstrip('/') not in ALLOWED_GITHUB_PATHS:
                errors.append(f'{page.relative_to(root)}: unapproved GitHub repository link: {href}')
        if link.scheme or link.netloc:
            continue
        if not link.path:
            target = page
        elif link.path.startswith('/'):
            target = root / unquote(link.path).lstrip('/')
        else:
            target = (page.parent / unquote(link.path)).resolve()
        if target.is_dir():
            target = target / 'index.html'
        checked += 1
        if not target.is_file():
            errors.append(f'{page.relative_to(root)}: missing {href}')
        elif link.fragment and target in pages and unquote(link.fragment) not in pages[target].ids:
            errors.append(f'{page.relative_to(root)}: missing fragment {href}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Checked {len(pages)} pages and {checked} local links/resources; no missing targets.')
