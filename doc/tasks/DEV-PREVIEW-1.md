---
id: DEV-PREVIEW-1
title: 免安装本地预览通道（浏览器假数据 + Tauri 热更新）
kind: feature
governance_version: 3
status: done
approval: user_authorized_DEV_PREVIEW_1_S1_20261022
suggested_owner: Codex
owner: Codex
reviewer: spec_audit
depends_on: []
base_commit: d43d12189
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 8ac00b97b644cdf6dcfb3124c9099c6e994e8b22
delivery_head: 8ac00b97b644cdf6dcfb3124c9099c6e994e8b22
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/DEV-PREVIEW-1
allowed_paths:
  - apps/desktop/frontend/src/main.tsx
  - apps/desktop/frontend/src/dev/devMockBridge.ts
  - apps/desktop/src-tauri/tauri.dev.conf.json
  - apps/desktop/src-tauri/build.rs
  - tools/dev/dev-preview.ps1
  - doc/tasks/DEV-PREVIEW-1.md
  - doc/reviews/DEV-PREVIEW-1-8ac00b97b.md
  - doc/reviews/DEV-PREVIEW-1-p2-fa7f4e0c0.md
  - doc/handoffs/DEV-PREVIEW-1-8ac00b97b.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/DEV-PREVIEW-1/
created: 2026-10-22
---

# DEV-PREVIEW-1：免安装本地预览通道

## 来源与目标

来源：用户对 DEV-PREVIEW-1 的直接授权及 S1 修复决策。目标是提供修改后可立即查看效果的本地入口：A 档在普通浏览器中用假数据预览四页 UI；B 档在 Tauri 窗口中加载 Vite 并运行真实 Python Core，不生成 NSIS 安装包。修复增量 sidecar 构建可能被占位目录误判为成功的 P1。

## Acceptance Criteria

- [x] **AC1 浏览器假数据预览**：仅 DEV 且无真实 Tauri bridge 时安装 mock；真实桥不覆盖；只读命令使用最小假数据，其余拒绝并有角标。TypeScript 检查和前端测试通过。 <<MET>>
- [x] **AC2 桌面 dev 构建**：dev overlay 指向 Vite/HMR，使用 `bundle.resources: []`；启动器在 Cargo 调用期间设置并清除 `M2RC1_DEV_PREVIEW=1`，build script 跳过本地预览不需要的 sidecar 检查，且不创建占位目录。 <<MET>>
- [x] **AC3 生产构建语义**：未设置预览变量且 sidecar 缺失时，构建仍 fail-closed 并保留可诊断 panic；随后恢复 dev 构建成功。 <<MET>>
- [x] **AC4 冻结契约不变**：主 `tauri.conf.json`、命令 allowlist、ACL/capabilities、permissions 与 `build_sidecar.ps1` 均未修改；生产打包默认不加载 dev overlay。 <<MET>>
- [x] **AC5 集成和治理验证**：`npx tsc --noEmit`、`npx vitest run`、`pwsh -NoProfile -File tools/governance/check.ps1` 和 `git diff --check` 运行并通过；实际结果记于 Handoff。 <<MET>>

## 允许修改范围

仅 frontmatter `allowed_paths` 列出的四个预览实现文件、`build.rs` 的 dev-only sidecar 探针例外，以及本 Task 的 Review/Handoff/STATUS/TASK_LEDGER 登记；证据目录按项目协议声明。完整 B 档窗口烟测由 DSH 在固定提交上执行，不改代码。

## 禁止范围

不改打包流程；不改主 `apps/desktop/src-tauri/tauri.conf.json`；不引入依赖；不改产品行为、command allowlist、ACL、capabilities、permissions 或 IPC 契约；不处理 `apps/desktop/src-tauri/target` 历史产物；不触碰其他 Agent 的未提交文件；不启动 NSIS。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `npx tsc --noEmit` | `apps/desktop/frontend`，Node 22 | PASS，EXIT 0 | Handoff |
| AC1 | `npx vitest run` | `apps/desktop/frontend`，Node 22 | PASS，32 files / 327 tests，EXIT 0 | Handoff |
| AC2 | `cargo build --no-default-features`，设置预览变量并经 `TAURI_CONFIG` 加载 overlay | `apps/desktop/src-tauri` | PASS，EXIT 0 | Handoff |
| AC3 | 清除预览变量后重复 Cargo build，再恢复变量编译 | sidecar 缺失 | 反向检查预期 EXIT 101 且 panic 明确；恢复 EXIT 0 | Handoff |
| AC5 | `pwsh -NoProfile -File tools/governance/check.ps1`、`git diff --check` | 仓库根 | PASS，EXIT 0；治理输出在集成记录 | 本 Task 检查与 Handoff |
| 完整 B 档桌面窗口 | `pwsh -NoProfile -File tools/dev/dev-preview.ps1` | DSH 在固定提交上执行 | PASS：编译 3.37s、窗口渲染四页、真实 IPC + Python Core、HMR 立即生效、退出无残留；详见下方 DSH 记录 | 本地证据（`G:/CODEX/New Manga.workspace/dev-preview/shots/`，未入库） |

