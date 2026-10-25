"""Publish the pinned, allowlisted SDK documentation and runnable sample inputs."""
import hashlib
import html
import json
import shutil
import zipfile

import markdown


DOCUMENTS = {
    'docs/tutorial/spp-tutorial.md': '/tutorial/',
    'sdk-tools/docs/user-guide.md': '/sdk/user-guide/',
    'sdk-tools/docs/builtin-technical-services.md': '/sdk/technical-services/',
    'sdk-tools/docs/tutorial-validation.md': '/sdk/validation/',
    'sdk-tools/samples/tutorial/README.md': '/tutorial/samples/first-scenario/',
    'sdk-tools/samples/custom-services/README.md': '/tutorial/samples/custom-services/',
}


def build_manuals(base, output, header, links_extension):
    root = base / 'manuals/inputs'
    provenance = json.loads((base / 'manuals/upstream.json').read_text())
    paths = [root / entry['path'] for entry in provenance['files']]
    # Fail closed if the imported documentation differs from the reviewed revision.
    for entry, path in zip(provenance['files'], paths):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
    commercial_root = base / 'manuals/commercial'
    commercial_provenance = json.loads((commercial_root / 'upstream.json').read_text())
    commercial_path = commercial_root / 'communication-services.md'
    assert commercial_provenance['files'] == [{
        'path': commercial_path.name,
        'sha256': hashlib.sha256(commercial_path.read_bytes()).hexdigest(),
    }], 'Unreviewed commercial documentation change'
    pages = {}
    for path in paths:
        relative = path.relative_to(root).as_posix()
        pages[path.resolve()] = DOCUMENTS.get(relative, f'/tutorial/files/{relative}/')
    pages[commercial_path.resolve()] = '/sdk/communication-services/'
    for sample, slug in [('tutorial', 'first-scenario'), ('custom-services', 'custom-services')]:
        sample_root = root / 'sdk-tools/samples' / sample
        for directory in (sample_root, sample_root / 'src/main/spp'):
            pages[directory.resolve()] = f'/tutorial/samples/{slug}/'

    sidebar = '<a class="book-index" href="/guide/">Language guide</a>' + ''.join(
        f'<a class="toc-link" href="{url}">{label}</a>' for url, label in [
            ('/tutorial/', 'S++ tutorial'),
            ('/sdk/user-guide/', 'SDK user guide'),
            ('/sdk/technical-services/', 'Technical services'),
            ('/sdk/communication-services/', 'Paid communication and identity services'),
            ('/sdk/validation/', 'Upstream validation and limits'),
            ('/tutorial/samples/first-scenario/', 'First scenario inputs'),
            ('/tutorial/samples/custom-services/', 'Persistence and custom services'),
        ])
    sidebar += '<a class="book-index" href="/tutorial/downloads/sdk-tutorial-samples.zip">Download sample sources</a>'
    for path in paths + [commercial_path]:
        is_commercial = path == commercial_path
        relative = path.name if is_commercial else path.relative_to(root).as_posix()
        title = path.name
        if path.suffix == '.md':
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', links_extension()])
            md.source, md.pages, md.repository_references = path.resolve(), pages, 0
            body = md.convert(path.read_text())
            title = next(line[2:] for line in path.read_text().splitlines() if line.startswith('# '))
            assert md.repository_references == 0, f'Unpublished SDK reference: {relative}'
        else:
            lines = ''.join(f'<span class="source-line" id="L{i}"><a class="line-number" href="#L{i}">{i}</a><code>{html.escape(line)}</code></span>'
                            for i, line in enumerate(path.read_text().splitlines(), 1))
            body = f'<h1>{html.escape(path.name)}</h1><p>{html.escape(relative)}</p><pre class="source-code">{lines}</pre>'
        if path.parent.name in {'tutorial', 'custom-services'} and path.name == 'README.md':
            sample_root = path.parent
            links = ''.join(f'<li><a href="{pages[p.resolve()]}">{html.escape(p.relative_to(sample_root).as_posix())}</a></li>'
                            for p in paths if p.is_relative_to(sample_root) and p != path)
            body += '<h2>Sample source files</h2><ul>' + links + '</ul>'
        if relative == 'docs/tutorial/spp-tutorial.md':
            body += '<p><a href="/tutorial/downloads/sdk-tutorial-samples.zip">Download the tutorial and custom-service sample sources</a>. Use them with the matching basic SDK source tree.</p>'
        url = pages[path.resolve()]
        navigation = sidebar.replace(f'href="{url}"', f'href="{url}" aria-current="page"')
        footer = ('<a href="/guide/">Developer guide</a><a href="/sdk/technical-services/">Technical service contracts</a>'
                  '<span>Documentation: MIT. appframe-channels implementation: commercial terms.</span>'
                  if is_commercial else
                  '<a href="/guide/">Language guide</a><a href="/tutorial/files/LICENSE/">SDK documentation and samples: Apache-2.0</a><a href="/tutorial/files/NOTICE/">Notices</a>')
        document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | S++ SDK</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/book.css"><script src="/site.js" defer></script></head><body class="book-page">{header('guide')}<div class="book-layout"><aside class="book-sidebar"><details class="book-toc" open><summary>Tutorial and SDK manuals</summary><nav aria-label="SDK documentation">{navigation}</nav></details></aside><main id="main-content"><div class="book-meta"><span>SDK DOCUMENTATION · 1.0-SNAPSHOT</span><a href="/tutorial/">Start the tutorial</a></div><article class="book-article">{body}</article><footer class="book-footer">{footer}</footer></main></div></body></html>'''
        target = output / url.lstrip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document)

    downloads = output / 'tutorial/downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    shutil.copy2(base / 'manuals/upstream.json', downloads / 'upstream.json')
    with zipfile.ZipFile(downloads / 'sdk-tutorial-samples.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            if path.is_relative_to(root / 'sdk-tools/samples') or path.name in {'LICENSE', 'NOTICE'}:
                archive.write(path, path.relative_to(root))
    print(f'Built {len(paths)} pinned SDK documentation and sample pages plus the paid communication services manual')
