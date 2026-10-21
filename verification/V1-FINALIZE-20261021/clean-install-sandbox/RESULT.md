# v1 全新机器安装/卸载验证（Windows Sandbox，2026-10-21）

**结论**：在全新 Windows Sandbox（无既有安装、无用户数据）中，安装包可静默安装、安装后文件与 frozen Core 一致、可静默卸载并清空安装目录/卸载项。**PASS**。

## 环境

- 主机：Windows 11 专业版 10.0.26300，Hyper-V/Sandbox 已启用。
- Sandbox：Windows 11 企业版 build 26100，用户 `WDAGUtilityAccount`，无既有 m2rc1 安装项。
- 隔离方式：Windows Sandbox（同主机隔离 VM，不是第二台物理机）；Networking 启用（本次 WebView2 已在 Sandbox 内，`pv=155.0.4283.60`，未触发下载）。

## 被测产物

| 产物 | 大小 | SHA-256 |
|---|---:|---|
| `m2rc1-desktop_0.1.0_x64-setup.exe` | 579,979,256 B | `b0ad46f5df01f4ffc287e9aeaef9ecaf5b163778d9ac632db92c6ce66ac38c7b` |
| `target/release/m2rc1-desktop.exe`（构建产物） | 11,882,496 B | `7063ac321b951091aa1a17daa9fdf272c94e473f8aefa34dc816a0a395fb85f9` |
| frozen `core_service.exe` | 68,793,273 B | `b61074d48b6c8d59e3dc930bd3482422e8d0309568a518527fad94f549564a46` |

## 结果（Sandbox 内实测）

| 步骤 | 结果 |
|---|---|
| 安装前 m2rc1 卸载项 | 0 |
| 静默安装 `setup.exe /S` | **exit 0** |
| 安装位置 | `C:\Users\WDAGUtilityAccount\AppData\Local\m2rc1-desktop`（currentUser 模式） |
| 卸载注册项 | 1 条：`m2rc1-desktop` / `0.1.0` / `uninstall.exe` |
| 安装文件 | 5,565 个，1,299,418,018 B |
| 安装后 `m2rc1-desktop.exe` | 11,882,496 B，SHA-256 `f2d85356f99c081691a0a2165b9523c1e50c7f47218ff6ffaef4fe4e9abab8ef`（与构建目录 exe 不同：NSIS/Tauri 打包写入 bundle 元信息；以安装 payload 为准） |
| 安装后 `resources/core-sidecar/core_service.exe` | 68,793,273 B，SHA-256 `b61074d48b6c8d59e3dc930bd3482422e8d0309568a518527fad94f549564a46`（与 frozen sidecar **一致**） |
| 静默卸载 `uninstall.exe /S` | **exit 0** |
| 卸载后安装目录 | 已删除 |
| 卸载后卸载项 | 0 |

## 证据文件

- `sandbox-result.txt`：Sandbox 内完整日志（含环境、哈希、exit code）。
- `clean-install-test.ps1`：实际执行脚本。
- `clean-install.wsb`：Sandbox 配置。
- `ps-copy.txt`：local-copy 执行标记。
- `RESULT.json`：机器可读结果与哈希。

## 限制 / 未声明

1. Sandbox 是同主机隔离 VM，不是独立物理机；内核/版本仍同机。
2. 安装包**未签名**（`Get-AuthenticodeSignature` = `NotSigned`）；签名验证待用户提供证书后补做。
3. 未在 Sandbox 内启动 GUI 做交互复盘（安装/卸载、文件与 sidecar 完整性已验）；产品功能测试沿用 v1 原始证据。
4. 首次尝试因 Sandbox 会话提前注销失败；本地复制脚本 + 重新冷启动后通过。该过程与失败截图未作为最终证据，最终证据为本次完整成功日志。
