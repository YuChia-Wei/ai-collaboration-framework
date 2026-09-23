# Selected checks and small test layout

Every command/case below is **proposed and unexecuted**, **deferred-by-owner**,
U001, program #322 coordinator / P7. Follow-up implements tests; #364 creates no
tests, fixtures, product results or schema validation evidence.

## Runtime, entry and imports

Select already provisioned Python >=3.11,<4, PyYAML >=6,<7, jsonschema >=4.18,<5
and its `referencing` dependency. Maintenance permits Python 3.10+, but builder/
record tools raise this pilot's minimum to 3.11. Record actual versions later.
Git is needed for assembly/PR prepare and selected ignored local-config checks.
`gh`/authentication belong only to separately selected actual PR provider calls.
Missing dependencies yield unavailable/blocked; tests install nothing or change
host settings.

Use stdlib `unittest` and the small V1/V2/V3 layout in [README](README.md), not a
gate registry. Proposed commands, which do not exist yet:

```text
python -I -B tests/framework_next/run.py --layer contracts
python -I -B tests/framework_next/run.py --layer public --family lesson
python -I -B tests/framework_next/run.py --layer public
python -I -B tests/framework_next/run.py --layer native-windows --native-root <explicit-existing-root>
```

Future commands require an explicit source workdir. `run.py` loads only named
test modules by exact path. Unit tests may load an owner module using
`importlib.util.spec_from_file_location` in an isolated child; any monkeypatch
or bootstrap replacement is synthetic and cannot satisfy fixed-entry admission.
No fallback to another checkout, private cross-skill import, pip install,
historical package chain or full repository copy. Public tests invoke actual
paths with `-I -B` and the owned request protocol:

```text
python -I -B <selected-package>/scripts/<entry>.py --request <absolute-request.json>
python -I -B <engine>/src/tools/maintain_framework.py
python -I -B <engine>/tools/build-development.py --repository <engine> --commit <full-oid> --profile lesson-minimal --output-root <output-parent> --scratch-root <scratch-parent>
```

Maintenance takes one strict JSON request on stdin, no flags/help/request file.
The runner uses `subprocess.run([...], input=request_bytes, shell=False)` with
bounded output/timeout, recording child exit/bytes without shell encoding changes.
Record requests use absolute project/package roots; CBF uses its documented file
request form. Builder inserts its explicit `src` path; maintenance verifies its
ten-file closure before import. A direct `installation.execute` import is not
public maintenance evidence.

## Shared contracts

| ID | Inputs and observable assertion |
| --- | --- |
| C1 closure | Actual 18 packages/seven profiles through owner loader/selector on one commit; compare exact declared members to Git regular blobs/modes, versions and destinations, not only 113 count. Package-local refs and generated installed-only links resolve; no root/custom/history payload. |
| C2 metadata | Actual Lesson v2 (two readable schemas/one writable), null-config v3 code-reviewer, mixed instruction/tool v3 CBF; one minimal synthetic v1. Reject bool/float/unknown version, duplicate schema pair, undeclared tool/reference, wrong owner and mixed union arms. Null-config entry must not request config/store or invent runtime probes. |
| C3 selection | One missing required dependency, optional absent (not auto-added), version mismatch and cycle using tiny synthetic selections; case-fold/prefix/escape collision and nonregular/missing member in one tiny Git fixture. Do not multiply by seven profiles. |
| C4 config | All seven actual configured entrypoints: absent selection means defaults; explicitly missing config fails; project/local/invocation precedence with whole-template replacement; foreign namespace inert; local constraints rejected; locks/caller roots only narrow. Duplicate keys, bool/float version, own null/unknown field fail. Lesson v1 read and selected v1/v2 mismatch are distinct, without M01 migration. |
| C5 candidate | Assemble real Lesson twice: same selection/files/content identity despite run/time differences; 9 payload + 1 entry + 3 metadata files; raw bytes/mode inventory agree with Git. Missing completion, changed payload/hash/member closure is refused by actual installer reader. Mutated reader fixtures stay synthetic; public plan/apply use actual emitted candidate. |
| C6 ownership | Public reads/render preserve bytes. Stale raw digest conflicts; unknown version/malformed direct sibling is preserved and visible (partial query is not absence). Escape/outside root, wrong executable/package binding and undeclared schema/template refuse before publication. No recursive store scan. |

Use tiny strings for parser/type/depth boundaries. One generated 4 MiB+1 input
exercises the 4 MiB boundary without copying per case. Installer 128 MiB cumulative
budget arithmetic can use synthetic readers, labelled synthetic; no giant physical
fixture. Native path/mount/link/syscall claims need a real selected backend case.

## Seven family round-trips

Start each family with <=3 records and its declared template. Use actual stdout
references/hashes, not guessed values. Ordinary tools use `succeeded`/exit 0;
CBF uses `ok`/0 and distinct 2/3/4 failure exits. Do not invent a validate operation
for PR, backlog or workflow.

