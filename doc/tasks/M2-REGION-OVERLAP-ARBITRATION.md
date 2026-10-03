---
id: M2-REGION-OVERLAP-ARBITRATION
title: "region 创建跨 provider 重叠仲裁（裁决③授权：sfx/speech 检出并存时改标/抑制语义，闭合误路由乱译损害的结构性缺口）"
kind: feature
status: ready
approval: user_ruling_2026-10-04_按推荐_裁决3_重叠仲裁契约授权
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-DETECT-DOMAIN-EXT-DIAG, M2-SFX-PROD-1]
base_commit: null
branch: agent/zcode/M2-REGION-OVERLAP-ARBITRATION
worktree: G:/CODEX/New Manga.worktrees/M2-REGION-OVERLAP-ARBITRATION-zcode
integration_commit: null
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
| AC2 误路由红转绿 | planned：BJ13 页 detect→region 创建 rerun，断言原乱译 region 进 SfxPolicy 门 | dev venv + 权重（task-envs/M2-SFX-DETECT） | NOT_RUN | 无 |
| AC3 域内零变化 | planned：BJ06 detect region 集合逐位对照 | 同上 | NOT_RUN | 无 |
| AC3 套件基线 | planned：pytest 三套件 / cargo / vitest | dev venv | NOT_RUN | 无 |
| AC4 env 校验 | planned：空/非法 env typed 拒绝用例（先红后绿） | dev venv | NOT_RUN | 无 |

## 依赖、风险与阻塞

- depends_on：M2-SFX-DETECT-DOMAIN-EXT-DIAG（done，证据与裁决输入）、M2-SFX-PROD-1（done，SFX provider 现状）。
- 风险：①仲裁阈值过激→真对白被改标为 sfx 被 SKIP（precision 损害）——以 BJ06+KO 对照回归与阈值证据控；②单向改标 vs 保留+标记的语义取舍影响 UI 缓解 Task 的数据基础——AC1 提案时须与 [M2-SFX-MISROUTE-UI-MITIGATION](M2-SFX-MISROUTE-UI-MITIGATION.md) 的设计假设对齐（在该 Task 文件预留接口注记，不阻塞）。
- 精度权衡已由用户裁决语境接受：误路由乱译损害优先于理论 precision 损失（有 SfxPolicy SKIP 与未来 UI 改标兜底）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 集成：尚无。
