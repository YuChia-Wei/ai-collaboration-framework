# PERF-002 Execution Retrospective

## Record Metadata

- `record_type`: `workflow-execution-retrospective`
- `record_version`: `1.0.0`
- `workflow_id`: `2026-08-25-package-apply-git-snapshot`
- `issue`: `#251`
- `owner_skill`: `ai-context-governance`
- `implementation_route`: `slice-implementer`
- `status`: `active-until-final-exact-head-audit`
- `created_at`: `2026-08-25T22:04:41+08:00`
- `updated_at`: `2026-08-25T22:22:25+08:00`
- `template_source`: `owner-requested workflow-local retrospective; no repository template`
- `template_version`: `1.0.0`

## Why This Is A Retrospective, Not An ADR

This record preserves execution, validation, and audit lessons from one bounded
implementation workflow. It does not introduce a repository-wide architecture
boundary, dependency direction, or canonical ownership rule. Under
`.dev/adr/WHEN-TO-CREATE-ADR.MD`, an ADR would overstate a local implementation
and validation adjustment. If the benchmark-reuse recommendations below are
later adopted across workflows, that separate policy decision should update the
owning standard and use an ADR only if the repository-wide tradeoff still meets
the ADR decision test.

## Outcome Summary

- The legacy implementation launched Git once or several times per target path.
  At the retained 631-record scale, plan used `3153` Git processes and apply used
  `13272`.
- The snapshot implementation uses payload-independent batches: plan `22`, apply
  `11`, and the real later-hop admission path `22`.
- On the terminal `13a33cc4` benchmark, warm medians were `169.2441546s` legacy
  versus `3.7895519s` snapshot for plan, and `702.1749036s` legacy versus
  `3.7676249s` snapshot for apply.
- Performance proof was not sufficient for integration. Independent fixed-head
  audits found correctness gaps in nested target provenance, pre-lock process
  admission, repository-local ignore policy identity, and later the selection of
  global/system/include config origins. Each finding remained blocking until a
  separate repair and fresh audit.

## Retained Validation History

| Exact subject | Outcome | Duration | Durable lesson |
| --- | --- | ---: | --- |
| `333fafb2` | blocked by Windows TEMP | `0.784052s` | Environment failure is not product failure and is never promoted to passed. |
| `c5aca006` | aggregate failed | `480.283356s` | Focused tests had missed target-validation and staging-cleanup compatibility. |
| `68204f58` | aggregate passed, later superseded | `4827.644808s` | A passing long run does not survive later product mutation or a blocking audit. |
| `fc691245` | aggregate failed | `756.404709s` | Direct-call compatibility must accompany real routed-path coverage. |
| `116893c8` | interrupted after audit drift | `4594.953609s` | Stop and preserve truthful partial evidence when the audited subject changes. |
| `13a33cc4` | terminal aggregate passed | `4865.614824s` | Retain the expensive same-host cold/three-warm baseline as reusable evidence. |
| `7a6f20a0` | exact-head audit failed | read-only | `.git/info/exclude` was missing from snapshot identity. |
| `ee55880b` | exact-head audit failed | read-only | Filtering config origins by already-effective core keys missed introduction of a new policy key/path. |
| `ad0b38a0` | exact-head audit failed | read-only | A comment-only file referenced by `include.path` had no returned value origin and was not bound. |
| `01f73f25` | exact-head audit failed | read-only | Git returned `file:.git/config`; the relative origin was resolved against process cwd instead of target root. |

All ignored dispatch/completion receipts remain local evidence. Failed,
blocked, interrupted, superseded, and passed outcomes are not rewritten.

## Lessons

### 1. Separate performance proof from safety proof

The deterministic process-count invariant establishes that runtime growth is no
longer proportional to payload count. It does not establish dirty, ignore,
attribute, symlink, recovery, or drift correctness. Performance benchmarks and
fixed-head safety audits answer different questions and both are required.

### 2. Reuse the expensive legacy baseline by default

