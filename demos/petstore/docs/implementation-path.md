# 实施路径与当前证据

> 2026-10-11 事务及存储规则更新：以下此前的共同提交、自动扮演者保存及 CustomerSubject 描述属于历史设计；当前规则见[实施约定](../../../book/references/transaction-storage-v1.md)。当前 APP 选择 AT 普通更新，量子先独立成交，不同模式通过 Saga 恢复，REQUIRED 不改变这一点。Person/Product 由原域显式维护。

需求、业务模型、语言与通用链路、源码与页面已按[多域实施路径](multidomain-implementation.md)完成。四域为customer、product、inventory、petshop；生产业务仅SPP/APP/PHY，三份Java测试只在src/test/java准备输入和组织验收。

## 实施结果

1. Person和Product归独立提供方，消费方显式Reference；Person扮演Buyer/Merchant，take增加角色特有事实，整体扮演映射保留Goods/Buyer关系。
2. Cart、CartLine、OrderLine、StockLine重构为角色；逐商品量子库存及各业务数量缺省为int。删除StockBook汇总及固定40总量校验。
3. APP同JVM部署、域限定本地服务容器及事实投影；提供方查询实例、集合确认、平台身份与版本基线保持稳定。库存按身份补全/保存并记录量子变化。
4. PHY共同数据库/schema、资源和事务连接；一键注册跨客户与销售域更新，场景不调用场景。调用处bounds声明成交范围，提供方实施边界控制，量子服务没有手写范围check或APP业务公式。
5. SPP具名常量及APP/PHY国际化；中文网页、默认参与者输入、Java测试输入和模型比较同步。

## 编译与静态证据

```bash
mvn -pl :petstore-demo -am test-compile -DskipTests
node --check demos/petstore/src/main/resources/web/app.js
git diff --check
```

隔离旧生成源、classes、test-classes后重新生成编译，BUILD SUCCESS：773份生产Java和3份测试源码。日志`/tmp/spp-automatic-transaction-reads-final-build.log`，本轮产物备份`/tmp/spp-automatic-reads-fresh-1qu35z1c`。生成清单含四个域，旧StockBook生成类型已移除，整数输入带精确反序列化约束，调用处生成bounds元数据并传入量子成交实现，库存提供方生成实际加减与逐商品记录。

没有执行测试、服务或浏览器，没有clean或修改现有数据库。编译只能证明类型和调用关系一致。历史运行结果属于旧模型，见[历史记录](acceptance-audit.md)。事务读取与量子边界控制的增补尚未提交。

## 后续运行验收

恢复回归后验收生命周期、集合身份、动态/负/null上下限及逐元素越界、跨域失败共同撤销、并发、防重、恢复和浏览器。旧库没有自动升级；重新运行选择独立数据库，旧数据迁移另定方案。

本例不演示复杂多实体组合、远程调用、跨库强一致、Saga/TCC或生产授权。REQUIRES_NEW/NESTED为通用语法，当前付款场景展示嵌套REQUIRED，其余使用默认REQUIRED；共享校验组复用语法仍待确认。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。

## 量子边界成交责任补充

调用处只生成边界元数据；提供方接收范围并交给选定量子实现。JDBC已有量子值使用带边界条件的UPDATE，首次值使用条件INSERT SELECT；范围不满足则拒绝，并撤销绑定事务。未接入动态边界的内存账簿、TCC、现有远程协议等版本明确拒绝有实际限制的调用，不以外部补查替代成交控制。继续只编译、静态核对，不运行回归。

量子边界成交控制增补已重新生成并通过 `mvn -pl :petstore-demo -am test-compile -DskipTests`：773份生产Java及3份测试源码，日志 `/tmp/spp-provider-quantum-bounds-final-build.log`。静态核对确认调用处为getQuantumBounds元数据，无调用后读取成交值的补查；JDBC写入含上下限条件，跨域提供方投影传递范围。未执行测试或数据库操作，SQL运行、并发及越界共同撤销仍待运行验收。

addCartItem事前买家查询与商品查询链改为parallel，商品链内部serial；校验留在场景主block，保留失败后不进入写事务的控制范围。本轮只生成、编译和静态核对，不执行回归。

事前查询并发调整已通过生成与编译（773份生产Java、3份测试源码），日志 `/tmp/spp-add-cart-parallel-build.log`。生成源码静态核对确认两条查询分支、商品链顺序、主block校验及事务位置；并发运行行为尚未回归。

