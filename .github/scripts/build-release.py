#!/usr/bin/env python3
"""Build generic catalog + Engine 2 bytes from a clean isolated immutable source."""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).absolute().parent))
from release_common import (SCHEMA, document, encoded, entry, git, identity, oid,
                            plain, require, safe_name, sha, verify_bundle)


def engine_pin(repository, source):
    lists = []
    for name in ("src/tools/maintain_framework.py", "src/distribution/installation_state.py"):
        tree = ast.parse(git(repository, "show", source + ":" + name))
        values = [node.value for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "ENGINE_FILES" for t in node.targets)]
        require(len(values) == 1 and isinstance(values[0], ast.Tuple), "literal ENGINE_FILES tuple required")
        value = ast.literal_eval(values[0])
        require(len(value) == 23 and all(type(n) is str and n.startswith("src/") for n in value) and tuple(sorted(set(value))) == value,
                "expected sorted 23-file product-only Engine 2 closure")
        lists.append(value)
    require(lists[0] == lists[1], "ENGINE_FILES declarations disagree")
    rows = []
    for name in lists[0]:
        safe_name(name)
        blob = git(repository, "show", source + ":" + name)
        path = repository / name
        plain(path)
        require(path.read_bytes() == blob, "executing engine differs from selected Git blob")
        rows.append({"path": name, "sha256": sha(blob)})
    return {"id": "framework-managed-installation", "version": "2.0.0", "source_commit": source, "files": rows}


def collect(root, prefix):
    payload = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink() and not getattr(path.lstat(), "st_file_attributes", 0) & 0x400, "linked package entry")
        if path.is_dir():
            continue
        plain(path)
        name = safe_name(prefix + "/" + path.relative_to(root).as_posix())
        payload[name] = (path.read_bytes(), 0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644)
    return payload


