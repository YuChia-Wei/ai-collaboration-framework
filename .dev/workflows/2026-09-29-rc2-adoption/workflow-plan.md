# RC2 source and target adoption

## Authority and delivery

On 2026-09-29 the owner selected RC2 source and mq-lab adoption, Git tag creation, integration and applicable Issue closure. Known framework-managed documents are replaced destructively with the current version; superseded documents are removed rather than retained as backup copies. Git history retains tracked predecessors. Effective project rules, recent product documentation and intentional untracked local settings remain project-owned.

This work is bound to source Issue #411, naming closeout #409 and program #322. Downstream adoption is independently bound to dotnet-distributed-architecture-lab Issue #22. Program #322 and #369 remain open for their other obligations.

The first source catalog and local installation used interim source commit `3908974fe3c1e2989253459cd3488d8c29da47f9`, version `0.19.0-rc.2`. The final shared product input is source commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`, which includes the bounded recovery-object capture scan repair. GitHub read-back confirms source PR #412 merged at `origin/main` commit `31fd8a02dcb22c9f4ddc6734d5b6ccab423211c5`. Remote annotated tag `v0.19.0-rc.2` has tag object `0f6118554f1573d835faf67aaa418dd291dd01d1` and peels to fixed product commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`. This records source integration and tag read-back only; it does not establish runtime acceptance or downstream completion. The earlier `3be598cb2025aaaded01df9c4c018086b5e0d1da` input was rejected during catalog preparation because nine knowledge resources carried rule IDs; the metadata repair changed 18 `kind` values to `normative-rule` without changing other resource semantics. A GitHub Release and stable publication are not selected.

## Execution and file ownership

- GPT-6 Luna prepares the fixed catalog/subsets and performs source context replacement.
- GPT-6 Sol reconciles mq-lab changes and performs the downstream replacement.
- Each checkout has one tracked writer. The coordinator owns integration, tag and Issue closeout after local delivery.
- Both selections contain all 18 delivered skills, Codex and Claude adapters, and original skill names. Source selects no engineering knowledge; mq-lab selects common and .NET knowledge.
- Product `src` stays authoritative. Generated installed core and runtime entries are copied from the verified fixed subset and are not hand-edited.
- Replacement uses explicit contained paths; tracked obsolete wrappers and documents are deleted. Retained legacy source tooling must have an active responsibility, not historical-retention reasoning.

## Owner-selected verification scope

S6 is `deferred-by-owner` for this delivery by direct instruction on 2026-09-29. This also defers actual runtime discovery, behavioral acceptance, upgrade/recovery trials and the downstream current-admission run for this mechanical adoption. Necessary inventory, parsing, changed-link, Git diff and generated-file hash checks remain. These checks do not establish S6 success or an independent target admission.

U001 continues to defer legacy/formal/hosted validation and CI restoration. No dormant source policy, CI setting, credential or application runtime change is selected. The later owner-selected S6/P7 work remains responsible for unexecuted checks.

## Completion

1. Source and mq-lab contain the intended explicit selections and current project routing; superseded active documents are gone and effective project semantics survive.
2. Necessary static/file checks and skipped checks are reported separately.
3. Both changes integrate through their authorized PRs and main read-backs.
4. The immutable product tag is pushed and read back; bounded adoption Issues and #409 close with S6 deferral visible.

## Source integration and tag read-back; downstream final-integration checkpoint

