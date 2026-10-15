# SPP 场景事务失败处理与系统结果

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 需求与语法

场景可以声明 `transaction { ... } fail { ... }`。fail 是上下文关键字，原有同名服务仍可正常声明和调用。事务执行和技术恢复先结束，随后执行失败块。业务层不声明 try/catch/throw，不接触 Java 异常对象；fail 内可查询业务事实、调用校验/计算服务，以及用新的显式事务保存业务处置。

`ResultInfo` 是场景内置参与者，不出现在入口参数中，也不由业务开发者声明。它不能作为原子服务参数，原子服务不能直接读取系统结果。编译器为相关合约提供系统 `resultInfo` 属性；该属性随场景返回，不作为普通业务存储属性。要长期保存的拒绝原因、待人工处理状态等仍是合约自己的业务属性，由 fail 中的更新保存。

场景只有一个标量合约时，fail 默认关联它；多个合约时写 `fail(目标合约)`，也可始终显式选择。系统仍只修改已有入口合约内部的结果，不替换合约实例。fail 与事务体是两个相邻作用域，fail 不属于已经失败的事务。

## 系统结果字段

|路径|含义|
|---|---|
|`ResultInfo.status`|PENDING、SUCCEEDED、REJECTED 或 FAILED；FAILED 表示事务失败，业务处置成功不改写失败事实|
|`ResultInfo.handled`|失败后的业务处置已完成，且技术恢复结果确定；不代表原事务成功|
|`ResultInfo.failure.code`|失败码，当前运行协议沿用原失败消息；无消息用 TRANSACTION_FAILED|
|`ResultInfo.failure.reason`|失败说明，不是 Java 异常对象；内置 JDBC 量子库提供具体越界说明|
|`ResultInfo.failure.serviceName`|已确认的失败服务名称；无法定位时为空，不能猜测|
|`ResultInfo.failure.resourceName`|已确认的失败资源名称；无法定位时为空|
|`ResultInfo.failure.phase`|EXECUTION、QUANTUM_SETTLEMENT 或无法细分时 TRANSACTION|
|`ResultInfo.failure.transactionOutcome`|UNREPORTED、ROLLED_BACK、COMMITTED、UNKNOWN，针对失败边界，不代表此前独立交易|
|`ResultInfo.failure.recoveryStatus`|ROLLED_BACK、REVERSED 或 RECOVERY_REQUIRED；REVERSED 表示已成交阶段已由系统恢复，不等同数据库回滚|
|`ResultInfo.failure.attribute`|可选的失败业务属性名，例如 inventory.StockLine.available|
|`ResultInfo.failure.actualValue`|可选的成交尝试值，用精确文本表达；不是成功成交值|
|`ResultInfo.failure.minimum` / `maximum`|调用约定的上下限文本；null 表示对应方向无边界|
|`ResultInfo.failure.causes`|原因链中的说明，保留顺序，不暴露 Java 类|
|`ResultInfo.failure.suppressedCodes`|附加的恢复或清理失败说明|

失败块可以在结果不确定时记录待核对信息；系统仍把原技术失败交给 APP/PHY，不能仅因执行完 fail 就把未知提交视为成功。只有恢复确定且 fail 正常完成，失败才成为已处置结果。fail 的保存也失败时，原失败保留，处置失败作为附加原因向 APP/PHY 报告。第一版只支持串行场景中外层事务的 fail；嵌套事务或并行分支中的 fail 编译报错，分别避免吞掉父事务的撤销信号和并发覆盖同一个系统结果。事务内部普通更新的 APP 自动并发仍可启用，不受此限制。

## 量子恢复与业务补偿

量子越界没有成功成交，不需要再补一笔反交易。LOCAL 内未提交的量子与普通变化共同回滚。非 LOCAL 已提交量子阶段由运行时根据成交记录自动反交易，完成后再执行 fail。业务拒绝、保留已受理申请、待处理记录等由 SPP 明确编写，框架不自动发明业务处置。

预约示例和验收路径见 [Petstore 预约失败处置](../../demos/petstore/docs/reservation-failure-handling.md)。更一般的业务补偿政策、远程恢复协议与嵌套 fail 后续扩展仍需独立讨论，不据此自动推导业务反交易。


## 实施路径及与传统方案比较

1. 解析 fail 的独立业务块及可选合约选择，使用编译器内置 ResultInfo/FailureInfo，不增加入口。
2. 校验合约选择、场景专用系统信息及首版嵌套限制；生成 Java 调用通用运行层。
3. 独立记录 Saga 各阶段与恢复交易的结果，避免把已经提交又完成反交易的阶段混成未知的数据库回滚结果。
4. 量子及普通阶段恢复结束后补全系统事实，运行 fail；业务处置另开明确事务。
5. 验证库存不足、普通保存失败、已成交量子反交易、提交未知和处置失败，最后回归生成链路及 Petstore。

传统 Java 通常需要手写 catch、解析异常并组织恢复事务。SPP 将业务处置写成明确的 fail 块，将技术故障对象、恢复顺序和错误保留交给生成框架。优势是业务不会手写库存逆增量或吞掉未知提交；代价是内置结果协议、物理恢复证据和跨模式恢复必须由框架可靠实现。fail 不自动创造业务补偿政策。


物理实现可以通过通用 FailureReasonProvider 提供稳定失败码和可读原因，也可以补充属性及边界信息；该接口只存在于 APP/PHY 的 Java 实现层，SPP 读取的是系统失败事实。尚未提供结构化原因的实现沿用原失败说明，详细边界字段为空，不能猜测。

## 验证记录

2026-10-13 执行 `mvn -fae -pl petstore-demo -am test -Dspp.environment=develop`，BUILD SUCCESS：语言 356、运行框架 607、生成器 105、Petstore 36，共 1,104 项测试，失败、错误和跳过均为 0。另通过 `git diff --check` 与网页脚本 `node --check`。

专项覆盖内置参与者作用域、合约关联及存储排除、嵌套和并行限制、原失败保留、未知恢复不能被吞掉、处置失败附加原因，以及 JDBC 量子阶段成交后自动反交易先于 fail 执行。Petstore 使用 develop 的本地共同事务验证库存不足、普通保存失败、成功预约及原始远程请求幂等重放；本轮不据此宣称验证了真实分布式 TCC 或外部量子服务。
