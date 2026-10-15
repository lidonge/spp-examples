# APP 事务内普通更新自动并发

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

对应《查询、计算、校验与普通更新的特点》中“普通更新在量子服务之后并发执行”。APP 选择调度策略，SPP 继续只表达参与者、业务顺序与事务边界。

```app
application petstore {
    environment develop {
        deploy customer; deploy product; deploy inventory; deploy petshop;
        transactions {
            mode: LOCAL;
            resource: shopRecordsResource;
            ordinaryUpdates: PARALLEL;
        }
    }
}
```

独立域也可以在已有 transactions 配置中增加 ordinaryUpdates。可选值 SERIAL、PARALLEL，缺省 SERIAL；部署环境的显式选择覆盖域级缺省。环境可以只声明 `transactions { ordinaryUpdates: PARALLEL; }`，继续推导既有事务模式和资源。

编译器标识没有业务实现的普通更新，自动并发连续、准备完整的更新段。量子更新在同一准备段内先完成；计算、校验、查询、条件分支、显式执行组与独立事务保持业务顺序，形成调度屏障，不能为了并发跨越这些步骤。两个更新直接操作同一参与者实例时保持先后顺序。自定义更新中仍有业务计算的实现不会被自动并发。

并发前先分配 APP 自动凭证编号，防止保存父合约时子明细编号尚未形成。量子成交回填结束后才启动普通更新。全部任务完成后，原协调器统一提交；失败时等待其他任务结束，再回滚共同事务或恢复已经成交的 Saga 节点，不能在后台任务仍写入时开始回滚。

任务继承原事务、参与者确认、读取修订、调用身份、审计流水与 JDBC 作用域，不能因线程切换变成独立 autocommit。共享单一 JDBC 连接时，连接访问串行保护，仍只有一次共同提交；这不承诺单连接 SQL 可以同时执行。不同独立资源/远程节点可以并发等待。

第一版不改变事务传播能力矩阵，不使原本不支持的分布式协调模式变得可用。量子阶段仍由所选实现负责成交，业务补偿仍由业务定义。SPP 显式 parallel 的既有约束保持原样。

实施路径：APP 解析与环境继承 → 编译器生成执行标识、准备动作和事务策略 → 运行时并发批次、上下文传递与汇合恢复 → 开启 Petstore 演示配置 → 用屏障验证真实并发、阶段顺序、失败汇合及数据库共同回滚，并执行 Petstore 回归。

与传统手写线程池相比，业务无需管理 Future、事务线程绑定与失败等待，调度策略可以按环境切换；代价是执行器及上下文传递开销。依赖步骤不会自动并发，共享单连接的数据库吞吐也不因开启配置而提升。

## 验证记录

2026-10-12 执行 `mvn -fae -pl petstore-demo -am test -Dspp.environment=develop`，BUILD SUCCESS：语言 349、运行时 600、生成器 105、Petstore 35，共 1,089 个测试，失败/错误/跳过均为 0。

新增语言用例验证 PARALLEL 开启、SERIAL 缺省、非法/重复配置、环境覆盖与仅指定调度的环境语法。新增运行时 9 个用例验证真实重叠执行、共享事务上下文、失败等待全部任务再回滚、同一入口参与者顺序、计算屏障、LOCAL 量子优先、代理量子模式与优先级、条件事务体的并发入组、JDBC 共同回滚及 Saga 同伴成交后的补偿。

Petstore develop 已显式开启此策略。全部既有场景测试通过，包括编号形成、库存预占、付款、订单快照、事务回滚、未知提交及后续查询；故障注入计划随任务继承到工作线程，因此验证没有绕开并发写入的故障路径。testing 仍使用缺省 SERIAL；这轮没有运行多进程 testing 验收。
