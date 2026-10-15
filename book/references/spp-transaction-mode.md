# 事务实现策略与业务传播

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

SPP只声明事务一致性范围及传播关系。`transaction { ... }` 默认 REQUIRED，支持 `transaction REQUIRES_NEW` 与 `transaction NESTED`；不再支持业务语法中的 at、tcc、saga、quantum。详细语义及本地实现限制见[事务边界设计](spp-transaction-boundaries.md)。

APP在原子更新服务上绑定实现策略，PHY提供资源和能力。生成器解析共同提交边界的策略并拒绝冲突；生成的运行时元数据仍使用TransactionMode进行技术检查，这不是SPP语法。空事务边界报错。旧样例带模式的SPP语法需要迁移，本次不批量修改其他demo。

## 独立场景与条件事务成员

业务Scenario只能调用原子服务，不能调用Scenario。场景不是可复用子流程；每个业务场景明确自己的事务边界和传播关系，查询、校验、计算、更新原子服务才是复用单位。编译器递归检查执行组、条件分支、guard及事务中的调用，禁止嵌套业务场景。运行时事务成员也拒绝动态替换为业务场景或验收编排。

事务体可直接包含原子服务调用、串行组、if/else和guard校验。例如同一场景可以按业务资格跳过一个校验范围；技术幂等重放由APP处理，不能根据action在一个场景中分发注册、付款、发货等不同业务。事务中的条件更新由SourceTransactionUpdates纳入当前场景显式声明、由APP绑定AT/QUANTUM实现的边界，不涉及子场景继承或隐式开启事务。当前条件更新不支持TCC/Saga，事务内parallel子组被拒绝，不能宣称跨线程或跨库原子性。

原先“子场景继承事务”的设计已撤销。Petstore以独立注册、购物车操作、下单、付款、履约及取消退货场景展示此规则；旧版样例中存在的嵌套场景需单独迁移，不为旧写法保留隐式兼容。

跨场景生命周期验收使用Java测试组合生成业务场景；SPP不支持Verification测试语法，测试夹具及断言不注册为生产服务。

## 更新场景的合约参与者

包含原子更新的业务Scenario必须在参数中明确声明至少一个Contract参与者。合约应表达本业务的当事人、约定和成交事实，类型检查仅证明声明存在，不能替代业务语义核对。原子服务参数分别声明实际角色与合约，避免以通用上下文隐藏参与者。旧样例需要按新原则迁移，本轮未运行其回归。

生产跨场景组合由前端组织，后端Scenario不能调用Scenario。Petstore读取也拆为独立场景，前端组合展示；Java测试可以在测试代码中组合生成场景。
