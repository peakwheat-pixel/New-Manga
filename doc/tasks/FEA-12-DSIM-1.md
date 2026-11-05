---
id: FEA-12-DSIM-1
title: FEA-12 D 流程模拟切片（可注入原文件回收适配器 + SimulatedRecycleBin，无真实 OS API）
kind: implementation
governance_version: 3
status: ready

approval: 用户 2026-11-05 口径（隔离 fixture + 模拟回收站路径，不触碰真实回收站）；ADJ-2026-11-05-FEA-12-SCOPE D5；DSH 2026-11-05 释放
suggested_owner: dsh（dsh-agent-team teammate）
owner: null
reviewer: 独立上下文 fresh subagent（未参与实现；会话 id 记录在 Review 报告）
depends_on: []
base_commit: null   # 释放时由 Lead 固定
branch: null
worktree: null
integration_commit: null
delivery_head: null
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

- [ ] **AC1 协议与生产默认实现**：`OriginalFileRecycleGateway` 协议 + typed 结果；生产默认实现 fail-closed、零文件操作；无 Host/UI 接线。
- [ ] **AC2 模拟实现**：`SimulatedRecycleBin` 全部操作限制在隔离根；manifest 可审计；不调用任何 Windows API。
- [ ] **AC3 失败语义**：失败注入下原文件字节/集合不变、结果逐项 typed、零永久删除/零 DB 删除；"D 失败不得降级 C"有测试。
- [ ] **AC4 隔离与禁令**：静态扫描 0 处 Windows 回收站 API；运行时哨兵证明隔离根外零变化；测试无 `%APPDATA%`/真实盘符/真实回收站路径。
- [ ] **AC5 交付件与门禁**：Task/Handoff/`verification/FEA-12-DSIM-1/`（隔离与扫描日志）；`check.ps1` PASS、`verify_pins.ps1` 18/18、pytest 全量与 .NET 基线记录（无 Python 生产路径接线，.NET 应零差异）。

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）。本卡只新增文件，不改既有生产文件（`__init__.py` 仅 additive 导出除外）。

## 禁止范围

见 `out_of_scope`。另：不得把模拟实现描述为真实回收站验证；不得写真实盘符路径；不得 push；不得删测试/放宽断言。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `C:/Python314/python.exe -m pytest tests/fea12/test_recycle_gateway_sim.py -q`；静态 grep 脚本；哨兵法 | 隔离 `tmp_path` | NOT_RUN | verification/FEA-12-DSIM-1/logs/ |
| AC5 | 全量 pytest；`dotnet test` 全量；`check.ps1`；`verify_pins.ps1` | 仓库根 | NOT_RUN | logs/gates.log |

## 依赖、风险与阻塞

- 依赖：无 Task 硬依赖（纯新增文件；与 CORE 写域不相交，可并行；若 CORE 需用该协议由 Lead 裁决改为 CORE 依赖）。
- 风险：①用户可能把"模拟回收站路径"理解为 D 真实实现 → 本卡明确 OUT 并交用户裁决；②未来真实 D 实现需重做 OS 适配器（本卡只保证接口稳定）；③不得被 UI/Release 误引用为"D 已实现"。
- 阻塞解除标准：本卡 Review approved + 集成；真实 D 需新授权。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-12-DSIM-1\` | DELETE_SAFE（交付后） | — | 待交付时填写 | 仅模拟回收站隔离根 |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\*\FEA-12-DSIM-1\` | PRESERVE_REFERENCED | 同上 | 待交付时填写 | 重复执行日志 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 未关闭项及保留原因：真实 D 流程（OS 回收站）NOT_RUN，待用户专门授权。
- 当前指针清理：待关闭时填写。
