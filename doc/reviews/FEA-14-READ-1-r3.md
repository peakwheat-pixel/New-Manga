---
task_id: FEA-14-READ-1
reviewer: fresh 独立上下文子 agent（续接 r1/r2；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: d0b77ed1a
reviewed_head: e7dcfaeda
decision: changes_requested
---

# Review：FEA-14-READ-1（r2 处置后复核，r3）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `e7dcfaedade177a628549c0ce561d22c4fbece33`**。审查开始 `2026-11-10T13:19:28+08:00`、结束 `13:20:34+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`d0b77ed1a..e7dcfaeda`，**9 文件**：`core_service`、`reading/service.py`、wire/storage 测试、README、Reader 定向日志、卡面、r2 报告、UNFREEZE 拼写。全部 ⊆ READ-1 allowed_paths（OUT=0）。
- 卡面 `base_commit: f9bf922aa`（实际实现起点）；用户本轮指定 base `d0b77ed1a`（r2 处置前）。本报告比较 r2→r3 处置并核对 head 代码；历史 base 异常见 R3-005。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/定向日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-1-r3\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=2** / **P3=3**）。

P14 wire 页面口径已修并通过非空 2 页 50% 测试；P10 的 partial 合并也已加入，但实现用「值等于默认值即视为未提供」的启发式，**无法显式把偏好重置回默认值**（mode=original/zoom=1.0/double_page=False/layout=single），属于未完成的 partial patch；README AC5 仍写 MET/旧 pin `ab60d503…`，与卡面 AC5 PARTIAL/实际 pin `59ab90f7…` 矛盾。其余 r1/r2 P2/P3 基本关闭。

## 2. r2 findings 关闭判定

| r2 ID | r2 级别 | r3 判定 | 依据 |
|---|---|---|---|
| R-001 | P1 | **CLOSED** | `core_service.py:5085-5088` 已映射 `read_pages/total_pages/finished`；`test_book_progress_wire_is_page_based`（2 页 50% → read_pages=1/total_pages=2/percent=50/finished=false）通过；定向 27 passed |
| R-002 | P2 | **CLOSED（登记偏差）** | P12/P15 返回类型与 `confirm_token` 偏差保留但已登记；AC5 卡面改 PARTIAL；偏差接受与否交 DSH。注意 README AC5 仍是 MET/旧 pin（R3-002） |
| R-003 | P2 | **CLOSED** | P15 三处 `confirm` 默认 false；Core `confirm=False` 拒绝逻辑未变 |
| R-004 | P2 | **OPEN（P2）** | `ReadingExtrasService.save_preferences` 增加合并，但用「等于默认值」判定未提供：显式传 `mode=original`/`zoom=1.0`/`double_page=False`/`layout=single` 无法覆盖已存值（R3-001）；测试只覆盖非默认 zoom，无 explicit-default 用例 |
| R-005 | P2 | **CLOSED** | inventory 合计 68；`--check` EXIT 0（渲染 61/68 一致）；pin `59ab90f7…`；pins 18/18 |
| R-006 | P2 | **CLOSED** | UNFREEZE 记录 `vverify_pins`→`verify_pins`；pin 实际值已填 |
| R-007 | P2 | **CLOSED** | `d0b..e7d` 9 文件 OUT=0；allowed_paths 含 UNFREEZE/tests/fea09/fea11 |
| R-008 | P2 | **CLOSED（范围注记）** | 卡面 base=f9bf；用户 base `82ea7ca82` 仍指实现之后（`82ea..a44c` 无代码），见 R3-005 |
| R-009 | P3 | **CLOSED** | 新增 `logs/reader-targeted.log`：Reader 定向 **70 passed / 0 failed**（13:18:41，HEAD=d0b77ed1a） |
| R-010 | P3 | **CLOSED** | README `:23` 已注明 pytest 首轮 5 failed/3482 passed（v10 适配 fea09/fea11）、重跑 3487/0/10；日志保留两段 |
| R-011 | P3 | **CLOSED（测试层）** | 新增 `test_preferences_survive_reopen_two_assemblies`（关闭连接→重开→再次装配）；但 AC1 的真实进程重启仍 NOT_RUN（UI 未接） |

