# Project-specific RC3 migration to public v0.20.2

## Authority and boundary

On 2026-10-21 the owner authorized this project's RC3 migration procedure,
isolated rehearsal, recovery validation, independent review, and direct actual
installation afterward, preserving custom content, history and nine untracked
records, then assessing #472/#473. The later owner instruction selects Git
restoration in Git projects and forbids separate backups unless explicitly
requested. The final bridge records hashes and a fixed Git revision only.
Earlier rehearsal copies remain historical evidence; no new content backup is
selected. The official installer's operation journal remains part of its public
apply/recover protocol, not a separately invented backup procedure.

This is source-project orchestration in this workflow, not portable RC3 upgrade
support. Published packages, source product contracts, root governance, feature
selection and provider state do not change. No push, PR, merge, Issue closure or
new publication is selected.

## Fixed inputs

- Actual root: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`.
- Initial branch/head: `codex/2026-10-21-self-install-v0202`,
  `5df786a97631c026e60ac5e2086a148e9cab5f5e`; implementation is committed before
  actual preparation, so actual recovery uses that later observed fixed HEAD.
- Original lock raw SHA-256:
  `1536e7ae04cb58b96cebc928d3e97d277664ce9ba1545a6e04a6b55dbbfc73a4`.
- Original engine source: `5ed50d1b59115a2677711dbb91fcb8cc12dc2148`.
  All 24 members were reconstructed from that Git commit and matched the lock's
  pin. The published RC3 tag points elsewhere and is not substituted for this
  exact installed engine. External engine: `C:/tmp/mig202/old-engine`.
- Public v0.20.2 source: `3c7434fd3ea65bcbf519fef3e3ca232a0bc59043`.
  Archive SHA-256:
  `9ca52a7ee2cfc043e4781d941b04a9eb664e2def75bb0837c890a9e81dd79b15`.
  Unchanged public package: `C:/tmp/v0202-release/package`.
- Derived candidate:
  `C:/tmp/si202/out/subset-d13513d5782d4c2b969f326b452168ff`;
  identity `subset:3:0.20.2:3c7434fd3ea65bcbf519fef3e3ca232a0bc59043:67797fb9be0794438fa99071a5f82053b7bfe5cd2e6e93cf905c461b42dc5dd6`.
- Selection: the existing 17 skills, `bdd-gwt-test-designer` replaced by
  `test-designer`, both adapters, original names, empty knowledge/bindings.
  No initialization or implicit normative adoption follows.

## Procedure

Use Python `-I -B` with the existing PyYAML 6 environment. Keep the original
engine, candidate and official recovery records at their exact external paths.
The helpers are bounded to this root and disposable `C:/tmp/mig202` fixtures.

1. Confirm relevant sessions, tools and external writers are stopped. Inspect
   the final diff and fixed review result. Verify the public package/selection
   identities and that existing untracked records remain the same nine files.
2. Run `rc3-prepare-installation.py <project> <new-external-output>` to generate
   the six exact paired edits and public plan request. It writes only external
   proposed after objects. Changes are the two skill README entry/link names,
   the matching root English/Chinese routing identifier, the `.ai/INDEX.MD`
   portable reinstall path, and `.ai/custom/installation.json`.
3. Run `rc3-migrate.py prepare --project <project> --operation <new-evidence-dir>
   --engine C:/tmp/mig202/old-engine`. This requires clean tracked state, no
   markers/guard, fresh successful old public inspect with 135 owned members and
   no drift, safe paths, and exact Git blob preimages for all 135 files and lock.
   It records the observed HEAD, raw hashes and untracked names, without copying
   content. Pin the returned manifest SHA-256 in the following calls.
4. Run `rc3-migrate.py retire` with the same project/evidence and
   `--manifest-sha256 <returned hash>`. It rechecks HEAD, Git preimages, complete
   selected preservation snapshot and public old ownership, writes a durable
   intent record, then unlinks only exact verified owned paths, lock last.
   No directory is recursively removed. The optional interruption count is
   permitted only on disposable fixtures.
5. Call public `engine/src/tools/maintain_framework.py` with the prepared plan
   JSON on stdin. Review the exact plan, path budget, 17-capability scope,
   project edits, protected input and conflicts. Any failure stops installation;
   use the Git restoration procedure below rather than overriding admission.
6. Call the same public CLI with operation `apply`, the exact returned plan hash
   and fresh maintenance declaration for its sorted scope. Preserve stdout,
   stderr, exit code and the engine's original operation directory.
7. Run public inspect, then `rc3-verify-installation.py <manifest> <manifest-hash>
   <plan-request> <inspect-response>`. It checks all selected unchanged raw files,
   original untracked names/bytes, allowed write set, removed old-only members,
   six after hashes, candidate/engine, selection, both sets of runtime entries,
   empty knowledge/bindings and absent operation markers. Record this immediate
   observation before updating the workflow itself.

The fixture-only `rc3-exercise-installation.py` drives plan/apply/inspect and a
process-termination experiment. Its mutation actions cannot target the actual
project. Actual execution uses the public CLI directly with freshly reviewed
requests, rather than reusing a fixture maintenance declaration.

## Recovery boundaries

For partial retirement, use `rc3-migrate.py restore` with the original pinned
manifest. It verifies the original Git blobs, accepts only missing or identical
owned files, and requires all non-owned content to match the observed state.
It runs `git restore --source=<observed HEAD> --worktree -- <missing owned paths>`
and restores the lock last. Git attributes mark these managed paths `-text`;
all 136 raw preimages matched Git blobs. Unknown replacement bytes are refused.
Restoration is restartable; retirement is not resumed from a guessed ordinal.
Start a new evidence directory for a later retirement attempt.

For interrupted new installation, first use its original public `recover` with
direction `restore`, exact engine pin, operation SHA and current marker/lock
hashes. Never delete markers or invent a journal. After official restore, run
the bridge restore with the retained `--recovery-request` and independently
observed `--recovery-request-sha256`. The bridge replays official restore as a
read-only `already-matching` observation before retiring only the new empty
coordination guard absent from the initial snapshot. It checks all unrelated
content first, opens that exact guard with zero sharing, verifies file identity,
and sets deletion disposition on the same Windows handle. An open writer,
unknown content, prior guard or nonmatching official state blocks this step.
Then Git restores the RC3 members and lock. No other untracked file is removed.

A completed successful new installation cannot be rolled back by replaying its
finished operation. If post-install acceptance fails, stop and retain evidence;
use the fixed Git revision only through a separately bounded reconciliation of
new paths and project edits. Do not blindly restore over newer unknown content.
These tests cover Windows process termination, not power loss, other platforms,
actor discovery or downstream behavior.

## Executed evidence

External paths below are execution-host evidence, not portable tool availability.
The actual project is still RC3 at this preparation checkpoint.

| Case | Observed result |
| --- | --- |
| Partial retirement | Fixture stopped after 17 deletions. An injected unknown replacement was refused without overwrite. After removing only the test-injected file, Git restored the original state; all 4,524 observed files matched. `C:/tmp/mig202/partial/git-evidence/` |
| Public new-install interruption | Unmodified official CLI was terminated after `.agents/skills/adr-author/SKILL.md` existed. Original operation `i-2a1654b00132a13f90a9e446b2cf2fcd` was retained. Official restore returned `recovered`, `uninstalled`, null lock; the bridge's official recheck returned `already-matching`, retired only its empty guard and restored RC3 via Git. All 4,524 files matched. `C:/tmp/mig202/interrupted/new/` and `interrupted/backup/restore-recheck.json` (historical directory name; final restore read Git, not backup objects). |
| Successful migration | Official apply and post-inspect passed; 137 owned members, 17 skills, both adapters, six paired edits, 4,382 preserved files and all ten fixture-untracked files unchanged. Ten includes the copied bridge script plus the nine original records; it is not the actual target's untracked count. Immediate installed lock hash `440c6e48d8e1eced1f8a84b50489453b459de39f0ea71f56e0d9e625e6690fc5`. `C:/tmp/mig202/success-new/` and `success-evidence/`. |
| Final request producer | Generated request exactly equals the successful exercise's request after excluding project/evidence roots and authority wording. `C:/tmp/mig202/producer-check2/`. No repeat install is needed for those differences. |

Retained harness corrections: initial verification compared the expanded lock
selection envelope with the desired document; comparison now uses `desired`.
The final producer's occurrence check initially missed README display/link pairs;
it now requires exactly two there and one in each root guide. One read-back was
blocked by sandbox access to the external Git fixture and then passed with the
authorized external-path execution. These are harness issues, not product
failures. Earlier noncanonical reconstructed engine descriptor attempts are
retained; the successful descriptor and every engine member use exact pin bytes.

Independent immutable review and actual-target acceptance follow this checkpoint.
