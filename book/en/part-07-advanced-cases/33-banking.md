# Chapter 33 — Bank Deposits, Repayment Allocation and Reversal

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

A bank's deposit business includes admission checks, authorization, repayment allocation, interest accrual, accounting and reversal. It provides a useful test of whether role-oriented service architecture can express complex rules while keeping business and technology separate.

This chapter uses the repository's [bank deposit case study](../../../demos/bank-deposit/README.md). Business logic is expressed in SPP, APP and PHY; tools generate the production Java code. Tests only prepare inputs, invoke generated services, assert outcomes and inject technical faults. Business rules and demonstration configuration have distinct sources; they do not represent every policy of the original bank system.

## Distinct Participating Facts

Accounts, debts, product policies, business dates, authorization evidence, funding sources, processing plans and original transactions all participate. Account balance, interest-bearing amount, interest owed, principal owed and overdraft exposure have different meanings. Their common representation as amounts does not justify combining them into one field.

Front-office cash acceptance and core calculations may also have different amount conditions. Requiring a positive amount at the front office does not justify deleting a zero-amount repayment path in the core. Service contracts must preserve these differences between calling layers.

The current case separates accounts, eligibility, calculations, fees, accruals, postings, deposits and reversals into capability directories. Each scenario has its own file and directly organizes queries, checks, calculations and updates. A single umbrella scenario does not hide every step. The [source navigation](../../../demos/bank-deposit/docs/source-map.md) identifies these capabilities.

## Repayment Allocation and Actual Fund Destinations

Normal debt and impaired debt can have different principal and interest repayment priorities. Business calculations first produce explicit components; the scenario then organizes account changes and postings. Eligibility and authorization checks remain visible in the scenario, while APP and PHY connect queries and storage.

Suppose a cash deposit of 100 US dollars repays 10 US dollars of interest and increases the customer's balance by 90 US dollars. The actual fund movements are:

```text
Cash settlement account       −100
Customer account               +90
Bank interest-income account   +10
Total fund movement              0

Interest owed separately falls by 10: this is a debt-settlement fact.
```

Treating a ten-dollar reduction in interest owed as the destination of funds is incomplete. Reducing debt explains how much less the customer owes; it does not explain where the money actually received by the bank is held. The case therefore explicitly introduces three internal accounts: interest income, collection-interest income and principal recovery. Calculations determine the components; quantum settlement updates actual recipients; the contract records the actual accounts and amounts; postings provide corresponding accounting evidence.

Debt and exposure continue to follow the case's quantum-property conventions, but must not be counted again in the fund-conservation group above. Fund conservation and changes in debt express different facts. APP specifies the current fund-conservation group; the runtime still records actual changes, bounds and inverse-transaction information for the other quantum properties.

Components need sufficient precision. Three-decimal interest can follow the agreed business mathematics; physical columns must not silently truncate it. Any required rounding must be explicit business policy. Demonstration parameters must also be distinguished from rules traced to original sources.

## Prepare Through Queries and Calculations, Then Settle Within the Transaction

The [cash-deposit scenario](../../../demos/bank-deposit/src/main/spp/cboddeposit/deposit/cboddeposit-scene-depositCash.spp) first queries the customer account, eligibility, funding counterparties and accrual facts in parallel. It then checks ownership, eligibility and authorization, and calculates fees, repayment components, postings and accruals. Updates that must hold together belong within an explicit transaction boundary.

Opening an account establishes only a zero balance; depositing cash creates actual fund movements. The bank's internal recipient accounts must also be opened first. A first interest repayment cannot create nonzero funds from nothing.

Within the transaction, quantum settlement comes first. Subsequent calculations of accrual and processing information prepare facts for ordinary saves, which persist account metadata, the deposit contract and postings. These calculations have dependencies preserved by the serial flow; parallel ordinary updates remain subject to their prerequisites. The scenario declares the complete business boundary, while APP and PHY implement it using actual resources.

## Authorization Checks and Resuming After Authorization

Pending authorization is a business outcome, not a generic technical exception. The current case supports eligibility and authorization assessment. Persisting pending applications, choosing the authorization domain and resuming across processes still have boundaries to resolve.

A complete resumption flow should requery and recheck potentially changed eligibility after authorization arrives, then execute against current facts. Existing authorization checks do not constitute that complete workflow. The case's [known issues](../../../demos/bank-deposit/docs/known-issues-latest.md) records the distinction.

## Reversal Driven by the Original Transaction

The [cash-reversal scenario](../../../demos/bank-deposit/src/main/spp/cboddeposit/reversal/cboddeposit-scene-reverseCash.spp) queries the original contract, actual postings and current account facts. It checks original ownership, recipient accounts, reversal eligibility and posting evidence, then derives reverse movements from the original settled components. Changed policies or loan status must not cause reallocation of the original amount.

