# P02 Phase A method blockers · memo r6 candidate

**评估对象状态：**Phase A=`BLOCKED / NOT_RUN`。本文是静态设计就绪度记录，不是测试结果、OS measurement、实施许可或 Gate 决定；本候选尚待新的非作者 Review。

## 基线、Task 修订范围与证据

- 仓库：G:\CODEX\New Manga；main@cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b。
- 用户授权及环境裁决：Task 行号最初以 memo r3 attempt 2 Review 派发快照（108405 bytes / SHA-256=`7521168C1FB9FB4A1D0FE562C217BD43F884431BB3788FC0B2B6CB6C05F037C1`）为准；本轮在 attempt 3 Review pin（111260 bytes / SHA-256=`351EB291C5A5243BA49B7F16CB874890B5CA27EF2763D0A50962A1B52B691AD2`）下重新核对，`PROJECT_ORCHESTRATION_AUTHORIZATION` 段仍对应 :68–70，Task :58–62 与 :382–386 仍记录用户裁决本机 Windows 验证替代 Windows Sandbox。行号锚点仅在 attempt 3 pin（111260 bytes / SHA-256=`351EB291C5A5243BA49B7F16CB874890B5CA27EF2763D0A50962A1B52B691AD2`）上复核；这些历史行号不转用于其他 Task 快照。memo r5 attempt 1 Review 派发时的 Task pin 为 116853 bytes / SHA-256=`7CCFA05D4EF1766DCAD8B401A0279DC9AE692E6A9791BEE037138798FB608AC3`，是独立对象；Codex 在该派发快照内容仍为 live 时复核了 :58–70、:382–386 的语义锚点。其后 Task 只追加了该 Review 的 dispatch 元数据，当前 live Task pin 为 117485 bytes / SHA-256=`C11BAEE46B59EF244C086CCFC86A167826582B2E3840D058AC2919A5E340B8BD`；这些不同 pin 不互换。授权是范围许可，不是 OS 证据或 Gate PASS；不查询、安装、启用或启动 Windows Sandbox。（RV6-P3-02）（RV2-P3-02；RV-N-02；RV3-P3-05；RV4-P3-01）
- Task 修订快照：memo r1 首轮 DSH 派发时为 100139 bytes / SHA-256=AB06351028B0E22ABC01E4D920946D10E17D45C2E1386D7A289CB4D77A43D160；memo r2 复审派发时为 102674 bytes / SHA-256=A35CB3A7C3347F7E96FC478055CA519ECB39DAE4B03D25D3905B66EEC6FC951C；本 memo r3 候选创建时当前 Task 为 105252 bytes / SHA-256=44C1F4B2EE8A846B5AD529019518B8788CB151ED14A8E44CE74E64D9B82291F3。三个 Task snapshot 是不同历史修订；需以新 Review prompt 的 Task pin 为准，不能互换。（RV2-P3-02；RV-N-02；RV3-P3-02）
- 先前独立内容 Review：memo r1=`APPROVED_WITH_CONDITIONS`（0/0/4/5，object_binding=`NOT_VERIFIED`）；memo r2=`APPROVED_WITH_CONDITIONS`（0/0/2/4，object_binding=`NOT_VERIFIED`）。r2 的 Review 对象为 6961 bytes / SHA-256=140DA099ED8B3382FB09CB8D64B82F2B81B77DF62784D8755D8054B72DFCD847；r2 DSH report=`846E4ADAAEF37871696EE7949A104DF4A64065C57B25B11EEEB675E338FB4F1E`；Codex finding adjudication=`B49B855F976775704A7445DF0C7AC44FA9CB3BD490616AEA49B8BE8F9C7160ED`。两轮 DSH object_binding 均保持 NOT_VERIFIED；前述静态 Review 结论不被继承为本候选批准。
- 其他固定依据：contract r7 SHA-256=7FBFFE6583511CBF5348539D1D8A2C4174000D93950FD54DBCDFBBC5B6C90ADF；manifest r3 SHA-256=AC45329A58BFFA3AF6984E02207E1AF4AD54E46644DFEEC25B50869E26C4BC43；r7 Codex adjudication SHA-256=6C585068E92A0A598065C9B2ABB1CA908BF567E113A696F7CF1E4B7EDEAA4E8B。memo r4 以 attempt 3 固定 Review 对象 memo r3（SHA-256=`773476745C19A1996043819E514788290B17D4DC8BFD250449AD235E777BD701`）为修订基线；memo r5 只修正文档引用与契约载体说明。memo r3 与 r4 均保留原样。

