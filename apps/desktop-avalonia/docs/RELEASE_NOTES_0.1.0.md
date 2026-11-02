# New Manga 0.1.0 发行说明

- 版本：**0.1.0**（2026-10-28）
- 适用平台：Windows 10/11 x64（桌面应用：Avalonia Host + Python Core sidecar）
- 发行形态：**base zip**、**models zip**、**NSIS per-user 安装包（未签名）**
- 本版本**没有代码签名**（用户暂无证书），因此 Windows SmartScreen 会提示「未知发布者」；请按下方「未签名与 SmartScreen」一节操作，并用 SHA-256 校验文件完整性。

## 1. 发行变体与许可证

| 变体 | 文件 | 是否含模型权重 | 整体分发许可 |
|---|---|---|---|
| **base** | `NewManga-0.1.0-win-x64.zip`（98.7 MB） | 否 | **GPL-3.0-or-later**（包内 `LICENSE`） |
| **models** | `NewManga-0.1.0-win-x64-models.zip`（691.9 MB） | 是（`app/core-sidecar/models/`） | **AGPL-3.0**（包内 `LICENSE-AGPL-3.0.txt`） |
| **NSIS 安装包** | `NewManga-0.1.0-setup.exe`（65.4 MB） | 否（base 内容） | **GPL-3.0-or-later** |

- `models` 变体随包分发 **Ultralytics YOLO11s-seg** 模型权重（AGPL-3.0），故该包整体按 **AGPL-3.0** 分发，并随包提供 GNU AGPL-3.0 全文。
- `base` 变体与 NSIS 安装包不含模型权重，按 **GPL-3.0-or-later** 分发；包内同样携带 `LICENSE-AGPL-3.0.txt`（说明可选 models 组件的许可）。
- 许可文件：每个包根目录含 `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE_AUDIT.md`；源码与构建脚本见发行页/仓库。

## 2. 文件与 SHA-256

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `NewManga-0.1.0-win-x64.zip` | 103,492,048 | `722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef` |
| `NewManga-0.1.0-win-x64-models.zip` | 725,499,708 | `480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67` |
| `NewManga-0.1.0-setup.exe` | 68,611,208 | `ebad86624a0add5393b8a28d258e2334c23fd13ee52f0a0f0b598a5ba9753691` |

同目录随发行提供 `SHA256SUMS`（标准 `sha256sum` 格式：`<sha256>  <filename>`）与 `SHA256SUMS.json`（含字节数与生成时间）。

## 3. 安装方式

### 方式 A：NSIS 安装包（推荐，per-user，无需管理员）

1. 下载 `NewManga-0.1.0-setup.exe` 与 `SHA256SUMS`，先做 SHA-256 校验（见 §4）。
2. 双击安装包；未签名时 SmartScreen 会拦截（见 §5）。
3. 选择「我接受」→ 安装目录默认为 `%LOCALAPPDATA%\Programs\NewManga`（per-user，不需要管理员权限）→ 安装。
4. 安装完成后从开始菜单「New Manga」启动；卸载用开始菜单「卸载 New Manga」或 `Uninstall.exe`。
5. 静默安装（脚本/批量）：`NewManga-0.1.0-setup.exe /S`；静默卸载：`"%LOCALAPPDATA%\Programs\NewManga\Uninstall.exe" /S`。

安装包行为：写入 HKCU 卸载项与开始菜单快捷方式；**不写 HKLM/Program Files**；**安装/卸载都不会触碰数据根** `%APPDATA%\com.newmanga.desktop`；升级 = 重新运行新版本 setup 覆盖安装（先清理旧程序文件，数据根与设置保留）。

### 方式 B：zip 包 + install.ps1

1. 校验并解压 zip（base 或 models）到任意目录。
2. 运行 `pwsh -File install.ps1 -PackageDir <解压目录>`（或按 `MANUAL_VERIFY.md` 手动放置）。
3. `app/NewManga.App.exe` 启动应用；卸载运行 `uninstall.ps1 -InstallDir <安装目录>`。
4. base 包不含模型：首次检测会以 typed `PROVIDER_NOT_CONFIGURED` 报错，属预期——把模型放到 `%APPDATA%\com.newmanga.desktop\models\{detector,ocr}`（或使用 models 包）。

