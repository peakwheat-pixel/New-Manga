# Privacy Policy — New Manga

_Last updated: 2026-10-29_

New Manga is a local-first Windows desktop application for translating manga/comic pages.

## What the application processes

- **Local by default.** With local providers, all processing (detection, OCR, translation, inpainting,
  rendering) happens on the user's machine. The application has no telemetry, no account system, and no
  network listener.
- **Optional remote providers.** If the user explicitly configures a remote provider in Settings, that
  provider may receive the data kinds shown in the settings privacy notice: page images (OCR), text
  (translation), and images/masks (inpainting). This is initiated by the user's configuration and can be
  removed at any time by switching back to a local provider.
- **Optional import helper.** The optional Playwright-based import helper downloads public web pages only
  when the user runs an import for a URL they provided.
- **User data location.** Library database, managed copies, caches, exports and logs are stored under
  `%APPDATA%\com.newmanga.desktop`. The installer and uninstaller never delete or rewrite this data root.

## What the application does NOT do

- No analytics, advertising, crash-reporting or usage telemetry.
- No silent updates or background downloads.
- No transfer of user media to systems the user did not configure.

## Third-party components

The application bundles open-source components whose own privacy behaviour is limited to local
processing. The `-models` package additionally bundles the Ultralytics YOLO11s-seg model weights (AGPL-3.0);
inference runs locally through ONNX Runtime / DirectML. Third-party licenses are listed in
[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) and [`NOTICE.md`](NOTICE.md).

## Contact

Repository: <https://github.com/peakwheat-pixel/New-Manga> — open an issue for privacy questions.
