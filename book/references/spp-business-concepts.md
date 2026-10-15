# S++ 业务建模核心概念

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 目标

跨领域业务样例、创新点覆盖与可执行验收见 business-showcase (maintainer reference: `../business-showcase/README.md`)，其中包含需求、实施路径、能力矩阵及 SPP 与传统 Java 方案对照。

原子服务的数学计算、逻辑规则、参与者契约及 PHY 数字适配遵循[原子计算服务设计](atomic-calculation-services.md)。

业务数字计算与具体表示的分层遵循[数值业务语义与 PHY 实现](numeric-physical-semantics.md)：SPP 数字声明提供默认实现提示，具体重定义由 PHY 承接，物理表示问题不能静默改变业务数学结果。

S++ 是严格区分业务语言和技术实现的服务语言。`.spp` 文件只描述业务世界中真实存在的概念、参与关系、合约产物和服务场景；`.app` 文件描述运行、检索、标识、仓储、事务资源、幂等、协议头、外部适配等技术实现约束。

因此，`Entity`、`Reference`、`Role`、`Contract` 都是纯业务概念，不能带有数据库主键、接口流水、检索标识、消息 ID、仓储 key、路由 key、租户隔离字段等技术实现影子。

## Entity

`Entity` 是自然实体的直接映射，是服务域内自然存在、可被业务人员直接识别的对象。

典型例子：

- `Product`：产品。
- `Store`：仓库或门店。

`Entity` 的数量在一个服务域中通常很少。它不应该为了页面展示、接口入参、数据库表结构或技术检索而膨胀。

`Entity` 只表达自然实体本身的业务属性。例如产品的名称、品牌、分类属于产品自然属性；数据库主键、索引号、接口请求号、内部编码规则不属于 `Entity` 的业务属性，除非它们本身就是业务世界中被自然使用的概念。

自然实体只能包含或关联自然实体，不能包含某个场景角色。如果一个概念需要把自然实体和角色组合起来，例如“某个仓库中的某个上架商品库存”，它本身就不是自然实体，而应该建模为 `Role`。

## Reference

`Reference` 表示对外部服务域自然实体的引用。

它和 `Entity` 的区别是生命周期归属不同：

- `Entity` 属于当前服务域。
- `Reference` 属于外部服务域，当前服务域只引用它、识别它或使用它的业务快照。

例如在额度电商域中，`Customer` 不是电商域拥有生命周期的自然实体，而是客户域的实体引用。电商域可以在订单、额度账户或场景中引用客户，但客户创建、客户资料维护、客户生命周期不属于额度电商域。

第一版 demo 可以用本地 mock 或快照仓储模拟外部域查询，但这种 mock 是 `.app` 或运行适配层的实现选择，不改变 `Reference` 的业务语义。

## Role

`Role` 是服务域中最多的概念。它是场景和服务的参与者，也就是自然实体进入服务前必须扮演的业务角色。

核心规则：

- 自然实体不能直接参与服务和场景，必须先扮演某种 `Role`。
- 一个实体可以在不同场景中扮演不同角色。
- 多个实体可以共同扮演一个组合角色，这叫联合扮演。
- S++ 用 `take Entity as Role` 或 `take EntityA, EntityB as Role` 显式声明自然实体扮演角色。
- 角色可以再扮演新的角色，这是第二阶段可以扩展实现的能力。
- 角色可以继承实体的全部或部分属性。
- 角色可以重载实体属性名，但不能改变属性类型。
- 角色可以拥有不从实体继承来的自有业务属性。

例如 `Product` 作为自然实体不能直接“下单”或“销售”，它需要先在销售/上架场景中扮演 `Goods` 角色，再在下单场景中进一步形成 `SalesItem`、`OrderLine` 或类似角色。`Inventory` 也不是自然实体，它是 `Store` 与 `Goods` 在库存管理场景中联合扮演的库存角色。客户作为外部实体引用也不能直接参与服务，它需要扮演 `Buyer`、`Payer`、`AccountOwner` 等角色。

`Role` 的存在是 S++ 区别于传统面向对象建模的关键点：服务不是围绕对象方法展开，而是围绕场景中的参与者展开。自然实体提供事实基础，角色表达这个事实在某个场景中的参与方式。

面向对象的多态通常来自继承关系；面向服务的多态来自角色扮演。服务和场景只接受 `Role` 作为参与者，并不关心运行时到底由哪个实体、外部引用或已有角色来扮演这个角色。`Goods` 可以由 `Product` 扮演，也可以由后续扩展出的其他业务对象扮演；`Inventory` 可以由 `Store` 与 `Goods` 联合扮演。真正的扮演者身份是运行时绑定和 `.app/.phy` 访问实现要解决的问题，不应该固化成 `Role` 内部的对象字段或 OO 式继承层级。

