---
id: M2-REGION-OVERLAP-ARBITRATION
title: "region 创建跨 provider 重叠仲裁（裁决③授权：sfx/speech 检出并存时改标/抑制语义，闭合误路由乱译损害的结构性缺口）"
kind: feature
status: in_progress
approval: user_ruling_2026-10-04_按推荐_裁决3_重叠仲裁契约授权
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-DETECT-DOMAIN-EXT-DIAG, M2-SFX-PROD-1]
base_commit: eb7cd15e
branch: agent/zcode/M2-REGION-OVERLAP-ARBITRATION
worktree: G:/CODEX/New Manga.worktrees/M2-REGION-OVERLAP-ARBITRATION-zcode
integration_commit: null
owner_claim: 2026-10-03T16:27:36Z
delivery_head: b27c826f
---

# M2-REGION-OVERLAP-ARBITRATION：region 创建跨 provider 重叠仲裁

## 来源与目标

- 来源：[M2-SFX-DETECT-DOMAIN-EXT-DIAG](M2-SFX-DETECT-DOMAIN-EXT-DIAG.md) 结构性发现（report §4/§5，DSH 双链 review 确认）——region 创建**无跨 provider 重叠仲裁**：①`detection_sfx.py:599-601` `result.candidates + sfx_candidates` 直接拼接；②`handlers.py:286-298` 逐候选 `region_creator` 无重叠检查；③`core_assembly.py:1013-1049` `_create_detected_region` 按 `sfx-` 前缀分发类型。后果：**仅恢复 SFX 召回不闭合误路由损害**——SFX 被判 text/speech 后仍进对话链乱译进渲染成品（BJ13 region#1「哎呀——」/region#3「Ｗｉｆｉｘ」实证）。
- 目标：在 detect→region 创建链上增加**确定性重叠仲裁语义**：当 SFX provider 候选与主检测器（ogkalu text/speech 类）候选空间重叠超过冻结阈值时，按冻结规则改标/抑制，使被误路由的 SFX 形态落入 `RegionType.SFX` → 既有 SfxPolicy 门（默认 SKIP）自动接管。可观察交付：BJ13 误路由 case 在全链 rerun 中不再产生 speech 乱译渲染（进 sfx 门 SKIP 或标记），域内/KO 行为零变化。

## Acceptance Criteria

- [ ] AC1 仲裁语义提案与证据定案：仲裁层位（provider 拼接层 vs region 创建层，Owner 侦察后提案并说明理由）、重叠度量（IoU/包含率）、阈值与优先级规则（sfx 覆盖 text 改标 / 双向保留标记 / 抑制——按 BJ13/14/15+BJ06 既有 raw 数据证据定案，directional）。提案与数据依据写入设计段并经 DSH review 确认。
- [ ] AC2 红绿判别（核心验收）：BJ13 误路由 case（region#1/#3 的 text 0.744/0.844 与 sfx 疑似框重叠形态）在仲裁后红转绿——原 SPEECH 乱译路径不再发生（进 SfxPolicy 门）；BJ15 结构性无载体形态（无 text/bubble 载体）如实登记为仲裁不可达（不伪造覆盖）。
- [ ] AC3 零变化回归：BJ06 域内 8 sfx region 逐位不变；KO 既有 qualification case 检测 region 计数与全链产物零变化；三套件基线不回退。
- [ ] AC4 边界与 fail-closed：阈值/规则可配置项（env，沿 TILING `NEWMANGA_DETECTOR_TILING_*` 先例）空/非法值 typed 拒绝；默认值冻结并记录依据；仲裁不可达形态 typed 可诊断。
- [ ] AC5 契约边界：预期零 IPC wire 变化（仲裁在 core 内部 detect 链）；若实现中触碰 RegionInput/provider 契约或 M2-C1 wire shape，**立即停等**并登记契约修订请求（沿 SEM-1 rev 1.1 / SETTINGS-IPC rev 1.3 先例），不得擅自 widening。

## 允许修改范围

- `src/infrastructure/providers/detection_sfx.py`（拼接/仲裁）、`src/infrastructure/providers/handlers.py`（若层位提案落此处）、`src/bootstrap/core_assembly.py`（装配/env 配置）、对应 `tests/`；
- `doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md`、`verification/M2-REGION-OVERLAP-ARBITRATION/**`、`doc/handoffs/M2-REGION-OVERLAP-ARBITRATION-*.md`；
- experiments 下证据脚本（只读 import 生产代码）。

## 禁止范围

