# Appendix D — Quantum Services and Conservation Mechanisms

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Balances and inventory explain deltas, conservation, bounds, atomic settlement and inverses. Each conclusion separates mathematical grounds from execution conditions, avoiding conservation arithmetic as a substitute for commit guarantees.

## D1 Changes as Vectors

The minimum quantum service is a pair of properties with equal opposite changes in one dimension. A larger vector can embed that pair or combine several services. State dimension differs from minimum service granularity.

For accounts A, B and C, A transfers 100 to B:

```text
x = (1000, 200, 50)
δ = (−100, +100, 0)
x' = x + δ = (900, 300, 50)
```

Coordinates identify complete participants and properties, not merely “balance.” Units and precision must agree; inventory coordinates are per goods identity.

## D2 Conservation Proof

Define total in one dimension:

```text
Q(x) = Σ xᵢ
Q(x + δ) = Σ(xᵢ + δᵢ) = Σ xᵢ + Σ δᵢ
Σ δᵢ = 0  ⇒  Q(x + δ) = Q(x)
```

Before and after totals are equal exactly when deltas sum to zero. −100 +100 +0 qualifies; debit 100 and credit 99 leave −1. A fee transferred to another account requires that real destination in the model.

This proves the applied complete vector. Crashing after debit before credit can still violate actual conservation, so joint commit is necessary.

## D3 Prove Independent Dimensions Separately

For available, reserved, sold and supply of goods P:

```text
After receipt:       (10, 0, 0, −10)
After reserving 2:    (8, 2, 0, −10)
After shipping 2:     (8, 0, 2, −10)
```

Each sums to zero. Goods Q needs a separate equation; one missing P and extra Q do not prove P correct. Money and item counts cannot be added. Exchange and unit conversion require rates, units, differences and rounding policies.

## D4 Prepared Inputs and Actual Bounds

The caller prepares fixed amount a and postsettlement bounds. Execution uses current x, not an earlier snapshot:

```text
Candidate xᵢ' = xᵢ + δᵢ
Require Lᵢ ≤ xᵢ' ≤ Uᵢ
```

null disables the corresponding side. Participant/contract facts determine limits before invocation; execution handles dynamic balances.

Two debits of 80 may both see 100. After one leaves 20, the other's −60 candidate rejects. Checking and protected writing belong to one mechanism, not a check followed by unprotected write.

## D5 Whole-Group Settlement

Success applies the entire δ; rejection applies none of the group. Partial unfinished state must not be published as success.

A local backend can protect reads, calculate, validate and write in one database transaction. Actual connection, isolation or atomic conditions and transaction capability determine guarantees.

Cross-resource execution needs coordination/recovery. A declared boundary does not coordinate independent connections automatically. Later ordinary failure cannot locally roll back already committed quantum phases.

## D6 Merged Submission and Delta Aggregation

Prepared services have order-independent joint results under B0, so one request can carry several without sequential send-and-wait order. The executor arranges changes and common submission.

A merged request can preserve individual changes, identities, bounds and result associations. If allowed, aggregate by complete identity and dimension:

```text
A → B 100: δ₁ = (−100, +100, 0)
B → C 30:  δ₂ = (0, −30, +30)
Net δ = δ₁ + δ₂ = (−100, +70, +30)
Net sum = 0
```

Zero-sum deltas retain conservation after aggregation. Communication merging differs from netting: one request can retain original details. Per-step and net-value bounds need not agree.

From (0,0), A→B100 then B→A100 nets zero. Final-only checks pass; non-overdraft checks reject the first step. The contract must select the semantic boundary instead of assuming conservation permits temporary overdraft.

With n changes, fixed request overhead h and per-change transmission p:

```text
Separate communication = n × h + n × p
Merged communication = h + n × p
Fixed overhead saved = (n − 1) × h
```

Data still travels. This is not system timing prediction: size, response details, sharding and protocol affect savings. One submitted request may still cause backend cross-resource communication.

Keep duplicate detection, original interpretation and recovery evidence. Net zero does not mean no business occurred. The objective is reduced communication without altered meaning or guarantees.

