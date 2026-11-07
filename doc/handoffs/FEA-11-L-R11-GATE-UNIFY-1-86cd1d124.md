---
task_id: FEA-11-L-R11-GATE-UNIFY-1
author: l-r11-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 2175238ab
start_head: 28a2826af
delivery_head: 86cd1d124
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-R11-GATE-UNIFY-1（L-R11 publication gate 统一：Core 单谓词）

- Task：`doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md`（`status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-08（Asia/Shanghai）
- 权限依据：卡面 `status: ready`（Owner=`l-r11-impl`）+ 权威 scope review
  `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（recommended；方案 C 单谓词 + 全链）+ C-16 v1.7 §2.4
  （PREREQ `2175238ab`，1/18 pin）+ C-17 §3.3（`:171-173`，零字节）
- 交付基线：卡 `base_commit=2175238ab`；**实现起点实测 `28a2826af`**（派发说明写 `8584f412f`；本会话开始时
  HEAD 已是 Lead 的 `28a2826af`）；实现/测试提交落在 Lead 并发 docs 提交 `2e4d6128e` 之上
- **delivery_head = `86cd1d124`**：实现 `1c1c9ca2f` + 测试 `86cd1d124`；随后同批 docs/evidence 提交
  （EV / `RESOURCE-MANIFEST.json` / 本 Handoff / 卡面交付记录）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / pytest 9.1.1；未建 worktree；未 push；零新依赖、零 schema/
  迁移、零 wire/命令/能力/错误码/`PROTOCOL_MINOR`、零 App/Host 改动、零契约字节改动

## 1. 交付结果（AC-1…AC-6 全 MET；卡面已 `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-1 单谓词唯一** | MET | `source_sync.py` 唯一判定 `_publication_gate_verdict` + 唯一公开入口 `SourceSyncStore.publication_gate_of_page` + 唯一链 walk `_binding_chain_ids`；`core_assembly.read_gate` 与 `core_service._assert_source_sync_gate` 均委托；`AuthorizeSourceReadForRun` 仍经 `catalog.source_gate_reader` 消费同一谓词；`read_gate` docstring「无行即 open」已删。静态用例 + 判别性 M4 |
| **AC-2 legacy 零回归** | MET | **真实 `MigrationRunner(conn, MIGRATIONS[:7])` 造 v7 → 升级 v8 → 真实 `assemble_core_services`**：`previous NULL 无行` 与 `previous 非空但全链无 publication` 两种 legacy 形态均 `open`；resolve 返回 v2 key、provider 读真实 zip 成员、target/commit guard/Authorize 正常。判别性 M1 |
| **AC-3 L-R11 一跳 fail-closed** | MET | B1(publication open)+B2(healthy 无行 previous=B1)：谓词 `corrupt_chain` → `read_gate="unavailable"`；`create_run`/commit guard `TARGET_NOT_FOUND`；provider `INVALID_INPUT` 且 `prepare_referenced_rendition`/`read_entry_bytes` **0 次**（真实 grant 已绑定）；resolve/reader `SOURCE_ACCESS_DENIED`；Authorize typed 拒绝 + 零映射 + 零业务写。判别性 M2 |
| **AC-4 全链检测（两跳）** | MET | B1(publication)+B2(无行)+B3(无行 current)：各面与一跳完全一致拒绝。判别性 M3（改回一跳 → 两跳 RED、一跳 PASS） |
| **AC-5 零漂移** | MET | pins **18/18**（C16 v1.7 `67286eeca8cb…`、C17 `aefa0fa5b17e…`）；`src/**` diff 仅 3 个 allowed 文件；`doc/plan`+`doc/contracts`+`schema.py`+`apps/**` 零 diff（0 字节）；无新码/命令/能力/`PROTOCOL_MINOR`/依赖 |
| **AC-6 门禁/证据/不夸大** | MET | 定向 78、`tests/fea11` 212（before 206）、全量 3369/10（before 3363/10）、pins 18/18、check×2 PASS、API EXIT 0、scope 通过、判别性 4/4；EV/Handoff/Manifest 完整；卡面登记 L-R11-a…e；未写「C-17 §3.3 完全实现 / L-R11 全部关闭」 |

