> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 量子属性与现金事务

本文前半部分保留旧手写实现的核查说明，不能作为纯源迁移完成的证据。当前执行路径以 SPP 92/93 的整笔 quantum 边界、APP 仓储/资源绑定和 PHY 后端为准；下面提到的 CashQuantumLedger、JdbcDepositStore、JdbcDepositReversalStore 都是待删除的旧实现。

业务源已按场景拆为 `cboddeposit-00` 到 `cboddeposit-95` 文件，同属 `cboddeposit` 域，根 `cboddeposit.spp` 是文件导航。APP 和 PHY 仍独立。

账户计息余额、冻结/授权金额、透支本金/利息/敞口，资格中的净余额和日累计、请求金额及分录金额明确标记 `quantum double`，APP `cashLedger` 列出所属属性；PHY 用 `jdbcQuantum` 配置量子日志和值表。现金适配器为这些表建立十进制字符串列，避免通用量子表默认小数位数造成隐式截断；超过物理列容量时由数据库拒绝，不静默舍入。BigDecimal 表示仍由 PHY 选择，量子性质与存储数字类型分别表达。

实际现金金额守恒路径见 `cboddeposit-95-cash-transaction.spp`：客户净余额与带符号现金对手方金额组成 `cashSettlement`。SPP `transaction` 调用量子更新 `moveCashQuantumValue`，APP 表达余额增加和对手方金额减少。存入时净增原存入金额；现金冲正时净减原金额。透支本金及利息的分摊仍由业务计算服务决定，不能只按计息余额与现金原金额配对，否则偿还透支时不会闭合。

`CashQuantumLedger` 使用实际账户 ID 区分量子对象，读取当前对手方金额，并运行生成的事务场景。`JdbcDepositStore` 与 `JdbcDepositReversalStore` 在共同提交前调用它。量子日志和值更新通过 `JdbcTransactionScope.withConnection` 加入该账户/成交/分录/审计的同一个 JDBC 连接，外层拥有提交、回滚和关闭权。重放已成交记录不重复运行量子更新。

demo 在单 JVM 的共享事务管理器上执行这段物理绑定；绑定期间同步并恢复原适配器，避免并发 demo 请求互相改写绑定。它不是跨数据库量子服务部署。原较早的无银行事实金融组件 fixture 仍单独验证 JDBC，不宣称那些 fixture 产生了量子日志。

量子属性声明不等于每个金额都能单独撤销：原请求和原分录保留为成交事实；现金冲正资格、日期、收费及特殊敞口公式沿用 XBOD。账户事实、日期、警示、原记录关联等非量子状态与量子金额共同由本地事务提交，不能用反向净金额替代整笔银行冲正。

银行完整冲正须调用 CashDepositReversal；通用 `reverseCommittedQuantumBoundary` 只处理其量子边界，不包含本 demo 的账户 JSON、资格、费用和原关联，因此不是本项目整笔银行冲正 API。当前可执行保障是单数据库共同事务，不能扩展为任意分布式量子服务已接入。


纯源迁移中的精确存储（实施中）：PHY cashLedger 现在显式 `config decimalStorage = "text";`，公共 JDBC 量子存储以文本保存数值，保留 PHY BigDecimal 的极小金额；默认 decimal 模式继续兼容已有工程。text 会检查既有列类型/容量，不符合即拒绝启动，不自行删表或修改数据。99zp 通过 APP 原生表映射查询真实日志和当前值，按源 quantum 调用验证 1e-25；完整源运行仍在验收。旧 CashQuantumLedgerTest 尚待账户隔离和失败分支的源责任承接，不能视为已删除或整体纯源完成。

99zp 精确存储阶段已完成增量完整验收：960 项 JUnit、62 个 APP 根入口全部通过。实际文本日志和当前值查询保留 1e-25，并验证两条 COMMITTED 记录的原值、增量、成交值和增减守恒。99zpa 的下一轮再验证两个对象隔离、显式 quantum 失败无持久残留后再次提交，以及错误 before 值拒绝、原记录不变、合法新值再次提交；该轮尚在运行，旧量子测试仍保留。业务公式始终使用业务数字，精确表示及存储容量由 PHY/APP 明确选择。
