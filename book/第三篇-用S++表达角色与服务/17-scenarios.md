# 第17章 场景中的串行并行与合约形成

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

原子服务解释局部职责，Scenario 表达一次明确的业务活动。读者应当能够从场景看到参与者、资格、依赖和提交边界，而无需逐层追踪隐藏调用。

## 从充值场景阅读结构

以下片段摘自 [钱包充值源码](../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-fundShopWallet.spp)：

```spp
Scenario serial fundShopWallet(
    Buyer, SettlementAccount, WalletFundingAgreement) {
    checkBuyerCredential; checkFundingAmount; prepareWalletFunding;
    parallel { findBuyer; findSettlementAccount; }
    identify(Buyer); identify(SettlementAccount);
    transaction {
        transferWalletFunds bounds {
            SettlementAccount.balance: [null, null];
            Buyer.wallet: [0, null];
        };
    }
}
```

入口给出买家、来源账户和充值约定。首先检查凭证与金额，准备来源和合约关系，再并行补全双方事实。身份确认之后，资金转移在显式事务内执行，成交范围在调用处声明。

## 场景中的合约

WalletFundingAgreement 表达金额与参与方；ShopOrder 表达订单；ReturnRequestAgreement 表达退货申请。一个合约对应明确活动，不能只为了包装列表或返回结果随意创建合约类型。

后续活动可以引用已有合约。付款使用订单，退货申请使用原订单与申请理由。这样的引用保持业务关系，不需要再次调用原场景。

## 显式编排与自动绑定

无参数调用减少重复写入口名称，但没有删除参与者。编译器按类型寻找唯一绑定，同类型多实例时需要显式参数。自动绑定服务于可读性，不能用猜测掩盖歧义。

串行组表达顺序，parallel 组表达重叠执行。业务必须先确认输入和影响关系；事务计划还会检查部署是否支持所需操作与恢复能力。

## 形成可审查的业务入口

一个场景应当对应可命名的业务动作。把许多动作塞进通用命令字符串，会把资格和参与者范围隐藏在分支中。独立付款、发货和退货入口更容易说明各自需要什么事实。

场景使服务组合成为正文可读的业务叙述。下一篇将讨论这些声明如何通过身份、存储、事务与资源约定得到保障。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](16-calculation-and-rules.md) · [下一章](../第四篇-一致性与执行保障/18-facts-and-storage.md)
