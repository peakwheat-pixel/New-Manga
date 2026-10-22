# P02PRE-R0S2 独立 Review（非作者 Reviewer：DeepSeek Harness）

## 0. Metadata

| 字段 | 值 |
|---|---|
| Review ID | `P02PRE-R0S2-REVIEW-20261011-DSH-01` |
| Task | `P02PRE-R0S2`（`doc/tasks/P02PRE-R0S2.md`，`status: in_review`，`approval: user_authorized_p02pre_read_only_20261011`） |
| Owner / Author | Codex `/root`（未参与本 Review） |
| Reviewer | DeepSeek Harness（非作者；未编写本 Task / manifest / runner / 任何 R0·R0S1·R6 对象） |
| Integrator / Adjudicator | Codex `/root`（本 Review 不代替其裁决） |
| Repo / branch | `G:/CODEX/New Manga` / `main` |
| Reviewed base/head（按派发采用，未独立核验） | `cddff58469b56e181019a8ddfeade80684bc7eb9`；tree 声明 `c25d051a4b9a0bd9773b50170e100f575ea19f2b` |
| 审查方式 | 纯只读文档审查（`read`）：9 个固定输入全文/大段读取；未运行任何命令、manifest 代码、OS/API/registry/WER/path/environment/token/ACL 查询，未修改任何文件 |
| **Review 决策** | **`NOT_SAFE_FOR_R0`**（本候选方法不得执行；P1 未解决） |
| Finding 计数 | **P0=0；P1=1；P2=3；P3=5** |
| Gate 效力 | **无**。不授权执行、不放行 P02PRE / Technical Gate / Build Gate / Hard Build Barrier / AC1–AC7，不改变 owner waiver |

> **重要限定**：即使本 Review 认为静态文本自洽，也**不代表执行已获授权**。只有 Codex 的独立 adjudication 才能决定是否将 Task 转为可执行；而在 P1 未解决前，按 Task L50/L51 与 manifest L88，**不得转 `ready`、不得建议执行**。

---

## 1. 范围与限制

**审查范围**：固定 9 个输入（Task、R0S2 manifest、R0S1 Review、R0S1 adjudication、R0 manifest、R0 evidence、P02M9 研究、R6 manifest、R6 adjudication）的文本一致性、冻结 runner 的逐 API/参数/异常/null/句柄语义、执行边界与启动副作用、停止逻辑与输出完整性、pin/waiver/Gate 表述、剩余条件分类。

**本 Review 未执行（NOT_RUN）**：任何 shell 启动、capture、manifest 代码、OS/API/registry/WER/token/profile/path/environment/ACL 查询；未运行 git/hash；未访问外部网页；未启动子进程；**未创建或修改任何文件**。

**能力与绑定限制**：

- 未复算任何 bytes/SHA-256、未独立核验 HEAD/tree/工作树；base/head 按派发采用，绑定强度等于派发声明。
- 派发与 9 个输入**均未提供** Task/manifest/runner 自身的 bytes/SHA pin（见 RP-02），故 Task AC L63 要求的“固定 Task/manifest SHA”在本轮**无法满足**。
- R0 evidence 只读至 L553（含 L1–L30 关键行与 L251–L268 分类表），其后的机器可读 JSON 尾部未逐行阅读；未影响本 Review 的判定。
- 未取得独立时间源，故不记录“当前时间”；未取得 stderr。

---

## 2. 逐项审查结论（对应 5 项重点）

### 2.1 授权范围 / R6 旧候选字符串 / waiver 与 Gate 效力 —— **无扩权（满足）**

| 检查 | 结论 |
|---|---|
| 授权来源归属 | Task L21 把授权明确归于“用户 2026-10-11 批准启动 P02PRE 的受控只读取证阶段”，对象选择归于“静态顾问指出”。**未把 R6 旧候选字符串当作授权** |
| 与 R6 候选的关系 | manifest L24–26 只取 `HKLM\...\LocalDumps` 一个键；**未使用** R6 的 `HKCU\...\LocalDumps`、`%LOCALAPPDATA%\CrashDumps`、`ReportQueue`/`ReportArchive` 历史字符串。与 R6 L66“此处字符串……不是本轮读取许可”一致 |
| 是否扩大为 waiver / Gate PASS | Task L21、L23、L66；manifest L7、L9、L94 均逐字声明“不是新风险豁免，也不代表 Gate PASS”“不解除 P02PRE/Create/Build Gate/Hard Build Barrier” |
| 风险原值一致性 | Task L23 = manifest L9 = R6 L14/L16 = R6 adjudication L19–24 = R0 manifest L13 = R0 evidence L14 = R0S1 adjudication L47：`private_registry_absence=UNPROVABLE`；`NOT_SATISFIED`；`APPROVED`；`WAIVED_BY_OWNER`；`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk` —— **逐字一致** |
| 副作用范围 | Task L48/L51–L59 与 manifest L26/L32/L92 的禁止项一致；body 不含任何写操作。**但“无副作用”的证明边界不成立**，见 RP-01 |

