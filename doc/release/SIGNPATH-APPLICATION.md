# SignPath Foundation — Free OSS Code Signing Application (Draft)

> **Status:** draft prepared by the New Manga project maintainers on 2026-10-28.
> **This file is a source document, not a submitted application.** Anything in `[SQUARE BRACKETS]` must be
> replaced or confirmed by the human maintainer before submitting. See
> `SIGNPATH-APPLICATION-CHECKLIST.md` for the mandatory pre-submission fixes (license/README/CI on the
> default branch are currently missing on GitHub).

---

## 1. Form-ready summary

| Field | Value |
|---|---|
| Project name | New Manga |
| Project website | `https://github.com/peakwheat-pixel/New-Manga` (no separate site yet) |
| Source repository | `https://github.com/peakwheat-pixel/New-Manga` |
| Repository visibility | public (created 2026-09-24; no public binary releases yet) |
| Default branch | `main` (see pre-submission fixes — the signing source will be the public release branch `[RELEASE_BRANCH]`) |
| License | GNU GPL-3.0-or-later (`LICENSE` at repo root); the `-models` distribution variant is **AGPL-3.0** because it bundles Ultralytics YOLO11s-seg weights (`LICENSE-AGPL-3.0.txt` ships with every package) |
| Project language / stack | C# / .NET 9 + Avalonia (desktop UI), Python 3 (local Core service), SQLite, PowerShell build scripts |
| Maintainer | `[YOUR NAME]` — `[YOUR EMAIL]` — GitHub: `peakwheat-pixel` |
| Artifact to sign | `NewManga-0.1.0-setup.exe` (NSIS per-user installer, currently unsigned); optionally the sidecar launchers |
| Build environment | Windows (GitHub-hosted `windows-latest` runner planned; see §5) |

## 2. What the project is

New Manga is a **local-first Windows desktop application for translating manga/comic pages**. It imports a
user's own image files or folders into a managed library, runs a translation pipeline (text/bubble
detection, OCR, translation, region cleanup/inpainting, render), and exports the translated pages as ZIP or
PDF. The application has four first-class pages — bookshelf, workbench, reader, settings.

**Privacy model (accurate wording):** processing is local by default; the application has no telemetry, no
account, and no network listener of its own. If the user explicitly configures a **remote provider** in
Settings, that provider may receive the data kinds shown in the settings privacy notice — page images for
OCR, text for translation, images/masks for inpainting (`src/application/settings/privacy.py`). With local
providers only, no user media leaves the machine.

Technology:

- **Avalonia / C# (.NET 9)** desktop host (single-file self-contained `NewManga.App.exe`).
- **Python Core** shipped as a local sidecar process (`core_service.exe`), spoken to over a typed JSON IPC
  protocol. The Core owns SQLite storage, the pipeline, and model inference (ONNX Runtime, DirectML).
- **Managed copy** storage model: original user files are never modified; derived artifacts live in an
  app-managed data root (`%APPDATA%\com.newmanga.desktop`).
- No silent updater, no bundled installers, no third-party ad/analytics SDKs.

## 3. Why the project needs code signing

The application is distributed as a Windows executable. Without an Authenticode signature, Windows
SmartScreen shows “Unknown publisher / Windows protected your PC” and requires users to click
“More info → Run anyway”. For an open-source project with **zero budget for a commercial code-signing
certificate**, this warning:

- scares away users and makes legitimate distribution indistinguishable from malware;
- breaks silent/unattended installs in some environments due to warning dialogs;
- pushes users toward disabling SmartScreen, which is a security regression.

The 0.1.0 release is currently **unsigned** and we mitigate it only with published SHA-256 checksums and a
step-by-step SmartScreen note in the release notes. A free SignPath Foundation OSS certificate would let us
ship a properly signed installer while keeping the project free and open source.

## 4. License and compliance

