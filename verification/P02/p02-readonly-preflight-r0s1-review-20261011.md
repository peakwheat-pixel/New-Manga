# P02PRE-R0S1 独立 Review（非作者 Reviewer：DeepSeek Harness）

## 0. Metadata

| 字段 | 值 |
|---|---|
| Review ID | `P02PRE-R0S1-REVIEW-20261011-DSH-01` |
| Task | `P02PRE-R0S1`（`doc/tasks/P02PRE-R0S1.md`，`8303 bytes / BD73A543B2DBA2A28A38493769B64770C88DB14188D6BBD97189EA903082E2AD`） |
| Owner / Author | Codex `/root`（未参与本 Review） |
| Reviewer | DeepSeek Harness（非作者；未编写本 Task、manifest、checkpoint 或 evidence） |
| Integrator / Adjudicator | Codex `/root`（本 Review 不代替其裁决） |
| Repo / branch | `G:/CODEX/New Manga` / `main` |
| Reviewed HEAD / tree | `cddff58469b56e181019a8ddfeade80684bc7eb9` / `c25d051a4b9a0bd9773b50170e100f575ea19f2b`（按派发给定，**未独立核验**，见 §4 验证表） |
| 审查对象 pins（按派发采用） | manifest `22925 / CA293C34…FEC6DE3`；checkpoint `7583 / EE26F209…C63AEDB`；evidence `5489 / 05C2DD24…71F3FCBD` |
| 背景参考 pins（仅比对） | R0 evidence `99592 / AE16A27C…4879F3`；R0 Review `29404 / 427F582D…E6B5C554`；R0 adjudication `11145 / E6613196…D01375E` |
| 审查方式 | 纯只读文档审查（`read`/`grep`）：4 个主对象全文、3 个背景对象全文或定向检索 |
| 结论枚举 | `APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY` |
| Finding 计数 | P0=0；P1=0；P2=2；P3=5 |
| Gate 效力 | **无**。不授予/不放行/不改变 P02PRE、Technical Gate、Build Gate、Hard Build Barrier、AC1–AC7，也不表示 scratch 条件通过 |

## 1. 范围与限制

**审查范围**：上述 4 个 pin 文档的文字内容一致性、冻结控制流与原始 stdout 的逐字段比对、范围/停止边界/分类枚举、waiver 与 Gate 表述。另对 3 个背景 pin 做交叉比对（R0 已记录的两 leaf 路径与 SID、R0 P2-3 释放依据）。

**本 Review 未执行（NOT_RUN）**：任何 PowerShell/OS/API/registry/ACL/path/进程/环境查询；未启动 capture；未执行测试/build/Cargo；未修改任何文件（**未创建** `verification/P02/p02-readonly-preflight-r0s1-review-20261011.md`；按 Task L65，Reviewer 唯一交付对象为 Review 内容，由 Codex 将 stdout byte-for-byte 归档）。

**能力与绑定限制**：

- 未计算任何 bytes/SHA-256，未核验 HEAD/tree/工作树状态；pins 按派发等值**采用**而非**复算**，对象绑定强度等于派发声明。
- 未读取 R0 evidence 全文（仅对其做定向 `grep`），故对 R0 的引用限于命中行。
- 本 Review 的精确时钟未核验；派发未提供独立时间源，故不记录"当前时间"。
- 结论只针对交付文本的范围、绑定、控制流与分类；不推导任何真实 OS 对象当前状态。

## 2. 逐项审查结论（对应派发 6 项）

### 2.1 唯一 runner / 停止边界 / 目标路径范围 / 用户只读授权是否一致（无 scope creep）

