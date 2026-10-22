# P02 Phase A method blocker memo r1 Review · Codex adjudication

日期：2026-10-10（Asia/Shanghai）
裁决者：Codex（Lead / Integrator）
性质：文本内容 Review 的 finding disposition；不是 OS measurement、测试结果或 Gate 放行。

## 固定对象与 Review 结果

| 对象 | 字节数 | SHA-256 |
|---|---:|---|
| P02 Task（DSH 派发时） | 100139 | AB06351028B0E22ABC01E4D920946D10E17D45C2E1386D7A289CB4D77A43D160 |
| 原始 memo | 5629 | 2E5128BF08232B3F4CE0E3FDE90A6585656124D341A0FB4A4226498E6935F57F |
| contract r7 | 32969 | 7FBFFE6583511CBF5348539D1D8A2C4174000D93950FD54DBCDFBBC5B6C90ADF |
| Phase A manifest r3 | 6339 | AC45329A58BFFA3AF6984E02207E1AF4AD54E46644DFEEC25B50869E26C4BC43 |
| r7 adjudication | 7016 | 6C585068E92A0A598065C9B2ABB1CA908BF567E113A696F7CF1E4B7EDEAA4E8B |
| DSH Review prompt | 3543 | 4F80472DEE5E8DFB27831F19E22F1D7344A5D00BBC086A763D8C487BD82A55CB |
| DSH Review report | 25062 | 67677D2ECDE1247BA54CCDBBE9486C28F705D122697E5EDAB192EFF7ABE396C7 |

DeepSeek Harness 内容决定为 APPROVED_WITH_CONDITIONS，P0/P1/P2/P3=0/0/4/5；DSH session=session-36f58e83-b125-4977-854b-f76b95fcdbfa，CLI exit=0，mount exit=0。DSH 的 object_binding=NOT_VERIFIED，因其 shell 初始化失败，无法复算 hash/Git。Codex 使用 Get-FileHash 对上表当前输入复算，结果均与派发值一致；这只记录 Codex 自己的字节核对，不升级 DSH 的 object_binding。

## Finding disposition

| Finding | 裁决 | 处置与边界 |
|---|---|---|
| RV-P2-01 | 接受 | 新 memo r2 将逐项列出 11 个 Gate token，包含 Phase A、private registry、profile、ACL/registry、scratch ACL/label、OS preflight、hook/cache/child closure、Build Gate、build、Hard Build Barrier、AC1–AC7。 |
| RV-P2-02 | 接受 | r7 §8.1 的三项条件与 §8 第 3 条额外要求“manifest 无歧义”存在不一致。新 memo 锚定两处原文及已记录的 EA-01；r3 仍不得执行。后续候选契约必须统一唯一前置条件，在新 Review 与 adjudication 前不测量。 |
| RV-P2-03 | 接受 | 采纳 r7 adjudication 已冻结的保守 fallback：两条依赖 %ProgramData% 的 WER 目录保持 UNKNOWN / BLOCKED，不读取第 24 个变量、不猜特殊文件夹映射。private_registry_absence 继续 UNPROVABLE / BLOCKED；两者不能混为同一类：前者可在新方法中明确为未知并继续阻断，后者在现行 contract 下没有获准且可证明的 absent-state 方法。 |
| RV-P2-04 | 接受 | ExpertAdvisor 咨询未形成可归档、可复算的独立输入，不作为证据。新 memo 只保留已有 Task/contract/manifest/DSH finding 与可直接引用的一手文档；不把 advisor 的 API 或强制方案建议当作已验证事实。 |
| RV-P3-01 | 接受 | 新 memo 将 METHOD_BOOTSTRAP、PROGRAMDATA_EQUIVALENCE、NO_CHILD_NO_WRITE_EVIDENCE 对应到 EA-01 的具体未闭合项，避免另造重复 finding 编号。 |
| RV-P3-02 | 接受 | FileHardLinkInfo mismatch 真实存在，但属于 contract r7 §5 的 Phase B/构建前路径检查，不是 Phase A manifest r3 的直接调用缺陷。它仍阻止 Phase B/Build Gate 候选，不能扩大为 Phase A 的新增操作。 |
| RV-P3-03 | 接受 | 新 memo 补充 Job completion-port 消息投递不保证、NT Kernel Logger 已弃用、5 个 WER 对象中只有 2 个路径依赖 %ProgramData%；%LOCALAPPDATA% 下 CrashDumps 路径可由 r3 的 23 项环境变量集合解析。上述资料只限于说明设计限制，不构成运行证据。 |
| RV-P3-04 | 接受 | NtOpenFile 属 ntdll，不在 manifest r3 明定的 PowerShell/.NET 调用约束内；不得把它当作已授权候选，除非未来契约明确修订并完成独立 Review。 |
| RV-P3-05 | 接受 | 新 memo 加入自身状态、输入 pins、local validation 状态、允许范围及 denylist，保留所有未运行状态。 |
| RV-N-01 | 接受 | PowerShell 版本未固定；PowerShell 7 Add-Type 文档不能证明 Windows PowerShell 5.1 行为。纳入 bootstrap 未冻结范围，不据此推断已发生写入。 |
| RV-N-02 | 接受 | DSH r7 adjudication 所引 Task SHA 与本次 memo Review 派发 SHA 不同，是不同修订快照；未来 Review 必须固定 Task 修订范围与 SHA。 |
| RV-N-03 | 接受 | r7 对 SECURITY_INFORMATION 的部分掩码已有文字；准确缺口是 r3 未绑定逐调用 masks，不表述为 r7 完全未提 masks。 |
| T1 reread 提议 | 不采纳 | 对 16 个根追加 T1 读取会增加操作，不属于 r3 当前冻结范围；本轮不授权，也不纳入新 memo 的执行步骤。 |

## 后续对象与当前 Gate

原 memo 保留为不可变的 Review 输入。Codex 已据此建立独立候选 memo r2；它必须再经非作者只读 Review，不能继承 r1 的条件批准。contract §8.1 与 §8 的前置条件不一致尚未在 contract 本身修订；应先以文档修订解决，不能用此 adjudication 覆盖合同原文。

当前方法仍未证明可在现有非提权、精确路径范围内覆盖完整子进程树、所有非 scratch 写入与临时/缓存重定向。该判断是证据不足，不是“Windows 不存在任何机制”的普遍结论。无可信方法之前，不能执行 Phase A、不能启动 Build Gate，也不能修改 profile、ACL、registry 或 label。若后续需要提权、驱动/内核过滤器、安装额外工具或扩大路径，均超出本轮授权，须停止并由用户决定。

当前 Gate 保持：Phase A=BLOCKED / NOT_RUN；private_registry_absence=UNPROVABLE / BLOCKED；profile=NOT_CREATED；ACL/registry=NOT_MODIFIED；scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED；OS isolation preflight=NOT_RUN；hook/cache/child-process closure=BLOCKED / NOT_VERIFIED；Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；Hard Build Barrier=EFFECTIVE；AC1–AC7=BLOCKED / NOT_RUN。

没有运行测试、Cargo、build、Windows API、ETW、process observer、profile/ACL/registry/label 操作或 Windows Sandbox。该审查与裁决不产生任何 Gate PASS。
