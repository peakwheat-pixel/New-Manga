---
id: VERIFY-RECHECK-1
title: Mica/4K@200%/Esc-H 三项复测补证（REPACK-4 补证）
kind: verification
governance_version: 3
status: done
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: core-admin-rca
owner: core-admin-rca
reviewer: dsh
depends_on: []
base_commit: caa0fdda8
branch: task/VERIFY-RECHECK-1
worktree: null
integration_commit: cabdd7a28
delivery_head: c00e32dd2
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/VERIFY-RECHECK-1
allowed_paths:
  - verification/VERIFY-RECHECK-1/**
  - doc/tasks/VERIFY-RECHECK-1.md

# VERIFY-RECHECK-1：三项复测补证

- [x] **AC1 Mica** <<MET: 非回归——遮挡时 100s 仍 None；主窗可见后全新启动约 35s actual=Mica（四角壁纸透色）；MICA-FIX-1 在回退祖先链上，4be1c3f4f 未丢修复>>
- [x] **AC2 4K@200%** <<PARTIAL: 环境阻塞——Mi TV 3840×2160 物理连接但不被系统识别为输出；DisplaySwitch/Win+P 均无效；未伪报 DPI；无系统变更无需还原>>
- [x] **AC3 Esc/H** <<MET: 聚焦沉浸窗后 H→HUD 消失（sha F6CE7968→FDED931F）；Esc→回阅读器（窗口数 2，sha 392E1E10）>>

## Review（DSH，2026-10-28）— PASS

仅补证、未重打包、未改源码；证据 erification/VERIFY-RECHECK-1/**。4K 遗留：需 Mi TV 被识别为可用输出后另测。
