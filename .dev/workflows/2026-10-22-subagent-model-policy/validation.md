# Local implementation evidence

Scope: Issue #487, local source and project settings. No push, PR, merge,
release, publication, Issue closure or paid model matrix was performed.

## Executed checks

- `python -I -B tests/run.py --suite distribution --suite schemas --suite loader`:
  153 tests, 0 failures, 0 errors, 0 skipped (2026-10-22, Windows, 14.41 seconds).
- Coverage includes explicit task/tier selection, premium authority requirement,
  provider/effort observations, conflicting overrides, legacy v1/v2 role reading,
  exact old engine catalog/lock closures, v3 adapter projection, policy plan/apply,
  replay/stale rejection, unsafe paths/case aliases/hardlinks, extension round
  trips, three-way comparison and portable pinned CLI tamper rejection.
- Existing maintenance checks cover retention of unknown project-owned agents
  and custom resources. They are small contract fixtures, not native downstream
  framework upgrade acceptance.
- `git diff --check`: passed before the implementation snapshot.
- Policy initialization used the source manager's `plan`/`apply` API against this
  repository; raw readback SHA-256:
  `6fd712085e48a8a540396b829629c3f5ccf1a954fa4cad154e25674a51ad571e`.
- Parsed the resulting project policy, Codex TOML and Claude JSON. Native defaults
  match the policy; all seven existing project Codex profiles have no conflicting
  fixed model/effort/provider pins. Framework lock and installed skill bytes were
  not edited. The source project's old installed skill snapshot remains separate.
- Exported all 25 engine members from immutable commit
  `5d80f8cf939036d9a005a2af28496366937f5c6f` and exercised the public
  `manage-sub-agents.py` interface in isolated Python outside the source checkout.
  Project inspect matched the above hash; plan plus apply returned `unchanged`.
  Resolve returned Luna/medium and Sol/medium for Codex inventory/review, and
  Haiku/no effort and Sonnet/medium for Claude inventory/review. All remained
  `configured`, availability unknown, invocation unobserved.

Disposable tests used bounded `F:/aicf-subagents-487` on the rechecked NTFS RAM
disk with per-process TEMP/TMP only. No machine-wide temporary setting changed.

## Project settings and reproduction

`.ai/custom/sub-agent-policy.json` and `.claude/settings.json` are tracked project
inputs. Existing `.codex/config.toml` is intentionally ignored/local; its agents
defaults were explicitly merged to `gpt-6-luna` and `medium`, retaining enabled,
concurrency and interrupt settings. A new checkout must explicitly merge the
manager's `native_settings_proposal`; a tracked policy does not activate native
settings by itself. Existing project-owned profiles are outside this project's
17-skill installed lock and were edited without rewriting managed installation.

Root AGENTS English and Taiwan Traditional Chinese carry matching rules. The
public source AGENTS template receives portable task/cost/authorization/ownership
principles, without copying source repository governance or specific model IDs.

## Independent review

Reviewer: `subagent_policy_review`, a separate read-only Codex agent requested
as `gpt-6.1-sol` with `medium` reasoning and fresh bounded context. Reviewed base
`1d9a42c80a0f0db2d69dc36d335a090bfb071281` through head
`5d80f8cf939036d9a005a2af28496366937f5c6f` using the installed `code-reviewer`
common method, source policy, guardrails and Issue #487 acceptance criteria.

Outcome: no supported actionable findings. Static coverage included policy
selection and file operations, CLI authentication, exact current/legacy closure
separation, v1/v2/v3 compatibility, runtime projections and documentation/tests.
No reviewer tests or mutations were performed; the 153 passing checks were
author-provided evidence. No technology knowledge package or exhaustive security
coverage was requested or claimed. Disposition: local implementation accepted for
this scope, with runtime/environment/provider limitations retained below.

This review covers the model-policy slice. The following resource-management
slice has separate implementation and review evidence.

## Resource registry and routing

- Fixed implementation: `fe0928e74b344c1a0208261ab764e6a0630cbbbc`.
- `python -I -B tests/run.py --suite distribution --suite schemas --suite loader`:
  166 tests, 0 failures/errors/skips, Windows, 18.77 seconds. Includes 13 new
  resource registry cases and source-free public CLI registry plan/apply.
- Project migration through registry plan/apply adopted 7 project roles,
  20 authoring/reference resources and 8 runtime entries; all hashes matched.
  Managed installation, model policy and native runtime names were preserved.
- Independent reviewer `subagent_registry_review`, requested Sol/medium with
  fresh bounded context, reviewed `ea7be1c81e0dd0b43245635109473d48e41c8df9`
  through the fixed implementation above. It inspected common contract/routing,
  path/write/recovery boundaries, source closures and project projections.
- One P2: the adopted auditor runtime retained obsolete guardrails classifier
  and preflight requirements contrary to its selected project role/playbook.
  The author repaired its project original through registry plan/apply, regenerated
  the native entry, and read back all registry resources. Permission and fixed
  independent-review boundaries remain. Affected independent re-review passed
  at `015c44e692f0500a4b58c34ed7ec55583e4a5602`; the original P2 is resolved,
  with no new related actionable findings.
- No other supported actionable findings. Reviewer performed no tests or writes;
  this is not specialist security, hosted CI or runtime activation evidence.
