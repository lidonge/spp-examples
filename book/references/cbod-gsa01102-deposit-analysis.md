# CBOD 一般存入交易：SPP 表达能力分析与核心原型

> © 2026 S++ project contributors. All rights reserved. Archived analysis; current behavior is documented by the migrated demo and current verification records.

分析日期：2026-10-07。源码根目录：`<BANK_COBOL_ROOT>`。

结论：`GSA01102` 的一般存入交易适合作为复杂业务验证。它的校验、偿还分配、余额推导和计息规则可以按参与者建模，并拆为共享的 query/calculate/check/update 服务。已使用现有 SPP 编译器验证其中的偿还分配及余额推导：14 个输入案例通过语义检查、PHY 数字生成和 Java 编译执行。整笔交易尚未迁移，原 COBOL、数据库、授权处理、账务规则与冲正尚未执行等价验证，不能据此宣称已经实现银行交易。

## 选择的交易和实际调用路径

选择 `onbb.cbl/GSA01102.cbl`，文件描述为“一般存入”，共 2325 个物理行；核心调用 `kbcf.cbl/KSADEP0.cbl`，描述为“DEPOSIT FOR ENTERPRISE SA ACCT”，共 4197 行。行数包含注释和历史修改，不作为工作量或复杂度的度量。

源码按 GB18030 解码阅读，没有改动银行源文件。以下引用是文件物理行号，不是 COBOL 第一列的历史序号。头部调用清单和被注释的旧代码不能替代当前执行路径。

| 原实现 | 确认的行为 | SPP 服务与参与者 |
| --- | --- | --- |
| GSA01102:289 (maintainer reference: `<BANK_COBOL_ROOT>/onbb.cbl/GSA01102.cbl:289`) | 初始化 → 输入校验 → 数据校验 → 功能处理 → 账务处理 → 收费 → 输出 | 存入场景及串行执行组；依赖同一请求、账户及业务上下文 |
| GSA01102:448 (maintainer reference: `<BANK_COBOL_ROOT>/onbb.cbl/GSA01102.cbl:448`) | 金额及起息日限制；交易方式、币别、凭证与进账单限制 | request/product/currency/calendar/document 角色上的 check 服务 |
| GSA01102:687 (maintainer reference: `<BANK_COBOL_ROOT>/onbb.cbl/GSA01102.cbl:687`) | 查账户、控制状态和币种金额档；区分现金、转账、托收、交换、批量等分支 | query 获取业务事实；check 判定受理；calculate 形成处理计划 |
| GSA01102:1089 (maintainer reference: `<BANK_COBOL_ROOT>/onbb.cbl/GSA01102.cbl:1089`) | 构造 PKSADEP0 并经 GSYSTRIG 调用 KSADEP0 | 声明共享存款服务，APP 决定本地或远程绑定；报文搬移与调度由 APP/PHY 承接 |
| KSADEP0:549 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:549`) | 临时户期限、销户状态、存入资格、起存和余额上限、授权条件 | account status/product policy/business date/authorization 角色上的 check 服务 |
| KSADEP0:1481 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:1481`) | 根据贷款状态选择两种偿还顺序，并更新额度、积数、交易明细和分户账簿 | calculate 生成分配与变更计划；update 完成业务状态变更及记录 |
| KSADEP0:1797 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:1797`) | 计息积数、回溯起息日调整、协定分档和透支积数 | 共享 calculate 服务；日历规则与计息单位仍是业务契约 |
| GSA01102:1413 (maintainer reference: `<BANK_COBOL_ROOT>/onbb.cbl/GSA01102.cbl:1413`) | 当前收费入口为 CSATXL0；柜员渠道调用 KSAFEE0 | fee policy/channel context 参与者上的共享收费服务 |
| KSADEP0:2642 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:2642`) | 冲正涉及原日志、原偿还分量、积数、交易明细和账簿反向更新 | 独立的 reversal 场景、原交易角色和资格校验；不能等同于异常回滚 |
| KSADEP0:3714 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:3714`) | 金额分类、业务记账条件和 GCCBAAR 账务规则处理 | posting plan 与分类规则属于业务；存储和实际记账执行属于 APP/PHY |

GSA01102 中直接调用 KCMFEE0 的旧段落已被注释，但 KSAFEE0:267 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSAFEE0.cbl:267`) 中仍存在条件性转调 KCMFEE0 的路径。不能把手续费简化为一个自行假设的“金额 × 固定费率”。

