# Appendix E — Language and Engineering Reference

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

This appendix gives language conventions and experiment commands used by the draft. It aids reading; module source and runtime instructions remain authoritative. Run commands at repository root.

## Concept Reference

|Concept|Responsibility|
|---|---|
|Entity|Natural entity owned by this domain|
|Reference|External entity, role or contract with explicit source|
|Role|Participating identity and role facts|
|Contract|Parties, terms and scenario results|
|take ... as|Single, joint or further role playing|
|mapsame|Explicit compatible same-name mapping; not default|
|takeall|Import player properties and generate mappings|
|business|Explain true business use of a suspicious technical ID and remove habitual-ID warning|
|query|Complete participants and support identity confirmation|
|check|Judge conditions without mutation|
|calculate|Prepare candidates and compose pure calculations|
|update|Apply changes through application/resources|
|quantum update|Define deltas and settlement relationships|
|Scenario|Organize complete activities|
|transaction ... fail|Business handling after execution and technical recovery|
|ResultInfo|Built-in scenario result/recovery participant, not an atomic parameter|

Entries use participants or collections; names can default. Argument-free calls require unique type binding. There are no business return values. Scalar input identity stays stable, while mutable collection contents can change.

Ordinary check ends lexical scope and does not default to rollback. Explicit reversal uses the repository spelling `breakTransction`. Participant execution defines conditions and provisional control flow; the text does not assume universal support across transaction modes.

## Example Backend Coverage

These are concrete baseline capabilities, not new conceptual definitions:

|Feature|Conditions|
|---|---|
|LOCAL|Same JVM and verified common database/schema/connections|
|REQUIRED|Reuse execution and commit context|
|REQUIRES_NEW|Supported homogeneous outer/local combinations; independent results handled separately|
|NESTED|Rejected by example backend|
|Bare check in parallel|Limited stop scope; use supported serial or guard forms|
|Enhanced for|Collection-order iteration, not automatic parallel calculation|
|calculate calls|Pure calculation composition; no cycles or technical effects|
|fail|Outer transactions in serial scenarios; fail(targetContract) for multiple contracts; nested/parallel fail rejected|
|Remote transaction/quantum protocol|Actual coordination and recovery evidence required; otherwise rejected|

Execution, storage and environment specifications define exact checks. Principles establish when combinations make sense; backends still need actual runtime support.

## Implementation References for Service Categories

|Characteristic|Source or Example|
|---|---|
|Independent concurrent queries followed by fact use|[Ordering](../../../demos/petstore/src/main/spp/petshop/order/petshop-scene-placeShopOrder.spp), [payment](../../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-payShopOrder.spp)|
|In-place completion and identity|[Query binding](../../references/participant-query-binding.md), [execution](../../references/spp-participant-execution.md)|
|Built-in query/update; visible scenario rules|[Implicit CRUD](../../references/implicit-participant-crud.md)|
|Atomic call restrictions and calculation cycles|SppDomain (maintainer reference: `../../../lang/src/main/java/com/servpp/lang/models/SppDomain.java`): validateBusinessCalculations, validateCalculationCycles|
|Calculation-only calls, no check mutation/require|BusinessCalculationValidator (maintainer reference: `../../../lang/src/main/java/com/servpp/lang/models/app/expr/BusinessCalculationValidator.java`)|
|Quotation reuses line calculation|[Pricing](../../../demos/petstore/src/main/spp/petshop/order/petshop-20-calculations.spp): quoteOrder and priceLine|
|Lexical checks, guards and reversal|[Execution](../../references/spp-participant-execution.md), [atomics](../../references/spp-atomic-services.md)|
|Record rejection after recovery|[Reservation](../../../demos/petstore/src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp), [system results](../../references/spp-transaction-failure-handling.md)|
|Local calculation/validation generation|SppService (maintainer reference: `../../../lang/src/main/java/com/servpp/lang/models/SppService.java`): isLocalService; generator (maintainer reference: `../../../generator/src/main/java/com/servpp/generator/openapi/MustacheClassWriter.java`); [APP](../../../demos/petstore/src/main/spp/petshop/petshop.app)|

Concurrency and local sequencing follow duties/dependencies, not automatically service categories. Local execution still accepts concurrent requests. Part I explains common arrangements, Part II costs and dependencies.

## Build and Test

```bash
mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=develop
mvn -pl :petstore-demo -am test-compile -DskipTests -Dspp.environment=testing
mvn -pl :petstore-demo -am test -Dtest=PetstoreScenarioTest -Dsurefire.failIfNoSpecifiedTests=false
```

The first two build/compile but skip running tests. The third runs selected tests. package success alone does not prove regression. Latest Petstore acceptance records provide joint-regression commands.

## Local Web Application

```bash
SPP_PETSTORE_JDBC_URL='jdbc:h2:file:/tmp/spp-book-develop' \
  ./demos/petstore/run-demo.sh web
```

Default port is 8086. Existing matching builds can use `SPP_DEMO_SKIP_BUILD=1`. Fixed paths retain previous data; choose paths by experimental round.

## Three-Process testing

Build testing artifacts first. Set identical caller credentials and experiment resources in all three terminals, replacing the token placeholder:

```bash
export SPP_ENVIRONMENT=testing
export SPP_DEMO_SKIP_BUILD=1
export SPP_DOMAIN_RPC_TOKEN='replace-with-session-token'
export SPP_TESTING_CUSTOMER_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-customer'
export SPP_TESTING_PRODUCT_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-product'
export SPP_TESTING_SHOP_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-shop'
export SPP_TESTING_LEDGER_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-ledger'
```

Start providers, confirm readiness, then start shop:

```bash
# Terminal 1, default port 8087
./demos/petstore/run-demo.sh web customerService
```

```bash
# Terminal 2, default port 8088
./demos/petstore/run-demo.sh web productService
```

```bash
# Terminal 3, default port 8086
./demos/petstore/run-demo.sh web petstore
```

Cross-host deployment needs endpoints and quantum resources ensuring one actual system. Identical copied H2 file-path strings do not create a shared remote database.

## Numbers and Output

SPP numeric specifications give defaults; PHY replacement and field overrides select representation, with field overrides taking precedence. Capacity is not rounding. Generated output stays in target; source in `src/main/spp`.

See [runtime instructions](../../../demos/petstore/docs/running-demo.md), [launcher](../../../demos/petstore/run-demo.sh), [execution](../../references/spp-participant-execution.md), [numbers](../../references/numeric-physical-semantics.md) and [environments](../../references/deployment-environments-and-physical-defaults.md).

---

[Appendix Contents](README.md) · [Full Book Contents](../README.md) · [Previous](d-quantum-contracts.md) · [Next](f-sources-and-evidence.md)
