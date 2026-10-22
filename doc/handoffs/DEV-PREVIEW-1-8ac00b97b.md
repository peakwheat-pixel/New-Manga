---
task_id: DEV-PREVIEW-1
author: Codex
recipient: Codex
base_commit: d43d12189
delivery_head: 8ac00b97b644cdf6dcfb3124c9099c6e994e8b22
status: delivered
---

# Handoff：DEV-PREVIEW-1

## 交付结果

已提交 `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22`，仅包含本任务允许的五个实现路径：

- `apps/desktop/frontend/src/main.tsx`
- `apps/desktop/frontend/src/dev/devMockBridge.ts`
- `apps/desktop/src-tauri/tauri.dev.conf.json`
- `apps/desktop/src-tauri/build.rs`
- `tools/dev/dev-preview.ps1`

S1 删除真实 sidecar 占位目录创建/清理；本地 `cargo tauri dev` 明确设置并清除 `M2RC1_DEV_PREVIEW=1`；`build.rs` 对 dev preview 跳过 sidecar 目录探针并声明环境变量变更触发重跑；dev overlay 用 `bundle.resources: []` 清空开发构建的 sidecar 资源。未改主 `tauri.conf.json`、ACL、permissions 或打包脚本。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2：dev Cargo build | `TAURI_CONFIG=(Get-Content -Raw tauri.dev.conf.json)`、`M2RC1_DEV_PREVIEW=1` 后执行 `cargo build --no-default-features` | PowerShell，`apps/desktop/src-tauri`，`8ac00b97b` | PASS，EXIT 0 | 下方原始输出尾部 |
| AC3：生产语义反向检查 | 清除 `M2RC1_DEV_PREVIEW` 后执行同一 `cargo build --no-default-features` | sidecar 目录缺失，`8ac00b97b` | PASS：预期退出 101，保留 `missing sidecar bundle` 可诊断 panic | 下方原始输出 |
| AC2：dev build 恢复 | 再设 `M2RC1_DEV_PREVIEW=1` 并执行同一 Cargo 命令 | PowerShell，`8ac00b97b` | PASS，EXIT 0 | 下方原始输出尾部 |
| AC1：类型检查 | `npx tsc --noEmit` | Node 22，frontend，`8ac00b97b` | PASS，EXIT 0 | 下方原始输出 |
| AC1：前端测试 | `npx vitest run` | Node 22，frontend，`8ac00b97b` | PASS：32 files / 327 tests，EXIT 0 | 下方原始输出尾部 |
| AC5：Task 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/DEV-PREVIEW-1.md` | 仓库根，当前 Task 文档 | PASS，2 warnings | 下方原始输出 |
| AC5：仓库治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根 | PASS，3 warnings | 下方原始输出 |
| AC5：whitespace 检查 | `git diff --check` | 仓库根 | PASS，EXIT 0 | 下方命令结果 |
| 完整 B 档桌面烟测 | `cargo tauri dev` / `tools/dev/dev-preview.ps1` | 本轮按用户要求不启动窗口/不占用 5188 | NOT_RUN，待 DSH 在提交后完成 | 无 |

关键原始输出（成功编译只展示实际捕获的末尾；反向验证为完整错误输出）：

```text
warning: `m2rc1-desktop` (bin "m2rc1-desktop") generated 8 warnings (run `cargo fix --bin "m2rc1-desktop" -p m2rc1-desktop` to apply 1 suggestion)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.37s
DEV_BUILD_EXIT=0
```

```text
   Compiling m2rc1-desktop v0.1.0 (G:\CODEX\New Manga\apps\desktop\src-tauri)
error: failed to run custom build command for `m2rc1-desktop v0.1.0 (G:\CODEX\New Manga\apps\desktop\src-tauri)`

Caused by:
  process didn't exit successfully: `G:\CODEX\New Manga\apps\desktop\src-tauri\target\debug\build\m2rc1-desktop-b5b60bae6b09a2b3\build-script-build` (exit code: 101)
  --- stdout
  cargo:rerun-if-env-changed=M2RC1_DEV_PREVIEW

  --- stderr

  thread 'main' (41888) panicked at build.rs:27:13:
  missing sidecar bundle: G:\CODEX\New Manga\apps\desktop\src-tauri\target\core-sidecar\core-sidecar does not exist (gitignored build artifact, absent on a fresh checkout).
  Fix: run `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1` from the repository root (add -Force to rebuild an existing bundle).
  See packaging/m2ac5/README.md (fresh checkout section) for the full setup.
  note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