## 3. R3 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R3-001 | **P2** | `src/application/reading/service.py:563-571`；`tests/storage/test_reading_preferences.py:157-165` | **P10 partial patch 用默认值当哨兵，显式重置回默认值失效**：`mode = existing.mode if mode == "original" and existing.mode != "original" else mode`，direction/zoom/double_page/layout 同理。已存 translated/rtl/zoom2/double 时，显式传 `mode=original, zoom=1.0, double_page=False, layout=single` 会被全部忽略，无法恢复默认。用户明确要求裁决：**不可接受**；partial patch 需要 `None` 哨兵/字段存在性映射，而不是值比较。测试只覆盖「只传非默认 zoom」。 | 将参数改为 `mode: str \| None = None` 等，合并时 `if mode is not None`；wire 侧只发送实际出现的键；补 explicit-default 重置测试。若坚持当前启发式，需在卡面/README 明确 limitation 并要求 UI 传完整五字段。 |
| R3-002 | **P2** | `verification/FEA-14-READ-1/README.md:15`；卡面 `:83`；pin | README AC5 仍 **MET** 且写 C-07 pin **`ab60d503…`**；卡面 AC5 已改 **PARTIAL**，实际 pin 为 **`59ab90f7…`**。同一证据集自相矛盾，AC5 判定不可信。README canonical hash 已刷新但内容未同步 is not enough. | README AC5 改 PARTIAL，pin 改 `59ab90f7…`；重新生成 README canonical hash；与卡面/UNFREEZE 对齐 |
| R3-003 | P3 | `src/infrastructure/sqlite/reading_export.py:650-658`；`core_service.py:5085-5088` | **P14 取整/完成态边界不一致**：`read_pages=int(round(read_pages_float))`，`finished` 用未取整 float 比较；2 页 99.6% → read_pages=2、total_pages=2、finished=false，wire 出现「读页数==总页数但未完成」。 | 明确用同一口径：finished 基于 percent/取整后的 read_pages，或 read_pages 用 floor；补 99.6%/2 页边界测试 |
| R3-004 | P3 | `verification/FEA-14-READ-1/README.md:13` | README AC3 仍写 `SqliteReadingExtrasStore.book_progress`（**章节完成数/百分比**），与 r3 的 page-based 实现/测试相反；属旧文案残留。 | 改为页面口径（read_pages/total_pages/percent/finished），与 AC3/测试一致 |
| R3-005 | P3 | 用户 base `82ea7ca82`；卡面 `f9bf922aa`；`logs/reader-targeted.log` HEAD=`d0b77ed1a`；`dotnet-app-tests.log` HEAD=`82ea7ca82` | provenance 注记：用户给的 base 在实现之后；Reader 定向日志生成于 r2 head（d0b），App 全量日志生成于 82ea；卡面 base 已 f9bf。当前代码/日志能对应，但 base/HEAD 字段仍未完全统一。 | closeout 时统一 base=f9bf922aa、在证据注记「Reader 日志生成 head」；或说明日志按执行时 HEAD 记录 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好持久化 | **PARTIAL** | Core v10/P9/P10 + 两次装配测试；**P10 explicit-default 重置仍失效（R3-001）**；Fluent UI 未接线；真实进程重启 NOT_RUN |
| AC2 书签 | **PARTIAL** | Core/P11-P13 CRUD/跨书通过；UI 未接线；P12/P15 偏差已登记（DSH 决定接受/改形状） |
| AC3 整书进度 | **PARTIAL** | wire P14 页面口径已修（2 页 50% 测试）；**取整/finished 边界 P3**；UI 未接 |
| AC4 迁移无损 | **MET** | v10 additive；旧 reading_progress 行字段级保留；v1-v9 bytes 未改；迁移测试通过 |
| AC5 契约/门禁 | **PARTIAL** | inventory 68/check EXIT 0、pins 18/18、P12/P15 偏差登记；**README 仍 MET/旧 pin（R3-002）**，卡面 PARTIAL |
| AC6 证据 | **MET（P3）** | App 867/0/11、pytest 3487/0/10、Reader 70、targeted 27；首轮 5 failed 已在 README 说明；日志 HEAD 注记见 R3-005 |

## 5. 门禁与定向

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:20:17 → 13:20:20 | PASS（3 warnings：11 非终态 / STATUS 3173 B·31 L / PLAN 6926 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-1.md` | 13:20:17 → 13:20:20 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:20:17 → 13:20:20 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:20:17 → 13:20:20 | `OK: rendered counts match FEA-C07 doc`；渲染合计 68 | **0** |
| 5 | `python -m pytest tests/storage/test_reading_preferences.py tests/core/test_read_wire.py tests/core/test_v9_migration.py -q` | 13:20:14 → 13:20:17 | **27 passed** | **0** |
| 6 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:19:28 / 13:20:34 | 两次均 **clean**；HEAD 均 `e7dcfaeda…` | — |
| 7 | 范围/Canonical | 13:20+ | 9 文件全部 ⊆ allowed（OUT=0）；READ-1 Canonical 6/6 sha256 匹配 | — |

## 6. NOT_RUN / 未验证

- Fluent Reader UI 的偏好/书签/进度/reset 确认：未接线（README limitation）。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘、READ-2 跨内容序列：NOT_RUN。
- 未重跑 App 全量/pytest 全量；采用 `verification` 日志（App 867/0/11、pytest 3487/0/10、Reader 70）。
- 真实进程重启只因 UI 未接而未做；两次装配测试已补（测试层）。

## 7. 处置建议

1. **R3-001（P2）**：改 `save_preferences` 为 None 哨兵/presence 合并，补 explicit-default 重置测试；这是 partial patch 的语义正确性，不是单纯样式。
2. **R3-002（P2）**：README AC5 改 PARTIAL、pin 改 `59ab90f7…`，重算 README canonical hash；与卡面/UNFREEZE 一致。
3. R3-003/R3-004（P3）：统一 `read_pages` 取整与 `finished` 计算，补 99.6%/2 页边界；README AC3 改页面口径。
4. R3-005（P3）：统一 base=f9bf922aa，并给日志注记执行 HEAD。
5. 修后重跑 check/pins/API/targeted；真实 UI 仍 NOT_RUN。

## 8. 审查者声明

本报告由未参与 FEA-14-READ-1 实现的独立上下文子 agent 出具（续接 r1/r2；历史报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/逐行核对；未执行项在 §6 记 NOT_RUN；P10 的 explicit-default 行为按 head 代码逐行判定为 OPEN。
