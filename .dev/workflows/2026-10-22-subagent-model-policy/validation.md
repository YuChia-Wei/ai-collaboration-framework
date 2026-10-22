# Local implementation evidence

Scope: Issue #487, local source and project settings. No push, PR, merge,
release, publication, Issue closure or paid model matrix was performed.

## Executed checks

- `python -I -B tests/run.py --suite distribution --suite schemas --suite loader`:
  153 tests, 0 failures, 0 errors, 0 skipped (2026-10-22, Windows, 14.41 seconds).
  The earlier run exposed an unsynchronized inline schema definition and stale
  Claude inheritance text; both were corrected. The added legacy-v2 fixture
  initially used fields absent from the original schema; it was corrected to
  the actual v2 contract before the final passing run.
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

## Limits and pending evidence

Independent review is pending on a fixed local commit. Provider configuration,
CLI version, available model listings and selected call arguments do not prove
the executed provider identity or billing. No paid Claude run, downstream native
installation acceptance, savings measurement or hosted CI pass is claimed.
`claude --version` reports 2.1.239 on this host, below the documented invocation
model/effort override requirements (2.1.251 / 2.1.292). Haiku defaults are
configured; task-specific Claude invocation using these overrides is unavailable
on this installed version and must stop. No CLI upgrade was selected or performed.
Hosted `Source change gate` remains required for a future authorized PR.
