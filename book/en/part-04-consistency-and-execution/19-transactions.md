# Chapter 19 — Transaction Boundaries, Execution Plans and Deployment Capabilities

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

“These changes must hold together” is a business requirement; resources and protocols are implementation. SPP expresses boundaries with transaction, APP selects strategy, PHY supplies real resources, and generated plans connect them.

## Ordinary Updates Default to Optimistic Locking

The system retains query baselines. After scenario calculation and validation, built-in updates conditionally write against those baselines. If another request changed ordinary facts, the update reports conflict rather than overwriting them. APP defines retry or recovery.

Two requests read one profile. The first changes address; the second changes phone using stale facts. Its save must detect the changed baseline instead of restoring the old address with the whole old profile. Optimistic locking avoids holding a record lock throughout query and calculation while checking competition at write time.

This coexists with automatic locking for queries inside a transaction. Outside queries establish baselines without prelocking; inside queries lock according to property type and the transaction's modifications.

|Queried Facts|Read Inside a Transaction|
|---|---|
|Ordinary participant|Automatic locking; current JDBC uses `SELECT ... FOR UPDATE`|
|Quantum facts|No ordinary read lock; quantum implementation protects settlement|
|Participant with ordinary and quantum facts|Ordinary facts lock if this transaction modifies them; quantum-only changes add no ordinary read lock|

SPP does not explicitly write select for update, but runtime locking exists. Outside profile queries protect later saves with baselines; inside queries lock ordinary records. Locking those does not mean locking wallet quantum facts. See [transaction reads](../../references/spp-transaction-reads.md).

## Local Joint Commit

Petstore develop uses LOCAL. Domains share a JVM and the required database, schema and connection resources, so quantum and ordinary changes enter one local transaction. Recovery applies within that resource scope.

The same database name does not prove a common transaction connection. Separate processes do not gain LOCAL merely by accessing one database. Compilation and startup validate actual identities.

## Phased Execution

Outside LOCAL, a concentrated quantum group may settle first, followed by ordinary groups according to mode. Saga restores committed phases. A later ordinary rollback cannot undo an already committed quantum change.

Plans require explicit recovery capabilities. Unsupported combinations should be rejected rather than inventing compensation. Joint success across phases differs from single-resource atomic commit.

## Nested Boundaries

REQUIRED joins the current boundary; ending it does not commit separately. Payment uses it for a logical scope, not independently committing payment before order.

REQUIRES_NEW is independent and does not automatically enter the outer recovery chain. Independent account opening may remain completed after outer failure and needs its own handling. Appendix E describes example-backend propagation support.

## Automatic Quantum-First Planning

Ordinary updates are built-in and contain no business query, calculation or validation. Scenarios supply complete facts through preparation and quantum results.

Ordinary saves do not affect quantum inputs or outcomes, and quantum order is exchangeable. The compiler therefore schedules quantum transactions before ordinary updates within a boundary, allowing unordered or merged execution. Serial groups arrange post-settlement calculations and validations before ready saves run concurrently. Runtime supplies context, resources, joining and failure handling. “After quantum services” describes phases; LOCAL can still commit them together at the end.

## Why SPP Has No Exception Syntax

SPP omits `try/catch/throw` so scenarios describe business rules and processing while APP defines technical-failure strategy executed by runtime and PHY. Business specialists need eligibility and joint-change requirements, not database connections, timeout types or low-level exceptions. Design separates error interception from business flow; [participant execution](../../references/spp-participant-execution.md) also excludes technical exceptions as SPP branch conditions.

Unsatisfied business conditions are explicit results. A shipped order may be ineligible for cancellation. Ordinary check ends its block; guard controls its enclosed steps; `breakTransction` explicitly requests reversal. Conditions and effects stay visible rather than hidden in exception classes.

Technical faults are not business facts. A database failure does not mean no order exists; payment timeout does not mean no settlement occurred. Catching these and choosing “not found” or “pay again” risks wrong decisions. APP defines confirmation, retry and recovery using execution and commit evidence, without presenting uncertainty as fact.

This also avoids coupling scenarios to providers' database and communication errors. Changing deployment should not force business rewrites. APP owns technical policies; generated Java and runtime can still use exceptions to implement them.

Separation does not remove business failure decisions. After acceptance, should unsuccessful processing leave an application pending, cancel it or refund fees? These choices alter business results and must be specified.

## Business Failure Compensation

SPP handles business failures: once conditions are known not to hold, what should happen to established results? Different businesses may choose different responses.

