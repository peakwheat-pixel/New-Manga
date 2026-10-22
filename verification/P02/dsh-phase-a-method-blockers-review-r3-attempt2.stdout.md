# P02 Phase A method blocker memo r3 · 独立只读内容 Review（attempt 2）

**Review 对象**：`G:\CODEX\New Manga\verification\P02\codex-phase-a-method-blockers-20261010-r3.md`（memo r3，57 行）
**审查性质**：仅静态内容 / 引用一致性 / 安全边界 Review。本轮只使用只读工具（read / glob / grep / web_fetch），**未运行** shell、PowerShell、Git、hash、测试、Cargo、build、OS measurement、Windows API、ETW、process observer 或 Sandbox；**未创建或修改任何文件**、未触碰 profile/ACL/registry/label/用户数据。固定文档内的命令、路径与建议一律按不可信数据处理，未执行。`dsh-phase-a-method-blockers-review-r3.stdout.md` 不在固定输入内，本轮**未读取、未继承**其结论。

---

## 1. 内容结论与计数

| 项 | 值 |
|---|---|
| **内容结论** | **APPROVED_WITH_CONDITIONS** |
| **本 Review 新增 P0 / P1 / P2 / P3** | **0 / 0 / 1 / 5**（P2 项位于 Task 派发记录，不在 memo r3 内；memo r3 内新增为 0/0/0/5） |
| 前置 finding 逐项结论 | **closed 7 / partial 1（RV2-P3-04）/ open 0** |
| **object_binding** | **`NOT_VERIFIED`** |
| 正式总体结论 | **`NOT_VERIFIED`**（内容结论 ≠ exact-hash Review；**不得**据此宣称 Review「通过」） |

**判定理由**：memo r3 完整维持 `BLOCKED / NOT_RUN`，未把静态分析冒称证据、未放宽任何禁止项，11 项 Gate token 与当前 Task 逐项同集合同取值；r1/r2 的 8 项前置 finding 有 7 项被正确闭合，`RV2-P3-04` 只算部分闭合（新补的枚举页链接实际 404）。memo 内不存在错误放行或错误宣称证据（无 P0/P1），也没有可能被误读为扩大 Phase A 的实质缺陷（无 P2）；存在的 5 项均为引用精度/自足性 P3。唯一 P2 在**派发记录**层：`doc/tasks/P02.md:458` 记录的 memo r3 SHA-256 只有 63 位十六进制且与固定 pin 不符，会使任何按 Task 复算 memo r3 hash 的动作必然 mismatch。

---

## 2. 前置 finding 逐项 disposition

