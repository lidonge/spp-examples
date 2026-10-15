# Chapter 10 — Parallel Execution and Service Call Costs

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Traditional microservices often seek scalability, isolation, independent deployment and scaling by dividing responsibilities into smaller services across processes or nodes. Responsibilities become more focused, but a complete scenario traverses more remote calls.

Smaller granularity may shorten individual business work while increasing the relative cost of communication, encoding, queueing and coordination. Serial calls accumulate waits and can substantially increase response time. More required remote dependencies also increase opportunities for a failure preventing the whole activity, pressuring scenario availability.

SPP overlaps atomic services to reduce response-time growth caused by finer granularity, retaining detailed business expression while overlapping independent waits. This chapter addresses response time; concurrency does not fix the availability issue introduced by those dependencies.

## How Fine Granularity Extends Response Time

Assume ordering queries buyer in 40 milliseconds, goods in 70, then calculates in 10. Sequential execution takes 120. These illustrative figures explain structure, not measured performance.

Only quotation needs both query results. Neither query needs the other, so sequencing them adds waits that could overlap.

Request encoding, round trips and service queues extend serial waiting further. Computation may be brief while most scenario time is spent calling and waiting.

## How Atomic Concurrency Reduces Waiting

Scenarios explicitly express participants and dependencies. Ready independent queries run together, followed by quotation:

```text
Serial: buyer 40 ─ goods 70 ─ calculation 10 = 120 ms

Concurrent: buyer 40 ┐
                     ├─ calculation 10 ≈ 80 ms + scheduling/join overhead
            goods 70 ┘
```

Work remains the same, but waiting overlaps. The scenario waits for the slower 70-ms query, then calculates for 10. It mitigates accumulated serial-call latency.

The basis is clear service responsibility: built-in queries complete facts; calculations and validations execute separately; quantum transactions commute; prepared ordinary updates save concurrently. Explicit dependencies preserve required waits and overlap independent work.

## Reducing Serial Waiting and Repeated Communication

Concurrent queries overlap remote waits. Quantum commutativity permits unordered execution and merged requests. Complete-input ordinary updates save concurrently. Calculations and validations normally execute locally in dependency order, avoiding remote calls for tiny formulas and conditions.

Business responsibilities can therefore be fine-grained without sequential waiting for every service. Concurrency overlaps waiting, merging reduces repeated communication, and local execution reduces small-service overhead. Together they shorten the path.

## Preserve Dependencies and Measure Gains

Real dependencies remain. Subtotal needs line amounts. If receipt preparation follows quantum settlement, a serial group must arrange calculation and validation before saving.

Concurrency also needs resources. A database processing one request at a time still queues both queries internally. Insufficient connections or threads can worsen contention. Compare identical rules and commit guarantees, and measure response time, throughput and resource use.

Role-oriented architecture naturally organizes concurrency by responsibility and dependency, reducing latency growth while preserving fine modeling. Appendix C gives time models, resource conditions and experiments; the next chapter relates service to deployment granularity.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](09-service-coordination.md) · [Next Chapter](11-deployment-granularity.md)
