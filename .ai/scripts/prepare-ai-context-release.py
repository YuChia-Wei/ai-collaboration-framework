#!/usr/bin/env python3
"""Run read-only pre-tag release gates and print the user-owned tag command."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/prepare-ai-context-release.py")

import yaml


STATE_PATH = Path(__file__).with_name("validate-ai-context-release-state.py")
STATE_SPEC = importlib.util.spec_from_file_location("ai_context_release_state", STATE_PATH)
assert STATE_SPEC and STATE_SPEC.loader
release_state = importlib.util.module_from_spec(STATE_SPEC)
STATE_SPEC.loader.exec_module(release_state)


def bash_executable(
    platform_name: str | None = None,
    which=shutil.which,
) -> str:
    """Resolve Bash without mistaking the Windows WSL launcher for Git Bash."""
    platform_name = platform_name or os.name
    if platform_name != "nt":
        bash = which("bash")
        if bash:
            return bash
        raise RuntimeError("bash is required to run the critical gate")

    candidates: list[Path] = []
    git = which("git")
    if git:
        candidates.append(Path(git).resolve().parent.parent / "bin/bash.exe")
    candidates.append(
        Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        / "Git/bin/bash.exe"
    )
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "Programs/Git/bin/bash.exe")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError(
        "Git Bash is required on Windows to run the critical gate; "
        "the WSL bash launcher is not supported"
    )


def bash_environment(
    executable: str,
    platform_name: str | None = None,
    base: dict[str, str] | None = None,
) -> dict[str, str]:
    """Supply Git Bash utilities without mutating the parent environment."""
    environment = dict(os.environ if base is None else base)
    if (platform_name or os.name) == "nt":
        git_usr_bin = Path(executable).resolve().parent.parent / "usr/bin"
        current_path = environment.get("PATH", "")
        environment["PATH"] = str(git_usr_bin) + os.pathsep + current_path
    return environment


def run(root: Path, args: list[str]) -> str:
    if args != ["bash", ".ai/scripts/check-all.sh", "--critical"]:
        raise RuntimeError("pre-tag preparation may execute only the critical gate")
    command = [bash_executable(), *args[1:]]
    result = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        env=bash_environment(command[0]),
    )
    stdout = (result.stdout or b"").decode("utf-8", errors="replace")
    stderr = (result.stderr or b"").decode("utf-8", errors="replace")
    if result.returncode:
        details = []
        if stdout.strip():
            details.append(f"stdout:\n{stdout.strip()}")
        if stderr.strip():
            details.append(f"stderr:\n{stderr.strip()}")
        detail = "\n\n".join(details)
        raise RuntimeError(
            detail or f"critical gate failed with exit code {result.returncode}"
        )
    return stdout


def single_line_tag_value(value: str, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or any(character in value for character in ('\r', '\n', '"', "\\"))
    ):
        raise RuntimeError(f"{label} must be a non-empty safe single-line value")
    return value.strip()


def checkpoint_ai_model(root: Path) -> str:
    registry_path = root / ".dev/workflows/handoff-checkpoints.yaml"
    try:
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        checkpoint_paths = registry["checkpoints"]
        checkpoint_path = root / checkpoint_paths[-1]
        checkpoint = yaml.safe_load(checkpoint_path.read_text(encoding="utf-8"))
        provenance = checkpoint["execution_provenance"]
    except (
        OSError,
        UnicodeDecodeError,
        yaml.YAMLError,
        KeyError,
        IndexError,
        TypeError,
    ) as exc:
        raise RuntimeError(
            "a registered handoff checkpoint with execution provenance is required"
        ) from exc
    if provenance.get("model_source") == "unavailable":
        raise RuntimeError(
            "the latest handoff checkpoint does not identify an AI model"
        )
    runtime = single_line_tag_value(provenance.get("runtime"), "checkpoint runtime")
    model = single_line_tag_value(provenance.get("model"), "checkpoint model")
    effort = single_line_tag_value(
        provenance.get("reasoning_effort"), "checkpoint reasoning effort"
    )
    source = single_line_tag_value(
        provenance.get("model_source"), "checkpoint model source"
    )
    return f"{runtime} / {model} / reasoning {effort} ({source})"


def compatibility_summary(data: dict) -> str:
    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict):
        raise RuntimeError("release compatibility must be a mapping")
    sources = compatibility.get("automatic_upgrade_sources")
    if not isinstance(sources, list) or not sources:
        raise RuntimeError(
            "release compatibility must declare automatic upgrade sources"
        )
    change = (
        "pre-1.0 breaking release"
        if compatibility.get("breaking_changes") is True
        else "backward-compatible release"
    )
    return single_line_tag_value(
        f"Compatibility: {change}; automatic sources {', '.join(sources)}.",
        "compatibility summary",
    )


def prepare(
    root: Path,
    version: str,
    commit: str | None = None,
    branch: str | None = None,
    ai_model: str | None = None,
    command_runner=run,
    state_runner=subprocess.run,
) -> str:
    """Run only read-only gates and return, but never execute, the tag command."""
    identity = release_state.validate(
        root,
        "candidate",
        version,
        commit,
        branch,
        runner=state_runner,
    )
    if identity["branch"] != "main":
        raise RuntimeError(
            "pre-tag preparation must run from the merged main branch"
        )
    _, data, _, _ = release_state.release_record(root, version)
    model = single_line_tag_value(
        ai_model if ai_model is not None else checkpoint_ai_model(root),
        "AI model",
    )
    summary = compatibility_summary(data)
    command_runner(root, ["bash", ".ai/scripts/check-all.sh", "--critical"])
    release_state.assert_clean_worktree(root, state_runner)
    return (
        f"git tag -a {version} {identity['commit']} "
        f"-m \"REL-{version} - Governed AI Context Release\" "
        f"-m \"{summary}\" "
        f"-m \"AI-Model: {model}\""
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", help="optional assertion; must equal current HEAD")
    parser.add_argument("--branch", help="optional assertion; must equal current branch")
    parser.add_argument(
        "--ai-model",
        help="optional safe single-line override; otherwise use the latest handoff checkpoint",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        tag_command = prepare(
            root,
            args.version,
            args.commit,
            args.branch,
            args.ai_model,
        )
    except (OSError, RuntimeError, release_state.ReleaseStateError) as exc:
        print(f"AI context release preparation failed: {exc}", file=sys.stderr)
        return 1
    print("Pre-tag gates passed. Tag creation remains user-owned.")
    print(tag_command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
