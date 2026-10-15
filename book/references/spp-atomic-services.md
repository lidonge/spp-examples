# 原子服务与显式业务校验

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

普通原子服务不可拆分，不允许调用其他服务或场景。calculate 可调用 calculate 组成纯计算，禁止调用 check/query/update/Scenario 及形成循环。场景只调用原子服务，不能调用场景。生产组合在前端；测试组合在 Java 测试目录。

atomic check 根据明确参与者判断资格，允许数学、逻辑、循环和局部变量，不能修改参与者。require(condition, code) 是校验语句，失败形成校验结果；SPP 不用技术异常作业务条件。场景缺省 check 失败结束所在 block，不自动回滚；checkXXX{...}; 只跳过自己的内容；checkXXX,breakTransction; 失败撤销当前事务。

atomic calculate 计算事实和创建明细，不能使用 require 或隐藏校验。roundHalfUp 等为内置数学函数，显式舍入是业务约定。

```spp
atomic check checkPaymentEligibility(Buyer customer, ShopOrder order) {
    require(order.status == OrderStatus.UNPAID, "ORDER_NOT_PAYABLE");
    require(customer.wallet >= order.total, "INSUFFICIENT_FUNDS");
}
atomic calculate preparePayment(ShopOrder order, PaymentAgreement agreement) {
    agreement.paymentAmount = order.total;
    order.status = OrderStatus.PAID;
}
```

多个共享 check 在场景显式排列。命名校验组复用语法尚未确认，不能让 check 互调冒充组合。技术版本由 APP 维护，不是付款业务资格。

量子更新与普通原子不同：定义内 check(expression) 校验变化后的量子属性，可使用合约阈值，失败撤销绑定事务；非量子资格仍在场景检查。量子服务要求显式事务，普通 check 不要求量子执行。APP 守恒资源可包含未变化的属性；单动作可以只改变部分资源，不能改资源外的量子属性。

仓储、部署及量子物理实现由 APP/PHY 绑定，通用生成代码不构成业务服务互调。未使用参与者告警，业务含义仍需人工审查。Petstore 本轮只生成并编译生产和测试，不运行回归。
