・ Reviewer 已完成全部只读核验。以下为报告全文（本工具调用捕获 stdout；我未创建/修改/删除任何文件）。

---

# P02 AppContainer 隔离契约 r2 · 独立只读 Review（DSH，非作者）

- Reviewer：DeepSeek Harness（非作者；Codex 未实现此设计，本报告只审文档）
- 审查对象：`verification/P02/appcontainer-isolation-contract-r2.md`（131 行）
- Task 绑定段：`doc/tasks/P02.md:68-70`（`2026-10-10 本轮 PROJECT_ORCHESTRATION_AUTHORIZATION：AppContainer 精确隔离范围`）
- 日期：2026-10-10（Asia/Shanghai）
- **decision = `NOT_VERIFIED`**（对象 hash 无法在本会话独立核验；内容层面等价于 `CHANGES_REQUESTED`，见 §5）

---

## 0. 结论摘要

| 项 | 结果 |
|---|---|
| 审查内容 1（授权仅作许可登记、保留全部 Gate 状态） | **PASS** |
| 审查内容 2（moniker 字面/长度/生命周期/前存在性/cleanup） | 基本成立，方法未定义 → R2-01/R2-02/R2-03 |
| 审查内容 3（LPAC opt-out/零 capability/重定向/环境表/权限假设） | 方向与 API 名称正确；**强制完整性缺失 → P0**；权限假设未闭合 |
| 审查内容 4（RO 根精确复用、RW 受限、deny 清单、祖先/reparse/ADS/继承） | RO/RW 清单**精确复用**；**祖先 ACE 与 deny 声明冲突 → P0**；ACL 变更无还原 → P1 |
| 审查内容 5（AccessCheck + 写探针） | 拒绝侧保守可用；**正向可写不可证**（MIC）→ P0/P1 |
| 审查内容 6（Job/no-breakaway/句柄/短命进程/PID 复用） | 设计总体可执行；执行通道细节缺失 → P2 |
| 审查内容 7（System32 loader 闭包无宽兜底） | **当前不是可实施的精确范围** → P1 |
| 审查内容 8（Microsoft 一手论据准确性） | 引用的 5 条 API/LPAC 论据均可被一手文档证实；调用上下文与清理语义不准确/不完整 |
| 发现计数（内容） | **P0=2，P1=5，P2=8，P3=7（共 22 项）** |
| 另有验证能力发现 | `C-00`（P0 级阻断，非契约内容缺陷） |
| 能否进入"无 profile 创建的只读 OS preflight" | **否**（按 r2:130 自设规则：存在未解决 P0/P1） |
| Gate 影响 | **无任何提升**。Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`、profile=`NOT_CREATED`、隔离预检=`NOT_RUN` |

---

## 1. 实际能力与对象绑定

### 1.1 本会话实际能力（必须先行声明）

| 能力 | 状态 | 原文/证据 |
|---|---|---|
| `pwsh` 工具 | **不可用（初始化即失败）** | `Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`；更换 workdir、更换命令、独立子代理复现均相同 |
| 沙箱升级 | **不可用（fail closed）** | `Error: sandbox escalation to "danger-full-access" requires approval, but no approval channel is available` |
| SHA-256 / 字节数 / `git status` 复算 | **不可用** | 依赖 shell |
| `web_search` | 不可用 | `DeepSeek API error (HTTP 401)` |
| `web_fetch` | **可用** | 成功取回 10 个 Microsoft Learn 页面（见 §7） |
| 文件读取（`read`/`glob`/`grep`） | **可用** | 本报告全部静态结论基于逐行读取的实际字节 |

**能力结论**：本会话**无法独立计算任何文件 hash、字节数与 workspace porcelain 状态**。这与项目中此前 DSH Review 的既有环境限制一致（例：`verification/P02/dsh-review-p02-preflight-r4.response.md:41` 记录 DSH 受限 shell 无法复算 manifest）。

### 1.2 对象绑定核验（尽力而为）

| 绑定项 | 声明值 | 本会话实测 | 判定 |
|---|---|---|---|
| 仓库 Root | `G:/CODEX/New Manga` | 路径存在，审查对象均在该路径下 | 成立 |
| branch | `main` | 读取 `.git\HEAD` 原始字节 = `ref: refs/heads/main` | **成立**（直接读 Git 元数据，非 CLI） |
| base HEAD | `cddff58469b56e181019a8ddfeade80684bc7eb9` | 读取 `.git\refs\heads\main` 原始字节 = 同值 | **成立** |
| 契约 SHA-256 | `8D84DA22…DE6963` | **UNAVAILABLE（无法计算）** | **不可核验** → C-00 |
| Task SHA-256 | `4915CE24…D2F7A3` | **UNAVAILABLE（无法计算）** | **不可核验** → C-00 |
| workspace dirty 状态 | "含原作者未提交内容" | **UNAVAILABLE**（`git status` 无法运行） | 不可核验（不影响内容审查） |
| 契约存在/形态 | docs-only | 存在于精确路径，全文 131 行，状态行 `隔离预检=NOT_RUN / profile=NOT_CREATED` | 成立 |
| Task 存在/形态 | 366 行 | 存在；绑定段位于 **第 68–70 行**，字面标题与 prompt 一致 | 成立 |

**旁证（非独立核验）**：契约 SHA 字面量同时出现在 Codex 自撰的 `verification/P02/codex-checkpoint-autonomous-orchestration-20261010.md:13`。这只能证明"Codex 记录的值与派发 prompt 一致"，**不构成独立复算**。Task SHA 字面量仅见于派发 prompt（`dsh-appcontainer-contract-r2-review.prompt.md:8`），**无任何 checkpoint 旁证**，故 Task 的对象绑定本会话完全不可核验。

### 1.3 报告落盘路径

派发请求建议的路径为 `verification/P02/appcontainer-isolation-contract-r2-review.stdout.md`；**实际 harness 捕获路径为 `verification/P02/dsh-appcontainer-contract-r2-review.stdout.md`**（审查开始时该文件存在且为 0 字节，`.stderr.log` 为同类运行日志）。引用本报告时应使用实际捕获路径（→ R2-20）。

### 1.4 只读声明

本会话未创建、修改、删除、stage 或 commit 任何文件；未创建/查询/删除 AppContainer profile；未改 ACL/registry；未运行 host/process probe、Sandbox、Smoke、Build、Cargo、Tauri、PyInstaller 或产品测试；未读取任何被保护用户数据样本。读取范围仅限：上列审查对象、`.git/HEAD`、`.git/refs/heads/main`、两个 checkpoint 与派发 prompt，以及公开 Microsoft 文档。stdout 落盘由 harness 完成，非本 Reviewer 的写操作。用户授权**未被**本报告当作任何 Gate/Test 通过证据。

---

## 2. 审查内容逐项判定

| # | 判定 | 关键依据 |
|---|---|---|
| 1 | **PASS** | r2:6 状态台账完整保留 `Build Gate=BLOCKED / build=NOT_AUTHORIZED / NOT_RUN / Hard Build Barrier=EFFECTIVE / AC1–AC7=BLOCKED / NOT_RUN`；r2:10 明确"不是任何 Test、Review 或 Gate 的 PASS 证据"；r2:12 明确授权不改变 r1 设计 Review 的 `NOT_VERIFIED`；r2:118 明确"当前绝不解除 Hard Build Barrier"；Task:70 同口径（"此授权是 scope 许可，不是测试或 Gate 通过凭证"）；`codex-checkpoint-autonomous-orchestration-20261010.md:13-15` 一致。**无 Gate 提升、无 PASS 假声明。** |
| 2 | 基本成立 | moniker `NewManga-P02-LPAC-20261010-cddff584`：35 字符 ≤ 64，字符集 ⊂ `[-_. A-Za-z0-9]+`，**合规**（doc 证实）；单次生命周期、只删本轮新建的 exact profile、`CLEANUP_BLOCKED` 保留现场均已写入。缺口：前存在性"证明方法"未定义、私有注册表确切键路径未列（R2-01）、moniker 非字面冻结（R2-02）、Delete 语义未对齐文档（R2-03） |
| 3 | API 名称正确，可行性假设未闭合 | `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES`、`PROC_THREAD_ATTRIBUTE_ALL_APPLICATION_PACKAGES_POLICY=PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT`、`internetClient`/`privateNetworkClientServer`/`registryRead`/`lpacCom`、`LOCALAPPDATA=…\Packages\<moniker>\AC`、`TEMP=TMP=…\AC\Temp`、双 SID 交集 — **逐项被一手文档证实**。但**强制完整性（Low IL / MIC）完全缺失 → R2-04（P0）**；`GetAppContainerFolderPath`/`GetAppContainerRegistryLocation` 调用身份未定义（R2-05）；6 项权限/身份假设不可核验（§3.4） |
| 4 | RO/RW 精确复用 ✓；闭包有 P0 洞 | RO 表 12 行与 `codex-scratch-build-preflight-hostfolders-r1.tsv` 的 12 个路径**逐字符一致**；RW 清单 12 行与 `P02.md:74-77` **逐项一致**（含 `npm-cache/`、`cargo-home/`、`tmp/`、`python-cache/`、`pyinstaller-config/`）；`P02.md:70` 的禁止清单（主仓/`.worktrees`/漫画库/数据库/Lock/current/pinned/凭据/全局缓存）在 r2:70 完整保留。缺口：**祖先"traverse/read-execute"与 deny 声明内部冲突 → R2-10（P0）**；ACL 变更范围未登记且无 DACL 还原 → R2-11；路径匹配语义 → R2-12；TSV 现状冲突 → R2-13；tracked 文件约束与 Task:81 冲突 → R2-14 |
| 5 | 拒绝侧保守可用；正向侧不可证 | r2:72 只对 scratch canary 做真实创建、对用户/主仓只用 DACL/AccessCheck 拒绝证明并禁止读取样本 — **方向正确**。缺口：AccessCheck 的 token 与语义未定义（R2-15）、canary 语义与 Task:79 冲突（R2-16）、前后 hash 覆盖过度声明（R2-17） |
| 6 | 大体可执行 | r2:107-110：挂起创建→入单一 Job→resume；kill-on-job-close；不授 breakaway；全部后代须同 job/同 Package SID；process-create/exit + Job 通知捕捉短命进程；按 creation time 区分 PID 复用；无法采集 ⇒ `UNKNOWN` 并停止；无项目代码的首轮 synthetic parent→child→grandchild probe — **均为可执行的 fail-closed 设计**。缺口：事件通道/权限/句柄表细节 → R2-18 |
| 7 | **不是可实施的精确范围** | r2:45 要求逐文件前置解析且明令禁止宽路径兜底（正确拒绝"整个 Windows 目录"化解）；但未给**授予主体/权限/继承/回滚**，也未给可实施程序，且集合本质动态、系统文件属 TrustedInstaller → R2-19（P1） |
| 8 | 一手论据准确；调用上下文与清理语义不准确 | 4 个 API 页 + 2 个 LPAC 页的引用语义**全部可证实**（详见 §7）；不准确/不完整处：`GetAppContainerFolderPath`/`GetAppContainerRegistryLocation` 的"当前 profile/当前 token"语义（R2-05）、`DeleteAppContainerProfile` 的"删除不存在返回成功/失败应再次调用"（R2-03）。§Microsoft 一手资料 标题写"核验"，实为 owner 侧引用核对（R2-20） |

---

## 3. Findings

### 3.1 验证能力

#### C-00 — 契约与 Task 的对象绑定无法独立核验
- **级别**：**P0（验证能力；非契约内容缺陷）**
- **路径/条款**：`verification/P02/appcontainer-isolation-contract-r2.md`（对象身份）；`doc/tasks/P02.md`（对象身份）
- **影响**：无法证明被审字节与 prompt 声明的 `8D84DA22…DE6963` / `4915CE24…D2F7A3` 同一；因此本报告的全部内容结论**绑定到"我在本会话逐行读取到的该两个路径的文件内容"**，不绑定到任何 SHA-256、Git blob 或 tree。下游不得把本报告的绑定关系当作 exact-object 证据复用。
- **最小修正**：在具备可执行 shell 的环境（或修复本 workspace 沙箱 `grantWrite` 失败）复算两文件的 SHA-256 与字节数；与 prompt 值一致则将本报告的对象绑定条款替换为复算记录，不一致则按 prompt 报 `BLOCKED / hash mismatch`。

### 3.2 审查内容 2

#### R2-01 — "创建前证明不存在"缺方法；私有注册表确切位置未列
- **级别**：**P2**
- **路径/条款**：r2:17（条款 2）、r2:19-20
- **影响**：(a) `DeriveAppContainerSidFromAppContainerName` 对任意合法 moniker **恒可派生**，"SID 对应存储不存在"不是可检验命题；契约未定义用哪些只读检查证明"profile/目录/私有注册表均不存在"（可读候选：`%LOCALAPPDATA%\Packages\<moniker>`、该 profile 的 AppContainer registry `Storage` 键），因此"查验方法不能证明不存在即停止"这句 fail-closed 目前**无落点**。(b) 契约只说"私有注册表由 `CreateAppContainerProfile` 作为 profile 状态创建"，未列出确切键路径，也未说明该存储位于**当前用户自己的 hive 内**（即一次真实 host-state 写入），F-03/D-1 的"路径级"要求只部分闭合。
- **最小修正**：写死三项检查及其 API/注册表位置（moniker→目录、profile local-data 根、私有注册表键路径），并声明三者的 before/after 存在性 manifest；写明该键位于当前用户 hive 内、由 Delete 一并移除。

#### R2-02 — moniker 非字面冻结；残留 profile 无恢复路径
- **级别**：**P3**
- **路径/条款**：r2:17（"派生自本契约记录的主仓 HEAD"）；对照 `P02.md:70` 冻结的 `Profile identity=NewManga-P02-LPAC-20261010-cddff584`
- **影响**：若 base HEAD 变更后按规则重新派生，会与 Task 冻结身份不一致；反之为确定性命名，一次失败遗留的 profile 会**永久阻断**该 moniker（无随机后缀），而契约未登记恢复路径。
- **最小修正**：声明 moniker 为**字面冻结值**（不随 HEAD 重派生，变更须新增授权登记）；登记残留 profile 的唯一恢复路径（同一契约下由同一 controller 走 `DeleteAppContainerProfile`）。

#### R2-03 — Delete 语义未对齐文档；缺"残留为空"断言
- **级别**：**P3**
- **路径/条款**：r2:115、r2:117（条款 4）、r2:124
- **影响**：一手文档明确 (a)"删除不存在的 profile 返回成功"、(b)"失败后状态不确定，**应再次调用 `DeleteAppContainerProfile` 以完成操作**"。r2:115 只写"不得尝试其他清理办法"，未区分**重试 Delete**（文档建议）与**递归/通配删除**（禁止），实现者可能把合法的重试也判为越界；同时契约未要求删除后"目录/键/私有存储残留为空"的正向断言，F-07 的清理闭环只做了一半。
- **最小修正**：写明"允许且仅允许对同一 exact moniker 重试 `DeleteAppContainerProfile`；禁止任何目录级递归/通配删除"，并加删除后残留为空断言（失败即 `CLEANUP_BLOCKED`）。

### 3.3 审查内容 3

#### R2-04 — 强制完整性（Low IL / MIC）完全缺失：scratch 写入与正向 canary 按现文不可实现
- **级别**：**P0**
- **路径/条款**：r2:20、r2:49、r2:66、r2:72、r2:81（`TEMP/TMP`）、r2:116
- **影响**：一手文档给出三条决定性事实：①"if you _are_ in an app container, then the integrity level (IL) is always _low_"；②"a principal with a low integrity level **cannot write** to an object with a medium integrity level, **even if that object's DACL allows write access**"；③"By default, the system creates every object with an access mask of `SYSTEM_MANDATORY_LABEL_NO_WRITE_UP`"、"Objects that lack an integrity label are treated as medium"。因此：**controller（medium IL）创建的任何 scratch 目录/文件都是 Medium + NO_WRITE_UP，LPAC（Low IL）对其一律不可写**，即使 r2 正确授予了 Package SID 的写 ACE。这直接推翻 r2:49 的"缺失目录由 controller 按需创建"、r2:57-64 的 scratch RW 清单，以及 r2:66 的"唯一正向写入 canary"（该 canary 会以 `ERROR_ACCESS_DENIED` 失败，但原因不是隔离失效）。同理，profile 内 `AC`/`Temp` 的实际标签必须**被证明**为 Low（文档未承诺 `CreateAppContainerProfile` 会把标签降到 Low，这属未核验假设）。另：标签 SID 存放在 **SACL** 中，而 r2 只在 r2:72 把 SACL 当作拒绝证明输入，未把它纳入写入前置条件与前后 manifest。
- **最小修正**：(1) 把"每个读/写目标的强制标签 + mandatory policy"列为**写入前置条件**并逐对象登记；(2) 要求 scratch 写目标处于 Low 标签（或显式、可逆地降标签），并记录原始标签；(3) 记录 LPAC token 的 `TokenIntegrityLevel`/`TokenMandatoryPolicy`；(4) 声明"未设标签/Medium + NO_WRITE_UP ⇒ 写入必然被拒"，并把它写成 `BLOCKED` 条件之一；(5) 若无法在非提权下变更标签，则本契约的 scratch RW 与正向 canary 设计**必须重构**（例如让 LPAC 在自身 profile 树内落盘，或放弃该正向控制）。

#### R2-05 — 两个"唯一来源"API 的调用身份未定义
- **级别**：**P2**
- **路径/条款**：r2:19（"`GetAppContainerFolderPath(PackageSID)`…该 API 返回值是唯一允许的 profile 路径来源"）、r2:20（"外部 controller 通过 `GetAppContainerRegistryLocation`…"）
- **影响**：一手文档写的是**当前身份语义**——`GetAppContainerFolderPath`："If a thread token is set, this function uses the app container for the current user. If no thread token is set, this function uses the app container associated with the process identity"，且"与 `SHGetKnownFolderPath(FOLDERID_LocalAppData)` 同值"；`GetAppContainerRegistryLocation` 无 SID 入参，取"**the current profile**"的存储，`E_INVALIDARG` = "The caller is not running as or impersonating a user who can access this profile"。外部、非 AppContainer 的 controller 是否符合上述前提**未定义**；而 r2 同时禁止猜路径，等于把路径获取建成一个可能不可执行的唯一通道。
- **最小修正**：写死调用上下文（impersonate 该 profile 的 token，或由 profile 内进程回读并回报），并定义失败/返回路径超出 `%LOCALAPPDATA%\Packages\<moniker>` 时的 `BLOCKED` 行为。

#### R2-06 — 环境/API 细节未写死（token 字段、CreateProcess flags、OS build pin）
- **级别**：**P3**
- **路径/条款**：r2:109（"`TokenIsAppContainer`、LPAC 标志"）、r2:16、r2:114
- **影响**：契约其余部分要求"exact"，但关键证据字段仍用泛称"LPAC 标志"。可核验的一手名称是 `TokenIsLessPrivilegedAppContainer`（`TOKEN_INFORMATION_CLASS`，winnt.h），另有 `TokenAppContainerSid`、`TokenCapabilities`、`TokenIntegrityLevel`、`TokenMandatoryPolicy`、`TokenRestrictedSids`。另：AppContainer/LPAC 启动样例固定使用 `EXTENDED_STARTUPINFO_PRESENT` flag，r2 未写；r1 F-08 要求的"固定 OS build + 架构 pin"与"被测进程回读 TEMP/TMP/LOCALAPPDATA 断言"也未落地（r2:76 只要求 controller 侧保存/校验）。
- **最小修正**：逐项点名 token information class 与所需 `TOKEN_QUERY` 权限、写明 `CreateProcess` flag 集合、加入 OS build/架构 pin 与被测进程回读断言。

#### R2-07 — 残余派生缓存锚点未列举
- **级别**：**P3**
- **路径/条款**：r2:78-101 环境表、r2:103
- **影响**：r1 F-04 点名的四个审计变量均已覆盖（`PYINSTALLER_CONFIG_DIR`/`TORCH_HOME`/`XDG_CACHE_HOME`/`HF_*`+token），并有"未登记变量/越界展开即阻断"的总兜底；但 venv 内实际存在 Transformers 等包，`TRANSFORMERS_CACHE`、`PIP_CACHE_DIR`、`TORCH_EXTENSIONS_DIR`、`XDG_DATA_HOME`、`UV_CACHE_DIR`、`PYTHONUSERBASE` 等可派生锚点未列举，仍依赖"工具不会自行派生"这一未经实测的假设。
- **最小修正**：补齐（或显式声明"未设置即视为不得派生，任何派生路径出现在登记集合外即 `BLOCKED`"并给出检测方法）。

#### R2-08 — 零 capability 的预期后果未作为结论登记
- **级别**：**P3**
- **路径/条款**：r2:16、r2:109、r2:118
- **影响**：一手文档明确"LPAC **cannot open any keys in the registry** unless it has the _registryRead_ capability and cannot use COM unless it has the _lpacCom_ capability"，且 LPAC 的文档定位是"a process running with no rights to any resources except what you explicitly grant（例如浏览器对子 worker 进程的沙箱）"。零 capability 下真实 PyInstaller/Torch/Transformers 闭包**大概率不可满足**（与文件 ACL 是否满足无关）。r2 的 fail-closed 处理正确，但没有把这一高概率结果写成预期结论与 Gate 语义，读者可能仍默认"能跑"。
- **最小修正**：在 §当前结果 或 §阻断条件 中显式登记：缺少 `registryRead`/`lpacCom` 时任何注册表打开/COM 激活失败 ⇒ 立即 `BLOCKED`，且这属于**预期**结果，不得据此放宽 capability。

#### R2-09 — "默认否决"缺 Gate 级证据与探针设计
- **级别**：**P2**
- **路径/条款**：r2:16、r2:118（Build Gate 证据清单）
- **影响**：r2:118 列举的 Gate 证据为"隔离身份、Protected-path denial、scratch positive write、TEMP/cache 重定向、完整 process tree、before/after hashes、hook/cache closure"，**不含** capability/网络/注册表/COM 否决证据；而"零 capability"恰是这套隔离的核心声明之一。结果是：能力面只有设计依据，没有任何可复核的负向证据路径（r1 F-05 未闭合）。
- **最小修正**：把 ≥3 项 OS 级负向证据纳入 Gate 证据清单（出站 TCP/DNS 被拒、`RegOpenKeyEx` 被拒、`CoCreateInstance` 被拒），并附 `TokenCapabilities` 空集快照。

### 3.4 本会话无法核验的 Windows 权限/身份假设（r2 未闭合）

| # | 假设 | 现状 |
|---|---|---|
| A1 | 非提权 controller 可成功 `CreateAppContainerProfile` / `DeleteAppContainerProfile` | 文档仅列 `E_ACCESSDENIED` 为可能返回值，**未给权限要求**；r2:18 直接断言"非提权" |
| A2 | 非提权可对 `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`、`E:\Program Files\nodejs`、`C:\Program Files\Git\mingw64` 等写 DACL | 需 WRITE_DAC/所有权；文档与 r2 均未论证 |
| A3 | 非提权可对系统文件（`C:\Windows\...`，TrustedInstaller 拥有）写 DACL | 同上，且可能需改所有权 |
| A4 | 非提权可设置/清除对象强制标签（SACL） | SACL 写入通常需 `SeSecurityPrivilege`；r2 未提 |
| A5 | Windows 是否已为 `ALL RESTRICTED APPLICATION PACKAGES`（`S-1-15-2-2`）在 System32/loader 路径预置 ACE | 决定"是否必须逐文件改系统 ACL"；**必须只读实测，不得假设**（文档只说 LPAC 不享受 `ALL_APPLICATION_PACKAGES` 隐式授权） |
| A6 | 外部非 AppContainer 调用者能从 `GetAppContainerFolderPath`/`GetAppContainerRegistryLocation` 得到本 profile 的路径/键 | 见 R2-05 |
| A7 | LPAC token 是否持 `SeChangeNotifyPrivilege` | 决定祖先目录是否**必须**放 ACE（见 R2-10） |

以上均应作为只读 preflight 的**测量项**或一手文档闭合项；在闭合前，r2 中依赖它们的条款属未验证假设。

### 3.5 审查内容 4

#### R2-10 — 祖先 "traverse/read-execute" 与 deny 声明内部冲突；继承标志与权限掩码未约束
- **级别**：**P0**
- **路径/条款**：r2:24（"祖先最多授予必要的 traverse/read-execute"）对照 r2:70（"尤其禁止主仓 `G:\CODEX\New Manga`、所有 `.worktrees`、…、AppData 中既有应用数据、用户文件…的读取和写入"）
- **影响**：(a) 在 Windows 上，对 `C:\Users\49745` 或 `G:\CODEX` 授予 read-execute 就是允许 LPAC **列举**这些被禁目录（`FILE_LIST_DIRECTORY`），与 r2:70 的"无读取"声明直接冲突；(b) 常见实现（`icacls /grant`）默认带 `(OI)(CI)` **继承**标志，若祖先用了继承 ACE，读权限会传播到整棵子树——包括主仓、其他项目 clone、用户资料，deny 清单在 ACL 层面**无法按路径反向抵消**；(c) r2 未约束 ACE 的精确 access mask（应仅 `FILE_TRAVERSE`，而非 generic READ）、未要求非继承（"this folder only"）、未处理 `SeChangeNotifyPrivilege`（token 若持有该特权则祖先**根本不需要** ACE）；(d) 契约又要求"祖先最多授予必要的 traverse/read-execute"，等于为越权开了口子。
- **最小修正**：改为 (1) 先记录 LPAC token 是否持 `SeChangeNotifyPrivilege`；持有时祖先**零 ACE**；(2) 必须放 ACE 时只允许 `FILE_TRAVERSE`（0x20）、**非继承**、且必须逐条列出该 ACE 并证明它不授予目录枚举/读数据；(3) 明令禁止在任何被禁路径的祖先上使用可继承 ACE；(4) 把"祖先 ACE 掩码/继承标志不符预期"写成 `BLOCKED`。

#### R2-11 — ACL 变更集合未登记；无 DACL/标签还原；非提权下不可实施
- **级别**：**P1**
- **路径/条款**：r2:10（授权覆盖项）、r2:24、r2:114、r2:117
- **影响**：(a) r2:10 把授权覆盖范围写成"profile 生命周期、私有数据/注册表状态、精确 scratch 输出路径、隔离预检与 OS 证据采集"——**未包含**"对只读输入根/祖先/系统文件添加 Package SID ACE"这一持久 host-state 变更；Task:70 的路径集合也只是"精确只读输入根 + scratch 输出子目录 + profile 根/Temp"，**不含祖先与 `C:\Windows\...`**。(b) 清理条款只讲删除 profile，**全程没有**要求采集→还原原 DACL（及标签），而 ACE 一旦写入即持久存在。(c) 其中 4 个 RO 根位于 `Program Files`/`E:\Program Files`，系统文件属 TrustedInstaller：**非提权 controller 无法写这些对象的 DACL**，因此 r2:24 的核心机制在"非提权"前提下不可实施（A2/A3）。
- **最小修正**：把"ACL/标签变更集合"独立登记为本轮 host-state 写入范围（逐对象 + 精确 ACE + 继承标志），要求运行前保存每个被改对象的原始 DACL/标签与所有者、运行后逐对象还原并断言一致；并先用只读查询证明 controller 对每个目标具备 `WRITE_DAC`/标签写入权限，任何一项不具备即 `BLOCKED`（不得提权、不得改址）。

#### R2-12 — 路径/别名匹配语义未定义（含仓库根前缀家族）
- **级别**：**P2**
- **路径/条款**：r2:24（"不得使用父盘符/用户目录/仓库通配符作授权"）、r2:70（"所有 `.worktrees`"、"主仓 `G:\CODEX\New Manga`"）
- **影响**：(a) deny 项 `G:\CODEX\New Manga` 是 **`G:\CODEX\New Manga.task-envs`（本契约的 RO 输入根！）与 `G:\CODEX\New Manga.worktrees` 的字面前缀**；未定义匹配语义（组件边界、尾分隔符、大小写不敏感、规范化、8.3 短名、UNC/`\\?\`、junction 解析）会让 allow 与 deny 的判定随实现而变。(b) `.worktrees` 是简称而非精确绝对路径（实际为 `G:\CODEX\New Manga.worktrees\...`），不满足 r2 自身的"精确路径"标准。(c) hardlink/ADS 只有"与预期不符即停止"这句原则，未给检测方法（`fsutil hardlink list` 在 18 万+ 文件上的成本、ADS 需 `FindFirstStreamW` 枚举）与覆盖范围；"整段祖先无 … hardlink 别名"对目录不成立（目录不能建硬链接）。
- **最小修正**：写死规范化与匹配规则（大小写不敏感、组件级、尾分隔符、拒绝短名/UNC/未解析 reparse），把 `.worktrees` 换成精确绝对路径清单，明确 `G:\CODEX\New Manga.task-envs` 与 `G:\CODEX\New Manga.worktrees` 是**独立兄弟组件**、不受仓库根 deny 影响，并给出 hardlink/ADS 的枚举方法与成本上限。

#### R2-13 — 只读输入清单的 scratch clone 现状与 r2 冲突
- **级别**：**P2**
- **路径/条款**：r2:5、r2:43、r2:114（"12 个 HostFolder…任一 UNKNOWN/MISMATCH 均停止"）对照 `codex-scratch-build-preflight-hostfolders-r1.tsv:2`
- **影响**：TSV 第 2 行把固定 scratch clone 记为 `expected=ABSENT / exists=False / match=True`（该行是 WSB HostFolder 时代的"预期不存在"快照）；而 r2:5/:43 把它当作**已存在**的只读输入根，`P02.md:100` 也已记录 clone 已按四条命令创建并通过（HEAD=`7ce3c40c`、tree=`ce8056b8`、clean）。若按 TSV 字面复核"12 个 HostFolder"，当前状态必然判 `match=False` → 触发 r2:114 的停止。契约未指明该 TSV 哪些行/列仍是 normative。
- **最小修正**：声明 TSV 的 normative 范围（哪些列用于比对），并单独固定 scratch clone 的期望状态（PRESENT + HEAD/tree/clean/remote=∅/alternates=∅/hardlink count=1），或重新采集一份 inventory。

#### R2-14 — "tracked 文件均只读"与写入表及 Task:81 冲突
- **级别**：**P2**
- **路径/条款**：r2:66 对照 r2:57-58（写入表第 5/6 行：`gen/schemas/`、`permissions/autogenerated/`）与 `P02.md:81`
- **影响**：Task:81 明确"`gen/schemas` 和 `permissions/autogenerated` 中**已跟踪文件**可以在 scratch 内按 Gate 明列的生成结果变化；执行前记录 Git blob 与原始字节 hash，仅接受目录 allowlist 中的实际生成差异，**其他 tracked 源码变化即阻断**"。r2:66 却笼统写"tracked 文件…均只读"，与该表自相矛盾；同时**未承接**"记录 Git blob + 原始字节 hash"与"其他 tracked 变化即阻断"这两条约束（r2:114-117 只覆盖主仓保护清单与 scratch 输入）。
- **最小修正**：把 r2:66 收窄为"写入表之外的对象（含 tracked 源文件）只读"，并原文承接 Task:81 的两项约束与阻断条件。

#### R2-22 — 跨容器写入面（WER/崩溃转储）未登记
- **级别**：**P2**
- **路径/条款**：r2:49、r2:116-117（"除显式 scratch/profile 输出外…"）
- **影响**：崩溃转储/Windows 错误报告由**容器外的服务进程**写盘，不受 LPAC 的 Package SID ACL 约束；一旦构建中的进程崩溃，落盘路径可能是用户 `CrashDumps` 或 `ProgramData` 下的 WER 目录，此时"唯一写入面 = profile + scratch"的声明不成立（r1 F-12 未闭合）。
- **最小修正**：把 WER/崩溃转储路径显式登记为两类之一：(a) 预期外 `BLOCKED` 条件并纳入前后 manifest 检测；或 (b) 显式接受并给出精确位置、清理责任与检测方法（只读检查 WER `LocalDumps` 配置，不做注册表写入）。

### 3.6 审查内容 5

#### R2-15 — AccessCheck 证据设计不完整（缺 token、缺 MIC 语义、缺配对对照）
- **级别**：**P1**
- **路径/条款**：r2:72（"Package SID effective access（Windows `AccessCheck`）"）、r2:118
- **影响**：(a) `AccessCheck` 的入参是 `ClientToken`（**impersonation token handle，需 `TOKEN_QUERY`**）、`GenericMapping`、`DesiredAccess`（须先经 `MapGenericMask`）、`PrivilegeSet`——**不接受裸 Package SID**；r2 未定义被检 token 的来源/生命周期（LPAC 进程退出后即失效）。(b) MIC 文档明确"**evaluates access _before_ access checks against an object's DACL are evaluated**"，而 `AccessCheck` 只按 DACL 判定：因此"AccessCheck 判拒"对**拒绝**方向是保守的、可用的；但"AccessCheck 判允"**不能**证明可写（真实内核检查更严），r2 必须禁止用其反证正向可写。(c) 缺探针有效性对照（r1 F-15）：建议在 scratch 内构造一个显式拒绝 Package SID 的对象，用**同一 API、同一 DesiredAccess** 做真实写尝试并期望被拒，与允许对象配对。
- **最小修正**：写死 token 采集方式与 context、`GENERIC_MAPPING`/`DesiredAccess`/`PrivilegeSet` 记录字段，声明"AccessCheck = DACL-only，早于 MIC 的判定不在此函数内"并限定其结论方向（只用于拒绝），并加入配对对照。

#### R2-16 — canary 语义与 Task:79 冲突（同一对象同时是 PASS 与 BLOCKED 判据）
- **级别**：**P1**
- **路径/条款**：r2:66（"唯一**正向写入** canary 为 Task 已列的 `verification/P02/tmp/smoke-readonly-probe/` 下本轮唯一新文件；**执行成功后**保留该文件及 hash"）对照 `P02.md:79`（"Smoke 的**只读** canary alias…**若只读 alias 写入成功**，文件只留在该 scratch 目录并**记为 BLOCKED**"）
- **影响**：同一路径在两份生效文本中语义相反：Task 规定"写入成功 ⇒ BLOCKED"，r2 规定"写入成功 ⇒ 预期结果（正向控制）"。若两文并存，一次 scratch 正写成功将同时满足"正向证据"与"阻断条件"，Gate 判定不可判定（这也会误导后续 r2:118 的 scratch positive write 评估）。
- **最小修正**：拆成两个不同对象与角色（scratch 内的正向控制路径 / Task 语义下的只读 alias），或由 Codex 在 Task/证据中显式登记废止旧的"只读 alias 写成功=BLOCKED"语义（该语义源自已被 2026-10-10 用户裁决取代的 WSB 流程），不得让两种语义并存。

#### R2-17 — 前后 hash 覆盖过度声明、口径缺失、且会被自身证据污染
- **级别**：**P1**
- **路径/条款**：r2:116（"记录新建前后主仓 203 项 protected manifest、固定 scratch 输入、12 个输入 HostFolder…所有受保护 hash 必须逐项前后 MATCH"）、r2:114
- **影响**：(a) 项目冻结的 root manifest 是**203 条 dirty/untracked 现场**（`status_command='git status --porcelain=v1 --untracked-files=all -z'`，`4×" M" + 199×"??"`，digest `3a54fa97…`，其创建 HEAD=`549a6544…`），**不是**整个仓库，也**不含**工具链根的内容；"所有受保护 hash 逐项 MATCH"隐含全覆盖，与登记事实不符。(b) 12 个 HostFolder 的内容覆盖是**部分**的（`P02.md:100`：50,356 个小文件全量哈希、33 个工具链选样、**138,947 个文件内容未计算**、6 个映射仅 metadata/size），r2 未声明这一覆盖口径，等于把采样当成全量。(c) 前后对比的"受保护集合"会**天然包含本契约/Review 自身产出的新文件**（本派发已在 `verification/P02/` 下生成 `dsh-appcontainer-contract-r2-review.{prompt.md,stdout.md,stderr.log}` 等未跟踪文件，历史 checkpoint 亦记录"pre-existing untracked DSH/R1–R4 run logs remain unstaged"）；r2 未定义排除集，该断言将因自身产物而必然 MISMATCH。(d) 未写 hash 口径（原始工作区字节 vs 规范化、EOL/CRLF、路径大小写与编码、Git blob vs 工作区内容）——项目已因 EOL 口径产生过实际争议（`P02.md:105` 的 R9F CRLF 事件）。
- **最小修正**：(1) 逐根声明覆盖口径（全量内容哈希 / metadata+选样 / 仅存在性），把"未内容哈希"的对象列为 UNKNOWN 而非 MATCH；(2) 给出冻结的排除集（本契约与 Review 派发自身产出的文件、日志、profile/scratch 输出）；(3) 写死 hash 口径（原始工作区字节 + 另附 Git blob hash；主仓清单沿用既有 `-z` 原始字节 recipe 与 digest）；(4) 明确 203 项只覆盖 root dirty/untracked 现场，clean tracked 文件由 Git 保护。

### 3.7 审查内容 6

#### R2-18 — 事件通道、句柄表快照、Job 权威性论证缺失
- **级别**：**P2**
- **路径/条款**：r2:107-109
- **影响**：(a) "OS process-create/exit 事件及 Job Object 通知"未指明具体通道：ETW 内核进程事件通常需要相应权限，可能与"非提权 controller"冲突；非提权可用的等价物是 Job completion port 的 `JOB_OBJECT_MSG_NEW_PROCESS`/`JOB_OBJECT_MSG_EXIT_PROCESS`（另需 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` 与关联完成端口）。契约未写选定通道、所需权限、消息类型与**通知丢失计数**，因此"完整进程树"缺乏可执行的取证路径。(b) `bInheritHandles=FALSE` 只是 controller 侧承诺；未要求 LPAC 主进程 resume 前记录句柄表快照以证明"无预存未授权句柄"（r1 F-01 的句柄表检查只部分闭合）。(c) 未写出"不授 breakaway ⇒ 后代无法脱离 Job ⇒ Job 是权威包含集合"这一关键论证（它正是"未知后代"能被穷举的依据）。
- **最小修正**：点名通道（优先 Job completion port）、权限、消息类型、丢失/超限计数与"任何丢失 ⇒ `BLOCKED`"；增加 resume 前句柄表快照要求；补写 Job 权威性论证。

