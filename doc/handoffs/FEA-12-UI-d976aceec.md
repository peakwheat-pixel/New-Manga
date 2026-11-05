---
task_id: FEA-12-UI
title: FEA-12 回收站 UI 切片（V2 单本彻底删除 + 软删/恢复 + 文案诚实化）
status: in_review
owner: dsh-agent-team teammate `fea12-prereq-impl`
reviewer: null   # 待 DSH 派独立上下文 fresh subagent；实现者不自审
base_commit: 9daa94a25
delivery_head: d976aceec
evidence_dir: verification/FEA-12-UI
canonical_evidence_status: pending
resource_closeout_status: pending
branch: null
worktree: null
integration_commit: null
---

# FEA-12-UI 交付 Handoff（V2 回收站 UI 切片，L2）

## 概述

按 `doc/tasks/FEA-12-UI.md`（ZCode SCOPE-ADJ 冻结、DSH 2026-11-06 释放，base `9daa94a25`）实现 V2 回收站 UI 切片：

1. **单本彻底删除**（C 流程）：只读披露（PD-01 三项 + 完整 current 保护集 + artifact 表达 + 保留项声明）→ 硬勾选「我理解不可恢复」+ **逐书 digest** 绑定 → 单帧 `library_delete_book_permanently`（payload 键集恰 `{book_id, confirm_permanent_delete, inventory_digest}`）→ typed 结果处置（STALE 自动重预览、BOOK_BUSY 预阻断、CLEANUP_PENDING 同 digest 重试、BOOK_NOT_FOUND 刷新）。
2. **软删入口**：书架/详情「移入回收站」危险确认（默认焦点取消、Esc 关闭、Enter 不提交）→ 单帧 `library_move_to_trash`；成功后清选中 + 刷新 + 本地撤销条（RestoreFromTrash，恢复成功才提示成功）。
3. **回收站列表/恢复**：`ListTrash` 单一数据源（无总数、无缩略图、cursor 原样回传不持久化、只显示“已加载 N 项”）；多选恢复按勾选顺序单帧 `library_restore_from_trash`，逐项 conflicts reason 白名单+兜底，不伪报整批成功。
4. **C-07 零变更**：独立 `ITrashController`（`Services/TrashModels.cs`）由 `HostController`/`NullHostController`/`FakeHostController` 分别实现；`IHostController.cs`/C-07 清单/契约/schema/依赖零改动；`generate_api_inventory.py --check` PASS；pins 18/18。
5. **文案诚实化**：回收站占位“能力待接入”文案全部替换为真实列表/空态/失败态/能力缺失态/只读态；Fluent 抽屉与删除 tooltip 改为“Fluent 前端未接线、请用 V2 前端”且不称能力缺失；页面级删除文案改“页面级删除无命令”。
6. **AC10 禁令**：全流程 0 帧 `library_purge_trash`、0 帧 `library_delete_books_permanently`；`ITrashController` 无对应成员。

## Commit 列表

| # | commit | 内容 |
|---|---|---|
| C1 | `d976aceec` | 实现 + 测试 + `verification/FEA-12-UI/` L2 证据（本 Handoff 提交紧随其后） |

> `delivery_head` 记录 C1；本 Handoff 提交在 C1 之后，构成 in_review 新 head。

## 变更文件（仅 allowed_paths）

- 生产：`Services/TrashModels.cs`（新）、`Services/HostController.cs`、`Services/NullHostController.cs`、`ViewModels/V2/Library/TrashViewModel.cs`（新）、`ViewModels/V2/Library/LibraryViewModel.cs`、`Views/V2/Library/RecycleBinView.axaml(.cs)`、`Views/V2/Library/LibraryView.axaml`、`Views/V2/Library/BookDetailPanel.axaml`、`Views/Fluent/ShelfPageView.cs`（仅文案）。
- 测试：`tests/NewManga.App.Tests/{FakeHostController.cs,TrashUiTests.cs(新),V2ShellUiTests.cs,NoDbOsAccessTests.cs(新)}`；`tests/NewManga.Host.Tests/{Fea12TrashUiIpcTests.cs(新),Support/Fea12ProductionFixture.cs(新)}`。
- 文档/证据：本卡、本 Handoff、`verification/FEA-12-UI/**`。
- 未改：`IHostController.cs`、`RunContracts.cs`、C-07 清单、任何 pinned 契约、`src/**`、`NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`、STATUS/PLAN/LEDGER/reviews、无新依赖/schema/wire。