## 依赖、风险与阻塞

无硬依赖。Review 记录了三个非阻塞 P2：端口服务身份未验证、Vite 启动超时可能不清理、清理按当前端口 listener 可能杀错 Agent 进程。完整 B 档未由 Codex 本轮启动，按用户要求由 DSH 固定提交烟测。`tauri.dev.conf.json` 仅作为 dev overlay；误用于打包会改变 CSP/resources。

## 交付与运行记录

- 2026-10-22 / Codex：实现提交 `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22`（main）；仅 5 个代码路径。
- Handoff：[DEV-PREVIEW-1-8ac00b97b](../handoffs/DEV-PREVIEW-1-8ac00b97b.md)。
- Review：[DEV-PREVIEW-1-8ac00b97b](../reviews/DEV-PREVIEW-1-8ac00b97b.md)，`approved`，P1 清零，保留 P2。
- 完整 B 档窗口烟测：**DSH 已完成（PASS）**，见下方 DSH 记录。

## DSH 独立烟测记录（2026-10-22，固定代码提交 `8ac00b97b`）

执行者：DeepSeek Harness（独立验证，未修改本提交代码）。命令：`pwsh -NoProfile -File tools/dev/dev-preview.ps1`。

| 检查项 | 结果 |
|---|---|
| 编译（`M2RC1_DEV_PREVIEW=1` + `--config` dev overlay） | PASS，`Finished dev profile in 3.37s` |
| 占位目录风险（原 P1） | PASS，`target/core-sidecar/core-sidecar` 全程不存在，未创建占位 |
| 桌面窗口与四页 | PASS，`m2rc1-desktop.exe` 窗口 1180x890；书架页、工作台页真实渲染（截图 `shots/p1-fixed-window.png`） |
| 真实 IPC + Python Core | PASS，production allowlist 正常公告；隔离目录内 `catalog.sqlite`、`library.db` 由真实 Core 生成 |
| HMR（改完即见） | PASS，改 `tokens.ts` 的 `accent.primary` 蓝→红，未刷新未重启窗口立即变色（`shots/p1-fixed-hmr.png`）；随后已还原，`git status` 无残留 |
| 正常退出清理 | PASS，关闭窗口后脚本 `exit 0`，停 Vite、释放 5188、无遗留进程 |
| 生产语义反向验证 | PASS，未设 `M2RC1_DEV_PREVIEW` 时 `cargo build --no-default-features` 仍 `exit 101` 并输出 `missing sidecar bundle` 原诊断 |

结论：原 P1 修复真实有效，B 档在固定提交上端到端可用。4 项 P2（启动器进程/端口健壮性）仍为遗留，不影响本次验收。

## 遗留 P2 修复与独立验证（2026-10-22，ZCode 实现 + DSH 验证）

实现提交 `fa7f4e0c0`（仅 `tools/dev/dev-preview.ps1`，+114/−42）；独立 Review 见
[DEV-PREVIEW-1-p2-fa7f4e0c0](../reviews/DEV-PREVIEW-1-p2-fa7f4e0c0.md)（`approved`）。

| ID | 修复方式 | 独立实测 |
|---|---|---|
| R-001 | 只清理本次启动的进程树：PID + `StartTime` 核对一致才 `taskkill /T`，不按端口盲杀 | 白盒：伪 `StartTime` → 跳过且进程存活；真 `StartTime` → 树杀。B 档退出日志 `停止 Vite 进程树 (pid 692)` |
| R-002 | Vite 启动 + 90s 等待纳入主 `try/finally` | 假 `npm.cmd` 永不监听 → 91.9s 后 exit 1 且完成树清理，无 cmd/ping 残留 |
| R-003 | 删除 `-VitePort` 参数，改用 `Set-Variable -Option Constant` 固定 5188 | `-VitePort 5199` → exit 1，参数绑定失败，无启动动作 |
| R-004 | 复用端口前做 HTTP 身份校验（`/@vite/client` 200 + `/` 含 `/src/main.tsx`），未知服务 fail-closed | python 占位 5188 → exit 1 fail-closed；真 Vite → `-NoVite -ViteOnly` exit 0 并打印复用 |

B 档完整回归：编译 8.69s、窗口启动、production allowlist 正常、关闭后 5188 释放且无 node/cmd 残留、脚本 `exit 0`。
语法检查 `ERRCOUNT=0`，`git diff --check` 无输出。

### 启动器日志化（同日，`d003785b3`）

