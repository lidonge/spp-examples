# Chapter 12 — Responsibilities of SPP, APP and PHY

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

S++ layers separate business from technology and logic from physical implementation. The first lets people with different skills handle business development and technical adaptation. The second separates technical development from deployment and operations.

For payment, business specialists care about parties, amount, eligibility and joint results. Technical developers handle storage and external-system integration; operators choose databases, locations and resource configuration. Combining everything in one program makes all participants understand and change mixed logic.

SPP, APP and PHY respectively carry business expression, application technical contracts and actual physical configuration, connecting the work through explicit agreements.

## Let Business Specialists Express Business

SPP defines participants, roles, contracts, calculations, validations and scenarios. Payment amounts, discounts, shipping eligibility and conservation belong here, as do required transaction boundaries.

Business development need not also write SQL, message conversion, networking or transaction-framework code. Built-in queries and updates, business calculations and explicit scenarios let people inspect requirements without understanding large implementations.

For “members receive ten percent off,” a requirements specialist can inspect membership role, formula and quotation flow. Buyer-customer role playing is expressed in SPP; integrating the customer system and choosing retrieval protocols is technical work.

Business development can even be assigned directly to people who understand requirements. After learning roles, services and scenarios, they can produce compilable models. Technical developers focus on connecting those expressions to actual systems.

Roles and contracts become shared interfaces: business specifies payer, payee and amount meaning; technical development supplies their facts and execution.

## Separate Technical Development from Operations

Technical logic states required capabilities; physical configuration supplies them in an environment. APP organizes repository mappings, bindings, interfaces, duplicate protection, numbering, logical resources and environment deployment. PHY selects databases, protocols, numeric representations and runtime resources.

Accessing customers, saving orders and using transaction resources are application contracts. Actual development, testing and production addresses, connections and parameters are physical choices.

Developers build and adapt capabilities; operators configure and manage resources. Switching customer endpoint or migrating a database should not rewrite payment or discount formulas.

Some capabilities, such as a new numeric representation or transaction protocol, first require an adapter. Once available, operators select and configure it. Development and resource management thus have distinct locations.

## How Three Layers Complete Payment

|Layer|Content|Primary Responsibility|
|---|---|---|
|SPP|Buyer, merchant, agreement, qualifications, amount and transaction boundary|Business developers or requirements specialists familiar with the language|
|APP|Storage mappings, bindings, interfaces and technical contracts|Technical developers and integrators|
|PHY|Databases, endpoints, resources and physical representations|Operators, with adapters supplied by technical developers|

SPP expresses buyer −100 and merchant +100 and the order-receipt result. APP organizes storage and integration, selecting execution that honors the boundary. PHY supplies actual resources.

Order numbers with direct business use can belong to SPP. Internal storage keys are supplied by compiler and system, without an extra business ID. Rounding is business; machine representation and storage capacity are physical. These distinctions preserve meaning while separating maintenance.

## AI Maintains Less Source; Tools Produce Deterministic Output

Traditional AI-generated payment code may mix business decisions, objects, conversion, repositories, remote calls, transactions and deployment. More code creates more consistency relationships to preserve and more locations to find when requirements change.

S++ gives AI clearer tools. Business changes concentrate in SPP, integration in APP, environments in PHY. AI modifies relevant source rather than recreating all implementation layers each time.

Compilers, generators and runtimes produce repeated model, mapping, query/save integration, call, interface and storage code from declarations. The same source, configuration and tool version use the same rules to produce corresponding output.

The amount of freely generated and maintained AI code can therefore decline substantially. Relationships formerly written repeatedly and manually checked are generated and validated by tools. Fewer simultaneous choices reduce opportunities for omissions, duplication and cross-layer inconsistency.

A discount change alters calculation while tools maintain models and infrastructure. A protocol change alters adaptation while payment retains its roles and scenarios. Deterministic transformations let AI focus on requirements, modeling and necessary adaptation.

Tools still execute the supplied expressions. Business correctness and adapter guarantees require review and validation by their owners. Layers locate these concerns and reduce mixed business-technology-deployment-operations logic maintained by AI.

## Human Focus and Quality Control

SPP contains business models, rules and flows. Human review can directly check parties, roles, calculations, conditions, settlement and failure results. Integration and deployment have their own places rather than being traced during every business review.

For AI-modified member discounts, specialists follow Buyer tier, formula and quotation to verify applicability, percentage and shipping. Readable expressions map to requirements.

Humans supply rules, exceptions and expected results; AI expresses them as roles, services and scenarios; tools generate implementation. This collaboration lets business omissions be found directly instead of reconstructed from mixed code by technical staff.

Each business change focuses review on SPP and results; technical and operational changes are reviewed by corresponding specialists. Tool rules and validation protect repeated generated code, reducing exhaustive review of every generated line. Toolchain or adapter changes receive targeted review of their own behavior.

Reduced code also narrows review: people can see what business AI changed, why, and whether results meet requirements. Expression, deterministic generation and real validation together support quality control.

## Locate a Change in Its Layer

Membership discounts change SPP calculations; new customer systems change APP adaptation; production endpoints and connections change PHY.

Requirements specialists, developers, operators and AI have clear scopes, connected by shared contracts. Business stays readable, integration explicit and resources checkable. The following chapters introduce source expressions. Part V, Chapters 23–27, extends the benefits and technical services for performance, security, reliability and governance.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](../part-02-service-cooperation/11-deployment-granularity.md) · [Next Chapter](13-business-models.md)
