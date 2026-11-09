#!/usr/bin/env python3
"""Build generic catalog + Engine 2 bytes from a clean isolated immutable source."""
from __future__ import annotations
import argparse
import hashlib
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
from release_common import (SCHEMA, STANDALONE_SCHEMA, README_LIMIT, README_SOURCE_PATH, document, encoded, engine_files, entry, git, identity, oid,
                            package_adapters, plain, release_version, render_readme, require, safe_name, sha, verify_bundle)
from release_tool_assets import refactor_notices, tool_asset_sources


def engine_pin(repository, source):
    members = engine_files(lambda n: git(repository, "show", source + ":" + n))
    rows = []
    for name in members:
        safe_name(name)
        blob = git(repository, "show", source + ":" + name)
        path = repository / name
        plain(path)
        require(path.read_bytes() == blob, "executing engine differs from selected Git blob")
        rows.append({"path": name, "sha256": sha(blob)})
    return {"id": "framework-managed-installation", "version": "2.0.0", "source_commit": source, "files": rows}


def load_readme_source(repository, source_commit):
    """Read one regular product blob from the selected source, never tooling HEAD."""
    oid(source_commit)
    listing = git(repository, "ls-tree", source_commit, "--", README_SOURCE_PATH).decode("ascii")
    match = re.fullmatch(r"(?:100644|100755) blob ([0-9a-f]{40})\t" + re.escape(README_SOURCE_PATH) + r"\n", listing)
    require(match is not None, "selected source requires a regular src README template; no fallback")
    raw = git(repository, "show", source_commit + ":" + README_SOURCE_PATH)
    require(len(raw) <= README_LIMIT, "README template budget")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(blob == match.group(1), "README source Git blob mismatch")
    return {"path": README_SOURCE_PATH, "commit": source_commit, "git_blob": blob,
            "sha256": sha(raw), "size": len(raw), "template_utf8": raw.decode("utf-8", errors="strict")}


def collect(root, prefix):
    payload = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink() and not getattr(path.lstat(), "st_file_attributes", 0) & 0x400, "linked package entry")
        if path.is_dir():
            continue
        plain(path)
        relative = path.relative_to(root).as_posix()
        name = safe_name(prefix + "/" + relative if prefix else relative)
        payload[name] = (path.read_bytes(), 0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644)
    return payload


def build(args):
    repository = args.repository.absolute()
    tooling = oid(args.tooling_commit)
    require(git(repository, "rev-parse", "HEAD").decode().strip() == tooling, "tooling checkout HEAD mismatch")
    require(not git(repository, "status", "--porcelain", "--untracked-files=all").strip(), "clean tooling checkout required")
    script_root = Path(__file__).absolute().parent
    require(script_root == repository / ".github/scripts", "run tooling from selected checkout")
    for name in ("build-release.py", "release_common.py", "release_tool_assets.py"):
        require((script_root / name).read_bytes() == git(repository, "show", tooling + ":.github/scripts/" + name), "tooling byte mismatch")
    source = identity(repository, args.source_commit, args.tag)
    readme_source = load_readme_source(repository, source["commit"])
    # Catalog 1 currently accepts stable or rc.N only. Keep snapshot identity in its name/manifest.
    version = release_version(source)
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
               "--repository", str(checkout), "--commit", source["commit"], "--release-version", version,
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
    adapters = package_adapters(document(payload["catalog/metadata/catalog.json"][0]),
                                {n: raw for n, (raw, _) in payload.items()})
    readme = render_readme(readme_source["template_utf8"], source, receipt["identity"], version, adapters)
    payload["README.md"] = (readme, 0o644)
    # Build tools from the same immutable source as the catalog. Their binaries
    # have an explicit manifest rather than masquerading as Git source blobs.
    generation_root = work / "generation"
    refactor_root = work / "refactor-delivery"
    standalone = not args.coreclr_tools and (checkout / ".github/scripts/release_tool_assets.py").is_file()
    generation_args = []
    if (checkout / '.github/scripts/native_tools.py').is_file():
        if args.coreclr_tools:
            require(args.native_tools is None, 'CoreCLR comparison cannot consume native artifacts')
            generation_args = ['--coreclr']
        else:
            require(args.native_tools is not None, 'Native tool artifacts required for this source')
            generation_args = ['--native-tools', str(args.native_tools.absolute())]
    else:
        require(args.native_tools is None, 'Legacy source cannot consume native artifacts')
    if standalone:
        generation_args.extend(['--refactor-output', str(refactor_root)])
    subprocess.run([sys.executable, "-I", "-B", str(checkout / ".github/scripts/build-generation.py"),
                    "--repository", str(checkout), "--commit", source["commit"],
                    "--version", version, "--output", str(generation_root),
                    "--work", str(work / "generation-build"), *generation_args], check=True, env=environment, timeout=900,
                   stdout=sys.stderr)
    generation = document((generation_root / "generation.json").read_bytes())
    generated_modes = {row["path"]: row["mode"] for row in generation["files"]}
    payload.update({name: (raw, generated_modes.get(name.removeprefix("generation/"), 0o644))
                    for name, (raw, _) in collect(generation_root, "generation").items()})
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
    manifest = {"schema": STANDALONE_SCHEMA if standalone else SCHEMA, "source": source, "version": version,
                "catalog_identity": receipt["identity"], "engine_pin_sha256": sha(pin_raw),
                "archive": {"name": archive.name, "size": len(raw), "sha256": sha(raw)},
                "entries": [entry(n, b, m) for n, (b, m) in sorted(payload.items())],
                "provenance": {"repository": args.repository_name, "tooling_commit": tooling, "readme_source": readme_source,
                    "workflow": args.workflow, "workflow_commit": oid(args.workflow_commit),
                    "run_id": args.run_id, "run_attempt": args.run_attempt,
                    "started_at": started, "completed_at": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "platform": platform.platform()},
                "validation": {"archive_raw_hashes": "verified", "readme_source": "verified", "generated_release_context": "verified",
                    "skill_adapter_inventory": "verified", "tests": "not-run", "runtime": "not-run", "publication": "not-performed"}}
    if standalone:
        refactor = {name: value[0] for name, value in collect(refactor_root, "").items()}
        executable = refactor.pop("RefactorTool.exe")
        notices = refactor_notices(refactor)
        standalone_rows = []
        for asset_name, source_path in tool_asset_sources(version).items():
            if source_path is None:
                asset = notices
            elif source_path == "RefactorTool.exe":
                asset = executable
            else:
                asset = payload[source_path][0]
            asset_hash = sha(asset)
            (output / asset_name).write_bytes(asset)
            (output / (asset_name + ".sha256")).write_bytes(f"{asset_hash}  {asset_name}\n".encode())
            standalone_rows.append({"name": asset_name, "size": len(asset), "sha256": asset_hash})
        manifest["standalone_tools"] = standalone_rows
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
    parser.add_argument("--workflow", choices=(".github/workflows/package-candidate.yml", ".github/workflows/publish-release.yml", ".github/workflows/native-tools.yml"), required=True)
    parser.add_argument("--repository-name", default="YuChia-Wei/ai-collaboration-framework")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--native-tools", type=Path)
    parser.add_argument("--coreclr-tools", action='store_true', help='Explicit framework-dependent comparison build')
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
