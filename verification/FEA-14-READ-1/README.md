# FEA-14-READ-1 证据索引（阅读偏好 / 书签 / 整书进度）

- Task：`FEA-14-READ-1`（FEA-14 S5 READ 切片；复用 PREQ 预冻结 wire P9–P15）
- Head：`82ea7ca82`（执行时主树）
- 日期：2026-11-10

## 结论状态（Core + wire + 门禁完成；Fluent UI 集成未接线）

| AC | 判别 | 结果 |
|---|---|---|
| AC1 偏好持久化 | 按书 mode/direction/zoom/double_page/layout 保存后恢复 | **PARTIAL**：Core schema v10 `reading_preferences` + `ReadingExtrasService` + wire P9/P10 已验证（保存→再次读取一致、默认偏好、非法值拒绝）；**Fluent Reader UI 尚未读取/应用偏好**（见 limitation） |
| AC2 书签 | 新增（left/right/both）/列表/删除；跨书隔离 | **PARTIAL**：Core + wire P11–P13 完整（创建/列表/删除/跨书隔离/非法 side 拒绝，wire 测试通过）；**UI 书签面板未接**（limitation） |
| AC3 整书进度 | 按页面数计算；reset 需 confirm | **PARTIAL**：`book_progress` **页面口径**（pages JOIN、per-chapter percent×pages、read_pages/total_pages/finished）+ wire P14/P15（reset 需 confirm，未确认 → `INVALID_REQUEST`）已验证；**UI 未显示/未接 reset 确认**（limitation） |
| AC4 迁移无损 | schema v10 additive；旧 reading_progress 行字段级无损 | **MET**：`test_v10_migration_preserves_legacy_progress_rows`（v9→v10 旧行 `progress_percent` 保留、新列 NULL）；core 全量 1034 passed |
| AC5 契约/门禁 | 七命令实现 + inventory/pin 更新；偏差登记 | **PARTIAL**：7 命令（PascalCase wire + minor 3）实现；`generate_api_inventory.py --check` EXIT 0（IHostController 61 / 合计 68）；C-07 UNFREEZE v1.3 pin **`59ab90f7…`**（最终字节）；`verify_pins` 18/18。**P12/P15 返回类型（`Task<string?>`/`Task<int>`）与 P15 `confirm` vs `confirm_token?` 属已登记偏差，未按 PREQ §8 完全对齐** |
| AC6 证据 | 定向/全量测试、日志含 EXIT、NOT_RUN 登记 | **MET**：见下表与 NOT_RUN（全量日志见 `logs/`） |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/dotnet-app-tests.log` | App.Tests 全量 **867 passed / 0 failed / 11 skipped**；Reader 定向 70 passed | 0 |
| `logs/pytest-full.log` | pytest 全量最终 **3487 passed / 0 failed / 10 skipped**（首轮 5 failed/3482 passed：v10 适配 `fea09/test_v7_migration.py`、`fea11/test_source_gate_unify.py` 的 latest 断言；修复后全绿，日志保留两段） | 0 |
| `logs/reader-targeted.log` | App.Tests Reader 定向 **70 passed / 0 failed** | 0 |
| `logs/read-wire.log` | `tests/core/test_read_wire.py` 3 passed（P9–P15 往返） | 0 |
| `logs/reading-storage.log` | `tests/storage/test_reading_preferences.py` 5 passed | 0 |

**实现提交**：`f3f9ee5c4`（schema v10 + Core 服务）、`9b1cabc23`（Core wire + 装配）、`dacd2e901`（v9 证据适配）、`d05460684`（CoreClient/HostRuntime）、`707ede92d`（IHostController/HostController/Null/Fake）、`82ea7ca82`（inventory 61/68 + C-07 UNFREEZE pin v1.3）。

## limitation（不阻断 Core/wire 交付，阻 AC1–AC3 的 UI 层）

- **Fluent Reader UI 未接线**：按书偏好的读取/应用（模式/方向/缩放/双页/布局）、书签面板（增删/列表）、整书进度显示、reset 确认提示均未接入 `ReaderWorkbenchPages`/`ReaderViewModel`。Core 与 wire 层已具备全部能力（`IHostController` 七方法）。
- 建议另立 **READ-2（UI 接线）** 或在 READ-1 后续返修中完成；当前不得声称 AC1–AC3 的 UI 行为已验证。

## NOT_RUN（不得记 PASS）

- 真实 UI 手势/IME/多屏/DPI/系统主题/托盘（沿用 A3 登记）。
- Fluent Reader 偏好/书签/整书进度的真实 UI 交互（未接线）。
- 跨内容连续序列（READ-2 范围）。

## 复现

```powershell
python -m pytest tests/storage/test_reading_preferences.py tests/core/test_read_wire.py tests/core -q
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -v q
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
