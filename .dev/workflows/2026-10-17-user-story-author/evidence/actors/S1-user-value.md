## user_value

### Title
會員關閉電子郵件通知後可確認儲存結果

### Description

#### User Story
身為會員，我希望關閉電子郵件通知並儲存，讓電子郵件通知偏好反映我的選擇，且能辨識此次儲存是否成功。（R-U v1）

#### Background
R-U v1 已接受：成功時 EmailEnabled=false 並顯示「已儲存」；失敗時顯示「未儲存」且兩個偏好維持原值。既有畫面與儲存機制的現況未提供，無法推定目前缺陷或使用痛點。

#### User Scenarios
會員在偏好設定情境關閉電子郵件通知並儲存。成功時看到「已儲存」，EmailEnabled 為 false，PhoneEnabled 保持儲存前值。儲存失敗時看到「未儲存」，EmailEnabled 與 PhoneEnabled 都保持儲存前值。實際畫面入口未提供。

#### Functional Requirements
依 R-U v1，關閉電子郵件通知並儲存成功後，EmailEnabled=false，畫面顯示「已儲存」，既有 PhoneEnabled 不變。儲存失敗時顯示「未儲存」，兩個偏好均保持原值。

#### Scope
包含關閉電子郵件通知的儲存成功與失敗結果，以及 PhoneEnabled 的保留。其他偏好功能及通知發送行為不在本份來源支持的範圍。

#### Open Questions
實際畫面入口、既有儲存流程及如何辨識儲存失敗尚未提供；接手實作前需定位，不能由草稿推定技術方式。

### Acceptance Criteria

- [ ] 會員關閉電子郵件通知並儲存成功後，EmailEnabled=false，畫面顯示「已儲存」。
- [ ] 上述儲存成功後，PhoneEnabled 與儲存前值相同。
- [ ] 關閉電子郵件通知的儲存失敗後，畫面顯示「未儲存」，EmailEnabled 與 PhoneEnabled 均與儲存前值相同。

### 交接脈絡
來源：R-U v1，已接受；本文件為文件草稿，AC 尚未執行或驗收。沿用決定：成功／失敗訊息、EmailEnabled 成功值及兩偏好保留規則。無真實父項／工作項 ID；沒有已知跨項依賴，實際程式關聯尚未建立。第一步：依本草稿確認既有會員偏好入口與儲存邊界，再由需求 owner 處理未決資訊。目前只授權文件草稿；provider 寫入與實作需另行授權。

