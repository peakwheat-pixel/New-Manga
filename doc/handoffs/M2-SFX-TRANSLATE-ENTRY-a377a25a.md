---
task_id: M2-SFX-TRANSLATE-ENTRY
author: ZCode
recipient: Codex（Integrator）；DeepSeek Harness（非作者 Reviewer）
base_commit: 8e0de8d0
delivery_head: a377a25a
status: in_review
---

# Handoff：M2-SFX-TRANSLATE-ENTRY（SFX 翻译策略可配置入口）

## 交付结果

### 调用链勘察结论（落笔前完成，全部有代码锚点）

1. **翻译门已三值就绪，无需改动**：`decide_sfx_translation`（`src/application/translation/context/gate.py:32`）translate 放行 / skip+manual → `skip_policy(sfx_skip)`；消费点两处——translate step（`application/translation/context/step.py:176`）与 plan 级门（`application/tasks/service.py:418-423`，经 `_sfx_gate_suppresses` 委托同一函数，planner 与执行层不漂移）。
2. **缺环只有一处**：detect handler（`infrastructure/providers/handlers.py:287`）→ 装配闭包 `_create_detected_region`（`bootstrap/core_assembly.py`）→ `RegionEditingService.create_region`（`application/editing/service.py:247`，`sfx_policy` 参数**已存在**、默认 SKIP）。闭包未传参 ⇒ 生产恒 SKIP。M2-SFX-PROD-1 的第 5 参（`provider_label`）传递链原样复用。
3. **settings 通道先例**：`PipelineDefaultsService.save_settings_section("ocr", {"script": ...})`（`application/settings/pipeline_defaults.py:105`）→ `pipeline_defaults` 行 `settings_json` → 装配侧 `_load_pipeline_defaults(conn)`（`bootstrap/core_assembly.py:441`）可读。写桥在装配已接好（`core_assembly.py` 的 `pipeline_defaults = PipelineDefaultsService(...)`）。
4. **fail-fast 先例**：`NEWMANGA_SFX_DETECTION` / `NEWMANGA_SFX_CONF_THRESHOLD` env 校验在装配段、mock 分支之外（DSH r1 R10 决议，`core_assembly.py` 注释在案）。
5. **相邻发现（只登记不修）**：executor 的 backfill（`application/tasks/service.py:922 _backfill_detected_regions`）把无 region 页任务只绑**第一个**检出 region（reading_order 1）——多 region 页的 region 级链路展开是已登记的后续调度片；本 Task 端到端测试按此真实语义组织（TRANSLATE_ALL 创建 + 逐 region 跟进命令），不改调度语义。

### 方案落点（AC1 落点自选留痕）

- **配置键（选任务书路线 (a)）**：`settings["sfx"]["policy"]`——与 `ocr.script` 同一 `pipeline_defaults` 行、同一 `save_settings_section` upsert 语义；写入方式 `save_settings_section("sfx", {"policy": "skip" | "translate" | "manual"})`。路线 (b)（detect provider binding 级）被否：policy 是 pipeline 行为策略而非 step→provider 映射，且 binding 校验形状（provider id/mapping）与之不符。
- **读取时点**：装配期（`assemble_core_services` 内、env 校验之后、mock 分支之外——DSH r1 R10 位置规则）。**re-assemble 语义**：settings 改后下一次 assemble 生效（pipeline_defaults 行是唯一事实源，无 live reload），与其余持久化键一致。**作用域（r1 R1 定案登记）：策略仅对「此后新建」的 region 生效**——`create_region` 只在 detect 新建时被调用，已有 region 被 detect handler 复用（`handlers.py:258-269`）、不回溯；既有手稿库的 SFX→translate 解锁需重新检出（清除后重跑 detect，注意 detect stage 有效性）或使用全新 data root；region 级策略更新入口（`Region.apply_sfx_policy`）暂无消费者，登记为后续候选（含 pinning test 建议：预置 SKIP region + policy=translate 重跑 detect 断言仍 SKIP）。
- **取值域与 fail-fast**：`SfxPolicy` 枚举三值（skip/translate/manual），strip+lower 规范化（与 env 门一致）；缺 section/缺键/null → 默认 **SKIP**（零行为变化）；存在但非法（未知词/空白/非字符串/section 形状坏）→ 装配期 `ValueError`（消息统一含可检索前缀 `sfx.policy`），mock 验收形态同样 fail-fast。
- **传递链**：`_sfx_policy_from_settings`（模块级纯函数，仿 `_detected_region_type` 可测先例）→ 装配读出 `sfx_policy_cfg` → `_create_detected_region` 闭包捕获 → **仅当** `_detected_region_type(label) is RegionType.SFX` 时传 `editing.create_region(sfx_policy=sfx_policy_cfg)`，其余 region 类型恒 SKIP（配置不可能泄漏到非 SFX region）。
- **不动面**：`models.py`（默认值不变）、`gate.py`（三值已实现）、`handlers.py`、`editing/service.py`（参数已贯通）、`detection_sfx.py`（provider 检测语义零触碰）、`src/ports/**`、`doc/contracts/**`。

