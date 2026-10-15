# APP 请求机制与平台版本

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

当前远程调用幂等与界面防重分别定义，规范见[调用幂等与界面防重](app-call-idempotency-and-duplicate-guard.md)。本地调用不登记请求。旧 `idempotency key(...) facts(...)` 解析兼容，但只在界面场景入口作为短期防重生效；新配置使用 `duplicate`。远程更新依据请求方身份和请求方流水号，无需每个服务再罗列业务字段作为幂等键。查询不缓存。

JDBC协议登记及保存结果使用短技术事务，不隐含包住SPP业务事务。确定完成记录按APP期限失效；执行中及待恢复记录不因过期重放。普通事实的修订保障与上述请求机制独立。

version 在 APP 表中声明为平台列，不进入 SPP 或 JSON。platform 定位该元数据；compareVersion 使用查询基线，advanceVersion 原子递增。缺少基线、身份变化、版本竞争均拒绝，不在保存时查询最新版本并覆盖。成功写入刷新基线，事务撤销恢复元数据。模型内版本字段及双目标声明保留旧语法兼容，不作为新的业务建模方式。

旧数据库键、关系和快照没有自动迁移。本轮只生成及编译，不执行防重、并发、故障或重启回归。

APP persist(update)缺省采用可靠快照修订标记的原子条件更新，不必显式定义version列。Petstore已移除手工版本声明；旧语法保留兼容。普通与量子事实分离及读取基线限制见[默认乐观保障](spp-optimistic-participant-facts.md)。
