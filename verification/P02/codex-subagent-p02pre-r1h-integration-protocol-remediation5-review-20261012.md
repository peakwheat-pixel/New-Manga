# P02PRE-R1H post-initial integration protocol 独立 Review

日期：2026-10-12（Asia/Shanghai）；非作者Reviewer=`/root/p02_r1h_remediation_review`；协议作者/Integrator/Adjudicator=`/root`。模型/力度在本执行上下文不可见，记录`UNKNOWN`。本次只评估Task追加的集成协议，不重审Round5 candidate静态意见。

VERDICT=`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/0/2/0`。旧/新字节限定和单文件范围成立，但status变化验收与Replace异常状态记录尚未闭合。未执行替换、测试或任何动态步骤。

## 冻结核验

派发=`verification/P02/codex-p02pre-r1h-integration-protocol-remediation5-review-dispatch-20261012.prompt.md`；pins=`verification/P02/codex-p02pre-r1h-integration-protocol-remediation5-review-pins-20261012.json`，实测SHA-256=`16ECD5CC8940703CF3C6C3E20DD6C7DD69AEE0A39632E9B457CDC63B61869DC0`。**Pre/post inputs=10/10 MATCH、candidateFiles=3/3 MATCH，合计13/13 MATCH**；candidate blob通过`git rev-parse dd5d2e3...:path`确认。

