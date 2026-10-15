# Petstore 场景、合约与事务设计

一个场景表达一个明确业务过程，直接组合查询、校验、计算及更新原子服务。场景不调用场景，不通过 ShopCommand/action 分发业务。生产跨场景交互由前端组织；Java 测试可以组合生成场景。

## 场景与合约对应

|场景|合约|入口中的其他参与者|约定|
|---|---|---|---|
|initializeStore|StoreOpeningAgreement|Goods[]、StockLine[]、Merchant|开设演示门店及初始目录|
|registerShopCustomer|RegistrationAgreement|Buyer、Cart|会员账户开立|
|updateShopCustomer|ProfileAgreement|Buyer|新姓名、联系方式、等级|
|addCartItem|CartAdditionAgreement|Buyer、Cart、Goods|增加商品及数量|
|setCartQuantity|CartQuantityAgreement|Buyer、Cart、Goods|设定选购数量|
|removeCartItem|CartRemovalAgreement|Buyer、Cart、Goods|移除商品选择|
|clearShopCart|CartClearingAgreement|Buyer、Cart|清空选择|
|placeShopOrder|ShopOrder|Buyer、Cart、StockLine[]、Goods选择条件、Goods[]、Receipt|成交商品、金额、地址及库存预占|
|payShopOrder|PaymentAgreement，引用原ShopOrder|Buyer、Merchant|订单全款|
|shipShopOrder|ShipmentAgreement，引用原ShopOrder|Buyer、StockLine[]|出库数量及物流凭证|
|deliverShopOrder|DeliveryAgreement，引用原ShopOrder|Buyer|确认收货|
|cancelUnpaidShopOrder|UnpaidCancellationAgreement，引用原ShopOrder|Buyer、StockLine[]|取消原因及释放数量|
|cancelPaidShopOrder|PaidCancellationAgreement，引用原ShopOrder|Buyer、Merchant、StockLine[]|取消原因、释放数量及退款|
|requestShopReturn|ReturnRequestAgreement，引用原ShopOrder|Buyer|退货原因及申请|
|approveShopReturn|ReturnRefundAgreement，引用原ShopOrder|Buyer、Merchant、StockLine[]|确认商品退回及退款|
|reserveShopPet|PetReservationAgreement|Buyer、Goods、StockLine[]|受理后尝试预占，预占失败保留申请|

上表列出销售域的开设/变更合约；客户、产品、库存提供方还有各自开立/修订场景和合约。原订单也是后续场景的参与者，不代表复用或调用下单场景。量子变化归属实际场景合约，不另建 InventoryMovement/MoneyMovement。回执是凭证实体；合约中可含本次回执，不能用通用 OperationOutcome 代替业务事实。

其余8个只读场景不另造合约：readShopReservation补全原预约合约；previewShopOrder 补全候选 ShopOrder；browseShopProducts 补全 Goods[]；readShopCustomer、readShopCart、readShopMerchant原地补全标量；readShopInventory补全StockLine[]；readShopOrders 补全 ShopOrder[]。无业务返回或集合包装合约。

## 申请退货示例

```spp
Scenario serial requestShopReturn(Buyer, ShopOrder, ReturnRequestAgreement) {
    checkReturnRequestAgreementInput;
    initializeReturnRequestAgreement;
    findBuyer; identify(Buyer);
    findShopOrder; identify(ShopOrder);
    checkOrderOwner;
    checkReturnRequest;
    prepareReturnRequest;
    prepareReturnRequestReceipt;
    transaction {
        updateShopOrder;
        insertReceipt(ReturnRequestAgreement.Receipt);
    }
}
```

入口 Buyer 携带会员号，ShopOrder 携带业务订单号，ReturnRequestAgreement 携带理由。初始化原子服务关联买家与原订单；查询补全同一入口实例。场景显式检查订单归属及已收货资格，再修改状态并保存。计算没有隐藏 check，也没有通用指令解释。

## 事务与校验顺序

16个销售域变更场景都声明 transaction；initializeStore只在商家角色尚未确认时声明初始化事务。报价和读取不写库，无成交事务。普通事务默认 REQUIRED，付款以嵌套REQUIRED明确资金结算加入订单的共同提交边界；特殊传播语义见 [事务边界](../../../book/references/spp-transaction-boundaries.md)。

入口合法性检查可以在事务前执行；需要存储事实的资格检查在查询后、第一次业务写入前显式执行。普通 check 不自动撤销；identify 等需要撤销的检查显式使用 breakTransction。量子调用处bounds约定成交范围，自动检查与绑定事务撤销；不在服务内部写死上下限。SPP 不声明 quantum/AT/Saga 事务模式或异常捕获。

付款仅涉及 Buyer、Merchant、ShopOrder 和付款合约；不查库存/购物车。未付款取消不涉及卖家资金。购物车移除不因商品下架而拒绝。资料变更拟值存于 ProfileAgreement，避免查询补全 Buyer 覆盖拟值。