Once a cold plus three-warm legacy baseline is bound to a host, fixture profile,
payload, base, and benchmark implementation, repeating it after every safety-only
repair has sharply diminishing value. Future commits should rerun deterministic
process-count and focused semantic tests. Repeat the full legacy baseline only
when at least one of these changes:

- the legacy emulation or snapshot process topology;
- the benchmark fixture/profile or payload composition;
- the host/storage condition used for the comparison;
- the code path whose wall time is being claimed;
- an auditor identifies timing evidence as materially stale.

This is a workflow recommendation, not yet a repository-wide policy.

### 3. Audit the selection mechanism, not only selected values

Snapshotting the current `core.excludesFile` value and file is insufficient.
The config files that can introduce a different value are part of the identity.
The same rule applies to attributes. A fail-closed snapshot binds the selectors,
their file-backed origins, dormant `include.path` and `includeIf.*.path` targets,
the process-stable global/system config candidate paths, the selected policy
paths, and absence/presence state.

Git may report a repository-local origin as a relative `file:.git/config` value.
Normalize that origin against the target repository root before resolving a
relative include against the origin's directory; never use the orchestrator's
process working directory as repository truth.

### 4. Run adversarial drift probes before expensive validation

The most valuable audit probes mutated state immediately after snapshot return
and before target mutation. Those probes should run before any multi-hour
aggregate benchmark. The minimum pre-long-run probe set should cover:

- HEAD/index and unrelated-worktree drift;
- `.git/info/exclude` and `.git/info/attributes` drift;
- existing configured external policy-file drift;
- introduction of a new policy key/path through a pre-existing config origin;
- creation of an absent `GIT_CONFIG_GLOBAL` or `GIT_CONFIG_SYSTEM` selector;
- policy introduction through a dormant include target;
- real multi-hop and standalone routes with legacy fallbacks forced to raise.

### 5. Bounded Git processes and filesystem work are separate invariants

Binding more constant-size identity sources does not add Git processes, but it
does add a fixed number of filesystem metadata and digest reads. Tests should
assert `constant + O(payload paths)` rather than mistake a calibrated constant
for payload amplification. A change to the fixed constant must still be
explained and measured.

### 6. Independent audit must bind the final clean commit

Any tracked mutation invalidates the previous exact-head audit. Audit findings
must be repaired by the implementation owner, committed, and then re-audited
read-only. An auditor's own probe or repair cannot count as verification.

### 7. Preserve the full failure chain

Blocked, failed, interrupted, and superseded receipts explain why elapsed time
was high and prevent later readers from interpreting one terminal pass as the
only execution. The evidence chain is part of the engineering result.

## AI Usage And Wall-Time Interpretation

Most of the multi-hour wall time came from local Git process startup, filesystem
I/O, and test fixtures. That local runtime is distinct from continuous model
reasoning. Model turns, delegated agents, audit analysis, and tool-result
processing consume Codex usage; a local command merely continuing to run does
not require the model to reason for every elapsed second.

## Residual And Follow-Up

- The current repair must receive a fresh independent exact-head audit.
- The Windows symlink-privilege and case-fold fixtures remain truthful skips;
  no Linux reference execution was performed in this workflow.
- The benchmark-reuse recommendation should remain local until an owner chooses
  whether to promote it into the Long-Running Validation Gate or another
  repository-wide standard.
- No push, pull request, merge, Issue/Project mutation, tag, Release, or
  publication action is authorized by this record.

## Evidence References

- Task ledger: `../tasks/PERF-002-implementation.json`
- Workflow plan: `../workflow-plan.md`
- Terminal receipt: `.tmp/issue-251/external/13a33cc4/completion.yaml` (ignored local evidence)
- Terminal benchmark: `.tmp/issue-251/external/13a33cc4/benchmark.json` (ignored local evidence)
- Terminal summary canonical digest: `eab959ab235114bdaee3f36c6e0acf244994f88bba8b509b2f49802017d33ade`
- Terminal benchmark canonical digest: `79df8f25189e0468eccb2fc358c336ec0dcfd08a66ac255cd993da9935743ca0`
