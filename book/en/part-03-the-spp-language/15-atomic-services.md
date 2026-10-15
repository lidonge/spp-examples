# Chapter 15 — Four Categories of Atomic Service

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Ordinary business atomic services are query, check, calculate and update. They retrieve facts, judge conditions, form candidate results and apply changes. Scenarios combine them into complete activities.

## Queries Complete Facts

Ordinary query is built-in. Scenarios call `findBuyer` and similar services directly; APP/PHY retrieve facts and complete input participants without redeclaring standard queries. There is no business return value such as `buyer = findBuyer()`. Identity confirmation is execution state, not inferred from nonempty fields. Completion need not load the whole role chain; property analysis and caching can optimize it as described in Part II, Chapter 11.

An omitted instance name defaults to its type. Multiple participants of one type need aliases. Omitted arguments require unique matching by complete type and collection dimension; ambiguity requires explicit selection.

## Validation Checks Eligibility

check reads facts and uses require for requirements without changing participants. Ordinary failure ends its lexical scope, not automatically a transaction rollback. Supported explicit control requests reversal.

Visible checks clarify admission. Actual quantum bounds must be enforced at settlement, not substituted by earlier balance reads.

## Calculations Prepare Results

calculate changes candidate facts through formulas. It may call pure calculations, not query, check, update or scenarios to hide side effects.

```spp
atomic calculate priceLine(OrderLine) {
    OrderLine.amount = roundHalfUp(
        OrderLine.unitPrice * OrderLine.quantity, 2);
}
```

This definition is from [pricing source](../../../demos/petstore/src/main/spp/petshop/order/petshop-20-calculations.spp), with line wrapping for presentation.

## Updates Apply Changes

Ordinary update is also built-in. After preparing complete facts, scenarios call standard insert, update or delete services suffixed by participant type. Current participants are passed; the framework retains technical baselines without a business before snapshot. Business calculations and checks stay outside the built-in update. Quantum updates describe special-property deltas and settlement requirements.

The categories clarify dependencies. Preparation and checks can often precede the settlement boundary, leaving protected updates inside. Business and concurrency constraints still matter; calling each category once is not automatically complete business.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](14-take.md) · [Next Chapter](16-calculation-and-rules.md)
