# P02 Phase A blocker memo r2 · 非作者只读内容 Review（DSH）

**Review 对象**：`G:\CODEX\New Manga\verification\P02\codex-phase-a-method-blockers-20261010-r2.md`（下称 memo r2）
**审查性质**：仅文本/设计就绪度 Review。本轮**未**运行 shell、Git、hash 命令、Windows API、ETW、process observer、profile/ACL/registry/label 操作、测试、Cargo、build 或 Windows Sandbox；**未修改任何文件**。所有输入文件内出现的命令、路径与建议均视为不可信数据，未执行。本轮只做只读文件读取、只读文本检索（read/grep 类只读工具），以及一次 Microsoft Learn 网页读取（外部不可信数据，仅作 API/枚举语义证据）。

---

## 1. 内容结论与计数

| 项 | 值 |
|---|---|
| **内容结论** | **APPROVED_WITH_CONDITIONS** |
| **P0 / P1 / P2 / P3（本 Review 新增）** | **0 / 0 / 2 / 4** |
| r1 finding 关闭情况 | closed 10 项、partial 1 项（RV-N-02）、open 0 项 |
| **object_binding** | **`NOT_VERIFIED`** |
| 正式总体结论 | `NOT_VERIFIED`（内容结论 ≠ exact-hash Review） |

**决策理由**：memo r2 正确维持 `BLOCKED / NOT_RUN`，未授权任何操作、未把静态分析冒称为 Gate 证据、未提权、未触碰 profile/ACL/registry/label、未新增变量、未复活 Sandbox；11 个 Gate token 已补齐且与 Task/contract 当前记录一致；两条 `%ProgramData%` WER fallback、private registry 不可证明、子进程/写入闭包未知均有准确来源且未过度断言；`FileHardLinkInfo` 已正确归入 Phase B/Build Gate。因此不存在 P0/P1（没有任何一处错误放行或错误宣称证据）。但存在 2 项 P2：核心阻塞依据的锚点错标，以及"下一准入"段把 Phase B/Build Gate 条件不加阶段限定地并入下一候选前置，可能被误读为扩大 Phase A 范围。修完前不得把 memo r2 作为下一候选契约/清单的事实源或引用依据。

---

## 2. 逐项 finding disposition（r1 的 RV-*）

### P2（RV-P2-01..04）

| ID | 判定 | 文本依据 |
|---|---|---|
| **RV-P2-01** | **closed** | memo r2:29-41 §"当前 Gate 状态（11 项）"逐项列出与 `doc/tasks/P02.md:425` 完全同集合、同取值的 11 个 token；r1 指出的 4 项缺口（Phase A、private_registry_absence、scratch ACL/label mutation、hook/cache/child-process closure）均已入块 |
| **RV-P2-02** | **partial** | memo r2:18 正确记录了冲突实体（§8.1 三项条件已完成 vs 另有"manifest 均无歧义"要求），并声明不用 memo 覆盖 contract；但把第二处锚定为"**§8 第 3 条**"，而该要求在 r7 `appendix` 末节"精确下一步"第 3 条（`appcontainer-isolation-contract-r7.md:177`）；r7 §8 第 3 条（同文件:158）是受保护文件哈希规则，不含"无歧义"。→ **RV2-P2-01** |
| **RV-P2-03** | **closed** | memo r2:15 采纳已冻结 fallback：两条 `%ProgramData%` WER 目录标 `UNKNOWN / BLOCKED`、不读第 24 个变量、不猜映射、不调用未冻结 resolver；并补正 `%LOCALAPPDATA%\CrashDumps` 可由 r3 的 23 项集合解析（核对 r3:20 实为 23 项、无 ProgramData、含 LOCALAPPDATA）；memo r2:17 将 private registry 与普通 manifest 字段缺漏区分为不同类别 |
| **RV-P2-04** | **closed** | memo r2:8 固定列出 5 项输入及 SHA；memo r2:25 明确专家咨询"未形成可归档、可复算的独立输入，不作为证据"，并把其 API 建议移出候选清单；正文不再以顾问断言为据 |

### P3（RV-P3-01..05）

