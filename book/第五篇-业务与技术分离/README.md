# 第五篇 业务与技术分离

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

业务场景已经说明谁参与、怎样计算、何时成交以及失败后怎样处理。接下来讨论技术能力怎样围绕这些业务表达工作：让系统更快、更安全、更可靠，并且能够观察、治理和持续演进。

本篇从分离的收益出发，用同一笔订单的不同技术需求说明缓存、按需数据、安全保护、幂等、防重和运行治理。APP 定义技术策略和服务拦截范围，PHY 绑定 Java 技术服务及实际资源与协议。技术人员可以实现新的 Java 技术服务，通过拦截器接入业务调用，扩展系统能力，而不向 SPP 加入技术调用。第23章介绍接入结构，第27章给出自定义实现示例；各项能力的接入方式仍需要符合其实际接口。

## 本篇目录

- [第23章 业务与技术分离的主要收益](23-separation-benefits.md)
- [第24章 缓存与按需数据提升性能](24-performance-services.md)
- [第25章 加解密指纹与安全服务](25-security-services.md)
- [第26章 幂等防重与可靠执行](26-reliability-services.md)
- [第27章 运行治理与技术演进](27-operations-and-evolution.md)

[返回全书目录](../README.md)
