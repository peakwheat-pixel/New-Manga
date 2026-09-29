# M2 Release Gate — release declaration (base 875eb818)

**Release candidate**: NSIS installer
`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
sha256 `d222073becc50d593a3f0d706ef799df45d369a51f13c1e81423dbeef7ed09db`
(console-policy fix included; self-contained onedir sidecar with the four
frozen entries host_bridge / core_service / acceptance_bridge / catalog_loader).

**GATE VERDICT: PASS** (machine-readable: [raw/rg1-gate.json](raw/rg1-gate.json),
23/23 scenarios; M2-AC5 clean-start regression on the same installer: 25/25,
[raw/rg1-m2ac5-cleanstart-gate.json](raw/rg1-m2ac5-cleanstart-gate.json)).

Ruling basis: user ruling 2026-09-29 — "把本机视为干净widows环境。若本机通过，
则视为pass". Verification basis: this machine (Windows 11 Pro x64, build
26200.9457). Windows 10 / other builds: **NOT_RUN** (disclosed; candidate for
future matrix expansion, non-blocking).

Support matrix declared by this gate:

| OS | Status |
|---|---|
| Windows 11 x64 (build 26200, this machine) | verified (this gate) |
| Windows 10 (any build) | NOT_RUN — disclosed |
| other Windows builds / ARM64 | NOT_RUN — disclosed |

Details per AC: [verification-results.md](verification-results.md).
Delivery chain and reproduction: `doc/handoffs/M2-RG1-a1100d75.md`.
