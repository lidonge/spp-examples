# 量子调用上下限与自动成交校验

上下限是量子服务调用的专用语法，不是服务参数、合约包装字段或服务体中的手写check。服务只声明数值转移：

```spp
quantum update payOrderFunds(Buyer customer, Merchant merchant, PaymentAgreement agreement) {
    customer.wallet -= agreement.paymentAmount;
    merchant.cash += agreement.paymentAmount;
}
```

调用者在显式事务中约定闭区间：

```spp
payOrderFunds(customer, merchant, agreement) bounds {
    customer.wallet: [0, null];
    merchant.cash: [0, null];
};
```

区间两端分别可为数字表达式或null。下限null表示不做下限检查，上限null表示不做上限检查，两端null表示不做区间检查；省略bounds的兼容调用不添加范围限制，量子守恒及事务一致性仍然生效。可透支账户调用者可使用负的下限或根据授信事实计算下限，不需要修改共用量子服务。当前Petstore只演示普通账户，下限0由调用场景明确选择；没有新增授信审批或透支业务。

编译器核对bounds只用于显式事务中的量子更新，目标是本次实际传入参与者的量子属性；重复属性、非量子属性及非数字边界被拒绝。两端在调用前确定，随量子调用传到成交提供方；由其具体实现约束本次成交，越界拒绝并触发绑定事务撤销，不走普通check的跳过block语义。集合边界对本次集合的每个成员分别传递和实施，不用汇总掩盖单个商品越界。

库存域只定义逐商品预占、出库、释放、退回的加减。销售场景为stock.available/reserved/sold声明范围，APP按域调用提供方；提供方负责实际守恒记录，消费入口不重复记账。所有服务和场景仍然只有参与者入口，业务无异常控制语法。

PHY选择BigInteger时，生成模型使用通用精确整数反序列化器，拒绝非整数输入，禁止静默截断。类型输入问题属于APP/PHY；SPP只描述正整数数量等业务条件。

本轮仅生成、编译与静态审查，不执行回归。负边界、空边界、成交越界、逐元素守恒和跨域共同撤销的运行行为须在恢复回归后验证。

数据库量子版已将范围放入成交写入的SQL条件；不同量子版本可采用不同机制，不能在调用结束后补查。非JDBC版本是否可用取决于实现能力，未接入动态范围的版本明确拒绝，详见[量子调用范围](../../../book/references/quantum-call-bounds.md)。
