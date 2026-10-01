---
task_id: M2-SFX-SEM-1
author: ZCode
recipient: Codex
base_commit: 0b43af7a
delivery_head: 0c2e746cbf284099d4d7709f59f414135f97a6e8
status: delivered_for_review
---

# Handoff：M2-SFX-SEM-1（SFX 翻译语义第一刀）

## 交付结果

**实现范围**：SFX 翻译语义第一刀——拟声词/效果词的文化对等转换（「ドガ」→「轰」形态，非音节直译）。协议 widening 携带 region_type 进翻译请求 + system prompt SFX 特化段 + mock 对应 + TASK-002 契约文档修订。SFX OCR、inpaint/重绘 out of scope（遗留登记）。

**提交列表**（claim=86ce44b4 为 release commit，实现+文档两 commit）：

| commit | 内容 |
|---|---|
| `0c2e746c` | 实现+测试+契约文档（11 文件，+352/-6）：protocol widening、prompt SFX 段、user_text/生产链/应用层类型传递、mock sfx 输出、+11 测试、TASK-002 §4+Revision history |
| `80ab3d43` | Task 回填（AC×6 勾选+frontmatter `in_review`+delivery_head）+ 本 Handoff |
| `1b7303e7` | prompt 拟声词示例「ゴショーン」→常用形「バキッ」（本 Handoff 引文同步；无测试语义变化） |

**变更路径**：
- `src/ports/translation/protocol.py` — AC1 widening
- `src/infrastructure/providers/translation_openai.py` — AC2 prompt+user_text
- `src/infrastructure/providers/handlers.py` — AC2 生产链传递（允许清单最小补充，见下）
- `src/infrastructure/providers/mock_local.py` — AC3
- `src/application/translation/context/step.py` — AC2 应用层 `region_types`
- `tests/providers/{test_translation_protocol,test_remote_providers,test_handlers_pipeline,test_mock_local}.py`、`tests/knowledge/test_translate_step.py` — AC4
- `doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md` — AC5

**裁决落地与偏差登记**：

1. **AC1 widening**：`RegionInput.region_type: str = "speech"`（默认值=既有两参构造零破坏，M2-FIX-LISTBOOKS rev-1.2 先例）。**ports→domain 反向依赖无先例**（grep 全 `src/ports/` 零匹配）→ 按裁决 1 条件分支走**本地值集常量** `REGION_TYPE_VALUES = frozenset({"speech","narration","sfx","title","note","other"})`，注释声明与 `domain.regions.entities.RegionType` 的同步责任（domain 新增枚举成员不同步本集合时在此 fail-closed）。非法值 → `ProviderInputError(stage="translate")`，校验在 `TranslationRequestPayload.__post_init__`。
2. **AC2① prompt 全文**（`TRANSLATION_SYSTEM_PROMPT`，新增 SFX 段）：

   > You are a manga translation engine. Translate every TARGET region into the requested target language and answer with a single JSON object of the form {"translations":[{"region_id":"...","translated_text":"..."}]}. Return exactly one entry per requested region_id, never rename, omit or invent an id, and use CONTEXT regions only as context. Regions whose region_type is "sfx" are manga onomatopoeia / sound-effect words (e.g. ドガ, バキッ): translate them by CULTURAL EQUIVALENCE into the natural onomatopoeia of the target language that expresses the same sound or emotion — never transliterate the source syllables. Keep the original's intensity and brevity: at most 6 characters unless the source is longer; when no equivalent onomatopoeia exists, use the shortest natural effect word. Speech and all other region types keep their normal translation semantics unchanged.

   （注：源码中以 `\u30c9\u30ac`、`\u30d0\u30ad\u30c3` 转义书写「ドガ、バキッ」，语义同上。）
