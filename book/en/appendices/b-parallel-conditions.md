# Appendix B — Conditions for Exchange, Reordering and Parallelism

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

We first prove fixed quantum-delta commutativity, including changes to the same property. We separately prove independent read/write conditions for general activities, then discuss implementation, bounds and failures.

## B0 Quantum-Service Commutativity

Let x be a state vector within one business dimension. A and B express prepared δ_A and δ_B. Identities, amounts and units are fixed; intermediate balances do not redefine deltas. If both settle:

```text
F_A(x) = x + δ_A
F_B(x) = x + δ_B
A then B: F_B(F_A(x)) = (x + δ_A) + δ_B
B then A: F_A(F_B(x)) = (x + δ_B) + δ_A
By associativity and commutativity of addition:
(x + δ_A) + δ_B = (x + δ_B) + δ_A
```

Both orders produce the same state even with overlapping coordinates. From 1000, −100 and −200 both give 700. Transfers from A to B and C can be written:

```text
x = (1000, 0, 0)
δ_A = (−100, +100, 0)
δ_B = (−200, 0, +200)
Either final state = (700, 100, 200)
```

Each delta and their joint result conserve. Intermediate states can differ, but settled totals cannot. Using intermediate values to recalculate amounts changes the delta set being compared.

For n changes and any permutation π:

```text
x_final = x + Σ δᵢ = x + δ_π(1) + … + δ_π(n)
```

Every permutation is a finite sequence of adjacent exchanges, each preserving results. This compares the same settled set. Which competing requests settle and how faults avoid lost/duplicate deltas are separate contracts, treated in B7–B9.

## B1 Fact Granularity

View state as a map from fact locations to values:

```text
(buyer A, tier) → VIP
(goods P, price) → 60
(order O, discount) → 12
```

Different objects of one type are different locations; properties of one object may also be distinct. Include actual mapper completion: copying a whole object writes more than one visibly used field.

R_A contains every location possibly read by A, W_A every changed location. Reads in conditions count. Resolve aliases before deciding whether names denote the same fact.

## B2 Assumptions

The following proof assumes:

1. A and B are deterministic, terminating and successful over the input range; rejection and faults are separate.
2. R and W cover every effect, including conditions, mapping and hidden access.
3. Activities use only their read facts and modify only declared writes, with no additional external effects.
4. No third activity changes relevant inputs during comparison.
5. Implementation correctly realizes independent logical writes, with final observation after both finish.

The last excludes corrupting adjacent fields, partial-object reads or undefined memory behavior as substitutes for the logical model.

## B3 Sufficient Independence Conditions

```text
W_A ∩ R_B = ∅   B does not read A's writes
W_B ∩ R_A = ∅   A does not read B's writes
W_A ∩ W_B = ∅   no shared writes
```

∩ denotes intersection and ∅ the empty set. Read sets may overlap; both reading one stable price does not overwrite it.

## B4 Step-by-Step Proof for Successful States

Start with any qualifying x. Let a be the result of A alone and b of B alone.

First, A modifies only W_A, disjoint from R_B. B reads the same facts in a as in x.

Second, B is deterministic, so preceding A does not change B's calculated writes. Symmetrically, preceding B does not change A's writes.

Third, compare each final position:

|Location|A then B|B then A|
|---|---|---|
|In W_A|A's value, not overwritten|The same A value|
|In W_B|The same B value|B's value, not overwritten|
|Outside both|Original x|Original x|

Disjoint writes assign each location exactly one category. Final states are equal. Deterministic outputs from those facts are equal too, completing the proof within assumptions.

## B5 Why Parallel Execution Can Be Considered

Neither activity changes the other's reads, and disjoint writes do not overwrite. Correctly protected interleavings can therefore produce the same final state.

Business must not observe unfinished whole results. Two fields may be updated at different moments, exposing a partial record. Require publication after joining, appropriate isolation or common commit if only complete results are visible.

The proof does not automatically supply thread safety or atomicity. It establishes logical permission; runtime supplies scheduling, writes and publication.

## B6 Counterexample with a Dependency

A sets line amount to 120; B copies current line amount into subtotal. Both initially zero:

```text
A then B: line = 120, subtotal = 120
B then A: line = 120, subtotal = 0
```

A's writes intersect B's reads. Concurrent B may likewise read zero. Independent line calculations can overlap, but summation waits.

## B7 Commutative Mathematics, Lost Implementation Updates

A adds ten and B twenty to 100. Mathematics gives 130 in either order; read-then-write can lose a delta:

|Time|A|B|Balance|
|---|---|---|---:|
|1|Read 100||100|
|2||Read 100|100|
|3|Write 110||110|
|4||Write 120|120|

