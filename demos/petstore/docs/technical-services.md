# 技术服务样例：调用日志与耗时

需求：不在 SPP 中添加日志调用，不增加业务参与者，统一观察商店域场景及原子服务的技术调用情况，包括标准 CRUD 与量子服务。

[APP](../src/main/spp/petshop/technical-services.app) 声明 invocationTrace，使用 `intercept services` 匹配商店域全部服务，在 before、after、failure 三个阶段执行。[PHY](../src/main/spp/petshop/technical-services.phy) 指定通用 InvocationTraceService 和日志名称 spp.petstore.invocations。实现位于框架，不依赖任何 Petstore 属性或业务状态。

启动中文网页后浏览商品、预约或下单即可看到日志，例如：

```text
phase=BEFORE service=petshop.reserveShopPet kind=SCENARIO ...
phase=BEFORE service=petshop.findBuyer kind=ATOMIC_QUERY ...
phase=AFTER service=petshop.findBuyer ... elapsedMicros=...
phase=AFTER service=petshop.reserveShopPet ... elapsedMicros=...
```

日志只记录服务、调用类别、受信任技术头、耗时和校验结果，不打印客户或订单内容。传播的技术错误使用 FAILURE；库存不足经过场景 fail 处理后正常返回，则场景记录 AFTER，而失败的量子成交仍按实际传播位置记录。量子服务方法返回时，量子结算可能尚待外层事务进行，不能把其 AFTER 当成量子成交成功。

商店域消费代理和其他域提供方是各自独立的服务调用，APP 配置只作用于声明所在域。需要产品域日志时在产品域配置同样规则，无须修改产品的 SPP。远程幂等重放仍会记录场景入口日志，但不重复执行业务原子服务。

与手写日志相比，业务源码不变、默认 CRUD 也被覆盖；代价是固定三个阶段及不暴露参与者的技术协议无法表达任意 AOP 切点。详细语义、错误策略和实施路径见[APP 技术服务](../../../book/references/app-technical-services.md)。

## 验证记录

2026-10-13，develop 全量回归通过 1,123 项测试，其中 Petstore 39 项。技术样例三个验收分别验证：场景与类型调用的默认 findBuyer 各一组 BEFORE/AFTER；库存不足经过 fail 处置后场景正常 AFTER，幂等重放不再次预占；findBuyer 技术故障同时记录原子服务和场景 FAILURE，保留原错误。所有业务 Java 仍从原 SPP 生成，本轮仅新增 APP/PHY 技术绑定及框架通用能力。
