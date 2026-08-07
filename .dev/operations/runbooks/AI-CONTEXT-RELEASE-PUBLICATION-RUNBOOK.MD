# AI Context Release Publication Runbook

## Trigger

當已核准的 governed framework release 已完成實作，需要從冷啟動環境建立候選、合併、建立 immutable annotated tag、GitHub Actions 發布，並完成本機 registry 收尾時使用本文件。除明列且已核對的 release-specific exception 外，tag 仍由 owner 建立。

不要用於補改既有 published tag、搬移 tag 或複製舊 release 目錄。任何既有 tag 的移動、重建與刪除都不屬於 automation 或 agent 的權限。

## Scope And Source Of Truth

- 新版本一律從 [canonical release-publication templates](../../../.ai/assets/skills/ai-context-governance/templates/release-publication/) instantiate；不得複製 `.dev/releases/v*` instance。
- `release.yaml`、`release-notes.md`、`migration-guide.md` 是 candidate 的 source of truth。`release-notes.md` 不得包含 renderer 的 automation marker 或 provenance block。
- 每個 `.dev/releases/<version>/release-phase-checks.yaml` 的 command 是 handoff 可比對的 sanctioned command；不可包進 shell substitution 或任意 command。
- 每個版本必須從 canonical template 建立自己的 phase contract。不可修改或重用另一版已記錄的 command；下方 `<version>` 必須先展開成同一個 stable `vMAJOR.MINOR.PATCH` literal，checkpoint 內也必須保存展開後的完整 command。

## Host Prerequisites

- Source-side Python tooling requires Python 3.11 or newer plus the exact
  dependency in `requirements.txt`.
- .NET validation requires SDK 10.0.300 or newer so the host satisfies
  `global.json`; 10.0.203 is below the required feature band.
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
concurrency group with cancellation disabled. A later dispatch or retry must
not cancel a release that may already be staging or publishing assets. General
governance remains read-only, package candidate remains read-only, and only the
environment-protected publication job receives `contents: write`.

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

After the owner has created and pushed the tag, first run:

```powershell
python .ai/scripts/validate-ai-context-release-state.py --phase tag --version <version>
```

Expected result: exit `0`; the tag is annotated, peels to the current validated
commit, and the tagged tree contains the `validated` registry skeleton.

Fail action: do not move, recreate, delete, or replace the tag. Preserve
evidence and escalate the mismatch to the owner.

Then run:

```powershell
python .ai/scripts/validate-ai-context-release-state.py --phase publication --version <version> --hosted
```

Expected result: exit `0`; the public release, exact rendered body, four governed
assets, and successful tag-triggered workflow match the immutable tag.

Fail action: do not move, recreate, delete, or replace the tag. Preserve evidence and escalate the mismatch to the owner.

## Hosted Publication

The tag push triggers `.github/workflows/publish-release.yml`. That workflow validates the tag, renders the public body, builds deterministic archives, and creates or resumes only its owned draft release. It never creates, selects, or moves a tag.

Expected result: the hosted workflow completes successfully; the GitHub Release is stable/non-draft with exactly the ZIP, tar.gz, and adjacent checksum assets produced from the tagged tree.

Fail action: retain the GitHub Actions run URL and logs, then repair the source workflow on a new branch. Do not mutate an unowned draft or a published release merely to hide a failure.

## Local Registry Finalization

After hosted publication evidence is available, record only observed tag, commit, timestamp, run, asset, and release URL facts in the governed release record. Keep generated marker/provenance material out of authored notes.

Run:

```powershell
python .ai/scripts/validate-ai-context-release-state.py --phase finalization --version <version> --hosted
```

Expected result: exit `0`; the published registry record equals the immutable tag peel, authored notes remain renderer-free, and required terminal evidence is present.

Fail action: do not alter the tag. Correct a factual registry omission through the governed finalization workflow, retain the publication evidence, and rerun the command.

## Terminal Checks

Run these read-only checks before declaring the release closed:

```powershell
python .ai/scripts/validate-ai-context-release-state.py --phase finalization --version <version> --hosted
python .ai/scripts/validate-ai-context-versions.py
git status --short
```

Expected result: both Python commands exit `0`; `git status --short` is empty after the finalization checkpoint is committed.

Fail action: the release is not closed. Record the failed command and output in the workflow, then resume only the task that owns the failed condition.
