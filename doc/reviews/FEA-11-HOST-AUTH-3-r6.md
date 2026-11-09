# FEA-11-HOST-AUTH-3 实现 Review r6（独立上下文只读子代理 · 收口终审）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、证据生成或卡面起草 |
| reviewer_kind | `subagent`（DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读 + 允许的实测：read/grep、只读 git、`check.ps1`（默认 + `-TaskPath`）、`verify_pins.ps1`、`generate_api_inventory.py --check`、聚焦 pytest、**全量** Canonical Evidence 路径/sha256 核验、wirelog JSON 解析。**未重跑** `crash-ack.ps1`（会写 `verification/…/crash/<run-id>/`，越出单文件写权限）；未改源码/测试/契约/证据；未 commit/push |
| 被审 head | **`874c54275`**（`main`，clean；`integration_commit`=`e9ffad62c`；base `e9ab2ef7c`） |
| **verdict** | **`changes_requested`** |
| **CLEARED FOR DONE** | **否** |

## 0. 一句话结论

r5 的 4 项文档 blocking 中 **3 项已闭合**：AC-H3-2 已改为「脱敏器命中面 0 命中 + 归档 signature 重脱敏」的精确措辞；`crash-ack.ps1` 已在归档后自动调用 `redact_signature.py`；README head 已由 `c20145bf2` 修正为门禁实际运行 head `caaaddc53`；lifecycle 已由 `874c54275` 认领。**但「卡 `:77` 1810 → 1811」未落到 AC 行**：AC-H3-6 仍写 **1810**，而 `logs/dotnet-full-console.log` 8 项目合计 **1811**、README `:18` 与 Closeout `:180` 均写 1811。该数字自 `28417176b` 起未更新，r5 已明确列为 blocking，故 r6 不能 CLEARED。

## 1. 门禁（本轮亲自执行，2026-11-10，head `874c54275`）

| 门禁 | 命令 | 结果 | EXIT |
|---|---|---|---|
| 治理（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | `PASS (3 warnings)`（当前 Task=SRC-6） | **0** |
| 治理（指定卡） | `... check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | `PASS (3 warnings)` | **0** |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；`C17 cdeee4872e29` | **0** |
| API 清单 | `python tools/generate_api_inventory.py --check` | 无 diff | **0** |
| 聚焦 pytest | `python -m pytest tests/fea11 tests/core/test_core_service.py -q` | `245 passed, 9 warnings in 12.73s` | **0** |
| 工作树 | `git status --short` | 空（本文件写入前） | — |
| diff 范围 | `git diff --name-only e9ab2ef7c..874c54275`（84 路径）逐条比对 19 条 allowed_paths + 2 glob | `outside=0` | — |
| 冻结面 | 同上 diff，对 C-17 三载体 + C-07 + 6 个「不得改动」文件 | **空**（C-17 与 17 pin 零变化） | — |
| 证据完整性 | 解析卡 Canonical Evidence 全部 63 行 → `Get-FileHash` | `ROWS=63`、`MISSING=0`、`SHA_MISMATCH=0` | — |

## 2. r5 blocking 逐条判定

| r5 项 | 判定 | 依据 |
|---|---|---|
| **R-r2-03 收口**：卡 AC-H3-2 措辞 | **FIXED** | 卡 `:73` 已改为「脱敏器命中面（敏感键/Bearer/sk- 形态）0 命中，归档 wirelog 的裸 `signature` 由 `tools/redact_signature.py` 重脱敏（10 条 → `[redacted]`，0 明文）」；旧措辞「脱敏 0 命中」已不存在 |
| **R-r2-03 收口**：`crash-ack.ps1` 接入脱敏器 | **FIXED** | `tools/crash-ack.ps1:286-287` 在归档 `wire-redacted.ndjson` 后调用 `python …/tools/redact_signature.py $archive`，注释说明 C-16 §7 不覆盖裸 `signature` |
| **卡 `:77` 1810 → 1811** | **OPEN** | 卡 `:77` 仍为「.NET **1810 passed** / 0 failed / 109 skipped」；`logs/dotnet-full-console.log` 逐项目 838+21+31+167+117+312+72+253=**1811**、skipped 11+24+74=**109**；README `:18`、Closeout `:180` 均写 1811；`git log -S 1810` 显示该行自 `28417176b` 起未再更新。`e9ffad62c` message 自称修 1811，实际只改 Closeout/README，未触及 AC 行 |
| **R-r1-05 残余**：README 最终 head | **FIXED（残余 P3）** | README `:11`、`:35-41` 的 head 列已由 `c20145bf2` 改为 `caaaddc53`（门禁实际运行 head，与 r5 取证一致）；但 `:31` 标题仍称「最终 head」，而 `delivery_head`=`e9ffad62c`、tip=`874c54275`，口径宜改为「门禁运行 head（此后仅文档提交）」 |
| **R-r1-12 lifecycle** | **FIXED** | `874c54275` 同时改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`；STATUS 当前 Task 指向 `FEA-13-SRC-6` **proposed**（非终态，符合预期）；PLAN 中 HOST-AUTH-3=`done`、`READY 节点：无`（合法，SRC-6 仍 proposed）；`check.ps1` 默认与指定卡均 PASS |

## 3. 收口规范化

