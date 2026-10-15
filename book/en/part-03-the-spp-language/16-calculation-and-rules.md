# Chapter 16 — Calculation Rules and Collection Participants

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Calculations express amounts, quantities, eligibility and policies. S++ retains familiar conditions and loops while separating mathematical meaning from physical representation. Formulas show business relationships; PHY supplies representation.

## Make Rounding a Business Rule

Line amount uses unit price times quantity, rounded to two decimals as agreed. `roundHalfUp` states the rule. Without a business rounding requirement, storage capacity or default precision must not silently change values.

BigDecimal is one physical option. Some operations still require explicit rounding or another representation; exact decimal does not finitely represent all mathematical results.

## Rules Execute in Defined Order

Petstore calculates lines and subtotal, then membership discount, shipping and total. These depend on facts at the current execution point.

if, switch, while and for provide deterministic flow, not a repeatedly firing rule agenda or arbitrary Java calls. Formulas remain within supported expressions and call contracts.

## Collections and Internal Lines

Participants can be one-dimensional collections such as Goods[]. Queries complete them, calculations traverse goods and cart lines and form new internal order lines. Scalar input instances cannot be replaced; collection inputs retain their container while contents change.

Syntax accepts `Goods[][]`, but current query, update and calculation implementations do not support multidimensional participant collections. Examples use one dimension; implementation will expand if practical demand emerges.

A schematic subtotal service, omitting domain and other definitions:

```spp
atomic calculate sumOrderLines(ShopOrder) {
    ShopOrder.subtotal = 0;
    for (OrderLine line : ShopOrder.lines) {
        ShopOrder.subtotal += line.amount;
    }
}
```

The loop is sequential. Parallel line processing requires explicit branch results, aggregation and execution support.

## Candidate and Settled Facts

A calculation may mark an in-memory candidate paid, but only protected updates make it an actual result. Technical failure cannot publish a candidate as settled.

Separation allows independent formula verification and shorter transactions. Version or settlement guarantees must still prevent competition after preparation from causing stale overwrite.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](15-atomic-services.md) · [Next Chapter](17-scenarios.md)
