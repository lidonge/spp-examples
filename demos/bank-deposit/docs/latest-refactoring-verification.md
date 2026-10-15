# 最新重构验证记录

2026-10-13，重构仍在活动 goal 中；以下 1,135 项为补充有限入口核对之前的联合回归记录；本报告只证明下列已执行范围，不证明所有历史验收或透支资金模型已完成。

## 联合回归

```
mvn -pl :petstore-demo,xbod-deposit-demo -am test -Dspp.environment=develop
```

BUILD SUCCESS，失败、错误、跳过均为零：

| 模块 | JUnit 测试数 |
| --- | ---: |
| lang | 362 |
| appframe | 617 |
| generator | 106 |
| Petstore | 39 |
| XBOD | 11 |
| 合计 | 1135 |

XBOD 的 11 项测试内包括 92 个历史输入向量：核心偿还 15、协议积数 12、准入/授权 49、手续费 16。向量计数与 JUnit 方法数分开，不冒充 92 个独立测试。缺失费率与授权评估的新版协议差异见重构文档。

## 分库存储验证

```
mvn -pl :xbod-deposit-demo -am test \
  -Dtest=XbodCalculationTest,XbodRuleTest,XbodTransactionTest \
  -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing
```

BUILD SUCCESS。覆盖零资金开户、现金对方负余额、成交回填、同日冲正、跨日保留后续存入、Mode2，以及普通保存故障时量子恢复、普通 Saga 已提交阶段仍需补偿的真实结果。testing 只是本 JVM 内两个独立 H2 数据源，不据此宣称验证真实网络分布式部署、XA、Seata AT 或 TCC。

## 验证限制

- 欠款及敞口的量子守恒贡献尚待建模决策；核心计算向量通过不代表透支偿还落库完成。
- 分库普通 Saga 补偿未擅自发明，fail 记录待核对信息并保留 RECOVERY_REQUIRED。
- 旧 86 个 APP 整体验收入口的技术故障、重启、通信与并发覆盖尚未全部迁移。
- 本轮未提交、未上传。业务源只在 SPP／APP／PHY；Java 源仅限验收。

## 有限入口开户补充验收

新增测试绕过测试辅助补零，仅给账户号、开户日期及空的已声明参与者实例；生成开户场景必须自行建立普通业务初态，默认仓储在量子库建立零事实，随后可以立即现金存入。补充通用仓储测试同时验证本地与独立量子库的缺失初值处理；原有非零初始化限制、提交后补建和恢复测试继续保留。

2026-10-13 develop 专项 BUILD SUCCESS：QuantumOpeningRecoveryTest 9 项、DatabaseInitializationTest 2 项、银行验收 12 项，共 23 项，失败、错误及跳过为零。该记录不替代上面的联合回归；本轮新增运行库改动仍需在最终验收时纳入完整回归。

testing 专项同样 BUILD SUCCESS，共 23 项、失败/错误/跳过为零；包含有限开户后立即现金存入。测试两边数据库均隔离，避免重复业务账户号共享旧量子事实而造成串扰。

补充运行库全量回归 `mvn -pl appframe -am test`：BUILD SUCCESS，618 项、失败/错误/跳过为零。默认量子零记录改动已纳入此轮完整运行库验证。

## 网点规则与账户归属补充验收

新增 54 组网点范围、柜员号边界与例外、卡和存折告警数据，复用旧源记录的输入及期望。新版银行业务向量共 146 组。

账户归属新增真实存储验收：混用另一账户的资格事实时，存入在成交前拒绝；拿另一账户原合约办理冲正时，在成交前拒绝；分别确认未错误改变资金。

2026-10-13，develop 和 testing 均执行银行三个测试类并 BUILD SUCCESS，各 15 项 JUnit 测试，失败、错误及跳过为零。这些向量和归属检查不解决 KI-R01 的欠款守恒建模问题，也不替代未迁移的技术恢复条目。

## 现金冲正分录补充验收

补齐原分录查询、八槽证据校验、借贷反向计算及冲正分录保存。原合约为 key 的原分录查询、冲正合约为 key 的反向分录查询均由 APP 外键关系默认推导，未添加冗余 repository 配置。

新增真实费率存储路径：登记个性化费率，现金存入 10,000 时原手续费为 6；现金冲正全额退回 6，并重新查询数据库验证八条反向分录的槽位、科目、方向和金额。同步验证回填的净余额为零。明细在合约自动生成编号后补全归属再插入，避免保存空合约凭证。

2026-10-13，develop 和 testing 银行验收均 BUILD SUCCESS，各 16 项 JUnit 测试，失败、错误及跳过为零，历史规则向量仍为 146 组。欠款量子守恒的模型决策及普通 Saga 补偿仍按已知问题处理，未据此宣布全量目标完成。

## 冲正分录保存故障验收

新增插入反向分录前故障，分别读取数据库核对资金、原成交标记、冲正合约与分录。develop 的 LOCAL 恢复原资金和未冲正标记，冲正合约不存在，随后重试可完成。testing 的 Saga 反交易资金成功，但已提交原交易标记与冲正合约仍在，分录为空；fail 返回 RECOVERY_REQUIRED、handled=false 并记录 RECONCILIATION_REQUIRED，不冒充整笔回滚。

2026-10-13 两套配置的 XbodTransactionTest 均 9 项通过，失败/错误/跳过为零。该新增方法连同此前计算和规则测试，银行方法总数为 17；本轮专项不等同重新运行所有 17 项。

## 独立 JVM 文件数据库重启验收

新增 XbodRestartTest：三个独立 JVM 使用相同文件数据库依次开户存入、重启后查询原成交并跨日冲正、再次重启查询原成交标记和八条冲正分录，并确认账户与现金结算资金为零。后续 JVM 不重新开户、不重置量子事实；测试 Java 只调用生成服务及断言。

2026-10-13 develop、testing 的重启专项均 BUILD SUCCESS，各 1 项通过。testing 使用两个独立文件数据库。此项证明正常退出后的跨 JVM 持久化与继续办理，不声称覆盖进程被杀、提交结果未知或网络分区恢复。

## 跨日积数与场景拆分验收

