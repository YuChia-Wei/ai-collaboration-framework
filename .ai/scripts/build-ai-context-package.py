#!/usr/bin/env python3
"""Build deterministic ZIP and tar.gz AI context release packages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/build-ai-context-package.py")

from ai_context_package import PackageError, build_package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--profile", default=".ai/distribution/profiles/dotnet-backend.yaml"
    )
    parser.add_argument(
        "--previous-files",
        type=Path,
        help="Governed files.yaml for the one declared upgrade source",
    )
    parser.add_argument(
        "--previous-version",
        help="Version identity bound to --previous-files",
    )
    parser.add_argument(
        "--migration-source",
        action="append",
        nargs=2,
        metavar=("VERSION", "FILES_YAML"),
        default=[],
        help=(
            "Repeatable exact automatic-upgrade source as VERSION FILES_YAML; "
            "legacy --previous-version/--previous-files remains accepted"
        ),
    )
    args = parser.parse_args()
    try:
        migration_sources = [
            (Path(files_path), version)
            for version, files_path in args.migration_source
        ]
        result = build_package(
            args.repo,
            args.ref,
            args.version,
            args.output,
            args.profile,
            args.previous_files,
            args.previous_version,
            migration_sources,
        )
    except (OSError, PackageError) as exc:
        print(f"AI context package build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Built {result['package_id']} from {result['commit']}")
    print(result["zip"])
    print(result["tar_gz"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