| 项 | 判定 | 依据 |
|---|---|---|
| `status: done` | 通过 | 卡 front-matter |
| `canonical_evidence_status: complete` | 通过 | 同上 |
| `resource_closeout_status: complete` | 通过 | 同上 |
| `integration_commit` / `delivery_head` | 通过 | 均为 `e9ffad62c`；`874c54275` 为收口文档提交，语义合理 |
| Canonical Evidence 63 行 | **通过（全量核验）** | 63/63 路径真实存在且 sha256 与文件逐条一致（`MISSING=0`、`SHA_MISMATCH=0`），覆盖 README、`logs/`（含 attempt12/negative/dotnet-full/pytest-full）、`crash/` 5 归档 ×6 文件、`mutations/M1…M6`、`tools/`（check_gate、crash-ack、redact_signature） |
| Closeout 生命周期叙述 | **P3** | `:179` 称「全部经 **5 轮**独立上下文 Review（r1→r5）收敛」，但 r5 verdict 为 `changes_requested`；收敛实际依赖 r6。建议改为「r1→r5 + r6 收口」，避免夸大 |
| `reviewer:` 字段 | **P3** | 仍为「待指派（必须独立上下文）」，与 `status: done` 及其 r1→r5 实存 Review 不一致 |
| EV-H3-060 | **P3** | 证据项为 `tools/__pycache__/redact_signature.cpython-314.pyc`（生成物，跨 Python 版本不可复现）；建议移除，保留 `.py` 源（EV-H3-063） |

## 4. 证据真实性（独立复算）

| 项 | 结果 |
|---|---|
| `logs/crash-driver-attempt12.log` | **10 个 CHECK 全 =1**（含 `page_bindings_fields_unchanged`、`journal_present`）、`CRASH_POINT=PASS`、头 `EXIT=0`，值与 `CHECK` 行一一对应 |
| `logs/crash-driver-negative.log` | `phase=replace source_replaced=1` → `CHECK negative_typed_refusal=1 code=SOURCE_ACCESS_DENIED` → `CRASH_POINT=NEGATIVE_PASS`、头 `EXIT=0` |
| 归档 wirelog | 5 份 `wire-redacted.ndjson`：**明文 `signature` = 0**，全部行 `ConvertFrom-Json` 通过（`BAD_JSON=0`） |
| .NET 全量 | `dotnet-full-console.log` 8 项目：passed **1811**、failed **0**、skipped **109**，逐项目 EXIT=0 |
| pytest 全量 | `pytest-full.log` 记录 3468/0/10，sha256 与卡一致；本轮未重跑全量（聚焦 245 passed） |
| 变异 | M1–M6 日志均在证据表内且 hash 一致 |

## 5. AC 复核

| AC | 判定 | 依据 |
|---|---|---|
| **AC-H3-1** | **MET** | `verify_pins` 18/18；C-17/C-07/禁改文件 diff 空；工作树 clean |
| **AC-H3-2** | **MET** | 措辞已精确到脱敏器命中面与归档重脱敏；归档 0 明文；驱动已接线 |
| **AC-H3-3** | **MET（P3）** | 7 例 typed 拒绝齐备，卡头已写「7 例（含多 baseline）」；括号内仍只列 6 条 reason→code（registry-missing 与 multi-baseline 均为 `SOURCE_ACCESS_DENIED`，未分列） |
| **AC-H3-4** | **MET** | 正例 10 CHECK 全 1；反例 `SOURCE_ACCESS_DENIED`/`NEGATIVE_PASS`；两日志头 `EXIT=0` |
| **AC-H3-5** | **MET** | M1–M6 证据齐备且 hash 一致（本轮复核到文件级；变异 RED 细节沿用 r4/r5） |
| **AC-H3-6** | **PARTIAL** | 门禁全绿、diff ⊆ allowed、冻结面零变化、工作树 clean 均成立；但 AC 行仍写 1810，与 1811 实测/README/Closeout 矛盾，且「在最终 head 重跑」的全量实测实际发生在 `bb24cb99a`，表述亦不精确 |

## 6. 结论

- **verdict：`changes_requested`**；**未 CLEARED FOR DONE**。
- **blocking（1 项，纯文档、无需改生产代码/证据）**：
  1. `doc/tasks/FEA-11-HOST-AUTH-3.md:77` AC-H3-6 的 **1810 → 1811**，并与 `Closeout:180`、`README:18`、`logs/dotnet-full-console.log` 的 8 项目汇总一致；建议同时把「在最终 head 重跑」改为「在门禁运行 head `caaaddc53` 重跑（此后仅文档/证据工具提交）」。
- **非 blocking、done 前宜收口（P3）**：Closeout「5 轮收敛」口径（r5 实为 changes_requested，宜写 r6）；`reviewer:` 字段；README `:31` head 标题口径；EV-H3-060 的 `.pyc` 生成物；AC-H3-3 第 7 例码的分列。
- **口径**：本轮未重跑 `crash-ack.ps1`（写权限约束），AC-H3-4 依据归档日志与程序集/产物独立复算；本报告只写此文件，不构成对实现/契约的批准，不改变任何 pin。完成上述一行修正后，可提交 r6 复审并据此翻 done。

---

审查者身份与来源：独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`，2026-11-10 派发；未参与该 Task 实现/返修/证据生成）。报告路径：`doc/reviews/FEA-11-HOST-AUTH-3-r6.md`。
