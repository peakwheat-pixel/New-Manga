---
id: M2-REGION-RETYPE-CORE
title: "Region 改标 Core 实现：SetRegionType 全链+11 断言落测+协议 minor bump+旁路同步（T5b；按 rev 1.4 冻结契约）"
kind: feature
status: ready
approval: user_ruling_2026-10-04_释放T1b_T5b_T5c
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-REGION-RETYPE-CONTRACT]
base_commit: 69321db7
branch: agent/zcode/M2-REGION-RETYPE-CORE
worktree: G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CORE-zcode
integration_commit: null
---

# M2-REGION-RETYPE-CORE：Region 改标 Core 实现（T5b）

## 来源与目标

按已冻结的 M2-C1 rev 1.4 契约（T5a done）实现 `set_region_type` 全链 runtime。**范围纪律：只做 Core/Rust/测试三层，前端接通归 Workbench UI 实现 Task（blocked 不在本 Task）**。沿 SETTINGS-IPC 先例（命令面变更=协议 minor bump+packaging 门旁路同步）。

## Acceptance Criteria

- [ ] AC1 Core 层：`editing/service.py` 新增 retype 写路径（经 commit seam 新 revision、origin=user、review_state=UNREVIEWED 不触发需校对、policy 快照按 EV-8 裁决重快照——sfx 方向按改标时全局配置/非 sfx 强制 SKIP）；`core_service.py` 注册 `set_region_type` 命令（wire=rev 1.4 §5.4：请求 region_id/new_region_type/expected_revision?→响应 revision_no+生效态；错误语义零新增逐码复用）。
- [ ] AC2 Rust 层：production command+allowlist 三视图+envelope 挂接（production-only，沿 settings 两命令先例）；DTO 与 wire 逐字段一致。
- [ ] AC3 11 条断言落测：C1-C7（人工优先写通道不互斥/AI 侧 Revision+Lock 双守卫 fail-closed/乐观期望显式拒绝/改标后决策生效/机器笔人工叠加/目标缺失/page_id 语义）+P1-P4（重开持久/重检测幂等复用不回滚人工改标/撤销完整恢复/撤销后再改标幂等）——**两层覆盖**（service guard 返回+管线候选持久化，T5a P3-6 要求），先红后绿。
- [ ] AC4 读取面：`list_regions` 按 rev 1.4 返回 RegionListSummary（若实现为扩容既有命令则按契约取舍得案）——T5c 导出器与本 Task 消费同一读取面。
- [ ] AC5 协议 minor 2→3+旁路同步：PROTOCOL_MINOR 更新、frozen-probe/EXPECTED 计数/CS-L1 envelope minor 沿 SETTINGS-IPC 登记口径同步；**M2-AC5 GATE 25/25 重跑 PASS**。
- [ ] AC6 回归：三套件基线不回退（pytest 三套件 627+1sk 口径+cargo+vitest）；m2_acceptance 35 passed。

## 允许修改范围

`src/application/editing/service.py`、`src/bootstrap/core_service.py`、`src/interface/**`（handler 注册）、`src-tauri/src/**`（command/allowlist）、对应 `tests/**`、协议常量文件（PROTOCOL_MINOR）、Task/Handoff/`verification/M2-REGION-RETYPE-CORE/**`。

## 禁止范围

`doc/contracts/**`（rev 1.4 已冻结，实现中发现契约缺口=停等登记，不得改契约）、`apps/**` 前端、`packaging/**`（GATE 跑但不改 spec）、`doc/STATUS.md`、既有设计稿。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC3 11 断言 | pytest 新增（先红后绿） | dev venv | NOT_RUN | 无 |
| AC5 GATE | M2-AC5 GATE 25/25 | build_sidecar | NOT_RUN | 无 |
| AC6 回归 | 三套件+m2_acceptance | dev venv | NOT_RUN | 无 |

## 依赖、风险与阻塞

depends_on=M2-REGION-RETYPE-CONTRACT（done）。与 T5c 并行（写范围零冲突：本 Task src/src-tauri/tests，T5c experiments）；集成串行 T5b→T5c。风险：实现中发现契约语义缺口→停等登记（不得擅自改契约或实现）；GATE 重跑需 sidecar 构建时间。

## 交付与运行记录

- Handoff：尚无。Review：尚无。
