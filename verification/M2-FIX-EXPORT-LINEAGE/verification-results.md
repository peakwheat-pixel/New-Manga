# M2-FIX-EXPORT-LINEAGE Verification Results（Owner 交付证据）

- Owner：ZCode（子 agent 代行，用户授权 2026-09-28）
- base：`8b0d9040`；release commit：`aa1e0c7c`；branch：`agent/zcode/M2-FIX-EXPORT-LINEAGE`
- worktree：`G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode`
- 解释器：`"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"`（路径含空格，r2 起日志头部以引号包裹；版本 = Python 3.12.3 + pytest 9.1.1，以 pytest 自带头行为准——r1 期 5 个旧日志头部的 `python:` 行是路径未加引号的取版本命令失败记录（DSH r1 P3-2），原样保留未改，非版本串）
- 证据纪律：所有命令日志带 shell/解释器/固定 HEAD/ISO 时间戳，尾部 EXIT；raw 日志见 [raw/](raw/)；时间口径（DSH r1 P3-3，以 `git log --format=%cI` 为准）：release `aa1e0c7c`=2026-09-29T01:07:24+08:00、claim `4e76b2fa`=01:12:09+08:00、交付（pre-clean）`0ec1f052`=01:18:42+08:00、r1 回填 tip `b0ef7f76`=01:22:18+08:00；证据 ISO（UTC）=2026-09-28T17:12:41Z–17:2x Z ≙ +08 01:12–01:2x，**释放（01:07:24+08）先于实施（red 01:12:41+08）**，时间序成立；`release-8b0d9040.md`/`doc/STATUS.md` 所记「02:1x」为近似偏晚记载，以本节 %cI 口径为准（旧文件不改）
- 日期：2026-09-29 Asia/Shanghai（r2 返修同日凌晨完成）

## 1. Commit ledger（claim → 实现+证据 → 回填；r2 重建后实际 hash，见 §9 amend 轨迹）

| # | commit | 内容 |
|---|---|---|
| 1 | `4e76b2fa` | claim（Task frontmatter owner/dispatch_state RELEASED→CLAIMED） |
| 2 | `297c9655`（= delivery_head；`0ec1f052` 的 r2 amend：whitespace-only 清理 + C4/C5，前身链见 §9） | 实现（`service.py`）+ 测试（xfail 移除/legacy 场景/C5 persisted missing 断言）+ raw 红绿日志（清理后）+ 本验证文档 + Handoff |
| 3 | 回填 commit（本文件随交付 tip 运行的复跑/自检日志经一次 amend 并入其中，run-at hash 见 [raw/final-tip-rerun-r2.log](raw/final-tip-rerun-r2.log) 头部；Task frontmatter `delivery_head` 指向 #2） | Task 回填 AC 判定、status: in_review、DELIVERED_FOR_REVIEW + C1b/C1c/C3 证据日志 |

r1 期 ledger（历史，全部可由 reflog 复核，见 §9）：claim `4e76b2fa` → 交付 `0ec1f052` → 回填 `cba8db48` --amend→ `e05696fd` --amend→ `b0ef7f76`。

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
| AC5 证据纪律 | **PASS（r2 达成冻结判据）** | 日志带头（shell/python/HEAD/ISO）尾 EXIT——r1 期 5 个旧日志的 `python:` 头行为取版本命令失败记录（路径未加引号），版本以 pytest 头行为准，r2 起新日志头部已修正（DSH r1 P3-2）；P3-7 评估见 §7；**整树 `git diff --check 8b0d9040..<delivery_head>` = EXIT 0**（`297c9655` 上复核；6 处 raw 日志行尾空白已按 DSH §D whitespace-only 清理，`--ignore-all-space` 空 diff 证明见 [raw/diff-check-evidence.log](raw/diff-check-evidence.log) 与 §9）；范围自检 raw 证据 [raw/scope-self-check.log](raw/scope-self-check.log)；交付 tip 绑定复跑 [raw/final-tip-rerun-r2.log](raw/final-tip-rerun-r2.log)；`schema.py` 0 命中 |

