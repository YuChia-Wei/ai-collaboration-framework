"""Issue 335 opt-in real Git regression; run only this file on a clean commit.

python -I -B tests/framework_next/test_pr_git_worktree.py --output-root <absolute>
Evidence and the unique disposable fixture are retained, including on failure.
No provider, target installation, real-repository setting or cleanup operation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import runpy
import stat
import subprocess
import sys
import time
import traceback

SOURCE = Path(__file__).resolve().parents[2]
MAX_PUBLIC = 32
MAX_GIT = 96


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def append(path, value):
    with path.open("ab") as stream:
        stream.write(encoded(value))


def git_events(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()] if path.exists() else []


def child_entry(script, fixture_root, event_path):
    """Observe actual Git Popen requests without replacing product transport."""
    def audit(event, args):
        if event != "subprocess.Popen":
            return
        executable, argv, cwd, environment = args
        if executable is None:
            if isinstance(argv, str):
                match = re.match(r'^\s*(?:"([^"]+)"|(\S+))', argv)
                executable = (match.group(1) or match.group(2)) if match else ""
            else:
                executable = argv[0]
        check(Path(str(executable)).name.lower() in {"git", "git.exe"}, "Unexpected product subprocess")
        check(Path(cwd).is_relative_to(fixture_root), "Product Git escaped the fixture")
        check(len(git_events(event_path)) < MAX_GIT, "Git launch cap reached")
        check(environment["GIT_CONFIG_NOSYSTEM"] == "1" and environment["GIT_CONFIG_GLOBAL"] == os.devnull,
              "Product Git lost configuration isolation")
        append(event_path, {"kind": "product-git", "argv": argv, "cwd": str(cwd)})
    sys.addaudithook(audit)
    sys.argv = [str(script), "--request", "-"]
    runpy.run_path(str(script), run_name="__main__")


class SelectedRun:
    def __init__(self, output_root):
        # Existing test support supplies contained, non-reparse fixture ownership
        # and measured path/byte accounting; this file adds narrower launch caps.
        sys.path.insert(0, str(Path(__file__).parent))
        import support
        self.run = support.FixtureRun(output_root)
        self.root = self.run.root
        self.events = self.root / "git-launches.jsonl"
        self.results = self.root / "process-results.jsonl"
        self.public_outputs = self.root / "public-results.jsonl"
        self.report_path = self.root / "report.json"
        self.public_count = 0
        self.fixture_write_count = 0
        self.cases = []
        self.started = datetime.now(timezone.utc).isoformat()
        self.started_clock = time.monotonic()
        self.script = SOURCE / "src/skills/pr/scripts/pr.py"
        self.subject_files = [self.script, SOURCE / "src/skills/pr/references/operations.md", Path(__file__).absolute()]
        self.hashes = {p.relative_to(SOURCE).as_posix(): sha256(p.read_bytes()).hexdigest() for p in self.subject_files}
        self.head = None
        self.run.measure()

    def measure(self):
        value = self.run.measure()
        check(len(git_events(self.events)) <= MAX_GIT, "Git launch cap exceeded")
        check(self.public_count <= MAX_PUBLIC, "Public launch cap exceeded")
        # Six finite one-file Git setup commands, with templates/hooks/automatic
        # maintenance disabled, reserve 24 creations each (including transient
        # objects/locks). PR calls reserve four lock/temp/record creations each.
        # Six further slots cover authored paths and evidence. This conservative
        # bound is separate from measured post-step paths, not an exact census.
        creation_bound = 6 + 24 * self.fixture_write_count + 4 * self.public_count
        check(creation_bound <= 256, "Conservative created-file budget exceeded")
        check(value["observed_files"] <= creation_bound, "Observed files exceed reserved creation bound")
        value["created_file_upper_bound"] = creation_bound
        return value

    def put(self, path, raw):
        self.run.verify()
        check(path.is_absolute() and path.is_relative_to(self.root), "Fixture edit escaped owned child")
        check(len(raw) <= 16384, "Authored fixture input too large")
        check(self.run.authored_bytes + len(raw) <= 1024 * 1024, "Authored byte cap exceeded")
        if path.exists():
            info = path.lstat()
            check(stat.S_ISREG(info.st_mode) and not path.is_symlink()
                  and not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
                  "Fixture edit requires a regular owned file")
            path.write_bytes(raw)
            self.run.authored_bytes += len(raw)
            self.measure()
        else:
            self.run.write(path, raw)

    def git(self, *args, cwd, expect=0, category="fixture-git", writing=False):
        check(len(git_events(self.events)) < MAX_GIT, "Git launch cap reached")
        self.fixture_write_count += int(writing)
        self.measure()
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",
                   GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
        argv = ["git", "--no-pager", "--no-replace-objects", "-C", str(cwd), *args]
        append(self.events, {"kind": category, "argv": argv, "cwd": str(cwd)})
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=30, shell=False)
        append(self.results, {"argv": argv, "exit_code": result.returncode,
                              "stdout_sha256": sha256(result.stdout).hexdigest(),
                              "stderr": result.stderr.decode("utf-8", errors="replace")})
        self.measure()
        check(result.returncode == expect, f"Git command exited {result.returncode}, expected {expect}")
        return result.stdout

    def public(self, name, operation, expected="succeeded", code=None, **fields):
        self.run.verify()
        check(self.public_count < MAX_PUBLIC, "Public launch cap reached")
        request = {"operation": operation, "project_root": str(self.linked),
                   "package_root": str(self.script.parents[1]), **fields}
        raw = encoded(request)
        check(self.run.authored_bytes + len(raw) <= 1024 * 1024, "Authored byte cap exceeded")
        self.run.authored_bytes += len(raw)
        before = {p.name: p.read_bytes() for p in self.store.iterdir()}
        argv = [sys.executable, "-I", "-B", str(Path(__file__).absolute()), "--child",
                str(self.script), str(self.root), str(self.events)]
        self.public_count += 1
        started = time.monotonic()
        result = subprocess.run(argv, cwd=SOURCE, input=raw, capture_output=True, timeout=45, shell=False)
        check(len(result.stdout) + len(result.stderr) <= 1024 * 1024, "Public capture exceeds selected limit")
        append(self.public_outputs, {"case": name, "request": request, "exit_code": result.returncode,
                                    "stdout": result.stdout.decode("utf-8", errors="replace"),
                                    "stderr": result.stderr.decode("utf-8", errors="replace"),
                                    "duration_seconds": round(time.monotonic() - started, 3)})
        self.measure()
        value = json.loads(result.stdout)
        check(value["outcome"] == expected, f"{name}: expected {expected}, got {value}")
        check(result.returncode == (0 if expected == "succeeded" else 1), name + ": wrong process exit")
        check(not result.stderr, name + ": unexpected stderr")
        if code:
            check(code in [x["code"] for x in value.get("diagnostics", [])], name + ": diagnostic differs")
        if expected != "succeeded" or operation == "render":
            check(value["mutation_state"] == "none", name + ": unexpected mutation state")
            check(before == {p.name: p.read_bytes() for p in self.store.iterdir()}, name + ": changed store")
        else:
            check(value["mutation_state"] == "committed", name + ": prepare did not publish")
        self.cases.append({"name": name, "expected_outcome": expected, "actual_outcome": value["outcome"],
                           "diagnostic": code, "assertions": "passed"})
        return value

    def prepare(self, name, **expected):
        return self.public(name, "prepare", repository_root=str(self.linked), base_commit=self.base,
                           head_commit=self.tip, content={"title": "Worktree regression",
                           "summary": "One committed UTF-8 text change.", "validation": [], "references": []}, **expected)

    def render(self, name, reference):
        result = self.public(name, "render", reference=reference, repository_root=str(self.linked))
        check(result["subject_verified"] is True, name + ": Git subject was not rebound")
        check(result["subject"]["head_commit"] == self.tip and result["subject"]["base_commit"] == self.base,
              name + ": wrong Git selection")
        check(result["subject"]["diff_recipe"] == "pr.diff/v1", name + ": diff recipe changed")
        return result

    def execute(self):
        self.head = self.git("rev-parse", "HEAD", cwd=SOURCE, category="source-identity").decode().strip()
        check(not self.git("status", "--porcelain=v1", cwd=SOURCE, category="source-identity"),
              "Selected execution requires a clean immutable source commit")
        repository = self.run.case("repository")
        empty_template = self.run.case("empty-template")
        self.linked = self.root / "linked"
        common = ("-c", "core.hooksPath=" + str(empty_template), "-c", "commit.gpgsign=false",
                  "-c", "gc.auto=0", "-c", "maintenance.auto=false")
        self.git(*common, "init", "--initial-branch=fixture", "--template=" + str(empty_template), cwd=repository, writing=True)
        changed = repository / "change.txt"
        for text, title in ((b"before\n", "base fixture"), ("after: 測試\n".encode(), "head fixture")):
            self.put(changed, text)
            self.git(*common, "add", "--", "change.txt", cwd=repository, writing=True)
            self.git(*common, "-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@example.invalid",
                     "commit", "-m", title, cwd=repository, writing=True)
            oid = (repository / ".git/refs/heads/fixture").read_text().strip()
            check(re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", oid) is not None, "Invalid fixture commit")
            if title == "base fixture":
                self.base = oid
            else:
                self.tip = oid
        self.git(*common, "worktree", "add", "--detach", str(self.linked), self.tip, cwd=repository, writing=True)
        self.store = self.linked / "notes/pull-requests"
        self.store.mkdir(parents=True)
        config = repository / ".git/config"
        original_config = config.read_bytes()
        check(b"worktreeconfig" not in original_config.lower(), "Extension unexpectedly enabled")
        gitdir = (self.linked / ".git").read_text().strip().removeprefix("gitdir: ")
        worktree_config = Path(gitdir) / "config.worktree"
        check(worktree_config.is_relative_to(self.root), "Linked Git directory escaped fixture")
        pinned = ("-c", "core.fsmonitor=false", "-c", "core.attributesFile=" + os.devnull,
                  "-c", "core.quotePath=true", "-c", "color.ui=false")
        self.git(*pinned, "config", "--worktree", "--no-includes", "--null", "--list", cwd=self.linked, expect=128)
        self.cases.append({"name": "old-explicit-scope-reproduces", "expected_exit": 128, "actual_exit": 128})
        prepared = self.prepare("disabled-extension-prepare")
        rendered = self.render("disabled-extension-render", prepared["reference"])
        enabled_config = original_config + b"\n[extensions]\n\tworktreeConfig = true\n"
        self.put(config, enabled_config)
        check(not worktree_config.exists(), "Missing-config case is not absent")
        missing = self.render("enabled-missing-worktree-config", prepared["reference"])
        check(missing["subject"] == rendered["subject"], "Missing optional scope changed diff subject")
        safe = b"[fixture]\n\tnote = safe\n"
        self.put(worktree_config, safe)
        safe_prepared = self.prepare("enabled-safe-worktree-config")
        record = json.loads((self.store / (safe_prepared["reference"]["id"] + ".pr.json")).read_bytes())
        check(record["subject"] == rendered["subject"], "Safe enabled scope changed diff subject")
        for name, content in (
            ("worktree-diff", b"[diff]\n\torderFile = missing-order-file\n"),
            ("worktree-include", b"[include]\n\tpath = missing-include\n"),
            ("worktree-include-if", b'[includeIf "gitdir:never-match/"]\n\tpath = missing-include\n'),
            ("worktree-promisor", b'[remote "fixture"]\n\tpromisor = true\n'),
        ):
            self.put(worktree_config, content)
            self.prepare(name, expected="unsupported", code="git-config")
        self.put(worktree_config, b"[broken\n")
        self.prepare("invalid-worktree-config", expected="blocked", code="git-read")
        self.put(worktree_config, safe)
        self.put(config, original_config + b"\n[extensions]\n\tworktreeConfig = invalid-boolean\n")
        self.prepare("invalid-extension-value", expected="blocked", code="git-read")
        for name, content in (
            ("local-diff", b"\n[diff]\n\torderFile = missing-order-file\n"),
            ("local-include", b"\n[include]\n\tpath = missing-include\n"),
        ):
            self.put(config, enabled_config + content)
            self.prepare(name, expected="unsupported", code="git-config")
        self.put(config, enabled_config)
        self.subject = rendered["subject"]
        self.measure()
        check(self.hashes == {p.relative_to(SOURCE).as_posix(): sha256(p.read_bytes()).hexdigest()
                              for p in self.subject_files}, "Selected source/test bytes drifted")

    def finish(self, outcome, failure=None):
        counts = self.measure()
        events = git_events(self.events)
        report = {"issue": 335, "task": "CR335-002", "source_head": self.head,
                  "source_sha256": self.hashes, "started_at": self.started,
                  "completed_at": datetime.now(timezone.utc).isoformat(),
                  "duration_seconds": round(time.monotonic() - self.started_clock, 3),
                  "outcome": outcome, "failure": failure, "fixture_root": str(self.root),
                  "cases": self.cases, "public_launches": self.public_count, "git_launches": len(events),
                  "git_launch_kinds": {k: sum(e["kind"] == k for e in events)
                                       for k in ("source-identity", "fixture-git", "product-git")},
                  "limits": {"public_launches": MAX_PUBLIC, "git_launches": MAX_GIT, "created_files": 256,
                             "authored_bytes": 1024 * 1024, "fixture_commits": 2,
                             "authored_repository_files": 1, "linked_worktrees": 1},
                  "accounting": counts, "git_subject": getattr(self, "subject", None),
                  "measurement_scope": "Git Popen launch requests are recorded before execution, including expected failures. "
                      "Files are distinct paths observed after steps; short-lived Git internals are not an exhaustive creation-event census. "
                      "Authored bytes include fixture edits and public JSON inputs; generated evidence is reported as retained bytes.",
                  "public_execution": "Isolated Python subprocess runs the actual CLI main via runpy; audit observes Git without replacing transport.",
                  "retention": "Entire unique fixture and evidence retained; no recursive cleanup or real repo config edit.",
                  "other_verification": "deferred-by-owner under U001; coordinator/P7 owns provider, candidate, installed target and CI checks"}
        self.report_path.write_bytes(encoded(report))
        report["accounting"] = self.measure()
        self.report_path.write_bytes(encoded(report))
        print(json.dumps({"outcome": outcome, "report": str(self.report_path), "public_launches": self.public_count,
                          "git_launches": len(events), "accounting": report["accounting"]}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    selected = SelectedRun(args.output_root)
    try:
        selected.execute()
    except BaseException as exc:
        selected.finish("failed", {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
        return 1
    selected.finish("passed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--child":
        child_entry(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        raise SystemExit(main())
