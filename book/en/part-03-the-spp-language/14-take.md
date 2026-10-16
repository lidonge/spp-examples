# Chapter 14 — Role Composition and take Relationships

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

A role is both a business identity and the structure consumed by services. It does not depend on a particular player, but its members must be explicit. Participant members declare intrinsic composition; ordinary properties describe facts belonging to that composition.

## Intrinsic composition needs no repeated take

```spp
Role CartLine {
    Buyer;
    Goods;
    int quantity;
}
```

Buyer and Goods are already intrinsic participants. Repeating `take Buyer, Goods as CartLine` and assigning the same players to the same members adds no information. Services use `CartLine.Buyer`, `CartLine.Goods` and `CartLine.quantity`. Generated Java/JSON keeps ordinary bean property names.

Declaring only quantity and silently adding members through an empty take would leave the service contract incomplete. Explicit member names remain valid. Two Buyer members must be distinguished by name; a type alone cannot select between them.

## take adds players rather than replacing intrinsic roles

```spp
take ReservationSource as CartLine;
```

Assuming ReservationSource is declared, this branch jointly combines Buyer, Goods and ReservationSource. Quantity remains a role fact. Commas within one take mean joint participation; separate take clauses are alternatives. Intrinsic participants join every alternative.

```spp
Role R;
take A as R;
take B as R;
take C, D as R;
```

With A, B, C and D declared, the valid combinations are `{A}`, `{B}` or `{C, D}`. Each R row selects one complete combination. Separate A and B clauses do not make them joint; C and D must both be present.

```spp
Role R { R1; R2; }
take A as R;
take B as R;
take A, B as R;
```

With the referenced types declared, the valid combinations are `{R1, R2, A}`, `{R1, R2, B}` or `{R1, R2, A, B}`. R1 and R2 are mandatory in every row. When explicit take clauses exist, intrinsic composition alone is not an additional alternative; without a take clause it is the default branch. Persistence requires one complete declared combination. In an inline layout, inactive player identity columns are null; in a separate layout, their relationship rows are absent.

If Person plays Buyer and Product plays Goods, the composition can be traced to those sources. Buyer and Goods remain distinct intermediate business identities.

An identity-only role is also valid:

```spp
Role Goods;
take Product, Package as Goods;
```

The players are explicitly composed, but their entire property sets are not automatically flattened into Goods. Declare the facts needed by services and map their sources. A role with no properties can still express an identity.

## Participant binding and scalar mapping

A unique match between an existing member and its player produces an automatic whole-participant mapping. Explicit mappings remain available, but must target declared members and must not silently add fields.

```spp
Role OrderLine {
    Goods;
    String name;
    BigDecimal(19, 2) unitPrice;
    int quantity;
}

take Goods as OrderLine {
    String name = name;
    BigDecimal unitPrice = price;
}
```

The Goods relationship is intrinsic. The scalar mappings select goods name and price as the sources of order-line facts. Explicitly resolve competing sources.

`mapsame;` enables compatible same-name mappings; it is not implied by an empty take block. Retrieving Product.name does not by itself select it as Goods.name. The existing `takeall;` keyword is a compatible explicit property-import form; new models should prefer complete Role declarations so service dependencies remain visible.

Participant collections retain their element identities. They are not converted into one scalar player. Explicit member names remain necessary when several members share a type.

## Stable independent identity and APP storage

Extending composition must not change an existing role identity. A role table without an explicit key receives an APP-only String roleId. A named independent key can be declared as follows:

```app
tables roles {
    table SHOP_CART_LINES(CartLine) {
        primarykey notnull String cartLineId;
        identity independent;
        performers in SHOP_CART_LINE_PLAYERS;
    }
}
```

Insertion generates the technical identity; later CRUD uses it. SPP neither declares nor modifies cartLineId. Player keys are relationship facts, not the default role primary key. Explicit historical business/composite keys remain supported. Business uniqueness and physical identity are separate concerns.

`performers inline;` stores player identity records in the role table. `performers in TABLE;` uses a separate association table joined through the stable role identity. The current JDBC realization uses technical per-player identity columns for the inline layout, and role_type, role_id, performer_type and performer_key for the separate layout. These contain identities, not copies of all source-domain facts.

Role and association writes use the same local transaction resource and roll back together. Nested participants carry technical identity through private persistence metadata rather than business properties. The current/snapshot policy for ordinary facts is independent of this layout; agreed order prices still belong to the role's snapshot storage.

New relationships do not backfill historical business facts. Business rules determine whether they are required. Adding inline columns requires a schema migration; separate tables can receive new association rows, but cannot invent real relationships. APP selects layout; PHY selects the database and deployment. Neither changes business cardinality or obligations.

See the [composition and storage specification](../../references/role-composition-and-storage.md).

---

[Part contents](README.md) · [Book contents](../README.md) · [Previous](13-business-models.md) · [Next](15-atomic-services.md)
