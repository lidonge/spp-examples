> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 源语言样例覆盖核对

本表追踪旧手写验收的业务责任，避免把一个源样例通过误认为所有旧分支已迁移。所有已列源入口由 APP 声明，数据、交易和断言在 SPP 中；PHY 绑定真实仓库及量子保障。

> 验收证据更正：修复前四个含空 catch 的入口实际生成了空方法（replay、missingFee、pendingCurrentAccount、crossDayCashReversal），原通过结论已撤回。修复后统一 verify 已实际执行 17 个入口全部通过，以下证据以本次重跑为准；详细更正见 source-only-refactoring.md。

## 真实存款生命周期

| 旧 NormalCashDepositTest 验收责任 | 源入口 | 当前证据及剩余范围 |
|---|---|---|
| 普通存入、手续费、余额、当日累计及借贷记录 | ordinaryCashExample / crossBranchFeeCashExample | 两入口实际通过；同分行免收费、跨分行存储费率最低收费、账户版本和八条分录已查验；旧成交前事实的全部字段仍需逐项核对 |
| 普通、坏账、核销账户的偿还优先级 | normalDebtCashExample / badDebtCashExample / writtenOffCashExample | 三入口实际通过；独立预期验证三种还款次序、剩余债务、实际余额及借贷记录 |
| 待授权不更新、政策变化重新判断、授权后提交 | authorizationCashExample | 实际通过；三次尝试逐次读回审计，两次等待均无成交和分录，最后才更新账户 |
| 等待授权期间其他交易改变账户 | pendingCurrentAccountCashExample | 实际通过；后续交易先提交，原交易续接按最新余额拒绝，保持后续结果并保存失败审计 |
| 后续更新及次日更严政策下重试原交易 | replayCashExample | 实际通过；原成交结果和当前状态分别核对、不重复分录、审计 Replayed，改金额复用编号被拒绝；跨进程重启和不同数字文本格式仍待验证 |
| 当日累计换日清零及警告依赖当前日累计 | bankAdmissionRulesExampleRun / dailyCashLifecycleExampleRun | 当日 101+400 发警告，换日原 900 清零为 400，无警告；真实 300/300/次日 100 已逐笔通过成交、当前账户、原账户快照、分录与审计核对 |
| 业务拒绝和费率缺失，仅留请求身份 | missingFeeCashExample / replayCashExample | 实际通过费率缺失及编号复用的拒绝、账户未变、无新增成交分录和独立审计；完整请求身份查询及其他拒绝分支仍待补充 |
| 待授权身份跨运行实例保持、改金额拒绝 | pendingRestartSetupExampleRun → pendingRestartResumeExampleRun | 两个独立 JVM 已实际通过：持久身份仍为 1500、改为 1501 拒绝，原数额授权成交后格式不同重放保持 v1；删除旧测试后已由 clean verify 证明重新生成执行 |
| 并发等价请求只提交一次 | concurrentCashLifecycleExampleRun | SPP parallel + APP barrier 让两路都读到缺失成交，600.00/600 实际竞争；失败一路确定回滚后查询原成交并重放，账户/分录只写一次、审计一条成交一条重放；完整 verify 已通过 |

## 尚需完成的完整迁移

现金冲正的剩余边界、日历与积数、协定窗口、资格规则、数字边界、实际事务失败、版本冲突、并发、提交结果确定/不确定分类、Saga 恢复及声明式报告继续迁移。当前源入口数为六十一；旧 demo 的 14 个主 Java 文件和 7 个测试文件仍属于待删除违规项。删除之前必须保留对应责任的源验收证据，不能用旧测试回归通过替代纯源要求。

Maven `verify` 自动执行源入口；Maven 旧测试数量与源入口数量分开报告。一个入口可执行多次真实交易和多组断言，入口数量不能直接与 JUnit 方法数量相加或作为业务覆盖率。

## 完整现金冲正

`crossDayCashReversalExample` 已实际通过，完全使用源存款及源冲正生命周期。它包括带银行资格/积数/存储费率的原成交、次日后续成交、现金冲正共同提交、账户及原/冲正记录读回、原手续费退款、八条反向分录、唯一冲正关联、同一冲正重试和另一编号再次冲正的拒绝审计。实际余额 100 → 700 → 800 → 200，原成交和后续积数 800 保留。

99k 新增 `sameDayCashReversalExample` 和 `mode2CashReversalExample`，按 XBOD 源规则分别验证同日机构限额恢复标记及隔夜日期强制更新；两者已通过自动源运行；本阶段进一步将原笔之前日期改为 20261006，重新运行十二个入口全部通过，证明同日确实还原日期、Mode2 强制采用当前日。债务/分数金额冲正、未撤销关联中的并发、冲正途中技术失败和不确定提交结果仍是未完成项。


