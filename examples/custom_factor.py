"""Custom factor plugin; illustrates a developer-defined enforceable policy."""
from trustelis_rai import FactorFinding, ResponsibleAIKit

policy = {
 "schema_version": "0.1", "use_case": {"id": "custom-demo", "name": "Demo"},
 "factors": {
   "authorization": {"enabled": True,"tenant_isolation": True,
                     "allowed_actions_by_role": {"developer": ["report.read"]}, "deny_actions": []},
   "allowed_region": {"enabled": True, "description": "Approved deployment region"}
 }
}

def allowed_region(req, config):
    # Region comes from the trusted application context, not LLM prompt output.
    if req.actor.get("region") != "eu":
        return FactorFinding("allowed_region", "ENFORCEMENT", "BLOCK", "REGION_NOT_AUTHORIZED")
    return FactorFinding("allowed_region", "ENFORCEMENT", "PASS", "REGION_MATCH")

kit = ResponsibleAIKit(policy, custom_factors={"allowed_region": allowed_region})
req = {"use_case_id": "custom-demo", "action": "report.read",
       "actor": {"id": "x", "role": "developer", "tenant_id": "a", "active": True, "region": "eu"},
       "target": {"id": "report-1", "tenant_id": "a"}}
print(kit.check(req).verdict)
