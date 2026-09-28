---
task_id: M2-AC2
reviewer: DeepSeek Harness (non-author, static recheck)
decision: approved_with_conditions
reviewed_head: 375cf43b92d89958c721fc2273ab0905aecc297f (C1-C3 closed by owner at 8db6d150 -> tip c3ee8dbe)
round: 2 (recheck)
---

已完成只读静态复核。先声明本会话的取证限制：**pwsh 工具在 workspace 授权初始化阶段即失败**（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），两次尝试均未执行任何命令；因此 `375cf43b` 是否确为当前 HEAD、`8d72f91f..375cf43b` 的 diff 是否全部落在 Task 允许路径内，我**无法用 git 证实**（下面标为残余 not_verified，交由 Codex 集成时用 git 复核）。全部技术判定基于对 worktree 内源码/测试/证据文件的静态读取。

---

## decision: approved_with_conditions

原 P1-1 已实质闭合（AC5 现有真实语义断言），P2-1..4 判别力项均已落地，P3 大部分闭合；无 P0/P1，无产品代码改动证据。剩余为 **P2 级证据一致性 + 一处新判别力缺口**，可在集成前以低风险 amend 关闭。

---

## R-A..R-G 判定表

| 项 | 判定 | 证据（path:line） | 说明 |
|---|---|---|---|
| **R-A**（原 P1-1）AC5 RUNNING→重装配→INTERRUPTED | **verified** | `tests/m2_acceptance/test_data_integrity.py:538-566`（554 `_store.get`、556 置 `RUNNING`、557 `_store.put`、560-561 `conn.close()`+重装配、562-565 断言 `is INTERRUPTED`）；`src/infrastructure/sqlite/pipeline.py:393-431`（`put` 走 `DELETE`+`INSERT`，418 写 `status` 列、428 写 `run_json`）、`497-507`（`get` 优先 cache、回退 DB `run_json`）；`src/bootstrap/core_assembly.py:804`（装配期 `pipeline.recover_running_runs()`）；`src/application/tasks/service.py:886-901`（RUNNING→INTERRUPTED 语义）；`doc/handoffs/M2-AC2-owner-delivery.md:26`（AC5 行）、`43-46`（NOT_RUN 段） | 状态**真持久化**（非内存态）：新 store 的 cache 为空，`recover` 从 DB 读回 RUNNING 才可能改写；若 `put` 未落 status，重装配后读到的是 create_run 的 PENDING，断言会失败 → 有判别力。若实现改为 CANCELLED 也会失败。`core.conn.close()`+重装配与 M2-AC1 既有先例一致（`tests/m2_acceptance/test_acceptance_loop.py:57-60`）。Handoff AC5 行已加"（语义断言，r1 P1-1 已闭合）"，NOT_RUN 段已同步收敛。 |
| **R-B**（原 P2-1）AC1 mtime_ns + hashlib oracle | **verified** | `test_data_integrity.py:147`（`st_mtime_ns` 采样）、`159`（`hashlib.sha256(...).hexdigest()` 独立 oracle）、`164-167`（size+mtime_ns 断言，失败消息明确） | 已不再用 `sha256_bytes`。附 P3-4：AC5 场景 `:513` 仍用实现 helper，AC1 已独立足以锚定 oracle 正确性。 |
| **R-C**（原 P2-2）AC2 收紧 + Qt 读面 NOT_RUN | **verified** | `test_data_integrity.py:236`（`== "ok"`）、`241`（`== "invalid"`，失败消息带实际值）；`src/bootstrap/core_assembly.py:205`（`"ok" if path.is_file() else "invalid"`，与断言逐字对应）；`test:238-240` 注释说明 Qt 读面需 QImage 适配器；`Handoff:45`（NOT_RUN 明确登记）、`Handoff:27`（AC6 行引用） | 不再"假装覆盖"，Qt `ProviderInputError` 分支如实 NOT_RUN，符合 AC6"NOT_RUN 分开报告"。 |
| **R-D**（原 P2-3）restore 等值 provenance + current 指向新 revision + 去硬编码 | **verified** | `test:452-453`（`first_manual_no`/`second_manual_no` 取 save 返回值）、`463-467`（`len(revisions) == second_manual_no + 1`、`max()` 取新号）、`471-476`（`restored_from_revision_id == source_revision.region_revision_id` 等值）、`477-479`（`current_revision_id ==` 新 revision id）；`src/application/editing/service.py:566`（`restored_from_revision_id=source.region_revision_id`）、`574-577`；`src/infrastructure/sqlite/regions.py:255-262`（号由事务 `MAX+1` 分配）、`285`（current 回填）、`71-75`（`_sync_region_state` 回传指针） | 等值语义成立（不是 revision_no 比较）；current 指向新 revision 由 `commit_region_revision:285` + `_sync_region_state:74` 保证。 |
| **R-E**（原 P2-4）cleanup 真实业务文件进 inventory | **verified** | `test:398-406`（`business = _managed_file(core, page)` 真文件 + `CleanupTarget(relative_path=business_rel)`）、`419-424`（`removed == 1`、`skipped >= 1`、`not stale.exists()`、`business.is_file()`）；`src/application/maintenance/cleanup.py:41`（`CACHE_SAFE_PREFIXES=("cache/",)`）、`127-131`（非 cache 前缀直接 skipped，**不交给 remover**）；`src/infrastructure/filesystem/managed_storage.py:147-180`（`remove_managed` 对业务路径**不会**拒绝，只做 containment/reparse） | 断言组合有判别力：若 cleanup 误把业务路径当可清（或 remover 误删），`business.is_file()`/`skipped` 会失败。**注意**：`skipped>=1` 本身证明的是策略层拒绝，remover 的拒绝分支从未被业务路径触达（见 P3-5）。 |
| **R-F**（原 P3-1/P3-2）证据 EXIT/head + docstring 如实 | **partially_verified** | 满足面：`verification/M2-AC2/verification-results.md:3`（head）、`:28/:33/:36`（三处 EXIT）；docstring `test:1-19` 点名 `assemble_core_services`，`:72-95` 如实说明适配器注入与 `_PassthroughImageDecoder` 缺陷（缺陷经源码核对真实：`src/bootstrap/core_service.py:54` 传 `format=`，`application/importing/images/ports.py:12-17` 只有 `width/height/mime_type`）。不足面：见 P2-2/P2-3。 | `:7` 声明 `pytest ... -q`，但 `:15-25` 是 `-v` 的逐条 `PASSED [ n%]` 格式（对照 `:31` 真 `-q` 的点行）→ 命令与"原始输出"不自洽；`Handoff:31-32` 残留 `10 passed / 14 passed`。 |
| **R-G**（原 P3-3/P3-4）revision 硬编码清除 + PermissionError 措辞 | **partially_verified** | 措辞已修正：`Handoff:37`（"service 层在调用 entities 前已拦截并返回 LOCK_CHANGED，生产路径不会看到该异常"）经源码核对基本成立——`src/infrastructure/providers/step_writes.py:158-165`（`LockBlocked`）、`src/application/editing/service.py:491-496`（`GuardStatus.LOCK_CHANGED`）；`step_writes.py:118-122` 印证 OCR 链只查 `region_locked`（Handoff:37 的双层锁语义与源码一致）。残留：`test:499` `set_revision_pinned(region.region_id, 1, True)` **仍是字面 1**（restore 场景已去硬编码，AC5 场景未）。 | 该处语义稳定（`create_region` 必然产生 v1）且 `:502` 复读实际 `revision_no`，故不阻断，列 P3-2。 |

