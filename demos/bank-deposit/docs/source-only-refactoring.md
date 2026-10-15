> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 纯源语言重构实施记录

2026-10-08 已启动重构 goal。验收依据为 AGENTS.md、source-language-only.md 和用户的新要求。旧的 P1–P4 行为证据作为迁移参考，不能替代纯源语言验收。

## 分阶段交付

| 阶段 | 交付 | 状态 |
|---|---|---|
| R1 | SPP 显式事务模式、编译检查、生成与运行一致性；禁止隐式切换协调器 | 已实现；回归通过 |
| R2 | 完整存入和冲正业务场景、校验作用域、待授权结果与条件服务执行 | 条件语法、生成与准备路由已加入，完整执行仍待迁移 |
| R3 | 通用查询/更新生成、账户与成交/分录/原关联/审计共同资源、版本与幂等 | 首批仓储写入声明及版本检查已实现，完整交易迁移待完成 |
| R4 | 日期能力、模型构造、自动启动与声明式数据/验收 | 日期和模型构造已加入；启动及声明式验收待实施 |
| R5 | 移除全部 demo 手写 Java，干净生成并完成交易与故障回归 | 待实施 |

顺序按依赖调整，但不能通过减少原三类存入、对应冲正或故障验收范围来消除缺口。

## R1 的具体实现

在现有事务组上支持 `transaction at/tcc/saga/quantum { ... }`。SPP 模式进入模型和生成代码；APP 对更新服务的绑定不能与其冲突。空的显式事务组报错。运行时在执行任何动作前验证实际服务模式，显式非 Saga 组不会被安装的 Saga 协调器接管。旧工程允许省略模式，迁移后的 demo 要求显式写出。

银行金额组已改为 `transaction quantum`，但这仍只是金额组。完整存款和冲正中的账户、成交、分录、原关联、审计的业务边界及物理提交尚未迁移；当前 14 个实现和 21 个测试的手写 Java 都仍是待移除违规项。

对应通用语法文档：[SPP 事务模式](../../../book/references/spp-transaction-mode.md)。本轮没有新增或修改 demo Java。

## R2 的首批能力

场景支持带明确作用域的 `if/else/else if`；条件类型及引用检查复用业务表达式，不允许条件副作用。选中的分支可包含显式事务，未选中的分支不启动服务或事务。所有分支仍参与编译检查。新增 `cboddeposit-85-deposit-route.spp` 从可选银行资格及积数事实选择四种已有准备场景，并加入 APP 本地部署声明。

已在公共生成器测试中实际编译生成 Java，验证成功提交、未授权分支跳过事务、其他拒绝分支，以及执行失败的恢复；测试不是 demo 手写实现。原 Java 入口及授权异常处理仍未移除，完整持久化执行将在后续阶段迁移。语法文档见 [场景条件](../../../book/references/spp-scenario-conditions.md)。

## 回归记录

首次 R1 框架回归：lang 260、appframe 450、generator 91，共 801 项通过。加入场景条件及源路由后的 `mvn -pl :xbod-deposit-demo -am test`：lang 263、appframe 450、generator 92、demo 143，共 948 项通过，无失败、错误或跳过。补充 else-if 后再次执行同一命令：lang 264、appframe 450、generator 92、demo 143，共 949 项通过，无失败、错误或跳过。

这些是语法扩展与旧行为保留证据；并非“纯源语言 demo 已完成”。当前 goal 保持 active，未进入 R5 最终验收。

## R3 的首批能力

新增通用 APP `persist(insert/update/upsert, argument(...))` 和 `compareVersion(...)`，生成服务内的仓储写入及版本捕获。仓储只加入显式事务，不自行开启或提交；支持新增唯一性、更新存在性和锁定后的版本比较。一维集合可整体加入调用者事务，集合版本检查暂时明确拒绝。

显式绑定到同一个 localJdbc 后端且连接配置一致的仓储与量子日志复用 DataSource；查询复用当前连接，能读到本事务写入。Saga 外层不包住所有局部节点的 JDBC 提交。语义及限制见 [APP 仓储写入](../../../book/references/app-persistence.md)。

这一阶段扩展公共编译器、模板和运行库，没有新增 demo 手写 Java。银行完整执行入口、统一资源配置、幂等回放、声明式验收和旧 Java 删除仍未完成，不能宣称 R3 或纯源语言 demo 已验收。

R3 首批能力回归：`mvn -pl :xbod-deposit-demo -am test` 全部通过，lang 269、appframe 459、generator 93、demo 143，共 964 项，失败/错误/跳过均为 0。新增验证包含实际生成服务编译、调用及幂等回放不重复写入。日志 `/tmp/spp-source-only-phase3-final.log` 是本地运行证据，测试代码及源声明为可重跑依据。

## R3 银行记录与边界迁移

新增 `cboddeposit-91-cash-storage-model.spp`、`cboddeposit-92-cash-deposit-records.spp` 与 `cboddeposit-93-cash-reversal-records.spp`，定义持久化账户、存入成交、现金冲正成交、分录、原成交冲正关联和审计角色；新增查询服务及 APP persist/compareVersion 绑定。原 Java 的账户事实与成交包装转为源语言字段，成交前后事实显式使用 copy 独立复制。

`commitCashDepositRecords` 和 `commitCashReversalRecords` 分别声明完整共同提交，包含账户 CAS、成交、分录、关联、金额守恒服务、准备余额与量子余额一致性检查、成功审计。冲正关联独立版本检查防止两笔冲正同时使用同一原成交。PHY 的 cashRecords 仓储、cashLedger 和两种事务资源显式绑定到 cashDatabase 后端。账户及现金对手角色使用 accountId 主键声明，避免多账户共享默认量子标识。

同时修复跨文件原子服务的声明合并：先调用、后定义的服务保留参数、返回及实现。新增参与者 copy 的通用类型校验、生成及运行支持，集合与嵌套事实不相互覆盖。原银行规则与跨日现金冲正计算保持已有源实现。

这些源服务已通过生成和 Java 编译，旧的 Java 入口仍在使用旧存储。尚需迁移真实入口及其查询顺序、可选事实、上下文构造、重复请求与待授权后继续执行，再由声明式案例证明新边界的完整行为；不能将旧 Java 测试通过当作这些新场景的银行端到端验收。

下一步缺口：构造计算上下文及默认集合、通用日期解析绑定、费率配置查询、来源于源语言的幂等生命周期（待授权不能被当作已成交缓存）、失败审计及声明式案例运行。继续按 R2–R5 完成，14 个 main 和 21 个 test 手写文件仍待删除。

银行记录、身份声明与复制能力回归：`mvn -pl :xbod-deposit-demo -am test` 通过，lang 273、appframe 461、generator 94、demo 143，共 971 项，失败/错误/跳过均为 0。存款及冲正提交源分别位于 92 和 93 文件，共享模型/身份/复制位于 91；生成结果放在 target，没有手工修改。日志 `/tmp/spp-bank-records-final.log`。这证明生成、编译及旧行为保留；新银行场景的完整入口与故障验收仍待声明式案例实现。


## R4 计算上下文与基础日历

新增 `new Type()`，仅构造当前域声明的数据模型；生成器和语义检查禁止任意 Java 类及错配类型。新增通用 Gregorian 日期有效性、年/月/日和 epoch-day 函数，数字通过 PHY 适配。日期允许范围及错误码保留在 SPP 的 decodeBankDate 中，没有移入银行专属运行实现。生成器测试实际编译及执行 BigInteger 物理字段的构造和日期计算。

`cboddeposit-96-deposit-work.spp` 在源语言中初始化计算上下文、独立复制账户和积数事实，并构造嵌套日期、期间及协定模型。费率改为 SPP 场景：准备客户/费目查询键、查询费率记录、校验及赋值；APP 负责 composite-key 仓储绑定。尚未删除旧费率及日期 Java，旧入口仍可能使用旧实现，不能以其回归证明新源查询已经端到端验收。

场景类型化调用返回自己的响应对象，与原始 execute 调用一致。请求调用的响应保存在调用局部变量中。生成器统一服务参数数组与模型 List 的转换，可选集合保持 null；这使没有积数事实的调用能到达 SPP 条件分支。

完整回归日志 `/tmp/spp-work-calendar-response.log`：`mvn -pl :xbod-deposit-demo -am test` 通过。此记录仍是扩展生成链路与旧行为保留证据；真实交易入口、请求身份及待授权重试、缺失记录的业务处理、失败审计、声明式验收、所有 demo 手写 Java 删除继续待完成。通用语义见 [参与者构造与日历](../../../book/references/spp-participant-construction.md)。

补充验证 `/tmp/spp-collection-construction-tests.log`：框架生成器实际生成并编译完整场景与原子服务，调用可空集合及嵌套集合，确认模型 List/服务数组转换、独立复制、每次调用的独立响应，以及类型化和原始调用响应一致。语义测试确认模型数字可校验 null、数字常量不能与 null 比较。指定测试 4 项通过，无失败、错误或跳过；测试位于公共框架模块，没有新增 demo Java。


## R2 存入尝试执行场景

`cboddeposit-97-deposit-execution.spp` 定义命令、执行上下文及 executeCashDepositAttempt。账户查询、上下文初始化、可选银行资格、现金路径和准入、四种准备路由、成交与八条分录装配、余额增量及完整提交均在业务源可见。批准时调用 92 文件的共同量子边界；待授权时只在单独显式量子边界写审计，跳过账户、成交、分录及金额修改。每次审计的 attemptId 必须由调用者提供，不在银行手写 Java 中生成。

补充一维参与者集合初始化及局部数组声明，用于源语言构造八条分录并逐条赋槽位；没有将银行数据或槽位逻辑加入公共运行库。

这是单次尝试场景，尚需显式包裹请求身份、已成交回放及拒绝/事务失败审计，完成对应冲正入口与声明式运行后才能替换旧入口。源查询、提交及新的完整场景仍需声明式银行端到端验收，旧 Java 基线不能替代该验收。


存入尝试场景与集合构造回归 `/tmp/spp-deposit-attempt.log`：`mvn -pl :xbod-deposit-demo -am test` 全部通过，lang 277、appframe 465、generator 96、demo 143，共 981 项，无失败、错误或跳过。该结果证明新增源场景可生成编译并保留旧基线，尚不证明新银行入口的纯源语言端到端行为。后续针对局部集合初始化、模型集合复制为局部数组的补充检查另记专项运行结果。

专项 `/tmp/spp-array-construction-final.log`：参与者构造语义及实际生成执行、场景集合传参共 6 项通过。覆盖空集合、null 元素、错误元素类型、标量/集合错配、原始数值局部集合错误初始化，以及模型 List 快照转成局部数组后再赋回模型。均为通用框架测试，demo 没有新增手写 Java。

## R3 可选查询缺失语义

APP 新增单记录 `optional` 修饰，生成的仓储查询元数据保留此声明。没有记录时返回空查询结果、保持查询键，不吞连接或反序列化等故障；必需查询仍报不存在。查询服务必须使用新构造的查询对象来区分缺失事实，不能复用上次已加载的数据。生成、语义检查及两种本地仓储已实现该通用能力。

存款费率查询改为 optional，缺失费率由 SPP 的 applyStoredDepositFeeRate 明确报 DEPOSIT_FEE_RATE_NOT_FOUND。这同时提供请求登记与已成交回放所需的缺失查询基础，但尚未完成请求生命周期和并发登记；不能据此宣称幂等已迁移。

回归 `/tmp/spp-optional-query.log`：完整生成编译和原有测试通过。专项 `/tmp/spp-optional-query-specific.log`、`/tmp/spp-optional-query-semantics.log` 共 4 项通过，覆盖标量约束、重复修饰/无仓储/集合目标拒绝，实际 H2 存储的存在与缺失、类型化和请求调用、必需查询拒绝缺失以及存储故障保留。没有新增 demo 手写 Java。旧银行 Java 基线仍须最终删除，新银行入口仍须声明式端到端验收。

## R2/R3 请求身份、待授权重试与成交回放

新增 `cboddeposit-98-deposit-lifecycle.spp`。executeCashDeposit 使用显式量子边界保留首次请求记录、重新加载并校验身份。身份比较包括账户、数值相等的金额、币种、日期、现金渠道及费上下文；授权证据、当日政策和演示分录配置不组成原 Entry 身份。已成交时复制原成交及其原/成交事实、计划、费用、积数和通知，单独提交 Replayed 审计，不重新加载账户或运行现行准入政策；未成交调用 97 的尝试场景，允许补充授权证据。

APP 显式 `idempotency business` 让存款场景自行管理生命周期，生成层保留追踪而不缓存一次待授权返回。新增通用 persist(insertIfAbsent)，不会覆盖已有请求；JDBC 在调用者事务内处理唯一键竞争，不另行开启或提交整笔业务。业务身份和回放政策全部留在 SPP，没有新增银行 Java。

这仍不是最终验收：拒绝/事务失败审计、对应现金冲正入口、源案例及运行启动必须继续迁移。尤其需要声明式银行案例证明同请求待授权后继续执行、异载荷拒绝、跨日/后续账户修改后的原成交回放及并发竞争。通用框架测试仅验证存储与生成机制，旧银行 Java 测试仍不是该证明。