### 3.8 审查内容 7

#### R2-19 — `C:\Windows\System32` 等 loader/runtime 动态读闭包：当前不是可实施的精确范围
- **级别**：**P1**
- **路径/条款**：r2:45、r2:101（`PATH` 含"经审查的 Windows loader 所需目录"）、r2:24
- **影响**：(a) r2:45 要求"在 preflight 中以实际模块加载/文件访问证据逐个解析到精确系统文件及其只读祖先"，但**没有说谁来授予这些 ACE、需要什么权限、是否继承、如何回滚**——而修改 `C:\Windows` 下对象 DACL 需提权/TrustedInstaller 所有权（A3），与 r2:18 的"非提权 controller"直接冲突；若改为"只解析不授予"，LPAC 进程根本无法启动，preflight 必然失败且无法区分"设计缺陷"与"隔离生效"。(b) 该集合本质是**动态**的（delay-load、API set 解析、MUI `.mui`、WinSxS/activation context、.NET 等），"逐文件前置解析"在没有实测轨迹的情况下不可完成，而 r2 又**正确地**禁止了宽路径兜底——于是契约陷入"既不能枚举、也不许兜底"的空集。(c) 是否**必须**授予取决于 Windows 是否已为 `S-1-15-2-2`（ALL RESTRICTED APPLICATION PACKAGES）预置 ACE（A5）；这正是唯一应当先只读测量的关键事实。这也与一手文档相印证：LPAC 的文档定位是"no rights to any resources except what you explicitly grant（如浏览器子 worker 进程）"，而不是承载完整 PyInstaller/Node/Rust 工具链闭包。
- **最小修正**（不改用宽泛 `Windows` 目录授权）：(1) 只读 preflight 先测量 System32/loader 路径 DACL 中是否已含 `S-1-15-2-2` ACE（只读，可非提权完成）——若已含，则本条要求可整体删除；(2) 若不含，改为可实施的"实测—冻结"两阶段：先用**显式登记、逐条列出的初始系统读集合**（加上"任何未登记访问即 `BLOCKED`"）跑一次无项目代码的 trace probe，把观测到的精确读写集合冻结为唯一允许集合并全部登记 ACE（含掩码/继承/回滚/所有者），再重跑；trace 本身作为授权基线；(3) 一次性记录 `CreateProcess` 的 HRESULT/`GetLastError` 与失败时的镜像/DLL 路径，使"LPAC 无法启动"成为有证据的 `BLOCKED` 而非"隔离通过"。

