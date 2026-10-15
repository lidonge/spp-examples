# Chapter 21 — Rollback, Inverse Transactions, Reversals and Compensation

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

“Undo” hides distinct duties: uncommitted rollback, settled-fund reversal, new business reversal and external compensation. Distinguishing them explains failure outcomes and recovery scope.

## Rollback Undoes an Unfinished Transaction

Technical rollback removes the current transaction's effects, retaining evidence and other independent committed results. Resources and protocols determine scope.

Committed Saga nodes are outside their original local transactions. The failed node can roll back its uncommitted effects; prior successful nodes need separate recovery.

## Ordinary Updates Can Also Be Automatically Reversed

Built-in ordinary updates contain no calculation or query for completion. They save already prepared facts. Systems can retain before facts and resulting versions to undo writes without a reverse service recalculating old values.

An address changes from A at v8 to B at v9. Recovery can restore A only if current version still equals this write's v9, and must produce a new version. Reverting the marker to v8 could wrongly accept formerly stale requests.

If another request produced C at v10, recovery cannot overwrite it. Even if values happen to return to B, the new version still matters. Version check and restore must be one atomic conditional operation, not a check followed by unconditional write.

Quantum reversal negates a delta while retaining later deltas; ordinary recovery restores facts only while the version qualifies, without later writes. Conflict requires APP confirmation and handling, not overwriting subsequent results.

## Recovering Mixed Cross-Domain Transactions

One SPP boundary may update different domains, processes and databases. It expresses joint business requirements, not a shared local database transaction. APP plans and PHY capabilities determine restoration.

Consider four updates:

|Update|Effect|Domain|
|---|---|---|
|Q1|Buyer wallet −100, merchant funds +100|Payment roles' domains|
|Q2|Available stock −1, order hold +1|Inventory|
|U1|Save order and agreed lines|Order|
|U2|Save processing receipt|Receipt owner|

Q1 and Q2 conserve different dimensions. Roles can belong to separate domains while configured unified quantum execution handles deltas. Ordinary repositories may be called remotely. Current non-LOCAL plans complete the quantum group, execute ordinary phases and retain commit records. Multiple quantum requests can settle together; ordinary updates follow configured coordination.

**If the quantum group does not settle, ordinary execution stops.** A balance or stock bound can reject the whole group. Its resource removes uncommitted effects and U1/U2 do not proceed. A purchase cannot debit without stock or save a success receipt for no settlement. Unknown quantum commit requires confirmation, not definite rejection.

**If quantum settlement succeeds but ordinary commit fails, restore both appropriately.** Suppose Q1/Q2 settle, U1 executes and U2 reports a definite conflict. If U1/U2 belong to a supported XA or Seata AT ordinary scope, that coordinator first restores its writes, then the mixed plan automatically reverses the quantum group. Executing U1 is not proof it committed independently; status follows its phase.

```text
Q1 + Q2 settled
  → Execute U1 and U2
  → U2 definitely fails
  → Undo unfinished ordinary transaction
  → Automatically reverse settled quantum group
  → Confirm every recovery result
```

**Independently committed ordinary phases need their own recovery.** Under Saga, U1 may commit before U2 fails. Roll back U2's unfinished transaction, restore U1 in reverse committed-phase order, then reverse quantum changes. U2's rollback cannot remove U1. Version-protected restoration uses U1 before facts and written version; if no later version exists it can restore without business recalculation. Otherwise retain a recovery conflict under APP policy.

**Unknown phase outcomes require confirmation first.** A remote U2 timeout may mean the receipt committed or never ran. Current mixed plans retain pending recovery instead of immediately reversing earlier commits. APP queries the original request, then completes or restores according to actual records. Otherwise funds and stock could be undone despite successfully saved order and receipt.

**Recovery failure means recovery remains incomplete.** Failed U1 restoration or lost quantum-reversal response retains original and recovery evidence. Current implementation records a failed recovery phase and still attempts others, potentially producing partial recovery. Every result must be checked; “recovery started” is not “fully undone.” APP defines later confirmation, retry and handling. Quantum inverse deduplication prevents duplicate refunds, and permitted business during recovery follows explicit policy.

