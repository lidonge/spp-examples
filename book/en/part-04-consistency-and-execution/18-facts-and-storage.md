# Chapter 18 — Business Facts, Participant Identity and Storage Ownership

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Buyer may contain customer name, membership tier and wallet balance, but these facts need not share a storage owner. Queries complete them; saves respect their respective ownership.

## Borrowed and Owned Facts

Customer name is borrowed through role playing and maintained by the customer domain. Tier belongs to Buyer; wallet settlement belongs to quantum storage. Ordinary role insert, update and delete write only their own table, without cascading to players.

This prevents goods updates altering products and cart saves implicitly modifying buyers. Entity maintenance is explicit through the original domain's services.

## Contracts Retain Settlement Facts

An order for “Kitten Food 1kg” must retain that name after the merchant renames it “Kitten Formula Food 1kg.” Current product pages show the new name; the old order describes what was purchased.

Current names and agreed contract names have different duties. Order queries must not overwrite historical names from today's products. APP storage and mapping configuration implements this requirement; ordinary role relationships alone do not imply it.

For example, a bank's failure-disposition record must preserve the deposit or reversal contract at the time of failure, including the system-provided cause, service, phase and recovery status. Saving only an association and later querying current facts can change the record's meaning as balances or contracts change.

APP `snapshot` now preserves explicitly declared associated participants and collections as historical snapshots. Queries do not continue filling those snapshot subtrees through role or association chains, and current quantum balances do not overwrite historical balances inside them. Ordinary live associations still follow their normal completion rules. APP configuration distinguishes these uses; see the [bank snapshot verification](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/latest-refactoring-verification.md).

## Identity Is Not the Whole Fact Set

Wallet and name may change while buyer identity remains. APP locates participants through keys, business credentials or combinations. Comparing all facts serves other questions, such as changes in candidate content.

The compiler supplies business-invisible entity keys, maintained by internal metadata, avoiding habitual business id fields. Real order and membership numbers enter the model through their actual use. Versions, duplicate keys and repository location each have technical responsibilities.

## Query Completion and Baselines

Queries and updates are built-in. APP/PHY determine completion, baseline recording and version comparison; scenarios arrange calls and rules.

Queries can retain an internal baseline for later saving. Version protection compares the version originally queried, rather than reading a fresh version immediately before overwriting a competitor.

If another request modifies facts during candidate calculation, saving reports conflict. This shortens lock time but requires explicit rejection when baseline is missing or identity changed.

## Master-Detail

An order is Master; each line is Detail, recording quantity and agreed unit price. Cart and cart lines use the same structure.

The example preserves detail identities and completes members and related participants via query metadata. Saving Master does not replace explicit insertion, modification or deletion of Details.

Ordering explicitly deletes old cart lines, inserts agreed order lines and saves order and cart. Visible operations identify ownership rather than treating the whole aggregate snapshot as freely overwritable.

## The Lifecycle of Zero Facts

Establishing zero quantum facts differs from crediting nonzero funds. Account opening prepares storage for future transfers; funding requires conserved quantum settlement.

With role and quantum facts in one database, a common local transaction establishes them. With split storage, the built-in runtime commits role records and a durable technical recovery task locally, then creates remote zero records after confirmation. Local rollback removes both. Remote unavailability or lost responses retain the task for retry. Retry creates only missing zero records, never overwrites settled values, and produces no quantum transaction journal entry.

Scenarios still call role insertion without manually splitting opening or writing business compensation. Opening is not fully successful before remote zero records exist. The current mechanism covers built-in JDBC ordinary and quantum repositories; see [split zero-record recovery](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/quantum-opening-recovery.md).

Every fact should have an owner, locator and maintenance entry. See the [transaction and storage specification](../../references/transaction-storage-v1.md).

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](../part-03-the-spp-language/17-scenarios.md) · [Next Chapter](19-transactions.md)