## 参与者应保留哪些业务信息

原接口区同时包含业务数据、报文布局、工作区、数据库键和调度信息，需要按含义重建角色，而不是按 COPY 区逐个生成业务类。

| 业务角色 | 业务可见的事实 | 原始来源 |
| --- | --- | --- |
| 存入请求 | 金额、交易方式、币种、现钞/现汇属性、起息日、凭证用途 | CTFTSA0 / PKSADEP0 |
| 存款账户 | 账户资格、状态、产品、计息金额、余额、冻结和授权金额 | SAACNACN / SAACNAMT |
| 透支债务 | 已入账透支本金、透支息、催收透支息、总透支金额、贷款状态 | SAACNAMT / PSACONST |
| 产品与币种政策 | 起存上下限、余额上限、计息方式、计息单位、收费和授权阈值 | CSAINF0、CCMCUR2、收费与参数查询 |
| 营业日与计息期间 | 营业日、起息日、上次积数日期、天数算法、协定生效区间 | SYS 业务日期、CSAPRD2 / CCMDAT1 |
| 授权与受理事实 | 受理渠道、机构关系、已有授权及需要的授权等级 | SYS/BCT、授权规则与参数 |
| 存入合约及处理计划 | 各偿还分量、变化后余额、积数、记账分量、需要执行的业务动作 | 由 calculate 服务推导 |
| 原交易 | 原金额、原偿还分量、日期、明细与账簿记录、是否已冲正 | KBN 等日志及交易档 |

“柜员渠道才执行某项收费”“某种机构关系才允许交易”是业务政策，不能因字段位于 SYS 工作区就删掉。APP 负责获得渠道和授权事实、解码机构信息；SPP 服务根据这些事实作业务判断。指针、COMP-3 编码、DBI 游标、打印报文和网络地址由 APP/PHY 承接。

## 实际验证的复杂计算

SAACNAMT:44 (maintainer reference: `<BANK_COBOL_ROOT>/dbseg.copy/SAACNAMT:44`) 区分已入账透支本金、计息金额、透支息和催收透支息；SAACNAMT:91 (maintainer reference: `<BANK_COBOL_ROOT>/dbseg.copy/SAACNAMT:91`) 另有账户余额；授权金额定义在同文件 161 行。它们不能合并成一个 balance。

原计算的分配起点是：

```text
可用于偿还的起始金额 = 本次存入金额 + 原计息金额 - 冻结金额
```

由 KSADEP0:1482 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:1482`) 和 PSACONST:1500 (maintainer reference: `<BANK_COBOL_ROOT>/apparm.copy/PSACONST:1500`) 可确认：

- 普通路径 4110：先透支息，再催收透支息，再已入账透支本金。
- 贷款状态为呆账、呆账核销的路径 4111：先已入账透支本金，再透支息，再催收透支息。
- 没有可偿还资金时仍增加计息金额，可用余额按下界零计算。
- 更新后的可用余额另扣授权金额。原分配起点没有扣授权金额，原型保留这个区别，不自行“修正”。

对应的 SPP 原型见 deposit.spp (maintainer reference: `examples/cbod-deposit/deposit.spp`)。业务层使用同一数学语法，PHY 在 deposit.phy (maintainer reference: `examples/cbod-deposit/deposit.phy`) 中选择 BigDecimal；呆账/核销状态到偿还顺序的判断直接写在业务服务体中，APP只需传入贷款业务状态。原型计算一个新计划，没有修改账户输入快照，也没有进行账务更新。

余额关系来自 KSADEP0:1942 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/KSADEP0.cbl:1942`)：

