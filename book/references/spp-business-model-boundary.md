# SPP 业务模型与技术存储边界

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

实体、角色、合约分别回答：实际存在什么、它在业务中扮演什么、这个场景约定什么。不能把传统 DTO 换一个关键字就当作业务模型。

## 实体与角色

Petstore 用 Product 表示产品（含成本），Goods 表示可售商品（含售价和上架事实）；Person 扮演 Buyer；Person 扮演 Merchant，shopName 等经营属性在 take 中声明为角色特有事实。take 表达属性映射及组合扮演；实体继承仍可表达简单扮演的特殊情况，当前语言未新增实体继承语法。生成器生成实体、角色及双向 mapper；原子执行中的通用框架根据 take 绑定并回填扮演实体。

StockLine、CartLine、OrderLine和Cart是角色。Goods扮演库存/选购/成交明细，Buyer扮演Cart，整体映射保留原参与者关系：

```spp
take Goods as StockLine { Goods goods = Goods; }
take Buyer as Cart { Buyer buyer = Buyer; }
```

Receipt是实际办理凭证实体。没有StockBook汇总状态；available/reserved/sold逐商品定义为quantum int，数量为int，汇总按需计算。角色并非持久化记录换个关键字，必须有实际业务角色关系。

本例展示简单实体/角色扮演、角色特有事实及整体参与者映射；复杂多实体组合为语言能力，但不在本例演示。简单角色可以与实体继承概念兼容，当前没有新增继承语法。take映射不自动替代实体仓储生命周期，也不承诺跨进程多个角色长期同步。

## 合约必须有明确场景

每份 Contract 对应明确业务场景，表达当事人与业务约定。ShopOrder 是下单合约，直接包含 Buyer、商品明细、成交金额和预占数量。付款、发货、退货等场景引用原订单合约是使用业务参与者，并非调用下单场景。

完整对应表见 [Petstore 场景设计](../../demos/petstore/docs/scenario-design.md)。申请退货直接进入 requestShopReturn(Buyer, ShopOrder, ReturnRequestAgreement)，申请理由属于退货申请合约；不由 ShopCommand 的动作字符串路由。

不为结果、集合、中间计算另建 Contract。库存预占归属订单，出库数量归属发货约定，释放数量归属取消约定，付款和退款金额归属相应约定。Receipt 是凭证实体。查询直接补全入口及入口集合；没有 OperationOutcome、ProductCatalogue、OrdersProjection、InventoryMovement、MoneyMovement、PurchaseAgreement 或 QuotationAgreement 包装。

## 业务标识和平台标识

SPP 不声明技术主键、外键、请求键、并发版本或无需求依据的 storeId。商品 SKU、会员账户号、订单凭证号、回执号有直接业务用途，可保留并声明用途：

```spp
Role Buyer { business("会员账户号，供客户识别及订单归属核对") String membershipNumber; }
Contract ShopOrder { business("面向买家的订单凭证号") String orderNumber; Buyer buyer; }
```

编译器拒绝未标明业务含义的 id、*Id/*ID、version、rowKey、rowId、requestId、recordId 等明显技术字段；business 的说明不能为空。这是可检查的命名规则，不是自然语言业务证明。改名或虚构说明不能使技术字段合法，仍须需求审查。

APP 可以声明参与者关系的存储投影及模型外列：

```app
tables contracts {
    table SHOP_ORDERS(ShopOrder) {
        primarykey(ShopOrder.orderNumber);
        foreignkey(ShopOrder.buyer) references Buyer;
        notnull long version;
    }
}
```

SPP 的 Buyer 是完整参与者关系；APP 将其会员号展开为外键列。平台 version 不进入生成业务模型或请求 JSON。StockLine按Goods业务凭证定位，Merchant的平台主键由APP定义，单商家定位用singleton，不向 SPP 塞入门店分区号。

APP 的 platform(index, Type.column) 定位模型外元数据；compareVersion(platform(...)) advanceVersion 采用查询基线进行原子版本保护。成功查询或插入记录平台身份，量子账簿据此定位，缺少身份不能悄悄选择默认对象。撤销同时恢复内部基线。APP 的 number(argument(...), "ORDER") 为实际业务凭证分配编号，不是技术请求防重键。

## 参与者稳定性与集合

入口只能是参与者，查询原地补全，服务不返回业务值。保存只接收当前参与者，技术快照不由业务另传 before/changed。参与者关系比较使用 APP 声明的直接业务身份，例如 Buyer.membershipNumber；sameFacts 仍比较全部业务事实。

场景可声明 Goods[] products、ShopOrder[] orders。Java 服务接口为这些一维参与者集合生成可变 List，查询和计算更新集合内容，保留入口容器；直接 Java 调用须提供可变集合。标量入口禁止重新赋值。原子服务可构造明细数组，再更新所属参与者属性。集合查询无匹配得到空集；以自身业务身份逐项查询的一维集合也支持optional及锁定，并按身份排序锁定；广义筛选集合查询不支持optional或锁定。

## 分层与验证

SPP 定义参与者、业务公式、资格、成交状态及 transaction 一致性边界；APP 定义部署、仓储投影、平台身份/版本、防重、接口和编号分配；PHY 定义数值表示与物理资源。普通 transaction 默认 REQUIRED；SPP 不选择 quantum、AT、Saga。量子属性仍显式声明，量子服务定义加减，调用处bounds选择上下限，生成代码传递范围，量子成交实现负责约束并在越界时撤销绑定事务；APP/PHY保障实现。

Java/ORM 也可分离领域关系与外键、采用角色和乐观锁。SPP 的收益是把这些边界及业务范围写成可核对的声明；代价是生成器和运行时承担映射、集合与技术元数据管理，且业务模型仍需要人工判断。

本次验证只生成并编译生产及测试源码，不运行回归。旧数据库的列、键和聚合快照与新模型不兼容；未自动迁移或清除演示数据库。重新运行时使用独立数据库，已有数据升级须另定方案。编译通过不证明并发、故障恢复或运行中实体同步已通过验收。

## 独立域与集中部署

customer拥有Person，product拥有Product，inventory拥有StockLine角色及逐商品库存，petshop拥有销售角色和订单合约。消费方Reference明确来源，可引用提供方实体、角色或合约。APP部署四域同JVM，通过域限定本地服务容器协作；PHY共同资源/数据库/schema/事务连接约定保障共同提交意图。不Mock、不跨域直接读表，场景不调用场景。

实现和生成编译已完成，未运行回归；详见[域边界](../../demos/petstore/docs/domain-boundaries.md)及[编译证据](../../demos/petstore/docs/implementation-path.md)。

量子属性业务上统一归逻辑量子域，真实一致性机制由APP配置、PHY资源实现；不是强制独立物理服务。事务内读取和混合参与者保护见[事务读取规则](spp-transaction-reads.md)。
