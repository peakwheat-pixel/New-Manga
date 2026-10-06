---
task_id: M2-RC4-DOMAIN-COMMANDS
author: Codex Executor (React consumer sub-slice)
recipient: Codex
base_commit: a27b344320af38ea6f17caece0284ac64d4fc672
delivery_head: 6f3544a22cf7e41d9bcbf0a89337ccb6ee26f6b5
status: delivered_awaiting_review
---

# Handoff：M2-RC4-DOMAIN-COMMANDS React Review 修订 6f3544a2

## 交付结果

针对独立 Review `doc/reviews/M2-RC4-DOMAIN-COMMANDS-a27b3443-react-reviewer.md` 的 changes_requested 修订已固定在代码 commit `6f3544a22cf7e41d9bcbf0a89337ccb6ee26f6b5`（`fix(frontend): guard RC-4 image requests`）。分支 `codex/rc4-react-consumer`，worktree `G:/CODEX/New Manga.worktrees/RC4-react-consumer`。此轮代码比较基线为被审 reviewed head `a27b344320af38ea6f17caece0284ac64d4fc672`；提交前包含前一轮 Handoff/log commit `4dd8fa2797f5061333b31474dcccdc6ab2a74cb8`。

仅修改授权 frontend 文件：

- `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx`：所有手工资源图片读取、rerender 预览共用 `imageRequestRef` 版本号；读取同时绑定发起时 page id 和 `pageEpochRef`。切页同步令旧请求失效并清空旧图；rerender 开始时令先前手工读取失效；迟到资源响应不改写当前图片/错误状态，并撤销它自己创建的 object URL。预览读取前同样清空旧图，且使用相同请求版本守卫。Core `preview_error` 对用户统一呈现为冻结安全代码 `PREVIEW_UNAVAILABLE`。
- `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx`：添加真实 JSDOM event interleaving tests、实际非零 PNG bytes 资源读取、typed preview read failure 和 `PREVIEW_UNAVAILABLE` 显示断言。
- `apps/desktop/frontend/src/workbench/RegionInspector.tsx`：移除已过期的“IPC 尚未落地/入口关闭”说明，改为当前撤销时限/资格和历史恢复确认行为。

## Finding disposition

| Finding | 处理 | 代码/验证证据 | 结论 |
|---|---|---|---|
| R-1 P1：切页后旧手工资源读覆盖新页，或迟到手工资源覆盖 rerender preview | 手工和 rerender 图片请求使用统一递增版本号并绑定 page epoch；切页同步作废并清图；旧读到达只 revoke 自己 URL。 | `WorkbenchPage.tsx`；`WorkbenchPage.test.tsx` 中 “drops a manual resource read that completes after switching pages” 与 “keeps the rerender preview when an earlier manual resource read finishes late”。两项新测试在临时反向应用修复代码时均失败，恢复修复后 23/23 focused tests 通过。 | 已修，待 fresh Reviewer 复审。 |
| R-2 P2：size=0 使 preview 不读图片 bytes；错误码不是冻结代码 | Fake invoke 返回 opaque issue URL 和 68-byte 1×1 PNG fixture；FakeCore read 的 `fetch(...?chunk=0)` 返回真实非空 PNG bytes，测试断言 chunk URL、Blob size 和 byte 内容一致。另有 fetch 返回 `REF_EXPIRED` 的 typed channel failure 测试。Core preview publish error 在 UI 固定显示 `PREVIEW_UNAVAILABLE`，不声称 rerender 失败。 | `WorkbenchPage.test.tsx` 主成功点击链及 `shows typed preview resource read failures without reporting render failure`、`keeps preview publication failure separate from committed render failure`；`react-test-fixed-head.log`。 | 已修，待 fresh Reviewer 复审。 |
| R-3 P2：Inspector 长驻文案称撤销/历史未启用 | 文案现在说明撤销需在当前页改标后 10 秒内且无新操作；历史可读，恢复前需确认。 | `RegionInspector.tsx`；主 JSDOM 行为测试对当前说明作文本断言。 | 已修，待 fresh Reviewer 复审。 |

## 验证证据

环境：Windows PowerShell 7.6.6、Node `v24.15.0`、npm `12.0.1`。本轮没有修改依赖，因此未重复 `npm ci`；前一交付 `npm ci` 的成功证据保留在 `react-npm-ci-fixed-head.log`。本轮固定 code HEAD `6f3544a22cf7e41d9bcbf0a89337ccb6ee26f6b5`：

| 检查 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 回归测试红色复现 | 在临时反向应用 `6f3544a2` 的 `WorkbenchPage.tsx` 修复期间运行 `npm test -- src/workbench/WorkbenchPage.test.tsx`，结束后立即恢复修复 | 预期 FAIL，EXIT=1：两条交错 DOM 用例失败（切页后 viewer image 非空；rerender preview URL 从 `blob:rc4-preview-1` 被旧请求改成 `blob:rc4-preview-2`）。此为红色回归探针，不是最终失败状态。 | `verification/M2-RC4-DOMAIN-COMMANDS/raw/react-review-regression-red.log` |
| 交错与 Workbench 定向绿测 | `npm test -- src/workbench/WorkbenchPage.test.tsx` | PASS，23 tests，EXIT=0。红色复现后对同一固定代码 HEAD 再跑一次。 | `react-review-fix-focused-2.log` |
| 全量前端测试 | `npm test` | PASS，11 files / 117 tests，EXIT=0，无 skip。 | `react-review-fix-test-fixed-head.log` |
| TypeScript + production build | `npm run build` | PASS，50 modules transformed，EXIT=0。 | `react-review-fix-build-fixed-head.log` |
| 修订前工作树检查 | 定向 `npm test -- src/workbench/WorkbenchPage.test.tsx` 与 `npm run build` | 分别 PASS 23 tests、PASS；均记录当时 HEAD 与 working-tree 状态。 | `react-review-fix-focused-1.log`、`react-review-fix-build-1.log` |

