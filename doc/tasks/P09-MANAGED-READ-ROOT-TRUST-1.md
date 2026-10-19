---
id: P09-MANAGED-READ-ROOT-TRUST-1
title: 托管文件读取/导出路径的 root 可信性（R5b P2 转交）
kind: security-hardening
status: proposed
owner: null
reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
delivery_head: null
created: 2026-10-19
---

# P09-MANAGED-READ-ROOT-TRUST-1

## 来源

由 `P09-AC3-DELETE-HARDEN-1` 的 R5b 复审转出（用户裁决路线 B）。**删除路径加固不含读取路径**，本 Task 单独处理。

## 范围（8 处，逐处验收）

| # | 位置 | 复现者 |
|---|---|---|
| 1–4 | `src/bootstrap/core_service.py` **464–467**、**1923–1926**、**2490–2493**、**2533–2542** | R5b |
| 5–7 | `src/bootstrap/core_assembly.py` **227–230**、**236–239**、**270–273** | R5b |
| **8** | **`src/infrastructure/resource_channel/handle_resolver.py` 的 `resolve_namespace_identity`（609–617）** | **R5b 与 R6 各自独立复现** |

**第 8 处的复现细节**：在 `_lstat_reparse_walk(path)` 之后、`path.resolve()` 时注入祖先 junction → **函数接受并返回 `outside\derived`**，**外部字节可读**。

**根因**：**它把句柄的最终路径与「已被重定向后的 `resolved` 名字」比对** —— **拿被污染的值验证自己**。

## 与删除路径的本质差异（**决定了这不是接线**）

| | 删除（已完成）| 读取（本 Task）|
|---|---|---|
| 手段 | **句柄 disposition，一次打开即可** | **句柄需保持打开并持续读**，窗口更长 |
| 现有基建 | ✅ `win_unlink.unlink_by_handle` | ❌ **无** |
| 修法性质 | **接线** | **新设计** |

## 必须先回答的设计问题

**「期望身份」从哪来？** 它必须是**在竞态发生前就已固定、且不随后续路径解析而变化的值**（例如**启动时对配置根的句柄身份快照**）。

**这是本 Task 的第一个交付物**，**不是实现细节**。

## 禁止范围

不改 IPC 契约、Schema、ACL、依赖；**不改删除路径**（那是 `P09-AC3-DELETE-HARDEN-1` 的范围）；**不采用「任一祖先段是 reparse 就拒绝」**作为默认方案 —— **它最简单但会破坏合法使用链接的用户**，**若最终采用必须显式记录取舍理由**。

## 验收方向

- **AC1**：R5b 的复现（祖先 junction → 读出 `outside bytes`）**被拒绝**
- **AC2**：**合法读取不回归**（含链接合法使用的场景 —— 需先明确产品是否允许）
- **AC3**：**8 处逐个**有测试或探针，**不接受「模式相同所以一起算」**
- **AC4**：不引入新依赖或契约变更
- **AC5**：`P09-AC3-DELETE-HARDEN-1` 的 9 个探针**不回归**

## 参考材料

- `verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md`（草案，**scope 与 AC3 已含第 8 处**）
- `verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md`（前序交付）
- `workspace/agent-output/coordinator/codex-r5b-result.md`、`codex-r6-result.md`（原始复现）
