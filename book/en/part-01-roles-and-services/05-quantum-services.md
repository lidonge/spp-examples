# Chapter 5 — Quantum Behavior and Quantum Services

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Changing an address and transferring 100 US dollars both change data but impose very different demands. An address describes a customer; fund changes alter actual assets. Treating both as generic field updates hides the timing, reliability and concurrency requirements of transactions.

These differences explain why quantum services are defined and why their efficient, stable execution is central to asset-transfer systems.

## Timeliness

An alternative contact address usually only needs to become effective before its next use. Even next-day propagation may meet requirements without affecting completed business. An address used by an active delivery has that delivery's timing requirements instead.

Payment often differs. Buyers wait for confirmation before collecting goods; merchants wait for funds before shipping. Without confirmation, neither can proceed. Transfers must quickly establish whether funds arrived, rather than merely report that an update request was submitted.

Transaction systems therefore reduce the time to a definite settlement result. Speed includes reliable confirmation: an earlier response that cannot say whether funds arrived does not accelerate completion.

## Reliability

An unsuccessful address save often leaves the original address and permits another attempt. An unsuccessful transfer must establish whether money was debited, credited or transferred twice. Underpayment, duplicate debit or one-sided completion can cause actual losses.

If A transfers 100 to B, a debit without a credit is incomplete; two debits with one credit are also wrong. Checking that individual methods returned successfully cannot replace verifying their joint result.

If settlement completed but the response was lost, retrying must not transfer another 100. The system needs the original transaction identity and result confirmation. Reliability includes complete settlement, duplicate handling and post-failure confirmation.

## Concurrency

Customers seldom change addresses, while one account may receive and make many payments concurrently. Popular goods may attract many buyers at once.

Competition affects the same resource. Two buyers cannot both reserve the last item. Two requests calculating from old balances and overwriting them may lose one change.

Transaction services must protect actual deltas and settlement bounds at high frequency without putting unrelated requests into one queue. Different accounts and products can be handled separately; competition on one resource needs correct arbitration.

## Update Meaning and Conservation

An address update states the new information. A fund transaction also states source, destination and amount. A decrease of 100 at A and increase of 100 at B sum to zero. Moving inventory from available to reserved likewise identifies where quantity went.

The basic expression is the current delta and its related parties, not a previously calculated balance that might overwrite intervening transactions.

Conservation also requires real sources and destinations. Wallet funding must identify the funds' source; inventory receipt must identify supply. Otherwise the new number cannot explain how resources entered the system.

## Failure Handling and Traceability

Without intervening changes, saving the same address again produces the same information. Repeating a credit produces another amount. Transactions need identities distinguishing retries from new business.

Reversal must use the original actual deltas while retaining later business. Restoring an entire old balance may erase subsequent receipts. Original identity, source, destination, amount and result must therefore be traceable.

Settlement and recovery are part of transaction responsibility, rather than an afterthought added upon failure.

## Why Define Quantum Services?

The common problem is expressing a transaction as a clear business unit that cannot be arbitrarily split, with dedicated execution guarantees. SPP defines a quantum service as conservation between a pair of quantum properties: one decreases and the other increases within one business dimension. This is its minimum granularity.

For a transfer of 100 from A to B, the debit and credit can be analyzed separately, but a debit alone cannot count as a transfer. Smaller fragments cannot independently fulfill its objective. The quantum service preserves the complete meaning.

Starting at 1,000 and 200, successful transfer gives 900 and 300; rejection leaves 1,000 and 200. The partial state 900 and 200 is not complete settlement. Commit and recovery mechanisms provide the actual guarantee; Appendix D gives detailed arguments.

## Efficient, Stable Settlement Is the Core Priority

In payment, accounting and inventory systems, queries, validations and calculations prepare facts and results; assets actually change at settlement. Faster pages and queries cannot compensate for settlement that queues indefinitely, duplicates execution or leaves results unknown.

Efficient execution processes valid transactions promptly under specified resources and expected concurrency. Stable execution avoids lost or duplicate changes, preserves bounds and conservation, and confirms or recovers results after faults.

Architecture should distinguish preparation from settlement, and arrange resources, scheduling and recovery around quantum services. Both efficiency and reliability matter; removing checks only produces apparent speed.

## Expressing Them in Services and Scenarios

SPP uses quantum update for balance and inventory deltas; callers specify permitted bounds. Part IV, [Chapter 20](../part-04-consistency-and-execution/20-quantum-execution.md), develops properties, constraints and actual settlement.

Payment scenarios still organize order queries, eligibility, amount preparation, fund transfer and receipt recording. Quantum services focus on complete transaction changes; scenarios connect them to other responsibilities to complete payment.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](04-decomposition.md) · [Next Chapter](06-composition-and-conservation.md)
