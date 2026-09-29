# ENF-001 Governance Enforcement Evidence

## Evidence Metadata

- Workflow: `2026-07-21-v0-5-0-development`
- Task: `V050-005`
- Backlog item: `ENF-001`
- Disposition subject:
  `d5d74eae4717fc0a5cb9a008667094dbfefe9f35`
- Published baseline:
  `v0.4.2@f474c3b058cb9f89f93929e0732fc1f276422dd9`
- Status: completed

## Published-Path Decision

The v0.5.0 candidate set contains 14 exact paths. All 14 exist in v0.3.0,
v0.4.0, v0.4.1, v0.4.2, the pinned subject, and the current portable package
profile. Ten paths are byte-identical across all four releases and the subject.
The three historical auditor templates and `check-test-compliance.sh` evolved
once before v0.4.2; their v0.4.2 blobs exactly match the pinned subject.

| Decision | Count | Compatibility result |
| --- | ---: | --- |
| retain | 7 | Keep 3 historical auditor templates and 4 compatibility/manual scripts at their exact packaged paths. |
| deprecate | 7 | Keep the exact packaged script paths, mark their shell lifecycle `deprecated`, and retain an explicit replacement/migration direction. |
| relocate | 0 | No candidate has an evidence-backed destination and downstream migration proof. |
| remove | 0 | No candidate has the downstream evidence required to remove a published path safely. |

The machine-readable source is
[`v050-published-path-disposition.yaml`](v050-published-path-disposition.yaml).
Its v2 validator checks exact candidate/entry parity, immutable subject bytes,
presence across all declared published versions, declared identical or evolved
blob history, latest-published-to-subject equality for evolved paths, package
profile inclusion, shell lifecycle agreement, consumer/evidence references,
and removal-specific downstream proof. Legacy v1 manifests remain readable.

Deprecation is not removal authorization. A later version must update the
manifest with independent downstream evidence, compatibility impact, migration
guidance, and exact distribution outcome before relocating or removing any of
these paths.

## Wrapper Semantic Contract

The canonical skill manifest remains the authority. Runtime wrapper validation
now checks:

- exact runtime directory and `SKILL.md` entry path;
- frontmatter `name` equality with canonical `asset_id`;
- non-empty routing description;
- citations for the canonical registry, spec, references, examples, human
  guide, and declared template maps;
- the exact canonical-authority fallback;
- exact Codex/current and Claude/compatibility thin-wrapper identity lines;
- byte-equivalent Codex and Claude projections after normalizing only those
  declared runtime identity differences.

The current 14 skill pairs pass. Five Claude descriptions were normalized from
generic “the agent” wording to the explicit Claude identity, and both
`dev-workflow` wrappers now cite the canonical machine-readable capability
profile they consume.

## Dedicated Governance CI

`.github/workflows/governance.yml` is the read-only
pull-request route for AI-context and portable governance surfaces. It is
separate from package-candidate ownership and does not own `releases/**`,
tags, or GitHub Release mutation.

## Validation

Focused local validation before the core checkpoint:

- 20 file-disposition GWT cases and the actual v0.5.0 manifest pass;
- 15 wrapper-metadata GWT and 14 canonical/runtime skill projections pass;
- 18 sub-agent-adapter GWT and 10 language/parity GWT pass;
- 12 dependency/version GWT plus the offline validator pass;
- 26 aggregate-runner/shell GWT plus the 14-asset lifecycle registry pass;
- 5 governance-workflow GWT pass, including exact filters, pinned setup,
  read-only permissions, required commands, and mutation exclusion;
- `git diff --check` passes.

The slow package suite passed cases 1 through 18 before the bounded command
timed out; case 19 passes independently. At the core checkpoint, the
committed-tree aggregate quick gate and hosted Ubuntu runs were still pending.

The first committed-tree quick gate at `8fc982d` completed 28 required checks:
27 passed and the package GWT gate failed in upgrade cases 16 and 17. The
package integrity validator correctly rejected direct references from portable
`check-all.sh` and `shell-assets.yaml` bytes to the excluded dated disposition
manifest. The correction introduces
`.ai/distribution/governance-checks.yaml` plus the source-only
`validate-source-governance.py` runner. Portable scripts now reference only the
stable runner, while the source registry retains the exact dated evidence
path. The source/downstream runner fixtures, source registry validator, shell
registry, AI-context validator, and six governance-workflow GWT cases pass.
Affected committed-tree package fixtures 16 and 17 pass after the correction.
Windows Git Bash passes 28/28 with zero failed, warning, or deferred checks.
Hosted Ubuntu portable run `29770661564` passes the same 28/28 gate, and
dedicated governance run `29770662383` passes every read-only step at
`83a0c1c`. Package-candidate run `29770662983` fails closed at candidate
discovery because REL-001 has not created a v0.5.0 release record; its log
reports `found none`, not an ENF-001 contract failure.
