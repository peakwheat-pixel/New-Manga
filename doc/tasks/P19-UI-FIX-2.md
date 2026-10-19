---
id: P19-UI-FIX-2
title: 修复顶栏「导入作品」静默无反馈（P19-UI-FIX-1 遗漏的入口）
kind: bugfix
governance_version: 2
status: done
approval: coordinator_release_20261017_from_P19_r6_probe
suggested_owner: Codex
owner: codex
reviewer: DeepSeek Harness
depends_on: [P19-UI-FIX-1]
base_commit: 3a3eeab02114b0230fe27bb60396e720dada6d26
branch: codex/P19-UI-FIX-2
worktree: G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2
integration_commit: ebec0b030
delivery_head: f1fab801717114cb1801158b0b7fa7fa80d961e0
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P19-UI-FIX-2
---

# P19-UI-FIX-2：顶栏「导入作品」静默无反馈

## 来源
`verification/P19/create-work-and-import-r6.md`：重建产品实测，**顶栏 `导入作品` `IsEnabled=True`，点击后无选择器/无错误/无反馈**（10 次窗口采样）；而空态那组按钮（`import-file-btn`/`import-folder-btn`）已由 P19-UI-FIX-1 修好。→ **修复遗漏了顶栏入口**。

## Acceptance Criteria
- [x] **AC1**：真实 GUI/UIA 点击顶栏 `导入作品` 后，同一 WebView 窗口显示可见“未开放”原因；无目标章节时 file/folder picker 均可见且禁用。修复前基线已满足该行为，修复后复验一致。
- [x] **AC2**：逐一检查顶栏、空书架、详情侧栏、file picker、folder picker。前三入口共用同一 `handleOpenImport`/`ImportDialog` 路径；无目标时说明原因并禁用 picker，有目标时保留既有选择器流程。
- [x] **AC3**：新增回归测试覆盖三处外层入口及无目标状态；前端 **28 files / 278 passed / 0 skipped / exit 0**。固定基线为 274，P19-UI-FIX-1 后为 277（+3），本 Task 后为 278（+1）；`npm run build` exit 0。
- [x] **AC4 真实 GUI 复验**：按 `npm run build` → `pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force` → `cargo build` 重建；bundle 与 resources 的 5 个 sidecar 哈希全部一致。隔离副本启动真实 GUI，点击顶栏后 UIA 捕获可见文本反馈，应用 exit 0；源数据前后哈希不变。
- [x] **AC5 交付**：delivery head、Handoff 与 Canonical Evidence 已固定；本 Task 状态=`in_review`。证据逐条绑定 commit/path 并按磁盘字节计算 SHA-256；BL-15/17/19/16/18 已核对。

## 允许 / 禁止
- 允许：`apps/desktop/frontend/**`、本 Task、`doc/handoffs/P19-UI-FIX-2-*.md`、`verification/P19-UI-FIX-2/**`。
- 禁止：改契约/Schema/依赖、改 `src/**`（需 Core 配合先上报）；**不得**用"隐藏顶栏按钮"规避；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty。

## 依赖、风险与阻塞
- 前置：P19-UI-FIX-1（done）。**被阻塞方**：P19 的 AC2。
- 风险：把"隐藏按钮"当修复（AC2 明确禁止）。
- **注意**：本 Task **不**裁决"空书架是否应允许新建作品"（该产品取舍待用户）；仅修"点了没反馈"。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。
- 2026-10-17 Owner 复验：修复前基线已经通过 AC1；原 R4/R6 仅证明没有新建系统选择器窗口，不能排除 WebView 内的文本反馈。未改生产组件，补齐三处入口的一致性回归测试与真实 GUI 证据。
- 实现/测试提交：`f1fab801717114cb1801158b0b7fa7fa80d961e0`；证据提交：`fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7`；Handoff 随后续文档提交。

## 验证与证据