### take 语法

`take` 是自然实体进入服务和场景之前的显式扮演声明：

```spp
take Product as Goods;
take Goods as SalesItem;
take Store, Goods as Inventory;
```

如果角色属性需要从实体属性继承或映射，可以继续使用映射块：

```spp
take Product as Goods{
    mapsame;
    takeall;
}
```

`take Entity as Role` 或 `take RoleA as RoleB` 表示单个参与方扮演某个角色；`take EntityA, RoleB as RoleC` 或 `take EntityA, EntityB as RoleC` 表示多个参与方共同扮演一个组合角色，也就是联合扮演。这样服务或场景可以在业务表达上使用由自然实体和已有角色形成的新角色，但真正参与服务签名和场景编排的仍然应该是 `Role`，而不是裸 `Entity`。

`Contract` 聚合内部的组成状态不是反向角色扮演。比如 `SalesOrder` 可以包含 `SalesItem[]` 作为订单明细状态，但不能因此写成 `take SalesOrder as SalesItem` 或 `take SalesOrder, Goods as SalesItem`。如果订单明细表达“哪个商品买了多少、单价和行金额是多少”，应写成 `take Goods as SalesItem;`：商品角色在下单场景中继续扮演订单明细角色，订单合约只是聚合这些明细状态。订单总数量、商品金额、折扣金额、占用金额、入账金额和应付金额这类金额字段更进一步，它们不是独立参与者，也不需要单独定义 `OrderAmount` 角色；它们是 `SalesOrder` 合约自己的组成属性，脱离订单没有独立业务生命期。合约组成关系应由 APP DDL 的合约组成、明细索引或后续 composition 语义表达；`take` 只表达运行时业务参与者扮演 Role。

被扮演的角色不应再把扮演者作为一个普通字段持有。例如 `take Product as Goods;` 已经表示某个 `Product` 在销售/上架场景中扮演 `Goods`，因此 `Role Goods` 里不应再声明 `Product product;`。商品角色自己的业务属性是价格、状态、标题、标签等；谁扮演商品这个角色，谁就是商品。若运行期仍需要按产品定位商品，应由 `.app` 的平台列、索引或 repository 规则表达，而不是把扮演关系重复写回 `.spp` 业务模型。

`take Store, Goods as Inventory;` 之后，`Role Inventory` 不应再声明 `Store store; Goods goods;`。库存自己的业务事实是可售数量、安全库存等；门店和商品是运行时扮演者，身份应由 `.app` 的平台主键、命名索引和运行时扮演绑定承接。

第一版 `take` 的作用是建立实体到角色的业务映射和生成 `RoleMapper`。无映射块的简写声明只表达扮演关系，不自动复制字段；需要字段继承时使用 `takeall`、`mapsame` 或显式字段映射。

## Contract

`Contract` 是场景的产物，由场景中参与的角色共同签署形成。它不是某个实体或角色的继承对象，也不是可以反过来扮演内部角色的 performer。

例如销售订单不是一个孤立自然实体，而是买方、商品项、额度账户、库存履约、价格金额等多个参与者在“提交订单”场景中共同形成的合约产物。

`Contract` 应该表达业务承诺、权利义务、状态和可被业务理解的结果。它不应该包含为了检索、标记、幂等、路由或持久化而加入的技术字段。

服务和场景里的签署参与者应优先是 `Role`。`Contract` 可以作为场景形成或后续流转的合约对象、当前上下文对象、快照对象或审计对象出现在服务中，但它不是签署者本身；真正签署合约的是场景中的角色参与方。比如 `SalesOrder` 可以由买方、商品、库存、额度账户等角色共同签署形成；`SalesItem[]` 是合约内部的明细角色状态，订单金额字段是合约内部的金额组成属性，它们都不是由 `SalesOrder` 反向扮演出来的角色。

`SalesOrder.buyer` 与 `SalesOrder.account` 的归属身份不应被强行合并。`buyer` 表达订单购买方，回答“这是谁的订单”；`CreditAccount account` 表达本次订单使用的额度资源，回答“从哪个额度账户扣减”；额度账户归属方由运行时某个 `Customer` 扮演 `CreditAccount` 的 Role performer identity 表达，而不是由 `CreditAccount.customer` 字段表达。购买方、使用的额度账户和额度账户归属方在个人自用额度场景中可以指向同一个客户，但在企业统一授信、家庭代付、渠道商账户代付等场景中也可以不同。是否要求买方与账户归属方一致，应由业务校验规则表达，而不是由模型结构假设。

例如：

```spp
Contract SalesOrder{
    String orderNo;
}
```

