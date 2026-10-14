"""Public value objects for the illustrative Responsible AI developer kit.

The kit is not a production policy decision point. Actor and target facts MUST be
provided by trusted application infrastructure, never from model-generated text.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ActionRequest:
    use_case_id: str
    action: str
    actor: Mapping[str, Any]
    target: Mapping[str, Any]
    parameters: Mapping[str, Any]

    @classmethod
    def from_dict(cls, obj: object) -> "ActionRequest":
        if not isinstance(obj, dict):
            raise ValueError("Request must be a JSON object")
        for key in ("use_case_id", "action"):
            if not isinstance(obj.get(key), str) or not obj[key].strip():
                raise ValueError(f"Request {key} must be a nonempty string")
        for key in ("actor", "target"):
            if not isinstance(obj.get(key), dict):
                raise ValueError(f"Request {key} must be an object")
        params = obj.get("parameters", {})
        if not isinstance(params, dict):
            raise ValueError("Request parameters must be an object")
        return cls(
            use_case_id=obj["use_case_id"], action=obj["action"],
            actor=obj["actor"], target=obj["target"], parameters=params,
        )


@dataclass(frozen=True)
class FactorFinding:
    factor: str
    mode: str
    status: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {"factor": self.factor, "mode": self.mode,
                "status": self.status, "reason": self.reason}
