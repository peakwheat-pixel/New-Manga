# M2-SFX-SEM-1 非作者独立 Review（DeepSeek Harness，纯静态）

审查对象：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-SEM-1-zcode`（branch `agent/zcode/M2-SFX-SEM-1`），artifact=`review-input.diff`（693 行/13 文件），tip 链经 `.git/worktrees/.../logs/HEAD` reflog 核对：`86ce44b4 → 0c2e746c → 80ab3d43 → 1b7303e7 → 00c9de60`（与锚点一致）。本会话沙箱无 shell（同仓库既往 DSH Review 记录一致），全部结论为只读静态取证，未修改任何文件。

## Verdict
**approved_with_conditions**（0×P0，0×P1；2×P2 证据/覆盖条件 + 3×P3 + 3×P4，均可由集成方在放行条件内闭合）

## 逐项核对表

| 项 | 结论 | 依据 |
|---|---|---|
| A widening 正确性 | **通过（1 处口径保留）** | `protocol.py:36-44` 本地值集、`:47-54` 默认值、`:76-91` 全部 regions fail-closed、`:93-103` 序列化；与 `domain/regions/entities.py:20-28` **逐值一致**（speech/narration/sfx/title/note/other）；`Region.__post_init__`（`entities.py:239-241`）强制枚举，`.value` 安全；生产构造点全仓唯一=`handlers.py:404-408`，其余为 tests（5 文件）与 experiments/TASK-017（自带协议副本 `experiments/TASK-017/protocol.py`，不经本模块）；零破坏由默认值保证。保留项见 R3/R6 |
| B 语义实现保真 | **通过（1 处 info 口径，见 R5）** | 六要点逐条命中：`translation_openai.py:47-49` 文化对等、`:50-51` 禁止音节直译、`:51-52` ≤6 字符、`:51-52` 强度/简洁、`:52-53` 最短自然效果词兜底、`:53-54` 对白语义不变；`_build_user_text` `:112-119` regions 带 `region_type`；`step.py:52-55`+`:135-137` `region_types` 覆盖全部 entries（含 context 角色）。**口径差**：provider 侧 user_text 的 context 条目**不带**类型（`ContextPage` 无类型槽），而应用层 `region_types` **带** context 角色——两者是不同对象、不同路径，登记如实，但无消费者（R5） |
| C 落点转移裁定 | **追认**（语义正确、登记如实） | `handlers.py:386` `region = self.deps.regions.get_region(region_id)` → `application/editing/ports.py:17-20` 返回 domain `Region`；`bootstrap/core_assembly.py:735, 973` 注入 `SqliteRegionRepository`，其 `regions.py:55` 走 `RegionType(row[...])` + `entities.py:239` 强制枚举 ⇒ `.value` 恒为字符串；同型先例 `application/translation/context/builder.py:111`；单行传参、不触禁改面、Task `:94`/Handoff `:42` 双处登记。裁定前提（`build_provider_request` 构造 `RegionInput`）确与 `step.py:126-138` 事实不符，Owner 的更正成立 |
| D mock 语义 | **通过** | `mock_local.py:40-43` 固定常量 + `:121-134` 按 `region_type == "sfx"` 分支（`RegionType` 为 `str` 枚举，比较恒稳）；输出以 `region.region_id` 为键 ⇒ 映射回正确 region；与 `:35-39` fixed-texts determinism 注释一致（无派生值、无 page/run 标识）。m2_acceptance 全目录无 sfx/无 `MOCK_TRANSLATION_TEXT` 依赖（grep 空），digest 不受影响 |
| E 测试质量 | **通过（矩阵完整；覆盖范围见 R2）** | 新增 11 例：protocol 4（`:142-186`）／remote 2（`:275-335`）／handlers 端到端 1（`:758-839`）／mock 3（新文件）／knowledge 1（`:204-232`，不在 AC6 三套件内）；端到端为真实链：真实 SQLite + `ProductionHandlers` + `FakeTranslationProvider`（`providers_helpers.py:162-179` 记录 `payload`）→ 断言 `payload.regions[0].region_type == "sfx"` → 断言 DB `machine/final_translation` 写回；既有测试**断言零改动**（diff 仅 `test_translation_protocol.py:14` 一行 import 增补 + 追加用例） |
| F 契约文档 | **通过（2 处格式/落点问题，见 R4）** | `TASK-002:132` §4 新增条目语义与实现一致（默认 speech/值域/枚举外 fail-closed/文化对等/skip·manual 仍拦截）；`§7.2` 引用正确（`:217-225` 确为 skip/manual 拦截）；`§4` 位置与 `Revision history` `:346-350` 已建，未版本化基线已披露；`M2-C1:3-10` 先例的差异见 R4。`D06 §18.1`（`06_TRANSLATION_PIPELINE.md:635-644`，概念输入列表）与 `§85:2446-2475`（translate=进入正常翻译）**未被引用/未改**——D06 不在允许清单，属正确取舍（后续指针建议见 R4） |
| G 范围纪律 | **通过；AC6 计数口径不成立（R1）** | 13 文件全落允许清单，唯一例外 `handlers.py`（已登记、应追认）；禁改面（detection 三 provider、`ports/detection/**`、`ports/providers/**`、`core_assembly.py`、`MERGE_*`、`experiments/**`、`apps/**`、`packaging/**`、`tauri.conf.json`、`run_clean_start_e2e.py`、`requirements.txt`）按 diff 文件清单**零出现**；`.rs/.ts/.tsx/.qml/.toml` 零出现。**算术**：589 口径实为 479+**10**=489，不是 479+11 |

## Findings

**R1 [P2]｜`doc/tasks/M2-SFX-SEM-1.md:60`（同 `:171`）、`doc/handoffs/M2-SFX-SEM-1-0c2e746c.md:88, :95`｜AC6/Handoff 计数口径算术不自洽｜**
AC6 写「基线 479+1skipped+**新增 11**=489+1skipped」，但 479+11=490；Handoff 写「providers 327（基线 317+1sk，**新增 11**）」，317+11=328。静态点算新增用例：tests/providers 内 4+2+1+3=**10**（`test_translation_protocol.py` 新增 4、`test_remote_providers.py` 2、`test_handlers_pipeline.py` 1、`test_mock_local.py` 3），第 11 条在 `tests/knowledge/test_translate_step.py:204`，而 AC6 三套件与复现命令（Handoff `:100`）都不含 `tests/knowledge`。故 317+10=327、479+10=489 自身成立，错的只是把 11 当作套件增量。
**建议**：改为「三套件内新增 10（489=479+10，providers 327=317+10）；另有 1 例落 `tests/knowledge`（不在三套件口径，按 node id 单跑）」，并让 489 与 327 两处口径同源。

**R2 [P2]｜改动面 `src/infrastructure/providers/handlers.py:399-414`、`tests/knowledge/test_translate_step.py`｜回归覆盖缺口：被改的生产文件与其对应套件未纳入本轮回归｜**
`handlers.py` 是 `tests/pipeline/*`（production seam，如 `test_pipeline_production_seam.py`）与 `tests/providers` 的共同覆盖对象；`tests/knowledge` 被本刀改动却仅按单条 node id 跑（Handoff `:85`）。AC6 只跑了 providers/core/m2_acceptance，其中 core 与 m2_acceptance 对本次改动实际无覆盖（m2_acceptance 无 sfx region）。仓库既有惯例是全量 `pytest tests`（`doc/14_TAKEOVER_VERIFICATION.md:22-23` 记录 982 collected）。
**建议（放行条件）**：集成方在冻结 tip 至少补跑 `pytest tests/pipeline tests/knowledge -q`（并在同轮重跑三套件），EXIT=0 后放行；静态检查显示风险低（`test_pipeline.py:614-627` 只断言 planning、`test_full_chain.py` 用 `FakeTranslationProvider` 而非 mock 常量），但结论应由实跑闭合。

**R3 [P3]｜`src/ports/translation/protocol.py:36-44`；`tests/providers/test_translation_protocol.py:152-161`｜「同步责任」仅靠注释，且新增测试是自洽断言，无法发现域侧漂移｜**
`test_payload_accepts_every_region_type_value` 用 `REGION_TYPE_VALUES` 生成输入再与 `REGION_TYPE_VALUES` 比较（集合比自身）；`domain/regions/entities.py:20-28` 与 `infrastructure/sqlite/schema.py:224-225` 是另两份定义（共三份）。domain 新增成员时，本集合与 SQLite CHECK 都不会报警。
**建议**：加一条跨层一致性断言（测试层可 import domain）：`assert REGION_TYPE_VALUES == {t.value for t in RegionType}`，把同步责任从注释升级为机器校验（schema CHECK 的一致性可一并登记为后续项）。

**R4 [P3]｜`doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md:3, :132, :346`｜契约修订的版本标记与落点不符合所引先例｜**
①状态行仍是「状态：**Frozen for implementation planning**」，无 `版本：1.1`，仅在文末 Revision history 体现——`M2-C1_TYPED_IPC_CONTRACT.md:3-10` 的先例是「状态行带 `版本：1.2` + Revision history 置于**文首**」；Handoff `:72`「参照 M2-C1 格式」属部分成立。②新增条目落在 §4「多目标输入与输出映射」（该节约束对象是 `StepRunInputRef/StepRunOutputRef` 的 DB 结构，`:106-133`），而条目内容是「发给 Provider 的翻译请求载荷」——同节中并列易被后续实现者误读为 `StepRunInputRef` 需要 `region_type` 列。③措辞「并**接受**枚举之外的值 fail-closed 拒绝」语义拗口（应为「枚举之外的值一律 fail-closed 拒绝」）。
**建议（非阻塞）**：状态行补 `版本：1.1（见文末 Revision history）`；把该条改为 §4.1/§9 下的独立子节并明确「端口载荷，非 StepRunInputRef 列」；顺带修措辞。另建议在后续可改 D06 的 Task 中给 `06_TRANSLATION_PIPELINE.md §85` 加一行指针（本刀 D06 不在允许清单，未改是正确的）。

**R5 [P3]｜`src/application/translation/context/step.py:52-55, :135-137`｜`TranslationRequest.region_types` 零消费者，且与 provider 侧口径不一致｜**
全仓 `region_types` 仅「定义 + 填充 + 测试」三处；`execute_translate_step`（`:161`）在 `src/` 无生产调用者，应用层 prompt 路径未接入生产链。该字段是为满足裁决 2③ 字面而新增的 inert 数据，且它覆盖 context 角色 region_id，而真实 provider 载荷（`_build_user_text`）的 context 页不带类型——同一语义在两处口径不同（**非**过度暴露 issue，region 类型非敏感，属 info 口径裂口）。
**建议**：二选一并留痕——(a) 保留则在字段注释写明「当前无生产消费者的预留字段，实际生产传递在 `handlers.py::handle_translate`」；(b) 删除并把 AC4 该条测试改为只锁生产链。若要满足裁决「应用层也带类型」，建议同时给 prompt 行加类型标记，使两处口径一致。

**R6 [P3]｜`src/ports/translation/protocol.py:47-54`｜`RegionInput` 自身无 fail-closed，唯一校验点是聚合对象｜**
`RegionInput` 无 `__post_init__`，`RegionInput("r","t",region_type="bogus")` 可构造成功，只在 `TranslationRequestPayload.__post_init__`（`:87-91`）被拒。AC1 字面「`RegionInput.region_type`（默认 speech+**枚举校验**）+payload 校验」只实现了后半（Owner 已登记，非隐瞒）。当前所有 provider 入口都经 payload（`handlers.py:399`、`mock_local.py:121`、`translation_openai.py:77`），覆盖等价，且错误码 `INVALID_INPUT` 属 `NOT_RETRYABLE_CODES`（`ports/providers/errors.py:140-143, :213-231`）⇒ fail-closed 且不重试，行为正确。
**建议**：在 Task/Handoff 明写「唯一校验点=`TranslationRequestPayload.__post_init__`」，避免后续新增直接消费 `RegionInput` 的路径绕过枚举门。

**R7 [P4]｜Review 锚点（非 Owner 交付物）与 artifact 不一致｜**
artifact 自洽：693 行、13 文件；静态点算 `^\+[^+]`=**408**、`^-[^-]`=**7**（逐行可见，如 `:232` `-regions=[RegionInput(region_id, source_text)]`）。锚点称「+486/-13」。commit 链经 reflog 已核对无误。
**建议**：集成方用 `git diff --shortstat 86ce44b4..00c9de60` 复算并修正锚点数字，以免后续 Review 复用错误基数。

**R8 [P4]｜`translation_openai.py:41-55` 与 `ports/translation/protocol.py:119-121`｜`payload_hash` 不覆盖 system prompt，而本刀同时改了两者｜**
`payload_hash` 只对 `payload_json()` 取摘要；system prompt 是模型输入的实质部分却不在摘要内（本刀 `0c2e746c` 与 `1b7303e7` 的示例词修改即为其例）。D06 §57 的「重试字节一致」在**单个 StepRun 内**成立（`payload` 在 `run_chain` 之前构造并复用，`handlers.py:399/415`），但摘要无法单独标识「模型实际收到什么」。
**建议**：非本刀范围，登记为后续 provenance 增强候选（把 prompt 版本/摘要纳入 `provenance`）。

## NOT_VERIFIED
1. pytest 三套件实跑结果（489+1skipped、providers 327+1sk、core 127、m2_acceptance 35）——间接佐证：`479-127-35=317=providers 基线`，与 Handoff 自洽；未独立执行。
2. `git diff --check 86ce44b4` EXIT=0、禁改面专项 `git diff --stat` 为空、`.rs/.ts/.tsx/.qml/.toml` diff=0——按 artifact 文件清单静态比对通过，未跑 git。
3. cargo/vitest「零需求」——静态可证（diff 无 Rust/TS/QML 文件），但未执行。
4. commit 对象 parentage（`0b43af7a`→`86ce44b4`）——只读 reflog 看不到 release commit 的父链，未解析 git 对象。
5. 真实 LLM 拟声词翻译质量（directional，任务风险①已如实登记；本 Review 不含 GT 验证）。
6. `tests/pipeline`、`tests/knowledge` 全套件在本 tip 的实际通过状态（R2）。

## 集成方闭合清单
- **C1（R2，放行条件）**：冻结 tip 复跑 `pytest tests/pipeline tests/knowledge -q` 并同轮重跑 `tests/providers tests/core tests/m2_acceptance -q`，全部 EXIT=0；日志绑定真实 HEAD 与 venv（`T1.1.1-impl-py312`, `PYTHONPATH=src`）。
- **C2（R1，放行条件）**：修正 `doc/tasks/M2-SFX-SEM-1.md:60/:171` 与 Handoff `:88/:95` 的计数口径为「三套件 +10（489=479+10、327=317+10）+ `tests/knowledge` 单独 1 例」。
- **C3（C 项）**：在集成记录中追认 `handlers.py:401-408` 的「允许清单最小补充」（集成裁决），或按 Handoff `:124` 的回退方案处理；二者择一留痕。
- **C4（R7）**：`git diff --shortstat 86ce44b4..00c9de60` 复算并修正 Review 锚点 ±stat。
- **C5（R6）**：在 Task/Handoff 补一句「region_type 唯一校验点=`TranslationRequestPayload.__post_init__`」。
- **可选（非阻塞）**：R3（加 `REGION_TYPE_VALUES == {t.value for t in RegionType}` 断言）、R4（状态行 `版本：1.1` + 条目落点/措辞）、R5（`region_types` 注释或删除）、R8（登记后续候选）。
- **归档**：本报告落 `verification/M2-SFX-SEM-1/`（按 Handoff `:116` 要求），并在 `doc/STATUS.md` 记 Review 结论；集成方负责 merge（Owner≠Integrator 保持）。

## 推荐下一步
由集成方（代行 Codex）执行 C1/C2/C4/C5 后合并 `agent/zcode/M2-SFX-SEM-1`（C3 追认与可选 R3/R4/R5 可在同一 hygiene 轮落地），并同步 `doc/STATUS.md` 口径。
