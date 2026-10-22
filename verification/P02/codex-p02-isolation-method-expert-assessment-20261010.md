# P02 本机隔离方法只读 ExpertAdvisor 评估

日期：2026-10-10。Reviewer=`/root/p02_isolation_advisor`，模型=`gpt-6.1-sol/high`；只读评估，没有修改文件或执行 OS、API、registry、ACL、profile、probe、测试、Cargo、build 或 Sandbox 操作。

## 范围与授权状态

- 评估基于 P02 Task 的用户授权记录（§ `PROJECT_ORCHESTRATION_AUTHORIZATION`，当时已记 attempt 2 dispatch，Task :445/:459 明示 Review 本身不授权 Phase A/Build Gate），以及 contract r7、manifest r3 和本机 Windows 方案约束。Agent 未记录 Task 的字节/hash pin，因此此评估不作 exact-object Review。
- 该授权已允许 Codex 选择并执行范围内的本机隔离方案；它不替代方法冻结、非作者 Review、Codex adjudication、操作系统证据或 Gate 决定。用户明确禁止使用 Windows Sandbox；本评估没有查询或调用它。
- 结论：当前没有安全 `READY` 的 Phase A 执行方法，也没有证据证明“低权限 Job Object + restricted token/AppContainer + Process Monitor”足以闭合所有子进程身份和写入路径。

## 分阶段结论

**Phase A 与后续 Build closure 必须分别判断。** Manifest r3 只测 controller 当前 token、固定根元数据、23 个环境变量与五个 WER 对象；它不测子进程、不写入、不读或 hash 文件内容。当前 Phase A 自身仍缺冻结的实现/runtime、native binding、access masks、错误映射、bootstrap 和路径解析时序，并且 `%ProgramData%` 不在 23 项清单中。故 Phase A 继续 `BLOCKED / NOT_RUN`。这不等于要求 Phase A 先满足全部 Build Gate 条件。

Build Gate 另外需要主进程和全部后代身份、受保护路径拒写、精确 scratch 可写、TEMP/cache 子进程回读、写入闭包与受保护文件前后 hash。现有 manifest r3 明确排除这些项目，需单独冻结与 Review；不能把“未观察到”当成“OS 已拒绝”。

## 候选机制限制

- **Job Object：**Microsoft 文档说明普通 `CreateProcess` 子进程通常继承 Job，但 `Win32_Process.Create` 创建的后代不自动加入；breakaway 设置及系统已有 job 也影响闭包。completion-port 通知（通知限额类之外）不保证送达。Job 不提供文件路径写白名单。
- **Process Monitor：**微软客户端故障排查文档要求 elevated / Run as administrator 捕获 trace，并说明它只捕获部分进程活动。它是诊断 observer，不是拒写 enforcement；管理员要求超出当前非提权边界，且不完整 trace 不能证明所有写入闭包。
- **Restricted token：**降低 token 权限仍需结合实际对象安全描述符与访问检查；它自身不是文件系统命名空间隔离或全路径写入白名单。
- **AppContainer：**能提供有 OS 支持的边界，但需要验证实际 token、capabilities、对象 ACL/MIC 和子进程 token。`CreateAppContainerProfile` 会为当前用户创建 profile，并包含 folders 与 registry storage；这些持久化对象必须纳入现有 profile/registry/cleanup 规则。Task 尚未允许绕过 contract/manifest 的 profile 前置条件。
- 因而，不能将上述监视器拼接成当前 Build Gate 所需的强制拒写与完整子进程证据，也不能以创建 profile 代替“无副作用地证明 profile/private registry 初始不存在”。

## 一手来源

- [Microsoft Process Monitor 故障排查说明](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/troubleshoot-apps-start-failure-use-process-monitor)：捕获 trace 需管理员权限；只捕获部分进程活动。
- [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)：child-process inheritance、`Win32_Process.Create` 例外、breakaway 及 completion-port delivery 限制。
- [Microsoft CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)：为当前用户创建 profile；返回状态区分 data store 创建和权限不足；profile 包含 per-user/per-app folders、registry storage 与 ACL。
- [Microsoft CreateRestrictedToken](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-createrestrictedtoken)、[Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)：token restricted SIDs、AppContainer SID/capability/ACL 的官方 API 背景；不能替代对本机进程和对象的实测。

## 建议与 Gate

Codex 可继续冻结一个仅限 controller 的 Phase A 方法候选，先补全实现绑定、受限调用、T0/T1 顺序、路径解析与 ProgramData 未知项，再派 DeepSeek Harness 非作者 Review。不得把 Process Monitor、profile 创建、canary 写入、受保护文件 hash 或子进程观测加入 Phase A manifest r3。完整 Build closure 若必须增加提权 observer、驱动/内核 enforcement、额外写权限或更改 Gate 标准，应带着精确能力、路径、持久化影响和清理方案交由用户裁决。

Gate 状态不变：Phase A=`BLOCKED / NOT_RUN`；`private_registry_absence=UNPROVABLE / BLOCKED`；`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；OS isolation preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。本评估不是 Review PASS、测试结果、用户许可或 Gate 通过证据。
