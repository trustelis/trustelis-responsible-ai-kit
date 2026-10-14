"""Example only: a fake trusted application store, not real signed approvals."""
import json
from pathlib import Path
from trustelis_rai import ResponsibleAIKit, ActionNotAuthorized

root = Path(__file__).resolve().parent
kit = ResponsibleAIKit(json.loads((root / "policy.json").read_text()))
request = json.loads((root / "request_needs_approval.json").read_text())

# In reality: call a server-side approval service to verify a non-revoked
# independently authenticated receipt bound to this exact actor/action/target.
# This fabricated in-memory fixture is NOT proof of a human approval.
trusted_demo_store = {("synthetic-staff-7", "refund.create", "synthetic-refund-15"): True}

def demo_verifier(req):
    return trusted_demo_store.get((req.actor["id"], req.action, req.target["id"]), False)

rec, result = kit.execute_guarded(request, lambda: "SIMULATED ACTION EXECUTED", approval_verifier=demo_verifier)
print(rec.verdict, result)
