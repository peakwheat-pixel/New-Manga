# P02 AppContainer 隔离契约 r3 · 独立只读 Review（DSH，非作者）

- Reviewer：DeepSeek Harness（非作者；本对象由 Codex 编写，Reviewer 与作者角色互异，依据仓库 `AGENTS.md`）
- 审查对象：`verification/P02/appcontainer-isolation-contract-r3.md`（实际读取 145 行）
- Task 绑定对象：`doc/tasks/P02.md`（实际读取 366 行；重点第 68–70 行 `2026-10-10 本轮 PROJECT_ORCHESTRATION_AUTHORIZATION：AppContainer 精确隔离范围`）
- 前轮：`verification/P02/dsh-appcontainer-contract-r2-review.stdout.md`（347 行，`NOT_VERIFIED`，内容等同 `CHANGES_REQUESTED`，P0/P1/P2/P3=`2/5/8/7`，另有 C-00）
- 作者处置：`verification/P02/codex-appcontainer-contract-r2-adjudication.md`（35 行，逐项 disposition 表）
- 日期：2026-10-10（Asia/Shanghai）
- **decision = `NOT_VERIFIED`**（对象 SHA 无法在本会话独立复算；内容层面等价于 `CHANGES_REQUESTED`，见 §5）

---

## 1. 实际能力与 object binding

### 1.1 本会话实际能力（先行声明）

