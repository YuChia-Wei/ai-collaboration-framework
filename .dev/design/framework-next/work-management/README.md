# PR and local backlog contract checkpoint

Issue [#335](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/335), program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322). **Bounded source implementation complete; execution verification deferred-by-owner to P7.**

Read [contract](contract.md), [integration proposal](integration-proposal.json), [synthetic examples](examples.md) and the proposed schemas for [PR records](schemas/pr-record.schema.json) / [local work](schemas/local-backlog-record.schema.json). This subtree records source design and selected implementation; it is not an installed package or activated backlog.

## Source binding

Starting commit: `a34ecd3c9423b17b6bb745f598ef22fd7437dd24`. The [assigned handoff](../../../workflows/2026-09-23-framework-redesign-control/handoffs/issue-335.yaml) selects this design boundary. Live Issue #335 was refreshed on 2026-09-23T08:13+08:00: OPEN; updatedAt 2026-09-22T18:11:35Z. Its scope still requires an early local checkpoint before product implementation.

Design inputs: P1 [portable contract](../portable-contracts/contract.md), [source layout](../source-layout/design.md), P2 [distribution implementation](../distribution-implementation/README.md), coordinator [P1 integration](../../../workflows/2026-09-23-framework-redesign-control/reports/p1-integration-and-p2-scope.md) and [P2 integration](../../../workflows/2026-09-23-framework-redesign-control/reports/p2-integration.md). Direct tracked source inspection covered Lesson metadata/configuration/operations and selected script functions, plus distribution package parsing and manifest.

Observed P2 restrictions: the Lesson config parser accepts only `skills.lesson` / `constraints.lesson`; package defaults are exactly store/template; no helper resource field exists; derived roles require a project record; distribution selects exactly declared members and requires implemented entrypoints. No product execution established these observations.

The current source repository still uses live GitHub Issues under `.dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml`. Historical `.dev/backlog` is not reactivated. Source policy, U001, this design and workflow records are excluded from proposed package members.

## Selected implementation and handoff

The coordinator selected config v2, metadata v2, exact 10/8 members and coordinated single-writer GitHub operations in [the shared contract](../p3-shared-contract.md). Source exists under src/skills/pr and src/skills/local-backlog, including the public pr.github adapter. Both local tasks are complete; the workflow closes only this bounded source delivery. Issue/Project/provider integration and closure remain coordinator-owned. Schema/behavior acceptance, package/install trials and CI remain deferred-by-owner under U001 to program coordinator / P7.
