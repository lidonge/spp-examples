# 完整 Petstore SPP 演示

APP 技术服务样例对商店域所有场景与原子服务记录调用和耗时，无需修改 SPP，见[技术服务样例](docs/technical-services.md)。

中文网页与Java自动验收使用同一套生成业务服务：商品目录、客户、购物车、报价与下单、付款、发货收货、取消退款、退货及预约受理/库存预占。业务只在SPP，部署在APP，数字表示与共同事务保障在PHY；业务Java全部生成；Java测试只在src/test/java中组合场景和断言结果。

本轮按独立场景、明确角色参数和业务合约规则重构，见[场景与事务设计](docs/scenario-design.md)。业务源码不使用ShopWork；数据库更新场景有明确Contract参与。生产跨场景组合在前端完成。普通事务默认REQUIRED，REQUIRES_NEW按当前能力矩阵支持，NESTED及未支持组合编译报错；check与calculate分离，防重与普通事实修订保护在APP/PHY，普通更新缺省使用查询基线条件提交。当前已启动完整回归，进展与实际结果见[回归记录](docs/regression-2026-10-11.md)。

## 打开中文网页

仓库根目录：

```bash
./demos/petstore/run-demo.sh web
```

浏览http://127.0.0.1:8086；局域网运行用`SPP_WEB_HOST=0.0.0.0`。已构建时加`SPP_DEMO_SKIP_BUILD=1`。数据库在target/petstore，重启保留；clean清除演示数据。[运行说明](docs/running-demo.md)。

## 验收

```bash
mvn -pl :petstore-demo -am test -Dtest=PetstoreScenarioTest -Dsurefire.failIfNoSpecifiedTests=false
./demos/petstore/run-demo.sh examples happyPathExample quantumLedgerExample
```

32个Java测试方法覆盖完整流程、多商品、拒绝、幂等、并发超卖、事务写入失败、付款回滚、未知提交结果、量子日志及独立JVM重启。测试只编译、未执行；运行时输出JUnit报告。Verification及90–95测试SPP已移除，APP不再绑定测试入口。见[Java验收](docs/java-tests.md)。旧版APP入口与浏览器结果只保留为[历史记录](docs/acceptance-audit.md)。

## 从需求读到源码

- [事务演进实施计划](docs/transaction-evolution-plan.md)、[30场景事务审计](docs/transaction-boundary-audit.md)、[默认乐观保障](../../book/references/spp-optimistic-participant-facts.md)。
- [需求与功能](docs/requirements-and-functions.md)、[实施路径](docs/implementation-path.md)、[能力矩阵](docs/capability-matrix.md)。
- [十分钟演示](docs/demo-walkthrough.md)、[按SPP文件导读](docs/source-guide.md)、[传统Java比较](docs/spp-vs-java.md)、[通用语法缺口](docs/language-gaps.md)。
- [商店域按功能阅读](docs/source-guide.md)：`membership`、`catalogue`、`cart`、`order`、`payment`、`fulfillment`、`returns`、`reservation`；共享定义放在 `shared`。
- [APP绑定与网页暴露](src/main/spp/petshop/petshop.app)、[PHY数字与资源](src/main/spp/petshop/petshop.phy)、[Java场景测试](src/test/java/free/servpp/petdemo/PetstoreScenarioTest.java)。

这是完整本地业务演示：支付使用演示钱包，集中量子库先提交金额/库存，再提交普通记录；跨模式以Saga恢复。网页只展示事实与发起操作，不复制报价、资格和状态规则。逐商品锁竞争的吞吐成本及外部支付/多资源事务边界在对比文档明确说明。

语言规则详见[事务传播](../../book/references/spp-transaction-boundaries.md)、[参与者](../../book/references/spp-scenario-participants.md)、[原子服务](../../book/references/spp-atomic-services.md)、[APP防重与版本](../../book/references/app-request-idempotency.md)。

