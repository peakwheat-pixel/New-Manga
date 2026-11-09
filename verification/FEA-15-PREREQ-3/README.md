# FEA-15-PREREQ-3 证据索引：集成验收准备

- Task：`FEA-15-PREREQ-3`（准备卡，零生产代码变更）
- Base：`afbc7e411`；日期：2026-11-09

## 交付

| 项 | 结果 |
|---|---|
| 隔离干净构建 | 全新 worktree `G:\CODEX\New Manga.workspace\FEA-15-PREREQ-3`（detached @ `afbc7e411`，无 bin/obj）→ `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`：**0 警告 / 0 错误，EXIT 0** |
| 验收矩阵 | `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md`（A1–A7 状态、可验收子集、FEA-14 切片顺序、正式验收前置 5 条） |

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 干净构建 | Release 0/0，EXIT 0；worktree 与 head 记录于日志头 | `logs/clean-worktree-build.log`（sha256 `e4d0c5db818946906ee571d4d265674ce0e7de370119dcd1638e86bb2e0b411b`） |
| AC2 验收矩阵 | A1–A7 状态与前置清单齐备，明确「准备版不构成正式验收」 | `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md` |
| AC3 门禁 | `check.ps1` 默认 + `-TaskPath` PASS；`verify_pins` 18/18 | 卡/Handoff |

## 说明

- 正式验收项（安装 / 真实双 UI 会话 / 真实旧库升级与回退）按计划待 FEA-14 与安装包；本卡**不得**替代 A2/A3/A4。
- worktree 保留为构建证据（删除须按 `WORKTREE_SAFETY_INVENTORY` 流程）。