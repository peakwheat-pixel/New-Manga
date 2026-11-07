# CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL：C-04b v1.2 + M2-C1 rev 2.15（契约债务清偿）

> 载体用途：按 C-04b 冻结记录的 UNFREEZE 流程提出 **C-04b v1.2** 与 **M2-C1 rev 2.15** 字节修订；须经独立上下文
> fresh subagent 做 **byte-level 复核** + DSH 重新冻结后方可视为最终字节。
> 触发：用户 AUTORUN 指令（2026-11-08：全部授权 / 自主裁决 / 不询问用户）；权威 scope review
> `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（session `0fc94b7f…`；verdict **recommended**；
> §3.3 给出 UNFREEZE 的**确切行/句**与**精确 pin 口径**）；**DSH 裁决（裁决人=DSH）**：按 AUTORUN §2 判据 (b)
> 「契约债务清偿」立项，清 R-1/R-2/R-3/R-4/R-5/R-8；R-1 的**代码**实现另立 `FEA-12-CORE-C04B-RESIDUAL-3`。
> 顺序：本载体 + C-04b + M2-C1 + 冻结记录 + 矩阵为 UNFREEZE 提交；实现另卡。

## 1. 背景与目标

- `FEA-12-CORE` closeout 时登记 8 项 P2 residual（`doc/tasks/FEA-12-CORE.md:284` ②），随后
  `FEA-12-CORE-C04B-RESIDUAL-1`（docs-only，`698ac9524`）把它们逐项登记进冻结记录 §4A `R-1…R-8` 与载体 §5F，
  但**契约字节未改**。其中 6 项属**契约正文措辞/谓词文字**（R-1 谓词、R-2 措辞、R-3 术语、R-4 行号、R-5 来源、
  R-8 单条取值），1 项属**记录**（R-6，已闭合），1 项属 M2-C1 非规范段（R-7）。
- **目标**：把这 6 项在**不改变任何规则、字段名、错误码、能力、wire minor、`PROTOCOL_MINOR`、schema、依赖**的前提下
  就地纠正为准确文字；同步 M2-C1 至 **rev 2.15**（banner/history/来源/校验/retry 措辞 + §5.11.1a/§5.13 标题）。
- **pin 口径（精确）**：C-04b 是 18 份冻结对象中的 **1/18**（重签后其余 **17 必须实测不变**）；
  **M2-C1 不在 `verify_pins.ps1` 的 18 份映射内** → 改它 **0/18 机械 pin**，其新 sha256 只能手工登记进
  冻结记录 §1/§1B/§4C 与本载体，`verify_pins` 不会发现其漂移（scope review §3.3 已指出并纠正「2 pins」说法）。

## 2. 提议修订

### A. C-04b v1.2（6 处，均为文字）

| # | 位置 | 改法 |
|---|---|---|
| R-1 | §0 第 1 条、§2.1 `DeletePreviewItem` | `currentArtifactRevisionIds[]` 的成员谓词补 **`media_artifacts.book_id = 本书`**（与删除面 `DELETE … WHERE book_id = ?` 一致），保留「`current_revision_id` 非空、不按可见性过滤」 |
| R-2 | §2.0 末段 | 「不得用单一 `inventory_digest` 字段同时服务两种形状」→「**不得在同一请求内混用两种 digest 语义**：单条只提供逐书 `inventory_digest`；批量必须同时提供集合级 `inventory_digest` 与逐书 `inventory_digests`」（与 §2.0 表、§2.2 形状分支一致） |
| R-3 | §0 第 1 条、§2.1 DTO | 删除**无定义术语** `separate/detached`（改为「全部 region（含 lineage-hidden）」）；`currentRevisionId` 的 representative 规则**写死且与实现一致**：「**按阅读序的第一个 lineage-visible region** 的 current（排序键 `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, region.reading_order, region_id`，过 lineage guard）；**若无可见 region current**，取**首个 artifact current pointer**（pointer 顺序；**非字典序**）；均无 null」，并明确「仅展示、不承担绑定、不进 digest」 |
| R-4 | §1 现状表 | 把 `M2-C1 §5.11.1 :685` / `:691-695` / `§5.11.2 :733` / `§5.11.3 :748`、`:745-760` / `§5.11.5 :776-802` 的**行号去掉**，改为**节名**（§5.11.1 / §5.11.2 / §5.11.3 / §5.11.5） |
| R-5 | §2.2 校验顺序、§2.2 首次确认 | 首次确认的比对对象由「预览 `book_ids`」改为「**请求** `book_ids`」（预览零副作用不缓存；digest 绑定保证与预览一致）；单条 digest **来源**写明「取自预览返回的 `inventoryDigests[bookId]`（逐书值）；集合级 `inventoryDigest` 不得用于单条」 |
| R-8 | §0 第 4 条、§2.2 manifest | 补单条取值：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry **只校验**逐书 `inventory_digest` |

另：状态行 → `FROZEN v1.2`（v1.1 2026-11-05 / v1.2 2026-11-08）；日期行补 v1.2；§0 增 v1.2 摘要块（v1.1 摘要保留）；
§6 变更记录追加 v1.2 行。

### B. M2-C1 rev 2.15（只同步，规则同 2.14）

| 位置 | 改法 |
|---|---|
| `:18` banner | **新增** rev 2.15 段（显式说明「只同步 C-04b v1.2 措辞与谓词文字，规则同 2.14」）；rev 2.14 段**原文保留** |
| `:30` Revision history | 追加 `2.15` 行（同上口径：不新增命令/字段/错误码/capability；`PROTOCOL_MINOR` 与 wire minor 不变） |
| `§5.11.1a` 标题 | `rev 2.14` → `rev 2.14/2.15`（措辞/谓词同步；运行未实现） |
| `§5.13` 标题 | `C-04b v1.1 §2.1，rev 2.14` → `C-04b v1.2 §2.1，rev 2.14/2.15` |
| 来源行 | 单条 digest 补「rev 2.15：取自预览返回的 `inventoryDigests[bookId]`；集合级 `inventoryDigest` 不得用于单条」 |
| 校验顺序行 | 「必须与预览 `book_ids` 完全一致」→「必须与**请求** `book_ids` 完全一致（rev 2.15：预览零副作用不缓存）」 |
| retry 规则行 | 标注「rev 2.15 明确集合级规则**仅批量**；单条 retry 只校验 manifest 逐书 digest」 |
| `:953` DTO 注释 | 删 `separate/detached`，改为「全部 region（含 lineage-hidden）current」 |`n| `:972` §5.13 PD-01 段 | 补 artifact 成员谓词 `media_artifacts.book_id = 本书`；representative 规则指向 C-04b v1.2 §0 第 1 条（r1 P1-2 / r2 确认） |
| `:954`（现 `:958`）DTO 注释 | 补成员谓词 `media_artifacts.book_id = 本书`，representative 规则指向 C-04b v1.2 §0 第 1 条（仅展示、不进 digest） |

