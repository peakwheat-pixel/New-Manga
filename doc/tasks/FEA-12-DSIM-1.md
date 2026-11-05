---
id: FEA-12-DSIM-1
title: FEA-12 D 流程模拟切片（可注入原文件回收适配器 + SimulatedRecycleBin，无真实 OS API）
kind: implementation
governance_version: 3
status: done

approval: 用户 2026-11-05 口径（隔离 fixture + 模拟回收站路径，不触碰真实回收站）；ADJ-2026-11-05-FEA-12-SCOPE D5；DSH 2026-11-05 释放；r1 approved（P0/P1=0，P2=2）→ r2 返修 → **r2 Review approved（P0/P1/P2=0，P3=3 非阻断）→ DSH 集成 closeout**
suggested_owner: dsh（dsh-agent-team teammate）
owner: dsh-agent-team teammate `fea12-dsim-impl`
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-12-DSIM-1-r1.md` session `fc7ffec8-b24b-418a-82f7-dcc99cb2a7dc`；r2 `doc/reviews/FEA-12-DSIM-1-r2.md` session `a39295f9-012b-401d-b35e-864c4c481d00`）
depends_on: []
base_commit: 37f84bb895c9ef9b64e3865f3a92b245f2e28a7c   # 释放时由 Lead 固定
branch: main
worktree: G:\CODEX\New Manga（main 主工作树；未新建分支/worktree）
integration_commit: beee351bb
delivery_head: beee351bb
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-12-DSIM-1
allowed_paths:
  - doc/tasks/FEA-12-DSIM-1.md
  - doc/reviews/FEA-12-DSIM-1-*.md
  - doc/handoffs/FEA-12-DSIM-1-*.md
  - src/application/maintenance/recycle_gateway.py（新增）
  - src/application/maintenance/__init__.py
  - src/infrastructure/filesystem/simulated_recycle_bin.py（新增）
  - tests/fea12/test_recycle_gateway_sim.py（新增）
  - tests/fea12/**
  - verification/FEA-12-DSIM-1/**
out_of_scope:
  - 任何真实 Windows 回收站 API（SHFileOperation/IFileOperation/Shell32/Microsoft.VisualBasic.FileIO/Windows.Storage 等）
  - 真实回收站路径、真实用户数据/AppData/外部卷
  - Host/UI 生产接线；不接 IHostController/C-07 冻结面
  - 真实 D 流程完成声明（本卡只交付模拟切片；真实 OS 验证 NOT_RUN）
  - 18 pinned 冻结契约字节；新 schema/migration/依赖；push
---

# FEA-12-DSIM-1：D 流程模拟切片

## 来源与目标

- 来源：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md` §2.1/§D5；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` §3 D 行；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` §3.7；`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` SC-B05；`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md` SC-31/SC-34；用户 2026-11-05"模拟回收站路径"口径。
- 目标：为 D 流程建立**可测试的接口与模拟实现**，证明"失败保留原文件、不降级为永久删除、不误删真实对象"的语义，而**不实现**任何真实 Windows 回收站调用。生产默认实现必须 typed 不可用。
- 边界：本卡完成 ≠ D 流程完成；真实 OS 行为 NOT_RUN，需用户另行专门授权。

## Scope（冻结）

