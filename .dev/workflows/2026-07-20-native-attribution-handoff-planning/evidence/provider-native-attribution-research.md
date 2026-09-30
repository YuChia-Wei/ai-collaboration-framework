# Provider-Native Attribution Research

## Scope And Evidence Date

- Research date: `2026-07-20`
- Repository base: `b3eb2af31fbeffe773967ca805fd78600901c03b`
- Purpose: bound HANDOFF-001 without changing provider settings, commit
  policy, validator behavior, or existing Git history.

## Confirmed Current Codex Runtime

The active Codex session exposed the following machine-readable request
metadata:

```yaml
runtime: "OpenAI Codex"
model: "gpt-5.6-sol"
reasoning_effort: "xhigh"
model_source: "runtime-reported"
```

The user's UI labels were `GPT 5.6 sol` and `極高`. They agree with the
runtime-reported values in this session, so no user-declared fallback is needed.
If runtime metadata is unavailable in a future session, preserve the user's
verbatim label with `model_source: user-declared`; do not relabel it as
runtime-reported.

## GitHub Copilot Contracts

GitHub's current official documentation establishes two different attribution
shapes:

1. Copilot CLI has `includeCoAuthoredBy: true` as its built-in default.
   `.github/copilot/settings.json` can replace that value for the repository.
2. Copilot cloud-agent commits are authored by Copilot, list the initiating
   human as co-author, are signed and shown as verified, and include a link to
   session logs.

Sources:

- <https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/copilot-cli-reference/cli-config-dir-reference>
- <https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/copilot-on-github/use-copilot-agents/manage-and-track-agents>

Consequences:

- Do not add a repository `includeCoAuthoredBy` override merely to normalize
  commit messages.
- Do not amend a signed Copilot cloud-agent commit merely to add an AI
  co-author trailer; rewriting would replace the provider-native evidence.
- The future validator must accept provider-native authorship/signature/session
  evidence and local AI co-author trailers as compatible alternatives.

## Claude Evidence Boundary

The official Claude Code documentation reviewed on `2026-07-20` documents Git
automation and explicit model selection, but the search did not establish a
stable native commit-attribution contract:

- <https://docs.anthropic.com/en/docs/claude-code/cli-usage>
- <https://docs.anthropic.com/en/docs/claude-code/common-tasks>

HANDOFF-001 must therefore use a real Claude-created commit captured verbatim
as a golden fixture before encoding or validating Claude-specific authorship,
committer, trailer, email, or signature expectations. Lack of documentation is
not permission to invent a Claude identity.

## Current Repository Compatibility Gap

`.dev/standards/GIT-COMMIT-POLICY.md`,
`.dev/standards/GIT-COMMIT-POLICY.yaml`, and
`tools/maintenance/validate-git-commits.py` currently require the final non-empty line
of every selected AI-assisted commit to be a valid AI `Co-Authored-By` trailer.
That is compatible with one local co-author shape, but it cannot represent the
documented Copilot cloud-agent shape without rewriting the native commit.

This planning workflow does not change that behavior. It records the gap as a
v0.5.0 HANDOFF-001 release-blocker requirement.

## Required Golden Fixtures

Before implementing the policy or validator change, capture provider-generated
commit objects without normalization:

| Fixture | Required evidence | Preservation assertion |
| --- | --- | --- |
| Copilot CLI | author, committer, complete message and trailers | native co-author trailer remains byte-for-byte unchanged |
| Copilot cloud agent | author, human co-author, signature status, session link | no amend, signature loss, or identity reversal |
| Claude | author, committer, complete message, trailers and signature status when present | observed native form passes without guessed provider fields |
| Codex local | author, committer, native or repository-created trailer plus runtime provenance | attribution and model-source claims remain distinct |

Regression tests must also prove that the validator is read-only and does not
invoke `git commit`, `git commit --amend`, rebase, or another history-writing
operation.
