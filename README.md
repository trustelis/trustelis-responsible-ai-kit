# TRUSTELIS Responsible AI Kit

**Control Before AI Acts.**  
**Add transparent Responsible AI factors to your AI application's action path.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
![Status](https://img.shields.io/badge/status-early%20prototype%20v0.1.0-yellow)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)

A standalone, **offline-first, provider-neutral Python developer kit** for trying Responsible AI controls on **proposed tool actions**. Describe your AI use case with a JSON policy, select the factors you need, and obtain one of three clear preflight outcomes:

- `ALLOW` — locally configured checks passed.
- `BLOCK` — a concrete rule denies the proposed action.
- `REQUIRE_APPROVAL` — an independent, trusted human approval is required.

The **Control Card** lists each configured factor and its actual mode: enforceable *inside this reference wrapper*, advisory review only, or minimal in-memory record. There is **no made-up compliance score** or silent substitution of unimplemented checks with success.

> **Scope: early developer prototype, not a production authorization engine or compliance product.** A model cannot authorize itself. You must construct actor, tenant, target, and data classification from trusted application systems. `execute_guarded` wraps only actions intentionally routed through it and does not control bypass paths, third-party AI providers, or actual transactions. Human approval depends on your own trustworthy verification integration. This project does not certify EU AI Act or other legal compliance and does not prove prevention of real-world attacks.

## Real developer problem this solves

A developer builds an AI-powered **refund agent**. A model can suggest `refund.create` even when the requesting employee lacks permission, the refund exceeds a limit, or a human must approve it. This kit provides an explicit *application-side* decision and a small, non-sensitive record **before your callable is invoked**.

### Example: run in under a minute — without API keys

Python 3.11 or later. Nothing is sent to a network endpoint. Clone or extract the public source package and run from its root:

```bash
# Zero dependencies for the offline examples
PYTHONPATH=src python -m trustelis_rai validate --policy examples/refund_agent/policy.json
PYTHONPATH=src python -m trustelis_rai card --policy examples/refund_agent/policy.json --format markdown
PYTHONPATH=src python -m trustelis_rai check --policy examples/refund_agent/policy.json --request examples/refund_agent/request_allowed.json
PYTHONPATH=src python examples/refund_agent/demo.py
```

On Windows PowerShell, use a single command without changing the machine's execution policy:

```powershell
$env:PYTHONPATH="src"; py -3 -m trustelis_rai card --policy examples/refund_agent/policy.json --format markdown
```

Or install into your normal Python environment: `pip install .` then use `trustelis-rai card --policy ...`.

### Developer API

```python
import json
from pathlib import Path
from trustelis_rai import ResponsibleAIKit, ActionNotAuthorized

policy = json.loads(Path("examples/refund_agent/policy.json").read_text())
kit = ResponsibleAIKit(policy)

# MUST come from trusted application identity and resource metadata, not the model.
request = {
    "use_case_id": "customer-refund-agent",
    "action": "refund.create",  # Action proposed by an agent, validated by app
    "actor": {"id": "staff-7", "role": "support_agent", "tenant_id": "company-a", "active": True},
    "target": {"id": "refund-12", "tenant_id": "company-a", "classification": "internal"},
    "parameters": {"amount_usd": 75}
}

try:
    record, result = kit.execute_guarded(request, lambda: "SIMULATED REFUND")
except ActionNotAuthorized as exc:
    print(exc.record.verdict)  # REQUIRE_APPROVAL (no executor called)
    print(exc.record.as_dict())
```

**Never** call your real tool outside your application's approved execution path. This sample is not a guarantee that other routes are secured. For a positive example using a simulated trusted verifier, see [`examples/refund_agent/trusted_approval_demo.py`](examples/refund_agent/trusted_approval_demo.py).

## Responsible AI factors in v0.1.0

| Factor | Mode | Actual capability |
| --- | --- | --- |
| Authorization | Reference preflight | Role-to-action, deny list, active identity and same-tenant boundary; **mandatory** |
| Action limits | Reference preflight | Finite nonnegative amount and action-specific hard caps |
| Data handling | Reference preflight | Enforcement of *trusted preassigned data labels*; does not discover PII |
| Human oversight | Reference preflight | Marks actions requiring approval; optional **application-owned** independent verifier |
| Evidence | In-memory only | Minimal decision record, policy fingerprint, factor reasons; not a tamper-proof audit log |
| Fairness | Advisory | `NOT_EVALUATED`; no statistical fairness result without suitable data |
| Regulatory context | Advisory | `NOT_EVALUATED`; does not determine legal applicability |
| Transparency | Advisory | `NOT_EVALUATED`; notices/explanations need independent review |
| Organizational readiness | Advisory | `NOT_EVALUATED`; cannot infer enterprise readiness from a tool call |

You can **disable** optional factors in the JSON policy; the Control Card will show `DISABLED`. Developers can add custom enforcement factors without modifying the core — see [`examples/custom_factor.py`](examples/custom_factor.py). Unknown policy factors or unsafe configuration are rejected instead of being ignored.

## Example decisions

| Request | Preflight result | Reason |
| --- | --- | --- |
| Refund $25, correct role/tenant | `ALLOW` | No approval needed, amount within cap |
| Refund $75, no verified approval | `REQUIRE_APPROVAL` | Approval threshold exceeded |
| Refund $20, wrong tenant | `BLOCK` | Tenant isolation boundary |
| Refund $125 | `BLOCK` | Hard spending limit, even if approval exists |

The CLI returns exit code `0` for `ALLOW`, `4` for `REQUIRE_APPROVAL`, `5` for `BLOCK`, and `2` for invalid configuration/request. This allows a developer to fail a build or demo on non-allow results without accidentally treating review as success.

## Provider independent, intentionally

No OpenAI, Anthropic, Microsoft or Google credentials are required. This kit does **not** claim access to provider Admin APIs. `ActionRequest` is an application-side contract; real provider adapters, durable signed approvals, trustworthy identity context, threat monitoring and organization-wide policy management are outside v0.1.0.

## Architecture and separation from commercial TRUSTELIS

This is **new, independently written, general-purpose open source**. It is not the proprietary TRUSTELIS Policy Rules Engine, Runtime Gateway, AI Use Case Builder or Trust Pack implementation. It contains no copies of private repository source, business data, Cloudflare credentials or customer policies.

- **Responsible AI Kit:** developer-side local reference factors, preflight wrapper, Control Card.
- **AI Agent Security Benchmark:** independent synthetic evaluation and model-decision scoring in the existing repository.
- **TRUSTELIS AI Control Platform:** separate proprietary, enterprise-level governance and authority for organizational policies, tasks, approvals, control blueprints, capabilities, budget and evidence.

If a future paid SaaS integration is developed, organizational policy decisions must remain authoritative in the SaaS; this open-source reference engine must never silently become an alternative organization-wide policy authority.

## Further reading

- [`docs/FACTOR_CATALOG.md`](docs/FACTOR_CATALOG.md) — statuses and responsibilities.
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — attack surfaces and explicit limits.
- [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) — custom factors and trusted approval integration.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — proposed next steps, not delivered functionality.
- [`docs/OPEN_SOURCE_BOUNDARIES.md`](docs/OPEN_SOURCE_BOUNDARIES.md) — proprietary separation.
- [`SECURITY.md`](SECURITY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

Copyright 2026 TRUSTELIS LTD. Apache License 2.0. **TRUSTELIS** brand names and logos are not licensed under Apache 2.0. Not endorsed by any AI provider.
