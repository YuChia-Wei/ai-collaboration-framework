# Validation and acceptance evidence

Scope: #452 AC01-07. Base: d334805b60b51574a94ce1634fbdf8158bbed406.
All evidence below is local Windows source evidence until stated otherwise.

## Author checks before the first immutable commit

| Check | Actual outcome |
| --- | --- |
| `python -I -B tests/run.py --suite distribution --suite schemas` | passed: 117 tests, zero failures/errors/skips, runner 10.893747 seconds |
| `python -I -B tests/run.py` | passed: 243 tests, zero failures/errors/skips, runner 67.380344 seconds |
| `git diff --check` | passed |
| Author inspection | New method/expression resources and optional BDD routing; exact dependency version closure synchronized. Corrected an overbroad manual replacement that briefly attributed BDD/Gherkin coverage to slice-implementer. No package behavior failure was observed. |

Full source stdout/stderr are retained locally under the ignored
`.dev/ai-context/local/bdd-452/` evidence root. The focused run is retained in the
conversation output. These tests do not execute installed-resource consumption
or judge agent instruction quality. No new tests that only mirror prose were added.

Initial discovery had stale graph coverage despite a current Git identity;
known current tracked paths were used as explicit fallback, and
`src/distribution` was reindexed as `bdd452-distribution` before further discovery.
Two path/PowerShell syntax lookup errors were corrected without product changes;
they are preparation errors, not failed product acceptance.

## Historical checkpoint at the implementation commit

- AC01-03: author inspection of the new resources; independent content review pending.
- AC04: fixed B1-B4 prompts and expected judgments are in workflow-plan.md; actual agent runs pending.
- AC05: source declarations pass; actual catalog/subset/install/reader checks pending.
- AC06: preserved GWT handoff and .NET rule bytes; independent immutable review pending.
- AC07: separate evidence states retained. Hosted CI, real-project adoption, release,
  parser/runner execution and token measurements are not performed.

The source-owned workflow is still in progress. No Issue completion is claimed.

The paragraph above describes the implementation checkpoint, not the later
local-delivery disposition below.

## Fixed source and independent review

Implementation commit: `c9439c1d29c21fe27f0415b62c910e9aabffe790`.
Independent reviewer: `/root/bdd_immutable_review`, separate read-only context,
using the installed code-reviewer and current source policy. It reviewed the
base-to-implementation immutable diff against live #452 AC01-07 and the fixed
workflow plan. No supported actionable defects were found. It did not implement
or repair the subject. HEAD and tracked cleanliness were unchanged across review.

The reviewer independently checked the method against official Cucumber sources,
the optional-consumption boundary, unchanged GWT handoff and .NET normative
content, 22 common-package members against the manifest, and 10 consumption
declarations containing 36 resource references. It did not rerun author tests or
claim installed/behavior acceptance from static evidence. Those gaps are addressed
by the separate evidence below. This review is a scoped content conclusion, not
hosted CI, maintainer PR acceptance or release approval.

## Actual isolated catalog, installation and reader evidence

The ignored driver `prepare-package.py` under `.dev/ai-context/local/bdd-452/`
exported the Engine from the fixed commit and called the existing
`tools/build-catalog.py --repository <source> --commit <fixed-commit>
--release-version 0.0.0 --engine-pin <external-pin> --output-root <fresh-output>
--scratch-root <fresh-scratch>` with `python -I -B`. The synthetic `0.0.0` label
allocates no release. Assembly passed in 68.252471 seconds.

Catalog identity:
`catalog:1:0.0.0:c9439c1d29c21fe27f0415b62c910e9aabffe790:3c797304f2bf3fa55b1d02b915dd557a3eace1b1c8fc445c99cc736c90e592c3`.

The packaged `src/tools/derive-subset.py` and `maintain_framework.py` ran as
isolated Python subprocesses from the external trial root. Exact external Engine
pins, explicit selections and saved plan hashes bound each operation. Both
consumers began empty, had no competing writers or sessions, and followed
inspect -> plan -> reviewed exact additive plan -> apply -> inspect. No unknown
files, project data or protected inputs were changed. Saved request/response
files retain exact argv, pins, declaration and outcome.

