# 按 SPP 文件阅读 Petstore

> 2026-10-11 事务及存储规则更新：以下此前的共同提交、自动扮演者保存及 CustomerSubject 描述属于历史设计；当前规则见[实施约定](../../../book/references/transaction-storage-v1.md)。当前 APP 选择 AT 普通更新，量子先独立成交，不同模式通过 Saga 恢复，REQUIRED 不改变这一点。Person/Product 由原域显式维护。

先读 [需求](requirements-and-functions.md)、[场景设计](scenario-design.md) 和 [业务模型边界](../../../book/references/spp-business-model-boundary.md)，再沿下单或申请退货场景逐个查看原子服务。

|目录 / 文件|业务范围|阅读重点|
|---|---|---|
|`membership/`|买家开户、资料维护及买家查询|客户域主体维护与商店域角色维护分别调用|
|`catalogue/`|商品浏览、调价、商店开设及入库|商品扮演产品、跨域目录查询与展示常量|
|`cart/`|购物车查询、添加、修改数量、移除及清空|明确参与者、合约及共享校验|
|`order/`|报价、下单、订单查询及取消|成交明细快照、价格计算与库存释放|
|`payment/`|支付、钱包充值|双边量子资金变化及调用处 bounds|
|`fulfillment/`|发货、收货|交付资格及库存预占转售出|
|`returns/`|退货申请与审批退款|独立场景、业务退款及库存回补|
|`reservation/`|预约受理、库存预占及预约查询|两个顺序事务，预占失败保留申请|
|`shared/`|经营者、回执、外域参与者、枚举及常量|跨功能共用的业务定义|
|`petshop.spp`|商店域声明|目录不改变业务域身份|
|`petshop.app`|表、查询实现、部署及网页入口|域级配置统一维护|
|`petshop.phy`|数字表示、数据源及量子存储|物理配置与业务功能分目录相互独立|

每个功能目录同时保存自己的模型与合约、校验、计算、服务声明和场景。原混合文件按完整声明拆分，文件按模型、校验、服务、计算、合约关联和查询命名，数字前缀保留稳定的生成扫描顺序；查找时以功能目录为准。例如 `payment/petshop-10-services.spp` 包含支付资金量子服务。

推荐先看 [申请退货](../src/main/spp/petshop/returns/petshop-scene-requestShopReturn.spp)：Buyer、原订单与申请合约就是业务范围，理由来自申请，资格在场景显式校验，保存处于 transaction 内。然后对比 [付款](../src/main/spp/petshop/payment/petshop-scene-payShopOrder.spp) 和 [下单](../src/main/spp/petshop/order/petshop-scene-placeShopOrder.spp)：付款不带库存/购物车，下单明确声明目录集合、库存、订单及回执。

下单 ShopOrder 自身记录成交和预占，不再套 PurchaseAgreement。报价补全候选订单，不持久化。商品和订单查询直接接收 Goods[]/ShopOrder[]；生成服务采用可变 List，补全内容但保留入口容器。

SPP 中会员号、商品编号、订单号、回执号是有说明的业务凭证；平台主键、版本、防重键只在 APP/PHY。订单直接引用 Buyer，明细直接引用 Goods。状态与钱包等事实可变，不影响按会员号识别同一买家。

Java测试只在 src/test/java 组合生成场景。生产 Java 全部在 target 生成；本轮只编译未执行回归。实体映射、多资源事务、并发及故障恢复的验证范围见 [实施路径](implementation-path.md)，不要用历史 PASS 证明当前模型。

## 独立域与集中部署

先读customer.spp/app/phy和product.spp/app/phy的实体所有权，再看inventory.spp/app/phy的角色库存及服务，最后读petshop各场景。APP把四域部署同JVM；消费原子通过域限定本地绑定调用，事务资源由PHY统一。库存逐商品量子整数，Cart/CartLine/OrderLine均是角色。见[域边界](domain-boundaries.md)。

## 默认参与者实例名的两个完整例子

清空购物车与申请退货同时展示合约字段和场景入口省略实例名，源码仍兼容其他场景的显式别名：

```spp
Contract CartClearingAgreement { Buyer; Cart; Receipt; }
Contract ReturnRequestAgreement { Buyer; ShopOrder; String reason; Receipt; }

Scenario serial clearShopCart(Buyer, Cart, CartClearingAgreement) { /* 见完整源码 */ }
Scenario serial requestShopReturn(Buyer, ShopOrder, ReturnRequestAgreement) { /* 见完整源码 */ }
```

Buyer; 等价于 Buyer Buyer;，合约通过 CartClearingAgreement.Buyer 指代该当事人；场景通过 Buyer 指代入口。基本事实仍需名称，如 String reason;。同类型参与者需区分时使用显式别名；默认名重复时应拒绝，无参数调用有歧义也应拒绝。

[清空购物车](../src/main/spp/petshop/cart/petshop-scene-clearShopCart.spp) 展示 checkBuyerCredential;、findBuyer; 等唯一绑定，以及 identify(Buyer)。[申请退货](../src/main/spp/petshop/returns/petshop-scene-requestShopReturn.spp) 展示 ShopOrder、ReturnRequestAgreement 和 insertReceipt(ReturnRequestAgreement.Receipt)。各原子服务可以保留显式别名，也可采用默认名，绑定不依赖被调用服务的别名。