```text
新计息金额 = 原计息金额 + 存入金额 - 三项偿还分量合计
新账户余额 = 新计息金额 - 剩余透支本金 - 剩余透支息 - 剩余催收透支息
新可用余额 = max(0, 新计息金额 - 冻结金额 - 授权金额)
```

原型还检查一个由这些公式推导的数学恒等式：在没有遗留隐式截断的测试输入域中，新净余额等于原计息金额减三类债务后再加本次存入金额。该恒等式是验证用的派生关系，不声称原系统已有同名 check 服务。

同一输入：原计息金额为 0，存入 50，透支息 30，催收透支息 40，透支本金 100，总透支金额 120，无冻结和授权金额。

| 规则 | 还透支息 | 还催收息 | 还本金 | 新账户余额 | 新总透支金额 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 普通路径 | 30 | 20 | 0 | -120 | 120 |
| 呆账类路径 | 0 | 0 | 50 | -120 | 70 |

另一个不能忽略的源码边界：如果总透支金额是 120、已入账本金是 100，只存入 100 且没有其他资金/债务，源码 `<=` 分支保留 20 的总透支金额；存入 100.01 则进入另一分支，将其置零。原型分别验证这两个结果。它们来自原公式，不代表对业务合理性的独立确认。

## 验证方式与限制

在当前仓库编译产物存在时运行：

```bash
python3 docs/examples/cbod-deposit/verify.py --output-dir /tmp/spp-cbod-deposit-verified
```

如果缺少依赖或当前编译产物，先执行 `mvn -pl generator -am test`。验证使用 JDK 17、Python 3 和现有 Maven 本地依赖。

VerifyDeposit.java (maintainer reference: `examples/cbod-deposit/VerifyDeposit.java`) 实际调用 SppCompiler、AppCompiler、业务语义检查与 PHY 运算生成，使用测试模型编译生成的 Java 语句，再执行 14 个案例。检查普通/呆账两种顺序、全部/部分偿还、冻结与授权、本金相等和相差一分钱、核心零金额、负金额错误 E1095，并检查九个计划输出。

本次运行全部通过，日志 `/tmp/spp-cbod-deposit-verification.log`；指定目录保留 Fixture.java、class 和 verification.txt。验证的边界如下：

- 预期值由读到的源公式和分支人工推导，没有运行原 COBOL，没有做双运行时差分。
- 验证用的账户模型由测试代码构建，没有执行完整 OpenAPI 服务生成或场景执行器；场景声明通过 SPP 编译，执行验证逐个运行原子服务的生成语句。
- 非负债务输入和以分为单位的金额覆盖本次计算域，不证明任意三位小数利息或所有异常状态等价。
- 核心 KSADEP0 接受零金额并可能自动还债；GSA01102 输入检查对一般金额要求更严格，只有特定路径例外。核心零金额案例不是“普通柜员零金额存款也允许”的证明。
- 账户资格、产品上限、币种粒度、日期积数、收费、授权、交易日志、账务落地和冲正没有加入本次可执行原型。

## 已发现的迁移边界