## 透支、小数和实际版本冲突

`normalDebtCashReversalExample`、`badDebtCashReversalExample`、`fractionalCashReversalExample` 已实际通过，分别查验原本金/利息/催收利息/敞口恢复、原手续费退款、当前积数保留、反向分录、账户版本、关联和审计。小数样例按用户已确认的精确业务语义验证，不能作为遗留 PIC 隐式截断的逐位等价证据。

`cashVersionConflictExampleRun` 已执行真实候选准备、另一笔存款及旧候选提交。提交场景第一步写成交、第二步版本保护失败后，真实查询证明候选成交撤销，分录和关联没有残留，当前账户保持另一笔存款结果，失败审计由源声明的独立量子事务保存。失败后再次成功存款的补强验证也实际通过，余额 950、版本 3、累计 850，并在真实共同提交中检查量子余额一致。该案例是确定的业务步骤交错；真实多线程并发、技术失败注入和提交结果不确定仍需独立证据。


## 分录写入后的技术故障

`cashWriteFailureExampleRun` 的 APP 声明在 storeCashPostingRecords 成功之后触发一次故障。运行器必须确认故障命中。SPP 独立断言查询实际存储，证明账户、成交、八条分录及关联撤销、失败审计独立保留；随后同一业务请求改尝试号成功提交，余额 700、版本 1、借贷分录各 600。该案例不代表数据库提交点故障、未知结果、并发或冲正失败已经验证。


## 日历与利息单位

`bankCalendarExampleRun` 已实际通过 30 组日期预期（8 组 ACT、两种 360 约定各 7 组、8 组业务拒绝）与 2 组显式单位量化。全部来源、输入和预期在 99o；使用生成日期服务。旧 BankCalendarTest 的四项方法完整由此替代，文件已删除。clean verify 已成功，确认旧字节码不存在，1011 项回归和 18 个源入口分别全部通过；其他积数、协定和源规则测试继续迁移。


## 存款内核和五档协定积数

`depositKernelExampleRun` 已实际通过十六组独立案例：十五组九字段计划断言与一组负金额拒绝，并逐组核对八字段账户快照。BigDecimal 绑定另由 PHY 声明和 javap 产物检查确认。`agreementProductExampleRun` 已实际通过十七组模式、阈值、单位量化、禁用和拒绝预期；各组校验全部五个结果字段及逐槽产品，拒绝前所有产品保持 999。干净重跑还增强模式 1 后复用同一五槽集合执行模式 2，确认实际 2000 产品被清零。

旧 DepositKernelTest 的十六组参数和 AgreementProductTest 的六项方法已由这些源入口承接，两个 Java 文件已删除。源 fixture 按偿还/边界和协定模式/精度/拒绝拆分；源入口本身保留顺序与断言。删除后的 clean verify 已成功：989 项回归与 20 个源入口分别全部通过，三个已替代旧测试 class 均不存在；其余旧测试继续迁移。


## 协议窗口、账户控制及四十九组现金准入

`datedAgreementExampleRun` 实际通过八组事实，校验七组有效/空窗口的交集天数、两类积数及真实裁剪日期；非法生效日期为 EE374 且产品尚未生成。`cashAccountControlExampleRun` 实际通过六类拒绝、正常账户，以及“冻结状态”和“冻结金额”的区别。`bankAdmissionRulesExampleRun` 实际通过四十九组输入，完整承接旧 BankRulesTest 的十二项方法：现金日期/金额、临时户、开户上下限和禁用配置、余额上限、警告及换日累计、B/A 严格阈值和权限、政策重验、六个交易与两种渠道例外、USD 阈值、单位量化及控制先行。

原 DatedAgreementTest 五项、CashAccountControlTest 三项和 BankRulesTest 十二项方法的文件已删除；源逻辑及独立预期分别在 99r、99s、99t，49 组配置和检查按 99ta/b/c 拆分。删除后的 clean verify 已成功：969 项回归与 23 个源入口分别全部通过，六份已迁移旧测试 class 均不存在；银行资格查询、并发、提交点技术失败、未知结果、报告和其余旧测试仍有迁移责任。


## 银行资格、原成交提示与现金冲正政策

