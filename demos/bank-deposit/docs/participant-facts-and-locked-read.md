> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 原交易事实复核：业务比较与物理锁定

冲正候选在准备阶段读取的原存款成交，必须在提交的完整 SPP 事务中再次复核。账户版本 CAS 防止过期余额计划提交；它不能证明原成交凭证没有改变。这两种检查承担不同责任。

## 业务表达式

`sameFacts(expected, actual)` 接受两个声明类型和集合维数一致的 Role 或 Contract，返回 boolean。比较只遍历 SPP 声明的属性，包含嵌套参与者和有序集合；忽略生成器附加的技术属性。两个 null 相同，一方 null 不同。数组和集合按照元素顺序比较；长度或元素事实不同即不相同。循环引用避免无限递归。

内置数值按照数学值比较，BigDecimal 的标度不作为业务差异。选择 PHY 数字适配器的属性调用其 compare，实现用户选择类型的比较语义，不强制要求转换为 BigDecimal。没有声明模型元数据的任意 Java 对象不进行猜测性 bean 比较。此谓词不修改既有对象 `==` 的引用语义。

源表达式由生成器产生声明模型及 getter 的比较元数据，公共运行库负责通用递归比较。不得将银行 JSON 文本比较写入运行库。银行源在 check 服务中决定原成交缺失或变化应返回哪个业务错误。

已完成针对性验证：BusinessCalculationSemanticsTest、ParticipantFactsTest 和 ParticipantFactsGenerationTest；生成代码实际经 Java 编译并执行，涵盖嵌套属性、集合、null、循环引用、BigDecimal 标度以及不提供 decimal 转换的自定义适配器。日志 `/tmp/spp-participant-facts-framework-validation.log`。此验证尚不表示银行提交已接入。

## APP 读取策略

APP 采用 `repository(argument(0, Receipt.id), receipt) using records for update optional lookupReceiptForCommit;`。`for update` 只声明单个身份的同步查询锁策略，`optional` 允许业务 check 自行判断缺失。禁止集合锁定查询、异步调用和省略显式返回。集合缺失仍由原有查询语义处理。

锁定读取只使用调用者已声明并已登记该 repository 的事务及连接，不另开事务、不自行提交或关闭连接。没有业务声明事务或没有登记连接时拒绝执行。不支持锁定读取的 repository 明确报不支持，不退化为普通读取。

当前 JDBC snapshot 实现锁定确切 `(objectType, objectId)`，返回持久 snapshot 的完整声明事实；不回落到未锁定的 APP 原生表或模糊属性匹配。APP 表镜像的原始 SQL 外部修改不受该 snapshot 锁保护，需要相应存储策略提供完整一致性；本 demo 的源更新通过同一 repository 同步写入。未存在的行不宣称提供缺失身份的范围锁。

锁从读取保持到外层事务完成；原凭证变化由 SPP 比较拒绝，整笔冲正回滚。锁定读取针对性 reactor 已通过，共27项JUnit无失败/错误/跳过，包含参与者事实比较与生成执行、查询绑定语义、普通可选查询兼容、事务外拒绝、未登记连接拒绝、同事务未提交数据可见、竞争更新实际超时及外层回滚后释放锁。日志 `/tmp/spp-locked-repository-framework-validation.log`。

银行源93已加入原成交证据、锁定读取及 check，91的冲正记录归档原存款快照，99已拆分 prepareCashReversalAttempt / submitPreparedCashReversal，保留旧入口的组合调用。SPP完整 quantum 边界保持明确。银行接入已通过完整增量 verify：975项JUnit和全部71个既有APP源入口通过，日志 `/tmp/spp-original-evidence-binding-source-validation.log`。新场景实际生成、编译及运行；原凭证改变、过期候选和准备结果重放的独立源案例仍待实施，不能把既有入口通过当作这些责任已经验收。

## 后续源案例的独立预期

银行接入基线通过后，按以下具体状态验证准备结果提交，所有夹具、更新和断言均为 SPP/APP/PHY。

1. 原存款600、收费2、后续存款100，当前账户版本2/余额800。准备冲正后，用声明式 update 改变原存款持久凭证的 settled.version 为99，账户本身不变。提交必须报 ORIGINAL_DEPOSIT_RECEIPT_CHANGED/ROLLED_BACK；账户仍版本2/800，没有新冲正成交或分录，原关联为空，量子日志仍只有两笔存款的4条。恢复夹具原事实，按同一冲正身份重新准备，成功后版本3/200，原及后续存款保持，量子日志总6条。
2. 同样准备冲正后，另行实际存入5，当前版本3/805。提交旧候选必须被版本保护拒绝，保留这笔后续存款；重新读取/准备后冲正只逆转原存款分量，最终版本4/205，不恢复旧账户快照。旧候选不得残留冲正成交、关联或量子日志。
3. 已成交冲正的准备结果重放，需要先以冲正稳定身份读取原成交，再比较它归档的原存款事实。相同原事实只能确认成交并记录重放，不再次执行；改变原凭证而复用该冲正身份，必须报 DEPOSIT_REQUEST_ID_REUSED。原请求入口和准备结果入口应共享成功/失败审计规则及并发结果查询，不能靠原子提交服务的唯一冲突冒充业务身份校验。

这些是待实施的验收责任，不计入现有71个已通过源入口，也不据此删除仍承接相关责任的旧测试。

三个准备结果案例已完成并实际通过：99zu、99zua、99zub。完整增量 verify 为978项JUnit、74入口全通过，日志 /tmp/spp-prepared-reversal-corrected-source-validation.log；仍不能据此认定全部Java已迁移或最终纯源验收完成。