1. **校验结果不能只有异常。** GSYSEHRT:26 (maintainer reference: `<BANK_COBOL_ROOT>/ccbmain.copy/GSYSEHRT:26`) 调用 GCCBAMH 后，根据错误前缀和批量标志决定退出。KSADEP0 的授权段有 F 类提示和参数决定的 A/B 授权。需要业务结果表达拒绝、警示、待授权以及授权后的继续执行。当前 require 只抛 IllegalStateException；不能把所有消息都翻译成 require 失败。授权获取可以在 APP 实现，但“何时、需要哪级授权”的判断属于业务服务。
2. **计息单位是业务规则，不是机器精度。** CSAPRD2:363 (maintainer reference: `<BANK_COBOL_ROOT>/kbcf.cbl/CSAPRD2.cbl:363`) 先以币种计息单位除计息金额，结果存到整数 PIC 的 WK-INTC-AMT-A，再乘回单位和天数。不能约掉这次除乘，直接改成余额乘天数。按确认后的业务含义，应显式表达计息单位取整，例如对非负金额使用 `roundDown(amount / unit, 0) * unit * days`；这不是为了恢复机器溢出，而是表达“计息单位”的业务政策。日期算法区分 ACT 和存款天数，当前 SPP 没有完整银行日历库；仍可声明共享 calculate 服务，由 APP 绑定合适实现。
3. **遗留截断必须识别。** SA-OD-INT / SA-OVDLN-OD-INT 是三位小数，而偿还工作变量多数是两位小数。分配、转存和余额重算可能包含隐式截断。逐位兼容必须明确迁移目标和原运行时行为；若确认它是业务取舍，需显式舍入/截断；若只是存储限制，由 PHY 承接或改用足够表示能力，不能默默塞回业务数字类型。日元“无角分”的源码检查也需要结合实际编译器和金额单位验证，不能只凭注释认定它已经正确实现。
4. **冲正是业务交易。** 它查原交易、检查可冲正条件、恢复原偿还分量并更新积数与明细。框架异常回滚和负向 delta 可承接技术恢复，但不等于业务冲正。只有“余额减原金额”不足以复现 KBN 相关逻辑。
5. **不能把业务账务交给技术黑箱。** GCCBAAMT/GCCBACND/GCCBAAR 既有布局/调度，也承接业务金额分类和核算规则。完整迁移需追到规则与配置，明确资金来源方、存款债务、透支本金和利息收入的对应分录及守恒关系，不能仅以更新存款余额宣称账务完成。现有 quantum 能提供守恒边界和物理接入，但本原型没有验证这笔交易的完整账务关系。
6. **复杂业务库仍需补齐。** SPP 已能表达当前算术、分支与集合循环，但银行日历、授权、费用、分档计息和账簿规则不是语言关键字自动带来的能力。它们适合成为基于角色的共享服务库；部署方式在 APP 选择，PHY 承接编解码、存储及具体资源。集合分档可用增强 for 表达；动态生成多笔明细的契约和执行、场景校验作用域、授权后续接仍需单独验证当前实现。

## 完整交易建议的服务划分与验证顺序

业务过程仍然可以规约为查询、计算、校验和更新。源码中的分支多数是在选择政策、形成计算计划或决定某项更新是否适用，没有发现需要增加第五类原子服务的证据。

完整场景可围绕以下契约组织：查询账户/产品/币种/授权及原交易事实 → 校验受理和资格 → 计算偿还/积数/费用/记账计划 → 校验计划与守恒 → 更新账户、明细与账簿 → 形成业务结果。现金、转账、托收和冲正是不同业务路径，应明确各路径的参与者和适用条件；条件由业务服务算出，APP 不重新决定业务政策。

第一阶段扩大当前核心原型：补三位小数及币种单位边界，与原运行时或银行确认的黄金结果对照。第二阶段加入产品上限、账户状态、授权与日历/计息共享服务。第三阶段加入真实生成的服务和场景、资金来源、分录、日志、幂等和并发冲突验证，证明同一交易全部提交或全部恢复。第四阶段实现基于原交易事实的业务冲正，覆盖重复冲正、跨日及状态变更。每阶段保留来源映射和明确未覆盖路径，不将 APP 的占位服务当作已完成业务能力。

SPP 相比直接 COBOL 迁移的价值在于角色、合约和服务职责可以独立阅读，数字与部署差异可放到 PHY/APP，偿还算法可以用统一数学表达式复用。代价是必须重建隐藏在 COPY 区、存储类型、消息和记账配置中的业务契约，并维护生成、物理适配和新旧等价的多层验证。14 个核心案例是表达能力证据，不是性能、开发成本或全银行业务可表达性的证明。
