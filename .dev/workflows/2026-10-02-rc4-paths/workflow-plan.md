# RC4 path inspection and source correction

Issue: [#430](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/430).
Base and release product: `158b8438f61a60eb621e3a5b43ed1a0479634f6f`.
Owner instruction on 2026-10-02 selects inspection, necessary repair, parent
review of GPT-6.1 Sol work, PR integration/push and public prerelease.

This workflow retains the delegated audit, package-impact decision and local
repair/review state. Provider integration and publication continue in Issue 430.
Those observations do not require a source commit after publication.

| Task | State | Result / next action |
| --- | --- | --- |
| T1 | completed | Three read-only inventories returned; root accepted source-only findings. |
| T2 | completed | Local fixed-commit gate passed; independent review finding corrected and affected review passed. |

## Release decision

Remote annotated `v0.19.0-rc.4` already exists: object
`988448b6eb65c418e2a243e392dbd1204fa0d3dc`, peeled source equal to the base above.
Release `401752316` is an owned draft/prerelease. No product-impact path defect
was supported. Retain that tag and the three original assets. Source-only
corrections enter main separately, then the existing draft is published as a
prerelease under the owner's current authorization.

## Scope and limits

Fix current project-owned navigation and qualify missing legacy routes. Preserve
source/target and source/installed authority. Do not edit managed projections,
legacy support implementations, frozen records, the RC4 product, or MQ Lab.
The source selector gains only `.dev/INDEX.md` and `.dev/workflows/INDEX.MD` as
exact governance paths: source tests and independent review remain required;
unknown neighboring paths continue to fail closed.

## Integration

Use a PR and merge commit to preserve the inspected release base plus the
separate source correction/review commits. Final-head Source change gate and
live head/base admission are required. Refs #430; Issue closure and Project
changes are not selected. Actual skill/initialization behavior remains with
the owner's MQ validation. Keep branches; no cleanup was authorized.

See [audit and validation](results.md) for evidence, failures and residuals.


## Local completion and provider continuation

Both local tasks are complete. The substantive repair passed the fixed-subject
gate at `35c3bbe6389123e673bf983d298f90323c9aed68`; independent review and its
affected correction review bind `cb3bbb6b3b75ebe53d59dc0e415512de5aa00e31`.
The subsequent commit records completion only. Its final-head Source change
gate, read-only record review, PR admission, main read-back and publication
remain mandatory provider operations recorded in Issue 430 / the PR, not an
assertion that they already happened. Root retains integration ownership.
