# Chapter 11 — Minimum Service Granularity and Deployment Principles

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Before asking how finely to split services, define the lower boundary. In SPP, a quantum service is conservation between a pair of quantum properties. Other services have a minimum granularity of an operation on a role. This business model does not split them further.

The boundary determines responsibilities; deployment determines locations and resource use. Deployment still depends on dependencies, communication cost and scaling requirements.

## A Pair of Conserved Properties Is the Quantum Minimum

A transfers 100 to B: A decreases by 100, B increases by 100.

```text
A.balance: −100 US dollars
B.balance: +100 US dollars
Sum of changes: 0
```

Keeping only debit or credit destroys the transfer's complete meaning. The pair's conserved change is the minimum; a single property's delta is not a smaller independent quantum service.

Inventory reservation similarly decreases available by two and increases reserved by two for the same goods. The properties may belong to one role or separate participants. Actual source and destination within one dimension are decisive.

Combining quantum services into larger requests does not change that minimum definition. Each basic change remains a pairwise conserved service.

## Other Services Use Role Operations as the Minimum

An ordinary query completes a role's facts, an update saves them, and calculation or validation performs a defined operation concerning a role: query Buyer, save Buyer, calculate OrderLine amount.

A role may have many properties, while an operation uses only some. Eligibility may read only buyer status but still judges Buyer participation. Line pricing uses price and quantity but still calculates OrderLine amount.

Complex calculations reuse calculations and scenarios organize multiple role operations. Splitting a field read, multiplication or comparison into a business service goes beyond SPP's minimum; these are expressions inside the operation.

## Comparing Property-Level Object Operations

Object-oriented code can expose `getName`, `setName` and another pair for address. Individual property reads or assignments can be methods, making code-level operations as small as one property.

SPP defines business services as role operations. Querying and saving Buyer complete and persist required facts. Names and addresses remain properties, but their accessors are not smaller business services. Queries and updates are built-in; scenarios call them and calculations or validations express rules.

SPP therefore has a definite endpoint: pairwise conserved quantum changes or role operations, rather than continuously shrinking the amount of data inside a method.

## Query Properties According to Use

Role granularity does not imply retrieving every property throughout the entire role-playing chain. Business granularity and loaded data volume are separate.

At compilation, property use in scenarios, calculations and validations can be collected into a required set. Generated queries need only complete those facts from their mapped sources.

Buyer may be played by a customer entity. Quotation needs tier, purchasing eligibility needs status, ordering needs address. Queries can obtain those and necessary identity without unused customer data. Buyer remains the operation unit while database reading, remote transfer and mapping volume decrease.

## Reduce Repeated Reads with Multiple Cache Levels

Request caches and shared process caches can reuse facts. One scenario may use an entity repeatedly; different requests may share relatively stable information under an appropriate policy.

Local caching is particularly useful for remote entities. Names and categories need not be fetched from the product domain every time. Cache required facts and complete local roles through the mappings.

These familiar optimizations can be implemented by built-in queries and APP/PHY configuration. Scenarios continue to call role queries. Refresh and invalidation follow requirements, while real money and inventory settlement still uses authoritative quantum mechanisms.

On-demand properties reduce data per read; caches reduce repeated reads. Both mitigate wide roles and long chains without splitting into property services. Appendix C13 states detailed conditions.

## Prefer Local Calculations and Validations

Line pricing, discounts and eligibility can retain separate definitions yet run inside the scenario process. Prepared facts avoid network round trips for brief formulas and conditions.

Definitions remain independently reusable and composable, while one deployment unit can host many services. The model retains minimum responsibilities; runtime groups them by cost.

## Arrange Queries, Quantum Transactions and Saves by Dependency

Queries run locally or remotely according to fact location. Independent role facts can be queried concurrently. Separate scaling or team ownership may justify remote product or customer access.

Within a boundary, quantum transactions precede ordinary updates and can run unordered or merged. After results arrive, serial groups arrange further calculation and validation, then ready updates run concurrently. Deployment must support these dependencies while controlling communication and coordination.

Service and deployment granularity need not coincide. Customer, product and shop responsibilities can share a process or be separated. “Co-location” simply means running multiple services in the same process, such as one Java application calling them locally. Responsibility ownership remains; paths and resources change.

## Deployment Must Honor Transaction Boundaries

Petstore develop hosts four domains in one process with LOCAL. testing separates customer, product and shop applications. The business model is the same, but communication and commit conditions differ.

Shared-process services using a common resource can handle quantum and ordinary changes in one local transaction. Separate processes require supported coordination or explicit phased settlement and recovery. Merely naming deployment distributed provides no joint commit guarantee.

Model at the defined minimum first; deploy by business dependencies, cost, capacity and transaction capabilities. This preserves detailed role services while reducing scenario response time.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](10-parallelism-and-costs.md) · [Next Chapter](../part-03-the-spp-language/12-layers.md)