1. `src/application/maintenance/recycle_gateway.py`：application 层协议 `OriginalFileRecycleGateway`，方法形状建议 `move_to_recyclebin(entries, *, journal) -> RecycleOutcome`；结果逐项 `moved`/`failed`（typed reason）/`not_started`；语义：**失败必须保留原文件**、绝不转永久删除、逐项原子。
2. 生产默认实现：`UnavailableOriginalFileRecycleGateway`（或等价）→ 任何调用返回 typed `not_supported/unavailable`，**零文件操作**。
3. `src/infrastructure/filesystem/simulated_recycle_bin.py`：`SimulatedRecycleBin`：只在隔离根内写 manifest/状态（`recyclebin-manifest.json` 或内存记录），不调用任何 OS API；测试用。
4. 测试 `tests/fea12/test_recycle_gateway_sim.py`：①成功模拟：条目进 manifest、原路径按模拟语义处理（移入隔离根的 simulated bin 子目录，只用 `tmp_path`）；②失败注入：原文件字节与集合不变、结果 `failed`、零永久删除/零 DB 删除；③生产默认实现调用 → typed 不可用且零副作用；④静态 grep：`src/**`/`apps/**` 零 Windows 回收站 API；⑤运行时哨兵：隔离根外真实路径零变化（哨兵文件/目录不变）。
5. 文档：Task 卡内记录"模拟实现 ≠ D 完成；真实 OS 验证 NOT_RUN"。

## Acceptance Criteria

- [x] **AC1 协议与生产默认实现**：`OriginalFileRecycleGateway` 协议 + typed 结果；生产默认实现 fail-closed、零文件操作；无 Host/UI 接线。 <<MET>>
- [x] **AC2 模拟实现（r2 收窄表述；P3 措辞修正）**：`SimulatedRecycleBin` 全部操作限制在**调用者提供的干净隔离根**内；自身写目标（bin/manifest/journal）构造期与每次读写前拒绝 junction/symlink/hardlink（typed 安全错误，**根外零写入**；拒绝前可能已在根内写 1 条 journal attempt——r2 Review P3① 实证，不涉及根外）；manifest 可审计；不调用任何 Windows API。**不再声称"任何情况下全部写入都在隔离根内"**：校验与写入之间的并发重植窗口（TOCTOU）未消除，属单写者测试替身残余风险。 <<MET>>
- [x] **AC3 失败语义**：失败注入下原文件字节/集合不变、结果逐项 typed、零永久删除/零 DB 删除；"D 失败不得降级 C"有测试。 <<MET>>
- [x] **AC4 隔离与禁令**：静态扫描 0 处 Windows 回收站 API；运行时哨兵证明隔离根外零变化；测试无 `%APPDATA%`/真实盘符/真实回收站路径。 <<MET>>
- [x] **AC5 交付件与门禁（基线口径 r2 Review 澄清）**：Task/Handoff/`verification/FEA-12-DSIM-1/`（隔离与扫描日志）；`check.ps1` PASS、`verify_pins.ps1` 18/18；**全量 pytest 基线**：r1 交付时点 3093/10、r2 复跑 **3101/10**（+8 r2 测试）；**全量 .NET**：稳定树 **1403/0/79**（r1 交付），r2 尝试 1 failed/670/7 已按实测 diff 归因（并发 verification 写入窗口）；.NET 对 DSIM 业务代码零差异。 <<MET>>

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）。本卡只新增文件，不改既有生产文件（`__init__.py` 仅 additive 导出除外）。

## 禁止范围

