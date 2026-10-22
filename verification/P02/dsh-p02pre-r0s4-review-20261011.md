# P02PRE-R0S4 独立 Review（非作者 Reviewer：DeepSeek Harness）

## 0. Metadata

| 字段 | 值 |
|---|---|
| Review ID | `P02PRE-R0S4-REVIEW-20261011-DSH-01` |
| 受审 Task | `doc/tasks/P02PRE-R0S4.md`（`status: in_review`，`approval: user_authorized_p02pre_controlled_readonly_r0_20261011`） |
| 受审 manifest | `verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md` |
| 受审 Delivery | `verification/P02/codex-p02pre-r0s4-delivery-20261011.md` |
| 安全依据（相关段落） | `verification/P02/p02-readonly-preflight-r0s2-review-20261011.md`、`verification/P02/codex-p02pre-r0s2-adjudication-20261011.md`、`verification/P02/codex-p02pre-r0s3-adjudication-20261011.md`、`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` |
| Owner / Author / Integrator / Adjudicator | Codex `/root`（未参与本 Review） |
| Reviewer | DeepSeek Harness（非作者；未编写本 Task / manifest / delivery / 任何 r6、R0、R0S1、R0S2、R0S3 对象） |
| Repo / branch / 声明基线 | `G:/CODEX/New Manga` / `main` / `cddff58469b56e181019a8ddfeade80684bc7eb9`（tree 声明 `c25d051a4b9a0bd9773b50170e100f575ea19f2b`） |
| 审查方式 | 纯只读文档审查（`read` / `glob` / `grep`）。**未**运行任何 shell、OS/Registry/WER/path/ACL/environment/hash/Git 查询，**未**启动 runner/子进程，**未**执行 Build/Cargo/AC，**未**修改除本文件外的任何对象 |
| **Review 决策** | **`CHANGES_REQUESTED`** |
| Finding 计数 | **P0=0；P1=1；P2=5；P3=6** |
| Gate 效力 | **无**。不授权执行、不放行 P02PRE / Technical Gate / Build Gate / Hard Build Barrier / AC1–AC7，不改变 Owner waiver |

> **核心判断**：本轮的安全处置（`STOP_BEFORE_HOST_QUERY`、零 host 查询、不换 shell、不运行 getter）**方向正确且是 R0S2 RP-01 的必然结果**，未发现任何 P0 级安全缺陷，未发现伪造证据、扩权或 Gate 弱化。要求修订的是**交付与治理完整性**：artifact 级 bytes/SHA pin 缺失（P1）、manifest 自身对“是否执行过命令”的记录前后矛盾（P2）、本轮禁项与 r6 历史候选对象的枚举覆盖不全（P2）、git status 披露与五类表覆盖不完整（P2/P3）。

---

## 1. 审查范围、reviewed paths 与能力限制

### 1.1 Reviewed paths