### 3.9 审查内容 8

#### R2-20 — 报告捕获路径与请求不一致；"核验"措辞
- **级别**：**P3**
- **路径/条款**：r2:120（"Microsoft 一手资料（2026-10-10 核验）"）；派发请求的输出路径行
- **影响**：请求建议 `verification/P02/appcontainer-isolation-contract-r2-review.stdout.md`，实际 harness 捕获为 `verification/P02/dsh-appcontainer-contract-r2-review.stdout.md`；若按建议路径引用会得到悬空引用。另：§Microsoft 一手资料 的"核验"字样与 r2:125"这些是 API 设计依据，不是本机已验证事实"并存，容易被读成"已独立复核"。
- **最小修正**：引用实际捕获路径；把"核验"改成"owner 侧引用核对（未在本机独立验证）"。

#### R2-21 — 状态台账缺 hook/cache 一项
- **级别**：**P3**
- **路径/条款**：r2:6 对照 `codex-checkpoint-autonomous-orchestration-20261010.md:14`
- **影响**：checkpoint 的状态台账包含 `hook/cache/child process closure=BLOCKED / NOT_VERIFIED`，r2:6 未列该项（只在 r2:103 提及仍需对账），属状态台账不完整。
- **最小修正**：在 r2:6 补齐 hook/cache=`BLOCKED / NOT_VERIFIED`。

