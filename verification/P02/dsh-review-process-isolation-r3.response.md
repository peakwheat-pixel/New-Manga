# P02 Process Isolation r3 — DSH 独立设计 Review（正式）

---

## 1. 审查范围、精确基点与工作区状态

| 项 | 值 | 复核方式 |
|---|---|---|
| Base | `3555213a748a7b407400589e1490a387353dec16`（r2，`docs(P02): revise sandbox isolation gate r2`） | `git rev-parse` |
| Base tree | `38f312374c88713b7e10269c9b4ecc5eb8e1eeda` | `git rev-parse 3555213a^{tree}` |
| Candidate | `92361e3578eedb93d7cf6c4c5a4db06652d31fe9`（r3，`docs(P02): revise process isolation smoke gate r3`） | `git rev-parse HEAD` |
| Candidate tree | `919e10809390a7fa6c4cf7133ae36ac600a9b517` | `git rev-parse HEAD^{tree}` |
| Parent / commit 数 | parent=`3555213a…`（=base），`base..HEAD` = 1 commit | `git log -1 --format='%H %P'`、`git rev-list --count` |
| Checkout | `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r3`，detached HEAD=`92361e35` | `git worktree list` |
| 洁净性 | 审查开始与结束 `git status --porcelain --untracked-files=all` **均为 0 项**；本轮未写任何文件、未改 Git、未动 index | 两次 `git status` |
| Diff 规模 | 18 路径，+416/−20；`M doc/tasks/P02.md`；其余全部为 `verification/P02/**`（3 个 checkpoint、r3 XML、r3 validation、Build input addendum、7 个 DSH r2 review 证据） | `git diff --name-status/--stat` |
| 范围合规 | 无产品代码/依赖/共享契约/Schema/AC/Owner allowlist/`STATUS`/`REBASELINE_PLAN` 变化；P02.md 仅 `### Codex-only scratch-build output boundary` 段（L60、L62、L69）改动 | 逐路径比对 |

补充独立核验：`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a` 是 `549a6544…`（root main）的祖先（`merge-base --is-ancestor` exit=0，相隔 3 个 commit），且两者之间 **无任何 `doc/`、`verification/` 之外的路径**，佐证 proposal L6 的“差异仅有 doc/ 与 verification/”。

---

## 2. 决定

**Decision：`APPROVED_WITH_CONDITIONS`（仅设计/Scheme Review）。**

- 本决定批准的是 **r3 进程隔离设计方案与停止条件**（proposal r3、plan/gate 增补、r3 Smoke config 的字节/哈希设计、F-01–F-10 处置登记）作为设计基线；它**不等于**任何运行时事实。
- 它**最多**允许：在固定 r3 head 下执行 **本机非提权、只读** 的 feature/resource/path/manifest preflight（proposal L78 步骤 1）；以及按条件 C1–C5 完成文档/证据修正。
- 它**不授权**：Windows Optional Feature 查询以外的任何功能变更或启用、提权、`wsb start/connect/exec`、Sandbox 启动、Smoke 执行或 Smoke PASS、Build Gate PASS、任何产品 build/tests/runner/Vitest/GUI/WebView、AC1–AC6 PASS。
- 条件（必须闭合，未闭合前不得进入对应 Gate）：
  - **C1**：修正“MSVC/SDK 为 Build-only、与 Smoke 分离”的表述与 r3 Smoke config 事实不符（R3-01）；若选择改 config 则必须重新冻结 bytes/hash 并再次 exact-head Review。
  - **C2**：修正 r3-start checkpoint 中 addendum 的过期字节/哈希与“未修改”声明（R3-02）。
  - **C3**：冻结 HostFolder manifest 聚合哈希的 record 字段 schema（R3-03）。
  - **C4**：统一 clone 命令在四处文档中的表述（R3-04）。
  - **C5**：登记 r3 的 scope 依据，并补 r3 delivery checkpoint（R3-05）。

Gate 语义分层（互不推导）：**Scheme/Plan Review = 本报告**；**Smoke admission = NOT_ADMITTED**（条件+preflight 未完成）；**Build Gate = BLOCKED**；**产品验收 = BLOCKED**。

---

## 3. Findings 与 r2 F-01..F-10 映射

### 计数

**P0 = 0；P1 = 0；P2 = 2；P3 = 4。**
无 P0/P1：未发现数据破坏、越权、提权、Sandbox/Feature 启动、把未验证事实写成 PASS 的情形。

### 编号发现

