---
id: TASK-036
title: 设置输入校验与导出发布顺序硬化（承接 TASK-034 R-02 / R-05 / R-07）
kind: maintenance
status: in_review
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-034]
base_commit: edfdcf2fe923c8c6e97d19377c61c4b8bba25abc
branch: agent/deepseek/TASK-036-settings-validation-and-export-order
worktree: G:/CODEX/New Manga.worktrees/TASK-036-deepseek
integration_commit: null
---

# TASK-036：设置输入校验与导出发布顺序硬化

**状态提示（2026-09-17）**：`status=in_review`——**AC ①～⑦ 已完成并取证**（delivery head `c931db0`），**AC ⑧（非作者四轴 Review + Codex 集成）未执行**。证据总表：[verification/TASK-036/author-verification.md](../../verification/TASK-036/author-verification.md)；交付说明：[Handoff](../handoffs/TASK-036-c931db0.md)。

**READY（2026-09-17 用户批准释放）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`edfdcf2`（释放时 master HEAD）、branch/worktree 见顶部元数据（已创建并同步到本次释放提交）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

本 Task 是 [TASK-034](TASK-034.md) 登记的三项**仓库级遗留**的收口切片；**不改变任何路由判定算法**。

## 来源

| 项 | 来源 | 现状（Codex 释放前实测，master `edfdcf2`） |
|---|---|---|
| **R-02** | TASK-034 Review [R-02](../reviews/TASK-034-002889e.md)（并入原 R-07 冻结项） | `RoutePolicy.from_settings({'inpaint': 'oops'}, default=…)` → **静默返回默认**（`inpaint` **段本身**非 mapping 被当作"键缺失"）。`route_policy` 非 mapping 已是 fail-loud（TASK-034 R-2），**段**类型错误却仍被静默忽略 |
| **R-07a** | [TASK-034 AC ① 裁决](TASK-034-ac1-route-policy-ruling.md) R-7（本次解除冻结） | `allowed_routes='simple-fill'` → **逐字符展开** 11 个单字符 `('s','i','m',…)`；`fallback_routes` 同型 |
| **R-07b** | 同上（D-9 记录的同型陷阱） | `requirements={'brushnet': 'false'}` → `{'brushnet': True}`（`bool("false")` 恒真） |
| **R-05** | TASK-034 Review R-05 / Handoff N-1 | `src/ui/viewmodels/export/viewmodel.py` 的 `_finish`（`:379-389`）与 `_fail`（`:391-398`）**先清 `self._running`，后写 `_status` 并 emit 终态信号** → 观察者可在"标志已清、终态未发布"的**半发布窗口**内读到不一致状态（导出类测试 flaky 的机制根因） |

**判据来源（本轮已在文内固化，无需再裁决）**：R-02/R-07 的目标语义沿用 TASK-034 R-2 已确立的 **fail-closed** 原则——"用户写错的配置不得被无声忽略或无声改写"（该原则已由用户批准的裁决确立）。**若实现中发现与既有文档/测试冲突，先在 Task 中留证并交 Codex 裁决，不得自行放宽。**

## Acceptance Criteria

