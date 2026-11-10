---
task_id: FEA-14-FONT-1
reviewer: fresh 独立上下文子 agent（续接 r1；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 40c252904
reviewed_head: 133498d33
decision: changes_requested
---

# Review：FEA-14-FONT-1（r1 处置后复核，r2）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `133498d338549faec1faf0bbf0dbf44a632b02d9`**。审查开始 `2026-11-10T14:26:29+08:00`、结束 `14:28+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`40c252904..133498d33`，**8 文件**：`service.py`、`core_service.py`、2 个测试、卡面、README、`regression-v11.log`、r1 报告。全部 ⊆ FONT-1 allowed_paths（OUT=0）。
- 卡面 base 已改 `24637d1b4`；无 Core 契约字节/DDL 之外变化；C-07 统计继续 65/72。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-FONT-1-r2\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=1** / **P3=3**）。

R1-001（严格魔数+扩展）、R1-002（删受管副本+`FONT_NOT_FOUND`）、R1-004（allowed_paths）已实质关闭；R1-003 只修到 service 层，**wire `ListFontAssets` 仍要求空 payload、无 family 过滤**，卡面/README 对 AC3 的“family 过滤”仍高于实际。P3：删除受管文件 OSError 被静默吞、严格格式仅测 `.ttf` 伪装、Host P2 DTO 空字段。

## 2. r1 findings 关闭判定

| r1 ID | r1 级别 | r2 判定 | 依据 |
|---|---|---|---|
| R1-001 | P2 | **CLOSED** | `_font_format` 现在先要求 suffix ∈ FONT_EXTENSIONS，再要求 magic 存在且与 suffix 匹配；`disguised.ttf` 测试通过；AC1 改为 family/subfamily/format，weight/style/display_name 登记为 limitation |
| R1-002 | P2 | **CLOSED（P3 残留）** | `delete_asset` 先 soft_delete，再 `managed.unlink(missing_ok=True)`；不存在/已删 → `FONT_NOT_FOUND`；wire `not_found`；测试断言源文件保留、受管副本删除、二次删除 typed。残余：`unlink` 的 `OSError` 被静默 pass（R2-002） |
| R1-003 | P2 | **PARTIAL（P2）** | `FontLibraryService.list_assets(family)` 已过滤 deleted + family；但 **wire `handle_list_font_assets` 仍 `set(payload) != set()`，无 family 参数**，P1 无法使用过滤；测试也无 family 过滤用例；卡面 AC3 写“family 过滤”，README AC3 写“family/weight 过滤/内置条目登记 limitation”，两者与 wire 现状不一致（R2-001） |
| R1-004 | P2 | **CLOSED** | allowed_paths 已补 `CONTRACT-UNFREEZE-*.md` + 4 个 v11 适配测试；`40c..133` 8 文件 OUT=0 |
| R1-005 | P3 | **PARTIAL（登记）** | Host `ImportFontAssetAsync` 仍用空 Format/Sha256/Size=0 构造 `FontAssetInfo`；卡面 r1 记录已登记、wire P2 只回 asset_id/family/subfamily/status（R2-003） |
| R1-006 | P3 | **PARTIAL** | 新增伪装 `.ttf`/删除 typed 测试；仍缺 `.woff2`/`.otf` 魔数一致、>50MB、>200 active、family 过滤、refresh sha mismatch/未知文件失败、并发同 sha（R2-004） |
| R1-007 | P3 | **CLOSED** | base 改 `24637d1b4`；新增 `logs/regression-v11.log` **1235 passed**，EXIT 0；pins/API 日志完整 |

