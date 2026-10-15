> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 实施路径

## 2026-10-08 路径修订

重构 goal 已启动，阶段记录见 [纯源语言重构实施](source-only-refactoring.md)。当前需先完成 [纯源语言迁移](source-language-only.md)：SPP 明确完整事务边界和模式，补齐场景控制与查询/更新生成能力，再生成全部执行及验收代码，移除 demo 手写 Java。历史阶段记录仅保留行为证据，不代表满足新的实现约束。

## 顺序与交付

1. 建立需求、决策、源码映射和比较文档，创建独立 Maven 模块。将已有计算原型升级为完整生成服务与场景执行，保留原型证据。
2. P1：将源码边界整理为案例，扩大三位利息及币种输入。对隐式截断和不确定分支先获得迁移目标，再实施显式规则或物理兼容；补独立参考结果。
3. P2：逐条追踪账户资格、产品限制、授权、日历/计息和收费。先定义角色契约与结果，再实现所选子集，加入来源及待确认配置。若当前场景不能表达授权续接或校验作用域，记录并补设计与实现，不用 APP 隐藏业务判断。
4. P3：追踪金额分类与记账规则，定义资金来源和分录，再加入查询/更新实现、持久化、日志、幂等和版本冲突。验证生成场景、业务守恒及事务故障；不能只用两个余额的技术转移代替银行账务。
5. P4：追踪 KBN 原日志及冲正段，实现业务冲正。使用原成交分量，验证后续变动、重复冲正、跨日积数、原记录状态和反向分录。框架回滚另测。
6. 汇总可执行案例、证据等级、传统方案对比及未覆盖范围；若修改共享编译器/运行库，完成对应回归。用户要求提交时再提交上传。

## 目录与运行

`src/main/spp` 保存业务、APP、PHY 源；不得在 `src/main/java` 或 `src/test/java` 手写 Java，当前文件均为待迁移违规项；`docs` 保存需求、路径、比较与决策；`target` 保存完整生成源码、Surefire 和后续案例报告。

统一入口为 `mvn -pl :xbod-deposit-demo -am test`。每阶段增加成功、拒绝及边界验收，文档同步列出已执行命令和结果。P3/P4 阶段补命令行交易演示与机器可读报告。

## 当前进度

- Goal 已启动；需求和路线已建立。
- P1 完整生成基线已建立，P2 已加入受理、账户控制、授权、日历、协定分档及收费子集，P3 已验证一般现金 demo、普通/协定/透支积数到 JDBC 共同提交、授权重验、原请求重试及审计，并可运行命令行文件数据库及报告；完整资格、剩余协议/积数分支及 P4 尚未完成。以下分阶段记录保留各次验收时的状态。
- 本项目 14 个源码推导案例均通过真实 OpenAPI 模型、生成原子服务及串行场景执行；断言九项输出、输入快照不变，以及负金额拒绝时未生成计划。仍没有运行原 COBOL。
- 用户已确认业务语义优先，以及首批现金/透支存入与对应冲正。未确认具体规则先记录，不猜测银行业务政策。

## 总体验收条件

四个重点都有可执行证据和明确覆盖边界；所选交易可从请求运行到持久化及冲正；拒绝、待授权、重试、失败恢复和并发有断言；业务政策仍在 SPP 或声明的共享业务库，部署与存储在 APP/PHY；每项规则有来源，未验证的等价性没有被宣称。确认业务决策及材料不足时仍可推进其他独立部分，但不得把模拟配置当作已迁移的银行配置。

## 本轮验收（2026-10-07）

`mvn -pl :xbod-deposit-demo,business-showcase -am test` 通过：语言 255、运行库 445、生成器 91、既有展示 24、存款 demo 14，共 829 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-demo-regression.log`。

完整生成暴露并修复局部 boolean 类型错误附加模型包名的问题，同时覆盖 String 局部类型并增加语义回归。已有算术原型的语句执行无法发现此类完整生成错误，这也是本项目保留生成及场景执行测试的原因。

下一步扩大 P1 的数字边界并实现 P2 所选规则契约；P3/P4 仍待实施，Goal 保持活动。业务冲正自动化方向及已存在的量子反交易接口已登记到决策文档。

## 受理与授权规则增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 24，共 815 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-rules.log`。10 项新增测试含多个边界断言；数值阈值为明确的 demo fixture，并非银行实际参数。

