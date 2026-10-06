---
task_id: M2-RC4-DOMAIN-COMMANDS
author: Codex Executor (React consumer sub-slice)
recipient: Codex
base_commit: 0fba60796c83a3039a260c5790353976bc891dd7
delivery_head: a27b344320af38ea6f17caece0284ac64d4fc672
status: delivered_awaiting_review
---

# Handoff：M2-RC4-DOMAIN-COMMANDS React 子面 a27b3443

## 交付结果

固定实现提交：`a27b344320af38ea6f17caece0284ac64d4fc672`（`feat(frontend): consume RC-4 commands`）。分支 `codex/rc4-react-consumer`，worktree `G:/CODEX/New Manga.worktrees/RC4-react-consumer`；实际起始 HEAD 为 `0fba60796c83a3039a260c5790353976bc891dd7`。

变更限定在授权 React consumer/UI 和测试依赖范围：

- `apps/desktop/frontend/src/region/{types.ts,client.ts,client.test.ts}`：增加 frozen DTO 和 `listRegionRevisions`、`restoreRegionRevision`、`rerenderPage` 三个 typed client 方法，Tauri invoke 参数使用 camelCase，并对返回形状及 Core 错误做显式处理。
- `apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts`：锁定生产命令面没有扩入 probe/AC1 命令。
- `apps/desktop/frontend/src/workbench/{RegionInspector.tsx,ViewerPanel.tsx,WorkbenchPage.tsx,relabelMachine.ts,WorkbenchPage.test.tsx}`：恢复历史列表/预览/明确确认目标；撤销保存原 suspect、原 revision、改标结果 expected revision 和 10 秒过期时间，使用 guarded restore 并刷新 Core 权威列表；切页/新操作/过期令撤销失效并隔离迟到响应；rerender 使用既有 `loadPageImageUrl` 发布 preview，preview 发布错误明确显示为预览不可用而不谎报 render 失败。
- `apps/desktop/frontend/package.json` 与 lock：只增加已批准的测试依赖 `jsdom@26.1.0`、`@types/jsdom@21.1.7`。无生产依赖，无全局 Vitest 配置调整，现有 `mockDom` 未修改。

显式历史恢复确认显示目标 revision 和恢复后的文本、类型、策略、锁状态，并说明恢复可能回退当前 Lock。Undo 是 10 秒的 guarded revision restore，不调用反向 `set_region_type`；新操作、切页和超时会取消撤销资格。渲染提交成功但 preview 发布失败时保留成功结果，单独提示 preview unavailable。

按 Task AC 对照：

- AC1：React 三命令 client 与 allowlist/command-surface 测试在本子面完成；Core、stdio、Tauri Rust production allowlist/ACL 不属于本交付，尚待整体集成验证。
- AC2：React 显式历史恢复确认和客户端消费已完成；Core 快照/Lock/事务语义不在本子面验收。
- AC3：React rerender 与 opaque preview resource 的既有资源通道消费已接通；真实 Core/headless 图像与持久化证据不在本子面验收。
- AC4：React 三入口、undo、历史确认、busy/切页/过期/迟到结果与错误可见性已有真实 DOM 事件测试。整体 AC4 仍需和 Core/Tauri 集成后验证。
- AC5：本 Handoff 和逐次 raw 日志已交付；独立 Review、集成及集成后回归仍未运行，因此本 Task 未完成。

## 验证证据

环境为 Windows PowerShell 7.6.6、Node `v24.15.0`、npm `12.0.1`。固定代码 HEAD 上重新完成：

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 锁文件安装 | `cd apps/desktop/frontend && npm ci` | PowerShell, Node v24.15.0, `a27b344320af38ea6f17caece0284ac64d4fc672` | PASS, EXIT=0；npm 报告 7 项 audit vulnerabilities，未在此子面归因 | `verification/M2-RC4-DOMAIN-COMMANDS/raw/react-npm-ci-fixed-head.log` |
| 全量前端测试 | `cd apps/desktop/frontend && npm test` | 同上 | PASS, 11 files / 114 tests | `verification/M2-RC4-DOMAIN-COMMANDS/raw/react-test-fixed-head.log` |
| 生产构建 | `cd apps/desktop/frontend && npm run build` | 同上 | PASS, TypeScript 与 Vite production build | `verification/M2-RC4-DOMAIN-COMMANDS/raw/react-build-fixed-head.log` |
| 实际 DOM 点击链 | `npm test` 中创建并清理 jsdom；向实际按钮分发 `MouseEvent`/`input` 事件 | 同上；`WorkbenchPage.test.tsx` | PASS：实际点击改标→10 秒 guarded undo→历史目标确认并恢复→preview 获取；另测 typed retype failure、undo 到期、切页撤销失效和迟到结果隔离、preview publish failure 与 render success 分离 | `react-test-fixed-head.log`；场景位于 `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx` 的 `RC-4 Workbench actual DOM actions` |
| Client/allowlist 定向验证 | 前期 focused Vitest runs | 初始 HEAD `0fba60796c83a3039a260c5790353976bc891dd7` + 当时工作树改动 | 最后一轮 45/45 PASS；早期迭代失败均在固定 HEAD 全测前已修正 | `react-focused-1.log` 至 `react-focused-5.log` |

