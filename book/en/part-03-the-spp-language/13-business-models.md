# Chapter 13 — Entity, Reference, Role and Contract

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Types answer different questions. Entity is a natural entity owned by the current domain; Reference points to an external-domain concept; Role is participating identity; Contract records an agreement formed by a scenario. Together they explain meaning and lifecycle ownership.

## Natural Entities and External References

The customer domain owns Person and the product domain Product. The shop uses their facts, but the original domains own their lifecycles. Reference makes origin explicit; APP and PHY determine integration.

References can target provider entities, roles or contracts. They identify fact sources without taking lifecycle maintenance away from providers.

## Roles and Scenario Contracts

Buyer expresses shopping identity and Goods sales identity. ShopOrder records ordering terms; PaymentAgreement payment terms. Later payment, shipping and return scenarios can reference an order without repeating ordering.

A short Petstore contract is:

```spp
Contract WalletFundingAgreement {
    Buyer buyer;
    SettlementAccount source;
    BigDecimal(19, 2) amount;
}
```

Participants and amount describe one funding activity. The contract records terms; services implement changes.

## Constituent Facts and Independent Participants

Order lines retain goods, quantity and agreed unit price. Total is a constituent fact of the agreement, not necessarily a separate amount role. Independent roles require real participation and lifecycle meaning.

Aggregating lines in a contract does not mean the contract plays each line. Composition and role playing are separate relationships.

## Internal Keys and Business IDs

Conventional developers often add a unique `id` to identify objects and database records. S++ does not require a business field merely for technical location: the compiler provides a business-invisible internal entity key. Technical uniqueness does not require a business ID.

Habitual fields such as `id` or `customerId` can imply nonexistent business credentials. The compiler checks suspicious habitual IDs and warns developers to confirm real meaning.

Where an ID truly serves business, `business` explains its purpose and removes the warning. A receipt identifier used by customers to query results is one example:

```spp
Entity Receipt {
    business("Business receipt number used by customers to look up and verify the outcome") String receiptId;
}
```

The customer uses this value. If its only purpose is database uniqueness, the internal key already serves that responsibility. `business` explains why a seemingly technical ID belongs in the business model.

Its purpose is resolving ambiguity. Review still asks who uses the number, in which activity and how it supports processing or verification. “Internally unique” describes technology, not a business credential.

Models are organized by membership, goods, cart, orders and other functions. See the [Petstore source guide](../../../demos/petstore/docs/source-guide.md).

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](12-layers.md) · [Next Chapter](14-take.md)
