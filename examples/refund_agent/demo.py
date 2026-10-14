"""No network and no real transactions; demonstrates preventing executor calls."""
import json
from pathlib import Path
from trustelis_rai import ResponsibleAIKit, ActionNotAuthorized

root = Path(__file__).resolve().parent
policy = json.loads((root / "policy.json").read_text())
kit = ResponsibleAIKit(policy)

for name in ("request_allowed.json", "request_needs_approval.json", "request_blocked.json"):
    proposal = json.loads((root / name).read_text())
    executed = []
    def synthetic_executor():
        executed.append("SIMULATED REFUND ONLY")
        return {"status": "SIMULATED_SUCCESS"}
    try:
        decision, result = kit.execute_guarded(proposal, synthetic_executor)
        print(f"{name}: {decision.verdict}, simulator={result['status']}")
    except ActionNotAuthorized as error:
        print(f"{name}: {error.record.verdict}, simulator_called={bool(executed)}")
