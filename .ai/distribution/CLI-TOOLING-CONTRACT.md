# CLI and Tooling Contract

Contract ID: `CLI-TOOLING-001`

## Status and Authority

This is a public contract only. It creates no native CLI, language runtime,
package, binary, registry publication, or toolchain repository.

`PRODUCT-SOURCE-001` owns canonical product-source and projection semantics.
The selected distribution profile owns source-to-target mapping and exclusions.
This contract defines how future tools consume those authorities without
duplicating them.

## Tool Boundaries

| Tool | Scope | Downstream delivery |
| --- | --- | --- |
| Distribution CLI | Controls inspection, planning, and explicitly authorized target lifecycle operations for an immutable framework payload. | Yes, when separately implemented and packaged. |
| Portable Validator Engine | Runs selected portable validation through a versioned external-process protocol and returns bounded evidence. | Yes, as a component of a future distribution capability. |
| Source Maintainer CLI | Handles release preparation, candidate verification, tag/release read-back, source closeout, and source tracker reconciliation. | Never. |

The source maintainer surface is source-only even when it shares a command name
or implementation library with another tool. It must not enter a payload,
consumer archive, or target repository.

## Distribution CLI Public Commands

Every command must declare its inputs, preconditions, preview behavior,
acknowledgement requirement, outputs, receipts, rollback boundary, security
requirements, outcomes, and exit codes. The contract categories below remain
stable while a future implementation chooses flags and presentation.

| Command | Purpose | Target mutation | Minimum authority |
| --- | --- | --- | --- |
| `init` | Initialize a new target from a verified payload. | Yes | Immutable product, safe target path, preview, acknowledgement where reconciliation exists. |
| `plan` | Produce a non-mutating application or upgrade plan. | No | Immutable product and target inspection evidence. |
| `apply` | Apply a fresh, reviewed plan transactionally. | Yes | Fresh plan, clean-worktree gate, explicit acknowledgements, and rollback receipt. |
| `upgrade` | Reconcile an initialized target with a verified newer payload. | Yes | Recorded target provenance, compatible migration source, and fresh plan. |
| `validate` | Inspect a payload, target, plan, or selected validator result. | No | Declared input and selected validation profile. |
| `rollback` | Restore only the state covered by an operation receipt. | Yes | Matching receipt, containment checks, and acknowledgement. |
| `uninstall` | Remove only safely identified framework-managed bytes. | Yes | Ownership and previous-release hash evidence plus acknowledgement. |
| `inspect` | Report product, profile, provenance, and receipt metadata. | No | Readable declared artifact or target. |

`init` does not mean installing the CLI. Installing a CLI, acquiring a framework
payload, initializing a target, reconciling an existing target, and upgrading
an initialized target are distinct operations.

## Safety and Trust

- Network access is denied by default. A network operation requires an explicit
  caller request plus a declared package source, checksum or signature policy,
  certificate and proxy policy, credential source, cache behavior, and offline
  behavior.
- A tool must never automatically download, log in, trust a certificate, use a
  credential, install a runtime, or elevate privileges.
- Target mutations require repository containment, symlink and case safety, no
  silent overwrite, dry-run support, stale-plan rejection, an explicit
  acknowledgement boundary, transaction handling, rollback information, and
  preservation of target-owned truth.
- A local archive, verified release artifact, or offline cache may supply a
  payload only when its canonical product version and digest are verified.
  Embedded bytes are permitted only under the same rule and are still a
  projection, not a second product authority.

## Stable Outcomes

Future command implementations use these semantic outcomes. The listed numbers
are the proposed public exit-code allocation and do not alter existing
validator exit-code contracts.

| Exit code | Outcome |
| --- | --- |
| `0` | `completed` |
| `1` | `failed` |
| `2` | `invalid-invocation-or-contract` |
| `3` | `blocked-by-environment` |
| `4` | `owner-decision-required` |
| `5` | `stale-plan` |
| `6` | `unsupported-source` |
| `7` | `cancelled` |

## Portable Validator Engine Protocol

The validator engine is process-based. A request declares at least:

```yaml
protocol_version: <version>
validator_id: <stable-id>
validator_version: <version>
profile: <selected-profile>
workspace: <contained-workspace>
selected_inputs: <declared-inputs>
input_fingerprint: <digest>
timeout: <bounded-duration>
environment: <declared-readiness-context>
```

Standard output is JSONL with `event`, `diagnostic`, `summary`, `outcome`, and
`evidence` records. Each run emits one terminal `outcome` record. Standard
error is bounded human diagnostics only and is not machine-contract authority.
The engine owns profile selection, changed-path impact, dependency ordering,
timeouts, cancellation, fingerprints, reuse decisions, external process
execution, evidence, and reporting; it must not infer a passing execution from
environment readiness alone.

## Deferred Decisions

The runtime/language, package manager or registry, signing, embedded-versus-
fetched payload transport, independent toolchain repository, CLI/product
version coupling, self-update, licensing/SBOM, notarization, and Windows code
signing remain owner decisions. This contract does not select or implement any
of them.

