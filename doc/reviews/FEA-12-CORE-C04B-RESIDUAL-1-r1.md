---
task: FEA-12-CORE-C04B-RESIDUAL-1
title: FEA-12-CORE-C04B-RESIDUAL-1 r1：C-04b v1.1 residual 8 项 docs-only 记录收口独立审查
reviewer: fresh subagent（独立上下文；未参与本卡起草、C-04b/CORE 实现或此前 scope review）
reviewer_kind: subagent
session: c66cd50f-35fc-4564-afbc-2f90cf266e48
parent_session: session-3ac1953a-094e-4339-889a-284df2b7b34d
base_commit: 28a2826af
reviewed_head: 28a2826af
date: 2026-11-07
verdict: approved
p0: 0
p1: 0
p2: 0
p3: 6
p3_total: 8
p3_fixed: 1
p3_mitigated: 1
post_review_commit: 698ac9524
---

# FEA-12-CORE-C04B-RESIDUAL-1 r1：docs-only 记录收口独立审查

> 审查对象：`G:\CODEX\New Manga`（`main`，HEAD `28a2826afdba0fbd3262d109dcd3afa86997afb6`）工作树中**未提交**的 docs 收口最终字节：任务卡 `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md`、冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`（§5F 追加）、Lead 指针 `doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`，以及证据 `verification/FEA-12-CORE-C04B-RESIDUAL-1/`。
> 权威依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（scope review；8 项逐项事实 §2、建议卡面 §4）；任务卡 AC-1…AC-6。
> 本报告只读审查；除本文件外未写入仓库任何字节；未 `git add`/`commit`/`push`/`reset`/`checkout`。

## 0. 结论先行

1. **verdict: `approved`**（P0=0、P1=0、P2=0、**P3=6 open**；8 项总计：P3-1 已在 Lead 提交 `698ac9524` 修复、P3-7 已由该 docs-only 提交缓解、P3-2…P3-6 + P3-8 仍 open）。P3 均为证据/路径/措辞精度、closeout 记录或审查期间并行工作树注记，**不阻断**本 docs-only 卡的实质结论。
2. **AC-1…AC-6 全部在实质上 MET**：8 项 residual 表与 scope review §2 逐项一致；行号在 `28a2826af` 工作树逐点命中；§1C 的 r1–r7 + 辅助报告 **sha256 与大小全部实测 MATCH**；载体 §5F **只追加**（`+14/−0`，HEAD 112 行为当前文件前缀）；C-04b/M2-C1 **契约字节零 diff**；`verify_pins.ps1` **18/18**、`check.ps1`（默认 + `-TaskPath`）**PASS**；**本卡产物**对 `src/**`/`apps/**`/`tests/**` 零 diff（审查开始时整树亦为零；审查期间并行 L-R11 实现新增 3 个 `src/**` 修改，见 P3-7，非本卡/非本审查）；未出现肯定性的「8 项全部关闭/契约已修复」断言。
3. **⑥/R-6 确实闭合**：§1C 给出 r1–r7 完整 sha256（r4–r7 与 §1B 的 8 位前缀一致），r2 子会话 id 未暴露已如实说明；§1B 原文（第 21–32 行）逐行未改，闭合落在新增 §1C。
4. **未修复的事实保留**：R-1/R-2/R-3/R-4/R-5/R-7/R-8 的规范修复均未做（契约正文仍为 `acc8f0e0…`/`701093b5…`），R-1 的代码偏差登记为 L-3「未修」，修复需另卡 UNFREEZE + 实现卡；本报告不声称任何 residual 已修复。
5. **P3 摘要**：P3-1（EV diff stat `+41/−2`）已在 `698ac9524` 的 EV 中修为 `+39/−2`，**fixed**；P3-2（§1C 路径非字面绝对、r4–r7 用 `...` 缩写）、P3-3（r4–r7 session 只记前缀）、P3-4（卡面 AC-2 写 §1B、落地在 §1C）、P3-5（§4B 相邻修正未在卡面显式标注）、P3-6（EV §2 AC-6 的 closeout 前瞻表述）仍 **open**；P3-7（并行 L-R11 的 3 个 src 修改）已由 `698ac9524` 的 docs-only 提交**缓解**；P3-8 的原始事实（`698ac9524` 内任务卡仍 `ready`、EV r1 仍「结论待回填」、committed 报告为中间版本）已由 `63b95abda`/`423efa200`/`3c4f62dbf` 修正，但最终 EV/卡面称 **P3-8 已由 closeout 闭合**且仍计 **open=6**，与「8 = 1 fixed + 1 mitigated + 6 open」的算术不一致；若 P3-8 确已闭合，open 应为 5。该计数口径仍 **open**（详见 §3.5/§4）。

## 1. 基线与只读事实

- 仓库/分支：`G:\CODEX\New Manga`、`main`。审查基线 `28a2826afdba0fbd3262d109dcd3afa86997afb6`（已 push；`base_commit` 与审查基线相同）；审查后 Lead 于 2026-11-07 23:57:55 提交 `698ac9524e7d86dbbc46d0063eec44c6f99e8cab`（docs-only 集成），随后 `63b95abda`（closeout done）、`423efa200`（EV r1 回填 + 本报告修正版入库）、`3c4f62dbf`（卡面 Canonical Evidence EV-01 指向 EV 最终版 `423efa200`）。此后 Lead 又提交 `a969f405f`（handoff §20）与 `a4cc8a9b7`（SCAN-RH 冻结）；当前 HEAD `a4cc8a9b7`，这些后续提交不改变 C-04b docs 字节。
- 审查开始时 `git status --porcelain=v1`：
  - ` M doc/REBASELINE_PLAN.md`
  - ` M doc/TASK_LEDGER.md`
  - ` M doc/plan/FEA-CONTRACT-FROZEN-C04b.md`
  - ` M doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`
  - `?? doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md`
  - `?? verification/FEA-12-CORE-C04B-RESIDUAL-1/`
- **审查期间并行变化（非本审查产生）**：约 23:51–23:52，工作树新增 3 个 `src/**` 修改：`src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py`（内容为 FEA-11/L-R11 publication gate 实现，`172 insertions(+) / 63 deletions(-)`）。它们不是本卡 allowed_paths 的产物，也不是本审查写入；我未触碰、未回滚它们。因此 23:37 的「零 code diff」是当时的真实状态，**提交前整树 `git diff` 已不再是零 `src/**`**；本报告的零代码结论只对**本卡产物**成立（见 AC-6 与 P3-7）。
- 提交前（约 23:56）`git status --porcelain=v1`：4 个 docs `M` + 3 个 `src` `M` + `?? doc/tasks/...` + `?? verification/...` + 本报告 `?? doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`。
- **审查后 Lead 提交链**：`698ac9524`（23:57:55；docs-only 集成：4 docs + 本报告当时版本 + 任务卡 `ready` + evidence，未含 src）→ `63b95abda`（closeout done：任务卡 `done`/`integration_commit=698ac9524`/`complete`；STATUS/PLAN/LEDGER 更新）→ `423efa200`（EV r1 回填 + 本报告修正版入库；并入库并行 SCAN-RH scope review r1）→ `3c4f62dbf`（卡面 Canonical Evidence EV-01 指向 EV 最终版 `423efa200`；P3 口径 `open=6/fixed=1/mitigated=1`；称 P3-8 由 closeout 闭合）。当前工作树：本报告再次修正（P3-8 计数口径注记，`M`）、3 个并行 `src/**` `M`、并行 `doc/reviews/FEA-11-SCAN-RH-scope-r1.md` `M`；任务卡/EV/冻结记录/载体均在 HEAD、无 diff。`git diff` 对冻结记录/载体为零；C-04b/M2-C1 sha 不变。
- 被审对象是审查时工作树最终字节（`28a2826af` 基线）；`698ac9524` 中的 docs 字节与之一致；C-04b/M2-C1 两个契约文件零 diff，`git diff --quiet HEAD -- <两契约>` 退出 0。
- 卡面在审查开始时 `status: ready`、`base_commit: 28a2826af`、`owner: dsh`、`reviewer` 指向本报告路径；AC-1…AC-6 在审查时仍为 `<<PENDING>>`。审查后 Lead 在工作树把卡面改为 `done`/`integration_commit=698ac9524`/`complete`（未提交）；committed 卡面仍是 `ready`（P3-8）。
- `doc/REBASELINE_PLAN.md` 与 `doc/TASK_LEDGER.md` 是 Lead 维护的指针（卡面 `out_of_scope` 明确 `STATUS/PLAN/LEDGER（Lead 维护）`）；本次 diff 仅将它们计入「Lead 指针」，不作为本卡 Owner 的 allowed_paths 内改动。
- 只读声明：本审查只读上述文件、两份契约、`src/infrastructure/sqlite/library.py`、`src/bootstrap/core_service.py`、`tests/core/test_core_delete_commands.py`、`doc/reviews/FEA-12-CORE-r3.md`、scope review 及仓外 7 份复核报告；未改任何被审字节，未 `git add`/`commit`/`push`/`stash`/`reset`/`checkout`；未在仓库内创建临时文件。

## 2. 逐 AC 核对

### AC-1 — 8 项逐项表（MET）

冻结记录 §4A（`doc/plan/FEA-CONTRACT-FROZEN-C04b.md:99-119`）已把原一行 residual 扩为 `R-1…R-8` 8 行表，列覆盖「ID / residual / 位置 / 当前文本/事实摘要 / 问题 / 性质 / 影响 / 现行权威读法 / 需 UNFREEZE」。逐项映射与 scope review §2 完全一致：

| §4A | scope review §2 | 性质（表内） | 需 UNFREEZE（表内） | 与 scope review 的一致性 |
|---|---|---|---|---|
| R-1 | ① artifact 成员谓词 | 契约措辞 + 代码行为 | C-04b 1/18 + M2-C1 rev + 独立实现卡 | 一致；代码位置补充 `:1920-1926`、`:1218-1225`，比 scope review 表内的 `:1926` 更完整 |
| R-2 | ② §2.0「单一字段」 | 契约正文（C-04b） | C-04b 1/18 | 一致；保留「v1.0 遗留、以 §2.2 为准」 |
| R-3 | ③ A1 separate/detached + representative | 载体 0 pin + 契约正文措辞 | 载体 0；两契约 C-04b 1/18 + M2-C1 rev | 一致；保留「无定义」「字典序最小、仅展示、不进 digest」 |
| R-4 | ④ §1 表 M2-C1 行号 | 契约 provenance 元数据 | C-04b 1/18 | 一致；保留「v1.0 时点、以节名为准」 |
| R-5 | ⑤ 首确认「预览 book_ids」与单条来源 | 契约正文 | C-04b 1/18 + M2-C1 rev | 一致；保留「请求 book_ids」「inventoryDigests[bookId]」「inventoryDigests[ 零命中」 |
| R-6 | ⑥ r1–r3 报告 sha 未记 | 纯记录（0 pin） | 否 | 一致；标为「已闭合」并指向 §1C |
| R-7 | ⑦ M2-C1 banner/history 批量限定 | M2-C1 正文（非规范段） | M2-C1 rev（0/18 机械 pin，需手工记录 sha） | 一致；保留「仅批量」 |
| R-8 | ⑧ 单条 manifest 批次字段 | 契约正文（C-04b） | C-04b 1/18 | 一致；保留实现取值与「契约未写死」 |

行号引用在 `28a2826af` 工作树逐点核对（详见 §3 实跑表）：C-04b `:18`/`:21`/`:28-32`/`:44`/`:53`/`:64`/`:69`/`:71`；M2-C1 `:18`/`:30`/`:814`/`:815`/`:819`/`:953`/`:954`/`:968`；`library.py:1178-1190`/`:1920-1926`/`:1218-1225`；`core_service.py:1904-1930`/`:2450-2454`；`test_core_delete_commands.py:1341-1344`。全部与表内引用一致，未见位置/性质/影响/权威读法/UNFREEZE 的歪曲。

补充核对：
- 全文 `inventoryDigests[`（camelCase）在 C-04b/M2-C1 **零命中**，与 R-5 表述一致；
- M2-C1 当前节名行号 `:746`/`:823`/`:838`/`:875` 与 R-4 一致；
- C-04b `:41`/`:42`（单条/批量 digest 形状）与 `:64`/`:69`（§2.2 分支）确实与 `:44` 的「单一字段」措辞字面冲突，R-2 的「v1.0 遗留」定性成立；
- C-04b `:55` 明写预览「零副作用、不缓存」，R-5 的「预览不缓存 → 读请求 book_ids」推论成立。

**结论：MET。** 唯一相邻项是 §4B 的「五轮」修正（P3-5，不改变 AC-1 内容）。

### AC-2 — ⑥ 完全闭合（MET，带 P3-2/P3-3/P3-4）

- **sha256/大小实测**：§1C（`FROZEN:34-53`）列出的 r1–r7 与辅助 `FINAL-CONFIRM.md`，用 `Get-FileHash -Algorithm SHA256` 逐份复算，**7/7 + 1 辅助全部 MATCH**，大小逐份一致（见 §3 表）。路径在 `G:\CODEX\New Manga.workspace\FEA-12\unfreeze-*`；每个目录实际仅一份同名报告，`...` 缩写不产生歧义。
- **r4–r7 与 §1B 前缀一致**：`b6bd2693…`、`02b30b52…`、`924847b9…`、`8af2d4f1…` 与 §1B `:27` 已记 8 位前缀逐项一致。
- **r2 session**：r2 报告 frontmatter 明写「本子会话 id 未在运行上下文中暴露」（父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c` 可见）；§1C 标「session 未在报告内暴露」，属如实说明，未编造。
- **§1B 原文保留**：`git diff --unified=0` 的 §1B 相关 hunk 从原始第 33 行才开始；对 HEAD 第 21–32 行与当前文件逐行比较，**IDENTICAL**。R-6 只靠新增 §1C 闭合，符合「§1B 原文保留不改」。
- **路径/字段精度（P3）**：
  - §1C 给的是「绝对 base `G:\CODEX\New Manga.workspace\FEA-12\` + 相对子路径」，不是逐行绝对路径；r4–r7 还使用 `...-final-review-rN.md` 省略文件名前缀；EV §2 却称「绝对路径」。虽可复算、无歧义，但字面 AC-2 的「绝对路径」未完全满足（P3-2）。
  - §1C 的 r4–r7 session 只记 8 位前缀（`79b03393…` 等），而报告 frontmatter 实际暴露完整 id：
    - r4 `79b03393-9753-47ae-8b14-4bd49717a52a`
    - r5 `6a22e682-1e3d-483b-a3f7-4cb42b784570`
    - r6 `1ece323d-1fbc-4284-a784-a0eb6c8b09d2`
    - r7 `14e8baef-047b-4679-9903-dd5d6f9cd84d`
    表头写「reviewer / session」，未注明 r4–r7 是前缀；属可补全的完整性问题（P3-3）。
  - 卡面 AC-2 原文仍写「§1B 补 r1–r3…」，实际落地为新增 §1C（§1B 保留）；EV 也把 AC-2 映射到 §1C。这是卡面文本与证据落点的表述差（P3-4）。

**结论：MET（⑥ 实质闭合）；P3-2/P3-3/P3-4 为非阻断精度项。**

### AC-3 — ③④ 的 0 pin 收口（MET）

- 载体 `git diff --unified=0` 只有一个 hunk：`@@ -112,0 +113,14 @@`，**+14/−0**；HEAD 112 行与当前文件前 112 行逐行比较为前缀，说明 §1–§5E（以及 §5C、§6、§7）**未改任何字节**，§5F 是纯追加。
- §5F（`CONTRACT-UNFREEZE-2026-11-05.md:114-126`）写明：
  - `separate/detached` **不是** C-01b/C-04b/M2-C1 定义的状态，载体 A1 `:16`/`:18` 与两契约同名表述为历史措辞；现行实现不据此裁剪；
  - representative 现行规则 = 无可见 region 时取 `currentArtifactRevisionIds` 的**字典序最小项**（`core_service.py:1904-1930` 的 `sorted(set(...))[0]`），仅展示、不进 digest；
  - C-04b `:28-32` 的 `M2-C1 §5.11.x :行号` 为 **v1.0 冻结时点**布局，v1.1 后漂移，现行定位以 §5.11.1/§5.11.2/§5.11.3/§5.11.5 节名为准；
  - 标题含日期 `2026-11-07` 与任务 id，正文指向冻结记录 §4A/§1C，来源可追溯。
- 观察（非阻断）：§5F 物理上追加在文件末尾（§7 之后），与编号顺序不一致；这是 append-only 的必然结果，载体既有 §5B/§5D/§5E/§5C 也不是线性顺序，不影响内容与可追溯性。

**结论：MET。**

### AC-4 — ① 的 limitation / L-3（MET）

- 冻结记录 §4A L-3（`FROZEN:119`）如实写明：
  - `src/infrastructure/sqlite/library.py:1178-1190` 的 `list_book_artifact_current_pointers` 用 **page/chapter join**，没有 `media_artifacts.book_id = 本书`；
  - 删除路径 `:1920-1926` 与 `list_book_artifact_revision_ids` `:1218-1225` 使用 `book_id`；
  - 损坏行（`media_artifacts.book_id` 与 `page_id` 所属书不一致）下，preview 的 current 保护集合与删除集合可能不一致（某书**多绑定**/另一书**少绑定**）；
  - **正常数据无影响；未修**；修复需 C-04b+M2-C1 UNFREEZE（补成员谓词）+ 独立实现卡（代码 + 跨书损坏行测试）。
