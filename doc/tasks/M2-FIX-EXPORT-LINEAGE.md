---
id: M2-FIX-EXPORT-LINEAGE
title: Export history 持久层补 included_stale/missing page ids（F-1 修复）
kind: fix
status: done
release_state: M2_FIX_EXPORT_LINEAGE_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（子 agent 代行，用户授权 2026-09-28）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC4]
base_commit: 8b0d9040
branch: agent/zcode/M2-FIX-EXPORT-LINEAGE
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode
delivery_head: 297c96557f1aa0ac41bc19fdf38c90a06badbea1（r2 amend 自 0ec1f052，DSH r1 §D whitespace-only 清理 + C4/C5，轨迹见 verification-results.md §9）
review: doc/reviews/M2-FIX-EXPORT-LINEAGE-0ec1f052-dsh-r1.md (approved_with_conditions) -> doc/reviews/M2-FIX-EXPORT-LINEAGE-d395ef70-dsh-r2.md (approved; C1-C6 closed)
integration_merge: d71883ec9a6c6fccb14b62908c02790bb3beb99c
dispatch_state: INTEGRATED
---

# M2-FIX-EXPORT-LINEAGE — Export history 持久层 included_stale/missing page ids 修复

## 来源与目标

**proposed / NOT_RELEASED 候选**——登记于 M2-AC4 集成收口（2026-09-28，integration merge `fc991821`，[集成记录](../../verification/M2-AC4/integration-890f0c74/integration.md)）。来源 = M2-AC4 缺陷 **F-1**（AC1(a) FAIL 证据；AC2(b) 持久留痕缺口）+ [DSH r1 非作者 Review](../reviews/M2-AC4-890f0c74-dsh-r1.md) §3 独立裁定（证据充分、定性准确）与 P2-3 范围裁定要求。本文件仅为登记，base/branch/worktree 未冻结，**禁止在任何会话中未经 Rebaseline Plan 释放流程实施**。

缺陷：`ExportService` 落库的 export history 行**不含** `included_stale_page_ids`/`included_missing_page_ids`。CONTINUE 放行了哪些 stale 页在持久 lineage 中不可追溯（内存 `ExportResult` 字段正确，仅持久层缺失）。

证据链（DSH r1 §3 逐行核对，全部 verified-by-reading）：
- `src/application/export/service.py:425-464` `_record` 落库 13 键无 included ids；`:467-479` `_scope_snapshot` 只序列化 `page_ids/filenames/mode/overwrite_policy/stale_policy`；`:175-191` `ExportRecord` 无该字段；`:159-172` `ExportResult` 有（内存正确）。
- `src/infrastructure/sqlite/schema.py:436-450` `export_history` 表 13 列无该列；`src/infrastructure/sqlite/reading_export.py:146-174/:206-232`（SELECT/INSERT/ON CONFLICT）及 legacy import 均无。
- 全仓 grep `included_stale|included_missing`：`src/**` 仅内存 dataclass（`service.py:170-171/234-235`）与 UI 展示计数（`ui/viewmodels/export/viewmodel.py:286-287`），无任何持久化落点。
- 探针与 xfail 场景双证据：`verification/M2-AC4/raw/probe-output.log`；`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` xfail 场景 `test_ac2_history_records_which_stale_pages_were_included`（断言点 `:583-586`）。

## 缺陷描述与触点清单（释放时由 Codex 冻结）

触点（DSH r1 §3 划法）：
- `src/application/export/service.py`（`_record`/`_scope_snapshot`/`ExportRecord`）
- `src/infrastructure/sqlite/schema.py`（新 migration：加列或 `scope_snapshot_json` 版本化 schema）
- `src/infrastructure/sqlite/reading_export.py`（SELECT/INSERT/legacy import 映射）
- 必要时导出 DTO 与前端展示
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（xfail 移除与断言转 PASS，见 AC）