`bankQualificationRulesExampleRun` 已实际通过五十四组独立事实：机构关系、空关系错误、限制子类作用域、柜员家族/编号和权限、交易/业务例外以及挂失独立提示。`bankWarningCashExampleRun` 通过真实收费/积数/分录共同提交，查询原成交中的 WN200/WN201 与 SA01102 柜员事实；重试时代理签约标记改变，仍返回原提示与原柜员身份，账户保持版本 1、余额 700、八条借贷各 602，审计 Replayed。`bankRejectedCashExampleRun` 实际验证 EN134 和柜员上下文不一致：两次均无成交/分录，账户版本 0、余额 100，独立 Rejected 审计保留。

`xbodCashPolicyExampleRun` 已实际通过四种元数据计划、一组积数不足以及原手续费 0/2/1.005。删除后的干净构建又加强退款为独立常量并检查原费用未改变。各计划校验日期、明细数、现金累计、正常/实际积数、机构限额标记及输入不变性；机构限额标记不是完整机构限额账簿更新。

上述入口完整承接 DepositBankQualificationTest 八项和 XbodCashReversalPolicyTest 五项方法，两份 Java 文件已删除。clean verify 已通过：956 项回归及 27 个源入口分别全部成功，八份已迁移旧测试 class 均不存在；当前仍有十四个主 Java、十三个测试 Java 待删除，跨进程、完整并发、提交点技术失败/未知结果及其余旧规则和报告继续迁移。


## 仓储费率收费与当前状态上的金融反向

`depositFeeRulesExampleRun` 实际通过十六组独立预期，使用唯一客户/收费代码的真实仓储费率，种入在 SPP 显式 quantum 事务内。完整 prepareDepositFee 路径验证地域先于机构分类、比例折扣、显式半入、固定额与上下限（含零上限）、无查询的 Mobile、未迁账户类别、缺失费率、错收费代码及负金额。收费代码不匹配还检查旧费用未被改写。

`financialInverseRulesExampleRun` 实际通过十组原/当前账户事实，原分量由真实存款内核和描述服务记录，反向计划七字段逐项比较独立常量，当前账户八字段逐项比较复制快照。覆盖后续支出/存入、冻结/授权、原与当前贷款状态改变、原敞口钳制实际增量、小数偿还、容量/结果资格和伪造原记录。早期拒绝还要求计划未开始生成。

DepositFeeTest 五项与 DepositReversalAmountsTest 七项方法已完整由这些源责任承接，Java 文件已删除；clean verify 已成功：944 项回归与 29 个源入口分别全部通过，十份已替代旧测试 class 均不存在。分录测试仍被旧整笔存款及仓储测试作为 fixture 引用，需要协同迁移，不能仅删除其测试文件。当前仍有十四个主 Java、十一个测试 Java 待迁移。

## 积数责任迁移（验证中）

旧 DepositAccrualTest 六项方法对应 99z/99za 的四个 APP 源入口：协议窗口积数与输入不变、360/ACT 分开计日、显式单位与催收利息天数、真实成交原区间/幂等/同日第二笔、无效单位全笔拒绝、账户和积数更新后技术故障/独立回滚审计/原身份重试。故障通过 APP `fault before storeCashPostingRecords` 声明，注入点为账户和积数已更新、分录尚未写入；旧 JDBC 驱动故障的通用生命周期责任由框架结果证据测试承担，源案例验证银行数据结果。

首轮新增两个纯规则/拒绝入口及原 29 个入口通过，两个真实成交入口在额外分录预期上失败，已按独立资金事实修正并重跑。当前仍保留旧积数测试，最终干净证据尚待取得。


修正后完整 verify 的 33 个入口均通过，旧 DepositAccrualTest 六项方法的 Java 文件现已删除，正在 clean verify 确认生成字节码不残留。另补 99zb 的纯审计政策入口：七组存款/冲正配对事实验证未上报、确定回滚、结果未知、成交后返回失败、重放审计失败、提交前拒绝、无工作上下文。此入口测试业务分类，不把手工 fixture 标记当作物理证明；真实数据库提交/回滚/清理结果由通用框架测试测量，银行提交点故障与恢复结果的源验收仍待补齐。


上述积数与审计阶段已取得最终干净证据：clean verify 成功，951 项 JUnit 和 34 个 APP 源入口分别全部通过；11 份已删除旧测试均无残留 class。旧积数六项方法由四个源入口承接，99zb 的七组配对审计政策另行实际通过。当前手写库存主 Java 14、测试 Java 10，仍不满足最终纯源验收。首轮 50/170 分录预期错误及修正过程保留在重构记录，最终使用现金 50、旧存款减少 120、本金 100/利息 30/催收息 40 的独立槽断言。

## 核心冲正资格与原成交准备（验证中）