- Project code: **GPL-3.0-or-later** (full text in `LICENSE`).
- The `-models` package bundles **Ultralytics YOLO11s-seg** ONNX weights (AGPL-3.0), therefore that package
  variant as a whole is distributed as **AGPL-3.0**; the GNU AGPL-3.0 full text
  (`LICENSE-AGPL-3.0.txt`; 34,523 bytes git blob / 35,184 bytes CRLF checkout, byte-identical to the
  official GNU text) ships inside **every** package together with `NOTICE.md`, `THIRD_PARTY_LICENSES.md`
  and `LICENSE_AUDIT.md` — four license/notice files in total.
- Model weights are never stored in the Git repository. Third-party components and their licenses are
  registered in `THIRD_PARTY_LICENSES.md`.
- No GPL/AGPL-incompatible proprietary components are linked into the signed installer.

## 5. Build and release process

Current pipeline (reproducible on a clean Windows machine):

1. Install dependencies: .NET 9 SDK, Python 3.11, `pip install -r requirements.txt -r requirements-dev.txt`
   (dev requirements include PyInstaller and pytest), NSIS 3.x, PowerShell 7.
2. Build the Python Core sidecar bundle with
   `packaging/m2ac5/build_sidecar.ps1 -PythonExe (Get-Command python).Source -SkipWeights` for a
   weights-free public build (the script requires a real `python.exe` path; the `-models` variant stages
   weights separately and weights are never uploaded to the repository).
3. `dotnet publish` the Avalonia host (single-file, self-contained, trimmed) → `app/`.
4. Robocopy the Core sidecar into `app/core-sidecar/`.
5. Copy the license/notice set (`LICENSE`, `LICENSE-AGPL-3.0.txt`, `NOTICE.md`, `THIRD_PARTY_LICENSES.md`)
   and `LICENSE_AUDIT.md`, and verify each copy byte-for-byte (SHA-256) —
   `apps/desktop-avalonia/scripts/package.ps1`.
6. Generate `VERSION.json` with the variant and license declaration.
7. Build the per-user NSIS installer — `apps/desktop-avalonia/scripts/build-installer.ps1` →
   `NewManga-<version>-setup.exe`.
8. Write `packaging/release/SHA256SUMS` for all artifacts and publish it with the release (the full
   three-artifact manifest; the CI draft writes a base-only manifest for its build artifact).

Planned CI for SignPath (draft workflow at `.github/workflows/build-release.yml`):

- Windows runner: checkout → install .NET/Python + `requirements-dev.txt` + NSIS → run pytest →
  build a weights-free sidecar (`-SkipWeights`) and the `base` package → build the NSIS installer →
  write a base-only SHA-256 manifest → upload the unsigned installer, base zip and manifest as artifacts.
- The signing step submits that artifact to SignPath through the official GitHub Action
  (`signpath/github-action-submit-signing-request`) and publishes the **signed** installer. It is disabled
  by a workflow input (`sign: false` by default) until SignPath issues the project credentials
  (`SIGNPATH_API_TOKEN`, `SIGNPATH_ORGANIZATION_ID`, `SIGNPATH_PROJECT_SLUG`,
  `SIGNPATH_SIGNING_POLICY_SLUG`); the workflow **never fabricates** a signature when they are absent.
- GitHub Actions `secrets` cannot be used in `if:` expressions, so the enable/disable switch is the
  workflow input; the token itself is injected only into the signing step's `env`.
- The full 258-test suite (including Host integration tests that need a prebuilt sidecar) runs on the
  maintainer machine; the public CI runs pytest plus the projects that do not require a prebuilt sidecar,
  and the workflow comments state this limitation.
- No signing secrets are stored in this repository; they will live only in GitHub Actions secrets.

## 6. Artifacts to be signed