新增 XbodAccrualTest 两条真实入账路径：余额 100 持有一天后再存入 50，保存正常积数 100；余额 650 的十天普通期间、四天协议窗口和五档门槛，保存普通积数 4,300、协议积数 2,200。通过生成查询重新读取数据库，不只验证计算计划。

2026-10-13，积数 develop 专项两项通过；完成全部 13 个场景各自独立文件后，testing 的 Xbod*Test 全部 20 项通过，失败/错误/跳过均为零。历史规则向量仍为 146 组，欠款量子模型和补偿政策仍未关闭。

同轮 develop 的 Xbod*Test 全部 20 项也 BUILD SUCCESS，失败/错误/跳过为零；场景拆分后的生成链路、本地共同提交、正常退出重启和真实积数保存均已纳入。

## APP 技术幂等与当前联合回归

可信 RemoteServiceIngress 验证存入和冲正的相同请求方/流水号重放，重新查询证明资金、合约编号和分录未重复发生；不同请求方相同流水号分别成交。本地调用携带相同请求技术头仍分别成交，不受远程幂等抑制。testing 专项四项通过；此项不冒充真实网络故障恢复。

2026-10-13 当前联合回归 `mvn -pl :petstore-demo,xbod-deposit-demo -am test -Dspp.environment=develop` BUILD SUCCESS：lang 362、appframe 618、generator 106、XBOD 24、Petstore 39，共 1,149 项，失败/错误/跳过为零。此轮包含新增默认量子零事实、单域部署生成、真实冲正分录、跨日积数、重启及幂等验收。

完整性审计见 [completion-audit.md](completion-audit.md)：欠款量子模型、普通 Saga 补偿及未逐入口迁移项未因联合回归通过而自动完成。

## 并发业务补充验收

XbodConcurrencyTest 两条路径：不同账户在事前计算结束处同步后分别存入 100/200，数据库核对各自资金、结算对方、合约归属及明细计数；同一原交易的两个冲正请求都通过事前校验后竞争，只有一个成交，另一个报告 ROLLED_BACK，最终资金为零且成交冲正分录为八条。

2026-10-13 develop、testing 并发专项均 BUILD SUCCESS，各 2 项、失败/错误/跳过为零。未在事务内设置测试屏障；没有手写账户计算或互斥业务实现。该项只验证两请求定点竞争，不冒充高负载或真实网络并发，也未逐项覆盖旧“不同请求身份作用于同一账户”重试入口。

## 执行中远程副本与请求内容冲突

并发相同请求方/流水号不会再次执行业务。现行 API 对正在运行的副本返回 REQUEST_IN_PROGRESS；原调用完成后，技术层重放取得相同合约编号与结果，数据库余额仍仅增加 100。此项没有偷偷改成同步等待协议。改变金额后复用原请求流水号，技术层返回 REQUEST_ID_REUSED，资金仍为 100。

2026-10-13 develop 的 XbodIdempotencyTest 六项通过；testing 的并发重放等五项通过，新增请求内容冲突专项一项也通过。失败/错误/跳过均为零。执行中返回策略的未决部分见 KI-R05，不把新的技术返回政策藏进业务语言。

## 本机 HTTP 与界面防重

通过真实回环 HTTP 调用 GeneratedWebServer 的 APP 场景目录，验证存入/冲正、重复点击重放、服务器覆盖伪造调用模式/请求方头，以及未暴露服务 404。网页 Origin.USER 使用 APP 的 5 秒 duplicate；系统 Origin.SERVICE 使用请求方流水号幂等，LOCAL 不受二者抑制。验收最初错误地把网页请求当成系统 RPC，已依据运行协议修正并补齐 APP 配置。

2026-10-13 develop、testing 的 HTTP + 幂等专项均 7 项通过，失败/错误/跳过为零。测试服务器使用随机本机端口，结束时关闭。不是对公网部署、网络丢包或完整银行前端的验证。

银行当前共 29 项方法（计算 5、规则 3、事务 9、重启 1、积数 2、幂等 6、并发 2、HTTP 1）。此前 1,149 联合回归为新增并发/HTTP等验收之前的记录，不冒充最新全量联合结果。

## 多参与者防重与最新联合回归

2026-10-13 执行 `mvn -pl :petstore-demo,xbod-deposit-demo -am test -Dspp.environment=develop`，BUILD SUCCESS。Surefire XML 核对：lang 364、appframe 620、generator 106、XBOD 29、Petstore 39，共 1,158 项，失败、错误、跳过均为零。日志：`/tmp/xbod-multi-facts-joint.log`。

APP 的 `facts(path1, path2, ...)` 同时核对多个参与者，支持可空可选资料并兼容原单路径元数据；新增远程代理元数据查询测试，确保这些查询不会调用业务适配器。真实 HTTP 更改费用参与者但保持金额不变时拒绝重放，余额保持原成交值。develop/testing 专项及 develop 联合回归通过，KI-R06 关闭。

本次测试通过不代表透支偿还的量子守恒模型、普通 Saga 补偿政策或全部历史恢复入口已完成；这些限制仍列在 known-issues-latest.md。

## 还本还息资金对方的分录验收

2026-10-13 根据用户澄清修订 KI-R01：还息必须增加银行内部户，不能以欠息减少代替资金流入。新增 `repaymentPostingsIncludeBankInterestAndPrincipalCounterparts`，输入存入 100、欠息 10、催收息 5、欠本金 20，实际调用生成的计算、校验及分录服务，断言客户余额入账 65、还本 20、利息 10、催收息 5，借贷总额分别为 100。

执行 `mvn -pl :xbod-deposit-demo -am test -Dtest=XbodCalculationTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop`，六项通过，失败/错误/跳过均为零。日志 `/tmp/xbod-repayment-postings.log`。此项验证分配与分录计算，银行内部户量子资金落库和冲正仍需实现，不把分录断言当成账户入账验收。

## 真实收款内部户与量子状态联合验收

2026-10-13 完成三类银行内部账户的 SPP 角色、独立开户场景、APP 表、原成交引用、存入及冲正更新。示例存入 100 后，客户余额 65、银行利息 10、催收息 5、本金回收 20、现金结算 -100；欠息、欠本金及敞口是同笔更新的量子状态，不再重复参加资金求和。