本轮四域30个场景（22个变更、8个只读）已按可靠乐观基线缩小事务：普通查询、校验与计算在事务前，事务内原子条件写入；只读准入不成为提交条件，量子成交不推进普通修订标记。预约展示两个顺序事务，预占失败保留已受理合约；付款展示嵌套REQUIRED逻辑边界；非LOCAL策略下量子阶段先成交，跨模式失败采用Saga恢复；本轮develop使用LOCAL共同提交量子与普通更新。详见[事务审计](transaction-boundary-audit.md)和[实施计划](transaction-evolution-plan.md)。

先前的保守边界版本编译记录见 `/tmp/spp-minimal-scenario-boundaries-build.log`。本轮已补齐默认原子乐观更新、跨域基线和量子事实组合，旧“重新保护订单”的方案已替换，当前依据事务审计和最后编译记录核对；未运行回归。

事务演进生成与编译完成：`/tmp/spp-transaction-evolution-final-build.log` BUILD SUCCESS，837份生产Java、3份Petstore测试源码，31个测试方法未执行。静态审查30场景边界、顺序/嵌套关系和默认保护声明通过；当前库未迁移，未启动网页或运行测试，未提交上传。

## 远程调用幂等与界面防重分离

APP requests配置统一保留期限 `3 days` 及界面窗口 `5 seconds`，Petstore将idempotency key改为duplicate，移除idempotency business列表；四域技术头增加callerId、requestSerialNumber、callMode。生产场景仍全部由SPP生成，web启动及expose清单保留。框架支持可信远程入口、可替换协议及内存／JDBC完成记录到期；本地执行不缓存。Java验收明确模拟远程系统调用，新增界面防重示例。只做生成编译，不运行测试、不改动现有数据库。详情见[请求机制设计](../../../book/references/app-call-idempotency-and-duplicate-guard.md)。

本轮最终生成编译日志`/tmp/spp-call-protocol-final-build.log`为BUILD SUCCESS，837份生成生产Java和3份Petstore测试源码（32个方法）已编译；新编译器及协议测试源码已编译。静态证据`/tmp/spp-call-protocol-static.txt`核对30个入口、全局期限及窗口覆盖；JavaScript语法和diff空白检查通过。未运行回归、启动服务或操作现有数据库。

### 默认参与者仓储与角色补全

删除标准主键 repository、普通 persist 及库存跨域 bind 的重复配置；标准插入声明改用 atomic insert，标准修改保持 atomic update，编译器还识别 atomic delete。角色查询自动补全外部实体，删除 describeBuyer/describeGoods/describeCatalogue 及场景重复调用。显式 repository 展示非主键筛选，显式 bind 展示跨域定制投影。APP SHOP_MERCHANTS 展示新增技术主键。实现验证仅生成与编译，不运行回归测试、不操作数据库。

生成静态证据：SimpleFindBuyer 根据 APP 推导 membershipNumber 查询并自动调用 customer.findSubject；SimpleFindGoods 推导 sku 查询并自动调用 product.findCatalogProduct，投影不含售价/上架；SimpleInsertProducts 推导 INSERT 与 sku 主键；SimpleInsertMerchant 推导 INSERT 与唯一 Person 扮演者身份，使用 APP merchantRowId 主键列，SHOP_MERCHANTS 的 merchantRowId 不进入 Merchant 业务模型。原 describe 服务生成文件在 clean 后已不存在。最终验证命令为 mvn -pl :petstore-demo -am test-compile -DskipTests，具体运行行为仍未执行回归验证。


### 按参与者身份和扮演关系生成查询

本轮将六个定制跨域 bind 改为只写目标；Goods 显式扮演产品域 CatalogProduct，Buyer/Merchant 显式扮演客户域 CustomerSubject。新增严格的参数身份、集合维度及 take 校验，移除默认字段形状推断；新增编译器测试源码，测试不执行。本域筛选继续直接用 repository，不绑定本域其他查询服务。

默认角色查询递归沿扮演关系读取根实体；根实体主键查询在客户域、产品域生成，根表在各域 APP 定义。生成框架执行本域有表实体的同步保存，外域实体更新仍需显式跨域服务。默认主键查询未命中或缺少主键确认失败，不退回字段筛选。无自身表角色视图可直接沿扮演关系补全。

