# Codex adjudication：P02PRE-R0S1

## 元数据与对象绑定

- Task=`P02PRE-R0S1`；Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- Repo=`G:/CODEX/New Manga`；branch=`main`；reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Review 前冻结对象：Task `8303 bytes / BD73A543B2DBA2A28A38493769B64770C88DB14188D6BBD97189EA903082E2AD`；manifest `22925 bytes / CA293C34473D25E406E72B7DB05AC9364A69544D41214B93857ABAD11FEC6DE3`；查询前 checkpoint `7583 bytes / EE26F209B56F5A249B5BED9BFE9E5E54A6FEDBBE062F292A2F3032D66C63AEDB`；capture evidence `5489 bytes / 05C2DD247D3B0238809DCB90E62B633AAD6B4E777186E4025CD371B371F3FCBD`。
- DSH Review=`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`；P0/P1/P2/P3=`0/0/2/5`；report=`verification/P02/p02-readonly-preflight-r0s1-review-20261011.md`，`21262 bytes / 2F27B72FB40D43F7B4DD40925E75283A151EC7E72327D1FD2542F6135DC0E7A0`。Review stdout 与归档 report byte-for-byte 同哈希。DSH 未独立复算输入 hashes 或 HEAD；Codex 在派发前核验 Task/manifest/checkpoint/evidence 对象 hashes。DSH session=`session-dec4e233-a752-4e83-a658-ca10645d2a60`，mount exit=`0`。
- Review prompt=`3904 bytes / 602402CDB8BBA95B339A7BA62CB0D32502D5C73A989AE6B6D6BFEF031253FF23`；DSH dispatch exit=`0`；exit artifact=`0`；stderr 原文留在固定日志，不在此重复；mount log=`315 bytes / 8A613B6D47C675616573B2433ACDACF2EB4B020CA3B62823ECF71E33CE35486C`。

## 对运行结果的裁定

本轮冻结 runner **已启动但不完整**，不是 `NOT_RUN`。工具返回的 shell exit code=`0` 仅表示 PowerShell runner 正常返回；stdout 明确为 `STOP_UNTRUSTED_OR_UNAVAILABLE_BUILTIN_MODULE`，不是目标采集成功或 Gate PASS。身份 getter 返回固定用户/SID、authenticated，且无 thread impersonation。`$modulesTrusted` 前置条件为 false 后，控制流在 `Get-PSDrive`、任何 G: path `Get-Item` 与 leaf `Get-ChildItem` 之前停止；本轮没有 scratch path 或其祖先结果。

stdout 的 `ManagementPath=` 与 `UtilityPath=` 空白**不能证明模块计数为零、模块未安装或文件缺失**。冻结 body 只在模块计数恰为 1 时输出路径；所以准确事实是“没有证明当前已加载模块数量/路径满足冻结的可信谓词，且模块计数未记录”。证据文档中“两个模块均未预加载”的文字强于原始输出，本裁定不采纳该推断。`$PSHOME` 生成的 expected path 字符串只证明脚本使用了这些期望字符串，不证明模块文件存在或实际 PowerShell executable 的路径/版本。

`functions.exec_command` 的调用记录表明 `cmd` 由 manifest fenced body 提供，但没有另存本次实际 `cmd` 原文或字节 hash。因此命令的来源是 Owner 记录；不能事后声称获得了字节级命令绑定。capture stdout 未含 UTC start/end 时间；工具结果未提供精确时间戳或独立 stderr 字段；这些缺口均保留 `UNPROVABLE`，不得以派发/检查文件的时间回填。`login=false` 不证明 PowerShell profile 未运行，shell startup/profile effects 仍=`UNPROVABLE`。

## DSH findings adjudication

| Finding | 级别 | Codex 处置 | 状态与影响 |
|---|---:|---|---|
| F-01：`Get-ChildItem` 与“不得读取 child name/metadata”的字面合同冲突 | P2 | `ACCEPT / DO_NOT_EXECUTE`。该 getter 会枚举并返回 child entries；其 `Name` 等字段进入 PowerShell 对象，不能同时作出操作层“从未读取 child name/metadata”的保证。此 runner 未到达该命令，未产生目录项泄露或目录状态证据。本 R0S1 scope 内该 direct-child inventory 方法=`NOT_SAFE_FOR_R0`；不修改已冻结 manifest 后重跑、不更换方法。若后续有更窄的无副作用 getter，须另建 Task、静态审查并重新 pin。 |
| F-02：本次 session 的模块可信前置条件未满足 | P2 | `ACCEPT_WITH_LIMIT`。以 stdout 的 `Status=NOT_SAFE_FOR_R0` 作为本次 runner 停止依据；不推断模块 count 或未来 session 状态。禁止重试/导入模块/放宽模块检查。R0S1 没有其他与该模块门槛独立且已冻结的路径查询。 |
| F-03：leaf predicate 与 runner safety 分类需分开 | P3 | `ACCEPT / CLARIFY`。两个 leaf 的 empty-or-absent **谓词**仍=`UNPROVABLE`；本 runner 的模块/继续执行安全条件=`NOT_SAFE_FOR_R0`；拟议的 `Get-ChildItem` 方法在当前 no-name-read 合同下也=`NOT_SAFE_FOR_R0`。两种分类描述不同对象，不互相替代。 |
| F-04：模块空路径不能推出“未预加载” | P3 | `ACCEPT / OVERRIDE`。以本节“模块计数和路径谓词未证明”为准；evidence 中更强的 prose 不作为事实采用。没有模块安装/文件存在性结论。 |
| F-05：实际 cmd 无字节绑定 | P3 | `ACCEPT_AS_LIMITATION`。保留 Owner 调用记录，不伪造 command hash；该限制不影响 STOP 记录的原始文本，但降低 runner-to-manifest 绑定强度。 |
| F-06：shell selector 与 executable identity | P3 | `ACCEPT_AS_LIMITATION`。`shell="powershell.exe"` 记录为工具 shell selector；stdout 中 `$PSHOME` 期望字符串不独立证明 actual executable path/version。不得重新查询已退出进程或外推版本。 |
| F-07：exit 与时间要求的归属 | P3 | `ACCEPT / CLARIFY`。`exit_code=0` 是 exec 工具返回的 shell 退出状态，不是目标检查通过；精确 capture 时间与逐目标时间窗=`UNPROVABLE`，因为没有目标查询且输出/工具记录无该时间戳。 |

