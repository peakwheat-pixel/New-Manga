---
id: READER-IPC-1
title: Tauri host 接线阅读器投影面（GetReaderProjection / SaveReadingProgress）——P17 阅读器页前置
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261016_confirmed_third_missing_host_surface
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P16, P16-C1, UI-DESIGN-1, EVENTS-FWD-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/READER-IPC-1
---

# READER-IPC-1：Tauri host 接线阅读器投影面

## 来源与缺口事实（Coordinator 只读复核确认）

**同一根因的第三例**（前两例：[RUN-IPC-1](RUN-IPC-1.md) Run 控制面、[EXPORT-IPC-1](EXPORT-IPC-1.md) 导出控制/查询面）：契约已冻结 + Core 已实现 + host 侧无出口，且设计 §7 的 G 清单未覆盖。

| 事实 | 证据（当前 main） |
|---|---|
| Core **已实现** | `src/bootstrap/core_service.py`：`GetReaderProjection` 2 处、`SaveReadingProgress` 2 处命中 |
| host **完全没有**出口 | `apps/desktop/src-tauri/src/*.rs` 对 `get_reader_projection` / `save_reading_progress` / `GetReaderProjection` / `SaveReadingProgress` / `library_get_reader` / `library_save_reading` / `reader_projection` **全部 0 命中**；生产命令表无一条阅读器命令 |
| 设计基线**绑定为可用** | §6 的 **W18**（章节阅读投影）绑 `GetReaderProjection`、**W19**（阅读进度保存）绑 `SaveReadingProgress` |
| 设计 §7 G 清单**未覆盖** | 无任何 G 条目描述该缺口 |
| W20（进度失效重查）**已就绪** | `ReadingProgressChanged` 已由 [EVENTS-FWD-1](EVENTS-FWD-1.md)（done）转发（`core:ReadingProgressChanged`） |
| 契约形状 | §5 行 158：`GetReaderProjection` `{chapter_id, mode: original\|translated, start_position: resume\|beginning}` → `ReaderProjection`；行 159：`SaveReadingProgress` `{chapter_id, mode, page_id, scroll_offset_y?, elapsed_seconds_delta?}` → `ReadingProgressSnapshot`；DTO 见 §6.3 |
| 无路径下发风险 | §6.3 明定 `ReaderProjection` 中缺失的译图以 **null** 表示，**绝不用路径或伪造引用**；`ReaderPageProjection` 使用**只读资源引用**（走既有 §10 资源通道） |

**结论**：P17 阅读器页除 W5（`resolve_page_resource`，已有）、W2/W3（`list_chapters`/`list_chapter_pages`，已有）与 W20（事件，已 done）外，**章节投影读取与进度保存两条命令在 WebView 侧不可达**。

## Acceptance Criteria

- [ ] **AC1 先冻结命名再实现**：在本 Task 内冻结两条 production-only Tauri command 名（建议沿既有同族前缀：`library_get_reader_projection`、`library_save_reading_progress`），并声明其参数/返回**直接对应**契约 §5 行 158/159 的冻结形状（**不新增 wire、不改契约、不改 Core**）。若判定契约确需补充"产品命令名"裁决 → `BLOCKED` 交 Coordinator。
- [ ] **AC2 实现 + 四处同步同一 commit**：经**既有** `LibraryChannel`/`CoreBridge` 通道调用 Core 冻结命令（wire 名为契约冻结的 **PascalCase** `GetReaderProjection` / `SaveReadingProgress`）；生产-only；`PRODUCTION_COMMANDS` / `generate_handler!`（仅生产分支）/ `build.rs` app-manifest（同步计数注释）/ `capabilities` + tauri-build 自动生成权限定义，**同一提交**内完成；probe / AC1 面形状不变（probe=7 / AC1=6）。
- [ ] **AC3 不得越界、不得泄露、不得破坏既有语义**：
      - `ReaderPageProjection` 的只读资源引用必须**保持不透明**并继续经 §10 资源通道解析（**不得**在返回中放入路径、目录或可解码出路径的字段；缺失译图必须是 **null**，不得伪造引用，§6.3）；
      - `SaveReadingProgress` **不得**消费或改写任何资源引用；`elapsed_seconds_delta` 缺失时**不得**重发（§5 行 159 语义）；
      - `GetReaderProjection.start_position="beginning"` **不得**改动 `saved_progress`（§6.3）；
      - 不暴露 host-only 能力；不改其他命令语义。
