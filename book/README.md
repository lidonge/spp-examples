# 面向角色的服务架构

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

[English edition / 英文版](en/README.md)

## S++（SPP）的建模思想、语言机制与工程实践

本书面向熟悉面向对象开发的读者。角色说明参与者以什么身份进入业务，服务说明他们完成什么行为，场景组织协作，合约记录当事人的约定与结果。全书从“服务＝参与者×行为”出发，把角色建模、服务组合与工程实践连成一个体系。

正文用业务例子解释概念，可以顺序阅读。形式化定义、证明、反例与性能推导集中在附录。公式采用普通文本，不依赖 LaTeX 插件；代码片段链接到案例源码。

全书分为七篇、35章及六篇附录。每篇有独立目录和阅读介绍，每章有本篇目录、上一章与下一章导航。

## [第一篇 角色与服务的基本模型](第一篇-角色与服务的基本模型/README.md)

- [第1章 从对象世界到业务活动](第一篇-角色与服务的基本模型/01-business-activities.md)
- [第2章 服务等于参与者乘行为](第一篇-角色与服务的基本模型/02-service-model.md)
- [第3章 角色与业务身份](第一篇-角色与服务的基本模型/03-roles.md)
- [第4章 服务的分类与场景组织](第一篇-角色与服务的基本模型/04-decomposition.md)
- [第5章 量子行为与量子服务](第一篇-角色与服务的基本模型/05-quantum-services.md)
- [第6章 量子服务的叠加交换与纠缠](第一篇-角色与服务的基本模型/06-composition-and-conservation.md)
- [第7章 查询、计算、校验与普通更新的特点](第一篇-角色与服务的基本模型/07-business-service-characteristics.md)
- [第8章 通过角色多态复用服务与场景](第一篇-角色与服务的基本模型/08-polymorphism-and-separation.md)

## [第二篇 服务协作与执行](第二篇-服务协作与执行/README.md)

- [第9章 服务协作与执行顺序](第二篇-服务协作与执行/09-service-coordination.md)
- [第10章 并行执行与服务调用成本](第二篇-服务协作与执行/10-parallelism-and-costs.md)
- [第11章 服务最小颗粒度与部署原则](第二篇-服务协作与执行/11-deployment-granularity.md)

## [第三篇 用 S++ 表达角色与服务](第三篇-用S++表达角色与服务/README.md)

- [第12章 SPP APP PHY 的分层职责](第三篇-用S++表达角色与服务/12-layers.md)
- [第13章 Entity Reference Role Contract](第三篇-用S++表达角色与服务/13-business-models.md)
- [第14章 用 take ... as 声明扮演关系](第三篇-用S++表达角色与服务/14-take.md)
- [第15章 四类原子服务](第三篇-用S++表达角色与服务/15-atomic-services.md)
- [第16章 业务计算规则与集合参与者](第三篇-用S++表达角色与服务/16-calculation-and-rules.md)
- [第17章 场景中的串行并行与合约形成](第三篇-用S++表达角色与服务/17-scenarios.md)

## [第四篇 一致性与执行保障](第四篇-一致性与执行保障/README.md)

- [第18章 业务事实参与者身份与存储归属](第四篇-一致性与执行保障/18-facts-and-storage.md)
- [第19章 事务边界执行计划与部署能力](第四篇-一致性与执行保障/19-transactions.md)
- [第20章 量子属性调用范围与守恒成交](第四篇-一致性与执行保障/20-quantum-execution.md)
- [第21章 回滚反交易冲正与补偿](第四篇-一致性与执行保障/21-recovery.md)
- [第22章 生成链路物理资源与运行配置](第四篇-一致性与执行保障/22-generation-and-runtime.md)

## [第五篇 业务与技术分离](第五篇-业务与技术分离/README.md)

- [第23章 业务与技术分离的主要收益](第五篇-业务与技术分离/23-separation-benefits.md)
- [第24章 缓存与按需数据提升性能](第五篇-业务与技术分离/24-performance-services.md)
- [第25章 加解密指纹与安全服务](第五篇-业务与技术分离/25-security-services.md)
- [第26章 幂等防重与可靠执行](第五篇-业务与技术分离/26-reliability-services.md)
- [第27章 运行治理与技术演进](第五篇-业务与技术分离/27-operations-and-evolution.md)

## [第六篇 完整实践 Petstore](第六篇-完整实践Petstore/README.md)

- [第28章 从需求识别角色行为与服务](第六篇-完整实践Petstore/28-petstore-modeling.md)
- [第29章 零开户充值与入库](第六篇-完整实践Petstore/29-opening-and-transfers.md)
- [第30章 报价下单付款与发货](第六篇-完整实践Petstore/30-order-lifecycle.md)
- [第31章 取消退货预约与失败处置](第六篇-完整实践Petstore/31-returns-and-reservations.md)
- [第32章 技术配置部署与综合验证](第六篇-完整实践Petstore/32-validation-and-performance.md)

## [第七篇 进阶案例与架构方法](第七篇-进阶案例与架构方法/README.md)

- [第33章 银行存款偿还分配与冲正](第七篇-进阶案例与架构方法/33-banking.md)
- [第34章 从现有面向对象系统迁移](第七篇-进阶案例与架构方法/34-migration.md)
- [第35章 架构设计评审与能力边界](第七篇-进阶案例与架构方法/35-design-review.md)

## [附录](附录/README.md)

- [附录 A 服务基本模型与形式化推导](附录/a-service-model.md)
- [附录 B 交换重排与并行的成立条件](附录/b-parallel-conditions.md)
- [附录 C 性能模型与实验方法](附录/c-performance.md)
- [附录 D 量子服务与守恒机制](附录/d-quantum-contracts.md)
- [附录 E 语言与工程参考](附录/e-language-and-build.md)
- [附录 F 资料来源与验证证据](附录/f-sources-and-evidence.md)

## 编辑资料

[待讨论问题](编辑工作/known-issues.md)单独记录尚需作者讨论的定义和契约，不属于书稿阅读顺序。案例源码与验证基线见附录 F。