新增业务层服务覆盖前台现金正金额与当前起息日、临时户期限、销户、首次/初期存入上下限、普通交易余额上限，以及现金日累计警示、一般 A/B 授权、特定美元路径与渠道/交易例外。授权评估返回 PendingAuthorization/Warning/Ready，警示可继续；执行门槛为独立 check。授权重试重新评估当前阈值，尚未验证数据库版本绑定和持久化续接。

计息单位服务验证显式单位取整及积数；业务日期有效性、银行日历、CSAQRY1 完整资格、分档和费用尚未迁入，不能宣称 P2 已完成。用户要求先讨论冲正与回滚概念及实现方案；相关新增实现暂不推进，Goal 保持活动。

## 计息日历与数字边界增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 30，共 821 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-calendar.log`。

新增两个三位利息数学案例和四项日历测试（内部覆盖多组日期）：真实生成的场景调用 APP 日期解码服务，再由 SPP 决定 ACT/360365/360360 天数；验证闰年、世纪年、月末、跨年、零期间、非法日期、倒序期间，以及日期结果驱动单位积数。取整后的除法还验证 unit=3 的非终止中间商可由显式业务舍入正确处理。非终止商本身没有被要求以 BigDecimal 精确表示。

源码常量确认 `C-CM-DT-GT-PRDH` 是功能 O（算头不算尾），不是 H（不算头尾）。期间非法与日期非法错误按实际常量迁移，未使用头部旧说明。未运行原 COBOL，结果依然为源分支推导或明确的业务数学预期。

当前适配器的反交易证据和差异已写入 `default-reversal-design.md`。普通赋值/状态默认还原规则用户选择继续讨论，未实现。P2 的完整账户资格、分档、收费，以及 P3/P4 仍未完成，Goal 保持活动。

## 协定分档计息增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 36，共 827 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-agreement.log`。

新增真实生成的 calculateAgreementProduct 服务和六项测试：保留五个原槽位并从 5 到 1 遍历；模式 2 逐档分配超额，模式 1 按命中槽位归入全额，未指定模式按币种选择。验证严格/非严格阈值区别、显式模式覆盖币种默认、停用/零重叠期间、低于起点、输入契约错误，以及逐档量化不能代数合并的边界。输入金额快照保持不变，剩余量与各档积数进入输出。

本增量使用已给出的普通期间和协定重叠期间天数，尚未迁入生效/取消日期裁剪；五槽非负阈值为当前服务输入契约，缺失槽位及原负阈值禁用标志仍需接入明确的读取/映射。积数各档分别取整可能导致各档和普通积数之和小于原总积数，测试按源分支保留这种边界；不能拿积数的这种差异替代货币记账守恒规则。原 COBOL 未执行，依旧不宣称黄金等价。

用户进一步确认量子/非量子反交易分类：量子逆操作不覆盖后续业务；非量子操作必须检查后续业务依赖。草案已据此替换单纯按字段版本还原的建议。具体反交易及依赖机制仍在讨论，未实现；Goal 保持活动。

## 普通现金存入收费增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 41，共 832 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-fee.log`。

新增 prepareDepositFee 真实生成场景，调用输入校验、SPP 地区/机构分类、APP 客户费率查询、SPP 收费计算。五项测试覆盖范围及收费代码、客户折扣、舍入后加固定费、上下限、零最高费、柜员渠道与缺费率/错费率/负金额错误。查询前拒绝负金额；当前只形成费用计划，没有扣款和收费记账。

