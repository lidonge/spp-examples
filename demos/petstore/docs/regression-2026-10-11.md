# Petstore 回归记录（已完成本轮，含 known issues）

本轮按用户要求执行完整回归，不再沿用此前“仅生成与编译，不运行回归”的限制。业务仍只能使用 SPP、APP、PHY；Java 修改仅涉及通用框架与测试。用户随后要求先提交上传，本次提交保存已完成的修复，完整回归仍在进行中。

本记录保留上一轮结果；新增守恒修正及当前 Goal 的最新证据见 [本轮回归记录](regression-2026-10-12-conserved-transfers.md)。

## 上一轮状态（10 月 12 日）

下文按修复过程保留历史结果，本表表示最新证据。按用户“未决项记录为 known issue 并跳过”的约定，本轮回归已完成；不代表 testing 全部业务链路通过，KI-001 及依赖步骤明确保留。

| 范围 | 最新结果 | 限制 |
| --- | --- | --- |
| lang 全套 | 340/340 通过 | 已有存储身份支持；不新增任意技术主键的初次输入/编号协议 |
| appframe 全套 | 578/578 通过（含技术初始化测试） | 不代表 testing 分库提交已协调 |
| generator 全部 17 类 | 105/105 通过 | 未覆盖尚缺失的分库量子初值协议 |
| Petstore develop 重新生成及业务验收 | 33/33 通过；网页完整流程通过 | 隔离内存库，实际 Chrome 操作及断言 |
| appframe-seata | 当前工具链 20/20 通过 | 三个现存测试类全部执行 |
| testing 三应用启动及商店重启 | 通过 | 全新隔离分库，三个 JVM 实际 readiness=true |
| testing 三应用业务/网页 | 注册失败；后续依赖步骤跳过 | KI-001：新建买家量子初值资源协调；技术启动初始化已修复 |

## 验收范围

1. 使用当前源码构建编译器、运行时、生成器，重新生成并编译 Petstore。
2. 完整执行 lang、appframe、generator、appframe-seata 相关测试；核对旧测试是否符合当前语言约定，保留有效的负向测试。
3. Petstore 业务验收覆盖注册、购物车、报价、下单、付款、履约、取消退款、退货、预约、多事务、并发、故障及重启恢复。
4. develop 集中部署和 testing 三应用部署分别启动，验证中文网页、业务接口、跨域调用、部署兼容检查。
5. 记录实际结果及未验证范围；全部验收通过后才结束 Goal。

## 已取得的证据

首次完整 reactor test 中，lang 333 项：31 failures、92 errors；appframe 562 项：5 failures。生成器、Seata 模块和 Petstore 被上游失败跳过。独立 Petstore 验收最初 32 项全部在创建订单关联索引时失败。

已修复：

- APP 参与者关联索引展开为物理身份列，包含联合身份；新增 H2 索引元数据断言，确认不会误包含同名前缀的兄弟属性。
- 查询补全与请求重放支持公共字段，同时保留已有嵌套参与者实例。两个请求协议测试类共 8 项通过。
- APP transactions 声明不再误访问空注解目标。
- APP scope 中可引用名为 commit 的业务服务；PHY config 可使用 endpoint 键。
- 外键列可空性由引用方配置决定，不继承被引用主键的非空约束；生成目录测试通过。
- 修正两项过时运行时断言：相同物理连接配置共享资源，加入外层事务的条件更新不提前提交。
- 定价边界测试区分合法的两位小数价格与超出 PHY 容量的输入，后者仍要求拒绝。

定向请求协议、资源共享和事务组测试共 19 项通过；关联索引专项测试 1 项通过。此证据不代表全套测试通过。

继续发现：商品 active 非主键查询缺少 APP 仓储实现，已补充；本地 Maven 仓库语言包早于工作区源码，已安装当前工具链并重新生成。更新工具链后，跨域计算绑定出现在生成代码中，商品目录专项验收通过。

后续修复跨域计算集合回填：计算服务可以创建新的集合成员，不能套用仅补全已有成员的查询规则。商品与四条库存的查询专项验收通过。量子服务进一步优先使用参与者查询时已确认的仓储身份，避免把物理外键列名直接当作业务属性路径；新增身份转移与歧义拒绝测试。事务快照补充 Map 处理，避免反射访问 JDK 内部字段；新增循环引用与回滚保留成员实例的测试。后续修复的联合回归已经通过。

## 已通过的联合验收

命令：

```bash
mvn -pl :petstore-demo -am test \
  -Dtest=PetstoreScenarioTest,PetstoreCatalogueTest,ExampleServiceFaultsTest,ArraySnapshotTransactionTest,RepositoryParticipantIdentityTest,ExampleDeclarationTest,BusinessIdempotencyDeclarationTest,ImplicitParticipantCrudTest \
  -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop
```

