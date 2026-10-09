# P02 Process Isolation r4 — DSH 非作者独立设计 Review（正式）

---

## 1. 审查范围、精确基点与工作区状态

| 项 | 值 | 复核方式 |
|---|---|---|
| Base / r3 reviewed candidate | `92361e3578eedb93d7cf6c4c5a4db06652d31fe9`（`docs(P02): revise process isolation smoke gate r3`，parent=`3555213a…`，tree=`919e1080…`） | `git log -1` |
| Candidate / r4 delivery | `fb0a7668d948ae68f15fd59aaffd6aedf6663c99` | `git rev-parse HEAD` |
| Candidate tree | `61abeb088dce6536494c27611f298187961c35ae`（=期望） | `git rev-parse <c>^{tree}` |
| Candidate parent | `92361e3578eedb93d7cf6c4c5a4db06652d31fe9`（=base，符合期望；`base..candidate`=**1** commit） | `git rev-parse <c>^`、`git rev-list --count` |
| commit 元数据 | author/committer=`peakwheat-pixel <peak.wheat@gmail.com>`，`2026-10-09T23:06:46+08:00`（=15:06:46 UTC），subject=`docs(P02): close r3 process isolation review findings` | `git log -1 --format=%H %P %T %aI %s` |
| 本审查 checkout | `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r4`，detached HEAD=candidate | `git worktree list` |
| Git 目录 | common=`G:/CODEX/New Manga/.git`；worktree git-dir=`…/P02-process-isolation-review-dsh-r4` | `git rev-parse --git-common-dir/--git-dir` |
| 洁净性 | 审查开始与结束 `git status --porcelain=v1 --untracked-files=all` 均 **0 项**；无 staged/工作区差量、无 stash、无 untracked JSONL | 两次 `git status` |
| Diff 规模 | 18 路径，+324/−30；`M doc/tasks/P02.md`，其余 17 条全在 `verification/P02/**` | `git diff --name-status/--raw/--numstat/--shortstat` |

**18-path scope 检查方式**：直接对 `base..candidate` 运行 `git diff --name-status/--raw` 取路径与 blob SHA-1，并把该 18 路径集合与 (a) scope extension（`codex-scratch-build-process-isolation-scope-delta-r1.md:45–56`）枚举的许可文件、(b) `doc/tasks/P02.md:58` 的 Codex-only boundary 段、(c) root 203 项保护 manifest 路径集合分别求交。结果：18/18 落在许可范围；与 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、产品源码/测试/依赖/Schema 路径交集=**0**；与 root dirty 路径交集=**0**。`git diff --check` EXIT=0。

---

## 2. 决定

**Decision：`APPROVED`（仅 Design / Scheme Review）。**

- 批准对象：r4 对 r3 条件 C1–C5 的定向修订、clone 命令规范化、manifest record schema 冻结、scope/delivery checkpoint 补录，以及更新后的 F-01–F-10 处置登记，作为**设计基线**。
- 它**最多**允许：在本固定 candidate 下执行 `proposal:78` 步骤 1 的**本机非提权、只读** preflight（feature/资源/路径/manifest），以及第 6 节的 3 项非阻断 P3 文档收尾。
- 它**不授权**：Windows Optional Feature 的查询以外的任何变更/启用、提权、`wsb start/connect/exec`、Sandbox 启动、Smoke 执行或 Smoke PASS、Build Gate PASS、任何产品 build/tests/runner/Vitest/GUI/WebView、任何 AC PASS。
- 合规性说明：C1–C5 已实质闭合、无 P0/P1/P2；仅余 3 项 P3（文档指代/许可描述精度）。按 r3 的判别口径（P3 不阻断只读 preflight），故给 `APPROVED` 而非 `APPROVED_WITH_CONDITIONS`；若治理方要求把所有本轮 finding 转为条件，这 3 项可在下一次纯文档 commit 内闭合，且**不需要**改动 XML 或任何 canonical hash。

Gate 语义分层（互不推导，不写 PASS）：**Design Review=本报告 APPROVED**；**Smoke admission=NOT_ADMITTED**；**Smoke=NOT_AUTHORIZED / NOT_RUN**；**Build Gate=BLOCKED**；**build=NOT_AUTHORIZED / NOT_RUN**；**产品验收=BLOCKED**。