**R3-01｜P2｜“Build-only MSVC/SDK 与 Smoke 分离”与 r3 XML 事实矛盾**
- 证据：
  - `codex-scratch-build-input-host-inventory-r2-build-addendum.md:15` 标题 `## MSVC / Windows SDK（Build config only）`；`:47` `Its Git/MSVC mappings must not be added to the r3 Smoke config.`
  - 但 `codex-p02-wsb-smoke-config-r3.xml:19–21` 实际映射 `…\2022\BuildTools`、`…\Microsoft Visual Studio\Installer`、`…\Windows Kits\10`（三条 ReadOnly=true）；`proposal:38–40` 也把它们列在 Smoke 映射表内；`:17` 自述“BuildTools 与 SDK 根目录已在 r2 smoke mapping 表中列出”。
  - 命令级矛盾：`proposal:89` 要求 Build 使用“**相同真实 HostFolder mapping 集合**”，而 `plan:40`/`addendum:42` 要求 Build config “**额外**只读映射 … Git for Windows 与 **MSVC/SDK** inputs … 不同于 r3 Smoke config”。
- 影响：Smoke/Build 的“config 分离”并未落地——MSVC/SDK 三条根映射自 r2 起一直在 Smoke config 内；Build 设计若按“额外”表述再次加入这三条，会产生重复/重叠 mapping，且“相同集合”与“不同 config”两种口径并存，Build Gate 冻结时无法判定唯一正确集合。注意：该 mapping 本身只读、且 F-07 已禁止向真实输入写 canary，**无写入/破坏风险**，属设计-文档一致性问题。
- 要求动作：二选一并写清：(a) 修正 addendum/plan/proposal 口径为“VS BuildTools / Installer / Windows Kits 为 Smoke 与 Build **共有**只读映射，仅 Git for Windows 为 Build-only”，同时修正 `proposal:89` 的“相同集合”措辞；或 (b) 从 Smoke config 移除这 3 条 → 新字节/哈希 → 重新 exact-head Review。闭合前不得冻结 Build config。

**R3-02｜P2｜r3-start checkpoint 的 addendum 字节/哈希过期，且“未修改”声明不成立**
- 证据：`codex-checkpoint-p02-process-isolation-r3-start.md:13` 记录 `…build-addendum.md | 4280 | 1acbe6711a9762b190cad9c23a0f89b8fe8223762072a17f7f3aa1ec7ff7ddbc`；同一文件 `:26` 声明“之前记录的 11 个 carry-forward artifacts **未修改**”。实际提交内容为 **4790 bytes / `dfaa8ecc8e49f5c70e1835d5adeb23a2a4da76e09ec94fe4c39ddf9cbc107c47`**（`git cat-file blob HEAD:…` 复算）。其余 10 条（r2-delivery/r2-review/r3.xml/dispatch/exit/mount/prompt/response/session/stderr）独立复算 **10/10 全部匹配**。
- 影响：r3 自身交付证据出现“checkpoint 记录不可复算 + 状态不变量自相矛盾”，与自己刚闭环的 F-09 同类；未来恢复/审计可能据此误判 drift。不改变任何 Gate，不影响 Smoke config 身份（XML 2609/`9af44513…` 已复算正确）。
- 要求动作：把 `:13` 更新为交付版本的真实 bytes/SHA-256（或明确标注为 14:34 时点快照 + 交付值），并修正 `:26` 的“未修改”表述；可复算口径与 F-09 erratum 统一。

**R3-03｜P3｜分级 manifest 配方可复算，但未冻结 record schema**
- 证据：`proposal:44` 已固定排序（`(casefold(path), path)`）、路径分隔符、大小写冲突拒绝、`json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(',',':'))`、UTF-8/SHA-256、并明示“分级目录 hash 只绑定路径/类型/大小，不声称大根内每个文件字节均已哈希”（**限制披露充分**）；但 `records` 的字段名/类型未定义（例如大根的 per-file `sha256` 缺省表示）。
- 影响：F-08 的“第三方可复算”只满足一半；不同实现会产出不同规范 JSON → 不同聚合 hash。
- 要求动作：在 Smoke preflight 前把 record schema（字段名、类型、缺省/空值语义）写进 proposal/addendum。**不阻断**只读 preflight。

**R3-04｜P3｜clone 命令四处表述不一致**
- 证据：`doc/tasks/P02.md:62`、`proposal:17`、`plan:38` 均为 `git clone --no-local --no-hardlinks --no-checkout --single-branch --branch main`；但 `proposal:79`（Isolation smoke 步骤 2）写 `git clone --no-local --no-hardlinks --no-checkout`，缺 `--single-branch --branch main`，且未写“移除 origin”（`:79` 仅写“空 remotes”，`plan:38` 写“移除 origin”）。
- 影响：命令级漂移；虽不改变隔离论证（`--no-local/--no-hardlinks` 仍在），但执行者可能按不同命令创建 clone，导致 config/evidence 口径不一致。
- 要求动作：以 P02.md 边界句为规范句统一四处。

