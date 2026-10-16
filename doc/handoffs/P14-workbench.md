---
task_id: P14
author: codex
recipient: dsh
base_commit: 536962909963eaeeff7e94ff511f76f927652cd6
delivery_head: ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c
status: in_review
canonical_evidence_status: complete
---

# Handoff：P14 工作台 Workbench

## 交付结果

实现提交：`ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c`（分支 `codex/P14`）。证据元数据修正提交：`3eee090770cb86362095c139ba093078fcc2351c`。交付未 push / merge。完整前端变更路径见 `git diff --name-only 536962909963eaeeff7e94ff511f76f927652cd6 ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c -- apps/desktop/frontend/src`。

前端涉及 `src/App.tsx` / `App.test.tsx`、`bookshelf/error.ts` / `.test.ts`、`region/RegionOverlay.tsx`、`resourceChannel/client.ts` / `.test.ts`、`shell/AppShell.tsx`，以及 `workbench/` 下的禁用入口、导出面板、PageList、Region Inspector、重标菜单、TaskProgressPanel、Viewer、WorkbenchError、WorkbenchPage、Toolbar、client、pageImage 及对应测试。

| AC | 状态 | 交付与证据 |
|---|---|---|
| AC1 §3 工作台 | 完成 | 六区布局、状态矩阵、固定 TaskProgressPanel、交互与键盘路径；Core 在作品/章节/页面/Region 投影不可用时提供全区块错误卡。前端 DOM 测试 19 files / 204 tests。 |
| AC2 §7 缺口 | 完成 | 禁用清单逐项映射至 §7；各入口均有可见、不可操作且可理解的原因，DOM 断言还核对 `aria-describedby`。详见下表与 `verification/P14/disabled-entry-evidence.md`。 |
| AC3 边界 | 完成 | 按 Coordinator 裁决 A 允许 `m2res` 仅用于媒体显示；路径、grant、会话凭据及可解码路径字段仍禁止。导出面板在本页实现，路径留在 host。详见 `verification/P14/boundary-evidence.md`。 |
| AC4 事件 | 完成 | 六类事件只作失效提示；收到后重查权威快照，不由事件序列推导状态。 |
| AC5 验证 | 完成（GUI e2e 按要求明确未运行） | 前端 tests/build、Core、Rust source 与 packaged 套件原始日志及退出码见验证表。DOM tests 不代表 GUI e2e。 |
| AC6 交付 | 完成，待独立 Review | 固定实现提交、Handoff、Canonical Evidence 与磁盘字节 SHA256 已登记；证据文件的包含性由 `git cat-file -e <commit>:<path>` 核验。 |

### §7 禁用入口逐项对应

| 设计 §7 缺口 | 入口 `data-testid` | DOM 断言 |
|---|---|---|
| G9 保存人工译文 | `gap-g9-save-manual-translation` | disabled、原因可见且可理解、ARIA 原因关联 |
| G10 新建 Region | `gap-g10-create-region` | 同上 |
| G10 删除 Region | `gap-g10-delete-region` | 同上 |
| G11 Region 几何编辑 | `gap-g11-region-geometry` | 同上 |
| G12 Lock 设置/解除 | `gap-g12-region-lock` | 同上 |
| G13 Revision pin | `gap-g13-revision-pin` | 同上 |
| G14 页序拖拽重排 | `gap-g14-page-order` | 同上 |
| G15 Run 发现/队列/中断处置 | `gap-g15-run-discovery` | disabled、原因明确包含缺少 `ListRuns` 查询、ARIA 原因关联 |
| G16 Core 可用性 | `gap-g16-core-availability` | disabled、原因可见且可理解、ARIA 原因关联 |
| G18 PageList 缩略图 | `gap-g18-page-thumbnails` | 同上 |
| G18 当前 Run 页缩略图 | `gap-g18-current-page-thumbnail` | 有 Run projection 时仍 disabled、原因可见、ARIA 原因关联 |
| G26 导入细分进度 | `gap-g26-import-progress` | disabled、原因可见且可理解、ARIA 原因关联 |

