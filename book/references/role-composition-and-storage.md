# Role composition and independent storage identity

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## Agreed model

A Role declares the structure consumed by services. Participant members form its intrinsic composition; scalar facts remain role facts. `take` adds explicit performer relationships and does not replace intrinsic members or implicitly flatten every source attribute. Type names can be used when member names are omitted. Explicit names and mappings remain available for ambiguity.

```spp
Role CartLine {
    Buyer;
    Goods;
    int quantity;
}
```

The intrinsic Buyer/Goods relationship needs no repeated `take Buyer, Goods`. `take Extra as CartLine;` adds Extra while retaining Buyer and Goods. An identity-only role can be declared with `Role Goods;`, followed by `take Product, Package as Goods;`. Role and performer identities are separate. Intermediate roles are preserved when traversing the performer chain.

## Joint and alternative take clauses

A comma joins performers within one clause. Separate clauses describe alternatives. Intrinsic role members are mandatory in every alternative. Explicit clauses do not retain an extra intrinsic-only branch.

```spp
Role R { R1; R2; }
take A as R;
take B as R;
take A, B as R;
```

With the referenced types declared, the complete combinations are `{R1, R2, A}`, `{R1, R2, B}` and `{R1, R2, A, B}`. Without explicit take clauses, `{R1, R2}` is the default. For `Role R;`, `take A as R; take B as R; take C, D as R;` allows `{A}`, `{B}` or `{C, D}`. Inactive alternatives have null identity columns or no relationship rows. Generated queries hydrate only the selected branch. Generated storage validates complete combinations and removes stale links when replacing a branch. It does not choose the first declared branch when no performer identity is available.

## APP storage

Role identity is independent of the changing performer set. APP can generate an opaque primary key absent from SPP. Existing explicitly configured business or composite keys remain supported. A role table without an explicit primary key receives an APP-only String `roleId` key. `identity independent;` explicitly requests this policy for an APP-only primary key; it disables sole-performer key reuse.

```app
tables roles {
    table CART_LINES(CartLine) {
        primarykey notnull String cartLineId;
        identity independent;
        performers inline;
    }
}
```

`performers inline;` stores performer identity key records beside the role's facts. `performers in CART_LINE_PLAYERS;` stores them in a separate relationship table associated by the stable role key. These technical keys and tables do not become business fields. Adding a relationship never changes an existing role identity. Cardinality and required business facts are not changed by storage layout. Performer facts continue to be maintained by their owning domains.

## Implementation and verification path

1. Normalize intrinsic and explicit role composition after parsing; bind unique existing members and validate ambiguous mappings without changing the declared structure.
2. Add APP identity/layout configuration, validation and generated metadata/DDL.
3. Generate independent insertion identity and persist/load/delete relationship identities using the same local transaction resource as the role table.
4. Simplify current demo declarations; update Chinese/English book and references.
5. Verify parsing, role mapping generation, stable identity across relationship extensions, both storage layouts, rollback and existing demo generation/acceptance.

Compared with composite performer primary keys, an independent key decouples identity from composition. It costs an extra key and association/index storage. Separate relationship tables make extension easier, at the cost of additional reads. Schema migrations and historical backfill remain explicit deployment work; creating tables is not an automatic migration of existing data.

## Current realization and boundaries

The implemented persistence realization is the generated JDBC repository. Same-table links use technical `spp_performer_<slot>` identity-key columns; separate tables use `(role_type, role_id, performer_type, performer_key)`. A composite source identity is encoded as an identity key record, not a copy of the source business object. Named same-type members retain distinct storage slots. Role/member identity stays in technical query metadata and internal nested snapshots, never in SPP properties or public business beans.

A query with only an opaque primary key requires identity obtained through the technical query protocol. It must not guess a role from its current player set. Non-primary-key selection remains an explicit APP query. Adding inline columns requires schema migration; adding separate-table rows does not backfill business participation. The framework does not invent missing historical relationships. Cross-resource transaction realization continues to follow the selected APP/PHY policy; these link tables do not create a distributed atomicity guarantee.

The Petstore CartLine table demonstrates an independent key and separate player table. StockLine demonstrates inline links while retaining its explicitly configured business identity. The bank demo keeps its explicit account-number keys and scalar take mappings, which are not redundant intrinsic-member declarations.

## 验证记录（2026-10-16）

本轮按最终约定完成回归：lang 377 项、appframe 640 项、generator 108 项，均通过。两个独立样例的完整生成、编译与验收通过：Petstore 40 项，存款 demo 88 项。合计 1,253 项，无失败、错误或跳过。最终针对联合/备选扮演、请求绑定及独立身份存储的 28 项专项检查也全部通过。

新用例覆盖内在组合与类型名访问、单条 take 联合、多条 take 备选与内在成员逐方案合入、空角色声明、禁止映射创造未声明成员、显式命名的同类型成员、独立技术主键、同表与分表关系、扩展后身份不变、备选方案精确选择、不完整联合组合拒绝保存、切换方案后旧关联清理、事务回滚和嵌套/复制身份保持。Petstore 的购物车用例实际检查 SHOP_CART_LINES 独立主键、SHOP_CART_LINE_PLAYERS 两条身份关联、替换/清空后无旧关联残留，并确认技术主键不出现在业务 JSON。

网站从源码本地构建成功；176 个页面、19,756 个本地链接/资源检查通过，529 个公开源文件及文档链接/许可边界检查通过。未部署官网，未修改已有数据库，未自动提交。

运行验收基于当前 JDBC/H2 及 LOCAL 演示配置；不能把这些结果称为真实 XA、Seata AT 或分布式 TCC 的端到端验收。旧数据库的键与关系布局升级需要显式迁移，框架不会把来源的当前事实当作历史业务关系自动补齐。
