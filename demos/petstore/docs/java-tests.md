# Java测试组合生成场景

测试已移出SPP。原90–95系列的6个SPP文件、测试角色/合约、185个测试服务APP绑定，以及测试专用日志查询映射均已删除。编译器不再识别Verification语法，运行时不再定义VERIFICATION身份。

业务仍由SPP／APP／PHY生成Java。手写Java只在src/test/java中准备输入、调用生成服务、编写断言、注入故障和组织测试流程，不实现价格公式、资格判断、状态转换、退款或库存更新。

## 文件职责

- [PetstoreScenarioTest](../src/test/java/free/servpp/petdemo/PetstoreScenarioTest.java)：28个JUnit测试方法，组合独立场景并断言业务与物理事实。
- [PetstoreTestSupport](../src/test/java/free/servpp/petdemo/PetstoreTestSupport.java)：生成请求/响应的调用支持，以及仅存在于Java测试中的Session输入。生产场景不会接收该夹具。
- [PetstoreRestartProbe](../src/test/java/free/servpp/petdemo/PetstoreRestartProbe.java)：测试专用子JVM入口；先创建并付款，再在另一进程读取原数据库，检查持久化事实。

例如完整交易测试依次调用下单、付款、发货和收货场景；调用顺序在Java测试中，业务状态更新仍在对应SPP场景的原子服务中。价格边界测试可直接调用生成的quoteOrder原子服务，提供固定输入与独立预期值，不在Java中重写计算公式。

## 覆盖目标

|范围|测试方法|
|---|---|
|生命周期、VIP、取消退款、退货|happyPathExample、vipPricingExample、unpaidCancellationExample、paidCancellationExample、returnRefundExample|
|购物车、多商品及只读报价|multiItemExample、cartAdditionExample、cartRemovalExample、quoteWithoutCommitExample|
|资格及作用域拒绝|insufficientFundsExample、shippedCancellationRejectedExample、duplicateCustomerExample、profileValidationScopeExample|
|库存与数量边界|oversellExample、multiItemAtomicRejectionExample、emptyCartExample、fractionalQuantityExample|
|后续交易保持|laterOrderPreservedExample|
|防重及身份冲突的当前行为|idempotencyExample、requestCollisionExample|
|回滚、重试与未知提交结果|rollbackRetryExample、paymentRollbackRetryExample、uncertainCommitQueryExample|
|并发与物理量子证据|concurrentCheckoutExample、quantumLedgerExample|
|数学边界与客户端输入隔离|pricingBoundaryExample、clientPriceIgnoredExample|
|独立JVM持久化重启|persistenceSetupExample，内部执行setup与resume两个进程|

并发测试由Java CyclicBarrier同时启动两个下单调用，不在业务场景中放置测试同步服务。故障注入使用通用运行时测试工具；量子证据直接通过测试JDBC读取物理日志及当前值，不再为测试增加SPP查询服务或数据模型。进程重启测试保留持久化量子证据，不在退出时清空存储。

各测试使用独立H2内存数据库；重启测试使用独立临时文件数据库。测试不会操作网页的target/petstore数据库，不注册测试服务，不打包到生产应用JAR。

## 构建与执行

只生成并编译业务及测试，不运行测试：

```bash
mvn -pl :petstore-demo -am test-compile -DskipTests
```

以下命令在用户需要回归时才执行：

```bash
./demos/petstore/run-demo.sh examples
./demos/petstore/run-demo.sh examples happyPathExample concurrentCheckoutExample
```

examples只是脚本保留的快捷名称，实际执行JUnit测试，不再运行APP examples。JUnit报告位于target/surefire-reports。其他项目已有的APP examples能力不在本次迁移中删除。

本轮只检查生成、编译及生产目录隔离，不执行测试。旧版APP验收PASS不能证明这些Java测试已通过。事务、校验与计算分离、防重和平台版本已经迁移；当前输入已按明确参与者、独立合约及集合同步。测试夹具中的 customerId/orderId 等变量只是 Java 测试标签，映射到业务会员号/订单号，不进入 SPP。生成源码及测试编译不证明运行行为。

多域夹具安装生成application部署清单，并组织真实客户/产品启动服务；没有生产Mock。库存输入是按商品关系定位的StockLine[]，统计只存在测试断言辅助。fractionalQuantityExample改为核对APP/PHY拒绝非整数JSON输入，避免静默截断；它不是SPP浮点数量资格。量子证据按商品身份读取，不再验证库存汇总状态。三份源码已编译，测试未执行。

新增三项测试源码：预约成功、预占拒绝后保留受理合约及阻止盲目重放、付款不改变买家的普通修订标记。付款故障注入移到payOrderFunds；未知提交测试现在核对恢复状态及业务查询，不承诺自动恢复原回执。通用仓储另有过期/缺失修订基线拒绝测试。这些测试只编译，未执行。

当前Java业务验收通过RemoteServiceIngress模拟外部系统请求；uiDuplicateGuardExample单独模拟界面连续点击。两者均调用生成场景，SPP没有测试入口。请求机制见[幂等与防重规范](../../../book/references/app-call-idempotency-and-duplicate-guard.md)。本轮仅编译，未执行这些测试。
