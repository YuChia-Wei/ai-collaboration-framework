# AI Context Release Publication Runbook

本 runbook 實作 source-only
[AI Context Source Release Policy](../../standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md)。
本文件中的 `candidate`、`publication` 與 `finalization` 簡稱只在各自明確
section 內成立，不得解讀成 target upgrade category、workflow completion
或跨階段 mutation authority。

## Trigger

當已核准的 governed framework release 已完成實作，需要從冷啟動環境建立候選、合併、建立 immutable annotated tag，並由 GitHub Actions 完成發布與 provider tracking 對帳時使用本文件。除明列且已核對的 release-specific exception 外，tag 仍由 owner 建立。從 `v0.12.0` 起，正常流程不再包含 post-tag source registry 收尾。

不要用於補改既有 published tag、搬移 tag 或複製舊 release 目錄。任何既有 tag 的移動、重建與刪除都不屬於 automation 或 agent 的權限。

## Scope And Source Of Truth

- 新版本一律從 [canonical release-publication templates](../../../.ai/assets/skills/ai-context-governance/templates/release-publication/) instantiate；不得複製 `.dev/releases/v*` instance。
- `release.yaml`、`release-notes.md`、`migration-guide.md` 是 candidate 的 source of truth。從 v0.10.0 起，source-repository candidate 的 Included Work 以 `planning.github_issue_refs` 的 GitHub read-back 為權威；既有已發布 release 的 `backlog_refs` 保持歷史相容。`release-notes.md` 不得包含 renderer 的 automation marker 或 provenance block。
- 從 `v0.12.0` 起，`release.yaml.provider_reconciliation` 以 machine-readable 方式宣告 included work 與 coordination Issues 在發布前後的 Issue／Project 狀態。契約 `1.0` 保留五個 canonical Project 欄位的完整精確檢查；契約 `1.1` 只把明列的 canonical Project 欄位視為必要條件，省略欄位屬 advisory、不得因缺值阻擋或由流程修改，未知欄位仍 fail closed。Issue state／state reason 在兩版都維持必要。tagged source 維持 `status: validated`；provider reconciliation 不回寫 source record。
- 每個 `.dev/releases/<version>/release-phase-checks.yaml` 的 command 是 handoff 可比對的 sanctioned command；不可包進 shell substitution 或任意 command。
- 每個版本必須從 canonical template 建立自己的 phase contract。不可修改或重用另一版已記錄的 command；下方 `<version>` 必須先展開成同一個 stable `vMAJOR.MINOR.PATCH` literal，checkpoint 內也必須保存展開後的完整 command。

## Host Prerequisites

- Source-side Python tooling requires Python 3.11 or newer plus the exact
  dependency in `requirements.txt`.
- The source framework release gate is SDK-free and does not require a .NET
  SDK. A downstream target may select its own SDK and .NET validation commands;
  those target-owned prerequisites are outside this publication runbook.
- A self-hosted GitHub Actions runner must be version 2.327.1 or newer. The
  candidate and publication workflows use the Node 24 artifact actions
  (`actions/upload-artifact@v7` and `actions/download-artifact@v8`); older
  self-hosted runners are unsupported.
- macOS may not provide a usable `python` command. After installing a supported
  interpreter and dependencies, set `AI_CONTEXT_PYTHON` to that executable or
  virtual-environment path. This is a supported execution route and must still
  produce a fully executed required gate, not a skip.

## Hosted Workflow Overlap And Cost

The three pull-request workflows use a workflow-and-PR concurrency group and
cancel a superseded run. A new commit on the same pull request therefore keeps
only the latest governance, portable-gate, and package-candidate execution,
while distinct workflows and pull requests remain isolated. This bounds
duplicate hosted-run cost without merging gates that have different trigger
paths or responsibilities.

Tag publication is deliberately different: it uses an immutable tag-scoped
concurrency group with cancellation disabled. A later retry must not cancel a
release that may already be staging or publishing assets. General governance
and package candidate remain read-only and never receive the Project write
credential. Only the environment-protected tag jobs receive release or Project
mutation authority; provider preflight runs before Release mutation and
post-publication reconciliation is idempotent.

## Cold-Start Candidate

1. Instantiate the six template artifacts into the active workflow and `.dev/releases/<version>/`; resolve every `<...>` placeholder with current observed values: release record, authored notes, migration guide, version-owned phase contract, workflow locator, and release task.

2. Run:

   ```powershell
   python .ai/scripts/validate-ai-context-release-state.py --phase candidate --version <version>
   ```

   Expected result: exit `0`, a governed `validated` candidate, complete authored artifacts, and no stale copied values.

   Fail action: do not merge, tag, or publish. Correct only the candidate artifact or its validation evidence, then rerun the same command.

3. Run the repository critical gate and record its exact output in the workflow evidence:

   ```powershell
   bash .ai/scripts/check-all.sh --critical
   ```

   Expected result: exit `0` and no required failed check.

   Fail action: remain on the owning remediation task. Do not mark the release record `validated`.

## Merge And Pre-Tag Gate