## 5. 回归日志

- **r2 交付 tip 绑定复跑（权威）**：[raw/final-tip-rerun-r2.log](raw/final-tip-rerun-r2.log)——`tests/m2_acceptance -q` = **34 passed, 1 xfailed** EXIT=0；`tests/core -q` = **76 passed** EXIT=0；`tests/m2_acceptance -q --runxfail` = **1 failed（恰 F-2 场景 `test_ac4_books_without_pages_are_not_presented_as_zero`）+ 34 passed** EXIT=1（证明套件内恰一处已知 xfail、无 XPASS 掩盖、无第二处隐藏 xfail）。日志头记录执行时刻 HEAD（run-at）与本文件并入方式（amend）。
- r1 期权威 rerun（历史保留）：[raw/regression-final-rerun.log](raw/regression-final-rerun.log) — `tests/m2_acceptance -q`：**34 passed, 1 xfailed**，EXIT1=0；`tests/core -q`：**76 passed**，EXIT2=0（运行于 claim+unstaged 修复态，HEAD=`4e76b2fa`）。
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

- 交付区间改动路径（claim+交付 commit，`git diff --name-status 8b0d9040..<delivery-head>`）：**raw 证据落盘见 [raw/scope-self-check.log](raw/scope-self-check.log)（r2 补，DSH r1 P2-1）**，本节为其判读：
  - `src/application/export/service.py`（允许）
  - `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（显式授权：F-1 xfail 移除 + docstring 同步 + legacy 场景 + C5 persisted missing 断言；其余场景断言零改动）
  - `verification/M2-FIX-EXPORT-LINEAGE/**`、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md`（允许）
  - `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`、`doc/STATUS.md`（claim/回填/release，允许；STATUS.md 改动属 release commit `aa1e0c7c`，非本 Owner 区间）
- `git diff --check 8b0d9040..<delivery_head>` 整树 **EXIT=0**（r2 起；r1 期曾 EXIT=2，已按 DSH §D whitespace-only 清理收口，轨迹与证明见 §9 与 [raw/diff-check-evidence.log](raw/diff-check-evidence.log)）。
- `src/infrastructure/sqlite/schema.py`：0 命中；`src/infrastructure/sqlite/reading_export.py`：0 改动（整体存取探查结论）；计数命令输出见 [raw/scope-self-check.log](raw/scope-self-check.log)。
- 未 git push；未删分支；未动 worktree 外文件。

## 9. amend 轨迹与 hash 来历（DSH r1 P1-1/P1-2，指令所指 §8 登记位——§8 已被范围自检占用，故以 §9 落实）

### 9.1 r1 期回填 commit 的两次 amend（`e05696fd`/`cba8db48` 来历，reflog 核实）

`git reflog show --date=iso HEAD`（2026-09-29 +08）逐条：

| reflog 项 | hash | 动作 | 内容 |
|---|---|---|---|
| 01:19:33 | `cba8db48` | commit | 第一次回填：Task AC 判定 + status in_review + DELIVERED_FOR_REVIEW + delivery_head=`0ec1f052` |
| 01:21:40 | `e05696fd` | commit (amend) | 第 1 次 amend：补 diff-check 披露（`raw/diff-check-evidence.log` 初版 + AC5/§8/Handoff 三处措辞） |
| 01:22:18 | `b0ef7f76` | commit (amend) | 第 2 次 amend：补交付 tip 终验 `raw/final-tip-rerun.log`（其头部 HEAD=`e05696fd` = run-at 时刻，amend 并入后 tip 变更——此即 r1 被指出的「日志 HEAD ≠ 声明 tip」来源） |

`git cat-file -t e05696fd` / `git cat-file -t cba8db48` 均 = `commit`（对象仍可达，为 `b0ef7f76` 的 amend 前身，非推送、非删除、无数据丢失）。r1 期文档未披露该轨迹，属 P1-1 缺陷，本节补登。

### 9.2 r2 whitespace-only 清理 amend（DSH §D 裁决执行）

- pre-clean delivery tip：`0ec1f052ff4a3b3875d9e242deb9fb3cb381fa5a`（r1 声明的 delivery_head）
- cleaned delivery tip：`297c96557f1aa0ac41bc19fdf38c90a06badbea1`（`0ec1f052` 的 amend 重建；**Task frontmatter `delivery_head` 已同步更新为此值**）
- 清理内容（仅行尾空白，traceback 文案逐字保留，行数不变 71/155）：`raw/red-pre-fix-test_ac2_history.log` 46/56/59 行、`raw/regression-final.log` 35/54/69 行
- 等价性证明：`git diff --ignore-all-space 0ec1f052..297c9655 -- verification/M2-FIX-EXPORT-LINEAGE/raw/` = **空输出 EXIT=0**；`git diff --check 8b0d9040..297c9655` = **空输出 EXIT=0**（冻结 AC5 判据在整树达成）；amend 全部差异 = 2 日志 whitespace + C4 文档 4 行 + C5 断言 5 行，`src/` 零差异。完整登记：[raw/diff-check-evidence.log](raw/diff-check-evidence.log)（r2 手写重写版，不再粘贴带空白原样输出）
- 重建方式：`git reset 4e76b2fa`（mixed，工作区保留）→ 交付文件集重建 commit `297c9655`（amend 语义，message 注明 r2 amend 与清理行号）→ 回填层重建。旧日志保留运行时刻 HEAD 原样（red/green/regression-final/regression-final-rerun 头部 `git HEAD: 4e76b2fa…` 系 claim+unstaged 态执行，final-tip-rerun 头部 `e05696fd` 系 run-at 时刻），r2 起交付 tip 绑定以 [raw/final-tip-rerun-r2.log](raw/final-tip-rerun-r2.log) 为准。
- r2 回填 commit 的 amend 链（reflog 逐条，全部为并入证据日志/whitespace 清理，测试与产品代码零改动）：`db975e7a`（回填首建：Task + C1b/C2/C4/C6 文档 + 重写版 diff-check-evidence.log + 旧 final-tip-rerun.log）→ `f412cd47`（amend：并入 r2 复跑 `final-tip-rerun-r2.log` 与范围自检 `scope-self-check.log`，两者均 run-at `db975e7a`）→ `46a444c8` 及最终收口 tip（amend：`final-tip-rerun-r2.log` 91/96 行——`--runxfail` traceback 内 pytest 空源码行缩进——按同一 §D 授权行尾空白清理，行数 118 不变；登记见 diff-check-evidence.log Postscript）。每次 amend 后整树 `git diff --check 8b0d9040..<tip>` 均复核 = 空 EXIT=0。

### 9.3 时间口径核定（DSH r1 P3-3，`git log --format=%cI`）

| commit | %cI |
|---|---|
| release `aa1e0c7c` | 2026-09-29T01:07:24+08:00 |
| claim `4e76b2fa` | 2026-09-29T01:12:09+08:00 |
| 交付（pre-clean）`0ec1f052` | 2026-09-29T01:18:42+08:00 |
| r1 回填 tip `b0ef7f76` | 2026-09-29T01:22:18+08:00 |

证据日志 ISO（UTC）：red `17:12:41Z`、green `17:13:18Z`、regression `17:14:47Z`、rerun `17:15:41Z`（≙ +08 01:12:41–01:15:41）。**时间序成立：release（01:07:24+08）先于 claim（01:12:09）先于 red（01:12:41）**；`release-8b0d9040.md` 与 `doc/STATUS.md` 所记「02:1x」为近似偏晚记载（本 Task 范围内不改这两个文件，以本节口径为准）。