## 4. SHA-256 校验步骤

Windows PowerShell（任选其一）：

```powershell
# 1) 直接比对（把 <file> 换成下载到的文件名）
Get-FileHash .\<file> -Algorithm SHA256
# 与本文档 §2 的 64 位十六进制值逐字符比较
```

```powershell
# 2) 使用随发行提供的 SHA256SUMS（仓库脚本同样可复算/校验）
#    把三个产物与 SHA256SUMS 放到同一目录后：
pwsh -File verify-release.ps1 -ArtifactDir .
# 或使用 packaging/release/verify-release.ps1（仓库内），-Quiet 只输出结论
```

```powershell
# 3) certutil（系统自带）
certutil -hashfile .\<file> SHA256
```

校验不通过（哈希不一致/文件缺失）时**不要运行**，请重新下载；本版本不含签名，哈希核对是发布完整性的主要保障。

## 5. 未签名与 SmartScreen（重要）

- 本版本**未做代码签名**（无证书）。Windows 10/11 可能显示「Windows 已保护你的电脑 / 未知发布者」。
- 处理方式：点击提示框中的 **「更多信息」→「仍要运行」** 即可继续安装/运行。请务必先按 §4 核对 SHA-256，确认文件来自官方发行页。
- 若企业环境禁止未签名程序，请由管理员按组织策略放行，或使用方式 B 的 zip 版并在受控目录运行。
- 签名不可得不会阻塞功能；证书到位后由签名线（V1-RELEASE-SIGNING-1）补签，届时 SmartScreen 提示会消失。

## 6. 数据根、升级与卸载

- 用户数据根：`%APPDATA%\com.newmanga.desktop`（书架数据库 `library.db`、托管副本、缓存、导出、日志等）。
- 安装/卸载**不会删除或修改**数据根；卸载只清理程序目录、开始菜单快捷方式与 HKCU 卸载项。
- 升级：安装包覆盖安装或解压新 zip 覆盖 `app/`；数据根保留。升级前建议备份 `library.db` 与 `backups/`。
- 卸载：NSIS 安装包 → 开始菜单「卸载 New Manga」或 `"%LOCALAPPDATA%\Programs\NewManga\Uninstall.exe"`；zip 版 → `uninstall.ps1 -InstallDir <目录>`。如需彻底清除用户数据，请手动备份后删除 `%APPDATA%\com.newmanga.desktop`（本版本不会代删）。

## 7. 已知限制

1. **未签名**：SmartScreen 提示未知发布者；见 §5。
2. **models 变体只以 zip 分发**（691.9 MB），不提供 NSIS 安装包；base 变体不含模型，需按 §3-B 放置。
3. **per-user 安装**：同一台机器多用户各自安装一份（不写 HKLM/Program Files，因此不需要管理员）。
4. **升级为覆盖式**：无回滚 UI/自动更新；升级前请自行备份数据根。
5. 首次启动/首次导入等操作耗时受机器性能影响；模型推理需要 base 模型文件或 models 包。
6. 应用启动会向数据根 `logs/` 写入诊断日志（例如 `window-material.log`），属正常行为。

## 8. 免费替代方案（签名不可得时）

- **SHA-256 校验**（本发行已提供）：零成本，能验证下载完整性、防篡改；真实性依赖官方发行页/渠道。
- **免费 OSS 代码签名**：开源项目可向 [SignPath Foundation](https://signpath.org/) 等免费代码签名计划申请（需项目开源、通过审核），获批后未来版本可由 CI 签名，SmartScreen 提示会消失。该流程不改变本版本的未签名事实。
- 企业分发可用内部证书或组策略白名单；个人用户按 §5 手动放行即可。

## 9. 验证与反馈

- 人工核验清单：[MANUAL_VERIFY.md](MANUAL_VERIFY.md)（含 Mica/DPI/IME/沉浸阅读等现场检查项）。
- 升级说明：[UPGRADE.md](UPGRADE.md)（构建识别、覆盖升级、数据根与备份）。
- 本发行说明中的哈希与字节数由 `packaging/release/generate-checksums.ps1` 从实际产物生成，可用 `packaging/release/verify-release.ps1` 复算。
