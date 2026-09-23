# Development candidate 組裝介面

下文保留 P2-B 交付時的介面與當時狀態。P3 的 metadata v2、readable/writable schema 與後續實際 mapping 邊界見 [P3 metadata v2 增補](metadata-v2.md)；增補仍是未執行的 source implementation。

這是 [Issue #331](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/331) 的 P2-B 程式交付說明，依 [P1/P2 整合安排](../../../workflows/2026-09-23-framework-redesign-control/reports/p1-integration-and-p2-scope.md) 實作。[P1-A](../portable-contracts/contract.md) 擁有 skill metadata；[P1-B](../source-layout/design.md) 擁有 source / installed output 邊界。

程式尚未執行。U001 將 CLI 試行、build、測試、安裝和 CI 延後到 P7；以下是實作介面與待試行命令，不是已生成的 candidate、lock 或 receipt。這個 branch 沒有 #330 的 skill source，整合後才能提供完整來源 commit。

## 輸入與公開入口

`tools/build-development.py` 只負責 CLI 引數及結果輸出。選取、metadata 檢查、projection 和組裝都在 `src/distribution/`。

| 入口 | 契約 |
| --- | --- |
| `distribution.assembly.assemble(repository, commit, profile, output_root, scratch_root)` | `Path` 型別的明確絕對 roots、一個完整小寫 40/64 位 commit OID、一個已宣告 profile；成功才回傳真實 candidate/scratch 路徑和 development identity。 |
| `distribution.git_source.GitSource` / `distribution.selection.select` | 唯讀 source selection；只讀 selected commit 的 exact Git blobs，不讀 payload checkout bytes。 |
| `distribution.codex.project_entry` | 從所選 adapter template 與 installed destinations 產生 prefixed Codex entry；不改 root runtime。 |
| CLI result | 成功 stdout JSON，`outcome=assembled`、實際 roots、candidate identity、completion metadata 路徑；輸入／組裝錯誤以 stderr JSON 和 exit 2 回報。argparse 使用標準 usage error。 |

執行環境需要 Python `>=3.11,<4`、PyYAML `>=6,<7`、本機 Git 和完整可讀 object database。程式不下載／安裝依賴、不取 credentials、不 fetch；拒絕 partial/promisor clone，關閉 Git replace refs、lazy fetch 和 terminal credential prompt。Lesson 自己的 jsonschema 等 runtime requirement 仍由 Lesson 工具處理，組裝不宣稱它們可用。

builder 的 Python modules 必須與所選 commit 相符；只容許 checkout 的 CRLF/LF 差異，Git source 與實際執行檔 bytes 的 identities 分開記錄。修改中的 payload checkout 檔案不會進入成品。沒有浮動 branch/tag、縮寫 commit、dirty payload、stable mode 或自動 dependency solver。

## 精確選取

`src/distribution/manifest.yaml` 的 `manifest_version: 1` 包含三個 closed arrays：

- `profiles`: `{id, path}`，path 必須是 `src/profiles/<id>.yaml`。
- `components`: `{id, source, metadata, members}`；source 是 `src/skills/<id>`，metadata 是 `skill-package.yaml`，每個 member 是 `{source, destination}`。
- `adapters`: `{id, template}`；目前只有 Codex 與其固定 template 路徑。

`src/profiles/lesson-minimal.yaml` 的 `profile_version: 1` 包含 `id`、`skills: [{id, version}]`、`adapters: [id]`。版本是 exact `MAJOR.MINOR.PATCH`。未知欄位、重複 ID、重複／大小寫別名路徑、檔案與目錄 prefix 衝突、escape、glob、Windows reserved name 都拒絕。Git 成員只接受 `100644` / `100755` 的 regular blob；symlink、submodule、directory、缺少的 blob 都不成為 payload。

manifest 成員集合必須精確等於 metadata 推導的集合：`SKILL.md`、`skill-package.yaml`、`resources.references[]`、schemas/templates 的 `path`、implemented tools 的 `entrypoint`。不新增另一個 member schema，也不掃入整個目錄。重複資源、owner/ID/version 不一致、未宣告 operation contract、tool/operation 不一致或 `design-only` / planned package 會拒絕。metadata/config default 的 closed fields 依 P1-A；distribution 不解析專案 config，不覆寫設定語意。

required dependency 必須已在同一 profile 精確選定；缺少、版本不符或 cycle 是錯誤。optional 不會自動選取；若已明確選取，則核對版本和 public operations。所有所選 package 都檢查 required closure。

Markdown 的標準 inline links/reference definitions 和 schema 的 `$ref` / `$dynamicRef` 檔案目標必須留在所選 package。網頁引用不會被下載。JSON schema 檔案需可讀為嚴格 JSON 且宣告 Draft 2020-12。這不是完整 Markdown/HTML parser、schema 語意 validator、程式 dependency analyzer 或 secret scanner；fragment 語意、動態 Python 路徑、程式內隱含 I/O 及內容可攜性仍需 owner 內容檢視與 P7 驗證。source-only/custom/history/root 資料不會被當成 build input 解決缺項。

## #330 對接成員

統籌在本次實作中採納下列八項；manifest 對齊此清單，通用程式不硬編碼清單。每項保留相對名稱並映射至 `.ai/core/skills/lesson/<member>`：

1. `SKILL.md`
2. `skill-package.yaml`
3. `references/configuration.md`
4. `references/operations.md`
5. `references/example.md`
6. `schemas/lesson-record.schema.json`
7. `templates/lesson.md`
8. `scripts/lesson.py`

`references/example.md` 由既有 `resources.references` 宣告。`lesson.fs` 的 entrypoint 是 `scripts/lesson.py`，沒有 helper、新 metadata 欄位或 glob。#330 的 CLI 是 `--request <explicit-file|->`，JSON 內含 explicit `project_root` / `package_root` / operation；builder 不 import 或執行它。統籌仍需在首次 push 前讀回 #330 最終 commit 的 metadata/member bytes。

## 輸出與身分

呼叫者先準備明確的 scratch/output parent directories，可位於 RAM disk，也可以同一個 parent。程式不發現磁碟、不修改 `TEMP` / `TMP`、不建立使用者未選擇的 parent。parent 必須位於 source worktree 之外，不能經過 symlink/reparse point。每次獨占建立 `scratch-<uuid>` 與 `candidate-<commit-prefix>-<uuid>`；existing destination 會拒絕，不重用舊 run。

candidate 結構是：

```text
payload/.ai/core/skills/lesson/<eight exact members>
runtime/.agents/skills/framework-lesson/SKILL.md
metadata/selection.json
metadata/files.json
metadata/build.json
```

payload 保留原始 Git blob bytes。`files.json` 保留每檔 source path / blob OID、Git mode、size、SHA-256、destination、owner。POSIX 會 materialize 並讀回 0644/0755；Windows 僅以 inventory 保留 Git executable mode，`mode_materialization=inventory-only` 明示此限制。P6 installer 必須使用 inventory 的 Git mode，不能從 Windows staging permissions 推測。工具不產生 archive 或 installed lock。

runtime 是獨立生成的 bytes，不是 payload 的第二個手工 owner。其 Markdown 連結由 installed destinations 計算，必須指向所選 installed resource；entry 提醒 caller 選定 project/config，預設慣例 `.ai/custom/framework.json` 只是專案提示。它不讀 config、不指向 source checkout、不改現有入口，也不證明任何 matching installation 已存在。

三個 JSON 文件都是 version 1：

- `selection.json`：development mode、`release_version=null`、source commit/tree、profile、實際 component identities/member list、dependencies、adapter template/entrypoint/output identities，以及精確 build inputs/generator Git identities。
- `files.json`：僅列 payload/runtime materialized files；不把自己當成可自我雜湊的 payload。
- `build.json`：最後才寫，包含真實完成時間/run ID、前兩檔 SHA-256、candidate identity、執行環境與 generator 執行檔 identities。installation / behavioral validation / publication 都是 `not-performed`。

`candidate_sha256 = SHA256(json_bytes({"metadata/selection.json": SHA256(selection bytes), "metadata/files.json": SHA256(files bytes)}))`。`json_bytes` 使用 UTF-8、sorted keys、indent 2 和一個結尾 LF。development identity 是 `development:<full-commit>:<candidate_sha256>`。時間、run UUID、host 和 checkout newline 執行資訊只放 `build.json`，不影響上述 content identity。這不是發行版本、簽章或外部驗證 receipt。

scratch 和失敗產物都保留；這個工具沒有清理／delete engine。組裝先檢查閉包，再 staging，逐檔讀回，複製至新的 candidate，核對 emitted bytes/modes，最後寫 completion metadata。任何中斷／錯誤都不能由檔案存在推論成功；missing、partial、mismatching completion metadata 必須拒絕。P6 仍須重新核對 inventory、hashes、managed ownership 和安裝狀態，不能直接信任一個 JSON 的 `outcome`。沒有跨目錄、跨磁碟或 crash-durable transaction 的宣稱。roots 必須由 caller 控制；這不是對抗另一個程序惡意替換目錄的 sandbox。

## 待 P7 執行的命令

在 coordinator 整合完整來源、選定 immutable commit 並允許 P7 試行後，使用相符 checkout。以下 placeholders 必須替換為 caller 的實際路徑／commit；此處沒有建立它們：

```text
python -B <source-worktree>/tools/build-development.py --repository <absolute-source-worktree> --commit <full-lowercase-commit-oid> --profile lesson-minimal --output-root <absolute-existing-output-parent> --scratch-root <absolute-existing-scratch-parent>
```

不呼叫 builder 的靜態 Python 檢查可用 `ast.parse` 讀取 `src/distribution/*.py` 和 `tools/build-development.py`，而非 import 或 `--help`。本次只做這類語法、UTF-8、JSON/YAML、reference/content 與 Git 檢查。P7 應選取 exact-blob/CRLF/mode、closure errors、path/collision/link、unique output/failure、metadata digest 和 installed-reference 的 focused cases；這是待辦方向，沒有測試執行結果。

P6 擁有 read-only installation planning 的後續產品介面、managed apply、migration/recovery 與 cutover；此 slice 不需要提前新增 plan engine。root runtime、core、lock、custom、ignore 和 source history 都保持其既有 owner。