当前客户域拥有Person、产品域拥有Product，商店引用它们并定义Goods/Buyer/Merchant角色，Merchant在take中新增角色事实。合约对应各域明确的开设和变更场景；订单直接含 Buyer、明细直接含 Goods，不使用通用 ShopCommand/OperationOutcome 或集合包装。平台主键、版本及外键投影仅在 APP，查询集合保持入口容器。详见 [业务模型边界](../../book/references/spp-business-model-boundary.md)。旧数据库没有自动迁移，重新运行应使用独立数据库；此前设计修改阶段没有执行回归或重启网页；当前回归状态见[回归记录](docs/regression-2026-10-11.md)。

## 独立域与集中部署

customer拥有Person，product拥有Product，inventory拥有StockLine角色及逐商品库存，petshop组织销售及订单。Cart/CartLine/OrderLine也是角色，StockBook汇总状态已删除。APP部署四域同JVM并绑定真实原子服务，PHY声明共同数据库/schema/资源及事务连接。一键注册登记主体并开立买家角色。见[域边界](docs/domain-boundaries.md)。

数量缺省为int，金额缺省为带精度和scale的BigDecimal；这些只是物理缺省表示，业务数字语义仍是number。PHY展示精确规格的全局替换及Buyer.wallet局部覆盖。量子服务只写加减，调用者用`bounds { 属性: [下限, 上限]; }`声明范围，null表示该侧不限，由量子成交实现自动控制边界，越界撤销绑定事务。[量子调用语法](docs/quantum-caller-limits.md)。SPP常量及APP/PHY国际化提供中英文商品文案。

此前设计阶段只执行生成、编译和静态检查。当前使用独立测试数据库进行完整回归，量子成交、跨模式反交易、并发和恢复的实际结果见[回归记录](docs/regression-2026-10-11.md)；[实施证据](docs/implementation-path.md)与[传统Java比较](docs/spp-vs-java.md)区分声明能力和实测结果。上述运行命令用于后续验收。

事务查询遵循[自动读保护与逻辑量子域](../../book/references/spp-transaction-reads.md)：普通参与者事务内自动锁定，混合参与者也修改普通属性时锁定；量子变化由配置的实现保障，不需要lockStock服务。

全部28个场景的事务外准入和最小业务一致性范围，见[事务边界审查](docs/transaction-boundary-audit.md)。

本轮新增预约顺序事务和付款嵌套REQUIRED：预约第一阶段已受理，库存不足时仍保留申请；付款内层 REQUIRED 加入量子成交阶段，资金先提交；后续订单失败时按原成交增量反交易。查询/校验/计算在写事务前，条件提交及量子成交在事务内。JDBC场景防重不再隐含包住整个场景；未知或部分提交的请求需查询业务凭证并恢复技术登记，当前没有自动恢复协调器。旧快照数据库需要迁移或使用独立数据库，本轮未改变现有数据库。

当前Java业务验收通过RemoteServiceIngress模拟外部系统请求；uiDuplicateGuardExample单独模拟界面连续点击。两者均调用生成场景，SPP没有测试入口。请求机制见[幂等与防重规范](../../book/references/app-call-idempotency-and-duplicate-guard.md)。本轮仅编译，未执行这些测试。


跨域查询可从 [petshop.app](src/main/spp/petshop/petshop.app) 的 `bind importCatalogue to product.listCatalogue;` 开始看，参数转换由 [外域参与者与 take](src/main/spp/petshop/shared/petshop-01-external-entities.spp) 明确约定。本地非主键筛选直接写 repository；默认主键查询沿 `Cart → Buyer → customer.Person`、`Goods → product.Product` 递归补全。[查询设计与限制](../../book/references/participant-query-binding.md)。

本轮事务模式、角色存储归属及第一版嵌套支持以[事务与存储实施约定](../../book/references/transaction-storage-v1.md)为准。APP 在 `environment develop` 部署四域，并使用 `transactions { mode: LOCAL; resource: shopRecordsResource; }` 选择共同数据库事务；量子与普通更新共同提交。量子属性及服务修改字段从SPP自动推导，不重复罗列APP清单。非LOCAL策略及环境规则见[环境部署与物理缺省配置](../../book/references/deployment-environments-and-physical-defaults.md)。客户域显式维护 Person，产品域显式维护 Product，角色保存不会隐式更新扮演者。

