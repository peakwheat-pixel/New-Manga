# FEA-12-CORE-C04B-RESIDUAL-3：R-1 artifact 成员谓词代码修复 — 证据（EV）

> 本 EV 只陈述**实改/实跑**事实。本卡是**实现卡（0 pin）**：把
> `src/infrastructure/sqlite/library.py` 的 `list_book_artifact_current_pointers` 的 artifact 成员谓词
> 从 **page/chapter join** 改为 **`media_artifacts.book_id = ?`**（C-04b v1.2 §0 第 1 条 /
> M2-C1 rev 2.15 §5.13），保留 `current_revision_id IS NOT NULL`、不按可见性过滤、阅读序排序；
> **正常数据行为零变化**，只消除「`media_artifacts.book_id` 与其 `page_id` 所属书不一致」损坏行下
> preview 保护集合与删除集合的偏差（L-3）。
> **不改** representative/`currentRevisionId` 语义与顺序逻辑、删除事务、契约字节、`schema.py`、
> `apps/**`、依赖、wire/命令/错误码/`PROTOCOL_MINOR`。

- Task：`doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`（`status` 与 closeout 由 Lead 维护）
- `delivery_head`：`25dc1523c`（`25dc1523c8afc2083a03e478dc65d4ee9c36cf5c`，实现+测试 commit；本 EV / 证据 /
  Handoff / 卡面交付记录为紧随其后的 docs/evidence 提交）
- `base_commit`：`26aa0ca4a`（本卡起点 HEAD=`4c42e11b8`；`4c42e11b8` 与 `857354751` 为 Lead 已 push 的 RESIDUAL-2 closeout 记录）
- 依赖：`FEA-12-CORE-C04B-RESIDUAL-2`（C-04b v1.2 + M2-C1 rev 2.15 谓词文字，已 push）
- 环境：Windows 11 / PowerShell 7 / Python 3.14；真实 production migrations（`assemble_production_core`，v8）；无 stub
- 冻结记录：`doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A **L-3**（本偏差现行登记）、§4A R-1 行

## 1. 代码变更（唯一生产改动）

`git diff --numstat 4c42e11b8`：

| 文件 | 插入 | 删除 |
|---|---|---|
| `src/infrastructure/sqlite/library.py` | 18 | 4 |
| `tests/core/test_core_delete_preview_commands.py` | 223 | 0 |

`list_book_artifact_current_pointers`（`:1178` 起）SQL 前后对照：

```sql
-- before（page/chapter join 判定成员）
SELECT p.page_id, ma.artifact_id, ma.artifact_type, ma.current_revision_id
FROM media_artifacts ma
JOIN pages p ON p.page_id = ma.page_id
JOIN chapters c ON c.chapter_id = p.chapter_id
WHERE c.book_id = ? AND ma.current_revision_id IS NOT NULL
ORDER BY c.sort_order, c.import_order, c.chapter_id,
         p.sort_order, p.page_id, ma.artifact_type, ma.artifact_id

-- after（成员 = media_artifacts.book_id；JOIN 仅用于阅读序与 page_id 投影）
SELECT ma.page_id, ma.artifact_id, ma.artifact_type, ma.current_revision_id
FROM media_artifacts ma
LEFT JOIN pages p ON p.page_id = ma.page_id
LEFT JOIN chapters c ON c.chapter_id = p.chapter_id
WHERE ma.book_id = ? AND ma.current_revision_id IS NOT NULL
ORDER BY c.sort_order, c.import_order, c.chapter_id,
         p.sort_order, p.page_id, ma.artifact_type, ma.artifact_id
