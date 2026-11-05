# FEA-12-PREREQ-1 — Environment

- 时间：2026-11-05（Asia/Shanghai）
- 仓库：`G:\CODEX\New Manga`（main；首日实现 head 以交付 commit 为准）
- 基线：`base_commit = 035468a81e43e8d70fb711536824cdf613a7a0c4`
- OS：Windows 10.0.26300
- PowerShell：7.6.8（.NET 10.0.13）
- .NET SDK：10.0.401；目标框架 net9.0（solution 既有配置）
- Python：`C:/Python314/python.exe`
- 冻结 sidecar（AC11 无标签副本）：`G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy`
  （`core_service.exe` / `host_bridge.exe` / `catalog_loader.exe`，只读复用，本卡未修改）
- 负向对照基线 worktree：`G:\CODEX\New Manga.workspace\task-envs\FEA-12-PREREQ-1\baseline-worktree-035468a81`
  （detached HEAD `035468a81`；**保留不删**，处置建议见 Handoff/Resource Manifest）
- 隔离数据根：
  - 基线 live Core 探针：`G:\CODEX\New Manga.workspace\temp\FEA-12-PREREQ-1\baseline-live-core`
  - 测试 evidence：`verification/FEA-12-PREREQ-1/test-evidence/`（`NEWMANGA_EVIDENCE_DIR` 显式指向仓内本卡证据目录）
  - sidecar 测试实际数据根由 `SidecarFixture` 建在系统临时目录（`%TEMP%/newmanga-host-client-tests/**`，测试后自清理），未触碰 `%APPDATA%`/真实数据/外部卷/真实回收站
- 构建/测试命令与日志：见 `logs/`（每条记录含命令、EXIT、结果摘要）

## 本卡不触碰

- `src/**`（Python 生产代码）：`rev213-diff-audit.ps1` 断言 `src_touched_count=0`
- 18 个 pinned 冻结契约（`doc/plan/FEA-C*`）：断言 `pinned_contracts_changed=0`
- 真实用户数据 / AppData / 外部卷 / 真实回收站 / push
