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

## 集成与关闭

2026-10-23 用户授权后 Codex 完成收口，integration_commit=eb5e821f3798b4d411ddbd60cd52db65208a2812；source/tests 与 r3 已审实现一致。集成复跑 111 passed / 0 skipped，证据 verification/PLUGIN-RUNTIME-2/integration-pytest.log；资源逐文件指纹和原位保留裁定见 resource-manifest.json，完整记录见 closeout.md。Task done，两项 closeout 状态 complete，无资源删除/迁移/归档。

## 下一任务建议

无需下一步操作：Plan 无 READY；沙箱未授权，签名仍待证书/发布签核，不创建或派发新 Task。

## 风险与遗留

继承 trusted-code 边界，非 OS 沙箱；stdin 上限和进程树终止沿用前期限制。独立 r3 approved（verification/PLUGIN-RUNTIME-2/review-r3.md），Task done，Codex 已完成集成与资源 closeout。没有授权新产品实现 Task。