| 检查 | 结论 |
|---|---|
| 唯一 runner | Task L29 = manifest L25 = checkpoint L35 = evidence L10：`functions.exec_command`、`shell="powershell.exe"`、`login=false`、`cmd` 直接取 manifest fenced body、无 wrapper/外部 executable/脚本文件。**四处文字一致**（实际二进制问题见 F-06） |
| 停止边界顺序 | identity → thread impersonation → Management/Utility 模块可信 → `G:` PSDrive provider/root → 共同祖先链 → 分支祖先/leaf → 一次性 leaf 枚举。Task L29/L40、manifest L25/L40、body L85–231、checkpoint L35 **一致** |
| 目标路径范围 | 仅 L1/L2 两 leaf + 其**完整**祖先前缀链。manifest L29–38 的 10 项顺序覆盖两条路径的**每一个组件**（`G:\` → `CODEX` → scratch root → `apps` → `desktop` → `src-tauri` → `gen`/`permissions` → leaf），**无跳项**（跳项会造成 reparse 逃逸缺口） |
| 两 leaf 字面值 | manifest L22/L23 与 R0 evidence L105/L106、JSON L753/L766 **逐字一致** |
| 祖先处理 | 仅 `Get-Item -LiteralPath` 逐项，**不列举祖先 children**（body 中祖先循环只有 `Get-Item`，`Get-ChildItem` 仅出现在两 leaf 各一次）→ 与 manifest L18/L33 一致 |
| 授权收紧 | manifest L12 明确"当前 Task 从该授权中**仅使用**身份 getter 与两个 scratch 目录的精确 metadata/direct-child enumeration"，窄于用户 2026-10-11 总授权的字面范围 |
| 实际执行范围 | 本轮只执行 identity/thread 与 `Microsoft.PowerShell.Core\Get-Module` 元数据查询 + `[IO.Path]::GetFullPath/Combine` 纯字符串运算；**未执行** `Get-PSDrive`、任何 `G:` 路径读取、任何枚举 |
| body 静态禁令核查 | 我逐行读完 body（L48–244）：无 `New-/Set-/Remove-/Out-File` 等写操作、无 `Add-Type`、无 P/Invoke/native、无 `Start-Process`/外部 executable、无 registry/ACL/profile API、无递归。**静态一致** |
| scope creep | **在审查范围内未发现执行的 scope creep**。唯一需要 adjudicator 注意的**文字**问题是：manifest L12 在 R0S1 artifact 内复述了更宽的用户总授权（含 ACL/TEMP/WER 类读取），虽同段已声明只使用窄子集，仍建议裁决时明示该复述**不是** R0S1 的授权扩张（见 §5） |

### 2.2 原始 stdout / 退出码 / PID / identity 字段 vs manifest 分支控制流；"已启动并安全停止"与 `NOT_RUN` 的区分

逐字段静态比对（原始 stdout 单行 vs body 的 STOP 分支格式串 `STOP|CapturePid={0}|CaptureStatus={1}|Identity={2}|IdentityError={3}|Modules={4}|ModuleError={5}`）：**字段数量、顺序、名称完全一致**；`Identity=@{...}` 的 7 个属性顺序与 body 的 pscustomobject 属性序一致；`Modules=@{...}` 的 5 个属性顺序一致。

控制流判定（**可由输出本身推出，而非仅采信叙述**）：

1. `IdentityError=` 为空 + `Identity` 块完整 → body 的 identity `try` 未抛异常，`$identityResult` 非空 → 未进入 `STOP_IDENTITY_UNPROVABLE` 分支。
2. `ThreadIdentityPresent=False` 且 SID=`S-1-5-21-2196946971-914346751-4210154634-1001`、`Authenticated=True` → 与 manifest L52 的 `$expectedSid` 逐一匹配 → 未进入 `STOP_IDENTITY_MISMATCH_OR_THREAD_IMPERSONATION`。
3. `CaptureStatus=STOP_UNTRUSTED_OR_UNAVAILABLE_BUILTIN_MODULE` 是 body **仅**在 L106 赋值的字符串 → 该分支确已执行 → `$commonFailure='NOT_SAFE_FOR_R0'`。
4. 因此 L124 的门条件 `$null -eq $commonFailure` 为假 → **`Get-PSDrive`、全部祖先 `Get-Item`、两个 leaf 的 `Get-ChildItem` 在控制流上均不可达**。evidence L26「`Get-PSDrive` 未执行，任何固定 scratch ancestor/leaf 路径均未查询，两个 leaf 也未枚举」**由冻结控制流蕴含，成立**。
5. `ModuleError=` 为空 → 模块 `try` 未抛异常（`Get-Module` 正常返回空集合），与 `Status=NOT_SAFE_FOR_R0` 一致；注意 `Get-Module` 返回空集合本身不是 ErrorRecord。

状态判定（**明确区分**）：

- 本轮**不是** `NOT_RUN`：shell 已启动（`$PID`=`44916`）且产出了只有 body 能生成的 stop record，属 Task L29 的"shell 已启动"情形与"capture 记为已启动但不完整"。
- 本轮也**不是**采集成功：`RUN_EXIT=0` 只说明调用工具侧返回成功，**不得**读作"采集成功"、更不得读作"无副作用"。
- 本轮对两个 leaf **未产生任何 PASS/FAILED 证据**（符合派发要求）。
- 强旁证（非独立证明）：`ExpectedManagementPath`/`ExpectedUtilityPath` 由运行时 `$PSHOME` 推导，其出现值与冻结 body 的运行时行为一致，且字段序、格式串、属性序无法由"随手手写一行"自然复现——支持（但未证明）执行的 `cmd` 与冻结 body 字面一致（字节级绑定缺口见 F-05）。

### 2.3 "Management/Utility 模块路径为空"能支持什么、不能推断什么

**仅支持**：本次冻结 runner 在本次 session 中**未获得可信的 built-in 模块预加载状态**（`$modulesTrusted=$false`），属"模块可信前置条件未满足"，因此按冻结停止规则安全停止 → runner 级 `NOT_SAFE_FOR_R0` 成立。

**不能推断**（evidence L29/L35 已如实声明，我确认其表述正确）：

- 不能推断模块**文件缺失**、未安装或 psd1 路径不可用；
- 不能推断任一 scratch path 的**存在性、类型、reparse 状态或内容**；
- 不能推断两个 leaf 当前存在、为空或非空。

**两个 scratch leaf 的状态**：未查询、未枚举 → 其 `empty-or-absent` 无任何证据；本 Review **不给出** `PASS_WITH_EVIDENCE` 或 `FAILED`，evidence 亦未给出，**符合要求**。

### 2.4 分类审查（五类枚举 vs 本 evidence 的 4 行）

| evidence 行 | 分类 | Reviewer 判定 |
|---|---|---|
| runner 继续执行安全前提（模块可信预加载） | `NOT_SAFE_FOR_R0` | **正确**，与 manifest L25/L42 停止规则及 body L104–107 一致 |
| L1 `…\gen\schemas` empty-or-absent | `UNPROVABLE` | 就"谓词证据"而言**正确且是唯一诚实的非结论标签**；但与冻结 body 在 `commonFailure` 分支的确定性映射（L167–171 → 两 leaf 序列化为 `NOT_SAFE_FOR_R0`）存在**标签语义冲突**，见 **F-03**（最小修正：双标注） |
| L2 `…\permissions\autogenerated` empty-or-absent | `UNPROVABLE` | 同上 |
| 精确时间 + shell startup/profile effects | `UNPROVABLE` | **正确**（stop record 不含 `$startedUtc/$endedUtc`；body 仅在 JSON 分支输出时间，从未到达） |

其余两类枚举未被使用，符合合同：leaf 未查询不得写 `PASS_WITH_EVIDENCE`/`FAILED`；`REQUIRES_ACTIVE_TEST` 保留项由 evidence L40 声明"保持既有 R0 adjudication 分类"，**无不当升级或降级**。

### 2.5 如实披露核查

| 要求 | evidence 位置 | 判定 |
|---|---|---|
| stderr 不可用 | L16「exec 结果没有提供独立 stderr 字段；本记录不据此声称 stderr 为空」 | **如实** |
| 精确时间戳不可用 | L16「精确时间为=`UNPROVABLE`，不得用之后读取的当前时间回填」 | **如实** |
| `login=false` ≠ 已证明 `-NoProfile` | L28「`login=false`，但这不证明 PowerShell profile 未运行；shell startup/profile effects=`UNPROVABLE`」 | **如实且表述准确** |
| 未观察到写入 ≠ 全局无副作用 | L28「不得把未观察到写入扩大为系统状态全局未变化的证明」 | **如实；未出现越界保证** |
| 未把停止说成成功 | L14/L26/L40/L45 | **如实；无 Gate/PASS 措辞** |

### 2.6 waiver 与 Gate 效力

evidence L40 的 6 项固定原值与 R0S1 Task L23、R0 adjudication L17**逐字一致**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。全文未出现把 waiver 写成技术 PASS、也未对 P02PRE/Build Gate/Hard Build Barrier/AC1–AC7 产生任何放行表述。**确认：无 PASS 或放行效力。**

## 3. Findings

**P0 = 0，P1 = 0（在审查范围内未发现阻断级问题）。**

| ID | 级别 | 对象 / 证据 | 影响 | 建议（最小修正） | 状态 |
|---|---|---|---|---|---|
| **F-01** | **P2** | manifest L25、L40「枚举只读取返回对象的数量，**不读取 child 的 name、属性、时间或内容**」 vs 冻结 body L222 `@(Get-ChildItem -LiteralPath … -Force -ErrorAction Stop)` | `Get-ChildItem` 必然枚举目录项并**物化**含 `Name`/`Attributes`/时间戳的对象后才能计数；"不读取 name"作为**操作层承诺不可满足**，只有"不向证据序列化/不使用"层面成立。若未来某轮真正执行枚举，"未观察 child 名称"这一安全结论将无法由证据支撑 | 改为可满足表述：「仅向证据序列化/报告 direct-child **数量**；不把 child name/属性/时间/内容写入输出或证据，也不据 child 元数据推断状态」。若确需"未观察名称"，须在**重新冻结**的 manifest 中改用不返回名称的枚举方式并另行安全评估，不得在运行中变更 | `OPEN`（对本次交付无实际影响：本轮枚举从未执行；属冻结合同表述缺陷） |
| **F-02** | **P2** | manifest L25/L42 + body L94–107；checkpoint L16（advisor `SAFE_TO_CAPTURE`） | 冻结的**模块可信前置条件在本机 host session 下经验性不可满足**（pwsh 7 未预加载 Management/Utility → 两条路径均为空）。按冻结 body 原样重跑，将**确定性地**在同一分支停止，Task 目标（两个 leaf 的 direct-child count）无法达成。静态顾问只做文档安全评审，**未覆盖"前置条件可满足性"** | 由 Codex adjudicate 二选一：(a) 接受本轮停止、将 leaf 条件维持 `UNPROVABLE`；(b) 冻结**修订版** runner 并在执行前重新取得非作者静态意见 + pre-query pin——例如以只读方式核验 `$PSHOME` 下 psd1 路径/存在性且**不触发模块自动加载**。**严禁**在运行中放宽该检查、允许自动加载或改用 alias/同名函数替代 | `OPEN`（需裁定；本 Review 不授权任何替代路径） |
| **F-03** | P3 | evidence L36/L37（`UNPROVABLE`） vs body L167–171、L232–235（`commonFailure='NOT_SAFE_FOR_R0'` → 两 leaf 序列化为 `NOT_SAFE_FOR_R0`） | 同一控制流下，冻结 body 的确定性输出与 evidence 的人工标签不一致；读者可能误读为"只是证据不足、重跑即可"，而忽略 runner 级安全不可用 | evidence 分类表增加双列/脚注：「谓词证据=`UNPROVABLE`；冻结 body 在该控制流下序列化为 `NOT_SAFE_FOR_R0`（安全处置）」；并明确**两类都不得升级为 PASS** | `OPEN`（表述层） |
| **F-04** | P3 | evidence L14「两个模块**均未**以冻结的路径预加载」 vs raw stdout `ManagementPath=`/`UtilityPath=` 为空；body L99 的 `if ($managementModule.Count -eq 1)` | 记录**无法区分**"0 个已加载模块"与"≠1 个已加载模块（如多版本同时加载）"两种情形（两者都输出空路径）。因此 L14 的"均未预加载"是**强于记录**的断言 | (a) L14 改为「未以已加载模块形式返回（Count 为 0 或 ≠1，记录未区分）」；(b) 后续 manifest 在 stop record 中增加 `ManagementCount`/`UtilityCount` 字段 | `OPEN`（对本轮结论无实质影响：两种情形都导致同一安全停止） |
| **F-05** | P3 | evidence L10 声称 `cmd` 直接取自 manifest fenced body；无 `cmd` 原文/bytes/SHA 或 dispatch log 归档 | 执行的命令文本与冻结 body 的**字节一致性**无法从交付物独立核验；"仅执行了 body 内语句"的推理依赖此绑定（R0 同类问题的 P3-6 已为此立规） | 沿用 R0 adjudication 的修正：在 pre-query checkpoint 或 dispatch log 中登记**实际 `cmd` 的 bytes/SHA-256** | `OPEN`（绑定强度问题，非事实错误；当前有格式/字段序强旁证） |
| **F-06** | P3 | Task L27/L29、manifest L6/L25、checkpoint L35 写 `shell="powershell.exe"` vs raw stdout 的 `ExpectedManagementPath=C:\Program Files\PowerShell\7\Modules\…`（即 `$PSHOME`=`C:\Program Files\PowerShell\7`，与仓库内 host 记录 `pwsh.exe 7.6.6` 一致）；evidence L14 亦自称"冻结的 PowerShell 7 安装路径" | 冻结参数名疑似为主机工具的名义 shell 选择器，**实际进程为 pwsh 7**；evidence 未说明该差异。因 expected 路径由运行时 `$PSHOME` 推导，检查本身**不绑定版本**，故无安全影响 | evidence/manifest 显式注明：该参数为主机 shell 选择器，实际解析为 `pwsh`（`$PSHOME` 观测值），因此模块 expected path 随 `$PSHOME` 派生 | `OPEN`（文档准确性） |
| **F-07** | P3 | evidence L14「工具返回 `RUN_EXIT=0`，没有返回 session ID」；Task AC（L56）要求"逐目标记录实际命令、**时间窗口**、PID、结果或错误" | `RUN_EXIT=0` 的归属（主机工具 vs PowerShell 进程）未声明；AC 要求的 UTC 时间窗口缺失（已披露为 `UNPROVABLE`，非隐瞒）。本轮无 target 命令，故"逐目标命令"自然缺失 | evidence 明示 `RUN_EXIT` 的归属与"不得读作采集成功"；时间窗口按"工具未提供、`UNPROVABLE`"保留，**不得**用事后时间回填 | `OPEN`（AC3 属"已披露的部分不满足"） |

## 4. 验证表

| # | 检查项 | 状态 | 依据 / 原因 |
|---|---|---|---|
| 1 | 4 个 pin 的 bytes/SHA-256 复算 | `NOT_RUN` | 派发禁止 OS/path/hash 查询；pins 按派发等值采用 |
| 2 | HEAD/tree/branch/工作树状态独立核验 | `NOT_RUN` | 同上；未运行 git 或任何进程 |
| 3 | 3 个背景 pin 的复算 | `NOT_RUN` | 同上；仅做内容交叉比对 |
| 4 | 原始 stdout 与冻结 body 格式串/字段序逐项比对 | **PASS（文本层）** | 6 字段名/序、`Identity` 7 属性序、`Modules` 5 属性序全一致（§2.2） |
| 5 | PID/identity/SID/thread-token 与冻结期望比对 | **PASS（文本层）** | SID 匹配 manifest `$expectedSid`，并与 R0 evidence L22 记录的 `HOME-MY\49745` + 同 SID + `CloudAP` 一致；`ThreadIdentityPresent=False`；PID 44916 仅见记录，**无独立进程核验** |
| 6 | "未执行 drive/任何 G: path/未枚举 leaf"的控制流蕴含 | **PASS（文本层）** | `CaptureStatus` 值只可能由 body L106 产生 → 路径代码不可达（§2.2） |
| 7 | 两 leaf 未获 PASS/FAILED | **PASS** | evidence 表两行为 `UNPROVABLE`；无 PASS/FAILED 标签 |
| 8 | "模块路径为空"仅支持前置未满足、不支持文件缺失/路径状态推断 | **PASS** | evidence L29/L35 表述正确；F-04 仅为记录粒度问题 |
| 9 | stderr 可用性 | `NOT_RUN`（不可得） | 工具未提供独立 stderr；evidence 已如实声明 |
| 10 | 精确时间戳 | `NOT_RUN`（不可得） | stop record 无时间字段（body L237/241 不一致处已核实）；`UNPROVABLE` 分类正确 |
| 11 | `login=false` ≠ `-NoProfile` | **PASS（文本层）** | evidence L28 表述准确 |
| 12 | 未把"未观察到写入"扩大为全局无副作用 | **PASS（文本层）** | evidence L28 明确拒绝该外推 |
| 13 | waiver/Gate 未被改变 | **PASS（文本层）** | evidence L40 与 Task L23、R0 adjudication L17 逐字一致；无放行措辞 |
| 14 | Task AC 勾选状态 | 与 evidence 一致 | Task L54–59 全部 `- [ ]`；AC3 时间窗口部分不满足已披露（F-07） |
| 15 | 目标路径/祖先链完整性、两 leaf 字面值 | **PASS（文本层）** | 祖先前缀链无跳项；与 R0 evidence L105/L106 逐字一致 |
| 16 | Reviewer 自身副作用 | **ZERO** | 未运行任何命令/进程，未写文件，未执行 capture/测试 |
| 17 | 本 Review 未核验项 | `NOT_VERIFIED` | 工作树对象哈希/HEAD、进程启动副作用、宿主 OS 状态：**无独立证据，不作猜测** |

## 5. 决定与剩余风险

**决定：`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`。**

含义严格限定为：这份**有限的只读证据交付**（capture 已在模块前置检查处安全停止、两个 leaf 未获任何数据、时间与 profile 边界如实记为 `UNPROVABLE`、waiver/Gate 未变）**可交 Codex 独立 adjudicate**。它**不代表** scratch 条件通过、不代表 runner 前提满足、不代表任何 Gate 通过，也不代替 Codex 的裁决职责。无需重采即可交付（本轮本就无数据可采）；F-01/F-02 需在 adjudication 层面处置。

**剩余风险与给 adjudicator 的建议**：

1. **runner 可满足性未解决（F-02）**：Task 的可观察目标在两个 leaf 上仍未取得任何证据，`empty-or-absent` 维持 `UNPROVABLE`；按 r6 §119 语义，执行前检查项仍应视为未通过。任何修订版 runner 必须重新冻结 + 重新取得非作者静态意见 + pre-query pin，**不得**通过放宽模块检查来"让它跑通"。
2. **授权复述风险**：manifest L12 在 R0S1 artifact 内复述了更宽的用户总授权（ACL/TEMP/WER 类读取）。建议 adjudication 明示该复述不构成 R0S1 的授权扩张，防止后续轮次据此扩大范围。
3. **证据绑定强度**：`cmd` 字节一致性（F-05）、`RUN_EXIT` 归属（F-07）、记录粒度（F-04）均依赖 Owner 单方记录；本轮**未发现**与冻结控制流矛盾之处，但也**无法独立认证**。
4. **状态滞后**：冻结 checkpoint 仍写 `CAPTURE_NOT_RUN`（其自述为查询前快照，evidence L9 已单向引用）。建议 adjudication 在 checkpoint/STATUS/DAG 处补记 post-capture 状态与"checkpoint 为 pre-query 快照"的取代关系。
5. **未核验声明**：本 Reviewer 对工作树对象哈希/HEAD、进程启动副作用、宿主 OS 状态**没有独立证据**，全部标为 `NOT_VERIFIED`/`NOT_RUN`，不作任何猜测；Codex 的独立 adjudication 不应以本 Review 代替。

**推荐下一 Task**：无新的可立即释放 Task 由本 Review 指定；下一可执行动作是 **Codex `/root` 对 R0S1 独立 adjudicate**（须自行固定 Review 对象 pins、核准 F-01/F-02 的处置，并保持 Build Gate/Hard Build Barrier/AC1–AC7 原状）。
