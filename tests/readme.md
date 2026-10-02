# Framework tests

Run from the repository root with Python 3.10+ and existing PyYAML 6.x,
jsonschema 4.x and referencing. Dependencies are explicit; the runner installs
nothing. Use an ordinary writable OS temporary directory; no F: drive, fixture
root setting, Git repository fixture, candidate build or installation is required.

```powershell
python -I -B tests/run.py
python -I -B tests/run.py --suite schemas --suite tools
python -I -B tests/run.py --suite distribution
python -I -B tests/run.py --suite release --suite source
```

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
| `source` | `source/`, `test_runner.py` | Dormant selector safety, current ownership, runner selection and rejection of false success |

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

CI activation remains a separate owner decision. `.github/` contains workflow
callers and production release/gate helpers; test implementation belongs here.
Historical design, workflow and release reports retain their original evidence.
