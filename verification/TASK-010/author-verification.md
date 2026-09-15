# TASK-010 Author Verification（作者自验）

- 作者：ZCode（实现者本人；独立 Review 由 DeepSeek Harness 承担，非作者）
- Task：[doc/tasks/TASK-010.md](../../doc/tasks/TASK-010.md)
- 分支：`agent/zcode/TASK-010-translation-context`（worktree `G:/CODEX/New Manga.worktrees/TASK-010-zcode`）
- base：`2bdfd6f82b67a550c0550ee930d49bdb12656322`（release `2cceb1e734c5079870662b7a28da316e46444810` 的父提交）
- **delivery_head：`cd76d30fdc561eb8f22a849eeb5989473957dc5b`**
- 记录时间：2026-09-15

## 环境

| 项 | 值 |
|---|---|
| OS | Windows 10.0.26200 x64（win32，Git Bash） |
| Python | 3.12.3（固定解释器 `G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`） |
| pytest | 9.1.1 |
| 依赖新增 | 无（仅标准库 difflib/hashlib/unicodedata；符合"不添加 Embedding/RAG"） |
| 设备 | 与仓库同机，无 GPU/模型推理，全部为确定性单元测试 |

## 命令与结果（在 delivery_head `cd76d30` 上执行）

| # | 命令 | 结果 | 退出码 |
|---|---|---|---|
| 1 | `PYTHONPATH=src python -m pytest tests/knowledge -q` | 78 passed | 0 |
| 2 | `PYTHONPATH=src python -m pytest tests -q`（全量） | 328 passed（连续 3 次） | 0 |
| 3 | `PYTHONPATH=src python -m pytest tests/core/test_architecture.py -q` | 4 passed | 0 |
| 4 | `git diff --check 2cceb1e..cd76d30 --` | 无输出 | 0 |
| 5 | `git diff --name-only 2cceb1e..HEAD` 范围核对 | 全部位于 TASK-010 白名单 | 0 |

## 范围声明

实现提交自 `2cceb1e` 起：`0df119d`（约束实体/合并/候选）→ `26ec405`（TM 服务）→ `1998e96`（Context Builder/冻结/SFX gate/Translate Step）→ `cd76d30`（TM 枚举正常化，delivery_head）。另有流程性认领提交 `cda5ab8`（仅 `doc/tasks/TASK-010.md` 状态 ready→in_progress）。

变更文件全部位于白名单：`src/domain/constraints/**`、`src/application/translation/knowledge/**`、`src/application/translation/context/**`、`tests/knowledge/**`、`doc/tasks/TASK-010.md`（加本文件与 Handoff 后的元数据提交）。未触碰 domain 其他包、AGENTS、依赖清单、Schema、共享接口与用户数据。

## 覆盖的主责 AC 与证据文件（tests/knowledge/）

| AC | 证据 | 说明 |
|---|---|---|
| AC-CONSTRAINT-001 | test_constraint_merge_and_candidates.py（3 项） | Chapter>Book>Global；他 scope 不泄漏；无 chapter 上下文时 global 生效 |
| AC-CONSTRAINT-002 | 同上（2 项） | 同层 locked>manual>auto；候选层 defer_to_locked 不改锁定项 |
| AC-CONSTRAINT-003 | 同上 + test_constraint_entities.py | active/pending/rejected/disabled 四态；pending/rejected/disabled 不作正式约束 |
| AC-CONSTRAINT-004 | test_rejected_key_is_not_recommended_again | 同 normalized key（不同表面形式）不再创建候选 |
| AC-TM-001 | test_tm_write.py（2 项） | 未确认机器译文写入抛 UnconfirmedTranslationError；无自动收集 current 的入口 |
| AC-TM-002 | 同上（2 项） | 人工确认与已校对内容可写入，含来源回溯字段 |
| AC-TM-003 | test_tm_query.py（8 项） | book Exact→book Fuzzy→全局 Exact/Fuzzy 顺序；语言对过滤；禁用不匹配 |
| AC-TM-004 | test_matches_are_reference_only + test_translate_step.py::test_tm_matches_never_write_final_translation | 匹配仅作参考；查询不写 Region/final、不自动计数 |
| AC-SFX-001/002/003 | test_sfx_gate.py（4 项）+ test_step_skips_sfx_and_translates_the_rest | skip/manual→skip_policy(reason=sfx_skip)；translate 正常；非 SFX 不 gate |
| AC-TRANS-003 | test_translate_step.py（3 项）+ test_context_builder.py::test_write_scope_only_contains_target_regions | 越界输出/缺失输出拒绝；Context Scope ≠ Write Scope |
| AC-TRANS-004 | test_entries_are_sorted_by_page_and_reading_order + test_chunks_preserve_global_reading_order | Page sort_order + Region reading_order 全程保持 |