**R3-05｜P3｜r3 缺少 scope 登记引用与 delivery checkpoint**
- 证据：唯一 scope 文件为 `codex-scratch-build-process-isolation-scope-delta-r1.md`，状态 `FROZEN_FOR_R2_REPAIR`（`:3`），其“精确修改许可”（`:13`）只枚举 r2 的 clone 形态内容；r3 在 P02.md 同一段新增了 Smoke 准入门槛句与 scratch-local canary 句（`doc/tasks/P02.md:60,69`），并新增 r3 config/validation/checkpoint，未在任何 r3 文件引用该 scope delta；`plan:81` 声称 r3 canonical hash“需在 delivery checkpoint 中精确记录”，但候选内**不存在 r3 delivery checkpoint**（glob 仅 `r3-start`、`r3 XML`、`r3-validation`），hash 仅落在 `proposal:60` 与 `validation:11`。
- 影响：治理可追溯性弱化；非产品范围问题。
- 要求动作：在 r3 checkpoint 中补一句 scope 依据（boundary 段 + `verification/P02/**`），并补 r3 delivery checkpoint（记录 XML 2609/`9af44513…` 与 18 路径清单）。

**R3-06｜P3｜AC 计数表述不一致（既存，非 r3 引入）**
- 证据：`doc/tasks/P02.md:39–45` 定义 **AC1–AC7**；`STATUS.md:3`、`REBASELINE_PLAN.md:5` 与 r2/r3 全部 gate 文本写 **AC1–AC6**（其中 `REBASELINE_PLAN.md:66` 又写 AC1–AC7）。
- 影响：仅表述口径；不影响本设计。要求动作：P02 收口时统一写 AC1–AC7（含固定证据/发现处置 AC7）。本轮不需改动。

其他非编号观察：F-05 阈值组合 `host RAM ≥ 4 GiB` 且 `available memory ≥ 4096 MiB` 在恰好 4 GiB 的机器上不可同时满足（fail-closed，不会伪 PASS），建议写成“总量 ≥4 GiB 且可用 ≥4096 MiB，实际需更高”。

### r2 F-01..F-10 逐条映射

