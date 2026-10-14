---
id: P02-NEW-TIME-X6-AC1-AC7
title: P02 新时点 AC1–AC7 当前版本验收
kind: verification
governance_version: 2
status: in_progress
approval: user_authorized_new_time_baseline_20261014
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [P02-NEW-TIME-BASELINE, P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW, P02-NEW-TIME-X6-BUILD-CARGO]
base_commit: 49d2a2f9c56462f5602b00ad4b824c5381abb1ab
branch: agent/zcode/P02-NEW-TIME-X6-AC1-AC7
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7
integration_commit: null
delivery_head: null
reviewed_head: null
review_decision: pending
integration_target: agent/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW
integration_status: not_started
dispatch_state: DISPATCHED_EXECUTION_BLOCKED_ENV
blocked_by: []
profile: ZCODE_PRIMARY
revisions: {implementation: 0, test: 1, evidence: 1}
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P02-NEW-TIME-X6-AC1-AC7
run_id: p02-newtime-ac-20261014-r1
---

# P02-NEW-TIME-X6-AC1-AC7：P02 新时点 AC1–AC7 当前版本验收

## 来源、准入与目标

本 Task 是 2026-10-14 新时点路径的独立产品验收，仅回答当前固定版本是否具备继续 X6、Build/Cargo 与 AC1–AC7 的准入资格。它不补齐、替代、关闭或改写旧 H1 / P2-1 结论及 13 项历史原始来源缺失记录。