---

## 3. Findings

**计数：P0 = 0；P1 = 0；P2 = 0；P3 = 3。**
无 P0/P1/P2：未发现数据破坏、越权/提权、Sandbox/Feature 启动、把未验证事实写成 PASS、产品范围或共享契约变化。

**N-01｜P3｜r4 未同步的旧状态/旧 config 指代**
- 证据：`codex-scratch-build-input-host-inventory-r2-build-addendum.md:13` 仍写 “**r2** Smoke config 不含这些 mapping”，而同文件 `:47` 已改为 “already exist in the **r3** Smoke config”；`codex-scratch-build-plan.md:81` 仍写 “当前 proposal=`PROPOSED / REVIEW_PENDING`”，而 `proposal:3`/`gate:58` 已记录 r3=`APPROVED_WITH_CONDITIONS` + r4 待审。
- 影响：同一子任务内 config 与 Review 指代不一致；Build config 冻结或恢复审计时可能取错参照基线。两句陈述本身为真（r2、r3 config 均无 Git 映射），故属**文档一致性问题**，不改变任何隔离论证或 Gate。
- 可验证修复：把 addendum`:13` 改为“当前冻结的 r3 Smoke config 不含这些 mapping”；在 plan`:81` 增补“r3 已 `APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=0/0/2/4），r4 定向修订待 exact-head Review”。

**N-02｜P3｜scope 文件级许可描述窄于实际改动**
- 证据：`codex-scratch-build-process-isolation-scope-delta-r1.md:52` 对 `codex-checkpoint-p02-process-isolation-r3-start.md` 的许可是“（只追加/校正 r3 hash 时间点 erratum）”；但 r4 实际还改了 `codex-checkpoint-p02-process-isolation-r3-start.md:23`（`Build-only Git/MSVC inputs` → `Build-only Git inputs、MSVC/SDK 的显式 guest 工具定位与环境`）。
- 影响：改动本身服务 R3-01、且该文件已在本子任务许可清单内，无越界路径；但 scope 文本与交付差量不完全对应，削弱 scope 可核验性。
- 可验证修复：把 `:52` 扩写为“…erratum 及 R3-01 措辞一致性修正”，或在 r4 delivery checkpoint 中显式登记该额外 1 行改动。

**N-03｜P3｜scope 章节引用名与真实标题不一致**
- 证据：`doc/tasks/P02.md:60` 写 “scope basis 见 … scope delta **§ R3 extension**”；实际标题为 `codex-scratch-build-process-isolation-scope-delta-r1.md:40` “## **r3/r4** scope extension”（r3 delivery checkpoint 用的是精确标题 “§ r3/r4 scope extension”）。
- 影响：权威 Task boundary 的 scope 指针无法按名精确定位章节，属 R3-05 同类可追溯性精度问题。
- 可验证修复：把 `P02.md:60` 统一为 “§ r3/r4 scope extension”。

**非阻断观察（不计入 finding）**
- r3 delivery checkpoint 的 `14:44:56 UTC` 建立时间为作者自述（该文件首次进入 Git 是 r4 commit）；但 `codex-checkpoint-p02-process-isolation-r3-review.md:7` 与 `codex-checkpoint-p02-process-isolation-r4-start.md:7` 均把它作为已存在、待更新的 artifact 引用，时间线自洽（r3 commit 14:42:29 → delivery 14:44:56 → dispatch 14:54 → review 14:56 → r4-start 14:57 → validation 15:04 → r4 commit 15:06:46）。未发现矛盾，仅“Git 不可复算 provenance”。
- manifest record schema 已冻结字段/类型/枚举/null/排序/canonical JSON，第三方可**从 records 复算聚合 hash**；但“大根内哪些文件必须 `verified`”仍是执行时选择（`proposal:44`），建议运行时把选择规则一并写入报告，以增强同输入跨执行的漂移检测力。
- `codex-process-isolation-r4-validation.md` 的 “Manifest schema self-check / Clone sequence” 两行未附可复跑脚本或日志；我已独立复现其结论（clone 序列 4×377 字符逐字相同、schema 字段在 `proposal:44` 完整定义），故不构成 finding。
- `gate:39/50`、`scope-delta:3` 仍保留更早状态串（`PROPOSED / REVIEW_PENDING`、`FROZEN_FOR_R2_REPAIR`），但均在明确标注日期的历史分层内、且被后续小节/extension 声明为当前状态所取代，不作为 finding。

---

## 4. R3-01..R3-06 / C1..C5 逐条 disposition

| 编号 | Disposition | 独立证据 |
|---|---|---|
| **R3-01 / C1**（P2，mapping 口径矛盾） | **CLOSED**（选择 r3 建议的 (a)：只改文档，XML/hash 不变） | `addendum:1,3,15,17,26,42,47` 明确 “两个 Git for Windows 根 Build-only、VS BuildTools/Installer/Windows SDK 为 Smoke/Build 共用只读”；`proposal:38–40,89`；`plan:38–40,78`；`gate:57`。我解析 r3 XML：11 mappings、1 RW/10 RO、含 BuildTools/Installer/Windows Kits 三条 RO、**无 Git**；r2 XML=10/1 RW/9 RO，差异仅 canary 行。XML bytes/hash 在 base 与 candidate 上均为 **2609 / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`**（LF、无 BOM）。全仓库无残留 “Build config 额外加 VS/SDK” 表述。 |
| **R3-02 / C2**（P2，r3-start 哈希/“未修改”） | **CLOSED** | `codex-checkpoint-p02-process-isolation-r3-start.md:13` 改为 “`??`(14:34 UTC start snapshot) … 4280 (r3 delivery: 4790) / `1acbe671…` (r3 delivery: `dfaa8ecc…`)”；`:26` 改为“该时点与已记录快照一致；后续 r3 repair 曾修订其中的 Build addendum”，不再声称交付件未修改。复算：`92361e35:addendum` = **4790 bytes / `dfaa8ecc8e49f5c70e1835d5adeb23a2a4da76e09ec94fe4c39ddf9cbc107c47`** ✓；同表其余 10 条与 r3 commit blob **10/10 全匹配**（2551/`81e653dc`、2628/`b7473578`、2609/`9af44513`、1992/`c12c4931`、2/`9a271f2a`、315/`a9861b6a`、4906/`2ea2b75e`、24520/`14b3dca4`、113/`832b89c9`、0/`e3b0c442`）。14:34 快照值 4280/`1acbe671` 未进入任何 commit，Git 不可复算——但已被明确标注为时点快照（r3 允许的两种闭合方式之一）。 |
| **R3-03 / C3**（P3，record schema） | **CLOSED** | `proposal:44` 冻结：`schema_version`(int 1)、`path`（相对 HostFolder 根、`/` 分隔、根写 `.`、保留 Unicode code points 不规范化）、`type`(`file`/`directory`)、`size_bytes`（文件非负整数、目录 `null`）、`sha256`（实算 64 位小写 hex，否则 `null`）、`sha256_status`(`verified`/`not_computed`/`not_applicable`)；目录必须 `null/null/not_applicable`；排序 `(path.casefold(), path)`、根记录纳入；`json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(',',':'))` + 无 BOM UTF-8 + SHA-256、无时间戳/ACL/ADS；并明示“不证明 `not_computed` 内容未变、不声称大根每字节已哈希，报告必须披露”。未发现把 un-hashed bytes 声称 verified 的表述。 |
| **R3-04 / C4**（P3，clone 命令漂移） | **CLOSED** | 四处（`doc/tasks/P02.md:62`、`proposal:17`、`proposal:79`、`plan:38`）抽出的命令序列**逐字相同**（脚本比对：4/4 均为 377 字符，`IDENTICAL=True`），均为 `git clone --no-local --no-hardlinks --no-checkout --single-branch --branch main "G:\CODEX\New Manga" "G:\CODEX\P02-scratch-build-source"` → `remote remove origin` → `config core.autocrlf true` → `checkout --detach 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`。 |
| **R3-05 / C5**（P3，scope 登记 + delivery checkpoint） | **CLOSED** | `scope-delta:40–57` 新增 “r3/r4 scope extension”，状态 `FROZEN_FOR_R4_REVIEW`，冻结 P02 boundary 段 + 已列 `verification/P02/**` artifacts 并排除 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、产品/Schema/依赖、root dirty。`codex-checkpoint-p02-process-isolation-r3-delivery.md` 新增：scope basis 段、**18 条精确 r3 diff 路径**、XML identity（2609/`9af44513…`）、DSH r3 Review 结果。我复算 r3 diff = 18 路径且与该清单**逐条一致**（含 `r2-candidate` 修改项与 7 个 r2 DSH 证据）。 |
| **R3-06 /（无 C）**（P3，AC1–AC7 vs AC1–AC6 文案） | **CLOSED（按期延期登记）** | `proposal:3,141`、`codex-checkpoint-p02-process-isolation-r4-start.md:7`、`scope-delta:44` 均明确“既存差异、留待 P02 closeout、本轮不改”；`gate:59`/`proposal:129`/`plan:81` 仍写 “AC1–AC6=BLOCKED”。核实：`doc/tasks/P02.md:39–45` 定义 AC1–AC7（AC7 为固定证据与发现处置），`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:5` 写 AC1–AC6（而 `REBASELINE_PLAN.md:21` 写 AC1–AC7）——既存事实成立。**无任何** r4 文件把 AC7 报告为已验收（P02.md 的 AC 全部仍为 `[ ]`）。本轮不改 `STATUS`/`PLAN`（r4 scope 明确禁止），符合 DSH r3 指示。 |

