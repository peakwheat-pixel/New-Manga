---
task_id: M2-FIX-EXPORT-LINEAGE
author: ZCode（子 agent 代行，用户授权 2026-09-28）
recipient: DeepSeek Harness（非作者 Review r1）→ Codex（Integrator）
base_commit: 8b0d9040
delivery_head: 297c96557f1aa0ac41bc19fdf38c90a06badbea1（r2 amend 自 0ec1f052，见 verification-results.md §9）
status: DELIVERED_FOR_REVIEW
---

# Handoff：M2-FIX-EXPORT-LINEAGE（Export history 持久层 included_stale/missing page ids，F-1 修复，方案 A）

## 交付结果

按冻结方案 A 完成：`export history` COMPLETED 记录的 `scope_snapshot_json` 携带 `included_stale_page_ids`/`included_missing_page_ids` 两键（CONTINUE 放行时非空，数据源=`ExportResult` 同源字段）；`_parse_scope` 对旧行缺省空 list、对新键类型校验（非 list → 类型化 `ExportError`）。`schema.py` 零触碰、`reading_export.py` 零改动（scope 整体字符串存取，逐行核实）、`ExportRecord` 无需字段。F-1 xfail 场景先红（临时移除标记证红，红点=原 `:584` 持久断言）后转 PASS；新增 legacy 前向兼容场景（SQLite 旧行 / legacy JSON import / 损坏值拒收三通道）。

变更路径（全部在允许范围）：
- `src/application/export/service.py`（`_scope_snapshot` 签名加 2 个 keyword-only 参数并序列化新键；`export()` COMPLETED 路径传 `result.included_*`；`_parse_scope` 缺省+类型校验）
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（F-1 xfail 标记移除、docstring 同步、新增 `test_ac2_legacy_scope_rows_without_included_keys_stay_compatible`；其余场景断言零改动、F-2 xfail 零触碰）
- `verification/M2-FIX-EXPORT-LINEAGE/**`、本 Handoff、Task 回填

Commit ledger（r2 重建后，amend 轨迹与 `e05696fd`/`cba8db48` 来历见 verification-results.md §9）：claim `4e76b2fa` → 交付 `297c9655`（r2 amend 自 `0ec1f052`：whitespace-only 清理 + C4/C5）→ Task 回填（delivery_head=`297c9655`，r2 复跑/自检日志经一次 amend 并入，run-at hash 见 raw/final-tip-rerun-r2.log 头部）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 先红（AC2 前置） | 临时移除 xfail 标记 → `$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py::test_ac2_history_records_which_stale_pages_were_included -v` | py3.12 task-env，HEAD=`4e76b2fa`（src 零改动） | **FAIL（预期红）**：原 `:584` 断言 `persisted_stale=={stale_page_id}` 失败，EXIT=1 | verification/M2-FIX-EXPORT-LINEAGE/raw/red-pre-fix-test_ac2_history.log |
| 修复后同场景 | 同上命令重跑 | 修复后工作区 | PASS（`1 passed`） | raw/green-post-fix-pre-marker.log |
| AC1/AC2/AC3 全套 | `$py -m pytest tests/m2_acceptance -q` | 交付 tip | **34 passed, 1 xfailed**（仅剩 F-2）EXIT=0 | raw/regression-final-rerun.log |
| AC4 既有面回归 | `$py -m pytest tests/core -q` | 交付 tip | **76 passed** EXIT=0 | raw/regression-final-rerun.log |
| 首跑留痕 | 同全套（新场景首版触发 one-time import 标记问题） | 同上 | 1 failed（测试自身修正，非产品缺陷；详见 verification-results §5） | raw/regression-final.log |
| AC5 范围/纪律 | `git diff --check 8b0d9040..<delivery_head>` 整树；`git diff --name-status`；`schema.py`/`reading_export.py` 计数 | 交付 tip `297c9655` | **整树 EXIT=0**（r2 whitespace-only 清理后达成，等价性证明 `--ignore-all-space` 空 diff）；范围自检 raw 证据落盘；schema.py 0 命中 | raw/diff-check-evidence.log、raw/scope-self-check.log |
| r2 交付 tip 绑定复跑 | `$py -m pytest tests/m2_acceptance -q`；`$py -m pytest tests/core -q`；`$py -m pytest tests/m2_acceptance -q --runxfail` | 交付 tip（run-at hash 见日志头） | **34 passed, 1 xfailed EXIT=0；76 passed EXIT=0；--runxfail 恰 1 failed（F-2）+34 passed EXIT=1** | raw/final-tip-rerun-r2.log |

