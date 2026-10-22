# P02PRE-R1H round-three Review adjudication

日期：2026-10-12（Asia/Shanghai）

## 裁决

- 独立 Reviewer=`/root/p02_r1h_remediation_review`，Owner=`/root/p02_r1h_codex_owner`，Integrator/Adjudicator=`/root`；Owner 与 Reviewer 不同。
- Review=`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/0/1/0`。报告=`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation3-20261012.md`，9545 bytes / SHA-256 `98E9C6F416518598865BCB1B6AD07FAB892868D2D95A9F38E2029DCD18BC03D8`。
- Root 重新计算 frozen Review inputs：source/candidate pins=`10/10 MATCH`；pin 文件 SHA-256=`502D164909D99C1BB6E9C4DB918D268181DE5C629F377764103DFBBDCD1CD655`。Root 已从 Owner worktree 静态核对 `selfcheck.ps1:211–223`；未执行候选脚本。
- 接受 R1H-007 / P2：稀疏整数键的 `[ordered]` dictionary 被以整数位置索引访问。`foreach ($index in $expectedDirectTexts.Keys)` 遍历整数键；`$expectedDirectTexts[$index]` 选择 `Item(int index)` 的位置重载。键 `3` 实际读取第四个插入值（键 `4` 的 `$full` 文本），与 `$prefix[3]` 的 normalization 文本不符，故真实合法候选的 contract 正例会返回 false；较大 key 也可能超出字典 count。这是静态推断，未执行触发。
- 语义依据：[Microsoft Learn — about_Hash_Tables（PowerShell 7.6），Accessing values](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_hash_tables?view=powershell-7.6#accessing-values) 说明 dictionary 整数访问使用值序列位置；`[object]` 整数才选择 key overload。Root 使用浏览器只读查阅了此官方文档，并核对 candidate 代码。
- 最小 Owner 修复：只把该 allowlist 的右侧读取改为明确的 object-key lookup（例如 `$expectedDirectTexts[[object]$index]`），或换成普通 hashtable；保持 prefix 左侧数组位置索引、13 项 exact allowlist、四个内存 mutation negative fixtures 与其它安全约束不变。禁止扩大范围；Owner 可按真实情况更新现有 Handoff。只有本轮 Owner 交付后再由非作者 Reviewer 复审。
- `R1H-006=FIXED_STATIC_COVERAGE`：真实 candidate outer loop 的 13-statement prefix 和四个 fixture 的静态结构已补上；fixtures 未执行。该项修复不覆盖当前 R1H-007，也不能放行 selfcheck。
- R1H-007=`OPEN / ACTION_REQUIRED / P2`。Task 整体继续 `in_progress`；Candidate 未集成。AC2=`BLOCKED / NOT_RUN`；AC3=`CHANGES_REQUESTED`；AC4、AC5、AC6=`NOT_RUN`；AC1=`NOT_VERIFIED`；AC7=`NOT_VERIFIED`。无运行或 OS/Gate PASS 结论。

## 后续边界

- 当前创建的 remediation dispatch 将固定起始 HEAD=`0ecada4182d624d4f352a253e09db3bdecbee5d1`，工作区=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`，branch=`agent/codex/P02PRE-R1H`，写入限定为既有 `p02pre-r1h-selfcheck.ps1` 与必要的既有 Handoff 文件；`capture.ps1` 不得修改。
- Owner 唯一允许执行的检查仍是 `git diff --check`。不得运行 parser/selfcheck/preflight/capture/getter/API/tests/Build/Cargo/AC1–AC7/OS dynamic 或 Windows Sandbox。Owner 交付后先做 Codex 范围/HEAD/pins/diff-check 验收，再启动同一非作者 Reviewer 对新固定 HEAD 复审；不得由 Owner 自审或 root 将静态意见写作 PASS。
- Gate 不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。