1. Merge the release workflow into `main` with the approved strategy. Re-open the merged checkout; do not create a tag from a workflow branch.

2. Run:

   ```powershell
   python .ai/scripts/prepare-ai-context-release.py --version <version>
   ```

   Expected result: exit `0`, clean worktree, exact validated candidate identity, and the critical gate evidence required for user tag creation.

   Fail action: do not request a tag. Repair the indicated registry, candidate, branch, or gate problem; make a new reviewed checkpoint and repeat from the candidate phase.

### Current-Main Command Invalidation

任何在 pre-tag 成功後合併至 `main` 的 commit（包括只更新 lifecycle
closeout 文件的 merge commit）都會使先前印出的 tag command 過期。建立 tag
前必須在當前 clean `main` 重新執行同一條 pre-tag command，並且只使用該次
新印出的完整 command；不得重用指向舊 SHA 的輸出。

## Tag Authority

The repository owner—not an agent, script, or GitHub workflow—creates and pushes
the annotated `<version>` tag only after the pre-tag preparation command passes,
except for the single `v0.10.0` authorization below. Use the complete command
printed by `prepare-ai-context-release.py`; it pins the validated commit,
summarizes compatibility, and takes the `AI-Model` value from the latest
registered handoff checkpoint.

### v0.10.0 Owner-Authorized Agent Exception

The owner-approved **AI Collaboration Framework v0.10.0 Terra implementation
work package** and online Issue #137 authorize the named Terra agent to create
and push only one **new annotated** `v0.10.0` tag, and only after the current
merged `main` pre-tag command has passed. This narrow exception does not
transfer ownership of any other tag and never allows moving, recreating,
deleting, or force-pushing an existing tag.

Before tag mutation, record the exact validated candidate SHA, the active
executing identity, the complete generated tag command, and the pre-tag gate
read-back in the release workflow. Immediately after the push, read back the
annotated tag object and peeled SHA. After hosted publication, retain the
workflow run URL, GitHub Release identity, and four governed asset tuples in
the records-only finalization evidence. Any mismatch stops the lifecycle; read
back provider state before deciding whether a new repair branch is needed.

After the owner has created and pushed the tag, no agent-operated closeout
command is part of the normal lifecycle. The tag workflow automatically runs
the equivalent tag, publication, hosted-finalization, and provider read-back
gates. The following commands remain read-only diagnostics for a failed run:

```powershell
python .ai/scripts/validate-ai-context-release-state.py --phase tag --version <version>
```

Expected result for the first diagnostic: exit `0`; the tag is annotated,
peels to the current validated commit, and the tagged tree contains the
terminal `validated` registry record.

Fail action: do not move, recreate, delete, or replace the tag. Preserve
evidence and escalate the mismatch to the owner.

The hosted diagnostic is:

```powershell
python .ai/scripts/validate-ai-context-release-state.py --phase publication --version <version> --hosted
```

Expected result: exit `0`; the public release, exact rendered body, four governed
assets, and successful tag-triggered workflow match the immutable tag.

Fail action: do not move, recreate, delete, or replace the tag. Preserve the
failed workflow evidence and correct only the retryable workflow, credential,
or provider-state condition. A retry must not create a source closeout commit.

## Hosted Publication And Provider Reconciliation

The tag push triggers `.github/workflows/publish-release.yml`. The workflow:

1. validates the immutable tag and builds deterministic archives;
2. performs provider preflight with `RELEASE_PROVIDER_TOKEN` before Release mutation;
3. creates or resumes only its owned draft and publishes the four governed assets;
4. verifies the stable hosted Release against the terminal `validated` source record;
5. applies only the postpublication Project-field transitions explicitly declared by the release contract, closes the release-coordination Issue as completed, and reads every required value back; omitted advisory Project fields are neither required nor mutated;
6. retains a provider reconciliation receipt as a workflow artifact.

It never creates, selects, or moves a tag, and it never commits a post-tag source
record. Expected result is one successful tag workflow, a stable/non-draft
GitHub Release with exactly the governed assets, and converged provider state.

Fail action: retain the GitHub Actions run URL and logs. Correct the bounded
credential or provider-state condition and rerun the failed job when safe. If
source code truly requires repair, use a new reviewed branch for a future retry;
never move the existing tag or rewrite source merely to claim closeout.

`ai-context-release-closeout` is retained only for historical records and
exception recovery. It is not a required normal step for `v0.12.0` or later.

## Pre-Tag Terminal Checks

Before handing tag creation to the owner, run these read-only checks from the
clean, integrated `main` tree:

```powershell
python .ai/scripts/reconcile-ai-context-release-provider.py --phase preflight --version <version>
python .ai/scripts/prepare-ai-context-release.py --version <version>
python .ai/scripts/validate-ai-context-versions.py
git status --short
```

Expected result: all Python commands exit `0`, `git status --short` is empty,
and the preparation command prints the one annotated-tag command pinned to the
current `main` SHA. At that point the only owner action is to create and push
that tag; all later normal lifecycle work is hosted automation.

Fail action: do not request or create the tag. Repair the exact candidate,
provider preflight, or current-main gate condition and repeat these checks.
