---
task_id: P02
reviewer: Codex independent Reviewer / orchestration_docs_review
author: Codex Lead
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_document_sha256: 427219AC35CB6407D4CB5BD5D2FD6F247866D8FD2E34644459A2A808EFABBC18
decision: approved
---

# P02 提权观测/强制方案静态评估 r1 · 独立 Review

**结论：APPROVED，仅针对被冻结的静态评估文档。** P0/P1/P2/P3=`0/0/0/0`；在记录范围内未发现实质问题。报告正确区分辅助观测、有限内核候选与尚未满足的完整闭包证明；没有把静态研究、用户选择或本次批准转为系统操作、测试 PASS 或 P02 Gate 放行。

## 对象、范围与授权

主仓 `G:/CODEX/New Manga`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。本次审查该 HEAD 上的冻结未提交文档，非代码实现 Review。Reviewer 不是报告作者；不修改任何受审对象、Task、治理文档、代码或测试。

本次本地 SHA-256 与派发 pins 一致：

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `codex-elevated-isolation-method-assessment-20261010-r1.md` | 19484 | `427219AC35CB6407D4CB5BD5D2FD6F247866D8FD2E34644459A2A808EFABBC18` |
| `codex-p02-human-required-decision-20261010.md` | 4856 | `316724F25DE820BD43080534A075A9256B11105F3D22DF36BE19F24A28A0E72C` |
| `doc/tasks/P02.md` | 138975 | `22A85DCF7F37461DE3D261330BB5B48E272B721596FDE9E1C4F9A80390B30A00` |

授权依据为决策包“用户裁决记录”与 Task `:605–611`：用户已选静态评估提权方案，但未授权安装/启动 ETW、observer、driver/service、管理员/LocalSystem，或改变 BCD、Secure Boot、签名、registry、ACL、label、profile、TEMP/cache、scratch、运行目录。报告 `:3`、`:11`、`:15–21`、`:98` 与此一致。Task 中旧 HUMAN_REQUIRED 段已标历史，不作为当前裁决。

## Findings

无新增 finding。没有将未来 implementation Task 尚需冻结的覆盖矩阵、签名包、主机版本、安装路径、IOCTL 或卸载实现视为本次研究遗漏：报告本身已在 `:8`、`:29`、`:33`、`:53`、`:59` 明列这些未知项并据此阻断执行。

## 技术与边界核验（Architecture）