## D7 Request Identity and Idempotency

Identity binds immutable amounts, endpoints, group and bounds. Successful same-identity retries return original results without reapplying δ; changed facts conflict.

Durable identity/results must relate reliably to actual writes. Crashing between balance and dedupe recording can duplicate credit; recording success first can claim a nonexistent update. Backends must resolve this commit relationship.

## D8 Why Inverse Transactions Preserve Later Changes

Original x, settled δ and later net e give:

```text
Before inverse = x + δ + e
After inverse = x + δ + e − δ = x + e
```

Thus e remains. 100 +50 +20 −50 =120; restoring 100 erases twenty.

The system automatically inverses original records without developer reverse services. It must preserve exact components and identity, additive meaning and deduplication. Assignment or irreversible external effects do not satisfy this proof.

## D9 Inverses Versus Subsequent Business

Failure recovery restores original quantum effects. Original location, inverse constraints, durable results, deduplication and recovery are system duties, with APP technical policy.

Later partial refund, reversal or fees are new business. A partial amount or deducted fee differs from −δ and needs its own eligibility/formula. Original inverse −δ must not be confused with a new δ′.

## D10 Unknown Outcomes and Retry

Disconnection after commit but before response leaves timeout with possibly changed balance. Stable-identity lookup distinguishes confirmed success, rejection, protocol-confirmed nonexecution and unknown.

Unknown does not mean unexecuted. New identity may transfer twice; immediate compensation may reverse something that never occurred. Confirm under protocol or wait for recovery evidence.

## D11 Boundaries and Implementation Coverage

|Relation|Required Actual Guarantee|
|---|---|
|LOCAL|Same JVM, actual database/schema, shared connection/commit resources|
|Non-LOCAL mixed phases|Defined quantum/ordinary order, durable outcomes and recovery|
|REQUIRED|Reuse outer boundary, no independent commit|
|REQUIRES_NEW|Independent resources/propagation and outer-failure handling|
|Unsupported propagation/protocol|Explicit build/deployment rejection, no silent weakening|

Appendices E/F describe example support. Names and passing test counts alone do not prove arbitrary resource combinations.

## D12 Value Uncertainty After Settlement and Observation

At preparation the query sees b; this request settles δ. Let C contain other changes effective before later observation. In the same additive dimension:

```text
b_observed = b + δ + Σ eⱼ    (j ∈ C)
```

Confirming δ without knowing C cannot determine the observed balance from b+δ alone. With b=1000, δ=−100 and another e=−200:

```text
Other request not effective: C = ∅, observed 900
Other request effective: C = {e}, observed 700
```

Both assume this debit settled. Superposition here is epistemic uncertainty after settlement and before observation, not two stored balances or physical probabilities/amplitudes. Confirmation does not identify every concurrent change included in observation.

For a fixed settled set:

```text
(1000 − 100) − 200 = (1000 − 200) − 100 = 700
```

This does not prove every request can settle. From 100, −80 and −30 cannot both satisfy zero lower bound. Order/arbitration can determine rejection. Candidate states pass through bounds; not every algebraic value is legal.

Confirmation answers whether this delta succeeded; observation what the property is then. A preparation query does not freeze later changes and settlement does not fix b+δ. Observations have explicit read semantics and can be followed by new changes.

Lock-read/calculate/overwrite determines a result during protection. Quantum deltas defer dynamic values and bounds to settlement. This distinction does not prove a lock-free backend: short locks, atomic conditions or coordination may still protect delta application and commit. Evidence establishes actual capability.

Sources: [quantum bounds](../../references/quantum-call-bounds.md), [transaction/storage](../../references/transaction-storage-v1.md), [environments](../../references/deployment-environments-and-physical-defaults.md). Unresolved contracts are outside the manuscript in [known issues](../../编辑工作/known-issues.md).

---

[Appendix Contents](README.md) · [Full Book Contents](../README.md) · [Previous](c-performance.md) · [Next](e-language-and-build.md)
