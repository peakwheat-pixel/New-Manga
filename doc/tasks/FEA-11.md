---
id: FEA-11
title: Source 变化 / 重定位 / 同步（scan/diff/plan + 页映射/tombstone + 共享引用 relink）
kind: implementation
governance_version: 3
status: proposed
approval: 待独立 scope review（DSH Appointment 前不释放实施）；依赖 FEA-09/FEA-10 done
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-09
  - FEA-10
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11
allowed_paths:
  - doc/tasks/FEA-11.md
  - doc/reviews/FEA-11-*.md
  - doc/handoffs/FEA-11-*.md
  - verification/FEA-11/**
  - src/application/sources/**
  - tests/fea11/**
out_of_scope:
  - FEA-12 删除/回收站；FEA-13 备份/迁移；FEA-14 子项
  - 冻结契约字节（C-05/C-08/C-13/C-15/C-16/FEA-01）、共享组合根
  - 真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11：Source 变化 / 重定位 / 同步

状态：**proposed**；范围矩阵与写域待独立 scope review 后由 DSH 冻结；不释放实施。

## 目标

按 [FEA-00 提案](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §8.1–§8.4、§12.1（S3）、§15.5/A10：实现 Source scan → diff → plan → 用户预览/确认 → 事务发布新 binding；支持单项/共享引用 relink、页映射与 tombstone。全部先预览、歧义默认待确认、stale plan 零写、其他项目不被误改、旧 binding/源字节保留。

## 依赖

- FEA-09（done：referenced source 基础、`source_versions/source_entries/page_bindings` 表、SourceReadService/lease）。
- FEA-10（done：Prepare/Accept 两阶段、durable receipt、candidate-only 安全）。
- 冻结契约：C-15 v1.1、C-05 v1.2、C-13（SC-D07/08）；**新增 `source_sync_plans`/`source_operations` 表的名称/索引/约束/迁移版本须先由 DSH 冻结**。

## AC 草案（待 scope review 冻结）

- AC11-1 变化检测四路（启动/访问前、操作前强验证、后台扫描、watcher dirty hint）；通知非唯一真值；mtime/size 未变不作内容未变证明；强验证=稳定 lease+digest。
- AC11-2 scan/diff/plan：目录新增/缺失/变化先列数量与明细；diff 分类（未变/新增/缺失/变化/歧义）；plan 记录基础 versions/generation/diff/映射/用户决定/digest。
- AC11-3 页匹配：精确未变独立图片强 digest；文件夹成员身份+digest；容器成员内容/规范解码像素 digest+尺寸/方向+唯一性；PDF/重编码先页级精确匹配，感知 hash/OCR 仅候选；重复 occurrence 不合并。
- AC11-4 预览与确认：歧义/未知/一对多默认需确认；确认前再变更→stale plan 拒绝且零写；预览=应用同一 plan digest。
- AC11-5 同步应用：未变唯一对应页保留 PageId/人工版本/进度；新增页新 PageId；缺失页 tombstone（保留问题与人工修改，不连带删除）；变化页新 binding generation、旧区域留旧 lineage；手动迁移区域新 revision 并记录映射来源。
- AC11-6 重定位/共享引用：预览共享引用；仅当前/全部由用户选择；仅当前分支必需 binding，不改其他项目 accepted version；容器内容已变不能只改路径标健康。
- AC11-7 缺失/无备份：原文件不在且无备份时保留元数据/人工修改并诚实显示缺失；不伪造旧版本。
- AC11-8 operation journal/幂等：operationId 幂等；失败保留 receipt；未达双方确认的 binding 不可读；重启按 Host registry generation 核对。
- AC11-9 真实链路与回归：Core scan/diff/plan/sync 真实 IPC；Host 授权/预览/确认链路；既有 managed 读路径/命令不回归；pytest/.NET 全量不减少。
- AC11-10 范围/冻结/证据：冻结契约与 FEA-08/09/10 closeout 未改；范围 diff 合规；独立 Review；DSH 集成；Handoff+EV+Resource Manifest。

## 待 DSH 裁决（建卡/scope review）

1. 新表 `source_sync_plans`/`source_operations` 最终 schema 与迁移版本（v8）。
2. 是否新增 wire 命令（SourceScan/SourcePlan/SourceApply/SourceRelink）及 M2-C1 minor/错误码；若新增须先独立 PREREQ 子卡。
3. Host registry generation 的持久化/核对落点（Host vs Core journal 分工）。
4. `src/application/sources/` 与既有 `src/infrastructure/resource_channel/` 职责边界。
5. AC11-1 的后台扫描调度是否本 Task 或后续小卡（建议首版只做前三路 + dirty hint 消费）。

## 验证矩阵（草案）

| AC | 测试/命令 | 隔离环境 | 证据 |
|---|---|---|---|
| 变化检测/scan/diff | `tests/fea11/test_source_scan.py`；`python -m pytest tests/fea11 -q` | `workspace/FEA-11/fixtures/<case>/` | `verification/FEA-11/logs/` |
| 页匹配/重复 occurrence | `tests/fea11/test_source_match.py` | 同上 | 同上 |
| plan 预览/stale 零写 | `tests/fea11/test_source_plan.py` | 同上 | 同上 |
| 同步应用/tombstone/新 binding | `tests/fea11/test_source_sync.py` | 同上 | 同上 |
| 重定位共享引用 | `tests/fea11/test_source_relink.py` | 同上 | 同上 |
| operation journal/幂等/重启 | `tests/fea11/test_source_operation.py` | 同上 | 同上 |
| 真实 IPC/回归 | `Fea11SourceIpcTests.cs` + 全量 .NET/pytest | 同上 | 同上 |
| 范围/冻结 | check.ps1、verify_pins.ps1、git diff | 主树 | EV+Handoff |

## Closeout Record

- 未开始（proposed；待 scope review + DSH Appointment）。
