# P02PRE-R1H Round6 integration protocol 独立 Review

日期：2026-10-12（Asia/Shanghai）；非作者 Reviewer=`/root/p02_r1h_remediation_review`；Owner=`/root/p02_r1h_codex_owner`；协议作者/Integrator/Adjudicator=`/root`。实际模型/力度不可见，记录`UNKNOWN`。

VERDICT=`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/0/2/0`。精确旧/新字节、CreateNew recovery、单次Replace与状态delta设计基本闭合，但排除用户数据路径和Git子进程边界的两处矛盾必须修订。未执行任何集成、AC4检查或动态操作。

## 冻结与实测状态

Prompt=`verification/P02/codex-p02pre-r1h-integration-protocol-dispatch-round6-20261012.prompt.md`，SHA=`D4AC2E1880E2F33028F02DF87CBC59086D59E602E2186085F34790B877586895`；protocol=`verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md`，11184 bytes / SHA=`9FE8AB32823BE853673A873E2F590E0DEC2C123BFF6C3EB07185D217B3D699D4`；pins=`verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-20261012.json`，SHA=`3AAECFEB5A0530C5B8B844BABF5003E639AED121A075F36752AB1729684D2A18`。三者实测匹配。**21项绝对路径input pins pre/post=21/21 MATCH，mismatch=0。**

Root main前后=`main@cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`，common-dir=`G:/CODEX/New Manga/.git`，index=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。主仓受控status在报告创建前的pre/post均exit0、stderr空、1006 NUL / 67485 bytes / `9CE38F0B1AA70CE2B43D222399CD783266FB8081DA33CE3A252B020438B64F90`。本报告随后CreateNew产生的唯一新路径属于派发授权，不把它计作不明冻结漂移。

