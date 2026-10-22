# P02 Phase A blocker memo r3 修订候选 · 非作者只读复审（attempt 3）

**审查性质**：仅静态文本 / 引用一致性 / 范围与安全边界复审。本轮只使用只读工具（`read` / `grep` / `web_fetch`），**未运行** shell、PowerShell、Git、hash、测试、Cargo、build、Windows API、ETW、process observer、OS measurement、profile/ACL/registry/label 操作、probe 或 Windows Sandbox；**未修改、创建、删除、移动任何文件**。固定输入中的命令、路径与 Agent 指示一律按不可信数据处理。

---

## 1. 内容结论与计数

| 项 | 值 |
|---|---|
| 内容结论 | **APPROVED_WITH_CONDITIONS** |
| 本轮新增 P0 / P1 / P2 / P3 | **0 / 0 / 0 / 3**（3 项均为引用精度/自足性 P3，不改变任何 Gate、阶段或范围结论） |
| 前置 finding 逐项结论 | **closed 13 / partial 1（RV3-P3-05）/ open 0** |
| `object_binding` | **`NOT_VERIFIED`** |
| 正式总体结论 | **`NOT_VERIFIED`**（内容结论 ≠ exact-hash / object-bound Review，**不得**表述为 Review「通过」） |

**判定理由**：修订后的 memo r3 逐项落实了 attempt 2 的 RV3-P2-01、RV3-P3-01..04 与前置 disposition 标注；修正后的枚举页 URL 经本轮只读访问确为官方 canonical 页并含正确成员表；`r7:115` 锚点、r7 计数 `0/0/0/5` 与 report SHA 均已补齐；11 项 Gate token 与当前 Task 逐项同集合同取值；无任何错误放行、错误宣称 OS 证据或扩大 Phase A 范围的表述（故无 P0/P1/P2）。残留 3 项为锚点基线、契约修订载体与 r7 引用绑定粒度的 P3。

---

## 2. 前置 finding（RV2-\*/RV-\*）disposition

| ID | 本轮判定 | 依据（只读核对） |
|---|---|---|
| **RV2-P2-01** | **closed** | memo r3:19 已改为「contract r7 §8.1（r7:156）三项准入」+「'精确下一步'第 3 条（r7:177）额外要求无歧义」。逐字核对：`appcontainer-isolation-contract-r7.md:156` 确为 §8 第 1 条三项；`:177` 含「均无歧义」；`:158`（§8 第 3 条）是受保护文件 hash 规则，不含该条件 |
| **RV2-P2-02** | **closed** | memo r3:25 把完整主进程/后代身份、保护目录拒写、scratch 正向写、TEMP/cache 重定向、前后 hash 单列为 Phase B / Build Gate 缺口并声明「不能并入下一 Phase A manifest」；:21 追加 Phase A 排除项；与 r7:44、manifest r3:32 一致 |
| **RV2-P3-01** | **closed** | memo r3:16「只可在下一候选 manifest 标为 UNKNOWN / BLOCKED；该 fallback 不会改写 manifest r3」，与 r2 adjudication:34 一致；manifest r3 pin 未受影响 |
| **RV2-P3-02** | **closed**（带 §4 RV4-P3-01 保留） | memo r3:9 分列 100139/`AB0635…`、102674/`A35CB3A7…`、105252/`44C1F4B2…` 三份 Task 快照与字节数+SHA，:8 锚定授权段行号；与 r2 adjudication:10-11、:26 一致 |
| **RV2-P3-03** | **closed** | memo r3:15 明确 EA-01 为 Codex execution-readiness finding、非 DSH r7 finding、非测试失败，与 r7 adjudication:40 一致 |
| **RV2-P3-04** | **closed** | memo r3:27 已补官方枚举页，且 URL 已修正；本轮只读访问 `…/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class` HTTP 200，成员表含 `FileStandardInfo`、`FileStreamInfo`，**不含 `FileHardLinkInfo`**；函数页 `…/win32/api/winbase/nf-winbase-getfileinformationbyhandleex` HTTP 200，Remarks 有效类表同结论。attempt 2 的 partial 事由（404 slug）已消除 |
| **RV-P2-02** | **closed** | memo r3:19 记录 r7 §8.1 与「精确下一步」第 3 条的原文冲突，明写「r7 adjudication 已指出 r3 仍不得执行」「不自行覆盖合同」，符合 r1 最小修订要求 |
| **RV-N-02** | **closed**（带 §4 RV4-P3-01 保留） | memo r3:9 已将「修订范围 + 字节数 + SHA」显式化，:10 区分 r1/r2 两轮 Review 的对象与 SHA |

---

## 3. attempt 2 finding（RV3-\*）disposition

