<!-- Source policy adopted by the owner on 2026-10-02:
.dev/standards/SOURCE-DEVELOPMENT-POLICY.md. Checks and integration remain separately verified. -->

## Change and authority

Describe the problem, resulting behavior, bounded scope and owner authorization.

## Validation

List exact commands, source commit and actual outcomes. Retain failed attempts,
limitations and deferred checks. Link current-head Source change gate when run.
Local/static/fixture results do not establish hosted or native acceptance.

## Review and admission

Record author diff inspection and maintainer acceptance. For authority, security,
credential, publication, installation or recovery changes, also record the
independent reviewer, immutable commit, criteria, findings and disposition.
Include selected native/release evidence only when applicable; unresolved
admission requirements remain explicit even when Source change gate passes.

## Issue disposition

For each Issue, state final delivery with an approved closing keyword, or `Refs`
with the deferred reason and next owner/gate. Closing intent never authorizes work.
Issue closure and Project state are separately read back after integration.

## Integration

State the selected topology and its reason, execution record (direct/workflow),
and any remaining owner decision. No release, downstream installation or branch
deletion follows implicitly from merging this PR.