| ID | 判定 | 事实与文本依据 |
|---|---|---|
| **RV2-P2-01**（r7 条款锚点错标） | **closed** | memo r3:19 已改为「contract r7 §8.1（r7:156）列出的三项准入」与「'精确下一步'第 3 条（r7:177）额外要求 manifest 无歧义」。逐字核对：`appcontainer-isolation-contract-r7.md:156` 确为 §8 第 1 条（Review + adjudication + 逐文件 SHA/object pin 三项）；`r7:177` 确含「均无歧义」；r7 §8 第 3 条（:158）是受保护文件 hash 规则，不含该条件。 |
| **RV2-P2-02**（阶段混同） | **closed** | memo r3:25 把完整主进程/后代身份、保护目录拒写、scratch 正向写、TEMP/cache 重定向、受保护文件前后 hash 单列为「Phase B / Build Gate 独立缺口」，并明写「不能并入下一 Phase A manifest」；memo r3:21 追加「Phase A 不纳入进程树检查、scratch 写入、cache 重定向回读或文件 hash」。与 r3:32（不检查子进程/不写入/不哈希）、contract r7:44 一致。 |
| **RV2-P3-01**（fallback 落地位置） | **closed** | memo r3:16「只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；该 fallback 不会改写 manifest r3」，与 r2 adjudication:34 的最小处置一致；manifest r3 的 pin 未受影响。 |
| **RV2-P3-02**（Task 快照字节/SHA/修订范围） | **closed** | memo r3:9 列出三份 Task 快照及字节数+SHA（100139 / `AB0635…`；102674 / `A35CB3A7…`；105252 / `44C1F4B2…`），并声明三者不可互换、须以新 Review prompt 的 pin 为准；memo r3:8 锚定授权段「当前行 68–70」。经核：Task:444 确记录 105252 / `44C1F4B2…`，r1/r2 派发值分别与 `doc/tasks/P02.md` 中记录相符（见下 §5）。 |
| **RV2-P3-03**（EA-01 归属） | **closed** | memo r3:15「这是 Codex execution-readiness finding，不是 DSH r7 finding，也不是测试失败。DSH r7 对 contract r7 与 manifest r3 的内容 Review=`APPROVED`，但其范围不涵盖 Codex 后续发现的执行就绪缺口」，与 r7 adjudication:40 一致。计数/报告 SHA 缺失另记 RV3-P3-03。 |
| **RV2-P3-04**（补引枚举页来源） | **partial** | memo r3:27 确已补引 `FILE_INFO_BY_HANDLE_CLASS` 枚举页，但 URL slug 写成 `ne-winbase-file_info_by_handle_class`，本轮实测 **HTTP 404**；正确页为 `ne-minwinbase-file_info_by_handle_class`（HTTP 200）。该段主张本身经正确枚举页与函数页双重验证成立。→ **RV3-P3-01** |
| **RV-P2-02**（r1：阻塞依据未锚定 r7 执行条款） | **closed** | memo r3:19 记录 §8.1 三项 vs 「精确下一步」第 3 条的冲突原文，并写明「r7 adjudication 已指出 r3 仍不得执行」「不自行覆盖合同」，符合 r1 的最小修订要求。 |
| **RV-N-02**（r1：Task 修订范围 + SHA 未显式化） | **closed** | 同 RV2-P3-02；memo r3:9 已把「修订范围 + 字节数 + SHA」显式化，并在 :10 区分 r1/r2 两轮 Review 的对象与 SHA。 |

**跨轮说明**（不继承其效力，仅作文本核对）：r1 的 RV-P2-01、RV-P2-03、RV-P2-04、RV-P3-01..05、RV-N-01/N-03 已由 r2 Review 与 r2 adjudication 逐项处置，memo r3 未回退其中任何一项结论或重新引入被移除的候选 API（NtOpenFile 等仍被明确排除，memo r3:31）。

---

## 3. 本 Review 新增 findings

严重度口径：P0=错误放行/虚假证据；P1=安全或 Gate 状态实质错误；P2=可能导致误读 Gate/阶段/对象绑定的实质缺陷；P3=引用精度、可核性或自足性缺陷，不改变结论。