34 vs AC4 预期 33 的偏差：+1 = 本 Task 按指令新增的 legacy 兼容场景（AC4 预期未计入新场景）；33 = 原 32 passed + F-1 转 PASS。如实登记于 verification-results.md §4。

## 接收方式

- branch=`agent/zcode/M2-FIX-EXPORT-LINEAGE`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode`；base=`8b0d9040`。
- 复现命令：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/m2_acceptance -q`（预期 34 passed, 1 xfailed）与 `... -m pytest tests/core -q`（预期 76 passed）。
- Review 重点建议：`_record` fallback 路径（SKIPPED/CANCELLED/FAILED）不带 included 键的语义边界（verification-results §6）、P3-7 并发评估结论（§7）是否接受为充分留痕。

## 下一任务建议（必填）

- Task ID / 标题：M2-FIX-EXPORT-LINEAGE 的非作者 Review（DSH r1）→ Codex 集成收口
- 推荐 Agent / Reviewer：DeepSeek Harness（Review）→ Codex（Integrator，另一子 agent，保持 Owner≠Integrator）
- 推荐原因与前置依赖：Task 交付完成，按协作协议进入 Review→集成；本 Task 为 Review 准备态（in_review）
- Recovery point：仓库 `G:/CODEX/New Manga`；branch/worktree 同上；固定 base=`8b0d9040`、delivery_head=Task frontmatter 所记交付 tip
- 允许修改路径：`reviews/M2-FIX-EXPORT-LINEAGE-*/**`（DSH 报告）、`doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（review/integration_merge 回填）、`verification/M2-FIX-EXPORT-LINEAGE/**`（集成记录）、`doc/STATUS.md`
- 禁止范围与新增授权条件：Review/集成不得改实现与测试语义；XPASS/回归异常按协议处理；`schema.py`/`reading_export.py` 保持零改动基线
- 交付物：DSH review 报告、集成记录、Task 终态回填
- 验证命令、环境与完成 Gate：同上两条 pytest 命令全绿 + 范围复算 + Owner≠Integrator 保持
- 可直接转发给 Agent 的指令：对交付 tip 做 M2-FIX-EXPORT-LINEAGE 非作者静态 Review（重点：方案 A 最小性、legacy 三通道断言有效性、先红真实性、P3-7 留痕充分性），产出 `reviews/M2-FIX-EXPORT-LINEAGE-<tip>-dsh-r1.md`；通过后由 Codex 集成收口。

## 风险与遗留

- P3-7 并发 write 丢失窗口（read-modify-write + `DELETE … NOT IN`）：只评估未修（冻结裁定），静态分析见 verification-results.md §7；生产单线程假设未验证。
- 未完成导出（CANCELLED/FAILED/SKIPPED）记录**携带两新键、值为空 list**（`service.py:248/268/280` `scope=None` → `:460` fallback `_scope_snapshot(request)` 默认参序列化；DSH r1 P2-2 更正——r1 前「不带 included 键」表述与代码相反）：AC 未冻结「非完成态持久化非空 included ids」的语义扩展，留未来裁定。
- per-page revision 已裁定拆出（未来独立候选）；ABORT 零记录语义澄清（D03 §31）另行裁定。
- 回退方法：revert 交付 commit 即恢复 base 行为（无 schema/数据迁移，旧库新库双向兼容）。