## Phase A 当前设计阻塞

1. **EA-01 / METHOD_BOOTSTRAP。**这是 Codex execution-readiness finding，不是 DSH r7 finding，也不是测试失败。DSH r7 对 contract r7 与 manifest r3 的内容 Review=`APPROVED`（P0/P1/P2/P3=`0/0/0/5`；report SHA-256=`C1FADDC2D366286F14473DB68AE72D20FCF946E15DE50E4AFA3E2752998EF705`；formal `object_binding=NOT_VERIFIED`，仅为内容层结论、不是 exact-object 凭证），但其范围不涵盖 Codex 后续发现的执行就绪缺口，不能据此推出 r3 可执行。manifest r3 没有冻结具体实现绑定、PowerShell 版本、CLR/native 调用方式、结构布局、句柄 flags、逐调用 access masks、错误映射与 bootstrap/路径解析时序；r3 已规定的 T0/T1 读取次序不在缺口之列。逐次 API 名称不证明启动过程无额外文件访问、缓存写入或子进程。（RV2-P3-03；RV3-P3-03）
2. **PROGRAMDATA_EQUIVALENCE。**r3 的 23 项环境变量中没有 ProgramData。依赖 %ProgramData% 的两个 WER 目录——ReportQueue 与 ReportArchive——只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；该 fallback 不会改写 manifest r3。不得读取第 24 个变量、猜测映射或调用未冻结的 resolver。其余 WER 对象中，%LOCALAPPDATA%\CrashDumps 可由 r3 的 23 项集合解析。（RV2-P3-01）
3. **NO_CHILD_NO_WRITE_EVIDENCE。**r3 的 Phase A 是 controller-only 只读测量，不检查子进程、不写入、也不读取文件内容或 hash。它没有外部 OS 证据覆盖短生命周期后代及所有写入尝试；API 目标句柄只读不能证明完整进程树无写入。当前没有通过 Review 的完整执行方法，因此仍 `BLOCKED / NOT_VERIFIED`；不以“未观察到”替代“OS 阻止”。
4. **PRIVATE_REGISTRY_ABSENCE / r7 P1-01。**目标 private registry storage 在 profile 创建前的 absent-state 仍为 `UNPROVABLE / BLOCKED`。不得猜 registry key/view、调用可能初始化 storage 的 API 或创建 profile。只有另行冻结并审查的可信证据方法才能重评。
5. **Contract 前置条件分层与下一候选方法未统一（非字面矛盾）。**contract r7 §8.1 item 1（r7:156）规定开始测量前须完成三项：DSH r7 Review、Codex adjudication、逐文件 SHA-256/object pin 核对；同项另行禁止调用 profile/private-registry API、创建 profile/file/dir、改 ACL/label/registry 或运行写 probe。“精确下一步”第 3 条（r7:177）再要求 Review、adjudication、object binding 与 Phase A manifest 均无歧义；r7 adjudication（:52）已明确不得执行 manifest r3，必须先冻结新的 Phase A manifest 和最小测量方法并重新 Review/Codex 核验。memo 记录这组分层要求和新候选方法缺口，不宣称 contract r7 的两条准入互相矛盾，也不自行覆盖 r7；未来候选契约须通过新版本 contract r8 统一前置条件及范围限制，并为新 manifest 写明版本化载体、精确 API/路径解析顺序、句柄访问与错误映射；在 r8 固定、非作者 Review 与 Codex adjudication 前，不产生新可执行候选。（RV6-P3-03）（RV4-P3-02；RV5-P3-02）（RV2-P2-01；RV-P2-02）

Phase A 的下一候选仍只限经授权的 controller-only 只读对象与字段；其唯一释放载体为新版本 contract r8，必须先固定方法、顺序、错误和失败闭包，再经非作者 Review 与 Codex adjudication。Phase A 不纳入进程树检查、scratch 写入、cache 重定向回读或文件 hash。（RV2-P2-02；RV4-P3-02）

