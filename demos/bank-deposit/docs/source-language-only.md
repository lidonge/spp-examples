> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 纯源语言实现约束与缺口核查

2026-10-08 用户明确：demo 只允许 SPP、APP、PHY，所有 Java 必须由生成链路产生，不得手写任何 Java。业务必须在 SPP 明确知道事务的边界和模式。此要求取代早期文档中允许 Java 演示入口、手工查询实现或数据库提交包装的选择。

## 当前验收结论

最终纯源验收已通过：主/测试手写Java为0，945项公共JUnit和86源入口全部通过，旧14主类/21测试族及嵌套class和JAR残留检查通过。详见[最终验证](source-only-final-verification.md)。

首次核查时 SPP 只为金额守恒更新声明 transaction。当前源路径已由 92/93 声明存入与现金冲正的完整 quantum 边界，覆盖账户、成交、分录、关联和审计；98/99b 的身份登记、重放和失败审计也在 SPP 显式声明独立边界，已从清空的 target 生成并执行。旧 JdbcDepositStore/JdbcDepositReversalStore 及测试均已删除；新路径的业务边界由SPP决定。整体合格仍须当前clean生成和全入口验收证明。

## 手写实现责任清单

| 已删除的原文件 | 原职责 | 源语言迁移要求/核对项 |
|---|---|---|
| NormalCashDeposit | 查询、四种业务场景选择、待授权结果、重放、计划装配和提交调用 | 查询与业务选择由声明驱动，SPP 表达校验作用域与业务结果；APP/PHY 绑定执行能力 |
| CashDepositReversal | 原记录查询、冲正调用顺序、事实校验、结果装配和提交 | 完整现金冲正场景及事务边界进入 SPP |
| DepositReversalPreparation | 原成交与当前账户读取、资格和冲正计算编排 | 服务查询绑定与可生成的场景编排 |
| JdbcDepositStore / JdbcDepositReversalStore | 表创建、请求唯一性、版本更新、成交/分录/审计共同提交 | APP/PHY 的持久化与资源声明驱动生成；完整边界及模式来自 SPP |
| CashQuantumLedger | 账户身份绑定、共享连接、量子场景调用及事务管理器切换 | 量子对象身份与共同资源声明、通用运行支持 |
| ExplicitSagaStep | Saga 节点执行、提交证据和业务恢复绑定 | 显式源语言模式及恢复服务绑定，不能由 Java 定义业务恢复策略 |
| BankDateDecoder | 日期表示解码、有效性检查及序号计算 | 通用日期能力及错误结果绑定；业务日数规则保留在 SPP |
| DepositFeeRateQuery | 费率配置查询及不适用/未找到处理 | 查询绑定，业务分支与结果必须可在声明中追溯 |
| DepositAccrualModels / DepositBankModels | 参与者复制、初始化和模型装配 | 通用参与者构造与复制能力，不能手写模型包装 |
| DepositDemoServices | 服务注册及替换部分生成服务 | 从 APP/PHY 和生成目录自动启动，不使用 demo Java 注册器 |
| DepositDemoMain / CashReversalDemo | 案例数据、调用、独立预期和报告 | 声明式案例、通用执行入口与报告支持，不手写银行演示入口 |
| 首次 src/test/java 的 21 个文件（现剩 0 个） | 断言、fixture、故障与并发执行 | 明确声明式验收能力或复用通用执行器，不增加 demo Java 测试 |

## 当前源能力与验收位置