def build(args):
    repository = args.repository.absolute()
    tooling = oid(args.tooling_commit)
    require(git(repository, "rev-parse", "HEAD").decode().strip() == tooling, "tooling checkout HEAD mismatch")
    require(not git(repository, "status", "--porcelain", "--untracked-files=all").strip(), "clean tooling checkout required")
    script_root = Path(__file__).absolute().parent
    require(script_root == repository / ".github/scripts", "run tooling from selected checkout")
    for name in ("build-release.py", "release_common.py"):
        require((script_root / name).read_bytes() == git(repository, "show", tooling + ":.github/scripts/" + name), "tooling byte mismatch")
    source = identity(repository, args.source_commit, args.tag)
    # Catalog 1 currently accepts stable or rc.N only. Keep snapshot identity in its name/manifest.
    release_version = source["tag"][1:] if source["tag"] else "0.0.0-rc." + str(int(source["commit"][:12], 16) + 1)
    require(re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-rc\.[1-9][0-9]*)?", release_version),
            "selected Catalog 1 supports stable or rc.N versions only")
    require(tooling == oid(args.workflow_commit), "workflow/tooling commit mismatch")
    work, output = args.work_root.absolute(), args.output.absolute()
    for target in (work, output):
        require(not target.exists(), "fresh external work/output roots required; retain prior attempt")
        require(not target.is_relative_to(repository) and not repository.is_relative_to(target), "external roots required")
    require(not work.is_relative_to(output) and not output.is_relative_to(work), "work/output roots overlap")
    work.mkdir(parents=True)
    output.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    checkout = work / "s"
    subprocess.run(["git", "clone", "--no-hardlinks", "--no-checkout", str(repository), str(checkout)], check=True, timeout=90, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "-C", str(checkout), "-c", "core.autocrlf=false", "checkout", "--detach", source["commit"]], check=True, timeout=90, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(not git(checkout, "status", "--porcelain", "--untracked-files=all").strip(), "isolated source checkout dirty")
    pin = engine_pin(checkout, source["commit"])
    pin_raw = encoded(pin)
    pin_file = work / "engine-pin.json"
    pin_file.write_bytes(pin_raw)
    for name in ("c", "e", "t"):
        (work / name).mkdir()
    command = [sys.executable, "-I", "-B", str(checkout / "tools/build-catalog.py"),
               "--repository", str(checkout), "--commit", source["commit"], "--release-version", release_version,
               "--engine-pin", str(pin_file), "--output-root", str(work / "c"),
               "--scratch-root", str(work / "t"), "--engine-output-root", str(work / "e")]
    # No release token or provider credential is passed to product code.
    environment = {k: v for k, v in os.environ.items() if not any(x in k.upper() for x in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))}
    result = subprocess.run(command, capture_output=True, env=environment, timeout=300)
    (work / "builder.stdout").write_bytes(result.stdout)
    (work / "builder.stderr").write_bytes(result.stderr)
    require(result.returncode == 0, "public builder rejected source/version; inspect retained builder.stdout/stderr")
    receipt = document(result.stdout)
    catalog_root = Path(receipt["artifact_root"])
    engine_root = Path(receipt["engine_bundle"]["engine_root"])
    require(catalog_root.is_relative_to(work / "c") and engine_root.is_relative_to(work / "e"), "builder roots escaped")
    require(receipt["engine_bundle"]["engine"] == pin, "builder engine differs from independent pin")
    payload = collect(catalog_root, "catalog") | collect(engine_root, "engine")
    payload["engine-pin.json"] = (pin_raw, 0o644)
    label = source["tag"] or "snapshot"
    readme = f"""# AI Collaboration Framework {label}

Source commit: {source['commit']}
Catalog identity: {receipt['identity']}
Distribution label: {release_version}
Engine: framework-managed-installation 2.0.0 (23 pinned product-source files).

This generic package includes the full catalog, standalone engine, independently
selected engine pin and raw content hashes. Catalog metadata includes the actual
build receipt. It contains no project-bound selection or installed target state.

Use engine/src/tools/derive-subset.py with an explicitly selected preset/selection,
the included catalog and its identity, and engine-pin.json. Run Python with -I -B;
provide PyYAML 6.x and explicit disjoint output/scratch roots.
Distribution and engine identity must be reviewed before target installation.

Snapshot builds are development artifacts, even though the current Catalog 1
builder requires a numeric rc.N distribution label. The full SHA identifies them.
Build/archive success does not establish test, runtime or native acceptance.
Draft readiness is not publication. Release notes and publication are owner actions.
"""
    payload["README.md"] = (readme.encode(), 0o644)
    payload["content-hashes.json"] = (encoded([entry(n, b, m) for n, (b, m) in sorted(payload.items())]), 0o644)
    name = f"ai-collaboration-framework-{label}-{source['commit']}.zip"
    archive = output / name
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for name_in_zip, (raw, mode) in sorted(payload.items()):
            info = zipfile.ZipInfo(safe_name(name_in_zip), (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zipped.writestr(info, raw)
    raw = archive.read_bytes()
    manifest = {"schema": SCHEMA, "source": source, "version": release_version,
                "catalog_identity": receipt["identity"], "engine_pin_sha256": sha(pin_raw),
                "archive": {"name": archive.name, "size": len(raw), "sha256": sha(raw)},
                "entries": [entry(n, b, m) for n, (b, m) in sorted(payload.items())],
                "provenance": {"repository": args.repository_name, "tooling_commit": tooling,
                    "workflow": args.workflow, "workflow_commit": oid(args.workflow_commit),
                    "run_id": args.run_id, "run_attempt": args.run_attempt,
                    "started_at": started, "completed_at": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "platform": platform.platform()},
                "validation": {"archive_raw_hashes": "verified", "tests": "not-run", "runtime": "not-run", "publication": "not-performed"}}
    (output / "release-manifest.json").write_bytes(encoded(manifest))
    (output / (archive.name + ".sha256")).write_text(f"{sha(raw)}  {archive.name}\n", encoding="utf-8", newline="\n")
    verify_bundle(output, source)
    extracted = work / "x"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        for row in manifest["entries"]:
            target = extracted / safe_name(row["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zipped.read(row["path"]))
            require(sha(target.read_bytes()) == row["sha256"], "extracted raw hash mismatch")
    require(not git(checkout, "status", "--porcelain", "--untracked-files=all").strip(), "source drift after build")
    require(identity(repository, source["commit"], source["tag"]) == source, "tag drift after build")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--tag")
    parser.add_argument("--tooling-commit", required=True)
    parser.add_argument("--workflow-commit", required=True)
    parser.add_argument("--workflow", choices=(".github/workflows/package-candidate.yml", ".github/workflows/publish-release.yml"), required=True)
    parser.add_argument("--repository-name", default="YuChia-Wei/ai-collaboration-framework")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        manifest = build(args)
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                stream.write("source_commit=" + manifest["source"]["commit"] + "\n")
        print(encoded({"outcome": "built", "source": manifest["source"], "archive": manifest["archive"],
                       "catalog_identity": manifest["catalog_identity"]}).decode(), end="")
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print(encoded({"outcome": "failed", "reason": str(exc), "next_action": "Preserve this attempt; fix the cause and use fresh external roots."}).decode(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
