#!/usr/bin/env python3
"""Run a local Windows installation smoke against one committed source.

Both output arguments are existing native F: RAM-disk parent directories. Each invocation
creates fresh w-<id>/e-<id> children and retains everything, including failures.
This is real local installation/API evidence, not publication, IDE discovery,
installer crash recovery, power-loss durability or target adoption. RAM-disk
evidence is limited to process-termination behavior; it is not durable storage.
Use provisioned Python 3.11+, PyYAML 6 and Git; dependencies are never added.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import uuid

VERSION = "workflow-records/1"
WORKFLOW = "installation-smoke"
GIT_REF = {"provider_id": "git", "store_id": "project-workflows", "workflow_id": WORKFLOW}
LOCAL_REF = {"provider_id": "local", "store_id": "local-records", "workflow_id": WORKFLOW}
CHECKPOINT = {"summary": "Installation smoke checkpoint", "authority": "Isolated synthetic fixture owner",
              "completed": ["Read installed workflow context"], "pending": ["Resume in another process"],
              "blockers": [], "evidence": ["fixture:installed-cli"], "next_action": "Read the saved checkpoint"}

# Each consumer invocation proves both source trees unreadable before dispatch.
# This is a Python file-access oracle, not an OS sandbox for native children.
AUDITED_LAUNCHER = r'''
import json, os, runpy, sys
from pathlib import Path
settings = json.loads(Path(sys.argv[1]).read_bytes())
roots = [os.path.normcase(os.path.realpath(p)) for p in settings["denied_roots"]]
def denied(value):
    if not isinstance(value, (str, bytes, os.PathLike)):
        return False
    path = os.path.normcase(os.path.realpath(os.fsdecode(value)))
    return any(path == root or path.startswith(root + os.sep) for root in roots)
violations = []
probing = True
def audit(event, args):
    if event in {"open", "os.listdir", "os.scandir", "os.chdir"} and args and denied(args[0]):
        if not probing:
            violations.append(event)
        raise PermissionError("source access denied by installed-consumer audit")
sys.addaudithook(audit)
probes = 0
for root in roots:
    try:
        with open(os.path.join(root, "AGENTS.md"), "rb"):
            pass
    except PermissionError:
        probes += 1
    else:
        raise RuntimeError("source exclusion probe did not reject access")
probing = False
sys.argv = settings["argv"]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
finally:
    modules = {}
    for name, module in list(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if name == "workflow_records" or name.startswith("workflow_records."):
            modules[name] = filename
        if filename and denied(filename):
            violations.append("loaded-source-module")
    Path(settings["audit_result"]).write_text(json.dumps({"probe_denials": probes,
        "unexpected_denials": violations, "workflow_modules": modules}, sort_keys=True), encoding="utf-8")
'''
PIN_LAUNCHER = r'''
import runpy, sys
from pathlib import Path
module = runpy.run_path(sys.argv[1])
pin = module["engine_pin"](Path(sys.argv[2]), sys.argv[3])
sys.stdout.buffer.write(module["encoded"](pin))
'''


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fresh(path, raw):
    """Never replace evidence from an earlier attempt or call."""
    with path.open("xb") as stream:
        stream.write(raw)


def canonical_directory(path):
    """Keep direct ancestry checks on RAM disks whose final-name API returns error 1."""
    require(os.name == "nt" and path.is_absolute() and re.fullmatch(r"[A-Za-z]:", path.drive)
            and ".." not in path.parts, "An explicit absolute native Windows directory is required.")
    require(path.is_dir(), "The selected directory must already exist.")
    def identities():
        rows = []
        for part in (path, *path.parents):
            info = part.lstat()
            require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
                    and not getattr(info, "st_file_attributes", 0) & 0x400, "Selected paths must have plain directory ancestry.")
            rows.append((info.st_dev, info.st_ino))
        return rows
    before = identities()
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.QueryDosDeviceW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    kernel.QueryDosDeviceW.restype = wintypes.DWORD
    buffer = ctypes.create_unicode_buffer(32768)
    size = kernel.QueryDosDeviceW(path.drive, buffer, len(buffer))
    require(0 < size < len(buffer) and re.fullmatch(r"\\Device\\[^\\]+", buffer.value),
            "Selected drive must be a native device, not SUBST/network storage.")
    kernel.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    kernel.GetDriveTypeW.restype = wintypes.UINT
    require(kernel.GetDriveTypeW(path.anchor) in {2, 3, 5, 6}, "Selected drive must be local.")
    try:
        canonical = path.resolve(strict=True)
    except OSError as exc:
        if getattr(exc, "winerror", None) != 1:
            raise
        require(all(device and inode for device, inode in before), "Native path identities are unavailable.")
        kernel.GetLongPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        kernel.GetLongPathNameW.restype = wintypes.DWORD
        canonical_buffer = ctypes.create_unicode_buffer(32768)
        size = kernel.GetLongPathNameW(str(path), canonical_buffer, len(canonical_buffer))
        require(0 < size < len(canonical_buffer), "Canonical native directory name is unavailable.")
        canonical = Path(canonical_buffer.value)
    require(canonical == path and identities() == before, "Canonical stable directory identities are required.")
    return canonical


def native_parent(path):
    require(path.drive.upper() == "F:", "Output parents must be explicit F: RAM-disk paths; C: output is not allowed.")
    require(len(str(path)) <= 70, "An existing short F: output parent (at most 70 characters) is required.")
    return canonical_directory(path)


class Smoke:
    def __init__(self, repository, commit, work, evidence):
        self.repository, self.commit = repository, commit
        self.work, self.evidence = work, evidence
        self.checkout, self.project = work / "s", work / "p"
        self.calls, self.checks = [], []
        self.audit_launcher = work / "audit.py"
        fresh(self.audit_launcher, AUDITED_LAUNCHER.encode("utf-8"))
        self.environment = {key: value for key, value in os.environ.items()
                            if not any(secret in key.upper() for secret in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))
                            and not key.upper().startswith(("GIT_", "PYTHON"))}
        self.environment["GIT_TERMINAL_PROMPT"] = "0"
        self.environment["GIT_CONFIG_NOSYSTEM"] = "1"
        self.environment["GIT_CONFIG_GLOBAL"] = os.devnull
        self.environment["TMP"] = self.environment["TEMP"] = self.environment["TMPDIR"] = str(work)

    def check(self, name, condition):
        self.checks.append({"name": name, "outcome": "passed" if condition else "failed"})
        require(condition, name)

    def call(self, label, command, request=None, *, audited=False, no_site=False, codes=(0,), timeout=60, parse=True):
        folder = self.evidence / (f"{len(self.calls) + 1:03d}-" + label)
        folder.mkdir()
        raw = b"" if request is None else encoded(request)
        fresh(folder / "request.json", raw)
        original = list(map(str, command))
        if audited:
            settings = {"denied_roots": [str(self.repository), str(self.checkout)],
                        "argv": original, "audit_result": str(folder / "audit.json")}
            settings_path = folder / "launch.json"
            fresh(settings_path, encoded(settings))
            actual = [sys.executable, "-I", "-B", *(["-S"] if no_site else []), str(self.audit_launcher), str(settings_path)]
        else:
            require(not no_site, "Site-package exclusion requires an audited Python invocation.")
            actual = original
        cwd = self.project if self.project.exists() else self.work
        fresh(folder / "command.json", encoded({"argv": actual, "cwd": str(cwd), "timeout_seconds": timeout,
                                               "consumer_audited": audited, "site_packages_disabled": no_site,
                                               "temp_roots": {key: self.environment[key] for key in ("TEMP", "TMP", "TMPDIR")}}))
        started = time.monotonic()
        row = {"label": label, "evidence": str(folder), "outcome": "started"}
        self.calls.append(row)
        try:
            result = subprocess.run(actual, input=raw, capture_output=True, env=self.environment, cwd=cwd, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            fresh(folder / "stdout.bin", exc.stdout or b"")
            fresh(folder / "stderr.bin", exc.stderr or b"")
            row.update(outcome="timeout", exit_code=None, duration_seconds=round(time.monotonic() - started, 3))
            fresh(folder / "exit.json", encoded(row))
            raise ValueError(label + " timed out; partial evidence retained") from exc
        except OSError as exc:
            fresh(folder / "stdout.bin", b"")
            fresh(folder / "stderr.bin", str(exc).encode("utf-8"))
            row.update(outcome="launch-failed", exit_code=None, duration_seconds=round(time.monotonic() - started, 3))
            fresh(folder / "exit.json", encoded(row))
            raise
        fresh(folder / "stdout.bin", result.stdout)
        fresh(folder / "stderr.bin", result.stderr)
        row.update(outcome="returned", exit_code=result.returncode, duration_seconds=round(time.monotonic() - started, 3))
        fresh(folder / "exit.json", encoded(row))
        require(result.returncode in codes, label + " unexpected exit; inspect retained stdout/stderr")
        if audited:
            audit = json.loads((folder / "audit.json").read_bytes())
            require(audit["probe_denials"] == 2 and not audit["unexpected_denials"], label + " source-isolation oracle failed")
            for filename in audit["workflow_modules"].values():
                require(filename and Path(filename).is_relative_to(self.project / ".ai/core/skills/workflow-records/tools"),
                        label + " imported workflow runtime outside the installation")
            if original[0].endswith("workflow-records.py") and result.returncode == 0:
                require("workflow_records.service" in audit["workflow_modules"], label + " did not load the installed service")
        if parse:
            require(not result.stderr, label + " unexpected stderr")
            return json.loads(result.stdout)
        return result.stdout

    def git(self, root, label, *arguments):
        return self.call(label, ["git", "-C", root, "-c", "core.hooksPath=" + str(self.work / "empty-hooks"),
                                *arguments], parse=False).decode("utf-8").strip()

    def maintenance(self, label, request, codes=(0,)):
        return self.call(label, [self.engine / "src/tools/maintain_framework.py"], request, audited=True, codes=codes)

    def declaration(self, scope, label):
        return {"declared_by": "isolated-smoke-runner", "declaration_reference": label,
                "affected_capabilities": scope, "sessions_stopped": True, "tools_stopped": True, "external_writers_stopped": True}

    def derive(self, skills, label):
        catalog_pin = {"identity": self.catalog_identity,
                       "catalog_sha256": digest((self.catalog / "metadata/catalog.json").read_bytes()),
                       "files_sha256": digest((self.catalog / "metadata/catalog-files.json").read_bytes())}
        selection = {"selection_version": 2, "catalog": catalog_pin, "skills": skills, "knowledge": [],
                     "adapters": ["claude", "codex"], "bindings": [], "skill_naming": "original"}
        path = self.work / (label + ".json")
        fresh(path, encoded(selection))
        output, scratch = self.work / (label + "o"), self.work / (label + "t")
        output.mkdir()
        scratch.mkdir()
        result = self.call(label, [self.engine / "src/tools/derive-subset.py", "--catalog-root", self.catalog,
                           "--catalog-identity", self.catalog_identity, "--selection", path,
                           "--engine-pin", self.pin_path, "--output-root", output, "--scratch-root", scratch], audited=True)
        root = Path(result["artifact_root"])
        self.check(label + " bounded artifact", root.is_relative_to(output))
        build = json.loads((root / "metadata/build.json").read_bytes())
        self.check(label + " candidate identity", build["identity"] == result["identity"])
        return root, result["identity"]

    def fixture(self):
        self.project.mkdir()
        workflow = self.project / ".dev/workflows" / WORKFLOW
        (workflow / "tasks").mkdir(parents=True)
        stamp = "2026-10-11T00:00:00+00:00"
        common = {"workflow_id": WORKFLOW, "owner_skill": "workflow-records", "created_at": stamp,
                  "updated_at": stamp, "template_source": "synthetic-installation-fixture", "template_version": "1.0"}
        locator = {**common, "schema_version": "1.0", "lifecycle_contract": "1.0", "workflow_kind": "software-development",
                   "title": "Installed Git workflow fixture", "status": "in_progress", "current_phase": "implementation",
                   "artifact_root": ".dev/workflows/" + WORKFLOW, "entrypoint": "workflow-plan.md",
                   "branch": "fixture", "base_branch": "fixture"}
        # JSON is a YAML subset and exercises the installed YAML reader.
        fresh(workflow / "workflow.yaml", encoded(locator))
        fresh(workflow / "workflow-plan.md", b"# Installed workflow plan\nRetain caller-owned bytes.\n")
        fresh(workflow / "tasks/T1.json", encoded({**common, "task_id": "T1", "title": "Resume installed checkpoint", "status": "in_progress"}))
        fresh(self.project / "sentinel.txt", b"caller-owned sentinel\r\n")
        fresh(self.project / "caller-data.bin", bytes(range(256)))
        self.database = self.work / "store.sqlite"
        self.config_path = self.project / ".ai/project/workflow-records.json"
        self.config_path.parent.mkdir(parents=True)
        config = {"contract_version": VERSION, "default_provider": "local", "stores": {"local": {"kind": "local",
                  "store_id": LOCAL_REF["store_id"], "repository_id": "smoke-repository", "database": str(self.database), "busy_timeout_ms": 500}}}
        fresh(self.config_path, encoded(config))
        self.original = {str(path.relative_to(self.project)): path.read_bytes() for path in self.project.rglob("*") if path.is_file()}
        self.git(self.project, "fixture-init", "init", "--initial-branch=fixture")
        self.git(self.project, "fixture-add", "add", ".")
        self.git(self.project, "fixture-commit", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "Synthetic installation consumer")

    def unchanged_callers(self):
        return all((self.project / name).read_bytes() == raw for name, raw in self.original.items())

    def workflow(self, label, request, config=None, codes=(0,), *, no_site=False):
        path = self.work / (label + ".json")
        fresh(path, encoded(request))
        command = [self.cli, "--root", self.project, "--request", path]
        if config is not None:
            command.extend(["--config", config])
        return self.call(label, command, request, audited=True, no_site=no_site, codes=codes)

    def request(self, operation, ref=None, **fields):
        value = {"contract_version": VERSION, "operation": operation}
        if ref is not None:
            value["workflow_ref"] = ref
        return {**value, **fields}

    def workflow_chain(self, prefix, ref, config=None):
        def invoke(operation, suffix=None, **fields):
            response = self.workflow(prefix + "-" + (suffix or operation), self.request(operation, ref, **fields), config)
            self.check(prefix + " " + (suffix or operation) + " structured status", response["status"] == "ok")
            return response["result"]
        found = self.workflow(prefix + "-find", self.request("find", provider_id=ref["provider_id"]), config)
        self.check(prefix + " discovery", found["status"] == "ok" and any(item["workflow_ref"] == ref for item in found["result"]["items"]))
        context = invoke("context")
        document = invoke("read", **context["entrypoint"])
        self.check(prefix + " selected document", bool(document["content"]))
        checkpoint = self.request("checkpoint", ref, checkpoint=copy.deepcopy(CHECKPOINT), operation_id=prefix + "-checkpoint",
                                  expected_revision=context["revision"], expected_source_head=context["source_head"])
        first = self.workflow(prefix + "-checkpoint", checkpoint, config)
        self.check(prefix + " checkpoint applied", first["status"] == "ok" and first["result"]["state"] == "applied")
        replay = self.workflow(prefix + "-replay", checkpoint, config)
        self.check(prefix + " checkpoint replay", replay["status"] == "ok" and replay["result"]["replayed"] is True)
        lookup = invoke("operation", operation_id=checkpoint["operation_id"])
        self.check(prefix + " receipt binding", lookup["checkpoint_revision"] == first["result"]["checkpoint_revision"])
        resumed = invoke("resume")
        self.check(prefix + " resumed checkpoint", resumed["checkpoint"]["next_action"]["text"] == CHECKPOINT["next_action"]
                   and resumed["plan"]["content"] == document["content"])
        conflict = copy.deepcopy(checkpoint)
        conflict["checkpoint"]["summary"] = "Conflicting replay must be rejected"
        rejected = self.workflow(prefix + "-id-conflict", conflict, config, (1,))
        self.check(prefix + " reused ID rejected", rejected["status"] == "error" and rejected["error"]["code"] == "operation_id_conflict")
        stale = copy.deepcopy(checkpoint)
        stale["operation_id"] = prefix + "-stale"
        rejected = self.workflow(prefix + "-revision-conflict", stale, config, (1,))
        self.check(prefix + " stale revision rejected", rejected["status"] == "error" and rejected["error"]["code"] == "revision_conflict")
        storage = (self.project / ".dev/workflows" / WORKFLOW / ".workflow-records/checkpoint.json"
                   if ref["provider_id"] == "git" else self.database)
        storage_before = digest(storage.read_bytes())
        self.git(self.project, prefix + "-advance-source", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", prefix + " source-conflict fixture")
        advanced_head = self.git(self.project, prefix + "-advanced-head", "rev-parse", "HEAD")
        self.check(prefix + " real source HEAD advanced", advanced_head != resumed["source_head"])
        source_conflict = self.request("checkpoint", ref, checkpoint=copy.deepcopy(CHECKPOINT), operation_id=prefix + "-source-conflict",
                                       expected_revision=resumed["revision"], expected_source_head=resumed["source_head"])
        rejected = self.workflow(prefix + "-source-conflict", source_conflict, config, (1,))
        self.check(prefix + " source conflict rejected without mutation", rejected["status"] == "error"
                   and rejected["error"]["code"] == "source_conflict" and rejected["mutation_state"] == "none")
        self.check(prefix + " source conflict preserves storage bytes", digest(storage.read_bytes()) == storage_before)
        self.check(prefix + " caller bytes preserved", self.unchanged_callers())
        return first["result"]

    def run(self):
        self.check("isolated host Python", bool(sys.flags.isolated and sys.flags.dont_write_bytecode and sys.version_info >= (3, 11)))
        # Producer calls may read selected source; consumer calls below may not.
        self.call("clone", ["git", "-c", "core.hooksPath=" + str(self.work / "empty-hooks"), "clone", "--no-hardlinks",
                            "--no-checkout", self.repository, self.checkout], parse=False, timeout=120)
        self.git(self.checkout, "checkout", "-c", "core.autocrlf=false", "checkout", "--detach", self.commit)
        self.check("selected immutable checkout", self.git(self.checkout, "source-head", "rev-parse", "HEAD") == self.commit)
        self.check("clean source before build", not self.git(self.checkout, "source-status-before", "status", "--porcelain", "--untracked-files=all"))
        self.check("executing smoke script matches selected commit", Path(__file__).read_bytes() ==
                   (self.checkout / "tools/validation/validate-workflow-installation.py").read_bytes())
        self.pin = self.call("engine-pin", [sys.executable, "-I", "-B", "-c", PIN_LAUNCHER,
                             self.checkout / ".github/scripts/build-release.py", self.checkout, self.commit])
        self.pin_path = self.work / "pin.json"
        fresh(self.pin_path, encoded(self.pin))
        for name in ("c", "e", "t"):
            (self.work / name).mkdir()
        built = self.call("catalog-build", [sys.executable, "-I", "-B", self.checkout / "tools/build-catalog.py",
                          "--repository", self.checkout, "--commit", self.commit, "--release-version", "0.20.0",
                          "--engine-pin", self.pin_path, "--output-root", self.work / "c", "--scratch-root", self.work / "t",
                          "--engine-output-root", self.work / "e"], timeout=300)
        self.check("catalog assembled without implicit installation", built["outcome"] == "assembled" and built["installation"] == "not-performed")
        self.catalog, self.catalog_identity = Path(built["artifact_root"]), built["identity"]
        self.engine = Path(built["engine_bundle"]["engine_root"])
        self.check("bounded catalog and standalone engine", self.catalog.is_relative_to(self.work / "c") and self.engine.is_relative_to(self.work / "e"))
        self.check("independent engine pin matches package", built["engine_bundle"]["engine"] == self.pin)
        self.candidate, candidate_identity = self.derive(["workflow-records"], "workflow")
        optional, _ = self.derive(["local-change-implementer"], "optional")
        self.check("unselected workflow runtime absent", not any("workflow_records" in path.parts or "workflow-records" in path.parts
                                                               for path in optional.rglob("*")))
        self.fixture()
        base = {"api_version": 2, "project_root": str(self.project), "engine_root": str(self.engine), "engine": self.pin}
        inspected = self.maintenance("inspect-before", {**base, "operation": "inspect", "candidate_root": str(self.candidate)})
        self.check("initial installation absent", inspected["outcome"] == "inspected" and inspected["details"]["managed_state"] == "uninstalled")
        for name in ("is", "it", "ir"):
            (self.work / name).mkdir()
        plan_request = {**base, "operation": "plan", "candidate_root": str(self.candidate), "candidate_identity": candidate_identity,
                        "expected_lock_sha256": None, "mode_policy": "windows-inventory-only", "scratch_root": str(self.work / "is"),
                        "staging_root": str(self.work / "it"), "recovery_root": str(self.work / "ir"),
                        "durability": {"declared_by": "isolated-smoke-runner", "declaration_reference": "fresh-RAM-disk-fixture",
                                       "failure_domain": "process-termination"},
                        "protected_inputs": [{"path": name.replace("\\", "/"), "sha256": digest(raw)} for name, raw in sorted(self.original.items())],
                        "project_data_action": "none", "project_edits": []}
        plan = self.maintenance("plan-first", plan_request)
        self.check("first install planned", plan["outcome"] == "planned" and plan["plan"]["noop"] is False)
        applied = self.maintenance("apply-first", {**plan_request, "operation": "apply", "expected_plan_sha256": plan["plan_sha256"],
                                   "maintenance": self.declaration(plan["plan"]["maintenance_scope"], "first-install-no-other-fixture-writers")})
        self.check("first install applied", applied["outcome"] == "applied" and applied["changed"] is True
                   and applied["details"]["managed_state"] == "managed-bytes-consistent")
        first_operation = Path(applied["details"]["operation_root"])
        self.check("bounded first operation", first_operation.is_relative_to(self.work / "ir"))
        self.cli = self.project / ".ai/core/skills/workflow-records/tools/workflow-records.py"
        self.check("both adapter entries installed", all((self.project / folder / "skills/workflow-records/SKILL.md").is_file()
                                                        for folder in (".agents", ".claude")))
        self.workflow_chain("git", GIT_REF)
        config_path = self.config_path
        initialized = self.workflow("sqlite-init", self.request("init", store_ref={key: LOCAL_REF[key] for key in ("provider_id", "store_id")},
                                    operation_id="initialize"), config_path)
        self.check("external SQLite initialized", initialized["status"] == "ok" and self.database.is_file())
        record = {"metadata": {"title": "Installed SQLite fixture", "status": "in_progress", "owner_skill": "workflow-records",
                               "authority": "Synthetic fixture owner", "extensions": {"future": ["preserved", 1]}},
                  "tasks": [{"task_id": "T1", "title": "Verify installed resume", "status": "in_progress", "unknown": {"x": True}}],
                  "entrypoint": "plan.md", "documents": {"plan.md": "# Installed SQLite plan\n", "evidence.txt": "observed evidence\n"},
                  "attachments": {"images/pixel.bin": base64.b64encode(b"\x00\xff\x10attachment").decode("ascii")}}
        created = self.workflow("sqlite-create", self.request("create", LOCAL_REF, operation_id="create-example", record=record), config_path)
        self.check("SQLite workflow created", created["status"] == "ok")
        receipt = self.workflow_chain("sqlite", LOCAL_REF, config_path)
        # An explicitly selected unavailable store must not write either available store.
        git_checkpoint = self.project / ".dev/workflows" / WORKFLOW / ".workflow-records/checkpoint.json"
        before_remote = {"git_checkpoint_sha256": digest(git_checkpoint.read_bytes()),
                         "sqlite_sha256": digest(self.database.read_bytes())}
        unavailable_config = json.loads(config_path.read_bytes())
        unavailable_config["stores"].update({"git": {"kind": "git", "store_id": GIT_REF["store_id"], "root": ".dev/workflows"},
                                             "remote": {"kind": "remote", "store_id": "unavailable-records"}})
        unavailable_config["default_provider"] = "remote"
        unavailable_path = self.work / "unavailable-config.json"
        fresh(unavailable_path, encoded(unavailable_config))
        unavailable_ref = {"provider_id": "remote", "store_id": "unavailable-records", "workflow_id": WORKFLOW}
        rejected = self.workflow("unavailable-provider", self.request("checkpoint", unavailable_ref,
                                 checkpoint=copy.deepcopy(CHECKPOINT), operation_id="unavailable-provider-checkpoint",
                                 expected_revision=receipt["revision"], expected_source_head=receipt["source_head"]), unavailable_path, (1,))
        self.check("unavailable provider refuses without fallback", rejected["status"] == "unavailable"
                   and rejected["error"]["code"] == "provider_unavailable" and rejected["mutation_state"] == "none")
        after_remote = {"git_checkpoint_sha256": digest(git_checkpoint.read_bytes()),
                        "sqlite_sha256": digest(self.database.read_bytes())}
        fresh(self.evidence / "unavailable-provider-preservation.json", encoded({"before": before_remote, "after": after_remote}))
        self.check("unavailable provider preserves both stores", before_remote == after_remote)
        database_before = digest(self.database.read_bytes())
        callers_before = {str(path.relative_to(self.project)): digest(path.read_bytes()) for path in self.project.rglob("*")
                          if path.is_file() and ".git" not in path.relative_to(self.project).parts}
        fresh(self.evidence / "preservation-before.json", encoded({"project_files": callers_before, "database_sha256": database_before}))
        missing_dependency = self.workflow("missing-prerequisite", self.request("capabilities"), codes=(1,), no_site=True)
        self.check("missing PyYAML prerequisite structured unavailable", missing_dependency["status"] == "unavailable"
                   and missing_dependency["error"]["code"] == "provider_unavailable" and missing_dependency["mutation_state"] == "none")
        # Remove one declared support file, prove refusal, restore its exact bytes.
        support = self.cli.parent / "workflow_records/backup.py"
        support_raw = support.read_bytes()
        held = self.work / "held-backup.py"
        support.rename(held)
        try:
            missing = self.workflow("missing-support", self.request("capabilities"), codes=(1,))
            self.check("missing support structured unavailable", missing["status"] == "unavailable"
                       and missing["error"]["code"] == "provider_unavailable" and missing["mutation_state"] == "none")
        finally:
            held.rename(support)
        self.check("support restored exactly", support.read_bytes() == support_raw)
        lock = self.project / ".ai/framework.lock"
        lock_hash = digest(lock.read_bytes())
        self.check("initial lock hash readback", applied["details"]["lock_sha256"] == lock_hash)
        noop_request = {**plan_request, "expected_lock_sha256": lock_hash}
        noop = self.maintenance("plan-noop", noop_request)
        self.check("same candidate no-op plan", noop["outcome"] == "planned" and noop["plan"]["noop"] is True)
        unchanged = self.maintenance("apply-noop", {**noop_request, "operation": "apply", "expected_plan_sha256": noop["plan_sha256"],
                                     "maintenance": self.declaration(noop["plan"]["maintenance_scope"], "noop-no-other-fixture-writers")})
        self.check("same candidate no-op apply", unchanged["outcome"] == "unchanged" and unchanged["changed"] is False
                   and unchanged["details"]["operation_root"] is None and unchanged["details"]["lock_sha256"] == lock_hash)
        operation_raw = (first_operation / "operation.json").read_bytes()
        operation = json.loads(operation_raw)
        self.check("first operation raw identity", operation["project_root"] == str(self.project) and operation["operation_root"] == str(first_operation))
        self.check("completed operation markers absent", not (self.project / ".ai/framework.operation").exists()
                   and not (self.project / ".ai/config-transition.operation").exists())
        recovery = {**base, "operation": "recover", "operation_root": str(first_operation), "operation_sha256": digest(operation_raw),
                    "direction": "finish", "expected_lock_sha256": digest(lock.read_bytes()), "expected_marker_sha256": None,
                    "maintenance": self.declaration(operation["maintenance"]["affected_capabilities"], "finish-no-other-fixture-writers")}
        finished = self.maintenance("recover-finish", recovery)
        self.check("completed finish readback", finished["outcome"] == "already-matching" and finished["changed"] is False)
        recovery.update(direction="restore", expected_lock_sha256=digest(lock.read_bytes()),
                        maintenance=self.declaration(operation["maintenance"]["affected_capabilities"], "restore-no-other-fixture-writers"))
        refused = self.maintenance("recover-restore-refused", recovery, (1,))
        self.check("completed restore rejected", refused["outcome"] == "conflict" and refused["changed"] is False
                   and any(row["code"] == "completed-operation-replay" for row in refused["diagnostics"]))
        after = self.maintenance("inspect-after", {**base, "operation": "inspect", "candidate_root": str(self.candidate)})
        self.check("final managed bytes consistent", after["outcome"] == "inspected" and after["details"]["managed_state"] == "managed-bytes-consistent")
        looked_up = self.workflow("sqlite-final-receipt", self.request("operation", LOCAL_REF, operation_id="sqlite-checkpoint"), config_path)
        self.check("SQLite receipt unchanged by maintenance", looked_up["status"] == "ok" and looked_up["result"] == receipt)
        self.check("SQLite raw bytes unchanged by maintenance", digest(self.database.read_bytes()) == database_before)
        callers_after = {str(path.relative_to(self.project)): digest(path.read_bytes()) for path in self.project.rglob("*")
                         if path.is_file() and ".git" not in path.relative_to(self.project).parts}
        fresh(self.evidence / "preservation-after.json", encoded({"project_files": callers_after, "database_sha256": digest(self.database.read_bytes())}))
        self.check("all installed and caller file bytes unchanged by replay", callers_before == callers_after and self.unchanged_callers())
        self.check("tracked caller diff empty", not self.git(self.project, "consumer-diff", "diff", "--name-only"))
        self.check("clean source after build", not self.git(self.checkout, "source-status-after", "status", "--porcelain", "--untracked-files=all"))
        return {"catalog_identity": self.catalog_identity, "candidate_identity": candidate_identity,
                "engine_pin_sha256": digest(self.pin_path.read_bytes()), "database_sha256": database_before,
                "installed_lock_sha256": lock_hash, "first_operation_sha256": digest(operation_raw)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--workspace", type=Path, required=True, help="Existing short native F: RAM-disk output parent")
    parser.add_argument("--evidence-root", type=Path, required=True, help="Existing short native F: RAM-disk evidence parent")
    args = parser.parse_args()
    evidence = None
    report = {"schema": "workflow-installation-smoke/1", "outcome": "failed", "source_commit": args.commit,
              "runner_sha256": digest(Path(__file__).read_bytes()), "runner_path": str(Path(__file__).absolute()), "python": sys.version,
              "storage_profile": "F-RAM-disk", "durability_scope": "process-termination-only",
              "started_at": datetime.now(timezone.utc).isoformat(), "checks": [], "calls": [],
              "limitations": ["synthetic isolated consumer only", "Python audit is not an OS sandbox",
                              "RAM-disk process-termination evidence only; no power-loss durability",
                              "installer interruption not tested", "IDE sessions and discovery not tested",
                              "provider, publication and adoption not performed"], "artifacts_retained": True}
    started = time.monotonic()
    try:
        entrypoint = Path(__file__).absolute()
        require(entrypoint.drive.upper() == "F:", "Execute the selected runner entrypoint from an F: worktree.")
        canonical_directory(entrypoint.parent)
        require(re.fullmatch(r"[0-9a-f]{40}", args.commit), "Select one full lowercase Git commit SHA.")
        require(args.repository.is_absolute() and args.repository.is_dir(), "An existing absolute repository is required.")
        repository = canonical_directory(args.repository)
        workspace, evidence_parent = native_parent(args.workspace), native_parent(args.evidence_root)
        for path in (workspace, evidence_parent):
            require(not path.is_relative_to(repository), "Output parents must be outside the source repository.")
        attempt = uuid.uuid4().hex[:12]
        work, selected_evidence = workspace / ("w-" + attempt), evidence_parent / ("e-" + attempt)
        work.mkdir()
        selected_evidence.mkdir()
        evidence = selected_evidence
        report.update(workspace=str(work), evidence_root=str(evidence), repository=str(repository))
        smoke = Smoke(repository, args.commit, work, evidence)
        report["checks"], report["calls"] = smoke.checks, smoke.calls
        report["identity"] = smoke.run()
        report["outcome"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        report["failure"] = {"type": type(exc).__name__, "reason": str(exc)}
    except KeyboardInterrupt:
        report["outcome"] = "interrupted"
        report["failure"] = {"type": "KeyboardInterrupt", "reason": "Preserve this attempt; validation did not complete."}
    finally:
        report.update(completed_at=datetime.now(timezone.utc).isoformat(), duration_seconds=round(time.monotonic() - started, 3))
        if evidence is not None:
            try:
                fresh(evidence / "terminal.json", encoded(report))
            except OSError as exc:
                report["outcome"] = "failed"
                report["terminal_write_failure"] = str(exc)
        sys.stdout.buffer.write(encoded(report))
    return 0 if report["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