## 量子服务与物理保障

available/reserved/sold、wallet/cash 为量子属性。预占、出库、释放、退回、付款和退款分别定义量子原子服务，调用处声明bounds成交范围。一个动作可只改变守恒资源中的部分属性，但完整资源仍纳入守恒快照，例如预占改 available/reserved，sold 不变。

APP 自动推导量子资源并声明技术防重，普通CRUD与乐观保护默认生成；PHY在develop中选择共同localJdbc后端、int缺省数量及带精度scale的BigDecimal金额。这描述本例同库的保障实现，不等于 SPP 指定事务模式。库存量子读取不加普通资源锁；多资源强一致、Saga/TCC 和远程实体生命周期不是本例已验收能力。

## 参与者与存储

场景及原子服务只声明实际参与者；默认实例名与显式别名兼容，省略参数按类型及集合维度唯一绑定。场景禁止构造或重新绑定标量参与者。Goods[]/ShopOrder[] 入口生成可变 List，原子查询替换内容而保持容器实例。动态业务明细只由原子服务创建。

保存只接收当前参与者。APP/PHY 记录普通事实与物理修订基线，不传 original/changed，不在合约保存技术 before。Buyer 关系按会员号核对身份，APP 将参与者关系保存为外键投影，SPP 不使用 customerId。技术表键由 APP 定义，CRUD 根据参与者及扮演关系默认生成。

编译器检查参与者、调用限制、未使用告警、构造范围、更新场景的 Contract、技术字段及量子约束；它不能替代业务含义审查。本轮只生成并编译生产与测试，不运行回归。历史验收不证明本次行为；旧数据库不自动升级。

库存服务由inventory域提供，销售场景通过APP绑定同类别原子服务，不调用openInventory场景。registerShopCustomer在自己的transaction中通过客户域原子服务登记主体并开立Buyer，保留一键流程。bounds语法见[量子调用](quantum-caller-limits.md)。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。

## 加购物车的事前查询并发

addCartItem通过parallel同时执行买家查询和商品查询链；findGoods 自动先查商品角色，再通过产品域服务补全产品事实。并行组等待两条查询完成后，在场景主block执行identify和商品可售校验，通过后定位购物车并进入原有写事务。查询不共享同一参与者的写入。

校验保留主block的原因是词法作用域：check失败只结束所在block。把资格校验放进并行分支的serial会缩小控制范围，不能据此保证整个场景停止。当前并行组还没有已约定的全组校验失败控制语义，本例不借调整编排改变失败范围。事前查询可能并发完成，即使其中一个参与者最终未被确认，也不会进入写事务。

传统Java同样可用CompletableFuture组合查询；SPP以parallel/serial直接表达业务依赖，APP/PHY及运行时承担线程调度、查询身份状态共享和技术失败处理。并发组不是跨域事务，资格查询仍在写事务之外。

本轮四域30个场景（22个变更、8个只读）已按可靠乐观基线缩小事务：普通查询、校验与计算在事务前，事务内原子条件写入；只读准入不成为提交条件，量子成交不推进普通修订标记。预约展示两个顺序事务，预占失败保留已受理合约；付款展示嵌套REQUIRED逻辑边界；非LOCAL策略下量子阶段先成交，跨模式失败采用Saga恢复；本轮develop使用LOCAL共同提交量子与普通更新。详见[事务审计](transaction-boundary-audit.md)和[实施计划](transaction-evolution-plan.md)。

## 一个场景中的嵌套事务

payShopOrder事前查询、校验和计算，外层条件更新订单并保存回执，内层transaction REQUIRED负责量子资金结算。内层不是独立提交：资金成功后若外层订单/回执失败，资金仍随外层撤销。该嵌套表达资金单元和订单整体的提交关系，不调用其他场景，也不把量子原子服务拆成可互调服务。

顺序事务则有不同含义：第一个事务结束后已提交，第二个事务失败不能以技术回滚撤销第一阶段。应采用明确允许保留受理事实的业务，例如预约申请受理后尝试库存预占，而不能将现有退款与订单状态任意拆分。reserveShopPet已实现该预约样例：第一次事务插入已受理合约，第二次事务预占库存并更新为已预占，失败保留已受理合约。

## 枚举代码与显示文案

业务枚举值使用英文代码，与枚举成员名称一致，例如 `Enum MemberTier { NORMAL("NORMAL"), VIP("VIP") }`。订单、回执、预约状态同样使用英文值；接口、存储和Java测试输入/断言使用代码。中文网页按代码映射中文名称，会员选择提交 NORMAL 或 VIP，显示普通或 VIP。中文不参与业务状态判断。既有中文值数据需迁移或使用新演示数据库；本轮不迁移现有数据。