仅迁入普通存款收款账户、付款账户为空的现金存入路径。多币种账户、双边费用及 KCMFEE0 分支明确未支持；参数为 demo fixture。已把算法与来源写入 source-map，未执行原 COBOL。P2 的完整资格及协定日期裁剪仍待完成，P3/P4 尚未实施，Goal 保持活动。

## 协定日期到积数场景增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 46，共 837 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-dated-agreement.log`。

新增 prepareAgreementWindow 与 calculateDatedAgreement：真实生成场景串联原日期解码、普通期间、业务重叠窗口、嵌套日历场景和分档算法。五项新增测试覆盖生效/取消日期裁剪、无取消日、未来/缺生效日、提前取消、零窗口和实际无效日期。缺日期以 0 表达原接口的空白；没有有效重叠时按有效原日期创建零期间，避免让 APP 决定是否调用业务算法。AgreementPolicy.enabled 在计划计算中成为本次有效性结果，应为本次请求的独立参与者，不能复用为跨请求的持久产品配置。

当前日期到积数子集已执行，银行协议查询、负阈值禁用标志映射及账户完整资格仍待接入。未执行原 COBOL。下一阶段继续完善所选路径资格，并追踪记账规则/配置及定义持久化更新计划，P3/P4 未完成，Goal 保持活动。

## 一般现金存入账户控制增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 51，共 842 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-account-control.log`。

新增前台账户控制及核心销户/产品检查，并在 assessNormalCashDeposit 真实生成场景中串联输入、前台控制、产品资格、核心事实和授权评估。五项新增测试含机构控制、只付不收、锁定、冻结状态与冻结金额区别、销户记录、房易安产品不适用于一般现金存入，以及拒绝时不继续生成授权结果。现有输入/产品服务仍可单独复用。

未完成 CSAQRY1 的跨机构通存、卡/存折挂失提示及其他例外；本次正常现金路径的错误案例分别验证单项原因，不能宣称任意多重非法状态下的消息优先级与原 COBOL 完全一致。记账追踪确认 GCCBAAR 依赖运行时装载的 ART/SMT/SMP 规则，金额分类及配置证据边界记录在 posting-plan-source.md。尚未持久化账户/账簿，P3/P4 未完成，Goal 保持活动。

## 记账计划增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 57，共 848 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-posting-plan.log`。

新增 classifyDepositAccounting/checkDepositAccounting 和 calculateDepositPostings/checkDepositPostings，并由 prepareDepositPostings 真实生成场景串联核心计算。六项新增测试覆盖现金及独立收费、普通与呆账分配差异、旧存款参与偿还、核心零金额、三位小数、配置错误和伪造汇总。科目为 DEMO 前缀的展示配置，未取得原 ART 配置，也没有原 COBOL 执行值。当前已验证的是计划，持久化及完整受理到成交链路仍待验收。

## JDBC 共同提交增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 63，共 854 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-jdbc.log`。

新增 SPP prepareDepositAccountUpdate，将已检查计划转为独立账户快照，偿还运算保持在业务层。JdbcDepositStore 在一个 JDBC 本地事务内写入账户及债务状态、原成交事实和八条分录；账户版本与原快照条件阻止旧计划覆盖新成交。同一成交标识及相同完整 Prepared 命令重放返回原结果，标识复用但事实改变则拒绝。

六项新增真实 H2 测试验证三位小数保存、共同提交、适配器重新读取、重复命令、旧版本和伪造快照、账户更新后/部分分录后/提交前故障、竞争交易及并发相同命令。JSON 和金额字符串避免引入数据库小数位截断。本次为演示 schema 和内存 H2，未验证数据库进程重启、磁盘故障或跨资源事务；也不能宣称量子协调器或 Saga 已通过这些测试。

当前 store 是接收已生成并校验计划的物理接口，不是完整请求入口。重放以完整 Prepared 命令为准，尚未接入“仅按原请求重试”的入口协议；受理/授权事实重验、日累计与计息更新、失败审计、命令行案例报告仍待完成。P4 按用户要求继续讨论具体机制，未开始新增实现。Goal 保持活动。

