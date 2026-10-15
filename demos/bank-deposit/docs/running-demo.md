> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 运行源语言交易验收

在仓库根目录执行，脚本构建模块并调用公共 GeneratedExampleRunner：

```bash
./demos/bank-deposit/run-demo.sh
./demos/bank-deposit/run-demo.sh ordinaryCashExample
./demos/bank-deposit/run-demo.sh pendingRestartSetupExampleRun
```

参数只能是 APP examples 声明的入口名。源业务事实、完整事务、查询、恢复及断言来自 SPP/APP/PHY。普通入口直接按 PHY 数据源配置执行；重启入口由 APP 声明两阶段，运行器依次启动两个独立 JVM，第二阶段重新创建空参与者并查询持久事实。默认专用 H2 文件库和两份阶段日志存于 `target/spp-examples/restart-*`；这属于真实进程重启验收，尚不等于崩溃或灾难恢复验收。

通过 `spp.examples.output` 可调整阶段输出目录；APP using 的数据源配置属性支持点分名称或带连字符的引号名称。银行声明为 `"spp.xbod.datasource-url"`，与既有 PHY 三处共享资源配置一致，未提供时运行器选择专用文件数据库。运行器转发应用系统配置和环境，默认 JVM 核心属性由子 JVM 自行确定。

`mvn -pl :xbod-deposit-demo -am verify` 自动执行全部 APP 源入口。成功输出 PASS，失败或阶段超时输出 FAIL 并以非成功结束；只打印阶段完成日志不能代替检查进程退出结果。旧银行Java入口和测试已全部删除，脚本不调用DepositDemoMain，也不把参数当作报告目录。最终clean验收正在执行，完整状态见 [纯源核查](source-language-only.md) 和 [覆盖责任](source-example-coverage.md)。

## 声明式聚合报告

`depositCashReportSetupExampleRun` 的现金报告两JVM验证已通过，包含三笔成交24条分录、授权等待与重放、当前2300/版本3/积数2200，以及两个未执行反向候选。新增 `depositCompleteReportSetupExampleRun` 与 `depositActualReversalReportSetupExampleRun` 分别汇总十案例/六成交/五候选和四实际冲正/20量子记录，两组已在逐案例来源增强前的生成版本通过；最新源码须以最终clean结果为准。

Maven verify和启动脚本默认在 `target/spp-examples/evidence` 导出JSON及Markdown。文件以实际阶段服务名命名，重启组父结果另用 `__restart` 后缀，避免覆盖阶段证据。直接调用公共Java执行器时可通过系统属性 `spp.examples.evidenceDirectory` 配置同一目录；这只是通用技术配置，银行标题、数值、执行标志及校验全部来自SPP。

## 历史 Java 实现与报告证据

以下保留旧实现的配置、输出格式及迁移责任；其中旧启动方式和路径参数已不适用于当前脚本。它们不代表当前纯源验收已实现全部报告功能。

# 旧运行交易演示与阅读报告

## 命令

在仓库根目录执行：

```bash
./demos/bank-deposit/run-demo.sh
```

脚本构建所需模块并运行测试，再启动 DepositDemoMain。Maven package 阶段生成运行时 classpath，Java 主程序使用本次构建的类及依赖，不需要将模块安装到本地 Maven 仓库。可选参数是报告根目录：

```bash
./demos/bank-deposit/run-demo.sh /tmp/xbod-deposit-report
```

每次运行创建新的 `run-<UUID>` 子目录，包含 report.json、report.md 及 deposit.mv.db。没有重用已有业务数据库，也不修改 XBOD 源目录。主程序完成时正常关闭 H2；这不是崩溃或灾难恢复测试。

## 展示配置

全部账户和参数是虚构的 demo fixture，不含真实客户数据。默认币种 CNY、营业日 20261007，换日案例使用 20261008。账户明细计数初始 10，每笔显式配置增加 1。

| 配置 | 值 |
| --- | --- |
| 现金日累计警示 | 500 |
| 柜员授权限额、A 级倍数 | 1000、2 |
| 客户同地区跨机构 SAC00001 费率、折扣、固定费 | .001、1、1 |
| 最低费、最高费 | 2、50 |
| 产品余额上限 | 10000 |
| 普通/透支积数量化单位及普通日历 | 1、.01、ACT；默认无协定 |
| 科目 | DEMO.CASH、DEMO.DEPOSIT_LIABILITY、DEMO.OVERDRAFT_PRINCIPAL、DEMO.OVERDRAFT_INTEREST、DEMO.COLLECTION_INTEREST、DEMO.FEE_INCOME |