请求生命周期回归 `/tmp/spp-deposit-lifecycle-final.log`：`mvn -pl :xbod-deposit-demo -am test` 完整通过。新增框架证据包括 insertIfAbsent 并发调用读取同一原记录、重复新增不覆盖并保留同边界的前后写入、外层失败恢复，以及业务管理场景相同追踪号仍继续执行并保留追踪。生成器实际编译、调用带唯一请求头和 idempotency business 的场景，第二次调用继续更新参与者并返回独立响应。银行新入口及其 APP/PHY 绑定可生成并编译，但纯源语言银行案例运行仍未实现，旧 143 项基线仍不能替代它。

## R2 现金冲正读取、计算与回放入口

新增 `cboddeposit-99-reversal-execution.spp`，构造冲正工作模型、八条原/反向分录及记录。通过返回值绑定读取原成交和实际持久化分录；按槽位装配实际分录并检查缺失/重复，再由已有服务核对成交证据。当前账户只读取一次，其版本由 93 的 CAS 提交校验，保留期间变化检测。核心账户资格、现金路径、费用返还、当前积数状态、明细及跨日规则继续使用原 XBOD 源服务，不改成通用余额还原。

新增 `cboddeposit-99b-reversal-lifecycle.spp`。executeCashReversal 先查询原冲正成交，核对冲正号/原交易号/overnightMode2 身份；成交回放只复制原证据并提交 ReversalReplayed 审计，不重算当前账户。首次调用进入完整准备及显式共同提交。原成交关联版本与账户版本继续在共同量子边界检查，不能重复撤销同一原成交。

通用语法新增 `participant.attribute = service(arguments);`，仅绑定恰有一个业务返回值，检查对象类型、集合维度及目标属性。生成器提取声明字段，业务不感知 Java 响应包装。费率可选查询及存款回放也改用准确返回值，缺失时直接为空，不依赖查询键内字段推测存在性。语义与限制见 [场景返回值绑定](../../../book/references/spp-scenario-results.md)。

这证明源语言可以表达现金冲正的读取与计算顺序；拒绝/失败审计、故障恢复、声明式案例运行及旧 Java 删除仍待完成。不能以新入口编译和旧测试通过替代其银行端到端验收。


现金冲正入口与返回值绑定回归：`mvn -pl :xbod-deposit-demo -am test` 在 `/tmp/spp-reversal-lifecycle-final.log` 全部通过，lang 283、appframe 470、generator 97、demo 143，共 993 项，无失败、错误或跳过。专项 `/tmp/spp-scene-results-tests.log` 3 项通过，包含类型/维度/多返回值/未知目标/按值参数拒绝，以及实际编译执行的标量、集合、可空结果、组、分支和事务。完整生成目录包含冲正尝试与回放，不手工修改产物。本结果仍包括未迁移的旧银行测试，纯源语言端到端案例和 Java 删除尚未完成。

## R2 失败审计与原错误传播

新增通用场景 try/catch 与重新抛出。catch 将原失败绑定到源声明的角色/合约事实；类型必须有 String code。SPP 决定调用哪些处理服务、声明哪些独立事务及是否 throw 原失败。框架不隐藏审计边界，处理本身失败时保留原异常并附加处理错误。语义见 [场景失败处理](../../../book/references/spp-scenario-failures.md)。

存款和冲正主入口显式包装 unchecked 执行场景。失败后分别调用 99c 的审计装配原子服务，并在独立 transaction quantum 中写入，再重新抛出原错误。尝试标识完整时才写入；缺失尝试标识仍返回原错误，不能凭空构造一个银行身份。工作上下文在新调用开始清除上次失败及结果，防止重试读取旧状态。

`cboddeposit-99c-failure-audit.spp` 根据准备、提交或回放阶段记录拒绝/失败事件及已有证据。CommitFailed/ReversalCommitFailed 描述观察到的失败阶段，不代表物理“已回滚”或“提交结果未知”的最终判定。原实现的 RolledBack/CommitOutcomeUnknown/CommittedResponseFailed 证据仍须通过通用提交结果支持与声明式故障案例迁移；不能仅根据源场景捕获错误推断最终状态。

公共专项 `/tmp/spp-scenario-failures-tests.log` 3 项通过：作用域及事实类型检查、实际生成 Java 编译执行、先回滚后独立审计提交、审计失败仍保留原异常并附加原因。没有新增或修改银行 Java。

补充请求入口验证：通用生成场景失败追踪改为 FAILED，避免将纯回滚或尚未确认的结果统一标成 COMPENSATED；真正 Saga 恢复记录继续由协调器产生。`/tmp/spp-trace-failure-test.log` 中，实际生成并编译的请求入口遇到业务失败与追踪存储同时失败，仍返回同一个原异常并附加追踪错误。该测试在公共生成器模块，未编写 demo Java。


失败审计与请求错误传播完整回归 `/tmp/spp-bank-failure-final.log`：`mvn -pl :xbod-deposit-demo -am test` 全部通过，lang 285、appframe 470、generator 98、demo 143，共 996 项，失败/错误/跳过均为 0。银行源包装、catch 事实绑定、显式审计边界及重新抛出均可生成编译。后续必须用源案例证明新银行路径及故障后的持久状态，并补充物理提交结果证据、自动启动与全部旧 Java 删除；当前 goal 仍 active。

## APP 样例入口迁移（进行中）

新增通用 APP `examples { run 场景名; }` 声明、语义检查、入口目录生成和框架运行器。银行样例的输入、独立预期值与执行步骤在 `cboddeposit-99d-source-examples.spp` 中；普通同分行现金存入样例声明账户初始化的量子事务，调用真实源存款生命周期，再查询账户与八条借贷记录校验。运行器不提供银行逻辑，也不对整个场景添加隐式事务。

本阶段首个真实运行结果见下文，不能将生成编译成功当作其他案例端到端通过。跨分行费率、透支、授权、冲正、失败与并发样例继续迁移。现存手写主程序和测试尚未删除，整个 demo 仍未达到纯源语言验收。

### 首个真实源验收结果

`GeneratedExampleRunner ordinaryCashExample` 已实际执行通过，输出 `PASS ordinaryCashExample` 与 `APP examples: 1 passed, 0 failed`。运行没有调用旧版 NormalCashDeposit/JdbcDepositStore 等银行 Java 入口；其业务输入构造、事务边界、执行顺序、查询和断言来自 99d SPP 文件及 APP/PHY 绑定。

这次真实加载也暴露并修复了三项通用问题：生成场景按子场景依赖排序注册；没有物理资源绑定的场景不套入破坏具体调用类型的事务代理；事务对象快照支持数组、空元素、原始类型数组和嵌套数组长度变更。通用测试覆盖入口选取/失败退出、目录顺序、场景依赖与循环拒绝、数组回滚。

样例范围为同分行普通现金存入，独立预期值为余额与计息基数 700、当日现金累计 600、明细数 11、账户版本 1、八条记录且借贷均为 600。尚不能以此声明跨分行收费、透支、授权续接、冲正、提交结果分类、失败注入或并发验收通过。

最终验证：`mvn -pl :xbod-deposit-demo -am package` 成功，lang 287、appframe 477、generator 99、demo 143，共 1006 项测试均通过。随后按 README 的类路径重新运行生成入口，普通现金存入样例独立通过。这里的 demo 143 项仍含旧手写测试，只作为迁移过程的回归证据。尚未进行删除旧 Java 后的干净构建验收。


## 验收证据更正：空 catch 导致空方法（2026-10-08）

本次新增故障入口要求“指定故障确实触发”，因此发现了生成器缺陷：空 `catch {}` 的执行列表为 null，渲染抛出空指针异常；模板反射吞掉异常，生成空场景方法。此前 replayCashExample、missingFeeCashExample、pendingCurrentAccountCashExample、crossDayCashReversalExample 的 PASS 没有实际执行业务，相关通过结论撤回。下文历史中的六/九/十/十二/十五/十六入口全通过，不能作为这些四个入口的验收证据。其他入口应以修复后的统一重跑为准。

修复将空分支按空列表处理，并在模板输出之前直接渲染、检查业务方法；渲染异常必须使生成失败。公共生成器回归使用通用业务模型，验证空 catch 后继续执行独立断言，以及渲染异常不能写出场景文件。99n 的故障未命中检查在修复前按预期拒绝空方法，不能把它计作通过。目前正在重新运行所有源入口，最终结果另行记录。

## 存款生命周期声明式验收（进行中）

`cboddeposit-99e-debt-examples.spp`、`cboddeposit-99f-authorization-examples.spp`、`cboddeposit-99g-replay-examples.spp` 新增普通透支、坏账、核销、授权续接和原请求重试五个入口。使用真实 `executeCashDeposit` 源生命周期，查询账户、成交、分录和独立审计，并以 SPP 校验服务给出独立预期：

- 同样的债务事实（利息 30、催收利息 40、本金 100）存入 50：普通账户先还利息，再还催收利息；坏账和核销账户先还本金。三类账户实际余额均从 -170 变为 -120，分录均借贷 50。
- 存入 1500 初需 B 级授权且不更新账户、不产生分录和成交；限额从 1000 降为 500 后，原 B 级证据仍不能执行；获得 A 级后才提交，余额 1600，累计现金 1500。每次尝试具有独立审计身份。
- 首笔存入 600 后再存入 100，次日以更严政策重试首笔返回原成交结果（700），实际账户保持后续结果（800、版本 2），不重复记账。把原请求金额改为 601 应拒绝并保留独立失败审计，账户不变。

上述预期已通过下文的真实源入口运行验证。尚不覆盖技术失败注入、并发、提交结果不确定、完整冲正和旧测试的全部分支。


五个新入口和上一轮普通入口已真实运行，输出 `APP examples: 6 passed, 0 failed`，银行业务与断言没有手写 Java。随后补 99h 跨分行费率查询/最低费用/分录及费率缺失的独立审计，99i 授权等待期间发生后续交易后重新检查当前余额限额。上述后续三个入口已加入下面的最终运行验证。


九个源入口最终全部真实通过，输出 `APP examples: 9 passed, 0 failed`；`mvn -pl :xbod-deposit-demo -am package` 回归 1006 项全部通过。新增 Maven `verify` 阶段自动执行全部 APP 样例，已验证其与生成目录及运行时类路径的集成。九个入口不是九个旧测试的简单替代：每个场景包含多次实际交易、查询及独立业务断言；剩余旧测试和主程序仍有完整迁移责任。


自动验收集成证据：`mvn -pl :xbod-deposit-demo -am verify -DskipTests` 成功，日志明确进入 `source-language-examples` 执行，九个入口逐个 PASS。这里跳过的是此前已回归的 JUnit，源入口仍实际运行；不是仅生成或打包。逐项覆盖和未完成责任见 `source-example-coverage.md`。Goal 继续保持活动，现金冲正、技术故障/版本冲突/并发、提交结果证据及删除全部旧 Java 尚未完成。

## 完整现金冲正源验收（进行中）

99j 新增 `crossDayCashReversalExample`，其 SPP fixture 明确构造银行资格、柜员、费率、正常/透支积数、五档协定事实，真实执行两个存款及首笔冲正。独立预期：初余额 100，首笔 600 后余额 700/积数 100；次日另存 100 后余额 800/积数 800；冲正首笔后余额 200，保留后续交易和积数 800，退原手续费 2，八条冲正记录借贷均为 602。跨日现金累计按 XBOD 原规则归零，明细数为 13，当前交易日保留次日。

样例继续次日重试同一冲正，检查账户版本仍为 3、记录不重复、返回原冲正业务日期，并以另一交易编号再次冲正原笔，要求 `ORIGINAL_DEPOSIT_ALREADY_REVERSED` 及独立拒绝审计。`mvn -pl :xbod-deposit-demo -am verify -DskipTests` 已实际运行全部十个入口，现金冲正也 PASS。此证据不代替透支及分数金额冲正、冲正技术失败/并发的后续责任。


同日及 Mode2 源路径已写入 99k：无后续成交时余额恢复为 100、版本 2、积数 100 保留，手续费仍退 2；同日恢复机构限额标记为真且交易日期还原为原笔之前的 20261006，Mode2 跨日不恢复机构限额且强制日期 20261008。正在通过 Maven verify 全量回归与源入口自动运行验证。


`mvn -pl :xbod-deposit-demo -am verify` 全量通过：1006 项既有回归与十二个实际源入口分别全部通过。之后仅增强 fixture 日期，以区分“还原原笔前日期”和“保持当前日期”；正在重新运行全部源入口，避免把日期未变化当作还原证据。旧手写 Java 仍未删除，整个 Goal 尚未达到纯源终态。


增强日期验证后的最终证据：`mvn -pl :xbod-deposit-demo -am verify -DskipTests` 全部十二个源入口通过。同日冲正确实从原成交日期 20261007 恢复到前次交易日期 20261006；Mode2 在相同前次日期下强制写入 20261008。跨日且有后续交易仍保存当前日期、后续余额及积数。这里验证的是源 metadata 的机构限额恢复标记，不宣称已实现未纳入 demo 的机构限额账簿更新。

