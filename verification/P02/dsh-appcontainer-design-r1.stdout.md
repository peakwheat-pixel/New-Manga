# P02 AppContainer 隔离设计候选 · 独立只读 Review（DSH）

## 0. 结论摘要

**decision = `NOT_VERIFIED`**

- **设计内容层面**：候选文件的**技术方向成立、边界陈述基本诚实**，但存在 6 项 P1 级设计缺口与若干 P2/P3，**不足以直接进入"通过设计审查"的状态**；即使 hash 可核验，本 Review 的 finding 结论也会是 `CHANGES_REQUESTED`。
- **证据完整性层面**：**我无法计算固定候选的 SHA-256**，因此**不能**把结论绑定到 `2febe1e204702b137e4894d7cd830ae494a1a01579295c708bb56753a951a60c`。这不是内容 hash mismatch，而是**本会话无法执行 hash 计算**（见 F-00）。依 prompt 第 3 行的绑定要求，最终 decision 取 `NOT_VERIFIED`。

**未变动的 Gate 口径（本 Review 不提升任何 Gate）**：`P02 Hard Build Barrier = EFFECTIVE`；`Build Gate = BLOCKED`；`build = NOT_AUTHORIZED / NOT_RUN`；`hook/cache = BLOCKED / NOT_VERIFIED`；`AC1–AC7 = BLOCKED / NOT_RUN`；`wsb start = NOT_RUN`。本 Review **不批准** profile 创建、host 探测、smoke、build、Cargo/Tauri，也不修改任何文件。

---

## 1. 绑定对象与 hash 校验状态

| 项 | 值 |
|---|---|
| 固定对象 | `verification/P02/appcontainer-isolation-candidate-r1.md` |
| prompt 声明 SHA-256 | `2febe1e204702b137e4894d7cd830ae494a1a01579295c708bb56753a951a60c` |
| 本会话实测 SHA-256 | **UNAVAILABLE（无法计算）** |
| 实测手段 | `pwsh` 工具在本 workspace 初始化即失败；独立子代理同样失败；`danger-full-access` 升级无审批通道 |
| 原始错误原文 | `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)` |
| 旁证（非 hash） | 该 hash 字面量存在于 `verification/P02/dsh-appcontainer-design-r1.prompt.md:3`（我逐字读取核对一致）；候选文件存在于固定路径，全文 41 行、内容与 prompt 描述的 docs-only candidate 形态一致 |

**判定**：按 prompt 规则，**hash 不符才报 `BLOCKED / hash mismatch`**。此处是"**无法核验**"而非"**不符**"，故**不报 BLOCKED**，而是把"对象绑定不可验证"如实登记为 **F-00（P0，验证能力阻断）**，并把决策降级为 `NOT_VERIFIED`。

**我的诚实边界**：本次 Review 的全部实质结论**绑定到"我在本会话逐行读取到的该路径文件内容"**，**不绑定**到 Git HEAD、tree、blob 或上述 SHA-256。任何下游集成方必须在能计算 hash 的环境复核该 hash 后才能引用本报告的绑定关系。

---

## 2. 授权与范围边界（我的独立核对）

- 候选自述状态 `PROPOSED / NOT_AUTHORIZED / NOT_TESTED`（候选 `:3`），并明确不修改 P02 Task/allowlist、不授权 profile 创建/host 探测/smoke/build（`:3`、`:25`、`:30`）——**与冻结治理一致**。
- `doc/tasks/P02.md:64-77` 的 `Codex-only local scratch-build output boundary` 只固定 scratch clone `G:\CODEX\P02-scratch-build-source` 与 scratch 内输出（`:68`、`:73`），**不含**任何 AppContainer profile、用户级注册表 hive 或 `%LOCALAPPDATA%` 路径。→ 候选 `:23-25` 关于"profile 位于 scratch-only allowlist 之外、当前授权不自动扩大"的陈述**属实**。
- `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`（r10 有效段落，`:156-185`）的许可路径**只**覆盖 `doc/tasks/P02.md` boundary 段与 `verification/P02/**` 证据文件，**不包含** profile 创建/清理或任何 host-state 写入。→ 候选要求的"新 scope 决定"**确实必须先有**。
- `doc/STATUS.md:5`、`doc/REBASELINE_PLAN.md:5`、`doc/00_INDEX.md:5` 三处当前口径一致：**本机 Windows 验证在项目验收口径上等同 Windows Sandbox 验证，但不表示具备 VM 隔离，且不豁免数据/写入保护**。→ 见 F-11（候选 `:9` 的表述与该项目口径表面冲突，需集成方澄清）。
- 阻断事实源仍为 `verification/P02/codex-hook-cache-closure-audit-r1.md:26`（静态清单不能证明完整可达写入闭包，结论 `BLOCKED / NOT_VERIFIED`）。→ 候选 `:9` 与 `:30` 的引用**准确**。

