# SIMPL-001 Controlled Context-Load Measurement

## Outcome

Five fresh, controlled session families loaded 38 repository-backed files or
runtime entries from the clean subject commit
`2e3c055050dbf2b2920ba80bc741c43799b359b6`. The exact loaded content totals
219,279 UTF-8 bytes and 25,481 whitespace-delimited words.

The repository corpus at that commit contains 1,170 regular tracked UTF-8 files,
4,783,210 bytes, and 476,339 whitespace-delimited words. That corpus is a
comparison boundary, not a prompt measurement. Provider-reported total prompt
tokens were unavailable and are therefore recorded as `null`.

| Session family | Load events | UTF-8 bytes | Whitespace words | Share of corpus words |
| --- | ---: | ---: | ---: | ---: |
| Runtime | 1 | 14,060 | 1,801 | 0.378% |
| Skill routing | 5 | 28,334 | 3,522 | 0.739% |
| Release | 15 | 78,798 | 9,162 | 1.924% |
| Handoff | 10 | 51,746 | 5,503 | 1.155% |
| Development | 7 | 46,341 | 5,493 | 1.153% |
| Combined evidence set | 38 | 219,279 | 25,481 | 5.350% |

The combined percentage sums five separate sessions and must not be interpreted
as one prompt. The 54,820-token value emitted by the measurement runner is only
the declared repository-loaded UTF-8 byte total divided by four and rounded up;
it is explicitly not total prompt usage.

## Active-Context Reduction

The root `AGENTS.md` entry was reduced from 2,067 words at the workflow bootstrap
commit `9ae5b2b` to 1,801 words at the measured subject commit, a reduction of 266
words or 12.9%. The change removes duplicate directory inventories while
retaining root safety, workflow gates, routing, precedence, approval boundaries,
and links to the owned indexes. `AGENTS.zh-TW.md` retains structural and
normative parity.

## Candidate Disposition

All seven Fable 5 candidates have an explicit disposition in
`candidate-dispositions.yaml`:

1. Historical evidence archiving is deferred to a separately approved,
   conditional v0.7.0 successor and cannot move, delete, or rely on Git-only
   recovery.
2. Bilingual root-entry work remains with `LANG-001`.
3. Wrapper consolidation remains with `ENF-001` and `SAG-001`; bulk generation
   is rejected.
4. Capability-skill collapse is rejected; `SKILL-001` owns taxonomy only.
5. Standards consolidation remains with `STD-001` and has no assigned release.
6. Template metadata is retained.
7. The bounded root-entry trim is implemented and measured here.

## Evidence And Reproduction

- Controlled trace manifest:
  `evidence/context-load-traces.yaml`
- Normalized measurement:
  `evidence/context-load-results.yaml`
- Runner:
  `tools/maintenance/measure-ai-context-load.py`
- Fail-closed tests:
  `.ai/scripts/tests/test_measure_ai_context_load.py`
- Reproduction contract:
  `.ai/evaluation/context-load/README.md`

The runner validates the exact clean subject commit, Git blob identities,
required session families, duplicate events, path safety, and the separation
between corpus, repository-loaded content, and provider prompt accounting.