见 `out_of_scope`。另：不得把模拟实现描述为真实回收站验证；不得写真实盘符路径；不得 push；不得删测试/放宽断言。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings --tb=no`；`pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1`；`C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py` | 隔离 `tmp_path`（含真实 junction/hardlink fixture）+ `tempfile.TemporaryDirectory()`；Python 3.14.6 | **PASS**：fea12 **21 passed**（r1 13 + r2 新增 8，EXIT 0）；静态扫描 766 files / **0** Windows 回收站 API、2 test files / **0** 真实路径字面量、2 modules **1020 lines** / **0** 删除/DB 回退（EXIT 0）；运行时哨兵 `PASS: runtime sentinel outside the isolated root unchanged`（EXIT 0） | `verification/FEA-12-DSIM-1/logs/pytest-fea12.log`、`logs/static-scan.log`、`logs/sentinel-probe.log`、`ISOLATION-EVIDENCE.md`、`AC-MATRIX.md` |
| AC5 | 全量 pytest（基线 + r2 head）；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-DSIM-1.md` | 仓库根；共享工作树（含并发 CORE 未提交改动，见 ENVIRONMENT） | **PASS（含已归因 flaky）**：基线（r1 交付 head）`3093 / 10 skipped` → **r2 head `3101 passed / 10 skipped`**（EXIT 0；+8 = 本卡 r2 新测试）；全量 .NET r2 尝试 **1 failed / 670 passed / 7 skipped（App.Tests）**（已知 `FluentResidual2VisualEvidenceTests` verification git-status 断言窗口，日志 `dotnet-r2-1.log`），**r2 无 .NET 改动 → 引用 r1 稳定树绿跑 失败 0 / 通过 1403 / 跳过 79**（`dotnet-full-3.log`）；pins **18/18 PASS**；`check.ps1` PASS **3 warnings、无 evidence_dir 告警**（warnings 均为预存/Lead-owned：13 非终态 Task、STATUS 80% 预算、PLAN 80% 预算；`gates.log`/`check-final.log` 已迁 agent-output 并在 `agent-output-manifest.json` 登记，EXIT 0） | `logs/baseline-pytest.log`、`logs/pytest-full.log`、`logs/dotnet-r2-1.log`、`logs/dotnet-full-3.log`、`logs/verify-pins.log`、`agent-output-manifest.json`、`G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\gates.log`（仓外） |

## 依赖、风险与阻塞

- 依赖：无 Task 硬依赖（纯新增文件；与 CORE 写域不相交，可并行；若 CORE 需用该协议由 Lead 裁决改为 CORE 依赖）。
- 风险：①用户可能把"模拟回收站路径"理解为 D 真实实现 → 本卡明确 OUT 并交用户裁决；②未来真实 D 实现需重做 OS 适配器（本卡只保证接口稳定）；③不得被 UI/Release 误引用为"D 已实现"。
- 阻塞解除标准：本卡 Review approved + 集成；真实 D 需新授权。

## 交付与运行记录

