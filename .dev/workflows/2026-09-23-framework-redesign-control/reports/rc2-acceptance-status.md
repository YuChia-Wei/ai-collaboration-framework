# RC.2 acceptance status

This coordinator projection follows the selected
[rc.2 scope](../../../design/framework-next/rc2-installation-selection.md).
It distinguishes work delivery from actual consumption and does not add a
mandatory approval, evidence tool or CI gate. Program #322 remains open.

## Current checkpoint

Issue #401 (S1) delivered exact contracts and the complete engineering-content
inventory; coordinator content review accepted correction 32a2b59d. PR #402
merged at 173b2523 and provider read-back confirmed #401 CLOSED / Project Done.
S2 #403 content delivery at f22674e2 and S4 #404 adapter delivery at ece36743
were integrated through PR #405 at 81c9603b. Fresh provider read-back confirmed
both Issues CLOSED / Project Done and #322 OPEN / In progress. The owner's
2026-09-24 execution amendment permits short bounded sub-agent work: S4 uses
that route; S2 retains a substantial independent task.
S3 Issue #406 has accepted local source delivery at 373c7250 after exact input
comparisons and two scoped static reviews. S5 consumer #407 is accepted locally
at b4dfe1cb. On 2026-09-29, source Issue #411 performed its first local RC2
installation from product commit `3908974fe3c1e2989253459cd3488d8c29da47f9`:
all 18 original-name skills, both adapters, zero engineering-knowledge packages,
selected project config, and lock SHA-256
`b9b74f03b3ce0e6940d738a22d148ab7167a6488ab3a68a9107512a9afae2a14` are installed.
API2 reported 151 additions, managed bytes consistent, and
`project_readiness: not-assessed`. This local lock does not settle product tag
creation or read-back. Runtime discovery/dogfood, behavioral acceptance, and S6
remain unperformed/deferred by owner. At this intermediate checkpoint, downstream
Issue #22 remained open pending coordinator synchronization; the final provider
read-back below records integration and closure.
After the source checkout advanced to product commit
`aad927328c20b08c8445e8ad1792eadd8ecc3466`, it completed a second official API2
apply from the final shared subset identity
`subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:49aa13e95517f00b14c3a53479a9275ce73f7cf74cf4c8ae43a3ace9ee7ac0ac`. The apply updated the project selection, kept all 149 managed members byte-identical, matched the protected framework config, and produced final lock SHA-256 `d2d69d0f6df72d35c258bdc7423b8168461b737c759eaf7ca9739086190e5368`. Runtime discovery/dogfood remains not performed; this local evidence makes no provider-state claim.
Source PR #412 integrated at source main `31fd8a02dcb22c9f4ddc6734d5b6ccab423211c5`; source checkpoint PR #413 was read back integrated at source main `26e18c178b74b2db5e10aa2a9443cd7aa58325b9`. The remote annotated tag `v0.19.0-rc.2` remains object `0f6118554f1573d835faf67aaa418dd291dd01d1`, peeling to product commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`. Issue #409 naming closeout is read back `CLOSED` (`completed`) at `2026-09-29T03:30:58Z` (comment: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/409#issuecomment-5883082732). Following direct user approval, the official MQ API2 rebind applied subset `subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:8e0eb8909b9a110b86398ed3f1a87d262b0691ddccdf63e7d49689a864556b71`; the new lock SHA-256 is `be0cba5c82425c1fc67755b65b7956c6333d8205f637f4cb3e48e6c45f907223`. API2 reports one selection change and 384 unchanged managed members; direct target raw hashes match the new lock, selection and corrected authority file. The selection contains 18 skills, two knowledge packages, both runtime adapters and 40 bindings. PR #24 merged at `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`; comparing `main` to this commit returned identical, and the clean primary checkout is on `main` at that SHA. Issue #22 is CLOSED/completed at `2026-09-29T05:52:26Z`; source #411 is CLOSED/completed at `2026-09-29T05:55:20Z`. The future admission gate #23 remains open; program #322 and #369 remain open. Project readiness remains `not-assessed`; runtime discovery/dogfood and S6/P7 remain deferred-by-owner.
The direct owner confirmation resolved the initial Issue-publication rejection.
A later proposed metadata comment was refused; the accepted public replacement
contains scope/progress only. New runtime task IDs, absolute worktree paths and
detailed execution provenance remain outside the published record.

## Observable completion

