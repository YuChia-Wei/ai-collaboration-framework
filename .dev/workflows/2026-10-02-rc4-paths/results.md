# RC4 path audit and repair evidence

## Subject, authority and delegation

Audit source/tag: `158b8438f61a60eb621e3a5b43ed1a0479634f6f` /
`v0.19.0-rc.4`. Three actual read-only invocations used `gpt-6.1-sol`, effort
`high`: `rc4_product_paths`, `rc4_doc_paths`, `rc4_tool_paths`. Root reviewed
all three reports and is the sole tracked writer/integration owner. Agents
read root/source policy and applicable auditor/reviewer instructions. No agent
modified files or provider state. These inventories are not the independent
review of the later authored repair.

The graph returned removed roots with missing identity/coverage fields for tool
discovery. Fixed-tree `git ls-tree`, `git show`, `git cat-file --batch`, scoped
path-string searches and read-only Python/YAML/AST/ZIP/hash checks supplied the
explicit tracked-file fallback. Markdown scanning used exact Git path case;
Windows filesystem tolerance was not treated as Linux path proof.

## Findings and disposition

| Partition | Actual evidence | Parent disposition |
| --- | --- | --- |
| Product source / downloaded RC4 | 388 tracked files; 379 delivered product/adapter files equal raw source blobs; 9 standards-promotion files intentionally excluded. 20 metadata files, 1505 declared path checks, zero missing/case mismatches. 57 routing/recipe checks resolve. | No supported product-impact finding; preserve tag/assets. |
| Product prose / archive | 359 source and 345 package link candidates inspected. Adapter variables, C# syntax and semantic-owner-relative normative links distinguished. 408 content hashes match; ZIP has 409 files, no duplicate/case collision, exact extraction parity. | No product repair; do not change correctly based semantic links. |
| Current source docs | 158 Markdown files, 479 inline links including 447 local links; 24 broken links in 12 source standard/navigation files. No missing reference-style definitions. Code-span/rooted discovery candidates separately triaged. | Replace missing guide index, remove 25 absent current catalog rows, correct root release paths, point authoring resources to verified managed files, qualify historical asset links and unavailable command examples. |
| Source tools/build | 405 manifest component/profile inputs, adapter members, both 24-file engine lists and relative engine imports resolve. Seven test suites resolve. | No RC4 builder/engine path defect. |
| Source CI selector | Existing `.dev/INDEX.md` and `.dev/workflows/INDEX.MD` lacked selected owners. | Add exactly those source-governance paths with source suite and independent review; tests retain rejection of unknown neighboring paths. |

The removed `.ai/assets` projection links retain their historical path names and
ownership meaning, but are no longer clickable promises of present files.
Current `src` sources and `.ai/core` managed projections are identified only
where the existing root/boundary authority already selects them. No legacy
semantic authority is redirected to a new package.

## Retained unavailable legacy surfaces

These source-only implementations are outside the catalog and Engine 2 closure.
Current source policy retains legacy duties without restoring their tools:

- `tools/maintenance/execution_artifact_contract.py:16` imports missing
  `artifact_core`; dependent old guardrails and terminal validators cannot load.
- `src/tools/dotnet/check-coding-standards.sh` needs removed `.ai/assets` and
  `.ai/scripts` trees. Two other retained .NET scripts, `check-dotnet-config.sh`
  and `validate-dual-profile-config.sh`, traverse `../..` from their new location
  to `src`, not the repository root. These unselected legacy target checks are
  not current framework validation commands. Correct target-root semantics and
  an available content closure need the separately selected restoration owner;
  this source-navigation repair does not revive them or claim they pass.
- The old Python entrypoint registry contains 38 absent paths among 47 rows.
  Existing launchers do not establish those legacy entrypoints are available.
- Six old workflow definitions retain legacy paths. Current adopted policy
  keeps them disabled; this audit does not activate or repair them.

## Actual checks and retained failures

- `python -I -B tests/run.py --suite source`: 46 passed, zero failures/errors/
  skips, 2.417278 seconds on the authored working tree before its first commit.
- Root changed-Markdown check: 33 local links and all 58 current `.dev/INDEX.md`
  table paths resolve case-exactly against the Git inventory; zero missing paths.
- Pinned old-selector reproduction at the base returns `unknown ownership` for
  `.dev/INDEX.md` and `unknown workflow identity` for the workflow index. The
  new regression selections require the source suite and independent review.
- `git diff --check`: passed. `git diff --name-only -- src` and the selected
  engine/build entrypoints: empty; no product/builder bytes changed.
- Draft build run `37000062722` was read back completed/success on the tagged
  source. Its ZIP SHA-256 is
  `db505854a2f355632e71a356ae8c4b85778880be4caee409e6557eca07ed5c4c`.
  Prior Source change gate `36973123695` succeeded at
  `f4480f6a34f9d729f14f492c7e00337c42874f11`; `git diff --quiet` proves that tree
  equals the release source. This is prior source evidence, not a new test run.
- Preparation lookup of a guessed `RELEASE-POLICY.md` failed; actual tracked
  `AI-CONTEXT-SOURCE-RELEASE-POLICY.md` was selected and read. One multi-file
  patch failed on the exact Chinese line; read-back confirmed no mutation,
  then the corrected exact-line patch succeeded.
- Agent utility failures retained: one Windows wildcard `rg` call corrected to
  directory plus `-g`; a supplementary semantic-owner helper failed twice on
  differing YAML owner shapes and was not retried a third time. Direct .NET
  owner checks and ordinary common-catalog link inspection supplied the bounded
  evidence; no checker failure was relabeled a product failure or a pass.

Fixed-commit affected gate, independent repair review, final hosted CI, merge
and public prerelease read-back are pending at this initial record. Static
path/closure checks do not establish anchors, external URLs, native runtime,
actual agent scenarios, downstream acceptance or full P7 completion.


## Fixed-subject validation and independent repair review

`python -I -B .github/scripts/check-source-change.py --base
158b8438f61a60eb621e3a5b43ed1a0479634f6f --head
35c3bbe6389123e673bf983d298f90323c9aed68` passed content, whitespace and source:
46 tests, zero failures/errors/skips, 22.765 seconds total. Admission separately
requires independent scoped review; the gate reports admission not evaluated.

Independent read-only reviewer `rc4_tool_paths` (actual `gpt-6.1-sol/high`
invocation; no repair authorship) reviewed the full 33-file diff against source
policy rule 6, exact path resolution, bilingual parity, preservation of legacy
semantic authority, restricted selector ownership, product/build/managed byte
invariance and truthful workflow/publication state. It found one P3 residue:
`.dev/workflows/INDEX.MD` still linked to removed `.dev/backlog/INDEX.MD` in its
current Related Discovery section. This pre-existing link is inside the touched
navigation surface. It is now retained as an explicitly unavailable historical
path. The finding is preserved here; affected review of the correction is next.
The reviewer otherwise found no supported actionable defect. It checked 377
local links across complete changed Markdown files (one missing link above), all
58 project index rows, fixed source identities and local tag state. Tests,
build, native execution and provider calls were not performed by the reviewer.
Its initial unquoted PowerShell tag-peel lookup failed; the corrected Python
subprocess succeeded. This preparation failure is not a product failure.

Parent fresh provider observations: main remains the original release source;
no ruleset and main unprotected. Source checks plus snapshot/draft workflows are
active; the other six workflows remain disabled. No settings changed. Original
RC4 assets were downloaded again to a fresh directory and all three provider
sizes/digests, original local bytes and 409 manifest entries matched. Release
401752316 remained draft=true/prerelease=true. No publication has occurred yet.