### 契约判定（TASK-002）

**不需要修订**：本 Task 未触任何契约语义——region schema 的 `sfx_policy` 三值 CHECK 约束（`infrastructure/sqlite/schema.py:230`）、`decide_sfx_translation` 语义（TASK-002 §7.2）、detect 协议（匿名 label 前缀）全部原样；新增的只是装配层对一个既有 settings 行的读取。若集成方认为设置键需要契约级登记（例如 React 设置页 Task 的 IPC 面定义时），按契约修订流程另行处理——`doc/contracts/**` 在本 Task 禁改面内，未触碰。

### 变更路径与提交列表

| commit | 内容 |
|---|---|
| `a377a25a`（delivery_head） | `implement(M2-SFX-TRANSLATE-ENTRY)`：`src/bootstrap/core_assembly.py`（+`_sfx_policy_from_settings` 纯函数+装配读取+闭包传参，+80 净行（r1 R2 更正：hunk 净增 0+1+6+49+13+11，文件 1123→1203 行））+ `tests/core/test_sfx_policy_settings.py`（19 条，Qt-free）+ `tests/core/test_sfx_policy_end_to_end.py`（2 条，Qt offscreen）；红→绿叙述见 commit body |
| 本 handoff commit | `doc/handoffs/M2-SFX-TRANSLATE-ENTRY-a377a25a.md` + Task frontmatter/AC 回填 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 先红 | `pytest tests/core/test_sfx_policy_settings.py tests/core/test_sfx_policy_end_to_end.py -q`（实现前） | TASK-012-py312 venv / base 8e0de8d0 工作区 | collection error（selector 不存在）+ 2 failed（policy 恒 SKIP）| 会话记录（红态未入库，红→绿由 commit body 叙述） |
| AC3 新增转绿 | 同上（实现后） | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe` / a377a25a | 21 passed | 本表下行全量含 |
| AC3 默认零变化（既有不动） | `pytest tests/providers tests/core tests/m2_acceptance -q` | 同上 / a377a25a | **530 passed + 1 skipped 0 failed** = 基线 509+1skipped + 新增 21；既有测试**零修改** | 本行即证据（解释器头见「接收方式」） |
| AC1/AC2 矩阵+接通 | `test_sfx_policy_from_settings_matrix`（9 参数化）/ `..._illegal_fails_fast`（6）/ `test_default_assembly_creator_keeps_skip` / `test_settings_policy_{translate,manual}_reaches_the_creator` / `test_settings_policy_illegal_fails_the_assembly` | 同上 / a377a25a | 全 PASS（真实装配 + 装配自己的 region_creator 闭包驱动，DSH r1 R9 解包接缝） | tests/core/test_sfx_policy_settings.py |
| AC3 translate 端到端 | `test_translate_policy_runs_the_sfx_region_end_to_end`：TRANSLATE_ALL 落 region（sfx=translate 落库/speech=skip 正常译文）→ OCR_REGION → RETRANSLATE_REGION：translate step COMPLETED、plan decision=run、`MOCK_SFX_TRANSLATION_TEXT` 落库（mock 仅对 region_type=sfx 请求返回该文本 ⇒ 类型+策略全链贯通双证明） | 同上 / a377a25a | PASS | tests/core/test_sfx_policy_end_to_end.py |
| AC3 manual 拦截 | `test_manual_policy_keeps_the_sfx_region_untranslated`：policy=manual 落库；OCR 保留（manual keeps Detect/OCR）；RETRANSLATE_REGION plan 登记 `SKIP_POLICY`/`sfx_skip`、无 translate step run、译文恒空；speech 邻居正常 | 同上 / a377a25a | PASS | 同上 |
| AC3 m2_acceptance 不受扰 | 三套件全量含 m2_acceptance 35 条 | 同上 / a377a25a | 35 passed（mock 链零扰动） | 同上 |
| 纪律 | `git diff --check`；`git status --porcelain`；禁改面 diff | a377a25a | EXIT=0 / 提交后干净 / `src/ports/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`detection_sfx.py`、`doc/STATUS.md` 零触碰（改动面仅 `core_assembly.py`+2 新测试文件） | commit diff 即证据 |

