# P02 AppContainer contract r7 / Phase A manifest r3 独立内容 Review（DSH 非作者）

## 0. 审查范围、方法与边界

- 本轮仅用 `read` 工具逐份读取以下**确切文档全文**，未使用 shell / PowerShell / Git / hash / Windows API / 外部网络，未运行任何 OS measurement、profile API、ACL/registry 操作、probe、build、Cargo/Rust/Tauri 或 Windows Sandbox，未创建 / 修改 / 暂存 / 删除任何文件：
  - `doc/tasks/P02.md`（396 行）
  - `verification/P02/appcontainer-isolation-contract-r7.md`（178 行）
  - `verification/P02/appcontainer-readonly-preflight-r3.md`（48 行）
  - `verification/P02/dsh-appcontainer-contract-r6-review.stdout.md`（190 行）
  - `verification/P02/codex-appcontainer-contract-r6-adjudication.md`（50 行）
  - 计数核验源：`verification/P02/appcontainer-readonly-preflight-r2.md`（47 行）、`verification/P02/appcontainer-isolation-contract-r6.md`（177 行）
- **正式 `object_binding = NOT_VERIFIED`**：本会话不具备且被禁止使用 shell/hash/Git，未复算 prompt 中任何声称 SHA-256（Task `AC200DA1…FF72`、r7 `7FBFFE65…0ADF`、r3 `AC45329A…BC43`、r6 report `D8821DF6…C96`、adjudication `103CBD5F…3759`），未读 `.git`，未核验任何 OS 状态。下列结论只绑定“本会话读到的上述路径文本与行号”，不是 exact-object hash Review。文中凡出现 SHA，均为**转述文档内部声称值**，不代表已核验。
- 本 Review 只审内容，不替代 Codex OS 验证、adjudication 或 Gate 放行；我不负责 Gate。

---

## 1. 内容 Decision

**`APPROVED`（内容层）。**

- 计数：**P0/P1/P2/P3 = `0/0/0/5`**，其中 5 项 P3 全部**非阻断**、**不影响安全或范围**（见 §5）。
- **DSH-R6A-01..12 全部 `CLOSED`**（逐项证据见 §2），未发现“只写在 adjudication 自述里、r7/r3 正文无落地”的空头修正。
- 因不存在任何 open 的 P0/P1/P2，本内容 Review **不再构成 Phase A 的内容层阻断**；但 `object_binding=NOT_VERIFIED`，且按契约 r7 `:156`、`:175-177`，Phase A 仍须 Codex 逐项 adjudicate + 逐文件 SHA/object pin 完成后才可执行。**本 Review 不授权执行 Phase A。**
- 若 Codex 决定在本轮落实下述 P3（会改变 r7/r3 字节并使其 pin 失效），则应视同新候选重新 pin + 重新 Review；否则本轮 APPROVED 只绑定当前读到的文本。

---

## 2. 需求 1：DSH-R6A-01..12 逐项 CLOSED/OPEN（只认 r7/r3 实际条文）

