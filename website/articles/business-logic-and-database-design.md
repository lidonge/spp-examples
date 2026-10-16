# Why Business Logic Should Not Depend on Database Design

A buyer pays for an order. The operation has a business meaning before anyone chooses a database table, a foreign key or a remote endpoint. **S++ (ServPP)** is an experimental business modeling language that makes those participants and operations explicit, while separate application and physical definitions select their implementation.

The distinction becomes practical when a system changes. A product catalogue may move to a separate service. A customer deployment may need larger monetary values. An order must still retain the price accepted at checkout. Which of these changes should alter the business description?

## Start with participants, not storage keys

In the Petstore demonstration, an order refers directly to its buyer:

```spp
Contract ShopOrder {
    business("Order reference presented to the buyer") String orderNumber;
    Buyer buyer;
    OrderStatus status;
    OrderLine[] lines;
    // Additional order facts omitted.
}
```

This is an excerpt of the [order model](/sources/petstore-demo/petshop/order/petshop-00-model.spp/). The order number is a business reference that a buyer can quote. A database-generated identifier, by contrast, can remain an application storage concern. The business model does not replace the buyer participant with a technical `customerId` field.

The APP layer defines the corresponding tables and relationships. It can store a participant association as a foreign key and can introduce a storage-only primary key. The generated implementation carries that identity for persistence without requiring SPP business services to manipulate it.

This does not eliminate database design. It gives database design a defined place, where it can be reviewed independently of the order's business meaning.

## A role's current value and an order's historical fact differ

Suppose a pet's catalogue name changes after an order is placed, or its price rises from $100 to $120. A current catalogue view should show the new facts. The earlier order must still show the name and $100 price agreed at checkout.

In the demonstration, goods play an order-line role. APP explicitly selects which mapped facts become independent snapshots:

```app
table SHOP_ORDER_LINES(OrderLine) {
    primarykey(OrderLine.lineNumber);
    auto OrderLine.lineNumber prefix "ORDER-LINE";
    foreignkey(OrderLine.goods) references Goods;
    snapshot(OrderLine.name, OrderLine.unitPrice);
}
```

The [application definition](/sources/petstore-demo/petshop/petshop.app/) makes the storage choice visible. The business role still has a name and a unit price; it does not need a second set of technical fields to express how they are persisted. Snapshotting preserves the accepted facts instead of accidentally replacing them during a later lookup.

## Numeric meaning also crosses the boundary

Business calculations should express what is being calculated. Their mathematical meaning should not depend on a programmer remembering whether Java operands require primitive operators or decimal methods.

S++ treats numeric declarations as default representations. PHY can select the concrete representation used by generated code, including a precise decimal shape for a particular attribute. The [Petstore physical definition](/sources/petstore-demo/petshop/petshop.phy/) includes both a global replacement rule and an attribute-specific override.

That separation does not make rounding disappear. If a business rule says to round a charge to cents, the rule belongs in the calculation. Storage capacity and numeric operation generation belong to the realization. An unsuitable physical choice is still a configuration problem to detect and resolve, not a reason to hide a new business rounding rule inside infrastructure code.

## What this approach costs

Separating business and storage creates work for the compiler and runtime. They must understand role mappings, preserve participant identity, load the facts a service uses and apply the selected persistence policy. Configuration must be checked against the actual deployment. These obligations do not vanish merely because the business source is shorter.

The benefit is a more focused review: a business reviewer can inspect the participants and accepted facts, while an implementation reviewer checks tables, resources and service routes. S++ is still in development; the demonstrations show exercised behavior rather than a guarantee for every production database or failure mode.

Continue with the [role-oriented order lifecycle](/articles/role-oriented-order-lifecycle/), [language guide](/guide/) or [book chapter on facts and storage](/book/part-04-consistency-and-execution/18-facts-and-storage/).
