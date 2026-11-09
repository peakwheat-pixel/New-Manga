# FEA-11-HOST-AUTH-3 实现 Review r5（独立上下文只读子代理 · 终审）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、证据生成或卡面起草 |
| reviewer_kind | `subagent`（DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读 + 允许的实测：read/grep、只读 git、`check.ps1`/`verify_pins.ps1`/`generate_api_inventory.py --check`、聚焦 pytest、内存内调用 `redact_text`、wirelog JSON 解析。**未重跑** `crash-ack.ps1`（会写 `verification/…/crash/<run-id>/`，越出单文件写权限）；未改生产源码/测试/契约；未 commit/push |
| 被审 head | **`caaaddc53`**（`main`，01:1x；r4 被审 head `c20145bf2`）；base `e9ab2ef7c` |
| **verdict** | **`changes_requested`** |
| **CLEARED FOR DONE** | **否** |

## 0. 一句话结论

**R-r2-03 的实质安全面已闭合**：5 份归档 wirelog 的 **10 条 `signature` 已全部为 `[redacted]`、0 条明文**，每份 22 行仍为合法 JSON；`tools/redact_signature.py` 为纯正则、内容幂等（二次调用文本不变）。**但 r5 验收的文档子项未做**：卡面 AC-H3-2（`:73`）仍是旧措辞「…、**脱敏 0 命中**。 `<<MET>>`」，未改为「脱敏器命中面 0 命中 + 归档 signature 重脱敏」；AC-H3-6（`:77`）仍写 **1810**（实际 **1811**），与修复提交 message、README、`dotnet-full-console.log` 均不一致。故 **R-r2-03 = PARTIAL**，不能判 done。

## 1. 门禁（本轮亲自执行，2026-11-10 01:15–01:19 +08:00，head `caaaddc53`）

| 门禁 | 命令 | 结果 | EXIT |
|---|---|---|---|
| 聚焦 pytest | `python -m pytest tests/fea11 tests/core/test_core_service.py -q` | `245 passed, 9 warnings in 16.31s` | **0** |
| 治理（指定卡） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | `Governance check: PASS (3 warnings)` | **0** |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；`C17 cdeee4872e29` | **0** |
| API 清单 | `python tools/generate_api_inventory.py --check` | 无 diff | **0** |
| 工作树 | `git status --porcelain` | 空（本文件写入前） | — |
| diff 范围 | `git diff --name-only e9ab2ef7c..caaaddc53`（83 路径）逐条比对 17 条 allowed_paths + 3 glob | **outside=0** | — |
| 冻结面 | 同上 diff，对 C-17 三载体 + C-07 + 6 个「不得改动」文件 | **空**（C-17 与 17 pin 零变化） | — |

## 2. 逐条判定

