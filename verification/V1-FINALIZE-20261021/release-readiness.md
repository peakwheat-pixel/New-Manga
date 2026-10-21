# v1 发布就绪清单（2026-10-21）

**结论：发布验证中「全新机器安装/卸载」已 PASS；「代码签名」按用户 2026-10-21 明确决定 **WAIVED（接受未签名 v1）**；签名流水线已用自签名测试证书在副本上验证可用，但未作为真实发布签名。**

## 1. 产物

| 产物 | 大小 | SHA-256 | 状态 |
|---|---:|---|---|
| `m2rc1-desktop_0.1.0_x64-setup.exe` | 579,979,256 B | `b0ad46f5df01f4ffc287e9aeaef9ecaf5b163778d9ac632db92c6ce66ac38c7b` | 未签名（NotSigned） |
| `target/release/m2rc1-desktop.exe`（构建） | 11,882,496 B | `7063ac321b951091aa1a17daa9fdf272c94e473f8aefa34dc816a0a395fb85f9` | — |
| `core_service.exe`（frozen sidecar） | 68,793,273 B | `b61074d48b6c8d59e3dc930bd3482422e8d0309568a518527fad94f549564a46` | 与安装内 payload 一致 |

## 2. 全新机器安装/卸载验证：PASS

- 环境：Windows Sandbox（Windows 11 Enterprise build 26100，`WDAGUtilityAccount`，无既有 m2rc1 安装/用户数据）。
- `setup.exe /S` → exit 0；安装到 `%LOCALAPPDATA%\m2rc1-desktop`，5,565 文件 / 1,299,418,018 B。
- `core_service.exe` SHA-256 与 frozen sidecar 完全一致（`b61074d4…`）。
- `uninstall.exe /S` → exit 0；安装目录删除，卸载项 0。
- 证据：`verification/V1-FINALIZE-20261021/clean-install-sandbox/RESULT.md`、`RESULT.json`、`sandbox-result.txt`。

## 3. 代码签名：WAIVED（用户接受未签名），流水线已验证

- 当前证书存储（CurrentUser/LocalMachine `My`）无 Code Signing EKU 证书；`Get-AuthenticodeSignature` 安装包 = `NotSigned`。
- **用户决定（2026-10-21）：“接受未签名 v1”**。真实签名不再作为本次发布阻塞项；本 Task 保留为未签名发布签核记录。
- `signtool.exe`：`C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe`。
- **流水线测试**（自签名证书 + RFC3161 时间戳，仅对**副本**，测试后删除证书与副本，源安装包未动）：
  - `signtool sign /sha1 <thumb> /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com setup-signing-test.exe` → **exit 0**（"Successfully signed"）
  - 时间戳：`The signature is timestamped`，时间戳链已验证到 DigiCert 根。
  - `signtool verify /pa` → exit 1，唯一原因 `certificate chain ... root which is not trusted`（自签名根不被信任，**预期**）；真实 CA 证书应通过。
  - 源安装包 SHA-256 前后未变（`b0ad46f5…`）；测试副本签名后 SHA-256 变化（`f652d617…`）。
- 日志：`signing-pipeline-test.log`（本目录）。
- **若后续补做真实签名**（非本次发布）：需要 PFX 绝对路径 + 密码（或已导入证书指纹）。命令模板：
  ```
  signtool sign /f <pfx> /p <password> /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com <setup.exe>
  signtool verify /pa /v <setup.exe>
  ```
  若使用证书存储：`signtool sign /sha1 <thumbprint> /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com <setup.exe>`。

## 4. 发布阻塞 / 待决项

1. **签名证书缺失 → 已由用户裁定 WAIVED**：用户 2026-10-21 明确接受未签名 v1；不再作为发布阻塞。记录于 [V1-RELEASE-SIGNING-1](../tasks/V1-RELEASE-SIGNING-1.md)（`in_review`）。
2. `WORKSPACE-CLEANUP-TOOL-HARDENING-1` 已集成 (`368c07809`) 且 Codex R4 `approved`，Task 保持 `in_review`，待最终收口裁定。
3. WORKSPACE 工具对真实仓库 fail-closed：发现 **163 条声明完整性错误**（含 69 条不可解析 JSON）；工具拒绝清理是预期行为，声明修复需另立 Task/Codex 裁定。
4. 既有限制（不因本轮改变）：P20 AC4 撕裂项 = LIMITATION/UNOBSERVED；安装包未签名前不可作为正式发布包。

## 5. 发布判定

- **安装/卸载：READY**。
- **签名：WAIVED（用户明确接受未签名 v1）**。
- 本包可作为**未签名自用/内测版**发布；Windows 可能提示“未知发布者/Windows 已保护你的电脑”，用户需点“更多信息 → 仍要运行”。
- 不得宣称“已签名/已验证发布者”；不得以自签名测试证书替代真实签名。