### 2.2 Registry API 逐调用 / 参数 / 权限 / 异常 / null / Dispose —— **静态合规（满足核心要求）**

| 检查 | 结论 |
|---|---|
| 逐调用 | body 对 `[Registry32, Registry64]` 顺序各一次：`OpenBaseKey(LocalMachine, view)` → `OpenSubKey(exactSubkey, $false)`；**与 Task L39–L40、manifest L24–L25 一致** |
| 参数 | `[Microsoft.Win32.RegistryHive]::LocalMachine`、`[Microsoft.Win32.RegistryView]::Registry32/Registry64`、`writable=$false`、subkey 字面量与 Task/manifest **逐字一致** |
| 权限 | `writable=false` 为只读打开；权限被拒 → 异常 → 记录 → `return`，不重试、不 fallback |
| 异常 | `catch` 记录 `ExceptionType` + `HResult` 后 `return`，**第一个 view 出错则不执行第二个**；无 retry 循环 |
| null | `$null -eq $targetKey` → `RETURNED_NULL`；manifest L86 明确“不得仅凭 null 断言不存在”“真实物理 key absence……仍=`UNPROVABLE`”。**未把 null 当 absence PASS**（标签风险另见 RP-05） |
| 未读 value/subkey/其他对象 | 无 `GetValue*`/`GetSubKeyNames`/`GetValueNames`/`GetSubKeyCount`/`ValueCount`/`GetAccessControl`；未枚举、未访问 HKCU/per-image/目录/dump |
| 句柄 Dispose | `targetKey` 与 `baseKey` 均在 `finally` 中 `Dispose()`；不输出句柄值 |
| 视图语义限制 | manifest L86 与 Task L42 明确“不得声称两个 view 指向不同物理 key”“不得由此断定 WER reader 使用哪个 view”，与 P02M9 §2 边界一致 |

### 2.3 PowerShell 启动 / profile / module / 精确执行边界 —— **不能证明无状态修改 ⇒ `NOT_SAFE_FOR_R0`（RP-01）**

| 检查 | 结论 |
|---|---|
| `login=false` 语义 | manifest L18 与 Task L50 均承认“`login=false` 不作为 `-NoProfile` 的证明”。**规范要求：不得以“预计没有 profile”放行**；manifest L88、Task L50 均自带 `NOT_SAFE_FOR_R0` 兜底 |
| 冻结输入能否证明启动无副作用 | **不能**。全部输入一致记录 shell startup/profile effects=`UNPROVABLE`（R0S1 evidence L28、R0S1 adjudication L17）。候选**未**冻结 `-NoProfile`/`-NonInteractive`/`-NoLogo`，**未**冻结完整 argv，**未**证明 ModuleAnalysisCache / PSReadLine history / profile 脚本不会写入 |
| 实际解释器身份 | R0S1 F-06 已记录 `shell="powershell.exe"` 是名义 selector，实际疑似 `pwsh` 7；本候选沿用同一 selector，**既未固定实际 executable，也未固定其 profile 位置**，启动行为更不可证 |
| host tool 自身行为 | manifest L32 声称“不写临时文件，不调用 module/provider/external executable，不启动子进程，不写任何状态”——这是**强于可证范围**的断言：`functions.exec_command` 的 wrapper/日志/临时文件行为未在本候选内冻结 |
| 结论 | 按 Task L50/L51 与 manifest L88 的强制规则：**整个候选 = `NOT_SAFE_FOR_R0`，不得执行，不得建议执行** |

### 2.4 身份失败 / 视图异常停止逻辑、输出完整性、两 view 限制

