# Provider Attribution Fixture Status

Observed at: 2026-07-27

## Captured repository-created Codex fixture

- Path: `codex-local`
- Status: `captured`
- Commit: `5af1ec40d6dc4b736d4f8af0e06c397cbcca77fa`
- Author and committer: `YuChia <h42279@gmail.com>`
- Signature status: unsigned
- Trailer: `Co-Authored-By: OpenAI Codex (gpt-5.6-sol, medium) <noreply@openai.com>`
- Classification: repository-created local AI trailer
- Provenance source: effective configured defaults under AEP-DEC-002, not a
  runtime-confirmed session report

This commit proves the repository-created path and the common trailer shape.
It does not prove that the Codex client injects the trailer natively.

## Provider-native fixture matrix

| Path | Status | Current official capability | Missing evidence |
| --- | --- | --- | --- |
| `codex-local` native injection | `blocked` | Codex documents model and reasoning configuration plus session/config inspection. | No documented native commit-attribution setting and no Codex-injected commit object. |
| `claude` | `blocked` | Claude Code documents default/customizable commit attribution, active-model trailer output, and model/effort controls. | No Claude-generated commit object in this repository; dynamic effort interpolation in a custom trailer is not documented. |
| `copilot-cli` | `blocked` | Copilot CLI documents `includeCoAuthoredBy`, `model`, and `effortLevel`. | No Copilot CLI-generated commit object in this repository; the documented trailer contract does not include effort. |
| `copilot-cloud-agent` | `blocked` | GitHub coding agent has a separate provider-managed commit/PR surface. | No provider-generated, signed or attributed commit object captured in this repository. |

Desktop chat and IDE chat are not promoted to captured Git fixtures merely
because they can discuss or edit a repository. A fixture requires an actual
provider-generated commit object with its original metadata preserved.

## Official evidence

- Codex configuration: <https://developers.openai.com/codex/config-basic>
- Codex slash commands: <https://developers.openai.com/codex/cli/slash-commands>
- Claude Code settings and attribution: <https://code.claude.com/docs/en/settings>
- Claude Code model and effort: <https://code.claude.com/docs/en/model-config>
- Copilot CLI configuration: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference>

The provider documentation establishes supported settings and native behavior.
It does not substitute for a golden commit fixture, so unavailable provider
paths remain explicitly blocked instead of being synthesized.
