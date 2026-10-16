---
task_id: P14
author: codex
recipient: dsh
base_commit: 536962909963eaeeff7e94ff511f76f927652cd6
delivery_head: 8f3fddcc15e4db55e22e7bde425af168c18bec44
status: in_review
canonical_evidence_status: complete
---

# Handoff：P14 工作台 Workbench

## 交付结果

实现提交：`8f3fddcc15e4db55e22e7bde425af168c18bec44`（分支 `codex/P14`，未 push / merge）。Task、原始验证日志、命令与退出码元数据、禁用项证据及边界核验证据均在该提交中；Canonical Evidence SHA256 按磁盘字节记录于 `doc/tasks/P14.md`。

实现文件：

- `apps/desktop/frontend/src/bookshelf/error.ts`
- `apps/desktop/frontend/src/bookshelf/error.test.ts`
- `apps/desktop/frontend/src/region/RegionOverlay.tsx`
- `apps/desktop/frontend/src/shell/AppShell.tsx`
- `apps/desktop/frontend/src/workbench/DisabledFeature.tsx`
- `apps/desktop/frontend/src/workbench/ExportDialog.tsx`
- `apps/desktop/frontend/src/workbench/PageListPanel.tsx`
- `apps/desktop/frontend/src/workbench/PageListPanel.test.tsx`
- `apps/desktop/frontend/src/workbench/RegionInspector.tsx`
- `apps/desktop/frontend/src/workbench/RelabelConfirmDialog.tsx`
- `apps/desktop/frontend/src/workbench/RelabelContextMenu.tsx`
- `apps/desktop/frontend/src/workbench/TaskProgressPanel.tsx`
- `apps/desktop/frontend/src/workbench/ViewerPanel.tsx`
- `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx`
- `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx`
- `apps/desktop/frontend/src/workbench/WorkbenchToolbar.tsx`
- `apps/desktop/frontend/src/workbench/client.ts`
- `apps/desktop/frontend/src/workbench/client.test.ts`
- `apps/desktop/frontend/src/workbench/pageImage.ts`

本页提供导出面板 `ExportDialog`，支持选定页面、格式选项、stale policy、取消、进度/历史与打开导出目录。保存位置由 host 系统对话框选择；前端请求不含输出路径或 `ExportTargetRef`，快照/历史 DTO 只投影 ID、范围、状态、格式、计数与摘要。

G15 **保持禁用**：Core 没有 `ListRuns` / 活跃 Run 查询；本页只读取本次明确启动的已知 `run_id`，不伪造发现列表、不做本地聚合，也没有新增命令或 wire。

`m2res` 依 Coordinator 裁决 A 作为专用媒体显示例外：短期随机页图 URL / opaque handle 只在 Viewer 的资源读取链路中使用，分块读入 Blob 后以可撤销 `blob:` URL 渲染；不持久化、不写日志或事件 payload、不授权写操作。请求、返回、事件和错误中的路径、授权 grant、会话凭据与可解码路径字段仍禁止。详细核验见 `verification/P14/boundary-evidence.md`。

设计 §7 禁用项逐条对应：

| Gap | 可见禁用入口 | 状态 |
|---|---|---|
| G9 保存人工译文 | `gap-g9-save-manual-translation` | `disabled`，显示原因 |
| G10 新建 Region | `gap-g10-create-region` | `disabled`，显示原因 |
| G10 删除 Region | `gap-g10-delete-region` | `disabled`，显示原因 |
| G11 Region 几何编辑 | `gap-g11-region-geometry` | `disabled`，显示原因 |
| G12 Lock 设置/解除 | `gap-g12-region-lock` | `disabled`，显示原因 |
| G13 Revision pin | `gap-g13-revision-pin` | `disabled`，显示原因 |
| G14 页序拖拽重排 | `gap-g14-page-order` | `disabled`，显示原因 |
| G15 Run 发现/任务队列/中断恢复 | `gap-g15-run-discovery` | `disabled`，说明无 `ListRuns` 查询 |
| G16 Core 可用性 | `gap-g16-core-availability` | `disabled`，显示原因 |
| G18 PageList 缩略图 | `gap-g18-page-thumbnails` | `disabled`，显示原因 |
| G18 当前 Run 页缩略图 | `gap-g18-current-page-thumbnail` | `disabled`，显示原因 |
| G26 导入细分进度 | `gap-g26-import-progress` | `disabled`，显示原因 |

## 验证证据

测试运行于与 `delivery_head` 前端源文件相同的工作树；源文件随后原样进入该提交。每条命令的 shell、解释器版本和退出码见相邻 `.meta.txt`。

