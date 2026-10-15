#!/usr/bin/env python3
"""Check generated static pages for missing local files and fragment targets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote


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
pages = {p: Links(p.read_text()) for p in root.rglob('*.html')}
errors = []
checked = 0
for page, parsed in pages.items():
    for href in parsed.targets:
        link = urlsplit(href)
        if link.hostname and link.hostname.lower() in {'github.com', 'www.github.com', 'raw.githubusercontent.com'}:
            errors.append(f'{page.relative_to(root)}: GitHub link must not be published: {href}')
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
