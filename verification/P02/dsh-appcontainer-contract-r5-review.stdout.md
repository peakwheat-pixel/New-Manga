# P02 AppContainer 隔离契约 r5 · 非作者只读内容 Review（DSH）

- Reviewer：DeepSeek Harness（非作者；Task/契约 Owner=Codex、产品 Owner=Antigravity，角色互异）
- 日期：2026-10-10（Asia/Shanghai）
- 本会话性质：**纯文档内容 Review**。未调用 shell / PowerShell / Git / 终端 / Windows API，未做任何 OS measurement，未创建或复用 profile，未访问 private registry，未改 ACL/label/registry，未运行 probe/build/Sandbox，未修改、创建或删除任何文件（不写报告文件）。

---

## 1. Reviewed 内容

| 对象 | 实际读取 | 形态 |
|---|---|---|
| `doc/tasks/P02.md` | 全文 | 377 行 |
| `verification/P02/appcontainer-isolation-contract-r5.md` | 全文 | 168 行 |
| `verification/P02/appcontainer-readonly-preflight-r1.md` | 全文 | 69 行 |
| `verification/P02/dsh-appcontainer-contract-r4-review.stdout.md` | 全文 | 253 行 |
| `verification/P02/codex-appcontainer-contract-r4-adjudication.md` | 全文 | 34 行 |
| （辅助，非本 Review 对象集）`verification/P02/dsh-appcontainer-contract-r5-review.prompt.md` | 全文 | 31 行（仅用于核对 pin 声明） |

路径存在性用只读 glob 旁证：`appcontainer-isolation-contract-r2/r3/r4/r5.md`、`dsh-appcontainer-contract-r2-review.stdout.md`、`codex-appcontainer-contract-r3/r4-adjudication.md`、`dsh-appcontainer-contract-r4-review.stdout.md`、`appcontainer-readonly-preflight-r1.md` 均存在；`appcontainer-preflight-exclusions-r1.json` 尚不存在（与契约 §1.1.9“digest 前才建立”一致）。

**正面确认（无 finding）**

