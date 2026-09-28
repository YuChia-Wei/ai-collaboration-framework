# Issue #409 implementation and focused evidence

The original-name mode is the default for new preset selections. Explicit prefixed
mode uses `aicf-`; existing saved v1 selections keep their prior names. See the
workflow plan and Issue #409 for owner authorization and acceptance criteria.

The implementation worker `/root/implement_naming` was the sole tracked writer
for source, schema, tests and user guidance, then released ownership to `/root`.
The parent added the current format-extension note and owns workflow records.

## Executed checks

| Selection | Result | Duration |
| --- | --- | --- |
| RC2 adapters, isolated runpy bootstrap | 5 passed | 0.016 s |
| RC2 distribution | 9 passed | 0.099 s |
| RC2 maintenance, explicit TEMP fixture parent | 7 passed | 0.110 s |
| New skill naming, explicit TEMP fixture parent | 9 passed | 6.953 s |

Exact command forms are retained in `tasks/NAMING-IMPLEMENT.json`. The naming
run observed 142 files / 583,028 bytes and successfully cleaned its unique run.
The tests derive/read nonempty synthetic subsets and locks, check both runtimes,
saved modes, old formats, both rename directions, no-op updates, drift and collisions.
Engine admission/native setup in planner fixtures is mocked; manual fixture
realization is not evidence of production apply/recovery or target installation.

Changed Python AST parsing and `git diff --check` passed. Deterministic AST
comparison showed SelectionV1 equals the prior Selection definition, all unrelated
contract definitions stayed unchanged, and the rc.1 renderer source stayed unchanged.
These are static/fixture results, not hosted or runtime UI acceptance.

## Earlier failures retained

The first distribution run failed its invalid empty-catalog fixture at
`CatalogFiles: array budget`. The parent independently reproduced that exact test
on clean base `ab1abc7be7e6d903ad601e372263c30f273f1a51` (1 error, 0.005 s).
The fixture now uses a valid nonempty catalog with an empty selection; production
minimum-member validation was not weakened.

The first naming run was blocked before tests by a sandbox permission error at
the explicit TEMP fixture parent. Normal scoped escalation enabled the subsequent
run. No automatic-approval rejection occurred; no unchanged behavioral retry was
used. Original failure output remains in the conversation/tool history.

## Remaining boundary

Independent review is the next stage. No production apply/recovery, Codex/Claude
UI discovery, CI restoration, downstream adoption, push, PR, merge, Issue closure
or publication was performed. This report does not activate the #322 exception or
convert earlier P7 deferrals into passes.

## Workflow metadata checks

The full `validate-workflow-artifacts.py` invocation failed before completion:
its timestamp parser received a YAML datetime from unchanged
`.dev/workflows/2026-09-23-portable-authoring/workflow.yaml`. The original file
matches base commit bytes; no global validator pass is claimed and the unrelated
historical record/validator was not changed. Scoped checks use the repository's
validator functions against this workflow's actual locator/tasks and index row.
Their first run caught this new row's unsupported `entry` link label; it was
corrected to the validator's required `plan` label before the next check.
The reproducible scoped driver is ignored `artifacts/skill-naming/check-workflow-scope.py`.
