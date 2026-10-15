# Chapter 28 — Identifying Roles, Behavior and Services from Requirements

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

The earlier parts now meet in one shop: a VIP buyer funds 500 US dollars, buys two goods at 60 each, pays and receives shipment, then examines cancellation, returns and failed reservations. These are illustrative inputs, not fixed demo seeds.

First establish objectives, then SPP expression, then APP/PHY integration and deployment. Meaning, source responsibilities and results can be checked together.

## Describe Complete Activities First

“Buyer purchases goods” is too broad. Expand it:

|Activity|Participants|Completion Result|
|---|---|---|
|Funding|Buyer, settlement source, funding contract|Wallet increases; source decreases equally|
|Ordering|Buyer, cart, goods, stock, order|Terms saved, stock reserved, cart maintained|
|Payment|Buyer, merchant, order, payment contract|Funds transferred, order paid, receipt formed|
|Shipping|Buyer, order, inventory, shipment contract|Reserved becomes sold; shipping recorded|
|Return request|Buyer, order, request contract|Reason and processing state recorded|
|Return approval|Buyer, merchant, order, inventory, refund contract|Funds returned, stock replenished, result saved|

Payment deserves its own scenario because wallet debit is only one part. Payee, eligibility, amount, status and receipt determine completeness. Starting from Buyer methods can scatter cooperation; starting from payment exposes participant duties. This is the emphasis of Part I, Chapters 1–2.

## Separate Entities, Roles and Contracts

Person belongs to customer and Product to product. Buyer, Merchant and Goods express shop identities; inventory owns StockLine and supply. The shop does not acquire ownership of all customer/product facts.

Person plays Buyer; Product plays Goods; buyer and goods jointly play CartLine, owning relationship quantity. Goods forms OrderLine with agreed name, quantity, price and amount. ShopOrder is an ordering contract; Receipt an evidence entity.

Current name differs from agreed name. “Pet Food A” later becoming “Pet Food A — New Packaging” must not change the old order. APP uses `current(Goods.name)` and `snapshot(OrderLine.name, OrderLine.unitPrice)`, developed in Part VI, Chapter 32.

Membership and order numbers serve customers, not merely tables. `business` states that use; keys, versions and duplicate identifiers belong to technology. Part III, Chapters 13–14, now have concrete applications.

## Classify Scenario Responsibilities

|Responsibility|Petstore Example|Work|
|---|---|---|
|Query|findBuyer, findMerchant, findShopOrder|Complete existing facts|
|Validation|checkOrderOwner, checkPaymentEligibility|Check ownership and qualification|
|Calculation|preparePayment, preparePaymentAgreementReceipt|Prepare amount, state and receipt|
|Quantum update|payOrderFunds|Transfer wallet funds to merchant|
|Ordinary update|updateShopOrder, insertReceipt|Save prepared facts|

Systems supply queries and ordinary saves; developers write calculations, validations and scenarios. Updates do not retrieve amounts or calculate discounts internally. Visible preparation concentrates rules in readable flows while persistence can be implemented separately.

## What Polymorphism Reuses

Quotation reads Buyer tier, Goods price and CartLine quantity, without knowing the original database, supplier or external system. Another legal Goods player supplying those facts can reuse calculation and validation.

Meaning still matters: having a `price` field does not authorize arbitrary substitution for sales goods. Existing Petstore demonstrates concrete chains; new players need models, mappings and verification, not merely matching fields.

## Follow Both Business and Technical Source

Read [requirements](../../../demos/petstore/docs/requirements-and-functions.md), then the [payment scenario](../../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-payShopOrder.spp) and its named calculations/checks. Ask what each uses, produces and waits for.

Then read [APP](../../../demos/petstore/src/main/spp/petshop/petshop.app) and [PHY](../../../demos/petstore/src/main/spp/petshop/petshop.phy) for storage, guards, transactions and resources. Functional directories organize source without changing domain identity or requiring a particular deployment machine.

Next establish participants and resource sources, then follow one set of amounts and quantities.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](../part-05-business-and-technology/27-operations-and-evolution.md) · [Next Chapter](29-opening-and-transfers.md)
