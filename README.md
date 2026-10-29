# New Manga

**Local-first manga/comic translation for Windows** — import your own pages, run a translation pipeline
(detection → OCR → translation → cleanup/inpaint → render), and export translated pages as ZIP or PDF.

> **Privacy:** everything is local **by default**; there is no telemetry, no account, and no network
> listener in the app. If you explicitly configure a **remote provider** in Settings, the data kinds that
> provider sends are shown in the settings privacy notice (OCR → page images, translation → text,
> inpainting → images/masks). With only local providers, nothing leaves the machine.
>
> **Status: 0.1.0 (early).** The Windows installer is **not code-signed yet**, so SmartScreen shows
> “Unknown publisher”. Verify the SHA-256 manifest and read the release notes before installing.
> A free open-source signing application is prepared in [`doc/release/`](doc/release/).

## What it does

- **Bookshelf** — managed library of books/chapters/pages. Original files are never modified (managed copy).
- **Workbench** — real page canvas with detected regions; retype/undo a region, rerender a page.
- **Reader** — immersive reader (Esc/H/F keys), webtoon scrolling, per-chapter reading progress.
- **Settings** — themes (9 packs, incl. macOS-style Sonoma/Launchpad/Split), provider bindings,
  network profiles, credential vault, device/GPU status.
- **Export** — ZIP image pack or PDF (image-only / searchable dual-layer CJK text).

## 架构 / 中文要点

- C# / .NET 9 + Avalonia 桌面壳（单文件自包含 `app/NewManga.App.exe`）；Python 3 Core 侧车
  （`app/core-sidecar/core_service.exe`）负责 SQLite 书库、流水线与本地推理（ONNX Runtime/DirectML）；
  两者经严格请求/响应的 typed JSON IPC 通信，无网络监听。
- 用户数据根 `%APPDATA%\com.newmanga.desktop`（书库、托管副本、缓存、导出、日志）；安装/卸载**不会**删除或改写它。
- 四个一级页面：书架 / 工作台 / 阅读器 / 设置。
- 构建：需 .NET 9 SDK、Python 3.11、NSIS 3.x、PowerShell 7；模型权重不随 Git 仓库分发，
  `-models` 发行包内置权重，base 包首次检测会以 typed `PROVIDER_NOT_CONFIGURED` 提示。
- 测试基线（2026-10-28）：.NET 258/258（0 skipped）、pytest 2773P/10S/0F、typed IPC 命令 66/66。
- 许可：项目代码 GPL-3.0-or-later；`-models` 包因内置 Ultralytics YOLO11s-seg（AGPL-3.0）整体按 AGPL-3.0
  分发，AGPL 全文随包（`LICENSE-AGPL-3.0.txt`）。
- 当前安装包未签名：SmartScreen 会提示「未知发布者」，请先核对 SHA-256 并按发行说明操作；签名申请材料见 `doc/release/`。

## Architecture

| Layer | Tech | Role |
|---|---|---|
| Desktop host | C# / .NET 9 + Avalonia | four pages, rendering, input; single-file self-contained `app/NewManga.App.exe` |
| Core service | Python 3 + SQLite + ONNX Runtime (DirectML) | library storage, pipeline, inference; local sidecar `app/core-sidecar/core_service.exe` |
| Transport | typed JSON IPC over stdio/named pipe | host ↔ Core; no network listeners |

User data lives in `%APPDATA%\com.newmanga.desktop` (SQLite library, managed copies, derived artifacts,
exports, logs). The installer never deletes or rewrites this data root.

## Requirements

- Windows 10/11 x64
- For building: .NET 9 SDK, Python 3.11 (with `requirements-dev.txt`, which includes PyInstaller and
  pytest), NSIS 3.x (`makensis`; 3.13 verified locally), PowerShell 7
- Models are **not** in the Git repository. The `-models` distribution bundles them; the base package
  reports a typed `PROVIDER_NOT_CONFIGURED` until weights are placed on the data root.
- A public CI build without model weights can be produced with
  `packaging/m2ac5/build_sidecar.ps1 -PythonExe python -SkipWeights`; weights are staged separately for
  the `-models` variant.