新增 XbodRepaymentTest 三项验收：混合清偿后重新查询真实内部户并跨日冲正；后续普通分录保存故障时同步恢复银行资金和欠款；内部户余额不足时拒绝冲正，原交易仍未冲正且欠款不被恢复。通用 QuantumStateWithConservationTest 验证资金仍需守恒、状态边界失败使所有资金变化回滚、持久化及反交易重试不重复执行。语言测试验证被排除出资金组的实际量子写入仍进入完整元数据。

核对归档源发现旧核心 JSON 提取遗漏了省略前导零的小数，共补回 22 个输入/期望字段；修复后两位小数的 PHY 容量确实不足，改为 `BigDecimal(25, 6)` 后，原 15 组精确计算向量通过。此前测试通过不能作为这批遗漏小数分支的验证依据。

命令 `mvn -pl :petstore-demo,xbod-deposit-demo -am test -Dspp.environment=develop` BUILD SUCCESS：lang 365、appframe 623、generator 106、XBOD 33、Petstore 39，共 **1,166 项**，失败/错误/跳过均为零。日志 `/tmp/xbod-internal-accounts-joint.log`。最终六位小数配置的 testing 全量验收另外执行，不能以 develop 结果替代。

最终配置下执行 `mvn -pl :xbod-deposit-demo -am test '-Dtest=Xbod*Test' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS：33 项，失败/错误/跳过均为零。日志 `/tmp/xbod-internal-accounts-testing-final.log`。KI-R01 关闭，普通 Saga 业务补偿及尚未逐项核对的历史恢复验收保持各自状态。

## 历史欠款分支与实际进程退出

新增 XbodRepaymentTest 的四条历史持久化路径：普通欠款先息后本、不良贷款先还本、核销贷款先还本、0.005/0.004/0.001 小数偿还。分别验证真实内部户、欠款恢复、成交前积数、原手续费、八条冲正分录，以及明细计数和原交易日期。测试通过物理存储夹具准备既有账户事实，业务处理只调用生成的 SPP；必须同时准备 APP 表和当前对象仓储事实，不能只改表后误以为查询读到了新状态。

新增 XbodReversalRuleTest 核对关闭/撤销/冻结/SA01116 例外及校验优先级，前置业务控制与核心冲正校验独立，以及 WN201 提示、EN134 拒绝。develop 的上述专项共 10 项全部通过。

新增 abruptExitAfterConfirmedCommitPreservesDepositForReversal：子 JVM 在成交确认并记录原交易号后执行 Runtime.halt(73)，第二、第三个 JVM 查询并冲正，再查真实分录及余额。第一次干净构建发现 H2 文件库默认 500 毫秒写延迟下，立即退出会丢失近期确认结果；将文件连接配置设为 WRITE_DELAY=0 后，两条重启测试通过。run-demo.sh 的默认文件库连接和 PHY 默认也同步此配置。自定义文件库 URL 应保留同步写配置。此项验证成交确认后的进程退出，不冒充提交时刻未知、操作系统断电或 Saga 中途恢复。

日志 `/tmp/xbod-debt-history-develop-v2.log`、`/tmp/xbod-crash-durability.log`。完整干净构建及分库验收单独记录最终结果。

## 干净构建最终结果

2026-10-13 执行 `mvn -pl :petstore-demo,xbod-deposit-demo -am clean package -Dspp.environment=develop`，BUILD SUCCESS：lang 365、appframe 623、generator 106、XBOD 41、Petstore 39，共 **1,174 项**，失败/错误/跳过均为零。日志 `/tmp/xbod-clean-joint-final.log`。本轮先清除旧生成目录，重新生成带域服务目录与 APP/PHY 元数据；生成目录不再依赖旧根目录 app-ddl.properties。生产服务目录中没有旧 ExampleRun/Verification 入口。

XBOD 新增验收包括四种实际欠款分支、三个核心冲正规则检查，以及成交确认后强制退出的重启验证。旧技术生命周期与待授权流程不因此自动视为完整迁移；具体范围和差异见历史入口台账及 KI-R02/KI-R04/KI-R05/KI-R07。

同日最终 testing 命令 `mvn -pl :xbod-deposit-demo -am test '-Dtest=Xbod*Test' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS：XBOD **41 项**，失败/错误/跳过均为零。日志 `/tmp/xbod-history-testing-final.log`。分库配置下新增坏账/核销/小数清偿及强制退出后的持久化检查均通过。

## 完整历史日历入口验收

从归档 `cboddeposit-99o-calendar-examples.spp` 逐项提取 30 组原输入与期望，保存为 `bank-calendar-cases.json`；另保留原两组计息单位向量（199.999 按 100 单位得到 100、10 按 3 单位得到 9，均计息两天）。`XbodCalendarTest` 只调用生成场景并断言，不在 Java 中实现日期或计息算法。覆盖世纪闰年、平年、跨年、起止同日、ACT/360365/360360、非法日期、倒置日期和不支持的日数制，错误码与归档逐项一致。

命令 `mvn -pl :xbod-deposit-demo -am test -Dtest=XbodCalendarTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS；2 个 JUnit 方法验证 32 组向量，失败/错误/跳过均为零。日志 `/tmp/xbod-calendar-testing.log`。此专项只补足日历入口，不代替完整交易回归或其余历史入口核对。

## 历史会计分录入口验收

`XbodPostingRulesTest` 与 `posting-rules-cases.json` 按归档 `cboddeposit-99zw-posting-rules-examples.spp` 迁移六种分配：普通存入含手续费、普通欠款先息后本、不良贷款先还本、零存入从原余额清偿、存入与原余额共同清偿、小数偿还。逐槽检查金额、科目、方向和序号，同时验证借贷总额。另核对错误方向、null 科目、伪造总额、分配缺失四类原错误码；前两项直接比较调用前后的生成请求对象，证明拒绝时未修改参与者。

当前规则要求场景显式调用 check，故测试调用 checkPostingRules 后才调用 calculateDepositPostings；旧计算内校验及 try/catch 不恢复。生产 depositCash 的分类、会计校验、分录规则校验、分录计算和借贷校验均位于事务之前。

`mvn -pl :xbod-deposit-demo -am test -Dtest=XbodPostingRulesTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS：3 个方法，失败/错误/跳过均为零；日志 `/tmp/xbod-posting-rules-testing.log`。这是该历史规则入口的专项证据，不代替分录持久化中途失败和其余恢复入口的验收。