## 透支及小数现金冲正

99l 新增普通透支、坏账和三位小数金额的真实现金冲正，十五个源入口已在 Maven verify 中全部通过。普通/坏账余额 -170 → -120 → -170；独立校验原利息 30、催收利息 40、本金和敞口 100 的恢复，以及原有透支积数 100 和利息积数 70 的保留。小数案例本金 0.01、利息 0.005、催收利息 0.004，存入 0.01 偿还分量分别 0.005、0.004、0.001，余额 -0.019 → -0.009 → -0.019；分录借贷各 2.01（含原手续费 2）。数字表达式和独立断言均在 SPP 中，没有 demo Java 数字处理。

## 版本冲突及部分提交撤销（进行中）

97 将读取事实和生成候选提取为 `prepareCashDepositAttempt`，实际入口继续显式选择待授权审计或 `commitCashDepositRecords`；原业务边界、事务模式及失败阶段保持一致。99m 先提交存款 600，基于版本 1 准备另一笔 100，再让实际存款 200 提交到版本 2，最后提交旧候选。候选使用同一真实提交场景，先插成交记录、再执行版本保护；若第二步冲突，第一步必须撤销，且由源 catch 的独立 quantum 事务记录 CommitFailed。

验收预期：当前账户保持版本 2、余额 900、当日累计 800；候选成交、分录、冲正关联均不存在；独立失败审计 code=PERSISTENCE_VERSION_CONFLICT。此案例采用确定的源步骤交错验证过期版本，不宣称已验证并发调度、通信故障、提交结果不确定或数据库在提交点的技术失败。


版本冲突源验收结果：`mvn -pl :xbod-deposit-demo -am verify` 成功，1006 项回归及十六个源入口均通过，99m 的候选成交撤销和独立失败审计已有实际读回证据。随后加强失败后继续成功存入 50 的验证，预期余额 950、版本 3、当日累计 850，证明账本仍可正常执行量子移动与银行共同提交；正在重新运行源入口。


补强结果：`mvn -pl :xbod-deposit-demo -am verify -DskipTests` 再次成功，十六个入口实际通过。99m 在旧候选失败并独立保存审计后继续实际存入 50，共同提交成功，读回余额 950、版本 3、当日累计 850；量子余额与提议余额的一致性检查也在该真实提交中通过。物理提交点故障、提交结果不确定、并发完整入口、剩余规则与报告、删除全部旧 Java 仍未完成，Goal 保持活动。

## 声明式技术故障验收（进行中）

APP examples 新增 `fault before/after 原子服务`，由通用运行器按入口作用域启用一次性技术故障。没有银行专属框架逻辑，也不改写业务恢复策略。99n 在 `storeCashPostingRecords` 实际写入分录后抛出故障，此时成交、账户更新和八条分录均已经在真实 quantum 事务内执行。SPP 存款生命周期捕获失败，独立 quantum 事务保存 CommitFailed，再把原失败返回验收场景。

源预期：账户恢复版本 0、余额 100、累计 0，成交/分录/关联不存在，独立失败审计 code=EXAMPLE_SERVICE_FAULT；随后原请求换尝试编号重试并真实提交，版本 1、余额 700、累计 600、八条借贷记录各 600。运行器还会检查指定故障确实触发；技术资源提交点失败及未知结果不由此案例代替。


## 空分支修复后的统一重跑证据

`mvn -pl :xbod-deposit-demo -am verify` 在空 catch 修复后成功完成：lang 289、appframe 482、generator 101、旧 demo 143，共 1015 项回归；APP 独立执行 17 个源入口，全部通过。四个旧假阳性入口在本次确实生成并执行了完整方法，拒绝、重试及冲正断言已有重新执行的证据。99n 指定故障也确实命中，实际存储读回确认事务内成交、账户和分录撤销、独立失败审计保留，原请求随后重试提交成功。

本结果取代上文受空 catch 缺陷影响的历史通过结论。仍有 14 个主 Java 和 21 个测试 Java 待删除；尚未完成全部纯源语言验收，Goal 保持活动。


## 日历和利息单位的源验收迁移（进行中）

99o 新增 bankCalendarExampleRun，完整承接 BankCalendarTest 的四项测试责任：8 个 ACT 闰年/世纪年/跨年/同日边界，360365 和 360360 各 7 个独立预期，5 个无效日期以及空日期、逆序期间、未知约定的业务错误码，最后验证 199.999 按 100 单位向下取整和 10/3 按 3 单位向下取整。总计 30 组日期事实与 2 组数字计算断言，全部在 SPP 中逐次构造、调用、捕获和校验；APP 只声明本地服务及运行入口。

这些案例直接调用生成的 decodeBankDate，而不是旧手写 BankDateDecoder。正在运行统一源入口验收；通过后删除旧 BankCalendarTest，并从干净目录构建确认无陈旧测试字节码。其他旧测试的责任不因此免除。


日历迁移干净验收结果：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 289、appframe 482、generator 101、剩余旧 demo 139，共 1011 项回归全部通过；18 个 APP 源入口另行全部通过。target 从空目录生成，已确认 BankCalendarTest.class 不存在。减少的 4 项旧 JUnit 方法已由 32 组源断言完整承接，不是删除验收责任。当前手写文件实际核对为主 Java 14 个、测试 Java 20 个，Goal 仍活动，继续迁移其余责任。

运行脚本已切换到公共 GeneratedExampleRunner，不再调用银行专属 Java 演示主程序；参数是 APP 声明入口名。旧银行报告功能仍须用声明式方式迁移，文档保留其历史配置与独立预期。


## 存款内核独立源验收（进行中）

99p 的 depositKernelExampleRun 承接 DepositKernelTest 的十六组参数：十五组金额分配与一组负金额拒绝。成功组逐项验证九个计划输出，所有组逐项验证八个账户输入字段与复制快照相同；负金额要求 E1095 且计划余额仍为空。覆盖普通/坏账/核销偿还顺序、全部及部分偿还、精确本金边界、冻结与授权扣减、三位小数和零金额内核行为。输入与期望为旧独立表中的常量，未用被测公式反算期望。

旧测试的 Java 类型反射检查属于物理表示验证，不应放入业务 SPP。PHY 的 `numeric double as BigDecimal` 继续作为具体类型绑定来源；源小数计算与编译产物类型另行核对。正在运行新增源入口，完整通过后删除旧参数化 Java 测试并从空目录构建。


## 五档协定积数源验收（进行中）

99q 声明验收参与者、独立校验和入口；99qa/99qb/99qc 分别提供模式、精度边界和拒绝事实，避免一个 SPP 文件集中所有 fixture。17 组案例承接 AgreementProductTest 的六项方法：模式 2 分档、模式 1 精确阈值与后续模式 2 清除旧产品、四种币种默认/显式模式、禁用/零交集/阈值以下、分段独立量化、五槽数量/顺序/阈值/期间错误。成功组检查全部五个结果字段及五槽产品；拒绝组检查错误码、未产生普通积数、所有槽仍为 999。

样例只使用已有参与者集合构造 `new AgreementBand[] { ... }`、增强 for 和 switch。按长度分配及下标赋值不是现有业务语法，本例可由固定五槽集合直接表达，无需添加 Java 实现或扩大语法。此轮正在运行新增验收，旧 Java 测试暂未删除。


内核与协定迁移的干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，lang 289、appframe 482、generator 101、剩余旧 demo 117，共 989 项回归全部通过；20 个 APP 源入口另行全部通过。协定源案例 03 实际复用案例 02 的五槽集合，先确认档 5 的原产品为 2000，再由模式 2 将其清零，其余产品与 1600 总数独立核对。生成、编译及运行来自清空后的 target；BankCalendarTest、DepositKernelTest、AgreementProductTest 的旧 class 均不存在。

本次删除的是旧内核十六组参数和协定六项方法的 Java 文件，责任已用源场景完整承接；不以回归总数减少宣称覆盖率变化。当前实际库存主 Java 14 个、测试 Java 18 个，剩余资格、冲正、报告及事务存储测试仍引用旧入口，继续逐项迁移。Goal 保持活动。


## 日期窗口、账户控制和现金准入（进行中）

99r 的 datedAgreementExampleRun 已实际通过七组有效/空窗口及一组非法生效日期，检查普通期间 10 天、协定交集、两类积数和裁剪后的起止日期。99s 的 cashAccountControlExampleRun 已实际通过正常控制、三种 EN432、冻结状态 EG877、取消 EN113、房地产账户 EI090，并验证冻结金额 10 下新存 1 的可用余额仍为 1。二十二个 APP 入口已全部成功；对应旧测试尚待删除后干净核实。

99t 与 99ta/99tb/99tc 进一步迁入 BankRulesTest 的全部十二项方法，展开为四十九组独立输入和预期：现金正金额/日期、临时户、开户上下限、禁用限额、净余额上限、警告/换日累计、严格 B/A 阈值、授权后政策重验、六个原交易例外及两种渠道例外、USD 专用阈值、利息单位和控制先于准入。待授权场景还真实调用授权校验并捕获 PENDING_AUTHORIZATION；控制拒绝检查后续 decision 未被计算。fixture 数据与独立校验按准入、授权及其他规则拆分。

这一轮使用已有 SPP/APP/PHY 生成链路，没有增加 demo Java 或银行脚本，正在运行四十九组规则和全部源入口。尚未宣称银行权限查询、多重非法事实优先级、并发和物理提交点失败已经验收。


日期窗口、控制和准入的最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 289、appframe 482、generator 101、剩余旧 demo 97，共 969 项回归全部通过；23 个 APP 源入口另行全部通过。新增源责任为八组协议窗口、完整控制拒绝/正常行为以及四十九组现金准入。target 从空目录生成，六份已迁移旧测试的 class 全部不存在。旧测试方法数减少二十，不能与源入口数相加，也不表示业务责任被移除。

目前实际库存主 Java 14 个、测试 Java 15 个。完整银行资格、收费查询、积数持久化、冲正/恢复与存储故障、并发、跨进程幂等、结果未知及报告责任仍继续迁移，不能宣布最终纯源验收完成。Goal 保持活动。


## 银行资格、原成交提示和 XBOD 现金政策（进行中）

99u/99ua/b/c 将 DepositBankQualificationTest 的关系、权限和提示展开为五十四组纯源事实：独立分行/支行/市/省关系，缺失关系明确失败，普通/限制子类的不同作用域，UH/O/ZD 柜员数值边界，十三种交易与三种业务例外，以及卡/折独立挂失提示。默认事实来自旧独立样例配置的常量，不由被测规则反算预期。

99v 用真实源存款入口执行带 WN200/WN201 的成交，查询账户、成交、分录和审计；改变代理签约标记后重试仍必须返回原提示与原柜员事实，不重复更新。另一入口顺次验证分行 EN134 与柜员上下文不一致，检查账户版本/余额不变、成交/分录不存在及独立 Rejected 审计。初始化复用现有银行事实与积数 fixture，完整提交仍来自 SPP 的 quantum 边界。

99w 将 XbodCashReversalPolicyTest 的五项方法转成八组源数据：四种日期/明细/隔夜边界，一组积数不足 EN097，以及手续费 0、2、1.005 的原实际金额退款。当前/原事实均在 SPP 中构造，独立预期与输入未修改的断言在校验服务中。正在运行全部二十七个 APP 源入口；旧对应测试尚未删除。


银行资格与现金政策的干净结果：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 289、appframe 482、generator 101、剩余旧 demo 84，共 956 项回归全部通过；27 个 APP 源入口另行全部通过。五十四组资格/提示、真实收费与积数存款的原提示重放、两种拒绝无更新及八组 XBOD 政策，均从清空后的 target 生成并执行。退款新增独立 0/2/1.005 常量与原费用未变校验，也全部通过。

八份已迁移测试 class 均确认不存在；本轮删除银行资格八项与现金政策五项方法的旧文件，责任继续由源验收承担。当前库存主 Java 14 个、测试 Java 13 个；完整银行查询权限、未覆盖资格优先级、其余费用/积数/冲正/事务/报告与全部 Java 删除尚未完成。Goal 保持活动。


## 收费库与金融反向分量（进行中）

99x/99xa/b 使用真实 APP 仓库种入每组独立客户/收费代码的费率，完整调用 prepareDepositFee。十六组案例承接 DepositFeeTest 五项方法：同机构免收、同区/异区代码（异区优先）、比例折扣后显式半入再加固定费用、最低/最高/零上限、Mobile 无查询、未迁账户类别、缺少费率、代码不匹配和负金额。费用和变量额的预期均为独立常量；收费配置种入的事务在 SPP 声明 quantum，不以 Java Map 假查询替代仓库。

99y/99ya/b 承接 DepositReversalAmountsTest 七项方法，展开为十组原账与当前账事实。先实际运行存款内核并记录原数学分量，再对当前账做反交易；七个计划字段与独立常量逐项比较，所有当前账户八字段均校验不变。覆盖后续支出/存入、当前冻结与授权、当次贷款状态改变不重分配、原敞口钳制的实际增量、小数偿还、容量/结果资格拒绝和伪造原分量；早期失败要求计划未生成。

