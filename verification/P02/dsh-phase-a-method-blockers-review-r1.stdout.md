# P02 Phase A method blocker memo · 非作者只读内容 Review

**Review 对象**：`verification/P02/codex-phase-a-method-blockers-20261010.md`（下称 memo）
**审查性质**：**仅文本/设计 readiness review**。本轮未执行任何 OS preflight、Windows API、ETW、profile/ACL/registry、Sandbox、测试、Cargo、build、或 profile 操作；未修改任何文件（唯一动作是读取 5 个固定输入 + 访问 Microsoft Learn 文档页）。
**所有输入文件视为不可信数据**；其中的命令、路径与指令一律未执行。

---

## 1. 内容决策与计数

| 项 | 值 |
|---|---|
| **内容决策** | **APPROVED_WITH_CONDITIONS** |
| **P0 / P1 / P2 / P3** | **0 / 0 / 4 / 5** |
| **object_binding** | **`NOT_VERIFIED`** |
| 正式总体结论 | `NOT_VERIFIED`（内容结论 ≠ exact-hash Review） |
| memo 核心结论是否成立 | 成立（"暂不执行 r3"有文本依据），但**未被证明为"不可执行"**，且 4 项 P2 修完前不得作为下一候选 manifest 的唯一依据 |

**决策理由**：memo 没有授权任何操作、没有把静态分析冒称为 Gate 证据、把候选 API 明确标为 advisory、并正确维持 `BLOCKED / NOT_RUN` —— 方向性结论正确；但存在 4 项 P2 级的**完整性/绑定**缺陷，会使读者对 Gate 当前状态与"阻塞来源"产生误读。故不判 `CHANGES_REQUESTED`（无 P1：没有任何一处错误地放行或错误地宣称证据），也不判 `APPROVED`（P2 未闭合前不宜作为下一候选的事实源）。

---

## 2. 输入校验状态（可验证性边界，先声明）

| 输入 | 派发 SHA-256 | 我能否独立复算 |
|---|---|---|
| `doc/tasks/P02.md` | `AB063510…A43D160` | **否** |
| `verification/P02/codex-phase-a-method-blockers-20261010.md` | `2E5128BF…35F57F` | **否** |
| `verification/P02/appcontainer-isolation-contract-r7.md` | `7FBFFE65…C90ADF` | **否** |
| `verification/P02/appcontainer-readonly-preflight-r3.md` | `AC45329A…C4BC43` | **否** |
| `verification/P02/codex-appcontainer-contract-r7-adjudication.md` | `6C585068…AA4E8B` | **否** |