**未运行/未覆盖（如实）**：真实模型链（chiqui7/ogkalu 权重推理）未跑——本 Task 是配置通道，检测/翻译模型质量不在范围内（TA3-B2 已有诚实基线）；React/IPC 设置页 UI 入口未做（核心通道 `save_settings_section` 已可用，UI 面属后续 Task）；`NEWMANGA_SFX_DETECTION=off` 与 policy 组合未单列（off 时无 SFX 候选产生，policy 读取仍生效但无消费点，语义自明）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-TRANSLATE-ENTRY`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TRANSLATE-ENTRY-zcode`，base `8e0de8d0`，delivery_head `a377a25a`。
- 复现命令（worktree 根）：
  `PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q`
  预期 `530 passed, 1 skipped`（QML TypeError stderr 行为 Legacy UI 测试噪音，与本 Task 无关）。
- 解释器口径如实登记：本机 `C:\Python314` 系统解释器缺 PySide6/numpy/cv2/PIL，跑不完整三套件（m2_acceptance 8 failed 为已知环境形态，STATUS C4 checkpoint 有先例记录）；基线验证用 `T1.1.1-impl-py312` venv（PySide6+numpy+cv2+PIL+pytest 9.1.1 齐备）。`TASK-012-py312` 缺 numpy/cv2/PIL，仅可跑 Qt-free 子集。
- 无新依赖、无 schema 迁移、无契约变更。

## 下一任务建议（必填）

- Task ID / 标题：无新 Task；本 Task 进入 DSH 非作者 Review → Codex 集成（既有流程）。
- 推荐 Agent / Reviewer：Reviewer=DeepSeek Harness（非作者）；Integrator=编排会话代行 Codex。
- 推荐原因与前置依赖：依赖已满足（M2-SFX-PROD-1/M2-SFX-SEM-1/M2-TA3-B2 全 done）；交付自检全绿。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch/worktree 见上节；base `8e0de8d0` / delivery_head `a377a25a`。
- 允许修改路径：Review 意见限 `src/bootstrap/core_assembly.py` SFX 段、`tests/core/test_sfx_policy_{settings,end_to_end}.py`、本 Task/Handoff/verification；集成如有契约登记诉求按流程另行授权。
- 禁止范围与新增授权条件：`src/ports/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`detection_sfx.py`、`doc/STATUS.md`（集成方专属）。
- 交付物：代码+测试+handoff+Task 回填（本 commit 链）。
- 验证命令、环境与完成 Gate：上节复现命令；Gate=三套件 0 failed + 禁改面零触碰。
- 可直接转发给 Agent 的指令：`请 DeepSeek Harness 以非作者身份 review agent/zcode/M2-SFX-TRANSLATE-ENTRY @a377a25a（handoff: doc/handoffs/M2-SFX-TRANSLATE-ENTRY-a377a25a.md）：重点核 _sfx_policy_from_settings 的 fail-fast 矩阵与默认 SKIP 零变化主张、闭包仅对 SFX 候选传参的泄漏防护、端到端断言是否真实贯通 plan 门与 step 门；验证命令见 handoff 接收方式。`

## 风险与遗留

1. **backfill 单 region 调度片（相邻发现，未修）**：无 region 页任务经 detect 后只绑第一个检出 region（`_backfill_detected_regions`，代码注释自称 "later scheduling slice"）。影响：TRANSLATE_ALL 一轮不会翻译同页全部检出 region，需逐 region 跟进命令。与本 Task 无耦合（本 Task 测试按真实语义组织），建议作为独立调度 Task 释放。
2. **设置 UI/IPC 入口未做**：核心写通道 `save_settings_section("sfx", {...})` 已可用（测试往返覆盖），但 React 设置页尚无该键的界面；用户配置当前经 IPC/开发者路径。建议后续由 Qoder 在设置页 Task 中接入（键语义见本 handoff「方案落点」）。
3. **默认仍是 SKIP**：precision-first 裁决不变；translate 路径生产可达但需用户显式配置。SFX 翻译质量评测（TA3-B2 的 n=0 缺口）须在用户真实配置 translate 后重新计量，本 Task 不预设质量结论。
4. **回退方法**：单 commit 代码面（+2 测试文件、core_assembly 局部段），revert `a377a25a` 即完整回退；无数据/ schema 迁移，已落库的 `sfx_policy` 值由既有 CHECK 约束与门语义自洽。

## superseded-by（M2-TASKS-BACKFILL-MULTIREGION 集成时搬运，2026-10-02）

本文「multi-region page needs one TRANSLATE_ALL run for detect+creation and per-region follow-up runs」与「the registered scheduling slice」两处表述已被取代：executor backfill 的多 region 逐 region fan-out 已由 [M2-TASKS-BACKFILL-MULTIREGION](M2-TASKS-BACKFILL-MULTIREGION-f541b2f4.md) 落地（同 run 内 fan-out，e2e 断言同步翻转）；「registered scheduling slice」不再是待办。