## 分录批量写入中途失败

新增 `XbodPartialPostingTest`，技术故障限定在测试源码：H2 AFTER INSERT 触发器允许前三条写入，第四条抛出 SQLException；断言触发计数为 4，证明并非服务开始前失败。分别执行生成的存入、冲正场景，查询真实表确认失败批次零残留，重新查询客户与现金结算账户确认资金恢复。冲正失败还验证八条原存入分录保留。

LOCAL 环境整笔回滚，删除故障触发器后重新办理成功且仅保存八条目标分录。testing 分库环境量子变化已反向恢复，但先前普通步骤已经提交（冲正标志仍为 true），因此必须报告 RECOVERY_REQUIRED，不能称为整笔回滚，也不在测试中替业务编写补偿。

`mvn -pl :xbod-deposit-demo -am test -Dtest=XbodPartialPostingTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` 与对应 develop 命令均 BUILD SUCCESS，各 2 项，失败/错误/跳过均为零。日志 `/tmp/xbod-partial-posting-testing.log`、`/tmp/xbod-partial-posting-develop.log`。旧例的预存主键碰撞、审计事件和精确量子日志条数未由该故障等价覆盖，迁移台账保留差异。

## 入口事实覆盖与原成交结算参与者

新增 `XbodSourceIntegrityTest`：入口伪造客户余额、欠款、账户关闭状态、明细数、现金结算余额、分配计划及合约金额，仍按查询到的零开户事实完成真实 100 元存入；冲正入口伪造原金额 999 和已冲正标志，默认查询恢复原成交 100 元事实并正确冲正。另逐一将现金结算、利息收入、催收息收入、本金回收参与者替换为另一个已开户的同类型角色，均被 ORIGINAL_SETTLEMENT_ACCOUNTS_MISMATCH 拒绝；原成交未标记冲正，客户资金及替代账户资金未改变。

`mvn -pl :xbod-deposit-demo -am test -Dtest=XbodSourceIntegrityTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop` 及对应 testing 命令均 BUILD SUCCESS，各 3 项，失败/错误/跳过均为零。日志 `/tmp/xbod-source-integrity-develop.log`、`/tmp/xbod-source-integrity-testing.log`。旧入口在查询之后篡改 prepared 工作对象的测试，与本次入口事实覆盖范围不同，迁移台账明确保留区别；也不将此测试视为解决 KI-R03 外部资格资料可信来源。

## 同一账户不同请求并发

新增 `XbodConcurrencyTest.concurrentSameAccountRejectsStaleFactsAndAllowsFreshRetry`：两线程在 prepareDepositAgreement 前汇合，确保两者已读取同一账户的旧事实，再分别存入 100、200。验证只有一个成功，失败方 handled=true；重新查询资金、现金结算余额、普通显示余额及明细数，确认只保留成功方。随后通过新的场景调用重新查询并办理失败方金额，最终余额 300、明细数 2。未在 SPP 引入版本属性或 Java 银行业务实现。

`mvn -pl :xbod-deposit-demo -am test '-Dtest=XbodConcurrencyTest#concurrentSameAccountRejectsStaleFactsAndAllowsFreshRetry' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop` 与对应 testing 命令均 BUILD SUCCESS，各 1 项。两日志均记录 PERSISTENCE_VERSION_CONFLICT，路径分别为 `/tmp/xbod-same-account-develop.log`、`/tmp/xbod-same-account-testing.log`。这里冲突发生在普通更新阶段；不代表所有 Saga 部分成交故障均能自动恢复，KI-R04 继续保留。同步并发验收也不代替高负载或真实网络测试。

## 原分录损坏与原现金冲正策略补充

`XbodOriginalPostingIntegrityTest` 同时破坏 APP 表和对象仓储中的同一分录，分别改金额和删除一条，随后调用生成冲正场景；要求拒绝且客户资金、结算资金、原交易标志和反向分录均不改变。首次执行金额篡改通过，删除夹具因直接调用严格仓储 delete 缺少声明事务而失败，尚未进入冲正；测试改用直接 SQL 构造缺失事实，未放松生产仓储约束。

`XbodCashPolicyTest` 逐项迁移归档 cash-policy 八组规则：四组日期、明细、日累计及积数期望；积数 2200 小于待撤销 2200.001 时 EN097；原手续费 0、2、1.005 全额退回。测试调用生成的显式校验或计算服务，比较调用前后输入参与者不变，不恢复旧计算内 check。最终运行结果另记。

