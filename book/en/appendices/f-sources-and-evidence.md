# Appendix F — Sources and Verification Evidence

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

This appendix provides concepts, source, execution and performance references. Concepts form one system; remaining cross-document issues are separately tracked in [editorial records](../../编辑工作/known-issues.md), outside the narrative.

## F1 Theory and Methods

|Reference|Coverage|
|---|---|
|S++ Concepts and Applications (maintainer reference: `../../../../spp/docs/cn/concept.md`)|Service model, decomposition, quantum services, polymorphism, separation and performance|
|S++ Modeling (maintainer reference: `../../../../spp/docs/cn/modeling.md`)|Shop participants, identity, agreements and storage|
|Scenario Composition Design (maintainer reference: `../../../scenario/docs/Composit.docx`)|Categories, dependency groups and scheduling|
|Application Framework Design (maintainer reference: `../../../lang/doc/ApplicationFrame.docx`)|Runtime, technical handling and transactions|

The neighboring spp repository must be obtained separately. Relative source references require that checkout beside this repository.

## F2 Language and Engineering Specifications

|Topic|Reference|
|---|---|
|Meaning and participation|[Business model boundaries](../../references/spp-business-model-boundary.md)|
|Query, identity and control|[Participant execution](../../references/spp-participant-execution.md)|
|Calculation rules|[Atomic calculation](../../references/atomic-calculation-services.md)|
|Representation and rounding|[Numeric semantics](../../references/numeric-physical-semantics.md)|
|Quantum bounds|[Call bounds](../../references/quantum-call-bounds.md)|
|Ownership, commit and recovery|[Transaction/storage](../../references/transaction-storage-v1.md)|
|Environments and resources|[Deployment/physical configuration](../../references/deployment-environments-and-physical-defaults.md)|

Petstore counts retain the separate baseline in F7. Bank source and newly added capabilities are checked against main revision `0fafa21d`. Specifications state goals and constraints, source expresses implementation, and runtime records evidence specific paths. No single layer replaces the others.

## F3 Petstore Functional Verification

[October 13, 2026 technical-service verification](../../references/app-technical-services.md) records 1,123 passing tests: language 362, runtime 617, generator 105, Petstore 39, with zero failures, errors or skips. Coverage includes matching, compilation, phases, access rejection, observer isolation, concurrency and replay. Remote proxies use controlled transport, without real cross-JVM acceptance. The [Petstore example](../../../demos/petstore/docs/technical-services.md) shows all-service tracing. Capability comes from main revision `65c766fc`; this book cites existing records.

[October 13 failure handling](../../references/spp-transaction-failure-handling.md) records 1,104 develop tests: language 356, runtime 607, generator 105, Petstore 36, all passing without skips. [Reservation evidence](../../../demos/petstore/docs/reservation-failure-handling.md) covers insufficient stock, ordinary-save fault and replay. Framework tests separately establish real JDBC settled inverse before fail. Petstore used LOCAL, not real distributed TCC/external quantum acceptance. These are cited records, not tests rerun for the manuscript.

[October 12 final regression](../../../demos/petstore/docs/regression-2026-10-12-conserved-transfers.md) records 1,080 passing tests: lang 340, appframe 581, generator 105, appframe-seata 20, Petstore 34; no failures, errors or skips.

That record also covers complete Chrome flows in develop, three-JVM testing with four isolated file databases, and shop restart. After shutdown, checks compare fund totals, per-goods stock/supply and per-transaction delta sums.

Temporary log paths identify original evidence; independent environments must rerun commands to obtain their own results. [Known limitations](../../../demos/petstore/docs/known-issues.md) cover opening retries and split zero recovery, detailed in [recovery design](../../../demos/petstore/docs/quantum-opening-recovery.md). Functional regression is not Appendix C's serial/parallel benchmark.

## F4 Verification of the Bank Deposit Case

The bank deposit case has completed its migration to current syntax and runtime protocols. Its [production source](../../../demos/bank-deposit/src/main/spp/cboddeposit) uses only SPP, APP and PHY, with no handwritten production Java. SPP does not use `try/catch/throw`; generated Java and runtime internals can still use exception handling for technical failures. Historical source remains for rule comparison, not as current executable examples.

