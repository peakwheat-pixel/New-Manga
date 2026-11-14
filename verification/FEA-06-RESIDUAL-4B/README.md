# FEA-06-RESIDUAL-4B 证据索引（RegionBox「查看对照」实现）

- Task：`FEA-06-RESIDUAL-4B`（`in_progress` → 收口）
- base：`9d0186a3d`（4B-3 复核 base）/ 首刀 base `f3ca74a10`
- 日期：2026-11-14
- 授权：[RO-1 重开裁决](../../doc/reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md)；规格依据 [`FEA-06-RESIDUAL-4A`](../tasks/FEA-06-RESIDUAL-4A.md) 的「对照内容规格 v1.1」（S1–S7 + S1-c）与 S7 扩面 errata（E-1/E-2/E-3）
- 独立复核：[`FEA-06-RESIDUAL-4B-r1.md`](../../doc/reviews/FEA-06-RESIDUAL-4B-r1.md)（`approved`，P0=0 / P1=0 / P2=3 / P3=6；被审 head `42123ae67`）

## 切片与提交

| 切片 | commit | 内容 | 结果 |
|---|---|---|---|
| 4B-1 wire | `eae0eb67a` | `CoreServiceClient.ListPageRegionTextsAsync` + payload writer + AC6 判别 5 例 | CoreClient **176 / 0 / 24** |
| 4B-2 端口 | `fd4008ce3` | `IHostController` + `HostController` + `NewManga.Host/HostRuntime.cs` + Null/Fake + 8 例端口契约测试 | App.Tests **897 / 0 / 11**、Host **321 / 0 / 74**、build 0/0 |
| 4B-2b 统计 | `ba6136d0` | 成员表 **#80 纯 append**、统计 **80/87**、pin **v1.10**、载体 | `--check` EXIT 0、pins 18/18 |
| 4B-3 UI | `42123ae67` | `RegionTextComparePanel`（新）+ `WorkbenchViewModel` 对照状态 + `WorkbenchPageView` 容器 + I13 正向/负向并存 + 13 例 | App.Tests **910 / 0 / 11** |

**中间态（已闭合，如实登记）**：`fd4008ce3` 自身 `--check` EXIT=1（源码 80 vs 文档 79），已由 `ba6136d0` 原子闭合；经独立复核用 blob 复算确认**红窗恰好只有该一个 commit**。当前基线全绿。

## pin 演进（C-07）

| 版本 | pin | 说明 |
|---|---|---|
| v1.9 | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` | RO-1 预授权（统计仍 79/86） |
| **v1.10** | `498882eb17507b89db463eb7cc8eb4522af80783a92ba21f80a5229c6d66984f` | 本卡落地（统计 **80/87**，成员表 #80 纯 append） |

v1.10 独立复核：`approved`（P0/P1/P2=0；`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-4B-r1.md`）。

## AC 结论

| AC | 判别 | 结论 | 依据 |
|---|---|---|---|
| AC1 端口实现 | `IHostController` + Host/Null/Fake 四处，降级一律 `null` | **MET** | `IHostController.cs:557`、`HostController.cs:1005`、`HostRuntime.cs:848`、`NullHostController.cs:181`、`FakeHostController.cs:1208`（方法起；`:1215` 为返回行）；8 例端口契约测试 |
| AC2 统计翻转 | #80 + 80/87 + `--check` 0 + pin v1.10 且 v1.9 保留 | **MET** | `ba6136d0`；独立复核 pin 三口径 = `498882eb…` |
| AC3 UI | 冲突态双栏、只读、L2 实时、恰好一次 | **MET（结构性）** | `RegionTextComparePanel.cs`（206 行）；`WorkbenchViewModel.cs:763-866`；`WorkbenchPageView.cs:695-716` |
| AC4 空态/失败态 | 三条原因固定优先级；`[]`+`page_size:null` 不得渲染成「无冲突」 | **MET** | `WorkbenchViewModel.cs:790/803/823`（①②③）+ `:816` 空态 |
| AC5 负向不变量 | 正向 + 负向**并存**；19 键未扩 | **MET** | `FluentResidualBatchATests.cs:671-687`（两条并存）；`RegionTextComparePanelTests.cs:270-316`（19 键 + 强负向） |
| AC6 wire 形状 | 仅 `page_id` + 可选 `region_ids`，无 `expected_revision` | **MET** | `RegionWriteCommandTests.cs:588-679`（5 例，含大小写不敏感 revision 扫描） |
| AC7 门禁 + 零越界 | 四项 EXIT 0；`src/**` 零改动 | **MET** | 见下方门禁节；两段 diff 均无 `src/**` |
| AC8 全量测试 + 独立 Review | App/CoreClient 0 failed；实现者不自审 | **MET** | DSH 复跑：App.Tests **910 / 0 / 11**（4m43s）、CoreClient **176 / 0 / 24**（24s）、Host **321 / 0 / 74**；独立复核 `FEA-06-RESIDUAL-4B-r1.md`（approved） |

## 门禁（原始输出见 `logs/`）

| # | 命令 | 结果 |
|---|---|---|
| 1 | `check.ps1`（默认） | `PASS (3 warnings)` / EXIT=0 |
| 2 | `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md` | `PASS (3 warnings)` / EXIT=0 |
| 3 | `verify_pins.ps1` | `PASS (all 18)`，C07 = `498882eb1750` / EXIT=0 |
| 4 | `generate_api_inventory.py --check` | `OK: rendered counts match`（`1/80/6 = 87`）/ EXIT=0 |

## NOT_RUN 与已披露缺口（不得记 PASS）

1. **无像素级证据（R-12）**：AC3/AC4/AC5 只有结构性断言（控件树、属性、AutomationProperties），**未做**主题/字体/像素截图层验收。DSH 裁决：结构性证据对验收可接受，但**不得**表述为「已完成视觉验收」；如需视觉验收，另开冒烟卡（可复用 `tools/p2-ui-smoke.ps1`）。
2. **Esc 走 `*ForTest` seam（R-11）**：`WorkbenchPageView.cs:219` 的 `HandleKeyForTest` 与真实 `OnWorkbenchKeyDown` 共用逻辑，但 headless 未端到端验证真实键盘事件。
3. **`HostController` 的 `catch (IsUiFacingFailure) → null` 分支未在默认门禁触发**（无 runtime seam）→ gated 集成用例。
4. **`CoreServiceClient` public 方法未贯穿 `SendAsync`**（无传输 seam）→ gated 集成用例 / Python 侧 `tests/core/test_region_text_read_command.py`。
5. **P2-1（4B r1）S6 焦点管理未断言**：登记为 limitation，不阻断；面板打开后焦点落点未验。
6. **P2-2（4B r1）AC4 三条原因文案「两两不同」缺显式断言**：实现正确，机械验收缺口，登记。

## 复现命令

```powershell
cd 'G:\CODEX\New Manga'
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
C:\Python314\python.exe tools/generate_api_inventory.py --check
dotnet build apps/desktop-avalonia/NewManga.sln -c Debug
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests -c Debug
dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests -c Debug
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests -c Debug
```

## 范围声明

- 本卡只改 `apps/desktop-avalonia/**` 与 `doc/**`/`verification/**`；`src/**`（Python Core）**零改动**。
- 未新增 wire 码、未改 schema、未改错误码闭集（`DraftErrorMap` 仍 19 键）。
- 未新增 `skip`/`xfail`；唯一被改的既有断言是 I13 的 `DoesNotContain("查看对照")` → 正向，且**同时新增**负向断言（方向为加强）。