每次命令各有 raw 日志，并记录 `SHELL`、`NODE`、`NPM`、`HEAD`、`COMMAND`、`EXIT`。所有证据位于 `verification/M2-RC4-DOMAIN-COMMANDS/raw/react-review-*`。红色日志描述临时 reverse-patch 探针并明确 EXIT=1；正式固定代码全量和构建均为 PASS。

仍未运行：Core/SQLite、真实 Rust/stdio、preview grant 生命周期或跨层集成验证；当前 FakeCore/JSDOM 用例只证明 React 发起了 opaque URL chunk read、接收并挂载了非空 fixture bytes，不替代真实 Core 或 WebView 验收。没有新增依赖，未修改 Task/STATUS/PLAN、合同、Core/Rust 或其他 Agent 文件。

## 接收方式

```powershell
Set-Location 'G:/CODEX/New Manga.worktrees/RC4-react-consumer/apps/desktop/frontend'
npm test
npm run build
```

fresh Review 固定 `reviewed_head=6f3544a22cf7e41d9bcbf0a89337ccb6ee26f6b5`；需要核对三条 finding 的修复及本 Handoff 对红/绿结果的描述。DeepSeek Harness 最终复审前仍以此 head 为准，若修订代码须重新固定新 head 并重跑受影响测试。

## 下一任务建议（必填）

- Task ID / 标题：`M2-RC4-DOMAIN-COMMANDS` — React changes_requested fresh Review 与 DeepSeek 最终复审。
- 推荐 Agent / Reviewer：先由 Codex 指派非作者 fresh Reviewer 复核 `6f3544a2`；finding disposition 确认后由 DeepSeek Harness 执行最终独立复审。
- 推荐原因与前置依赖：前一 review 的 R-1/R-2/R-3 已分别返修并有测试证据；必须固定新 head 检查，不可复用 `a27b3443` 上的结论。父 Task AC5 仍要求独立 Review 和集成 Gate。
- Recovery point：仓库 `G:/CODEX/New Manga`；实现 branch/worktree `codex/rc4-react-consumer` / `G:/CODEX/New Manga.worktrees/RC4-react-consumer`；Review base `a27b344320af38ea6f17caece0284ac64d4fc672`，当前 code head `6f3544a22cf7e41d9bcbf0a89337ccb6ee26f6b5`；fresh Reviewer worktree 待 Codex 创建。
- 允许修改路径：审查时只读 frontend 代码、测试、冻结契约、Task 和本 Handoff；Review 产物仅写 `doc/handoffs/M2-RC4-DOMAIN-COMMANDS*` / `verification/M2-RC4-DOMAIN-COMMANDS/**`。
- 禁止范围与新增授权条件：不得改 React/Core/Rust/契约/共享依赖/Task/STATUS/PLAN，不得合并 main；任何新 finding 交回实现 Owner/Codex 处理。Review 通过也不自动等于 AC5 或 Task done。
- 交付物：fresh Reviewer 和 DeepSeek Harness 各自固定 head 的 Review 结果、findings disposition、逐次验证日志及明确的整体跨层未验证项。
- 验证命令、环境与完成 Gate：在独立 worktree 查看 `a27b3443..6f3544a2` React diff，运行 `npm test`、`npm run build`；逐次保存含 `SHELL/NODE/HEAD/COMMAND/EXIT` 的证据。随后由 DeepSeek Harness 对同一新 head 进行最终复审。Codex 核对两份 Review 与当前 head 后才决定集成 Gate。
- 可直接转发给 Agent 的指令：请独立复审 RC-4 React 子面固定 head `6f3544a22cf7e41d9bcbf0a89337ccb6ee26f6b5`（branch `codex/rc4-react-consumer`，worktree `G:/CODEX/New Manga.worktrees/RC4-react-consumer`，Review base `a27b344320af38ea6f17caece0284ac64d4fc672`）。逐项复核原报告 R-1/R-2/R-3：异步资源请求跨页与 rerender 的统一版本/epoch guard、迟到 object URL revoke、非零 PNG bytes 经 resource channel chunk 读取、typed fetch 错误与 `PREVIEW_UNAVAILABLE`、Inspector 当前撤销/历史说明；查看真实 JSDOM 交错点击测试与 red/green raw 日志。运行 `npm test`、`npm run build` 并逐次保存 `SHELL/NODE/HEAD/COMMAND/EXIT`；只写独立 Review/verification，不改生产代码、契约、Task/STATUS/PLAN，不合并。交付 findings/限制给 Codex；之后由 DeepSeek Harness 对新 head 最终复审。

## 风险与遗留

此交付只收敛 React 层 Review findings；Core preview 发布、真实 sidecar、Rust ACL、opaque grant expire/revoke 与 Core save/render success 仍待整体任务的 owner/integrator 验证。manual resource ID 是现有诊断输入面，切页会清空当前图像并令当前读取失效；用户可重新触发后续读取。全量前端在本 head 是 117 tests，早一 head 上的 114 tests 结果不适用于新代码。Review 状态仍为 `changes_requested`，fresh Review 和 DeepSeek 最终复审尚待运行。