正在执行二十九个源入口；旧两份测试尚未删除。金融反向计算的通过不等于已经完成整笔冲正、历史积数调整或业务补偿。


收费与金融反向的干净结果：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 289、appframe 482、generator 101、剩余旧 demo 72，共 944 项回归全部通过；29 个 APP 源入口另行全部通过。十六组真实仓储费率收费与十组原/当前账户反向事实均从清空后的 target 生成执行，独立结果、输入不变性和早期拒绝断言都通过。

十份已迁移测试 class 均确认不存在；本轮删除旧收费五项及反向七项方法的文件，源验收承担对应责任。当前库存主 Java 14 个、测试 Java 11 个。分录 fixture 仍被整笔存款与 JDBC 仓储测试引用，需一起迁移；积数、资格/完整冲正、Saga、存储并发/故障/结果、跨进程与报告以及全部 Java 删除仍未完成，Goal 保持活动。

## 积数源验收与事务结果证据（进行中）

99z 将旧 DepositAccrualTest 的纯计算责任迁成四组源事实：旧金额上的协议窗口、正常 360 与透支 ACT 日历分别使用、normalUnit=3 和 overdraftUnit=0.01 的显式量化，以及只有催收利息时不增加透支利息天数。预期来自旧测试的独立常量；输入积数与五档原产品保持不变。

99za 的三个真实交易入口使用完整 SPP quantum 提交，覆盖账户与积数共同成交、原计息区间持久化、同笔重试不重复积数、同日第二笔零区间、无效单位拒绝，以及账户/积数更新后、写分录前的技术故障和原业务身份重试。故障通过 APP 的通用声明注入，要求实际命中 storeCashPostingRecords；不是在 demo 手写 DataSource 或 PreparedStatement 代理。

公共运行层新增可选 catch 事实 transactionOutcome，仅报告技术证据，不定义银行审计政策。未发起 commit 且 JDBC rollback 返回可报告 ROLLED_BACK；commit 抛错即使 rollback 返回仍为 UNKNOWN；commit 返回后清理失败为 COMMITTED；参与者恢复失败或边界资源结果冲突不能宣称整体回滚。无证据为 UNREPORTED。原异常身份和 suppressed 原因保留。银行事件由 99c 源分支选择，版本冲突/写入故障的源断言相应要求 RolledBack。当前不宣称未上报后端或远程协议具备确定结果证明。

新增九项 JDBC 通用证据测试已通过，另补参与者恢复失败的保守合并回归；正在运行完整生成链路。四个新增入口尚未取得最终干净结果，旧积数测试仍保留，不能据此宣称迁移完成。

首轮执行：33 个入口中 31 个通过，新增正常积数和故障后重试在额外的分录总额预期上失败。旧测试没有该分录断言；新断言误写借贷各 50，实际源内核使用当次现金 50 与原存款减少 120 偿还本金 100、普通利息 30、催收利息 40，借贷应各 170。已修正为独立常量并增加对应槽金额断言，重新执行；未减少原业务责任，也未删除旧积数测试。


修正后的完整 verify 成功，33 个 APP 入口均实际通过；新增四个积数入口完整承接旧六项方法后，已删除 DepositAccrualTest。又补 99zb 的纯审计分类规则：七组存款/冲正配对事实覆盖四种结果证据及重放、提交前拒绝、缺少工作上下文。它只验证源政策，物理结果证明仍来自后端测试；不会把 fixture 构造当作确定事务结果。正在清空所有 target 后执行 clean verify，预期 34 个源入口，最终结果尚待取得。当前手写库存为主 Java 14、测试 Java 10，全部删除目标仍未达成。


积数与事务结果证据的最终干净结果：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 290、appframe 494、generator 101、剩余旧 demo 66，共 951 项 JUnit 全部通过且无跳过；34 个 APP 源入口另行全部通过。四个积数入口和七组配对审计政策均在清空后的 target 生成执行。十一份已替代旧测试的 class（包括嵌套 class）全部确认不存在。当前库存仍为主 Java 14、测试 Java 10，全部删除目标仍未达成，Goal 保持活动。

公共层本轮实际新增 12 项测试：11 项 JDBC 结果证据（含部分资源提交、同资源加入、身份弱引用区分、循环原因链和未测量后续操作）及 1 项参与者恢复失败；语言层新增 1 项可选 transactionOutcome 的类型检查。它们不含银行专属实现。现金冲正资格与准备、分录责任、Saga、持久化关闭重开/并发/物理提交点故障/结果核对、报告与剩余 Java 删除继续实施；本轮成功不能作为这些缺口已验收的证据。

## 核心冲正资格与只读候选准备（进行中）

99ca 将旧 DepositReversalPreparation Java 的查询和组合责任迁为三个业务源入口：prepareFinancialDepositReversal、prepareCoreQualifiedDepositReversal、prepareFinancialDepositReversalPostings。原成交及当前账户由 APP 查询绑定读回，容量/操作者/渠道/退款决定用 SPP copy 保存独立候选事实；数学、核心资格、账簿证据和反向分录复用既有 SPP 服务。它们只准备候选，不写账户、分录、审计或冲正关联，不能冒充新交易提交。

99zc 的核心资格源规则覆盖关闭 EO082、注销 EN113、冻结 EN111、SA01116 冻结例外、注销不被该例外豁免、核心冲正的文档提示不继承普通存入机构范围门槛，以及核心校验不继承前端 institution/control 限制。99zd 用真实存款和后续存款，源 quantum CAS 更新当前冻结/挂失/范围事实，再查询核心候选；必须保留后续余额与积数、保存当次操作者/容量快照、再次注销后拒绝。查询实际审计、原分录和关联以核验准备不产生提交副作用。

首轮解析发现当前多文件链路在结果绑定时需要类型字段已定义；新文件原名 87 先于 CashReversalWork 的 99 声明，导致字段解析失败，现改为 99ca 位于其定义之后。没有使用银行 Java 绕行，任意文件顺序的跨文件字段解析仍是编译器能力限制，未宣称本轮已消除。正在运行全部 36 个源入口；旧资格及准备测试暂保留。三个新准备入口中的完整金融/分录准备分支仍需后续独立源验收，不能仅由核心资格案例通过推断全部完成。

第二轮解析还发现新例子的辅助 Scenario 放在调用者之后，会将前向服务占位符按 SppScenario 转换而失败；现将辅助场景移到入口前，遵循当前先定义后调用的支持范围。此调整不改变业务流程或断言；未宣称任意跨文件/场景定义顺序受支持。再次运行真实生成链路，旧资格测试仍未删除。

按定义顺序调整后，完整 verify 成功，36 个 APP 入口全部实际通过。核心资格四项旧责任已由两份源场景承接，DepositReversalEligibilityTest 已删除，正在 clean verify 检查十二份已删除测试均无残留字节码。当前库存主 Java 14、测试 Java 9，整体纯源验收仍未完成。

下一批原分录准备验收还需要构造真实缺失分录：现有 APP persist 支持 insert/insertIfAbsent/update/upsert，没有 delete；ObjectRepository 同样缺少删除契约。应完善通用删除声明、事务内删除执行、语义与生成验证，再用 SPP/APP fixture 删除实际存储的原分录，不能以手工 JDBC DELETE 或只替换返回数组绕行。退款决定缺失的检查顺序及完整准备不写账户/积数/审计的责任亦需保留。


核心冲正资格阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 290、appframe 494、generator 101、剩余旧 demo 62，共 947 项 JUnit 全部通过无跳过；36 个 APP 源入口另行全部通过。十二份已替代旧测试的 class（含嵌套类）全部不存在。新的核心资格和当前事实案例均在清空 target 后生成执行；当前手写库存主 Java 14、测试 Java 9，整体纯源要求尚未满足，Goal 继续活动。

只读金融/分录准备的其余八项责任、实际存储删除/证据破坏、提交点和结果核对、并发、Saga/补偿与报告仍继续实施。此次没有新增 demo Java，也没有把银行查询或资格逻辑迁入公共 Java 运行库。

## 通用删除与原成交/分录候选准备（进行中）

APP 增加 persist(delete, argument(...))，生成 DELETE 写入元数据；同步本地更新服务必须加入源声明事务，支持标量/一维集合和复合键，记录缺失明确报错。删除不继承 update 的 compareVersion，编译及运行层都拒绝忽略版本条件。JDBC 锁定原快照，再删除快照与映射原生表，原生键来自实际快照；原生约束失败或后续批量删除失败必须整体恢复。解码原生小数键使用 BigDecimal，避免将精确键转为 double。通用默认后端未支持删除时明确报错，不定义银行业务逆操作。

框架删除验证已通过：标量边界/缺失/保留其他行、集合后续失败恢复、非法版本元数据、复合快照/原生表共同删除与回滚、原生外键失败恢复。语言验证检查生成元数据与非法版本绑定；生成器测试实际编译执行删除服务及幂等重试不重复删除。首轮原生表测试 fixture 使用无默认构造器的 Java record，读回链路按生成模型要求实例化而失败；已改用与生成模型一致的 Bean，并保持原生查询及恢复断言。另补精确小数原生键验证，将随完整检查执行。

99ze/99zf/99zg 新增八个源入口承接旧 DepositReversalPreparationTest 八项方法：原存入 600、授权存入 1500、原笔重放、下一营业日 100 形成当前版本 3/余额 2300/普通产品 2200；金融候选反向原 600 得到 1700，仍不提交，操作者/容量/费用决定独立复制。原成功/重放两条审计、八条借贷各 602 的实际原分录、未冲正关联必须保持。退款 0/1.25/2 明确提供，普通/呆账/三位小数来自实际成交与实际分录。未知原笔、实际拒绝原笔、容量不足、缺少/负数/超过原费的决定，以及实际修改成交/分录和删除第 8 条分录都必须拒绝候选。

首轮银行生成发现字符串 + 仍被数学语义拒绝，尽管生成器已有字符串拼接路径。现完善 String + String 的类型验证，保留字符串类型，混合数字及减法仍拒绝；新增通用语义回归。没有用硬编码 Java 编号构造器绕过源表达。所有角色编号及后缀仍在 SPP 构造。正在运行全部 44 个源入口，旧八项准备测试尚未删除，不能宣称该责任已完成。


第一轮实际执行为 39/44：三个债务/小数入口及原有入口通过，五个共享现金 fixture 的入口失败。复核发现复用了跨日冲正 fixture 的初始计息日 20261006，而旧准备测试的初始计息日为 20261007；前者会额外累积原余额 100 的一天产品，不能套用旧测试的 2200。现仅在新准备 fixture 明确设置 lastProductDate 和 lastTransactionDate 为 20261007，保留独立产品 2200、余额 2300 和反向余额 1700 的断言，重新执行。未改原跨日冲正案例，也未降低准备不提交的要求。


后续迁移依赖核查：NormalCashDepositTest 的基本成交/三种偿还、授权策略重新校验、等待期间账户变更、重放保留原结果、身份复用拒绝及费率缺失已有源入口，但仍缺同日累计警告与次日重置的完整成交入口、重新启动后读取待授权身份、等价数字格式的真实并发提交证据。DepositPostingTest 同时是旧仓储和整笔存款的 fixture，不能单独删除。CashDepositReversalTest 的报告断言仍依赖旧入口，Saga 的六项责任还依赖 ExplicitSagaStep。后续必须完善通用执行/恢复/报告能力并验证这些责任，不能只凭现有顺序入口通过删除所有 Java。另需检查源准备的原成交账户一致性，旧 load 曾明确拒绝 INVALID_ORIGINAL_DEPOSIT_ACCOUNT；现有新入口尚未覆盖该异常事实。


日期一致后完整 verify 成功：44 个 APP 入口全部通过；通用框架 501 项测试含精确小数删除键亦通过。旧准备八项方法已由新源责任承接，DepositReversalPreparationTest 已删除。进一步在 prepareCashReversalQueries 明确检查原/成交账户 id 与原交易账户一致，在已有存储证据入口实际修改原账户 id，要求 INVALID_ORIGINAL_DEPOSIT_ACCOUNT 并保留当前账户、积数、审计及分录。此追加异常责任和已删除旧测试的字节码清理正在 clean verify 中验证。当前库存主 Java 14、测试 Java 8；完整纯源目标仍未达到。


原成交/分录准备阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，lang 292、appframe 501、generator 101、剩余旧 demo 54，共 948 项 JUnit 无失败、错误或跳过；44 个 APP 源入口另行全部通过。实际原账户身份篡改亦拒绝 INVALID_ORIGINAL_DEPOSIT_ACCOUNT，账户/积数/审计/原分录保持。十三份已删除测试（含嵌套类）均无残留 class。当前手写库存主 Java 14、测试 Java 8，目标仍未完成，Goal 保持活动；重启、并发、银行提交点结果、Saga/业务恢复和报告责任继续实施。


## 完整换日累计与真实并发身份（实施中）

