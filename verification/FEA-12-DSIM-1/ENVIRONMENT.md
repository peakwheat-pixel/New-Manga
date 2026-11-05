# FEA-12-DSIM-1 — Environment

- 时间：2026-11-05（Asia/Shanghai）
- 仓库：`G:\CODEX\New Manga`（`main`；本卡不 push、不新建分支/worktree）
- base_commit：`37f84bb895c9ef9b64e3865f3a92b245f2e28a7c`（Task 释放提交）
- 实现 commit：`94a12e93fdfad756bfe6f0fdd72a25de2bbd688b`（`feat(fea-12-dsim-1)`：实现 + 测试，5 files / +1625）
- 交付 commit：本证据目录所在 docs 提交（见 `doc/handoffs/FEA-12-DSIM-1-94a12e93f.md`）

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
| pytest 隔离根 | `tmp_path/isolated-root`（`tests/fea12/conftest.py::isolated_root`） | 唯一允许 `SimulatedRecycleBin` 写入的根；`pytest` 自动创建/清理 |
| pytest 哨兵树（隔离根外） | `tmp_path/outside-root`（`tests/fea12/conftest.py::outside_tree`） | 运行时证明"隔离根外零变化"；同样位于 `tmp_path` 内 |
| 哨兵探针 scratch | `tempfile.TemporaryDirectory()`（`tools/sentinel-probe.py`） | 与 pytest `tmp_path` 同族（OS temp），脚本结束自动清理；不创建 workspace temp 资源 |
| 仓外 temp / agent-output | 未创建 | Resource Manifest 记为 NOT_APPLICABLE |

**未使用**：`%APPDATA%`/`%LOCALAPPDATA%`/`%USERPROFILE%` 环境变量、真实盘符路径、`$Recycle.Bin`、真实用户数据、AppData、外部卷、真实回收站；**未调用任何 Windows 回收站 API**（见 `logs/static-scan.log`）。

## 并发工作树说明（不得混淆）

本卡实施期间工作树存在其它 teammate 的**未提交并发改动**，本卡未触碰、未提交：

- `FEA-11-LINEAGE-1 r3`：`src/application/{rendering,services}/…`、`src/bootstrap/core_assembly.py`、`src/infrastructure/{providers,sqlite}/…`、`tests/fea11/**`
- `FEA-12-PREREQ-1 r2`：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1`

因此本卡全量 `pytest tests` / `dotnet test` 的数字是在上述并发工作树上实测（见 `logs/gates.log` 与 Handoff「风险与遗留」）；本卡自身只新增/修改：`src/application/maintenance/recycle_gateway.py`（新增）、`src/application/maintenance/__init__.py`（仅 additive 导出）、`src/infrastructure/filesystem/simulated_recycle_bin.py`（新增）、`tests/fea12/**`（新增）、`doc/tasks/FEA-12-DSIM-1.md`、`doc/handoffs/FEA-12-DSIM-1-94a12e93f.md`、`verification/FEA-12-DSIM-1/**`（新增）。
