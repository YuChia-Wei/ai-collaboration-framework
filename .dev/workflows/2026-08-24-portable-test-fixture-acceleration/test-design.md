# PERF-001 Deterministic GWT Test Design

## Inputs Used

- GitHub Issue #246 and `fixture-inventory.md` at `4be33ff90de061dc1db221f60e57ff6130cab54a`.
- Fresh framework-source packet `0fb5c4e8fe640a257412988bed243a40ba6a97b5dcacca0c937f3602a22acd38` with `AICTX-EVIDENCE-001`.
- Test implementation is separately authorized and handed to `slice-implementer`; this design is not execution evidence.

## Scenario Set

| ID | Level | Given / When / Then |
| --- | --- | --- |
| GWT-001 | unit | Given no explicit or environment root, when resolving, then select `default` without preflight. |
| GWT-002 | unit | Given different runner and environment roots, when resolving, then runner input wins. |
| GWT-003 | unit | Given only a valid environment root, when resolving, then select it. |
| GWT-004 | unit | Given a missing, file, unwritable, volume-root, symlink, or reparse root, when preflight runs, then fail before material fixtures with a corrective reason. |
| GWT-005 | integration | Given a valid root, when the first ephemeral fixture is created, then a unique run directory and child are contained below it. |
| GWT-006 | unit | Given a verified run and sibling sentinel, when cleaning up, then remove only the run. |
| GWT-007 | unit | Given the root itself, outside path, or nonconforming child, when cleaning up, then refuse without deletion. |
| GWT-008 | integration | Given acceleration and `ephemeral-fixture-io`, when creating a fixture, then consume the accelerated run. |
| GWT-009 | integration | Given acceleration and `durability-storage-semantics`, when creating a fixture, then use OS default. |
| GWT-010 | integration | Given acceleration and `platform-filesystem-semantics`, when creating a fixture, then use OS default. |
| GWT-011 | unit | Given an unknown classification, when routing, then fail closed. |
| GWT-012 | unit | Given Windows, Linux, WSL `/mnt/*`, and WSL-native path inputs, when classifying, then return stable path classes without path bytes. |
| GWT-013 | unit | Given WSL `/mnt/*`, when rendering guidance, then emit one non-blocking actionable warning. |
| GWT-014 | unit | Given WSL-native paths, when rendering guidance, then avoid the mount warning. |
| GWT-015 | unit | Given diagnostics, when rendered, then include route/root type but no private absolute path, user, hostname, or drive letter. |
| GWT-016 | integration | Given default and accelerated runs at one commit, when selecting tests, then ordered identities and outcome semantics match. |
| GWT-017 | integration | Given fewer than three benchmark runs, when validating, then fail with a reproducibility reason. |
| GWT-018 | integration | Given at least three same-profile runs, when complete, then report runs, median, condition, fixture count, and unavailable metrics without estimates. |
| GWT-019 | contract | Given the classification manifest, when validating, then accept only existing files, known classes, and unique ordered paths. |
| GWT-020 | contract | Given the opt-in CI profile, when inspected, then require a caller-supplied root and reject ambient selection. |

## Assertion Notes And Gaps

- Containment uses resolved identity and a direct prefix-conforming child; negative cleanup preserves external/sibling sentinel bytes.
- Routing tests inspect live paths but never persist them. Parity compares ordered test IDs and process exit codes; duration cannot hide failure.
- Platform cases use injected facts where ambient access would be nondeterministic.
- Windows RAM-backed and WSL tmpfs benchmarks require runtime preflight. Unavailable evidence is blocked or deferred, never passed.
- Reparse, NTFS-specific, and durability suites remain outside acceleration. Nested subprocess phase metrics remain `unavailable` until reliable instrumentation exists.

No `.feature` runner is selected. Workflow-owned design stays here; implementation tests belong beside the repository runner under `.ai/scripts/tests/`.