| AC/场景 | 命令 / 步骤 | 环境与被测 commit | 结果 | 证据 |
|---|---|---|---|---|
| AC3 基线套件 | `npm test` | Node/Vitest；基线 `3a3eeab02114b0230fe27bb60396e720dada6d26` | PASS：28 files / 277 passed；相对 274 基线 +3 | `frontend-npm-test-before.log` |
| AC2/AC3 新增测试与完整套件 | `npm test` | Node/Vitest；delivery `f1fab801717114cb1801158b0b7fa7fa80d961e0` | PASS：28 files / 278 passed / 0 skipped / exit 0；净增 1 | `frontend-npm-test-delivery.log` |
| AC3 前端构建 | `npm run build` | Node/Vite；delivery `f1fab801717114cb1801158b0b7fa7fa80d961e0` | PASS：exit 0；dist=`index-B2KOm56c.js` | `frontend-npm-build-final.log` |
| AC4 强制 sidecar 构建 | `pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force`，`PYINSTALLER_CONFIG_DIR` 指向 worktree `target`，禁用 pyc 写入 | Windows / PyInstaller 6.22.3；delivery head | PASS：exit 0；closure assertions 通过；清理缓存路径位于 worktree | `sidecar-build-final.log` |
| AC4 Cargo 构建 | `cargo build`，cwd=`apps/desktop/src-tauri` | Windows / Cargo；delivery head | PASS：exit 0；7 条已有 warning；构建后还原 58 个自动生成文件 | `cargo-build-final.log` |
| AC4 bundle/resource hash | SHA-256 比较 `target/core-sidecar/core-sidecar` 与 `target/debug/resources/core-sidecar` | delivery head | PASS：5/5 一致；`core_service.exe`=`7759d3fba4dd0cc7b46836460c47440a77273f3d804fd2d7c0f1b36b7d2954c5` | `sidecar-resource-hash-final.json` |
| AC1/AC4 修复前真实 GUI | 构建基线产品；隔离数据启动；UIA `InvokePattern` 点击顶栏 | 基线 `3a3eeab02114b0230fe27bb60396e720dada6d26` | PASS：顶栏 enabled；同一窗口显示“未开放”说明；picker 均 disabled；应用 exit 0 | `before-confirm/uia-run.log`、`before-confirm/import-open.uia.txt` |
| AC1/AC4 修复后真实 GUI | 固定 delivery 重建产品；隔离数据启动；UIA 点击顶栏 | delivery `f1fab801717114cb1801158b0b7fa7fa80d961e0` | PASS：同一可见反馈；picker 均 disabled；应用 exit 0 | `after/uia-run.log`、`after/import-open.uia.txt` |
| AC4 源数据保护 | 比较 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data}` 前后树哈希 | 本地真实布局只读复制；UIA 仅使用 worktree 隔离根 | PASS：catalog 1 文件、data 2 文件；哈希均 unchanged | `appdata-source-before.json`、`appdata-source-after.json`、`appdata-source-preservation-check.json` |

执行备注：第一次 UIA runner 在控件树尚未稳定时未找到顶栏按钮；等待/重试后的 `before-confirm` 与 `after` 均通过。新增测试首轮因复用 React root 导致初始化 props 不更新，改为独立 root 后定向测试 18/18 通过，完整套件 278/278 通过；原始日志保留在 evidence 目录。未跳过测试。

## Canonical Evidence

以下证据均在 commit `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7`，每条均通过 `git cat-file -e <commit>:<path>`。SHA-256 按当前 worktree 磁盘字节计算；class 仅使用 `CANONICAL`。

| evidence_id | AC | path | commit | sha256 | class |
|---|---|---|---|---|---|
| P19UIFIX2-TEST-BASELINE | AC3 | `verification/P19-UI-FIX-2/frontend-npm-test-before.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `e219492ef68c842a1c294ce1a59a552adff21aa17a606c92979a520016c2a45b` | CANONICAL |
| P19UIFIX2-TEST | AC2, AC3 | `verification/P19-UI-FIX-2/frontend-npm-test-delivery.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `35d700b3128fc742d9cdf844fd1ccaf582977bb3bc9f0bc7a3b9b0a437a44222` | CANONICAL |
| P19UIFIX2-FRONTEND-BUILD | AC3 | `verification/P19-UI-FIX-2/frontend-npm-build-final.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `864d96edc1efad104c376742f40be181f818a02af563baf7844c703a86bf583c` | CANONICAL |
| P19UIFIX2-SIDECAR | AC4 | `verification/P19-UI-FIX-2/sidecar-build-final.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `ab9add4c35b064725105e3ad63fcc3af859b2df9b668a6467540d7326dc9c3af` | CANONICAL |
| P19UIFIX2-CARGO | AC4 | `verification/P19-UI-FIX-2/cargo-build-final.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `de7ece18654d9b4fdaa4a1cb2d487825c78feb577cbdf6aadce66e306b3454db` | CANONICAL |
| P19UIFIX2-HASH | AC4 | `verification/P19-UI-FIX-2/sidecar-resource-hash-final.json` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `efc2ccb14fd32f488c398b1c8182c4dca755fa44bd8bf835a3f75672e8b69524` | CANONICAL |
| P19UIFIX2-UIA-BEFORE | AC1, AC4 | `verification/P19-UI-FIX-2/before-confirm/uia-run.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `3a2d823669b7abeab5f17fb7f5d3158b1174b787ee783aa94400bdb57c127a98` | CANONICAL |
| P19UIFIX2-UIA-BEFORE-ELEMENTS | AC1, AC4 | `verification/P19-UI-FIX-2/before-confirm/import-open.uia.txt` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `db3ebf3146eb8aae9f49513c7a53fd00be88a3155e68d63eca4e048814f4ac68` | CANONICAL |
| P19UIFIX2-UIA-AFTER | AC1, AC4 | `verification/P19-UI-FIX-2/after/uia-run.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `81900914c6f79588df28304b7215f0f62c5c757c7585f26534ca7ef850bdfd90` | CANONICAL |
| P19UIFIX2-UIA-AFTER-ELEMENTS | AC1, AC4 | `verification/P19-UI-FIX-2/after/import-open.uia.txt` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `db3ebf3146eb8aae9f49513c7a53fd00be88a3155e68d63eca4e048814f4ac68` | CANONICAL |
| P19UIFIX2-DATA | AC4 | `verification/P19-UI-FIX-2/appdata-source-preservation-check.json` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `38a55e549a2bebeb8f0b39e2050c587e234cc936a291fc897f0bbbf0cba75d45` | CANONICAL |
| P19UIFIX2-COMPARISON | AC1, AC4 | `verification/P19-UI-FIX-2/uia-before-after-comparison.md` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `668f4e6b39b72ac1d80a0ceca7f66d018d84c0de0747dd830dbf71fde312b216` | CANONICAL |
| P19UIFIX2-UIA-RUNNER | AC4 | `verification/P19-UI-FIX-2/run-uia.ps1` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `1e93214afae808be2738a5624482fd510ed1cb8d5d980d376d995da164e83180` | CANONICAL |
| P19UIFIX2-ISOLATION-REBIND | AC4 | `verification/P19-UI-FIX-2/rebind-isolated-namespace.py` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `f24b70b8c71b1a3e7a79c8821609dce56371e6b677cbb7b4f6bfdf08e1ef79c6` | CANONICAL |
| P19UIFIX2-ISOLATION-LOG | AC4 | `verification/P19-UI-FIX-2/isolation-rebind.log` | `fc8e4eb9c4e8f32a00ccd6cd1d79df728f10d8f7` | `d1e4f7218ba0ac3ed5ba0547005c7f7c135bc81697537a48e139f4298b506c35` | CANONICAL |