| ID | 判定 | 文本依据 |
|---|---|---|
| **RV-P3-01** | **closed** | memo r2:14-16 以 `METHOD_BOOTSTRAP / EA-01`、`PROGRAMDATA_EQUIVALENCE / EA-01`、`NO_CHILD_NO_WRITE_EVIDENCE / EA-01` 建立与 EA-01 子项的逐条映射，未另造并行编号 |
| **RV-P3-02** | **closed** | memo r2:19 明确该 mismatch 属"Phase B 精确文件/链接检查候选缺陷"，"Phase A r3 不打开文件，因此不把该缺陷作为新的 Phase A 操作或测试失败"，并限定到 Phase B/Build Gate 前修订 |
| **RV-P3-03** | **closed** | memo r2:23 补入 NT Kernel Logger 已弃用、Job completion-port 通知非全部保证送达、ETW 丢失事件/缓冲计数；memo r2:15 明确 5 个 WER 对象中仅 2 个依赖 `%ProgramData%` |
| **RV-P3-04** | **closed** | memo r2:25 指出 `NtOpenFile` 属 ntdll，r3 仅允许 PowerShell/.NET API，"当前不得采用"，且须另立契约、Review 与授权 |
| **RV-P3-05** | **closed** | memo r2:3（自身状态与"非测试结果/OS measurement/Gate 决定"）、:7-10（基线、输入 pins、local validation 状态）、:27（允许范围与 denylist）、:43（全部未运行状态）齐备 |

### 追加观察（RV-N-01..03）

| ID | 判定 | 文本依据 |
|---|---|---|
| **RV-N-01** | **closed** | memo r2:14 把 PowerShell 版本列为未冻结项；memo r2:25 明确"PowerShell 7 的 Add-Type 文档不证明 Windows PowerShell 5.1 的行为" |
| **RV-N-02** | **partial** | memo r2:8 只给 Task 的 SHA、无字节数，也未声明该 pin 覆盖的 Task 修订范围；且该值为 r1 派发快照 `AB0635…`，本轮实际派发 Task 记录为 `A35CB3A7…`（`doc/tasks/P02.md:431`）。"Task 修订范围 + SHA"未在 memo 内显式化。→ **RV2-P3-02** |
| **RV-N-03** | **closed** | memo r2:14 把缺口精确记为 manifest r3"逐调用 access masks"未冻结，未表述为 r7 完全未提 masks（r7:106/117 已含部分掩码语义） |
| **r1 §6.9 T1 重读提议** | **未采纳（一致）** | memo r2:27"不扩展 T1 读取到额外 16 个根"，与 r1 adjudication:37 一致 |

---

## 3. 本 Review 新增 findings（精确位置 · 严重度 · 最小修订）