G15 **保持禁用且未被发明**：没有新增 `ListRuns` 命令、wire 或本地 Run 聚合；DOM 测试逐项检查禁用入口，另断言生产启动不调用 Run 列表命令。工作台只读取本次明确启动且已知 `run_id` 的快照/投影。

### 导出面板与路径投影

导出面板 `ExportDialog` 在本页 `WorkbenchPage` 内实现。保存目标由 host 系统对话框选择；WebView 导出请求仅含业务 ID、所选范围、格式/选项与 stale policy，不含输出路径或 `ExportTargetRef`。快照与历史经 allowlist 投影，不含路径或 grant 材料；页面说明保存位置由系统对话框选择，不接收或显示路径。

### Coordinator 裁决 A 与 `m2res` 精确边界

依据 [M2-C1 §10 / L783](../contracts/M2-C1_TYPED_IPC_CONTRACT.md)：仅允许由 `resolve_page_resource` / `issue_resource_url` 产生的短期随机 `m2res` 页图 URL / opaque handle 用于 Viewer 媒体显示和分块读取；该显示句柄不授权任何写操作。

仍禁止绝对/相对/UNC 路径出现在请求、返回、事件 payload、错误 message；禁止 `ExportTargetRef` / `ImportSourceRef` / `ResourceRef` grant 材料、`host_session_credential` / `core_session_id` 等会话凭据及任何可解码出路径的字段。经核验未发现越界。URL/opaque handle 不持久化、不写日志或事件 payload、不离开媒体显示路径；展示完成后用可撤销 `blob:` URL 渲染。

## 验证证据

| AC / 场景 | 实际命令 / 步骤 | 环境与被测提交 | 结果 | 原始日志 / 产物 |
|---|---|---|---|---|
| AC1–AC4 | `npm --prefix apps/desktop/frontend test` | Node v24.15.0 / npm 12.0.1；源码 `ac2296d` | PASS：19 files / 204 tests，exit 0 | `verification/P14/frontend-tests-r3.log`、`.meta.txt` |
| AC5 | `npm --prefix apps/desktop/frontend run build` | Node v24.15.0 / npm 12.0.1；源码 `ac2296d` | PASS，exit 0 | `verification/P14/frontend-build-r3.log`、`.meta.txt` |
| AC2 / AC5 | 逐项枚举 §7 禁用入口并断言 DOM | Vitest / jsdom | PASS：每项 disabled、原因文本可见，ARIA 关联；G18 Run 缩略图另有断言 | `verification/P14/disabled-entry-evidence.md`、`WorkbenchPage.test.tsx` |
| AC3 | 核对请求/返回/事件/错误投影及资源调用链 | 固定源码提交 `ac2296d` | PASS；A 裁决边界逐项核对 | `verification/P14/boundary-evidence.md`、`client.test.ts` |
| AC4 | 事件到快照重查测试 | Vitest | PASS；以权威快照而非事件 payload 显示状态 | `verification/P14/frontend-tests-r3.log` |
| AC5 Core | `python -m pytest tests/core -q -p no:cacheprovider` | Python 3.14.6 / pytest 9.1.1 | PASS：407 passed，exit 0 | `verification/P14/core-tests.log`、`.meta.txt` |
| AC5 Rust source | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests` | cargo/rustc 1.98.1 | PASS：95 passed、1 ignored、12 filtered，exit 0 | `verification/P14/rust-source-tests.log`、`.meta.txt` |
| AC5 Rust packaged | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture` | cargo/rustc 1.98.1；既有 `target/core-sidecar` junction | PASS：12 passed，exit 0 | `verification/P14/rust-packaged-tests.log`、`.meta.txt` |
| AC5 GUI e2e | GUI WebView2 端到端交互 | 无头 Windows | **NOT_RUN**：窗口句柄错误 `0x80070578`；不把 DOM 单测称为 e2e | 本 Handoff、`doc/tasks/P14.md` |
| 历史记录 | R1 前端运行 | Node v24.15.0 / npm 12.0.1 | 18 files / 190 tests 原始日志保留，不作为最新运行结果 | `verification/P14/frontend-tests.log`、`frontend-build.log` 及 meta |