## 一般现金请求到成交增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 72，共 863 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-full-entry.log`。

新增 prepareNormalCashDeposit 生成场景、prepareDepositEligibilityUpdate 业务更新计划及 NormalCashDeposit APP 入口。账户资格、控制、产品政策和收费身份通过 JDBC 一起读取；新资格与金额状态一起受版本和快照条件保护、一起提交。业务层形成每日现金累计、净余额及配置的明细计数；物理层保存请求身份和原成交结果。服务装配暴露生成场景构造时即查依赖的问题，demo 已按依赖顺序注册；未修改通用生成器。

九项新增测试验证普通/呆账/核销存入、警示继续、收费与八条分录、待授权无业务更新、授权升级及当前阈值/账户重验、原请求在后续交易及营业日变化后重放、金额格式归一、每日累计与换日、控制/收费查询失败、适配器重建后续接和整笔入口并发重复提交。

具体契约及来源见 cash-execution-contract.md。请求身份保存不等于完整审批或失败审计；授权签发未实现，外部配置资源的并发变更尚未纳入共同版本保证。数据库进程重启/应答丢失未注入。计息积数落地、银行完整资格及真实配置、失败审计、命令行报告和 P4 仍待完成，Goal 保持活动。

## 审计与失败结果增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 76，共 867 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-audit.log`。

新增 deposit_audit 的尝试身份、事件、代码和载荷查询。成功审计与业务记录共同提交；失败时先回滚，再经独立连接追加失败审计；APP 保存拒绝、待授权及重放事件。错误在 commit 前、commit 调用期间或 commit 已返回成功之后，分别按确定回滚、结果未知及已提交返回失败处理；原业务异常及审计异常均保留，不自动发起冲正或补偿。

四项新增 store 测试验证部分分录失败的审计保留和重试历史、成功后的返回失败、代理注入 commit 异常、审计不可用。既有九项入口测试补充拒绝、收费查询失败、待授权与重放的审计断言。故障模型为进程内回调/JDBC 代理，并非实际网络断线或数据库崩溃；审计存储不可用时异常可观察，不宣称仍能保证失败审计已写入。

证据及边界见 audit-and-failure.md。积数落地、完整资格与真实银行配置、命令行案例报告及 P4 仍待完成，Goal 保持活动。

## 文件数据库与交易报告增量（2026-10-07）

`./demos/bank-deposit/run-demo.sh` 通过。脚本执行 `mvn -pl :xbod-deposit-demo -am package`，语言 255、运行库 445、生成器 91、demo 77，共 868 项，0 失败、0 错误、0 跳过；随后 Java 主程序成功完成 10 个案例、6 笔成交和 48 条分录。日志 `/tmp/spp-xbod-report.log`。

最近运行目录为 `target/demo-report/run-e0d3bbed-b1ef-45ba-adb6-39b5896ffb9c/`，含 report.json、report.md 和 deposit.mv.db。每次新建运行目录，不重用旧演示数据库。报告保存独立预期与实际查询快照、原成交事实、实际分录和尝试审计；主程序检验预期状态/错误/净余额/版本、分录与计划一致及守恒。原请求重放引用旧成交，单独保存当前快照。

新增 DepositDemoReportTest 验证导出内容、普通/呆账偿还与三位小数预期、待授权/重放/拒绝结果，并在关闭文件数据库后重新打开，读取账户、原成交、审计和 48 条分录。该证据是正常关闭重开，不是进程崩溃测试。

运行说明见 running-demo.md。报告明确列出尚未实现的积数落地、完整所选资格、冲正及对应恢复验证，并将未取得的银行配置/黄金运行值列为证据限制；goalComplete 为 false。Goal 保持活动。

## 积数共同提交增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 83，共 874 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-accrual.log`。

