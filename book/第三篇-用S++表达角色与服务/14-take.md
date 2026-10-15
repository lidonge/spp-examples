# 第14章 用 take ... as 声明扮演关系

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

定义 Goods 只说明销售角色需要哪些事实，模型还要说明由谁扮演它。S++ 用 `take ... as` 声明这一关系，并表达属性映射、借用和角色自己的事实。

`take` 后面写扮演者，`as` 后面写所扮演的角色。例如 `take Product as Goods` 表示 Product 扮演 Goods。

## 单方扮演与映射

Petstore 将产品映射为商品：

```spp
take Product as Goods {
    mapsame;
    String sku = productCode;
}
```

`mapsame` 显式启用同名属性映射。例如 Product 与 Goods 都有 name，类型等条件满足时，商品名称可以从产品名称取得。名称不同的属性则显式映射：上例把 Product.productCode 映射为 Goods.sku。

`mapsame` 不是默认规则。若只写下面的映射，就只明确了商品编号的来源，同名的 name 不会因此自动加入映射：

```spp
take Product as Goods {
    String sku = productCode;
}
```

无映射块的 `take ... as` 简写也只声明扮演关系，不自动启用同名映射。`takeall` 是另一种明确的写法，用于让角色继承扮演者的属性，并为相应属性生成映射；它与仅声明扮演关系的简写不同。

映射还决定事实归属。直接借用的事实由原扮演者拥有，角色新增或明确重定义的事实由角色拥有。查询需要补全两类事实，保存则不能任意跨越所有权边界。

## 查询扮演链与属性回填

角色查询会沿扮演关系查询来源事实。例如查询 Goods，系统取得商品自己的事实，并查询相应 Product。取得产品之后，再按照已声明的映射把相应属性补入 Goods。

因此，“查询到了 Product.name”和“把 Product.name 用作 Goods.name”是两个步骤。前者取得来源数据，后者由映射决定。上例显式使用 mapsame 时可以补全同名名称；仅映射 sku 时，查询产品不会自动增加 name 的映射。这也解释了为什么递归查询扮演链，并不使 mapsame 成为可省略的默认行为。

## 联合扮演

购物车明细由商品与买家共同扮演：

```spp
take Goods, Buyer as CartLine {
    Goods goods = Goods;
    Buyer buyer = Buyer;
    int quantity;
}
```

第一行声明两个扮演者：Goods 和 Buyer 共同扮演 CartLine。映射块中的两行分别把这两个参与者作为整体放到购物车明细中。以 `Goods goods = Goods;` 为例：

- 左边的 `Goods` 是属性类型，说明这个属性表示一个商品角色。
- 左边的 `goods` 是 CartLine 中的属性名。
- 右边的 `Goods` 指向第一行声明的商品扮演者，表示把这个参与者整体映射给 `goods`。

`Buyer buyer = Buyer;` 同理。右边写的是扮演者名称，不是在创建一个新买家，也不是读取买家的某个同名属性。生成的映射把参与者对象交给相应属性；若角色尚未声明该属性，编译器会补上类型相符的属性。

因此，购物车明细的业务结构可以这样理解：

```text
CartLine（购物车明细）
├─ goods：Goods（本条明细的商品）
├─ buyer：Buyer（选购该商品的买家）
└─ quantity（本条明细的选购数量）
```

这里的 quantity 是 CartLine 自己的事实，需要在角色定义中声明。使用商品名称时访问 `cartLine.goods.name`，使用买家名称时访问 `cartLine.buyer.name`。即使商品和买家都有 name，也能明确区分。上述结构表达业务上的参与关系，具体怎样存储仍由 APP 配置决定。

小林和小王都把同一商品加入购物车，分别选了 2 件和 3 件。两条明细的商品相同，买家不同，数量也不同。CartLine 因而要保留“哪位买家选了哪个商品”的关系；数量属于这段关系，APP 按双方身份定位各自明细。

## 整体参与者映射与 takeall 的区别

当前语言中，批量引入扮演者属性的关键字是 `takeall`，并没有 `mapall`。它与上面的整体参与者映射有不同的结构。

例如，Goods 有 sku、name 两个属性：

```spp
take Goods as DisplayGoods {
    takeall;
}
```

`takeall` 把 Goods 的属性引入 DisplayGoods；尚未声明的属性会被补入，并生成相应映射。因此可以直接访问 `displayGoods.sku`、`displayGoods.name`，无需先经过一个 goods 属性。

| 写法 | 角色中的结构 | 商品名称的访问方式 |
| --- | --- | --- |
| `Goods goods = Goods;` | 有一个 Goods 类型的 goods 属性，保留完整商品参与者 | `cartLine.goods.name` |
| `takeall;` | 把扮演者的属性引入角色本身 | `displayGoods.name` |

购物车明细需要同时表达“商品”和“买家”，整体参与者映射使两者各有明确的位置。如果对 Goods、Buyer 一起使用 `takeall`，它也不会自动产生 goods、buyer 两个分组；双方的同名属性还需要明确区分来源，不能仅靠批量引入表达“商品名称”和“买家名称”。

`mapsame` 又有所不同：它为角色已有的兼容同名属性生成映射；`takeall` 还会把扮演者中角色尚未声明的属性引入角色。选择写法时，先确定业务需要的是完整参与者，还是参与者的某些属性，再声明对应的映射。

## 角色自己的事实

角色可以借用扮演者的资料，也可以拥有这个业务身份需要的事实。例如，小林扮演商家时，商家借用小林的个人资料，同时拥有店铺名称“林家宠物店”与经营资金。小林修改个人资料，商家查询按映射取得相应资料；修改店铺名称，则是在维护商家自己的事实，不是在修改小林的个人姓名。

因此，声明扮演关系时需要分清：哪些属性来自扮演者，哪些属性属于角色自己的业务身份。合约保留成交时的信息是另一项要求，见第四篇第18章的说明。

## 扮演关系的合法性与持久化

`take ... as` 是需要编译器检查的业务声明。编译器检查扮演者是否为已定义的合法参与者类型、`as` 后面的目标是否为角色，以及属性类型是否符合扮演关系的要求。当前实现的严格业务模型检查允许 Entity、Reference 或 Role 扮演角色，拒绝把 Contract 当作扮演者；这一检查由 `strictRoleOnlyBusinessModel` 配置启用。

合约仍可以作为服务或场景的上下文传入，供计算、校验和后续处理使用，不必为了读取合约就声明扮演关系。例如，退款场景可以读取原订单合约，同时由买家、商家等角色参与退款。合约包含订单明细，也不等于合约扮演明细：包含关系与扮演关系需要分别表达。

例如，扮演者的 name 是字符串，角色中的同名属性也必须保持相同类型，不能改成数值类型；整体参与者映射也必须指向声明中的扮演者，并与目标属性的类型一致。这样的错误应在编译时发现，不应等到查询或保存时才暴露。

声明合法之后，编译器才能据此生成类型、映射与查询元数据。但声明一个扮演关系，并不等于创建一个实际参与者。例如，声明 Person 可以扮演 Merchant，不会自动为小林建立商家记录；何时开店、何时保存商家自己的资料，仍由场景安排。

持久化也需要遵守事实归属。普通角色更新自己的事实，客户或产品的资料则通过相应的内置服务维护。编译时确认谁可以扮演谁，运行时根据具体参与者完成查询与保存，两者共同支撑扮演关系。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](13-business-models.md) · [下一章](15-atomic-services.md)
