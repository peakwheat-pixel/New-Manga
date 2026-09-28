# M2-FIX-EXPORT-LINEAGE Verification Results（Owner 交付证据）

- Owner：ZCode（子 agent 代行，用户授权 2026-09-28）
- base：`8b0d9040`；release commit：`aa1e0c7c`；branch：`agent/zcode/M2-FIX-EXPORT-LINEAGE`
- worktree：`G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode`
- 解释器：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.x，日志头有原样版本串）
- 证据纪律：所有命令日志带 shell/解释器/固定 HEAD/ISO 时间戳，尾部 EXIT；raw 日志见 [raw/](raw/)
- 日期：2026-09-29 Asia/Shanghai

## 1. Commit ledger（claim → 实现+证据 → 回填）

| # | commit | 内容 |
|---|---|---|
| 1 | `4e76b2fa` | claim（Task frontmatter owner/dispatch_state RELEASED→CLAIMED） |
| 2 | （本交付 commit，hash 见交付后 frontmatter delivery_head） | 实现（`service.py`）+ 测试（xfail 移除/legacy 场景）+ raw 红绿日志 + 本验证文档 + Handoff |
| 3 | （回填 commit） | Task 回填 AC 判定、status: in_review、DELIVERED_FOR_REVIEW，注 tip hash |

## 2. 先红证据（AC2 前置：修复前证红留痕）

- 操作顺序：claim 后**临时移除** `test_ac2_history_records_which_stale_pages_were_included` 的 `@pytest.mark.xfail(strict=True)` 标记（工作区未提交，src/ 零改动）→ 跑单场景 → **真红** → 修复 `service.py` → 同场景转绿 → 标记保持正式移除。
- 红点 = 原 `:584` 断言（临时移除 12 行装饰器后日志显示 `:572`，同一断言）：
  `AssertionError: the persisted export record must carry the included stale page ids`（`set() == {stale_page_id}` 失败——持久 scope 中无 `included_stale_page_ids`）。
- 日志：[raw/red-pre-fix-test_ac2_history.log](raw/red-pre-fix-test_ac2_history.log)，尾部 `EXIT=1`。
- 修复后同场景转绿：[raw/green-post-fix-pre-marker.log](raw/green-post-fix-pre-marker.log)（`1 passed`；同日志内全套临时快跑 `33 passed, 1 xfailed EXIT=0`，此时 legacy 场景尚未加入）。

## 3. 修复实现与 scope 键数据流（AC1）

方案 A（冻结）：`scope_snapshot_json` 内加键，不动 schema.py（`git diff` 范围自检 `schema.py` 0 命中）。

数据流（探查确认，`_scope_snapshot` 全仓仅 2 调用点）：

1. `export()` :218 `stale_ids, missing_ids = _stale_scope(request)`（仅 `mode=="translated"` 非空）→ :227-236 打包进 `ExportResult.included_stale_page_ids/included_missing_page_ids`（内存正确，缺陷不在内存层）。
2. COMPLETED 路径在 `result` 构造**之后**才调 `_record`（原 ：290），因此**无需提前生成再合并**：直接把 `result.included_stale_page_ids/included_missing_page_ids` 作为关键字参数传给 `_scope_snapshot`——落库值与内存 `ExportResult` 严格同源（数据源=ExportResult，指令要求）。
3. `_scope_snapshot(request, *, included_stale_page_ids=(), included_missing_page_ids=())` 序列化 5 旧键 + 2 新键（list 化）。
4. `_record` 的 `scope_snapshot_json` 为整体 JSON 字符串落库。fallback 路径（SKIPPED/CANCELLED/FAILED：`:248/:268/:280` 传 `scope=None` → `:460` `scope or _scope_snapshot(request) or "{}"`）经 `_scope_snapshot(request)` 以默认空参序列化——**两新键存在、值为空 list**（`service.py` 默认参数 `:482-483`、序列化 `:496-497`；无 `null` 落库路径）。更正（DSH r1 P2-2）：r1 前文档称 fallback「保持不变/不带新键」与代码相反——本 Task 实际改变了非 COMPLETED 行的 JSON 形状（新增 2 个空 list 键）。AC 只冻结 CONTINUE 放行（COMPLETED）非空与 ABORT 拒绝零记录不变；「未完成导出是否应持久化非空 included ids」留未来裁定（见 §6）。
5. `_parse_scope`：新键 `setdefault(key, [])`（缺省空 list）；非 list → `ExportError("corrupt export scope snapshot")`（损坏不是空，拒收）。`repeat()`（唯一调用方）不受影响。
6. `ExportRecord`：无需字段同步（scope 整体字符串，无 per-key 列）。
7. `src/infrastructure/sqlite/reading_export.py`：**零改动**——SELECT/INSERT/ON CONFLICT 与 legacy import 均把 `scope_snapshot_json` 当整体字符串透传（逐行核实 `:146-174/:206-232/:472`），新键随 JSON 内容自动通过；旧行无新键不崩。符合允许范围"如整体存取则可能零改动"。
8. ABORT 拒绝：`StaleExportError` raise 于任何 `_record` 之前，「零任何记录」语义不变（`test_ac2_stale_abort_fail_closed_zero_side_effects` 继续通过）。

