# Domain and software architecture split — local implementation

Current continuation: see the [external review handoff](workflow-plan.md#macos--claude-opus-handoff).
The original local delivery below is historical evidence; subsequent installation,
review and correction are recorded at the end of this document.

## Subject and scope

The accepted design was reviewed before source edits. The implementation follows
Feature #476 and Stories #477–#480 on `codex/plan/skill-evolution-20261022`.
The original implementation subject is 51865868a50233d734f1140c7e11ce8fe80cd21d;
its reviewed instruction correction is 589abfcd97d8e145d8d9930814904b17bc05f2c7.
The [independent source review](source-review.md) records full coverage and F1 disposition.

- Added `domain-model-designer@0.1.0` (explore/design/review) and
  `software-architect@0.1.0` (design/review); removed the old combined source
  package and current manual without an alias or runtime retirement router.
- Reconciled requirement, Story, spec, test and orchestrator ownership. Business
  consistency requirements remain with the domain owner; technical mechanisms
  and feedback remain with the software owner. GWT notation does not transfer
  authorship to the test designer.
- Updated metadata-4 optional knowledge, exact pins and source resource closure:
  engineering-common 0.4.0 and dotnet-backend 0.1.5, including its required common
  dependency. Four affected presets are 0.2.0; knowledge remains explicitly empty.
- Updated the 21-row source skill catalog, nine-consumer knowledge matrix,
  migration guide, neighboring manuals and bilingual root navigation. The
  existing 17-skill installed snapshot remains separate and unchanged.
- Added three source-backed distribution tests for independent/combined selection,
  retired-ID rejection and representative operation/resource binding validity.
  The read-only customization-assessment delegate contributed a test draft;
  the parent adapted and wrote all tracked changes.

## Actual validation

`python -I -B tests/run.py --suite distribution --suite schemas` completed with
exit 0: 130 tests, 0 failures, 0 errors, 0 skipped (15.222 seconds test time;
16.209 seconds runner time). This covers source metadata, manifests, member
closure, subset selection, adapters, schemas and the new resolver/binding cases.
The three new tests exercise both new skills alone and together with no knowledge,
common knowledge, or common plus .NET knowledge; the retired ID is rejected by the
catalog resolver; domain explore, Story plan and spec formulation bindings are
validated, including an invalid Story-plan/formulation combination.

F: was not ready when rechecked. Test scratch was scoped to this task under the
ignored `.dev/ai-context/local/domain-split-tests` directory using only that
command's TEMP/TMP environment; no machine-wide settings were changed. After this
run, documentation/protocol wording and semantics-preserving metadata
format/comment restoration changed. The later F1 spec-guide instruction correction
received bounded independent semantic review; it changed no metadata/member/parser
contract. No additional distribution/schema test was triggered.

A bounded local-link check found 286 valid file links in 48 changed/new Markdown
files. All 21 table versions match source package metadata. The four changed
preset versions, skill counts and replacement IDs match source files.
`git diff --check` passed. New and changed English/Traditional Chinese root
navigation were compared for structural and normative parity. Final closeout
checked 366 existing file links across 63 changed/new Markdown files (anchors
excluded), all three terminal/addressed task records and local workflow status.
The reviewed product source remains identical to 589abfcd; installed projections
remain identical to the original baseline.

These are local mechanical and author checks. Independent review covered all 13
criteria and four specified walkthroughs; one P2 guide contradiction was corrected
and independently verified resolved. The source review and these checks do not
establish model-output quality, runtime
invocation, downstream installation, hosted CI or release acceptance. No full
model/native/E2E/installation matrix was selected: no affected engine or installer
behavior and no such acceptance criterion was added by this change.

## Delivery limits

Source implementation does not install the new skills in this project. Managed
`.ai`, `.agents` and `.claude` projections were not edited. The original untracked
2026-10-19 and 2026-10-20 workflow directories remain outside this change.

Future local-workflow integration (#481/#483) and customization upgrade design
(#482/#484) were documented and filed only. No implementation was done for them.
Push, PR, merge, hosted CI, Issue closure, Project fields, self-installation,
downstream upgrade, tags, release and publication remain separate actions outside
this local delivery. No provider state is inferred from local tests.

## Owner-authorized Preview review and wording follow-up (2026-10-22)

Continue Feature #476 and Stories #479/#480. The owner authorized applying the
current source to the existing F: Preview, an Antigravity Gemini 4 Argon review,
then both optional wording corrections and a branch push for macOS / Claude Opus
review. No new Issue is created and no Issue is closed.

### Observed installation and external review

- Installed subject: 438b15eb5947d4b49a5c1f7f3d293f53cba32fa7, synthetic 0.0.0.
- Target: `F:\AICF-Release-Preview`; 21 skills, two knowledge packages,
  two adapters and six existing role definitions. Replacement selection was
  explicit; bindings remained empty.
- Apply reported 17 added, 46 changed, 6 removed and 450 unchanged files.
  Independent inspect before and after review reported managed-bytes-consistent,
  no drift; six non-managed files retained their hashes.
- Google official PowerShell installer installed Antigravity CLI 1.4.4 at
  `C:\Users\h4227\AppData\Local\agy\bin\agy.exe` and updated user PATH.
- CLI init observed `gemini-4-argon-medium`, target cwd and request-review
  permissions. Conversation: `1599d8dd-bf85-4de1-a8b1-a51add53640d`.
  Final status SUCCESS, exit 0, duration 522.7905823 seconds; all 185 completed
  tool calls were read_file. No delegated agents, repairs or runtime skill tests.
- Reviewer reported no actionable findings in its reviewed scope, plus O1/O2
  below. Its report addresses 13 criteria and four walkthroughs as static
  instruction review, not runtime acceptance.
- Important limitation: 33 report line-range citations (including repeats)
  exceed actual file lengths. For example, it cites code-reviewer/SKILL.md through
  line 78 although the installed file has 34 lines. Its complete-coverage and
  citation claims are not independently accepted. Preserve this limitation;
  macOS review must read actual files and report its own evidence.
- Windows-only original report and evidence are at
  `F:\AICF-Preview-Notes\2026-10-22-gemini-4-argon-review-original.md` and
  `F:\AICF-b\438b15eb\review-receipt.json`. They are not Git artifacts or
  prerequisites for the receiving reviewer; this summary supplies the relevant
  outcome, limitations and dispositions without those machine-local files.

### Accepted suggestions and source correction

| Suggestion | Verified source and disposition |
| --- | --- |
| O1 | `src/skills/software-development-orchestrator/SKILL.md`: clarify that 0.2.0 identifies the historical restoration, rather than the current package version (0.4.0). Preserve retirement of 0.1.0 record tools and evidence boundaries. |
| O2 | `src/knowledge/dotnet-backend/design/source-map.md`: explicitly distinguish domain-model-designer and software-architect; use common resources for the selected responsibility and .NET hotspots only when the target/task requires them. No new capability, selector, binding or authority adoption. |

Both statements were verified in actual files before editing. Changes remain in
editable source; neither generated source-project entries nor the Windows Preview
were hand-edited. The Preview review applies to 438b15eb, not this later wording.
Package versions remain the accepted, unreleased source versions; no new version
allocation, publication or installation occurred in this follow-up.

Validation decision: inspect the two changed sentences, their existing links and
the handoff/locator; run git diff --check and validate the exact commit message.
No executable/schema/selection contract changed, so no new product test or repeated
AI evaluation is selected. The earlier 130-test result and fixed-source review
retain their original subjects and limits. Hosted PR CI and macOS / Claude Opus
review are pending; pushing a branch does not establish either result.

Follow-up checks: git diff --check passed; YAML locator parses and its entrypoint
exists. The initial blanket main..HEAD workflow-message check rejected 4ade82bc
because that design commit predates this workflow and has no Workflow section.
No history was rewritten: ordinary --commit 4ade82bc validation passed (1 commit),
and --range 4ade82bc..HEAD --workflow-id 2026-10-22-domain-architecture-split passed
for the five existing workflow commits. The new handoff message is separately
validated with the workflow identity before commit.
