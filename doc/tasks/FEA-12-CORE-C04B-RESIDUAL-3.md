---
id: FEA-12-CORE-C04B-RESIDUAL-3
title: R-1 代码修复：artifact 成员谓词补 media_artifacts.book_id（与 C-04b v1.2 / 删除谓词一致）
kind: implementation
governance_version: 3
status: done
approval: 用户 AUTORUN 指令（2026-11-08，全部授权/自主裁决/不询问用户）；权威 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（§2.1 R-1 事实：`library.py:1178-1190` page/chapter join vs 删除面 `:1920-1926` 与 `:1218-1225` 的 `book_id`；§3.3 末段「先契约 → 再实现卡 → 再复核」）；**DSH 裁决（2026-11-08，裁决人=DSH）**：拆出独立实现卡，依赖 `FEA-12-CORE-C04B-RESIDUAL-2`（契约先写谓词文字）；正常数据零变化；跨书损坏行保护集合偏差修复
suggested_owner: dsh
owner: c04b-impl
reviewer: null
depends_on:
  - FEA-12-CORE-C04B-RESIDUAL-2
base_commit: 26aa0ca4a
branch: null
worktree: null
integration_commit: 25dc1523c
delivery_head: 25dc1523c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-12-CORE-C04B-RESIDUAL-3
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md
  - doc/reviews/FEA-12-CORE-C04B-RESIDUAL-3-*.md
  - doc/handoffs/FEA-12-CORE-C04B-RESIDUAL-3-*.md
  - src/infrastructure/sqlite/library.py
  - tests/core/test_core_delete_preview_commands.py
  - verification/FEA-12-CORE-C04B-RESIDUAL-3/**
out_of_scope:
  - 契约字节（RESIDUAL-2 负责；本卡实现期 pins 18/18 零改动）
  - schema/迁移/依赖；wire/命令/能力/错误码/`PROTOCOL_MINOR`
  - 删除事务本身（`DELETE FROM media_artifacts WHERE book_id = ?` 不变）
  - `apps/**`、App/UI、Host 侧
  - 其它 residual（R-2/R-3/R-4/R-5/R-8 的**契约文字**由 RESIDUAL-2 修正；本卡不重复改）
  - STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-12-CORE-C04B-RESIDUAL-3：R-1 artifact 成员谓词代码修复

> **状态：`proposed`（待 `FEA-12-CORE-C04B-RESIDUAL-2` 完成后释放）。**
> 依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md` §2.1（代码事实与风险）+
> `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A **L-3**（本偏差的 limitation 登记）。

## 目标

把 `list_book_artifact_current_pointers`（`src/infrastructure/sqlite/library.py:1178-1190`）的 artifact 成员谓词
从 **page/chapter join** 改为 **`media_artifacts.book_id = 本书`**，与删除路径（`:1920-1926`）和
`list_book_artifact_revision_ids`（`:1218-1225`）一致；与 C-04b v1.2 的谓词文字对齐。
**正常数据行为零变化**；仅修复「`media_artifacts.book_id` 与其 `page_id` 所属书不一致」的损坏行下
preview current 保护集合与删除集合不一致（多绑定/少绑定）。

## Acceptance Criteria

- [x] **AC-1 谓词对齐**：`list_book_artifact_current_pointers` 使用 `media_artifacts.book_id = ?`；不再依赖 page/chapter join 判定成员；静态断言 Core 内「preview 侧与删除侧的 artifact 成员谓词同源/一致」。 <<MET>>
- [x] **AC-2 正常数据零回归**：既有 `tests/core/test_core_delete_preview_commands.py` 全绿；对 book_id 与 page 所属书一致的正常数据，preview 的 `currentArtifactRevisionIds` 与修复前逐值相同（真实库 + 真实数据形态）。 <<MET>>
- [x] **AC-3 损坏行判别**：新增用例——构造 `media_artifacts.book_id=A` 但 `page_id` 属于 B 的损坏行 → 修复后 **A 的 preview 包含该 artifact、B 的 preview 不含**（与删除集合一致：删除 A 时 `DELETE FROM media_artifacts WHERE book_id='A'` 会带走它）；反向行（`book_id=B`/页属 A）同理；判别性：把谓词改回 page join → 红。**注（closeout 更正，R3-001）**：本行原写「A 不含 / B 含」系方向笔误，实现与测试自始按「与删除集合一致」= **A 含 / B 不含** 落地并双向覆盖。 <<MET>>
- [x] **AC-4 零漂移**：`schema.py`/`apps/**`/契约字节/依赖零 diff；pins **18/18**；`check.ps1` PASS；scope ⊆ allowed_paths。 <<MET>>
- [x] **AC-5 门禁/证据/不夸大**：定向 pytest + 全量 pytest 不降（起点 **3369/10**）；EV/Manifest/Closeout 完整；**不得**写「正常数据行为变化」；损坏 DB 属异常输入，修复后仅消除偏差。 <<MET>>

## 依赖与下一步

- 依赖：`FEA-12-CORE-C04B-RESIDUAL-2`（C-04b v1.2 谓词文字必须先落地）。
- 完成后：`L-3` 状态由「未修」更新为「已修（RESIDUAL-3）」，并在冻结记录 §4A 与 R-1 行更新（**由 Lead 在 closeout 维护**）。

## 交付记录（c04b-impl，2026-11-08）

- **delivery_head**：`25dc1523c`（`git rev-parse HEAD` = `25dc1523c8afc2083a03e478dc65d4ee9c36cf5c`；实现+测试 commit）
- **commit 链**：`25dc1523c`（`fix(fea-12-core-c04b-residual-3)`：`src/infrastructure/sqlite/library.py` +
  `tests/core/test_core_delete_preview_commands.py`）→ 紧随其后的 docs/evidence commit（本卡交付记录 +
  `doc/handoffs/FEA-12-CORE-C04B-RESIDUAL-3-25dc1523c.md` + `verification/FEA-12-CORE-C04B-RESIDUAL-3/**`）
- **AC 判定**：AC-1…AC-5 全部 MET（逐条见上；`<<MET>>` 已就位于各 AC 行末）
- **门禁（before → after）**：
  - 定向 `pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings`：
    **56 passed → 59 passed**（+3 新用例）
  - 全量 `pytest tests -q -p no:warnings --tb=no`：**3369 passed / 10 skipped → 3372 passed / 10 skipped**
    （251.43 s，不降）
  - `verify_pins.ps1`：**PIN AUDIT: PASS (all 18)**，EXIT 0；契约零改动（C-04b `4b304c0c…`、M2-C1 `a82a7fc1…`
    与冻结记录 §1/§1B 一致）
  - `check.ps1`（默认 / `-TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`）：**PASS (3 warnings) ×2**
  - `generate_api_inventory.py --check`：**EXIT 0**
  - scope：实现 diff（vs `4c42e11b8`）仅 `src/infrastructure/sqlite/library.py`、
    `tests/core/test_core_delete_preview_commands.py` ⊆ allowed_paths；契约/`doc/plan`/`doc/contracts`/
    `schema.py`/`apps/**`/依赖 **零 diff**
- **判别性计数**：修复前基线 **3/3 RED**；把谓词改回 page/chapter join → **3/3 RED**；逐字节复原
  **sha256 MATCH**（`da07ccdb4d0590828658c859e6c606e1c2614d7c1dde52894d3b15957b1bd792`）+ `touch` →
  **3/3 GREEN**
- **AC-3 方向说明**：卡面 AC-3 文字写「修复后 A 的 preview **不含**、B 的 preview **包含**它」；按同一行括号内的
  判定基准「**与删除集合一致**」及 C-04b v1.2 §0 第 1 条谓词，正确结果是 **`book_id=A` 侧包含、B 侧不含**
  （删除事务按 `WHERE book_id = A` 删除该行；旧 page/chapter join 才给出 A 不含/B 含）。实现按括号基准落地，
  并以**双向两行**（`book_id=A`/页属 B、`book_id=B`/页属 A）覆盖两个方向，任何读法下均可判别。
- **limitation（不夸大）**：**正常数据零变化**；仅在 `media_artifacts.book_id` 与 page 所属书不一致的
  **损坏 DB（异常输入）**下改变归属，修复后仅消除该偏差。representative/`currentRevisionId` 语义与顺序逻辑未改；
  删除事务未改；**未**声称「8 项 residual 全部关闭」——只写「R-1 的代码侧已与 C-04b v1.2 谓词一致」。
  未 push、未 closeout（`status` 与冻结记录 L-3 由 Lead 维护）。
- **证据**：`verification/FEA-12-CORE-C04B-RESIDUAL-3/{EV.md, RESOURCE-MANIFEST.json, logs/**}`。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-1..AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-3/EV.md | 2babb0c78 | 821d9f4da5ee7e1b1b2a2fb05cf422548dbd2fb2d61140654feaa72596ab4c29 | CANONICAL |
| EV-02 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/api-inventory.txt | 2babb0c78 | b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47 | CANONICAL |
| EV-03 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/check-default.txt | 2babb0c78 | 92b00387951acb14be3c7207cbc194d89a0080665624454e3f58cf1e65128a59 | CANONICAL |
| EV-04 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/check-taskpath.txt | 2babb0c78 | 92b00387951acb14be3c7207cbc194d89a0080665624454e3f58cf1e65128a59 | CANONICAL |
| EV-05 | AC-3 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/discriminate-green-after-restore.txt | 2babb0c78 | 84a0a163a78814956bcf8cf19344d40d1b997c43068c1d5ce2792044b45c4d7c | CANONICAL |
| EV-06 | AC-3 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/discriminate-red.txt | 2babb0c78 | 9a811c07d9a685745034fa14aa024302a4dfbe01f169602bf9a91208dbbac8a0 | CANONICAL |
| EV-07 | AC-3 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/discriminative-sha-chain.txt | 2babb0c78 | 9c2ca937363ec99662ed0b5458b8158d39c9ba17d2996b7deb276b65e3e77e7b | CANONICAL |
| EV-08 | AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/full-after.txt | 2babb0c78 | e0f54b3835e176a719b95e6ee901706a615fc02548a56f0f006278cb71c87ebf | CANONICAL |
| EV-09 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/pins.txt | 2babb0c78 | aedf5a6b579c255e4b1544ccc1479aaf8517d6cdd711f9e7a12018f08e6f118d | CANONICAL |
| EV-10 | AC-3 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/red-before-fix.txt | 2babb0c78 | 1ab79ac8e8249b7ee79f848f3fd8b552666e2118742c5cdd8c9bc093df8c4c08 | CANONICAL |
| EV-11 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/scope-post-commit.txt | 2babb0c78 | c3f8e2b4a65e8fbaa6c57f5ab75ad2173ccc0f44b4644e628c8906e139cdcc83 | CANONICAL |
| EV-12 | AC-4 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/scope.txt | 2babb0c78 | ff8fc970696e41c8d8c333c94ff4527413aebac375682b735f488a323f1b1dd4 | CANONICAL |
| EV-13 | AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/sha256-files.txt | 2babb0c78 | 408c6686ad6b985e2e57e3ca42c7d809aa2e56b75a484f900223fc691a5ec8c8 | CANONICAL |
| EV-14 | AC-2/AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/targeted-after.txt | 2babb0c78 | 7e59671ec44e4d1b59c87ec8427aaf0a11a26078db0deff0d2b19115db41568e | CANONICAL |
| EV-15 | AC-2/AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-3/logs/targeted-before.txt | 2babb0c78 | 2b5a3e5222cd2ed71e51abebea47c076519dbf69ad0066aa90231ac2c7fccdce | CANONICAL |
| EV-16 | AC-5 | verification/FEA-12-CORE-C04B-RESIDUAL-3/RESOURCE-MANIFEST.json | 2babb0c78 | 967f17d3eb8a3b28bd9be1de7da4bd2ce260971607e51d514b1b957a63cdd04b | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；仅改 `library.py` + 测试 + 卡/评审/证据；仓外 `workspace\C04B-RESIDUAL\review-r3` 备份/基准库保留（无独有数据）；无残留进程 |

## Closeout Record（2026-11-08；Lead）

- **状态**：`done`；`integration_commit`/`delivery_head` = **`25dc1523c`**（实现+测试）；docs/evidence = `6e20d5d28` + `2babb0c78`（`reviewed_head=25dc1523c`，evidence HEAD=`2babb0c78`，两者代码部分一致）。
- **AC 判定**：AC-1…AC-5 **全 MET**（AC-3 方向文字已按 R3-001 更正为「A 含 / B 不含」，实现与测试自始按此落地）。
- **Review 链**：独立 fresh subagent **r1 `approved`（P0=0/P1=0/P2=2/P3=4；session `a4b5d82e-…`）**；reviewer 独立复跑判别性（回退谓词 → 3 failed → 复原 `da07ccdb…` MATCH + touch → 3 passed）、pins 18/18、check×2、API、manifest 15/15 MATCH。
- **Lead 集成门禁**：全量 pytest **3372 passed / 10 skipped**（起点 3369/10 → +3，不降）；pins **18/18**（契约零改动）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API EXIT=0；scope：实现仅 `library.py` + 测试 2 文件，`doc/plan`/`doc/contracts`/`schema.py`/`apps/**`/依赖 **零 diff**。
- **实现要点**：`list_book_artifact_current_pointers` 成员谓词 `WHERE c.book_id = ?` → **`WHERE ma.book_id = ?`**（保留 `current_revision_id IS NOT NULL`、不过滤可见性），pages/chapters 改 `LEFT JOIN`（仅阅读序排序 + `page_id` 投影）；阅读序 7 键逐项保留；与删除面 `DELETE FROM media_artifacts WHERE book_id = ?`、`list_book_artifact_revision_ids` 同源；`core_service.py`/representative/删除事务零改动。
- **P2/P3 处置**：**R3-001**（卡面 AC-3 方向笔误）→ 已在本 closeout 更正；**R3-002**（`media_artifacts.book_id` 无索引 → 计划退化为 `SCAN ma`，60k artifacts 实测 0.26→5.32 ms/书）→ **登记为冻结记录 §4A `L-4`**（建议后续独立 schema 卡加 `idx_media_artifacts_book(book_id)`；本卡 AC-4 要求 `schema.py` 零 diff，故本卡不改）；**R3-003**（损坏数据下 `currentRevisionId` 展示值可能随成员/排序键变化，规则未改、不进 digest）→ 本记录 limitation 已含；**R3-004**（`preview_lifecycle` 清理枚举按 page 归属，损坏行可能漏清，pre-existing）→ 登记 §4A **`L-5`**；**R3-005**（HEAD 口径：`reviewed_head=25dc1523c` / evidence HEAD=`2babb0c78` / 20 文件）→ 已在本条写明；**R3-006**（静态断言 `inspect.getsource` 白空格脆性）→ 登记为 follow-up（非阻塞）。
- **limitation 保留**：正常数据零变化；损坏 DB 属异常输入；**L-4**（无 `book_id` 索引的性能回退）、**L-5**（preview_lifecycle 漏清，pre-existing）**未修**；representative/删除事务未改。**不得**写「8 项 residual 全部关闭」——准确口径：R-1～R-8 均已处置（R-6 闭合、R-7 由 rev 2.15 落地、R-1/R-2/R-3/R-4/R-5/R-8 契约文字由 RESIDUAL-2 修正，**R-1 代码由本卡修复并与契约一致**），但 **L-1/L-2/L-4/L-5 等运行限制仍在**。
- **Resource Manifest**：仓内 0 删除/0 移动/0 归档；仓外备份保留。
- **指针清理**：Lead 更新 STATUS/PLAN/TASK_LEDGER。
- **push**：随本轮 Lead 统一 push（记录见 handoff §25）。
