# Chapter 8 — Reusing Services and Scenarios Through Role Polymorphism

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Individual purchases and corporate procurement involve different entities but may both query goods, calculate quotations, validate eligibility and place orders. Services tied to concrete entity types invite duplicate logic when a new purchasing subject appears.

Role-oriented services depend on business roles. If different entities satisfy those roles, existing calculations, validations and scenarios can be reused. Change primarily concerns how entities enter roles and provide facts; existing workflows continue with the same roles and rules.

## Role Polymorphism Makes Participants Replaceable

Object-oriented developers commonly use interfaces to accept different objects. Role polymorphism also admits different entities, but centers on the capacity in which they enter behavior. People and companies can be buyers; the same person can be a seller elsewhere.

A purchase scenario supporting both needs Buyer identity, delivery information and eligibility. Mapping personal and company names and retrieving delivery facts belong to role relationships and query completion. The scenario uses a prepared Buyer rather than separate individual and corporate scenarios.

“Playing the role well” means satisfying its facts and meaning: identity, property mapping, role-owned facts and rule inputs. Mapping the company name alone is insufficient. Other purchase facts must also be ready.

## Reusing Calculations on Role Facts

Line pricing needs agreed unit price and quantity. Food, toys and household goods can reuse it when their entities provide the same meaning of goods facts.

Kitten food at 60 US dollars for two units yields 120; toys at 30 for three yield 90. Entities differ but the formula is the same. Unit price and quantity belong to the role, avoiding multiplication and rounding implementations for every goods type.

Petstore `priceLine` calculates an OrderLine's amount; `quoteOrder` reuses it for quotation. Reuse occurs both between calculations and when different entities enter the same role. A new product capable of playing Goods can reuse line pricing and quotation.

Likewise, discounts use Buyer membership tier and order amount, without testing the buyer's natural entity type.

## Reusing Validation on Role Conditions

Validation expresses qualifications: positive purchase quantity, an unpaid order, or payer matching order buyer. These conditions concern roles, contracts and processing state.

A person buying two bags and a company buying twenty can use the same quantity check. It reads quantity without caring who supplied it. Payment eligibility can use the same Buyer-order relationship.

New entities can thus reuse existing validations. Scenarios call them in the same positions and branch on acceptance or rejection. Polymorphism reuses the rule; scenario organization preserves where it applies.

## Reusing an Entire Scenario

Scenarios organizing reused calculations and validations can themselves be reused:

```text
Confirm buyer and goods
          ↓
Validate purchase conditions
          ↓
Calculate line and order amounts
          ↓
Complete quantum transactions
          ↓
Further calculations and validations as needed
          ↓
Save complete business facts
```

Individuals and companies supply different entity facts; food and toys supply different product facts. After playing Buyer and Goods correctly, one scenario uses existing responsibilities to complete purchasing. Reuse covers whole behavior, not just a method or formula.

If quotation and ordering already support individuals, adding corporate procurement under the same prices, conditions and terms mainly requires the company to enter Buyer and provide facts. Quantity checks, line pricing, subtotal and saving remain reusable.

Roles connect reuse: entities satisfy roles, services use roles, and scenarios organize services. New entities can enter existing capabilities through existing roles.

## Distinguishing Participant Changes from Rule Changes

First identify where change occurs. Replacing an individual with a company under unchanged rules preserves existing services and scenarios. Adding approval, credit purchasing or exclusive prices changes rules, so introduce the required roles, validations, calculations or steps explicitly. Existing applicable services remain reusable.

Business expansion starts by locating existing roles and services, explaining how new entities play them, and adding genuinely new terms. Capability can admit new participants without repeating logic for each entity type.

Role polymorphism supports reuse of fine-grained services and scenarios. The next part discusses the call costs of fine granularity and distributed deployment, and how concurrency and merged requests reduce scenario response time.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](07-business-service-characteristics.md) · [Next Chapter](../part-02-service-cooperation/09-service-coordination.md)
