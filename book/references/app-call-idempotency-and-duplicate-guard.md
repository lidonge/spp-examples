# 远程调用幂等与界面防重

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 需求与分层

SPP只表达业务。跨系统更新调用幂等、界面误操作防重以及技术调用头由APP／PHY负责。JVM内的本地调用不执行请求幂等或界面防重，量子服务内部成交去重仍由所选实现保证。

远程更新使用请求方身份、唯一请求方流水号和目标服务识别请求。相同请求恢复原输出参与者及结果；同一流水号改变内容是协议冲突。请求方身份由接入设施提供，不能把正文中的调用模式作为可信输入。调用设施建立LOCAL／REMOTE和USER／SERVICE上下文，进入服务后内部调用切换LOCAL。全局业务追踪流水号与请求方流水号分别存在。

界面防重只作用于APP对网页开放的场景入口。按声明的key及facts识别重复操作；服务调用服务不使用此策略。普通查询无需缓存。旧idempotency key语法保留解析兼容，语义改为界面防重，Petstore使用duplicate语法。

## APP配置

```app
requests {
    idempotency retention 3 days;
    duplicateWindow 5 seconds;
}
scope { local(in requestContext, out responseContext) {
    duplicate key(customer.membershipNumber, goods.sku)
        facts(agreement.quantity) addCartItem;
} }
```

期限使用“正整数 + 单位”，支持 day/days、hour/hours、minute/minutes、second/seconds、millisecond/milliseconds。旧的带引号 ISO-8601 Duration 仅保留兼容，生成运行时配置仍使用原格式。requests是应用默认策略，可在入口域定义一次；集中部署时合并显式声明，冲突报错。幂等期限从确定完成开始计算，默认三天，金融应用可选 `7 days`；界面防重窗口从完成开始计算，默认五秒；单个声明可在facts后加 `window 10 seconds` 覆盖。Petstore预约入口展示十秒窗口。正在执行、结果不确定或已部分提交的请求不因到期释放。

带单位时长的语法、Petstore 配置和生成链路已同步，`mvn -pl :petstore-demo -am test-compile -DskipTests` 通过；生成配置仍为 `P3D`、`PT5S`，框架协议不变。旧格式兼容和新格式校验用例源码已编译，未运行回归测试。编译日志：`/tmp/spp-readable-duration-compile.log`。

期限后不保证恢复旧结果；上游超过期限须确认原交易，不能直接当作新请求重试。界面窗口到期后的相同操作可作为新操作受理，是否仍满足业务资格由SPP校验。

## 框架协议与PHY

框架公开InvocationContext技术调用上下文、RemoteServiceIngress远程入口及RequestIdempotencyStore接口。接入适配器建立远程上下文并执行生成服务；存储接口原子登记、协调执行中请求、保存恢复确定结果、保护待恢复状态，并清理已到期完成记录。可替换实现必须遵守这些语义，不能通过默认接口退化为不可靠的先查后写。

内置内存和JDBC实现支持期限。JDBC下一次安装时为技术表补充expires_at列及过期索引；旧无期限记录保留，需单独迁移策略。本轮没有启动运行层，因此未改动现存数据库。JDBC登记和结果保存采用独立短技术事务，不能包住SPP事务。业务已部分提交或结果不确定时保留RECOVERY_REQUIRED；当前不提供自动业务恢复编排。PHY已有幂等store接入选择继续有效，第三方可实现公开接口替换。

PHY可声明 `config requestIdempotencyAdapter = "memory";`、`"jdbc"`，或实现类的完整名称；类实现RequestIdempotencyStore、提供无参数构造并通过configure接收配置。jdbc缺省沿用已有框架数据库配置。内存实现仅保证本JVM生命周期，不提供重启恢复。已过期完成记录访问时删除，且有新请求时最多每分钟触发一次批量清理；空闲期间可由PHY调度调用purgeExpired。

