# GUI 插件沙箱冒烟（手工，已暂停）

- 日期：2026-10-23
- 环境：`tools/dev/dev-preview.ps1`（Tauri dev，隔离数据根 `G:\CODEX\New Manga.workspace\dev-preview\data`），commit 基线 `d79e1a48` 之后的工作区。
- 状态：**paused**（用户 2026-10-23 指示：手工 GUI 检查太慢、占用鼠标、消耗 token → 后续改用自建检查工具；本文件保存已获得的证据）。

## 已完成（截图证据）

| 证据 | 内容 |
|---|---|
| [plugins-page-2.png](plugins-page-2.png) | 设置 → Plugin/Hooks：`bad-permissions` 拒绝加载（`PLUGIN_PERMISSIONS_UNSUPPORTED: this release only enforces: network; rejected: files_read`）；`Demo Detect Plugin`、`GUI Net Probe`（权限徽标「网络」）、`GUI Net No-Perm`、`GUI Sandbox FS Probe`（「无权限」）已启用；审计列表（加载成功/拒绝加载/已启用）；安全说明全文（AppContainer + Job Object、只读例外、每插件独立容器、最小 env、fail-closed、仅 network 可强制）。 |
| [workbench-run.png](workbench-run.png) | 真实导入页面（`long-strip-01.png`，ActiveBook/Chapter 1）并点击「启动」→ Run `completed_with_failures`（检测 failed，dev 数据根无检测模型权重），工作台阶段状态可见。 |

## 已执行的 GUI 操作（可复现）

1. 启动 dev-preview（Vite 5188 + Tauri dev 窗口）。
2. 向隔离数据根 `data-root/plugins/` 放入 4 个插件：`gui-sandbox-fs`（after_detect，尝试读 `C:\Windows\win.ini`）、`gui-net-probe`（`permissions: ["network"]`，连接 1.1.1.1:443）、`gui-net-none`（无权限对照）、`bad-permissions`（已存在）。
3. 设置 → Plugin/Hooks：确认加载/拒绝/权限徽标；启用 3 个新插件（审计出现「已启用」）。
4. 书架 → ActiveBook → 新建章节 `Chapter 1` → 导入 `long-strip-01.png`（1 页）→ 阅读器显示页面 → 工作台选章节 → 「启动」全章翻译。
5. Run 结果：检测 failed（缺模型权重），后续阶段 pending；插件 `after_detect` 未被调用（审计无 `hook_invoked`）。

## 未完成 / 结论

- **未完成**：GUI 内真实触发插件 Hook（`before_detect`/`after_detect`）并观察沙箱行为与审计，需要 dev 数据根具备检测模型权重（属环境配置，不是功能缺失）。
- **替代证据（更强）**：沙箱执行路径已由真实 AppContainer 测试覆盖——
  - `verification/PLUGIN-RUNTIME-SANDBOX-1/`（根外读 BLOCKED、联网 NET_BLOCKED、超时、fail-closed、孙进程树杀、最小 env）；
  - `verification/PLUGIN-RUNTIME-PACKAGED-PYTHON-1/real-bundle-verify.log`：真实 core-sidecar bundle 的 `python/python.exe` + AppContainer 内执行 Hook（`real-bundle-sandbox-hook-ok`）。
- **暂停原因**：手工 GUI 检查成本高（时间长、抢占鼠标、token 消耗大）；用户计划后续写一个软件检查工具替代手工操作。
- **后续**：工具化检查（待用户启动写工具的任务）；GUI 内 Hook 触发需要检测模型权重或一个可脚本化的触发入口。