---

## 4. r1 Review（F-00…F-18）闭合对账

| r1 finding | 现状 | 去向 |
|---|---|---|
| F-00 hash 绑定 | **未闭合**（本会话同样无法计算） | C-00 |
| F-01 读写双向白名单 + fail-closed 判定 | 部分闭合（r2:24/70/72 已写双向清单与"权限交集"要求）；ACE 掩码/继承/标签/句柄表未定义 | R2-10、R2-15、R2-18 |
| F-02 祖先 traverse 授权 | 形式闭合（r2:24 要求逐项登记祖先），但语义不精确且与 deny 冲突 | R2-10 |
| F-03 profile 路径/hive 逐条量化 | 部分闭合（API 为唯一来源 + `Temp` 关系 + 祖先 reparse）；确切目录形态与私有键路径未列 | R2-01 |
| F-04 缓存/凭据变量清单 | **已闭合**（r2:78-101 固定表、`HF_TOKEN_PATH`、禁止复制 token、`HF_HUB_DISABLE_IMPLICIT_TOKEN=1`） | 残余 R2-07 |
| F-05 网络关闭判定 | 部分闭合（零 capability 设计正确）；无证据/探针设计 | R2-09、R2-08 |
| F-06 profile 创建/删除权限模型 | 部分闭合（声明非提权 controller）；无一手依据，未覆盖 WRITE_DAC/标签权限 | R2-11、§3.4 |
| F-07 清理闭环 | 部分闭合（唯一 moniker + 存在性检查 + 只删本轮 profile + `CLEANUP_BLOCKED`）；缺创建前/后/删除后 manifest 与"残留为空"断言；确定性命名无随机后缀 | R2-02、R2-03 |
| F-08 OS build pin + TEMP 实测断言 | 部分闭合（要求保存并校验变量最终值）；缺 OS build/架构 pin、缺被测进程回读 | R2-06 |
| F-09 注册表读语义 | **已闭合**（以更强方式：不授 `registryRead` ⇒ 不能打开任何键） | — |
| F-10 时序安全采集 / PID 复用 | **已闭合**（挂起创建 + Job + 创建/退出事件 + creation time 区分复用 + UNKNOWN⇒stop） | 残余 R2-18 |
| F-11 验收等效口径澄清 | **已闭合**（由 `P02.md:58-62` 承担，r2 未反向改变该口径） | — |
| F-12 崩溃转储/WER 跨容器写入 | **未闭合** | R2-22 |
| F-13 reparse point 前置枚举 | **已闭合**（祖先/递归 reparse + 禁通配）；hardlink/ADS 方法与成本待补 | R2-12 |
| F-14 带外/breakaway 启动路径 | **已闭合**（不授 breakaway + 同 job/同 Package SID + UNKNOWN⇒stop） | 残余 R2-18 |
| F-15 负向/阳性对照 | **未闭合** | R2-15 |
| F-16 manifest 规范化口径 | **未闭合** | R2-17 |
| F-17 BLOCKED 时保留现场 | **已闭合**（r2:115 `CLEANUP_BLOCKED` 保留现场；r2:117 不清理 scratch/日志/既存 profile） | — |
| F-18 单次 profile 互斥 | 部分闭合（"只允许一个 profile" + 存在性检查 ≈ 互斥）；无显式并发声明与残留恢复 | R2-02 |