结果：BUILD SUCCESS。PetstoreScenarioTest **32/32** 通过，PetstoreCatalogueTest **1/1** 通过；本次指定的 lang 测试 **18/18**、appframe 测试 **14/14** 通过。

业务验收覆盖并发库存、报价边界、客户端伪造价格、重复请求与请求碰撞、付款及取消退款、退货、失败回滚后重试、提交结果不确定时的查询、预约先受理再预占的部分提交，以及真实子 JVM 重启恢复。

进一步修复了两个运行时问题：跨域服务名包含域前缀时，故障注入仍须识别无域前缀的 Java 方法；事务提交证据不应把事务外查询或技术请求登记的 JDBC 提交当成业务阶段已提交，否则确定回滚的请求无法重试。验收同时保留了预约部分提交请求不能盲目重放的断言。

履约及取消退款的业务合约在准备回执时补全当前订单事实，避免把入口查询前的空订单事实传给库存服务。修改仍仅在 SPP 中实现业务。

测试夹具也同步到当前约定：请求方流水号技术头、Merchant 的客户域存储身份、四条实际非零量子流水、无参数实例名的请求属性。并发失败可能发生在业务额度检查或量子成交边界，分别允许两种明确拒绝码，仍断言只有一笔订单成交且库存没有超卖。重启验收使用独立 H2 文件库，DB_CLOSE_DELAY=-1 避免每个连接关闭后重复开库，退出 JVM 后再开启另一个 JVM 验证持久化。

## 当前未完成项

提交 `9753ad6c` 后继续执行回归，第三次完整 reactor test（同上命令）结果：lang **338 项，14 failures、0 errors**；appframe **567/567**、appframe-seata **20/20** 通过。generator 和 Petstore 仍因 lang 失败在该 reactor 中跳过。剩余 14 项均位于 APP 语义测试，不能据此宣称编译器全部通过。

本阶段修复了 PHY `timeoutMillis` 配置键与关键字冲突、APP 量子实现被误识别为已有 SPP 实现、自动持久化推断重复登记显式事务模式及资源三个编译器问题，增加 APP/Spp 实现冲突及重复推断专项验证。测试夹具同步到当前参与者语义：查询没有返回值，普通校验与计算分离，废弃 context 与 SPP try/catch/throw 被拒绝，本地事务不要求幂等头。仓储版本快照仍为权威读取来源，直接修改原生镜像表不会覆盖快照；快照不存在时仍验证原生表读取及补全。

相关专项已验证：事务存储 5 项、JDBC 仓储 255 项、查询与量子实现 21 项、异常控制及补偿 8 项通过。生成在源目录的编辑器 ANTLR 临时文件移入 target，Maven 继续使用 target/generated-sources/antlr4。

develop 的 `mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=develop` 已通过；实际启动服务后，`/spp/readiness` 返回 ready=true，部署清单包含 customer/product/inventory/petshop 四域及 LOCAL 模式，商品查询返回四件商品。该启动使用独立内存数据库，未改动既有演示数据库。

Chrome 浏览器验证发现未注册客户查询失败导致整个页面刷新中断，已修复前端仅对参与者未确认结果展示未注册/空购物车，其余错误继续报告。网页完整操作回归通过：新客户注册、加购、报价、下单、付款、发货、收货、退货退款、另一下单后的付款及取消退款、原请求重放、英文目录、预约预占；钱包恢复与订单状态均有断言，pageerror 为空。复用脚本 `src/test/browser/PetstoreBrowserRegression.cjs` 已独立再跑通过。

浏览器回归需要可用 Chrome 和 Playwright 包，例如 `npm install --prefix /tmp/spp-petstore-browser --no-audit --no-fund playwright`，启动独立 demo 后执行：

```bash
NODE_PATH=/tmp/spp-petstore-browser/node_modules \
SPP_DEMO_URL=http://127.0.0.1:18886 \
node demos/petstore/src/test/browser/PetstoreBrowserRegression.cjs
```

`SPP_CHROME_BIN` 可指定 Chrome 路径，截图输出到 `target/browser-regression`。每次使用新会员号；运行会创建真实演示交易，应使用隔离的回归数据库。

10 月 12 日 testing 已完成首次生成与打包，客户和产品服务实际启动时失败，错误为 PERSISTENCE_REPOSITORY_NOT_ENLISTED。已定位两处原因：纯 Saga 事务计划错误走共同执行路径；Saga 局部节点及远程更新入口只开启默认量子资源，而没有开启其普通仓储资源。已增加仓储事务执行 API 及生成接口，局部节点和远程入口按各自仓储资源执行。H2 专项 5 项通过，包括明确禁止普通 Saga 节点访问量子资源、分别提交两个节点及读取前一节点成交事实。正在重新生成 testing，并继续实际部署验证；不能将专项通过视为 testing 已通过。

