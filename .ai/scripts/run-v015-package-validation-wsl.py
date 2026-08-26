#!/usr/bin/env python3
"""Run one v0.15 validation lane in a WSL-native temporary clone.

The Windows checkout is transferred as an exact-head Git bundle over stdin.
WSL never reads the checkout, launcher, or evidence directory through a shared
Windows mount. Result evidence returns as a bounded tar stream and is written
only below the ignored validation root by this Windows-side process.
"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile


SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/run-v015-package-validation-wsl.py")


VALIDATION_ROOT = Path(".dev/ai-context/local/validation")
CLEANUP_MARKER = "AI_CONTEXT_WSL_NATIVE_CLEANUP=passed"
RESULT_MEMBERS = {"lane.stdout", "lane.stderr", "launcher.json"}

WSL_BOOTSTRAP = r"""
set -euo pipefail
subject_sha="$1"
lane="$2"
has_prior="$3"
shift 3
test -d /tmp
test -w /tmp
filesystem_type="$(stat -f -c %T /tmp)"
case "$filesystem_type" in
  9p|drvfs) printf '%s\n' 'shared-filesystem-rejected' >&2; exit 94 ;;
esac
run_root="$(mktemp -d "/tmp/ai-context-v015.XXXXXXXX")"
cleanup() {
  rm -rf -- "$run_root"
  printf '%s\n' 'AI_CONTEXT_WSL_NATIVE_CLEANUP=passed' >&2
}
trap cleanup EXIT HUP INT TERM
tar -xf - -C "$run_root"
git clone --no-checkout "$run_root/subject.bundle" "$run_root/repo" >&2
git -C "$run_root/repo" config core.longpaths true
git -C "$run_root/repo" checkout --detach "$subject_sha" >&2
observed_sha="$(git -C "$run_root/repo" rev-parse HEAD)"
test "$observed_sha" = "$subject_sha"
test -z "$(git -C "$run_root/repo" status --porcelain=v1 --untracked-files=no)"
test "$(stat -f -c %T "$run_root/repo")" = "$filesystem_type"
lane_output="$run_root/repo/.dev/ai-context/local/validation/wsl-native-output"
mkdir -p "$lane_output"
if test "$has_prior" = "1"; then
  set -- "$@" --prior-terminal "$run_root/prior-terminal.json"
fi
set +e
(
  cd "$run_root/repo"
  env -u AI_CONTEXT_TEST_TMP_ROOT python3 -B \
    .ai/scripts/run-v015-package-validation.py "$lane" \
    --expected-commit "$subject_sha" --output-dir "$lane_output" "$@"
) >"$run_root/lane.stdout" 2>"$run_root/lane.stderr"
lane_exit="$?"
set -e
result_root="$run_root/result"
mkdir -p "$result_root/output"
cp -a "$lane_output"/. "$result_root/output/"
cp "$run_root/lane.stdout" "$result_root/lane.stdout"
cp "$run_root/lane.stderr" "$result_root/lane.stderr"
printf '{"cleanup":"trap-confirmed","filesystem":"%s","lane":"%s","lane_exit":%s,"subject_sha":"%s","workspace":"linux-native-temp"}\n' \
  "$filesystem_type" "$lane" "$lane_exit" "$subject_sha" >"$result_root/launcher.json"
