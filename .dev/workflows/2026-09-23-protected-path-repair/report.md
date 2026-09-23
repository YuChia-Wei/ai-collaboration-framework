# Protected path repair report

Implementation and selected simulated regressions are complete; the actual F:
public plan is pending a clean repair commit. This is not native apply/recovery,
CI, target readiness or whole-P7 acceptance.

## Repair and compatibility

`installation_plan._protected_path` now catches only Windows WinError 1 from
strict resolution. It checks direct directory ancestry, nonzero device/inode
identities and stable identity/mode across the existing Windows long-name query.
The same final containment and case-sensitive relative-component comparison
still rejects aliases. No directory entries or protected data trees are scanned.
`installation_state._windows_long_path` is an extraction of the existing root
query; direct drive mapping, drive type and bounded long-name result checks stay
unchanged. Both existing modules remain in the ten-file engine pin.

The `_Reader.read` path still rejects hardlinks and binds raw bytes to file
identity. Expected absence, required presence and SHA-256 checks are unchanged.
The shared caller in `installation.py` receives the repaired path admission;
its writer/recovery flow and all other planner semantics are untouched.

## Evidence

- `python -I -B tests/framework_next/test_protected_paths.py --mode regressions`:
  **passed**, nine tests in 0.099 seconds. Cases use simulated Windows APIs,
  metadata and byte streams; no native-link or filesystem acceptance is implied.
- AST parsing of the three changed Python files, UTF-8 reads, workflow YAML
  parsing and `git diff --check`: **passed**.
- Actual F: plan: **pending**, selected command
  `python -I -B tests/framework_next/test_protected_paths.py --mode actual-plan`.
  Its fixed source evidence, inputs, caps and retention are in
  [workflow-plan.md](workflow-plan.md) and the test's selected mode.
- Live Issue #383 was read as OPEN with the assigned scope. Initial sandbox
  proxy failure is retained as an environment observation, followed by one
  successful scoped read-only query. No provider mutation occurred.

Unselected legacy/full/history/formal/audit/lease/effective-rule-packet/hosted
checks remain **deferred-by-owner** under U001, owner program #322 coordinator /
P7. Next action is separately selected integration and P7 restoration/adoption.
No push, PR, merge, Issue closure, release/tag or target installation occurred.