传统方案需业务代码接收查询结果、创建 DTO、逐字段复制和调用外域接口；SPP 将主键与条件放 APP、参数对应放 take、实现放生成链路。优势是业务参与者与入口实例稳定；约束是必须有明确映射及唯一主键提供方。本轮尚未增加完整 MyBatis SQL/XML 方言，不声称复杂 SQL 语法已实现。数据库根实体旧数据未迁移，运行验收仍待执行。

最终生成与编译：`mvn -pl :petstore-demo -am test-compile -DskipTests`，日志 `/tmp/spp-role-query-final-build.log` 为 BUILD SUCCESS，848份生产Java、3份Petstore测试源码及新增编译器测试源码已编译。静态核对递归查询链、目录扮演适配、集合主键及本域根实体持久化通过；没有执行测试、运行服务或操作数据库，未提交上传。

## 2026-10-11 事务与角色存储实施

普通服务由 APP 选择 AT；源边界生成量子先成交、普通 AT 随后提交的 Saga 阶段。集中库反交易以当前值加负向成交增量，回填参与者。客户资料与产品资料分别显式维护 Person/Product，role 保存不级联。CartLine 由 Buyer+Goods 扮演并以联合身份单独保存；OrderLine 以业务明细凭证号单独保存；父集合只保存身份并通过查询服务补全。

第一版仅集中 localJdbc 开放新执行计划的量子成交及独立嵌套；支持同质 AT 外层 REQUIRES_NEW，NESTED 与其他未支持组合编译错误。外部量子/TCC 的新计划协议留待扩展，业务补偿保留专门讨论项。测试源码已补充，本轮只生成、编译及静态检查。旧快照需要明细数据迁移或新演示库；没有操作现有数据库。

## 标准 CRUD 简化

标准主键查询及单表增删改不再写 SPP 空原子声明。场景直接使用 `find/insert/update/delete + 类型名`，集合保持同名调用；APP 可直接为该内置服务配置事务模式、编号或定制绑定。编译器解析参与者签名并生成通用运行时桥接；复杂查询保留显式定义。规范见[参与者内置 CRUD](../../../book/references/implicit-participant-crud.md)。


### 可读配置、查询条件和表级编号

请求期限采用 `3 days`、`5 seconds` 等带单位配置，兼容旧 ISO 字符串。订单列表改为 `atomic query listOrders(key Buyer, ShopOrder[]);`，自动根据 APP 关联生成仓储查询，网页和测试输入同步改为买家参与者。五类业务编号迁移到所属表的 `auto 属性 prefix "前缀";`，不再按服务参数位置重复声明。相比传统代码，业务入口保持参与者含义，存储定位和编号实现留在 APP/生成链路；自动推导要求唯一关联，复杂及歧义查询仍需显式 APP 实现。


本轮 `mvn -pl :petstore-demo -am clean test-compile -DskipTests` 为 BUILD SUCCESS，日志 `/tmp/spp-table-auto-key-query-final-compile.log`。静态核对五处表级编号生成及 Buyer→订单关联查询通过，JavaScript 语法与 diff 空白检查通过。未执行回归测试、启动服务或操作数据库，运行行为待后续验收。


## 本轮环境、数字与源码展示

- APP按environment选择本进程部署域，develop使用可读LOCAL策略；PHY参数按环境选择，并在启动解析运行时参数后重新核验资源身份。LOCAL共同提交包含量子及普通更新，分布式能力缺失时拒绝配置。
- 量子属性与服务修改属性自动收集，APP不重复清单。XA选择真实Seata XA数据源代理，不能以AT代理冒充XA；外部协调器和真实数据库仍需单独运行验收。
- 模型数字类型仅为缺省表示，PHY展示精确规格全局替换与字段局部覆盖；业务舍入明确，容量限制不改变业务数学规则。
- 文案按语言分文件，PHY引用资源目录；业务常量名保持稳定。
- 默认参与者名和无参数调用统一应用；单个Goods与Goods[]按完整类型匹配，只有重复完整类型保留别名。SPP集合引用保留Goods[]，Java内部才改用合法标识符。
- SPP、APP、PHY与枚举移除源码注释，说明集中在独立文档中；只做源码生成、编译和静态核对，不执行回归测试。

相较传统方案，部署与物理表示变化由APP/PHY集中控制，业务场景不会重复DTO别名、量子字段清单和国际化加载代码。代价是编译器与框架需要核验资源及协议能力；配置可解析不代表分布式链路已经可运行。


### 多进程接入核对