## 门禁与实测（2026-11-06，Asia/Shanghai）

| 场景 | 命令 | 结果 |
|---|---|---|
| 全量 .NET | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test ... --no-build --nologo` | **PASS**：1474 passed / 0 failed / 82 skipped（App.Tests 703/0/7；Host.Tests 144/0/51；CoreClient 167/0/24；其余 4 项目全绿） |
| 定向 UI/静态（headless + 真实窗口） | `dotnet test NewManga.App.Tests ... --filter "TrashUiTests\|NoDbOsAccessTests\|V2ShellUiTests.RecycleBin\|V2ShellUiTests.MoveToTrash"`（curated `NEWMANGA_EVIDENCE_DIR`） | **PASS 28/28**；4 张快照（`screens/`）；`TrashUiTests` 23、`NoDbOsAccessTests` 3 |
| 真实 IPC/wire | `$env:NEWMANGA_FEA12_UI_IPC=1` + curated；`Fea12TrashUiIpcTests` | **PASS 1/1**：真实 `src/bootstrap/core_service.py`，27 wire 帧；0 purge、0 批量删除；逐书 digest 绑定；DataRoot 仓外；哨兵指纹前后相等 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 18/18** |
| API inventory / C-07 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **PASS**（`IHostController.cs` 零改动） |
| 契约/计划/Python 零漂移 | `git diff --name-only 9daa94a25..HEAD -- doc/plan doc/contracts src/` | **空** |
| check.ps1 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-UI.md` | 见交付后复跑（卡已 `in_review`；证据表/Resource Manifest 完整） |
| L3 真机 | 人工 | **NOT_RUN**（冻结 OUT/L10，不写 PASS） |

证据目录：`verification/FEA-12-UI/`（`AC-MATRIX.md`、`ENVIRONMENT.md`、`logs/`、`screens/`、`fea12-trash-ui-ipc.json`、`agent-output-manifest.json`）。所有证据 sha256 已登记在卡 Canonical Evidence（worktree 实测；DSH 集成时补 commit）。

## 关键实现决策与发现

1. **digest 绑定（R12，Review 重点）**：M2-C1 §5.13 预览返回集合级 `inventoryDigest` 与逐书 `inventoryDigests[bookId]`；单本删除命令在 Core 侧按**逐书** digest 重算比较。本实现以 `inventoryDigests[bookId]` 作为唯一确认绑定值，集合 digest 仅展示。真实 IPC 初次以集合 digest 删除得到 typed `BOOK_DELETE_STALE_PREVIEW`，修正后 wire 断言：集合 digest ≠ 逐书 digest，删除帧 digest = 逐书 digest。
2. **rev 2.14 完整 current 集**：`protection.currentRegionRevisionIds`/`currentArtifactRevisionIds` 缺失或 null → `CurrentSetKnown=false` → 禁止确认删除（fail-closed）；仅空数组才表示“无 current”。artifact 表达 = 数组长度（`currentArtifactRevisionIds.Count`）。
3. **能力探测**：`ITrashController.ProbeTrashCapabilitiesAsync` 只读 `core.ping`（`library.trash.read/write/preview`），不发送任何回收站命令探测；缺读能力 → 0 list 帧、不渲染空列表；只缺写/preview → 允许真实只读列表。
4. **单帧纪律**：每个端口方法恰好映射一 Host 命令帧；UI 无批量/清理以外的隐藏调用；`library_purge_trash` 与批量删除在接口层不存在。
5. **隔离**：真实 IPC fixture 启动仓库自身 Python Core（csc 编译仅转发的 launcher），DataRoot/日志/sidecars 均在仓外 `G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-*`；sentinel 树 SHA-256 前后一致。

## 风险与遗留

