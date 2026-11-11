---
task_id: FEA-15-PIN-EOL-GOV-1
adjudicator: ZCode CLI (`sess_8df67a95-be8f-4518-89fe-d71e950d9cff`)
adjudicator_kind: agent
independent_review: doc/reviews/FEA-15-PIN-EOL-GOV-1-r1.md
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
reviewed_head: 996f9768985ee121767bd750d24b1cdfe74dd186
current_head: d9c6360bb4cfcee970c0fe21f825e58b0d26df09
decision: accept_review_and_integrate
---

# Adjudication：FEA-15-PIN-EOL-GOV-1

## 授权链与绑定

- 用户于 2026-11-11 授权 ZCode 做最终裁决、Codex 继续执行；DSH 原 Lead 因额度停止。本报告由未参与实现的 ZCode 独立 CLI 会话作出，未复用实现会话、Review 会话 `sess_1ff7ce49-fa46-4cb8-b7a7-d2efcb347fdc` 或释放裁决会话 `sess_abdb4288-4a4f-49c1-8097-6edbb6e3866f`。
- Task base：`4173961dfe1b65256cb06d7628cc813b0603caa3`；Review 精确 head：`996f9768985ee121767bd750d24b1cdfe74dd186`；裁决时 HEAD：`d9c6360bb4cfcee970c0fe21f825e58b0d26df09`。
- 本裁决只处理独立 Review 与 Task 生命周期，不释放 pin 口径实施范围。

## 裁决

1. 接受 Review `approved` 结论：Architecture / Verification 均通过，0 P0 / 0 P1。
2. R-001 保持 `open`、P2、非阻断，作为后续 pin 口径裁定的输入；不要求 `changes_requested`。把 R-001 修复扩入当前 AC1–AC3 只读 Task 会越过冻结范围。
3. Task 可由 `in_review` 转为 `approved` 并进入集成窗口；当前**不允许**直接标 `done`。完成集成验证、资源收口和权威指针更新后，Codex 可按本裁决完成 `done` 收口。

## 独立核实

- `tools/governance/check.ps1` r194 的双基准语义：先比工作区 SHA-256，不匹配再比记录 commit 的 blob SHA-256，任一匹配即通过。这支持 R-001 非阻断判断。
- 对 `pin-inventory.json`、`checkout-matrix.json`、`candidate-policy-analysis.md`、`gate-final.log`、`resource-manifest.json` 的工作区 SHA-256 复算为 5/5 匹配 Task 当前登记值。R-001 报告的 WORKTREE/BLOB 区别仍由 r1 记录。
- 版本化 `gate-final.log` 记录 HEAD=`ef6253677a608f285e1c86a321712e45ae54cfef`：default 与 TaskPath checks 各 PASS（3 warnings），pins 18/18 PASS，API 1/79/6=86，均 EXIT 0；初次失败日志保留为失败。
- `96b79ca35…` 的早期门禁复跑当时没有持久化 artefact；因此不能用未落盘的命令记录完成集成验证。裁决时 Task 仍 `in_review`，AC1–AC3 `<<MET>>` 合法。

## Finding disposition

| ID | 级别 | disposition | 依据 |
|---|---|---|---|
| R-001 | P2 | 接受为非阻断开放遗留；纳入后续 pin 口径裁定 Task；本 Task 不返修 | r194 仍接受双基准；当前 Task 冻结为只读盘点，禁止 pin 口径整改；现有证据和 AC1–AC3 结论不因此失效。 |

## Task disposition 与集成条件

`in_review → approved`。`approved` 不等于 `done`。置 `done` 前须完成：

1. 在集成验证 head 重新运行 default check、TaskPath check、`verify_pins.ps1` 与 API inventory，并将每条命令的 timestamp、HEAD、完整结果和 EXIT 持久化；四项须 EXIT 0。
2. 将 `integration_commit` 绑定到门禁实际验证的 head。本 Task 主线为 `main`，裁决建议使用 `d9c6360bb4cfcee970c0fe21f825e58b0d26df09`。
3. 三项资源均按 `PRESERVE_REFERENCED` 保留并核验；无需删除、迁移或归档。将 `resource_closeout_status` 设为 complete，并刷新 STATUS / PLAN / TASK_LEDGER 指针。
4. 在终态卡面保留 R-001 的开放状态及非阻断说明；Linux fresh clone、renormalize simulation、产品 pytest/.NET tests 继续为 `NOT_RUN`。

## NOT_RUN 与 limitation

- 本 adjudication 会话为 `--mode plan`；pwsh / 带参数 Python 门禁亲跑 `NOT_RUN`。不以 ZCode Review 或 adjudicator 的身份声称运行过这些命令。
- r1 Review 与本裁决均未亲跑产品测试；Linux fresh clone 和 renormalize simulation 也未运行，均按 Task 范围保留为 `NOT_RUN`。
- R-001 的 WORKTREE 基准 pin 为非阻断 limitation，保持原始哈希与状态，不标成 PASS。

## 最终决定

**接受 r1 Review；R-001 = open / P2 / non-blocking；不要求返修；Task 进入 `approved`，集成门禁及资源 closeout 闭合后由 Codex 标为 `done`。** `.gitattributes`、checker 语义、历史证据/pin、契约、源代码、依赖、Schema、资源清理与 push 均未获授权。