## 4. AC 逐项判定

| AC | 判定 | 证据 |
|---|---|---|
| AC1 方案 A 落地 | **PASS** | §3 数据流；xfail 场景转 PASS 证明 COMPLETED+CONTINUE 持久行含 `included_stale_page_ids`（场景同时核 `result.included_stale_page_ids=={stale}` 同源）；ABORT 零记录场景不变；`_parse_scope` 缺省空 list+类型校验由 legacy 场景的 corrupt-value guard 断言；`schema.py` 0 命中 |
| AC2 xfail 移除转 PASS | **PASS** | 先红留痕（§2）→ 修复 → 转 PASS；标记正式移除；默认套件无 XPASS（strict 下若有残留会报 xpassed，实际 `34 passed, 1 xfailed`）；F-2 xfail 场景零触碰 |
| AC3 legacy 前向兼容 | **PASS** | 新场景 `test_ac2_legacy_scope_rows_without_included_keys_stay_compatible`：①手工 INSERT 修复前 13 列旧行（5 键无 included 键）→ `find_export` 读回不崩、`_parse_scope` → included 双键=空 list、旧键完好；②legacy JSON import 通道（`import_legacy_export_history`，旧行无新键）→ 导入成功、解析空集；③损坏 guard：新键为字符串（非 list）→ 类型化 `ExportError`，不静默伪造 |
| AC4 回归如实 | **PASS（数字偏差已解释）** | `tests/m2_acceptance -q` = **34 passed, 1 xfailed**（仅剩 F-2）EXIT=0；`tests/core -q` = **76 passed** EXIT=0。34 与预期 33 的差异 = 本 Task 按指令新增的 legacy 兼容场景 1 条（AC4 预期未计入新场景）：33 = 原 32 passed + F-1 转 PASS。两次回归日志均留痕（见 §5） |
| AC5 证据纪律 | **PASS（diff --check 事实精确披露）** | raw 日志带头尾；P3-7 评估见 §7；`git diff --check` 对 `src tests doc` 及「排除 raw 证据日志的全树」均 EXIT=0（raw/diff-check-evidence.log）；整树 EXIT=2 的唯一来源 = `raw/*.log` 内 pytest 原样输出的 6 行固有行尾空白（断言缩进行如 `E␣␣…`，证据本体，字节保真未改写）；`schema.py` 0 命中 |

## 5. 回归日志

- 权威 rerun：[raw/regression-final-rerun.log](raw/regression-final-rerun.log) — `tests/m2_acceptance -q`：**34 passed, 1 xfailed**，EXIT1=0；`tests/core -q`：**76 passed**，EXIT2=0。
- 首跑 [raw/regression-final.log](raw/regression-final.log) `1 failed, 33 passed, 1 xfailed EXIT1=1` 如实保留：失败 = 新 legacy 场景首版断言 `imported==1`，但 production 装配（`core_assembly.py:850`）已对同一 conn 执行过 one-time import（文件缺失 → 写入 `missing_empty` 标记，`import_legacy_export_history` 直接返回 0）。修正 = 场景内先删除 `application_metadata` 的 `legacy_export_history_imported` 标记行再调用，复现"升级前 legacy 文件存在"状态；非产品代码问题。