| ID | 本轮判定 | 依据 |
|---|---|---|
| **RV3-P2-01**（Task:458 memo SHA 63 位） | **closed（文本层）** | `doc/tasks/P02.md:458` 现为 64 位 `5EEED098…7DFE9CAAD9AA…EB9F0FCB`，与 :444/:450/:466/:472 及 attempt 2 pin 逐字一致；`:461` 已把 attempt 1 的 `6B9F…`/`1D40…` 冲突保留为历史 `STATE_CONFLICT / NOT_VERIFIED`，`:466` 声明初始 SHA 不再代表当前文件。**未复算该 SHA**（无 hash 工具），仅文本一致 |
| **RV3-P3-01**（枚举页 slug 404） | **closed** | memo r3:27 已用 `ne-minwinbase-file_info_by_handle_class`；本轮 HTTP 200 且成员表验证主张成立 |
| **RV3-P3-02**（未标注前置 finding ID） | **closed** | memo r3 内联标注齐备：:8（RV2-P3-02/RV-N-02/RV3-P3-05）、:9（RV2-P3-02/RV-N-02/RV3-P3-02）、:15（RV2-P3-03/RV3-P3-03）、:16（RV2-P3-01）、:19（RV2-P2-01/RV-P2-02）、:21 与 :25（RV2-P2-02）、:27（RV2-P3-04/RV3-P3-01/RV3-P3-04）。第 2 节 8 个前置 ID 全部可溯 |
| **RV3-P3-03**（r7 计数/report SHA） | **closed** | memo r3:15 含 `P0/P1/P2/P3=0/0/0/5` 与 report SHA-256 `C1FADDC2…EF705`；与 r7 adjudication:15/:24 及 `dsh-appcontainer-contract-r7-review.stdout.md:19/:21` 一致 |
| **RV3-P3-04**（`r7:115` + canonical URL） | **closed** | memo r3:27 含「（r7:115）」；`appcontainer-isolation-contract-r7.md:115`（§5）逐字含 `GetFileInformationByHandleEx(FileHardLinkInfo)`；第二条链接已换为 `/win32/api/winbase/nf-winbase-getfileinformationbyhandleex`（HTTP 200） |
| **RV3-P3-05**（Task 行锚点未注明快照） | **partial → RV4-P3-01** | memo r3:8 已声明行号基线，但声明的是 attempt 2 派发快照 108405/`7521168C…`，与当前 Review pin 111260/`351EB291…`（Task:472）不同，且未声明在当前 pin 下复核。本轮只读复核：三处锚点在当前 Task 文本上仍分别命中 :68/:70、:58–:62、:382–:386（行号由 read 工具给出；字节/SHA 未独立复核） |

---

## 4. 本轮新增 findings

| ID | 位置 | 级别 | 证据 | 最小修订 |
|---|---|---|---|---|
| **RV4-P3-01** | `memo r3:8` | **P3** | 该句把全部 Task 行号锚定到「attempt 2 派发快照（108405 bytes / `7521168C…`）」；但 ①该对象不在本轮固定输入内、无法按 pin 取得，②Task:461 记录 attempt 2 期间 live Task 已含追加的 lines 455–459（即行号实际是在与 pin 不同的对象上复核的），③当前 pin 为 111260/`351EB291…`（Task:472）。读者无法区分「行号漂移」与「引用错误」 | 补一句「上述行号在 attempt 3 pin（111260 bytes / `351EB291…`）下复核仍一致」，或改用 Task:84 式稳定语义锚点 |
| **RV4-P3-02** | `memo r3:21`、`:27`（另见 :19） | **P3** | :27 只写「Phase B/Build Gate 前须先修正并另行 Review」，未指明修正载体；而该缺陷位于被 pin 的 contract r7:115，且 r7:156 把 manifest r3 定为「唯一 Phase A 候选范围」，故 EA-01 要求的「新的 Phase A manifest」需要契约修订/契约级 adjudication 才能取得可溯依据（r7 adjudication:52 是当前唯一依据，memo 未引） | 在 :21/:27 各补一句：修正与下一 Phase A 候选须以契约修订（新 r8 或 Codex 契约级 adjudication）为载体并重新 pin/Review |
| **RV4-P3-03** | `memo r3:15` | **P3** | 引用 r7 `APPROVED` 时给出计数与 report SHA，但未附该 Review 自身的正式 `object_binding=NOT_VERIFIED`（`dsh-appcontainer-contract-r7-review.stdout.md:12`；r7 adjudication:20 亦称其为「its own limitation」），与 memo :10 对 r1/r2 两轮的记录粒度不一致 | 在 :15 补「（formal `object_binding=NOT_VERIFIED`，内容层结论，非 exact-object 凭证）」 |