tar -cf - -C "$result_root" output lane.stdout lane.stderr launcher.json
""".strip()


class LauncherError(ValueError):
    """Fail-closed WSL launcher error."""


def run_git(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=text,
    )


def validate_subject(root: Path, expected_commit: str) -> None:
    head = run_git(root, "rev-parse", "HEAD")
    if head.returncode != 0 or head.stdout.strip() != expected_commit:
        raise LauncherError("subject-head-mismatch")
    status = run_git(root, "status", "--porcelain=v1", "--untracked-files=no")
    if status.returncode != 0 or status.stdout:
        raise LauncherError("subject-tracked-drift")


def validate_output(root: Path, output_dir: Path) -> Path:
    resolved = output_dir.resolve()
    allowed = (root / VALIDATION_ROOT).resolve()
    if not resolved.is_relative_to(allowed):
        raise LauncherError("output-outside-ignored-validation-root")
    ignored = run_git(root, "check-ignore", "--no-index", "--quiet", str(resolved))
    if ignored.returncode != 0:
        raise LauncherError("output-not-ignored")
    if resolved.exists():
        raise LauncherError("output-already-exists")
    return resolved


def add_tar_file(archive: tarfile.TarFile, path: Path, arcname: str) -> None:
    info = archive.gettarinfo(str(path), arcname=arcname)
    if not info.isfile():
        raise LauncherError(f"non-file-input:{arcname}")
    with path.open("rb") as stream:
        archive.addfile(info, stream)


def build_transfer(
    root: Path,
    expected_commit: str,
    prior_terminal: Path | None,
    scratch_root: Path,
) -> bytes:
    scratch_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".wsl-bundle-", dir=scratch_root) as temporary:
        bundle = Path(temporary) / "subject.bundle"
        created = run_git(root, "bundle", "create", str(bundle), "HEAD")
        if created.returncode != 0:
            raise LauncherError("git-bundle-create-failed")
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as archive:
            add_tar_file(archive, bundle, "subject.bundle")
            if prior_terminal is not None:
                prior = prior_terminal.resolve()
                if not prior.is_file():
                    raise LauncherError("prior-terminal-missing")
                add_tar_file(archive, prior, "prior-terminal.json")
        return buffer.getvalue()


def wsl_command(distribution: str, expected_commit: str, lane: str, has_prior: bool, lane_args: list[str]) -> list[str]:
    return [
        "wsl.exe",
        "--distribution",
        distribution,
        "--exec",
        "bash",
        "-c",
        WSL_BOOTSTRAP,
        "ai-context-wsl-native",
        expected_commit,
        lane,
        "1" if has_prior else "0",
        *lane_args,
    ]


def normalized_member_name(member: tarfile.TarInfo) -> str:
    if "\\" in member.name or ":" in member.name:
        raise LauncherError("unsafe-result-member")
    path = PurePosixPath(member.name)
    parts = tuple(part for part in path.parts if part not in ("", "."))
    if not parts or any(part == ".." for part in parts) or path.is_absolute():
        raise LauncherError("unsafe-result-member")
    return PurePosixPath(*parts).as_posix()


def extract_result(payload: bytes, destination: Path, expected_commit: str, lane: str) -> tuple[int, str, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".wsl-result-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as archive:
            members = archive.getmembers()
            names = [normalized_member_name(member) for member in members]
            if len(names) != len(set(names)):
                raise LauncherError("duplicate-result-member")
            for member in members:
                name = normalized_member_name(member)
                if member.isdir():
                    if name != "output":
                        raise LauncherError("unsafe-result-member")
                    target = staging / PurePosixPath(name)
                    if not target.resolve().is_relative_to(staging.resolve()):
                        raise LauncherError("unsafe-result-member")
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile() or not (name in RESULT_MEMBERS or name.startswith("output/")):
                    raise LauncherError("unsafe-result-member")
                source = archive.extractfile(member)
                if source is None:
                    raise LauncherError("missing-result-member-bytes")
                target = staging / PurePosixPath(name)
                if not target.resolve().is_relative_to(staging.resolve()):
                    raise LauncherError("unsafe-result-member")
                target.parent.mkdir(parents=True, exist_ok=True)
                with source, target.open("wb") as destination_stream:
                    shutil.copyfileobj(source, destination_stream)
            if not RESULT_MEMBERS.issubset(set(names)):
                raise LauncherError("incomplete-result-envelope")
        launcher = json.loads((staging / "launcher.json").read_text(encoding="utf-8"))
        if launcher.get("subject_sha") != expected_commit or launcher.get("lane") != lane:
            raise LauncherError("result-subject-mismatch")
        if launcher.get("workspace") != "linux-native-temp" or launcher.get("filesystem") in {"9p", "drvfs"}:
            raise LauncherError("result-shared-filesystem")
        lane_exit = launcher.get("lane_exit")
        if type(lane_exit) is not int or not 0 <= lane_exit <= 255:
            raise LauncherError("invalid-lane-exit")
        output = staging / "output"
        if not output.is_dir():
            raise LauncherError("missing-output-envelope")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(output, destination)
        shutil.copy2(staging / "launcher.json", destination / "wsl-native-launcher.json")
        shutil.copy2(staging / "lane.stdout", destination / "lane.stdout")
        shutil.copy2(staging / "lane.stderr", destination / "lane.stderr")
        stdout = (staging / "lane.stdout").read_text(encoding="utf-8", errors="replace")
        stderr = (staging / "lane.stderr").read_text(encoding="utf-8", errors="replace")
        return lane_exit, stdout, stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane", choices=("fast", "medium", "long"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--distribution", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--prior-terminal", type=Path)
    parser.add_argument("--material-state-change")
    parser.add_argument("--authorization-ref")
    parser.add_argument("--trusted-reference", action="store_true")
    args = parser.parse_args()
    root = args.repo.resolve()
    try:
        if os.name != "nt":
            raise LauncherError("windows-host-required")
        validate_subject(root, args.expected_commit)
        output = validate_output(root, args.output_dir)
        lane_args = ["--attempt", str(args.attempt)]
        if args.material_state_change:
            lane_args.extend(("--material-state-change", args.material_state_change))
        if args.authorization_ref:
            lane_args.extend(("--authorization-ref", args.authorization_ref))
        if args.trusted_reference:
            lane_args.append("--trusted-reference")
        transfer = build_transfer(root, args.expected_commit, args.prior_terminal, output.parent)
        completed = subprocess.run(
            wsl_command(
                args.distribution,
                args.expected_commit,
                args.lane,
                args.prior_terminal is not None,
                lane_args,
            ),
            cwd=root,
            input=transfer,
            capture_output=True,
            check=False,
        )
        transport_stderr = completed.stderr.decode("utf-8", errors="replace")
        if completed.returncode != 0 or CLEANUP_MARKER not in transport_stderr:
            raise LauncherError("wsl-native-transport-failed")
        lane_exit, lane_stdout, lane_stderr = extract_result(
            completed.stdout, output, args.expected_commit, args.lane
        )
        if lane_stdout:
            print(lane_stdout, end="")
        if lane_stderr:
            print(lane_stderr, end="", file=sys.stderr)
        return lane_exit
    except (OSError, json.JSONDecodeError, tarfile.TarError, LauncherError) as error:
        print(f"WSL-native validation launcher failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
