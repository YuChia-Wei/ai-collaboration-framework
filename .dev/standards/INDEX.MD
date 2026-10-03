# Source Governance Standards Index

These are this framework source project's policies. Reusable engineering
knowledge lives in `src/knowledge`, product manuals in `docs`, and generated
installed content in `.ai/core`. Load only the applicable policy.

## Ordinary Source Work

- [Source development policy](SOURCE-DEVELOPMENT-POLICY.md): adopted eight rules,
  affected checks and conditional independent review.
- [Context boundary](AI-CONTEXT-BOUNDARY.md), [language](AI-CONTEXT-LANGUAGE-POLICY.md)
  and [source ownership](AI-CONTEXT-OWNERSHIP.md).
- [Source work authority](SOURCE-WORK-MANAGEMENT-AUTHORITY.md) and its
  [configuration](SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml).
- [GitHub work management](GITHUB-WORK-MANAGEMENT-POLICY.yaml) and
  [Issue closure](GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md).
- [Git commit policy](GIT-COMMIT-POLICY.md) and [configuration](GIT-COMMIT-POLICY.yaml).
- [Assessment records](ASSESSMENT-ARTIFACT-POLICY.md),
  [workflow locator](WORKFLOW-ARTIFACT-POLICY.md),
  [workflow selection](WORKFLOW-GATE-POLICY.md) and
  [handoff](WORKFLOW-HANDOFF-POLICY.md)/[configuration](WORKFLOW-HANDOFF-POLICY.yaml).
- [Effective source rules](AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml).

## Selected Legacy And Release Duties

- [Source release policy](AI-CONTEXT-SOURCE-RELEASE-POLICY.md).
- [Temporary redesign/U001 override](FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md),
  only for explicitly retained obligations outside adopted ordinary source scope.
- [Legacy identity registry](AI-CONTEXT-OWNERSHIP.yaml) and
  [legacy effective-rule evidence schema](AI-CONTEXT-SOURCE-EFFECTIVE-RULE-EVIDENCE.schema.yaml),
  for interpreting compatible records; they are not current product configuration.

See [contracts](../contracts/README.md) for source execution boundaries. Removed
compatibility notices and obsolete commands are not current navigation; retrieve
an explicitly selected historical revision when needed.
