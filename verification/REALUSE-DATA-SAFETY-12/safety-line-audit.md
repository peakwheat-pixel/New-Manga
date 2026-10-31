# SAFETY 线收尾审计（REALUSE-DATA-SAFETY-12）

日期：2026-11-01。Owner：DSH。审计基线：`main@7ace93780`（SAFETY-11 集成后）。

## 1. 结论

SAFETY 线（SAFETY-6 → SAFETY-11 六个 Task）**全部 `done` 且已集成**，P2 处置链**闭合**：
每条 P2 要么在当轮处置、要么转下一个 Task 并在其 AC 内闭环，没有未登记的悬挂项（全量 17 条，含 SAFETY-6 的 3 条）。
`check.ps1` PASS；STATUS/PLAN/LEDGER 与各卡 front matter 一致。

## 2. Task 与集成点

| Task | 结论 | 集成 commit | Review |
|---|---|---|---|
| REALUSE-DATA-SAFETY-6 | done | **`011b19bbf`（merge）**；`b94dc3d86`（治理检查）/ `82e86e97b`（manifest） | approved（P2×3 转 SAFETY-7） |
| REALUSE-DATA-SAFETY-7 | done | `aaed145e9` | approved，P2×5（F-001…F-005） |
| REALUSE-DATA-SAFETY-8 | done | `84b9f4319` | approved，P2×3（R-001…R-003） |
| REALUSE-DATA-SAFETY-9 | done | `9aa6758b6` | approved，P2×1（R-101） |
| REALUSE-DATA-SAFETY-10 | done | `8b15adbfe` | approved（最终版；Codex 首轮 blocked 的 RV-001/RV-002 已修） |
| REALUSE-DATA-SAFETY-11 | done | `a1b82ffb9` | approved，P2×2（R-102-A/B，集成前已处置） |

## 3. P2 处置链

| 来源 | P2 | 内容摘要 | 处置 | 落地证据 |
|---|---|---|---|---|
| SAFETY-6 | R-001 | 关闭浮层与在途保存并发：镜像回调解引用已置 null 的 `_book` → 未捕获 NRE；关闭时权威重读被跳过 | 转 SAFETY-7 AC1 → `await` 前局部固化 book/chapter/page + `CloseAsync` 先等待在途保存 | `ReaderOverlayViewModel`；SAFETY-7 `ac1-fix.md` |
| SAFETY-6 | R-002 | 证据 pin 受 CRLF/LF 影响（worktree 10/11、blob 6/11；`E-GOV-CHECK` pin 不符） | 转 SAFETY-7 AC2 → `.gitattributes` `verification/** text eol=lf` + 重算 pin（blob 基准） | SAFETY-7 `ac2-eol-pin.md`；SAFETY-8 Review 12/12 |
| SAFETY-6 | R-003 | AC1 测试日志缺 EXIT 与完整命令；负向对照为散文摘要 | 转 SAFETY-7 AC3 → 日志补 `generated_at`/完整命令/`EXIT=`/可复现负向步骤 | SAFETY-7 `ac3-log-format.md`、`ac1-fix-tests.txt` |
| SAFETY-7 | F-001 | `ac2-eol-pin.md` 计数与实际不符 | 转 SAFETY-8 → 12 pin 表 + 5 条变化 | SAFETY-7 `ac2-eol-pin.md`（`60056d353` 修订）；12/12 由 SAFETY-7 Review（`:101/:126`）与 SAFETY-8 Review（`:82`）复核 |
| SAFETY-7 | F-002 | 负向对照是提交前配方、交付 head 上为空操作 | 转 SAFETY-8 → post-delivery 配方并实测 | SAFETY-7 `ac1-negative-control.md`（post-delivery 配方）；SAFETY-9 复现 |
| SAFETY-7 | F-003 | filtered 未进 canonical 日志、缺 cwd | 转 SAFETY-8 → 日志补 cwd/filtered/EXIT | SAFETY-8 `ac1-fix-tests.txt` |
| SAFETY-7 | F-004 | `CloseAsync` 的 `catch (Exception)` 静默吞未知异常 | 转 SAFETY-8 → 类型限定 + 通用 catch 可见化 | SAFETY-8 AC2；`ReaderOverlayViewModel` |
| SAFETY-7 | F-005 | closing 窗口内翻页可跳过权威重读 | 转 SAFETY-8 → `_isClosing` 门禁 + 循环等待 + 判别性断言 | SAFETY-8 AC3；SAFETY-9 判别性补强 |
| SAFETY-8 | R-001 | manifest 声称删除的 tmp 日志仍在 | **当轮闭环**（集成前删除，`Test-Path=False`） | SAFETY-8 manifest |
| SAFETY-8 | R-002 | AC3 用例不判别修复 | 转 SAFETY-9 → `PageIndex == 3` 判别性断言 + pre-F-005 负向对照 | SAFETY-9 `ac1-discriminating.md` |
| SAFETY-8 | R-003 | 证据文档写入未发生的 Review 结论 | 转 SAFETY-9 → 只引用已入库报告 | SAFETY-7 `ac2-eol-pin.md` |
| SAFETY-9 | R-101 | 负向对照转录不完整（无位置/命令/host/失败明细） | 转 SAFETY-10 → 四点补齐 | SAFETY-9 `ac1-discriminating.md` |
| SAFETY-10（Codex） | RV-001 | E-AC1-DOC pin 未跟随修正版 | **当轮修复** | SAFETY-10 卡 `4d2658dd6` / `7c00accf…` |
| SAFETY-10（Codex） | RV-002 | 证据表行被字面字符拼接 | **当轮修复** | 同上（两条独立行） |
| SAFETY-10 | R-102 | 转录超出所附日志范围 | 转 SAFETY-11 → 完整五步日志（217 行） | `ac1-negative-control-full.txt` |
| SAFETY-11 | R-102-A | 引用与执行位置/时间不一致 | **当轮处置** | `e2eb824e0` |
| SAFETY-11 | R-102-B | AC 勾选与 PARTIAL 标记并存 | **当轮处置** | 同上，改 `<<MET>>` |

合计 **17 条 P2**：当轮处置 5 条、转后续并闭环 12 条；**0 条悬挂**。

## 4. 治理一致性

| 检查 | 结果 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | PASS (3 warnings：非终态 Task 计数、STATUS/PLAN 预算 80%) |
| STATUS 当前 Task 指针 | 指向 `REALUSE-DATA-SAFETY-12`（非终态，可解析） |
| PLAN READY 节点 / 当前 DAG | `READY 无` / 当前 DAG = `REALUSE-DATA-SAFETY-12`（in_progress） |
| TASK_LEDGER 非终态计数 | 与各卡 front matter 一致（`7ace93780` 时已重跑 `task_ledger.py --write`；本审计提交未再改 ledger） |
| SAFETY-10 卡上游遗留 | 已补正为 `done`（`6f23b8ce5`），并登记 `E-AC1-LOG-FULL` pin |

## 5. 遗留（不在本线范围）

- SAFETY 线的保护语义依赖 ADJ-001（`G-DELETE-CONTRACT: OPEN`）与 AD-003（`G-REVIEW: ADDRESSED_PENDING_R2`）——契约冻结前不得据此声称"删除语义已冻结"。
- FEA 线：C-01b r2 `changes_requested`（1 P1 + 8 P2），待 r3；`U-02/U-03/U-04` 等仍待用户裁决。
