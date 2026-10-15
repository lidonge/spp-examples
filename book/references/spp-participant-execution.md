# 参与者驱动的服务执行

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

本文件记录本轮语言约定、实施路径、已实现范围和编译证据。

## 入口与身份

服务及场景入口只声明参与者，不能传入独立基本属性。实例名可选，省略时以角色名作为默认实例名，例如 Buyer 等价于 Buyer Buyer。传统显式实例名仍允许，例如 Customer source、Customer target。

入口实例在一次执行中保持不变，服务只修改其内部事实。SPP不提供业务返回值，不允许将查询结果赋值给参与者。APP/PHY在实现查询时补全原实例。原子服务可以创建参与者内部的新明细；不能替换已有入口实例。

单个参与者与集合是不同类型：`Goods` 与 `Goods[]` 不构成歧义。入口可以直接声明 `(Goods, Goods[])`，表达式分别用 `Goods` 与 `Goods[]`，例如 `for (Goods item : Goods[])`、`Goods[] = filtered;`。生成 Java 时才使用 `GoodsArray` 等合法标识符；SPP 不需要出现该名字。相同完整类型有多个参与者才保留显式实例名。

无参数调用按参与者类型和集合维度唯一匹配；缺失或歧义时报错，允许显式参数选择。计算调用也遵循此规则。查询确认状态属于语言内部事实，if(Buyer)表示身份已确认，identify(Buyer)是内置确认检查；不以 null 表示未找到。查询技术失败由APP/PHY处理，不等同于未找到。

## 校验与控制范围

普通 check 成功继续下一句，失败结束当前词法block。checkXXX { ... }; 或 checkXXX(param) { ... }; 只有成功才执行所包围范围，失败跳过该范围后继续。identify支持相同控制方式。普通check缺省不触发回滚，包括所在block是事务块的情况。

显式写 `checkXXX,breakTransction;` 或 `checkXXX(Buyer),breakTransction;`：成功继续执行，失败撤销当前事务并结束该事务的执行。`breakTransction` 保留用户约定的拼写，不是独立语句，也不在业务层引入异常。`identify(Buyer),breakTransction;` 使用相同规则。事务之外使用、用于非check服务、与guard块组合均为编译错误。

“当前事务”遵循传播约定：`REQUIRED` 加入既有事务，失败撤销共享事务；`NESTED` 撤销嵌套范围；`REQUIRES_NEW` 撤销当前独立事务。APP/PHY必须先完成撤销，再转换业务失败结果；技术撤销失败仍作为技术故障处理。Saga已提交的节点无法获得本地物理回滚，不能将补偿成功伪称回滚；不支持确定撤销的实现应明确拒绝该约定。

```spp
transaction {
    checkBuyer;                  // 失败结束当前block，缺省不回滚
    checkBalance,breakTransction; // 失败显式回滚当前事务
    debit;
}
```

SPP不存在异常语法，移除try/catch/throw。技术异常在APP/PHY处理，可审计、终止执行和触发事务回滚；不能成为SPP业务分支条件。

## 量子服务

量子更新服务在SPP定义加减，调用者以bounds声明量子属性成交范围。上下限在调用前确定，null禁用对应方向，由量子成交实现逐参与者实施范围控制；越界撤销绑定事务。账户状态等非量子资格在调用前由场景显式check。服务内check仅兼容旧定义，新示例不用它写死上下限。APP/PHY负责一致执行与撤销，详见[量子调用范围](quantum-call-bounds.md)。

## 计算组合

calculate保持纯计算，不调用check、query、update、quantum或Scenario；可以调用其他calculate组合复杂计算。参与者共享结果，不返回业务数据。禁止循环调用图以避免未约定递归和无法终止的自动绑定。

## 实施路径

1. 修改入口、无参数调用、guard检查、identify、量子约束、计算调用语法；删除业务返回值与异常语法。
2. 完善模型、唯一绑定、入口类型、调用图及量子约束检查；生成稳定参与者及校验范围控制。
3. 通用运行时支持原地查询补全、身份确认、业务校验结果和量子约束撤销；不手写demo业务Java。
4. Petstore使用具体Buyer/Seller角色，改为无返回查询和明确参与者事实；展示默认命名、自动绑定、guard及计算组合。
5. 迁移前端和Java验收输入，生成并编译生产/测试源码，按当前要求不执行回归、不提交上传。

其他旧样例不在本轮业务源码迁移范围；新语义的兼容缺口必须明确记录，不能保留语义相反的业务返回/异常写法作为隐式兼容。

## 本轮实现和编译证据

已加入 `breakTransction` 的解析、事务内使用约束及生成控制，普通check使用词法block结束而非业务异常。APP执行转换业务失败时必须置于物理提交/撤销范围之外，避免吞掉撤销信号后误提交。guard失败不作为普通block失败；已结束block的校验结果可以通过APP接口说明，APP幂等重放保留该结果。

最小SPP/APP示例已生成并编译Java，覆盖默认角色实例名、唯一自动绑定、显式参与者、guard、普通check、显式撤销、identify及传播关键字。框架/编译器/生成器生产和测试源码编译通过；未执行回归。这些证据不代表真实资源上的撤销已做运行验证。

Petstore 已完成 Buyer/Seller 角色迁移、原地查询、显式集合参与者、默认角色命名、无参数唯一绑定、identify、check控制范围及复合计算迁移。查询补全才确认参与者，普通事实复制不会自动确认；APP幂等重放保留查询确认和校验结果。生成目录及类目录隔离后，完整生产和测试源码编译通过，未运行测试。

