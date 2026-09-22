# P1 跨契約整合與 P2 工作範圍

此文件是統籌的內容檢視與實作安排，不是獨立驗證或執行結果。依 U001，行為測試與 CI 仍延後至 P7。

## P1 採納

- #325 擁有 skill-package.yaml、設定解析語意、Lesson schema 與 public operations。#326 擁有 src / distribution / installed output 邊界，不能重複定義這些資料格式。
- Lesson package 的六個設計成員為 SKILL.md、skill-package.yaml、references/configuration.md、references/operations.md、schemas/lesson-record.schema.json、templates/lesson.md。實作工具及必要 helper 必須另外明確宣告，不用 glob 自動擴大成品。
- 此 repo 的設定選定位置為 `.ai/custom/framework.json`，由 project 擁有；JSON 語意以 #325 為準。這不是全域強制位置，呼叫者仍明確傳入 project/config roots。
- 採納 stable core、lock 與精確 generated runtime outputs 一起 tracked 的方向。首個 runtime 路徑為 `.agents/skills/framework-lesson/SKILL.md`。只有 matching installation 才能切換入口；目前沒有安裝或發布的 stable 成品。
- #324 已經由 PR #328 線上合併，main merge 為 `5f9981c43d083d8428db52f49756a41cfbea6d15`；Issue CLOSED/COMPLETED、Project Done 已讀回。P7 驗證仍未完成。

## 檢視發現

1. #324 原始 delivery 的文字 source-only 宣告未排除 distribution wildcard。CORR-001 已補精確 exclusion 並保留歷史提交，詳見該 Issue workflow。
2. #326 原始 delivery `42601292b9fa1d4fbd190c0d03f570c25e991624` 使用五個成員的 allowlist，漏掉 #325 最終新增的 configuration.md；原設定範例副檔名也與 JSON-only 契約不符。修正版 `f2255fe3328bd91f8f9a54c7cea8a1e9e6ffecac` 已補成六個成員並改用 framework.json，統籌已核對；修正只代表契約對齊，不代表實際 build/install 通過。
3. #325 的 callback 被自動核准審查拒絕。統籌改以任務狀態與本機唯讀交付讀回完成接收，未重試繞過，也不需請使用者重做授權。設計 HEAD `c3891615f97625e7c59cd871abea3c2b27b5021f` 保留。

## P2 拆分與所有權

| 工作項 | 唯一寫入範圍 | 交付與相依 |
| --- | --- | --- |
| P2-A Lesson | `src/skills/lesson/`、自己的 workflow | 從 P1-A specimen 實作 candidate-only filesystem tool，入口 `scripts/lesson.py`；owned helpers 在 skill 內。工具執行延後。 |
| P2-B 成品組裝 | `src/distribution/`、`src/profiles/`、`src/adapters/codex/`、`tools/build-development.py`、自己的設計／workflow | immutable Git source 的精確選取、runtime projection、candidate assembly 與必要 read-only install plan；metadata 閉包以 P2-A 最終輸出為準。 |

兩項可平行寫程式，統籌在首次 push 前將 P2-A 的完整 member list 交給 P2-B 對齊。不得相互改檔或建立更多對話／sub-agents。共通設定暫留 Lesson；沒有第二個 consumer 前不抽通用核心。

P2 只交付程式與文件，依 U001 不執行新 CLI（含試跑）、package build、installer 或測試。可用 ast.parse 做 Python 語法檢視而不 import、執行或產生 pycache。其他實際檢查維持 UTF-8、JSON/YAML、差異／引用與完整 commit-message 格式檢查。

原 P2 的根目錄消費目標分段落地：本階段交付成品生成與消費介面的程式；managed apply、資料轉移與 recovery 實作留 P6，真正安裝／tool trial／行為驗收留 P7。現有根目錄 runtime 入口在明確 cutover 前保留，不指向尚未安裝的 core。這是配合使用者「最後才試行、測試」的工作排序，不是已完成端到端 dogfood 的宣稱。

P3/P4 能力可在 P2-A 合併後依已實作的 package/config 介面推進，不以候選組裝工具的試跑當前置。P5/P6 再整理剩餘來源與安裝更新；P7 依最終產品風險設計必要檢查。外部 provider、發布、任意舊版 migration、全量 repo 搬移均不在這兩個 P2 工作項。
