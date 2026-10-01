---
id: M2-SFX-TRANSLATE-ENTRY
title: "SFX→translate 产品入口：sfx_policy 可配置化（用户裁决④：解除 SFX 翻译评测 n=0 的前置阻断）"
kind: feature
status: done  # DSH r1 approved_with_conditions（R1 语义登记+R2 行数更正由集成方闭合；0×P0/P1）

approval: user_ruling_2026-10-01_all_four
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-PROD-1, M2-SFX-SEM-1, M2-TA3-B2]
base_commit: 8e0de8d0  # Task 授权基线；分支 fork=批次 release 8996ca55（r1 R8 口径注记，M2-IMPORT-ALLOC-LIMIT R5 同款）
branch: agent/zcode/M2-SFX-TRANSLATE-ENTRY
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-TRANSLATE-ENTRY-zcode
delivery_head: a377a25a（implement=a377a25a → handoff/Task 回填=本 commit；契约判定：TASK-002 不需修订，见 handoff §契约判定）
tip_note: handoff=doc/handoffs/M2-SFX-TRANSLATE-ENTRY-a377a25a.md；方案落点=settings["sfx"]["policy"]（ocr.script 同通道，装配期读取、re-assemble 生效、非法值装配 fail-fast、默认 SKIP）；三套件 530+1skipped 0 failed=基线 509+1sk+新增 21
---

# M2-SFX-TRANSLATE-ENTRY：SFX 翻译策略可配置入口

## 背景（TA3-B2 发现 + 用户裁决④）

生产链 SFX region 的 `sfx_policy` 恒为默认 SKIP（`domain/tasks/models.py:186` 默认值；region 创建时无配置覆盖入口），翻译门 `decide_sfx_translation` 的 translate 放行路径（SFX-SEM-1 已实现）生产不可达——TA3-B2 的 9 个 SFX region 全部 SKIP、SFX 翻译评测 n=0。用户裁决：做 SFX→translate 产品入口（策略可配置）。

## 交付（AC）

1. **AC1 配置通道**：`sfx_policy` 从 provider/pipeline 设置读取（复用既有 settings/profile 通道，如 detect provider binding 或 pipeline_defaults 的一个键，具体落点 Owner 按 M2-SFX-PROD-1 的装配结构定并留痕），默认仍 **SKIP**（行为零变化），可配置为 translate/manual。
2. **AC2 装配与消费**：detect 装配把策略传到 region 创建/翻译门消费点（`decide_sfx_translation` 已支持三值，验收其生产接线）；非法值 fail-fast（沿用 SFX conf 阈值 env 校验先例）。
3. **AC3 测试**：先红后绿——默认 SKIP 零变化（既有测试不动）；配置 translate 后 SFX region 进入翻译（handler 端到端 1 条：SFX region 译文落库）；非法值装配 fail-fast；mock 链探针（m2_acceptance 不受扰动的确认）。
4. **AC4 文档**：TASK-002 契约如涉及（策略键语义）则按契约修订流程登记（contracts 在禁改面时以 Handoff 登记移交集成方）；Handoff 登记设置键名与取值域。

## 交付记录（Owner 回填 2026-10-01，delivery_head=a377a25a）

