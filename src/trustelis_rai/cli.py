"""Strictly offline command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .engine import ResponsibleAIKit
from .models import ActionRequest
from .policy import load_policy
from .reports import card_markdown, decision_markdown


def _json_file(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON document must be an object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trustelis-rai", description="Offline Responsible AI preflight and Control Cards")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    for label in ("validate", "card", "check"):
        cmd = sub.add_parser(label)
        cmd.add_argument("--policy", required=True)
        if label == "check": cmd.add_argument("--request", required=True)
        if label != "validate":
            cmd.add_argument("--format", choices=("json", "markdown"), default="json")
            cmd.add_argument("--output", help="Optional output path; creates local file explicitly")
    args = parser.parse_args(argv)
    try:
        kit = ResponsibleAIKit(load_policy(args.policy))
        if args.command == "validate":
            print(f"PASS policy={kit.policy_sha256} (offline, zero network)")
            return 0
        if args.command == "card":
            card = kit.control_card()
            content = json.dumps(card, indent=2, ensure_ascii=False) if args.format == "json" else card_markdown(card)
            status = 0
        else:
            request = ActionRequest.from_dict(_json_file(args.request))
            decision = kit.check(request)
            content = json.dumps(decision.as_dict(), indent=2, ensure_ascii=False) if args.format == "json" else decision_markdown(decision)
            # REJECTED and APPROVAL_REQUIRED both signal non-zero, for CI use.
            status = 0 if decision.verdict == "ALLOW" else 4 if decision.verdict == "REQUIRE_APPROVAL" else 5
        if args.output:
            p = Path(args.output)
            if p.is_dir(): raise ValueError("Output path is a directory")
            p.write_text(content + "\n", encoding="utf-8")
            print(f"Written {p}")
        else: print(content)
        return status
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
