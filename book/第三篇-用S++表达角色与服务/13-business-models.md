# 第13章 Entity Reference Role Contract

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

业务模型中的类型需要回答不同问题。Entity 表示当前域拥有的自然实体，Reference 表示对外域概念的引用，Role 表示参与身份，Contract 表示场景形成的约定。它们帮助我们同时理解业务含义与生命周期归属。

## 自然实体与外域引用

客户域拥有 Person，产品域拥有 Product。商店使用客户与产品事实，相关生命周期仍归原域维护。Reference 明确引用来源，接入方式由应用和物理配置决定。

Reference 可以引用提供方的实体、角色或合约。例如商店引用产品域的 Product，付款引用库存域或其他域提供的业务概念。引用说明事实来自哪里，维护生命周期仍由提供方负责。

## 角色与场景合约

Buyer 表达买家身份，Goods 表达商品的销售身份。ShopOrder 表达下单约定，PaymentAgreement 表达付款约定。订单可以被后续付款、发货和退货场景引用，但引用订单不等于重新执行下单。

下面摘录 Petstore 的一个简短合约：

```spp
Contract WalletFundingAgreement {
    Buyer buyer;
    SettlementAccount source;
    BigDecimal(19, 2) amount;
}
```

参与者与金额共同说明一次钱包充值。合约记录约定，资金增减通过相应服务完成。

## 组成事实与独立参与者

订单明细保留商品、数量与成交单价。订单总额属于订单约定中的组成事实，未必需要为它创建一个独立金额角色。是否形成独立角色，要看是否具有真实参与关系与生命周期。

合约也不能仅因为聚合明细，就被解释为反过来扮演每条明细。扮演关系和组成关系需要分别表达。

## 内部主键与有业务含义的 ID

传统开发者习惯先给实体加一个唯一的 `id`，再用它标识对象和数据库记录。在 S++ 中，不必为了技术定位给业务实体添加这样的字段：编译器会为实体建立业务不可见的内部主键，系统据此维护存储身份。技术上需要唯一定位，不意味着业务模型也必须出现一个 ID。

习惯性添加的 `id`、`customerId` 等字段，容易让读者误以为它们是业务需要的凭证。编译器会检查这类疑似习惯性 ID，并给出警告，提示开发者确认它是否有真实业务含义。

如果这个 ID 确实来自业务需求，可以用 `business` 声明其用途，告诉编译器它是业务事实，从而消除相应警告。例如一个回执号供客户查询办理结果：

```spp
Entity Receipt {
    business("业务办理回执号，供客户查询和核对办理结果") String receiptId;
}
```

这里的 `receiptId` 有客户实际使用的含义。若只是为了给数据库记录分配一个唯一值，系统内部主键已经承接这项责任，无需把它加入 SPP。`business` 用来说明为什么这个看起来像技术 ID 的字段应当留在业务模型中。

所以，`business` 的重点是消除习惯性 ID 带来的歧义。模型评审仍需核对说明是否符合真实需求：谁使用这个编号，在哪项业务中使用，如何凭它办理或核对结果。“内部唯一标识”只说明技术用途，不能据此把技术字段解释成业务凭证。

模型已按会员、商品、购物车、订单等业务功能拆分，完整阅读入口见 [Petstore 源码导读](../../demos/petstore/docs/source-guide.md)。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](12-layers.md) · [下一章](14-take.md)
