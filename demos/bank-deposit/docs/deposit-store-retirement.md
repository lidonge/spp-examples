> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 旧存款存储测试的迁移责任

状态：JdbcDepositStoreTest十项旧方法已迁移删除；不跳过测试的clean verify通过（948项JUnit、83源入口），旧测试class及嵌套class不存在。此前删除分录测试暴露的旧夹具依赖已消除，未补写银行Java。

| 旧责任 | 当前源证据／剩余工作 |
|---|---|
| 债务、小数、原事实、收费与八条分录共同提交 | 债务现金、StoredFractionalPreparation、真实分录和查询入口已通过；源精度由PHY决定 |
| 重放不更新、不同请求不得复用身份 | replayCashExample、身份拒绝和跨JVM待授权/续接已通过 |
| 过期计划和伪造原账户快照不得成交 | cashVersionConflictExampleRun验证过期版本；forgedCashSnapshotExampleRun已通过同版本原快照999篡改的拒绝、完整回滚与新准备700成交；91/92/93在完整量子事务内锁定复核 |
| 账户/中途分录/提交前故障全部回滚 | cashWriteFailure、partialCashPosting以及beforeCommit实际JDBC源故障已通过 |
| 两个不同成交身份竞争同版本只成交一个 | 同身份现金并发及不同冲正身份已通过；differentIdentityConcurrentCashExampleRun真实两线程准备后屏障共同提交，恰好一笔成交/一笔版本冲突；新准备后两个身份均成交，余额800和量子4条 |
| 相同身份并发一笔成交一笔重放 | concurrentCashLifecycle真实线程及准备屏障已通过 |
| 回滚审计持久，稳定身份重试记录独立尝试 | cash故障各入口及history独立查询已通过 |
| 提交成功后响应失败应查询／重放 | afterCommitCashFault实际JDBC连接故障已通过 |
| commit实际调用前/后异常都须分类结果未知 | commitBefore/commitAfterCashFault的持久证据和稳定身份续接已通过 |
| 审计故障不掩盖主失败，缺失主审计不成交 | depositAuditUnavailable/rejectedDepositAuditUnavailable实际双故障已通过 |

账户复核应置于SPP的完整现金提交事务内，可复用已有APP锁定读取和sameFacts能力。不得在手写Java中添加提交前业务判断，也不得只证明版本CAS存在便声称原事实已复核。量子增量与普通账户快照各自的责任须明确：本 demo 仍有完整业务记录的版本更新，不能用覆盖一个过期快照替代量子增量。

对应新增源证据通过后才删除旧测试；最终clean构建确认旧class不存在。当前主13/测试2尚未清零，整个Goal未完成。


最新干净构建证据（2026-10-08 23:16）：`mvn -pl :xbod-deposit-demo -am clean verify` 成功，日志 `/tmp/spp-account-boundary-retirement-clean-validation.log`。JUnit 948项（lang303、appframe536、generator105、旧demo4）零失败、零跳过；APP83入口零失败，包括实际并发及两个独立JVM重启组。已确认JdbcDepositStoreTest、DepositPostingTest、DepositSagaRecoveryTest、JdbcDepositReversalStoreTest及ExplicitSagaStep的旧class和嵌套class均不存在。此证据对应83入口，随后新增现金报告源码及第84重启入口不包含在该证据内。剩余13份主Java、2份测试Java仍属待迁移违规项，Goal继续活动。
