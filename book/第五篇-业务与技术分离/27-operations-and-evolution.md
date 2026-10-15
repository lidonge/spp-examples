# 第27章 运行治理与技术演进

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

业务模型正确以后，系统还需要在负载变化、依赖故障和环境迁移中持续提供能力。APP 可以组织追踪、限流、隔离和技术恢复，PHY 提供实际部署、资源与监测设施。这些能力围绕业务服务工作，使问题可以发现、定位和处理。

## 追踪与指标帮助定位问题

例如，订单场景变慢，可能是产品域查询耗时，也可能是库存成交等待或订单保存发生冲突。只记录“下单失败”，无法判断应该优化哪一项能力。

技术追踪可以关联场景、跨域调用、事务阶段和恢复动作；指标可以统计耗时、错误率、缓存命中率、普通更新冲突与待恢复请求数量。量子阶段已成交、普通阶段失败和反交易尚未确认，也应能在轨迹中区分。

业务合约用于回答买了什么、付了多少、目前如何办理；技术轨迹用于回答调用经过哪里、哪个阶段失败以及恢复进行到哪一步。两类信息通过标识关联，页面业务状态不需要混入数据库连接或线程细节。

## 用 Java 增加一个慢调用观察服务

假设已有日志之外，还希望单独记录超过 200 毫秒的调用。可以新增 Java 技术服务，而不修改任何业务场景。以下示例使用当前 TechnicalService (maintainer reference: `../../appframe/src/main/java/free/servpp/service/technical/TechnicalService.java`) 与 TechnicalInvocation (maintainer reference: `../../appframe/src/main/java/free/servpp/service/technical/TechnicalInvocation.java`) 接口：

```java
package example.technical;

import java.util.Map;
import java.util.logging.Logger;
import free.servpp.service.technical.TechnicalInvocation;
import free.servpp.service.technical.TechnicalService;

public final class SlowCallObserver implements TechnicalService {
    private long thresholdNanos;
    private Logger logger;

    public SlowCallObserver() {}

    @Override
    public void configure(Map<String, String> config) {
        long millis = Long.parseLong(config.getOrDefault("thresholdMillis", "200"));
        if (millis < 0) throw new IllegalArgumentException("Negative threshold");
        thresholdNanos = Math.multiplyExact(millis, 1_000_000L);
        logger = Logger.getLogger(config.getOrDefault("logger", "spp.slow"));
    }

    @Override
    public void handle(TechnicalInvocation event) {
        if (event.elapsedNanos() > thresholdNanos) {
            logger.warning("service=" + event.serviceName()
                + " phase=" + event.phase()
                + " elapsedMicros=" + event.elapsedNanos() / 1_000);
        }
    }
}
```

实现类需要公共无参构造器。注册时调用 `configure`，执行时调用 `handle`；实例可以被并发使用，因此不要把某一次请求的开始时间或身份放进共享成员。这里阈值与日志器在初始化后不再修改，每次调用的数据来自当前事件。

将类放入应用运行时类路径之后，APP 可以只观察场景：

```app
technical services { slowCall; }
intercept scenarios {
    after: slowCall;
    failure: slowCall;
}
```

PHY 指定实现与参数：

```phy
phy {
    technical service slowCall {
        implementation: "example.technical.SlowCallObserver";
        config thresholdMillis = "200";
        config logger = "spp.slow";
    }
}
```

慢调用观察只是一个起点。相同接入结构可以连接指标库、调用链系统或技术告警设施；若加入基于调用元信息的访问控制或限流，可以选择 `before`。线程池隔离、远程取消、报文转换等能力还需要相应运行时或通信适配，不能只靠观察事件完成。

## 明确拦截范围与错误含义

全服务匹配只作用于声明所在业务域。商店域消费代理与产品域提供方是两次独立调用，要观察产品域内部服务，就在产品域配置技术绑定。配置按声明与阶段列表顺序执行，同一服务、阶段和技术服务重复匹配会被编译器拒绝。

`before` 可以阻止调用；`after` 失败会留下技术诊断并继续其他观察服务；`failure` 处理失败会附加到原错误并继续其他观察服务，不替换原错误。这样，日志设施故障不会在正常返回之后把原业务结果改写成新失败。

方法返回与事务提交也应分开观察。量子服务方法返回时，外层事务可能还没有结算；一个场景有多笔顺序事务时，一次场景 `after` 更不能替代每笔事务的提交证据。当前接口还没有独立提交回调，成交与恢复的判断需要相应执行记录。

技术服务本身不注册为 SPP 原子服务，因而不会被全服务匹配再次拦截成递归调用。这也保持了职责关系：业务服务完成业务，技术服务围绕调用提供设施。

## 限流与隔离保护运行资源

某个外部目录服务响应变慢，如果所有请求都长期等待它，连接和工作线程可能被占满，其他业务也受到影响。技术层可以为不同依赖设置容量限制、等待期限和独立资源池，减少故障传播。

限流控制单位时间的受理量，隔离控制不同调用使用的资源，熔断则在持续故障时暂时停止反复访问不可用依赖。这些策略可以提高系统应对故障和负载的能力，但不能把依赖不可用解释为商品不存在，也不能宣称它们自动保证整笔业务成功。

已经开始的更新还要确认真实结果。调用超时后释放页面等待，不意味着后台更新已经停止；技术层必须将执行状态与结果确认纳入协议。响应时间管理与交易恢复要配合，不能分别作出冲突的判断。

## 降级需要保持业务含义

商品推荐不可用时，页面可以省略推荐；展示图片读取失败时，可以显示占位图。此类调整可以由接口与展示适配承接。

但价格来源不可用时，不能随意改用旧价格完成成交；支付依赖故障时，也不能先把订单标为已支付。哪些内容可以省略、哪些事实允许使用缓存、哪些办理必须暂停，需要有明确的业务与接口约定。技术层选择降级方法，业务层确认允许的结果范围。

消息或异步执行也有同样边界。发送通知可以异步，但“订单成功”的承诺不能在库存与付款尚未确认时悄悄成立。若业务本来就是先受理、后办理，应在 SPP 中明确阶段和合约状态，技术队列负责运输与执行。

## 数据转换与环境适配促进复用

不同外部系统可能用不同字段名、报文格式和数值表示。技术适配负责把它们转换为约定的业务事实，再交给角色查询、计算或更新。日期格式、序列化、传输压缩等能力也可以集中维护。

例如，产品域使用另一个接口协议，商店仍通过商品角色取得事实；展示文案需要多种语言，常量与语言资源可以由相应机制承接。币种转换、成交舍入等会改变业务金额的规则，则不能仅当作报文格式转换处理。

开发、测试和生产环境的服务地址、数据源、缓存与密钥设施由 PHY 落实。技术能力具备以后，运维可以按环境配置资源；能力尚未实现时，仅增加配置名称并不能使其生效。

## 让技术演进具有可核对的结果

每项技术改进都需要明确目标与验证范围。增加缓存，应核对读取时效与失效行为；修改防重存储，应核对并发请求和重启恢复；调整事务部署，应核对提交、反交易与结果不明的处理；增加安全适配，应核对身份来源与输出保护。

这些验证围绕技术能力的约定展开，业务验证则继续检查计算、资格和合约结果。分层使技术升级与业务变化各有清楚的评审范围，双方通过共同约定确认系统能力。下一篇以 Petstore 串联角色、服务、场景以及相应技术接入，观察这些原则如何用于完整业务。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](26-reliability-services.md) · [下一章](../第六篇-完整实践Petstore/28-petstore-modeling.md)