99ca 为原成交查询、当前账户查询、金融候选、核心资格候选及显式退款反向分录提供源入口；候选没有隐含事务或提交。99zc/99zd 的两个 APP 入口正在替代 DepositReversalEligibilityTest 四项责任：核心关闭/注销/冻结顺序、SA01116 例外、文档提示而无普通存入范围门槛、前端机构控制独立、真实后续更新的冻结/挂失/注销事实、输入复制和准备不更新账户/审计/分录/关联。

当前首轮生成曾因跨文件字段定义顺序失败，已调整新源文件顺序，完整执行尚待取得。金融/分录准备的旧八项责任尚未全部迁移，不能据这两个资格入口删除 DepositReversalPreparationTest。


核心资格完整 verify 已通过：两个新增入口和原 34 个入口全部实际成功。源候选使用当前版本 3 的冻结账户、余额/积数 800，反向原 600 得到金融候选 200，不提交该候选；复制的 SA01116/容量 1000 不受调用者后续修改影响，当前注销更新版本 4 后拒绝 EN113。查询原成交实际分录/审计/关联，仍为八条借贷各 602、一条 Committed 审计、版本 0 未冲正关联。旧四项资格测试已删除，正在 clean verify 确认旧字节码不残留。金融/分录准备八项责任仍待完整迁移，后续真实缺失分录需要通用 APP 删除能力，不能用假的查询结果替代。


核心冲正资格阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 290、appframe 494、generator 101、剩余旧 demo 62，共 947 项 JUnit 全部通过无跳过；36 个 APP 源入口另行全部通过。十二份已替代旧测试的 class（含嵌套类）全部不存在。新的核心资格和当前事实案例均在清空 target 后生成执行；当前手写库存主 Java 14、测试 Java 9，整体纯源要求尚未满足，Goal 继续活动。

只读金融/分录准备的其余八项责任、实际存储删除/证据破坏、提交点和结果核对、并发、Saga/补偿与报告仍继续实施。此次没有新增 demo Java，也没有把银行查询或资格逻辑迁入公共 Java 运行库。

## 原成交与实际分录的候选准备（验证中）

99ze/99zf/99zg 的八个 APP 入口覆盖旧准备测试：当前版本 3/余额 2300/产品 2200 的原笔金融反向、不提交及容量复制；0/1.25/2 显式退款和方向/科目/六个金融分量不变；普通/呆账/小数从实际成交恢复；未知/实际拒绝原笔及 ES020；缺失/负数/过量退款；实际成交 settled 基数改为 999 后拒绝；实际分录科目改为 DEMO.WRONG_CASH 后拒绝；通过新 APP delete 真正删除第 8 条记录并查询剩余 7 条后拒绝。所有种入/破坏 fixture 的事务在 SPP 声明 quantum，不用银行 Java 或替换查询返回值。

完整执行尚待取得。String + String 的一般业务语义和通用删除能力已补齐，精确小数原生删除键另有框架验证；旧 DepositReversalPreparationTest 暂保留。


日期对齐旧准备 fixture 后，完整 verify 已通过全部 44 个入口；三个债务/小数入口和现金准备、退款、拒绝、成交/账簿证据入口均实际成功。DepositReversalPreparationTest 八项方法的文件已删除。已追加实际原账户身份篡改并要求 INVALID_ORIGINAL_DEPOSIT_ACCOUNT；clean verify 正在验证此追加责任以及十三份已删除旧测试均无残留字节码。当前手写库存主 Java 14、测试 Java 8，仍不能宣布整个 demo 满足纯源要求。


原成交/分录准备阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，lang 292、appframe 501、generator 101、剩余旧 demo 54，共 948 项 JUnit 无失败、错误或跳过；44 个 APP 源入口另行全部通过。实际原账户身份篡改亦拒绝 INVALID_ORIGINAL_DEPOSIT_ACCOUNT，账户/积数/审计/原分录保持。十三份已删除测试（含嵌套类）均无残留 class。当前手写库存主 Java 14、测试 Java 8，目标仍未完成，Goal 保持活动；重启、并发、银行提交点结果、Saga/业务恢复和报告责任继续实施。


## 完整日累计与同步并发（验证中）

99zh 的 dailyCashLifecycleExampleRun 用三个真实成交覆盖同日累计警告和次日重置，逐笔核对入库的原/成交事实、账户、八条分录和审计。99zi 的 concurrentCashLifecycleExampleRun 使用独立生命周期、同一业务 id、600.00/600 两种精确源数字表示，经 SPP parallel 与 APP barrier 同步进入缺失成交后的准备分支；必须返回同一版本 1/余额 700，实际账户仅一次更新，八条分录，原笔两条审计为一次 Committed 和一次 Replayed。新入口正在执行，当前最终基线仍是上一阶段 clean verify 的 44 个入口；旧 NormalCashDepositTest 九项仍保留，跨进程待授权身份尚缺证据。


