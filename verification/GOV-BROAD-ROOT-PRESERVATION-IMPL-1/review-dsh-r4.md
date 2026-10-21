---
task_id: GOV-BROAD-ROOT-PRESERVATION-IMPL-1
author: DeepSeek Harness
base_commit: f47c68969dac7d3cec0dddbe3fca4ea2fa7803db
reviewed_head: d5d21ff9f4cfbd667f0a6bcc5e1fefe104efff05
decision: approved
---

## 结论

**approved**

- `reviewed_head = d5d21ff9f4cfbd667f0a6bcc5e1fefe104efff05`
- `diff_base = f47c68969dac7d3cec0dddbe3fca4ea2fa7803db`
- `delivery/source = 6e3bac7867c67a2e76e45e2facbbf859d5dba526`

R3 的唯一 P1（CRLF 导致 `git diff --check` 失败）已消除；本轮只读复核未发现新的 P0/P1。批准范围仅本实现与本 Task metadata；不批准真实 cleanup、父 Task done、r212 解除、push 或删除 6 个探针目录。

## P0 / P1 / P2

- **P0：0。**
- **P1：0。** R3 的 CRLF/`diff --check` 问题已修复。
- **P2（历史说明，不阻塞）：** `runtime-proof-r3.json` 的 `snapshot_basis` 明确说明 “22 EV 为 pre-final 快照”，但文字写 `final31 EV`；当前 Task 已因新增 R3 Review 记录变为 32 EV。该字段是 R3 时点历史说明，不是当前实时计数，pin/内容不受影响；建议后续把文字改为“R3 final 31 / R4 32”或标注快照时点，避免读者误认为当前只有 31 EV。

## 实际只读核验

**metadata diff：**

- `798cc8161..d5d21ff9` 仅 5 个文件：
  - `doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md`（32 EV 重签）
  - `verification/.../checkpoint.md`
  - `verification/.../review-dsh-r3.md`（新增，完整 R3 Review）
  - `verification/.../runtime-proof-r3.json`
  - `verification/.../test-execution.json`
- `6e3bac786..d5d21ff9 -- tools verification/.../tests` **为空**，代码与 T01–T18 测试未变。
- `runtime-proof-r3.json` 新增 `snapshot_basis`，正文以 `PRE_FINAL_EV_REGISTRATION` 开头，说明 22 EV 是测量时点快照，31 EV 由 DSH R3 另行核对，不冒充为快照计数。
- `checkpoint.md` 已修正为“恢复时所见 dirty 均属本 Task；固定 798cc 审查时 WT 已 clean”，不再把审查时 WT 说成 dirty。

**固定检查：**

- `git diff --check f47c…d5d21ff9`：**exit 0**。
- canonical `tools/governance/check.ps1`：**PASS（2 个既有 warning）**。
- `d5d21ff9` 尚未进入 main（`merge-base --is-ancestor` exit 1）；main 当前 `d3714a371`，未误称已集成。

**32 EV：**

- EV-1…EV-32 逐项 `raw = blob = pin` 全部成立。
- Task 的 `parse_markdown_declarations`：**EVIDENCE_PIN 32、errors 0**（48 declarations）。
- 三个本轮应转 LF 的文件均为 LF：`checkpoint.md`、`runtime-proof-r3.json`、`test-execution.json`；新增 `review-dsh-r3.md` 也为 LF。

**6 个探针目录：**

- Task Resource Manifest 中 `reviewer-probe` 恰 **6 行**，行号连续（[7..12]），包含：
  - 5 个 `dsh-probe-*`
  - `.dsh-mode-29c6eed9`
- 实际 6 个目录均存在，与登记集合一致。
- 本进程对 6 个目录的 `os.listdir` 均为 `PermissionError`，故**内容枚举 NOT_RUN**；未改 ACL、未删除、未迁移，仍按 `PRESERVE_REFERENCED` 原位保护。

## R3 保留证据与 NOT_RUN

- **R3 已执行的逻辑/positive/negative 证据继续有效**：同 canonical 数据 `24→12`、恰 12 个完整 error pair、`+5 roots/+12 declarations/+12 warnings`、旧保护与其余 12 不变；`warn_alias=False`、REAL_DRIFT 与无副作用内存 mock 均已实际执行。本轮不重复。
- **Owner 127 日志**：r4 18 / r3 29 / r3 80，均 exit 0、0 skip；canonical 与 raw agent-output 双 SHA 已核；两 replay-r3 均 `15 REJECT / 0 deleted / 0 violations`。R3 已核，本轮不重跑。
- **NOT_RUN**：
  - Reviewer 完整 18 fixture：**NOT_RUN**（沙箱禁写；Task TMP 不可用）。
  - 127 全套未由 Reviewer 重跑。
  - 6 探针目录内容枚举：NOT_RUN（PermissionError）。
  - canonical consolidate 全 100/138 盘点：未跑。
  - 真实 apply/cleanup/迁移/归档/GC/prune/push/ACL/Legacy：未执行。
  - 未 merge main；100 分支/138 工作树未重新枚举，未做任何资源增减。

## 范围与下一步

- 本批准仅覆盖固定实现（代码实际为 `6e3bac786`）及 `d5d21ff9` 上的 Task metadata/evidence；R3 的 P1 已关闭，P2 为历史说明，不影响 merge。
- 建议 Codex 按正常流程将本固定 head merge 到 main，再复验正式 24→12、32 EV、6 目录保护、check/diff；随后再 done。**不批准**父 Task done、r212 清理禁令解除、真实 cleanup、删除 6 个探针目录或 push。