# Role-Oriented Service Architecture

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## S++ (SPP): Modeling, Language Mechanisms and Engineering Practice

This book is for developers familiar with object-oriented programming. Roles describe the capacities in which participants enter a business activity; services describe their behavior; scenarios organize cooperation; contracts record agreements and results. Beginning with “service = participants × behavior,” the book connects role modeling, service composition and engineering practice into one system.

The main text explains concepts through business examples and can be read in order. Formal definitions, proofs, counterexamples and performance derivations appear in the appendices. Equations use plain text without requiring a LaTeX plugin; examples link to case source.

Monetary examples in this English edition use US dollars (USD), with English participant names. Amounts are illustrative and retain their numeric values; no exchange-rate conversion is implied. The banking case preserves its original currency-specific eligibility rules.

The complete manuscript has seven parts, 35 chapters and six appendices. Each part has its own introduction and contents; each chapter links to its part, the whole book and adjacent chapters.

The initial English translation follows the Chinese manuscript at revision `39287373`, including the discussions of modeling expressiveness, the bank case and COBOL/S++ code counts. S++ keywords, identifiers and executable examples retain their source forms; referenced engineering documents and editorial issue records retain their original language. The bank is described generically; real repository paths remain in source links. Chapters 3 and 14 were updated in both languages on October 16, 2026 for intrinsic role composition, joint and alternative take relationships and independent APP storage identity; translation-map.json records those section updates.

[Chinese Edition](../README.md)

## [Part I — The Basic Model of Roles and Services](part-01-roles-and-services/README.md)

- [Chapter 1 — From Objects to Business Activities](part-01-roles-and-services/01-business-activities.md)
- [Chapter 2 — Service Equals Participants Multiplied by Behavior](part-01-roles-and-services/02-service-model.md)
- [Chapter 3 — Roles and Business Identity](part-01-roles-and-services/03-roles.md)
- [Chapter 4 — Service Categories and Scenario Organization](part-01-roles-and-services/04-decomposition.md)
- [Chapter 5 — Quantum Behavior and Quantum Services](part-01-roles-and-services/05-quantum-services.md)
- [Chapter 6 — Superposition, Commutativity and Entanglement](part-01-roles-and-services/06-composition-and-conservation.md)
- [Chapter 7 — Queries, Calculations, Validations and Ordinary Updates](part-01-roles-and-services/07-business-service-characteristics.md)
- [Chapter 8 — Reusing Services and Scenarios Through Role Polymorphism](part-01-roles-and-services/08-polymorphism-and-separation.md)

## [Part II — Service Cooperation and Execution](part-02-service-cooperation/README.md)

- [Chapter 9 — Service Cooperation and Execution Order](part-02-service-cooperation/09-service-coordination.md)
- [Chapter 10 — Parallel Execution and Service Call Costs](part-02-service-cooperation/10-parallelism-and-costs.md)
- [Chapter 11 — Minimum Service Granularity and Deployment Principles](part-02-service-cooperation/11-deployment-granularity.md)

## [Part III — Expressing Roles and Services in S++](part-03-the-spp-language/README.md)

- [Chapter 12 — Responsibilities of SPP, APP and PHY](part-03-the-spp-language/12-layers.md)
- [Chapter 13 — Entity, Reference, Role and Contract](part-03-the-spp-language/13-business-models.md)
- [Chapter 14 — Declaring Role Relationships with take ... as](part-03-the-spp-language/14-take.md)
- [Chapter 15 — Four Categories of Atomic Service](part-03-the-spp-language/15-atomic-services.md)
- [Chapter 16 — Calculation Rules and Collection Participants](part-03-the-spp-language/16-calculation-and-rules.md)
- [Chapter 17 — Serial and Parallel Scenarios and Contract Formation](part-03-the-spp-language/17-scenarios.md)

## [Part IV — Consistency and Execution Guarantees](part-04-consistency-and-execution/README.md)

- [Chapter 18 — Business Facts, Participant Identity and Storage Ownership](part-04-consistency-and-execution/18-facts-and-storage.md)
- [Chapter 19 — Transaction Boundaries, Execution Plans and Deployment Capabilities](part-04-consistency-and-execution/19-transactions.md)
- [Chapter 20 — Quantum Properties, Call Bounds and Conserved Settlement](part-04-consistency-and-execution/20-quantum-execution.md)
- [Chapter 21 — Rollback, Inverse Transactions, Reversals and Compensation](part-04-consistency-and-execution/21-recovery.md)
- [Chapter 22 — Generation, Physical Resources and Runtime Configuration](part-04-consistency-and-execution/22-generation-and-runtime.md)

## [Part V — Separating Business and Technology](part-05-business-and-technology/README.md)

- [Chapter 23 — Benefits of Separating Business and Technology](part-05-business-and-technology/23-separation-benefits.md)
- [Chapter 24 — Performance Through Caching and On-Demand Data](part-05-business-and-technology/24-performance-services.md)
- [Chapter 25 — Encryption, Fingerprints and Security Services](part-05-business-and-technology/25-security-services.md)
- [Chapter 26 — Idempotency, Duplicate Guards and Reliable Execution](part-05-business-and-technology/26-reliability-services.md)
- [Chapter 27 — Runtime Governance and Technical Evolution](part-05-business-and-technology/27-operations-and-evolution.md)

## [Part VI — Complete Petstore Practice](part-06-petstore/README.md)

- [Chapter 28 — Identifying Roles, Behavior and Services from Requirements](part-06-petstore/28-petstore-modeling.md)
- [Chapter 29 — Zero Opening, Funding and Inventory Receipt](part-06-petstore/29-opening-and-transfers.md)
- [Chapter 30 — Quotation, Ordering, Payment and Shipping](part-06-petstore/30-order-lifecycle.md)
- [Chapter 31 — Cancellation, Returns, Reservations and Failure Handling](part-06-petstore/31-returns-and-reservations.md)
- [Chapter 32 — Technical Configuration, Deployment and Integrated Verification](part-06-petstore/32-validation-and-performance.md)

## [Part VII — Advanced Cases and Architectural Methods](part-07-advanced-cases/README.md)

- [Chapter 33 — Bank Deposits, Repayment Allocation and Reversal](part-07-advanced-cases/33-banking.md)
- [Chapter 34 — Migrating an Existing Object-Oriented System](part-07-advanced-cases/34-migration.md)
- [Chapter 35 — Architecture Review and Capability Boundaries](part-07-advanced-cases/35-design-review.md)

## [Appendices](appendices/README.md)

- [Appendix A — The Service Model and Formal Derivations](appendices/a-service-model.md)
- [Appendix B — Conditions for Exchange, Reordering and Parallelism](appendices/b-parallel-conditions.md)
- [Appendix C — Performance Models and Experimental Methods](appendices/c-performance.md)
- [Appendix D — Quantum Services and Conservation Mechanisms](appendices/d-quantum-contracts.md)
- [Appendix E — Language and Engineering Reference](appendices/e-language-and-build.md)
- [Appendix F — Sources and Verification Evidence](appendices/f-sources-and-evidence.md)

## Supporting Material

[Editorial Issues](../编辑工作/known-issues.md) are author working notes outside the reading sequence. Appendix F contains source references, verification evidence and reproducible code counts. The [translation map](translation-map.json) records corresponding Chinese and English files.
