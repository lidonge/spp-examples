# Chapter 1 — From Objects to Business Activities

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Both object-oriented and role-oriented modeling express entities and their behavior. Their emphasis differs in what they choose as the subject of modeling. Object orientation centers on entities and organizes properties and actions around them. Role orientation centers on business behavior and organizes participants around a complete business objective. The former asks what an object can do; the latter asks who participates in what capacity and how the activity is completed.

This book applies the modeling method to commercial service architecture. Part VII, Chapter 35 further examines its expressive scope and how it constructs complex data structures and algorithms.

## Organizing Actions Around Objects

When a store accepts orders, concepts such as customers, products, inventory and orders appear. Object-oriented modeling usually establishes these objects first and attaches actions to them: customers maintain profiles, products adjust prices, inventory reserves quantities, and orders change state. Cooperation among objects completes the business process.

Actions belong to their objects. The model emphasizes their properties, capabilities and mutual calls. Interfaces, inheritance and composition help reuse capabilities, while objects and their capabilities remain the starting point for organizing business.

## Organizing Participants Around Business Behavior

Role-oriented modeling first describes the complete behavior of purchasing: a buyer selects goods, reaches an agreement with a seller, and obtains goods or a delivery commitment. It then identifies roles such as buyer, seller and goods, and lets concrete entities play them.

A person purchasing household supplies and a company procuring office equipment are different entities. Both can play the buyer role if they satisfy the qualifications, facts and obligations required by purchasing. The behavior depends on the buyer role; the entity playing it can change.

One entity can also participate in different behaviors. Alex is a buyer when purchasing and a seller when operating a store. The participating identity changes with the activity; Alex has not become another person.

Role orientation therefore makes the business activity itself an explicit modeling subject. Its objective, relationships and completion conditions form the model's main thread. Objects join that thread as participants. They still provide facts and carry actual changes, but the complete meaning of the behavior does not belong to one particular entity.

## Starting with a Purchase

Alex buys two items. The store confirms purchasing eligibility, checks goods and quantities, calculates the agreed price, reserves inventory and forms an order. Customer and product data provide the facts; eligibility, price, reserved quantity and order terms belong to this activity.

Reading along the purchasing behavior, Alex participates as buyer, a product participates as saleable goods, inventory supports fulfillment, and the order records the agreement. Every query, calculation and update must be explained within that purchase: whose facts does it prepare, which agreement does it serve, and how does it help complete the whole activity?

Suppose two items have been reserved but the order could not be saved. Completing one operation does not mean the purchase has been established. Behavioral completeness requires us to explain whether the agreement was formed and what happens to existing changes. These requirements begin with the objective of completing a purchase and are then assigned to participant operations.

## Actions and Behavior

An action is an operation an object can perform; behavior is an activity with internal logic and purpose. Changing a field is an action; confirming a payment is behavior. The former describes a local change. The latter also explains why it occurs, who participates, and what counts as completion.

This distinction prevents technical steps from becoming business services merely because they are operations. Serialization, sending a request and updating a row are runtime operations, but do not necessarily constitute complete business behavior. A payment cannot be considered complete merely because its request was sent; it requires an interpretable settlement result.

## Different Participating Identities of One Object

A person may be buyer, merchant, payer or account owner in different activities. Their qualifications and facts differ. Buyers concern membership and purchasing relationships; merchants concern business operations; payers concern the funds used. Making one Person class carry all these rules concentrates unrelated business changes in one model.

S++ expresses participating identities through roles. Entities provide natural facts; roles explain how those facts enter particular services. Their relationship is developed in Part I, [Chapter 3](03-roles.md). For now, read the model by asking who participates in which behavior and in what capacity.

## Constraining Models Through Results

Business modeling must answer what completion means. A successful order means that its agreed content and inventory reservation satisfy the terms. A successful payment means that fund changes and payment status satisfy the terms. These results let us judge decomposition, identify steps that must succeed together, and recognize technical failures requiring recovery.

Role-oriented service architecture retains the facts of the object world while expressing business activities, participating identities and cooperation explicitly. The next chapter connects them through a simple model: service equals participants multiplied by behavior.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Next Chapter](02-service-model.md)
