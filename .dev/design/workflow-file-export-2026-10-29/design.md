# Current workflow file export design

Accepted parent design for FILE-EXPORT/#524; source baseline
`bc12a0d32c4a73f205aaa4a4e912ea48052c09d9`. Owning implementation route is
`slice-implementer`, generic mode. Parent owns integration and final acceptance.

One shared `workflow_records/file_export.py` plans, validates and writes
`workflow-records/files/1`. Native service `export-files` captures immutable state
and every referenced blob in one SQLite transaction. Group `group-export-files`
checks all three CAS fields under the existing group lock and exports only its
selected current authority. Existing archive exports and recovery are unchanged.

Workflow/task YAML contains exact metadata/task mappings without added reserved
keys. Manifest preserves task order, logical names, source reference/revision,
profile identity and file hashes/sizes. Current-record JSON retains complete native
state or group event body; raw blob files preserve bytes. Preflight reassembles YAML
values against the raw record, validates source revision/cut and reconstructs the
complete expected manifest. No import or restore API is added.

Optional explicit project selection pins a project-owned JSON document, workflow/
task Draft 2020-12 schemas and optional templates by raw digest. `.ai/project` is
allowed; managed runtime resources are rejected. Schemas support local references
only. Templates are validated mappings without transformations/default insertion.
Copied defaults carry their exact resource hashes. No installer/project settings
are modified and no custom legacy record is automatically upgraded.

All planning and validation precedes a fresh `mkdir` reservation. Portable
no-replace directory reservation avoids POSIX rename replacing another empty
destination. Exclusive payload writes precede manifest completion marker. Failure
cleans only invocation-created members; process termination may leave an invalid
partial directory. Direct hostile mutation and physical power-loss durability are
outside the cooperating-writer guarantee. Existing destination/live storage,
links/reparse/ADS/traversal/reserved paths and case/prefix aliases fail closed.

See product [contract](../../../src/skills/workflow-records/references/file-export.md)
for request fields, bounds, physical/logical path mapping and unsupported historical
reader/restore boundary. Focused tests are in
`tests/tools/test_workflow_file_export.py`; runtime tests and package closure are
local evidence, not independent review, hosted CI or deployment acceptance.
