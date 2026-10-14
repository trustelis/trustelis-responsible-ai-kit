"""Strict configuration parsing; refuses unknown fields and invalid factor values."""
from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1"
STANDARD_FACTORS = {
    "authorization", "action_limits", "data_handling", "human_oversight",
    "evidence", "regulatory_context", "fairness", "transparency",
    "organizational_readiness",
}
ENFORCEMENT_FACTORS = {
    "authorization", "action_limits", "data_handling", "human_oversight"
}
ADVISORY_FACTORS = {
    "regulatory_context", "fairness", "transparency", "organizational_readiness"
}
FACTOR_FIELDS = {
    "authorization": {"enabled", "allowed_actions_by_role", "tenant_isolation", "deny_actions"},
    "action_limits": {"enabled", "maximum_amounts_usd"},
    "data_handling": {"enabled", "deny_classifications", "require_classification"},
    "human_oversight": {"enabled", "approval_required_actions", "approval_thresholds_usd"},
    "evidence": {"enabled"},
    "regulatory_context": {"enabled", "review_note"},
    "fairness": {"enabled", "review_note"},
    "transparency": {"enabled", "review_note"},
    "organizational_readiness": {"enabled", "review_note"},
}


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f"{name} must be a nonempty string of at most 200 characters")
    return value


def _strings(values: Any, name: str) -> None:
    if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
        raise ValueError(f"{name} must be an array of nonempty strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must not contain duplicates")


def _limits(obj: Any, name: str) -> None:
    if not isinstance(obj, dict):
        raise ValueError(f"{name} must be an object")
    for action, amount in obj.items():
        _string(action, f"{name} action")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
            raise ValueError(f"{name}.{action} must be a finite nonnegative number")


def validate_policy(obj: Any, *, custom_factors: set[str] | None = None) -> dict:
    if not isinstance(obj, dict):
        raise ValueError("Policy must be an object")
    if set(obj) != {"schema_version", "use_case", "factors"}:
        raise ValueError("Policy must contain only schema_version, use_case and factors")
    if obj["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"Unsupported policy version; expected {SCHEMA_VERSION}")
    use_case = obj["use_case"]
    if not isinstance(use_case, dict) or not {"id", "name"}.issubset(use_case):
        raise ValueError("use_case must contain id and name")
    if set(use_case) - {"id", "name", "industry"}:
        raise ValueError("Unknown use_case fields")
    for k in ("id", "name"):
        _string(use_case[k], f"use_case.{k}")
    if "industry" in use_case:
        _string(use_case["industry"], "use_case.industry")
    factors = obj["factors"]
    if not isinstance(factors, dict) or not factors:
        raise ValueError("factors must be a nonempty object")
    permitted = STANDARD_FACTORS | set(custom_factors or ())
    if set(factors) - permitted:
        raise ValueError("Unknown factor(s): " + ", ".join(sorted(set(factors) - permitted)))
    if "authorization" not in factors or not isinstance(factors["authorization"], dict) or factors["authorization"].get("enabled") is not True:
        raise ValueError("authorization factor is mandatory and must be enabled for ActionGuard")
    for name, cfg in factors.items():
        if not isinstance(cfg, dict) or not isinstance(cfg.get("enabled"), bool):
            raise ValueError(f"{name}: enabled must be a boolean")
        allowed_fields = FACTOR_FIELDS.get(name, {"enabled", "description"})
        if set(cfg) - allowed_fields:
            raise ValueError(f"{name}: unknown config fields {sorted(set(cfg)-allowed_fields)}")
        if not cfg["enabled"]:
            if set(cfg) != {"enabled"}:
                raise ValueError(f"{name}: disabled factors may contain only enabled")
            continue
        if name == "authorization":
            if set(cfg) != {"enabled", "allowed_actions_by_role", "tenant_isolation", "deny_actions"}:
                raise ValueError("authorization requires allowed_actions_by_role, tenant_isolation, deny_actions")
            if cfg["tenant_isolation"] is not True:
                raise ValueError("tenant_isolation must be true in this prototype")
            roles = cfg["allowed_actions_by_role"]
            if not isinstance(roles, dict) or not roles:
                raise ValueError("authorization.allowed_actions_by_role must be nonempty")
            for role, actions in roles.items():
                _string(role, "role")
                _strings(actions, f"role {role}")
            _strings(cfg["deny_actions"], "deny_actions")
        if name == "action_limits":
            if set(cfg) != {"enabled", "maximum_amounts_usd"}:
                raise ValueError("action_limits requires maximum_amounts_usd")
            _limits(cfg["maximum_amounts_usd"], "maximum_amounts_usd")
        if name == "data_handling":
            if set(cfg) != {"enabled", "deny_classifications", "require_classification"}:
                raise ValueError("data_handling requires deny_classifications and require_classification")
            _strings(cfg["deny_classifications"], "deny_classifications")
            if cfg["require_classification"] is not True:
                raise ValueError("data_handling.require_classification must be true in prototype")
        if name == "human_oversight":
            if set(cfg) != {"enabled", "approval_required_actions", "approval_thresholds_usd"}:
                raise ValueError("human_oversight requires approval_required_actions and approval_thresholds_usd")
            _strings(cfg["approval_required_actions"], "approval_required_actions")
            _limits(cfg["approval_thresholds_usd"], "approval_thresholds_usd")
        if name in ADVISORY_FACTORS and "review_note" in cfg:
            _string(cfg["review_note"], f"{name}.review_note")
        if name not in STANDARD_FACTORS and "description" in cfg:
            _string(cfg["description"], f"{name}.description")
    # Normalize by deep-copy to prevent callers mutating the policy after construction.
    return deepcopy(obj)


def canonical_hash(policy: dict) -> str:
    payload = json.dumps(policy, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def load_policy(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
