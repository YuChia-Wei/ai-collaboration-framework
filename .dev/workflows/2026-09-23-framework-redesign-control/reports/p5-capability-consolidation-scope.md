# P5 capability and schema disposition design

Program #322 / Issue #342. This is a bounded design/inventory assignment under U001, preparing separately owned implementation slices. It runs independently of #341 workflow design and #337 mapping, owns no product or shared-file edits, and does not adopt its proposed dispositions automatically.

## Current-source observations

At integration checkpoint 2bd7acdaf8a580df965396bdb9dbb8c05f6308af, direct Git inventory and YAML reads establish 16 top-level .ai/assets/skills/*/skill.yaml entries. Five are AI-context maintenance/release routes, one is the organizational orchestrator already assigned to #341, and ten are specialist reasoning, design, authoring, implementation or compliance capabilities. Preserve their useful methods while explicitly removing hidden source-project dependencies.

The legacy artifact-lifecycle-registry.json has 95 kind rows: applicability portable=60, source=34, dotnet-backend-profile=1. Authoring labels are executable=61, semantic-owner=20, manual-gap=9, external=4, creation-template=1. These are inventory labels, not executed tooling coverage, independent schema files, or commitments to preserve all formats. Filename search alone is incomplete because some formats are defined in Markdown or Python; use each exact kind/model/owner as the coverage basis and add the new src-owned formats.

Graph navigation located distribution.package.load_package. The current source requires nonempty operations, each with implementation_status=implemented and a string tool mapped to a declared implemented executable. The package.py Git blob is unchanged between loader integration 879b195160540f74bab2ac57cad148bcfaddbcbe and the selected current subject: ffb0d580021d2c8bd33bd4aa0dbb804b5f81b135. The graph range metadata predates inserted lines and is navigation only; the returned current source plus exact Git blob are the evidence. This tool-centric contract is sufficient for P3, but cannot honestly describe a reasoning-only review operation without a contract decision. P5 must propose the smallest versioned representation instead of a dummy executable.

## Owned result

Own only .dev/design/framework-next/capability-consolidation/ and .dev/workflows/2026-09-23-capability-consolidation/. Produce exact per-skill and per-kind coverage with grouped recommendations, dependencies, output/store ownership and version/reader/writer/validator/migration dispositions. Include current package metadata/config/manifest/profile/build-output formats that the legacy registry does not list. Explain optional context-maintenance selection, source-only release/history separation and P6 installation/update ownership.

Give concrete minimal examples for an instruction-driven reasoning skill and a schema-owned authoring skill, proposed metadata evolution preserving v1/v2, exact expected members/references, and small implementation work packages. Preserve specialist capability rather than replacing it with mandatory ceremony. A plain prose output need not acquire a machine schema merely for inventory symmetry; an actually retained machine format needs an accountable tool owner. Historical records may explicitly remain preserved/unsupported. Identify one necessary exact-version migration candidate and its future owner without implementing it.

No src, legacy policy/skill/script, manifest/profile, root/runtime/core/custom, test, CI or shared-index edits. No mass move, deletion, global runtime registry, fake receipts, product trial or rewritten compatibility claims. #316/#320/#149/#168/#274/#275 remain separate unless explicitly reconciled later. P4/P6/P7 retain their owners and sequence. Report proposals to the coordinator; source implementation is assigned only after selection.

Use one independent gpt-6-astra / ultra task at F:/framework-next/342, no sub-agents or child-created tasks. Direct data/syntax/reference/Git and exact message-format checks only. Product CLI/help, schema validators, tests/fixtures/build/install/migration/audit/CI remain deferred-by-owner under U001 to program #322/P7.