3. **AC2② user_text**：regions 条目 `{region_id, text, region_type}`；**context 条目不加**——`ContextPage` 是页面级上下文结构（page_id/position/text/reading_order），无 region 类型槽，扩其结构超出本刀最小面（最小决策登记）。
4. **AC2③ 传递落点转移（任务事实偏差登记）**：裁决前提"`build_provider_request` 构造 RegionInput"与代码不符——`step.py::build_provider_request` 构造的是**应用层** `TranslationRequest`（prompt 字符串形态），不构造 `RegionInput`；生产链唯一构造点是 `handlers.py:401`（`handle_translate`）。落地两处：① `handlers.py::handle_translate` 构造 `RegionInput(region_id, source_text, region_type=region.region_type.value)`（单行 widening 传参；handlers.py 不在允许清单、也不在禁改面，登记为**允许清单最小补充**——这是 SFX 类型进入生产 provider 请求的唯一路径，端到端验收必经）；② 应用层 `TranslationRequest` 增 `region_types: Mapping[str, str]`（region_id→region_type，覆盖全部 bundle entries 含 context 角色；默认空映射零破坏），`build_provider_request` 填充（满足裁决应用层意图与 AC4⑤）。prompt 行 `[TARGET]/[CONTEXT]` 格式不动。
5. **AC3 mock 形态**：sfx 条目 → 固定常量 `MOCK_SFX_TRANSLATION_TEXT = "MOCK-SFX-TRANSLATED-TEXT"`，非 sfx 条目 → 既有 `MOCK_TRANSLATION_TEXT`。任务建议 `sfx:<原文本长度>` 形态，**选固定常量**：与 mock 模块 determinism contract 的 fixed-texts 注释模式一致（同输入恒同输出、无派生值），验收 digest 稳定性最强；判定=`region.region_type == "sfx"`。
6. **AC5**：TASK-002 契约无既有修订记录格式（grep 确认）→ 文末新增「Revision history」节（`1.1` 条目，参照 M2-C1 格式；原文为未版本化基线已注明）。region_type 语义落 §4（多目标输入与输出映射——翻译请求结构在本契约的对应节；D06 §18.1 为概念输入列表无字段结构）。M2-C1 TYPED_IPC 零触碰。

## 验证证据

环境：主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（PYTHONPATH=src）；被测 commit=`0c2e746c`。

| AC/场景 | 实际命令/步骤 | 结果 |
|---|---|---|
| AC1 widening 兼容（旧两参构造=speech） | `pytest tests/providers/test_translation_protocol.py::test_region_input_defaults_to_speech` | PASS |
| AC1 值集全覆盖+非法值 fail-closed | `test_payload_accepts_every_region_type_value`、`test_payload_rejects_unknown_region_type` | PASS |
| AC1/AC2 payload 序列化含 region_type | `test_payload_serializes_region_type`（sfx 快照断言） | PASS |
| AC2 prompt SFX 段关键约束词 | `pytest tests/providers/test_remote_providers.py::test_system_prompt_carries_sfx_specialization`（onomatopoeia/CULTURAL EQUIVALENCE/never transliterate/at most 6 characters/intensity/shortest natural effect word/semantics unchanged） | PASS |
| AC2 user_text 携带 region_type | `test_user_text_carries_region_type`（sfx 条目快照 + speech 条目默认值） | PASS |
| AC2 应用层 region_types 传递 | `pytest tests/knowledge/test_translate_step.py::test_provider_request_carries_region_types`（speech/narration/sfx 混合 primary+context entries） | PASS |
| AC3 mock sfx 确定性 | `pytest tests/providers/test_mock_local.py`（3 例：sfx 固定文本/speech 默认/混合两次调用相同） | PASS |
| AC4 端到端 | `pytest tests/providers/test_handlers_pipeline.py::test_sfx_translate_region_carries_type_and_maps_output`：sfx region policy=translate → provider 收到 `region_type='sfx'` → 输出映射回 region 写 machine/final translation（render blocked 形态与既有 RETRANSLATE 测试一致） | PASS |
| AC6 回归 providers | `pytest tests/providers -q` → **327 passed, 1 skipped**（基线 317+1sk，新增 11） | PASS |
| AC6 回归 core | `pytest tests/core -q` → **127 passed**（基线持平） | PASS |
| AC6 回归 m2_acceptance | `pytest tests/m2_acceptance -q` → **35 passed**（基线持平；QML TypeError stderr 为既有测试无害噪音） | PASS |
| AC6 diff --check | `git diff --check 86ce44b4` → **EXIT=0** | PASS |
| AC6 禁改面 | `git diff --stat 86ce44b4 -- detection_{sfx,manga,doctr}* ports/detection ports/providers core_assembly.py MERGE_* experiments apps packaging tauri.conf.json run_clean_start_e2e.py requirements.txt` → **空**；`.rs/.ts/.tsx/.qml/.toml` diff=0 行 | PASS |
| cargo/vitest | 本刀零触碰 Rust/TS 面（上行为证）→ 零需求，声明留痕 | N/A |