| Finding | 严重度 | 判定 | 实际落点（行号） |
|---|---|---|---|
| DSH-R6A-01 WER T0/T1 作用域与触发点 | P2 | **CLOSED** | r7 `:35`（同一测量进程、任何 Phase A 读取前 T0、全部读取后且进程退出前 T1、两次同覆盖 2 键 + 3 目录）；r7 `:44`（§1.2 复述“同一测量进程内的 WER T0/T1（两次均覆盖相同 5 个 WER 对象）”）；r3 `:22`（T0 = 任何 Phase A 读取开始前第一项；T1 = 全部读取完成后、进程退出前；5 个对象） |
| DSH-R6A-02 Phase A 环境集合关系未声明 | P2 | **CLOSED** | r3 `:20`（“该集合是 Phase A 完整集合”；“r7 §6 其余映射变量一律 `NOT_RUN / Phase B`”；“不构成 cache 重定向或写入闭包证据”）；r7 `:44`（“Phase A 完整集合 23 个 controller 环境变量”）；r7 `:7`（数量校正） |
| DSH-R6A-03 `TRITON_CACHE_DIR` 未单独成行 | P3 | **CLOSED** | r7 `:132` 独立行 `TRITON_CACHE_DIR → scratch python-cache/triton/`（r6 仅在 `:97` 泛称行内注解） |
| DSH-R6A-04 隐私路径类别与输出规则不清 | P3 | **CLOSED** | r3 `:20` 定义 `SCRATCH_EXPECTED` / `HOST_SYSTEM` / `USER_PRIVATE` / `UNDETERMINED`，并规定“只输出类别标签，不输出任何原始值或路径”、“此分类本身不构成 Gate failure”；r3 `:10` 不输出凭据材料/token handle |
| DSH-R6A-05 未列变量/路径处理规则缺失 | P3 | **CLOSED** | r3 `:32`（“未列出的变量、路径、对象或字段一律不读取并记 `NOT_RUN`；任何扩展项须通过 Phase B exact manifest、非作者 Review 与 Codex adjudication”） |
| DSH-R6A-06 悬空 `§4.5` | P3 | **CLOSED** | r7 `:34` 改为“§4 scratch 表与 §4 约束 5 列出的三条精确 leaf”；r6 `:34` 的 `§4.5` 已不存在；r7 §4 仍只有约束 1–5（`:106-110`），引用可解析 |
| DSH-R6A-07 ACL/label 写入路径缺状态锚点 | P3 | **CLOSED** | r7 `:8` 增补 `scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；与 adjudication `:49`、Task `:395` 同 token；r7 `:15` 的“均明确放行”现有可机读入口 |
| DSH-R6A-08 根元数据 vs 既有内容清单 | P3 | **CLOSED** | r7 `:44`（“根元数据不包含任何子项或内容 inventory；所有子项及内容信息均属 Phase B”）；r7 `:83`（“output-root 安全快照和既有内容/子项清单属于 Phase B”）；r3 `:12`（不得递归、枚举子项） |
| DSH-R6A-09 scratch 相对路径基准 | P3 | **CLOSED** | r7 `:83`（“下表全部相对路径均以固定 scratch clone `G:\CODEX\P02-scratch-build-source` 为根，主仓对应路径保持 deny”）；r3 `:14` 同基准 |
| DSH-R6A-10 manifest 未命名“四个 scratch 根” | P3 | **CLOSED** | r3 `:14`（“以下四项是 Phase A 唯一的四个 scratch 根”）；`:15-18` 逐条列名 |
| DSH-R6A-11 exclusion manifest 适用 Phase 未限定 | P3 | **CLOSED** | r7 `:36`（“仅在 Phase B 或后续 Gate 需要保护文件 digest 时…Phase A 不做任何受保护文件 digest，因此不适用该 manifest”）；r7 `:159` §8.4 呼应 |
| DSH-R6A-12 “普通文件”限定词留口 | P3 | **CLOSED** | r3 `:12` 统一为“不得递归、枚举子项、打开或哈希任何文件”（r2 `:12` 原为“普通文件”）；r3 `:32`/`:34` 一致 |

**重点项复核（未被 Phase A 解除，三文档无矛盾）**：`private_registry_absence=UNPROVABLE / BLOCKED`（r7 `:8`、`:28`、`:52`、`:177`）；`GetAppContainerRegistryLocation` 明确禁止（r7 `:54`、r3 `:32`）；`profile` 不得创建（r7 `:52`、`:53`、r3 `:32`）。

---

## 3. 需求 2：数量差异的实数核验（23 vs 24）

**结论：实数 = 23。r6 DSH 报告中的“24 项”是计数错误；r7 `:7` 与 Task `:392` 的校正正确，且未借机扩大读取范围。**

- **r2 manifest `:19` 逐项实列**（按顿号分隔，22 个分隔符 → 23 项，与 r3 完全同集、同序）：
  `LOCALAPPDATA、TEMP、TMP、APPDATA、USERPROFILE、HOME、PYTHONUSERBASE、PYTHONNOUSERSITE、PIP_CACHE_DIR、UV_CACHE_DIR、HF_HOME、HF_HUB_CACHE、TRANSFORMERS_CACHE、TORCH_HOME、TRITON_CACHE_DIR、CARGO_HOME、CARGO_TARGET_DIR、NPM_CONFIG_CACHE、NPM_CONFIG_USERCONFIG、GIT_CONFIG_GLOBAL、GIT_CONFIG_NOSYSTEM、GIT_TERMINAL_PROMPT、PYINSTALLER_CONFIG_DIR`
  → **23 项**。
- **r3 manifest `:20` 的集合**逐项与 r2 `:19` **完全一致**（无增、无删、无改名），并显式声明“该集合是 Phase A 完整集合” → 不存在“为凑 24 而扩展读取范围”的行为。
- **与 r7 §6 的对齐**：r7 §6（`:123-142`）左栏具名变量 33 个，另有 3 个仅出现在映射列（`PYTHONDONTWRITEBYTECODE` `:129`、`GIT_CONFIG_NOSYSTEM` / `GIT_TERMINAL_PROMPT` `:141`），共登记 **36 个具名变量**；Phase A 的 23 项**全部**能在 §6 找到映射 → 无“读取未登记变量”。其余 **13 项**（`HOMEDRIVE`、`HOMEPATH`、`PYTHONPYCACHEPREFIX`、`PYTHONDONTWRITEBYTECODE`、`TORCHINDUCTOR_CACHE_DIR`、`TORCH_EXTENSIONS_DIR`、`XDG_CACHE_HOME`、`XDG_DATA_HOME`、`HF_ASSETS_CACHE`、`HF_XET_CACHE`、`HF_TOKEN_PATH`、`HF_HUB_DISABLE_IMPLICIT_TOKEN`、`PATH`）由 r7 `:44` 与 r3 `:20` 判为 `NOT_RUN / Phase B`。
- **前轮报告的错误定位（供 Codex 记录）**：`dsh-appcontainer-contract-r6-review.stdout.md:49` 与 `:183`（推荐第 (2) 条）均写“24 个变量”；其列举的“不在 24 项内”的 6 个变量（`HF_ASSETS_CACHE`/`HF_XET_CACHE`/`PYTHONPYCACHEPREFIX`/`PYTHONDONTWRITEBYTECODE`/`HF_TOKEN_PATH`/`HF_HUB_DISABLE_IMPLICIT_TOKEN`）确实不在 r2 `:19`，但该列表本身**遗漏了其余 7 个同样不在集合内的 §6 变量**（`HOMEDRIVE`、`HOMEPATH`、`TORCHINDUCTOR_CACHE_DIR`、`TORCH_EXTENSIONS_DIR`、`XDG_CACHE_HOME`、`XDG_DATA_HOME`、`PATH`）。r7 `:44` 用“r7 §6 其余映射变量一律 NOT_RUN / Phase B”覆盖了全部 13 项，语义上比前轮建议更准确。
- 判断：r3 **准确保留原集合、明示“完整集合”、把其余留为 `NOT_RUN / Phase B`、未扩范围** → DSH-R6A-02 处置成立。

---

## 4. 需求 3–5 核验

### 4.1 WER T0/T1（需求 3）— 满足

- **同一测量进程**：r7 `:35`、r3 `:22` 均显式写“在同一测量进程内”。
- **T0 在任何 Phase A read 前**：r7 `:35`“任何 Phase A 读取前采集 T0”；r3 `:22`“T0 必须是任何 Phase A 读取开始前的第一项读取”。措辞在“T0 自身也是读取”上有轻微自指，但执行序无歧义（T0 排第一，先于 `:10` 的 controller 身份字段读取）。
- **T1 在全部 read 后、进程退出前**：r7 `:35`“所有 Phase A 读取完成后且进程退出前”；r3 `:22`“全部 Phase A 读取完成后、测量进程退出前立即采集”。与 r3 `:40`“测量进程运行期间不得写 evidence”无冲突（T1 是内存读取，不是写 evidence）。
- **同一 5 个对象（2 精确键 + 3 目录）**：r7 `:35`、r3 `:22` + `:24-28` 逐条列出 `HKLM…\LocalDumps`、`HKCU…\LocalDumps` + `%LOCALAPPDATA%\CrashDumps`、`%ProgramData%\...\ReportQueue`、`ReportArchive`；r7 `:44` 复述“相同 5 个 WER 对象”；Task `:394` 一致。
- 只读约束：不打开 / 不读取 / 不哈希 dump 内容；新直接子项 / 读取失败 / 无法解析实际 dump destination → `UNKNOWN / BLOCKED`（r7 `:35`、r3 `:22`）。

### 4.2 需求 4 清单逐项 — 全部满足

| 检查项 | 判定 | 证据 |
|---|---|---|
| environment 类别 / 隐私处理 | 满足 | r3 `:20`（四类枚举 + 只输出类别标签）；r3 `:10`（不输出凭据/token handle）；r3 `:34`（不读取/哈希用户文件、凭据、生产数据） |
| `TRITON_CACHE_DIR` | 满足 | r7 `:132` 独立具名行 |
| 未列变量/路径/字段 | 满足 | r3 `:32`（一律不读取 → `NOT_RUN`；扩展走 Phase B + 非作者 Review + Codex adjudication） |
| 悬空 §4.5 | 已消除 | r7 `:34` 指向“§4 scratch 表 + §4 约束 5”，两者均存在（`:99-102`、`:110`） |
| scratch ACL/label mutation = NOT_APPROVED | 满足 | r7 `:8` token；r7 `:15`/`:108`/`:110` 均要求 Review+预检+Gate 放行；adjudication `:49`、Task `:395` 同 token |
| Phase A 根元数据不含子项/内容 inventory | 满足 | r7 `:44`、r7 `:83`、r3 `:12`、r3 `:32`（仅三个 WER 目录例外枚举直接子项，且属显式登记范围） |
| scratch 相对路径基准 | 满足 | r7 `:83`（基准 = `G:\CODEX\P02-scratch-build-source`；主仓对应路径 deny）；r3 `:14` |
| 四个 scratch 根 | 满足 | r3 `:14` 命名 + `:15-18` 四条精确路径；与 r7 `:99-102` 表逐条对应（父目录 + 三条 leaf） |
| exclusion manifest Phase B-only | 满足 | r7 `:36`、`:159`；r3 `:32`、`:47`（Phase A 不产生受保护文件前后 hash） |
| 不得打开或哈希任何文件 | 满足 | r3 `:12`“打开或哈希任何文件”；r7 `:44`“不检查文件内容或 hash”；r3 `:34` 延伸至用户/模型/源码 |

三条 leaf 策略一致且互不重叠：`smoke-readonly-probe/`（只读 alias，写成功即 `BLOCKED`，不授 ACE/不改 label）、`lpac-write-control/`（正向 canary，Phase B Gate 后仅新增一个唯一文件并保留 SHA-256）、`lpac-write-deny-control/`（负向 DACL control，不授 ACE/不改 label；仅真实 LPAC token 下 `ERROR_ACCESS_DENIED` 算拒绝，MIC 拒绝 = `INCONCLUSIVE / BLOCKED`）——r7 `:34`、`:99-102`、`:108-110`、`:159`；r3 `:16-18`；Task `:95`。

### 4.3 需求 5：Phase A 候选性与状态保持

- **仍为候选、未冻结/未运行**：r3 `:4`（`CANDIDATE / NOT_RUN / NOT_AUTHORIZED_FOR_EXECUTION`）、r3 `:6`、r7 `:22`（“本 r7 是 r6 的待审候选”）、r7 `:156`（“唯一 Phase A 候选范围…（待审）”）、r7 `:175`、Task `:393`（“二者状态均为候选…不可据此执行 Phase A”）——**满足**。
- **阻断面完整**：profile/private-registry API（`CreateAppContainerProfile`、`DeleteAppContainerProfile`、`GetAppContainerRegistryLocation`、`GetAppContainerFolderPath`、派生/创建/复用）→ r3 `:32`、r7 `:52`/`:54`；ACL/registry/label mutation + 提权 + take ownership → r3 `:34`、r7 `:18`、`:106`；写 probe / MIC probe → r3 `:32`、r7 `:38`；工具链/build → r3 `:32`（“不执行写入、探针或工具链操作”）、r7 `:20`（明确点名 build/Cargo/Tauri/PyInstaller/Smoke/AC1–AC7）、`:156`；Windows Sandbox → r3 `:34`、r7 `:20`——**满足**。
- **状态 token 保持**（逐 token 对照见 §6）。

---

## 5. 新 finding（全部 P3，非阻断，不影响安全或范围）

> 说明：以下均为文档完备性/措辞问题，**不改变任何授权、路径、Gate 或安全边界**，不阻断 Phase A。任一项若在本轮落实，都会改变 r7/r3 字节并使已 pin 的 `AC45329A…BC43` / `7FBFFE65…0ADF` 失效 → 建议**默认推迟到 r4 候选**，除非 Codex 认为值得立即重 pin。

**P3-01（新）— 候选清单仍带“冻结日期”标签**
- 位置：`verification/P02/appcontainer-readonly-preflight-r3.md:3`（“冻结日期：2026-10-10”），而同文件 `:4` 为 `CANDIDATE / NOT_RUN / NOT_AUTHORIZED_FOR_EXECUTION`。
- 影响：与 r2 `:4` 的 `FROZEN_PLAN` 不同，r3 是候选；“冻结日期”可被机读/人读误当作“已冻结”。
- 最小修正：改为“候选日期：2026-10-10（尚未冻结）”。
- 阻断性：**非阻断**。安全/范围影响：**无**。

**P3-02（新）— manifest r3 未逐 token 复述完整 Gate 集合**
- 位置：`appcontainer-readonly-preflight-r3.md:47`（仅 `Build Gate 保持 BLOCKED`、`Hard Build Barrier 保持 EFFECTIVE`）；`:4` 仅 `NOT_RUN / NOT_AUTHORIZED_FOR_EXECUTION`。
- 事实：`private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`OS isolation preflight=NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN` 在 r3 中**没有**显式 token（仅有等价语义：`:32` 禁建 profile、`:47` “继续 UNKNOWN / BLOCKED / NOT_RUN”），不构成矛盾，但跨三文档逐 token 比对不会全等。
- 最小修正：在 r3 `:47` 补入契约 r7 `:8` / Task `:395` 的 10 个 token。
- 阻断性：**非阻断**。安全/范围影响：**无**（权威状态在 r7 `:8` 与 Task `:395`，r3 未作相反声明）。

