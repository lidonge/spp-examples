# SPP 场景返回值绑定

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

场景可以将服务的一个业务返回值写入参与者属性：

```spp
Role Entry { String id; }
Contract Work { Entry original; Entry[] entries; }
atomic query <Entry entry> queryEntry(Entry key);
atomic query <Entry[] entries> queryEntries(Entry key);
Scenario serial load(Entry key, context Work work) {
    work.original = queryEntry(key);
    serial { work.entries = queryEntries(key); }
}
```

生成器调用服务并提取其声明的业务返回字段，不要求业务了解请求/响应包装类或 Java getter。标量和集合均可绑定；集合直接进入生成模型的 List 属性。可选查询缺失时，属性准确变为空值，而不是依赖查询键是否被填充；集合查询无记录时返回空集合。

目标必须是已声明参与者的属性，不能用赋值替换按值传入的场景参数。目标类型及集合维度须与业务返回值完全一致。当前只支持恰有一个业务返回值的调用；没有返回值或多个返回值的调用不能直接绑定。原来的忽略返回值调用继续支持。

绑定可用于串行/并行组、if/else 分支及显式事务中的服务调用，保留既有调用顺序、服务资源和事务协调规则。它是场景的数据流表达，不使查询变成更新，也不隐式创建持久化事务。

公共生成器测试实际编译并调用生成的标量/集合绑定、条件分支和显式事务，确认空值与非空值均正确进入参与者属性。
