---
task_id: NSIS-INSTALLER-1
author: region-workbench-owner
recipient: DeepSeek Harness
base_commit: 7401a53039c46f0c0ff7d2799fb725c57cdae1f3
delivery_head: d657b52b347a4bb8fa3a43b2788939a815545175
status: in_review
---

# Handoff：NSIS-INSTALLER-1（per-user 无签名 NSIS 安装包 + 真机安装/卸载验证）

## 交付结果

- Task：`doc/tasks/NSIS-INSTALLER-1.md`（shared task-3）；Owner `region-workbench-owner` / Reviewer `dsh`。
- Branch / Worktree：`task/NSIS-INSTALLER-1` / `G:/CODEX/New Manga.workspace/worktrees/NSIS-INSTALLER-1`。
- 基线：worktree 起点 `3fcb7429b`（Task 卡登记 base `7401a5303`）。
- 实现提交：`acf1a5fab8500abc69482016e4649ce25f955dce`（`packaging/nsis/` + `build-installer.ps1` + 安装说明）。
- 证据提交 / **delivery head**：`d657b52b347a4bb8fa3a43b2788939a815545175`（`verification/NSIS-INSTALLER-1/**`）。
- 本 Handoff 与 Task 卡为紧随 delivery head 的文档提交（rebase main 后；不改代码/证据内容）。
- 未 push；未改产品源码/Core/旧壳/冻结契约；未写 HKLM/Program Files；installer exe 不入 Git（只写 task-env 并登记字节/sha256）。

| AC | 结论 | 证据（`verification/NSIS-INSTALLER-1/`） |
|---|---|---|
| AC1 安装器实现 | **MET** | `packaging/nsis/installer.nsi`（Unicode true / RequestExecutionLevel user / SimpChinese+English / SOLID lzma / 许可页 / 开始菜单 / HKCU 卸载项 / `/S`）+ `apps/desktop-avalonia/scripts/build-installer.ps1`；产物 68,611,208 B sha256 `ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691`（NotSigned） | `packages/build-info.json`、`logs/build-installer.log` |
| AC2 数据保护 | **MET** | 安装/卸载只动安装目录/快捷方式/HKCU；真实数据根 durable 摘要全程 `fdf52d87…b530`（与 DSH 独立 before 快照一致），`library.db` sha256 不变，HKLM/Program Files 全程不存在 | `data-root.json`、`registry.json`、`verify.json` |
| AC3 真机验证 | **MET** | 安装 6.81s（1,970 文件，app 树与 stage 逐字节一致）→ Host 就绪 2.48s + 窗口截图/UIA「Host 就绪」→ 卸载 0.73s（目录/快捷方式/HKCU 清零）→ 重装 6.57s（幂等）→ 最终卸载 0.72s；54 断言 0 失败 | `install-phase.json`、`uninstall-phase.json`、`verify.json`、`app-uia.txt`、`app-window.json`、`screens/installed-app.png` |
| AC4 门禁 | **MET** | `extract-command-surface --check` PASS（66）；`test.ps1` 隔离复跑 **258/258 passed, 0 skipped**（61/60/137，2026-10-28）；`check.ps1 -TaskPath` PASS；全部证据 64-hex pin | `logs/extract-command-surface.log`、`test/summary.json`、`logs/test-ps1-console.log`、`check-governance.json` |
| AC5 已知限制 | **MET** | 未签名（SmartScreen 提示；签名由 V1-RELEASE-SIGNING-1）、仅 base 变体、per-user（无需管理员）、覆盖式升级、无自动更新；见 REPORT §5 | `REPORT.md` |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 -StageDir <AGPL base stage> -MakensisPath <NSIS 3.13> -OutDir <task-env>/out` | Win11 + NSIS v3.13 | **PASS**（安装包 65.43 MB，构建 55.23 s，Authenticode=NotSigned） | `packages/build-info.json` |
| AC3 | `verify-installer.ps1 -Phase install` → UIA/截图 → `-Phase finish` → `compose-verify.ps1` | 隔离数据根 `--data-root`；真实数据根只读 | **PASS**：安装 6.81s / 卸载 0.73s / 重装 6.57s / 最终卸载 0.72s；Host 就绪 2.48s；54/54 断言 | `verify.json`、`install-phase.json`、`uninstall-phase.json` |
| AC4 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | 仓库 | **PASS：66** | `logs/extract-command-surface.log` |
| AC4 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | Win11 + frozen sidecar | **PASS 258/258 passed, 0 skipped** | `test/summary.json`、`logs/test-ps1-console.log` |
| AC4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NSIS-INSTALLER-1.md` | rebase main 后 | **PASS** | `check-governance.json`（原始日志 task-env `logs/check-governance.log`） |

## 接收方式

```powershell
git -C "G:\CODEX\New Manga.workspace\worktrees\NSIS-INSTALLER-1" status
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NSIS-INSTALLER-1.md
# 复核安装包（只读；产物在 task-env，不入 Git）
Get-FileHash "G:\CODEX\New Manga.workspace\task-envs\NSIS-INSTALLER-1\out\NewManga-0.1.0-setup.exe" -Algorithm SHA256
# 复核真机证据
Get-Content "G:\CODEX\New Manga.workspace\task-envs\LEAD-NSIS-REVIEW-1\data-root-before.json" -Raw
```

## 下一任务建议

无需下一步操作（签名由 V1-RELEASE-SIGNING-1 在证书到位后处理；models 变体安装包与 MSIX 不在本卡范围，需 DSH 另行释放）。

## 风险与遗留

1. **未签名**：SmartScreen 会提示未知发布者；属 AC5 已知限制，签名归 V1-RELEASE-SIGNING-1。
2. **仅 base 变体**：models（725MB）仍走 zip；如未来要 models 安装包，需另评体积/许可（AGPL-3.0 声明已由 AGPL-RELEASE-1 落地）。
3. **验证迭代**：首次真机验证因 `Start-Process` 未给含空格路径加引号导致应用回落默认数据根（仅追加 `logs/window-material.log` 一行，durable 内容不变），修复后重跑 54/54；见 REPORT §3 与 `data-root.json` 的 changes。
4. **数据根行为**：应用自身启动会向 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 追加诊断行（产品行为，非安装器）；durable 摘要（排除 `logs/`）不变。
5. 本卡未改 STATUS/PLAN/LEDGER（DSH 统一更新）。