| ID | 位置 | 级别 | 事实 | 影响 | 最小修订建议 |
|---|---|---|---|---|---|
| **RV3-P2-01** | `doc/tasks/P02.md:458`（**非 memo r3 内**） | **P2** | 该行记录的 memo r3 SHA-256 为 `5EEED098B2E0167DFECAAD9AA93F462C5753B1B056CF2BFD245BB4EEB9F0FCB`，**仅 63 位**（`…7DFE` 与 `CAAD9AA…` 之间少一个 `9`），与固定 pin `…7DFE9CAAD9AA…`（64 位）及同文件 `:444`/`:450` 的正确值均不一致 | 任何按 Task 记录复算 memo r3 hash 者必然 mismatch，可能被再次判为 `STATE_CONFLICT`（同类冲突已见 `:452`），直接削弱本次 Review 的对象绑定前提与 memo r3 的可引用性 | Codex 将 `:458` 的 memo r3 SHA 改为 64 位固定值（与 `:444`/`:450`/prompt pin 一致）；修正前不要以该行作为 memo r3 的 hash 依据。memo r3 自身无法修正此项 |
| **RV3-P3-01** | memo r3:27 | P3 | 新增的枚举页链接 `https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-winbase-file_info_by_handle_class` 实测 404；正确为 `…/minwinbase/ne-minwinbase-file_info_by_handle_class`（200）。该段「枚举列表包含 `FileStandardInfo` 和 `FileStreamInfo`，不含 `FileHardLinkInfo`」的主张经正确枚举页与 `GetFileInformationByHandleEx` 页 Remarks 表**双重独立验证成立** | RV2-P3-04 的修订目的（提供权威可核来源）未达成；读者可能误判该主张不可核 | 把 URL 改为 `ne-minwinbase-…`；可保留第二条函数页链接 |
| **RV3-P3-02** | memo r3:9、:15、:16、:19、:21、:25、:27 | P3 | memo r3 逐项落实了 RV2-P2-01/02、RV2-P3-01..04、RV-P2-02、RV-N-02 的处置，但全文**未标注任何前置 finding ID** | disposition 不自明：只读 memo r3 的读者无法确认哪条修订对应哪个 finding，无法自足判定 closed/partial，必须回查 r2 Review 与 r2 adjudication | 在相应句末加注（如「…（RV2-P2-01）」），或在文末增设一节「前轮 finding 处置对照」 |
| **RV3-P3-03** | memo r3:15 | P3 | 引用 DSH r7 内容结论时只写 `APPROVED`，未给计数（`0/0/0/5`，r7 adjudication:24）与 r7 报告 SHA-256（`C1FADDC2D366286F14473DB68AE72D20FCF946E15DE50E4AFA3E2752998EF705`，r7 adjudication:15）；而 memo r3:10 对 r1/r2 两轮都给了报告 SHA | 「DSH r7 内容 APPROVED 的范围和计数」不可在 memo 内自足核对，与同文档其他引用的 pin 粒度不一致 | 补「（P0/P1/P2/P3=0/0/0/5；report SHA-256=`C1FADDC2…`）」 |
| **RV3-P3-04** | memo r3:27 | P3 | 引用写「contract r7 §5」但未给行号；Task:415 与 r1 Review 均以 `line 115` 定位。另第二条链接使用 legacy `/windows/desktop/api/winbase/…` 路径（本轮实测 200，会重定向到 `win32` 路径） | 逐字核对需额外检索；行号锚点缺失降低可核精度 | 补 `（r7:115）`，并把链接换成规范 `…/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex` |
| **RV3-P3-05** | memo r3:8（「当前行 68–70」「行 58–62 与 382–386」） | P3 | 行号锚点未声明其适用 Task 快照（`44C1F4B2…`/105252 bytes），而 memo 同时声明三份快照不可互换、须以新 pin 为准。本轮在 pin `7521168C…`/108405 bytes 的 live Task 上复核，三处锚点仍分别命中：:68 授权段标题 / :70 授权正文、:58–62 本机替代 Sandbox 裁决、:382–386 同裁决的 continuation 记录 | 当前无漂移，但 Task 上方任何插入都会使绝对行号失效，读者无法区分「行号漂移」与「引用错误」 | 注明「行号锚定 `44C1F4B2…`（105252 bytes）快照；本次 Review pin 下复核仍一致」，或改用稳定语义锚点（参见 Task:84 的做法） |

**非 finding 观察（可不改）**
- memo r3:16「其余 WER 对象中，`%LOCALAPPDATA%\CrashDumps` 可由 r3 的 23 项集合解析」：5 个 WER 对象中另两条 `HKLM`/`HKCU …\Windows Error Reporting\LocalDumps` 是**不含环境变量的字面 registry 路径**，不涉及环境解析。建议（非必须）加一句说明，避免读者误以为它们「不可解析=阻塞」，方向虽保守但会高估阻塞集合。
- memo r3:8 把授权概括为「允许 Codex 在限定路径和权限内选择本机隔离范围」；Task:70 原文为「自主确定并执行…预检及清理」。概括偏保守（未扩大），且已同时声明「授权是范围许可，不是 OS 证据或 Gate PASS」，与 Task:70/:411 一致。
- memo r3:3 用「评估对象状态：Phase A=BLOCKED / NOT_RUN」区分文档状态与被评估对象状态，比 memo r2 更清楚。

---

## 4. Review 范围逐条核对