---

## 新问题分级

**P0：none**

**P1：none**

**P2-1（判别力，新发现）** — `test:343` `assert all(value == "skip_lock" for value in decisions.values())` 与 `test:533-535` `assert all(u.decision.value == "skip_lock" for u in planned.tasks[0].units)`：对**空 units/空 decisions 恒真**。若 planner 回归为"不产生任何 unit"，AC4/AC5 会假 PASS（这是原 P2 判别力同类缺口，返修未覆盖）。建议前置 `assert decisions` / `assert planned.tasks[0].units`。

**P2-2（证据自洽性）** — `verification-results.md:7` 记 `-q` 却在 `:15-25` 给出 `-v` 格式输出（对照 `:31` 真 `-q` 点行），二者不可能来自同一命令；`:35` cmd3 用占位符 `$(delivery head)` 而非实际 hash，无法审计被检区间；`:3` 的 delivery head=8d72f91f 与本会话 tip 375cf43b 不一致且无"workspace tip / amend commit"说明。

**P2-3（文档同步）** — `Handoff:14`（"10 场景"）、`:31-32`（"10 passed / 14 passed"）为返修前残留，与同文件 `:27`（11/15）及证据文件（11/15）矛盾；`doc/tasks/M2-AC2.md:17` `delivery_head` 仍为 `a3e3fb22`（初始交付），Handoff/证据均为 `8d72f91f`。

**P3-1** 死 import：`test:44 RegionRevision`、`:45 ManagedFileStorage`、`:47 SqliteRegionRepository` 全文未使用（若仓库 lint gate 含 F401 会失败）。

**P3-2** `test:499` 硬编码 revision `1`（见 R-G）。

**P3-3** `test:553` 函数内局部 `from domain.tasks.models import PipelineRunStatus`，而顶部 `:39` 已从同模块导入——风格不一致。

**P3-4** `test:513` AC5 仍用实现 helper `sha256_bytes` 作 hash 断言（AC1 已独立；该行前后已有源字节直比，风险低）。