## 2. 验证证据（实跑；`delivery_head=86cd1d124`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向 pytest | `pytest tests/fea11/test_source_gate_unify.py tests/fea11/test_source_rendition_gates.py tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_run_grant.py tests/fea11/test_source_resolve.py -q` | **78 passed**（既有 72 + 新增 6） | `verification/FEA-11-L-R11-GATE-UNIFY-1/logs/pytest/targeted-gate-files.log` |
| `tests/fea11` 全量 | `pytest tests/fea11 -q` | **212 passed**（**before 206 → after 212**） | `logs/pytest/tests-fea11-full.log` |
| 全量 Python | `pytest tests -q -p no:warnings --tb=no` | **3369 passed / 10 skipped**（**before 3363/10 → after 3369/10**，不降；skip 不变） | `logs/pytest/full-pytest.log` |
| pins | `verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** | `logs/governance/pins.log` |
| check（默认 / `-TaskPath`） | `check.ps1` | **PASS (3 warnings) ×2** | `logs/governance/check.log`、`check-taskpath.log` |
| API inventory | `python tools/generate_api_inventory.py --check` | **EXIT 0** | `logs/governance/api-inventory.log` |
| scope | `git diff HEAD~2 --name-only` / 零漂移 diff | 仅 3 个 `src/**` allowed 文件；契约/schema/apps **0 字节** | `logs/scope/**` |
| 判别性 | `python G:/CODEX/New Manga.workspace/FEA-11-L-R11-GATE-UNIFY-1/mutate.py` | **4/4 RED_AS_EXPECTED + 复原 sha256 2/2 MATCH + 复绿 6 passed** | `logs/discriminative/**` |
| 构建 / 全量 .NET / 真实 IPC | — | **N/A**（纯 Python Core + tests；零 App/Host/wire 改动） | — |

- **before / after**：损坏形态（一跳/两跳）在修复前 `read_gate="open"`、Run 目标/commit guard/provider/
  `AuthorizeSourceReadForRun` 全部放行（read_gate 侧）；修复后这些面全部按既有 family 拒绝，resolve 面由
  「一跳启发式」变为同一谓词（两跳也拒绝）。legacy 形态 before/after 均为 `open`（零回归）。
- **全量 pytest 后**工作树无额外 tracked 变更（`verification/FEA-09` 未被触碰）。
- **并发披露**：共享 `main` 同期 Lead docs-only 提交（`698ac9524…2e4d6128e`，C-04b residual / SCAN-RH /
  STATUS/handoff）；本卡提交均显式 pathspec，`src/**` 仅 3 个 allowed 文件。

## 3. 实现要点（供 Reviewer 定点核查）

1. `source_sync.py`：
   - `_publication_gate_verdict`（唯一判定）：healthy → 行（`open`/`pending`）→ 无行则**全链 walk**（任一
     publication → `corrupt_chain`）→ 否则 `open`；无/非 healthy binding → `unavailable`。
   - `_binding_chain_ids`（唯一 walk，cycle-safe）+ `_publication_row`（唯一 publication 读）；`page_is_sync_managed`
     复用同一 walk（行为不变）。
   - `SourceSyncStore.publication_gate_of_page`：唯一公开入口。
2. `core_assembly.read_gate`：只委托 + 把 `corrupt_chain` 映射为冻结三态 `unavailable`；不再本地读 gate 行。
3. `core_service._assert_source_sync_gate`：委托同一谓词；`pending`/`corrupt_chain` 抛既有 `SOURCE_ACCESS_DENIED`
   固定文本；`unavailable` 留给 resolve 既有 binding-readiness 拒绝（同码零漂移）；删除旧一跳 `previous_binding_id`
   启发式。`_assert_source_sync_gates` 仍只循环委托。
4. `AuthorizeSourceReadForRun` 未改代码，仍经 `catalog.source_gate_reader` 消费同一 `read_gate`；损坏形态下
   `catalog.expand` 先 typed 拒绝（既有 `INVALID_REQUEST`），零映射。

## 4. 不夸大与 limitation（Review/closeout 必须保留）

- **不构成**「C-17 §3.3 已完全实现」；**不构成**「L-R11 全部关闭」。
- **L-R11-a（残余，关键）**：`relation='added'`（previous NULL）新同步 binding 缺行时链检测不可见，与 legacy
  不可区分；plan receipt 检测未实现。
- **L-R11-b**：写面 / 章级面仍 pending-only；损坏链下它们仍放行，直到逐页 resolve 拒绝。
- **L-R11-c**：损坏状态映射既有 family，无专用诊断码、无新增日志行。
- **L-R11-d**：不提供损坏 publication 行自动修复/重建。
- **L-R11-e**：legacy 证据使用真实 v7→v8 migration，非 v8 内伪造。
- 真实 IPC/gated 不适用本卡（零 wire/命令改动）。

## 5. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；**delivery_head=`86cd1d124`**（未 push、未建 worktree）。
- 复现（repo root）：见 `verification/FEA-11-L-R11-GATE-UNIFY-1/EV.md` §9。
- 接收者下一步（建议 Lead 指派**独立上下文** Review，只读 `86cd1d124`；重点）：
  ①单谓词唯一性与四处消费（含静态断言、无第二份一跳判定）；
  ②legacy 零回归（真实 v7→v8、`previous 非空但全链无 publication` 也 open）；
  ③一跳/两跳 fail-closed 各面与错误 family（Run `TARGET_NOT_FOUND`、provider `INVALID_INPUT`、resolve
  `SOURCE_ACCESS_DENIED`、Authorize typed+零映射）；
  ④判别性 4/4 与复原 sha256；
  ⑤零漂移（pins 18/18、契约/schema/apps 0 字节、无新码/wire）；
  ⑥limitation 口径与不夸大声明。
- 本 Handoff 不改卡 `status`；卡面 `delivery_head` 已回填；不自行 closeout、不 push。

## 6. 下一任务建议（由 Lead 裁决，仅供队列参考）

- 本卡 Review/集成通过前不释放依赖它的后续实现；Review 通过后由 Lead 按既有 DAG 处理
  `FEA-11-SCAN-RH-1`（已冻结 proposed）/ C-04b / UI P3 等队列。
- **Recovery point**：`G:\CODEX\New Manga` / `main` / `86cd1d124`（未创建 worktree）。

## 7. 风险与回退

- **R1 口径**：不要把「单谓词统一」读成「读面全面一致」——写面/章级面仍 pending-only（L-R11-b），
  `added` 缺行仍不可检测（L-R11-a）。
- **R2 行为变化面**：仅「损坏形态」被收紧（正常 legacy / import / sync 库零变化）；损坏库中 Run 目标/provider/
  commit guard/Authorize 由放行变拒绝，属 C-17 §3.3 要求的 fail-closed。
- **R3 并发共享工作树**：证据按 `delivery_head` 归因；Lead 集成若 HEAD 前进，需按其 head 重跑门禁。
- **回退**：`git revert 86cd1d124 1c1c9ca2f`（测试 + 实现两个提交）；无 schema/数据迁移、无写行为变化，回退无
  数据风险。
