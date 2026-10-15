# 第15章 四类原子服务

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

S++ 将普通业务原子服务分为 query、check、calculate 和 update。分类表达的是服务职责：获得事实、判断条件、形成候选结果，以及实施变化。完整业务场景通过组合这些职责完成。

## 查询补全事实

普通 query 是内置系统服务，开发者不编写或修改其实现。场景直接调用 `findBuyer` 等服务，系统按 APP 和 PHY 配置取得事实并补全入口参与者，不需要重复声明标准查询服务。服务没有业务返回值，不写成 `buyer = findBuyer()`。查询是否确认了身份也是执行状态的一部分，不能只根据字段非空推断。补全角色所需事实不要求读取整个扮演链的全部属性；可以通过编译期属性使用分析和缓存优化内置查询，具体方法见第二篇第11章。

入口可以省略实例名，默认采用类型名；同类型多个参与者需要显式别名。调用也可以省略参数，但必须按完整类型和集合维度唯一匹配。歧义时应显式选择。

## 校验判断资格

check 读取事实，使用 require 表达业务要求。它不修改参与者。普通 check 失败结束对应词法范围，并不自动保证事务回滚；需要撤销时必须采用受支持的显式控制约定。

把校验放在场景可见的位置，有助于理解业务准入。成交范围则需要在实际量子执行中检查，不能用事前余额读取代替。

## 计算准备结果

calculate 按业务公式修改候选事实。它可以调用其他纯计算，不能调用查询、校验、更新或场景来隐藏技术与业务副作用。

例如单行金额计算：

```spp
atomic calculate priceLine(OrderLine) {
    OrderLine.amount = roundHalfUp(
        OrderLine.unitPrice * OrderLine.quantity, 2);
}
```

这是 [定价源码](../../demos/petstore/src/main/spp/petshop/order/petshop-20-calculations.spp) 中的定义，排版做了换行。

## 更新实施变化

普通 update 同样是内置系统服务，开发者不编写或修改其实现。场景准备完整事实后，直接调用 `insert`、`update`、`delete` 加参与者类型名的标准服务。保存服务接收当前参与者，技术基线由框架保留，不需要业务额外传入 before 快照。计算和校验在场景中单独调用，内置更新内部不执行这些业务逻辑。量子更新进一步描述特殊属性的增减与成交要求。

分类让依赖更容易检查。准备事实、判断资格与候选计算通常可以在成交边界前完成，事务内部聚焦受保护的更新。但具体流程仍需考虑业务与并发约束，不能机械地把四类服务各执行一次就当作完整业务。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](14-take.md) · [下一章](16-calculation-and-rules.md)