- [x] **AC ①（R-02）`inpaint` 段类型错误 fail-loud**：`from_settings` 用哨兵区分"键缺失"与"键存在但类型错误"；`inpaint` 非 mapping → `ProviderInputError("inpaint must be a mapping (got X)")`，与 `route_policy` 的错误消息**分级可辨**。装配回归 `test_runtime_assembly_reports_a_malformed_section_instead_of_ignoring_it`；运行回归 `test_handlers_pipeline.py::test_run_settings_non_mapping_inpaint_section_fails_the_step_loudly`（Step `FAILED`/`INVALID_INPUT`、未写出 clean artifact）。**附带关闭** TASK-034 实现的 `route_policy: null` 静默漏洞。
- [x] **AC ②（R-07a）序列校验**：新增 `_route_sequence()`——`allowed_routes`/`fallback_routes` 必须是真序列且元素全 `str`；裸字符串（原逐字符展开）、非序列（int/dict/set/None）、非 `str` 元素一律拒绝，消息含字段名与期望类型。用例：`test_route_lists_reject_a_bare_string`、`…_reject_non_sequences`、`…_reject_non_string_entries`、`test_legal_route_sequences_keep_their_meaning`。
- [x] **AC ③（R-07b）`requirements` 值域**：新增 `_requirement_flags()`——值必须真 `bool`（`"false"`/`"true"`/`0`/`1`/`None` 全部拒绝，不再 `bool()` 强转）；非 mapping 由裸 `ValueError` 改为 typed error；空 `{}` 与全 bool 行为不变（`test_requirements_values_must_be_real_bools`、`test_legal_requirement_flags_keep_their_meaning`、`test_requirements_must_be_a_mapping`）。
- [x] **AC ④（R-05）导出发布顺序**：`_finish`/`_fail` 改为终态 `_status` → `changed` → 终态信号 → `_running = False` → `changed`（`running` 的 notify）。导出用例等待收回自然终态等待（预算 5 s、断言、`export_diagnostics` 均未变）；`test_export_outcome_wait_does_not_accept_the_half_published_state` **按新顺序更新而非删除**，新增成功路径同型用例。证据：[`export-publish-order.txt`](../../verification/TASK-036/export-publish-order.txt)（前后对照）+ 判别力 2 failed（[`discriminative-prefix.log`](../../verification/TASK-036/discriminative-prefix.log)）。
- [x] **AC ⑤ 冻结解除声明**：**已解除 TASK-034 R-07 冻结**并声明；更新三处锁定旧行为的用例（`test_missing_section_or_key_returns_the_explicit_default` 的段类型断言、`test_allowed_routes_as_string_keeps_the_frozen_char_expansion`、`test_fallback_routes_and_requirements_defaults_are_frozen` 的 `bool("false")` 断言），未放宽/删除其它断言、未新增 skip。
- [x] **AC ⑥ 语义不变性证据**：12 类输入前后对照矩阵（[`input-matrix-before-after.txt`](../../verification/TASK-036/input-matrix-before-after.txt)）——8 类合法输入前后**逐字相同**（R-1～R-6 保持），非法输入由静默/改写改为 typed error（含 `route_policy: null`、字符串列表、非 str 元素、非 bool requirements 四处）。
- [x] **AC ⑦ 回归与分列**：mandated 四套件 **274 passed / 0 skipped**（基线 243）；全仓 **737 passed / 6 skipped ×7 次**（逐次 exit 0；基线 `edfdcf2` 706/6；6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`）。逐目录：providers 134→164、core 18→18、reading_export 65→66、editing 26→26、ui_shell 46→46、workbench 51→51（[`test-counts.txt`](../../verification/TASK-036/test-counts.txt)）。
- [ ] **AC ⑧** 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（协作协议 §6 四轴）与 Codex 集成验证后才能 done。
      → Handoff 与取证已交付；**Review 与集成尚未执行**，本 Task 不自行标记 `approved`/`done`。

## 允许修改范围

- `src/application/translation/inpaint/router.py`（AC ①②③）
- `src/ui/viewmodels/export/viewmodel.py`（AC ④）
- `tests/**`
- `doc/tasks/TASK-036.md`、`doc/handoffs/TASK-036-*.md`、`verification/TASK-036/**`
- **超出以上路径需先申请范围变更并由 Codex 裁决**（例如 AC ①②③ 若确需改动 `src/infrastructure/providers/runtime.py`/`handlers.py`）。

## 禁止范围

- 不得修改路由**判定算法**（`decide_route` / `acceptable_routes` / `preferred_route_order` / `route_gate` / `RouterFeatures`）、`RoutePolicy` 的既有合法语义（TASK-034 裁决 R-1～R-6）、Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail` 掩盖失败。
- **不处理 R-06**（`tests/reading_export` 的 webtoon 保存 flaky：未复现、根因未定）与 **R-03**（`DEFAULT_ROUTE_POLICY` 跨层归属，纯建议）——它们不在本 Task 范围。
- 不得把已登记的 flaky 或未定性间歇失败记为通过；不得释放 TASK-020～TASK-023、TASK-025～TASK-027、TASK-033。
- 不 push。

## 测试要求

- `python -m pytest tests/providers tests/core tests/reading_export tests/editing -q -p no:cacheprovider -rs`
- 全仓 `python -m pytest -q -p no:cacheprovider -rs` **至少 5 次**串跑并**逐次记录**（本环境全仓串跑非 100% 稳定，见 [STATUS](../STATUS.md)「已知 flaky 测试（跟踪条目）」；若复现失败**立即用 `-rf` 记录用例名**并按同一口径登记）。
- AC ④ 须给出"发布顺序改变后，观察者在 `running == False` 时必已见终态"的证据（如断言顺序敏感的用例或定向探针）。
- 分列 passed/skipped 与 skip 原因；记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-034](TASK-034.md) 已集成 `done`（唯一入口 `RoutePolicy.from_settings` 与导出诊断均由该 Task 落地）。

阻塞：**已解除**——2026-09-17 用户批准释放。

风险：
- **校验收紧可能触发现有测试**：若某既有测试依赖"静默/强制转换"的旧行为，须按 AC ⑤ 显式更新并说明，**不得**靠放宽断言绕过。
- **R-05 的发布顺序改动触及 `src/ui/**`**：须确认 `tests/ui_shell`、`tests/workbench`、`tests/reading_export` 均未依赖旧顺序；若发现消费方依赖旧顺序，先在 Task 中留证并交 Codex 裁决。
- R-06 未定性间歇失败可能再次污染"全仓 N passed"证据（已登记，非本 Task 缺陷）。

## 交付与运行记录

- Handoff：[TASK-036-c931db0](../handoffs/TASK-036-c931db0.md)（delivery_head=`c931db0`）。
- Review：尚无（待 Codex 非作者独立 Review，按协作协议 §6 四轴：Standards / Spec / Architecture / Verification）。
- 实际执行/测试：
  - 取证总表：[verification/TASK-036/author-verification.md](../../verification/TASK-036/author-verification.md)；输入矩阵：[input-matrix-before-after.txt](../../verification/TASK-036/input-matrix-before-after.txt)；发布顺序：[export-publish-order.txt](../../verification/TASK-036/export-publish-order.txt)；判别力：[discriminative-prefix.log](../../verification/TASK-036/discriminative-prefix.log)；全仓串跑：[full-suite-runs.log](../../verification/TASK-036/full-suite-runs.log)；逐目录计数：[test-counts.txt](../../verification/TASK-036/test-counts.txt)。
  - 命令与结果（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：mandated 四套件 `tests/providers tests/core tests/reading_export tests/editing` **274 passed / 0 skipped**（基线 243）；全仓 **737 passed / 6 skipped ×7 次**（逐次 exit 0；基线 `edfdcf2` 706/6；6 条 skip 均为既有 `openssl unavailable`；本轮既有间歇失败与 webtoon flaky **未触发**，未记为通过）。逐目录：providers 134→164、core 18→18、reading_export 65→66、editing 26→26、ui_shell 46→46、workbench 51→51。
  - 判别力：新测试放到 base `edfdcf2` 的 `src`/viewmodel 上 → providers **28 failed / 37 passed**、reading_export **2 failed**（AC ①②③④ 的新语义均可被判据检出）。边界：改动恰为 `src/application/translation/inpaint/router.py`、`src/ui/viewmodels/export/viewmodel.py`、`tests/**`、`verification/TASK-036/**`；越界 0；`git diff --check` 退出码 0。
- **未关闭项**：AC ⑧ 的非作者四轴 Review 与 Codex 集成；R-03（`DEFAULT_ROUTE_POLICY` 跨层归属）与 R-06（webtoon flaky 未复现）按 Task 禁止范围**不在本 Task 处理**。
- **最近状态（当前，唯一）**：2026-09-17 **AC ①～⑦ 完成并取证**，整体置 **`in_review`**，待 Codex 非作者 Review 与集成。分支 `agent/deepseek/TASK-036-settings-validation-and-export-order`、worktree `G:/CODEX/New Manga.worktrees/TASK-036-deepseek`、fixed base `edfdcf2`、delivery head `c931db0`（`dd608f4` 开工文档、`c931db0` 实现与取证）。**未 push、未合并 master、未释放任何冻结 Task。** 请 Reviewer 重点裁定：⑥ 矩阵中我主动扩大的两处行为变化（`route_policy: null`、`requirements` 非 mapping 的 typed error）；④ 的二次 `changed`（`running` notify）；以及 ② 对 `set`/生成器等非序列可迭代类型的拒绝口径。
- 历史状态（2026-09-17）：由 Codex 依 TASK-034 Review 的 R-02/R-05/R-07 与 Handoff N-1 创建为 `proposed`；随后用户批准释放为 `ready`（Owner=`DeepSeek Harness`、Reviewer=`Codex`、base=`edfdcf2`）。
