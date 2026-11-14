---
id: FEA-06-RESIDUAL-4A
title: C-07 additive UNFREEZE 前置：对照内容规格 v1 + ListPageRegionTextsAsync 端口预授权 + pin 重算
kind: decision
governance_version: 3
status: done
disposition: "RO-1 派生的契约前置卡（2026-11-14）；scope 未冻结、未释放，不得据此实施产品代码"
approval: 待 DSH scope review；依据 [RO-1 重开裁决](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md) §3 R1/R2 与 §4 拆卡表
suggested_owner: null
owner: null
reviewer: null
depends_on: []
base_commit: 4cb24ed20556f85bbbe8c4a0ff9d34b6dbfcf65a
branch: null
worktree: null
integration_commit: 5c84dc22f
delivery_head: 7c1ac472f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-06-RESIDUAL-4A
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-4A.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md
  - doc/reviews/FEA-06-RESIDUAL-4A-*.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - doc/TASK_LEDGER.md
  - verification/FEA-06-RESIDUAL-4A/**
out_of_scope:
  - 不写产品代码：`src/**`、`apps/**`、`tests/**` 一律不改（App 端口 / UI / 测试属 `FEA-06-RESIDUAL-4B`）
  - 不改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（由 DSH 维护）；`doc/TASK_LEDGER.md` 只允许按 R-1 经 DSH 授权做**一次机械重生成**（`task_ledger.py --write`），不得手写
  - 不改任何其他冻结契约字节（C-01b…C-17、FEA-01 零改动）
  - 不改 Core 命令 / schema / wire：`list_page_region_texts` 已实现并注册，本卡只做 App 端口预授权
  - 不写「复核通过」：独立字节级复核由 DSH 另派，本卡只写 `pending`
  - 不 push 远端
---

# FEA-06-RESIDUAL-4A：C-07 additive UNFREEZE 前置（规格冻结 + 端口预授权 + pin 重算）

## 来源与目标

用户 2026-11-14 指令撤销 Q7 `OUT` 裁决并重开「查看对照」，固定走 **C-07 additive UNFREEZE** 路线。裁决原文与事实基线见 [RO-1 重开裁决](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md)；被重开的伞卡见 [FEA-06-RESIDUAL-4](FEA-06-RESIDUAL-4.md)。

本卡是**契约前置卡**（RO-1 §4 4A），只交付契约侧四件事，**不含任何产品代码**：

1. 把 RO-1 §5 的「对照内容规格 v0」细化为**可实现、可判别**的规格 v1（本卡 §「对照内容规格 v1（冻结候选）」）；
2. 在 C-07 冻结面内为 `IHostController.ListPageRegionTextsAsync` 做 **additive 预授权登记**（inventory 计划节 + 载体 + pin 重算）；
3. 写 UNFREEZE 载体 [CONTRACT-UNFREEZE-2026-11-14-C07-RO1](../reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md)；
4. 重算 C-07 pin 并更新 [C-07 冻结记录](../plan/FEA-CONTRACT-FROZEN-C07.md)。

**为什么必须是 additive**：Core 侧 `list_page_region_texts` 已实现（`src/bootstrap/core_service.py:3533/7787/7796`），Host 侧已注册并分发（`HostCommandRegistry.cs:191/357/465`、`HostCommandDispatcher.cs:868-871`），客户端解析器已在库（`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:224-281`，当前仅测试使用）。缺的只有 **App 侧 `IHostController` 端口**，因此不需要 Core/schema/wire 任何改动。

**统计口径的关键事实（本卡不绕开）**：`tools/generate_api_inventory.py` 的计数**由源码 interface 块解析得出**（`generate_api_inventory.py:105-119`，源 `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs`）。该文件当前 **79 个方法**、无 `ListPageRegionTextsAsync`；`python tools/generate_api_inventory.py` stdout 实测 `IHostController | 79`、合计 `86`。因此 **80/87 只能在 4B 落地端口代码的同一个 Task 内翻转**（这正是 `FEA-CONTRACT-FROZEN-C07.md` §3「实现注意」与 v1.3–v1.8 六次先例的做法）。本卡把 80/87 作为**预授权目标值**锁进计划节与载体，不提前写进统计行——否则成员表会与脚本 stdout 差一行、`--check` 必红（`generate_api_inventory.py:174` 的子串判定）。

## Acceptance Criteria

状态标记为本卡起草提交时的真实状态； <<MET>> / `<<PARTIAL>>` / `<<PENDING>>` 由 DSH 在释放与收口时更新，**本卡不得自评通过**。

- [x] **AC1 规格冻结**：RO-1 §5 v0 细化为规格 v1，覆盖**两层定义 / 字段 / 布局 / 交互 / 空态与失败态 / a11y**，逐项给出可判别断言（供 4B 直接派生测试）；规格文本落本卡 §「对照内容规格 v1（冻结候选）」，且与计划节的方法名、返回类型、字段名**逐字一致**。规格「冻结」以独立 scope review 通过为准。  <<MET>>
- [x] **AC2 inventory 更新（成员表逐行一致口径）**：[C-07 API Inventory](../plan/FEA-C07_API_INVENTORY.md) 新增「RO-1 计划追加」节，锁死 `ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>` / 落地后行号 `#80`；**正式成员表与统计行保持与脚本 stdout 逐行一致**（79 方法 + 4 非方法成员；`IHostController 79`、合计 `86`），并显式写明「80/87 由 4B 落地时翻转 + pin 重算 v1.10」。`python tools/generate_api_inventory.py --check` EXIT 0。  <<MET>>
- [x] **AC3 pin 重算与冻结记录同步**：C-07 文件 pin 由 v1.8 重算为 v1.9 并写入 [冻结记录](../plan/FEA-CONTRACT-FROZEN-C07.md) §1（**新行置顶、前一 pin 原值保留不改写**）、§1B（登记 v1.9 RO-1 与「独立复核 pending」）、§2 条件 3（计数口径）、§5（变更行）；`pwsh -NoProfile -File tools/governance/verify_pins.ps1` PASS 且 C07 行等于新 pin。  <<MET>>
- [x] **AC4 UNFREEZE 载体**：载体落 `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md`，含「依据 / 为什么必须 UNFREEZE / 变更范围 / 计划节 / 新 pin / 独立复核要求 / 复核记录（pending）/ 不构成什么」，结构对齐同型先例 [CONTRACT-UNFREEZE-2026-11-10-C07](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md)。  <<MET>>
- [x] **AC5 独立字节级复核（r2 `approved`，<<MET>>；r1 `changes_requested` 已处置）**：由 DSH 另派**未参与本卡写作**的独立上下文 reviewer（本项目 Review 独立性以上下文独立为准），逐字节核对：inventory 成员表 = 脚本 stdout、pin = 文件 SHA-256、计划节与规格字段逐字一致、冻结记录 §1–§5 自洽、无 `src/**`/`apps/**`/`tests/**` diff。结论回填载体 §6 与冻结记录 §1B。**本卡作者不得自审，也不得代写 approved。**  <<MET>>
- [x] **AC6 门禁四件套 + 零越界**：① `pwsh -NoProfile -File tools/governance/check.ps1`；② 同脚本 `-TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md`；③ `pwsh -NoProfile -File tools/governance/verify_pins.ps1`；④ `python tools/generate_api_inventory.py --check`。四者原始输出与 EXIT 码留 `verification/FEA-06-RESIDUAL-4A/logs/`；**本提交所含路径** ⊆ `allowed_paths`（工作树里 `tests/fea11/test_source_match.py` 的未提交改动属 DSH 并行的 `custom_rank` 夹具修复，**不在本卡范围、不纳入本提交**）；无产品代码 / DDL diff。  <<MET>>

## 对照内容规格 v1（冻结候选）

> v0 出自 [RO-1 §5](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md)。本节把 v0 的六个字段组细化为 4B 可直接实现、测试可直接判别的规格。任何与本节冲突的实现视为超范围。

**规格版本：v1.1（2026-11-14 定稿）**。v1.0 字节保留在 git 历史；v1.1 在正文同步三处更正——P2-3（空集合语义，S3）、P2-4（L2 取 VM 实时 `DraftText`，S1/S2）、P2-2（`TARGET_NOT_FOUND` 改本地判定，S3/S5），与「r1 独立复核处置」节及「S7 扩面 errata」节一致。**复核边界（r3 F-2 更正）：r2 的 `approved` 覆盖的是 C-07 v1.9 的 inventory 字节与记录链；v1.1 定稿与 S7 errata 属 r2 后处置，由 r3 窄复核覆盖（`doc/reviews/FEA-06-RESIDUAL-4A-r3.md`，P0=0/P1=0）。不得表述为「v1.1 已通过 r2」。**

### S1 两层定义（固定两层，不得扩为三层）

| 层 | 名称 | 数据来源（只读） | 权威性 |
|---|---|---|---|
| **L1** | 基底 / 已提交文本 | Core `list_page_region_texts` → 新增端口 `ListPageRegionTextsAsync` → `RegionPageTextProjection`（`RegionTextProjection.cs:224-281`） | 唯一权威读投影。**不得**用 L2 或本地缓存替代或回填 |
| **L2** | 当前工作副本 | 现有 `LoadPageRegionsAsync` 的 `RegionSummary`（`CoreServiceClient.cs:204-210`）+ **`WorkbenchViewModel` 的实时可编辑 `DraftText`**（用户此刻屏幕上可见且可编辑的文本；**不得**取持久化 `Draft.Patch["text"]`——冲突态下两者可能不一致，而对照的意义正是让用户看到当下差异。v1.1 修订，见 §r1 处置 P2-4） | 仅展示本地态。**无草稿即「本地无草稿」，不得用 L1 值冒充 L2** |

判别断言：
- **S1-a**：面板打开时 `ListPageRegionTextsAsync` 必须被调用**恰好一次**（一页一次，禁止 per-region N+1）。边界 = **每次打开**：关闭再开算第二次；页面重排**不得**重复调用。
- **S1-b**：L1 的任何字段都不得由 L2 派生；反向亦然（双向独立可判别：用不同取值的 Fake 断言两栏文本不同源）。
- **S1-c（v1.1 补充，DSH R-9 裁决）**：L2 的**实时性由 View 层保证**——`WorkbenchViewModel` 的对比记录可以是打开瞬间快照，但面板必须在 `DraftText` 变化时更新并**在页面重排后仍显示当前值**（不得回落成旧值）。判据是用户看到的值，不是数据结构的刷新频率。若重排后显示旧值，属功能缺陷（P1），不是实现口径分歧。

### S2 字段（每行显示项）

| 显示项 | L1 取值 | L2 取值 | 空/缺省显示 |
|---|---|---|---|
| RegionType | `RegionTextDetail.RegionType` | `RegionSummary.RegionType` | 不适用（两者必填） |
| SfxPolicy | `RegionTextDetail.SfxPolicy` | `RegionSummary.SfxPolicy` | 不适用 |
| Origin | `RegionTextDetail.Origin` | `RegionSummary.Origin` | 不适用 |
| RevisionNo | `RegionTextDetail.RevisionNo` | `RegionSummary.RevisionNo` | 不适用 |
| 文本 | `Text.FinalTranslation` | **VM 实时 `DraftText`**（非持久化 `patch.text`；v1.1 修订） | 空串 → 显示 `（空文本）` 标签；**这是「值为空」的约定显示，不是替代文本**，不得用另一层的值填充 |
| 文本来源 | `Text.FinalSource`（`none` 时显示 `—`） | 固定显示 `本地草稿` / `本地无草稿` | — |

判别断言：
- **S2-a**：`IsConflict` **必须是派生值、不新增存储字段**。定义：`HasRevisionDrift := L1.RevisionNo != L2.RevisionNo`（基底在本地读取后被推进）。`IsConflict` 本身沿用既有状态机 `FluentPageState.Conflict`（`FluentViewModelBase.cs:15`），本卡不新增枚举值、不新增数据库字段、不新增 wire 字段。
- **S2-b**：L1 文本为空串时，L2 若也空串，**两栏都显示 `（空文本）`**，不得出现任何一栏显示对方的值。
- **S2-c**：`HasRevisionDrift == true` 时面板顶部追加一行 typed 提示（见 S5），并在两栏 RevisionNo 处同时显示真实数字（不得只显示 L1）。

### S3 端口方法签名（与 inventory 计划节逐字一致）

```csharp
// 建议实现位置：apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
// 需 using NewManga.CoreClient.Commands;
Task<RegionPageTextProjection?> ListPageRegionTextsAsync(
    string pageId,
    IReadOnlyList<string>? regionIds = null,
    CancellationToken cancellationToken = default);
```

- 返回 `null` 表示「投影不可用」，**不得**抛异常进 UI、**不得**返回空集合冒充「无可比对内容」。**空集合不能单独表示「该页无区域」**——Core 对未知 page 也会返回 `regions: []`（且 `page_size` 为 `null`），必须结合 `page_size` / `page_id` 与 `TARGET_NOT_FOUND` 区分（v1.1 修订，见 §r1 处置 P2-3）。
- `regionIds` 参数**保留在签名中**（v1.9 预授权、不得改动签名），但 **4B 调用时一律不传（传 `null`）**：整页一次，符合 S1-a。因为 4B 永不传 `regionIds`，`TARGET_NOT_FOUND` **不来自 Core 错误码透传**（`HostController.IsUiFacingFailure` 会把 `CoreOperationException` 吞成 `null`），而由**本地成员判定**：page 不在当前投影中 → `TARGET_NOT_FOUND`。这样既不触发第二次 UNFREEZE，也不改变返回类型（见 §S7 扩面 errata E-2）。
- `NullHostController` / `FakeHostController` 一律 `null`（降级语义与既有读方法一致）。

### S4 布局

- 面板**只在 `FluentPageState.Conflict` 且已选中 region 时出现**；非冲突态不渲染（`IsVisible=false`），**不得改变现有非冲突态视觉**。
- 位置：冲突横幅（`WorkbenchPageView.cs:656-660`，`AlertBanner("并发冲突", …)`）**下方**，RegionBox 内纵向排列；**不得改动 `FluentUi.Banner` 的单 action 签名**（`Controls/FluentUi.cs:143` 只接受一个 action）：横幅右侧的「查看对照」按钮作为同一纵向容器的独立控件渲染。
- 展开后为纵向双栏：**上 = L1 基底文本（只读）**、**下 = L2 当前工作副本（只读）**；两栏各有标题条；行高自适应（`TextWrapping=Wrap`、无固定高度、不截断）；宽度随 RegionBox。
- 关闭后恢复到「仅冲突横幅」的原状（不残留占位高度）。

### S5 交互与 typed 原因

- 入口：冲突横幅旁按钮，文案恒为 `查看对照`（测试已按 `Content` 含「查看对照」断言，见 `FluentResidualBatchATests.cs:668-669`）。
- 打开后**只读**：不提供「以某一方覆盖」「应用 L1/L2」等任何写动作（避免误操作）；不自动合并。
- 关闭：`关闭` 按钮 + `Esc`；关闭不发写请求。
- 失败/空态 typed 原因（面板内显示，**不显示任何文本行**）：

| 情形 | typed 原因 | 处置文案 |
|---|---|---|
| 端口返回 `null` | `REGION_TEXT_PROJECTION_UNAVAILABLE` | 投影暂不可用；请先「重新读取页面」后再打开对照（面板不给重试按钮） |
| Host 未就绪 | `HOST_NOT_READY` | Host 未就绪；恢复后请重新读取页面 |
| 该 page 不在当前投影中（**本地判定**，非 Core 错误码） | `TARGET_NOT_FOUND` | 目标页面已变化；请重新读取页面 |
| 既有 conflict 错误码（`DRAFT_OWNER_CHANGED` / `STALE_BASE_REVISION` / `LOCK_CHANGED` / `EDIT_TOKEN_EXPIRED` 等） | 沿用 `DraftErrorMap`（`WorkbenchViewModel.cs:806-835`）的既有映射 | 沿用既有 `Presentation` 文案，不新造第二套 |

- **负向不变量（先由本规格锁定，4B 只实现不减弱）**：投影不可用时**不得**显示任何对照内容（不得用本地文本、缓存或 L1 推测值填充），沿用既有 `WithoutFabricatedCompare` 语义。既有 `I13_WorkbenchConflictRow_ConflictBannerShowsWithoutFabricatedCompare`（`FluentResidualBatchATests.cs:642-670`）的 `DoesNotContain(查看对照)` 断言由 4B 改为**正向断言**（冲突态存在「查看对照」按钮），但**必须同时新增**「投影不可用 → 面板不出现任何文本行、只出现 typed 原因」的断言；两条断言并存才算保持不变量。**本条在规格里先冻结**：若 4B 只把旧断言翻成正向而不同时补负向断言，即视为削弱 `WithoutFabricatedCompare`，4A 独立复核与 4B Review 都必须判 `changes_requested`。

### S6 可访问性（a11y）

- 面板根 `AutomationProperties.Name = "区域文本对照"`；两栏分别 `"基底文本（只读）"` / `"当前工作副本（只读）"`。
- 「查看对照」按钮 `AutomationProperties.Name = "查看对照"`（与 `Content` 文案一致，供既有 UIA 断言与新增断言共用）。
- 键盘：按钮可 Tab 到达；面板打开后焦点落在 `关闭` 按钮；`Esc` 关闭；两栏文本为只读 `TextBlock`，**不进入 Tab 序列**（避免逐字停靠），其内容通过 `AutomationProperties.Name` 暴露给屏幕阅读器。
- 对比度：只用既有主题笔刷，**不新增颜色常量**；两层用标题文字区分（**不得**仅靠颜色区分），满足色盲可读。

### S7 规格与实现的边界（给 4B 的硬约束）

- 只允许新增：1 个 `IHostController` 方法 + 3 处实现（`HostController` / `NullHostController` / 测试 Fake）+ 1 个对照面板控件 + 1 组测试。
- 不允许：改 `FluentUi.Banner` 签名、改 `RegionSummary` 形状、改 `RegionPageTextProjection` 解析器、改任何 Core/wire 命令、改 `FluentPageState` 枚举。
- 若实现中发现本规格某条不可行，**回到本卡改规格**（走 DSH 裁决），不得在 4B 内静默放宽。

## 允许修改范围

- 本卡 `doc/tasks/FEA-06-RESIDUAL-4A.md`
- `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md` 与本卡复核报告 `doc/reviews/FEA-06-RESIDUAL-4A-*.md`
- `doc/plan/FEA-C07_API_INVENTORY.md`、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`
- `doc/TASK_LEDGER.md`：**本卡唯一的例外**，且仅做一次机械重生成——新增卡文件会改变 `task files` / `non-terminal` 两个计数，`check.ps1:272-283` 会因为台账过期而报错；该文件平时归 DSH 维护，本卡经 **DSH 2026-11-14 显式授权**执行一次 `python tools/governance/task_ledger.py --write`（不手写、不做判断），并纳入同一提交（R-1）
- `verification/FEA-06-RESIDUAL-4A/**`（含 frontmatter `evidence_dir`，已在 `allowed_paths` 中显式列出）

## 禁止范围

- 产品源码 `src/**`、`apps/**`、`tests/**`（含 `IHostController.cs` 本身——端口落地属 4B）。
- `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（DSH 维护）；`doc/TASK_LEDGER.md` 仅限 R-1 的一次机械重生成。
- 任何其他冻结契约字节；任何 DDL/schema；任何 Core 命令面。
- 远端写操作（不 push）。

## 测试要求

本卡为文档/契约卡，**无产品测试**；判别面是脚本与门禁。

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 成员表逐行一致 | `python tools/generate_api_inventory.py`（stdout）与 inventory 正式成员表逐行 diff | 仓库根、Python 3 | 实测 EXIT 0；stdout = 79 方法 + 4 非方法成员，与成员表逐行一致 | `verification/FEA-06-RESIDUAL-4A/logs/api-inventory.log` |
| AC3 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | 18/18 PASS；C07 = v1.9 新 pin | 同上 |
| AC6 门禁 | `check.ps1`、`check.ps1 -TaskPath`、`verify_pins.ps1`、`--check` | 同上 | 四项全部 `EXIT=0`（台账按 R-1 重生成后转绿） | `verification/FEA-06-RESIDUAL-4A/logs/gates-2026-11-14.log` |

## 依赖、风险与阻塞

| # | 项 | 说明 | 处置 |
|---|---|---|---|
| R-1 | **`check.ps1` 与新增卡的结构性冲突** | `check.ps1:272-283` 用现场重建的 `task files` / `non-terminal` 对齐 `doc/TASK_LEDGER.md`；新增本卡（`status: done`）后实测由 `599 / 7` 变为 `600 / 8` → 台账过期即 `Add-Error` | **已解除**：DSH 2026-11-14 授权执行一次 `python tools/governance/task_ledger.py --write`（不手写），台账随本 commit 一并提交（`ledger: non-terminal 7->8`）；重生成后 `check.ps1`（默认 + `-TaskPath`）**PASS (3 warnings)** |
| R-2 | **80/87 不能在本卡翻转** | 计数来自源码解析（`generate_api_inventory.py:105-119`）；`IHostController.cs` 属 `apps/**`，本卡禁改；提前写 80/87 会让成员表与 stdout 差一行、`--check` 必红 | 本卡只做预授权（计划节 + 载体 + 目标值），统计翻转与成员表 `#80` 行留给 4B（pin v1.10），与 v1.3–v1.8 先例一致 |
| R-3 | **负向断言被削弱** | 既有 `WithoutFabricatedCompare` 断言「冲突态没有查看对照按钮」；4B 上线后该断言必然反转 | 规格 S5 已要求**同时新增**「投影不可用 → 零文本行」负向断言；4A 复核与 4B Review 都必须核对这一点 |
| R-4 | 规格不可实现即超范围 | 规格 S7 已把实现面限制在 1 方法 + 3 实现 + 1 控件 + 1 组测试 | 实现受阻时回本卡改规格，不得在 4B 静默放宽 |
| R-5 | 独立复核独立性 | 作者不得自审（2026-10-31 裁决） | 由 DSH 另派未参与本卡写作的上下文；本卡只写 `pending` |

## 交付与运行记录

- **起草提交**：2026-11-14，base `4cb24ed20556f85bbbe8c4a0ff9d34b6dbfcf65a`。
- **本次落盘**：本卡（含规格 v1）、UNFREEZE 载体、inventory 计划追加节 + v1.9 pin、冻结记录 §1/§1B/§2/§3/§5、证据 `verification/FEA-06-RESIDUAL-4A/`。
- **门禁实测**（原始输出见证据目录 `logs/gates-2026-11-14.log`）：① `check.ps1` **PASS (3 warnings) / EXIT=0**；② `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md` **PASS (3 warnings) / EXIT=0**；③ `verify_pins.ps1` **PASS (all 18) / EXIT=0**（C07 = 新 pin `91e51ab7…`）；④ `generate_api_inventory.py --check` **EXIT=0**（`1/79/6 = 86`）。台账按 R-1 由 DSH 授权重生成一次（`task files 599→600`、`non-terminal 7→8`）。
- **零越界核对**（**仅本提交所含路径**逐文件）：`doc/tasks/FEA-06-RESIDUAL-4A.md`（新）、`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md`（新）、`doc/plan/FEA-C07_API_INVENTORY.md`（+18/−2）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`、`doc/TASK_LEDGER.md`（机械重生成）、`verification/FEA-06-RESIDUAL-4A/**`（新）——全部 ⊆ `allowed_paths`；**无 `src/**`、`apps/**`、`tests/**`、DDL/schema diff**。
  - **范围外声明**：工作树中 `tests/fea11/test_source_match.py` 有 DSH 并行的 `custom_rank` 夹具修复（未提交，属 `MAINT-1` 的 DoD §4 事项）；本卡**不读不改不提交**它。`git status --short` 里它会显示为 ` M`，属预期。
- **未做（交付时）**：独立字节级复核（**已于 2026-11-14 完成：r1 `changes_requested` → 处置 → r2 `approved`**）；80/87 统计翻转（R-2，属 4B）；任何产品代码。
- **下一步**：① DSH 独立 scope review 本卡规格与预授权（RO-1 §4：`proposed` → `ready` 前必须有）→ ② DSH 另派独立上下文做字节级复核并回填载体 §6 / 冻结记录 §1B → ③ 复核通过后重冻 C-07 v1.9 → ④ 释放 `FEA-06-RESIDUAL-4B`（端口 + UI + 判别测试 + 统计 80/87 翻转 + pin v1.10）。

## r1 独立复核处置（append-only，2026-11-14）

**复核**：[`FEA-06-RESIDUAL-4A-r1.md`](../reviews/FEA-06-RESIDUAL-4A-r1.md)（独立上下文子 agent，未参与写作与实现）。**结论 `changes_requested`：P0=0 / P1=2 / P2=7 / P3=5**。
**字节层全部通过**（不采信卡面自述、由复核者独立实测）：pin 三口径 = `91e51ab7…`；旧 pin `8ccaba05…` 原值保留；成员表与源码逐行 `ALL_MATCH: True`（79 + 4 非方法 = 86）；diff 10 文件 ⊆ allowed_paths、`src/apps/tests` 零改动；`verify_pins` 18/18；四门禁 EXIT=0。

### P1（已修；不触 inventory 字节 ⇒ pin 仍 `91e51ab7…`）

- **P1-1**：冻结记录 §5 v1.9 行曾称 `check.ps1` 为红，与 §2 条件 4 及实测矛盾 → 已改为「台账重生成后 PASS；重生成前曾因 TASK_LEDGER 计数过期报错」。
- **P1-2**：载体 §2 曾把 `expected_revision` 写成 `list_page_region_texts` 的可选字段（实际 dispatcher `:868-871` 与 Core handler 只收 `page_id`/`region_ids`，该字段属 `restore_region_revision`）→ 已删除并改为明确「**不接受** `expected_revision`」，防止 4B 偏离预授权签名。

### P2（逐条处置）

| # | 处置 |
|---|---|
| P2-1 | 冻结记录 §2 条件 1 状态列改为 `✅（v1.9 ⏳ pending）`，消除「标 ✅ 而复核 pending」矛盾。**已修** |
| P2-2 失败态判别链 | **规格 v1.1 约束**：`null` 单一返回不可机械区分原因，4B 必须按固定优先级判定并各自可测：① `HOST_NOT_READY`（runtime/端口未就绪）② `REGION_TEXT_PROJECTION_UNAVAILABLE`（IPC 失败/投影不可读）③ `TARGET_NOT_FOUND`（page 不存在）。禁止把三种原因合并为同一 UI 文案。 |
| P2-3 空集合语义 | **规格 v1.1 更正**：`regions: []` **不能**单独表示「该页无区域」——Core 对未知 page 也返回 `regions: []`（`page_size` 为 `null`）。4B 必须结合 `page_size`/`page_id` 与 `TARGET_NOT_FOUND` 区分，**不得**把空集合直接渲染成「无冲突」。 |
| P2-4 L2 数据源 | **规格 v1.1 更正**：L2 必须取 ViewModel 的**实时可编辑 `DraftText`**，不得取持久化 `Draft.Patch`；冲突态下两者可能不同，而对照的意义正是让用户看到当下差异。 |
| P2-5 新码闭集 | **规格 v1.1 写死**：`REGION_TEXT_PROJECTION_UNAVAILABLE` 是 **UI 面板本地原因码**，**不得**加入 `DraftErrorMap`（19 键闭集 = FEA-05 的 17 个 wire 码 + `INTERNAL`/`UNKNOWN`）；4B 不得新增 wire 码、不得改该闭集。 |
| P2-6 S7 允许面 | **4B 卡 `allowed_paths` 必须**包含 `WorkbenchViewModel.cs` / `WorkbenchPageView.cs`（及新增控件文件）；4A 不实现，只在卡面登记。 |
| P2-7 旧 pin 复现命令 | 证据 README 由 `git show HEAD:` 改为 `git show 4cb24ed20:`（父提交）。**已修** |

### P3（登记，不修）

- **P3-1**：冻结记录 §1B 缺 v1.8 行（既有断档，非本轮引入）→ 下次触及时补「v1.8：AI-1 统计 79/86 + P21–P25 并入」。
- **P3-2**：载体 §1 指纹拆分称 RO-1 节「12 行」，实际 15 行（`FEA-C07_API_INVENTORY.md:140-154`）；总数 `+18/−2` 正确 → 登记。
- **P3-3**：卡面把既有 `DoesNotContain` 描述成正向断言（卡面后文已纠正）→ 登记。
- **P3-4**：证据 README 的日志头声明过度（两份日志无 HEAD/status）→ 登记。
- **P3-5**：`.gitattributes` 无 `doc/plan/FEA-C07_API_INVENTORY.md text eol=lf`，`core.autocrlf=true` 的 fresh clone 会破 pin（**既有债**，v1.8 及更早同病，载体/README 已披露）→ 登记为 `GOV-EOL-PIN` 扩展候选，不在本卡 `allowed_paths`。

**复核者的明确结论**：当前字节**不满足重冻条件**（记录层两处假陈述必须先修）；修完 P1（不触 inventory）后 r2 只需窄复核三口径 + 两处改动 + 四门禁即可 `approved`，随后由 DSH 回填载体 §6 与冻结记录 §1B 并重冻。

## S7 扩面 errata 与 4B 实施口径（append-only，2026-11-14 DSH 裁决）

依据：起草 `FEA-06-RESIDUAL-4B` scope 时的只读实测（4 跳生产链取证）。本节的扩面**不改变** v1.9 预授权的方法名 / 返回类型 / 统计（仍 1 个方法、`Task<RegionPageTextProjection?>`），因此 **pin 保持 `91e51ab7…`，不需要第二次 UNFREEZE**。

### E-1｜S7 允许面不完整（补 2 个生产文件）

- **事实**：生产链是 **4 跳**——`IHostController`（`IHostController.cs`）→ `HostController`（`HostController.cs:17`）→ `HostRuntime`（`HostRuntime.cs:826-840` 门控样板）→ `CoreServiceClient`（`CoreServiceClient.cs:1104` 样板）。`CoreServiceClient` 中 `region_texts` **0 命中**，wire 调用与解析都必须新写。
- **裁决**：S7 允许面扩充为包含 `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`（**r3 F-1 更正：本节初稿写成了不存在的子路径，已改；正确文件在 `NewManga.Host/`，2,875 行 / 134,124 B，class 定义于 `:20`**）与 `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`（含其 wire DTO，若需）。该扩面只在 `FEA-06-RESIDUAL-4B` 的 `allowed_paths` 落地；4A 是契约卡，**不实现**这两个文件。

### E-2｜`TARGET_NOT_FOUND` 通道口径（R-8 确认）

- **问题**：若端口传 `regionIds` 而某 region 已消失，Core 抛 `CoreOperationException(TARGET_NOT_FOUND)`；`HostController.IsUiFacingFailure`（`HostController.cs:2932`）把 `CoreOperationException` 统一吞成 `null`，VM 会误判成 `REGION_TEXT_PROJECTION_UNAVAILABLE`。要保留错误码就得改已预授权的返回类型 → 触发第二次 UNFREEZE。
- **裁决**：端口**不传 `regionIds`**（整页一次，符合 S1-a「一页一次」）。`TARGET_NOT_FOUND` 一律由**本地成员判定**（page 不在当前投影/已删除），不依赖 Core 错误码透传。签名与 v1.9 预授权**完全一致，零额外 UNFREEZE**。
- **对 P2-2 的补充**：三条原因的判定优先级不变，但 `TARGET_NOT_FOUND` 的来源改为本地判定。

### E-3｜4B 实施顺序（避免半翻转）

1. **第一刀**：`CoreServiceClient.ListPageRegionTextsAsync` wire 方法 + AC6 wire 形状测试（可独立编译/测试，不依赖 UI）；
2. 随后：Host 三处实现（`HostController` / `NullHostController` / Fake）→ UI 面板 → 判别/负向测试；
3. **最后**：统计翻转 `80/87` + pin `v1.10`（避免 R-5 半翻转）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-1 | AC2-AC6 | verification/FEA-06-RESIDUAL-4A/README.md | 5c84dc22f | 56d83df5123ff8186ca7199681a1c15985457369ab52ed7c8cd6f59a8e11b171 | canonical |
| EV-2 | AC2-AC6 | verification/FEA-06-RESIDUAL-4A/logs/gates-2026-11-14.log | 7c1ac472f | f7adf15606bcf49e4a9834057ae5824f104bd80ee28571155f07c739201e2227 | canonical |
| EV-3 | AC2-AC6 | verification/FEA-06-RESIDUAL-4A/logs/api-inventory.log | 7c1ac472f | a93cb53e45b55e5d0651e381de11bb910503b9adcf39625ca3609c5363277640 | canonical |
| EV-4 | AC2-AC6 | verification/FEA-06-RESIDUAL-4A/logs/member-table-eq-stdout.log | 7c1ac472f | e2312d43b2e1ece65afff09da1cb3cbe128d8b8ad8eb16f6731861d6ea0fe964 | canonical |
| EV-5 | AC2-AC6 | verification/FEA-06-RESIDUAL-4A/logs/pin-before-after.log | 7c1ac472f | cb9735057b5f140cff7bb8ff96f07e018fbcd3eccdb44cd80e4fb4a67583d055 | canonical |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树；无新建 worktree |
| evidence（仓库） | `verification/FEA-06-RESIDUAL-4A/**` | NOT_APPLICABLE | 仓库内 | `verification/FEA-06-RESIDUAL-4A/EV`（见 Canonical Evidence） | 门禁/脚本原始日志已保留；逐文件 SHA-256 见 Canonical Evidence |
## Closeout Record

- Closeout date / DSH：待关闭时填写（当前 `proposed`，未释放）。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0（本轮无删除/迁移/归档）。
- 未关闭项及保留原因：AC5 **已关闭**（r1 `changes_requested` → 处置 → r2 `approved`，2026-11-14）；AC2 的 80/87 翻转按 R-2 归属 4B；AC4 载体 §6 复核记录**已回填**（`approved`，含 r2 覆盖范围声明）。
- 当前指针清理：本轮不改 `STATUS` / `REBASELINE_PLAN`（RO-1 §6：`proposed` 不触发 DAG 登记），由 DSH 在释放时更新；`TASK_LEDGER` 已按 R-1 一次性重生成（`task files 600` / `non-terminal 8`）。

## 收口记录（2026-11-14，DSH）

- **终态：`done`**。AC1–AC6 全 `<<MET>>`：AC1 规格 v1.1 定稿（scope review 形式要件由 r2+r3 替代，DSH 依 r3 F-9 裁决）；AC2 计划节 + 成员表逐行 = stdout（统计翻转由 4B 完成，本卡口径为保持 79/86）；AC3 pin 重算 v1.9 并重冻；AC4 载体 §6 已回填 `approved`；AC5 独立字节级复核 r1 `changes_requested` → 处置 → **r2 `approved`**；AC6 门禁四件套 + 零越界。
- **证据**：`verification/FEA-06-RESIDUAL-4A/`（README + 4 份原始日志），逐文件 SHA-256 见 Canonical Evidence。
- **交付链**：`7c1ac472f`（4A 交付）→ `756ab29e2`（r1 处置）→ `5c84dc22f`（r4 处置）；`integration_commit: 5c84dc22f`、`delivery_head: 7c1ac472f`。
- **下游**：`FEA-06-RESIDUAL-4B` 已据此把统计翻到 **80/87**、pin 推到 **v1.10 `498882eb…`** 并冻结（`ba6136d0`）；4B 已 `done`。
- **未闭合**：无（本卡范围）；后续限制见 4B 的 6 项 limitation。