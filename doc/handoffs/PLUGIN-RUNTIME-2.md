---
task_id: PLUGIN-RUNTIME-2
author: Codex
recipient: reviewer-settings-a
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
delivery_head: 2ea97edd6e65260d1276e7b1e505a036dc612f80
status: delivered
---

# Handoff：PLUGIN-RUNTIME-2

## 交付结果

初始实现 050530dfb；r2 空覆盖修复，r3 approved；r1 changes_requested（verification/PLUGIN-RUNTIME-2/review-r1.md）；修复 head 2ea97edd6e65260d1276e7b1e505a036dc612f80。before_export 现先于 job/history 快照，TEXT 内容按最终选项延迟生成，Hook 幂等只执行一次。真实 StartExport 与恢复历史一致性测试已通过。

生产 Core 共用一个 PluginService：detect/ocr 在 provider request 生成后调用 before，export 在校验/写盘前调用 before；after 只传 JSON 摘要且丢弃返回。
可写输入：detect options、ocr script/direction/options、export format_options。拒绝未知字段及非法值，plugin_error 审计后用原输入继续；身份/源图/路径/锁与 Revision 不可覆盖。沿用 nm-plugin-hook/1；无新增 IPC/UI/Schema/依赖。
子进程 -I 忽略环境编码设置，现入口强制 UTF-8，以保证中文 OCR payload 正确往返。

## 验证证据

| AC/场景 | 实际命令 | 环境与被测 commit | 结果 | 日志 |
|---|---|---|---|---|
| AC1/AC2 | `python -m pytest tests/providers/test_handlers_pipeline.py tests/infrastructure/test_plugin_runtime.py tests/core/test_core_plugin_wire.py tests/reading_export/test_export.py tests/core/test_p16_reader_export.py -q --tb=short --basetemp="G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/run9"` | Windows Python 3.14，PYTHONUTF8=1，2ea97edd6e65260d1276e7b1e505a036dc612f80 同实现 | 103 passed / 0 skipped | verification/PLUGIN-RUNTIME-2/pytest-r3.log |
| AC3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 当前治理指针 | PASS（3 warnings） | 最终交付复跑 |

Run 测试含真实 SQLite + 真实插件子进程，模型 provider 使用 fake，不代表模型质量。detect 测试直接调用真实 Handler；export 测试实际写 ZIP 并检查压缩选项生效。未运行 GUI、全量 pytest 或打包，因无前端/IPC/打包变化。

## 接收方式

仓库 G:/CODEX/New Manga，branch main，共享 .git，固定 delivery_head 如上。未跟踪的六个 verification/P04 诊断文件未纳入提交。没有执行 push/merge/reset/stash，没有清理任何资源。

## 下一任务建议

- Task ID / 标题：PLUGIN-RUNTIME-2 Codex 集成记录与 closeout（当前 Task 收口，无新产品 Task）。
- 推荐 Agent：Codex（Lead/Integrator）；Reviewer：reviewer-settings-a r3 已 approved。
- 前置依赖：r3 接受固定 head 2ea97edd6e65260d1276e7b1e505a036dc612f80，103 passed；无生产改动待审。
- Recovery point：G:/CODEX/New Manga，main，base d28b7a8b1449e5f4790470bcbbba10abcf3ab388，head 2ea97edd6e65260d1276e7b1e505a036dc612f80。
- 允许修改路径：当前 Task、STATUS、LEDGER、REBASELINE、Handoff 和本 Task evidence。
- 禁止范围：新增产品行为、IPC/UI/Schema、资源清理；禁止 push/merge/reset/stash。
- 交付物：integration_commit、资源逐项保留裁定、done 状态与最终治理结果。
- 验证与 Gate：核对 source 与已审 head 一致，证据 pin 完整，check.ps1 PASS，STATUS ≤3200 字节。
- 可直接转发指令：请 Codex 以 head 2ea97edd6e65260d1276e7b1e505a036dc612f80 和独立 r3 approved 为恢复点，核对已提交的103项测试证据，完成 PLUGIN-RUNTIME-2 集成记录与资源 closeout；只做治理收口，不改变生产实现，不删除资源，不执行 push/merge/reset/stash。无已授权新产品 Task，收口后无需下一步操作。

## 风险与遗留

继承 trusted-code 边界，非 OS 沙箱；stdin 上限和进程树终止沿用前期限制。独立 r3 approved（verification/PLUGIN-RUNTIME-2/review-r3.md），Task approved，待 Codex 正式 closeout，不视作 done。没有授权新产品实现 Task。