If 100 US dollars is deposited and another five US dollars arrives later, reversing the first deposit must preserve the later five US dollars. Reversal must not restore the entire account to its old snapshot. Similarly, the original agreement records the fee and internal recipient accounts; current rates or account routing must not select them again.

The contract preserves a snapshot of settled postings. Before reversal, actual postings are compared against that evidence. Corrupted accounts, amounts or records must cause explicit rejection; balanced totals alone do not justify proceeding. Cross-day handling, Mode2, accruals and current eligibility also have their own checks and calculations.

A separate [read-only reversal preview](../../../demos/bank-deposit/src/main/spp/cboddeposit/reversal/cboddeposit-scene-previewCashReversal.spp) runs the same preparatory queries, checks and candidate calculations without settlement or persistence. Displaying eight candidate posting lines does not mean accounting facts have changed. Formal reversal must check current facts again.

## Recovery from the Same Failure Under Different Deployments

In develop, related updates share a local transaction resource. If saving reversal postings fails, quantum and ordinary changes roll back together. The original transaction remains unreversed and can be retried after the outcome is confirmed.

In testing, quantum storage and ordinary records are separate. After quantum settlement, some ordinary Saga stages may already have committed. A later posting-save failure can trigger an inverse transaction for quantum funds, while already-committed ordinary facts may remain. The current case explicitly preserves `RECOVERY_REQUIRED` and `handled=false`. Restoring funds is not proof that the whole business activity has been undone.

This demonstrates the implementation boundary discussed in Part IV, Chapter 21. The architectural possibility of version-guarded automatic reversal for ordinary updates does not mean every repository and deployment already supports it. The case's `fail` block saves a failure-disposition record. It records that this transaction's fund movement was not completed only after the system confirms `ROLLED_BACK` or `REVERSED`; a reconciliation record cannot replace actual recovery.

The disposition record preserves the contract and system failure information as they stood at the time. Later queries must still show the original cause, phase and recovery status, without current balances or associations overwriting them. If saving that record also fails, the original transaction failure and actual recovery state must remain available.

## Business Expression in Relation to Source Size

A source count on October 14, 2026 identified nine COBOL programs explicitly located by file or line references in the case documentation. They directly reference 135 COPYBOOKs; following nested references yields 161 distinct COPYBOOKs.

|Content|Files|Physical Lines, Including Blanks and Comments|Lines Excluding Blanks and Comments|
|---|---:|---:|---:|
|COBOL programs directly located for analysis|9|14,156|11,410|
|Corresponding COPYBOOKs, including nested references|161|23,488|11,179|
|Original-source total|170|37,644|22,589|
|Current SPP business source and enums|35|1,043|979|
|Current APP and PHY configuration|4|86|86|
|Current S++ source total|39|1,129|1,065|

Expanding the scope to all related programs mentioned in the documentation gives 22 COBOL programs and 192 distinct COPYBOOKs: 45,587 physical lines, or 28,358 excluding blanks and comments. This broader scope includes dispatch, data access, accounting configuration and branches that have not been migrated.

These figures describe the maintenance scale of the business expression and original implementation, but their coverage differs. The original count includes entire source files; the case migrates selected business paths. Current S++ figures exclude tests, web pages, generated Java and shared frameworks. They therefore do not establish that more than thirty thousand lines of COBOL have been fully and equivalently replaced by roughly one thousand lines of S++, nor do they establish a productivity multiplier.

S++ concentrates selected rules in business models, calculations, checks and scenarios, leaving repetitive access and execution facilities to tools. Business expression becomes more focused, while tools and frameworks still implement the system. Appendix F9 provides detailed counts, source inventories and reproduction instructions.

## From Web Operations to Verification Evidence

The [Chinese-language deposit workbench](../../../demos/bank-deposit/docs/web-workbench.md) supports account opening, cash deposits, reversal previews, formal reversals and accounting queries. The page submits participants and displays results; it does not calculate fees or repayment allocation. Communication loss is shown as an unconfirmed outcome, without automatically resubmitting an update or presenting input balances and candidate postings as settled facts.

Verification includes real JDBC storage, rule vectors, failures in two environments, concurrent contention, request idempotency, independent-process restarts and browser flows. See the [latest verification record](../../../demos/bank-deposit/docs/latest-refactoring-verification.md) and Appendix F for configurations, batches and limits. Outstanding ordinary Saga recovery, complete authorization resumption and automatic resolution of unknown settlement outcomes remain separately documented in the [completion audit](../../../demos/bank-deposit/docs/completion-audit.md).

Complex business becomes manageable by expressing rules, participating facts, processing plans, settlement and recovery separately, then connecting them through scenarios. Existing evidence supports defined paths. Original COBOL execution and bank-confirmed results remain distinct evidence levels; test counts alone cannot establish business equivalence.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](../part-06-petstore/32-validation-and-performance.md) · [Next Chapter](34-migration.md)