A's ten is overwritten. Atomic deltas, exclusion or appropriate isolation prevent this only when implemented. Shared writes do not satisfy B3; other safe concurrency needs another proof.

## B8 Bounds Change Accepted Results

From 100 with no overdraft, A debits 80 and B 30:

```text
A first: A succeeds, balance 20; B rejects; final 20.
B first: B succeeds, balance 70; A rejects; final 70.
```

The algebraic total is order-independent, but acceptance and final balance are not. A contract may permit settlement order to arbitrate competition, but cannot claim each request's result is independent of order.

## B9 Failures and External Observations

A and B write disjoint parties. If A commits then B fails, A remains; if B fails first and stops the scenario, A never occurs. Successful-path exchange does not prove equivalent failure processes.

Joint success needs common commit or recovery. Permitted partial results need explicit states. A parallel fault requires knowing which other branches completed, not merely terminating a waiting thread.

Notifications are observations too. Announcing success after debit but before credit exposes an incomplete promise. Publish after confirmation, with duplication and delivery handling.

## B10 Joining Parallel Validations

Two validations reading stable facts without mutation can return independently. If both must pass:

```text
Continue = A passes AND B passes
```

AND is order-independent. Choosing the first completed rejection makes displayed reasons schedule-dependent. Fixed priority requires collecting and selecting results accordingly. Immediate-stop control must specify scope and effects on other branches.

This defines the contract needed, not a claim arbitrary bare checks already have it. Appendix E and editorial records state expression limits.

## B11 Extending to Groups

Build read/write sets and dependency edges for production, conflicts, observation and commit. Apply sufficient independence to unrelated nodes; legal sequences satisfy all prerequisites.

Two legal sequences differing only in independent-node order can be transformed by adjacent independent exchanges. Each preserves successful results. Shared writes, dynamic aliases or external state prevent direct use of this corollary.

## B12 Ordinary Updates with Complete Inputs Commute

Within one transaction's save phase, built-in updates contain no business queries, calculation or checks. Queries/calculations and quantum changes have prepared facts. Any post-settlement calculation/check completes first in serial groups. Let P be complete facts to save; Uᵢ persists its part Pᵢ.

Writes do not depend on another save's result. Different services save different locations; if they overlap, both save the same already fixed P value.

|Location k|Final Value in Either Order|
|---|---|
|Only A saves|P_A(k)|
|Only B saves|P_B(k)|
|Both save|P_A(k) = P_B(k) = P(k)|
|Neither saves|Original value|

Thus:

```text
U_B(U_A(x; P); P) = U_A(U_B(x; P); P)
```

Adjacent exchange extends to any number, allowing concurrent saves after quantum work followed by a join. Physical implementation still must share transaction context, protect writes and honor common commit or recovery.

Prepared order status, amount and receipt can save independently. Receipt calculations based on settlement must complete first; this proof exchanges ready saves, not calculation with saving.

Built-in updates prevent hidden business access/calls. Serial groups enforce preparation. Complete input and consistent save relations support the proof. Same-identity insert/delete conflicts, foreign-key ordering and physical concurrency are editorial KI-011.

Different transactions can have different P and still require version/conflict protection. Intra-boundary exchange does not prove arbitrary cross-transaction overwrite commutativity.

## B13 Why Quantum Work Can Move Earlier

For quantum Q and ordinary U within one boundary:

1. The scenario prepares Q's identity, deltas and bounds; U does not complete or change them.
2. U saves facts, does not produce Q's business calculations and does not modify quantum properties.
3. Q's fixed deltas satisfy B0.
4. Q completes settlement facts; required further calculations/checks run in serial groups before U under B12.

Q therefore has no business need to await U. Delaying saves does not affect Q's inputs. Saves may need Q results, so dependency points from quantum results to saving. The compiler can concentrate Q first.

```text
Prepare scenario inputs
          ↓
Q: concentrated quantum execution, unordered or merged
          ↓
Complete settlement facts
          ↓
Serial group: further calculations/checks as needed
          ↓
U: concurrent ordinary saves
          ↓
Join and complete under the transaction contract
```

Commutativity explains Q's internal order, complete-input saving U's internal order, and one-way dependency cross-category scheduling. Quantum-first planning retains explicit settlement-calculation-validation-save dependencies.

Reordering stays within one boundary, without merging independent transactions or turning physical phases into atomic commit. LOCAL can commit common resources; phased backends retain protocols. Editorial KI-012 tracks implementation coverage.

Sources: [participant execution](../../references/spp-participant-execution.md), [transactions/storage](../../references/transaction-storage-v1.md) and scenario composition design (maintainer reference: `../../../scenario/docs/Composit.docx`).

---

[Appendix Contents](README.md) · [Full Book Contents](../README.md) · [Previous](a-service-model.md) · [Next](c-performance.md)