换日及并发阶段最终证据：`mvn -pl :xbod-deposit-demo -am verify` 成功，lang 293、appframe 504、generator 101、剩余旧 demo 54，共 952 项 JUnit 无失败/错误/跳过；46 个 APP 入口另行全部通过。新增换日入口逐笔通过 Ready→Warning→Ready、日累计与入库事实；并发入口通过两种精确数字表示、屏障实际会合、恰好一次 PERSISTENCE_ALREADY_EXISTS/ROLLED_BACK、查询原成交并返回同一结果、账户与分录仅一次更新、一条 Committed 与一条 Replayed。普通业务运行不启用屏障。新语义与生成目录以及运行支持均有通用框架验证。当前库存主 Java 14、测试 Java 8 未改变；NormalCashDepositTest 的跨运行实例/待授权身份仍未全部替代，不能删除它或宣布纯源验收完成。下一批继续跨进程、竞争无原成交的拒绝分支、提交点结果、Saga/业务恢复及报告。


跨 JVM 等待身份阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 294、appframe 507、generator 101、剩余旧 demo 45，共 947 项 JUnit 无失败/错误/跳过；48 个 APP 入口另行全部通过，其中等待种入与重启续接两个独立 JVM 阶段分别通过。实际阶段日志为 target/spp-examples/restart-5696792022188799453/stage-0.log、stage-1.log。授权历史三条（两次等待、一笔成交）、拒绝/费率缺失身份读回、原收费事实、未成交冲突确定回滚及原异常保持均在清空 target 后实际执行。十四份已迁移旧测试（含嵌套类）均无残留 class。当前手写库存主 Java 14、测试 Java 7，全部删除目标尚未完成，Goal 保持活动；下一批继续提交点结果、Saga/业务恢复、量子日志与报告。


## 存款 JDBC 提交点与查询恢复

99zl 的 beforeCommitCashFaultExampleRun、commitBeforeCashFaultExampleRun、commitAfterCashFaultExampleRun、afterCommitCashFaultExampleRun 均在完整 `mvn -pl :xbod-deposit-demo -am verify` 中实际通过。锚点为主 quantum 事务最后的 storeCashAudit。分别验证 ROLLED_BACK/UNKNOWN/UNKNOWN/COMMITTED，并查询真实账户、成交、八条分录、唯一关联和尝试历史。两种 UNKNOWN 对外错误相同，但实际数据分别未提交/已提交；SPP 随后按稳定业务身份重试及精确数值 600.00 重放，最终账户只更新一次。

审计 APP 存储键为 (attemptId,event)，同一次已成交但确认丢失/响应失败可保留两条事件。多个事件以集合查询明确核对，不使用标量任选记录。已确认成交后的返回失败不调用 rollback。四种控制均须实际触发，不能靠入口返回成功冒充故障执行。

本轮完整 verify：lang 295、appframe 513、generator 101、剩余旧 demo 45，共 954 项 JUnit 无失败/错误/跳过；52 个 APP 根入口另行全部通过。此次是增量 verify，上一阶段 clean verify 的 947 项和 48 个入口仍是已有干净基线，不将本轮称为 clean 构建。剩余旧测试没有删除；冲正提交点、并发、审计失败、量子日志、Saga 与报告仍待全部迁移。


## 现金冲正故障与跨 JVM 重放

99zm/99zma/99zmb 六个根入口实际全部通过：beforeCommitReversalFaultExampleRun、commitBeforeReversalFaultExampleRun、commitAfterReversalFaultExampleRun、afterCommitReversalFaultExampleRun、recordReversalFaultExampleRun、linkReversalFaultExampleRun。完整源码查询区分 ROLLED_BACK/UNKNOWN/UNKNOWN/COMMITTED，另验证首笔冲正记录及关联写入后的确定回滚。未提交保持原/后续成交和 v2/800；已提交为 v3/200、积数 800、原手续费退款 2、关联 v1、八条借贷各 602。恢复与次日重放之后没有第二次冲正；原/后续分录 side/subject/amount 仍与成交证据一致。