1. manifest 的只读约束逐项成立：`appcontainer-readonly-preflight-r1.md:12`（仅根目录级元数据、不递归、不打开/不哈希普通文件）、`:43`（WER 不打开/读取/复制/哈希内容）、`:51`（禁 profile/private-registry API、禁 profile 创建/复用、不猜 key）、`:52`（禁创建/删除/移动/写入/探测/ACL/label/owner/提权/网络）、`:53`（禁读/哈希漫画、用户文件、DB、Lock、current/pinned、凭据、模型/源码内容）、`:54-55`（禁子进程/产品/Cargo/Tauri/PyInstaller/Smoke/GUI/Sandbox），与契约 `r5:18/20/28/48/105/107` 方向一致。
2. 路径可追溯且未发现过宽路径：manifest `:16-27` 的 12 根与契约 `r5:58-69` 逐字一致；manifest `:31-34` 的四条精确目录（`verification/P02/tmp/` 及三条 leaf）与契约 `r5:34/93/99/101` 一致；manifest `:63-65` 的落盘证据路径位于 Task Owner allowlist（`P02.md:51`）内，且明确不属于 scratch/LPAC 写入许可，属“测量结束后 Codex 证据落盘”，不违反测量期只读。
3. 顺序与状态如实：`r5:146`（§8.1）绑定“DSH r5 Review 完成且 Codex adjudicate 后”才可 measurement，无 r3/r4 残留 Gate 主体；`r5:8`、`r5:76`（Task）、manifest `:4/6/69` 均保持 `private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`OS preflight=NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`；`r5:28/146` 与 manifest `:69` 明确“只读测量不解除 private-registry blocker / Build Barrier”。
4. 授权未被写成 Gate/Test 证据：`r5:12`、manifest `:4/5`；`r5:6` 的 Codex 复算被限定为“只关闭 Codex 自己的字节核对，不改写 DSH `NOT_VERIFIED`”。

---

## 2. object_binding

**`object_binding = NOT_VERIFIED`**

本会话无可靠 shell/hash 能力，且按派发边界不得调用 PowerShell/Git/Windows API：未复算 Task `8CB345…10F7`、契约 `298C17…E9BA`、manifest `55E4AB…9BD2`、r4 报告 `B7A353…6FA1` 的任何 SHA-256 或字节数，未读 `.git`，未核验 `main@cddff584…` / tree `c25d051a…`。本报告全部结论只绑定“本会话用 read 工具实际读到的上述路径内容形态（行数与逐行文本）”，不绑定任何 SHA/Git blob/tree。**本 Review 不是 exact-object Review**，不得因 Codex 或派发 prompt 提供的 SHA 声明而改称已独立绑定对象。

---

## 3. Decision

- **内容层 Decision = `CHANGES_REQUESTED`**（P0/P1/P2/P3 = `0/1/2/6`，open=9）。
- **整体正式 Decision = `NOT_VERIFIED`**：因 `object_binding=NOT_VERIFIED`，与 r2/r4 先例一致（“不可核验”≠“mismatch”），本报告不能作为 exact-object 通过凭证。
- 判定口径：R4-01..09 中 8 项闭合、1 项部分闭合；但 manifest 与契约对**首轮（本轮唯一排定的）只读预检范围**存在实质不一致（R5C-01），因此 r5 尚不能作为“后续有限 controller-only 只读预检的无歧义执行契约”。

---

## 4. P0 / P1 / P2 / P3 计数与 open findings

| 严重度 | 数量 | 编号 |
|---|---|---|
| P0 | 0 | — |
| P1 | 1 | R5C-01 |
| P2 | 2 | R5C-02、R5C-03 |
| P3 | 6 | R5C-04 … R5C-09 |
| 合计 | 9 | 全部 open |

> 编号前缀用 `R5C-`（r5 Contract）以避免与 Task 历史中已有的 Stage A `R5-01..R5-06`、`R5F-01..03` 冲突。

#### R5C-01（P1）— 契约与冻结 manifest 对首轮只读预检范围不一致，`§精确下一步 4` 的 P1-02 出口在该清单下不可达
- **引证**：契约 `r5:71`（§3“只读预检**须**核对实际需要的系统文件 DACL 中是否存在适用的 `S-1-15-2-2` ACE，并记录精确路径与访问 mask”）、`r5:29`（§1.1.2 loader/runtime DACL 只读查询与 `SYSTEM_ACL_UNREADABLE / MISSING`）、`r5:46`（§2“moniker/profile 与 local-data directory 的只读状态**可在** §8.1 授权的测量范围内核验”）、`r5:97`（§4.1“只读预检先记录 exact output-root path、file ID、owner/group、DACL、label/policy、reparse status、**既有内容清单**…”）、`r5:147`（§8.2“每次运行前重采 `git status --porcelain=v1 --untracked-files=all -z`…固定 clone HEAD/tree/clean/remotes/alternates/hardlinks”）；对照 manifest `:12`（**仅**对 12 个输入根与精确 scratch 根读取根目录级元数据、不递归）、`:29-34`（仅 4 条 scratch 目录）、`:52`（禁任何创建/写入/探测）、`:59`（禁用会生成文件/缓存/**索引**的命令）。
- **冲突内容**：(a) 系统 loader/runtime DACL 与 `S-1-15-2-2` ACE 核对不在 manifest 读取集内，而契约 `r5:71` 用“须”表述、`r5:29` 将其列为只读预检产物；(b) moniker/profile 与 local-data directory 的只读存在性不在 manifest 读取集内，而契约 `r5:46` 称其可在该测量范围内核验；(c) 契约 `r5:97` 的 output-root 安全快照（含“既有内容清单”）不在 manifest 内，且“既有内容清单”与 manifest `:12`“不得递归列举内容”字面冲突；(d) 契约 `r5:147` 的运行前 Git pin 重采在 manifest `:59`（禁生成索引的命令）与 `:52` 下大概率不可执行。
- **影响**：manifest 是契约 `r5:165/166/167` 认可的“本轮 controller-only 只读测量清单”，若执行者以 manifest 为操作面，则 P1-02 永远得不到测量，`r5:168`（“若只读测量证实 P1-01 或 P1-02 无法解除…提交用户裁决”）的出口无法被真实触发，正是 R4-09 想消除的“静默长期 BLOCKED”；同时 `r5:167` 自设的“只读清单与 review disposition 均无歧义”前提不成立。
- **最小修正（二选一，须显式）**：(1) 在 manifest 增列精确只读对象（系统 loader/runtime 精确文件路径、`%LOCALAPPDATA%\Packages\<moniker>` 与 local-data 目录、契约 `r5:79-93` 各 output root、clone pin 只读采集方式），并说明“既有内容清单”是仅列名还是含长度/digest；(2) 或修改 `r5:71/46/97/147`，明确这些核对**不属于**本轮有限只读范围、另需单独授权，并同步 `r5:168` 的出口条件。任一修正都会改变冻结字节，须重新 pin（见 R5C-03）。

#### R5C-02（P2）— r5 中 `Task:79` / `Task:81` 行号引用在冻结 Task 上已失效
- **引证**：契约 `r5:22`（“P02 Task:79 的 Smoke 只读 alias 语义继续有效”）、`r5:101`（“`verification/P02/tmp/smoke-readonly-probe/` 是 Task:79 只读 alias”）、`r5:149`（“Task:79 只读 alias”）、`r5:77`（“仅可按 Task:81 记录原始工作区字节 hash 和 Git blob”）。
- **实际文本**：本会话所读 `doc/tasks/P02.md` 中，Smoke 只读 alias 段落位于 **`:86`**（“Smoke 的只读 canary alias 仅映射…`verification/P02/tmp/smoke-readonly-probe/`…写成功…记为 BLOCKED”），`gen/schemas`/`permissions/autogenerated` 已跟踪文件 hash 规则位于 **`:88`**；而 `:79` 是 clone 四条命令段、`:81` 是构建输出清单首行。引用错位量 = 7 行，来源是 Task 新增的 `### 2026-10-10 continuation` 段（`P02.md:72-77`）插在 `:68-70` 授权段与其下属输出段（`:79-90`）之间。
- **旁证（不构成字节结论）**：派发声明 Task SHA-256=`8CB345…10F7`，与 `codex-appcontainer-contract-r4-adjudication.md:6` 记录的 `C7959EF9…138C` 不同，与“Task 已被编辑、r5 的 Task 行号随之漂移”一致。
- **影响**：契约的“精确路径/Task 追溯”要求（Review 范围 2、3）在冻结对象对上不成立；按引用检索会落到 clone 命令段与构建输出段。语义本身在契约 `r5:101` 与 manifest `:32` 有重复定义，故不产生执行歧义，但破坏引用完整性。

