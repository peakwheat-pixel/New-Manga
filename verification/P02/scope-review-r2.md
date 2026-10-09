# P02 范围契约独立复核 r2

- Timestamp：2026-10-09T03:06:42Z
- Reviewer：`/root/p02_scope_review`（独立于 Codex 契约作者）
- Worktree：`G:/CODEX/New Manga.worktrees/P02-harness-scope`
- Branch：`codex/P02-harness-scope`
- Baseline HEAD：`241ff3b70b6fc0490ea238efd486cc707f849031`
- Git common directory：`G:/CODEX/New Manga/.git`
- Reviewed artifact：未提交的 `doc/tasks/P02.md`
- Reviewed artifact SHA-256：`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- r1 报告 SHA-256：`1E62ECCE51E72D24AE44AB16AC30E4A2255666554DAC00DE790E3EE5CB3DFC40`
- Decision：`approved`
- 新增 Findings：P0/P1/P2/P3 = 0/0/0/0

本轮仅复核 Codex 对 r1 的契约修订及相关范围回归。批准适用于上述 SHA-256 的范围草案，不是后续实现的正式 DeepSeek Harness Review，不证明产品验收通过，也不自行将 Task 释放为 ready 或置为 done。

## r1 Findings 处置

| Finding | 原级别 | 证据与复核场景 | 独立处置 |
|---|---|---|---|
| P02-SCOPE-R1-01 | P2 | `doc/tasks/P02.md:41` 明确要求真实 WebView、默认双 300ms 下分别判别 retype/undo/restore；将任一不能安全或可靠执行的情况设为 BLOCKED，并明确阻止 done、不得以 NOT_RUN 满足 AC4。模拟 Core/IPC 仍须标明边界。复核“只有 retype 已执行，undo/restore 未执行”情形：该文字不能满足 AC4 或关闭任务。 | closed；无需追加修订 |
| P02-SCOPE-R1-02 | P2 | `doc/tasks/P02.md:43` 将 token_mapping 与 contrast_result 分列；实际前景和合成背景可确定时强制计算，不因 UNMAPPED 或 CSS fallback 跳过。复核“fallback 颜色已解析且背景确定”情形：仍必须记录 ratio 并作 PASS/FAIL 判定；只有背景无法确定时才可 NOT_VERIFIABLE 且须附原因。 | closed；无需追加修订 |
| P02-SCOPE-R1-03 | P3 | `doc/tasks/P02.md:51` 明确授权不纳入提交的 frontend/dist 与 task-local cargo-target 输出，要求记录既有状态并保护来源不明内容；`:59` 保留生产源码、依赖及既有发布产物禁写；`:65` 将 Cargo 输出改为 task-local CARGO_TARGET_DIR。复核“fresh frontend build + root 下 Cargo build”情形：输出位于明确授权生成目录，不要求修改生产源码或配置。 | closed；无需追加修订 |

## 来源与范围回归检查

- `doc/tasks/P02.md:25,38,55,59` 仍区分真实嵌入式 Tauri/WebView2、真实 WebView 的 mock IPC/Core 以及普通浏览器/JSDOM；没有把 mock 结果升级为真实 Core 持久化证据。
- `doc/tasks/P02.md:40-41` 仍区分页面读取 quiet-period 与写成功后的即时读回。`WorkbenchPage.tsx:85` 的默认值、`:366,423` 的读取 timer、`:655,690,738` 的写后 refreshRegions 直调支持该事实描述。
- 对比度阈值及状态不能只依赖颜色的要求仍来自 `doc/contracts/UI_UX_GUI_DESIGN.md` §7.2、§9；文本 4.5:1、禁用文字/非文本 3.0:1 未被改动。未将 F token 目标冒充当前 React 已实现。
- `doc/tasks/P02.md:42` 保留当前 Workbench 的键盘与焦点操作范围，没有扩成全应用 WCAG 审计。
- `doc/tasks/P02.md:50-51,55,59` 保留合成数据隔离、用户库/人工编辑/Lock/current/pinned/凭据保护，新增依赖仍须 scope delta；未授权产品 UI、token、键盘或 debounce 修复。
- `frontend/package.json:8`、`vite.config.ts:9` 与 `src-tauri/tauri.conf.json:7` 仍以 frontend/dist 为构建嵌入来源。Owner 应在 frontend 目录执行 npm 命令、在工作树根目录设置相对 CARGO_TARGET_DIR 并执行 Cargo；实际 runner 必须记录 cwd、命令与输出路径。这里只核对现有配置，不改配置。

未发现新的 material finding；从本轮契约审查角度，没有阻止 Codex 登记 ready 的未关闭 finding。

## Verification 与局限

实际执行了 Git HEAD/branch/common-dir/status、两个审查输入 SHA-256、修订文件逐行读取及相关现有源码/配置/契约读取。审查前工作树只有未提交的 P02 Task 与 verification/P02 内容。Reviewer 仅新增本报告，不修改 Task、代码、依赖、配置或其他证据。

构建、Vitest、真实 WebView2 驱动/鼠标键盘/时序/颜色采样均 NOT_RUN。本轮没有证明 harness 实际可用，也没有验证 Core/SQLite 持久化。后续环境或驱动不可用仍按 Task 记录 BLOCKED；AC4 任一必要操作未执行不能 done。

## 推荐下一步

由 Codex 固定并登记本 SHA-256 对应的 P02 release metadata，更新 Plan/Status 后创建 Task 指定的 ZCode worktree，再派发 Owner；非作者实现 Reviewer 保持 DeepSeek Harness。本报告不构成对 Task 后续任意修订的自动批准。具体实施指令以正式释放后的 Task、实际 base/head 和恢复点为准，不在此生成或提前启动新的产品 Task。

可转发给 Codex：在 `G:/CODEX/New Manga.worktrees/P02-harness-scope`、`codex/P02-harness-scope@241ff3b70b6fc0490ea238efd486cc707f849031`，核对 P02 文件 SHA-256 与本报告一致后，串行完成治理文档登记和 release commit；保留生产源码/依赖/数据只读，保护主工作区既存未提交内容。随后按正式 Task 创建并核对 ZCode Owner worktree，派发 AC1–AC7 验证，记录真实/Mock 边界及所有命令、环境、Hash、EXIT 和 blocker；不得用本范围 approved 替代实现 Review 或产品 PASS。

未检查实际构建与 GUI；风险是运行环境和驱动仍需 Owner 在正式任务内实证。
