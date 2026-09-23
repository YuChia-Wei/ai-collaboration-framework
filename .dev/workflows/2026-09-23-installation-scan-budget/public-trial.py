"""Issue #386 one complete-candidate public plan/apply/read-back; retain every root."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
import uuid

SOURCE = Path("F:/framework-next/386")
NATIVE = Path("F:/framework-next/p7-runs/scan-budget-386")
BOOTSTRAP = Path("C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend")
DURABLE = BOOTSTRAP / ".dev/ai-context/local/p7/n386"
CANDIDATE = Path("F:/framework-next/p7-runs/versioned-candidate/complete-ae3645163ae84569a1ccbacdb8fb4ad5/candidate-3755b217421a-880decbc11734dae8fbc24939280fcbb")
IDENTITY = "versioned:0.19.0-rc.1:3755b217421a4f1238f740a09de7e034ccf56038:691ef5f2202c02772e0af76c3789e0af829501d8dea5bc24837763fe1caf8a28"
BRANCH = "codex/2026-09-23-installation-scan-budget"
MAX_FILES, MAX_BYTES = 700, 16 * 1024 * 1024


def check(value, reason):
    if not value:
        raise RuntimeError(reason)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def digest(raw):
    return sha256(raw).hexdigest()


def direct(path):
    check(path.is_absolute() and ".." not in path.parts, "non-direct path")
    for current in (path, *path.parents):
        info = current.lstat()
        check(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
              and not getattr(info, "st_file_attributes", 0) & 0x400, "linked/nondirectory ancestor")
        check(info.st_dev and info.st_ino, "missing direct identity")


def inventory(roots):
    files = total = 0
    for root in roots:
        pending = [root]
        while pending:
            for target in pending.pop().iterdir():
                info = target.lstat()
                check(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                      "linked output retained")
                if stat.S_ISDIR(info.st_mode):
                    pending.append(target)
                else:
                    check(stat.S_ISREG(info.st_mode), "nonregular output retained")
                    # Focused hardlink refusal fixtures count as two logical files.
                    files += 1
                    total += info.st_size
                    check(files <= MAX_FILES and total <= MAX_BYTES, "retained output cap")
    return dict(files=files, logical_bytes=total, file_cap=MAX_FILES, logical_byte_cap=MAX_BYTES)


class Trial:
    def __init__(self):
        self.launches = []
        self.result = dict(outcome="not-passed", project_readiness="not-assessed",
                           candidate_identity=IDENTITY, source_root=str(SOURCE),
                           started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                           launches=self.launches, max_simultaneous_owned_children=1,
                           driver_processes=1, nested_transient_process_counts="unavailable",
                           public_listing_counts="not exposed by the unchanged public entry",
                           cleanup="retain all selected and failed roots; coordinator owns disposition")
        self.observations = None
        self.native = self.recovery = None
        self.started = time.monotonic()

    def launch_git(self, cwd, *arguments):
        check(len(self.launches) + 2 <= 8, "launch cap")  # include this driver
        command = ["git", "--no-replace-objects", "-C", str(cwd), *arguments]
        self.launches.append(dict(kind="git-read", command=command))
        env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
        env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        result = subprocess.run(command, cwd=SOURCE, capture_output=True, timeout=20, env=env)
        self.launches[-1]["exit_code"] = result.returncode
        check(result.returncode == 0, "Git preflight/read-back failed")
        return result.stdout.decode("utf-8").strip()

    def write(self, name, value):
        with (self.observations / name).open("xb") as stream:
            stream.write(encoded(value))

    def public(self, request):
        operation = request["operation"]
        check(len(self.launches) + 2 <= 8, "launch cap")
        self.write(operation + "-request.json", request)
        command = [sys.executable, "-I", "-B", str(SOURCE / "src/tools/maintain_framework.py")]
        row = dict(kind="public-" + operation, command=command)
        self.launches.append(row)
        started = time.monotonic()
        stdout = self.observations / (operation + ".stdout.json")
        stderr = self.observations / (operation + ".stderr.txt")
        with stdout.open("xb") as out, stderr.open("xb") as err:
            child = subprocess.Popen(command, cwd=SOURCE, stdin=subprocess.PIPE, stdout=out, stderr=err)
            row["pid"] = child.pid
            try:
                child.communicate(encoded(request), timeout=90)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
                row.update(outcome="timeout", exit_code=child.returncode)
                raise
            row.update(exit_code=child.returncode, duration_seconds=round(time.monotonic() - started, 3))
        row.update(stdout_bytes=stdout.stat().st_size, stderr_bytes=stderr.stat().st_size)
        check(max(row["stdout_bytes"], row["stderr_bytes"]) <= 1024 * 1024, "public stream cap")
        result = json.loads(stdout.read_bytes())
        row["outcome"] = result.get("outcome")
        self.result["retained"] = inventory((NATIVE, DURABLE))
        check(child.returncode == 0, "public product failure; stop and retain")
        return result

    def run(self):
        check(os.name == "nt" and sys.flags.isolated and sys.flags.dont_write_bytecode, "native isolated Python required")
        check(Path(__file__).absolute().parents[3] == SOURCE, "driver source binding")
        for root in (SOURCE, NATIVE, DURABLE / "recovery", DURABLE / "observations", CANDIDATE):
            direct(root)
        token = "p-" + uuid.uuid4().hex[:8]
        self.native, self.recovery = NATIVE / token, DURABLE / "recovery" / token
        self.observations = DURABLE / "observations" / token
        for root in (self.native, self.recovery, self.observations):
            root.mkdir()
        self.result["roots"] = dict(native=str(self.native), recovery=str(self.recovery), observations=str(self.observations))
        source_status = self.launch_git(SOURCE, "status", "--porcelain=v1", "--branch", "--untracked-files=all")
        check(source_status == "## " + BRANCH, "source must be clean on the assigned branch")
        self.commit = self.launch_git(SOURCE, "rev-parse", "HEAD")
        self.result.update(source_commit=self.commit, branch=BRANCH, source_status=source_status)
        relatives = [str((DURABLE / name).relative_to(BOOTSTRAP)) for name in ("recovery", "observations")]
        ignored = self.launch_git(BOOTSTRAP, "check-ignore", "--", *relatives)
        check(len(ignored.splitlines()) == 2, "durable roots not ignored")
        tracked = self.launch_git(BOOTSTRAP, "ls-files", "--", *relatives)
        check(not tracked, "durable roots tracked")
        self.result["durable_scope"] = dict(ignored=ignored.splitlines(), tracked=[])

        tree = ast.parse((SOURCE / "src/tools/maintain_framework.py").read_bytes())
        declarations = [node for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "ENGINE_FILES" for target in node.targets)]
        check(len(declarations) == 1, "engine closure declaration")
        names = ast.literal_eval(declarations[0].value)
        check(type(names) is tuple and len(names) == 10 and tuple(sorted(names)) == names, "engine closure shape")
        pin = dict(id="framework-managed-installation", version="1.0.0", source_commit=self.commit,
                   files=[dict(path=name, sha256=digest((SOURCE / name).read_bytes())) for name in names])
        self.result["engine_pin"] = pin

        candidate_names = ["metadata/selection.json", "metadata/files.json", "metadata/build.json"]
        selection = json.loads((CANDIDATE / candidate_names[0]).read_bytes())
        members = json.loads((CANDIDATE / candidate_names[1]).read_bytes())["files"]
        build = json.loads((CANDIDATE / candidate_names[2]).read_bytes())
        check(len(members) == 131 and len(selection["components"]) == 18 and build["candidate_identity"] == IDENTITY,
              "fixed complete candidate differs")
        candidate_names += [row["path"] for row in members]
        candidate_hashes = {name: digest((CANDIDATE / name).read_bytes()) for name in candidate_names}
        contents = {}
        for row in members:
            raw = (CANDIDATE / row["path"]).read_bytes()
            check(len(raw) == row["size"] and digest(raw) == row["sha256"], "candidate member differs")
            contents[row["destination"]] = raw

        project, scratch = self.native / "project", self.native / "scratch"
        project.mkdir()
        scratch.mkdir()
        protected, unknown = b"Owner-selected tiny project; inactive capabilities.\n", b"Unknown file retained exactly.\n"
        (project / "AGENTS.md").write_bytes(protected)
        (project / "unknown-sentinel.txt").write_bytes(unknown)
        request = dict(api_version=1, operation="plan", candidate_root=str(CANDIDATE), candidate_identity=IDENTITY,
                       project_root=str(project), engine_root=str(SOURCE), engine=pin, expected_lock_sha256=None,
                       mode_policy="windows-inventory-only", project_data_action="none",
                       scratch_root=str(scratch), staging_root=str(scratch), recovery_root=str(self.recovery),
                       protected_inputs=[dict(path="AGENTS.md", sha256=digest(protected))],
                       durability=dict(failure_domain="process-termination", declared_by="Issue 386 sole writer",
                                       declaration_reference="Owner-selected tiny native project and durable C recovery; OS/storage remain available"))
        self.result["retained_before"] = inventory((NATIVE, DURABLE))
        plan = self.public(request)
        check(plan["outcome"] == "planned" and len(plan["plan"]["delta"]) == 131, "complete plan mismatch")
        request.update(operation="apply", expected_plan_sha256=plan["plan_sha256"],
                       maintenance=dict(affected_capabilities=plan["plan"]["maintenance_scope"],
                                        declared_by="Issue 386 sole writer",
                                        declaration_reference="Exclusive newly allocated tiny project; no affected sessions/tools/external writers; inactive after return",
                                        sessions_stopped=True, tools_stopped=True, external_writers_stopped=True))
        result = self.public(request)
        check(result["outcome"] == "applied" and result["details"]["managed_state"] == "managed-bytes-consistent",
              "public apply did not establish managed bytes")
        check(result["details"]["project_readiness"] == "not-assessed", "readiness claim mismatch")
        checks = []
        for row in members:
            raw = (project / row["destination"]).read_bytes()
            check(raw == contents[row["destination"]], "managed raw byte mismatch")
            checks.append(dict(destination=row["destination"], sha256=digest(raw), size=len(raw)))
        lock_raw = (project / ".ai/framework.lock").read_bytes()
        lock_hash = digest(lock_raw)
        check(lock_hash == result["details"]["lock_sha256"], "lock result mismatch")
        operation = Path(result["details"]["operation_root"])
        check(operation.parent == self.recovery and operation.name.startswith("i-"), "unexpected operation root")
        check(lock_raw == (operation / "objects" / lock_hash).read_bytes(), "durable lock differs")
        operation_doc = json.loads((operation / "operation.json").read_bytes())
        check(operation_doc["engine"] == pin, "durable pin differs")
        markers = [".ai/framework.operation", ".ai/config-transition.operation"]
        # The current engine declares the exact two markers; read its immutable literal.
        state_tree = ast.parse((SOURCE / "src/distribution/installation_state.py").read_bytes())
        marker_node = next(node for node in state_tree.body if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name) and target.id == "MARKERS" for target in node.targets))
        markers = ast.literal_eval(marker_node.value)
        check(all(not (project / name).exists() for name in markers), "marker remains")
        check((project / "AGENTS.md").read_bytes() == protected and (project / "unknown-sentinel.txt").read_bytes() == unknown,
              "sentinel changed")
        check({name: digest((CANDIDATE / name).read_bytes()) for name in candidate_names} == candidate_hashes, "candidate changed")
        check(all(digest((SOURCE / row["path"]).read_bytes()) == row["sha256"] for row in pin["files"]), "engine changed")
        operation_roots = list(self.recovery.glob("i-*")) + list(scratch.glob("i-*"))
        check(len(operation_roots) == 2, "operation root cap")
        final_status = self.launch_git(SOURCE, "status", "--porcelain=v1", "--branch", "--untracked-files=all")
        check(final_status == source_status, "source changed during trial")
        self.result.update(outcome="passed", public_outcome=result["outcome"], managed_state="managed-bytes-consistent",
                           member_count=len(checks), package_count=18, members=checks,
                           lock_sha256=lock_hash, lock_matches_durable_object=True,
                           marker_readback={name: None for name in markers}, protected_sentinel="exact",
                           unknown_sentinel="exact", candidate_readback="134 selected files unchanged",
                           operation_roots=[str(root) for root in operation_roots], final_source_status=final_status)

    def save(self):
        self.result["duration_seconds"] = round(time.monotonic() - self.started, 3)
        self.result["observed_launches_including_driver"] = len(self.launches) + 1
        if self.observations is not None:
            path = self.observations / "result.json"
            self.result["retained"] = inventory((NATIVE, DURABLE))
            path.write_bytes(encoded(self.result))
            # Include this report itself in retained-byte/file accounting.
            for _ in range(4):
                self.result["retained"] = inventory((NATIVE, DURABLE))
                raw = encoded(self.result)
                if path.read_bytes() == raw:
                    break
                path.write_bytes(raw)
        print(json.dumps({key: self.result.get(key) for key in
                          ("outcome", "source_commit", "roots", "public_outcome", "member_count",
                           "retained", "observed_launches_including_driver", "failure")}, indent=2))


def main():
    trial = Trial()
    try:
        trial.run()
    except Exception as error:
        trial.result["failure"] = dict(type=type(error).__name__, reason=str(error))
    finally:
        trial.save()
    return 0 if trial.result["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
