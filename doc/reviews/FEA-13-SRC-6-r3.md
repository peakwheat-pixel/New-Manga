---
task_id: FEA-13-SRC-6
reviewer: DSH 派发的独立上下文子代理（fresh；未参与 FEA-13-SRC-6 实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 1a8bb1235
reviewed_head: ef0618e57
previous_review: doc/reviews/FEA-13-SRC-6-r2.md
decision: changes_requested
---

# FEA-13-SRC-6 r3 复审（只读）

- **被审 head**：`ef0618e575be05d7a923d4bb0cf0c6959aa51152`（`main`，02:10:36 +0800）
- **base**：`1a8bb1235`；前序 r2（`cc042df4b`，changes_requested：P0 N-001 / P1 N-002 / P2 N-003 / P3 N-004）
- **审查性质**：只读定向复核（N-001…N-004 + 证据/门禁/范围），仅写本文件；未改源码/测试/契约/卡，未 commit / push。写本文件前 `git status --short` 为空。
- **环境**：Windows / pwsh 7.6.8 / Python 3.14 / .NET 9。
- **结论**：**`changes_requested`**（**P0=0、P1=0、P2=0**；仅剩 **P3 证据/文档一致性**，代码与测试无需再改）；**CLEARED FOR DONE：否**。

## 一句话结论

r2 的四项发现中，**N-001（P0）、N-002（P1）、N-003（P2）已在 `ef0618e57` 真正修好**——定向 pytest 已回绿、启动补导入有 read-only 守卫、同代次不同 roots 判 `Conflicts`；证据日志也已随本 head 重生成（7 / 9 / 321 / PASS / 18/18，EXIT 全 0）。但 **N-004（P3）只处置了一半**：`verification/FEA-13-SRC-6/README.md:17` 仍写「≥3 变异 **RED** | PASS」，与同文件 `:34`/`:38` 的「MA 无效（NOT RED）」直接矛盾；门禁表 `:25`/`:26` 仍写 `7 passed` / `319`，而同目录本 head 日志是 **9** / **321**；卡面 AC5 仍写「截断 → `registry_corrupt`」`<<MET>>`，而唯一截断测试只断言 `handoff_corrupt`。这三处是 AC6（证据门禁 AC）自身的索引失真，属机械修正，但不应带进 done。

## 核验项逐条（本 head 实测）