| AC / 场景 | 实际命令 / 步骤 | 环境与被测提交 | 结果 | 日志 / 产物 |
|---|---|---|---|---|
| AC1–AC4 | `npm --prefix apps/desktop/frontend test` | Node v24.15.0 / npm 12.0.1；源码同 `delivery_head` | PASS：18 files / 190 tests，exit 0 | `verification/P14/frontend-tests.log`、`.meta.txt` |
| AC1 | `npm --prefix apps/desktop/frontend run build` | Node v24.15.0 / npm 12.0.1；源码同 `delivery_head` | PASS，exit 0 | `verification/P14/frontend-build.log`、`.meta.txt` |
| AC2 | DOM 测试逐项枚举 §7 入口 | Vitest DOM；源码同 `delivery_head` | PASS：每个入口 disabled、有可见原因并以 `aria-describedby` 关联；G18 Run 缩略图有额外断言 | `verification/P14/disabled-entry-evidence.md`、`WorkbenchPage.test.tsx` |
| AC3 | 静态检查调用链与错误/导出投影；`client.test.ts` 对路径和 target ref 污染输入验证 allowlist 投影 | 源码同 `delivery_head` | PASS；边界细节见证据文件 | `verification/P14/boundary-evidence.md`、`client.test.ts` |
| AC4 | 前端事件消费测试 | Node / Vitest；源码同 `delivery_head` | PASS：事件后重查 Run 快照与任务投影 | `verification/P14/frontend-tests.log` |
| AC5 | `python -m pytest tests/core -q -p no:cacheprovider` | Python 3.14.6 / pytest 9.1.1 | PASS：407 passed，exit 0 | `verification/P14/core-tests.log`、`.meta.txt` |
| AC5 | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests` | cargo/rustc 1.98.1 | PASS：95 passed，1 ignored，12 filtered，exit 0 | `verification/P14/rust-source-tests.log`、`.meta.txt` |
| AC5 | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture` | cargo/rustc 1.98.1；既有 `target/core-sidecar` junction | PASS：12 passed，exit 0 | `verification/P14/rust-packaged-tests.log`、`.meta.txt` |
| AC5 | GUI e2e | 无头 Windows / WebView2 | **NOT_RUN**：无法取得 WebView2 窗口句柄，错误 `0x80070578`。以上 DOM 单测不作为 GUI e2e 证据。 | 本 Handoff、`doc/tasks/P14.md` |
| AC6 | 核对固定提交、Handoff 与 Canonical Evidence SHA256 | Git；`delivery_head` 如上 | PASS；Task 中每条证据的 `commit` 均为真实提交 SHA | `doc/tasks/P14.md` |

## 接收方式

- 分支 / worktree：`codex/P14` / `G:/CODEX/New Manga.workspace/worktrees/P14`
- 基线：`536962909963eaeeff7e94ff511f76f927652cd6`
- 固定交付提交：`8f3fddcc15e4db55e22e7bde425af168c18bec44`
- 验证：审阅 `doc/tasks/P14.md` 的 Canonical Evidence 表与 `verification/P14/**` 原始日志；当前无需重跑前端、Core 或 Rust 测试，因为源树自记录后未变化。

## 下一任务建议

- Task ID / 标题：P14 独立实现 Review（P14 后续 Gate，不新建占位 Task）
- 推荐 Agent / Reviewer：dsh
- 推荐原因与前置依赖：本 Task 固定 `reviewer: dsh`；Owner 不自审。前置为本 Handoff 与固定 `delivery_head`。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch/worktree `codex/P14` / `G:/CODEX/New Manga.workspace/worktrees/P14`；base `536962909963eaeeff7e94ff511f76f927652cd6`；head `8f3fddcc15e4db55e22e7bde425af168c18bec44`。
- 允许修改路径：只读审查；发现问题写 Review findings 并交回 Codex，不直接修改实现。
- 禁止范围与新增授权条件：不得修改代码、提交、push、merge 或更改用户 dirty 文件；新增能力/契约仍需另行授权。
- 交付物：依 `doc/templates/REVIEW.md` 记录 Architecture、Verification、findings disposition 和未覆盖风险；逐条核对本 Task AC、G15 禁用、导出路径投影及 `m2res` 精确边界。
- 验证命令、环境与完成 Gate：以固定提交和已归档原始日志为输入；给出 `approved` / `changes_requested` 等合法 Review 结论及对应证据。Codex 核验后再决定集成；本 Handoff 不代表已接受。
- 可直接转发给 Agent 的指令：

  > 请在仓库 `G:/CODEX/New Manga` 对分支 `codex/P14` 的固定提交 `8f3fddcc15e4db55e22e7bde425af168c18bec44` 做只读独立 Review。基线为 `536962909963eaeeff7e94ff511f76f927652cd6`。阅读 `doc/tasks/P14.md`、`doc/design/AD001_FOUR_PAGE_UI_BASELINE.md` §3/§7、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §6.4/§10、受影响前端源文件及 `verification/P14/**`。重点核对 AC1–AC6、禁用项逐条 DOM 断言、G15 未发明、导出路径/授权投影、`m2res` 媒体例外及四处数据边界。不要修改任何文件、不要提交或合并；按 `doc/templates/REVIEW.md` 输出 findings、严重级别、证据、未覆盖风险与结论。GUI e2e 明确未运行（WebView2 `0x80070578`），不得把单测等同于 GUI e2e，也不得把本次 Owner 交付视为已接受。

## 风险与遗留

- GUI e2e 未运行，原因是无头环境无法取得 WebView2 窗口句柄 `0x80070578`。
- dsh 独立 Review 与 Codex 集成验收尚未完成；当前 Task 状态保持 `in_review`，未声称已被接受。
- G15 继续禁用，直至另一个授权 Task 冻结 Run 发现 / 列表 wire。
