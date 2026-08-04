# Sub-Agent Reachability Follow-Up Notes

- `status`: `deferred-separate-issue-discussion`
- `source_workflow`: `2026-07-30-ai-context-architecture-kit-standards-discussion`
- `recorded_at`: `2026-08-02T17:09:26+08:00`
- `updated_at`: `2026-08-02T20:22:21+08:00`
- `external_provider_adoption`: `not-planned`

## Boundary Decision

Sub-agent runtime reachability is not part of the main AI Context rule-architecture and Architecture Kit issue. Preserve these observations for a separate future discussion; do not create that issue yet and do not introduce `kevintsengtw/dotnet-testing-agent-orchestration-codex`.

## Existing Related Issue

- <https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/58> (`SAG-001`) is closed as completed for v0.5.0.
- It established dynamic canonical loading as the default for seventeen roles and runtime-native promotion only for `context-translator`.
- The observations below are a post-contract operational-reachability question, not a request to repeat adapter promotion/parity design.

## Possible Problems To Revisit

1. `.ai/SUB-AGENT-SYSTEM.MD` declares role ownership, but it is not an executable dispatcher. A manifest marked `active` may never be loaded when its owning skill does not cite it.
2. `slice-implementer` command, query, and reactor modes load their role manifests as mandatory references, but do not distinguish inline application from actual delegated execution.
3. Aggregate, controller, outbox, and profile-config roles are mapped to `slice-implementer` without matching explicit execution modes.
4. `problem-frame-author`, `bdd-gwt-test-designer`, and `code-reviewer` do not currently cite their mapped role manifests in canonical specs or runtime wrappers.
5. `bdd-gwt-test-designer` stops before final test implementation, while its mapped test roles implement concrete tests. The top-level owner for that transition is unclear.
6. `software-development-orchestrator` can pass handoff packets but does not map the canonical role inventory or record whether execution was direct, delegated, or unavailable.
7. `AICDISC-ADAPTER-001`: The downstream target lacks `.codex/agents/context-translator.toml` even though its canonical manifest declares that adapter. The source package includes the file, but the target-retained `.gitignore` omits the `!/.codex/agents/**` exception. `validate-ai-context.py` and the cross-machine critical gate fail with the missing adapter path.
8. Current structural validation can detect the missing adapter after installation, but the install/upgrade reconciliation path did not prevent or clearly surface the ignored framework-managed path before the downstream state was finalized.

## Future Decision Questions

1. Must every owning skill evaluate each mapped role and report one disposition: `direct`, `delegated`, or `unavailable`?
2. Which task-size, isolation, cost, permission, and runtime-capability conditions justify delegation rather than inline execution?
3. Does the framework need deterministic reachability validation from owning skill to role manifest, in addition to manifest and adapter parity?
4. Which top-level capability owns test implementation after `bdd-gwt-test-designer` finishes scenario design?
5. Should target install/upgrade detect a framework-managed runtime adapter that is excluded by target `.gitignore` and stop, reconcile, or create an explicit pending item?
6. What acceptance evidence demonstrates that a dynamic role was actually invokable without making runtime-native adapters mandatory for all roles?

## Retention

Keep these notes on the dedicated downstream discussion branch, which the owner has pushed for cross-machine continuation. Do not merge, copy upstream, or create a dedicated issue until the owner separately authorizes that action.
