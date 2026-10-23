# Chapter 31 — Cancellation, Returns, Reservations and Failure Handling

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Completed order stages determine subsequent services. Cancellation and return are new activities; rollback and inverse execution restore the original failed activity. Both can reverse changes but have different meanings.

## Follow Established Facts

These are alternative branches, not consecutive steps on one order:

|Starting Point|Activity|Money|Inventory|
|---|---|---|---|
|Ordered, unpaid|Cancel unpaid order|None|Two reserved become available|
|Paid, unshipped|Cancel paid order|Refund 108|Two reserved become available|
|Delivered, return eligible|Request return|None|None; record request/reason|
|Request qualifies for approval|Approve return|Refund agreed amount|Corresponding sold units become available|

[Return request](../../../demos/petstore/src/main/spp/petshop/returns/petshop-scene-requestShopReturn.spp) needs buyer, original order and request. [Approval](../../../demos/petstore/src/main/spp/petshop/returns/petshop-scene-approveShopReturn.spp) adds funds and stock. Policies requiring physical receipt first need that fact and eligibility; demo rules are not universal.

Use confirmed amounts and quantities, not old wallet/stock snapshots that erase later business.

## Business Refund Versus Automatic Inverse

Canceling a successful payment is new refund business with eligibility, contract and receipt. Undoing a payment that failed during execution restores its original effects; quantum inverses need no separate business service.

Ordinary restoration protects later versions under Part IV, Chapter 21. The current implementation still requires corresponding compensation capability; simple save logic is not proof all deployments already provide automatic conditional inverse updates.

If quantum funds settle but cross-resource order save fails, APP recovers committed phases. Full confirmed recovery permits declaring reversal; partial failure remains pending. SPP does not take over remote result queries and database retries.

## Reservation Intentionally Retains Acceptance

The [reservation scenario](../../../demos/petstore/src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp) first saves acceptance and number, then reserves and confirms in a second transaction. Competition may cause the second to fail while acceptance survives.

With ten available and eleven requested, quantum bounds reject reservation. After confirmed rollback or inverse execution, the scenario records rejection while keeping the number for queries.

The second boundary is:

```spp
transaction {
    reserveRequestedInventory bounds {
        StockLine[].available: [0, null];
        StockLine[].reserved: [0, null];
    };
    confirmPetReservation; updatePetReservationAgreement;
} fail {
    if (ResultInfo.failure.recoveryStatus == "ROLLED_BACK" ||
        ResultInfo.failure.recoveryStatus == "REVERSED") {
        findStockLine; identify(StockLine[]);
        rejectPetReservation;
        transaction { updatePetReservationAgreement; }
    }
}
```

The fresh stock query supports reason selection: insufficient current stock versus another incomplete reservation. [Model and calculation](../../../demos/petstore/src/main/spp/petshop/reservation/petshop-35-reservation.spp) define it. Business does not catch database exceptions; it handles accepted applications after recovery confirmation.

## Three Different Failure Paths

|Situation|Facts|Handling|
|---|---|---|
|Invalid quantity|No settlement|Validation rejects before stock transaction|
|Reservation fails; recovery confirmed|Acceptance retained, reservation undone|fail saves business rejection and reason|
|Reservation/recovery unknown|Resource changes unconfirmed|APP confirms and recovers; no definite rejection|

Definite meaningful technical failures can reach business handling. Timeout is not automatically insufficient stock and must not make fail reserve again. The guard prevents that error.

If the rejection save fails, do not pretend it persisted. Preserve evidence and continue confirmation. ResultInfo describes this execution; stored status and reason describe the application.

## Verify Completion with Faults

Check insufficient stock, ordinary-save failure after quantum changes, and unknown results. The first two require stock, application state and reason checks; unknown requires recovery records and no repeated reservation.

See [failure evidence](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/reservation-failure-handling.md). LOCAL tests alone do not prove every real cross-domain recovery. Check resources and evidence together next.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](30-order-lifecycle.md) · [Next Chapter](32-validation-and-performance.md)
