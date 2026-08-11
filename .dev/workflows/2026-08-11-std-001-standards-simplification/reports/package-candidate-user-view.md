# Package Candidate User-View Baseline

## Build Identity And Limitation

The first exact v0.13 attempt was intentionally fail-closed:

```text
python .ai/scripts/build-ai-context-package.py --ref df7012b6... --version v0.13.0 ...
AI context package build failed: missing required Git-tree file: .dev/releases/v0.13.0/release.yaml
```

No v0.13 release record was invented because #61 does not authorize release-candidate truth, tag, or publication. To inspect the exact current payload bytes, a controlled projection used the existing v0.12.0 release contract plus the verified published v0.11.0 `metadata/files.yaml`, while pinning source ref to `df7012b6bf6ac360cfb47e2c79813384880665f8`.

- downloaded v0.11.0 ZIP SHA-256: `cd7010f65941cccfa2151ded2e0d7b3ef27f7a9d0bb3c5772a5b5c9855a0a10c` (matches the hosted asset digest);
- generated ZIP and tar.gz both passed `validate-ai-context-package.py`;
- metadata source commit: `df7012b6bf6ac360cfb47e2c79813384880665f8`;
- payload: 624 files, 2,729,493 bytes;
- limitation: the envelope says v0.12.0 and is not a releasable v0.13 candidate. It is evidence only for current-tree payload selection, navigation, and bytes.

## Component Inventory

| Component | Files | Bytes |
| --- | ---: | ---: |
| `software-development-core` | 340 | 1,497,071 |
| `ai-context-lifecycle-core` | 110 | 716,756 |
| `dotnet-backend` | 172 | 511,954 |
| `repo-backlog` | 2 | 3,712 |

The archive inventory contains all declared components; clean-install defaults enable both mandatory cores and the `dotnet-backend` profile while leaving `repo-backlog` disabled.

## Code Review User Journey

Strengths:

1. Both runtime registries list `code-reviewer`.
2. The Codex/Claude wrappers, canonical skill, top-level references, four review roles, shared references, and granular .NET standards are present.
3. Every explicit Code Reviewer reference resolves inside the default dotnet-backend payload.
4. `code-review.sh` is labeled compatibility/advisory in the scripts registry rather than semantic authority.

Observed friction:

- the routing/role subset contains 23 files and 74,798 bytes;
- a broader review-support corpus including granular standards, the assessment policy, template, and compatibility shell contains 34 files and 185,099 bytes;
- 20 routing/role/compatibility files (54,943 bytes) are classified as `software-development-core`, while the three central .NET checklist/index files (19,855 bytes) are `dotnet-backend`;
- the canonical skill is explicitly .NET-specific, so this component split makes the metadata claim that the entry is core even though its mandatory references require the optional profile component.

The current default package happens to select the dotnet profile, so the path resolves. The component graph is nevertheless incomplete for reuse, selective migration, or a future profile combination.

## Governance And Release User Journey

`INSTALL.md` correctly says the package is not a whole-repository overwrite and that source-only release publication is not part of target installation. The payload then exposes contradictory navigation:

- `.dev/standards/AI-CONTEXT-VERSION-POLICY.md` tells a target user to create `.dev/releases/<version>/`, use source release records, run publication gates, and reconcile source Issue/Project state;
- `.dev/releases/**`, release-publication templates, the release validator, the publication runbook, and the closeout skill/guide are intentionally excluded;
- `.ai/scripts/README.md` lists and explains the excluded release validator;
- `.dev/operations/RUNBOOK-GUIDE.MD` and `.dev/operations/runbooks/README.MD` link to the excluded publication runbook;
- the human guide index names the excluded closeout guide.

A filtered Markdown-link scan checked 204 local links and found seven genuine missing targets across five payload files after excluding six code-example false positives:

1. two links to the excluded release publication runbook;
2. three links from the requirement guide to excluded source requirement instances;
3. one spec-guide link to an excluded source standard path;
4. one Reactor-standard link to excluded source architecture truth.

The generated ZIP/tar validation still passed. Current package validation therefore proves archive parity and declared metadata, but not that downstream navigation is complete after source-only exclusions.

## Required After Evidence

The real v0.13 candidate review must repeat this user journey after a governed v0.13 record exists and prove:

- no active Markdown link resolves to an excluded/missing payload target;
- no portable guide instructs a downstream user to invoke a source-only release command or create source release records;
- Code Reviewer component identity and all mandatory references are closed under the selected component set;
- entry-to-file-type routing loads only applicable standards and produces the same rule/severity/output contract matrix;
- ZIP and tar.gz remain deterministic and parity-valid.

## Finding Handoff

- `ASM-20260811-003#PKG-001`: a validated archive can still contain broken navigation and actionable source-only release doctrine.
- `ASM-20260811-003#CMP-001`: the .NET Code Reviewer entry is split across core and dotnet component identities.

## Controlled After Evidence

Issue #193 implementation `ff80d590006ebec8ccfbd540abb4083a9d386613` was evaluated as a fixed local subject by `ASM-20260811-006`. This remains controlled after-evidence rather than a governed v0.13 candidate.

- The selected projection contains 628 files: software-development core 322, AI-context lifecycle core 110, dotnet-backend 194, and repo-backlog 2.
- One schema 2.2 user-view contract now runs during package build and archive validation. It fails closed on broken local links and anchors, unavailable actionable commands, excluded lifecycle references, and incomplete component/capability selections.
- All 22 Code Reviewer capability paths are owned by `dotnet-backend`; core-only declares Code Reviewer unavailable and dotnet-selected declares it available.
- ZIP/tar inventory and user-view parity, versioned apply, routing, and the aggregate fast profile passed. Environment blocks, the initial WSL timeout, and the fast-profile duration advisory remain explicit receipts rather than rewritten passes.
- `PKG-001` and `CMP-001` are addressed locally. A real governed v0.13 candidate must repeat the same contract against its immutable previous-release source and obtain downstream owner/provider read-back.
- Active upgrade testing now begins at v0.6.0. Each later governed version has exactly one immediate-predecessor automatic route, and every breaking release establishes a predecessor-only checkpoint; the older broad matrix is retained only as non-discoverable history.