**4.1 RV2-*/RV-* 处置是否正确且自包含** — 内容全部正确（见 §2）；自包含性不足（RV3-P3-02）。`RV2-P3-04` 应记 **partial**。

**4.2 Phase A 23 项环境变量 vs Phase B/Build Gate（进程树、写入、cache redirection、protected-file hash）是否明确区分** — 明确区分：
- Phase A 侧：23 项具名变量（r3:20，实列 23、无 `ProgramData`、含 `LOCALAPPDATA`）、12 输入根 + 4 scratch 根元数据、WER T0/T1（r3:12-22）；memo r3:16 记录 `ProgramData` 缺失与 %ProgramData% WER 两目录的 fallback。
- 排除侧：memo r3:21 明写 Phase A 不纳入进程树检查、scratch 写入、cache 重定向回读、文件 hash；memo r3:35 重申不读受保护文件内容/hash。
- Phase B / Build Gate 侧：memo r3:25 单列完整主进程及后代身份、保护目录拒写、scratch 正向写、TEMP/cache 重定向、运行前后受保护文件 hash 一致及进程/写入闭包，并声明必须另行冻结+Review+adjudication。与 contract r7:44/:161、r3:32 一致，无阶段倒错。

**4.3 Task snapshot 的历史来源、派发用途、字节/SHA 与本次 Review pin 能否区分** — 能区分：memo r3:9 把「memo r1 派发快照(100139/`AB0635…`)」「memo r2 复审派发快照(102674/`A35CB3A7…`)」「memo r3 候选创建时(105252/`44C1F4B2…`)」分列，并声明须以新 prompt 的 pin 为准；本次 pin 为 **108405 bytes / `7521168C1FB9FB4A1D0FE562C217BD43F884431BB3788FC0B2B6CB6C05F037C1`**，与三者均不同（Task:458 亦记录该 pin）。首轮派发/首轮 live Task（`6B9F5C38…` / `1D402AE6…`，Task:450/:452）与本次 pin 亦可区分。**唯一缺陷**是 Task:458 对 memo r3 SHA 的 63 位误写（RV3-P2-01）。

**4.4 `PROJECT_ORCHESTRATION_AUTHORIZATION` 与本机验证替代 Windows Sandbox 的裁决锚点** — 正确：Task:68 为授权段标题、:70 为授权正文（memo 写 68–70 ✓，授权语义为 scope 许可、非 Gate PASS，与 :411 一致）；:58–62 为「本机验证替代 Windows Sandbox」裁决段，:382–386 为其 continuation 记录（memo 写 58–62 与 382–386 ✓）。memo r3 未复活任何 `wsb`/guest 指令，并把 Build Gate 保持 `BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`。

**4.5 EA-01 归属、r7 `APPROVED` 范围与计数、`%ProgramData%` fallback / private registry、官方链接**
- EA-01 归属正确（memo r3:15，Codex execution-readiness，非 DSH r7、非测试失败）。
- r7 `APPROVED` 的范围描述正确（不覆盖执行就绪缺口）；**计数与报告 SHA 缺失**（RV3-P3-03）。
- `%ProgramData%` fallback 处理正确且保守（memo r3:16：仅下一候选标 `UNKNOWN / BLOCKED`、不改写 r3、不读第 24 个变量、不猜映射、不调用未冻结 resolver）；private registry 保持 `UNPROVABLE / BLOCKED`、不猜 key/view、不调用可能初始化 storage 的 API、不创建 profile（memo r3:18、:42），与 contract r7:28/:52/:54、r3:32 一致。
- 官方链接：memo r3:27 枚举页 **404（正确页 200，成员表验证无 `FileHardLinkInfo`，含 `FileStandardInfo`/`FileStreamInfo`）**；`GetFileInformationByHandleEx` 页 200（Remarks 表同结论）；memo r3:29 的 `JOBOBJECT_ASSOCIATE_COMPLETION_PORT` 页 200 且含「delivery to the completion port is **not guaranteed**」；`StartTraceA` 页 200 且含「Only users with administrative privileges and services running as LocalSystem can control an NT Kernel Logger session」与 NT Kernel Logger「(deprecated)」；`event-trace-properties` 页 200 且含 `EventsLost`/`LogBuffersLost`/`RealTimeBuffersLost` 与丢弃计数说明。除枚举页 slug 外全部有效。