generator 全测试类独立执行得到 **105 项，9 failures、17 errors**。其中多项旧夹具仍使用返回值、context、SPP 异常及场景调用场景；同时存在生成 Java 编译失败，需要分别修复并回归，不能统一按过时夹具忽略。当前完整 Goal 仍未完成。

testing 后续验证：客户域与产品域独立应用启动成功，ready=true，清单分别为 customer／product、SAGA、UNIFIED_STORE、shopLedger。修复同 JVM 跨域 Saga 提供方写入缺少仓储事务，以及集中部署合并不同 domainRoutes 的错误；同目标不同端点仍拒绝合并，新增两项断言。此后 appframe 全套 **570/570** 通过。

商店应用的下一项实际失败是 **QUANTUM_PROVISION_RESOURCE_NOT_ENLISTED**：新增 Merchant 需要普通角色记录和独立量子库的 cash 初值，普通 Saga 节点已经有仓储事务，但跨库量子初值配置/协调尚不完整。因此 testing 尚不能完成启动，浏览器交易回归未执行通过。失败启动已提交部分普通初始化节点，并报告 COMMITTED_STAGE_COMPENSATION_REQUIRED；后续测试改用另一个隔离商店数据库，保留失败库供分析，没有改动用户的原有数据库。不得把两个数据库的嵌套本地提交宣称为共同原子提交；该初始化及恢复协议仍需完善。

本次启动的 develop/testing 服务均已停止。本批修复按用户要求作为阶段性结果提交上传；Goal 保持进行中，剩余编译器 14 项、生成器 26 项以及 testing 初始化与完整业务/网页验证仍需完成。先前 Petstore 33 项通过是 develop 的业务证据；跨库 Saga 改动后还需重新生成并执行该验收。

第二次完整 reactor test 已结束，命令为 `mvn -fae -pl petstore-demo,appframe-seata -am test -Dspp.environment=develop`，结果为 BUILD FAILURE。lang 共 334 项，其中 28 failures、70 errors；appframe 共 567 项，其中 1 failure、0 errors。generator、appframe-seata 和 Petstore 在本次完整 reactor 中因上游失败跳过，Petstore 的通过证据来自上面的独立联合验收。

仍需修复剩余编译器测试问题，完成 generator 测试及 testing 实际网页与跨域部署验证，再更新最终结果。上述定向通过不代表完整回归通过，当前 Goal 未完成。

## 10 月 12 日数值与计算生成回归

提交 `e6b1be3a` 后继续回归，修复 PHY 对 `java.math.BigDecimal` 等完整类型名的解析：内置数字类型关键词不再使限定类型名解析失败；旧 numeric 配置与新版 numeric replace/override 共用类型名规则。没有改变业务 number 语义或舍入约定。

生成 Java 的两项编译失败来自过时夹具：参与者集合入口现为 List，深拷贝测试仍手写数组入口；check 服务生成 void 方法，数值比较测试却把该方法体放入有返回值的方法。夹具修正后继续编译并执行生成代码，保留集合成员深拷贝、精确算术、溢出与非整除拒绝断言。纯计算短路规则不再调用 require；基本数值数组作为参与者属性传入，仍验证 foreach 的物理转换及 short 溢出拒绝。事实比较测试使用两个明确参与者及 BusinessChecks.evaluate，验证普通数字/自定义适配器下的嵌套值相等、不同值及不同明细拒绝。

专项命令：

```bash
mvn -pl generator -am test \
  -Dtest=NumericPhysicalGenerationTest,BusinessCalculationGenerationTest \
  -Dsurefire.failIfNoSpecifiedTests=false
mvn -pl generator -am test \
  -Dtest=ParticipantFactsGenerationTest \
  -Dsurefire.failIfNoSpecifiedTests=false
mvn -pl generator -am test \
  -Dtest=ExampleCatalogGenerationTest,ScenarioConditionGenerationTest \
  -Dsurefire.failIfNoSpecifiedTests=false
```

分别为 24、2、2 项全部通过。随后独立重跑 generator 的全部 17 个测试类：**105 项，1 failure、16 errors**，剩余失败由 26 项减少为 **17 项**。其余测试仍需逐项处理，未按“旧夹具”统一忽略。又将数值局部覆盖测试改用 `numeric { override Amount.a with long; replace double with java.math.BigDecimal; }`，该类 9 项重新通过，验证限定类型名也适用于新版全局替换规则。

编译器完整命令 `mvn -pl lang -am test` 重新执行：**338 项，14 failures、0 errors**，无新增失败。testing 分库量子初值协调问题、剩余编译器/生成器问题及最终 develop/testing 联合验收仍未完成；本轮没有重新启动演示服务，也没有提交或推送新修改，Goal 保持进行中。

