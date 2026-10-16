# Modeling an Order Lifecycle with Roles and Services

An online order touches a person, a product, inventory, a merchant and an agreement. Treating all of them as database records misses an important distinction: an entity can participate in different activities through different roles. **S++ (ServPP)** uses role-oriented programming to describe those responsibilities explicitly.

The [Petstore demonstration](/examples/#petstore) provides a concrete example. Its customer and product domains define entities. Its shop and inventory operations use roles such as buyer, goods and order line. A role is not merely a different variable name for the same object; it can add facts specific to the activity.

## A product becomes goods, then an order line

The shop's goods role is played by a product. It carries sale-related facts such as price and availability for sale. When goods participate in an order, the order-line role adds quantity, line amount and the accepted unit price.

The [order model](/sources/petstore-demo/petshop/order/petshop-00-model.spp/) defines the mapping:

```spp
take Goods as OrderLine {
    Goods goods = Goods;
    String name = name;
    BigDecimal unitPrice = price;
}
```

These roles describe different business responsibilities rather than subclasses of a single persistence record. A role can also be played jointly by several participants; this example deliberately uses a simpler chain. APP decides whether mapped values remain current or are retained as order-time snapshots.

## A scenario says who participates

The payment scenario declares its participants by role:

```spp
Scenario serial payShopOrder(Buyer, Merchant, ShopOrder, PaymentAgreement)
```

This is the declaration from the [payment scenario](/sources/petstore-demo/petshop/payment/petshop-scene-payShopOrder.spp/). The buyer pays, the merchant receives funds, the order changes state and the agreement carries this payment's business facts.

There is no need to bundle the entire application state into a generic context object. Nor does a buyer number replace the buyer participant at the service boundary. An incoming participant may initially contain only enough information to identify it; a query service fills its facts into that same participant instance.

When a role is unambiguous, S++ permits its type name to identify the participant. Calls such as `checkBuyerCredential;` use the available roles without repeating a conventional argument list. Explicit names and arguments remain available when several participants or collection mappings would make that shorthand ambiguous.

## Checks, calculations and changes are visible separately

The payment flow looks up participants, checks ownership and eligibility, prepares payment facts, then enters its transaction boundary. The calculation service is not a hidden route to another scenario, and a calculation does not conceal a business check.

This helps a reviewer ask specific questions. Is the buyer allowed to pay? Does the order belong to that buyer? How is the amount calculated? Which balances and records change together? The source places these decisions in identifiable services and blocks.

Checks also need explicit failure semantics. A failed ordinary check controls business flow; it does not automatically request transaction rollback. S++ provides an explicit rollback convention where required. Technical failures are handled by the generated application/runtime rather than expressed as business `try`/`catch` branches.

## One lifecycle contains several independent scenarios

Placing an order, paying, shipping, confirming receipt, cancelling and requesting a return are separate business scenarios. The Petstore interface drives this lifecycle by invoking the appropriate scenario. It does not send a command string to one giant scenario that branches into every possible operation.

This has a tradeoff. The model contains more clearly named operations and their agreements. In return, each operation declares a smaller, more understandable business scope. A reviewer does not need to reconstruct that scope from whichever fields a large shared context happens to use.

## Evaluate the model on a change

A useful evaluation is to change a product's name and price after checkout, then inspect the old order. Another is to reject a payment because the buyer's allowed funds would be exceeded. These tests reveal whether roles preserve the right facts and whether service boundaries carry the intended rules.

The complete [source browser](/sources/petstore-demo/) exposes the SPP, APP and PHY definitions. For the next step, read [business transactions and infrastructure](/articles/business-transactions-and-infrastructure/) or the [book's role model](/book/part-01-roles-and-services/03-roles/). The demonstrations run through generated Java with a separately supplied SDK; they are not a finished production commerce platform.
