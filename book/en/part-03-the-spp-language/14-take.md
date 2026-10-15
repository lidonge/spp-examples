# Chapter 14 — Declaring Role Relationships with take ... as

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Goods defines facts required by a sales role, but not who plays it. `take ... as` declares players, mappings, borrowed facts and role-owned facts. Players follow `take`; the role follows `as`. `take Product as Goods` means Product plays Goods.

## One-Party Role Playing and Mapping

Petstore maps products to goods:

```spp
take Product as Goods {
    mapsame;
    String sku = productCode;
}
```

`mapsame` explicitly enables compatible same-name mappings. If Product and Goods both have name, goods can obtain it from the product. Differently named fields need explicit mapping, here Product.productCode to Goods.sku.

This is not the default. The following declares only sku's source, without automatically mapping name:

```spp
take Product as Goods {
    String sku = productCode;
}
```

A `take ... as` shorthand without a block also only declares the relationship. `takeall` explicitly imports player properties and creates mappings; it differs from the shorthand.

Mapping also determines ownership. Borrowed facts remain owned by their player; added or explicitly redefined facts belong to the role. Queries complete both, but saves must respect ownership boundaries.

## Querying the Chain and Filling Properties

Goods queries retrieve role facts and the corresponding Product. Declared mappings then fill Goods from source facts.

“Product.name was queried” and “Product.name supplies Goods.name” are different steps. Retrieval obtains data; mapping chooses its use. With mapsame the name can be completed. With only sku mapping, querying Product creates no name mapping. Recursive chain querying therefore does not make mapsame optional by default.

## Joint Role Playing

Goods and buyer jointly play a cart line:

```spp
take Goods, Buyer as CartLine {
    Goods goods = Goods;
    Buyer buyer = Buyer;
    int quantity;
}
```

The declaration identifies two players. `Goods goods = Goods;` maps the entire goods participant into the cart line: the left Goods is the property type, goods its name in CartLine, and the right Goods the declared player.

`Buyer buyer = Buyer;` is analogous. The right side does not create a new buyer or read a same-name property. The generated mapper supplies the player object; compatible undeclared target properties are added by the compiler.

```text
CartLine
├─ goods: Goods, the item selected
├─ buyer: Buyer, who selected it
└─ quantity, selected for this line
```

Quantity is CartLine's own fact and must be declared in the role definition. Access names as `cartLine.goods.name` and `cartLine.buyer.name`, even if both participants have name. This is business structure; APP determines storage.

Alex and Jordan select the same goods, two and three units respectively. The lines share goods but differ in buyer and quantity. CartLine preserves which buyer selected which goods, while APP locates each line by both identities.

## Whole-Participant Mapping Versus takeall

The current keyword for bulk importing player properties is `takeall`; there is no `mapall`. It creates a different structure from whole-participant mapping.

For Goods with sku and name:

```spp
take Goods as DisplayGoods {
    takeall;
}
```

`takeall` imports them into DisplayGoods, adding missing properties and mappings. Access becomes `displayGoods.sku` and `displayGoods.name`, without a goods grouping property.

|Declaration|Role Structure|Name Access|
|---|---|---|
|`Goods goods = Goods;`|Goods-typed property preserving the entire participant|`cartLine.goods.name`|
|`takeall;`|Player properties imported into the role itself|`displayGoods.name`|

A cart line needs both goods and buyer, and whole mapping gives each a distinct place. Applying takeall to both does not automatically create goods and buyer groups. Same-name properties need explicit source distinction.

`mapsame` maps existing compatible same-name role properties; `takeall` also imports properties the role has not declared. Choose whether business needs whole participants or selected properties before declaring mappings.

## Role-Owned Facts

A merchant played by Alex may borrow personal facts and own store name “Alex's Pet Store” and operating funds. Personal-data changes are obtained through mappings; changing store name changes merchant facts, not Alex's personal name.

Distinguish borrowed and identity-specific facts. Contracts retaining historical settlement information are a separate requirement, discussed in Part IV, Chapter 18.

## Legality and Persistence

The compiler checks that players are defined legal participant types, targets are roles, and property types satisfy the relationship. The current strict check allows Entity, Reference and Role but rejects Contract as player, when `strictRoleOnlyBusinessModel` is enabled.

Contracts can still be passed as service or scenario context for calculation, validation and later processing. Refunds can read the original order while buyer and merchant participate. Containing lines does not mean playing lines; composition differs from role playing.

A string name cannot become a number in a same-name mapping. Whole-participant mapping must reference a declared player and match the target type. These errors belong at compilation, not at query or save time.

Legal declarations enable generated types, mappings and metadata, but do not create participants. Person may play Merchant without automatically establishing a merchant record for Alex; opening and saving remain scenario activities.

Persistence respects ownership. Ordinary role updates maintain role facts; customer or product data uses its appropriate built-in services. Compile-time legality and runtime participant-specific querying and saving jointly support the relationship.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](13-business-models.md) · [Next Chapter](15-atomic-services.md)
