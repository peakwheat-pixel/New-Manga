---
task_id: FEA-14-FONT-1
reviewer: fresh 独立上下文子 agent（续接 r1/r2；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 133498d33
reviewed_head: 0b0733322
decision: changes_requested
---

# Review：FEA-14-FONT-1（r2 处置后复核，r3）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `0b0733322e4ba1947e2c1b2e0a5bedf06e59b07c`**。审查开始 `2026-11-10T14:29:14+08:00`、结束 `14:30+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`133498d33..0b0733322`，**6 文件**：`service.py`、`test_fonts.py`、卡面、README、`pytest-font.log`、r2 报告。全部 ⊆ FONT-1 allowed_paths（OUT=0）。
- 卡面 base `24637d1b4`；无 Core/wire/契约/DDL 新改动。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-FONT-1-r3\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=1** / **P3=3**）。

R2-001 口径已自洽：AC3/README 明确 wire P1 保持 `{}`、不做 family/weight 过滤；service 的 family 过滤留内部/FONT-2。R2-002 的 typed 失败也已加入，8 passed。但 **删除失败路径先 soft_delete 再 unlink**：unlink 失败时行已 deleted、受管文件残留，`delete_asset` 再次调用会返回 `FONT_NOT_FOUND`，**调用方无法“重试”**；wire 还把 `FONT_DELETE_FAILED` 也映射到 `not_found` 类别。

## 2. r2 findings 关闭判定

| r2 ID | r2 级别 | r3 判定 | 依据 |
|---|---|---|---|
| R2-001 | P2 | **CLOSED** | 卡面 AC3 改为「wire P1 保持 PREQ `{}` 形状、不做 family/weight 过滤，过滤留 FONT-2」；README AC3 同步；service `list_assets(family)` 仅内部/测试，wire 不暴露 |
| R2-002 | P3 | **PARTIAL（P2）** | `delete_asset` 对 unlink 失败抛 `FONT_DELETE_FAILED`，不再静默；8 passed 含 `test_delete_reports_typed_failure_when_managed_copy_is_stuck`。**但顺序是先 `soft_delete` 再 unlink**：失败后行已 deleted、文件仍在，重试只会 `FONT_NOT_FOUND`；卡面“调用方可重试”不成立（R3-001） |
| R2-003 | P3 | **PARTIAL（登记）** | Host P2 import DTO 空 Format/Sha256/Size 仍登记；UI 需 import 后 List 刷新；未改 |
| R2-004 | P3 | **OPEN（P3）** | 仍缺 `.woff2`/`.otf` 魔数一致、>50MB、>200 active、family 过滤、refresh sha mismatch/未知文件失败、并发同 sha 边界测试（登记） |