## P02PRE 分类更新

| 条件 | 最终分类 | 依据/范围 |
|---|---|---|
| R0 既有的 host identity、固定对象 metadata/ACL descriptor、受限环境字符串、固定 WER 候选 snapshot、13 项 pre/post hash | `PASS_WITH_EVIDENCE` | 只接受 R0 adjudication 的当时点和精确对象范围；不外推 future controller/LPAC 行为或完整保护集。 |
| 两个登记 scratch leaf 的当前 empty-or-absent | `UNPROVABLE` | 本轮未查询任一 ancestor/leaf 或列举 children；没有 `PASS_WITH_EVIDENCE` 或 `FAILED`。 |
| 本次 R0S1 runner 的可信模块前置条件 | `NOT_SAFE_FOR_R0` | trusted module path/count predicate 未被证明，按 frozen STOP 分支结束。 |
| R0S1 冻结 `Get-ChildItem` direct-child inventory 操作 | `NOT_SAFE_FOR_R0` | 与本 Task 的 no-child-name/metadata read promise 不兼容；未执行。 |
| capture 精确时间、shell profile startup effects、实际 executable identity、cmd bytes binding | `UNPROVABLE` | 未从当次执行取得相应字段/独立对象绑定；不回填、不重查。 |
| effective LPAC/canary write boundary、实际 child/process/cache/TEMP/write closure、未来 freshness/T0 | `REQUIRES_ACTIVE_TEST` 或沿用 R0 的 `UNPROVABLE` | 只有既有分类与精确条件继续适用；本轮不改变。 |
| profile-folder no-side-effect/path、详细 token/elevation、完整 ancestry/file IDs/hardlink/ADS/hash、WER global/per-image policy/views/destination/T0、private registry absence | `NOT_SAFE_FOR_R0` 或 `UNPROVABLE`，按 R0 adjudication 原行保持 | 本轮无新 OS 证据；private registry 技术状态仍=`UNPROVABLE`，仅 owner waiver。 |

本任务完成为 `DONE / ACCEPTED_AS_LIMITED_READ_ONLY_STOP_EVIDENCE`，仅关闭一个 capture-stop/evidence-delivery slice；scratch emptiness 与总体 P02PRE 未解决。R0S1 无剩余安全且已冻结的 READY 查询。是否存在其他可安全补充的只读 query，交由下一项独立静态候选审查裁定；在它完成前不执行新 query。

## 风险、Gate 与授权

原用户 waiver 保持不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。不新增 waiver，不把技术条件伪记为 `PASS`。profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。本 Review 与 adjudication 均不解除 barrier。

## Review 期间操作记录

- `dsh --version` → `0.2.0-rc.2`，exit 0。
- `dsh headless '只回复两个字：收到'` → `收到`，exit 0。
- DSH Review dispatch 使用冻结 prompt，CLI exit 0，session 已挂载；stdout 原样固定，stderr 未在此展开。
- 一次初始 hash 结果格式查询发生 PowerShell parser error，未执行查询；修正后成功读取相同对象 pins。
- DSH dispatch 的首次路径保护表达式发生 PowerShell `Test-Path` 参数绑定错误；该错误不是 terminating error，固定 prompt 随后仍被 DSH 启动。派发前独立路径检查显示所有 Review 输出文件不存在，未覆盖已有文件；输出在 dispatch 后检查并成功归档。
- 一次在 DSH 尚未完成时尝试读取 `.exit` 的诊断命令返回 file-not-found，并产生后续 null 处理错误；没有写入目标文件。待 DSH 实际结束后 `.exit` 正常记录 `0`。
- 本轮没有执行 parser、产品测试、OS/API/profile/registry/ACL/path 查询、build/Cargo、AC1–AC7、Sandbox 或任何系统/项目状态写入（除授权 Task/Review/evidence 文档与 dispatch 日志）。

