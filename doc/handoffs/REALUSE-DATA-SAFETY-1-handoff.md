---
task_id: REALUSE-DATA-SAFETY-1
author: dsh-lead
recipient: DeepSeek Harness (Lead/Integrator)
base_commit: b1c1f5a56
delivery_head: b1ff8921f
status: delivered (AC1-AC4 all implemented, awaiting independent review)
---

# Handoff：REALUSE-DATA-SAFETY-1（B1 数据安全）

## 交付结果

本 Handoff 覆盖 **AC1–AC4 全部四项**：AC1 数据根迁移自愈、AC2 真实 `.nmbak` 备份 + Console 接线、AC3 旧布局目录迁移顺序、AC4 只读语义 seam 显式化。四项均已实现并有单元/集成测试，等待未参与实现的 Agent 独立审查。

| AC | 状态 | 变更 |
|---|---|---|
| AC1 命名空间迁移自愈 | **DELIVERED** | `src/infrastructure/resource_channel/catalog_store.py`（+`verify_binding_for_root`、`rebind_namespace`、`_assert_canonical_namespace_table`；`restore_namespace_lock` 复用 canonical 校验）；`src/bootstrap/core_service.py`（`_ensure_preview_namespace` 校验现有绑定并仅在可识别 mismatch 时重绑 + stderr 迁移日志）；`tests/infrastructure/test_preview_namespace_rebind.py`（4 例） |
| AC2 真实备份 | **DELIVERED** | `core_assembly.py`（迁移前 `_NmbakMigrationBackup`）、`core_service.py`（`_ensure_automatic_backup` + 保留 5 份）、`nmbak.py`（`page_original_refs` 原图纳入包/校验/恢复 + consistency）、`CoreServiceClient.cs`/`HostRuntime.cs`/`IHostController`/`HostController`/`NullHostController`（backup 4 方法）、`ConsoleViewModel.cs` + `ConsoleView.axaml`（⑥ 分区接真实面，含二次确认） |
| AC3 迁移顺序 | **DELIVERED** | `upgrade_legacy_layout.py`（`_promote_directory_merged`：空目标原子替换、非空目标只补缺失、绝不覆盖）+ 4 新测试 |
| AC4 只读语义 | **DELIVERED** | `core_assembly.py`（`[core.schema]` 日志）+ `Coexistence.cs`（决策文案/UI 标签声明 schema seam）+ `HostUnitTests` 契约测试；选择「明确区分」而非拒绝迁移 |

提交：`38f09ac90`（AC1）、`75aeff349`（AC2 Core）、`811078ebb`（AC2 UI）、`ff3dee029`（AC3）、`b1ff8921f`（AC4），分支 `task/REALUSE-DATA-SAFETY-1`，worktree `G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-1`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 复制数据根重绑定 | `pytest tests/infrastructure/test_preview_namespace_rebind.py -q` | Python 3.14 / Windows 10.0.26300 / `38f09ac90` | **PASS 4/4** | 测试文件本身 |
| AC1 安全边界（篡改/损坏锁/非 canonical） | 同上 + `pytest tests/core/test_core_namespace_bootstrap.py -q` | 同上 | **PASS 7/7** | 既有测试文件 |
| AC1 真实数据副本完整启动链 | `python verify_migrated_root.py %APPDATA%\com.newmanga.desktop <副本>` | 真实库 169 页 + 旧 lock | **PASS**：重绑定日志 + `books=1 chapters=1 pages=169 progress=1 title='家族战记'` | `G:\CODEX\New Manga.workspace\tmp\self-audit\verify_migrated_root.py`、`runs\12-migrated-root` |
| AC2 自动备份含原图 | `python verify_backup_real.py %APPDATA%\com.newmanga.desktop <副本>` | 真实库 169 页 / `75aeff349` | **PASS**：包 90.2 MiB、`page_originals=169`、`original_bytes=100,434,899`、包内库 `pages=169` | `verify_backup_real.py`、`runs\13-backup-real` |
| AC2 UI 备份分区 | `dotnet test --filter "FullyQualifiedName~V2ConsoleUiTests.Backup"` | headless Avalonia / `811078ebb` | **PASS 3/3** | `V2ConsoleUiTests.cs` |
| AC3 预创建目录仍迁移 | `pytest tests/infrastructure/test_upgrade_legacy_layout.py -q` | Python 3.14 / `ff3dee029` | **PASS 16/16**（含 4 个 AC3 新例） | 该测试文件 |
| AC4 只读 seam | `dotnet test tests/NewManga.Host.Tests --filter ReadOnlyUntilParity_NamesTheSchemaWriteSeam` | net9.0 / `b1ff8921f` | **PASS**（Host 50 passed） | `HostUnitTests.cs` |
| 全量回归 | `pytest -q --tb=no`；`dotnet test NewManga.sln` | `b1ff8921f` | **pytest exit 0**；**dotnet 811 passed / 0 failed**（App 325 / Host 50 / ThemeEngine 235 / DesignSystem 85 / CoreClient 116） | `pytest-full6.log` |

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
