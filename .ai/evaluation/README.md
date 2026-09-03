# Deterministic AI Behavior Evaluation

This directory owns the model-free behavioral regression corpus used by the
aggregate repository gate. The corpus consumes structured, preclassified facts;
it does not interpret natural language and it never calls a model, judge, or
network service.

Run the complete corpus and exact oracle:

```text
python .ai/scripts/validate-ai-behavior-evaluation.py validate
```

Write a normalized candidate result and compare it with the checked-in
baseline:

```text
python .ai/scripts/validate-ai-behavior-evaluation.py run --output candidate.yaml
python .ai/scripts/validate-ai-behavior-evaluation.py compare \
  --baseline .ai/evaluation/baselines/v1.yaml \
  --candidate candidate.yaml
```

The six fixture families cover empty, existing, and copied-template repository
initialization; software-development orchestration; customization-aware
upgrades; and identifier compatibility. Exact outputs are checked in under
`expected/`. Tests mutate the structured inputs to prove that missing routes,
unauthorized implementation, false test success, source-truth leakage, dual
provenance, and silent compatibility removal fail closed.

## Incident-Derived Fault Injection

`incident-mutants.yaml` composes the existing deterministic validators into one
measurable effectiveness gate. Its critical corpus covers the CTX-010
coordinated weakening, REL-016 semantic publication bypass, UPG-005 incoming
validator-chain break, identity substitution, and required-evidence omission.
Every mutant binds an exact candidate-input file set and raw SHA-256 before it
runs.

Run the release/nightly-bound fault-injection gate with:

```text
python .ai/scripts/validate-ai-behavior-evaluation.py fault-injection
```

An optional normalized report may be written create-only beneath the ignored
`.dev/ai-context/local/validation/` directory. Any surviving critical mutant,
unexpected critical detector, candidate-input drift, or tracked-worktree drift
fails the command. Exploratory survivors remain `survived`, carry explicit
follow-up text, and produce `passed-with-exploratory-survivors`; they are never
relabeled as detected or passed mutants.

Package-facing references use placeholders such as
`.dev/workflows/<workflow-id>/workflow.yaml`. Source workflow, assessment,
release, and backlog instances are not evaluation inputs and must not be
embedded in distributed corpus files.

Model-in-the-loop evaluation remains a separately approved release-side
activity. Model and judge selection, repetitions, sampling, thresholds, token
budgets, and stochastic result retention are intentionally outside this
deterministic contract.

## Repository Context Load Measurement

`context-load/` is reserved for source-release trace manifests and normalized
measurement results. It intentionally contains no trace or result until a
representative trace is approved and recorded; synthetic fixtures belong in
the validator test suite, not in this evidence directory.

Use the source-only measurement interface with a clean repository and a trace
manifest pinned to the full current `HEAD`:

```text
python .ai/scripts/measure-ai-context-load.py \
  --traces <trace-manifest.yaml> \
  --output <normalized-result.yaml>
```

A trace must contain exactly the `runtime`, `skill-routing`, `release`,
`handoff`, and `development` families. Every `runtime` or `full-file` event
pins a safe repository-relative path to its Git blob, byte count, and
whitespace-word count. The result separates the tracked UTF-8
`repository_corpus` from
the actual `repository_loaded` events.

`total_prompt_tokens` is recorded only when a provider reports it; otherwise it
is null. The deterministic bytes-divided-by-four heuristic is explicitly a
repository-loaded estimate and must never be described as total prompt tokens.
The source-only test suite uses disposable Git repositories and does not create
release evidence.
