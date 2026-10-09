# P02 非提权宿主 Preflight r1 exact-head Review（非作者独立审查）

## 0. 审查对象与身份

| 项 | 值 | 我的核验方式 |
|---|---|---|
| candidate | `561f4105171b99910d739698380787f35203d3f2` | `git rev-parse HEAD` |
| candidate tree | `256066495920ee1a34163a868348e0bd07db0882` | `git rev-parse HEAD^{tree}` |
| parent（=base） | `6855c113e6a44320d9555777900cfb78a218d383` | `git rev-parse HEAD^` |
| 单 commit 性 | `base..candidate` = **1** | `git rev-list --count` |
| author 分支指针 | `codex/P02-process-isolation` = candidate | `git rev-parse codex/P02-process-isolation` |
| root 现场 | `G:/CODEX/New Manga`，`main`=`6855c113…`（未集成，符合 FF 前预期） | 只读 `git -C … status/rev-parse`（`GIT_OPTIONAL_LOCKS=0`） |
| Reviewer worktree | `C:/Users/49745/.codex/worktrees/P02-preflight-review-dsh-r1`，detached at candidate | 见下 |
| Reviewer cleanliness | `git status --porcelain=v1 -uall` = **0 项**（审查开始与结束各一次） | 同上 |

被审角色：Owner/author=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex；本 Reviewer 全程只读，未写任何文件、未改本 checkout/Git-index/root/其他 worktree。

## 1. Decision

**`APPROVED_WITH_CONDITIONS`**（P0/P1/P2/P3 = **0 / 0 / 1 / 5**）

候选的技术内容、事实陈述与 Gate 状态**未发现虚假 PASS 或越界**；唯一 P2 是**授权依据的可审计性**（第 2 节 P2-01），须在 fast-forward 集成前闭合。P3 为措辞/证据完整性建议，可与 P2 一并处理或按既有惯例登记延期。

## 2. Findings

### P2-01（条件，集成前须闭合）本轮 `doc/**` 修改的授权基础不可审计

- 事实：候选修改了 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md` 4 个共享文档。
- 该授权的**唯一**库内依据是候选自身新增的 `verification/P02/codex-checkpoint-p02-preflight-scope-frozen.md:6`（自声明允许修改"`doc/REBASELINE_PLAN.md`/`doc/STATUS.md`/`doc/00_INDEX.md` 各自顶部当前状态段"）。
- 我独立检索 base 树（`6855c113`）确认：**不存在**任何先于本候选的授权文件提到本 preflight 证据路径或 3 个状态文档（`git grep` `preflight-(inputs|hostfolders)-r1`、`wsb-version-r1`、`PREFLIGHT_EVIDENCE` → 无匹配）。
- 且最新冻结范围**明文禁止**：`codex-scratch-build-process-isolation-scope-delta-r1.md:69` 与 `:77` 均写"不得改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`"；本候选之前同一子任务的三个 commit（`1c7efb17`→`30da5faf`→`2394dc98`→`6855c113`）只触及 `verification/P02/**`，无 `doc/**`。
- 对照：`scope-delta` 历次 extension 均显式声明"在用户持续有效的 `PROJECT_ORCHESTRATION_AUTHORIZATION` 下签发"；本轮 scope-frozen checkpoint 未引用该授权，也未在 `scope-delta` 中登记 extension。
- 影响判定：内容本身真实（仅顶部当前状态段，无 AC/范围/allowlist/产品改动）、无产品或用户数据风险，故**不判 P1**；但授权基础若只靠候选自证，exact-head 审查无法确认其合规。
- 建议：FF 前由 Codex 在 `scope-delta` 追加本轮 extension（或在该 checkpoint 中引用 `PROJECT_ORCHESTRATION_AUTHORIZATION`）后再集成。

### P3-01 `PASS_WITH_LIMIT` 标签含 PASS 字样，易在 Gate 汇总被误读

`codex-scratch-build-preflight-r1.md:23` 把 source pins 记为 `PASS_WITH_LIMIT`。该项实际证明的是 **Git LF blob → CRLF 的预测转换**与冻结 pin 一致，真实 clone checkout 字节为 `NOT_RUN`（同行与 `:47` 已如实披露限制）。建议改为 `PARTIAL / PREDICTED` 或 `MATCH_PREDICTED / CHECKOUT_NOT_RUN`，与"不得推导 PASS"的 Gate 语义一致。

### P3-02 准入关键测量缺少版本化原始输出