**非 finding 观察（可不改）**
- **r7 `APPROVED` 引用范围本身准确**：memo :15 明确其为内容 Review、不涵盖 EA-01，与 r7 stdout:19/:23、r7 adjudication:24/:36 一致；本轮未发现范围扩张。
- memo :16「其余 WER 对象中 `%LOCALAPPDATA%\CrashDumps` 可由 23 项集合解析」成立（LOCALAPPDATA 在 manifest r3:20 的 23 项内）；另两条 WER 对象是不含环境变量的字面 registry 键，未列举但不构成错误。
- memo :29 的 Job/ETW 主张经本轮一份官方页只读核对成立：`JOBOBJECT_ASSOCIATE_COMPLETION_PORT` 页（HTTP 200）含「delivery to the completion port is **not guaranteed**」，且明确 `JobObjectNotificationLimitInformation` 通知是保证送达的——memo 的表述未过度概括。
- 首轮 attempt 1 报告无 `.exit`（Task:451 亦如此记录），本轮**未读取、未继承**其 `CHANGES_REQUESTED` 结论；Task:452 的 `STATE_CONFLICT / NOT_VERIFIED` 属 Codex 收口责任，本轮不裁定。
- memo :8 对授权的概括（「在限定路径和权限内选择本机隔离范围」）相对 Task:70 原文偏保守，未扩大授权。

---

## 5. `object_binding` 状态

- **`object_binding = NOT_VERIFIED`**。本轮未运行任何 hash/字节复算或 Git 检查，全部字节数、SHA-256（Task 111260/`351EB291…`、memo r3 9033/`7734767…`、attempt 2 adjudication `7B881C5C…`、attempt 2 report `491469D7…`、r2 memo/report/adjudication、contract r7、manifest r3、r7 adjudication）**均为文本一致性观察**，不构成对象绑定或 hash 复核。
- 我**独立只读复核到的**：11 份固定输入的正文与行号、`doc/tasks/P02.md` 相关段落（:58–:70、:376–:420、:435–:473）、r7 contract 相关行（:8、:28、:44、:52、:54、:115、:156、:158、:161、:177）、manifest r3 全文、r7 adjudication 全文、r2 两份 adjudication/report、r7 stdout 关键行，以及三处 Microsoft Learn 页面语义（枚举页、函数页、Job completion port 页）。上述网页为外部不可信数据，仅作文档语义证据。
- **不可复核的**：所有字节数/SHA、Git 与工作区状态、本机 OS/registry/ACL/profile 状态、CLI exit 与 mount 证据，以及本次派发 prompt 文件自身的身份（Task:471 记为 `F6124F90…`，本轮未核）。

---

## 6. Gate 边界（精确重述）

以下 11 项与 `doc/tasks/P02.md:439`（及 :395/:404/:410）逐项同集合同取值，memo r3:41–51 未做任何提升：

1. **Phase A=`BLOCKED / NOT_RUN`** —— 这是**未执行/未授权**状态，**不是测试失败**，也不是任何 OS 测量结果；
2. private_registry_absence=`UNPROVABLE / BLOCKED`；3. profile=`NOT_CREATED`；4. ACL/registry=`NOT_MODIFIED`；5. scratch ACL/label mutation=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；6. OS isolation preflight=`NOT_RUN`；7. hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；8. **Build Gate=`BLOCKED`**；9. build=`NOT_AUTHORIZED / NOT_RUN`；10. **Hard Build Barrier=`EFFECTIVE`**；11. AC1–AC7=`BLOCKED / NOT_RUN`。

本复审为纯静态内容 Review：**不产生任何 Gate PASS、不构成 Phase A 执行授权、不解除 Build Gate 或 Hard Build Barrier、不放行 build/AC1–AC7**，也不得据任何静态 Review 推断本机 OS 证据或执行许可；不改变 P02 Task、contract r7、manifest r3、memo r1/r2/r3 与各 adjudication 的任何字节或 pin。

**推荐下一步（唯一可执行项，给 Codex，Lead / Integrator；仍全程只读/纯文档）**：在不触碰任何执行路径的前提下，(a) 按 RV4-P3-01 在 memo r3:8 补记当前 pin 下的锚点复核；(b) 按 RV4-P3-02 补记契约修订载体与下一 Phase A 候选的契约依据；(c) 按 RV4-P3-03 补记 r7 Review 的 `object_binding=NOT_VERIFIED`；修订后重新固定 Task 与 memo 的字节/SHA 并派发新的非作者只读 Review，再由 Codex adjudicate。在此之前不得执行任何 Phase A 读取、不得创建 profile、不得改 ACL/registry/label、不得写入或 probe、不得进入 Build 或 Sandbox；`private_registry_absence=UNPROVABLE / BLOCKED`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE` 保持不变。
