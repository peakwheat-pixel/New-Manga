# FEA-00 Codex r4 复审 Appointment 与 DSH 实测记录

日期：2026-10-31（Asia/Shanghai）。派发者：DSH（Lead / Architect / Integrator）。本文件是 Appointment 登记与 DSH 独立核验记录；不是 Review 报告本体，也不构成集成批准、Task 释放或实现授权。

## Appointment

| 项 | 值 |
|---|---|
| reviewer | Codex（独立新会话，未参与 r2 报告、remediation handoff 与 r3 复审的撰写/修订） |
| reviewer_kind | `agent`（另一个独立 Agent，CLI 新会话） |
| 通道 | `codex exec`（PATH `codex-cli 0.162.0`，`-s read-only -c windows.sandbox=unelevated -m gpt-6-luna -c model_reasoning_effort=xhigh`） |
| reviewer 会话 ID | `01a19230-36a9-7022-8d44-b23f100eeb08`（stderr；另有低档可用性探测会话 `01a1922f-afc7-7003-b865-c39f8d93bd6c`） |
| 派发 prompt | `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/codex-r4-review-prompt.md` |
| 原始输出 | `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/codex-r4-review-result.md`（SHA-256 `f12bf56ee18d8b074690575ccc9289e5a603714fffb4b6bf089f33db2fd549d5`） |
| 入库报告 | `doc/reviews/FEA-00-codex-r4.md`（原字节，同上 SHA-256） |
| 被审对象 | `doc/reviews/FEA-00-codex-r2.md`、`doc/handoffs/FEA-00-codex-r2-remediation.md`、`doc/reviews/FEA-00-codex-r3.md`、当前工作区 `tools/governance/check.ps1` 与 `tools/governance/tests/test_architecture_assertions.py`（HEAD `504797ba7` 之后的未提交修改）、仓外证据目录 |

## r4 结论（转述）

`changes_requested`：1 项 P1（跨行 Markdown code span 仍可让 AGENTS 的 AD-003 权威链接与哨兵被当作有效字段，R3-01 未完全关闭；r4 自述为静态推演、因只读环境未实测）、1 项 P2（remediation handoff 的"未提交"自述与 `delivery_head: null` 已过期，属历史快照，不应改写原文）。

## DSH 独立实测（补 r4 未执行部分）

环境：Windows、PowerShell 7.6.8、Python 3.14.6。复用 `tools/governance/tests/test_architecture_assertions.py` 的隔离夹具（复制最小文件集到 `New Manga.workspace/agent-output/codex/` 临时目录，运行真实 `check.ps1`，结束时清理），未修改仓库文件。

| 场景 | 期望 | 实际 |
|---|---|---|
| 跨行 code span 包裹 AGENTS 首句唯一 AD-003 链接 | 拒绝（FAIL） | **`EXIT=0` / `PASS (2 warnings)`——漏报，P1 成立** |
| 跨行 code span 包裹 AD-003 唯一 sentinel 行 | 拒绝（FAIL） | 拒绝（当前修复已覆盖） |
| 同一行 code span 包裹链接 | 拒绝（FAIL） | 拒绝（既有回归通过） |
| 现有 12 个架构断言测试 | 全部通过 | 全部通过（`Ran 27 tests`，仅新增跨行链接用例失败） |

- 实测脚本：`G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/r4_p1_probe.py`
- 实测日志：`G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/r4-p1-probe.log`（SHA-256 `f3019753297be33163db125281335c4b892b7a2727b3eea75263c5b96ad7eeb9`）

## 边界

- r4 与 DSH 实测只覆盖治理检查器的静态判别；产品功能、真实删除、迁移、并发、GUI 均 `NOT_RUN`。
- r2 报告、remediation handoff、r3/r4 报告与本次交付均在工作区未提交；未 push。
- P1 的修复、§4.4 事前基线（受影响全集与正负例）与修复后的新独立复审，由 DSH 另行安排；本记录不替代这些步骤。

## P2 处置（2026-10-31 22:0x，后续状态记录）

r4 P2：remediation handoff 第 15 行“所有修改目前仍在 `main` 工作树，未提交”与 `delivery_head: null` 是修订时快照。处置：**不改写 handoff 历史字节**；其截至时点为 2026-10-31 20:49（当时工作树未提交）。随后 r2 修订文档已随 commit `504797ba7` 入库；handoff 固定的 AD-002、AD-003、ADJ-001、`doc/reviews/FEA-00-codex-r2.md` 哈希与当前字节一致，`check.ps1` 与测试在其后又有后续修改（见 `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/r5-verification.md`）。读取该 handoff 时应以其固定哈希为准，不代表当前工作树状态。

## P1 修复记录（2026-10-31）

P1 已由 DSH 按 §4.4 前置核验后修复：`Get-AuthorityLines` 新增段落级跨行 inline code span 屏蔽（保留换行；同行 span 保留原文）。旧基线 3 mismatch → 新基线 0 mismatch；`check.ps1` PASS；16 个架构断言测试通过。证据与哈希：`G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/r5-verification.md`。修改尚未提交；修复后的独立复审需由未参与实施的 Reviewer 执行。
