# Workflow 0.22.0：本機紀錄契約與多載體整合設計

狀態：#483 設計已依本次 owner 補充收斂，SQLite create-task 與 Board V2 query 增量已完成來源實作、直接驗證及獨立審查；未定選項仍明列，不是完整功能或遷移驗收。
來源基準：`b6de8cdb28404296e41f2b15079675cc96c7b8e4`。
本次讀回的需求：[Epic #416](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/416)、
[#481](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/481)、
[#483](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/483)、
[#513](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/513)、
[#445](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/445)、
[#514](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/514)。
執行狀態與 owner 決策來源見[本次工作紀錄](../../workflows/2026-10-25-workflow-0220-design/workflow-plan.md)。

## 1. 目標與需求變更

0.22.0 同時交付本機 SQLite、線上 adapter 與本來源庫實際採用。日常計畫、
狀態、日誌、工作文件、結果與接續資訊應離開 Git 追蹤；正式採納的規格、決策、
程式碼、測試、規則及可重用資源仍保留版本審查。

本次 owner 補充了三項產品需求：

1. 同一份 workflow 可同時保存於多個載體；由 adapter 傳送資料，避免 AI 為每個載體重複輸出。
2. 讀取使用者明確指定的唯一來源。
3. 某載體失敗時，顯示各載體結果與「同步未完成」；adapter 保留待補送資料並有限重試。

這是同一 workflow 的多載體寫入需求，超出「不同 workflow 分別選不同 provider」。
上述需求已由 owner 提出；跨載體成功語意、命令權威與讀取切換的具體機制仍需設計。
後續收斂使用 [#520](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/520)
承接多載體實作。線上平台已選定 Workflow Board，採用需要其
[多專案能力 #22](https://github.com/YuChia-Wei/ai-collaboration-workflow-board/issues/22)。

「由 adapter 傳送」不表示 adapter 自動理解或撰寫工作成果。AI 仍可產生一次必要的
語意內容；已存在的文件、命令、結果與附件應由工具讀取、序列化並傳送，避免再由
AI 抄寫成多份。節省 token 是目標，尚無實測節省比例。

## 2. 固定來源的現況與缺口

| 現有 owner | 公開能力 | 限制與後續變更 |
| --- | --- | --- |
| `local-backlog` | `explain/create/inspect/query/revise/transition/render`；JSON work item 是權威，Markdown 是 view | 有 AC、狀態與完成證據；沒有 operation receipt、版本歷史或 migration API；不能直接刪除入口 |
| `workflow-records` Git | `capabilities/find/context/read/checkpoint/resume/validate/operation` | 唯一持久 writer 是 checkpoint journal；locator、task、status 仍由專案 writer 管理 |
| `workflow-records` SQLite | 上列能力及 `init/create/write-document/export/preflight/restore/deactivate/activate` | `create` 可含初始 task；之後沒有 task/metadata 編輯與完整 transition；文件更新只能取代既有文字文件 |
| `software-development-orchestrator` | instruction 型 `orchestrate/resume` | 選階段、路由、驗證與下一步；沒有資料庫、schema 或 record writer |

直接依據：

- [local-backlog operations](../../../src/skills/local-backlog/references/operations.md) 與 [configuration](../../../src/skills/local-backlog/references/configuration.md)。
- [workflow operations](../../../src/skills/workflow-records/references/operations.md) 的 Public operations、Exact requests、SQLite recovery；[Git format](../../../src/skills/workflow-records/references/git-format.md) 的 writer 邊界。
- [service dispatch](../../../src/skills/workflow-records/tools/workflow_records/service.py) 與 [SQLite writer](../../../src/skills/workflow-records/tools/workflow_records/sqlite_store.py)。
- [orchestrator metadata](../../../src/skills/software-development-orchestrator/skill-package.yaml) 與 [orchestration method](../../../src/skills/software-development-orchestrator/references/orchestrate.md)。

目前兩個 workflow provider 都需要 Git source identity。SQLite 使用明確選定的
持久本機路徑，排除工作目錄、Git common directory 所在目錄及不安全路徑；不能用
RAM disk 保存工作紀錄。Git common directory identity 可識別 linked worktree，
獨立 clone 不因 logical repository ID 相同就可直接寫同一 store。

local-backlog 採 expected raw hash/state 與合作 writer lock；workflow-records 採
revision/source head、operation ID 與持久 receipt。兩者不是相同的並行契約。
SQLite 的 status 目前是必要字串，並未等價提供 local-backlog 的完整生命週期。

現有 SQLite export 保存保留期內 revisions、events、blobs 與 receipts，但 binary
附件沒有公開讀寫操作；容量有限且滿額拒絕，不能稱無限歷史。restore 產生 inactive
實體，啟用依賴原 DB 退役與唯一 successor；原 store 不可用時的接續需求仍有缺口。
package 的 `implemented`、schema、capabilities 或歷史測試檔均不證明本次 runtime 通過。

## 3. 責任與候選方案

| 方案 | 資料責任 | 取捨／目前狀態 |
| --- | --- | --- |
| A：維持分離 | local-backlog 管 item；workflow-records 管 workflow | 遷移少，但跨 store 的關聯、版本及恢復仍需處理；未採納 |
| B：整合紀錄、編排分離 | workflow-records 管 workflow/task/document 與可選本機 item；orchestrator 決定工作 | 本次選定方向；優先服務外部 Issue 系統，補齊 writers 與遷移後退役獨立 local-backlog |
| C：紀錄與編排全部合一 | 新 manager 同時管理資料與階段判斷 | 與現行 orchestrator 重疊、擴大授權耦合；不推薦，未採納 |

B 延續[既有候選](../skill-evolution-2026-10-22/local-workflow-and-customization.md)，
本次依 owner 對外部 Issue 系統的實際使用與開始作業授權收斂；不是回頭將歷史推薦改成決策。
D-P3-04 是 optimistic preflight/post-read，並非 writer owner 決策。
新多載體需求不改變 orchestrator 的開發判斷責任，也不使它成為同步引擎。

**local-backlog 不是 workflow 的必要依賴。** 一個 workflow 可以關聯外部權威工作項目、
明確選用的本機 work item，或經授權的直接工作；建立 workflow 不必先建 local item。
本來源庫與 owner 的主要情境直接關聯 GitHub／ADO，需求／AC／外部狀態仍由該系統擁有。
內部 task、結果與 checkpoint 不複製成另一套可寫 Issue 系統，也不自動關閉外部 Issue。

本機需求管理對無線上 tracker 的使用者仍有價值，但保留的是 workflow-records 的可選能力，
不是永久維持一個必要的獨立 skill。獨立 local-backlog 在等效 create/read/revise/transition、
render 與 migration 讀回完成後退役；在此之前保留舊入口相容性，不手改 managed installation。
這項相容工作不阻擋一般 workflow/task 操作、線上 adapter 或多載體功能。

| 概念 | 建議唯一責任及生命週期 |
| --- | --- |
| Work item | 外部 tracker 擁有外部需求、AC、狀態；workflow 僅保存穩定 refs／帶時間觀察。只有明確選本機需求模式時才由可選 local item 擁有需求，不是每個 workflow 的前置 |
| Workflow | 一次被選定的執行脈絡、item refs、計畫、授權引用、結果；不強制 item 與 workflow 1:1 |
| Task/step | workflow 內部工作與阻礙、相依、結果；新增 50 個 step 不新增 Issue 或改 Project |
| Checkpoint | 對特定 revisions 的接續觀察；不覆寫 item/task state，也不自行產生授權 |
| Document/revision | 穩定文件 ID、不可變修訂及 lineage；定稿用增補／勘誤／後繼修訂，保留 finding/decision ID |
| Command owner | 檢查授權、版本及合法狀態轉換，接受一次邏輯 mutation；不可由讀取或 resume 隱式觸發 |
| Dispatcher 與 provider adapters | 保存及傳送同一 accepted payload，記錄逐載體 receipts、unknown 與補送；不決定工作優先序或放寬權限 |
| Read router | 只讀明確的 carrier reference，回報其 revision/同步進度；不因來源失聯自動改讀其他副本 |

Command owner 與 dispatcher 的實際承載位置仍待選定。推薦一個邏輯命令入口配合
多個受控儲存副本；這不是現有的 provider 組合能力，也不是允許各副本獨立改寫後自動合併。
人類 UI 若能繞過此入口，必須有可驗證的同等命令／事件契約，否則不能納入「一致寫入」聲明。

## 4. 建議公開操作與版本語意

下表是能力設計，名稱是候選 operation family，尚未加入 `workflow-records/1`。
正式名稱、contract version 與相容讀取範圍須在實作前固定。

| 操作族 | 主要輸入／輸出 | 新增或保留的契約 |
| --- | --- | --- |
| work-item create/read/query/revise/transition | ID、AC、狀態、完成證據、extensions、expected revision | 保留原 ID/created_at；合法轉換；completed/cancelled 不自動重開 |
| workflow create/read/revise/transition | source identity、item refs、授權引用、狀態與結果 | revision 不代替授權；外部 work item 狀態只是帶時間的 provider observation |
| task create/read/revise/transition | workflow ID、task ID、相依、owner、結果、expected revision | 不依靠手改 DB 或 checkpoint 假冒 task writer；完成必備證據由明確契約定義 |
| document create/read/revise/finalize/supersede | document ID、content/hash、parent revision、finding/decision refs | 新增文件與附件公開操作；任意 SQL、任意路徑覆寫不在一般 agent 權限 |
| context/resume | workflow ref、分頁／範圍、必要 revision refs | 清楚呈現完整／截斷／缺漏；摘要不能替代未讀正文；不執行下一步 |
| checkpoint | revision、source identity、operation ID、observations | 引用 item/task/doc 版本，不另立狀態權威 |
| operation/result | logical operation ID 與逐載體 ID/receipt | same ID+payload 回傳原結果；異 payload 衝突；不存在 receipt 為 unknown |
| export/preflight/restore/activate | manifest、cut、hash、identity mapping、activation authority | export、migration、同步及切換分開；保留 inactive restore 與受控啟用 |

單一 SQLite mutation 需在同一 transaction 提交狀態、revision、事件及 receipt；
衝突或不合法轉換不留下半份資料。查既有 receipt 應先於新寫入的 stale revision 判斷，
使已成功操作的重試不因 current revision 前進而被誤認失敗。異 payload 不覆寫原 receipt。
對未知結果先查 operation，再有限重試原命令；不自行換 expected revision 或換身分。

狀態對映需要逐項保留：local-backlog 的 draft/planned/in_progress/blocked/completed/cancelled，
來源庫 task 的 pending/in_progress/completed/deferred，以及 legacy 不認得的值。
不把 deferred 改成 passed，也不把沒有證據的 completed 升級成已驗收。

## 5. 多載體增量與 Story 安排

實作 Story [#520](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/520)
承接「由轉接器同步 workflow 至多個載體並從指定來源讀取」，歸入 #513 的 adapter 整合範圍，
依賴 #481 所需本機操作與 #445 的 Workflow Board adapter，納入 #416 的 0.22.0 交付。

| 既有工作 | 應吸收的部分 | 保留的交付邊界 |
| --- | --- | --- |
| #416 | 多載體產品目標；單一邏輯寫入權威與唯一指定讀取來源；部分成功語意 | 仍分開實作、來源庫採用及 0.22.0 驗收；新 Story 是否納入同版需明確記錄 |
| #483 | 現在設計 command/dispatcher/adapter/read router 邊界與相容契約 | 不提前實作 fanout，不選定平台 |
| #481、#445 | 每個載體的能力協商、operation lookup、revision、receipt 與完整資料操作 | 不各自實作跨載體同步策略 |
| #520 | 多目標傳送、逐載體進度、持久待補送、重試、指定讀取與來源切換 | 在實際選用 adapters 具備所需能力後交付，不等待所有可能平台 |
| #514 | 真實 SQLite+線上多載體整合、跨 session/client 與無 tracked diff | 不以模擬或 adapter 連線取代使用證據 |

傳送紀錄至少需保存 logical operation ID、canonical payload digest、固定目標集合、
各載體 operation ID、expected/actual revision 與 receipt/status。各 provider 的 revision
不能互相比大小；須另有可對應的 logical revision/sequence。新操作不能越過同一載體未完成
的相依操作。payload 大小、附件與完整歷史仍受 provider 的實際能力及容量約束。

在任何載體寫入之前，命令權威必須以同一持久提交保存「命令已接受」與完整傳送意圖：
不可變 payload（或足以重建原內容的不可變 references）、digest、logical sequence、固定
目標集合，以及各目標初始 pending 狀態。若權威狀態也在此步改變，必須在同一原子邊界
提交，不能先改資料再另寫待補送紀錄。重啟由同一 journal 恢復；不可重新讀取已變動文件
拼出不同 payload。選定 host 若無法提供此邊界，須先說明替代協定與失敗語意，不能宣稱
已具有可靠補送。此處的命令接受不等於所有載體均已同步完成。

已接受的需求是「逐載體結果＋同步未完成＋持久待補送＋有限重試」。因此不能在部分成功
時回報全部完成、重送已成功 mutation 或假稱所有載體都回滾。重試上限、退避、保留期、
停止／人工處置及總體 command acceptance 與同步完成的關係，仍需在新 Story 定稿。
認證或權限失敗不能以重試換身分；達限後保留待處理結果。

讀取選擇應持久保存完整 carrier ref 與 binding revision。當所選來源落後時，明示其
logical revision 與未完成同步；來源不可用時回報不可用，不偷偷讀另一份。來源切換
須是明確操作，驗證新來源的完整性／進度，不等同寫入權威切換、災難復原或遷移。
新增／移除載體及補齊歷史需要另外受控的配置 revision；不能靠改 default provider
重新解釋既有 operation 的目標集合。同步錯誤或刪除也可能傳播，副本不等於獨立備份。

## 6. 遷移、退出與恢復

1. 預覽選定原資料與目標映射：repo/commit、原始 bytes/hash、schema/policy version、
   work item/workflow/task/document ID、created_at、AC、終態、完成證據、references、extensions。
2. 無法理解的版本／欄位保留原資料及診斷，該項不可宣稱完成遷移；不丟欄位、不重開終態。
   既有 local-backlog 若未保存 revisions，只能匯入可證明的歷史，不能製造完整修訂。
3. 新 store 先建 inactive/staging 資料並讀回；比對數量、hash、關聯、歷史與操作去重。
   Git 歷史須讀相應 commits，僅讀最新檔案不能稱完整歷史。
4. 凍結選定原 writer，取得最後一致截點，再完成增量、驗證並切換 binding。無法確認
   原 writer 停止時不啟用第二個獨立 writer；多載體副本須服從同一邏輯命令入口。
5. 回復涵蓋切換後新資料。不得只回退舊 snapshot，也不得重播 Issue/Project/部署等外部副作用。
   未選定紀錄維持原樣，不改 Git history。
6. 完整匯出含 versioned manifest、cut、IDs、保留期 revisions/events/receipts/tombstones、
   文件與附件實體/hash、來源與角色 mapping。秘密與 token 排除；重新綁定身份、使舊 lease
   失效，外部寫入預設停用。最新 Markdown、CSV 或過期 URL 不構成完整退出。
7. 原 store 不可用時仍需乾淨替代 store 的可閱讀／接續驗收。目前 activation route 不足，
   必須另設可審核 recovery authority／舊 writer 隔離程序；在決策完成前不能聲稱已解決。
   不以單機設定檔保證跨機所有歷史副本都已失效。

備份頻率、保留期、容量及刪除政策仍待決策。現階段建議維持滿額拒絕與不自動刪除，
但必須評估 50 個 task 加文件修訂的實際 workload，不能沿用舊上限就宣稱足夠。
export/restore 不等同 Git↔SQLite↔online 轉換；fanout 亦不等同雙向同步。

## 7. 來源庫採用影響

Workflow Board 是本次選定平台。2026-10-25 讀回其私人 Site version 14 與現行
collaboration/1 的 18 commands、8 queries；實際 schema 固定 personal namespace，
服務只接受一個 configured store。它已有 owner 隔離，尚無同 owner 的多專案資料範圍。
Board #22 補穩定 project ID、UI/CLI/MCP 傳遞、文件/cursor/receipt 隔離及舊資料映射；
不擴充成商業租戶組織、帳務或完整 RBAC。完整退出與恢復仍屬 Board #6。
清空資料不能補上 project scope；本次先保留線上資料，完整備份、匯入預檢及恢復未驗證前不重建。

本次仍依現行政策保存 bootstrap workflow，尚未達成「日常工作紀錄不進 Git」。
後續 #514 必須一次對齊下列直接 owners/consumers，避免只搬 status：

| Owner／consumer | 必要調整 |
| --- | --- |
| WORKFLOW-GATE／ARTIFACT／HANDOFF policies | store discovery、穩定 refs、授權與完整接續；取代 Git-trackable root 必要條件 |
| SOURCE-DEVELOPMENT、Git flow、commit policy | 保留程式碼分支／PR／授權責任，移除日常狀態紀錄專用 commit 要求 |
| `.dev/INDEX.md`、workflow index、root navigation | 區分歷史 Git records 與目前 store；索引不再複製每日狀態 |
| Assessment refs／validator | `tools/maintenance/validate-assessment-artifacts.py` 現在查 Git locator，需明確 resolver |
| `workflow-records` Git reader／project writers | 保留舊 refs；切換後停止選定舊 writer；不能刪 locator 卻繼續靠它接續 |
| 安裝與 runtime entry | 本 repo 安裝不含 workflow-records；source CLI 可供開發，不能當成已安裝或已採用 |
| 特殊 release/recovery records | 保留原 ID、revision 與適用責任；不存在的 legacy validator 不因圖索引命中就恢復可用 |

Git 工作紀錄處置推薦「停止新 workflow 的 Git writer，保留歷史唯讀」；若需可編輯的
不追蹤文件區，必須定義匯入命令與 revision 檢查，避免它與 DB 都成為權威。此選項未採納。
正式規格／已採納決策保留 Git；工作草稿、審查執行結果與日誌進 store，是否升格為正式
版本文件須由文件 owner 決定，不將整個 `.dev` 一律搬走。

## 8. 後續可觀察情境（尚未執行）

| ID／Given | When | Then |
| --- | --- | --- |
| S01：無網路但本機 prerequisites 齊備，沒有 local-backlog 或 local item | 建立 workflow 與 50 個 task，再由新 session resume | 完整資料可讀，可保留已有外部 refs；不需連線 tracker，外部 Issue/Project 無變動，紀錄更新不產生 tracked diff |
| S02：兩個 writer 持同 revision | 同時修改同一 task／文件 | 一個成功，另一個衝突；無遺失更新或半份 receipt |
| S03：服務已提交但回應遺失 | 以相同 operation ID/payload 查詢及重送 | 回傳原接受結果，mutation/event 不重複；payload 不同則拒絕 |
| S04：task 缺完成證據或要求非法轉換 | 提交 transition | 拒絕且狀態/revision 不變，不以 checkpoint 繞過 |
| S05：定稿文件／舊修訂仍被引用 | 更正文件 | 新增可追溯 successor/erratum，原 finding/decision IDs 與原文仍可讀 |
| S06：transaction 中斷與完整 export 存在 | 重開 SQLite；另向乾淨 store restore | 無部分 transaction；ID/hash/history/receipt 一致，未經啟用不接受 writes |
| S07：原 store 不可用 | 依新 recovery 契約恢復並接續 | 必須提供受控啟用與舊 writer 隔離證據；現行契約不足，此項未通過 |
| S08：migration 遇未知欄位／版本／終態 | 預覽及嘗試切換 | 原資料保留，未映射項阻擋完成宣告；終態不重開，未選定紀錄不變 |
| S09：兩載體 A 成功、B 失敗 | adapter 回報並跨 session 補送 | 顯示 A receipt、B 待處理與同步未完成；不重複 A，B 有限重試且達限可查 |
| S10：唯一讀取來源 B 落後或失聯 | context/resume | 只回 B 的可證明內容及落後／不可用狀態，不默讀 A 或補寫成成功 |
| S11：固定目標集合的操作尚未完成 | 修改 carrier config 或相同 ID 改 payload | 原操作目標與 digest 不變；配置修改是新受控操作，無跨目標誤重播 |
| S12：選定人類與兩個真實 client | 登入、讀寫、交接、撤銷與 namespace 越權測試 | 真實可讀回結果；憑證身份不冒充每個 agent；stub/開網頁不算驗收 |
| S13：命令接受與傳送意圖使用同一持久提交 | 在意圖提交前、提交後首次 dispatch 前，以及 A 已提交但 receipt 未保存時中斷 | 提交前無接受命令或載體寫入；提交後重啟從原 payload/目標恢復；先查 A 的 operation 結果，不遺失 B 的待補送也不重複 A |

## 9. #483 驗收對照與待決事項

| #483 AC | 設計涵蓋 | 結論 |
| --- | --- | --- |
| AC01 | 第 2 節現況／缺口，第 4 節候選操作 | 草案已涵蓋；未宣稱 runtime |
| AC02 | 第 3 節 owner、GitHub 與授權邊界 | B 已收斂；本機 item 可選；dispatcher 的具體承載仍待固定 |
| AC03 | 第 2、4、5、7 節 before/after 與 conflict/replay | Git 文件處置與新同步契約待決 |
| AC04 | S01–S07 | 已列具體情境，尚未執行 |
| AC05 | 第 6 節與 S08 | 保留未知資料、終態與舊入口 |
| AC06 | 本節決策表 | 明列缺口；草案不是實作或採用 |
| AC07 | 第 5–6 節 | export/recovery/migration/fanout/read-source switch 分開 |

| 決策 | 建議／已知狀態 | 阻擋範圍 |
| --- | --- | --- |
| D01 資料與編排 owner | B：外部 tracker 為主要需求來源，可選本機 item 整合至 workflow-records，獨立 skill 待相容遷移後退役 | 第一個 workflow/task 增量可開始；退役需等效能力與讀回 |
| D02 Git 文件處置 | owner 已選統一以 SQLite 日常讀寫，再同步 Board；歷史 Git 保留，正式政策切換尚未執行 | 來源庫政策切換與既有紀錄匯入驗收 |
| D03 DB 位置與 Git 前提 | SQLite 為已選命令權威；持久路徑提案見第 13 節，尚未初始化；現有 Git binding 限制暫留 | store 初始化／採用；不阻擋契約設計 |
| D04 平台/client/帳號與維護 | 已選 Workflow Board，保持當前 owner-private；CLI／現有 MCP 是初始入口，多專案由 Board #22 補齊 | project-aware adapter 與真實跨 client 驗收 |
| D05 多載體失敗結果 | owner 已選 SQLite 權威、Board 同步副本、逐載體結果、同步未完成、持久補送與有限重試 | 交易內 outbox、retry 參數及正式切換待實作驗證 |
| D06 recovery／備份／保留 | 原 store 不可用時啟用程序及參數待決 | 災難接續與完整退出驗收 |
| D07 多 executor claim | 本增量不選；是否列 0.22.0 不適用需 owner 固定 | 不得以未實作 fencing 宣稱 claim 安全 |
| D08 新 Story 與版本 | #520，在所需 adapters 後交付，屬 #416／0.22.0 | adapters 的必要能力完成後實作 |

## 10. 第一個可獨立交付的本機操作

先加入 SQLite-only `create-task`，不依賴 Board 或 local-backlog。request 攜帶既有
workflow_ref、operation_id、expected_revision、expected_source_head 與一個 task。
task 使用既有 create 的 task_id/status/title 要求；owner_skill 為可選 extension，
保留未知 extension 欄位；
不能重複 task_id，不修改其他 task、metadata、documents 或 attachments。
使用現有單 DB transaction／revision／receipt 邊界；同操作重播先於 current revision
檢查，異 payload、過期 revision/source、inactive store 均拒絕。此操作只新增 task，
不另定 transition、完成證據或刪除規則；後續 task 更新／transition 分別依設計補齊。

直接驗證：公開 CLI 可新增並由 context/resume 讀回、相同 payload 重播、異 payload
碰撞、重複 task ID、stale revision/source、50 tasks 不變更外部 tracker、extensions／
文件／附件／原修訂保留，以及既有 export/restore 的資料閉包。Git provider 明確不宣告
此 writer。套件發布與來源庫安裝另行驗證，source 能力不等於下游已採用。

本文件保存 #483 的設計與後續增量邊界；第 10 節已有來源實作，驗證與審查狀態由
workflow 記錄。其他候選操作仍是設計，不代表現行 package、政策、安裝或資料已切換。
後續採納應更新同一設計的狀態與決策來源；新的來源需求／公開 Story 需保持可讀回關聯。

## 11. Board V2 query adapter increment

The 2026-10-25 continuation received the owner's Board deployment handoff and
confirmed the selected Work Records plugin's V2 tools in this conversation.
The owner then explicitly selected stable project ID `ai-collaboration-framework`.
Its creation and accepted receipt were read back at project revision 1. This is
project provisioning, not Framework workflow migration or source adoption.

### Accepted implementation boundary

Use an additive `workflow-records/board-query/1` profile in the existing reusable
package. Keep Git/SQLite `workflow-records/1` unchanged: its three-field references,
digest revisions, source_head and offset paging cannot losslessly represent Board
V2's complete project scope, numeric revisions, document ID/revision/hash and cursors.
The parent selects this versioning and transport mechanism as technical details
within the authorized #445 adapter scope; it does not adopt new lifecycle policy.

The first increment has two executable operations, `board-query-prepare` and
`board-query-accept`, implemented by a separately packaged Python CLI and modules.
The prepare operation validates an explicit non-secret binding and query, and
returns the exact native request plus an allowlisted symbolic MCP tool name.
The accept operation receives that prepared request, the same explicit binding,
and the real MCP result, checks their identities and critical response invariants,
then returns the native result without flattening its unknown data, missing inputs,
pagination, document references or receipt outcome. Preparation alone is not execution.

The binding contains adapter_id `workflow-board-v2`, a stable transport binding ID,
a positive binding revision and complete ProjectRef. It carries no token or ambient
credential lookup. A host supplies the selected connection and tool-name mapping.
The final concrete JSON shape is documented with the implementation before use;
unknown envelope fields, profile/schema drift and mismatched returned scope fail.
ProjectRef is explicit per request, never a mutable default substituted during replay.

Allow only `project.list`, `project.read`, `project.operation.get`, `capabilities`,
`workflow.find`, `workflow.context`, `context.page`, `task.read`, `decision.read`,
`document.read` and `operation.get`. Preserve the two receipt types and unknown
outcomes. Do not advertise remote commands as adapter writers merely because Board
capabilities list them. Do not route legacy-personal V2 workflow reads into V1.
No source_head is synthesized, and no local provider is selected on remote failure.

The host bridge must pass the prepared object directly to the selected plugin tool,
and pass the returned structured result directly to the accept operation. Both hops
must run as code, without AI copying or rewriting document bodies or native payloads.
This session will exercise that path through the actual selected plugin. The package
does not pretend that a standalone Python process can invoke Codex tools itself;
host availability and binding remain explicit runtime prerequisites.

Whole-response limits must be explicit and bounded. The profile may accept up to
2 MiB of JSON with a default 64 KiB output budget, using explicit caller overrides
for larger documents. Refuse an oversized whole result rather than clip content.
Verify exact document UTF-8 SHA-256 against the requested document reference.
Preserve opaque cursors and require exact fixed revisions in detail/page reads.

### Required evidence and exclusions

Direct tests cover valid native queries, A/B scope mismatch, missing/unknown fields,
contract mismatch, distinct project/workflow receipts, accepted/rejected/unknown,
exact document revision/hash, paging/missing context, malformed plugin results,
bounded output and no transport or mutation during prepare/accept. A package-closure
check must prove the isolated CLI has all source-owned modules. Existing local/Git
behavior remains a separate regression boundary.

Live acceptance must run through prepare -> selected plugin -> accept, including
the formal project read, A/B context, at least one exact document and known/unknown
receipt lookup. Direct prerequisite reads cannot substitute for this path. Test
fixtures and source code never require the Board checkout at consumer runtime.

This query increment excludes domain writes, claims, retry/fanout queues, implicit
binding persistence, credential setup, full export/restore, publication, installation
and migration. Their later contracts retain the original complete scope, operation
ID, expected revision and payload after unknown outcomes. Board #6 still owns the
full recovery gap; a deployed V2 endpoint does not remove that prerequisite.

## 12. Board V2 command adapter

The owner explicitly authorized this continuation after the query increment.
Add `workflow-records/board-command/1` alongside the unchanged query and local
profiles. Use the same explicit nonsecret binding and selected host connection.
The parent selects a Python CLI with jsonschema as an explicitly declared runtime
dependency for these new operations only. Package a frozen, source-owned native
V2 schema resource with origin commit/hash; no Board checkout or network schema
resolution is permitted at consumer runtime. Validate only the supported schema
selectors and the 18 currently advertised workflow commands; decision.resolve and
project administration remain outside this writer profile. Missing dependency or
capability is unavailable, not success.

Prepare validates binding, full V2 command, native capability scope/versions and
limits, safe integer wire syntax (including rejection of -0/exponents/floats),
UTF-8/Unicode and native byte limits. It returns the unchanged command, symbolic
allowlisted tool, separate local command fingerprint and original operation.get
query. A host must retain the complete prepared object before dispatch and pass
request/result as code. It must not alter operation ID, payload, expected revision,
project or identity during retry. This pure adapter is not a durable journal.

Accept validates the actual direct command result against the prepared request,
including exact workflow/operation, original expected revision, before/after
revision, actor shape, native digest shape and receipt/effect invariants. Preserve
the native receipt and distinguish accepted, durable rejected and unknown. The
bridge has no direct side effects, but observed original-command acceptance must
not be described by an unconditional mutation_state none. Native faults are not
durable rejected receipts; lost, malformed or mismatched responses after dispatch
remain unresolved. Authentication/permission failure never selects a new identity.

Board request_digest includes trusted owner_id and actor. The current host does
not expose independently verified owner_id; do not derive it from project or actor,
and do not relabel the local command fingerprint as the server digest. Direct
command acceptance is correlated by the host sending the exact prepared command
through the selected tool. State that server payload digest is not recomputed
locally. Operation lookup alone is insufficient to establish that an unknown
operation ID belongs to the original payload. If a prior verified server digest
exists, compare it; otherwise an observed lookup receipt requires replaying the
exact original command through the same host before final acceptance. The server's
payload-conflict check precedes CAS and prevents accepting a different payload.
The implementation must expose this distinction, not silently adopt a lookup as
proof. Reconcile prepares/validates only the original lookup; it never dispatches
or creates a new command automatically.

Host retry remains bounded and explicit. This increment supplies primitives and
clear next actions, not a background retry loop, automatic fallback or fanout.
Domain lifecycle, task/assignment fencing, human decisions, scope changes and
completion semantics remain Board-owned. Historical copies preserve source data
through the selected project-scoped source-replica profile; they do not translate
historical status into native events.

Required evidence includes supported commands and fail-closed capability/schema
checks, isolated package closure, exact request preservation, direct accepted and
rejected receipts, lost-response lookup requiring original replay, altered payload
collision, stale revision, wrong target, corrupted transport, strict bytes/numbers
and independent review. Actual host tests use an explicit synthetic workflow, then
low-cost workers may run deterministic historical copy batches and exact readback.

Observed host compatibility is now part of this profile: the selected MCP host
adds only `structuredContent.error_code: "INVALID_ARGUMENT"` on error results.
Accept that exact annotation only with `isError: true` and corroborating native
text; all remaining parsed fields must agree. A fully correlated native
`accepted: false` receipt remains a durable rejection even with that error flag.
An accepted receipt with the flag is contradictory; native faults remain unknown.

## 13. Selected SQLite authority and historical replica direction

The owner corrected the proposed read choice: "應該是統一使用 SQLite ，然後同步寫入
Board 才對". SQLite therefore owns daily reads, command acceptance and retained
workflow data; Board is a synchronized replica. The previously proposed Board-only
read authority was not selected. A local state mutation and its immutable pending
delivery must commit together in the same SQLite transaction. Remote receipt
updates must not create another domain revision or recursively enqueue delivery.

The proposed durable directory is
`C:\Users\h4227\AppData\Local\AI-Collaboration\ai-collaboration-framework\`.
It has not been provisioned or selected as an active store. RAM-disk scratch is
for disposable validation only. Source policy cutover, installation and recovery
remain concrete follow-on operations; none is implied by the command bridge.

The owner selected implementing a project-scoped historical mirror importer
before pushing the old workflow copies, and separately authorized Board Issue
[#24](https://github.com/YuChia-Wei/ai-collaboration-workflow-board/issues/24).
The selected new Board contract is `workflow-board/source-replica/1`: preserve
original metadata/status, paths, modes and raw bytes, stage bounded chunks, then
activate a complete immutable version with CAS and a receipt. This supports Git
snapshot IDs and SQLite logical revisions without manufacturing native task events.
The existing forbidden fixture import is not a production route. Production
delivery and actual historical import are not yet accepted.

At fixed Framework commit `f701105059bfc180dc5c212122e2fed939fdf664`, the inventory
contains 219 workflow units plus three root index/control files: 1931 Git blobs,
19427197 exact bytes. The 19437970 checkout-byte count is superseded because of
line-ending conversion. The largest unit by bytes has 41 files and 6473677 bytes;
the largest by file count has 107 files and 612065 bytes. Legacy fields, binaries
and records without locators must remain data, not be coerced into current create
semantics. Whole Git commit history is outside this snapshot copy.

## 14. SQLite snapshot and replica delivery implementation boundary

After independent command review, implement an additive version-2 SQLite schema
in the same explicit database. Preserve native workflows/revisions/blobs/operations
and their hashes; add immutable source snapshots/raw chunks, persisted replica
bindings, immutable delivery intents and delivery observations. The new profile
may provide its own CLI and kind-aware discovery without changing existing /1
request meanings. New initialization explicitly selects schema 2. Existing v1
databases are never upgraded by a read or an ordinary write; snapshot/replica
operations refuse v1 with an actionable result unless a separately implemented
explicit upgrade is selected. This increment may support fresh schema 2 only.

Historical snapshots have a distinct kind and preserve original bytes, paths,
modes, status, unknown fields and missing locators. Do not weaken native create
validation or invent tasks/authority/entrypoints to fit legacy data. A root-index
archive unit preserves the three files outside workflow folders. Derived views
identify source files and leave missing/unparseable values unknown. A committed
Git snapshot import must read Git objects, not checkout bytes. Local readback must
reconstruct every file and verify its size/hash before reporting import acceptance.

Snapshot staging accepts bounded manifest and chunk input; activation validates
all files, publishes the local version and enqueues the fixed-target intent in
one existing SQLite transaction. Native create/create-task/write-document/checkpoint
use the same transaction completion hook when a persisted binding is active.
Omitting per-call binding data cannot bypass that saved requirement. Replay occurs
before active/current-revision checks and never adds a second intent. Binding
activation and baseline selection must avoid a scan/install missed-write window.

Use the reviewed Board `workflow-board/source-replica/1` input/response contract
from 5bf075abb64b797f039e7484aa96485f814835e2, with self-contained packaged support.
Freeze each source snapshot, target/project/source mapping and binding revision.
Materialize and retain each exact begin/chunk/activate command before dispatch;
the next source version waits for the preceding accepted remote activation.
Unknown/conflict retains the original operation, expected revision and payload.
No automatic rebase, target switch, lost-payload replay or manufactured acceptance.
Receipt recording must be monotonic; a delayed unknown observation cannot erase
accepted evidence or recursively create a source revision/delivery.

The host dispatches one explicitly requested bounded step at a time; no background
scheduler or automatic pruning is selected. Native local acceptance means state
plus pending intent committed, with synchronization separately reported incomplete
until all selected replica receipts are verified. Reads continue using SQLite.
Transport credentials remain host-owned and never enter the database or export.

Version-2 export/restore includes all native history, staging/published snapshots,
raw chunks, bindings, intents, exact prepared requests and receipts, with complete
referential/hash/capacity validation. Keep v1 archive validation and semantics
unchanged. Restore remains inactive; neither restore nor inactive/retired stores
may dispatch. The existing deactivate/activate authority-transfer rules still
apply. No history, unfinished delivery or unknown fields may be silently dropped
to fit retention bounds; capacity failure rolls back the local mutation.

Required checks include transaction rollback and committed-response loss; replay
without duplicate enqueue; binary/empty/oversized/legacy reconstruction; bad or
missing chunk refusal; persisted binding enforcement; ordering and stale remote
receipts; inactive dispatch refusal; export/restore of pending prepared commands;
source-only isolated package execution; and immutable independent recovery review.
Runtime/host acceptance and formal source-policy cutover remain later evidence.

## 15. Implemented source-store slice and remaining cutover gaps

The first slice implements explicit fresh schema 2 and the separate
`workflow-records/source-store/1` CLI. Local historical import reads one committed
Git directory and atomically publishes its verified snapshot and target intents;
it does not expose a general caller-driven local staging/chunk import API.
Native capture runs for all four existing local mutation families. Each intent
already contains its complete immutable Board requests, and predecessor acceptance
gates later dispatch. Source observations remain separate from domain revisions.
Schema-2 export/restore retains the complete snapshot/delivery closure while v1
archives and native request meanings remain compatible.

The reviewed Board source-replica contract is deployed in owner-private Site
version 16. Actual CLI capabilities/list queries and browser project selection
succeeded; the project still has no published source copy. New source MCP tools
are not currently exposed in this runtime. The supported Windows CLI can carry
native DTOs through the source-store observation boundary after strict host
response validation; credentials remain host-owned.

This is an initial immutable-binding, SQLite-authority, manual-dispatch slice.
Dynamic binding changes, read-source switching, complete task/workflow editing,
permanent store provisioning, historical copy, real cross-session synchronization
and formal source-policy adoption are not established by local tests. Existing
Git workflow/branch/commit policies and locator consumers must be reconciled at
their owners before retiring daily Git writes. Keep historical source files and
their missing fields intact; an archive is not a migrated native lifecycle.
