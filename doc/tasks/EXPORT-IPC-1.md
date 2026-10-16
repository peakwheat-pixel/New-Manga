---
id: EXPORT-IPC-1
title: Tauri host 接线导出控制/查询面（CancelExport/GetExportSnapshot/GetExportHistory）+ 去除路径的 WebView 投影——P14 工作台第二处前置
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261016_confirmed_second_missing_host_surface
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P16, P16-C1, EXPORT-REVEAL-1, UI-DESIGN-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/EXPORT-IPC-1
---

# EXPORT-IPC-1：Tauri host 接线导出控制/查询面（去除路径的 WebView 投影）

## 来源与缺口事实（Coordinator 只读复核确认）

**这是与 [RUN-IPC-1](RUN-IPC-1.md) 同型的第二处未登记缺口**——同样是"契约已冻结 + Core 已实现 + host 侧无出口"，同样是设计基线 §6 绑定了命令但**未核对 host 是否已有出口**（BL-14 根因的第二例）。

| 事实 | 证据（当前 main） |
|---|---|
| Core **已实现**三命令 | `src/bootstrap/core_service.py`：`CancelExport` 2 处、`GetExportSnapshot` 2 处、`GetExportHistory` 1 处命中 |
| host **完全没有**出口 | `apps/desktop/src-tauri/src/*.rs` 对 `cancel_export` / `get_export_snapshot` / `get_export_history` / `CancelExport` / `GetExportSnapshot` / `GetExportHistory` / `library_cancel_export` / `library_get_export*` **全部 0 命中**；生产命令表无一条导出控制/查询命令 |
| 设计基线**绑定为可用** | §6 的 **W22**（导出取消）、**W23**（导出进度/终态查询）、**W24**（导出历史）分别绑定 `CancelExport` / `GetExportSnapshot` / `GetExportHistory` |
| 设计 §7 的 G 清单**未覆盖** | G17=事件（已 done）、G18=缩略图、G20=打开文件夹（EXPORT-REVEAL-1）、G26=导入进度、G13=revision pin —— **无一条覆盖本缺口** |
| 契约**已裁决路径不得下发** | M2-C1 §5 行 164：`GetExportHistory` "只供可信 Tauri host 使用，host 不得将路径或写引用转发给 WebView"；§10.3 **L853**："Host 不得把绝对路径或 `ExportTargetRef` 转发给 React/WebView；**前端若需展示状态/触发打开文件夹，必须经独立 host command 按不透明 `export_id` 操作，不能借此取得路径**" |

**结论**：P14 工作台的导出面板（W21–W25）除 `StartExport`（`library_start_export`，HOST-ISSUER-1）与事件（G17）外，**取消 / 进度终态 / 历史三项在 WebView 侧不可达**。EXPORT-REVEAL-1 只交付了 L853 的"触发打开文件夹"那一半；**"展示状态"这一半尚未有任何 host 出口**。

## Acceptance Criteria

- [ ] **AC1 先冻结命名与投影，再实现**：在本 Task 内冻结三条 production-only Tauri command 名，并冻结**去除路径的 WebView 投影**：
      - `CancelExport` `{export_id}` → `ExportProgressSnapshot`（契约 §5 行 162）
      - `GetExportSnapshot` `{export_id}` → `ExportProgressSnapshot`（§5 行 163）
      - `GetExportHistory` `{}` → `{"exports": ExportHistoryEntry[]}`（§5 行 164）
      **投影必须是白名单式重建**：WebView 返回中**绝不允许**出现 `output_path`、任何绝对/相对/UNC 路径、`ExportTargetRef`、grant/session 凭据或文件字节（依 §5 行 164 与 §10.3 L853）。若判定契约需要**补充冻结**该投影形状，按 §3.2 提**契约 minor 修订**并在本 Task 内完成；若判定必须由用户/Codex 裁决 → `BLOCKED`，不得自行放宽。
- [ ] **AC2 实现 + 四处同步同一 commit**：三命令经**既有** `LibraryChannel`/`CoreBridge` 通道调用 Core 冻结命令（wire 名为契约冻结的 **PascalCase**）；生产-only；`PRODUCTION_COMMANDS` / `generate_handler!`（仅生产分支）/ `build.rs` app-manifest（同步计数注释）/ `capabilities` + tauri-build 自动生成权限定义，**同一提交**内完成；probe / AC1 面命令形状不变。
- [ ] **AC3 路径零泄露（本 Task 的核心风险）**：以**测试**断言 —— 三条命令的任何成功返回、typed 拒绝 message/details、以及日志/事件中**均不含** `output_path` 或任何绝对路径；投影由白名单重建而非"删字段"。同时**不得**因本命令消费或改写 `ExportTargetRef` 的单次写授权语义（§10.3 L849–L854）。
- [ ] **AC4 证据**：① allowlist 断言（三命令在生产面存在、probe/AC1 面不存在，且 probe=7 / AC1=6 冻结形状不变）；② 每条命令的 typed 拒绝路径测试（未知/外来 `export_id` → typed 错误；空历史 → 空列表而非错误）；③ **frozen 2.3 bundle 上的真实往返**（免夹具即可达成）：`GetExportSnapshot`/`CancelExport` 对不存在的 `export_id` 返回**域级** typed 错误（证明 wire 名与 payload 形状正确，而非 `PROTOCOL_MALFORMED`），`GetExportHistory` 返回真实历史结构；**不得**伪造一次成功导出。④ 归档原始日志与退出码。
- [ ] **AC5 不回归**：`tests/core/**` 与既有 Rust 测试全绿；CRLF 纯噪音按 `git diff` 判定并恢复。
- [ ] **AC6 交付**：固定 commit、[Handoff](../templates/HANDOFF.md)、Canonical Evidence（真实 sha256）；不 `push`、不 `merge`。
      ⚠️ **BL-15**：**不要**在 Handoff 中自引用"即将产生的 SHA"——先完成全部提交，最后再写 Handoff；或直接把 `delivery_head` 交由 Coordinator 在 closeout 以 `git rev-parse HEAD` 冻结。