新增 prepareDepositAccrual 和 prepareCashDepositWithAccrual 生成场景，使用交易前金额及独立积数日计算普通/五档协定、透支本金和透支息积数，再形成累计快照。AccountFacts.accrual 与金额/资格/分录共同提交；Prepared.accrual 保存原起止日期、天数和实际分量，为跨日冲正保留依据。未把公式放进 JDBC 或 Java 模型分配器。

六项新增测试验证不同日历、单位及非终止中间商、原计数条件、原输入不变、期内/同日/重放、非法配置拒绝，以及金额和积数写入后账簿失败的共同回滚。文件报告测试增加积数关闭重开断言。

使用本次编译的 Java 主程序再次执行演示，报告在 `target/demo-report/run-dbbecdf1-8ea4-4b08-a4bd-a84b58a02244/`，日志 `/tmp/spp-xbod-accrual-demo.log`；下一营业日普通积数为交易前 2200 × 1，而非新余额 2300，原期间为 20261007 到 20261008。CLI 所有账户均有积数事实。

来源及源调用条件差异见 accrual-execution.md。协议游标/负阈值禁用、原计息标志组合、模式 1 高档保存条件及回溯起息仍有未验证边界；不宣称原银行全流程等价。冲正及所需资格/跨日调整尚未实现，Goal 保持活动。

## 金融反向计划增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 90，共 881 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-reversal-amounts.log`。

新增 describeOriginalDepositMovement 和 prepareDepositReversalAmounts，取得原实际金融分量并对当前账户反向计算，使用当前冻结和授权重新推导可用余额，不恢复旧快照或重新按当前贷款状态分配。源码容量 ES020、新计息金额 EN249 和恢复债务后的 EN177 作为共享资格服务。透支敞口按实际 delta 逆转与原增加偿还本金的差异已单独登记。

七项新增真实生成场景测试验证存入后消费/再存入的影响保留、普通/呆账原分量、精确三位金额、敞口原截断、资格拒绝及伪造分量拒绝。目前仅形成金融计划，未执行新冲正成交。

已向用户提出跨日计息及退费政策选择；金额计划不依赖这些选择，可以先验证。原成交查询、独立冲正身份、重复冲正互斥、跨日/费用/分录与审计共同提交仍待实施，见 reversal-financial-plan.md。Goal 保持活动。

## 通存与挂失提示增量（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 98，共 889 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-bank-qualification.log`，各模块 Surefire XML 已核对。

新增账户/操作事实角色、通存校验、独立 WN200/WN201 提示及两个完整现金资格场景。银行条件在 SPP，APP 提供解码事实并保存成功成交依据；原请求重放保留原提示。八项测试验证普通及受限子类不同的例外作用域、关系和柜员边界、缺失事实、实际现金/积数/分录共同提交及拒绝。规则来源、非银行自定义错误和多重错误优先级限制见 bank-qualification.md。

使用本次编译的主程序完成 10 个演示案例，文件报告在 `target/demo-report/run-00460a5d-a192-4c67-9f5a-e303421585a5/`，日志 `/tmp/spp-xbod-bank-demo.log`。原成交载荷加入银行账户/操作事实和提示，原积数仍与账务共同保存。真实银行查询及配置、完整资格边界、剩余协议分支与完整冲正仍待完善，Goal 保持活动。

用户确认的反交易分类已写入 default-reversal-design.md：量子类使用原实际 delta，对当前状态执行逆操作；非量子类先判定后续业务依赖。版本保护不能替代该依赖判断。金额计划已有验证，通用非量子机制未实现；跨日和退费政策仍待明确，不能自动推断。

文件报告测试另补银行事实导出及关闭重开后的读取断言；`mvn -pl :xbod-deposit-demo -am -Dtest=DepositDemoReportTest -Dsurefire.failIfNoSpecifiedTests=false test` 通过（1 项针对性测试，0 失败/错误/跳过），日志 `/tmp/spp-xbod-bank-report.log`。该证据仅为正常关闭重开，不扩大为进程崩溃恢复。

## 真实成交到金融反向计划（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 102，共 893 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-recorded-reversal.log`，Surefire XML 已核对。

