# SAG-002 Sub-Issue Binding Corrigendum

## Corrigendum Metadata

- `corrigendum_id`: `sag-002-sub-issue-binding-2026-08-05`
- `workflow_id`: `2026-08-05-sub-agent-reachability`
- `owner_skill`: `ai-context-governance`
- `status`: `final-corrigendum`
- `created_at`: `2026-08-05T20:56:32+08:00`
- `corrects`: `release-allocation-2026-08-05-sub-agent-reachability`
- `scope`: provider relationship projection and receipt only

## Owner Authorization

On 2026-08-05, the owner explicitly approved the proposed provider correction: formally bind implementation Issue #119 as a GitHub sub-issue of canonical Issue #118. The owner also requested corresponding online and local documentation updates.

## Correction

The release-allocation addendum correctly retained the pre-correction fact that no formal relationship had been created. This corrigendum records the subsequent owner decision and does not rewrite that historical final artifact.

| Record | Formal GitHub relationship after correction | Canonical role |
| --- | --- | --- |
| Proposal #94 | no parent; no sub-issues | intake and seven-decision provenance only |
| Issue #118 | parent: none; sole child: #119 | canonical provider projection for `SAG-002` |
| Issue #119 | parent: #118 | dependent runtime-execution implementation slice |

The relationship is intentionally `#118 -> #119`, not `#94 -> #118/#119`: `SAG-002` remains included exactly once through #118, while #94 remains proposal provenance and #119 remains its dependent slice.

## Provider Read-Back

- GitHub GraphQL read-back at `2026-08-05T20:56:32+08:00` confirms closed/completed #118 has one closed sub-issue, #119.
- The same read-back confirms closed/completed #119 has parent #118; Proposal #94 has neither a formal parent nor formal sub-issues.
- Project #3 retains #118 as Done / P1 High / Approved / v0.9.0 / Not yet published. No release allocation, Issue state, target-release, Published in, packaging, tag, GitHub Release, or publication field changed.
- A documentation comment records the correction on [Issue #118](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/118#issuecomment-5191998686).

## Policy Interpretation

`.dev/backlog/providers/github.yaml` sets `infer_sub_issues: false`, which prevents automated or bulk inference. It does not prohibit this later explicit owner-approved relationship. The correction is therefore provider-specific dashboard projection, not a change to the canonical `SAG-002` allocation or the completed #94 implementation scope.

## Validation Boundary

No local validation script, test, build, formatter, `check-all`, aggregate gate, or verification program ran. Evidence consists of manual file review and hosted GitHub relationship/Issue/Project read-back.