| # | 路径 | 读取程度 |
|---|---|---|
| 1 | `doc/tasks/P02PRE-R0S4.md` | 全文（78 行） |
| 2 | `verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md` | 全文（49 行） |
| 3 | `verification/P02/codex-p02pre-r0s4-delivery-20261011.md` | 全文（35 行） |
| 4 | `verification/P02/p02-readonly-preflight-r0s2-review-20261011.md` | 全文（177 行） |
| 5 | `verification/P02/codex-p02pre-r0s2-adjudication-20261011.md` | 全文（56 行） |
| 6 | `verification/P02/codex-p02pre-r0s3-adjudication-20261011.md` | 全文（65 行） |
| 7 | `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | 全文（239 行） |
| 8 | `verification/P02/dsh-p02pre-r0s4-review-20261011.prompt.md` | 全文（20 行，作为本派发的桌面对应件读取） |
| 9 | `verification/P02/**` 的 `R0S4` / `index_side_effect` / `普通 git status` 定位命中段 | 条件检索（用于核对历史先例与本轮一致性） |

另以 `glob` 确认：R0S4 相关对象当前仅有 manifest、delivery、prompt 三件；`codex-p02pre-r0s4-adjudication-20261011.md` 与 `codex-checkpoint-p02pre-r0s4-20261011.md` **尚不存在**（见 P3-04）。以 `grep` 确认 `doc/` 下 `R0S4` 仅出现在 Task 自身，`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md` **尚未登记 R0S4**（Task L52 允许治理更新，属集成阶段待办）。

### 1.2 Owner pins 的核对能力与限制（**NOT_VERIFIED**）

| Pin | Owner 声明值 | 本 Reviewer 能力 |
|---|---|---|
| Task | `A8A4B995263541A74CFE9F568E707BD7121105F56C5CC538CDC5ACE5B810604E` | **NOT_VERIFIED**（无法复算） |
| Manifest | `8C57B9B8E7177A22E354280106E7D0FD82310C42778CF0BAEDB773002AD46CAD` | **NOT_VERIFIED**（无法复算） |
| Delivery | `AFED69527714E016361E66D9AFF47AE1CC7A6B1433B1486052316C8157C934F1` | **NOT_VERIFIED**（无法复算） |

限制来源与强度，须如实记录：

- 本派发**明确禁止** OS/path/ACL/environment/hash 查询与 runner 启动，因此 **bytes / SHA-256 / live HEAD / tree 均无法独立复算**。上表三值在本文中一律记 `NOT_VERIFIED`，**不声称已复核**，也**不主张 pin 不匹配**。
- 三个 artifact **自身内部均未登记 bytes/SHA-256**（Task 全文、manifest 全文、delivery 全文均无 pins 段），因此 Owner 提供的 pins 无法与交付物内部记录交叉对账（P1-01）。
- 我读取的是工作区当前字节，**不能证明**它与“Codex 计算 pin 时的那份字节”一致；该绑定只有 Codex adjudication 侧的 dispatch/pre-query pin 才能补齐（沿 R0S2 RP-02、R0S3 adjudication L25 已确立的先例：owner 侧复算、Reviewer 侧记 `NOT_VERIFIED`）。
- 我读取的 `dsh-p02pre-r0s4-review-20261011.prompt.md` 是否与本派发输入逐字一致，同样 **NOT_VERIFIED**（无法证明派发链路字节一致）。
- Reviewer 侧的 digest 随本文件归档时须由 Codex 独立复算并绑定（我无法自算）。

### 1.3 未执行（NOT_RUN）声明

任何 shell/进程启动、`git` 任意子命令（含 `status`/`rev-parse`/`hash-object`）、文件 hash、`.git/index` 读取、OS/Registry/WER/profile/token/ACL/path/TEMP/cache/scratch 查询、外部网页抓取、Build/Cargo/AC —— 全部 `NOT_RUN`。本 Review 唯一的写操作是**创建本文** `verification/P02/dsh-p02pre-r0s4-review-20261011.md`。

---

## 2. 检查重点 1：最新用户授权是否被准确、有限地记录

**结论：准确、有限，且未被冒充为 waiver / Gate PASS。符合要求。**

| 检查项 | 证据 | 判定 |
|---|---|---|
| 授权来源与对象 | Task L22 把授权归于“用户于 2026-10-11 批准重新启动 P02PRE 的受控只读取证阶段”，并限定“只允许有证据证明不会创建、删除或修改系统/项目状态的查询”；manifest L7 同义复述 | 通过 |
| 是否新 waiver / Gate PASS | Task L22「不是新的风险豁免，也不代表 Gate PASS」；manifest L7「此授权不是 waiver，也不是 Gate PASS」；delivery L9 同义 | 通过（明确否定） |
| 授权来源不是历史授权 | 全链**未**把 R6 的旧候选字符串、更早的 NOT_AUTHORIZED/B 类准入裁决或历史 Review 当作本轮授权来源；r6 L18 自身亦声明旧状态只是历史 | 通过（沿 R0S2 RP-09 的方向，本轮表述更明确） |
| 五值风险原值 | Task L22 = manifest L8 = delivery L29，逐字一致：`private_registry_absence=UNPROVABLE`；`Technical Gate=NOT_SATISFIED`；`Owner Risk Acceptance=APPROVED`；`Gate Disposition=WAIVED_BY_OWNER`；`Build Authorization=AUTHORIZED_WITH_EXCEPTION` | 通过 |
| 固定原文 | `technical condition unmet; user explicitly accepted residual risk` 在 Task L22、manifest L8、delivery L29 **逐字（英文原文）保留，未改写、未翻译、未省略分号** | 通过 |
| 与上游证据一致 | 与 r6 L14/L16、R0S2 adjudication L52、R0S3 adjudication L52–L57 完全一致 | 通过 |
| 技术状态与风险接受分列 | Task L69、manifest L9、delivery L29/L33 均把 `private_registry_absence=UNPROVABLE` 与 Owner 风险接受分列，未以风险接受冒充技术 PASS | 通过 |
| 未改变的安全状态 | `P02PRE=BLOCKED`；`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；`Build Gate=BLOCKED`；`Hard Build Barrier=EFFECTIVE`；`build/Cargo=NOT_RUN`；`AC1–AC7=BLOCKED / NOT_RUN`：Task L69、manifest L9、delivery L33 三者一致 | 通过 |
| Windows Sandbox | Task L60/L70 禁止；manifest L43、delivery L33 记录未查询/未安装/未启用/未启动 | 通过 |

**未覆盖风险**：「最新用户授权」的**原始裁决文本本身**不在受审对象内，本轮只能核对二次记录的一致性；若存在更新的用户裁决，本 Reviewer 无权从聊天或其他用户授权中引入（派发 L8 明令禁止），故记为范围外风险而非 finding。

---

## 3. 检查重点 2：只读范围是否精确限于 r6 已列对象

**结论：边界方向正确（只收窄、不扩张），但对象枚举覆盖不全，且本轮禁项清单有遗漏。**

### 3.1 收窄性判定（通过项）

- manifest L13 把读取根限定为“r6 已列出的精确对象和已存在 R0 evidence 中的精确对象”，并显式禁止“增加路径、祖先、registry key/view/value、WER policy 字段、环境变量、文件清单或递归范围”，禁止 reparse/alias 跟随与文件内容读取；与 r6 L13/L15/L70/L87/L137 的边界一致。
- Task L51 的禁止读取集（用户漫画、数据库、Lock、current/pinned Revision、凭据、模型、dump 内容）在 manifest 中保持（L30 明确“不读 host profile/config/credentials”、L31“不扩展为全量 Git/用户数据 inventory”、L35 明确“不猜 SID 路径”、L44“子进程不写临时文件”）；但该禁止集**未在 manifest 中以完整清单形式逐字复述**，属 P2-04/P2-03 的同一覆盖问题，不构成扩权。
- Task L50 允许的细粒度对象（user/SID/token 观察、精确路径 existence/metadata、只读 ACL getter、TEMP/cache/scratch/protected path 解析、已有保护文件集合 hash、WER/T0 只读状态）**在 manifest 中全部落到 `NOT_RUN`**，未被当作既成许可使用；Task L67 又把执行前置条件绑定到 R0S2 RP-01，方向正确。
- 未发现把 candidate / 方法审查写成实际查询：manifest L42「P02PRE host query 命令：NONE；目标 OS/API/Registry/WER/path/ACL/TEMP/cache/scratch/hash capture：NOT_RUN」、delivery L15 首句，均明确本轮**零**目标机查询；manifest L38 `FAILED=∅` 与此自洽（就该句而言）。

### 3.2 覆盖缺口（P2-03 / P3-02）

manifest 的“条件分类与候选查询处置”表（L25–L39）**没有为 r6 已列出的若干精确对象单列行**：

| r6 已列对象 | 来源 | R0S4 manifest 是否单列 | 影响 |
|---|---|---|---|
| `HKCU\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps` | r6 L66（保留为“历史额外观察候选”） | **否** | 该键的法律地位（观察候选 ≠ 读取许可）未在本轮 manifest 复述 |
| `%LOCALAPPDATA%\CrashDumps` | r6 L66 | **否** | 同上 |
| `C:\ProgramData\Microsoft\Windows\WER\ReportQueue` | r6 L66 | **否** | 同上 |
| `C:\ProgramData\Microsoft\Windows\WER\ReportArchive` | r6 L66 | **否** | 同上 |
| r6 L72–L85 的 12 个只读输入根 | r6 L68–L85 | 仅以“只读输入根”隐含（manifest L13） | 12 根的具体清单/traceability 未在本轮登记 |
| 唯一正向 canary 叶、负向 deny-control 叶 | r6 L141–L145 | 仅覆盖“两个 scratch output leaf empty-or-absent”（L34） | 3 个 canary 对象的独立处置未列 |

R0S3 adjudication L44 的 `NOT_SAFE_FOR_R0` 方法清单同样包含“未冻结的 WER/path/dynamic-inventory helpers”，说明这些对象属于此前已被承认的待处置集合；本轮 manifest 未把它们逐项落表，属于**枚举不完整**（对象边界不可逐条对账），不构成扩权。

### 3.3 明确禁止项遗漏（P2-05）

Task L55–L62 列出 7 条禁止项。manifest L43 只枚举了：`CreateAppContainerProfile/DeleteAppContainerProfile`、Registry write、ACL change、profile create/delete、Windows feature/Sandbox query/change、Build/Cargo、AC1–AC7。**未在 manifest 中显式出现**的 Task 禁项包括：

- “任何尚未证明无副作用的 API、getter、shell、module、provider、external executable、子进程、runner、wrapper 或后台缓存/历史路径”（Task L59）——manifest L44 有等价表述（不创建脚本、不调用 external executable、不启动子进程、不写临时文件），基本等价但未逐字覆盖 “provider/module/wrapper/后台缓存/历史路径”；
- “权限提升、服务/驱动/ETW、网络、编译/JIT”（Task L61）——manifest 全文**未见** `网络`、`编译/JIT`、`服务/驱动/ETW`、`权限提升` 的禁止性枚举；
- “超出 r6 exact path/key/read allowlist 的访问，以及访问用户漫画/数据库/Lock/current或pinned Revision/凭据/模型/dump 内容”（Task L62）——manifest L13 覆盖，L43 未复述。

由于本轮实际零执行，遗漏**未产生实际后果**；但 manifest 是本轮范围冻结的正式载体，禁项清单不完整会削弱后续轮次的范围约束力。

---

## 4. 检查重点 3：R0S2 RP-01 是否足以要求 STOP_BEFORE_HOST_QUERY

**结论：足以，且本轮处置正确。未换 shell、未运行 getter。**

- R0S2 Review RP-01（P1，阻断）的实质：`login=false ≠ -NoProfile`、完整 argv 与实际 executable 未冻结、profile/ModuleAnalysisCache/PSReadLine history/临时文件与 `functions.exec_command` wrapper 的副作用无证；R0S2 候选整体判 `NOT_SAFE_FOR_R0`。R0S2 adjudication L15/L23 `ACCEPT / STOP`。
- Task L67 把该结论写成本轮硬前置：「除非本 Task 对精确 runner 取得新的安全证据并经非作者 Review、Codex adjudication，否则禁止任何 host/registry/path/hash query」；manifest L19–L21 据此冻结 `STOP_BEFORE_HOST_QUERY`，并显式写出「改变 shell/runtime、直接调用子进程或假定 login=false 代表 NoProfile 都不构成安全证明」。
- 与 Task L24「若查询或启动环境是否无副作用不确定，不执行该项……并继续其他能安全完成的工作」一致：安全不确定 ⇒ 不执行。
- 未发现换 shell / 换 runtime / `-NoProfile` 替代 Review / 直接调用子进程 / 运行 `OpenBaseKey`、`OpenSubKey`、`GetAppContainerFolderPath`、`GetAppContainerRegistryLocation`、`GetCurrent` 等 getter 的任何记录；manifest L42–L44、delivery L15 均记零执行。R0S3 adjudication L46「不切换 shell/runtime 重试」的先例被正确延续。

**同时如实记录的可靠性限制（P3-05）**：「本轮未运行任何 host 查询 / 未启动子进程」本身是 Owner 的**自我报告**。在本派发禁止一切 OS/进程/命令核验的前提下，Reviewer **无法独立验证**该声明为真——任何试图验证它的动作恰好就是被禁止的查询。这一限制应写入 Codex adjudication，不得把“文本自洽 + 无相反证据”读成“已证明零查询”。

**可安全的静态分类是否确实继续完成（是，但有覆盖缺口）**：manifest L25–L39 与 delivery L21–L27 均在不接触主机的前提下完成了“条件 × 方法”分列与五类归入，且未以零执行推导出任何 PASS；覆盖面问题见 §3.2、§6。

---

## 5. 检查重点 4：五类枚举、历史 PASS_WITH_EVIDENCE 与 FAILED

### 5.1 条件与采集方法是否拆分

**基本正确，但有两处结构性弱点。**

- 正确之处：manifest 表采用“条件状态 / 方法状态”双列（L25–L38 表头），delivery 表采用“分类 / 本轮结论”并逐行说明方法；两处都把同一条件区分了“谓词未证（`UNPROVABLE`）”与“采集方法不可安全运行（`NOT_SAFE_FOR_R0`）”。这是对 R0S2 RP-05「观察完整性 vs 目标谓词必须分列」的正确执行。
- 弱点 A（P3-01）：双列在文本层面**没有一句显式声明“方法 = `NOT_SAFE_FOR_R0` 表示未运行，不等于目标条件被测试并失败”**，而 Task L74 恰恰要求“未运行、安全停止、对象缺失和方法不安全不得记为 FAILED”。manifest L38 与 delivery L27 仅在 `FAILED` 行作了否定说明，未把该口径外推到所有行。
- 弱点 B（P2-04）：本轮自身的 `index_side_effect` **未**进入任何五类表（manifest 表 L25–L38 无该行；delivery 表 L21–L27 无该行），只以正文段落出现（manifest L45、delivery L17）。R0S3 Round 1 的 P2-01 正是要求为 `index_side_effect` 单列分类行（`codex-p02pre-r0s3-classification-20261011.md` L34：条件 `UNPROVABLE` / 方法 `NOT_VERIFIED`），本轮出现同类回退。

### 5.2 历史 PASS_WITH_EVIDENCE 是否限制到原有对象与时点

**通过。** manifest L27、L30、L31 与 delivery L23 均写明 `PASS_WITH_EVIDENCE（历史时点）` 且“只适用于原 evidence 的对象与时间，不外推至现在或完整集合”。具体限制逐项落实：

- identity/路径 metadata/ACL/WER 局部快照/13 个 hash → 仅 R0 evidence 原对象（delivery L23）；未外推同型的“当前”状态，而是另列 `UNPROVABLE`（delivery L24）。
- TEMP/cache/scratch 解析 → 明确“既有定点解析仅 `PASS_WITH_EVIDENCE`；当前映射 `UNPROVABLE`”（manifest L30）。
- protected-file baseline → “历史 13 项 `PASS_WITH_EVIDENCE`；当前 baseline `UNPROVABLE`”（manifest L31）；未扩展为全量 Git/用户数据 inventory。
- 未出现“历史 PASS ⇒ 当前 PASS”“历史 absence ⇒ 当前 absence”的任何推断。

### 5.3 FAILED 是否仅代表真实执行失败

**通过。** manifest L38「已执行查询失败：本轮没有目标 OS 查询 ⇒ `FAILED=∅`」；L21 明确“不得把此 stop 当作目标查询失败”；delivery L27 同义。与 R0S2 adjudication L48、R0S3 adjudication L41 的口径一致。

---

## 6. 检查重点 5：git status 的 index_side_effect 披露与用户未提交状态

| 要求 | 证据 | 判定 |
|---|---|---|
| `index_side_effect=NOT_VERIFIED` 如实披露 | manifest L45、delivery L17/L35 三处均明记，且 Task/Review prompt L15 要求的正是该标签 | **通过** |
| 未把旧 index hash 冒充本次紧邻 pre-hash | manifest L45「未做紧邻的 .git/index pre-hash……不把旧 index hash 冒充本次 pre-hash」；外部历史证据中存在的 `214767403C…F3B89C`（`codex-checkpoint-p02-profile-folder-contract-m6-20261010.md` L7 等）在本轮对象中**未被引用为本次 pre-hash** | **通过**（未冒用） |
| 未恢复/覆盖 index | manifest L45、delivery L17 | **通过** |
| 未执行破坏性 Git 操作 | delivery L17「未执行 reset、clean、stash、恢复、覆盖、删除或提交」 | 通过（自我报告，不可独立核验） |
| 用户未提交状态受保护 | delivery L17「此前所有未提交内容仍按原作者归属保护」 | 方向通过（见下） |
| 不以该项宣称 Git gate 通过 | delivery L35 | 通过 |

**但披露存在实质缺口与前后矛盾（P2-01 / P2-04）：**

1. **manifest 自相矛盾**：L42 声明「P02PRE host query 命令：NONE」，L45 却记录“曾执行一次普通 git status 命令”。两者并置会使读者无法判断本轮到底调用过哪些命令；且 L45 未记录该命令的**执行主体、时点、完整命令行、exit code、stdout/stderr**（delivery L17 甚至说“未观察到 Git 错误”——在未保留 stderr/exit 的情况下该表述无法支撑）。
2. **归因模糊**：manifest L45 说该命令发生在“非 P02 orchestration baseline 中”，delivery L17 说“本轮从 orchestration 工具曾执行”，措辞互相不完全对应，也未说明该命令是否属于本 Task 的授权范围（Task L52 允许治理文档状态检查，但允许范围不等于副作用已证）。
3. **用户未提交状态的“保护”无法被本轮验证**：由于未保留 `status` 输出（raw NUL 记录/hash）也无法读取 index，Reviewer 既不能确认用户未提交文件清单，也不能确认其未被改动。这是 STOP 轮次的**固有限制**，应显式登记为 `NOT_VERIFIED`，而不是以“未观察到错误”一笔带过。
4. 与上游先例对照：`codex-checkpoint-p02-profile-folder-contract-m6-20261010.md` L8、`codex-p02-owner-risk-waiver-manifest-r4-adjudication-20261010.md` L14 对该类普通 status 的处理均登记了“命令文本 + exit=0 + stdout 丢弃 + 无 pre-hash + 不恢复 index”四要素；本轮记录要素更少。

---

## 7. 检查重点 6：Findings（P0/P1/P2/P3）

**P0 = 0；P1 = 1；P2 = 5；P3 = 6。**

### P1

| ID | 级别 | 对象 / 证据 | 影响 | 建议（最小修正） |
|---|---|---|---|---|
| **R0S4-P1-01** | **P1（需修订，不阻断安全结论）** | Task 全文、manifest 全文、delivery 全文均无 bytes/SHA-256 pins；派发 L3–L6 提供的三个 pin 因此**在交付物内部无锚点**；对照 R0S2 Review RP-02（P2）→ R0S2 adjudication L24 `ACCEPT_WITH_LIMIT`（“下一次派发应把 pins 写入 prompt”）→ R0S3 adjudication L25 已由 Codex 侧复算绑定 | Reviewer 无法在该轮建立“被审字节 = 被语义审查字节”的绑定；本 Review 的三项 pin 全部只能记 `NOT_VERIFIED`。这不是安全缺陷，但使本轮 Review 独立性的证据链不完整 | Codex 在 adjudication / checkpoint 中登记 Task、manifest、delivery 的实际 bytes + SHA-256（并与派发三值对账），同时登记本 Review 交付物的 digest；如需第三轮核对，把 pins 直接写入 Review prompt |

### P2

| ID | 级别 | 对象 / 证据 | 影响 | 建议（最小修正） |
|---|---|---|---|---|
| **R0S4-P2-01** | P2 | manifest L42 vs L45（delivery L17 相关） | 同一文档内“命令 NONE”与“曾执行 git status”并存，属本轮事实记录不一致；且该命令的命令行/exit/stderr/输出保留状况未记 | 把 git status 移出“非本 Task 命令”的模糊归因：单列“治理侧 Git 读取”小节，逐项记录命令文本、exit、stderr 可得性、输出是否保留、`index_side_effect=NOT_VERIFIED`，并删除或改写 L42 中与之冲突的“NONE”表述 |
| **R0S4-P2-02** | P2 | manifest 表 L25–L38；delivery 表 L21–L27；manifest L45 / delivery L17 | 本轮自身的 `index_side_effect` 未进入五类分类表，与 R0S3 Round 1 P2-01 确立的“每项剩余条件单列分类”口径回退 | 在分类表补一行：条件对象=`本轮 index side effect`，条件状态=`UNPROVABLE`，方法状态保留原始标记 `NOT_VERIFIED`，并注明“旧 index hash 不补 pre-hash、不恢复/覆盖 index” |
| **R0S4-P2-03** | P2 | r6 L66（HKCU LocalDumps、`%LOCALAPPDATA%\CrashDumps`、`ReportQueue`、`ReportArchive`）；r6 L72–L85（12 只读根）；r6 L141–L145（canary 叶）；manifest L15/L25–L39 | r6 已登记的对象中，若干未在本轮 manifest 落表，导致“只读范围精确限于 r6 已列对象”无法逐条对账；canary/负向叶与 scratch 只覆盖到“两个 leaf empty-or-absent” | 在 manifest 表中补齐上述对象的单列行（方法=`NOT_SAFE_FOR_R0`，本轮=`NOT_RUN`），或新增“本轮未单列的对象及其归并位置”声明，明确 HKCU 键与三个 WER 目录仍只是历史观察候选、非读取许可 |
| **R0S4-P2-04** | P2 | Task L55–L62 vs manifest L43–L44 | 本轮禁项清单未显式覆盖 Task L61 的“权限提升、服务/驱动/ETW、网络、编译/JIT”，也未逐字覆盖 Task L59 的 module/provider/wrapper/后台缓存与历史路径 | 在 manifest 的禁止清单中逐条复述 Task L55–L62（可与 Task 交叉引用），补齐网络/编译-JIT/提权/服务-驱动-ETW/module-provider-wrapper 各项 |
| **R0S4-P2-05** | P2 | Task L17「五类归入」+ L50/L51；manifest L25–L39；delivery L21–L27 | 五类表未把“`NOT_VERIFIED`”作为**本轮完整性属性**与五类枚举的关系写清（R0S3 交付曾显式写明“`NOT_VERIFIED` 是原始记录属性，不是第五枚举的替代值”，`codex-p02pre-r0s3-classification-20261011.md` 语境），本轮仅有零散的 `index_side_effect=NOT_VERIFIED` 标签 | 在 manifest/交付加一句口径声明：`NOT_VERIFIED` 是原始审计标记/完整性属性，五类枚举用于条件与方法；并明确哪些行携带该方法列属性 |

### P3

| ID | 级别 | 对象 / 证据 | 影响 | 建议 |
|---|---|---|---|---|
| R0S4-P3-01 | P3 | manifest L25–L38 双列表头；Task L74 | 未显式声明“方法 `NOT_SAFE_FOR_R0` ≠ 条件测试失败”，口径仅出现在 `FAILED` 行 | 加一句总纲 |
| R0S4-P3-02 | P3 | manifest L31「13 项历史 hash」与 L34/L37 语境中的 scratch“13 exact leaf”（r6 L35） | “13”在两处指不同对象集合（protected-file hashes vs scratch leaf），若同行阅读易混 | 分别为“R0 protected-file hash 13 项”“R0 scratch leaf 13 项”加限定词 |
| R0S4-P3-03 | P3 | manifest L27（历史 PASS_WITH_EVIDENCE 行） | 未附 R0 evidence 的 13 项清单/对应证据行位置，历史集合不可在本轮内自证 | 加 R0 evidence 的段落引用（对象与 hash 表位置） |
| R0S4-P3-04 | P3 | `glob verification/P02/*r0s4*`；`grep R0S4 doc/` | Task L34/L35 的 adjudication 与 checkpoint 尚未创建；STATUS/Plan/Index 尚未登记 R0S4，Task L52/L46 的治理与 checkpoint 交付未完成（`in_review` 阶段的预期缺口） | 集成阶段补齐 adjudication、checkpoint 与治理登记 |
| R0S4-P3-05 | P3 | manifest L21/L42–L44；delivery L15；Task L24/L67–L68 | “零 host 查询 / 未启动子进程 / 未换 shell”是 Owner 自我报告，本派发禁止任何核验手段，故不可独立验证 | 在 adjudication 明记该声明为自我报告、`NOT_VERIFIED`（不可验证），不得记为已证明 |
| R0S4-P3-06 | P3 | delivery L13「本轮核对 Live Git 基线、STATUS、唯一 REBASELINE_PLAN、Index、P02/R0 Task、r6 execution manifest 与 R0S2/R0S3 adjudication」 | 该“已核对”的可复现证据（读了哪些、核到什么）未在交付内绑定；与 L17 的 git status 记录关系亦未说明 | 补一行核对清单与与 Git 读取的关系，或明示其属编排动作、非 Task 证据 |

**未构成 finding 的观察（明确不作为缺陷）**：manifest 与 Task 在“是否允许只读 ACL getter / 路径 metadata”上并非矛盾——Task L50 是有条件允许、L67 是硬前置，manifest L21 触发前置后整体冻结为零执行，属**收窄**而非扩张。

---

## 8. 覆盖与未覆盖风险

### 8.1 已覆盖（本轮 Review 已核）

- 授权归属与有限性；五值风险原值与固定英文原文的逐字一致（Task / manifest / delivery / r6 / R0S2 / R0S3 六处对照）。
- 不是 waiver、不是 Gate PASS、未解除 Build Barrier 的表述链。
- `STOP_BEFORE_HOST_QUERY` 的触发逻辑与 RP-01 的对应关系；未换 shell、未运行 getter 的记录一致性。
- 五类枚举的条件/方法拆分结构；历史 `PASS_WITH_EVIDENCE` 的时点限制；`FAILED=∅` 的口径。
- git status 的 `index_side_effect=NOT_VERIFIED` 披露、未冒用旧 pre-hash、未恢复 index。
- Task / manifest / delivery 三者的文本一致性、范围收窄方向、禁项与对象枚举覆盖度。

### 8.2 未覆盖 / 未核验（NOT_VERIFIED / NOT_RUN）

| # | 项 | 状态 | 原因 |
|---|---|---|---|
| 1 | Task / manifest / delivery 的 bytes、SHA-256 复算 | `NOT_VERIFIED` | 派发禁止 hash/OS/path 查询；工具与沙箱约束 |
| 2 | live HEAD / tree / branch / 工作树独立核验 | `NOT_VERIFIED` | 禁止运行 `git`；仅确认三份文档**文本**上的基线声明彼此一致 |
| 3 | 三份 artifact 自身是否登记 pin | 已核：**均未登记** | 见 P1-01 |
| 4 | “本轮零 host 查询 / 未启动子进程”的真实性 | `NOT_VERIFIED`（不可验证） | 验证手段本身被禁止（P3-05） |
| 5 | git status 的命令行、exit、stderr、输出保留 | `NOT_VERIFIED` | 未记录（P2-01） |
| 6 | 用户未提交文件清单与其完整性 | `NOT_VERIFIED` | 未保留 status 输出，禁止读取 index |
| 7 | Reviewer 侧 dispatch prompt 与本派发输入的字节一致性 | `NOT_VERIFIED` | 无法证明链路一致 |
| 8 | 上游 r6 / R0S2 / R0S3 对象的 bytes/SHA（其文档内声明值） | `NOT_VERIFIED` | 同上，仅核文本引用一致性 |
| 9 | Microsoft 官方文档原文 | `NOT_FETCHED` | 本轮保持零外部访问，按 r6 引用采用 |
| 10 | 任何 P02PRE host/Registry/WER/path/ACL/environment/hash 状态 | `NOT_RUN`（按设计） | 本轮安全停止，且属禁止范围 |

### 8.3 剩余风险（本轮不因 Review 而消除）

- **private registry technical condition 仍未满足**：`private_registry_absence=UNPROVABLE` 依旧，Owner 风险接受依旧只是风险接受；本轮**没有**产生任何技术证据。
- **runner 缺口未解**：`functions.exec_command` / PowerShell 启动、profile、module analysis cache、PSReadLine history、wrapper 与临时文件的副作用边界仍 `UNPROVABLE`；在没有新的精确绑定 runner 与独立 Review 前，任何 host 查询仍不得执行。
- **索引完整性缺口**：本轮 `index_side_effect=NOT_VERIFIED`，且无紧邻 pre-hash；该缺口**不可追补**。
- **P1/P2 未修订期间**：Task / manifest / delivery 的 artifact 级绑定与禁项覆盖不完整，后续若据其规划新轮次，存在继承“边界记不全”的风险。

---

## 9. 结论与建议的下一动作

**Review 决策：`CHANGES_REQUESTED`。**

- **安全结论不动摇**：本轮 `STOP_BEFORE_HOST_QUERY` 是正确的，`private_registry_absence=UNPROVABLE`、`Technical Gate=NOT_SATISFIED`、`Owner Risk Acceptance=APPROVED`、`Gate Disposition=WAIVED_BY_OWNER`、`Build Authorization=AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`、`P02PRE=BLOCKED`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`build/Cargo=NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN` 全部保持；本 Review **不**授权执行、**不**放行任何 Gate、**不**代替 Codex adjudication、**不**改变 waiver。
- **不构成 P0**：未发现伪造证据、扩权、把授权当 waiver、把 NOT_RUN 当 PASS、把方法否决当目标失败或弱化历史限制的情形。
- **修订范围（最小）**：P1-01（登记 Task/manifest/delivery 与本 Review 的 bytes/SHA 并写入 adjudication）、P2-01（消除 L42/L45 矛盾并完整记录 git status）、P2-02（`index_side_effect` 入表）、P2-03（补齐 r6 已列对象的单列行/归并声明）、P2-04（禁项清单逐条复述）、P2-05（`NOT_VERIFIED` 与五类枚举的口径声明）。
- **建议的下一动作（唯一）**：由 `Codex /root` 对 P02PRE-R0S4 执行独立 adjudication，同时完成上述 P1/P2 的文档层修订，登记三份 artifact 与本 Review 的 bytes/SHA，并在 checkpoint 中保留 `index_side_effect=NOT_VERIFIED`。在此期间**不**派发任何 host/Registry/WER/path/ACL/hash 查询，**不**换 shell，**不**创建 profile，**不**查询/安装/启用/启动 Windows Sandbox，**不**触碰 Build/Cargo 与 AC1–AC7。

---

## 10. Reviewer 未核验声明与自身副作用

- **Reviewer 自身副作用 = ZERO（除本文件外）**：未启动任何进程或 shell，未运行任何 `git` 子命令，未调用任何 OS/API/Registry/WER/profile/token/path/environment/ACL/hash 查询，未复算任何 bytes/SHA-256，未读取 `.git/index`，未抓取外部网页，未修改、删除或移动任何既有文件。唯一写入为**创建** `verification/P02/dsh-p02pre-r0s4-review-20261011.md`。
- 我**未**独立核验 HEAD/tree/branch、三份 artifact 与上游对象的 hash、git status 的副作用与输出、用户未提交状态、以及“零 host 查询”声明；上述各项一律标 `NOT_VERIFIED` / `NOT_RUN`，不作推测、不声称已复核。
- 本 Review **不**改变 private-registry waiver、Technical Gate、P02PRE 总体状态、Hard Build Barrier、Build Gate、build/Cargo 或 AC1–AC7；**不**授权执行；**不**代替 Codex adjudication；**不**把任何历史或聊天中的授权当作新的授权来源。
- 本文件的 bytes/SHA-256 由 Codex 在归档/绑定阶段独立复算；Reviewer 无法自算，故不在本文件内声明自身 digest。