**P3-5** `test:400` `page.managed_original_ref.replace(chr(92), "/")`：`managed_original_ref` 由 `ManagedFileStorage.new_revision_relative_path:92` 以 `"/"` 生成，永不含反斜杠，replace 冗余（`cleanup.py:235` 内部也会归一化）；`chr(92)` 写法隐晦。同理 `skipped>=1` 只覆盖策略层，remover 的业务路径拒绝未被触达。

**P3-6** 私有 API 依赖：`pipeline._store` **有既有先例**（`tests/pipeline/test_regionless_rebinding.py:688`），且 `get/put` 是 `PipelineStore` 协议方法（`infrastructure/sqlite/pipeline.py:393/497`），一致；但 `core.editing._repo`（`test:282` 等 15 处）**无既有先例**，且 `RegionEditingService` 无公开 revision 读接口——建议加注释或后续补只读查询面。

**P3-7** `test:147/165` 的 mtime 断言在 Windows/NTFS 上**稳定**（写后仅读，无重写；tmp_path 为本地盘），无 flakiness；但其判别力有限——`ImportSource` 只吃 `filename+data_provider`，源路径并非导入输入，该断言主要防"测试自重写源文件"；`:163` 的目录清单断言补强了这一点。另 `test:561` 新建 `core2` 未 `close()`（仅可能触发 tmp 清理告警）。

**P3-8** `Handoff:46` 的"r1 各项均已闭合"清单漏列 P2-2（已在 45 行 NOT_RUN 说明）与 P3-5。

---

## 是否达到可集成标准

**达到（approved_with_conditions）。** 静态判定层面：AC1–AC5 的语义承诺均在生产装配 + 真实 SQLite/文件系统上被真实断言覆盖，原 P1-1 与 P2-1..4 已闭合，无产品代码改动、无范围越界**证据**，测试数字与其内容不矛盾，可交 Codex 集成复跑。

但请按以下条件处理（均低风险，不需触碰产品代码）：

- **C1（对应 P2-2）集成前 amend** `verification/M2-AC2/verification-results.md`：cmd1 命令与实际使用一致（`-v`）；cmd3 写真实 head hash；补一行"delivery head=8d72f91f（代码返修）/ workspace tip=375cf43b（证据+handoff amend）"。
- **C2（对应 P2-3）集成前 amend**：Handoff `:14/:31/:32` 改为 11 场景 / 11 passed / 15 passed；`doc/tasks/M2-AC2.md:17` `delivery_head` 同步到最终 tip。
- **C3（对应 P2-1）集成前补断言**：`test:343` 与 `test:533` 前加 `assert decisions` / `assert planned.tasks[0].units`，然后按 Owner 口径复跑 `pytest tests/m2_acceptance`（预期 11/15 passed EXIT 0）并更新证据文件。
- **C4（P3-1..P3-6）登记为后续清洁项**，不阻断集成。

残余 **not_verified（须由 Codex 集成时用 git 关闭）**：① `375cf43b` 是否为当前 HEAD；② `8d72f91f..375cf43b` 的变更文件是否全部落在 Task 允许路径（`tests/m2_acceptance/test_data_integrity.py`、`doc/tasks/M2-AC2.md`、`verification/M2-AC2/**`、`doc/handoffs/M2-AC2-*.md`）；③ pytest 11/15 passed 与 `git diff --check` EXIT 0 的**实跑复现**（本会话未执行命令）。

**建议下一步**：由 Integrator=Codex 在新会话中先关闭 C1–C3（可并为一个 amend），再执行集成验证（复跑两条 pytest + `git diff --check 61f9db9b..<delivery-head>` + 范围核对），通过后置 M2-AC2 为 `done`。可直接转发指令：

> 你是 Codex（Integrator，非本 Task 作者）。目标 worktree：`G:/CODEX/New Manga.worktrees/M2-AC2-zcode`，Task `doc/tasks/M2-AC2.md`，Owner 交付 tip `375cf43b`（代码返修 commit `8d72f91f`）。DSH 非作者 Review 结论为 `approved_with_conditions`。请：① 关闭 Review 条件 C1–C3（修正 `verification/M2-AC2/verification-results.md` 的 cmd1 命令与实际输出格式/补齐 cmd3 真实 hash 与 tip 说明；Handoff 场景数与 passed 数改为 11/15；`doc/tasks/M2-AC2.md` 的 `delivery_head` 同步最终 tip；为 `tests/m2_acceptance/test_data_integrity.py` 的 page-lock/AC5 `all(...)` 断言补非空前置断言）；② 复跑 `pytest tests/m2_acceptance/test_data_integrity.py -v`、`pytest tests/m2_acceptance -q`、`git diff --check 61f9db9b..<delivery-head>` 并记录每条 EXIT；③ 用 git 核对 diff 范围仅含允许路径、Owner≠Integrator 保持；④ 给出集成结论与是否置 `done`。
