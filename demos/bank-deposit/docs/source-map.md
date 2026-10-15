# 最新源导航

本轮生产源目录是 `src/main/spp/cboddeposit/`。每个独立业务场景单独保存；旧版下面列出的文件名只能在 `docs/legacy-source/` 查找。

| 能力 | 最新位置 |
| --- | --- |
| 账户模型和开户 | account/ |
| 偿还分配 | calculation/cboddeposit-00-deposit-kernel.spp |
| 资格与授权 | admission/ |
| 手续费及个性化费率 | fee/ |
| 日历、协议积数 | accrual/ |
| 借贷平衡分录 | posting/ |
| 现金存入 | deposit/cboddeposit-scene-depositCash.spp |
| 现金冲正 | reversal/cboddeposit-scene-reverseCash.spp |
| 只读现金冲正试算 | reversal/cboddeposit-scene-previewCashReversal.spp |
| 银行还本还息内部户 | account/cboddeposit-20-internal-accounts.spp、account/cboddeposit-scene-openBankRepaymentAccounts.spp |
| 环境与存储 | cboddeposit.app、cboddeposit.phy |
| 所有服务技术拦截 | technical-services.app、technical-services.phy |
| 中文 Web 工作台 | src/main/resources/web/；docs/web-workbench.md |
| 新版自动验收 | src/test/java、src/test/resources |

当前范围、未决问题与验证限制见 [重构设计](latest-petstore-refactoring.md) 和 [已知问题](known-issues-latest.md)。

---

以下为重构前导航，保留作 COBOL 来源与历史规则核对，不代表现行实现：

# 源码与迁移证据

源目录 `<BANK_COBOL_ROOT>`，按 GB18030 解码阅读。以下为物理行号；带历史修改标签的注释段须以 COBOL 注释列识别，不以头部调用清单判定有效路径。

| 功能 | 来源 | 当前证据/实现 |
| --- | --- | --- |
| 前台金额受理 | GSA01102:448 | checkCashInput 已验证一般正金额；核心零金额不能替代前台契约 |
| 核心金额受理 | KSADEP0:389 | 负数 E1095；SPP checkKernelInput，含零金额案例 |
| 日元粒度 | KSADEP0:344 | 表达式与 PIC 语义尚不能证明注释含义，待业务粒度确认 |
| 临时户期限 | KSADEP0:552 | checkDepositEligibility 已验证 EDF19 及临时户例外 |
| 销户与存入资格 | KSADEP0:603、614；CSAQRY1 | EO082、前台控制及核心销户/产品子集已验证；所选跨机构范围和挂失提示已接入，见 bank-qualification.md |
| 首次存入上下限 | KSADEP0:660–686 | checkDepositEligibility 已验证原明细次数及既有余额条件 |
| 余额上限 | KSADEP0:688 | checkDepositEligibility 已验证普通交易金额加原账户余额 |
| 警示/授权 | KSADEP0:750–860 起；GSYSEHRT | assessCashAdmission 已验证累计提示及一般/美元分级和所选例外；完整授权执行链路另验 |
| 偿还顺序 | KSADEP0:1481、1540–1768；PSACONST:1498 | 已迁入 calculateDepositPlan，普通/呆账/核销 |
| 余额及额度 | KSADEP0:1925–2067；SAACNAMT | 已验证计划、独立更新快照及 demo JDBC 共同提交 |
| 计息单位和日期 | CSAPRD2:309、332、363 | 已验证显式单位、业务日历、协定日期裁剪/分档及共同保存；协议读取及原调用条件差异仍待确认 |
| 计息天数的实际功能号 | PCMCONST:1133、1176、1182；CCMDAT1:292、8100/8200/G000 段 | `GT-PRDH=O`，ACT=1，存款天数=4；对应算头不算尾，360 类两端日数取 min(day,30) |
| 收费 | GSA01102:1413；KSAFEE0:194、267 | 普通收款账户费用计划及 demo 独立借贷已验证；原收费记账配置/其他分支未迁入，参数为 fixture |
| 业务记账 | KSADEP0:3714 起 | 金额分类及 demo 分录/共同提交已验证；真实 ART 配置未取得，见 posting-plan-source.md |
| 冲正 | KSADEP0:637、2642–2732 起、4640 | 已验证原实际金融分量反向计划及 ES020/EN249/EN177 子集；完整新冲正成交、跨日与费用尚未接入，不等于事务回滚 |

P1 的 14 个预期值沿用前期源码公式推导，完整列表见 `DepositKernelTest`。当前执行真实生成模型及场景，但未运行原 COBOL；未取得黄金值，不宣称逐位等价。