| Evidence | BDD + common | BDD only |
| --- | --- | --- |
| Derive / initial inspect / plan | passed / uninstalled / planned | passed / uninstalled / planned |
| Apply | applied, 28 added members | applied, 6 added members |
| Final inspect | managed-bytes-consistent; no drift | managed-bytes-consistent; no drift |
| Payload bytes compared with committed source | 26 matched | 4 matched |
| Codex / Claude runtime entries | both assembled and installed | both assembled and installed |
| Verified installed knowledge resources | 21, including both new guides | 0 |
| Saved knowledge bindings | one optional, knowledge-only binding | none |

Common subset:
`subset:3:0.0.0:c9439c1d29c21fe27f0415b62c910e9aabffe790:24f0880fa57752640c1fc57230ba913ac79ee086ce80b59c5c61545200a82088`.
BDD-only subset:
`subset:3:0.0.0:c9439c1d29c21fe27f0415b62c910e9aabffe790:073a02410b02e9c45d2ec306058e09fd5887f587f4a813f3f43d2690b0a7d292`.

| Pin | BDD + common | BDD only |
| --- | --- | --- |
| Plan SHA-256 | `152695b322875472100f8378e2acd29154e50743bd61a263ffd157b1b3e6c433` | `2466a03f9b5ff3428878ce8cdcb657721c4d58416403e80f032db7333191e871` |
| Installed lock SHA-256 | `4f8224d6d037f9edb331e545bae50452365c36dac8b8b23ed6cea9bcc903e426` | `e233116437e3304f9460f7945a6b91774667b8893aacf77c757a90254a4c357a` |

The source-owned read-only host authenticated the packaged bootstrap and Engine
against the selected external pin before calling packaged
`distribution.catalog.read_installed_resources(project, expected_lock_sha256, [])`.
The reader returned verified inventory and saved selectors; it does not implement
semantic applicability. Parent and actors selected the relevant installed resources.
All returned member bytes were independently hashed. Both new resources also
matched the committed source: BDD-METHOD
`65dd5669a4b06f6b00abcec5a3c273b4cc4d2920b767201da5f4cbf82ae4f4d4`,
GHERKIN-SCENARIOS
`53943e3d23a62242a3320692b3c6fc0b085f7d24dd60047d598e3edf2093f154`.

Raw local evidence remains in `C:\b452-74060e5c`: catalog/subset outputs,
external pin, selection files, exact requests/responses, installed consumers,
`common-resources.json`, `absent-resources.json` and `installed-summary.json`.
These are disposable test consumers, not real downstream adoption. The host
selected `windows-inventory-only` and process-termination durability; native
filesystem mode/recovery, power-loss durability and product readiness were not
assessed. Generated Claude entries were not executed by a Claude runtime.

## Actual agent behavior and retained limitations

The fixed expected judgments were committed before the actors ran. Actors were
given installed inputs and prompts, not that answer table. Parent remains the
acceptance judge. Initial actors reused the gpt-6.1-sol/low inventory contexts:
`/root/bdd_source_inventory` for B1-B3 and `/root/bdd_chat_inventory` for B4.
Their output content is retained in
[common attempt 1](evidence/behavior-common-attempt-1.md) and
[BDD-only output](evidence/behavior-absent.md).
`evidence/artifacts.json` records local capture hashes before Git line-ending
normalization; the original bytes remain in the external trial root.

Common attempt 1 generated supported outputs, but loaded both method and Gherkin
resources together. It cannot establish negative-read isolation for B1 or B3.
That evidence limitation is retained, not passed. Parent selected one materially
changed second attempt for each: separate fresh contexts, one case per actor,
same installed bytes and prompts, and pre-read verification. No product edit or
unbounded retry was made. The initial instruction display also preceded member
comparison; hashes were checked before outputs and afterward. B4 retained an
initial inventory-shape bookkeeping error, corrected to `inventory.files`, and
an entry display before verification followed by verified reread. Neither was
installed-byte drift; neither proves an entirely verified first-read sequence.

