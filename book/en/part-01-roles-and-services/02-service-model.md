# Chapter 2 — Service Equals Participants Multiplied by Behavior

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

“Transfer” names a behavior. To understand the business activity it forms, we need to know who supplies funds, who receives them, the amount and the constraints. Conversely, placing two accounts together does not transfer money. Participants and behavior jointly form a meaningful business activity.

In “service = participants × behavior,” service has its broad, traditional meaning, as in order-placement or payment service: participants jointly complete business and produce an intended result. Multiplication emphasizes that both are necessary. Behavior needs participants to carry it; participants must enter behavior to produce a business result.

SPP further distinguishes **services** from **scenarios**. A service carries a defined business responsibility. A scenario organizes participants and services around a complete business objective. This chapter explains the common model and its mapping to those concepts.

## A Simple Expression

Write a business activity as:

```text
B = p × b
Business activity = participants × behavior
```

Here p denotes a participant or participant combination, b a behavior with business purpose, and B the activity with its objective and result. A complete service in the traditional sense can combine multiple activities. Appendix A gives the full notation and conditions.

Multiplication is a modeling expression, not numerical multiplication of account values and methods. Nor does it imply that all business steps obey ordinary algebra. It helps identify missing participants, behavior or results in a definition.

## Participants Determine the Concrete Meaning

Buyer-to-merchant payment, merchant-to-buyer refund and settlement-account-to-wallet funding all involve different relationships. Naming all of them pay obscures the differences. The model must identify who plays each role, which facts change, and which contract expresses the agreement.

Participants are also more than a collection of primitive interface parameters. An account number locates an account but does not fully express payer eligibility, account facts or confirmed identity. An amount must belong to an explicit payment agreement so the caller knows whether it is a quotation, payment or refund. A participant is therefore more than a conventional class: it needs the relevant role information.

## From Complete Business to Services and Scenarios

A conventional order-payment service queries buyer, merchant and order, confirms eligibility, prepares the amount, transfers funds and records order state and a receipt. Together these activities fulfill the objective of paying an order.

|Concept|Meaning in Order Payment|
|---|---|
|Service|A defined responsibility: query a participant, check eligibility, prepare an amount, transfer funds or save an order|
|Scenario|Organize buyer, merchant, order and payment contract; combine services; express sequence, transaction boundaries and completion requirements|

The fund-transfer service describes a decrease in the buyer's wallet and an increase in merchant funds. The scenario also identifies the order, the source of its amount, eligibility and how fund changes and order records form the payment result. Fund transfer alone cannot replace the entire activity.

Analysis therefore starts with “the buyer and merchant complete order payment under a payment agreement.” We then identify service responsibilities and organize them in a scenario. The model begins with the objective; SPP expresses local responsibilities and overall cooperation separately.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](01-business-activities.md) · [Next Chapter](03-roles.md)