**P3-03（新）— WER 对象 `%LOCALAPPDATA%\CrashDumps` 的指代未钉到 controller**
- 位置：`appcontainer-readonly-preflight-r3.md:22` 与 `:26`。
- 事实：r7 §6 `:125` 把 `LOCALAPPDATA` 映射为 `GetAppContainerFolderPath` 的 profile local-data directory；Phase A 又是 controller-only。r3 `:20` 只说明所列 23 个变量是 controller 当前值，未就 WER 路径声明 `%LOCALAPPDATA%` 即 controller 的 `LOCALAPPDATA`。
- 影响有界：Phase A 禁调任何 profile API（r3 `:32`）且不存在 profile，故唯一可解指代就是 controller 值，不会改变执行范围。
- 最小修正：r3 `:22`/`:26` 写明“`%LOCALAPPDATA%` 指当前 controller 的 `LOCALAPPDATA`”。
- 阻断性：**非阻断**（因不存在第二指代）。安全/范围影响：**无**。

**P3-04（新）— r7 §1.2 的 Phase A 枚举未覆盖 r3 实际采集的 OS/build 与 5 个 token 字段**
- 位置：`appcontainer-isolation-contract-r7.md:44`（“controller 身份/token 字段”）vs `appcontainer-readonly-preflight-r3.md:10`（实际记录 elevated、OS/build、controller 身份与 PID，以及 `TokenUser`、`TokenGroups`、`TokenPrivileges`、`TokenIntegrityLevel`、`TokenMandatoryPolicy`）。
- 影响：契约摘要比 manifest 实际范围略窄，但 r7 `:44` 已声明“严格限于待审 manifest r3 列明的 controller-only 读取”，故以 manifest 为准，不会扩大范围。
- 最小修正：r7 `:44` 补“OS/build 与 manifest 列明的 token 字段”。
- 阻断性：**非阻断**。安全/范围影响：**无**。

