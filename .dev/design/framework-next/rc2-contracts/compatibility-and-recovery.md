# Reader compatibility, migration and recovery

This table is a required S3 implementation boundary, not executed compatibility
evidence. Fixed rc.1 source: `1ce41a4f03f61e83bf9b99de3ce196887547e922`;
maintenance engine: `3afb4ff4207acb3e12e3953018736305a439ed21`.
The S1 source baseline is `6f5a13046f1978ba4b8701e4ae772faecde2c2ff`.

| Input | Existing API 1 / engine 1 reader | Existing writer | Required API 2 / engine 2 reader | Required writer disposition |
| --- | --- | --- | --- | --- |
| Selection 1 development, inventory/build 1 | Supported existing branch | Existing managed route only | Preserve exact legacy parser, canonicalization and identity | Legacy API 1 route stays available with an explicit old pin; API 2 does not fabricate upgraded identity |
| Selection 2 versioned rc.1, inventory/build 1 | Supported existing branch | Existing lock 1 route | Preserve exact legacy branch | API 2 can use it as old installed evidence; new rc.2 output requires a real catalog/subset |
| Lock 1 embedding selection 1 or 2 | Existing lock parser | Existing apply/recover only within its pinned contract | Read with exact original semantics and original embedded engine pin | rc.1 to rc.2 upgrade only after fresh old-byte/ownership checks; emit lock 2, never rewrite old lock before plan |
| Catalog 1 / catalog-files 1 / catalog build 2 | Unsupported | Unsupported-write | New catalog branch; bounded complete artifact read | Catalog is an input; never treat it as an installable legacy candidate |
| Selection 3 / inventory 2 / subset build 2 | Unsupported | Unsupported-write | New subset branch, strict parent/subset recomputation | API 2 can emit lock 2 after admitted apply |
| Lock 2 | Unsupported | Unsupported-write | New lock branch; recompute embedded parent and subset | API 2 apply/recover only; old engine must not touch it |
| Unknown or mixed discriminator combinations | Reject | No writes | `unsupported` or malformed closed-shape block | No fallback, field stripping, version coercion or best-effort repair |

Existing identity strings remain `development:COMMIT:DIGEST` and
`versioned:VERSION:COMMIT:DIGEST`. Their digest input is the existing canonical
mapping of selection/files raw hashes. No rc.2 field enters a legacy digest. The
retained engine 1 identity inside a lock 1 must be accepted only by the legacy
branch; engine 2 pins must not be substituted into historical evidence. A reader
pin never stands in for a writer's full executable closure.

API 2 is a distinct public protocol discriminator. The old API 1 behavior and
request shape remain unchanged under the original pinned implementation. A new
engine may inspect both old and new states but API 2 writes only the explicitly
selected new subset format. Downgrade is not an implicit inverse upgrade. Recovery
restores the retained exact old lock/core/runtime/project states through its
recorded engine and journal contract; an unrelated install of old files is not
recovery evidence. Unknown journal versions or incomplete closure fail closed.

## rc.1 to rc.2 plan and apply sequence

1. Select one immutable new catalog, explicit desired selection, separately pinned
   engine 2 and existing installation root. Preserve fixed rc.1 candidate identity:
   `versioned:0.19.0-rc.1:1ce41a4f03f61e83bf9b99de3ce196887547e922:286088361638d65f741c0fd5c39b210b0bd868c2a08d1e235a3d5613d40bcdbb`.
   Fixed mq-lab lock hash is
   `a04e2df01f5f6df6889b7c09daa1b9ae1c78e6b503aac852d5aa2b325c56a0e8`;
   reobserve actual current raw lock before any future operation.
2. Read all old lock-owned files and every affected destination through verified
   bounded readers. Absence of a lock is absence of ownership. An unowned file is
   still a collision when its bytes happen to equal the candidate. Edited/missing
   old managed files block an ordinary upgrade; do not restore defaults or infer
   adoption from matching names. Check case aliases, hardlinks, symlinks/reparse
   points, inaccessible entries and path/volume identities before making a plan.
3. Resolve the new subset and its exact runtime names. List add/change/remove/
   unchanged/mode-only entries, old-to-new name transitions, knowledge dependencies,
   affected rule bindings, protected inputs and exact project-owned edit intents.
   Prefix migration is two inventory actions with one semantic pair, not a loose
   directory rename. Directory names alone never authorize removal.
4. For each old `.agents/skills/framework-<id>/SKILL.md`, require both old lock
   ownership and unchanged current descriptor/bytes before scheduling removal.
   Check the new `.agents/skills/aicf-<id>/SKILL.md` and Claude destination for any
   unowned or edited collision. Preserve unknown sibling files; do not recursively
   delete an entry directory. If an extra file could retain old active discovery,
   block the cutover and report the exact entry. No accidental dual-autoload window
   is a completed transition.
