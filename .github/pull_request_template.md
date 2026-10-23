<!-- Source policy adopted by the owner on 2026-10-02:
.dev/standards/SOURCE-DEVELOPMENT-POLICY.md. Checks and integration remain separately verified. -->

## Change

Describe the problem, resulting behavior and bounded scope. Follow
[the public content boundary](../.dev/standards/PUBLIC-REQUIREMENT-CONTENT-POLICY.md)
for the description, comments and review discussions. Keep execution authorization,
agent handoff and continuation instructions in the workflow mechanism.

## Validation

List exact commands, source commit and actual outcomes. Retain failed attempts,
limitations and deferred checks. Link current-head Source change gate for PRs
changing `src/**` or `tools/**`; otherwise state that source CI is not applicable.
Local/static/fixture results do not establish hosted or native acceptance.

## Review

Summarize technical review results and coverage limits. For authority, security,
credential, publication, installation or recovery changes, also record the
independent reviewer, immutable commit, criteria, findings and disposition.
Include selected native/release evidence only when applicable. Missing validation
or unresolved defects remain visible even when Source change gate passes.

## Issue disposition

Link related requirements and summarize delivered, remaining or deferred product
scope. Use closing keywords only for the selected final delivery; otherwise use
`Refs` with actual product status and any remaining limitation or dependency. Keep closure authority,
integration decisions and execution checkpoints in the workflow, not this body.