后续增加两项三位利息案例，以业务精确运算为预期：偿还分量保留 .005/.004 等值，不继承原两位偿还工作变量的隐式截断。这些是已确认“业务语义优先”方向的数学案例，不能列为原 COBOL 输出等价案例。

日历源路径特别核对常量后再迁移：CSAPRD2 使用功能 O，不是名称相近的 H；H 不算头尾并会减一天，不能替代当前路径。Java APP 仅解码并验证公历日期，SPP 根据 ACT/360365/360360 决定计算方法；日期解码不隐藏业务天数政策。日期非法 EE374、缺日期 EEC28、起日晚于迄日 E1175 均来自当前源常量及路径，未使用头部过时的错误说明。

## 差异登记

| 差异 | 处理原则 | 状态 |
| --- | --- | --- |
| 原利息三位小数、偿还变量两位 | 用户已选择业务语义优先；必要舍入须有业务依据，记录原截断影响 | 已有三位数学及存储案例；原 PIC 差异的运行值与额外业务舍入仍未确认 |
| 日元检查可能受中间表示影响 | 显式币种政策替代猜测的机器计算 | 待金额单位及规则确认 |
| 原总透支额在本金相等/略大时分支不同 | 当前按确认的源分支保留，并单独测试；合理性另议 | 已有两个计算案例 |
| 业务冲正与自动回滚 | 资格和原成交分量声明属于业务，反向执行可由框架自动化 | P4 先检查可逆元数据及日志能力 |

## 协定分档源码映射

CSAPRD2 的 5000 段按协定生效/取消日裁剪区间；5400 段读取五个阈值；5500/5550 段从槽位 5 向 1 按严格大于阈值逐档分配；5555/5556 段以大于等于阈值选中一档并使用全额。模式常量 PSACONST:1853/1855 为 1/2；模式 2 对应逐档，模式 1 对应全额，其他值按人民币/其他币种选择。calculateAgreementProduct 迁入核心分配，calculateDatedAgreement 已验证日期裁剪，完整协议查询尚待实施。

五槽的逐档取整与普通积数扣减为分别计算，不能假设积数总和在任意阈值/单位输入下保持原总积数。测试 amount=250、unit=100、最低两阈值 50/125 验证这一点：普通积数由 200 扣除 200，各档积数合计 100。该预期来自已读源算法，不是银行政策合理性确认，也不是原运行时实测。

## 普通收款账户现金收费映射

GSA01102:1427 的柜员渠道向 KSAFEE0 提交收款账户，付款账户为空。KSAFEE0:194 起调用 CSAFEE0，后者在普通存款账户分支中查询所属机构及四位跨行通兑地区代码（原字段切片由 APP 解码），按同机构/同地区不同机构/跨地区分别确定范围 0/1/2。同地区跨机构选择 SAC00001，跨地区选择 SAP00001，再按客户编号向 CCMFRT2 查询费率、折扣、固定费及上下限。

CSAFEE0:349 起先算金额×费率×折扣，再对变动费舍入，加固定费，最后按先最高、后最低的原分支限额。SPP 显式使用 roundHalfUp(...,2) 表达该非负收费域的舍入政策，保留固定费加入顺序及零最高费的实际限额。参数由 APP 查询给出；demo 使用明确的客户/收费代码 fixture，不声称银行实际费率。KSAFEE0 的负金额 EP192 在查询前检查。

本次只迁入所选现金存入的普通收款账户分支；多币种账户转调 KCMFEE0 的路径、付款方与收款方取较大费用、凭证、收费日志及实际记账尚未迁入。对柜员渠道的其他账户种类返回 demo 未支持错误，不能默默按零费用当作完成迁移。prepareDepositFee 场景真实调用分类、APP 客户费率查询及业务计算，未进行收费扣款。

## 协定日期场景映射

CSAPRD2:223–267 的业务区间为 max(上次积数日,生效日) 到 min(本次积数日,取消日)，取消日为空时使用本次积数日；生效日为空或无严格正区间时不计算协定部分。prepareAgreementWindow 迁入该选择，calculateDatedAgreement 使用同一套日历和分档服务计算完整计划。日期解码仍在 APP，区间选择与是否生效由 SPP 决定。原负阈值禁用标志及完整协议读取未迁入，不能据此宣称整个 CSAPRD2/KSADEP0 等价。

## 一般现金存入资格增量