- `tools/dev/dev-preview.ps1`：把应用正常关闭导致的 Tauri 退出码 `-1 / 0xffffffff` 识别为正常结束（提示「应用窗口已关闭，预览正常结束」），不再显示为失败警告；其余非零退出码仍报「编译或启动失败」。
- 桌面启动器（`C:\Users\49745\Desktop\New Manga 本地预览.cmd`，仓外本地文件）改为带日志：`*>&1 | Tee-Object` 捕获全部输出流到 `G:\CODEX\New Manga.workspace\dev-preview\launcher-last.log`（UTF-8，每次运行覆盖），窗口头部提示 `0xffffffff` 属正常结束。
- 实测：日志 6149 字节、UTF-8 中文正常，含 dev-preview 提示行、cargo 警告、应用输出与「应用窗口已关闭…预览正常结束」收尾行；退出后 Vite 正常清理、5188 释放。

### WebView2 隔离与单实例保护（同日，`8209e04a3`）

真实故障（`launcher-last.log` 原文）：`WebView2 error: HRESULT(0x800700AA) "请求的资源在使用中"` 导致 `Failed to setup app` → exit 101；同时 `sqlite3.OperationalError: unable to open database file`。根因是上一实例被强制结束后的残留进程占用默认 WebView2 用户数据目录（`%LOCALAPPDATA%\com.newmanga.m2rc1.desktop\EBWebView`）与 SQLite 目录。

- `dev-preview.ps1` 设置 `WEBVIEW2_USER_DATA_FOLDER = <dataRoot>\webview2-udd`，dev 预览与正式版、其他实例彻底隔离。
- 新增单实例保护：检测到 `m2rc1-desktop` 正在运行即 fail-closed，明确提示先关闭现有窗口（避免 WebView2 0x800700AA / SQLite 锁冲突）。
- 实测：正常启动（新 UDF 自动创建 `EBWebView`）；应用运行中再次启动 → 1 秒内拒绝并给出中文说明；`CloseMainWindow` 优雅关闭后无 `core_service` 残留、5188 释放、Vite 树清理。

### 并发实例文件锁（同日，`2cc724e94`）

重复失败的根因判定为**并发启动窗口**：进程检测到 `m2rc1-desktop` 之前的瞬间即可通过，两个实例同时创建 WebView2 / 打开 SQLite 会互相报 `0x800700AA` 与 `unable to open database file`（日志中两者总是成对出现）。

- `dev-preview.ps1` 增加 `data/.dev-preview.lock` 独占文件锁（`FileShare.None`，进程退出由 OS 自动释放），并发实例在启动第一步即被拒绝，不再进入 Vite/编译/WebView2 阶段。
- 启动前清理「父进程已死」的本项目残留（`python -m bootstrap.core_service` / `infrastructure.resource_channel.host_bridge` 孤儿、使用本 UDF 的孤儿 `msedgewebview2`），实测强杀应用后 Core 子进程会自行退出，因此该清理为防御性措施。
- 实测：实例 A 运行时锁被持有；实例 B 1 秒内退出且 A 不受影响；A 优雅关闭后锁释放。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-1 | AC1 A 档 mock 与启动门 | `apps/desktop/frontend/src/main.tsx` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |
| E-2 | AC1 假桥白名单/拒绝 | `apps/desktop/frontend/src/dev/devMockBridge.ts` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |
| E-3 | AC2 dev overlay | `apps/desktop/src-tauri/tauri.dev.conf.json` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |
| E-4 | AC2/AC3 build.rs dev flag 与生产 panic | `apps/desktop/src-tauri/build.rs` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |
| E-5 | AC2 移除占位目录及环境变量清理 | `tools/dev/dev-preview.ps1` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |
| E-6 | AC1-AC5 测试/输出 | `doc/handoffs/DEV-PREVIEW-1-8ac00b97b.md` | - | `8a1e7af95e6cc6c7ae0ea51cd70efb630f8909e49e2cb42da17eb9bc5b4bdf43` | SOURCE_PIN |
| E-7 | 独立审查 | `doc/reviews/DEV-PREVIEW-1-8ac00b97b.md` | - | `96f52fc4555c5147298ad90c6bae2f1a76b5f1ff8035da01bf696371bd4cfabc` | SOURCE_PIN |
| E-8 | 冻结主配置、ACL 与打包脚本未变 | `apps/desktop/src-tauri/tauri.conf.json` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |
| E-9 | 冻结 build_sidecar 增量逻辑未变 | `packaging/m2ac5/build_sidecar.ps1` | `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` | - | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree / task-env / temp / artifact | `G:/CODEX/New Manga/apps/desktop/src-tauri/target`（既有共享 Cargo cache） | `NOT_APPLICABLE` | same location; preserved | - | 仅原位复用 Cargo build cache；未删除、迁移或归档；不处理历史 target 产物。预览隔离数据目录与桌面进程未启动。 |

## Closeout Record

- Closeout date / Codex：2026-10-22 / Codex。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`complete`。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：P2 启动器进程/端口风险留待专门 Task；完整 B 档由 DSH 在固定提交上烟测；均不影响 sidecar P1 修复验收。
- 当前指针清理：STATUS 仅增加最近完成记录；REBASELINE_PLAN 未改（Task 已终态且无 READY/Active 指针）；Task README 不在本次允许路径，未改；无 rolling checkpoint 更新。