所有安装、focused test、全量 test、build 轮次均保留在 `verification/M2-RC4-DOMAIN-COMMANDS/raw/react-*`，包含 shell、Node、HEAD、命令和退出码。早期失败轮次保留作开发证据：根仓库目录没有 npm lockfile，误从根目录执行的 `npm ci` EXIT=1，随后在 frontend 正确执行成功；实现迭代中也曾出现重复 prop、漏导入 `useState`、SVG 点击方式及一项陈旧页断言问题，已修复并由固定 HEAD 的全量 114 tests/build 覆盖。npm install 输出提示 `esbuild@0.21.5` install script 被 npm policy 阻止，但 `npm ci`、TypeScript 与 Vite build 均成功。

未运行：Core/SQLite/render/preview 真环境、Rust bridge/ACL、真实 sidecar、跨层持久化/资源读取和全仓 Python/Rust 回归。这些由相应实现 Owner 与 Codex 集成 Gate 验证，不能从 jsdom/mock client 结果推断为通过。

## 接收方式

```powershell
Set-Location 'G:/CODEX/New Manga.worktrees/RC4-react-consumer/apps/desktop/frontend'
npm ci
npm test
npm run build
```

审查目标固定为 `a27b344320af38ea6f17caece0284ac64d4fc672`。测试用例在每个相关 test 内创建和关闭 jsdom，不依赖浏览器安装或新增全局 test setup。渲染预览通过既有 opaque `resource_id`/`loadPageImageUrl` 消费链读取，不把路径或 bytes 暴露给 WebView。

## 下一任务建议（必填）

- Task ID / 标题：`M2-RC4-DOMAIN-COMMANDS` — React consumer/UI 子面独立 Review。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者独立 Reviewer）。
- 推荐原因与前置依赖：本子面已固定代码 head，测试和 Handoff 均提交；父 Task 指定 DeepSeek Harness。Reviewer 应核对冻结契约、完整 diff、真实 DOM 点击覆盖、数据保护/失败状态，并将 React 子面结论与 Core/Tauri 的整体完成状态分开记录。
- Recovery point：仓库 `G:/CODEX/New Manga`；实现 branch/worktree `codex/rc4-react-consumer` / `G:/CODEX/New Manga.worktrees/RC4-react-consumer`；`base_commit=0fba60796c83a3039a260c5790353976bc891dd7`，`head=a27b344320af38ea6f17caece0284ac64d4fc672`。独立 Reviewer worktree：待 Codex 创建。
- 允许修改路径：Review 只读本分支代码、测试、冻结契约和本 Handoff；报告仅写 `doc/handoffs/M2-RC4-DOMAIN-COMMANDS*` 与 `verification/M2-RC4-DOMAIN-COMMANDS/**` 中 Review 产物。
- 禁止范围与新增授权条件：不改 React/Core/Rust/契约/Task/STATUS/PLAN/共享依赖，不合并 main，不替代 Codex 集成；发现需要修改时报告 finding 并交实现 Owner/Codex。Review 和 Gate 完成前不得标记 Task done。
- 交付物：固定 reviewed head 的独立 Review 报告、findings disposition（含无发现时覆盖范围/限制）、Review 实际命令及逐次日志。
- 验证命令、环境与完成 Gate：Reviewer 在独立 worktree 对固定 head 检查完整 diff，运行 `cd apps/desktop/frontend && npm ci`、`npm test`、`npm run build`；记录 PowerShell、Node、HEAD、COMMAND、EXIT，修正任何阻断再复审。Gate 是 DeepSeek 报告完成并由 Codex 核对，不自动等于 AC5 或 Task done。
- 可直接转发给 Agent 的指令：请作为非作者 Reviewer，独立审查 `G:/CODEX/New Manga.worktrees/RC4-react-consumer` 的 `codex/rc4-react-consumer`，固定 `base_commit=0fba60796c83a3039a260c5790353976bc891dd7`、`reviewed_head=a27b344320af38ea6f17caece0284ac64d4fc672`。对照 `doc/tasks/M2-RC4-DOMAIN-COMMANDS.md` 与 `doc/contracts/M2-RC4_DOMAIN_COMMANDS.md`，检查完整 React diff、真实 DOM 事件用例、busy/失败/过期/切页/陈旧响应保护和 resource channel 消费。使用独立 worktree，只写 Review 报告及 `verification/M2-RC4-DOMAIN-COMMANDS/**` 证据，不改产品代码、Core/Rust/契约/Task/STATUS/PLAN，不合并。运行 `npm ci`、`npm test`、`npm run build`，逐次保存带 SHELL/NODE/HEAD/COMMAND/EXIT 的日志；报告 findings、复现、范围和未验证的跨层边界，交 Codex 集成 Gate。

## 风险与遗留

本提交只证明 React 消费/UI 行为与测试，不证明 Python Core、Rust ACL、真实渲染或真实 preview resource grant 的端到端成功。跨层 integration 应校验 camelCase Tauri 参数映射、DTO 形状、Core typed errors、`PREVIEW_UNAVAILABLE`、切换 revision 后旧 grant 的失效以及 resource channel 的读取生命周期。npm audit 在安装输出中报告 7 项漏洞（3 moderate、2 high、2 critical）；本子面没有判断其是否为新增或是否可达。npm 安装策略阻止 `esbuild@0.21.5` postinstall，当前 `npm run build` 仍成功。代码回退可通过不集成本 delivery commit 实现；无用户数据迁移。