#### R5C-03（P2）— 契约与 Task 均未以精确路径标识本轮只读测量清单，契约内亦无其 SHA-256
- **引证**：契约 `r5:146`（“将本条列出的只读范围固定在**独立 evidence 文件**并计算 SHA-256”）、`r5:165`（“本轮 controller-only 只读测量清单”）、`r5:166`（“本只读测量清单”）；`P02.md:75`（仅给 manifest SHA-256=`55E4AB…9BD2`，未给路径）。契约全文未出现 `appcontainer-readonly-preflight-r1.md`，也未出现 `55E4AB…`。唯一同时给出路径+SHA 的是派发 prompt `:9`。
- **影响**：仅持契约+Task 的执行者无法唯一解析“本轮清单”是哪个文件；`r5:167` 的“只读清单…无歧义”在契约内部不可自证。清单本身只单向指回契约（manifest `:6`），关系未闭合。

#### R5C-04（P3）— R4-07 部分闭合：§4 表行指向“下方三条 leaf”，但表内无该三行
- **引证**：契约 `r5:93`（表行 `verification/P02/tmp/`：“LPAC may access only the three exact leaves **below**, each with its own read/write policy”）；对照 `r5:34`、`r5:99`、`r5:101`（三条 leaf 在表外精确列出）与 `codex-appcontainer-contract-r4-adjudication.md:22`（要求“与三条 leaf 逐项对应”）。
- **影响**：R4-07 的“补表行”已落实，“逐项对应”未落实；仅凭 §4 表无法枚举可写 leaf，表内出现悬空指代。三条 leaf 的精确路径在契约别处有定义，故为文档精度问题。