| ID / owner | Minimal sequence | Distinguishing negative/boundary |
| --- | --- | --- |
| T1 Lesson | `explain -> query -> create -> inspect -> validate -> render`; revise once and identical revise no-op; derive one v1 fixture into new v2 | Actual query-v2 digest and same text/status required; changed inventory conflicts, partial needs explicit acknowledgement. V1 stays unchanged/read-only. Accept without selected adapter blocks; fixture decision success is synthetic authority only. |
| T2 ADR | `query -> create -> inspect -> revise -> render`; two options and a synthetic mapped decision exercise decide, then derive | Stale decision subject/unknown option refuses; accepted cannot revise; derived draft resets decision and retains source snapshot. Synthetic actor does not prove project adoption. |
| T3 promotion | `query -> propose -> inspect -> validate -> render -> reconcile` with one source/target and synthetic project bindings | Changed captured target/config blocks; missing adoption/effect are distinct unresolved dimensions. Successful reconciliation need not mean adoption/effect succeeded. Target bytes never change; no apply operation. |
| T4 PR | One disposable two-commit repo, one UTF-8 change: `prepare -> inspect -> revise -> render(repository_root)` | Empty validation means none supplied; stale subject/digest refuses, deferred stays deferred. Adapter simulations cover unavailable gh, preflight conflict, post-write read failure/unknown and no retry. Actual provider trial requires separate authority. |
| T5 backlog | `query -> create -> inspect -> revise -> transition(draft,active) -> transition(active,completed) -> render` | Missing completion evidence/stale state fails; terminal revise fails; online references stay reference-only, no provider state change. Completion evidence is caller-attributed. |
| T6 workflow | `create -> inspect -> transition(planned,active) -> checkpoint -> resume -> retrospect -> retention-preview` | Retain fixture failure/attributed deferral in history; unresolved decision/failed acceptance blocks completed. Retrospective binds current content; change clears it. Preview never deletes; too-small resume budget refuses rather than drops criteria/history. Separate tiny with-deferrals completion is not aggregate pass. |
| T7 CBF | `explain -> create -> inspect -> validate -> render` with one source, actor/command/domain statements and one GWT assertion | Duplicate/missing links, unknown family/version, YAML legacy, filename/ID mismatch and same-byte destination conflict. Exact digest/inventory order/counts/pointers/unresolved IDs; no revise/query/migration/compliance claim. |

No full lifecycle matrix. Supersession gets one tiny chain/cycle negative per
independently implemented Lesson/ADR/promotion owner, not long histories. A defect
gets one focused regression and an explicit repair assignment at its owner.

## Instruction observations

C1/C2 cover all eleven null-config packages structurally. For useful later semantic
observation, supply one small requirement and inert target example; record actual
inputs/output/limits in prose: requirement/spec retain source uncertainty;
architecture identifies a boundary/tradeoff; GWT emits an observable assertion;
review/diagnosis distinguish supported findings from unconfirmed causes;
local/slice implementation respect selected radius; compliance consumes the actual
CBF owner result and keeps missing runtime evidence unresolved; optional auditor/
governance distinguish read-only findings from authorized edits. CBF authoring
precedes T7 through its instruction arm. These are agent observations, not keyword
tests or a schema for prose. Structural success cannot prove quality. Fresh runtime
observation belongs to later adoption; tests never spawn agents implicitly.

## Fixture and output limits

New test-only setting: `FRAMEWORK_TEST_OUTPUT_ROOT`, overridden by explicit
`--output-root`. Do not reinterpret legacy `AI_CONTEXT_TEST_TMP_ROOT`. Default
uses the OS temporary parent with one exclusive `fn-<uuid>` run and case-owned
subdirectories; no RAM/config/env setting required. Explicit invalid, unwritable,
linked or unsafe roots fail, never fall back. Preflight direct ancestors and
containment before allocation; cleanup only its verified created case/run.
Preserve failed residue until recorded; recovery is never disposable cleanup.
Leave TEMP/TMP and `F:/ai-context-tests` unchanged.

Opt-in affects logical fixtures only. `--native-root` is separately required and
never inherited from disposable settings or drive detection. Native defaults to
not-executed unless explicitly selected. Pilot has a third explicit binding set
in [windows-pilot.md](windows-pilot.md). No old classification manifest or native/
durability suite is silently rerouted.

| Selection | Initial stop-and-report cap / reason |
| --- | --- |
| Contracts/public | <=3 records per family, <=16 KiB normal fixture, <=1 MiB authored fixtures excluding one transient 4 MiB+1 boundary; <=256 created files; <=160 public launches and <=256 nested Git/helpers; two commits/<=4 files for PR Git fixture |
| Native Windows | <=2 live children, <=30 public/helper launches, <=3 retained operation roots, <=256 files/16 MiB output; one actual interruption boundary, not every member |
| Lesson pilot | Two same-content builds, <=24 builder/maintenance/Lesson launches plus <=12 driver Git launches; <=256 disposable files/16 MiB retained output; no repository-history copy |

Run one family at a time during development; the all-public command is an explicit
aggregate selection, not the default on every edit. These are planned limits,
not measured usage or relaxed product limits. Count
nested child work separately and in totals. Report logical bytes where instrumented,
files, Git/process count, wall time and retained bytes, otherwise unavailable.
No physical-write, SSD-wear, speed or token inference. No three-run benchmark
without a separately selected performance claim.
