# GitHub Provider Projection Preview

- Canonical source revision: `9ce991f52e076bd3736516c2c200ee54c9312464`
- Generated at: `2026-07-30T22:18:19+08:00`
- Generator: `.ai/scripts/github_backlog_provider.py`
- Mode: read-only branch preview
- Online writes performed: `false`

This preview proves deterministic projection from the committed canonical
backlog changes. It is not authorization to mutate live GitHub state. The
provider projection must be regenerated from merged `main` before online
writes.

| Backlog | Source SHA-256 | Body SHA-256 | State | Status | Priority | Owner review | Target release | Published in | Related work | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `STD-001` | `519e12c5dc945dd58de30b1858088a064edb03d25df4bac5f460c274290110fc` | `f68f5c9c5546430ab3f7fc939e59e8a883480e9cb79d578038a7656547b1e5bf` | open | Planned | P1 High | Approved | Unassigned | Not yet published | `OBS-001` | none |
| `OBS-001` | `63daa0aee7ee2e4d50999f428cfde8dc594243cbbfcd2bfeb8da19056114f05d` | `dc5e9906bc43f8daa4d72dd3865be8025ea09c045950420c9deddd0ca89b15aa` | open | Inbox | P2 Normal | Pending | Unassigned | Not yet published | `STD-001` | none |

Validation at this revision:

- `python .ai/scripts/validate-workflow-artifacts.py`: passed for 53
  post-adoption workflows, 73 indexed workflow directories, and 42 backlog
  items.
- `python .ai/scripts/tests/test_github_backlog_provider.py`: 18/18 passed.
- Assessment validation remained green for 24 assessments.
