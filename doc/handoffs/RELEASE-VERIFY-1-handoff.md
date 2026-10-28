---
task_id: RELEASE-VERIFY-1
author: region-workbench-owner
recipient: DeepSeek Harness
base_commit: b54d2d36f56ac60cf9d1e7b01db27b67f66df566
delivery_head: 75db4fd643f47a92924f607617c348fd85e6d411
status: in_review
---

# Handoff：RELEASE-VERIFY-1（免证书发布完整性：SHA-256 清单/校验脚本 + 发行说明）

## 交付结果

- Task：`doc/tasks/RELEASE-VERIFY-1.md`（shared task-4）；Owner `region-workbench-owner` / Reviewer `dsh`。
- Branch / Worktree：`task/RELEASE-VERIFY-1` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-VERIFY-1`。
- 基线：worktree 起点 `28991823a`（Task 卡登记 base `b54d2d36f`）。
- 实现提交：`8d149ca6d749d9fb8ebe67812713603977a648c2`（`packaging/release/**` + `RELEASE_NOTES_0.1.0.md` + `MANUAL_VERIFY.md` 链接）。
- 证据提交 / **delivery head**：`75db4fd643f47a92924f607617c348fd85e6d411`（`verification/RELEASE-VERIFY-1/**`）。
- 本 Handoff 与 Task 卡为紧随 delivery head 的文档提交（rebase main 后；不改代码/证据内容）。
- 未 push；三个发布产物只读未改；zip/exe 未入 Git；不做签名、不关闭 V1-RELEASE-SIGNING-1。

| AC | 结论 | 证据（`verification/RELEASE-VERIFY-1/`） |
|---|---|---|
| AC1 校验清单与脚本 | **MET** | `packaging/release/generate-checksums.ps1`（显式/-ArtifactDir/默认三级定位，只读哈希）+ `verify-release.ps1`（逐项校验、缺失/不匹配 exit 1、`-Quiet`）；真实产物生成/校验 PASS | `logs/generate-checksums.log`、`logs/verify-positive.log`、`logs/verify-artifactdir.log`、`artifacts.json` |
| AC2 清单入库与可复算 | **MET** | `packaging/release/SHA256SUMS`（284 B，3 产物，`sha256sum` 兼容）+ sidecar JSON（字节/来源/时间）；正向校验 PASS 3/3 | `checksums/SHA256SUMS`、`checksums/SHA256SUMS.json` |
| AC3 负向验证 | **MET** | setup.exe task-env 副本翻转 offset 34,305,604 一字节（`ebad8662…`→`bb84e283…`）→ `verify-release.ps1 -SetupExe <tampered>` **FAIL exit 1 且点名该文件**；真实产物复验 PASS；缺失产物场景 3 MISSING/exit 1 | `logs/verify-negative-tamper.log`、`negative/tamper.json`、`logs/verify-missing.log`、`logs/verify-quiet-after-negative.log` |
| AC4 发行说明 | **MET** | `RELEASE_NOTES_0.1.0.md`：变体/许可、NSIS 与 zip 两种安装、**未签名 + SmartScreen「更多信息→仍要运行」**、SHA-256 校验、数据根/卸载、已知限制、SignPath 等免费 OSS 签名替代；`MANUAL_VERIFY.md` 增补链接 | `docs/release-notes-check.json`、`docs/manual-verify-link.json`、`docs/diff-stat.txt` |
| AC5 门禁 | **MET** | `extract-command-surface --check` PASS（66）；`test.ps1` 隔离复跑 **258/258 passed, 0 skipped**（2026-10-28）；`check.ps1 -TaskPath` PASS；全部证据 64-hex pin | `logs/extract-command-surface.log`、`test/summary.json`、`logs/test-ps1-console.log`、`check-governance.json` |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2 | `generate-checksums.ps1` + `verify-release.ps1`（默认定位）；`-ArtifactDir`（硬链接 staging） | Win11 / 三真实产物（897,602,964 B） | **PASS**：生成 exit 0；校验 PASS 3/3（两种定位模式） | `logs/verify-positive.log`、`logs/verify-artifactdir.log` |
| AC3 | 复制 setup.exe → 单字节篡改（offset 34,305,604）→ `verify-release.ps1 -SetupExe <tampered>` | task-env 副本 | **PASS（负向）**：`FAIL (1/3)`、exit 1、点名 `NewManga-0.1.0-setup.exe`；真实产物再验 PASS | `logs/verify-negative-tamper.log`、`negative/tamper.json` |
| AC4 | 文档撰写 + 关键词/链接自动检查 | 仓库 | **PASS**：required_keywords 全命中；MANUAL_VERIFY 链接 target 存在 | `docs/release-notes-check.json`、`docs/manual-verify-link.json` |
| AC5 | `extract-command-surface.py --check` / `test.ps1` / `check.ps1 -TaskPath` | 仓库 + 隔离 evidence dir | **PASS**：66 命令零漂移；258/258；check PASS | `logs/extract-command-surface.log`、`test/summary.json`、`check-governance.json` |

## 接收方式

```powershell
git -C "G:\CODEX\New Manga.workspace\worktrees\RELEASE-VERIFY-1" status
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RELEASE-VERIFY-1.md
# 复算/复核发布完整性（产物只读，可加 -ArtifactDir 指向发布目录）
pwsh -NoProfile -File packaging/release/verify-release.ps1
pwsh -NoProfile -File packaging/release/verify-release.ps1 -Quiet
```

## 下一任务建议

无需下一步操作（发布完整性已可用：清单+校验脚本+发行说明；签名仍由 V1-RELEASE-SIGNING-1 等待证书，不阻塞发布；证书到位后补签即可删除 SmartScreen 提示）。

## 风险与遗留

1. `SHA256SUMS` 与产物必须**一起分发**（清单入库、产物在发布页/task-env）；校验脚本跨机器请用 `-ArtifactDir` 或显式路径。
2. 哈希校验只证完整性，清单真实性依赖官方发行页；未签名状态未改变（SmartScreen 提示仍在，发行说明 §5 指引）。
3. `SHA256SUMS.json` 的 `source_path` 含本机构建路径（sidecar 不参与 `sha256sum` 校验，仅内部审计）。
4. 本卡未改 STATUS/PLAN/LEDGER（DSH 统一更新）；V1-RELEASE-SIGNING-1 保持 in_review。
