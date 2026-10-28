# Project provider controls and unique local workflow authority

Date: 2026-10-26. Functional scope: [Story #520](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/520), under [Feature #513](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/513). This document defines expected behavior, not executed acceptance.

## Need and terms

Downstream maintainers need offline workflow records and independently owned remote integrations. The same workflow must support Local file and SQLite together, with exactly one selected source determining both reads and accepted changes. Secondary carriers follow that source. Registration identifies a project-owned remote adapter; it does not establish backend availability.

The scope comes from the owner's 2026-10-26 product request and the current #520 AC01–12. The unique-source interpretation includes reads and writes; it is distinct from the earlier source-store/2 read selector, whose writer remains SQLite.

## Requirements and acceptance

| ID | Required result | Observable acceptance / Issue mapping |
| --- | --- | --- |
| LOCAL-01 | Offline Local file is the default local arrangement. | A fresh explicit group can create, revise, resume and read a workflow without SQLite or remote dependencies. #520 AC01/11. |
| LOCAL-02 | Local file and SQLite can carry the same logical workflow. | Actual operations work with either selected authority; synchronization preserves identity, structured extensions, text and binary bytes. #520 AC01. |
| LOCAL-03 | Exactly one local carrier owns reads and writes. | Effective configuration names it; missing/conflicting selection, stale CAS and unavailable authority produce explicit failures without fallback. #520 AC05/07/11. |
| LOCAL-04 | Accepted changes retain recoverable, fixed delivery intent. | Payload, original operation identity, logical revision and target generations commit with acceptance; interrupted synchronization remains visible and can resume without regenerating content. #520 AC02–04. |
| LOCAL-05 | Authority and membership changes are explicit. | A change preserves old operation targets. Existing-data authority transfer validates the complete current state; stale or incomplete copies cannot become authority. #520 AC06/07. |
| LOCAL-06 | Complete backup retains recovery state. | Export/preflight/inactive restore retain data, original receipts, provider settings references and pending intents. Restore never replays external effects or silently activates a second writer. #520 AC08. |
| EXT-01 | Downstream projects own custom provider implementations and configuration. | Two separately identified registrations can be selected without modifying or importing into core; project paths do not enter managed framework resources. #520 AC10. |
| EXT-02 | Framework supplies versioned control and configuration interfaces. | Register, inspect, enable, disable, update and explicit operation handoff identify the selected generation, scope, payload and settings; stale revisions and unknown registrations are rejected. #520 AC10–12. |
| EXT-03 | Remote use remains experimental, optional and disabled by default. | Registration and inspection do not launch code or contact a remote. Offline use does not depend on a provider. Workflow Board remains the provided remote option. #520 AC11/12 and #513. |

## Boundaries

The framework owns local coordination and the provider control contract. Downstream projects own custom adapter code, settings semantics, credentials and remote operations. This delivery does not supply or verify those implementations, authentication, networks, remote persistence, availability, ACLs or real clients. A controlled framework-contract fixture is not remote acceptance.

Existing Git workflow locators, native SQLite schemas and Board protocols retain their meanings. No automatic migration, source-project production adoption, installation change, automatic failover, independent multi-master writes or conflict merging is required. The new managed Local file carrier is accessed through its public operations; arbitrary edits to legacy workflow.yaml/tasks files are not an additional concurrent writer protocol.

## Design-derived safeguards

The design uses explicit initialization, stable operation IDs, CAS, a local OS lock and full-state integrity checks to make the authority rule observable. Divergent members are rejected rather than silently merged. Timing/throughput and power-loss durability thresholds were not supplied; process-crash recovery must not be reported as physical power-loss proof.

Validation covers actual Local file and SQLite operations through the public CLI and framework-only provider control/configuration fixtures. Custom remote backend implementation and verification are excluded rather than counted as failed or passed coverage. Existing provided Board behavior receives regression checks only where affected; hosted acceptance remains separate.