**P3-05（新）— r7 相对 r6 丢失 exclusion manifest 的文件名**
- 位置：`appcontainer-isolation-contract-r7.md:36`（只说“精确 exclusion manifest”），r6 `:36` 曾具名 `verification/P02/appcontainer-preflight-exclusions-r1.json`。
- 影响：该 manifest 仅 Phase B/后续 Gate 适用且必须另行冻结+Review+adjudicate，文件名非授权要素，故无实质缺口；仅追踪性略降。
- 最小修正：需要时在 r7 `:36` 恢复可登记的文件名，或明确“文件名由 Phase B manifest 冻结”。
- 阻断性：**非阻断**。安全/范围影响：**无**。

**非 finding 的编辑性观察（不计入 P0–P3 计数）**
- `appcontainer-isolation-contract-r7.md:24` 小节标题仍写“（r5/r6 继承）”，未点名 r7 自身（条款正文在 r7 中实际存在，不致误读）。
- `appcontainer-readonly-preflight-r3.md:32` 用“工具链操作”泛指，未点名 build/Cargo/Tauri/PyInstaller（r7 `:20` 已点名，`:47` 另保持 `Build Gate=BLOCKED`）。
- `appcontainer-isolation-contract-r7.md:97` 的 `python-cache/` 行说明不再提 Triton（已由 `:132` 独立行覆盖）。
- r7 `:5`“主仓基线 main@cddff584…”与 Task 后段记录的更晚 main 快照（如 `P02.md:364` 的 `54a39770…`）不同：这是**签署时的 pin**，非“当前 HEAD”声明；Phase A 只读 scratch clone（pin `7ce3c40…`/`ce8056b8…`，与 Task `:88`、`:116` 一致），故不影响范围。

