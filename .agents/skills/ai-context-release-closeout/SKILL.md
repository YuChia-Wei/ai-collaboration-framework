---
name: ai-context-release-closeout
description: Verify historical post-tag records or explicitly authorized exception recovery without altering a release tag or making source closeout a normal release step.
---

# AI Context Release Closeout

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/ai-context-release-closeout/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-CONTEXT-RELEASE-CLOSEOUT-SKILL-GUIDE.md`
- References:
  - `.dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md`
  - `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`
  - `.dev/standards/GIT-COMMIT-POLICY.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Run it only after a tag and hosted publication exist and normal automation cannot represent a historical or explicitly authorized exception. It is not a normal `v0.12.0`-or-later stage. Do not create, move, or recreate a tag; do not prepare a candidate or rerun package migrations or .NET tests. If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-release-closeout/skill.yaml`.
