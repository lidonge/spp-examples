# Part VI — Complete Petstore Practice

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

The first five parts established models, cooperation, language, consistency and technical separation. We now apply them to one buyer's complete journey through Petstore models, scenarios, APP and PHY: zero facts, funding, inventory receipt, quotation, ordering, payment, shipping and subsequent handling or failure.

Illustrative amounts and quantities can be checked step by step; snippets link to real files. Existing implementations and evidence are distinguished from proposed caching, on-demand data and full security/governance extensions. Experiments and detailed arguments remain in the appendices.

## A Code-Size Comparison with Java

The comparison below uses the recorded source baseline described in Appendix F7. Later expanded formatting and English/USD presentation change physical line counts; these historical figures are not counts of the current downloadable files.

The four-domain, 34-scenario example covers membership, goods, cart, orders, payment, fulfillment, returns and reservations. Its source generated the following Java:

|Content|Files|Code Lines|
|---|---:|---:|
|SPP business models, services and scenarios|63|999|
|Business enums|2|18|
|APP and PHY configuration|8|331|
|Maintained S++ source total|73|1,348|
|Tool-generated Java|962|100,151|

Counts exclude blank lines and comments but include brace-only lines. About one thousand business lines plus three hundred configuration lines expand into about one hundred thousand Java lines, including models, request/response types, interfaces, implementations and integration. Business specialists mainly maintain SPP; tools deterministically produce expanded models, calls and persistence.

A rough Spring Boot + MyBatis + Lombok estimate is:

|Java Scope|Maintained Code and Configuration|
|---|---:|
|Conventional monolith for 34 scenarios using local transactions|About 6,000–10,000 lines|
|Including this example's domain calls, conserved transactions, durable idempotency and recovery responsibilities|About 10,000–20,000 lines|

Java, SQL/Mapper and necessary configuration are counted together, as with S++ source plus configuration. Dependencies, tests, pages and generated accessors are excluded. Existing frameworks and components are assumed to handle repetition; developers need not rewrite generated output line by line.

The rough comparison is thus about 1,350 maintained S++ lines versus ten to twenty thousand conventional Java-project lines. Java ranges are responsibility-based estimates, not independently measured implementations. One hundred thousand is actual generated volume, a different quantity. [Appendix F7](../appendices/f-sources-and-evidence.md#f7-petstore-code-size-statistics) gives methods and assumptions.

## Connecting to the First Five Parts

|Practice|Principles Applied|
|---|---|
|Identify roles, contracts and responsibilities|Part I completeness and polymorphism; Part III models and services|
|Arrange queries, calculations, validations and saves|Part II dependencies and concurrency; Part III scenarios|
|Settle money/inventory and handle failure|Part I quantum services; Part IV transactions, conservation and recovery|
|Configure storage, requests, security, performance and deployment|Part III layers; Part IV guarantees; Part V technical capabilities|

Check objective completeness, ready inputs, consistent settlement and storage, and whether technical strategies honor them.

## Contents

- [Chapter 28 — Identifying Roles, Behavior and Services from Requirements](28-petstore-modeling.md)
- [Chapter 29 — Zero Opening, Funding and Inventory Receipt](29-opening-and-transfers.md)
- [Chapter 30 — Quotation, Ordering, Payment and Shipping](30-order-lifecycle.md)
- [Chapter 31 — Cancellation, Returns, Reservations and Failure Handling](31-returns-and-reservations.md)
- [Chapter 32 — Technical Configuration, Deployment and Integrated Verification](32-validation-and-performance.md)

[Full Book Contents](../README.md)
