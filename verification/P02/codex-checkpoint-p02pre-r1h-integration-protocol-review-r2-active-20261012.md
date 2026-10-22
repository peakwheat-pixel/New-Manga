# P02PRE-R1H Rolling Checkpoint — Integration Protocol Review Round 2 Active

- 时间：2026-10-12 06:52:03 +08:00（Asia/Shanghai）
- 仓库：G:\CODEX\New Manga；branch=main；HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9；tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b；Git common-dir=.git；main ahead 1365。
- 主仓 .git/index SHA-256=214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C；读取前后需一致。
- Root workspace dirty。未知作者 dirty/untracked 内容保持原样；没有 reset/clean/stash/delete/overwrite。每个 git status 都将 :(exclude).tmp.driveupload 作为独立 argv pathspec；未访问该路径。
- Owner worktree=C:\Users\49745\.codex\worktrees\p02pre-r1h-codex；branch=agent/codex/P02PRE-R1H；HEAD=dd5d2e3bc8e0702da9d059131f6364a997897661；tree=8cf6cf2dec8b375746b4c423f3c00ffe611a60d7；controlled status=0；frozen Task base=946938bd0696dfddd01f87d61fe6723c63ecdc86。Owner commit includes only three approved candidate paths.
- Task=doc/tasks/P02PRE-R1H.md SHA-256=10CD84B847AD82D02BF3D1AD48711FDB095E17F703A27FB2EC6E7B51F9E1D108；manifest=verification/P02/p02pre-r1h-manifest-20261012.md；Codex adjudication=verification/P02/p02pre-r1h-remediation5-adjudication-20261012.md SHA-256=9A011D04459A377A8E8DD973705C447EB58FEBB4F20816927DA916993341F47D。
- Round5 candidate code Review=APPROVED_STATIC_CONTENT (0/0/0/0)；Round4 integrated selfcheck remains actual FAILED (PID 48712, exit 1), AC4=NOT_VERIFIED. Round5 parser/selfcheck/preflight/capture have not run.
- First integration-protocol Review=CHANGES_REQUESTED (P0/P1/P2/P3=0/0/2/0), report SHA-256=7CDAB7B6157C709C8BA6E4955A84F1285379AB4DDC952D6071076BACC8C9CF52. Findings: success status delta was unspecified; File.Replace exception paths/recovery source were insufficient.
- Root amended only the Task protocol and Codex adjudication. The proposed Round4 Owner Git blob is LF-normalized: PowerShell 7.6.6 root compared the old local 57,623-byte target and 57,648-byte Owner candidate with raw Git blobs, transformed only CRLF pairs to LF, and matched each blob byte-for-byte (722 and 723 CRLF pairs). Raw blob bytes are not the Windows working-tree pins.
- Revised protocol freezes the old destination, stage, CreateNew byte recovery file, and File.Replace API backup paths; it defines initial/pre-call/success and exception status deltas, preserves partial artifacts, and forbids automatic retry/cleanup/rollback. Current destination still matches Round4 57,623 / EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1; stage/recovery/API backup are absent. No integration action or API call has occurred.
- New protocol pins=verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-pins-20261012.json SHA-256=DE58847092D56476B54323E0FE4E8103D8E7FBD99D47D11C6F191289BEEBED51; dispatch prompt=verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-dispatch-20261012.prompt.md SHA-256=5F739D5F7527083874CFF673770C92E77CC4129829EFDD4900F4B162F8B4A239; report path=verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-r2-20261012.md.
- Independent Reviewer /root/p02_r1h_remediation_review was reactivated for static protocol review; report is the only permitted write. Actual reviewer model/effort was not surfaced, record UNKNOWN. Root actual model/effort=gpt-6-luna/max; preferred gpt-6.1-sol/high unavailable.
- Exact next step: receive the R2 report; root recomputes all 13 reference and 3 candidate pins before/after, adjudicates findings, and only if protocol has no P0/P1/P2 executes the guarded integration. Then run actual PowerShell 7.6.6 parser/selfcheck/no-profile preflight as AC4. Preserve Round4 failure evidence.
- If AC4 passes, continue AC5 exact final pre-run. Main/scratch frozen status/index baseline remains UNPROVABLE; no capture unless every Task/manifest precondition is proven. Build Gate remains BLOCKED; Hard Build Barrier=EFFECTIVE; Build/Cargo=NOT_RUN; system AC1–AC7=BLOCKED / NOT_RUN.
- P02 risk values unchanged: private_registry_absence=UNPROVABLE; Technical Gate=NOT_SATISFIED; Owner Risk Acceptance=APPROVED; Gate Disposition=WAIVED_BY_OWNER; Build Authorization=AUTHORIZED_WITH_EXCEPTION; exact residual=technical condition unmet; user explicitly accepted residual risk.
- Authorization remains active for R0/R1H, dynamic validation, build/Cargo, AC1–AC7, necessary repairs/reviews/integration. No Windows Sandbox query/install/enable/launch. User requests shutdown on completion; computer remains on until all authorized work reaches safe closeout.
- Main controlled status=`982 NUL records / 65601 bytes / SHA-256 7AFF751BF9990FFDD5A6A580D230147CD3A503ADBCD207A6571AD6542E43C9F0`; exact argv=`git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload`; exit=0/stderr=0. Index SHA-256 before/after=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`.

## 本轮追加审计记录

- 首次进程级状态采集 helper 把 PowerShell 自动变量名 `$args` 作为函数参数，导致 Git 实际只收到无 subcommand 的 argv，返回 usage/exit 1；该输出未作为 status 证据。改用 `$argv` 后显式调用 `C:\Program Files\Git\cmd\git.exe` 和固定 NUL 参数复核，main/Owner status 均 exit 0；Main `982/65601/7AFF...C9F0`，Owner controlled status=`0 bytes`。index 前后相同。没有任何 status 文件写入，也没有触及 excluded path。
- Owner worktree 三候选文件与提交 Git blobs均经独立 bytes/SHA验证；Owner HEAD/tree与 pins一致，候选在CRLF→LF后与各Git blob逐字节相同，status clean。Root Task、Review和 adjudication 使用 working-tree exact pins。
- Root 已把 DAG/status/index 刷新到本 R2 checkpoint；Plan=`doc/REBASELINE_PLAN.md`、Status=`doc/STATUS.md`、Index=`doc/00_INDEX.md`。本轮与上一有效 checkpoint（978 records/65221 bytes）相比新增4条 status records/380 bytes；未能逐项确认归属的旧 dirty/untracked 项仍为UNKNOWN。
- R2协议Review派发前 root复算 pins=`13/13 inputs + 3/3 candidates MATCH`、mismatch=`0`；destination仍为Round4 exact bytes，stage/recovery/API backup均absent且not ignored。Review report尚未交付。

## 2026-10-12 Codex adjudication完成；集成前核验 ACTIVE

- 仓库=`G:\CODEX\New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；main `.git/index` SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。
- 本轮受控 status=`985 records / 65837 bytes / SHA-256 1B6482311494E7D07C45AA7C1FFBBEE93B31A883F5A613CFAC4A9934B02344D1`；精确argv=`git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload`，通过PS7 `ProcessStartInfo.ArgumentList`调用Git并从stdout BaseStream读取原始NUL bytes；exit=0/stderr=0；index前后相同。排除pathspec为独立argv参数；未访问该路径。上一有效checkpoint为`982 / 65601 / 7AFF751BF9990FFDD5A6A580D230147CD3A503ADBCD207A6571AD6542E43C9F0`，本轮净增3 records/+236 status bytes，对应R2 Review报告、Codex adjudication、执行JSON；更早未知作者dirty/untracked内容归属仍=`UNKNOWN`且保持原样。
- 非作者Reviewer `/root/p02_r1h_remediation_review` 的R2 verdict=`APPROVED_STATIC_PROTOCOL`，0/0/0/0；report=`verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-r2-20261012.md`（9375 / `1D8D78A479887470B0B2065F68E4DC5073493C141868320C231B55198F2F3E7C`）；report所列16/16 pins已由root再独立复算，0 mismatch。Owner worktree仍为 `agent/codex/P02PRE-R1H@dd5d2e3bc8e0702da9d059131f6364a997897661`，parent=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`，tree=`8cf6cf2dec8b375746b4c423f3c00ffe611a60d7`，controlled status=0 bytes，index SHA=`DCBE24A2827B8465807C5627523DC6570346278935DA4A71BEF3FF969A9341FE`。review pins=`verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-pins-20261012.json` SHA=`DE58847092D56476B54323E0FE4E8103D8E7FBD99D47D11C6F191289BEEBED51`。
- Root adjudication=`verification/P02/p02pre-r1h-integration-protocol-r2-adjudication-20261012.md` SHA=`B6115EABF14381FADC7609863FDCB090FE33947DEA1C5F4E86766B139E40BBC6`；`INT-R5-001/002=FIXED_STATIC_PROTOCOL` accepted. Execution evidence=`verification/P02/p02pre-r1h-integration-execution-20261012.json`（当前冻结版4528 bytes / `C08365428F0FD718ACAF66BA6472E983CDD577965C646FF3512FD4C66A4005BD`；preflight/S0前将更新该同一路径并再记录最终hash）。Task、Plan、Status、Index均已刷新到新阶段。
- 本Root在审阅过程中遇到的命令构造错误均为只读且无文件副作用：PowerShell命令需将`HEAD^{tree}`作为引号参数；owner worktree index须用`git rev-parse --path-format=absolute --git-path index`而非假设`.git`为目录；clean status返回null须按0 bytes处理。修正后Pin复算通过；无一错误输出被当作有效Git证据。
- 当前状态=`POST_REVIEW_INTEGRATION_PRECHECK / ACTIVE`。本条记录是治理刷新快照，**不是S0**。还未执行ACL/ADS/volume metadata查询、未创建stage/recovery/API backup、未调用Replace。唯一四路径、源/目标hash及fail-stop状态变更规则以Task §Post-initial integration repair rule为准；下一步是执行全只读preflight、记录S0与证据，然后仅在所有条件满足后CreateNew stage/recovery并单次调用经Review的三参数Replace。
- AC4仍=`NOT_VERIFIED`；Round4真实`FAILED`证据保留；Round5 parser/selfcheck/preflight未运行。AC1 frozen main/scratch status/index baseline仍=`UNPROVABLE`，未获AC1 PASS；因此capture尚未授权执行。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；系统AC1–AC7=`BLOCKED / NOT_RUN`。
- Gate准确值：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。技术项不改记PASS。无Windows Sandbox操作；未关机。
- 实际模型：Root=`gpt-6-luna/max`；优先`gpt-6.1-sol/high`不可用；Reviewer模型/力度=`UNKNOWN`。Owner已完成并不审核自身工作。用户授权继续必要的P02PRE、宿主验证、Build/Cargo、AC1–AC7、修复/Review/重测/集成；本次静态批准不等于运行结果或Gate授权升级。用户要求全部工作真正完成并安全收口后关机。

## S0：只读执行前核验通过，写入尚未开始

- Captured with PowerShell 7.6.6/Core, process C:\Program Files\PowerShell\7\pwsh.exe, PID 47232; current identity=HOME-MY\49745 / SID=S-1-5-21-2196946971-914346751-4210154634-1001 / authenticated=True / administrator=False。
- Owner source再核验=agent/codex/P02PRE-R1H@dd5d2e3bc8e0702da9d059131f6364a997897661，parent=7e7d0bce8dd86a2302d2a9eb278702d9c70354ff，tree=8cf6cf2dec8b375746b4c423f3c00ffe611a60d7，controlled status=0 bytes，index=DCBE24A2827B8465807C5627523DC6570346278935DA4A71BEF3FF969A9341FE；source=57648 / 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA。旧destination=57623 / EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1；普通非reparse文件。独立CRLF-to-LF比较确认候选只插入一条已审查allowlist literal（candidate line 376）。
- 目标路径全部解析于同一目录=G:\CODEX\New Manga\verification\P02、ready NTFS volume=G:\；source与destination的已检查父级均非reparse。stage/recovery/API backup经File.GetAttributes严格absence及git check-ignore只读查询均通过。destination ACL SDDL、parent ACL SDDL、alternate stream清单和默认流hash已经采集；仅发现默认流，长度/哈希与旧目标一致。attributes/timestamps/file identity=NOT_VERIFIED。
- 初始受控status S0 porcelain-v2 NUL multiset=985 records / 65851 bytes / SHA-256 926590B47D936EA3F896C0188717E8113488DDFDD470EEA0BDDCE8F43E4705F9；main index before/after=214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C（stable）。完整record数组在execution JSON的S0.records；JSON=verification/P02/p02pre-r1h-integration-execution-20261012.json SHA-256=0F1C3A7750468FA043D8BCDCE942F3BE767A508742016C3F58EBB3A1E0944155。
- S0采集时四路径状态：destination为上述Round4 bytes；stage/recovery/API backup均absent。尚未写入任何一个四路径目标，也未调用Replace。授权执行路径严格限于Task中的四路径。
## S0后治理文档冻结；S1写入准备

- Plan/STATUS/Index/Task已刷新到precheck PASS、单文件集成ACTIVE；这些路径在S0中已存在。当前受控porcelain-v2记录multiset与S0逐项相同；所有S0 records完整保存于execution JSON。main index仍为214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C。当前全局v1 snapshot=985 records / 65837 bytes / 1B6482311494E7D07C45AA7C1FFBBEE93B31A883F5A613CFAC4A9934B02344D1，exit=0/stderr=0。
- 刷新后证据hash：doc/tasks/P02PRE-R1H.md=34670/D57058797677EED223F2385D4A13883E979125BE9067D1171CEB699B1CB0BE5D; doc/REBASELINE_PLAN.md=293835/E2C64D17C0C249BE5939BDF0C3EEF2A7BC41D1621535485EC5101E248541E376; doc/STATUS.md=298417/F8430C884373DA57AA2E23C5FD8EF1C2076D74C05DCEC7304438D8BBF0A6E610; doc/00_INDEX.md=62189/279E11107C9B455C0EBB83B06F82F4EDAB99865C7EEDF081BC17528BA956254B; verification\P02\codex-checkpoint-p02pre-r1h-integration-protocol-review-r2-active-20261012.md=12589/62F269FD581B73119F7E7D2DBD9C9679CD542593683E526BD803A35C534F59E0。
- execution JSON=verification/P02/p02pre-r1h-integration-execution-20261012.json，当前=88412 bytes / 7D9BDEC7E1D8BE29938C3CA287A775C6455A8B02AADAB9967AA06662F2D719FD；checkpoint已先于四路径写入并存在。stage/recovery/API backup经严格absence复查仍不存在，Replace calls=0。
- 下一步只执行两个CreateNew，并采集S1；若S1 status delta不是恰好新增stage与recovery、index不变或四路径任一metadata不符，则停止并保留partial files，不调用Replace。
## S1创建/核验失败：fail-stop，Replace未调用

- 异常：System.Management.Automation.MethodException: 找不到“Open”的参数计数为“6”的重载。
   at System.Management.Automation.ExceptionHandlingOps.CheckActionPreference(FunctionContext funcContext, Exception exception)
   at System.Management.Automation.Interpreter.ActionCallInstruction`2.Run(InterpretedFrame frame)
   at System.Management.Automation.Interpreter.EnterTryCatchFinallyInstruction.Run(InterpretedFrame frame)
   at System.Management.Automation.Interpreter.EnterTryCatchFinallyInstruction.Run(InterpretedFrame frame)
