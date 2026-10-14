"""Built-in Responsible AI factors. Reference controls, not a compliance certification."""
from __future__ import annotations

import math
from typing import Callable

from .models import ActionRequest, FactorFinding
from .policy import ADVISORY_FACTORS

APPROVAL_CHECK = Callable[[ActionRequest], bool]


def _value(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finding(name: str, status: str, reason: str, mode: str = "ENFORCEMENT") -> FactorFinding:
    return FactorFinding(name, mode, status, reason)


def authorization(req: ActionRequest, cfg: dict) -> FactorFinding:
    if not _value(req.actor.get("id")) or not _value(req.actor.get("role")) or not _value(req.actor.get("tenant_id")):
        return _finding("authorization", "BLOCK", "MISSING_TRUSTED_ACTOR_FACTS")
    if req.actor.get("active") is not True:
        return _finding("authorization", "BLOCK", "INACTIVE_OR_UNKNOWN_IDENTITY")
    if not _value(req.target.get("id")) or not _value(req.target.get("tenant_id")):
        return _finding("authorization", "BLOCK", "MISSING_TARGET_FACTS")
    if req.actor["tenant_id"] != req.target["tenant_id"]:
        return _finding("authorization", "BLOCK", "CROSS_TENANT_BOUNDARY")
    if req.action in cfg["deny_actions"]:
        return _finding("authorization", "BLOCK", "HARD_DENIED_ACTION")
    allowed = cfg["allowed_actions_by_role"].get(req.actor["role"], [])
    if req.action not in allowed:
        return _finding("authorization", "BLOCK", "ROLE_NOT_AUTHORIZED")
    return _finding("authorization", "PASS", "ROLE_TENANT_AND_ACTION_MATCH")


def amount(req: ActionRequest, cfg: dict) -> FactorFinding:
    if req.action not in cfg["maximum_amounts_usd"]:
        return _finding("action_limits", "NOT_APPLICABLE", "NO_AMOUNT_LIMIT_FOR_ACTION")
    amt = req.parameters.get("amount_usd")
    if isinstance(amt, bool) or not isinstance(amt, (int, float)) or not math.isfinite(amt) or amt < 0:
        return _finding("action_limits", "BLOCK", "INVALID_OR_MISSING_AMOUNT")
    if amt > cfg["maximum_amounts_usd"][req.action]:
        return _finding("action_limits", "BLOCK", "AMOUNT_EXCEEDS_HARD_LIMIT")
    return _finding("action_limits", "PASS", "AMOUNT_WITHIN_HARD_LIMIT")


def data_handling(req: ActionRequest, cfg: dict) -> FactorFinding:
    label = req.target.get("classification")
    if not _value(label):
        return _finding("data_handling", "BLOCK", "MISSING_TRUSTED_DATA_CLASSIFICATION")
    if label in cfg["deny_classifications"]:
        return _finding("data_handling", "BLOCK", "RESTRICTED_DATA_CLASSIFICATION")
    return _finding("data_handling", "PASS", "DECLARED_CLASSIFICATION_ALLOWED")


def human_oversight(req: ActionRequest, cfg: dict, verifier: APPROVAL_CHECK | None) -> FactorFinding:
    needed = req.action in cfg["approval_required_actions"]
    if req.action in cfg["approval_thresholds_usd"]:
        amt = req.parameters.get("amount_usd")
        if isinstance(amt, bool) or not isinstance(amt, (int, float)) or not math.isfinite(amt) or amt < 0:
            return _finding("human_oversight", "BLOCK", "INVALID_OR_MISSING_APPROVAL_AMOUNT")
        needed = needed or amt > cfg["approval_thresholds_usd"][req.action]
    if not needed:
        return _finding("human_oversight", "NOT_APPLICABLE", "NO_APPROVAL_RULE_MATCHED")
    if verifier is None:
        return _finding("human_oversight", "REQUIRE_APPROVAL", "NO_TRUSTED_APPROVAL_VERIFIER")
    # The request body contains no approval grant. The application must supply a
    # trusted, independently implemented verifier, not a model assertion or flag.
    try:
        approved = verifier(req)
    except Exception:
        return _finding("human_oversight", "BLOCK", "APPROVAL_VERIFIER_ERROR")
    if type(approved) is not bool:
        return _finding("human_oversight", "BLOCK", "INVALID_APPROVAL_VERIFIER_RESULT")
    if approved:
        return _finding("human_oversight", "PASS", "TRUSTED_APPLICATION_VERIFIER_APPROVED")
    return _finding("human_oversight", "REQUIRE_APPROVAL", "AWAITING_VERIFIED_HUMAN_APPROVAL")


def advisory(name: str) -> FactorFinding:
    return _finding(name, "NOT_EVALUATED", "REQUIRES_INDEPENDENT_ASSESSMENT", "ADVISORY")


def evidence() -> FactorFinding:
    return _finding("evidence", "INFO", "MINIMAL_IN_MEMORY_DECISION_RECORD_ONLY", "RECORD_ONLY")


def run_builtin(name: str, req: ActionRequest, cfg: dict,
                verifier: APPROVAL_CHECK | None) -> FactorFinding:
    if name == "authorization": return authorization(req, cfg)
    if name == "action_limits": return amount(req, cfg)
    if name == "data_handling": return data_handling(req, cfg)
    if name == "human_oversight": return human_oversight(req, cfg, verifier)
    if name == "evidence": return evidence()
    if name in ADVISORY_FACTORS: return advisory(name)
    raise ValueError(f"Unknown built-in factor {name}")
