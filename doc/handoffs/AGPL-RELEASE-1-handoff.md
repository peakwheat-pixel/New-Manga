---
task_id: AGPL-RELEASE-1
author: region-workbench-owner
recipient: DeepSeek Harness
base_commit: d8aadc0deb9bcd696953a75ce6b65a7bab54b5e5
delivery_head: 35fd83c3ab28e0f3293238bd17543c5cec2f8e91
status: in_review
---

# Handoff：AGPL-RELEASE-1（models 包 AGPL-3.0 声明落地 + AGPL 全文随包 + 重打包验证）

## 交付结果

- Task：`doc/tasks/AGPL-RELEASE-1.md`（shared task-2）；Owner `region-workbench-owner` / Reviewer `dsh`。
- Branch / Worktree：`task/AGPL-RELEASE-1` / `G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1`。
- 基线：worktree 起点 `7f0d1daef`（任务卡登记 base `d8aadc0de`）。
- 实现提交：`80fe5cde23b1ead55fd3a2b961a15124fc7b031a`。
- 证据提交 / **delivery head**：`35fd83c3ab28e0f3293238bd17543c5cec2f8e91`。
- 本 Handoff 与 Task 卡为紧随 delivery head 的文档提交（rebase main 后；不改代码/证据内容）。
- 未 push；未改产品源码/Core/旧壳/冻结契约；未改 `LICENSE`（GPL-3.0 原文）；未覆盖 RELEASE-REPACK-5 out。

| AC | 结论 | 证据（`verification/AGPL-RELEASE-1/`） |
|---|---|---|
| AC1 权重与许可事实表 | **MET** | `weights-licenses.json`（10 文件字节/sha256/许可结论；yolo11s-seg ONNX metadata_props = author Ultralytics + license AGPL-3.0；GNU/Ultralytics 一手来源 URL+抓取时间+sha256） |
| AC2 声明修正 | **MET** | `NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md` 按变体修正（models=AGPL-3.0，base=GPL-3.0-or-later）；包内副本见 `package-check.json` |
| AC3 AGPL 全文随包 | **MET** | 根 `LICENSE-AGPL-3.0.txt`（34,523 B，sha256 `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`）；`package.ps1` 4 许可文件复制+逐字节校验，base/models 均随包 |
| AC4 重打包验证 | **MET** | base zip `103,492,048 B` sha256 `722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef`；models zip `725,499,708 B` sha256 `480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67`；包内 5 许可文件在 zip 流+staging 双验逐字节一致；VERSION.json 记录 license；大小与 REPACK-5 相当（各 +0.11MB/+1 file） |
| AC5 回归与门禁 | **MET** | `extract-command-surface --check` PASS（66）；`test.ps1` 隔离复跑 258/258（61/60/137，0 skipped）；`check.ps1 -TaskPath` PASS；15 项 64-hex pin |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | 只读扫描 REPACK-5 models 包 + onnx metadata_props + 抓取 GNU/Ultralytics 许可来源 | Win11 / onnx 1.23.2（build venv） | **PASS** | `weights-licenses.json` |
| AC4 | `package.ps1` base 与 `-WithModels` 各一次（sidecar=REPACK-5 out 只读） | dotnet publish + robocopy + Compress-Archive | **PASS**（两包 exit 0） | `package-check.json`、`packages/*`、`logs/package-*.log`、`logs/publish-*.log` |
| AC5 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | 仓库 | **PASS：66** | `logs/extract-command-surface.log` |
| AC5 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | Win11 + frozen sidecar | **PASS 258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137） | `test/summary.json`、`logs/test-ps1-console.log` |
| AC5 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/AGPL-RELEASE-1.md` | rebase main 后 | **PASS** | `check-governance.json`（原始日志 task-env `logs/check-governance.log`） |

## 接收方式

```powershell
git -C "G:\CODEX\New Manga.workspace\worktrees\AGPL-RELEASE-1" status
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/AGPL-RELEASE-1.md
# 复核重打包产物（只读；输出目录为 task-env）
Get-FileHash "G:\CODEX\New Manga.workspace\task-envs\AGPL-RELEASE-1\out\NewManga-0.1.0-win-x64.zip" -Algorithm SHA256
Get-FileHash "G:\CODEX\New Manga.workspace\task-envs\AGPL-RELEASE-1\out\NewManga-0.1.0-win-x64-models.zip" -Algorithm SHA256
```

## 下一任务建议（必填）

无需下一步操作（AGPL 声明的发行侧「对应源码」链接与 RT-DETR/MangaOCR 一手许可补全属发布流程/下一次发行 Gate，非本 Task 范围；需 DSH 另行释放）。

## 风险与遗留

1. RT-DETR / MangaOCR 许可仍 [待核实]（无内嵌许可元数据；AC1 明确不阻断本卡，THIRD_PARTY §3 保留标记）。
2. 发行页需提供 models 包对应源码获取方式（AGPL 义务），属发布流程。
3. `check-governance.json` 是 `check.ps1 -TaskPath` PASS 的静态捕获（原始 tee 日志在 task-env），已在 Canonical Evidence 中 pin。
4. 本卡不改 STATUS/PLAN/LEDGER（DSH 统一更新）。
