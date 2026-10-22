---
name: user-story-author
description: Plan independent outcome slices, draft or normalize a User Story, or review a whole Story or selected acceptance criteria while preserving sources, decisions, templates and uncertainty.
---

# User Story Author

Use `plan`, `draft`, `normalize` or `review` independently. One explicit need or
existing Story is sufficient input; no upstream authoring skill or PRD is required.
Read the [shared Story contract](references/story-contract.md) for every operation,
then only [planning](references/plan.md), [authoring](references/authoring.md) for
draft/normalize, or [review](references/review.md) for the selected operation.

For draft/normalize select the caller's template first. Otherwise choose only the
matching Description template: [user value](references/templates/user-value.md),
[business rules](references/templates/business-rules.md), or
[technical outcome](references/templates/technical.md). Load
[examples](references/examples.md) only when an illustration helps. Do not preload
all templates. Use the caller's language, including Traditional Chinese (Taiwan),
and preserve its accepted terminology and custom format.

Return in conversation unless a destination is requested and authorized. Review
leaves its subject and provider state untouched; export a report only if requested.
This instruction package has no configuration, store, tool or required skill
dependency. Optional selected BDD/DDD knowledge follows the metadata-4 allowlist
and [verified resource protocol](references/knowledge.md). Missing coverage is
unavailable without source fallback; selection does not adopt target rules.
Availability supplies no provider-write,
implementation, approval or product-acceptance authority.

This skill owns dedicated Story planning, authoring and requirement/AC review.
Broader PRD, Feature and general requirements remain with requirement-author.
Test-designer owns test cases, levels, data, oracle machinery and coverage;
observable acceptance wording here does not create a second test-design owner.
No handoff or skill chain is mandatory.
