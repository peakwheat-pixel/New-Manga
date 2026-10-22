# P02 AppContainer 隔离契约 r4 · 非作者只读 Review（DSH）

- Reviewer：DeepSeek Harness（非作者；契约与 Task 由 Codex 编写，角色互异）
- 日期：2026-10-10（Asia/Shanghai）
- 本会话性质：**纯文档审查**。未修改/创建/删除任何文件，未创建 profile，未改 ACL/label/registry，未运行任何 probe、Sandbox、build、Cargo、Tauri、PyInstaller、runner、Vitest 或产品测试，未读取用户数据样本、未进入 `G:\CODEX\P02-scratch-build-source`。

---

## 1. 工具能力与实际读取记录

### 1.1 能力声明（先行）

| 能力 | 本会话实测 | 证据 |
|---|---|---|
| `pwsh` | **不可用（初始化即失败）** | 5 次尝试（`git rev-parse`、`Get-FileHash` 相对/绝对路径、`Get-Location` 最小命令、更换命令形态）全部返回同一条：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`；第 5 次为一次性升级重试，返回 `sandbox escalation to "danger-full-access" requires approval, but no approval channel is available` |
| SHA-256 / 文件字节数 / `git status` / HEAD·tree 复算 | **不可用**（均依赖 shell） | 同上；无其它可复算路径（本会话无 bash/其它 shell 工具，`read` 只返回行号内容，不返回字节数） |
| 文件读取 / 路径枚举 / 内容检索 | 可用 | 下述对象逐份读取成功 |
| `web_search` | 不可用（HTTP 401 鉴权失败） | 改用 `web_fetch` + Microsoft Learn 检索 API |
| `web_fetch`（公共文档） | 可用 | 见 §6 |

**结论**：本会话**不能独立复算任何 SHA-256 或字节数**，故不得声称 exact-object Review 成立。这不是内容 mismatch，而是验证能力缺失。

### 1.2 object_binding 状态

**`object_binding = NOT_VERIFIED`**

| 绑定项 | dispatch 声明值 | 本会话实测 | 判定 |
|---|---|---|---|
| 项目根 | `G:\CODEX\New Manga` | 四个对象均实际存在于该根下 | 路径级成立 |
| 契约 SHA-256 | `F025A267…1F49` | **UNAVAILABLE** | **未核验** |
| Task SHA-256 | `C7959EF9…138C` | **UNAVAILABLE** | **未核验** |
| r3 报告 SHA-256 | `50EA7BAC…8117` | **UNAVAILABLE** | **未核验** |
| branch=`main` / HEAD `cddff584…` / tree `c25d051a…` | 同声明 | 未复算（未读 `.git`） | 未核验 |

**实际读取形态（非哈希证据）**：`appcontainer-isolation-contract-r4.md` 共 165 行、`doc/tasks/P02.md` 共 370 行、`dsh-appcontainer-contract-r3-review.stdout.md` 共 228 行、`codex-appcontainer-contract-r3-adjudication.md` 共 44 行。

**声明一致性（非复算，仅旁证）**：r4 契约 SHA 同时出现在派发 prompt 第 9 行与 `doc/tasks/P02.md:110`，两处字面一致；r3 报告 SHA 同时出现在 prompt 第 11 行与 `codex-appcontainer-contract-r3-adjudication.md:11`，字面一致。这只证明「声明彼此一致」，**不构成我自己的字节复算**。

### 1.3 实际读取的对象

1. `verification/P02/appcontainer-isolation-contract-r4.md`（全文 165 行）
2. `doc/tasks/P02.md`（全文 370 行；重点 5、13、51、58–62、64–72、74–81、108–110、114 行）
3. `verification/P02/dsh-appcontainer-contract-r3-review.stdout.md`（全文 228 行）
4. `verification/P02/codex-appcontainer-contract-r3-adjudication.md`（全文 44 行）
5. `verification/P02/dsh-appcontainer-contract-r4-review.prompt.md`（27 行）
6. `verification/P02/dsh-appcontainer-contract-r4-dispatch-attempt1.log`（3 行）
7. `glob` 路径枚举：确认 `verification/P02/appcontainer-isolation-contract-r2/r3/r4.md` 为三个独立文件，且 `dsh-appcontainer-contract-r4-review.*` 在此之前**不存在**已落盘的 r4 报告
8. 公共一手/官方文档（§6），仅文档语义，不代表本机状态

---

## 2. decision

- **正式 decision = `NOT_VERIFIED`**
  理由：对象绑定层无法在本会话独立复算 SHA-256/字节数，因此本报告不能作为 exact-object 批准；按项目 r2/r3 先例，「不可核验」≠「mismatch」，故降级为 `NOT_VERIFIED` 而非 `BLOCKED / hash mismatch`。
- **内容层结论 = `APPROVED_WITH_CONDITIONS`**
  理由：r3 的 19 项 finding 中 16 项完全闭合、3 项有残余；本轮新增 **P0=0 / P1=0**、P2=3、P3=6。内容上无阻断级缺陷，但有 3 项 P2 应在任何进一步授权（尤其 profile 创建路径）前修正。
- **重要限定**：因对象绑定未成立，本报告**不能被用作** `契约 §8.1` / `§精确下一步 2` 所需的 exact-hash Review 通过凭证；下一轮必须由可执行 shell 的环境复算 SHA 并显式声明「本次 Review 为内容级」。

---

## 3. 新增 finding 计数（本轮 r4）

| 严重度 | 数量 | 编号 |
|---|---|---|
| P0 | **0** | — |
| P1 | **0** | — |
| P2 | **3** | R4-01、R4-02、R4-03 |
| P3 | **6** | R4-04 … R4-09 |
| 合计 | **9** | 另：C-00（验证能力）仍未闭合，不计入内容 finding |

> 历史计数澄清（不改写）：r2 报告内容结论 `CHANGES_REQUESTED P0/P1/P2/P3=2/5/8/7`；r3 报告 `NOT_VERIFIED`／内容 `CHANGES_REQUESTED P0/P1/P2/P3=0/3/8/8`（r3 报告正文自述「15」与其逐项 ID 实为 19 项不一致，`r3 adjudication:12` 已如实指出且未擅自改写）。**上述数字均为历史结果，不是本 r4 Review 的结果。**

---

## 4. 逐条 Findings（新增）

### P2

#### R4-01 — §2 仍保留「必须证明私有 registry 存储不存在」与调用 `GetAppContainerRegistryLocation` 的可执行条文，与 §1.1.1 的 `UNPROVABLE / BLOCKED` 直接冲突且无交叉引用
- **严重度**：P2
- **路径/条款**：`appcontainer-isolation-contract-r4.md:45`、`:47`（对照 `:27` = §1.1.1）
- **触发**：执行者按 §2 逐条实施「profile 创建前只读检查」，或按 `:47` 的强制要求「仅在文档要求的当前用户/impersonation 身份上下文内调用 `GetAppContainerFolderPath` 和 `GetAppContainerRegistryLocation`，并逐项记录调用 token、API HRESULT、返回路径/HKEY 身份与关闭句柄结果」。
- **影响**：`§1.1` 声明 addendum 优先，但该声明是**概括性**的，§2 这两条未加任何指向 §1.1.1 的交叉引用或作废标记。只读 §2 的执行者会认为：(a) 三项创建前不存在性证明是可完成的任务；(b) `GetAppContainerRegistryLocation` 的调用是被授权的强制动作。而 §1.1.1 的原话正是禁止「调用可能创建/初始化 storage 的 API」——两项条文在**同一个被判定为不可证明的对象**上给出相反指令。这正是 r3 P1-01 想要消除的「执行路径停在创建前、且无法区分『不存在』与『无法检查』」的残余形态。
- **最小修正**：在 `:45` 与 `:47` 各加一句显式作废/交叉引用，例如「本项已由 §1.1.1 判定为 `private_registry_absence=UNPROVABLE / BLOCKED`；在 P1-01 经新授权解除前，本条不得执行，**包括不得调用 `GetAppContainerRegistryLocation`**」。或直接删除 `:47` 中该 API 的强制调用要求。

#### R4-02 — §8.4 输出例外集合与 §1.1.5 / §1.1.9 不同步：仍把 profile/private registry 无条件列为排除项，且仍写「两处 canary」
- **严重度**：P2
- **路径/条款**：`appcontainer-isolation-contract-r4.md:147`（§8.4）；对照 `:31`（§1.1.5 新增负向 control）、`:35`（§1.1.9 冻结 exclusion manifest）、`:99`（§4.5 正/负 canary 与只读 alias）
- **触发**：按 §8.4 构造前后比较的排除集，或按 §8.4 执行「其他 root dirty/untracked 哈希逐项 MATCH」。
- **影响**：两处不一致。① §8.4 把 `profile/private registry` 列为**无条件排除项**，即「本轮允许新增」；而 §1.1.9 明确「profile/private-registry 不存在性未证实前不得把它们列为『本轮允许新增』」。在 P1-01 判定为 `UNPROVABLE` 的当下，若某次只读测量真的把 target private registry storage 创建出来，按 §8.4 该变化**不会**出现在差异面里 —— 这恰好是 P1-01 唯一可用的运行时检测面被削弱。② §8.4 仍写「两处 canary」，但 r4 已把对象扩为三类：Task:79 只读 alias（写成功即 BLOCKED）、§1.1.5 新增的独立负向 DACL control、§4.5 独立正向 canary；§1.1.9 新增的 exclusion manifest 自身亦未列入。
- **最小修正**：把 §8.4 改写为与 §1.1.9 一致的表述：「排除集以 §1.1.9 冻结的 manifest 为唯一事实源；profile/private registry 在不存在性证实前**不属于**排除项，其出现即 `UNKNOWN / BLOCKED`」，并把 canary 计数改为与 §4.5/§1.1.5 实际对象一一对应的精确路径列表。

#### R4-03 — 负向 DACL control 只规定了父链/label 条件，未登记精确 scratch 路径，写入面无法从表内枚举
- **严重度**：P2
- **路径/条款**：`appcontainer-isolation-contract-r4.md:31`（§1.1.5「control 使用与任何 Package SID ACE 不同的 scratch 父链」）、`:33`（§1.1.7「所有 canary/control 路径均相对 `G:\CODEX\P02-scratch-build-source`」）、`:99`（§4.5「负向 DACL control 使用另一个新 scratch 子目录」）、`:78–91`（§4 输出表）、`:149`（§8.6 Gate 要求「scratch 正/负 canary」）
- **触发**：为负向 control 新建目录、或按 §4.3 判定哪些 leaf 可以获得 Package SID ACE / Low label。
- **影响**：正向 canary 有精确路径（`verification/P02/tmp/lpac-write-control/`，`:99`），只读 alias 有精确路径（`verification/P02/tmp/smoke-readonly-probe/`，`:99`），**负向 control 只有条件、没有路径**。这与 r3 P2-05 所纠正的同类缺陷（对象归属不明导致写入面不可枚举）性质相同：§4.2 的「只能新建 exact leaf」在负向 control 上无从校验，§8.6 的 Gate 项「正/负 canary」也无法逐对象绑定。另：§4.3 授权设置 DACL/Low label 的对象集合是「上述 exact output leaf + `lpac-write-control/`」，负向 control 既不在表内也不在该句内，其「不授 Package SID ACE / 不改 label」的前提缺少可比对的登记对象。
- **最小修正**：显式命名负向 control 的精确 leaf（例如 `verification/P02/tmp/lpac-write-deny-control/`），在 §4 输出表新增 `verification/P02/tmp/` 行并把三条 leaf 全部列明；同时写明该 leaf 的父链与自身禁止继承任何 Package SID ACE、禁止改 label/policy。

### P3

#### R4-04 — §8.1 的只读 preflight Gate 条件引用「r3 独立 Review … 通过后」，而 r3 Review 从未通过
- **严重度**：P3
- **路径/条款**：`:144`（§8.1）；对照 `:7`（r3 Review=`NOT_VERIFIED`）、`:164`（§精确下一步 2）、`doc/tasks/P02.md:110`
- **触发**：判定只读 OS preflight 是否已获准。
- **影响**：§8.1 的原文是「**r3 独立 Review 与 Codex finding adjudication 通过后**，才可进行无 profile、无 ACL/registry 修改的只读 OS preflight」。r3 Review 的实际结论是 `NOT_VERIFIED` + 内容 `CHANGES_REQUESTED`，从未「通过」；因此该 Gate 条件在严格字面下**永不可满足**，而在宽松解读下（把「通过」理解为「已完成 adjudication」）又会在 **r4 Review 之前**放行 preflight，与 `:164` 及 `Task:110`「Review 通过或处置前不做 OS preflight」不一致。这是 §1.1 优先列表**未覆盖**的复制自 r3 的残留 Gate 条件。
- **最小修正**：把 `:144` 的「r3 独立 Review」改为「本轮（r4）独立 Review」，并明确「本轮 Review 的 `object_binding=NOT_VERIFIED` 时，须由具备复算能力的复核或 Codex 显式接受内容级审查后方可进入」。

#### R4-05 — §8.5 术语漂移 `profile folder/private storage`，与 §1.1.11 声明的三术语一致口径不符（P3-10 残余）
- **严重度**：P3
- **路径/条款**：`:148`（§8.5）；对照 `:37`（§1.1.11 声明「`profile directory`、`local-data directory`、`private registry storage` 用词一致」）、`:45`、`:47`、`r3 adjudication:32`
- **触发**：把删除后残留断言与创建前不存在性断言逐项对应。
- **影响**：§1.1.11 声称术语已统一，但 §8.5 仍写「删除后重测 **profile folder/private storage** 不残留」，既非 §1.1.11 的三个固定术语，也与 §2 的三项对象命名无法一一对应。这是 r3 P3-10 的同类残余，且 addendum 存在「已声明一致但实际未一致」的落差。
- **最小修正**：把 §8.5 改为「删除后重测 `profile directory`、`local-data directory`、`private registry storage` 三者均不残留」。

#### R4-06 — §1.1.11「当前没有 profile，不运行任何 probe」与 §8.1 允许的只读测量冲突，且 MIC control 被错误地挂到「有 profile」前提上
- **严重度**：P3
- **路径/条款**：`:37`（§1.1.11 末句）；对照 `:144`（§8.1 允许只读 preflight）、`:164`（§精确下一步 2「纯只读 OS measurement」）、`:132`、`:149`
- **触发**：判定本轮是否允许 `GetNamedSecurityInfoW` 只读 DACL/label 查询、主仓只读 hash、WER 只读快照等纯测量动作。
- **影响**：① `:37` 末句字面为「不运行任何 probe」，若按字面执行，会一并禁止 §8.1/`精确下一步 2` 明确允许的**只读测量**，使 r3 Review §4 与本报告 §8 的 preflight 放行边界失去依据（正确口径应为「不运行任何写探针/MIC 探针」而非「不运行任何 probe」）。② 该句把未来的 MIC negative control 前置条件写成「如能安全创建 profile」，但 MIC 拒绝证据只需 Low IL token 与 Medium/无标记目标，**不依赖 AppContainer profile**；真实的当前障碍是「无写探针授权」。这一措辞会把一条与 profile 无关的证据项永久绑死在已被判 `UNPROVABLE / BLOCKED` 的 profile 创建上，从而连带影响 §8.6 Gate 项「MIC/DACL」的可达性判断。
- **最小修正**：改为「当前不运行任何**写探针或 MIC 探针**；`§8.1` 的只读测量不受此限。MIC negative control 的独立证据仅在获得写探针授权后另行登记，与 profile 是否创建无关」。

#### R4-07 — §1.1.7 声称「scratch 输出表另含 clone 相对路径 `verification/P02/tmp/`」，但 §4 表内无该行
- **严重度**：P3
- **路径/条款**：`:33`（§1.1.7）；对照 `:78–91`（§4 输出表 12 行，仅有 `tmp/`、`verification/P02/cargo-target/`，无 `verification/P02/tmp/`）、`:97`、`:99`
- **触发**：核对「LPAC 可写输出根」清单与 canary/control 归属。
- **影响**：addendum 是规范性文本且有优先权，故写入面本身仍可枚举（该路径由 §1.1.7 授权），不构成未枚举写入；但表与 addendum 不一致，读者仅凭 §4 表会认为 `verification/P02/tmp/**` 不是已登记的 scratch 输出根，而 §4.3/§4.5 的三个 leaf 全部落在该根下。r3 P2-05 的「§4 表内新增一行」这一半确实未落实。
- **最小修正**：在 §4 表补 `verification/P02/tmp/` 行（用途：canary/control 与只读 alias 的宿主根），或把 §1.1.7 的措辞改为「scratch 输出范围另含 …（本节有效，表未同步）」。

#### R4-08 — §5 的「明确禁止读取/写入：主仓」未标明约束主体，与 §8.4/§1.1.9 要求在 `verification/P02/**` 落盘证据存在解释张力
- **严重度**：P3
- **路径/条款**：`:103`（§5）、`:105`、`:106`；对照 `:35`（manifest 路径 `verification/P02/appcontainer-preflight-exclusions-r1.json`）、`:147`（§8.4 前后比较与排除集）、`doc/tasks/P02.md:51`（Owner allowlist 含 `verification/P02/**`）
- **触发**：确定 manifest、digest 清单、WER 快照、canary 证据等 artifact 的宿主位置。
- **影响**：§5 标题与首句是对「路径访问判定」的统一禁令，未写明其约束对象是 LPAC 进程（及其子进程/JS/C++ 组件）还是同时约束 controller。§1.1.9 要求先在 `verification/P02/...` 建立并哈希 manifest —— 若按字面同受 §5 禁令，则该 artifact 无处可写；若归属 controller 写入，则在 Task Owner allowlist 内成立。执行者可能据 §5 误判「不能产出证据」，或在反之的解读下多写未登记路径。
- **最小修正**：在 §5 首句加主体限定：「本节约束 LPAC 进程及其全部子进程/组件；controller 的 evidence 产出仅限 Task Owner allowlist 的 `verification/P02/**`，且不得写入 §5 deny 集合中的任何对象。」

#### R4-09 — 未声明 `P1-01` / `P1-02` 的终止性后果与升级出口（建议性）
- **严重度**：P3（建议性，非缺陷阻断）
- **路径/条款**：`:27`（§1.1.1）、`:28`（§1.1.2）、`:149`（§8.6 Build Gate）、`:165`（§精确下一步 3）
- **触发**：判定该 blocker 是「待测项」还是「可能永久阻断本方向、需用户裁决」。
- **影响**：r4 正确保持 fail-closed，但未写出：若系统对象 DACL 缺乏适用 `S-1-15-2-2` ACE 或不可读（`:28`），本机非提权 Codex-only 路线可能**不可实施**，届时应由用户裁决（放弃该方向 / 另行授权提权 / 接受 Build Gate 长期 `BLOCKED`）。缺少该出口会让 P02 长期停在 BLOCKED 而无人被触发决策（r3 Review §6 曾提示该情形，r4 未承接）。
- **最小修正**：在 §精确下一步追加一条：「若 §1.1.1/§1.1.2 判定为不可解除，Codex 须向用户登记该方向不可实施结论与三个可选裁决项，不得静默长期 BLOCKED。」

---

## 5. r3 finding disposition 是否成立

判定口径：**不采信 adjudication 自述，只看 r4 实际条文是否落地**。

| r3 finding | adjudication 处置 | r4 实际落点 | 本次判定 |
|---|---|---|---|
| C-00 对象绑定能力 | 保持 `NOT_VERIFIED`；下一轮 prompt 明列 SHA | prompt:9–11 已列契约/Task/r3 报告 SHA；`:36` §1.1.10 写明 DSH 无法复算时记 `NOT_VERIFIED`、内容 Review 不得冒称 exact-hash | **流程要求已落实；绑定仍未闭合**（本会话无 shell）→ 见 R4-07 之外的独立限制，不计为契约缺陷 |
| P1-01 私有 registry 创建前不存在性 | OPEN / BLOCKED | `:27` `UNPROVABLE / BLOCKED`，禁猜 key、禁调用可能初始化 storage 的 API、禁 `CreateAppContainerProfile`；`:45`、`:165` 维持 profile=`NOT_CREATED` | **方向成立且经文档核验支持**（§6）；但 `:45/:47` 保留可执行矛盾 → **R4-01**，未完全闭合 |
| P1-02 系统 DACL 只读可见性 | 接受，fail-closed | `:28` 分列 `SYSTEM_ACL_UNREADABLE` / `SYSTEM_ACL_MISSING`，均 `BLOCKED`，不提权、不设 ACL、不加系统/盘符级回退；`:70` 承接 | **闭合**（惟终止性出口见 R4-09） |
| P1-03 既存 scratch 输出与 Low MIC | 接受并收窄 | `:29` 只允许新建、精确登记且不存在的 output leaf；既有 `node_modules/`、`dist/`、`target/`、cache、temp、generated output 一律只读；设置 Low label 不重标既有子对象；**MIC 拒绝只证明 MIC 结果，不是 AppContainer/DACL 隔离通过证据**；不能建 fresh leaf 即 `BLOCKED` | **闭合**（措辞与 r3 要求逐项对应） |
| P2-01 `PYTHONUSERBASE` / user site | 采纳 | `:30` `PYTHONUSERBASE=<scratch>/python-cache/userbase` + `PYTHONNOUSERSITE=1` + 回读 `site.USER_BASE`/`site.ENABLE_USER_SITE`/`sysconfig`；`:119–120` 表内同值；`:110` 派生写路径出 scratch 即 `BLOCKED` | **闭合** |
| P2-02 负向 control 继承 / MIC 混淆 | 采纳 | `:31` 独立父链、父链与 control 均不改 label/policy、同一真实 token + 相同 `DesiredAccess` 的 DACL `AccessCheck` 与实际拒绝配对、MIC 型拒绝或非 `ERROR_ACCESS_DENIED` = `INCONCLUSIVE / BLOCKED` | **条件闭合**；精确路径缺失 → **R4-03** |
| P2-03 `AccessCheck` 字段 / 写权限 | 采纳 | `:32` 分列 BOOL return、`AccessStatus`、`GrantedAccess`、`GENERIC_MAPPING`、target owner、有效 `WRITE_DAC`/`WRITE_OWNER`、token 来源；任一赋权即使「不可写」降级为 `INCONCLUSIVE / BLOCKED`；`:106`「真实 protected-path 写入始终禁止」 | **闭合** |
| P2-04 一手来源不全 | 采纳 | `:39` 新增 `TOKEN_INFORMATION_CLASS`、Privilege Constants（`SE_CHANGE_NOTIFY_NAME`）、Well-known SIDs、Standard Access Rights、WebView2 固定版本部署；`:159` LocalDumps；`:153–159` 保留「仅 API 语义，不代表本机已实测」 | **闭合**（WebView2 页面中 SID 名称映射本会话未能抓取复核，见 §9） |
| P2-05 canary 根归属 | 采纳 | `:33` 所有 canary/control 相对 `G:\CODEX\P02-scratch-build-source`，主仓 `verification/P02/tmp/` 保持 deny | **根归属闭合**；表未同步 + 负向 control 无路径 → **R4-07 / R4-03** |
| P2-06 WER / dump 外写面 | 采纳 | `:34` 记录 `%LOCALAPPDATA%\CrashDumps`、`%ProgramData%\...\WER\ReportQueue`、`ReportArchive` 的存在性与文件名/长度/last-write time/file ID；**不打开、不读取、不哈希 dump 内容**；不属 digest exclusion；新文件/读取失败/无法解析目的地即 `BLOCKED`；并声明快照只是检测、不声称阻止容器外写入 | **闭合**（检测与「不读内容」双重要求均已写明） |
| P2-07 exclusion manifest 漂移 | 采纳 | `:35` digest 前建立并冻结 manifest（精确路径、理由、scope、开始时间、SHA-256）；冻结后新路径 = `UNKNOWN / BLOCKED`；未证实不存在前不得列 profile/private-registry 为允许新增 | **闭合**；但与 §8.4 的张力 → **R4-02** |
| P2-08 契约自带 SHA | 部分采纳 | `:36` 契约不自嵌 SHA；由 Codex 写入独立 prompt 与 checkpoint；DSH 无法复算时记 `NOT_VERIFIED` 且不得冒称 exact-hash Review | **闭合**（口径明确且与本次实践一致） |
| P3-09 特权 / 提权 | 采纳 | `:37` 不提权、不 take ownership、权限不足即 `BLOCKED`；`:17`、`:70` 一致 | **闭合** |
| P3-10 profile/storage 命名 | 采纳 | `:37` 声称三术语一致，但 `:148` 仍为 `profile folder/private storage` | **未完全闭合** → **R4-05** |
| P3-11 恢复后比较 | 采纳 | `:37` 恢复后重读并逐字段比较 file ID、owner/group、DACL ACE 集合、label/policy，漂移 = `CLEANUP_BLOCKED`；`:98`、`:148` 一致 | **闭合** |
| P3-12 表外对象只读 | 采纳 | `:37` 写入表外对象（含 tracked source）只读；`:76` 承接 | **闭合** |
| P3-13 `ERROR_ALREADY_EXISTS` / 残留 | 采纳 | `:37` 一律 `BLOCKED`，残留处置无新授权不得删除；`:46` 不复用/不覆盖/不删除 | **闭合** |
| P3-14 MIC 阴性证据 | 采纳但非当前执行授权 | `:37` 未来如能安全创建 profile 时作为独立证据；当前不运行 probe | **未完全闭合**（前置条件挂错，且与 §8.1 只读放行措辞冲突）→ **R4-06** |
| P3-15 sibling path 语义 | 采纳 | `:33` `G:\CODEX\New Manga.task-envs` 与 `.worktrees` 均为主仓兄弟目录；仅登记 task-env 子路径可只读、worktrees 全部 deny；`:103` 承接 | **闭合** |
| P3-16 moniker | 采纳 | `:37` 固定字面值、不派生不改写；`:44` 唯一实例、不随 HEAD 变动 | **闭合** |

**disposition 总评**：`r3 adjudication` 表格完整覆盖 19 个实际 finding ID（另含 C-00），并在 `:12` 如实指出 r3 报告「15」与 19 项 ID 的矛盾而未擅改历史计数——这一点值得肯定。r4 对 **16/19** 达到完全闭合，**3/19**（P2-05、P3-10、P3-14）为「方向正确但落地不完整」。

**同时确认的正面事实**（不构成 finding）：
- r4 未把 `AccessCheck` 当作可写性证据（`:106`、`:139`），未把 MIC 拒绝冒充 DACL/AppContainer 证据（`:29`、`:139`）。
- `DeleteAppContainerProfile` 的失败分支表述**忠实于文档**：官方页原文为「If the function fails, the status of the profile is undetermined, and you should call **DeleteAppContainerProfile** again to complete the operation」，与 `:148`「失败后状态不确定，可对同一 moniker 重试」一致。
- 官方页同时注明「Deleting a non-existent profile returns success」，因此 `:148`「删除后重测 profile folder/private storage 不残留；不空则 `CLEANUP_BLOCKED`」是对该返回值不可信性的正确处理，方向正确。

---

## 6. P1-01 的 fail-closed 充分性判定与权威文档核验

### 6.1 结论：充分 fail-closed，且比 r3 的建议更稳妥

r4 采取 `UNPROVABLE / BLOCKED` 并同时禁止三件事（猜 key / 调用可能创建或初始化 storage 的 API / 创建 profile），且声明「该 blocker 不被任何其他只读测量覆盖」（`:27`）。这是**可执行且不泄露写入**的 fail-closed 形态。补充理由：r3 P1-01 曾建议退路之一是「对私有 registry 存储做纯只读 `RegOpenKeyExW(KEY_READ)` 存在性查询」。但 `RegCreateKeyExW` 的官方 Remarks 指出，子键创建权是对**父键安全描述符**的检查、与取得句柄时使用的访问掩码无关，甚至以 `KEY_READ` 取得的句柄在安全描述符允许时**仍可创建子键**。因此「只读打开」本身不足以证明「无有效子键创建权或无副作用」，r4 放弃该路线、只保留 BLOCKED，比 r3 的建议方向更保守也更站得住。

### 6.2 本会话抓取的权威/官方文档核验结果

| 文档 | 核验到的事实 | 对 r4 结论的作用 |
|---|---|---|
| [`GetAppContainerRegistryLocation`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation) | 只定义「取得与 app container 关联的 registry storage 位置」「`phAppContainerKey` 收到**当前 profile** 的 storage 位置」「取得当前用户的 storage，取其他用户须 impersonation」；错误码仅列 `S_OK` 与 `E_INVALIDARG`（调用者未以可访问该 profile 的用户运行/impersonate）。**全文未给出具体键路径/registry view，也未说明目标 storage 不存在时是否创建/初始化或是否有任何副作用。** | **直接支持** r4 `:27` 的两点主张（缺精确 key/view、absent-state 副作用未定义） |
| [`Launch an AppContainer`](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer) | 只给出**文件夹**路径形态：`LOCALAPPDATA=C:\Users\<u>\AppData\Local\Packages\<moniker>\AC`、`TEMP`/`TMP` 同根下 `\Temp`；并明确「**LPAC cannot open any keys in the registry unless it has the registryRead capability**」，以及 LPAC 属性用 `PROC_THREAD_ATTRIBUTE_ALL_APPLICATION_PACKAGES_POLICY=PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT`（与 `:43` 一致）。**未记载任何 private registry 存储路径。** | **支持**；并印证 `:48`「运行进程不获 registry capability、容器内 registry 打开按预期否决」的口径有文档依据 |
| [`CreateAppContainerProfile`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile) | 「A profile contains folders and **registry storage** that are per-user and per-app」；`S_OK` = 「The data store was created successfully」；`ERROR_ALREADY_EXISTS` 仅在已存在时返回。**未给键路径/view，未说明 storage 与 profile 之外的其它 API 的副作用关系。** | **这是唯一可能支持另一种（更窄）结论的文档**：可读出「registry storage 由 profile 创建而产生」的暗示。但它既无路径、也不排除其它 API 的副作用、也不保证删除后无残留，**不足以**把「目标私有 registry 不存在」变成可证明项 |
| [`DeleteAppContainerProfile`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile) | 删除不存在的 profile 返回成功；失败后状态不确定、应再次调用；容器内调用返回 `ERROR_NOT_SUPPORTED`；须先关闭 profile storage 中所有文件句柄 | 支持 `:148` 的失败重试与「删除后必须重测残留」口径 |
| Microsoft Learn Q&A：[*Supported private-registry reference for an unchanged zero-capability LPAC caller*](https://learn.microsoft.com/en-us/answers/questions/6000195/supported-private-registry-reference-for-an-unchan)（外部人员 Moderator 答复） | 逐条答复：无法从已发布 Win32 文档确认零 capability LPAC 的该契约；未找到 LPAC 打开自身私有存储的 `registryRead` 例外；**无法确定该 API 返回的确切 registry view**；**文档未说明 storage 缺失时该函数是否创建/初始化/修改**；无法从 `KEY_READ` 单独证明无有效子键创建权 | **佐证** r4/adjudication 的判定。注意：这是 Q&A 答复，**非规范性文档**，不能单独作为权威依据；r4 选择只引用 API 页而非该 Q&A，是更稳的做法 |

### 6.3 是否存在权威文档支持其他结论

**未找到足以推翻 `UNPROVABLE / BLOCKED` 的权威文档。** 唯一可援引的相反方向是 `CreateAppContainerProfile` 的 Remarks（「profile 包含 per-user、per-app 的 folders 与 registry storage」，`S_OK` 表示 data store 已创建），它最多支持一个**更窄的替代提案**：「把可证明的 profile/local-data 目录不存在性当作 registry storage 不存在的代理证据」。该提案不成立，因为（a）无任何文档给出目标私有 registry 的键路径或 view，代理比对无对象；（b）`GetAppContainerRegistryLocation` 的 absent-state 副作用在官方文档中未定义，不能排除检查动作本身初始化 storage；（c）删除不存在的 profile 会返回成功，说明存储残留与 profile 存在性并非一一对应。因此 r4 的结论与公开一手依据一致。

### 6.4 但 fail-closed 的完整性受 R4-01 影响

fail-closed 的**方向与禁止项**充分；唯一可被绕过的缝隙是 §2 仍以强制语气要求证明第三项并调用 `GetAppContainerRegistryLocation`（R4-01）。修正该条后，P1-01 的 fail-closed 才算在文档内部完全闭合。

---

## 7. 是否仅允许「纯测量 OS preflight」

**是——当前仅允许无 profile、无 ACL/label/registry 修改、无真实写探针的纯测量只读 preflight，且该许可不等于任何更高授权。**

| 维度 | 判定 | 依据 |
|---|---|---|
| 纯只读测量 OS preflight（只读 DACL/label/owner/file ID/reparse 查询、只读存在性查询、只读 hash、WER 只读快照、`SeChangeNotifyPrivilege` 查询、token 字段查询） | **允许**（且须先经本轮 Review/处置，见 R4-04 对 §8.1 的修正要求） | `:144`（§8.1）、`:164`（§精确下一步 2）、`:175`；但 `:37`「任何 probe」措辞需按 R4-06 澄清 |
| 创建 profile / 调用 `CreateAppContainerProfile` | **禁止** | `:27`、`:45`、`:165` |
| 调用可能创建或初始化 private registry storage 的 API（含 `GetAppContainerRegistryLocation`） | **禁止** | `:27`；与 `:47` 冲突见 R4-01 |
| ACL / mandatory label / owner / registry 写入 | **禁止** | `:17`、`:29`、`:37`、`:96` |
| 真实写探针（正向 canary 新建文件、负向 DACL control 的真实拒绝、MIC 探针） | **禁止**（当前无 profile，且无写探针授权） | `:37`、`:99`（仅在 §4 前置与 Gate 满足后另议） |
| 删除/递归删除/覆盖任何对象 | **禁止**（仅未来可对同一 moniker 调用 `DeleteAppContainerProfile`） | `:148`、`:37` |
| Windows Sandbox 查询/安装/启用/启动、Smoke | **禁止** | `:19`、`Task:60` |
| build / Cargo / Tauri / PyInstaller / runner / Vitest / GUI / AC1–AC7 | **禁止** | `:19`、`Task:114` |
| 解除 Hard Build Barrier / 写 `Build Gate=PASS` | **不可能由本路径达成**：`private_registry_absence=UNPROVABLE / BLOCKED` 不被任何只读测量关闭 | `:27`、`:149`、`:165` |

**门禁状态未因本 Review 变动**：`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；`OS preflight=NOT_RUN`；`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`；`Build Gate=BLOCKED`；`build=NOT_AUTHORIZED / NOT_RUN`；`Hard Build Barrier=EFFECTIVE`；`AC1–AC7=BLOCKED / NOT_RUN`；`private_registry_absence=UNPROVABLE / BLOCKED`（未关闭）。

---

## 8. 允许与禁止的下一步

**给 Codex（Lead / Architect / Integrator）——单一可转发指令：**

> 请对 `verification/P02/appcontainer-isolation-contract-r4.md` 作**纯文档修订**（不创建 profile、不改 ACL/label/registry、不运行 probe/Sandbox/build/产品测试），保持 `profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`OS preflight=NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`、`private_registry_absence=UNPROVABLE / BLOCKED`：
> (1) 修正 3 项 P2：**R4-01** 在 `:45`/`:47` 加显式作废与交叉引用（P1-01 解除前不得执行该创建前检查、不得调用 `GetAppContainerRegistryLocation`）；**R4-02** 使 §8.4 的排除集以 §1.1.9 冻结 manifest 为唯一事实源，profile/private registry 在证实不存在前不得列为排除项，并把 canary 计数改为与 §4.5/§1.1.5 实际对象一一对应的精确路径；**R4-03** 显式命名负向 DACL control 的精确 leaf 并纳入 §4 输出表。
> (2) 处置 6 项 P3（R4-04…R4-09），每项给 closed 或显式 disposition：§8.1 的 Gate 主体从「r3」改为「本轮 r4」；§8.5 术语改为三固定词；`:37`「不运行任何 probe」改为「不运行任何写探针/MIC 探针」并解除 MIC control 对 profile 创建的错误前置；§4 表补 `verification/P02/tmp/` 行；§5 明确禁令主体为 LPAC 进程、controller 证据产出限于 `verification/P02/**`；§精确下一步补 P1-01/P1-02 不可解除时的用户裁决出口。
> (3) 复算并登记新候选 SHA-256 与字节数；**本轮 DSH 的 object binding 未成立**（本会话 `pwsh` 沙箱 `grantWrite(G:\CODEX\New Manga)` 在 4 种调用形态下均失败，升级重试因无审批通道被拒），故本报告只能作为**内容级**审查，不得作为 §8.1 / §精确下一步 2 所需的 exact-hash 通过凭证。请在具备可执行 shell 的环境安排一次 exact-hash 复算与只读复审，或明确记录「由 Codex 独立复算并显式接受内容级审查」。
> (4) 不改 P02 Owner allowlist、产品 AC、现有 scratch 输出 allowlist、Task 依赖、用户数据保护要求；不扩大任何路径授权。
> (5) 在修正与 exact-hash 复核完成前，**只**可进行 §7 表内「允许」一行的纯测量只读 preflight，且不得据此关闭 `private_registry_absence=UNPROVABLE / BLOCKED`。

**给用户**：当前**无需新授权**。唯一可能需要裁决的是 R4-09 描述的情形——若只读测量证明非提权 controller 无法读取系统对象 DACL 或系统未预置适用的 `S-1-15-2-2` ACE，则本机非提权 Codex-only 的 AppContainer 方向不可实施，届时应决定：放弃该方向 / 另行授权提权方案 / 接受 Build Gate 长期 `BLOCKED`。

---

## 9. 未覆盖范围与本报告限制

1. **对象绑定未成立**：四个绑定对象的 SHA-256、字节数、`main@cddff584…`/tree `c25d051a…` 均未复算。本报告全部结论绑定到「本会话实际逐行读取的该 4 条路径的内容形态（行数）」，不绑定任何 SHA、Git blob 或 tree。下游**不得**把本报告当作 exact-object 证据复用。
2. **未做任何 OS 状态测量**：未查询/创建/删除 AppContainer profile，未访问 registry，未读取任何 ACL/mandatory label，未运行 `GetNamedSecurityInfoW`、`AccessCheck`、token 查询、WER 快照或 hash 命令。本报告中**没有任何本机状态主张**。
3. **未读对象**：`appcontainer-isolation-contract-r2.md`、r2 DSH Review、`codex-appcontainer-contract-r2-adjudication.md`、`codex-scratch-build-process-isolation-scope-delta-r1.md`（Task:66/70 引用的 scope basis）、`WER`/HostFolder/R2 各类 manifest 与 checkpoint、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`dsh-preflight-version.txt`。因此对「r4 与 Task 的一致性」的核对只覆盖 `doc/tasks/P02.md` 全文，不覆盖 Task 所引用的外部 scope 文档。
4. **未复核 r4 引用的历史数值**：`:6` 的 r2 契约/Task 复算值、`:7` 的 r3 计数、各处 session/exit/环境版本声明，均按「未复核的历史声明」处理。
5. **文档来源核验缺口**：`S-1-15-2-2` = `ALL RESTRICTED APPLICATION PACKAGES` 的字面映射，本会话未能从抓取到的页面直接复核（Learn 检索 API 未返回含该短语的有效片段）；`web_search` 通道因 401 不可用，仅使用 `web_fetch` 与 Learn 检索 API，覆盖面有限。`WebView2 固定版本部署` 页面中「列出 `S-1-15-2-2` 访问要求」的主张（`:39`）同样未直接抓到原文。这两项建议在具备检索能力的会话中另行复核。
6. **本报告无任何 Gate 效力**：不构成 profile 创建、ACL/label/registry 修改、Smoke、build、AC1–AC7 的批准，不解除 P02 Hard Build Barrier，不改变任何历史 finding 计数。

*报告结束。本报告为只读审查产物。*