最终命令 `mvn -pl :xbod-deposit-demo -am test '-Dtest=XbodOriginalPostingIntegrityTest,XbodCashPolicyTest' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS，5 个方法，失败/错误/跳过均为零。日志 `/tmp/xbod-original-policy-testing.log`。原分录损坏均在更新前拒绝；cash-policy 八组历史期望全部保留。

## 账户控制与手续费入口边界

新增 `XbodAdmissionBoundaryTest`：迁移原 cash-control 的正常通过、控制机构/只付不收/锁定/冻结/撤销/房地产类六种拒绝，以及余额 10 冻结 10 后存入 1 的可用余额 1。当前 checkCashControl 合并原前置与核心账户控制，计算仍独立。另经完整存入场景验证费率缺失和锁定拒绝，重新查询资金、明细并直接检查成交与分录表无记录。

跨网点费率 0.001、固定 1、最低 2、最高 50，对 600 元存入收取 2 元；查回八条分录验证两个手续费槽位，借贷各 602。新账户从零开户，不复制旧例凭空注入 100 的资金夹具。首次验收发现缺少费率虽记录 PARTICIPANT_NOT_IDENTIFIED，场景却继续入账：identify 只跳过其所在 if 块，未退出场景。修复为 if 内只查询，主层调用 checkRequiredFeeIdentified，以参与者确认状态返回原 DEPOSIT_FEE_RATE_NOT_FOUND 并在事务前终止。depositCash 与 quoteDepositFee 同步修复；纯费率计算预览不要求查询身份。旧业务 request/attemptId 和拒绝审计结构不回迁。最终执行结果另记。

修复后 testing 专项 3 项通过，日志 `/tmp/xbod-admission-boundary-fixed.log`。随后全量 `Xbod*Test` 执行 60 项：59 项通过，唯一失败为资源复制时仍使用旧通用码的手续费第 14 组（实际已返回原业务码）。只修正该原始期望后，运行 `mvn -pl :xbod-deposit-demo -am test '-Dtest=XbodRuleTest,XbodAdmissionBoundaryTest' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing`，6 项全部通过，涵盖 49/54/16 组规则及新增拒绝和真实入账测试；日志 `/tmp/xbod-fee-regression-final.log`。全量初次日志 `/tmp/xbod-expanded-testing.log` 保留失败证据，不称为一次全绿构建。其余 59 项无需因该单个期望值变更重复运行。

## 协议日期与分档结果复用

`XbodDatedAgreementTest` 迁移七组原协议日期窗口：部分重叠、全部覆盖、未来生效、已失效、无生效日、同日生效取消等，分别验证裁剪日期、重叠天数、10 天普通期间及原普通/协议积数；第八组非法日期由显式 checkAccrualDates 返回 EE374，输入不变。testing 专项 2 个方法全部通过，日志 `/tmp/xbod-dated-agreement-testing.log`。

继续核对原 17 个分档案例，现有 JSON 覆盖 01、02、04 至 13，共 12 组；缺失的是 03 的跨调用结果复用和 14 至 17 的拒绝规则。新增 XbodAgreementReuseTest 在同一个生成请求上执行模式 1、修改输入后执行模式 2，验证旧 2000 分档积数被清零，新分档为 0/400/400/400/400；另验证缺少分档、分档乱序、负门槛、重叠期间过长时在计算前拒绝且所有参与者不变。最终结果另记。

`mvn -pl :xbod-deposit-demo -am test -Dtest=XbodAgreementReuseTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS，2 个方法验证缺失五组，失败/错误/跳过均为零。日志 `/tmp/xbod-agreement-reuse-testing.log`。加上既有 12 组，原 agreementProductExampleRun 的 17 组规则现均有对应验收。

## 冲正额度与敞口恢复策略

XbodReversalCapacityTest 迁移原通用反交易 07–10 中与现金共享的拒绝规则：可用额度不足 ES020、许可透支但基数负值 EN249、正基数与恢复欠本冲突 EN177、原金额不平衡；验证校验不改变任何输入。XbodRepaymentTest 新增真实敞口小于还本金额的开户夹具：欠本 20、敞口 5，偿本 10 后敞口为 0、原 exposureDelta 为 -5；按原 XBOD 现金规则冲正后欠本 20、敞口 10，本金回收账户回零。原现金规则与通用实际增量反交易差异已写入设计和迁移台账。

`mvn -pl :xbod-deposit-demo -am test '-Dtest=XbodReversalCapacityTest,XbodRepaymentTest#cashReversalKeepsXbodPrincipalBasedExposureRule' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS，3 项，无失败、错误或跳过。日志 `/tmp/xbod-reversal-capacity-testing.log`。本项保留已确认现金业务语义，不修改系统技术失败时的量子反交易算法。

## 成交提示与办理信息持久化

核对 bankWarningCashExampleRun 发现原成交记录要求保留卡/存折提示、准入告警和办理信息，而新版合约原先仅保存金额与冲正所需分量。新增 notices/operator/bankProfile/admission 四项明确业务事实，由 SPP prepareDepositAgreement 写入 CashDepositAgreement。

XbodBankNoticeTest 完成真实 600 元存入后，用默认查询查回 WN200、WN201、WARNING/F0554、SA01102、未代理办理以及原账户系列 49927；再以不同办理和卡资料完成另一笔存入，重查第一笔，核对原事实仍保持。测试不写业务 Java，只准备请求并断言。同步验证原交易、冲正与技术幂等测试，结果另记。此项不解决外部资格资料可信来源 KI-R03，也不把新请求当作原请求幂等重放。

`mvn -pl :xbod-deposit-demo -am test '-Dtest=XbodBankNoticeTest,XbodTransactionTest,XbodIdempotencyTest' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS，16 项，失败/错误/跳过均为零。日志 `/tmp/xbod-bank-notice-testing.log`。新增提示留存、原有现金冲正及远程重放均通过。

## 网点限制与柜员上下文的整场景拒绝

XbodBankNoticeTest 新增完整场景验收：仅限原网点的账户在异网点办理时 EN134；柜员地区与费用办理上下文不一致时 DEPOSIT_OPERATOR_CONTEXT_MISMATCH。两次拒绝后重新查询客户/结算账户及明细，均未变化，直接查询 CASH_DEPOSITS/CASH_POSTINGS 均为空。

`mvn -pl :xbod-deposit-demo -am test -Dtest=XbodBankNoticeTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop` BUILD SUCCESS，2 项，失败/错误/跳过均为零。日志 `/tmp/xbod-bank-notice-develop.log`。同时验证上一轮新增成交提示留存功能在 LOCAL 部署正常；testing 的提示、冲正、幂等 16 项证据见上一节。

另逐项阅读 ordinaryCashExample、crossDayCashReversalExample、sameDayCashReversalExample、mode2CashReversalExample 的原断言，台账更新为明确的新测试映射及未直接迁移的旧技术结构，不再使用笼统未核对占位，也不将多个专项夸大为原入口逐字等价。

## 失败处置记录的查询缺口

增强 XbodTransactionTest 两条保存故障验收：通过 findCashFailureRecord 重新查询处理记录，核对处理状态和所关联失败合约的完整失败字段。testing 命令 `mvn -pl :xbod-deposit-demo -am test '-Dtest=XbodTransactionTest#storageFailureRollsBackFundsAndRunsSourceFailureDisposition+reversalPostingFailureRestoresFundsAndExposesOrdinaryStageOutcome' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` **失败**（1 failure、1 error），日志 `/tmp/xbod-persisted-failure-testing.log`。

存入用例默认关联补全查找未提交的合约并报 PARTICIPANT_ASSOCIATION_NOT_FOUND；冲正用例查回实时合约导致原失败 code 消失。新增断言保持，未降低验收要求。定位到 ParticipantRelationshipQueries 的无差别关联递归，以及 APP snapshot 只允许角色标量属性的限制。修复方向与当前未完成状态见 KI-R08。

### KI-R08 修复进展：关联快照贯通与物理容量