**r2 值得记录的正项**：12 个 RO 根与 TSV 逐字符一致；RW 清单与 `P02.md:74-77` 逐项一致且禁止清空/覆盖既有文件；禁止清单完整覆盖主仓/worktree/漫画库/数据库/Lock/current-pinned/凭据/全局缓存；"用户/组 SID 与 AppContainer SID 交集"表述与一手文档一致；LPAC opt-out 属性名与取值、零 capability（含 `registryRead`/`lpacCom`）、`LOCALAPPDATA`/`TEMP`/`TMP` 形态均与一手文档一致；挂起创建 + 单一 Job + 不授 breakaway + `UNKNOWN`⇒停止是可用且 fail-closed 的进程设计；删除只针对本轮新建的 exact profile；首轮只跑无项目代码的 synthetic probe。

---

## 5. 最终判定

**decision = `NOT_VERIFIED`**

- **对象绑定层面**：契约与 Task 的 SHA-256 在本会话**无法独立核验**（`pwsh` 沙箱 `grantWrite` 失败、子代理同样失败、`danger-full-access` 无审批通道），Task SHA 亦无任何 checkpoint 旁证。按 exact-object 口径，本报告不能声称绑定到 prompt 声明的 hash（C-00）。据 r1 prompt 的同类先例（"无法核验"≠"不符"，故不报 `BLOCKED / hash mismatch`，而降级为 `NOT_VERIFIED`），此处取 `NOT_VERIFIED`。
- **内容层面**：**等同 `CHANGES_REQUESTED`**。r2 在 API 名称、LPAC 语义、路径清单复用与 fail-closed 姿态上质量较高，但存在 **2 项 P0 内容缺陷**（强制完整性/MIC 缺失使 scratch 写与正向 canary 不可实现；祖先 ACE 策略与被禁路径的 deny 声明内部冲突并可能泄漏可读性）、**5 项 P1**（ACL 变更无范围登记与还原、AccessCheck 证据设计、canary 语义冲突、前后 hash 过度声明、系统 loader 闭包不可实施）以及 8 项 P2 / 7 项 P3。