上一阶段为明确进展：清空 target 后 948 项回归和 44 个源入口全部成功，旧准备测试已删除。接续 NormalCashDepositTest 的剩余完整交易责任，99zh 新增真实 300/300/次日 100：逐笔保存并查询原成交、账户、分录和审计；必须 Ready→Warning→Ready，余额 400/700/800，当日现金 300/600/100，次日转账累计清零、日期更新和明细数 13。

99zi 使用两套独立请求/生命周期、同一账户和业务身份，以及源数字 600.00 与 600；SPP parallel 调用完整现金生命周期。为证明实际并发，APP examples 增加通用 barrier before 原子服务 N，生成目录传递目标及参与数；运行器只在样例实例启用代理，目标前首次 N 路同步，30 秒未到齐或未执行目标均失败，不隐藏事务/业务策略。当前入口选 initializeCashDepositExecution，即两路都已读取缺失成交且尚未持有提交锁时会合，确保验收不是先成交后再顺序重放。结果要求同一原成交、版本 1/余额 700、八条借贷各 600 分录、一条成交加一条重放审计。框架另验证屏障跨线程、超时、一次性和作用域清理，语言验证数量/目标/与 fault 不兼容，生成验证元数据。正在真实生成执行，尚未删除整笔存款测试；若并发路径发现缺口，须修正 SPP 的业务重读/身份处理，不能由公共 Java 代替银行重试。


首轮实际执行 45/46：完整日累计与原 44 个入口通过，并发入口失败于 CashDepositTrade 的真实主键竞争（PERSISTENCE_ALREADY_EXISTS）。说明现有源生命周期尚未承接旧实现的同身份竞争后结果查询。现直接在 98 的 SPP 中表达：保存 submissionFailure；提交尝试报告已存在后，退出失败事务，再按原业务 id 查询原成交；只有存在原成交时生成重放结果，并在独立 quantum 边界写本次 Replayed 审计；查不到或其他错误继续抛原失败，外围失败审计策略不变。没有增加银行 Java 锁或重试器。并发源断言同时要求恰好一条实际竞争失败事实、PERSISTENCE_ALREADY_EXISTS 及测量得到的 ROLLED_BACK，证明已执行竞争分支而非偶然顺序重放。修正后正在重新运行全部入口。


换日及并发阶段最终证据：`mvn -pl :xbod-deposit-demo -am verify` 成功，lang 293、appframe 504、generator 101、剩余旧 demo 54，共 952 项 JUnit 无失败/错误/跳过；46 个 APP 入口另行全部通过。新增换日入口逐笔通过 Ready→Warning→Ready、日累计与入库事实；并发入口通过两种精确数字表示、屏障实际会合、恰好一次 PERSISTENCE_ALREADY_EXISTS/ROLLED_BACK、查询原成交并返回同一结果、账户与分录仅一次更新、一条 Committed 与一条 Replayed。普通业务运行不启用屏障。新语义与生成目录以及运行支持均有通用框架验证。当前库存主 Java 14、测试 Java 8 未改变；NormalCashDepositTest 的跨运行实例/待授权身份仍未全部替代，不能删除它或宣布纯源验收完成。下一批继续跨进程、竞争无原成交的拒绝分支、提交点结果、Saga/业务恢复及报告。


## 待授权身份的跨 JVM 持久性与未成交冲突（实施中）

通用 APP examples 增加两阶段 restart；生成两套请求/参与者元数据与 PHY 数据源属性，公共运行器依次启动独立 JVM、各自空请求和参与者、新请求头，不复制 Java 对象。默认生成唯一 H2 文件 URL，共享给声明属性和框架存储；使用既有显式外部 URL 时沿用。日志及默认文件数据库保留于 target/spp-examples。第一阶段失败不得启动第二阶段，第二阶段失败或超时不得报告整体成功，普通业务事务仍由源描述。

语言检查同步本地场景、参与者、与 fault/barrier 不兼容，生成目录保存后续服务及配置。公共测试用进程 id 与数据库行证明真正独立进程、持久读回及空状态，并验证两种失败路径。首轮 fixture SQL 误用 H2 保留字 value 作列名导致两项失败，已改为 stored_value，保持原证明断言，通用测试全部通过。银行第一轮集成发现既有属性 spp.xbod.datasource-url 含连字符，qualifiedName 无法表达，现支持 quoted using 配置属性并补通用语义验证；不改既有 PHY 属性名。

99zj 新源阶段一显式 quantum 种入，等待授权后查询持久身份/空成交空分录和等待审计；阶段二新进程先查询这些已存事实，改金额 1501 复用身份拒绝且原 1500 不变，授权 B 后成交 1600/v1，再用 1500.00、更严政策和次日营业日重放，账户/分录仍一次，四条尝试为等待/拒绝/成交/重放。第二阶段不会靠上一进程的 lifecycle.execution 得到等待状态。

99zk 是竞争恢复的负例：在源 quantum fixture 中预存一条孤立分录，让真实成交尝试在账户更新后、分录插入时遇到主键冲突；失败事务须确定回滚，查不到原成交时原异常继续抛出，当前账户 v0/100、空成交和原一条 fixture 分录保持，仅留下 RolledBack 审计和原请求身份。收费及真实 Locked 拒绝现另行查询持久身份；跨分行收费入口查询保存的原事实与 fee=2。正在执行全部 48 个入口；NormalCashDepositTest 仍保留，待全部旧九项责任确认后才删除。


首轮 quoted 属性修正后的完整 verify 已成功：48 个入口全部通过，两个子 JVM 分别通过等待种入与重启后拒绝/授权/重放，实际阶段日志位于 target/spp-examples/restart-1061934216006567257。未成交分录冲突负例亦实际通过确定回滚、原成交缺失、原异常重抛、账户/孤立分录保持及失败审计。

已对照旧 NormalCashDepositTest 九项责任：基本成交/存储原事实/收费、三类偿还、授权政策改变、等待期间账户改变、后续状态/政策下原请求重放、完整同日/次日累计、拒绝及费率缺失身份保留、跨 JVM 等待身份、真实同步等价金额竞争均有源证据。补授权场景整体三条审计查询（两次等待、一笔成交），通用跨 JVM 配置传递涵盖自定义应用属性并加证明，不限于 spp./example. 前缀。删除 NormalCashDepositTest 后正在 clean verify 检查十四份已替代旧测试均无残留 class；当前库存主 Java 14、测试 Java 7，仍需继续仓储/提交点结果、Saga、量子日志和报告迁移。


跨 JVM 等待身份阶段最终干净证据：`mvn -pl :xbod-deposit-demo -am clean verify` 成功；lang 294、appframe 507、generator 101、剩余旧 demo 45，共 947 项 JUnit 无失败/错误/跳过；48 个 APP 入口另行全部通过，其中等待种入与重启续接两个独立 JVM 阶段分别通过。实际阶段日志为 target/spp-examples/restart-5696792022188799453/stage-0.log、stage-1.log。授权历史三条（两次等待、一笔成交）、拒绝/费率缺失身份读回、原收费事实、未成交冲突确定回滚及原异常保持均在清空 target 后实际执行。十四份已迁移旧测试（含嵌套类）均无残留 class。当前手写库存主 Java 14、测试 Java 7，全部删除目标尚未完成，Goal 保持活动；下一批继续提交点结果、Saga/业务恢复、量子日志与报告。


## JDBC 提交点的真实源故障（实施中）

上一阶段 clean verify 947 项回归与 48 个源入口及跨 JVM 身份均成功，属于明确进展。本阶段承接旧仓储的提交点与结果责任：通用 APP jdbcFault 锁定目标 atomic update 首次成功后的唯一活动 JDBC 连接，只在该事务到指定点时触发一次。beforeCommit=提交前检查点，回滚返回则 ROLLED_BACK；commitBefore=提交调用中物理提交前报连接错，调用者只能 UNKNOWN；commitAfter=物理提交后丢失确认，调用者仍 UNKNOWN；afterCommit=已确认提交后的返回失败，为 COMMITTED，不再调用 rollback。业务选择、查询与恢复保持在 SPP。没有银行 DataSource/Connection 代理或硬编码存款故障器。缺目标、无事务、多活动连接、时点未实际触达皆失败，初版不与其他 examples 控制混合。

语言第一轮遇到 jdbcFault 三个 Identifier 被普通 fault 的宽松规则吸收，语义错误地报告 fault timing；现以局部 parser predicate 排除该上下文标记，保持 jdbcFault 可作为普通 Identifier，补语义回归。生成目录保存目标和时点，通用运行测试实际验证四种数据结果及事务证据、已确认成交不调用 rollback、目标事务以前不消耗故障、同作用域重试一次性、无目标/无事务/多连接不冒充触发。通用测试完整成功。

99zl 四个银行入口以完整 source quantum 写账户、成交、分录、关联、守恒及成功审计；APP 故障锚定 storeCashAudit，因此种入与身份登记事务不消耗故障。SPP catch 查询实际结果：未提交 v0/100、空成交/分录/关联；已提交 v1/700、八条借贷各 600、未冲正关联；业务审计按实测 ROLLED_BACK/UNKNOWN/COMMITTED 分类。提交调用前后两种连接故障都叫 EXAMPLE_JDBC_COMMIT_FAULT，不能按注入名字推断状态，必须查询。随后以稳定业务 id、新尝试 id 重试及 600.00 重放，最终只一次成交。

发现原 APP 审计键只用 attemptId，会使同次尝试的 Committed 与 CommitUnknown/CommittedResponseFailed 两条事件冲突。现由 APP 明确 composite(attemptId,event)，SPP 审计政策不变；新源案例查询整个历史，不用单事件查询猜测唯一行。旧 Java 的 CommitOutcomeUnknown 名称与当前源 CommitUnknown 映射记录为审计命名差异，结果语义保持。正在运行全部 52 个入口，旧仓储/完整冲正/Saga/报告测试仍未删除；不得凭当前通用框架测试直接宣称银行提交点全部完成。


提交点首轮银行集成为 29/52，不能作为验收通过：commitBefore/commitAfter 的失败事实 code 是公共量子事务包装消息 Cannot execute quantum transaction，而非底层 SQLException 消息；事务结果仍须独立验证 UNKNOWN，不能靠错误文案推断。其余多数失败来自旧 optional 标量查询将 attemptId 当完整存储身份，复合键后误报不存在。公共查询补齐显式 optional 标量的缺失身份回退：按声明属性筛选，无匹配返回空，唯一匹配返回结果，多匹配明确 REPOSITORY_SCALAR_QUERY_AMBIGUOUS；完整角色/DDL 身份及无返回值 hydration 不回退。银行多事件入口使用集合历史，不隐式取第一行。通用测试覆盖 JDBC/JSON 两个仓储、类型调用和请求封装调用、唯一/空/歧义；继续重新生成验证。


本轮旧测试责任复核（删除门槛，不代表已经完成）：

| 剩余手写测试 | 仍必须提供的源证据 |
|---|---|
| JdbcDepositStoreTest | 不同交易对同一版本的真实竞争、账户写入后/部分批次写入失败、成功及失败审计不可用时主异常保持；提交点四种结果待本轮银行集成通过 |
| JdbcDepositReversalStoreTest | 同/不同冲正身份并发、冲正中版本/原成交变化、稳定请求身份、冲正提交点四种结果、跨进程重放及审计不可用 |
| DepositPostingTest | 原分录独立字段预期及精确小数；旧仓储 fixture 依赖须同时移除 |
| CashDepositReversalTest | 四种实际冲正报告、当前积数保持与真实量子日志，不只内存计划正确 |
| CashQuantumLedgerTest | 外围失败后量子记录/当前值一并撤销、极小精确金额及不同账户身份独立、错误 before 值拒绝并清理作用域 |
| DepositSagaRecoveryTest | 六类显式业务恢复、无局部成交不反交易、后续独立成交保留、恢复拒绝不冒充补偿、稳定恢复身份与完成日志失败后查询 |
| DepositDemoReportTest | 声明式报告实际持久结果及量子记录，不能仅输出入口 PASS 名称 |

现有完整源冲正与存款运行路径不调用这些旧实现，但这不足以删除其未替代责任。后续先用同一通用提交点控制完善冲正，再补资源查询/报告及 Saga 的源语义和生成执行，最终从无手写 Java 的目录 clean verify。


提交点阶段最终证据：修复查询后完整 `mvn -pl :xbod-deposit-demo -am verify` 成功，lang 295、appframe 513、generator 101、剩余旧 demo 45，共 954 项 JUnit 无失败/错误/跳过；52 个 APP 入口全部通过。四个 JDBC 故障入口、原有 48 个入口（含两个新 JVM 的待授权阶段）均实际成功。UNKNOWN 的两种真实数据结果分别被源断言区分，稳定业务身份重试/重放只成交一次；已提交的同次尝试保留两条事件。此次为增量 verify，不宣称 clean 验证。本轮无旧 Java 删除，库存主 14/测试 7，Goal 继续活动。下一阶段先承接冲正的对应提交点与竞争恢复，再补齐审计不可用、量子日志、Saga/报告及剩余源责任。


## 现金冲正提交点与跨 JVM 原成交身份（实施中）