- 四路径实测状态与受控status/index详见execution JSON failure对象；保留全部partial files，不清理、不重试、不恢复、不调用Replace。Replace调用计数=0。
## Root adjudication of pre-S1 invocation error

- First CreateNew orchestration attempt stopped at binder resolution: File.Open(string, FileMode, FileAccess, FileShare, int, FileOptions) overload does not exist; use FileStream constructor. No stage handle opened, stage/recovery/API backup all remain absent; destination and Owner source hashes match; S0 porcelain-v2 raw hash and main index are unchanged; Replace call count=0.
- Classification=ORCHESTRATION_CALL_SIGNATURE_ERROR_BEFORE_IO. This was not an OS/API test failure and did not consume the one-shot Replace. Correction is to use the six-argument FileStream constructor, recheck S0/pins/absence, then attempt only CreateNew stage/recovery. No file cleanup or recovery was needed.
- Existing failure detail is retained in execution JSON; new adjudication is in failure.rootAdjudication. Evidence currently=167671 bytes / 5654335F0CB3A3F246AA9F14A0A617EE166F91EA399E7AC5168C75BD8637FDC2.
## S1：CreateNew stage/recovery完成；Replace尚未调用

- Stage从冻结Owner working-tree source经FileStream(CreateNew)写入并Flush(true)：57648 / 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA，regular/non-reparse；Recovery从Round4 destination经CreateNew复制并Flush(true)：57623 / EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1。未创建其它目标文件。
- 调用前四路径的默认数据流、ACL SDDL及stream metadata已采集。Destination仍为旧bytes/hash且ACL未变；parent ACL SDDL与S0相同；stage/recovery读回pin匹配；API backup仍absent。Attributes/timestamps/file identity仍NOT_VERIFIED。
- S1 porcelain-v2 NUL multiset=987 records / 65986 bytes / SHA-256 F6612F21217070E3078ED259125C249AE8FFDDA5DA385D3F3772606E78478430；相对S0只新增两条untracked record，精确为stage与recovery；删除=0；main index=214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C，与S0相同。完整S1 records在execution JSON S1.records。
- execution evidence=247420 bytes / F0118E378B64716F9FF3501132EED23B70F1A458C825304874F953F6AD38E5D8；Replace调用计数=0。只有这一S1状态被再次核对后才允许执行三参数Replace。
## 调用前guard helper误报；S1独立复核通过