显式撤销后的后续控制流尚待讨论。当前实现按事务传播范围退出：共享 REQUIRED 撤销传播到场景入口；嵌套 NESTED 或独立 REQUIRES_NEW 完成局部撤销后继续外层。此项是暂定实现，不能视为用户已经确认的最终语言规则。

量子服务入口要求处于显式源码事务且由事务管理器执行，拒绝绕过事务直接更新；量子约束在更新后、提交前检查。技术异常及撤销信号只存在于生成框架内部，SPP没有业务异常语法。

远程查询也需补全调用方原实例。单参与者 objectRepositoryRemote 查询使用同样的原地补全与确认规则；HTTP void 服务的物理响应必须包含 participants（单参与者对象或按入口顺序的数组），可提供 confirmations（按入口顺序的确认路径映射数组）。确认状态不能从普通数据响应中推断。没有该物理协议的旧HTTP服务不能静默忽略响应，需要在APP/PHY接入层转换。

当前实现只为AT/QUANTUM的事务内校验提供生成支持，其他物理策略需要先补齐其执行能力，不能把Saga补偿当作确定回滚。并行组内裸check结束整个组的顺序含义尚未约定，当前编译器要求将其放入串行组或使用guard；该缺口不能用只结束某个并行任务来隐式替代。

## 完成项核对

| 已确认约定 | 实现位置与编译证据 |
| --- | --- |
| 入口仅参与者、默认角色名、显式别名、唯一自动绑定 | 语法与SppDomain绑定检查；Petstore读取场景默认调用完成生成编译 |
| 无业务返回、入口不替换、查询确认、if/identify | 原地仓储补全、ParticipantFacts与ParticipantIdentity；Petstore所有查询迁移 |
| 普通check词法结束、guard局部跳过、显式撤销 | 标签范围生成、BusinessChecks、SourceTransactionBoundary；参数guard与传播示例生成编译 |
| SPP没有try/catch/throw | 删除语法及监听处理；框架内部技术故障仍由APP/PHY处理 |
| 量子成交约束与撤销绑定 | QuantumConstraintProvider提交前校验；Petstore库存及资金量子约束完成编译 |
| 纯计算组合、禁止其他调用及递归 | calculate调用类型与调用图检查；quoteOrder/priceLine完成生成编译 |
| 只生成和编译，不运行回归 | Petstore644份生产源及3个测试类编译；lang/appframe/generator生产和测试源编译；无APP头示例生成及javac编译 |

最终完整构建：`mvn -pl :petstore-demo -am package -DskipTests`，`BUILD SUCCESS`；日志 `/tmp/spp-participant-petstore-final-build.log`。未提交或上传。编译不能替代实际资源上的事务、并发和远程协议运行验证；上文暂定控制流及能力缺口保留在设计中。

## 保存单个参与者

同一参与者的修改前后状态不是两个业务角色。保存服务只接收当前参与者，例如 `atomic update saveCustomer(Buyer);`；业务合约不得为了持久化版本检查或技术回滚携带before快照。APP可声明 `compareVersion(platform(0, Buyer.version)) advanceVersion`，框架以查询时自动记录的原实例事实为比较基线，持久化使用当前事实。缺少查询基线时拒绝版本保护写入，不能临时读取最新数据库版本后覆盖并发结果。已有双目标APP版本声明保留兼容，但Petstore不再以业务参与者表达技术快照。

实施顺序：完善APP单目标声明和编译检查、通用查询基线及事务撤销支持；迁移五类保存服务和全部调用；删除合约技术快照及复制服务；生成并编译生产及测试源码，不运行回归。

本次单参与者保存迁移已完成；从空Petstore生成目录、生产/测试类目录构建成功，生成624份生产Java并编译3个测试类，未执行测试。日志 `/tmp/spp-petstore-single-participant-fresh-build.log`。当前生成目录不含被删除的load*Facts服务。订单价格等业务快照继续保留；变化仅移走持久化技术快照。

## 业务模型与集合入口

实体/角色/场景合约的当前规范见 [业务模型边界](spp-business-model-boundary.md)。业务关系直接包含参与者；技术主键、外键投影及版本在 APP/PHY。Goods[]/ShopOrder[] 等一维参与者集合入口生成可变 List，更新内容保留容器；不再用投影合约包装集合。直接 Java 调用须传可变集合，optional/锁定查询仍限制为标量。

以自身业务身份逐项查询的集合支持optional和锁定；按身份排序逐行锁定，全部成员确认后才确认集合，跨域补全同步确认状态。筛选集合查询不支持锁定/optional。量子记录逐成员以完整身份分组，不允许其他商品的变化抵消某商品的不守恒。

量子属性业务上统一归逻辑量子域，真实一致性机制由APP配置、PHY资源实现；不是强制独立物理服务。事务内读取和混合参与者保护见[事务读取规则](spp-transaction-reads.md)。


## 场景内置处理结果与事务 fail

场景可写 `transaction { ... } fail { ... }`，通过无需声明、无需入口参数的 ResultInfo 读取 FailureInfo。单合约默认关联，多个合约用 fail(目标合约) 选择；原子服务不可直接使用系统结果参与者。fail 是事务恢复后的业务块，不是 SPP try/catch。详细字段、恢复结果及首版嵌套限制见[失败处理](spp-transaction-failure-handling.md)。
