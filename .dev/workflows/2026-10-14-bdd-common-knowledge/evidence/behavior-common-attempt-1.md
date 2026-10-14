# #452 common installed-instruction actor samples B1-B3

Actor output only; no acceptance judgment. Isolated consumer: C:/b452-74060e5c/common/p. Entry bdd-gwt-test-designer@0.3.0; knowledge engineering-common@0.2.0. Selectors: test-design/design/direct/technology_profile null, examples/renewal.md (B1/B3), examples/renewal.feature (B2). All selected guidance is optional knowledge, not adopted project rules. applicable_rule_ids=[]; conditional_rule_ids=[]; authorities=[].

## Provenance and consumption log

The actor had previously read older source inventory in this conversation, including pre-change skill/GWT descriptions, but did not use repository source for these samples. No workflow expected judgments were inspected. New reads for this task: supplied common-resources.json, installed Codex entry, installed SKILL, metadata, design instruction, lock inventory; then installed BDD-METHOD and GHERKIN-SCENARIOS. BDD-METHOD was read again after explicit lock inventory checks.

Important sequence limitation: both knowledge resources were read in one batch before generating B1-B3. GHERKIN-SCENARIOS was selected for requested B2 expression, but was already present in context during B1/B3. Thus this is not isolated per-case negative-read evidence. Initial knowledge reads checked raw hashes against the supplied verified-reader result; direct lock inventory checks of all six chosen instruction/knowledge members occurred afterward, before the outputs. Initial entry/instruction reads preceded those inventory checks. No claim of perfect before-first-read inventory protocol is made.

Exact hashes, inventory matched before outputs:
- .agents/skills/bdd-gwt-test-designer/SKILL.md: ebca01010328ff9433eb772048181fd88425da32468229e2c6ae24681b3846cc
- .ai/core/skills/bdd-gwt-test-designer/SKILL.md: dae30d2ca24774605aec8fa13d25d1218710f6d5a1d7f52f1e894c4585220630
- .ai/core/skills/bdd-gwt-test-designer/skill-package.yaml: 7cfaad3fa1d5467fcb3b1621c580b2f517f0bd7f9a467590421b51ea9b22d670
- .ai/core/skills/bdd-gwt-test-designer/references/design.md: bd671a3d1b15977a5ade72f401797fae4b2476ae52d4e7b1235c03ff6415d0cb
- member:references/BDD-METHOD.md, .ai/core/knowledge/engineering-common/references/BDD-METHOD.md: 65dd5669a4b06f6b00abcec5a3c273b4cc4d2920b767201da5f4cbf82ae4f4d4
- member:references/GHERKIN-SCENARIOS.md, .ai/core/knowledge/engineering-common/references/GHERKIN-SCENARIOS.md: 53943e3d23a62242a3320692b3c6fc0b085f7d24dd60047d598e3edf2093f154

Lock SHA256 initially and before outputs: 4f8224d6d037f9edb331e545bae50452365c36dac8b8b23ed6cea9bcc903e426. Candidate identity from verified reader: subset:3:0.0.0:c9439c1d29c21fe27f0415b62c910e9aabffe790:24f0880fa57752640c1fc57230ba913ac79ee086ce80b59c5c61545200a82088. desired_sha256: 16e86e2647879423122627dffa910a5bf74430456e778d999d0c3e1784bac6de.

Catalog, GWT handoff, README and other knowledge resources were indexed in supplied JSON but their content was not loaded. No runner/parser/tests/implementation executed. Hashing and reading only; no library business system observed.

## B1 actual output

目前沒有提供逾期續借政策，因此不能判定逾期借閱可否續借。這次只探索規則與待釐清問題，先不寫情境。

- 已知意圖：借閱者希望了解逾期後是否仍可續借。來源為本次 B1 指示；它是探索題目，尚不是已同意的業務規則。
- 待決 Q1：逾期借閱是否可續借？應由圖書館借閱政策負責人提供現行規則及生效範圍。
- 待決 Q2：若允許，是否有逾期天數、欠款、續借次數或會員資格限制？這些是釐清問題，不是新增要求。
- 待決 Q3：若拒絕，借閱者看見什麼結果？若允許，新到期日如何計算？目前沒有可用的預期結果來源。
- 可用來討論的暫定例子：一筆已逾期一天的借閱提出續借請求。結果仍未知，可用它詢問政策負責人；不能將允許或拒絕寫成已批准的答案。

