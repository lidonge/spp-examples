# Chapter 23 — Benefits of Separating Business and Technology

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Payment requires eligible parties to transfer an agreed amount and form a verifiable result. Encryption, caches, duplicate detection and database access support execution. S++ puts business in SPP, technical strategies in APP and resources and protocols in PHY, giving each a clear maintenance location.

## Let Business Specialists Review Business Directly

Changing a member discount from ten to fifteen percent requires checking eligibility, percentage and quotation. Mixed database, conversion and retry code makes specialists understand technology before assessing completeness.

SPP expresses discounts as calculations, conditions as validations and invocation as scenarios. Requirements specialists can review and model with AI. Tools supply queries, saves and integration, so review concerns business facts and rules. Part III, Chapter 12, explains how this reduces freely generated AI code.

Technical work also concentrates. Poor cache hit rates concern access policies; duplicates concern request identification and execution, not payment formulas.

## Adapt One Business to Different Environments

Customer facts can come from local storage or a remote domain. Protocols and protection can change while scenarios still use Buyer with the same meaning.

Moving the customer domain to a separate application changes APP bindings and PHY endpoints and resources, requiring transaction and recovery checks. If providers honor the same contract, payment gains no HTTP conversion or connection-management code.

Replacement must preserve meaning, effects and failures, not just types. A new interface cannot treat timeout as the old “not found.” Separation makes adaptation and verification explicit.

## Reuse Technical Capabilities Centrally

Orders, reservations and funding all need request identification. Separate lock, registration, result and recovery implementations can drift. A shared technical protocol with scenario-specific configuration reduces duplication and centralizes improvements.

Encryption, compression, tracing and throttling have similar value. Technical developers maintain facilities while business describes facts and results. Updated capability can serve many scenarios through configuration.

## Bind Java Technical Services Through APP Interception

Capabilities need not all be built into the compiler. Technical developers can implement Java services and bind them around scenario or atomic calls. SPP remains business; APP chooses targets and stages; PHY chooses classes and parameters.

To record all shop-service durations without modifying each payment, order or query, Petstore's [technical APP](../../../demos/petstore/src/main/spp/petshop/technical-services.app) declares:

```app
technical services { invocationTrace; }
intercept services {
    before: invocationTrace;
    after: invocationTrace;
    failure: invocationTrace;
}
```

`invocationTrace` names a capability. `intercept services` matches all generated services in this domain, including scenarios, ordinary CRUD and quantum services. `intercept scenarios` limits it to scenarios; `intercept findBuyer, reserveShopPet` selects named services. This is a technical binding, not a business call to a logging atomic service.

Its [PHY](../../../demos/petstore/src/main/spp/petshop/technical-services.phy) specifies:

```phy
phy {
    technical service invocationTrace {
        implementation: "free.servpp.service.technical.InvocationTraceService";
        config logger = "spp.petstore.invocations";
    }
}
```

New implementations implement `TechnicalService` and enter the runtime classpath. APP declares name and scope; PHY binds class and configuration. Chapter 27 builds a slow-call observer.

|Stage|When|Typical Use|
|---|---|---|
|before|Before business invocation|Technical access control and start recording|
|after|After normal return|Duration, validation result and completion recording|
|failure|When technical error propagates|Diagnostics and alerts|

`after` means normal method return, not validation acceptance or outer transaction commit. A reservation rejected and handled by fail can return normally and trigger after. Recording after alone cannot certify successful payment.

The interface exposes read-only service identity, kind, trusted headers, duration, validation result and technical error, not mutable participants. It directly supports observation and identity-based control. Data rewriting, query replacement or response changes need suitable adapters. Java capability can evolve while business ownership stays explicit. See the [interception protocol](../../references/app-technical-services.md).

## Optimization Must Honor Business Agreements

Display names may tolerate caching; payment cannot overwrite balances based on caches. Lists may return summaries, while returns need eligibility facts.

Business defines fact purposes and results; technology chooses strategies. It cannot omit checks or relax quantum bounds for speed or success rate. Freshness, recovery and outputs must honor agreements.

The next chapters discuss performance, security, reliable execution and governance. Facilities may reside in runtime, integration or adapters, without each becoming a remote microservice.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](../part-04-consistency-and-execution/22-generation-and-runtime.md) · [Next Chapter](24-performance-services.md)