**发现计数**：内容 **P0=2，P1=5，P2=8，P3=7（合计 22）**；另有 **C-00（验证能力 P0 级阻断，非契约内容缺陷）**。

**能否进入"无 profile 创建的只读 OS preflight"**：**不能**。r2:130 自设前置是"Review 无未解决 P0/P1"，当前未满足。在 Codex 完成 finding adjudication 并产出修订契约（建议 r3）后，该只读 preflight **可以且应当**进行——且建议把它设计成**纯测量**（不建 profile、不改任何 ACL），至少闭合：moniker/path/私有注册表键不存在性；每个目标对象的 `WRITE_DAC` 与标签写入能力（非提权）；每个读/写目标的强制标签与 mandatory policy；LPAC token 的 `SeChangeNotifyPrivilege`；System32/loader 路径 DACL 是否已含 `S-1-15-2-2`；以及 `CreateAppContainerProfile`/`DeleteAppContainerProfile` 的实际权限要求。

**Gate 声明（本报告无任何提升）**：`Build Gate=BLOCKED`；`build=NOT_AUTHORIZED / NOT_RUN`；`Hard Build Barrier=EFFECTIVE`；`AC1–AC7=BLOCKED / NOT_RUN`；`hook/cache=BLOCKED / NOT_VERIFIED`；`profile=NOT_CREATED`；`隔离预检=NOT_RUN`。本报告**不批准** profile 创建、ACL 修改、Smoke 或 Build；用户授权未被当作任何 Gate/Test 依据。本 Reviewer 非作者，角色互异成立（依据仓库 `AGENTS.md`）。

