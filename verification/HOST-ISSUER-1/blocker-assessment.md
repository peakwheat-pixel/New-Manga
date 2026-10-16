# HOST-ISSUER-1 blocker assessment

## Reality check

- Execution worktree: `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`
- Branch: `codex/HOST-ISSUER-1-tauri-ref-issuer`
- User-specified base / actual start HEAD: `2eaa3241295e1f483eabf640289a4bea4126370c`
- `2eaa324` is a direct child of Task metadata base `03412b6558aa1ba9bf0ed109ae41c0e3874f5068`. The Task metadata base was stale; no history rewrite or branch change was needed.
- Initial worktree was clean. No Python Core, React, contract, user data, or main-worktree files were modified.

## Blocking seam mismatch

The released scope permits Tauri Rust changes and explicitly forbids Python Core changes. The Core registration methods delivered by P09-FU2/P16 are in-process private methods, but the production host has no trusted way to call them:

1. `src/bootstrap/core_service.py:1491-1559` defines `_register_export_target`, `_revoke_export_target`, `_register_import_source`, and `_revoke_import_source` as methods on the live `CoreServiceServer`.
2. `src/bootstrap/core_service.py:2282-2960` dispatches public Core JSON-RPC requests. The dispatch includes `ImportPages` and `StartExport`, but no registration/revocation command. Those consumers resolve grants from registries attached to the current Core instance.
3. `src/bootstrap/core_assembly.py:1204,1260` constructs the export/import grant registries in memory for that Core instance. A second process or the existing resource-channel sidecar would not populate the live registries.
4. `apps/desktop/src-tauri/src/library_bridge.rs:265` sends requests to `bootstrap.core_service` through its JSON-RPC dispatcher. Sending registration payloads there would hit an unsupported command; adding such a JSON-RPC command requires a Core change and a security review of the host-only boundary.
5. `apps/desktop/src-tauri/src/core_bridge.rs` talks to a different sidecar (`infrastructure.resource_channel.host_bridge`). Its dispatcher supports only resource-channel methods (`ping`, `issue`, `resolve`, `touch`, `revoke`, `revoke_resource`, `shutdown`) and owns no Import/Export grant registries.

The frozen contract defines the required host→Core trust semantics but leaves runtime serialization, Tauri command names, process supervision, and auth/permission handshake `UNKNOWN / NOT_IN_SCOPE` (`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §11). A Rust-only implementation cannot register grants in the live Core without inventing a new transport or changing Python Core. Exposing the seam on the WebView JSON-RPC/Tauri surface would violate the trusted-host boundary. This requires an external scope/architecture decision and, if approved, a separately authorized narrow Core-side host-only injection path. No wire fields were added or changed.

## WebView negative evidence

`webview-static-scan.txt` records a scan of the repository's actual frontend source directory, `apps/desktop/frontend/src`, for `ImportSourceRef`, `ExportTargetRef`, `host_signature`, `source_path`, and `target_path`: `NO_MATCHES` (ripgrep exit 1). The current Tauri production command list, handler, build manifest, and capability file also contain no host issuer command or dialog permission. This is baseline/static evidence only; because no issuer flow can be built, it does not satisfy AC4's implementation-level negative test.

## Build/test evidence

- `cargo-build.txt`: `cargo build` exited 101 in `build.rs` because the ignored `apps/desktop/src-tauri/target/core-sidecar/core-sidecar` bundle is absent.
- `cargo-test.txt`: `cargo test` exited 101 for the same reason, before Rust unit tests could run.
- The project build prerequisites are also absent in this worktree: the dedicated `m2ac5-build` Python interpreter, frontend `node_modules`, and frontend `dist` are missing. The repository packaging instructions describe provisioning/building these artifacts; that environment setup is outside this Task's authorized code paths and was not performed.

## Key/dependency/security disposition

- No host key was generated or persisted because no supported registration channel exists. Therefore key-at-rest, session rotation, and revoke-on-shutdown are not implemented and AC3 remains blocked.
- No reference or path was added to the WebView. The frontend scan found no matching fields, but AC4 is not marked pass because there is no executable issuer flow to probe.
- No Tauri command, capability, permission, or dependency was added. In particular, no dialog plugin was introduced; a frontend-callable picker would disclose paths and would not solve the missing Core registration channel.
- Existing P09-FU2/P16 Core rejection evidence remains valid for their Core consumers, but cannot prove host issuance or host-side rejection end to end. No new host forgery/scope test ran; AC7 remains blocked.

## Required unblock

User/Codex must decide and authorize the trusted host→Core registration transport and its allowed Core-side changes (including how it is bound to the live Core session and how shutdown/revocation invalidates grants). After that seam is frozen and released, resume HOST-ISSUER-1 from the resulting integrated base; do not expose registration as a WebView-callable command or add fields to either reference.
