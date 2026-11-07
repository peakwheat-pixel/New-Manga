---
task: FEA-12-CORE-C04B-RESIDUAL-2
title: C-04b v1.2 + M2-C1 rev 2.15 UNFREEZE：独立 byte-level 复核（r2 / 返修后新字节）
reviewer: fresh subagent (r2)
session: 1975a972-5b34-4267-91cd-f3d16e3585c7
reviewed_head: d91d9b6cc4afef307b0662055812c129468054a0
reviewed_worktree_sha256:
  C-04b: 23398a2296df000d5ab73d89d9305115e672522d973eed000ed031b32048c489
  M2-C1: 3c74d946f1b46e7da173b12a568eb0d038b76177596f4713ef7aa434dd504058
verdict: changes_requested
p0: 0
p1: 1
p2: 2
p3: 2
date: 2026-11-08
---

# C-04b v1.2 + M2-C1 rev 2.15 UNFREEZE：独立 byte-level 复核（r2 / 返修后新字节）

> 只读复核。我是本次委派的 fresh subagent（session `1975a972-5b34-4267-91cd-f3d16e3585c7`），**未参与**本包起草、**未参与** r1 复核、**未参与** C-04b/CORE 实现或返修。未修改生产代码、测试、契约、冻结记录、矩阵、载体或任务卡；未 `git add`/`commit`/`push`/`reset`/`checkout`/`stash`。本报告是本次唯一写入仓库的文件（untracked）；仓外临时文件仅写 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review-r2\`（`probe-representative.py` 与 `.log`）。

## 0. 结论先行

**verdict: changes_requested**——P0=0、**P1=1**、P2=2、P3=2。

**机械面干净**：两契约实测 SHA-256/blob 与题面及冻结记录一致（**MATCH**）；`verify_pins.ps1` **18/18 PASS**；18 份映射中**其余 17 份 blob 与 HEAD 逐项相同**，仅 C-04b 变化；M2-C1 不在映射（**0/18 机械 pin**），§1B/§4C/载体 §7 三处登记与实测一致；`git diff --check` 干净；`src/**`、`apps/**`、`tests/**` 零 diff；`check.ps1` 默认与 `-TaskPath` 均 PASS（3 warnings）。**P1-2 已真正关闭**：M2-C1 §5.13 正文 `:972` 已补 `media_artifacts.book_id = 本书`，且 M2-C1 内未发现其他“artifact 谓词=current_revision_id 非空、缺 book_id”的现行规范句。

但 **P1-1 未完全关闭**：C-04b v1.2 §0 第 1 条的 **artifact fallback** 仍写成“取按字典序排序的 `currentArtifactRevisionIds` 的首项”，而现行实现取的是**阅读序第一个 artifact current pointer**（局部 list 未排序），不是 revision id 字典序最小。r1 §4 与 scope review §2.3 所说“该列表已排序”是对 `core_service.py:1901-1930` 的误读——`sorted()` 只赋给 `inventory[...]`，代表值用的是未排序的局部 list `[0]`。我用只读探针复现：DTO 数组为 `["aaa","zzz"]`，代表值却是 `"zzz"`（pointer 首项），不是 `"aaa"`。这使 v1.2“写死且与实现一致”的自述在 R-3 上仍不成立。

其余为非阻断：P2-1（banner/history/摘要仍笼统写“representative 取字典序最小项”，载体 §3 仍保留“改动仅让文字与现行实现一致”的过宽句）、P2-2（EV/载体的 diff 数字与 pins/check 日志早于返修字节）、P3-1（M2-C1 `:28`/`:140`/`:928` 仍是 rev 2.14 / C-04b v1.1）、P3-2（记录未列 `:972` 且行号仍是插入前编号、r1 状态仍写“待派/待回填”）。

## 1. 基线与只读事实

- 仓库/分支/HEAD：`G:\CODEX\New Manga`，`main`，`d91d9b6cc4afef307b0662055812c129468054a0`；任务卡 `base_commit: d91d9b6cc` 与 HEAD 一致。
- 开始/结束时 `git status --porcelain` 的 tracked 集合相同：
  - `M doc/REBASELINE_PLAN.md`、`M doc/STATUS.md`、`M doc/TASK_LEDGER.md`
  - `M doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
  - `M doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`
  - `M doc/plan/FEA-CONTRACT-FROZEN-C04b.md`
  - `M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`
  - `?? doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md`、`?? doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r1.md`、`?? doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md`、`?? doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`、`?? verification/FEA-12-CORE-C04B-RESIDUAL-2/`
- 只读手段：`Get-FileHash`、`git hash-object`、`git rev-parse HEAD:<path>`、`git diff`/`--numstat`/`--name-only`/`--check`、`Select-String`、`verify_pins.ps1`、`check.ps1`、逐行读取 `src/bootstrap/core_service.py`、`src/infrastructure/sqlite/library.py`、`tests/core/test_core_delete_preview_commands.py`，以及一个只读探针（见 §2.4）。
- 本报告行号：除注明“旧”外，均指**当前工作树**行号；diff 的 old/new 为 `git diff` hunk 行号。

## 2. 核对 1：P1-1 representative 是否真正与实现逐要素等价

### 2.1 结论：**部分等价；artifact fallback 不等价（P1）**

| 要素 | C-04b v1.2 文字 | 现行实现 | 判定 |
|---|---|---|---|
| region 分支排序 | “按阅读序的第一个 lineage-visible region 的 current”，排序键 `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, region.reading_order, region_id` | `core_service.py:1912-1928` 按 `raw["region_current_pointers"]` 顺序遍历；该顺序来自 `library.py:1172-1173` 的 `ORDER BY c.sort_order, c.import_order, c.chapter_id, p.sort_order, p.page_id, r.reading_order, r.region_id` | **MATCH** |
| lineage-visible 过滤 | “过 lineage guard 判可见” | `:1916-1926` 调 `guard.is_region_readable(...)`；不可见/异常跳过 | **MATCH** |
| fallback 条件 | “**若无可见 region current**” | `:1929` `current_revision_id is None`（扫描完可见 pointer 后仍无值） | **MATCH** |
| artifact fallback | “则取按字典序排序的 `currentArtifactRevisionIds` 的**首项**” | `:1929-1930` 取 `current_artifact_revision_ids[0]`；该局部 list 在 `:1891-1898` 按 artifact pointer 顺序追加，**未排序** | **MISMATCH（P1）** |
| 仅展示/不绑定/不进 digest | “仅展示、不承担绑定、不进 digest” | `:2043` 单独返回 `currentRevisionId`；digest 输入 `src/application/library/service.py:297-312` 不含该字段 | **MATCH** |

### 2.2 代码事实（关键）

`core_service.py:1891-1906`：

```python
current_artifact_revision_ids: list[str] = []
...
for pointer in raw["artifact_current_pointers"]:
    revision_id = pointer["current_revision_id"]
    ...
    current_artifact_revision_ids.append(revision_id)
...
inventory["current_artifact_revision_ids"] = sorted(
    set(current_artifact_revision_ids)
)
```

- `sorted(...)` 的结果只写入 `inventory["current_artifact_revision_ids"]`（供 DTO/digest）；局部变量 `current_artifact_revision_ids` 仍是 pointer 顺序。
- `:1929-1930` 的 fallback 用的是**局部变量** `[0]`，不是排序后的 DTO 数组。
- `:1858-1861` 的 docstring 也明确写：“falling back to the **first artifact current pointer**, else null”——实现意图是 pointer 顺序，不是 revision id 字典序。
- artifact pointer 的顺序由 `library.py:1186-1187` 决定：`ORDER BY c.sort_order, c.import_order, c.chapter_id, p.sort_order, p.page_id, ma.artifact_type, ma.artifact_id`；不含 `current_revision_id` 排序。
- `artifact_revision_id` 由 `src/infrastructure/sqlite/artifacts.py:154` 的 `uuid.uuid4().hex` 生成，与阅读序无关；因此“pointer 首项”与“revision id 字典序最小”在多 artifact 时必然可能不同。

### 2.3 r1 / scope review 的误读

- r1 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r1.md:227` 写：“回退到 `current_artifact_revision_ids[0]`（该列表已排序，故等价于 artifact 字典序最小）”。
- scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md:95` 写：“先 `sorted(set(...))`，再取 `current_artifact_revision_ids[0]`，即 artifact revision id 字典序最小”。

两处都把“`inventory[...]` 被排序”误当成“局部 list 被排序”。实际代码只排序了前者；`[0]` 取的是后者。本包的 v1.2 文字沿用了该误读，因此 normative text 与实现仍不一致。

### 2.4 只读探针（独立复现）

探针：`G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review-r2\probe-representative.py`（只读调用 Core preview；临时 DB 在仓外 workspace）。
构造：1 本书、1 页、**无 region**、2 个 artifact；pointer 顺序为 `mask→zzz`、`translated→aaa`（`mask` 在 `translated` 前，但 `zzz > aaa`）。

实测输出：

```json
{
  "currentArtifactRevisionIds": ["aaa", "zzz"],
  "currentRevisionId": "zzz",
  "artifact_pointer_order": ["zzz", "aaa"],
  "sorted_artifact_ids": ["aaa", "zzz"]
}
```

- DTO 数组按字典序排序（`["aaa","zzz"]`），与契约一致；
- 代表值取 **`"zzz"`**（第一个 artifact pointer），**不是**契约文字规定的排序数组首项 `"aaa"`；
- 该差异在“无可见 region current 且 ≥2 个 artifact current”时必须出现，不是理论边角。

### 2.5 影响与修复建议

- **影响面**：`currentRevisionId` 仅展示、不进 digest、不承担绑定，因此**不构成保护集合/删除判定/数据丢失风险**；但它是 normative representative 规则，且本卡 R-3 的目标就是“写死且与实现一致”。当前文字仍会让未来实现者按“字典序最小”实现出与现行 Core 不同的展示值，并让 v1.2/载体“与现行实现一致”的自述在 R-3 上不成立。
- **方案 A（推荐，纯文字回到实现）**：把 §0 第 1 条 artifact fallback 改为“取**第一个 artifact current pointer**（阅读序：`chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, artifact_type, artifact_id`；按 revision id 去重）”；同步 M2-C1 `:972` 的“否则 artifact 数组首项”、C-04b §0 摘要/§6、冻结记录 §4C、载体 §2A/§3、EV §2。
- **方案 B（若确实要 lexicographic min）**：把“representative artifact = 排序数组首项”作为**规则/代码变更**另立实现卡（改 `core_service.py:1929-1930` + 多 artifact 测试），不能塞在本卡“只改文字”的叙述里；当前 `RESIDUAL-3` 的 AC 只覆盖 artifact 成员谓词，不含 representative 排序，需扩卡或另卡。

## 3. 核对 2：P1-2（M2-C1 §5.13 正文 artifact 谓词）——**已关闭**

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:972`（旧 `:968`）现为：
  > artifact 成员谓词=**`media_artifacts.book_id = 本书`** 且 `current_revision_id` 非空、不按可见性过滤（rev 2.15 补）；受保护 artifact 表达=数组长度。representative `currentRevisionId` 取值规则见 C-04b v1.2 §0 第 1 条……
- 同节 DTO 注释 `:958` 也含 `media_artifacts.book_id = 本书`；banner `:18`、history `:32` 亦含。
- 对 M2-C1 全文检索“谓词 / `current_revision_id` 非空 / `currentArtifactRevisionIds`”：现行规范句只有 `:958`/`:972`（均已含 `book_id`）；`:18`/`:32` 是 banner/history（也已含）；`:20`/`:34`/`:142` 是 rev 2.14 历史段（保留不改，可接受）；`:1461` 的 §12 状态表只写“artifact current”不带谓词，不构成缺谓词的规范句。
- 结论：**P1-2 关闭**；M2-C1 内部“DTO 注释 vs 正文”的旧冲突已消除。

## 4. 核对 3：语义零变更

- `git diff --numstat`：C-04b **26 插入 / 15 删除**；M2-C1 **19 插入 / 15 删除**（r1 时为 11/7，返修新增了 P1-2 与若干版本引用行）。
- `git diff -U0`：C-04b **11 个 hunk**（与 r1 的表一致，仅 hunk 3/7 的 representative 文本变化）；M2-C1 **15 个 hunk**（banner/history 2 个新增 + 13 个替换）。
- 逐 hunk 核对：变化均为**措辞、版本引用、谓词文字、行号→节名**；未发现：
  - 校验顺序变化（`§5.11.1a` 仍：单条=逐书值；批量=集合级+逐书 map；retry 仅批量集合级规则）；
  - 拒绝条件/失败分类变化（缺/多 key → `INVALID_REQUEST`；语义失败 → `BOOK_DELETE_STALE_PREVIEW`，与 HEAD 相同）；
  - 字段名/错误码/能力变化（无新增/删除）；
  - `PROTOCOL_MINOR` 变化（仍 3）；wire minor 变化（preview 仍 11、trash 仍 13、既有删除仍 10）。
- `git diff --check`：exit 0；仅 Git 的 LF→CRLF warning（`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`），非本包内容问题。
- `git diff --name-only -- src apps tests`：**空**。
- 结论：**文字级 zero-semantic-change 成立**（R-1 谓词是 scope 明确授权的契约文字补全；R-3 representative 的 artifact fallback 是 P1，见 §2）。

## 5. 核对 4：pin 账

| 项 | 实测 | 判定 |
|---|---|---|
| C-04b SHA-256 | `23398a2296df000d5ab73d89d9305115e672522d973eed000ed031b32048c489` | 与题面、冻结记录 §1 `:15` 一致 |
| C-04b blob | `806f942d89c41824bfa588dfb507f637974728cd` | 与 §1 `:16` 一致 |
| M2-C1 SHA-256 | `3c74d946f1b46e7da173b12a568eb0d038b76177596f4713ef7aa434dd504058` | 与题面、§4C `:111`、载体 §7 `:95` 一致；§1B `:31` 为 `3c74d946…` 前缀，前缀一致 |
| M2-C1 blob | `1ec38cc9addda6705fa198341bb433eb6e62507b` | 与 §1B `:31` 一致 |
| 18 份映射 | **17 份 SAME + C-04b DIFF（预期）** | 其余 blob 与 HEAD 逐项相同 |
| `verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；OK C04b `23398a2296df` | **18/18 PASS** |
| M2-C1 机械 pin | `verify_pins.ps1:6-13` 的 18 项 map **无 M2-C1** | **0/18 机械 pin**，只能手工登记 |

- 17 份 SAME 的 blob 前缀：`C01b 7127d064 / C02 fcea994a / C03 81738c04 / C05 32d039c0 / C06 b537e76d / C07 cd51f8e6 / C08 b09291c1 / C09 9870d73a / C10 5cea9445 / C11 0f1e7b16 / C12 a5a17fd9 / C13 5a0cb284 / C14 111a2ce1 / C15 b0360cc9 / C16 3cd9d2fb / C17 f767e158 / FEA01 0f0c2d14`。
- C-04b 工作树 blob `806f942d…` vs HEAD `201c8369…`（预期 DIFF）；M2-C1 工作树 `1ec38cc9…` vs HEAD `6690606c…`（0/18，记录型登记）。

## 6. 核对 5：P2/P3 处置

| 项 | 实测 | 判定 |
|---|---|---|
| P2-1 冻结记录 §4A | `:122-126` 已写明 R-1“契约谓词文字已补、代码实现未改 → 契约与实现当前不一致”；R-6 闭合、R-7 落地；上表历史读法不改写 | **已收紧** |
| P2-1 EV §6 | `:66` 明确“R-1 侧契约与实现当前不一致”“不得说本包全部文字与实现一致” | **已收紧** |
| P2-1 载体 §3 | `:65-66` 有 R-1 收窄句；但 `:63-64` 仍保留“改动仅让文字与**现行实现**……一致”的过宽句 | **部分**（P2-1） |
| 版本引用（r1 P3-1 指定项） | M2-C1 `:797` → rev 2.14/2.15；`:936`/`:940`/`:974` → C-04b v1.2 §2.1；C-04b §2.1 region 数组已去版本标签 | **已修**（但见 P3-1 的新残留） |
| P3-2 循环措辞 | C-04b `:74`、M2-C1 `:819` 已改为“`inventory_digests` 的键集合与顺序必须与同一请求的 `book_ids` 一致” | **已修** |
| P3-3 EV code-drift 日志 | `verification/FEA-12-CORE-C04B-RESIDUAL-2/logs/code-drift.log` 存在，**0 字节** | **已补** |
| P3-4 RESIDUAL-3 卡 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md:33` 已改为“R-2/R-3/R-4/R-5/R-8 的**契约文字**由 RESIDUAL-2 修正；本卡不重复改”，无“已解决”断言 | **已修** |

## 7. 核对 6：记录一致性

- **一致面**：§1 pin/blob、§1B v1.2 行、§2 条件 7 **⏳ 待复核**、§4C 两契约 sha、§4A append-only 状态、§5 变更记录、矩阵状态行/第 4 行、载体 §6/§7 在“pin 与待复核状态”上互不矛盾。
- **没有**「8 项全部关闭」「R-1 已修复」：冻结记录 §4A、EV §6、载体 §3/§7、任务卡 AC-6 均明确 R-1 代码未改、L-3 仍有效、归 RESIDUAL-3；搜索未发现禁用断言。
- **不一致面**（已计入 P2-2/P3-2）：
  - EV §2 `:31`、§4 `:55` 仍写 M2-C1 **11/7**，而同目录 `logs/diffstat.log` 实测 **19/15**；
  - 载体 §7 `:96` 仍写两文件 `+37/−22`，实测两文件 **+45/−30**（7 文件合计 `+83/−43`）；
  - `logs/pins.log` 仍显示 `OK C04b f5b4af88feab`（r1 旧字节），`logs/check*.log` 时间戳早于返修（`sha-check.log`/`diffstat.log` 已是新字节）；EV §4 把它们当作最终字节证据；
  - 载体 §6 `:88`、EV §5 `:61`、矩阵 `:22` 仍写 r1“待派/待回填”，而 r1 报告已存在且为 `changes_requested`（r2 即本报告）；
  - 冻结记录 §4C `:109`、载体 §2B、EV §2、任务卡 AC-2 `:57` 的 M2-C1 清单仍是 9 处（`:18`/`:30`/`:814/:815/:819`/`:953/:954`），**未列** `:972` 的 PD-01 正文修改；且这些行号是插入前编号（现行应为 `:32`/`:818/:819/:823`/`:957/:958`）。

## 8. 核对 7：门禁

| 检查 | 命令 | 实测 | 判定 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；exit 0 | PASS |
| check 默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；exit 0 | PASS |
| check taskpath | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | 同上；exit 0 | PASS |
| whitespace | `git diff --check` | 无输出；exit 0 | PASS |
| 代码漂移 | `git diff --name-only -- src apps tests` | 空 | PASS |

- **未跑**：全量 pytest、全量 .NET、GUI/e2e、真实回收站 D 流程。本卡是纯文档 UNFREEZE（`src/apps/tests` 零 diff），这些不在本卡门禁内；本报告不据此宣称运行时通过。
- 只跑了一个**只读探针**（§2.4）验证 representative 的 artifact fallback；探针不写仓库、只写仓外 workspace 临时 DB。

## 9. Diff 表（精确）

### 9.1 C-04b（`git diff --numstat` = 26/15）

| hunk | old→new | 内容 | 判定 |
|---|---|---|---|
| 1 | `:3-4` → `:3-4` | 状态行 v1.2、日期行补 v1.2 | OK |
| 2 | `:14` → `:14-24` | §0 标题改“修订摘要（v1.2 / v1.1）”；新增 v1.2 摘要；v1.1 摘要降 `###` | OK（摘要措辞见 P2-1） |
| 3 | `:18` → `:28` | R-1 谓词 + R-3 representative | **P1-1：artifact fallback 错** |
| 4 | `:21` → `:31` | 单条 manifest 取值 | OK |
| 5 | `:28-32` → `:38-42` | §1 表行号→节名 | OK |
| 6 | `:44` → `:54` | R-2 “不得在同一请求内混用两种 digest 语义” | OK |
| 7 | `:53` → `:63` | §2.1 DTO：R-1 谓词 + representative 指针 | 谓词 OK；指针指向 P1-1 |
| 8 | `:64` → `:74` | 首确认“请求 `book_ids`” | OK |
| 9 | `:69` → `:79` | 单条来源 `inventoryDigests[bookId]` | OK |
| 10 | `:71` → `:81` | 单条 manifest 取值 | OK |
| 11 | `:144` → `:155` | §6 变更记录 v1.2 | OK（摘要措辞见 P2-1） |

### 9.2 M2-C1（`git diff --numstat` = 19/15）

| hunk | old→new | 内容 | 判定 |
|---|---|---|---|
| 1 | `:17` → `:18-19` | rev 2.15 banner | OK（representative 措辞见 P2-1） |
| 2 | `:29` → `:32-33` | history 2.15 | OK（representative 措辞见 P2-1） |
| 3 | `:136` → `:140` | C-04b v1.1→v1.2 | OK |
| 4 | `:169` → `:173` | 命令表 C-04b v1.1→v1.2 | OK |
| 5 | `:791` → `:795` | §5.11.1a 标题 2.14/2.15 | OK |
| 6 | `:793` → `:797` | “现行规则以 2.14 + 2.15 为准” | OK |
| 7 | `:814-815` → `:818-819` | 来源 + 校验措辞 | OK |
| 8 | `:819` → `:823` | retry 仅批量标注 | OK |
| 9 | `:922` → `:926` | §5.13 标题 C-04b v1.2 + rev 2.14/2.15 | OK |
| 10 | `:924` → `:928` | 目标 wire 行 C-04b v1.1→v1.2 | OK（同段仍有 v1.1，见 P3-1） |
| 11 | `:932` → `:936` | `bookIds` camelCase 注释 v1.2 | OK |
| 12 | `:936` → `:940` | 正文 v1.1→v1.2 | OK |
| 13 | `:953-954` → `:957-958` | region 数组去 `separate/detached` + artifact 谓词/representative | 谓词 OK；representative 见 P1-1/P2-1 |
| 14 | `:968` → `:972` | §5.13 PD-01 正文补 `media_artifacts.book_id = 本书` + representative 指针 | **P1-2 关闭**；representative 见 P1-1 |
| 15 | `:970` → `:974` | digest 算法 C-04b v1.1→v1.2 | OK |

- 无第 12 个 C-04b hunk、无第 16 个 M2-C1 hunk；无新命令/字段/错误码/能力/`PROTOCOL_MINOR`/wire minor 变化。

## 10. Findings

### P1-1（阻断）representative 的 artifact fallback 仍与实现不一致

**位置**：`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:28`（§0 第 1 条）；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:972`（“否则 artifact 数组首项”，指向同一排序数组）；相关指针 `:63`、M2-C1 `:958`。

**契约文字（工作树）**：
> **若无可见 region current**，则取按字典序排序的 `currentArtifactRevisionIds` 的**首项**；均无 null

**实现（HEAD 工作树）**：
- `core_service.py:1891-1898` 按 `raw["artifact_current_pointers"]` 顺序构造局部 list；
- `:1904-1906` 仅把 `sorted(set(...))` 写入 `inventory["current_artifact_revision_ids"]`；
- `:1929-1930` fallback 用局部 list `[0]`；
- `library.py:1186-1187` 的 artifact pointer 顺序是 `chapter/page/artifact_type/artifact_id`，不是 revision id；
- `:1858-1861` docstring 写“first artifact current pointer”；
- `artifact_revision_id = uuid.uuid4().hex`（`artifacts.py:154`），与阅读序无关。

**实测**：见 §2.4；DTO `["aaa","zzz"]`，代表值 `"zzz"`（pointer 首项），契约要求 `"aaa"`。

**为什么是 P1**：
1. 这是 normative text 的规则要素，不是摘要；本卡 R-3 的目标就是“写死且与实现一致”。
2. 它会使未来实现者按契约实现出与现行 Core 不同的展示值；虽然仅展示、不进 digest，但正是 r1 P1-1 同一类“规则被写错”的问题。
3. v1.2/载体“只改文字、与现行实现一致”的自述在 R-3 上不成立；§4A“R-3 的契约文字已由 v1.2 修正”也过宽。
4. r1 与 scope review 的“该列表已排序”是误读（§2.3），不能作为“已核实”的依据。

**建议修复**：优先方案 A（把文字改成“第一个 artifact current pointer（阅读序 `... artifact_type, artifact_id`）”），同步 M2-C1 `:972`、C-04b §0 摘要/§6、冻结记录 §4C、载体 §2A/§3、EV §2；若坚持“字典序最小”，走方案 B（另立/扩实现卡改代码 + 多 artifact 测试，不能写成本卡“只改文字”）。

### P2-1（非阻断）banner/history/摘要/载体仍保留“字典序最小”的笼统表述

**位置与现状**：
- M2-C1 `:18` banner、`:32` history：“（……representative 取**字典序最小项**、仅展示、不进 digest）”——对 region 分支不成立（实现是阅读序首个 lineage-visible）。
- C-04b `:18-19`（v1.2 摘要）：“写死 representative 排序（**字典序最小**、仅展示、不进 digest）”；`:155`（§6 变更记录）同。
- 冻结记录 §4C `:109`：“R-3 删无定义术语 `separate/detached` + 写死 representative 排序（**字典序最小**、仅展示、不进 digest）”。
- 载体 §2A `:31`：“……取按字典序排序的 `currentArtifactRevisionIds` 的**首项**……”（即 P1 的错误来源）；载体 §3 `:66` 称“其余 R-2/R-3/R-5/R-8 的文字与现行实现一致（representative 规则……）”。
- 载体 §3 `:63-64` 仍写“改动仅让文字与**现行实现**……一致”——`P2-1` 的返修说明称已删去过宽表述，但该句仍在（`:65-66` 的 R-1 收窄句只是部分补救）。

**影响**：非规范段，不改变 wire/行为；但与修正后的 §0 第 1 条及实现冲突，读者会再次得到“representative=字典序最小”的错误规则。P1 修复时应同步改为“region=阅读序首个 lineage-visible；artifact=首个 artifact pointer（或按最终裁决）”，并在载体 §3 删除/改写 `:63-64` 的过宽句。

### P2-2（非阻断）EV/载体的 diff 数字与 pin/check 证据早于返修字节

**实测 vs 记录**：
- `git diff --numstat`：C-04b **26/15**、M2-C1 **19/15**；EV §2 `:31` 与 §4 `:55` 仍写 M2-C1 **11/7**（r1 旧值），与同目录 `logs/diffstat.log` 的 `19 15` 自相矛盾。
- 载体 §7 `:96` 仍写“C-04b 与 M2-C1 两文件（**+37/−22** 合计）”；实际两文件 **+45/−30**（7 文件合计 `+83/−43`）。
- `logs/pins.log` 仍是 `OK C04b **f5b4af88feab**`（r1 旧 sha），`logs/check.log`/`check-taskpath.log` 时间戳 `03:42`，早于返修完成（C-04b `03:57:52`、M2-C1 `03:58:28`、冻结记录 `03:58:37`）；EV §4 把它们当作最终字节的门禁证据。`sha-check.log`/`diffstat.log` 已是新字节，但 pin/check 日志没有重跑。
- 我本次重跑 `verify_pins`（18/18，C04b `23398a22`）与 `check`（PASS）均通过，所以**门禁结论不受影响**；但证据链与最终字节不一致，closeout 前应重生成 `pins.log`/`check*.log` 并改 EV 数字。

### P3-1（非阻断）M2-C1 仍有 3 处 rev 2.14 / C-04b v1.1 的现行状态引用

- `:28`：“状态：文档 rev `2.14`；……”——现已 rev 2.15，应改为 2.15 或 2.14/2.15。
- `:140`：“文档 rev 2.14（§5.13 rev 2.14 保护完整性）不等于 Core 运行常量……”——应加 rev 2.15。
- `:928`：“本节 additive 登记 **C-04b v1.1** §2.0–§2.2 已冻结的只读预览协议；……文档 rev **2.14** 与运行常量分离……”——同句后半已写 C-04b v1.2，标题也是 v1.2/2.14/2.15，前后不一致。
- 说明：r1 P3-1 指定的 `:797`、`:936`、`:940`、`:974` 与 C-04b §2.1 region 标签**已修**；以上 3 处是 r1 未列的新残留，属同一类版本引用精度问题。
- `:1461` 的“M2-C1 rev 2.13 + rev 2.14 protection completeness”是 §12 的历史/实质修订描述；rev 2.15 无规则变更，可不改，但建议一并核对。

### P3-2（非阻断）记录未覆盖 `:972` 且行号仍是插入前编号；r1 状态仍写“待派/待回填”

- **清单漏项**：冻结记录 §4C `:109`、载体 §2B、EV §2、任务卡 AC-2 `:57` 的 M2-C1 修改清单仍是 9 处（`:18` banner、`:30` history、`:814/:815/:819` 来源/校验、`:953/:954` DTO），**未列** `:972` 的 PD-01 正文补 `book_id`（P1-2 的实际修改点）。r1 §4 P1-2 已建议把清单从 9 处补为 10 处；本包未同步。
- **行号漂移**：上述清单使用插入前行号；banner/history 插入后，现行行号为 `:32`、`:818/:819/:823`、`:957/:958`，并新增 `:972`。冻结记录/载体/任务卡若以行号定位，应按现行工作树更新（或明确“base `d91d9b6cc` 行号”）。
- **r1 状态**：载体 §6 `:88`“r1：待派”、EV §5 `:61`“r1：待回填”、矩阵 `:22`“①v1.2 独立 byte-level 复核 **⏳ 待派**”均与事实不符——r1 报告已存在且 verdict 为 `changes_requested`；本 r2 报告也已完成。应改为“r1 changes_requested（P1=2/P2=1/P3=4）→ 返修 → r2 …”，并在 approved 后回填最终 session/结论。
- 任务卡 `reviewer:` 字段当前只指向 r1 报告；r2 入库后应补 r2 路径或改为“r1/r2 见 …”。

## 11. 结论

**changes_requested**。本包在字节、pin、零漂移、门禁和 P1-2 上均已达标；但在以下一项修复并重跑记录/门禁前，不应把当前字节作为 v1.2/rev 2.15 的最终冻结字节：

1. **P1-1（阻断）**：把 C-04b §0 第 1 条的 artifact fallback 改成与实现一致的“首个 artifact current pointer（阅读序 `... artifact_type, artifact_id`）”，并同步 M2-C1 `:972`、C-04b §0 摘要/§6、冻结记录 §4C、载体 §2A/§3、EV §2；或者把“字典序最小”作为显式规则/代码变更另立卡（不能写成本卡“只改文字”）。
2. **P2-1**：修 P1 时同步清掉 banner/history/摘要/载体 §3 的“字典序最小”“与现行实现一致”过宽句。
3. **P2-2**：重生成 `pins.log`/`check*.log`，把 EV §2/§4 的 M2-C1 `11/7` 改为 `19/15`，把载体 §7 的 `+37/−22` 改为实际值。
4. **P3-1/P3-2**：更新 M2-C1 `:28`/`:140`/`:928` 的版本引用；把 `:972` 加入 M2-C1 修改清单并更新行号；把 r1 状态从“待派/待回填”改为实际结果，r2 回填后重签。

修复后两契约 sha 都会变，需重新登记 §1/§1B/§4C/§5 与载体 §7、重跑 `verify_pins.ps1`（18/18；其余 17 不变）与 `check.ps1`，再由独立上下文复核新字节。**当前本报告不批准任何字节**；P0=0 只表示未发现数据丢失/保护失效级缺陷，P1=1 足以阻断冻结。

## 12. 真实性声明

- **身份与独立性**：我是本次委派的 fresh subagent，session `1975a972-5b34-4267-91cd-f3d16e3585c7`；未参与 C-04b v1.2 / M2-C1 rev 2.15 的起草、实施或返修，未参与 r1 复核，未参与此前 C-04b/CORE 实现或 residual scope review。`reviewed_head=d91d9b6cc4afef307b0662055812c129468054a0`，只读该工作树。
- **写入范围**：本报告 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r2.md` 是本次唯一写入仓库的文件（untracked）；仓外只写 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review-r2\`（探针脚本/日志）。未修改任何 tracked 文件、契约、记录、矩阵、载体、任务卡、源码或测试；未 `git add`/`commit`/`push`/`reset`/`checkout`/`stash`。
- **字节未变**：审查前后两契约复算仍为 C-04b `23398a22…`、M2-C1 `3c74d946…`；`git diff --name-only` 的 7 个 tracked 文件集合相同；新增的只有本报告（以及本包既有 untracked 证据目录）。
- **实测与未跑**：§5/§8 的数字均来自本次命令；§8 明确列出未跑的 pytest/.NET/GUI/e2e。未把既有 `verification/` 日志当作本次实跑；未把 `verify_pins` 18/18 当作语义正确性的替代。§2.4 的探针只读调用 Core preview，不写仓库；其输出已保存到仓外日志。
- **不夸大**：本报告没有说“8 项 residual 全部关闭”“R-1 已修复”“C-04b/M2-C1 已最终冻结”；只确认字节/pin/门禁的机械事实，并对 P1-1/P2/P3 明确要求修改。`verify_pins` 只证明 pin 行与当前文件自洽，不覆盖 M2-C1（0/18），也不替代本报告对 representative/谓词的语义复核。
- **限制**：本报告未逐行重读 C-04b/M2-C1 全文的每一句历史注释，只对本次 diff、§5.13/§5.11.1a 相关段、R-1/R-2/R-3/R-5/R-8 语义点及实现/测试/探针事实做逐项核对；对未涉及本次 diff 的条款按“零 diff”采信，不再逐条重审。
