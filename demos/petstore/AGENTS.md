# Petstore 演示约束

- 业务实现只能使用 SPP、APP、PHY，不得手写业务 Java；Java 测试可以在 src/test/java 中组合生成场景、准备输入、编写断言及注入技术故障。生成结果只在 target。
- Java 框架扩展只能提供通用能力，不得硬编码 Petstore 字段、状态、公式或流程。
- 事务一致性边界在 SPP 显式声明；影响业务提交及失败结果的嵌套传播语义也应在 SPP 可见，普通 transaction 默认 REQUIRED，传播名称包含 REQUIRES_NEW、NESTED；新版策略按 docs/transaction-storage-v1.md 的能力矩阵校验，未支持组合编译报错。事务实现模式及资源机制由 APP／PHY 约定，事务内量子属性自动保持量子一致性。APP 决定部署、接口暴露及仓储绑定；PHY 决定数值表示与存储。禁止在 SPP 中选择 quantum、AT、Saga 等实现模式。
- 网页只展示服务事实并提交命令，不能计算价格、判断业务资格、执行库存或状态更新。
- 先维护需求、路径与对比文档；能力缺口要明确登记并完善生成链路，不能通过脚本或 Java 绕行。
- 不改变既有 petstore、business-showcase 或银行 demo 的业务实现。

- 业务Scenario只能调用原子服务，禁止调用Scenario；不同业务动作分别定义独立场景。
- SPP 不定义 Verification 或测试夹具；测试编排不得注册为生产服务或APP web入口。普通原子服务不得调用其他服务；calculate可调用calculate，禁止其他服务调用和循环计算调用图；共享校验组合属于场景执行组，具体复用语法待设计。

- 业务场景和原子服务禁止用ShopWork等全局参与者集合代替明确参数；只携带实际参与的角色及业务合约。
- 场景必须明确声明内部所需参与者；入口可只有有限属性，由查询或其他原子服务补全。参与者只能由原子服务创建，场景不得构造或隐式引入参与者，入口参与者始终保持同一实例；查询原地补全，不使用返回赋值。SPP不定义异常控制语法。
- 数据库更新场景必须有明确业务Contract参与；不能仅将技术上下文改名为合约。跨场景生产组合只在前端进行。

- 业务校验由场景显式调用check；共享check由场景执行组组合，不能包装成互相调用的原子服务；calculate不混入校验。技术防重幂等属于APP／PHY。源码已分离check与calculate；防重键和内容比较在APP声明，普通更新缺省由APP/PHY基于可靠读取修订标记条件提交，兼容显式advanceVersion；SPP不能重放查重或递增技术版本。
- 状态等有限取值的业务属性优先使用枚举，业务表达式引用枚举成员，枚举值及接口值使用英文代码；中文等本地化文案在展示层或APP/PHY国际化配置中维护，不写入业务枚举值。

- 入口只允许参与者，默认实例名为角色名，保留显式实例名；无参数调用按类型及集合维度唯一绑定。查询确认使用if(参与者)/identify，不能用参与者null判断是否查询到。
- 普通check失败按词法block控制执行，缺省不回滚；显式checkXXX,breakTransction;仅在失败时撤销当前事务，成功继续；量子服务只声明加减；调用处用bounds声明nullable上下限，自动校验成交值，失败撤销绑定事务。旧内置check仅作兼容，不用于新演示。具体执行约定见根目录book/references/spp-participant-execution.md。

- Contract必须对应明确业务场景并表达业务约定，不得作为通用命令、中间计算值、集合或结果包装。不得用ShopCommand/action字符串及场景动作匹配校验表达独立业务；APP按具体场景映射参与者，前端选择入口。明细/值结构语法不足时完善生成链路，不能机械改成Role。

- 多域演示采用真实独立客户域/产品域，Person/Product 在消费域为 Reference；APP 集中部署不改变域归属，不能用 Mock 或跨域直接读表代替服务协作。新跨域绑定与应用级部署语法不足时应明确登记并完善生成链路。

- 普通参与者事务内查询默认生成锁定读取；混合参与者也修改普通属性时锁定，只有量子变化时不加普通读锁。SPP不声明数据库锁，APP/PHY无需新增forupdate配置。量子属性统一归逻辑量子域，真实数据库/TCC/专用量子实现由APP选择、PHY接入；不把逻辑域等同固定物理部署。

- 普通事实事务外读改写采用默认乐观保障，修订标记不进SPP。量子事实在选定量子存储补全和成交，不复制保存到普通快照；场景防重不得隐含包住多个源事务。

- 远程更新按请求方身份及唯一请求方流水号幂等；本地调用不登记请求。界面防重只在网页场景入口执行，APP用duplicate声明，默认5秒；远程幂等全局默认3天。执行中／待恢复记录不因期限自动释放。规范见docs/app-call-idempotency-and-duplicate-guard.md。

- 标准主键查询、普通 insert/update/delete 与唯一 Reference 提供方绑定默认生成，不重复写 repository/persist/bind。本地复杂非主键查询直接由 APP repository 实现；定制外域查询只绑定目标，参数必须是相同参与者身份或有显式 take，不能按字段形状猜测。角色查询默认先查本域角色，再沿 take 递归通过所属域服务补全根角色或实体，禁止直接跨域读表。
- 标准 CRUD 不在 SPP 重复声明；直接调用 find/insert/update/delete + 参与者类型名，集合沿用同名调用。复杂查询及业务原子服务保留显式定义。规范见 ../../book/references/implicit-participant-crud.md。
- 跨域标准 CRUD 通过 Reference 与唯一显式 take 自动绑定：insertPerson(customer)/updatePerson(customer) 维护客户域主体，insertBuyer(customer)/updateBuyer(customer) 维护商店域角色。不保留 registerPerson(Buyer) 等重复代理声明。
- APP 可以新增 SPP 中不存在的技术主键；生成的 CRUD 必须使用该主键定位记录，技术身份通过 APP 映射与运行时管理，SPP 不显式定义或操作。单扮演者角色可用扮演者主键确定 APP 新增主键列的值，默认 CRUD 自动生成。

- 本轮事务与属性归属以 ../../book/references/transaction-storage-v1.md 为准：APP 选择普通原子服务模式，同角色必须一致；非LOCAL时量子阶段先成交，普通阶段随后提交，跨模式采用 Saga 恢复；本轮LOCAL例外以 ../../book/references/deployment-environments-and-physical-defaults.md 为准，所有参与域同JVM、同数据库/schema/连接资源时量子与普通更新共同提交。角色普通持久化只写自身表，不隐式保存扮演者。新增/重定义属性归角色，继承/映射属性默认归原域；APP snapshot 声明的普通映射属性副本在角色表独立保存，不反向保存扮演者，见 ../../book/references/role-mapped-storage.md。业务补偿议题待专门讨论。