上一阶段为明确进展：954 项 JUnit、52 个 APP 源入口完整 verify 成功，审计复合键查询回归已修复。本阶段没有增加或改写任何 demo Java。99zm 共用真实跨日 fixture（原存入 600、原手续费 2、后续存入 100、当前积数 800）；99zma 保存独立断言，99zmb 六个根场景包括四种 jdbcFault 及冲正记录写入后、关联更新后两种原子 after 故障。提交点锚定 storeCashReversalTrade，原存款/后续存款不会提前消耗该故障。SPP catch 后查询实际账户、原/后续/反向分录、冲正记录、关联和审计；无成交应保留 v2/800、关联未撤销、无反向分录；已成交应 v3/200、积数 800、反向八条借贷各 602、关联 v1。原/后续分录逐槽比对 side/subject/amount；原费用、原成交版本、后续积数均须保持。随后稳定冲正业务 id、新尝试号重试，再次日重放，最终只一次冲正。

99zn 使用 APP restart 先成交冲正，再启动独立 JVM 构造空参与者并只查询，不能重跑第一阶段种入或携带生命周期。确认冲正仍为 v3/200、原/后续分录保留后，新存入 25（v4/225、积数 1000），重放旧冲正必须返回 v3/200 的原成交结果且保持当前 v4/225。改原交易或 overnightMode2 复用已成交身份分别拒绝 DEPOSIT_REQUEST_ID_REUSED，新编号再冲正已撤销原交易拒绝 ORIGINAL_DEPOSIT_ALREADY_REVERSED。实际持久审计必须区分成交、重放与两种拒绝。此阶段正在执行 59 个根入口，尚无成功验收结论；并发冲正、审计不可用、量子日志、Saga 与报告及手写 Java 全删除仍未完成。


冲正提交点阶段最终证据：完整 verify 成功，lang 295、appframe 513、generator 101、剩余旧 demo 45，共 954 项 JUnit 无失败/错误/跳过；59 个 APP 根入口全部通过。六个新增冲正故障入口及两个独立 JVM 冲正阶段实际通过，原有 52 个根入口均无回归。阶段日志 target/spp-examples/restart-4430443081500016374/stage-0.log 和 stage-1.log 分别 PASS；后续存款 v4/225 与积数 1000 未被重放覆盖，两种身份变化与另一编号重复撤销被源拒绝。此次没有改写编译器/框架 Java，也未删除剩余旧实现；业务与验收新增内容只在 SPP/APP，存储保障继续使用原 PHY 声明。此次增量 verify 不宣称 clean。Goal 保持活动，库存主 14/测试 7；继续冲正并发、未成交的部分分录冲突与过期版本、审计不可用、量子日志、Saga/报告及最终删除。


## 同/不同身份的真实现金冲正竞争（实施中）

上一阶段完成 954 项 JUnit 和 59 个源根入口，属于明确进展。本阶段补齐旧 JdbcDepositReversalStoreTest 的两类并发责任：99zo 事实与两路提交场景、99zoa 独立断言、99zob 根入口。APP barrier before markCashReversalCommitting 2 使两路都完成原成交/当前版本/未撤销关联查询和逆向计划，再同时进入共同 quantum 提交；同步点不持有 JDBC 排他锁。源断言必须恰好有一次实际 PERSISTENCE_ALREADY_EXISTS 或 PERSISTENCE_VERSION_CONFLICT，且其事务结果为 ROLLED_BACK。

99b 生命周期新增 submissionFailure 与 competingLink。已存在或版本冲突退出失败事务后，显式按请求 id 重查冲正成交；有成交则核对原笔及模式身份，返回原结果并在独立 quantum 写重放审计。无该成交则重查原交易关联；只有实际已指向另一冲正时，将本次业务标为 Rejected 并报 ORIGINAL_DEPOSIT_ALREADY_REVERSED，否则保持原存储失败。恢复、重放和错误转换不在 Java 锁/重试器中。

同身份案例要求两路都返回原 v3/200、唯一关联、八条借贷各 602、一条成交加一条重放审计；不同身份案例要求一成功一业务拒绝、一份成交和一组八条分录，失败候选不得残留。两者都核对原 600/费用 2 的成交和后续 100 的分录/积数仍保持。当前正生成执行 61 个根入口，没有提前宣称通过，也没有删除仍承担其他责任的旧仓储 Java。


并发第一轮同身份通过、不同身份失败于首路业务拒绝码。只读检查实际生成 ExecuteCashReversalUnchecked.java 确认：catch handler 内 classifyConcurrentCashReversalLink 的业务拒绝按通用规则附加到原存储冲突，主异常保持原冲突。不是忽略事务结果或放宽预期；SPP 修正为 catch 内只重查成交/关联并记录 concurrentReplay，缺事实或查询失败保持原错误，退出 catch 后再进行身份检查、重放及独立审计，或者有据的业务拒绝。身份检查在 catch 外也避免并发身份复用错误被存储冲突遮蔽。断言增加实际失败码便于定位，仍要求 ORIGINAL_DEPOSIT_ALREADY_REVERSED。当前原轮继续完成；修正版待重新生成执行，未宣称 61 个入口通过。


修正轮在解析阶段发现新添的动态诊断不符合 require 第二参数的固定 StringLiteral 契约，银行场景未执行；保留原固定断言标识，去除这项非必要诊断拼接，再验证已修正的 catch 外业务分支。检查 Spp.g4 的 calculationStatement 确认这是 require 消息参数限制，不是普通字符串拼接语义缺失，不能将其记录为通用表达式漏洞，也不能把未运行的修正轮称为通过。主要事务与竞争断言保持原要求。


量子持久性后续核查（尚未实现）：旧 CashQuantumLedger 明确预建 before_value/delta_value/after_value/current_value 为 VARCHAR(4096)，再使用通用 JdbcQuantumJournalStore，因此极小金额 1e-25 的旧测试能通过；新源 PHY 直接建默认 DECIMAL(38,12)，不能据普通金额案例认定同样精确。当前 APP 已有表/主键及按属性的集合查询，原生 reader 支持 snake_case/camelCase 名称对照，理论上可声明技术证据 Role 映射实际 xbod_quantum_journal/xbod_quantum_value；但 appDdlTables 默认未启用，且 reader 对文本数值到 PHY BigDecimal 尚无转换。PHY 初始化早于 APP 目录建表，不能靠后置 APP 建表替代适配器的存储选择。

后续实施要求：通用 jdbcQuantum 提供明确的文本精确数值存储配置，默认兼容原 decimal 模式；已有不兼容表须明确拒绝，不能静默当作精确或自动删表。补通用文本数值读回转换，并以 APP/PHY 声明映射查询实际日志和当前值；SPP 表达极小金额、账户隔离、外围失败无日志/无当前值变化及错误 before 值拒绝/作用域清理的独立预期。业务计算不新增精度/小数位参数，物理表示、容量及存储方式留在 PHY/存储映射。测试数据必须来自源事务和真实仓储，不能把旧 CashQuantumLedger 搬进公共框架。


并发冲正阶段最终证据：修正 catch 外业务判定并恢复 require 固定错误标识后，完整 verify 成功，lang 295、appframe 513、generator 101、剩余旧 demo 45，共 954 项 JUnit 无失败/错误/跳过；61 个 APP 根入口全部通过。两种并发均恰好一次实测存储冲突及确定回滚，查询与业务重放/拒绝按 SPP 执行，账户/关联/分录保持唯一，原及后续成交证据不变；原 59 个入口无回归。此次增量构建，不宣称 clean，也未删除旧 Java。库存主 14/测试 7、Goal 活动。下一阶段已核实旧极小量子金额依赖文本建表，必须改为明确 PHY 配置及源查询/断言，补框架读回数值，再承接余下量子日志、Saga/报告责任并最终删尽手写 Java。


## PHY 精确量子表示与原生日志读取（实施中）

上一阶段为明确进展：954 项 JUnit、61 个源入口完整 verify 全部成功，并发业务拒绝已移到 catch 后。本阶段公共 JdbcQuantumJournalStore 增加 decimalStorage="decimal"（默认兼容）或 "text"（VARCHAR(4096)）；text 明确检查已有日志三列及当前值列的文本类型/容量，遇到不兼容表报 QUANTUM_DECIMAL_STORAGE_MISMATCH，保留旧数据且不自动改表。PHY 配置经语言语义检查、生成目录及公共启动链路传入；其他值明确拒绝。公共 APP 原生 reader 对文本/数值的 BigDecimal、BigInteger 做精确转换，整数分数拒绝而非截断。

四项新公共测试实际通过：极小 1e-25 与两个独立对象的持久读回、外部 JDBC 回滚及错误 before 值拒绝后继续提交、未知存储/既有 decimal 表不冒充 text、声明式原生列到精确数字的读回及分数整数拒绝。已有语言测试扩充接受 text/decimal 与拒绝 float，生成测试确认 decimalStorage 传入目录，针对性 reactor 测试全部成功。未把银行 CashQuantumLedger 实现移入框架。

99zp 新源声明两类技术证据 Role、按对象查询原生量子日志/当前值、显式 quantum 调用和独立极小金额断言。APP 以现有 table/repository 语法映射实际 xbod_quantum_journal/xbod_quantum_value 文本列；PHY cashRecords 开启 appDdlTables、cashLedger 选择 text。业务数字仍 double 的抽象公式，由 PHY BigDecimal 表示，没有在业务计算中增加精度/小数位。当前完整生成运行 62 个根入口；账户隔离、外围回滚、错误 before 值的银行源断言仍需补齐后才删除旧量子测试。不得用四个公共技术测试替代这项源验收，也不宣称已有生产表已自动迁移。


银行首轮新量子入口失败 EXAMPLE_Q_EXACT_VALUES，其他已运行入口仍通过。核查公共启动实现：objectSnapshot 安装 JSON 快照查询，appDdlTables 的原生读取只接入 jdbcObjectRepository，因此需在 PHY 明确选择已有 jdbcObjectRepository；不能假装 objectSnapshot 自动读取技术表。生成目录另显示“snake_case 显式平台列 + camelCase 继承业务字段”重复展开，且表前注解未产生预想的列精度。现按已有 APP primarykey(Role.field) 与 map table { businessField = notnull String(width) physical_column; } 声明精确映射，业务证据保留 double/PHY BigDecimal，物理表名/列名/文本表示只在 APP/PHY。第一轮尚在完成，修正后需重新生成并验证原 61 个入口与量子入口，无手写银行查询器。

上述第一轮最终为原 61 个入口通过、新量子入口失败；958 项 JUnit 全部通过。修正映射的下一轮在语义阶段被原有“列类型须等于业务字段类型”检查拒绝，未执行银行源入口。现补齐通用精确数字文本映射：只有 PHY 内置 BigDecimal/BigInteger 可映射 String 存储列，字段级绑定优先，普通数字和非数字错配仍拒绝；语言及 DDL 生成共享判定。两项新增测试覆盖接受、未绑定拒绝、字段覆盖拒绝、布尔拒绝、真实 VARCHAR 宽度与列别名、业务模型类型不变及无重复列，针对性 reactor 已通过。当前重新进行完整 verify；不提前认定 62 个源入口成功。


精确映射修正轮最终完整 verify 成功：lang 296、appframe 517、generator 102、旧 demo 45，共 960 项 JUnit 无失败/错误/跳过；62 个 APP 根入口全部通过。99zp 从实际文本量子表读回两个精确当前值和两条 COMMITTED 日志，独立核对原值、增量、成交值及守恒；原 61 个入口，包括实际并发及两类跨 JVM 重启，无回归。日志 /tmp/spp-quantum-evidence-exact-mapper-validation.log。此次增量构建，主 14/测试 7 未删除，Goal 继续活动；仍需账户隔离/失败/旧值冲突源验收、Saga/报告及最终删尽 Java 的 clean 验收。


99zpa 继续仅用 SPP/APP 描述三个量子生命周期入口：两个账户分别提交极小金额/25，查询两者真实记录；显式 quantum 内更新后业务拒绝，捕获确定回滚、查询零日志/零当前值，再合法提交；先提交 100→110，再以错误 before=100 请求 120，要求实际旧值冲突及回滚、原两条记录/110不变，随后按 110→115 合法提交并查询四条日志。没有手写 Java、外挂连接或银行专属适配器。当前启动 65 个源入口完整 verify，未预先宣称这些入口通过，旧量子测试仍保留。精确文本映射同时拒绝数组，并对无效 PHY 类型返回诊断而非使 mapper 检查抛异常。


后续 Saga 源迁移核查：SppDomain.validateCompensationDeclarations 当前将补偿目标限定为 local atomic update，并要求目标有 local transaction mode/resource；CompensationTransactionParticipant 用原调用参数调用目标，之后写 COMPENSATION_DONE，失败写 COMPENSATION_FAILED。银行恢复实际是带查询/资格/反向计划/显式 quantum 提交的完整冲正场景，不能压成空壳 atomic update 或复制进公共运行库。因此还需验证并完善完整业务场景的恢复绑定与参数契约、真实本地成交证据、未成交不执行逆向、恢复资格拒绝后保留原成交、稳定冲正身份重试以及成交后审计不可用的查询确认路径。此项登记为后续通用能力实施工作，未认定现有 Saga 生成链路已满足旧六项责任。


