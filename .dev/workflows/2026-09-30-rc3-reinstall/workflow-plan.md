# RC3 source reconciliation and breaking reinstall

Owner authorization: 2026-09-30 conversation, four work items, MQ trial in an
F: RAM-disk Git worktree. Continuation starts at the owner's cleanup commits on
`0.19.0-rc3`, rather than dropping them by starting at older `main`.

| Task | Ownership | Acceptance | State |
| --- | --- | --- | --- |
| S1/T1 | source_coverage, F:/framework-next/rc3-skill-packages | Retire portable workflow v2; three author package IDs; keep record family identities | in_progress |
| S2/T2 | original_requirements, F:/framework-next/rc3-knowledge | Every moved document has an include, consolidate or retire disposition; declared resources and live links | in_progress |
| S3/T3 | coordinator, F:/framework-next/rc3-coordinator | Explicit breaking reinstall with Git baseline, exact cleanup preimages and preservation checks | in_progress |
| S4/T4 | coordinator, isolated F source and MQ trials | Actual package/subset/install; obsolete files absent; preserved target content hashes match | pending |

The target inventory worker is read-only and writes external evidence only.
One tracked writer per worktree. Workers return local commits; coordinator owns
integration. No push, PR, merge, CI restoration, tag or publication is authorized.

Workflow storage, compression and online hosting remain v0.20.0 #416. Source
`.dev/workflows`, existing work products and project-owned knowledge are retained.
Obsolete framework files may be removed or replaced; Git is the recovery source.

This proportionate source locator follows WORKFLOW-ARTIFACT-POLICY directly;
there is no active legacy package template after the owner's source cleanup.
It does not claim old validator compliance or restore the retired portable skill.
U001 keeps broad legacy/CI/admission verification `deferred-by-owner` to #322/P7.
The user separately selected these focused RC3 packaging and installation trials.

Model attribution uses configured host defaults (gpt-6.1-sol / ultra), observed
from config.toml, where the session exposes no concrete execution attestation.

Next: integrate S1/S2, commit the engine change, build one immutable candidate,
then perform the explicit source and MQ preservation trials with real evidence.
