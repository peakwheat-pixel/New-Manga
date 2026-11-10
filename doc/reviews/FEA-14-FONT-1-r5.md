---
task_id: FEA-14-FONT-1
reviewer: fresh 独立上下文子 agent（续接 r1–r4；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 2bec370e7
reviewed_head: 8e39bb72c
decision: approved
---

# Review：FEA-14-FONT-1（r4 处置后复核，r5）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `8e39bb72ce9b8f188fa5910b184170cdcc0854fc`**。审查开始 `2026-11-10T14:34:13+08:00`、结束 `14:34+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`2bec370e7..8e39bb72c`，**5 文件**：`core_service.py`（category internal）、卡面、README、`pytest-font.log`、r4 报告。全部 ⊆ FONT-1 allowed_paths（OUT=0）。
- 卡面 base 24637d1b4；无新建 Core/wire/契约/DDL 变更。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-FONT-1-r5\`。

## 1. 结论

**`approved`**（P0=0 / P1=0 / P2=0 / **P3=2**）。

R4-001 已关闭：`FONT_DELETE_FAILED` category 改为既有 **`internal`**，wire envelope 与 README AC2/卡面 r4 记录一致；r3 历史记录里的「write + retryable」措辞仍残留（P3 文档噪音）。R4-002/R4-003 已登记（wire 级失败负例缺口、日志 HEAD 为生成时工作树），不阻断。AC1–AC6 均 MET。

## 2. r4 findings 关闭判定

| r4 ID | r4 级别 | r5 判定 | 依据 |
|---|---|---|---|
| R4-001 | P2 | **CLOSED** | `core_service.py:5130-5134`：`not_found` vs `internal`，`"write"` 已删除；README AC2 写 `FONT_DELETE_FAILED`（category `internal`，行保持 active 可重试）；卡面 r4 记录同步，删除「+ retryable」 |
| R4-002 | P3 | **CLOSED（登记）** | wire 级 FONT_DELETE_FAILED 负例未补；卡面 r4 记录已登记（P1 不回 managed_path，无法定位受管文件；storage 已覆盖失败/重试） |
| R4-003 | P3 | **CLOSED（登记）** | 日志 HEAD 为生成时工作树，Canonical 5 行正确；卡面 r4 记录已登记，保留可追溯 |

## 3. R5 Findings（P3）

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R5-001 | P3 | 卡 `:100`（r3 处置记录） | r3 历史记录仍写「`FONT_DELETE_FAILED` → `write` + retryable」，与 r4/r5 的实际 `internal`/无 retryable 相反；历史记录未被标注为已过时，读者可能误读。 | 在该行加「已被 r4 修正为 internal」或删除/改写历史措辞；保持 r4 记录为准 |
| R5-002 | P3 | `verification/FEA-14-FONT-1/logs/pytest-font.log:1`；`logs/dotnet-app-tests.log`；`tests/core/test_font_wire.py` | `pytest-font.log` HEAD=`2bec370e7`（r4），App 全量日志 HEAD=`4ecb195f2`（更早），均生成于 r5 提交前；wire 层没有 FONT_DELETE_FAILED 负例。均为已登记 P3，不影响主证据。 | 最终 head 重生成日志或注明；后续补 wire 失败负例（需可注入 managed 路径或 wire 返回定位信息） |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 字体安装 | **MET** | 严格魔数+扩展、≤50MB/≤200 active、受管复制、sha256、幂等、typed 错误；weight/style/display_name limitation 已登记 |
| AC2 删除 | **MET** | 先删受管副本→成功 soft_delete；失败 `FONT_DELETE_FAILED`（category internal）、row active 可重试；不存在/已删 typed `FONT_NOT_FOUND`；源文件保留 |
| AC3 列举/刷新 | **MET** | wire P1 `{}`、无 family/weight 过滤（FONT-2 limitation）；list 排除 deleted；refresh available/failed；内部 family 参数保留 |
| AC4 迁移无损 | **MET** | v11 additive；v1–v10 不变；regression-v11 **1235 passed** |
| AC5 契约/门禁 | **MET** | inventory 65/72；`--check` EXIT 0；pins 18/18；C-07 UNFREEZE v1.4 `8d92a32f…`；error category internal |
| AC6 证据 | **MET（P3）** | 8 passed、App 874/0/11、1235 回归、pins/API、Canonical 5/5；日志 HEAD 见 R5-002 |

## 5. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 14:34:23 → 14:34:27 | PASS（3 warnings：11 非终态 / STATUS 3166 B·31 L / PLAN 6994 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-FONT-1.md` | 14:34:23 → 14:34:27 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 14:34:23 → 14:34:27 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 14:34:23 → 14:34:27 | `OK: rendered counts match FEA-C07 doc`；合计 72 | **0** |
| 5 | `python -m pytest tests/storage/test_fonts.py tests/core/test_font_wire.py -q` | 14:34:23 → 14:34:24 | **8 passed** | **0** |
| 6 | v11 regression（日志） | 14:24:17 | **1235 passed**，EXIT 0 | **0** |
| 7 | App.Tests 全量（日志） | 14:14:54 | **874 passed / 0 failed / 11 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 14:34:13 / 14:34+ | 两次均 **clean**；HEAD 均 `8e39bb72c…` | — |
| 9 | 范围/Canonical | 14:34+ | 5 文件全部 ⊆ allowed（OUT=0）；Canonical **5/5** sha256 匹配 | — |

## 6. NOT_RUN

- 真实字体渲染/随包字体、商业字体元数据准确性、Fluent 设置页字体 UI：NOT_RUN。
- 真实大文件/占用文件/并发导入：仅单元测试，未做真实资源压力。
- 未重跑 Core/App 全量；采用 regression-v11 与 App 日志。

## 7. 处置建议

1. R5-001（P3）：把 r3 历史记录的 `write + retryable` 标注为已被 r4 修正，或直接删除该措辞，避免与 r4 的 `internal` 冲突。
2. R5-002（P3）：最终 head 重生成日志或注明生成时 HEAD；wire 失败负例留 FONT-2/后续。
3. AC1–AC6 均 MET，可进入收口；真实渲染/UI 仍 NOT_RUN。

## 8. 审查者声明

本报告由未参与 FEA-14-FONT-1 实现的独立上下文子 agent 出具（续接 r1–r4；历史报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/日志/逐行核对；未执行项在 §6 记 NOT_RUN。