- 初次调用前的本地Same-Multiset辅助函数返回false，导致在Replace前fail-stop；该检查未写任何四路径目标，也未调用Replace。重新用ProcessStartInfo原始stdout bytes与独立Dictionary差分复算：当前S1 count/bytes/raw SHA与冻结记录逐项一致；added=0、removed=0；index相同。destination/stage/recovery与S1 pins保持，API backup absent。
- 归类为Root验证helper false-negative，不是文件/Git状态变化。execution JSON的precallRevalidation保留该经过及修正结论；当前=248068 bytes / 8FC8419F73FF0CA331F6503941FE06D00663CA61BABE51BDC4D7C925798AA3E7。下一步仅以已复核的raw hash、count、add/remove差分实现最终guard，复核通过才调用一次Replace。
## 集成fail-stop：不得重试、清理或自动回滚

- classification=BEFORE_REPLACE replaceCalls=0 returnedNormally=False exceptionType=System.Management.Automation.RuntimeException HResult=-2146233087 exception=System.Management.Automation.RuntimeException: final pre-call raw S1 status mismatch
- 四路径状态、porcelain-v2 records与index SHA详见execution JSON integrationFailure对象；保留全部部分文件。不得再次调用Replace；仅Codex单独adjudicate后决定是否恢复。
## Root adjudication of final pre-call guard false-negative (2026-10-12)

