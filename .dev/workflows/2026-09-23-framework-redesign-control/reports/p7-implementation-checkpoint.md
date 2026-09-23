# First P7 implementation checkpoint

This is coordinator integration, not independent validation or P7 acceptance.
U001 and the [selected plan](../../../design/framework-next/p7-execution-selection.md)
remain effective. CI, root adoption and native installation are unperformed.

| Issue | Fixed return | Actual result and remaining work |
| --- | --- | --- |
| #368 | `070a47335ffce99d31bd83e487447942539e4a9f` | 12 added files; final contracts exit 1, 14 methods / 11 successful / 3 affected methods / 7 error instances / zero skips. No candidate built. Product repair is approval-blocked. |
| #369 | `5ee20036392b6ad217e4029c8a256e176e9d8cdf` | 10 added files; 24 focused selector/event tests passed in 1.733 s after a separately approved fixture-only correction. Policy writes remain approval-blocked; product/native bindings incomplete. |
| #370 | `6de20bfeb059d74f1ba0ede96c28d312db04235f` | 3 review records; fixed product `38e6458f8d3e81dc2568daf1fa467571fb529fee`. One P1 source finding, CR-001. No product or native execution. |

Worker source reports retain the first F: strict-resolution failures. Later
helper/selector success does not erase them or establish native support. The
#368 final run took 3.483 s (3.529 s helper lifetime), with 11 known child
launches and 7 final logical files / 434 bytes; earlier tiny helper probes add
2 files / 31 bytes. These are authored logical observations, not physical SSD
or cumulative I/O measurements. Two failed unique F: directories remain named
in the worker report. No broad cleanup or drive substitution was performed.

## Fixed-return inspection

The coordinator inspected all 25 changed files at their fixed Git subjects:
strict UTF-8, direct AST/JSON/YAML syntax, Git whitespace/scope and 23 local
Markdown references passed. No product modules were imported by these checks.
All files are additions; no product source, existing policy/root entry, PR
template or seven legacy workflow was changed. Worker behavior tests were not
rerun without a source change. These checks do not certify schemas or runtime
behavior. The source gate's pinned both-tree selection, event/head and command
result paths were inspected; its explicit pending bindings remain non-passing.

## Approval stops and unaffected continuation

#368's attempted GitSource/assembly/two-metadata batch was rejected because the
Issue addendum was not trusted expanded-write authority and path fallback
affects canonical-path protection. #369's governance/AGENTS/policy/template
batch was rejected for missing trusted authorization of persistent policy
changes. Both stopped before the rejected writes. The coordinator requested
direct confirmation in their respective original conversations; no reply has
been received at this checkpoint. Neither batch is reassigned or bypassed.

#369 may separately bind only its existing source-gate code and synthetic
command tests to #368's actual fixed runner interface. It must not invent a
JSON success contract. Public/native layers stay explicitly unavailable until
their actual deliveries. Rejected policy writes remain stopped. That follow-up
uses the original #369 task and has not returned at this checkpoint.

## CR-001 disposition

[The independent report](../../2026-09-23-installation-source-review/report.md)
finds that normal Python loaders can use existing valid local bytecode after
the bootstrap has verified only `.py` bytes. Expected module origins and
source hashes can match while different cached code executes. This is a
high-confidence source finding; runtime reproduction is unexecuted.

[Issue #371](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/371)
owns a bounded repair to the public bootstrap: compile the exact verified
source bytes for every allowlisted local module, with unchanged pin membership,
host dependency and path boundaries. Its new focused loader tests and at most
one N1 public-entry attempt are selected; a pre-existing F: refusal must remain
visible. It cannot modify the stopped #368 files or any path policy. The
original #370 task will independently inspect changed source after delivery.
CR-001 remains unresolved until that evidence exists. #370 stays open for the
affected review; #368/#369 remain open for their missing work.

## Integration boundary

The coordinator preserves all referenced commits in the local integration.
The planned online checkpoint uses Refs #368/#369/#370/#371, without closing
unfinished Issues. New workflow definitions remain dormant under disabled
repository Actions. No hosted pass, policy activation, P7 exit, root adoption,
release or downstream acceptance follows from merging this checkpoint.

## Contracts binding follow-up

The original #369 task returned `6c5f4a298bc3ffdbea47348ae6ef8c9f4584b41d`:
9 changed files, actual fixed #368 `--layer contracts` command and exit/unittest/
observation parsing, plus explicit dormant dependencies. Its 28 focused tests
passed, zero skips, 2.441 s; the new subprocess responses are synthetic, not
product execution. The prior 24-pass checkpoint remains preserved. Coordinator
inspection of the 9 fixed files and 9 local references passed direct syntax,
whitespace and scope; no test rerun was needed. Public/native remain explicitly
unimplemented/non-passing. Policies/root/template remain untouched.

#371 is active in task `01a0cd2f-f89d-7381-a3cd-1e73ce02d8aa`, verified runtime
`gpt-6-astra` / `ultra`, F:/framework-next/371 at starting commit
`fe6c63f87cb54e166fc796fd315f11e3c2212823`. Its actual first Git command targeted
that F: checkout. Live Project read-back shows OPEN / In progress with only
Status selected. Source repair and affected review have not returned yet.

Before transport, provider read-back at `2026-09-23T15:35:12.2652819+08:00`
showed Actions disabled, all seven legacy workflows disabled_manually, and main
`01aeb8ae4f18132dfdd7ad3479346c78b9f5f913`. The final transport read-back remains
a separate observed step; these historical settings are not a hosted pass.

## Online transport and corrected provider state

PR #372 merged at `3a21b0eb58e80752df010e7277aec55725b3061e`. Read-back at
`2026-09-23T15:40:20.1687996+08:00` confirmed MERGED, main equal to that SHA,
Actions disabled and checks empty (not passed). New workflow IDs 364914272
(source-checks.yml) and 364914274 (source-native.yml) registered active under the
repository-wide suspension; the coordinator then explicitly disabled both under
the owner's all-CI-stop instruction. All nine workflows were read back as
`disabled_manually`. This changes the future restoration inventory: the adopted
new IDs must explicitly be enabled, in addition to any owner-adopted Actions
setting. No workflow was executed or policy activated.

An unintended provider transition was discovered, not hidden: GitHub's closed
event for #368 at `2026-09-23T07:39:52Z` cited coordinator commit
`fe6c63f87cb54e166fc796fd315f11e3c2212823`. Its prose placed the keyword `fixed`
immediately before the Issue reference, causing automatic Issue closure and
Project Done despite the explicit deferred PR disposition. The coordinator
reopened #368 and restored only Project Status to In progress; live read-back
confirmed OPEN / In progress. No product acceptance was inferred. Future commit
prose must be checked for unintended provider closing syntax before push; keep
these published referenced commits intact rather than rewriting history.

The already merged coordinator branch was removed locally and remotely only
after ancestry/clean-state proof, with the remote deletion bound to expected SHA
`61eaa81653b34d3b2142a40ace3bebac45068e8a`. Active Issue branches and every F:
worktree/file remain preserved. Continuation uses
`codex/2026-09-23-p7-source-pin-control` from the online merge.
