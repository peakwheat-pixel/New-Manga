---
id: FEA-12-DSIM-1
title: FEA-12 D 流程模拟切片（可注入原文件回收适配器 + SimulatedRecycleBin，无真实 OS API）
kind: implementation
governance_version: 3
status: in_review

approval: 用户 2026-11-05 口径（隔离 fixture + 模拟回收站路径，不触碰真实回收站）；ADJ-2026-11-05-FEA-12-SCOPE D5；DSH 2026-11-05 释放
suggested_owner: dsh（dsh-agent-team teammate）
owner: dsh-agent-team teammate `fea12-dsim-impl`
reviewer: 独立上下文 fresh subagent（未参与实现；会话 id 记录在 Review 报告）
depends_on: []
base_commit: 37f84bb895c9ef9b64e3865f3a92b245f2e28a7c   # 释放时由 Lead 固定
branch: main
worktree: G:\CODEX\New Manga（main 主工作树；未新建分支/worktree）
integration_commit: null
delivery_head: 3d0d325f7
canonical_evidence_status: pending
resource_closeout_status: pending
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
- [x] **AC2 模拟实现**：`SimulatedRecycleBin` 全部操作限制在隔离根；manifest 可审计；不调用任何 Windows API。 <<MET>>
- [x] **AC3 失败语义**：失败注入下原文件字节/集合不变、结果逐项 typed、零永久删除/零 DB 删除；"D 失败不得降级 C"有测试。 <<MET>>
- [x] **AC4 隔离与禁令**：静态扫描 0 处 Windows 回收站 API；运行时哨兵证明隔离根外零变化；测试无 `%APPDATA%`/真实盘符/真实回收站路径。 <<MET>>
- [x] **AC5 交付件与门禁**：Task/Handoff/`verification/FEA-12-DSIM-1/`（隔离与扫描日志）；`check.ps1` PASS、`verify_pins.ps1` 18/18、pytest 全量与 .NET 基线记录（无 Python 生产路径接线，.NET 应零差异）。 <<MET>>

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）。本卡只新增文件，不改既有生产文件（`__init__.py` 仅 additive 导出除外）。

## 禁止范围

见 `out_of_scope`。另：不得把模拟实现描述为真实回收站验证；不得写真实盘符路径；不得 push；不得删测试/放宽断言。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings --tb=no`；`pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1`；`C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py` | 隔离 `tmp_path` + `tempfile.TemporaryDirectory()`；Python 3.14.6 | **PASS**：fea12 **13 passed**（EXIT 0）；静态扫描 766 files / **0** Windows 回收站 API、2 test files / **0** 真实路径字面量、2 modules / **0** 删除/DB 回退（EXIT 0）；运行时哨兵 `PASS: runtime sentinel outside the isolated root unchanged`（EXIT 0） | `verification/FEA-12-DSIM-1/logs/pytest-fea12.log`、`logs/static-scan.log`、`logs/sentinel-probe.log`、`ISOLATION-EVIDENCE.md`、`AC-MATRIX.md` |
| AC5 | 全量 pytest（基线 + 交付 head）；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-DSIM-1.md` | 仓库根；共享工作树（并发改动见下） | **PASS（含已归因 flaky）**：基线 clean tree `3073 passed / 10 skipped`（EXIT 0）→ 交付 head `3093 passed / 10 skipped`（EXIT 0；+20 = 本卡 13 + 并发已提交 LINEAGE-1 r3 7）；全量 .NET 首跑/二次各 **1 failed / 670 passed / 7 skipped（App.Tests）**、稳定树复跑 **失败 0 / 通过 1403 / 跳过 79**（8 assemblies）；pins **18/18 PASS**；`check.ps1` 结果见 `logs/check-final.log` | `logs/baseline-pytest.log`、`logs/pytest-full.log`、`logs/dotnet-full-1.log`、`logs/dotnet-full-2.log`、`logs/dotnet-full-3.log`、`logs/verify-pins.log`、`logs/gates.log` |

## 依赖、风险与阻塞

- 依赖：无 Task 硬依赖（纯新增文件；与 CORE 写域不相交，可并行；若 CORE 需用该协议由 Lead 裁决改为 CORE 依赖）。
- 风险：①用户可能把"模拟回收站路径"理解为 D 真实实现 → 本卡明确 OUT 并交用户裁决；②未来真实 D 实现需重做 OS 适配器（本卡只保证接口稳定）；③不得被 UI/Release 误引用为"D 已实现"。
- 阻塞解除标准：本卡 Review approved + 集成；真实 D 需新授权。

## 交付与运行记录