新增testing三应用配置（customerService、productService、petstore），PHY域路由及框架内部原子服务协议；业务参与者原地补全、技术修订证据跨进程传递。消费者启动比对环境、事务协调组、量子身份及原子签名，再检查提供方就绪状态。LOCAL仍在单进程共同提交，testing量子执行域共置以使用默认统一量子库实现。未支持的远程量子成交恢复或事务内锁定查询在编译／运行保护处拒绝，不隐式降级。

启动脚本支持SPP_ENVIRONMENT、应用名、独立端口与统一内部调用凭据。生成、生产及测试源码编译覆盖develop和testing；没有执行JUnit、网页、数据库或外部协调器。运行协议验收在后续用户允许回归时开展，不能把编译通过当作已证实分布式执行。

本轮环境与物理缺省规则已实现，最终静态证据见[需求与实现对应表](../../../book/references/deployment-environments-and-physical-defaults.md#需求与实现证据对应)。develop 使用一个 JVM／共同 LOCAL 提交；testing 生成三个应用及远程默认 CRUD 路由，统一量子库。数字全局替换和局部覆盖、按语言资源、默认参与者已同步演示；源码注释按最新约定移除，说明保留在独立文档中。只完成生成、编译与静态核对，未运行回归、数据库或部署；真实协调器和网络故障验收不在本轮执行范围。

## Zero opening and conserved external transfers

开户只建立零钱包；商品库存、第三方结算账户、库存供应来源均从零开始。充值和入库是独立场景，量子服务执行双边增减，来源调用 bounds 不设下限，接收方要求不小于零。网页提供独立入口；测试组合生成场景获取演示余额/库存，不手写业务 Java。具体需求、实施顺序与传统初始化赋值方案的比较见 [设计说明](conserved-opening-and-transfers.md)。

## APP 普通更新自动并发

APP 新增 `ordinaryUpdates: SERIAL | PARALLEL`，支持域级缺省与部署环境覆盖。生成器为事务边界保留调度策略，为准备完整的普通更新标记并发资格，并追溯跨域本地代理的量子身份及事务模式。执行器在量子阶段之后并发保存，计算/校验/查询及独立事务作为屏障；共享 JDBC 作用域统一提交，失败先汇合再回滚，Saga 成交节点按原规则恢复。自动凭证编号在并发启动前分配。设计、与手写线程池的比较及验收范围见[实现说明](../../../book/references/automatic-transaction-update-concurrency.md)。


## 商店域按业务功能组织源码

目标：浏览一个业务功能时，在同一目录找到参与者模型、业务合约、校验、计算和场景，避免跨功能混合文件。

实施：在 `petshop/` 下按会员、商品、购物车、订单、支付、履约、退货和预约划分目录；混合文件按完整顶层声明拆分，公共定义进入 `shared/`。域声明、APP、PHY 保留在根目录，递归扫描不改变域身份或部署、事务边界。同步更新 README 和源码导读的链接。

验收：逐项比较整理前后的顶层声明内容及数量，验证递归生成和 Java 编译；本次目录调整不修改业务公式、资格条件或事务定义。

与传统按 controller/service/repository 技术层划分相比，这种目录让一个业务动作的定义更集中；共享定义仍需按实际复用程度管理，目录本身不构成服务隔离。

本次验收结果：整理前后的 173 个顶层业务声明逐项比较完全一致；README 与导读中的商店域源码链接全部有效。`mvn -pl :petstore-demo -am compile -DskipTests -Dspp.environment=develop` 从新目录递归生成并编译成功，日志 `/tmp/spp-petshop-functional-layout-build.log`。未运行回归测试。


## 场景失败处理实施

先确定系统内置 ResultInfo/FailureInfo 及合约关联协议，再实现 fail 解析、场景专用参与者检查和恢复后的生成控制。用预约受理→库存预占→失败处置验证独立提交，业务逻辑仅使用 SPP；Java 测试用于调用生成服务、注入技术故障和断言。完整设计及对比见[失败处理](../../../book/references/spp-transaction-failure-handling.md)，业务行为见[预约示例](reservation-failure-handling.md)。

## APP 技术服务与全服务拦截

先完成[需求、语法和实施路径](../../../book/references/app-technical-services.md)，再实现 APP 目标匹配与 PHY 技术类绑定、生成服务元数据及统一运行时拦截。保留场景类型，原子服务的类型调用与统一 execute 入口均被覆盖。Petstore 仅新增 APP/PHY 配置，通用日志实现放框架；[样例](technical-services.md)展示查询、计算、量子更新及场景调用。测试捕获日志，验证幂等重放及故障传播，不在 Java 中实现业务。
