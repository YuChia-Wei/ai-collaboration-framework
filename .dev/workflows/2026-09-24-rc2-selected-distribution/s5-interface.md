# S5 verified resource interface, version 1

Issue #406. This protocol is fixed for S5 integration and implemented on this S3
branch; selected S6 execution remains deferred-by-owner. Source presence and direct AST checks are not behavioral evidence.

## Entry and ownership

`distribution.catalog.read_installed_resources(project_root, expected_lock_sha256, authorities)`
is read-only. Import it only through the verified engine-2 source closure in an
isolated `-I -B` host; never add an ambient checkout to a target's import search path.
The maintenance `inspect` request does not discover or save project configuration.
An instruction-only S5 consumer may follow the exact installed-file protocol below
using this same reader owner; it must not invent another lock/metadata parser.

Arguments:

- `project_root`: explicit canonical project root selected by the caller.
- `expected_lock_sha256`: exact externally observed raw SHA-256 of `.ai/framework.lock`.
- `authorities`: closed Authority rows `{path, sha256, selector}`. This is the exact
  deduplicated authority allowlist from the selected bindings, not a query expression
  for S3 to evaluate. Duplicated `(path, selector)` is invalid. Every raw hash must
  match the direct bounded project file. Different selectors may name one file.

The reader rejects incomplete markers, absent/legacy lock, stale lock identity,
managed drift, unknown formats, path aliases/links/hardlinks, undeclared authorities
or authority/project-input drift. It verifies the complete installed lock-2
identity/member closure, all saved project-input pins and a fresh final marker/lock
observation before returning any index. Failures raise the shared bounded `InstallationError`
or `DistributionError`; no partial resource result is returned.

Exact successful return keys:

```text
{
  lock_sha256, candidate_identity, desired_sha256,
  resources: [{package, version, resource_id, member, sha256, resource}],
  bindings: [Binding],
  authorities: [{path, sha256, selector,
                 status: "raw-hash-matched", semantic_applicability: "target-owned"}],
  semantic_applicability: "target-owned"
}
```

`resource` is the exact closed Resource from content-package 1, including kind,
rule_ids, capabilities, operations and technology_profile. `member` is the exact
installed `.ai/core/knowledge/<id>/<member>` path; `sha256` binds its raw bytes.
`bindings` is the exact saved desired selection binding list embedded in lock 2.
No binding means no adopted normative coverage. Index availability grants neither
applicability nor approval. Caller data remain unchanged.

S5 filters the verified index/bindings by the caller's explicit capability,
operation, execution mode, affected paths/file types, technology and requested
coverage; consults the named target owner for authority selectors and predicates;
and reads only those resource bytes through bounded direct file reads matching the
returned SHA-256. Re-observe the exact lock/markers and authority hashes around the
read; if drift occurs, discard the result. It returns the consumption result from
S1 consumption.md (available/unavailable/blocked, coverage and exact missing items).
No technology inference, source `.ai/assets` fallback or silent specialist success.

Metadata-4 consumer row shape is the S1 KnowledgeConsumption definition:
`{id, package, version, operations, resources, requirement, on_missing}`.
Rows sort by id; operations/resources are sorted unique sets. IDs/operations and
configuration semantics retain their owner. S5 returns exact metadata/member bytes,
component versions and hashes to S3; only S3 updates shared manifest/catalog rows.

## Project-owned transition seam

API-2 plan/apply adds required `project_edits` (possibly empty) to the existing
closed plan fields. An intent is exactly
`{path, before_sha256: hash|null, after_sha256: hash|null, after_content_ref: string|null}`.
Non-null after content uses `objects/<after_sha256>` under the explicit staging root.
The object must already exist, be bounded/direct and match the hash. A delete has
both after fields null. Absence is explicit and never inferred from a filename.

The caller separately authorizes each root/config/routing withdrawal. S3 verifies
preimages and object bytes, rejects any managed/protected/control path overlap,
retains exact before bytes/modes and after objects, and binds all edits into the plan
hash and journal 2. It never seeds target roots or writes config on ordinary inspect,
plan or invocation. `project_data_action` remains `none`. Final operation/journal
shape and phase transitions are published in api2-maintenance.md before S6 use.

## Isolated read-only host recipe

The bootstrap now exposes `verified_engine(engine_root, engine_pin)` as a host
context manager. It is the same `_load_engine` / `_VerifiedSourceFinder` used by
maintenance, verifies the complete Engine2 closure and checkout HEAD or standalone
engine descriptor, and unloads its distribution modules at exit. This is not a new
maintenance operation. A caller must authenticate the bootstrap raw bytes against
its independently selected pin before executing them.

A concrete host can reuse `verified_host(engine_root, pin_file)` from the delivered
`tools/derive-subset.py`; that small launcher authenticates the bootstrap bytes
before execution and never changes sys.path. The caller must authenticate that
launcher against the same engine pin before using it. In an isolated `python -I -B`
host, with an independently selected immutable `engine_pin` object and explicit
absolute `engine_root`, the equivalent steps are:

```python
import hashlib, os, stat, types
from pathlib import Path

# engine_pin comes from the caller's trusted admission record, not engine.json.
root = Path(engine_root)
name = "src/tools/maintain_framework.py"
expected = next(row["sha256"] for row in engine_pin["files"] if row["path"] == name)
launch = root / name
for item in (launch, *launch.parents):
    info = item.lstat()
    assert not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400
before = launch.lstat()
assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= 16 * 1024 * 1024
with launch.open("rb") as stream:
    opened = os.fstat(stream.fileno())
    code = stream.read(16 * 1024 * 1024 + 1)
    after = os.fstat(stream.fileno())
signature = lambda row: (row.st_dev, row.st_ino, row.st_size, row.st_mtime_ns, row.st_mode)
assert signature(before) == signature(opened) == signature(after) == signature(launch.lstat())
assert len(code) <= 16 * 1024 * 1024 and hashlib.sha256(code).hexdigest() == expected
host = types.ModuleType("aicf_consumer_bootstrap")
host.__file__ = str(launch)
exec(compile(code, str(launch), "exec", dont_inherit=True), host.__dict__)
with host.verified_engine(str(root), engine_pin):
    from distribution.catalog import read_installed_resources
    index = read_installed_resources(project_root, expected_lock_sha256, authorities)
```

Use ordinary explicit conditional checks instead of assertions if the host enables
Python optimization; the prescribed invocation does not enable `-O`. The host owns
bounded parsing of its trusted admission record and user operation arguments. S5
must preserve the returned identity with its task-scoped interpretation. Engine2
and the selected installed writer may be independently pinned; they are not inferred
from a source worktree, preset, package version or current lock description.
