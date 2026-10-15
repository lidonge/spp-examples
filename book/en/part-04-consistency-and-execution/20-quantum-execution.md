# Chapter 20 — Quantum Properties, Call Bounds and Conserved Settlement

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Balances and inventory frequently face concurrent changes. “Enough when queried” is insufficient; actual settlement requires bounds and consistency. Quantum properties and services make that need explicit.

## Properties and Deltas

Petstore declares wallet quantum and defines bilateral funding:

```spp
quantum update transferWalletFunds(
    Buyer, SettlementAccount, WalletFundingAgreement) {
    SettlementAccount.balance -= WalletFundingAgreement.amount;
    Buyer.wallet += WalletFundingAgreement.amount;
}
```

The service states the relationship; bounds specify this call's range. Limits generally belong to wallet-role properties, so scenarios query them before passing them. One transfer service can serve wallets with different limits.

## Query Wallet Limits First

A normal wallet may range from zero to 10,000 US dollars, while overdraft permits −500. Such facts belong to particular wallets rather than a hard-coded universal nonnegative transfer rule.

Payment queries the source lower bound; funding queries the destination upper bound; transfers obtain both sides' relevant limits. Adding 300 to 9,800 with a 10,000 maximum violates the range.

Limit queries retrieve settlement rules; balance queries support display or preliminary judgment. The scenario passes the limits, and execution checks them against actual settlement values. An earlier balance cannot guarantee success.

## Bounds Apply at Settlement

Two requests see 100 and each pays 80. Both preliminary checks can pass, but at most one settles without overdraft. The quantum implementation processes current values and checks constraints before commit.

Limits are evaluated before the call; null disables that direction's check. It does not mean unknown amount or replace a legitimate funding source. Eligibility remains explicit validation.

## Conserve Actual Relationships

Payment source decrease and destination increase match. Reservation moves available to reserved; shipping reserved to sold. Each goods identity conserves separately; another product's increase cannot hide this one's loss.

Money and inventory use different dimensions, not one numerical conservation equation. They can cooperate under a scenario with separate conservation groups and an overall transaction or recovery plan.

## Settlement Results and Participant Completion

The framework fills participants with settlement results. These describe the transaction's facts, not a global simultaneous snapshot across sources. Later transactions can continue changing values.

Ordinary prepared inputs remain stable as agreed; dynamic quantum facts belong to quantum execution. Business must not bypass it to save nonzero balance changes.

## Fully Automatic Inverse Transactions

To undo a quantum settlement, the system locates its original record and applies opposite deltas to original participants, without a developer-written inverse or corresponding compensation transaction.

A transfer of 100 from A to B reverses 100 from B to A. This restores the transaction's effect, not entire old balances, retaining other changes. Identity, inverse execution, deduplication and technical recovery belong to the system.

Other business handling remains explicit: cancel an order, return physical goods or retain an application. None requires reimplementing quantum reversal. The next chapter distinguishes rollback, inverse transactions and compensation.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](19-transactions.md) · [Next Chapter](21-recovery.md)
