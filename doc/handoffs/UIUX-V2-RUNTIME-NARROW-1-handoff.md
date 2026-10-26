---
task_id: UIUX-V2-RUNTIME-NARROW-1
author: ZCode
recipient: DeepSeek Harness
base_commit: 7020dc591
delivery_head: null
status: delivered
---

# Handoff：UIUX-V2-RUNTIME-NARROW-1

> delivery_head 留 null 的原因：本 Task 全部交付（代码 + 证据 + 文档）合入**单一
> commit**，该 commit 即 `git log -1`（Handoff 与代码同提交，hash 无法自引用）。
> 集成方复核时以 `doc/tasks/UIUX-V2-RUNTIME-NARROW-1.md` frontmatter 与 git log 为准。

## 交付结果

修复 900×700（DPR 2）窄窗横向溢出：根因是 `src/ui/ui.css` 中 `.nm-app` 的
`min-width: 1024px` 把运行时根盒强制撑到 1024（实测四页全部
`documentElement.scrollWidth=1024 / clientWidth=900`）。删除该 min-width，
并为书架网格新增 `<1024px` 自适应列断点（消除库区内部横滚）；
S10 的 KNOWN_DEFECT 升级为硬断言并新增两档×四页宽度矩阵断言。
全部验收通过（run.mjs exit 0 / tsc exit 0 / vitest 60 files 567 tests 全绿）。

### 变更文件

| 文件 | 变更 |
|---|---|
| `apps/desktop/frontend/src/ui/ui.css` | 删 `.nm-app { min-width: 1024px }`（根因行），注释说明来历 |
| `apps/desktop/frontend/src/pages/pages.css` | 新增 `@media (max-width: 1023px)`：书架网格 `repeat(auto-fill, minmax(150px,1fr))` + `.nm-book-card { width:auto }` |
| `apps/desktop/frontend/e2e/uiux-v2/run.mjs` | S10 knownDefect→硬断言；新增 900×700 与 1280×800 两档×四页 `scrollWidth===clientWidth` 断言与截图；TASK_ID/RUN_ID 改 NARROW-1 |
| `apps/desktop/frontend/e2e/uiux-v2/lib/env.mjs` | 隔离根/canonical 证据目录改指 `task-envs/UIUX-V2-RUNTIME-NARROW-1` 与 `verification/UIUX-V2-RUNTIME-NARROW-1`（落实任务卡硬约束 1） |
| `apps/desktop/frontend/e2e/uiux-v2/diag-narrow.mjs` | 新增：两档四页宽度诊断脚本（offender 扫描 + 截图） |
| `verification/UIUX-V2-RUNTIME-NARROW-1/**` | README（根因/修法/改前改后数字/复现命令）、改前改后诊断 JSON 与截图、run-i3 完整验收报告与 S10 截图 |
| `doc/tasks/UIUX-V2-RUNTIME-NARROW-1.md` | 追加执行记录（只追加，未改既有内容） |