### C. 冻结记录 / 矩阵

- `FEA-CONTRACT-FROZEN-C04b.md`：§1 pin → v1.2 `4b304c0c…`（blob `a30e4080…`）+ 历史 pin 保留；§1B 增 v1.2 行
  （含 M2-C1 `a82a7fc1…` / blob `cb8eeb21…`，标注 0/18 机械 pin）；§2 增条件 7（⏳→复核后 ✅）；新增 **§4C**
  v1.2 重冻记录；§4A 增「v1.2 状态更新」append-only 说明；§5 变更记录追加 v1.2 行。
- `FEA-CONTRACT_FREEZE_MATRIX.md`：状态行补 C-04b v1.2；第 4 行 → `FROZEN v1.2`（含复核 ⏳ 与 R-1 代码归 RESIDUAL-3）。

## 3. 安全与兼容

- **零语义变更**：不新增/删除命令与字段，不改错误码/能力/`PROTOCOL_MINOR`/wire minor/schema/依赖；不改任何校验
  顺序、拒绝条件或失败分类。改动仅让文字与**现行实现**（`core_service.py:1904-1930`、`:2450-2454`；
  `library.py:1178-1190` 待 RESIDUAL-3）一致。
- **R-1 的契约侧改动只写谓词**：契约从此要求「成员=本书」；**代码尚未改**（仍 page/chapter join）→ 该偏差在
  `L-3` 中继续如实登记为**未修**，由 `RESIDUAL-3` 收敛。**不得**因本卡而声称「R-1 已修复」，也**不得**说「本包全部文字与现行实现一致」——**R-1 侧契约与实现当前不一致**（这正是 RESIDUAL-3 的存在理由）；其余 R-2/R-3/R-5/R-8 的文字与现行实现一致（representative 规则、请求侧比对、单条 manifest 取值）。
