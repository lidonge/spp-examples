# 第29章 零开户充值与入库

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

购买之前，需要有买家、商店、商品、钱包和库存。本章把“建立参与资格”和“转入资金或货物”分开：开户不赠送余额，开店不凭空增加库存。这样，后续每次非零变化都能找到对应来源。

## 开户准备身份与零事实

新钱包为零，新商品库存的可售、预留与已售数量为零。结算来源与供应来源也从零开始。建立零事实不产生非零交易流水；开户重试不得把已经充值的钱包重新写成零。

这包含两类工作：业务上建立买家与商店身份，技术上准备普通记录和量子地址。分库零记录的建立通过持久技术待办确认与恢复，不要求业务人员在每个开户场景中编写数据库重试。第四篇第18章说明了这一生命周期，第五篇第26章说明了持久恢复的作用。

如果开户之后还没有充值，买家身份已经存在，钱包仍为零。这是可以直接解释的业务状态。

## 充值展示一对守恒属性

充值 500 元，Buyer.wallet 增加 500，SettlementAccount.balance 减少 500。假设双方之前都为零，成交后分别为 500 和 −500，合计仍为零。

负来源是演示边界中的对侧记载。实际支付接入还需要确认资金来源、支付结果与结算资格，不能把允许负来源理解成允许无条件赠送资金。

[充值源码](../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-fundShopWallet.spp) 中的量子定义直接表达这对属性：

```spp
quantum update transferWalletFunds(Buyer, SettlementAccount, WalletFundingAgreement) {
    SettlementAccount.balance -= WalletFundingAgreement.amount;
    Buyer.wallet += WalletFundingAgreement.amount;
}
```

服务的最小业务职责是完成这一对守恒变化。把它拆成两个互不相关的远程更新，会失去“一次充值”的完整含义。

## 查询准备事实，成交检查实际范围

充值场景的关键流程如下，片段取自同一源文件：

```spp
checkBuyerCredential; checkFundingAmount; prepareWalletFunding;
parallel { findBuyer; findSettlementAccount; }
identify(Buyer); identify(SettlementAccount);
transaction {
    transferWalletFunds bounds {
        SettlementAccount.balance: [null, null];
        Buyer.wallet: [0, null];
    };
}
```

先检查输入，计算准备来源关系，然后补全买家与结算账户。两项查询的输入已经就绪，彼此不依赖，因此可以并发。事务只处理准备好的资金转移，不再在更新内部查找充值金额。

查询得到的余额用于了解参与者，不能代替实际成交约束。查询后仍可能有其他充值或付款发生，量子服务按实际成交值检查范围。本例钱包下限为零、来源不设上下限；如果业务把其他上下限保存在钱包角色中，场景应查询这些属性，并将相应限制传给量子调用。

## 入库沿用相同的业务结构

某商品入库 10 件，StockSupply.balance 减少 10，StockLine.available 增加 10。库存变化与资金变化使用不同属性，却都需要来源、去向、数量和实际成交约束。

[入库场景](../../demos/petstore/src/main/spp/petshop/catalogue/petshop-scene-receiveShopStock.spp) 先查询并确认商品，再准备库存和供应来源关系，并行查询双方，最后调用 `receiveInventory`。商店中的服务外观对接 [库存域量子定义](../../demos/petstore/src/main/spp/inventory/inventory.spp)，业务调用不用混入库存数据库的地址和协议。

同一种结构不意味着所有服务都应合并成一个通用动作。充值与入库具有不同业务单位和资格，分别命名后，业务人员可以直接识别它们的含义。

## 先留下可核对的基线

继续购买之前，记录这一组假设结果：

|事实|开户后|充值及入库后|
|买家钱包|0|500|
|结算来源|0|−500|
|可售／预留／已售|0／0／0|10／0／0|
|供应来源|0|−10|

检查失败也要具体：负金额应被校验拒绝，身份不存在不能成交，原请求重放不能再入账。页面防重和远程请求幂等由技术策略承担，不改变充值金额必须为正的业务规则。具体配置留到第六篇第32章统一讨论。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](28-petstore-modeling.md) · [下一章](30-order-lifecycle.md)