## 3. R2 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R2-001 | **P2** | `src/bootstrap/core_service.py:5105-5108`；`src/application/fonts/service.py:96-102`；卡 AC3 `:73`；README AC3 `:13` | **family 过滤没有 wire 入口**：`handle_list_font_assets` 仍只接受空 payload，调用 `list_assets()` 不传 family；service 的 family 参数和测试都没有接到 P1。卡面写“目录查询按 family 过滤”，README 写“family/weight 过滤/内置条目登记 limitation”，实际只做到“排除 deleted + 无过滤列表”。 | 让 P1 接受可选 `family`（PREQ 允许可选键）并传给 `list_assets(family)`；补 wire/storage family 过滤测试；或把 AC3 改为“无过滤列表”，与 README 一致 |
| R2-002 | P3 | `src/application/fonts/service.py:150-160` | `delete_asset` 的 `managed.unlink(missing_ok=True)` 包在 `try/except OSError: pass` 中：删除受管副本失败时仍返回 True，行已 soft-delete → 受管文件残留，AC2“删除受管副本”不保证。 | 让 unlink 失败也 typed 报错/记录失败，或至少把失败写入错误；补只读文件/占用文件失败测试 |
| R2-003 | P3 | `CoreServiceClient.cs:ImportFontAssetAsync` | Host P2 返回的 `FontAssetInfo` 只有 asset_id/family/subfamily（Format/Sha256 空、Size=0）；UI 若消费这些字段会显示空值。卡面已登记，但仍应在 DTO/README 明确“import 后需 List 刷新”。 | DTO 文档化空字段语义，或 P2 wire 返回完整资产；import 后 UI 重新 List |
| R2-004 | P3 | `tests/storage/test_fonts.py`；`tests/core/test_font_wire.py` | 严格格式只测了 `.ttf` 伪装；缺 `.woff2`/`.otf` 魔数/扩展不一致、>50MB、>200 active、family 过滤、refresh sha mismatch/未知文件失败、并发同 sha。 | 补上述边界；尤其 `.woff2`/`.otf` 与大小/数量上限 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 字体安装 | **MET** | 严格魔数+扩展、≤50MB/≤200 active、复制到 `fonts/<sha16>.ext`、sha256、幂等、typed 错误；weight/style/display_name 已明确 limitation（R1-001 关） |
| AC2 删除 | **MET（P3）** | 删除行（soft delete）+ 受管副本，源文件保留；不存在/已删 → typed `FONT_NOT_FOUND`；unlink 失败静默 P3 |
| AC3 列举/刷新 | **PARTIAL（P2）** | 列举排除 deleted；refresh available/failed；family 过滤只在 service，P1 wire 无入口；weight 过滤/内置条目 limitation（R2-001） |
| AC4 迁移无损 | **MET** | schema v11 additive；v1–v10 不变；regression-v11 **1235 passed** |
| AC5 契约/门禁 | **MET** | inventory 65/72；`--check` EXIT 0；pins 18/18；C-07 UNFREEZE v1.4 `8d92a32f…` |
| AC6 证据 | **MET（P3）** | 7 passed、App 874/0/11、pins/API、1235 回归日志；Canonical 5/5 |

## 5. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 14:27:07 → 14:27:11 | PASS（3 warnings：11 非终态 / STATUS 3166 B·31 L / PLAN 6994 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-FONT-1.md` | 14:27:07 → 14:27:11 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 14:27:07 → 14:27:11 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 14:27:07 → 14:27:11 | `OK: rendered counts match FEA-C07 doc`；合计 72 | **0** |
| 5 | `python -m pytest tests/storage/test_fonts.py tests/core/test_font_wire.py -q` | 14:27:07 → 14:27:08 | **7 passed** | **0** |
| 6 | v11 regression（日志） | 14:24:17 | storage+core+fea09+fea11 **1235 passed**，EXIT 0 | **0** |
| 7 | App.Tests 全量（日志） | 14:14:54 | **874 passed / 0 failed / 11 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 14:26:29 / 14:28+ | 两次均 **clean**；HEAD 均 `133498d33…` | — |
| 9 | 范围/Canonical | 14:26+ | 8 文件全部 ⊆ allowed（OUT=0）；FONT-1 Canonical 5/5 sha256 匹配 | — |

## 6. NOT_RUN

- 真实字体渲染（Avalonia/系统字体）、随包字体、商业字体元数据准确性：NOT_RUN。
- Fluent 设置页字体管理 UI：NOT_RUN（FONT-2）。
- 真实字体文件（非合成 fixture）的大文件/占用文件/并发导入：仅单元测试，未做真实资源压力。
- 未修改/重跑 Core 全量；采用 regression-v11 日志。

## 7. 处置建议

1. **R2-001（P2）**：给 P1 `ListFontAssets` 加可选 family 并接 service；补 wire/storage family 过滤测试；或把 AC3 改为“无 family 过滤”并删 README 的放宽表述。
2. R2-002（P3）：unlink 失败 typed/记录，补只读/占用文件测试。
3. R2-003/R2-004（P3）：Host import DTO 空字段语义；补 `.woff2`/`.otf` 魔数、大小/数量上限、refresh 异常、并发测试。
4. AC1/AC2 可维持 MET；AC3 修 wire 后再转 MET；AC4/5/6 已有证据。

## 8. 审查者声明

本报告由未参与 FEA-14-FONT-1 实现的独立上下文子 agent 出具（续接 r1；r1 报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/日志/逐行核对；未执行项在 §6 记 NOT_RUN。