`wsb --version` / `wsb list --raw` 有 4 个版本化原始文件；但 WSB AppX identity、`wsb.exe` SHA-256/大小、非提权判定、`VirtualizationFirmwareEnabled`、总/可用 RAM、物理核心、C:/G: 空闲空间仅以报告内摘要存在，无机器可读原始输出，也未标注字段/类 provenance（例如"总 RAM"取自 `Win32_ComputerSystem.TotalPhysicalMemory` 还是 `Win32_OperatingSystem.TotalVisibleMemorySize`；`31.647 GiB` 更接近后者，与 32 GiB 机器的硬件保留一致）。建议补一份 JSON/TSV 原始输出，使 preflight→Smoke admission 链条可独立复核。

### P3-03 delivery checkpoint 计数口径含糊

`codex-checkpoint-p02-non-elevated-preflight-delivery.md:5` 写"4 个限域状态文档修改与 9 个预检证据文件"，4+9=13，而候选实测 **14** 路径（差值=其自身未计入）。建议写成"4 个 `doc/**` 状态段 + 10 个 `verification/P02/**` 证据文件（含本 checkpoint）"，避免后续 Reviewer 读作漏项。

### P3-04 manifest `head` 与报告所述 root HEAD 不同且未说明

`codex-process-isolation-root-start-manifest.json` 的 `head`=`549a6544f0be1eec66c09ece393fd1a409f10bf3`，而报告/checkpoint 记 root `main@6855c113…`。manifest 记录的是**冻结时** HEAD，其 203 项条目仍与 live root 匹配（我已复算），但报告未说明该时间口径，易被误判为 head mismatch。建议加一句说明。

### P3-05 HostFolder 12 行混合 Smoke 与 Build-only 映射，未标注构成

`codex-scratch-build-preflight-hostfolders-r1.tsv` 12 行 = 10 个 Smoke 宿主根（clone + 9 个输入；canary 是 clone 内子路径）+ **2 个 Build-only** Git for Windows 根。proposal `:89`/`:118` 明确 r3 Smoke config **不含 Git**，且 Smoke config 为 **11 条映射**（1 RW + 10 RO，`proposal:60`）。报告/STATUS/PLAN 统一表述为"HostFolder `12/12`"，未说明 12 的构成，易与 Smoke mapping 计数（11）混读。建议每行加映射域标签（Smoke RO / Build-only RO / RW scratch）。

## 3. Scope / diff 核对

`base..candidate` = **恰好 14 路径**，与授权清单逐条一致；`git diff --check` EXIT=0；`+133/−5`。

- `doc/**`（4）：`00_INDEX.md`、`REBASELINE_PLAN.md`、`STATUS.md`、`tasks/P02.md`
- `verification/P02/**`（10）：`codex-scratch-build-preflight-r1.md`、`…-inputs-r1.tsv`、`…-hostfolders-r1.tsv`、`wsb-version-r1.{stdout,stderr}.txt`、`wsb-list-raw-r1.{stdout,stderr}.txt`、`codex-checkpoint-p02-{non-elevated-preflight-start,preflight-scope-frozen,non-elevated-preflight-delivery}.md`

不含产品源码/测试/依赖/共享契约/Schema/IPC/用户数据路径。**root dirty 路径 ∩ 候选路径 = 0**（我独立复算：root 203 项 = `4×" M" + 199×"??"`，交集 0）。

## 4. Gate 真实状态（互不推导）

