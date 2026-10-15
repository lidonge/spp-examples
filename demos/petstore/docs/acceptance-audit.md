# Petstore 验收记录

2026-10-09，独立子项目petstore-demo，业务/数据/验收只由SPP、APP、PHY描述，网页为薄展示与请求层。

本记录描述独立场景重构之前的版本。本轮源码重构按用户要求不运行回归，以下PASS不证明重构后的运行行为。

## 构建与自动验收

已执行`mvn -pl :petstore-demo -am clean verify`，从空target生成并编译全部项目Java。随后完成公共事务限制的回归与最终源业务验证：

- `mvn -pl :petstore-demo -am verify`：956项公共测试通过（lang307、appframe544、generator105），28个APP入口通过；日志`/tmp/spp-petstore-completion-verify.log`，10:43:58完成。
- 最后补充源业务的请求身份校验后，执行`mvn -pl :petstore-demo -am verify -DskipTests`：28个APP入口重新全部通过；公共代码未改动，故不重复运行公共测试。日志`/tmp/spp-petstore-final-business-verification.log`，10:45:39完成。
- demo源中手写Java为0，target/generated-sources下806个Java文件全部由生成链路产生。

30份JSON及30份Markdown位于target/spp-examples/evidence，全部PASS。重启组额外导出resume与父组证据，故文件数高于28个根入口。

|业务/保障|入口|已查询的证据|
|---|---|---|
|完整成交与履约|happyPathExample|2袋主粮67.80；付款后钱包4932.20/收入67.80；最终可售38/售出2、已收货|
|VIP公式|vipPricingExample|119.60−11.96+0=107.64|
|多商品|multiItemExample|两行72.15+8=80.15；可售37/预占3|
|取消/退款/退货|unpaidCancellationExample、paidCancellationExample、returnRefundExample|库存还原40，钱包5000/收入0；原订单保留|
|后续交易保留|laterOrderPreservedExample|第一笔取消后第二笔仍待付款，39可售/1预占|
|业务校验|oversell/empty/fractional/insufficientFunds/shippedCancellation/duplicateCustomer/profileValidationScope等|拒绝对应输入与状态；失败作用域不修改已存事实|
|报价只读/购物车操作|quoteWithoutCommitExample、cartRemovalExample|报价不生成订单或库存预占；移除后空车|
|业务幂等|idempotencyExample、requestCollisionExample|重复付款不再扣款；同编号不同事实拒绝|
|多行原子拒绝|multiItemAtomicRejectionExample|先一行可售、后一行缺货，库存和订单都不成交|
|真实并发|concurrentCheckoutExample|屏障让两路同时尝试购买7件，仅一路成功；33可售/7预占|
|写入中途失败|rollbackRetryExample|insertOrder之后故障，订单/库存回滚，原编号可重试|
|资金中途失败|paymentRollbackRetryExample|金额转移后saveMerchant故障；钱包/商店/订单回到付款前，结果ROLLED_BACK，再次付款成功|
|未知提交结果|uncertainCommitQueryExample|commitAfter模拟确认丢失，结果UNKNOWN；查询实际回执和38/2库存，重试返回原回执|
|真实量子存储|quantumLedgerExample|3库存+2金额日志及5当前值；日志差额和0，量子值与业务记录一致|
|独立进程持久化|persistenceSetupExample→persistenceResumeExample|两个独立JVM、空参与者；第二阶段读取38/2库存与4932.20/67.80金额|

## 中文网页

公共GeneratedWebServer实际运行，APP只暴露3个场景并调用1个源启动场景。无手写demo启动类或Controller业务实现。

Chrome/Playwright实际点击注册、商品/购物车、报价、下单、付款、重放、发货、收货、退货及退款：PASS，页面错误0，390px手机宽度无横向溢出。证据target/ui-evidence/browser.json、desktop.png、mobile.png；技术检查脚本本次放在临时目录，不是业务实现。源业务可通过上述APP入口和网页重新验证。

## 补充边界与兼容回归

pricingBoundaryExample独立验证普通满额100、未满额99.99、VIP折后满额及12.345舍入四组输入/预期；clientPriceIgnoredExample确认伪造客户端价格和金额不影响持久化目录价；cartAdditionExample验证重复加入商品累加数量。取消与退货断言最终状态；缺少requestId在源校验阶段拒绝，尚未进入物理事务，结果为UNREPORTED。

