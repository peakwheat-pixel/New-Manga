# SETTINGS-OPEN-B-1 r3 — Follow-up 复审（P2 处置）

- Reviewer：`reviewer-settings-a`（非实现者）
- 复审头：**`3fdfcb3d21b36382f78691e8c7584f0e8df5eda8`**；修复 commit `02f1752dc`；B-1 代码交付头仍为 `b521ad27`
- 原 Review：[review-b1-r3.md](review-b1-r3.md)（`approved`，P2-1/P2-2/P2-3）
- 结论：**approved**。原三项 P2 均已处置，未发现新 blocker/major。

## P2 disposition

| 原 finding | 状态 | 核对 |
|---|---|---|
| P2-1 Handoff/Task 运行记录旧计数 | **fixed** | `doc/handoffs/SETTINGS-OPEN-B-1-7d19164.md:26-27` 已是 clean **1253/3**、**2585/3/9**，并注明旧 1212/1251 不再使用；`doc/tasks/SETTINGS-OPEN-B-1.md:85` 已同步 clean 数字 |
| P2-2 M3 语义未写入设计/UI，core-report 旧观察/重复 §9 | **fixed** | 设计 `SETTINGS_SECTION_SCHEMAS.md:105` 已写“偏好仅作用于 descriptor `requires_gpu=True` 的 provider；CPU-only/远程 provider 忽略偏好保持 auto”；前端 `sections.ts:555` / panel test 文案同步；`core-report.md:251` 改为“已由 M3 裁决修复（见 §10）”，原重复章节改为 `## 10` |
| P2-3 canonical sha256 为工作区 CRLF 而非 blob | **fixed（口径记录）** | Task `:85` 已注明工作区 CRLF pin、blob hash 差异、`check.ps1` 双接受、clean 复核以 raw 计数为准；`check.ps1` 继续 PASS |

## 独立验证（HEAD 3fdfcb3d，工作区仅 P04 未跟踪诊断）

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` | **1253 passed, 3 skipped, 1 warning in 50.06s，EXIT 0** |
| `python -m pytest tests -q` | **3 failed, 2585 passed, 9 skipped, 2 warnings in 175.59s**；3 failed = 2 个既有 `test_detection_manga_real` 环境失败 + 1 个既有 workbench 基线失败 |
| `npm --prefix apps/desktop/frontend test` | **41 files / 406 tests passed**（B-1 树 39/387；B-2 增加 2 files/19 tests） |
| `tsc --noEmit` | exit 0 |
| `tools/governance/check.ps1` | **PASS (2 warnings)**：3 个非终态 Task、STATUS 80% 预算 |
| 证据表 | Task canonical **20 行**，含 `EV-B1-REVIEW-B1-R3`，commit `02f1752` 含所 pin 文件 |

M3 行为仍为 r3 已验证的边界：非 GPU provider 忽略偏好保持 auto，`requires_gpu=True` 才走偏好/回退；B1 descriptor、m1 guard 未回退。B-1 Task `:85` 的 39/387 是 B-1 树口径，B-2 加入后 41/406，不构成 B-1 回归。

## 剩余

- 无阻塞 finding。
- 仅需在关闭时把 `doc/tasks/SETTINGS-OPEN-B-1.md:17,121` 的 `canonical_evidence_status/resource_closeout_status: pending` 收口为完成；本 Follow-up 文件若作为正式复审证据，需由 Lead 追加到 Task canonical evidence 并刷新 pin（当前 Task 已把旧的 `review-b1-r3.md` 固定在 `02f1752`，本文件为新 Review 文件，不修改旧文件以免破坏已固定 hash）。