APP 解析及部署校验已允许实体/角色/合约参与者关联和集合的 snapshot，保留原标量映射限制。生成元数据已确认包含 `table.CASH_FAILURES.snapshotFacts=deposit,reversal`。默认关联查询跳过快照子树，存储投影不再把快照压缩为身份键。新增语言与运行测试分别通过 6 项和 2 项，另已加入存储投影测试待运行。

端到端测试仍未通过。v3 查询侧修复消除了缺失合约查询异常，但暴露写入仅存身份的问题；v4 同步保存完整快照后，H2 报 `DEPOSIT_RESULTINFO_FAILURE_SUPPRESSEDCODES VARCHAR(50)`（冲正为 REVERSAL 前缀）容量不足，造成失败记录自身保存失败。日志 `/tmp/xbod-failure-snapshot-v3.log`、`/tmp/xbod-failure-snapshot-v4.log`；两次 XBOD 均 9 项中 2 失败。不能关闭 KI-R08，下一步需完善参与者快照的物理表示/系统失败字段容量，并运行新增投影测试及端到端复验。

### KI-R08：快照 CLOB 与空值覆盖复验

`/tmp/xbod-snapshot-clob-testing.log` 的 testing 联合验证通过：语言 6 项、运行库 3 项、XBOD 交易 9 项，共 18 项；失败记录重新查询能够保留失败合约的完整失败字段。生成的 CASH_FAILURES 使用 deposit/reversal CLOB 保存整个快照。

后续直接 JDBC 验收发现：将已有快照设为 null 时，通用列回退逻辑取出旧 JdbcClob 再做 JSON 编码，触发 PARTICIPANT_SNAPSHOT_WRITE_FAILED。现已改为快照列直接保存参与者当前完整值（包括 null），不回退旧数据库对象。命令 `mvn -pl generator -am test '-Dtest=ParticipantSnapshotJdbcTest,DDLGeneratorTest' -Dsurefire.failIfNoSpecifiedTests=false` 已通过，日志 `/tmp/participant-snapshot-jdbc-ddl-fixed.log`，覆盖长失败原因、类型化集合、空值覆盖及 DDL CLOB 生成。Goal 保持 active；本轮未标记 blocked，整体回归仍需继续。

## 当前全量回归与历史积数专项

2026-10-13 执行 `mvn -pl :xbod-deposit-demo,petstore-demo -am clean test -Dspp.environment=develop`，日志 `/tmp/xbod-petstore-current-joint.log`。目前语言 366、运行库 627、生成器 107、XBOD 70 项通过，Petstore 尚在执行；最终结果以本节后续记录为准。新增 XbodAccrualRuleTest 用四组历史原始期望核对积数、计息日历差异、截取单位及催收利息天数，未用测试 Java 重写计算。

回归运行期间追加了 QuantumRepositoryFacts 快照子树边界修复及 QuantumParticipantSnapshotTest；上述全量结果不包含这项后续修改，需专项复验。

上述 develop clean 联合回归最终 BUILD SUCCESS：语言 366、运行库 627、生成器 107、XBOD 70、Petstore 39，共 1,209 项，失败/错误/跳过均为零。结束于 2026-10-13 17:04:34。随后以 testing 环境启动量子快照、JDBC 快照、关联投影及 XBOD 交易/积数专项，日志 `/tmp/xbod-quantum-snapshot-final.log`，结果待实际核对。

量子快照后续复验：首次测试夹具误用了 seedCurrentValue 三参数重载（其第一个参数为 groupId，并非属性），导致实时账户未初始化；修正为显式 groupId/attributeId/objectId 后，`/tmp/xbod-quantum-snapshot-final-v2.log` BUILD SUCCESS。运行库 5 项及 testing 的 XBOD 10 项通过，共 15 项。量子投影保留显式快照内的历史余额，量子查询不进入该快照子树；普通实时关联仍取最新余额。XBOD 9 项交易测试及四组历史积数测试均通过。

## testing 完整回归及原分录科目证据