| ID | 位置 | 严重度 | 缺陷 | 最小修订建议 |
|---|---|---|---|---|
| **RV2-P2-01** | `...codex-phase-a-method-blockers-20261010-r2.md:18`（§评估结论 第 5 项）；同类松散表述亦见 `:47` | **P2** | 把"manifest 均无歧义"要求错标为"§8 第 3 条"。r7 §8 第 3 条（`appcontainer-isolation-contract-r7.md:158`）为受保护文件哈希规则；该要求在"精确下一步"第 3 条（同文件:177）。读者按所指位置核查会找不到该条件，反而可能据 §8.1 三项已完成得出"Phase A 可执行"的相反结论 | 改为"r7 §8 第 1 条（§8.1，`r7:156`）列三项条件，而 r7 '精确下一步' 第 3 条（`r7:177`）另要求 Phase A manifest 无歧义"；`:47` 的"§8.1 与 §8"同步改为"§8.1 与精确下一步第 3 条" |
| **RV2-P2-02** | memo r2:47（§下一准入与停止条件 第 2 段） | **P2** | 将"下一候选必须证明：可验证主进程及**全部后代身份**、**scratch 允许写入**、**TEMP/cache 重定向**、**运行前后受保护文件 hash 一致**"与 Phase A 准入并置且不加阶段限定。上述四项均属 contract §8 第 6 条 Build Gate 条件；而 r3:32 与 contract §1.2 明定 Phase A 不检查子进程、不写入、不哈希文件，r3:20 亦声明 Phase A 环境读取"不构成 cache 重定向或写入闭包证据"。该句可被误读为要求下一 Phase A 候选纳入 Build Gate 级证据，构成范围扩张 | 拆为两段：Phase A 准入=统一唯一前置清单 + 冻结工具/版本/API/路径/字段/mask/失败闭包/stdout 边界；明确"Phase A 不做子进程检查、不写入、不做文件 hash"；进程树身份、写入闭包、TEMP/cache 回读、受保护文件前后 hash 归入"Phase B/Build Gate 先另行冻结与 Review" |
| **RV2-P3-01** | memo r2:15（第 2 项） | P3 | "采纳……两个目录标为 UNKNOWN / BLOCKED"未限定落地位置。r3 原文并未修改（r3:27-28 仍把两条 `%ProgramData%` 目录列为 Phase A T0/T1 目标，r7/r3 字节 pin 仍有效），易被读成 r3 已按 fallback 修订 | 补"该 fallback 只可在下一候选 manifest 中落地；r3 原文与 pin 不变，执行仍禁用" |
| **RV2-P3-02** | memo r2:8（固定依据行） | P3 | Task pin 无字节数、无修订范围，且为 r1 派发快照（`AB0635…`），与本轮 Task 记录 `A35CB3A7…`（`doc/tasks/P02.md:431`）不同；授权依据段落（`PROJECT_ORCHESTRATION_AUTHORIZATION`）未被行号锚定 | 补字节数与锚定段落（如 `doc/tasks/P02.md:68-70`），或注明"本 memo 依据的 Task 快照为 `AB0635…`，其后 Task 已前进，引用时须以派发 SHA 为准" |
| **RV2-P3-03** | memo r2:14-18、:19 | P3 | 全篇未交代 EA-01 的性质（`codex-appcontainer-contract-r7-adjudication.md:40`：Codex execution-readiness finding，非 DSH finding、非测试失败），也未在阻塞段交代 r7 DSH 对 contract r7/r3 的内容结论为 `APPROVED`（0/0/0/5）。读者可能误以为 r3 不可执行系 DSH r7 的发现 | 在第 1 项加一句："EA-01 为 Codex 执行就绪 finding，非 DSH r7 finding、非测试失败；DSH r7 内容 `APPROVED` 不覆盖 EA-01" |
| **RV2-P3-04** | memo r2:19（引用行） | P3 | 断言"不在 Microsoft 列出的 `FILE_INFO_BY_HANDLE_CLASS` 中"，但仅链接函数页；权威成员表在枚举页 | 补引 `FILE_INFO_BY_HANDLE_CLASS` 枚举页（见 §4 第 4 问） |

**非 finding 观察（可不改）**：① memo r2:9 的"非作者内容 Review：DSH APPROVED_WITH_CONDITIONS……"未显式限定为"r1 memo 的 Review"（:3 与 :10 已可消歧，建议加限定词）；② memo r2:3 的状态行未区分"文档自身状态"与被评估对象的 Gate 状态；③ memo r2:27 未复述 2026-10-10"本机验证替代 Windows Sandbox"的用户裁决（`doc/tasks/P02.md:60-62`、:380-386），仅以"不访问 Sandbox"体现合规。

---

## 4. 对 Review 问题的逐条回答

**Q1. 是否准确关闭 RV-P2-01..04、RV-P3-01..05、RV-N-01..03？**
RV-P2-01、RV-P2-03、RV-P2-04、RV-P3-01..05、RV-N-01、RV-N-03 = **closed**；RV-P2-02 = **partial**（RV2-P2-01）；RV-N-02 = **partial**（RV2-P3-02）；无 open。

**Q2. 是否区分 DSH 批准条件与 Codex adjudication；r1 `object_binding=NOT_VERIFIED` 是否未被抹去或升级？**
是。memo r2:9 分别记录 DSH 内容结论与 Codex 的独立字节复算，并明确"不替代 DSH 对象绑定结论"；memo r2:10 记录 `object binding=待新 Review`、不声称 Git commit 或 exact-head pin。`:3` 与 `:10` 表明 r1 条件批准不被继承。**r1 Review 的 `object_binding=NOT_VERIFIED` 在 memo r2 中未被抹去、未被升级**（本轮 Review 亦维持该状态，见 §5）。