| ID | 状态 | 证据（路径:行） | 判定 |
|---|---|---|---|
| F-01 guest Git | **CLOSED（设计）** | `addendum:6–13`（Git cmd/mingw64、版本 2.52.0.windows.1、size/SAH-256、ReadOnly=true、Build-only、Smoke 不含）；r3 XML `:11–21` 无 Git mapping（我 grep 全文无 `Git`） | Git 与 Smoke 分离**成立**；guest 解析仍 `NOT_VERIFIED`，属 Build Gate 待测项 |
| F-02 MSVC linker/SDK 环境 | **CLOSED（设计，伴 R3-01）** | `addendum:21–24`（cl/link/rc/mt 版本/size/SHA-256）、`:28–40`（`VCToolsInstallDir`/`WindowsSdkDir`/`WindowsSDKVersion`/PATH/INCLUDE/LIB/GIT_EXEC_PATH + `where.exe` 复核）；`plan:40` | 缺显式定位的问题已闭环；“Build-only”标签与 XML 矛盾见 R3-01 |
| F-03 Networking token 可能被静默忽略 | **CLOSED（设计）** | `proposal:58`（exit=0 不足；须 guest 无 default route + 同 endpoint TCP 失败，否则 BLOCKED；不得换拼写）、`:81`（步骤 4）、`:85`（非 fail-closed 即 BLOCKED/NOT_VERIFIED） | 失败模式被显式覆盖；运行态证据未产生 → Smoke 仍 NOT_RUN |
| F-04 `MemoryInMB > 4096` | **DEFERRED（显式）** | `proposal:64`（`>4096` 仍 `UNKNOWN`，未经实测不得用于 Build config）、`:121`；`plan:40`（“>4096 MiB 而无法实证接受范围时 BLOCKED”）、`:79` | 两个 XML 的 `MemoryInMB` 均为 2048（复算确认），无任何 >4096 授权；延期合理 |
| F-05 资源阈值数值化 | **CLOSED（设计）** | `proposal:64`（AMD64/ARM64、BIOS virtualization、RAM ≥4 GiB、磁盘 ≥1 GiB、≥2 CPU core、可用内存 ≥4096 MiB、C:/G: ≥1 GiB free）、`:78`、`:122` | 全部可测量；阈值偏严为 fail-closed |
| F-06 dirty clone 停止条件 | **CLOSED（设计）** | `proposal:79`（`git status --porcelain --untracked-files=all` 必须为空；任何状态项/未登记文件 → BLOCKED；**保留现场，不清理、不换路径**）；`plan:41,48` | 数据保留要求满足 |
| F-07 RO canary 可能写入真实输入 | **CLOSED（设计）** | `proposal:31`（canary = scratch clone 内子目录，独立 RO alias）、`:80`（仅在 `C:\P02\readonly-canary` 与 scratch RW 路径写入）、`:124`；`doc/tasks/P02.md:69`（明确禁止对 Python/模型/Node/Rust/VS/SDK 真实输入写入）；XML `:12` | canary 只落在一次性 Task scratch（`tmp/**` 已在 P02.md allowlist 内）；写成功即 BLOCKED 且禁止删除 |
| F-08 manifest 配方 + cache secret scan | **CLOSED（设计，伴 R3-03）** | `proposal:44`（确定性配方+限制披露）、`:125`；`plan:40`（seed 前 credential/secret filename 与 token pattern 扫描，命中即不复制并 BLOCKED；`.npmrc`/日志/Cargo credentials/config 永不 seed） | 限制披露充分；record schema 未冻结见 R3-03 |
| F-09 r2 candidate hash 不可复算 | **CLOSED（已独立复算）** | `codex-checkpoint-p02-process-isolation-r2-candidate.md:23–36` erratum（Git blob SHA-1 + canonical UTF-8/LF SHA-256 + bytes） | 我按 `git rev-parse <rev>:<path>` + `git cat-file blob` 复算 **8/8 行全匹配**（43106/4531/2397/48115/8855/15020/16136/2269，`cr=0`、无 BOM）；旧表已标为历史捕获并声明不作为 candidate identity（`:25`） |
| F-10 r1/r2 raw JSONL 出库 | **CLOSED（设计/证据）** | r3-start checkpoint `:22`（外部路径 `…/p02-process-isolation-plan/dsh-review-logs/dsh-review-process-isolation-r2.stdout.jsonl`，size=431099，SHA-256=`e59473d7…`）；`dsh-review-process-isolation-r2.dispatch.md:7`；r1 同口径见 `dsh-review-process-isolation-r1.dispatch.md` | 外部文件实际存在、size/SHA 完全匹配，含 `"thinking"` 37 处；`git ls-tree -r` 显示候选树内**无** r2 JSONL；prompt/response/dispatch/exit/session/mount/stderr 均已版本化且哈希匹配 |

**独立复算的关键正例（支撑上述判定）**：r3 XML canonical bytes = **2609 bytes / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`**（`i/lf w/crlf`；`cr=0`、无 BOM、无 XML 声明），结构 = 11 mappings / 1 RW / 10 RO、无 `LogonCommand`；r2 XML = 10/1 RW/9 RO，且两者 `Compare-Object` 仅有 canary 一行差异 → proposal L60“相对 r2 只新增一个 canary mapping；真实只读输入映射不增加”**成立**。root manifest `entries` 按记录配方复算 = **36985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`**（`status_command` 含 `-z`，路径编码口径完整）；root live 状态与 manifest **203/203** 路径/状态一致（唯一差异是 git 默认 `core.quotepath` 转义显示，非真实差量）。

---

## 4. 明确 Gate 状态（不推导、不带 PASS）

| Gate | 状态 | 依据 |
|---|---|---|
| Windows Sandbox Feature（`Containers-DisposableClientVM`） | **UNKNOWN** | 候选内无查询证据；设计自述查询需提权（`proposal:78,93`）；本轮未查询 |
| Isolation Smoke | **NOT_RUN / NOT_AUTHORIZED**（Smoke admission=NOT_ADMITTED） | 仅设计；`proposal:76,85`、`plan:81`、`gate:58`；未执行 `wsb start/connect/exec` |
| Build Gate | **BLOCKED** | `gate:59`、`plan:81`、`proposal:129`；未被任何 r3 文档改变 |
| build | **NOT_AUTHORIZED / NOT_RUN** | 同上；无任何 build 命令执行证据 |
| 产品 AC1–AC6（Task 内另有 AC7） | **BLOCKED** | `gate:59`、`proposal:129`；无产品代码/测试差量（diff 仅 doc/verification） |
| P02 Hard Build Barrier | **保持有效（active）** | `gate:59`、`proposal:129`、`plan:81` |
| Scheme/Plan Review（本报告） | **APPROVED_WITH_CONDITIONS（仅设计）** | 本文 §2–§3 |

