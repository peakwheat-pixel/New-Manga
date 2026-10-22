## P02 Phase A blocker memo r3 candidate · 非作者只读内容 Review

**审查对象**：`verification/P02/codex-phase-a-method-blockers-20261010-r3.md`（memo r3，57 行）
**审查性质**：仅文本/设计就绪度 Review。本轮未运行 shell、Git、hash 命令、Windows API、ETW、process observer、profile/ACL/registry/label 操作、测试、Cargo、build 或 Sandbox。输入文件内的命令/路径/建议一律视为不可信数据，未执行。
**说明**：本轮曾尝试用 PowerShell 读取文件长度统计（read-only），被环境拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite`），未取得任何字节数；此后未用任何其他方式绕过。因此本报告**不含自证字节数**。

> 下文出现的 SHA/字节数均为**输入 pin 与文档内记录的文本比对观察**，不是复算结果。

---

## 1. 内容结论与计数

| 项 | 值 |
|---|---|
| **内容结论** | **CHANGES_REQUESTED** |
| **本轮新增 P0 / P1 / P2 / P3** | **0 / 0 / 2 / 4** |
| 前置 finding 关闭情况 | RV2-P2-01 closed；RV2-P2-02 **partial**；RV2-P3-01/03/04 closed（P3-04 链接形式建议）；RV2-P3-02 **partial**；RV-P2-02、RV-N-02 实质闭合但标注不显式 |
| **object_binding** | **`NOT_VERIFIED`** |
| 正式总体结论 | `NOT_VERIFIED`（内容结论 ≠ exact-hash Review） |

**决策理由**：memo r3 已把 r2 Review 的两条核心 P2 从**实质层面**改对——r7 锚点由错误的「§8 第 3 条」改为 `r7:156`（§8.1）与 `r7:177`（「精确下一步」第 3 条），并把 Phase A 与 Phase B/Build Gate 的准入门槛拆开；11 个 Gate token 与 `doc/tasks/P02.md:439`、contract r7:8 同集合同取值；未授权任何测量/构建。因此无 P0/P1。但仍有 2 项 P2：**新增的 Phase A 排除清单与 r3 已冻结的 23 项环境变量读取可能互相抵触**；**Task 修订快照三元组缺少来源标注**。修完前不宜把 memo r3 作为下一候选契约/清单的事实源。

---

## 2. 复核重点逐项回答

### 2.1 RV2-P2-01（锚点）—— **closed**
- memo r3:19 写「contract r7 §8.1（r7:156）列出的三项准入」与「"精确下一步"第 3 条（r7:177）」。
- 逐字核对：`contract r7:156` = §8 第 1 条（即 §8.1），含 manifest r3 路径/SHA 与「DSH r7 Review、Codex adjudication 与逐文件 SHA-256/object pin 核对全部完成」；`contract r7:177` = 「精确下一步」第 3 条，含「Phase A manifest 均无歧义」。两处 `r7:NNN` 行号锚定**准确**。
- 与 r2 adjudication 要求的最小处置（r2ad:32：「改为 r7 §8 第 1 条（§8.1，r7:156）与"精确下一步"第 3 条（r7:177）」）完全对应；r7 §8 第 3 条（`contract r7:158`）确为受保护文件 hash 规则，不含无歧义要求，旧误标已清除。
- 结论：**closed**（唯一可选措辞改进见 F3，P3）。

### 2.2 RV2-P2-02（阶段拆分）—— **partial**
已做对的部分：
- memo r3:17「r3 的 Phase A 是 controller-only 只读测量，不检查子进程、不写入、也不读取文件内容或 hash」——与 r3:12/32 一致。
- memo r3:21「Phase A 不纳入进程树检查、scratch 写入、cache 重定向回读或文件 hash」。
- memo r3:25 把「完整主进程及所有后代的隔离身份、保护目录拒绝写入、scratch 正向写入权限、TEMP/cache 重定向、运行前后受保护文件 hash 一致及所需的进程/写入闭包」明确归入 Phase B / Build Gate，并要求「每项需独立冻结精确方法、路径、字段、失败判据和证据」——与 contract §8 第 6 条（`contract r7:161`）对应，未并入下一 Phase A manifest。
未闭合的部分见 **F1（P2）**：第 21 行的排除句「cache 重定向回读」与 r3:20「只读取当前 controller 的以下 23 个环境变量（该集合是 Phase A 完整集合）」并置后，可被误读为 r3 已冻结的环境变量类别读取也属排除项。

### 2.3 RV2-P3-01..04
- **RV2-P3-01（closed，附 P3 建议）**：memo r3:16「只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；该 fallback 不会改写 manifest r3」→ 约束位置正确。可补的显式句见 F5。
- **RV2-P3-02（partial）**：memo r3:9 已给三组字节数/SHA 与「三个 Task snapshot 是不同历史修订……不能互换」，远超 r2 水平；但未标注每组对应哪一轮派发，也未按建议锚定授权段落（详见 F4）。
- **RV2-P3-03（closed）**：memo r3:15 明确「这是 Codex execution-readiness finding，不是 DSH r7 finding，也不是测试失败」，并写明「DSH r7 对 contract r7 与 manifest r3 的内容 Review=`APPROVED`，但其范围不涵盖 Codex 后续发现的执行就绪缺口，不能据此推出 r3 可执行」。与 `codex-appcontainer-contract-r7-adjudication.md:24`（`APPROVED`，0/0/0/5）与 `:40`（EA-01 性质）一致。F6 仅为可选补强。
- **RV2-P3-04（closed）**：memo r3:27 已改引枚举页；链接可及（见 §4），仅措辞与路径形式建议（F6）。

### 2.4 旧 RV-* disposition 是否被抹去 —— **未被抹去**
memo r3:10 记录 memo r1=`APPROVED_WITH_CONDITIONS`（0/0/4/5）、memo r2=`APPROVED_WITH_CONDITIONS`（0/0/2/4），并保留两轮 `object_binding=NOT_VERIFIED`、r2 对象 6961 bytes/SHA、r2 DSH report SHA、r2 adjudication SHA，且明写「前述静态 Review 结论不被继承为本候选批准」。对照 r2 报告 §2 的 r1 dispositions（10 closed / RV-N-02 partial / RV-P2-02 partial / 0 open）与 r1 adjudication:22-37 的 12 项 + T1 不采纳，无被静默升级或删除的项。
唯一可读性缺口：memo r3:10 未点名「partial 的是 RV-P2-02 与 RV-N-02」（F4 的附带部分）。

### 2.5 Phase A 边界叙述是否清楚
- 不检查子进程、不写入、不读内容/hash：r3:17、21、25、32 内外一致。
- 「未来 Phase B/Build Gate 对完整进程树、写入闭包、scratch、TEMP/cache 与 hash 的要求不会并入 Phase A」：**成立**（r3:25 明列于 Phase B 段，并称「不能并入下一 Phase A manifest」）。
- 与 contract 一致：`contract r7:44`（§1.2 Phase A 不检查文件内容或 hash、子进程、profile…）、`contract r7:46`（Phase B 独立冻结）、`contract r7:157`（Phase B manifest 要求）均支持。

### 2.6 Task 修订 snapshot / 授权引用
- 字节数与 SHA：memo r3:9 给出 100139/AB0635…、102674/A35CB3…、105252/44C1F4B2…。与 r1 adjudication:11、r2 adjudication:11、`doc/tasks/P02.md:444` 的文本记录一致；**未复算**。
- 修订范围：有（「memo r1 首轮 DSH 派发时 / memo r2 复审派发时 / 本 memo r3 候选创建时」+「三个 Task snapshot 是不同历史修订……不能互换」）。
- 用户授权：memo r3:8「P02 Task 的 PROJECT_ORCHESTRATION_AUTHORIZATION 段（当前行 68–70）……授权是范围许可，不是 OS 证据或 Gate PASS」；核对 `doc/tasks/P02.md:68` 确为该段标题、:70 为其正文，**锚点正确**。
- 本机验证替代 Sandbox：memo r3:8「P02 Task 行 58–62 与 382–386 记录用户裁决本机 Windows 验证替代 Windows Sandbox」；核对 :58-62（标题+裁决正文）与 :382-386 均正确，且全篇未把该裁决当作 Gate 证据（r3:8 明写「不是 OS 证据或 Gate PASS」；r3:36「不运行……Sandbox」）。**准确**。
- 缺陷见 F4（P2）。

### 2.7 EA-01 / DSH r7 范围 / %ProgramData% / private registry
- EA-01 attribution：**准确**（r3:15，见 2.3）。
- DSH r7 `APPROVED` 范围：**准确但未量化**（缺 0/0/0/5；F6）。
- `%ProgramData%` fallback 仅适用于后续 candidate、r3 pin 不变：**准确**（r3:16「只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；该 fallback 不会改写 manifest r3」；r3:18「不得读取第 24 个变量、猜测映射或调用未冻结的 resolver」）。r3 原文确未改动：`appcontainer-readonly-preflight-r3.md:27-28` 仍把两条 `%ProgramData%` 目录列为 T0/T1 目标。
- private registry=`UNPROVABLE / BLOCKED`：**准确**（r3:18 与 `contract r7:28`/`:52`、r7-adjudication:58 一致；并明写「不得猜 registry key/view、调用可能初始化 storage 的 API 或创建 profile」）。

### 2.8 FileHardLinkInfo 与其他 OS observer
- **仅归 Phase B/Build Gate**：成立（memo r3:27「这是 Phase B 的精确文件/链接检查候选缺陷；Phase A r3 不打开文件，故不新增 Phase A 调用」）；与 r7 原文 `GetFileInformationByHandleEx(FileHardLinkInfo)` 属 `contract r7:115`（§5 路径规范化）一致。
- **引用了枚举主页面**：是 —[FILE_INFO_BY_HANDLE_CLASS enumeration](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-winbase-file_info_by_handle_class)（另有[函数页](https://learn.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-getfileinformationbyhandleex)）。
- **我方独立核对该断言（读取外部一手页面）**：枚举成员表为 `FileBasicInfo … FileStandardInfo … FileStreamInfo … FileNormalizedNameInfo, MaximumFileInfoByHandleClass`，**不含 `FileHardLinkInfo`**；memo r3:27 的主张成立，无过度断言。
- **其他 OS observer 描述有来源且未过度断言**：逐条核对——
  - 「Job completion-port 消息并不保证全部送达」：[JOBOBJECT_ASSOCIATE_COMPLETION_PORT](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port) 明写 delivery "is not guaranteed"，成立。
  - 「NT Kernel Logger 已弃用且控制要求管理员或 LocalSystem」：[StartTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea) 明写 NT Kernel Logger 为 deprecated，且 "Only users with administrative privileges and services running as LocalSystem can control an NT Kernel Logger session"，成立。
  - 「ETW 也记录丢失事件/缓冲计数」：[EVENT_TRACE_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/etw/event-trace-properties) 含 `EventsLost`（"the number of events that were not recorded"）、`LogBuffersLost`、`RealTimeBuffersLost`，成立。
  - 免责句「不据此断言 Windows 一般不存在其他可行机制」（r3:29）、「上述资料是设计限制，不是本机运行证据」——克制，无过度断言。
- 附带：r3:31 对 `NtOpenFile`（ntdll，超出 r3 的 PowerShell/.NET 约束）与「PowerShell 7 `Add-Type` 文档不证明 Windows PowerShell 5.1 行为」的处理，与 r1 adjudication:32/34 一致，未把顾问建议当证据。

### 2.9 Gate token / 数据边界 / 禁用操作 / 是否可被误读
- r3:41-51 的 11 项与 `doc/tasks/P02.md:439`（及 :395、:404、:425）**同集合、同取值**：Phase A=`BLOCKED / NOT_RUN`；private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS isolation preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。另有 r3:37「全部是状态记录，不是 Gate 通过证据」。
- 数据边界与禁用操作（r3:33-37）与 `contract r7:18`/`:114-118`、r3:12/32/34 一致：不扩 T1 到额外 16 根、不加环境变量、不扫子项、不读受保护文件内容/hash、不碰漫画库/数据库/Lock/current·pinned Revision/凭据/生产数据、不建 profile、不改 ACL/registry/label、不写 probe、不提权、不装工具、不扩可写路径、不跑测试/Cargo/build/Sandbox。
- 「可被误读为允许测量/构建/扩大范围」的表述：未发现正面授权句。r3:3、:53、:55、:57 反复声明非测试结果、未运行、不自动放行、需用户裁决。唯一需要收紧的是 F1。

---

## 3. 本轮 findings

### P2

**RV3-P2-01｜Phase A 排除清单与 r3 已冻结的环境变量读取可能互相抵触（阶段边界内部不一致）**
- 位置：`codex-phase-a-method-blockers-20261010-r3.md:21`（「Phase A 不纳入进程树检查、scratch 写入、cache 重定向回读或文件 hash」），与 `:17`、`:25` 并读。
- 缺陷：「cache 重定向回读」与 r3 的 controller 环境变量类别读取边界不清。r3:20 明确 Phase A **要读** controller 的 23 个变量（含 `CARGO_HOME`、`NPM_CONFIG_CACHE`、`HF_HOME`、`PYTHONUSERBASE` 等 cache 相关项，且该集合被声明为「Phase A 完整集合」）；`contract r7:44` 亦把「Phase A 完整集合 23 个 controller 环境变量」列为允许读取，排除的是**子进程回读**与「cache 重定向/写入闭包证据」。memo r3:21 未加该限定词，恰是 RV2-P2-02 要求防止的「阶段混同」方向的反向版本：读者可能据此认为 r3 的环境变量读取超出 Phase A，进而在下一候选里删除或改写 r3 已冻结读取集合。
- 最小修订：把 :21 改为「Phase A 保留 manifest r3:20 已冻结的 23 项 controller 环境变量类别读取；此处排除的是子进程环境回读、cache 重定向证据、scratch 写入、进程树检查与文件 hash」。

**RV3-P2-02｜Task 修订快照三元组缺少来源标注，且未锚定授权段落**
- 位置：`:9`（「Task 修订快照」行）。
- 缺陷：三组「字节数 / SHA」只按 memo 轮次命名（memo r1 首轮派发 / memo r2 复审派发 / 本 memo r3 候选创建时），未标明各自对应哪一次 Review 派发的 Task pin、也未标注哪一组是本次 r3 Review 的固定 pin。评审者必须跨读 r1 adjudication:11、r2 adjudication:11、`doc/tasks/P02.md:431`/`:444`/`:450` 才能定位，这正是 RV2-P3-02 建议（「补字节数与锚定段落（如 `doc/tasks/P02.md:68-70`）」）未落实的部分；`:8` 虽写了授权段锚点，但 :9 的授权依据行未复述。
- 最小修订：在 :9 后逐条加标签，例如「r1 DSH review pin=AB0635…（100139 bytes，对应 `doc/tasks/P02.md` 该轮派发记录）；r2 DSH review pin=A35CB3…（102674 bytes，对应 `doc/tasks/P02.md:431`）；本次 r3 review pin=44C1F4B2…（105252 bytes，对应 `doc/tasks/P02.md:444`）」，并注明「本 memo 的授权依据段落=`doc/tasks/P02.md:68-70`」。
- 说明：该缺陷不影响任何 Gate 结论；但 memo r3 的主要用途之一就是固定「以哪个 Task pin 为准」，因此不应停在 partial。

### P3

**RV3-P3-01｜fallback 建议补「r3 pin 不变且禁止执行」的显式句**
- 位置：`:16`。现已写「只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；该 fallback 不会改写 manifest r3」，语义已达 RV2-P3-01 要求；建议再补「manifest r3 的字节与 SHA-256 pin 不变，且按其状态仍禁止执行」，避免「不会改写」被读成「已按 fallback 重签」。

**RV3-P3-02｜§8.1 三项条件概括为「三项准入」宜加限定**
- 位置：`:19`。`contract r7:156` 的三项实为「唯一候选范围 + Review/adjudication/逐文件 SHA·object pin 核对完成 + 不得调用 profile/private-registry API、不得写」；概括为「三项准入」在 `:15` 已说明执行缺口仍未闭合的语境下无放行风险，但建议写成「§8.1（r7:156）列出的三项执行前置（范围、Review/adjudication/object pin 完成、禁写禁 profile API）」，以免被引为「准入已满足」。

**RV3-P3-03｜补记 old RV-* 的 partial 归属，增强自包含性**
- 位置：`:10`。建议补「RV-P2-02（r2 误标 §8 第 3 条）与 RV-N-02（Task snapshot 未固定）为 partial，其余 RV-* 为 closed」，使「0/0/2/4 且 10 closed/1 partial/0 open」不依赖 r2 adjudication 才能解码。

**RV3-P3-04｜枚举链接形式与 DSH r7 `APPROVED` 计数的两处可选补强**
- (a) `:27` 的枚举链接写作 `.../ne-winbase-file_info_by_handle_class`；建议统一为枚举主页面 `.../ne-minwinbase-file_info_by_handle_class`（两路径当前均可达并渲染同一页，已由本轮外部读取确认；仅一致性问题）。
- (b) `:15` 建议补计数「DSH r7 内容 Review=`APPROVED`（P0/P1/P2/P3=`0/0/0/5`）」，依据 `codex-appcontainer-contract-r7-adjudication.md:24`，以完整闭合 RV2-P3-03 的建议措辞。

---

## 4. 逐项 disposition 总表

| 前置 finding | 本轮判定 | 文本依据 |
|---|---|---|
| RV2-P2-01（r7 锚点） | **closed** | r3:19；`r7:156`（§8.1）、`r7:177`（精确下一步第 3 条）行号核对无误；r7:158 为 hash 规则，旧误标已除 |
| RV2-P2-02（Phase A/Phase B 拆分） | **partial** → RV3-P2-01 | r3:17/21/25 拆分成立；:21「cache 重定向回读」与 r3:20 的 23 变量集合并置可被误读 |
| RV2-P3-01（%ProgramData% fallback 落地位置） | **closed**（建议 RV3-P3-01） | r3:16「只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；不会改写 manifest r3」 |
| RV2-P3-02（Task snapshot 字节数/范围/授权锚点） | **partial** → RV3-P2-02 | r3:9 有三元组与「不能互换」；缺来源标注，:9 未复述 :8 的 `68–70` 锚点 |
| RV2-P3-03（EA-01 归属 + r7 APPROVED 范围） | **closed**（建议 RV3-P3-04b） | r3:15 明写非 DSH r7 finding、非测试失败、APPROVED 不覆盖 EA-01；未给 0/0/0/5 |
| RV2-P3-04（枚举页来源） | **closed**（建议 RV3-P3-04a） | r3:27 已引枚举页；断言经外部核对成立 |
| RV-P2-02（partial → 锚点） | **实质闭合**，建议 RV3-P3-02 | r3:19 已按 r2ad:32 修正；「三项准入」概括宜加限定 |
| RV-N-02（partial → Task 修订范围） | **实质闭合**，建议 RV3-P3-03 | r3:9 已补修订范围；缺标签与 partial 归属 |
| RV-P2-01/03/04、RV-P3-01..05、RV-N-01/03、T1 不采纳 | **未被改写或抹去** | r3:10 保留两轮结论与 `object_binding=NOT_VERIFIED`；r3:33-36 维持 T1/范围禁令 |

---

## 5. 可验证性边界

- 本轮**未运行** shell、Git、hash 命令、Windows API、ETW、process observer、profile/ACL/registry/label 操作、测试、Cargo、build 或 Sandbox；**未修改任何文件**。故**无法复算任何 SHA-256 或字节数**，`object_binding=NOT_VERIFIED`，正式总体结论=`NOT_VERIFIED`。本报告**不得**被表述为 exact-hash / object-bound Review。
- 一次 read-only PowerShell 长度统计尝试被环境拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite`），**未取得数据**；未以任何替代方式规避。
- 可独立复核部分（已完成）：8 份固定输入 + `doc/tasks/P02.md`、r1 adjudication、r1 memo 的只读正文与行号核对；只读文本检索；4 个 Microsoft Learn 页面的一手语义核对（`FILE_INFO_BY_HANDLE_CLASS`、`JOBOBJECT_ASSOCIATE_COMPLETION_PORT`、`StartTrace`、`EVENT_TRACE_PROPERTIES`）。
- 仅**文本比对观察**：memo r3 记录的 100139/AB0635…、102674/A35CB3…、105252/44C1F4B2…、6961、6339、32969 与 r1/r2 adjudication 及 `doc/tasks/P02.md` 的记录互相一致；DSH r1 report SHA `67677D2E…` 与 r1 prompt SHA `4F80472D…` **不在本次固定输入与用户列表内**，本轮无法独立核对 memo r3 相关表述（`:10`）——这三项属**不可验证边界**。
- 未复算 DSH r2 report（`846E4ADA…`）、r2 prompt（`D14B1EC6…`）与 r2 memo 的字节数；`:10` 的值均为文本转录。

