# Chapter 4 — Service Categories and Scenario Organization

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Order payment combines business activities and technical support. Eligibility checks, amount calculations and fund transfer are business; request parsing, data conversion, communication protection and storage access make them executable. Separating these categories and then refining business responsibilities clarifies every service in a scenario.

## Technical and Business Services

Business services directly express business objectives and rules: whether an order may be paid, how much is due, and how money moves from buyer to merchant.

Technical services supply execution means: HTTP reception, JSON parsing, message encryption and database connections. Changing the protocol should preserve the business meaning of payer, payee and amount; the technical implementation changes.

Classification depends on responsibility, not name. Checking a request signature is technical security; checking purchase eligibility is a business rule. Business services declare needed facts and results; technical services obtain facts, transmit information and protect execution under the agreed contract.

## Four Categories of Business Service

|Category|Question|Payment Example|
|---|---|---|
|Query|What facts do participants have?|Obtain order, buyer and merchant information|
|Validation|Are business conditions satisfied?|Check order ownership and payment eligibility|
|Calculation|What result follows from the rules?|Prepare the payment amount from the order|
|Update|Which business facts actually change?|Transfer funds and record payment state and receipt|

Ordinary queries and updates are built-in system services whose implementations developers cannot alter. Business calculations and validations are called separately in scenarios. Queries complete facts, validations judge conditions, calculations prepare results, and updates apply changes. Calculating 100 US dollars due does not mean payment occurred; actual changes must complete.

The categories generalize. Registration queries existing records, validates eligibility, prepares content and establishes identity. Quotation queries goods and membership facts, checks conditions and calculates price, without necessarily making a settlement update.

## Updating Descriptive Properties

Descriptive properties state what participants are and their information or status: a customer's address, a merchant's store name, or goods changing from listed to unlisted.

Numbers can also be descriptive. Changing a price from 60 to 65 US dollars changes quotation input; it does not move five US dollars out of an account. Classification depends on business meaning, not whether the field contains a string or number.

These updates still require protection against competing overwrites and may participate in complete activities. Their distinctive role is maintaining information or status. The consistency chapters discuss protection.

## Updating Quantifiable Transaction Properties

Other properties represent transaction quantities, such as wallet balances and inventory. Their changes must identify amount, source, destination and permitted range.

Payment of 100 US dollars decreases the wallet and increases merchant funds by 100. Reserving two items decreases available and increases reserved quantity by two. Business concerns the transfer and both results, not merely assigning a new field value.

Suppose a wallet contains 500 US dollars and receives 20 after being queried. A 100-dollar payment should subtract from the actual 520, leaving 420. Writing the previously calculated 400 would erase the funding. Transaction updates must express actual deltas and use settlement mechanisms to handle competition, bounds and related changes.

A conserved change between a pair of quantum properties is the smallest quantum service. Later chapters explain source, destination and joint settlement.

## Scenarios Organize the Services

Each category has its responsibility; scenarios combine them into complete business. Payment specifies facts to retrieve, qualifications to check, amount preparation, fund changes, order state and receipts.

One activity can use both update kinds. Payment moves funds and changes order state. The scenario explains how they jointly form its result; the technical layer supplies storage and execution guarantees.

This preserves both clear responsibilities and the whole objective. The next chapter introduces quantum behavior and services through changes in transaction properties.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](03-roles.md) · [Next Chapter](05-quantum-services.md)