新增 APP DepositReversalPreparation 读取成功原成交及当前账户，调用 prepareRecordedDepositReversal。checkOriginalDepositSettlement 校验存储中的前后金额与原计划相符，然后提取实际分量并计算候选逆操作。查询只按原成交的账户身份读取，不接受另填原分量；当前版本及容量快照随结果返回。

四项新增测试使用实际生成场景和 JDBC 成交，覆盖原现金存入后仍保留后续成交、普通/呆账及三位金额、无成功成交或容量不足拒绝、不一致原成交拒绝。准备过程的账户、原记录、分录、请求及审计均不变。该检查是 demo 事实契约，不是 KBN 格式适配、防篡改或完整冲正成交；规则及限制见 reversal-financial-plan.md。

独立新冲正身份、原记录关联和重复互斥、整体资格及非量子后续依赖、跨日/收费政策和分录/审计共同提交仍待实施。只读准备允许读取跨日原成交，不等于跨日冲正获准；不会退款或改积数。Goal 保持活动。

## 反向分录及显式退费决定（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 106，共 897 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-reversal-postings.log`。

新增查询实际原账簿、checkRecordedDepositLedger、assessOriginalDepositPostingLines、checkDepositFeeRefund 及 prepareRecordedDepositReversalPostings。反向计划核对原成交与实际分录，验证金额分类及原费，再反转六项核心方向；收费两项必须提供显式退费决定，范围为零至原实际收费。SPP 承接条件、运算和汇总，APP/PHY 只查询及分配结果。初次编译发现汇总服务误声明 check，已改为 calculate，保留 check 不能写业务属性的语言约束。

四项增补测试覆盖零/部分/全额的明确演示输入、原方向与精确分量、不一致及不完整账簿拒绝、缺少/负数/超额退费拒绝。准备不更新账务或审计；测试输入不代表已选择银行退费政策。

演示报告加入五个 reversalCandidates，均标记 executed=false；展示现金不退/退原费两种不同输入和普通/呆账/三位偿还候选。报告与准备测试针对性回归：`mvn -pl :xbod-deposit-demo -am -Dtest=DepositDemoReportTest,DepositReversalPreparationTest -Dsurefire.failIfNoSpecifiedTests=false test` 通过（9 项，0 失败/错误/跳过），日志 `/tmp/spp-xbod-reversal-report.log`。原 10 个案例、6 笔成交、48 条实际分录保持原结果。

完整冲正提交、重复互斥、日累计及跨日计息政策、非量子依赖和对应恢复仍未完成。退费是显式业务决定，不提供技术默认；跨日金融候选不代表整笔业务可以冲正。Goal 保持活动。

本次编译的主程序运行及报告验证通过，目录 `target/demo-report/run-42989940-e59f-43c9-8907-a1a670107680/`，日志 `/tmp/spp-xbod-reversal-demo.log`。实际成交仍为 6 笔、48 条分录；另有 5 个未执行候选，各 8 条平衡反向分录。现金两种退费输入对应分录汇总 600/602，核心反向后净余额均为 1700，不修改当前余额 2300。

## 金融组件的实际冲正提交（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 115，共 906 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-reversal-store.log`。补充审计及身份检查后，`mvn -pl :xbod-deposit-demo -am -Dtest=JdbcDepositReversalStoreTest -Dsurefire.failIfNoSpecifiedTests=false test` 通过（12 项，0 失败/错误/跳过），日志 `/tmp/spp-xbod-reversal-store-audit.log`；当前 Surefire 共 909 项通过，其中 demo 118 项。

新增 prepareDepositReversalAccountUpdate 和 JdbcDepositReversalStore。原存入日志保留，新冲正与原交易唯一关联，反向分录、新账户及成功审计共同提交。原成交锁和唯一约束处理同原交易竞争，版本及快照条件防止覆盖当前计划之后的普通成交；稳定请求身份支撑重放，不要求当前账户仍在原冲正版本。

