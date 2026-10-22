# P02PRE-R1G 修订 Review Round 1 Codex Adjudication

日期：2026-10-12（Asia/Shanghai）  
Task=`P02PRE-R1G`；基线=`cddff58469b56e181019a8ddfeade80684bc7eb9`；交付候选 HEAD=`6943c6727c82c706d90a3ed4c14617b04c98d360`。

## Review 执行证据

- Non-author Reviewer=`DeepSeek Harness`；DSH CLI=`0.2.0-rc.2`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1g/New Manga`；session=`session-a35eed45-d8d3-4676-8955-03bd630f9927`；CLI exit=`0`。
- Frozen prompt=`verification/P02/dsh-p02pre-r1g-remediation-review-20261012.prompt.md`，`5115 bytes / SHA-256 EE66C5BCC9D77A88D017B56305996F7DAA2B6C96D27FDBFC60B2EDB2F4309975`。
- Raw stdout JSONL=`verification/P02/dsh-p02pre-r1g-remediation-review-20261012.stdout.jsonl`，`115873 bytes / SHA-256 6F851C569ECF5AFA067E9FCC0880EF2D1CF4EE0D61DB0A6A7156F5348BB03441`；stderr=`0 bytes / E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`；exit marker=`0\r\n`，`3 bytes / 13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`。
- Codex 审计 raw JSONL 共发现 8 次 tool call，全部 `read`。7 个 distinct paths 均属于 frozen allowlist；candidate script 第二次读取指定 `offset=765`；未见 shell、PowerShell、Git、测试、枚举、subagent、写入或未列路径访问。Review 工具边界=`COMPLIANT_WITH_PROMPT`。
- DSH 最终 verdict=`BLOCKED_BY_MISSING_EVIDENCE`；finding `RP-001 / P1`。Reviewer 正确指出：prompt 同时禁止除 `read` 以外的工具、又要求 Reviewer 自行核对 byte length/SHA-256，而 `read` 结果没有 size/hash 字段，导致 pin 自检不可能。
- DSH 会话按 dispatch skill 发起挂载；工具输出表示已挂到 `New Manga` worktree 的 DSH workspace。UI 实际显示状态未单独核验。

## Adjudication

1. `RP-001` 的过程缺陷=`CONFIRMED / ACCEPTED`。Review 工具边界本身无违例，但 prompt 中的互斥要求令 Reviewer 必须 fail-closed；本轮因此不是可用于 AC4 的完整 Independent Review。Verdict 保留为原始事实；Codex 不把它改写成 `APPROVED` 或 `CHANGES_REQUESTED`。
2. Codex 在 DSH 返回后对 prompt 内冻结的全部 9 个路径重新计算 bytes/SHA，均与 dispatch pins 相符。证据=`verification/P02/codex-p02pre-r1g-review-input-pins-remediation-20261012.json`，`4796 bytes / SHA-256 4C0F166343F9A59B904A6D1E0BB1105D6AA8FA61494672C4C927DFEFBC4209CF`。这证明文件在复查时仍匹配冻结值；DSH 本身没有独立校验这些 hashes。
3. DSH 报告 §5.1 的代码观察明确为 `ADVISORY / NOT_ACCEPTED_AS_REVIEW_FINDINGS`；由于 pin 通道阻断，不能据此确认 R-001/2/3/5/6/8 已独立通过，或确认 R-004/7 的闭环。
4. Codex 独立核实一个 manifest/candidate 契约差异：manifest 要求 child 调用使用 `ProcessStartInfo.ArgumentList` 并留下可核验的 argv；candidate 的 `Invoke-CapturedProcess`（script line 60–100）使用 `$info.Arguments` 字符串，`Invoke-Git` 及五个 Git 调用和 `whoami.exe /all` 调用均传递字符串（line 102–104、347、349、365、379、381、651）。此为 Codex adjudication 的实现差异，不把 DSH advisory 计作 Review finding；需由 Antigravity 在原授权三文件内修复后重新独立 Review。
5. 已选择最小安全修复路径：Codex 负责自身 pin 冻结并保存独立 pin-evidence；下一轮 Reviewer 只做内容 Review，不再要求其通过无 hash 输出的 `read` tool 计算 hash。Codex 在 Review 后再核对同一组输入文件 hash，以绑定审查对象。若前后 pins 不同则 Review 无效。

## 当前释放结论

- AC4 Independent Review=`BLOCKED_BY_MISSING_EVIDENCE / NOT_VERIFIED`；Hard Build Barrier 不变。
- Candidate main integration=`BLOCKED / NOT_RUN`；R1G parser/self-check、PS7 no-profile preflight、final pre-run、capture、post-run Review=`NOT_RUN`。
- Build Gate=`BLOCKED`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。此处 `NOT_RUN` 不代表测试失败。
- 用户风险裁决严格保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。

## 下一步

更新 R1G Task/manifest 的 review/pin 证据通道；由 Antigravity 修复 `ArgumentList` 与 argv 记录；Codex 重新冻结并校验输入 pins，DeepSeek Harness 以只读内容审查方式重审。不得在合规 Review 与 Codex adjudication 前集成 candidate 或运行 parser/self-check/preflight/capture。