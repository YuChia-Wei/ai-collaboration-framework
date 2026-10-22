# Independent design review and disposition

- Reviewer: /root/split_design_review; bounded-general-worker, existing ddd-ca-hex-architect artifact-review method.
- Author/integration owner: /root. Reviewer did not author or repair the subject; read-only, fresh context.
- Fixed subject: 4ade82bcc2eb4f8bc1230dbe9905c4db58293cbf.
- Base: f96fffe0af6e9e4f79d5f2f4be05bb3665553123.
- Classification: independent-review, limited to design/source contracts; no runtime acceptance.

## Findings and author disposition

| ID | Severity and evidence | Disposition |
| --- | --- | --- |
| R1 | P1: implementation-design.md:24 retained dotnet@0.1.4 while common becomes0.4.0. dotnet content-package.yaml:2427 requires common0.3.0; content.py:259 uses exact versions. Selecting both would fail closure. | Corrected design to dotnet0.1.5, required common0.4.0, new domain/software and four surviving consumers' dotnet pins; existing skill bumps cover metadata. Add explicit common+dotnet selection validation. No .NET rule semantics change. Verified resolved in follow-up. |
| R2 | P2: implementation-design.md:147 promised a retirement response when invoking absent old runtime ID, with no response owner; resolver only returns selection-unavailable. | Separate catalog rejection, removed new entry, unchanged old installed snapshot, and migration-guide/caller explanation. No router/tombstone or guaranteed runtime diagnostic. Verified resolved in follow-up. |
| R3 | P3: context-and-references.md:34 used nonexistent derived_dependencies/validate_dependencies function names. | Replaced with actual content.py descriptor/closure and fixed-source line references. Verified resolved in follow-up. |

The reviewer examined all five design files, directly related skill/knowledge metadata,
source rules, manifest/presets and dependency/binding/resolver functions. Core ownership,
GWT/test boundaries, incremental routing and separate future work were coherent. 31 local
links in design files resolved at the fixed subject (anchors not checked). Graph extraction
freshness/snippets were insufficient; the reviewer used fixed Git blobs for code evidence.
No source edits, product tests, installation or provider operations were performed by reviewer.

A-AC-01..13 remain the criteria. Later source review must explicitly inspect A-AC-06..10/13
(skip/reuse, feedback, checkpoint, optional absence, reviewer identity, system/DevOps boundary),
not claim the four main examples exhaust all semantic coverage. C/D-AC remain future scope.

## Provider read-back

Issues476..484 were created in Traditional Chinese and fetched open with expected titles,
scope:framework/created-by:codex and kind:story on Stories. Feature bodies link child Stories;
native sub-issue fields were not set. R1 corrections were applied to476..480 and fetched back
with dotnet0.1.5. These are work definitions, not completion or installation claims.

## Corrected design verification

Reviewer /root/split_design_review independently inspected only R1-R3 corrections at
3a3e3098fdd7a08dbe6c41a07bc174eabab1f4a9 against4ade82bc. All three are resolved at design
level; no blocking design finding remains. Source diff between those commits is empty.
No product test/runtime conclusion was made. The optional table wording was aligned to
common/dotnet dependency pins without changing the already reviewed detailed contract.
