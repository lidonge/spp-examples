# Chapter 25 — Encryption, Fingerprints and Security Services

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Correct rules also require trusted requests, protected data and traceable operations. APP organizes authentication, encryption, integrity and output control; PHY supplies protocols, keys and resources. Scenarios operate on trusted business facts.

## Protect Transfer and Storage

Customer addresses may travel across domains and be stored. Integration can protect transport and select field encryption without business handling ciphertext, key choice or decryption calls.

Transport and at-rest encryption have distinct scopes and do not replace each other. Specialized facilities manage keys; PHY supplies endpoints and configuration. Rotation and upgrades affect adaptation while meaning stays stable.

Authentication and decryption may precede business; output encryption follows. Technical ordering has its own dependencies and is not arbitrarily exchangeable because business atomics can be concurrent.

## Fingerprints Identify Content; Integrity Protection Verifies It

A content fingerprint is a normalized digest for detecting change. A request number first transferring 100 and later 200 is not a retry; comparing facts or fingerprints detects the conflict.

Cover relevant content, including parties, not just amount. Consistent normalization avoids treating reordered fields as changed business. Identity identifies the call; fingerprint checks its content against the original.

A plain digest does not authenticate a sender or stop an attacker replacing both content and digest. Use authenticated message checks or signatures when protection requires origin and integrity. SPP receives verified facts; integration establishes trust.

Biometric fingerprints also belong to authentication. If business explicitly requires verified identity, that qualification and result enter business rules. Means and eligibility have separate places.

## Authentication, Permissions and Business Eligibility

Authentication establishes who calls, access control what entries and data they may access, and business validation whether this activity is eligible.

A logged-in buyer may query only authorized orders. Refunds additionally check ownership, delivery and deadlines. APP supplies trusted identity and protection; SPP expresses relationships and qualifications.

A submitted Buyer object is not proof of its identity, and a browser duplicate marker is not authentication. Integration verifies origin and binds trusted identity to participants before business processing.

## Technical Access Control with before

An internal entry may accept only specified verified callers. A Java technical service reads trusted headers in before and rejects unauthorized calls before business starts. APP selects entries, PHY selects implementation, and SPP needs no technical identity code.

before failure prevents invocation and enters failure with the original technical error. Trusted headers must already be established by authentication; arbitrary user values cannot become credentials. Ownership and payment eligibility remain SPP checks.

Current metadata excludes addresses, amounts and message contents. Field encryption, content fingerprinting and masking need data or communication adapters. Interception can audit calls, but committed-transaction evidence must also use transaction/storage records.

## Output Control and Audit

Order details may show a telephone number while lists show a masked one. APP can combine permissions, selected fields and masking, including logs and replay rather than only normal responses.

Technical audit records callers, entries, verification and traces. Business contracts record parties, amounts and processing results. Correlated identities support distinct safety and business inquiries without exposing keys or unnecessary sensitive facts.

Facilities can serve many scenarios, but algorithms, key management, authentication and permissions require implementations and scope verification. This chapter does not assume all security infrastructure is built in.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](24-performance-services.md) · [Next Chapter](26-reliability-services.md)
