---
task_id: FEA-14-READ-1
reviewer: fresh 独立上下文子 agent（续接 r1–r3；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: e7dcfaeda
reviewed_head: 4de1c54f0
decision: approved
---

# Review：FEA-14-READ-1（r3 处置后复核，r4）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `4de1c54f087c9be5ab9f736071b05cc7821e8234`**。审查开始 `2026-11-10T13:22:11+08:00`、结束 `13:22:54+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`e7dcfaeda..4de1c54f0`，**6 文件**：`service.py`、`reading_export.py`、storage 测试、README、卡面、r3 报告。全部 ⊆ READ-1 allowed_paths（OUT=0）；无产品代码之外的契约字节改动。
- 卡面 base `f9bf922aa`（实际实现起点）；用户按 r3 报告用的 base 是 `e7dcfaeda`。provenance 注记见 §5/R3-005（保留 r3 结论）。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/定向日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-1-r4\`。

## 1. 结论

**`approved`**（P0=0 / P1=0 / P2=0 / **P3=2**）。

r3 的 P2/P3 已实质关闭：P10 改为 **None 哨兵/presence 合并**（显式默认值可重置；旧“值等于默认即未提供”启发式已删除；测试通过）；P14 `read_pages_int` 与 `finished` 统一取整；README AC5 改 PARTIAL、pin `59ab90f7…`；README AC3 改页面口径；UNFREEZE 拼写已修。定向 28 passed、门禁全绿。残余 2 个 P3 是测试/边界（P10 wire 未单独测 partial；P14 99.6% 边界未有测试）。

## 2. r3 findings 关闭判定

| r3 ID | r3 级别 | r4 判定 | 依据 |
|---|---|---|---|
| R3-001 | P2 | **CLOSED** | `service.py:550-580` 五参数默认改 `None`；未提供保留已存值，显式传入（含 original/ltr/1.0/False/single）覆盖；旧启发式（`mode == "original"` 等）已删除；新增 `test_explicit_default_values_can_reset_preferences` 通过 |
| R3-002 | P2 | **CLOSED** | README AC5 改 **PARTIAL**，pin 写 `59ab90f7…`；Canonical EV-RD-006 hash 刷新；与卡面/UNFREEZE 一致 |
| R3-003 | P3 | **CLOSED（P3 残余）** | `read_pages_int=int(round(read_pages))`；`finished = bool(total_pages and read_pages_int >= total_pages)`；代码逻辑一致；但未补 99.6%/2 页边界测试（R4-002） |
| R3-004 | P3 | **CLOSED** | README AC3 改为页面口径（pages JOIN/per-chapter percent×pages/read_pages/total_pages/finished） |
| R3-005 | P3 | **CLOSED（登记）** | provenance 注记保留：用户 base 82ea 在实现之后；Reader 日志 HEAD=d0b、App 全量 HEAD=82ea、卡面 base=f9bf；不追改历史日志（R4-001/R4-002 不再重复） |

## 3. R4 Findings（P3）

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R4-001 | P3 | `tests/storage/test_reading_preferences.py:178-187`；`core_service.py:5042-5066` | P10 的 explicit-default 测试只覆盖 **storage service**；wire 层 `_extras_prefs`/`**prefs` 的 presence 语义没有单独测试。静态看 `**prefs` 只转发提供键、None 哨兵正确，但缺少 wire 级回归（例如 `SaveReadingPreferences` 先 translated，再只发 `prefs{}`/只发默认值）。 | 加一条 wire P10 partial/explicit-default 测试；或在 README 说明该语义仅由 storage 测试覆盖 |
| R4-002 | P3 | `reading_export.py:653-666`；`tests/storage/test_reading_preferences.py` | P14 取整/finished 代码已统一，但没有 99.6%/2 页边界测试；`finished` 在 99.6% 时会因 `read_pages_int=2` 变 true，UI 可能同时在 `percent=99.6` 与“已完成”之间产生语义歧义。 | 补 99.6%/2 页边界测试；在 AC3/README 明确“按页取整后完成”的判定口径，或改为 percent>=100 才 finished |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好持久化 | **PARTIAL** | Core v10/P9/P10、partial/explicit-default、两次装配测试通过；**Fluent UI 未接线**；真实进程重启 NOT_RUN |
| AC2 书签 | **PARTIAL** | Core/P11-P13 CRUD/跨书通过；UI 未接线；P12/P15 偏差登记（DSH 接受/后续 READ-2） |
| AC3 整书进度 | **PARTIAL** | P14 wire 页面口径（2 页 50% 测试）、取整/finished 代码一致；UI 未接；99.6% 边界无测试（R4-002） |
| AC4 迁移无损 | **MET** | v10 additive；旧 reading_progress 行字段级保留；v1-v9 bytes 未改；迁移测试通过 |
| AC5 契约/门禁 | **PARTIAL** | inventory 68/check EXIT 0、pins 18/18、偏差登记；README/卡面均为 PARTIAL（已一致） |
| AC6 证据 | **MET（P3）** | App 867/0/11、pytest 3487/0/10、Reader 70、targeted 28；首轮 5 failed 已在 README 说明；provenance 登记 |

## 5. 门禁与定向

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:22:32 → 13:22:34 | PASS（3 warnings：11 非终态 / STATUS 3173 B·31 L / PLAN 6926 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-1.md` | 13:22:32 → 13:22:34 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:22:32 → 13:22:34 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:22:32 → 13:22:34 | `OK: rendered counts match FEA-C07 doc`；渲染合计 68 | **0** |
| 5 | `python -m pytest tests/storage/test_reading_preferences.py tests/core/test_read_wire.py tests/core/test_v9_migration.py -q` | 13:22:39 → 13:22:43 | **28 passed** | **0** |
| 6 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:22:11 / 13:22:54 | 两次均 **clean**；HEAD 均 `4de1c54f0…` | — |
| 7 | 范围/Canonical | 13:22+ | 6 文件全部 ⊆ allowed（OUT=0）；READ-1 Canonical 6/6 sha256 匹配 | — |

## 6. NOT_RUN / 未验证

- Fluent Reader UI 的偏好/书签/进度/reset 确认：未接线（README limitation）。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘、READ-2 跨内容序列：NOT_RUN。
- 真实进程重启（两次装配测试已覆盖数据层，UI 未接）；未重跑 App/pytest 全量，采用 verification 日志（867/0/11、3487/0/10、Reader 70）。

## 7. 处置建议

1. R4-001/R4-002（P3）：补 wire P10 partial/explicit-default 测试与 P14 99.6% 边界测试；在 README/AC3 明确 finished 口径（取整后 or percent）。
2. AC1–AC3 的 UI 接线按 READ-2/后续卡处理；AC5 偏差由 DSH 明确接受或后续对齐 PREQ。
3. 保持 Canonical 6 行 hash 与 README/log 一致；真实 roots 不再写。

## 8. 审查者声明

本报告由未参与 FEA-14-READ-1 实现的独立上下文子 agent 出具（续接 r1–r3；历史报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/逐行核对；未执行项在 §6 记 NOT_RUN。
