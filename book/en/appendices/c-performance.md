# Appendix C — Performance Models and Experimental Methods

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Starting with one call, we derive serial, parallel and merged execution, then critical paths, capacity, completion probability and experiments. All numeric examples are hypothetical, not Petstore measurements.

## C1 Cost of One Call

Along its actual path:

```text
lᵢ = cᵢ + eᵢ + qᵢ + tᵢ + dᵢ
```

|Symbol|Meaning|
|---|---|
|cᵢ|Transfer and round-trip cost|
|eᵢ|Encoding, decoding and adaptation|
|qᵢ|Queueing for service, connections and resources|
|tᵢ|Net business work and resource access|
|dᵢ|Uncounted transaction setup, coordination and commit|

Do not double-count. If server duration includes commit, decompose it or use whole lᵢ without another dᵢ. Overlapping intervals require path analysis, not simple addition.

## C2 Why Serial Calls Accumulate

If each call begins after the preceding complete return, intervals do not overlap:

```text
T_serial = h + Σ lᵢ + u
```

h prepares common input; u is shared postprocessing/commit. Do not recount branch transactions already in dᵢ.

With equal c and d, omitting other costs:

```text
T_fine_serial = Σ(c + d + tᵢ) = n(c + d) + Σ tᵢ
T_one_call = c + d + Σ tᵢ
Difference = (n − 1)(c + d)
```

The difference comes from repeated boundaries. It assumes comparable work/results and genuinely mergeable communication and commits. Independent business phases cannot be merged just to lower a formula.

## C3 Independent Parallel Branches

With simultaneous starts, ready inputs, no mutual waits and no extra contention, completion is the last branch finish:

```text
T_parallel = h + max(l₁, l₂, …, lₙ) + j + u
Savings = Σ lᵢ − max(lᵢ) − j
Net gain requires: j < Σ lᵢ − max(lᵢ)
```

j is additional scheduling/join overhead. Two 1-ms tasks with 3-ms overhead take 2 ms serially but 4 ms in parallel. Small work may not justify it.

## C4 One Communication and One Commit

If one entry carries independent internal work, resources suffice and actual common commit exists:

```text
T_combined_parallel = c + d + max(tᵢ) + j
```

This reduces boundaries and overlaps work. Remote branches still have their own communication, and phased quantum/ordinary commits retain phase costs. SPP syntax alone cannot remove them.

## C5 A Complete Numeric Example

Let h = 5 ms, l₁ = 40, l₂ = 70, j = 3 and u = 10:

```text
T_serial = 5 + 40 + 70 + 10 = 125 ms
T_parallel = 5 + max(40, 70) + 3 + 10 = 88 ms
Savings = 37 ms
Speedup = 125 / 88 ≈ 1.42
```

If contention increases l₂ to 110:

```text
T_parallel_contended = 5 + 110 + 3 + 10 = 128 ms
```

It becomes slower than original serial execution. Measure actual branch times rather than retaining unchanged-duration assumptions.

## C6 Dependency Graphs and Critical Paths

For an acyclic graph with duration t(v), unlimited resources and no scheduling overhead:

```text
E(v) = t(v)                         if v has no predecessors
E(v) = t(v) + max{E(p)}              for predecessors p
T_ideal = max{E(v)}                 over terminal nodes
```

A node waits for every predecessor; the latest determines its start. Computing E topologically gives the longest dependency path.

Queries of 40 and 70, quotation of ten and settlement of twenty yield:

```text
E_buyer = 40
E_goods = 70
E_quote = max(40, 70) + 10 = 80
E_settlement = 80 + 20 = 100
```

Scheduling, queues and retries add or change durations. Improving the 40-ms branch cannot shorten the critical 70-ms branch.

## C7 Lower Bounds with Finite Resources

For homogeneous resource work W and k equivalent slots:

```text
T ≥ max(CP, W/k)
```

Critical-path activities cannot overlap, requiring CP. Over interval T, k slots perform at most k×T work, which must reach W.

Do not treat all network waits as CPU work or database connections as CPU slots. Model heterogeneous bottlenecks separately; thread count is not automatically k.

## C8 Latency and Throughput

Parallelism can reduce one request's time while consuming several connections. If database work capacity is fixed and work unchanged, throughput may not rise.

Under stable load and a fixed boundary, average in-flight L, throughput λ and average residence T satisfy L = λ×T. Summing occupied time over a window and averaging by requests/time explains the relationship. It requires stability, not a continually growing queue, and averages rather than high percentiles.

Measure latency, throughput, concurrency and utilization together. One-request improvement does not establish capacity.

## C9 Comparable Experiments

Keep inputs, scale, relationships, eligibility, commit guarantees, protocols and resources equal. Change only the studied factor. After warmup, alternate repeated trials to avoid cache or JIT favoring a fixed order.

Serial/parallel comparison keeps deployment unchanged; local/remote is a separate experiment. Do not simultaneously alter threads, storage, commits and rules and attribute everything to parallelism.

Observe critical paths at low load, then increase concurrency to locate queueing, rejection and saturation. Branch start/end events verify overlap. Artificial delays establish scheduling, not real workload performance.

