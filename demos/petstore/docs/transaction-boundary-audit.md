# Petstore 全场景事务边界审查

> 2026-10-11 事务及存储规则更新：以下此前的共同提交、自动扮演者保存及 CustomerSubject 描述属于历史设计；当前规则见[实施约定](../../../book/references/transaction-storage-v1.md)。当前 APP 选择 AT 普通更新，量子先独立成交，不同模式通过 Saga 恢复，REQUIRED 不改变这一点。Person/Product 由原域显式维护。

当前四域30个场景：22个变更、8个只读。普通查询、校验和可提前完成的计算在事务外；APP缺省使用查询修订基线做原子条件更新。写事务聚焦必须共同提交的变化，量子服务在内部保障成交值与调用处bounds。

## 缩小规则

普通事实和修订标记一次读取，固定参与者及跨域投影传递基线。普通更新比较其查询基线，不在事务内重读、重验。纯准入角色不参与普通写入比较；量子变化不推进普通修订标记。新增记录由唯一约束保护。独立查询可并行，有依赖的补全保持串行；check留在主block，失败结束场景。

## 逐场景结果

|域/场景|事务外查询、校验、计算|事务内提交|
|---|---|---|
|petshop.initializeStore|主体及目录补全、开设事实|商品、库存、商家共同开立|
|petshop.registerShopCustomer|准入、注册角色、购物车和回执准备|客户域登记主体，销售域买家、购物车及回执共同开立|
|petshop.updateShopCustomer|买家和客户域主体查询，拟值计算及输入校验|两域普通事实条件更新与回执|
|petshop.addCartItem|买家与商品查询链并行，购物车查询、校验及加购计算|购物车条件更新与回执|
|petshop.setCartQuantity|买家与商品查询链并行，购物车查询及数量计算|购物车条件更新与回执|
|petshop.removeCartItem|买家及购物车查询、移除计算|购物车条件更新与回执|
|petshop.clearShopCart|买家、购物车查询和清空计算，展示默认参与者名|购物车条件更新与回执|
|petshop.placeShopOrder|买家/目录并行，购物车查询、报价、库存范围和资格、订单准备|订单插入、库存预占、购物车条件更新及回执；回执需取得插入时分配的订单号后补全|
|petshop.payShopOrder|买家/商家并行，订单查询、资格与付款计算、回执准备|嵌套REQUIRED资金结算加入外层，订单条件更新与回执共同提交|
|petshop.shipShopOrder|买家/订单并行、库存查询、发货校验和计算|库存预占转出库、订单条件更新、回执|
|petshop.deliverShopOrder|买家及订单查询、收货校验和计算|订单条件更新与回执|
|petshop.cancelUnpaidShopOrder|买家/订单并行、库存查询、取消校验和计算|释放预占、订单条件更新与回执|
|petshop.cancelPaidShopOrder|买家/商家/订单并行、库存查询、取消及退款计算|释放预占、退款、订单条件更新与回执|
|petshop.requestShopReturn|买家及订单查询、理由和资格校验、申请计算|订单条件更新与回执|
|petshop.approveShopReturn|买家/商家/订单并行、库存查询、退货校验及退款计算|库存退回、退款、订单条件更新与回执|
|petshop.reserveShopPet|买家/商品并行及申请校验；阶段一后准备并查询库存|事务一提交受理合约；事务二预占库存并条件更新合约；恢复后 fail 用事务三保存拒绝状态和原因，保留阶段一|
|petshop.previewShopOrder|查询、校验和报价|无写事务|
|petshop.browseShopProducts|目录补全、国际化、筛选|无写事务|
|petshop.readShopCustomer|买家及主体查询|无写事务|
|petshop.readShopCart|购物车查询|无写事务|
|petshop.readShopOrders|订单集合查询|无写事务|
|petshop.readShopInventory|商品范围与库存查询|无写事务|
|petshop.readShopMerchant|商家查询|无写事务|
|petshop.readShopReservation|预约合约查询|无写事务|
|customer.registerSubject|输入、是否存在、登记合约准备|主体插入，重复由唯一约束拒绝|
|customer.initializeCustomerDomain|开设事实、是否存在、输入校验|首次主体插入|
|customer.updateSubjectProfile|主体查询、拟值计算和事实校验|主体条件更新|
|product.initializeProductDomain|目录查询、首次目录计算|首次目录集合插入|
|product.reviseProduct|产品查询、修订计算和事实校验|产品条件更新|
|inventory.openInventory|库存初值及合约准备|库存角色和量子初值共同开立|

## 为什么不再重读订单

订单、库存范围及业务判断基于同一份事前订单事实，提交时比较这份事实的修订标记。若订单被其他交易改变，本次条件更新拒绝，量子变化及回执随绑定事务撤销。重新查询订单但继续使用旧库存范围和旧计算结果会混用事实，不能替代该保障。不存在“版本变了但依然按旧校验更新成功”的默认路径。

购物车与实际跨域资料更新也采用同样规则。准入买家后续停用不重新否决已经开始更新的在途交易；量子金额/库存始终由成交内部的权威基线和bounds保障。

## 顺序、嵌套及请求协调

预约合约第一阶段已受理，第二阶段库存不足时仍可凭预约号查询原申请，fail 保存 REJECTED 与 INSUFFICIENT_STOCK；不撤销已经受理的申请。付款内层REQUIRED不是独立提交，订单或回执失败会撤销资金。原子服务不互相调用，场景不组合场景。

JDBC防重登记与结果保存使用短技术事务，不包住场景。已发生独立提交或结果不确定的失败保留恢复状态，不能自动重放整个场景；自动恢复协调器尚未实现。

## 与传统方案比较及验证范围

Java也能实现相同事务保障，但常依赖手写版本判断与方法级事务。SPP显示准入、并行依赖和共同/分阶段提交范围；APP统一管理修订基线，PHY实现条件更新与量子成交。代价是跨域基线、权威事实组合和恢复协议必须由框架正确实现。

本例使用共同JDBC资源/schema/连接；其他量子提供方须实现事实加载与初始化协议。现有数据库没有自动迁移；新快照修订列和量子事实拆分详见[默认乐观保障](../../../book/references/spp-optimistic-participant-facts.md)。本轮只生成、编译及静态审查，不运行回归、服务或数据库。
