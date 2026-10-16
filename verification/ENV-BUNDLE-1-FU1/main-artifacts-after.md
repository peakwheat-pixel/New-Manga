# Main ignored artifacts after AC4

Refreshed by mirroring the artifacts built in this task worktree using `packaging/m2ac5/build_sidecar.ps1 -Force` and `npm ci` + `npm run build`. Destination paths were confirmed gitignored before the copy. Copy logs: [`ac4-copy-sidecar-to-main.log`](ac4-copy-sidecar-to-main.log), [`ac4-copy-frontend-to-main.log`](ac4-copy-frontend-to-main.log); Robocopy exit `3` for both (files copied and stale extras present, zero failures).

| Artifact | Before | After |
|---|---|---|
| Main `core_service.exe` bytes | `68,604,146` | `68,717,156` |
| Main `core_service.exe` SHA-256 | `61f128d6878baad1c72fa24f7cda75675b31354ea47b43828861e7d8b2ca91f0` | `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` |
| Main executable protocol | `1.6` (2.3 request returned `PROTOCOL_VERSION_UNSUPPORTED`) | `2.3` (`core.ping` ready; `core.shutdown` stopped; exit `0`) |
| Main sidecar tree | `5,610` files / `1,296,373,783` bytes | `5,563` files / `1,287,287,472` bytes |
| Main frontend dist | `2` files / `196,591` bytes; manifest SHA-256 `d6dd3bdbea477414f72a92fe19f75d402cd41c945e81d82f2842f64a1c96c041` | `2` files / `201,081` bytes; manifest SHA-256 `d56249d8a1afc8edd88309a7fb4ad9b4add39ec9c68151dca7850c9012898ea7` |

The refreshed main executable and its direct isolated protocol probe are captured in [`ac4-main-core-smoke-after.log`](ac4-main-core-smoke-after.log). Frontend file manifest after copy matches the pinned task build in [`ac1-bundle-and-frontend-manifest.md`](ac1-bundle-and-frontend-manifest.md).
