---
task_id: FEA-14-FONT-1
reviewer: fresh 独立上下文子 agent（未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 24637d1b4
reviewed_head: 40c252904
decision: changes_requested
---

# Review：FEA-14-FONT-1（r1）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `40c252904396bff5a227ba73dec1546fa815949c`**。审查开始 `2026-11-10T14:21:25+08:00`、结束 `14:23+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`24637d1b4..40c252904`，**28 文件**（Core schema/service/store/wire、Host 三层、契约、测试、证据、PLAN/ledger/card）。无 C-02/C-03/P15 等契约字节改动。
- **范围 OUT=5**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-FONT1.md`（allowed 只有 `doc/reviews/FEA-14-FONT-1-*.md`）、`tests/core/test_v9_migration.py`、`tests/fea09/test_v7_migration.py`、`tests/fea11/test_source_gate_unify.py`、`tests/storage/test_reading_preferences.py`。
- 卡面 `base_commit: bd6aa5246`，用户 base `24637d1b4`；实现提交 6f696eaeb/4ecb195f2 在 24637 之后（P3 provenance）。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-FONT-1-r1\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=4** / **P3=3**）。

迁移/受管复制/幂等/typed wire 主链路可跑（7 passed、App 874/0/11、pins 18/18、inventory 65/72）；但 **AC1/AC2/AC3 的卡面判据与实现不一致**：AC1 要求的 weight/style 未落库；AC2 要求的「删除受管文件 + 不存在 typed 错误」实现为 soft-delete + false；AC3 要求的 family/weight 目录过滤与内置条目不存在。另有导入格式校验「魔数 OR 扩展」可绕过、范围 OUT=5。

## 2. Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R1-001 | **P2** | `src/application/fonts/service.py:42-110`；卡 AC1 `:68`；README AC1 | **AC1 判据未全部落地**：卡面要求记录 `family/weight/style/sha256`，实现表/`FontAsset` 只有 `family/subfamily/format/sha256/size_bytes/managed_path/license_note/state/created_at`，**无 weight/style（也无 display_name）**；family 为文件名启发式（limitation 已披露）。另 `_font_format` 对扩展名在允许列表的文件直接返回后缀——**任意内容只要改名 `.ttf` 即可通过魔数校验**（PNG 后缀测试只覆盖 suffix 不允许的情况）。 | 补 weight/style（或把 AC1 改为 family/subfamily/format 并记录 limitation）；格式校验必须同时满足魔数与扩展名（或明确只信扩展名并改判据）；补“PNG 内容改名 .ttf”负例 |
| R1-002 | **P2** | `src/application/fonts/service.py:111-116`；`src/infrastructure/sqlite/fonts.py:soft_delete`；卡 AC2 `:69`；README AC2 | **AC2 判据与实现相反**：卡面要求「删除行 + 受管文件；不存在 → typed 错误」；实现 `delete_asset` 只 `soft_delete`（state=deleted + deleted_at），**不删受管副本**；不存在/已删除直接返回 `False`，wire 返回 `deleted:false`（不是 typed 错误）。README limitation 已写「软删保留受管副本」，但卡面仍标 MET。 | 要么实现受管文件删除 + `FONT_ASSET_NOT_FOUND` typed 错误，要么把 AC2 改成「soft delete 保留受管副本、不存在返回 false」并同步卡面/README；明确引用检查由 FONT-2 负责 |
| R1-003 | **P2** | `src/application/fonts/service.py:list_assets`/wire P1；卡 AC3 `:70`；README AC3 | **AC3 判据缺失**：卡面要求「含内置条目，目录查询按 family/weight 过滤」；实际 `ListFontAssets` 无任何过滤参数、无内置条目（README 已说内置缺省空），`list_assets()` 也返回 **deleted** 行；refresh 仅 available/failed。 | 把 AC3 改为「列举 + refresh（无过滤/无内置）」并记录 limitation；或补 filter/内置条目；`list_assets` 默认排除 deleted，或明确 wire 返回全部状态 |
| R1-004 | **P2** | `git diff --name-only 24637d1b4..40c252904` vs 卡 allowed_paths `:21-44` | **范围 OUT=5**：UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-FONT1.md` 不符合 FONT-1 审查文件 pattern）与 4 个 v11 适配测试（`tests/core/test_v9_migration.py`、`tests/fea09/test_v7_migration.py`、`tests/fea11/test_source_gate_unify.py`、`tests/storage/test_reading_preferences.py`）不在 allowed_paths。用户要求“无未授权文件”不成立。 | 扩 allowed_paths（UNFREEZE 载体 + 4 个适配测试）并记录，或拆分/移动适配改动；重跑范围审计 |
| R1-005 | P3 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:ImportFontAssetAsync` | Host P2 的 `FontAssetInfo` 用 **空 Format/Sha256/SizeBytes=0** 构造；P2 wire 只回 `asset_id/family/subfamily/status`，Host DTO 字段无法填充。UI 若消费 format/sha/size 会拿到空值。 | 要么 P2 wire 返回完整 asset（与 P1 一致），要么 UI 在 import 后重新 List；在 DTO/README 说明空字段语义 |
| R1-006 | P3 | `tests/storage/test_fonts.py`；`tests/core/test_font_wire.py` | 测试未覆盖：>50MB、>200 active、PNG 内容改名 .ttf、非存在删除的 typed 错误、family/weight 过滤、list 的 deleted 行、refresh 的 sha mismatch/未知文件导入失败、并发导入同 sha。 | 补这些边界/负例；尤其格式魔数与数量上限 |
| R1-007 | P3 | 卡 `:13`；README `:12`（1235 passed） | 卡面 base `bd6aa5246` 与用户 base `24637d1b4` 不一致；README 声称迁移回归 **1235 passed** 但仓库只有 `pytest-font.log` 7 passed、App 874、pins-api，没有 1235 的日志。 | base 统一；把 1235 的 pytest 日志补入证据目录，或删除该数字/注明来源 |

## 3. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 字体安装 | **PARTIAL** | 受管复制/幂等/大小/数量/typed 错误/软删源文件保留有实现；**weight/style 缺失**；格式校验可被“魔数 OR 扩展”绕过；测试未覆盖边界（R1-001/R1-006） |
| AC2 删除 | **PARTIAL** | 只 soft-delete，受管文件保留；卡面要求的「删受管文件/不存在 typed」未实现；README limitation 与卡面矛盾（R1-002） |
| AC3 列举/目录 | **PARTIAL** | `ListFontAssets` 无 family/weight 过滤、无内置条目；`list_assets` 含 deleted；refresh available/failed 可用（R1-003） |
| AC4 迁移无损 | **MET** | schema v11 additive；v1–v10 未改；v11 表/索引；迁移适配测试通过（1235 未留日志，见 R1-007） |
| AC5 契约/门禁 | **MET** | inventory 65/72；`--check` EXIT 0；pins 18/18；C-07 UNFREEZE v1.4 `8d92a32f…`；无 C-02/C-03/P15 改动 |
| AC6 证据 | **MET（P3）** | 7 passed、App 874/0/11、pins/API 日志 EXIT 0；1235 无日志（R1-007） |

## 4. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 14:22:32 → 14:22:35 | PASS（3 warnings：11 非终态 / STATUS 3166 B·31 L / PLAN 6994 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-FONT-1.md` | 14:22:32 → 14:22:35 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 14:22:32 → 14:22:35 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 14:22:32 → 14:22:35 | `OK: rendered counts match FEA-C07 doc`；合计 **72** | **0** |
| 5 | `python -m pytest tests/storage/test_fonts.py tests/core/test_font_wire.py -q` | 14:22:35 → 14:22:37 | **7 passed** | **0** |
| 6 | App.Tests 全量（日志） | 14:14:54 起 | **874 passed / 0 failed / 11 skipped**（HEAD=4ecb195f2） | **0** |
| 7 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 14:21:25 / 14:23+ | 两次均 **clean**；HEAD 均 `40c252904…` | — |
| 8 | 范围/Canonical | 14:22+ | 28 文件，**OUT=5**；Canonical 4/4 sha256 匹配 | — |

