# Migrate To v0.13.0

## Supported Sources

Automatic governed upgrade 僅支援從 `v0.12.0` 升級。v0.13.0 是 breaking migration checkpoint，不得自動跨越；更早版本需要 owner-reviewed reconciliation，或先按各版本 checkpoint 逐步升級。

## Before You Start

1. 保持 target worktree clean，並備份或 commit target-owned `AGENTS.md`、requirements、specifications、ADRs、operations、provenance、customizations、SDK 與 analyzer configuration。
2. 驗證 v0.13.0 archive checksum，並確認 automatic route 的 recorded source 正是 `v0.12.0` 與其 `metadata/files.yaml`。
3. 先執行 dry-run；在 apply 前逐項 review removals、collisions、component selection、target-owned preservation 與 acknowledgement-required reconciliation。

## Migration Steps

1. 使用 v0.12.0 files inventory、目前 target provenance/customizations 與 v0.13.0 package 執行 governed dry-run planner。
2. Review 已退役的 bundled provider paths。若 target 曾自行 reference-in-place 或複製 analyzer/runtime-validation project，將它視為 target-owned truth；明確選擇 preserve、remove，或依 `dotnet-backend` on-demand recipe 重建，不得由 framework 靜默覆寫。
3. Review Code Reviewer custom references 與 component selection。Core-only target 應接受 Code Reviewer unavailable disposition；需要 .NET review 時必須選取 `dotnet-backend`，讓完整 capability path closure 成立。
4. Reconcile 任何把 source release records、publication runbook 或 source-only commands 當作 downstream target instruction 的 customization；portable target 只使用 version、provenance、customization 與 upgrade policy。
5. 若 target 有自訂長時間 validation orchestration，保留其 runtime choice，但對齊 fixed clean commit、exact argv、terminal-only callback、no-polling 與 schema-valid pre-send completion evidence。
6. Acknowledge 已 review 的 reconciliation items，套用與 dry-run digest 綁定的新鮮 plan，並保留 apply receipt。
7. 執行 target-owned validation。Framework 不要求 .NET SDK；只有 target 明確選取的 analyzer、build、test 或 CI contract 才可要求 `dotnet`。若結果不接受，依 apply receipt rollback。

## Clean Installation

Clean install 選取 mandatory software-development core、AI-context lifecycle core 與預設 `dotnet-backend` technology profile。Payload 不含 framework-owned compilable analyzer、runtime validator、`.csproj` 或 root SDK pin；它包含 target-selected analyzer design recipe、diagnostic mapping 與 reference-only snippets。Optional provider、repo backlog 與 target-owned mechanical enforcement 仍需明確選取。

## Scope Boundaries

- Framework source workflows、assessments、release records、publication runbook、GitHub Project state 與 provider reconciliation 不安裝成 target truth。
- v0.13.0 不建立或發布 `EngineeringGuardrails.Contracts.*`；是否採用仍由 target owner 與 #179 的獨立 readiness contract 決定。
- Reference-only snippets 不宣稱跨 SDK 可直接編譯；target owner 負責 project、package、severity、tests 與 CI evidence。
- Historical provider paths可留在 immutable evidence，但不得恢復為 active framework capability。