十二项物理测试使用真实生成场景及 H2，验证 200→存入10→再存入20→当前230→反原10后220，保留后续业务；重复及并发、版本冲突重试、原关联/账户/部分分录/提交前故障、已提交返回失败、原 Receipt 改变、身份改变及审计不可用均有执行证据。测试使用无产品/积数事实及零原费/零退费的明确金融组件 fixture，不为正式现金入口推断业务政策。

提交契约及两个账簿的查询范围见 reversal-submission.md。正式现金冲正入口、整体资格及非量子依赖、日累计/积数更新、跨日和退费政策以及量子/Saga 验收仍未完成。已提出两项业务决策，跨日生效方式和 demo 退费规则需明确；独立技术提交先完成，不将候选或组件成果改称完整 P4。Goal 保持活动。

## 核心冲正资格及文件持久化（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 124，共 915 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-reversal-eligibility.log`，Surefire XML 已核对。

新增 checkCoreDepositReversalEligibility/assessCoreDepositReversalEligibility 及 prepareCoreQualified 查询入口，迁入 KSADEP0:603 的 EO082、CSAQRY1:5000/9751/9753 的 EN113/EN111 和 SA01116 冻结例外，并复用挂失提示。冲正路径不调用正常 9709 通存，前台机构控制另有调用范围，不能直接套用整个正常受理组。

四项新增资格测试验证独立错误/例外、警示与正常范围区别、原成交后当前控制事实、前台/核心分工。物理提交测试新增正常关闭文件 H2 后重开，读取原及反向成交、唯一关联、实际八槽分录、成功审计及请求身份，并在后续存入后重放；另验证原 Receipt 更换属于身份拒绝而非审计故障。ledger(reversalId) 查询实际反向账簿，未从载荷重新生成。

源规则与限制见 bank-qualification.md、reversal-submission.md。正式现金冲正的全部事实更新、待确认跨日/退费政策及量子/Saga 验收仍未完成；本次核心允许不代表整笔业务获准。Goal 保持活动。

## 原生 Saga 与显式金融业务恢复（2026-10-07）

`mvn -pl :xbod-deposit-demo -am test` 通过：语言 255、运行库 445、生成器 91、demo 129，共 920 项，0 失败、0 错误、0 跳过。日志 `/tmp/spp-xbod-saga-recovery.log`。补充完成日志失败案例后，`mvn -pl :xbod-deposit-demo -am -Dtest=DepositSagaRecoveryTest -Dsurefire.failIfNoSpecifiedTests=false test` 通过（6 项，0 失败/错误/跳过），日志 `/tmp/spp-xbod-saga-log-outcome.log`；当前 Surefire 共 921 项通过，其中 demo 130 项。

新增 APP ExplicitSagaStep，将局部执行、成功成交查询及明确业务恢复绑定到原生 DefaultTransactionManager/SagaTransactionStrategy，持久事件使用框架 SagaLogRecorder/JdbcSagaLogStore。getTransactionParticipant.rollback 在本绑定中代表业务恢复，不提供默认技术回滚或补偿。

六项实际生成计划及 H2 案例覆盖局部成功、后续失败时仅反原分量并保留独立成交、无成交不反向、ES020 业务恢复拒绝、显式稳定身份重试，以及 R1 已成交但恢复完成日志失败后的结果查询。新反交易保留原成交和反向账簿；框架保持主失败及 suppressed 恢复失败，不把整体流程改成成功。

原费/退费为零，无产品/积数事实，仍为明确金融组件 fixture。日志及 callback 绑定不是局部业务提交的同一事务，不自动扫描或跨进程重建；完整银行 Saga 和量子性存款提交仍未接通。范围及比较见 saga-recovery.md、spp-vs-cobol-java.md。待决策政策及完整现金冲正仍需继续，Goal 保持活动。

## 冲正提交结果不确定及当前完整命令验收（2026-10-07）

