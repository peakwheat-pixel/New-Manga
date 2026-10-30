---
task_id: REALUSE-DATA-SAFETY-1
author: dsh-lead
recipient: DeepSeek Harness (Lead/Integrator)
base_commit: b1c1f5a56
delivery_head: 38f09ac90
status: partial (AC1 delivered, AC2/AC3/AC4 pending)
---

# Handoff：REALUSE-DATA-SAFETY-1（B1 数据安全）

## 交付结果

本 Handoff 覆盖 **AC1**（数据根迁移自愈）；AC2（真实备份）、AC3（迁移顺序）、AC4（只读语义）尚未开始。

| AC | 状态 | 变更 |
|---|---|---|
| AC1 命名空间迁移自愈 | **DELIVERED** | `src/infrastructure/resource_channel/catalog_store.py`（+`verify_binding_for_root`、`rebind_namespace`、`_assert_canonical_namespace_table`；`restore_namespace_lock` 复用 canonical 校验）；`src/bootstrap/core_service.py`（`_ensure_preview_namespace` 校验现有绑定并仅在可识别 mismatch 时重绑 + stderr 迁移日志）；`tests/infrastructure/test_preview_namespace_rebind.py`（4 例） |
| AC2 真实备份 | PENDING | 无变更 |
| AC3 迁移顺序 | PENDING | 无变更 |
| AC4 只读语义 | PENDING | 无变更 |

提交：`38f09ac90`（分支 `task/REALUSE-DATA-SAFETY-1`，worktree `G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-1`）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 复制数据根重绑定 | `pytest tests/infrastructure/test_preview_namespace_rebind.py -q` | Python 3.14 / Windows 10.0.26300 / `38f09ac90` | **PASS 4/4** | 测试文件本身 |
| AC1 安全边界（篡改/损坏锁/非 canonical） | 同上 + `pytest tests/core/test_core_namespace_bootstrap.py -q` | 同上 | **PASS 7/7** | 既有测试文件 |
| AC1 真实数据副本完整启动链 | `python verify_migrated_root.py %APPDATA%\com.newmanga.desktop <副本>` | 真实库 169 页 + 旧 lock | **PASS**：重绑定日志 + `books=1 chapters=1 pages=169 progress=1 title='家族战记'` | `G:\CODEX\New Manga.workspace\tmp\self-audit\verify_migrated_root.py`、`runs\12-migrated-root` |
| 全量回归 | `python -m pytest -q --tb=line` | 同上 | **2727 passed, 12 skipped, 0 failed** | `G:\CODEX\New Manga.workspace\tmp\self-audit\pytest-full2.log` |

未运行：`dotnet test NewManga.sln`（本 AC 无 C# 变更；AC2/AC3 接线时需要）、sidecar PyInstaller 构建（本机无 PyInstaller；AC1 用源码级启动链覆盖同一路径）。

## 接收方式

- 分支：`task/REALUSE-DATA-SAFETY-1`；worktree：`G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-1`
- 复现：`python -m pytest tests/infrastructure/test_preview_namespace_rebind.py tests/core/test_core_namespace_bootstrap.py -q`
- 实机：`python G:\CODEX\New Manga.workspace\tmp\self-audit\verify_migrated_root.py %APPDATA%\com.newmanga.desktop <空目录>`
- 依赖：无新增第三方依赖；未改 schema。

## 下一任务建议（必填）

- Task ID / 标题：**REALUSE-DATA-SAFETY-1 续作（AC2）**——首次写入/迁移前的真实 `.nmbak` 备份与 Console 备份恢复接线
- 推荐 Agent / Reviewer：实现 DSH（current owner）；**独立 Reviewer 必须未参与实现**（Codex / ZCode / Antigravity），Lead 不得审自己代码
- 推荐原因与前置依赖：AC1 只解决「迁移后能启动」，AC2 才解决「数据损坏可恢复」（MA-03 P1）；无硬前置
- Recovery point：仓库 `G:\CODEX\New Manga`；branch `task/REALUSE-DATA-SAFETY-1`；base `b1c1f5a56`；当前 head `38f09ac90`
- 允许修改路径：见 Task frontmatter（`DataSafety.cs`、`HostRuntime.cs`、`HostCommandRegistry.cs`、`IHostController/HostController`、`Console/**`、`tests/**`、`verification/REALUSE-DATA-SAFETY-1/**`）
- 禁止范围与新增授权条件：不得清空/改写真实 `%APPDATA%`；不得改 schema；不得 push
- 交付物：备份单测 + UI 截图 + 恢复验证；AC2 标 `<<MET>>` 前须有「删库后恢复出 169 页」证据
- 验证命令、环境与完成 Gate：`python -m pytest -q`；`dotnet test apps/desktop-avalonia/NewManga.sln`；0 失败 + AC 逐项证据
- 可直接转发给 Agent 的指令：见本文件「接收方式」与 Task 文档 AC2 段落