This section checks the case against main revision `0fafa21d` and cites existing repository evidence. The manuscript update did not rerun bank tests. The [latest verification record](../../../demos/bank-deposit/docs/latest-refactoring-verification.md) preserves commands, results and scope by batch:

|Verification Batch|Result|Scope|
|---|---|---|
|October 13, 2026 clean develop joint regression|1,226 tests; zero failures, errors or skips|Language 366, runtime 628, generator 107, bank case 86, Petstore 39; internal recipient accounts, historical snapshots and included fault/concurrency tests|
|Subsequent testing bank regression|86 tests; zero failures or errors, two skips|Separate quantum and ordinary H2 data sources in one JVM; two LOCAL-only commit-fault tests skipped|
|Independent reversal-preview tests|Two passing tests in each of develop and testing|No preview writes; formal reversal preserves later deposits; missing originals are rejected without side effects|
|Chinese workbench verification|Backend tests and browser flows pass in both environments|Exact decimal display, negative-amount rejection, preview, reversal, receipt lookup and mobile layout; see [workbench acceptance](../../../demos/bank-deposit/docs/web-workbench.md)|

Split-storage testing does not constitute complete acceptance of real network distribution, XA, Seata AT or TCC. Independent JVM restart and forced exit after confirmed settlement cover their specified persistence paths, not automatic resolution of interrupted or unknown commits. Later targeted tests must not be added together and represented as one unexecuted joint regression.

The [completion audit](../../../demos/bank-deposit/docs/completion-audit.md) identifies implemented scenarios, storage, transactions and technical capabilities. The [86-entry historical migration inventory](../../../demos/bank-deposit/docs/legacy-entry-migration.md) lists evidence, differences and unmigrated parts entry by entry. Those 86 historical entries and the 86 JUnit tests above are different measures; equal numbers do not establish one-to-one equivalence.

[Known issues](../../../demos/bank-deposit/docs/known-issues-latest.md) retain boundaries for committed ordinary Saga recovery, persisted pending authorization and cross-process resumption, automatic confirmation of unknown settlement, and durable auditing of every invocation. A split-storage failure can restore quantum funds while leaving ordinary committed facts. The system explicitly reports `RECOVERY_REQUIRED` and `handled=false`, not complete rollback.

[Source mapping](../../../demos/bank-deposit/docs/source-map.md) gives current directories and original rule locations. Source derivation, mathematical expectations, demonstration inputs, generated execution comparisons, original COBOL execution and bank-confirmed results represent different evidence levels. Case success does not establish every bank policy or original-system output equivalence.

## F5 QService References

The neighboring qservice repository's SPP boundary contract (maintainer reference: `../../../../qservice/docs/spp-qservice-boundary-contract.md`) and quantum design (maintainer reference: `../../../../qservice/docs/qservice-early-design.md`) describe commands, durable identities, lookup and recovery.

It has separate artifacts and baselines. Verify the backend protocol actually integrated; independent-project tests do not extend to arbitrary deployments.

## F6 Using Evidence

Parsing establishes accepted expression; compilation checks artifacts; runtime exercises paths; fault/restart tests cover specified recovery. Performance needs workload/resources.

For each claim, identify participants, behavior and configuration, then input, expectation, result and fault scope. These connections make conceptual arguments reviewable as engineering practice.

## F7 Petstore Code-Size Statistics

The figures in this section describe their recorded source baseline. Subsequent English/USD presentation and expanded source formatting change physical line counts; they do not retroactively change these measurements.

On October 13, 2026, source at book branch `5b9b182c` was measured; that manuscript change did not alter demo source. develop generation began with no existing generated Java directory, excluding stale files. Run at root:

```bash
mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=develop
```

Inputs are `.spp`, `.enum`, `.app` and `.phy` under `demos/petstore/src/main/spp/`; output is `.java` under `demos/petstore/target/generated-sources/openapi/src/main/java/`. Excluded are tests, pages, resources, build scripts, generator and shared runtime dependencies. Java includes both S++ and OpenAPI generation. Reproduce in a clean directory and recount after source/tool changes.

|Category|Files|Physical Lines Including Blanks/Comments|Code Lines|
|---|---:|---:|---:|
|SPP|63|1,104|999|
|Enums|2|25|18|
|APP|4|126|117|
|PHY|4|222|214|
|Inputs total|73|1,477|1,348|
|Generated Java|962|131,107|100,151|

