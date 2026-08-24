#!/usr/bin/env python3
"""GWT regression tests for fail-closed shell asset validation.

These tests intentionally operate only on synthetic Git repositories. They
must never change executable modes, index entries, or files in the real repo.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_SOURCE = REPO_ROOT / ".ai/scripts/validate-shell-assets.py"
RUNNER_SOURCE = REPO_ROOT / ".ai/scripts/check-all.sh"
PROFILE_REGISTRY_SOURCE = REPO_ROOT / ".ai/scripts/validation-profile-registry.sh"
EVIDENCE_SOURCE = REPO_ROOT / ".ai/scripts/validation-evidence.py"
TEST_COMPLIANCE_SOURCE = REPO_ROOT / ".ai/scripts/check-test-compliance.sh"
SUBPROCESS_TIMEOUT_SECONDS = 30
RUNNER_TIMEOUT_SECONDS = 60


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_SECONDS,
    )


def real_repo_snapshot() -> tuple[str, str, str]:
    head = run(["git", "rev-parse", "HEAD"], REPO_ROOT)
    status = run(["git", "status", "--porcelain=v1"], REPO_ROOT)
    shell_stage = run(
        ["git", "ls-files", "--stage", "*.sh"],
        REPO_ROOT,
    )
    for result in (head, status, shell_stage):
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
    return head.stdout, status.stdout, shell_stage.stdout


def bash_executable() -> str | None:
    if os.name == "nt":
        candidates = (
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Git/bin/bash.exe",
        )
        return next((str(candidate) for candidate in candidates if candidate.is_file()), None)
    return shutil.which("bash")


class SyntheticShellAssetRepo:
    """Own a disposable repository whose shape matches validator assumptions."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="aic007-shell-assets-")
        self.root = Path(self._temporary.name)
        self.scripts = self.root / ".ai/scripts"
        self.scripts.mkdir(parents=True)
        shutil.copy2(VALIDATOR_SOURCE, self.scripts / VALIDATOR_SOURCE.name)
        shutil.copy2(
            REPO_ROOT / ".ai/scripts/python_prerequisites.py",
            self.scripts / "python_prerequisites.py",
        )
        shutil.copy2(
            REPO_ROOT / ".ai/scripts/python-entrypoints.json",
            self.scripts / "python-entrypoints.json",
        )
        shutil.copy2(REPO_ROOT / "requirements.txt", self.root / "requirements.txt")
        initialized = run(["git", "init", "--quiet"], self.root)
        if initialized.returncode != 0:
            self.close()
            raise RuntimeError(initialized.stderr.strip())

    def close(self) -> None:
        self._temporary.cleanup()

    def add_shell(self, name: str, mode: str = "100755") -> str:
        relative = f".ai/scripts/{name}"
        path = self.root / relative
        path.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8", newline="\n")
        added = run(["git", "add", "--", relative], self.root)
        self._require_success(added)
        mode_flag = "+x" if mode == "100755" else "-x"
        updated = run(["git", "update-index", f"--chmod={mode_flag}", "--", relative], self.root)
        self._require_success(updated)
        return relative

    def add_runner(self, required_children: list[str]) -> str:
        runner = ".ai/scripts/check-all.sh"
        body = ["#!/bin/bash"]
        for child in required_children:
            body.extend(
                (
                    f'run_check "{child}" \\',
                    f'    "Fixture {child}" \\',
                    '    "required" "true" "true"',
                )
            )
        (self.root / runner).write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
        added = run(["git", "add", "--", runner], self.root)
        self._require_success(added)
        updated = run(["git", "update-index", "--chmod=+x", "--", runner], self.root)
        self._require_success(updated)
        return runner

    def add_command_runner(self, required_commands: list[str]) -> str:
        runner = ".ai/scripts/check-all.sh"
        body = ["#!/bin/bash"]
        for command in required_commands:
            body.extend(
                (
                    f'run_command_check "{command}" \\',
                    f'    "Fixture {command}" \\',
                    '    "required" "true" "true"',
                )
            )
        (self.root / runner).write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
        added = run(["git", "add", "--", runner], self.root)
        self._require_success(added)
        updated = run(["git", "update-index", "--chmod=+x", "--", runner], self.root)
        self._require_success(updated)
        return runner

    def write_manifest(
        self,
        *,
        retained: list[str],
        retirement_candidates: list[str] | None = None,
        required_entrypoints: list[str] | None = None,
        check_all_required_scripts: list[str] | None = None,
        check_all_required_commands: list[str] | None = None,
    ) -> None:
        assets = [
            {
                "path": path,
                "role": "context-validator",
                "lifecycle": "active",
                "distribution": "packaged",
                "authority": "structural",
                "replacement": None,
            }
            for path in retained
        ]
        assets.extend(
            {
                "path": path,
                "role": "transitional-helper",
                "lifecycle": "retirement-candidate",
                "distribution": "packaged",
                "authority": "advisory",
                "replacement": "fixture replacement",
            }
            for path in (retirement_candidates or [])
        )
        manifest = {
            "schema_version": "2.0",
            "contract": {
                "distribution_rule": "fixture distribution rule",
                "authority_rule": "fixture authority rule",
            },
            "assets": assets,
            "required_entrypoints": required_entrypoints or [],
            "check_all_required_scripts": check_all_required_scripts or [],
            "check_all_required_commands": check_all_required_commands or [],
        }
        (self.scripts / "shell-assets.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )

    def validate(self) -> subprocess.CompletedProcess[str]:
        return run([sys.executable, str(self.scripts / VALIDATOR_SOURCE.name)], self.root)

    @staticmethod
    def _require_success(result: subprocess.CompletedProcess[str]) -> None:
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())


