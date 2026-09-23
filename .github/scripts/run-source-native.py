#!/usr/bin/env python3
"""Dormant Windows native entry. V3 command binding is deliberately unresolved."""
import argparse
import json
import os
import platform
import re


def decision(subject, system, event_name=None, ref=None):
    if not re.fullmatch(r"[0-9a-f]{40}", subject or "") or subject == "0" * 40:
        return "invalid-subject"
    if system != "Windows":
        return "unsupported-platform:Windows-only"
    if event_name is not None and (event_name != "workflow_dispatch" or ref != "refs/heads/main"):
        return "requires-manual-main-workflow"
    return "native-binding-pending:coordinator-must-supply-fixed-V3-interface-and-selected-cases"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True)
    args = parser.parse_args(argv)
    hosted = os.environ.get("GITHUB_ACTIONS") == "true"
    reason = decision(args.subject, platform.system(), os.environ.get("GITHUB_EVENT_NAME") if hosted else None,
                      os.environ.get("GITHUB_REF") if hosted else None)
    print(json.dumps({"context": "Source native trial", "status": "blocked", "reason": reason,
                      "subject_sha": args.subject if re.fullmatch(r"[0-9a-f]{40}", args.subject) else None,
                      "subject_fetched": False, "native_executed": False,
                      "runner_revision": os.environ.get("GITHUB_SHA") if hosted else None,
                      "continuation": "Bind actual V3 native-windows argv, explicit native/recovery roots, "
                                      "fixed runner/subject verification and process-termination result before enablement."},
                     sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