| Gate | 真实状态 | 我的判定 |
|---|---|---|
| Root 保护现场 | **PASS**（203/203，canonical entries=36985 bytes / `3a54fa97…0e2`，staged=0） | 独立复算一致 ✔ |
| 当前命令进程非提权 | 作者记为 `False` | 作者证据（不同 shell），`NOT_VERIFIED`（by me） |
| WSB identity/version | `0.8.107.0`、156,160 bytes、SHA-256 `247e092b…c441` | 独立只读 stat+hash 一致 ✔ |
| WSB sessions | 空 list（无 running/stopped） | 与原始文件一致 ✔ |
| 固定 scratch clone | **不存在** | 独立实测不存在 ✔ |
| 架构/虚拟化/RAM/CPU/磁盘阈值 | 报告全项满足冻结阈值（≥4 GiB / ≥4096 MiB / ≥2 core / ≥1 GiB） | 数值合理；CIM 复算被拒（见 §5），`NOT_VERIFIED` |
| HostFolder（12 项） | 11 PRESENT + 1 预期 ABSENT | TSV 内部一致；构成标注见 P3-05 |
| 固定文件 pins（20 项） | 20/20 匹配 | 抽样 4/4 独立一致 ✔ |
| Source commit pins | 预测匹配（LF→CRLF 6/6 与 `codex-scratch-build-plan.md:29` pin 一致）；clone checkout=`NOT_RUN` | 独立复算 6/6 一致 ✔ |
| **Windows Sandbox Feature** | **`UNKNOWN`（未查询）** | 一致；未提权、未查询 ✔ |
| **完整 preflight** | **`BLOCKED / INCOMPLETE`** | 一致 ✔ |
| **Smoke admission** | **`NOT_ADMITTED`** | 一致 ✔ |
| **Smoke** | **`NOT_AUTHORIZED / NOT_RUN`** | 一致，无越权痕迹 ✔ |
| **Build Gate** | **`BLOCKED`** | 一致 ✔ |
| **build** | **`NOT_AUTHORIZED / NOT_RUN`** | 一致 ✔ |
| **P02 AC1–AC7** | **`BLOCKED / NOT_RUN`**（`doc/tasks/P02.md:39–45` 全 `[ ]`） | 一致 ✔ |
| **Hard Build Barrier** | **有效** | 一致 ✔ |
| 静态 hook/cache 闭包 | `BLOCKED / NOT_VERIFIED` | 与 `codex-hook-cache-closure-audit-r1.md:3` 一致 ✔ |
| R6 设计 Review | `APPROVED_WITH_CONDITIONS`（仅设计），N-06 `CLOSED`，新 findings `0/0/0/0` | 与 `dsh-review-process-isolation-r6.followup.response.md` §1/§5/§6 一致 ✔ |

无任何 PASS 由资源阈值/目录存在性推导；无"资源检查通过即允许 Smoke"的措辞。

## 5. 已运行 / 未运行检查

**已运行（全部只读）**：`git rev-parse HEAD/HEAD^{tree}/HEAD^`、`rev-list --count`、分支指针解析、`git status --porcelain -uall`（本 checkout，0 项）、`git diff --name-status/--name-only/--stat/--check base..candidate`（EXIT=0）、`git show --name-status`（`561f4105`/`6855c113`/`2394dc98`/`30da5faf`/`1c7efb17`）、`git grep`（base 树授权检索、candidate/base 树 pin 定位）、root 只读 status/rev-parse（`GIT_OPTIONAL_LOCKS=0`）、Python 只读复算 manifest canonical SHA-256 与 `git cat-file blob` 的 LF/CRLF 双哈希、`Get-FileHash`/`read_bytes` 抽样。

**我独立复算一致的结果（非转述作者结论）**：
1. manifest canonical entries SHA-256 = `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`，36985 bytes，203 项，`entry_count=203`/`staged_count=0`；
2. root `HEAD=6855c113…`、`branch=main`、203 项 = `4×" M" + 199×"??"`；root dirty ∩ candidate = **0**；
3. manifest 条目抽样 **6/6** path/size/SHA-256 与 live root 匹配；
4. `inputs-r1.tsv` 宿主文件抽样 **4/4** size+SHA-256 匹配（`python.exe`、`pyvenv.cfg`、`rc.exe`、`vcvars64.bat`）；
5. `hostfolders-r1.tsv` 的固定 clone 路径实测**不存在**；
6. `wsb.exe` 只读 stat+hash = 156,160 / `247e092b5c5bd37820f225a7dd3ddf10ae37a67e2751a19c24b802c84769c441`，与报告一致（**未执行 wsb CLI**）；
7. source commit `7ce3c40c` 三个 blob 的 LF 与 LF→CRLF SHA-256 **6/6** 与报告表及 `codex-scratch-build-plan.md:29` 冻结 pin 一致。

**未运行 / 未验证（一律不写 PASS）**：未查询/启用任何 Windows Feature；未提权；未运行任何 `wsb` 命令（未 `start/connect/exec`）、未启动 Sandbox、未 Smoke、未 Build、未 Cargo/Tauri、未 Vitest、未产品 runner、未 GUI/WebView；未创建/删除/改动固定 scratch clone；未访问用户漫画/数据库/Lock/current-pinned Revision/凭据；未写入任何文件（含未写 review 文件）。未能复算：`Get-CimInstance Win32_ComputerSystem/Win32_Processor/Win32_LogicalDisk/Win32_OperatingSystem` 在当前 DSH shell 一律返回"拒绝访问"，故 RAM/可用内存/物理核心/磁盘/虚拟化标志为**作者本地测量**，`NOT_VERIFIED`；非提权判定（不同 shell）与 AppX 包身份字符串 `Get-AppxPackage` 亦未重做。作者记录的 `verify_plan.py` EXIT=0（196 节点）**本轮未运行**（避免任何写副作用），记为作者证据。

## 6. 逐项核对结论（对应审查目标 1–5）