Owner=`agent/codex/P02PRE-R1H@c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`，parent/base=`dd5d2e3bc8e0702da9d059131f6364a997897661`，tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`，shared common-dir相符、status前后为空；parent→HEAD精确为selfcheck修改与Round6 Handoff新增。旧root target为普通FileInfo/Archive、57648 / `977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`，候选为57812 / `6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9`；root capture/Handoff、Owner三文件pins均匹配。8个planned integrationOutputs逐项absent、check-ignore exit1。身份/ACL/streams只读取已有证据与pin，本轮未调用相应getter，执行时仍需实际preflight。

## R6-IP-001 — P2 / OPEN：明确的排除路径禁止与“Read”指令相矛盾

位置：`verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md:40`；对照section2末段与本次dispatch禁令。

触发：pre-write步骤1要求“Read but never query paths under .tmp.driveupload”。该句字面允许读取用户上传暂存数据，和同协议的“不query/follow”及Task/dispatch严格禁止读取/检查此路径冲突。执行者不能从冻结协议唯一确定读取边界；它也不能靠禁止query推导禁止内容read。

影响：可能产生未授权用户数据读取，或执行者依严格规则停止而无法执行协议。当前没有读过此目录，不推导已发生访问。

最小修复：将该句替换为“Do not read, query, enumerate, stat, hash, resolve or follow .tmp.driveupload or its descendants; every Git status query must use the independent exclusion pathspec.” 仅核对明确冻结的输入和允许路径；保留大小写/路径同义访问的既有禁止要求。不要借此新增任何getter或文件读取范围。

## R6-IP-002 — P2 / OPEN：Git核验要求没有可执行的子进程允许范围

位置：protocol **36**，以及 **40/42/47/53/55** 的refs/status/unignored/delta要求。

触发：36声称“selfcheck and no-profile capability query are the only two planned child processes”且“do not start any other child”。但实际必需的Git CLI refs/status/check-ignore核验会启动git.exe子进程，协议没有枚举其固定executable、允许argv、CWD与调用阶段。不能把git进程当成没有child，也不能在执行时自行增添未冻结实现。

影响：按协议的两child规则执行会把必要Git核验判为未知child并停止；若临时默许Git，又失去精确子进程闭包和argv审计边界。此项不是要求执行新动态测试，而是消除执行契约自相矛盾。

最小修复：区分“File.Replace/CreateNew数据写入动作本身不启动child”与“pre/post只读Git核验”和“两个pwsh验证child”。冻结实际Git executable绝对路径及只读argv/CWD/阶段，至少涵盖协议所要求的refs、branch/common-dir、check-ignore、porcelain-v2 NUL status；Git可用性与全部PID/exit/stdout/stderr入证据，不允许hooks/fsmonitor等未经审核子进程，禁止其余child。保持status的独立exclude pathspec。或冻结等价的无child读取实现；不能仅写“Git允许”而不列精确命令。

## 其他静态协议结论

- 源/目标身份：固定旧root-owned字节与新reviewedOwner working-tree字节、protectedcapture/Handoff明确；固定PS7/user/SID/adminfalse与no-reparse路径、普通FileInfo、同卷/absent/unignored均要求执行前复核，不用Git untracked推断目标absent。未见通用覆盖授权。
- S0/S1/S2：execution evidence先CreateNew再入S0，governance在S0→S2不改；S1仅新增stage/recovery/Handoff，S2仅保留recovery/apiBackup/Handoff，旧target记录不变、index不变。旧目标当前untracked，因此内容替换不产生额外tracked status字段。以后S3仅新增两validation evidence路径；这些设计解决前轮status equality问题，不能把枚举以外的artifact当成默许变化。
- Replace/recovery：独立CreateNew recovery保留旧默认流，apiBackup由唯一三参数Replace生成；postcheck允许stage absent/API backup present，不再次使用pre-call absent规则。失败采集实际状态/HResult，保留partial artifacts，禁retry/cleanup/rollback，不把异常当作全有或全无。ACL/stream对比与attributes/timestamps/fileID未证明限制有说明，默认hash不是完整metadata证明。
- AC4：新sourceS2精确验证后才Parser/selfcheck与冻结Round5 capability command；ArgumentList启动、PID/argv/output/exit证据、两新CreateNew结果文件和历史失败保留明确。两个pwsh验证child须有固定rootCWD；现有Task/历史argv规定可作为精确冻结引用，执行者不得猜测相对File参数的解析目录。真实结果仍NOT_RUN，本次不重审代码verdict或预测断言通过。
- Gate：protocol末段没有改变private_registry_absence=UNPROVABLE、Owner waiver、Build Gate=BLOCKED/Hard Build Barrier=EFFECTIVE；不释放capture/Build/Cargo/system AC或Sandbox。

## 实际读取与命令

完整读取frozen prompt/protocol/pins；Task当前协议范围、Plan/STATUS/Index当前段及其hash；Round6 codeReview/adjudication、Round5 protocolReview/adjudication、manifest、失败/engine/旧integration证据与已有candidate/Handoff相关内容。大体量历史execution仅按pin核验和相关上下文，不重审其所有事件链。旧human-decision作为pin限定授权历史引用，不能用其旧阻塞覆盖当前Task的正式持续授权。

只读命令：`Get-Content`、对JSON已枚举21项的`Get-Item`/`Get-FileHash`，pre/post21/21；refs/branch/common-dir、parent→HEAD name-status与受控candidate status均exit0；8output的`Test-Path=false`和`git check-ignore -- exact-path`逐项exit1；主仓raw-status仅stdout内存字节计算NUL数/SHA，精确argv为`git --no-optional-locks status --porcelain=v2 -z --untracked-files=all -- . ':(exclude).tmp.driveupload'`，前后匹配freeze。未输出用户文件内容或访问excluded路径。

唯一写入本报告，以FileMode.CreateNew独占写入。未修改21项输入、main/source/target/Task/Plan/STATUS/Index/protocol/checkpoint/pins，未运行integration、Parser/selfcheck/fixtures、capture/getter/API、Build/Cargo、AC、OSdynamic或Sandbox。

下一步可转发root：仅修订冻结protocol的40排除路径禁令和36精确Git/pwsh子进程契约，更新Task引用、pins与新派发；保持source/target与所有execution outputs未创建。重新非作者Review并root adjudicate后才可运行唯一集成/重测。此次CHANGES_REQUESTED不沿用旧协议批准。

未执行File.Replace、ACL/streams/身份getter或AC4验证；两项P2仍开放，不能据本报告执行协议或解除Gate。