未触碰：`design/tokens.css`、`design/base.css`、七态符号、Rust/IPC、
`tauri.conf.json`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| G1 根因定位 | `node e2e/uiux-v2/diag-narrow.mjs`（改前 exe = REALCORE-2 冻结构建，SHA256 `E58CFE59…`） | 隔离 env `task-envs/UIUX-V2-RUNTIME-NARROW-1/run-i1` | PASS：900 档四页 1024/900，`.nm-app` computed min-width=1024px、width=1024，offender 全为其子孙 | `verification/UIUX-V2-RUNTIME-NARROW-1/diag/before-fix-diag.json` |
| G2 900×700 四页无横向溢出 | run.mjs S10（升级后硬断言） | 本交付构建，exe SHA256 `C1AB2749EAEE5E1BD793EEC1FCA59158B76E44CF741349A0962B76AC11DFA8BD`，隔离 env run-i3 | PASS：四页 `scrollWidth=clientWidth=900`；S10 knownDefects=0 | `run-i3/report.json`（`narrowViewportMatrix`）、`run-i3-shots/11-900x700-dpr2-*.png` |
| G3 不退化（1280×800） | diag before/after 数值对比 + run.mjs S10 | 同上 | PASS：改前改后 1280 档四页布局数值完全一致（titlebar 453/326/453、库区 892、详情 340）；四页 1280/1280 | `diag/before|after-fix-diag.json`、`run-i3-shots/12-1280x800-dpr2-*.png` |
| G3 既有通过项保持 | run.mjs S10 原断言 | 同上 | PASS：标题栏三段不重叠、内容/详情不重叠、blurLayers=2、状态条可见（868×44） | `run-i3/report.json` S10 |
| G4 断言升级防回退 | run.mjs S10 源码 + 实跑 | 同上 | PASS：knownDefect 已删除，溢出直接 FAIL | `run.mjs` S10 段 |
| 全量回归 | `node e2e/uiux-v2/run.mjs` | 同上（真实 packaged EXE + 真实 Python Core sidecar，S1..S10 含建书/导入/sidecar 掉线恢复） | PASS：exit 0，10/10 scenarios | `run-i3/report.json` |
| 类型与单测 | `node node_modules/typescript/bin/tsc --noEmit`；`npx vitest run` | frontend 工作区 | PASS：tsc exit 0；vitest 60 files / 567 tests 全绿（基线一致） | 复现命令见 verification README |

## 接收方式

- 分支：`main`（单 commit，未 push）；base = `7020dc591`。
- 复现：
  ```powershell
  cd "G:/CODEX/New Manga/apps/desktop/frontend"; npm run build
  cd ../src-tauri; cargo tauri build --no-bundle --config tauri.acceptance.conf.json
  cd ../frontend; $env:UIUX_E2E_EXE='G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe'; node e2e/uiux-v2/run.mjs
  ```
- 证据入口：`verification/UIUX-V2-RUNTIME-NARROW-1/README.md`。
- Reviewer 注意点：① 断言升级后的 S10 曾以改前 exe 跑必然 FAIL（防回退有效性的
  旁证 = 改前 diag 数据）；② env.mjs 目录改指属于本卡硬约束 1 的落实，
  REALCORE-2 证据树未动。

## 已知限制 / 未覆盖项

1. **纵向未处理**：`.nm-app` 仍保留 `min-height: 680px`；视口高度 <680 时会有同类
   纵向溢出。本卡 AC 只覆盖宽度；如需处理另立卡。
2. **≤1023 断点内的书架网格视觉**：自适应列在 900 视口为 3 列（卡片 150–160px 宽，
   略窄于宽窗的 168px）。S10 截图（`run-i3-shots/11-900x700-dpr2-shelf.png`）
   已含带书卡场景，但"3 列卡片的美观度"属人工评审范畴。
3. **极窄视口（<~884px，标题栏 min-content）以下**：标题栏会开始挤压/裁剪
   （.nm-shelf overflow:hidden 兜底）。本卡验收口径为 900 与 1280 两档；
   <900 未逐档验证。
4. 阅读器页在无书/无章节数据时也断言了宽度（run-i3 中阅读器有真实章节上下文）；
   "带真实页面图像的阅读器 900 档"依赖导入真图，S8 的 CDP 注入在
   HOST-ISSUER-1 架构下不可用（人工验证项，REALCORE-2 已裁定）。

## 下一任务建议（必填）

- Task ID / 标题：无需下一步操作（本卡交付后转 DSH Review；未发现需要立即释放的后续安全项）
- 推荐 Agent / Reviewer：Reviewer = DSH（任务卡 frontmatter 已定）；DSH 不得审核自己实现的变更不适用（本卡实现者为 ZCode）
- Recovery point：仓库 `G:/CODEX/New Manga`、branch `main`、base `7020dc591`、head = 本交付单 commit（`git log -1`）；无新 worktree（在主 worktree 实施改动）
- 允许修改路径 / 禁止范围：见任务卡 `allowed_paths`
- 验证命令、环境与完成 Gate：见上"接收方式"；Gate = Review approved + 集成验证后置 done