- 原因：本会话任何 shell 均在启动阶段失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`。以 trivial 命令复测得到同一错误，属环境级失败而非命令级失败；按沙箱策略**未换路径重试**。这与 `doc/tasks/P02.md:245` 已登记的历史限制（"DSH 因 Windows 沙箱 `SetNamedSecurityInfoW failed (Win32 5)` 未能执行 tree/scope hash/Git diff/runner"）一致。
- 因此**本次仅完成内容级 Review**，不得声称 exact-hash / object-bound Review。按 r7 §1.1.10（`appcontainer-isolation-contract-r7.md:37`）的约定，`object_binding=NOT_VERIFIED` 是正确记录。
- **可独立复核的部分**：5 个输入文件的正文与行号（只读读取）；Microsoft 一手文档语义（`web_fetch`，见 §4）。
- **不可复核的部分**：所有字节数/SHA-256、Git/工作区状态、本机 OS/registry/ACL/profile 状态、ExpertAdvisor（memo:10）是否存在与会话记录、以及 NT 层是否存在同名 `FILE_INFORMATION_CLASS`（本会话 `web_search` 返回 HTTP 401，不可用，故不作断言）。

---

## 3. 逐项 blocker / mismatch disposition

引用格式：`路径:行号`。

### 3.1 memo 四项 findings

| ID | memo 位置 | 判定 | 依据 |
|---|---|---|---|
| `METHOD_BOOTSTRAP` | memo:14 | **CONFIRMED**（文本证据充分） | r3:10 只列 token 字段、r3:12 只列根元数据字段、r3:38 仅说"PowerShell/.NET API"，三处均未固定 API、handle flags、access masks、路径解析顺序或错误映射；与 adjudication:44 的 EA-01 一致 |
| `PROGRAMDATA_EQUIVALENCE` | memo:15 | **CONFIRMED**（事实精确） | r3:20 的 23 项清单逐项核对，确无 `ProgramData`/`ALLUSERSPROFILE`；r3:27-28 的两个 `%ProgramData%` WER 目录不可解析。**但处置不完整** → RV-P2-03 |
| `NO_CHILD_NO_WRITE_EVIDENCE` | memo:16 | **CONFIRMED**（证据/可审计性缺口，非已发生的写入） | r3:32"不启动或检查子进程"、r3:34"不得创建…文件"、r3:38 仅 stdout。这是**负向断言无验证手段**，memo 正确地未声称任何写入实际发生 |
| `PRIVATE_REGISTRY_ABSENCE` | memo:17 | **CONFIRMED，且是本 memo 最扎实的一项** | r7:28（P1-01）、r7:52、r3:32 三处一致；memo 未猜 key、未调用 API，符合 r7:28 的禁令 |

### 3.2 `FILE_INFO_CLASS_MISMATCH`（memo:30）

**判定：CONFIRMED —— memo 的说法正确，r7 该处确需修订。** 我独立访问了 Microsoft 一手页面：

- 枚举权威页 `FILE_INFO_BY_HANDLE_CLASS` 的完整成员列表为 `FileBasicInfo … FileIdExtdDirectoryRestartInfo, FileDispositionInfoEx, FileRenameInfoEx, FileCaseSensitiveInfo, FileNormalizedNameInfo, MaximumFileInfoByHandleClass`，**不含 `FileHardLinkInfo`**（[FILE_INFO_BY_HANDLE_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class)）。
- memo 实际引用的函数页 Remarks 有效类表同样**不含**该项，且确实含 `FileStandardInfo`(1) 与 `FileStreamInfo`(7)（[GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-getfileinformationbyhandleex)）。
- memo 的两条候选说明本身也被文档证实：`FILE_STANDARD_INFO.NumberOfLinks` = "the number of links to the file"（[FILE_STANDARD_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info)）；`FILE_STREAM_INFO` "is used to enumerate the streams for a file"，且通过 `NextEntryOffset` 分页（[FILE_STREAM_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_stream_info)）。
- 引用精度：memo 写"contract r7 §5, line 115"，与 `appcontainer-isolation-contract-r7.md:115` 实际文本逐字相符。
- **补充（我未独立验证，不作 finding）**：NT 层存在名称相近的 link-information 信息类，其是否名为 `FileHardLinkInfo`/`FILE_LINKS_INFORMATION` 我无法用本会话工具证实；无论如何，它不属于 Win32 `FILE_INFO_BY_HANDLE_CLASS`，不能通过 `GetFileInformationByHandleEx` 取得。建议 r7 的下一候选直接删去该名并改述为文档支持的结构，而不是猜测 NT 等价物。
- **适用范围修正** → RV-P3-02。

### 3.3 DEBUG_PROCESS / Job Object / WMI / NT Kernel Logger / ETW 四项断言（memo:31, Task:416）

**判定：全部 CONFIRMED，均未过度断言。** 逐条对一手文档核对：

| memo 断言 | 一手文档原文 | 结论 |
|---|---|---|
| 调试链在链内进程再次以 `DEBUG_PROCESS` 创建时结束 | "A process that uses **DEBUG_PROCESS** becomes the root of a debugging chain. This continues until another process in the chain is created with **DEBUG_PROCESS**."（[process-creation-flags](https://learn.microsoft.com/en-us/windows/desktop/ProcThread/process-creation-flags)） | ✅ 逐字成立 |
| Job 默认不覆盖 `Win32_Process.Create` 创建的子进程 | "（Child processes created using **Win32_Process.Create** are not associated with the job.）"（[job-objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)） | ✅ 逐字成立，**且就在 memo 所引页面上**（无引用错配） |
| NT Kernel Logger 控制需要管理员或 LocalSystem | "Only users with administrative privileges and services running as LocalSystem can control an NT Kernel Logger session."（[StartTraceA](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea)） | ✅ 逐字成立 |
| ETW 暴露事件/缓冲丢失计数 | `EVENT_TRACE_PROPERTIES.EventsLost` / `LogBuffersLost` / `RealTimeBuffersLost`；"the session discards incoming events until a buffer becomes available. Each session keeps a record of the number of events discarded (see the **EventsLost** member)."（[event-trace-properties](https://learn.microsoft.com/en-us/windows/desktop/ETW/event-trace-properties)） | ✅ 成立，且文档明确承认丢弃行为 |
| 结论"该候选无法认证全部瞬时后代与全部文件操作" | 上述四条 + job-objects 页面另有 "delivery of messages to the completion port is **not guaranteed**" | ✅ 作为设计结论可接受（非"文档化不可能"的强断言） |

memo:31 末句"Do not elevate, install a tool, or widen write paths to make it work"与 r7:18/r3:34 的最小权限约束一致。✅

### 3.4 状态一致性核对（用户数据边界 / 路径范围 / Sandbox / profile / ACL / 无 OS measurement）

| 断言 | 出现处 | 与固定输入比对 | 判定 |
|---|---|---|---|
| `profile=NOT_CREATED` | memo:27 | r7:8、adjudication:58、Task:410 一致 | ✅ |
| `ACL/registry=NOT_MODIFIED` | memo:27 | r7:8、r7:18、Task:410 一致 | ✅ |
| 无 OS measurement / 无 Sandbox 操作 | memo:27, memo:33 | r3:34（禁止 Sandbox）、r3:48、adjudication:56 一致；未复活任何 `wsb`/guest 指令，符合 Task:60-62 的用户裁决 | ✅ |
| 未触碰用户数据 / 未扩写入路径 | memo:21, memo:31（隐含） | r7:114-118、r3:34 | ✅ 方向一致，但 memo 未自述 deny-list → RV-P3-05 |
| Gate 状态块 | memo:27 | 仅 7/11 项 → **RV-P2-01** | ⚠️ 不完整 |
| 阻塞性质 = "design blockers, not test failures" | memo:3, memo:33 | Task:410、adjudication:40 一致 | ✅ |

---

## 4. 逐审查问题回答

**Q1. r7 §5 的 `GetFileInformationByHandleEx(FileHardLinkInfo)` 是否与 Microsoft 正式 `FILE_INFO_BY_HANDLE_CLASS` 列表不一致？**
**是，不一致，memo 的发现成立。** 我**独立访问了**枚举权威页与 memo 所引函数页（§3.2），两者均无 `FileHardLinkInfo`。此项不是"无法访问网页故未验证"的情形。

**Q2. memo 四项描述是否有输入文件证据？BLOCKED / NOT_RUN 是否与测试失败正确区分？**
前三项有直接文本证据（r3:10/12/20/27-28/32/34/38），第四项有 r7:28/52 与 r3:32 三重证据（§3.1）。区分是**正确**的：memo:3 明确"not a test result, OS measurement, or Gate decision"；memo:33 明确"These are newly discovered design blockers, not test failures"；memo:27/33 两处声明未运行任何测试/构建/OS 测量。与 Task:410"当前不是测试失败"一致。⚠️ 但 memo:27 的 Gate 状态块只列 7/11 项（RV-P2-01）。

**Q3. DEBUG_PROCESS / Job / WMI / NT Kernel Logger / ETW 说明是否准确且不过度断言？**
**准确、不过度**，四项断言逐字被一手文档支持（§3.3）；结论以"无法认证"表述而非"文档化不可能"，措辞克制。两项**可补强**（P3）：StartTrace 页把 NT Kernel Logger 会话标为 `(deprecated)`；job-objects 页明说完成端口消息投递"not guaranteed"。两者都**加强**而非削弱 memo 的结论。

**Q4. 这些分析是否足以证明 r3 不应执行 / Build Gate 与 Hard Build Barrier 不能放行？是否存在当前授权内的静态修订空间？**
- **"r3 不应执行"：在文本层面成立，但依据需要重新锚定。** r3 自身文本（r3:10/12/38 只有字段名与"PowerShell/.NET API"，无 API/handle/mask/顺序/错误映射）足以证明 r3 **不是**一份无歧义的可执行 manifest；r7 的"精确下一步"第 3 条要求"仅当 Review、adjudication、object binding 和 Phase A manifest **均无歧义**后，才可执行"（r7:177）。据此保留 `BLOCKED / NOT_RUN` 有合同文本依据。**但** r7 的执行条款 §8.1（r7:156）只列 3 个条件（Review + adjudication + 逐文件 SHA/object pin），而这 3 项按 adjudication:20 与 Task:400 **已完成** —— 若只读 §8.1，会得出"Phase A 已可执行"的相反结论。当前 memo 的阻塞依据实际来自 Codex 的 out-of-band `EA-01`（adjudication:40）+ 未 pin 的 ExpertAdvisor（memo:10），**没有**落在 §8.1 上。→ **RV-P2-02**：下一候选必须统一前置条件集合，或明确记载 §8.1 被 EA-01 取代。
- **"证明不可执行"：不成立。** memo 只证明"现有提议的方法不足"，属**可审计性**缺口，不是安全性证明，也未展示任何违规写入。（memo 本身也没声称不可能。）
- **Build Gate / Hard Build Barrier：结论正确，但属于"本轮无任何证据"而非"memo 证明了阻断"。** r7:161（§8.6）要求 Build Gate 逐项绑定 LPAC token+子进程身份、拒绝访问、正负 canary、MIC/DACL、TEMP/cache 回读、WER、完整写入闭包与保护文件前后 hash；本轮零 OS 测量（memo:27/33），因此**不可能**满足任何一项 → 不能放行。这与 adjudication:58 的 `Build Gate=BLOCKED` / `Hard Build Barrier=EFFECTIVE` 一致。Build Gate 的放行依据**不在**本 memo 的对象范围内，本 Review 也不据此提升或降低它。
- **当前授权内的静态修订建议：存在，见 §6（全部为文档/范围提议，须经 Codex adjudication 与非作者 Review，本 Review 不授权任何执行）。**

**Q5. 用户数据边界、路径范围、Sandbox 禁止、`profile=NOT_CREATED`、ACL/registry 未修改、无 OS measurement 是否一致？**
除 RV-P2-01 的 Gate 状态块不完整外，**一致**（§3.4）。memo 未复活任何 Sandbox 指令，符合 Task:60-62 的用户裁决；未打开/哈希用户数据、未改 ACL/label/registry、未创建 profile，与 r3:34、r7:18、r7:114-118 相符。⚠️ memo 未自述受保护路径 deny-list 与本地验证裁决 → RV-P3-05。

---

## 5. Findings 明细（P0/P1/P2/P3）

### P2（4 项）

| ID | 位置 | 缺陷 | 影响 |
|---|---|---|---|
| **RV-P2-01** | memo:27 | Gate 状态块仅列 **7/11** 项：缺 `Phase A=BLOCKED / NOT_RUN`（仅由 memo:3 的 Status 行部分覆盖，且该行语义是 memo 自身状态）、`private_registry_absence=UNPROVABLE / BLOCKED`（只在 findings 出现，未进状态块）、`scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`（**全文未出现**）、`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`（**全文未出现**） | 读者可能把 memo 的状态块当作完整当前状态引用，误判这两项已被处置 |
| **RV-P2-02** | memo:14-16 vs r7:156 / r7:177 | memo 的阻塞依据未锚定到 r7 的执行条款：§8.1（r7:156）只列 3 个条件且**已完成**，而"无歧义"这一条件只出现在"精确下一步"第 3 条（r7:177）。memo 未指出该内部不一致，也未声明 §8.1 被 EA-01（adjudication:40）取代 | 下一候选若只按 §8.1 起草，会与 memo 结论冲突；阻塞依据目前依赖 Codex 单方 finding + 未 pin 的顾问意见 |
| **RV-P2-03** | memo:23 | 把"可观察/强制每一个后代与写入边界的、另行 Review 的 OS 机制"设为前置条件，但未记载**已冻结的替代路径**——adjudication:52 明确允许"either resolve the WER path using an explicitly permitted system-folder API inside the T0 bootstrap **or mark it `UNKNOWN / BLOCKED`**"；也未区分**可经 manifest 修订解除**与**在当前授权下永久 BLOCKED** 两类阻塞（`PRIVATE_REGISTRY_ABSENCE` 属后者） | 会让可解除项（`PROGRAMDATA_EQUIVALENCE`）显得同样不可解，也可能被读成"必须引入观测/强制机制"，与本 memo 自己的"不得提权/安装工具/放宽写入路径"（memo:31）产生张力 |
| **RV-P2-04** | memo:10（并涉及 memo:7 无输入 pin） | ExpertAdvisor 是**不可 pin 的输入**：无会话 ID、无 transcript、无 SHA、无字节数，且 memo:10 断言"It made no file changes and ran no APIs or measurements"——这是对第三方工具行为的**不可验证断言**；而 memo 后半部分（候选 API、DEBUG_PROCESS/ETW 评估）相当程度上源自其意见。同时 memo 只 pin 了 repo HEAD/tree（memo:7），未列出它实际读取的对象 pin | 与项目"Review prompt 固定各对象 SHA-256"的约定（r7:176）不一致；object_binding 无法闭合 |

### P3（5 项）

| ID | 位置 | 缺陷 |
|---|---|---|
| **RV-P3-01** | memo:14-16 | finding ID 卫生：三项与 adjudication:44-48 的 EA-01 子项实质重叠但未建立映射，形成同一缺口的并行 ID 与重复计数 |
| **RV-P3-02** | memo:30、Task:415 | 阶段归属未写明：r7:115 的路径规范化/别名枚举规则服务于**实际被访问文件**（对应 r7:158 §8.3），属 LPAC 运行/Phase B/Build Gate 面；它不应被读成 Phase A 的执行前置（Phase A 不开文件、不枚举内容，r3:32）。Task:415 的"新增阻塞 `FILE_INFO_CLASS_MISMATCH`"缺少该限定 |
| **RV-P3-03** | memo:31、memo:15 | 引用完整性：StartTrace 页把 NT Kernel Logger 会话标为 `(deprecated)`（应补，结果为**加强**该候选的否决理由）；memo:15 宜写明 5 个 WER 对象中**仅 2 个** `%ProgramData%` 目录不可解析，而 `%LOCALAPPDATA%\CrashDumps`（r3:26）所依赖的 `LOCALAPPDATA` **在** 23 项集合内（r3:20） |
| **RV-P3-04** | memo:21 | 候选 API 的可采性表述不足：`NtOpenFile` + `OBJ_DONT_REPARSE` 属 ntdll 层，而 r3:38 把机制限为"当前 controller 进程中的 **PowerShell/.NET API**"；因此它不只是"unapproved"，而是**在现行 r3 文本下不可采**，除非先改契约。memo 目前只说"unapproved candidates only" |
| **RV-P3-05** | memo 全文 | 文档自洽性：memo 无自身的文档状态行（对比 r3:4 的 `CANDIDATE / NOT_RUN / NOT_AUTHORIZED_FOR_EXECUTION`）；未复述受保护路径/用户数据 deny-list（r7:114、r3:34）与 2026-10-10 本机验证裁决（Task:60-62）。以引用方式成立，但并非自足 |

### 追加观察（非 finding，供 Codex 处置）

- **RV-N-01（added to `METHOD_BOOTSTRAP` 处置说明）**：r3 未固定测量所用 PowerShell 版本/edition；adjudication:50 引用的"Add-Type 默认生成内存程序集"是 **PowerShell 7** 文档的属性，该页面并不覆盖 Windows PowerShell 5.1 行为。因此不能据该文档推断 5.1 下同性质成立——这本身就是"bootstrap 未固定"的一个可复核子项。
- **RV-N-02（对象绑定观察）**：adjudication:11 记录 r7 派发时 P02 Task 为 `AC200DA1D9565BD612420C0518752D4CCCDFB32FA62C85CDD01449BDCE81FF72`（94063 bytes），本轮派发值为 `AB063510…A43D160`。两者不同是**预期**的（Task:398-417 的 r7/Phase A 续记在 r7 审核之后写入）。但因此 memo:8 所依赖的 `PROJECT_ORCHESTRATION_AUTHORIZATION` 文本**不是** r7 Review 批准时的同一字节；下一候选应以"Task 修订范围 + SHA"的方式 pin 授权依据，而非泛指"P02 Task"。
- **RV-N-03（正向）**：r7:106 的访问掩码陈述（DACL/label 查询需 `READ_CONTROL`、设置需 `WRITE_DAC`/`WRITE_OWNER`；不查询完整审计 SACL）与 [SECURITY_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/secauthz/security-information) 一致。这意味着 memo:14 的"未固定 access masks"应精确表述为：**r3 层面**缺逐调用绑定，而 r7:106/r7:117 已提供部分掩码语义。

---

## 6. 当前记录授权下的静态修订建议（**提议，非执行方案**）

以下全部落在"Codex-only `verification/P02/**` + `doc/**`"证据/文档面，不触碰 ACL/registry/profile、不写入 scratch、不运行工具链。**须先经 Codex adjudication 与新一轮非作者 Review 才可采纳**；本 Review 不授权任何一条落地，也不选任何 API。

1. **统一前置条件**（对应 RV-P2-02）：在下一候选契约中把 r7:156 的 3 条与 r7:177 的 4 条合并为一份唯一清单，并显式记载 EA-01 是否取代 §8.1。
2. **补齐 Gate 状态块**（RV-P2-01）：memo 的 Gate 段落改为与 Task:410 / adjudication:58 **逐 token 同集合**的 11 项。
3. **采纳已冻结的 fallback**（RV-P2-03）：在下一 Phase A 候选中把 2 个 `%ProgramData%` WER 对象标为 `UNKNOWN / BLOCKED`，其余 3 个对象与可解析路径照常冻结；这样无需读取第 24 个变量、无需新 API，也无需特殊文件夹解析器。
4. **逐项标注终态**（RV-P2-03）：为每个阻塞 token 标 `FIXABLE_BY_MANIFEST_REVISION` 或 `PERMANENTLY_BLOCKED_ON_CURRENT_AUTHORIZATION`（`private_registry_absence` 属后者）。
5. **finding 映射**（RV-P3-01）：建立 `METHOD_BOOTSTRAP`/`PROGRAMDATA_EQUIVALENCE`/`NO_CHILD_NO_WRITE_EVIDENCE` → EA-01 子项的逐条映射。
6. **错误与字段映射表**（RV-P3-03 的可执行部分）：下一候选在文本层面补齐以下**已被引用一手文档证实**的条目——`FileStreamInfo` 成功但无 stream 时 `GetLastError()` 为 `ERROR_HANDLE_EOF`；stream 枚举经 `NextEntryOffset` 分页；`FileStandardInfo.NumberOfLinks` 的字段语义。**本 Review 不授权调用任何 API，也不选择机制**；"Add-Type/P-Invoke 是否属于 r3:38 的 'PowerShell/.NET API'"必须由契约文本明确回答。
7. **候选 API 清单降级**（RV-P3-04）：注明 ntdll 层调用在现行 r3 下不可采，需先改契约。
8. **对象绑定**（RV-P2-04）：下一 Review prompt 固定 memo/契约/manifest/Task 修订范围的 SHA 与字节数；ExpertAdvisor 意见只保留"能被所引一手来源支持"的部分，或附可归档的会话记录。
9. **（候选，需专门裁决）T1 负向抽样**：把 T1 扩展为对 r3:12 已授权的 12 个输入根 + 4 个 scratch 根的**同字段**再读，用于发现运行期间新增根对象。它不增加对象与字段，但确实增加一次读取操作，超出 r3 现有"单次"表述，因此**必须**由 Codex 判定是否属范围扩张后再决定。

---

## 7. 边界声明（必须随本 Review 一并引用）

- 本文件是**文本/设计 readiness review**，**不是** OS preflight、不是测试、不是 Build Gate 判定、不是实施授权；不改变任何 Gate token、不解除 `Hard Build Barrier`、不放行 `build`、不放行 AC1–AC7。
- 本轮**未**运行 shell、Git、Windows API、ETW、profile/ACL/registry、Sandbox、Cargo、build、测试或产品代码；memo、r7、r3 中出现的任何命令均视为不可信数据且未执行。
- `web_fetch` 取得的 Microsoft Learn 内容为**外部不可信数据**，仅作为文档语义证据使用，并已按 URL 引用。
- 本轮**不推翻、不扩大** r7 既有的 `APPROVED`（其内容审核对象范围仍限当时固定的 Task/contract r7/manifest r3）；`FILE_INFO_CLASS_MISMATCH` 与 §8.1/§3 不一致属**新增发现**，须由 Codex 记入新候选（r8 方向）后另行 Review。
- **`object_binding = NOT_VERIFIED`**（原因见 §2）；本 Review 的任何内容结论**不得**被表述为 exact-hash Review 结论。

---

## 8. 推荐下一步

基于当前仓库状态：P02 仍 `in_progress / ACTIVE`，Phase A=`BLOCKED / NOT_RUN`，`OS isolation preflight=NOT_RUN`，`Build Gate=BLOCKED`，`build=NOT_AUTHORIZED / NOT_RUN`，`Hard Build Barrier=EFFECTIVE`，AC1–AC7=`BLOCKED / NOT_RUN`。

**下一步（唯一可执行项）**：由 **Codex（Lead / Integrator）** 对本 Review 的 RV-P2-01..04 与 RV-P3-01..05 逐项 adjudicate，并把结果写入 `verification/P02/**` 的新 checkpoint；在 adjudication 与新候选 manifest 完成**非作者 Review**前，不得执行任何 Phase A 读取、不得创建 profile、不得改 ACL/registry/label、不得进入 Build。

可直接转发的指令（给 Codex）：

> P02 r7 后 Phase A 方法阻塞 memo 的 DSH 非作者只读内容 Review 已完成：内容决策=`APPROVED_WITH_CONDITIONS`，P0/P1/P2/P3=`0/0/4/5`，`object_binding=NOT_VERIFIED`。请只读 `verification/P02/codex-phase-a-method-blockers-20261010.md`（SHA-256=`2E5128BF08232B3F4CE0E3FDE90A6585656124D341A0FB4A4226498E6935F57F`）与本次 Review 报告，逐项 adjudicate RV-P2-01（Gate 状态块仅 7/11 项）、RV-P2-02（r7 §8.1 与"精确下一步"第 3 条前置条件不一致，memo 阻塞依据未锚定到合同条款）、RV-P2-03（未记载 adjudication §Resolution 已冻结的 `%ProgramData%` → `UNKNOWN / BLOCKED` 替代路径，未区分可解除/永久阻塞）、RV-P2-04（ExpertAdvisor 输入不可 pin、memo 未列输入对象 pin），以及 RV-P3-01..05。同步独立复核 Task（派发 SHA-256=`AB06351028B0E22ABC01E4D920946D10E17D45C2E1386D7A289CB4D77A43D160`）、contract r7（`7FBFFE65…C90ADF`）、manifest r3（`AC45329A…C4BC43`）、adjudication（`6C585068…AA4E8B`）与 memo（`2E5128BF…35F57F`）的字节 hash（DSH 本轮因 `SetNamedSecurityInfoW failed (Win32 5)` 无法复算，`object_binding` 保持 `NOT_VERIFIED`）。adjudication 完成前不得执行 Phase A；不得调用 profile/private-registry API、不改 ACL/registry/label、不写入、不 probe、不运行工具链、不访问 Windows Sandbox；`private_registry_absence` 保持 `UNPROVABLE / BLOCKED`，`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN` 不变。