- Handoff（r2）：[FEA-12-DSIM-1-d5925957b](../handoffs/FEA-12-DSIM-1-d5925957b.md)（实现 commits `94a12e93f` + `3d0d325f7` + `d5925957b`；交付 docs commit 其后相邻提交）。
- Review：r1 独立 Review `approved`（P0=0/P1=0/P2=2/P3=7，`doc/reviews/FEA-12-DSIM-1-r1.md`）；r2 处置后待 Lead 派 fresh subagent 复审（实现者 `fea12-dsim-impl` 未自审）。
- 实际测试：见「测试要求」表与仓外 `gates.log`；关键数字：pytest fea12 **21 passed**；全量 pytest **3101 passed / 10 skipped**（r1 基线 3093/10，+8）；全量 .NET r2 尝试 flaky 已归因、引用 r1 稳定树 **0 failed / 1403 passed / 79 skipped**；pins **18/18**；静态扫描 766 files / 0 Windows 回收站 API；运行时哨兵 PASS；`check.ps1` PASS（3 warnings、无 evidence_dir 告警）。
- **边界声明（不得误读）**：本卡只交付 **D 流程模拟切片**——application 端口 + 生产 typed 不可用默认实现 + `SimulatedRecycleBin` 测试替身 + 隔离/哨兵测试。**真实 Windows 回收站行为未实现、未验证（`NOT_RUN`）**，需用户另行专门授权；不得据此声称 D 流程完成；无 Host/UI 生产接线、无 DB/schema/依赖改动、无 push。
- r2 处置（Review r1）：R-001 已修复（自身写目标 realpath containment + junction/symlink/hardlink 拒绝，构造期 + 每次读写前，typed `RecycleSafetyError` 零写入；8 项新判别测试）；R-002 已修复（过程日志迁 agent-output + `agent-output-manifest.json` 登记，check 无 evidence_dir 告警）；R-003…R-009 逐项处置见 `AC-MATRIX.md`「r2 处置」表。
- 并发工作树：r2 期间共享工作树含 FEA-12-CORE 分片 A/B 未提交改动；本卡只改自己的 6 类路径（见 ENVIRONMENT per-commit scope）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | src/application/maintenance/recycle_gateway.py | d5925957b | - | CANONICAL |
| EV-02 | AC2 | src/infrastructure/filesystem/simulated_recycle_bin.py | d5925957b | - | CANONICAL |
| EV-03 | AC1/AC2/AC3/AC4 | tests/fea12/test_recycle_gateway_sim.py | d5925957b | - | CANONICAL |
| EV-04 | AC1 | src/application/maintenance/__init__.py | d5925957b | - | CANONICAL |
| EV-05 | AC1–AC4 | verification/FEA-12-DSIM-1/logs/pytest-fea12.log | - | b4e14d28da5cf97520e57be54d2a761e94f18cd9e6f5fd3f0a1cf7715120a603 | CANONICAL |
| EV-06 | AC5 | verification/FEA-12-DSIM-1/logs/pytest-full.log | - | 64667fbd2cc058b5f2d14440b27c363f2287cb742a031d652f7b0e189bba2430 | CANONICAL |
| EV-07 | AC5（基线） | verification/FEA-12-DSIM-1/logs/baseline-pytest.log | - | e49df1798ce269e630fbfd2249f2a6dfa3eb866fa2051ef8d4722583fc749731 | CANONICAL |
| EV-08 | AC5（.NET 稳定树绿跑，r1） | verification/FEA-12-DSIM-1/logs/dotnet-full-3.log | - | 5ffeee7b817ecd728d338c8ffbc6a92656ca64dc1a967c80217319580336d7a6 | CANONICAL |
| EV-09 | AC5（.NET 首跑 flaky 归因） | verification/FEA-12-DSIM-1/logs/dotnet-full-1.log | - | 6b90736058321715f6108f4bb3eb63f4675871e58015f61b0869e4a257b106be | SOURCE_PIN |
| EV-10 | AC5（.NET 二次 flaky 归因） | verification/FEA-12-DSIM-1/logs/dotnet-full-2.log | - | 7b1d1ccc739eea08ca4db5b24de1cfa823f3617bda2a818e25e01f5aaf5bc458 | SOURCE_PIN |
| EV-11 | AC4（静态扫描） | verification/FEA-12-DSIM-1/logs/static-scan.log | - | 5339b85a248e8214c31083f62bb46d38978ad476babd5c35d675cee34444d08d | CANONICAL |
| EV-12 | AC4（运行时哨兵） | verification/FEA-12-DSIM-1/logs/sentinel-probe.log | - | c642f1cbcd4780c963fa9bb17c8d5b1932d265733ffac80ec79ddf92145f5175 | CANONICAL |
| EV-13 | AC5（pins） | verification/FEA-12-DSIM-1/logs/verify-pins.log | - | 8b5b4fbe88ba558c65bc2db6823d5c1277a94139151aa0d0625bb0310b510ffa | CANONICAL |
| EV-14 | AC2/AC4（隔离证明，r2） | verification/FEA-12-DSIM-1/ISOLATION-EVIDENCE.md | - | f1cc4c49e126bbab5d1c5064ea7cb2f6f2fcbc5f47c031faa361b88dd94c3058 | CANONICAL |
| EV-15 | AC5（AC 矩阵，r2） | verification/FEA-12-DSIM-1/AC-MATRIX.md | - | d385caa20b73d7b6ac4d17232c78009b7cdb9f7caea0411f353f51ca1ea9d83e | CANONICAL |
| EV-16 | AC5（环境，r2） | verification/FEA-12-DSIM-1/ENVIRONMENT.md | - | 980bf99e280e3f7c8c6582b26407d8b0b9caae8933f5b66449eb12a632c1a89c | CANONICAL |
| EV-17 | AC4（扫描脚本） | verification/FEA-12-DSIM-1/tools/static-scan.ps1 | - | 7855217f100451ed155243accffc350ba8cdfe2a93d3045af0803c640e5a70ea | SOURCE_PIN |
| EV-18 | AC4（哨兵探针） | verification/FEA-12-DSIM-1/tools/sentinel-probe.py | - | b27f8b5b44ace71293e3f64fc95bbf689dce802659ffa4b2da0550ce12942be8 | SOURCE_PIN |
| EV-19 | AC5（R-002 处置/仓外过程日志 manifest） | verification/FEA-12-DSIM-1/agent-output-manifest.json | - | 925a2a6147633784a239943ec97ef21ff2cb09f88b4a5c5b4fafa7f7a5694c14 | SOURCE_PIN |
| EV-20 | AC5（.NET r2 尝试 flaky 归因） | verification/FEA-12-DSIM-1/logs/dotnet-r2-1.log | - | 01538fa854aab411d94c89bc9a7068c70373d6d9ac477b24085cac7a78891b53 | SOURCE_PIN |
| EV-21 | Gate/Review（r2 独立复审 approved） | doc/reviews/FEA-12-DSIM-1-r2.md | - | 5b54947b8a9aafa30920275aedb04cdc79ea9904e05281d941fa4055c2c79f0e | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | — | NOT_APPLICABLE | — | — | 未创建 workspace temp：全部 scratch 在 pytest `tmp_path` 与 `tempfile.TemporaryDirectory()`（自清理）内；R-001 junction/hardlink fixture 也在 `tmp_path` 内并由测试 `finally` 解除；无残留资源需处置。 |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\` | verification/FEA-12-DSIM-1/agent-output-manifest.json | R-002 处置：`gates.log`（r2 门禁汇总）、`check-final.log`（r2 `check.ps1` 最终输出）、`check-final-r1.log`（r1 历史）迁出证据目录；逐文件 bytes/sha256 见所引 manifest；判别力证据仍以仓内 `verification/FEA-12-DSIM-1/**` 为准；无需迁移。 |

## Closeout Record

- Closeout date / DSH：2026-11-05 / DSH（Lead/Architect/Integrator）。
- 终态：`done`；integration_commit / delivery_head = `beee351bb`（r2 docs head，含 `d5925957b` 修复；main 线性集成，无 merge commit）。
- Review 链：r1 approved（P0/P1=0；P2=2/P3=7）→ r2 最小返修 → **r2 approved（P0/P1/P2=0，P3=3 非阻断）**；Reviewer 均为独立上下文 fresh subagent（session 见 frontmatter/报告）。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- AC 定稿：AC1 MET、AC2 MET（限定：调用者干净隔离根 + 自身写目标拒绝 reparse/hardlink；TOCTOU 未消除）、AC3 MET、AC4 MET、AC5 MET。
- 残余风险（已登记）：①真实 D 流程（Windows 回收站桥）**NOT_RUN**，生产默认 typed 不可用，需用户另行专门授权；②TOCTOU 并发重植窗口未消除（单写者测试替身；真实桥需绑定句柄）；③manifest 写失败/崩溃恢复未实现（属真实桥）；④manifest 写失败/损坏、journal 目录/符号链接等残余用例未覆盖；⑤.NET 全量首跑 flaky 为既有 verification 并发写窗口债务（本卡未改 .NET）。
- r2 Review P3 处置：AC2「零写入」措辞已改为「根外零写入 + 根内 journal attempt 说明」；AC5 基线/复跑口径已澄清；Handoff 中旧门禁数字（2 warnings/15 Task、--tb=no）为历史快照，以本卡 Closeout 与 `verification/FEA-12-DSIM-1/` 证据为准（不改写 Handoff 原字节）。
- 删除、迁移、归档数量/字节数：r2 将 `gates.log`/`check-final.log` 从 evidence_dir 迁至 workspace agent-output（3 files，manifest 见 EV-19）；无仓外 temp 残留。
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新；本卡为终态，不进入 READY DAG。
- 后续：真实 D 流程需用户专门授权后另开卡；模拟件作为 test double 保留。