---

## 6. 授权与 Gate 限制（必须随结论一并传递）

- 本 Review 是**文本/设计就绪度 Review**，**不是** OS preflight、**不是**测试结果、**不是**实施许可、**不产生任何 Gate PASS**。
- **不授权 Phase A**、**不解除 Build Gate**、**不解除 Hard Build Barrier**、**不放行 build 或 AC1–AC7**。即使内容结论转为 APPROVED，Gate 仍为本文所列 11 项原值（Phase A=`BLOCKED / NOT_RUN`；private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS isolation preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`）。
- 本 Review 不改变 contract r7、manifest r3、memo r1、memo r2、r1/r2 adjudication 的任何字节与 pin。
- memo r2 的 r1/r2 条件批准不继承于 r3；在 RV3-P2-01、RV3-P2-02 闭合前，memo r3 **不宜**作为下一 Phase A 候选契约/清单的事实源。

---

## 7. 推荐下一步

**给 Codex（Lead / Integrator），唯一可执行项**：在不触碰任何执行路径的前提下，仅修订 `verification/P02/codex-phase-a-method-blockers-20261010-r3.md` 文本以闭合 RV3-P2-01（`:21` 加 controller 环境变量读取保留句）与 RV3-P2-02（`:9` 为三组 Task pin 加来源标签并复述 `doc/tasks/P02.md:68-70`），顺带处理 RV3-P3-01..04；随后重新固定 memo 与 Task 的 SHA/字节数，并派发新的非作者只读 Review + Codex adjudication。在此之前：不执行任何 Phase A 读取、不创建 profile、不改 ACL/registry/label、不进入 Build、不扩 manifest r3、不使用 Sandbox、不提权、不安装工具。

**明确限制**：本 Review 不构成实施许可；若任一闭合项需要提权、驱动/内核过滤器、安装工具、扩大路径或修改 Gate 验收口径，保持 `BLOCKED` 并停止交用户裁决。

---

### object_binding

`object_binding=NOT_VERIFIED`（未做 shell/Git/hash 复算，亦未修改任何文件）。