- Handoff：[FEA-12-DSIM-1-3d0d325f7](../handoffs/FEA-12-DSIM-1-3d0d325f7.md)（实现 commits `94a12e93f` + `3d0d325f7`；交付 docs commit 其后相邻提交）。
- Review：待 Lead 派**独立上下文 fresh subagent**（实现者 `fea12-dsim-impl` 未自审）。
- 实际测试：见「测试要求」表与 `verification/FEA-12-DSIM-1/logs/gates.log`；关键数字：pytest fea12 13 passed；全量 pytest 3093 passed / 10 skipped（基线 3073/10）；全量 .NET 稳定树复跑 0 failed / 1403 passed / 79 skipped；pins 18/18；静态扫描 766 files / 0 Windows 回收站 API；运行时哨兵 PASS；`check.ps1` 见 `logs/check-final.log`。
- **边界声明（不得误读）**：本卡只交付 **D 流程模拟切片**——application 端口 + 生产 typed 不可用默认实现 + `SimulatedRecycleBin` 测试替身 + 隔离/哨兵测试。**真实 Windows 回收站行为未实现、未验证（`NOT_RUN`）**，需用户另行专门授权；不得据此声称 D 流程完成；无 Host/UI 生产接线、无 DB/schema/依赖改动、无 push。
- 并发工作树：交付时共享工作树含 FEA-11-LINEAGE-1 r3 已提交改动（+7 tests）与并发 `verification/**` 写入；全量 .NET 首跑 flaky 归因见 `logs/gates.log` G3（本卡未改 .NET）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | src/application/maintenance/recycle_gateway.py | 3d0d325f7 | - | CANONICAL |
| EV-02 | AC2 | src/infrastructure/filesystem/simulated_recycle_bin.py | 3d0d325f7 | - | CANONICAL |
| EV-03 | AC1/AC2/AC3/AC4 | tests/fea12/test_recycle_gateway_sim.py | 3d0d325f7 | - | CANONICAL |
| EV-04 | AC1 | src/application/maintenance/__init__.py | 3d0d325f7 | - | CANONICAL |
| EV-05 | AC1–AC4 | verification/FEA-12-DSIM-1/logs/pytest-fea12.log | - | 568017b8a1eba253ba35733a2d056f767adfb5dfe95bd754e9ff650d2c8093b3 | CANONICAL |
| EV-06 | AC5 | verification/FEA-12-DSIM-1/logs/pytest-full.log | - | 26ad4e0407d37c30fb2b6e71e3dd1b0f23d3f478b3a0cad6aa1c06093cb2387e | CANONICAL |
| EV-07 | AC5（基线） | verification/FEA-12-DSIM-1/logs/baseline-pytest.log | - | 7ef4c572d8941791a1ec9a4e4a601dfe92f893ce8af1c2fe4179dd63cbc67cbe | CANONICAL |
| EV-08 | AC5（.NET 稳定树复跑） | verification/FEA-12-DSIM-1/logs/dotnet-full-3.log | - | a93443eaba8d0fa63b67582367d3059e536b2d3a96ff220ae6d692222f29e8e2 | CANONICAL |
| EV-09 | AC5（.NET 首跑 flaky 归因） | verification/FEA-12-DSIM-1/logs/dotnet-full-1.log | - | 7d3a69becd58d2e0b5245d0fa4ccc51333f1ba71aa96284e78681d9a1856a442 | SOURCE_PIN |
| EV-10 | AC5（.NET 二次 flaky 归因） | verification/FEA-12-DSIM-1/logs/dotnet-full-2.log | - | 59f5c720ea5c0af6ccd2e561c6bdb6fbf23efb4cfb9be7d6784e0c457ba5fd97 | SOURCE_PIN |
| EV-11 | AC4（静态扫描） | verification/FEA-12-DSIM-1/logs/static-scan.log | - | 79f518d1f50c7d145e76bb6293cd686a1ad648a4d1bb05793717d4ede9f2d08f | CANONICAL |
| EV-12 | AC4（运行时哨兵） | verification/FEA-12-DSIM-1/logs/sentinel-probe.log | - | 80cd617edd03a328a480c51bbd14e53a525d6303d90c7bfbfca1b96e358b7269 | CANONICAL |
| EV-13 | AC5（pins） | verification/FEA-12-DSIM-1/logs/verify-pins.log | - | 991a8cbb25a884e4063157042dbaca2b04ab53866247c4e5b9e19b154cd83c13 | CANONICAL |
| EV-14 | AC2/AC4（隔离证明） | verification/FEA-12-DSIM-1/ISOLATION-EVIDENCE.md | - | 13d052d8eeda6e295a9bd27930ff5c3f50bb7f7b573f6ad11cf151a0e65336e5 | CANONICAL |
| EV-15 | AC5（AC 矩阵） | verification/FEA-12-DSIM-1/AC-MATRIX.md | - | f409ecf29bd8aea6d2c8e9c23809315dcdecc447b7578c2f15703b4b32d692cd | CANONICAL |
| EV-16 | AC5（环境） | verification/FEA-12-DSIM-1/ENVIRONMENT.md | - | b84a35d29eb5964d44a97ddabd27e53670b4000ff5980d39bb78e43467089b6a | CANONICAL |
| EV-17 | AC4（扫描脚本） | verification/FEA-12-DSIM-1/tools/static-scan.ps1 | - | 7855217f100451ed155243accffc350ba8cdfe2a93d3045af0803c640e5a70ea | SOURCE_PIN |
| EV-18 | AC4（哨兵探针） | verification/FEA-12-DSIM-1/tools/sentinel-probe.py | - | b27f8b5b44ace71293e3f64fc95bbf689dce802659ffa4b2da0550ce12942be8 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | — | NOT_APPLICABLE | — | — | 未创建 workspace temp：全部 scratch 在 pytest `tmp_path` 与 `tempfile.TemporaryDirectory()`（自清理）内；无残留资源需处置。 |
| agent-output | — | NOT_APPLICABLE | — | — | 未创建仓外 agent-output；判别力证据全部直接入库内 `verification/FEA-12-DSIM-1/**`（见 Canonical Evidence），无需迁移。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 未关闭项及保留原因：真实 D 流程（OS 回收站）NOT_RUN，待用户专门授权。
- 当前指针清理：待关闭时填写。