## 10 月 12 日参与者查询与持久化生成回归

远程查询夹具改为 void 方法，单条/集合结果作为明确参与者原地补全；仍验证远程代理标记、无本地 HTTP 入口、缺少适配实现时明确拒绝及远程补偿服务声明。部署目录夹具与现行自动绑定约定一致：显式本地服务和未列举的默认本地服务都会注册，默认本地服务也生成实现类及接口入口。

持久化生成测试改为 `store(Stored stored)` 单参与者更新，移除 SPP 技术 id/version 和两个前后实例；编译、加载并执行真实生成服务，仓储测试替身检查读取修订 token、调用前事实和更新后事实，连续两次调用得到 20→30→40，持久化始终接收同一实例。读取修订保留在框架中。本地更新和删除均执行两次，证明未登记请求去重。本测试验证生成链路与仓储协议，不代替 JDBC 条件提交和事务专项。

PHY 属性生成夹具使用无返回值查询及显式订单合约，7 项全部通过。远程生成 2 项及单参与者持久化 1 项通过。角色扮演迁移样例将 Product/Bundle/Goods/Customer 的字段改为 productCode/bundleCode/sku/membershipNumber 等业务编号，保留组合及替代扮演者计划断言。查询写入拒绝测试移除废弃返回值语法，让其实际到达查询语义校验；输出目录失败测试和量子字段 DDL 排除测试补齐默认 PHY 仓储。量子 DDL 夹具中的主键统一为业务 amountNumber，避免模型字段与 APP 主键不匹配。

生成器全部 17 类再次执行，命令按类名集合选择（避免上游未完成的编译器全套阻断）：**105 项，0 failures、6 errors**，由本轮开始时的 17 项剩余失败降至 **6 项**。剩余为 EmptyCatchGenerationTest、ScenarioCollectionGenerationTest、ScenarioFailureGenerationTest、ScenarioResultGenerationTest，以及 GeneratorUtilValidationTest 中 APP 语义迁移和物理存储分离两项，分别涉及废弃异常/返回值语法及场景调用场景，尚未完成替换和回归。

当前编译器全套最近证据仍为 338 项、14 failures、0 errors；appframe 最近全套证据为 570/570，Seata 为 20/20，本轮没有改动运行时代码或重新执行这两套。testing 的跨库量子初值协调及最终 develop/testing 业务、网页联合验收仍未完成。新修改没有提交或上传，完整 Goal 保持进行中。

## 10 月 12 日生成器全套通过

剩余六项全部处理后，独立重跑 generator 全部 17 个测试类：**105/105 通过，0 failures、0 errors、0 skipped**。本次日志为 `/tmp/spp-regression-generator-all-current.log`；选择全部类名执行，避免 lang 尚未通过的完整语义测试阻断 generator 的独立验证。

查询结果测试改为 `readItem(Item key, Item item)` 和 `readItems(Item key, Item[] items)`，场景通过 `if(item)` 判断确认状态。生成的方法体编译并执行，验证成功时原地补全、未找到时实例仍存在但未确认、集合为空，以及不同分支中的串行组和事务查询执行。集合调用测试改为场景直接调用原子服务，不再场景嵌套调用；传输入口每次生成独立响应，业务 typed 方法返回 void，并继续验证集合的重复深拷贝和故障记录失败不覆盖原故障。

废弃的空 catch 测试改为解析时拒绝业务 try/catch，保留模板渲染错误不写出损坏文件的验证。事务故障测试生成的 SPP 仅含显式 transaction；Java 测试中的技术处理器核对事务回滚已完成，回滚失败以 suppressed 信息附加在原始技术故障上。没有重新引入 SPP 异常控制，也没有通过 Java 测试实现 Petstore 业务补偿。

`transaction { ... } fail { ... }` 目前未出现在现有语法中，补偿语法/协议仍是待讨论项；本次这些技术故障专项不代表业务 fail 块已实现或获得验收。

APP 语义迁移及物理存储目录夹具改用无返回值查询、业务编号及明确参与者目标，并补齐默认仓储。迁移目录也核对由默认 CRUD 推导出的 findProduct 查询计划，保留显式 repository 和远程适配器特例的迁移信息验证。

当前工具链执行 `mvn -pl generator -am install -DskipTests` 成功，继续重新生成 develop Petstore 并进行业务验收。编译器完整回归仍有 14 项失败，testing 跨库量子初值协调及最终部署/网页联合验收仍待完成；生成器全套通过不代表完整 Goal 已完成。

develop 重新生成后的业务验收已完成：

```bash
mvn -pl :petstore-demo -am test \
  -Dtest=PetstoreScenarioTest,PetstoreCatalogueTest \
  -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop
```

