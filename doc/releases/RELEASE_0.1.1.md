# New Manga 0.1.1 — 发布产物（2026-10-30）

- Git：`main` @ `cc88d1ee9fdd27825869b4cdc0a1b68965b3d1fc`；远端 `origin/main` 已推送（https://github.com/peakwheat-pixel/New-Manga）
- 运行时：.NET 9 self-contained single-file（无需安装 .NET）
- 形态：便携 ZIP（便携 + core sidecar）、NSIS 安装包

## 产物与校验

| 产物 | 大小 | SHA-256 |
|---|---:|---|
| `NewManga-0.1.1-win-x64-portable.zip` | 121,047,833 B (115.4 MB) | `47BC1513DD1ACC5E3558B200243B6CC3C79F00B1E8DCB058AC4EF112360493A7` |
| `NewManga-0.1.1-win-x64-setup.exe` | 75,144,897 B (71.7 MB) | `D8FCB7EB48F3725B0CC6563DDFCBE05EE5D8AB497344D2191664A257FAE5BBEC` |

校验：`pwsh -File packaging/release/verify-release.ps1 -Manifest <dir>/SHA256SUMS -ArtifactDir <dir>` → **PASS (2/2)**。

## 内容

- `NewManga.App.exe`（单文件自包含）、`core-sidecar/`（core_service.exe + host_bridge.exe + _internal）
- `Run-NewManga.cmd`（便携启动，自动传 `--sidecar-dir=core-sidecar`）
- `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`README.md`、`RELEASE-0.1.1.md`
- 模型权重不随包（按项目策略外置）

## 冒烟验证

- 从**打包后的 stage** 启动：窗口 `New Manga`、Host 就绪（host.log: core_service ready / host_bridge ready / mode=ReadWrite）、自然退出 `exit 0`；`--theme-home` 隔离生效。
- 安装包：构建成功（NSIS 3.13）；**安装/卸载冒烟 NOT_RUN**（避免改动当前用户环境），验证命令：`NewManga-0.1.1-win-x64-setup.exe /S /D=<临时目录>`，随后运行 `<临时目录>/Uninstall.exe /S`。

## 构建复现

```
pwsh -NoProfile -File tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir "<sidecar>"
"C:\Program Files (x86)\NSIS\makensis.exe" /DVERSION=0.1.1 /DVERSION4=0.1.1.0 /DSTAGE_DIR=<stage-with-app-subdir> /DOUT_FILE=<setup.exe> /DINSTALL_SIZE_KB=290000 /DLICENSE_FILE=<stage>/NOTICE.md packaging/nsis/installer.nsi
```
