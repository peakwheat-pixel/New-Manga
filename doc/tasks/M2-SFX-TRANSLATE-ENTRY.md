---
id: M2-SFX-TRANSLATE-ENTRY
title: "SFX→translate 产品入口：sfx_policy 可配置化（用户裁决④：解除 SFX 翻译评测 n=0 的前置阻断）"
kind: feature
status: ready
approval: user_ruling_2026-10-01_all_four
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-PROD-1, M2-SFX-SEM-1, M2-TA3-B2]
base_commit: 8e0de8d0
branch: agent/zcode/M2-SFX-TRANSLATE-ENTRY
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-TRANSLATE-ENTRY-zcode
---

# M2-SFX-TRANSLATE-ENTRY：SFX 翻译策略可配置入口

## 背景（TA3-B2 发现 + 用户裁决④）

生产链 SFX region 的 `sfx_policy` 恒为默认 SKIP（`domain/tasks/models.py:186` 默认值；region 创建时无配置覆盖入口），翻译门 `decide_sfx_translation` 的 translate 放行路径（SFX-SEM-1 已实现）生产不可达——TA3-B2 的 9 个 SFX region 全部 SKIP、SFX 翻译评测 n=0。用户裁决：做 SFX→translate 产品入口（策略可配置）。

## 交付（AC）

1. **AC1 配置通道**：`sfx_policy` 从 provider/pipeline 设置读取（复用既有 settings/profile 通道，如 detect provider binding 或 pipeline_defaults 的一个键，具体落点 Owner 按 M2-SFX-PROD-1 的装配结构定并留痕），默认仍 **SKIP**（行为零变化），可配置为 translate/manual。
2. **AC2 装配与消费**：detect 装配把策略传到 region 创建/翻译门消费点（`decide_sfx_translation` 已支持三值，验收其生产接线）；非法值 fail-fast（沿用 SFX conf 阈值 env 校验先例）。
3. **AC3 测试**：先红后绿——默认 SKIP 零变化（既有测试不动）；配置 translate 后 SFX region 进入翻译（handler 端到端 1 条：SFX region 译文落库）；非法值装配 fail-fast；mock 链探针（m2_acceptance 不受扰动的确认）。
4. **AC4 文档**：TASK-002 契约如涉及（策略键语义）则按契约修订流程登记（contracts 在禁改面时以 Handoff 登记移交集成方）；Handoff 登记设置键名与取值域。

## 允许修改面 / 禁改面

允许：`src/`（detect/translate 装配+settings 读取的最小面，Owner 提案后落笔——预期 `core_assembly.py` SFX 装配段+models 默认值不动）、`tests/**`（SFX 相关）、`experiments/M2-SFX-TRANSLATE-ENTRY/**`、`verification/M2-SFX-TRANSLATE-ENTRY/**`、Task/Handoff。
禁改：`src/ports/**`（协议 widening 已完成不重开）、`doc/contracts/**`（如需修订先在 Handoff 登记）、`packaging/**`、`apps/**`、`doc/STATUS.md`、chiqui7/ogkalu provider 检测语义。

## 纪律

- 默认行为零变化（SKIP）；precision-first 裁决不变（配置是用户显式选择，不是默认放开）。
- 基线不回退：main 509+1skipped 0 failed；GATE/闭包不涉及（无新依赖）。
