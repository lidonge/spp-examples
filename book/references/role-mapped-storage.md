# APP 角色映射属性的当前值与独立快照

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

SPP 用 take 描述业务角色与扮演者的属性映射；APP 决定映射属性是否在角色表保留副本。模型、业务表达式和 PHY 的数值表示彼此独立。角色自己的新增属性继续正常保存，扮演者仍由原域维护。

```spp
Role OrderLine { String lineNumber; Goods; String name; BigDecimal(19, 2) unitPrice; }
take Goods as OrderLine { String name = name; BigDecimal unitPrice = price; }
```

```app
tables roles {
    table ORDER_LINES(OrderLine) {
        primarykey(OrderLine.lineNumber);
        foreignkey(OrderLine.Goods) references Goods;
        snapshot(OrderLine.name, OrderLine.unitPrice);
    }
    table GOODS(Goods) {
        primarykey(Goods.sku);
        current(Goods.name);
    }
}
```

映射属性缺省为 current：本角色不保存业务值副本，查询角色时按 take 规则查询扮演者并补全当前值。身份关联与主键仍按原规则保存。snapshot 为角色生成独立物理列，并将其从“仅由扮演者补全”的排除清单移出；首次插入保存本次业务已经确定的角色值，不在提交时重新查询并替换成交报价。后续查询保留这些角色表的值，即使扮演者改名、调价。反向 take 映射不将快照写回扮演者。

APP 配置只针对当前角色的普通标量映射属性，支持改名映射、多扮演者中的明确属性映射及 takeall/mapsame。同一属性不能重复配置或同时 current/snapshot；角色自有属性、实体/合约、集合、参与者关联、身份键和量子属性不接受此配置。它不是外键对象的整对象复制，也不将普通副本变成量子事实。

快照独立于当前商品。它保证不会自动跟随扮演者变化，不禁止业务显式修改本角色的独立属性；更正成交明细仍应有明确业务场景。本版本不提供对已有缺失快照数据的自动补录，因为当前商品值不能还原历史成交值。

Petstore 订单明细的 name 与 unitPrice 显式映射商品 name 与 price，并在 APP 中保存独立快照；商品名称使用 current。默认主键查询旧明细时保留其历史名称/单价，并通过商品服务补全关联商品的当前名称/价格；订单集合查询也保留成交明细，后续履约、付款及退款仍使用成交明细和订单金额。

实施路径：完善 APP 解析及语义校验 → 让角色存储归属、DDL 和仓储元数据接受快照列 → 在生成查询补全时保护快照、反向映射时跳过副本 → 更新 Petstore 建模/APP → 验证商品变更、旧订单重读、状态更新再读以及新订单采用新值。

相比传统代码手动复制 DTO 字段，APP 声明把复制范围与存储责任显式化，生成器统一落实，不需要每个查询都手写防覆盖逻辑。代价是额外存储、历史值与当前值并存，以及需要明确业务创建角色时的取值时点。切换既有部署的模式需要相应数据库迁移；配置不会凭空恢复历史数据。

## 验证结果

2026-10-12：语言校验、运行时和生成器回归通过；Petstore 原有 34 个用例通过，新增成交快照用例单独通过。该用例组合生成的 SPP 场景完成下单、产品改名、商品单价从 29.90 调整到 39.90、旧订单集合查询、明细主键查询、付款和再次下单。旧明细名称不变、单价仍为 29.90、金额仍为 59.80；明细主键查询关联商品采用当前资料；付款后旧值保持，新订单采用新名称及 39.90。

语言用例覆盖 current/snapshot 的存储归属、角色自有属性及扮演者主键误配置、重复冲突和未知属性。运行时用例覆盖补全后的快照保护，包括独立快照为 null 时不使用当前资料替代。生成的订单明细 DDL 包含名称/单价列，元数据包含 snapshotFacts=name,unitPrice，反向映射不生成这两个字段的写回语句。
