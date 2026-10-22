# P02PRE-R1G Post-run Codex Adjudication

日期：2026-10-12（Asia/Shanghai）

## 裁决

- 非作者独立 Review：`APPROVED`，范围仅为本次 capture 证据分类与 fail-stop 处置，findings=`0/0/0/0`。
- Codex 复核 Review 输入 pins：`13/13 MATCH`；post-pin=`verification/P02/codex-p02pre-r1g-postrun-review-input-pins-post-20261012.json`。
- `P02PRE-R1G = DONE_WITH_LIMITATIONS`。单次 capture 已消耗，禁止重跑或覆盖任何输出。
- Stop=`SCRATCH_BASELINE_OR_HASH_FAILED`；scratch 的 `.codex/skills/ask-matt` Git mode=`120000`，但文件系统未报告 `ReparsePoint`。Candidate 在哈希前 fail-closed；停机前未完成 inventory。
- `identity` 与 `mainRepository` 有证据；`scratchRepository=FAILED`；后续 `environment`、`paths`、`wer`、`protectedHashes`、`aclStability`=`NOT_REACHED`，完整取证=`NOT_VERIFIED`。
- 96 个已登记 protected-file pre/post hashes 一致，但不能证明临时修改未发生，也不证明 OS 范围的写入、路径或进程闭包。
- 下一 READY Task=`P02PRE-R1H`：对 tracked Git symlink 的 Windows 非-reparse 表示作最小、失败关闭恢复；仅当有效性可由冻结的 Git 元数据和现有只读前置条件证明时允许 path-only skip，否则继续 stop。R1G source/output 均保留。

## Gate 保持

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；精确风险说明=`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（不是失败）。

## 证据路径

- 独立报告：`verification/P02/codex-subagent-p02pre-r1g-postrun-review-20261012.md`
- Capture runner：`verification/P02/p02pre-r1g-runner-evidence-20261011.json`
- Capture child：`verification/P02/p02pre-r1g-evidence-20261011.json`
- stdout/stderr/exit：`verification/P02/p02pre-r1g-capture-20261011.stdout.log`、`...stderr.log`、`...exit`
- Pre-run rolling checkpoint：`verification/P02/codex-checkpoint-p02pre-r1g-20261012.md`

Reviewer 没有执行脚本、命令、测试、hash 或 Git/OS 查询；Codex 仅按冻结 13 路径复算 pins。未访问 `.tmp.driveupload`。