如果 `orderNo` 只是为了检索和标记订单的技术属性，就不应该出现在 `.spp` 的 `Contract` 中。它应当在 `.app` 中定义为订单合约的运行标识、仓储 key、外部接口映射或索引规则。

只有当订单编号在业务中本身具有合约含义，例如客户、商户、财务、客服都把它作为业务凭证直接使用，并且它不是由技术层为了存储或路由临时引入的字段时，才可以作为业务属性进入 `Contract`。这个判断必须从业务语义出发，而不是从实现便利出发。

## 技术属性归属

以下内容不属于 `.spp` 业务模型，应放在 `.app` 或运行适配层：

- 数据库主键、外键、索引字段。
- 仓储 key、对象快照 key、分片 key、路由 key。
- `globalSerialNumber`、`messageId`、幂等 key、请求流水号。
- 接口协议头、调用方、租户、渠道、鉴权上下文。
- 技术检索编号，例如仅用于定位订单快照的 `orderNo`。
- 事务资源 ID、事务模式、补偿服务绑定。
- 外部服务 mock、repository hydrate、JSON 快照等参考实现细节。

`.app` 可以为业务概念补充这些技术规则，例如：

```spp
scope{
    local (in baseIn, out baseOut){
        repository(appKey(SalesOrder), salesOrder) querySalesOrder;
        at resource(salesOrder) snapshot(appKey(SalesOrder)) openSalesOrder;
    }
}
```

上面的 `appKey(SalesOrder)` 是示意语法，表达的是：订单合约的检索、快照、索引和技术标识由 `.app` 定义，而不是污染 `.spp` 中的 `Contract SalesOrder`。

## 建模原则

S++ 建模时先问四个问题：

1. 这是当前服务域自然拥有的实体吗？如果是，建模为 `Entity`。
2. 这是外部服务域拥有的实体吗？如果是，建模为 `Reference`。
3. 它是否以某种身份参与场景或服务？如果是，建模为 `Role`。
4. 它是否是场景形成的业务产物？如果是，建模为 `Contract`。

如果一个字段或概念的存在理由是“为了查到它、存下它、区分它、路由它、保证幂等、暴露接口、生成代码、回滚事务”，它就不是 `.spp` 的业务概念，应进入 `.app` 或框架运行层。

本次 review 进一步明确：`xxxId`、`xxxNo`、`skuId` 这类字段默认应先被视为技术标识，而不是业务属性。只有当它们本身是业务世界直接使用的凭证，例如客户、商户、客服、财务都会直接使用的订单号、合同号、发票号，并且不是技术层为了存储、检索、路由或快照定位引入的字段，才可以留在 `.spp`。

否则：

- 数据库主键放在 `.app` 的 `tables`/`primarykey`。
- 外键和关联 key 放在 `.app` 的 `foreignkey` 或映射规则。
- 查询 key 放在 `.app` 的 repository/index 规则。
- 快照 key 放在 `.app` 的 `snapshot(...)`。
- 外部系统 key 放在 `.app` 的 remote adapter 或接口映射。

## 对当前 credit-commerce 的约束

当前 `credit-commerce` 第一版 demo 中仍保留了一些形似技术标识的字段，例如 `Customer.customerId`、`Product.productId`、`Goods.skuId`、`SalesOrder.orderNo`。当前约定不是把它们一概视为实现折中，而是逐个声明语义：`Product.productId`、`Goods.skuId`、`SalesOrder.orderNo` 这类当前业务会直接使用的编号已经在 `.app` 对应表上用 `@businessCredential` 标记为业务凭证，并由 APP DDL 平台主键、索引、Role performer identity 和 current snapshot key 统一承接；如果某个部署把这些字段解释为纯技术标识，应移除业务凭证声明，并把字段语义完全下沉到 `.app`、repository、snapshot、remote adapter 或运行适配层。

后续收敛方向是：

- `.spp` 中的 `SalesOrder` 只保留订单合约的业务事实。
- 只有业务人员直接使用的客户号、商品 SKU、产品 ID、订单号等编号才作为业务凭证留在 `.spp`；纯检索号、快照 key、接口请求号和幂等流水下沉到 `.app`。
- `Goods` 应是 `Product` 扮演的销售/上架角色，而不是独立 `Entity`。
- `Inventory` 应是 `Store` 与 `Goods`/`Product` 共同扮演的库存角色，而不是独立 `Entity`。
- 场景入参优先使用 `Role`，避免 `Entity` 或 `Reference` 直接参与场景。
- 外部域引用通过 `Reference` 保持业务语义，通过 `.app` 或运行适配接入真实外部服务或 mock。
- `Reference Customer` 对应的 `queryCustomer` 目标语义应是远程客户域查询；当前 local profile 的对象仓储 remote adapter 只是参考实现，http/seata/tcc/quantum profile 应绑定真实外部客户域 adapter。