| 检查 | 结论 |
|---|---|
| 身份前置 | `GetCurrent($false)`/`GetCurrent($true)`、Name/SID/authenticated/thread identity 核验在任何 registry 调用**之前**；失败 → `STOP_IDENTITY_...` → 顶层 `return`，**registry 代码不可达** |
| 身份期望值 | `HOME-MY\49745` + `S-1-5-21-...-1001` 与 R6 L49 固定身份、R0 evidence L22 **一致** |
| 视图异常停止 | catch → STOP → `return`，第二个 view 不运行；与 manifest L85 一致 |
| 停止语义依赖 | STOP 依赖 PowerShell `return` 退出当前 scope 的语义；body 中 `return` 位于顶层/`foreach` 内，均可提前退出脚本。**未发现 body 内停止逻辑缺陷** |
| 输出完整性 | 有 PID、identity 字段、每 view `StartUtc`、`State`、异常 `ExceptionType/HResult`、`COMPLETE EndUtc`。**但每 view 缺“查询结束 UTC”**（RP-03），且**未定义 stderr 缺失的归类**（RP-06） |
| 两 view 限制 | 已正确编码“不得推断不同物理对象 / WER 实际 reader / effective policy / destination / T0” |

### 2.5 pin 与用户 waiver 各状态 —— **文本一致，但绑定不足**

| 检查 | 结论 |
|---|---|
| base/head/tree | Task L29 = manifest L8 = R0/R0S1/R6 全部 `cddff584...`；tree `c25d051a...`。**文本一致**（未独立核验） |
| waiver 五值 + 固定原文 | 全链逐字一致（见 2.1） |
| Task/manifest/runner 自 SHA | **均缺失**；`cmd` 与 manifest fenced body 的字节一致性无绑定（沿用 R0S1 F-05 同类缺口）→ **RP-02** |
| Task AC 状态 | Task L63–L66 全部 `- [ ]`，与 `in_review` 一致；L63 的“固定 Task/manifest SHA”本轮不可满足 |

---

## 3. Findings

**P0 = 0；P1 = 1；P2 = 3；P3 = 5。**

