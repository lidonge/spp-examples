# English / USD Demo Presentation

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## Scope and decisions

The public Petstore and XBOD deposit demonstrations use English as their primary language. Petstore catalogue localization remains available in Chinese; the selected language does not change the monetary unit. Supporting legacy engineering documents and regression records retain their original language.

Both public walkthroughs use US dollars (USD). Numeric amounts are illustrative and remain unchanged; this is not currency conversion. Petstore uses an English/USD currency formatter. The bank workbench prefixes decimal text with its currency code without converting it to a JavaScript number, so a value such as `100.005000` remains exact in the display.

Bank eligibility and accrual rules with explicit CNY, USD or JPY conditions are preserved. Alternate currency selections and currency-specific tests continue to exercise the original rules. A presentation change must not replace those constants or reinterpret stored agreements. Receipts retain their original currency.

## Business data and localization

- APP chooses `en-US` as the default catalogue locale, with optional `zh-CN` bundles.
- Product and merchant fallback constants are English even when no localization header is supplied.
- APP maps the product description column to `String(200)`, so the complete English adoption description fits the physical table. This is a storage-capacity choice; it adds no SPP business constraint. Existing databases are not automatically altered.
- Demonstration people use English names, including Alex Taylor; book examples use Alex and Jordan.
- Business-purpose annotations are written in English. Type names, service names, participant identities, enum codes, numeric values, checks and transaction boundaries are preserved.
- New demonstration databases receive English seed facts. Existing names, role snapshots and settled order-line prices/names are not migrated or overwritten. Use an isolated database when demonstrating the new defaults.

## Source layout

Original SPP, APP, PHY and enum files use four-space indentation, separate statements, expanded blocks, one enum member per line and continuation lines for long argument lists and expressions. Formatting keeps every non-whitespace token unchanged; localization changes only the intended descriptive string values and locale selection.

The website renders these actual source-file lines. Browser automatic line wrapping is disabled. Long literals can still be scrolled horizontally, avoiding the appearance of fabricated source lines. Original-file and ZIP downloads have identical content to the corresponding repository files.

## English book

The chapter files and complete manuscript use English currency words and USD examples. No example customer name or business-purpose annotation remains in Chinese. Chinese paths in bibliographic references and the translation map identify actual source artifacts and remain intact. Historical code counts refer to their original recorded revisions: the later source layout and presentation changes do not replace those measured baselines.

## Verification and publication

1. Check formatter stability and compare token sequences for formatting changes.
2. Generate the demo Java from current SPP/APP/PHY sources and run the existing Petstore and XBOD acceptance suites.
3. Exercise both actual web applications in isolated databases: English defaults, USD display, preserved decimal values, checks, payment/refund or deposit/reversal, receipt inquiries, alternate catalogue locale and mobile layout.
4. Rebuild the static English book and source browser; check local page links and section anchors.
5. Publish to `https://us.servpp.top/` and verify live page and download content.

The website builder provides canonical HTTPS page URLs, `robots.txt` and `sitemap.xml`. The owner can add the URL-prefix property `https://us.servpp.top/` in Google Search Console, verify ownership and submit `sitemap.xml`. These steps aid discovery but do not guarantee indexing or ranking.

## Acceptance results — October 15, 2026

- XBOD: 88 tests passed; Petstore: 39 tests passed. Both suites had zero failures, errors or skips. All production Java was generated from the current source-language files.
- Petstore's actual browser journey passed in a fresh in-memory database: English default catalogue and participant names, USD wallet and prices, funding and stock receipt, order/payment/shipping/delivery/return, paid cancellation, request replay, Chinese/English catalogue switching and reservation. No browser script errors occurred.
- The bank's actual browser journey passed: English/USD defaults, exact `USD 100.005000` display, rejected deposit, read-only preview, reversal, receipt lookup, original receipt currency despite a changed form selection, history, controlled in-flight inputs, network failure and 390px mobile layout. No browser script errors occurred.
- All 114 source-language files passed stable-format verification. Business tokens were retained; the intended descriptive strings and locale defaults changed. The additional product APP mapping increases description-column capacity to 200 characters.
- English chapter files and the complete manuscript were checked for remaining Chinese prose, example names and non-USD monetary examples; real bibliographic source paths remain untouched.
- Publication verified all 294 deployed files over HTTPS against their local content hashes. All 171 page URLs in the sitemap are live; the site's 19,324 local links/resources have no missing files or fragment targets. Live desktop/mobile reader checks passed, and source code uses its actual newlines with browser wrapping disabled. Temporary demo acceptance servers were stopped after verification.

Commands and evidence:

```bash
mvn -pl :petstore-demo,xbod-deposit-demo -am test \
  '-Dtest=Petstore*Test,Xbod*Test' -Dsurefire.failIfNoSpecifiedTests=false
# After aligning APP/PHY locale defaults and product description capacity:
mvn -pl :petstore-demo -am package \
  '-Dtest=Petstore*Test' -Dsurefire.failIfNoSpecifiedTests=false
python3 website/format_demo_sources.py --check
python3 website/check_site.py
```

Local evidence is in `/tmp/spp-english-demo-tests.log` (bank acceptance and initial Petstore validation), `/tmp/spp-english-petstore-tests.log` (successful Petstore acceptance/package), `/tmp/spp-english-petstore-browser.log` and `/tmp/spp-english-xbod-browser.log`. These temporary files are verification evidence rather than required runtime artifacts.