明细角色已拆为独立 APP 表；父记录只存明细身份，SPP 显式调用单表明细服务。订单页展示明细凭证号。旧集合快照需要迁移或新建演示数据库，本轮未修改运行数据库。

## 内置参与者 CRUD

标准查询和增删改无需在 SPP 声明空原子服务，场景直接使用 `findBuyer`、`insertBuyer`、`updateBuyer`、`deleteBuyer` 等约定名称。集合调用也使用类型的原名，如 `insertCartLine(cart.lines)`。APP/PHY 生成对应存储绑定；复杂查询与业务原子服务仍显式定义。详见[参与者内置增删改查](../../book/references/implicit-participant-crud.md)。

跨域登记主体直接写 `insertPerson(customer)`，更新主体直接写 `updatePerson(customer)`；编译器使用 `take Buyer as Person` 自动调用客户域，随后由 `insertBuyer/updateBuyer` 单独维护商店角色。初始化经营者用 `findPerson(merchant)` 查询客户域主体，不另声明代理服务或默认 bind。


所有场景和原子服务优先省略参数实例名与可唯一匹配的调用参数。`Goods` 与 `Goods[]` 是不同参与者类型，入口可以写 `(Goods, Goods[])`，计算直接使用 `Goods[]`；`GoodsArray` 仅是生成Java/API传输时的内部名称。相同完整类型重复出现时才保留显式实例名。SPP、APP、PHY及业务枚举源码不保留解释性注释，业务说明集中在独立文档中。

国际化资源位于 `src/main/resources/i18n/{product,petshop}/{zh-CN,en-US}.properties`，PHY只引用目录。默认构建环境为develop；使用 `-Dspp.environment=环境名` 选择APP部署声明和PHY环境块。testing包含customerService、productService、petstore三应用的远程路由和独立存储配置，量子执行域共置并使用统一量子库。先启动两个提供方，再启动petstore；通过SPP_DOMAIN_RPC_TOKEN提供统一内部调用凭据。启动时检查提供方契约和就绪状态，缺失配置不退回本地调用。构建／启动步骤及尚未运行验证的范围见[环境部署设计](../../book/references/deployment-environments-and-physical-defaults.md)。

新库开户和库存均从零开始。网页中先注册，再独立充值、入库；第三方结算账户及库存供应来源以负余额记录累计净转出，双边量子交易保持守恒。详见 [零开户与守恒交易](docs/conserved-opening-and-transfers.md) 和 [本轮回归](docs/regression-2026-10-12-conserved-transfers.md)。

业务源码按域存放于 `src/main/spp/customer/`、`product/`、`inventory/`、`petshop/`，商店域进一步按业务功能组织场景、合约和服务，域级 APP／PHY 保留在域根目录；详见 [源码阅读指南](docs/source-guide.md)。Maven 源码根目录配置不变，插件递归扫描各域。

## 成交属性快照

订单明细 `OrderLine.name`、`OrderLine.unitPrice` 映射商品属性，在 APP 表中使用 `snapshot(...)` 独立保存；商品名称使用 `current(...)`。商品改名、调价后，旧订单保留成交值，新订单采用新值。[配置与实现说明](../../book/references/role-mapped-storage.md)。`reviseShopGoodsPrice` 展示商品调价，产品改名由产品域 `reviseProduct` 维护。

## 事务内普通更新自动并发

develop 环境在 APP 中开启 `ordinaryUpdates: PARALLEL`。事务执行器先完成量子成交，再并发执行连续、准备完整的普通更新；计算、校验和执行组保留顺序边界。缺省策略仍为 SERIAL，testing 未显式开启。共享 JDBC 连接由原事务持有，工作线程不会独立提交。[执行配置、实现路径与限制](../../book/references/automatic-transaction-update-concurrency.md)。


预约场景现已展示真实的事务失败处置：保留先前受理的申请，框架完成量子恢复，SPP fail 查询事实并保存拒绝原因；系统 ResultInfo 不需入口声明。[完整示例与验收](docs/reservation-failure-handling.md)。