生命周期第一轮主动停止于生成阶段（进程已退出 143，未执行 65 个源入口），不是完整通过或运行失败。进一步核查 QuantumConservationParticipant.beforeExecute 确认它从持久层加锁刷新参数；旧 CashQuantumLedger.append 更新后另比对预期 after 值，不一致报 QUANTUM_CASH_BALANCE_MISMATCH。因此源案例不能误称运行链会按参数里的旧值直接拒绝日志。99zpa 改为显式 transaction quantum 内增量更新后调用已有 checkCashSettledQuantumBalance：实际当前 110，加 20 得 130，与旧计划 120 不符，业务校验拒绝并回滚，查询确认仍 110、原两条日志；随后合法加 5 得 115。守恒增量刷新行为不修改，直接 journal 错误 before 拒绝仍由公共测试独立覆盖。修正轮将重新生成执行三个新入口及原 62 个。


修正轮已实际通过 quantumIsolationExampleRun、quantumRollbackExampleRun、quantumStaleValueExampleRun、quantumEvidenceExampleRun：两个对象分开查询，失败无记录后能再提交；过期计划触发 QUANTUM_CASH_BALANCE_MISMATCH/ROLLED_BACK，查询仍为 110/-10 及原两条日志，合法再次提交为 115/-15 和四条日志。当前原 62 个入口继续完整回归，尚未提前认定全部 65 通过；旧量子测试仍保留至该轮完成。没有更改 QuantumConservationParticipant 刷新最新值的行为。


生命周期修正轮最终完整 verify 成功：960 项 JUnit 无失败/错误/跳过，65 个 APP 根入口全通过，两个跨 JVM 场景及实际并发无回归。日志 /tmp/spp-quantum-lifecycle-checked-validation.log。删除 CashQuantumLedgerTest 后库存主14/测试6，累计十五份旧测试已迁移；量子源案例替换三个业务责任，公共测试单独覆盖外部连接和直接日志旧值校验。启动 clean verify 确認重生成和十五份旧测试无残留；预计lang296/appframe517/generator102/旧demo42=957，源65。只是预计数，待实际日志。Goal活动，剩余审计/部分批次/过期候选、Saga/报告、主Java全部删除仍需完成。


量子迁移 clean verify 仍在执行原 65 入口的基线（本轮编译公共模块完成后）。利用独立时间完善下一批通用源码能力，未重新编译影响该进程：APP fault 可指定 times 正次数、可选 after 成功的同步本地原子启用服务，fixture 不消耗未启用故障；必须触发全部次数，旧目录默认一次。可选 String[] suppressedCodes 将直接附加失败码写入源失败事实，主 code 保持。新增语言/公共运行测试及目录断言尚待当前构建结束后执行；不能把当前 clean 结果当作这些新扩展已验证。银行主/失败审计双故障与冲正准备后启用案例待迁移，不用删表或手写银行 JDBC 故障器。


量子生命周期最终 clean verify 成功：lang296、appframe517、generator102、剩余旧demo42，共957项JUnit无失败/错误/跳过；65个APP源入口全通过。十五份已删除测试（包括嵌套类）无残留class。当前主Java14、测试Java6，Goal活动。此构建验证量子迁移基线，不包含编译之后才写入的连续故障/附加失败码新扩展；该扩展正在单独测试。日志 /tmp/spp-quantum-lifecycle-clean-validation.log。


连续故障及附加错误码针对性 reactor 已通过：ExampleDeclarationTest、ScenarioFailureSemanticsTest、ExampleServiceFaultsTest、ScenarioSuppressedFactsTest、ExampleCatalogGenerationTest、GeneratedExampleRunnerTest。保留旧目录默认一次，启用服务失败不启用、重复启用不重置、次数不足使入口失败；附加码数组/List 两种生成形态及旧 minimal facts 兼容均有验证。99zq/99zr 新增四个银行源入口：主存款审计及失败审计连续两次不可用；费率缺失业务拒绝并且审计失败；真实原存款/后续存款准备后才启用冲正双审计失败；原冲正已成交后启用重放/失败审计双失败，查询仍有原成交、余额/关联/分录及六条真实量子日志，随后稳定身份重试只补重放审计。源失败事实显式 opt-in suppressedCodes，独立断言次要故障附加且主码保持。当前69入口完整verify已启动，未先认定通过或删除剩余旧测试。公共模块测试阶段发现并修正源 fixture 使用了不存在的 lifecycle.work，改为实际 lifecycle.execution.status；银行编译尚未开始。


四个审计入口首轮在银行解析阶段终止，未执行69个入口：新 ReversalAuditEvidenceExample 的字段名 quantum 是既有保留字，属于案例错误，不是语法缺口。改为 evidence，未放宽关键字规则。公共模块已验证通过；修正后重新生成及执行银行完整验收，旧测试不删除。


余下冲正候选核查发现明确缺口：93 的 commitCashReversalRecords 在 quantum 内更新冲正成交、账户、分录、关联、量子值及审计，但没有重新读取/对比准备时的原成交证据；99 的 executeCashReversalAttempt 将准备和提交放在同一场景，缺少可复用的只准备/提交准备结果入口。旧 JdbcDepositReversalStore.commit 在同一连接中复核原 transaction/account/version/facts，变化报 ORIGINAL_DEPOSIT_RECEIPT_CHANGED；重放还对已成交冲正所绑定的原凭证做身份核对。后续需将 prepare/submit 拆成源场景，在显式提交边界复核原成交事实，补源凭证变化/账户过期计划拒绝及稳定身份重试。不得用只检查当前账户CAS代替原成交证据。源角色/集合事实深层相等能力若不足，须完善通用逻辑表达式及生成，不复制银行JSON比较进公共库。

批次故障已有 RepositoryWriteSession.persist 对集合/数组按顺序执行 write，无全批次事先排重；当前99zk预置slot1只能证明首行冲突。后续源案例预置中间slot4，核对slot1～3未残留、原冲突记录仍存；显式删除fixture后同身份重试，再验证唯一成交、分录、关联和审计。此项需存款及冲正两条路径独立证明。


审计失败修正轮最终完整verify成功：964项JUnit、69个APP根入口均无失败/错误/跳过，四个新增入口全部通过。存款/冲正的主审计及失败审计连续不可用保持主错误并附加一项次要错误；业务费率拒绝不被审计失败掩盖；已成交冲正重放审计失败保留原成交、余额/分录/关联及六条真实量子日志，后续稳定身份重试不再扣减。日志 /tmp/spp-bank-audit-failure-corrected-validation.log。新增能力和原65入口完整无回归；本轮增量，主14/测试6保持，Goal活动。下一批落实slot4批次中途故障，并补原成交事实复核及准备/提交源分层；Saga/报告继续实施。


99zs/99zt 新增两条纯源批次中途案例：预置slot4/777/DEMO.EXISTING，实际写slot1～3后第4条唯一冲突触发PERSISTENCE_ALREADY_EXISTS/ROLLED_BACK；独立查询要求仅原fixture一条、账户/成交/关联不变、失败审计存在，量子日志存款0条/冲正原4条；显式源quantum删除fixture后同身份再提交，存款8条及2条量子日志，冲正8条及总6条量子日志，原及后续存款保持。复用现有声明式批量delete，无新银行Java或故障器。71入口完整verify执行中，未提前认定通过。

参与者事实比较核查：BusinessCalculationValidator 接受对象相等表达式，但 NumericJavaRenderer.valueEquality 只对字符串/字符/布尔/枚举使用值相等，对Role/Contract的 == 仍生成Java引用比较。因此不能用复制后两个不同实例的 == 复核原成交完整事实；不修改既有 == 语义。后续同事实谓词应显式说明递归属性/有序集合相等、null语义、内置数字数学相等以及已选PHY适配器比较，不以银行JSON字符串或BigDecimal标度作为业务判断。锁定原凭证的APP查询绑定亦须在已有SPP事务中执行，不能在查询适配器中另开隐藏交易。


批次中途冲突最终增量 verify 成功：lang298、appframe522、generator102、旧demo42，共964项JUnit无失败/错误/跳过；71个APP根入口全部通过。99zs/99zt 实际在slot4冲突，确认前面已写分录全部回滚，原fixture保持；删除fixture后同身份提交成功，量子日志没有重复。日志 /tmp/spp-partial-posting-source-validation.log。本轮不是clean，主Java14、测试Java6保持；原成交事实复核、准备/提交分层、Saga和报告仍须迁移，Goal保持活动。


sameFacts及APP repository for update 通用能力针对性测试全部通过，共27项JUnit，日志 /tmp/spp-locked-repository-framework-validation.log。比较元数据来自源声明及PHY数字适配；锁定读取不另开隐藏事务。91归档原存款事实，93在完整quantum提交内锁定读取/复核，99拆分准备及提交场景并保留原组合入口；当前银行生成编译验证中，未认定新源行为通过，主14/测试6保持。详细语义见 participant-facts-and-locked-read.md。

银行首次原证据接入生成在角色身份元数据遍历处持续高CPU，无生成进展；线程诊断定位 OpenApiGenerator.addRoleIdentityMetadataFields 对无角色映射工程仍枚举所有嵌套路径。共享参与者图在新增原成交快照后放大无效递归，属于通用生成性能缺口。已终止该轮自身Maven进程，不能记为生成或银行验收成功。公共生成器在映射元数据目录为空时直接跳过此遍历；新增与银行无关的35层共享模型实际生成测试，核对声明字段保持且不扩展无元数据路径。修正后的针对性测试及银行生成正在执行，日志 /tmp/spp-original-evidence-pruned-generation-validation.log。

共享图测试首轮生成在0.6秒内完成，但测试夹具未声明APP本地部署，故没有InspectRequest而断言错误，银行阶段未开始。补上明确的APP local inspect绑定，使测试实际经过请求身份元数据路径；没有放宽生成或业务语义。修正轮继续验证。

共享图测试最终补齐标准APP验证及两个普通Role参数（context仅允许Contract，单个对象请求允许折叠为原模型），实际生成35层共享引用请求成功，0.676秒，无失败/错误/跳过；InspectRequest仅facts/label，Node35仅first/second。银行阶段已进入模板生成，尚未认定完成。该阶段只跳过整个映射目录为空时的无效遍历，不宣称对存在角色映射的所有图均提供相同复杂度保证。

银行阶段构建证据纠正：针对性 test 生命周期没有重新打包 Maven 编译插件及其依赖，target 插件JAR仍为19:49而最新class为20:40，不能用此轮银行生成证明最新语义接入。已停止该轮自身进程（通用针对性测试已通过），改跑完整reactor verify，使公共模块package后再由银行调用插件，并执行完整JUnit与71源入口。日志 /tmp/spp-original-evidence-source-validation.log；不再将先前两个test构建的银行阶段计为通过。

首次最新插件完整verify在银行Java编译阶段失败：新增 prepareCashReversalAttempt、submitPreparedCashReversal、describeCashReversalPrepared、checkPreparedCashReversal、prepareCashOriginalEvidence、checkCashOriginalEvidence 六个服务没有APP本地部署绑定，对应响应模型未生成。公共lang300/appframe528/generator105共933项JUnit通过，但旧demo测试及71源入口尚未执行，不记为银行成功。补齐APP local声明，两条场景使用idempotency business；未手改生成Java。修正后完整verify日志 /tmp/spp-original-evidence-binding-source-validation.log，执行中；库存主14/测试6，Goal仍活动。


原成交事实复核接入修正轮完整 verify 成功：lang300、appframe528、generator105、旧demo42，共975项JUnit无失败/错误/跳过；71个APP根入口全部通过，含两组跨JVM重启及同/不同身份的真实并发冲正。93的完整SPP quantum内锁定读取原存款并以sameFacts复核，91归档原存款快照，99准备/提交分层已实际生成、编译、运行。APP六项遗漏绑定已补齐，没有手改生成Java。日志 /tmp/spp-original-evidence-binding-source-validation.log。本轮为增量verify，不是clean；主Java14、测试Java6保持。原凭证变化/过期候选/准备结果已成交身份的三组新独立验收，以及Saga和报告仍待实施；原71个通过不代替这些未完成责任，Goal保持活动。

准备结果提交迁移本轮：99b将原请求/准备结果提交收敛为decideCashReversalSubmission源场景，保持已有冲突后查询/业务拒绝/重放及显式Quantum审计；新增prepared入口保留候选，已成交时额外比较归档原存款与候选原事实，差异返回DEPOSIT_REQUEST_ID_REUSED。99zu/99zua/99zub新增三条纯源入口：持久原凭证settled.version变99后拒绝及恢复夹具同身份重试；另行存入5造成过期候选，拒绝后重新准备保留805上的5，最终205；冲正后另行存入25，未来日期准备结果重放保留225当前余额/原200成交，改变候选原凭证拒绝，恢复原候选确认成交。独立查询余额/版本、原及后续交易/分录、审计历史和实际量子日志。APP显式注册所有新增服务，夹具原凭证改变通过源update和声明式persist(update)，没有手写Java。74入口完整verify已启动，日志 /tmp/spp-prepared-reversal-source-validation.log；尚未认定通过或删除旧测试，主14/测试6保持。

