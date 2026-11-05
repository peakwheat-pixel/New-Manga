# FEA-12-DSIM-1 — Environment（r2）

- 时间：2026-11-05（Asia/Shanghai）
- 仓库：`G:\CODEX\New Manga`（`main`；本卡不 push、不新建分支/worktree）
- base_commit：`37f84bb895c9ef9b64e3865f3a92b245f2e28a7c`（Task 释放提交）
- 实现 commits：
  - `94a12e93f` — feat：协议/模拟件/测试（5 files / +1625）
  - `3d0d325f7` — fix：目录指纹 junction 拒绝 + normcase（1 file / +54/−18）
  - **`d5925957b` — fix（r2）：R-001 自身写目标加固 + 8 项判别测试（2 files / +346/−4）**
- 交付 docs commit：本证据目录所在提交（见 r2 Handoff `doc/handoffs/FEA-12-DSIM-1-d5925957b.md`）

## per-commit scope 证明（Review r1 R-005）

`base..head` range 含其他任务（FEA-11-LINEAGE-1 r3/r4、FEA-12-PREREQ-1 r1/r2）与 Lead 生命周期指针 commit，**不是**本卡 delta；本卡自有 commit 的逐 commit 文件集如下（全部在 `allowed_paths` 内）：

| commit | 文件（逐项） | 越界 |
|---|---|---|
| `94a12e93f` | `src/application/maintenance/recycle_gateway.py`（新）、`src/application/maintenance/__init__.py`、`src/infrastructure/filesystem/simulated_recycle_bin.py`（新）、`tests/fea12/conftest.py`（新）、`tests/fea12/test_recycle_gateway_sim.py`（新） | 无 |
| `3d0d325f7` | `src/infrastructure/filesystem/simulated_recycle_bin.py` | 无 |
| `d5925957b` | `src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/test_recycle_gateway_sim.py` | 无 |
| （docs commit） | `doc/tasks/FEA-12-DSIM-1.md`、`doc/handoffs/FEA-12-DSIM-1-*.md`、`verification/FEA-12-DSIM-1/**` | 无 |

## 工具链

| 项 | 值 |
|---|---|
| Python | `C:\Python314\python.exe`（Python 3.14.6） |
| .NET SDK | `10.0.401`（`dotnet test --no-build`，沿用既有 Release 产物） |
| OS | Windows 11 专业版（`Microsoft Windows NT 10.0.26300.0`） |
| pwsh | PowerShell 7（`pwsh -NoProfile`） |

## 隔离根与数据路径

| 用途 | 路径 | 说明 |
|---|---|---|
| pytest 隔离根 | `tmp_path/isolated-root`（`tests/fea12/conftest.py::isolated_root`） | 唯一允许 `SimulatedRecycleBin` 写入的根；pytest 自动创建/清理 |
| pytest 哨兵树（隔离根外） | `tmp_path/outside-root`（`tests/fea12/conftest.py::outside_tree`） | 运行时证明"隔离根外零变化"；同样位于 `tmp_path` 内 |
| R-001 判别 fixture | `tmp_path` 内真实 NTFS junction（`mklink /J`）与硬链接（`os.link`） | 预置/重植攻击场景；测试 `finally` 中解除 junction、删除硬链接 |
| 哨兵探针 scratch | `tempfile.TemporaryDirectory()`（`tools/sentinel-probe.py`） | 与 pytest `tmp_path` 同族（OS temp），脚本结束自动清理 |
| **过程日志（仓外）** | `G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\`（`gates.log`、`check-final.log`、`check-final-r1.log`） | R-002 处置：证据目录只保留登记过的判别力证据；仓外日志由 `verification/FEA-12-DSIM-1/agent-output-manifest.json` 登记 bytes/sha256 |
| 仓外 temp（其它） | 未创建 | Resource Manifest：temp = NOT_APPLICABLE |

**数据边界（Review r1 R-008 修正）**：pytest `tmp_path` 与探针的 `TemporaryDirectory()` 运行时物理上位于 OS temp（本机 `C:\Users\<user>\AppData\Local\Temp\...`），属 ADJ-2026-11-05 §D7 允许的隔离根族；本卡**未读取/使用 `%APPDATA%` 等环境变量、未读写用户 AppData 业务数据、未触碰真实回收站/外部卷**。

## 并发工作树说明（不得混淆）

本卡 r2 期间共享工作树存在其它 teammate 的**未提交并发改动**，本卡未触碰、未提交：

- `FEA-12-CORE` 分片 A（`fea12-core-py`）：`src/application/{library,maintenance}/…`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/library.py`、`src/domain/books/entities.py` 等
- `FEA-12-CORE` 分片 B（`fea12-core-host`）：`apps/desktop-avalonia/src/NewManga.CoreClient/…`、`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`、对应测试
- Lead-owned：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/reviews/**`

因此全量 pytest / .NET 数字是在上述共享工作树实测；本卡自身只新增/修改：`src/application/maintenance/recycle_gateway.py`、`src/application/maintenance/__init__.py`（additive 导出）、`src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/**`、`doc/tasks/FEA-12-DSIM-1.md`、`doc/handoffs/FEA-12-DSIM-1-*.md`、`verification/FEA-12-DSIM-1/**`。
