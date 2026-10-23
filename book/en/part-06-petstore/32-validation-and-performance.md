# Chapter 32 — Technical Configuration, Deployment and Integrated Verification

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

The preceding chapters expressed participants, quotation, settlement and failure. Now inspect existing configuration, extensions and deployment verification. Part V separation should become concrete files and results.

## Put the Layers Together

|Layer|Payment Content|Files|
|---|---|---|
|SPP|Eligibility, amount, transfer, order and receipt|Scenario, models, calculations and validations|
|APP|Storage, request policy, bindings, transactions and environments|petshop.app|
|PHY|Database, quantum storage, routing, timeout and adapters|petshop.phy|

Business reviews parties, amount, eligibility and handling; developers review storage/calls; operators resources. AI helps each, but understanding payment does not require reviewing all generated Java and drivers. Runtime evidence still verifies guarantees.

Snippets come from [APP](../../../demos/petstore/src/main/spp/petshop/petshop.app) and [PHY](../../../demos/petstore/src/main/spp/petshop/petshop.phy).

## Retain Agreed Facts Through Mapping

```app
table SHOP_ORDER_LINES(OrderLine) {
    primarykey(OrderLine.lineNumber);
    auto OrderLine.lineNumber prefix "ORDER-LINE";
    foreignkey(OrderLine.goods) references Goods;
    snapshot(OrderLine.name, OrderLine.unitPrice);
}
```

Goods name uses `current(Goods.name)`. Save an order, change product name and selling price, then query goods and old order. Current facts change, historical name/price remain. This tests Part III mapping and Part IV ownership together.

## Protect Repeated Processing

Global and payment-entry declarations occur in requests and scope local:

```app
requests { idempotency retention 3 days; duplicateWindow 5 seconds; }
```

```app
duplicate key(Buyer.membershipNumber, ShopOrder.orderNumber)
    facts(ShopOrder.orderNumber) payShopOrder;
```

PHY uses `config requestIdempotencyAdapter = "jdbc";`. UI guards handle quick repeated actions; remote idempotency handles repeated transmission. SPP still checks eligibility.

Verify no second payment for repeated clicks, original results for same-identity/content remote replay, and conflict for changed content. LOCAL calls do not register remote transport requests and cannot substitute for its tests. See [protocol](../../references/app-call-idempotency-and-duplicate-guard.md).

Check actual durable data sources and restart records. Three-day retention does not allow unknown requests to become new payments when time expires; unresolved recovery needs explicit treatment.

## Compare Concentrated and Split Deployment

develop deploys four domains in one process:

```app
transactions {
    mode: LOCAL;
    resource: shopRecordsResource;
    ordinaryUpdates: PARALLEL;
}
```

PHY binds ordinary and quantum resources locally. Ready independent ordinary saves run concurrently; unprepared steps retain scenario dependencies.

testing separates customer and product processes while inventory and shop share a process. Ordinary and quantum databases are separate; PHY supplies routes/timeouts, APP chooses unified quantum storage and recovery for ordinary resources.

Domains stay the same while paths/resources change. LOCAL rollback is not cross-resource rollback. Quantum-first settlement followed by save failure requires phase confirmation and recovery, not relaxation of consistency.

Web, restart/conservation and failure evidence is in Appendix F. Recorded paths are neither all-fault proof nor a performance benchmark.

## Apply Performance Methods to Queries

Goods browsing can cache names, descriptions and display facts. Property-use analysis can limit quotation to pricing/eligibility and listings to display, avoiding complete recursive loads.

Order lists need number, state and total; detail needs lines. Measure on-demand reads and responses separately, and never save partial objects as complete snapshots.

These proposals from Part V, Chapter 24, are not proven complete multilevel caches, compiler pruning or generic output projection in this example. Add keys, invalidation, permissions and unloaded-field save contracts, not just fewer scenario queries.

Display caches for wallets and availability do not replace actual payment/reservation bounds. “Two cached items” cannot guarantee buying two.

## Extend the Existing Logging Example

[Technical APP](../../../demos/petstore/src/main/spp/petshop/technical-services.app) binds invocationTrace to shop services with intercept services, while [PHY](../../../demos/petstore/src/main/spp/petshop/technical-services.phy) supplies generic Java logging. SPP has no added logging calls.

Business reviews payment, status and rejection reasons; technology reviews events. A fail-handled reservation normally returns AFTER even though reservation failed. Logs omit customer/order contents.

Part V, Chapter 27, shows custom Java metrics, alerts and controls through APP/PHY. Query caches and output masking need data adapters. See [technical example](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/technical-services.md).

## Apply Security and Governance to Entries

testing has an interdomain token, not a complete authentication, authorization and data-protection system. Production work includes:

|Capability|Location|Verification|
|---|---|---|
|Authentication/access control|Page and domain entries|Trusted caller; no impersonating another buyer|
|Encryption/masking|Transfer, addresses, logs and output|No unauthorized sensitive disclosure|
|Content fingerprints|Request registration|Changed content under same identity detected|
|Tracing/metrics|Query, settlement, save and recovery|Locate delays and establish phase results|
|Throttling/isolation/breakers|Browse/update entries and remote resources|Contain faults while confirming accepted updates|

These are design tasks, not a claim all exist. Content fingerprints and ownership checks do not authenticate callers, as Part V, Chapter 25, explains.

Recommendations/images may degrade; payment cannot falsely report success or rejection after timeout. Correlate original requests, journals, ordinary saves and recovery, without SPP network catches.

## Produce an Integrated Record

Check Chapters 29–30 numeric tables, then cancellation, return or reservation branches. Verify states, receipts, conservation, duplicates, versions, insufficient stock and unknown outcomes.

Keep performance comparison focused: serial versus parallel independent queries under identical business and resources, recording latency, overlap, throughput, errors and use. Add separate cache/projection comparisons if implemented. Appendix C holds detailed methodology.

Record source version, APP strategy, PHY resources and coverage. Business correctness, honored configuration and confirmable deployed results together complete the practice.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](31-returns-and-reservations.md) · [Next Chapter](../part-07-advanced-cases/33-banking.md)