## 允许修改范围

- `apps/desktop/src-tauri/src/**`（三命令、投影、四处同步）、对应测试
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（**仅当 AC1 判定需要补充冻结投影形状**时，按 §3.2 提 minor 修订；不得改动既有冻结字段/语义）
- 本 Task、`doc/handoffs/EXPORT-IPC-1-*.md`、`verification/EXPORT-IPC-1/**`

## 禁止范围

- **不得**修改 Python Core（`src/**`）、不得新增 Core wire、不得改既有 Export DTO/Schema/依赖清单（除 AC1 明确授权的契约 minor 修订）；
- **不得**把任何路径、`ExportTargetRef` 或凭据下发到 WebView（请求/返回/事件/错误四处）；
- **不得**改动 `library_start_export` / `library_reveal_export_folder` 的既有语义；**不得**触碰其他 Task 的 verification 目录；
- **不得**改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`；**不得触碰**用户 19 项 dirty/untracked（逐条）：
  `AGENTS.md`、`.qoder-credits/report.json`、`doc/00_INDEX.md`、`doc/01_FUNCTIONAL_ARCHITECTURE.md`、
  `doc/03_DATA_MODEL.md`、`doc/04_USER_FLOW.md`、`doc/06_TRANSLATION_PIPELINE.md`、`doc/09_COLLABORATION.md`、
  `doc/11_ARCHITECTURE_MAPS.md`、`doc/12_ROADMAP.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、
  `doc/WORKTREE_SAFETY_INVENTORY.md`、`doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md`、`doc/tasks/P02-NEW-TIME-X6.md`、
  `doc/tasks/P02.md`、`doc/templates/HANDOFF.md`、`doc/templates/REVIEW.md`、`doc/templates/TASK.md`、
  `verification/PROJECT-ROADMAP-20261008/ROADMAP.md`；
- 不删除/弱化既有测试；不 `push`/`merge`/`reset`/`stash`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 冻结三命令名与去路径投影；裁决是否需契约 minor 修订 | 只读契约 §5 行 162–164、§10.3 L853 | NOT_RUN | 无 |
| AC3 | 断言成功返回/拒绝 message/日志均不含 `output_path` 或绝对路径 | 构建产物 | NOT_RUN | 无 |
| AC4-① | allowlist 断言：生产面三命令存在 / probe+AC1 面不存在，probe=7 / AC1=6 不变 | 构建产物 | NOT_RUN | 无 |
| AC4-② | typed 拒绝路径测试（未知/外来 export_id；空历史 → 空列表） | 构建产物 | NOT_RUN | 无 |
| AC4-③ | frozen 2.3 上 `GetExportSnapshot`/`CancelExport` 域级错误 + `GetExportHistory` 真实结构 | 已重建 bundle（junction） | NOT_RUN | 无 |
| AC5 | `tests/core/**` + Rust 测试全绿 | 构建产物 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：P16/P16-C1（导出 Core 与 wire 冻结，done）、EXPORT-REVEAL-1（同源路径保密先例与 §10.3 L853 的另一半）、UI-DESIGN-1（设计基线，done）。
- 风险一：**最容易犯的错是把 `output_path` 顺手透传**。投影必须**白名单重建**，且必须有测试钉死"返回/拒绝/日志三处都不含路径"。可参考 EXPORT-REVEAL-1 的 `EXPORT_REVEAL_FAILED` 用 `map_err(|_| …)` 丢弃宿主错误文本以夹带路径的处置。
- 风险二：`CancelExport` 是**写操作**（取消活动导出）。测试必须只走"未知 `export_id` 的拒绝路径"，不得在共享/bundle 目录里真实取消一个导出。
- 风险三：`GetExportHistory` 的 `ExportHistoryEntry` 含 `output_path` 与若干终态字段；投影需明确保留哪些字段供 UI 展示（状态/时间/格式/页数），并在 Handoff 中逐字段说明**保留与剔除**的理由。
- 阻塞条件：若 AC1 判定契约不足以支撑去路径投影、且必须由用户/Codex 裁决字段取舍 → `BLOCKED` + 证据。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 6）：依据设计基线 §6 的 W22/W23/W24 绑定 + Coordinator 只读复核（Core 已实现 / host 全变体 0 命中 / §7 G 清单未覆盖 / §5 行 164 与 §10.3 L853 已裁决路径不得下发）。**释放前先核实缺口真实**。
- **BL-14 第二例登记**：与 RUN-IPC-1 同根因（设计 §6 只核契约冻结、未核 host 出口）。
- Handoff：尚无。Review：尚无。实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/EXPORT-IPC-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/EXPORT-IPC-1 | verification/EXPORT-IPC-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放时同步。
