# Appendix A — The Service Model and Formal Derivations

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

“Service = participants × behavior” starts business analysis. We explain symbols with a transfer, then decomposition, composition and the precise meanings of equality. Equations use ordinary text readable in Markdown.

## A1 Participants and Behavior Jointly Determine an Activity

A transfers 100 US dollars to B. Participant configuration p includes both and the agreement; behavior b defines debit, credit, bounds and results:

```text
B = p × b
p = {source: A, destination: B, agreement: 100 US dollars}
b = complete the agreed transfer
B = the business activity of A transferring 100 US dollars to B
```

p is not an amount vector, and b not a number for arithmetic multiplication. The product expresses constitution. Replacing B with C changes the activity; replacing transfer with balance query changes objectives and results.

“If either is missing the result is zero” means no defined activity forms without necessary participants or behavior. Missing payee is not a successful zero-amount transfer. Rejection differs from numerical zero.

## A2 Define What Is Compared

State x contains relevant participant facts. For identified A and B:

```text
x = (A balance, B balance)
x₀ = (1000, 200)
Exec(B, x) = (resulting state, result classification, observable records)
```

Success gives (900, 300) and a record connected to this transaction. Rejection preserves (1000, 200) with its reason. Communication failure may temporarily prevent a definite answer and require actual-state lookup.

Business equivalence must specify records. Equal funds with different receipts is weaker than equal original associations and replay results. Service contracts choose observations; proofs cannot silently narrow them.

## A3 Composition of a Complete Service

Here complete service uses the broad traditional meaning, such as order payment: queries, ownership, amount preparation, transfer and records. Addition denotes activity composition:

```text
S = B₁ + B₂ + … + Bₙ = Σ Bᵢ
```

S is whole business and Σ composition. In SPP, services carry individual responsibilities and scenarios organize them. The equation does not require an ordinary service containing all calls. Dependencies, commit boundaries and failures remain part of composition; names alone do not specify execution.

“Transfer + order save” with joint commit differs from fund-first commit and later recovery. Success objectives may match, while failure contracts and guarantees differ.

### Minimum Services and Composition Boundaries

Quantum minimum is conservation between two quantum properties; other minimums are role operations. Field reads, expressions and local assignments stay internal rather than becoming smaller business services.

Auxiliary inputs differ from operation targets. A line calculation can use prepared pricing rules but produces a line-role amount. A transfer contract supplies amount while conservation still concerns the balance pair. Collections, calculation reuse and request merging can cover many units without changing the minimum.

## A4 Distribution over Behavior

If b₁ + b₂ means explicitly organized behaviors on the same participants:

```text
p × (b₁ + b₂) = (p × b₁) + (p × b₂)
```

Left names the whole; right expands responsibilities. Equality requires the same bindings, inputs, sequence, boundaries and observations.

For pricing two lines (60, 2) and (20, 3):

```text
Line 1 = 60 × 2 = 120
Line 2 = 20 × 3 = 60
Subtotal = 120 + 60 = 180
```

Expansion into two prices and aggregation preserves 180 because aggregation reads exactly their results. Moving aggregation earlier or changing per-line rounding requires rechecking.

Distribution explains expansion, not commutativity. Aggregation waiting for prices is a counterexample to arbitrary exchange.

## A5 Distribution over Participants Describes Contributions

A contributes −100 and B +100:

```text
δ_A = (−100, 0)
δ_B = (0, +100)
δ = δ_A + δ_B = (−100, +100)
Result = (1000, 200) + (−100, +100) = (900, 300)
(p_A + p_B) × b_transfer = p_A × b_transfer + p_B × b_transfer
```

Each right-hand term is this behavior's effect on its party, not an independent complete transfer. Otherwise the right side transfers twice.

Contributions can be analyzed separately while commit honors the whole. A-only completion (900, 200) violates conservation. Vector addition does not replace a joint-settlement protocol.

Joint eligibility also limits distribution: two jointly qualified applicants need not each qualify alone. Distinguish local contributions from whole-only rules before decomposition.

## A6 Quantum Commutativity

For prepared identities and deltas δ_A and δ_B, when both settle:

```text
A then B: (x + δ_A) + δ_B
B then A: (x + δ_B) + δ_A
```

Addition makes results equal. Both can affect one property: 1000 minus 100 and 200 gives 700 in either order. The basis is fixed-delta commutativity, not disjoint writes. Appendix B0 gives details.

General queries, checks and calculations still need dependency analysis; Appendix B treats them separately. Bound rejection and recovery require execution contracts.

## A7 Testing Business/Technology Separation

Let F be the logical business transformation, G its implementation, and π the mapping from physical records to business facts. Successful semantics require:

```text
π(G(physical input)) = F(π(physical input))
```

A cents column maps 10000 to 100 US dollars. A 10-dollar transfer must move 1000 cents, not ten. The mapping then preserves the formula.

Full contracts also preserve identity, bounds, failure and duplicate handling. Not changing the business objective does not make technical duration or responsibility zero.

## A8 Constructing a Role-Behavior Model from Object Execution

