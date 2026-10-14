"""Lightweight developer-side preflight checks. No production enforcement claim."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, TypeVar
from uuid import uuid4

from .factors import APPROVAL_CHECK, run_builtin
from .models import ActionRequest, FactorFinding
from .policy import STANDARD_FACTORS, canonical_hash, validate_policy

CustomEvaluator = Callable[[ActionRequest, Mapping[str, Any]], FactorFinding]
T = TypeVar("T")


@dataclass(frozen=True)
class DecisionRecord:
    event_id: str
    created_at: str
    use_case_id: str
    action: str
    verdict: str
    policy_sha256: str
    findings: tuple[FactorFinding, ...]

    def as_dict(self) -> dict[str, Any]:
        # Deliberately exclude actor IDs, tenant IDs, raw parameters, PII, and
        # prompt content. This is a sample record, not a durable audit trail.
        return {"record_type": "prototype_decision", "event_id": self.event_id,
                "created_at": self.created_at, "use_case_id": self.use_case_id,
                "action": self.action, "verdict": self.verdict,
                "policy_sha256": self.policy_sha256,
                "findings": [x.as_dict() for x in self.findings],
                "note": "In-memory demonstration only; not an authenticated audit log"}


class ActionNotAuthorized(RuntimeError):
    def __init__(self, record: DecisionRecord):
        self.record = record
        super().__init__(f"Preflight did not authorize action: {record.verdict}")


class ResponsibleAIKit:
    """Developer-side reference kit. Host application must use trusted identities.

    Policy is validated and snapshotted when constructed. Unknown factors raise
    an error instead of silently permitting a decision.
    """

    def __init__(self, policy: dict, *, custom_factors: Mapping[str, CustomEvaluator] | None = None):
        custom = dict(custom_factors or {})
        if set(custom) & STANDARD_FACTORS:
            raise ValueError("Custom factors cannot replace built-in factors")
        if any(not callable(v) for v in custom.values()):
            raise ValueError("Custom evaluators must be callable")
        self._policy = validate_policy(policy, custom_factors=set(custom))
        self._custom = custom
        self._sha = canonical_hash(self._policy)

    @property
    def policy_sha256(self) -> str:
        return self._sha

    def check(self, request: ActionRequest | dict, *,
              approval_verifier: APPROVAL_CHECK | None = None) -> DecisionRecord:
        if isinstance(request, dict):
            request = ActionRequest.from_dict(request)
        if not isinstance(request, ActionRequest):
            raise ValueError("request must be ActionRequest or dict")
        result: list[FactorFinding] = []
        if request.use_case_id != self._policy["use_case"]["id"]:
            result.append(FactorFinding("use_case_scope", "ENFORCEMENT", "BLOCK", "WRONG_USE_CASE"))
        for name, cfg in self._policy["factors"].items():
            if cfg["enabled"] is not True:
                result.append(FactorFinding(name, "NOT_ACTIVE", "NOT_APPLICABLE", "DISABLED_IN_POLICY"))
                continue
            if name in STANDARD_FACTORS:
                try:
                    finding = run_builtin(name, request, cfg, approval_verifier)
                except Exception:
                    finding = FactorFinding(name, "ENFORCEMENT", "BLOCK", "FACTOR_EXECUTION_ERROR")
            else:
                try:
                    finding = self._custom[name](request, cfg)
                    if not isinstance(finding, FactorFinding) or finding.factor != name or finding.mode != "ENFORCEMENT" or finding.status not in {"PASS", "BLOCK", "REQUIRE_APPROVAL", "NOT_APPLICABLE"}:
                        raise ValueError("Unexpected custom finding")
                except Exception:
                    finding = FactorFinding(name, "ENFORCEMENT", "BLOCK", "CUSTOM_FACTOR_ERROR")
            result.append(finding)
        statuses = {finding.status for finding in result if finding.mode == "ENFORCEMENT"}
        verdict = "BLOCK" if "BLOCK" in statuses else ("REQUIRE_APPROVAL" if "REQUIRE_APPROVAL" in statuses else "ALLOW")
        return DecisionRecord(
            event_id=str(uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            use_case_id=self._policy["use_case"]["id"], action=request.action,
            verdict=verdict, policy_sha256=self._sha, findings=tuple(result),
        )

    def execute_guarded(self, request: ActionRequest | dict, executor: Callable[[], T], *,
                        approval_verifier: APPROVAL_CHECK | None = None) -> tuple[DecisionRecord, T]:
        """Prevent a supplied callable from running when the local preflight fails.

        Only this wrapper's execution path is guarded. It cannot prevent code
        from calling the tool elsewhere, and has no external side-effect safety
        guarantees, transaction binding, or authoritative audit persistence.
        """
        if not callable(executor):
            raise ValueError("executor must be callable")
        decision = self.check(request, approval_verifier=approval_verifier)
        if decision.verdict != "ALLOW":
            raise ActionNotAuthorized(decision)
        return decision, executor()

    def control_card(self) -> dict[str, Any]:
        entries = []
        for name, cfg in self._policy["factors"].items():
            active = cfg["enabled"] is True
            mode = "ENFORCEMENT" if name in {"authorization", "data_handling", "action_limits", "human_oversight"} or name in self._custom else (
                "RECORD_ONLY" if name == "evidence" else "ADVISORY")
            entries.append({"name": name, "enabled": active,
                            "mode": mode if active else "NOT_ACTIVE",
                            "status": ("CONFIGURED_FOR_PREFLIGHT" if mode == "ENFORCEMENT" else
                                       "MINIMAL_IN_MEMORY_ONLY" if mode == "RECORD_ONLY" else
                                       "NOT_EVALUATED") if active else "DISABLED",
                            "does_not_claim": "Legal compliance, enterprise deployment safety, or certification"})
        return {"kit_version": "0.1.0", "use_case": self._policy["use_case"].copy(),
                "policy_sha256": self._sha, "factors": entries,
                "disclaimer": "Developer-side reference kit; no compliance, real-world safety or provider enforcement certification"}
