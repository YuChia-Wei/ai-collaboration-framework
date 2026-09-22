# 可攜 Skill 契約：P1-A

本目錄交付 Issue #325 的設計與具體範例。這些是待 P2 實作的契約，不是已可執行的套件；版本 `0.1.0` 與範例資料都是設計值，沒有發布、安裝、執行或核准的含義。

核心選擇是：一個 Lesson skill、一個 filesystem store、一個 Lesson record schema。Lesson 可單獨使用，不需要 workflow、ADR、GitHub 或 ai-context 維護技能。套件宣告其內容與相依；專案決定資料位置、模板及可寫範圍；執行時只讀取選定設定，不搜尋這個來源 repo 的私有目錄。

- [契約](contract.md)：身份／版本、required 與 optional、設定順序、所有權、logical artifact roles 與錯誤行為。
- [Lesson 入口](lesson/SKILL.md) 與 [package metadata](lesson/skill-package.yaml)：具體套件宣告。
- [操作契約](lesson/references/operations.md) 與 [record schema](lesson/schemas/lesson-record.schema.json)：第一個 family 的寫入／讀取邊界。
- [獨立使用範例](examples/walkthrough.md)：自訂 project 路徑及模板，附可直接讀取的設定與示例資料。
- 執行紀錄：`.dev/workflows/2026-09-23-portable-contracts/`。

JSON record 是可編輯的專案資料；Markdown 是依模板產生的閱讀投影。模板可改位置與標題，但不能把 Lesson 變成新的規範權威。初版只建立與修改 `candidate`；採納、supersede、promotion 由 P3-A 再定義。

`skill-package.yaml` 屬於套件，工具／schema／模板的相對路徑以 package root 為基準。專案設定與 artifact root 則以明確 project root 為基準。這與 #326 的 `src` 唯一來源、`.ai/core` 安裝及 runtime projection 設計相容；本契約不決定那些實體目錄，也不複製 distribution manifest 或 framework.lock schema。

本次依 U001 只做內容檢視、JSON/YAML 可讀性與 Git／commit-message 檢查。舊 validators、測試、package/upgrade/migration 試行、獨立驗證 audit 與 CI 均為 **deferred-by-owner，待 P7**。範例不能作為執行成功或相容性證據。
