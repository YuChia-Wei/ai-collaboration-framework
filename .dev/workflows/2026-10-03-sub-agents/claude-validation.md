# Claude extension validation

Created/updated: `2026-10-03T08:56:55+08:00`. Immutable source:
`51a939c5b1de1ca32b7c46a130f29532a4424ff6`; combined diff base `37a588c8c0b6f5e760079c563e71d742af8f962d`.
Owning workflow/Issue: `2026-10-03-sub-agents` / #434.

The owner's follow-up explicitly selected all six Claude roles. Existing Codex
selection is retained; `sub-agents-claude@0.1.0` selects Claude only. Manual v3
selection may choose `claude` or sorted `claude, codex`. Five analyzers declare
only Read/Grep/Glob and inherit; translator retains Haiku and Read/Write/Edit.
Mandatory unavailable command/preflight tooling stops and returns to the parent.

## Exact-head checks

`python -I -B .github/scripts/check-source-change.py --base 37a588c8c0b6f5e760079c563e71d742af8f962d --head 51a939c5b1de1ca32b7c46a130f29532a4424ff6`
passed in 55.803 seconds: schemas43, distribution46,
source49, platform26; total164, zero errors/failures/skips, content/whitespace
passed. Raw result: `artifacts/sub-agents-claude-corrected-source-gate.json`.
The previous head also passed its tests/installation but independent review
rejected missing exact model enforcement. The LF-only parser failure and model
review finding/repair remain in the plan; neither is relabeled as passed.

## Real assembly/install scenario

One isolated source-read-only external CLI task ran:
`python -I -B artifacts/verify-claude-corrected-delivery.py`.
Duration: 111.653939 seconds. Start:
`2026-10-03T08:53:13+08:00`; completion: `2026-10-03T08:55:04+08:00`.
Its schema-valid terminal record binds exact source, command, content subject
`df03154df6b5f3f0978aac1f3d91379cffa174c565916510f85680a59cc42a7f`, timings, outcome/exit0, evidence and clean
tracked state before/after. Inline terminal schema is retained with raw logs.
No tracked repair occurred during the task.

All24 Engine2 files independently matched committed bytes/hashes. Real
`tools/build-catalog.py` assembled this immutable source with the independent
engine pin. Artifact version0.0.0 is a verification-only label, not release
allocation. Catalog identity: `catalog:1:0.0.0:51a939c5b1de1ca32b7c46a130f29532a4424ff6:a86c6772dfc7009233e1cb2843f4f720314c9f7ca84348bc0784aa660f8ad7d2`.
The standalone engine's real `tools/derive-subset.py` derived the Claude preset
without source-repository input. Subset identity: `subset:3:0.0.0:51a939c5b1de1ca32b7c46a130f29532a4424ff6:594521ef47e2eba4f9234cbef1e432622db41cca83ea2fe486d51c2cd0a0b992`.
All36 subset hashes matched: 30 canonical package files and six Claude profiles.

Actual plan/apply and inspect passed on new isolated target
`C:\Windows\Temp\c434-6_f4drch` / `p`. All36 installed hashes matched;
state `managed-bytes-consistent`. Existing `.claude/settings.json` and
`.claude/agents/custom.md` remained byte-identical. A managed profile modification
was detected as drift; restoration returned consistency. A same-byte unowned
profile collision refused planning and preserved the existing profile.
Raw terminal, assembly and installation reports:
`artifacts/claude-sub-agents-corrected-terminal.json`,
`artifacts/claude-sub-agents-corrected-physical-result.json`,
`artifacts/claude-sub-agents-corrected-installation-result.json`;
CLI/API requests/stdout/stderr/schema/pin are in
`artifacts/claude-sub-agents-corrected-physical/`. Original fcaf7aa7 artifacts
remain separately retained. Temporary scenario directories remain retained by
selection; no global TEMP/TMP or acceleration configuration changed.

## Review and remaining ownership

The authorized independent reviewer accepted the corrected scope; details and
retained rejected attempts are in `review.md`. This is configuration, physical
delivery and scoped review evidence, not actual Claude invocation/model access,
native runtime behavior, recovery, full P7, downstream adoption, hosted CI or
publication. The source gate still reports admission not-evaluated and an
owner-selected native requirement. Main integration and #434 closure need their
separate owner/provider evidence; no push/PR/merge/tag/release or cleanup ran.
The final record-only commit gets fresh source checks and administrative review
binding before local handoff, without rebuilding unchanged reviewed products.
