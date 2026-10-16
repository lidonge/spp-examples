# Introductory post drafts

These are ready-to-adapt drafts, not evidence of external publication. Share through an owner-approved account after the linked pages are live. They introduce an experimental language and invite evaluation rather than promising production readiness.

## Project introduction

I am developing S++ (ServPP), a role-oriented language for business systems. It describes participants, checks, calculations, updates and transaction boundaries, with deployment and storage choices in separate APP and PHY definitions.

The public site includes an English book and browsable source for a Petstore lifecycle and selected banking deposit transactions. I am looking for feedback from engineers who maintain complex business workflows: which rules are hardest to keep visible in your current implementation?

https://us.servpp.top/

## Business facts and storage

An old order should keep its accepted name and price when the product catalogue changes. That small requirement exposes a larger modeling question: which facts belong to a business role, and which choices belong to persistence?

This article uses the S++ Petstore model to explain participant associations, storage-only keys and order-time snapshots, with links to the actual definitions.

https://us.servpp.top/articles/business-logic-and-database-design/

## Roles and the order lifecycle

A person can act as a buyer; a product can participate as goods and then as an order line. S++ makes those roles explicit instead of sending a generic command and a large shared context through one workflow.

Here is a practical walk through participants, shared checks and independent business scenarios in the Petstore demonstration. The language is still in development, and feedback on the model is welcome.

https://us.servpp.top/articles/role-oriented-order-lifecycle/

## Transactions and business failure

An accepted reservation can remain a useful business fact even when inventory cannot be reserved. Erasing the entire interaction is not always the right outcome.

This S++ example uses separate transaction boundaries and explicit failure handling to preserve the application and record rejection after recovery. The article also distinguishes local rollback, reverse financial operations and business compensation.

https://us.servpp.top/articles/business-transactions-and-infrastructure/