产品验收合同来自 [P02 2026-10-14 新时点 AC1–AC7](P02.md#2026-10-14-p02-新时点准入路径独立于旧-h1--p2-1)。本 Task 固定以下执行对象：

- 产品源码基线：`49d2a2f9c56462f5602b00ad4b824c5381abb1ab`；Build Task 冻结的 tracked source manifest 与补充输入清单继续作为源码/依赖身份依据。
- 已通过 Build/Cargo 的可执行文件：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`，9,367,040 bytes，SHA-256=`92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`；其 packaged sidecar 在同目录 `resources/core-sidecar/`。启动前由 Codex 重新核验二进制与 sidecar manifest。
- Build/Cargo Gate：`P02-NEW-TIME-X6-BUILD-CARGO` 已集成，官方 convergence=`APPROVED`、`wait_external=false`。BC-AC5 仍为 `PARTIAL`；其中未知来源 Python cache 与未检查的 profile cache 均保留为非阻断 residual，未记为 PASS，Build Task 也不改记为 `done`。此 Gate 决定可释放本 Task，不宣称前述 residual 已消失。
- 唯一 RunId：`p02-newtime-ac-20261014-r1`。禁止重用基线、X6、post-run Review 或 Build/Cargo 的 RunId。

目标是在本机 Windows 上对已构建的 Tauri/WebView2 应用逐项执行 AC1–AC7，固定可复核证据与产品 findings。只读使用现有产物；不重建、不安装应用、不更改产品代码或产品行为。若真实 WebView、输入驱动、隔离数据或某项必需证据无法建立，按该 AC 记 `BLOCKED`，不得用浏览器、JSDOM、Vite、静态模型或 fake timer 冒充真实运行结果。

## Acceptance Criteria

- [ ] **AC1 真实 WebView2 harness**：从固定源码对应的现有 packaged binary 启动 Windows Tauri 窗口，证明交互发生于嵌入式 WebView2，而非 Vite/外部浏览器/JSDOM。记录 OS、WebView2 Runtime、源码与二进制 Hash、启动命令、进程/窗口身份、隔离测试数据和驱动；标明 mock 面。
- [ ] **AC2 导航与操作**：用真实鼠标和键盘操作 Console/Workbench、Workbench 页面选择、输入、按钮和状态；记录可见结果、焦点/可访问性状态和截图。预期行为缺失时登记 finding，不在本 Task 修复。
- [ ] **AC3 300ms quiet-period 与失效窗口**：真实 WebView2 连续输入/切换 page ID，分别观察 `resolve_page_resource` 与 `list_regions`；中间前缀不得提前读取；300ms 未到不得触发，到期后仅对最终 page ID 各触发一次；页面变化取消旧 timer，旧 page 迟到响应不得覆盖当前状态。记录单调时钟与可见结果。
- [ ] **AC4 写后刷新即时性**：在真实 WebView、默认 `resolveDebounceMs=300` / `regionDebounceMs=300` 下，对 retype、undo、restore 三种操作分别构造合成状态并判别写后刷新；逐项记录 write 返回与随后 `list_regions` 的次序/单调时钟，确认读回不再等待 300ms。允许 IPC/Core 明确标为 mock（`REAL_WEBVIEW_MOCK_IPC`），但不得声称验证了真实 Core/SQLite 持久化。三种操作均为必要覆盖；任一项不能安全或可靠执行时，该项记 `BLOCKED` 并阻止 Task 进入 `done`，不得用 `NOT_RUN` 满足 AC4。
- [ ] **AC5 键盘与焦点**：以真实按键检查选择/输入/按钮/对话框的 Tab、Shift+Tab、Enter/Space、Escape 及焦点位置。仅覆盖 P02 Workbench 操作面，不声称完成全应用 WCAG 审计；观察到的缺失只登记 finding。
- [ ] **AC6 F token / 对比度**：采集真实 WebView2 代表性状态的 computed foreground/background、F token 映射状态、算法和 contrast ratio。将 `token_mapping`（`MAPPED` / `UNMAPPED` / `NOT_APPLICABLE`）与 `contrast_result`（`PASS` / `FAIL` / `NOT_VERIFIABLE`）分开记录。只要实际前景、背景及必要的合成底色可确定，就必须计算 contrast ratio；token 未映射或 CSS fallback 不得跳过计算。只有无法确定实际合成背景时，ratio 才可为 `NOT_VERIFIABLE`，并附原因。按 UI/UX GUI design contract `7.2` / `9`：文本至少 4.5:1，禁用文字/非文本至少 3.0:1，状态不得仅靠颜色表达。不另定阈值、不改视觉样式。React 当前无浅色主题入口时记录 `NOT_APPLICABLE`。
- [ ] **AC7 固定证据与发现处置**：逐场景记录 PASS/FAIL/BLOCKED/NOT_RUN、真实/模拟层、命令、环境、源码/二进制 Hash、退出码、时序/颜色数据、截图/日志和逐项 skip 原因。产品缺口单独登记 finding 与建议后继路线；测试脚手架 Gate PASS 不等于产品 UI 质量 PASS。固定 delivery head 经 DSH 独立 Review、Codex 范围/验证/集成 Gate 后才可 `done`。

产品观察即使为 FAIL，也不授权 Owner 修复产品实现。所有产品缺口只记 finding，交 Codex 按严重度、依赖和新版 orchestrator 规则重算 DAG。

## 允许修改范围

- `apps/desktop/frontend/e2e/p02-new-time/**`：仅本 Task 新增的 WebView2 驱动、断言及采集代码；优先复用已安装运行时和现有协议，不改产品前端源码。
- `verification/P02-NEW-TIME-X6-AC1-AC7/**`：仅本 Task 的 synthetic fixtures、runner、截图、日志、命令/环境记录、哈希清单、findings、immutable evidence manifest 与 checkpoint。输入数据必须为 Task-local synthetic data。
- `doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md`：Owner 仅更新状态、运行结果、证据链接与交付指针；AC、基线、依赖、范围和禁止项不得自行改动。
- `doc/handoffs/P02-NEW-TIME-X6-AC1-AC7-*.md`：本 Task Handoff。
- 非 Git 运行时数据、缓存与临时目录仅可写入 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/` 和 `G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6-AC1-AC7/` 下的本 Task 专属目录；真实截图与 canonical 证据须复制到本 Task 的 `verification/` 路径并固定 hash。

## 禁止范围与用户数据保护

- 不改产品实现/共享契约/Schema/依赖/lockfile/构建脚本：包括 `apps/desktop/frontend/src/**`、`apps/desktop/src-tauri/src/**`、Python Core、`package.json`、lockfile、Cargo 配置、视觉 token、debounce 与 IPC 契约；不得添加依赖。
- 不重跑 npm、Cargo、Tauri、PyInstaller 构建；不安装应用或启动 NSIS installer；不写入 Build worktree、Build artifact 或现有 sidecar。仅从上方固定 binary 和 `resources/core-sidecar/` 读取、启动。
- 不连接、读取、导入或修改用户漫画库、用户数据库、人工编辑、Lock、current/pinned Revision、凭据或生产 app data。执行时显式隔离 `APPDATA`、`LOCALAPPDATA`、`NEWMANGA_DATA_ROOT`、`M2RC1_DERIVED_ROOT`、`M2RC1_MANAGED_ROOT`、`M2RC2_CATALOG_DB`、`M2RC1_FIXTURES`、`M2AC1_RESULTS_OUT`、`TEMP`、`TMP` 和所有语言/工具缓存至 Task env；仅使用新建的 synthetic fixture 与数据目录。`M2AC1_TEST_MODE=1` 可按本 Task 进行显式验收配置；不得设置 `M2RC1_PROBE_OUT`。
- 不检查或更改 OS/ACL/registry、用户 profile 或无关缓存；不启动 Windows Sandbox；本 Task 使用已裁决的本机 Windows 验收环境，不声称具有虚拟机隔离。
- 不修改旧 H1、P2-1、13 项缺失记录及其历史 Task/Review/evidence。不得将 Legacy PySide6/QML、Vite、外部浏览器、JSDOM、SSR、静态 AST、mock-only 或 fake timers 作为真实 WebView2 证据。
- 不因发现产品问题扩大 Task。需要改产品代码、共享契约、Schema、依赖或允许路径时，停止该修改并交 Codex 登记 scope delta 与 DAG 重新规划。

## 证据落盘规则

1. 每一命令/场景保存原始命令、shell 与版本、工作目录、固定源码与 binary hash、环境变量清单（不含 secret）、stdout、stderr、退出码和单调计时数据；每个 skip 单独写明 AC、原因、证据和恢复条件。
2. 截图须来自真实 Tauri/WebView2 窗口，记录时间、场景、窗口身份和对应日志；不能由截图单独推断 WebView2 身份。
3. 运行数据与 fixture 仅为 synthetic，且从 Task env 的独立根读取/写入。启动前证明上述路径不存在用户数据；发现来源不明内容时不覆盖，另用空的 Task-local 目录或将场景记 `BLOCKED`。
4. 运行证据放入 `verification/P02-NEW-TIME-X6-AC1-AC7/`；原始输出可同时保留在 workspace agent-output，但外部目录不能作为唯一证据来源。
5. Owner 完成后，Codex 冻结 delivery head 与证据集合并用官方 evidence-manifest generator 生成/验证 immutable manifest；manifest 自身不得自引用。Review、adjudication、integrated head 和 post-integration check 均记录精确 commit/hash。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| Preflight / release | 校验 Task、依赖门、binary/sidecar hashes、write scope、Task env 空白状态；运行 official `preflight-agent.py` live PREFLIGHT 与 ZCode availability probe | 本 Task 已登记；Build convergence approved；独立 worktree 已创建；无其他 Owner 写入 | PASS：EXE hash 匹配；packaged sidecar copy 与冻结 5,610-file manifest 比对 PASS（5,610 / 5,610，1,296,373,783 bytes，无缺失/多余/hash mismatch）；Task env=0 items。ZCode CLI 0.16.9 live probe 返回有效回复与 session ID；official AGENT_PREFLIGHT r1 在 HEAD=c7b791ecfff4276e0a42ed57de3f920603067a5f 返回 overall=PASS、dispatch_allowed=true、worktree 0 dirty entries。Task 证据/状态更新后需再对最终冻结 HEAD 运行 live PREFLIGHT；尚未启动应用 | `verification/P02-NEW-TIME-X6-AC1-AC7/preflight/sidecar-resource-copy.stdout.json`、`agent-preflight-r2/stdout.json`、`zcode-availability-r2/probe.stdout.jsonl`；各自 command/environment/stderr/exit 同目录 |
| AC1 runtime identity | 启动固定 packaged exe；采集 WebView2 host/runtime identity、process/window identity、source/binary pins | 本机 Windows；isolated synthetic env；不重建或安装 | BLOCKED（run-r1）：Owner 会话 Bash 无权限客户端，任何进程执行命令（node/python/powershell/certutil）与 git 写命令均被 "No permission client configured" 拒绝（子代理复现一致）；固定 EXE 未启动，run-r1 保持 0 items。EXE SHA-256 只读复算匹配 pin。驱动已交付：`apps/desktop/frontend/e2e/p02-new-time/ac1-identity.mjs` | `verification/P02-NEW-TIME-X6-AC1-AC7/execution-blocked/execution-blocker-evidence.json` |
| AC2 navigation / operation | 在真实 Workbench 窗口执行鼠标/键盘导航、输入与按钮状态操作 | AC1 PASS；真实 WebView2 窗口 | BLOCKED（同上，依赖真实窗口）。驱动已交付：`ac2-navigation.mjs` | 同上 blocker evidence；驱动在 e2e 目录 |
| AC3 debounce / stale response | 使用真实页面和单调时钟驱动连续输入、page ID 切换及延迟响应观察 | AC1 PASS；不以 fake timer 作为产品行为证据 | BLOCKED（同上）。驱动已交付：`ac3-debounce.mjs`（Phase A 真实 IPC 观察；Phase B 仅 invoke 边界 mock 迟到响应并标注 MOCK_IPC；时钟=页面 performance.now()） | 同上 |
| AC4 write/read freshness | 对 retype、undo、restore 分别记录 write return 与 list_regions readback；清晰标注 IPC/Core mock 边界 | AC1 PASS；synthetic state；三项均执行，否则 BLOCKED | BLOCKED（同上；三项 retype/undo/restore 均未执行，不折衷为 NOT_RUN）。驱动已交付：`ac4-write-refresh.mjs`（REAL_WEBVIEW_MOCK_IPC，默认 300ms debounce 下测写后即时 readback） | 同上 |
| AC5 keyboard / focus | 真实按键序列与 focus/active element 采集 | AC1 PASS；真实窗口输入 | BLOCKED（同上）。驱动已交付：`ac5-keyboard.mjs` | 同上 |
| AC6 computed colors | 真实 DOM computed styles、token mapping、实际颜色/背景、WCAG ratio 和阈值 | AC1 PASS；颜色可采集；不得改样式 | BLOCKED（同上）。驱动已交付：`ac6-contrast.mjs`（对照 `doc/design/tokens-cand-f.json`，token_mapping/contrast_result 分列，浅色入口缺席记 NOT_APPLICABLE） | 同上 |
| AC7 adjudication | 固定证据 manifest；DSH bounded read-only Review；Codex official result/convergence、集成及验证 | AC1–AC6 状态齐全；delivery head 固定 | NOT_RUN：AC1–AC6 无逐场景证据可裁决；DSH 独立 Review 未发生；delivery head 未固定（会话无 git 写权限） | 同上 |

以上 `PLANNED` / `NOT_RUN` 不是 PASS；Task 建立与 preflight 不会预先判定产品行为。

## 依赖、Review 与阻塞

- 前置节点：`P02-NEW-TIME-BASELINE=DONE`、`P02-NEW-TIME-X6=APPROVED`、`P02-NEW-TIME-X6-POSTRUN-REVIEW=APPROVED`、`P02-NEW-TIME-X6-BUILD-CARGO=INTEGRATED + official convergence APPROVED`。Build 的 BC-AC5=`PARTIAL` 与保留 residual 必须继续在 Plan、Status 和本 Task 可见；不得将其当作 PASS，也不得阻止本 Task 在官方批准范围内启动。
- 开始运行的硬条件：Codex 已冻结 Task/Plan/Status，ZCode availability probe 与 live AGENT_PREFLIGHT 均通过，isolated worktree 和 Task env 已验证，binary/sidecar hashes 匹配，synthetic data 为空且 source pinned。任一失败时维持 `blocked` / `NOT_RUN` 并记录恢复条件；不自动升级为 `BLOCKED_WAITING_EXTERNAL_DECISION`。
- ZCode 为主要执行 Owner；仅当 fresh probe 证明 ZCode 不可用时按项目故障转移顺序交由 Antigravity，并记录原因、probe artifact、branch/worktree 与新的 preflight。Qoder 不参与。
- DeepSeek Harness 在固定 delivery head 上独立 Review，Codex 重算 evidence pins、scope 与 AC 结论并集成。Finding 按 `multi-agent-project-orchestrator` 的 I1/I2、bounded review、follow-up/resolution lineage 与 DAG replanning 处理；最多 I1、I2 两轮，禁止 I3 与无限返修。P0/P1/P2 blocker 未关闭不得批准；可安全关闭的非阻断 E 文档 finding 按协议处置；P3/P4 明确入 backlog，不为追求零 finding 无界重开。产品实现修复需 Codex 另立依赖 Task。
- AC4 三项 retype/undo/restore 均是必需条件；任一被阻断则 Task 不能 `done`。旧 H1 / P2-1 状态不属于本 Task 的输入或验收范围。

## 交付与运行记录

- 2026-10-14 run-r1（RunId=`p02-newtime-ac-20261014-r1`，Owner=ZCode）：派发会话 Bash 执行通道不可用（无权限客户端），AC1–AC6 全部 `BLOCKED`、AC7 `NOT_RUN`；无产品 finding；无任何真实启动，run-r1 目录保持空白。逐字错误、子代理复现与恢复条件：`verification/P02-NEW-TIME-X6-AC1-AC7/execution-blocked/execution-blocker-evidence.json`；findings：同目录 `findings.md`。零依赖 e2e 驱动套件（AC1–AC6 + lib + README）已交付于 `apps/desktop/frontend/e2e/p02-new-time/`，是重试会话的直接执行入口。固定 EXE SHA-256 只读复算匹配（92AC…13FD / 9,367,040 bytes）。
- Owner Handoff：`doc/handoffs/P02-NEW-TIME-X6-AC1-AC7-zcode-r1-20261014.md`（本文件同 commit；如 git 写通道不可用则未提交，见 Handoff dirty-state 说明）。
- 独立 Review：尚无；Reviewer=DeepSeek Harness，待 AC1–AC6 真实证据存在后再执行。
- Codex adjudication / integration / post-integration check：尚无。
- 当前状态：`in_progress / DISPATCHED_EXECUTION_BLOCKED_ENV`；产品 AC1–AC6=`BLOCKED`、AC7=`NOT_RUN`；恢复条件=以允许进程 spawn 与 git 写的会话重派本 Task（其余冻结条件不变）。