1. **L1–L10 全部保留**（见卡）：批量删除无 UI、无缩略图/内容预览、cleanup 重试仅会话内、无总数/逐项 busy、restore reason 首版恒 `TRASH_ENTRY_NOT_FOUND`、导出占用仅删除时 `BOOK_BUSY`、Fluent 回收站未接线、D 流程 NOT_RUN、无保留期限承诺、L3 真机 NOT_RUN。
2. **R12 digest 语义**：已按真实 Core 修正并断言；若后续 Core 调整 digest v2 记录/集合口径，需同步扩展。
3. **R13 证据卫生**：`verification/FEA-12-UI/` 内非本卡未跟踪历史/意外同步证据已整体归档到 `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\`（`spill-tree`/`moved-tree`），本目录只保留本卡 14 个证据文件；归档不参与 Canonical Evidence。
4. **既有 flaky**：Fluent 视觉/交互测试在全量并行首跑曾抖动（与本卡写域无关）；本卡最终全量首跑 0 失败。若复跑遇到，请保留首跑/复跑日志，不归因本卡。
5. **未跑项**：pytest 未重跑（本卡零 Python 改动，引用 FEA-11 基线 3073/10）；L3 真机 NOT_RUN。
6. **未 push**；未提交他人文件；`verification/FEA-09` 在全量运行后已 `git checkout --` 恢复。

## 资源处置

| resource | disposition | 说明 |
|---|---|---|
| `G:\CODEX\New Manga.workspace\temp\FEA-12-UI\` | DELETE_SAFE | 测试日志副本；Canonical 日志已固化 |
| `G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-*` | PRESERVE_REFERENCED | 真实 IPC 隔离根（DataRoot/sidecars/wire/哨兵）；Review/集成后可删 |
| `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\` | ARCHIVED | evidence_dir 非本卡证据整体归档 |
| worktree | NOT_APPLICABLE | 未创建 |

## 下一任务建议

- **Task ID / 标题**：`FEA-12-UI` **独立复审**（DSH 派 fresh subagent，只读 delivery head `d976aceec` + 本 Handoff 提交）。
- **推荐 Agent / Reviewer**：Lead 派独立上下文 fresh subagent（2026-10-31 裁决：上下文独立即可；实现者不自审；ZCode/Codex 可选）。
- **前置依赖**：无（CORE 已闭环）；Review approved 后由 DSH 集成 closeout（L3 真机另授权）。
- **Recovery point**：仓库 `G:\CODEX\New Manga`（main）；实现 commit `d976aceec`；未 push、无分支/worktree。
- **允许修改路径 / 禁止范围**：见卡 allowed_paths/out_of_scope；Reviewer 只读，不改实现。
- **验证命令与 Gate**：卡「测试要求」+ 本 Handoff 门禁表（全量 .NET 分列、pins 18/18、API check、真实 IPC、check.ps1）。
- **可直接转发给 Agent 的指令**：

```text
你是 FEA-12-UI 的独立复审者（未参与实现）。仓库 G:\CODEX\New Manga（main）。
只读复审 delivery head `d976aceec`（实现 commit）+ 其 Handoff 提交（doc/handoffs/FEA-12-UI-d976aceec.md）。
对照 doc/tasks/FEA-12-UI.md（AC1–AC10 + L1–L10 + 冻结决策 Q1–Q8）、doc/reviews/SCOPE-ADJ-2026-11-05-zcode.md B 节、
doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md rev 2.14 §5.11/§5.13/§5.14、C-04b v1.1 §2.0–2.2、C-09 SC-B06、C-07。
重点复核：
①C-07 零变更：IHostController.cs 未改、ITrashController 独立、generate_api_inventory.py --check PASS；
②digest 绑定：单本删除是否只用 inventoryDigests[bookId]（逐书），真实 wire 是否证明集合 digest ≠ 逐书 digest；
③单帧纪律：probe→1 list；preview→confirm→1 delete；stale 不重发删除；cleanup 同 digest 重试无新 preview；
④fail-closed：旧 Core 缺 current 数组/能力缺失时 0 删除帧、不渲染空列表；Host 只读 0 写帧；
⑤AC10 禁令：0 帧 purge、0 帧批量删除；payload 键集恰 3 键；无伪造成功/总数；
⑥证据真实性：verification/FEA-12-UI/ 的日志/截图/IPC JSON 与卡 Canonical Evidence sha256 一致；
⑦测试未放宽（V2ShellUiTests 旧断言意图保留）；未改他人写域/pinned 契约。
输出 doc/reviews/FEA-12-UI-r1.md（P0/P1/P2 分级 + verdict approved/changes_requested +
reviewer 身份/session ID + reviewed_head）。不得修改实现文件；不 push。
```

## Review 就绪声明

实现与 L2 证据已提交于 `d976aceec`；AC1–AC10 全部 `<<MET>>`（L1–L10 保留、L3 `NOT_RUN`）；
全量 .NET 1474/0/82、定向 UI 28/28、真实 IPC 1/1、pins 18/18、API check PASS、契约/计划/Python diff 空、check.ps1 见复跑；
**实现者不自审**，请 DSH 派独立上下文 fresh subagent 复审本 head。
