# S++ — Book and Business Demos

S++ describes business systems through participants, roles, atomic services, scenarios and explicit consistency boundaries. APP and PHY select how those business descriptions run.

**[Read the English book](https://us.servpp.top/book/)** · **[Browse demo source](https://us.servpp.top/sources/)** · **[Project website](https://us.servpp.top/)** · **[Report an issue](https://github.com/lidonge/spp-examples/issues)**

The current full Petstore and bank demos explicitly select the official enhanced
generator and runtime (`generator-enhanced` and `appframe-enhanced`). Install those
SDK artifacts as well as the public compiler/runtime before building the demos.
Their source code remains under this repository's scoped license. A basic-runtime
custom-service example is supplied separately with the compiler; no commercial
implementation source is copied here.

## Start here

| Material | What it contains |
| --- | --- |
| [English book](book/en/README.md) | Seven parts, 35 chapters and six appendices; modeling, language mechanisms and engineering practice |
| [Chinese book](book/README.md) | The original-language manuscript and its source references |
| [Petstore](demos/petstore/README.md) | Customer and product domains, cart, ordering, payment, fulfillment, returns and reservations |
| [Bank deposits](demos/bank-deposit/README.md) | Zero-balance opening, conserved cash deposits, repayment allocation, postings and reversals |
| [Website tools](website/README.md) | Static book rendering, source browsing, downloads and link checks |

The current demonstrations are English-first and use US dollars (USD). Bank currency-specific legacy rules remain intact. All demo production business Java is generated from SPP/APP/PHY sources; Java acceptance tests prepare participants, invoke generated services and assert results.

## License boundaries

**Demo and website code: MIT. Book: all rights reserved.**

The book is publicly published for reading, with no open-source or Creative Commons license. Its manuscripts, publications and companion references under `book/` are governed by [the book copyright notice](book/COPYRIGHT.md). The [repository license](LICENSE) explains which code is MIT-licensed. Publishing the book alongside the demos does not apply MIT to the book.

## Run a demonstration

Requirements: JDK 17+, Maven, and the separately supplied S++ SDK artifacts `free.servpp:generator` and `free.servpp:appframe` (default version `1.0-SNAPSHOT`). The compiler/runtime implementation is not included in this repository. See [toolchain setup](docs/toolchain.md).

With those artifacts installed in your Maven repository:

```bash
mvn -pl :petstore-demo -am package -DskipTests
./demos/petstore/run-demo.sh web
# http://127.0.0.1:8086/

mvn -pl :xbod-deposit-demo -am package -DskipTests
./demos/bank-deposit/run-demo.sh web
# http://127.0.0.1:8089/
```

Use fresh, isolated demonstration databases to see English seed facts. Existing order names and prices are historical snapshots and are not overwritten by a language or catalogue change. These demonstrations are not connected to real payment providers.

## Build the public website

This path needs Python and Markdown, and does not need the S++ SDK:

```bash
python3 -m venv .venv
.venv/bin/pip install -r website/requirements.txt
.venv/bin/python website/build_book.py
python3 website/check_site.py
python3 -m http.server 18777 --directory website/dist
```

Generated pages are not separately maintained or committed. The book, demo files and website tools in this repository are the authoritative inputs. The production site is `https://us.servpp.top/`.

## Contributing and verification

Use [Issues](https://github.com/lidonge/spp-examples/issues) for questions, corrections and reproducible problems. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes; book corrections do not change the book's reserved-rights status.

[Migration and maintenance](docs/migration.md) describes the split from the compiler workspace, checks and remaining toolchain requirements. Older experimental samples remain in the compiler workspace and are not presented here as current implementations.