#### R5C-05（P3）— 当前状态行未使用规范状态 token，且 `OS preflight` 命名与 Task 不一致
- **引证**：契约 `r5:8`（“因 profile private-registry 创建前不存在性当前不可由公开依据验证，profile 创建=`BLOCKED`；…OS preflight=`NOT_RUN`…”）；对照 `r5:28/46/149/167` 使用 `private_registry_absence=UNPROVABLE / BLOCKED`，`P02.md:76` 使用 `private_registry_absence=UNPROVABLE / BLOCKED` 与 `OS isolation preflight=NOT_RUN`。
- **影响**：状态 token 不统一，逐项机读比对（如 r8/r9 系列 status assertion）可能漏项；语义可由散文推得，故非阻断。

#### R5C-06（P3）— manifest 的两处可追溯性细节
- manifest `:36` 读取 controller 环境 `TRITON_CACHE_DIR`，契约 §6 环境表（`r5:114-132`）未登记该变量（仅 `r5:91` 泛称 “Python/Torch/HF/Triton cache variables”）。
- manifest `:38-47` 规定 WER 键/目录的只读采集，但未写明契约 `r5:35`（§1.1.8）要求的“**只读 preflight 前后**记录”；按现文执行者可能只采一次，无法支持“新文件即 `BLOCKED`”判定。

#### R5C-07（P3）— Task 仍保留现在时的 r4 待审状态，未标为已被取代
- **引证**：`P02.md:115-117`（“### 2026-10-10 r4 AppContainer contract follow-up…**r4 当前仍是文档候选**，不是 Gate 凭证…**等待** DeepSeek Harness 对固定 r4/Task 对象作非作者只读 Review”）与 `P02.md:72-77`（r5 continuation）并存；`r5:22` 声明 r2/r3/r4 只作历史证据。
- **影响**：Review 范围 2 关注的“是否遗留 r4 状态”在 Task 侧仍有一处现在时表述；契约侧（r5:7“r5 是修订候选，尚待非作者 Review”、r5:22“本 r5 取代 r4”）无残留。

#### R5C-08（P3）— 术语残留 `profile root` / `profile 树`
- **引证**：契约 `r5:50`（“profile root/Temp 的 DACL…本轮新建 profile 树内”）、`r5:116`（`LOCALAPPDATA` = “profile root”）、`r5:117`（“profile root 下 `Temp`”）；对照 `r5:37`（§1.1.11 声明“`profile directory`、`local-data directory`、`private registry storage` 用词一致”）与 `r5:150`（§8.5 已改三固定词）。
- **影响**：R4-05 主体已闭合，但“profile root”是否等同 `local-data directory` 未定义，§1.1.11 的“一致性”声明仍有缺口（同类残余）。

#### R5C-09（P3）— `r5:5` 的授权措辞与 §8.1 前置条件存在字面张力
- **引证**：契约 `r5:5`（“本契约只授权 Codex-only 隔离预检，不扩大产品 AC、Owner allowlist 或输出 allowlist”）；对照 `r5:12`（该授权“不是 Review、测试、预检或 Gate 凭证”）与 `r5:146`（“Review 与 adjudication 完成前，禁止任何 OS measurement”）。
- **影响**：范围限定句采用现在时“授权”，可被读成“预检当前已获准”。建议改为“本契约的授权范围限于 Codex-only 隔离预检（执行前置见 §8.1）”。

---

