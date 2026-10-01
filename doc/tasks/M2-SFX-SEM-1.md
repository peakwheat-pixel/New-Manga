---
id: M2-SFX-SEM-1
title: "SFX 翻译语义第一刀：拟声词文化对等转换（userselect 2026-10-01「SFX OCR/翻译语义」；协议 widening 先例落地）"
kind: feature
status: ready
approval: user_select_2026-10-01_sfx_sem
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-PROD-1]
base_commit: 0b43af7a
branch: agent/zcode/M2-SFX-SEM-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-SEM-1-zcode
---

# M2-SFX-SEM-1：SFX 翻译语义第一刀

## 来源与目标

- 来源：用户在 SFX-PROD-1 收口后的候选中 **userselect「SFX OCR/翻译语义」**（2026-10-01）。
- 现状缺口（已核实）：`decide_sfx_translation` 让 policy=translate 的 SFX region 进**通用对白 prompt 直译**——拟声词（「ドガ」「빠악」）被译成无意义音节而非目标语拟声词。根因=`RegionInput(region_id, text)` **无类型槽**，region_type 在进 provider 请求时丢失（`application/translation/context/step.py` 的 bundle entry 有 region_type，`build_provider_request` 未传递）。
- 目标：SFX 翻译语义=**拟声词/效果词的文化对等转换**（「ドガ」→「轰」，保持强度与简洁，非直译）——协议 widening 携带类型 + prompt 特化段。**本刀纯翻译语义**；SFX OCR（变形字识别能力）与 inpaint/重绘不在范围。

## 已核实事实

1. `RegionInput`（`src/ports/translation/protocol.py:37-39`）= (region_id, text)；`TranslationRequestPayload.regions` 校验仅 region_id。
2. `TRANSLATION_SYSTEM_PROMPT`（`translation_openai.py:42-48`）=通用 manga translation engine，无 SFX 段；`_build_user_text` regions 条目仅 id+text（`:104-107`）。
3. bundle entry 有 `region_type`（`context/builder.py:45,112`）；`build_provider_request`（`step.py:76`）构造请求时未传。
4. gate（`step.py:168`）已把 skip/manual 的 SFX 挡在翻译外——**进翻译的 SFX 全部 policy=translate**（语义特化的精确作用域）。
5. widening 先例：M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN（契约 rev 1.2 §5 widening+默认值向后兼容）；D06/TASK-002 契约=SFX 语义的文档出处（gate.py docstring 引用 D06 §85/§18）。
6. MockLocalTranslationProvider（`mock_local.py:104`）=验收链的翻译桩。

## 设计决策（代理裁决，用户可撤销）

1. **协议 widening**：`RegionInput` 增 `region_type: str = "speech"`（默认值=零破坏；值域=RegionType 枚举 fail-closed 校验——非法值 ProviderInputError）；`TranslationRequestPayload` 校验同步。
2. **请求体携带类型**：`_build_user_text` 的 regions 条目加 `"region_type"`；system prompt 增 SFX 特化段（region_type=sfx 的条目=目标语言拟声词/效果词**文化对等转换**，输出 ≤6 字符级、保持强度、禁止直译音节）。
3. **上游传递**：`build_provider_request` 从 bundle entry.region_type 填入（context 区域同样带类型——LLM 知道哪些是 SFX 上下文）。
4. **mock 对应**：MockLocalTranslationProvider 对 sfx region 的确定性输出（如 `sfx:<原文本长度>` 形态——具体形态 Owner 按既有 mock 模式定，登记）。
5. **契约文档同步**：TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md（D06 语义）相应节修订+修订记录（对照 M2-C2 先例）；M2-C1_TYPED_IPC 不动（本刀不触 IPC 面）。
6. SFX OCR/重绘=out of scope（登记遗留）。

## Acceptance Criteria

- [ ] AC1 协议 widening：RegionInput.region_type（默认 speech+枚举校验）+payload 校验+既有调用零破坏（默认值路径测试）
- [ ] AC2 语义实现：system prompt SFX 段+user_text 携带 region_type+build_provider_request 传递
- [ ] AC3 mock：sfx region 确定性输出+验收链不回退
- [ ] AC4 测试：widening 兼容/SFX 段注入/类型传递/mock/端到端（sfx region translate 路径的请求快照）
- [ ] AC5 契约文档：TASK-002 契约修订+修订记录
- [ ] AC6 回归与纪律：pytest 三套件（479+1sk 基线）不回退；cargo/vitest 留痕；diff --check EXIT=0；禁改面（detection providers/ports/detection/**、ports/providers/**、core_assembly、MERGE_*、experiments、tauri、run_clean_start_e2e.py）零触碰

## 允许/禁止

允许：`src/ports/translation/protocol.py`（widening）、`src/infrastructure/providers/translation_openai.py`（prompt+user_text）、`src/application/translation/context/step.py`（传递）、`src/infrastructure/providers/mock_local.py`、tests/**、`doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md`、Task/Handoff/verification/M2-SFX-SEM-1/**。
禁止：detection 三 provider、`src/ports/detection/**`、`src/ports/providers/**`、core_assembly.py（本刀不触装配）、MERGE_*、experiments/**、apps/**、packaging/**、tauri.conf.json、run_clean_start_e2e.py、requirements.txt（零新依赖）。

## 依赖、风险与阻塞

- 依赖：M2-SFX-PROD-1 done（sfx region 已进管线）。
- 风险：①prompt 特化的翻译质量无 GT 验证（directional——真实效果待用户实测，验收=请求快照与语义定义一致性）；②widening 的旧消费者兼容（默认值覆盖）；③契约文档映射若有出入（D06 编号）即停下登记。
- 阻塞：无。

## 遗留与边界

- SFX OCR（变形字识别率）→ 另立（OCR provider 能力）。
- SFX inpaint/艺术字重绘 → 产品后续范围。
- 翻译质量 GT 验收 → 待真实使用反馈。
