# Chapter 24 — Performance Through Caching and On-Demand Data

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Performance means reducing repeated access and unnecessary data as well as concurrency. SPP retains role organization; APP selects query, transfer and output strategies; PHY supplies resources.

## Observe Performance Before Choosing an Optimization

APP after/failure can collect query and scenario names, durations and faults, identifying whether product access or saving dominates. No timing code enters SPP. A Java collector can integrate metrics through PHY.

Current interceptors only expose invocation metadata. They cannot modify participants or return a cached answer while skipping a query. Observation fits directly; caches, field selection and response projection belong in query, repository or output adapters.

## Caches Reduce Repeated Access

Ten cart lines may reuse product information. Request caches reuse facts within a call; process caches share across requests; shared caches reduce source-domain reads across application instances.

Remote product names and categories can be cached locally. Business still calls role queries; technical cache hits complete facts without explicit “cache first, database next” in scenarios.

Keys must distinguish participant identity, loaded fields and version. Having a name does not imply having price and status. Freshness follows purpose: name display may tolerate age, while settlement needs authoritative mechanisms. Cached balances can support display or preparation, not settlement.

## On-Demand Queries Reduce Read Sets

A role chain may expose many properties while quotation needs only tier, price and quantity. Compile-time use analysis can form a required set, with queries retrieving its sources.

Buyer may include name, avatar, address and tier. Discount only needs tier; ordering adds address. Role granularity remains Buyer while loaded volume decreases.

Retain identity, internal baselines and loaded-property markers. An unloaded address must not become an empty saved address. Partial loading and saving need a protocol, not merely shorter SQL.

## On-Demand Responses Reduce Output Sets

Calculation input and display needs differ. Quotation may use addresses and complete pricing facts while showing only names, quantity, unit price and total.

APP can define output sets per entry: order summaries, detailed lines, or payment receipt and system result. Roles and contracts retain meaning; output adapters select allowed needed fields.

Queries determine retrieval; response selection determines disclosure. Internal sensitive facts need not reach the page. Selection must cooperate with permissions, masking and replay.

Current generated web interfaces mainly return completed input objects and result information. General projection, role-use query pruning and multilevel caches need further implementation and scope verification. These are optimization methods, not universally completed capabilities. Appendix C13 specifies conditions.

## Batching and Execution Paths

Independent goods can use batch or parallel queries. Quantum services can merge requests. Ready ordinary updates can save concurrently.

Calculations and validations normally run in the scenario process, avoiding network calls for small work. Compressing large payloads saves bandwidth but adds encoding cost and should follow measurement.

Measure full latency, read/output volume, cache hits and source calls. Faster lists that cause many later detail reads may need adjusted data sets. Appendix C gives experiments.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](23-separation-benefits.md) · [Next Chapter](25-security-services.md)