| Criterion | Delivery owner / input | Required observable result | Current evidence |
| --- | --- | --- | --- |
| RC2-C1 stable skill IDs and runtime names | S1 contract; S4 adapters | IDs retain identity under original names; both runtime entry sets and core are generated from the selected package; each runtime still needs separate observation. | Final source installation has 18 original-name entries in each adapter and a matching API2 lock; runtime discovery is not performed. |
| RC2-C2 project-owned selection | S1 formats; S3 distribution | Source and mq lab choose different explicit skills/knowledge/adapters from one verified immutable catalog; locks bind parent and subset; unselected managed bytes are absent. | Final source selection and lock bind the product commit and subset with 18 skills, 0 knowledge, and both adapters. Directly approved MQ API2 rebind selected 18 skills, two knowledge packages, both runtime adapters and 40 bindings; API2 reported the one project-selection change with 384 managed members unchanged. PR #24 merged at `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`, `main` matched that SHA, and Issue #22 closed. Project readiness remains `not-assessed`; no runtime behavior is claimed. |
| RC2-C3 usable engineering knowledge | S1 inventory; S2 content; S5 consumers | Every scoped active portable item has a destination or explicit disposition; applicable installed references are actually consumed without changing target rule semantics. | S1 inventory and S2 content are accepted, and S5 consumer delivery is integrated. Runtime consumption observation remains deferred with S6/P7; no runtime use is claimed. |
| RC2-C4 adapter selections and deselection | S3 maintenance; S4 adapters | Codex-only, Claude-only, both and core-only selections behave as specified; safe deselection preserves still-selected core and project-owned data. | Pending focused checks and selected runtime observations. |
| RC2-C5 rc.1 update and recovery | S3/S4 implementation; S5 target; S6 trial | Exact rc.1-to-rc.2 path covers renamed entries, ownership/drift/collision/dependency decisions and paired managed/project-owned recovery. | Pending actual trial against recorded candidate and engine identities. |
| RC2-C6 source self-adoption | S5 source; S6 observation | Source installs no engineering knowledge and exercises installed product in real source work; retained legacy/source duties are explicit. | Final installation has zero knowledge; source-owned compatibility/tooling duties are documented. Runtime dogfood and discovery remain not performed. |
| RC2-C7 truthful evidence and readiness | Coordinator; all owners | Implementation, local checks, actual target, each runtime and deferred outcomes remain separately attributable to their tested input. | Bounded mechanical source and target adoption is integrated, with provider closure read back for #411 and #22. Runtime/behavioral acceptance remains deferred-by-owner; no runtime or admission pass is claimed. |

S1 may provide exact schemas and proposed S6 cases. Its parsing/link/Git checks
are static evidence only. S6 must select affected checks after concrete
implementation, rather than infer success from this table or run a legacy
full matrix. No Cartesian all-skill/runtime matrix is implied.

## Residuals carried forward

| ID | Current disposition |
| --- | --- |
| R1 source self-adoption | Final source package is installed locally; runtime discovery/dogfood remains pending S6/P7. |
| R2 new-format publication/delivery | Fixed RC2 tag `v0.19.0-rc.2` was read back as object `0f6118554f1573d835faf67aaa418dd291dd01d1` targeting `aad927328c20b08c8445e8ad1792eadd8ecc3466`. GitHub Release and stable publication remain separate. |
| R3 stable-input update/recovery | Remains later stable work; rc.1-to-rc.2 does not substitute. |
| R4 cross-computer admission/recovery | Remains open; local receipts and recovery state are not automatically transported by Git. |
| R5 native/CI/policy and admission gaps | #369 native expansion and P7/CI restoration remain deferred-by-owner; future admission gate #23 remains open. Dormant policy adoption is unselected. |
| R6 runtime and lifecycle boundaries | Claude is selected for rc.2; other target decision adapters and retained lifecycle duties remain explicit. |
| R7 input-specific verification / C-001 | Preserve exact candidate/engine binding and existing uncertainty; no blanket stability claim. |
| R8 selectable installation and engineering knowledge | Source and MQ mechanical selections are integrated; actual S5 consumption and S6 acceptance remain deferred-by-owner. |

The fixed rc.1 tag/source, candidate digest, engine pin, target identity and
local-evidence limits remain in
[the rc.2 handoff](../handoffs/rc2-coordinator-transfer.json). Existing
security, credential, target ownership and publication boundaries remain.
U001 legacy/critical/formal/hosted checks are deferred-by-owner, responsible
owner program #322 coordinator/P7; later selection/adoption is separate.