PRODUCTION_SEMANTICS_CARGO_BUILD_EXIT=101
```

```text
warning: `m2rc1-desktop` (bin "m2rc1-desktop") generated 8 warnings (run `cargo fix --bin "m2rc1-desktop" -p m2rc1-desktop` to apply 1 suggestion)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 3.43s
DEV_BUILD_RECOVERY_EXIT=0
```

```text
--- npx tsc --noEmit
npm notice run m2rc1-frontend@0.1.0 npx
npm notice run tsc --noEmit
TSC_EXIT=0
```

```text
 Test Files  32 passed (32)
      Tests  327 passed (327)
   Start at  17:22:57
   Duration  2.86s (transform 3.25s, setup 0ms, collect 23.21s, tests 5.86s, environment 5ms, prepare 6.43s)
VITEST_EXIT=0
```

```text
--- Task-scoped governance check
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\DEV-PREVIEW-1.md
WARN: 存在 1 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3163 bytes / 30 lines
Governance check: PASS (2 warnings)
TASK_GOVERNANCE_EXIT=0
--- Repository governance check
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\V1-RELEASE-SIGNING-1.md
WARN: 存在 1 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3163 bytes / 30 lines
WARN: 当前 Task 是 lifecycle v1；保留其原状态与证据，不强制回填旧 Task。
Governance check: PASS (3 warnings)
GOVERNANCE_EXIT=0
--- git diff --check
DIFF_CHECK_EXIT=0
```

完整 B 档未运行。桌面构建及窗口渲染仍由 DSH 按下方交接命令完成；Cargo 反向检查确认生产环境未设置变量时仍因缺少 sidecar 失败，随后 dev 环境构建已恢复成功。

## 接收方式

- 分支/worktree：`main` / `G:/CODEX/New Manga`。
- 固定实现 head：`8ac00b97b644cdf6dcfb3124c9099c6e994e8b22`。
- dev 配置只经 `cargo tauri dev --config apps/desktop/src-tauri/tauri.dev.conf.json` 加载；完整启动器为 `pwsh -NoProfile -File tools/dev/dev-preview.ps1`。
- 本轮没有启动服务或窗口；未触碰其他未提交文件。共享 `apps/desktop/src-tauri/target` Cargo cache 保留在原位。

## 下一任务建议

- Task ID / 标题：DEV-PREVIEW-1 提交后 B 档烟测
- 推荐 Agent / Reviewer：DSH 执行；Codex 复核结果。
- 推荐原因与前置依赖：用户已指定 DSH 在收到提交后验证完整 B 档；当前 review 未运行桌面窗口。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `main`，固定 head `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22`；worktree 已存在。
- 允许修改路径：无；只运行现有预览入口并记录结果。代码修复需先由 Codex 另行授权。
- 禁止范围与新增授权条件：不修改其它 Agent 文件；不运行打包/NSIS；不清理 sidecar 或 Cargo 历史产物；不使用 `git add -A` 等宽泛暂存。
- 交付物：窗口截图、启动/退出日志、Vite/HMR 结果、隔离数据根确认、清理结果及精确 commit 引用。
- 验证命令、环境与完成 Gate：在 `apps/desktop/src-tauri` 用 `pwsh -NoProfile -File tools/dev/dev-preview.ps1` 启动；验证四页加载、Python Core 真实启动、HMR 可见、隔离数据目录有效；正常关闭后确认无占位 sidecar 目录、环境变量已清除；记录实际退出码。另记录 `VitePort` 复用/进程所有权 P2，不进行范围外修复。
- 可直接转发给 Agent 的指令：`请在 main 上固定 8ac00b97b644cdf6dcfb3124c9099c6e994e8b22，只读执行 pwsh -NoProfile -File tools/dev/dev-preview.ps1 的完整 B 档烟测；不要改文件或暂存/提交。记录四页渲染、Python Core、HMR、隔离数据目录、正常退出清理和实际日志/截图。启动前检查 5188 是否由预期 Vite 服务占用；如所有权不明确或启动超时，停止并报告，不要杀终止其他进程。完成后返回命令、环境、退出码、截图路径和风险。`

## 风险与遗留

- 独立 Review `doc/reviews/DEV-PREVIEW-1-8ac00b97b.md` 接受 S1；剩余 P2 为端口身份/固定端口、超时清理和可能杀错 listener，已转后续独立修复处理。
- `tauri.dev.conf.json` 是本地 dev overlay；误用于打包会放宽 CSP 并清空 bundle resources。默认打包未加载它，主配置字节未变。
- 回滚实现：`git revert 8ac00b97b644cdf6dcfb3124c9099c6e994e8b22`；保留当前工作区其他未提交内容。