Rollback concerns the uncommitted phase; quantum inverse restores committed deltas; ordinary reversal restores qualifying versions. A later bank reversal is new business, not this automatic failure recovery.

These capabilities need before facts, versions, records and backend protocols. Shared databases do not imply shared connections, and naming XA, Seata AT or Saga does not prove deployment guarantees. See [environments](../../references/deployment-environments-and-physical-defaults.md) and [storage contracts](../../references/transaction-storage-v1.md).

## Local Rollback and Split-Storage Recovery in the Bank Case

The bank case in Part VII, Chapter 33 provides a concrete comparison: cash reversal has already applied reverse fund movements when saving reversal postings fails.

|Deployment and Failure Point|Actual Funds and Ordinary Facts|System Outcome|
|---|---|---|
|Shared local transaction resource; reversal postings fail to save|Funds, the original-transaction flag and reversal contract roll back together; the original remains unreversed|`ROLLED_BACK`|
|Separate quantum and ordinary storage; posting save fails after some ordinary stages commit|Quantum inverse transactions restore funds; ordinary flags or reversal contracts may remain|`RECOVERY_REQUIRED`, `handled=false`|
|Saving the failure-disposition record also fails|Preserve the original failure, actual recovery state and secondary disposition failure|Entering `fail` does not establish successful disposition|

The case's split-storage repository has not yet implemented automatic recovery for committed ordinary stages. This does not change the principle of version-guarded automatic reversal, but shows that the backend protocol must actually be implemented and verified. Recording reconciliation facts is failure disposition; restoring funds and ordinary records is transaction recovery.

Tests also change an original contract's version after it has been queried, verifying that reversal cannot overwrite a later change. Even when split-storage funds have been restored, earlier ordinary stages may remain. The system preserves the pending-recovery result rather than allowing a direct retry to hide it. The [case verification record](../../../demos/bank-deposit/docs/latest-refactoring-verification.md) documents the persisted outcomes.

## Automatic Inverse Transactions Retain Later Results

Starting at 100, +50 then +20 gives 170. Reversing the first subtracts 50, leaving 120. Restoring a snapshot of 100 would erase the second activity.

The system inverses original settlement components and maintains participant identity, duplicate protection and confirmation. APP handles technical confirmation and recovery. Failure of the inverse request does not prove the inverse did not settle.

## Business Reversal Is a New Activity

A bank reverses a completed transaction for business reasons by querying the original, checking eligibility and forming a new result. Original principal and interest components must be restored, not recalculated under today's policy.

It has its own transaction and failure handling. Cross-day rules, later dependencies, disbursed funds and external effects may constrain eligibility. This differs from technical rollback before original commit.

## Compensation Requires Business Decisions

Consumed goods or irreversible external effects may require another remedy. Content, triggers and completion criteria must be agreed; systems execute, record and retry the defined rules.

Automatic quantum inverses and version-qualified ordinary restoration do not decide physical returns or substitute fulfillment. Database restoration cannot erase external effects, and later ordinary versions prohibit forced old-value restoration.

## APP Converts Definite Technical Failures into Business Failures

Conversion requires a known outcome and agreed business meaning. A definitely rejected unique-key write may become “number already taken”; optimistic conflict may become “information changed; reconfirm.” SPP handles the result without database error types. APP defines these mappings explicitly, rather than classifying every error as one rejection.

Timeout, disconnection or lost commit confirmation can occur after commit. They indicate absence of a definite response, not business failure. APP confirms before returning success or rejection; until then, retain uncertainty and technical recovery, without triggering business compensation.

Separation therefore permits cross-layer failure information: definite, meaningful failures become business failures; uncertain ones require confirmation first.

## Unknown Outcomes

Timeout can precede or follow commit. Stable request identity and result lookup confirm the original instead of starting a duplicate with a new identity.

The repository contains inverse execution and several recovery evidence paths. Complete durable coordination and compensation have specific coverage limits. Appendix F separates existing evidence from unresolved matters.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](20-quantum-execution.md) · [Next Chapter](22-generation-and-runtime.md)
