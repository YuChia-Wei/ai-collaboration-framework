---
name: ai-context-release-closeout
description: Plan and verify source-only, post-tag AI context release closeout without altering a release tag or downstream package.
---

# AI Context Release Closeout

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/ai-context-release-closeout/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-CONTEXT-RELEASE-CLOSEOUT-SKILL-GUIDE.md`
- References:
  - `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`
  - `.dev/standards/GIT-COMMIT-POLICY.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Run it only after a tag and hosted publication exist. Do not create, move, or recreate a tag; do not prepare a candidate or rerun package migrations or .NET tests. If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-release-closeout/skill.yaml`.
