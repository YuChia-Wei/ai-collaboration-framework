# First selected P7 execution: observed repairs

This is coordinator triage of #368's actual run, not a fresh test run or
independent verification. Original reviewed source is
`38e6458f8d3e81dc2568daf1fa467571fb529fee`; the worker has returned partial
checkpoint `070a47335ffce99d31bd83e487447942539e4a9f`.
No aggregate passing outcome is claimed.

| Observation | Evidence and disposition |
| --- | --- |
| Initial F: parent preparation | Worker command `exec-b56800e1-b5c2-445b-9efc-d4faee56a60f` failed in `Path.resolve(strict=True)` at F:/framework-next with Windows error 1; the subsequent runner reported the still-missing output parent. No product case ran in that attempt. |
| Later real selected run | Worker command `exec-be023b8e-3bda-4754-a69c-bb289794798f` prepared only the exact F: binding with direct ancestor/link checks, then actually ran the selected tests. Candidate/real-Git paths and source metadata produced errors; helper and several negative cases ran. Full counts/final results belong to the worker's forthcoming fixed report. |
| PR/backlog metadata | Coordinator directly inspected tracked `src/skills/pr/skill-package.yaml` and `src/skills/local-backlog/skill-package.yaml`: both contain `&id001` / `*id001`; PR also uses `id002`. The worker reports the existing owner reader rejects these, as required. |
| Instruction expectation | The test incorrectly treated legitimate `authorized-target-editor` declarations as forbidden runtime probing. Correct the test to the accepted instruction metadata; this is not a product change. |
| GitSource path handling | The worker isolated strict F: path resolution as blocking real C3/C5 operations. Existing `git_source.py` is selected for a narrow source-identity-preserving repair; no native writer/recovery admission is accepted by that repair. |

The live #368 body was reconciled with provider updated_at
`2026-09-23T15:13:14+08:00` and its returned full body matched the update.
The original executor received that exact scope and must re-read the Issue.
This assigns only two metadata alias expansions preserving parsed types, list order,
versions, members, operations and resource identity, plus the existing GitSource
path repair. The loader must still reject anchors/aliases. No new package or engine
member, guarantee change, global monkeypatch, exception swallowing or C: fallback.
All other skill/installer files remain outside that task. This was coordinator
assignment, not evidence that the proposed writes were approved or executed.

A local coherent repair checkpoint may precede the final test checkpoint because
real GitSource/candidate tests must consume committed repaired bytes. Preserve the
failed original subject and disclose the new actual source. #370 reviews the
original fixed engine; changed EnginePin bytes need affected review later. Missing
runtime/native proof remains explicit. Root adoption and CI stay unperformed.

## Returned outcome and approval stop

The corrected test expectation and explicit no-alias regression were committed.
Final actual result: 14 methods, 11 successful, 3 affected methods producing 7
error instances, zero skips, exit 1. C5 built zero candidates. Detailed commands,
counts, times and retained F: residue are in the [worker report](../../2026-09-23-source-contract-checks/report.md).

Automatic approval rejected the attempted four-file batch before any product
mutation: `src/distribution/git_source.py`, `src/distribution/assembly.py`, and
the PR/backlog metadata. The stated concerns were that the Issue addendum did not
provide trusted expanded-source authority and that strict-resolution fallback
affected canonical-path protection. The product source diff remained empty.
The worker did not retry or use another writer/destination. The coordinator asked
for direct user confirmation in that same original #368 task. No response has
been received at this checkpoint; assignment and elapsed time are not approval.

The existing installation-state and public-entry strict-root operations also
remain a separate observed applicability concern. They are not silently added
to #368 or the cache-loader repair #371. Any shared path decision must preserve
link/reparse, identity and containment guarantees and retain affected review.
