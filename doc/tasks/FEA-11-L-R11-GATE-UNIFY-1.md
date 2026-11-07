---
id: FEA-11-L-R11-GATE-UNIFY-1
title: L-R11 两读面 publication gate 统一（Core 单谓词；legacy open / 新同步链缺行 fail-closed；全链检测）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（session `5aa2c0cf…`；recommended；方案 C 单谓词 + 全链）；**DSH 裁决（2026-11-07）**：先 `FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（C-16 v1.7，1 pin；**已 done `2175238ab`，r1 byte-level approved**）→ 本卡（Core-only，0 pin）**已释放（2026-11-07）**；`added` relation 缺行检测与写面/章级面 **Out**（登记 limitation）
suggested_owner: zcode
owner: l-r11-impl
reviewer: 独立上下文 fresh subagent（r1 approved P0=0/P1=0/P2=0/P3=5；session 见 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-r1.md`）
depends_on:
  - FEA-11-RENDITION-1
  - FEA-11-RUN-GRANT-2C
  - FEA-11-L-R11-GATE-UNIFY-PREREQ-1
base_commit: 2175238ab
branch: null
worktree: null
integration_commit: 86cd1d124
delivery_head: 86cd1d124
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-L-R11-GATE-UNIFY-1
allowed_paths:
  - doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md
  - doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-*.md
  - doc/handoffs/FEA-11-L-R11-GATE-UNIFY-1-*.md
  - verification/FEA-11-L-R11-GATE-UNIFY-1/**
  - src/infrastructure/sqlite/source_sync.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - tests/fea11/test_source_gate_unify.py
out_of_scope:
  - 契约字节（PREREQ 卡负责；实现期 18 pins 零改动）
  - schema/迁移（`schema.py` 零 diff）、wire/命令/能力/错误码/`PROTOCOL_MINOR`、依赖
  - `apps/**`、App/UI、Host 接线、Run wire
  - RENDITION-1 的 provider/选择语义；`managed_original_ref` 混合页取舍（L-R5）
  - 写面 `_refuse_pending_gate_writes` / 章级 `_refuse_pending_gate_chapter` 的 pending-only 语义（L-R11-b）
  - `relation='added'` 缺行检测（plan receipt / 新持久标记；L-R11-a）
  - 损坏 publication 行的自动修复/重建（L-R11-d）
  - C-04b/SCAN-RH/UI P3；STATUS/PLAN/LEDGER；push
---

# FEA-11-L-R11-GATE-UNIFY-1：L-R11 两读面 publication gate 统一（Core-only）

> **状态：`ready`（已释放 2026-11-07；Owner=`l-r11-impl`；base=`2175238ab`）。** 依赖已满足：`FEA-11-L-R11-GATE-UNIFY-PREREQ-1`
> **done**（C-16 v1.7，1 pin，r1 byte-level approved）、`FEA-11-RUN-GRANT-2C` done（共享 `tests/fea11/test_source_run_grant.py`）。
> 依据：`doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（recommended；已复现 L-R11 一跳形态、发现两跳链两面均放行、
> `added` 缺行不可检测）+ C-17 §3.3（`:171-173`）+ C-16 v1.7 §2.4。

## 目标

统一 Core 内 publication gate 判定为**唯一谓词**：healthy + 行状态 + **全链**检测；**旧 v7 legacy 无行 open**；
**新同步链缺 publication 行 fail-closed**；由 `core_assembly.read_gate`、`core_service._assert_source_sync_gate` 与
`AuthorizeSourceReadForRun` 的 per-page 路径共同消费。修复 L-R11 一跳分歧与 scope review 新发现的**两跳链**
（B3/B2 无行、B1 有行时两面均放行，违反 C-17 §3.3 全链 fail-closed）。

## 候选范围

- **In**：`src/infrastructure/sqlite/source_sync.py`（或 `SourceSyncLineageFacts` 所在模块）实现单谓词（返回
  `open`/`pending`/`unavailable`/`corrupt_chain`，组装层把 `corrupt_chain` 映射既有 `unavailable`）；`core_assembly.read_gate`
  委托；`core_service._assert_source_sync_gate` 委托；`AuthorizeSourceReadForRun` per-page 经 `catalog.source_gate_reader`
  消费同一谓词；新增 `tests/fea11/test_source_gate_unify.py`（真实 v7→v8 migration fixture、真实 grant、真实
  assembly；含 legacy / 一跳 / 两跳 / pending/open 回归 + 判别性）。
- **Out**：见 frontmatter `out_of_scope`。

## Acceptance Criteria（草案，冻结时定稿）

- [x] **AC-1 单谓词唯一**：Core 内只有一处 publication-gate 判定（`_publication_gate_verdict` → `SourceSyncStore.publication_gate_of_page`）；`read_gate`/`_assert_source_sync_gate`(+复数)/`AuthorizeSourceReadForRun` per-page 均消费它；旧一跳启发式已删、docstring 已修；静态唯一性 + 判别性 R3。 <<MET>>
- [x] **AC-2 legacy 零回归**：真实 v7→v8 migration 库（previous NULL 与「previous 非空但全链无 publication」两种形态）均 `read_gate=="open"`；resolve/provider/target/commit/Authorize 行为与修复前一致；判别性 M1「无行即 corrupt」→ 红。 <<MET>>
- [x] **AC-3 L-R11 一跳 fail-closed**：v8 库 B1(publication open)+B2(无行,previous=B1) → read_gate 拒绝、resolve `SOURCE_ACCESS_DENIED`、provider 0 次 prepare/read、`create_run` `TARGET_NOT_FOUND`、commit guard 拒绝、Authorize typed 拒绝零映射；判别性 M2 → 红。 <<MET>>
- [x] **AC-4 全链检测（两跳）**：B3/B2 无行、B1 有行 → 同样 fail-closed；判别性 M3「改回只查一跳」→ 红。 <<MET>>
- [x] **AC-5 零漂移**：18 pins 零改动（C-16 v1.7）；`schema.py`/`apps/**`/依赖零 diff；无新错误码/命令/能力/`PROTOCOL_MINOR`；`src/**` diff ⊆ allowed_paths（仅 3 文件）；实跑 pins 18/18、`git diff --check` 0。 <<MET>>
- [x] **AC-6 门禁/证据/不夸大**：定向 78 passed、`tests/fea11` 212 passed、全量 pytest 3369/10 不降、check PASS、API EXIT 0、scope 合规；EV/Handoff 完整、`L-R11-a…e` 已登记；**无**「C-17 §3.3 完全实现 / L-R11 全部关闭」表述；判别性 4/4；独立 r1 approved。 <<MET>>

## 预登记 limitation（实现时如实保留）

- **L-R11-a**：`relation='added'` 的新同步 binding 缺 publication 行（previous NULL）时，链检测不可见，无法与 v7
  legacy 区分；C-17 §3.3 的 plan receipt 检测未实现。本卡只覆盖 previous 链可检测的损坏子集。
- **L-R11-b**：写面与章级面仍 pending-only；损坏链形态下编辑/章级预检仍放行，直到逐页 resolve 拒绝。
- **L-R11-c**：损坏状态映射既有 `unavailable`/`TARGET_NOT_FOUND`/`INVALID_INPUT`/`SOURCE_ACCESS_DENIED`，无专用诊断码
  （C-17 §8 禁止新增码）。
- **L-R11-d**：不提供损坏 publication 行的自动修复/重建。
- **L-R11-e**：优先真实 `MigrationRunner(..., MIGRATIONS[:7])` 造 v7 再升级；若只用 v8 内 legacy 形态须在卡面写明。

## 依赖与下一步

- 依赖：`FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（C-16 v1.7，done 后 DSH 冻结释放）；`FEA-11-RUN-GRANT-2C`（done，共享
  `tests/fea11/test_source_run_grant.py` 基线）。
- Release 后走实现 → 独立 Review → 集成门禁 → closeout → push。

## 交付记录（Owner 回填；不改 status）

- **交付完成（2026-11-08）**：`delivery_head=86cd1d124`；commit 链 `1c1c9ca2f`（实现：`source_sync.py` 单谓词
  `_publication_gate_verdict` + `SourceSyncStore.publication_gate_of_page` + 全链 walk `_binding_chain_ids`；
  `core_assembly.read_gate` 委托并把 `corrupt_chain`→`unavailable`；`core_service._assert_source_sync_gate` 委托并删除
  一跳 `previous_binding_id` 启发式）→ `86cd1d124`（`tests/fea11/test_source_gate_unify.py` 6 例：真实 v7→v8 legacy /
  一跳 / 两跳 / pending-open / 无 binding / 静态唯一性，全部真实 migrations+zip+grant+`assemble_core_services`）。
  随后同批 docs/evidence 提交（本卡面 / Handoff / `verification/FEA-11-L-R11-GATE-UNIFY-1/**`）。实现起点实测
  `28a2826af`（派发说明写 `8584f412f`）；落地于 Lead 并发 docs 提交 `2e4d6128e` 之上。
- **AC 判定**：AC-1…AC-6 **全 MET**（逐项 `<<MET>>`；见 `verification/FEA-11-L-R11-GATE-UNIFY-1/EV.md` §3）。
- **实跑门禁（before → after）**：定向 pytest **78 passed**（既有 72 + 新增 6）；`tests/fea11` 全量
  **206 → 212 passed**；全量 `pytest tests` **3363/10 → 3369/10**（+6，不降、skip 不变）；`verify_pins.ps1`
  **18/18**（C16 v1.7 `67286eec…`、C17 `aefa0fa5…`）；`check.ps1` 默认 + `-TaskPath` **PASS(3 warnings)×2**；
  API inventory **EXIT=0**；scope 通过（`src/**` 仅 3 个 allowed 文件；契约/schema/apps **0 字节**；无新错误码/
  命令/能力/`PROTOCOL_MINOR`/依赖）；build / 全量 .NET / 真实 IPC **N/A**（纯 Python Core + tests，零 App/Host/wire）。
- **判别性**：**4/4 RED_AS_EXPECTED + 复原 sha256 2/2 MATCH + 复绿**（M1「无行即 corrupt」→ legacy RED；M2 分支改回
  open → 一跳/两跳 RED；M3 改回一跳 → 两跳 RED、一跳 PASS；M4 resolve 面改回一跳启发式 → 静态唯一性 RED；
  `logs/discriminative/**`）。
- **行为口径**：正常 legacy / 导入 / sync 库零变化；仅「新同步链缺 publication 行」的损坏形态由放行变 fail-closed
  （Run `TARGET_NOT_FOUND`、provider `INVALID_INPUT`、resolve/reader `SOURCE_ACCESS_DENIED`、
  `AuthorizeSourceReadForRun` typed 拒绝且零映射），全部映射既有 family、无新增码。
- **Limitation 保留**：L-R11-a（`relation='added'` 缺行不可检测 / plan receipt 未实现）、L-R11-b（写面/章级面仍
  pending-only）、L-R11-c（无专用诊断码/无新增日志行）、L-R11-d（不自动修复损坏行）、L-R11-e（legacy 用真实
  v7→v8 migration，非 v8 伪造）。**不夸大**：未写「C-17 §3.3 已完全实现 / L-R11 全部关闭」；实现 ≠ 集成，待独立
  Review 与 Lead 集成门禁。
- **证据目录**：`verification/FEA-11-L-R11-GATE-UNIFY-1/`（`EV.md`、`RESOURCE-MANIFEST.json`、`logs/**`）。未 push、
  未建 worktree；`status` 未改（由 Lead 维护）；未自行 closeout。
## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/EV.md | 1e339f30a | 49d1b64f91e89880fc1e185cebf600d910fd1e82dabe6ee74a69ed04a7227a36 | CANONICAL |
| EV-02 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/discriminative/M1-no-row-is-corrupt.log | 1e339f30a | a2954c14b5b05753d6a70c5efdda44fbace4584eb64ab92e9fcf67e8ebd12061 | CANONICAL |
| EV-03 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/discriminative/M2-missing-row-is-open.log | 1e339f30a | 8347029fbb0aebb4c18c5423291779e97c9fd462e17a6bc201cc82e796ddafeb | CANONICAL |
| EV-04 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/discriminative/M3-one-hop-only.log | 1e339f30a | 0b371c5b4a55086f1c126ceeaaff0b79cc9ca858b004c37500415486dfc7ff2d | CANONICAL |
| EV-05 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/discriminative/M4-resolve-face-own-heuristic.log | 1e339f30a | 76fd4e7920050adaf3693e6112712f96243b313242dd4b187b8d56fc766d5b3e | CANONICAL |
| EV-06 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/discriminative/M5-restored-green.log | 1e339f30a | 40bc778be4167da7f4e91f09217f6322e714aeb20ce4172df207cbec3cabce33 | CANONICAL |
| EV-07 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/discriminative/SUMMARY.txt | 1e339f30a | e439e07c77178197dcb28ef4e2e572159b50f4a519948733b3895bf6d071a8f4 | CANONICAL |
| EV-08 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/governance/api-inventory.log | 1e339f30a | 6d1e41178756c82c9500e141743fe5783c00f75d4ca09b4c6206323efb02e4b7 | CANONICAL |
| EV-09 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/governance/check-taskpath.log | 1e339f30a | 14c26f634bb92644cb95b1f1b69ce8189c106526ea99e97c2a2297ca815439b3 | CANONICAL |
| EV-10 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/governance/check.log | 1e339f30a | 14c26f634bb92644cb95b1f1b69ce8189c106526ea99e97c2a2297ca815439b3 | CANONICAL |
| EV-11 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/governance/pins.log | 1e339f30a | bbd82df4d119205b7198d08acac40ad87418d7b54dab5cd9142c02932cae7128 | CANONICAL |
| EV-12 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/final-tree-fea11.log | 1e339f30a | d983361603a69efce4c94d55050158b8d436888bd1c23934d2c81937d0b523a3 | CANONICAL |
| EV-13 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/final-tree-new-file.log | 1e339f30a | 6998440ce93a50fab6d5ba2ce1a3e473bb986b6a16416d760de05de0343dbe22 | CANONICAL |
| EV-14 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/full-pytest.log | 1e339f30a | 44fb193e579b3ce3741943ba85cefd56bd95f742f3094c64de634047d26a6e7a | CANONICAL |
| EV-15 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/new-file-verbose.log | 1e339f30a | e1084d15fa5205841a1981d75c2debbda42ce8a13c17602312ca11a978367e07 | CANONICAL |
| EV-16 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/targeted-gate-files.log | 1e339f30a | 9f2f1775565e81cf301d17c50381a960f21219ddf2db65e4199565438852f598 | CANONICAL |
| EV-17 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/tests-fea11-full.log | 1e339f30a | 48dfaa80ec8078891d9ea0d485949b2341298e223716ab89f3ae3a2fdcce5e86 | CANONICAL |
| EV-18 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/delivery-commits.log | 1e339f30a | 032f447ed39c3695a4b5def25f3f3421bf2b9562ad75e01b335c8635d327da00 | CANONICAL |
| EV-19 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/delivery-file-sha256.log | 1e339f30a | 0f4b28f031d9854aaf405ab4780da6d5242f55f5c1ced9263bb0cfb6846b5ffb | CANONICAL |
| EV-20 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/diff-check.log | 1e339f30a | 2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8 | CANONICAL |
| EV-21 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/diff-head-name-only.log | 1e339f30a | 4f8b714f86b073b0eb4ba704ea87b7ddd20f09f27a4a86799057c0575822232f | CANONICAL |
| EV-22 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/diff-head-stat.log | 1e339f30a | b8e6d56add80e664013dddf1d60b4c8d0b2abefc5cd115c1e0363f69c4317fbe | CANONICAL |
| EV-23 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/git-status.log | 1e339f30a | 4ccefbfaf04238ae442b05bdc1ceb721c5825d67a3707293bdabb439023fa74b | CANONICAL |
| EV-24 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/show-impl-stat.log | 1e339f30a | 48ee4e2994f8d484232afe8603d7696d09e6b15eb76a3f5e875fbe895e767d7e | CANONICAL |
| EV-25 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/show-test-stat.log | 1e339f30a | 0218986eff2fb089e54b8f6add15978d338c73caf7d3d92513a117d85bf44815 | CANONICAL |
| EV-26 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/src-changed.log | 1e339f30a | 4f8b714f86b073b0eb4ba704ea87b7ddd20f09f27a4a86799057c0575822232f | CANONICAL |
| EV-27 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/src-numstat.log | 1e339f30a | f31a6f2ca70483fff11eebb8b3c7f3fea6dc4836f6227106f07a9555208c0327 | CANONICAL |
| EV-28 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/logs/scope/zero-drift-contracts-schema-apps.log | 1e339f30a | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | CANONICAL |
| EV-29 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/RESOURCE-MANIFEST.json | 1e339f30a | 8f70a29faf7e364accffc282728b88a16b0ac2d69bace2f6abfa88bf952f43fe | CANONICAL |
| EV-30 | AC-1..AC-6 | verification/FEA-11-L-R11-GATE-UNIFY-1/tools/gen_manifest.py | 1e339f30a | 0e10a91f8d9a02ae15fad89d9658287a8900d3d425e4c692d57f8b436387f119 | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；仅改 3 个 src 文件 + 新测试 + 卡/评审/证据；无残留进程 |
## Closeout Record（2026-11-08；Lead）

- **状态**：`done`；`delivery_head`/`integration_commit` = **`86cd1d124`**（feat `1c1c9ca2f` → test `86cd1d124`；docs/evidence `1e339f30a`）。
- **AC 判定**：AC-1…AC-6 **全 MET**（无 PARTIAL/BLOCKED）。
- **Review 链**：独立上下文 fresh subagent **r1 `approved`（P0=0/P1=0/P2=0/P3=5 非阻断）**（报告 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-r1.md`；reviewed_head `86cd1d124`）。reviewer 独立复跑 3 个破坏点（R1「无行即 corrupt」/R2「全链改回一跳」/R3「resolve 面恢复旧启发式」）**3/3 RED + 复原 sha MATCH + 复绿**；manifest 33/33 sha MATCH。
- **Lead 集成门禁（2026-11-08 实跑）**：全量 pytest **3369 passed / 10 skipped EXIT=0**（起点 3363/10 → +6，不降）；pins **18/18**（C16 v1.7 `67286eec…`）；`check.ps1` 默认 + `-TaskPath` **PASS(3 warnings)**；API inventory **EXIT=0**；scope：实现+测试仅 `src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py` + `tests/fea11/test_source_gate_unify.py`（4 文件），`doc/plan`/`doc/contracts`/`schema.py`/`apps/**` **零 diff**，`git diff --check` 0。
- **实现要点**：`source_sync.py` 新增唯一谓词 `_publication_gate_verdict`（open/pending/unavailable/corrupt_chain）+ `SourceSyncStore.publication_gate_of_page` + 全链 walk `_binding_chain_ids`；`core_assembly.read_gate` 委托（corrupt_chain→unavailable）；`core_service._assert_source_sync_gate`(+复数) 委托并删除旧一跳 `previous_binding_id` 启发式；`read_gate` docstring 修正。**legacy 零漂移**（previous NULL 与「previous 非空但全链无 publication」均 open）；新同步链缺行（一跳/两跳）**全链 fail-closed**，各面映射既有 family（Run `TARGET_NOT_FOUND`、provider `INVALID_INPUT`、resolve/reader `SOURCE_ACCESS_DENIED`、Authorize typed 拒绝零映射）。
- **P3 保留（5 项，非阻断，不要求本卡返修）**：① manifest 的 3 个 src changed-file sha 为工作树 CRLF 字节（commit blob 为 LF；文本一致）——**EOL 口径记录**；② 无 publication 链的全链 walk 每代 2 条查询、reader 逐页潜在 N+1；③ 谓词多语句读取无显式只读快照（修复前已有的残余 TOCTOU，本卡略加长）；④ resolve 面对「非 healthy + pending」的 message 文本变化（错误码/类别/retryable 不变）；⑤ docstring「only judgement in Core」宜限定 read-face、静态唯一性测试为源码子串计数（有行为用例 + AST 复核补偿）。
- **limitation 保留**：**L-R11-a**（`relation='added'` 缺行不可检测 / plan receipt 未实现）、**L-R11-b**（写面/章级面仍 pending-only）、**L-R11-c**（无专用诊断码）、**L-R11-d**（不自动修复损坏行）、**L-R11-e**（legacy 用真实 v7→v8）。**未声称**「C-17 §3.3 完全实现 / L-R11 全部关闭」——`added` 子集与写面/章级面仍未覆盖。
- **Resource Manifest**：仓内 0 删除/0 移动/0 归档；工作区 `L-R11\review`/`lead-gates` 备份保留（无独有数据）。
- **指针清理**：Lead 更新 STATUS/PLAN/TASK_LEDGER；释放 `FEA-11-SCAN-RH-1`（proposed → ready）。
- **push**：随本轮 Lead 统一 push（PRE/POST hash、AHEAD 记录见 `doc/handoffs/DSH-HANDOFF-2026-11-06.md` §22）。