---

## 3. Findings（逐条：位置 / 严重度 / 影响 / 最小修复）

### F-00 — 固定候选 hash 无法独立核验
- **位置**：`verification/P02/appcontainer-isolation-candidate-r1.md`（对象身份）；prompt `:3`
- **严重度**：**P0（验证能力，非内容缺陷）**
- **影响**：无法证明被审内容与 prompt 指定的 `2febe1e2…a60c` 同一；所有结论的对象绑定不成立，不能作为后续 Review/Gate 的固定输入引用。
- **最小修复**：在具备可执行 shell 的环境（或修复本 workspace 沙箱 `grantWrite` 失败）重算 SHA-256；若与 prompt 值一致，本报告的对象绑定条款由该复算替换；若不一致，按 prompt 报 `BLOCKED / hash mismatch`。

### F-01（对应审查范围 3/4）— 进程树/写入路径的"完整清单 + fail closed"缺少逐项闭环定义
- **位置**：候选 `:17`、`:19`
- **严重度**：**P1**
- **影响**：`:17` 只枚举"源码 clone、Python/toolchain、依赖、hook 文件"读与 scratch 写，并把"未知/未映射路径 fail closed"写成原则；但**未定义 fail-closed 的判定机制与覆盖面**——写拒绝探针无法覆盖"读泄漏"与"句柄继承"，而 `:19` 的阻断条件也只列"未登记路径可写"。若某子进程能**读**受保护目录或继承未授权句柄，现有设计既检测不到也不阻断。
- **最小修复**：把 fail-closed 定义为**逐路径 ACE 白名单 + 全祖先遍历权**的双向闭合（读与写各自白名单，未列出即可读=FAIL、可写=FAIL），并把 `:19` 的阻断条件扩展为"任一读白名单外成功打开 / 任一写白名单外成功创建或修改 / 任一进程句柄表含未授权目标"。

### F-02（范围 3/4）— 缺少**祖先目录遍历授权**要求（Windows ACE 继承语义）
- **位置**：候选 `:15`（"最小 ACL"）、`:17`
- **严重度**：**P1**
- **影响**：Windows 访问检查要求路径上**每个父目录**具备 traverse/`SeChangeNotifyPrivilege` 才能到达目标。设计只说"按清单给予最小 ACL"，未要求把每个白名单对象的祖先目录一并登记；实践中会导致两种坏结果：要么实现时为了"能跑"而放宽祖先 ACL（静默扩大范围），要么在深层路径上随机失败并被误判为兼容性问题。
- **最小修复**：ACL contract 必须**逐对象列出自身 + 全部祖先**的 ACE 条目，并声明"祖先目录只授 traverse、不授 create/write/delete"，任何未列出的祖先目录 = BLOCKED。

