# Release Gate 条件 4 · 取证执行清单（2026-11-17，DSH）

> 用途：拿到**真实 Authenticode 证书**后，照着这份清单一次性跑完条件 4，并把证据按指定路径落盘。
> 依据：`doc/tasks/RELEASE-GATE4-SIGNED-MATRIX-1.md`（AC1–AC7）、`doc/reviews/ZCODE-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md`（Q3 条件 4 口径）、
> `doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md`（Q3：旧包不得作证据，必须在新包字节上重跑）。

## 0. 为什么现在做不了（阻塞点唯一）

| 前置 | 现状（2026-11-17 实测） |
|---|---|
| 代码签名证书 | **无** —— `Cert:\CurrentUser\My`、`Cert:\LocalMachine\My` 均无 `-CodeSigningCert` |
| `signtool.exe` | **不存在**（Windows SDK 未安装） |
| 干净的 Windows 环境 | 可用（本机 Win11 26H2 10.0.26300.9711），但「干净」需另备 VM/快照 |
| 合规安装包 | **已有**（见 §1） |

⇒ 除证书与 signtool 外，其余前置**已就绪**。

## 1. 已就绪的输入（本轮已实测）

| 项 | 值 |
|---|---|
| stage | `NewManga-0.1.1-win-x64-models`（`package.ps1 -WithModels` 干净产出） |
| stage 护栏 | `verify-package-manifest.ps1` → **`OK (exe, core_service, 3 onnx / 632552582 B all match VERSION.json)` / EXIT=0** |
| 包级声明 | `license = GPL-3.0-or-later`（两变体相同；随包权重上游声明 Apache-2.0）；`app_build.repo_head` = exe 内嵌 40-hex |
| 安装包 | `NewManga-0.1.1-setup.exe` **652,081,157 B / sha256 `3c9984b21d663a9ec9a8890387e5800df7d85a3005ed66f0231c67653751df05`**（**未签名**；2026-11-18 收紧为 GPL-3.0-or-later 后重新打包，包内六份许可文件与仓库逐字节相同） |
| 向导文案 | 实拍：欢迎页「models 变体（含模型权重，按 GPL-3.0-or-later 分发）」；许可页正文中文正常、清单含 Apache 副本 |
| 包内合规文件 | 从 setup.exe 抽出 **6 份**与仓库根**逐字节相同**（NOTICE / THIRD_PARTY / LICENSE_AUDIT / LICENSE / LICENSE-Apache-2.0.txt / LICENSE-AGPL-3.0.txt） |

## 2. 需要证书后执行的动作（按顺序）

### S1 签名（AC1/AC2）

```powershell
# 1) 确认证书可用（把 <thumbprint> 换成真实指纹）
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Format-List Subject,Thumbprint,NotAfter

# 2) 签 stage 里的应用 exe（单文件发布；先签再打包，包内即签名版）
signtool sign /sha1 <thumbprint> /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `
  "<stage>\app\NewManga.App.exe"

# 3) 重新出安装包（会带签名后的 app.exe）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 -StageDir "<stage>" -OutDir "<out>"

# 4) 签安装包本身
signtool sign /sha1 <thumbprint> /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `
  "<out>\NewManga-0.1.1-setup.exe"

# 5) 验签（必须 Verified + 时间戳）
Get-AuthenticodeSignature "<out>\NewManga-0.1.1-setup.exe" | Format-List Status,StatusMessage,SignerCertificate
Get-AuthenticodeSignature "<stage>\app\NewManga.App.exe" | Format-List Status
```

**证据**：`verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac1-authenticode.log`（两条 `Status = Valid` + 证书 Subject/Thumbprint/NotAfter）、
`ac1-signed-setup.sha256`（签名后包字节与 sha256 —— **后续所有矩阵都绑定这个 hash**）。

### S2 干净安装（AC3）

```powershell
# 干净 VM/快照；记录基线
Get-ChildItem "$env:LOCALAPPDATA\Programs\NewManga" -ErrorAction SilentlyContinue   # 应为空
Get-ChildItem "$env:APPDATA\com.newmanga.desktop" -Recurse -File -ErrorAction SilentlyContinue |
  Get-FileHash -Algorithm SHA256 | Sort-Object Path   # 用户数据根基线（若已存在）

# 静默安装 + 退出码
Start-Process -FilePath "<out>\NewManga-0.1.1-setup.exe" -ArgumentList '/S' -Wait -PassThru |
  Select-Object ExitCode
```

**证据**：`ac3-clean-install.log`（安装前目录为空、安装 `ExitCode=0`、安装后 `app/NewManga.App.exe` 与 stage 内**签名版** sha256 相同）。

### S3 四页可达（AC4）

从**已安装的 exe** 启动（不是 stage 里的），逐页截图并记录窗口标题/关键控件：

```
资料柜 → 工作位 → 控制台（设置）→ 阅读器（F11）
```

**证据**：`ac4-page-<n>-<name>.png` 四张 + `ac4-notes.md`（每页的窗口截图、启动命令带 `--data-root` 指向隔离目录、exe 的 sha256）。

### S4 跨版本升级/回退（AC5）

```powershell
# 准备上一版已签名安装包（例如 0.1.0），先装它，再用 0.1.1 覆盖安装
# 回退：卸载 0.1.1 → 重装 0.1.0 → 确认用户数据仍可读
```

**证据**：`ac5-upgrade.log` / `ac5-rollback.log`（两版 hash、每次安装 ExitCode、升级后 `库/章节` 数量与升级前一致）。

### S5 卸载 + 用户数据保护（AC6）

```powershell
# 卸载前：记录用户数据根的文件数与总字节
# 静默卸载
Start-Process -FilePath "$env:LOCALAPPDATA\Programs\NewManga\uninstall.exe" -ArgumentList '/S' -Wait -PassThru |
  Select-Object ExitCode
# 卸载后：用户数据根必须**不变**（同文件数、同总字节、抽样 sha256 相同）
```

**证据**：`ac6-uninstall.log`（卸载前后用户数据根 `文件数/总字节` 对照 + 抽样 sha256）。

### S6 不虚报（AC7）

- 写清「签名证书来源、颁发者、有效期」；**不得**用自签名冒充。
- 写清「矩阵在哪台机器/哪个 Windows 版本上跑」；未跑的子项必须写 `NOT_RUN`。
- 明确「本矩阵只对 `ac1-signed-setup.sha256` 那个字节有效」。

## 3. 禁止事项（违反即不可回滚）

1. **不得**用自签名证书、`/a` 自动选证书、或跳过时间戳来"凑"签名。
2. **不得**把旧包（`a4b11458…`、`23c04abd…`、`6f9a45f3…` 或任何未签名/文档不符的包）的矩阵结果移花接木到新包。
3. **不得**为了让矩阵通过而改 `installer.nsi` 的安装行为或绕过护栏。
4. **不得**在 `Technical Gate`/`Release Gate` 上写「通过」，直到 S1–S6 全部有证据且经独立复核。

## 4. 完成后由谁复核

条件 4 属**外部资源依赖**（证书）项，完成后须交**独立上下文**复核者（DSH 子 agent 或 ZCode/Codex）核对：
签名有效性、矩阵绑定 hash、四页截图与安装产物一致性、升级/回退与卸载的数据保护。
**不得**由执行者自审。

## 5. 当前判定

`RELEASE-GATE4-SIGNED-MATRIX-1` 保持 **`proposed`**；条件 4 保持 **未关闭**。
本清单**不构成**任何 Gate 通过，也不改变 `Technical Gate=NOT_SATISFIED`。
