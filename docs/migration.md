# Independent public project migration

The public project is the authoritative maintenance home of the current Petstore and bank-deposit demos, the publicly readable book and the website inputs.

## Scope

| Original workspace directory | Public project directory |
| --- | --- |
| `book/` | `book/` |
| `petstore-demo/` | `demos/petstore/` |
| `xbod-deposit-demo/` | `demos/bank-deposit/` |
| `website/` | `website/` |

Only these two current demos migrate. Earlier `business-showcase`, `credit-commerce`, `petstore`, `invoice` and `petclient` experiments remain in the compiler workspace. Compiler/runtime internals, original bank COBOL, credentials, database files and compiled Java are not included in the public project.

The public repository begins with the reviewed current source snapshot, including the English/USD and source-formatting working-tree changes. The private original Git history, pre-migration source snapshot and patches remain backed up with the compiler workspace. `migration.json` records provenance and scope. No unrelated private history is rewritten or published.

## Licenses and publication

The book is publicly published for reading but remains all rights reserved under `book/COPYRIGHT.md`. It is not MIT or Creative Commons licensed. Demo and website code use the scoped MIT code license in `LICENSE`.

The site is generated from the repository sources. Its existing `/book/` and `/sources/` URLs remain stable. Source download URLs retain their public names even though archive paths reflect the new repository layout. Book copyright notices appear in the manuscript and online pages. Generated website output is ignored by Git.

## Build separation

The public Maven reactor has its own parent POM and includes only the two current demo modules. It consumes separately supplied SDK artifacts instead of compiling private runtime sources from adjacent workspace directories. The demo launch scripts use Maven's runtime classpath and do not require `../appframe/target/classes`.

The compiler workspace removes the two demo modules from its default reactor. An optional integration profile can consume the public repository as a submodule, so maintainers can still exercise compiler changes against the demos in one reactor. This is a reference to the independent project, not a second maintained copy.

## Maintenance

- Change book, demo and site sources here, review changes, then rebuild and publish the website.
- Track questions and corrections in GitHub Issues; keep book and code contribution/license scopes distinct.
- Do not commit `target/`, generated website output, local environment files, runtime databases or private source trees.
- Use fresh isolated databases for repeatable demonstrations and preserve existing order snapshots.

## Verification — October 15, 2026

The independent Maven reactor generated and compiled both demonstrations against the installed SDK, with no compiler-source directory on its reactor. Petstore passed 39 tests and bank deposits passed 88: 127 tests, zero failures, errors or skips. The SDK was prepared from the authorized compiler workspace; it is not committed or distributed here.

Both language editions and standalone publications carry the book copyright notice. The English PDF was regenerated from the current USD/name examples and checked as extracted text. The Python-only site build and local links/fragment checks passed; source formatting is stable. Public source checks cover local Markdown targets, excluded artifacts and the book/code license boundary.

Evidence: `/tmp/spp-independent-demo-tests.log`, `/tmp/spp-public-book-pdf.log`, and local Surefire reports under each demo's ignored `target/` directory. The optional compiler-workspace integration profile also passed Maven reactor validation. Both demos then started independently using only their Maven runtime classpaths and fresh isolated in-memory databases. Browser acceptance passed for Petstore order/refund/reservation flows and bank opening/deposit/reversal/history flows, including mobile presentation, exact-decimal USD amounts and no page errors. Existing demonstration services and their persistent data were left running unchanged. GitHub publication remains pending account authorization.