- [x] **AC1 配置通道**——落点=任务书两候选中的路线 (a)：`settings["sfx"]["policy"]`（`ocr.script` 同一 `pipeline_defaults` 行、同一 `save_settings_section` upsert 通道；binding 级被否：policy 是 pipeline 行为策略非 step→provider 映射）。默认（缺 section/缺键/null）= **SKIP** 零行为变化；取值域=`SfxPolicy` 三值（skip/translate/manual），strip+lower 规范化；存在但非法（未知词/空白/非字符串/section 形状坏）⇒ 装配期 `ValueError`（消息含 `sfx.policy` 前缀）。实现=`core_assembly.py` 模块级 `_sfx_policy_from_settings`（`_detected_region_type` 可测先例同款）。
- [x] **AC2 装配与消费**——装配期读取（env 校验之后、mock 分支之外=DSH r1 R10 位置规则）⇒ 非法值 mock 验收形态同样 fail-fast；re-assemble 语义（settings 改后下一次 assemble 生效，无 live reload）与全部持久化键一致；传递链=`sfx_policy_cfg` → `_create_detected_region` 闭包 → `editing.create_region(sfx_policy=...)`（参数已存在，`editing/service.py` 零改动；M2-SFX-PROD-1 第 5 参 `provider_label` 链原样复用）；**仅 SFX 候选**携带配置策略，非 SFX region 恒 SKIP（泄漏不可能）；**策略仅对新建 region 生效，既有 region 不回溯**（r1 R1，恢复=重新检出或新 data root）。翻译门 `decide_sfx_translation` 三值已就绪（SFX-SEM-1），`gate.py` 零改动——生产接线由端到端测试验收。
- [x] **AC3 测试（先红后绿）**——红态实证：实现前 `test_sfx_policy_settings.py` collection error（selector 不存在）+ `test_sfx_policy_end_to_end.py` 2 failed（policy 恒 SKIP）；绿态：新增 21 条全 PASS——`tests/core/test_sfx_policy_settings.py` 19 条 Qt-free（选择矩阵 9/fail-fast 矩阵 6/默认装配闭包 SKIP/save_settings_section→re-assemble→闭包 translate+manual/非法值装配 fail-fast 含 mock 形态），`tests/core/test_sfx_policy_end_to_end.py` 2 条 Qt offscreen（acceptance 同款装配+mock bindings：TRANSLATE_ALL 落 region 断言 sfx=translate/speech=skip+译文，OCR_REGION+RETRANSLATE_REGION（SFX-SEM-1 端到端形状）`MOCK_SFX_TRANSLATION_TEXT` 落库=门放行+类型贯通双证明；manual 保留 OCR+plan 级 `SKIP_POLICY`/`sfx_skip` 登记+译文恒空+speech 无扰）。**既有测试零修改全通过**：三套件 `tests/providers tests/core tests/m2_acceptance` = **530 passed + 1 skipped 0 failed**（基线 509+1skipped + 新增 21；解释器 `T1.1.1-impl-py312`，口径见 handoff）。mock 链探针=m2_acceptance 35 条含于全量。
- [x] **AC4 文档**——**TASK-002 契约判定：不需修订**（未触契约语义：schema 三值 CHECK、gate 语义、detect 协议全原样；新增仅为装配层对既有 settings 行的读取；如集成方认为需契约级登记按流程另行处理，`doc/contracts/**` 零触碰）。设置键名/取值域/生效时机=fail-fast/默认=本节+handoff `doc/handoffs/M2-SFX-TRANSLATE-ENTRY-a377a25a.md` §方案落点。
- 纪律：`git diff --check` EXIT=0；禁改面（`src/ports/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`detection_sfx.py`、`doc/STATUS.md`）零触碰；改动面=仅 `core_assembly.py`+2 新测试文件。相邻发现只登记不修：executor backfill 单 region 绑定（`application/tasks/service.py:922`，"later scheduling slice"），影响与本 Task 无耦合。

## 允许修改面 / 禁改面

允许：`src/`（detect/translate 装配+settings 读取的最小面，Owner 提案后落笔——预期 `core_assembly.py` SFX 装配段+models 默认值不动）、`tests/**`（SFX 相关）、`experiments/M2-SFX-TRANSLATE-ENTRY/**`、`verification/M2-SFX-TRANSLATE-ENTRY/**`、Task/Handoff。
禁改：`src/ports/**`（协议 widening 已完成不重开）、`doc/contracts/**`（如需修订先在 Handoff 登记）、`packaging/**`、`apps/**`、`doc/STATUS.md`、chiqui7/ogkalu provider 检测语义。

## 纪律

- 默认行为零变化（SKIP）；precision-first 裁决不变（配置是用户显式选择，不是默认放开）。
- 基线不回退：main 509+1skipped 0 failed；GATE/闭包不涉及（无新依赖）。
