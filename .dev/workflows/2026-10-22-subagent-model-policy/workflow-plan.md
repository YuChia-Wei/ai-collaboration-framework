# Subagent model policy execution

Issue: [#487](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/487).
Base: `1d9a42c80a0f0db2d69dc36d335a090bfb071281`.

Owner approved local implementation and Issue creation on 2026-10-22: Luna
default, Sol by task, Astra separately authorized; verify equivalent Claude
selection and independent customization-preserving management. No push, merge,
release or publication. Parent is sole writer. Research children are read-only
Sol requests with `fork_turns=none`; no Astra child is authorized.

## Accepted scope and design

- New role policy v3 requires explicit task selection, model and effort; missing
  policy/availability never authorizes parent inheritance or escalation.
- Codex: Luna/Sol/Astra; Claude: Haiku/Sonnet/Opus. Premium is separately
  authorized. Provider-specific precedence and supported effort stay distinct.
- For this delivery, the owner accepts Claude configuration alignment with
  official documentation. Live account tests belong to the owner's later team
  environment testing and are not a completion prerequisite on this private host.
- Independently versioned project-owned `.ai/custom/sub-agent-policy.json` has
  a deterministic reader, preview/update writer and three-way comparison.
  Managed role bytes and framework lock do not own project model preferences.
- Management tool ships with the existing pinned engine, not a new installer.
  Existing exact engine closures remain readable for upgrade; execution pins
  remain strict. Native config changes are explicit project edits, not hidden
  installation writes. Unknown custom entries remain protected without registry.
- Apply #482/#484 ownership, resource provenance, baseline/local/candidate and
  explicit routing to sub-agents. Keep general skill customization outside this
  slice. Project authoring lives outside managed core; registry never grants
  installer ownership.
- Reusable cost/authorization rules feed back to the public AGENTS template;
  source GitHub governance and exact source-project models do not.

## Evidence and sequence

1. Official Codex and Claude docs plus current static inventory; completed.
2. Source policy/schema/profiles, portable manager and project settings; completed.
3. Focused checks and old-lock compatibility; 153 checks passed.
4. Immutable implementation commit and independent Sol review; no supported findings.
5. Public CLI readback and local-only delivery records; completed.

Claude references: https://code.claude.com/docs/en/sub-agents,
https://code.claude.com/docs/en/model-config and
https://code.claude.com/docs/en/settings. Per-invocation model precedence requires
2.1.251+; effort override 2.1.292+. Forced global model/effort can defeat routing.
Codex: https://learn.chatgpt.com/docs/agent-configuration/subagents; custom model
pins override spawn values. Current full-history forks cannot override models.

## Validation necessity

Behavior/schema/engine closure changes require focused deterministic tests for
legacy reads, v3 projection, policy resolution, unavailable/premium/conflicting
overrides, stale writes, paths and preserved custom data. Use bounded temp roots.
Do not run paid model matrices. Static tests do not prove actual invocation or
subscription debit. Installation/authority changes require immutable independent
review. Hosted gate remains for a future authorized PR; not run without push.

## Resource customization acceptance

Owner explicitly selected the earlier customization design for this subagent
work: distinguish user-created, user-modified and framework-integrated resources;
keep project authoring outside managed core; provide explicit routing when a
future framework role overlaps a local role. This extends #487 rather than
implementing the general skill Feature/Story #482/#484.

- Project resource provenance and exact package/reference closure have a real
  reader/writer under `.ai/custom/sub-agent-registry.json` and
  `.ai/custom/sub-agents/<project-id>/`.
- Existing 7 Codex and 1 Claude entries are explicitly adopted by preimage;
  preserve runtime names and permissions. Selected source-role snapshots and
  project profiles provide baseline evidence, not installer ownership.
- Runtime projections use project packages, with no framework checkout resource
  dependency. Existing obsolete `.ai/assets` and undeclared role_bindings
  references are reconciled inside the adopted project profiles.
- Upgrade comparison exposes old/local/candidate tree differences, unavailable
  base, declared capability overlap and registered/unknown path collisions.
- Explicit namespace rebinding or selected framework routing preserves custom
  authoring; only exact registered project runtime entries may be detached.
- Managed paths remain with the installer. Coverage/adoption references, file
  readback, native discovery and observed invocation remain distinct.
- Interrupted multi-file writes report partial progress, preserve the accepted
  plan and support explicit resume; stale external edits are never overwritten.

## Current status

Local delivery is complete. The model-policy slice is implemented at
`5d80f8cf939036d9a005a2af28496366937f5c6f`. The resource manager is implemented
at `fe0928e74b344c1a0208261ab764e6a0630cbbbc`; scoped fixes end at
`580dadc3910bef78ae916039023a8ed476228c8b`. Independent review findings are
resolved and affected re-reviews returned no supported actionable findings.
See [validation](validation.md) for exact subject and evidence boundaries.

The selected checks passed: 166 distribution/schema/loader tests, followed by
14 registry and 9 policy/public-CLI tests after the targeted replay repair.
An isolated actual-source public CLI trial proved collision refusal, explicit
namespace rebind, framework install and deselect while preserving all 9 selected
project/custom/unknown files. Final pinned public CLI readback matched 7 role
records, 20 authoring/reference files and 8 runtime projections in this repo.

Branch: `codex/2026-10-22-subagent-model-policy`. Runtime names remain unchanged;
future actual catalog selection determines which collisions need explicit
namespace rebinding or framework adoption. No automatic ownership takeover or
native activation is claimed.

## Continuation boundary

No authorized local implementation task remains. Push, PR, merge, publication,
Issue closure and Project mutation require their separately applicable authority.
A future PR needs actual current-head hosted Source change gate success. Keep
existing test evidence unless affected semantics or inputs justify repetition.

No live Claude tests or company-account login are requested. The owner accepts
official documentation alignment for this delivery and will test in the team
environment later. General skill customization under #482/#484 remains separate.
