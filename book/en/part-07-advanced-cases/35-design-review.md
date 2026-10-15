# Chapter 35 — Architecture Review and Capability Boundaries

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Review meaning, composition and guarantees. Declarations help discover errors, but designers still judge whether concepts are real, rules complete and implementation honors contracts.

## Modeling Method and Architectural Approach Are Two Levels

“Role-oriented service architecture” contains two levels: role orientation is a modeling method; service architecture is an approach to organizing a system. For comparison, a service architecture based on object modeling may be called “object-oriented service architecture.” These names let us discuss modeling expressiveness separately from architectural scope. Object orientation can also support other architectures.

The service architecture in this book targets commercial business services. Purchasing, payment, reservations and shipping have explicit participating identities, processing rules and completion criteria, making them suitable for roles, services and scenarios. S++ delegates common queries, updates, conserved settlement and technical integration to tools, allowing business developers to express an activity with few declarations. This brevity comes from recurring domain structures and tool support; complex rules still need to be specified.

Fluid simulation, celestial mechanics and numerical solvers may instead focus on equations, discretization and error. Organizing those problems entirely as commercial services is usually inconvenient. A few business declarations cannot be expected to replace numerical algorithms. Task submission, resource allocation and result delivery in a scientific-computing system can use service architecture, while its solvers use expressions appropriate to their own domain.

When asking whether the architecture can meet requirements of arbitrary complexity, first distinguish a modeling method, a domain architecture and the capabilities already supported by the current language and tools. These are three separate questions.

## Simple Concepts Can Also Build Complex Role Models

Object orientation starts with entities: many stateful objects receive actions, and their interactions describe a complete process. Role orientation starts with behavior: many activities identify their participating roles, and compositions of behavior describe a complete process. A scenario can be understood here as behavior in the broad sense, organizing several behaviors toward a larger objective.

Both approaches express state, change and composition; their starting points differ. Role orientation does not remove entities or data structures. It understands them through the behaviors in which they participate. A complex process can be decomposed into subbehaviors, and participants into simpler structures. Modeling can continue as long as each level has explicit state, rules and composition relationships.

A chess game, for example, can begin with board and piece objects that provide move methods. Alternatively, it can begin with moving behavior and identify the player, selected piece and board as participating roles, then organize alternating moves, position evaluation and game termination. The board still holds the position and pieces still have locations; behavior becomes the organizing thread.

Role-oriented modeling is therefore not inherently limited to commercial activities. For processes describable by state and computable rules, both approaches can extend through composition. Expressing a process, expressing it concisely and executing it efficiently are different questions. Appendix A8–A9 gives a constructive argument and its conditions.

## Comparing the Starting Points with a Hash Table

A hash table shows why simple foundational concepts can compose into complex structures and algorithms.

Object orientation typically begins with a hash-table object. It holds a sparse storage table and offers `put(key, value)` and `get(key)` methods. The methods calculate positions, handle collisions, save records and find them. We first see what a hash table is and what it can do.

Role orientation can begin with “hash storage” behavior and identify three participating roles: a key used for lookup, a value to store and a sparse table providing storage. A particular string or identifier can play the key, a record the value, and a concrete structure the sparse table. The behavior explains their cooperation:

```text
Hash storage (key, value, sparse table)
1. Calculate a candidate position from the key and table capacity.
2. Check whether that position already contains the same key.
3. If so, replace its associated value.
4. If another key occupies it, continue under the collision policy.
5. At an available position, save the key and value.
```

This is a modeling illustration, not executable current SPP syntax. Collision handling could use open addressing. Resizing can introduce behaviors for allocating a new table, migrating records and switching storage. Complexity remains, carried by explicit cooperating behaviors.

“Hash lookup” takes a key and sparse table, follows the same hashing and collision rules, and returns the found value or a not-found result. Storage and lookup must share these rules, or a successfully stored value might never be found.

For example, with capacity eight, let an integer key's initial position be its remainder on division by eight. Key 10 first checks position 2; key 18 also checks position 2. If key 10 occupies that position, a policy that searches forward for a free slot stores key 18 at position 3. Looking up 18 must likewise start at 2, compare the key and continue to 3. Object methods and role behaviors can both express this process.

Key and value are algorithmic participating roles here. They need not be declared as SPP business Roles, nor must every probe become a remote service. This example concerns role orientation as a foundational modeling method. Part III's business roles, atomic services and scenarios are its domain-specific constraints and applications in commercial service systems.

## Reusing Object Implementations for Complex Algorithms

If needed, a general-purpose language could be built around role orientation, providing further expressions for data structures, algorithm composition and execution. Current S++ focuses on commercial business services. Demonstrating the modeling method does not require reimplementing every general computing facility.

Object orientation has already produced extensive data structures and algorithms. Role modeling can reuse these achievements: the business layer states required capabilities and results, APP declares bindings or adapters, and PHY supplies Java implementations and runtime resources. A complex Java object can internally use hash tables, graphs or numerical algorithms while exposing a clear capability contract.

For example, a delivery quotation may calculate distance from prepared locations and a route network. The business layer explains how distance affects pricing; a technical adapter can reuse Java route-search code. Another search algorithm can replace it without changing quotation rules if input, distance meaning and accuracy remain satisfied. Membership discounts, delivery eligibility and who bears the fee remain in SPP.

This integration needs the appropriate calculation or data-adapter interface. The `before`, `after` and `failure` interceptors in Part V receive invocation metadata only. They cannot replace route calculations or rewrite business participants. This discussion identifies the architectural location of complex implementation bindings in APP; actual binding forms depend on the interfaces provided by the implementation.

Complex requirements can thus be divided between explicit business models and reusable technical implementations. Their complexity does not require algorithms, data structures and deployment details all to enter the business language. Review whether responsibilities are clear, composition complete and each layer fulfills its contract.

## Review Model Meaning

Each role explains player, behavior and own facts. Each contract identifies activity, parties and terms. Fields have owners and purposes; business credentials and technical identity have their places.

List-wrapper roles and generic-return contracts need reconsideration. Independently maintained duplicate properties need explicit ownership.

## Review Composition

Services need clear duties; scenarios understandable dependencies and completion. Before parallel, check inputs, read/write conflicts and failure joins; before transaction, scope/resources; after phased execution, recovery owners.

Ordinary check failure is not automatic rollback; REQUIRED is not separate commit; co-location does not change domains; remote failure does not prove no transaction occurred. Explain these concrete effects.

## Review Benefits and Costs

Roles and declarations reduce mixed logic but concentrate mapping, metadata and plans in tools/runtime. Teams must maintain them and understand output.

Simple business may not justify extra layers. Multiple-party cooperation, complex rules, conservation and environments benefit from explicit contracts. Decide according to real team/system needs.

## Review Evidence Levels

Parsing proves accepted expression, compilation checked artifacts, running tests exercised paths, and faults/restarts specific recovery conditions. Performance also needs workload/resources.

Separating levels avoids claiming all reliability from one build. Maintain limits with versions so promises match capability.

## Keep Architecture Explainable

Trace each activity through identity, behavior, contract, ownership and result. Locate unfinished phases on failure, responsibility on change and critical paths on optimization.

This book connects participants and behavior through roles/services into scenarios, then APP/PHY into running systems. That connection also guides continuous review and evolution.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](34-migration.md) · [Next Chapter](../appendices/a-service-model.md)