B2 is usable formulation evidence from the first report: independent L7/Ada/Ben
setup, a renewal request, refusal plus unchanged 20 October due date, R1/AC1
mapping, and no inferred positive/overdue rule or runtime claim. B4 is usable
optional-absence evidence: zero resources/bindings, no source fallback, a bounded
GWT scenario with both outcomes, and explicit unavailable knowledge coverage.
These conclusions do not depend on claiming perfect first-read verification.

Fresh B1 actor `/root/bdd_discovery_sample` used gpt-6.1-sol/low with no inherited
conversation. Its [raw report](evidence/behavior-b1-isolated.md) records the
verified entry/core/metadata/design instruction reads and only BDD-METHOD as
knowledge. Gherkin and handoff resource contents were not read. It retained the
overdue policy as unknown, supplied questions and provisional probes, and did
not produce scenarios or adopt the illustrative reservation rule. All five
consumed members and the pinned lock matched before reads and after output.
Parent judgment: B1 satisfies the fixed discovery-only case.

Fresh B3 actor `/root/bdd_combined_sample` also used gpt-6.1-sol/low with no
inherited conversation. Its [raw report](evidence/behavior-b3-isolated.md)
records only BDD-METHOD as knowledge, the same five verified installed members,
and no Gherkin or handoff content read. It reused R1/AC1 in scenario notes,
preserved refusal and due date, and left overdue/no-reservation outcomes
unresolved. The conditional test-level advice did not invent target ownership.
Before/after hashes matched. Its first lock-data display was unnecessarily large
and truncated; subsequent selected-member reads were bounded. Parent judgment:
B3 satisfies the fixed combined case; no token-efficiency claim follows.

| Fixed case | Parent disposition | Evidence boundary |
| --- | --- | --- |
| B1 discovery only | passed on isolated attempt 2 | BDD method only; rules unknown; questions/provisional probes; no scenarios |
| B2 scenarios only | passed on attempt 1 | Requested Gherkin and both observable outcomes; batch-read limitation retained |
| B3 combined | passed on isolated attempt 2 | BDD method only; supported scenario notes and explicit unknown policy |
| B4 knowledge absent | passed on attempt 1 | Installed design + caller inputs; no knowledge or source fallback; optional coverage unavailable |

These are actual sampled agent instruction outcomes, not automated product tests,
statistical reliability, parser validation, model-wide guarantees or token savings.
The two fresh samples establish the specific no-Gherkin-content-read cases. A
metadata index listing a resource is not a read of its content. No claim of
token savings is made from that distinction.

## Acceptance disposition and local delivery

| Criterion | Local disposition | Evidence |
| --- | --- | --- |
| AC01 | passed | Two source resources; official-source comparison and independent content review |
| AC02 | passed | Optional knowledge, operation and target/profile boundaries inspected; installed samples preserve them |
| AC03 | passed | Concrete examples/counterexamples; source/status mapping and unknowns confirmed by review and samples |
| AC04 | passed with retained attempt limitations | Fixed B1-B4 samples above; first common batch is not negative-read proof |
| AC05 | passed within selected local installation scope | 117 focused checks, actual catalog/subsets, two apply/inspect results, verified reader and source-byte closure |
| AC06 | passed | Immutable diff: GWT handoff unchanged; .NET and other consumers only required version metadata changes |
| AC07 | passed | Evidence layers, preparation errors, retry rationale and all unperformed scopes explicitly retained |

Local implementation and validation are complete. Source tests and independent
product review bind to the implementation commit. The delivery commit changes
only this workflow's evidence and task state: deterministic Git comparison must
confirm every path outside this workflow remains identical before reuse. No
test command, runner, dependency, policy or configuration changed. Product review
is reused for that unchanged subject; current workflow records receive author
inspection, JSON/YAML relationship checks, Markdown link checks and diff checks.
The complete planned message and authored commit range are validated separately.

Next owner is the maintainer for separately authorized push/PR/integration. This
source diff will select hosted `Source change gate` when a PR is created; hosted
CI is currently not run, not passed. Issue #452 remains open. No real-project
installation, source-project self-upgrade, downstream adoption, parser/runner
execution, publication or release acceptance was performed.