| 核查项 | 受审报告位置 | 审查结论与一手证据 |
|---|---|---|
| Job 不是全树证明 | `:7`、`:27`、`:70` | 普通 CreateProcess 后代默认进入 Job，WMI 创建和 breakaway 有例外；completion-port 通知一般不保证送达。报告没有把缺少事件当成没发生事件。[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) |
| Process callback 能力与身份 | `:8`、`:29–31`、`:58` | 父 PID 与 creator PID 可不同；CreationStatus 可阻止创建；FORCE_INTEGRITY 注册要求及卸载前撤销 callback 均有文档支持。报告未声称能自动归属 broker 请求或覆盖 impersonation/句柄传递。[PS_CREATE_NOTIFY_INFO](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/ns-ntddk-_ps_create_notify_info)、[PsSetCreateProcessNotifyRoutineEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex) |
| 注册操作、cached/paging I/O | `:8`、`:33`、`:72` | Minifilter 只收到注册的操作；read/write registration flags 还可忽略 cached/paging I/O。报告将其列为必须单独验证的 coverage matrix，没有承诺仅注册 WRITE 就覆盖所有写入。[注册回调](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/registering-preoperation-and-postoperation-callback-routines)、[pre-operation callbacks](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/writing-preoperation-callback-routines) |
| Requestor provenance | `:31`、`:33`、`:60` | RequestorProcess 可为 NULL，返回进程是 requesting thread 当前附着进程；预操作也可能在 system worker 中执行。仅按当前线程/PID 归属不充分是合理推论；报告要求固定 handle/file/stream provenance，归属不明停止目标 run，避免全局拒绝。[FltGetRequestorProcess](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nf-fltkernel-fltgetrequestorprocess)、[callback context](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/writing-preoperation-callback-routines) |
| Section 与映射限制 | `:8`、`:29`、`:33` | SyncTypeOther 不可失败；SyncTypeCreateSection 文档仅明确允许内存不足错误。报告据此不承诺通用拒绝可写映射，既有 mapping/延迟 I/O 继续未闭合。[Section synchronization](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/flt-parameters-for-irp-mj-acquire-for-section-synchronization) |
| Metadata/security/filter stack | `:33`、`:73–75` | SET_INFORMATION 属于 metadata 设置，具体 FILE_INFORMATION_CLASS 需细分；driver-generated I/O 从指定 instance 以下穿过 stack，报告要求 altitude/stack 与对象归属验证。security 设置亦属于需覆盖的权限改变。[SET_INFORMATION](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-set-information)、[generated I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/i-o-requests-generated-by-the-minifilter-driver)、[SET_SECURITY parameters](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/flt-parameters-for-irp-mj-set-security) |
| 特权/签名/安装 | `:29`、`:53`、`:58` | FilterLoad 要 SeLoadDriverPrivilege；签名要求依 Windows 版本而异。报告拒绝 TESTSIGNING、安全启动变化和默认 LocalSystem，不猜 DriverStore/registry 落点。具体 package 是否可部署是 UNKNOWN，不由本次来源核查确认。[FilterLoad](https://learn.microsoft.com/en-us/windows/win32/api/fltuser/nf-fltuser-filterload)、[签名要求](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/kernel-mode-code-signing-requirements--windows-vista-and-later-) |
| 卸载与恢复 | `:64–66`、`:77` | 撤销 process callback 要等待正在执行的 callback；minifilter teardown 必须处理 pending work、停止排新工作，仍有引用/I/O 时不能当作已恢复。报告先停止目标 run、保留现场、再按生命周期卸载，仅删除本轮明确对象；失败记 CLEANUP_BLOCKED，不以一次卸载成功冒充恢复证明。[callback removal](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex)、[加载与卸载](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/loading-and-unloading) |
| ETW 权限与有限证据 | `:7`、`:28`、`:51`、`:57`、`:64` | NT Kernel Logger 控制需要管理员/LocalSystem；一般 session 还存在其他受支持账户权限。报告以 API 为准并不默认扩权。lost counters 非零阻断、零不证明 provider 全覆盖是合理的保守结论。[StartTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea)、[EVENT_TRACE_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties) |
| ETW 文件路径/ACL | `:51` | ETW 不创建父目录，日志采用父目录 ACL；报告只提出未来授权后建立 run 目录、核验 owner/ACL、再启动 trace，指定 LogFileName/size/buffer 并禁止旁落主机 TEMP/cache。未来 ACL 的确切值与写入身份尚未实施，不冒充主机事实。[ETW 文件与安全描述符](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties) |
| Profile absent blocker | `:9`、`:66`、`:79`、`:100` | GetAppContainerRegistryLocation 说明当前 profile/user 的存储，没有定义不存在目标的无副作用检查；CreateAppContainerProfile 创建 data store 与 folders/registry。报告保留未找到证明方式的 BLOCKED，不宣称数学上或所有 Windows API 都不可能。[registry location](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[profile creation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) |

Architecture 结论：技术限制、授权边界及未来 deployment/cleanup 前置条件描述足够支持这份静态评估；没有可直接执行的 READY 方案。受控 run 的归属、完整 I/O 覆盖、驱动故障安全和可卸载性仍需将来固定实现与独立验证，以上表格不是这些能力已实现的证明。

## 实际来源与执行记录（Verification）

实际运行的本地命令仅限 PowerShell 的 `git rev-parse HEAD`、`Get-Item`、`Get-FileHash -Algorithm SHA256`、`Get-Content`（带行号/尾部）、`rg -n` 和指定输出文件 `Test-Path`。上述只读读取和 pin 复算均成功；目标 Review 文件起初不存在。未执行 Windows API、ETW、driver/service、管理员/LocalSystem、OS inventory/probe、build/Cargo/产品测试或 Sandbox；没有系统修改。

实际访问报告 `:70–80` 链接的 Microsoft Learn 文档：Job Objects、PS_CREATE_NOTIFY_INFO、PsSetCreateProcessNotifyRoutineEx、Registering pre/post callbacks、Writing pre-operation callbacks、FltGetRequestorProcess、IRP_MJ_SET_INFORMATION、Section synchronization、Minifilter-generated I/O、FilterLoad、Loading/unloading、EVENT_TRACE_PROPERTIES、StartTraceA、GetAppContainerRegistryLocation、CreateAppContainerProfile、kernel-mode signing requirements、TESTSIGNING option。网页工具读取了各关键段落；页面模板虽然带有登录提示，以上条目仍返回可读正文，未据登录提示跳过核查。

来源读取限制：报告 `:74` 指向的 `kernel/irp-mj-set-security` 原链接两次返回网页工具 `Internal Error`，因此该 URL 的当前有效性/正文记 `NOT_VERIFIED`，不能仅从工具错误断定 404 或文件不存在。随后限 Microsoft Learn 搜索并读取同站 [FLT_PARAMETERS for IRP_MJ_SET_SECURITY](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/flt-parameters-for-irp-mj-set-security) 的返回正文，确认 DACL/owner/group/SACL 设置操作和所需访问权；技术主张有替代一手证据支持。这是来源访问限制，没有形成报告结论错误的 finding。

签名策略和 test-signing 文档说明启用 TESTSIGNING 需管理员、修改 boot configuration 且需重启；报告排除该路径与用户边界一致。[Microsoft TESTSIGNING option](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/the-testsigning-boot-configuration-option)

不推断的未知状态：本机 Windows 版本/Secure Boot/HVCI/driver inventory/filter list/volume 文件系统、实际管理员令牌、日志父目录 ACL、用户漫画库具体路径、任何已签名 package、可安装服务/registry 目标、pending I/O 排空与 cleanup 恢复事实。来源只能证明公开 API 文档的语义，不能证明本机实施结果。

报告 `:86–96` 与 Task `:610` 11 项 Gate 一致：Phase A=`BLOCKED / NOT_RUN`；private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。AC 未运行，不是失败。

Verification 结论：静态对象 pin 与引用核心主张得到核查，文档 Review 可以批准；所有系统/产品验证仍为 NOT_RUN，P02 不得据此完成或执行。

## 下一步建议

推荐 Agent=Codex Lead/Integrator，在 `G:/CODEX/New Manga` 的 `main@cddff58469b56e181019a8ddfeade80684bc7eb9` 上对本 Review 独立 adjudicate，记录该冻结 SHA 的静态报告批准与仍阻塞的 Gate。允许范围限 P02 Task 追加结果、规定治理状态及 adjudication 证据；禁止改固定报告/Review、代码/测试、系统权限或 Gate token。交付裁决记录及准确下一决定；验收为引用/hash/授权范围一致，不执行系统或产品验证。这是当前已授权的文档收口步骤，不释放 driver/ETW 实施 Task。

可转发指令：

> Codex Lead：请对本 Review 与冻结报告 `427219AC35CB6407D4CB5BD5D2FD6F247866D8FD2E34644459A2A808EFABBC18` 独立 adjudicate；工作目录为 `G:/CODEX/New Manga`，base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`。仅追加 P02 Task/规定治理记录与裁决证据，保留固定报告、所有他人未提交内容和原 Gate。记录静态 APPROVED、OS/产品 NOT_RUN，以及当前无可执行 READY 方案；之后提出有具体边界的下一项用户决定。不得安装/启动 observer、ETW、driver/service，或执行 OS probe、build、Cargo、AC1–AC7。

未检查：主机配置与实际安装/覆盖/卸载行为；未运行任何系统或产品验证。
剩余风险：静态批准不解决 private-registry absent、全树身份及完整写入闭包，Build Gate 继续阻塞。