This section concerns the expressiveness of a modeling method. It does not establish that the current SPP compiler supports every general-purpose program, or that either representation is shorter or faster. Complexity here means that structures, rules and execution steps can continue to compose; it does not mean executing an infinite process completely in finite time.

Consider an explicitly defined object model consisting of object states, operations and their composition. Let state x include object identities, relevant fields and execution position, and let a identify an operation and its inputs. One execution step is:

```text
Object model: x --a--> x′
```

The state must include facts that affect later execution. A hash table includes not only key/value records but capacity and collision rules. If resizing affects later positions, the new capacity is part of the state. If the original model permits alternative next steps, as with concurrent scheduling, this notation denotes a transition relation rather than a single function.

Construct a role behavior for each object operation. Its target becomes a participating role; input values become necessary participants or behavior inputs; state changes follow the original rules. An operation involving several objects lets them play their corresponding roles. Method calls, conditional choices and repetition become behavior composition, branches and repetition.

Let E encode object-model states as role-model states and b_a be the constructed behavior. Each step must satisfy:

```text
Original step:      x --a--> x′
Corresponding step: E(x) --b_a--> E(x′)

Business or algorithm observations:
Obs_role(E(x)) = Obs_object(x)
```

Induction then covers every finite execution sequence:

1. E encodes the initial state with equal relevant facts and observations.
2. Suppose the representations correspond after step k. The behavior for operation k+1 was constructed from its original rules, so the resulting state and observations still correspond.
3. After any finite number of steps, the role model therefore continues to express the process already described by the object model.

If an object-based hash insertion encounters a collision at slot 2, checks slot 3 and writes a record, the role model follows the same steps. If the object model resizes and rearranges records first, the role model must include that migration and switch. Encoding only the final key/value set would discard facts that affect subsequent behavior.

The construction assumes the ability to preserve required state, express original operation rules, and provide necessary choice, repetition and composition. These algorithmic facilities need not mean remote services, business transactions or commercial contracts. Imposing SPP's domain constraints on general modeling would change the subject of the argument.

A reverse construction is also possible: objects hold role-model participant state, methods implement behavior, and coordinating objects organize composition. The two modeling starting points can therefore carry the same computable process under these conditions. Clarity and implementation cost remain separate questions.

## A9 Expressiveness, Domain Brevity and Implementation Capability

The preceding argument is conditional and constructive. Without explaining how state, rules and composition are expressed, merely observing that no counterexample has been found is not a universal proof. A counterexample must likewise identify a missing expressive capability, rather than show that one notation is inconvenient.

Simulation of the real world first needs an observation scope. A chess model records rules, positions and outcomes; it need not also record the material of each piece or every molecule's motion. Simulation here means preserving specified observations between models. Changing the modeling starting point does not make infinite-precision continuous facts or noncomputable rules fully manageable by finite computation.

Three questions can now be separated:

|Question|What Must Be Established|What Does Not Follow Automatically|
|---|---|---|
|Can the modeling method express a complex process?|Constructions for state, change and composition, with corresponding observations|The current compiler implements every required capability|
|Can the domain architecture express commercial services concisely?|How roles, services and scenarios reuse recurring domain structures|Every scientific algorithm fits a few business declarations|
|Can current tools execute a requirement?|Syntax, binding interfaces, representation, execution and resources|A valid model alone guarantees performance and reliability|

S++ obtains much of its brevity from common commercial-service capabilities. Once payment participants, amounts and processing relationships are declared, tools provide standard queries, updates, identity maintenance and technical integration. A new route-search algorithm still has its own complexity; existing Java code can implement it without expanding it into many business declarations.

For external calculation reuse, let C denote the business-required result, J the adapter and implementation, and encode/decode the input/output mappings. The contract requires:

```text
decode(J(encode(business input))) = C(business input)
```

The agreement must also cover precision, missing input and failure semantics. A route-search implementation cannot return straight-line distance when road distance is required and still claim equivalence. Missing road data cannot silently produce a zero distance. Approximation needs a contractual error bound; comparison then asks whether the result satisfies that contract, rather than demanding exact numerical equality.

A pure calculation implementation must not hide data queries, persistence or transactional side effects, or the scenario's dependencies and boundaries become incomplete. Required external facts should first be prepared through queries and then passed to calculation. Persistence remains an update organized by the scenario. Reusing general algorithms must not conceal business responsibilities inside technical adapters.

A complex requirement can therefore use roles for business modeling, APP bindings and adapters for existing capabilities, and PHY for implementations and resources. Missing support in a particular binding interface is an implementation gap; it does not prove that the modeling method cannot express the requirement.

Sources: S++ concepts (maintainer reference: `../../../../spp/docs/cn/concept.md`), [numeric semantics](../../references/numeric-physical-semantics.md) and [participant execution](../../references/spp-participant-execution.md). Cross-document issues are tracked outside the manuscript in [known issues](../../编辑工作/known-issues.md).

---

[Appendix Contents](README.md) · [Full Book Contents](../README.md) · [Previous](../part-07-advanced-cases/35-design-review.md) · [Next](b-parallel-conditions.md)