Task 附加测试要求：优先级冲突、重复 Rejected、未确认 TM 不写、上下文越界输出拒绝均覆盖；「Run 中改术语不影响已冻结值」= test_constraint_freeze.py::test_midrun_term_edit_does_not_touch_frozen_values；「Webtoon 以 Region 窗口而非 Tile 作为上下文」= test_context_webtoon.py（6 项，builder 无 Tile 输入概念）。

## 提交范围与全量运行观察（如实记录）

1. base `2bdfd6f` 干净树（临时 worktree，已删除）全量 `2 failed, 251 passed`：失败为 `tests/rendering/test_source_style.py::TestPixelAnalyzer::test_two_horizontal_lines_estimate_size_and_direction` 等两例，仅在与其他套件同跑时出现、单独跑 `tests/rendering` 时 56 passed 全过——**pre-existing 测试顺序依赖，早于本 Task 存在，与本 Task 代码无关**（本 Task 全部为新增文件）。按协作协议未顺手修改非白名单文件，移交 Codex 处置。
2. 最终实现 HEAD `cd76d30` 上全量连续 3 次 `328 passed, 0 failed`。早前一次运行曾观察到 `2 failed, 329 passed`（收集 331）的瞬态结果，与最终稳定态相差 rendering 顺序依赖 2 例 + 收集计数 3 例；最终 HEAD 上未复现，以三次稳定结果为准。
3. 模型/视觉/性能类结果：不适用（本 Task 无模型推理、无渲染像素、无性能指标），未以 Mock 冒充。

## 设计取舍（需 Review 与 Codex 确认）

- **Fuzzy 阈值**：获批规格（D03 §14.4/D06 §12）只定「Exact + Fuzzy、不要求 Embedding」未给数值；实现默认 `0.80`（`TranslationMemoryService.DEFAULT_FUZZY_THRESHOLD`，可配置），相似度用 `difflib.SequenceMatcher`（标准库）。
- **自动候选高置信阈值**：D03 §12.5 只定状态不定数值；默认 `AUTO_ACTIVE_CONFIDENCE = 0.90`，可配置。
- **TM 模型位置**：白名单无 domain/tm 路径，TM 记录模型与 Store 协议置于 application 层（consumer-side port），持久化适配器留待后续基础设施 Task。
- **Token 预算单位**：1 token ≈ 1 字符（CJK 友好、确定性），estimator 可注入；真实 tokenizer 属 Provider 适配层。
- **Webtoon chunk 重叠**：D06 §17「前一 Chunk 的 OCR + 当前 Chunk + 后一小段」为"允许"而非必须；本版实现连续 Region 窗口 + 预算切块，chunk 间文本重叠留待 Provider 适配层。
- **TranslateStep 边界**：不含 Planner 的 Lock/skip_lock 决策与真实 Provider 调用（TASK-011+）；`provider_call` 为注入函数，输出映射守卫（TASK-002 §4 语义）在调用前强制执行。

## 未完成项

- TM/约束的 SQLite 持久化适配器：不在本 Task 白名单（属后续持久化 Task）。
- 真实 Provider 端到端翻译：依赖后续 Provider 适配 Task；本 Task 仅完成编排与映射守卫。
- rendering 套件顺序依赖缺陷：pre-existing，证据见上文第 1 条，移交 Codex。
