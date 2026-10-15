# Chapter 7 — Queries, Calculations, Validations and Ordinary Updates

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Quantum services change quantifiable properties such as balances and inventory. Complete business also retrieves facts, calculates amounts, checks eligibility, and saves information and processing status. Scenarios organize these responsibilities; applications choose execution accordingly.

Payment queries buyer and merchant, validates the order, prepares an amount, transfers funds, and saves the order and receipt. Each category has a defined responsibility.

## Most Queries Naturally Suit Concurrency

Ordinary queries and updates are built-in. Developers call them in scenarios but cannot alter their implementations. Separate calculations and validations express rules.

Queries obtain existing facts. Querying buyer data does not debit inventory; querying a price does not change the buyer. When inputs are ready and neither query needs the other's result, they can usually start together.

Petstore queries buyer and goods together for ordering, and buyer and merchant together for payment. The scenario uses completed participant facts afterward. Waiting overlaps, especially for database and external-domain access.

“Most” preserves dependencies. Goods cannot be queried from an order until that order identifies them. Queries also fill in-memory participants; concurrent writes to the same participant property need an explicit fill relationship. Inputs and fact-completion ranges determine concurrency.

A query also needs participant confirmation. Finding no buyer differs from failing to access the customer system. Unconfirmed information cannot be treated as complete calculation input.

## Calculations Can Reuse Calculations

Calculations use prepared facts and formulas: line amount is unit price times quantity, subtotal sums line amounts, and membership determines discount.

These formulas can be separate and reusable. Petstore `quoteOrder` calls `priceLine` for order lines and sums their results. Results are written to participants and reused as shared facts.

A calculation may call another calculation, but may not query a database, call validation, update facts or start a scenario. Missing prices must be queried by the scenario first; validity of quantity must be checked there. Readers can then understand calculations from existing facts alone.

The calculation call graph must be acyclic. A calling itself, or A calling B and B calling A, is prohibited recursion. The compiler rejects a cycle even when a base case exists. This does not prohibit for or while iteration. A subtotal can be accumulated in a loop, including calls to a line calculation, provided the service graph has no cycle. Graph checking does not prove loop termination; loops still need clear stopping conditions.

## Scenarios Organize Atomic Cooperation

An atomic service carries one defined responsibility. Ordinary atomic services cannot call other services or scenarios. Queries, validations, calculations and saves do their own work; scenarios organize business cooperation explicitly. Built-in queries complete participant facts; built-in updates save fully prepared facts.

Pure calculation-to-calculation reuse is the explicit exception. It remains calculation, not a hidden mixed query-validation-update process.

A payment scenario visibly arranges “query order, validate eligibility, prepare amount, transfer funds, save receipt.” The reader can see when funds change and which facts are saved. Call restrictions keep responsibilities and combinations visible.

Repository access within built-in queries and updates follows APP/PHY configuration. Business developers select participants and call positions; configuration supplies databases, mappings and protocols.

## Validation Controls Continuation

Validation checks conditions on existing facts without modifying participants: payment eligibility, shipping status or a required return reason.

Ordinary validation success continues execution; failure ends its execution scope. Failed payment eligibility prevents amount preparation and debit. A validation surrounding a local scope can execute that scope if allowed or skip it and continue later work.

The scenario may explicitly request reversal of the current transaction on validation failure. Reversing existing changes differs from merely ending a scope. The scenario chooses whether rejection causes rollback; Part III presents the syntax.

Calculation answers “how much,” validation “may we proceed.” Calculations cannot hide business rejection inside formulas. Validations do not call each other; scenarios arrange them.

## Calculations and Validations Suit Local Execution

With prepared facts, these services usually work entirely in memory. Line arithmetic and checking order status can execute in the scenario's process without remote calls for each formula or condition.

Both can be deployed locally. Ordinary business usually executes them directly in dependency order rather than creating a concurrent task for each small operation. Calculate lines, sum subtotal, then check payment conditions: clear flow avoids communication, scheduling and join overhead.

Different requests may still run concurrently. Sequential calculation within one request does not serialize the whole system. Large collections or expensive calculations can justify other execution strategies; Part II explains the criteria.

Inputs must be prepared first. Membership discounts need a membership tier: query obtains it and calculation uses it. This avoids hidden external accesses making local computation unexpectedly slow.

## Ordinary Updates Run Concurrently After Quantum Services

Ordinary updates are built-in, with no developer-defined update implementation. They perform no business queries, calculations or validations and call no business services. The scenario supplies all information through queries, calculations and quantum services. Queries retrieve existing facts, calculations prepare facts to save, and quantum services apply actual deltas and complete settlement results. Updates save that prepared information.

For payment, the scenario prepares order, amount and receipt; the quantum service transfers funds. During ordinary saving, neither order save nor receipt save needs information from the other. Each uses complete facts independently.

Within one transaction boundary, the SPP compiler therefore schedules quantum transactions before ordinary updates. Ordinary updates do not change quantum inputs, deltas or results. Quantum transactions need not await saves and are themselves commutative, permitting unordered or merged submission.

If facts still require preparation after the quantum phase, the scenario first completes calculations and validations. Ready ordinary updates can then run concurrently. Exchanging their order changes neither prepared facts nor the result after all are saved. This is the basis of ordinary-update commutativity under the service rules and the generated quantum-first plan.

```text
Scenario queries, validations and calculations
                    ↓
Unordered quantum execution or merged submission
                    ↓
Complete settlement results
                    ↓
Serial group: further calculations and validations as needed
                    ↓
       ┌─ Save order ──────────┐
       ├─ Save payment receipt ┤
       └─ Save other facts ────┘
                    ↓
Join and complete the transaction
```

Developers plan calculations and checks preceding saves. After quantum payment, receipt balance, content and completeness may still need preparation. A serial group expresses “obtain quantum result, calculate receipt, validate receipt, save receipt.” A save cannot start before its inputs exist.

Serial groups establish phases; ready ordinary updates within a phase can still run in parallel. Built-in updates always save current complete facts. Appendix B12 explains exchange of updates, and B13 quantum-first scheduling and preparation phases.

Concurrent updates inside one transaction differ from independent transactions competing over the same information. Two profile requests still need version checks or conflict handling to prevent stale overwrite. Intra-transaction exchange does not remove inter-transaction protection.

The arrangement is clear: queries retrieve facts; calculations prepare results; validations control flow; quantum services apply deltas; ordinary updates concurrently save complete facts. Scenarios express dependencies and execution supplies scheduling and transaction guarantees.

This division makes concurrent execution a natural advantage. Explicit dependencies, built-in queries and updates, and quantum commutativity expose independent queries, merged quantum requests and concurrent saving. Fine responsibilities need not become a remote call apiece. Traditional microservices use fine distributed services for scalability and isolation but introduce communication and serial waiting. Part II explains how atomic-service concurrency reduces the response-time cost of finer granularity.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](06-composition-and-conservation.md) · [Next Chapter](08-polymorphism-and-separation.md)