## 5. NOT_RUN

- 真实字体渲染（Avalonia/系统字体）与随包字体：NOT_RUN（本卡仅数据面）。
- Fluent 设置页字体管理 UI：NOT_RUN（FONT-2）。
- 真实商业字体解析/元数据准确性：NOT_RUN（family 启发式、无 fontTools）。
- 未修改/重跑 Core 全量、App 全量（采用日志）；无真实用户数据写入。

## 6. 处置建议

1. **R1-001/R1-002/R1-003（P2）**：先决定 AC1/AC2/AC3 的产品口径并同步卡面/README：补 weight/style、删受管文件+typed 错误、family/weight 过滤/内置条目；若产品决定不实现，则改 AC 并登记 limitation，不能继续标 MET。
2. **R1-001 格式校验**：魔数与扩展名同时校验；补 PNG 改名 .ttf 负例。
3. **R1-004（P2）**：扩 allowed_paths/拆分 UNFREEZE 载体与 4 个适配测试，重跑范围审计。
4. P3：Host import DTO 空字段、边界测试、1235 日志/base 统一。
5. 修后重跑 check/pins/API/定向 7；真实字体渲染/UI 仍 NOT_RUN。

## 7. 审查者声明

本报告由未参与 FEA-14-FONT-1 实现的独立上下文子 agent 出具；只读审查，唯一写入为本文件。PASS 基于本次实测/日志/逐行核对；未实测项在 §5 记 NOT_RUN；AC1/AC2/AC3 的判据与实现差异按卡面/README 原文逐项对照记录。
