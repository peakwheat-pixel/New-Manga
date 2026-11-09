# FEA-11-HOST-AUTH-3 证据索引（崩溃恢复 · C-17 v1.2）

- Task：`FEA-11-HOST-AUTH-3`（跨进程崩溃恢复的 grant 语义）
- Base：`e9ab2ef7c`（scope 冻结点）；C-17 v1.2 已冻结（pin `cdeee487…`，18/18）
- 日期：2026-11-10；批次：`fea-11-host-auth-3`

## 结论状态

| 项 | 结果 |
|---|---|
| `crash-ack.ps1` 两阶段驱动 | **PASS**（`logs/crash-driver-attempt12.log`，EXIT 0，head `caaaddc53`） |
| 三重防伪 | host PID 不同 / Core session 不同 / 重铸 grant ∉ journal（`fresh_grant=1`） |
| 进程死亡证明 | park 进程树 **12–13 PID（含 1 Python sidecar）** 枚举 → kill 后 30s 轮询断言全灭（`pids-before.txt`/`pids-after.txt`） |
| 数据安全 | `source_sha256_unchanged=1`、`rows_unchanged=1`（bindings/publications） |
| gate | `gates_open=1`（`check_gate.py` 实查 `read_binding_publications.read_gate`，0 pending） |
| 幂等 | `second_call_idempotent=1`（二次 recover 0 新 wire 帧） |
| **崩溃反例** | `-Negative` 模式：phase 间替换源文件 → **`SOURCE_ACCESS_DENIED` typed 拒绝**（`logs/crash-driver-negative.log`，EXIT 0） |
| 全量基线（门禁运行 head `caaaddc53` 重跑） | pytest **3468/0/10**（`logs/pytest-full.log`）；.NET 8 项目 **fresh build 1811/0/109**（`logs/dotnet-full-console.log` 与 `logs/dotnet-*.log`） |

## 断言全部由事实计算（P0 修复）

驱动脚本 `tools/crash-ack.ps1` 的 PASS 行由 **10** 个 `CHECK` 结果拼接，**不是常量**：

```
CHECK commit_digest_match / distinct_host_pid / distinct_core_session /
      source_sha256_unchanged / rows_unchanged / gates_open /
      second_call_idempotent / fresh_grant /
      page_bindings_fields_unchanged / journal_present  → 全部 =1
```

## 逐项门禁记录（门禁运行 head = `caaaddc53`；`delivery_head` = `e9ffad62c`）

| 步骤 | 命令 | 时间（+08:00） | head | EXIT |
|---|---|---|---|---|
| 治理默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | 01:2x | `caaaddc53` | 0 |
| 治理指定卡 | `... check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | 01:2x | `caaaddc53` | 0 |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 01:2x | `caaaddc53` | 0（18/18） |
| API 清单 | `python tools/generate_api_inventory.py --check` | 01:1x | `caaaddc53` | 0 |
| 全量 pytest | `python -m pytest -q` | 00:5x | `bb24cb99a` | 0（3468/0/10） |
| 崩溃正例 | `crash-ack.ps1`（gated） | 01:0x | `caaaddc53` | 0（10 CHECK） |
| 崩溃反例 | `crash-ack.ps1 -Negative`（gated） | 01:09 | `caaaddc53` | 0（NEGATIVE_PASS） |

## 崩溃证据归档（每次运行）

`crash/<run-id>/`：`park.json`、`recover.json`、`pids-before.txt`、`pids-after.txt`、`library.db`、`wire-redacted.ndjson`（`signature` 已由 `tools/redact_signature.py` 脱敏）。
说明：`kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt` 以 `park.json`/`recover.json` 的内嵌字段（`source_sha256`、`db_counts`、`wire_lines`、`second_call_frames`）表达，未单独成文件；`4a18…`/`8e63…` 为负例/早期运行归档。

## 变异判别

| 变异 | 判别 | 结果 |
|---|---|---|
| M1 复用 journal grants | 驱动 recover 阶段 → `SOURCE_ACCESS_DENIED`（"grant is not registered"） | **RED**（`mutations/M1-journal-grant-reuse.log`，EXIT 12） |
| M2 移除 host-control 注册 | `test_source_command_parity.py` | **RED** |
| M3 投影写库 | fake store 零写断言 | **RED** |
| M4 删 digest 校验 | STALE 用例 | **RED** |
| M5 删 applied 前置 | 拒绝矩阵例 1 | **RED** |
| M6 猜 source_kind | 拒绝矩阵例 3 | **RED** |

## 复现命令

```powershell
$env:NEWMANGA_FEA11_IPC='1'; $env:NEWMANGA_BUILD_PYTHON='C:/Python314/python.exe'
pwsh -NoProfile -File verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1            # EXIT 0 = PASS（正例）
pwsh -NoProfile -File verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1 -Negative  # EXIT 0 = NEGATIVE_PASS（反例）
python -m pytest tests/fea11 -q
```

## 说明

- 恢复需要 **恰好一个 readable root**（生产语义：root == 用户选中的源）；多 root fail-closed。
- 源路径不可猜：`source_kind` 来自 `source_list_scan_targets`，`version/entries` 来自物化投影（ZCode 裁决 E′）。
- 契约字节零改动；`verify_pins` 18/18。