新增两项 JDBC 代理故障，分别为实际 commit 前抛异常和数据库已 commit 后才抛异常。两者记录 CommitOutcomeUnknown，再以独立冲正标识查询；未成交时同标识重试一次，已成交时仅重放原 Receipt，不再次减金额。`JdbcDepositReversalStoreTest` 针对性回归 16 项通过，日志 `/tmp/spp-xbod-reversal-unknown.log`。

运行文档中的 `./demos/bank-deposit/run-demo.sh` 完成当前源码的 reactor package、测试和文件数据库演示。语言 255、运行库 445、生成器 91、demo 132，共 923 项通过，0 失败/错误/跳过；日志 `/tmp/spp-xbod-current-demo.log`。

报告目录 `target/demo-report/run-84ce53fa-b681-4f4a-9a2c-9821dafdc5b1/`，已核对 10 个案例、6 笔实际成交、48 条实际分录、5 个未执行反向候选及其借贷平衡。goalComplete/cobolExecuted/bankConfigurationObtained 仍为 false。

逐项验收核对见 acceptance-audit.md。P4 完整现金冲正及跨日行为仍无端到端证据；跨日生效方式和退费规则待决策，不能从金融组件或正常存入换日测试推断完成。第一批范围不无限扩展成全产品、全部事务后端或生产部署。Goal 保持活动。

## P4：现金冲正政策已确认

用户明确现金冲正（含跨日）按原 XBOD 规则。此前待选择的跨日和退费候选方案不再构成阻塞；上文阶段记录保留为历史。已追踪 KSADEP0 4600/4630/4640 和 KSAFEE0 5500，有效规则及注释边界记录于 cash-reversal-source.md。新增 SPP 元数据计划及原费选择，验证后继续连接完整入口，不将独立计划称作端到端现金成交。

## 按场景拆分与显式量子事务

用户指出单一业务源过大、量子属性及事务不可见。已拆成同域场景文件，补齐金额的 quantum 声明、APP cashLedger、PHY jdbcQuantum。现金净余额/带符号对手方组成守恒组，生成 SPP transaction 在实际 JDBC 提交连接上运行；验收包括真实量子日志、账户对象隔离、重复和失败共同回滚，见 quantum-and-transactions.md。

## 当前验证：场景拆分、现金冲正及量子共同提交

完整回归 934 项通过：lang 255、appframe 445、generator 91、demo 143，无失败/错误/跳过。run-demo.sh 实际执行存入阶段及四笔 XBOD 现金冲正，每笔重放不重复更新，导出 32 条反向分录和 20 条量子记录。最新输出位于 target/demo-report/run-a7aa3ad3-df28-4f64-b5be-95d8dba12f77；构建与运行日志 /tmp/spp-xbod-final-cash-demo.log。量子测试验证外层回滚、对象隔离、错误原值拒绝和超过通用 SQL 默认小数位的精确值保存。

所选模型及 fixture 的完成证据见 acceptance-audit.md。原系统黄金等价、外围银行字段、通用非量子生命周期恢复和跨库部署等限制保持明确，不以本轮成功取消这些边界。


2026-10-09最终迁移门槛：默认父执行器现金冲正报告两新JVM组通过，日志 `/tmp/spp-report-default-lifetime-runtime.log`；同生成版本的JSON/Markdown已核对四实际冲正、32反向分录、20量子行和现金1700/版本4/积数2200。最后13主Java和1测试Java已删除，源目录Java当前全部为0。逐案例请求/授权/来源与实际重放返回增强已补SPP，尚需当前clean重新生成验证；`/tmp/spp-source-only-final-clean-validation.log` 正在执行，最终Goal尚未完成。


## 最终状态（2026-10-09）

本次纯源重构已完成：手写Java主0/测试0，旧14主类及21测试族无残留class，干净生成编译及945项公共JUnit、86个APP入口全部通过。五个两JVM组、逐案例输入/授权/来源增强、六成交48分录五候选及四冲正32反向分录20量子行全部核对。完整权威证据见[最终验证](source-only-final-verification.md)，当前状态以该记录为准，前文保留阶段历史及范围限制。