### F-03（范围 2/4）— profile 存储位置与额外重定向目录**未量化**，存在 profile 外写入遗漏
- **位置**：候选 `:23`、`:24`；对照 `doc/tasks/P02.md:68`、`:73`
- **严重度**：**P1**
- **影响**：`:23` 只提到"profile 路径"与 `LOCALAPPDATA`/`TEMP`/`TMP` 重定向、以及"per-user/per-app registry storage"。**未写出 profile 的实际绝对路径形态**（`%LOCALAPPDATA%\Packages\<PackageFamilyName>\…`、其中 `AC\`、`Temp\`、`LocalCache`、私有 hive 等子目录），也未覆盖 AppContainer 的**其他重定向/私有目录**（如 `LocalState`、`Roaming`、`AC\Microsoft\…`）。因此"scratch-only scope delta"目前是**分类级**而非**路径级**，"是否仍有 profile 外写入遗漏"**无法回答**。
- **最小修复**：在候选内**逐条列出**该 profile 将创建的全部绝对路径与 hive 文件，标注每一条属于 scratch 内还是 profile scope；并明确声明**除此清单外不存在其他新增 host 写入**，任何运行期新出现的第 N 条路径 = BLOCKED / FAIL。

### F-04（范围 3/4）— 缓存/状态变量清单不完整，含凭据位置
- **位置**：候选 `:17`；对照 `verification/P02/codex-hook-cache-closure-audit-r1.md:18-20`
- **严重度**：**P1**
- **影响**：`:17` 只写"`TEMP`、`TMP`、Python bytecode、PyInstaller、Torch、Hugging Face 等缓存变量"，**未逐个点名**审计已确认的可变面：`PYINSTALLER_CONFIG_DIR`（审计 `:18`）、`TORCH_HOME` / `XDG_CACHE_HOME`（审计 `:19`）、`HF_HOME` / `HF_HUB_CACHE` / `HF_XET_CACHE` 及 **token 文件位置**（审计 `:20`）。其中 **HF token/凭据路径** 属数据保护敏感面：若未显式重定向，build 进程可能读用户真实凭据目录或在其下写状态文件。
- **最小修复**：候选内附**固定变量表**（变量名 → 必须在 scratch 内的最终值 → 禁止回退值），并加两条要求：(a) 运行前记录每个变量的**最终值**并断言均在 scratch 内；(b) 凭据类路径（如 HF token）**不授予读取**，缺失即按离线/匿名处理，不得回退到用户真实凭据目录。

### F-05（范围 4）— 网络能力关闭的具体判定未定义
- **位置**：候选 `:15`、`:19`
- **严重度**：**P1**
- **影响**：`:15` 只写"默认不授予网络 capability"，`:19` 只列 5 个阻断条件（无"网络连通"一项）。没有定义"网络能力关闭"的**可观测证据**：应禁止出站 TCP/UDP、DNS、命名管道到容器外、以及经由 broker 的代理访问；也不清楚 loopback/UNC 的行为是否被检查。→ smoke 无法产出一条能被独立复核的"网络关闭"结论。
- **最小修复**：定义至少 3 个负向探针（公共 DNS/TCP、局域网目的地址、loopback 端口）各自期望"被 OS 拒绝"，并把任一成功连接加入 `:19` 阻断条件；同时声明**未启用** `internetClient`/`privateNetworkClientServer` 等 capability，且 UNC/SMB 路径不在任何读白名单内。

### F-06（范围 2/4）— profile 创建的**权限模型**未声明
- **位置**：候选 `:15`、`:23`、`:25`
- **严重度**：**P1**
- **影响**：设计把 launcher 描述为"Codex-only launcher"，但**未说明 profile 创建/删除所需的权限等级**（是否需提权、在哪个账户上下文执行）。已有行业事实是 profile 删除路径通常需要管理员权限；若属实，则现有"Codex-only 非提权"前提**直接失效**，整个执行的授权前提要重写。设计不写明这一点，等于把一个可能推翻方案可行性的前置条件留给实现阶段临时发现。
- **最小修复**：在候选"未决范围"内**显式登记**：profile 创建与删除各需何种权限、由哪个账户/上下文执行、若需提权则本候选立即失效并回到用户裁决；**不得**在未声明权限模型的情况下进入实现。
- **我的边界**：本会话 `web_search` 端点鉴权失败（HTTP 401），我**未能**取得微软一手文档复核此点，故按"必须在实现前用一手资料确认"的未验证项处理（见 §6）。

### F-07（范围 4）— cleanup/lifecycle 不足以证明"精确清理"
- **位置**：候选 `:24`
- **严重度**：**P1**
- **影响**：`:24` 只规定"只删除本次任务创建的 profile、遇已存在即阻塞保留现场"，属于**负向约束**；缺少正向闭环：profile 名的唯一化生成方式（是否含不可碰撞随机后缀）、创建前的存在性检查证据、删除后的**残留断言**（profile 目录、私有 hive、注册表键是否全部消失）、以及"只影响本 profile"的证明。没有这些，"精确 profile lifecycle/cleanup"无法成为 smoke 证据。
- **最小修复**：最小契约四件套：(1) profile 名 = 固定前缀 + 本次运行随机 ID，并以 `ERROR_ALREADY_EXISTS` 作为硬阻断；(2) 创建前、创建后、删除后各留一条 manifest（路径存在性 + hive 存在性）；(3) 删除后断言**残留为空**，否则记 FAIL；(4) 记录删除操作的实际权限与退出码。

### F-08（范围 1/4）— `TEMP`/`TMP` 重定向**未验证**且缺算法差异
- **位置**：候选 `:23`（陈述 Windows 会重定向到 profile 下 `AC`/`Temp`）
- **严重度**：**P2**
- **影响**：`:23` 的陈述方向正确，但这是**文档语义**而非**实测值**；不同 Windows 版本在"取临时路径"的 API 行为上存在差异（系统/服务上下文与交互用户上下文对临时目录的判定不同）。候选**未**要求固定 OS build/架构，也**未**要求在 smoke 中断言"实际临时路径位于 scratch/profile 内"。若实际值落在 profile 外，会被 F-01 的薄弱 fail-closed 漏过。
- **最小修复**：登记**固定的 OS build + 架构**为输入 pin；smoke 中由被测进程回读 `TEMP`/`TMP`/`LOCALAPPDATA` 实际值并断言落在已登记路径集合内，否则 BLOCKED。

### F-09（范围 2/3）— "private registry" 语义过宽，未区分私有 hive 与共享 hive 的读
- **位置**：候选 `:23`
- **严重度**：**P2**
- **影响**：`:23` 仅称 profile "包含 per-user/per-app registry storage"，并把其整体暴露为 scope delta。但 AppContainer 的**读**通常仍会落到用户/机器的真实注册表视图（`HKCU`/`HKLM` 的既有内容），**写**才被引导到私有存储。候选未区分读写，读者可能误以为注册表**整体**已被隔离，从而低估"读泄漏/持久化残留"面。
- **最小修复**：拆分为两条陈述：写 = 私有 hive（scope delta，须逐路径登记）；读 = 仍可见用户/机器既有 hive 的可见子集，**仅作为隔离限制登记**，不授予"注册表已完全隔离"的表述。

### F-10（范围 4）— 探针与进程采集机制缺少时序保证（短命进程 / PID 复用）
- **位置**：候选 `:16`、`:18`
- **严重度**：**P2**
- **影响**：`:16` 要求"每个相关进程采集 `TokenIsAppContainer` 与 Package SID"、`:18` 以"全进程树 token 记录"为证据，但**未说明采集机制**。PyInstaller isolated worker 与 hook 子进程是**短命进程**；事后按 PID 枚举会因进程已退出或 **PID 复用**而产出**伪证据**（把别人的 PID 记成全树覆盖）。
- **最小修复**：要求**时序安全的采集**：以挂起方式创建 launcher 并纳入 job object（或等价的 ETW 事件采集），保证"进程创建→token 检查"之间不存在未观测窗口；并把"存在无法采集 token 的进程"直接列为 `:19` 的阻断条件（不可记为"未观测/不适用"）。

### F-11（范围 1）— `:9` 表述与项目现行裁决表面冲突
- **位置**：候选 `:9`
- **严重度**：**P2（文档一致性）**
- **影响**：候选 `:9` 只记录"用户裁决免去 Windows Sandbox Feature 查询/安装/启用/启动及 guest 验证"，**未**复述裁决的另一半——`doc/STATUS.md:5` / `doc/REBASELINE_PLAN.md:5`（及 `doc/00_INDEX.md:5`）明确"**本机 Windows 验证在项目验收口径上等同 Windows Sandbox 验证**"。候选 `:11` 又强调"不是 Windows Sandbox/Hyper-V VM、不能声称相同虚拟机边界"。两处并读会让读者以为该提案**更改**了本机验收等效口径；实际候选 `:30` 只处理 Build Gate，未处理该口径。
- **最小修复**：在候选 `:9` 补一句显式声明："本候选不改变 `P02/P04` 本机验证的验收等效口径（见 `doc/STATUS.md` 当前段），也不据此声称 VM 级隔离。"
- **注**：这同时消除了"不得称等价于 Windows Sandbox/VM"这一审查要求在**文档层**的歧义——候选 `:11` 本身已正确拒绝 VM 等价性声明，无需改动。

### F-12（范围 2）— 崩溃转储与现代待机内存构建，未纳入 profile 外写入面
- **位置**：候选 `:24` 的 scope delta 边界
- **严重度**：**P2**
- **影响**：若 build 中的进程发生崩溃，Windows 错误报告可能向**容器外**路径写入 dump（例如用户 `CrashDumps` 或 `ProgramData` 下的 WER 目录）；现代 Windows 的"待机内存构建"亦会在容器外落盘。候选未提，因此 `:24` 的"仅限本次 profile"scope 在崩溃路径下**不成立**。
- **最小修复**：在 scope delta 中增加两项之一：(a) 明确把崩溃转储/WER 写入列为**预期外 BLOCKED 条件**并在 smoke 前后 manifest 中检测；或 (b) 显式登记为可接受的第三类写入路径并给出其精确位置与清理责任。二者择一，不可留空。

### F-13（范围 4）— 仅 ACL 拒绝探针，未覆盖 reparse point / 符号链接边界
- **位置**：候选 `:18`
- **严重度**：**P2**
- **影响**：`:18` 的 deny 探针只"尝试打开既有目标"，**未**要求枚举输入/scratch 路径上的 **reparse point（junction/symlink/mount point）**。若 scratch 白名单目录内存在指向受保护路径的重解析点，写入白名单可被用于**穿透**到 scratch 之外，而 ACL 检查本身不会发现。项目在 HostFolder 检查中已有 reparse 枚举先例（见 `doc/tasks/P02.md:241` 的 `reparse=0` 证据口径），此处应同等对待。
- **最小修复**：在 smoke 前置条件中加入"对全部读/写白名单根递归枚举 reparse point，任何非普通目录/文件即 BLOCKED"。

### F-14（范围 3）— tag 边界与带外启动路径未声明
- **位置**：候选 `:16`、`:19`
- **严重度**：**P2**
- **影响**：`:16` 依赖"child 通常继承 parent token"，`:19` 以"任一子进程不在 AppContainer 中"为阻断。但**存在一类合法但不继承 token 的启动路径**（如通过 `CREATE_BREAKAWAY_FROM_JOB` 脱离 job，或经 COM/broker 服务的激活）。设计未声明这些路径是被禁止、被检测、还是被接受为"后代可能在容器外"的已知限制——若接受，则 `:19` 的"整树在容器内"不可断言。
- **最小修复**：显式声明两条约束：(a) 禁止使用 breakaway/带外启动（并说明如何检测）；(b) 明确"经 broker 激活的进程"是否计入"后代"，若不计入则把该豁免写入设计并给出理由与检测方式。

### F-15（范围 4）— 缺少负向/复现性要求
- **位置**：候选 `:18`
- **严重度**：**P3**
- **影响**：`:18` 只要求**正向**证据（deny 探针被拒、scratch 可写）。没有要求**负向对照**证明探针本身有效（例如对 scratch 内路径的同类探针**必须成功**），单侧探针无法排除"探针根本没执行"的假证据。
- **最小修复**：每个 deny 探针对应一个 scratch 内**阳性对照**（同 API、同参数、期望成功），并要求 `:19` 在任一侧不符合预期时阻断。

### F-16（范围 4）— manifest/hash 未声明规范化口径
- **位置**：候选 `:18`
- **严重度**：**P3**
- **影响**：`:18` 要求"测试前后受保护文件 manifest/hash"，但未声明 **EOL/编码/路径大小写** 的规范化口径。项目历史上已因"mixed EOL vs committed blob"产生过 hash 记录口径争议（`doc/tasks/P02.md:258`、`:263`）。若不预先定口径，前后对比会因规范化差异产出假变更或漏检。
- **最小修复**：规定 manifest hash 一律基于**原始字节**；若另行提供规范化 hash，必须**同时**给出两种口径与各自用途。

### F-17（范围 4）— 证据保留等价于"数据保护"
- **位置**：候选 `:18`、`:19`
- **严重度**：**P3**
- **影响**：`:19` 对不匹配场景只写"smoke=BLOCKED/FAIL"，未按项目既有规则要求**保留现场**（对照 `:24` 仅在已存在 profile 时要求保留现场）。同一候选内两条规则不一致。
- **最小修复**：把"BLOCKED/FAIL 时保留 scratch、profile 与日志现场，不清理不覆盖"统一写入 `:19`。

### F-18（范围 4）— 单次 profile / 并发互斥未声明
- **位置**：候选 `:24`
- **严重度**：**P3**
- **影响**：`:24` 要求"本次运行唯一命名"，但未规定**同一时刻只允许一个 P02 AppContainer profile**。并发（或重跑未清理）会破坏"唯一可识别"的前提，使 cleanup 与 scope 归属不可判定。
- **最小修复**：增加排他锁/互斥要求：已存在任一 P02 命名空间 profile 即 BLOCKED，不得并行创建。

---

## 4. scratch-only scope delta（候选已暴露 vs 必须补齐）

**候选已如实暴露的部分（我核对属实，应记为正项）**：
1. `CreateAppContainerProfile` 的 per-user/per-app profile 位于 P02 当前 scratch-only allowlist **之外**（候选 `:23`、`:24`、`:25`）。对照 `doc/tasks/P02.md:68`/`:73` 与 scope delta `:156-185`——**确实不在**授权写集合内。
2. profile 私有 **registry storage** 亦在此 scope 之外（候选 `:23`）。
3. `LOCALAPPDATA`/`TEMP`/`TMP` 被容器重定向到 profile 下（候选 `:23`）。
4. 明确拒绝把 `%LOCALAPPDATA%`、整用户目录、通用 temp 根纳入写权限（候选 `:24`）——**边界收得正确**。
5. 明确"当前用户授权不自动扩大该 scope、须由用户决定"（候选 `:25`）——**权限归属正确**。

**必须补齐的 delta 要求（本 Review 的 scope 结论）**：
- **D-1（路径级清单）**：profile 的全部绝对路径 + 私有 hive 文件必须逐条列出（F-03）。
- **D-2（权限模型）**：profile 创建/删除所需权限与执行账户必须声明；需提权则本候选失效（F-06）。
- **D-3（清理闭环）**：唯一化命名 + 创建前后/删除后三类 manifest + 残留为空断言（F-07）。
- **D-4（权限外写入面归零声明）**：崩溃转储/WER 一类跨容器写入必须被显式列为 BLOCKED 条件或显式登记（F-12）。
- **D-5（读语义登记）**：注册表读仍可见既有 hive，须作为"隔离限制"登记而非计入隔离收益（F-09）。
- **D-6（单次运行互斥）**：同一时刻仅一个 P02 profile（F-18）。

**结论**：候选**把 profile scope 暴露为 scope delta 这件事本身是诚实且方向正确的**（这是进入用户 scope review 的必要条件之一）；但 delta 目前是**分类级**，未达到用户可就"精确 host-state 授权"做决定所需的**路径级/权限级精度**。

---

## 5. 审查范围逐项答复

**范围 1（AppContainer/LPAC 是否技术上合适；不得称 VM 等价）**
方向**合适**：AppContainer 确实提供 OS security token + ACL/capability 边界，适用于"约束本机 PyInstaller build 的写入/读取面"这一目标；LPAC 作为更严选项留待实测是**稳妥的保守姿态**（候选 `:15`）。候选 `:11` **正确拒绝**了 Windows Sandbox/Hyper-V VM 等价性声明。→ **通过（无 P0/P1）**，仅需 F-11 的文档澄清。
**但我必须提醒的下游风险（非候选缺陷，属 scope review 输入）**：AppContainer 是**用户态**安全边界，不构成内核/硬件级隔离，也不隔离共享内核组件与 GPU/驱动面。若用户对"本机验收等效 Sandbox"的期望被理解成"内核隔离等价"，则该期望**不应**由本候选承载。这属于用户决策的前提，我在此显式标注，**不**替用户决定。

**范围 2（profile/registry/ACL/重定向是否如实暴露；是否仍有遗漏）**
**如实暴露 = 是**；**仍有遗漏 = 是**（F-03 路径未量化、F-06 权限未声明、F-07 清理未闭环、F-12 崩溃写入面未提、F-09 读语义未区分、F-18 未互斥）。

**范围 3（token/capability/ACL 证据设计是否充分；实现前必须明确什么）**
**部分充分**：`:16` 的"不能只以 launcher token 证明整树"与 `:19` 的 token 不匹配即阻断——**方向正确且是本候选最有价值的设计点**。
**实现前必须明确（不可留给实现阶段临时决定）**：
1. F-10 时序安全采集（短命进程 / PID 复用）；
2. F-14 带外启动路径的禁止与检测；
3. F-02 祖先目录 traverse 授权；
4. F-04 变量/凭据位置的固定清单与最终值断言；
5. F-06 profile 权限模型；
6. F-01 读写双向白名单与 fail-closed 判定机制；
7. F-13 reparse point 前置枚举。

**范围 4（现有 6 类证据是否足以构成后续 smoke 证据）**
逐项判定：protected-path deny（**不足**，F-13/F-15）、scratch write（**不足**，F-15 缺阳性对照）、网络能力关闭（**不足**，F-05 无判定定义）、process tree token（**不足**，F-10/F-14）、前后 manifest/hash（**基本可用**，需 F-16 定口径 + F-11 无关）、profile lifecycle/cleanup（**不足**，F-07）。
→ **合并结论：不足以构成后续 smoke 证据**；按上述最小修正补齐后**可以**构成。

**范围 5（只评价设计；Hard Build Barrier 保持）**
本 Review **只**评价设计候选，**不**批准 profile 创建、host 探测、smoke、build、Cargo/Tauri，**不**修改任何文件、Task、allowlist 或 Gate。`Hard Build Barrier = EFFECTIVE`、`Build Gate = BLOCKED`、`build = NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7 = BLOCKED / NOT_RUN` **均未变动**。候选 `:30` 的自我定位与之一致（**属实**）。

---

## 6. 尚未验证内容（我未做、也无法做）

**A. 因环境阻断而未做**
1. 固定候选 SHA-256 复算（F-00）——`pwsh` 沙箱初始化失败，子代理同样失败。

**B. 因授权/范围而未做（本 Review 主动不越界）**
2. 任何 Windows host 探测（OS build、AppContainer/LPAC 可用性、profile 路径实际形态、`TEMP` 实际重定向值）。
3. 任何 profile 创建/删除、ACL 变更、注册表读取或写入。
4. 任何 smoke / build / Cargo / Tauri / PyInstaller / Sandbox 运行。

**C. 候选自身声明的未验证项（与候选 `:26` 一致）**
5. PyInstaller/Torch/Hugging Face 在目标 capability/ACL 集合内**能否正常运行**（兼容性）。
6. 后代进程是否确实全部留在容器内。
7. 注册表/私有 hive 的实际写入面。
8. 网络拒绝的实际行为。
9. 静态 hook/cache 闭包是否可证（仍为 `BLOCKED / NOT_VERIFIED`，`verification/P02/codex-hook-cache-closure-audit-r1.md:26`）。

**D. 外部资料核实未完成**
10. `CreateAppContainerProfile` / `DeleteAppContainerProfile` 的**权限要求**（F-06）：本会话 `web_search` 端点鉴权失败（HTTP 401），**我未能**取得并复核微软一手文档。此项必须由具备检索能力的一方以一手文档确认，**不得**凭记忆当作已核实结论。

---

## 7. 能否进入用户 scope review

**判定：暂时 `否`——但差距很小且路径明确。**

理由：
1. **对象绑定未成立**（F-00）。把未绑定 hash 的候选交给用户做 host-state 授权决定，违反项目既有的 exact-object 审查口径。
2. **scope delta 精度不足**（§4 的 D-1/D-2/D-3/D-4/D-6）。用户此刻只能回答"是否接受一个 AppContainer profile 大类"，**无法**回答"是否接受这些精确路径、这个权限模型、这套清理与残留断言"——而后者才是可执行、可审计的授权。
3. **权限模型未知**（F-06）可能直接推翻"Codex-only 非提权"前提，属于**决策前置条件**：若需提权，用户面对的问题就不是"接不接受 profile scope"，而是"要不要为一个需提权的方案重开授权"。

**满足以下条件后即可进入用户 scope review**（建议作为一次性交付）：
- ① 在可执行环境复算 hash 并与 `2febe1e2…a60c` 一致，或按不符规则改报 BLOCKED；
- ② 补齐 §4 的 D-1…D-6 与 §5 范围 3 的 7 项"实现前必须明确"；
- ③ 用一手微软文档闭合 F-06 的权限模型；
- ④ 产出新候选（建议 `r2`），并在 commit message/证据文件中登记其 SHA-256。

明确说明：**本 Review 不建议、也不授权**在此阶段创建 profile、探测 host 或运行 smoke。

---

## 8. 下一动作（单一、可直接转发）

**给 Codex（Lead / Architect / Integrator）**：

> 请在 `verification/P02/` 下产出 AppContainer 设计候选 `r2`，只做文档修订，保持 `Hard Build Barrier = EFFECTIVE`、`Build Gate = BLOCKED`、`build = NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7 = BLOCKED / NOT_RUN`，不得创建 profile、探测 host、运行 smoke/build/Cargo/Sandbox：
> (1) 逐条闭合 DSH Review 的 F-00…F-18，其中 F-01/F-02/F-03/F-04/F-05/F-06/F-07 为必闭合 P1；
> (2) 按 §4 的 D-1…D-6 把 profile scope delta 从"分类级"提升为"路径级 + 权限级 + 清理闭环级"；
> (3) 用微软一手文档确认 profile 创建/删除的权限要求（DSH 本会话检索端点 401，未能核实）；
> (4) 修订后**复算并登记新候选文件的 SHA-256**，把结论对象绑定到该 hash 而非任何 Git HEAD；
> (5) 提交时只改 `verification/P02/**` 证据路径与已授权的 boundary 段，不扩大 P02 Owner allowlist、不改 Task AC/依赖/STATUS/Plan/Index；
> (6) 完成后以 `dsh --profile headless --json` 派发本会话之外的 exact-hash 只读复审；复审通过后，**才**把"是否接受该 profile scope"提交用户裁决。
> 现有唯一阻断事实仍是 `verification/P02/codex-hook-cache-closure-audit-r1.md` 的 `BLOCKED / NOT_VERIFIED`，不得以本次设计修订推导任何 Gate 提升。

**给用户（若希望现在就推进决策）**：请先裁决**一个**前置问题——`AppContainer profile 是否需要提权即可免除，若非提权不可行，是否仍授权为该方案重开 host-state 授权**。该答案会决定 F-06 走向，也是后续 scope review 的唯一前提；在此之前不必对路径级清单做决定。

**无需并行创建重复 Review**：本报告为唯一在途 Review，且其结论**不绑定** hash，集成方在复算 hash 后应重新触发一次 exact-hash Review，而非复用本条绑定关系。

---

## 9. 只读与 Gate 声明

- 本 Review **未修改、未创建、未删除任何文件**；**未**修改 P02 Task/allowlist/Gate。
- **未**查询/探测 Windows host；**未**创建或删除任何 AppContainer profile；**未**变更任何 ACL/注册表。
- **未**运行 smoke、build、Cargo、Tauri、PyInstaller、Sandbox 或产品测试。
- Gate 口径维持：`P02 Hard Build Barrier = EFFECTIVE`；`Build Gate = BLOCKED`；`build = NOT_AUTHORIZED / NOT_RUN`；`hook/cache = BLOCKED / NOT_VERIFIED`；`AC1–AC7 = BLOCKED / NOT_RUN`；`wsb start = NOT_RUN`。本 Review **不批准** profile 创建、host smoke 或 build。
- 依据仓库 `AGENTS.md`，DSH 不得审核自己实现的变更；本候选作者非 DSH，角色互异成立。

**最终 decision = `NOT_VERIFIED`**（对象 hash 无法核验，不构成内容 mismatch，故不报 `BLOCKED / hash mismatch`；设计内容层面的 finding 结论为等同 `CHANGES_REQUESTED`：P0=1（验证能力）、P1=6、P2=8、P3=4）。