## 5. R4-01..09 处置核对（口径：只认 r5 实际条文落地，不采信 adjudication 自述）

| Finding | 要求 | r5 实际落点 | 判定 |
|---|---|---|---|
| R4-01 (P2) | §2 明示 `UNPROVABLE / BLOCKED`、删除强制调用 `GetAppContainerRegistryLocation` | `r5:28`（结论=`UNPROVABLE / BLOCKED`，禁猜 key/递归枚举/可能初始化 storage 的 API、禁 `CreateAppContainerProfile`，且“不被任何其他只读测量覆盖”）、`r5:46`（“不得猜测 key/view、调用 `GetAppContainerRegistryLocation`…禁止调用 `CreateAppContainerProfile`”）、`r5:48`（“**本 Task 禁止调用 `GetAppContainerRegistryLocation`**”）、`r5:146`（该有限读取不调用该 API） | **CLOSED**（`:159` 仅作为文档来源列出，非执行指令） |
| R4-02 (P2) | §8.4 以冻结 manifest 为唯一排除源、profile/private registry 不得列为可忽略项、三条 canary/control 精确 leaf | `r5:149`（“唯一排除集合必须是 §1.1.9 冻结的 exact-path exclusion manifest”；“在创建前不存在性未被证实前不得列为允许新增或排除项”；三条 leaf 精确列出；“不能笼统排除‘两处 canary’”） | **CLOSED** |
| R4-03 (P2) | 负向 DACL control 精确 leaf 入表并声明不授 ACE/不改 label | `r5:32`、`r5:34`、`r5:99`、`r5:101`、`r5:149` 均为 `verification/P02/tmp/lpac-write-deny-control/`，并明确父链与自身不授 Package SID ACE、不改 label/policy | **CLOSED** |
| R4-04 (P3) | §8.1 Gate 主体改为本轮 Review | `r5:146`（“只有 DSH **r5** Review 完成且 Codex adjudicate 其 findings 后…”）；无 “r3” 残留 | **CLOSED** |
| R4-05 (P3) | §8.5 三固定术语 | `r5:150`（`profile directory`、`local-data directory`、`private registry storage`） | **CLOSED**（另有 R5C-08 的别处残留） |
| R4-06 (P3) | 区分写/MIC 探针与获准只读测量、解除 MIC 对 profile 的错误前置 | `r5:38`（“不运行**写探针或 MIC 探针**；符合 §8.1 的只读测量不受此禁令限制。MIC negative control 使用独立 Low token 时不依赖 profile 创建，但仍需后续精确测量授权；不能替代真实 LPAC 身份或写入闭包证据”） | **CLOSED** |
| R4-07 (P3) | §4 表加 `verification/P02/tmp/` 并与三条 leaf 逐项对应 | `r5:93` 表行已加；但仅写 “the three exact leaves **below**”，表内无 leaf 行 | **部分闭合 → R5C-04** |
| R4-08 (P3) | §5 明确禁令主体为 LPAC、controller 证据写入限 allowlist | `r5:105`（“本节禁止读取/写入的主体为 LPAC 主进程及其全部子进程/组件…；Codex/controller 的证据读取范围与写入例外单独受 P02 Task allowlist 管理：仅允许在该 allowlist 的 `verification/P02/**` 下写入…不可借此放宽 LPAC 路径或写入本节 deny 集”） | **CLOSED** |
| R4-09 (P3) | 追加 P1-01/P1-02 不可解除时的用户裁决出口 | `r5:168`（三个可选裁决 + “不得自行提权、修改受保护 ACL 或放行 Gate”） | **CLOSED**（可触达性受 R5C-01 影响） |

**重点项复核**：private registry 不存在性 `UNPROVABLE / BLOCKED`（`r5:28/46/149/167`）；`GetAppContainerRegistryLocation` 禁止（`r5:48/146`，manifest `:51`）；profile 继续不得创建（`r5:28/46`，`r5:167`“该测量结果禁止创建 profile”，manifest `:51`）——三项在 r5 与 manifest 内**无相互矛盾**，且未被任何只读测量授权解除。