结果 BUILD SUCCESS，PetstoreScenarioTest **32/32**、PetstoreCatalogueTest **1/1** 通过。867 个生成 Java 源文件重新编译成功。这是 Saga 仓储作用域修复后的 develop LOCAL 共同提交、业务并发及重启恢复验证；不能据此声称 testing 分库协调已经通过。当前 target 已切回 develop，后续 testing 运行必须显式重新生成所选环境。本轮未启动网页服务器，未提交上传修改，Goal 保持进行中。

## 10 月 12 日远程仓储查询接口修复

发现 `objectRepositoryRemote` 的 PHY 校验仍强制只有一个参数，运行时也仅支持旧返回值或单参与者原地查询。现补齐当前无返回值接口：一个标量键参与者加一个结果参与者，或加一个结果集合。单结果查询原地回填，未找到只改变确认状态；集合查询按组合查询路径读取，补全同一个 List，保留已有成员实例，空结果清空集合并标记未确认。键参与者保持原状。显式结果必须匹配配置的仓储对象类型，且运行时要求声明 void 方法及非空结果参与者；未声明泛型集合成员类型时明确拒绝。旧单参与者查询和运行时兼容返回接口仍保留。

新增 `ObjectRepositoryRemoteParticipantTest` 三项，验证单结果成功/缺失、组合键集合成功/空结果、空结果参与者拒绝。`mvn -pl appframe -am test` 全套 **573/573** 通过（原 570 项加新 3 项），既有远程适配器和 JDBC 仓储测试也全部通过。

进一步补齐普通 repository 的批量校验：集合键仅可原地补全同一个参与者集合，不允许将一组键灌入单个结果参与者或另一个不关联集合；复杂集合条件需要 APP 仓储实现。保留已支持的标准身份批量查询正例及反例验证，没有恢复旧的“所有集合参数均非法”限制。

`mvn -pl lang -am test` 当前全套 **338 项，10 failures、0 errors**，由 14 项减少为 10 项。同步修正 strictAppDdlReplacement 夹具的仓储目标名称，使其实际检查显式仓储路径，而非先因目标参数不存在失败。远程查询形状反例改为“结果类型必须匹配存储对象”，组合查询反例改为缺少结果集合，仍保留拒绝断言。

编译器剩余十项涉及角色复合/扮演者主键推导、量子存储夹具及旧 strictRoleOnly/current-snapshot 迁移检查，需要继续逐项核对。生成器全部 17 类再次执行 **105/105** 通过，日志 `/tmp/spp-regression-generator-query-adapter.log`。testing 跨库量子初值协调和最终 develop/testing 部署、网页验收仍未完成。本轮未重新安装这批查询接口修改或启动网页服务，新修改未提交上传，Goal 保持进行中。

## 10 月 12 日阶段提交：参与者边界与首次校验诊断

按用户“先提交上传”的要求保存当前回归进展，完整回归 Goal 保持进行中。此前各小节的“未提交上传”描述是当时状态，本阶段提交后以本节为准。

Contract 是合法业务参与者，不应由旧 strictRoleOnly 迁移检查判定为非法入口；校验现在允许 Role 和 Contract，仍保留实体/引用迁移诊断及实际存储配置检查。相关测试按当前参与者语义调整，未取消角色复合主键校验。

修复默认绑定推导的错误直到第二次校验才出现的问题：先准备默认绑定，再收集解析/推导错误，并去重相同诊断。新增测试验证第一次校验即可返回错误、重复校验不会追加重复错误；ImplicitParticipantCrudTest 10/10 通过。current-snapshot 测试补充按业务订单编号查询的显式 repository，使测试真实进入其目标严格校验。

最新完整 lang 回归为 **339 项，7 failures、0 errors、0 skipped**，日志 `/tmp/spp-regression-lang-contract-final.log`。剩余涉及无法自动推导的技术主键、角色扮演者/复合主键写入归属以及量子存储物理配置。首次错误收集修复也暴露了此前第一遍校验遗漏的配置问题；不能简单把失败数量变化等同于全部问题已经解决。角色复合键仍需同时修复生成及运行时写入协议，不能仅放宽校验。

最新 generator 全部 17 类 **105/105** 通过，日志 `/tmp/spp-regression-generator-contract-final.log`。运行时最近全套 **573/573** 通过；develop 最近业务验收 **33/33** 通过，但该 develop 验收早于本阶段最终编译器/远程查询接口修改，最终联合验收仍需重跑。testing 跨库量子初值协调尚未解决，分布式业务/网页验收未完成，不宣称独立数据库提交具有共同原子性。

## 10 月 12 日角色复合主键写入归属修复

