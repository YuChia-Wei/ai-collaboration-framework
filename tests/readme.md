# Framework tests

Run from the repository root with Python >=3.11,<4 (the tested baseline is 3.13)
and the explicit dependencies in [requirements.txt](requirements.txt). The runner installs
nothing. Use an ordinary writable OS temporary directory; no F: drive, fixture
root setting, Git repository fixture, candidate build or installation is required.

```powershell
python -I -B tests/run.py
python -I -B tests/run.py --suite schemas --suite tools
python -I -B tests/run.py --suite distribution
python -I -B tests/run.py --suite release --suite source
```

Before selecting a command, inspect the actual diff, semantics and direct
dependencies under the [source development policy](../.dev/standards/SOURCE-DEVELOPMENT-POLICY.md#decide-before-running-a-test).
No-semantic-effect whitespace, ordinary prose or changes unrelated to schema
constraints do not require product/schema tests just because a file changed.
Whitespace affecting parsing or output is a real contract change. Use affected
existing cases/suites when needed; a report, commit or handoff alone adds no run.
After a failure, locate the cause and rerun its affected scope. Do not turn a
repair into repeated full-suite execution without a concrete wider impact.

Large integration, E2E, usability, full installation/upgrade and high-cost actor
checks require a clearly affected behavior/boundary or an explicit requirement.
They are not a default consequence of local development or closeout. Investigate
unknown impact first; do not silently expand to a whole matrix. This decision
needs no additional ledger, hash inventory, benchmark or trial.

A local default-suite run before a PR is optional integration feedback. It is
not required at every commit/stage and cannot replace the hosted current-head
PR gate. Existing results retain their original source and outcome.

The default selects the five suites below. Repeating `--suite` selects their
union in the supplied order. Unknown selections, empty suites, missing imports,
failures, errors and skips all fail. Unittest details go to stderr; stdout is one
`framework_tests` JSON object with interface `framework-tests/1`, selected suites,
outcome, test/failure/error/skip counts and elapsed seconds.

| Suite | Owned tests | Evidence |
| --- | --- | --- |
| `schemas` | `schemas/` | Current JSON schemas, real validators, accepted/rejected data, exact types, closure and references; declarative consistency for the provider YAML schema |
| `tools` | `tools/` | Actual renderers, config/record validation, small real local record lifecycles, bounded CLI requests and offline provider transports |
| `distribution` | `framework_next/` selected modules | Source declarations read in place; metadata, selection, adapters, versions and small maintenance records |
| `release` | `release/` | Release-helper behavior using synthetic offline transports; production helpers stay under `.github/scripts/` |
| `source` | `source/`, `test_runner.py` | Workflow trigger/permission boundaries, source policy, runner selection and rejection of false success |

Tool lifecycle cases exercise native local storage on the current supported host;
they are distinct from framework installation. PR render/config cases use supplied
records and offline transport; they do not establish Git-subject or live-provider
acceptance. The unpublished standards-promotion renderer is labelled experimental
and remains outside the released catalog.

Optional focused suites:

```powershell
python -I -B tests/run.py --suite loader
python -I -B tests/run.py --suite platform
```

`loader` checks verified source loading and bytecode-cache refusal with tiny
synthetic modules. `platform` requires Windows and checks simulated path/API
responses. See [coverage details](framework_next/README.md). Both remain separate
from native installation/apply/locking/interruption/recovery trials, which were
removed by owner decision. These tests also do not assess skill instruction
quality, agent outputs, downstream adoption, hosted CI or release publication.

The Source change gate uses Windows/Python 3.13 and the fixed default suites.
GitHub's native PR path filter selects only `src/**` and `tools/**`; no diff
classifier or changed-file count is used. Platform/loader remain optional local
checks. CI activation and each actual hosted result are separate provider facts.
`.github/` contains workflow callers and production release helpers; test
implementation belongs here. A green check does not complete independent review
or separately selected native/release acceptance.
Historical design, workflow and release reports retain their original evidence.
