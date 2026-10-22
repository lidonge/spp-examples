# APP 技术服务与服务拦截

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 需求及分层

技术服务为场景及原子服务提供日志、计时、技术访问控制等设施。SPP 不调用它们，也不增加技术参与者。APP 决定服务名称、匹配范围和执行阶段；PHY 选择 Java 实现及配置。技术实现不能代替 SPP 的业务校验、计算、更新或失败补偿。

```text
technical services { invocationTrace; }
intercept services {
    before: invocationTrace;
    after: invocationTrace;
    failure: invocationTrace;
}
```

`intercept services` 匹配当前业务域的所有生成服务，包括标准 CRUD、量子服务和场景；`intercept scenarios` 只匹配场景；`intercept findBuyer, reserveShopPet` 匹配指定服务。跨域提供方由其自身 APP 配置，消费方的代理仍是消费域服务。每次逻辑服务调用只拦截一次：原子服务的类型方法和统一 execute 入口均生效。

```text
phy {
    technical service invocationTrace {
        implementation: "com.servpp.service.technical.InvocationTraceService";
        config logger = "spp.invocations";
    }
}
```

## 执行协议

配置按源码声明顺序合并，每个阶段内部按列出顺序执行。同一服务、阶段和技术服务重复匹配编译报错，避免重复执行。未知服务、非服务目标、未知阶段、未声明技术服务、缺少或重复物理实现也编译报错。实现类接口及构造能力在服务注册时检查。

|阶段|含义|技术处理失败|
|---|---|---|
|before|业务调用前；可以拒绝技术访问|阻止业务调用，执行 failure，然后保留原错误|
|after|调用正常返回，包括业务校验不通过、fail 已处置的结果|记录技术诊断，继续后续 after，不改变已返回的业务结果|
|failure|调用向外传播技术错误；不是业务 check 不通过|附加到原错误，继续后续 failure，不替换原错误|

before 在场景入口位于场景自己的事务及远程幂等执行之外，所以重放也记录调用。原子服务在事务内被调用时，其拦截器也处于该调用时点；不承诺原子拦截器在事务之外。after 不是事务提交回调，原子服务返回后外层事务仍可能失败；多事务场景也不能用一个 after 代表某笔提交。尚不提供独立提交回调或拦截器自行重试、改变业务返回值的协议。

技术接口接收只读调用元信息：服务名、阶段、服务类别、受信任的本地/远程调用头、耗时、业务校验结果及传播的技术失败。它不暴露可修改的业务参与者。实现应线程安全，不能通过此扩展隐藏业务行为；初始化一次，实例可被并发调用。拦截器本身不注册为 SPP 服务，避免全服务匹配造成递归。

PHY 可以在 environment 中选择实现及参数，配置值沿用 `${系统属性:默认值}` 的物理参数解析。每个生成业务服务注册时建立一份拦截计划；同名技术服务在该计划的各阶段共享一个实例，不承诺跨业务服务共享同一个单例。自定义实现须实现框架 TechnicalService，提供公共无参构造器，通过 configure 接收不可修改的配置，通过 handle 接收技术事件，并放入应用运行时 classpath；它不是 SPP 原子服务。

首版以实际服务方法调用为拦截边界；跨域原子 RPC 协议自身重放缓存响应而未调用服务方法时，不会重复触发原子方法拦截。场景生成的 execute 拦截则位于场景幂等之外，每次入口调用仍有事件。网络接入层的逐请求过滤和独立事务提交回调不属于本次方法拦截协议。

## 实施路径及比较

1. 编译 APP/PHY 声明并校验引用、匹配范围、重复规则，向各生成服务写入明确技术绑定。
2. 注册服务时初始化实现。保留场景生成类的类型，原子服务在现有持久化与远程代理之外增加技术拦截。
3. 通用运行层按 before → 业务调用 → after/failure 执行，不改变源事务语义。
4. Petstore 用通用日志/耗时服务展示全服务拦截，Java 测试只捕获日志及准备输入、断言。
5. 验证直接原子调用、场景正常及失败、访问拒绝、阶段错误保留、并发、幂等重放和默认未配置行为。

传统方案通常在业务代码加日志或手工配置 AOP。SPP 的优势是技术绑定独立于业务，默认 CRUD 也可被统一覆盖，并在编译时验证目标；代价是首版只提供固定阶段和受限元信息，复杂 AOP 切点、业务参数改写及提交钩子不在本协议内。

## 验证记录

2026-10-13，`mvn -fae -pl petstore-demo -am test -Dspp.environment=develop` 完整生成与回归通过：语言 362、运行框架 617、生成器 105、Petstore 39，共 1,123 项测试，失败、错误、跳过均为 0。另通过 `git diff --check` 和网页脚本 `node --check`。

新增专项覆盖匹配范围与标准 CRUD、编译错误、PHY 环境选择、直接原子方法调用、场景类型保留、重复入口抑制、技术访问拒绝、观察阶段失败隔离、当前 check 结果、并发调用上下文、物理参数解析、远程代理元信息读取，以及 Petstore 查询故障、量子预占和场景幂等重放。远程代理覆盖使用运行框架的可控传输实现，本轮没有进行真实跨 JVM 部署验收。
