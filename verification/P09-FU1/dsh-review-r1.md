---
task_id: P09-FU1
title: 同步 legacy stub decoder 测试到 P09 真实 decoder 语义
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P09-FU1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 693019756e5a1731d1d4f9e02a52ee178f141354
declared_delivery_head: e5741448ab706a1337efbe81792d0e0af644e702
reviewed_head: c15cb9589917aaecc8e54fb8b4ef0152619a0d6b
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P09-FU1-DECODER-TEST
date: 2026-10-16
mode: 只读审查 + 独立 Git/日志复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
decision: approved
---

# P09-FU1 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 69301975..HEAD` | **6 个路径，全部在授权范围** |
| **产品实现零改动** | 过滤 `^(src\|apps\|packaging)/` | **空** ✅ —— 未通过放宽实现来"修测试" |
| 越界路径 | 反向过滤授权集合 | **空** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 测试日志真实性 | 独立读原始日志末尾 | `tests/core`：**261 passed, EXIT_CODE=0**；`tests/core+import_formats+library`：**342 passed, EXIT_CODE=0** |
| 断言改法 | 读 `tests/core/test_stub_decoder.py` | 见 §1 |

## 1. AC 逐项结论

| AC | 判定 | 依据 |
|---|---|---|
| AC1 生产装配语义 | **接受** | 测试现断言 `isinstance(decoder, QtImageDecoder)`；合法 PNG → **真实尺寸 `(16, 12)`**；非法 `b"fake"` → `pytest.raises(ImageDecodeError)`。与 `core_service.py:370` 的生产注入完全一致 |
| AC2 legacy double 定位 | **接受** | `test_stub_decoder_passthrough_any_payload_does_not_raise` 保留，docstring 明确 `Only covers the retained legacy test double; it does not describe production assembly`；`1×1` 断言只作用于 legacy double |
| AC3 `tests/core` | **接受** | 261 passed / exit 0（原始日志已独立复核） |
| AC4 扩展基线 | **接受** | 342 passed / exit 0（原始日志已独立复核）——**P09 Review F2 的基线破坏已修复** |
| AC5 Review + 集成 | **Review 由本文件闭合；集成由 Coordinator 执行** | Task 保持 `in_review`，未越权标完成 |

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| F1 | P3（流程，同 BL-7） | `delivery_head` 申报 `e5741448`（实现/验证 commit），实际 HEAD=`c15cb958`（归档 commit） | 本次 Task 已明确区分两者；closeout 冻结实际 HEAD |
| F2 | P4 | Task 契约的 AC5 同时包含"固定 head 并写 Handoff"与"非作者 Review + 集成"两件事，Owner 只能闭合前者 | 契约表述可优化（拆分），不阻塞；不影响结论 |
| F3 | P4 | 两组 pytest 各有 1 条既有 Pillow 弃用 warning | 与本次变更无关，登记观察即可 |

**无 P0/P1/P2 finding。** 修复方向正确：**改测试以匹配正确的实现**，而非放宽实现以迁就旧测试。

## 3. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `c15cb9589917aaecc8e54fb8b4ef0152619a0d6b`。
- **C2**：closeout 将本 Review 登记为 CANONICAL 证据（`verification/P09-FU1/` 是 evidence_dir）。
- 无返修要求。

## 4. 能力边界

- 本 Review 覆盖测试变更的范围合规与断言正确性；**不代表**全仓 pytest（未执行 `tests/` 全集）。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
