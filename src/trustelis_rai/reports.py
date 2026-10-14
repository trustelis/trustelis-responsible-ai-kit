"""Human-readable Control Card with statuses, not fabricated compliance scores."""
from __future__ import annotations

from .engine import DecisionRecord


def card_markdown(card: dict) -> str:
    uc = card["use_case"]
    lines = ["# TRUSTELIS Responsible AI Control Card", "",
             f"**Use Case:** {uc['name']} (`{uc['id']}`)",
             f"**Policy SHA256:** `{card['policy_sha256']}`", "",
             "| Factor | Mode | Status |", "| :-- | :-- | :-- |"]
    for item in card["factors"]:
        lines.append(f"| {item['name']} | {item['mode']} | {item['status']} |")
    lines += ["", "**Important:** This is a configuration summary, not a legal/compliance certificate or a claim of production enforcement.", ""]
    return "\n".join(lines)


def decision_markdown(record: DecisionRecord) -> str:
    data = record.as_dict()
    lines = ["# TRUSTELIS Responsible AI Decision", "",
             f"**Proposed action:** `{data['action']}`", f"**Preflight decision:** {data['verdict']}",
             f"**Use Case:** `{data['use_case_id']}`", f"**Policy:** `{data['policy_sha256']}`", "",
             "| Factor | Mode | Status | Reason |", "| :-- | :-- | :-- | :-- |"]
    for f in record.findings:
        lines.append(f"| {f.factor} | {f.mode} | {f.status} | {f.reason} |")
    lines += ["", "**This is a prototype preflight record, not a persistent or tamper-proof audit log.**", ""]
    return "\n".join(lines)
