# 可攜 workflow 編排設計 checkpoint

目前狀態：C341-01～05 已由[統籌選定](../p4-selected-contract.md)，十個成員／十個操作的 source 已完成；尚未建置、安裝或執行驗證。原設計 commit 7f821ee866e7e54e551036785e19dffaa3d7ac39 保留，下面是當時的設計說明。實作與限制見 [source 交付報告](../../../workflows/2026-09-23-workflow-orchestration/reports/source-implementation.md)。

這是 [#341](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/341) 的第一階段設計，尚未實作產品。英文 [contract.md](contract.md) 與 [record-shapes.md](record-shapes.md) 是本提案的契約；本頁提供繁體中文說明。[interface-proposal.json](interface-proposal.json) 列出完整檔案、操作與待協調事項；[examples.json](examples.json) 全部是假設案例，沒有執行證據。

建議保留 `software-development-orchestrator` 這個 skill 身分，提供十個公開操作。專案指定 filesystem store；一份 JSON 保存意圖、範圍、驗收項目、工作相依、證據、未決問題、下一步及回顧。它不要求固定 `.dev` 路徑，也不替每個 task 產生 locator、索引與 receipt。專門技能仍可直接使用，workflow 不接管它們的成果或權限。

最小輸入是「要做什麼、範圍、如何判斷完成、第一個動作與負責人」。工具只能建立 planned／pending 記錄；不能猜出已完成工作。後續 checkpoint 保存原狀態與失敗證據。Resume 明確指出誰在什麼條件下做哪件事，遇到必要內容超出容量時回報限制，不悄悄省略 blocker。只有實際呼叫者回報的觀察才會被保存，而且標示 caller-supplied，避免把記錄本身說成執行或核准證明。

workflow 完成可以包含明確委派的延後項，但會顯示 with-deferrals。延後必須留下原因、owner、觸發條件、下一步與授權出處；它不等於驗證通過。task 的 deferred、failed、blocked 都不滿足相依工作的 completed 條件。要完成 workflow，仍須交代所有必要驗收、未決問題與回顧。

回顧可以說「沒有值得新增的知識」。有需要時產生具體 Lesson／ADR／規範提案／PR／backlog 交接候選，附來源、用途、缺少輸入及下一步；不自動呼叫其他套件或產生其檔案。#334 的知識套件尚待實際交付核對；本 checkpoint 使用已協調的公開契約，沒有宣稱可執行。PR／backlog 已讀到 source contract，但也沒有執行或發布。

tracked／ignored 是專案意圖，不能證明 Git 追蹤、備份或多人持久化。工具不改 ignore/config、不 stage、不 commit、不挑磁碟。單一 writer lock 與 expected digest 只協調合作中的寫入者，無法保證未配合編輯器的 CAS，也沒有跨檔案或 provider 交易保證。

保留政策只提供 compact／archive／purge 預覽。進行中工作、延後責任、未解引用、不可取代或未知的證據會阻擋清理。掃描一個 store 不能證明外部沒有引用。Compact 最多產生保留原檔的摘要；archive 要列出耐久副本與引用續接所缺的證據；purge 永遠不回傳 safe-to-delete。本階段沒有自動刪除、搬移或 Git history 改寫。

協調者需選定 C341-01 至 C341-05：套件／record／operation 身分、候選交接方式、保守預覽規則、含延後項的完成語意，以及 metadata v2 維持 store／template defaults、retention／resume 預設值由 skill 自有契約管理的界線。接著在同一任務交付明確 source scope，才會進入實作。#316 的舊 workflow／assessment authoring 工作仍獨立存在，交由 P5／P7 決定重疊部分。

目前只做 U001 允許的檔案讀回、JSON／YAML 語法、引用與 Git 差異檢視、commit message 格式檢查。產品 CLI、schema validator、測試、建置／安裝／migration、audit 與 CI 都是 deferred-by-owner，owner 為 program #322 coordinator／P7。設計可讀及本機 commit 不代表產品已驗證。
