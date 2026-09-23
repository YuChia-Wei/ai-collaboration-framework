# PR and local backlog contract checkpoint

Issue [#335](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/335), program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322). **Design checkpoint; source implementation remains pending.**

Read [contract](contract.md), [integration proposal](integration-proposal.json), [synthetic examples](examples.md) and the proposed schemas for [PR records](schemas/pr-record.schema.json) / [local work](schemas/local-backlog-record.schema.json). This subtree is source design evidence, not an installed package or activated backlog.

## Source binding

Starting commit: `a34ecd3c9423b17b6bb745f598ef22fd7437dd24`. The [assigned handoff](../../../workflows/2026-09-23-framework-redesign-control/handoffs/issue-335.yaml) selects this design boundary. Live Issue #335 was refreshed on 2026-09-23T08:13+08:00: OPEN; updatedAt 2026-09-22T18:11:35Z. Its scope still requires an early local checkpoint before product implementation.

Design inputs: P1 [portable contract](../portable-contracts/contract.md), [source layout](../source-layout/design.md), P2 [distribution implementation](../distribution-implementation/README.md), coordinator [P1 integration](../../../workflows/2026-09-23-framework-redesign-control/reports/p1-integration-and-p2-scope.md) and [P2 integration](../../../workflows/2026-09-23-framework-redesign-control/reports/p2-integration.md). Direct tracked source inspection covered Lesson metadata/configuration/operations and selected script functions, plus distribution package parsing and manifest.

Observed P2 restrictions: the Lesson config parser accepts only `skills.lesson` / `constraints.lesson`; package defaults are exactly store/template; no helper resource field exists; derived roles require a project record; distribution selects exactly declared members and requires implemented entrypoints. No product execution established these observations.

The current source repository still uses live GitHub Issues under `.dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml`. Historical `.dev/backlog` is not reactivated. Source policy, U001, this design and workflow records are excluded from proposed package members.

## Handoff boundary

The contract subtask may complete after its local commit. Overall workflow and Issue remain in_progress. The coordinator reconciles WM-C1/C2/C3, then resumes this same task with explicit source ownership. Product implementation, schema/behavior acceptance, package/install trials and CI remain outstanding; U001 assigns verification to program coordinator / P7.