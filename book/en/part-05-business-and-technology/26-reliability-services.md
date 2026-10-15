# Chapter 26 — Idempotency, Duplicate Guards and Reliable Execution

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Repeated clicks, communication retries and lost confirmation can deliver payment requests more than once. Reliability identifies their relationship to original business so duplicate transport does not duplicate debit. APP defines strategy; SPP retains qualifications, amount and outcome.

## Idempotency Identifies the Same Request

A 100-dollar payment may settle without its response reaching the page. Retrying the same identity and content should restore the result, not debit again.

Current remote-update protocols identify caller, caller serial and target service. Identical content replays original participant facts and result; changed amount or payee under the same serial conflicts. Registration tracks running, completed and recovery-needed requests, not just a seen flag.

An order number and technical request serial differ. One order has many processing activities; a retry must retain the original call identity. New serials on every retry prevent recognizing the same payment.

## Duplicate Guards Identify Repeated Operations

Transport idempotency concerns one request; UI guards also catch similar clicks with different serials. Repeated “add to cart” may be one accidental action.

APP declares identity keys, facts and a window, such as buyer, goods and quantity. After expiration, another addition can be legitimate; rejection must not be permanent.

Whether an order can be paid again is SPP business eligibility. Expired technical windows do not make it payable or imply no previous settlement. Both protections cooperate.

Current remote idempotency and UI guards are separate. Local calls do not repeat transport registration; quantum deduplication belongs to its backend. Queries do not replay through the update protocol; query caches are distinct. See [call idempotency](../../references/app-call-idempotency-and-duplicate-guard.md).

## Optimistic Locking Protects Competition Between Different Requests

Two legitimate profile edits may share stale facts without being duplicates. Conditional updates compare query baselines and reject overwrites after new versions. Quantum services apply deltas and actual bounds.

Deduplication, versions and quantum settlement protect repeated calls, competing replacement and quantitative change respectively. One duplicate key cannot replace all three.

## Confirm Outcomes Before Retrying

Timeout may mean uncommitted work or lost confirmation of committed work. APP queries original execution or retains recovery status. Repeating an entire uncertain scenario can duplicate debit or acceptance.

Confirmed full restoration with no independent stage committed may permit retry. Partial or unknown completion needs continued original recovery. Quantum inverses are automatic; ordinary restoration follows version contracts; business handling follows rules. Part IV, Chapter 21, distinguishes them.

Retries need deadlines, limits and backoff. Exhaustion does not create a compensation policy; preserve evidence and enter defined technical handling.

## Interceptors Observe; Execution Protocols Confirm

Java services can correlate request identity, target and failures. Scenario entry events may include idempotent replay; if replay does not execute atomics, it produces no repeated atomic execution events.

Two entry events do not prove two debits; atomic after does not prove outer commit. Registration, journals and receipts establish actual duplication.

Current after/failure are observation stages, and failures do not replace original results/errors. There is no arbitrary retry, result mutation or independent commit callback. failure must not simply rerun payment. Execution protocols retain confirmation and reversal responsibility; interception supplies diagnostics.

## Durable Records Survive Restart

Memory-only registration can forget requests after restart. Required update recovery uses durable identities and results coordinated with actual settlement.

The framework supports memory and JDBC stores with different capabilities. Unknown or partially committed records cannot expire into brand-new requests. Split zero creation also uses durable technical tasks rather than new business compensation. Central strategies keep scenarios focused on results rather than rewritten retry protocols.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](25-security-services.md) · [Next Chapter](27-operations-and-evolution.md)