**r3 非编号观察（RAM 阈值组合）**：`proposal:64` 已改写为“总内存 ≥4 GiB 与 available ≥4096 MiB 为**并列**要求；恰好 4 GiB 总内存的机器无法通过 available 阈值；任何不可读或低于阈值即 BLOCKED”，并同步 `proposal:122`（F-05 行）。已处理。

---

## 5. r2 F-01..F-10 独立复核

| ID | 状态 | 独立证据与限制 |
|---|---|---|
| F-01 guest Git | **CLOSED（设计）** | `proposal:118`、`addendum:6–11`；我解析 r3 XML 全 11 条 mapping **无 Git**；两个 Git 根为 Build-only。guest 解析=`NOT_VERIFIED`（无运行态证据，且本轮未读 host Git 文件）。 |
| F-02 MSVC linker/SDK 环境 | **CLOSED（设计；R3-01 措辞已修）** | `proposal:119`、`addendum:15–26,30–42,47`；r3 XML 三条 VS/Installer/SDK RO roots 已独立确认；PATH/INCLUDE/LIB/`where.exe` 复核要求齐备。host `cl.exe/link.exe/rc.exe/mt.exe` 版本/大小/SHA-256 由 addendum 登记，本轮**未读取 `C:\Program Files`**，对这些值为 `NOT_VERIFIED`。 |
| F-03 Networking token 静默忽略 | **CLOSED（设计）** | `proposal:58`（exit=0 不足，须 host endpoint 可达 + guest 无 default route + 同 endpoint TCP fail，否则 BLOCKED，不得换拼写）、`:81,85`；XML `Networking=Disabled`。运行态=`NOT_RUN`。 |
| F-04 `MemoryInMB > 4096` | **DEFERRED（显式）** | 我解析 r2/r3 XML 均为 `MemoryInMB=2048`；`proposal:64,121`、`plan:40,79` 保持 `UNKNOWN` 且禁止未经实测用于 Build config。 |
| F-05 资源阈值数值化 | **CLOSED（设计）** | `proposal:64,122`（AMD64/ARM64、BIOS virtualization、总 RAM ≥4 GiB、磁盘 ≥1 GiB、≥2 core、available ≥4096 MiB、C:/G: ≥1 GiB free，全部可测量、fail-closed）。 |
| F-06 dirty clone 停止条件 | **CLOSED（设计）** | `proposal:79`（`--untracked-files=all` porcelain 必须为空；任何状态项/未登记文件 → BLOCKED；保留现场、不清理、不换路径）。 |
| F-07 RO canary 写入真实输入 | **CLOSED（设计）** | `proposal:31,80`；`doc/tasks/P02.md:69` 明确禁止对 Python/模型/Node/Rust/VS/SDK 真实输入写入；XML canary 为 clone 内 `tmp/**` 子目录的 `ReadOnly=true` 独立 alias（我逐条核对 HostFolder/SandboxFolder 与 ReadOnly）。 |
| F-08 manifest 配方 + cache scan | **CLOSED（设计；schema 已冻结）** | `proposal:44,125`、`plan:40`（seed 前 credential/secret filename 与 token pattern 扫描，命中即 BLOCKED；`.npmrc`/日志/Cargo credentials 永不 seed）；缓存来源目录不映射（`proposal:48`）。 |
| F-09 r2 candidate hash 不可复算 | **CLOSED（本轮独立复算 8/8）** | `codex-checkpoint-p02-process-isolation-r2-candidate.md:29–36`：按 `git rev-parse 3555213a:<path>` + canonical LF SHA-256 复算 **8/8** 全匹配（43106、4531、2397、48115、8855、15020、16136、2269；无 BOM、无裸 CR）。 |
| F-10 raw JSONL 出库 | **CLOSED（留档边界成立）** | 外部文件实测：r2=`…/p02-process-isolation-plan/dsh-review-logs/dsh-review-process-isolation-r2.stdout.jsonl`，**431099 / `e59473d78b491a6bba66df69480ed8eb5fd032c6d2a73476e5e59f45ee2f1f1a` / `thinking`×37**；r3 同目录，**313007 / `8d16c4ec39da295bff9cc02d7b03cd02784414c58a2d9c8ce5c4b667b50c285e` / `thinking`×44**。candidate 树内 `git ls-tree -r` **无** `dsh-review-process-isolation-r{2,3}*.jsonl`（仅两条与本子任务无关的历史 jsonl）。r3 prompt/dispatch/response/exit/session/mount/stderr 均已版本化：response=**19419 / `6a121e0d6cd56efef4ed0bd70dde2e35fb83c9965c040edcc8bba0b05d82f94e`**、exit.txt=`0`、stderr=0 bytes、mount exit=0、session=`session-fea5e641-6352-45a4-b5db-01f4424e3c6b`，与 dispatch/checkpoint 声明一致。 |