`mvn -pl :xbod-deposit-demo -am test '-Dtest=Xbod*Test' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS，70 项，失败/错误/跳过均零；日志 `/tmp/xbod-current-testing-full.log`。该次运行包含量子快照子树修复。

随后核对旧 storedLedgerEvidenceExampleRun 发现原分录科目被篡改的拒绝规则尚未迁移。新增 CashDepositAgreement.postingEvidence、SPP preserveDepositPostingEvidence 和 APP 集合 snapshot；实际分录与成交快照比对位于显式 checkOriginalDepositPostings。Java 测试只通过数据库故障注入篡改科目，不实现业务规则。专项日志 `/tmp/xbod-original-evidence-testing.log`，完成前不将新增规则计入上述 70 项证据。

原分录证据 testing 专项 BUILD SUCCESS：XbodOriginalPostingIntegrityTest 3 项、XbodTransactionTest 9 项，共 12 项。修改科目和金额返回 ORIGINAL_DEPOSIT_LEDGER_EVIDENCE_MISMATCH，缺失原分录返回 INVALID_ORIGINAL_DEPOSIT_POSTINGS；资金及原冲正标志未改变，也未保存反向分录。后续 develop 验收同时加入 XbodRepaymentTest，结果见 `/tmp/xbod-original-evidence-develop.log`。

原分录证据 develop 专项 BUILD SUCCESS：原分录完整性 3、交易 9、还本还息 8，共 20 项，失败/错误/跳过均零。覆盖 LOCAL 回滚、现金同日/跨日/Mode2 冲正、真实内部户偿还及旧小数偿还规则。日志 `/tmp/xbod-original-evidence-develop.log`。

## 失败处置自身故障

新增 XbodFailureDispositionTest，原业务服务故障之外使用 H2 触发器拒绝 CASH_FAILURES 插入。修复前两项均失败：主原因和回滚正确，但 ResultInfo.failure.suppressedCodes 为空，日志 `/tmp/xbod-secondary-failure-before.log`。通用 TransactionFailureHandling 现于 disposition 异常后更新返回失败事实，仍抛主异常；元数据更新自身失败也不覆盖主异常。现有框架测试增加返回信息断言。

`mvn -pl :xbod-deposit-demo -am test '-Dtest=TransactionFailureHandlingTest,XbodFailureDispositionTest' -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=develop` BUILD SUCCESS，框架 7、银行 2，共 9 项。日志 `/tmp/xbod-secondary-failure-develop.log`。testing 对应命令日志 `/tmp/xbod-secondary-failure-testing.log`，结果待核对。

testing 框架/银行专项共 9 项通过；新增明确恢复状态断言后 testing 两条整场景再次通过，日志 `/tmp/xbod-secondary-outcome-testing.log`：二次保存失败不覆盖原 RECOVERY_REQUIRED，也不会把 handled 改为 true。LOCAL 同断言复验日志 `/tmp/xbod-secondary-outcome-develop.log`。

LOCAL 同恢复状态断言复验两项通过：原 ROLLED_BACK 保留，二次故障可见、handled=false；与 testing 的 RECOVERY_REQUIRED 区分。所有本轮专项失败/错误/跳过均零。

## LOCAL 提交故障四阶段验收

新增 XbodCommitOutcomeTest 对生成 depositCash 在 JDBC beforeCommit、commitBefore、commitAfter、afterCommit 四个技术故障点注入失败。分别期待 ROLLED_BACK、UNKNOWN、UNKNOWN、COMMITTED，并从真实数据库核对前两种无成交/分录、后两种保留一笔成交及八条分录；不以异常本身推断是否成交。该测试仅适用 LOCAL，testing 的多阶段协调须另行验证。首次执行日志 `/tmp/xbod-commit-outcome.log`，结果待核对。

LOCAL 存入、冲正的八种提交故障组合通过：XbodCommitOutcomeTest 两项测试各包含四个独立数据库用例，失败/错误/跳过均零，日志 `/tmp/xbod-commit-outcome-both.log`。独立默认查询及物理表计数证明前两阶段没有本次合约/分录，后两阶段保留一笔及八条分录；资金变化与结果一致。此项不宣称已有提交未知自动恢复、远程重放消歧或分库提交恢复。

## 日累计生命周期与非法积数配置

`mvn -pl :xbod-deposit-demo -am test -Dtest=XbodDailyCashTest -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing` BUILD SUCCESS，2 项，失败/错误/跳过均零。日志 `/tmp/xbod-daily-testing.log`。三次真实存入及默认重查验证 300→600 的累计警告、次日重置为 100、明细累计与积数 600；normalUnit=0 在完整场景拒绝且物理成交/分录为空。未复制旧初始凭空余额。

旧三类 report setup 是测试证据汇编，按测试移出 SPP 的约定不作为生产场景恢复。逐业务证据、授权续办/持久化审计未完成项和量子模型差异已写入 legacy-entry-migration，不能把拆分的专项宣称为旧报告逐字段等价。

## 准备后的冲正与介入存款

新增 XbodStaleReversalTest，通过 APP 技术调用日志的测试监听器，在 prepareCashReversalPostings 前暂停已查询并校验的冲正；随后执行真实存入 5，再放行冲正。预期旧普通事实提交冲突且资金恢复为 105，原交易未标记冲正；全新查询后重试成功，余额为 5，介入交易八条分录保留。测试仅做技术调度和调用生成场景，不构造 Java 银行业务。首次 testing 日志 `/tmp/xbod-stale-reversal-testing.log`，结果待核对。

XbodStaleReversalTest 在 testing、develop 两套配置均 BUILD SUCCESS（各 1 项）；日志 `/tmp/xbod-stale-reversal-testing.log`、`/tmp/xbod-stale-reversal-develop.log`。精确控制查询之后、更新之前介入另一笔生成存入场景，验证旧冲正失败和新查询重试，未使用 sleep 或手写业务更新。该证据覆盖账户事实过期，不替代原合约自身并发变更测试。

## 原合约准备后被改动

XbodStaleReversalTest 新增技术故障：冲正查询完后，修改已存原合约 fee 及仓储修订标记，再放行。首次 testing 运行发现 PERSISTENCE_VERSION_CONFLICT 确实阻止覆盖，但普通 Saga 前序阶段已提交，故向调用方抛失败而不是 handled=true；最初按账户介入用例假定全部恢复的测试预期不成立。日志 `/tmp/xbod-changed-receipt-testing.log`。

修订验收保留严格事实：原合约 fee=1 未被覆盖、原成交未标记冲正、资金恢复 100；testing 必须报告 RECOVERY_REQUIRED/RECONCILIATION_REQUIRED/handled=false，不直接重试以掩盖普通残留。LOCAL 则要求完整回滚，恢复测试夹具后重查重试成功。此差异属于已知 KI-R04，不修改生产代码去伪称回滚成功。

原合约/账户过期专项完成：testing、develop 各 2 项通过（失败/错误/跳过均零），日志 `/tmp/xbod-changed-receipt-testing-v2.log`、`/tmp/xbod-changed-receipt-develop.log`。LOCAL 包含恢复夹具后成功重试；testing 原合约冲突明确保留待补偿结果。

## 冲正当前资格事实

新增 XbodCurrentEligibilityTest：成交后在数据库夹具将 AccountEligibility.status 设为 FROZEN，再以 ACTIVE 入口调用生成的 reverseCash，要求 EN111；改用 SA01116 不能绕过当前现金路径限制，要求 UNSUPPORTED_CASH_REVERSAL_PATH。独立查询验证资金、冻结状态、原成交标志及零冲正记录。此项不把普通属性查询变成全程状态锁，也不承诺阻止已通过检查的在途交易。testing 日志 `/tmp/xbod-current-eligibility.log`，结果待核对。

XbodCurrentEligibilityTest testing BUILD SUCCESS，1 项，失败/错误/跳过均零；日志 `/tmp/xbod-current-eligibility.log`。已查证当前资格来自默认数据库查询，不能由入口 ACTIVE 覆盖；冻结核心例外不会扩展现金场景的业务范围。

## 非零积数保存后的故障

XbodAccrualFailureTest 先真实存入 100，次日申请再存 50，并在 insertCashDepositAgreement 前注入失败（积数保存已执行）。testing 专项通过：资金恢复 100/-100，积数保留已提交的 100 和次日日期，返回 RECOVERY_REQUIRED/handled=false；失败处理记录可重查，仍只有原一笔合约及八条分录。不把普通积数恢复冒充为量子反交易的一部分。日志 `/tmp/xbod-nonzero-accrual-testing.log`。LOCAL 重试验证待 `/tmp/xbod-nonzero-accrual-develop.log` 结果。

非零积数 LOCAL 专项通过（1 项，零失败/错误/跳过），日志 `/tmp/xbod-nonzero-accrual-develop.log`：故障后积数仍零、日期保持原日，资金 100/-100；重试后余额 150、积数 100。两套配置对差异的断言均由真实持久化结果支持。

## 同流水并发冲正及原合约持久化完整性

XbodIdempotencyTest 新增同一远程请求方/流水并发 reverseCash，用真实存入准备原成交；要求最终同一冲正凭证和结果、资金归零、只有一个冲正合约及八条反向分录。RUNNING 允许当前技术协议 REQUEST_IN_PROGRESS，原调用完成后再取原结果，不在业务 SPP 加幂等。testing 类全量 7 项通过，日志 `/tmp/xbod-concurrent-reversal-idempotency.log`。

新增 XbodOriginalAgreementIntegrityTest：不存在的原凭证、数据库原合约 amount 被改为 999、原合约账户改为另一个已开户账户。直接修改物理表和对象仓储两种表示，验证默认查询后的原成交守恒/归属检查，资金不变且无冲正合约/反向分录。testing 日志 `/tmp/xbod-original-agreement-integrity.log`，结果待核对。

原合约完整性 testing BUILD SUCCESS，3 项，失败/错误/跳过均零。缺原合约返回 PARTICIPANT_NOT_IDENTIFIED；已存金额损坏返回 ORIGINAL_DEPOSIT_MOVEMENT_NOT_BALANCED；账户归属损坏返回 ORIGINAL_DEPOSIT_ACCOUNT_MISMATCH。日志 `/tmp/xbod-original-agreement-integrity.log`。

## 冲正合约插入前故障

XbodTransactionTest 新增 insertCashReversalAgreement 前技术故障验收，与已有反向分录故障共享资金、原成交标记及失败快照重查断言。要求冲正表无记录；LOCAL 完整回滚并允许新请求重试，testing 资金逆转但普通前序事实已提交，保留 RECOVERY_REQUIRED。testing 类全量日志 `/tmp/xbod-reversal-receipt-fault.log`，结果待核对。

冲正合约插入前故障完成：testing XbodTransactionTest 全类 10 项通过，LOCAL 对应方法 1 项通过，日志 `/tmp/xbod-reversal-receipt-fault.log`、`/tmp/xbod-reversal-receipt-local.log`。LOCAL 验证新请求重试成功；testing 原合约标记已提交而资金逆转，明确 RECOVERY_REQUIRED，不直接重试。

收口静态检查：src/main 无手写 Java；生产 SPP 无 try/catch/throw、Verification、context 及 transaction quantum/saga；PHY quantumStore 是部署配置，不作为 SPP 业务事务语法。git diff --check 通过。README 和设计页已移除过时回归次数及资金模型待决策描述，历史执行日志仍保留在验证文档。
# 当前干净回归补充（2026-10-13）

本轮 clean develop 联合回归在 appframe 失败：lang 366 项通过，appframe 628 项中 7 failures、3 errors，后续模块未执行。日志 `/tmp/xbod-final-joint-develop.log`。新增 QuantumRepositoryFacts.snapshotProperties 无条件访问可空 APP 表目录，破坏无目录的量子开户恢复路径。

已修复为无目录时返回空快照配置。QuantumOpeningRecoveryTest、DatabaseInitializationTest、QuantumParticipantSnapshotTest 共 12 项通过（`/tmp/xbod-snapshot-no-catalog.log`），覆盖无目录恢复与有目录历史快照。已重新启动完整 clean 联合回归（`/tmp/xbod-final-joint-develop-v2.log`）；本条记录时尚未完成。

## 当前源码干净联合回归通过（2026-10-13 18:36）

命令：`mvn -pl :xbod-deposit-demo,petstore-demo -am clean test -Dspp.environment=develop`。日志 `/tmp/xbod-final-joint-develop-v2.log`，BUILD SUCCESS，用时 9 分 6 秒。lang 366、appframe 628、generator 107、XBOD 86、Petstore 39，共 1,226 项，零失败、零错误、零跳过。该批次包含无 APP 表目录兼容修复、历史快照、内部收款户、原分录证据及所有已新增故障/并发测试。

已启动 testing 的 XBOD 全量验证，日志 `/tmp/xbod-final-testing.log`，此处暂不记录未完成结果。独立试算及其他明确未迁移范围仍以 completion-audit 和 known issues 为准。

## testing 全量回归通过（2026-10-13 18:41）

命令 `mvn -pl :xbod-deposit-demo -am test -Dtest=Xbod*Test -Dsurefire.failIfNoSpecifiedTests=false -Dspp.environment=testing`；日志 `/tmp/xbod-final-testing.log`。86 项，零失败、零错误、2 项跳过；跳过的是仅适用于 LOCAL 的 XbodCommitOutcomeTest 两个方法。该批次尚未包含随后新增的 previewCashReversal 场景，不能宣称验证了试算；试算另行生成与专项验收。

## 独立现金冲正试算专项（2026-10-13）

新增 SPP previewCashReversal，复用正式冲正前的查询、check 与 calculate，不含 transaction、量子更新或普通持久化调用。XbodReversalPreviewTest 在 develop/testing 各 2 项通过；日志 `/tmp/xbod-preview-develop.log`、`/tmp/xbod-preview-testing.log`。真实存入 100 后再存入 5，试算生成八条平衡候选分录，数据库余额仍为 105、原交易未冲正、冲正合约及分录表均为空；随后正式冲正保留后来存入的 5。缺原成交拒绝也无持久化副作用。该专项不声称覆盖旧通用部分退费候选。

## 打包和脚本启动验收

`mvn -pl :xbod-deposit-demo -am package -DskipTests -Dspp.environment=develop` 成功，日志 `/tmp/xbod-final-package.log`。使用 run-demo.sh web、跳过重复构建、回环端口 18089、独立 H2 内存库实际启动，POST openDepositAccount 成功创建零资金账户并返回开户参与者。最初省略整个参与者的请求被技术错误拒绝；补齐场景声明的六个参与者对象后成功，README 已提供完整 JSON。该验证不宣称入口会自动构造被省略的参与者。临时服务器已停止，未留下后台服务。