---

## 6. 需求 6：Contract r7 / manifest r3 / Task 一致性核对

| 核对项 | Contract r7 | manifest r3 | Task `P02.md` | 判定 |
|---|---|---|---|---|
| 版本与状态 | r7 待审候选 `:22`、`:156` | `CANDIDATE / NOT_RUN / NOT_AUTHORIZED_FOR_EXECUTION` `:4` | r7+r3 均为候选、不可执行 `:393` | 一致 |
| 路径互 pin | pin manifest r3 路径+SHA `:156` | 指回 `appcontainer-isolation-contract-r7.md` `:6` | 同时给出 r7/r3 路径与 SHA `:392-393` | 一致（内部声称值互相吻合；未复算字节） |
| 环境集合数量 | 23 `:7`、`:44` | 23 且声明完整集合 `:20` | 23 `:392`、`:394` | 一致（实数核验见 §3） |
| 输入根 / scratch 根 / WER 对象数 | 12 / 4 / 5 `:44`、`:35` | 12 `:12`、4 `:14`、5 `:22` | 12 / 4 / 5 `:394` | 一致 |
| clone pin | HEAD `7ce3c40…`、tree `ce8056b8…`、无 remote/alternates `:81` | 基准路径 `:14` | 同 pin `:88`、`:116` | 一致 |
| 三条 leaf 与 alias 语义 | `:99-102`、`:108-110`、`:159` | `:16-18` | `:95` | 一致 |
| Gate token | 10 个 token `:8` | 部分（见 P3-02） | 10 个 token `:395` | 语义一致，r3 缺机读复述 |
| 授权定位 | “执行范围许可，不是 Review/测试/预检/Gate 凭证” `:12` | 同义 `:5` | 同义 `:70`、`:87`、`:390` | 一致，未被写成 Gate 凭证 |
| Owner/Reviewer/Integrator | Antigravity / DSH / Codex `:4` | — | `:7`/`:9`/`:11` | 一致 |
| 越界指令 | 未发现 Phase A 现在时越界；`CreateAppContainerProfile` 等被禁 `:52`/`:54` | 未发现；扩展须走 Phase B `:32` | 未发现；AC1–AC7 保持未完成 `:247`、`:395` | 未发现越界 |

