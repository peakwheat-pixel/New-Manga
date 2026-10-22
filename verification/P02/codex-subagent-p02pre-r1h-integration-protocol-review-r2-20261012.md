# P02PRE-R1H integration protocol Round 2 独立 Review

日期：2026-10-12（Asia/Shanghai）。非作者Reviewer=`/root/p02_r1h_remediation_review`；协议修订作者/Integrator/Adjudicator=`/root`；candidate Owner=`/root/p02_r1h_codex_owner`。实际模型/力度未暴露，记录`UNKNOWN`。

VERDICT=`APPROVED_STATIC_PROTOCOL`；P0/P1/P2/P3=`0/0/0/0`。在本次冻结四路径协议中未发现仍需阻止批准的实质问题。仅批准协议的静态内容，未执行替换、metadata采集或恢复，也不放行任何Gate。

## 冻结核验

派发=`verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-dispatch-20261012.prompt.md`；pins=`verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-pins-20261012.json`，实测SHA-256=`DE58847092D56476B54323E0FE4E8103D8E7FBD99D47D11C6F191289BEEBED51`。

**Pre/post inputs=13/13 MATCH，candidateFiles=3/3 MATCH，合计16/16 MATCH**；candidate commit/path/blob与absolute working-tree bytes/SHA一致。Task=30202 / `10CD84B847AD82D02BF3D1AD48711FDB095E17F703A27FB2EC6E7B51F9E1D108`；当前Owner refs：branch=`agent/codex/P02PRE-R1H`、HEAD=`dd5d2e3bc8e0702da9d059131f6364a997897661`、parent=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`、tree=`8cf6cf2dec8b375746b4c423f3c00ffe611a60d7`。受控porcelain-v2 -z输出为空；index前后=`DCBE24A2827B8465807C5627523DC6570346278935DA4A71BEF3FF969A9341FE`，符合pin。

主仓destination实测仍为57623 / `EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1`，属性Archive、无ReparsePoint。stage/recovery/apiBackup三路径前后均absent；`git check-ignore -- <path>`逐项无输出、exit=1，确认当前未忽略。只核对已枚举命名路径，没有创建任何文件或采集ACL/ADS。

## INT-R5-001：status/index精确delta

Disposition=`FIXED_STATIC_PROTOCOL`。Task153定义初始S0、CreateNew stage/recovery后调用前S1；156定义正常返回且核验后的S2。比较对象明确为porcelain-v2 NUL records multiset，而非raw hash必须相等：

| 比较 | 允许状态变化 | 不允许变化 |
|---|---|---|
| S0→S1 | stage/recovery两条新`?`未跟踪record；apiBackup absent | destination record或其余record变化、index改变 |
| S0→S2 | recovery/apiBackup两条新`?`record；stage最终absent | destination原record或其它record变化、index改变 |
| S1→异常 | 仅四个冻结路径的实际变化 | 其它路径变化或index改变，须记隔离未证明 |

Task文字以人类常用`??`描述untracked，实际协议使用porcelain-v2解析，应识别其`? <path> NUL`记录，而不是硬编码v1的两字符字段。此是格式说明，不是缺失状态放宽。

backup/recovery明确登记为Codex本Task integration evidence，保留且不做宽泛排除；未来capture须重新冻结包含这些路径的Git/protected baseline，解决它们被降级为无归属输出的问题。有效派发还要求所有dispatch/Review artifacts和已存在rolling checkpoint在执行初始状态采样前建立；执行者必须遵守这一条件，执行中不得新建未枚举证据路径破坏delta。本Review报告将在集成初始采样前完成，属于该条件的一部分。

## INT-R5-002：异常状态与独立恢复来源

Disposition=`FIXED_STATIC_PROTOCOL`。Task151–152不再从相似Git commit假定旧working-tree bytes，先校验精确主仓destination；stage只用reviewedOwner working-tree exact bytes；recovery以CreateNew从校验后的旧destination默认数据流复制并hash-match。它独立于API是否生成backup，故Replace前已有旧字节恢复材料。API backup独立absent路径，不能预创建后让Replace覆盖。

154明确三参数Replace、禁止ignore-metadata-error重载，正常返回与异常全有/全无保证分开。157覆盖抛错及postcheck失败：只读采集四路径实际state、default-stream pins、可见ACL/ADS和异常HResult，保留全部partial files，失败项与无法查询项入rolling checkpoint，不重试/清理/自动回滚。恢复只能在root独立adjudicate、destination已证明absent、来源已验证时进行；不存在“错误即原文件未动”的推论。未知目标不可覆盖，异常未裁决则BLOCKED。

API generated backup只有字节和所查询metadata实际匹配后才算旧副本；recovery只是默认流字节副本，不伪称DACL/ADS/timestamps备份。协议没有保证断电事务或完整NTFS metadata恢复，限制已明示，未见当前root-created .ps1单文件修复需要扩张至通用恢复系统。

## EOL pins与source identity

本Reviewer对两份已枚举工作树文件只读读取bytes，并对对应Git blob只读`git cat-file blob`获取原始bytes；在内存中仅移除紧邻LF的CR，直接比较归一后的字节序列，未执行任何候选/Parser或fixture。

| 对象 | working-tree bytes | CRLF pairs | blob bytes | 独立normalized equality |
|---|---:|---:|---:|---|
| 旧Round4主仓selfcheck / blob `0d56b658fac83f8b1fb6028d92136997c456f606` | 57623 | 722 | 56901 | true |
| 新Round5Owner selfcheck / blob `b3fa71a371a7d7ea6b6152a174ee6fdd19fc0914` | 57648 | 723 | 56925 | true |

这独立复核了adjudication中的换行表示说明；不推导两版源码逻辑相同，也不把raw LF blob直接用作CRLF执行字节。协议继续以旧`EEFB...`、新`977C...`工作树pins操作，来源HEAD/blob与working-tree bytes分别冻结。源capture/Handoff的absolute bytes/hash/blob也匹配pins；本次不重做candidate code verdict。

## ACL/ADS/metadata限制与API四路径

Task151要求普通非reparse destination、固定目录解析；152要求四路径同目录/卷、后三路径absent且未忽略，CreateNew碰撞或hash不符则不调用Replace。实际同卷与运行前no-follow检查属于执行preconditions，本Reviewer只核对静态路径/pin，没有把它们当已完成的动态检查。

153/155要求调用前、正常返回后ACL SDDL及alternate-stream名称/length/hash证据，destination/API backup需与旧destination可见metadata一致；query失败或差异走停止路径。157对异常也要求只读记录observed/unqueryable state。attributes/timestamps/file identity未验证明确列出，默认数据流hash或.NET正常返回不冒充完整metadata证明。严格要求保持旧ACL/streams而不是主动修改它们，未发现永久削弱安全机制或超范围权限。

精确四路径为destination=`p02pre-r1h-selfcheck.ps1`、stage=`p02pre-r1h-selfcheck-round5-stage-20261012.ps1`、recovery=`p02pre-r1h-selfcheck-round4-recovery-20261012.ps1`、apiBackup=`p02pre-r1h-selfcheck-round4-integrated-backup-20261012.ps1`，均限定`verification/P02/`。第一次AC4的absent+CreateNew与本次经Review指定单文件replacement分开；capture/Handoff不被替换，未授权通用覆盖。单次失败不自动再调用，恢复仍需后续root裁决。

## Gate与验收边界

Task159–161仍保持历史Round4 FAIL，未称Round5 parser/selfcheck已通过；Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE、Build/Cargo=NOT_RUN。private_registry_absence=UNPROVABLE、Technical Gate=NOT_SATISFIED、Owner Risk Acceptance=APPROVED、Gate Disposition=WAIVED_BY_OWNER、Build Authorization=AUTHORIZED_WITH_EXCEPTION与`technical condition unmet; user explicitly accepted residual risk`均保持。此协议静态批准不更新AC或释放capture；root必须完成adjudication、执行前checks、精确替换与真实AC4重测，frozenGit baseline缺失仍需后继处理。

## 实际读取与只读命令

- 读取frozen dispatch/pins、Task修订151–161与其原AC/允许禁止项、Round5 adjudication及EOL段、既有protocol Review、candidate Review/manifest/integration/failedselfcheck等pin限定输入；已读治理内容通过本轮hash核验未变。
- `Get-Item`/`Get-FileHash`仅复核已枚举inputs/candidate绝对路径，pre/post16/16；主仓旧destination额外按integrationPath pin核对bytes/hash/attributes。
- `git rev-parse HEAD HEAD^{tree} HEAD^`、`branch --show-current`、`rev-parse <commit>:<repoPath>`、`rev-parse --path-format=absolute --git-path index`与只读indexhash符合pins；`--no-optional-locks status --porcelain=v2 -z --untracked-files=all -- . ':(exclude).tmp.driveupload'`前后均无输出。`git check-ignore`三路径逐项exit=1，`Test-Path`三路径均false。
- `git cat-file blob <blob>`以只读Git子进程、stdout内存bytes取样完成上述换行核验，均exit=0/stderr空；内存CRLF过滤仅处理输入bytes，没有调用脚本parser/fixture或写临时文件。
- 没有Get-Acl/ADS getter、Replace、stage/recovery/backup创建、candidate/parser/selfcheck/preflight/capture/API/tests/Build/Cargo/AC/OSdynamic/Sandbox。未访问`.tmp.driveupload`。唯一写入本报告。

下一步可直接交root：复核本报告、同一16项pins与四路径当前状态并adjudicate；若接纳，先建立全部唯一execution artifacts和checkpoint再采S0，按Task151–157逐项留证进行一次受控integration及独立AC4重测。仅在preconditions实际满足时调用Replace；异常按四路径协议停止，不放行任何产品Gate。本Reviewer交付后停止，不执行集成或adjudication。

未执行Replace、metadata查询或恢复验证；批准仅为静态协议意见，实际preconditions失败时仍必须停止，Build Barrier保持。
