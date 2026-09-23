# P6 安裝、差異更新與恢復設計

這是 [#345](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/345) 的 design checkpoint，依 [#322 U001](../../../assessments/ASM-20260923-00-6oq/execution-plan.md) 編寫。狀態為 **proposed / design-complete；implementation、activation、驗證皆未完成**。本文件不啟用新產品、不轉移 root owner，也不授權 migration。

採用現有 development candidate：精確 commit、profile、package versions、44 個宣告 payload members 與 Codex 生成入口。安裝器只管理 lock 列出的 `.ai/core` 與 runtime 檔案；專案設定、自訂內容、資料與未知檔案保留。更新先比較 raw digest 與 mode；相同檔案不重寫、不改 mtime。這能省去人工複製技能、同步 runtime、逐檔辨認移除項目與猜測中斷位置，但仍須讀取檔案偵測 drift，且首次 durable snapshot 仍需寫入完整受管集合。沒有實測 I/O、速度或 SSD 壽命效益。

安裝本身只有兩種持久格式：lock 與 immutable operation；另為實際需要的 M01 config pair 轉換提議一份獨立、由 conversion owner 負責的最小恢復記錄。operation 在明確 durable store 保存完整 before/after 受管 bytes；專案 marker 是同一份文件，不另造 journal、receipt 或多階段事件流。狀態從 marker、lock 與實際檔案比對得出。RAM disk 消失後，可用 durable store 還原 matching core/lock/runtime；專案其餘內容仍需原有 Git／備份，不能把受管 snapshot 當成 whole-worktree backup。

- [實作契約](contract.md)：versions、public operations、ownership、delta、activation、恢復及失敗案例。
- [機器格式](formats.md)及 [synthetic exact-shape examples](examples.json)：僅設計文件，非 candidate、fixture、lock 或成功證據。
- [一次性 dogfood 與 implementation slices](cutover-and-slices.md)：統籌選擇點與各 owner。
- [固定來源證據](source-evidence.md)：實際程式格式、Git blobs、線上 Issue overlap、P4/P5 依賴。

統籌已在 `842b73ca09d701d1561109255193d80439dc996b` 選定 P5 M01：只在實際需要時轉換 P2 JSON config exact integer `1 → 2`，其他語意值、absence、write_roots 與 locks 保持不變。此處只設計介面與恢復，未執行轉換。仍需選擇 engine/state 版本、distribution 入口阻擋方式、metadata v3 instruction 讀取邊界、首個 profile 與明確 durable 路徑；不為獨立技能引入 shared runtime。新安裝可先做 read-only plan，activation 必須等所需實作及 P7 checks。

本次未執行任何產品工具。UTF-8、JSON/YAML/AST syntax、參照與 Git/diff、exact planned commit-message 是有限檢查，不是 schema 或行為通過。其餘全部 `deferred-by-owner`，authority U001，owner program #322 coordinator / P7，next action：implementation 完成後由 P7 選定 redesigned checks。