---

## 6. 契约与 manifest 中发现的精确路径/行号汇总

- 契约 `r5:5`、`:8`、`:12`、`:22`、`:28`、`:29`、`:37`、`:38`、`:46`、`:48`、`:50`、`:71`、`:77`、`:93`、`:97`、`:99`、`:101`、`:105`、`:116`、`:117`、`:146`、`:147`、`:149`、`:150`、`:159`、`:165`、`:166`、`:167`、`:168`。
- Task `P02.md:51`（allowlist `verification/P02/**`）、`:72-77`（r5 continuation）、`:75`（manifest 仅 SHA 无路径）、`:76`（Gate 状态）、`:79/81`（引用落空目标）、`:86`（Smoke alias 实际行）、`:88`（tracked hash 规则实际行）、`:115-117`（残留 r4 现在时）。
- manifest `:4`、`:5`、`:6`、`:12`、`:16-27`、`:29-34`、`:36`、`:38-41`、`:43-47`、`:51-55`、`:59`、`:61-67`、`:69`。

---

## 7. Gate 状态（本 Review 不改变任何 Gate）

`private_registry_absence=UNPROVABLE / BLOCKED`；`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；`OS preflight / OS isolation preflight=NOT_RUN`；`hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`；`Build Gate=BLOCKED`；`build=NOT_AUTHORIZED / NOT_RUN`；`Hard Build Barrier=EFFECTIVE`；`AC1–AC7=BLOCKED / NOT_RUN`。

- 未把用户授权写成 Gate/Test/预检证据（`r5:12`、manifest `:4/5` 均已正确限定）。
- 未把任何只读测量结果写成可解除 private-registry blocker 或 Build Barrier 的依据（`r5:28/146`、manifest `:69`）。
- 本 Review 无 P0，且不请求 Build Gate 放行。

---

## 8. 是否允许进入有限 controller-only 只读预检

**否——当前不允许。**

1. P1（R5C-01）未闭合：契约 `r5:167` 自设前提“只读清单与 review disposition 均无歧义”不成立，manifest 与契约对首轮读取范围不一致，且 `r5:168` 的 P1-02 出口在该清单下不可达。
2. 即便 R5C-01 按“延后核对”路径修正，仍必须先满足契约 `r5:146` 的两道前置：本 Review（内容层为 `CHANGES_REQUESTED`）→ **Codex 逐项 adjudicate**；且在修正 R5C-01/R5C-02/R5C-03 后，契约与 manifest 字节都会变化，其 SHA 与冻结关系须重新固定并重新确认（新的 manifest 候选至少需 Codex 对象核对，或按项目惯例另派只读复审）。
3. 在任何情形下，只读预检都不得创建 profile、不得调用 `GetAppContainerRegistryLocation`、不得修改 ACL/label/registry、不得解除 `private_registry_absence=UNPROVABLE / BLOCKED` 或 Hard Build Barrier。

---

## 9. 不能被此 Review 证明的内容

1. **对象绑定**：未复算任何 SHA-256/字节数，未核验 branch/HEAD/tree/Git blob；`object_binding=NOT_VERIFIED`。Codex 在 `r5:6`、`codex-appcontainer-contract-r4-adjudication.md:5-10` 声明的历史哈希、session、exit 均为“未复核的历史声明”。
2. **无任何 OS 状态主张**：未测量本机 ACL/mandatory label/owner/file ID/reparse、token、环境、registry、WER、clone pins、profile 是否存在；未确认 manifest `:16-27` 的 12 个路径在本机存在或其形态（仅确认文档中的字面路径）。
3. **一手文档未复核**：未联网抓取 `r5:155-161`、`r5:40` 引用的 Microsoft 页面，对 `S-1-15-2-2`、`GetAppContainerRegistryLocation` absent-state 等语义只做文档内部一致性审查，不独立确认外部事实。
4. **跨轮一致性范围有限**：未读 r2/r3 契约与 r2/r3 DSH 报告、r2/r3 adjudication、`codex-scratch-build-process-isolation-scope-delta-r1.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`；对 R4-01..09 的处置判定基于 r4 report 与 r4 adjudication 所载内容，未独立回溯 r3 finding 原文。
5. **无 Gate 效力**：不构成 profile 创建、ACL/label/registry 修改、OS preflight、Smoke、build、AC1–AC7 的任何批准，不解除 Hard Build Barrier，不改写任何历史 finding 计数与 Gate 状态。
6. **未核实派发链路**：`dsh-appcontainer-contract-r5-review.prompt.md` 的 pin 值与真实文件字节的一致性由 Codex 负责，本 Review 未验证。

---

## 10. 推荐下一步（单一可转发指令）

> 请 Codex（Integrator/Gate owner）对 `verification/P02/appcontainer-isolation-contract-r5.md` 与本 Review 作**纯文档 adjudicate + 修订**（不创建 profile、不改 ACL/label/registry、不运行 probe/Sandbox/build/OS measurement），保持 `private_registry_absence=UNPROVABLE / BLOCKED`、`profile=NOT_CREATED`、`ACL/registry=NOT_MODIFIED`、`OS preflight=NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`、`AC1–AC7=BLOCKED / NOT_RUN`：
> (1) **R5C-01（P1，必先消歧）**：在 `appcontainer-readonly-preflight-r1.md` 与 r5 `§3:71 / §2:46 / §4.1:97 / §8.2:147` 之间二选一保持一致——或把系统 loader/runtime DACL 与 `S-1-15-2-2` ACE 核对、moniker/profile 与 local-data directory 只读存在性、各 output-root 安全快照（并澄清“既有内容清单”的粒度）、clone pin 只读采集方式显式纳入清单读取集；或明确这些项目不属于本轮有限只读范围、另需单独授权，并同步 `§精确下一步 4:168` 的 P1-02 出口条件。
> (2) **R5C-02（P2）**：把 r5 `:22/:77/:101/:149` 的 `Task:79`/`Task:81` 改为经核对的当前行号（本会话读取的 Task 文本中对应 `:86`/`:88`），或改用“Task §Smoke 只读 alias 段 / §scratch 生成差异段”这类稳定锚点，避免再次因 Task 结构性插入而漂移。
> (3) **R5C-03（P2）**：在 r5 `:146/:165/:166` 与 `P02.md:75` 写入本轮清单的精确路径 `verification/P02/appcontainer-readonly-preflight-r1.md` 及其 SHA-256；若清单被修订，同步更新 Task 记录并重新冻结 pin。
> (4) **R5C-04..09（P3）**：逐项给 closed 或显式 disposition（§4 表补三条 leaf 行；`:8` 使用 `private_registry_absence=UNPROVABLE / BLOCKED` 与统一 `OS isolation preflight` 命名；manifest 补 Triton 变量口径与 WER 前后两次采集；`P02.md:115-117` 标为已被 r5 continuation 取代的历史段；`profile root`/`profile 树` 映射到三固定术语或纳入 §1.1.11；`r5:5` 授权句加“执行前置见 §8.1”限定）。
> (5) 修订后重新固定 Task/契约/清单 SHA-256，并在**本 Review 的 P1 闭合 + Codex 逐项 adjudicate + 新 pin 生效**之前，不得运行任何 OS measurement、不得进入 controller-only 只读预检；此后亦不得据只读读数解除 private-registry blocker 或 Hard Build Barrier。

**给用户**：当前无需新授权。唯一可能需要裁决的情形仍未变（r4 R4-09 / r5 `:168`）：若将来只读测量证实非提权 controller 无法读取系统对象 DACL 或系统未预置适用的 `S-1-15-2-2` ACE，本机非提权 Codex-only 路线不可实施，需在“停止本机 AppContainer 路线 / 另行授权替代方案 / 接受 Build Gate 持续 `BLOCKED`”三者中选择。

*报告结束。本报告为只读审查产物，DSH 未创建或修改任何文件。*