## 风险、限制与阻塞

- 此 worktree 的修复前 UIA 已证明顶栏行为满足 AC1，因此没有改生产组件；本 Task 以入口清单测试和重建产品证据关闭原观察歧义。独立 Reviewer 仍需确认该判定。
- 本次隔离 GUI 没有可导入章节；有目标章节时的文件选择器调用由现有前端 IPC/组件测试覆盖，未在真实 GUI 中选择文件。
- 第一次基线 `build_sidecar.ps1 -Force` 使用了默认 `C:\Users\49745\AppData\Local\pyinstaller` 缓存；日志显示该缓存被清理并重建（worktree 外副作用）。最终 AC4 构建通过 `PYINSTALLER_CONFIG_DIR` 将缓存隔离在 worktree `target`。用户源漫画数据未改。
- `cargo build` 生成的 58 个 `gen/schemas` / `permissions/autogenerated` 文件已按构建前干净状态还原，不在提交中。

## Closeout Record

- 关闭：2026-10-17（dsh）。Reviewer=dsh（approved，erification/P19-UI-FIX-2/dsh-review-r1.md）。
- 合并 bec0b030（--no-ff，无冲突）；delivery_head 1fab8017。
- 复核要点：顶栏导入现有 import-dialog+import-unavailable-notice；三类入口（toolbar/empty-state/book-detail）行为一致有测试；AC4 GUI 前后对比 + sidecar hash 前后 + **用户数据保全检查** 齐备。
- **记录缺陷（未尽事项）**：**未产出 doc/handoffs/P19-UI-FIX-2-*.md**（AC5 要求）。受让人未补写，Coordinator 不代写以免伪造执行方自述——如实登记，不阻断集成。