默认写入规则现在显式保存拥有该表的参与者类型，不再把第一个扮演者的类型作为写入目标。生成代码保留扮演者类型与键路径，以框架元数据 `@performer:Type.property` 传给仓储；SPP 不需要增加技术字段。编译器仅允许符合该角色 APP 主键及 take 映射的跨类型键，其他跨类型写入仍拒绝。默认角色查询也保留 `APP_DDL_ROLE_TAKE_PRIMARY_KEY` 身份来源标记，供运行时解析扮演者身份。

运行时通过 RoleIdentityContext 解析每个扮演者的键，缺失或同类型多个候选时明确拒绝；复合身份按现有编码组合，写入目标始终是角色。带显式修订校验的写入使用读取时保存的角色身份，避免把当前已改变的扮演者身份错误当作原身份。没有改变普通字段键的既有基线校验。

新增两个 JDBC 快照仓储专项：复合键插入只建立角色记录、不建立 Store/Goods 记录，缺失/歧义身份拒绝；带版本守卫的角色可正常更新，改变扮演者身份后更新拒绝且保留原记录。运行时完整 `mvn -pl appframe -am test` **575/575** 通过，日志 `/tmp/spp-regression-role-write-appframe-final.log`。这证明框架身份及 JDBC 快照写入协议，不代替 APP DDL 物理列写入和跨域端到端验收。

为量子角色快照测试补齐其声明的 globalQuantum 的 PHY JDBC 实现，保留量子模型不变。两个复合键编译器用例与该量子角色用例通过，并核对生成的拥有者、扮演者键及默认查询来源。最新 lang 全套 **339 项，4 failures、0 errors**，日志 `/tmp/spp-regression-role-write-lang-final.log`；剩余四项均涉及默认查询无法从模型推导 APP-only 主键（包括部分匹配的角色复合主键），仍需处理真实身份协议与相关夹具，未取消诊断。generator 全部 17 类 **105/105** 通过，日志 `/tmp/spp-regression-role-write-generator-final.log`。

本阶段尚未重新安装工具链、重跑 Petstore develop 或启动 testing/网页服务。testing 跨库量子初值协调及最终联合验收仍未完成。没有提交或推送本阶段修改，Goal 保持进行中。

## 10 月 12 日原生角色表与当前 Petstore 再验收

补充原生 APP DDL 表测试，使用框架生成规则中的两项扮演者键，实际核对 inventory 的 store_name/goods_sku 主键及 available 列。角色记录插入与删除均执行；删除后注入技术故障，确认原生表和快照同时恢复，独立的扮演者审计记录不变。未手写 Petstore 业务 Java。专项 RepositoryWriteSessionTest **15/15** 通过，完整 appframe **576/576** 通过，日志 `/tmp/spp-regression-role-write-native-fixed.log` 与 `/tmp/spp-regression-role-write-native-appframe-all.log`。首次测试编译时引用了不存在的测试仓储 getter，已改为使用相同数据源建立 JDBC 仓储并重新验证。

当前工具链 `mvn -pl generator -am install -DskipTests` 成功。随后重新生成并编译 develop Petstore，执行 PetstoreScenarioTest 和 PetstoreCatalogueTest：**33/33** 通过，BUILD SUCCESS，日志 `/tmp/spp-regression-role-write-petstore-develop.log`。这是最新角色身份及远程查询接口修改后的 develop 证据；没有把旧 target 或此前安装包的结果当作当前验证。

编译器四项默认技术主键查询问题、testing 分库量子初值协调以及最终网页/Seata 联合验证仍未完成。分库初始化涉及普通记录与量子初值两个资源，其恢复协议不能通过嵌套两次本地数据库提交替代。新修改未提交上传，Goal 继续进行。

## 10 月 12 日当前网页与 Seata 最终回归

用已重新生成的 develop target 和当前 appframe 类启动独立内存库 `petstore-final-browser`，仅监听 127.0.0.1:18886，readiness 实际返回 ready=true。执行已纳入仓库的 PetstoreBrowserRegression.cjs，进程退出 0；注册、加购、报价、下单、付款、发货、收货、退货退款、第二笔付款后取消、原请求重放、英文目录及预约预占全部通过断言，pageErrors 为空，钱包退款后恢复。日志 `/tmp/spp-regression-final-develop-browser.log`。测试结束按确切端口、数据库配置及主类定位并停止本 Goal 的进程，未操作其他服务和既有数据库。

Seata 最初选择的两个测试名称不属于现存源码，Maven 成功但未执行测试，该结果不作为证据。核对目录后选择全部三个实际测试类 NativeSeataSagaStateMachineCompilerTest、NativeSeataSagaEngineTest、NativeSeataTransactionBridgeTest 重新执行，**20/20 通过**，日志 `/tmp/spp-regression-final-seata-actual.log`。没有把未选中测试的 BUILD SUCCESS 当作验收通过。