```

- 谓词现与删除面 `execute_permanent_delete_db`（`DELETE FROM media_artifacts WHERE book_id = ?`）与
  `list_book_artifact_revision_ids`（`WHERE ma.book_id = ?`）**同一条**。
- JOIN 改为 `LEFT JOIN`：成员集合不再因 page/chapter 链条断裂而丢行（成员判定只由 `ma.book_id` 决定）。
- 阅读序排序键**逐项保留**（`chapter.sort_order, chapter.import_order, chapter_id, page.sort_order, page_id, artifact_type, artifact_id`）；
  `SELECT` 的 `page_id` 改取 `ma.page_id`（与 `p.page_id` 在正常数据上相等；调用方 `_finalize_delete_inventory` 只用
  `current_revision_id`，representative 的 pointer 顺序不变）。
- **未改** `core_service.py`（不在写域）：`currentRevisionId = 首个 artifact current pointer`（局部列表阅读序、非字典序）逻辑保持原样。
- 最终字节：`library.py` SHA-256 `da07ccdb4d0590828658c859e6c606e1c2614d7c1dde52894d3b15957b1bd792`
  （blob `fcef8cc91d75c687f59ad69c0ed9fd3053df22db`）。

## 2. 测试变更（3 个用例 + 3 个 helper）

`tests/core/test_core_delete_preview_commands.py`（+223 行；最终 SHA-256
`5c350d3e56928e6d1611093580b8e9c3a829d4d350634de6efbe1a94afb1c48e`）：

1. `test_artifact_membership_predicate_matches_delete_surface` — **AC-1 静态断言**：
   `inspect.getsource` 断言 preview 侧含完整谓词
   `WHERE ma.book_id = ? AND ma.current_revision_id IS NOT NULL`、**不含** `c.book_id = ?`、
   `ORDER BY c.sort_order, c.import_order, c.chapter_id` 与 `ma.artifact_type, ma.artifact_id` 保留；
   并断言 `list_book_artifact_revision_ids` 含 `ma.book_id = ?`、
   `execute_permanent_delete_db` 含 `DELETE FROM media_artifacts WHERE book_id = ?`。
2. `test_preview_artifact_membership_follows_book_id_not_page_owner` — **AC-2 对照 + AC-3 正向判别 + 删除一致性**：
   真实 production migrations 库、真实数据形态；先断言正常数据 `["ar-a"]`/`["ar-b"]`（零回归对照），
   再插入损坏行 `ma-x`（`book_id=book-a`、`page_id=pg-b` 属于 book-b），断言
   `book-a.currentArtifactRevisionIds == ["ar-a", "arv-x"]`、`book-b == ["ar-b"]`，
   digest 与独立重算一致；最后**实跑** `PermanentlyDeleteBook(book-a)`，断言 `arv-x` 与 `ar-a`
   被删除、`ar-b` 保留、`book-b` 的 preview 仍为 `["ar-b"]` —— preview 保护集合与删除集合一致。
3. `test_preview_artifact_membership_reverse_corrupt_row` — **AC-3 反向覆盖**：
   损坏行 `ma-y`（`book_id=book-b`、`page_id=pg-a` 属于 book-a），断言 `book-b` 含 `arv-y`、
   `book-a` 不含；实跑 `PermanentlyDeleteBook(book-b)` 后 `arv-y` 被删除、`ar-a` 保留。

### 2.1 AC-3 方向说明（如实登记）

任务卡 AC-3 文字为「构造 `media_artifacts.book_id = A` 但 `page_id` 属于 B 的损坏行 → 修复后
**A 的 preview 不含**该 artifact、**B 的 preview 包含**它（与删除集合一致）」。按括号内的判定基准
（**与删除集合一致**）与 C-04b v1.2 §0 第 1 条的成员谓词，正确结果是 **A 含 / B 不含**：删除事务按
`WHERE book_id = A` 删除该行，保护集合必须包含它才与删除一致；「A 不含 / B 含」恰是旧 page/chapter join 的行为。
实现按括号基准（契约谓词 + 删除一致性）落地，并用**双向两行**覆盖两个方向（正向 `book_id=A`/页属 B、
反向 `book_id=B`/页属 A），保证任何读法下都可判别。卡面 AC 文字的方向笔误已记入交付记录，未据此改变实现。

## 3. AC 逐条判定

| AC | 判定 | 证据 |
|---|---|---|
| **AC-1 谓词对齐** | **MET** | §1 SQL 对照 + §2 用例 1（静态断言三处谓词同源，ORDER BY 保留）；pins 18/18 |
| **AC-2 正常数据零回归** | **MET** | §2 用例 2 的对照断言（`["ar-a"]`/`["ar-b"]`）；既有 `test_preview_binds_artifact_current_set`（`["ar1"]`→`["ar2"]`）等 15 个既有 preview 测试全绿；定向 56→59、全量 3369/10→3372/10 |
| **AC-3 损坏行判别** | **MET** | §2 用例 2/3（双向）；§4 判别性实验：回退谓词 → **3 failed**；逐字节复原 SHA-256 MATCH → **3 passed** |
| **AC-4 零漂移** | **MET** | §5：契约/schema/apps/依赖**零 diff**；C-04b `4b304c0c…`、M2-C1 `a82a7fc1…` 不变；pins 18/18；check PASS；scope ⊆ allowed_paths |
| **AC-5 门禁/证据/不夸大** | **MET** | §3 门禁表；本 EV + `RESOURCE-MANIFEST.json` + `logs/**`；limitation 见 §7；未写「8 项 residual 全部关闭」 |

## 4. 判别性实验（sha256 链）

详见 `logs/discriminative-sha-chain.txt`；实跑日志 `logs/red-before-fix.txt`、
`logs/discriminate-red.txt`、`logs/discriminate-green-after-restore.txt`。

1. **修复前 RED**（HEAD `4c42e11b8` 的 `library.py` + 新测试）：`-k artifact_membership` → **3 failed, 15 deselected**。
2. **修复后 GREEN**：3 passed。
3. **判别性回退**：把谓词临时改回 page/chapter join（`library.py` 临时 sha256
   `b3c230b559e569a901f23a21095819cdb047ebf3108fd863239b478c89f9401e`）→ **3 failed**（必须 RED）。
4. **逐字节复原**：从备份恢复修复版，`expected sha256 = actual sha256 =
   da07ccdb4d0590828658c859e6c606e1c2614d7c1dde52894d3b15957b1bd792` **MATCH**；`touch` 源文件后
   复跑 → **3 passed**（复绿）。
5. **定向 before/after**（完整两文件）：before（两文件逐字节回退到 HEAD 版本）**56 passed**；恢复修复版
   （两文件 SHA-256 MATCH）+ `touch` → **59 passed**。

## 5. 门禁（实跑，确切数字）

| 项 | 命令 | before | after | 判定 | 日志 |
|---|---|---|---|---|---|
| 定向 pytest | `pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings` | **56 passed** | **59 passed**（+3 新用例） | 不降 | `logs/targeted-before.txt` / `logs/targeted-after.txt` |
| 全量 pytest | `pytest tests -q -p no:warnings --tb=no` | **3369 passed / 10 skipped**（起点） | **3372 passed / 10 skipped**（251.43s） | +3，不降 | `logs/full-after.txt` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 18/18 | **PASS (all 18)**，EXIT 0 | 无变化 | `logs/pins.txt` |
| 治理 check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS (3 warnings) | **PASS (3 warnings)**，EXIT 0 | 无变化 | `logs/check-default.txt` |
| 治理 check（-TaskPath） | `... check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | PASS | **PASS (3 warnings)**，EXIT 0 | 无变化 | `logs/check-taskpath.txt` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | EXIT 0 | **EXIT 0** | 无变化 | `logs/api-inventory.txt` |
| scope | `git diff 4c42e11b8 --name-only` | — | 仅 `src/infrastructure/sqlite/library.py`、`tests/core/test_core_delete_preview_commands.py` ⊆ allowed_paths | PASS | `logs/scope.txt` |
| 零漂移 | `git diff --name-only 26aa0ca4a -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps pyproject.toml requirements*.txt uv.lock` | — | **空** | PASS | `logs/scope.txt` |
| 文件指纹 | `Get-FileHash` / `git hash-object` | — | 见 `logs/sha256-files.txt` | — | `logs/sha256-files.txt` |

- **pins 18/18 的契约 sha 对照**：C-04b `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52`、
  M2-C1 `a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e` —— 与冻结记录 §1/§1B 的 v1.2 登记一致，本卡**零改动**。
- scope 口径说明：`git diff 26aa0ca4a --name-only` 还会列出 Lead 已 push 的 RESIDUAL-2 closeout 文件
  （`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md`、
  `doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md`）与本卡卡面；这些不是本卡写入，本卡工作树 diff（vs HEAD `4c42e11b8`）只有上述 2 个文件。

## 6. 交付物

- 实现 + 测试（本卡 commit，显式 pathspec）：`25dc1523c`。
- `verification/FEA-12-CORE-C04B-RESIDUAL-3/{EV.md, RESOURCE-MANIFEST.json, logs/**}`（本目录）。
- Handoff：`doc/handoffs/FEA-12-CORE-C04B-RESIDUAL-3-25dc1523c.md`。
- 卡面「交付记录」（Lead 的 closeout 维护 status 与冻结记录 L-3 更新）。

## 7. 不构成什么 / limitation（不夸大）

- **正常数据行为零变化**：仅当 `media_artifacts.book_id` 与其 `page_id` 所属书不一致（**损坏 DB，属异常输入**）时，
  preview 的 `currentArtifactRevisionIds` 归属才改变；正常数据逐值不变。
- **不构成** representative/`currentRevisionId` 语义或 pointer 顺序变化：`core_service.py:1904-1930` 未改。
- **不构成**删除事务变更：`DELETE FROM media_artifacts WHERE book_id = ?` 未改；跨书损坏行在 FK 约束下可能使某一方向的
  删除 fail-closed（本卡只对齐 preview 集合与删除谓词；测试用「删除 artifact 所属书」这一 FK 安全方向实跑验证）。
- **不构成**契约修复：C-04b v1.2 / M2-C1 rev 2.15 的谓词文字由 RESIDUAL-2 落地；本卡只让代码与之一致。
- **不构成**「8 项 residual 全部关闭」：本卡只关闭 R-1 的**代码**侧；其余项状态以冻结记录 §4A/§4C 为准。
- **不构成** push 授权（Lead 统一）与 Task closeout（Lead 维护 `status`、冻结记录 L-3 状态）。

## 8. 复现

```powershell
cd 'G:\CODEX\New Manga'
C:/Python314/python.exe -m pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings
C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
git diff 4c42e11b8 --name-only
```
