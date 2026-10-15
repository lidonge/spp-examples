# SPP 场景失败处理

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

当前语法使用 `transaction { ... } fail { ... }`。场景通过系统内置 `ResultInfo` 读取失败码、原因、服务来源及恢复结果，不声明失败参与者，也不使用 try/catch/throw。完整定义见[事务失败处理与系统结果](spp-transaction-failure-handling.md)。

旧银行 demo 中的 try/catch/throw 是未迁移的历史源码，不再属于当前合法 SPP 语法。本文原有 catch、显式 FailureFacts、throw、context 等示例已撤下，避免被误当成可用设计。APP/PHY 的生成 Java 仍可用技术异常处理来实现恢复及错误保留。

本地回滚、已成交量子反交易和业务处置是不同结果；提交未知或恢复失败不能因 fail 执行完而变成成功。历史技术故障证据继续由 TransactionOutcomes 保留，系统结果不会把此前独立提交的交易说成已经回滚。