GSA01102:707 起的机构控制、只付不收/锁定为 EN432，金额档冻结状态为 EG877；CSAQRY1:988 的销户记录为 EN113，9724/9725 对房易安产品要求特定业务码，一般现金存入不适用并返回 EI090。SPP 将前台和核心检查分别声明共享 check 服务，普通现金场景串联执行。仅冻结金额为正不能被当作冻结状态而拒绝，原计算规则仍使用金额参与可用余额推导。

普通产品所选跨机构范围和挂失提示现已接入，详见 bank-qualification.md。挂失 W 类消息分别返回并可继续成交；完整资格及多重错误优先级仍未证明。

## JDBC 本地执行证据补充

prepareDepositAccountUpdate 使用已有 DepositPlan 中的新计息金额/透支敞口和原偿还分量形成独立 DepositAccount。债务余额按原值减去计划偿还计算，冻结、授权及贷款状态保留；来源为 KSADEP0 已追踪的余额更新公式。本服务不实现冲正。

JdbcDepositStore 的 schema、JSON 成交载荷、版本条件及 Prepared 重放协议属于 demo 的 APP/PHY 实现，不能称为遗留数据库迁移或银行默认协议。JdbcDepositStoreTest 的六项测试通过生成的 prepareDepositPostings 和 prepareDepositAccountUpdate 取得更新值，再执行真实 H2 共同提交及故障/并发检查。证据支持本地计划落地，不支持完整受理、银行配置等价或原 COBOL 运行等价。

## 一般现金执行链路增量

NormalCashDepositTest 的九项测试执行 prepareNormalCashDeposit 到 JDBC 共同提交、待授权重验和原请求重放，补充了仅有计划落地时的证据。当前链路包含已迁移的资格子集，并非全部 CSAQRY1 规则。lastTransactionDate 绑定金额档 SA-LTM-TX-DT，按 KSADEP0:689 判断同日，1990–1991 更新，2029–2048 决定累计；不绑定通用账户档的 SA-LAST-TXN-DT。detailCount 按 2073 的 WK-DET-ITEM 加法，通过显式 demo itemCount=1 实施，尚未迁移实际多明细生成与未打印数量。配置、源金额分类和原运行结果证据仍分别标记。

## 审计执行证据

deposit_audit 与事件协议属于 demo 的 APP/PHY 实现，不是银行遗留审计接口迁移。JdbcDepositStoreTest 当前十项测试中新增四项覆盖失败审计、提交结果分类及审计不可用；NormalCashDepositTest 补充当次业务审计断言。当前回归 demo 76 项通过。成功审计共同提交，失败审计在回滚后独立保存；commit 异常和成功后的返回失败为明确模拟故障，不作为实际 COBOL 或银行网络故障恢复等价证据。

## 可执行报告与文件持久化证据

DepositDemoMain 的 10 个案例通过同一生成现金业务场景和 JDBC 提交，导出独立预期、实际数据库快照、来源标识、分录与审计。DepositDemoReportTest 验证报告内容和文件数据库正常关闭重开；最近模块回归 77 项通过。三位金额案例使用业务数学预期，其余具体配置均为明确 demo fixture。此证据支持演示路径真实执行及文件持久化，不支持原 COBOL 黄金等价或完整存款交易迁移已完成。

## 普通与透支积数共同保存

KSADEP0:1802–1867 以交易前计息金额和独立上次积数日计算普通/协定分量，1892–1920 传递交易前债务计算透支分量；1946、1973–1979、1992 保存累计及积数日。CSAPRD4:146–151 使用 ACT 功能 O，165–181 显式 .01 单位量化，184–191 按本金/普通透支息为正分别增加计数；币种单位查询在当前 5200 段未调用。DepositAccrualTest 六项测试执行生成场景及 H2，模块最近回归 83 项通过。

prepareCashDepositWithAccrual 的积数和账务在同一版本及快照条件下共同提交，原期间/实际分量在成交保存，文件报告验证关闭重开。业务精确求和后显式单位量化与原 PIC 截断分别标记。原协定保存入口只在第 1 档分量为正时调用，demo 则累计每个已计算的档；模式 1 高档情形等价性未确认，见 accrual-execution.md。此差异及未运行原程序不能因测试通过而略去。

## 金融反向计划证据

KSADEP0:4610 减原计息金额变化，4640 加原本金和两类利息偿还；前置容量不足 ES020、计息金额负值 EN249、计息金额/本金并存条件 EN177 已在角色服务中验证。DepositReversalAmountsTest 七项测试执行真实生成场景，包括后续消费/存入影响保留及贷款状态变化不重跑原分配。当前模块回归 90 项通过。

