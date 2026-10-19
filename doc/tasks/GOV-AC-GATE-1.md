---
id: GOV-AC-GATE-1
title: AC 状态的机械门禁（machine-readable AC gate）
kind: governance
governance_version: 3
status: in_review
approval: codex_r20_followup_not_yet_released
suggested_owner: codex
owner: codex
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: null
delivery_head: fbf459f28941f3760366d5f8e581f8e8ae79ce18
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-AC-GATE-1
---

# GOV-AC-GATE-1：AC 状态的机械门禁

## 来源与目标

Codex r20 §2.6 分析了本会话中三次「交付方在自己的 Task 里犯了它正在治理的那类错误」：

| 例 | 具体故障 |
|---|---|
| 审计「未实测汇总」却产出未实测汇总 | 证据与结论不匹配 |
| 修「CRLF 破坏 pin」却自己 CRLF 破坏 pin | 字节/环境假设未在最终工作树验证 |
| 给漏勾 AC 补勾而自己 AC1–AC4 漏勾 | **交付状态清单未执行自检** |

r20 的判断：**这是同一更高层模式的重复，但不是同一种具体故障**；
共同描述是「Agent 执行治理规则时，没有把自身产物纳入检查集合」。
它明确否定了「有意豁免自己」这种动机推断。

**第三个例子是本 Task 要解决的**：AC 漏勾是**检查器可以机械发现**的，
因为它不需要理解语义，只需要知道「进入了 in_review，却有 AC 既未勾选也未标注阻塞」。

r20 的原话：

> **建议在协作协议加入机械 AC gate，值得做。** 单靠「所有已完成 AC 必须勾选」不够机械，
> 因为检查器无法从自由文本推知某项是否已完成。可采用最小结构约定：
> 进入 `in_review` 时每个 AC 必须有显式 machine-readable 状态
> （如 `MET` / `PARTIAL` / `BLOCKED`…）。
>
> 这样能直接拦住本 Task 的 4 个已完成 AC 未勾选问题，也能防止把阻塞项勾成完成；
> 它不能独自发现「测试没有实际运行却写成 PASS」或错误的字节假设，
> 仍需相应的执行记录/哈希验证 gate。

## Acceptance Criteria

- [x] **AC1 定义状态词汇表**：在 `doc/09_COLLABORATION.md` 中定义 AC 的显式状态枚举 <<MET>>
  （至少 `MET` / `PARTIAL` / `BLOCKED` / `NOT_APPLICABLE`），并说明各状态的**语义与证据门槛**。
  必须明确：`BLOCKED` 与 `PARTIAL` **不得**写成 `MET`；`MET` 必须有可指向的证据。
- [x] **AC2 定义书写形式**：给出 AC 行末状态标记的**确切语法**（必须能被正则稳定匹配， <<MET>>
  且不破坏既有 Markdown 渲染）。必须说明**既有 Task 的兼容策略**——
  已 `done` 的历史 Task 是否回溯补标？若不回溯，如何区分「未标注」与「标注为 MET」？
- [x] **AC3 实现检查器 gate**：在 `tools/governance/check.ps1` 中实现： <<MET>>
  Task 状态为 `in_review` 或**终态**时，每个 AC 必须
  **①已勾选**，或 **②带有非 `MET` 的显式状态标记并附原因**。
  违反时报 error 并指出具体 AC。
  **不得**因新增该 gate 而使既有 PASS 的 Task 变红——若会，须在 AC4 中给出兼容方案。
- [x] **AC4 回归测试**：用夹具（**不得写进 `doc/tasks/`**）覆盖至少四种情形： <<MET>>
  ① 全部勾选 → PASS；② 有未勾且无标 → FAIL；
  ③ 有未勾但标 `BLOCKED` + 原因 → PASS；④ 已勾但标 `BLOCKED` → FAIL（矛盾状态）。
  夹具路径须使用系统临时目录，并在测试中断言 `doc/tasks/` 未被触碰。
- [x] **AC5 全库回归**：对当前全部 Task 跑一遍新检查器，**如实记录**哪些 Task 会因此变红， <<MET>>
  并逐个判断是「真实缺陷」还是「兼容性问题」。**不得为了让全库变绿而放宽 gate。**
- [ ] **AC6 交付与 Review**：改动协议与检查器；生成 Handoff；由 Antigravity 对固定 <<PARTIAL: Handoff 已交付，独立 Review 待进行>>
  delivery head 独立 Review。Review 必须实际构造违反情形验证 gate 生效。

## 允许修改范围

- `doc/09_COLLABORATION.md`：仅 AC 状态词汇与书写形式章节。
- `tools/governance/check.ps1`、`tools/governance/tests/`。
- `verification/GOV-AC-GATE-1/`。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- 不改任何 Task 的 AC 内容或勾选状态。
- 不把 gate 放宽到「只要有任意文字就不报错」——那等于没有 gate。
- 不为让既有 Task 变绿而豁免它们；若变红，如实记录并交裁定。
- 不改 `src/`、`apps/`、`tests/`。

## 测试与验证

```powershell
pwsh -NoProfile -File tools/governance/check.ps1
python tools/governance/tests/run-<新用例>.py
```

## Canonical Evidence

交付时登记协议 diff、检查器 diff、四类夹具结果、全库回归输出、Handoff、Review。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| GATE-PROTOCOL | AC1、AC2 | `doc/09_COLLABORATION.md` | `fbf459f28` | `8c4fa3c7b7c6bc85bc4eba98782e8bd62bc6878ac4b6fa3741faa0fcf5456f46` | `CANONICAL` |
| GATE-CHECKER | AC3 | `tools/governance/check.ps1` | `fbf459f28` | `19ee5e972ce72a35f7e97e97af616645268dbda6ca2cdbe1d6efee0a3b29514f` | `CANONICAL` |
| GATE-FIXTURES | AC4 | `tools/governance/tests/test_ac_gate.py` | `fbf459f28` | `3bf623ba1068ca875cbaa30f43163e54a835329df733448190212062fbcf00ce` | `CANONICAL` |
| GATE-WRITEUP | AC1–AC5 | `verification/GOV-AC-GATE-1/ac1-ac4-protocol-and-gate.md` | `fbf459f28` | `f449c758b6fc9d415f20806d73472b53607b509a85cf1eca96ad350d4dc8fa5e` | `CANONICAL` |
| GATE-HANDOFF | AC6 | `doc/handoffs/GOV-AC-GATE-1-fbf459f28.md` | `489d7b1ba` | `8be08f1088179638c1bbe1d4d3838040954a59a37aa040c051d6cf329e8e7ea5` | `CANONICAL` |

## Resource Manifest

交付时逐项登记；新增夹具须证明写在临时目录。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| task-env | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| dataset | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| artifact | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| temp | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| agent-output | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| exchange | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-AC-GATE-1.md` | 本 Task 只改协议、检查器与测试 |
| evidence_dir | `verification/GOV-AC-GATE-1/` | `PRESERVE_REFERENCED` | `verification/GOV-AC-GATE-1/` | `f449c758b6fc9d415f20806d73472b53607b509a85cf1eca96ad350d4dc8fa5e` | 2 份证据 |

## Closeout Record

- 状态：`proposed`。授权来源：Codex r20 §2.6。
- 释放前置：由 Codex 确认范围冻结、登记 base/head。
