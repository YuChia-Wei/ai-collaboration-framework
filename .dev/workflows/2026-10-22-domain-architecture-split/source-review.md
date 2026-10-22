# Independent implementation review and disposition

## Fixed subjects and independence

- Reviewer: `/root/split_design_review`, bounded-general-worker, owning method
  `code-reviewer`; no tracked writes, repairs, test runs or provider mutations.
- Author and integration owner: `/root`. Reviewer did not author the source subject.
- Original subject: `51865868a50233d734f1140c7e11ce8fe80cd21d`.
- Base: `9b44783d5d0c2caa5dddbcf78f86073628ed8b7d`.
- Bounded correction: `589abfcd97d8e145d8d9930814904b17bc05f2c7`.
- Classification: independent read-only source/contract review. This is not a
  runtime/model invocation, installation, hosted CI or release acceptance result.

The review covered the accepted design, both new packages, directly affected
neighbor methods/metadata, common selectors/routing, .NET dependency, manifest,
four presets, regression tests, manuals, migration and bilingual root navigation.
New-test graph search and index status did not establish extraction freshness or
complete symbol coverage. The reviewer explicitly read fixed Git blobs for the
new tests and directly relevant resolver/helpers; absence in the graph was not
used as evidence of absence in source.

## Findings

| ID | Finding on the original fixed subject | Author disposition |
| --- | --- | --- |
| F1, P2 | `src/skills/spec-author/references/spec-guide.md:15–16,42–43` still denied optional method consumption and assigned all scenario/assertion/test design to test-designer. The guide is a packaged SKILL.md link, so a caller could receive instructions contrary to new metadata, knowledge.md and authoring.md. This affects GWT spec examples and requested optional methods. | Corrected only the two obsolete instructions in commit 589abfcd: use the existing verified knowledge protocol; distinguish observable contract examples from formal tests, fixtures, oracles and assertions; preserve no source fallback. Independent reviewer verified F1 resolved at 589abfcd against authoring.md, knowledge.md and metadata; no new contradictory routing was found. |

No other actionable new defect was found in the selected scope. The historical
responsibility guide's current navigation was separately updated to remove its
stale “not implemented” wording and link real execution records. Its historical
tables were preserved. Design entry status now links design review and workflow
records; neither navigation correction changes the accepted source contract.

## Criterion and scenario coverage

The following is static instruction/contract coverage, not proof that an arbitrary
model invocation will follow the instructions correctly.

| Criterion | Reviewed behavior and disposition |
| --- | --- |
| A-AC-01 | Pure cancellation-domain work preserves language, rules, state and invariant ownership without choosing DB, broker, CA or runner. |
| A-AC-02 | Existing-model payment API isolation can directly enter software design with ports, adapters and failure contracts. |
| A-AC-03 | Atomic business requirements versus eventual mechanisms produce explicit conflicts, affected behavior and owner options; the architect cannot weaken the model. |
| A-AC-04 | Story and spec authoring preserve observable GWT examples with the selected author. F1 addresses contradictory spec presentation guidance. |
| A-AC-05 | Test design owns levels, cases, data, isolation, independent expected-value sources and coverage; unknown business expectations remain unresolved. |
| A-AC-06 | Orchestrator reuses accepted artifacts/authorization and selects only work blocking the increment, without a fixed pipeline. |
| A-AC-07 | Counterexamples route requirement ambiguity, model ownership and mechanism infeasibility to their respective owners. |
| A-AC-08 | Checkpoint continuation retains identities, completed work, authority and unknowns without restarting completed stages. |
| A-AC-09 | Optional missing knowledge permits unaffected caller-source common work with unavailable coverage; protocols prohibit ambient source fallback and implicit configuration writes. F1 aligns spec guidance. |
| A-AC-10 | Model/architecture review binds a fixed subject and discloses author relation, independence and coverage; self-check is not independent acceptance. |
| A-AC-11 | New source catalog rejects the retired ID without alias; migration keeps explicit selection/bindings and preserves custom/drift conflicts. |
| A-AC-12 | Source members, exact common 0.4.0/dotnet 0.1.5 pins, presets 0.2.0 and knowledge-empty selections agree. Root/manuals distinguish source from the unchanged installation. F1 aligns the packaged spec guide. |
| A-AC-13 | Large network/infrastructure/platform operations are outside the selected software skill; no future system/DevOps capability is claimed available. |

The four requested walkthroughs were explicitly examined: pure domain order
cancellation, payment API isolation with an accepted model, GWT Story/production
spec authoring, and strong business consistency against an eventual mechanism.
The third exposed F1; the other paths had no supported new finding. All thirteen
criteria were examined rather than treating those four cases as exhaustive.

## Corrected-subject follow-up

The same independent reviewer read only the correction at
`589abfcd97d8e145d8d9930814904b17bc05f2c7` against the original reviewed commit and
its direct protocol/metadata/authoring dependencies. F1 is resolved: guide lines
44–47 preserve GWT contract examples (A-AC-04), lines 15–18 preserve verified
optional knowledge and no source import (A-AC-09), and metadata-4/common 0.4.0
consumption remains consistent without implying rule adoption (A-AC-12).
The diff contains only spec-guide.md; earlier unaffected review coverage remains
applicable. No actionable finding remains in the selected reviewed scope.

## Test evidence and limits

The reviewer inspected the setup/action/assertions of the three new source-backed
resolver tests, including independent/combined selection, absent/common/.NET
knowledge, retired ID and legal/illegal resource selectors. The reviewer used the
parent's recorded 130-test result in [implementation results](implementation-results.md)
as supplied evidence and did not claim to have rerun it. The Catalog unit fixture
is not evidence of an installed project or actual model behavior.

The F1 correction changes instruction prose and one local guidance link, not
metadata, member closure, parser or executable behavior. Its three guide file
links resolve; whitespace check passed. Verification is the bounded independent
semantic follow-up, not a repeated distribution/schema run without a new trigger.

## Local work and provider state

| Issue | Local delivery covered by these records |
| --- | --- |
| #476 | Complete design, prior independent design review, four coherent source Stories and implementation review; F1 is independently verified resolved and local work is complete. |
| #477 | Domain explore/design/review, domain consistency owner, optional methods and independent selection. |
| #478 | Software design/review, accepted-model input, dependency/failure mechanisms and model-owner feedback. |
| #479 | Requirement/Story/spec/test/orchestrator boundaries and common BDD/DDD method access; F1 correction independently verified resolved. |
| #480 | Catalog/preset/pin/member closure, old-ID retirement, source-backed regression evidence and controlled migration/manuals. |

All nine Issues #476–#484 were fetched open with their expected Chinese Feature/
User Story titles and labels. Feature/Story hierarchy uses explicit bidirectional
Issue links; native sub-issue fields were not set. Local completion does not close
the Issues or update Project fields. Future #481/#483 and #482/#484 retain their
separate design scope and have no product implementation in this delivery.

Push, PR, hosted checks, merge, self-installation, downstream upgrade and release
remain outside this local delivery. Their absence is not a passed gate.
