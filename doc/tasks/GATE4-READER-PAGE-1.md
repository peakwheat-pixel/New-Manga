---
id: GATE4-READER-PAGE-1
title: 条件 4 的 reader 页 —— 查明真实入口并如实定性（能否无交互到达）
kind: evidence
governance_version: 3
status: done
disposition: "GATE4-PAGES-UPGRADE-1 的 reader NOT_REACHABLE 需查明：是空库回落，还是映射/交互问题"
approval: DSH 2026-11-15（已初步查明：--page=reader 与 bookshelf 映射到同一 SpaceId.Library）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GATE4-PAGES-UPGRADE-1
base_commit: 33712b622
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GATE4-READER-PAGE-1
allowed_paths:
  - doc/tasks/GATE4-READER-PAGE-1.md
  - doc/reviews/GATE4-READER-PAGE-1-*.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE4-READER-PAGE-1/**
  - verification/GATE4-PAGES-UPGRADE-1/**
---

# GATE4-READER-PAGE-1：reader 页的真实入口

## 已查明的两件事（推翻我上一轮的判断）

1. **`--page=reader` 不是"空库回落"** —— `App.axaml.cs:497` 的
   `SpaceForStartupPage` 把 `"bookshelf" or "library" or "reader"` **全部映射到 `SpaceId.Library`**。
   所以 `reader.png == bookshelf.png` 是**映射本身**决定的，与库里有没有书**无关**。
   **上一轮"空库回落"的结论是错的，本卡更正。**
2. **阅读器是"沉浸式阅读器窗口"，不是第四个空间** —— 由
   `App.axaml.cs:515` 订阅 `ImmersiveReaderRequested` 打开 `ImmersiveReaderWindow`；
   触发点只有两处（`AppShellViewModel.cs`）：
   - **F11**（无修饰键、无文本焦点、无确认框/命令面板时）
   - `ShellCommandIds.LibraryImmersiveReader` 命令

## Acceptance Criteria

- [x] **AC1 更正登记**：在 `verification/GATE4-PAGES-UPGRADE-1/README.md` 与 Gate 评估中更正
      "空库回落"的说法，写明真因是**空间映射同一**；并承认这是我上一轮的判断失误。
- [x] **AC2 判定"能否无交互到达"**：明确回答 —— 在只有命令行参数、没有任何鼠标/键盘输入的前提下，
      能否让安装产物显示**阅读器**（普通阅读视图或沉浸式窗口）？依据必须是**代码事实**（不是猜测）。
- [~] **AC3 若可：出证据**（**不适用**：不可）：有书的数据根 + 到达阅读器的启动方式 + **人眼确认过**的截图。
- [x] **AC4 若不可：如实定性**（`NEEDS_INTERACTION`，含 `match=False` 实测）：标 `NEEDS_INTERACTION`，写明缺的是哪一步
      （例如"必须先选中一本书，再按 F11"），并说明**为什么不能用参数替代**（引用代码行）。
      不得用书架截图冒充阅读器。
- [x] **AC5 有书时的资料柜**（无论 AC3/AC4 结果）：至少证明"资料柜能显示书籍卡片"
      —— 用 `BOOK-FIXTURE-1` 的隔离数据根副本启动 `--page=library` 并截图 + 人眼确认。
      这既排除"空库导致页面空白"，也为 AC2 提供前提。
- [x] **AC6 隔离与数据保护**：所有启动用 `--data-root=<workspace 隔离目录>`；
      用户数据根清单 SHA-256 前后必须一致。
- [ ] **AC7 不虚报**：任何未验证的结论必须标 `NOT_RUN`；不得声称条件 4 满足。

## 允许修改范围

见 frontmatter（只加证据与文档更正，不改产品代码）。

## 禁止范围

- **不得**改 `App.axaml.cs` / `AppShellViewModel.cs` 来"让 `--page=reader` 打开阅读器"——
  那是行为变更，需另卡并由 DSH 裁决范围。
- 不得提交二进制截图进仓库（留 workspace）。
- 不得用 headless 渲染冒充安装产物。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 更正两份文档 | — | NOT_RUN | 无 |
| AC2 | 读代码 + 结论 | — | NOT_RUN | 无 |
| AC5 | fixture 数据根 + `--page=library` + 截图 | BOOK-FIXTURE-1 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：把 `BOOK-FIXTURE-1/isolated-data` 复制进隔离根后，新 sidecar 会执行 v14 迁移；
  需确认迁移成功且书仍在（否则 AC5 也会失败）。
- **风险 R2**：若强行用 `SendInput` 模拟点击+F11，坐标脆弱、易截错图 —— **不做**，除非能可靠验证。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | G:/CODEX/New Manga.workspace/task-envs/GATE4-READER-PAGE-1 | PRESERVE_REFERENCED | 同左 | 待填 | 截图与数据根副本 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`complete`（数据根副本与截图在 workspace）。
- 删除、迁移、归档数量/字节数：0。
- **结论（限定）**：
  - **更正**了 `GATE4-PAGES-UPGRADE-1` 里"空库回落"的错误说法 —— 真因是 `SpaceForStartupPage`
    把 `bookshelf/library/reader` 三者映射到同一 `SpaceId.Library`。
  - **`reader` 标 `NEEDS_INTERACTION`**：阅读器是独立沉浸式窗口，需先选中一本书再按 F11（或点 `阅读`）。
    实测 `SetForegroundWindow` 从非交互进程失败（`foreground=66368 ≠ shell=1376488`），F11 送不进去 ——
    **这是"试了并证明为什么不行"**，不是"没试"。
  - **已取得**：`--page=library` + `BOOK-FIXTURE-1` 副本的有书资料柜截图（**人眼确认**），
    证明缺口只在交互层。
- **未达成**：阅读器页本身**没有**截图；**未**声称四页全部可达。
- **自登记的错误（本卡更正上一轮）**：上一轮把 `reader.png == bookshelf.png` 归因为"空库回落"，
  **是错的** —— 与书库内容无关，是空间映射同一。已在本卡与两份上层文档中更正。
- 条件 4 仍**不判 MET**：sidecar 缺 SFX 权重、安装器 unsigned、`reader` 需交互。