## 6. 语义边界（如实披露，非缺陷）

- SKIPPED/CANCELLED/FAILED 记录的 scope（`_record` fallback 生成，`service.py:248/268/280` `scope=None` → `:460`）**携带两新键、值为空 list**（`_scope_snapshot(request)` 默认参序列化）——语义诚实（未发布任何页 = 空集合），非「无键」也非 `null`（DSH r1 P2-2 更正，r1 前表述「不带 included 键」有误）。AC1 只冻结 CONTINUE 放行（COMPLETED）非空与 ABORT 零记录；"被取消的 CONTINUE 导出是否也应持久化非空 included ids"属 accepted-but-unspecified 语义扩展，未纳入本 Task（禁止范围条款同样警示不得顺手扩语义）。
- 被拒导出（ABORT）零记录语义未动（D03 §31 澄清事项，M2-AC4 Handoff 已披露，另行裁定）。

## 7. P3-7 并发 write 风险评估（冻结裁定：只评估，不修）

静态分析（`src/infrastructure/sqlite/reading_export.py:176-240` write + `src/application/export/service.py` `_record`）：

- 形态：document-store 全量 read-modify-write。`_record` 先 `store.read()`（全表 SELECT → list），append 后 `store.write(rows)`（事务内逐行 INSERT ON CONFLICT + `DELETE FROM export_history WHERE export_id NOT IN (active_ids)` 全量替换）。
- 丢失窗口：两个 `_record` 并发交错——A read=[X]、B read=[X]、A write([X,A])、B write([X,B])：B 的 `DELETE … NOT IN` 会**物理删除 A 行**（含 COMPLETED 行），最终仅剩 B。read（无事务持有到 write）与 write 之间窗口为毫秒级，但存在。
- 触发面：同进程多线程并发导出（`ExportService` 无内部锁）；或多进程共享同一 `library.db`（WAL 写互斥不能弥补 read-modify-write 的 read 已过期）。
- 本修复的影响：**不改变该窗口**——只改 `scope_snapshot_json` 字符串内容，不新增 read/write 调用、不改时序；风险不因本修复变大或变小。
- 缓解事实（未验证，留 Review/planning 核实）：生产 sidecar 若为单线程串行命令循环，窗口不可达。
- 结论：真实、既有、非本修复引入（与 DSH r1 P3-7 定性一致）；修复（如 store 层增量 upsert 或 `_record` 级锁）另立候选。

## 8. 范围自检

- 交付区间改动路径（claim+交付 commit，`git diff --name-status 8b0d9040..<delivery-head>`）：
  - `src/application/export/service.py`（允许）
  - `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（显式授权：F-1 xfail 移除 + docstring 同步 + legacy 场景；其余场景断言零改动）
  - `verification/M2-FIX-EXPORT-LINEAGE/**`、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md`（允许）
  - `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（claim/回填，允许）
- `git diff --check 8b0d9040..HEAD`（整树）EXIT=2——**唯一来源** = `raw/red-pre-fix-test_ac2_history.log`（3 行）与 `raw/regression-final.log`（3 行）内 pytest 原样输出的固有行尾空白（断言缩进行）。这些行是红证/回归证据本体，**字节保真保留、不做 whitespace 改写**；等效纪律证明：`git diff --check -- src tests doc` EXIT=0、`git diff --check -- . ':(exclude)verification/M2-FIX-EXPORT-LINEAGE/raw/*'` EXIT=0，完整命令与两种口径输出见 [raw/diff-check-evidence.log](raw/diff-check-evidence.log)。裁决权交 Review/Integrator：若裁定必须整树 EXIT=0，唯一手段是改写 raw 证据字节，需明确授权。
- `src/infrastructure/sqlite/schema.py`：0 命中；`src/infrastructure/sqlite/reading_export.py`：0 改动（整体存取探查结论）。
- 未 git push；未删分支；未动 worktree 外文件。