99zn 的 reversalRestartSetupExampleRun 与 reversalRestartResumeExampleRun 两个独立 JVM 阶段亦实际通过：共享 PHY 文件数据库，空参与者只读回成交及分录，不重跑种入。新 JVM 再存入 25 元后，当前账户 v4/225、积数 1000；重放冲正返回原 v3/200 而保持当前状态。改原交易、改 overnightMode2 复用编号均拒绝 DEPOSIT_REQUEST_ID_REUSED，另一冲正编号再次撤销原笔拒绝 ORIGINAL_DEPOSIT_ALREADY_REVERSED。四条原冲正审计（一成交、一重放、两身份拒绝）和独立重复冲正拒绝均来自实际仓储。

本轮 `mvn -pl :xbod-deposit-demo -am verify` 成功：954 项 JUnit 无失败/错误/跳过；59 个根入口全部通过（compound restart 的两个阶段另有各自 PASS）。阶段日志：target/spp-examples/restart-4430443081500016374/stage-0.log、stage-1.log。此次为增量 verify，未删除旧 Java；当前主 14/测试 7。剩余删除门槛仍包括真实冲正并发、过期/变化的候选、部分批次与审计不可用、量子持久记录、Saga 恢复和报告。


## 真实并发冲正

99zo/99zoa/99zob 的 sameIdentityConcurrentReversalExampleRun 与 differentIdentityConcurrentReversalExampleRun 已在完整 verify 实际通过。APP 屏障使两路完成候选准备后同时提交，源断言恰好一次实际存储冲突且其事务确定 ROLLED_BACK。同身份返回同一 v3/200 成交、唯一关联/八条分录、一成交一重放审计；不同身份一成功一 ORIGINAL_DEPOSIT_ALREADY_REVERSED 拒绝、失败候选无残留、总计八条借贷各 602 分录、一成交一拒绝审计。原存款、后续存款与其分录/积数仍保持。

恢复先在 catch 内查询真实成交或关联，查询失败保留原异常；身份校验、重放和有据的业务拒绝在 catch 之后执行，避免通用处理异常保留机制把业务拒绝附加为副异常。未查询到成交或已撤销关联时仍抛原失败，不能凭存储冲突推断业务结果。

最终 `mvn -pl :xbod-deposit-demo -am verify` 成功：954 项 JUnit 无失败/错误/跳过，61 个 APP 根入口全部通过，原有故障及两个跨 JVM 方案均无回归。此次为增量 verify，旧 Java 库存仍主 14/测试 7。量子日志极小金额的文本物理表示、部分批次/审计不可用、Saga 与报告责任仍待完成。


## 精确量子存储与原生日志查询

99zp 的 quantumEvidenceExampleRun 由 SPP 创建 100 的账户净额和零对手方，提交 1e-25，并通过 APP 映射的实际量子日志/当前值表查询。独立断言确认两个属性分别为 100.0000000000000000000000001 与 -1e-25，两条 COMMITTED 记录的原值、增量及成交值均精确，增量合计为零。PHY 明确选择 BigDecimal 和 jdbcQuantum text 存储；APP 数字字段到文本列的映射不改变业务数字语义。

完整增量 verify 成功：lang 296、appframe 517、generator 102、旧 demo 45，共 960 项 JUnit 无失败/错误/跳过，62 个 APP 根入口全部通过。两个跨 JVM 阶段均通过。不是 clean 构建，手写库存仍主 14/测试 7；账户隔离、量子失败后日志不变和旧值冲突的源责任继续迁移，不能据此删除旧 CashQuantumLedgerTest。


## 量子生命周期的源责任承接

99zpa 三个入口实际通过。quantumIsolationExampleRun 在独立 A/B 对象提交 1e-25/25 后查询两者日志/当前值，A 保持精确；quantumRollbackExampleRun 在 SPP 显式 quantum 内更新后业务拒绝，要求 ROLLED_BACK 与零持久日志/值，随后同对象能合法提交 110/-10；quantumStaleValueExampleRun 先提交 100→110，再由旧计划 100→120 请求增量20。量子参与者锁定最新值110后所得130与计划120不符，源业务校验报 QUANTUM_CASH_BALANCE_MISMATCH/ROLLED_BACK；查询仍110/-10和原两条日志，合法增量5后为115/-15和四条日志。框架仍按最新值增量操作，不改成覆盖式更新。

完整增量 verify 成功：960 项 JUnit，65 个 APP 根入口全部通过，原62个无回归。旧 CashQuantumLedgerTest 三个方法由四个量子源入口承接，文件已删除；库存主14/测试6，清理后预计旧JUnit42项。原测试使用手写 JDBC 外围事务及内部作用域断言，源案例改为业务可见显式 quantum 边界、持久结果及失败后合法提交；调用者自持连接回滚/作用域清理另有通用框架测试，不在 demo 增加 Java 辅助。此刻 clean verify 刚启动，尚不宣称干净验收通过或旧字节码已经清除。


