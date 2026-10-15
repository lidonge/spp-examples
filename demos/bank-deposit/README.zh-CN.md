# XBOD 存款业务演示

本轮对照最新版 Petstore 重构。业务实现仅在 SPP／APP／PHY，Java 测试只准备输入、调用生成服务、断言和注入技术故障。

**本轮对齐重构及回归已完成，以下已知限制保留。** 当前业务包括现金存入、正常/不良/核销欠款偿还、现金冲正及只读试算、手续费、资格/授权评估、日历、协议分档及积数计算。偿还资金进入真实银行内部户；开户仅建立零余额，资金增量和欠款量子状态分别核对。

86 个历史入口已逐项记录对应证据、行为差异及未迁移部分。历史恢复流程、待授权续办和普通 Saga 业务补偿未全部实现，不能仅以测试数量声明等价。最新执行结果见[验证记录](docs/latest-refactoring-verification.md)，当前限制见[已知问题](docs/known-issues-latest.md)。

- [需求、实施路径与传统方案对比](docs/latest-petstore-refactoring.md)
- [最新源文件导航](docs/source-map.md)
- [最新验证记录](docs/latest-refactoring-verification.md)
- [目标完整性审计](docs/completion-audit.md)
- [已知问题与待决策](docs/known-issues-latest.md)
- [旧源及历史验收对照](docs/legacy-source/README.md)
- [86 个历史入口迁移台账](docs/legacy-entry-migration.md)

## 源码结构

```
src/main/spp/cboddeposit/
  account/       账户及零资金开户
  admission/     资格、柜员、地域及授权
  calculation/   偿还分配与计算预览
  fee/           个性化费率、业务舍入与上下限
  accrual/       日历、协议分档、计息积数
  posting/       平衡分录
  deposit/       现金存入合约与独立场景
  reversal/      现金冲正合约与 XBOD 跨日规则
  cboddeposit.app / .phy / .enum
  technical-services.app / .phy
src/test/        验收输入、期望及调用编排
```

查询原地补全参与者，CRUD 按类型名默认生成。合约记录原成交分量，冲正使用当前账户事实，保留后续交易。累计与积数是统计事实，不参与现金守恒求和。事务边界只包含需要共同提交的更新；事前查询和计算在边界外，普通读改写采用默认乐观保障。`fail` 的技术原因通过合约内置 `resultInfo` 返回；业务处置显式另开事务。

APP 的 develop 在同一 JVM／数据库资源下采用 LOCAL；testing 将普通记录和量子库分开，使用统一量子库与 Saga 协调。PHY 提供真实数值默认和数据源；不在 SPP 暴露主键版本、幂等实现或数据库锁。

## 生成与验证

在仓库根目录：

```bash
mvn -pl :xbod-deposit-demo -am package -Dspp.environment=develop
mvn -pl :xbod-deposit-demo -am test -Dspp.environment=testing
```

干净工作区首次构建宜使用 package，以生成 Maven 插件描述。运行产物只能在 target，不修改生成 Java。历史的 86 个 APP examples 已退出生产编译，旧报告只作为历史证据。当前回归结果须以最新 surefire 报告为准。

`./demos/bank-deposit/run-demo.sh examples` 运行新版 demo 验收；`SPP_ENVIRONMENT=testing` 选择分库存储。`run-demo.sh web` 启动框架生成服务的 HTTP 入口（默认仅本机 8089），通过 POST `/api/cboddeposit.openBankRepaymentAccounts`（银行内部户零资金开户）、`/api/cboddeposit.openDepositAccount`、`/api/cboddeposit.depositCash`、`/api/cboddeposit.reverseCash` 调用；根路径 `/` 提供中文存款工作台，可直接完成开户、存入、冲正试算、正式冲正及账务查询。输入结构可对照生成 OpenAPI 和测试资源。

文件库启动默认使用 `WRITE_DELAY=0`，以支持成交确认后进程突然退出的持久化验收；自定义 H2 文件库 URL 也应保留此参数。该验收不覆盖操作系统断电或事务提交结果未知。

HTTP 请求必须提供场景声明的参与者对象；属性可由原子服务补全，空对象写 `{}`。例如零余额开户：

```json
{"BankAccount":{"accountNumber":"ACCOUNT-001"},"DepositAccount":{},"AccountEligibility":{"openedOn":20261013},"CashSettlementAccount":{"accountNumber":"CASH-001"},"DepositAccrualState":{},"AccountOpeningAgreement":{}}
```

当前验证：clean develop 联合回归 1,226 项通过；testing XBOD 86 项零失败、2 项 LOCAL 专属测试跳过；随后新增只读试算在两环境各 2 项通过。打包及脚本 HTTP 开户已验证。具体批次与范围见验证记录，以上数字不是原 COBOL 的运行等价证明。

网页操作、OpenAPI 请求模板的生成方式及浏览器验收见 [中文存款工作台](docs/web-workbench.md)。