Canonical Evidence SHA256 以 PowerShell `Get-FileHash -Algorithm SHA256 -LiteralPath <path>` 对工作区磁盘字节计算；Task 表中的证据 commit 为 `3eee090770cb86362095c139ba093078fcc2351c`，该提交包含每个登记路径。未重新运行 Core / Rust；它们使用本次既有原始日志与退出码。

## 接收方式

- 仓库 / 分支 / worktree：`G:/CODEX/New Manga`；`codex/P14`；`G:/CODEX/New Manga.workspace/worktrees/P14`
- 基线：`536962909963eaeeff7e94ff511f76f927652cd6`
- 固定实现 `delivery_head`：`ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c`
- Canonical Evidence 包含提交：`3eee090770cb86362095c139ba093078fcc2351c`
- 接收检查：读取 `doc/tasks/P14.md`、本 Handoff、`verification/P14/**`；验证证据 commit 包含性及 Task 中磁盘字节 SHA256。

## 下一任务建议

- Task ID / 标题：P14 独立实现 Review（现有 Gate，不新建占位 Task）
- 推荐 Agent / Reviewer：dsh
- 推荐原因与前置依赖：Task 指定 reviewer=dsh；R2 已返回 `changes_requested`，Owner 完成返修，须由非作者复核固定交付。
- Recovery point：`G:/CODEX/New Manga`；分支/worktree `codex/P14` / `G:/CODEX/New Manga.workspace/worktrees/P14`；base `536962909963eaeeff7e94ff511f76f927652cd6`；实现 head `ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c`。
- 允许修改路径：只读审查；发现问题写 Review finding 交还 Codex，不直接改文件。
- 禁止范围与新增授权条件：不修改代码或用户 dirty 文件，不提交、push、merge；不增改共享契约。
- 交付物：按 `doc/templates/REVIEW.md` 记录结论、findings、严重级别、证据与未覆盖风险；逐项复核 AC1–AC6、禁用入口、G15、导出路径投影、`m2res` 四处边界与 Canonical Evidence。
- 验证命令、环境与完成 Gate：独立复核固定实现 head 与本 Handoff/Task/证据；可只读重算哈希与检查 `git cat-file -e` 包含性。不得将 GUI e2e 标为已运行或将交付写成已接受。
- 可直接转发给 Agent 的指令：

  > 请在仓库 `G:/CODEX/New Manga` 对 `codex/P14` 的固定实现提交 `ac2296d59a63f4ea5c2fe8ea54c8e29b15072d5c` 做只读独立 Review，基线为 `536962909963eaeeff7e94ff511f76f927652cd6`。读取 `doc/tasks/P14.md`、`doc/handoffs/P14-workbench.md`、工作区当前 P14 AC6 文档修订、设计基线 §3/§7、M2-C1 §6.4/§10、受影响前端源码及 `verification/P14/**`。重点复核 AC1–AC6、每条禁用项的 DOM 断言、G15 未发明、导出面板去路径投影、裁决 A 的 `m2res` 专用媒体边界、四处 payload、磁盘 SHA256 与证据 commit 包含性。不要修改文件或提交，不要把 GUI e2e、未复跑的 Core/Rust 或当前交付描述为已接受。按 `doc/templates/REVIEW.md` 给出合法结论与证据。

## 风险与遗留

最新外部 Review R2 的结论针对旧提交 `e99be4d`，为 `changes_requested`；F-05/F-06 与 AC6 文档/证据问题已修订，但新一轮独立 Review 尚未完成。本交付仍是 `in_review`，不表示已接受或集成。GUI e2e 未运行；资源清理未执行，`resource_closeout_status` 仍为 `pending`。
