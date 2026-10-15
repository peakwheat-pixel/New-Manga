---
task_id: P02-MAINLINE-INTEGRATION
author: Codex
recipient: Codex / 用户
base_commit: a9c3214b2d7806c2b8920897e5684c039ae14057
delivery_head: 7a6ff57527a3872e0e3caebb3620182d60e61c6a
status: complete
---

# Handoff：P02 主线集成与限定收口

## 交付结果

已审 9e3c5310 通过原生 FF 合入 main；7a6ff575 固定主线报告、保护证据与治理关闭文档；5ccceb7c 固定 11 文件 immutable manifest。本 Handoff/Task pins 为后续 E 文档提交，不包含自己的 commit hash。变更范围仅 doc/STATUS、Plan、Task/索引/Handoff 与 verification/P02-MAINLINE-INTEGRATION/**；产品/依赖/原始 Review 均未改。

| AC/场景 | 实际命令/步骤 | 环境/被测提交 | 结果 | 证据 |
|---|---|---|---|---|
| 已审成果进主线 | git merge --ff-only --no-autostash | Windows main a9c3214b → 9e3c5310 | exit 0 | verification/P02-MAINLINE-INTEGRATION/result/fast-forward-preservation.json |
| 本地内容保护 | 两组 fixture assertions + 实际 38 文件 SHA/字节核验 | 同名冲突 index-only 对齐 approved blob，不提交用户内容 | PASS，index empty | 同上 |
| 主线已有 pins | official generate-evidence-manifest.py --verify | main source/Gate capsule | 102/102、19/19 PASS | result/source-pins-on-main.json、gate-pins-on-main.json |
| 本轮 immutable evidence | 同一 official helper，source=7a6ff575 | 11 文件，排除 mutable Task/STATUS/Plan | 11/11 PASS | freeze/mainline-evidence-manifest.json |
| 生命周期 | pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P02-MAINLINE-INTEGRATION.md | 当前主 checkout | PASS | workspace agent-output/codex/P02-MAINLINE-INTEGRATION/ |

## 接收方式与下一步

仓库 G:/CODEX/New Manga，branch main；已审源 head=9e3c5310；关闭文档基线=7a6ff575；固定证据清单=5ccceb7c。最终主线 head 由 rolling checkpoint / git rev-parse main 记录。原始备份、输出及 fixture 保留，禁止按本 Handoff 擅自清理。
当前无其它已释放 READY；无需下一步操作。不创建产品 P3/P4 或 Git 修复占位 Task。

## 风险与遗留

P02 总入口 closed_with_limitations；AC1–AC7/AC6 resolution DONE。旧 H1/P2-1/13 项缺失、BC-AC5 PARTIAL、产品 Escape/token/theme backlog 保持原样；不是产品全面 PASS。Git autocrlf 对新文件的表示差异已证明 EOL-only 后恢复 canonical bytes，首次 FAIL 证据保留。旧坏 ref 未清理；未 push、未重跑 GUI/Build，无资源删除。
