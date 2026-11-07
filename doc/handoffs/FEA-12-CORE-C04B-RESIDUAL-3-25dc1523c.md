---
task_id: FEA-12-CORE-C04B-RESIDUAL-3
author: c04b-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 26aa0ca4a
start_head: 4c42e11b8
delivery_head: 25dc1523c
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-12-CORE-C04B-RESIDUAL-3（R-1 artifact 成员谓词代码修复，0 pin）

- Task：`doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`（`status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-08（Asia/Shanghai）
- 权限依据：卡面 `status: ready`（Owner=`c04b-impl`）+ 权威 scope review
  `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md` §2.1（R-1 代码事实）与 §3.3 末段
  （「先契约 → 再实现卡 → 再复核」）+ 依赖 `FEA-12-CORE-C04B-RESIDUAL-2`（C-04b v1.2 + M2-C1 rev 2.15，
  已 push 于 `26aa0ca4a`）
- **三处 head 区分**：卡面 `base_commit=26aa0ca4a`（RESIDUAL-2 契约 UNFREEZE）→ 派发/实施起点
  `4c42e11b8`（Lead 已 push 的 RESIDUAL-2 closeout 记录，本卡 diff 以此为基准）→
  **`delivery_head=25dc1523c`**（实现+测试 commit；本 Handoff / EV / 证据 / 卡面交付记录为紧随其后的
  docs/evidence 提交）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14；真实 production migrations（`assemble_production_core`，v8）；
  无新依赖、零 schema/迁移、零 wire/命令/能力/错误码/`PROTOCOL_MINOR`、零契约字节、零 `apps/**`
- **未 push、未 closeout**：Task `status`、冻结记录 §4A L-3/R-1 行、STATUS/PLAN/LEDGER 由 Lead 维护

## 1. 交付结果（AC-1…AC-5 全 MET；卡面已 `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-1 谓词对齐** | MET | `list_book_artifact_current_pointers` 成员谓词 = **`WHERE ma.book_id = ? AND ma.current_revision_id IS NOT NULL`**；页/章 JOIN 改为 `LEFT JOIN`，只承担阅读序排序与 `page_id` 投影；静态断言三处谓词同源（preview / `list_book_artifact_revision_ids` `ma.book_id = ?` / 删除面 `DELETE FROM media_artifacts WHERE book_id = ?`），并断言 `c.book_id = ?` 不再出现、`ORDER BY c.sort_order, c.import_order, c.chapter_id … ma.artifact_type, ma.artifact_id` 保留 |
| **AC-2 正常数据零回归** | MET | 新增用例先断言正常数据 `["ar-a"]`/`["ar-b"]`；既有 `test_preview_binds_artifact_current_set`（`["ar1"]`→`["ar2"]`）等 preview 测试全绿；定向 **56→59**；全量 **3369/10→3372/10** |
| **AC-3 损坏行判别** | MET | 正向：`ma-x`（`book_id=book-a`、`page_id` 属 book-b）→ book-a 的 preview 含 `arv-x`、book-b 不含；**实跑** `PermanentlyDeleteBook(book-a)` 删除 `arv-x`（与删除集合一致）。反向：`ma-y`（`book_id=book-b`、页属 book-a）→ book-b 含、book-a 不含，删除 book-b 带走 `arv-y`。判别性：谓词改回 page/chapter join → **3/3 RED**；逐字节复原 sha256 MATCH + `touch` → **3/3 GREEN**（见 §4） |
| **AC-4 零漂移** | MET | 契约/schema/`apps/**`/依赖 **零 diff**；C-04b `4b304c0c…`、M2-C1 `a82a7fc1…` 与冻结记录 §1/§1B 一致；pins **18/18**；check 默认与 `-TaskPath` **PASS (3 warnings)**；scope ⊆ allowed_paths |
| **AC-5 门禁/证据/不夸大** | MET | `verification/FEA-12-CORE-C04B-RESIDUAL-3/{EV.md, RESOURCE-MANIFEST.json, logs/**}`；定向/全量不降；未写「8 项 residual 全部关闭」，只写「R-1 的代码侧已与 C-04b v1.2 谓词一致」 |

## 2. 代码变更（唯一生产改动）

`src/infrastructure/sqlite/library.py`（`git diff --numstat 4c42e11b8` = **+18/−4**）：

```sql
-- before（page/chapter join 判定成员）
WHERE c.book_id = ? AND ma.current_revision_id IS NOT NULL
-- after（成员 = media_artifacts.book_id；JOIN 仅用于阅读序）
WHERE ma.book_id = ? AND ma.current_revision_id IS NOT NULL
```

- `JOIN pages/chapters` → `LEFT JOIN`：成员集合不再因 page/chapter 链条断裂而丢行，成员判定只由 `ma.book_id` 决定。
- **保留** `current_revision_id IS NOT NULL`、不按可见性过滤、阅读序排序键**逐项不变**。
- **未改** `core_service.py`（不在写域）：`currentRevisionId` = 阅读序首个 lineage-visible region current，
  否则**首个 artifact current pointer**（局部列表阅读序、**非字典序**）；`_finalize_delete_inventory` 未动。
- 删除事务 `DELETE FROM media_artifacts WHERE book_id = ?` **未改**（`out_of_scope`）。

## 3. 验证证据（实跑；`delivery_head=25dc1523c`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向 before | `pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings`（两文件逐字节回退到 `4c42e11b8`） | **56 passed** | `verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/targeted-before.txt` |
| 定向 after | 同上（恢复修复版，两文件 sha256 MATCH + `touch`） | **59 passed**（+3） | `logs/targeted-after.txt` |
| 全量 | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | **3372 passed / 10 skipped**（251.43 s；起点 3369/10，不降） | `logs/full-after.txt` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | `logs/pins.txt` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT 0 | `logs/check-default.txt` |
| check（`-TaskPath`） | `... check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md` | **PASS (3 warnings)**，EXIT 0 | `logs/check-taskpath.txt` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT 0** | `logs/api-inventory.txt` |
| scope / 零漂移 | `git diff 4c42e11b8 --name-only`；`git diff --name-only 26aa0ca4a -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps pyproject.toml requirements*.txt uv.lock` | 实现 diff 仅 2 文件 ⊆ allowed_paths；契约/schema/apps/依赖 **空** | `logs/scope.txt` |
| 指纹 | `Get-FileHash` / `git hash-object` | `library.py` sha256 `da07ccdb…`；测试 `5c350d3e…`；契约 sha 不变 | `logs/sha256-files.txt` |

## 4. 判别性实验（3/3 RED → sha256 MATCH → 3/3 GREEN）

详见 `EV.md` §4 与 `logs/discriminative-sha-chain.txt`：

1. 修复前 RED（HEAD `library.py` + 新测试）→ **3 failed**（`logs/red-before-fix.txt`）。
2. 修复后 GREEN → 3 passed。
3. **判别性回退**：谓词临时改回 page/chapter join → **3 failed**（`logs/discriminate-red.txt`）。
4. **逐字节复原**：`expected = actual =
   da07ccdb4d0590828658c859e6c606e1c2614d7c1dde52894d3b15957b1bd792` **MATCH**；`touch` 后复绿
   → **3 passed**（`logs/discriminate-green-after-restore.txt`）。

## 5. AC-3 方向说明（如实登记）

卡面 AC-3 文字为「`media_artifacts.book_id = A` 但 `page_id` 属于 B → **A 的 preview 不含**、**B 的 preview 包含**它
（与删除集合一致）」。按括号基准（**与删除集合一致**）与 C-04b v1.2 §0 第 1 条谓词，正确结果是 **A 含 / B 不含**
（删除事务按 `WHERE book_id = A` 删除该行）；「A 不含 / B 含」恰是旧 page/chapter join 的行为。本卡按括号基准实现，
并**双向两行**覆盖两个方向，任何读法下均可判别；未按文字方向反向实现。

## 6. Limitation / 不构成什么（不夸大）

- **正常数据行为零变化**；只有 `media_artifacts.book_id` 与 page 所属书不一致的**损坏 DB（异常输入）**才改变归属。
- **不构成** representative/`currentRevisionId` 语义或 pointer 顺序变化（`core_service.py` 未改）。
- **不构成**删除事务变更；跨书损坏行在 FK 约束下可能使某一方向删除 fail-closed（本卡只对齐 preview 集合与删除谓词；
  测试用「删除 artifact 所属书」这一 FK 安全方向实跑验证）。
- **不构成**契约修复（C-04b v1.2 / M2-C1 rev 2.15 由 RESIDUAL-2 落地）与 pin 变化；**不构成**「8 项 residual 全部关闭」。
- **不构成** push 授权与 Task closeout；L-3 的「未修 → 已修」由 Lead 在 closeout 维护。

## 7. 建议下一步（Lead）

1. 派发**上下文独立 Review**（只读 `delivery_head=25dc1523c`；reviewer 未参与本卡实现）。
2. Review approved 后 closeout：冻结记录 §4A **L-3** → 「已修（RESIDUAL-3）」、R-1 行「代码已与契约一致」；
   STATUS/PLAN/LEDGER 更新；push。

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
