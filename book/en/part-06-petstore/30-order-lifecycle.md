# Chapter 30 — Quotation, Ordering, Payment and Shipping

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Continue with wallet 500 and available stock ten. A VIP buys two at 60. Distinct quotation, ordering, payment and shipping activities organize different service categories.

## Quotation Forms Candidate Terms

Subtotal 120, discount 12, discounted amount 108 qualifies for free shipping, so total is 108. See [calculations](../../../demos/petstore/src/main/spp/petshop/order/petshop-20-calculations.spp).

Queried prices, quantities and tier produce a candidate, not persistent settlement. Lines retain names, quantities, unit prices and amounts; the order retains discount, shipping and total. Numerical price is descriptive quotation input, not automatically a quantum property.

Later price changes leave old agreed lines unchanged. Business requires historical terms; APP snapshots implement saving and querying them.

## Ordering Connects Terms and Reservation

The [order scenario](../../../demos/petstore/src/main/spp/petshop/order/petshop-scene-placeShopOrder.spp) has four dependency phases:

1. Prepare selection and query buyer/catalog concurrently.
2. Locate and query cart, validate it and calculate quotation.
3. Prepare inventory identities, query and validate reservation, prepare order/cart changes.
4. Save lines, order, cart and receipt with inventory reservation in the transaction.

Initial queries are independent. Stock query needs goods relationships prepared from the order, so cannot arbitrarily join the first parallel group.

Two units move from available to reserved: 8/2/0. Supply stays −10 and this goods total zero. Preliminary availability does not prevent competing orders, so actual bounds remain mandatory.

The compiler schedules quantum and ordinary work by preparation dependencies. `preparePurchaseReceipt` is inside the current transaction; not every statement can execute as a simultaneous save. Calculation precedes dependent receipt insertion. Built-in saves do no hidden completion.

## Payment Makes Amount and Parties Explicit

Payment reads the formed order instead of cart or recalculating discounts. It verifies ownership and eligibility, prepares 108 and receipt, then transfers and saves.

From [payment](../../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-payShopOrder.spp):

```spp
transaction {
    transaction REQUIRED {
        payOrderFunds bounds {
            Buyer.wallet: [0, null]; Merchant.cash: [0, null];
        };
    }
    updateShopOrder;
    insertReceipt(PaymentAgreement.receipt);
}
```

Wallet becomes 392 and merchant gains 108. Quantum services conserve funds; ordinary services save order and receipt. Their ready inputs permit parallel saving under supporting configuration.

Inner REQUIRED joins the outer logical boundary, not an independent settlement. APP/PHY determine joint physical commit or phases and recovery. SPP alone does not prove two databases share a transaction.

## Shipping Uses Another Inventory Pair

[Shipping](../../../demos/petstore/src/main/spp/petshop/fulfillment/petshop-scene-shipShopOrder.spp) queries buyer/order, prepares and queries inventory, checks status and reserved quantity, then prepares agreement and receipt.

Two move reserved to sold: available 8, reserved 0, sold 2. Ordinary saves retain state, tracking and receipt. Payment conserves money; shipping conserves quantities, with different completion conditions.

## Check Each Stage

|Stage|Wallet|Merchant Delta|Available / Reserved / Sold|Ordinary Facts|
|---|---:|---:|---|---|
|Ordered|500|0|8 / 2 / 0|Lines, total 108, unpaid|
|Paid|392|+108|8 / 2 / 0|Paid state, receipt|
|Shipped|392|+108|8 / 0 / 2|Shipping state, tracking, receipt|

These expected illustrative results do not replace runtime evidence. Unknown payment cannot be shown as definitely failed or successful; APP confirms settlement and saves. Next distinguish recovery from subsequent business.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](29-opening-and-transfers.md) · [Next Chapter](31-returns-and-reservations.md)
