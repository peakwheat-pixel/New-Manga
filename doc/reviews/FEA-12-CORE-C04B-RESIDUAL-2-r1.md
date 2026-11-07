---
task: FEA-12-CORE-C04B-RESIDUAL-2
title: C-04b v1.2 + M2-C1 rev 2.15 UNFREEZE：独立 byte-level 复核（r1）
reviewer: fresh subagent
session: ad0bb17e-8271-40de-981b-78b3bd31bee4
reviewed_head: d91d9b6cc4afef307b0662055812c129468054a0
reviewed_worktree_sha256:
  C-04b: f5b4af88feab69946534a810dfa6704112ddfdbc8bcf8b0412b00334f131485b
  M2-C1: eaec765f5da54005c75af51c4f2f8926a7c34b63df585aa90b0b6224ac06bd59
verdict: changes_requested
p0: 0
p1: 2
p2: 1
p3: 4
date: 2026-11-08
---

# C-04b v1.2 + M2-C1 rev 2.15 UNFREEZE：独立 byte-level 复核（r1）

> 只读复核。我是 fresh subagent（session `ad0bb17e-8271-40de-981b-78b3bd31bee4`），未参与 C-04b v1.2 / M2-C1 rev 2.15 起草，未参与此前 C-04b/CORE 实现或 residual scope review。未修改生产代码、测试、契约、冻结记录、矩阵、载体或任务卡；未 `git add`/`commit`/`push`/`reset`/`checkout`。本报告是本次唯一写入仓库的文件；复现日志在仓外 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review\probe-log.txt`。

## 0. 结论先行

**verdict: changes_requested**——P0=0、**P1=2**、P2=1、P3=4。

字节、pin 账、零漂移与门禁本身**干净**：两个契约的 `Get-FileHash` 与 `git hash-object` 均与题面/冻结记录一致；`verify_pins.ps1` **18/18 PASS**；18 份映射中其余 **17 份 blob 与 HEAD 逐项相同**，仅 C-04b 变化；M2-C1 确认**不在** `verify_pins.ps1` 的映射内（0/18 机械 pin）；`src/**`、`apps/**`、`tests/**` 零 diff；`git diff --check` 干净；`check.ps1` 默认与 `-TaskPath` 均 PASS（3 warnings）。

但两处**阻断性语义/一致性问题**不能以当前字节冻结：

1. **P1-1（C-04b R-3 representative 文字错误）**：v1.2 把 `currentRevisionId` 的 representative 规则从旧文「首个 lineage-visible region current；无可见 region 取首个 artifact current」改为「取 `currentRegionRevisionIds` 的**字典序最小项**；无 region current 时取 `currentArtifactRevisionIds` 的字典序最小项」。现行实现 `src/bootstrap/core_service.py:1907-1930` 是**按阅读序取首个 lineage-visible region current**，仅当没有可见 region current 时才回退到已排序 artifact 列表的 `[0]`；region 数组本身虽按字典序排序，但 representative 并不读该排序。新文既改变了 representative 规则，又与实现不一致，与 v1.2「只改文字、不改规则」及载体「与现行实现一致」的自述矛盾。
2. **P1-2（M2-C1 R-1 同步不完整）**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:972`（旧 `:968`）的 §5.13 规范性正文仍写「artifact 谓词=`current_revision_id` 非空、不按可见性过滤」，**没有** `media_artifacts.book_id = 本书`；这与同节新 DTO 注释 `:958`、rev 2.15 banner/history、C-04b v1.2 §0/§2.1 及 scope review §3.3 明确要求修改的旧 `:968` 直接冲突。M2-C1 因此内部自相矛盾，冻结记录 §4A「R-1 契约谓词文字已修正」也只在 C-04b/DTD 侧成立。

记录口径总体诚实：§2 条件 7 **⏳ 待复核**、§4C 复核待派、载体 §6 待回填；没有「8 项 residual 全部关闭」或「R-1 已修复」的断言，且明确 R-1 **代码未修**、L-3 仍有效、代码归 `RESIDUAL-3`。这一点应保留。下面 P2/P3 均为非阻断收口项。

## 1. 基线与只读事实

- 仓库/分支/HEAD：`G:\CODEX\New Manga`，`main`，`d91d9b6cc4afef307b0662055812c129468054a0`；任务卡 `base_commit: d91d9b6cc` 与 HEAD 一致。
- 开始审查时 `git status --porcelain`（本审查未产生任何 tracked 改动）：
  - `M doc/REBASELINE_PLAN.md`、`M doc/STATUS.md`、`M doc/TASK_LEDGER.md`
  - `M doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
  - `M doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`
  - `M doc/plan/FEA-CONTRACT-FROZEN-C04b.md`
  - `M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`
  - `?? doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md`
  - `?? doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md`
  - `?? doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`
  - 另有本包的证据目录 `?? verification/FEA-12-CORE-C04B-RESIDUAL-2/**`（EV/logs/unfreeze.diff）。
- 只读核对手段：`Get-FileHash`、`git hash-object`、`git rev-parse HEAD:<path>`、`git diff`/`--numstat`/`--name-only`/`--check`、`Select-String`、`verify_pins.ps1`、`check.ps1`、逐行读取 `src/bootstrap/core_service.py`、`src/infrastructure/sqlite/library.py`、`tests/core/test_core_delete_commands.py`。
- 本报告的行号：除特别注明「旧」外，均指**当前工作树**行号；diff 表的 old/new 为 `git diff` 的 hunk 行号。

## 2. 逐项核对（题面 1–8）

### 2.1 最终字节与 pin：**PASS（MATCH）**

| 对象 | SHA-256（实测） | blob（实测） | 期望/登记 | 判定 |
|---|---|---|---|---|
| C-04b | `f5b4af88feab69946534a810dfa6704112ddfdbc8bcf8b0412b00334f131485b` | `d719ad9c05d7f36dbb22e4fb2269be3f27d601ff` | 题面同值；冻结记录 §1 `:15`/`:16` 同值 | MATCH |
| M2-C1 | `eaec765f5da54005c75af51c4f2f8926a7c34b63df585aa90b0b6224ac06bd59` | `faa1f100ff08bf9ef3bbf3537db268243dd4a3aa` | 题面同值；§1B `:31`、§4C `:111`、载体 §7 `:95` 同值 | MATCH |

- 冻结记录 §1 `:15` 的 C-04b pin 与 `Get-FileHash` 一致，`:16` 的 blob 与 `git hash-object` 一致；§1 只登记 C-04b，M2-C1 不在此处。
- 冻结记录 §1B `:31`、§4C `:111`、载体 §7 `:95` 三处 M2-C1 sha 均为 `eaec765f…`，无第二值。
- `git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = `6690606c26f67e99e9f61ac87d72ec33c4bd8589`；工作树 M2-C1 blob 为 `faa1f100…`，说明 M2-C1 确实改了字节（但不在机械 pin 映射内）。

### 2.2 pin 账：**PASS（18/18；其余 17 不变；M2-C1 不在映射）**

`pwsh -NoProfile -File tools/governance/verify_pins.ps1` 实测：

```text
OK C01b 3c9f5af7d74f   OK C02 bb365ca891a7   OK C03 b77e7968a00b
OK C04b f5b4af88feab   OK C05 f6e6f3cb1fe1   OK C06 75f8e2b4eb80
OK C07 3fdb44e49afe    OK C08 453f993c1a16   OK C09 dc51226b336c
OK C10 ec8fd862f95f    OK C11 44f4273f7ad1   OK C12 f49835860143
OK C13 8faf1e805eac    OK C14 05056cbf65f9   OK C15 f9e376a0ed4c
OK C16 67286eeca8cb    OK C17 aefa0fa5b17e   OK FEA01 0370c18932b1
PIN AUDIT: PASS (all 18)
```

- `verify_pins.ps1:6-13` 的 map 为 **18 项**（C01b/C02/C03/C04b/C05/C06/C07/C08/C09/C10/C11/C12/C13/C14/C15/C16/C17/FEA01），**无 M2-C1**；M2-C1 是 0/18 机械 pin，只能手工登记。
- 逐项 `git hash-object` vs `git rev-parse HEAD:<path>`：其余 **17 份全部 SAME**；C-04b 为预期 DIFF（工作树 `d719ad9c…` vs HEAD `201c8369…`）。17 份实测 blob 前缀：
  `C01b 7127d064 / C02 fcea994a / C03 81738c04 / C05 32d039c0 / C06 b537e76d / C07 cd51f8e6 / C08 b09291c1 / C09 9870d73a / C10 5cea9445 / C11 0f1e7b16 / C12 a5a17fd9 / C13 5a0cb284 / C14 111a2ce1 / C15 b0360cc9 / C16 3cd9d2fb / C17 f767e158 / FEA01 0f0c2d14`。
- 精确表述：18 份映射中**仅 C-04b 变化**；M2-C1 不在映射内但也变化（`6690606c…`→`faa1f100…`），靠记录 sha 防漂移。这与 scope review §3.3 的「C-04b 1/18 + M2-C1 0/18 机械 pin」口径一致。

### 2.3 C-04b diff：**11 处均在白名单内；但 ③ 的 representative 内容触发 P1-1**

`git diff --numstat -- doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` = **26 插入 / 15 删除**。`git diff -U0` 共 11 个 hunk，逐项对应题面 ①–⑪，**没有发现第 12 类字节变化**：

| # | hunk（old→new） | 内容 | 题面项 | 判定 |
|---|---|---|---|---|
| 1 | `:3-4` → `:3-4` | 状态行 v1.2、日期行补 v1.2 | ① | OK |
| 2 | `:14` → `:14-24` | `## 0. 修订摘要（v1.2 / v1.1）` + v1.2 摘要块 + v1.1 摘要降为 `###` | ② | OK |
| 3 | `:18` → `:28` | §0 第 1 条：R-1 谓词 + R-3 术语/representative | ③ | **P1-1**：谓词 OK；representative 文字错误 |
| 4 | `:21` → `:31` | §0 第 4 条：单条 manifest 批次取值 | ④ | OK |
| 5 | `:28-32` → `:38-42` | §1 表 5 行：M2-C1 行号 → 节名 | ⑤ | OK |
| 6 | `:44` → `:54` | §2.0 末段 R-2 | ⑥ | OK |
| 7 | `:53` → `:63` | §2.1 `DeletePreviewItem`：R-1 谓词 + representative 指针 | ⑦ | 谓词 OK；指针指向 P1-1 的错误规则 |
| 8 | `:64` → `:74` | §2.2 校验顺序：预览 `book_ids` → **请求** `book_ids` | ⑧ | OK（P3-2 措辞另记） |
| 9 | `:69` → `:79` | §2.2 首次确认：单条来源 `inventoryDigests[bookId]` | ⑨ | OK |
| 10 | `:71` → `:81` | §2.2 manifest：单条取值 + 单条 retry 只校验逐书 digest | ⑩ | OK |
| 11 | `:144` → `:155` | §6 变更记录 v1.2 | ⑪ | OK |

- 没有发现未授权的状态行/日期行以外的 header 变化、§2.3 码表变化、§3/§4/§5 条款变化；`git diff --check` 干净。
- **但 ③ 不是“纯文字等价改写”**：见 §4 P1-1，representative 规则从「首个 lineage-visible region current」变成「`currentRegionRevisionIds` 字典序最小项」，既改规则又与实现不一致。

### 2.4 M2-C1 diff：**9 处白名单变化均在；但 R-1 漏掉 §5.13 正文旧谓词（P1-2）**

`git diff --numstat -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = **11 插入 / 7 删除**。`git diff -U0` 共 7 个 hunk，覆盖题面 ①–⑨：

| # | hunk（old→new） | 内容 | 题面项 | 判定 |
|---|---|---|---|---|
| 1 | `:17` → `:18-19` | rev 2.15 banner（2.14 原文保留） | ① | OK（representative 措辞见 P1-1） |
| 2 | `:29` → `:32-33` | Revision history 增 2.15 | ② | OK（representative 措辞见 P1-1） |
| 3 | `:791` → `:795` | §5.11.1a 标题 rev 2.14→2.14/2.15 | ③ | OK |
| 4 | `:814` → `:818` | 来源行补单条 `inventoryDigests[bookId]` | ⑤ | OK |
| 5 | `:815` → `:819` | 校验顺序「预览」→「请求」 | ⑥ | OK |
| 6 | `:819` → `:823` | retry 行标注集合级规则仅批量 | ⑦ | OK |
| 7 | `:922` → `:926` | §5.13 标题 C-04b v1.1→v1.2 + rev 2.14/2.15 | ④ | OK |
| 8 | `:953` → `:957` | DTO `currentRegionRevisionIds` 删 `separate/detached` | ⑧ | OK |
| 9 | `:954` → `:958` | DTO `currentArtifactRevisionIds` 补 `media_artifacts.book_id` + representative | ⑨ | 谓词 OK；representative 见 P1-1 |

- **没有**新增/删除命令、字段、错误码、capability；**没有** `PROTOCOL_MINOR` 数值变化（仍为 3）；**没有** wire minor 变化（§5.13 仍 11、§5.14 仍 13）；**没有**发现 §5.11 家族的拒绝条件/校验顺序/失败分类被改写成新规则——单条 retry「不校验集合级值」是对既有形状分支的明确化，不是新规则。
- **但**旧 `:968`（新 `:972`）的 §5.13 正文仍保留旧 artifact 谓词，构成 P1-2；该行不在本包的 9 处白名单内，却正是 scope review §2.1/§3.3 明确要求修改的旧 `:968`。

### 2.5 记录一致性：**主体一致；P2-1 的“已修正/与实现一致”表述过宽**

| 载体/字段 | 实测 | 一致性 |
|---|---|---|
| 冻结记录 §1 `:15`/`:16` | C-04b `f5b4af88…` / blob `d719ad9c…` | 与两实测一致 |
| §1B `:31` | C-04b v1.2 `f5b4af88…`（blob `d719ad9c…`）；M2-C1 `eaec765f…`（blob `faa1f100…`，0/18 手工登记）；复核 ⏳ | 与 §1/§4C/载体一致；复核状态如实待定 |
| §2 条件 7 `:68` | v1.2 复核 **⏳ 待复核**；`verify_pins` 18/18；其余 17 不变；M2-C1 不在映射；无新命令/字段/错误码/能力/`PROTOCOL_MINOR` | 与题面/实测一致 |
| §4C `:103-113` | 载体、触发/授权、修订内容、复核待派、两契约 sha、历史 pin、17 pins | 与 §1B/载体一致 |
| §4A `:117-136` | append-only 状态更新：R-1/R-2/R-3/R-4/R-5/R-8 契约文字已改；R-1 代码未改 → L-3 仍有效；R-1 代码归 `RESIDUAL-3`；R-6 已闭合；R-7 由 banner/history 落地；上表历史读法不改写 | 方向正确，但“R-1 契约谓词文字已修正”“R-3 已修正”在 M2-C1 `:972`/representative 两处**过宽**（P2-1） |
| §5 `:150` | v1.2 变更记录、pin 变化、复核后重冻、载体 | 与 §1/§4C 一致 |
| 矩阵 `:3` / 第 4 行 `:22` | 状态行补 C-04b v1.2；第 4 行 `FROZEN v1.2`，条件 ① 复核 **⏳ 待派**，⑤ M2-C1 rev 2.15 已同步，⑥ 18/18；R-1 代码归 `RESIDUAL-3` | 与冻结记录一致；`FROZEN` 与 `⏳` 并存是“待复核重冻”的时态张力，记录条件 7/§4C 已明确待复核，**非阻断**（不另计 finding，建议复核回填时统一措辞） |
| 载体 §2 `:29-51` | C-04b 6 处 + M2-C1 9 处 + 记录/矩阵；`:62-64` 零语义变更、R-1 代码未改、L-3 仍有效 | 与记录一致；但 `:63` “改动仅让文字与现行实现一致”被 P1-1 推翻（P2-1） |

- **明确存在**：「R-1 契约文字已改但代码未修、L-3 仍有效、R-1 代码归 `RESIDUAL-3`」——见 §4A `:122-125`、§4C、任务卡 `:52`。
- **不存在**「8 项全部关闭」「R-1 已修复」这类断言；载体 §7.3、EV §6 均明确只改契约文字、R-1 代码未修。
- 但 §4A 的「R-1 的**契约谓词文字**已修正」和载体的「与现行实现一致」在当前字节下不完整：M2-C1 `:972` 仍旧谓词，representative 也与实现不符。该表述应与 P1 修复一起收窄。

### 2.6 零漂移：**PASS**

- `git diff --name-only`（7 个 tracked 修改）：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`、两个契约、冻结记录、矩阵。均为题面允许的 UNFREEZE 包（+ Lead 指针）。
- `git diff --name-only -- src apps tests`：**空**。
- `git diff --name-only -- doc/contracts doc/plan`：仅 `M2-C1_TYPED_IPC_CONTRACT.md`、`FEA-C04b_DELETE_PROTOCOL_DRAFT.md`、`FEA-CONTRACT-FROZEN-C04b.md`、`FEA-CONTRACT_FREEZE_MATRIX.md`；无 C-17/C-06/C-15/C-16/C-07 等其它契约。
- untracked 仅载体、两张新卡（RESIDUAL-2/3）、本包证据目录；均为本包/允许范围。
- `git diff --check`：exit 0（无 whitespace error）；仅 Git 的 LF→CRLF warning（`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`），非本包内容问题。

### 2.7 语义正确性抽查

| 项 | 结论 | 证据/说明 |
|---|---|---|
| R-2「不得在同一请求内混用两种 digest 语义」 | **PASS** | C-04b `:54` 与 §2.0 表 `:51-52`、§2.2 `:74/:79/:81` 一致：单条=逐书值；批量=集合级 + 逐书 map；两者都校验 |
| R-5「请求 `book_ids`」与「预览不缓存」 | **PASS（措辞 P3-2）** | §2.1 `:65` 明写「只读、零副作用、不缓存」；`:74` 把比对对象改为请求侧并说明 digest 绑定保证与预览一致。逻辑自洽，但「键集合与顺序必须与请求 `book_ids` 完全一致」字面上有“自己对自己”的循环感，见 P3-2 |
| R-8 单条 manifest 取值 vs 实现 | **PASS** | C-04b `:31`/`:81`：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry 只校验逐书 `inventory_digest`。`src/bootstrap/core_service.py:2450-2454` 正是 `uuid.uuid4().hex`、`[book_id]`、`collection_inventory_digest([book_id], {book_id: expected_digest})`；`tests/core/test_core_delete_commands.py:1341-1344` 钉住后两者 |
| R-1 谓词文字 vs 删除面 | **C-04b PASS；M2-C1 FAIL（P1-2）** | C-04b `:28`/`:63` 写 `media_artifacts.book_id = 本书` 且 `current_revision_id` 非空；删除面 `src/infrastructure/sqlite/library.py:1920-1926` 为 `DELETE FROM media_artifacts WHERE book_id = ?`（artifact_revisions 用同书子查询）。只核文字，不要求代码已改；代码 `:1178-1190` 仍 page/chapter join，属 L-3/RESIDUAL-3。M2-C1 `:972` 仍只写 `current_revision_id` 非空，与 C-04b/同节 DTO 冲突 |
| R-3 representative vs 实现 | **FAIL（P1-1）** | 新文 `currentRegionRevisionIds` 字典序最小项 vs `core_service.py:1907-1930` 阅读序首个 lineage-visible；fallback 条件也不同（`无 region current` vs `无可见 region current`）。详见 §4 |
| R-4 §1 表行号→节名 | **PASS** | 5 行全部改为 `§5.11.1`/`§5.11.2`/`§5.11.3`/`§5.11.5`，无残留 `:685`/`:733`/`:748`/`:745-760`/`:776-802` |
| R-7 banner/history 批量限定 | **PASS** | M2-C1 `:18`/`:32` 均写「retry 集合级规则明确**仅批量**；单条 retry 只校验 manifest 逐书 digest」 |
| R-6 报告 sha | **已闭合（非本包新增）** | 冻结记录 §1C `:37-56` 已有 r1–r7 完整 sha；本包未回退该表 |

### 2.8 实跑表与门禁：**PASS**

| 检查 | 命令 | 实测 | 判定 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；exit 0 | PASS |
| check 默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；exit 0；warnings=11 个非终态 Task / STATUS 80% / PLAN 80% | PASS |
| check taskpath | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | 同上（默认也解析到该 Task） | PASS |
| whitespace | `git diff --check` | 无输出；exit 0 | PASS |
| 代码漂移 | `git diff --name-only -- src apps tests` | 空 | PASS |

- **未跑**：全量 pytest、全量 .NET、GUI/e2e、真实回收站 D 流程。本卡是纯文档 UNFREEZE（`src/apps/tests` 零 diff），这些不在本卡门禁内；本报告不据此宣称运行时通过。
- 本报告不把既有 `verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/` 里的日志当作我自己的实跑；上面的数字均来自本次命令输出（同时写入仓外 probe-log）。

## 3. Diff 表（精确）

### 3.1 C-04b（`git diff --numstat` = 26/15）

| hunk | old→new | 变化 | 白名单 |
|---|---|---|---|
| 1 | `:3-4` → `:3-4` | 状态行/日期行 v1.2 | ① |
| 2 | `:14` → `:14-24` | §0 标题改「修订摘要（v1.2 / v1.1）」；新增 v1.2 摘要块；v1.1 摘要降 `###` | ② |
| 3 | `:18` → `:28` | R-1 谓词 + R-3 术语/representative | ③（representative **P1-1**） |
| 4 | `:21` → `:31` | R-8 单条 manifest | ④ |
| 5 | `:28-32` → `:38-42` | §1 表 5 行，行号→节名 | ⑤ |
| 6 | `:44` → `:54` | R-2 §2.0 末段 | ⑥ |
| 7 | `:53` → `:63` | R-1/R-3 §2.1 DTO | ⑦（指向 **P1-1**） |
| 8 | `:64` → `:74` | R-5 请求 `book_ids` | ⑧ |
| 9 | `:69` → `:79` | R-5 单条来源 | ⑨ |
| 10 | `:71` → `:81` | R-8 单条 manifest | ⑩ |
| 11 | `:144` → `:155` | §6 变更记录 v1.2 | ⑪ |

- 合计 26 插入/15 删除；**无第 12 个 hunk**。
- 唯一“白名单内但内容错误”的是 ③/⑦ 的 representative 文字（P1-1）；R-1 谓词本身正确。

### 3.2 M2-C1（`git diff --numstat` = 11/7）

| hunk | old→new | 变化 | 白名单 |
|---|---|---|---|
| 1 | `:17` → `:18-19` | rev 2.15 banner | ① |
| 2 | `:29` → `:32-33` | history 2.15 | ② |
| 3 | `:791` → `:795` | §5.11.1a 标题 2.14/2.15 | ③ |
| 4 | `:814` → `:818` | 来源行单条 `inventoryDigests[bookId]` | ⑤ |
| 5 | `:815` → `:819` | 校验顺序「预览」→「请求」 | ⑥ |
| 6 | `:819` → `:823` | retry 仅批量标注 | ⑦ |
| 7 | `:922` → `:926` | §5.13 标题 v1.2 + rev 2.14/2.15 | ④ |
| 8 | `:953` → `:957` | 删 `separate/detached` | ⑧ |
| 9 | `:954` → `:958` | 补 `media_artifacts.book_id` + representative | ⑨ |

- 合计 11 插入/7 删除；**无第 10 个 hunk**。
- **漏项**：旧 `:968`（新 `:972`）§5.13 正文旧谓词未改——P1-2。
- 无新命令/字段/错误码/capability/`PROTOCOL_MINOR`/wire minor 变化；§5.11 家族规则未发现新语义。

## 4. Findings

### P1-1（阻断）C-04b R-3 representative 新文与实现/旧文不一致，属于规则变化

**位置**：`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:28`（§0 第 1 条）、`:19`（v1.2 摘要）、`:63`（§2.1 DTO 指针）。M2-C1 `:18`/`:32`/`:958` 的 representative 措辞同源，需一起澄清。

**before（HEAD `:18`）**：
> `currentRevisionId` 保留为代表展示值（首个 lineage-visible region current；无可见 region 取首个 artifact current；均无 null），**不承担绑定职责**。

**after（工作树 `:28`）**：
> `currentRevisionId` 保留为代表展示值（取 `currentRegionRevisionIds` 的**字典序最小项**；无 region current 时取 `currentArtifactRevisionIds` 的字典序最小项；均无 null），**仅展示、不承担绑定、不进 digest**。

**实现事实**：
- `src/bootstrap/core_service.py:1901-1906` 先把 `current_region_revision_ids`/`current_artifact_revision_ids` 排序去重（供 DTO/digest 用）。
- `:1907-1930` 的 representative **不读排序后的 region 数组**：它按 `raw["region_current_pointers"]` 的顺序（`src/infrastructure/sqlite/library.py:1158-1175` 的 `ORDER BY c.sort_order, c.import_order, c.chapter_id, p.sort_order, p.page_id, r.reading_order, r.region_id`，即阅读序）遍历，跳过 `guard.is_region_readable(...)` 不可见的 pointer，取**第一个可见** region current；仅当没有任何可见 region current 时，才回退到 `current_artifact_revision_ids[0]`（该列表已排序，故等价于 artifact 字典序最小）。
- `library.py:1158-1165` 的 docstring 明确写：“The caller picks the first *lineage-visible* pointer for the PD-01 `currentRevisionId` disclosure (Lead ruling: the disclosure must follow the released FEA-11 read semantics, so the visible filter lives in the application/guard layer, not here).”
- scope review §2.3 `:95-100` 只确认了 **artifact 回退**取“字典序最小项”，并给出“无可见 region 时取 `currentArtifactRevisionIds` 的字典序最小项”的现行规则；它没有授权把 **region 分支**也改成字典序最小。本包把 region 分支一并改成 `currentRegionRevisionIds` 字典序最小，超出了该 scope review 的结论。

**为什么是 P1**：
1. **规则被改**：旧文「首个 lineage-visible region current」与实现一致；新文改成「`currentRegionRevisionIds` 字典序最小项」，会选中**隐藏 region** 或**阅读序不是第一**的 region current。这个字段虽然“仅展示、不进 digest”，但它是 DTO 的展示规则，属于语义变化，不是措辞。
2. **与自述矛盾**：C-04b `:16` 自述“不改任何规则/语义”，载体 §3 `:63` 自述“改动仅让文字与现行实现一致”；两者都不成立。
3. **fallback 条件也错**：新文“无 region current 时”才会回退 artifact；实现是“无**可见** region current 时”就回退。若存在 hidden region current 但没有可见 region current，新文会选 hidden region，实现会选 artifact。
4. **M2-C1 同步不完整**：`:18`/`:32`/`:958` 也写“representative 取字典序最小项”，同样没有写清“region=阅读序首个 lineage-visible；artifact=字典序最小”两分支。

**建议修复（二选一）**：
- **A（推荐，纯文字回到实现）**：把 representative 写回“按阅读序取**首个 lineage-visible** region current；无可见 region current 时取 `currentArtifactRevisionIds` 的字典序最小项；均无 null；仅展示、不承担绑定、不进 digest”。这样既写死了排序，又不改规则。同步 M2-C1 `:18`/`:32`/`:958` 的措辞。
- **B（若确实要改规则）**：把“region representative = `currentRegionRevisionIds` 字典序最小”作为**规则变更**登记，另立代码卡改 `core_service.py:1907-1930` + 测试；不能把它写成“仅措辞”，也不能塞在本卡“与现行实现一致”的叙述里。当前 `RESIDUAL-3` 只覆盖 artifact 成员谓词，不含 representative 代码，故选 B 需要扩卡或另卡。

### P1-2（阻断）M2-C1 §5.13 正文旧 artifact 谓词未同步，R-1 在 M2-C1 侧不完整

**位置**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:972`（旧 `:968`），属于 §5.13 `PreviewPermanentDeleteBooks` 的“PD-01 三项强制 / rev 2.14 追加”段。

**当前字节（工作树 `:972` 末尾）**：
> artifact 谓词=`current_revision_id` 非空、不按可见性过滤；受保护 artifact 表达=数组长度。

**同节新字节（`:958`）**：
> 本书全部 artifact 的 current（成员谓词=`media_artifacts.book_id = 本书` 且 `current_revision_id` 非空，不过滤可见性）

**冲突链**：
- C-04b v1.2 `:28`/`:63` 已写 `media_artifacts.book_id = 本书`；
- M2-C1 `:18` banner、`:32` history、`:958` DTO 注释均写 `media_artifacts.book_id = 本书`；
- 但 `:972` 仍写旧谓词，导致同一节内 DTO 注释与正文互相矛盾；
- scope review §2.1 明确把旧 `:968` 与旧 `:954` 称为同义句；§3.3 明确要求 `:953`/`:954`/`:968` 补 artifact 成员谓词。本包的载体 §2B、任务卡 AC-2、EV §2 只列 `:953`/`:954`，漏了 `:968`，所以 diff 干净但**同步不完整**。

**为什么是 P1**：
1. 这是**规范性正文**，不是历史注释；未来读者按 `:972` 实现会得到旧谓词，与 v1.2 目标谓词相反。
2. 冻结记录 §4A `:122-125` 说“R-1 的契约谓词文字已修正”，但 M2-C1 正文未修正，记录不完整。
3. 18 pin 机械检查发现不了 M2-C1 漂移（0/18），所以必须靠本次 byte-level 复核抓出；这正是本卡要防的风险。

**建议修复**：
- 在 `:972` 补 `media_artifacts.book_id = 本书`（与 `:958` 完全一致），并把任务卡 AC-2、载体 §2B、EV §2 的 M2-C1 清单从 9 处补为 10 处（或明确说明该句的修改位置）。
- 或者，如果确实要把 `:972` 留作 rev 2.14 历史文本，必须在该句前加“以下为 rev 2.14 历史表述，现行以 `:958` 为准”并同步记录；不能让它以现行规范句的形式与 `:958` 并存。
- 修复后 M2-C1 sha 会变（当前 `eaec765f…`），需重新登记 §1B/§4C/载体 §7 三处并重跑 pins/check；本报告不把当前 sha 视为最终。

### P2-1（非阻断，但需随 P1 一起收口）记录/载体/EV 的“已修正 / 与现行实现一致”过宽

**位置**：
- 冻结记录 §4A `:122-125`：“R-2 / R-3 / R-4 / R-5 / R-8 的**契约文字**已由 C-04b v1.2 修正……**R-1** 的**契约谓词文字**已修正（`media_artifacts.book_id = 本书`）……”
- 载体 §3 `:63`：“改动仅让文字与**现行实现**（`core_service.py:1904-1930`、`:2450-2454`；`library.py:1178-1190` 待 RESIDUAL-3）一致。”
- EV §2 `:31-34` 的 M2-C1 清单只到 `:954`。

**问题**：在 P1-1/P1-2 未修前，“R-3 已修正”“R-1 契约谓词文字已修正”“与现行实现一致”都不完整。记录**正确地**写了 R-1 代码未修、L-3 仍有效、RESIDUAL-3，也**没有**写“R-1 已修复/8 项全关”；这里只需要把“已修正”收窄为“C-04b + M2-C1 DTO 已改；M2-C1 §5.13 正文旧谓词待补；representative 规则待回到实现”，或在 P1 修复后改写为准确表述。

**建议**：P1 修复后更新 §4A、载体 §3、EV §2，并在 §4C/矩阵条件 ① 回填复核结果时使用“批准的最终字节”而不是当前待修字节。

### P3-1（非阻断）版本引用/标签残留

- M2-C1 `:936`、`:940`、`:974` 仍写“C-04b v1.1 §2.1”，而 `:926` 标题已是 C-04b v1.2；`:797` 仍写“本节现行规则以 rev 2.14（形状分支/retry/manifest）为准”，而标题已是 rev 2.14/2.15。
- C-04b `:63` 的 `currentRegionRevisionIds[]（v1.1：……）` 标签仍是 v1.1，但该行文字在 v1.2 已改（删 `separate/detached`）；同行的 artifact 数组已标 v1.2。
- 这些不改变规则，但会让读者误判版本；建议在本次 UNFREEZE 中改成 v1.2/2.15，或明确标注“v1.1 历史引用”。scope review §3.3 也要求同步“所有 rev 引用”。

### P3-2（非阻断）C-04b `:74` / M2-C1 `:819` 的“与请求 book_ids 完全一致”字面循环

- 当前写“首次确认键集合与顺序必须与**请求** `book_ids` 完全一致……且值=当前重算集合值”。请求的 `book_ids` 与它自己比较在字面上是循环；实际校验是 `inventory_digests` 的 key 恰好覆盖请求 `book_ids`（后文已写）以及 digest 重算。
- 旧文“与预览 book_ids 完全一致”确实因“预览不缓存”而不可执行，R-5 的方向正确；建议把该句改成“首次确认的 `inventory_digests` key 集合与顺序必须恰好覆盖请求 `book_ids`，且集合 digest=按请求顺序重算值”，避免循环读法。非阻断，不影响当前 fail-closed 语义。

### P3-3（非阻断）EV 引用的 `logs/code-drift.log` 不存在

- `verification/FEA-12-CORE-C04B-RESIDUAL-2/EV.md:44` 的零漂移表把 `src/**`/`apps/**`/`tests/**` 的证据指向 `logs/code-drift.log`，但该目录下没有这个文件（只有 check/check-taskpath/diffstat/other-contracts-drift/pins/scope-changed/sha-check 七个日志）。
- 本次独立实跑 `git diff --name-only -- src apps tests` 为空，结论仍成立；但 EV 的引用应补上实际日志（或把命令输出写进现有日志），否则证据链有一处断引。

### P3-4（非阻断）RESIDUAL-3 卡过早写“已由 RESIDUAL-2 解决”

- `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md:33` 的 `out_of_scope` 写“其它 residual（R-2/R-3/R-4/R-5/R-8 **已由 RESIDUAL-2 解决**）”。RESIDUAL-2 当前是 `ready`、复核 `changes_requested`，尚未 approved；该表述应改为“拟由 RESIDUAL-2 解决 / 待其 approved”，或在 RESIDUAL-2 关闭后再改。
- 这不影响 RESIDUAL-3 的 R-1 代码范围本身；只是不要在 RESIDUAL-2 未通过时替它宣称完成。

## 5. 结论

**changes_requested**。在以下两项修复并重跑门禁/重签记录前，不应把当前字节作为 v1.2/rev 2.15 的最终冻结字节：

1. **P1-1**：C-04b §0 第 1 条的 representative 规则改回与 `core_service.py:1907-1930` 一致的“阅读序首个 lineage-visible region current；无可见 region current 时取 artifact 字典序最小项”，或把“region 字典序最小”作为显式规则变更并另立代码卡；同步 M2-C1 banner/history/DTO 措辞。
2. **P1-2**：M2-C1 `:972` 补 `media_artifacts.book_id = 本书`，或明确标为 rev 2.14 历史并声明以 `:958` 为准；同步任务卡 AC-2/载体 §2B/EV §2 的 M2-C1 清单。
3. **P2-1**：P1 修复后收窄 §4A/载体 §3/EV 的“已修正/与实现一致”表述；保持“R-1 代码未修、L-3 仍有效、代码归 RESIDUAL-3”的既有正确口径。
4. **P3**：可同批清理版本引用、循环措辞、缺失日志和 RESIDUAL-3 的“已解决”措辞。

修复后需重新计算两契约 sha（C-04b 与 M2-C1 都会变）、更新冻结记录 §1/§1B/§4C/§5 与载体 §7、重跑 `verify_pins.ps1`（18/18；其余 17 不变）与 `check.ps1`，再由独立上下文复核新字节。**当前本报告不批准任何字节**；P0=0 只表示未发现数据丢失/保护失效级缺陷，P1=2 已足以阻断冻结。

## 6. 真实性声明

- **身份与独立性**：我是本次委派的 fresh subagent，session `ad0bb17e-8271-40de-981b-78b3bd31bee4`；未参与 C-04b v1.2 / M2-C1 rev 2.15 的起草、实施、返修，也未参与此前 C-04b/CORE 实现或 residual scope review。`reviewed_head=d91d9b6cc4afef307b0662055812c129468054a0`，只读该工作树。
- **写入范围**：本报告 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r1.md` 是本次唯一写入仓库的文件（untracked）；仓外只写 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review\probe-log.txt`。未修改任何 tracked 文件、契约、记录、矩阵、载体、任务卡、源码或测试；未 `git add`/`commit`/`push`/`reset`/`checkout`/`stash`。
- **字节未变**：审查前后 `git diff --name-only` 的 7 个 tracked 文件集合相同；两契约末尾复算仍为 C-04b `f5b4af88…`、M2-C1 `eaec765f…`；新增的只有本报告（以及本包既有 untracked 证据目录）。
- **实测与未跑**：§2/§3 的数字均来自本次命令；§2.8 明确列出未跑的 pytest/.NET/GUI/e2e。未把既有 `verification/` 日志当作本次实跑；未把 `verify_pins` 18/18 当作语义正确性的替代。
- **不夸大**：本报告没有说“8 项 residual 全部关闭”“R-1 已修复”“C-04b/M2-C1 已最终冻结”；只确认字节/pin/门禁的机械事实，并对 P1-1/P1-2 明确要求修改。`verify_pins` 只证明 pin 行与当前文件自洽，不覆盖 M2-C1（0/18），也不替代本报告对 representative/谓词的语义复核。
- **限制**：本报告未逐行重读 C-04b/M2-C1 全文的每一句历史注释，只对本次 diff、§5.13/§5.11.1a 相关段、R-1/R-2/R-3/R-5/R-8 语义点及实现/测试事实做逐项核对；对未涉及本次 diff 的条款按“零 diff”采信，不再逐条重审。
