# REL-v0.13.0 — SDK-Free 基線、漸進式檢閱與封閉的發行包

## Status

已驗證的 framework version candidate。Publication 仍需 repository owner 在最終接受的 `main` commit 上建立並推送 annotated `v0.13.0` tag。

## Highlights

- 將 framework-owned required checks 改為 SDK-free：source release 不再需要安裝 .NET SDK、restore Roslyn/NuGet，或建置 framework 自有的 `.csproj`。
- 退役 bundled compilable analyzer／runtime-validation provider；保留 engineering rules、diagnostic mapping 與 bounded recipes，只有 target owner 明確選取時才建立符合目標 SDK、Roslyn、severity 與 CI policy 的 analyzer project。
- Code Reviewer 改為 entry、file type、finding 三層 progressive disclosure；只載入目前檔案與 finding 所需規範，並保留 checklist、severity、output contract 與 canonical engineering semantics。
- 將 framework version candidate、repository integration、hosted publication、validation phase 與 target upgrade 等治理詞彙綁回各自 canonical owner，分離 source-release procedure 與 portable target policy。
- Package schema `2.2.0` 對 selected payload 的 local links、anchors、actionable commands、source-only lifecycle references、component dependencies、capability ownership 與 availability 採 fail-closed，ZIP 與 tar.gz 使用同一套 user-view contract。
- 長時間 release／nightly／full-matrix validation 綁定 clean immutable commit 後交由低成本 external task；來源對話不輪詢，schema `1.1` 要求 task 在送出 callback 前驗證完整 dispatch／completion pair。
- Pull request 的 candidate packaging 改以 PR base/head 間實際變更的 governed release record 選版；沒有候選時明確 not applicable，多筆候選則 fail closed，不再因歷史 `validated` release 或全域最高 SemVer 推導而誤選版本。

## Practical Effect

Framework 的可攜基線現在只要求受支援的 Python runtime 與宣告的 Python dependencies；沒有 `dotnet` 的環境仍可執行 framework-owned required gates。`.NET` 架構、DDD／Clean Architecture／CQRS／Event Sourcing guidance 仍由 `dotnet-backend` profile 提供，但 compiled enforcement 已明確成為 target-selected capability，而不是 framework 假設已啟用的保證。

對 package 使用者而言，v0.13.0 的 archive validation 不只確認檔案清單與 checksum，也會從實際 selected payload 檢查導覽與 component closure。Code Reviewer 在 core-only selection 明確為 unavailable；選取 `dotnet-backend` 時，其 22 個 capability paths 必須完整封閉。

## Compatibility

這是 pre-1.0 breaking migration checkpoint。Automatic governed upgrade 僅支援從 immediate predecessor `v0.12.0` 升級；不得宣稱可自動跨越此 checkpoint。更早版本必須先經 owner-reviewed reconciliation，或先升至上一個受治理版本。Target-owned `AGENTS.md`、requirements、specifications、ADRs、operations、provenance、customizations、SDK 與 analyzer configuration 仍受 dry-run、acknowledgement 與 rollback 邊界保護。

## Release Validation

SDK-free、review routing、governance terminology 與 selected-payload deliveries 已由 PR #195 的五項 hosted checks 驗證，且六份 baseline／verification assessments 沒有留下 blocking finding。#194 的 schema `1.1` focused tests、AI-context validator 與真實 pre-send callback regression 已通過；#197 另以 Git-backed fixtures 驗證單一候選、無候選、多候選與 release record 刪除的選版邊界。最終 candidate archive、provider preflight、release-bound PR checks 與 merged-main pre-tag preparation 由 workflow `2026-08-12-v0-13-release-readiness` 固定與回讀。

## Publication Completion

Owner 推送 exact annotated tag 後，tag-triggered hosted workflow 才會建立 GitHub Release、上傳四個 governed assets、將 Included Work 的 `Published in` 更新為 `v0.13.0`，並完成 coordination Issue #61。Tagged source record 維持 `status: validated`，不建立 post-tag source closeout commit。
