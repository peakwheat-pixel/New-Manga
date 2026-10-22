# P02 Phase A method blockers · memo r2

状态：BLOCKED / NOT_RUN。本文是设计就绪度记录，不是测试结果、OS measurement 或 Gate 决定。r1 为不可变 Review 输入；本版吸收其 finding 裁决，并单独提交非作者 Review。

## 基线、输入与本地校验

- 仓库：G:\CODEX\New Manga；main@cddff58469b56e181019a8ddfeade80684bc7eb9，tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b。
- 固定依据：P02 Task（派发快照 SHA-256=AB06351028B0E22ABC01E4D920946D10E17D45C2E1386D7A289CB4D77A43D160）；contract r7（7FBFFE6583511CBF5348539D1D8A2C4174000D93950FD54DBCDFBBC5B6C90ADF）；manifest r3（AC45329A58BFFA3AF6984E02207E1AF4AD54E46644DFEEC25B50869E26C4BC43）；r7 adjudication（6C585068E92A0A598065C9B2ABB1CA908BF567E113A696F7CF1E4B7EDEAA4E8B）；r1 memo（2E5128BF08232B3F4CE0E3FDE90A6585656124D341A0FB4A4226498E6935F57F）。逐项裁决见 codex-phase-a-method-blockers-review-r1-adjudication.md。
- 非作者内容 Review：DSH APPROVED_WITH_CONDITIONS，0/0/4/5；原对象绑定 NOT_VERIFIED。Codex 对派发快照独立复算上述 SHA 均匹配，不替代 DSH 对象绑定结论。
- Local validation：Get-FileHash 对本节所列输入复算一致；状态=已完成。本文尚未提交新的非作者 Review，object binding=待新 Review；不声称 Git commit 或 exact-head pin。

## 评估结论与精确阻塞

1. METHOD_BOOTSTRAP / EA-01：manifest r3 没有冻结实现语言/PowerShell 版本、启动顺序、CLR/native binding、结构布局、句柄 flags、逐调用 access masks、路径解析时序或错误映射。PowerShell/.NET 的概括不足以证明 bootstrap 未产生未枚举的文件访问、缓存写入或子进程。
2. PROGRAMDATA_EQUIVALENCE / EA-01：r3 固定 23 个环境变量，没有 ProgramData。采纳 r7 adjudication 已准许的保守 fallback：%ProgramData%\Microsoft\Windows\WER\ReportQueue 与 ReportArchive 两个目录标为 UNKNOWN / BLOCKED，不读取第 24 个变量、不猜映射、不调用未冻结的 special-folder resolver。其余 WER 对象中，%LOCALAPPDATA%\CrashDumps 路径可由 r3 的 23 项集合解析。
3. NO_CHILD_NO_WRITE_EVIDENCE / EA-01：r3 不检查子进程，也没有外部 OS 观察/强制方法覆盖短生命周期后代及全部写尝试。只读 API 的目标句柄不证明整个进程树没有写入。当前没有经 Review 验证的完整方法；保持 BLOCKED / NOT_VERIFIED，不以“未观察到”替代“OS 阻止”。
4. PRIVATE_REGISTRY_ABSENCE / r7 P1-01：仍为 UNPROVABLE / BLOCKED。不得猜测 registry key/view，不调用可能初始化存储的 API，不创建 profile。此项不是普通的 manifest 字段缺漏；只有新证据方法经独立 Review 与 Codex adjudication 后，才可重评。
5. 合同前置条件不一致 / RV-P2-02：contract r7 §8.1 列有三项执行前置条件，而 §8 第 3 条还要求 Phase A manifest “均无歧义”。DSH Review 与既有 EA-01 已说明 Review/adjudication/SHA pins 完成不等同方法无歧义。contract 需先统一唯一准入清单；此处记录冲突，不用 memo 覆盖 contract。
6. Phase B API defect / RV-P3-02：contract r7 §5 的 GetFileInformationByHandleEx(FileHardLinkInfo) 不在 Microsoft 列出的 FILE_INFO_BY_HANDLE_CLASS 中，构成 Phase B 精确文件/链接检查候选缺陷；Phase A r3 不打开文件，因此不把该缺陷作为新的 Phase A 操作或测试失败。后续 Phase B/Build Gate 前必须另行修正并 Review。Microsoft 来源：[有效信息类](https://learn.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-getfileinformationbyhandleex)、[FILE_STANDARD_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info)、[FILE_STREAM_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_stream_info)。

## OS 观察方案边界

现有候选材料不能作为完整进程树与写入边界证明。Microsoft 文档指出 Job Object completion-port 通知并非全部保证送达，NT Kernel Logger 已弃用且会话控制需管理员或 LocalSystem；ETW 也记录丢失事件/缓冲计数。因此这些机制单独或未经设计、验证的组合都不构成 Gate 证据：[Job Object completion port](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port)、[StartTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea)、[ETW loss counters](https://learn.microsoft.com/en-us/windows/desktop/ETW/event-trace-properties)。本 memo 不选择或调用任何 API/observer，不声称 Windows 一般不存在可行机制。

专家咨询意见未形成可归档、可复算的独立输入，不作为证据；此前提到的 NtOpenFile 等 API 建议从候选方案移除。NtOpenFile 属 ntdll，且 r3 仅允许 PowerShell/.NET API，当前不得采用；修改调用约束必须另立契约、Review 和授权。PowerShell 7 的 Add-Type 文档不证明 Windows PowerShell 5.1 的行为，版本与启动机制必须在任何未来候选中固定。

不扩展 T1 读取到额外 16 个根，不读取受保护文件内容或 hash，不扫描目录子项，不访问用户漫画库、数据库、Lock、current/pinned Revision、凭据或生产数据。不创建 profile，不修改 ACL、registry、label，不运行 probe、测试、Cargo、build，不访问 Windows Sandbox。

## 当前 Gate 状态（11 项）

1. Phase A=BLOCKED / NOT_RUN
2. private_registry_absence=UNPROVABLE / BLOCKED
3. profile=NOT_CREATED
4. ACL/registry=NOT_MODIFIED
5. scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED
6. OS isolation preflight=NOT_RUN
7. hook/cache/child-process closure=BLOCKED / NOT_VERIFIED
8. Build Gate=BLOCKED
9. build=NOT_AUTHORIZED / NOT_RUN
10. Hard Build Barrier=EFFECTIVE
11. AC1–AC7=BLOCKED / NOT_RUN

本轮没有执行 OS measurement、Windows API、ETW、process observer、profile/ACL/registry/label 操作、Sandbox、测试、Cargo 或 build。没有测试失败；Gate 仍阻塞。

## 下一准入与停止条件

本 memo 仅供新的非作者文本 Review；即使 Review 通过，也不授权 Phase A。下一候选必须先统一 contract r7 §8.1 与 §8 的准入条件，并证明同一精确、非提权范围内可验证主进程及全部后代身份、禁止保护路径写入、scratch 允许写入、TEMP/cache 重定向和运行前后受保护文件 hash 一致。每项都需固定工具/版本、API、路径、字段、mask、失败闭包和证据保存方式，再由非作者 Review 与 Codex adjudication 固定哈希。

目前没有被证实满足上述全部要求的方案。若需要管理员权限、驱动/内核过滤器、额外安装工具、扩大可写路径或修改 Gate 验收标准，超出当前授权边界；在用户决定前保持 BLOCKED。未经完整 OS 证据不得解除 Hard Build Barrier、构建或运行 AC1–AC7。