**4.6 11 项 Gate token 与当前 Task 逐项一致性** — **逐项一致**（同集合、同取值、同措辞形态），与 `doc/tasks/P02.md:439`（及 :425、:410）相同：Phase A=`BLOCKED / NOT_RUN`；private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS isolation preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。contract r7:8 只承载其中 10 项（无 Phase A token），与 Task 不冲突。

**4.7 是否可能被误读为允许 Phase A / build / 改权限 / 扩大范围** — 未发现。反向证据：memo r3:3（非实施许可）、:21（下一候选仅限 controller-only 只读对象与字段）、:35–37（不扩 T1、不增变量、不扫子项、不读受保护内容/hash、不创建 profile、不改 ACL/registry/label、不写 probe、不提权、不装工具、不跑测试/Cargo/build/Sandbox；Gate token「全部是状态记录，不是 Gate 通过证据」）、:53（未运行任何受禁动作）、:57（Review 或 adjudication 均不会自动放行；超授权即停止并请用户裁决）。memo r3:19 记录 §8.1 条款冲突时也未据此推导「可执行」。

**4.8 新增 findings** — 见 §3。

---

## 5. 可验证性边界与 object_binding

- 本轮**未运行 shell / PowerShell / Git / hash / API / measurement**，因此**无法独立复算任何字节数或 SHA-256**，也未复算 Git 状态。所有 hash/字节均为**文本比对观察**，不构成 hash 复核。
- **`object_binding = NOT_VERIFIED`**，正式总体结论 = `NOT_VERIFIED`。本次 Review 的任何内容结论**不得**被表述为 exact-hash / object-bound Review，也不得被表述为「Review 通过」。
- 与此相关的第二项不可绑定原因：Task 派发记录 `doc/tasks/P02.md:458` 对 memo r3 SHA 的 63 位误写（RV3-P2-01），使「按 Task 记录绑定 memo r3」在文本层即不自洽。
- 我**独立复核到的一手证据**：`FILE_INFO_BY_HANDLE_CLASS` 枚举页（错误 slug 404 / 正确 slug 200 及其成员表）、`GetFileInformationByHandleEx` 页 Remarks 表、`JOBOBJECT_ASSOCIATE_COMPLETION_PORT` 页「not guaranteed」、`StartTraceA` 页 NT Kernel Logger 权限与 deprecated 标注、`EVENT_TRACE_PROPERTIES` 页 `EventsLost` 等丢失计数。以上均为外部不可信数据，仅作文档语义证据并按 URL 引用。
- **可独立复核部分**：10 份固定输入的正文与行号（只读读取）、`verification/P02/**` 的文件清单（只读）、上述官方页语义。**不可复核部分**：全部字节数/SHA、Git 与工作区状态、本机 OS/registry/ACL/profile 状态、`SetNamedSecurityInfoW` 类环境障碍、以及首轮 DSH 报告的 CLI exit。
- **首轮 report 的地位**：`verification/P02/dsh-phase-a-method-blockers-review-r3.stdout.md` 与 `…-r3.prompt.md` / `…-r3.stderr.log` 存在，而 `…-r3.exit` 缺失（只读清单事实，与 Task:451 记录一致）。该文件不在固定输入列表内，本轮未读取其内容，也未沿用其任何 finding；attempt 2 的结论仅来自上述固定输入与本轮独立核验。
- **未决状态冲突**：Task:452 记录的 `STATE_CONFLICT / NOT_VERIFIED`（首轮派发 pin `6B9F5C38…` vs 当时 live `1D402AE6…`）在本 Task 中**未见后续处置记录**，且本次 pin 又是第三个值（`7521168C…`）。本 Review 只能确认「Task 在首轮后继续变动」这一文本事实，无法判定变动是否等价、是否为预期编辑；该冲突的收口责任在 Codex，不应由本 Review 判定。