- Actual-source artifacts at `015c44e692f0500a4b58c34ed7ec55583e4a5602`, with
  local-only version `0.0.0`, passed the isolated RAM-disk consumer trial through
  the public pinned maintenance CLI: ordinary install first returned
  `unowned-collision`; explicit project rebind to `team-context-translator`
  allowed framework installation; framework deselection removed its 2 runtime
  entries while all 9 project/custom/unknown files retained exact bytes.
  Both Codex and Claude entry files were included; this is filesystem/installer
  evidence, not native agent discovery or an account/model invocation.
- Trial harness inputs initially used an unsupported version and a library call
  outside the selected engine root. Both were correctly rejected before consumer
  installation. Corrected to supported local metadata and the actual pinned CLI;
  reused the built artifacts instead of rebuilding the catalog.
- Author inspection then reproduced a completed-plan replay defect: a detached
  old entry recreated with matching old bytes could be deleted again. Added a
  failing regression case, then changed completed replay to accept only matching
  after-state. Registry suite: 14 passed; model policy/portable CLI suite: 9 passed.
  The earlier 166-check result and trial remain scoped to their source revision;
  this repair changes completed replay only, not first application, installation
  or deselection. Independent affected review passed at
  `580dadc3910bef78ae916039023a8ed476228c8b`, with no supported actionable
  findings; the reviewer verified pre-publication resume and post-publication
  unchanged replay remain coherent.

## Accepted Claude verification scope

The owner accepts consistency with official Claude Code documentation as the
Claude verification criterion for this delivery. Model precedence, supported
per-invocation model/effort overrides and forced environment overrides were
checked against the [official subagent documentation](https://code.claude.com/docs/en/sub-agents).
This criterion is satisfied; a live Claude account test is not a prerequisite
for completing the current work.

The owner will perform live account tests separately in an appropriate team
environment. This private computer will not use a company account, and no login
or further Claude runtime validation is requested here. No live Claude invocation
or billing result is claimed.

Downstream native installation acceptance and savings measurement remain outside
this delivery. Hosted `Source change gate` remains required for a future
authorized PR.

## Final project readback

Packaged the engine from `580dadc3910bef78ae916039023a8ed476228c8b` and ran its
public `manage-sub-agents.py` in isolated Python from outside the source checkout.
`registry-inspect` reported 7 roles, 28 matched authoring/projection resources,
and no unknown native entries in this selected project. `route-resolve` returned
Sol/medium for the Codex fixed-head auditor and Haiku/no effort for Claude
translation. Both remain configured with availability/activation unknown and
invocation unobserved. No native model/account test was invoked.

Local implementation and the selected independent reviews are complete. The
final workflow record commit changes records only; implementation evidence stays
bound to the commits above. Issue #487 remains open; no push, PR, merge or
publication is performed. At that earlier boundary the source repo's installed lock and 17-skill
installation remained unchanged; the later directory transition is recorded below. Future self-installation must select the actual
released candidate and explicitly resolve any colliding project runtime names.


## Project directory transition

The owner selected `.ai/project` on 2026-10-23. Source implementation commit
`8424f92e42d523a9514bb4e9afccd37524934d26` passed 180 distribution/schema/loader
checks and supplies the pinned public CLI used for the actual migration.

An isolated consumer was first installed by the previous 26-file engine
`015c44e692f0500a4b58c34ed7ec55583e4a5602`. Its subsequent public layout migration
preserved all 7 managed members, configuration and selection bytes, provenance,
model preferences, unknown binary/native files and an empty directory. Its strict
installed-resource reader passed after relocation; completed replay was unchanged.
A subsequent actual deselection with an explicit canonical selection edit passed
and preserved the 9 selected project files. This is a bounded consumer trial,
not native agent activation or general skill-customization acceptance.

The actual source-project migration used the same pinned CLI and matched 7 roles
and all 28 registered authoring/native resources. The validated lock transition
changes only the executing engine pin and two relocated project-input paths;
candidate identity, selected packages, inventory and managed bytes remain intact.
Root guidance and project navigation now name the canonical directory.

Author compatibility inspection found a configured-skill wrapper regression:
current rendering initially changed old candidate guidance. The correction chooses
the convention from the artifact's admitted generator closure, preserving legacy
v1 and v2 outputs and producing canonical guidance for new artifacts. Regression
coverage uses the actual old Codex and Claude adr-author wrapper hashes, rejects
cross-convention contents even when inventory hashes match, and verifies the full
old installed-member projection. Installed skill entries are not hand-edited.

The source project's strict installed-resource index is not claimed current:
AGENTS.md and AGENTS.zh-TW.md already differed from their stored project-input
hashes before this continuation; the authorized navigation edit also changes
.ai/INDEX.MD. Their hashes were not silently rebound by the directory migrator.
Managed-member verification and registry readback are separate successful facts.
An explicitly selected future installation must reconcile current root authority
inputs through its normal protected-input planning. This limitation does not
occur in the clean isolated migration consumer described above.

128 distribution checks passed after the adapter correction; 10 loader checks passed with isolated Python. Earlier schema coverage remains applicable. The first combined invocation omitted -I and six loader checks correctly refused that host; only the loader suite was rerun, without a product-code change.

Staged Git bytes also match all 28 registered resources and preserve configuration,
selection and model-policy bytes across the rename.

The requested immutable Antigravity / Claude Opus 5.5 analysis is pending.