---

## 6. 本会话未做 / 无法做

1. 未独立计算契约/Task/Candidate/TSV/audit 的 SHA-256 与字节数；未复核 workspace porcelain、staged 集合与 203 项 protected manifest（`pwsh` 不可用，C-00）。
2. 未查询/探测 Windows host（OS build、AppContainer/LPAC 可用性、profile 路径实际形态、TEMP 实际值、system ACL 是否含 `S-1-15-2-2`、`WRITE_DAC`/标签权限）。
3. 未创建/删除任何 AppContainer profile；未改任何 ACL/registry。
4. 未运行 Sandbox、Smoke、Build、Cargo、Tauri、PyInstaller、runner、Vitest、GUI 或产品测试。
5. 未读取任何被保护用户数据样本；未进入 `G:\CODEX\P02-scratch-build-source`。
6. 未核验 r2 引用文献之外的 Microsoft 文档；`web_search` 端点 401 不可用（`web_fetch` 可用）。
7. 未复核 `scope-delta`、`build-preflight-*`、`owner-transfer-*` 等旁证工件（超出本次绑定对象）。

## 7. 一手文档核验记录（本会话成功取回并逐条比对）

- [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)：per-user/per-app profile；name ≤64 且匹配 `[-_. A-Za-z0-9]+`；`ERROR_ALREADY_EXISTS`；`E_ACCESSDENIED` = "caller doesn't have permission to create the profile"；folder ACL 阻止其他用户/应用访问。
- [DeleteAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deleteappcontainerprofile)："Deleting a non-existent profile returns success"；`ERROR_NOT_SUPPORTED`（从 app container 内调用）；应先关闭 profile 存储的所有文件句柄；"If the function fails, the status of the profile is undetermined, and you should call DeleteAppContainerProfile again"。
- [GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)：取指定 AppContainer 的 local app data 目录；与 `SHGetKnownFolderPath(FOLDERID_LocalAppData)` 同值；"If a thread token is set … current user; if no thread token is set … process identity"。
- [GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)：无 SID 入参，取**current profile** 的注册表存储；`E_INVALIDARG` = caller 未以可访问该 profile 的用户身份运行/impersonate。
- [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)：`STARTUPINFOEX`+`PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES`；LPAC 追加 `PROC_THREAD_ATTRIBUTE_ALL_APPLICATION_PACKAGES_POLICY=PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT`；`CreateProcess(..., FALSE, EXTENDED_STARTUPINFO_PRESENT, ...)`；"LPAC **cannot open any keys in the registry** unless it has the _registryRead_ capability and cannot use COM unless it has the _lpacCom_ capability"；无 network capability 不能访问网络；权限 = user/group SID 与 AppContainer SID 的**交集**；`LOCALAPPDATA=…\Packages\TestAppContainer\AC`、`TEMP=TMP=…\AC\Temp`；AppContainer 运行于 Low IL。
- [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)：credential / device / file / network / process / window 隔离；写授权可针对具体持久文件与注册表键。
- [AppContainer for legacy apps](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-for-legacy-applications-)："if you _are_ in an app container, then the integrity level (IL) is always _low_"；unpackaged 子进程通常继承父 token（仍须实测）。
- [TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class)：`TokenIsAppContainer`、`TokenIsLessPrivilegedAppContainer`（"effectively an AppContainer that's disregarded by the ALL_APPLICATION_PACKAGES SID"；LPAC 只能以 API 命令式创建）。
- [AccessCheck](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck)：入参为 `pSecurityDescriptor` + **`ClientToken`（impersonation token handle，需 `TOKEN_QUERY`）** + `DesiredAccess`（须先 `MapGenericMask`）+ `GenericMapping` + `PrivilegeSet`；只按 DACL 与 token 判定，不产生审计。
- [Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)：MIC "evaluates access **before** access checks against an object's DACL"；"a principal with a low integrity level cannot write to an object with a medium integrity level, even if that object's DACL allows write access"；"By default, the system creates every object with an access mask of `SYSTEM_MANDATORY_LABEL_NO_WRITE_UP`"；无标签对象按 Medium 处理；完整性 SID 存于 **SACL**。

