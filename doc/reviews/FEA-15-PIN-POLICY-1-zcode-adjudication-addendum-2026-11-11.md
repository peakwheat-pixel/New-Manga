---
task_id: FEA-15-PIN-POLICY-1
adjudicator: ZCode CLI（延续最终 adjudication session）
adjudication_session_id: sess_39001b09-6b67-417a-b81d-85f3e62ec80d
addendum: closeout-empty-task-gate
input_head: d2b1f6a0fa08fb6c9020e7a06107ba3b7a52a3c0
decision: OPTION_2_DONE_WITH_DISCLOSED_DEFAULT_GATE_LIMITATION
---

# 最终裁决 Addendum：收口期治理冲突

## 裁决身份与输入 HEAD 更正

本 Addendum 延续 ZCode 最终裁决 session `sess_39001b09-6b67-417a-b81d-85f3e62ec80d`，区别于 Review `sess_08fc30ae-10e9-48c5-8029-c3adb02fe9a5` 和 release `sess_236d9541-8358-45f0-9318-4844a86a767e`。CLI 调用前仓库实测 HEAD 为 `d2b1f6a0fa08fb6c9020e7a06107ba3b7a52a3c0`；工作树有 4 个 closeout 文档修改：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`、`doc/tasks/FEA-15-PIN-POLICY-1.md`。Addendum 首版沿用了旧 HEAD `a3db215...`；ZCode 已更正并确认本裁决选择不变。

## 核验事实

`tools/governance/check.ps1` 的结构如下，且实际运行结果吻合：

- 第 192–197 行：default 模式必须从 STATUS 解析 `- 当前 Task：…（tasks/….md）`；无指针时输出 `STATUS 未提供可解析的当前 Task 指针。`。
- 第 246–249 行：无解析路径时再报 `当前 Task 文件不存在：`。
- 第 632–633 行：若 STATUS 指针指向终态 Task，则报 `STATUS 仍指向终态 Task：done`。
- 第 624–656 行：显式 `-TaskPath` 可在无 STATUS 指针时校验 done 卡；实际 `check.ps1 -TaskPath doc/tasks/FEA-15-PIN-POLICY-1.md` 为 PASS。
- 第 743 行：done Task 必须有 `integration_commit`，故两步提交中 A 暂存 `pending` 时该 TaskPath 校验预期失败。

结论：default checker 没有表达合法“无 Active Task”空窗的模式；这是过度严格的表达缺口，而非放行漏洞。本 Task 禁止改 checker，不能在当前范围修复。

## 三选项裁决

**选择 (2)：Task 置 `done`、STATUS 清空终态 Task 指针；default `check.ps1` 的 `EXIT=1` 作为明确披露的 checker limitation 接受。空窗期改用 `-TaskPath` 门禁。**

- 拒绝 (1) 保留 `approved/current`：它会制造永远悬置的伪 current，且终态前指针检查不允许此状态。
- 接受 (2)：STATUS 如实表达无 Active Task；default EXIT 1 是保守侧失败信号，`-TaskPath`、18 pins、API 门禁仍可独立校验。
- (3) 作为后续候选登记，但不释放 Task、不授权修改 checker。修复或释放 successor 均需另行冻结范围。

该裁决部分取代上一轮“收口五项 gates 均 EXIT 0”的预期；其余四项政策裁定、Review 发现处置和禁止边界不变。

## 两步集成与修订版门禁

1. 提交 A：Task `status: done`、AC1–AC3 均 `MET`、`resource_closeout_status: complete`；`integration_commit: pending`；清空 STATUS 当前 Task 指针、Plan 节点设 done、重生成 Ledger。记录 default 与 TaskPath 的预期失败，不将其写成 PASS。
2. 提交 B：把 A 的实际 commit hash 回填到 `integration_commit`；本裁决与 Addendum 均按 Canonical Evidence 记录 commit 和 SHA-256。
3. clean HEAD 上保存五项 gates 的实际输出与 generation HEAD：

| 命令 | 预期 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | `EXIT=1`，仅上述两条已知无当前 Task 错误；记录为 limitation，绝不标 PASS。 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-POLICY-1.md` | `EXIT=0`；若仍为 `integration_commit: pending`，记录预期失败，pinbackfill 后重跑。 |
| prior TaskPath `FEA-15-PIN-EOL-GOV-1.md` | PASS，`EXIT=0`。 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 18/18 PASS，`EXIT=0`。 |
| `python tools/generate_api_inventory.py --check` | `1/79/6=86`，`EXIT=0`。 |

空窗期治理检查一律指定 `-TaskPath`。default EXIT 1 必须作为 limitation 记录，不伪装为 PASS。

## 文档要求、授权边界

- STATUS 使用不包含 Task 文件路径的空窗声明，例：`当前 Task：无（S5 收口空窗；default gate EXIT 1 为已披露 checker limitation，用 -TaskPath）。`；另更新“刚收口”摘要。
- Closeout Record 记录 default gate limitation、Review finding #1/#2/#3 的处置、两步 `integration_commit` pinbackfill 与 generation HEAD。
- no-current-task checker 模式登记为后续候选；本 Addendum 不释放 successor，不授权改 `check.ps1`、`verify_pins.ps1`、`task_ledger.py`、Task 模板、`.gitattributes`、历史 pins、契约、源码、资源，也不授权 push。
- 本裁决不请求人工批准；收口按此 Addendum 执行。