APP 防重路径、网页请求及 Java 测试输入同步使用默认名称。生成 JSON 的这两个入口为 Buyer/Cart/CartClearingAgreement 和 Buyer/ShopOrder/ReturnRequestAgreement；合约内部默认属性为 Buyer/Cart/Receipt 或 Buyer/ShopOrder/Receipt。业务不是无参与者，只是省略冗余实例别名。只生成与编译，不运行回归。

本轮新增 `product.spp` 定义商品文案常量，`shared/petshop-02-constants.spp` 定义商店常量，`catalogue/petshop-16-catalog-labels.spp` 使用常量计算当前语言的展示事实；APP约定语言，PHY提供英文值。量子库存加减在 `inventory.spp`，资金加减分别位于 `payment/`、`order/` 和 `returns/` 的服务文件，APP只保留资源绑定。详见 [常量与国际化](constants-and-localization.md) 和 [多域接入](local-domain-binding.md)。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。

本轮四域30个场景（22个变更、8个只读）已按可靠乐观基线缩小事务：普通查询、校验与计算在事务前，事务内原子条件写入；只读准入不成为提交条件，量子成交不推进普通修订标记。预约展示两个顺序事务，预占失败保留已受理合约；付款展示嵌套REQUIRED逻辑边界；非LOCAL策略下量子阶段先成交，跨模式失败采用Saga恢复；本轮develop使用LOCAL共同提交量子与普通更新。详见[事务审计](transaction-boundary-audit.md)和[实施计划](transaction-evolution-plan.md)。

预约定义位于[petshop-35-reservation.spp](../src/main/spp/petshop/reservation/petshop-35-reservation.spp)，业务流程位于[petshop-scene-reserveShopPet.spp](../src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp)。前一个文件定义合约、纯计算与校验；后一个文件显式声明两个顺序事务和只读查询。付款源文件展示嵌套REQUIRED，二者的提交含义不能混淆。

## Zero opening and independent transfers

`payment/petshop-00-model.spp` 定义第三方结算账户及充值合约，`inventory.spp` 定义供应来源角色并执行双边入库；`petshop-15-store-opening.spp` 仅准备零事实。`petshop-scene-fundShopWallet.spp` 是独立充值场景，`petshop-scene-receiveShopStock.spp` 是独立入库场景，均在调用处明确 nullable bounds。零开户不隐藏资金赠送，网页/测试通过独立场景组合演示余额及库存。

## 按业务域组织源码

`src/main/spp/` 下四个目录分别对应客户域 `customer/`、产品域 `product/`、库存域 `inventory/` 和商店域 `petshop/`。每个域目录保存本域源码；商店域内进一步按业务功能划分，专用合约和服务与场景放在同一功能目录，公共定义放在 `shared/`，域级 APP、PHY 保留在 `petshop/` 根目录。域身份仍由文件内的 domain 声明确定，目录只组织源码，不改变业务归属和部署关系。

编译插件从原源码根目录递归发现文件，按后缀保持枚举 → SPP → APP/RDB → PHY 的阶段，再以文件名排序、相对路径消除同名排序歧义。现有 YAML、生成 Java 包名及运行入口保持原约定。国际化资源已有 `src/main/resources/i18n/product/` 和 `i18n/petshop/`，继续按业务域与语言组织。

目录整理验收：递归扫描与嵌套 PHY profile 选择测试通过（`/tmp/spp-domain-layout-generator.log`）；develop 从新目录生成并编译 Java，34 项 Petstore 测试通过（`/tmp/spp-domain-layout-petstore.log`）。43 个源码文件逐一与整理前比较，业务内容不变，仅 product/petshop PHY 中的国际化相对路径随目录层次增加调整。

## 成交属性快照

订单明细 `OrderLine.name`、`OrderLine.unitPrice` 映射商品属性，在 APP 表中使用 `snapshot(...)` 独立保存；商品名称使用 `current(...)`。商品改名、调价后，旧订单保留成交值，新订单采用新值。[配置与实现说明](../../../book/references/role-mapped-storage.md)。`reviseShopGoodsPrice` 展示商品调价，产品改名由产品域 `reviseProduct` 维护。


本次功能目录整理已核对全部 173 个顶层声明，内容保持一致；新目录下递归生成及 Java 编译通过。详见[实施路径](implementation-path.md)的目录整理验收。


预约场景增加 fail 业务处置，ResultInfo 为场景内置系统参与者；库存不足与其他预占失败使用不同业务枚举原因。[失败处置导读](reservation-failure-handling.md)。

## APP 技术服务

商店域的 [technical-services.app](../src/main/spp/petshop/technical-services.app) 配置全服务拦截；[technical-services.phy](../src/main/spp/petshop/technical-services.phy) 绑定框架的调用日志与耗时服务。业务 SPP 无需配合，阶段、错误策略及日志示例见[技术服务说明](technical-services.md)。
