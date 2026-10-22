# P02PRE-R1H Round6 integration protocol — independent Review attempt 2

请由非作者 Reviewer `/root/p02_r1h_remediation_review` 对修订后的集成协议做一次独立、只读、静态 Review。协议作者/Integrator/Adjudicator 是 `/root`；Owner 是 `/root/p02_r1h_codex_owner`。不得让Owner或协议作者审核自己工作。

## 冻结输入与基线

- 唯一输入pins：`verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-attempt2-20261012.json`，29项，SHA-256=`E53BAFA801115B8CFEDF66EC956A0AD313C1CE8EBF61EFA1CBD973302595E563`。先核对全部输入的bytes/hash，Review后再核对一次，要求29/29 MATCH；如果有任何漂移或冻结仓库状态不符，报告`BLOCKED_BY_MISSING_EVIDENCE`，不要批准。
- 当前修订协议：`verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md`。协议attempt1原字节、report、adjudication及旧pins/prompt均以独立路径固定并包含在输入pins中；不能把旧`CHANGES_REQUESTED`报告覆盖或解释成批准。
- root=`G:\CODEX\New Manga`，预期`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`，`.git/index` SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；冻结受控status=`1012 records / 68049 bytes / C672D6E508F303696440D7BF66973915E68CC5593EF0B9B123C9B7DAB4BF9F4F`。
- Owner candidate=`agent/codex/P02PRE-R1H@c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`，parent=`dd5d2e3bc8e0702da9d059131f6364a997897661`，tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`，worktree status empty。root Round5 selfcheck目标仍是57648 bytes / `977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`；Round6候选是57812 / `6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9`。候选代码及目标均没有在本轮集成。
- `verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-round6-attempt2-20261012.md`是唯一允许写入的报告目标；dispatch前已确认absent且unignored。Codex adjudication目标`verification/P02/p02pre-r1h-integration-protocol-review-adjudication-round6-attempt2-20261012.md`也已确认absent。

## 本轮Review范围

只审查协议是否把执行前的文件保护、身份、路径、status/index、子进程、单次Replace、失败保全、证据和Gate边界写成无歧义、可执行、最小权限的契约。重点裁决attempt1的两个P2是否已彻底修复：

1. **R6-IP-001：**任何条款不得再允许访问、读取、枚举、解析、stat、hash、打开或跟随`.tmp.driveupload`下内容/元数据；同时每条Git status argv都必须以独立参数`:(exclude).tmp.driveupload`排除此路径。查找协议内所有相关措辞，确认无矛盾。
2. **R6-IP-002：**检查固定`C:\Program Files\Git\cmd\git.exe`、`ProcessStartInfo.UseShellExecute=false`、main与Owner各自的精确WorkingDirectory、只读Git子命令和逐项ArgumentList、S0/S1/S2/S3调用顺序、每次进程PID/stdout/stderr/exit证据、Git环境边界、禁止未列child，以及两个固定PowerShell 7.6.6验证child的executable/CWD/ArgumentList。所有status必须保留单独exclude pathspec；检查是否仍存在遗漏的Git命令或与“无其他child”冲突的要求。
3. 复核CreateNew、备份、S0/S1/S2/S3 delta、三参数File.Replace唯一调用、partial failure不清理/不重试、protected-file hash/ACL/stream保护、未知子进程fail-stop及AC4测试范围之间是否一致。
4. 确认协议没有把`private_registry_absence=UNPROVABLE`说成PASS；Owner waiver仍只接受该项风险，不表示AC1–AC7或Build Gate通过。Windows Sandbox、Build/Cargo、capture、host getter、profile/registry/ACL API、本轮集成/Parser/selfcheck均不得执行。

## 操作边界与交付

- 只读静态Review：可使用PowerShell 7.6.6/Core `C:\Program Files\PowerShell\7\pwsh.exe`做输入hash、文本和冻结状态核验。若为核验必须启动Git，只允许协议中枚举的固定Git executable、CWD与argv；不启动其他子进程。
- 不运行Parser、自检、fixtures、capture、任何OS/API查询、File.Replace、Build、Cargo、AC或Sandbox；不写协议、Task、Plan、STATUS、Index、pins、prompt、checkpoint、代码或集成输出。
- 唯一写入是向报告目标用CreateNew写入一份报告，记录VERDICT、P0/P1/P2/P3计数、Finding ID/位置/证据/最小修复、29项pre/post pins结果、冻结Git refs/status/index、实际使用模型/力度（不可见写`UNKNOWN`）、实际运行的命令及其结果。Verdict应为`APPROVED_STATIC_PROTOCOL`、`CHANGES_REQUESTED`或`BLOCKED_BY_MISSING_EVIDENCE`之一。
- 如果有P0/P1/P2，保持`CHANGES_REQUESTED`；不要建议或暗示Codex可先执行集成。只有Review通过并由Codex单独adjudicate后，才考虑下一执行阶段。
- Review过程中不得修改pins中的任何输入。主Agent会在Review结束后再独立复算pins并执行adjudication。