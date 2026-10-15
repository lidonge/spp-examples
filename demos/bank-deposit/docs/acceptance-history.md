> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 历史验收记录

以下记录说明各阶段当时的证据和限制，不作为最新完成状态。最新核对见[验收核对](acceptance-audit.md)。

# 当前验收核对

**当前状态：全部demo手写Java已删除（主0、测试0），最终clean验收正在执行。** 完整存款及实际冲正报告的两JVM及导出事实已通过；最终必须验证最新逐案例来源增强、全部86源入口和公共JUnit，并检查全部旧class及嵌套class不存在。最终日志 `/tmp/spp-source-only-final-clean-validation.log`，终态前不认定Goal完成。

下表和后续旧阶段记录保留当时证据，旧测试名称不代表文件仍应保留。当前逐项源替代见 [覆盖责任](source-example-coverage.md)、[重构记录](source-only-refactoring.md) 和 [报告迁移](source-report-migration.md)。最终仍须全手写Java为零、旧class不存在、全部源入口通过新的clean verify。

本表按 requirements-and-functions.md 的第一批三类交易及 P1–P4 核对，不将组件完成改称完整交易完成。测试数量只说明已执行范围，不能替代下面各项的证据。

| 要求 | 当前可检查证据 | 判定及缺口 |
| --- | --- | --- |
| 独立子项目，先文档后实施 | 根 pom 的模块项、模块 pom、需求/功能/路径/比较/决策/源码映射，run-demo.sh | 已建立；各阶段记录保留当时状态，不能用早期未实现说明覆盖最新实现 |
| 普通/呆账/核销偿还及余额关系 | DepositKernelTest、DepositReversalAmountsTest、真实生成 cboddeposit 服务及模型 | 所选计算已验证；源码公式与黄金运行值分开，原 COBOL 未执行 |
| 数字分层及三位金额 | PHY double as BigDecimal、三位数学及 JDBC 成交测试、显式业务计息/收费取整 | 已验证所选表示和输入；日元遗留检查及 PIC 截断等不确定边界已登记，不能宣称全币种兼容 |
| 共享受理/产品/授权/警示 | bankAdmissionRulesExampleRun / cashAccountControlExampleRun（已替代删除旧测试）、bankQualificationRulesExampleRun / bankWarningCashExampleRun / bankRejectedCashExampleRun（已替代删除银行资格旧测试）、NormalCashDepositTest | 所选源路径子集已运行；实际银行查询/权限和完整多重非法消息优先级未取得或未实现 |
| 普通/协定/透支积数 | bankCalendarExampleRun（已替代删除 BankCalendarTest）、agreementProductExampleRun（已替代删除 AgreementProductTest）、datedAgreementExampleRun（已替代删除 DatedAgreementTest）、depositAccrualRulesExampleRun / depositAccrualCashExampleRun / depositAccrualInvalidExampleRun / depositAccrualWriteFailureExampleRun（已替代删除 DepositAccrualTest），源 CashAccountRecord/CashDepositTrade | 已与存入账务共同保存；协议读取/禁用和已登记源调用差异仍未覆盖 |
| 收费及业务分录 | DepositFeeTest、DepositPostingTest、实际 deposit_ledger、CLI 独立预期 | demo 规则已验证；ART/实际费率为不可获取配置的明确 fixture，不把它扩展成必须生产部署的要求 |
| 三类存入从查询到提交 | NormalCashDeposit、DepositDemoMain 十个案例、DepositDemoReportTest | 已执行一般、普通/呆账和精确金额，含受理/授权/收费/积数/账务及当前事实 |
| 存入失败、重试及并发 | JdbcDepositStoreTest、NormalCashDepositTest，账户/事实/分录/审计断言 | 已验证本地 JDBC 共同提交；正常关闭重开和进程内故障不等于实际崩溃/网络实测 |
| 原交易查询、核心冲正资格和反向分量 | DepositReversalPreparationTest、DepositReversalEligibilityTest，生成原子及场景 | 已验证真实原成交和当前资格；正常通存与冲正路径分别处理，不以版本代替业务资格 |
| 原分录驱动的反向账务及退费输入 | prepareRecordedDepositReversalPostings、实际原账簿及反向候选测试 | 已验证六类核心逆向及显式退费范围；较早组件输入保留；正式现金入口按 XBOD 原 KBN 实际收费退费 |
| 冲正金融组件实际提交、重复与并发 | JdbcDepositReversalStoreTest，deposit_reversal/ledger、原记录关联、文件重开 | 已有实际金融组件成交及故障证据；目前 fixture 没有正式现金积数/资格事实，不是完整现金冲正 |
| 完整三类现金冲正 | CashDepositReversal、CashDepositReversalTest、CashReversalDemo 及实际报告 | 所选账户模型路径已连接资格、日累计/明细/日期、积数和反向分录共同提交；外围额度和打印字段仍明确排除 |
| 跨日期冲正 | 现金跨日端到端、原最新/后续明细日期、24 小时模式、日累计归零、EN097 及实际报告 | 已按 XBOD 有效源码验证所选模型：普通积数减原追溯分量、不重算后续历史，透支日数保留 |
| 完整冲正退费政策 | selectXbodCashReversalFee、原 KSAFEE0 5500、实际现金冲正收费分录 | 已连接柜台现金路径，退原实际费用，不重新查费率 |
| 量子类反交易保留后续影响 | 金融逆分量及提交测试、Saga 独立后续存入案例 | 已验证选定金融分量；不扩展为任意数字字段或任意非量子更新可逆 |
| 非量子依赖及补偿 | default-reversal-design.md、rollback-reversal-compensation.md | 分类已确认；通用依赖跟踪/补偿未实现。首批没有开户反交易，不能把范围外生命周期加入完成要求，但必须保留能力边界 |
| 事务模式及恢复比较 | JDBC 回滚测试、原生 Saga 金融绑定和持久事件测试，方案比较文档 | 本地共同提交及显式业务恢复有证据；现已配置 quantumStore、生成 SPP transaction，现金净余额与对手方量子记录加入同一个 JDBC 连接；这不是跨库量子部署。跨进程 Saga 重建/自动扫描也尚无证据 |
| 原 COBOL 等价证据与限制 | source-map.md、各 source 文档、报告标记 cobolExecuted=false/bankConfigurationObtained=false | 已明确源码推导、数学目标、fixture 和遗留差异；未取得原运行时，不宣称黄金等价 |
| 传统方案比较 | spp-vs-cobol-java.md 各阶段同契约对照 | 已总结职责、收益和代价；没有性能、开发工时或生产成本实测结论 |

