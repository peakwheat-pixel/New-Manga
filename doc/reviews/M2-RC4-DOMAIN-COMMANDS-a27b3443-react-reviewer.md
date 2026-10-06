---
task_id: M2-RC4-DOMAIN-COMMANDS
reviewer: Codex non-author React reviewer
author: Codex Executor
base_commit: 0fba60796c83a3039a260c5790353976bc891dd7
reviewed_head: a27b344320af38ea6f17caece0284ac64d4fc672
decision: changes_requested
---

# RC-4 React 消费面独立 Review

范围：只读审查 `0fba6079..a27b3443` 的 11 个 frontend 变更及其现有调用链；依据 `doc/tasks/M2-RC4-DOMAIN-COMMANDS.md` AC4/AC5、`doc/contracts/M2-RC4_DOMAIN_COMMANDS.md@300b4007` §应用与 UI 约束 4–6、`doc/09_COLLABORATION.md` §6。被审 worktree 为 `G:/CODEX/New Manga.worktrees/RC4-react-consumer`，HEAD 与固定 reviewed head 一致，Git common directory 为主仓库 `.git`。未修改被审源码，未运行依赖安装。主线 Core/Rust 及最终集成不在本次批准范围。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 证据与建议 | 状态 |
|---|---|---|---|---|---|
| R-1 | P1 | `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:263-304,328-359,572-583` | 用户在 A 页输入手工 `resource_id`，其 `loadPageImageUrl` 尚未结束时切到 B 页：资源 effect 仅依赖 `resourceId/resourceRevision`，切页不取消它；完成后仍执行 `replaceImageUrl(url)`，B 页展示 A 的图。另一顺序是手工资源请求晚于 A 页 `rerender_page` 预览完成：晚到的 effect 清空 `previewPageIdRef` 并覆盖新预览，导致反馈称已加载新 revision，画面却是旧资源。 | 静态确定性调用顺序；现有 `operationIsCurrent` 仅保护 rerender 分支，不保护手工资源 effect。把图像读取与 page epoch / 当前预览请求关联，切页取消并清空旧图；晚到响应只 revoke 自己的 URL。补交错 DOM 用例。 |
| R-2 | P2 | `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx:179-191,492-500,563-585` | 预览“读取成功”测试返回 `size: 0`，`ResourceChannelClient.fetchAll` 因零 chunk 从不请求图片字节；断言仅见 mock `blob:` URL。预览失败测试又返回非冻结字面量 `PREVIEW_PUBLISH_FAILED`，未断言 `PREVIEW_UNAVAILABLE`。因此 114 tests 通过仍不能证明实际预览读取或固定安全错误呈现。 | `apps/desktop/frontend/src/resourceChannel/client.ts:81-93` 的零字节分支。用非零 PNG bytes 模拟至少一个 chunk，并分别覆盖 typed fetch failure 和冻结 `PREVIEW_UNAVAILABLE`；记录可判别日志。 |
| R-3 | P2 | `apps/desktop/frontend/src/workbench/RegionInspector.tsx:121-128` | 选中区域后，常驻说明仍称“撤销入口待 Core restore IPC 命令面、历史入口待 ListRegionRevisions 命令面各自落地后启用（当前 UI 通道均未开通）”，但同页已启用撤销和历史。用户会得到与当前可操作状态矛盾的信息。 | 更新该句为当前入口及 10 秒/资格条件；无需新 UI 抽象。 |

三入口成功路径的 JSDOM 点击测试真实执行；`restore_region_revision` 的 undo/历史拒绝、`rerender_page` 拒绝与页面预览交错没有同等 DOM 断言，按关键路径验证缺口记录，不把源码实现推断为失败。历史确认文案已明确文字、类型、策略、Lock 回退；undo 发送改标前 revision 和返回的 expected revision，且不反向调用 `set_region_type`。新请求/过期失效和 Core 刷新路径在源码中存在。

## Architecture

**PASS（限 React 消费面）**：新增三命令经 `RegionClient` / Tauri invoke；组件不直连 DB、OS 路径或模型。预览走既有 `loadPageImageUrl`，未看到 managed path/base64 下发。R-1 是页面图像状态归属问题；R-3 是错误用户文案。Core/Rust/持久化整体架构为 **NOT_RUN / 未审**，不能据此作 RC-4 整体批准。

## Verification

环境：PowerShell 7.6.6；Node `E:/Program Files/nodejs/node.exe` v24.15.0；npm `E:/Program Files/nodejs/npm.ps1`；worktree `G:/CODEX/New Manga.worktrees/RC4-react-consumer/apps/desktop/frontend`；HEAD `a27b344320af38ea6f17caece0284ac64d4fc672`。本节为 Reviewer 本次实际运行，非作者日志。

| 检查 | 命令 | 结果 | 运行输出 |
|---|---|---|---|
| 前端测试 | `npm test` | **PASS，EXIT=0** | [Reviewer 原始输出](../../verification/M2-RC4-DOMAIN-COMMANDS/integration/reviewer-react-a27b3443-npm-test.log)：Vitest v2.1.9；11 files passed，114 tests passed；无 skip。 |
| 前端构建 | `npm run build` | **PASS，EXIT=0** | [Reviewer 原始输出](../../verification/M2-RC4-DOMAIN-COMMANDS/integration/reviewer-react-a27b3443-npm-build.log)：`tsc && vite build`；50 modules transformed，built in 488ms。 |
| diff 空白检查 | `git diff --check 0fba60796c83a3039a260c5790353976bc891dd7 a27b344320af38ea6f17caece0284ac64d4fc672` | **PASS，EXIT=0** | [Reviewer 原始输出](../../verification/M2-RC4-DOMAIN-COMMANDS/integration/reviewer-react-a27b3443-diff-check.log)：无 diff 输出。 |
| 完整 preview bytes、三入口拒绝、跨页图像交错 DOM 判别 | 当前测试中未覆盖 | **NOT_RUN** | R-1/R-2；不能从 114 passed 推断。 |
| Core SQLite、stdio、Rust ACL、preview grant/revoke、集成后回归 | 不属于本 reviewer 分配范围 | **NOT_RUN** | 需各自证据和最终独立 Review。 |

一次错误命令 `npm test -- --runInBand` 在同一环境返回 **EXIT=1**，Vitest 报 `Unknown option --runInBand`（[Reviewer 原始输出](../../verification/M2-RC4-DOMAIN-COMMANDS/integration/reviewer-react-a27b3443-runinband-error.log)）；随后按仓库脚本运行 `npm test` 得到上表结果。该命令错误不计为产品测试失败。

**Verification 结论：PARTIAL。** AC4 中图像跨页隔离与真实预览读取未充分验证，R-1 仍 open；此 reviewed head 不建议集成。返修后固定新 head 复审。下一步由 RC-4 React 实现 Owner 在原 worktree 修 R-1/R-3、补 R-2 与三入口失败/交错 DOM 断言，提交新 head 和逐次 EXIT 日志，再交非作者 Reviewer；主线集成 Gate 仍由 Codex 独立执行。