透支敞口采用实际原 delta 的逆分量，区别于原语句加原本金；符合已确认非覆盖目标，但不声称旧系统等价。4640 中日期、日累计和新增明细及 4630 的 KBN-ADD-PRDT 不是把所有旧快照或所有积数交换恢复。跨日及退费政策已提出业务决策，完整冲正尚未执行。

## 通存与挂失提示执行证据

CSAQRY1:1738 起的 9704、1874 起的 9709 及 2054 起的独立子类检查迁入角色服务。DepositBankQualificationTest 八项测试执行真实生成服务及现金提交，覆盖关系、柜员及交易例外的作用域，WN200/WN201 与 F0554 同时保留、原提示重放及拒绝时无成交。模块回归 98 项通过。角色是明确的解码契约，demo 不实现原银行查询，源结果运行等价仍未证明。

## 真实成交查询到金融计划

DepositReversalPreparation 从 demo deposit_trade 取得成功原成交，再查询其当前账户并执行生成场景。DepositReversalPreparationTest 四项测试验证实际现金/债务/三位成交、后续交易保留、无成交/容量/不一致记录拒绝及只读准备。当前模块回归 102 项通过。新的原成交一致性错误属于 demo 事实契约；尚未读取遗留 KBN 格式，也没有实现新冲正共同提交及完整跨日/退费政策。

## 反向分录候选与证据一致性

反向核心金额仍依据已记录的六类存入分量。实际 demo 账簿与成交载荷的科目、方向、金额必须一致，完整八槽和借贷平衡分别验证；两个收费槽位使用显式退费金额。DepositReversalPreparationTest 共八项测试含四项新增分录测试，模块回归 106 项通过；五个未执行候选进入演示报告。这里采用固定 DEMO 科目契约，不宣称原 ART/冲正记账配置等价，也没有执行实际退款或新冲正提交。

## 金融组件的物理成交

prepareDepositReversalAccountUpdate 从当前账户与反向金额形成独立快照；JdbcDepositReversalStore 保存原成交唯一关联、新账户、反向账簿及成功审计。JdbcDepositReversalStoreTest 十二项测试验证保留后续分量、并发/重复、版本冲突和故障，当前 demo 118 项通过。这是明确金融 fixture 的实际组件提交，不是完整现金冲正、银行 KBN/ART 迁移、跨日政策或量子/Saga 的运行验收。

## 冲正资格实际调用路径

CSAQRY1:235–247 按 SYS-TX-TYP 分支，2312 起的 DEP 冲正路径调用挂失、取消开户和全额冻结检查，不调用正常 9709 通存；KSADEP0:603 仍先检查 Closed。所选服务及四项 DepositReversalEligibilityTest 已执行，使用当前控制事实并保留例外作用域。JdbcDepositReversalStoreTest 现十四项，新增文件数据库正常关闭重开及身份错误的审计分类；模块回归 124 项通过。该证据不扩大到前台全量资格、跨日政策或进程崩溃恢复。

## Saga 恢复的证据范围

ExplicitSagaStep 调用原生 SAGA 策略并明确绑定 JdbcDepositStore 成交查询及生成反交易/JdbcDepositReversalStore。DepositSagaRecoveryTest 六项测试使用真实持久记录，验证只反原分量、业务恢复失败、稳定身份重试和反交易已提交但日志未完成的区别。当前 demo 130 项通过。这是金融组件的框架绑定，不是原 COBOL Saga 迁移、全银行恢复或跨进程自动扫描；没有默认补偿政策。

## 提交异常的两种查询结果

JdbcDepositReversalStoreTest 现十六项，新增 commit 前/后异常的实际 JDBC 状态对照，均标记结果未知并查询原冲正身份。当前完整 run-demo.sh 构建及测试为 demo 132 项、全 reactor 923 项通过。故障是进程内代理注入，不能标成银行网络或原 COBOL 实测；实际查询及重试证明不会因一次异常自动再反金额。

## 场景源文件导航

业务文件同属 cboddeposit 域：00-deposit-kernel、10-cash-admission、20-bank-calendar、30-agreement-product、40-deposit-fee、45-agreement-window、50-cash-deposit、60-deposit-accrual、70-reversal-financial、80-bank-qualification、90-cash-reversal、95-cash-transaction。根 cboddeposit.spp 只保留导航；部署/金额更新映射和物理配置分别在 cboddeposit.app / .phy。

## 纯源语言重构新增路由

`cboddeposit-85-deposit-route.spp` 在同域按可选银行资格及积数事实选择四种既有准备场景，条件执行由 SPP 生成。旧 Java 入口尚未切换，完整交易边界仍待迁移，见 [实施记录](source-only-refactoring.md)。