| Artifact | Type | Size (0.1.0) | Notes |
|---|---|---|---|
| `NewManga-<version>-setup.exe` | NSIS installer, PE32 (x86 installer stub; x64 app payload inside) | 68,611,208 B | primary artifact; per-user install, HKCU-only uninstall entry |
| `NewManga.App.exe` (inside the package) | application host | — | built from public source by the same workflow; could be signed in a second policy if desired |
| `core_service.exe` / `host_bridge.exe` (inside the package) | Python sidecar launchers | ~399 KB each | built from public source by the same workflow |

Signing the installer is the minimum we need. If the Foundation’s policy allows, we would also sign the
sidecar launchers with the same project.

## 7. Integrity verification (already published)

- `packaging/release/SHA256SUMS` — `sha256sum`-compatible manifest of every release artifact.
- `packaging/release/verify-release.ps1` — one-command verification; per-file PASS/FAIL, exit code 1 on any
  mismatch or missing file (negative-tamper tested).
- Release notes (`apps/desktop-avalonia/docs/RELEASE_NOTES_0.1.0.md`, written in Chinese) document the
  verification steps and the SmartScreen instructions for end users; an English summary will be added
  before the first public release.

## 8. Project maturity

- First release **0.1.0** packaged on 2026-10-28 (base zip, models zip, NSIS installer).
- Automated tests on 2026-10-28: **258/258** .NET tests (0 skipped), **2773 passed / 10 skipped / 0 failed**
  Python tests, 66/66 typed IPC commands implemented.
- Real-device validation recorded for install/uninstall, data-root preservation (durable digest unchanged)
  and page screenshots under `verification/NSIS-INSTALLER-1/` and `verification/REGION-WORKBENCH-1/`;
  page-level interactive coverage is primarily automated headless UI tests plus real-device screenshots.
- Repository activity: created 2026-09-24; currently 0 stars / 0 forks and **no public binary release yet**
  — 0.1.0 is the first public release attempt. The project is maintained by a single human maintainer with
  AI-agent assistance; no company, no revenue, no commercial certificate budget.

## 9. Maintainer and contact

- Name: `[YOUR NAME]`
- Email: `[YOUR EMAIL]`
- GitHub: `https://github.com/peakwheat-pixel` (repository owner)
- Timezone / availability: `[TIMEZONE]`

## 10. Declarations

I confirm that:

- New Manga contains no malware, adware, bundled installers, or hidden network clients;
- the signed artifact is built from the public source in this repository by a public CI workflow;
- no signing keys or tokens are committed to the repository;
- I will keep the release notes and SHA-256 manifest published alongside each signed artifact;
- I will follow the SignPath Foundation terms and will not redistribute the certificate.

## 11. Release policy (planned)

- Versioning follows `0.x` releases with signed installers; each release publishes the installer, the
  SHA-256 manifest and release notes, and keeps the corresponding source tag public.
- The public release branch is protected; signing is performed only by the CI workflow (never on a
  developer machine with production certificates).
- Only the NSIS installer (`NewManga-<version>-setup.exe`) is the signing target; the application and
  sidecar binaries inside it are built by the same public workflow.

## 12. Pre-submission status (honest snapshot, 2026-10-28)

The GitHub repository is public, but before submitting we must fix the following (see
`SIGNPATH-APPLICATION-CHECKLIST.md` for the ordered plan):

1. Default branch has **no `LICENSE`** at the repo root (GitHub reports `license: null`) — must be added and
   pushed, otherwise the “open source” requirement is not verifiable.
2. Default branch has **no `README.md`** — a project build/release description must be added.
3. Default branch currently holds an **old Python-only tree**; the current product tree exists on the local
   `main` and on the public `clean-snapshot-20261026` branch (which also lacks `LICENSE`). The
   signing/release branch must be made public and buildable.
4. **No GitHub Actions workflow** exists yet — the draft in this repository must be reviewed and added.
5. No public GitHub Release exists for 0.1.0 yet — the first release should reference the SHA-256 manifest.

None of these steps require money. They are the price of asking for a free certificate.
