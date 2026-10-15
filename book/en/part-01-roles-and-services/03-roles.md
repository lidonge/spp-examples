# Chapter 3 — Roles and Business Identity

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

A product in a catalog has a name, specifications and cost. When sold, it also has a selling price, listing status and sales text. Product and saleable goods are closely related but have different responsibilities. S++ uses Product for the product and Goods for its sales role.

Roles make participating identities part of the model. They can borrow facts from role players and own new facts arising from participation.

## Identity and Eligibility

The same Person can play Buyer and Merchant. A person's name is a natural fact, membership tier belongs to the buyer identity, and store name belongs to the merchant identity. Creating a person does not automatically authorize operating a store; role eligibility must be established and checked separately.

Changes become easier to locate. Membership discounts concern the buyer role and pricing services, while customer-name maintenance remains in the customer domain. Roles connect activities to entity facts and help distinguish fact ownership.

## Joint Role Playing

Some roles require multiple participants. A cart line involves both goods and buyer: the same goods have different quantities in different buyers' carts. Goods and buyer therefore jointly play CartLine, whose quantity is its own fact.

Joint role playing expresses relationship-based business. Ask which participants are indispensable to interpreting a role's facts. If cart quantity makes no sense without buyer and goods, its ownership should express that relationship.

## Roles Can Play Other Roles

Goods entering an order form an agreed order line. Current selling price can differ from the agreed unit price because historical terms must be retained. Goods can play OrderLine, which owns agreed quantity, unit price and amount.

Alex orders “Kitten Food” at 60 US dollars. The store later renames it “Kitten Formula Food” and raises the price to 65 US dollars. The product page can show the new facts; Alex's old order must still record “Kitten Food” and 60 US dollars.

When goods play an order line, distinguish information read as current goods values from information recorded separately at settlement. The relationship expresses their connection, not an obligation to update historical order names and prices whenever goods change.

## Roles and Object Types

An object type describes what an entity is; a role describes the capacity in which it participates. Alex remains one person while playing buyer when shopping and seller when running a store. Buyer and seller have different requirements: confirming and paying for purchases versus providing agreed goods.

Conversely, different entity types can play the same role. A person purchases household supplies and a company procures equipment. Both can be buyers. Purchasing services depend on the role's facts, qualifications and obligations. The player is replaceable if those requirements remain satisfied.

There is no one-to-one relationship between entity types and roles. One entity can play many roles; one role can admit different entities. Role-oriented modeling identifies required participating identities from behavior before assigning entities to them.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](02-service-model.md) · [Next Chapter](04-decomposition.md)