## 必须保持的完成门槛

本轮已补齐所选账户模型的现金冲正、重复及跨日链路，新增量子属性、生成事务、同连接量子记录与回滚。最新完整回归 934 项通过（lang 255、appframe 445、generator 91、demo 143），无失败/错误/跳过。CLI 实际生成 4 笔现金冲正、32 条反向分录及存入/冲正合计 20 条量子记录，输出见 cash-reversal-report 和 quantum-report。

该证据覆盖本项目明确选择的模型与 fixture。当前仍保留原 COBOL 未运行、真实 ART/费率未取得、外围机构额度/打印字段未接入、跨进程 Saga 恢复和跨库量子服务未实现等限制。通用 quantum boundary 反向不代替银行 CashDepositReversal；原存入阶段 report.json 的 goalComplete=false 是该阶段快照，不把它升级为整个原系统等价证明。

生产部署、全银行产品、转账/托收、所有事务后端和通用生命周期反交易不是第一批范围；相关能力缺口必须如实保留，但不随实现过程无限加入本 Goal 的必做范围。量子/Saga 等概念在所选资源范围内说明和验证，不以引用通用运行库测试代替银行集成证据。


## 当前纯源语言验收的增量证据

空 catch 生成缺陷修复后，十八个 APP 源入口均真实执行通过；此前四个入口的假阳性结论已经撤回并重跑。99n 验证分录写入后故障的实际存储撤销、独立失败审计和原请求重试；99o 验证三十组日期及两组利息单位计算，替代删除旧日历 Java 测试。当前仍有十四个主 Java 和二十个测试 Java 待迁移，不能宣布纯源实现完成；全部从空目录生成的最终责任仍见 source-language-only.md。


内核和协定增量：99p/99q 的源入口已通过，删除对应两个 Java 测试；剩余手写主 Java 十四个、测试 Java 十八个。内核覆盖全部原十六组参数和输入不变性，协定覆盖全部原六项方法的十七组独立数据与逐槽输出。删除后的干净构建已通过：989 项回归及 20 个源入口全部成功，并确认三个已迁移旧测试 class 不存在。不以旧测试数量作为源验收指标。


日期窗口、控制与准入又删除三份旧 Java 测试；99r/99s/99t 的独立预期真实通过，clean verify 回归 969 项及源入口 23 个分别全部成功，六份已迁移测试 class 已确认不存在。当前手写库存为主 Java 十四个、测试 Java 十五个；未覆盖项与全部删除责任仍在 source-example-coverage.md 跟踪。


银行资格与现金政策又删除两份旧测试：五十四组资格事实、原成交提示重放、两种无更新拒绝及八组 XBOD 日期/费用政策均实际通过。clean verify 完成 956 项回归与 27 个源入口，八份已替代测试 class 确认不存在。当前剩余手写主 Java 十四个、测试 Java 十三个，整体验收仍未完成。


收费与金融反向再删除两份旧测试；真实仓储费率的十六组收费及当前账上的十组反向金额独立预期已通过。clean verify 完成 944 项回归与 29 个源入口，十份已替代测试 class 确认不存在。当前主 Java 十四个、测试 Java 十一个，整体验收继续按源语言责任迁移。


## 积数与事务结果证据的纯源阶段验收

2026-10-08 的 clean verify：lang 290、appframe 494、generator 101、剩余旧 demo 66，共 951 项 JUnit 全部通过无跳过；APP 声明的 34 个入口另外全部通过。新增四个积数入口承接旧 DepositAccrualTest 六项责任，原测试文件已删除，累计十一份旧测试 class 均无残留。

通用结果证据实测提交前成功回滚、提交确认失败前后两种实际效果、回滚失败、已提交清理失败、多资源部分提交、同资源加入、恢复失败与原异常保留。源 99c 决定银行审计事件，99zb 的七组配对事实验证分类，但不以 fixture 构造替代真实物理故障。银行完整提交点故障/结果核对、其余冲正/恢复/报告和 Java 全量删除尚未验收，当前仍有主 Java 14、测试 Java 10。


核心冲正资格阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 290、appframe 494、generator 101、剩余旧 demo 62，共 947 项 JUnit 全部通过无跳过；36 个 APP 源入口另行全部通过。十二份已替代旧测试的 class（含嵌套类）全部不存在。新的核心资格和当前事实案例均在清空 target 后生成执行；当前手写库存主 Java 14、测试 Java 9，整体纯源要求尚未满足，Goal 继续活动。

只读金融/分录准备的其余八项责任、实际存储删除/证据破坏、提交点和结果核对、并发、Saga/补偿与报告仍继续实施。此次没有新增 demo Java，也没有把银行查询或资格逻辑迁入公共 Java 运行库。
