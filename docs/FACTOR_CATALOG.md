# Responsible AI factor catalog (v0.1.0)

Factors are developer-configured controls, **not a certification or universal risk score**. This catalog distinguishes decisions this sample code can make on trusted metadata from human reviews it cannot perform.

| Factor | Type | Statuses | What it can establish | What it cannot establish |
| --- | --- | --- | --- | --- |
| Authorization | Reference enforcement | `PASS`, `BLOCK` | Trusted role/action, active actor, tenant, deny list | Identity authentication or provider-side access |
| Action limits | Reference enforcement | `PASS`, `BLOCK`, `NOT_APPLICABLE` | Action-specific numeric threshold | External transaction limits or fraud |
| Data handling | Reference enforcement | `PASS`, `BLOCK` | Classification tag is permitted | PII detection, minimization, lawful basis |
| Human oversight | Reference enforcement | `PASS`, `REQUIRE_APPROVAL`, `BLOCK`, `NOT_APPLICABLE` | Whether a rule needs approval; result of *supplied* verifier | Whether a human actually approved unless application verifier is trustworthy |
| Evidence | Minimal record | `INFO` | In-memory decision/factor record | Durable, authenticated, immutable audit trail |
| Fairness | Advisory | `NOT_EVALUATED` | Review item exists | Bias, fairness metrics or certification |
| Regulatory context | Advisory | `NOT_EVALUATED` | Review item exists | Applicable law or legal compliance |
| Transparency | Advisory | `NOT_EVALUATED` | Review item exists | Explanations or notices are sufficient |
| Organizational readiness | Advisory | `NOT_EVALUATED` | Review item exists | Real enterprise preparedness |

**Verdict precedence:** `BLOCK` > `REQUIRE_APPROVAL` > `ALLOW`. Advisory factors never silently change overall verdict to `PASS`; they remain explicit review gaps. An actual action must still be routed through `execute_guarded` or equivalent trusted host logic.

**Adding a factor:** implement `FactorFinding(factor, mode='ENFORCEMENT', status='PASS|BLOCK|REQUIRE_APPROVAL|NOT_APPLICABLE', reason='SAFE_CODE')`, register it when creating the kit, and add `{ "enabled": true, "description": "..." }` to the policy's `factors`. Invalid or crashing plugins deny in the sample engine.
