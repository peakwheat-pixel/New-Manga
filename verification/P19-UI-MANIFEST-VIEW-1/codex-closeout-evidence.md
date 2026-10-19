# Codex closeout evidence — P19-UI-MANIFEST-VIEW-1

**裁定来源**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md`

## head 三元组（依 r12 §2.1）

| 名称 | 值 | 含义 |
|---|---|---|
| `reviewed_head` | `b36817d65e08a9e1269075bf7c116793e650e928` | Review frontmatter 的 `reviewed_head`，也是 Task 的 `delivery_head` |
| `delivery_head` | `b36817d65e08a9e1269075bf7c116793e650e928` | 与 `reviewed_head` **相同**——被审查的就是被交付的 |
| `closeout_head` | `67a665e49` | 其后仅含 Review 落盘、两项 Minor 修正与 Handoff v2，不含逻辑改动 |

**`delivery_head` 不改写为 `67a665e49`。** 理由（r12）：`delivery_head` 应指 Review 实际审查并
批准的交付 head；`67a665e49` 之后的变化是文档性收尾。若格式无 `closeout_head` 字段，
该值记录于本文档。

这与 `GOV-RESOURCE-MANIFEST-JSON-1` 的处理一致（那里 Review `7d09143d6`、集成源 `a2ca297f1`）。

## 终态与 AC

- 终态：**`closed_with_limitations`**（r11 裁定，Antigravity 复核确认恰当）。
- AC1 / AC2 / AC4 / AC5 / AC6 达成并勾选；**AC3 失败，保持未勾选**。
- 错误由 4 增至 10 属 **unmasking**（解除引用语法阻断后深层校验首次可达），
  不构成本 Task 引入 6 个资源债务。

## 十项错误归属（r12 §2.3 口径）

| # | 错误 | 归属 |
|---|---|---|
| 1 | `frontend-npm-test-final.log` SHA 不匹配 | `P19-UI-FIX-1` 历史债务 |
| 2 | `frontend-npm-build-final.log` SHA 不匹配 | `P19-UI-FIX-1` 历史债务 |
| 3 | `verification/P19/import-no-response-r4.md` SHA 不匹配 | worktree 镜像换行差异，环境性 |
| 4 | `DONE evidence_dir 含未登记文件`（8 个合并 1 条） | `P19-UI-FIX-1` 历史债务 |
| 5–9 | `Resource 最终路径未验证：Same ...`（5 条） | 检查器缺同源语义 → `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` |
| 10 | `Resource 最终路径未验证：p19-ui-fix-1-isolation-20261017` | 真实不存在 → 独立只读核实 Task |

## 待 Codex 收口（本 Task 之外）

r12 §执行顺序 2–3 明确 Plan / STATUS 由 **Codex 作为唯一权威写入者**修改：

1. Plan：`P19-UI-MANIFEST-VIEW-1` 行改为终态、从 READY 移除（**必须移除**，它不增加 done 计数）；
2. STATUS：需登记后继 ready Task 与 P19 终态指针。**注意 STATUS 替换后约 3198 / 3200 bytes，
   只剩 2 bytes 余量**，写入后必须实测并跑 checker；
3. 由 Codex 创建并释放 `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1`。

本 Task 未擅自修改 Plan / STATUS。

## 未做的事

- 未回退引用修正。
- 未修改 `verification/P19-UI-FIX-1/resource-manifest.json`（sha256 `b0772d93…` 前后一致）。
- 未改动任何 pin、历史证据或资源；未删除/迁移任何东西。
