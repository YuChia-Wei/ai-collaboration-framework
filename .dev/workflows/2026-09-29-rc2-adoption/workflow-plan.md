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

## Source and target integration read-back; bounded mechanical adoption complete

GitHub read-back confirms source PR #412 merged at `origin/main` commit
`31fd8a02dcb22c9f4ddc6734d5b6ccab423211c5`. Remote annotated tag
`v0.19.0-rc.2` is tag object `0f6118554f1573d835faf67aaa418dd291dd01d1`
and peels to product commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`.

Issue #409 is read back `CLOSED` (`completed`) at `2026-09-29T03:30:58Z`; provider comment: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/409#issuecomment-5883082732. At this intermediate checkpoint #411 and mq-lab #22 were still open; the final provider read-backs below record their closeouts. Future admission gate #23 remains open.

The initial MQ API2 apply returned `applied` with lock SHA-256
`c9a47c945f19fe869696c514003f7eb64ad0219b8f4a315fde4b1d7eaa7ea15f`, candidate
identity `subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:291ca4a018051a591e40018f91e6f0ef26c28854eabd746f9de0582a266f1ad2`, and
`project_readiness: not-assessed`. The resulting lock inventory contains 384
managed members; the selection contains 40 bindings. Read-only raw-byte checks
matched all 384 members against the subset manifest, staged Git blobs, and
working tree; lock, authority file, and installation selection staged/worktree
bytes also match. This proves byte consistency for that applied candidate, not
validity of every authority reference or runtime acceptance.

Automatic approval review initially blocked changes to the moved
`.dev/ai-context/TARGET-ENGINEERING-RULES.md`; direct user approval on
2026-09-29 then authorized the nine Markdown URL corrections and API2 rebind of
the forty bindings. The corrected authority file is SHA-256
`e46c6527b6cb7bf9cd9ef5c3cb19c0f9e36c38dd8ecdeda546c5c273b87d4c08`. The final
subset identity is
`subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:8e0eb8909b9a110b86398ed3f1a87d262b0691ddccdf63e7d49689a864556b71`.
Official API2 plan `572e8c2add8a7da06a7613d31671e827405b12a26f2e781d9b999d701a4a099b`
and apply returned `planned` and `applied`. The apply changed only
`.ai/custom/installation.json` (SHA-256
`4d74012367bd1ec4a5aedb2ed7b923880c315dd7492d32559be88f101af3a5a3`); all 384
managed members were unchanged, with no additions or removals. The resulting
lock SHA-256 is
`be0cba5c82425c1fc67755b65b7956c6333d8205f637f4cb3e48e6c45f907223`. Direct
target read-back matched the lock, selection and authority hashes; the selected
configuration contains 18 skills, two knowledge packages, both runtime
adapters, and 40 bindings. API2 reports `managed-bytes-consistent` and
`project_readiness: not-assessed`; this establishes installation consistency,
not runtime or target acceptance.

GitHub read-back confirms mq-lab PR #24 is merged, with head
`711739f651491dc90259c5647ce7ca3e12efc0a8`, merge commit
`179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`, and merged time
`2026-09-29T05:52:25Z`. Comparing `main` to that merge commit returned
`identical` (ahead/behind 0); the primary MQ checkout is clean on `main` at the
same SHA. Direct provider read-back confirms MQ Issue #22 is CLOSED/completed at
`2026-09-29T05:52:26Z` (closeout:
https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/22#issuecomment-5884545150)
and source Issue #411 is CLOSED/completed at `2026-09-29T05:55:20Z` (closeout:
https://github.com/YuChia-Wei/ai-collaboration-framework/issues/411#issuecomment-5884545394).
This workflow is complete for mechanical source and target adoption. Future
admission gate #23 remains open; program Issues #322 and #369 remain open.
Runtime discovery/dogfood, S6 and P7 remain deferred-by-owner; no runtime,
behavioral or admission acceptance pass is claimed.

| Field | Current state |
| --- | --- |
| MQ Issue #22 | Closed/completed at `2026-09-29T05:52:26Z`; closeout linked above |
| MQ API2 installation | Rebind applied; lock `be0cba5c82425c1fc67755b65b7956c6333d8205f637f4cb3e48e6c45f907223`; 384 managed members unchanged |
| MQ selection bindings | 40; updated installation selection SHA `4d74012367bd1ec4a5aedb2ed7b923880c315dd7492d32559be88f101af3a5a3` |
| Authority URL rebind | 9 corrections directly approved and applied; authority SHA `e46c6527b6cb7bf9cd9ef5c3cb19c0f9e36c38dd8ecdeda546c5c273b87d4c08` |
| MQ PR / head | PR #24 merged; head `711739f651491dc90259c5647ce7ca3e12efc0a8` |
| MQ merge / main read-back | Merge and `main` are `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`; compare returned identical |
| Source Issue #411 | Closed/completed at `2026-09-29T05:55:20Z`; closeout linked above |
| Naming Issue #409 | Closed; read-back and comment linked above |
| Future admission Issue #23 | Open |
| Runtime / S6 / P7 | Deferred-by-owner; no acceptance pass claimed |

One diagnostic invocation of `validate-workflow-artifacts.py` stopped on the unrelated legacy locator `.dev/workflows/2026-09-23-portable-authoring/workflow.yaml`: its unquoted `created_at` was parsed as a datetime, then the validator raised `TypeError` in `datetime.fromisoformat()`. This was not a selected closeout gate; no legacy workflow was changed. Focused changed-file parsing/link checks and `git diff --check` passed.

## Source local outcome

The first source API2 plan returned `planned` with plan SHA-256 `3b3d13195bd88635f8bbd52ca1c33f94474ba8c236a300441c1c1f5700ded260`. Apply returned `applied` with 151 additions (149 subset members plus `.ai/custom/framework.json` and `.ai/custom/installation.json`), operation `i-0c67c406734a28642b913e8ac21bff21`, interim lock SHA-256 `b9b74f03b3ce0e6940d738a22d148ab7167a6488ab3a68a9107512a9afae2a14`, and managed state `managed-bytes-consistent`. Static read-back confirmed all 149 installed member hashes matched that interim subset. After the shared final catalog/subset was assembled from `aad927328c20b08c8445e8ad1792eadd8ecc3466`, the source API2 plan returned `planned` with SHA-256 `d302abd474be2dea0d6e5c931ef9d0d6cc51f25d079face715b324aa45d00282`; apply returned `applied`, operation `i-bf53cac734964f414be34da71bbdc892`, with 149 managed members unchanged, the selection updated, protected framework config matching, and final lock SHA-256 `d2d69d0f6df72d35c258bdc7423b8168461b737c759eaf7ca9739086190e5368`. The selection is 18 original-name skills, both adapters, zero knowledge packages; six filesystem stores use exact write roots and package templates. No records/evidence or decision/promotion/local-backlog adapters were created. Final apply reports project readiness `not-assessed`; runtime discovery and dogfood were not performed. S6 remains `deferred-by-owner`.
