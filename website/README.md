# S++ website and publication tools

The production website is <https://us.servpp.top/>. Its public English pages include the project introduction, guide, examples, English book and source browser. Book publication is reserved-rights under `../book/COPYRIGHT.md`; the website code is MIT-licensed.

## Inputs and generated output

- `static/`: maintained HTML, CSS, JavaScript and icons for the public website.
- `../book/en/`: the maintained English manuscript and translation order.
- `articles/` and `articles.json`: original introductory articles and their titles, summaries, dates and URL slugs.
- `../demos/petstore/` and `../demos/bank-deposit/`: current demo source-language files.
- `dist/`: generated publication; ignored by Git and never maintained separately.

The generator produces `/book/`, a complete printable manuscript, `/sources/`, source-file views with line anchors, original downloads, per-demo ZIP files, canonical HTTPS URLs, `robots.txt` and `sitemap.xml`. Existing public source URL slugs remain compatible with the previous website, while the repository stores demos under their new directory names.

## Build and preview

From the public project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r website/requirements.txt
.venv/bin/python website/build_book.py
python3 website/check_site.py
python3 tools/check_public_sources.py
python3 -m http.server 18777 --directory website/dist
```

Open <http://localhost:18777/>. No compiler/runtime artifact or deployment credential is required to build the website.

`build_book.py --source /path/to/english-manuscript` can select a different English source directory. Internal chapter links become website URLs; demo references open source views. Supporting references outside the English reading sequence remain identified as repository references. The `/docs` path is intentionally unused to preserve the pre-existing service on the production host.

## Source formatting

`python3 website/format_demo_sources.py` formats the original SPP/APP/PHY/enum files. `--check` verifies stable formatting without edits. It uses four-space indentation, separate statements and continuation lines for long argument lists/expressions, while preserving lexical tokens. Online source views keep these actual source lines; browser automatic wrapping is disabled.

## Publish

Maintain deployment credentials and remote filesystem settings outside this public repository. After building and checking the site:

```bash
SPP_SITE_HOST=user@host \
SPP_SITE_DIRECTORY=/absolute/remote/site/path \
./tools/deploy-website.sh
```

The script uploads static publication files to the selected destination. It does not modify Nginx, Docker, certificates, mail forwarding or other services. Verify live pages and downloads after publishing. CI validates public material on push and pull requests; production publication stays an explicit maintainer action.

## Search discovery

Use Google Search Console to add and verify the URL-prefix property `https://us.servpp.top/`, submit `sitemap.xml`, and request indexing for the home page and book contents. The generator supplies crawl and canonical settings, page descriptions, sharing metadata, homepage site-name structured data and article structured data. See [the rollout guide](../docs/search-discovery.md) for positioning, verification steps and measurement, and [post drafts](../docs/promotion-copy.md) for owner-approved sharing. These steps do not guarantee indexing or ranking. Ownership verification belongs to the owner's Google account. Owner-supplied public verification files are kept verbatim under `static/`; account credentials remain outside this repository.

## Reserved-rights PDF publications

After building the site, `python tools/prepare-chinese-print.py` prepares a temporary Chinese print view. Serve `website/dist` at port 18977 and run `NODE_PATH=/path/to/node_modules node tools/export-book-pdf.cjs` with Playwright and Chrome available. This updates the two publications in `book/exports/`, including copyright notices. Remove `website/dist/pdf-zh/` afterward; it is a print helper, not a Chinese website entry.
