# SPP 场景中的条件执行范围

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

原子计算里的 if/else 只决定参与者数据如何计算，不能代替场景中是否调用某个服务。为消除 Java 入口中的业务场景选择，Scenario 现在也可以按角色事实选择执行范围：

```spp
Scenario serial submit(Request request, context Admission admission, context Result result) {
    assess(request, admission);
    if (admission.executable) {
        transaction at {
            updateBusinessRecords(request, result);
        }
    } else if (admission.pendingAuthorization) {
        recordPending(request, result);
    } else {
        describeRejection(request, result);
    }
}
```

条件必须为 boolean，支持现有业务表达式；条件内不允许赋值、增减或任意 Java 调用。if/else/else if 都使用明确的花括号范围。只有选中的分支执行；其余分支的查询、更新和事务组不会启动。条件为 false 不等于异常，已选分支中的校验服务失败仍按其契约中止执行，不能吞掉错误继续提交。

原子校验或计算先形成参与者的业务决定，场景再用这个决定限定执行范围。警示、待授权和拒绝分别表示；不能仅用捕捉 `PENDING_AUTHORIZATION` Java 异常来隐藏授权流程。

分支可以组合服务调用、串行组、并行组、进一步的条件和事务组。分支中的顶层动作按声明顺序执行；需要并行时明确使用 parallel 组。分支是执行范围，不自动创建事务；事务边界与模式仍须写出。

编译时检查所有分支的角色引用、条件类型、服务参数和事务模式，包括运行时可能不会选中的分支。数字比较沿用 PHY 表示的生成机制，业务源无需改成 BigDecimal 方法链。现有 Scenario 的串并行行为不变。

XBOD 的 `cboddeposit-85-deposit-route.spp` 用可选银行资格和积数事实选择四种已有准备场景。当前新增源路由已生成并编译，旧 Java 入口尚未切换或删除；它是迁移步骤，不是纯源语言 demo 完成证明。