**Cross-cutting 正例**：root `G:/CODEX/New Manga` 只读复核 = `main@549a6544f0be1eec66c09ece393fd1a409f10bf3`、203 status entries（4×`" M"` + 199×`"??"`、staged=0）；保护 manifest 逐项 `203/203` 匹配（path/status/kind/size/SHA-256 全等，missing/extra/mismatch=0），`entries` canonical = **36985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`**；r4 的 18 路径与 root dirty 交集=0。`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX`、产品源码/测试/依赖/Schema **均未出现在 diff**。

---

## 6. 精确 Gate 状态（不推导、不写 PASS）

| Gate | 状态 | 依据 |
|---|---|---|
| Windows Sandbox Feature（`Containers-DisposableClientVM`） | **UNKNOWN** | 无候选内查询证据；设计自述查询需提权（`proposal:78,93`）；本轮未查询、未提权 |
| Smoke admission | **NOT_ADMITTED** | `doc/tasks/P02.md:60`（需设计 Review 通过 + 条件闭合 + Codex 单独记录 admission + 完整 preflight）；`gate:58` 明示 r3 Review 不代表 admission |
| Isolation Smoke | **NOT_AUTHORIZED / NOT_RUN** | 未执行 `wsb start/connect/exec`；`proposal:76,85`、`plan:81`、`gate:58` |
| Build Gate | **BLOCKED** | `gate:1,9,59`、`proposal:93,129`、`plan:4`、`r4-start`、`scope-delta:57` |
| build | **NOT_AUTHORIZED / NOT_RUN** | 同上；无任何 build 命令与证据 |
| P02 AC1–AC7 | **AC1–AC7 全部 `NOT_RUN` / `BLOCKED`**（`doc/tasks/P02.md:39–45` 全部 `[ ]`，无任何验收证据） | gate/proposal 行文仅列 AC1–AC6（R3-06 既存文案差异，已登记延期至 closeout）；`AC7` 未被任何 r4 文件声称通过 |
| P02 Hard Build Barrier | **保持有效（active）** | `gate:59`、`proposal:129`、`plan:81`、`r4-start`、`scope-delta:57` |
| Design/Scheme Review（本报告） | **APPROVED（仅设计）** | 本文 §2–§3 |

---

## 7. 已执行 / 未执行命令、限制与下一项可安全 Gate

**已执行（全部只读；未写文件、未改 Git/index、未动 root 或其他 worktree、未提权）**
`git rev-parse HEAD/^{tree}/^`、`git log -1 --format`、`git rev-list --count`、`git status --porcelain=v1 --untracked-files=all`（审查前后均 0 项）、`git stash list`、`git worktree list`、`git diff --name-status/--raw/--numstat/--shortstat/--check`、`git cat-file blob <rev>:<path>`、`git ls-tree -r --name-only`、`git -C "G:/CODEX/New Manga" rev-parse/status`（只读 203 项）；`python -X utf8 -c` 内存内计算 canonical SHA-256/字节数、解析 r2/r3 XML 结构与 mapping 计数、比对四处 clone 命令序列、逐项复算 root manifest（203/203）与 r2 erratum（8/8）、stat+hash 两个 checkout 外 raw JSONL。未运行 `verify_plan.py`（r3/r4 记录已含其结果；非必需，避免无谓执行第三方脚本）。

**未执行 / 不可复算（限制）**
- 未查询或修改任何 Windows Feature，未运行 `wsb`、未启动/连接 Sandbox、未执行 Smoke，未 build，未运行 runner/Vitest/GUI/WebView——运行态一律 `UNKNOWN/NOT_RUN/BLOCKED`。
- host `git.exe/cl.exe/link.exe/rc.exe/mt.exe` 的版本/大小/SHA-256 **未复核**（未读 `C:\Program Files`、`E:`）；对 F-01/F-02 只确认“设计已登记、映射集合正确”，主机工具链事实为 `NOT_VERIFIED`。
- r3-start 的 14:34 快照值（4280/`1acbe671`）与 r3 delivery checkpoint 的 14:44:56 建立时间**无法由 Git 复算**（该 revision/时点未进入历史）；前者已被明确标注为时点快照，后者由 r3-review/r4-start 的同期引用间接佐证。
- `codex-process-isolation-r4-validation.md` 中 “Manifest schema self-check / Clone sequence” 两行无可复跑脚本或日志；其结论已由我对仓库文本的独立复现替代。
- DSH token usage、Desktop session 可见性、r3 Reviewer 自身 shell 限制：仅采信版本化证据，未重放。
- 本轮 PowerShell 运行在 ConstrainedLanguage（.NET 静态调用/`Measure-Object -Line` 失败），已改用 git plumbing + python 完成全部复算。

**下一项可安全 Gate（建议顺序）**
1. **本机非提权只读 preflight**（`proposal:78` 步骤 1）：root HEAD/branch/common-dir、`wsb` identity/version、`wsb list` 无 running session、固定 clone 路径不存在、架构/BIOS 虚拟化/RAM/可用内存/磁盘/CPU、全部 HostFolder 与 pinned inputs。`Containers-DisposableClientVM` 查询在非提权 shell 下失败时按设计得 `BLOCKED`，属**正确结果**而非缺陷。
2. 在 Smoke preflight 证据定稿前顺手闭合 **N-01/N-03**，在 Build config 冻结前闭合 **N-02**（均纯文档、不改 XML 与任何 canonical hash，无需重跑 exact-head config Review）。
3. **Smoke admission 必须由 Codex 单独记录**；在本报告之外，任何 `wsb start`/Sandbox/Smoke/Build/产品测试仍需独立 Gate，Hard Build Barrier 继续有效。

**推荐下一步（可直接转发 Codex）**
> 在 `codex/P02-process-isolation` 的既有 scope（`doc/tasks/P02.md` 的 `Codex-only scratch-build output boundary` 段 + `verification/P02/**`）内做一次纯文档收尾并固定新 commit：(1) `addendum:13` 的 “r2 Smoke config” 改为当前冻结的 r3 config，`plan:81` 补记 r3=`APPROVED_WITH_CONDITIONS` / r4 待审；(2) `scope-delta:52` 的文件级许可扩写为“erratum 及 R3-01 措辞一致性修正”；(3) `doc/tasks/P02.md:60` 的 “§ R3 extension” 统一为 “§ r3/r4 scope extension”。不改 r3 XML。随后按 `proposal:78` 步骤 1 在固定 head 下执行非提权只读 preflight，并由 Codex 单独记录 Smoke admission；在此之前保持 `Smoke=NOT_AUTHORIZED/NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED/NOT_RUN`、AC1–AC7=`BLOCKED`、Hard Build Barrier 有效。
