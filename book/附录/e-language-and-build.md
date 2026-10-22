# 附录 E 语言与工程参考

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

本附录提供初稿采用的语言约定和实验命令入口。它是阅读辅助，完整配置仍以对应模块源码和运行说明为准。命令在仓库根目录执行。

## 概念速查

| 概念 | 职责 |
| --- | --- |
| Entity | 当前域拥有的自然实体 |
| Reference | 明确来源的外域实体、角色或合约引用 |
| Role | 业务参与身份及角色事实 |
| Contract | 场景的当事人、约定与结果 |
| take ... as | 声明单方、联合或再次扮演关系 |
| mapsame | 显式启用满足条件的同名属性映射，默认不启用 |
| takeall | 明确继承扮演者属性，并生成相应映射 |
| business | 声明疑似技术 ID 的真实业务含义，消除习惯性 ID 警告 |
| query | 补全参与者并承接身份确认 |
| check | 判断业务条件，不修改参与者 |
| calculate | 形成候选事实，可组合纯计算 |
| update | 实施明确变化，由应用与资源兑现 |
| quantum update | 定义量子增减与成交关系 |
| Scenario | 组织完整业务活动 |
| transaction ... fail | 事务执行与技术恢复后，办理明确的失败业务处置 |
| ResultInfo | 场景内置系统参与者，提供执行结果与失败恢复事实，不作为原子服务参数 |

服务入口采用参与者或参与者集合，实例名可以省略。无参数调用需要唯一类型绑定。没有业务返回值，标量入口实例保持稳定；集合内容可以更新，生成 Java 采用可变容器。

普通 check 失败结束词法范围，缺省不触发回滚。显式撤销采用仓库约定的 `breakTransction` 拼写，支持条件和暂定控制流见参与者执行规范。正文没有将这种控制方式当成所有事务模式的通用能力。

## 示例后端的能力范围

下面列的是案例源码基线中的具体能力，不用于重新定义服务、角色或事务概念：

| 项目 | 使用条件 |
| --- | --- |
| LOCAL | 相关域同 JVM，并使用可核对的共同数据库、schema 和连接资源 |
| REQUIRED | 复用已有执行与提交上下文 |
| REQUIRES_NEW | 仅受支持的同质外层及本地资源组合；独立结果另行处理 |
| NESTED | 示例后端不支持，构建拒绝 |
| parallel 内裸 check | 停止范围有限制，使用受支持串行或 guard 表达 |
| 增强 for | 按集合顺序执行，不自动变为并行集合计算 |
| calculate 调用 | 可以组合纯计算，禁止循环调用图和技术副作用 |
| fail 块 | 当前支持串行场景的外层事务；多个合约用 fail(目标合约) 选择；嵌套及并行分支内拒绝 |
| 远程事务与量子协议 | 需要实际协调能力及恢复证据，缺失时拒绝配置 |

这些能力的具体判定见参与者执行、事务存储和环境规范。书中的原理推导说明某种组合何时合理，后端还需真正提供对应的运行能力。

## 各类业务服务的实现依据

第一篇第7章的调用、流程与执行特点，可沿以下入口核对：