**方案取舍（2026-09-29 释放时由编排会话冻结，代理裁决，用户可撤销）**：**采用方案 A**——`scope_snapshot_json` 内加 `included_stale_page_ids`/`included_missing_page_ids` 键。理由：`_parse_scope`（`service.py:482-491`）只校验 `page_ids` 是 list，加键向后兼容、旧行解析无歧义；不触碰 schema migration 纪律；方案 B 的可查询性收益当前无命令面消费者。**若实现中发现方案 A 不可行必须动 schema，停下登记 FAIL/BLOCKED 证据，不得擅自升级为方案 B**（那是范围变更）。

**per-page revision 范围裁定（DSH r1 P2-3，2026-09-29 冻结）**：**拆出本 Task 范围**——per-page 导出 revision/内容指纹需要触达导出执行路径抓取 revision 信息，范围显著更大，登记为未来独立候选（登记与否留 planning），本 Task 仅补 included ids。

**并发风险评估（DSH r1 P3-7，2026-09-29 冻结）**：`reading_export.py:176-240` write 的 read-modify-write + `DELETE … NOT IN` 并发互删问题**不在本 Task 修复范围**（既有问题、非本修复引入），Owner 在验证记录中做评估留痕即可，修复另立候选。

## Acceptance Criteria（2026-09-29 释放时冻结为正式 AC）

- [x] **AC1 — 方案 A 落地：** `_scope_snapshot` 序列化新增 `included_stale_page_ids`/`included_missing_page_ids` 键（CONTINUE 放行时非空；ABORT 拒绝场景「零任何记录」语义不变）；`_record` 落库经 `scope_snapshot_json` 携带新键；`_parse_scope` 解析兼容（新键缺省为空、类型校验 list）。`ExportRecord`/读取路径（`reading_export.py` SELECT/INSERT/legacy import）如需映射同步补齐——**以最小变更为限，不新增列、不动 schema.py**。→ **PASS**：数据源=`ExportResult.included_*`（COMPLETED 路径同源传入）；`reading_export.py` 整体字符串存取经探查**零改动**；`schema.py` 0 命中；ABORT 零记录场景继续通过。
- [x] **AC2 — xfail 移除转 PASS：** 移除 `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` 中 `test_ac2_history_records_which_stale_pages_were_included` 的 `@pytest.mark.xfail`（strict）标记，断言转 PASS；**先证实修复再移除标记**（修复前该测试证红留痕）；XPASS 一旦出现即处理，不留「意外通过」。→ **PASS**：先红=临时移除标记跑出真红（红点=原 `:584` 持久断言，EXIT=1，raw/red-pre-fix-test_ac2_history.log）→ 修复 → 转 PASS → 标记正式移除；默认套件无 XPASS；F-2 xfail 零触碰。
- [x] **AC3 — legacy 前向兼容：** 新增断言：变更前写入的旧 history 行（`scope_snapshot_json` 无新键）经新代码读取解析不报错、语义为「无 included ids 记录」而非崩溃或伪造。→ **PASS**：新场景 `test_ac2_legacy_scope_rows_without_included_keys_stay_compatible` 覆盖三通道（手工 INSERT 修复前 13 列旧行 / `import_legacy_export_history` legacy JSON 旧行 / 新键非 list → 类型化 `ExportError` 拒收），included 双键均解析为空 list。
- [x] **AC4 — 回归如实：** `tests/m2_acceptance -q` 修复后预期 **33 passed + 1 xfailed**（仅剩 F-2 xfail）；如实际数字不同，如实记录原因。既有其余测试面（tests/core 等）零回归。→ **PASS（偏差已解释）**：实际 **34 passed + 1 xfailed**（EXIT=0）= 预期 33（原 32 passed + F-1 转 PASS）+ 本 Task 按指令新增的 legacy 兼容场景 1 条（AC4 预期未计入新场景）；`tests/core -q` = **76 passed** EXIT=0 零回归。r2 交付 tip 绑定复跑：34+1xf EXIT=0 / 76 EXIT=0 / `--runxfail` 恰 1 failed（F-2）EXIT=1（raw/final-tip-rerun-r2.log）。首跑 1 failed（新场景未重置 one-time import 标记的测试自身问题）已修正并双日志留痕。
- [x] **AC5 — 证据纪律：** 命令日志带 shell、解释器、固定 HEAD、EXIT；P3-7 并发评估留痕；`git diff --check <base>..<delivery-head>` exit 0；范围自检仅落允许路径。→ **PASS（r2 达成冻结判据）**：整树 `git diff --check 8b0d9040..297c9655` = 空 EXIT=0（r1 期 6 处 raw 日志行尾空白已按 DSH §D whitespace-only 清理，`--ignore-all-space` 空 diff 证明 raw/diff-check-evidence.log，amend 轨迹 §9）；范围自检 raw 证据 raw/scope-self-check.log；交付 tip 绑定复跑 raw/final-tip-rerun-r2.log（r1 期「日志 HEAD≠声明 tip / amend 未披露 / 整树 EXIT=2」三项已闭合）；P3-7 静态评估见 verification-results.md §7；`schema.py`/`reading_export.py` 零命中。