5. Legacy unprefixed entries and old Claude entries are not lock 1-owned. Their
   withdrawal is an explicit project-owned route edit with baseline bytes and
   before-state recovery. Never revive archived entries or apply prefix deletion
   to them. S4 generates the new Claude adapter; S5 owns project routing changes.
6. Preflight recovery closure for managed and project-owned surfaces, acquire the
   existing nonblocking OS-held writer exclusion, check operation markers, exact
   expected lock hash, protected input hashes and caller quiescence again. A plan
   does not establish exclusion or quiescence. Do not unlink/replace the guard.
7. Journal preimages before mutation. Apply the selected managed transition,
   publish lock 2 only through the admitted writer, and perform separately
   authorized project edits under the paired transition boundary. Verify exact
   after-state bytes and all affected runtime entries. Until both sides complete,
   markers continue to block normal activation; a managed-byte receipt is not a
   whole-project-ready receipt.
8. Retain the immutable parent/subset metadata, exact engine closure, old/new lock
   bytes, managed descriptors and project edit receipts with the recovery record.
   Cleanup is separate and must not discard unique rollback data or volatile-only
   evidence. Copying a commit to another machine does not transport local recovery
   objects; R4 remains until a separate portability run proves the needed closure.

## Deselection and dependency changes

Deselecting knowledge removes only unchanged inventory-owned members. Required
package or active normative-binding dependency omissions block the plan until an
explicit, authorized selection/authority reconciliation is in the same transition.
Removing an optional package changes coverage to unavailable, never to a successful
specialist review. Arbitrary removal from a candidate directory is invalid closure.
Removing Codex does not remove Claude or selected core; removing Claude does not
remove Codex. Removing both leaves selected core. Removing one skill removes only
its unchanged core and corresponding selected adapters' entries; unknown user
entries, `.ai/custom`, project rules, records, Lessons and ADRs remain project-owned.
Same payload with a different parent/subset/selection identity requires a lock
transition; same identity, mode and project-input binding can be a true no-op.

## Paired recovery contract

| Surface | Required before-state | Recovery requirement |
| --- | --- | --- |
| Selected core members | Exact old descriptor and content, including absent state | Restore exact bytes/modes/absence without overwriting unexpected drift |
| Runtime entries and name transition | Both old/new names and each owned entry's bytes | Restore the old discovery set with no duplicate active counterpart |
| `.ai/framework.lock` | Exact raw previous lock or explicit absence | Restore paired lock after validating retained metadata and writer provenance |
| `.ai/custom/installation.json` | Raw bytes or explicit absence, plus expected current hash | Restore exact prior desired selection; no reconstructed equivalent substitute |
| `.ai/custom/framework.json` | Raw bytes/absence, package settings and stores preserved | Restore exact previous configuration without undoing unrelated user changes |
| Roots, indexes and authority/routing files | Exact named files and route withdrawal/archive preimages | Restore the paired project activation state; no whole-file template seeding |
| Project data created during later real use | Explicitly separate data-migration ownership | This transition is `project_data_action: none`; do not erase newer records to simulate rollback |

Project edit intent is closed and serialized separately from managed payload:
`{path, before_sha256|null, after_sha256|null, after_content_ref|null}` with exact
before bytes retained by the transition record; null expresses absence. The
after-content reference addresses a verified transaction object, not an arbitrary
file. Plan pins the complete canonical intent list and checks that no managed or
protected path is double-owned. Source/target adoption writers must expose these
intents to S3, not edit roots opportunistically after installation.

A recovery implementation must retain its actual marker/journal versions and exact
phase transitions in the S3 design before use. API 2 may extend those versions but
cannot merely skip old ownership, bounded-object verification, drift, quiescence,
atomic/unsupported-filesystem handling or fail-on-incomplete behavior. Interruptions
at each paired boundary remain S6/P7 work. Unknown before/current state requires
operator reconciliation, not guessed replay. Windows mode policy records inventory
modes without inventing POSIX permission restoration.

## Remaining stable obligations

R1 source self-adoption, R2 publication/delivery, R3 actual stable-input update and
rollback, R4 cross-computer recovery portability, R5 owner-deferred native/CI/policy
and selector/admission gaps, R6 runtime/decision adapters and legacy duties,
R7 input-specific candidate/engine admission and C-001 uncertainty, and R8 selectable
knowledge installation all retain their identities. S1 specifies R8 and part of
R1/R6; it closes none through execution. rc.1-to-rc.2 success cannot substitute for
R3 stable-input evidence. #369 native, Actions/CI, dormant source policy, stable
0.19.0 and a new rc.2 tag/Release remain unselected.
