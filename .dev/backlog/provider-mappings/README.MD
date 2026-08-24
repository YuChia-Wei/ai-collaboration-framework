# Historical Provider Mapping Receipts

Provider mapping files are frozen point-in-time source-repository receipts.
They preserve how historical local backlog IDs mapped to external identities;
they do not own current backlog, roadmap, provider, workflow, or integrated
repository truth.

[`github-issues.yaml`](github-issues.yaml) starts empty in Stage A. Stage B must
append each successful Issue creation immediately, including the canonical
source digest and provider read-back result, so a failed batch can resume
without creating duplicates.

Post-migration receipts already recorded here remain historical evidence.
[`github-issues-SKILL-002.yaml`](github-issues-SKILL-002.yaml) is the first such
receipt; it keeps its live-creation idempotency key separate from the historical
July migration batch.

The hidden `canonical-backlog-id` and `migration-id` markers remain historical
idempotency evidence. New source Issues are not projected back into this frozen
directory. Current provider claims require explicit live read-back.