准备结果首轮完整verify：975项JUnit通过，APP源入口73通过/1失败。新增原凭证变化及准备结果重放两入口已实际通过，原71入口均通过；过期候选已验证旧提交拒绝、重新准备提交和后续5元成交保持，但在最后合并账户断言处失败。源规则核查60/30/90：第三笔存款与上次积数日同日，normalDays=0、normalIncrement=0，原积数800保持；不是805（805是当前余额）。已修正fixture预期为800，将余额、明细和积数拆为明确错误码，并对第三笔实际成交额外断言零天/零积数增量。未改业务计算、未先认定修正通过，旧Java不删除。

独立Saga缺口实施中：通用语义开始允许本地Scenario恢复目标，它必须在SPP声明或委托给声明了完整本地事务的源场景；场景调用图检测嵌套compensate仍拒绝，参数/重复/自我恢复检查保持。Saga节点也允许委托给有明确源边界的场景，而不是让原子空包装或APP隐藏交易。新增通用ScenarioCompensationSemanticsTest，正在与完整AppSemanticsTest单独验证。该扩展是在前述975项公共模块测试打包之后写入，不能用73入口通过声称它已验证。日志 /tmp/spp-scenario-compensation-semantics-validation.log。

Saga恢复场景语义与调用元数据针对性验证完成：ScenarioCompensationSemanticsTest 3项及完整AppSemanticsTest 245项，共248项无失败/错误/跳过。夹具首轮因APP in/out声明不完整及commit为保留字解析失败，补齐响应header并将服务命名commitWork；未放宽语法。恢复可拥有或委托源中的明确本地事务，无边界/参数不一致/自我/重复/可达嵌套恢复链仍拒绝。Saga节点委托commitWork时生成store事务调用元数据，workflow保留node调用元数据；非Saga场景的既有目录行为保持。通用运行的实际场景恢复与银行六项Saga责任仍待验证。日志 /tmp/spp-scenario-compensation-semantics-validation.log。

准备结果修正轮完整verify已启动，日志 /tmp/spp-prepared-reversal-corrected-source-validation.log，预计978项JUnit及74个APP入口，未提前认定通过。过期候选同日积数预期改800并独立核对第三笔零天/零增量；准备结果重放再增加改变overnightMode2复用成交身份的拒绝，审计独立要求一笔成交、两次重放、两次身份拒绝共五条。旧测试暂不删除，主14/测试6保持，Goal活动。

准备结果修正轮完整 verify 成功：lang303、appframe528、generator105、旧demo42，共978项JUnit无失败/错误/跳过；74个APP根入口全部通过。新增99zu原凭证变化、99zua过期准备结果及同日积数800、99zub已成交准备结果重放与两类身份差异拒绝均实际成功；两组跨JVM重启和真实并发保持。日志 /tmp/spp-prepared-reversal-corrected-source-validation.log。按 reversal-store-retirement.md 的责任表删除 JdbcDepositReversalStoreTest（16方法），当前主Java14、测试Java5；正在clean verify，预期旧JUnit26，但不提前认定干净验收成功或旧class已清除。Saga和报告及全部主Java迁移仍未完成，Goal保持活动。

旧冲正存储测试退休后的clean verify成功：lang303、appframe528、generator105、旧demo26，共962项JUnit无失败/错误/跳过；74个APP根入口全通过。JdbcDepositReversalStoreTest及嵌套class均无残留，累计十六份旧测试退休，当前主14/测试5。日志 /tmp/spp-reversal-store-retirement-clean-validation.log。此干净基线不包括其后才接入的99zv Saga六类和99zw分录规则新源，后者下一轮另行验证；不得据此宣称Saga已通过或整个目标完成。

99zv/99zw首轮接入verify在源解析阶段失败：Scenario中显式transaction组直接接try并非现有语法允许的普通语句形态（事务组须以执行组表达）。将99zv的事务包装为现有serial { transaction quantum/saga { ... } }形式，保持所有边界和模式可见，未修改生成Java、未放宽语法。公共936项JUnit通过，银行新源没有运行，不计为成功；修正轮继续verify。

事务组语法修正后，新源解析及APP语义通过，PHY验证指出三个Saga服务尚未明确分配后端（cashSagaDepositNode、cashSagaLaterNode、cashSagaWorkflow）。已在已有localJdbc cashDatabase后端逐个加入saga绑定，不把模式藏在Java。前两轮936项公共JUnit通过，银行生成运行仍未进行；补齐PHY后的verify继续验证。

PHY绑定补齐轮（-DskipTests）完成生成和3836文件Java编译，但运行注册阶段失败：JDK接口代理不能转换为生成Scenario具体handler类。尚无银行81入口执行证据，不能计为通过。通用修正增加SourceScenarioService基类，可原位装饰事务参与者钩子而保留场景类型；TransactionParticipantProxy对其他服务仍用既有接口代理。两项非银行测试证明具体方法、参与者begin/commit/rollback及多次装饰组合均保持。报告通用导出器的三项测试也通过，合计5项JUnit，日志 /tmp/spp-source-scenario-evidence-framework-validation.log。现接入执行器可选spp.examples.evidenceDirectory导出，并扩展运行器现有六项测试验证普通成功/失败及跨JVM文件。框架修正和银行81入口下一轮完整验证中，主14/测试5保持。

通用场景物理绑定与证据导出集成最终针对性验证：11项JUnit全部通过（2场景参与者、3导出器、6运行器），日志 /tmp/spp-source-scenario-evidence-runner-corrected-validation.log。导出仅通过@JsonProperty读取源事实，数字在JSON/Markdown保持精确；失败事实保留主/附加异常；两个JVM阶段与父restart结果分别保存，修正首轮父失败覆盖setup成功文件的问题。银行POM启用通用证据目录。现重新完整verify，公共新代码和场景基类模板会重新打包，验证预计967项JUnit及81根入口，不提前认定银行Saga及最终纯源目标通过。

场景物理绑定与证据导出完整verify成功：lang303、appframe533、generator105、旧demo26，共967项JUnit无失败/错误/跳过；81个APP根入口全部通过。99zv六类Saga和99zw分录规则均实际成功，原74入口及两组独立JVM重启、真实并发无回归。证据导出实际读取到六类Saga的Done/NotCommitted/Failed/Confirmed状态、3次恢复重试与2次完成记录失败后的确认；七个新增入口的JSON和Markdown均在target/spp-examples/evidence存在且状态PASS。日志 /tmp/spp-source-saga-runtime-evidence-validation.log。按源责任接替删除DepositPostingTest和DepositSagaRecoveryTest（各6方法），累计十八份旧测试退休，当前主14/测试3，预计剩余旧JUnit14。清理后clean verify尚未执行，不提前认定旧class已清除；报告、存款存储的快照复核/不同身份真实竞争和全部主Java迁移继续，Goal保持活动。

删除Saga和分录测试后的clean构建在旧测试编译失败：JdbcDepositStoreTest仍调用已删除DepositPostingTest.rules夹具，不能认定955项/81入口的干净证明已经取得。未补写银行Java夹具，保留临时构建缺口，继续完成旧存款存储剩余责任再删除其依赖测试。源91增加账户锁定查询/同版本完整sameFacts复核，92/93在完整quantum内先保留成交身份，再锁定复核当前账户并提交其他事实，保持同身份碰撞的原语义。CashQuantumMovement源合同移到91并增加current读回事实，95的增量运算保持。99zx两个新入口验证同版本原快照篡改拒绝及重新准备；不同现金身份真实并发在准备完/提交前屏障会合，只有一笔成交/一笔版本冲突，失败身份重新准备后两笔均保持。APP显式绑定所有新服务，没有银行Java。新源尚未验证；旧Java库存主14/测试3，Goal活动。

独立通用恢复目录开始对齐场景边界：根据生成调用元数据及已注册的本地服务判别显式本地事务，区分SPP场景的业务恢复与原子对象快照/适配器量子反向。有边界但恢复目标未注册时保持RECOVERY_OPEN、提示绑定业务恢复，不把它误报为缺少原子更新；无边界不声称闭合。三项新非银行目录测试及完整appframe正在验证，不用先前清理构建的旧JAR证明新诊断通过。日志 /tmp/spp-scenario-recovery-catalog-framework-validation.log。

恢复目录全部appframe536项JUnit通过，日志 /tmp/spp-scenario-recovery-catalog-framework-validation.log。银行账户边界首次源验证在解析99zx失败：夹具字段使用了保留字quantum；改名evidence，未改语法/业务逻辑。使用-Dmaven.test.skip=true仅用于本轮完整源生成/运行，绕过仍引用旧分录夹具的JdbcDepositStoreTest编译；公共新代码已独立验证，旧测试移除后必须再完整clean verify。首轮无银行源执行证据，不计为通过。

账户边界两入口已实际通过：forgedCashSnapshotExampleRun拒绝CASH_ACCOUNT_SNAPSHOT_CHANGED/ROLLED_BACK，失败时账户100且无凭证/关联/分录/量子残留；重新准备后账户700/版本1、量子2条。differentIdentityConcurrentCashExampleRun两准备结果在提交前屏障会合，恰好一笔成交/一笔版本冲突；失败身份重新准备后版本2/余额800、两份八条分录以及量子4条均独立查询通过。对应JSON/Markdown已生成并读回核对。本轮完整83入口尚未终态，不提前删除JdbcDepositStoreTest。核查ExplicitSagaStep除自身外无任何Java引用，六类业务恢复已由99zv替代，已删除该主文件；当前主Java13/测试3，旧class清理仍待下一轮clean。

账户边界修正轮完整源验证成功：mvn -pl :xbod-deposit-demo -am verify -Dmaven.test.skip=true，83个APP根入口全部通过，无FAIL；既有81入口、两组跨JVM重启及真实并发保持。日志 /tmp/spp-cash-account-boundary-corrected-source-validation.log。本轮跳过JUnit和测试编译，不宣称它是全测试回归；新的公共恢复目录已另行完整appframe536项JUnit通过。新91/92/93账户锁定复核和99zx篡改/不同现金身份竞争两项均已实际生成编译运行。按deposit-store-retirement.md责任表删除JdbcDepositStoreTest（10方法），解决它对已退休DepositPostingTest夹具的最后编译依赖；累计十九份旧测试退休，当前主Java13、测试Java2（剩四项报告/现金冲正责任）。现启动完整clean verify，预计948项JUnit和83入口，不提前认定旧class清除或整个目标完成；银行聚合报告及全部剩余主Java仍需继续迁移。


最新干净构建证据（2026-10-08 23:16）：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，日志 `/tmp/spp-account-boundary-retirement-clean-validation.log`。JUnit 948项（lang303、appframe536、generator105、旧demo4）零失败、零跳过；APP83入口零失败，包括实际并发及两个独立JVM重启组。已确认JdbcDepositStoreTest、DepositPostingTest、DepositSagaRecoveryTest、JdbcDepositReversalStoreTest及ExplicitSagaStep的旧class和嵌套class均不存在。此证据对应83入口，随后新增现金报告源码及第84重启入口不包含在该证据内。剩余13份主Java、2份测试Java仍属待迁移违规项，Goal继续活动。


84入口增量验证完成：日志 `/tmp/spp-source-cash-report-corrected-validation.log`，`mvn -pl :xbod-deposit-demo -am verify -Dmaven.test.skip=true` 成功，84源入口全部通过（含新增现金报告两JVM组）。此命令跳过JUnit及测试编译，不能替代此前948项/83入口的clean证据。现金报告增强校验与两个完整报告入口之后接入，当前86源码的package生成正在运行 `/tmp/spp-source-complete-report-generation.log`，未认定86入口已通过。

完整存款报告两JVM及JSON/中文Markdown事实核对通过，DepositDemoReportTest已删除，文件数当前主Java13、测试Java1（CashDepositReversalTest三项）。旧报告测试class尚待新的clean构建清除，不认定已清除。公共批量注册避免逐项全目录刷新已通过537项框架JUnit。实际冲正报告因重复尝试身份的审计歧义失败，已修正源fixture编号，正在再生成验证；详见source-report-migration.md。


2026-10-09最终迁移门槛：默认父执行器现金冲正报告两新JVM组通过，日志 `/tmp/spp-report-default-lifetime-runtime.log`；同生成版本的JSON/Markdown已核对四实际冲正、32反向分录、20量子行和现金1700/版本4/积数2200。最后13主Java和1测试Java已删除，源目录Java当前全部为0。逐案例请求/授权/来源与实际重放返回增强已补SPP，尚需当前clean重新生成验证；`/tmp/spp-source-only-final-clean-validation.log` 正在执行，最终Goal尚未完成。


## 最终状态（2026-10-09）

本次纯源重构已完成：手写Java主0/测试0，旧14主类及21测试族无残留class，干净生成编译及945项公共JUnit、86个APP入口全部通过。五个两JVM组、逐案例输入/授权/来源增强、六成交48分录五候选及四冲正32反向分录20量子行全部核对。完整权威证据见[最终验证](source-only-final-verification.md)，当前状态以该记录为准，前文保留阶段历史及范围限制。
