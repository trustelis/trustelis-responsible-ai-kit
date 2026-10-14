import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "examples/refund_agent/policy.json").read_text(encoding="utf-8"))

def request(action="refund.create", amount=25, role="support_agent", tenant="demo-company-a", target_tenant="demo-company-a", classification="internal", active=True):
    return {
        "use_case_id": "customer-refund-agent",
        "action": action,
        "actor": {"id": "staff-1", "role": role, "tenant_id": tenant, "active": active},
        "target": {"id": "refund-1", "tenant_id": target_tenant, "classification": classification},
        "parameters": {"amount_usd": amount},
    }

def policy():
    return deepcopy(POLICY)