量子生命周期最终 clean verify 成功：lang296、appframe517、generator102、剩余旧demo42，共957项JUnit无失败/错误/跳过；65个APP源入口全通过。十五份已删除测试（包括嵌套类）无残留class。当前主Java14、测试Java6，Goal活动。此构建验证量子迁移基线，不包含编译之后才写入的连续故障/附加失败码新扩展；该扩展正在单独测试。日志 /tmp/spp-quantum-lifecycle-clean-validation.log。


## 主审计与失败审计同时不可用

99zq/99zr 四个源入口完整通过：depositAuditUnavailableExampleRun 在主审计及失败审计前连续注入两次故障，确认主错误/ROLLED_BACK、附加错误一项、账户/成交/分录无残留，随后同身份正常提交；rejectedDepositAuditUnavailableExampleRun 保持 DEPOSIT_FEE_RATE_NOT_FOUND 业务主码、附加审计故障且账户未改；reversalAuditUnavailableExampleRun 在真实原存款及后续存款完成后才启用双审计故障，确认完整反向交易回滚、原及后续交易保持，再重试与重放仅一笔冲正；replayedReversalAuditUnavailableExampleRun 已有原冲正成交后启用重放/失败审计故障，确认已知成交保持、六条实际量子日志不增加，合法重试只补一条重放审计。附加错误来自原异常直接 suppressed 链，源事实中独立计数，不替换主错误。

最终增量 verify 成功：lang298、appframe522、generator102、旧demo42，共964项JUnit无失败/错误/跳过，69个APP源入口全通过；原65个入口无回归。此轮不是clean，主14/测试6未删除；银行审计不再以删表/手写JDBC故障器实现。原凭证在准备后变化、过期候选、部分批次中途失败、Saga及报告仍待完成，不能删除仍承担这些责任的旧测试。


批次中途冲突最终增量 verify 成功：lang298、appframe522、generator102、旧demo42，共964项JUnit无失败/错误/跳过；71个APP根入口全部通过。99zs/99zt 实际在slot4冲突，确认前面已写分录全部回滚，原fixture保持；删除fixture后同身份提交成功，量子日志没有重复。日志 /tmp/spp-partial-posting-source-validation.log。本轮不是clean，主Java14、测试Java6保持；原成交事实复核、准备/提交分层、Saga和报告仍须迁移，Goal保持活动。


原成交事实复核接入修正轮完整 verify 成功：lang300、appframe528、generator105、旧demo42，共975项JUnit无失败/错误/跳过；71个APP根入口全部通过，含两组跨JVM重启及同/不同身份的真实并发冲正。93的完整SPP quantum内锁定读取原存款并以sameFacts复核，91归档原存款快照，99准备/提交分层已实际生成、编译、运行。APP六项遗漏绑定已补齐，没有手改生成Java。日志 /tmp/spp-original-evidence-binding-source-validation.log。本轮为增量verify，不是clean；主Java14、测试Java6保持。原凭证变化/过期候选/准备结果已成交身份的三组新独立验收，以及Saga和报告仍待实施；原71个通过不代替这些未完成责任，Goal保持活动。

准备结果修正轮完整 verify 成功：lang303、appframe528、generator105、旧demo42，共978项JUnit无失败/错误/跳过；74个APP根入口全部通过。新增99zu原凭证变化、99zua过期准备结果及同日积数800、99zub已成交准备结果重放与两类身份差异拒绝均实际成功；两组跨JVM重启和真实并发保持。日志 /tmp/spp-prepared-reversal-corrected-source-validation.log。按 reversal-store-retirement.md 的责任表删除 JdbcDepositReversalStoreTest（16方法），当前主Java14、测试Java5；正在clean verify，预期旧JUnit26，但不提前认定干净验收成功或旧class已清除。Saga和报告及全部主Java迁移仍未完成，Goal保持活动。

旧冲正存储测试退休后的clean verify成功：lang303、appframe528、generator105、旧demo26，共962项JUnit无失败/错误/跳过；74个APP根入口全通过。JdbcDepositReversalStoreTest及嵌套class均无残留，累计十六份旧测试退休，当前主14/测试5。日志 /tmp/spp-reversal-store-retirement-clean-validation.log。此干净基线不包括其后才接入的99zv Saga六类和99zw分录规则新源，后者下一轮另行验证；不得据此宣称Saga已通过或整个目标完成。

