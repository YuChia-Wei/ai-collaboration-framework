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
- Reuse #482/#484 ownership and baseline/local/candidate distinctions for this
  bounded model policy only. Do not implement or close general skill provenance.
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

## Current status

Authorized local implementation is complete at source commit
`5d80f8cf939036d9a005a2af28496366937f5c6f`; the subsequent record commit contains
only review/validation/closeout evidence. See [validation](validation.md).
Branch: `codex/2026-10-22-subagent-model-policy`; base remains the SHA above.
Issue #487 was read back open after implementation. #482/#484 remain
reference-only open design work. No push, merge, publication, runtime acceptance
or savings measurement is claimed.

## Continuation boundary

No local implementation task remains. The owner may separately authorize a PR
and push; then inspect this branch and current provider state, retain the existing
product checks unless the diff changes, and obtain actual hosted Source change
gate success before integration. Do not close #487 or change Project state
without the separately required authority and integration evidence.

Claude documentation alignment is accepted. No further local Claude validation
or company-account login is requested; the owner will conduct live account tests
separately in the team environment. New checkouts must explicitly merge native
settings proposals because this source project's `.codex/config.toml` remains
ignored/local. General skill customization
under #482/#484 and downstream native acceptance remain outside this delivery.
