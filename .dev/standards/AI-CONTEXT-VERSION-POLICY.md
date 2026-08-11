# AI Context Version Policy

This source-repository compatibility entry is not the downstream policy bytes.
It preserves the stable source path while routing each authority to exactly one
owner:

- Source framework version candidates, release-source status, tag handoff,
  hosted publication, publication/finalization validation phases, and
  historical exception closeout are owned by
  [AI Context Source Release Policy](AI-CONTEXT-SOURCE-RELEASE-POLICY.md).
- Installed framework version identity, target provenance, and upgrade safety
  are owned by the portable
  [AI Context Version Policy projection](../../.ai/assets/shared/governance/AI-CONTEXT-VERSION-POLICY.md).

The distribution profile excludes this source compatibility entry and maps the
portable projection back to `.dev/standards/AI-CONTEXT-VERSION-POLICY.md` in a
target package. Do not copy source-release procedure into the portable
projection and do not infer source release authority from the stable target
path.