- `doc/contracts/**`（触契约即停）、`doc/STATUS.md`、`packaging/**`、`apps/**`、前端；
- SFX OCR/重绘、检测模型/权重更换（域外根因不属本 Task）、UI 改标交互（另见 M2-SFX-MISROUTE-UI-MITIGATION）；
- 既有 qualification raw 证据改写（只读引用）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 误路由红转绿 | `arbitrate_bj13.py`：BJ13 页 ogkalu+chiqui7 真实 rerun（红态）+ 合成召回恢复口径（口径 A 不可达诊断 / 口径 B 近重复改标闭环）+ 生产分发函数逐候选判定 | dev venv（M2-TA3-B-ocr）+ 权重（ogkalu @M2-DOCTR-QUAL-C4 pin 校验通过、chiqui7 @M2-SFX-DETECT） | PASS（红态真实对位 region#1/#3；口径 B relabels=3 全落 RegionType.SFX；口径 A/BJ13 现状/BJ14/BJ15 不可达如实登记不伪造） | `verification/M2-REGION-OVERLAP-ARBITRATION/raw/{arbitrate-pages,arbitrate-manifest}.json`、`raw/arbitrate-run.log` |
| AC3 域内零变化 | BJ06 composite 仲裁 off vs on 候选逐位对照 + 与 qual-BJ06 基线对位 | 同上 | PASS（off/on 17=17 bit-identical=True；rerun 17=qual 17（9 speech+8 sfx）；域内最高 IoU 0.8865<0.90；BJ13/14/15 计数 4/6/7 对位） | `raw/bj06-on-off-candidates.json`、`raw/arbitrate-manifest.json`（bj06_zero_change） |
| AC3 套件基线 | `T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs`（cargo/vitest 零改动面，集成方复跑） | T1.1.1-impl-py312（依赖矩阵全齐，无 CUDA） | PASS（627 passed + 1 skipped, 0 failed, EXIT=0；基线 611+1sk + 本 Task 16 新用例 = 628 精确吻合；全量 tests/ 1731+1sk + 1 个本地素材计数环境性失败与本 Task 零交集） | `raw/pytest-three-suites.log`、`raw/pytest-full-suite.log`、环境对照 `raw/pytest-t111-py312.log` |
| AC4 env 校验 | 7 组参数化（两 env 空串/未知词/非数字/0/1.5/负数）+「primary 未被调用」探针（先红后绿） | dev venv | PASS（14 仲裁测试实现前全红 EXIT=1，实现后转绿） | `raw/red-phase-arbitration-tests.log`；`tests/providers/test_detection_sfx.py` 仲裁段 |

## 依赖、风险与阻塞

- depends_on：M2-SFX-DETECT-DOMAIN-EXT-DIAG（done，证据与裁决输入）、M2-SFX-PROD-1（done，SFX provider 现状）。
- 风险：①仲裁阈值过激→真对白被改标为 sfx 被 SKIP（precision 损害）——以 BJ06+KO 对照回归与阈值证据控；②单向改标 vs 保留+标记的语义取舍影响 UI 缓解 Task 的数据基础——AC1 提案时须与 [M2-SFX-MISROUTE-UI-MITIGATION](M2-SFX-MISROUTE-UI-MITIGATION.md) 的设计假设对齐（在该 Task 文件预留接口注记，不阻塞）。
- 精度权衡已由用户裁决语境接受：误路由乱译损害优先于理论 precision 损失（有 SfxPolicy SKIP 与未来 UI 改标兜底）。

## 交付与运行记录

- Handoff：[M2-REGION-OVERLAP-ARBITRATION-b27c826f](../handoffs/M2-REGION-OVERLAP-ARBITRATION-b27c826f.md)（待 Review）
- Review：尚无。
- 集成：尚无。

### 交付记录（Owner=ZCode，2026-10-03，@b27c826f）

- **AC1 提案定案**：层位=provider 拼接层（`MangaSfxParallelDetectionProvider.detect` 拼接前，两端候选只在此层同时可见、零契约面、降级路径天然隔离）；度量=bbox IoU（与上游证据同口径）；规则=sfx 候选驱动的 directional 改标 `sfx-arb-<原label>`（复用 `startswith("sfx-")` 分发契约 → RegionType.SFX → SfxPolicy 门，core_assembly 零改动）；冻结阈值 **0.90**；env `NEWMANGA_SFX_ARBITRATION`（on|off）/`NEWMANGA_SFX_ARBITRATION_IOU`（(0,1]）typed 拒绝沿 TILING 先例。
- **结构性定案（Review 必读）**：纯几何重叠在域内对照与误路由 case 间**反向不可分离**——BJ06 域内 sfx×speech 最高 IoU **0.8862/0.8865**（「！！！」双检出对）> BJ13 误路由 **0.4902/0.5501**；「误路由高、域内低」分离前提不成立，任何捕获 BJ13 的阈值必先改标 BJ06 真对白（违反 AC3）。0.90 = 域内最高之上的保守域（语义=近重复双检出的类型仲裁），BJ13 现状闭合依赖 sfx 召回恢复（域外根因另行 Task），不可达面已按 AC4 typed 诊断（`sfx_arbitration_partial_overlap`）如实登记。
- **AC2 红绿**：BJ13 真实 rerun 红态对位（manga-1/manga-3 = qual region#1/#3 乱译路径；现状 sfx 仅 T 恤印花且零相交=第一层不可达）；口径 B（近重复双检出，0.90 域设计目标形态）relabels=3 全部落 RegionType.SFX（绿态闭环）；口径 A（参照框=召回恢复）partial 0.5501 诊断不迁移（诚实不可达）；BJ14（sfx=0 + 0.123/0.4287 双层不可达）、BJ15（与全部 ogkalu 候选零相交=结构性无载体）如实登记。
- **AC3**：BJ06 off/on 逐位一致（17=17）+ qual 基线对位（17 region、9 speech+8 sfx）；三套件 **627+1sk EXIT=0**（+16 恰为本 Task 新用例）；cargo/vitest 零改动面。
- **AC5**：`doc/contracts/**`、RegionInput wire、`region_creator` 签名、分发矩阵逻辑零改动——**未触发停等**。
- **UI-MITIGATION 对齐注记（Task 风险②）**：本仲裁只产生确定态改标，不新增 region 级「疑似」字段（零契约面）；「改标前疑似警示」所需 region 级信号本 Task 无产出（不可达形态仅 detect options 审计字段），UI 侧若需属未来契约修订候选。建议 Codex 将本注记转写入 M2-SFX-MISROUTE-UI-MITIGATION Task 文件（他人 Task 产物，本 Task 不直接改写）。
- 证据：[arbitration-report.md](../../verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md) + `raw/` 全量落盘。