场景物理绑定与证据导出完整verify成功：lang303、appframe533、generator105、旧demo26，共967项JUnit无失败/错误/跳过；81个APP根入口全部通过。99zv六类Saga和99zw分录规则均实际成功，原74入口及两组独立JVM重启、真实并发无回归。证据导出实际读取到六类Saga的Done/NotCommitted/Failed/Confirmed状态、3次恢复重试与2次完成记录失败后的确认；七个新增入口的JSON和Markdown均在target/spp-examples/evidence存在且状态PASS。日志 /tmp/spp-source-saga-runtime-evidence-validation.log。按源责任接替删除DepositPostingTest和DepositSagaRecoveryTest（各6方法），累计十八份旧测试退休，当前主14/测试3，预计剩余旧JUnit14。清理后clean verify尚未执行，不提前认定旧class已清除；报告、存款存储的快照复核/不同身份真实竞争和全部主Java迁移继续，Goal保持活动。

账户边界修正轮完整源验证成功：mvn -pl :xbod-deposit-demo -am verify -Dmaven.test.skip=true，83个APP根入口全部通过，无FAIL；既有81入口、两组跨JVM重启及真实并发保持。日志 /tmp/spp-cash-account-boundary-corrected-source-validation.log。本轮跳过JUnit和测试编译，不宣称它是全测试回归；新的公共恢复目录已另行完整appframe536项JUnit通过。新91/92/93账户锁定复核和99zx篡改/不同现金身份竞争两项均已实际生成编译运行。按deposit-store-retirement.md责任表删除JdbcDepositStoreTest（10方法），解决它对已退休DepositPostingTest夹具的最后编译依赖；累计十九份旧测试退休，当前主Java13、测试Java2（剩四项报告/现金冲正责任）。现启动完整clean verify，预计948项JUnit和83入口，不提前认定旧class清除或整个目标完成；银行聚合报告及全部剩余主Java仍需继续迁移。


最新干净构建证据（2026-10-08 23:16）：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，日志 `/tmp/spp-account-boundary-retirement-clean-validation.log`。JUnit 948项（lang303、appframe536、generator105、旧demo4）零失败、零跳过；APP83入口零失败，包括实际并发及两个独立JVM重启组。已确认JdbcDepositStoreTest、DepositPostingTest、DepositSagaRecoveryTest、JdbcDepositReversalStoreTest及ExplicitSagaStep的旧class和嵌套class均不存在。此证据对应83入口，随后新增现金报告源码及第84重启入口不包含在该证据内。剩余13份主Java、2份测试Java仍属待迁移违规项，Goal继续活动。


84入口增量验证完成：日志 `/tmp/spp-source-cash-report-corrected-validation.log`，`mvn -pl :xbod-deposit-demo -am verify -Dmaven.test.skip=true` 成功，84源入口全部通过（含新增现金报告两JVM组）。此命令跳过JUnit及测试编译，不能替代此前948项/83入口的clean证据。现金报告增强校验与两个完整报告入口之后接入，当前86源码的package生成正在运行 `/tmp/spp-source-complete-report-generation.log`，未认定86入口已通过。

完整存款报告两JVM及JSON/中文Markdown事实核对通过，DepositDemoReportTest已删除，文件数当前主Java13、测试Java1（CashDepositReversalTest三项）。旧报告测试class尚待新的clean构建清除，不认定已清除。公共批量注册避免逐项全目录刷新已通过537项框架JUnit。实际冲正报告因重复尝试身份的审计歧义失败，已修正源fixture编号，正在再生成验证；详见source-report-migration.md。


2026-10-09最终迁移门槛：默认父执行器现金冲正报告两新JVM组通过，日志 `/tmp/spp-report-default-lifetime-runtime.log`；同生成版本的JSON/Markdown已核对四实际冲正、32反向分录、20量子行和现金1700/版本4/积数2200。最后13主Java和1测试Java已删除，源目录Java当前全部为0。逐案例请求/授权/来源与实际重放返回增强已补SPP，尚需当前clean重新生成验证；`/tmp/spp-source-only-final-clean-validation.log` 正在执行，最终Goal尚未完成。


## 最终状态（2026-10-09）

本次纯源重构已完成：手写Java主0/测试0，旧14主类及21测试族无残留class，干净生成编译及945项公共JUnit、86个APP入口全部通过。五个两JVM组、逐案例输入/授权/来源增强、六成交48分录五候选及四冲正32反向分录20量子行全部核对。完整权威证据见[最终验证](source-only-final-verification.md)，当前状态以该记录为准，前文保留阶段历史及范围限制。
