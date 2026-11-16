# MAINT-1 Gate 条件 6 收口证据索引

- Task：`doc/tasks/MAINT-1-RELEASE-MONITOR.md`（`in_progress`，伞形维护哨位）
- Gate 判据：`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:30`
- 复评报告：`doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md`
- 冻结交付 head：`45af570079eeaa57bb731e766caa82a480e7d0cd`
- 证据生成时点：2026-11-16T07:35:11Z
- 解释器：PowerShell 7.6.8 / Python 3.14.6 / dotnet 10.0.401 / git 2.52.0.windows.1 / Windows 10.0.26200

## 1. 四件套实测（同一 head、工作区 clean）

| # | 命令 | EXIT | 原始输出 |
|---:|---|---:|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | `gates.log` §1（PASS，3 warnings） |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAINT-1-RELEASE-MONITOR.md` | 0 | `gates.log` §2（PASS，3 warnings） |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | `gates.log` §3（PIN AUDIT: PASS，all 18） |
| 4 | `python -B tools/generate_api_inventory.py --check` | 0 | `gates.log` §4（`1/80/6 = 87`） |
| 5 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1` | 0 | `gates.log` §5（1591/1639 passed，48 skipped；App 969/0/4） |

复现：在交付 head 的干净工作区依次执行上表命令，比对 `gates.log` 的 `EXIT=` 行与判定行。

## 2. §3.2-③ / P2-2 前后实测

`p2-2-before-after.log` —— BEFORE（把 PLAN 换回 `6a408e5aa` 的 6990 B blob）5/6 张卡 `-TaskPath` FAIL；
AFTER（本 head 的 6960 B PLAN）0/13 FAIL；PLAN 字节复原经 sha256 校验。

## 3. 资源核销

`resource-closeout.log` —— P2 UI 冒烟遗留的 8 个 `%TEMP%/newmanga-p2-*` 隔离数据根（1,523,132 B）按
`DELETE_SAFE` 删除，删除后复查 0 残留。本卡无独立 worktree；sidecar 夹具按 `PRESERVE_REFERENCED` 保留。

## 4. 已知副作用（诚实登记）

`apps/desktop-avalonia/tests/NewManga.App.Tests/ImmersiveReaderVisualEvidenceTests.cs` 会在每次全量测试时
重写 `verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`（把「渲染 HEAD」改成当前 head，并丢弃该文件
末尾的「全量测试回归确认」段）。这是既有测试副作用，**不是本卡引入**。本次已在提交前用
`git checkout 6a408e5aa -- verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md` 恢复基线字节，
并要求后续跑全量测试的轮次同样恢复（已写入 `NEXT-SESSION-STARTER` 的注意事项）。

## 5. 三口径复算

`threeway.log` —— 对本卡 `## Canonical Evidence` 表逐行取 `path/commit/sha256`，重算 Git blob SHA-256 并
`git cat-file -e` 断言该 commit 树含该路径；三口径任一不符即 FAIL。
