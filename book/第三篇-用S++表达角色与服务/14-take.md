# 第14章 角色组合与 take 扮演关系

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

角色既是服务依赖的结构，也是业务参与身份。角色不关心具体由谁来扮演，但必须明确服务可以使用什么成员。参与者成员同时表达内在角色组合，普通属性表达这个组合自己的事实。

## 角色声明已经表达内在组合

```spp
Role CartLine {
    Buyer;
    Goods;
    int quantity;
}
```

Buyer、Goods 的类型和业务身份已经确定，不需要重复写 `take Buyer, Goods as CartLine`，更不必重复写 `Buyer buyer = Buyer`。服务可以使用 `CartLine.Buyer`、`CartLine.Goods` 和 `CartLine.quantity`。生成的 Java/JSON 仍采用正常的 bean 属性名，既有界面不必随 SPP 的省名写法改动。

角色不能只留下 quantity，再由一个空的 take 块隐式增加 Buyer、Goods。那会让服务依赖的结构失去明确声明。显式名字仍然可用，例如 `Buyer purchaser;`；同类型多个成员必须按名字区分，不能仅按类型猜测该用哪一个。

## take 补充而不替换内在组合

```spp
take ReservationSource as CartLine;
```

假设 ReservationSource 已在模型中声明，这个方案由 Buyer、Goods、ReservationSource 联合扮演 CartLine，quantity 仍是角色自己的事实。单条 take 内的逗号表示联合，多条 take 之间表示备选；角色声明中的内在参与者会加入每一个备选方案。

```spp
Role R;
take A as R;
take B as R;
take C, D as R;
```

假设 A、B、C、D 已定义，允许的组合是 `{A}`、`{B}` 或 `{C, D}`。一行 R 选择其中一个完整组合：A 与 B 不会因两条 take 自动联合；C 与 D 则必须同时存在。

```spp
Role R { R1; R2; }
take A as R;
take B as R;
take A, B as R;
```

假设相关类型已定义，允许的组合是 `{R1, R2, A}`、`{R1, R2, B}` 或 `{R1, R2, A, B}`。R1、R2 在每行中都必需。显式声明 take 后，内在组合本身不额外构成一个独立备选；没有 take 时，内在组合就是缺省方案。选中的方案必须完整，不能保存不属于任何方案的零散组合。同表布局中，未选中来源的身份列为空；分表布局中不保存它们的关系行。

内在 Buyer 可能由 Person 扮演，Goods 可能由 Product 扮演。查询和身份关联会沿实际扮演链处理，仍保留 Buyer、Goods 的业务身份，不把中间角色抹平为根实体。

仅需先声明角色身份时，可以写：

```spp
Role Goods;
take Product, Package as Goods;
```

这里假设 Product、Package 已定义。它表达两者共同扮演 Goods，但不会自动把所有产品和包装属性平铺到 Goods。服务需要的商品属性仍应明确声明；映射选择它们的来源。没有属性的角色也可以表达一种身份。

## 参与者绑定与普通属性映射

已有成员与扮演者类型唯一对应时，编译器生成整体参与者映射。保留显式写法用于定制，但目标成员必须已经声明，映射不能悄悄创造成员。

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

Goods 的整体关系已由角色成员表达。name 和 unitPrice 的来源则明确映射到商品名称与售价。若多个来源都能提供同一属性，需要明确选择，不能靠遍历先后决定含义。

`mapsame;` 显式启用兼容同名属性映射，并不是空 take 的缺省行为。查询到了 Product.name，不等于已经约定将其用作 Goods.name。既有 `takeall;` 是显式引入来源属性的兼容写法；新模型应优先在 Role 中完整声明结构，避免把服务依赖藏在导入过程中。

参与者数组保留集合语义，各成员独立携带身份；不能把整个集合压成一个同类型的标量扮演者。服务直接按已声明成员访问，类型名不能区分多个同类型成员时必须使用显式名字。

## 独立角色身份与 APP 存储

增加扮演者不应该改变已经存在的角色身份。因此，角色表没有显式主键时，APP 缺省增加一个 SPP 不可见的 String roleId；也可以自行命名独立主键：

```app
tables roles {
    table SHOP_CART_LINES(CartLine) {
        primarykey notnull String cartLineId;
        identity independent;
        performers in SHOP_CART_LINE_PLAYERS;
    }
}
```

插入服务生成技术身份，查询、更新和删除继续使用该身份。SPP 不声明或操作 cartLineId。扮演者的主键是关联信息，不再组成缺省的角色主键；明确配置的历史业务主键和联合主键仍受支持。独立身份与业务唯一约束是不同问题。

`performers inline;` 将扮演者身份记录与角色事实放在同表；`performers in 表名;` 将身份关联放在另一张表，以角色主键关联。当前 JDBC 实现的同表方式使用每个扮演者对应的技术身份列，分表方式使用 role_type、role_id、performer_type 与 performer_key。它们保存身份，不复制或更新来源域的全部事实。

角色与关联写入使用同一个已声明事务的本地资源，失败一并回滚。角色内嵌在合约或其他参与者中时，技术身份由内部持久化元数据携带，不混入 SPP 属性。普通事实的 current/snapshot 选择独立于关系表布局；成交价格副本仍在角色表中保存。

添加扮演关系不意味着历史数据已经补齐。是否必需由业务约定和校验决定；新增同表身份列需要正常的数据库迁移，分表可以追加新关系行，但不会自动建立真实业务联系。APP 选择布局，PHY 选择数据源与数据库实现；布局不能改变业务基数、资格和义务。

规范与实施说明见[角色组合与存储](../references/role-composition-and-storage.md)。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](13-business-models.md) · [下一章](15-atomic-services.md)