- [ ] **AC4 证据**：① allowlist 断言（两命令生产面存在、probe/AC1 面无，且 probe=7 / AC1=6 不变）；② typed 拒绝路径测试（未知 `chapter_id` → `TARGET_NOT_FOUND`；非法 `mode` → `INVALID_REQUEST`；未知 `page_id` 保存 → typed 错误且**未产生写副作用**）；③ **frozen 2.3 bundle 上的真实往返**（免夹具即可达成）：两命令对不存在的 `chapter_id`/`page_id` 返回**域级** typed 错误（而非 `PROTOCOL_MALFORMED`），据此证明 wire 名、payload 形状与端到端可达；**不得**伪造一次成功投影；④ 归档原始日志与退出码。
- [ ] **AC5 不回归**：`tests/core/**` 与既有 Rust 测试全绿；CRLF 纯噪音按 `git diff` 判定并恢复。
- [ ] **AC6 交付**：固定 commit、[Handoff](../templates/HANDOFF.md)、Canonical Evidence（真实 sha256）；不 `push`、不 `merge`。
      ⚠️ **BL-15**：不要在 Handoff 中自引用"即将产生的 SHA"；先完成全部提交，最后再写 Handoff。

## 允许修改范围

- `apps/desktop/src-tauri/src/**`（两命令、四处同步）、对应测试
- 本 Task、`doc/handoffs/READER-IPC-1-*.md`、`verification/READER-IPC-1/**`

## 禁止范围

- **不得**修改 Python Core（`src/**`）、契约（`doc/contracts/**`）、Schema、依赖清单；
- **不得**新增 wire/事件/字段；不得把路径或资源引用内的可变部分下发；
- **不得**改 `library_start_export` / `library_reveal_export_folder` / Run 六命令的既有语义；不得触碰其他 Task 的 verification 目录；
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
| AC1 | 冻结两命令名并声明对应 §5 行 158/159 形状 | 只读契约 | NOT_RUN | 无 |
| AC3 | 断言返回/错误不含路径；缺失译图为 null；`beginning` 不改 `saved_progress` | 构建产物 | NOT_RUN | 无 |
| AC4-① | allowlist 断言：生产面两命令存在 / probe+AC1 面无，probe=7 / AC1=6 不变 | 构建产物 | NOT_RUN | 无 |
| AC4-② | typed 拒绝路径测试（未知 chapter / 非法 mode / 未知 page 且无写副作用） | 构建产物 | NOT_RUN | 无 |
| AC4-③ | frozen 2.3 上两命令的域级错误往返 | 已重建 bundle（junction） | NOT_RUN | 无 |
| AC5 | `tests/core/**` + Rust 测试全绿 | 构建产物 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：P16/P16-C1（Reader wire 冻结，done）、UI-DESIGN-1（设计基线，done）、EVENTS-FWD-1（W20 事件已 done）。
- 风险一：`SaveReadingProgress` 是**写操作**（持久化进度）。测试必须只走"未知 `page_id`/非法 mode 的拒绝路径"，并在**隔离数据目录**中运行，不得污染主仓或用户数据。
- 风险二：`ReaderProjection` 是**较大 DTO**（pages 数组 + 布局 + 进度）。host 应**原样透传** Core 投影（它已是不含路径的只读投影），**不要**在 host 侧重解释坐标或裁剪 pages——除非契约要求。
- 风险三：不要把 W5（`resolve_page_resource`，已有）误当成本 Task 的一部分；本 Task **不**新增资源通道逻辑。
- 阻塞条件：若判定契约缺少产品命令名裁决且必须由用户/Codex 决定 → `BLOCKED` + 证据。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 6）：依据设计基线 §6 的 W18/W19 + Coordinator 只读复核（Core 已实现 / host 全变体 0 命中 / §7 G 清单未覆盖 / §6.3 DTO 无路径）。**释放前先核实缺口真实**。
- **BL-14 第三例登记**：与前两例同根因；已把"W 行 → `PRODUCTION_COMMANDS` 逐条映射"确立为释放任何 UI Task 前的标准步骤。
- Handoff：尚无。Review：尚无。实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1 | verification/READER-IPC-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放时同步。