| 能力 | 状态 | 原文/证据 |
|---|---|---|
| `pwsh` 工具 | **不可用（初始化即失败）** | 3 次尝试（含更换 workdir 到 `C:\Windows\Temp`、更换命令形态）均返回同一条：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)` |
| SHA-256 / 字节数 / `git status` 复算 | **不可用**（依赖 shell） | 同上一行 |
| 沙箱升级（本会话未尝试） | 不可假定可用 | 前轮同环境记录：`sandbox escalation … requires approval, but no approval channel is available` |
| 文件读取（`read`） | **可用** | 本报告全部静态结论基于逐行读取的真实文件字节 |
| 修改文件 / 建 profile / 改 ACL·label·registry / 探针·Sandbox·Build·Cargo·Tauri·PyInstaller·产品测试 | **未执行（0 次）** | 见 §1.4 |

**能力结论**：本会话**无法独立计算任何 SHA-256 或字节数**，因此**不能声称 exact-object Review 成立**。这不是内容 mismatch，而是验证能力缺失（同 C-00 性质）。

### 1.2 对象绑定核验（尽力而为）

| 绑定项 | 声明值 | 本会话实测 | 判定 |
|---|---|---|---|
| 仓库根 | `G:/CODEX/New Manga` | 对象均存在于该路径下 | 成立（路径级） |
| 契约 SHA-256 | `30FA3DC1…429C3CC4` | **UNAVAILABLE** | **`object_binding=NOT_VERIFIED`** |
| Task SHA-256 | `74E37666…0B13CDE4` | **UNAVAILABLE** | **`object_binding=NOT_VERIFIED`** |
| branch=`main` | `main` | 未复算（依赖 shell）；未读 `.git` 元数据以免与 shell 限制混淆 | 未核验 |
| base HEAD / tree | `cddff584…` / `c25d051a…` | 未复算 | 未核验 |
| 对象存在/形态 | 契约 145 行、Task 366 行 | 逐行读取成立；r3 第 5 行自述 base HEAD/tree 与派发值字面一致 | 形态成立；绑定未核验 |
| Task 绑定段 | 新增 `PROJECT_ORCHESTRATION_AUTHORIZATION / AppContainer 精确隔离范围` | **位于第 68–70 行**，标题与字面一致 | 成立 |

**旁证（非独立核验）**：r3 第 6 行记录 Codex 用 `Get-FileHash -Algorithm SHA256` 复算 r2 契约=`8D84DA22…`、Task=`4915CE24…`；r2 adjudication 第 5 行同值。这只证明“Codex 记录的值与当次派发一致”。**r3 自身预期 SHA（`30FA3DC1…`）未写入 r3 文件内任何位置**，故本 Reviewer 即便能算也无从在该文件内比对声明值（→ P2-08）。

### 1.3 报告落盘路径

派发建议路径 `verification/P02/appcontainer-isolation-contract-r2-review.stdout.md`；r2 **实际**捕获路径为 `verification/P02/dsh-appcontainer-contract-r2-review.stdout.md`，且 r3 第 6 行与 adjudication 第 4 行**均已引用实际路径**（R2-20 已闭合）。本报告引用亦使用实际文件名。

### 1.4 只读声明

本会话**未**创建、修改、删除、stage 或 commit 任何文件；未创建/查询/删除任何 AppContainer profile；未改任何 ACL/label/registry；未运行 host/process probe、Windows Sandbox、Smoke、Build、Cargo、Tauri、PyInstaller 或产品测试；未读取任何被保护用户数据样本（未进入 `G:\CODEX\P02-scratch-build-source`）。读取范围仅限：上述 4 个仓库文件与 `.git` 之外的公开 Microsoft Learn 文档。用户授权未被当作任何 Gate/Test 证据。

---

## 2. 范围覆盖对账（r2 findings → r3 落点）

对 22 项内容 finding + C-00 逐项核对 Codex adjudication 与 r3 实际条文（**不采信 adjudication 自述，只看 r3 条文**）：

| finding | r2 级别 | adjudication | r3 实际落点 | 本次判定 |
|---|---|---|---|---|
| C-00 | 能力 P0 | 接受 | r3:6 承认 Codex 复算不升级 DSH；要求本轮 Reviewer 重新绑定 | **仍未绑定**（本会话无 shell）→ 保持 open |
| R2-01 | P2 | 部分接受 | r3:27（三项独立只读不存在证明、禁止猜 registry 键、不可证明即 `BLOCKED`） | **闭合**（→ P1-01 记录残余） |
| R2-02 | P3 | 接受 | r3:26（moniker 字面冻结、不随 HEAD 变、唯一实例、残留按 §5 恢复流程） | **闭合** |
| R2-03 | P3 | 接受 | r3:128（仅同 moniker 重试 `DeleteAppContainerProfile`、禁递归/通配、删除后残留为空断言、`CLEANUP_BLOCKED` 留现场） | **闭合** |
| R2-04 | **P0** | 接受 | r3:31（profile root/Temp 的 DACL/label/owner/file ID 写前单独保存；Low label 只限本轮 profile 树）、r3:77（`LABEL_SECURITY_INFORMATION` 查询需 `READ_CONTROL`／设置需 `WRITE_OWNER`）、r3:79（最小 Package SID DACL + Low label，继承须实测）、r3:80（逐对象快照/还原）、r3:118（`TokenIntegrityLevel`/`TokenMandatoryPolicy` 逐进程）、r3:119（Low+Medium/未标记 ⇒ 必拒，即使 DACL 允许） | **实质闭合**（残余 → P1-03、P3-14/15） |
| R2-05 | P2 | 接受 | r3:29（当前用户/impersonation 上下文、逐项记 token/HRESULT/返回身份/句柄；身份不符即阻断） | **闭合** |
| R2-06 | P3 | 接受 | r3:25（`EXTENDED_STARTUPINFO_PRESENT \| CREATE_SUSPENDED`）、r3:118（完整 token 字段点名，含 `TokenIsLessPrivilegedAppContainer`）、r3:124（OS build/architecture 重确认） | **闭合** |
| R2-07 | P3 | 接受 | r3:100–109 表**实际列出 5 个**（`TRANSFORMERS_CACHE`/`PIP_CACHE_DIR`/`UV_CACHE_DIR`/`TORCH_EXTENSIONS_DIR`/`XDG_DATA_HOME`） | **部分**：**`PYTHONUSERBASE` 缺失** → P2-01 |
| R2-08 | P3 | 接受 | r3:25、r3:30（零 capability 下 registry/COM 需求按预期否决处理并记 `BLOCKED`，不得放宽） | **闭合** |
| R2-09 | P2 | 部分接受 | r3:112（`TokenCapabilities` 空集快照 + synthetic negative controls；无安全有效控制则 Build Gate 保持 `BLOCKED`） | **闭合** |
| R2-10 | **P0** | 接受 | r3:17（输入/祖先/Windows 系统零修改，权限不足立即 `BLOCKED`，不得加 ACE/降标签/take ownership/提权）、r3:87（绝不加祖先 ACE，只测 `SeChangeNotifyPrivilege` 存在/启用） | **闭合** |
| R2-11 | **P1** | 收窄 | r3:14（变更仅限输出叶+本轮 canary，逐对象快照与还原）、r3:77（`WRITE_DAC`/`WRITE_OWNER` 实际有效权限）、r3:80（逐对象还原） | **实质闭合**（残余 → P2-02/P3-15） |
| R2-12 | P2 | 接受 | r3:85（组件边界、ordinal case-insensitive、`\\?\` 映射、拒绝短名/UNC/未解析 reparse/junction/mount point/hardlink/ADS）、r3:86（`GetFinalPathNameByHandleW`、volume/file ID、`FindFirstStreamW`、`FileHardLinkInfo`） | **闭合**（成本上限未给 → P3-21） |
| R2-13 | P2 | 接受 | r3:56（旧 HostFolder TSV 标为 WSB 期快照，不作当前 clone 判定；clone HEAD/tree/无 remote/alternates/hardlink 重采集） | **闭合** |
| R2-14 | P2 | 接受 | r3:58（原文承接 Task:81：记录原始工作区字节 hash 与 Git blob，仅 Gate 明列的生成差异范围，其他 tracked 差异即阻断） | **闭合** |
| R2-15 | **P1** | 接受 | r3:88（真实 impersonation token、`TOKEN_QUERY`、`MapGenericMask`、`GENERIC_MAPPING`、`DesiredAccess`、`PrivilegeSet`、`AccessStatus`、`GrantedAccess`、token 来源/生命周期；明确 `AccessCheck` 只证 DACL、不含 MIC、不得反证可写）、r3:81（正向/负向 canary 配对） | **实质闭合**（负向对照污染风险 → P2-02） |
| R2-16 | **P1** | 接受 | r3:21（Task:79 alias 写成功仍判 `BLOCKED`，正向 canary 用不同新路径）、r3:81（`smoke-readonly-probe` 仍为只读 alias；独立新路径 `lpac-write-control`） | **闭合**（路径归属歧义 → P2-05） |
| R2-17 | **P1** | 接受 | r3:125（`git status --porcelain=v1 --untracked-files=all -z` 原始字节清单与 digest、不沿用旧 203 数字、dirty/untracked 原始字节 SHA-256、路径/编码/EOL 不规范化、未 hash 标 `UNKNOWN`）、r3:127（排除轮次自产物、profile/private registry、scratch outputs、两处 canary，逐路径列明） | **实质闭合**（排除集未冻结成 manifest → P2-07） |
| R2-18 | P2 | 接受 | r3:116（resume 前 handle table 快照、`bInheritHandles=FALSE`、白名单 stdio）、r3:117（Job completion port `JOB_OBJECT_MSG_NEW_PROCESS`/`EXIT_PROCESS`、丢失/溢出计数、`KILL_ON_JOB_CLOSE` 且无 breakaway ⇒ 完整子进程边界、每 PID+creation time 单独取 token） | **闭合** |
| R2-19 | **P1** | 接受 | r3:52（Windows loader/runtime 只用 OS 现有权限；只读核对现有 `S-1-15-2-2` ACE 并记精确路径与 mask；该 ACE 仅候选条件；缺项/不可读/需增添系统 ACE/轨迹不可冻结 ⇒ `BLOCKED`；不授予 `C:\Windows`、`System32`、`WinSxS`、盘符级权限） | **闭合但留下空集风险** → P1-02 |
| R2-20 | P3 | 接受 | r3:6 实际路径引用；r3:131 标题为「Microsoft 一手依据（API 语义，不代表本机已实测）」 | **闭合**（引用集缺项 → P2-04） |
| R2-21 | P3 | 接受 | r3:7 台账含 `hook/cache/child-process closure=BLOCKED / NOT_VERIFIED` | **闭合** |
| R2-22 | P2 | 接受 | r3:120（只读检查全局及 exact executable 的 `LocalDumps`/WER policy 与解析出的 dump 目的地，不修改 registry/policy；可能越界 dump/无法检查/crash/新 dump ⇒ `BLOCKED` 并保留）、r3:139（`SetErrorMode` 不替代 policy 检查） | **闭合**（检测面未列 → P2-06） |

**覆盖统计**：22 项内容 finding 中，18 项**实质闭合**，4 项**部分闭合**（R2-01 方法仍空、R2-07 缺 `PYTHONUSERBASE`、R2-11/R2-15 有残余、R2-17 排除集未冻结）；C-00 因本会话无 shell **仍未闭合**。**未遗留 r2 的 P0**（R2-04、R2-10 均已按一手文档口径重写）。

---

## 3. 逐项 Findings

### 3.1 P1

#### P1-01 — profile / private registry「创建前不存在」只有阻断语句，没有可执行只读方法
- **路径/条款**：`appcontainer-isolation-contract-r3.md:27`；Task:70（「若不能证明即 `BLOCKED`，不猜测键路径、不创建」）
- **影响**：条款正确地把「无法证明」写成 `BLOCKED`，且明确禁止猜键路径——这一点符合 fail-closed。但三项检查（moniker profile、local-data 目录、**当前用户私有 registry 存储**）中，前两项有可执行的只读落点（`%LOCALAPPDATA%\Packages\<moniker>`；`GetAppContainerFolderPath` 的文档语义），**第三项在 r3 中没有可执行的只读方法**：既不许猜键路径，又未给出可用只读 API，于是 profile 创建前置条件在任何实现下都不可满足。这不是「绕过前置条件」（r3 明确不绕过），而是**执行路径整体停在创建前**，且没有任何证据能区分「不存在」与「无法检查」。r2 的 R2-01 建议「写死三项检查及其 API/注册表位置」只完成了一半：写死了「禁止猜」，没有写死「用什么查」。
- **最小修正**：在 §2 增加一段「不存在性证明方法」，逐项写死**允许的只读检查手段**与**证据字段**：① moniker 目录 = 对 `%LOCALAPPDATA%\Packages\<moniker>` 做规范化路径存在性 + `GetFileAttributesW` 返回 `INVALID_FILE_ATTRIBUTES`/`ERROR_PATH_NOT_FOUND` 的记录（同步记 volume/file ID 查询结果）；② 用 `DeriveAppContainerSidFromAppContainerName` 派生 SID 后调用 `GetAppContainerPath`/`GetAppContainerRegistryLocation` 类 API 的返回码与 `ERROR_NOT_FOUND`/`E_INVALIDARG` 语义留证；③ 私有 registry 存储：**只允许**用「Windows 文档化的 AppContainer 存储位置在当前用户 hive 内」这一条，若引用就给出对应 Microsoft Learn 一手链接与精确键路径，并使用纯只读 `RegOpenKeyExW(KEY_READ)`（不 `KEY_SET_VALUE`、不创建）记录 `ERROR_FILE_NOT_FOUND`；若无法引用一手依据，则**显式写明本项在当前设计下不可证明 ⇒ 永久 `BLOCKED`，本契约不得调用 `CreateAppContainerProfile`**。二者都必须在该条内写清，不得留给实现者选择。

#### P1-02 — 系统对象只读闭包：`S-1-15-2-2` 缺项时无任何回退路径，且「读 DACL」本身可能先被阻断
- **路径/条款**：r3:52；对照 r3:17、r3:87
- **影响**：r3 正确地禁止了宽兜底（不授予 `C:\Windows`/`System32`/`WinSxS`/盘符级权限），也正确地拒绝在系统对象上加 ACE。但由此产生一个**空集**：若只读实测发现 loader/runtime 所需文件 DACL 中**没有**适用的 `S-1-15-2-2` ACE，r3 只有 `BLOCKED` 一个出口，没有任何「实测—冻结—登记」的第二阶段（r2 的 R2-19 曾并列给出该选项）。更基础的是：要「核对 DACL 是否存在该 ACE」必须先对系统对象执行 `GetNamedSecurityInfoW` 读取 DACL，这需要该对象的 `READ_CONTROL`；`C:\Program Files (x86)\...` 与 `C:\Windows\...` 下的对象由 TrustedInstaller 拥有，非提权 controller 是否具备 `READ_CONTROL` **本身就是一个未测量的前提**（r2 §3.4 A3/A5）。若读 DACL 即被拒，r3 的「只读核对」通道在第一步就失败，而条款未说明此时记什么证据、如何区分「缺 ACE」与「无权限读 DACL」。
- **最小修正**：① 在 §3 明确记录两类不同失败：`S-1-15-2-2` ACE 缺失（→ `BLOCKED / SYSTEM_ACL_MISSING`）与 `READ_CONTROL` 被拒（→ `BLOCKED / SYSTEM_ACL_UNREADABLE`），字段与 HRESULT 分别留证；② 显式写明本契约**不采用**两阶段「实测—冻结—登记」路线，若缺 ACE 则本机 AppContainer 方向在「非提权 Codex-only」前提下判定为不可实施，需由用户裁决（放弃该方向 / 另行授权提权 / 接受 Build Gate 长期 `BLOCKED`）；③ 保留「不授予系统/盘符级权限」不变。

#### P1-03 — 未登记 Low-label 与既有文件的写冲突：正向写入前置条件在「已存在输出树」上不成立
- **路径/条款**：r3:79（只对 exact output leaf 与 canary 设置最小 Package SID DACL 与 Low mandatory label；继承效果由 synthetic probe 实测）、r3:119（Low IL + Medium/未标记 ⇒ 必拒，即使 DACL 允许）、r3:78（目标存在且含未登记内容即 `BLOCKED`）、Task:74–77（输出根允许多轮复用，含 `npm-cache/`、`cargo-home/`、`target/*`）
- **影响**：r3 已正确写出「Low 不能写 Medium」的 MIC 规则，但没有把这个规则**施加到「已存在的输出树」**上。MIC 的关键语义是：给目录设置 Low label **不会**事后降低其内部既有文件的 label；当 Low 进程在低标签目录内新建文件时，新文件继承目录的 Low label（可写），但对**既有 Medium/未标记文件**执行覆盖/删除仍会被拒。Task:74–77 允许输出根被多轮构建复用（npm/cargo/PyInstaller 的典型行为就是改写既有中间产物），于是「目标存在」这一最常见情形下，Low 进程将无法改写既有内容——失败原因在 MIC，而条目一旦被误判为「隔离拒绝」，会把基础设施限制当成隔离证据。r3:78 的「存在未登记内容即 `BLOCKED`」是前置拦截，但它拦的是「内容身份」，不是「label 可写性」，两者不等价。
- **最小修正**：在 §4「scratch DACL/mandatory-label 操作约束」增加一条：明确「设置 Low label 不改变既有子对象标签；Low 进程对既有 Medium/未标记文件的覆盖/删除必然被 MIC 拒绝」，并给出二选一处置：① 本轮写目标以 `tmp/` 或按 §4.2 新建 exact leaf 为**唯一**写入口，既有输出树仅作只读或整体新建，不复用；② 逐文件登记既有对象的 mandatory label 与 policy 并证明其在 Low 下可写，否则 `BLOCKED`。同时明文禁止把 MIC 拒绝记录为「隔离生效」证据。

### 3.2 P2

#### P2-01 — `PYTHONUSERBASE` 闭环缺失（venv/user-site 脚本可写回用户 profile）
- **路径/条款**：r3:92、r3:100–109（环境表）；r2 R2-07 点名的 6 项中 5 项已列
- **影响**：Task:40 与 r3 §3 绑定的 P02 pinned venv 为 `G:\CODEX\New Manga.task-envs\m2ac5-build`；若该 venv 允许 user site 或 Python 以 `--user`/`PYTHONUSERBASE` 派生路径解析，脚本入口会在 **`%APPDATA%\Python`** 或 `%APPDATA%\Roaming\Python` 写入，而该位置不在 12 个只读输入根、不在 scratch 输出根、且被 §5 显式禁止（「用户既有 AppData」）。r3 未设 `PYTHONUSERBASE`，也未声明 `PYTHONNOUSERSITE=1`。
- **最小修正**：在 §6 表内新增 `PYTHONUSERBASE` → scratch `python-cache/userbase`（或等价 scratch 子树）并设 `PYTHONNOUSERSITE=1`；或在同条明确写「不设 `PYTHONUSERBASE`，但任何 `PYTHONUSERBASE`/user-site 派生路径出现即 `BLOCKED`」并给出检测方法（回读 `site.USER_BASE`/`sysconfig` 路径）。

#### P2-02 — 负向 DACL control 未与父目录 ACE 继承 / Low label 隔离，可能污染对照有效性
- **路径/条款**：r3:81（「负向 DACL control 使用另一个新 scratch 子目录且不授 Package SID ACE；失败路径必须返回明确拒绝，其他错误不算负向通过」）、r3:79（ACE 不得继承到列出的输出根以外）、r3:80
- **影响**：r3 已要求「明确拒绝」而排斥其他错误（方向正确），但未隔离两种污染源：① 若负向 control 目录放在 `verification/P02/tmp/`（或另一已授权输出根）**内部**，父目录上为本轮设置的最小 Package SID 写 ACE 会被子目录**继承**，负向对照就不再是「无授权」，拒绝原因也不再来自 DACL；② 若父目录或其自身被设为 Low，拒绝可能来自 MIC 而非 DACL，与 r3:88 的「`AccessCheck` 只证 DACL」证据链无法配对。r2 的 R2-15 建议要求「同一 API、同一 `DesiredAccess` 的对象配对」，r3 未写死负向对象的父链安全项。
- **最小修正**：在 §4.5 写明负向 control 的三项隔离条件：其父链上**不得**存在本轮添加的 Package SID ACE（或置于独立非授权父目录），其自身及父目录保持原始 mandatory label/policy（不变为 Low），并给出拒绝码判别表——只接受 `ERROR_ACCESS_DENIED`/`E_ACCESSDENIED` 且必须由 `AccessCheck` 的 DACL 结果**与**实际写入尝试**双向**印证；出现 MIC 类拒绝（`STATUS_ACCESS_DENIED` 的标签路径）时记为 `INCONCLUSIVE`，不得算负向通过。

#### P2-03 — `AccessCheck` 证据字段自相矛盾，且未排除 `WRITE_OWNER` 绕过路径
- **路径/条款**：r3:88（要求记 `AccessStatus`）
- **影响**：`AccessCheck` 的输出参数是 `AccessStatus` 与 `GrantedAccess`；`GrantedAccess` 才是授予掩码，`AccessStatus` 是布尔成功标志，把「返回值、`AccessStatus`、`GrantedAccess`」并列为三个语义并列字段会让留证字段产生歧义。另：`AccessCheck` 只按 DACL + token 判定，**不反映 `WRITE_OWNER`/`WRITE_DAC` 带来的隐式能力差异**（例如拥有 `WRITE_DAC` 的主体可改写 DACL 从而获得写能力），而 r3:88 又禁止对被保护路径做真实写入尝试。因此 protected-path 写禁的「只接受 DACL + mandatory label + 路径权限证据」这句里，**必须**明确列出 `WRITE_DAC`/`WRITE_OWNER` 的实测值，否则证据集合不足以支撑「不可写」结论。
- **最小修正**：把字段改写为 `BOOL return`、`AccessStatus`、`GrantedAccess`（分别注明语义），并在 protected-path 判定中显式加入「controller/token 对目标的有效 `WRITE_DAC`/`WRITE_OWNER`（含 owner 身份）」字段；出现任一为真时，把该目标的写禁结论降级为 `INCONCLUSIVE / BLOCKED`。

#### P2-04 — Microsoft 一手依据清单缺 3 项被契约实际依赖的依据
- **路径/条款**：r3:131–139
- **影响**：契约实际依赖但清单未引：① `TokenIsLessPrivilegedAppContainer`/`TokenIntegrityLevel`/`TokenMandatoryPolicy` 等所需 **`TOKEN_INFORMATION_CLASS`**（r3:118 逐字段点名却无依据）；② **`SeChangeNotifyPrivilege`**（r3:87 的依据，「Bypass traverse checking」）；③ `S-1-15-2-2` = **`ALL RESTRICTED APPLICATION PACKAGES`**（r3:52 的核心依据）。清单被称为「一手依据」，缺项会让下游无法区分「文档化事实」与「设计者假设」。
- **最小修正**：在 §9 补三条链接（`TOKEN_INFORMATION_CLASS`、`SeChangeNotifyPrivilege`/`Privilege Constants`、`ALL APPLICATION PACKAGES`/well-known SID），并保留「仅为 API 语义，不代表本机已实测」的总声明。

#### P2-05 — 正向 canary 路径 `verification/P02/tmp/lpac-write-control/` 的根归属歧义，且 §4 输出根表未收编 `tmp/`
- **路径/条款**：r3:79（`verification/P02/tmp/lpac-write-control/`）、r3:81（同路径；`verification/P02/tmp/smoke-readonly-probe/`）、r3:60–73 表（`tmp/` 与 `verification/P02/cargo-target/` 作为 **scratch 相对路径**）、r3:14（授权范围 2 只覆盖「P02 Task 精确列出的 scratch 输出子树」）
- **影响**：两处相互矛盾的可能读法：(a) 该路径落在**主仓** `G:\CODEX\New Manga\verification\P02\tmp\`——但主仓在 §5 的 deny 集合内，Task 的 Owner allowlist 也不含 `verification/P02/tmp/`，且 r3:14 的授权只指向「Task 精确列出的 scratch 输出子树」，于是正向 canary 的主机写入**没有明确授权落点**；(b) 该路径落在**固定 scratch clone** 内（与 Task:79 的 alias 同根）——那就需要在 §4 表内显式声明，且 §4 表当前**没有** `verification/P02/tmp/` 这一行。两种读法给出不同的 host 写入面，而这是 §4 全部 ACL/label 变更的核心对象。
- **最小修正**：在 §4 表内新增一行明确根归属（建议固定为 scratch clone 内的 `verification/P02/tmp/`，主仓 `verification/P02/tmp/` 保持 deny），并把 §4.3、§4.5 中的 `verification/P02/tmp/lpac-write-control/`、`verification/P02/tmp/smoke-readonly-probe/` 改写为该根下的完整相对路径；若确实要在主仓建 canary，则必须由 Codex 在 Task 中登记该精确例外路径，并同步修改 §5 deny 集合表述。

#### P2-06 — 意外写入面（`%LOCALAPPDATA%\CrashDumps` / WER store）未列入只读检查面
- **路径/条款**：r3:120、r3:127
- **影响**：r3 要求只读检查 WER `LocalDumps` policy 与「解析出的 dump 目的地」，并规定新 dump 出现即 `BLOCKED`。但它未点名**默认**（policy 未配置时）的两个落点：`%LOCALAPPDATA%\CrashDumps` 与 `%ProgramData%\Microsoft\Windows\WER\ReportQueue|ReportArchive`。跨容器 WER 写入恰恰发生在**策略未配置**的默认路径上（r2 R2-22 的原意），而 r3:127 的排除集只列本轮 evidence/profile/scratch/canary，未预先把这两个默认路径登记为「预期外、出现即阻断」的检测面。
- **最小修正**：在 §7 或 §8.1 增加「WER/dump 检测面」清单：exact 列出 `%LOCALAPPDATA%\CrashDumps` 与 `%ProgramData%\Microsoft\Windows\WER\**` 的**只读**存在性/条目计数前后快照，写入 §8.4 的排除集**禁止**清单（即它们的新增等于 `BLOCKED`，不是排除项）；继续不修改任何 registry/policy。

#### P2-07 — §8.4 的「例外逐路径列明」未冻结成 manifest，仍会因本轮自产物产生不可判定的 MATCH/UNKNOWN
- **路径/条款**：r3:127
- **影响**：r3 已正确要求「前后比较单独排除本轮明确允许的新增 evidence、profile/private registry、scratch outputs 和两处 canary」。但「本轮明确允许」的判定时点未固定：DSH 报告、派发 prompt、`.exit`/`.stdout.log` 等审查产物会在**同一轮**持续出现（r2 审查自身就产生了 3 个新文件，这是项目已有事实）。若不先把排除集以**路径清单 + 判定时点**冻结，§8.4 的「其他 root dirty/untracked 哈希必须逐项 MATCH」会在同轮内自相矛盾，最终只能落到 `UNKNOWN`，也让 Build Gate 无从绑定。
- **最小修正**：在 §8.4 写明排除集为「在 §8.2 采集 digest 之前已存在的精确路径清单（含 glob 的精确展开）+ 采集时点」，并要求该清单随 digest 一起固定为轮次 artifact；采集时点之后出现的新路径不进入排除集，出现即 `UNKNOWN`（不得记 MATCH）。

#### P2-08 — 契约未内嵌自身预期 SHA 或候选字节摘要，Reviewer 无法在对象内完成绑定比对
- **路径/条款**：r3:6（只记录 r2 契约/Task 的复算值）
- **影响**：派发绑定给出 r3 预期 SHA `30FA3DC1…`，但 r3 文件内没有任何位置声明本次契约的预期 SHA、LF/字节数或 Git blob 摘要。在具备 shell 的环境，Reviewer 只能算出一个数而**无法与对象内声明值比对**；在不具备 shell 的环境（本会话）则连「比对目标是否存在」都无法确认。
- **最小修正**：在 r3 头部（或紧邻 §精确下一步）增加一行「本文件（canonical LF/UTF-8）字节数=SHA-256=…」，并说明该值为候选提交后的 blob 摘要、由派发 prompt 与契约双向声明；或明确写出「本文件 SHA 只由派发 prompt 声明，对象内不自我声明」这一口径，避免下游把「无声明」误读为「无绑定」。

### 3.3 P3

- **P3-09 — 未声明 Low label 设置的最小性/non-elevated 能力前提**（r3:31、r3:77、r3:119）：设置 `LABEL_SECURITY_INFORMATION` 需要 `WRITE_OWNER`（r3 已写），但 r3 未要求登记「是否需要用 `SeSecurityPrivilege`/其他特权」、也未写明失败即 `BLOCKED` 的对应条目。**最小修正**：在 §4 增加「任何需要提权或 ACL/label 写入失败的处置 = `BLOCKED`，不得提权」的显式句子。
- **P3-10 — §8.5 的字段名漂移**（r3:128 写作「profile folder/private storage」；§2 用词是 local-data 根 / private registry storage）：**最小修正**：统一为 §2 的三项术语，使删除后残留断言与创建前断言一一对应。
- **P3-11 — 恢复后一致性断言的对照口径未定义**（r3:80）：r3 要求逐对象还原，但未要求「还原后重新读取并与快照逐字段比对（含 owner/group、DACL ACE 集合、label/policy、file ID）」。**最小修正**：加一句还原后复读并逐字段断言相等，差异即 `CLEANUP_BLOCKED`。
- **P3-12 — 「表外对象只读」的显式句子缺失**（r3:58）：Task:81 的约束已承接，但 r3 未写出 r2 R2-14 建议的收窄句「写入表之外的对象（含 tracked 源文件）只读」。**最小修正**：在 §4 表后补一句显式限定。
- **P3-13 — `ERROR_ALREADY_EXISTS` 分支的残留处置**（r3:28）：r3 规定出现即停止、不复用/不覆盖/不删除，但未说明「若既存 profile 为本轮失败残留」时是否允许按 §8.5 走 `DeleteAppContainerProfile`。**最小修正**：写明二者关系（或明确本契约下 `ERROR_ALREADY_EXISTS` 一律 `BLOCKED`，残留处理需新授权登记）。
- **P3-14 — MIC 拒绝的负向证据登记缺失**（r3:119）：r3 正确要求「Low+Medium 必拒」，但未要求在 Gate 证据中登记一条**真实**的 MIC 拒绝事件（Medium 目标 + Low token，期望 `ERROR_ACCESS_DENIED`），使「MIC 生效」目前只有规则文本而无观测。**最小修正**：把一条 MIC 负向 control 列入 §8.6 的 Gate 证据项；无安全执行条件时保持 `BLOCKED`。
- **P3-15 — 路径身份的正确性**（r3:56、r3:72）：未明确 `G:\CODEX\New Manga.task-envs` 是主仓的**兄弟组件**而非其前缀子路径（r2 R2-12 已要求写死）。**最小修正**：在 §5 补一句组件级澄清，并说明 `G:\CODEX\New Manga.worktrees` 同为兄弟组件、但整体保持 deny。
- **P3-16 — 非法/异常 moniker 形状未列出**（r3:26 已固定字面值 35 字符、字符合法）：**最小修正**：补一句「moniker 为字面常量，不派生、不改写；长度/字符集校验只需指向 `CreateAppContainerProfile` 的输入约束」。

**Findings 总数：15（P0=0，P1=3，P2=8，P3=8）**，另 C-00（验证能力）仍未闭合。注：上面 P3 小节条目编号为 P3-09…P3-16，共 8 条；P2-01…P2-08 共 8 条；P1-01…P1-03 共 3 条。

---

## 4. 能否进入「无 profile、无 ACL 修改」的只读 OS preflight

**可以进入——但仅限纯测量形态，且必须形如 r2 §5 建议与本报告 §1.4 的约束。**

理由：

1. r3 已把三项**写入**动作全部加以显式 gate：profile 创建需三项不存在性证明（r3:27–28）；ACL/label 变更需预检 + 逐对象快照 + 可逆（r3:77–80）；Build 需独立 Gate `PASS` 后另行记录（r3:129）。只读 preflight 本身不触碰任何一项。
2. 本报告的 3 项 P1 **全部是「用测量来关闭」的条目**：P1-01（不存在性方法/证据）、P1-02（系统 ACL 与 `READ_CONTROL` 的可读性）、P1-03（既有输出树的 label 可写性）——正是只读 preflight 要产出的数据。把它们当作「preflight 前置」会形成死锁，故应把它们当作 preflight 的**必测项与必录证据**。
3. 无 P0 内容缺陷；r2 的两项 P0（MIC、祖先 ACE）已实质闭合。

**放行边界（必须逐条遵守）**：

- 允许：`GetNamedSecurityInfoW`/只读 DACL、label、owner、file ID、reparse 查询；`SeChangeNotifyPrivilege` 查询；`TokenIntegrityLevel`/`TokenMandatoryPolicy`/`TokenCapabilities` 查询；`%LOCALAPPDATA%\Packages\<moniker>`、AppContainer storage 键的存在性**只读**查询；`Get-FileHash` 级别的主仓/输入根只读 hash；WER/`LocalDumps` 只读查询；系统 loader 文件的 `S-1-15-2-2` ACE 只读核对。
- **禁止**：`CreateAppContainerProfile`、`DeleteAppContainerProfile`；任何 `SetNamedSecurityInfo`/`WRITE_DAC`/`WRITE_OWNER`/label 设置；任何 registry 写入；任何对受保护路径的真实写探针；Sandbox/`wsb start`/Smoke；Build/Cargo/Tauri/PyInstaller/runner/Vitest/产品测试。
- 任一必测项判定为「无法检查」时，记录 `BLOCKED / NOT_VERIFIED` 并停止，不得以「未观测到问题」替代。

**批准语义声明**：本 Review **只批准文档与只读测量**，不批准 profile 创建、不批准任何 ACL/label/registry 变更、不批准 Smoke/Build、不解除 Hard Build Barrier。

---

## 5. 未覆盖风险与最终判定

### 5.1 未覆盖风险（本 Review 无法关闭）

1. **C-00 未闭合**：本会话无 shell，r3 与 Task 的 SHA/字节数未独立复算；全部内容结论绑定到「本会话实际逐行读取的该两个路径的文件内容」，不绑定任何 SHA、Git blob 或 tree。下游不得把本报告当作 exact-object 证据复用。
2. **host 侧事实未测**：非提权 controller 是否可 `CreateAppContainerProfile`/`DeleteAppContainerProfile`、是否可读系统对象 DACL、是否已具备 `S-1-15-2-2` ACE 预置、Low label 在目标卷/文件系统上的继承实际行为，全部未观测（本 Review 未探测 host）。
3. **能力面的运行时否决无证据**：网络/registry/COM 的真实拒绝目前只有设计依据（r3:112 已如实写成「无证据即 `BLOCKED`」）；`pyinstaller`/Torch/Transformers 在零 capability + Low IL 下的完整写入闭包仍未闭合。
4. **P02 状态未被本 Review 提升**：与 r3:7、Task:70 一致——profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、hook/cache/child-process=`BLOCKED / NOT_VERIFIED`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。
5. **未审旁证工件**：`scope-delta`、`build-preflight-*`、`owner-transfer-*`、R2 manifest 等超出本次绑定对象，未复核。

### 5.2 逐项结论摘要

| 项 | 结果 |
|---|---|
| 实际能力与 object binding | shell 不可用 ⇒ **`object_binding=NOT_VERIFIED`**；内容审查有效 |
| r2 finding 覆盖 | 22 项：18 实质闭合、4 部分闭合；**r2 两项 P0 已闭合** |
| 新增发现 | **P0=0，P1=3，P2=8，P3=8（共 15）**，另 C-00 未闭合 |
| 授权/Gate 语义 | 无任何提升；不批准 profile/ACL/registry/Smoke/Build |
| 只读 OS preflight | **可以**（纯测量形态，见 §4 边界） |
| 写入动作（profile/ACL/label/registry/Build） | **不可以**，维持 `BLOCKED` |

### 5.3 decision

**decision = `NOT_VERIFIED`**

- **对象绑定层面**：r3 与 Task 的 SHA-256 在本会话**不可独立复算**（`pwsh` 沙箱 `grantWrite(G:\CODEX\New Manga)` 在 3 次不同调用形态下均失败），故本报告不能声称绑定到 `30FA3DC1…` / `74E37666…`。按前轮 C-00 先例，「不可核验」≠「mismatch」，故降级为 `NOT_VERIFIED` 而非 `BLOCKED / hash mismatch`。
- **内容层面**：**等同 `CHANGES_REQUESTED`**。r3 相比 r2 是实质性改进：MIC/Low label 已进入写入前置条件（R2-04）、祖先与系统对象已改为零修改并删除「祖先最多 read-execute」（R2-10）、ACL/label 变更已收窄到精确叶并配逐对象快照还原（R2-11）、`AccessCheck` 已被明确限定为 DACL-only（R2-15）、两处 canary 语义已分离（R2-16）、hash 口径与排除集已写实（R2-17）、Job completion port 与句柄快照已点名（R2-18）。但仍有 3 项 P1 未闭合：创建前不存在性检查**没有可执行方法**（P1-01）、系统对象闭包在缺 ACE 时**无任何回退路径且读 DACL 前提未测**（P1-02）、**既有输出树在 Low label 下的可写性未纳入前置条件**（P1-03），另有 8 项 P2 需最小修正（`PYTHONUSERBASE` 缺项、负向 control 污染、`AccessCheck` 字段与 `WRITE_OWNER`、Microsoft 依据缺 3 项、canary 路径归属与 §4 表缺 `tmp/`、WER 默认 dump 面、排除集未冻结成 manifest、契约未内嵌自身 SHA）。
- **纯文档批准，不代表 OS 测量或 Gate 放行**。

---

## 6. 推荐下一步（单一、可直接转发）

**给 Codex（Lead / Architect / Integrator）**：

> 请对 `verification/P02/appcontainer-isolation-contract-r3.md` 做**纯文档修订**，产出 r4，并保持 `Hard Build Barrier=EFFECTIVE`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`OS preflight=NOT_RUN`，不创建 profile、不改 ACL/label/registry、不探测 host、不运行 Sandbox/Smoke/Build/Cargo/Tauri/PyInstaller/产品测试：
> (1) 必闭合 P1：P1-01（§2 增补「不存在性证明方法」，逐项写死允许的只读 API/registry 检查与证据字段，或显式声明该项不可证明 ⇒ 永久 `BLOCKED` 且不调用 `CreateAppContainerProfile`）；P1-02（§3 区分 `SYSTEM_ACL_MISSING` / `SYSTEM_ACL_UNREADABLE`，写明是否采用两阶段路线与否决判定，保留不授予系统/盘符级权限）；P1-03（§4 写明 Low label 不改变既有子对象标签，给出「新建 exact leaf 为唯一写入口」或「逐文件证明可写」二选一，并禁止把 MIC 拒绝计为隔离证据）。
> (2) 处置 8 项 P2：`PYTHONUSERBASE`/`PYTHONNOUSERSITE`；负向 DACL control 与父链 ACE/Low label 隔离及拒绝码判别；`AccessCheck` 字段语义与 `WRITE_DAC`/`WRITE_OWNER` 证据；§9 补 `TOKEN_INFORMATION_CLASS`/`SeChangeNotifyPrivilege`/`S-1-15-2-2` 三条一手链接；canary 路径根归属与 §4 表新增 `verification/P02/tmp/` 行；`%LOCALAPPDATA%\CrashDumps` 与 `%ProgramData%\Microsoft\Windows\WER\**` 只读检测面与禁止排除；§8.4 排除集冻结为路径清单+采集时点；r3 头部内嵌本文件 canonical-LF 字节数与 SHA-256（或声明不自我声明的口径）。
> (3) 处置 8 项 P3（P3-09…P3-16），至少给出 closed / explicit disposition 二选一。
> (4) 修订后复算并登记新候选 SHA-256 与字节数，并注明本轮 DSH 的 object binding 未成立（C-00），需在可执行 shell 环境重算 r3 与 Task 的 hash。
> (5) 不改 P02 Owner allowlist、产品 AC、现有 scratch 输出 allowlist、Task 依赖或用户数据保护要求；不扩大任何路径授权。
> (6) 修订后派发**本会话之外**的 exact-hash 只读复审。在复审无未解决 P0/P1 且 adjudication 通过前，**只**可进行本报告 §4 所述纯测量只读 OS preflight；profile 创建、ACL/label/registry 变更、Smoke 与 Build 继续 `BLOCKED`。

**给用户**：当前**无需**新授权。唯一可能需要用户裁决的情形是：只读 preflight 证明非提权 controller **无法**读取系统对象 DACL 或系统未预置 `S-1-15-2-2` ACE，或无法以非提权方式证明私有 registry 存储不存在——则该 AppContainer 方向在「非提权 Codex-only」前提下不可实施，届时需决定放弃该方向、另行授权提权方案，或接受 Build Gate 长期 `BLOCKED`。

---

*报告结束。本报告为只读审查产物，对任何实际 Gate 均无提升；不得据此批准 profile 创建、ACL/registry 修改、Smoke 或 Build。*
