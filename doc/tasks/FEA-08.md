---
id: FEA-08
title: Source/回收站隔离原型（H4/H5/H6 能力矩阵与技术报告）
kind: prototype
governance_version: 3
status: proposed
approval: 待独立 scope Review 冻结（scope-r1）；D-15 推荐先于 FEA-09
suggested_owner: codex
owner: codex
reviewer: 待 scope Review + impl Review appointment
depends_on:
  - FEA-00
  - FEA-01
base_commit: e36a7442bd5f704252e4b0af8c63ab4f790000e1
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-08
allowed_paths:
  - doc/tasks/FEA-08.md
  - doc/research/FEA-08-*.md
  - doc/handoffs/FEA-08-*.md
  - doc/reviews/FEA-08-*.md
  - verification/FEA-08/**
---

# FEA-08：Source/回收站隔离原型

> 草案来源：workspace `G:\CODEX\New Manga.workspace\FEA-08\FEA-08-scope-draft.md`（DSH 起草，2026-11-03）；本卡在独立 scope Review 冻结前为 `proposed`，不得实施。
> 依据：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` S3 FEA-08 行与 H4/H5/H6 表、`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`、`doc/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`；`G-CONTRACT` 已 CLOSED（2026-11-01）。

## 目标（原型，不产出生产实现）
在隔离环境（synthetic 非真实资料、临时卷/目录）验证并交付：
- **H4 稳定源 lease**：读取期间检测外部替换/重命名/删除/断连/共享写；同一已验证句柄一致读取并计算 digest；不能保证时明确返回 unavailable。覆盖 NTFS 本地；USB 可移动如可用；SMB/网络盘以 mock/受限报告。
- **H5 Windows 回收站**：IFileOperation/SHFileOperation 在临时树上移至回收站；失败/取消/部分失败/中断时**不得永久删除**；receipt/日志；负向原型。
- **H6 精确页面匹配**：PDF 重生成、ZIP/CBZ 重编码/重复名、GIF/色彩/方向、加密格式 golden fixtures 可行性；无法唯一匹配只给候选。
- 交付：能力矩阵（PASS/LIMITED/UNAVAILABLE + 证据/失败分支）、技术报告、可复现原型/脚本、依赖与许可说明。

## OUT
- 生产 Source/导入实现、Host `SourceAccessRegistry`/grant、Core schema/DB、UI 集成（FEA-09+）。
- 真实用户文件/真实库/AppData 写入；改变文件系统或回收站设置。
- 无证据的 PASS；覆盖所有卷/格式的承诺。

## BLOCKED / 限制登记
- 无硬件的卷类型/云盘行为：LIMITED/UNAVAILABLE，交产品裁决。
- H6 新格式：登记候选策略，不扩大自动匹配。

## 验收（待 scope Review 冻结）
- [ ] AC-1（H4 原型）：正常读取 digest 一致；外部替换/删除被检测；不可保证返回 unavailable；命令/EXIT/证据哈希。 <<PARTIAL: 待实施>>
- [ ] AC-2（H5 负向原型）：失败/取消/部分失败/模拟中断路径证明不永久删除；receipt/日志；不触真实用户数据。 <<PARTIAL: 待实施>>
- [ ] AC-3（H6 golden fixtures）：匹配/候选结果报告；无法唯一匹配列入候选清单。 <<PARTIAL: 待实施>>
- [ ] AC-4（交付完整）：能力矩阵+技术报告+可复现命令+依赖/许可；无生产代码改动。 <<PARTIAL: 待实施>>

## 交付与证据
- 原型/脚本：`G:\CODEX\New Manga.workspace\FEA-08\`（非 Git；Task 记录路径与 hash）。
- 报告：`doc/research/FEA-08-source-capability.md`；证据：`verification/FEA-08/**`；Handoff：`doc/handoffs/FEA-08-*.md`。

## 待 scope Review 决定
1. 是否允许原型触碰隔离的测试 SQLite（建议否；纯文件系统级）。
2. USB/SMB 无硬件时接受 mock/受限结论（建议接受并标 LIMITED）。
3. H6 是否引入 Python 依赖（建议仅标准库 + 已有 Pillow/zipfile；新依赖需许可记录）。