Models account for 64,431 code lines, services 21,031, interfaces/handlers 14,535, and mapping/configuration 154. Model and request/response expansion is substantial; every line is not independently designed business logic.

This script removes blank, line-comment and block-comment lines while preserving comment symbols in strings and brace-only lines. It fits this source, not every language construct:

```python
from pathlib import Path
import re

pattern = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/'
)

def code_lines(source):
    def remove_comment(match):
        token = match.group()
        if token.startswith(("//", "/*")):
            return "\n" * token.count("\n")
        return token
    source = pattern.sub(remove_comment, source)
    return sum(bool(line.strip()) for line in source.splitlines())

source_root = Path("demos/petstore/src/main/spp")
java_root = Path("demos/petstore/target/generated-sources/openapi/src/main/java")
for suffix in (".spp", ".enum", ".app", ".phy", ".java"):
    root = java_root if suffix == ".java" else source_root
    files = sorted(root.rglob("*" + suffix))
    sources = [path.read_text(encoding="utf-8") for path in files]
    print(suffix, len(files),
          sum(len(source.splitlines()) for source in sources),
          sum(code_lines(source) for source in sources))
```

SPP can place multiple declarations/calls on one line, while Java formatting, accessors and request/response types expand lines. This is version-specific scale, not a universal expressiveness, productivity or speed ratio. Exact handwritten Java comparison requires an independent implementation with equivalent business, capability and acceptance. The following is an estimate by responsibility.

### Estimate with Common Java Frameworks

