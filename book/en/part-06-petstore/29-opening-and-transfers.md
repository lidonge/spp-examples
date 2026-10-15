# Chapter 29 — Zero Opening, Funding and Inventory Receipt

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Purchasing needs buyer, store, goods, wallet and stock. Establishing participation is separate from moving money or goods: opening creates no gifted balance or stock. Every later nonzero change has a source.

## Opening Prepares Identity and Zero Facts

New wallets, available/reserved/sold stock and sources begin at zero. Creation generates no nonzero transaction journal, and retries must not reset funded balances.

Business establishes identities; technology prepares records and quantum addresses. Durable split-storage tasks confirm and recover zero creation without per-scenario database retries. Part IV, Chapter 18, and Part V, Chapter 26, explain lifecycle and persistence.

After opening but before funding, the buyer exists with zero balance: an interpretable state.

## Funding Shows a Conserved Pair

Funding 500 increases Buyer.wallet by 500 and decreases SettlementAccount.balance by 500. From zero, results are 500 and −500, still summing to zero.

The negative source is a counterpart within the demo boundary. Real integration must confirm funding source, payment and settlement eligibility; this does not permit unconditional gifts.

[Funding source](../../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-fundShopWallet.spp) states:

```spp
quantum update transferWalletFunds(Buyer, SettlementAccount, WalletFundingAgreement) {
    SettlementAccount.balance -= WalletFundingAgreement.amount;
    Buyer.wallet += WalletFundingAgreement.amount;
}
```

The minimum responsibility is this pair's complete change. Splitting into unrelated remote updates loses the meaning of one funding activity.

## Query Facts, Check Actual Bounds at Settlement

From the same source:

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

Check inputs, prepare relationships, query buyer and source. Inputs are ready and independent, permitting concurrency. The transaction handles prepared transfer without looking up the amount inside the update.

Queried balances do not replace actual bounds: other funding or payment can intervene. This example uses a zero wallet lower bound and unlimited source bounds. Role-owned limits, if required, must be queried and passed to the quantum call.

## Inventory Receipt Uses the Same Structure

Receiving ten decreases StockSupply.balance by ten and increases StockLine.available by ten. The properties differ from money but still need source, destination, quantity and settlement bounds.

The [receipt scenario](../../../demos/petstore/src/main/spp/petshop/catalogue/petshop-scene-receiveShopStock.spp) confirms goods, prepares stock/source, queries both concurrently and calls `receiveInventory`, whose facade binds to [inventory quantum definitions](../../../demos/petstore/src/main/spp/inventory/inventory.spp). No database address or protocol enters business calls.

Similar structure does not require a generic action. Funding and stock receipt have different units and qualifications; distinct names preserve meaning.

## Record a Checkable Baseline

|Fact|After Opening|After Funding and Receipt|
|---|---:|---:|
|Buyer wallet|0|500|
|Settlement source|0|−500|
|Available / reserved / sold|0 / 0 / 0|10 / 0 / 0|
|Supply source|0|−10|

Check negative-amount rejection, absent-identity nonsettlement and original-request replay without another credit. UI guards and transport idempotency do not replace positive-amount rules. Part VI, Chapter 32, gives configuration.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](28-petstore-modeling.md) · [Next Chapter](30-order-lifecycle.md)
