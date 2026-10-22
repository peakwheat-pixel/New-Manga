# P02PRE-R1H Round6 integration protocol：独立静态 Review attempt 2

日期：2026-10-12
Reviewer：`/root/p02_r1h_remediation_review`（非作者）
协议作者 / Integrator / Adjudicator：`/root`
候选 Owner：`/root/p02_r1h_codex_owner`
实际模型 / reasoning effort：`UNKNOWN / UNKNOWN`（当前 Reviewer 配置不可见；不借用 pins 中 root 的配置）。
实际审查 shell：`C:\Program Files\PowerShell\7\pwsh.exe`，`7.6.6 / Core`。

## 结论

**VERDICT = APPROVED_STATIC_PROTOCOL**

本轮新增 finding 数：**P0=0，P1=0，P2=0，P3=0**。在冻结输入与本轮静态范围内未发现新的实质问题。该结论仅批准协议文本，不是执行结果、AC4 PASS、集成成功或 Gate 放行；Codex 必须独立 adjudicate 后才可考虑执行阶段。

旧 attempt 1 的 `CHANGES_REQUESTED` 保持历史有效；其两个 finding 在本次修订协议中均为 `FIXED_STATIC_PROTOCOL`，不覆盖旧报告。

## 冻结证据

输入清单：`codex-p02pre-r1h-integration-protocol-pins-round6-attempt2-20261012.json`，SHA-256 `E53BAFA801115B8CFEDF66EC956A0AD313C1CE8EBF61EFA1CBD973302595E563`。

- PRE：29/29 bytes 与 SHA-256 MATCH。
- POST：29/29 MATCH；最后一次写报告前再复算仍为29/29 MATCH，无漂移。
- 协议：16310 bytes / `26E152C31EF9111ECA55BAB96C3783F249329C5DE111909E9B8C55B2DD666697`。
- main：`main@cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`，common-dir=`G:/CODEX/New Manga/.git`。
- main index PRE/POST：`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。
- main controlled status PRE/POST（报告 CreateNew 前）：1012 NUL records / 68049 bytes / `C672D6E508F303696440D7BF66973915E68CC5593EF0B9B123C9B7DAB4BF9F4F`；exit=0，stderr empty。
- Owner：`agent/codex/P02PRE-R1H@c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`，parent=`dd5d2e3bc8e0702da9d059131f6364a997897661`，tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`；common-dir一致，controlled status PRE/POST empty。
- root Round5目标：57648 / `977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`；Owner Round6源：57812 / `6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9`。没有执行复制或替换。
- 7个集成输出均只读存在性检查为 absent；7次精确 `check-ignore --no-index --quiet -- <path>` 均exit=1、stdout/stderr empty。

本报告是唯一获准新增文件，采用 CreateNew 写入；报告本身增加已知未跟踪路径。上述status基线是报告创建前的快照，不将报告新增记录伪称为冻结输入漂移或声称写后status仍完全相同。

## Finding dispositions 与覆盖

### R6-IP-001：FIXED_STATIC_PROTOCOL

位置：协议 §2（line 32）、§3.1（lines 43、48）及 §3 前置条件。

修订统一禁止读取、枚举、解析、stat、hash、打开、跟随或查询 `.tmp.driveupload` 内容及元数据；Git status 使用独立 ArgumentList 项 `:(exclude).tmp.driveupload`。原先“可以read但不query”的冲突已移除；审阅全部相关条款未发现恢复访问权限的例外。Reviewer 未访问该排除路径。

### R6-IP-002：FIXED_STATIC_PROTOCOL

位置：协议 §3（line 36）、§3.1（lines 40–48）、§3.2。

协议明确列出固定 Git executable、两个精确 CWD、无shell的 UseShellExecute=false 与逐项 ArgumentList。repository identity、单路径ignore、带exclude的status均有完整子命令；S0/S1/S2/S3时序、identity重复检查和7个ignore查询都有指定位置。记录PID、argv、CWD、开始结束、stdout/stderr字节/hash、exit；清理列举的Git上下文环境变量及GIT_TRACE*，禁pager、hook、fsmonitor、external diff和未知child/descendant。两个验证PS7 child分别固定selfcheck和原Round5 capability query；其余子进程禁令与列举Git已一致。执行时仍须实际证明闭包，静态文本不是进程证据。