1. **范围**：✔ 精确 14 路径、HEAD/tree/parent 正确、reviewer checkout clean、无产品源码/依赖/共享契约/用户数据/越界路径。授权**基础**见 P2-01。
2. **证据一致性**：✔ 报告 ↔ 4 个原始 stdout/stderr ↔ 两个 TSV 相互一致；计数（HostFolder 12、pins 20、4 个模型输入）、WSB identity/hash/version/list、架构/虚拟化/RAM/CPU/磁盘阈值、固定 clone absent 记录严谨；source pins 明确区分 Git LF blob、LF→CRLF 预测值与**尚未创建 clone** 的真实 checkout `NOT_RUN`。唯一保留：PASS 标签（P3-01）、原始输出完整性（P3-02）、构成标注（P3-05）。
3. **状态如实性**：✔ Feature=`UNKNOWN`（未查询）、完整 preflight=`BLOCKED / INCOMPLETE`、Smoke admission=`NOT_ADMITTED`、Smoke=`NOT_AUTHORIZED / NOT_RUN`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier 有效；**无 PASS 推导**。
4. **文档同步**：✔ Plan/STATUS/Index/P02 顶部当前状态准确；`REBASELINE_PLAN` 明标"前次检查点快照…已由上方 2026-10-10 checkpoint 取代"，`P02.md:81` 明标历史段；无"资源通过即允许 Smoke"措辞、无跨文档 Gate 冲突；AC1–AC7 口径在三个状态文档中已统一（既存 R3-06 `AC1–AC6` 仅留在冻结的 proposal/plan 设计文本，延期登记有效）。
5. **验收范围**：✔ scope-frozen checkpoint §验收只要求报告完整性、独立 exact-head Review、路径交集=0 与 post-FF 验证；未把 Sandbox/Smoke/Build/产品行为作为本次审查通过前提。

## 7. 证据限制

本 Review 的独立复算覆盖 Git 元数据、blob 哈希、文件哈希、路径存在性与 manifest 规范化哈希；**不覆盖** CIM 资源值、非提权判定与 AppX 身份查询（当前 DSH shell 受权限限制），这些是作者本地测量（报告本身 `:48` 已要求任何未来 Smoke admission 前在同一非提权交互 PowerShell 即时重核）。大体积输入（`model.safetensors` 171 MB、`yolo11s-seg.onnx` 40 MB、Node/cargo/cl 等）我未重算哈希，仅抽检了 4 个小文件。本次审查**不声称**我的环境重复通过了作者的宿主测量。

## 8. 是否建议 Codex 集成

**建议集成，但须先满足 P2-01**：补登记本轮 scope 授权依据（`scope-delta` extension，或在该 checkpoint 引用 `PROJECT_ORCHESTRATION_AUTHORIZATION`），并可顺带处理 P3-01/P3-03/P3-04/P3-05。之后 `561f4105` 可 fast-forward 集成；集成后按 scope-frozen checkpoint §验收复跑 post-FF 验证（route validator、`git diff --check`、目标 HEAD、root 203 项 manifest、路径交集）。集成**不得**改变任何 Gate：Feature 仍 `UNKNOWN`、Smoke admission 仍 `NOT_ADMITTED`、Smoke/Build/AC 状态不变。

## 9. 下一条安全动作

> Codex 在 `codex/P02-process-isolation`（现 `561f4105171b99910d739698380787f35203d3f2`）上补登本轮 scope extension 并修订 P3 措辞，形成新的纯证据 commit；随后本地 fast-forward 集成到 `main`，执行 post-FF 验证（196 节点路线 validator、`git diff --check`、目标 HEAD/tree、root 203 项 protected manifest、root dirty ∩ 集成路径=0）。**不得**提权、查询/启用任何 Windows Feature、运行 `wsb` 或创建 `G:\CODEX\P02-scratch-build-source`、启动 Sandbox/Smoke/Build/产品测试；`Feature=UNKNOWN`、完整 preflight=`BLOCKED / INCOMPLETE`、`Smoke admission=NOT_ADMITTED`、`Smoke=NOT_AUTHORIZED / NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、P02 AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier 保持有效。

**Reviewer 声明**：本次审查全程只读；未修改本 checkout、Git/index、main root 或其他 worktree，未新建/删除文件，未提权、未查询/更改/启用任何 Windows Feature、未运行 `wsb`/Sandbox/Smoke/Build/产品 runner/Vitest/GUI/WebView，未创建或改动 scratch clone，未访问用户数据或凭据；未执行的检查一律标为 `UNKNOWN` / `NOT_RUN` / `BLOCKED` / `NOT_VERIFIED`，未写为 PASS。