**Q3. 11 个 Gate token 是否齐全并与 Task/contract 当前记录一致？状态表达是否清楚？**
齐全且一致。核对（文本比对，非 hash 复核）：

| # | memo r2:31-41 | `doc/tasks/P02.md:425` | `appcontainer-isolation-contract-r7.md:8` |
|---|---|---|---|
| 1 | Phase A=BLOCKED / NOT_RUN | 同 | （contract 未单列该 token） |
| 2 | private_registry_absence=UNPROVABLE / BLOCKED | 同 | 同 |
| 3 | profile=NOT_CREATED | 同 | 同 |
| 4 | ACL/registry=NOT_MODIFIED | 同 | 同 |
| 5 | scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED | 同 | 同 |
| 6 | OS isolation preflight=NOT_RUN | 同 | 同 |
| 7 | hook/cache/child-process closure=BLOCKED / NOT_VERIFIED | 同 | 同 |
| 8 | Build Gate=BLOCKED | 同 | 同 |
| 9 | build=NOT_AUTHORIZED / NOT_RUN | 同 | 同 |
| 10 | Hard Build Barrier=EFFECTIVE | 同 | 同 |
| 11 | AC1–AC7=BLOCKED / NOT_RUN | 同 | 同 |

`Phase A=BLOCKED / NOT_RUN`、`private_registry_absence=UNPROVABLE / BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN` 均显式、无歧义表达；无一处被写成可测量或可构建。

**Q4. r7 §8.1 与"无歧义"要求冲突、两条 WER 目录 fallback、private registry 不可证明、完整子进程与写入闭包未知：来源是否准确、有无过度断言？**
- 冲突实体成立：r7 §8 第 1 条（:156）三项条件确实只要求 Review + adjudication + 逐文件 SHA/object pin，且按 r7 adjudication:20 均已完成；而 r7:177 另加"Phase A manifest 均无歧义"。memo r2 对该冲突的实体陈述准确、来源正确（仅位置标签错，RV2-P2-01），且明确"不用 memo 覆盖 contract"。
- WER fallback：与 r7 adjudication:52（"either resolve…or mark it `UNKNOWN / BLOCKED`"）及 r3:20/26-28 相符；"不读第 24 个变量、不猜映射"为保守处置，无过度断言。
- private registry：与 contract:28（§1.1.1）、:54、r3:32 一致；未猜 key/view、未调用可能初始化 storage 的 API。
- 子进程/写入闭包：memo r2:16、:23 表述为"现有候选材料不构成 Gate 证据""这些机制……不构成 Gate 证据"，并明确"不声称 Windows 一般不存在可行机制"，属证据不足而非不可能性断言，措辞克制。
- 轻微过度概括提示："manifest r3 没有冻结……启动顺序"（`:14`）：r3:22 已冻结 T0/T1 读取次序，未冻结的是 bootstrap/解析时序，建议写成"bootstrap/路径解析时序"。

**Q5. `FileHardLinkInfo` 是否归入 Phase B/Build Gate、未称 Phase A 调用；有无 Microsoft 一手来源？**
是。memo r2:19 明确限定 Phase B/Build Gate 候选缺陷，并声明 Phase A 不打开文件、不据此新增操作。本轮我直接读取 Microsoft `FILE_INFO_BY_HANDLE_CLASS` 枚举页（HTTP 200，[枚举页](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class)），成员表为 `FileBasicInfo … FileNormalizedNameInfo, MaximumFileInfoByHandleClass`，**不含 `FileHardLinkInfo`**，且含 `FileStandardInfo`、`FileStreamInfo`；与该断言一致，来源成立（该网页为外部不可信数据，仅作文档语义证据）。建议补引该枚举页（RV2-P3-04）。