### 文件保护、状态和单次替换

位置：协议 §1–§2、§3前置条件、§4。

精确冻结旧目标、新Owner源和两项protected root文件；output碰撞不得清理，路径链必须普通且无reparse，同目录/卷条件在写前确认。先CreateNew execution evidence再S0，随后stage/recovery/Handoff分别CreateNew、Flush和readback；S1允许且仅允许3项新增，index与无关record不变。唯一三参数 File.Replace一次；S2要求stage消失、新目标精确、两份旧字节保全和Handoff精确，ACL/stream对照S0，并限定status delta。异常立即停止、保留partial artifacts和实际只读状态/异常HResult，不重试、不自动回滚。文本未宣称File.Replace失败全无副作用，也未宣称attributes/timestamps/file identity保留。未发现这些约束间的实质矛盾。

### 验证、历史与Gate

位置：协议 §5–§6。

仅在S2后执行固定PS7 parser/selfcheck/capability query，使用新的CreateNew证据，保留旧Round5结果，S3只增加两项验证证据。失败必须真实记录，代码变更需新Owner delivery与独立Review。原AC2失败仍为历史FAILED，不能由本Review改写。

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。保留：`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、系统AC1–AC7=`BLOCKED / NOT_RUN`。本轮没有扩大waiver或执行权限。

## 实际读取与只读命令记录

完整读取本轮prompt、29项pins清单与修订协议；结合本Reviewer已读且重新核对同字节的治理、Task、manifest、Round5证据、旧protocol/Review/adjudication、Round6代码Review/adjudication及Owner候选文本。历史大体量执行JSON作为冻结参考证据，不声称逐字重新阅读其全部493429字节或把历史记录当作新运行。

执行输入 `Get-Content -LiteralPath ... -Raw`、精确path `Get-Item`/`Get-FileHash -Algorithm SHA256`、7个精确output `Test-Path`与PSVersionTable只读检查；未运行候选。

Git只通过固定 `C:\Program Files\Git\cmd\git.exe`，ProcessStartInfo / UseShellExecute=false / ArgumentList / 精确CWD与协议规定前缀及环境边界启动。只用 `symbolic-ref --short HEAD`、`rev-parse HEAD`、`rev-parse HEAD^{tree}`、`rev-parse --git-common-dir`、Owner `rev-parse HEAD^`、规定controlled status和7次单pathignore检查；没有diff、checkout、add或其他Git操作。所有status均保留单独exclude pathspec。

有效PRE Git PID：main branch27000、HEAD6552、tree20500、common-dir32996、status41464；Owner branch31784、HEAD47144、tree39912、common-dir14544、status7680、parent12580；7次ignore为6536、7028、40684、45048、46324、46240、41444。有效POST status PID：main15508、Owner47332。identity/status均exit0；ignore均exit1。使用内存捕获输出，未创建临时证据文件。

一次早期只读helper在Git完成后的输出格式化中调用 `$info.ArgumentList.ToArray()` 导致 InvalidOperation，没有形成有效状态记录；其结果已丢弃，修正Reviewer的输出helper后重新执行允许的只读查询并获得上述有效结果。这是Reviewer格式化错误，不是候选失败；没有因此运行测试或修改受审文件。

## NOT_RUN / NOT_VERIFIED边界与下一步

未运行Parser、selfcheck、fixtures、capture、getter、profile/registry/ACL API、File.Replace、Build/Cargo、系统AC、Windows Sandbox；未创建stage/recovery/backup/validation evidence，未改输入、治理或代码。实际身份/SID、ACL/stream、卷/路径链、动态child闭包及替换后的状态必须由后续执行阶段重新取证；本轮仅审查其协议约束，均不记PASS。

推荐下一步：由 `/root` 独立复算29项pins并adjudicate本报告；若通过，再由Codex按冻结协议进行执行前安全检查及单次集成。Reviewer到此停止，无授权进行集成或释放successor。

跳过与风险：所有动态行为、元数据保全和AC4结果未验证；静态批准不能保证实际OS操作成功，执行遇到任何不符必须保留证据并停止。