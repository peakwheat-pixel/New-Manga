# 独立 Review：P02PRE-R1G

- Reviewer：Codex 非作者独立 Reviewer；作者：Antigravity；Integrator/Adjudicator：root Codex。
- Branch：agent/antigravity/P02PRE-R1G
- Base：cddff58469b56e181019a8ddfeade80684bc7eb9
- Reviewed HEAD：6e1c00fee3db07805c92c25cdc311af9279ceb51
- Verdict：CHANGES_REQUESTED
- 未解决发现：P0=0 / P1=0 / P2=2 / P3=0。既有已修订项不重复计数。

本次 Reviewer 读取冻结的 12 份精确文件，进行静态内容审查；未修改文件、未运行命令或被审代码、未计算 hashes、未访问 .tmp.driveupload。输入 pin 前后验证由 root Codex 负责。

## Architecture / Safety 与 Task / AC 范围

审查覆盖候选及 R1F 继承行为中的 child/getter/API/path/write allowlists、参数顺序、身份与仓库检查、no-read/no-follow、停止条件、证据回退和 CreateNew。未发现新增 executable、profile/registry/ACL 写入或用户数据写入代码。下述两项阶段证据缺陷未关闭，因此当前候选不能批准。

六个原生 child 调用点均使用有序数组，launcher 逐项加入 ProcessStartInfo.ArgumentList。Git prefix、五种 Git 参数及 whoami /all 保持冻结顺序；:(exclude).tmp.driveupload 是单一元素。普通与 partial command records 保留 executable、argv、CWD、PID、exit。此为静态实现结论，尚无实际 child argv 或运行证据。

## 既有发现处置

| 项目 | 本轮处置 | 内容依据 |
|---|---|---|
| ArgumentList 契约 | 静态修复确认 | candidate L60–115、L358、L360、L376、L390、L392、L662；partial record L528。 |
| R-001 | 原要求的分类与底层 stop 保留已修订；新增 R-010 | L1099–1122 保存底层 stop；L1125–1135 区分 size partial；L1148 输出 write failure，写入失败由 stderr/runner 留证。 |
| R-002 | 静态修复确认 | Handoff L85–91 区分 Codex-owned、作者交付和 NOT_RUN / NOT_VERIFIED，不再把 AC1/AC3 宣称为作者 PASS。 |
| R-003 | 静态修复确认 | L943–955 的 protected-hash failure 阻止 ACL re-query；L994–1001 和 L1090–1093 正确处理 ACL phase failure。 |
| R-004 | 文档契约修复确认；实际集成未验证 | Manifest L69–73 绑定精确 worktree/source/HEAD/pin，规定 absent destination、CreateNew、flush 后复算及执行前再次核对。 |
| R-005 | 静态修复确认 | Handoff L5–8、L18–23 保留历史 commit 身份；最终 delivery HEAD 外部记录，无自包含 HEAD。 |
| R-006 | 静态修复确认 | Handoff L76 与 candidate L629–654 一致：psHome、cmdlet source/version 是记录值，未冒充进程内精确断言。 |
| R-007 | 文档修复确认 | Manifest L5–8 明确历史 pins；L71、L94–97 指向当前 candidate。当前输入是否匹配冻结 pins仍由 Codex核验。 |
| R-008 | 静态修复确认 | author self-check 的 executionAttestation 承认只读 Git/Python 检查，并明确 parser/self-check/preflight/capture 等未运行。 |
| RP-001 | 本轮派发约束已修正 | Reviewer 无需通过读取工具自行计算 SHA；Codex承担前后 pins。此前 blocked/invalidated Review 不据此改写为有效批准。 |

## 新增发现

### R-009 / P2：WER 非法路径仍被标为完成，停止延迟到后续查询之后

位置：candidate L817，相关 L823–833、L837、L955、L1018、L1077；Manifest L28。

触发：任一冻结 WER 目录返回 REPARSE_POINT 或 NOT_DIRECTORY。Get-ExactDirectoryRecord 明确产生这些状态，但 WER 阶段只统计 QUERY_ERROR / ACL_QUERY_ERROR，于是 werQueriedFields=PASS_WITH_EVIDENCE、phases.wer=COMPLETED，且 stopReason 为空。脚本随后进入 protected hashes 和 ACL stability；非法 WER 路径直到最终聚合才导致停止。

影响：失败阶段被误报为完成，且在已发现非法路径后继续执行后续 getter。与 Manifest L28 的阶段状态及失败关闭要求不符。路径 helper 本身没有跟随该重解析点；本发现不声称发生了目标内容读取。

建议：在 WER 阶段检查上述非法路径状态，设置 wer=FAILED、明确 stop detail，并阻止进入 protected hashes / ACL stability；同步避免 queried-fields 的成功分类。

### R-010 / P2：两个最小证据回退分支丢失全部阶段状态

位置：candidate L1109 与 L1135；Manifest L28。

触发：主 ConvertTo-Json 失败，或 bounded partial JSON 仍超过 64 MiB。两个最终 JSON 对象均省略 Result.phases。

影响：即使成功写出唯一 evidence，post-run Reviewer 也无法逐阶段判断 NOT_REACHED、FAILED 或 COMPLETED。底层 stop 字段只能说明停止原因，不能恢复所有已到达阶段。这遗漏了 Manifest L28 明确要求的阶段证据，尤其影响失败捕获结果的判读。

建议：在两个最小 fallback 中保留固定、有限大小的 phases 字典，同时保留现有底层 stop 字段。

## 程序不确定性与验证结论

WORKTREE_RELATIVE_EXCLUDED_PATH_ACCESS=NOT_VERIFIED 保持原分类。现有材料不能证明作者查询了主仓受保护路径，也不能证明其 worktree 操作完全未查询同名路径。该限制不妨碍本次固定候选的静态内容判读，不据推测新增代码 finding，也不据此关闭过程风险。

Parser、self-check、PS7 child preflight、capture、host evidence、Build/Cargo、AC1–AC7 均为 NOT_RUN，未推断任何 PASS。实际 main 集成、运行时 no-read/no-follow、child closure 和写入稳定性未验证。既有 waiver 不构成技术通过；Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE 保持不变。

推荐下一步：root Codex 先复算同一输入集并 adjudicate 本报告；接受发现后，交 Antigravity 在原三文件范围内修订 R-009/R-010、同步 pins/Handoff，再冻结新 HEAD 独立复审。不得运行 parser/self-check/preflight/capture/host getter/Build/Cargo/AC。

未检查运行时行为或 excluded-path 状态；本候选仍有两项 P2，当前不得据此进入集成或执行。