## Phase B / Build Gate 独立缺口

下列验证属于后续 Phase B / Build Gate，不能并入下一 Phase A manifest：完整主进程及所有后代的隔离身份、保护目录拒绝写入、scratch 正向写入权限、TEMP/cache 重定向、运行前后受保护文件 hash 一致及所需的进程/写入闭包。每项需独立冻结精确方法、路径、字段、失败判据和证据，然后经非作者 Review 与 Codex adjudication。当前无该证据，所以 Build Gate 仍关闭。（RV2-P2-02）

**FILE_INFO_CLASS_MISMATCH。**contract r7 §5（r7:115）的 `GetFileInformationByHandleEx(FileHardLinkInfo)` 不属于 Microsoft 列出的 `FILE_INFO_BY_HANDLE_CLASS`；枚举列表包含 `FileStandardInfo` 和 `FileStreamInfo`，不含 `FileHardLinkInfo`。这是 Phase B 的精确文件/链接检查候选缺陷；Phase A r3 不打开文件，故不新增 Phase A 调用。须先通过新版本 contract r8 修正并固定精确替代检查方法，随后重新 pin、非作者 Review 与 Codex adjudication；在此之前不进行依赖该检查的 Phase B measurement 或 Build Gate 决策。（RV4-P3-02）来源：[FILE_INFO_BY_HANDLE_CLASS enumeration](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class)、[GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex)。（RV2-P3-04；RV3-P3-01；RV3-P3-04）

现有 DEBUG_PROCESS、Job Object 与 ETW 等候选不能被当作完整后代与文件操作证明：Job completion-port 消息并不保证全部送达，NT Kernel Logger 已弃用且控制要求管理员或 LocalSystem，ETW 也记录丢失事件/缓冲计数。上述资料是设计限制，不是本机运行证据：[Job Object completion port](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port)、[StartTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea)、[ETW event trace properties](https://learn.microsoft.com/en-us/windows/desktop/ETW/event-trace-properties)。不据此断言 Windows 一般不存在其他可行机制。

此前 ExpertAdvisor 提到的 API 建议未形成可固定、可复算的独立输入，不作为证据或获准方案；例如 `NtOpenFile` 属 ntdll，超出 r3 明定的 PowerShell/.NET 调用约束，未经契约变更、Review 与授权不得采用。PowerShell 7 `Add-Type` 文档也不证明 Windows PowerShell 5.1 行为。

## Scope、状态与禁止操作

- 不扩大 T1 到额外 16 个根，不增加环境变量，不扫描目录子项，不读取受保护文件内容/hash，不访问漫画库、数据库、Lock、current/pinned Revision、凭据或生产数据。
- 不创建 profile；不改 ACL、registry 或 label；不写 probe；不提权、不安装工具、不扩大可写路径；不运行测试、Cargo、build 或 Sandbox。
- 下面 Gate token 与当前 P02 Task 一致；全部是状态记录，不是 Gate 通过证据。

## 当前 Gate 状态（11 项）

1. Phase A=`BLOCKED / NOT_RUN`
2. private_registry_absence=`UNPROVABLE / BLOCKED`
3. profile=`NOT_CREATED`
4. ACL/registry=`NOT_MODIFIED`
5. scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`
6. OS isolation preflight=`NOT_RUN`
7. hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`
8. Build Gate=`BLOCKED`
9. build=`NOT_AUTHORIZED / NOT_RUN`
10. Hard Build Barrier=`EFFECTIVE`
11. AC1–AC7=`BLOCKED / NOT_RUN`

本次 memo 编写未运行 Windows API、ETW、process observer、profile/ACL/registry/label 操作、OS measurement、测试、Cargo、build 或 Windows Sandbox。无测试失败记录。

## 下一步

本文仅为静态设计就绪度记录，供新的非作者文本 Review。Review 或 Codex adjudication 均不会自动放行 Phase A。若后续完整进程/写入闭包需要管理员权限、驱动/内核过滤器、安装工具、扩大路径或改变 Gate 验收标准，超出现有授权；停止并请用户裁决。没有新的独立 Review 与完整 OS 证据前，保持上述所有 BLOCKED / NOT_RUN 状态，不构建、不运行 AC1–AC7。
