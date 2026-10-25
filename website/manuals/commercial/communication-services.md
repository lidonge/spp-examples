# Communication and identity technical services

The paid extension `com.servpp:appframe-channels:1.0-SNAPSHOT` provides reusable
provider adapters originally developed for ServPP. All classes below use package
`com.servpp.service.channels`. Commercial generated projects include this runtime
dependency. Hand-built applications can add it explicitly:

```xml
<dependency>
  <groupId>com.servpp</groupId>
  <artifactId>appframe-channels</artifactId>
  <version>1.0-SNAPSHOT</version>
</dependency>
```

The open Basic distribution contains no implementation or reverse dependency on
this module. Third-party replacements continue to use Basic's open contracts.
These services are explicitly bound through PHY; there is no global provider
registration, automatic outbound traffic or additional membership enforcement in
the runtime. Application eligibility and authorization stay in SPP.

## SMTP notifications and email challenges

Bind `SmtpEmailService` through `TechnicalRequestService`. Configuration requires
`simulationMode=LIVE`, `credentialsFile` and `datasourceUrl`. The current configured
store uses H2; include its JDBC driver in the application. Alternatively construct
`SmtpEmailService(DataSource, Sender, byte[], Clock)` with an application-owned
sender, HMAC key and clock. Other database dialects are not certified.

A PHY binding has this shape:

```text
domain application;
phy {
    technical service email {
        implementation: "com.servpp.service.channels.SmtpEmailService";
        config simulationMode = "LIVE";
        config credentialsFile = "${application.smtp-file}";
        config datasourceUrl = "${application.email-store}";
    }
}
```

Declare and invoke the matching technical service through your APP participant
adaptation. Bindings do not authorize arbitrary callers to send messages. Resolve
the recipient and allowed purpose from trusted application state first.

The private JSON credentials file contains `host`, `port` (587), `username`,
`password` (24–256 printable ASCII characters), `fromAddress`, `replyTo`, `enabled`
and `challengeKey` (Base64 encoding of 32 random bytes). Store it outside source
control. On POSIX, require mode 0600 inside a 0700 directory; symbolic links are
rejected. The SMTP transport requires STARTTLS, server certificate/hostname
verification and authentication. Credentials and provider diagnostics are not
included in delivery errors. Email display names and EHLO no longer identify the
ServPP platform; EHLO uses the configured sender domain.

| Operation | Input fields in addition to `operation` | Result |
| --- | --- | --- |
| `startVerification` | `clientReference`, `to`, `purpose` | `reference`, `emailAddress`, `status=PENDING` |
| `checkVerification` | `reference`, `code` | `approved`, `emailAddress`, `purpose` |
| `cancelVerification` | `clientReference`, optional `reference` | `cancelled` |
| `send` | `messageId`, `to`, `subject`, `text` | `status=ACCEPTED` |
| `lookupDelivery` | `messageId` | `status=ACCEPTED` or `UNKNOWN` |

References are 1–160 ASCII letters, digits, underscores or hyphens. Purposes start
with an ASCII letter and contain at most 40 letters, digits, underscores or
hyphens. The reusable adapter validates syntax; it does not define business
purposes. The platform compatibility adapter keeps its existing purpose allowlist.

Challenges contain six random digits, expire after five minutes, lock after five
failed attempts and approve only once, including concurrent checks. Only an HMAC
of the code is persisted. Reusing a request reference with different content is
rejected. An ambiguous SMTP acknowledgement remains `UNKNOWN` and is not blindly
resent. `ACCEPTED` means SMTP acceptance, not inbox delivery. A new reference may
produce another email, so callers must apply their own request authorization and
rate limiting. Successful, cancelled, expired or locked challenges clear their
recipient, purpose and code MAC. Technical request rows are retained; there is no
generic retention scheduler in this module.

The legacy table name `PLATFORM_SMTP_REQUESTS` is deliberately retained so existing
stores can reopen without migration. Use a separate store per application: no
tenant isolation is implied by a shared JDBC URL. Keep the HMAC key stable across
restarts; key rotation for outstanding challenges is not implemented.

## Twilio Verify SMS

`TwilioSmsTechnicalService` implements the same request contract. Configure
`credentialsFile`, or explicit `accountSid`, `authToken`, `serviceSid` supplied by
secure configuration. File configuration accepts those three fields and validates
private file permissions. The legacy `registrationEnabled` flag is preserved for
platform configuration compatibility; the adapter itself never registers users.

- `start`: supply `phoneNumber` in international form.
- `check`: supply the original `reference`, original `phoneNumber` and `code`.
- Results contain `reference`, normalized `phoneNumber`, `status`, `simulated=false`.

`SmsVerification` also exposes the typed `start`/`check` protocol for custom
providers. `TwilioSmsVerification` validates account, service, phone and verification
reference correlation. Timeouts, throttling, missing or ambiguous provider results
remain `UNKNOWN`; they do not prove approval. HTTP redirects are disabled. The
application owns recovery/retry policy, country eligibility and user activation.
The extension does not impose the platform's registration country restrictions.

## Google OIDC

Configure `GoogleOidcService` with `clientId`, `clientSecret`, `redirectUri`.
Redirects require HTTPS except localhost/127.0.0.1 development callbacks.

- `authorizationUrl`: `state`, `nonce`, `codeChallenge` returns `url` using S256 PKCE.
- `exchange`: `code`, `codeVerifier`, `nonce` returns verified `issuer`, `subject`,
  `email`, `emailVerified=true`.

The adapter verifies Google's token signature, audience, token validity, nonce,
authorized party and verified email. The application must generate and persist
one-time state/nonce/PKCE verifier, validate callback state, consume the attempt
once and decide account association in SPP. This is a protocol adapter, not a
complete browser login/session implementation. Secrets should come from an
application-owned secret source, never literal committed PHY configuration.

## Supporting primitives

- `ContactSyntax`: phone normalization and numbering-region facts; email syntax
  normalization. Neither proves ownership, residence nor eligibility.
- `PrivateConfigurationFiles`: fail-closed credential file/parent permission and
  symbolic-link checks (POSIX or supported Windows ACLs).
- `Ed25519JwtSigner`: signs the caller's exact claims as an EdDSA JWT. It does not
  decide claims, add expiry, authorize users or verify incoming tokens. Callers
  must supply already-authorized claims, including issuer/audience/time limits.
- `SmtpConfiguration`, `SmtpMailSender`, `TwilioConfiguration`: typed setup and
  direct provider access for applications that do not need JSON adaptation.

## Compatibility and deployment limits

The platform depends on this module. Its original `GoogleOidcService`,
`TwilioSmsTechnicalService` and `SmtpEmailService` class names remain thin adapters
for existing PHY configurations. Other Java users migrate imports from
`com.servpp.platform.technical` to `com.servpp.service.channels`.

No live SMS, Google authorization or email delivery is exercised by the extraction
acceptance tests. They use synthetic keys, local databases and simulated provider
responses. Production credentials, DNS, provider accounts and deployment are
application responsibilities. Existing commercial terms and Basic licensing do
not change as a result of this extraction.