**Q6. 是否遵循 Task 数据保护范围、精确路径、不扩展 T1、不新增变量、不提权、不触碰 profile/ACL/registry/label、不使用 Windows Sandbox？**
是。memo r2:15（不读第 24 个变量、不猜映射）、:25（不采用 ntdll `NtOpenFile`，须另立契约）、:27（不扩展 T1 到额外 16 个根、不读取受保护文件内容或 hash、不扫描子项、不访问用户漫画库/数据库/Lock/current/pinned Revision/凭据/生产数据、不创建 profile、不改 ACL/registry/label、不运行 probe/测试/Cargo/build、不访问 Windows Sandbox）、:43、:49（提权/驱动/安装工具/扩大可写路径/改验收标准均须停止并交用户决定）逐条与 contract r7:18/:114-118、r3:32/:34 及 `doc/tasks/P02.md:60-62` 一致。除 RV2-P2-02 的"阶段未限定"外，无范围扩张陈述。

**Q7. 是否仍有实质遗漏、内部矛盾、错误状态或可能被误读为可测量/可构建？**
- 无错误 Gate 状态；无"可测量/可构建"的正面陈述（`:43`、`:49` 明确相反）。
- 实质缺陷即 §3 的 2 项 P2（锚点错标、阶段混同），其中 RV2-P2-02 属"可能被误读为扩大 Phase A"的内部不一致。
- 其余为 4 项 P3 可读性/引用缺陷，不改变任何结论。

---

## 5. 可验证性与 object_binding

- **本轮未运行 shell、Git、hash 命令、Windows API、ETW、process observer、profile/ACL/registry/label 操作、测试、Cargo、build 或 Windows Sandbox**；故**无法独立复算任何 SHA-256、字节数或 Git 状态**。
- **`object_binding = NOT_VERIFIED`**；正式总体结论 = `NOT_VERIFIED`。本 Review 的任何内容结论**不得**被表述为 exact-hash / object-bound Review。
- 可独立复核部分：5 份输入 + Task/plan 相关文件的正文与行号（只读读取）、只读文本检索，以及 Microsoft Learn 枚举页语义。
- 固定输入 SHA 与 Task 记录的一致性仅为**文本比对观察**（Task:431 记录 memo r2=`140DA099…`、r1 adjudication=`83EFF63D…`、派发 Task=`A35CB3A7…`），不构成 hash 复核。memo r2:10 的 `Get-FileHash 复算一致` 是 memo 作者的自述动作，本 Review 未复算、也未升级。

---

## 6. 适用范围与 Gate 限制

- 本 Review 是**文本/设计就绪度 Review**，**不是** OS preflight、**不是**测试结果、**不是**实施许可、**不产生任何 Gate PASS**。
- **不授权 Phase A**、**不解除 Build Gate**、**不解除 Hard Build Barrier**、**不放行 build 或 AC1–AC7**；即使内容结论为 APPROVED_WITH_CONDITIONS，Gate 状态仍为 memo r2 所列 11 项（Phase A=`BLOCKED / NOT_RUN`；private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；OS isolation preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`）。
- memo r2 的 r1 条件批准不被继承；本 Review 的 2 项 P2 未闭合前，memo r2 **不得**作为下一候选契约/清单的事实源，也不得被引为 r7 §8/§8.1 冲突位置的权威出处。
- 本 Review 不改变 contract r7、manifest r3、memo r1、r1 adjudication 的任何字节与 pin。

---

## 7. 推荐下一步

**唯一可执行项（给 Codex，Lead / Integrator）**：在本轮不触碰任何执行路径的前提下，仅修订 `verification/P02/codex-phase-a-method-blockers-20261010-r2.md` 文本以闭合 RV2-P2-01（`r7:177` 锚点）与 RV2-P2-02（`:47` 阶段拆分并声明 Phase A 不检查子进程/不写入/不哈希文件），顺带处理 RV2-P3-01..04；修订后重新固定 memo SHA 并派发新的非作者只读 Review。在该新 Review 与 Codex adjudication 完成前，不得执行任何 Phase A 读取、不得创建 profile、不得改 ACL/registry/label、不得进入 Build。

明确限制：本 Review 不构成实施许可；如上任一条件无法在现授权内闭合，保持 `BLOCKED`，不得提权、安装工具、扩大可写路径或修改验收标准。