| ID | 级别 | 对象 / 证据 | 影响 | 建议（最小修正） |
|---|---|---|---|---|
| **RP-01** | **P1（阻断）** | Task L48/L50/L51；manifest L18/L32/L88；body L34–79；R0S1 evidence L28；R0S1 adjudication L17；R0S1 Review F-06 | PowerShell 启动/profile/module-analysis/host tool wrapper 的副作用**无法证明**；`login=false ≠ -NoProfile`；完整 argv 与实际 executable 未冻结；manifest L32“不写临时文件/不启动子进程/不写任何状态”**强于可证范围**。按 Task L50/L51 与 manifest L88，本候选方法整体不满足 R0 只读安全要求 | **判 `NOT_SAFE_FOR_R0`，禁止执行与派发 capture。** 若要推进，必须另建 Task、重新冻结一个可证明启动无副作用的 runner（并取得新的用户授权与 Codex 范围冻结），且需提供 ModuleAnalysisCache/PSReadLine history/profile/临时文件的可审查“不写”证据；**不得**靠“预计没有 profile”放行 |
| **RP-02** | **P2** | Task L63；manifest 全文；body 无 bytes/SHA | Task/manifest/runner 均无自身 bytes/SHA pin，派发亦未提供；Task AC L63“固定 Task/manifest SHA”**无法满足**；实际 `cmd` 与 fenced body 的字节一致性无独立绑定（R0S1 F-05 未修） | 由 Codex 在 pre-query checkpoint / dispatch log 登记 Task/manifest/`cmd` 的实际 bytes + SHA-256；Reviewer 被禁止运行 hash/path 查询时，应在 Review 中记为 `NOT_VERIFIED` 并由 Owner 补 pin |
| **RP-03** | **P2** | Task L42 要求逐查询记录“查询开始/**结束** UTC”；manifest L86 将 “query/start/end time 缺失”列为 `UNPROVABLE`；body L61/L68/L79 | body 只输出每 view `StartUtc` 与一个全局 `COMPLETE EndUtc`，**没有每 view 的查询结束 UTC**；届时“查询结束 UTC”字段不可满足，可能被判输出不完整 | 在每条 `QUERY` 行增加每 view `EndUtc`（`OpenSubKey` 返回后立即取），或在 manifest 明示“结束 UTC 指整个 capture 的 COMPLETE 时点”以消除歧义 |
| **RP-04** | **P2** | Task L44、manifest L25/L86；body L58–59 | host OS 架构与 view 可用性未在候选内固定；`RegistryView.Registry64` 在不支持的平台上**抛异常还是静默回退到默认视图**未由冻结来源固定。若静默回退，`Registry64` 标签可能名不副实 | manifest 固定 host 架构（或写明核验方式），并声明 view 不受支持时按 `ERROR`/`UNPROVABLE` 停止；明确两个 view 的相同结果**既不证明同一、也不证明不同**物理对象（现有禁令保留） |
| **RP-05** | **P3** | manifest L86；Task L44/L65；body L67 | `RETURNED_NULL` 与 `OPENED_READ_ONLY` 同归 `PASS_WITH_EVIDENCE`，虽已声明 absence 仍 `UNPROVABLE`，但标签易被后续分类表读成“键已观测确认” | 加双列/脚注：“观察完整性=`PASS_WITH_EVIDENCE`；谓词（存在/缺失）=`UNPROVABLE`”，并注明 null/error 语义未消歧 |
| **RP-06** | **P3** | manifest L87；body | 输出完整性判定只列 PID / start / end / stdout，**未覆盖 stderr**；profile/startup 错误与主机警告可能只出现在 stderr 而不被捕获 | 将“stderr 不可得或非空”显式列为 `UNPROVABLE` 条件（沿用 R0S1 evidence L16 的如实披露方式） |
| **RP-07** | **P3** | body L44/L51；R0S1 evidence L22 | 线程 impersonation 判定依赖 `GetCurrent($true)` 未在冻结来源中固定的 null 语义（虽有 R0 `threadIdentityPresent=false` 经验旁证）；若语义相反，runner 将**恒 STOP**（安全但不可用） | manifest 注明该 null 语义来源，或改为显式比较 process/thread SID，避免依赖隐含语义 |
| **RP-08** | **P3** | Task `depends_on`；R0S1 adjudication L23–24/L38 | 未显式说明 R0S1 的两个 `NOT_SAFE_FOR_R0` 停止项（module trust 前置、`Get-ChildItem` direct-child inventory）**如何映射到本候选**（本候选不使用这些 cmdlet） | 加一句映射说明，避免读者误以为 R0S1 结论已被本候选解除 |
| **RP-09** | **P3** | Task L21；manifest L7/L24–26；R6 L66 | 授权来源语义正确（用户 2026-10-11 批准），但未**逐字**写明“R6 旧候选字符串不是本候选授权来源” | 在 Task/manifest 加一句显式声明，防止后续轮次据 R6 字符串扩大范围 |

---

## 4. 覆盖与未覆盖

**已覆盖**

- 9 个固定输入的文本一致性、逐 API/参数/异常/null/Dispose、停止逻辑、分类口径、waiver/Gate 表述、base/head/tree 文本一致性。
- 重点 1（授权范围、R6 字符串、waiver/Gate）：**满足，无扩权**。
- 重点 2（Registry getter 逐调用/权限/异常/null/Dispose/未读 value/subkey）：**静态满足**；null 未被当作 absence PASS。
- 重点 4（身份/视图停止、输出完整性、两 view 与 WER reader 限制）：停止逻辑正确；输出完整性有两个缺口（RP-03、RP-06）。

**未覆盖 / 未核验（NOT_VERIFIED / NOT_RUN）**

| # | 项 | 状态 | 原因 |
|---|---|---|---|
| 1 | Task/manifest/R0·R0S1·R6 的 bytes/SHA-256 复算 | `NOT_RUN` | 派发禁止 OS/path/hash 查询；输入亦未提供 pin |
| 2 | HEAD/tree/branch/工作树独立核验 | `NOT_RUN` | 同上 |
| 3 | PowerShell 启动/profile/module/argv 实际副作用 | `UNPROVABLE` | 无独立证据（RP-01） |
| 4 | 实际 executable 身份（powershell.exe vs pwsh） | `NOT_VERIFIED` | 沿用 R0S1 F-06 缺口 |
| 5 | 外部 Microsoft Learn 引用原文 | `NOT_FETCHED` | 保持纯静态、零外部访问；按 manifest 引用采用 |
| 6 | stderr、精确时钟 | `NOT_RUN`（不可得） | 派发与工具未提供 |
| 7 | R0 evidence L554+ JSON 尾部 | 未逐行阅读 | 不影响判定 |

---

## 5. 决策、剩余风险与建议的下一动作

**决策：`NOT_SAFE_FOR_R0`。** 含义：R0S2 冻结候选的**执行边界/启动副作用无法在 R0 只读阶段被安全证明**（RP-01），因此该 runner **不得运行**，不得建立 pre-query checkpoint 执行，不得派发 capture。静态文本层面的授权归属、范围冻结、Registry API 参数、null/absence 口径与 waiver/Gate 表述**基本自洽且无扩权**（P0=0），但不足以放行。

**给 Codex adjudicator 的建议**：

1. 采纳 RP-01：将 R0S2 候选方法标 **`NOT_SAFE_FOR_R0`**，保持 `private_registry_absence=UNPROVABLE`、waiver 五值与固定原文不变，P02PRE=`BLOCKED`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。
2. **不**转 `ready`、**不**创建执行 checkpoint；Task 保持 `in_review` 或转 `blocked`（由 Codex 决定），并记录“Review 未授权执行”。
3. 处置 RP-02/RP-03/RP-04（绑定、输出字段、view 可用性）；RP-05–RP-09 作为文档净化项。
4. 若 Owner 仍要推进只读 WER 观察，必须先有**新的明确用户裁决与范围冻结**，并另建 Task 冻结一个可证明启动零副作用的 runner；在满足前不得复用本候选、不得“放宽检查让它跑通”。
5. 本 Review **不**指定任何可执行 capture 任务；在 Codex adjudication 完成前，Repo 下一动作仅为“Codex 对 R0S2 独立 adjudicate”。

**建议的下一动作（唯一）**：由 `Codex /root` 对 R0S2 执行**独立 adjudication**，核准 RP-01 的 `NOT_SAFE_FOR_R0` 处置与其余 findings，并保持 Build Gate / Hard Build Barrier / AC1–AC7 / owner waiver 原状。

---

## 6. 剩余条件分类（明确 `UNPROVABLE` / `REQUIRES_ACTIVE_TEST` / `NOT_SAFE_FOR_R0`）

| 条件 | 分类 | 依据 |
|---|---|---|
| 本候选 runner 的启动/profile/执行边界 | **`NOT_SAFE_FOR_R0`** | RP-01；Task L50/L51、manifest L88 |
| 两个 view 下 `LocalDumps` 的精确 API 观察（若执行） | 仅“观察值”，且谓词=`UNPROVABLE` | Task L44/L65、manifest L86 |
| 真实物理 key absence | `UNPROVABLE` | null/error 语义未消歧 |
| WER effective view / reader / policy / destination / T0 | `UNPROVABLE`（M9：`wer_view_destination_binding=NOT_RESOLVED / BLOCKED`） | manifest L86、P02M9 §2–4、R6 L66 |
| `private_registry_absence` | `UNPROVABLE`（唯一 owner waiver） | R6 L18、R6 adjudication L26 |
| `profile_folder_no_side_effect` | `UNPROVABLE / BLOCKED` | R6 L57、R6 adjudication L28 |
| `zero_capability_getter_eligibility` / `getter_effective_write_boundary` / `getter_success_failure_no_write` | `NOT_RESOLVED / BLOCKED` | R6 L65 |
| appcontainer profile exact path / pre-create absence | `NOT_SAFE_FOR_R0` | R0 manifest L51、R0 evidence L262 |
| 详细 token / elevation / LPAC capability / 实际子进程 token | `NOT_SAFE_FOR_R0` | R0 evidence L264 |
| 两个 scratch leaf 的 empty-or-absent | `UNPROVABLE` | R0S1 adjudication L36 |
| canary 写边界 / 真实 token write boundary | `REQUIRES_ACTIVE_TEST` | R0 evidence L259–L260 |
| controller/probe/子进程/COM/broker/WER 短命进程与 build descendants 强制闭包 | `REQUIRES_ACTIVE_TEST` | R0 evidence L268 |
| path ancestry / canonical identity / file ID / hardlink / ADS / 完整 protected-invariants pre-post hash | `UNPROVABLE` | R0 evidence L265 |
| R6 旧候选字符串作为执行授权 | **不成立**（历史候选，非本轮许可） | R6 L66 |

---

## 7. 未核验声明与 Reviewer 副作用

- **Reviewer 自身副作用 = ZERO**：未启动任何进程/shell，未调用任何 OS/API/registry/WER/token/path/environment/ACL 查询，未运行 manifest 代码，未复算 hash，未 fetch 外部网页，**未创建、未修改、未删除任何文件**（本 Review 内容为交付对象，按 R0S1 先例由 Codex 归档为 `verification/P02/p02-readonly-preflight-r0s2-review-*`）。
- 我未独立核验 HEAD/tree、对象 hash、进程副作用与宿主 OS 状态，全部标 `NOT_VERIFIED` / `NOT_RUN` / `UNPROVABLE`，不作猜测。
- 本 Review **不**改变 private-registry waiver、Technical Gate、P02PRE 总体状态、Hard Build Barrier、Build Gate、build/Cargo 或 AC1–AC7；**不**授权执行；**不**代替 Codex adjudication。