**潜在歧义清单**：仅 §5 的 P3-01..05 与“编辑性观察”4 条；无 P0/P1/P2 级歧义，无授权越界。

**Phase A 实际读取面**（r3 全集）：controller 进程的 elevated/OS-build/身份/PID + 5 个 token 字段（`:10`）；12 输入根 + 4 scratch 根**仅根元数据**（`:12`、`:14-18`）；23 个环境变量（`:20`）；2 个 WER 注册表键 + 3 个 WER 目录（`:22`、`:24-28`）。与 r7 `:44` 的 Phase A 摘要相符（差异仅 P3-04 的枚举粒度），**未超出**契约 §3/§4/§6 的登记范围。

---

## 7. 当前 Gate 与本 Review 不构成的授权边界

**当前 Gate（本 Review 未改变任何一项）**：
`private_registry_absence=UNPROVABLE / BLOCKED`；`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；`scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`；`OS isolation preflight=NOT_RUN`；`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`；`Build Gate=BLOCKED`；`build=NOT_AUTHORIZED / NOT_RUN`；`Hard Build Barrier=EFFECTIVE`；`AC1–AC7=BLOCKED / NOT_RUN`。（r7 `:8`、adjudication `:49`、Task `:395` 三处一致。）

**本 Review 明确不构成**：
1. Phase A 执行授权——仍须 Codex 逐项 adjudicate + 逐文件 SHA/object pin（r7 `:156`、`:175-177`；r3 `:6`）；因 `object_binding=NOT_VERIFIED`，本轮不是 exact-object 通过凭证。
2. profile 创建/复用或任何 profile/private-registry API 调用许可；不解除 `P1-01`、`P1-02`、`private_registry_absence=UNPROVABLE / BLOCKED`。
3. ACL/DACL/owner/label/policy/registry 修改、提权、take ownership、写 probe/MIC probe、工具链/build（Cargo/Tauri/PyInstaller/Smoke）、AC1–AC7、Windows Sandbox 的任何批准；不解除 `Build Gate=BLOCKED` / `Hard Build Barrier=EFFECTIVE`。
4. 三个 control（`smoke-readonly-probe/`、`lpac-write-control/`、`lpac-write-deny-control/`）本轮均 `NOT_RUN`；未产生任何隔离、拒写、cache 重定向或写入闭包证据。
5. 未做任何 OS 状态、路径存在性、DACL/label、Git/worktree/clone pin、输出文件或文件内容/hash 的独立核验；对 r7 §9 的 Microsoft 一手页面未联网核对，只做文档内部一致性审查。
6. 未回溯 r3/r4/r5 契约与其 DSH 报告原文；R6A 判定基于本轮实读的 r7、r3、r6 report、r6 adjudication、r2 manifest、r6 contract 与 Task 文本。

---

## 8. 推荐下一步（单一可转发指令）

> 请 **Codex（Integrator / Gate owner）** 对 contract r7、Phase A manifest r3 与本 Review 作**纯文档 adjudicate**，不得调用任何 profile/private-registry API、不得创建 profile、不得修改 ACL/label/registry、不得运行 probe/measurement/Sandbox/build，并保持 `private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`、`OS isolation preflight=NOT_RUN`、`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`：
> (1) 记录 DSH-R6A-01..12 **全部 CLOSED**、内容 `APPROVED`、P0/P1/P2/P3=`0/0/0/5`；说明“24 项”为前轮 DSH 计数错误、实数 23 且 r2 `:19` 与 r3 `:20` 同集同序、未扩读取范围；
> (2) 对 P3-01..05 逐项给出接受/驳回/延期的显式处置（默认建议**延期至 r4**，以免在 Phase A 前改动 r3 字节并作废已 pin 的 `AC45329A…BC43`）；接受任一项即须重固定 SHA 并另派只读复审；
> (3) 复核 Task、contract r7、manifest r3 的精确字节 SHA/object pin，并把最终 SHA 写入 checkpoint；
> (4) 仅在 (1)–(3) 完成且无歧义后，才可严格按 r3 执行 Phase A 的 controller-only 读取，且不得调用 profile/private-registry API、不得写文件、不得改 ACL/registry/label；
> (5) Phase A 完成亦不解除 private-registry blocker、P1-01、P1-02、Build Gate 或 Hard Build Barrier；Phase B 每项读取仍需独立 exact manifest + 非作者 Review + Codex adjudication。

**给用户**：当前无需新授权，也没有需要用户裁决的新出口。唯一潜在裁决情形未变（r7 `:177`）：若将来只读或 Phase B 证据证实非提权 controller 无法读取系统对象 DACL，或系统未预置适用的 `S-1-15-2-2` ACE，则本机非提权 Codex-only 路线不可实施，需在“停止本机 AppContainer 路线 / 另行授权替代方案 / 接受 Build Gate 持续 `BLOCKED`”之间选择。

*报告结束。本报告为只读内容审查产物；本会话未运行 shell/PowerShell/Git/hash/Windows API，未做 measurement、profile 调用、ACL/registry 修改、probe、build 或 Sandbox，未创建/修改/删除任何文件，`object_binding=NOT_VERIFIED`。*
