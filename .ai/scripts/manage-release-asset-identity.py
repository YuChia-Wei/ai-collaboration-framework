#!/usr/bin/env python3
"""Prepare, stage, or verify exact release assets; never upload or rebuild them."""
from __future__ import annotations

import argparse
import json
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from python_prerequisites import guard_direct_entrypoint
guard_direct_entrypoint(".ai/scripts/manage-release-asset-identity.py")

from release_asset_identity import (
    PackageError, governed, load_admission, make_admission, stage, strict_json,
    verify_provider, verify_source, verify_transported, describe_assets,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("required", "admit", "stage", "verify", "provider"))
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--assets-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository")
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()
    try:
        required = governed(args.version)
        if args.action == "required":
            print("true" if required else "false")
            return 0
        root = args.root.resolve()
        if args.action == "admit":
            if args.assets_dir is None or args.output is None:
                raise PackageError("admit requires --assets-dir and --output")
            directory = args.assets_dir.resolve()
            result = make_admission(root, directory, args.version)
            _, _, selected = describe_assets(root, directory, args.version)
            verify_source(root, args.version, args.ref, result, selected)
        else:
            result = load_admission(root, args.version, args.ref)
            if args.action == "stage":
                if args.assets_dir is None:
                    raise PackageError("stage requires --assets-dir")
                stage(root, result, args.assets_dir.resolve())
            elif args.action == "provider":
                if not args.repository or args.assets_dir is None or args.output is None:
                    raise PackageError("provider requires --repository, --assets-dir and --output")
                if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
                    raise PackageError("unsafe repository identity")
                verify_transported(root, result, args.assets_dir.resolve())
                locator = subprocess.run([
                    "gh", "release", "view", args.version, "--repo", args.repository,
                    "--json", "databaseId,tagName",
                ], cwd=root, capture_output=True, check=True)
                identity = strict_json(locator.stdout)
                if identity.get("tagName") != args.version or type(identity.get("databaseId")) is not int or identity["databaseId"] <= 0:
                    raise PackageError("provider release locator disagrees with the requested tag")
                response = subprocess.run([
                    "gh", "api", "--method", "GET",
                    f"repos/{args.repository}/releases/{identity['databaseId']}",
                ], cwd=root, capture_output=True, check=True)
                provider = strict_json(response.stdout)
                result = verify_provider(result, provider, args.repository, allow_draft=args.allow_draft)
                result["raw_provider_sha256"] = hashlib.sha256(response.stdout).hexdigest()
            elif args.assets_dir is not None:
                verify_transported(root, result, args.assets_dir.resolve())
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(result, stream, indent=2)
                stream.write("\n")
    except (OSError, ValueError, KeyError, TypeError, PackageError, subprocess.CalledProcessError) as exc:
        print(f"Release asset identity blocked: {exc}", file=sys.stderr)
        return 1
    print(f"Release asset identity {args.action} passed; no publication was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
