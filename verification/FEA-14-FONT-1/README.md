# FEA-14-FONT-1 证据索引（Core 字体库）

- Task：`FEA-14-FONT-1`（FEA-14 S5 FONT 切片；复用 PREQ 预冻结 wire P1–P4）
- Head：`4ecb195f2`（Host 层 + C-07 v1.4 后；Core 提交 `6f696eaeb`）
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 字体安装 | 合法字体（严格魔数+扩展名）→ 受管 `fonts/` + SHA-256 行；幂等；非法拒绝 | **MET**：`FontLibraryService.import_asset`（≤50MB、≤200 active、ttf/otf/woff/woff2 魔数/扩展、复制到 `data_root/fonts/<sha16>.ext`）；同 sha256 幂等返回既有资产；`FONT_SOURCE_INVALID`/`FONT_FORMAT_UNSUPPORTED`/`FONT_LIMIT_REACHED` typed 错误 |
| AC2 删除 | 软删行 + 删除受管副本；不删用户源文件；不存在/已删 → typed `FONT_NOT_FOUND` | **MET**：`soft_delete`（state=deleted + deleted_at）；测试断言源文件保留 |
| AC3 列举/刷新 | 列举（排除 deleted）；refresh 报 available/failed；wire P1 保持 PREQ `{}` 形状（family/weight 过滤与内置条目登记 limitation/FONT-2） | **MET**：`list_assets`（wire `assets[]`）；`refresh_assets` 扫描受管目录，缺失/哈希不匹配 → `{path, code}`，未登记文件尝试导入 |
| AC4 迁移无损 | schema v11 additive | **MET**：v11 `font_assets` 表 + 索引；v1–v10 字节不变；v9/v10 证据测试动态适配（1235 passed） |
| AC5 契约/门禁 | P1–P4 按 PREQ §8；inventory EXIT 0；pins 18/18 | **MET**：四命令实现（`ListFontAssets`/`ImportFontAsset`/`DeleteFontAsset`/`RefreshFontAssets`，minor 3）；`generate_api_inventory.py --check` EXIT 0（IHostController 65 / 合计 72）；C-07 UNFREEZE v1.4 `8d92a32f…`；`verify_pins` 18/18 |
| AC6 证据 | 定向/全量测试、日志 EXIT、NOT_RUN | **MET**：见下表与 NOT_RUN |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/pytest-font.log` | `tests/storage/test_fonts.py` + `tests/core/test_font_wire.py` **8 passed**（含 unlink typed 失败测试） | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **874 passed / 0 failed / 11 skipped** | 0 |
| `logs/regression-v11.log` | v11 回归：storage+core+fea09+fea11 **1235 passed** | 0 |
| `logs/pins-api.log` | `verify_pins` 18/18、`generate_api_inventory.py --check` EXIT 0 | 0 |

**实现提交**：`6f696eaeb`（Core schema v11 + service/store + wire + 7 测试）、`4ecb195f2`（Host 三层 4 方法 + C-07 UNFREEZE v1.4）。

## 设计说明与 limitation

- **不随包任何字体**（PREQ §2）：内置字体列表缺省为空；内置条目需授权记录后另行加入（许可证红线）。
- family/subfamily 为**文件名启发式**（无 fontTools 依赖）：`MyFont-Regular.ttf` → family=MyFont、subfamily=Regular；真实字体元数据解析留 FONT-2/后续（登记）。
- 删除为软删，受管副本保留（PREQ：不删原文件；引用检查由 FONT-2 UI 消费）。
- 刷新对未登记的受管文件尝试导入（`refresh-import` 许可注记），失败逐文件记 `{path, code}`。

## NOT_RUN（不得记 PASS）

- 真实字体渲染（Avalonia 消费/系统字体）与随包字体 = NOT_RUN（本卡仅数据面；渲染留 FONT-2/UI 卡）。
- Fluent 设置页字体管理 UI = NOT_RUN（未接线；FONT-2 范围）。
- 真实字体文件（商业字体）解析与元数据准确性 = NOT_RUN（启发式，未用 fontTools）。

## 复现

```powershell
python -m pytest tests/storage/test_fonts.py tests/core/test_font_wire.py -q
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
