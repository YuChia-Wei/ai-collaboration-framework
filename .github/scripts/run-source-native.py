#!/usr/bin/env python3
"""Retained non-passing entry for owner-retired native trials; not an active route."""
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
    return "native-trials-retired:owner-must-select-an-actual-consumer-scenario"


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
                      "continuation": "Select a real consumer scenario and its supported runner, "
                                      "fixed source and actual evidence before proposing a new native route."},
                     sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