当前未完成范围仍是 lang 四项 APP-only 主键默认查询身份、testing 分库量子初值协调及 testing 业务/网页端到端验证。已有 LogicalQuantumProvisioningClient 接口仅提供 provision；它不能直接证明集中量子库与普通角色 insert 的分库失败恢复已实现。JdbcQuantumJournalStore.insertInitialValue 明确要求量子资源已经加入 JDBC 事务，而普通 Saga 仓储节点只加入自己的资源。仍需完善可恢复的分阶段初始化及失败处理协议，不能移除资源检查或者嵌套两个本地提交伪造共同原子性。Goal 未完成，新修改未提交上传。

## 10 月 12 日存储身份协议与完整联合回归通过

默认主键查询对无法从模型完整推导的 APP-only 主键使用框架的已有存储身份，内部规则标记为 @storageIdentity。普通更新/删除使用同一身份。已能完整推导的单/多扮演者键继续使用现有映射；显式业务查询不会因配置不完整而被改成另一种查询，首次默认绑定错误诊断测试继续通过。四个快照/参与者测试现通过真实生成的默认绑定，不是删除断言或忽略错误。

身份未知时默认查询保留同一实例与事实并标记未确认；更新拒绝 PERSISTENCE_READ_IDENTITY_REQUIRED。新增 JDBC 测试用两个业务属性相同的记录验证未知身份不误选、已有身份原地补全、更新只改变正确记录、记录删除后参与者仍存在但未确认。新增编译器测试核对 APP-only 主键不进入 SPP 模型，默认查询获得框架身份规则。该协议仅使用已建立的存储身份，不声称任意 APP-only 主键的自动插入值或首次外部身份输入协议已经实现；首次非主键定位仍需要 APP 查询。

安装当前工具链后执行完整联合命令：

```bash
mvn -fae -pl petstore-demo,appframe-seata -am test -Dspp.environment=develop
```

**全部模块 BUILD SUCCESS**，lang **340/340**、appframe **577/577**、generator **105/105**、appframe-seata **20/20**、Petstore **33/33**，无失败/错误/跳过。日志 `/tmp/spp-regression-storage-identity-reactor.log`；安装日志 `/tmp/spp-regression-storage-identity-install.log`。没有用指定少量测试替代本次全套联合验证。

再次用新 develop 生成结果与当前运行时启动隔离内存库，readiness=true，真实 Chrome 的完整中文业务、英文目录、重放及预约流程通过，pageErrors 为空；日志 `/tmp/spp-regression-storage-identity-browser.log`。测试服务已停止，未使用既有演示数据库。

剩余阻塞集中到 testing 分库初始化和该环境的端到端验收。已向用户提出待确认的技术恢复方案：记录初始化阶段，失败/重启后核对普通记录成交事实，再完成量子初值或撤销未使用初值；这不是业务补偿，也不承诺两个数据库共同原子提交。该方案尚未获得答复，未实现未经确认的补偿规则。Goal 保持进行中，所有本阶段修改未提交上传。

当前 testing 环境重新生成、生产/测试源码编译及打包也已完成，命令 `mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=testing`，BUILD SUCCESS，日志 `/tmp/spp-regression-storage-identity-testing-package.log`。该命令跳过执行测试，只证明配置生成与编译，不能代表 testing 交易通过。当前 target 已切换为 testing；再次运行 develop 必须先重新生成该环境，不能用 skip-build 沿用 testing 产物。

## 10 月 12 日最新 testing 启动及分库事实核对

使用最新 testing 产物及全新隔离目录 `/tmp/spp-testing-current-5eggeusg`，启动三个独立 JVM。客户域 customerService 与产品域 productService 实际 readiness=true；部署清单分别只包含 customer/product，普通模式 SAGA，量子系统 UNIFIED_STORE。商店 JVM 启动退出 1，仍为 QUANTUM_PROVISION_RESOURCE_NOT_ENLISTED，且附加 petshop.insertStockLine / petshop.insertGoods 的 COMMITTED_STAGE_COMPENSATION_REQUIRED。实际部署证据在目录中的 evidence.json；三个进程均已终止，未改动其他服务和既有数据库，没有用 readiness 代替业务验收。

停止进程后，以 IFEXISTS=TRUE、ACCESS_MODE_DATA=r 只读打开隔离 H2 库核对已成交事实：普通 shop 库有四条 StockLine 快照，每条只保存 Goods.sku，不含 available/reserved/sold；量子 ledger 库有 12 条库存事实，分别为每种商品 available=10、reserved=0、sold=0。说明先前库存节点已经在两个存储中产生事实，恢复问题不能只处理失败 Merchant 的现金初值，更不能把已提交节点视为普通数据库回滚。检查日志为 shop-inspection.log、ledger-inspection.log。