当前Task=26605 bytes / `AA314BD24E04CEEC8BF23E58D2EADD81A8C442A5C6EA97F4D047AAEBCAE508AD`。Delivery=`agent/codex/P02PRE-R1H@dd5d2e3bc8e0702da9d059131f6364a997897661`；frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`。相关旧目标/新候选：

- 主仓旧selfcheck=57623 / `EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1`。
- Owner reviewed新selfcheck=57648 / `977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`；blob=`b3fa71a371a7d7ea6b6152a174ee6fdd19fc0914`。
- stage=`verification/P02/p02pre-r1h-selfcheck-round5-stage-20261012.ps1`；backup=`verification/P02/p02pre-r1h-selfcheck-round4-integrated-backup-20261012.ps1`，前后静态检查均absent。二者只是同目录路径限定/不存在观察，未创建或测试同卷操作。

## Findings

### INT-R5-001 — P2：status要求前后一致与永久保留新backup不相容

位置：`doc/tasks/P02PRE-R1H.md:152`–`:154`，尤其154。

触发：成功的Replace消耗stage，同时留下新backup。主仓selfcheck是此前CreateNew集成的untracked文件，替换同路径字节不改变porcelain路径记录；但backup原absent变为存在，受控status会新增一条`??`记录。协议154要求“受控status和index前后记录一致”，按raw status字节/hash一致执行会必然误拒绝成功状态；若临时忽略差异，又没有精确delta作为依据。

影响：集成可完成文件更新，但验收停在模糊漂移状态；备份还可能被下一轮protected inventory视作无归属新增文件，违反状态/证据精确登记目标。

最小修复：明确**index hash前后不变**；status不要求raw equality，使用原始记录集比较并允许唯一已枚举delta：旧destination路径记录保留、backup新增、stage最终absent，无其他新增/修改/删除。若需新增integration evidence，其唯一文件名也应先冻结并分阶段计入expected delta。将stage/backup标为Codex本Task集成evidence paths、保留策略与新hash写入Task/checkpoint；未来capture仅在重新冻结包含这些授权路径的Git/保护基线后进行，不额外排除或放宽inventory。

Disposition=`OPEN`。

### INT-R5-002 — P2：把Replace称作原子换入却缺少异常后实际三路径状态与恢复来源

位置：`doc/tasks/P02PRE-R1H.md:153`–`:154`；相关`verification/P02/p02pre-r1h-remediation5-adjudication-20261012.md`的“任何path/hash/collision mismatch stops integration without touching the destination”必须限定为**调用前检查失败**。

触发：Replace抛异常，不能一律假设destination未改、backup未创建、stage未变。Microsoft说明ReplaceFile的不同错误可能把旧文件移到backup并让replacement继承streams/attributes，或保留原名但未完整合并metadata。参见[ReplaceFileW错误与Remarks](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew)、[File.Replace重载](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.replace?view=net-9.0)。这不是已经观察到的本机失败，也不代表禁止使用此API。

影响：协议只有成功post-hash与通用“异常停止”，没有规定异常时如何冻结实际destination/stage/backup状态、是否有可验证旧字节、从何处恢复；后续接手者可能误把API失败等同无变更，无法按精确安全边界续接。backup由Replace生成，并非事先已CreateNew保存且hash验证的旧字节副本；文档不得混称两者。

最小修复：限定“atomic”只描述正常换入行为，不承诺异常全有或全无。明确调用前保存三路径状态/pins；catch及success-validation失败均停止后，仅只读采集三路径exists/type/bytes/hash、异常类型/HResult和已授权metadata证据，写rolling checkpoint并保留所有部分文件，禁止重试/清理/盲目回滚。冻结旧字节的独立恢复来源，例如old reviewed commit `7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`的精确selfcheck blob和旧bytes/SHA，或另一个CreateNew预备份；任何恢复仅在后续明确范围中、目标状态可证明时做，不在catch中自动覆盖。区分“backup尚不存在但旧commit可恢复”“backup旧hash匹配”“destination已新hash”等恢复状态。

Disposition=`OPEN`。

## 五项问题的其余结论

1. 旧hash、bytes及Round4 root CreateNew integration evidence共同提供**本次目标内容**归属证据，授权限定单文件且没有通用覆盖，符合当前用户已授权的必要修复。hash本身不是完整ownership/file-identity/metadata证明；执行前应继续使用项目已有no-follow路径/普通文件检查，路径对象异常即停止，不能仅凭hash跟随未知reparse目标。
2. stage使用CreateNew，三个绝对解析目标需保持同一目录/卷；成功后验证旧backup和新destination、保留backup，是正确的恢复设计方向。该协议只创建stage，backup由Replace原子替换流程生成，不是CreateNew预备份。上述INT-R5-002补齐失败状态后无需扩张为通用系统备份框架。
3. 新规则明确说明首次AC4 CreateNew与经Review后指定旧文件替换的区别，并限制root执行、单文件/本轮，未授予Owner集成权限。按本次授权不需要新产品裁决，但Task规则必须经本独立Review修正/接受后才可执行。
4. 三参数File.Replace默认不忽略metadata merge errors，应明确保持此重载，禁止改为ignoreMetadataErrors=true。Replace保留/合并旧DACL及命名streams等metadata；普通SHA只覆盖默认数据流，无法证明ACL或Zone.Identifier不变。对这份root-created本地.ps1，未见必须移除streams或主动修改ACL的依据；应记录实际可见metadata前后/异常状态或明确未验证限制，不能声明hash-match等于所有metadata一致。API失败状态分类是当前必要修订，不要求Reviewer运行新的getter。
5. stage/backup是Task新增已枚举integration输出，不是capture可任意新增权限。INT-R5-001要求登记预期status delta与后续重新冻结baseline，可以避免将它们降级为未知artifact或宽泛排除。当前Git基线缺失仍UNPROVABLE；本协议Review不释放capture。

## 证据与操作边界

实际读取：frozen prompt/pins、Task新增段（137–158）与其原AC/禁止范围、AGENTS、协作协议已读内容及当前pin、manifest、Round5 adjudication、Round5静态Review与pins、Round4集成记录。Candidate本次仅核对commit/blob/bytes/SHA；没有再评审代码verdict。

实际命令：`Get-Content`、对pins已枚举输入`Get-Item`/`Get-FileHash`、`git rev-parse <delivery>:<candidate-path>`、`Test-Path`只对stage/backup命名路径检查absent；exit=0，pre/post13/13 MATCH，两路径均False。`web.search/open`只读Microsoft File.Replace/ReplaceFileW文档，未运行示例或宿主API。没有git status、没有访问`.tmp.driveupload`。

唯一写入本报告。未改Task/candidate/governance/pins，未执行integration、parser/selfcheck/fixtures/preflight/capture/getter/API/tests/Build/Cargo/AC/OS dynamic/Sandbox。Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE保持；Owner waiver不是本协议或AC PASS。

下一步可直接交root：在`G:/CODEX/New Manga`，仅修正Task上述两个P2的status delta、三路径异常checkpoint和旧字节恢复来源说明，同步矛盾的adjudication措辞并重新冻结protocol pins；不要替换任何目标。修订后交非作者复审，再由root adjudicate/执行。当前delivery保持`dd5d2e3bc8e0702da9d059131f6364a997897661`；本Reviewer不集成或放行。

未验证实际File.Replace、ACL/streams或恢复操作；协议两项P2尚开放，不能据本报告执行替换。