class SyntheticRunnerRepo:
    """Run an unmodified copied check-all.sh against deterministic stubs."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="aic007-check-all-")
        self.root = Path(self._temporary.name)
        self.scripts = self.root / ".ai/scripts"
        self.bin = self.root / "bin"
        self.validation_logs = self.root / "validation-logs"
        self.scripts.mkdir(parents=True)
        self.bin.mkdir()
        shutil.copy2(RUNNER_SOURCE, self.scripts / RUNNER_SOURCE.name)
        shutil.copy2(PROFILE_REGISTRY_SOURCE, self.scripts / PROFILE_REGISTRY_SOURCE.name)
        shutil.copy2(EVIDENCE_SOURCE, self.scripts / EVIDENCE_SOURCE.name)
        self._write_declared_python_targets()
        self.add_python_stub("python")
        self._write_stub(
            self.bin / "dotnet",
            'if [ -n "${DOTNET_STUB_OUTPUT:-}" ]; then printf "%s\\n" "$DOTNET_STUB_OUTPUT"; fi\n'
            'printf "dotnet %s\\n" "$*" >> .aic-sentinel\nexit "${DOTNET_STUB_EXIT:-0}"',
        )
        self._write_child("check-coding-standards.sh", "CODING_STUB_EXIT")
        self._write_child("check-spec-compliance.sh", "SPEC_STUB_EXIT")
        self._require_success(run(["git", "init", "--quiet"], self.root))
        (self.root / ".git/info/exclude").write_text(
            "/validation-logs/\n/artifacts/\n/.aic-sentinel\n/.aic-evidence-sentinel\n",
            encoding="utf-8",
            newline="\n",
        )
        self._require_success(run(["git", "add", "--all"], self.root))
        self._require_success(
            run(
                [
                    "git",
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "fixture initial state",
                ],
                self.root,
            )
        )

    def close(self) -> None:
        self._temporary.cleanup()

    def remove_child(self, name: str) -> None:
        (self.scripts / name).unlink()

    def _write_declared_python_targets(self) -> None:
        registry = (self.scripts / PROFILE_REGISTRY_SOURCE.name).read_text(
            encoding="utf-8"
        )
        targets = set(re.findall(r'"python ([^"\s]+\.py)(?: [^"]*)?"', registry))
        for relative in sorted(targets):
            target = self.root / relative
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "# Synthetic command target used only for runner admission.\n",
                encoding="utf-8",
                newline="\n",
            )

    def add_python_stub(self, name: str, exit_variable: str = "PYTHON_STUB_EXIT") -> Path:
        path = self.bin / name
        self._write_stub(path, self._python_stub_body(name, exit_variable))
        return path

    @staticmethod
    def _python_stub_body(name: str, exit_variable: str) -> str:
        return (
            'if [ "$1" = ".ai/scripts/validation-evidence.py" ]; then\n'
            '  evidence_command=$2\n'
            '  shift 2\n'
            '  printf "evidence %s %s\\n" "$evidence_command" "$*" >> .aic-evidence-sentinel\n'
            '  case "$evidence_command" in\n'
            '    snapshot)\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        if [ "$1" = "--output" ]; then output=$2; break; fi\n'
            '        shift\n'
            '      done\n'
            '      mkdir -p "$(dirname "$output")"\n'
            '      printf "{\\"schema_version\\":\\"validation-repository-admission-fixture/v1\\"}\\n" > "$output"\n'
            '      if [ -n "${EVIDENCE_STUB_SNAPSHOT_DIRTY_AFTER_CAPTURE:-}" ]; then printf "drift\\n" > "$EVIDENCE_STUB_SNAPSHOT_DIRTY_AFTER_CAPTURE"; fi\n'
            '      [ "${EVIDENCE_STUB_SNAPSHOT_EXIT:-0}" -eq 0 ] || exit "$EVIDENCE_STUB_SNAPSHOT_EXIT"\n'
            '      exit 0\n'
            '      ;;\n'
            '    verify-snapshot)\n'
            '      output=\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        if [ "$1" = "--output" ]; then output=$2; break; fi\n'
            '        shift\n'
            '      done\n'
            '      [ -z "$output" ] || { mkdir -p "$(dirname "$output")"; printf "{}\\n" > "$output"; }\n'
            '      exit "${EVIDENCE_STUB_VERIFY_EXIT:-0}"\n'
            '      ;;\n'
            '    verify-supervision-result)\n'
            '      result_path=\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        if [ "$1" = "--result-path" ]; then result_path=$2; shift 2; continue; fi\n'
            '        shift\n'
            '      done\n'
            '      case "$result_path" in *control-seal.result.json) [ "${EVIDENCE_STUB_SEAL_VERIFY_SUPERVISION_EXIT:-0}" -eq 0 ] || exit "$EVIDENCE_STUB_SEAL_VERIFY_SUPERVISION_EXIT" ;; esac\n'
            '      [ "${EVIDENCE_STUB_VERIFY_SUPERVISION_EXIT:-0}" -eq 0 ] || exit "$EVIDENCE_STUB_VERIFY_SUPERVISION_EXIT"\n'
            '      [ -n "$result_path" ] && [ -f "$result_path" ] && [ -f "$result_path.stub.tsv" ] || exit 1\n'
            '      cat "$result_path.stub.tsv"\n'
            '      exit 0\n'
            '      ;;\n'
            '    verify-terminal-invocation)\n'
            '      manifest=\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        case "$1" in\n'
            '          --manifest) manifest=$2; shift 2 ;;\n'
            '          --) shift; break ;;\n'
            '          *) shift ;;\n'
            '        esac\n'
            '      done\n'
            '      [ "${EVIDENCE_STUB_TERMINAL_VERIFY_EXIT:-0}" -eq 0 ] || exit "$EVIDENCE_STUB_TERMINAL_VERIFY_EXIT"\n'
            '      if [ -n "${EVIDENCE_STUB_TERMINAL_VERIFY_DIGEST:-}" ]; then\n'
            '        printf "%s\\n" "$EVIDENCE_STUB_TERMINAL_VERIFY_DIGEST"\n'
            '      else\n'
            '        sha256sum "$manifest" | awk \'{print $1}\'\n'
            '      fi\n'
            '      exit 0\n'
            '      ;;\n'
            '    supervise)\n'
            '      log_path= result_path= accepted_exit_10=false bootstrap_snapshot_output= stub_bootstrap=false stub_prepare=false\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        case "$1" in\n'
            '          --log-path) log_path=$2; shift 2 ;;\n'
            '          --result-path) result_path=$2; shift 2 ;;\n'
            '          --bootstrap-snapshot-output) bootstrap_snapshot_output=$2; stub_bootstrap=true; shift 2 ;;\n'
            '          --accepted-child-exit-code) [ "$2" != 10 ] || accepted_exit_10=true; shift 2 ;;\n'
            '          --) shift; break ;;\n'
            '          *) shift ;;\n'
            '        esac\n'
            '      done\n'
            '      case " $* " in *" .ai/scripts/validation-evidence.py "*) stub_control=true ;; *) stub_control=false ;; esac\n'
            '      case " $* " in *" .ai/scripts/validation-evidence.py prepare "*) stub_prepare=true ;; esac\n'
            '      case " $* " in *" .ai/scripts/validation-evidence.py seal-invocation "*) stub_terminal_seal=true ;; *) stub_terminal_seal=false ;; esac\n'
            '      if [ "$stub_bootstrap" = true ]; then stub_supervise_exit=${EVIDENCE_STUB_BOOTSTRAP_SUPERVISE_EXIT:-}; elif [ "$stub_prepare" = true ]; then stub_supervise_exit=${EVIDENCE_STUB_PREPARE_SUPERVISE_EXIT:-}; elif [ "$stub_control" = true ]; then stub_supervise_exit=${EVIDENCE_STUB_CONTROL_SUPERVISE_EXIT:-}; else stub_supervise_exit=${EVIDENCE_STUB_SUPERVISE_EXIT:-}; fi\n'
            '      if [ "$stub_terminal_seal" = true ] && [ -n "${EVIDENCE_STUB_SEAL_SUPERVISE_EXIT:-}" ]; then stub_supervise_exit=$EVIDENCE_STUB_SEAL_SUPERVISE_EXIT; fi\n'
            '      if [ "$stub_control" = false ] && [ -z "$stub_supervise_exit" ] && [ "$accepted_exit_10" != true ]; then stub_supervise_exit=${EVIDENCE_STUB_SUPERVISE_EXIT_NON_PREPARATION:-}; fi\n'
            '      if [ -n "$stub_supervise_exit" ]; then\n'
            '        printf "stub supervision exit=%s\\n" "$stub_supervise_exit" > "$log_path"\n'
            '        stub_omit_result=${EVIDENCE_STUB_SUPERVISE_OMIT_RESULT:-false}\n'
            '        if [ "$stub_terminal_seal" = true ] && [ "${EVIDENCE_STUB_SEAL_SUPERVISE_OMIT_RESULT:-false}" = true ]; then stub_omit_result=true; fi\n'
            '        if [ "$stub_omit_result" != true ]; then\n'
            '          case "$stub_supervise_exit" in\n'
            '            124) stub_status=timed-out; stub_launched=true; stub_exit= ;;\n'
            '            125) stub_status=snapshot-drift; stub_launched=true; stub_exit=0 ;;\n'
            '            126) stub_status=cleanup-failed; stub_launched=true; stub_exit=0 ;;\n'
            '            127) stub_status=launch-failed; stub_launched=false; stub_exit= ;;\n'
            '            128) stub_status=snapshot-drift; stub_launched=false; stub_exit= ;;\n'
            '            130) stub_status=cancelled; stub_launched=true; stub_exit= ;;\n'
            '            *) stub_status=completed; stub_launched=true; stub_exit=$stub_supervise_exit ;;\n'
            '          esac\n'
            '          printf "{\\"status\\":\\"%s\\",\\"exit_code\\":%s}\\n" "$stub_status" "${stub_exit:-null}" > "$result_path"\n'
            '          printf "%s\\t%s\\t%s\\n" "$stub_status" "$stub_launched" "$stub_exit" > "$result_path.stub.tsv"\n'
            '        fi\n'
            '        exit "$stub_supervise_exit"\n'
            '      fi\n'
            '      if [ "$stub_bootstrap" = true ]; then\n'
            '        mkdir -p "$(dirname "$bootstrap_snapshot_output")"\n'
            '        printf "{\\"schema_version\\":\\"validation-repository-admission-fixture/v1\\"}\\n" > "$bootstrap_snapshot_output"\n'
            '        if [ -n "${EVIDENCE_STUB_SNAPSHOT_DIRTY_AFTER_CAPTURE:-}" ]; then printf "drift\\n" > "$EVIDENCE_STUB_SNAPSHOT_DIRTY_AFTER_CAPTURE"; fi\n'
            '        [ "${EVIDENCE_STUB_SNAPSHOT_EXIT:-0}" -eq 0 ] || exit "$EVIDENCE_STUB_SNAPSHOT_EXIT"\n'
            '      fi\n'
            '      "$@" > "$log_path" 2>&1\n'
            '      rc=$?\n'
            '      printf "{\\n  \\"execution\\": {\\n    \\"launched\\": true\\n  },\\n  \\"exit_code\\": %s,\\n  \\"schema_version\\": \\"validation-supervision-result/v1\\",\\n  \\"status\\": \\"completed\\",\\n  \\"timeout_seconds\\": 30\\n}\\n" "$rc" > "$result_path"\n'
            '      printf "completed\\ttrue\\t%s\\n" "$rc" > "$result_path.stub.tsv"\n'
            '      [ "$rc" -eq 0 ] && exit 0\n'
            '      [ "$rc" -eq 10 ] && [ "$accepted_exit_10" = true ] && exit 0\n'
            '      exit 1\n'
            '      ;;\n'
            '    prepare)\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        if [ "$1" = "--selection" ]; then selection=$2; break; fi\n'
            '        shift\n'
            '      done\n'
            '      fixture_first=true\n'
            '      while IFS="$(printf \'\\t\')" read -r validator_id _; do\n'
            '        if [ -n "$validator_id" ]; then\n'
            '          fixture_reuse=${EVIDENCE_STUB_REUSE:-false}\n'
            '          fixture_prior_log=\n'
            '          [ "$fixture_reuse" != true ] || fixture_prior_log="fixture-cache/$validator_id.log"\n'
            '          fixture_output_id=$validator_id\n'
            '          fixture_fingerprint=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n'
            '          fixture_suffix=\n'
            '          if [ "$fixture_first" = true ]; then\n'
            '            case "${EVIDENCE_STUB_PREPARE_MODE:-valid}" in\n'
            '              unknown-id) fixture_output_id=unknown-check ;;\n'
            '              invalid-fingerprint) fixture_fingerprint=invalid ;;\n'
            '              invalid-cache) fixture_reuse=maybe; fixture_prior_log= ;;\n'
            '              extra-column) fixture_suffix="$(printf \'\\textra\')" ;;\n'
            '              missing-row) fixture_first=false; continue ;;\n'
            '              crlf-invalid-id) fixture_output_id=invalid_id ;;\n'
            '              crlf-invalid-fingerprint) fixture_fingerprint=invalid ;;\n'
            '              crlf-invalid-cache) fixture_reuse=maybe; fixture_prior_log= ;;\n'
            '              crlf-false-prior-log) fixture_reuse=false; fixture_prior_log="fixture-cache/$validator_id.log" ;;\n'
            '              crlf-extra-column) fixture_suffix="$(printf \'\\textra\')" ;;\n'
            '              crlf-internal-cr) fixture_output_id="$(printf "%s\\r" "$fixture_output_id")" ;;\n'
            '            esac\n'
            '          fi\n'
            '          if [[ "${EVIDENCE_STUB_PREPARE_MODE:-valid}" = crlf-* ]]; then\n'
            '            printf "%s\\t%s\\t%s\\t%s%s\\r\\n" "$fixture_output_id" "$fixture_fingerprint" "$fixture_reuse" "$fixture_prior_log" "$fixture_suffix"\n'
            '          else\n'
            '            printf "%s\\t%s\\t%s\\t%s%s\\n" "$fixture_output_id" "$fixture_fingerprint" "$fixture_reuse" "$fixture_prior_log" "$fixture_suffix"\n'
            '          fi\n'
            '          if [ "$fixture_first" = true ] && [ "${EVIDENCE_STUB_PREPARE_MODE:-valid}" = duplicate-id ]; then\n'
            '            printf "%s\\t%s\\t%s\\t%s\\n" "$fixture_output_id" "$fixture_fingerprint" "$fixture_reuse" "$fixture_prior_log"\n'
            '          fi\n'
            '          fixture_first=false\n'
            '        fi\n'
            '      done < "$selection"\n'
            '      exit 0\n'
            '      ;;\n'
            '    summarize|workflow-summary)\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        if [ "$1" = "--output" ]; then output=$2; break; fi\n'
            '        shift\n'
            '      done\n'
            '      [ -z "$output" ] || printf "{}\\n" > "$output"\n'
            '      exit 0\n'
            '      ;;\n'
            '    seal-invocation)\n'
            '      output= publication_output=\n'
            '      while [ "$#" -gt 0 ]; do\n'
            '        case "$1" in\n'
            '          --output) output=$2; shift 2 ;;\n'
            '          --publication-output) publication_output=$2; shift 2 ;;\n'
            '          *) shift ;;\n'
            '        esac\n'
            '      done\n'
            '      if [ "${EVIDENCE_STUB_SEAL_WRITE_BEFORE_EXIT:-false}" = true ] && [ -n "$output" ]; then printf "{}\\n" > "$output"; fi\n'
            '      [ "${EVIDENCE_STUB_SEAL_EXIT:-0}" -eq 0 ] || exit "$EVIDENCE_STUB_SEAL_EXIT"\n'
            '      [ -z "$output" ] || printf "{}\\n" > "$output"\n'
            '      if [ "${EVIDENCE_STUB_PRECREATE_PUBLICATION_OUTPUT:-false}" = true ] && [ -n "$publication_output" ]; then printf "pre-existing\\n" > "$publication_output"; printf "stub precreated publication=%s\\n" "$publication_output"; fi\n'
            '      if [ "${EVIDENCE_STUB_SIGNAL_DURING_SEAL:-false}" = true ]; then kill -TERM "${AI_CONTEXT_VALIDATION_RUNNER_PID:-$PPID}"; fi\n'
            '      exit 0\n'
            '      ;;\n'
            '    finalize) exit "${EVIDENCE_STUB_FINALIZE_EXIT:-0}" ;;\n'
            '  esac\n'
            'fi\n'
            'if [ "$1" = ".ai/scripts/validate-immutable-history.py" ] && [ "$2" = "verify" ]; then\n'
            f'  printf "{name} %s\\n" "$*" >> .aic-sentinel\n'
            '  if [ ! -f .ai/distribution/validation/immutable-history-receipt.yaml ]; then printf "full-required\\tmissing-receipt\\t1111111111111111111111111111111111111111\\t2222222222222222222222222222222222222222\\t3333333333333333333333333333333333333333\\t\\n"; exit 10; fi\n'
            '  case "${IMMUTABLE_HISTORY_STUB_MODE:-error}" in\n'
            '    reusable) printf "routine-reusable\\treceipt-valid\\t1111111111111111111111111111111111111111\\t2222222222222222222222222222222222222222\\t3333333333333333333333333333333333333333\\tworkflow-artifacts,assessment-artifacts,source-ai-context-version\\n"; exit 0 ;;\n'
            '    full) printf "full-required\\timmutable-history-change\\t1111111111111111111111111111111111111111\\t2222222222222222222222222222222222222222\\t3333333333333333333333333333333333333333\\t\\n"; exit 10 ;;\n'
            '    crlf-full) printf "full-required\\tprofile-requires-full-validation\\t\\t\\t\\t\\r\\n"; exit 10 ;;\n'
            '    crlf-full-with-identity-cr) printf "full-required\\tprofile-requires-full-validation\\t\\r\\t\\t\\t\\r\\n"; exit 10 ;;\n'
            '    crlf-full-with-reusable-ids) printf "full-required\\tprofile-requires-full-validation\\t\\t\\t\\tworkflow-artifacts\\r\\n"; exit 10 ;;\n'
            '    crlf-full-extra-column) printf "full-required\\tprofile-requires-full-validation\\t\\t\\t\\t\\textra\\r\\n"; exit 10 ;;\n'
            '    forged-full) printf "full-required\\timmutable-history-change\\t1111111111111111111111111111111111111111\\t2222222222222222222222222222222222222222\\t3333333333333333333333333333333333333333\\t\\n"; exit 1 ;;\n'
            '    *) printf "configuration-error\\tfixture-error\\t\\t\\t\\t\\n"; exit 2 ;;\n'
            '  esac\n'
            'fi\n'
            f'printf "{name} %s\\n" "$*" >> .aic-sentinel\nexit "${{{exit_variable}:-0}}"'
        )

    def enable_source_release_context(self) -> None:
        (self.root / ".dev/releases").mkdir(parents=True)
        (self.root / ".ai/distribution").mkdir(parents=True)
        (self.scripts / "ai_context_package.py").write_text(
            "# source-only package builder marker\n",
            encoding="utf-8",
            newline="\n",
        )

    def enable_immutable_history_context(self) -> None:
        for path in (
            self.root / ".dev/workflows",
            self.root / ".dev/assessments",
            self.root / ".dev/releases",
            self.root / ".ai/distribution/validation",
        ):
            path.mkdir(parents=True, exist_ok=True)
        for path in (
            self.scripts / "validate-immutable-history.py",
            self.root / ".ai/distribution/validation/immutable-history-validation.yaml",
            self.root / ".ai/distribution/validation/immutable-history-receipt.yaml",
        ):
            path.write_text("# immutable history fixture marker\n", encoding="utf-8")

    def enable_source_governance_context(self) -> None:
        workflow = self.root / ".github/workflows/governance.yml"
        registry = self.root / ".ai/distribution/governance-checks.yaml"
        validator = self.scripts / "validate-source-governance.py"
        workflow.parent.mkdir(parents=True)
        registry.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("# source-only governance workflow marker\n", encoding="utf-8")
        registry.write_text("# source-only governance registry marker\n", encoding="utf-8")
        validator.write_text("# source-only governance validator marker\n", encoding="utf-8")

    def execute(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        bash = bash_executable()
        if not bash:
            raise unittest.SkipTest("Bash is required for check-all.sh fixture tests")
        merged_environment = {
            key: value for key, value in os.environ.items() if not key.startswith("BASH_FUNC_")
        }
        merged_environment["PATH"] = str(self.bin) + os.pathsep + merged_environment["PATH"]
        merged_environment.pop("SPEC_FILE", None)
        merged_environment.pop("TASK_NAME", None)
        merged_environment.pop("COMMIT_RANGE", None)
        merged_environment.pop("WORKFLOW_ID", None)
        merged_environment.pop("AI_CONTEXT_PYTHON", None)
        merged_environment.pop("VIRTUAL_ENV", None)
        if environment:
            merged_environment.update(environment)
        return subprocess.run(
            [bash, str(self.scripts / RUNNER_SOURCE.name), *arguments],
            cwd=self.root,
            env=merged_environment,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=RUNNER_TIMEOUT_SECONDS,
        )

    def sentinel(self) -> list[str]:
        path = self.root / ".aic-sentinel"
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def evidence_sentinel(self) -> list[str]:
        path = self.root / ".aic-evidence-sentinel"
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def invocation_directories(self) -> list[Path]:
        if not self.validation_logs.exists():
            return []
        return sorted(path for path in self.validation_logs.iterdir() if path.is_dir())

    def override_dependencies(self, **dependencies_by_id: str) -> None:
        with (self.scripts / PROFILE_REGISTRY_SOURCE.name).open(
            "a", encoding="utf-8", newline="\n"
        ) as registry:
            for check_id, dependencies in dependencies_by_id.items():
                registry.write(f'CHECK_DEPENDS["{check_id}"]="{dependencies}"\n')

    def override_input_paths(self, **input_paths_by_id: str) -> None:
        with (self.scripts / PROFILE_REGISTRY_SOURCE.name).open(
            "a", encoding="utf-8", newline="\n"
        ) as registry:
            for check_id, input_paths in input_paths_by_id.items():
                registry.write(f'CHECK_INPUT_PATHS["{check_id}"]="{input_paths}"\n')

    def override_commands(self, **commands_by_id: str) -> None:
        with (self.scripts / PROFILE_REGISTRY_SOURCE.name).open(
            "a", encoding="utf-8", newline="\n"
        ) as registry:
            for check_id, command in commands_by_id.items():
                registry.write(f'CHECK_COMMAND["{check_id}"]="{command}"\n')

    def restrict_profile_to(self, profile: str, *check_ids: str) -> None:
        fallback_profile = "nightly-full" if profile != "nightly-full" else "release"
        with (self.scripts / PROFILE_REGISTRY_SOURCE.name).open(
            "a", encoding="utf-8", newline="\n"
        ) as registry:
            registry.write(
                'for fixture_id in "${CHECK_IDS[@]}"; do '
                f'CHECK_PROFILES["$fixture_id"]="{fallback_profile}"; done\n'
            )
            for check_id in check_ids:
                registry.write(f'CHECK_PROFILES["{check_id}"]="{profile}"\n')

    def create_changed_path_revisions(self, relative_path: str) -> tuple[str, str]:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("baseline\n", encoding="utf-8", newline="\n")
        self._require_success(run(["git", "init", "--quiet"], self.root))
        (self.root / ".git/info/exclude").write_text(
            "/validation-logs/\n/artifacts/\n/.aic-sentinel\n/.aic-evidence-sentinel\n",
            encoding="utf-8",
            newline="\n",
        )
        commands = (
            ["git", "add", "--all"],
            [
                "git",
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "--quiet",
                "-m",
                "fixture baseline",
            ],
        )
        for command in commands:
            self._require_success(run(command, self.root))
        base = self._require_stdout(run(["git", "rev-parse", "HEAD"], self.root))
        path.write_text("changed\n", encoding="utf-8", newline="\n")
        self._require_success(run(["git", "add", "--", relative_path], self.root))
        self._require_success(
            run(
                [
                    "git",
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "fixture change",
                ],
                self.root,
            )
        )
        head = self._require_stdout(run(["git", "rev-parse", "HEAD"], self.root))
        return base, head

    def selected_evidence_files(self) -> list[Path]:
        return sorted(self.validation_logs.glob("*/selected-checks.tsv"))

    @staticmethod
    def selected_rows(path: Path) -> list[tuple[str, str]]:
        return [
            tuple(line.split("\t", 1))
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]

    @staticmethod
    def _require_success(result: subprocess.CompletedProcess[str]) -> None:
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

    @staticmethod
    def _require_stdout(result: subprocess.CompletedProcess[str]) -> str:
        SyntheticRunnerRepo._require_success(result)
        return result.stdout.strip()

    def _write_child(self, name: str, exit_variable: str) -> None:
        self._write_stub(
            self.scripts / name,
            f'if [ -n "${{{exit_variable}_OUTPUT:-}}" ]; then printf "%s\\n" "${{{exit_variable}_OUTPUT}}"; fi\n'
            f'printf "{name} %s\\n" "$*" >> .aic-sentinel\nexit "${{{exit_variable}:-0}}"',
        )

    @staticmethod
    def _write_stub(path: Path, body: str) -> None:
        path.write_text(f"#!/bin/bash\n{body}\n", encoding="utf-8", newline="\n")
        path.chmod(0o755)


class CheckAllRunnerGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_before = real_repo_snapshot()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.real_before != real_repo_snapshot():
            raise AssertionError("check-all fixture tests mutated the real repository")

    def test_gwt_001_given_required_script_missing_when_critical_runs_then_gate_fails(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the selected required child script is absent.
            fixture.remove_child("check-coding-standards.sh")

            # When critical mode executes the copied runner.
            result = fixture.execute(
                "--critical",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_REUSE": "true",
                },
            )

            # Then the aggregate fails and records an unexecuted required check.
            self.assertEqual(1, result.returncode)
            self.assertIn("FAILED", result.stdout)
            self.assertIn("check-coding-standards.sh not found", result.stdout)
            self.assertIn("Required Selected:", result.stdout)
            self.assertIn("Required Executed:", result.stdout)
            self.assertIn("Required Failed:", result.stdout)
            invocation = fixture.invocation_directories()[0]
            coding_event = next(
                row.split("\t")
                for row in (invocation / "evidence-events.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if row.startswith("coding-standards-structural\t")
            )
            self.assertEqual("not-executed", coding_event[4])
            self.assertEqual("false", coding_event[7])
            self.assertEqual("", coding_event[12])
        finally:
            fixture.close()

    def test_gwt_003_given_required_script_nonzero_when_selected_then_counted_once(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the required coding check returns 17.
            # When critical mode executes.
            result = fixture.execute("--critical", environment={"CODING_STUB_EXIT": "17"})

            # Then the aggregate fails exactly one required check.
            self.assertEqual(1, result.returncode)
            self.assertIn("Coding Standards Structural Integrity returned non-zero", result.stdout)
            self.assertRegex(result.stdout, r"Required Failed: .*1")
        finally:
            fixture.close()

    def test_gwt_004_given_source_context_without_dotnet_when_selected_then_no_sdk_command_runs(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given source-only checks are selected and any accidental dotnet
            # invocation would fail with command-not-found semantics.
            fixture.enable_source_release_context()
            result = fixture.execute(
                "--critical",
                environment={
                    "DOTNET_STUB_EXIT": "127",
                    "DOTNET_STUB_OUTPUT": "bash: dotnet: command not found",
                },
            )

            # Then the source framework passes without selecting the dotnet
            # stub, while the SDK-free Python contract is selected.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            sentinel = fixture.sentinel()
            self.assertFalse(any(line.startswith("dotnet ") for line in sentinel))
            self.assertTrue(
                any("test_sdk_free_framework_contract.py" in line for line in sentinel),
                sentinel,
            )
        finally:
            fixture.close()

    def test_gwt_004c_given_read_only_child_when_critical_runs_then_gate_is_blocked(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given a required child reports a read-only filesystem.
            # When critical mode runs.
            result = fixture.execute(
                "--critical",
                environment={
                    "CODING_STUB_EXIT": "1",
                    "CODING_STUB_EXIT_OUTPUT": "Read-only file system",
                },
            )

            # Then it remains non-passing and reports an environment block.
            self.assertEqual(3, result.returncode, result.stdout + result.stderr)
            self.assertIn("read-only-filesystem", result.stdout)
            self.assertRegex(result.stdout, r"Required Failed: .*0")
            self.assertRegex(result.stdout, r"Required Blocked: .*1")
        finally:
            fixture.close()

    def test_gwt_005_given_retirement_candidate_when_modes_run_then_it_is_never_selected(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the stale helper is a packaged retirement candidate.
            # When every supported mode executes.
            results = (
                fixture.execute("--critical"),
                fixture.execute("--quick"),
                fixture.execute("--full"),
            )

            # Then no aggregate mode routes to its obsolete policy.
            for result in results:
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertNotIn("Test Standards Compliance", result.stdout)
                self.assertIn("reused=0", result.stdout)
                self.assertIn("full-log:", result.stdout)
                self.assertNotIn("Elapsed By Check (slowest first)", result.stdout)
                self.assertRegex(
                    result.stdout,
                    r"AI_CONTEXT_CHECK_TIMING total_seconds=\d+ profile=\S+ checks=\d+ executed=\d+ reused=0 failed=0 blocked=0",
                )
        finally:
            fixture.close()

    def test_gwt_006_given_no_spec_inputs_when_quick_runs_then_spec_is_not_applicable(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given both conditional spec inputs and source release context are absent.
            # When quick mode reaches spec compliance.
            result = fixture.execute("--quick")

            # Then target-inapplicable checks and optional inputs record N/A without failing.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("source governance registry not packaged", result.stdout)
            self.assertIn("source CI workflow not packaged", result.stdout)
            self.assertIn("Spec Implementation Compliance", result.stdout)
            self.assertRegex(result.stdout, r"not-applicable=\d+")
            self.assertRegex(result.stdout, r"Required Failed: .*0")
            self.assertFalse(
                any(
                    "test_ai_context_version_governance.py" in line
                    or "test_ai_context_packaging.py -v" in line
                    or "validate-source-governance.py" in line
                    or "test_repository_identity.py" in line
                    or "test_governance_workflow_contract.py" in line
                    for line in fixture.sentinel()
                )
            )
        finally:
            fixture.close()

    def test_gwt_007_given_partial_spec_inputs_when_quick_runs_then_configuration_fails(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            for environment in ({"SPEC_FILE": "spec.json"}, {"TASK_NAME": "task"}):
                with self.subTest(environment=environment):
                    # Given exactly one conditional-required input is present.
                    # When quick mode reaches spec compliance.
                    result = fixture.execute("--quick", environment=environment)

                    # Then configuration fails before the spec child launches.
                    self.assertEqual(1, result.returncode)
                    self.assertIn("requires both SPEC_FILE and TASK_NAME", result.stdout)
                    self.assertFalse(
                        any(line.startswith("check-spec-compliance.sh") for line in fixture.sentinel())
                    )
        finally:
            fixture.close()

    def test_gwt_007a_given_source_governance_paths_without_release_context_then_checks_are_not_applicable(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given a downstream happens to retain the two source governance paths.
            fixture.enable_source_governance_context()

            # When the critical gate runs without source release/build identity.
            result = fixture.execute("--critical")

            # Then source-pinned Git/tag validation remains not applicable.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("source governance registry not packaged", result.stdout)
            self.assertFalse(
                any(
                    "validate-source-governance.py" in line
                    or "test_repository_identity.py" in line
                    or "test_governance_workflow_contract.py" in line
                    for line in fixture.sentinel()
                )
            )
        finally:
            fixture.close()

    def test_gwt_007b_given_pending_target_apply_receipt_without_provenance_when_critical_runs_then_target_validation_is_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given a downstream pending receipt but no finalized target provenance.
            receipt = fixture.root / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
            receipt.parent.mkdir(parents=True)
            receipt.write_text("schema_version: '1.1.0'\n", encoding="utf-8")

            # When the critical gate is selected.
            result = fixture.execute("--critical")

            # Then the target validator is selected as a required check, not N/A.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("target-ai-context-version", result.stdout)
            self.assertTrue(
                any(
                    "validate-ai-context-target.py" in line
                    for line in fixture.sentinel()
                )
            )
        finally:
            fixture.close()

    def test_gwt_008_given_complete_spec_inputs_when_quick_runs_then_child_result_is_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            base = {"SPEC_FILE": "spec.json", "TASK_NAME": "task"}
            # Given both inputs exist, when the spec child passes, then the gate passes.
            passing = fixture.execute("--quick", environment=base)
            self.assertEqual(0, passing.returncode, passing.stdout + passing.stderr)

            # Given both inputs exist, when the spec child fails, then the gate fails.
            failing = fixture.execute("--quick", environment={**base, "SPEC_STUB_EXIT": "4"})
            self.assertEqual(1, failing.returncode)
            self.assertIn("Spec Implementation Compliance (.NET) returned non-zero", failing.stdout)
        finally:
            fixture.close()

    def test_gwt_009_given_dependency_gate_when_quick_runs_then_it_is_required_not_deferred(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the offline dependency validator and its fixtures are declared required.
            # When quick mode reaches the dependency gate.
            result = fixture.execute("--quick")

            # Then both commands execute and no dependency deferral remains.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("DEFERRED: Dependencies and Versions", result.stdout)
            self.assertIn("dependency-versions", result.stdout)
            self.assertIn("dependency-versions-tests", result.stdout)
            self.assertTrue(
                any("validate-dependency-versions.py" in line for line in fixture.sentinel())
            )
            self.assertTrue(
                any("test_dependency_version_consistency.py" in line for line in fixture.sentinel())
            )
            self.assertIn("deferred=0", result.stdout)
            self.assertRegex(result.stdout, r"Required Failed: .*0")
        finally:
            fixture.close()

    def test_gwt_009_language_gate_when_quick_runs_then_it_is_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the language and bilingual parity fixtures are a required gate.
            # When quick mode reaches the AI context validators.
            result = fixture.execute("--quick")

            # Then the language suite executes and remains fail closed.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("ai-context-language-policy", result.stdout)
            self.assertTrue(
                any(
                    "test_ai_context_language_policy.py -v" in line
                    for line in fixture.sentinel()
                )
            )
            self.assertRegex(result.stdout, r"Required Failed: .*0")
        finally:
            fixture.close()

    def test_gwt_010_given_modes_when_each_runs_then_selection_and_default_are_truthful(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given identical passing stubs, when each supported mode executes.
            critical = fixture.execute("--critical")
            quick = fixture.execute("--quick")
            full = fixture.execute("--full")
            default = fixture.execute()

            # Then all pass, mode labels are truthful, and default selects full behavior.
            for result in (critical, quick, full, default):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Profile: ", critical.stdout)
            self.assertIn("release", critical.stdout)
            self.assertIn("pr", quick.stdout)
            self.assertIn("nightly-full", full.stdout)
            self.assertEqual(
                [line.split()[0] for line in full.stdout.splitlines() if line.rstrip().endswith("executed")],
                [line.split()[0] for line in default.stdout.splitlines() if line.rstrip().endswith("executed")],
            )
            self.assertNotIn("Test Standards Compliance", critical.stdout)
            self.assertNotIn("Test Standards Compliance", quick.stdout)
            self.assertNotIn("Test Standards Compliance", full.stdout)
        finally:
            fixture.close()

    def test_gwt_011_given_invalid_cli_when_runner_starts_then_no_check_launches(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given invalid arguments, when the runner parses them.
            unknown = fixture.execute("--unknown")
            extra = fixture.execute("--quick", "--full")
            help_result = fixture.execute("--help")

            # Then invalid forms exit 2, help exits 0, and no checks launch.
            self.assertEqual(2, unknown.returncode)
            self.assertEqual(2, extra.returncode)
            self.assertEqual(0, help_result.returncode)
            self.assertIn("Usage:", unknown.stderr)
            self.assertIn("Usage:", extra.stderr)
            self.assertIn("Usage:", help_result.stdout)
            self.assertIn("--quick       --profile pr", help_result.stdout)
            self.assertIn("--critical    --profile release", help_result.stdout)
            self.assertEqual([], fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_011a_given_profile_selection_when_runner_starts_then_membership_is_registry_driven(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the canonical registry supplies five named profiles and
            # source-only checks can execute when their profile selects them.
            fixture.enable_source_release_context()
            fast = fixture.execute("--profile", "fast")
            pr = fixture.execute("--profile", "pr")
            release = fixture.execute("--profile", "release")

            # When each profile is selected directly, then its declared
            # membership is visible and progressively stronger without the
            # legacy aliases hiding the selected profile.
            for result, profile in ((fast, "fast"), (pr, "pr"), (release, "release")):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(f"profile={profile}", result.stdout)
                self.assertIn("full-log:", result.stdout)

            def executed_check_ids(output: str) -> set[str]:
                return {
                    fields[0]
                    for line in output.splitlines()
                    if (fields := line.split()) and fields[-1] == "executed"
                }

            self.assertNotIn("package-full-matrix", executed_check_ids(fast.stdout))
            self.assertNotIn("package-full-matrix", executed_check_ids(pr.stdout))
            self.assertIn("package-full-matrix", executed_check_ids(release.stdout))
            self.assertTrue(
                any("test_ai_context_package_apply.py -v" in line for line in fixture.sentinel())
            )
            self.assertTrue(
                any("test_ai_context_packaging.py -v" in line for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_012_given_source_release_context_when_critical_runs_then_source_tests_are_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the runner can prove it is executing in the source release repository.
            fixture.enable_source_release_context()
            fixture.enable_source_governance_context()

            # When the critical gate executes.
            result = fixture.execute("--critical")

            # Then both source-only suites and the downstream-safe apply suite execute.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(
                any("test_ai_context_version_governance.py -v" in line for line in commands)
            )
            self.assertTrue(any("test_ai_context_packaging.py -v" in line for line in commands))
            self.assertTrue(
                any("validate-source-governance.py" in line for line in commands)
            )
            self.assertTrue(
                any("test_repository_identity.py -v" in line for line in commands)
            )
            self.assertTrue(
                any("test_governance_workflow_contract.py -v" in line for line in commands)
            )
            self.assertTrue(
                any("test_ai_context_package_apply.py -v" in line for line in commands)
            )
            self.assertNotIn("source release context not packaged", result.stdout)
            self.assertNotIn("source governance registry not packaged", result.stdout)
        finally:
            fixture.close()

    def test_gwt_012a_given_valid_history_receipt_when_fast_runs_then_native_history_validators_are_reused(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "fast",
                environment={
                    "IMMUTABLE_HISTORY_STUB_MODE": "reusable",
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                },
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            lines = {line.split()[0]: line for line in result.stdout.splitlines() if line.split()}
            self.assertTrue(lines["workflow-artifacts"].rstrip().endswith("reused"))
            self.assertTrue(lines["assessment-artifacts"].rstrip().endswith("reused"))
            self.assertTrue(lines["source-ai-context-version"].rstrip().endswith("reused"))
            commands = fixture.sentinel()
            self.assertTrue(
                any("validate-immutable-history.py verify" in line for line in commands)
            )
            self.assertFalse(
                any("validate-workflow-artifacts.py" in line for line in commands)
            )
            self.assertFalse(
                any("validate-assessment-artifacts.py" in line for line in commands)
            )
            self.assertFalse(
                any("validate-ai-context-versions.py" in line for line in commands)
            )
            evidence_commands = fixture.evidence_sentinel()
            preparation_calls = [
                line
                for line in evidence_commands
                if line.startswith("evidence supervise ")
                and "validate-immutable-history.py verify" in line
            ]
            self.assertEqual(1, len(preparation_calls), preparation_calls)
            self.assertIn("--repo . --profile fast --output-format tsv", preparation_calls[0])
            self.assertIn("--accepted-child-exit-code 10", preparation_calls[0])
            self.assertNotIn(" -- bash -c ", preparation_calls[0])
            self.assertTrue(
                any(
                    line.startswith("evidence finalize ")
                    and "--preparation-python" in line
                    for line in evidence_commands
                )
            )
            seal_call = next(
                line for line in evidence_commands if line.startswith("evidence seal-invocation ")
            )
            self.assertIn("--preparation-result", seal_call)
            self.assertIn("immutable-history-preparation.result.json", seal_call)
            self.assertIn("--cache", seal_call)

            events_path = fixture.invocation_directories()[0] / "evidence-events.tsv"
            events = {
                columns[0]: columns
                for columns in (
                    line.split("\t")
                    for line in events_path.read_text(encoding="utf-8").splitlines()
                )
            }
            for validator_id in (
                "workflow-artifacts",
                "assessment-artifacts",
                "source-ai-context-version",
            ):
                self.assertEqual(
                    "immutable-history-preparation.result.json",
                    events[validator_id][12],
                )
                reuse_log = (
                    fixture.invocation_directories()[0] / f"{validator_id}.log"
                ).read_text(encoding="utf-8")
                self.assertIn(
                    "prior_log=.ai/distribution/validation/immutable-history-receipt.yaml",
                    reuse_log,
                )
        finally:
            fixture.close()

    def test_gwt_012b_given_history_change_when_fast_runs_then_all_native_history_validators_execute(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "fast",
                environment={"IMMUTABLE_HISTORY_STUB_MODE": "full"},
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(any("validate-workflow-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-assessment-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-ai-context-versions.py" in line for line in commands))
            self.assertIn("reused=0", result.stdout)
        finally:
            fixture.close()

    def test_gwt_012c_given_release_gate_when_local_cache_is_eligible_then_history_validators_still_execute(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "release",
                environment={
                    "IMMUTABLE_HISTORY_STUB_MODE": "full",
                    "EVIDENCE_STUB_REUSE": "true",
                },
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(any("validate-immutable-history.py verify" in line for line in commands))
            self.assertTrue(any("validate-workflow-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-assessment-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-ai-context-versions.py" in line for line in commands))
        finally:
            fixture.close()

    def test_gwt_012d_given_history_receipt_is_missing_when_fast_runs_then_native_history_validators_execute(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()
            (
                fixture.root
                / ".ai/distribution/validation/immutable-history-receipt.yaml"
            ).unlink()

            result = fixture.execute("--profile", "fast")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(any("validate-immutable-history.py verify" in line for line in commands))
            self.assertTrue(any("validate-workflow-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-assessment-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-ai-context-versions.py" in line for line in commands))
        finally:
            fixture.close()

    def test_gwt_012e_given_history_verifier_has_configuration_error_when_fast_runs_then_runner_stops_before_checks(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "fast",
                environment={"IMMUTABLE_HISTORY_STUB_MODE": "error"},
            )

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "Immutable history validation preparation failed",
                result.stderr,
            )
            commands = fixture.sentinel()
            self.assertTrue(
                any("validate-immutable-history.py verify" in line for line in commands)
            )
            self.assertFalse(
                any("validate-workflow-artifacts.py" in line for line in commands)
            )
            self.assertFalse(
                any("validate-assessment-artifacts.py" in line for line in commands)
            )
            self.assertFalse(
                any("validate-ai-context-versions.py" in line for line in commands)
            )
        finally:
            fixture.close()

    def test_gwt_012f_given_full_required_text_with_wrong_child_exit_when_prepared_then_runner_stops_before_checks(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "fast",
                environment={"IMMUTABLE_HISTORY_STUB_MODE": "forged-full"},
            )

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "Immutable history validation preparation failed",
                result.stderr,
            )
            commands = fixture.sentinel()
            self.assertTrue(any("validate-immutable-history.py verify" in line for line in commands))
            self.assertFalse(any("validate-workflow-artifacts.py" in line for line in commands))
            self.assertFalse(any("validate-assessment-artifacts.py" in line for line in commands))
            self.assertFalse(any("validate-ai-context-versions.py" in line for line in commands))
        finally:
            fixture.close()

    def test_gwt_012g_given_crlf_full_required_decision_without_identities_when_release_runs_then_native_history_validators_execute(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "release",
                environment={"IMMUTABLE_HISTORY_STUB_MODE": "crlf-full"},
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(any("validate-immutable-history.py verify" in line for line in commands))
            self.assertTrue(any("validate-workflow-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-assessment-artifacts.py" in line for line in commands))
            self.assertTrue(any("validate-ai-context-versions.py" in line for line in commands))
        finally:
            fixture.close()

    def test_gwt_012h_given_crlf_full_required_decision_has_identity_or_shape_data_when_fast_runs_then_runner_stops_before_checks(self) -> None:
        for mode in (
            "crlf-full-with-identity-cr",
            "crlf-full-with-reusable-ids",
            "crlf-full-extra-column",
        ):
            with self.subTest(mode=mode):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.enable_source_release_context()
                    fixture.enable_immutable_history_context()

                    result = fixture.execute(
                        "--profile",
                        "fast",
                        environment={"IMMUTABLE_HISTORY_STUB_MODE": mode},
                    )

                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                    commands = fixture.sentinel()
                    self.assertTrue(
                        any("validate-immutable-history.py verify" in line for line in commands)
                    )
                    self.assertFalse(
                        any("validate-workflow-artifacts.py" in line for line in commands)
                    )
                    self.assertFalse(
                        any("validate-assessment-artifacts.py" in line for line in commands)
                    )
                    self.assertFalse(
                        any("validate-ai-context-versions.py" in line for line in commands)
                    )
                finally:
                    fixture.close()

    def test_gwt_013_given_explicit_python3_when_critical_runs_then_runner_uses_it(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the host selects a usable python3 executable explicitly.
            fixture.add_python_stub("python3")

            # When the critical gate executes with the supported override.
            result = fixture.execute(
                "--critical",
                environment={"AI_CONTEXT_PYTHON": "python3"},
            )

            # Then required Python commands use that interpreter and the gate passes.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(
                any(line.startswith("python3 ") for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_014_given_explicit_python_missing_when_gate_starts_then_it_is_blocked(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given an explicit interpreter selection cannot be resolved.
            # When the critical gate starts.
            result = fixture.execute(
                "--critical",
                environment={"AI_CONTEXT_PYTHON": "missing-aic-python"},
            )

            # Then the runner remains non-passing before launching any required check.
            self.assertEqual(3, result.returncode)
            self.assertIn("BLOCKED-BY-ENVIRONMENT", result.stderr)
            self.assertIn("Python 3.11 or newer is required", result.stderr)
            self.assertEqual([], fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_015_given_parent_python_override_when_fixture_runs_then_path_stub_remains_authoritative(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the host exports a real interpreter for its outer gate.
            with mock.patch.dict(
                os.environ,
                {"AI_CONTEXT_PYTHON": sys.executable},
            ):
                # When a synthetic fixture runs without its own explicit override.
                result = fixture.execute("--quick")

            # Then the fixture isolates the host override and retains its PATH stub.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(
                any(line.startswith("python ") for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_016_given_active_environment_when_gate_starts_then_it_precedes_path_python(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            active = fixture.root / "active"
            active_python = active / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            active_python.parent.mkdir(parents=True)
            fixture._write_stub(
                active_python,
                fixture._python_stub_body("active-python", "ACTIVE_PYTHON_STUB_EXIT"),
            )
            result = fixture.execute(
                "--critical", environment={"VIRTUAL_ENV": str(active)}
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(any(line.startswith("active-python ") for line in commands))
            self.assertFalse(any(line.startswith("python ") for line in commands))
        finally:
            fixture.close()

    def test_gwt_017_given_only_versioned_path_python_when_gate_starts_then_it_is_selected(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.add_python_stub("python", "GENERIC_PYTHON_STUB_EXIT")
            fixture.add_python_stub("python3", "GENERIC_PYTHON_STUB_EXIT")
            fixture.add_python_stub("python3.13", "VERSIONED_PYTHON_STUB_EXIT")
            result = fixture.execute(
                "--critical",
                environment={"GENERIC_PYTHON_STUB_EXIT": "1"},
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(
                any(line.startswith("python3.13 ") for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_018_given_only_offline_uv_python_when_gate_starts_then_uv_is_queried_once(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture._write_stub(
                fixture.bin / "dirname",
                'value=${1%/}\ncase "$value" in */*) printf "%s\\n" "${value%/*}" ;; *) printf ".\\n" ;; esac',
            )
            fixture._write_stub(
                fixture.bin / "date",
                'printf "2026-01-01 00:00:00\\n"',
            )
            for command in (
                "awk",
                "cat",
                "grep",
                "head",
                "mkdir",
                "sed",
                "sha256sum",
                "sort",
            ):
                fixture._write_stub(
                    fixture.bin / command,
                    f'PATH=/usr/bin:/bin exec {command} "$@"',
                )
            fixture.add_python_stub("python", "GENERIC_PYTHON_STUB_EXIT")
            fixture.add_python_stub("python3", "GENERIC_PYTHON_STUB_EXIT")
            managed = fixture.add_python_stub("managed-python", "MANAGED_PYTHON_STUB_EXIT")
            fixture._write_stub(
                fixture.bin / "uv",
                f'printf "uv %s\\n" "$*" >> .aic-sentinel\nprintf "%s\\n" "{managed.as_posix()}"',
            )
            result = fixture.execute(
                "--critical",
                environment={
                    "GENERIC_PYTHON_STUB_EXIT": "1",
                    "PATH": str(fixture.bin),
                },
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            uv_commands = [line for line in commands if line.startswith("uv ")]
            self.assertEqual(1, len(uv_commands))
            self.assertIn(
                "python find --managed-python --no-python-downloads --offline --no-config --no-project >=3.11",
                uv_commands[0],
            )
            self.assertTrue(any(line.startswith("managed-python ") for line in commands))
        finally:
            fixture.close()

    def test_gwt_019_given_repository_snapshot_admission_fails_when_runner_starts_then_no_check_is_launched(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SNAPSHOT_EXIT": "2",
                },
            )

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "snapshot admission failed under process-tree supervision",
                result.stderr,
            )
            self.assertIn("admission-evidence:", result.stderr)
            invocations = fixture.invocation_directories()
            self.assertEqual(1, len(invocations))
            retained = invocations[0] / "repository-snapshot-pre.json"
            self.assertTrue(retained.is_file())
            self.assertIn("admission-fixture", retained.read_text(encoding="utf-8"))
            self.assertFalse(
                any("check-coding-standards.sh" in line for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_020_given_supervisor_reports_snapshot_drift_when_selected_then_remaining_commands_are_not_launched(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            result = fixture.execute(
                "--quick",
                environment={"EVIDENCE_STUB_SUPERVISE_EXIT": "125"},
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("repository snapshot drift", result.stdout)
            self.assertIn("snapshot-drift", result.stdout)
            launched_validators = [
                line
                for line in fixture.sentinel()
                if ".ai/scripts/" in line and "validation-evidence.py" not in line
            ]
            self.assertEqual([], launched_validators)
        finally:
            fixture.close()

    def test_gwt_021_given_invocation_seal_fails_when_runner_finishes_then_gate_cannot_pass_or_publish_a_manifest(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SEAL_EXIT": "9",
                    "EVIDENCE_STUB_SEAL_WRITE_BEFORE_EXIT": "true",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("validation invocation artifacts could not be sealed", result.stdout)
            invocations = fixture.invocation_directories()
            self.assertEqual(1, len(invocations))
            self.assertFalse((invocations[0] / "sealed-manifest.json").exists())
            self.assertIn("sealed-manifest: unavailable", result.stdout)
            self.assertTrue(
                any(line.startswith("evidence seal-invocation ") for line in fixture.evidence_sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_022_given_selected_nonexecuted_paths_when_quick_finishes_then_every_selected_id_has_one_bound_event(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            result = fixture.execute(
                "--quick",
                environment={"AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs)},
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            invocations = fixture.invocation_directories()
            self.assertEqual(1, len(invocations))
            invocation = invocations[0]
            selected_ids = {
                line.split("\t", 1)[0]
                for line in (invocation / "selected-checks.tsv").read_text(
                    encoding="utf-8"
                ).splitlines()
                if line
            }
            event_rows = [
                line.split("\t")
                for line in (invocation / "evidence-events.tsv").read_text(
                    encoding="utf-8"
                ).splitlines()
                if line
            ]
            event_ids = [row[0] for row in event_rows]
            self.assertEqual(len(event_ids), len(set(event_ids)))
            by_id = {row[0]: row for row in event_rows}
            self.assertEqual(selected_ids, selected_ids & set(by_id))
            self.assertTrue(
                all(by_id[check_id][4] != "not-selected" for check_id in selected_ids)
            )
            self.assertTrue(any(row[4] == "not-executed" for row in event_rows))
            self.assertTrue(all(len(row) == 14 for row in event_rows))
            supervised_calls = [
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence supervise ")
                and ".ai/scripts/validation-evidence.py" not in line
            ]
            self.assertTrue(supervised_calls)
            self.assertTrue(all("bash -c" not in line for line in supervised_calls))
            self.assertTrue(all("eval" not in line for line in supervised_calls))
        finally:
            fixture.close()

    def test_gwt_023_given_selected_command_times_out_when_quick_runs_then_remaining_chain_is_not_launched(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SUPERVISE_EXIT": "124",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            supervised_calls = [
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence supervise ")
                and ".ai/scripts/validation-evidence.py" not in line
            ]
            self.assertEqual(1, len(supervised_calls), supervised_calls)
            invocation = fixture.invocation_directories()[0]
            events = [
                line.split("\t")
                for line in (invocation / "evidence-events.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            self.assertEqual("timed-out", next(row for row in events if row[4] == "timed-out")[4])
            self.assertTrue(any(row[4] == "not-executed" for row in events))
            self.assertTrue((invocation / "sealed-manifest.json").is_file())
            self.assertNotIn("sealed-manifest: unavailable", result.stdout)
            self.assertNotIn("All Checks Passed Successfully", result.stdout)
            self.assertIn("reused=0", result.stdout)
            seal_call = next(
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence seal-invocation ")
            )
            self.assertIn("--outcome failed", seal_call)
        finally:
            fixture.close()

    def test_gwt_024_given_supervisor_cannot_launch_when_quick_runs_then_attempt_is_not_counted_as_executed(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SUPERVISE_EXIT": "127",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("executed=0", result.stdout)
            self.assertRegex(result.stdout, r"Required Executed: .*0")
            events = [
                line.split("\t")
                for line in (fixture.invocation_directories()[0] / "evidence-events.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            attempted = next(row for row in events if row[12])
            self.assertEqual("not-executed", attempted[4])
        finally:
            fixture.close()

    def test_gwt_025_given_runner_command_drifts_from_registry_when_selected_then_drift_fails_before_target_launch(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.override_commands(
                **{"profile-registry-contract": "python fixture-wrong-command.py"}
            )
            result = fixture.execute(
                "--quick",
                environment={"AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs)},
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("runner command contract", result.stdout)
            self.assertFalse(
                any("fixture-wrong-command.py" in line for line in fixture.sentinel())
            )
            self.assertFalse(
                any("test_validation_profile_registry.py" in line for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_026_given_invocation_directory_already_exists_when_runner_starts_then_no_artifact_or_check_is_reused(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            invocation = fixture.validation_logs / "fixed-invocation"
            invocation.mkdir(parents=True)
            marker = invocation / "sealed-manifest.json"
            marker.write_text("pre-existing\n", encoding="utf-8", newline="\n")

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "AI_CONTEXT_VALIDATION_INVOCATION_ID": "fixed-invocation",
                },
            )

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn("not uniquely creatable", result.stderr)
            self.assertEqual("pre-existing\n", marker.read_text(encoding="utf-8"))
            self.assertFalse(
                any(".ai/scripts/" in line for line in fixture.sentinel()),
                fixture.sentinel(),
            )
            self.assertEqual([], fixture.evidence_sentinel())
        finally:
            fixture.close()

    def test_gwt_027_given_signal_arrives_during_seal_when_runner_finishes_then_manifest_is_removed_and_exit_fails(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "profile-registry-contract")

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SIGNAL_DURING_SEAL": "true",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            invocation = fixture.invocation_directories()[0]
            self.assertFalse((invocation / "sealed-manifest.json").exists())
            self.assertIn("sealed-manifest: unavailable", result.stdout)
            self.assertNotIn("All Checks Passed Successfully", result.stdout)
            self.assertIn("runner-signal-TERM", result.stdout)
        finally:
            fixture.close()

    def test_gwt_028_given_supervisor_return_has_no_authenticated_result_when_check_runs_then_chain_aborts_without_execution_credit(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to(
                "pr",
                "profile-registry-contract",
                "validation-evidence-contract",
            )

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SUPERVISE_EXIT": "1",
                    "EVIDENCE_STUB_SUPERVISE_OMIT_RESULT": "true",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("executed=0", result.stdout)
            self.assertIn("supervision evidence was invalid", result.stdout)
            self.assertFalse(
                any("test_validation_evidence.py" in line for line in fixture.sentinel())
            )
            invocation = fixture.invocation_directories()[0]
            event = next(
                line.split("\t")
                for line in (invocation / "evidence-events.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.startswith("profile-registry-contract\t")
            )
            self.assertEqual("not-executed", event[4])
            self.assertEqual("", event[12])
        finally:
            fixture.close()

    def test_gwt_029_given_immutable_receipt_prepares_reuse_when_earlier_check_aborts_then_later_protected_check_uses_standard_fingerprint(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "workflow-implementation-contract")
            fixture.enable_source_release_context()
            fixture.enable_immutable_history_context()

            result = fixture.execute(
                "--profile",
                "pr",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "IMMUTABLE_HISTORY_STUB_MODE": "reusable",
                    "EVIDENCE_STUB_SUPERVISE_EXIT_NON_PREPARATION": "124",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            invocation = fixture.invocation_directories()[0]
            selected_fingerprints = {
                line.split("\t", 1)[0]
                for line in (invocation / "evidence-selection.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            }
            self.assertNotIn("assessment-artifacts", selected_fingerprints)
            self.assertNotIn("workflow-artifacts", selected_fingerprints)
            self.assertIn("source-ai-context-version", selected_fingerprints)
            source_event = next(
                line.split("\t")
                for line in (invocation / "evidence-events.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.startswith("source-ai-context-version\t")
            )
            self.assertEqual("not-executed", source_event[4])
            self.assertEqual("false", source_event[7])
            self.assertEqual("", source_event[12])
        finally:
            fixture.close()

    def test_gwt_030_given_successful_checks_when_terminal_evidence_is_published_then_all_control_roles_and_seal_are_supervised(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "profile-registry-contract")

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                },
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            control_calls = [
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence supervise ")
                and ".ai/scripts/validation-evidence.py" in line
            ]
            bootstrap_calls = [
                line
                for line in control_calls
                if "--bootstrap-snapshot-output" in line
            ]
            self.assertEqual(1, len(bootstrap_calls), control_calls)
            self.assertEqual(
                2,
                sum(
                    ".ai/scripts/validation-evidence.py verify-snapshot" in line
                    for line in control_calls
                ),
                control_calls,
            )
            for command in (
                "prepare",
                "finalize",
                "summarize",
                "workflow-summary",
                "seal-invocation",
            ):
                self.assertEqual(
                    1,
                    sum(
                        f".ai/scripts/validation-evidence.py {command}" in line
                        for line in control_calls
                    ),
                    control_calls,
                )
            seal_call = next(
                line
                for line in control_calls
                if ".ai/scripts/validation-evidence.py seal-invocation" in line
            )
            for role in (
                "bootstrap-snapshot",
                "prepare",
                "post-snapshot",
                "finalize",
                "summarize",
                "workflow-summary",
            ):
                self.assertIn(f"--control-result {role} ", seal_call)
            self.assertIn("--terminal-result", seal_call)
            self.assertIn("--terminal-log", seal_call)
            self.assertIn("--publication-output", seal_call)
            self.assertIn("--preparation-selection", seal_call)
            terminal_verifications = [
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence verify-terminal-invocation ")
            ]
            self.assertEqual(1, len(terminal_verifications), terminal_verifications)
            self.assertIn("--manifest ", terminal_verifications[0])
            self.assertIn("--result-path ", terminal_verifications[0])
            self.assertIn(" -- ", terminal_verifications[0])
            self.assertIn(" seal-invocation ", terminal_verifications[0])
            invocation = fixture.invocation_directories()[0]
            self.assertTrue((invocation / "sealed-manifest.json").is_file())
            self.assertFalse((invocation / "sealed-manifest.staged.json").exists())
            self.assertTrue((invocation / "control-seal.result.json").is_file())
            self.assertTrue((invocation / "control-seal.log").is_file())
            self.assertIn("seal-supervision-result:", result.stdout)
            self.assertNotIn("seal-supervision-result: unavailable", result.stdout)
        finally:
            fixture.close()

    def test_gwt_031_given_supervised_control_times_out_when_finalizing_then_no_terminal_pair_is_published(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "profile-registry-contract")

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_CONTROL_SUPERVISE_EXIT": "124",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "repository identity could not be supervised through final snapshot verification",
                result.stdout,
            )
            self.assertIn("sealed-manifest: unavailable", result.stdout)
            self.assertIn("seal-supervision-result: unavailable", result.stdout)
            self.assertNotIn("All Checks Passed Successfully", result.stdout)
            invocation = fixture.invocation_directories()[0]
            self.assertFalse((invocation / "sealed-manifest.json").exists())
            self.assertFalse((invocation / "sealed-manifest.staged.json").exists())
            control_calls = [
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence supervise ")
                and ".ai/scripts/validation-evidence.py" in line
            ]
            self.assertEqual(3, len(control_calls), control_calls)
            self.assertIn("--bootstrap-snapshot-output", control_calls[0])
            self.assertIn("validation-evidence.py prepare", control_calls[1])
            self.assertIn("validation-evidence.py verify-snapshot", control_calls[2])
        finally:
            fixture.close()

    def test_gwt_032_given_all_control_roles_complete_when_terminal_seal_supervision_is_untrustworthy_then_no_manifest_or_pass_is_published(
        self,
    ) -> None:
        cases = (
            (
                "missing-result",
                {
                    "EVIDENCE_STUB_SEAL_SUPERVISE_EXIT": "1",
                    "EVIDENCE_STUB_SEAL_SUPERVISE_OMIT_RESULT": "true",
                },
            ),
            (
                "invalid-result",
                {"EVIDENCE_STUB_SEAL_VERIFY_SUPERVISION_EXIT": "1"},
            ),
            (
                "child-nonzero",
                {
                    "EVIDENCE_STUB_SEAL_EXIT": "9",
                    "EVIDENCE_STUB_SEAL_WRITE_BEFORE_EXIT": "true",
                },
            ),
        )
        for label, injection in cases:
            with self.subTest(label=label):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.restrict_profile_to("pr", "profile-registry-contract")
                    environment = {
                        "AI_CONTEXT_VALIDATION_LOG_DIR": str(
                            fixture.validation_logs
                        ),
                        **injection,
                    }

                    result = fixture.execute("--quick", environment=environment)

                    self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                    control_calls = [
                        line
                        for line in fixture.evidence_sentinel()
                        if line.startswith("evidence supervise ")
                        and ".ai/scripts/validation-evidence.py" in line
                    ]
                    seal_index = next(
                        index
                        for index, line in enumerate(control_calls)
                        if "validation-evidence.py seal-invocation" in line
                    )
                    self.assertTrue(
                        any(
                            "--bootstrap-snapshot-output" in line
                            for line in control_calls[:seal_index]
                        ),
                        control_calls,
                    )
                    for command in (
                        "prepare",
                        "verify-snapshot",
                        "finalize",
                        "summarize",
                        "workflow-summary",
                    ):
                        self.assertTrue(
                            any(
                                f"validation-evidence.py {command}" in line
                                for line in control_calls[:seal_index]
                            ),
                            control_calls,
                        )
                    invocation = fixture.invocation_directories()[0]
                    self.assertFalse(
                        (invocation / "sealed-manifest.staged.json").exists()
                    )
                    self.assertFalse((invocation / "sealed-manifest.json").exists())
                    self.assertIn("sealed-manifest: unavailable", result.stdout)
                    self.assertIn("seal-supervision-result: unavailable", result.stdout)
                    self.assertIn("reused=0", result.stdout)
                    self.assertNotIn("All Checks Passed Successfully", result.stdout)
                finally:
                    fixture.close()

    def test_gwt_033_given_seal_child_stages_a_manifest_when_publication_target_appears_then_no_overwrite_publication_fails_closed(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "profile-registry-contract")

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_PRECREATE_PUBLICATION_OUTPUT": "true",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            invocation = fixture.invocation_directories()[0]
            self.assertIn(
                "stub precreated publication=",
                (invocation / "control-seal.log").read_text(encoding="utf-8"),
            )
            self.assertFalse((invocation / "sealed-manifest.staged.json").exists())
            publication = invocation / "sealed-manifest.json"
            self.assertTrue(publication.is_file())
            self.assertEqual(b"pre-existing\n", publication.read_bytes())
            self.assertIn(
                "validation invocation artifacts could not be sealed",
                result.stdout,
            )
            self.assertIn("sealed-manifest: unavailable", result.stdout)
            self.assertIn("seal-supervision-result: unavailable", result.stdout)
            self.assertIn("reused=0", result.stdout)
            self.assertNotIn("All Checks Passed Successfully", result.stdout)
        finally:
            fixture.close()

    def test_gwt_034_given_bootstrap_snapshot_supervision_cannot_complete_when_runner_starts_then_no_validation_target_launches(
        self,
    ) -> None:
        cases = (
            ("timeout", {"EVIDENCE_STUB_BOOTSTRAP_SUPERVISE_EXIT": "124"}),
            (
                "missing-result",
                {
                    "EVIDENCE_STUB_BOOTSTRAP_SUPERVISE_EXIT": "1",
                    "EVIDENCE_STUB_SUPERVISE_OMIT_RESULT": "true",
                },
            ),
        )
        for label, injection in cases:
            with self.subTest(label=label):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.restrict_profile_to("pr", "profile-registry-contract")
                    result = fixture.execute(
                        "--quick",
                        environment={
                            "AI_CONTEXT_VALIDATION_LOG_DIR": str(
                                fixture.validation_logs
                            ),
                            **injection,
                        },
                    )

                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                    self.assertIn(
                        "snapshot admission failed under process-tree supervision",
                        result.stderr,
                    )
                    self.assertFalse(
                        any(".ai/scripts/" in line for line in fixture.sentinel()),
                        fixture.sentinel(),
                    )
                    bootstrap_calls = [
                        line
                        for line in fixture.evidence_sentinel()
                        if line.startswith("evidence supervise ")
                    ]
                    self.assertEqual(1, len(bootstrap_calls), bootstrap_calls)
                    self.assertIn(
                        "--bootstrap-snapshot-output", bootstrap_calls[0]
                    )
                    invocation = fixture.invocation_directories()[0]
                    self.assertFalse((invocation / "evidence-events.tsv").exists())
                    self.assertFalse((invocation / "sealed-manifest.json").exists())
                finally:
                    fixture.close()

    def test_gwt_035_given_cache_preparation_supervision_cannot_complete_when_admission_runs_then_no_validation_target_or_reuse_is_admitted(
        self,
    ) -> None:
        cases = (
            ("timeout", {"EVIDENCE_STUB_PREPARE_SUPERVISE_EXIT": "124"}),
            (
                "missing-result",
                {
                    "EVIDENCE_STUB_PREPARE_SUPERVISE_EXIT": "1",
                    "EVIDENCE_STUB_SUPERVISE_OMIT_RESULT": "true",
                },
            ),
        )
        for label, injection in cases:
            with self.subTest(label=label):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.restrict_profile_to("pr", "profile-registry-contract")
                    result = fixture.execute(
                        "--quick",
                        environment={
                            "AI_CONTEXT_VALIDATION_LOG_DIR": str(
                                fixture.validation_logs
                            ),
                            **injection,
                        },
                    )

                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                    self.assertIn(
                        "preparation failed under process-tree supervision",
                        result.stderr,
                    )
                    self.assertFalse(
                        any(".ai/scripts/" in line for line in fixture.sentinel()),
                        fixture.sentinel(),
                    )
                    supervised_calls = [
                        line
                        for line in fixture.evidence_sentinel()
                        if line.startswith("evidence supervise ")
                    ]
                    self.assertEqual(2, len(supervised_calls), supervised_calls)
                    self.assertIn(
                        "--bootstrap-snapshot-output", supervised_calls[0]
                    )
                    self.assertIn(
                        "validation-evidence.py prepare", supervised_calls[1]
                    )
                    invocation = fixture.invocation_directories()[0]
                    self.assertEqual(
                        "",
                        (invocation / "evidence-events.tsv").read_text(
                            encoding="utf-8"
                        ),
                    )
                    self.assertFalse((invocation / "sealed-manifest.json").exists())
                finally:
                    fixture.close()

    def test_gwt_036_given_cached_command_target_is_missing_when_selected_then_reuse_is_rejected(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            target_ref = ".ai/scripts/tests/test_validation_profile_registry.py"
            fixture.restrict_profile_to("pr", "profile-registry-contract")
            (fixture.root / target_ref).unlink()

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_REUSE": "true",
                },
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "canonical command target for Validation Profile Registry Contract",
                result.stdout,
            )
            self.assertFalse(
                any(target_ref in line for line in fixture.sentinel()),
                fixture.sentinel(),
            )
            invocation = fixture.invocation_directories()[0]
            event = next(
                row.split("\t")
                for row in (invocation / "evidence-events.tsv")
                .read_text(encoding="utf-8")
                .splitlines()
                if row.startswith("profile-registry-contract\t")
            )
            self.assertEqual("not-executed", event[4])
            self.assertEqual("false", event[7])
            self.assertEqual("", event[12])
        finally:
            fixture.close()

    def test_gwt_037_given_malformed_preparation_rows_when_cache_admission_runs_then_runner_fails_before_checks(
        self,
    ) -> None:
        for mode in (
            "unknown-id",
            "duplicate-id",
            "invalid-fingerprint",
            "invalid-cache",
            "extra-column",
            "missing-row",
        ):
            with self.subTest(mode=mode):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.restrict_profile_to("pr", "profile-registry-contract")
                    result = fixture.execute(
                        "--quick",
                        environment={
                            "AI_CONTEXT_VALIDATION_LOG_DIR": str(
                                fixture.validation_logs
                            ),
                            "EVIDENCE_STUB_PREPARE_MODE": mode,
                        },
                    )

                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                    self.assertIn(
                        "preparation failed under process-tree supervision",
                        result.stderr,
                    )
                    self.assertFalse(
                        any(".ai/scripts/" in line for line in fixture.sentinel()),
                        fixture.sentinel(),
                    )
                    invocation = fixture.invocation_directories()[0]
                    self.assertEqual(
                        "",
                        (invocation / "evidence-events.tsv").read_text(
                            encoding="utf-8"
                        ),
                    )
                    self.assertFalse((invocation / "sealed-manifest.json").exists())
                finally:
                    fixture.close()

    def test_gwt_037a_given_crlf_cache_preparation_rows_without_reuse_when_admission_runs_then_validation_continues(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "profile-registry-contract")

            result = fixture.execute(
                "--quick",
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_PREPARE_MODE": "crlf-valid",
                },
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(
                any("test_validation_profile_registry.py" in line for line in fixture.sentinel()),
                fixture.sentinel(),
            )
            invocation = fixture.invocation_directories()[0]
            self.assertIn(b"\r\n", (invocation / "control-prepare.log").read_bytes())
        finally:
            fixture.close()

    def test_gwt_037b_given_crlf_cache_preparation_rows_have_invalid_data_when_admission_runs_then_runner_fails_before_checks(
        self,
    ) -> None:
        cases = {
            "crlf-false-prior-log": "log without a cache hit",
            "crlf-extra-column": "row must contain exactly four columns",
            "crlf-invalid-cache": "invalid cache flag",
            "crlf-invalid-fingerprint": "invalid fingerprint",
            "crlf-invalid-id": "invalid check id",
            "crlf-internal-cr": "invalid check id",
        }
        for mode, expected_error in cases.items():
            with self.subTest(mode=mode):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.restrict_profile_to("pr", "profile-registry-contract")
                    result = fixture.execute(
                        "--quick",
                        environment={
                            "AI_CONTEXT_VALIDATION_LOG_DIR": str(
                                fixture.validation_logs
                            ),
                            "EVIDENCE_STUB_PREPARE_MODE": mode,
                        },
                    )

                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, result.stderr)
                    self.assertIn(
                        "preparation failed under process-tree supervision",
                        result.stderr,
                    )
                    self.assertFalse(
                        any(".ai/scripts/" in line for line in fixture.sentinel()),
                        fixture.sentinel(),
                    )
                finally:
                    fixture.close()

    def test_gwt_038_given_terminal_pair_is_not_authenticated_when_publication_is_pending_then_no_manifest_is_published(
        self,
    ) -> None:
        cases = (
            ("verifier-failed", {"EVIDENCE_STUB_TERMINAL_VERIFY_EXIT": "1"}),
            (
                "digest-malformed",
                {"EVIDENCE_STUB_TERMINAL_VERIFY_DIGEST": "not-a-sha256"},
            ),
        )
        for label, injection in cases:
            with self.subTest(label=label):
                fixture = SyntheticRunnerRepo()
                try:
                    fixture.restrict_profile_to("pr", "profile-registry-contract")
                    result = fixture.execute(
                        "--quick",
                        environment={
                            "AI_CONTEXT_VALIDATION_LOG_DIR": str(
                                fixture.validation_logs
                            ),
                            **injection,
                        },
                    )

                    self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                    self.assertIn(
                        "validation invocation artifacts could not be sealed",
                        result.stdout,
                    )
                    invocation = fixture.invocation_directories()[0]
                    self.assertFalse((invocation / "sealed-manifest.staged.json").exists())
                    self.assertFalse((invocation / "sealed-manifest.json").exists())
                    self.assertIn("sealed-manifest: unavailable", result.stdout)
                    self.assertNotIn("All Checks Passed Successfully", result.stdout)
                    self.assertTrue(
                        any(
                            line.startswith("evidence verify-terminal-invocation ")
                            for line in fixture.evidence_sentinel()
                        ),
                        fixture.evidence_sentinel(),
                    )
                finally:
                    fixture.close()


class ChangedPathDependencyClosureGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_before = real_repo_snapshot()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.real_before != real_repo_snapshot():
            raise AssertionError("changed-path fixtures mutated the real repository")

    @staticmethod
    def execute_changed_path(
        fixture: SyntheticRunnerRepo, base: str, head: str
    ) -> subprocess.CompletedProcess[str]:
        return fixture.execute(
            "--profile",
            "pr",
            "--base",
            base,
            "--head",
            head,
            environment={"AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs)},
        )

    def test_gwt_001_given_direct_multilevel_root_then_full_closure_and_chain_are_recorded(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.override_dependencies(
                **{
                    "profile-projection": "dependency-versions-tests",
                    "dependency-versions-tests": "dependency-versions",
                }
            )
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            base, head = fixture.create_changed_path_revisions(changed_path)

            result = self.execute_changed_path(fixture, base, head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            evidence = fixture.selected_evidence_files()
            self.assertEqual(1, len(evidence))
            rows = fixture.selected_rows(evidence[0])
            self.assertEqual(
                [
                    ("dependency-versions", "dependency-chain:profile-projection -> dependency-versions-tests -> dependency-versions"),
                    ("dependency-versions-tests", "dependency-chain:profile-projection -> dependency-versions-tests"),
                    ("profile-projection", f"direct-path-match:{changed_path}"),
                ],
                rows,
            )
        finally:
            fixture.close()

    def test_gwt_002_given_diamond_dependency_then_shared_check_is_selected_once(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.override_dependencies(
                **{
                    "profile-projection": "dependency-versions-tests coding-standards-integrity",
                    "dependency-versions-tests": "dependency-versions",
                    "coding-standards-integrity": "dependency-versions",
                }
            )
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            base, head = fixture.create_changed_path_revisions(changed_path)

            result = self.execute_changed_path(fixture, base, head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            rows = fixture.selected_rows(fixture.selected_evidence_files()[0])
            selected_ids = [check_id for check_id, _ in rows]
            self.assertEqual(1, selected_ids.count("dependency-versions"))
            self.assertEqual(
                [
                    "dependency-versions",
                    "dependency-versions-tests",
                    "coding-standards-integrity",
                    "profile-projection",
                ],
                selected_ids,
            )
            dependency_executions = [
                line
                for line in fixture.sentinel()
                if "validate-dependency-versions.py" in line
            ]
            self.assertEqual(1, len(dependency_executions), fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_003_given_dependency_cycle_then_exact_path_fails_before_execution(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.override_dependencies(
                **{
                    "dependency-versions-tests": "profile-projection",
                    "profile-projection": "dependency-versions-tests",
                }
            )

            result = fixture.execute("--profile", "pr")

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "Dependency cycle detected: dependency-versions-tests -> profile-projection -> dependency-versions-tests",
                result.stderr,
            )
            self.assertEqual([], fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_004_given_unknown_dependency_then_registry_fails_before_execution(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.override_dependencies(**{"profile-projection": "missing-check"})

            result = fixture.execute("--profile", "pr")

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "Unknown dependency 'missing-check' in validation check 'profile-projection'",
                result.stderr,
            )
            self.assertEqual([], fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_005_given_dependency_outside_profile_then_it_remains_selected_and_deferred(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.override_dependencies(**{"profile-projection": "test-di-compliance"})
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            base, head = fixture.create_changed_path_revisions(changed_path)

            result = self.execute_changed_path(fixture, base, head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DEFERRED: Test DI Compliance", result.stdout)
            self.assertIn("deferred=1", result.stdout)
            rows = fixture.selected_rows(fixture.selected_evidence_files()[0])
            self.assertIn(
                ("test-di-compliance", "dependency-chain:profile-projection -> test-di-compliance"),
                rows,
            )
        finally:
            fixture.close()

    def test_gwt_006_given_multiple_direct_roots_then_evidence_is_repeatable(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            changed_path = "fixture/shared.txt"
            fixture.override_input_paths(
                **{
                    "coding-standards-integrity": changed_path,
                    "profile-projection": changed_path,
                }
            )
            base, head = fixture.create_changed_path_revisions(changed_path)

            first = self.execute_changed_path(fixture, base, head)
            second = self.execute_changed_path(fixture, base, head)

            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertEqual(0, second.returncode, second.stdout + second.stderr)
            evidence = fixture.selected_evidence_files()
            self.assertEqual(2, len(evidence))
            first_rows = fixture.selected_rows(evidence[0])
            second_rows = fixture.selected_rows(evidence[1])
            self.assertEqual(first_rows, second_rows)
            self.assertIn(
                ("coding-standards-integrity", f"direct-path-match:{changed_path}"),
                first_rows,
            )
            self.assertIn(
                ("profile-projection", f"direct-path-match:{changed_path}"),
                first_rows,
            )
        finally:
            fixture.close()

    def test_gwt_007_given_supervisor_changes_when_pr_selection_runs_then_it_is_a_global_invalidator(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to(
                "pr",
                "profile-registry-contract",
                "validation-evidence-contract",
                "validation-process-supervisor-contract",
            )
            changed_path = ".ai/scripts/validation_process_supervisor.py"
            base, head = fixture.create_changed_path_revisions(changed_path)

            result = self.execute_changed_path(fixture, base, head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            rows = fixture.selected_rows(fixture.selected_evidence_files()[0])
            self.assertEqual(
                [
                    (
                        "profile-registry-contract",
                        "profile-inclusion:pr;escalation:global-invalidator",
                    ),
                    (
                        "validation-process-supervisor-contract",
                        "profile-inclusion:pr;escalation:global-invalidator",
                    ),
                    (
                        "validation-evidence-contract",
                        "profile-inclusion:pr;escalation:global-invalidator",
                    ),
                ],
                rows,
            )
        finally:
            fixture.close()

    def test_gwt_008_given_explicit_head_is_not_current_when_pr_selects_then_selection_escalates_and_binds_current_head(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to(
                "pr",
                "profile-registry-contract",
                "validation-evidence-contract",
            )
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            base, stale_head = fixture.create_changed_path_revisions(changed_path)
            (fixture.root / changed_path).write_text(
                "current\n", encoding="utf-8", newline="\n"
            )
            fixture._require_success(run(["git", "add", "--", changed_path], fixture.root))
            fixture._require_success(
                run(
                    [
                        "git",
                        "-c",
                        "user.name=Fixture",
                        "-c",
                        "user.email=fixture@example.invalid",
                        "commit",
                        "--quiet",
                        "-m",
                        "fixture current head",
                    ],
                    fixture.root,
                )
            )
            current_head = fixture._require_stdout(
                run(["git", "rev-parse", "HEAD"], fixture.root)
            )

            result = self.execute_changed_path(fixture, base, stale_head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            invocation = fixture.invocation_directories()[0]
            comparison = (invocation / "selection-comparison.tsv").read_text(
                encoding="utf-8"
            ).rstrip("\n").split("\t")
            self.assertEqual("escalated", comparison[1])
            self.assertEqual(current_head, comparison[3])
            self.assertEqual("comparison-head-mismatch", comparison[5])
            selected = {row[0] for row in fixture.selected_rows(invocation / "selected-checks.tsv")}
            self.assertIn("profile-registry-contract", selected)
            self.assertIn("validation-evidence-contract", selected)
        finally:
            fixture.close()

    def test_gwt_009_given_explicit_current_range_has_dirty_worktree_when_pr_selects_then_selection_escalates(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to("pr", "profile-registry-contract")
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            base, head = fixture.create_changed_path_revisions(changed_path)
            (fixture.root / "fixture/dirty.txt").write_text(
                "dirty\n", encoding="utf-8", newline="\n"
            )

            result = self.execute_changed_path(fixture, base, head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            invocation = fixture.invocation_directories()[0]
            comparison = (invocation / "selection-comparison.tsv").read_text(
                encoding="utf-8"
            ).rstrip("\n").split("\t")
            self.assertEqual("escalated", comparison[1])
            self.assertEqual(head, comparison[3])
            self.assertEqual("dirty-repository-selection", comparison[5])
        finally:
            fixture.close()

    def test_gwt_010_given_worktree_drifts_after_changed_path_selection_when_snapshot_is_captured_then_no_validator_launches(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            base, head = fixture.create_changed_path_revisions(changed_path)

            result = fixture.execute(
                "--profile",
                "pr",
                "--base",
                base,
                "--head",
                head,
                environment={
                    "AI_CONTEXT_VALIDATION_LOG_DIR": str(fixture.validation_logs),
                    "EVIDENCE_STUB_SNAPSHOT_DIRTY_AFTER_CAPTURE": ".selection-drift",
                },
            )

            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn("selection changed before repository snapshot admission", result.stderr)
            self.assertFalse(
                any(".ai/scripts/" in line for line in fixture.sentinel()),
                fixture.sentinel(),
            )
            supervision_calls = [
                line
                for line in fixture.evidence_sentinel()
                if line.startswith("evidence supervise ")
            ]
            self.assertEqual(1, len(supervision_calls), supervision_calls)
            self.assertIn("--bootstrap-snapshot-output", supervision_calls[0])
            self.assertIn("validation-evidence.py verify-snapshot", supervision_calls[0])
        finally:
            fixture.close()

    def test_gwt_011_given_explicit_base_is_not_current_ancestor_when_pr_selects_then_selection_escalates(
        self,
    ) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            fixture.restrict_profile_to(
                "pr",
                "profile-registry-contract",
                "validation-evidence-contract",
            )
            changed_path = "fixture/profile-projection.txt"
            fixture.override_input_paths(**{"profile-projection": changed_path})
            common_base, current_head = fixture.create_changed_path_revisions(changed_path)
            fixture._require_success(
                run(["git", "switch", "--quiet", "--detach", common_base], fixture.root)
            )
            (fixture.root / changed_path).write_text(
                "changed\n", encoding="utf-8", newline="\n"
            )
            fixture._require_success(run(["git", "add", "--", changed_path], fixture.root))
            fixture._require_success(
                run(
                    [
                        "git",
                        "-c",
                        "user.name=Fixture",
                        "-c",
                        "user.email=fixture@example.invalid",
                        "commit",
                        "--quiet",
                        "-m",
                        "fixture sibling change",
                    ],
                    fixture.root,
                )
            )
            unrelated_base = fixture._require_stdout(
                run(["git", "rev-parse", "HEAD"], fixture.root)
            )
            fixture._require_success(
                run(["git", "switch", "--quiet", "--detach", current_head], fixture.root)
            )

            result = self.execute_changed_path(fixture, unrelated_base, current_head)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            invocation = fixture.invocation_directories()[0]
            comparison = (invocation / "selection-comparison.tsv").read_text(
                encoding="utf-8"
            ).rstrip("\n").split("\t")
            self.assertEqual("escalated", comparison[1])
            self.assertEqual(unrelated_base, comparison[2])
            self.assertEqual(current_head, comparison[3])
            self.assertEqual("comparison-base-not-ancestor", comparison[5])
            selected = {
                row[0]
                for row in fixture.selected_rows(invocation / "selected-checks.tsv")
            }
            self.assertIn("profile-registry-contract", selected)
            self.assertIn("validation-evidence-contract", selected)
        finally:
            fixture.close()


class AdvisoryRootResolutionGwtTests(unittest.TestCase):
    def test_gwt_001_given_retained_script_when_run_from_ai_scripts_then_repo_src_is_scanned(self) -> None:
        bash = bash_executable()
        if not bash:
            raise unittest.SkipTest("Bash is required for advisory path fixture tests")

        with tempfile.TemporaryDirectory(prefix="aic005-test-root-") as temporary:
            # Given the retained script is at .ai/scripts and a repository test exists.
            root = Path(temporary)
            scripts = root / ".ai/scripts"
            target = root / "src/Example/Tests/SampleTest.cs"
            scripts.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            script = scripts / TEST_COMPLIANCE_SOURCE.name
            shutil.copy2(TEST_COMPLIANCE_SOURCE, script)
            script.chmod(0o755)
            target.write_text(
                "// Gherkin-style sample\npublic sealed class SampleTest { }\n",
                encoding="utf-8",
                newline="\n",
            )
            environment = dict(os.environ)
            if os.name == "nt":
                git_usr_bin = Path(bash).parent.parent / "usr/bin"
                environment["PATH"] = (
                    str(git_usr_bin) + os.pathsep + environment["PATH"]
                )

            # When the advisory helper resolves its repository root.
            result = subprocess.run(
                [bash, str(script)],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # Then it scans the repository src tree instead of the repository parent.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("No target files found", result.stdout)
            self.assertIn("All checks passed", result.stdout)


class ShellAssetValidationGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_before = real_repo_snapshot()

    @classmethod
    def tearDownClass(cls) -> None:
        # Then the real checkout HEAD, status, and shell index are unchanged.
        cls.real_after = real_repo_snapshot()
        if cls.real_before != cls.real_after:
            raise AssertionError("synthetic fixture tests mutated the real repository")

    def test_gwt_002_given_tracked_asset_mode_100644_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        fixture_root = fixture.root
        try:
            # Given a classified shell tracked with Git mode 100644.
            script = fixture.add_shell("required.sh", mode="100644")
            fixture.write_manifest(retained=[script], required_entrypoints=[script])

            # When shell asset validation runs against the synthetic index.
            result = fixture.validate()

            # Then index truth rejects the path regardless of host executability.
            self.assertEqual(1, result.returncode)
            self.assertIn(script, result.stdout)
            self.assertIn("tracked shell asset must use Git mode 100755, found 100644", result.stdout)
        finally:
            fixture.close()
        self.assertFalse(fixture_root.exists())

    def test_gwt_012_given_manifest_coverage_mismatch_when_validated_then_lists_both_sides(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given one unclassified tracked shell and one nonexistent manifest path.
            classified = fixture.add_shell("classified.sh")
            missing = fixture.add_shell("missing-from-manifest.sh")
            extra = ".ai/scripts/extra-in-manifest.sh"
            fixture.write_manifest(retained=[classified, extra])

            # When shell asset validation compares manifest and index coverage.
            result = fixture.validate()

            # Then it fails with deterministic missing and extra lists.
            self.assertEqual(1, result.returncode)
            self.assertIn(f"missing=['{missing}']", result.stdout)
            self.assertIn(f"extra=['{extra}']", result.stdout)
        finally:
            fixture.close()

    def test_gwt_013_given_invalid_asset_records_when_validated_then_invariants_fail(self) -> None:
        cases = (
            ("overlap", ["assets contains duplicate path"]),
            ("duplicate", ["assets contains duplicate path"]),
            ("required-outside", ["required_entrypoints contains non-runnable lifecycle path"]),
        )
        for case, messages in cases:
            with self.subTest(case=case):
                fixture = SyntheticShellAssetRepo()
                try:
                    # Given a manifest violating one asset-record invariant.
                    retained = fixture.add_shell("retained.sh")
                    outside = fixture.add_shell("outside.sh")
                    if case == "overlap":
                        fixture.write_manifest(
                            retained=[retained, outside],
                            retirement_candidates=[retained],
                        )
                    elif case == "duplicate":
                        fixture.write_manifest(
                            retained=[retained, retained],
                            retirement_candidates=[outside],
                        )
                    else:
                        fixture.write_manifest(
                            retained=[retained],
                            retirement_candidates=[outside],
                            required_entrypoints=[outside],
                        )

                    # When shell asset validation checks role and lifecycle ownership.
                    result = fixture.validate()

                    # Then the matching invariant is reported as a failure.
                    self.assertEqual(1, result.returncode)
                    for message in messages:
                        self.assertIn(message, result.stdout)
                finally:
                    fixture.close()

    def test_gwt_014_given_valid_manifest_when_validated_then_counts_and_exit_pass(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given complete classification, executable active paths, and valid subsets.
            entrypoint = fixture.add_shell("entrypoint.sh")
            child = fixture.add_shell("child.sh")
            fixture.write_manifest(
                retained=[entrypoint, child],
                required_entrypoints=[entrypoint],
                check_all_required_scripts=[child],
            )

            # When shell asset validation runs.
            result = fixture.validate()

            # Then it passes with truthful role, lifecycle, and tracked counts.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("passed for 2 tracked asset(s)", result.stdout)
            self.assertIn("'active': 2", result.stdout)
            self.assertIn("'context-validator': 2", result.stdout)
        finally:
            fixture.close()

    def test_gwt_017_given_transitional_asset_without_replacement_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given a transitional helper that omits its replacement direction.
            script = fixture.add_shell("transitional.sh")
            fixture.write_manifest(retained=[script])
            manifest_path = fixture.scripts / "shell-assets.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"][0].update(
                {
                    "role": "transitional-helper",
                    "lifecycle": "transitional",
                    "authority": "advisory",
                    "replacement": None,
                }
            )
            manifest_path.write_text(
                yaml.safe_dump(manifest, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )

            # When lifecycle validation runs.
            result = fixture.validate()

            # Then packaging retention cannot hide an unspecified replacement.
            self.assertEqual(1, result.returncode)
            self.assertIn("replacement is required for non-active lifecycle", result.stdout)
        finally:
            fixture.close()

    def test_gwt_019_given_deprecated_helper_with_replacement_when_validated_then_passes(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given a deprecated-in-place helper with an explicit replacement.
            script = fixture.add_shell("deprecated.sh")
            fixture.write_manifest(retained=[script])
            manifest_path = fixture.scripts / "shell-assets.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"][0].update(
                {
                    "role": "transitional-helper",
                    "lifecycle": "deprecated",
                    "authority": "advisory",
                    "replacement": "Use the compiled validator.",
                }
            )
            manifest_path.write_text(
                yaml.safe_dump(manifest, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )

            # When lifecycle validation runs, then explicit deprecation is valid.
            result = fixture.validate()
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("'deprecated': 1", result.stdout)
        finally:
            fixture.close()

    def test_given_required_runner_child_omitted_when_validated_then_parity_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given the runner has two required children but the manifest declares one.
            coding = fixture.add_shell("check-coding-standards.sh")
            spec = fixture.add_shell("check-spec-compliance.sh")
            runner = fixture.add_runner(["check-coding-standards.sh", "check-spec-compliance.sh"])
            fixture.write_manifest(
                retained=[runner, coding, spec],
                required_entrypoints=[runner],
                check_all_required_scripts=[coding],
            )

            # When runner declarations and manifest ownership are compared.
            result = fixture.validate()

            # Then the undeclared conditional-required child blocks validation.
            self.assertEqual(1, result.returncode)
            self.assertIn("check_all required-script coverage mismatch", result.stdout)
            self.assertIn(f"missing=['{spec}']", result.stdout)
        finally:
            fixture.close()

    def test_gwt_016_given_required_command_omitted_when_validated_then_parity_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given the runner invokes two literal required commands but declares one.
            runner = fixture.add_command_runner(["python first.py", "python second.py"])
            fixture.write_manifest(
                retained=[runner],
                required_entrypoints=[runner],
                check_all_required_commands=["python first.py"],
            )

            # When aggregate command registration is compared by set.
            result = fixture.validate()

            # Then the missing command fails closed without relying on a fixed count.
            self.assertEqual(1, result.returncode)
            self.assertIn("check_all required-command coverage mismatch", result.stdout)
            self.assertIn("python second.py", result.stdout)
        finally:
            fixture.close()

    def test_gwt_018_given_required_command_format_changes_when_validated_then_parity_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given the manifest owns one command but the runner call no longer
            # follows the retained literal multiline format.
            runner = fixture.add_command_runner(["python first.py"])
            fixture.write_manifest(
                retained=[runner],
                required_entrypoints=[runner],
                check_all_required_commands=["python first.py"],
            )
            (fixture.root / runner).write_text(
                "#!/bin/bash\n"
                'run_command_check "python first.py" "Fixture" "required" "true" "true"\n',
                encoding="utf-8",
                newline="\n",
            )

            # When the shell registry validator compares the retained grammar.
            result = fixture.validate()

            # Then formatting drift fails closed rather than silently removing
            # a required command from the governed set.
            self.assertEqual(1, result.returncode)
            self.assertIn("check_all required-command coverage mismatch", result.stdout)
            self.assertIn("extra=['python first.py']", result.stdout)
        finally:
            fixture.close()

    def test_gwt_015_given_failed_fixture_when_cleaned_then_real_repo_and_temp_root_are_safe(self) -> None:
        # Given a real-repository snapshot and a synthetic failing fixture.
        real_before = real_repo_snapshot()
        fixture = SyntheticShellAssetRepo()
        fixture_root = fixture.root
        script = fixture.add_shell("non-executable.sh", mode="100644")
        fixture.write_manifest(retained=[script])

        # When validation fails and fixture cleanup runs through finally.
        try:
            result = fixture.validate()
            self.assertEqual(1, result.returncode)
        finally:
            fixture.close()

        # Then temporary state is removed and the real Git state is unchanged.
        self.assertFalse(fixture_root.exists())
        self.assertEqual(real_before, real_repo_snapshot())


if __name__ == "__main__":
    unittest.main()
