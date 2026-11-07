---
task: FEA-12-CORE-C04B-RESIDUAL-3
reviewer: fresh subagent
reviewer_kind: subagent
session: a4b5d82e-0649-4935-aab4-9b0fb84593ff
reviewed_head: 25dc1523c
verdict: approved
p0: 0
p1: 0
p2: 2
p3: 4
date: 2026-11-08
---

# Review：FEA-12-CORE-C04B-RESIDUAL-3（R-1 artifact 成员谓词代码修复）

> 我是 Lead（`lead`）委派的 **fresh subagent**（独立上下文；session `a4b5d82e-0649-4935-aab4-9b0fb84593ff`），
> **未参与**本卡实现/返修，也**未参与** C-04b / CORE 实现或 `RESIDUAL-1/2` 的起草与复核。本次只读被审对象，
> 未执行 `git add/commit/push`；唯一写入是本文件（另有临时备份/基准库写在
> `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\review-r3\`）。结论只对 `reviewed_head=25dc1523c` 有效。

## 0. 结论（先给）

- **verdict: approved**；P0=0、P1=0、**P2=2**、P3=4。代码改动**与已冻结契约一致**，AC-1…AC-5 均可复核为 MET；
> 两项 P2 分别是「卡面 AC-3 方向文字写反」（文档，非实现）与「`media_artifacts.book_id` 无索引导致的查询计划回退」
> （性能，非阻塞，且在本卡 AC-4「`schema.py` 零 diff」约束下无法在本卡内修）。详见 §5。
- 独立复跑关键数字：定向 **59 passed**（3.71 s）；判别性自做回退 → **3 failed / 15 deselected**（0.52 s）；
> 逐字节复原 `sha256 = da07ccdb…` **MATCH** + `touch` → **3 passed**；`verify_pins.ps1` **PASS (all 18)**；
> `check.ps1`（默认 / `-TaskPath`）**PASS (3 warnings) ×2**；`generate_api_inventory.py --check` **EXIT 0**；
> 证据 manifest **15/15 sha256 + bytes MATCH**；`git diff --check` EXIT 0；工作树 clean。
- **head 口径偏差（须 Lead 在 closeout 记录）**：派发说明写 HEAD=`6e20d5d28`，实测 HEAD=`2babb0c78`
> （在其上多一个 docs/evidence 提交，只动 `EV.md`、`RESOURCE-MANIFEST.json`、`logs/scope-post-commit.txt`）。
> 被审实现提交仍是 `25dc1523c`，`git diff 4c42e11b8..2babb0c78` 与 `4c42e11b8..25dc1523c` 的代码部分完全一致；
> 详见 R3-005。

## 1. 审查对象

| 项 | 值 |
|---|---|
| 卡 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`（`status: ready`；AC-1…AC-5 已 `<<MET>>`；closeout 字段 pending） |
| `delivery_head` | `25dc1523c8afc2083a03e478dc65d4ee9c36cf5c`（实现 + 测试提交） |
| 实现 commit | `25dc1523c`：`src/infrastructure/sqlite/library.py`（+18/−4）、`tests/core/test_core_delete_preview_commands.py`（+223/−0） |
| docs/evidence commit | `6e20d5d28`（卡面交付记录 + Handoff + EV/manifest/logs）→ `2babb0c78`（补 `scope-post-commit` 证据 + manifest 刷新） |
| base | `26aa0ca4a`（C-04b v1.2 / M2-C1 rev 2.15）；交付起点 `4c42e11b8`（RESIDUAL-2 closeout，已 push） |
| 契约依据 | `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` v1.2 §0 第 1 条 / §2.1；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.15 |
| 冻结记录 | `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A **L-3** / R-1 行 |
| 证据 | `verification/FEA-12-CORE-C04B-RESIDUAL-3/{EV.md, RESOURCE-MANIFEST.json, logs/**}`（EV `821d9f4d…`） |
| Handoff | `doc/handoffs/FEA-12-CORE-C04B-RESIDUAL-3-25dc1523c.md` |

代码事实（修复后行号；本卡 +14 行使冻结记录里以释放时 HEAD 标注的 `:1920-1926` 等行号整体下移）：

- `library.py:1178-1204` `list_book_artifact_current_pointers`：docstring `:1179-1192`；SQL `:1193-1203`；
  成员谓词 `:1199` `WHERE ma.book_id = ? AND ma.current_revision_id IS NOT NULL`；
  排序 `:1200-1201` `ORDER BY c.sort_order, c.import_order, c.chapter_id, p.sort_order, p.page_id, ma.artifact_type, ma.artifact_id`；
  `JOIN pages/chapters` → `LEFT JOIN`（`:1197-1198`）；`SELECT` 首列由 `p.page_id` 改 `ma.page_id`。
- 删除面 `:1934-1940`（`DELETE FROM artifact_revisions WHERE artifact_id IN (… WHERE book_id = ?)`、`:1940` `DELETE FROM media_artifacts WHERE book_id = ?`）。
- `list_book_artifact_revision_ids` `:1232-1239`（`WHERE ma.book_id = ?`，`:1236`）。
- `book_delete_inventory` `:1488-1563`（artifact pointer 装配 `:1531-1533`；`artifacts` 计数 `:1549-1551` 用 `book_id`）。
- `list_book_cleanup_targets` `:1078-1109`（artifact 受管路径 `:1090-1095` 用 `ma.book_id`）。
- `core_service.py` **零 diff**：`_finalize_delete_inventory` `:1855-2003`、representative 回退 `:1907-1931`、
  `_preview_item_dto` `:2034-2069`、`_collect_delete_targets` `:2332-2355` 均未改。
- 新增测试：helpers `tests/core/test_core_delete_preview_commands.py:875-955`；三用例 `:957`、`:983`、`:1051`。

## 2. AC 逐条结论

### AC-1 谓词对齐 —— MET

- 成员谓词已改为 `ma.book_id = ?`（`:1199`），与删除面 `:1940`、`list_book_artifact_revision_ids` `:1236` 同一谓词；
  `current_revision_id IS NOT NULL` 保留；**无任何可见性过滤**（artifact 侧本无 lineage 可见性状态，`:1184-1185` docstring 也写明）。
- 阅读序排序键 7 项**逐项保留**（`:1200-1201`，与被删除的两行逐字符相同）；`JOIN` 仅承担排序与 `page_id` 投影。
- **未顺手改动** representative / `_finalize_delete_inventory` / 可见性逻辑：`git show --stat 25dc1523c` 只有 2 个文件；
  `library.py` 内只有 `list_book_artifact_current_pointers` 一个 hunk（函数体质 4 删 18 增，含 docstring），
  `:1158-1176` 的 region 查询与其它方法字节未动。
- 静态断言（`:957-981`）同时锚定 preview 侧完整谓词、`c.book_id = ?` 不出现、`ORDER BY` 头尾保留，
  以及两处删除侧谓词——满足 AC-1 的「静态断言同源」要求。

### AC-2 正常数据零回归 —— MET

- 新用例 `:983-1048` 先插两本书各 1 个**归属一致**的 artifact，断言
  `book-a.currentArtifactRevisionIds == ["ar-a"]`、`book-b == ["ar-b"]`、representative 分别为 `ar-a`/`ar-b`
  （`:1003-1013`，正常数据对照）。
- 该对照的**判别力有硬证据**：修复前 RED 日志中，这三/四条 control 断言全部通过，失败点在后续损坏行断言
  （`logs/red-before-fix.txt`、`logs/discriminate-red.txt`；独立复跑同样如此）——说明旧谓词在正常数据上给出相同的值。
- 既有 preview/delete 测试全绿：定向两文件 **59 passed**（我实跑 3.71 s）；测试函数计数由 `4c42e11b8` 的 15 个
  增至 18 个（+3），与 56→59 自洽。schema 上 `media_artifacts.page_id` 为 `NOT NULL` 且 FK 到 `pages`（`schema.py:71-86`），
  不存在「无 page 的合法 artifact」这一类会因 LEFT JOIN 改变归属的正常数据；
  正常写入路径的 `book_id` 全部由既有 artifact/目标快照派生（`application/rendering/service.py:213-219`、`:414-415`；
  `infrastructure/sqlite/pipeline.py:148`、`:1157-1162`），因此「book_id 与 page 所属书一致」在正常数据下成立。

### AC-3 损坏行判别 —— MET（**卡面方向文字写反，见 R3-001**）

- 损坏行是**真实构造**的：`_seed_current_artifact(book_id="book-a", chapter_id="ch-b", page_id="pg-b")`
  （`:1016-1019`），即 `media_artifacts.book_id=A`、`page_id` 属于 B；库由 `assemble_production_core` 走真实 production
  migrations（v8）建立，**非 stub**（fixture `:34-40`，pytest stderr `[core.schema] applied 8 migration(s) up to v8`）。
- 修复后断言：A 侧 `["ar-a", "arv-x"]`（含损坏行）、B 侧 `["ar-b"]`（不含）（`:1022-1025`）；并**实跑**
  `PermanentlyDeleteBook(book-a)`，断言 `arv-x`/`ar-a` 被删、`ar-b` 保留（`:1037-1048`）——与删除集合一致。
  反向用例 `:1051-1090` 用 `book_id=B`、页属 A 的 `arv-y` 覆盖另一方向，并实跑删除 B。
- **判别性（我独立复跑，见 §3）**：把谓词改回 page/chapter join → 三用例 **3 failed**；逐字节复原 sha256 MATCH → **3 passed**。
- **方向裁定**：卡面 AC-3 文字「A 的 preview **不含**、B 的 preview **包含**（与删除集合一致）」自相矛盾——
  删除按 `WHERE book_id = A` 删除，该行只能属于 A 的删除集合；「A 不含 / B 含」正是**修复前** page/chapter join 的偏差行为
  （scope review §2.1 亦把旧行为描述为「A 多绑定 / B 少绑定」）。实现按括号基准（与删除集合一致）+ C-04b v1.2 §0 第 1 条
  落地为 **A 含 / B 不含**，并在卡面交付记录、`EV.md` §2.1、Handoff §5 三处如实登记，**未**按文字方向反向实现。
  这是正确处置；但 AC 文字本身仍须修正（P2，R3-001），否则后续读者/测试可能被误导。

### AC-4 零漂移 —— MET

- `git diff 4c42e11b8..25dc1523c --name-only` = **仅** `src/infrastructure/sqlite/library.py`、
  `tests/core/test_core_delete_preview_commands.py`；延伸到当前 HEAD `2babb0c78` 共 **20 个文件**，
  全部落在卡面 `allowed_paths`（2 代码/测试 + 卡面 + Handoff + EV/manifest + 14 日志）。
- `doc/plan`、`doc/contracts`、`src/infrastructure/sqlite/schema.py`、`apps/**`、`pyproject.toml`、`requirements*.txt`、
  `uv.lock` 在 `4c42e11b8..2babb0c78` **零 diff**；C-04b sha256 `4b304c0c…`、M2-C1 `a82a7fc1…`、
  `schema.py` `8714348c…` 与冻结记录/pins 完全一致。
- `verify_pins.ps1`：**PIN AUDIT: PASS (all 18)**，EXIT 0（我实跑，18 条 `OK` 全列）。
- `check.ps1` 默认与 `-TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`：均 **PASS (3 warnings)**、EXIT 0
  （3 条 warning 与本次改动无关：10 个非终态 Task、STATUS 80% 预算、REBASELINE_PLAN 80% 预算）。
- `generate_api_inventory.py --check`：**EXIT 0**（我实跑）。

### AC-5 门禁/证据/不夸大 —— MET（含 1 处 P3 口径注记）

- 卡面/EV 数字与实跑一致：定向 **56→59**（旧测试文件 15 个函数 + 新 3 个 = 18，另一文件 41 个，合计 59）；
  全量日志 `logs/full-after.txt` 末行 **3372 passed, 10 skipped in 251.43s**（**我未重跑全量**，按派发口径由 Lead 复跑）；
  pins/check/API 与我的实跑一致。
- 证据完整可复算：`RESOURCE-MANIFEST.json` 列出的 **15 个 artifact 全部 sha256 + bytes MATCH**（我逐个复算）；
  `EV.md` 给出复现命令与日志对应关系；`git diff --check` EXIT 0（无空白/冲突标记）。
- 不夸大：卡面、EV §7、Handoff §6 均明确「正常数据零变化」「损坏 DB 属异常输入」「未 push/未 closeout」，
  并明确**未**声称「8 项 residual 全部关闭」，只写「R-1 的代码侧已与 C-04b v1.2 谓词一致」——符合要求。
- 唯一的口径瑕疵：`EV.md:127` 的「19 个文件（tree `6e20d5d28`）」在当前 HEAD（含第 20 个文件）需补一句说明（R3-005）。

## 3. 判别性独立复跑（我自己的，1 个破坏点）

| 步骤 | 操作 | 结果 |
|---|---|---|
| 1 | 备份 `library.py`（sha256 `da07ccdb4d0590828658c859e6c606e1c2614d7c1dde52894d3b15957b1bd792`）与测试文件（`5c350d3e…`）到 workspace | 两份备份与仓内逐字节一致 |
| 2 | 只把成员谓词改回 page/chapter join（`LEFT JOIN`→`JOIN`，`WHERE ma.book_id = ?`→`WHERE c.book_id = ?`；SELECT 与 docstring 不动） | 回退版 sha256 `471df70b49d7c8e1f36ec5f9367655ff1ba4e620b003c133b0c603bb3212af5b`（与实现者记录的 `b3c230b5…` 不同：实现者的回退版还改了别的文本，不影响判别结论） |
| 3 | `pytest … -k artifact_membership -q -p no:warnings` | **3 failed, 15 deselected in 0.52s**（必须 RED）——三用例全红，含静态断言与双向损坏行 |
| 4 | 从备份逐字节复原 + `Get-FileHash` 比对 | expected = actual = `da07ccdb…` **MATCH** |
| 5 | `touch`（重写 mtime）后复跑 | **3 passed, 15 deselected in 3.86s**（复绿） |
| 6 | `git status --porcelain` / `git diff --check` | **clean** / EXIT 0；HEAD 版本即修复版（diff 为空） |

复跑过程中未触碰其它文件；未 `git add/commit/push`。

## 4. 门禁、证据与范围（实跑记录）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 定向 pytest | `C:/Python314/python.exe -m pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings` | **59 passed in 3.71s** | 本次 Review 输出；实现者日志 `logs/targeted-after.txt`（59 passed） |
| 判别性 RED/GREEN | 见 §3 | **3 failed** → sha MATCH → **3 passed** | 本次 Review 输出；实现者 `logs/discriminate-red.txt`、`logs/discriminate-green-after-restore.txt` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**，EXIT 0 | `logs/pins.txt` 同值 |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT 0 | `logs/check-default.txt` 同值 |
| check（`-TaskPath`） | `… check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | **PASS (3 warnings)**，EXIT 0 | `logs/check-taskpath.txt` 同值 |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT 0** | `logs/api-inventory.txt` 同值 |
| scope | `git diff 4c42e11b8..25dc1523c --name-only`；`git diff --name-only 4c42e11b8..2babb0c78 -- <契约/schema/apps/依赖>` | 2 文件 / 20 文件；零漂移范围**空** | `logs/scope.txt`、`logs/scope-post-commit.txt` |
| 证据 sha | Python 逐文件 `hashlib.sha256` 对比 manifest | **15 MATCH / 0 MISMATCH** | `RESOURCE-MANIFEST.json` |
| 空白/冲突 | `git diff 4c42e11b8..25dc1523c --check` | 无输出，EXIT 0 | 本次 Review |
| 全量 pytest | 未重跑（派发口径：Lead 跑并给 3372/10） | **NOT_RUN（本 Review）** | `logs/full-after.txt`（3372/10，251.43s） |
| `tests/fea11` | 可选，未跑 | **NOT_RUN** | — |

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R3-001 | P2 | `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md:57-58` | AC-3 方向文字与契约/删除集合相反：字面写「A 不含 / B 含」，而删除面按 `book_id=A` 删除，正确结果与「与删除集合一致」都要求 **A 含 / B 不含**；实现与测试是对的，但 AC 原文会误导后续修测试/复核者 | C-04b v1.2 §0 第 1 条；`library.py:1940`；scope review §2.1（旧行为=A 多绑定/B 少绑定）；卡面交付记录、`EV.md:82-89`、Handoff §5 已登记 | Lead 在 closeout 修正 AC-3 文字（改为「A 含 / B 不含」或删掉与括号基准冲突的方向句）；不需改代码/测试 | open |
| R3-002 | P2 | `src/infrastructure/sqlite/library.py:1193-1203` | 性能回退：`media_artifacts` 只有 `(page_id, artifact_type)` 索引（`schema.py:86`），新谓词 `ma.book_id = ?` 无索引 → 执行计划由三级索引 `SEARCH` 变为 `SCAN ma`；成本随**全库** artifact 总数增长，且批量预览最多 20 书会逐书重复扫描 | 我实测 `EXPLAIN QUERY PLAN`：旧=SEARCH chapters→pages→media_artifacts；新=`SCAN ma` + PK LEFT-JOIN 查找。基准（同 schema v8、18 读缓存）：6,000 artifacts 时 0.24→0.43 ms/书；60,000 artifacts 时 **0.26→5.32 ms/书**（各 10 次均值） | 非阻塞：预览是一次性只读路径，绝对量级小。建议后续单独 schema 卡加 `idx_media_artifacts_book(book_id)`（本卡 AC-4 要求 `schema.py` 零 diff，不宜在本卡改）；或在 closeout 登记为已知 residual | open（Lead 决定） |
| R3-003 | P3 | `EV.md:148-150`、Handoff `:90` | 「不构成 representative/`currentRevisionId` 语义或 pointer 顺序变化」对**损坏数据**略宽：规则与排序键未改，但 pointer 列表成员变了，损坏行可能进入 A 的列表并按 B 的 chapter/page 排序键参与排序；若 page/chapter 链断裂，`NULL` 排序键在 SQLite `ASC` 中排最前。展示值可能变，但**不进 digest、正常数据不变** | `core_service.py:1907-1931` 未改；新 SQL 的 `LEFT JOIN` + `ORDER BY`；现有测试未覆盖该展示值 | closeout 的 limitation 补一句「损坏数据下 `currentRevisionId` 展示值可能随成员/排序键变化」 | open |
| R3-004 | P3 | `core_service.py:2346-2354`、`library.py:2038-2058` | 损坏行（`book_id=A`、页属 B）删除 A 时：DB 行与 `managed_path` 会随 `book_id` 删除，但 `preview_lifecycle` 资源枚举仍按 `page_ids` 归属（`list_page_artifact_ids(A 的 page)`），该 artifact 的 preview 缓存文件可能漏清。**pre-existing、非本卡引入**，`EV.md` limitation 未提 | 代码路径 + 本卡只对齐「preview 集合 vs 删除谓词」 | closeout/后续 residual 记录即可；不阻塞本卡 | open |
| R3-005 | P3 | `verification/…/EV.md:127`；派发说明的 HEAD | HEAD 口径漂移：派发写 HEAD=`6e20d5d28`，实测 HEAD=`2babb0c78`（额外 docs/evidence 提交：EV +5/−2、manifest 刷新、新增 `logs/scope-post-commit.txt`）；EV 的「19 文件（tree `6e20d5d28`）」在当前 HEAD 为 20 文件（`git diff 4c42e11b8..2babb0c78 --name-only` = 20）。代码零变化 | `git rev-parse`、`git show --stat 2babb0c78`、`git diff --name-only` | closeout 同时写明 `reviewed_head=25dc1523c` 与 evidence HEAD=`2babb0c78`，避免「19 vs 20」被误读为漂移 | open |
| R3-006 | P3 | `tests/core/test_core_delete_preview_commands.py:957-981` | 静态断言依赖 `inspect.getsource` 的精确白空格子串；仅重排 SQL 字符串就会误报（维护脆性），且「不含 `c.book_id = ?`」只挡一种写法 | 测试代码 | 后续可改为规范化空白后的匹配或纯行为断言；非阻塞 | open |

在记录范围内**未发现** P0/P1。

## 6. 代码质量专项

- **连接/事务语义**：改动仍是一次 `self._conn.execute(...)` 只读查询，未新增查询、未开/改事务、无缓存、无写操作；
  `:1158-1176` 的 region 查询零 diff。preview 的只读性（PD-03）未被破坏。
- **排序稳定性**：集合判定与 `currentArtifactRevisionIds`（字典序排序去重，`core_service.py:1901-1906`）无关；
  损坏行仅影响 pointer 列表顺序（进而不进 digest 的 representative 展示值）——见 R3-003。正常数据下
  `p.page_id == ma.page_id`，排序键与旧实现逐值等价。
- **性能**：存在可测量的计划回退（R3-002），但非阻塞；正确性上新的 `LEFT JOIN` 还避免了「page/chapter 链断裂时成员静默丢失」，
  与 `media_artifacts.page_id` 的 `NOT NULL`/FK 约束一起看，正常数据无额外行。
- **测试质量**：损坏行双向覆盖 + 静态断言 + 删除一致性实跑，判别力足够；`_expected_digest` 由 DTO 重算
  （等价于 DTO↔digest 一致性校验，非独立读库），配合显式的集合值断言已足够。
- **副作用面**：`SELECT` 改取 `ma.page_id` 不改变任何调用方行为——`artifact_current_pointers` 的消费者只有
  `_finalize_delete_inventory`（只用 `current_revision_id`）与 `current_revision_count` 的长度统计
  （`core_service.py:1893-1898`、`:1932-1934`），`page_id` 不外泄到 DTO/IPC。

## 7. 未执行 / 未覆盖

- **全量 pytest 未重跑**（按派发口径由 Lead 复跑并给 3372/10）；`tests/fea11` 未跑（可选）。
- 未复核实现者记录的「修复前 56 passed」旧代码定向运行（以测试函数 15→18、日志 56→59 与 RED 日志中的 control 断言通过作交叉验证）。
- 未构造真实 E2E/迁移库损坏数据的文件系统级清理验证（R3-004 只作代码路径判断，未实跑）。

## 8. 结论与复审

`reviewed_head=25dc1523c` 的代码与测试**可以交 DSH 集成**：R-1 的代码侧已与 C-04b v1.2 §0 第 1 条、
M2-C1 rev 2.15 及删除面/`list_book_artifact_revision_ids` 的 `media_artifacts.book_id` 谓词一致；正常数据零变化；
损坏数据下 preview 保护集合与删除集合一致；契约/schema/apps/依赖零漂移；pins 18/18、check PASS、API inventory EXIT 0；
证据可复算。剩余风险是 **R3-001（AC 文字需 Lead 修正）** 与 **R3-002（无 `book_id` 索引的性能回退，建议后续 residual）**，
二者都不阻塞本卡 closeout。head 变更或 closeout 改写 AC 后，本文件按约定转为历史记录。

## 9. 本次 Review 的写入与工作树

- 唯一仓内写入：本文件 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-3-r1.md`（untracked，`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-3-*.md` ⊆ allowed_paths）。
- 仓外临时目录：`G:\CODEX\New Manga.workspace\C04B-RESIDUAL\review-r3\`（`library.py.fixed`、`test_core_delete_preview_commands.py.fixed` 备份；
  `explain-db/`、`bench-db*/` 基准库）。结束状态：工作树 clean（仅本报告 untracked），无 `git add/commit/push`。