Assume Spring Boot + MyBatis + Lombok, existing reusable components, no separate remote interface for every internal operation and no manually expanded accessors. Lombok provides model boilerplate, MyBatis SQL mapping and Spring declarative transactions. Their source is dependency, not project-maintained code. See [Lombok Data](https://projectlombok.org/features/Data), [MyBatis Mapper](https://mybatis.org/mybatis-3/sqlmap-xml.html) and [Spring transactions](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html). Documentation establishes capabilities; estimates are the book's engineering judgment, not vendor benchmarks.

|Maintained Content|Estimated Lines|Basis|
|---|---:|---|
|Models, DTOs and enums|1,000–2,000|Four domains, reused models and Lombok|
|Entries, conversion and mapping|1,000–2,000|34 scenario boundaries|
|Orchestration, calculation and eligibility|3,000–5,000|Approximately 90–150 per scenario including shared rules|
|Persistence, SQL, mappings and schema|2,000–4,000|Facts, snapshots, version conditions and associations|
|Conservation, idempotency and recovery integration|2,000–5,000|Bilateral deltas, bounds, original confirmation and phase recovery|
|Domain calls, environments and technical errors|1,000–2,000|Local/remote adaptation, resources and environment selection|
|Total|10,000–20,000|Java, SQL/Mapper and necessary configuration|

Responsibilities are allocated to avoid duplication: business rejection belongs to scenario/checks; timeout confirmation to recovery/technical handling. Proposed general cache pruning and full security/governance not yet implemented in the case are excluded, as is developing the shared framework itself.

A conventional monolith with local transactions, merged models, less domain adaptation and only local rollback may need 6,000–10,000 lines. That narrower scope omits domain deployment and its confirmation/recovery and is not an equivalent-capability baseline.

Mature accounting, idempotency and coordination middleware reduces handwritten code; building such general facilities can exceed these ranges. Formatting also matters. Ten to twenty thousand describes maintenance scale, not an exact productivity multiplier or development time.

## F9 COBOL and S++ Code Size in the Bank Case

The count was made on October 14, 2026, using case source and reference documents at repository revision `92ed491b`. Original COBOL and COPYBOOK files were read from the local bank-source directory, without modification or copying their contents into this book. That directory must be obtained separately. File inventories and figures are preserved in the appendix's [count results](../../附录/统计资料/bank-code-count.json).

### Source Scope and Deduplication

The “directly located for analysis” scope selects nine COBOL programs identified by program filename or specific line references in the source documentation. Located analysis means there is a source-tracing basis; it does not mean every branch of each program has been migrated.

|Program|Source Responsibility|Physical Lines|Lines Excluding Blanks and Comments|
|---|---|---:|---:|
|GSA01102|Front-office acceptance of a general deposit|2,325|1,820|
|KSADEP0|Deposit core, repayment allocation and reversal|4,197|3,508|
|CSAQRY1|Account eligibility and acceptance checks|2,654|1,867|
|KSAFEE0|Fee entry point|384|310|
|CSAFEE0|Fee rules|415|331|
|CCMDAT1|Calendar and day counting|2,856|2,563|
|CSAPRD2|Deposit and agreement accrual products|483|315|
|CSAPRD4|Overdraft accrual products|237|154|
|GCCBAAR|Accounting-rule integration and configuration-source analysis|605|542|
|Total|Nine programs|14,156|11,410|

Active `COPY` statements in those programs directly reference 135 COPYBOOKs. Nested references add another 26, yielding 161 distinct files. A shared COPYBOOK is counted once by actual file, even when several programs or repeated statements reference it. Invocation and expansion counts do not multiply it.

The broader “all related” scope selects 22 programs explicitly mentioned in the source documents and actually present in the original directory. It includes dispatch, query and configuration programs. It does not recursively expand every `CALL` dependency and is not the size of the entire banking system.

|Source Scope|COBOL Programs|Distinct COPYBOOKs|Program Physical Lines|COPYBOOK Physical Lines|Total Physical Lines|Total Lines Excluding Blanks and Comments|
|---|---:|---:|---:|---:|---:|---:|
|Directly located for analysis|9|161|14,156|23,488|37,644|22,589|
|All related programs mentioned in documentation|22|192|20,626|24,961|45,587|28,358|

See the [direct-source inventory](../../附录/统计资料/bank-direct-source-files.csv) and [all-related-source inventory](../../附录/统计资料/bank-related-source-files.csv) for per-file figures. They contain locations and counts, not bank source contents.

### Current S++ Source

Only production SPP, enums, APP and PHY are counted. Historical material, Java tests, test inputs, web pages, build scripts, generated Java, and shared compilers and runtime frameworks are excluded.

|Source Category|Files|Physical Lines, Including Blanks and Comments|Lines Excluding Blanks and Comments|
|---|---:|---:|---:|
|SPP|34|1,037|973|
|Business enums|1|6|6|
|APP|2|48|48|
|PHY|2|38|38|
|Total|39|1,129|1,065|

SPP and enums total 979 nonblank, noncomment lines describing the business models, services, scenarios and finite value sets maintained in this case; APP and PHY add 86. Several S++ statements currently share a physical line. Line ratios therefore do not directly measure algorithmic complexity, work or productivity.

### Counting and Reproduction

Physical lines follow each file's original line breaks. COBOL nonblank, noncomment counts use fixed-format processing: exclude lines whose seventh column is `*` or `/`, take content from columns 8–72, remove inline comments following `*>`, and count remaining nonempty lines. Sequence columns and right-hand identification areas are not code. Data definitions, `COPY` directives, procedures and control declarations still count; these are not business-statement counts.

COPYBOOKs follow the same rule. SPP, enums, APP and PHY remove `//` and `/* … */` comments while preserving comment symbols in strings, then count remaining nonempty physical lines. COPYBOOKs are not expanded and repeatedly counted inside every program.

The [reproduction script](../../附录/统计资料/count-bank-code.py) takes the original COBOL root directory. Run from the repository root:

```bash
python3 book/附录/统计资料/count-bank-code.py /path/to/original/cobol-root \
  --output-dir /tmp/bank-demo-code-count
```

The root must contain the original program and COPYBOOK category directories. The script writes two source inventories and a summary JSON. Changes to source or reference documents can change scope and results; recount and identify the revision. Neither current scope contains unresolved or ambiguous COPYBOOK references.

### Limits of the Comparison

Source and implementation sizes help explain how concentrated the expression is; they do not prove equivalent conversion of every source line. Entire source programs include other transaction modes, shared configuration and unmigrated branches. The S++ case covers business paths explicitly implemented and verified.

Role and service models concentrate their rules, participating relationships and execution boundaries. Tools supply repetitive implementation, and APP/PHY connect storage and runtime facilities. The case still depends on shared frameworks, uses demonstration configuration for accounts and external facts, and retains authorization-resumption and ordinary Saga recovery limits described in F4. Dividing all source lines by case lines does not establish an unconditional compression factor or full replacement.

---

[Appendix Contents](README.md) · [Full Book Contents](../README.md) · [Previous](e-language-and-build.md)
