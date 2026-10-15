# Chapter 22 — Generation, Physical Resources and Runtime Configuration

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Declarative models must become executable code, interfaces, repositories and resource access. Generation performs this conversion and checks model-implementation contracts. Reading output reveals declarations' effects.

## From Models to Runtime Artifacts

The compiler parses models, calls, role relationships and boundaries, combines APP/PHY, and generates Java models, services, mappings, OpenAPI, DDL and runtime catalogs according to module and configuration.

This supports Part III, Chapter 12: AI mainly maintains SPP, APP and PHY while tools deterministically generate repetitive models, interfaces and integration. Fewer free implementation choices mean fewer consistency relationships for AI to maintain manually.

Business review focuses on roles, rules, scenarios and actual results. Toolchain changes receive their own generation checks instead of reviewing all mixed code on each business change.

Business source stays in source directories; generated Java is in target. Direct changes to generated files affect only one build and may be overwritten. Maintain rules in SPP and source configuration.

## Generation and Startup Checks

Generation detects undefined facts, ambiguous binding, illegal calls, unsupported propagation and contradictory resources. Startup checks actual override parameters, environments, identities, provider contracts and readiness.

Static checks do not prove current remote settlement capability, and startup does not replace concurrency or fault tests. Each supplies different evidence.

## Build and Local Demonstration

Run at repository root with the documented JDK 17, Maven and dependencies:

```bash
mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=develop
SPP_PETSTORE_JDBC_URL='jdbc:h2:file:/tmp/spp-book-petstore' \
  ./demos/petstore/run-demo.sh web
```

The web demo defaults to 8086. This uses an independent experimental database; reusing the path retains old data. Appendix E provides variables and multiprocess commands.

## Numbers and Resources

PHY selects representation and capacity; APP organizes technical mappings. SPP specifies rounding; inexact unsupported conversion must fail rather than silently alter meaning.

develop and testing can use different deployments and plans for one scenario. Compare selected environment, generated catalog and startup arguments rather than using artifacts from one to prove another.

## Verify That Declarations Are Honored

A successful build establishes source-generation checks, not actual business completion. Execute scenarios and verify results. The later Petstore practice follows requirements through fund and stock movement to show the architecture as a complete system.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](21-recovery.md) · [Next Chapter](../part-05-business-and-technology/23-separation-benefits.md)