- `src/infrastructure/sqlite/library.py:1178-1190`、`:1920-1926`、`:1218-1225` 的实际代码与 L-3 描述一致（见 §3）。
- 全文**没有**肯定性的「已对齐/已修复」断言。字符串「已对齐/已修复」只出现在禁止性/历史描述语境：卡面 AC-4 的「**不得**写」、L-3 末尾的「**不得**在任何记录写」、§4B `:90` 对 r6 P1-E 的历史说明、EV §5 的「不得写」。按「不得声称」语义判定合规；若按字面零字样口径，可把这些否定句改写为「不得声称已对齐/已修复」（P3 提示，不阻断）。

**结论：MET。**

### AC-5 — ②⑤⑦⑧ 的权威读法登记（MET）

- §4A 前言明确「**C-04b / M2-C1 契约字节未改**：C-04b 仍 `acc8f0e0…`、M2-C1 仍 `701093b5…`（`verify_pins` 18/18）」；「需 UNFREEZE」列给出真正修复所需的动作；«本卡不做» 明确。
- 逐项覆盖：
  - **R-2/②**：`:44` 为 v1.0 遗留，现行以 §2.2 形状分支为准（单条=逐书值；批量=集合级值 + 逐书 map）；
  - **R-5/⑤**：首确认的「预览 `book_ids`」读作**请求 `book_ids`**（预览零副作用、不缓存；digest 绑定保证一致）；单条取预览返回的 `inventoryDigests[bookId]`，集合级 `inventoryDigest` 单条不得使用；全文 `inventoryDigests[` 零命中；
  - **R-7/⑦**：M2-C1 `:18`/`:30` 的 retry 描述**仅适用于批量**；单条以 §5.11.1a `:815`/`:819` 为准；
  - **R-8/⑧**：单条现行实现 `batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry 仅校验逐书 `inventory_digest`；契约未写死。
- 载体 §5F 对 R-2/R-3/R-4/R-5/R-7/R-8 有对应条目，R-1 指向 L-3，R-6 指向 §1C；与 scope review §2.2–§2.8 的读法一致。

**结论：MET。**

### AC-6 — 零字节/零代码门禁与不夸大（MET，带 P3-2…P3-6/P3-8；P3-1 fixed、P3-7 mitigated）

- 审查开始时 `git diff --name-only` 只有 4 个 tracked 文件：`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`（Lead 指针）、`doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`（allowed_paths 内）；`git diff --cached` 为空；无其他 tracked/untracked 越界文件。提交前多出 3 个并行 L-R11 的 `src/**` 文件（P3-7），非本卡/非本审查；**审查后 Lead 提交 `698ac9524` 为 docs-only（4 docs + 本报告 + 任务卡 + evidence，未含 src）**，故本卡集成提交本身仍只有 docs 文件。
- C-04b sha256 `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`、M2-C1 `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f`，与冻结记录 §1 `:15` / §1B `:27` 一致；`git hash-object` 与 `git rev-parse HEAD:<path>` 两侧相同（C-04b `201c8369…`、M2-C1 `6690606c…`）。
- `verify_pins.ps1`：`PIN AUDIT: PASS (all 18)`，C04b `acc8f0e03d42`，exit 0；`check.ps1` 默认与 `-TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` 均为 `PASS (3 warnings)`，exit 0（并行 src 改动不影响这两项治理检查）。
- 审查开始时 `git diff --name-only -- src apps tests` 为空；提交前为 3 个 `src/**`（并行 L-R11）；`698ac9524` 本身为 docs-only、未含 src，**本卡集成提交零代码**。工作树仍保留 3 个并行 src `M`（P3-7 mitigated：提交干净，工作树注记保留）。`git diff --check` 仍 exit 0。
- 不夸大：卡面、EV、冻结记录、载体均未出现「8 项全部关闭/契约已修复」的肯定断言；EV §5 明写「8 项中仅 ⑥ 完全闭合，其余规范修复待 UNFREEZE（另卡，未建立）」，冻结记录 §4A 前言写「仅 R-6 完全闭合；R-3/R-4 的 0 pin 部分已登记；其余契约正文未改」。
- P3：P3-1 已在 `698ac9524` 的 EV 中修为 `+39/−2`（**fixed**）；P3-2/P3-3/P3-4/P3-5/P3-6 仍 open；P3-7 已由 docs-only 提交缓解；P3-8 的原始卡面/EV/报告不一致已由 `63b95abda`/`423efa200`/`3c4f62dbf` 修复，但最终 EV/卡面称 P3-8「由 closeout 闭合」且仍写 `open=6`（8 = fixed 1 + mitigated 1 + open 6），committed 报告 `p3: 6` 也把 P3-8 计为 open；若接受 P3-8 闭合，open 应为 5（计数口径 open）。

**结论：MET（就本卡产物与 `698ac9524` 的 docs-only 集成提交而言；closeout 记录一致性见 P3-8）。**

### §4B 相邻修正与真实性

- §4B `:82` 已由「五轮复核均 CHANGES（r1/r2/r3/r4/r5）」改为「r1–r6 均 CHANGES、r7 窄面 APPROVE（完整报告 sha 见 §1C），无 P0 残留」；与 §1B `:27`（r1–r6 CHANGES、r7 APPROVE）和 §1C（r1–r7 完整 sha）一致。
- 冻结记录 §5 `:129` 已记录该相邻修正「不计入 8 项 AC」；但卡面 AC/目标本身没有这句话（P3-5）。
- EV 的 sha/门禁数字全部与实测一致；唯一数字偏差是 P3-1 的 diff stat。EV §2 的「绝对路径」是 P3-2 的措辞过度；EV §2 AC-6 的 `closeout 明确…` 是 P3-6 的前瞻表述。未发现「声称已完成但实际未落地」的实质声明。

## 3. 实跑与证据

### 3.1 门禁与工作树

| 检查 | 命令/对象 | 实测 | 判定 |
|---|---|---|---|
| HEAD | `git rev-parse HEAD` | `28a2826afdba0fbd3262d109dcd3afa86997afb6` | — |
| 分支/状态 | `git branch --show-current`; `git status --porcelain=v1` | `main`；审查开始 4 M + 2 ??；提交前 7 M + 3 ??；最终 5 M + 1 ??（本报告/SCAN-RH scope review/3 个并行 src；`tests/fea11/test_source_gate_unify.py` 为 `??`；见 §3.5） | — |
| tracked diff | `git diff --name-only` | 审查开始：`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`；提交前：+ 3 个并行 `src/**`；提交后：C-04b 4 docs 已入 `698ac9524`，工作树仅本报告/并行 SCAN-RH/3 src 为 M | 本卡 2 allowed + 2 Lead；src/SCAN-RH 为并行 |
| staged | `git diff --cached --name-only` | 空 | — |
| diff stat | `git diff --numstat` | docs-only：frozen `39/2`、carrier `14/0`、total `61/9`；提交前整树另加 src `172/63`（total `233/72`）；提交后冻结记录/载体已入提交、工作树 docs diff 为 0 | carrier 与 EV 一致；frozen 已 fixed（P3-1）；src 见 P3-7 |
| C-04b sha256 | `Get-FileHash -Algorithm SHA256` | `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f` | 与 pin 一致 |
| M2-C1 sha256 | 同上 | `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f` | 与记录一致 |
| 契约 blob | `git rev-parse HEAD:<path>` / `git hash-object` | C-04b `201c8369d5c79b1052c54dcf24d82ae0cb171ca8`；M2-C1 `6690606c26f67e99e9f61ac87d72ec33c4bd8589`（两侧相同） | 工作树=HEAD |
| 契约零 diff | `git diff --quiet HEAD -- <两契约>` | exit 0 | 零 diff |
| 代码零 diff（本卡） | `git diff --name-only -- src apps tests` | 审查开始：空；提交前：3 个并行 `src/**`（`core_assembly.py`/`core_service.py`/`source_sync.py`，非本卡产物）；提交后：3 个 src 仍为并行 M，`698ac9524` 本身为 docs-only、未含 src | 本卡零 diff；P3-7 mitigated |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `OK C04b acc8f0e03d42`；`PIN AUDIT: PASS (all 18)`；exit 0 | 18/18 |
| check 默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；exit 0 | PASS |
| check `-TaskPath` | 同上 + `-TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` | `PASS (3 warnings)`；exit 0 | PASS |
| 空白 | `git diff --check` | exit 0 | PASS |

`check.ps1` 的 3 个 warning 为：11 个非终态 Task、`doc/STATUS.md` 80%、`doc/REBASELINE_PLAN.md` 80%；与 EV §3 的「PASS (3 warnings)」一致。

### 3.2 §1C 报告哈希/大小复算（全部 MATCH）

| 轮次 | 文件 | 实测大小 | 实测 sha256 | 与 §1C | 与 §1B 前缀 |
|---|---|---:|---|---|---|
| r1 | `unfreeze-review\CONTRACT-UNFREEZE-2026-11-05-review.md` | 48,399 B | `600da6aa08d4834733eef947c11913c08ed6506086456d881997529372796a44` | MATCH | — |
| r2 | `unfreeze-review-r2\CONTRACT-UNFREEZE-2026-11-05-review-r2.md` | 87,408 B | `2eae498f06ef455c5c3a1e963e3003f0ab917f863158e7dfe41767b479432388` | MATCH | — |
| r3 | `unfreeze-final-review\CONTRACT-UNFREEZE-2026-11-05-final-review.md` | 42,856 B | `1b2fa41ec10c8dac7e51203b4d2a1d51f69de042dbdae0296d0fb6632d6f20aa` | MATCH | — |
| r4 | `unfreeze-final-review-r2\CONTRACT-UNFREEZE-2026-11-05-final-review-r4.md` | 33,127 B | `b6bd26937b92c1c799585838f1bec6787cdcbf456a6371fc76c9f823906419d6` | MATCH | `b6bd2693…` MATCH |
| r5 | `unfreeze-final-review-r3\CONTRACT-UNFREEZE-2026-11-05-final-review-r5.md` | 34,683 B | `02b30b5273ffea20da62490509b89d06efc48f1b79dd0a4cb650122ba6bc6ee4` | MATCH | `02b30b52…` MATCH |
| r6 | `unfreeze-final-review-r4\CONTRACT-UNFREEZE-2026-11-05-final-review-r6.md` | 30,007 B | `924847b91f4d819a459c10dca9bb7daa0bafff6a7511c8128d24eef32fa7e066` | MATCH | `924847b9…` MATCH |
| r7 | `unfreeze-final-review-r5\CONTRACT-UNFREEZE-2026-11-05-final-review-r7.md` | 17,688 B | `8af2d4f182163215a883f6908b1b17564ced7e470dab29ef719c41131d046424` | MATCH | `8af2d4f1…` MATCH |
| 辅助 | `unfreeze-final-review\FINAL-CONFIRM.md` | 1,269 B | `d687ede7c4ab326985bd52de38239a4d52807446dc1c67de910a175f2452a010` | MATCH | — |

路径基准：`G:\CODEX\New Manga.workspace\FEA-12\`；表中为相对该 base 的路径。7 份报告所在目录均只有一份对应报告（`...` 缩写不产生歧义）。

### 3.3 关键行号核对

| 对象 | 引用 | 实测内容摘要 | 判定 |
|---|---|---|---|
| C-04b | `:18` | `currentRegionRevisionIds`/`currentArtifactRevisionIds`、`separate/detached`、artifact 谓词 | 命中 |
| C-04b | `:21` | manifest 持久化 `batch_id`/`original_book_ids`/`original_collection_digest`/… | 命中 |
| C-04b | `:28-32` | `M2-C1 §5.11.1 :685`、`:691-695`、`:733`、`:748`、`:745-760`、`:776-802` | 命中 |
| C-04b | `:44` | 「**不得**用单一 `inventory_digest` 字段同时服务两种形状…」 | 命中 |
| C-04b | `:53` | `DeletePreviewItem` 的 `currentRegionRevisionIds`/`currentArtifactRevisionIds` | 命中 |
| C-04b | `:64` | 批量校验「与预览 `book_ids` 完全一致」 | 命中 |
| C-04b | `:69` | 单条首次确认 = 当前重算逐书 digest | 命中 |
| C-04b | `:71` | manifest 行（`batch_id`/`original_book_ids`/`original_collection_digest`/…） | 命中 |
| M2-C1 | `:18` | rev 2.14 banner（retry 规则未限定批量） | 命中 |
| M2-C1 | `:30` | Revision history 2.14（同上） | 命中 |
| M2-C1 | `:814` | 单条逐书 digest / 批量集合级 + 逐书 map | 命中 |
| M2-C1 | `:815` | 两级校验、「与预览 `book_ids` 完全一致」 | 命中 |
| M2-C1 | `:819` | 单条 retry=manifest 逐书值；批量 retry=`original_collection_digest` | 命中 |
| M2-C1 | `:953` | `currentRegionRevisionIds` 含「历史 separate/detached」 | 命中 |
| M2-C1 | `:954` | `currentArtifactRevisionIds`（谓词=`current_revision_id` 非空） | 命中 |
| M2-C1 | `:968` | rev 2.14 追加：artifact 谓词、旧 Core 缺省=unknown | 命中 |
| M2-C1 | §5.11.1 `:746`、§5.11.2 `:823`、§5.11.3 `:838`、§5.11.5 `:875` | 当前节名位置 | 命中 |
| `library.py` | `:1178-1190` | `ma JOIN pages p ... JOIN chapters c ... WHERE c.book_id = ?`（无 `ma.book_id`） | 命中 |
| `library.py` | `:1920-1926` | `DELETE ... WHERE book_id = ?` / `DELETE FROM media_artifacts WHERE book_id = ?` | 命中 |
| `library.py` | `:1218-1225` | `list_book_artifact_revision_ids` 用 `ma.book_id = ?` | 命中 |
| `core_service.py` | `:1904-1930` | `sorted(set(...))`；无可见 region 时 `current_artifact_revision_ids[0]` | 命中 |
| `core_service.py` | `:2450-2454` | 单条 `batch_id=uuid4().hex`、`original_book_ids=[book_id]`、集合级 digest | 命中 |
| `test_core_delete_commands.py` | `:1341-1344` | 断言 `original_book_ids == ["b1"]` 与集合级 `original_collection_digest` | 命中 |

### 3.4 载体/§1B 字节保持

| 检查 | 命令/方法 | 实测 | 判定 |
|---|---|---|---|
| carrier 只追加 | `git diff --unified=0` | 唯一 hunk `@@ -112,0 +113,14 @@`；`+14/−0` | PASS |
| carrier 前缀 | `git show HEAD:<carrier>` 112 行 vs 当前前 112 行 | HEAD 112 行为当前前缀 | PASS |
| §1B 未改 | `git diff --unified=0`；HEAD 第 21–32 行 vs 当前 | hunk 从原始第 33 行开始；21–32 行 `IDENTICAL` | PASS |
| 冻结记录 hunk | `git diff --unified=0` | `-33,0 +34,21`（§1C）、`-61 +82`（§4B）、`-80 +101,15`（§4A 表）、`-83,0 +119`（L-3）、`-92,0 +129`（§5） | 与预期一致 |

### 3.5 Post-review 提交链（Lead）

| 项 | 实测 | 判定 |
|---|---|---|
| HEAD | C-04b closeout 链末 `3c4f62dbfa479a22a82abfbc2daa9ffd72b6b242`（链：`698ac9524` → `63b95abda` → `423efa200` → `3c4f62dbf`）；当前 HEAD `a4cc8a9b7` 为后续 handoff/SCAN-RH 提交 | — |
| 集成 commit | `698ac9524e7d86dbbc46d0063eec44c6f99e8cab`；docs-only 0 pin；含 4 docs + 本报告 + 任务卡 + `verification/**`；**无 `src/**`** | docs-only 集成，未混入并行 src |
| closeout | `63b95abda`：任务卡 `done`/`integration_commit=698ac9524`/`delivery_head=698ac9524`/canonical+resource `complete`；STATUS/PLAN/LEDGER 同步 | closeout done |
| EV/报告入库 | `423efa200`：EV r1 回填 `approved`/P0/P1/P2=0/`open=6/fixed=1/mitigated=1`；本报告修正版入库；并行 SCAN-RH scope review r1 入库 | EV r1 已回填 |
| Canonical Evidence | `3c4f62dbf`：卡面 `Canonical Evidence EV-01` 指向 EV 最终版 `423efa200`；称 **P3-8 由 closeout 闭合** | 与 `open=6` 的算术冲突（见下） |
| 被审 docs 字节 | 提交后 `git diff --name-only -- doc/plan/FEA-CONTRACT-FROZEN-C04b.md doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md` 为空；C-04b/M2-C1 sha 仍 `acc8f0e0…`/`701093b5…` | `698ac9524` 中的 docs 字节 = 被审字节 |
| 任务卡 | committed：`status: done`、`integration_commit/delivery_head=698ac9524`、canonical/resource `complete`、Canonical Evidence `EV-01` → `423efa200` | 原始 P3-8（卡面 ready/pending）已 fixed；计数口径仍 open |
| EV | final `423efa200`：r1 `approved`；总数 8，`fixed=1`（P3-1）、`mitigated=1`（P3-7）、`open=6`；正文称 P3-8「由 closeout 提交闭合」 | 若 P3-8 闭合，8 = 1 fixed + 1 mitigated + 6 open 中不能再含 P3-8；open 应为 5。**算术不一致** |
| 本报告 | committed `423efa200`：`p3: 6`、P3-8 open（P3-2…P3-6 + P3-8）；当前工作树 `M` 为本轮 P3-8 计数注记 | P3-8 open（计数口径） |
| 并行 src/测试 | 3 个 `src/**` 仍为工作树 `M`，另 `tests/fea11/test_source_gate_unify.py` 为 `??`（L-R11）；均未入任何上述 commit | P3-7 **mitigated**（提交干净），工作树注记保留 |

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| P3-1 | P3 | `verification/FEA-12-CORE-C04B-RESIDUAL-1/EV.md:15` | 审查时 EV 写「+41/−2 行」，实际 `git diff --numstat` 为 `39/2`（41 是 `--stat` 的变更行数）；Lead 已在 `698ac9524` 的 EV 中改为 `+39/−2`。影响：已消除；原为证据数字精度。 | `git show 698ac9524:verification/FEA-12-CORE-C04B-RESIDUAL-1/EV.md` → `+39/−2`；`git diff --numstat` → `39 2` | 无（已 fixed） | fixed (698ac9524) |
| P3-2 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:36-48`；`EV.md:33` | §1C 用「绝对 base + 相对子路径」，r1–r3 是完整相对路径，r4–r7 用 `...-final-review-rN.md` 缩写；EV §2 却称「绝对路径」。影响：字面 AC-2「绝对路径」未完全满足；但 7 份 sha/大小均可从 base+路径复算，每个目录仅一份报告，无歧义。 | 见 §3.2；`Get-FileHash` 7/7 MATCH | 写全绝对路径，或明确标注「相对 base 的路径；r4–r7 的 `...` 表示省略 `CONTRACT-UNFREEZE-2026-11-05` 前缀」；同步修正 EV 措辞 | open |
| P3-3 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:45-48` | §1C 的 r4–r7 session 只记 8 位前缀（`79b03393…`/`6a22e682…`/`1ece323d…`/`14e8baef…`），但报告 frontmatter 暴露完整 id；表头写「reviewer / session」，未注明前缀。r2 的子会话 id 确实未暴露（父会话可见），§1C 的「未在报告内暴露」可更精确写为「子会话 id 未暴露（父会话 …）」。影响：AC-2 证据完整性；不影响 sha/路径。 | 7 份报告 frontmatter 的 `reviewer_session`/`session` 字段（见 §2 AC-2） | 补全 r4–r7 完整 session id，或加「r4–r7 为前缀，完整值见报告」注 | open |
| P3-4 | P3 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md:54-55`；`FROZEN:34-38`；`EV.md:33` | 卡面 AC-2 仍写「§1B 补 r1–r3…」，实际落地为新增 §1C（§1B 原文保留）；EV 也把 AC-2 指向 §1C。影响：AC 文本与证据落点表述不一致，未来读者可能误以为 §1B 被修改。 | `git diff --unified=0` 显示 §1B 第 21–32 行未改；§1C 新增于第 34 行起 | closeout 时在卡面注明「AC-2 落地为新增 §1C，§1B 原文保留」，或由 Lead 更新 AC-2 措辞 | open |
| P3-5 | P3 | `FROZEN:82`；`EV.md:15`；`FROZEN:129`；卡面 AC-1…AC-6 | §4B 的「五轮→r1–r6 CHANGES + r7 APPROVE」是 8 项之外的相邻精度修正；EV 与冻结记录 §5 都写「相邻精度项，不计入 8 项 AC」，但卡面 AC/目标没有这句话。影响：scope 文档不够显式；修正本身与 §1B/§1C 一致、无契约字节变化。 | `git diff` 的 `-61 +82` hunk；§5 `:129`；EV §1 `:15` | 在卡面/closeout 补一句「§4B 为 R-6 证据链的相邻精度修正，不计入 8 项 AC」，按 scope review §3.4 明确范围 | open |
| P3-6 | P3 | `verification/FEA-12-CORE-C04B-RESIDUAL-1/EV.md`（§2 AC-6） | EV §2 AC-6 写「closeout 明确『仅 ⑥ 完全闭合；③/④ 的 0 pin 部分已登记；其余契约文本未改』」，但当前 EV/卡面尚无该 closeout 文本；EV §5 只写了「8 项中仅 ⑥ 完全闭合」。影响：属 closeout 前的前瞻表述，不属于已落地声明；closeout 时必须把三句写入。 | EV §2 AC-6 与 EV §5；冻结记录 §4A 前言已有等价三句 | 改为「closeout 须明确…」，或在 closeout 时补齐三句并回填 EV | open |
| P3-7 | P3 | `src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py`（审查期间并行 L-R11） | 23:51–23:52 工作树新增 3 个 `src/**` 修改（`172/63`），非本卡 allowed_paths 产物、非本审查写入；审查开始时为零。Lead 的 `698ac9524` 为 docs-only、未含 src，集成提交干净；工作树仍有 3 个 src `M` + `tests/fea11/test_source_gate_unify.py`（`??`，L-R11 测试）。影响：仅剩工作树/未来提交需保持 pathspec；不会由本卡引入代码。 | `git show --name-only 698ac9524` 无 `src/`；`git diff --numstat -- src` → `19/14`、`26/24`、`127/25`；`git status` 显示测试文件 `??`；文件时间戳 `2026-11-07T23:51:02`–`23:52:26` | 保持显式 pathspec；并行 L-R11 自行提交；不得把 src/测试改动归入本卡 | mitigated (698ac9524) |
| P3-8 | P3 | `423efa200`（EV/报告）；`3c4f62dbf`（任务卡 Canonical Evidence） | **原始事实已 fixed**：`63b95abda` 把任务卡改为 `done`/`integration_commit=698ac9524`/complete；`423efa200` 回填 EV r1（`approved`/P0/P1/P2=0）并入库本报告修正版；`3c4f62dbf` 把 Canonical Evidence EV-01 指向 EV 最终版 `423efa200`。**剩余 open**：EV/任务卡称 P3-8「由 closeout 闭合」，但 EV 仍计 `open=6`（8 = fixed 1 + mitigated 1 + open 6），committed 报告 `p3: 6` 也把 P3-8 计为 open；若 P3-8 闭合，open 应为 5。影响：P3 计数口径不一致，不涉及代码/契约字节。 | `git show 423efa200:verification/.../EV.md`（open=6 + P3-8 closed）；`git show 3c4f62dbf:doc/tasks/...`；`git show HEAD:doc/reviews/...-r1.md`（p3:6, P3-8 open） | Lead 统一口径：P3-8 标 closed 且 open=5，或保留 open=6 且不称 P3-8 闭合；同步 report/EV/task card/commit message | open（原始卡面/EV 不一致已 fixed；计数口径待统一） |

**P0/P1/P2：0。** 8 项总计：P3-1 **fixed**（`698ac9524`）、P3-7 **mitigated**（`698ac9524` docs-only）、P3-2…P3-6 + P3-8 共 **6 项 open**；均非阻断。口径说明：EV/任务卡称 P3-8 已闭合但仍写 `open=6`；若接受 P3-8 闭合，open 应为 **5**。本报告暂按「P3-8 open（计数口径待统一）」计 6，Lead 可在 closeout 记录中二选一。

## 5. 结论与复审

- **verdict: `approved`**。P0=0、P1=0、P2=0、**P3=6 open**（8 项总计：P3-1 fixed、P3-7 mitigated；P3-2…P3-6 + P3-8 open）；AC-1…AC-6 实质 MET（AC-6 就本卡产物与 `698ac9524` 的 docs-only 集成提交而言）。
- **closeout 已发生（`698ac9524` → `63b95abda` → `423efa200` → `3c4f62dbf`）**：集成提交为 docs-only（4 docs + 本报告 + 任务卡 + evidence，未含 src），被审 docs 字节与提交一致，C-04b/M2-C1 未变；任务卡已 `done`/`integration_commit=698ac9524`/complete，EV r1 已回填 `approved`/P0/P1/P2=0，本报告修正版已入库。**剩余不一致**：EV/任务卡称 P3-8「由 closeout 闭合」，但 EV 仍写 `open=6`（8 = fixed 1 + mitigated 1 + open 6），committed 报告 `p3: 6` 也把 P3-8 计为 open；若 P3-8 闭合，open 应为 5。建议 Lead 二选一统一（P3-8 closed + open=5，或 open=6 + 不称 P3-8 闭合），并同步 report/EV/task card/commit message。
- **并发注记**：`src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py` 的 3 个修改是审查期间并行 L-R11 的 publication gate 实现（C-17 §3.3），**不是本卡产物**；`698ac9524` 已用 docs-only 提交排除它们（P3-7 mitigated），工作树仍有 3 个 src `M`，应由 L-R11 自行提交，不得归入本卡。
- **剩余风险**：本卡只登记 residual，不修复契约措辞/① 代码；R-1 的损坏行保护集合偏差仍在（L-3），R-2/R-5/R-7/R-8 的规范修复待 UNFREEZE，R-3/R-4 的契约措辞待 UNFREEZE；这些均为已登记、未修，不是本卡引入的新风险。
- **不得**据本报告宣称「8 项全部关闭」或「契约已修复」；准确的表述是「8 项中仅 R-6 完全闭合；其余为已登记、未修，规范修复待 UNFREEZE；C-04b/M2-C1 字节未改」。

## 6. 真实性声明

- **写入范围**：本报告是本次**由审查者**唯一写入仓库的文件（`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`）。Lead 已在 `423efa200` 中提交本报告的修正版；当前工作树版本是进一步的 P3-8 计数口径注记（未提交）。未修改任务卡（`status: done`/`integration_commit`/`complete` 与 Canonical Evidence 字段是 Lead 的 closeout 改动，非本审查）、冻结记录、载体、C-04b/M2-C1、`src/**`、`apps/**`、`tests/**`、EV 或任何证据日志；未 `git add`/`commit`/`push`/`stash`/`reset`/`checkout`；仓内未创建临时文件。审查期间并行 Agent 对 3 个 `src/**` 文件、`tests/fea11/test_source_gate_unify.py` 与 `doc/reviews/FEA-11-SCAN-RH-scope-r1.md` 的修改不是本审查产生，我未触碰、未回滚。
- **独立性**：我是 fresh subagent（会话 `c66cd50f-35fc-4564-afbc-2f90cf266e48`；父会话 `session-3ac1953a-094e-4339-889a-284df2b7b34d`），未参与本卡起草、C-04b/CORE 实现或返修、此前 scope review；只读被审工作树最终字节与 `reviewed_head=28a2826af`。
- **实测与未跑**：实测项见 §3（HEAD/status/diff、两契约 sha 与 blob、7+1 报告 sha/大小、逐点行号、§1B/载体前缀、pins、check、`698ac9524`/`63b95abda`/`423efa200`/`3c4f62dbf` 的提交内容/卡面/EV/报告状态）。**未跑**：全量 `pytest`、全量 .NET、GUI/e2e、真实 Windows 回收站 D 流程；本卡 docs-only、本卡产物零 `src/**`/`tests/**`/`apps/**` 改动，审查期间并行 L-R11 的 src 改动非本卡，上述未跑项不作为本报告的正面证据，也不宣称其通过。
- **口径**：`git hash-object` 是 blob SHA-1，只用于证明「工作树字节=HEAD 字节」；与冻结 pin 的 SHA-256 不是同一算法，不能互相替代。`verify_pins` 18/18 只证明 pin 行与当前文件自洽，不替代语义复核。行号以 `28a2826af` 工作树为准；C-04b/M2-C1 与 HEAD 字节相同，故行号在两侧一致。P3 计数口径：`p3: 6` = open；总 findings 8（P3-1 fixed、P3-7 mitigated、P3-2…P3-6 + P3-8 open；若接受 P3-8 闭合则 open=5）。
- **工作树**：审查后最终状态 = 本报告 `M`（P3-8 计数注记）+ 3 个并行 `src/**` `M`（L-R11）+ `tests/fea11/test_source_gate_unify.py`（`??`，L-R11）+ 并行 `doc/reviews/FEA-11-SCAN-RH-scope-r1.md` `M`；任务卡/EV/冻结记录/载体/`REBASELINE_PLAN`/`TASK_LEDGER`/`STATUS` 均已入 HEAD、无 diff；C-04b/M2-C1 sha 未变。未触碰、未回滚 Lead 指针、任务卡 closeout 字段或任何并行文件。
