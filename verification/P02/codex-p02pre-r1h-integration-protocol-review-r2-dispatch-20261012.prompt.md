# P02PRE-R1H Integration Protocol Review — Round 2

日期：2026-10-12（Asia/Shanghai）
Reviewer：/root/p02_r1h_remediation_review，必须与实现 Owner /root/p02_r1h_codex_owner 不同；Integrator/Adjudicator=/root。
delivery=agent/codex/P02PRE-R1H@dd5d2e3bc8e0702da9d059131f6364a997897661；frozen Task base=946938bd0696dfddd01f87d61fe6723c63ecdc86。
本次只 Review 已修订的 post-initial AC4 integration protocol，不重做 Round5 candidate code Review。

## 冻结输入

唯一 pins=verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-pins-20261012.json
pins SHA-256=DE58847092D56476B54323E0FE4E8103D8E7FBD99D47D11C6F191289BEEBED51
唯一报告写入路径=verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-r2-20261012.md。
开始与结束时都复算 pins 内全部输入；任一 mismatch 或候选路径/HEAD/status 与 pin 不一致，立即停止并报告 CHANGES_REQUESTED，不得继续 Review 推论。

Owner worktree 候选是 Windows working-tree bytes，候选路径在 pins 中给出绝对路径、bytes/SHA 和 Git blob。逐字验证候选工作树文件；不得用 git cat-file 的 LF-normalized raw blob 代替工作树字节。Pins 同时记录候选字节做 CRLF→LF 后与各自 blob 的 byte-equality。

## 必须独立审查

1. 判断 Task 是否明确解决前一轮 INT-R5-001：以初始状态、Replace 调用前、成功后三个 checkpoint 比较 porcelain-v2 NUL status record multiset 和 index hash；成功 delta 是否精确限定为 recovery 与 apiBackup 两个新 ?? 记录、stage 消失、destination 原记录不变、其他状态不变。确认所有必要 dispatch/review artifacts 与 rolling checkpoint 都在执行前建立，使其状态不产生未枚举 delta。
2. 判断是否解决 INT-R5-002：每个路径初始状态、stage/recovery CreateNew 后的调用前状态、File.Replace 正常/抛错/postcheck 失败后的精确路径状态；是否不假设异常全有或全无、不自动 retry/cleanup/rollback；异常时保留四路径和 checkpoint；是否有独立、精确旧字节恢复来源及仅在目标证明 absent 后才可恢复的边界。
3. 检查 file ownership 与 metadata 前提：destination 要求精确 Round4 bytes 且非 reparse；stage source 是已 reviewed Owner worktree exact bytes；recovery 用 CreateNew 从旧 destination 默认数据流产生；API backup 目标必须预先 absent；ACL SDDL/ADS 查询和差异 fail-stop；哪些 metadata 未验证有没有明示。不得把 default-stream hash 或 .NET File.Replace 的正常返回描述为完整 metadata/异常原子性证明。
4. 核实 Round4/Round5 Git blob 与 Windows working-tree bytes 的换行证据。Adjudication 指出在 PowerShell 7.6.6 中对 working-tree byte array 仅把 CRLF 归一为 LF 后逐字节比较，Round4 722 对、Round5 723 对，均与相关 blob 完全相同。确认这一证据支持 EOL representation difference，不错误推出源码逻辑变化；检查协议仍使用工作树 exact pins。
5. 核对 API backup/path/volume/ignored-path preconditions、调用边界、成功和失败 status deltas 是否自洽；识别任何可能导致覆盖用户数据、无法恢复或无法证明隔离的 P0/P1/P2 风险。以最小修改建议报告。

## 评审边界

仅只读静态审查 Task、pins 指定的 source/evidence 和必要 Git metadata；可只读核验字节、hash、路径存在性、Git refs/status、无忽略状态。不运行任何 candidate/selfcheck/parser/fixture/preflight/capture/getter/API/ACL/profile/registry/Build/Cargo/AC/OS dynamic/Sandbox，不创建 stage/recovery/backup，不修改 Task、Plan、Status、Index、candidate、manifest、pins 或 adjudication。唯一允许写入是上方固定 Review report。不得访问 .tmp.driveupload；Git status 必须把 :(exclude).tmp.driveupload 作为独立 pathspec argv 参数。

## 报告格式

简体中文，记录真实 reviewer agent 与实际模型/力度；未暴露时填 UNKNOWN，不得声称使用未确认的模型。
报告开头写明 verdict=APPROVED_STATIC_PROTOCOL 或 CHANGES_REQUESTED、P0/P1/P2/P3 计数。若仍有 P0/P1/P2，则不能批准。
必须分别结论：
- INT-R5-001（status/index exact delta）
- INT-R5-002（异常状态/独立恢复来源）
- 工作树换行 pin 与 source identity
- ACL/ADS/metadata 限制
- API backup 语义与指定四路径边界
- Gate/Build/AC 状态不得变化
附上 pin pre/post 计数和 mismatch；列明实际读取的文件与运行的只读命令。只做分析，不写 Review 之外的文件。