未发现任何把 XML parse、文档承诺、设计推导写成运行态 PASS 的表述；所有 r3 文件在 L76/L83/L85/L129 等处均显式区分 Review/Smoke/Build/产品验收。allowlist 侧无 mismatch：产物路径仍在 P02.md 既有 scratch allowlist（`doc/tasks/P02.md:64–67`），canary 位于其 `tmp/**` 之下，Owner allowlist 与 AC 未变。

---

## 5. Reviewer 限制、已执行命令与是否阻断下一步

**执行的命令（全部只读；未写任何文件、未改 Git、未动 Windows/Sandbox/build/产品测试）**
- `git rev-parse HEAD/HEAD^{tree}/3555213a^{tree}`、`git log -1 --format`、`git rev-list --count`、`git diff --name-status/--stat`、`git status --porcelain --untracked-files=all`（审查前后均 0 项）、`git ls-files --eol`、`git ls-tree -r --name-only`、`git merge-base --is-ancestor 7ce3c40 549a6544`（exit=0）。
- `git cat-file blob <blob> | python -c`（在内存中算 canonical SHA-256，避免任何临时文件写入；沙箱拒绝了我对 `%TEMP%` 的写入尝试，故改用该管道）。复算对象：r3 XML、r2 XML、r2 erratum 全部 8 行、r3-checkpoint 11 行、root manifest entries。
- `python -c`（`xml.etree` 解析 XML 结构与 mapping 计数；读取外部 raw JSONL 的 size/SHA/`thinking` 出现次数）。
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → **EXIT=0，196 nodes**，与 `codex-process-isolation-r3-validation.md:9` 一致（该脚本仅读 `task-inventory.csv`，无写操作，属规划校验而非产品测试）。
- `git -C "G:/CODEX/New Manga" status --porcelain --untracked-files=all`（只读）→ 203 项，与 manifest 路径/状态集合一致。

**未执行/未复现（限制）**
- 未查询/修改任何 Windows Feature，未运行 `wsb`，未启动/连接 Sandbox，未执行 Smoke，未 build，未运行 runner/Vitest/GUI/WebView；所有运行态均按 `UNKNOWN/NOT_RUN/BLOCKED` 记录。
- 未复核 `addendum` 中 Git/MSVC/SDK 主机可执行文件的版本/大小/SHA-256（属主机工具链事实，本轮未读取 `C:\Program Files…`），故这些值对本 Review 为 **NOT_VERIFIED**；不影响 F-01/F-02 的“设计已登记”判定。
- root 203 项只做了路径/状态集合比对，未逐文件复算 size/SHA-256（manifest 自身的 `entries` 聚合 hash 已独立复现）。
- 受限 PowerShell（ConstrainedLanguage）阻止 .NET 静态调用与 `%TEMP%` 写入；已用 git/python 管道规避，未擅自提权或改道写入仓库。
- 本 Reviewer 非作者（author=Codex），detached 只读 checkout，全程洁净；本报告不授权 build，也不把任何 NOT_VERIFIED 转为 PASS。

**是否阻断下一步只读 preflight：不阻断。** 无 P0/P1。可按 `proposal:78` 步骤 1 在固定 r3 head 下执行非提权只读 feature/资源/路径/manifest preflight；但 **C1 与 C2 必须在任何 `wsb start` 尝试与 Build config 冻结之前闭合**，C3/C4 应在 Smoke preflight 证据定稿前闭合。提示期望管理：feature 查询在非提权 shell 下可能失败，此时按设计 fail-closed 得到 `BLOCKED`，属正确结果而非缺陷。

**推荐下一步（可直接转发 Codex）**：
> 在 `codex/P02-process-isolation` 同一 scope（P02.md 的 Codex-only boundary 段 + `verification/P02/**`）内：(1) 按 R3-01 修正 Build-only/Smoke mapping 分离口径（若改 config 必须重算 r3 canonical hash 并重新 exact-head Review）；(2) 修正 r3-start checkpoint `:13`/`:26` 的过期哈希与“未修改”声明；(3) 冻结 manifest record schema；(4) 统一四处 clone 命令；(5) 补 r3 scope 引用与 r3 delivery checkpoint。完成后固定新 commit，再派 DeepSeek Harness 做 exact-head 设计复审；复审期间仍 `Smoke=NOT_AUTHORIZED/NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED/NOT_RUN`、AC1–AC6/AC7=`BLOCKED`，Hard Build Barrier 有效。