以上引用均为外部不可信数据，仅按事实比对使用；r2 对这 4 个 API 与 2 个 LPAC 页的引用语义**可逐条证实**，故审查内容 8 的"准确性"判定为"引用准确、调用上下文与清理语义不准确/不完整"。

---

## 8. 推荐下一步（单一、可直接转发）

**给 Codex（Lead / Architect / Integrator）**：

> 请对 `verification/P02/appcontainer-isolation-contract-r2.md` 做**纯文档修订**，产出 r3，保持 `Hard Build Barrier=EFFECTIVE`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`profile=NOT_CREATED`、`隔离预检=NOT_RUN`，不创建 profile、不改 ACL/registry、不探测 host、不运行 Sandbox/Smoke/Build/Cargo/Tauri/PyInstaller/产品测试：
> (1) 必闭合 P0：R2-04（把强制完整性/MIC 写入前置条件、标签采集与还原、`TokenIntegrityLevel`/`TokenMandatoryPolicy` 写入契约，并重估 scratch RW 与正向 canary 的可行性）、R2-10（祖先 ACE 改为"持有 `SeChangeNotifyPrivilege` 则零 ACE"，否则仅非继承 `FILE_TRAVERSE` 并逐条登记；删除"祖先最多 read-execute"）。
> (2) 必闭合 P1：R2-11（ACL/标签变更集合独立登记 + 原 DACL/标签采集还原 + 非提权 `WRITE_DAC` 可行性证明）、R2-15（AccessCheck token/语义/配对对照）、R2-16（canary 语义与 Task:79 二选一并登记）、R2-17（逐根 hash 覆盖口径 + 排除集 + 原始字节 hash 配方）、R2-19（系统 loader 闭包改为"先只读实测 `S-1-15-2-2` → 两阶段实测-冻结"，并写明授予主体/权限/继承/回滚）。
> (3) 处置 8 项 P2 与 7 项 P3（至少给出 closed / explicit disposition 二选一）。
> (4) 修订后复算并登记新候选 SHA-256，并注明本报告的对象绑定未成立（C-00），需在可执行 shell 环境重算 r2 与 Task 的 hash 才能引用本报告。
> (5) 不改 P02 Owner allowlist、产品 AC、现有 scratch 输出 allowlist、Task 依赖或用户数据保护要求；不扩大任何路径授权。
> (6) 完成后派发**本会话之外**的 exact-hash 只读复审；复审无未解决 P0/P1 且 Codex 逐项 adjudication 通过后，**才**进行**不创建 profile、不改任何 ACL** 的只读 OS preflight（测量项见本报告 §5）。在 Build Gate 由 Codex 明确记录 `PASS` 并解除 Hard Build Barrier 之前，不得运行 Cargo/Tauri/PyInstaller 或 AC1–AC7。

**给用户**：当前**无需**任何新授权；本契约的修订与只读 preflight 都在既有授权范围内。唯一可能需要用户裁决的情形是：若只读 preflight 证明非提权 controller **无法**在 `Program Files`/系统文件/标签上完成所需 ACL/标签变更（R2-11/R2-19），则该 AppContainer 方向在"非提权 Codex-only"前提下不可实施，届时需用户决定是放弃该方向、另行授权提权方案，还是接受 Build Gate 长期 `BLOCKED`。

---

*报告结束。本报告为只读审查产物，对任何实际 Gate 均无提升；不得据此批准 profile 创建、ACL 修改、Smoke 或 Build。*