公共测试验证同步本地串行子场景继承AT/QUANTUM边界，拒绝不兼容模式、TCC隐式继承及事务内跨线程子组；Saga已成交节点不会被当作量子事务技术撤销。

银行兼容执行`mvn -pl :xbod-deposit-demo -am verify -DskipTests`，86个APP入口全部通过，包括5组重启验证；日志`/tmp/spp-petstore-bank-regression.log`，10:34:46完成，耗时17分。该命令跳过公共单元测试，公共测试由上述Petstore构建覆盖。

## 公开边界

本地H2同库、单门店库存簿锁、演示钱包。没有生产登录认证或实际支付机构，没有执行多资源Saga/TCC部署；实体多角色take映射也不是此路径的执行证据。原始银行业务模块保持不变，不把宠物商店测试冒充银行测试。

## 本轮参与者驱动迁移的证据边界

当前源码已迁移到Buyer/Merchant角色、原地查询、无业务返回、默认角色名、隐式绑定、identify、check词法范围、显式撤销、量子约束和复合计算。只进行源生成与生产/测试编译，未执行回归。上面的历史用例与统计对应旧建模，不能作为当前源码通过测试的证明。当前编译证据见[实施路径](implementation-path.md)。

## 2026-10-10 四域模型与bounds编译记录

本轮完成customer/product/inventory/petshop源码、角色/整数库存、真实本地绑定、常量国际化和调用处bounds。隔离旧生成物后`test-compile -DskipTests`成功，781份生产Java和3份测试源码；日志`/tmp/spp-petstore-final-four-domain-build.log`。只编译和静态审查，未运行测试、服务或浏览器，未操作旧数据库。此前PASS记录全部是历史模型证据，不能当作当前运行验收。

## 2026-10-10 自动事务读取与量子域约定

移除lockStock及APP显式for update，addCartItem资格查询移至事务外。生成普通Cart锁定元数据、资料更新Buyer普通写保护、付款Buyer/Merchant量子变化免普通读锁、库存findStock免普通读锁，并传递跨域投影意图。旧产物隔离后773份生产Java及3份测试源码编译成功，日志`/tmp/spp-automatic-transaction-reads-final-build.log`。静态检查和网页脚本语法通过；没有执行回归、服务或修改数据库。逻辑量子域与APP选择数据库/TCC/专用实现写入设计，不宣称所有物理策略或存储拆分已完成运行验收。

量子边界成交控制增补已重新生成并通过 `mvn -pl :petstore-demo -am test-compile -DskipTests`：773份生产Java及3份测试源码，日志 `/tmp/spp-provider-quantum-bounds-final-build.log`。静态核对确认调用处为getQuantumBounds元数据，无调用后读取成交值的补查；JDBC写入含上下限条件，跨域提供方投影传递范围。未执行测试或数据库操作，SQL运行、并发及越界共同撤销仍待运行验收。

全场景边界审查已通过生成及 `mvn -pl :petstore-demo -am test-compile -DskipTests`：785份生产Java、3份测试源码。日志 `/tmp/spp-minimal-scenario-boundaries-build.log`。静态核对事前查询位置、订单重新保护、量子读取元数据和bounds保留。未运行回归。默认乐观保障已记录为设计方向，其原子读取及自动生成仍属待实现能力。

## 本轮事务演进：编译及静态证据

默认普通快照修订保护、跨域基线、普通/量子事实分离、场景防重边界、预约顺序事务与付款嵌套REQUIRED已经落入源码。当前30场景（22变更、8只读），所有场景普通查询在源事务外，事务内条件写入；仅量子变化的角色不调用普通保存。

`mvn -pl :petstore-demo -am test-compile -DskipTests` BUILD SUCCESS，日志 `/tmp/spp-transaction-evolution-final-build.log`：837份Petstore生产Java、3份测试源码（31个测试方法），appframe的49份测试源码也编译。静态审查记录 `/tmp/spp-transaction-evolution-static.txt`；网页 `node --check` 与 `git diff --check` 通过。未执行测试、服务、数据库、故障、并发或重启验证，没有提交或上传。

预约拒绝后的已受理持久化、嵌套付款撤销、量子成交不推进普通版本及过期基线拒绝均有测试源码，但不能据编译宣称运行通过。旧数据库没有自动迁移；请求登记与业务提交分离后，未知/部分提交需要技术恢复协调，目前不支持自动恢复原回执。
