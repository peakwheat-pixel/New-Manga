---
task_id: DEV-PREVIEW-1
reviewer: dsh (独立验证：静态审查 + 行为实测)
author: ZCode（R-001..R-004 实现）, DSH（验证证据）
base_commit: 835d552be
reviewed_head: fa7f4e0c0
decision: approved
---

# Review：DEV-PREVIEW-1 遗留 P2 修复（ZCode 实现，DSH 独立验证）

## 范围

`835d552be..fa7f4e0c0`，唯一改动 `tools/dev/dev-preview.ps1`（+114 / −42，234 行），目标是关闭
`doc/reviews/DEV-PREVIEW-1-8ac00b97b.md` Findings 表中的 R-001..R-004。未触碰 `build.rs`、主
`tauri.conf.json`、`tauri.dev.conf.json`、产品前端代码、`packaging/m2ac5/build_sidecar.ps1`、`doc/**`（本 Review 与 Task 记录除外）。

## 逐项结论

| ID | 原问题 | 修复方式 | 独立验证证据 | 结论 |
|---|---|---|---|---|
| R-001 | 清理按端口反查 listener 强杀，可能误杀接管端口的其他 Agent 进程 | 新增 `Stop-LaunchedTree`：记录本次启动 cmd 的 PID + `StartTime`，清理时二者一致才 `taskkill /PID /T /F`；不匹配则警告并跳过（宁遗留勿误杀） | 白盒：传入伪 `StartTime` → 进程存活且打印不匹配警告；传入真实 `StartTime` → 进程树被清。B 档回归日志 `停止 Vite 进程树 (pid 692)`，5188 释放，无 node/cmd 残留 | 关闭 |
| R-002 | Vite 启动/等待位于 `try/finally` 之外，超时抛错会遗留进程 | 主 `try` 上移至 Vite 段之前，启动 + 90s 就绪等待纳入同一生命周期；以 `$viteProcess` 非空判断是否清理 | 用假 `npm.cmd`（永不监听端口）实测：91.9s 后 exit 1，日志含 `停止 Vite 进程树 (pid 46940)`，无 cmd/ping 残留，5188 空闲 | 关闭 |
| R-003 | `-VitePort` 参数与 `vite.config.ts`(strictPort 5188)、`tauri.dev.conf.json`(devUrl 5188) 不一致 | 删除参数，改为 `Set-Variable -Option Constant` 固定 5188，注释钉住三处一致 | 传 `-VitePort 5199` → exit 1，`找不到与参数名称 'VitePort' 匹配的参数`，无任何启动动作 | 关闭 |
| R-004 | 端口复用只判断「有人监听」，可能把其它应用页面装进带真实 IPC 的窗口 | 新增 `Test-OurVite`（`GET /@vite/client` 200 且 `GET /` HTML 含 `/src/main.tsx`，双栈探测、`-NoProxy`）+ `Assert-ReusableVite`（身份不明 fail-closed，报错含占用 pid/进程名与排查命令） | 负向：`python -m http.server` 占 5188 → `-ViteOnly` exit 1，throw 于 `dev-preview.ps1:95`（fail-closed 分支）；正向：真 Vite 在跑时 `-NoVite -ViteOnly` → exit 0，打印 `复用已运行的 Vite (5188)` | 关闭 |

## 独立验证矩阵（DSH 实跑）

| 项 | 命令/方法 | 结果 |
|---|---|---|
| 改动面 | `git status --porcelain -- tools/dev/dev-preview.ps1` | 仅该文件 `M` |
| 空白/行尾 | `git diff --check` | 无输出 |
| 语法 | `[Parser]::ParseFile(...)` | `ERRCOUNT=0`，234 行 |
| R-003 | `-VitePort 5199` | exit 1，参数绑定失败 |
| R-004 负向 | python 占位 5188 + `-ViteOnly` | exit 1，fail-closed |
| R-004 正向 | 真 Vite + `-NoVite -ViteOnly` | exit 0，复用成功 |
| R-001 白盒 | 伪/真 `StartTime` 对比 | 伪 → 存活；真 → 树杀 |
| R-002 | 假 npm 永不监听 | 91.9s → exit 1 + 清理，无残留 |
| B 档回归 | `pwsh -NoProfile -File tools/dev/dev-preview.ps1` | 编译 8.69s、窗口启动、production allowlist 正常、关闭后清理且 5188 释放、exit 0 |

## Findings

未发现 P1/P2。P3（不影响验收，记录备查）：

- `Test-OurVite` 的判据 2 与 `apps/desktop/frontend/index.html` 的 `/src/main.tsx` 字面值耦合，代码注释已标注「改动入口路径时同步这里」。
- `taskkill` 使用 `$env:SystemRoot\System32\taskkill.exe` 绝对路径（防 PATH 劫持）。
- 自动启动分支只等端口就绪、未做 HTTP 就绪校验，首次页面加载可能短暂 404 后由 HMR 恢复；与修复前行为一致，非回归。
- ZCode 侧 CLI 的 Bash 工具在本机不可用（`No permission client configured for Bash`），故其无法自验语法与 git 状态；上述验证均由 DSH 补跑。

## 结论

**approved**。R-001..R-004 全部关闭；`-ViteOnly` / `-NoVite` / 默认 B 档三个入口语义保持不变；生产构建与打包路径未被触碰。建议后续仅在启动器再变更时重跑本 Review 的验证矩阵。