## C10 Metrics and Reports

Keep request start/end, result, retries and branch associations. Report median and percentiles from sorted durations; nearest-rank p95 is item ceil(0.95×N), with the method stated.

Report success, business rejection, technical failure and timeout separately. Do not discard slow failures and report success averages alone. Define throughput as completed requests or successful business, and distinguish replay from new settlement.

Retain versions, build, resources, workloads, warmup, rounds, correctness, raw data and analysis. Functional regression is not this benchmark.

## C11 Remote Dependencies and Whole-Business Completion

This section asks whether valid business completes within a deadline. Eligibility rejection is not technical unavailability, and per-request completion probability is not time-based availability.

If every remote call must succeed, with Sᵢ its in-deadline success:

```text
P(completion) = P(S₁ ∩ S₂ ∩ … ∩ Sₙ)
```

Only with independence, no retry/alternative/partial-completion policy and equal p:

```text
P(completion) = pⁿ
p = 0.999, n = 20:
pⁿ ≈ 0.980189 ≈ 98.02%
```

For 0 < p < 1, each required call multiplies probability by a factor below one. This proves cost in that model, not universal incompatibility of microservice scalability and availability.

Shared networks, databases and hosts invalidate independence. Use joint probability or measurement instead. Retry, redundancy, isolation, alternatives and recovery change event definitions and structure and require new models.

## C12 What Concurrency, Merging and Local Deployment Change

Serial and parallel require the same intersection if scheduling does not change success conditions. Starting order alone does not remove branch faults. Parallelism mainly reduces time; fixed deadlines may see fewer accumulated-time timeouts, not automatic availability improvement.

Merged requests reduce communication and protocol boundaries. Multiple deltas to one executor can arrive together, reducing request-level failures and confirmation cost. The executor still must apply every change; one entry does not make internal resources infallible.

Local calculation/checks remove separate remote dependencies without changing logical service count. Host and storage still fail, requiring their own statistics. Do not replace pⁿ by p and call it measured improvement.

The book's latency mechanisms are exposed independence, quantum request merging and local small operations. They do not prove SPP fixes remote-dependency availability.

Use C9–C10 with equal guarantees/resources, measuring remote calls, timeouts and failures. Keep slow failures in statistics.

## C13 Property-Use Analysis and Multilevel Caching

### Determining Query Sets

For role R, Uses(R) includes properties read by scenarios, calculations, validations, quantum calls and bound expressions within the compilation scope. Follow calculation calls, mappings and relationships, not merely direct expressions.

Queries also locate and confirm identity and obtain saving baselines:

```text
Fields(R) = Uses(R) ∪ NeededIdentity(R) ∪ NeededBaseline(R)
```

Outputs count as use too. APP and output-protocol dependencies need analyzable implementation or explicit declarations. Without evidence, choose conservative fields rather than treating unrecognized access as absent.

Mapped attributes require source dependency sets: Buyer tier may come from a role and address from a root entity. Preserve identity/mapping/association requirements; on-demand querying is not arbitrarily skipping necessary role relationships.

Correctness requires every property to be completed from its source before use. Unloaded differs from actual null or zero. Pruning must not make defaults business facts or replace stable input participants.

### Partial Queries and Saving

Saving must not overwrite unloaded facts with defaults. Loaded-range metadata, explicit writes or another preservation mechanism can protect them; valid baselines still support versions.

Analysis, reading, mapping and saving jointly implement optimization. Fewer SELECT columns or response fields alone do not prove whole-business equivalence.

### Cache-Hit Conditions

Request caches reduce repeated scenario reads; process caches reuse stable facts across requests. Remote source facts can be locally cached then mapped.

Keys include source domain, identity and isolation conditions, not only type or incomplete numbers. Records state loaded sets. If requested fields F and cached C satisfy F ⊆ C, field coverage qualifies; otherwise fetch missing fields or refresh.

Versions, notifications or expiration offer different freshness guarantees chosen by requirements. Missing identity, technical read failure and expiry differ; old confirmation cannot be reused unconditionally.

Cache speeds retrieval, not actual quantum bounds/conservation. Display balances can be cached, while settlement uses authoritative facts. Protected ordinary transaction reads also need appropriate version, isolation and baseline conditions.

### Gains and Verification

Pruning reduces transfer, reading and mapping but does not guarantee scan time proportional to columns. Cache savings depend on hits, refresh, size and contention.

Keep roles, rules and save results fixed. Record fields, payload, source calls, hits, latency and refresh costs. Test missing dependencies, partial hits, source changes, conflicts and saving unloaded fields to ensure unchanged meaning.

These are methods and correctness conditions, not acceptance evidence that current compiler implements generic pruning/caching. Editorial KI-014 tracks scope.

Sources: S++ concepts (maintainer reference: `../../../../spp/docs/cn/concept.md`) and [deployment configuration](../../references/deployment-environments-and-physical-defaults.md).

---

[Appendix Contents](README.md) · [Full Book Contents](../README.md) · [Previous](b-parallel-conditions.md) · [Next](d-quantum-contracts.md)