| 项 | 判定 | 依据 |
|---|---|---|
| **R-r2-03** 归档 signature 明文 | **PARTIAL** | ①**已脱敏**：`crash/<run-id>/wire-redacted.ndjson` 5×2 个 `signature` 字段值**全部 `[redacted]`，明文=0**；每份 22 行 `json.loads` 全通过（`bad_json=0`）。②**工具**：`redact_signature.py` 纯正则、无随机/无外部输入 → 确定性；内存内对合成转义+普通样例与 `588f…` 实际文本二次调用，`fixed_point=True` → **内容幂等**；但正则会把已脱敏的 `[redacted]` 再算一次命中，二次运行 `count=2/文件（合计 10）` 并重写同字节，**计数不幂等**（P3 误导）。③**未接入驱动**：`tools/crash-ack.ps1:282` 仅 `Copy-Item wire.ndjson → wire-redacted.ndjson`，**未调用**脱敏器 ⇒ 重跑 gated 正例会再次生成明文归档（P2 可复现性缺口）。④**卡面措辞未改**：`doc/tasks/FEA-11-HOST-AUTH-3.md:73` 仍是「脱敏 0 命中。 `<<MET>>`」，r5 要求的「脱敏器命中面 0 命中 + 归档 signature 重脱敏」不存在（全文件检索 `signature`/`C-16` = 0 命中；README 仅在 `:45` 记一句工具说明） |
| **R-r1-05** README 逐项 | **FIXED（残余 P3）** | `README.md:31-41` 已新增「步骤/命令/时间/head/EXIT」五列表（7 行，EXIT 全 0）；`:45-46` 已说明 `kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt` 以 `park.json`/`recover.json` 内嵌字段表达、未单独成文件。残余：head 列写 `c20145bf2` 而非终审 `caaaddc53`；时间仅 `01:2x`/`00:5x`；全量 pytest 行 head `bb24cb99a`（commit 01:07:26）与 `pytest-full.log` 记录时间 `00:45:31` 时序矛盾 |
| **R-r1-12** lifecycle | **OPEN** | `git log e9ab2ef7c..caaaddc53 -- doc/STATUS.md doc/REBASELINE_PLAN.md doc/TASK_LEDGER.md` 仅 `4d787ffcf`（scope 冻结）、`bfa5016c7`、`7e2d0c241`（均为实现轮），**无 DSH lifecycle 提交**；卡 `status: in_progress`、Closeout Record 仍为「未开始」 |
| **卡面数字/矩阵/AC** | **不一致** | .NET 实测 **1811**（838+21+31+167+117+312+72+253，`dotnet-full-console.log` 逐项目 `EXIT=0`），卡 `:77` 仍写 **1810**；`caaaddc53` message 自称「…矩阵 7 例、1811」但实际只改了 AC-H3-3 一行。矩阵 **7 例与测试一致**（`Fea11HostAuthTests.cs:948-1022`：STALE/UNAVAILABLE/ACCESS_DENIED/CORE_UNAVAILABLE/GRANT_REVOKED/registry-missing ACCESS_DENIED/multi-baseline ACCESS_DENIED 共 7 个 typed 拒绝），但卡 `:74` 括号内只列 6 条 reason→code，第 7 例的码未列出（P3）。「AC 全 MET」因此不成立（AC-H3-2 措辞、AC-H3-6 数字） |
| 崩溃正例 | **PASS** | `crash-driver-attempt12.log`：**10 个 CHECK 全 =1**（含 `page_bindings_fields_unchanged`、`journal_present`）、`CRASH_POINT=PASS`、头 `EXIT=0`；`CHECK` 值来自现场测量 |
| 崩溃反例 | **PASS** | `crash-driver-negative.log`：`phase=replace source_replaced=1` → `CHECK negative_typed_refusal=1 code=SOURCE_ACCESS_DENIED` → `CRASH_POINT=NEGATIVE_PASS`、头 `EXIT=0` |

**计数：FIXED=1（R-r1-05）/ PARTIAL=1（R-r2-03）/ OPEN=1（R-r1-12）；另有卡面数字不一致 1 项。**

## 3. AC 复核

| AC | 判定 | 依据 |
|---|---|---|
| **AC-H3-1** | **MET** | `verify_pins` 18/18；C-17/C-07/禁改文件 diff 空；工作树 clean |
| **AC-H3-2** | **PARTIAL** | 安全实质已达标（10 条→0 明文、JSON 合法），但卡面仍以旧措辞「脱敏 0 命中」记 `<<MET>>`，且脱敏器未接入驱动 |
| **AC-H3-3** | **MET** | 7 例 typed 拒绝（含 multi-baseline）测试齐备；卡面括号未列第 7 例的码（P3） |
| **AC-H3-4** | **MET** | 正例 10 CHECK 全 1；反例 `SOURCE_ACCESS_DENIED`/`NEGATIVE_PASS`；两日志头 `EXIT=0` |
| **AC-H3-5** | **MET** | M1–M6 日志齐备（本轮未复核细节，沿用 r4） |
| **AC-H3-6** | **PARTIAL** | 门禁全绿、diff ⊆ allowed、冻结面零变化、工作树 clean 均成立；但「全量（在最终 head 重跑）1810」与实际 1811 不符，README head 列亦非最终 head |

## 4. 结论

- **verdict：`changes_requested`**；**未 CLEARED FOR DONE**。
- **blocking（文档层，无需改生产代码）**：
  1. **R-r2-03 收口**：把卡 `:73` AC-H3-2 改为「脱敏器命中面 0 命中 + 归档 signature 重脱敏（10 条→0 明文）」，删除「脱敏 0 命中」旧措辞；README 增一句复现命令（驱动后运行 `python verification/FEA-11-HOST-AUTH-3/tools/redact_signature.py verification/FEA-11-HOST-AUTH-3/crash`），并视需要在 `crash-ack.ps1` 归档后自动调用脱敏器。
  2. **卡 `:77` 1810 → 1811**（并与 `dotnet-full-console.log` 的 8 项目汇总一致）。
- **非 blocking、done 前宜收口**：R-r1-12（DSH lifecycle 提交认领，`STATUS`/`REBASELINE`/`LEDGER`；卡 `status` 与 Closeout）、R-r1-05 残余（README head/时间改为最终 head 与准确时刻）、脱敏器二次运行计数、卡 `:74` 第 7 例码。
- **口径**：本轮未重跑 `crash-ack.ps1`（写权限约束），AC-H3-4 依据归档日志、脚本与程序集/产物独立复算；本报告只写此文件，不构成对实现/契约的批准，不改变任何 pin。