| 特点 | 实现或示例入口 |
| --- | --- |
| 独立查询并发，完成后再使用事实 | [下单场景](../../demos/petstore/src/main/spp/petshop/order/petshop-scene-placeShopOrder.spp)、[付款场景](../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-payShopOrder.spp) |
| 查询原地补全与身份确认 | [参与者查询绑定](../references/participant-query-binding.md)、[参与者执行](../references/spp-participant-execution.md) |
| 普通查询与普通更新均为内置服务，开发者不修改实现；场景组织调用、计算与校验 | [内置 CRUD 规范](../references/implicit-participant-crud.md) |
| 普通原子服务不允许调用其他服务，计算调用图禁止循环 | SppDomain 校验 (maintainer reference: `../../lang/src/main/java/com/servpp/lang/models/SppDomain.java`)中的 `validateBusinessCalculations`、`validateCalculationCycles` |
| 计算只调用计算，校验不修改参与者，计算不能使用 require | 业务计算校验器 (maintainer reference: `../../lang/src/main/java/com/servpp/lang/models/app/expr/BusinessCalculationValidator.java`) |
| 订单报价复用明细计算 | [Petstore 定价服务](../../demos/petstore/src/main/spp/petshop/order/petshop-20-calculations.spp)中的 `quoteOrder` 与 `priceLine` |
| 校验控制词法范围、局部 guard 与显式撤销 | [参与者执行规范](../references/spp-participant-execution.md)、[原子服务规范](../references/spp-atomic-services.md) |
| 事务恢复后记录业务拒绝 | [预约场景](../../demos/petstore/src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp)、[失败处理与系统结果](../references/spp-transaction-failure-handling.md) |
| 计算与校验可以生成本地实现 | SppService (maintainer reference: `../../lang/src/main/java/com/servpp/lang/models/SppService.java`)中的 `isLocalService`、生成器 (maintainer reference: `../../generator/src/main/java/com/servpp/generator/openapi/MustacheClassWriter.java`)、[Petstore APP](../../demos/petstore/src/main/spp/petshop/petshop.app) |

查询并发与本地顺序执行是根据职责和依赖选择的安排，不是由服务类别自动获得的调度效果。本地执行也不等于不能处理并发请求。第一篇说明常见业务的安排，第二篇进一步讨论实际成本与依赖。

## 构建与测试

```bash
mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=develop
mvn -pl :petstore-demo -am test-compile -DskipTests -Dspp.environment=testing
mvn -pl :petstore-demo -am test -Dtest=PetstoreScenarioTest -Dsurefire.failIfNoSpecifiedTests=false
```

前两项分别构建、编译，均跳过测试执行；第三项实际执行所选测试。模块回归不能仅从 package 成功推断。公共联合回归可沿最新 Petstore 验收记录中的命令执行。

## 本地网页

```bash
SPP_PETSTORE_JDBC_URL='jdbc:h2:file:/tmp/spp-book-develop' \
  ./demos/petstore/run-demo.sh web
```

默认端口为 8086。已有构建可设置 `SPP_DEMO_SKIP_BUILD=1`，但必须确保产物对应当前环境。固定文件路径会保留前次实验数据，需要根据实验轮次选择路径。

## 三进程 testing

先构建 testing 产物，在三个终端设置同一调用凭据和实验资源。以下变量块应在三个终端分别执行，凭据占位值替换为本次实验值：

```bash
export SPP_ENVIRONMENT=testing
export SPP_DEMO_SKIP_BUILD=1
export SPP_DOMAIN_RPC_TOKEN='replace-with-session-token'
export SPP_TESTING_CUSTOMER_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-customer'
export SPP_TESTING_PRODUCT_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-product'
export SPP_TESTING_SHOP_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-shop'
export SPP_TESTING_LEDGER_JDBC_URL='jdbc:h2:file:/tmp/spp-book-testing-ledger'
```

随后先启动提供方，确认就绪后启动商店应用：

```bash
# 终端一，默认端口 8087
./demos/petstore/run-demo.sh web customerService
```

```bash
# 终端二，默认端口 8088
./demos/petstore/run-demo.sh web productService
```

```bash
# 终端三，默认端口 8086
./demos/petstore/run-demo.sh web petstore
```

跨主机需要修改端点和量子资源，确保所有参与方使用同一个真实量子系统。文件型 H2 示例不能仅通过复制路径字符串变为跨主机共享数据库。

## 数值与输出

SPP 的数字规格提供默认提示，PHY 全局替换与字段覆盖选择实际表示，字段覆盖优先。容量检查不能代替业务舍入。生成产物在 target，业务源码在 `src/main/spp`。

阅读入口：[运行说明](../../demos/petstore/docs/running-demo.md)、[启动脚本](../../demos/petstore/run-demo.sh)、[参与者执行](../references/spp-participant-execution.md)、[数值语义](../references/numeric-physical-semantics.md)与[环境配置](../references/deployment-environments-and-physical-defaults.md)。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](d-quantum-contracts.md) · [下一章](f-sources-and-evidence.md)
