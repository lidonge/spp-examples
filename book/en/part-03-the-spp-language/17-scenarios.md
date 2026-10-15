# Chapter 17 — Serial and Parallel Scenarios and Contract Formation

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Atomic services explain local responsibilities; Scenario expresses one defined business activity. Readers should see participants, qualifications, dependencies and commit boundaries without tracing hidden calls through layers.

## Reading a Funding Scenario

From [wallet funding source](../../../demos/petstore/src/main/spp/petshop/payment/petshop-scene-fundShopWallet.spp):

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

Inputs identify buyer, source account and agreement. Credentials and amount are checked, relationships prepared, then both sides queried concurrently. After identity confirmation, the explicit transaction executes fund transfer with bounds declared at the call.

## Contracts in Scenarios

WalletFundingAgreement expresses parties and amount; ShopOrder ordering; ReturnRequestAgreement a return request. A contract corresponds to a defined activity, not an arbitrary wrapper for a list or return object.

Later activities reference existing contracts. Payment uses an order; returns use the original order and reason. This preserves relationships without invoking the original scenario again.

## Explicit Orchestration and Automatic Binding

Argument-free calls reduce repeated names without removing participants. The compiler finds unique type bindings; multiple instances need explicit arguments. Readability cannot depend on guessing ambiguity.

Serial groups express order and parallel groups overlap execution. Inputs and effects must be established first; plans also check deployment support and recovery capabilities.

## A Reviewable Business Entry

A scenario should correspond to a named activity. Packing many actions into a generic command string hides eligibility and participant scope inside branches. Separate payment, shipping and return entries state their facts more clearly.

Scenarios turn combinations into readable business narratives. The next part explains identity, storage, transactions and resources that honor them.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](16-calculation-and-rules.md) · [Next Chapter](../part-04-consistency-and-execution/18-facts-and-storage.md)