| # | 项 | 结论 | 依据 |
|---|---|---|---|
| 1 | **N-001（P0）** 测试引用已删 wire 字段 | **FIXED** | `tests/storage/test_nmbak_source_access.py:187,197` 已改为 `assert "source_access_handoff" not in report`；`src/` 仅剩 `nmbak.py:436/441` 的内部调用，无 `report[...]` 写入。实跑 `python -m pytest tests/storage/test_nmbak_source_access.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py -q` → **36 passed，EXIT 0** |
| 2 | **N-002（P1）** read-only 守卫 | **FIXED** | `HostRuntime.cs:443-446`：`ImportPendingSourceAccessHandoffs()` 首句 `if (!Policy.WritesAllowed) return Array.Empty<SourceAccessRestoreOutcome>();`，早于 `Registry`/`DataRoot` 访问，`TryImportPending→ImportRestoredSnapshot→Save` 不可达 → read-only 零写成立。**残留（非阻断）**：该分支不记日志、不写 receipt（handoff 仍留在磁盘，下次可写启动会导入），且本 head 未补 read-only 零写测试（r2 R-012 残留） |
| 3 | **N-003（P2）** 同 generation 不同 roots | **FIXED** | `SourceAccessRegistry.cs:270-274`：`sameShape = Generation 相等 && Roots.Select(Root).SequenceEqual(...)`；仅完全相同 → `unchanged++`，否则 `conflicts++`；旧代次仍 `conflicts++`（`:265-275`）。**残留（非阻断）**：未补「同代次不同 roots」回归测试；比较仅取 `Root` 字符串且按顺序，未含 `Readable`/顺序无关归一（只会更保守地判冲突，无写入风险） |
| 4 | **N-004（P3）** README 措辞与判别力声明 | **PARTIAL** | 已修：`README.md:16` AC5 行改为「Host 边界 `handoff_corrupt`（registry 级为 `registry_corrupt`）」；`:38` 增加判别力声明「MA 不可判别，不等于判别力成立」。未修：`:17` AC6 行仍「≥3 变异 **RED** \| PASS」（实为 2 RED + 1 无效）；`:25`「Host 导入测试 7 passed」≠ 本 head 日志 9；`:26`「319 / 0 / 74」≠ 本 head 日志 321 / 0 / 74 / 395；卡面 `doc/tasks/FEA-13-SRC-6.md:89` 仍「截断 → `registry_corrupt`」`<<MET>>`，而 `TamperedOrTruncatedSegmentIsRejected` 只断言 `handoff_corrupt`（`registry_corrupt` 至今无测试） |
| 5 | 证据日志对应本 head | **PASS（附注）** | 5 份日志统计与 EXIT 全对：`pytest-src6.log` **7 passed / EXIT 0**（02:10:08）、`dotnet-restore-tests.log` **9 passed / EXIT 0**（02:10:16）、`dotnet-host-tests.log` **321 passed / 0 failed / 74 skipped / 395 total / EXIT 0**（02:10:27）、`gates-check.log` **PASS / EXIT 0**、`gates-pins.log` **18/18 PASS / EXIT 0**（02:10:29）；均早于提交 02:10:36，属本 head 产物。**附注**：README 门禁表数字未同步（见 #4）；`mutations/` 三条日志时间 01:51–02:04（早于 r2 修复提交），其变异目标与本次 diff 无交集，不改变结论，但严格意义上未随 head 重跑 |
| 6 | 门禁 | **PASS** | `check.ps1` 默认 **EXIT 0**（PASS，3 warnings：STATUS/PLAN 预算、11 非终态 Task）；`check.ps1 -TaskPath doc/tasks/FEA-13-SRC-6.md` **EXIT 0**（PASS，选中本卡）；`verify_pins.ps1` **18/18 PASS，EXIT 0**；`git status --short` 写本文件前为空 |
| 7 | 范围/契约/pins | **PASS** | `git diff --name-only 1a8bb1235..ef0618e57` = 31 文件，全部落在 14 条 `allowed_paths`（4 生产/测试 + 卡 + 2 review（glob）+ 1 Core 测试 + 1 `nmbak.py` + 22 `verification/FEA-13-SRC-6/**`）；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 为 scope §2.6 明示的生命周期指针豁免（3 文件，仅指针行）。`git diff 1a8bb1235..ef0618e57 -- doc/contracts doc/plan` **为空**；C-06/C-09/C-17 零字节；18 pins 零变化（verify_pins 18/18） |

## 门禁实测（本 head，2026-11-10，独立重跑）

| # | 命令 | 结果 |
|---|---|---|
| G1 | `python -m pytest tests/storage/test_nmbak_source_access.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py -q` | **PASS**：36 passed，**EXIT 0**（本人重跑，3.19s） |
| G2 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --filter "FullyQualifiedName~SourceAccessRestoreTests"` | **PASS**：9 passed / 0 failed，**EXIT 0**（本人重跑，249ms；编译含本 head 的 registry 改动） |
| G3 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，**EXIT 0** |
| G4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SRC-6.md` | **PASS**，**EXIT 0** |
| G5 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (18/18)**，**EXIT 0** |
| G6 | `git status --short` | 写本文件前**空** |

## 处置建议（P3，机械修正，不改代码/测试）

1. `verification/FEA-13-SRC-6/README.md:17`：AC6 行改为「2 判别 RED + 1 无效（MA 已登记）」并把 `≥3 变异 RED` 删去/改写；
2. 同文件 `:25` 改 `7 passed` → `9 passed`；`:26` 改 `319 / 0 / 74` → `321 / 0 / 74 / 395`；
3. 卡面 `doc/tasks/FEA-13-SRC-6.md:89` 的 AC5 截断判据补「Host 边界 `handoff_corrupt`；`registry_corrupt` 未测」，与 README `:16` 对齐（或明确 `registry_corrupt` 未达）。

以上 3 处仅文档字节，**不影响本 r3 已实测的代码/测试事实**；改完即可 done，无需新一轮独立 Review（如需确认，只需核对 README/卡面 3 行）。r1/r2 其余 OPEN/PARTIAL 项（R-007/R-008/R-009/R-010/R-011/R-013–R-017/R-019/R-020 等）不在本次 r3 核验范围，维持前序状态。

## 最终

- **verdict**：`changes_requested`（**P0=0 / P1=0 / P2=0**；仅 **P3 = 1 项**：N-004 剩余 + 证据索引数字滞后）
- **CLEARED FOR DONE**：**否**（差 3 处文档机械修正；代码/测试/门禁/范围均已达标）
- **报告**：`doc/reviews/FEA-13-SRC-6-r3.md`
