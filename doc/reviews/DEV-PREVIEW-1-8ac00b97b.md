---
task_id: DEV-PREVIEW-1
reviewer: spec_audit (independent read-only reviewer)
author: Codex (DSH implementation integrated with S1 remediation)
base_commit: d43d12189
reviewed_head: 8ac00b97b644cdf6dcfb3124c9099c6e994e8b22
decision: approved
---

# Review：DEV-PREVIEW-1

## 范围与依据

固定审查 `d43d12189..8ac00b97b644cdf6dcfb3124c9099c6e994e8b22`，覆盖 A 档浏览器假数据预览、B 档本地 dev 配置及 S1 sidecar 探针修复。依据为用户授权的 DEV-PREVIEW-1 范围、`doc/09_COLLABORATION.md`、Task 文件和当前实现。未运行完整 `cargo tauri dev` / `dev-preview.ps1`，按用户要求留给 DSH 在提交后实测。

## Architecture

- `main.tsx:11-14` 仅在 `import.meta.env.DEV` 安装垫片；`devMockBridge.ts:72-74` 发现真实 `window.__TAURI__.core.invoke` 时直接返回；只读命令由 `EMPTY_READS` 放行，其余拒绝并显示假数据角标。它不改变真实 IPC 命令表或产品行为。
- `tauri.dev.conf.json` 仅由启动脚本显式传入 `--config`，只为 localhost Vite/HMR 放宽 CSP，并以 `bundle.resources: []` 覆盖 dev 构建资源映射。主 `tauri.conf.json` 字节未改。
- `build.rs:2,20-35` 仅当显式 `M2RC1_DEV_PREVIEW=1` 才跳过 sidecar 目录探针；正常构建仍保留原诊断 panic。`command_allowlist`、capabilities、permissions 和 `packaging/m2ac5/build_sidecar.ps1` 均未改。
- `dev-preview.ps1:133-144` 在 Cargo 子进程调用期间设置并于 `finally` 清除预览变量；占位目录创建/清理已整体删除，不能再触发 `build_sidecar.ps1:172-179` 的“目录存在即短路”。
- 生产边界：默认打包不加载 `tauri.dev.conf.json` 且不设置预览变量，主配置与 sidecar 校验保持原语义。显式将 dev 配置用于打包属于误用，会清空资源并放宽 CSP，启动器只用于 `cargo tauri dev`。

## Verification

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| dev Cargo build | `cargo build --no-default-features`，设置 `M2RC1_DEV_PREVIEW=1` 并经 `TAURI_CONFIG` 加载 dev overlay | Windows PowerShell / `8ac00b97b` | PASS，EXIT 0 | Handoff 原始输出 |
| 生产语义反向检查 | 清除 `M2RC1_DEV_PREVIEW` 后运行同一 Cargo 命令 | sidecar 不存在 / `8ac00b97b` | PASS：按预期 EXIT 101，输出 `missing sidecar bundle` 和原修复指引 | Handoff 原始输出 |
| dev Cargo 恢复 | 重新设置变量运行 Cargo 命令 | Windows PowerShell / `8ac00b97b` | PASS，EXIT 0 | Handoff 原始输出 |
| TypeScript | `npx tsc --noEmit` | Node 22 / `8ac00b97b` | PASS，EXIT 0 | Handoff 原始输出 |
| 前端测试 | `npx vitest run` | Node 22 / `8ac00b97b` | PASS：32 files、327 tests | Handoff 原始输出 |
| Task 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/DEV-PREVIEW-1.md` | 当前工作区 Task 文档 | PASS（2 warnings） | Handoff 原始输出 |
| 仓库治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | 当前工作区 | PASS（3 warnings） | Handoff 原始输出 |
| whitespace | `git diff --check` | 当前工作区 | PASS，EXIT 0 | 命令输出 |
| 完整桌面 B 档 | `cargo tauri dev` / `dev-preview.ps1` | 用户禁止本轮运行 | NOT_RUN；交 DSH 提交后测试 | Handoff 下一步指令 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | `tools/dev/dev-preview.ps1:151-159` | 清理时按端口重新查询并强杀 listener；若本脚本启动的 Vite 已退出且其他 Agent 接管端口，会误杀对方进程。 | 静态检查清理逻辑；本轮按要求未运行脚本。 | 记录并只清理本次启动进程树及其 PID/创建时间匹配的子进程。 | deferred；不阻塞 S1；后续专门修复 |
| R-002 | P2 | `tools/dev/dev-preview.ps1:106-114,118` | Vite 启动与等待发生在最外层 `try/finally` 前；等待超时抛出后不进入清理块，可能遗留进程。 | 静态检查控制流；本轮未运行脚本。 | 将启动/等待置于同一 `try/finally` 生命周期。 | deferred；不阻塞 S1；后续专门修复 |
| R-003 | P2 | `tools/dev/dev-preview.ps1:26,107` | `VitePort` 可指定非 5188，但 npm/Vite 配置与 Tauri `devUrl` 固定为 5188，参数会导致等错端口或超时。 | 静态检查参数、启动命令和固定配置。 | 删除参数或限制为 5188。 | deferred；不阻塞 S1；后续专门修复 |
| R-004 | P2 | `tools/dev/dev-preview.ps1:90-97` | 仅凭端口监听状态便复用服务，可能把其他应用的页面载入带真实 IPC 的 Tauri 窗口。 | 静态检查端口探测逻辑；本轮未运行脚本。 | 校验服务来源/内容，或端口由未知服务占用时 fail-closed。 | deferred；不阻塞 S1；后续专门修复 |

在记录范围内未发现 P1。S1 四项均满足；剩余 P2 是预览启动器既有的进程/端口健壮性风险，不导致 sidecar 增量构建误判，不污染生产配置或 ACL。`cargo tauri dev` 未运行是用户明确要求的检查边界，已安排 DSH 后续实测；因此批准仅覆盖固定代码提交及上述已运行验证。

## 结论与复审

**approved**，接受固定 head `8ac00b97b644cdf6dcfb3124c9099c6e994e8b22` 集成。原 P1 已消除；生产缺 sidecar 的失败语义经反向构建复核。P2 遗留项已列明并需后续单独处理；完整 B 档桌面窗口验证由 DSH 在该提交上执行。
