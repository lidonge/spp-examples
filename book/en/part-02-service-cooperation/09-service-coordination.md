# Chapter 9 — Service Cooperation and Execution Order

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Ordering needs buyer data and prices before calculating the agreed amount. It is tempting to write three successive steps: query buyer, query goods, calculate price. Only the calculation actually requires completed queries. The two queries can start together.

Explaining why each step waits is more useful than immediately selecting threads or network protocols.

## Three Sources of Waiting

The first is business agreement. A store may require verification of returned goods before refunding. That result establishes refund eligibility; changing the sequence changes the policy.

The second is data dependency. Payment has no definite amount before the total exists; discount must await subtotal if it uses that subtotal.

The third is code arrangement. Buyer queries use membership credentials, goods queries use goods credentials, and neither needs the other. Sequential calls merely choose one execution strategy.

The third category, and other ready activities without mutual interference, can run in parallel. The first two require preserving dependencies or changing the business and calculation design.

## Evaluating an Example

Suppose buyer query completes membership tier and goods query completes selling price. Quotation needs both. Concurrent queries do not omit either fact.

For calculations, A calculates line amounts and B totals them. B cannot start by reading unfinished lines. Different lines may be calculated separately before aggregation, but multiple threads must not arbitrarily overwrite one subtotal.

Queries also write memory. If both fill the same Buyer's name, the last write determines the result. Examine actual field-completion ranges.

## Identifying Join Points

Arrows show waits in a simplified order:

```text
                  ┌─ Query buyer ─┐
Prepare inputs ───┤               ├─ Eligibility ─ Quote ─ Prepare inventory ─ Settle
                  └─ Query goods ─┘
```

Joining means both queries have completed with usable results. Missing identity or technical failure prevents normal quotation. Parallel plans must also identify branches that can stop and effects already produced on failure.

## Updates Need Further Checks

Two requests each read a wallet of 100 and want to debit 80. Preparation can overlap, but settlement must enforce the lower bound so at most one succeeds. Earlier reads and scheduling cannot replace settlement protection.

Wallet debit and merchant credit must also form one payment result. Starting both concurrently still needs a mechanism guaranteeing their joint outcome.

Ordinary updates have a different arrangement. Under Part I, Chapter 7, the scenario supplies all information through queries, calculations and quantum services. After quantum execution within one boundary, ordinary updates can concurrently save complete facts and join to finish the transaction. Order and receipt saves need not wait to obtain business information from each other.

The method is: identify inputs and outputs, explain waits, then check shared writes and settlement. Appendix B gives complete conditions, proofs and counterexamples.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](../part-01-roles-and-services/08-polymorphism-and-separation.md) · [Next Chapter](10-parallelism-and-costs.md)