## 允许修改范围（2026-09-29 冻结）

- `src/application/export/service.py`（`_record`/`_scope_snapshot`/`_parse_scope`/`ExportRecord` 映射）
- `src/infrastructure/sqlite/reading_export.py`（SELECT/INSERT/legacy import 的 scope_snapshot 映射，**不新增列**）
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（**显式授权**：F-1 xfail 移除转 PASS + legacy 兼容新增断言；其余场景断言不改语义）
- `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`、`verification/M2-FIX-EXPORT-LINEAGE/**`、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-*.md`

## 禁止范围

- `src/infrastructure/sqlite/schema.py`（方案 A 不动 schema；发现必须动 schema 即停下登记，不得擅自升级方案 B）、per-page revision 字段（已裁定拆出）、并发 write 修复（P3-7 只评估）。
- 不得顺手把「导出失败留 failed 记录」等 accepted-but-unspecified 语义一起改：被拒导出零任何记录是 D03 §31 语义澄清事项（M2-AC4 Handoff 已披露），应单独裁定。
- 不修改与 F-1 无关的 IPC 契约、Library page-count 面（归 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN，仍 proposed/NOT_RELEASED）；不修改 F-2 xfail 场景；不修改其他 src 路径、apps/**、doc/contracts/**、依赖。

## 交付与运行记录

- **2026-09-29 Codex 集成收口（集成方修正；本节以下字段为准）**：DSH r2 **`approved`**（C1-C6 全部真实关闭，无 P0/P1/P2），集成 merge=`d71883ec9a6c6fccb14b62908c02790bb3beb99c`（`--no-ff`，无冲突，parent2=Owner 最终 tip **`d395ef70b311b0d960cddcb0680e9fc423c0b09c`**，dispatch_state→INTEGRATED，status→done）。DSH r2 §4 八组 not_verified 由集成方在 Owner worktree 代跑全部符合期望：①tip 身份=上述 hash；②整树 `git diff --check 8b0d9040..HEAD` 空输出 EXIT=0；③`--ignore-all-space 0ec1f052..297c9655 -- raw/` 空输出（`--quiet` 判差异=1，hunk 全为行尾空白删空）；④Proof3 名单 5 文件、11+/6-（Handoff 2+2、verification-results 4+4、test +5）；⑤`e05696fd`/`cba8db48` 均 commit、reflog 轨迹与 §9.1/§9.2 ledger 一致；⑥`%cI` 时间序 01:07:24<01:12:09<01:18:42<01:22:18 成立；⑦`297c9655..HEAD` 仅证据/文档差异（无 `src/**`、无测试语义）；⑧回归三组 34 passed+1 xfailed EXIT=0 / 76 passed EXIT=0 / `--runxfail` 恰 1 failed=F-2（`:890`）EXIT=1。集成 head 复跑：34 passed, 1 xfailed EXIT=0 / 76 passed EXIT=0。AC1-AC5 集成复核全部 PASS（数字按上述实测，与 AC 判定一致）。双轮 Review 报告归档 doc/reviews/（原字节，SHA256 见集成记录）；DSH r2 P3 残留 N1-N3 由集成方收口（N1=Handoff:41 fallback 措辞改「行键存在、值为空 list」并标注集成方修正；N2=记账口径澄清见集成记录 §3；N3=final tip hash 补登于集成记录）。P3-7 采信 Owner §7 评估（未修，候选留 planning）；C6 时间口径采信 §9.3 `%cI`（release evidence「02:1x」为近似偏晚，不回改）。证据：[集成记录](../../verification/M2-FIX-EXPORT-LINEAGE/integration-d395ef70/integration.md) 及 [raw/](../../verification/M2-FIX-EXPORT-LINEAGE/integration-d395ef70/raw/)。
- **2026-09-29 Owner 交付 r2（DSH r1 `approved_with_conditions` 返修）**：代码层 approved 不变；证据层条件 C1-C6 全部关闭——C1 whitespace-only 清理（`raw/red-pre-fix-test_ac2_history.log` 46/56/59、`raw/regression-final.log` 35/54/69，`--ignore-all-space` 空 diff 证明）后交付 commit amend 重建为 `297c9655`（前身 `0ec1f052`），整树 `git diff --check 8b0d9040..297c9655` = 空 EXIT=0，交付 tip 绑定复跑三组（34 passed+1 xfailed EXIT=0 / 76 passed EXIT=0 / `--runxfail` 恰 1 failed=F-2 EXIT=1，raw/final-tip-rerun-r2.log）；C2 `e05696fd`/`cba8db48` 来历=回填 commit 两次 amend 前身（reflog 逐条登记 §9.1）；C3 范围自检 raw 证据 raw/scope-self-check.log；C4 三处 fallback 描述更正（键存在、值为空 list）；C5 F-1 场景补 persisted `included_missing_page_ids` 断言；C6 新日志头修正（解释器路径加引号+shell/command 行）+ 时间口径以 `git log --format=%cI` 核定（release 01:07:24+08 先于 claim 01:12:09 先于 red 01:12:41，时间序成立）。
- **2026-09-29 Owner 交付 r1（ZCode 子 agent 代行，用户授权 2026-09-28）**：三 commit ledger——claim `4e76b2fa` → 实现+证据 `0ec1f052`（delivery_head）→ 回填。方案 A 落地：`_scope_snapshot` 加 2 个 keyword-only 参数并序列化 `included_stale_page_ids`/`included_missing_page_ids`（数据源=`ExportResult.included_*`，COMPLETED 路径同源传入）；`_parse_scope` 缺省空 list + 非 list → `ExportError`；`reading_export.py` 整体字符串存取探查后零改动；`schema.py` 零触碰。先红（原 `:584` 持久断言 EXIT=1）→ 转 PASS；legacy 三通道兼容场景新增。回归：`tests/m2_acceptance -q` = **34 passed, 1 xfailed**（仅剩 F-2；+1=新增 legacy 场景，见 AC4）、`tests/core -q` = **76 passed**，均 EXIT=0。P3-7 并发 write 只评估未修（verification-results.md §7）。证据：[verification-results.md](../../verification/M2-FIX-EXPORT-LINEAGE/verification-results.md)、[raw/](../../verification/M2-FIX-EXPORT-LINEAGE/raw/)、[Handoff](../../doc/handoffs/M2-FIX-EXPORT-LINEAGE-owner-delivery.md)。状态 `in_review / DELIVERED_FOR_REVIEW`，r1 Review=DSH `approved_with_conditions`（代码层 approved、证据层 changes_requested），r2 已交付待复审。