RemoteServiceIngress.execute接收生成服务、请求、接入设施确认的请求方身份及流水号。它自动建立REMOTE／SERVICE上下文、补全技术头；调用者必须复用原流水号和原输入才是重试。网页入口固定REMOTE／USER，以浏览器cookie区分客户端，HTTP X-SPP-Request-Serial携带点击流水号；浏览器标识只用于防重作用域，不是认证身份。网页正文不能更改调用模式。内部业务执行切换LOCAL，不重复登记。

生成的httpJson远程更新绑定自动携带requestUpdateEntry元数据，要求PHY配置callerId；发送X-SPP-Caller-Id、X-SPP-Request-Serial、REMOTE／SERVICE调用头。每个新出站调用生成一次流水号；传输重试复用同一报文。需要跨调用重试的接入设施可通过OutboundRequestContext复用原身份与流水号。接收网关根据已确认的身份和流水号调用RemoteServiceIngress；不能仅相信HTTP自报身份。界面/api入口始终是USER，不会因这些头被改成服务入口。

此框架协议不改变第三方系统已有HTTP报文约定，也不自动开放新的网络端点；第三方接入设施需要对接公开入口API。

## 实施路径与验证

1. 增加APP全局期限及duplicate声明、编译校验和生成元数据。
2. 提供可信调用上下文、远程更新幂等入口、界面防重入口及可替换存储协议。
3. 内存和JDBC落实执行中保护、完成期限及过期清理。
4. 更新Petstore配置和网页技术头，保留启动与expose语义。
5. 补充针对机制的测试源码，仅生成与编译，不运行回归、数据库或服务。

与传统方案相比，统一协议消除业务代码中的查重、requestId传递和缓存重放；本地调用没有重复登记开销。代价是调用设施必须建立可信身份，存储必须支持并发协调、期限和结果恢复；协议不能自动解决部分提交业务的恢复，也不提供无限期重试保障。

远程服务执行的量子追踪依据使用请求方／流水号／服务的命名空间，避免两个系统的同号请求在量子成交去重中冲突。界面窗口到期后的新执行使用新的技术追踪依据。JDBC提交证据同时记录事务外已提交的更新，后续局部回滚不能释放包含已成交步骤的请求记录。

## 本轮验证记录

`mvn -pl :petstore-demo -am test-compile -DskipTests`通过，最终日志为`/tmp/spp-call-protocol-final-build.log`。Petstore生成并编译837份生产Java，3份测试源码包含32个测试方法；新增编译器、请求协议和JDBC期限测试源码也已编译。未运行任何测试、服务或数据库操作。

静态核对记录`/tmp/spp-call-protocol-static.txt`确认：30个场景的生成元数据区分22个更新、8个只读入口；P3D／PT5S默认策略及预约PT10S覆盖已生成；Petstore不再使用旧idempotency key／business列表。node语法检查及git diff --check通过。运行期并发、过期和恢复行为仍须后续执行验收。

远程入口的 Java 包装顺序为：登记或重放请求 → 进入业务事务上下文执行服务 → 退出业务事务上下文 → 保存调用结果。幂等属于技术协议，SPP 不添加调用语句；命中已有结果时不进入业务事务。跨域原子调用的完成记录表示该次调用结果，全局事务最终结果仍由协调器决定。

## 多参与者防重事实

APP 的 facts 可以列出一个或多个参与者/属性路径：

```app
scope { local {
    duplicate key(Buyer.membershipNumber)
        facts(Agreement, Selection.option, AuthorizationEvidence) window 5 seconds submit;
} }
```

key 确定界面操作的短时防重槽位；facts 核对该槽位的业务输入，任何一个声明事实变化均按现有内容冲突协议处理。多个事实可以包含为空的可选属性，空值也参与核对。旧单路径写法及运行协议保持兼容。

生成服务提供 getDeclaredIdempotencyFactsPaths 列表元数据；旧接口 getDeclaredIdempotencyFactsPath 在单路径时保留，多路径时不冒充第一项。远程代理读取这些元数据不调用远程业务适配器。系统调用仍按可信请求方/流水号幂等；此配置不将业务查重放入 SPP，也不隐含扩展业务事务。
