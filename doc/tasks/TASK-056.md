---
id: TASK-056
title: TASK-021 冻结子集②：缓存·版本·模型清理
kind: implementation
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-021, TASK-053, TASK-054]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-056-cache-version-cleanup
worktree: G:/CODEX/New Manga.worktrees/TASK-056-zcode
integration_commit: null
---

# TASK-056：缓存·版本·模型清理（TASK-021 冻结子集②）

**READY（2026-09-19，ZCode 全权窗口 W9）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-053 已集成**（清理面须先无已知缺陷：孤儿文件/run 累积）。

## 来源与目标

来源＝TASK-021 冻结子集之一。已知相关面：瓦片缓存（`src/infrastructure/imaging/webtoon_tiles.py` 的 `clear()`、`_TILE_CACHE_FORMAT` 升版遗留 v1 文件——见 TASK-045 R-005/R-102）、artifact/revision 与 Managed Copy 的清理边界。

**目标**：提供**受控清理**能力（缓存/垃圾版本/模型外部文件），**永不触碰用户源文件与 current/pinned revision**；每一项清理都可诊断、可预览、可取消。

## Acceptance Criteria

- [ ] **AC ①（范围与安全边界）**：明确列出"可清理"与"永不清理"（用户源文件、current/pinned revision、Lock 保护对象）；清理仅在受控副本/缓存/生成资产范围内。
- [ ] **AC ②（预览与结果）**：清理前可统计将删除的对象与字节数；执行后返回结构化结果（成功/失败/跳过及原因）。
- [ ] **AC ③（瓦片缓存跨代回收）**：把 TASK-045 R-005 的"升版遗留旧瓦片"纳入回收范围（一次性清理 `tile-*.png` 各代），并有用例。
- [ ] **AC ④（幂等与失败）**：重复清理幂等；文件删除失败不得静默（可诊断 + 可重试，复用 TASK-053 的清单化思路）。
- [ ] **AC ⑤（不回归 + 判别力）**：全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑥** Handoff + `verification/TASK-056/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/**`、`src/infrastructure/**`（清理相关；**待按实际结构收紧**）
- `tests/**`（对应目录）
- 本 Task、Handoff、`verification/TASK-056/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`AGENTS.md`、其他 Task、`src/ui/qml/**`；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`，前置 TASK-053）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 开立为 `ready`（窗口 W9）。**实施尚未开始。**
