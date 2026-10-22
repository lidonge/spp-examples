# Chapter 27 — Runtime Governance and Technical Evolution

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

Correct models still need capability under variable load, dependency failure and migration. APP organizes tracing, throttling, isolation and recovery; PHY supplies deployment and monitoring. These facilities help detect, locate and handle problems.

## Traces and Metrics Locate Problems

Slow ordering may reflect product queries, stock settlement waiting or ordinary-save conflicts. “Order failed” alone identifies none.

Trace scenarios, domain calls, phases and recovery. Measure duration, errors, cache hits, version conflicts and pending requests. Distinguish settled quantum work, failed ordinary work and unconfirmed inverses.

Contracts answer what was bought, paid and processed; traces answer paths, failures and recovery progress. Correlation avoids exposing connections or threads as page business state.

## Add a Slow-Call Observer in Java

Suppose calls over 200 ms need a separate record. Add a technical service without changing scenarios. This example uses current TechnicalService (maintainer reference: `../../../appframe/src/main/java/com/servpp/service/technical/TechnicalService.java`) and TechnicalInvocation (maintainer reference: `../../../appframe/src/main/java/com/servpp/service/technical/TechnicalInvocation.java`):

```java
package example.technical;

import java.util.Map;
import java.util.logging.Logger;
import com.servpp.service.technical.TechnicalInvocation;
import com.servpp.service.technical.TechnicalService;

public final class SlowCallObserver implements TechnicalService {
    private long thresholdNanos;
    private Logger logger;

    public SlowCallObserver() {}

    @Override
    public void configure(Map<String, String> config) {
        long millis = Long.parseLong(config.getOrDefault("thresholdMillis", "200"));
        if (millis < 0) throw new IllegalArgumentException("Negative threshold");
        thresholdNanos = Math.multiplyExact(millis, 1_000_000L);
        logger = Logger.getLogger(config.getOrDefault("logger", "spp.slow"));
    }

    @Override
    public void handle(TechnicalInvocation event) {
        if (event.elapsedNanos() > thresholdNanos) {
            logger.warning("service=" + event.serviceName()
                + " phase=" + event.phase()
                + " elapsedMicros=" + event.elapsedNanos() / 1_000);
        }
    }
}
```

A public no-argument constructor is required. Registration calls configure; execution calls handle. Instances can receive concurrent calls, so do not store a request's start time or identity in shared fields. This example initializes threshold and logger once, and uses each event's data.

Put the class on the runtime classpath, then observe scenarios in APP:

```app
technical services { slowCall; }
intercept scenarios {
    after: slowCall;
    failure: slowCall;
}
```

Bind implementation and parameters in PHY:

```phy
phy {
    technical service slowCall {
        implementation: "example.technical.SlowCallObserver";
        config thresholdMillis = "200";
        config logger = "spp.slow";
    }
}
```

The same structure integrates metrics, traces and alerts; identity-based controls or throttling can choose before. Thread-pool isolation, cancellation and message transformation still need runtime or communication adapters, not observation alone.

## Interception Scope and Failure Meaning

All-service matching applies only to its declaring domain. A shop proxy and product provider are separate calls; observing provider internals requires product configuration. Declaration and phase-list order determines execution. Duplicate service-stage-technical-service matches fail compilation.

before may block invocation. after faults become diagnostics while later observers continue. failure faults attach to the original error while others continue, without replacing it. Logging failure cannot rewrite an already normally returned business result.

Method return also differs from commit. Quantum return may precede outer settlement; one scenario after cannot represent several sequential commits. Current interfaces have no independent commit callback. Execution records determine settlement and recovery.

Technical services are not registered as SPP atomics, avoiding recursion under all-service matching. Business completes activities; technical services surround calls with facilities.

## Throttling and Isolation Protect Resources

A slow external catalog can occupy connections and threads until other business suffers. Limits, deadlines and isolated pools reduce propagation.

Throttling limits admission rate, isolation separates resources, and circuit breaking pauses access to persistently failing dependencies. These improve handling but cannot interpret unavailable dependencies as missing goods or guarantee whole-business success.

Timeout ending page waiting does not stop background updates. Confirmation and execution status must cooperate with response-time policy.

## Degradation Must Preserve Meaning

Unavailable recommendations can be omitted and failed images replaced. Display adaptation can handle these.

Unavailable price sources cannot silently cause old-price settlement, nor payment faults mark orders paid. Agreements define optional output, acceptable cached facts and mandatory suspension. Technical methods honor business-approved outcomes.

Async notification is similar. Queues may carry notices, but an order-success promise cannot silently precede confirmed stock and funds. If business accepts now and processes later, SPP explicitly defines phases and contract states.

## Conversion and Environment Adaptation

Adapters normalize external field names, formats and number representations into agreed facts. Dates, serialization and compression can be shared.

A protocol change still supplies goods-role facts. Localization can use constants and resources. Currency conversion and rounding alter business amounts and are not mere formatting.

PHY supplies environment endpoints, storage, caches and keys. Operators configure existing capabilities; naming an unimplemented option does not make it work.

## Verify Evolution

Each change needs objectives and coverage. Caches require freshness/invalidation; durable guards concurrency/restart; transaction deployments commits/inverses/unknown results; security trusted identity and output protection.

Technical tests honor capability contracts while business tests retain calculations, qualifications and agreements. Separate reviews meet at shared requirements. Petstore next connects roles, services, scenarios and integration into complete practice.

---

[Part Contents](README.md) · [Full Book Contents](../README.md) · [Previous Chapter](26-reliability-services.md) · [Next Chapter](../part-06-petstore/28-petstore-modeling.md)
