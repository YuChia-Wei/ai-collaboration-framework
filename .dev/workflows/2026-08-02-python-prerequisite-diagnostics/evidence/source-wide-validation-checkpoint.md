# Source-Wide Python Prerequisite Validation Checkpoint

## Metadata

- `workflow_id`: `2026-08-02-python-prerequisite-diagnostics`
- `backlog_id`: `TOOL-002`
- `github_issue`: `#77`
- `baseline_finding`: `ASM-20260730-001#AIC-004`
- `subject_commit`: `cc08a36ca50cd284f3163747aa335bd6c934212f`
- `validated_at`: `2026-08-03T02:03:07+08:00`
- `environment`: Windows, Python `3.13.14`, PyYAML `6.0.3`, Git Bash

## Outcome

The complete source-wide critical gate passed from the committed subject with
exit `0`. Every selected required check completed without a required failure or
advisory warning. This supersedes the earlier timed-out packaging attempt; that
attempt remains recorded as not passed rather than being rewritten as success.

No `.dev/releases/v0.8.0/**` artifact was created, and no release preparation,
tag, publication, dependency installation, or persistent host mutation was
performed.

## Gate Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Shared prerequisite contract | `passed` | `test_python_prerequisites.py`: 14/14 passed outside the sandbox; no ACL skip |
| Source-only direct entrypoints | `passed` | `test_python_source_entrypoints.py`: 3/3 passed; all 13 direct help paths and all 12 PyYAML negative paths covered |
| Portable/package projection | `passed` | `test_ai_context_packaging.py`: 28 passed; the one retained downstream integration was conditionally skipped because `AI_CONTEXT_DOWNSTREAM_REPO` was not supplied and is not counted as passed |
| Extracted planner regressions | `passed` | packaging cases 006 and 014 passed after the current-process probe, transitive fixture, and governed requirements-path fixes |
| AI context and wrappers | `passed` | `validate-ai-context.py` reported 24 active indexes, 16 canonical skills, 2 runtime roots, 34 canonical manifests, and structural root bilingual parity |
| Entrypoint registry | `passed` | 25 production CLIs: 12 portable and 13 source-only; 23 PyYAML profiles and 2 standard-library-only profiles |
| Shell assets | `passed` | 15 tracked shell assets; the runtime launcher is classified and executable |
| Aggregate critical gate | `passed` | started `2026-08-03T01:55:28+08:00`; elapsed `459.5s`; exit `0` |
| Release boundary | `passed` | `.dev/releases/v0.8.0` absent; general governance workflows contain no release mutation |

`Selected Git Commit Messages` was `not-applicable` because `COMMIT_RANGE` was
not set. The retained downstream integration case was also not executed without
its explicit external-repository input. Neither outcome is represented as a
pass.

## Failure Discovery And Resolution

The first final aggregate attempt failed only at the packaging GWT check. A
minimum probe proved that Python `TemporaryDirectory()` could create its parent
inside the sandbox but could not create a child (`WinError 5`); the identical
probe succeeded outside the sandbox. The sanctioned replacement therefore ran
outside the sandbox with `TEMP`, `TMP`, and `TMPDIR` pointed at an ignored,
workspace-local isolation root.

That valid rerun exposed two real defects rather than an environment-only
failure:

1. synthetic packages omitted `python_prerequisites.py` and
   `python-entrypoints.json`, even though the guarded planner required them;
2. direct preflight launched a fresh interpreter instead of inspecting the
   current process, and its package recovery command pointed at
   `payload/requirements.txt` rather than the envelope's governed file.

Commit `cc08a36ca50cd284f3163747aa335bd6c934212f` corrects those defects. The
focused regressions and complete package suite passed before the aggregate gate
was rerun from that commit.

## Commands

```text
python .ai/scripts/tests/test_python_prerequisites.py -v
python .ai/scripts/tests/test_python_source_entrypoints.py -v
python .ai/scripts/tests/test_ai_context_packaging.py -v
AI_CONTEXT_PYTHON=<python-3.13.14> bash .ai/scripts/check-all.sh --critical
```

## Next Gate

Independent `ai-context-auditor` read-back must verify this committed evidence
and the current repository state before `ASM-20260730-001#AIC-004` can be
reconciled as resolved. PR integration and merged-`main` read-back remain
pending.