## Build (Windows)

```powershell
# 0) dependencies
python -m pip install -r requirements.txt -r requirements-dev.txt

# 1) tests
python -m pytest -q
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1      # 258/258 on 2026-10-28

# 2) Core sidecar bundle (no weights for a public build; stage weights for the -models variant)
pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -PythonExe python -SkipWeights

# 3) package (base; add -WithModels for the models variant — requires staged weights)
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 `
  -OutputRoot <out-dir> -Version 0.1.0 `
  -SidecarDir apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar

# 4) per-user NSIS installer (unsigned in this release)
pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 `
  -StageDir <out-dir>/NewManga-0.1.0-win-x64 -OutDir <out-dir> -Version 0.1.0

# 5) integrity manifest (full release: base + models + setup)
pwsh -NoProfile -File packaging/release/generate-checksums.ps1 `
  -BaseZip <out-dir>/NewManga-0.1.0-win-x64.zip `
  -ModelsZip <out-dir>/NewManga-0.1.0-win-x64-models.zip `
  -SetupExe <out-dir>/NewManga-0.1.0-setup.exe `
  -OutFile packaging/release/SHA256SUMS
```

A GitHub Actions pipeline **draft** lives in [`.github/workflows/build-release.yml`](.github/workflows/build-release.yml):
public base build → SignPath signing request (disabled until the project is approved and secrets exist).

## Test & quality baseline (2026-10-28)

- .NET: **258/258 passed, 0 skipped** (coreclient 61 / host 60 / app 137)
- Python: **2773 passed, 10 skipped, 0 failed**
- Typed IPC command surface: **66/66 implemented**
- Governance checker: PASS

## Verify a release

```powershell
pwsh -NoProfile -File packaging/release/verify-release.ps1 -ArtifactDir <dir-with-artifacts>
Get-AuthenticodeSignature .\NewManga-0.1.0-setup.exe    # currently NotSigned
```

See `apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md` for install/upgrade/uninstall, SmartScreen
instructions, and known limitations (written in Chinese).

## Install / uninstall

- **Installer (per-user, no admin):** run `NewManga-0.1.0-setup.exe` → installs to
  `%LOCALAPPDATA%\Programs\NewManga`; uninstall from Start Menu or `Uninstall.exe /S`.
- **Zip:** extract, then `install.ps1 -PackageDir <extracted>`; uninstall with `uninstall.ps1`.
- Silent install/uninstall for scripts: `NewManga-0.1.0-setup.exe /S` and `Uninstall.exe /S`.

## License

- Project code: **GPL-3.0-or-later** — see [`LICENSE`](LICENSE).
- `-models` packages bundle Ultralytics YOLO11s-seg weights (**AGPL-3.0**) and are therefore distributed
  under **AGPL-3.0**; the full AGPL text ships inside every package
  ([`LICENSE-AGPL-3.0.txt`](LICENSE-AGPL-3.0.txt)). Third-party components: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md),
  [`NOTICE.md`](NOTICE.md). Fonts are system fonts only — none are redistributed.

## Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by [SignPath Foundation](https://signpath.org/).

- Committers and reviewers: [@peakwheat-pixel](https://github.com/peakwheat-pixel) (repository owner)
- Approvers (signing requests): [@peakwheat-pixel](https://github.com/peakwheat-pixel)
- Privacy policy: [`PRIVACY.md`](PRIVACY.md) — the program transfers information to other networked
  systems only when the user explicitly configures a remote provider or uses the Playwright-based import
  helper; local providers keep all processing on the machine.

## Contributing

This is an early, single-maintainer project (repository created 2026-09-24). Issues and pull requests are
welcome; please do not include model weights or third-party copyrighted assets in pull requests.
Release/signing process: [`doc/release/SIGNPATH-APPLICATION.md`](doc/release/SIGNPATH-APPLICATION.md)
(English) and [`doc/release/SIGNPATH-APPLICATION-CHECKLIST.md`](doc/release/SIGNPATH-APPLICATION-CHECKLIST.md) (中文).
