---
id: TASK-056
title: TASK-021 冻结子集②：缓存·版本·模型清理
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-021, TASK-053, TASK-054]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-056-cache-version-cleanup
worktree: G:/CODEX/New Manga.worktrees/TASK-056-zcode
integration_commit: 11517ac
---

# TASK-056：缓存·版本·模型清理（TASK-021 冻结子集②）

**READY（2026-09-19，ZCode 全权窗口 W9）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-053 已集成**（清理面须先无已知缺陷：孤儿文件/run 累积）。

## 来源与目标

来源＝TASK-021 冻结子集之一。已知相关面：瓦片缓存（`src/infrastructure/imaging/webtoon_tiles.py` 的 `clear()`、`_TILE_CACHE_FORMAT` 升版遗留 v1 文件——见 TASK-045 R-005/R-102）、artifact/revision 与 Managed Copy 的清理边界。

**目标**：提供**受控清理**能力（缓存/垃圾版本/模型外部文件），**永不触碰用户源文件与 current/pinned revision**；每一项清理都可诊断、可预览、可取消。

## Acceptance Criteria

- [x] **AC ①（范围与安全边界）**：明确列出"可清理"与"永不清理"（用户源文件、current/pinned revision、Lock 保护对象）；清理仅在受控副本/缓存/生成资产范围内。 <!-- verified: 装配接线与 wire 级安全边界均已验：`src/bootstrap/core_assembly.py:1404` 构造 `CleanupService`、`src/bootstrap/core_service.py` 暴露 cleanup 命令族；wire 测试 `test_run_skips_business_files_and_dotdot_traversal`（业务文件与 `..` 遍历被跳过）与 `test_missing_service_fails_closed_with_core_unavailable`（缺失服务 fail-closed）在**真实 production assembly** 上通过。受控范围由 `is_safe_relative_path@src/application/maintenance/cleanup.py:229` + `_safe_targets@:193` 界定；模型目录不在受控清理范围内，符合 AC「仅在受控副本/缓存/生成资产范围内」。 -->
- [x] **AC ②（预览与结果）**：清理前可统计将删除的对象与字节数；执行后返回结构化结果（成功/失败/跳过及原因）。 <!-- verified: wire 级已验证：`test_preview_lists_targets_bytes_and_pending_count`（预览给出目标/字节数/pending 计数）、`test_run_removes_cache_generations_and_returns_structured_counts`（执行后返回结构化计数）、`test_preview_empty_cache_reports_zero_and_removes_nothing`（空缓存零目标）；命令暴露于 `core_service.py` 的 application command 族（`test_cleanup_commands_are_application_commands_not_host_control`）。 -->
- [x] **AC ③（瓦片缓存跨代回收）**：把 TASK-045 R-005 的"升版遗留旧瓦片"纳入回收范围（一次性清理 `tile-*.png` 各代），并有用例。 <!-- verified: `WebtoonTileCacheSweeper@src/infrastructure/imaging/tile_cache_sweep.py:22` + 单元用例 `test_lists_every_generation_relative_to_managed_root@tests/maintenance/test_cleanup.py:90`、`test_missing_cache_dir_is_empty@:101`；wire 级 `test_run_removes_cache_generations_and_returns_structured_counts` 在真实 assembly 上验证各代 `tile-*.png` 一次性回收并返回计数。 -->
- [x] **AC ④（幂等与失败）**：重复清理幂等；文件删除失败不得静默（可诊断 + 可重试，复用 TASK-053 的清单化思路）。 <!-- verified: wire 级已验证三条：`test_run_is_idempotent`（重复清理幂等）、`test_failed_removal_is_persisted_as_pending`（删除失败持久化为 pending，不静默）、`test_retry_clears_pending_after_the_fault_is_gone`（故障消除后重试清空 pending）；实现 `retry_pending_cleanups@src/application/maintenance/cleanup.py:160` + `pending_cleanup_count@:188`。 -->
- [x] **AC ⑤（不回归 + 判别力）**：全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。 <!-- verified: 当前全仓基线复算 **3569 passed / 0 failed / 10 skipped**（338.61s，verification/AC-RERUN-CLOSE-1/full-suite-run1.log）。**限制说明**：历史 ≥5 次逐次记录（verification/TASK-056/full-suite-run1.log … run5.log，各 900 passed / EXIT 0）是**旧套件时代**的记录；当前架构（3569 collected）仅 1 次全仓复算。两者的「不减少」是跨测试集比较（900→3569 为测试面扩张），非同一测试集重复 5 次。旧 PySide6/QML 壳测试已归档（apps/desktop/LEGACY_FROZEN.md:25）。独立复核 r1 的 F-01 已记录该强度限制。 -->
- [ ] **AC ⑥** Handoff + `verification/TASK-056/**` + 独立子对话 Review + 集成 + STATUS 台账行。 <!-- blocked: Handoff/verification/Review/集成俱在（file:doc/handoffs/TASK-056-delivery.md + file:verification/TASK-056/ + file:doc/reviews/TASK-056-15f977a.md + 集成 commit 11517ac 可解析），但缺 STATUS 台账行：doc/STATUS.md 与 doc/TASK_LEDGER.md 均无 TASK-056 行（grep 0 命中）；另卡面 48 行保留「装配接线与模型目录 NOT_RUN」。 -->

## 允许修改范围

- `src/application/**`、`src/infrastructure/**`（清理相关；**待按实际结构收紧**）
- `tests/**`（对应目录）
- 本 Task、Handoff、`verification/TASK-056/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`AGENTS.md`、其他 Task、`src/ui/qml/**`；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：[TASK-056-delivery.md](../handoffs/TASK-056-delivery.md)。Review：尚无（待窗口独立子对话 Review）。实际测试：新套件 8/0 + 全仓 ×5（900/0，=892 基线 + 8），入库 `verification/TASK-056/`。
- **集成完成（2026-09-19，当前）**：首轮独立子对话 Review `approved_subagent`（[TASK-056-4c8b8a7](../reviews/TASK-056-4c8b8a7.md)；R-001 P2 守卫建议）→ 守卫修订 `15f977a` → 复审 `approved_subagent`（[TASK-056-15f977a](../reviews/TASK-056-15f977a.md)，固定被审 `15f977a`）→ ZCode 按窗口授权代行集成 `11517ac`（--no-ff，其上已含并行会话 W0–W4/W6–W8），集成后 master 复跑 904/0 ×2。装配接线与模型目录 NOT_RUN（见 Handoff）。历史：2026-09-19 ZCode 实现（实现提交 `cae3dd3`）：`cleanup.py` 受控清理框架（前缀白名单边界/预览/结构化结果/幂等/pending 重试）+ `tile_cache_sweep.py` 跨代枚举；装配接线 NOT_RUN（同 TASK-055 口径）；模型目录未注册（窗口排除项）。`base=8bf8da3`（开工已 merge master `c083f60`，含 W0–W3/W6–W8）。