最新失败与先前结果一致，当前也没有残留测试服务或运行中的构建。独立可推进的集中部署回归均已通过；testing 的初始化恢复与后续端到端验收依赖此前发出的规则选择问题，尚未收到用户答复。没有实现未经确认的业务补偿，没有重新运行已部分成交的初始化以掩盖失败。Goal 尚未完成，修改未提交上传。

## 阻塞审计：等待初始化恢复规则

同一分库初始化恢复问题已在提出方案、最新三 JVM 实测及本次状态核对中连续出现。完整 develop 联合测试与网页验收通过，testing 配置生成/编译通过，客户与产品提供方就绪；商店仍因量子初值资源未加入事务而启动失败，且先前节点已成交。没有活跃构建或测试进程需要等待，也没有可以代替该规则确认的独立验收工作。

待用户决定是否采用此前提出的技术恢复方案：框架记录初始化阶段，失败或重启后核对普通记录成交事实，再完成量子初值或撤销未使用初值。必须处理此前已提交的库存等节点，不仅是失败的 Merchant。业务补偿仍须按用户既有约定单独讨论，不自行添加业务补偿。完整 Goal 因此标记 blocked，未标记完成，未提交上传；收到决定后继续实现和 testing 端到端验收。

## 10 月 12 日初始化归类修正与未决事项处理

用户明确：数据库及量子初值初始化属于技术启动准备，不是业务交易，不需要业务补偿。此前以补偿规则未决将 Goal 标为 blocked 的判断撤销，继续回归。APP web.start 在通用运行时初始化上下文中执行；初始化完成前不发布 readiness。普通种子记录只在缺失时插入，量子初值在自身数据库事务内补齐，已有值不覆盖；启动失败保留此前成功种子步骤，重启可继续补齐。该流程不承诺不同数据库原子提交，也不改变正常业务插入及业务 Saga 恢复规则。

实现及验证路径：先验证分库初始化、部分失败后重试和余额不重置；再生成 testing，执行三个 JVM 的启动及业务网页回归。未决问题登记为 known issue，注明影响和未验证范围，跳过受影响验收并继续其他工作，不以未决本身标记 blocked，也不将未验证项报告为通过。业务补偿的进一步设计仍作为独立未完成项。

### 技术初始化修复实测结果

使用当前生成的 testing 配置和修复后的运行时，在全新隔离目录 `/tmp/spp-bootstrap-testing-m8r0jigq` 启动 customerService、productService、petstore 三个 JVM，全部 readiness=true。商店 JVM 停止后复用同库重启，再次 readiness=true。启动失败及经营者初值问题已解除，不需要业务补偿。测试进程均已停止。

同次 Chrome 网页验收在注册买家处返回 QUANTUM_PROVISION_RESOURCE_NOT_ENLISTED：业务新建角色的量子初值配置仍缺资源协调。这是业务创建而非启动种子准备，不通过放宽启动上下文掩盖。按用户要求记录为 [KI-001](known-issues.md)，跳过依赖注册的 testing 后续网页步骤，继续其他回归，Goal 不标 blocked。初始化重试的当前支持范围及未验证项见 KI-002。

### 修复后 develop 网页验证

当前 develop 生成结果及修复后运行时，在隔离内存库启动 readiness=true，真实 Chrome 完整流程通过（注册、购物车、下单、付款、履约、退货退款、付款后取消、重放、英文目录、预约预占），pageErrors=[]。日志 `/tmp/spp-bootstrap-develop-0vjuw_t_/browser.log`，浏览器退出码 0，服务已停止。

先前独立 appframe 全测日志 `/tmp/spp-bootstrap-appframe.log` 作废：我在其尚未结束时启动另一个 Maven 联合构建，共用 target/test-classes，导致测试类被并发重编译而出现 NoClassDefFoundError。最终以无其他并发构建的 `/tmp/spp-bootstrap-reactor.log` 为验收证据；其中新增 DatabaseInitializationTest 已通过，appframe 578/578、lang 340/340、generator 105/105。

### 本轮最终结果

当前联合回归命令 `mvn -fae -pl petstore-demo,appframe-seata -am test -Dspp.environment=develop` 最终 BUILD SUCCESS：lang 340/340、appframe 578/578、generator 105/105、appframe-seata 20/20、Petstore 33/33，无失败、错误或跳过。日志 `/tmp/spp-bootstrap-reactor.log`。develop 真实网页通过；testing 技术启动和重启通过，testing 业务注册失败及其后续依赖步骤按用户要求保留为 known issue，不算通过。当前 target 为 develop。

本轮按上述 known-issue 处理约定结束回归 Goal；业务补偿及新建量子事实业务协调并未宣称实现。文档及源码修改未提交上传，没有修改既有演示数据库。