Insufficient inventory may lead to waiting for restocking or cancellation and refund. The framework confirms reservations and payment, but cannot choose for parties. `transaction { ... } fail { ... }` expresses post-failure business operations. Technical execution and recovery occur first; the adjacent fail receives failure facts. Its saves use a new explicit transaction.

|Failure|Decision Required from Business Developers|
|---|---|
|Admission rejects before changes|Reject with reason; do not refund a debit that never happened|
|Inventory held but later business validation rejects|Whether to cancel, releasing the actual reservation if canceled|
|Payment settled but fulfillment impossible|Keep payment for later handling, or cancel, refund and release holds|
|Application independently accepted but approval rejected|Keep for retry or mark rejected/canceled, and decide fee treatment|
|Goods delivered but later business cannot finish|Return, refund or another remedy; state changes do not return physical goods|

These are decisions, not a universal instruction to reverse all steps. Uncommitted changes can roll back; quantum services automatically reverse original transactions without a separately written business inverse. Business still decides cancellation, release or continued fulfillment. Later partial refunds or fees are new activities, not erasing original payment history.

Compensation respects layering. Refund eligibility is SPP; timeout executing the refund is APP. SPP defines qualifications, amounts and result; APP confirms, retries and recovers. Timeout is not business rejection.

## Example: Retain an Accepted Reservation and Record Rejection

Petstore saves acceptance before reserving inventory. With ten available and eleven requested, acceptance exists but reservation cannot settle. The scenario retains the original number and records rejection for insufficient stock. From the [actual scenario](../../../demos/petstore/src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp), omitting initial checks:

```spp
transaction { insertPetReservationAgreement; }
prepareReservationInventory; findStockLine; identify(StockLine[]);
transaction {
    reserveRequestedInventory bounds {
        StockLine[].available: [0, null]; StockLine[].reserved: [0, null]; };
    confirmPetReservation; updatePetReservationAgreement;
} fail {
    if (ResultInfo.failure.recoveryStatus == "ROLLED_BACK" || ResultInfo.failure.recoveryStatus == "REVERSED") {
        findStockLine; identify(StockLine[]);
        rejectPetReservation;
        transaction { updatePetReservationAgreement; }
    }
}
```

The first transaction independently saves acceptance; failure of the later one does not delete it. Success marks RESERVED. Failure first rolls back uncommitted effects or automatically reverses the settled quantum phase, then enters fail.

`ResultInfo` is a built-in scenario participant, not an input declaration. The example acts only for ROLLED_BACK or REVERSED: confirmed rollback or recovery of committed phases. It re-queries stock, calculates rejection and saves state in a fresh transaction, outside the failed boundary.

[Rejection calculation](../../../demos/petstore/src/main/spp/petshop/reservation/petshop-35-reservation.spp) marks REJECTED and distinguishes INSUFFICIENT_STOCK from RESERVATION_NOT_COMPLETED using recovered stock and requested quantity. Ten available against eleven yields the same reservation number, insufficient-stock reason and unchanged 10 available/0 reserved. A later ordinary-save fault despite sufficient stock instead records reservation not completed.

fail does not manually add inventory back. System rollback or automatic reversal handles that; fail expresses the business choice to preserve acceptance and record final rejection.

Unknown outcomes give RECOVERY_REQUIRED, so this example does not declare safe rejection. fail may record pending verification facts, but technical failure continues to APP and is not considered recovered merely because fail ran. After successful handling, status remains FAILED with handled true, rather than converting the original transaction to success. Current support is outer transaction fail in serial scenarios; multiple input contracts use `fail(targetContract)`. See [failure and system results](../../references/spp-transaction-failure-handling.md).

## Technical Failures Are Defined in APP

Update timeout may precede commit or follow commit with lost confirmation. APP defines original-request result queries, permitted retries, durable recovery tasks and operational escalation when confirmation is impossible. Runtime and PHY execute the policy.

Order-update timeout does not require SPP to catch it and cancel. APP first confirms the original update, restores a completed result or retries under the contract, and retains pending status if uncertain. Timeout alone does not trigger refund or cancellation.

Technical failures during refund or release also need APP progress, duplicate protection, confirmation and recovery. Report compensation complete only after business effects actually complete; retry must not duplicate them.

## Report Actual Results

Request failure may mean no commit, partially committed phases or an unknown outcome. Settlement and recovery evidence determine actual state; an HTTP error alone does not prove rollback everywhere.

Explicit transaction semantics and deployment capabilities turn boundaries into reliable promises. Appendices D and F state detailed support.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](18-facts-and-storage.md) · [Next Chapter](20-quantum-execution.md)
