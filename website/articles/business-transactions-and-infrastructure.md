# Business Transactions Without Infrastructure Details

A business transaction has an intended consistency boundary. A database transaction is one possible mechanism for implementing it. **S++ (ServPP)** keeps that distinction visible: SPP states the business boundary, while APP and PHY select how services and resources realize it.

That separation is useful only if the model also explains failure. A local database rollback, a reverse financial transaction and a business compensation are different operations. Calling all of them “rollback” makes a distributed workflow harder to reason about.

## Payment declares a boundary and a business limit

In the Petstore payment scenario, eligibility checks and calculation precede the update boundary. Inside it, a bounded funds transfer changes the buyer and merchant balances, and ordinary updates record the payment outcome.

The [quantum service](/sources/petstore-demo/petshop/payment/petshop-10-services.spp/) defines the transfer itself:

```spp
quantum update payOrderFunds(Buyer, Merchant, PaymentAgreement) {
    Buyer.wallet -= PaymentAgreement.paymentAmount;
    Merchant.cash += PaymentAgreement.paymentAmount;
}
```

The caller supplies the permitted bounds. This is the bounded invocation inside the [payment scenario](/sources/petstore-demo/petshop/payment/petshop-scene-payShopOrder.spp/):

```spp
payOrderFunds bounds {
    Buyer.wallet: [0, null];
    Merchant.cash: [0, null];
};
```

Here zero is a business lower limit and `null` leaves the upper limit unspecified. Another business operation may permit an overdraft and choose a different lower bound. The shared transfer service need not hard-code a universal prohibition on negative balances.

The generated implementation must enforce those bounds at the update, not merely check an old balance before changing it. A database-backed implementation can use conditional updates within its transaction. A different quantum service system may enforce the same contract differently. Committed values are filled back into the supplied participants so the scenario can continue using this transaction's results.

## Deployment determines what can commit together

The [APP definition](/sources/petstore-demo/petshop/petshop.app/) includes a development environment that deploys the domains together and selects `LOCAL`. That policy requires a compatible local deployment and database resource arrangement. It is not a way to make unrelated distributed databases share a local commit.

The testing configuration makes different choices, including a unified quantum store and remote domain routes. The [PHY definition](/sources/petstore-demo/petshop/petshop.phy/) supplies repositories, ledger storage and endpoints. These are realization choices rather than new business participants.

When several service modes cannot share one physical commit, a source-level boundary does not magically turn them into a single database transaction. The implementation needs coordination, reverse actions and recovery appropriate to those modes. The public demonstrations exercise particular configurations; they do not establish that every possible distributed combination is production-ready.

## A reservation can fail without erasing its application

The [reservation scenario](/sources/petstore-demo/petshop/reservation/petshop-scene-reserveShopPet.spp/) deliberately has two sequential transaction boundaries. The first stores an accepted reservation application. The second attempts to reserve inventory and confirm it.

If inventory is insufficient, the business wants to preserve the application and record its refusal. Undoing the whole user interaction would lose a useful business fact. The scenario therefore includes a `fail` block with access to the built-in result information:

```spp
if (ResultInfo.failure.recoveryStatus == "ROLLED_BACK"
    || ResultInfo.failure.recoveryStatus == "REVERSED") {
    findStockLine;
    identify(StockLine[]);
    rejectPetReservation;
    transaction {
        updatePetReservationAgreement;
    }
}
```

This excerpt is the body of that scenario's `fail` block. It checks that technical recovery has completed before recording the business rejection. It does not treat an unresolved recovery as an ordinary out-of-stock result. The earlier accepted application remains committed.

## Recovery is not the business decision

A local rollback restores uncommitted state. A reverse quantum operation reverses a committed change without overwriting unrelated later changes. A business compensation decides what to do when the desired outcome cannot be completed or reversed normally.

The framework can provide technical recovery and reverse-operation mechanisms. It cannot decide whether a customer should receive a substitute item, a manual review or another offer. Those are explicit business policies, expressed in services and failure handling.

Start with the [reservation source](/sources/petstore-demo/petshop/reservation/petshop-scene-reserveShopPet.spp/), then compare the [selected banking deposit examples](/examples/#deposit). The [transaction chapter](/book/part-04-consistency-and-execution/19-transactions/) develops the model further. The goal is to make both the business intention and the implementation's actual guarantees reviewable.