合计 **489 passed + 1 skipped, 0 failed**（基线 479+1skipped 不回退，新增 11 如实）。

## 接收方式

- 分支/worktree：`agent/zcode/M2-SFX-SEM-1` @ `G:/CODEX/New Manga.worktrees/M2-SFX-SEM-1-zcode`；base=`0b43af7a`，交付 head=`0c2e746c`。
- 复现：`cd` 该 worktree 后 `PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q`。
- 前置条件：无网络需求；无新依赖（requirements.txt 零改动）。
- Reviewer（DeepSeek Harness，非作者）建议核对：①TASK-002 §4 修订条目与 Revision history `1.1` 的语义一致性；②`REGION_TYPE_VALUES` 与 `domain.regions.entities.RegionType` 值集逐值比对；③handlers.py 允许清单补充的裁决认可；④prompt SFX 段与裁决文案要点逐条对照。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-SEM-1 Review（DeepSeek Harness 非作者独立 Review）→ Codex 集成。
- 推荐 Agent / Reviewer：DeepSeek Harness（Review）；集成=编排会话代行 Codex。
- 推荐原因与前置依赖：本刀已 delivered_for_review，AC×6 自证通过；Review 通过后可集成。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-SFX-SEM-1`，base `0b43af7a` / head `0c2e746c`（+回填 commit）。
- 允许修改路径：Review 意见按协作协议流程；集成由 Codex 执行 merge。
- 禁止范围与新增授权条件：禁改面同 Task 正文；无新增授权。
- 交付物：本 Handoff + Task 回填 + `0c2e746c` 实现提交。
- 验证命令、环境与完成 Gate：上表命令；完成 Gate=独立 Review 通过 + Codex 集成验证（协作协议 §5.1）。
- 可直接转发给 Agent 的指令：

  > 对 M2-SFX-SEM-1 做非作者独立 Review：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-SEM-1-zcode`，branch `agent/zcode/M2-SFX-SEM-1`，交付 head `0c2e746c`（+Task/Handoff 回填 commit）。核对 [doc/handoffs/M2-SFX-SEM-1-0c2e746c.md] 验证证据表逐条复跑（pytest 三套件 489+1skipped 0 failed、diff --check EXIT=0、禁改面空 diff）；重点：①`REGION_TYPE_VALUES` 与 domain RegionType 值集一致性；②TASK-002 §4/Revision history 1.1 语义与实现一致；③handlers.py 单行传参的允许清单补充裁决；④prompt SFX 段与六条裁决文案要点对照。产出 Review 报告至 verification/M2-SFX-SEM-1/。

## 风险与遗留

- **翻译质量 directional**（任务风险①原样登记）：prompt SFX 段的语义定义已由请求快照测试锁定（请求结构与语义定义一致性=验收口径），但真实 LLM 的拟声词转换质量无 GT 验证——待用户实测反馈；不将 Mock/请求快照成功表述为模型质量达标。
- **SFX OCR（变形字识别率）** → 另立 Task（OCR provider 能力），本刀不触。
- **SFX inpaint/艺术字重绘** → 产品后续范围。
- **`REGION_TYPE_VALUES` 同步责任**：ports 层本地值集与 domain 枚举为两份定义（ports→domain 无 import 先例），domain 新增 RegionType 成员时必须同步，否则新类型 region 在翻译请求 fail-closed 被拒（注释已声明）。
- **handlers.py 允许清单补充**：超出 Task 允许清单字面、不触禁改面的单行传参，已登记裁决理由（生产链类型传递唯一路径）；若 Review/集成不认可，回退该行后 SFX 类型在生产链退化为默认 speech（语义特化失效，端到端测试需同步调整）。
- **回退方法**：revert `0c2e746c` 即恢复 86ce44b4 语义（widening 默认值保证无数据/契约残留）。
