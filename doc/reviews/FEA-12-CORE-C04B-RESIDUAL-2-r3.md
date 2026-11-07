---
task: FEA-12-CORE-C04B-RESIDUAL-2
title: C-04b v1.2 + M2-C1 rev 2.15 UNFREEZE：独立 byte-level 复核（r3 / 第二轮回修后最终字节）
reviewer: fresh subagent (r3)
session: 98692074-315d-46d5-ba77-37e1df07f093
reviewed_head: d91d9b6cc4afef307b0662055812c129468054a0
reviewed_worktree_sha256:
  C-04b: 4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52
  M2-C1: a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e
verdict: approved
p0: 0
p1: 0
p2: 3
p3: 4
date: 2026-11-08
---

# C-04b v1.2 + M2-C1 rev 2.15 UNFREEZE：独立 byte-level 复核（r3 / 第二轮回修后最终字节）

> 只读复核。我是本次委派的 fresh subagent（session `98692074-315d-46d5-ba77-37e1df07f093`），**未参与**本包起草、
> **未参与** r1/r2 复核、**未参与** C-04b/CORE 实现或返修。未修改生产代码、测试、契约、冻结记录、矩阵、载体或任务卡；
> 未 `git add`/`commit`/`push`/`reset`/`checkout`/`stash`。本报告 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r3.md`
> 是本次唯一写入仓库的文件（untracked）；仓外只写
> `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review-r3\`（`probe-representative.py` 与 `.log`）。

## 0. 结论先行

**verdict: approved**——P0=0、**P1=0**、P2=3、P3=4（均为记录/证据精度，不阻断冻结）。

**两项 P1 均已真正关闭，且用只读探针独立复现**：

1. **P1-1 关闭**。C-04b v1.2 §0 第 1 条（`:28`）现为「按阅读序的第一个 lineage-visible region 的 current（排序键
   `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, region.reading_order, region_id`，
   过 lineage guard）；**若无可见 region current**，取**首个 artifact current pointer**（pointer 顺序
   `... artifact_type, artifact_id`；**非字典序**）；均无 null；仅展示、不承担绑定、不进 digest」——与
   `core_service.py:1907-1930` + `library.py:1158-1190` **逐要素等价**。我的探针三案全部命中预期：
   无 region + 2 artifact（DTO `["aaa","zzz"]`）→ 代表值 **`zzz`**（pointer 首项，非字典序最小 `aaa`）；
   rg1 hidden（阅读序 1）+ rg2 visible（阅读序 2）→ **`rr2`**；仅 hidden region current + 1 artifact →
   **`zzz`**（证明 fallback 条件是「无**可见** region current」，而非「无 region current」）。
2. **P1-2 关闭**。M2-C1 `:972` 已含 `media_artifacts.book_id = 本书`；全文再无「artifact 谓词=`current_revision_id` 非空」
   缺 `book_id` 的现行规范句（精确检索 `artifact 谓词|谓词=current_revision_id` 零命中；`:58`/`:171` 的「谓词」是
   BookSummary COUNT 谓词，与 artifact 无关；`:1461` 不含「谓词」）。

**机械面全部干净**：两契约 `Get-FileHash` 与 `git hash-object` 均与题面/冻结记录一致（**MATCH**）；`verify_pins.ps1`
**18/18 PASS**（`OK C04b 4b304c0c315f`）；18 份映射中**其余 17 份 blob 与 HEAD 逐项相同**，仅 C-04b 变化；
M2-C1 **不在映射（0/18 机械 pin）**，§1B/§4C/载体 §7 三处登记与实测一致；`git diff --numstat` = C-04b **26/15**、
M2-C1 **20/16**（与题面一致）；`git diff --check` 干净；`src/**`、`apps/**`、`tests/**` 零 diff；`check.ps1`
默认与 `-TaskPath` 均 **PASS (3 warnings)**；`logs/` 已按返修后字节重跑（`pins.log` 为 `4b304c0c…`、`diffstat.log`
为 `26 15` / `20 16`、check 双日志 04:15 重写）。

**仍存在的非阻断残余**（不改变「approved」，但 closeout 前应清）：三处 P2 均为**记录/载体/EV 仍沿用返修前的
「字典序最小」措辞与旧 diff 数字**，与最终契约及实现冲突；另有 4 项 P3 精度问题（其中载体 §2B 有一处字面 `` `n ``
把两行表格并成一行）。详见 §9。

## 1. 基线与只读事实

- 仓库/分支/HEAD：`G:\CODEX\New Manga`，`main`，`d91d9b6cc4afef307b0662055812c129468054a0`；任务卡
  `base_commit: d91d9b6cc` 与 HEAD 一致。
- 开始/结束时 `git status --porcelain` 的 tracked 集合相同（7 个）：
  `M doc/REBASELINE_PLAN.md`、`M doc/STATUS.md`、`M doc/TASK_LEDGER.md`、
  `M doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`M doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`、
  `M doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`M doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`。
  untracked：载体、r1/r2 报告、RESIDUAL-2/3 两张卡、`verification/FEA-12-CORE-C04B-RESIDUAL-2/**`。
- 只读手段：`Get-FileHash`、`git hash-object`、`git rev-parse HEAD:<path>`、`git diff`/`--numstat`/`--name-only`/`--check`、
  `Select-String`、`verify_pins.ps1`、`check.ps1`、逐行读取 `src/bootstrap/core_service.py`、
  `src/infrastructure/sqlite/library.py`、`src/application/library/service.py`、
  `src/application/sources/lineage.py`、`tests/core/test_core_delete_preview_commands.py`，以及一个只读探针（见 §2.4）。
- 本报告行号：除注明「旧/HEAD」外，均指**当前工作树**行号；diff 的 old/new 为 `git diff` hunk 行号。

## 2. 核对 1：P1-1 representative——**已关闭（逐要素等价 + 探针复现）**

### 2.1 逐要素对照（C-04b §0 第 1 条 `:28` 与 M2-C1 `:958`/`:972`）

| 要素 | 契约文字（最终字节） | 现行实现 | 判定 |
|---|---|---|---|
| region 分支排序 | 「按阅读序的第一个 lineage-visible region 的 current」，排序键 `chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, region.reading_order, region_id` | `core_service.py:1912-1928` 按 `raw["region_current_pointers"]` 顺序遍历；顺序来自 `library.py:1172-1173` 的同序 `ORDER BY` | **MATCH** |
| lineage-visible 过滤 | 「并过 lineage guard 判可见」 | `:1916-1926` 调 `guard.is_region_readable(...)`；不可见/异常跳过 | **MATCH** |
| fallback 触发条件 | 「**若无可见 region current**」 | `:1929` `current_revision_id is None`（可见 pointer 扫完仍无值） | **MATCH**（探针 C 证伪旧读法） |
| artifact 取值 | 「**首个 artifact current pointer**（pointer 顺序 `... artifact_type, artifact_id`；**非字典序**）」 | `:1930` 取**未排序局部 list** `current_artifact_revision_ids[0]`；该 list 在 `:1891-1898` 按 pointer 顺序追加、仅按 revision id 去重；无 `sorted` | **MATCH**（探针 A 复现 `zzz`） |
| 去重 | 未显式写（受保护表达=数组长度） | `:1895-1897` 按 revision id 去重 | 不冲突（首项不受去重影响） |
| 仅展示/不绑定/不进 digest | 「**仅展示、不承担绑定、不进 digest**」 | `:1931` 单独写入 `current_revision_id`；digest canonical 输入 `src/application/library/service.py:297-320` **不含**该字段 | **MATCH** |

- 排序键字面：`library.py:1172-1173` = `c.sort_order, c.import_order, c.chapter_id, p.sort_order, p.page_id, r.reading_order, r.region_id`；
  `:1186-1187` = `c.sort_order, c.import_order, c.chapter_id, p.sort_order, p.page_id, ma.artifact_type, ma.artifact_id`。
  契约去掉了表别名，键序与语义完全一致。
- `core_service.py:1858-1861` 的 docstring 亦写 "falling back to the **first artifact current pointer**"，与最终文字同向。
- 「字典序排序去重」用于两个 **DTO 数组**（`:1901-1906` 的 `sorted(set(...))`），与 §2.1「受保护 artifact 表达=数组长度」
  一并成立；代表值不再声称字典序。**旧文「按字典序排序的 `currentArtifactRevisionIds` 的首项」已从契约中消失**
  （C-04b `:28` 明写「非字典序」；`:63` 改为「取值规则见 §0 第 1 条」）。

### 2.2 M2-C1 侧同步

- M2-C1 `:958`：「representative 取值规则见 C-04b v1.2 §0 第 1 条（阅读序首个 lineage-visible region current，
  否则首个 artifact current pointer；仅展示、不进 digest）」——**与实现一致**。
- M2-C1 `:972`：同句复述「（阅读序首个 lineage-visible region current，否则**首个 artifact current pointer**；
  仅展示、不进 digest）」——**与实现一致**。
- M2-C1 `:18`/`:32`（banner/history）不再写「字典序最小」，改为「representative 规则见 C-04b v1.2 §0 第 1 条」——
  指向单一定义源，**可接受**（消除了 r2 P2-1 的「笼统写字典序最小」）。

### 2.3 只读探针（独立复现；不改仓库）

探针：`G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review-r3\probe-representative.py`
（只读调用 `PreviewPermanentDeleteBooks`；每案独立临时 DB，位于仓外 workspace；日志同名 `.log`）。
复用 `tests/core/test_core_delete_preview_commands.py` 的 fixtures/seed 助手，三案：

| 案 | 构造 | 实测 | 契约预期 | 判定 |
|---|---|---|---|---|
| A | 1 书 1 页、**无 region**、2 artifact：`mask→zzz`（pointer 首）、`translated→aaa` | `currentArtifactRevisionIds=["aaa","zzz"]`；`currentRevisionId=**zzz**` | 「首个 artifact current pointer」「非字典序」→ `zzz` | **命中**（若按字典序最小则为 `aaa`，与实现不符） |
| B | rg1 阅读序 1 **hidden**（rr1）+ rg2 阅读序 2 **visible**（rr2，lineage 指向当前 binding） | `currentRegionRevisionIds=["rr1","rr2"]`；`currentRevisionId=**rr2**` | 「按阅读序第一个 lineage-visible」→ `rr2` | **命中**（证明按阅读序遍历 + 可见性过滤，隐藏项不入代表值但仍计入绑定集合） |
| C | 仅 rg1 **hidden**（rr1）+ 1 artifact current `zzz` | `currentRevisionId=**zzz**` | 「无**可见** region current」即回退 → `zzz` | **命中**（若条件写成「无 region current」，隐藏项会压住回退，输出应为 `null`） |

结论：**最终 normative 文字与现行实现逐要素等价；P1-1 关闭**。r2 的复现（DTO `["aaa","zzz"]`→`"zzz"`）在本轮最终字节下
仍然成立，说明返修确实把文字改到了实现一侧，而不是把实现解读迁就文字。

### 2.4 该文字是否构成「改规则」

- HEAD `:18` 原文为「首个 lineage-visible region current；无可见 region current 取首个 artifact current」——
  artifact 分支**未写排序**（欠定义）。最终文字补上「pointer 顺序 / 非字典序」，是对既有实现的**写死**，不是行为变更：
  探针 A 的 `zzz` 在 HEAD 实现下亦为 `zzz`（代码零 diff 可证）。
- 因此 C-04b `:16` 自述「只纠正措辞与谓词文字，不改任何规则/字段名/错误码/语义」在 R-3 上**成立**；r1 的 P1-1
  （把 region 分支改成「字典序最小」）已被回退。

## 3. 核对 2：P1-2——**已关闭**

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:972`（§5.13 PD-01 段）现为：
  > artifact 成员谓词=**`media_artifacts.book_id = 本书`** 且 `current_revision_id` 非空、不按可见性过滤（rev 2.15 补）；……
  > representative `currentRevisionId` 取值规则见 C-04b v1.2 §0 第 1 条（阅读序首个 lineage-visible region current，否则**首个 artifact current pointer**；仅展示、不进 digest）。
- 同节 DTO 注释 `:958` 亦含 `media_artifacts.book_id = 本书`；banner `:18`、history `:32` 亦然。
- 全文精确检索 `artifact 谓词` 与 `谓词=current_revision_id`：**M2-C1 内零命中**。（旧谓词文字仍作为**历史描述**存在于
  别处：冻结记录 §4A 表 R-1 行及「现行权威读法」栏写的是 v1.1 时点状态，而 §4A:126 已声明该栏「保留 v1.1 读法、
  不改写」；C-04b `:18`/`M2-C1:18`/`:32` 的 `separate/detached` 只是「已删除该术语」的变更记录。二者均非现行规范句。）
- `:58`/`:171` 命中的「谓词」是 `ListBooks` 的 COUNT 谓词（`BookSummary.page_count`），与 artifact 无关；
  `:1461`（§12 状态表）不含「谓词」，只写「artifact current」，不构成缺谓词的规范句。
- 结论：M2-C1 内部「DTO 注释 vs 正文」的旧冲突已消除；**0/18 机械 pin 的漂移风险由本轮 byte-level 复核覆盖**。

## 4. 核对 3：语义零变更——**PASS**

- `git diff --numstat`：C-04b **26 插入 / 15 删除**、M2-C1 **20 插入 / 16 删除**（与题面预期一致；EV §4:55 与
  `logs/diffstat.log` 亦为 `26 15` / `20 16`）。
- `git diff -U0`：C-04b **11 个 hunk**、M2-C1 **16 个 hunk**，逐 hunk 核对均为**措辞/版本引用/谓词文字/行号→节名**：

  | 契约 | hunk（old→new） | 内容 | 判定 |
  |---|---|---|---|
  | C-04b | `:3-4` | 状态行 v1.2 + 日期行 | OK |
  | C-04b | `:14`→`:14-24` | §0 标题 + v1.2 摘要块（v1.1 降 `###`） | OK |
  | C-04b | `:18`→`:28` | R-1 谓词 + R-3 representative | OK（P1-1 已修） |
  | C-04b | `:21`→`:31` | R-8 单条 manifest | OK |
  | C-04b | `:28-32`→`:38-42` | §1 表行号→节名 | OK |
  | C-04b | `:44`→`:54` | R-2 digest 语义不混用 | OK |
  | C-04b | `:53`→`:63` | §2.1 DTO 谓词 + representative 指针 | OK |
  | C-04b | `:64`→`:74` | R-5 请求 `book_ids` | OK |
  | C-04b | `:69`→`:79` | R-5 单条来源 `inventoryDigests[bookId]` | OK |
  | C-04b | `:71`→`:81` | R-8 单条 manifest 取值 | OK |
  | C-04b | `:144`→`:155` | §6 变更记录 v1.2 行 | OK |
  | M2-C1 | `:17`→`:18-19` | rev 2.15 banner | OK |
  | M2-C1 | `:26`→`:28` | 状态行 rev 2.15 | OK |
  | M2-C1 | `:29`→`:32-33` | history 2.15 | OK |
  | M2-C1 | `:136`→`:140`、`:169`→`:173` | `C-04b v1.1`→`v1.2` | OK |
  | M2-C1 | `:791`→`:795`、`:793`→`:797` | §5.11.1a 标题 + 现行规则声明 | OK |
  | M2-C1 | `:814-815`→`:818-819`、`:819`→`:823` | 来源 + 校验顺序 + retry 仅批量 | OK |
  | M2-C1 | `:922`→`:926`、`:924`→`:928`、`:932`→`:936`、`:936`→`:940` | §5.13 标题/目标 wire/`bookIds` 注释/正文 rev | OK |
  | M2-C1 | `:953-954`→`:957-958` | region 数组去 `separate/detached` + artifact 谓词 + representative | OK |
  | M2-C1 | `:968`→`:972` | §5.13 PD-01 段补 `book_id` + representative | OK（P1-2 已修） |
  | M2-C1 | `:970`→`:974` | digest 算法 rev 引用 | OK |

- **未发现**：校验顺序变化（§5.11.1a 仍单条=逐书值 / 批量=集合级+逐书 map / retry 集合级仅批量）；拒绝条件与失败分类
  变化（缺/多 key → `INVALID_REQUEST`；语义失败 → `BOOK_DELETE_STALE_PREVIEW`，与 HEAD 一致）；字段名/错误码/能力
  增删；`PROTOCOL_MINOR` 变化（`core_service.py:320` 仍 `PROTOCOL_MINOR = 3`）；wire minor 变化（preview 仍 11、
  trash 仍 13、既有删除仍 10）。§2.3 错误码 12 行未动。
- C-04b 的 `separate/detached` 只剩**变更记录**（`:18` 摘要、`:155` 表）在描述「删除了该术语」，规范面已无该术语。

## 5. 核对 4：pin 账——**PASS**

| 项 | 实测 | 与登记 | 判定 |
|---|---|---|---|
| C-04b SHA-256 | `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52` | 冻结 §1:15 同值 | **MATCH** |
| C-04b blob | `a30e4080116d01512977eca40de1c43ea7244a64` | 冻结 §1:16、§1B:31、载体 §7 同值 | **MATCH** |
| M2-C1 SHA-256 | `a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e` | §1B:31（前缀）、§4C:111（全值）、载体 §7:103（全值） | **MATCH** |
| M2-C1 blob | `cb8eeb21279ff3dd23ad7c1cec6c171b211592e9` | §1B:31、载体 §7:103 | **MATCH** |
| 18 份映射 | **17 份 SAME + C-04b DIFF（预期）** | — | **PASS** |
| `verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；`OK C04b 4b304c0c315f`；exit 0 | — | **18/18 PASS** |
| M2-C1 机械 pin | `verify_pins.ps1:6-13` 的 18 项 map **无 M2-C1** | — | **0/18 机械 pin** |

- 17 份 SAME 的 blob 前缀（本次实算）：`C01b 7127d064 / C02 fcea994a / C03 81738c04 / C05 32d039c0 / C06 b537e76d /
  C07 cd51f8e6 / C08 b09291c1 / C09 9870d73a / C10 5cea9445 / C11 0f1e7b16 / C12 a5a17fd9 / C13 5a0cb284 /
  C14 111a2ce1 / C15 b0360cc9 / C16 3cd9d2fb / C17 f767e158 / FEA01 0f0c2d14`。
- C-04b 工作树 `a30e4080…` vs HEAD `201c8369…`（预期 DIFF）；M2-C1 工作树 `cb8eeb21…` vs HEAD `6690606c…`
  （不在映射，记录型登记）。
- 精确表述：18 份映射中**仅 C-04b 变化**；M2-C1 不在映射但已变化，靠 §1B/§4C/载体 §7 三处手工 sha 防漂移——
  三处与实测**逐字符一致**，且与 scope review §3.3 的「C-04b 1/18 + M2-C1 0/18」口径一致。

## 6. 核对 5：P2/P3 处置——**大部分已修；残余 3×P2 + 4×P3（非阻断）**

| r1/r2 项 | 现状（实测） | 判定 |
|---|---|---|
| r2 P1-1（artifact fallback） | C-04b `:28` 改「首个 artifact current pointer；**非字典序**」；M2-C1 `:958`/`:972` 同步 | **已修（关闭）** |
| r1 P1-2（`:972` 缺 book_id） | `:972` 已补 `media_artifacts.book_id = 本书` | **已修（关闭）** |
| r2 P2-1「banner/history/摘要不再写字典序最小」 | 两契约 banner/history/§0 摘要/§6 **已清**；但**冻结 §4C:109、载体 §2A:31、载体 §2B:51、EV §2:27 仍写「字典序最小/排序数组首项」** | **部分**（P2-1） |
| r2 P2-1「载体 §3 无『与现行实现一致』过宽句」 | 载体 §3:65-66 已把 **R-1** 收窄为「契约与实现当前不一致」；但 `:63-64` 的「改动仅让文字与**现行实现**……一致」**仍在** | **部分**（P2-2） |
| r2 P2-2「EV/载体 diff 数字」 | 载体 §7:104 已改 `26/15 + 20/16`（两文件 **+46/−31**，实算正确）；**EV §2:31 仍写 M2-C1 `11/7`**，与 EV §4:55 及 `logs/diffstat.log` 的 `20/16` 自相矛盾 | **部分**（P2-3） |
| r2 P2-2「logs 重跑」 | 关键日志均于 **04:15-04:16** 按返修后字节重写：`pins.log`=`OK C04b 4b304c0c315f`、`diffstat.log`=`20 16`/`26 15`、`check.log`/`check-taskpath.log`=PASS、`sha-check.log`=新 sha、`code-drift.log` 0 字节、`unfreeze.diff` 62 KB；仅 `scope-changed.log`（03:42）与 `other-contracts-drift.log`（03:59）早于末轮返修，但二者分别记录「scope 文档变更」与「其余契约零 diff」，返修未触及这两项，结论仍成立 | **已修** |
| r1 P3-1 / r2 P3-1 版本引用 | M2-C1 `:28`（rev 2.15）、`:797`（2.14+2.15）、`:928`（v1.2 + rev 2.15）、`:936`/`:940`（v1.2）、`:972`/`:974`（v1.2）全部一致；C-04b §2.1 region 数组已去版本标签 | **已修**（新残 `:140`，见 P3-1） |
| r1 P3-2 循环措辞 | C-04b `:74`、M2-C1 `:819` 已改「`inventory_digests` 的键集合与顺序必须与**同一请求的** `book_ids` 一致」 | **已修** |
| r1 P3-3 code-drift 日志断引 | `logs/code-drift.log` 存在（0 字节=零 drift）；我本次独立 `git diff --name-only -- src apps tests` 亦为空 | **已修** |
| r1 P3-4 RESIDUAL-3「已解决」 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` 已改为「**契约文字**由 RESIDUAL-2 修正；本卡不重复改」 | **已修** |
| r1 P1-2 清单补 `:972` | **载体 §2B 与卡 AC-2 已含 `:972`**；冻结 §4C:109 与 EV §2 仍用插入前行号且**未列 `:972`** | **部分**（P3-3） |
| r2 P3-2 r1 状态「待派/待回填」 | 载体 §6:88-96 与 EV §5:61 已如实记 r1 `changes_requested`（P0=0/P1=2/P2=1/P3=4）→ r2 `changes_requested`（P0=0/P1=1/P2=2/P3=2）→ r3 待派；**矩阵 `:22` 仍写「⏳ 待派」** | **部分**（P3-4） |

- 版本引用专项（题面枚举项）：M2-C1 `:28` = `2.15` ✓、`:797` = `2.14 + 2.15` ✓、`:928` = `C-04b v1.2` + `文档 rev 2.15` ✓、
  `:936`/`:940`/`:972`/`:974` = `C-04b v1.2` ✓；C-04b §2.1 标签：region 数组无版本标签、artifact 数组标 `v1.2：`（指 v1.2
  的谓词补充），可读且不误导 → **一致**。

## 7. 核对 6：记录一致性/不夸大——**PASS（不夸大面干净）**

- **一致面**：§1 pin/blob（`:15`/`:16`）、§1B v1.2 行（`:31`）、§2 条件 7（`:68`，**⏳ 待复核**）、§4C（`:103-113`）、
  §4A append-only 状态（`:122-126`）、§5 变更记录（`:151`）、矩阵状态行 `:3`/第 4 行 `:22`、载体 §6/§7 在
  「pin、17 不变、0/18、待复核」上互不矛盾。
- **明确存在（正确口径）**：R-1 **代码未改**（仍 page/chapter join）→ **契约与实现当前不一致**、**L-3 仍有效**、
  归 `FEA-12-CORE-C04B-RESIDUAL-3`（§4A:123-125、载体 §3:65-66、EV §6:66、任务卡 `:61`）。
- **不存在**「8 项 residual 全部关闭」「R-1 已修复」的断言：对 5 份记录 + EV + 卡片检索 `8 项全部关闭|R-1 已修复|
  全部文字与实现一致|已对齐`，**全部命中均为「不得写…」的禁止句或 `L-3` 的「不得写已对齐/已修复」**，无一处是正面宣称。
- **不一致面**（已计入 P2-1/P2-2/P2-3 与 P3-3/P3-4）：
  - 冻结 §4C:109 仍写 R-3「写死 representative 排序（**字典序最小**…）」，与契约 `:28`（非字典序）及探针 A 矛盾；
    同行的 M2-C1 清单用 `:18/:30/:814/:815/:819/:953/:954`（插入前编号）且漏 `:972`；`:18`/`:30` 恰好仍指向 banner/
    history 节，属可读但基准混用。
  - 载体 §2A:31 仍写「取按字典序排序的 `currentArtifactRevisionIds` 的**首项**」，与载体自身 §6:94-96（「首个 artifact
    current pointer；**非字典序**」）**自相矛盾**。
  - 载体 §2B:51 仍写「写死 representative=**字典序最小**」。
  - EV §2:27 仍写「写死 representative 排序（**字典序最小**…）」；EV §2:31 的 M2-C1 numstat 仍为 `11/7`。
- 「R-7 已由 rev 2.15 banner/history 落地」「R-6 已闭合」的表述与 banner/history 实际字节（`:18`/`:32` 均写
  「retry 集合级规则明确**仅批量**」）一致 ✓。

## 8. 核对 7：门禁——**PASS**

| 检查 | 命令 | 实测 | 判定 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；exit 0 | **PASS** |
| check 默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；exit 0 | **PASS** |
| check taskpath | `... -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | 同上；exit 0 | **PASS** |
| whitespace | `git diff --check` | 无输出；exit 0（仅 Git LF→CRLF warning，非本包内容问题） | **PASS** |
| 代码漂移 | `git diff --name-only -- src apps tests` | 空 | **PASS** |
| 变更面 | `git diff --name-only` | 7 个 tracked（3 个 Lead 指针 + 两契约 + 冻结记录 + 矩阵） | **PASS** |

- 3 warnings 与既有 `logs/check.log` 逐字相同（11 个非终态 Task / STATUS 80% / PLAN 80%），非本包引入。
- **未跑**：全量 pytest、全量 .NET、GUI/e2e、真实回收站 D 流程。本卡是纯文档 UNFREEZE（`src/apps/tests` 零 diff），
  这些不在门禁内；本报告不据此宣称运行时通过。唯一运行的是一个**只读探针**（§2.3），它只读调用 Core preview、
  临时 DB 在仓外。
- 本报告不把既有 `verification/…/logs/` 当作我自己的实跑；上表数字均来自本次命令（同时写入仓外 probe 日志）。

## 9. Findings

### P2-1（非阻断，closeout 前应清）三份记录/载体/EV 仍保留「字典序最小 / 排序数组首项」

**位置**（实测逐处）：
- `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:109`（§4C 修订内容）：「R-3 删无定义术语 `separate/detached` + 写死 representative 排序（**字典序最小**、仅展示、不进 digest）」。
- `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md:31`（§2A R-3 改法）：「取按**字典序排序**的 `currentArtifactRevisionIds` 的**首项**」。
- 同上 `:51`（§2B `:954` 行）：「写死 representative=**字典序最小**、仅展示、不进 digest」。
- `verification/FEA-12-CORE-C04B-RESIDUAL-2/EV.md:27`：「写死 representative 排序（**字典序最小**、仅展示、不进 digest）」。

**问题**：最终契约 C-04b `:28` 对 artifact 分支明写「**非字典序**」，`:63` 改为指向 §0 第 1 条；实现（探针 A）
给出 `zzz` 而非字典序最小 `aaa`。上述 4 处因此**与冻结字节及实现相反**，且载体 §2A/§2B 与载体自身 §6:94-96
互相矛盾。**性质**：记录/证据精度，不改变契约字节、wire 或行为，故非阻断；但若随 closeout 发布，会再次把错误规则
传播给未来实现者——这正是本卡 R-3 要消除的问题。

**建议**：把 4 处统一改为「阅读序首个 lineage-visible region current，否则**首个 artifact current pointer**（pointer 顺序
`... artifact_type, artifact_id`；**非字典序**）；仅展示、不进 digest」，或统一改为「规则见 C-04b v1.2 §0 第 1 条」
（M2-C1 `:18`/`:32` 已用该单指源写法，可照办）。注意：冻结 §4A:132 的「现行权威读法」栏**属 v1.1 历史读法且
`:126` 已声明不改写**，不在本次修改范围。

### P2-2（非阻断）载体 §3 仍保留「改动仅让文字与现行实现一致」的过宽句

**位置**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md:63-64`：
「……改动仅让文字与**现行实现**（`core_service.py:1904-1930`、`:2450-2454`；`library.py:1178-1190` 待 RESIDUAL-3）一致。」

**问题**：r2 P2-1 已指定删除/改写该句；本轮只在 `:65-66` 追加了 R-1 的收窄说明（「**不得**说本包全部文字与现行实现
一致——R-1 侧契约与实现当前不一致」）。`:63-64` 的「改动仅让文字与现行实现一致」仍是无条件断言，而 R-1 的
**契约谓词**恰恰与实现不一致（`library.py:1178-1190` 无 `book_id`）。同段内 2 行后自我否定，读者仍可能只读 `:63-64`。

**建议**：把 `:63-64` 改为「除 R-1 的 artifact 成员谓词外，改动仅让文字与现行实现一致（R-1 见下条）」或直接删去
「与现行实现一致」的限定，保留 `:65-66` 的准确口径。

### P2-3（非阻断）EV §2 的 M2-C1 diff 数字与实测/EV §4 自相矛盾

**位置**：`verification/FEA-12-CORE-C04B-RESIDUAL-2/EV.md:31`：「**M2-C1 rev 2.15（`git diff --numstat` = 11 插入 / 7 删除）**」。

**问题**：实测（本次）与同 EV `:55`、`logs/diffstat.log` 均为 **20 插入 / 16 删除**。`11/7` 是 r1 时点（P1-2 与版本
引用行尚未补入）的旧值。同一份 EV 内 §2 与 §4 给出两个不同的 numstat，属证据自相矛盾；且 §2 是「变更清单」正文，
读者会据 11/7 低估 M2-C1 的改动面（实际含 `:972` 的规范性补全）。

**建议**：把 `:31` 改为 `20 插入 / 16 删除`；同时把该段 M2-C1 清单补上 `:972` 的 PD-01 段修改（见 P3-3）。

### P3-1（非阻断）M2-C1 `:140` 仍以「文档 rev 2.14」描述现行状态

**位置**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:140`：「……**文档 rev 2.14**（§5.13 rev 2.14 保护完整性）不等于
Core 运行常量……」。

**问题**：同段前半的 `C-04b v1.1`→`v1.2` 已改，但「文档 rev 2.14」未同步；而 `:28`（状态行）= `2.15`、`:797` =
「rev 2.14 与 rev 2.15 为准」、`:928` =「文档 rev 2.15 与运行常量分离」都已是 2.14/2.15 口径。r2 P3-1 明确点名过
`:28`/`:140`/`:928`，本轮修了 `:28`/`:928`，漏了 `:140`。

**建议**：改为「文档 rev 2.14/2.15」（保留「该内容由 2.14 引入」的事实，又不再声称现行 rev 是 2.14）。
`:1461`（§12 状态表的「rev 2.13 + rev 2.14 protection completeness」）是历史归因、rev 2.15 无规则变更，
**可保留**，不在本条要求内。

### P3-2（非阻断）载体 §2B 表格含字面 `` `n ``，两行被并成一行

**位置**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md:50`。原始字节（按 UTF-8 解码后检索：反引号+`n`
两字符子串位于第 3620 个字符处）：

```text
... | `:953` DTO 注释 | 删 `separate/detached`，改为「全部 region（含 lineage-hidden）current」 |`n| `:972` §5.13 PD-01 段 | 补 artifact 成员谓词 ...
```

即 R-3（`:953`）行与 `:972` 行之间应是换行，实际写成了字面 `` `n ``，导致表格只有一行、且渲染出多余字符。

**影响**：内容（含 `:972`）**存在**，不影响契约与门禁；但载体是复核链的证据文档，表格损坏降低可读性，
且与「`:972` 已列入清单」的自述形式不符。**建议**：把 `` |`n| `` 改回换行，恢复两行。

### P3-3（非阻断）M2-C1 修改清单的行号基准混用，且冻结 §4C / EV 未列 `:972`

**实测**：
- 载体 §2B 与任务卡 AC-2 均**已含 `:972`** ✓，但行号混用基准：`:953`/`:954`（HEAD 基准）与 `:972`（现行基准）；
  现行应为 `:957`/`:958`。
- 冻结 §4C:109 的 M2-C1 清单（`:18/:30/:814/:815/:819/:953/:954`）**未列 `:972`**，且 `:814/:815/:819` → 现行
  `:818/:819/:823`、`:953/:954` → 现行 `:957/:958`。
- EV §2:31-34 的清单同样**未列 `:972`**，行号同为插入前值。
- 任务卡 AC-1/AC-2 声明 `base_commit: d91d9b6cc`，使用 base 行号本身可接受；问题只在**同表混用 base 与现行**
  （`:972` 是现行坐标）。冻结 §4C 未声明基准，宜按现行或注明 base。

**建议**：在载体 §2B / 卡 AC-2 / 冻结 §4C / EV §2 统一注明「行号为 base `d91d9b6cc`」或全改为现行行号；
并把 `:972` 补进 §4C 与 EV §2 的清单（P1-2 的实际落点，缺失会使证据链读不出关键修复点）。

### P3-4（非阻断）矩阵 `:22` 仍写复核「⏳ 待派」

**位置**：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:22`：「①v1.2 独立 byte-level 复核 **⏳ 待派**（载体 …）」。

**问题**：矩阵「冻结条件（差什么）」列显示 ⏳ 本身正确（条件①尚未满足），但「待派」与事实不符——r1、r2 已完成且
均为 `changes_requested`，r3 已派（本报告）。载体 §6 / EV §5 已如实记 r1→r2→r3，矩阵未同步，四份记录口径不一致。

**建议**：改为「⏳ r1/r2 `changes_requested` → r3 复核中（见载体 §6）」，approved 后回填 ✅。

## 10. 结论

**approved**（P0=0、P1=0）。最终字节
C-04b `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52`（blob `a30e4080116d01512977eca40de1c43ea7244a64`）与
M2-C1 `a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e`（blob `cb8eeb21279ff3dd23ad7c1cec6c171b211592e9`）
在以下意义上可作 v1.2 / rev 2.15 的冻结字节：

1. **两项 P1 的 normative 文字与现行实现逐要素等价**，并用三个只读探针案独立复现（含「hidden region current 不压制
   artifact fallback」这一唯一能证伪旧读法的构造）；
2. **语义零变更**：27 个 hunk（C-04b 11 + M2-C1 16）全为措辞/版本引用/谓词文字/行号→节名；无校验顺序、拒绝条件、失败分类、字段、错误码、
   能力、`PROTOCOL_MINOR`、wire minor 变化；
3. **pin 账自洽**：C-04b 1/18 重签且 `verify_pins` 18/18；其余 17 份逐字节不变；M2-C1 0/18 机械 pin 由 §1B/§4C/载体 §7
   三处手工登记覆盖，与实测全等；
4. **门禁全绿**：`check.ps1` 默认与 `-TaskPath` PASS、`git diff --check` 干净、`src/apps/tests` 零 diff；
5. **记录不夸大**：仍明确 R-1 代码未修、L-3 有效、契约与实现当前不一致、R-1 归 RESIDUAL-3，无「8 项全关/R-1 已修复」。

**批准附带条件（非阻断，须在 closeout 前清）**：P2-1（4 处「字典序最小」残余）、P2-2（载体 §3 过宽句）、
P2-3（EV §2 numstat `11/7`→`20/16`）应在本包提交前修正；P3-1…P3-4 可同批清理。上述修改**只动记录/载体/EV 文字**，
不触及两契约字节、不改 pin、不需重新 byte-level 复核；但若因此改动**冻结记录 §4C 的 sha 行或两契约任何字节**，
则须重新登记 pin 并由独立上下文复核新字节。

## 11. 真实性声明

- **身份与独立性**：我是本次委派的 fresh subagent，session `98692074-315d-46d5-ba77-37e1df07f093`；未参与 C-04b v1.2 /
  M2-C1 rev 2.15 的起草、实施或任何一轮返修，未参与 r1/r2 复核，未参与此前 C-04b/CORE 实现或 residual scope review。
  `reviewed_head=d91d9b6cc4afef307b0662055812c129468054a0`，只读该工作树。
- **写入范围**：本报告 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r3.md` 是本次唯一写入仓库的文件（untracked）；
  仓外只写 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\unfreeze-review-r3\`（`probe-representative.py`/`.log`）。
  未修改任何 tracked 文件、契约、记录、矩阵、载体、任务卡、源码或测试；未 `git add`/`commit`/`push`/`reset`/
  `checkout`/`stash`。
- **字节未变**：审查开始与结束时两契约复算均为 C-04b `4b304c0c…`、M2-C1 `a82a7fc1…`；`git diff --name-only` 的
  7 个 tracked 文件集合相同；新增的只有本报告（以及既有 untracked 证据目录）。
- **实测与未跑**：§5/§8 数字来自本次命令；§8 明确列出未跑的 pytest/.NET/GUI/e2e/真实回收站流程。§2.3 探针只读调用
  Core preview，临时 DB 在仓外、不写仓库，输出已存仓外日志。未把既有 `verification/` 日志当作本次实跑；
  未把 `verify_pins` 18/18 当作语义正确性的替代（M2-C1 0/18，机械检查发现不了其漂移）。
- **不夸大**：本报告未写「8 项 residual 全部关闭」「R-1 已修复」「C-04b/M2-C1 已最终冻结」；`approved` 只针对**当前
  字节的 normative 文字/零语义变更/pin/门禁**，不含运行时通过、不含 R-1 代码修复、不含 push 授权。
- **限制**：未逐行重读 C-04b/M2-C1 全文每一句历史注释；对未落入本次 diff 的条款按「零 diff」采信（HEAD 未被改动的
  字节不重复审），只对本次 27 个 hunk、R-1/R-2/R-3/R-4/R-5/R-8 语义点、§5.11.1a/§5.13 相关段、pin 账、记录/载体/EV
  与实现/测试/探针事实做逐项核对。