- 上次guard报错为`final pre-call raw S1 status mismatch`，但其失败对象自身记录raw bytes=`65986`、SHA-256=`F6612F21217070E3078ED259125C249AE8FFDDA5DA385D3F3772606E78478430`，与冻结S1相同；`statusCount=1`字段与该raw capture矛盾。Root将其分类为`ROOT_GUARD_FALSE_NEGATIVE_BEFORE_REPLACE`；具体局部计数器成因=`UNPROVEN`，不伪造根因。
- PowerShell 7.6.6/Core、PID 10988用Git原始stdout NUL bytes重新解析得987 records/65986 bytes/同SHA；与S1做ordinal multiset对比，added=0、removed=0。main index SHA=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`不变。Destination、stage、recovery、API backup 4/4均与S1的exists/type/attributes/regular/non-reparse/length/hash/ACL SDDL/stream签名匹配。
- Replace调用计数仍为0。此前一次status argv因pathspec前有空格而被Git拒绝（exit=128）；属于只读命令构造错误，未读取排除路径、未产生写入。修正后的精确argv采集exit=0/stderr=0并通过S1核验。
- Codex单独adjudication：此前BLOCKED边界没有发生Replace；经此证据可继续执行唯一一次已独立Review的`[IO.File]::Replace(stage,destination,apiBackup)`。调用前须在同一PowerShell进程内再验证S1 raw hash/bytes/count、多重集增删=0、index及4路径pin；任一不匹配则不调用。Replace一旦进入调用，异常也不得重试、清理或自动回滚。
- 证据明细追加于同路径`p02pre-r1h-integration-execution-20261012.json`的`integrationFailure.rootAdjudication`与`commandConstructionErrors`。

## 单次Replace执行边界已进入（2026-10-12）

此次计划唯一调用数=1。execution JSON在最终复核前记录CALL_MAY_HAVE_BEEN_ENTERED；若进程意外中断，须先只读核查四路径与Git状态并由Codex adjudicate，禁止盲目重试。脚本先做同进程最终S1校验，全部通过后紧接着调用一次三参数Replace，再采集post-state。


## 单次Replace结果（2026-10-12）

``json
{
  "PowerShell": "7.6.6",
  "PID": 30280,
  "CallEntered": true,
  "ReturnedNormally": true,
  "CallCount": 1,
  "Status": "RETURNED_POSTCHECK_FAILED",
  "PrecallRecords": 987,
  "PrecallBytes": 65986,
  "PrecallSha": "F6612F21217070E3078ED259125C249AE8FFDDA5DA385D3F3772606E78478430",
  "PrecallAdded": 0,
  "PrecallRemoved": 0,
  "PostRecords": 987,
  "PostBytes": 65998,
  "PostSha": "290F9059F1D6E920F44CACC781CB86CB9C78634BF8695C32C7A93E8C28EC7FD2",
  "PostAdded": "? verification/P02/p02pre-r1h-selfcheck-round4-integrated-backup-20261012.ps1",
  "PostRemoved": "? verification/P02/p02pre-r1h-selfcheck-round5-stage-20261012.ps1",
  "IndexBefore": "214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C",
  "IndexAfter": "214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C",
  "Postcheck": false,
  "Exception": null,
  "PathStates": [
    {
      "name": "destination",
      "state": {
        "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02pre-r1h-selfcheck.ps1",
        "exists": true,
        "type": "File",
        "attributes": "Archive",
        "isReparse": false,
        "regularFile": true,
        "bytes": 57648,
        "sha256": "977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA",
        "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1301bf;;;AU)(A;ID;0x1200a9;;;BU)",
        "streams": [
          {
            "name": ":$DATA",
            "length": 57648,
            "sha256": "977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA",
            "kind": "default"
          }
        ]
      }
    },
    {
      "name": "stage",
      "state": {
        "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02pre-r1h-selfcheck-round5-stage-20261012.ps1",
        "exists": false,
        "type": null,
        "attributes": null,
        "isReparse": false,
        "regularFile": false,
        "bytes": null,
        "sha256": null,
        "sddl": null,
        "streams": []
      }
    },
    {
      "name": "recovery",
      "state": {
        "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02pre-r1h-selfcheck-round4-recovery-20261012.ps1",
        "exists": true,
        "type": "File",
        "attributes": "Archive",
        "isReparse": false,
        "regularFile": true,
        "bytes": 57623,
        "sha256": "EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1",
        "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1301bf;;;AU)(A;ID;0x1200a9;;;BU)",
        "streams": [
          {
            "name": ":$DATA",
            "length": 57623,
            "sha256": "EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1",
            "kind": "default"
          }
        ]
      }
    },
    {
      "name": "apiBackup",
      "state": {
        "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02pre-r1h-selfcheck-round4-integrated-backup-20261012.ps1",
        "exists": true,
        "type": "File",
        "attributes": "Archive",
        "isReparse": false,
        "regularFile": true,
        "bytes": 57623,
        "sha256": "EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1",
        "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1301bf;;;AU)(A;ID;0x1200a9;;;BU)",
        "streams": [
          {
            "name": ":$DATA",
            "length": 57623,
            "sha256": "EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1",
            "kind": "default"
          }
        ]
      }
    }
  ]
}
``n
结果已追加到execution JSON；call count=$(System.Management.Automation.OrderedHashtable.replacementAttempt.callCount)，状态=$(System.Management.Automation.OrderedHashtable.replacementAttempt.status)。若已进入调用，绝不重试/清理/自动回滚。

## Codex adjudication of postcheck helper false-negative (2026-10-12)

- Executor原始状态`RETURNED_POSTCHECK_FAILED`保留；根因已查明：实现把调用前S1中API backup的`exists=false`沿用为调用后期望值，没有按协议要求把它与旧destination比较。不是File.Replace失败，也没有第二次调用。
- Codex在PowerShell 7.6.6/Core、PID 42568只读复算S2：987 records / 65998 bytes / SHA-256=`290F9059F1D6E920F44CACC781CB86CB9C78634BF8695C32C7A93E8C28EC7FD2`。S1→S2新增仅API backup、删除仅stage；S0→S2仅新增API backup与recovery、无删除。Main index仍=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。
- 四路径逐项通过只读核验：destination=`57648 / 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`；stage absent；recovery及API backup均=`57623 / EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1`。所有已查路径均为非reparse普通文件；destination/recovery/backup的ACL SDDL匹配Round4 destination；每个现存文件均只有default stream且其长度/hash相符。
- Root adjudication=`INTEGRATION_STATE_PASS_WITH_EVIDENCE`。Round5 bytes现已集成；Replace调用恰好一次且正常返回。属性/时间戳/file identity仍=`NOT_VERIFIED`。AC4 parser/selfcheck/no-profile preflight未运行，必须继续；没有解除Build Gate或改变AC1–AC7状态。
- 最近一次只读postcheck的JSON formatter曾失败（duplicate key Value），没有写入或目标调用；修正后的诊断输出如上。原始executor误报与Codex adjudication分别保留在execution JSON `replacementAttempt`。

## AC4 Round5 verification dispatched in-process boundary (2026-10-12)

即将用PowerShell 7.6.6/Core执行：直接Parser解析capture/selfcheck；pwsh.exe -NoLogo -NoProfile -NonInteractive -File p02pre-r1h-selfcheck.ps1；以及从Round4冻结证据逐字节复用的no-profile capability getter argv。唯一新结果路径=$selfEvidencePath与$engineEvidencePath，均须absent+unignored并用CreateNew保存。期间不得运行capture、Git查询以外getter、Build/Cargo或system AC。


AC4复跑记录：第一轮selfcheck子进程已结束，但编排器结果对象未保留stdoutBytes，exit/stdout=NOT_CAPTURED；未创建证据路径、未运行capture。使用显式PSCustomObject原始byte collector重跑；engine preflight第一次尚未启动。

## Round5 AC2 failed; engine capability preflight passed (2026-10-12)

- PowerShell 7.6.6/Core 直接Parser解析 `p02pre-r1h-capture.ps1` 与 integrated `p02pre-r1h-selfcheck.ps1` 均 `errors=0`。
- No-profile selfcheck实际命令=`pwsh.exe -NoLogo -NoProfile -NonInteractive -File verification/P02/p02pre-r1h-selfcheck.ps1`，PID=48356，exit=1，stdout=0；stderr=416 bytes / SHA-256=`8302CDA30C0359673F2873E58CC2D8E8549F675AECB8518A20B25FF86C019E40`，失败位于 `Test-RepositorySkipAstContract` 实际组件循环控制流断言（selfcheck line 648）。Selfcheck artifact=`verification/P02/p02pre-r1h-selfcheck-round5-20261012.json`（4076 / `8F8127718FD1B07AD8031DC71CCE43A55258BF4B36D8694D1520A3197C77340C`）。AC2=`FAILED`，不是Parser或OS版本失败；capture未调用。
- 独立 no-profile child capability preflight=`PASS`，PID=45772 / exit=0 / stderr=0；PS 7.6.6/Core/FullLanguage、PSHOME、Utility/Security modules、Get-FileHash/Get-Acl均通过。Evidence=`verification/P02/p02pre-r1h-engine-preflight-round5-20261012.json`（6990 / `72FA81E395EE62A0D85F6333C8D5A05A976C6B6FEDC333217F322B0EC6375C2F`）。该预检不能覆盖selfcheck失败，故AC4=`BLOCKED_BY_AC2`。
- 两次早先的wrapper selfcheck命令均启动并结束，但wrapper没有保留stdout/exit，记录为`RUN_COMPLETED_RESULT_CAPTURE_FAILED`；第三次直接流读取取得上列实际失败。随后摘要命令因本地未定义`Dict` helper中断；两个CreateNew evidence文件已成功落盘，未清理/覆盖，Root从文件复读并独立复算status。
- S2→S3只新增两项：上述selfcheck/engine evidence；无删除。S3 porcelain-v2 NUL=`989 records / 66127 bytes / 0E34A1B0A609F2771EE25CA74A3B88287F2C4410F816F4F17DB691053B02378A`；main index仍=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。完整状态和child证据见execution JSON。
- 下一步为Round6：Codex Owner在独立 worktree 仅修复 selfcheck AST predicate；root负责集成与重测；非作者Reviewer独立Review，不得作者自审。AC5/capture/Build/Cargo/system AC没有运行，Gate原值不变。