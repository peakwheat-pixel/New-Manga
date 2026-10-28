# New Manga

**Local-first manga/comic translation for Windows** — import your own pages, run a local AI pipeline
(detection → OCR → translation → cleanup/inpaint → render), and export translated pages as ZIP or PDF.
No uploads, no telemetry, no account: everything runs on your machine.

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
- For building: .NET 9 SDK, Python 3.11, NSIS 3.13 (`makensis`), PowerShell 7
- Models are **not** in the Git repository. The `-models` distribution bundles them; the base package
  reports a typed `PROVIDER_NOT_CONFIGURED` until weights are placed on the data root.

## Build (Windows)

```powershell
# 1) tests
python -m pytest -q
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1      # 258/258 on 2026-10-28

# 2) package (base; add -WithModels for the models variant)
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 `
  -OutputRoot <out-dir> -Version 0.1.0 -SidecarDir <built-core-sidecar>

# 3) per-user NSIS installer (unsigned in this release)
pwsh -NoProfile -File apps/desktop-avalonia/scripts/build-installer.ps1 `
  -StageDir <out-dir>/NewManga-0.1.0-win-x64 -OutDir <out-dir> -Version 0.1.0

# 4) integrity manifest
pwsh -NoProfile -File packaging/release/generate-checksums.ps1 `
  -BaseZip <out-dir>/NewManga-0.1.0-win-x64.zip `
  -SetupExe <out-dir>/NewManga-0.1.0-setup.exe `
  -OutFile packaging/release/SHA256SUMS
```

A GitHub Actions pipeline draft lives in [`.github/workflows/build-release.yml`](.github/workflows/build-release.yml):
public build → SignPath signing request (disabled until the project is approved).

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
instructions, and known limitations.

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

## Contributing

This is an early, single-maintainer project. Issues and pull requests are welcome; please do not include
model weights or third-party copyrighted assets in pull requests. Release/signing process:
[`doc/release/SIGNPATH-APPLICATION.md`](doc/release/SIGNPATH-APPLICATION.md) (English) and
[`doc/release/SIGNPATH-APPLICATION-CHECKLIST.md`](doc/release/SIGNPATH-APPLICATION-CHECKLIST.md) (中文).
