# Provider Mapping Receipts

Provider mapping files are source-repository receipts. They bind portable
backlog IDs to actual external provider identities and record read-back state;
they never replace canonical backlog or workflow truth.

[`github-issues.yaml`](github-issues.yaml) starts empty in Stage A. Stage B must
append each successful Issue creation immediately, including the canonical
source digest and provider read-back result, so a failed batch can resume
without creating duplicates.

The hidden `canonical-backlog-id` and `migration-id` markers are the provider
idempotency keys. Provider numbers, node IDs, URLs, Project item IDs, and repair
notes belong only here.