| 能力 | 源实现与验证位置 | 真实边界 |
|---|---|---|
| 角色、合约、数学和逻辑规则 | Role/Contract、atomic check/calculate、统一表达式及Java式分支/循环；99p/99t/99x/99y等 | 不用银行Java重写公式；生产参数和COBOL逐位黄金输出未取得 |
| 串并行、异常与结果编排 | Scenario serial/parallel、if/else、try/catch、查询返回绑定；99zi/99zo/99zx实际竞争 | 并发测试由APP屏障证明到达，银行判断在SPP；未覆盖任意生产调度拓扑 |
| 完整事务边界和模式 | 92/93整笔quantum；98/99b身份/审计独立quantum；99zv显式saga与业务恢复 | 量子技术回滚与Saga业务恢复不同；本demoPHY使用本地JDBC共同资源 |
| 查询及更新 | APP repository optional/for update、persist/compareVersion、PHY仓储；91/92/93/99ca | 账户和原凭证在提交边界锁定复核；银行原数据库接口和ART配置非本次范围 |
| 故障、审计、幂等、重试 | 99zl/99zm真实JDBC四提交点；99zq审计失败；99zr/99zs分录中途失败；99zu准备/重放 | 不凭异常推断已回滚，未知结果由源查询确认；并非灾难恢复验证 |
| 冲正与Saga | 99b完整现金冲正；99zv六类业务恢复及失败重试；99zy实际四冲正报告 | 不实现通用开户生命周期反交易或自动推导业务补偿 |
| 数字、日期和复制 | PHY double as BigDecimal；20/30日历；new/copy/固定槽数组及业务舍入 | 日元/PIC遗留差异记录保留；跨文件字段/辅助场景仍需依赖顺序 |
| 声明式验收及报告 | APP examples86入口；SPP独立预期；通用JSON/Markdown和两独立JVM阶段 | 逐案例输入/来源增强须本轮clean重新生成；代码存在、编译通过与业务通过分别证明 |

语法能解析、生成代码能编译、按声明执行正确且失败可恢复，是不同验收步骤。公共运行库只实现日期、数字适配、仓储、事务、调度和证据导出等通用能力；银行规则及报告内容保留在SPP，禁止移入公共库或模板。

## 实施顺序与完成条件

1. 明确 SPP 的完整存款和冲正执行场景、事务模式，以及待授权/拒绝的执行范围；补齐缺失语法与语义检查。
2. 使用或完善 APP/PHY 的查询、更新、对象身份、幂等和共同资源绑定，生成持久化与启动代码；模式或资源不匹配应在生成阶段明确报错。
3. 将手写 Java 中的业务判断和编排迁回 SPP；通用日期、参与者初始化及运行能力由声明绑定，不另写 demo 实现。
4. 提供声明式案例执行和独立预期验证，覆盖原第一批三类存入与对应冲正、授权、重试、后续变动、跨日、版本冲突及事务故障。
5. 删除全部 demo 手写 Java，干净目录从 SPP/APP/PHY 生成、编译并执行，确认完整事务边界和模式能直接从业务源读出。

迁移完成前，旧命令与测试结果仅说明旧实现的行为，不能作为新约束下的验收通过。更新后的验收必须检查源语言到生成产物的追溯关系，并禁止手写或修改生成 Java。

重构进度与回归证据见 [纯源语言重构实施记录](source-only-refactoring.md)，通用仓储写入规则见 [APP 仓储写入](../../../book/references/app-persistence.md)。


最新干净构建证据（2026-10-08 23:16）：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，日志 `/tmp/spp-account-boundary-retirement-clean-validation.log`。JUnit 948项（lang303、appframe536、generator105、旧demo4）零失败、零跳过；APP83入口零失败，包括实际并发及两个独立JVM重启组。已确认JdbcDepositStoreTest、DepositPostingTest、DepositSagaRecoveryTest、JdbcDepositReversalStoreTest及ExplicitSagaStep的旧class和嵌套class均不存在。此证据对应83入口，随后新增现金报告源码及第84重启入口不包含在该证据内。剩余13份主Java、2份测试Java仍属待迁移违规项，Goal继续活动。

完整存款报告两JVM及JSON/中文Markdown事实核对通过，DepositDemoReportTest已删除，文件数当前主Java13、测试Java1（CashDepositReversalTest三项）。旧报告测试class尚待新的clean构建清除，不认定已清除。公共批量注册避免逐项全目录刷新已通过537项框架JUnit。实际冲正报告因重复尝试身份的审计歧义失败，已修正源fixture编号，正在再生成验证；详见source-report-migration.md。


## 最终状态（2026-10-09）

本次纯源重构已完成：手写Java主0/测试0，旧14主类及21测试族无残留class，干净生成编译及945项公共JUnit、86个APP入口全部通过。五个两JVM组、逐案例输入/授权/来源增强、六成交48分录五候选及四冲正32反向分录20量子行全部核对。完整权威证据见[最终验证](source-only-final-verification.md)，当前状态以该记录为准，前文保留阶段历史及范围限制。