- **M2-C1 的可漂移风险**：它不在 `verify_pins` 映射内，故必须靠「冻结记录/载体登记的 sha + 手工 `Get-FileHash`
  复核」防漂移；本卡在 §1B/§4C/载体 §7 三处登记新 sha。
- 兼容：旧 Host/Core 行为不变（无 wire/字段变动）。

## 4. 风险与回退

- 风险：①C-04b 1/18 pin 重签须独立复核；②M2-C1 无机械 pin，若登记录错会静默漂移 → 以三处 sha + 复核覆盖；
  ③若 R-1 契约先改而代码长期不改，会形成「契约与实现不一致」——已用 `L-3` 显式登记并排 RESIDUAL-3。
- 回退：恢复 C-04b v1.1 `acc8f0e0…` 与 M2-C1 rev 2.14 `701093b5…` 字节 + 冻结记录/矩阵；RESIDUAL-3 不释放。

## 5. 独立复核要求

- Reviewer：**未参与起草/前轮复核**的 fresh subagent，只读最终字节；记录 session/reviewed_head。
- 核对：①§2 逐项落地（C-04b 6 处 + M2-C1 9 处 + 记录/矩阵）；②`git diff` 仅命中 C-04b/M2-C1/冻结记录/矩阵/载体/卡；
  C-17/C-06/C-15/C-16/C-07 及其余契约零 diff，`src/apps/tests/schema` 零 diff；③无新命令/字段/错误码/能力/wire minor/
  `PROTOCOL_MINOR`；④pin 可复算：C-04b `4b304c0c…`、其余 **17 不变**、18/18 PASS；M2-C1 `a82a7fc1…` 与三处登记一致；
  ⑤语义零改动（不得把任何「措辞同步」写成规则变化）；⑥**不夸大**：R-1 代码未修（L-3 仍有效）、不得写「8 项全部关闭」。
- 通过标准：`approved`（可含非阻断 P3）；随后 DSH 回填记录并重跑 pins。

## 6. 复核结果（独立 byte-level）

- **r1 `changes_requested`（P0=0 / P1=2 / P2=1 / P3=4）**：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r1.md`。
  P1-1 = representative 规则被误改为「region 数组字典序最小项」（与实现不符）；P1-2 = M2-C1 `:972`（旧 `:968`）
  §5.13 正文缺 `media_artifacts.book_id = 本书`。已返修。
- **r2 `changes_requested`（P0=0 / P1=1 / P2=2 / P3=2）**：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r2.md`。
  P1-2 **已关闭**；P1-1 残余——artifact fallback 被写成「按字典序排序的 `currentArtifactRevisionIds` 首项」，
  但实现 `core_service.py:1929-1930` 取的是**未排序局部 pointer 列表的首项**（reviewer 只读探针复现：
  DTO `["aaa","zzz"]` → 代表值 `"zzz"`）。已按「**首个 artifact current pointer**（pointer 顺序
  `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, artifact_type, artifact_id`；
  **非字典序**）」返修，并同步 banner/history/`§5.13`/`:958`/载体/EV。
- **r3**：**待派**（复核新字节 C-04b `4b304c0c…` / M2-C1 `a82a7fc1…`）；approved 后回填。

## 7. 真实性声明

1. 本载体只记录**提议字节**；独立 byte-level 复核 approved + DSH 重冻前，不得作为「已复核字节」引用。
2. 实测：C-04b `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52`（blob `a30e4080116d01512977eca40de1c43ea7244a64`）；
   M2-C1 `a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e`（blob `cb8eeb21279ff3dd23ad7c1cec6c171b211592e9`）；
   `git diff --numstat` = C-04b `26/15` + M2-C1 `20/16`（两文件合计 +46/−31），其余契约与源码零 diff。
3. 不声称 R-1 代码已修、不声称 8 项 residual 全部关闭；R-6 已闭合、R-7 已由 rev 2.15 banner/history 落地。
