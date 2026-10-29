---
id: V11R-C-RESEARCH-1
title: 主题框架参考研究（SukiUI/FluentAvalonia/Semi.Avalonia/PleasantUI/Avalonia）
kind: research
governance_version: 2
status: in_progress
approval: approved_by_lead_2026-10-30
suggested_owner: codex
owner: codex
reviewer: dsh
depends_on: [V11R-BASELINE-1]
base_commit: c73239999
branch: v11r/theme-research
worktree: (doc-only, lead merges)
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/V11R-C-RESEARCH-1
allowed_paths:
  - doc/design/theming/
  - verification/V11R-C-RESEARCH-1/
---

# V11R-C-RESEARCH-1：主题框架参考研究

## 目标
按用户工作流 C1，研究并审查 5 个上游项目，产出可执行的架构/许可证/维护成本结论，作为新 Theme Engine 设计的决策依据。

## 必读上游
SukiUI、FluentAvalonia、Semi.Avalonia、PleasantUI、Avalonia（主题/资源系统）。

## Acceptance Criteria
- [ ] AC1 `doc/design/theming/RESEARCH_V1.md`：逐项目记录版本、许可证（精确 SPDX + 义务）、主题架构（令牌/资源/变体/动态切换机制）、视觉表现、控件一致性、个性化能力、维护活跃度（近 12 月提交/发布/issue 响应）、Avalonia 11.3.x 兼容性、与 GPL-3.0 分发的兼容结论。
- [ ] AC2 对比矩阵 + 明确建议：可借鉴什么、可复用哪些（许可证允许时）、**禁止简单拼装**的理由与边界。
- [ ] AC3 给出与新 `NewManga.ThemeEngine` 契约（`doc/plan/V11R_AVALONIA_CONTRACT.md` §4）的映射建议：哪些机制可直接采用、哪些必须自研。
- [ ] AC4 结论必须可被验证：每条事实附 URL/版本/日期；无法核实的标 UNVERIFIED。
- [ ] AC5 不修改任何生产代码；不引入依赖。

## 交付与运行记录
- Handoff：尚无。
