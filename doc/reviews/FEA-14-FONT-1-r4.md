---
task_id: FEA-14-FONT-1
reviewer: fresh 独立上下文子 agent（续接 r1–r3；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 0b0733322
reviewed_head: 2bec370e7
decision: changes_requested
---

# Review：FEA-14-FONT-1（r3 处置后复核，r4）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `2bec370e7ebe0d3f28866cd3c1acf7255d0b2493`**。审查开始 `2026-11-10T14:31:57+08:00`、结束 `14:32+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`0b0733322..2bec370e7`，**6 文件**：`service.py`、`core_service.py`、`test_fonts.py`、卡面、`pytest-font.log`、r3 报告。全部 ⊆ FONT-1 allowed_paths（OUT=0）。
- 卡面 base 24637d1b4；无新建 Core/wire/契约/DDL 变更。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-FONT-1-r4\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=1** / **P3=2**）。

R3-001 已实质关闭：删除改为先 unlink、成功后再 soft_delete；失败时 row 保持 active，测试补了失败/重试/list 空。R3-003 的 Canonical 实际 5 行也已核实。剩余问题集中在 **FONT_DELETE_FAILED 的 wire error category**：实现用 `"write"`，但现有 error taxonomy 的 category 是 `validation/not_found/conflict/internal`；卡面还写「write + retryable」，而 `P16WireError` 没有 retryable 参数/字段。另有 wire 负例与日志 HEAD 的 P3。

## 2. r3 findings 关闭判定

| r3 ID | r3 级别 | r4 判定 | 依据 |
|---|---|---|---|
| R3-001 | P2 | **CLOSED** | `service.py:150-163` 先 `managed.unlink(missing_ok=True)`，成功后才 `soft_delete`；unlink 失败 → `FONT_DELETE_FAILED` 且 row 仍 active；测试断言失败后 row 仍在 list、retry 成功、最终 list 为空；8 passed |
| R3-002 | P3 | **PARTIAL（P2）** | `core_service.py:5130-5134` 已按 code 映射：`FONT_NOT_FOUND`→`not_found`，其他→`"write"`；但 `"write"` 不在现有 category 集合（validation/not_found/conflict/internal）中，且没有 wire 负例测试；卡面 `:100` 写「write + retryable」，实际 `P16WireError` 无 retryable 参数，envelope `retryable=false`（R4-001/R4-002） |
| R3-003 | P3 | **CLOSED** | 卡面 Canonical 实际 **5 行**（EV-FN-001..005）并写清；日志 HEAD 为生成时工作树（收口提交前），保留可追溯 |

## 3. R4 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R4-001 | **P2** | `src/bootstrap/core_service.py:5130-5134`；`make_error_envelope` `:906-921`；卡 `:100` | **wire error category `"write"` 不在既有 taxonomy**：现有 category 为 `validation`/`not_found`/`conflict`/`internal`（backup 写失败用 `internal`）；客户端按 category 分支时无法识别 `write`。卡面还写「`FONT_DELETE_FAILED` → `write` + retryable」，但 `P16WireError` 不接收 retryable，envelope `retryable=false`，与文字不符。 | 把 `FONT_DELETE_FAILED` 映射到既有 `internal`（或经 DSH 裁决新增 `write` 并更新 taxonomy/客户端）；删除卡面「+ retryable」或明确 retryable 由 code 表达；补 wire 负例断言 category/retryable |
| R4-002 | P3 | `tests/core/test_font_wire.py`；`tests/storage/test_fonts.py` | **没有 wire 级 FONT_DELETE_FAILED 负例**：只测了 storage 失败码；`DeleteFontAsset` 的 error envelope category/retryable/row 状态未在 wire 层验证。 | 加 wire 测试：注入 stuck managed file → `FONT_DELETE_FAILED`、category 与 retryable 断言、row 仍 active |
| R4-003 | P3 | `verification/FEA-14-FONT-1/logs/pytest-font.log:1`；`logs/dotnet-app-tests.log` | 日志 HEAD 仍为生成时工作树（pytest HEAD=0b0733322，App HEAD=4ecb195f2 更早），非最终 r4 head；Canonical 5 行本身正确。 | 在最终 head 重生成日志，或注明生成时 HEAD/工作树；保持 Canonical 5 行 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 字体安装 | **MET** | 严格魔数+扩展、≤50MB/≤200 active、受管复制、sha256、幂等、typed 错误；weight/style/display_name limitation 已登记 |
| AC2 删除 | **MET（P2 wire category）** | 正常：soft delete + 删除受管副本 + 源文件保留；失败：row active 可重试；不存在/已删 typed `FONT_NOT_FOUND`；wire category 问题见 R4-001 |
| AC3 列举/刷新 | **MET（P3）** | wire P1 `{}`、无 family/weight 过滤（FONT-2 limitation）；list 排除 deleted；refresh available/failed；内部 family 参数保留 |
| AC4 迁移无损 | **MET** | v11 additive；v1–v10 不变；regression-v11 **1235 passed** |
| AC5 契约/门禁 | **MET（P2/P3）** | inventory 65/72、pins 18/18、C-07 v1.4 `8d92a32f…`；error category 与卡面 retryable 描述见 R4-001 |
| AC6 证据 | **MET（P3）** | 8 passed、App 874/0/11、1235 回归、pins/API、Canonical 5/5；日志 HEAD 见 R4-003 |

## 5. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 14:32:32 → 14:32:36 | PASS（3 warnings：11 非终态 / STATUS 3166 B·31 L / PLAN 6994 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-FONT-1.md` | 14:32:32 → 14:32:36 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 14:32:32 → 14:32:36 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 14:32:32 → 14:32:36 | `OK: rendered counts match FEA-C07 doc`；合计 72 | **0** |
| 5 | `python -m pytest tests/storage/test_fonts.py tests/core/test_font_wire.py -q` | 14:32:32 → 14:32:33 | **8 passed** | **0** |
| 6 | v11 regression（日志） | 14:24:17 | **1235 passed**，EXIT 0 | **0** |
| 7 | App.Tests 全量（日志） | 14:14:54 | **874 passed / 0 failed / 11 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 14:31:57 / 14:32+ | 两次均 **clean**；HEAD 均 `2bec370e7…` | — |
| 9 | 范围/Canonical | 14:32+ | 6 文件全部 ⊆ allowed（OUT=0）；Canonical **5/5** sha256 匹配 | — |

## 6. NOT_RUN

- 真实字体渲染/随包字体、商业字体元数据准确性、Fluent 设置页字体 UI：NOT_RUN。
- 真实大文件/占用文件/并发导入：仅单元测试，未做真实资源压力。
- 未重跑 Core/App 全量；采用 regression-v11 与 App 日志。

## 7. 处置建议

1. **R4-001（P2）**：`FONT_DELETE_FAILED` category 改用既有 `internal`（或 DSH 明确新增 `write` 并更新 taxonomy）；删卡面「+ retryable」或写清 retryable 由 code 表达；补 wire 负例。
2. R4-002/R4-003（P3）：wire 失败负例；最终 head 重生成日志或注明 HEAD。
3. AC1/AC2/AC3/AC4/AC5/AC6 均已有主证据；修 R4-001 后可收口。

## 8. 审查者声明

本报告由未参与 FEA-14-FONT-1 实现的独立上下文子 agent 出具（续接 r1–r3；历史报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/日志/逐行核对；未执行项在 §6 记 NOT_RUN。