## 3. R3 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R3-001 | **P2** | `src/application/fonts/service.py:150-162`；`tests/storage/test_fonts.py:119-134` | **删除失败后不可重试/状态不一致**：`soft_delete` 先执行，`unlink` 失败才抛 `FONT_DELETE_FAILED`；此时 row.state=deleted、deleted_at 已写，受管文件 stuck。再次 `delete_asset` 走 `state=="deleted"` → `FONT_NOT_FOUND`；调用方只能上报，不能按卡面注释“重试”。测试只断言错误码，未断言 row/file 状态或二次调用行为。 | 先 unlink，成功后再 soft_delete；或在 unlink 失败时回滚 row 状态（active）并保留可重试；补失败后 row 仍 active/文件仍存在/二次可重试测试 |
| R3-002 | P3 | `src/bootstrap/core_service.py:5130-5134` | **wire 错误类别错误**：`except FontLibraryError` 一律 `P16WireError(error.code, "not_found", ...)`；`FONT_DELETE_FAILED` 也被归类为 `not_found`，与 `FONT_NOT_FOUND` 不可区分。 | 按 code 映射类别：`FONT_NOT_FOUND`→not_found，`FONT_DELETE_FAILED`→write/failed；补 wire 负例 |
| R3-003 | P3 | `verification/FEA-14-FONT-1/logs/pytest-font.log:1`；`logs/dotnet-app-tests.log:1`；卡 Canonical | `pytest-font.log` HEAD=`133498d33`（r2 提交），App 全量日志 HEAD=`4ecb195f2`（更早），生成于 r3 提交前；卡 Canonical 实际 **5 行**（EV-FN-001..005），用户 r3 描述“6 行”与之不符。 | 在最终 head 重生成日志，或注明生成时 HEAD/工作树；Canonical 行数与描述统一 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 字体安装 | **MET** | 严格魔数+扩展、≤50MB/≤200 active、受管复制、sha256、幂等、typed 错误；weight/style/display_name limitation 已登记 |
| AC2 删除 | **PARTIAL（P2）** | 正常路径：soft delete + 受管副本 + 源文件保留；不存在/已删 typed `FONT_NOT_FOUND`；**unlink 失败后 row 已 deleted、文件 stuck、不可重试（R3-001）** |
| AC3 列举/刷新 | **MET（P3）** | wire P1 `{}`、无 family/weight 过滤（FONT-2 limitation）；list 排除 deleted；refresh available/failed；内部 family 参数保留 |
| AC4 迁移无损 | **MET** | v11 additive；v1–v10 不变；regression-v11 **1235 passed** |
| AC5 契约/门禁 | **MET** | inventory 65/72；`--check` EXIT 0；pins 18/18；C-07 v1.4 `8d92a32f…` |
| AC6 证据 | **MET（P3）** | 8 passed、App 874/0/11、1235 回归、pins/API；日志 HEAD/Canonical 行数见 R3-003 |

## 5. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 14:29:58 → 14:30:02 | PASS（3 warnings：11 非终态 / STATUS 3166 B·31 L / PLAN 6994 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-FONT-1.md` | 14:29:58 → 14:30:02 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 14:29:58 → 14:30:02 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 14:29:58 → 14:30:02 | `OK: rendered counts match FEA-C07 doc`；合计 72 | **0** |
| 5 | `python -m pytest tests/storage/test_fonts.py tests/core/test_font_wire.py -q` | 14:29:58 → 14:30:00 | **8 passed** | **0** |
| 6 | v11 regression（日志） | 14:24:17 | **1235 passed**，EXIT 0 | **0** |
| 7 | App.Tests 全量（日志） | 14:14:54 | **874 passed / 0 failed / 11 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 14:29:14 / 14:30+ | 两次均 **clean**；HEAD 均 `0b0733322…` | — |
| 9 | 范围/Canonical | 14:29+ | 6 文件全部 ⊆ allowed（OUT=0）；Canonical **5/5** sha256 匹配 | — |

## 6. NOT_RUN

- 真实字体渲染/随包字体、商业字体元数据准确性、Fluent 设置页字体 UI：NOT_RUN。
- 真实大文件/占用文件/并发导入：仅单元测试，未做真实资源压力。
- 未重跑 Core/App 全量；采用 regression-v11 与 App 日志。

## 7. 处置建议

1. **R3-001（P2）**：调整删除顺序（unlink 成功→soft_delete）或失败回滚 row active；补失败后状态/重试测试。
2. **R3-002（P3）**：按 code 映射 wire error category，区分 not_found 与 write/failed。
3. **R3-003（P3）**：最终 head 重生成日志或注明 HEAD；统一 Canonical 行数（实际 5）。
4. R2-003/R2-004 P3 仍登记；AC1/AC3/AC4/AC5/AC6 可维持，AC2 需 R3-001 后再转 MET。

## 8. 审查者声明

本报告由未参与 FEA-14-FONT-1 实现的独立上下文子 agent 出具（续接 r1/r2；历史报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/日志/逐行核对；未执行项在 §6 记 NOT_RUN。