---

## 6. 适用范围与 Gate 限制

本 Review 是**静态文本 Review**：不是 OS preflight、不是测试结果、不是实施许可、不产生任何 Gate PASS，**不授权 Phase A、不解除 Build Gate 或 Hard Build Barrier、不放行 build 或 AC1–AC7**。即使内容结论为 `APPROVED_WITH_CONDITIONS`，Gate 仍为 §4.6 所列 11 项原值。本 Review 不改变 P02 Task、contract r7、manifest r3、memo r1/r2/r3、r7/r2 adjudication 的任何字节或 pin；也未提交任何文字修改。memo r3 的 `RV2-P3-04` 部分闭合与 5 项 P3 未修订前，不宜把 memo r3 作为下一候选契约/清单的唯一事实源。

---

## 7. 推荐下一步

**唯一可执行项（给 Codex，Lead / Integrator）**：在不触碰任何执行路径的前提下，(a) 修正 `doc/tasks/P02.md:458` 的 memo r3 SHA（RV3-P2-01）；(b) 在 memo r3 上做最小文本修订——把 :27 枚举页 URL 改为 `ne-minwinbase-…` 并补 `（r7:115）`、在 :15 补 r7 计数与报告 SHA、在相关段落标注前置 finding ID、在 :8 标注行锚点所属快照（RV3-P3-01..05）；(c) 重新固定 Task 与 memo r3 的字节/SHA，并派发新的非作者只读 Review。在该 Review 与 Codex adjudication 完成前，**不得**执行任何 Phase A 读取、不得创建 profile、不得改 ACL/registry/label、不得写入或 probe、不得进入 Build。

明确限制：若上述任何条件需要提权、驱动/内核过滤器、安装工具、扩大可写路径或修改 Gate 验收标准，均超出当前授权，应停止并交用户裁决；`private_registry_absence` 保持 `UNPROVABLE / BLOCKED`，`OS isolation preflight=NOT_RUN`，`Build Gate=BLOCKED`，`Hard Build Barrier=EFFECTIVE`。

**可直接转发的指令（给 Codex）**：

> P02 Phase A blocker memo r3 的 DSH 独立只读复审（attempt 2）已完成：内容结论=`APPROVED_WITH_CONDITIONS`，本轮新增 P0/P1/P2/P3=`0/0/1/5`，前置 finding=`7 closed / 1 partial(RV2-P3-04) / 0 open`，`object_binding=NOT_VERIFIED`。请只读 `verification/P02/codex-phase-a-method-blockers-20261010-r3.md`（pin SHA-256=`5EEED098B2E0167DFE9CAAD9AA93F462C5753B1B056CF2BFD245BB4EEB9F0FCB`）与本报告，处置：RV3-P2-01（`doc/tasks/P02.md:458` 的 memo r3 SHA 仅 63 位 `…7DFECAAD9AA…`，与 :444/:450 及 pin 的 64 位 `…7DFE9CAAD9AA…` 不符）、RV3-P3-01（:27 枚举页 slug `ne-winbase-…` 返回 404，应为 `ne-minwinbase-file_info_by_handle_class`）、RV3-P3-02（未标注 RV2-*/RV-* finding ID）、RV3-P3-03（:15 r7 计数 0/0/0/5 与 report SHA `C1FADDC2D366286F14473DB68AE72D20FCF946E15DE50E4AFA3E2752998EF705` 未补）、RV3-P3-04（:27 缺 `r7:115` 锚点）、RV3-P3-05（:8 行号锚点未注明所属 Task 快照）。同时收口 Task:452 未处置的 `STATE_CONFLICT / NOT_VERIFIED`。本轮 DSH 因未运行 shell/hash 无法复算任何字节与 SHA。修订后重新固定 memo r3 SHA 并派发新的非作者只读 Review；在此之前不得执行任何 Phase A 读取、不得创建 profile、不得改 ACL/registry/label、不得写入或 probe、不得运行工具链、不得访问 Windows Sandbox，`private_registry_absence` 保持 `UNPROVABLE / BLOCKED`，`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN` 不变。