GitHub read-back confirms source PR #412 merged at `origin/main` commit
`31fd8a02dcb22c9f4ddc6734d5b6ccab423211c5`. Remote annotated tag
`v0.19.0-rc.2` is tag object `0f6118554f1573d835faf67aaa418dd291dd01d1`
and peels to product commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`.

Issue #409 is read back `CLOSED` (`completed`) at `2026-09-29T03:30:58Z`; provider comment: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/409#issuecomment-5883082732. Direct GitHub issue read-backs show #411 and mq-lab #22 remain open, and #23 is open as the future target-admission gate.

The coordinator's official MQ API2 apply returned `applied` with lock SHA-256
`c9a47c945f19fe869696c514003f7eb64ad0219b8f4a315fde4b1d7eaa7ea15f`, candidate
identity `subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:291ca4a018051a591e40018f91e6f0ef26c28854eabd746f9de0582a266f1ad2`, and
`project_readiness: not-assessed`. The resulting lock inventory contains 384
managed members; the selection contains 40 bindings. Read-only raw-byte checks
matched all 384 members against the subset manifest, staged Git blobs, and
working tree; lock, authority file, and installation selection staged/worktree
bytes also match. This proves byte consistency for that applied candidate, not
validity of every authority reference or runtime acceptance.

The move of `.dev/ai-context/TARGET-ENGINEERING-RULES.md` left nine authority
URLs proposed for correction. The exact nine-replacement diff remains
`proposed-not-applied`; owner disposition is pending after automatic review
required direct owner approval. No URL has been changed. Rebuild the final target
subset and perform the official API2 rebind only after that disposition. GitHub
read-back confirms mq-lab PR #24 is OPEN and draft, targets `main`, and reports
head branch `codex/2026-09-29-framework-rc2-adoption` at
`aecf4b2ebc3ed1fc661138c06a93c6d2c03101ca`; `merged_at` is null. Branch search
confirms that head branch exists, and fetching the reported commit returns the
same SHA. PR integration and main read-back remain pending. Do not mark MQ
adoption or the overall workflow complete.

| Field | Current state |
| --- | --- |
| MQ Issue #22 | Open |
| MQ API2 installation | Applied; lock `c9a47c945f19fe869696c514003f7eb64ad0219b8f4a315fde4b1d7eaa7ea15f`; 384/384 exact staged and worktree bytes |
| MQ selection bindings | 40; official rebind pending corrected subset |
| Authority URL proposal | 9 replacements; not applied; owner disposition pending |
| MQ PR / head | PR #24 is OPEN/draft against `main`; provider reports head `codex/2026-09-29-framework-rc2-adoption` at `aecf4b2ebc3ed1fc661138c06a93c6d2c03101ca`; not merged |
| MQ merge / main read-back | Pending owner disposition, final subset rebuild and API2 rebind, then integration |
| Source Issue #411 | Open |
| Naming Issue #409 | Closed; read-back and comment linked above |
| Future admission Issue #23 | Open |
| Runtime / S6 / P7 | Deferred-by-owner; no acceptance pass claimed |

One diagnostic invocation of `validate-workflow-artifacts.py` stopped on the unrelated legacy locator `.dev/workflows/2026-09-23-portable-authoring/workflow.yaml`: its unquoted `created_at` was parsed as a datetime, then the validator raised `TypeError` in `datetime.fromisoformat()`. This was not a selected closeout gate; no legacy workflow was changed. Focused changed-file parsing/link checks and `git diff --check` passed.

## Source local outcome

The first source API2 plan returned `planned` with plan SHA-256 `3b3d13195bd88635f8bbd52ca1c33f94474ba8c236a300441c1c1f5700ded260`. Apply returned `applied` with 151 additions (149 subset members plus `.ai/custom/framework.json` and `.ai/custom/installation.json`), operation `i-0c67c406734a28642b913e8ac21bff21`, interim lock SHA-256 `b9b74f03b3ce0e6940d738a22d148ab7167a6488ab3a68a9107512a9afae2a14`, and managed state `managed-bytes-consistent`. Static read-back confirmed all 149 installed member hashes matched that interim subset. After the shared final catalog/subset was assembled from `aad927328c20b08c8445e8ad1792eadd8ecc3466`, the source API2 plan returned `planned` with SHA-256 `d302abd474be2dea0d6e5c931ef9d0d6cc51f25d079face715b324aa45d00282`; apply returned `applied`, operation `i-bf53cac734964f414be34da71bbdc892`, with 149 managed members unchanged, the selection updated, protected framework config matching, and final lock SHA-256 `d2d69d0f6df72d35c258bdc7423b8168461b737c759eaf7ca9739086190e5368`. The selection is 18 original-name skills, both adapters, zero knowledge packages; six filesystem stores use exact write roots and package templates. No records/evidence or decision/promotion/local-backlog adapters were created. Final apply reports project readiness `not-assessed`; runtime discovery and dogfood were not performed. S6 remains `deferred-by-owner`.
