# Threat model — boundaries of this developer prototype

## Assets and authority

The sample evaluates developer-supplied proposed actions against trusted, structured **application context**: authenticated actor, tenant, target resource and data label. `untrusted_text`, model prompts and model outputs must never authenticate identities, supply approval receipts, determine authoritative resource ownership or modify policy.

## What v0.1.0 can exercise

- Unauthorized role/actions in a synthetic allowlist.
- Cross-tenant resource boundary in structured metadata.
- Hard-denied actions, invalid amount types and monetary caps.
- Human approval request routing and a demo external verifier hook.
- Restricted data classification based on a trusted pre-assigned tag.
- Minimal structured decision explanations with no raw payloads.

## What v0.1.0 does NOT secure

- Real user authentication, session management, tool credentials, provider Admin APIs or end-to-end agent execution.
- Provider-internal tools, calls that bypass the wrapper, asynchronous queues, retries, TOCTOU races, remote effects or multi-service transactions.
- Authenticated, scoped, revocable, replay-resistant approval records, two-person approval, segregation of duties or trusted read-back. The `approval_verifier` callback is a contractual trust boundary: a permissive verifier defeats approval protection.
- PII detection from raw text, data egress control, content safety classifiers, adversarial model security, fairness evaluation, regulatory applicability assessment or compliance certification.
- Persistent tamper-proof evidence, observability pipeline, incident monitoring or business continuity guarantees.

## Security rules

1. Keep policies on the application/server side and do not let LLMs modify them.
2. Supply actor and target context from authenticated trusted application services only.
3. Fail closed on unknown factor names, malformed inputs, missing mandatory facts, invalid approvals and plugin errors.
4. Treat `ALLOW` as *only this local reference preflight*, not an external provider guarantee.
5. Never send real customer data or secrets to example CLI JSON files or to a future provider test adapter.
6. Never pass a side-effectful callable to `execute_guarded` unless the application understands bypass and transaction risks.
7. Any future external product integration must validate actual provider capabilities before claiming enforcement.

If a security flaw is found, see [SECURITY.md](../SECURITY.md). Never disclose live credentials or exploit unrelated services.
