# Chapter 6 — Superposition, Commutativity and Entanglement

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

A major difference between quantum services and traditional updates is their treatment of values during transactions. A traditional update often obtains and locks the current value before calculating a definite new one. A quantum service expresses its delta; even after that delta settles, the observed property value cannot be determined solely from the earlier query and this delta.

S++ borrows superposition, commutativity and entanglement from quantum terminology to describe value states, execution order and related changes. We begin with balance updates and then discuss order and conservation.

## Superposition Allows Value Uncertainty After Settlement

An account has 1,000 US dollars and this operation subtracts 100. One traditional approach locks the account with `select for update`, reads 1,000 and writes 900. Other requests cannot change that record during the protected update, so the transaction can determine the value it produces.

The quantum service expresses “subtract 100.” Seeing 1,000 in a query does not lock that value until the transaction ends or require the eventual balance to be 900. Other requests may change it meanwhile.

Suppose another concurrent payment of 200 also takes effect:

```text
Balance at query: 1,000 US dollars
This delta: −100 US dollars
Another concurrent delta: −200 US dollars
Balance after both settle: 1,000 − 100 − 200 = 700 US dollars
```

This operation's 100 has settled, but the later observed balance need not be 900. Other settlements and execution order affect it. Quantum services guarantee the delta, while allowing the resulting property value to reflect concurrent changes. Observation obtains the concrete facts.

That is the borrowed meaning of “superposition before observation.” After this service settles, the property is not restricted to the value predicted from this operation alone. With no other change it can be 900; with the other debit it can be 700. This debit may have succeeded in both cases.

Superposition thus concerns value uncertainty after settlement and before observation. Confirmation answers whether the delta succeeded; observation answers the property's value at that point. One cannot replace the other. Execution must still enforce bounds, conservation and settlement. Appendix D12 elaborates.

## Commutativity Means Order Does Not Affect the Joint Result

With 1,000 US dollars, service A subtracts 100 and B subtracts 200. If both settle, either order gives 700:

```text
A then B: 1,000 − 100 − 200 = 700
B then A: 1,000 − 200 − 100 = 700
```

Each service expresses a fixed delta rather than making its intermediate balance a fixed input for the next service. Execution order can therefore be exchanged even when both affect the same quantum property.

Commutativity relates to superposition. Intermediate observations and which change occurs first may differ, but they do not determine already prepared deltas. After all settle, the joint result remains equal. This supports unordered and parallel execution. Appendix B0 proves the two- and multiple-delta cases.

## Entanglement Becomes a Conservation Relationship

Wallet payment of 100 and merchant receipt of 100 sum to zero. Decreasing available inventory by two and increasing reserved by two also describes conserved transfer. The changes constrain each other; without the counterpart, the destination of money or goods is unexplained.

Money and inventory remain different dimensions even when both are quantum properties. They cannot be added to prove conservation. Products must also be checked under their own identities. A scenario can coordinate them, but conservation groups must reflect actual relationships.

## Multiple Quantum Services Can Be Submitted Together

Commutativity enables several services to become one larger quantum request. Each has defined participants and fixed deltas; execution can collect them and submit them together.

A transfers 100 to B and 200 to C. Separate submission sends two requests and receives two results; merged submission carries both:

```text
Service A: party A −100, party B +100
Service B: party A −200, party C +200
Merged request: {A, B}
Joint delta: party A −300, party B +100, party C +200
```

Since order is exchangeable, the sender need not await the first before sending the second just to preserve sequence. The executor can arrange them under a common boundary. The business model retains distinct responsibilities while communication is combined.

This reduces network round trips, packaging and protocol processing. Fixed communication overhead is especially worth combining when services are numerous and individual changes small. Commutativity provides the basis; Appendix D6 explains merged submission and delta aggregation.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](05-quantum-services.md) · [Next Chapter](07-business-service-characteristics.md)
