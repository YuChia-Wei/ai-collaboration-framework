# Issue #361 local design delivery

Template adaptation: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`;
proportionate source design report under U001, not an audit or assessment-finding closure.

## Docs updated and boundary decisions

Only the [source-adoption design](../../../design/framework-next/source-adoption/README.md)
and this issue's workflow/task/evidence/report are written. Fixed input is
`b4a147c1bc8ec00fcdb92a7006c142209c61a29f`; exact assigned branch/worktree are
recorded in [workflow.yaml](../workflow.yaml).

The design supplies concrete predecessor/owner/disposition rows, exact 13-package /
90-member source inventory versus 5 / 44 manifest membership, root/Git/config
proposals and an explicit future config-2 Lesson body. The first pilot remains
lesson-minimal / Lesson 0.2.0 / Codex. A later ten-package / 76-member ordinary
source-repository profile is a proposal; five missing #347 engineering packages,
#346 mapping and #356/#357 later mapping retain their owners. Optional maintenance
and optional local backlog are excluded from that ordinary selection.

New records have separate project-owned bindings. Existing Markdown knowledge,
workflow/assessment/release history, frozen backlog and active old transaction
recovery remain with their current owners. Managed recovery, project backups,
quiescence, fresh-session activation and post-use rollback are distinct. Installer
project_readiness remains not-assessed. No active config 1 was found at named
inspected paths; M01 remains unassigned, without a repository-wide absence claim.

## Actual checks and outcomes

Completed direct checks before commit preparation:

| Actual command / bounded observation | Result |
| --- | --- |
| First `Get-Location`, Git root/branch/HEAD/common-dir/status commands | Exact assigned checkout and starting SHA; initially clean |
| `python -B -` with strict UTF-8 decode, `json.loads`, `yaml.safe_load` over the two owned directories | 10 files readable; 3 JSON and 1 YAML parsed; syntax only |
| Same inline read-only script resolves local Markdown file links | 46 local file references resolved; external availability and fragment semantics excluded |
| Same script compares source HEAD and retained raw SHA-256 values | Assigned HEAD unchanged; all 37 selected source files match retained fixed-source identities |
| `git ls-files`, direct metadata/profile/manifest parsing and exact route-path checks | 13 packages / 90 members; manifest 5 / 44; all 16 legacy canonical/Codex/Claude route triples exist |
| `git check-attr --all -- <four selected paths>` | Observed text=auto, eol=lf; no byte-preservation trial |
| `git check-ignore -v --no-index -- <message.tmp> <local-config> <dist-file>` | Message temporary file ignored by existing *.tmp; proposed local/dist paths had no matching ignore |
| `git diff --cached --check`, `git diff --cached --stat`, selected staged diff read and unstaged-path read | No whitespace errors; ten added paths confined to two owned directories; no other tracked changes |

Staging emitted CRLF-to-LF notices for newly authored documents under existing
repository attributes. The owned new files are normalized to LF before final
checks; existing source/records/attributes are untouched. Final direct syntax,
reference, scope and staged-diff checks are rerun after report/task updates.
The exact complete commit-message check ran successfully (exit 0):
`Git commit validation passed for planned message.` The full command, output and
complete message are retained in
[commit-message-validation.txt](../evidence/commit-message-validation.txt).
Message SHA-256: `db8724239030b9a731e4f04b2bdb6c1e2a2a53108a046e17138e50a871e8621b`.
Commit uses those unchanged message-file bytes. This single-message check is the
U001 exception; no history validator or framework gate was run.

Actual source observations already performed: first-command Git path/branch/HEAD/
common-directory/clean status; direct tracked metadata/Git inventory; exact named
path existence; current effective attributes and ignore match; live Issue #361
OPEN read-back. Source identity details are in [source-observation.json](../evidence/source-observation.json).

## Retained failures and limits

- The final staged whitespace check initially failed with `new blank line at EOF`
  in the message-validation transcript (exit 2); the direct-check wrapper then
  exited 1. The extra transcript separator was removed. The validated message
  file and its SHA-256 were unchanged; affected direct checks were rerun before
  commit. Earlier syntax/reference/source checks were already successful.

- Initial web access to the Issue returned cache-miss; initial sandboxed `gh issue
  view` failed on the restricted proxy connection. The same read-only query was
  then run with normal scoped network permission and returned Issue #361 OPEN.
  No credential/settings changes or provider mutation occurred.
- Direct reads of `.dev/project-config.yaml` and an assumed
  `portable-authoring/README.md` reported missing files. The first is retained as
  a bounded absence observation; Git identified the actual authoring handoff as
  `portable-authoring/design.md`, which was then read. No file was created to fill
  either presumed location.
- A small read-only inventory extraction initially treated the existing `groups`
  JSON object as a list and raised AttributeError. After reading its actual shape,
  keyed extraction of F06/F07/F11 succeeded. No product code/import, schema
  validator or fixture ran; this was an analysis-script correction.
- No independent review, behavior, native durability, schema compliance, install,
  migration, release, CI or whole-repository readiness result is claimed. Evidence
  from source documents about other Issues/provider state is not live verification.

## Deferred items and next task

Every prohibited verification class is **deferred-by-owner**, authority **U001**,
responsible owner **program #322 coordinator / P7**: product CLI/help/import,
schema validation, tests/fixtures/build/package/install/migration/probes,
audit/lease/effective-rule/acceptance packets, native handoff validation and CI.
Next action: integrate required source, resolve actual inputs and select focused
new-contract observations before pilot/root activation. No new tooling or schemas
were created to simulate those gates.

Coordinator choices: actual pilot/engine/candidate/scratch/staging/durable recovery/
project-backup roots and failure domain; broader profile adoption and engineering
coverage; affected Claude availability; source workflow policy transition; optional
maintenance; real evidence-adapter bindings; P7 check/pipeline set. These do not
block design completion and do not authorize implementation by this task.

## Receiving instructions

Read this report, [workflow plan](../workflow-plan.md),
[design entry](../../../design/framework-next/source-adoption/README.md) and its
three detailed documents. Read back the local branch's final commit and changed
paths before any integration. The source observation remains bound to the assigned
base, not to later source changes; reconcile changed upstream contracts before
adoption. The completed local design is the only closeout claim. Coordinator owns
first push/PR/merge and Issue/Project read-back. No callback is sent.