Installed knowledge used: BDD-METHOD (available as knowledge). GHERKIN-SCENARIOS previously read for B2 but not needed for this output. Coverage: bounded Discovery questions only; no designed scenario set, no test/behavior coverage claim. No rule adopted from the illustrative library example.

## B2 actual output

以下情境只依據本次已同意的 R1/AC1：另一位會員的預約阻止續借，並保留原到期日。來源為 B2 指示；scenario ID S-R1-01 是本次本地追蹤標籤。

```gherkin
Feature: Renew a library loan
  Rule: Another member reservation prevents renewal
    @R1 @AC1 @S-R1-01
    Scenario: Refuse renewal and preserve the due date of a reserved loan
      Given Ada has borrowed loan L7 due on 20 October
      And Ben has reserved the item on loan L7
      When Ada requests renewal of loan L7
      Then renewal of loan L7 is refused
      And the due date of loan L7 remains 20 October
```

R1/AC1 → S-R1-01 對應兩個重要觀察：續借被拒絕、到期日仍為 20 October；兩項預期值都來自已同意的 R1/AC1。測試邊界可先選續借應用操作，實際呼叫續借主體並檢查公開拒絕結果及可讀取的到期日；它可證明操作行為，尚不證明完整 UI 或資料庫整合。setup 必須獨立建立 Ada／L7／Ben 預約，若日期判斷影響此規則，需由目標補足年份、時區與固定時鐘。未提供逾期政策，未設計逾期判定；未推導無預約必定允許續借。

Installed knowledge used: GHERKIN-SCENARIOS plus previously read BDD-METHOD for source/status distinction. status=available for these optional knowledge resources; adopted normative coverage=none. Coverage: supplied AC1 represented in scenario text with both outcomes; parsing, step binding and execution not run. No runner or mandatory destination selected.

## B3 actual output

已同意的規則只有 R1/AC1：他人預約阻止續借並保持到期日。逾期政策仍未知；探索與表述使用同一組來源 ID，未知問題不轉成已同意規則。

| 項目 | 來源／狀態 | 內容 |
| --- | --- | --- |
| R1/AC1 | B3 指示引用 B2；已同意 | 他人預約阻止續借，原到期日不變。 |
| Q-overdue | B3 指示；未決 | 逾期後可否續借？哪些限制及日期計算規則適用？ |
| E-overdue | 本地探索例子；暫定 | 一笔逾期且無他人預約的借閱請求續借；預期結果待政策負責人確認，未納入已支持的情境。 |

S-R1-01：有他人預約時拒絕續借且到期日不變。
- Given：Ada 借閱 L7，原到期日為 20 October，Ben 已預約其借閱品項。
- When：Ada 請求續借 L7。
- Then：L7 的續借被拒絕。
- And：L7 的到期日仍為 20 October。
- 來源及預期結果：R1/AC1；具體 Ada／Ben／L7 資料沿用 B2 例子，作為本次例子資料，不另設新規則。

AC1 → S-R1-01 保留拒絕與到期日兩項觀察。實作時應使用真正續借操作，分別確認拒絕結果與到期日；必要相依可依目標規則控制，無需先選 runner。逾期例子保持暫定，沒有足夠規則建立它的預期答案。無他人預約也不能推出續借一定成功。若時鐘會影響已同意情境，先補足獨立日期 setup；不能靠前一個情境留下的狀態。

Installed knowledge used: BDD-METHOD (already read, no additional read for B3). GHERKIN-SCENARIOS was previously read for B2; no new Gherkin resource read and no requested .feature expression. status=available for optional BDD method knowledge; adopted normative coverage=none. Coverage: supported AC1 scenario notes plus explicit unresolved overdue question; no implemented/executed or end-to-end coverage.

## Terminal limits

These samples are generated actor responses under one inherited conversation, not three fresh independent sessions. Parent must evaluate the sequence and contamination limitations. No acceptance pass is claimed.
Terminal read-back after report generation: all six consumed instruction/knowledge members matched lock inventory hashes; framework.lock SHA256 remained 4f8224d6d037f9edb331e545bae50452365c36dac8b8b23ed6cea9bcc903e426. No terminal drift observed in these chosen bytes.
