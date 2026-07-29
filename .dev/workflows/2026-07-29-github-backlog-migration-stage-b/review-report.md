# GitHub Backlog Migration Stage B Review Report

## Outcome

Stage B is complete. GitHub now contains all 41 formal canonical backlog items as Issues and one public Project named `AI Collaboration Framework — Backlog & Roadmap`.

## Issue Migration

- 41/41 canonical backlog items have unique, verified GitHub Issue mappings.
- 5 unfinished items remain open; 36 resolved or declined items are closed with their exact close reason and historical evidence comment.
- Exact title, body, hidden markers, labels, empty assignees, lifecycle state, close reason, and closing comment were independently read back.
- Formal Issues carry `created-by:codex`; the hidden creation marker retains runtime, model, reasoning effort, and attribution email.

## Project Projection

- Project 3 is public and has the approved title and description.
- Five workflow-managed fields are configured: Status, Priority, Owner review, Target release, and Published in.
- 41/41 Issues have unique Project item IDs recorded in the provider receipt.
- 205/205 managed field values and 41/41 empty assignee sets match the canonical projection.
- Provider-native fields remain visible but are not repository workflow authority.

## Views And Automation

- `Active Backlog`: board, excludes Done, columns by Status, Priority ascending.
- `Roadmap`: table, excludes Done and Unassigned target release, grouped by Target release, Priority ascending.
- `Owner Review`: Pending or Changes requested, Priority ascending then Updated descending.
- `History by Release`: Done, grouped by Published in, Title ascending. The title prefix is the canonical backlog ID, so this implements the approved backlog-ID ordering without another field.
- Exactly three provider workflows are enabled to implement two approved outcomes: auto-add matching open Issues plus initialize Inbox, and set Done when an item closes.
- PR merge, PR linkage, auto-close, and sub-issue auto-add workflows are off.

## Canonical Boundary

GitHub Issues and Projects provide visibility, community feedback, priority, status, roadmap, and owner-review surfaces. `.dev/backlog/` and repository workflow artifacts retain detailed planning, execution tasks, validation evidence, and authorization. GitHub availability or state is not a prerequisite for repository workflow execution and cannot reverse-write canonical truth.

## Validation

- 41/41 Issue mappings and provider inventory: passed.
- 41/41 Project item URL and ID mappings: passed.
- 205/205 managed Project values: passed.
- Four Project views: exact GraphQL readback passed.
- Three enabled provider workflows and two allowlisted outcomes: signed-in UI readback passed.
- Repository provider tests and AI context validation: passed before final closeout; repeated in the final validation bundle.

## Residual Provider Constraints

- GitHub's built-in auto-add workflow evaluates new or updated Issues matching `is:issue is:open`; this is the provider-native implementation of the approved issue-opened outcome.
- Project view display options required signed-in UI configuration; GraphQL was used for exact persisted readback.
- No redundant Backlog ID custom field was created because every formal Issue title begins with `[BACKLOG-ID]`.
