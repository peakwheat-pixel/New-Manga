---
task_id: PLUGIN-RUNTIME-2
author: Codex
recipient: reviewer-settings-a
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
delivery_head: 55af609b0cbb4d7dc29160df150b116989b3b0be
status: delivered
---

# Handoff：PLUGIN-RUNTIME-2

## 交付结果

初始实现 050530dfb；r1 changes_requested（verification/PLUGIN-RUNTIME-2/review-r1.md）；修复 head 55af609b0cbb4d7dc29160df150b116989b3b0be。before_export 现先于 job/history 快照，TEXT 内容按最终选项延迟生成，Hook 幂等只执行一次。真实 StartExport 与恢复历史一致性测试已通过。

生产 Core 共用一个 PluginService：detect/ocr 在 provider request 生成后调用 before，export 在校验/写盘前调用 before；after 只传 JSON 摘要且丢弃返回。
可写输入：detect options、ocr script/direction/options、export format_options。拒绝未知字段及非法值，plugin_error 审计后用原输入继续；身份/源图/路径/锁与 Revision 不可覆盖。沿用 nm-plugin-hook/1；无新增 IPC/UI/Schema/依赖。
子进程 -I 忽略环境编码设置，现入口强制 UTF-8，以保证中文 OCR payload 正确往返。

## 验证证据

| AC/场景 | 实际命令 | 环境与被测 commit | 结果 | 日志 |
|---|---|---|---|---|
| AC1/AC2 | `python -m pytest tests/providers/test_handlers_pipeline.py tests/infrastructure/test_plugin_runtime.py tests/core/test_core_plugin_wire.py tests/reading_export/test_export.py tests/core/test_p16_reader_export.py -q --tb=short --basetemp="G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/run8"` | Windows Python 3.14，PYTHONUTF8=1，55af609b0cbb4d7dc29160df150b116989b3b0be 同实现 | 102 passed / 0 skipped | verification/PLUGIN-RUNTIME-2/pytest-r2.log |
| AC3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 当前治理指针 | PASS（3 warnings） | 最终交付复跑 |

Run 测试含真实 SQLite + 真实插件子进程，模型 provider 使用 fake，不代表模型质量。detect 测试直接调用真实 Handler；export 测试实际写 ZIP 并检查压缩选项生效。未运行 GUI、全量 pytest 或打包，因无前端/IPC/打包变化。

## 接收方式

仓库 G:/CODEX/New Manga，branch main，共享 .git，固定 delivery_head 如上。未跟踪的六个 verification/P04 诊断文件未纳入提交。没有执行 push/merge/reset/stash，没有清理任何资源。

## 下一任务建议

- Task ID / 标题：PLUGIN-RUNTIME-2 独立 Review（当前 Task 的审查阶段）。
- 推荐 Agent / Reviewer：reviewer-settings-a（已派发独立 Reviewer 子代理）。
- 前置依赖：固定实现提交、102 项测试通过；审查不授权集成或产品扩展。
- Recovery point：G:/CODEX/New Manga，main，base d28b7a8b1449e5f4790470bcbbba10abcf3ab388，head 55af609b0cbb4d7dc29160df150b116989b3b0be；不新增 worktree。
- 允许修改路径：verification/PLUGIN-RUNTIME-2/review-r2.md。
- 禁止范围：生产代码、UI/IPC、Schema、用户文件；禁止 push/merge/reset/stash。
- 交付物：绑定精确 base/head 的独立 Review，标明 approved/changes_requested。
- 验证命令：上述 pytest（改用独立 review temp）、治理 check；Gate 为独审无 blocker 后 Codex 才可处置集成/closeout。
- 可直接转发指令：请独立审查 PLUGIN-RUNTIME-2，比较 base d28b7a8b1449e5f4790470bcbbba10abcf3ab388 与 head 55af609b0cbb4d7dc29160df150b116989b3b0be，核对三个真实入口、覆盖输入/只读 after、关闭零调用、超时崩溃审计继续；只写 verification/PLUGIN-RUNTIME-2/review-r2.md，不改生产代码、不自行关闭 Task。

## 风险与遗留

继承 trusted-code 边界，非 OS 沙箱；stdin 上限和进程树终止沿用前期限制。独立审查尚未返回，Task 保持 in_review，不视作 done。没有授权新产品实现 Task。