这些机构/地区事实同时用于收费分类和已迁入的所选通存资格；City 范围允许本演示的同地区跨机构存入。这是明确的 demo 配置，不代表银行批准，规则来源与边界见 [银行资格服务](bank-qualification.md)。

## 案例与预期值

| 案例 | 已知预期 |
| --- | --- |
| 普通现金存入 600，原余额 100 | 净余额 700，F0554 警示继续，费用 2 |
| 普通债务账户存入 50，息 30/40、本金 100 | 偿还息 30/20、本金 0，净余额 -120 |
| 呆账账户相同输入 | 偿还本金 50、两类息 0，净余额 -120 |
| 存入 .01，息 .005/.004、本金 .01 | 保留三位偿还，偿还本金 .001，净余额 -.009 |
| 已存入 600 的账户再存入 1500 | None 凭据停在待授权；B 凭据续接成交，净余额 2200 |
| 重放原 600 请求，格式改为 600.00 | 返回原成交；当前净余额仍是后续交易后的 2200，版本不增加 |
| 下一营业日存入 100 | 日累计重置为 100，净余额 2300 |
| 锁定账户、旧起息日 | 分别 EN432、E1043；不留下分录或成交，只保留身份和当次审计 |

前三项金额预期从已迁入的源公式推导；三位小数项按用户确认的精确业务语义，不能当成遗留 PIC 工作区逐位等价结果。授权及收费使用上述明确配置。主程序将预期状态、错误、净余额及账户版本与实际读回结果比较，任何不一致会使进程失败；JUnit 另验证偿还分配、导出字段及文件数据库关闭重开。

## 机器报告字段与证据限制

cases 包含每一步实际请求、营业日、授权等级、执行前版本、执行后查询快照、业务结果或错误、独立预期、来源标识及该步骤已出现的审计。trades 包含六笔实际成交的原计划与前后事实、从数据库读回的分录和完整审计历史；待授权和重复请求不会多出成交。

程序逐条核对持久化分录与计划，并检验借贷及净余额关系。旧请求重放的 Receipt 指向原成交；其计划不是后续交易后的当前账户快照，报告分别保存两者。

remaining 列出尚未完成的实施工作，limitations 记录当前不可获取的银行配置和原系统运行证据。cobolExecuted、bankConfigurationObtained 和 goalComplete 均为 false。文档及报告不把测试通过升级为原 COBOL 全流程等价，也不把缺少生产配置自动扩展成必须部署生产系统的要求。

命令行账户现均包含积数事实，下一营业日使用旧余额 2200 和一个实际日计算积数 2200，并与账务共同保存；JSON 包含原期间和分量。本轮展示覆盖存入、授权、收费、记账、日累计及所选积数模型；完整资格、剩余协议/积数边界、业务冲正、重复冲正及跨日冲正仍须接入，才能满足完整 Goal。

银行范围及操作事实现已进入所有 CLI 账户及原成交记录；该运行默认不挂失。WN200/WN201 与 F0554 同时保留并可成交的案例由 DepositBankQualificationTest 验证。

报告增加 reversalCandidates：现金不退费/退原费两个不同演示输入，以及普通/呆账和三位偿还的候选，共五项。每项 executed=false，列出实际原账簿、当前版本、核心反向金额、显式退费输入及反向分录汇总；Markdown 有“金融与分录反向候选（未执行）”表。候选不改变六笔原成交或 48 条实际分录，不作为重复/跨日完整冲正已实现的证据。

## 当前命令行现金冲正及量子输出

命令行在上述存入报告后执行四笔现金冲正：一般现金、普通/呆账透支偿还、三位金额；每笔再次执行同身份请求验证重放。新增 cash-reversal-report.json / .md 保存新成交、当前账户及实际反向分录，quantum-report.json 保存十笔成功业务产生的 20 条量子记录及按账户区分的当前值。原 report.json 是存入阶段快照及较早只读候选，不随之后冲正改写；检查最终状态应使用现金冲正报告及数据库。

跨日规则按用户决定沿用 XBOD，资格、日期、日累计、普通积数与原实际费用的依据见 cash-reversal-source.md；事务链路见 quantum-and-transactions.md。源码推导及 demo 配置仍不等于运行过原 COBOL。


## 最终状态（2026-10-09）

本次纯源重构已完成：手写Java主0/测试0，旧14主类及21测试族无残留class，干净生成编译及945项公共JUnit、86个APP入口全部通过。五个两JVM组、逐案例输入/授权/来源增强、六成交48分录五候选及四冲正32反向分录20量子行全部核对。完整权威证据见[最终验证](source-only-final-verification.md)，当前状态以该记录为准，前文保留阶段历史及范围限制。
